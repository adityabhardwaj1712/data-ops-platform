from typing import Dict, Any
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


COMMON_SELECTORS = {
    "title": ["h1", "h2", "title"],
    "price": [".price", ".price_color", "[itemprop=price]"],
    "rating": [".rating", ".star-rating"],
}


async def extract_fields(
    html: str,
    schema: Dict[str, Any],
    llm_client=None,   # optional
) -> Dict[str, Any]:

    soup = BeautifulSoup(html, "lxml")
    extracted = {}

    for field, rule in schema.items():

        # -----------------------
        # 1️⃣ MANUAL SELECTOR
        # -----------------------
        if rule not in ("string", "number", "text", "auto"):
            el = soup.select_one(rule)
            if el:
                extracted[field] = el.get_text(strip=True)
                continue

        # -----------------------
        # 2️⃣ HEURISTIC SELECTORS
        # -----------------------
        found = False
        for sel in COMMON_SELECTORS.get(field, []):
            el = soup.select_one(sel)
            if el:
                extracted[field] = el.get_text(strip=True)
                found = True
                break

        if found:
            continue

        # -----------------------
        # 3️⃣ AI SELECTOR (OPTIONAL)
        # -----------------------
        if llm_client:
            try:
                # Take a snippet of HTML to be token-efficient
                snippet = html[:10000] 
                suggested_selector = await llm_client.guess_selector(field, snippet)
                if suggested_selector:
                    el = soup.select_one(suggested_selector)
                    if el:
                        extracted[field] = el.get_text(strip=True)
            except Exception as e:
                logger.warning(f"AI selector failed for {field}: {e}")

    return extracted
