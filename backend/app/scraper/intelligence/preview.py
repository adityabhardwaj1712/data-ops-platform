import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PreviewEngine:
    """
    Dry-run extraction engine to validate schemas and show partial success.
    Works directly on raw HTML.
    """

    def preview(self, html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        if not html:
            return {
                "found": {},
                "missing": list(schema.keys()),
                "success_rate": 0.0,
                "status": "blocked_or_empty",
                "html_length": 0,
            }

        soup = BeautifulSoup(html, "lxml")
        found = {}
        missing = []

        for field, selector in schema.items():
            try:
                el = soup.select_one(selector)
                if el:
                    found[field] = el.get_text(strip=True)[:150]
                else:
                    missing.append(field)
            except Exception as e:
                logger.warning(f"Preview selector failed [{field}={selector}]: {e}")
                missing.append(field)

        success_rate = (len(found) / len(schema)) * 100 if schema else 0

        return {
            "found": found,
            "missing": missing,
            "success_rate": success_rate,
            "status": (
                "success"
                if success_rate == 100
                else "partial"
                if success_rate > 0
                else "failed"
            ),
            "html_length": len(html),
        }
