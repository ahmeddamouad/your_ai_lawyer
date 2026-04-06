"""
Adala Justice Portal Scraper

Scrapes legal PDF documents from https://adala.justice.gov.ma/

The website uses Next.js with server-side props. Documents are organized in folders
and accessed via /resources/{folder_id}. Each folder's files are in pageProps.folder.files.
PDF URLs are constructed as: https://adala.justice.gov.ma/api/{file.path}
"""
import asyncio
import aiohttp
import aiofiles
import json
import re
import os
from pathlib import Path
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from tqdm import tqdm

from .config import (
    BASE_URL, OUTPUT_DIR, REQUEST_DELAY, MAX_CONCURRENT,
    CATEGORIES, HEADERS
)


class DocumentInfo:
    """Represents a legal document."""
    def __init__(
        self,
        title: str,
        pdf_url: str,
        category: str,
        doc_id: Optional[int] = None,
        doc_type: Optional[str] = None,
        doc_number: Optional[str] = None,
        doc_date: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self.title = title
        self.pdf_url = pdf_url
        self.category = category
        self.doc_id = doc_id
        self.doc_type = doc_type
        self.doc_number = doc_number
        self.doc_date = doc_date
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "pdf_url": self.pdf_url,
            "category": self.category,
            "doc_id": self.doc_id,
            "doc_type": self.doc_type,
            "doc_number": self.doc_number,
            "doc_date": self.doc_date,
            "metadata": self.metadata
        }


