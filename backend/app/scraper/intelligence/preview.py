import logging
from typing import Dict, Any
from app.scraper.processing.field_extractor import extract_fields

logger = logging.getLogger(__name__)


class PreviewEngine:
    """
    Dry-run extraction engine using semantic extraction
    (same logic as real scrape).
    """

    def preview(self, html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        extracted = extract_fields(html, schema)

        missing = [k for k in schema.keys() if k not in extracted]

        success_rate = (
            (len(extracted) / len(schema)) * 100 if schema else 0
        )

        return {
            "found": extracted,
            "missing": missing,
            "success_rate": success_rate,
            "status": (
                "success"
                if success_rate == 100
                else "partial"
                if success_rate > 0
                else "failed"
            ),
        }
