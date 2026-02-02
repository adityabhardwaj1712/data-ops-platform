from typing import Dict, Any
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


COMMON_SELECTORS = {
    "title": ["h1", "h2", "title"],
    "price": [".price", ".price_color", "[itemprop=price]"],
    "rating": [".rating", ".star-rating"],
}


def extract_fields(
    html: str,
    schema: Dict[str, Any],
    ai_suggestor=None,   # optional
) -> Dict[str, Any]:

    soup = BeautifulSoup(html, "lxml")
    extracted = {}

    for field, rule in schema.items():

        # -----------------------
        # 1️⃣ MANUAL SELECTOR
        # -----------------------
        if rule != "string":
            el = soup.select_one(rule)
            if el:
                extracted[field] = el.get_text(strip=True)
            continue

        # -----------------------
        # 2️⃣ HEURISTIC SELECTORS
        # -----------------------
        for sel in COMMON_SELECTORS.get(field, []):
            el = soup.select_one(sel)
            if el:
                extracted[field] = el.get_text(strip=True)
                break

        if field in extracted:
            continue

        # -----------------------
        # 3️⃣ AI (OPTIONAL)
        # -----------------------
        if ai_suggestor:
            try:
                suggested = ai_suggestor(html, field)
                if suggested:
                    el = soup.select_one(suggested)
                    if el:
                        extracted[field] = el.get_text(strip=True)
            except Exception as e:
                logger.warning(f"AI selector failed for {field}: {e}")

    return extracted
