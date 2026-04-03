"""
Chat management module for storing and retrieving conversation history.
"""

import os
import json
from typing import List, Dict, Tuple
from datetime import datetime


class ChatManager:
    """Manages chat sessions and conversation history."""
    
    def __init__(self, chats_dir: str):
        """
        Initialize Chat Manager.
        
        Args:
            chats_dir: Directory to store chat files
        """
        self.chats_dir = chats_dir
        os.makedirs(chats_dir, exist_ok=True)
    
    def create_new_chat(self) -> str:
        """
        Create a new chat session.
        
        Returns:
            Chat ID (timestamp-based)
        """
        chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        
        chat_data = {
            "chat_id": chat_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "documents_used": []
        }
        
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)
        
        return chat_id
    
    def list_chats(self) -> List[Dict]:
        """
        List all available chat sessions.
        
        Returns:
            List of chat metadata
        """
        chats = []
        for filename in sorted(os.listdir(self.chats_dir), reverse=True):
            if filename.endswith(".json"):
                chat_path = os.path.join(self.chats_dir, filename)
                try:
                    with open(chat_path, 'r') as f:
                        chat_data = json.load(f)
                    chats.append({
                        "chat_id": chat_data["chat_id"],
                        "created_at": chat_data["created_at"],
                        "message_count": len(chat_data["messages"]),
                        "documents_count": len(chat_data.get("documents_used", []))
                    })
                except:
                    pass
        return chats
    
    def load_chat(self, chat_id: str) -> Dict:
        """
        Load a specific chat session.
        
        Args:
            chat_id: ID of the chat to load
            
        Returns:
            Chat data
        """
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        if os.path.exists(chat_file):
            with open(chat_file, 'r') as f:
                return json.load(f)
        return None
    
    def add_message(self, chat_id: str, role: str, content: str, documents_used: List[str] = None):
        """
        Add a message to a chat session.
        
        Args:
            chat_id: ID of the chat
            role: "user" or "assistant"
            content: Message content
            documents_used: Optional list of documents used for this response
        """
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        
        try:
            with open(chat_file, 'r') as f:
                chat_data = json.load(f)
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            if documents_used:
                message["documents_used"] = list(documents_used)
            
            chat_data["messages"].append(message)
            
            # Track documents used
            if documents_used:
                for doc in documents_used:
                    if doc not in chat_data.get("documents_used", []):
                        chat_data.setdefault("documents_used", []).append(doc)
            
            with open(chat_file, 'w') as f:
                json.dump(chat_data, f, indent=2)
                
        except Exception as e:
            print(f"Error adding message: {str(e)}")
    
    def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """
        Get all messages in a chat session.
        
        Args:
            chat_id: ID of the chat
            
        Returns:
            List of messages
        """
        chat_data = self.load_chat(chat_id)
        return chat_data["messages"] if chat_data else []
    
    def get_chat_history_for_context(self, chat_id: str, last_n: int = 6) -> str:
        """
        Get chat history in a format suitable for LLM context.
        
        Args:
            chat_id: ID of the chat
            last_n: Number of recent messages to include
            
        Returns:
            Formatted chat history
        """
        messages = self.get_chat_messages(chat_id)
        recent_messages = messages[-last_n:] if len(messages) > last_n else messages
        
        history = ""
        for msg in recent_messages:
            role = msg["role"].upper()
            history += f"{role}: {msg['content']}\n\n"
        
        return history

    @staticmethod
    def prepare_llm_turn(
        messages: List[Dict],
        *,
        max_prior_messages: int = 16,
        strip_sources_footer: bool = True,
    ) -> Tuple[List[Dict[str, str]], str]:
        """
        Split in-session messages for the LLM: prior user/assistant turns + current user text.
        Expects messages to end with the current user message (system messages skipped).
        """
        if not messages:
            return [], ""
        last = messages[-1]
        if last.get("role") != "user":
            return [], last.get("content") or ""

        current_question = last.get("content") or ""
        prior: List[Dict[str, str]] = []
        for m in messages[:-1]:
            role = m.get("role")
            if role not in ("user", "assistant"):
                continue
            content = m.get("content") or ""
            if strip_sources_footer and role == "assistant" and "📎 **Sources:**" in content:
                content = content.split("\n\n📎 **Sources:**")[0].strip()
            prior.append({"role": role, "content": content})
        if len(prior) > max_prior_messages:
            prior = prior[-max_prior_messages:]
        return prior, current_question
    
    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            chat_id: ID of the chat to delete
            
        Returns:
            True if successful
        """
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        if os.path.exists(chat_file):
            try:
                os.remove(chat_file)
                return True
            except:
                return False
        return False
    
    def export_chat(self, chat_id: str, export_path: str) -> bool:
        """
        Export a chat to a text file.
        
        Args:
            chat_id: ID of the chat
            export_path: Path to save the exported chat
            
        Returns:
            True if successful
        """
        chat_data = self.load_chat(chat_id)
        if not chat_data:
            return False
        
        try:
            with open(export_path, 'w') as f:
                f.write(f"Chat ID: {chat_data['chat_id']}\n")
                f.write(f"Created: {chat_data['created_at']}\n")
                f.write(f"Documents Used: {', '.join(chat_data.get('documents_used', ['None']))}\n")
                f.write("=" * 60 + "\n\n")
                
                for msg in chat_data["messages"]:
                    role = msg["role"].upper()
                    f.write(f"{role}:\n{msg['content']}\n\n")
            
            return True
        except Exception as e:
            print(f"Error exporting chat: {str(e)}")
            return False
