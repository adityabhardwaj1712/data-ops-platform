import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PreviewEngine:
    """
    Dry-run extraction engine to validate schemas and show partial success.
    SAFE: Handles blocked / empty HTML.
    SMART: Handles bad schema input.
    """

    def preview(self, html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        # ---------------------------
        # 1. Sanity check
        # ---------------------------
        if not html or len(html) < 200:
            return {
                "found": {},
                "missing": list(schema.keys()),
                "success_rate": 0.0,
                "status": "blocked_or_empty",
                "html_length": len(html) if html else 0,
            }

        soup = BeautifulSoup(html, "lxml")
        found = {}
        missing = []

        # ---------------------------
        # 2. Extract fields
        # ---------------------------
        for field, selector in schema.items():
            try:
                # 🔥 FIX: user sends "string" instead of CSS
                if selector == "string":
                    selector = "body"

                el = soup.select_one(selector)
                if el:
                    found[field] = el.get_text(strip=True)[:120]
                else:
                    missing.append(field)

            except Exception as e:
                logger.warning(f"Preview selector failed [{field}={selector}]: {e}")
                missing.append(field)

        # ---------------------------
        # 3. Score
        # ---------------------------
        success_rate = round((len(found) / max(len(schema), 1)) * 100, 2)

        status = (
            "success"
            if success_rate == 100
            else "partial"
            if success_rate > 0
            else "failed"
        )

        return {
            "found": found,
            "missing": missing,
            "success_rate": success_rate,
            "status": status,
            "html_length": len(html),
        }
