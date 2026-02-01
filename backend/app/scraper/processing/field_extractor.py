from bs4 import BeautifulSoup
from typing import Dict, Any
import re


def extract_fields(html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    result: Dict[str, Any] = {}

    full_text = soup.get_text(" ", strip=True)

    for field in schema.keys():
        field_l = field.lower()
        value = None

        # ---------- TITLE / NAME ----------
        if field_l in ("title", "product_name", "name"):
            # <title>
            if soup.title:
                value = soup.title.get_text(strip=True)

            # <h1>
            if not value:
                h1 = soup.find("h1")
                if h1:
                    value = h1.get_text(strip=True)

        # ---------- PRICE ----------
        elif field_l == "price":
            match = re.search(r"(₹|\$|€)\s?\d[\d,]*(\.\d+)?", full_text)
            if match:
                value = match.group(0)

        # ---------- RATING ----------
        elif field_l == "rating":
            match = re.search(r"\b\d(\.\d)?\b", full_text)
            if match:
                value = match.group(0)

        if value:
            result[field] = value

    return result
