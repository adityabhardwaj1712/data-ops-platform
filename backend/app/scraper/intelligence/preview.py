import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PreviewEngine:
    """
    Dry-run extraction engine to validate schemas.

    ✔ Works on raw HTML
    ✔ Supports multi-match selectors
    ✔ Explains partial / failed results
    """

    MAX_ITEMS_PER_FIELD = 5
    MAX_TEXT_LENGTH = 150

    def preview(self, html: str, schema: Dict[str, Any]) -> Dict[str, Any]:

        if not html:
            return {
                "found": {},
                "missing": list(schema.keys()),
                "success_rate": 0.0,
                "status": "blocked_or_empty",
                "reason": "blocked_or_empty",
                "html_length": 0,
            }

        soup = BeautifulSoup(html, "lxml")
        found: Dict[str, Any] = {}
        missing = []

        for field, selector in schema.items():
            try:
                elements = soup.select(selector)

                if not elements:
                    missing.append(field)
                    continue

                values = []
                for el in elements[: self.MAX_ITEMS_PER_FIELD]:
                    text = el.get_text(" ", strip=True)
                    if text:
                        values.append(text[: self.MAX_TEXT_LENGTH])

                if values:
                    found[field] = values[0] if len(values) == 1 else values
                else:
                    missing.append(field)

            except Exception as e:
                logger.warning(
                    f"Preview selector failed [{field}={selector}]: {e}"
                )
                missing.append(field)

        success_rate = (len(found) / len(schema)) * 100 if schema else 0.0

        if success_rate == 100:
            status = "success"
            reason = None
        elif success_rate > 0:
            status = "partial"
            reason = "partial_match"
        else:
            status = "failed"
            reason = "selector_not_found"

        return {
            "found": found,
            "missing": missing,
            "success_rate": success_rate,
            "status": status,
            "reason": reason,
            "html_length": len(html),
        }
