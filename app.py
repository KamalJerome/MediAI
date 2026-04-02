"""
Main Streamlit application for MediAI chatbot.
"""
# python -m streamlit run app.py
# Load .env file FIRST, before any other imports
import os
from dotenv import load_dotenv
load_dotenv(override=True)  # Override system env vars with .env file

import streamlit as st
import sys
import shutil
from datetime import datetime

# Add utils to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.safety_checker import is_unsafe_request, get_safety_guidelines
from utils.pdf_processor import extract_text_from_pdf
from utils.ocr_processor import extract_text_from_image
from utils.rag_manager import RAGManager
from utils.chat_manager import ChatManager


# Page configuration
st.set_page_config(
    page_title="MediAI - Medical Information Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
BASE_CSS = """
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .safety-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .emergency-warning {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
        font-weight: bold;
    }
    /* Sticky input area at bottom: upload bar + typing bar */
    .mediai-input-anchor { display: block; height: 0; margin: 0; padding: 0; }
    section:has(.mediai-input-anchor) + section,
    section:has(.mediai-input-anchor) + div,
    .stMarkdown:has(.mediai-input-anchor) + div,
    .stMarkdown:has(.mediai-input-anchor) + section,
    [data-testid="stVerticalBlock"]:has([data-testid="stFileUploader"]) {
        position: sticky !important;
        bottom: 0 !important;
        z-index: 100;
        background: var(--background-color, #0e1117);
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        margin-top: 0.5rem;
        border-top: 1px solid rgba(250, 250, 250, 0.1);
    }
</style>
"""

# Base directory for per-chat embeddings (each chat gets its own subfolder)
EMBEDDINGS_BASE = "./data/embeddings"


def apply_css():
    """Inject base CSS."""
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def ensure_rag_manager():
    """Lazy-load RAG for current chat only when needed (upload or query)."""
    if st.session_state.current_chat_id is None:
        return
    if st.session_state.rag_manager_chat_id != st.session_state.current_chat_id:
        chat_embeddings_dir = os.path.join(EMBEDDINGS_BASE, st.session_state.current_chat_id)
        st.session_state.rag_manager = RAGManager(chat_embeddings_dir)
        st.session_state.rag_manager_chat_id = st.session_state.current_chat_id


def initialize_session():
    """Initialize session state variables."""
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = ChatManager("./data/chats")
    
    if "current_chat_messages" not in st.session_state:
        st.session_state.current_chat_messages = []
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "pdf_upload_key" not in st.session_state:
        st.session_state.pdf_upload_key = 0
    
    # Lazy load: do not create RAGManager here; created on demand in ensure_rag_manager()
    if "rag_manager_chat_id" not in st.session_state:
        st.session_state.rag_manager_chat_id = None
    if "rag_manager" not in st.session_state:
        st.session_state.rag_manager = None
    


def display_sidebar():
    """Display sidebar with chat management and settings."""
    with st.sidebar:
        st.title("🏥 MediAI")
        
        # Chat management section
        st.subheader("💬 Chat")
        
        if st.button("➕ New Chat", use_container_width=True):
            chat_id = st.session_state.chat_manager.create_new_chat()
            st.session_state.current_chat_id = chat_id
            st.session_state.current_chat_messages = []
            st.session_state.rag_manager = None
            st.session_state.rag_manager_chat_id = None
            st.rerun()
        
        # Leave chat (clear selection)
        if st.session_state.current_chat_id:
            if st.button("👋 Leave chat", use_container_width=True):
                st.session_state.current_chat_id = None
                st.session_state.current_chat_messages = []
                st.session_state.rag_manager = None
                st.session_state.rag_manager_chat_id = None
                st.rerun()
        
        # Display current chat info
        if st.session_state.current_chat_id:
            st.info(f"Current Chat: {st.session_state.current_chat_id}")
        else:
            st.warning("No active chat. Create or load a chat to start.")
        
        # Chat history with delete
        st.subheader("📝 Recent Chats")
        chats = st.session_state.chat_manager.list_chats()[:5]
        for chat in chats:
            row1, row2 = st.columns([3, 1])
            with row1:
                if st.button(f"{chat['chat_id']} ({chat['message_count']} msgs)", key=f"open_{chat['chat_id']}", use_container_width=True):
                    st.session_state.current_chat_id = chat['chat_id']
                    st.session_state.current_chat_messages = st.session_state.chat_manager.get_chat_messages(chat['chat_id'])
                    st.session_state.rag_manager = None
                    st.session_state.rag_manager_chat_id = None
                    st.rerun()
            with row2:
                if st.button("🗑️", key=f"del_{chat['chat_id']}", help="Delete chat"):
                    st.session_state.chat_manager.delete_chat(chat['chat_id'])
                    if st.session_state.current_chat_id == chat['chat_id']:
                        st.session_state.current_chat_id = None
                        st.session_state.current_chat_messages = []
                        st.session_state.rag_manager = None
                        st.session_state.rag_manager_chat_id = None
                    emb_dir = os.path.join(EMBEDDINGS_BASE, chat['chat_id'])
                    if os.path.isdir(emb_dir):
                        shutil.rmtree(emb_dir, ignore_errors=True)
                    st.rerun()
        
        # Safety guidelines
        st.divider()
        st.subheader("⚠️ Safety Information")
        with st.expander("View Safety Guidelines"):
            st.markdown(get_safety_guidelines())


def display_chat():
    """Display the chat interface."""
    st.title("🏥 MediAI - Medical Information Chatbot")
    
    # Always sync UI from persisted chat + attach RAG for this chat (fixes switching away and back)
    if st.session_state.current_chat_id:
        st.session_state.current_chat_messages = st.session_state.chat_manager.get_chat_messages(
            st.session_state.current_chat_id
        )
        ensure_rag_manager()
    
    # Chat info header + documents in this chat (from chat file, no RAG load)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.current_chat_id:
            st.caption(f"Chat ID: {st.session_state.current_chat_id}")
        else:
            st.caption("No active chat")
    with col2:
        docs_in_chat = []
        if st.session_state.current_chat_id:
            chat_data = st.session_state.chat_manager.load_chat(st.session_state.current_chat_id)
            if chat_data:
                docs_in_chat = chat_data.get("documents_used", [])
        if docs_in_chat:
            st.caption(f"📄 Documents: {', '.join(docs_in_chat)}")
        else:
            st.caption("📄 No documents in this chat")
    with col3:
        st.caption(f"💬 {len(st.session_state.current_chat_messages)} message(s)")
    
    st.divider()
    
    # Display messages
    for message in st.session_state.current_chat_messages:
        role = message["role"]
        content = message["content"]
        
        if role == "system":
            st.info(content)
        else:
            with st.chat_message(role):
                st.markdown(content)
    
    if not st.session_state.current_chat_id:
        st.warning("Please create or load a chat first.")
        return
    
    # Sticky input area at bottom: upload bar then typing bar
    st.divider()
    st.markdown('<div class="mediai-input-anchor"></div>', unsafe_allow_html=True)
    with st.container():
        upload_key = f"chat_pdf_upload_{st.session_state.current_chat_id}_{st.session_state.pdf_upload_key}"
        uploaded_file = st.file_uploader(
            "📎 Attach PDF or prescription image (OCR)",
            type=["pdf", "png", "jpg", "jpeg", "webp", "bmp"],
            key=upload_key,
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            ensure_rag_manager()
            if st.session_state.rag_manager is not None:
                ext = os.path.splitext(uploaded_file.name)[1].lower()
                is_image = ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp")
                spinner_label = "Running OCR on image..." if is_image else "Processing PDF..."
                temp_path = f"./temp_{uploaded_file.name}"
                text_content = None
                with st.spinner(spinner_label):
                    try:
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        if ext == ".pdf":
                            text_content = extract_text_from_pdf(temp_path)
                        elif is_image:
                            text_content = extract_text_from_image(temp_path)
                        else:
                            st.error("Unsupported file type.")
                    except Exception as e:
                        st.error(f"Failed to process file: {str(e)}")
                    finally:
                        try:
                            if os.path.isfile(temp_path):
                                os.remove(temp_path)
                        except OSError:
                            pass

                    if text_content is not None:
                        if not text_content.strip():
                            st.warning(
                                "No text could be extracted. For images, try a sharper, well-lit photo; "
                                "for PDFs, the file may be scanned images only—use a photo + OCR instead."
                            )
                        else:
                            doc_name = os.path.splitext(uploaded_file.name)[0]
                            success = st.session_state.rag_manager.add_document(doc_name, text_content)
                            if success:
                                kind = "image (OCR)" if is_image else "PDF"
                                doc_msg = f"📄 **Document added** ({kind}): {doc_name}"
                                st.session_state.chat_manager.add_message(
                                    st.session_state.current_chat_id,
                                    "system",
                                    doc_msg,
                                    documents_used=[doc_name]
                                )
                                st.session_state.current_chat_messages.append({
                                    "role": "system",
                                    "content": doc_msg,
                                    "timestamp": datetime.now().isoformat()
                                })
                                st.session_state.pdf_upload_key += 1
                    st.rerun()
        
        user_input = st.chat_input(
            "Ask a question about your documents or medical information...",
            key="user_input"
        )
    
    if user_input:
        st.session_state.current_chat_messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        st.session_state.chat_manager.add_message(
            st.session_state.current_chat_id,
            "user",
            user_input
        )
        with st.chat_message("user"):
            st.markdown(user_input)
        ensure_rag_manager()
        has_docs = bool(st.session_state.rag_manager and len(st.session_state.rag_manager.list_documents()) > 0)
        is_unsafe, warning = is_unsafe_request(user_input, has_documents=has_docs)
        if is_unsafe:
            with st.chat_message("assistant"):
                if "EMERGENCY" in warning:
                    st.markdown(f'<div class="emergency-warning">{warning}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="safety-warning">{warning}</div>', unsafe_allow_html=True)
            st.session_state.chat_manager.add_message(
                st.session_state.current_chat_id,
                "assistant",
                warning
            )
            st.session_state.current_chat_messages.append({
                "role": "assistant",
                "content": warning,
                "timestamp": datetime.now().isoformat()
            })
        else:
            try:
                prior_msgs, llm_question = ChatManager.prepare_llm_turn(
                    st.session_state.current_chat_messages
                )
                gen, sources = st.session_state.rag_manager.query_stream(
                    llm_question, prior_messages=prior_msgs
                )
                full_parts = []
                with st.chat_message("assistant"):
                    stream_placeholder = st.empty()
                    for chunk in gen:
                        full_parts.append(chunk)
                        stream_placeholder.markdown("".join(full_parts) + "▌")
                    stream_placeholder.markdown("".join(full_parts))
                    if sources:
                        st.caption("📎 **Sources:** " + ", ".join(sources))
                full_response = "".join(full_parts)
                if sources:
                    full_response += "\n\n📎 **Sources:** " + ", ".join(sources)
                st.session_state.chat_manager.add_message(
                    st.session_state.current_chat_id,
                    "assistant",
                    full_response,
                    documents_used=st.session_state.rag_manager.list_documents() if st.session_state.rag_manager else []
                )
                st.session_state.current_chat_messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
        st.rerun()


# Main app
def main():
    """Main application entry point."""
    initialize_session()
    #apply_css()
    display_sidebar()
    display_chat()


if __name__ == "__main__":
    main()
