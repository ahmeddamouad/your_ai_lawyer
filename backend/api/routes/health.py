"""
Health check API routes.
"""
from fastapi import APIRouter
from pydantic import BaseModel
import sys

sys.path.insert(0, '../..')
from config import settings


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    ollama_host: str
    model: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        ollama_host=settings.OLLAMA_HOST,
        model=settings.LLM_MODEL
    )


@router.get("/")
async def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": "Moroccan Legal AI Chatbot API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
