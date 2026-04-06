"""
Moroccan Legal AI Chatbot - FastAPI Backend

Main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from api.routes import chat, documents, health


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI-powered legal assistant for Moroccan law.

    Features:
    - RAG-based question answering
    - Bilingual support (French/Arabic)
    - Conversation memory
    - Source citations
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(documents.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Ollama host: {settings.OLLAMA_HOST}")
    print(f"LLM model: {settings.LLM_MODEL}")
    print(f"Embedding model: {settings.EMBEDDING_MODEL}")


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
