"""
Document loading and indexing.

Handles PDF loading, text chunking, and ChromaDB indexing.
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.vectorstores.chroma import Chroma

import sys
sys.path.insert(0, '..')
from config import settings
from core.embedding import get_embedding_function


# Legal document separators (French and Arabic)
LEGAL_SEPARATORS = [
    "\n\n",           # Paragraph breaks
    "\n",             # Line breaks
    "Article ",       # French article markers
    "المادة ",        # Arabic article markers
    "Chapitre ",      # Chapter markers (French)
    "الباب ",         # Chapter markers (Arabic)
    "Section ",       # Section markers
    "القسم ",         # Section markers (Arabic)
    ". ",             # Sentence boundaries
    " ",              # Word boundaries
]


def load_documents(data_path: Optional[str] = None) -> List[Document]:
    """
    Load PDF documents from a directory.

    Args:
        data_path: Path to directory containing PDFs.
                  Defaults to settings.DATA_PATH

    Returns:
        List of loaded documents
    """
    path = data_path or settings.DATA_PATH

    if not os.path.exists(path):
        print(f"[WARN] Data path does not exist: {path}")
        return []

    # Check if it's a single file or directory
    if os.path.isfile(path) and path.endswith('.pdf'):
        loader = PyPDFLoader(path)
    else:
        loader = PyPDFDirectoryLoader(path, recursive=True)

    print(f"[INFO] Loading documents from: {path}")
    documents = loader.load()
    print(f"[INFO] Loaded {len(documents)} document pages")

    return documents


def split_documents(
    documents: List[Document],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> List[Document]:
    """
    Split documents into chunks for indexing.

    Uses legal-document-aware separators for better chunking.

    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk (default from settings)
        chunk_overlap: Overlap between chunks (default from settings)

    Returns:
        List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
        separators=LEGAL_SEPARATORS
    )

    chunks = text_splitter.split_documents(documents)
    print(f"[INFO] Split into {len(chunks)} chunks")

    return chunks


def calculate_chunk_ids(chunks: List[Document]) -> List[Document]:
    """
    Calculate unique IDs for each chunk.

    ID format: "source:page:chunk_index"
    Example: "data/laws/constitution.pdf:6:2"

    Args:
        chunks: List of document chunks

    Returns:
        Chunks with IDs added to metadata
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", 0)
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks


def add_to_database(chunks: List[Document], chroma_path: Optional[str] = None):
    """
    Add document chunks to the ChromaDB vector store.

    Handles deduplication - only adds new chunks.

    Args:
        chunks: Document chunks to add
        chroma_path: Path to ChromaDB (default from settings)
    """
    path = chroma_path or settings.CHROMA_PATH

    db = Chroma(
        persist_directory=path,
        embedding_function=get_embedding_function()
    )

    chunks_with_ids = calculate_chunk_ids(chunks)

    # Get existing IDs
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"[INFO] Existing documents in DB: {len(existing_ids)}")

    # Filter to new chunks only
    new_chunks = [
        chunk for chunk in chunks_with_ids
        if chunk.metadata["id"] not in existing_ids
    ]

    if new_chunks:
        print(f"[INFO] Adding {len(new_chunks)} new documents")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        print("[INFO] Documents added successfully")
    else:
        print("[INFO] No new documents to add")


def clear_database(chroma_path: Optional[str] = None):
    """
    Clear (delete) the ChromaDB database.

    Args:
        chroma_path: Path to ChromaDB (default from settings)
    """
    path = chroma_path or settings.CHROMA_PATH

    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"[INFO] Database cleared: {path}")
    else:
        print(f"[INFO] Database does not exist: {path}")


def index_documents(
    data_path: Optional[str] = None,
    chroma_path: Optional[str] = None,
    reset: bool = False
):
    """
    Full indexing pipeline: load, split, and store documents.

    Args:
        data_path: Path to PDF documents
        chroma_path: Path to ChromaDB
        reset: If True, clear existing database first
    """
    if reset:
        clear_database(chroma_path)

    documents = load_documents(data_path)
    if not documents:
        print("[WARN] No documents loaded")
        return

    chunks = split_documents(documents)
    add_to_database(chunks, chroma_path)
    print("[INFO] Indexing complete!")


def get_database_stats(chroma_path: Optional[str] = None) -> dict:
    """
    Get statistics about the vector database.

    Args:
        chroma_path: Path to ChromaDB

    Returns:
        Dictionary with database statistics
    """
    path = chroma_path or settings.CHROMA_PATH

    if not os.path.exists(path):
        return {"exists": False, "count": 0}

    db = Chroma(
        persist_directory=path,
        embedding_function=get_embedding_function()
    )

    items = db.get(include=[])

    return {
        "exists": True,
        "count": len(items["ids"]),
        "path": path
    }
