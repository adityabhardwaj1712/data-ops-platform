import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

from app.scraper.processing.field_extractor import extract_fields

logger = logging.getLogger(__name__)


class PreviewEngine:
    """
    Dry-run extraction engine to validate schemas and show partial success.
    Uses the SAME extraction logic as production scraping.
    """

    def preview(self, html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        if not html or not schema:
            return {
                "found": {},
                "missing": list(schema.keys()) if schema else [],
                "success_rate": 0.0,
                "status": "failed"
            }

        try:
            # ✅ CORE FIX: Use unified extractor
            extracted = extract_fields(html, schema)

            found = extracted or {}
            missing = [k for k in schema.keys() if k not in found]

            success_rate = (
                (len(found) / max(len(schema), 1)) * 100
            )

            return {
                "found": found,
                "missing": missing,
                "success_rate": round(success_rate, 2),
                "status": (
                    "success"
                    if not missing
                    else "partial"
                    if found
                    else "failed"
                )
            }

        except Exception as e:
            logger.error(f"Preview extraction failed: {e}")

            return {
                "found": {},
                "missing": list(schema.keys()),
                "success_rate": 0.0,
                "status": "failed"
            }
