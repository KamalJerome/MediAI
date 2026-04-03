"""
RAG (Retrieval Augmented Generation) module for document-based Q&A.
"""

import os
import json
import pickle
from typing import List, Tuple, Optional, Generator, Dict
from datetime import datetime
from openai import OpenAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Direct OpenAI client (avoids LangChain prompts/chains and "langchain.prompts" errors)
def _openai_chat(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Call OpenAI Chat Completions API directly. No LangChain dependency."""
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return (response.choices[0].message.content or "").strip()


def _openai_chat_stream(prompt: str, model: str = "gpt-3.5-turbo"):
    """Stream OpenAI Chat Completions; yields text deltas."""
    from openai import OpenAI
    client = OpenAI()
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _openai_chat_stream_messages(messages: List[dict], model: str = "gpt-3.5-turbo"):
    """Stream chat completions with multi-turn messages."""
    from openai import OpenAI
    client = OpenAI()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _retrieval_query_from_history(
    prior_messages: List[Dict[str, str]], question: str, max_chars: int = 1200
) -> str:
    """Combine recent turns with the current question so retrieval matches follow-ups."""
    if not prior_messages:
        return question
    parts = []
    for m in prior_messages[-6:]:
        role = m.get("role", "")
        content = (m.get("content") or "").strip()
        if not content:
            continue
        parts.append(f"{role}: {content}")
    parts.append(f"user: {question}")
    combined = "\n".join(parts)
    return combined if len(combined) <= max_chars else combined[-max_chars:]

def _check_imports():
    missing = []
    if RecursiveCharacterTextSplitter is None:
        missing.append("RecursiveCharacterTextSplitter (langchain or langchain-text-splitters)")
    if OpenAIEmbeddings is None:
        missing.append("OpenAIEmbeddings (langchain or langchain-openai)")
    if FAISS is None:
        missing.append("FAISS (langchain or langchain-community)")
    if missing:
        raise ImportError(
            "Missing LangChain components: " + "; ".join(missing)
            + ". Install with: pip install langchain faiss-cpu openai"
            + " or for newer versions: pip install langchain langchain-openai langchain-community faiss-cpu"
        )

_check_imports()


class RAGManager:
    """Manages RAG operations for document-based Q&A."""
    
    def __init__(self, embeddings_dir: str, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize RAG Manager.
        
        Args:
            embeddings_dir: Directory to store embeddings
            model_name: OpenAI model to use
        """
        self.embeddings_dir = embeddings_dir
        self.model_name = model_name
        self.vector_store = None
        self.qa_chain = None
        self.documents_info = {}
        
        os.makedirs(embeddings_dir, exist_ok=True)
        self._load_vector_store()
    
    def add_document(self, doc_name: str, doc_text: str) -> bool:
        """
        Add a document to the vector store with source metadata for citations.
        
        Args:
            doc_name: Name/ID of the document
            doc_text: Text content to embed
            
        Returns:
            True if successful
        """
        try:
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(doc_text)
            embeddings = OpenAIEmbeddings()
            if Document is not None:
                docs = [Document(page_content=c, metadata={"source": doc_name}) for c in chunks]
                if self.vector_store is None:
                    self.vector_store = FAISS.from_documents(docs, embeddings)
                else:
                    new_store = FAISS.from_documents(docs, embeddings)
                    self.vector_store.merge_from(new_store)
            else:
                if self.vector_store is None:
                    self.vector_store = FAISS.from_texts(chunks, embeddings)
                else:
                    new_store = FAISS.from_texts(chunks, embeddings)
                    self.vector_store.merge_from(new_store)
            
            self._save_source_text(doc_name, doc_text)
            self._save_vector_store()
            self.documents_info[doc_name] = {
                "added_at": datetime.now().isoformat(),
                "chunks": len(chunks),
                "content_length": len(doc_text)
            }
            self._save_documents_info()
            return True
            
        except Exception as e:
            print(f"Error adding document: {str(e)}")
            return False
    
    def query(self, question: str, max_tokens: int = 500) -> str:
        """
        Query using RAG if documents available, otherwise use direct LLM.
        
        Args:
            question: User's question
            max_tokens: Maximum tokens in response
            
        Returns:
            Answer from documents (if available) or general knowledge response
        """
        try:
            # If no documents uploaded, use direct LLM query
            if self.vector_store is None:
                return self._direct_llm_query(question)
            
            # Documents available - use manual RAG (avoids langchain.prompts dependency)
            result = self._query_rag_manual(question)
            
            # Check if answer is generic (no relevant documents found)
            if self._is_generic_response(result, question):
                return "I don't have enough information in the uploaded documents to answer that question. You can upload relevant medical documents or ask another question."
            
            return result
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def query_stream(
        self,
        question: str,
        prior_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[Generator[str, None, None], List[str]]:
        """
        Stream the LLM response and return sources for citations.
        prior_messages: prior user/assistant turns in this chat (OpenAI shape) for memory.
        Returns (generator of content chunks, list of source document names).
        """
        prior = prior_messages or []
        system = (
            "You are a helpful medical information assistant. "
            "Use earlier messages in this conversation for context (e.g. who 'the patient' or 'they' refers to). "
            "When the latest user message includes retrieved document context, base factual claims on that context only; "
            "if it is insufficient, say so. "
            "Do NOT provide diagnosis, prescription, or treatment advice."
        )

        if self.vector_store is None:
            user_last = (
                "Question: " + question + "\n\nAnswer clearly, using the conversation so far if relevant."
            )
            api_messages = [{"role": "system", "content": system}] + prior + [
                {"role": "user", "content": user_last}
            ]
            return _openai_chat_stream_messages(api_messages, self.model_name), []

        retrieval_q = _retrieval_query_from_history(prior, question)
        chunks_with_sources = self.get_relevant_chunks_with_sources(retrieval_q, k=3)
        if not chunks_with_sources:
            def _empty_msg():
                yield "I don't have enough information in the uploaded documents to answer that question. You can upload relevant medical documents or ask another question."
            return _empty_msg(), []
        chunks = [c[0] for c in chunks_with_sources]
        sources = list(dict.fromkeys(c[1] for c in chunks_with_sources))
        context = "\n\n".join(chunks)
        user_last = (
            "Retrieved context from uploaded documents:\n"
            f"{context}\n\n"
            f"Question: {question}\n\n"
            "Answer using the context and the conversation so far where helpful."
        )
        api_messages = [{"role": "system", "content": system}] + prior + [
            {"role": "user", "content": user_last}
        ]
        return _openai_chat_stream_messages(api_messages, self.model_name), sources
    
    def _query_rag_manual(self, question: str) -> str:
        """RAG query using direct OpenAI API; appends citations (Sources)."""
        chunks_with_sources = self.get_relevant_chunks_with_sources(question, k=3)
        if not chunks_with_sources:
            return "I don't have enough information in the uploaded documents to answer that question. You can upload relevant medical documents or ask another question."
        chunks = [c[0] for c in chunks_with_sources]
        sources = list(dict.fromkeys(c[1] for c in chunks_with_sources))  # unique, order preserved
        context = "\n\n".join(chunks)
        prompt = f"""You are a helpful medical information assistant. Answer based only on the following context from uploaded documents. If the context doesn't contain relevant information, say so. Do NOT provide diagnosis, prescription, or treatment advice.

Context:
{context}

Question: {question}

Answer:"""
        response = _openai_chat(prompt, self.model_name)
        if sources and response:
            response += "\n\n📎 **Sources:** " + ", ".join(sources)
        return response
    
    def _direct_llm_query(self, question: str) -> str:
        """
        Query the LLM directly without RAG (when no documents uploaded).
        Uses OpenAI API directly to avoid LangChain prompts/chains.
        """
        prompt = """You are a helpful medical information assistant.
Provide clear, accurate, and student-friendly information about medical topics.
Do NOT provide diagnosis, prescription advice, or treatment recommendations.
Keep responses informative but concise.

Question: """ + question + """

Answer:"""
        return _openai_chat(prompt, self.model_name)
    
    def get_relevant_chunks(self, question: str, k: int = 3) -> List[str]:
        """
        Get relevant document chunks for a question.
        
        Args:
            question: User's question
            k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks
        """
        pairs = self.get_relevant_chunks_with_sources(question, k)
        return [p[0] for p in pairs]
    
    def get_relevant_chunks_with_sources(self, question: str, k: int = 3) -> List[Tuple[str, str]]:
        """
        Get relevant chunks with source document names for citations.
        
        Returns:
            List of (content, source_name) tuples
        """
        if self.vector_store is None:
            return []
        try:
            results = self.vector_store.similarity_search(question, k=k)
            return [(r.page_content, r.metadata.get("source", "unknown")) for r in results]
        except Exception:
            return []
    
    def list_documents(self) -> List[str]:
        """Get list of uploaded documents."""
        return list(self.documents_info.keys())
    
    def remove_document(self, doc_name: str) -> bool:
        """
        Remove a document from the vector store.
        Note: FAISS doesn't support deletion, so we rebuild the store.
        """
        if doc_name in self.documents_info:
            del self.documents_info[doc_name]
            self._save_documents_info()
            self._remove_source_text(doc_name)
            return True
        return False
    
    def clear_all_documents(self):
        """Clear all documents and vector store."""
        self.vector_store = None
        self.documents_info = {}
        self._save_vector_store()
        self._save_documents_info()
        path = self._source_texts_path()
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
    
    def _source_texts_path(self) -> str:
        return os.path.join(self.embeddings_dir, "source_texts.json")
    
    def _save_source_text(self, doc_name: str, doc_text: str):
        """Persist raw text so we can rebuild FAISS if the index is missing or unload fails."""
        path = self._source_texts_path()
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data[doc_name] = doc_text
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _remove_source_text(self, doc_name: str):
        path = self._source_texts_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.pop(doc_name, None)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def _load_source_texts(self) -> dict:
        path = self._source_texts_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _try_load_faiss_index(self) -> bool:
        """Load FAISS from disk. Returns True if vector_store was loaded."""
        store_path = os.path.join(self.embeddings_dir, "faiss_index")
        if not os.path.exists(store_path):
            return False
        try:
            embeddings = OpenAIEmbeddings()
            try:
                self.vector_store = FAISS.load_local(
                    store_path, embeddings, allow_dangerous_deserialization=True
                )
            except TypeError as te:
                # Only fall back for older LangChain that doesn't accept this kwarg.
                # Other TypeErrors must not drop the flag (loading would fail on pickle guard).
                msg = str(te).lower()
                if "unexpected keyword" in msg or "allow_dangerous" in msg:
                    self.vector_store = FAISS.load_local(store_path, embeddings)
                else:
                    raise
            return self.vector_store is not None
        except Exception as e:
            print(f"Error loading FAISS index: {str(e)}")
            self.vector_store = None
            return False
    
    def _rebuild_vector_store_from_sources(self) -> bool:
        """Rebuild FAISS from source_texts.json when index is missing but documents were ingested."""
        source_texts = self._load_source_texts()
        if not source_texts or not self.documents_info:
            return False
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            embeddings = OpenAIEmbeddings()
            self.vector_store = None
            for doc_name in list(self.documents_info.keys()):
                if doc_name not in source_texts:
                    continue
                doc_text = source_texts[doc_name]
                chunks = text_splitter.split_text(doc_text)
                if Document is not None:
                    docs = [Document(page_content=c, metadata={"source": doc_name}) for c in chunks]
                    if self.vector_store is None:
                        self.vector_store = FAISS.from_documents(docs, embeddings)
                    else:
                        new_store = FAISS.from_documents(docs, embeddings)
                        self.vector_store.merge_from(new_store)
                else:
                    if self.vector_store is None:
                        self.vector_store = FAISS.from_texts(chunks, embeddings)
                    else:
                        new_store = FAISS.from_texts(chunks, embeddings)
                        self.vector_store.merge_from(new_store)
            if self.vector_store is not None:
                self._save_vector_store()
                return True
        except Exception as e:
            print(f"Error rebuilding vector store from sources: {str(e)}")
        self.vector_store = None
        return False
    
    def _save_vector_store(self):
        """Save vector store to disk."""
        if self.vector_store is not None:
            try:
                store_path = os.path.join(self.embeddings_dir, "faiss_index")
                os.makedirs(self.embeddings_dir, exist_ok=True)
                self.vector_store.save_local(store_path)
            except Exception as e:
                print(f"Error saving vector store: {str(e)}")
    
    def _load_vector_store(self):
        """Load documents metadata, FAISS index, or rebuild index from stored source text."""
        self._load_documents_info()
        self.vector_store = None
        if self._try_load_faiss_index():
            return
        if self.documents_info and self._rebuild_vector_store_from_sources():
            return
    
    def _save_documents_info(self):
        """Save documents info to file."""
        info_path = os.path.join(self.embeddings_dir, "documents_info.json")
        with open(info_path, 'w') as f:
            json.dump(self.documents_info, f, indent=2, default=str)
    
    def _load_documents_info(self):
        """Load documents info from file."""
        info_path = os.path.join(self.embeddings_dir, "documents_info.json")
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r') as f:
                    self.documents_info = json.load(f)
            except:
                self.documents_info = {}
    
    def _is_generic_response(self, response: str, question: str) -> bool:
        """Check if response seems generic (no document context used)."""
        generic_phrases = [
            "i don't have",
            "i can't",
            "i'm not sure",
            "unable to find",
            "no information",
            "without knowing"
        ]
        return any(phrase in response.lower() for phrase in generic_phrases)
