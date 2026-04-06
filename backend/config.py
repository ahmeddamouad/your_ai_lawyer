"""
Configuration settings for the backend.

All settings can be overridden via environment variables.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Moroccan Legal AI Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Ollama Configuration
    OLLAMA_HOST: str = "http://localhost:11434"  # Docker: "http://ollama:11434"
    LLM_MODEL: str = "mistral"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # RAG Configuration
    CHROMA_PATH: str = "./chroma"
    DATA_PATH: str = "./data/legal_pdfs"
    RETRIEVAL_K: int = 5
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 200

    # Conversation
    MAX_CONVERSATION_HISTORY: int = 5

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost"]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
