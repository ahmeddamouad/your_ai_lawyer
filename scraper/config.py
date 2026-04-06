"""Configuration for the Adala Justice Portal scraper."""
import os
from pathlib import Path

# Base URL
BASE_URL = "https://adala.justice.gov.ma"

# Output directory for downloaded PDFs
# Use absolute path based on this file's location
_SCRIPT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(os.getenv("SCRAPER_OUTPUT_DIR", str(_SCRIPT_DIR / "data" / "legal_pdfs")))

# Rate limiting (seconds between requests)
REQUEST_DELAY = 1.5

# Maximum concurrent downloads
MAX_CONCURRENT = 3

# Categories to scrape with their resource IDs
# These IDs are based on the website's folder structure from /resources
# The website organizes documents in folders, each with a unique ID
CATEGORIES = {
    # Legislative Texts (Parent ID: 1)
    "constitutions": {
        "name_fr": "Constitutions",
        "name_ar": "دساتير المملكة",
        "resource_id": 568,
        "output_dir": "constitutions"
    },
    "organic_laws": {
        "name_fr": "Lois organiques",
        "name_ar": "القوانين التنظيمية",
        "resource_id": 896,
        "output_dir": "organic_laws"
    },
    "justice_laws": {
        "name_fr": "Lois du systeme de justice",
        "name_ar": "قوانين منظومة العدالة",
        "resource_id": 2,
        "output_dir": "justice_laws"
    },
    "national_laws": {
        "name_fr": "Lois et legislations nationales",
        "name_ar": "قوانين وتشريعات وطنية",
        "resource_id": 12,
        "output_dir": "national_laws"
    },
    "constitutional_institutions": {
        "name_fr": "Lois des institutions constitutionnelles",
        "name_ar": "القوانين المنظمة للمؤسسات والهيئات الدستورية",
        "resource_id": 569,
        "output_dir": "constitutional_institutions"
    },

    # Circulars (Parent ID: 280)
    "circulars_ministry": {
        "name_fr": "Circulaires - Ministere",
        "name_ar": "مناشير الوزارة",
        "resource_id": 1066,
        "output_dir": "circulars/ministry"
    },
    "circulars_civil": {
        "name_fr": "Circulaires - Matiere civile",
        "name_ar": "مناشير المادة المدنية",
        "resource_id": 437,
        "output_dir": "circulars/civil"
    },
    "circulars_criminal": {
        "name_fr": "Circulaires - Matiere penale",
        "name_ar": "مناشير المادة الجنائية",
        "resource_id": 305,
        "output_dir": "circulars/criminal"
    },

    # Conventions and Treaties (Parent ID: 681)
    "conventions": {
        "name_fr": "Conventions et traites",
        "name_ar": "اتفاقيات ومعاهدات",
        "resource_id": 681,
        "output_dir": "conventions"
    },

    # Documentary References (Parent ID: 148)
    "references": {
        "name_fr": "References documentaires",
        "name_ar": "مراجع توثيقية",
        "resource_id": 148,
        "output_dir": "references"
    },
}

# HTTP headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,ar;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}
