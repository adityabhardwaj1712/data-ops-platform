import logging
from typing import Dict, Any, List, Tuple
from bs4 import BeautifulSoup
from app.schemas import ScrapeResult, ScrapeFailureReason

logger = logging.getLogger(__name__)

class PreviewEngine:
    """
    Dry-run extraction engine to validate schemas and show partial success.
    """
    
    def preview(self, html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        soup = BeautifulSoup(html, 'lxml')
        found = {}
        missing = []
        
        for field, selector in schema.items():
            try:
                # Basic CSS selector support
                el = soup.select_one(selector)
                if el:
                    found[field] = el.get_text(strip=True)[:100] # Truncated preview
                else:
                    missing.append(field)
            except Exception as e:
                logger.warning(f"Preview failed for selector {selector}: {e}")
                missing.append(field)
        
        success_rate = (len(found) / len(schema)) * 100 if schema else 0
        
        return {
            "found": found,
            "missing": missing,
            "success_rate": success_rate,
            "status": "success" if success_rate == 100 else "partial" if success_rate > 0 else "failed"
        }
