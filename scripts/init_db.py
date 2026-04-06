#!/usr/bin/env python3
"""
Initialize the vector database with documents.

Usage:
    python -m scripts.init_db
    python -m scripts.init_db --reset
"""
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from core.document_loader import index_documents, get_database_stats
from config import settings


def main():
    parser = argparse.ArgumentParser(description="Initialize the vector database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing database before indexing"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default=settings.DATA_PATH,
        help=f"Path to documents (default: {settings.DATA_PATH})"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("INITIALIZING VECTOR DATABASE")
    print("=" * 60)
    print(f"Data path: {args.data_path}")
    print(f"ChromaDB path: {settings.CHROMA_PATH}")
    print(f"Reset: {args.reset}")
    print()

    # Show current stats
    stats = get_database_stats()
    if stats["exists"]:
        print(f"Current documents in DB: {stats['count']}")
    else:
        print("Database does not exist yet")
    print()

    # Run indexing
    index_documents(
        data_path=args.data_path,
        reset=args.reset
    )

    # Show final stats
    stats = get_database_stats()
    print()
    print("=" * 60)
    print(f"DONE! Documents in DB: {stats['count']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
