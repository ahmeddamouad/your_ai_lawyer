"""
Document management API routes.

Handles document indexing and management.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional

import sys
sys.path.insert(0, '../..')
from core.document_loader import (
    index_documents,
    get_database_stats,
    clear_database
)
from config import settings


router = APIRouter(prefix="/api/documents", tags=["documents"])


# Models

class IndexRequest(BaseModel):
    """Document indexing request."""
    data_path: Optional[str] = Field(None, description="Path to documents")
    reset: bool = Field(False, description="Clear existing index first")


class StatusResponse(BaseModel):
    """Status response model."""
    status: str
    message: str


class DatabaseStats(BaseModel):
    """Database statistics model."""
    exists: bool
    count: int
    path: str


# Background task for indexing
indexing_in_progress = False


async def run_indexing(data_path: Optional[str], reset: bool):
    """Background task to index documents."""
    global indexing_in_progress
    indexing_in_progress = True
    try:
        index_documents(data_path=data_path, reset=reset)
    finally:
        indexing_in_progress = False


# Routes

@router.post("/index", response_model=StatusResponse)
async def start_indexing(
    request: IndexRequest,
    background_tasks: BackgroundTasks
):
    """
    Start document indexing.

    This runs in the background. Use /status to check progress.
    """
    global indexing_in_progress

    if indexing_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Indexing already in progress"
        )

    background_tasks.add_task(
        run_indexing,
        request.data_path,
        request.reset
    )

    return StatusResponse(
        status="started",
        message="Document indexing started in background"
    )


@router.get("/stats", response_model=DatabaseStats)
async def get_stats():
    """Get vector database statistics."""
    stats = get_database_stats()
    return DatabaseStats(
        exists=stats["exists"],
        count=stats["count"],
        path=stats.get("path", settings.CHROMA_PATH)
    )


@router.get("/status")
async def get_indexing_status():
    """Get current indexing status."""
    return {
        "indexing_in_progress": indexing_in_progress
    }


@router.delete("/clear", response_model=StatusResponse)
async def clear_index():
    """
    Clear the vector database.

    WARNING: This deletes all indexed documents.
    """
    try:
        clear_database()
        return StatusResponse(
            status="success",
            message="Database cleared successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear database: {str(e)}"
        )
