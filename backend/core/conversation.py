"""
Conversation memory management.

Handles per-session conversation history for the chatbot.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    sources: Optional[List[str]] = None


@dataclass
class Conversation:
    """A conversation session with message history."""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    language: str = "fr"

    def add_message(self, role: str, content: str, sources: Optional[List[str]] = None):
        """Add a message to the conversation."""
        self.messages.append(Message(
            role=role,
            content=content,
            sources=sources
        ))

    def get_history_text(self, max_messages: int = 5) -> str:
        """
        Get conversation history as formatted text.

        Args:
            max_messages: Maximum number of message pairs to include

        Returns:
            Formatted conversation history string
        """
        # Get recent messages (user + assistant pairs)
        recent = self.messages[-(max_messages * 2):]

        if not recent:
            return ""

        history_parts = []
        for msg in recent:
            prefix = "Utilisateur" if msg.role == "user" else "Assistant"
            if self.language == "ar":
                prefix = "المستخدم" if msg.role == "user" else "المساعد"
            history_parts.append(f"{prefix}: {msg.content}")

        return "\n".join(history_parts)


class ConversationManager:
    """
    Manages multiple conversation sessions.

    Stores conversations in memory. For production, consider
    using Redis or a database for persistence.
    """

    def __init__(self, max_history: int = 5):
        self.sessions: Dict[str, Conversation] = {}
        self.max_history = max_history

    def create_session(self, language: str = "fr") -> str:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = Conversation(
            session_id=session_id,
            language=language
        )
        return session_id

    def get_session(self, session_id: str) -> Optional[Conversation]:
        """Get an existing session."""
        return self.sessions.get(session_id)

    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        language: str = "fr"
    ) -> Conversation:
        """Get existing session or create a new one."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        new_id = session_id or str(uuid.uuid4())
        self.sessions[new_id] = Conversation(
            session_id=new_id,
            language=language
        )
        return self.sessions[new_id]

    def add_exchange(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        sources: Optional[List[str]] = None
    ):
        """Add a user-assistant exchange to a session."""
        session = self.get_session(session_id)
        if session:
            session.add_message("user", user_message)
            session.add_message("assistant", assistant_response, sources)

    def get_history(self, session_id: str) -> str:
        """Get formatted conversation history."""
        session = self.get_session(session_id)
        if session:
            return session.get_history_text(self.max_history)
        return ""

    def clear_session(self, session_id: str) -> bool:
        """Clear/delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def list_sessions(self) -> List[Dict]:
        """List all active sessions."""
        return [
            {
                "session_id": s.session_id,
                "message_count": len(s.messages),
                "created_at": s.created_at.isoformat(),
                "language": s.language
            }
            for s in self.sessions.values()
        ]


# Global conversation manager instance
conversation_manager = ConversationManager()
