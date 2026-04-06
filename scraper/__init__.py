"""Adala Justice Portal Scraper Package"""
from .adala_scraper import scrape_adala, AdalaScraper, DocumentInfo
from .config import CATEGORIES, BASE_URL, OUTPUT_DIR

__all__ = ['scrape_adala', 'AdalaScraper', 'DocumentInfo', 'CATEGORIES', 'BASE_URL', 'OUTPUT_DIR']
