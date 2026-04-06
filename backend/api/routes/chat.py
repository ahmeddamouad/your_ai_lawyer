"""
Chat API routes.

Handles chat interactions with the RAG system.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

import sys
sys.path.insert(0, '../..')
from core.rag_engine import rag_engine, query_rag
from core.conversation import conversation_manager


router = APIRouter(prefix="/api/chat", tags=["chat"])


# Request/Response Models

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    language: str = Field("fr", pattern="^(fr|ar)$", description="Response language (fr or ar)")


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str = Field(..., description="Assistant's response")
    sources: List[str] = Field(default_factory=list, description="Source document IDs")
    session_id: str = Field(..., description="Session ID")
    language: str = Field(..., description="Response language")


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    message_count: int
    created_at: str
    language: str


class SessionListResponse(BaseModel):
    """List of sessions response."""
    sessions: List[SessionInfo]


class StatusResponse(BaseModel):
    """Status response model."""
    status: str
    message: str


# Routes

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response from the legal AI assistant.

    The assistant will:
    - Search relevant legal documents
    - Consider conversation history (if session_id provided)
    - Generate a response in the specified language

    Returns the answer, source documents, and session ID.
    """
    try:
        result = await query_rag(
            question=request.message,
            session_id=request.session_id,
            language=request.language
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=result["session_id"],
            language=result["language"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """List all active conversation sessions."""
    sessions = conversation_manager.list_sessions()
    return SessionListResponse(
        sessions=[SessionInfo(**s) for s in sessions]
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get details of a specific session."""
    session = conversation_manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "language": session.language,
        "created_at": session.created_at.isoformat(),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "sources": msg.sources
            }
            for msg in session.messages
        ]
    }


@router.delete("/session/{session_id}", response_model=StatusResponse)
async def clear_session(session_id: str):
    """Clear/delete a conversation session."""
    success = conversation_manager.clear_session(session_id)

    if success:
        return StatusResponse(
            status="success",
            message=f"Session {session_id} cleared"
        )
    else:
        return StatusResponse(
            status="not_found",
            message=f"Session {session_id} not found"
        )


@router.get("/stats")
async def get_stats():
    """Get RAG engine statistics."""
    return rag_engine.get_stats()
