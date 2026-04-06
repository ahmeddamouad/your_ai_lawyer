#!/usr/bin/env python3
"""
Adala Justice Portal Scraper - Main Entry Point

Usage:
    # Scrape all categories
    python -m scraper.main

    # Scrape specific category with limit
    python -m scraper.main --category laws --limit 10

    # Dry run (list documents without downloading)
    python -m scraper.main --dry-run

    # Specify output directory
    python -m scraper.main --output ./data/legal_pdfs
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.adala_scraper import scrape_adala
from scraper.config import CATEGORIES, OUTPUT_DIR


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape legal PDFs from adala.justice.gov.ma"
    )
    parser.add_argument(
        "--category", "-c",
        choices=list(CATEGORIES.keys()),
        help="Specific category to scrape (default: all)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Maximum documents per category"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(OUTPUT_DIR),
        help=f"Output directory (default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List documents without downloading"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available categories and exit"
    )
    return parser.parse_args()


def list_categories():
    """Print available categories."""
    print("\nAvailable Categories:")
    print("-" * 60)
    for key, info in CATEGORIES.items():
        print(f"  {key:15} | {info['name_fr']:20} | {info['name_ar']}")
    print("-" * 60)


async def main():
    args = parse_args()

    if args.list_categories:
        list_categories()
        return

    print("\n" + "=" * 60)
    print("ADALA JUSTICE PORTAL SCRAPER")
    print("Moroccan Ministry of Justice Legal Documents")
    print("=" * 60)

    categories = [args.category] if args.category else None

    if categories:
        print(f"\nTarget category: {args.category}")
    else:
        print("\nTarget: ALL categories")

    if args.limit:
        print(f"Limit: {args.limit} documents per category")

    if args.dry_run:
        print("Mode: DRY RUN (no downloads)")

    print(f"Output: {args.output}")
    print()

    try:
        results = await scrape_adala(
            categories=categories,
            limit=args.limit,
            output_dir=args.output,
            dry_run=args.dry_run
        )

        # Summary
        total_docs = sum(len(docs) for docs in results.values())
        print(f"\nTotal documents found: {total_docs}")

        for cat, docs in results.items():
            if docs:
                print(f"  {cat}: {len(docs)} documents")

    except KeyboardInterrupt:
        print("\n[INFO] Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Scraping failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
