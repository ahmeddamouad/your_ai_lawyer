"""
RAG (Retrieval Augmented Generation) Engine.

Core logic for querying the vector database and generating responses.
"""
import re
from typing import Optional, List, Dict, Any
from langchain.vectorstores.chroma import Chroma
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate

import sys
sys.path.insert(0, '..')
from config import settings
from core.embedding import get_embedding_function
from core.conversation import conversation_manager, Conversation
from prompts.legal_fr import PROMPT_FR, PROMPT_FR_WITH_HISTORY
from prompts.legal_ar import PROMPT_AR, PROMPT_AR_WITH_HISTORY


class RAGEngine:
    """
    RAG Engine for the Moroccan Legal AI Chatbot.

    Handles:
    - Vector similarity search in ChromaDB
    - Conversation history management
    - Bilingual prompt construction (French/Arabic)
    - LLM response generation via Ollama
    """

    def __init__(self):
        self._db: Optional[Chroma] = None
        self._llm: Optional[Ollama] = None

    @property
    def db(self) -> Chroma:
        """Lazy-load the ChromaDB instance."""
        if self._db is None:
            self._db = Chroma(
                persist_directory=settings.CHROMA_PATH,
                embedding_function=get_embedding_function()
            )
        return self._db

    @property
    def llm(self) -> Ollama:
        """Lazy-load the Ollama LLM instance."""
        if self._llm is None:
            self._llm = Ollama(
                model=settings.LLM_MODEL,
                base_url=settings.OLLAMA_HOST
            )
        return self._llm

    def _clean_response(self, response: str) -> str:
        """
        Clean the LLM response.

        Removes thinking tags (from DeepSeek-style models)
        and cleans up formatting.
        """
        # Remove <think>...</think> tags
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)

        # Clean up extra whitespace
        response = response.strip()

        return response

    def _build_prompt(
        self,
        question: str,
        context: str,
        history: str,
        language: str
    ) -> str:
        """
        Build the prompt for the LLM.

        Args:
            question: User's question
            context: Retrieved context from documents
            history: Conversation history
            language: "fr" for French, "ar" for Arabic

        Returns:
            Formatted prompt string
        """
        if language == "ar":
            template = PROMPT_AR
            history_template = PROMPT_AR_WITH_HISTORY
        else:
            template = PROMPT_FR
            history_template = PROMPT_FR_WITH_HISTORY

        # Build history section
        history_section = ""
        if history:
            history_section = history_template.format(history=history)

        # Build full prompt
        prompt = template.format(
            history_section=history_section,
            context=context,
            question=question
        )

        return prompt

    def search_documents(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[tuple]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            k: Number of results (default from settings)

        Returns:
            List of (document, score) tuples
        """
        k = k or settings.RETRIEVAL_K
        results = self.db.similarity_search_with_score(query, k=k)
        return results

    async def query(
        self,
        question: str,
        session_id: Optional[str] = None,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Process a user query and generate a response.

        Args:
            question: User's question
            session_id: Conversation session ID (creates new if None)
            language: Response language ("fr" or "ar")

        Returns:
            Dictionary with answer, sources, and session_id
        """
        # Get or create conversation session
        conversation = conversation_manager.get_or_create_session(
            session_id=session_id,
            language=language
        )

        # Search for relevant documents
        results = self.search_documents(question)

        # Build context from search results
        context_parts = []
        sources = []
        for doc, score in results:
            context_parts.append(doc.page_content)
            source_id = doc.metadata.get("id", "unknown")
            if source_id not in sources:
                sources.append(source_id)

        context = "\n\n---\n\n".join(context_parts)

        # Get conversation history
        history = conversation.get_history_text(settings.MAX_CONVERSATION_HISTORY)

        # Build prompt
        prompt = self._build_prompt(
            question=question,
            context=context,
            history=history,
            language=language
        )

        # Generate response
        raw_response = self.llm.invoke(prompt)
        response = self._clean_response(raw_response)

        # Update conversation history
        conversation_manager.add_exchange(
            session_id=conversation.session_id,
            user_message=question,
            assistant_response=response,
            sources=sources
        )

        return {
            "answer": response,
            "sources": sources,
            "session_id": conversation.session_id,
            "language": language
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics."""
        try:
            items = self.db.get(include=[])
            doc_count = len(items["ids"])
        except Exception:
            doc_count = 0

        return {
            "model": settings.LLM_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL,
            "ollama_host": settings.OLLAMA_HOST,
            "document_count": doc_count,
            "retrieval_k": settings.RETRIEVAL_K
        }


# Global RAG engine instance
rag_engine = RAGEngine()


async def query_rag(
    question: str,
    session_id: Optional[str] = None,
    language: str = "fr"
) -> Dict[str, Any]:
    """
    Convenience function to query the RAG engine.

    Args:
        question: User's question
        session_id: Optional session ID for conversation continuity
        language: Response language ("fr" or "ar")

    Returns:
        Dictionary with answer, sources, and session_id
    """
    return await rag_engine.query(question, session_id, language)
