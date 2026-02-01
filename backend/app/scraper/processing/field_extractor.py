from bs4 import BeautifulSoup
from typing import Dict, Any
import re


def extract_fields(html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    result: Dict[str, Any] = {}

    text_content = soup.get_text(" ", strip=True)

    for field in schema.keys():
        field_l = field.lower()
        value = None

        # ---------- TITLE / NAME ----------
        if field_l in ["title", "product_name", "name"]:
            # 1️⃣ <title>
            if soup.title and soup.title.string:
                value = soup.title.string.strip()

            # 2️⃣ <h1>
            if not value:
                h1 = soup.find("h1")
                if h1:
                    value = h1.get_text(strip=True)

        # ---------- PRICE ----------
        elif field_l == "price":
            price_match = re.search(r"(₹|\$|€)\s?\d[\d,]*(\.\d+)?", text_content)
            if price_match:
                value = price_match.group(0)

        # ---------- RATING ----------
        elif field_l == "rating":
            rating_match = re.search(r"\b\d(\.\d)?\b", text_content)
            if rating_match:
                value = rating_match.group(0)

        if value:
            result[field] = value

    return result
