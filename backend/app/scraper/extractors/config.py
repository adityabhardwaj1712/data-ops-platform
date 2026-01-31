from typing import Dict, Any, Tuple
from bs4 import BeautifulSoup

class ConfigExtractor:
    """
    Extracts data using fixed CSS selectors provided in a configuration schema.
    """
    def is_applicable(self, schema: Dict[str, Any]) -> bool:
        # If schema has selectors (non-empty dict), it's applicable
        return bool(schema)

    def extract(self, soup: BeautifulSoup, schema: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        data = {}
        for field, selector in schema.items():
            try:
                el = soup.select_one(selector)
                data[field] = el.get_text(strip=True) if el else None
            except:
                data[field] = None
                
        # Simple confidence: ratio of found fields
        found = sum(1 for v in data.values() if v is not None)
        confidence = (found / len(schema)) if schema else 0.0
        
        return data, confidence