class AdalaScraper:
    """
    Scraper for the Moroccan Ministry of Justice legal portal.

    The website (adala.justice.gov.ma) provides access to:
    - Constitutions (دساتير المملكة)
    - Organic Laws (قوانين تنظيمية)
    - Laws (قوانين)
    - Decrees (مراسيم)
    - Circulars (مناشير)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.base_url = BASE_URL
        self.output_dir = output_dir or OUTPUT_DIR
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.downloaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=120, connect=30)
        self.session = aiohttp.ClientSession(
            headers=HEADERS,
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page and return its HTML content."""
        async with self.semaphore:
            try:
                await asyncio.sleep(REQUEST_DELAY)
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    print(f"[WARN] Status {response.status} for {url}")
                    return None
            except Exception as e:
                print(f"[ERROR] Failed to fetch {url}: {e}")
                return None

    def extract_next_data(self, html: str) -> Optional[Dict]:
        """Extract __NEXT_DATA__ JSON from a Next.js page."""
        soup = BeautifulSoup(html, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if script and script.string:
            try:
                return json.loads(script.string)
            except json.JSONDecodeError as e:
                print(f"[WARN] Failed to parse __NEXT_DATA__: {e}")
                return None
        return None

    def build_pdf_url(self, file_path: str) -> str:
        """
        Build the full PDF URL from a file path.

        File paths are like: uploads/2024/01/30/filename-1706626006826.pdf
        Full URL: https://adala.justice.gov.ma/api/uploads/...
        """
        # Remove any leading slash
        file_path = file_path.lstrip('/')

        # The API endpoint for files
        return f"{self.base_url}/api/{file_path}"

    async def get_folder_documents(
        self,
        folder_id: int,
        category: str
    ) -> List[DocumentInfo]:
        """
        Get all documents from a specific folder.

        Fetches /resources/{folder_id} and extracts files from pageProps.content.files
        """
        documents = []

        url = f"{self.base_url}/resources/{folder_id}"
        print(f"[DEBUG] Fetching folder {folder_id}: {url}")

        html = await self.fetch_page(url)
        if not html:
            print(f"[WARN] Could not fetch folder {folder_id}")
            return documents

        next_data = self.extract_next_data(html)
        if not next_data:
            print(f"[WARN] No __NEXT_DATA__ found for folder {folder_id}")
            return documents

        try:
            page_props = next_data.get('props', {}).get('pageProps', {})
            # The data is in 'content', not 'folder'
            content = page_props.get('content', {})
            files = content.get('files', [])

            folder_name = content.get('name', f'Folder {folder_id}')
            print(f"[DEBUG] Folder '{folder_name}' has {len(files)} files")

            for file_item in files:
                # File path is directly on the file item
                file_path = file_item.get('path', '')

                if not file_path:
                    continue

                # Build PDF URL
                pdf_url = self.build_pdf_url(file_path)

                # Get document info - name is directly on file item
                title = file_item.get('name', 'Untitled')
                doc_id = file_item.get('id')

                doc = DocumentInfo(
                    title=title,
                    pdf_url=pdf_url,
                    category=category,
                    doc_id=doc_id,
                    metadata={
                        'folder_id': folder_id,
                        'folder_name': folder_name,
                        'file_path': file_path,
                        'language': file_item.get('language'),
                        'type': file_item.get('type'),
                        'created_at': file_item.get('createdAt'),
                    }
                )
                documents.append(doc)

            # Check for subfolders in 'folders' key
            subfolders = content.get('folders', [])
            if subfolders:
                print(f"[DEBUG] Folder {folder_id} has {len(subfolders)} subfolders")
                for subfolder in subfolders:
                    subfolder_id = subfolder.get('id')
                    if subfolder_id:
                        subfolder_docs = await self.get_folder_documents(subfolder_id, category)
                        documents.extend(subfolder_docs)

        except Exception as e:
            print(f"[ERROR] Error parsing folder {folder_id}: {e}")
            import traceback
            traceback.print_exc()

        return documents

    async def get_latest_releases(self) -> List[DocumentInfo]:
        """Get documents from the latest releases page."""
        documents = []

        url = f"{self.base_url}/new_releases"
        html = await self.fetch_page(url)

        if not html:
            return documents

        next_data = self.extract_next_data(html)
        if not next_data:
            return documents

        try:
            page_props = next_data.get('props', {}).get('pageProps', {})
            releases = page_props.get('latestReleases', [])

            print(f"[DEBUG] Found {len(releases)} latest releases")

            for item in releases:
                file_obj = item.get('File', {})
                file_path = file_obj.get('path', '')

                if not file_path:
                    continue

                pdf_url = self.build_pdf_url(file_path)
                title = item.get('title', '') or item.get('object', '') or file_obj.get('name', 'Untitled')

                # Determine category from lawTypeId
                law_type = item.get('LawType', {})
                law_type_name = law_type.get('name', 'unknown')

                doc = DocumentInfo(
                    title=title,
                    pdf_url=pdf_url,
                    category='latest_releases',
                    doc_id=item.get('id'),
                    doc_type=law_type_name,
                    doc_number=item.get('lawNumber'),
                    doc_date=item.get('gregorianDate'),
                    metadata=item
                )
                documents.append(doc)

        except Exception as e:
            print(f"[ERROR] Error parsing latest releases: {e}")

        return documents

    async def download_pdf(
        self,
        doc: DocumentInfo,
        output_subdir: str
    ) -> bool:
        """Download a single PDF file."""
        output_path = self.output_dir / output_subdir
        output_path.mkdir(parents=True, exist_ok=True)

        # Create safe filename from title
        safe_title = re.sub(r'[<>:"/\\|?*]', '', doc.title)  # Remove invalid chars
        safe_title = re.sub(r'\s+', ' ', safe_title).strip()  # Normalize whitespace
        safe_title = safe_title[:150] or f"document_{doc.doc_id or 'unknown'}"
        filename = f"{safe_title}.pdf"
        filepath = output_path / filename

        # Skip if already exists
        if filepath.exists():
            self.skipped_count += 1
            return True

        async with self.semaphore:
            try:
                await asyncio.sleep(REQUEST_DELAY)
                async with self.session.get(doc.pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()

                        # Verify it's a PDF
                        if not content or len(content) < 10:
                            print(f"[WARN] Empty response from {doc.pdf_url}")
                            self.failed_count += 1
                            return False

                        if content[:4] != b'%PDF':
                            # Check if it's HTML (error page)
                            if content[:5] == b'<!DOC' or content[:5] == b'<html':
                                print(f"[WARN] Got HTML instead of PDF: {doc.pdf_url}")
                            else:
                                print(f"[WARN] Not a valid PDF (starts with {content[:20]}): {doc.pdf_url}")
                            self.failed_count += 1
                            return False

                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(content)

                        self.downloaded_count += 1
                        return True
                    else:
                        print(f"[WARN] Status {response.status} downloading {doc.pdf_url}")
                        self.failed_count += 1
                        return False

            except Exception as e:
                print(f"[ERROR] Failed to download {doc.pdf_url}: {e}")
                self.failed_count += 1
                return False

    async def scrape_category(
        self,
        category_key: str,
        limit: Optional[int] = None,
        dry_run: bool = False
    ) -> List[DocumentInfo]:
        """Scrape all documents from a category."""
        if category_key not in CATEGORIES:
            raise ValueError(f"Unknown category: {category_key}")

        cat_info = CATEGORIES[category_key]
        print(f"\n[INFO] Scraping category: {cat_info['name_fr']} ({cat_info['name_ar']})")
        print(f"[INFO] Folder ID: {cat_info['resource_id']}")

        # Get documents from the folder
        documents = await self.get_folder_documents(
            cat_info['resource_id'],
            category_key
        )

        # Remove duplicates based on PDF URL
        seen_urls = set()
        unique_docs = []
        for doc in documents:
            if doc.pdf_url not in seen_urls:
                seen_urls.add(doc.pdf_url)
                unique_docs.append(doc)

        documents = unique_docs
        print(f"[INFO] Found {len(documents)} unique documents")

        if limit:
            documents = documents[:limit]
            print(f"[INFO] Limited to {limit} documents")

        if dry_run:
            for doc in documents:
                print(f"  - {doc.title}")
                print(f"    URL: {doc.pdf_url}")
            return documents

        # Download documents
        for doc in tqdm(documents, desc=f"Downloading {category_key}"):
            await self.download_pdf(doc, cat_info['output_dir'])

        return documents

    async def scrape_all(
        self,
        categories: Optional[List[str]] = None,
        limit_per_category: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, List[DocumentInfo]]:
        """Scrape documents from all (or specified) categories."""
        categories = categories or list(CATEGORIES.keys())
        results = {}

        for category in categories:
            try:
                docs = await self.scrape_category(
                    category,
                    limit=limit_per_category,
                    dry_run=dry_run
                )
                results[category] = docs
            except Exception as e:
                print(f"[ERROR] Failed to scrape {category}: {e}")
                import traceback
                traceback.print_exc()
                results[category] = []

        return results

    def print_summary(self):
        """Print download summary."""
        print(f"\n{'='*50}")
        print("DOWNLOAD SUMMARY")
        print(f"{'='*50}")
        print(f"Downloaded: {self.downloaded_count}")
        print(f"Skipped (existing): {self.skipped_count}")
        print(f"Failed: {self.failed_count}")
        print(f"{'='*50}")


async def scrape_adala(
    categories: Optional[List[str]] = None,
    limit: Optional[int] = None,
    output_dir: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, List[DocumentInfo]]:
    """
    Main scraping function.

    Args:
        categories: List of category keys to scrape (None = all)
        limit: Maximum documents per category
        output_dir: Output directory for PDFs
        dry_run: If True, only list documents without downloading

    Returns:
        Dictionary mapping category names to lists of DocumentInfo
    """
    output_path = Path(output_dir) if output_dir else OUTPUT_DIR

    async with AdalaScraper(output_path) as scraper:
        results = await scraper.scrape_all(
            categories=categories,
            limit_per_category=limit,
            dry_run=dry_run
        )
        scraper.print_summary()
        return results
