import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# ✅ Semantic fallbacks for common fields
SEMANTIC_RULES = {
    "title": [
        "meta[property='og:title']",
        "meta[name='title']",
        "title",
        "h1",
        "h2"
    ],
    "price": [
        "[class*='price']",
        "[id*='price']",
        "span"
    ],
    "rating": [
        "[class*='rating']",
        "[aria-label*='rating']"
    ],
    "description": [
        "meta[name='description']",
        "[class*='description']",
        "p"
    ]
}


def extract_fields(html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    extracted: Dict[str, Any] = {}

    for field, field_type in schema.items():
        value = None

        # ✅ Semantic extraction
        selectors = SEMANTIC_RULES.get(field, [])

        for selector in selectors:
            el = soup.select_one(selector)
            if not el:
                continue

            # Meta tags
            if el.name == "meta":
                value = el.get("content")
            else:
                value = el.get_text(strip=True)

            if value:
                extracted[field] = value[:500]
                break

    return extracted
