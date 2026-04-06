"""
Embedding function for the RAG system.

Uses Ollama embeddings with configurable model and host.
"""
from langchain_community.embeddings.ollama import OllamaEmbeddings
from functools import lru_cache

import sys
sys.path.insert(0, '..')
from config import settings


@lru_cache(maxsize=1)
def get_embedding_function() -> OllamaEmbeddings:
    """
    Get the embedding function for vector operations.

    Returns a cached OllamaEmbeddings instance configured
    with the model and host from settings.
    """
    return OllamaEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OLLAMA_HOST
    )
