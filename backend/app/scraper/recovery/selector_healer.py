import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SelectorHealer:
    """
    Heals broken CSS selectors by searching for behavioral matches in the DOM.
    """
    
    def heal(self, soup: BeautifulSoup, original_selector: str, field_name: str) -> Optional[str]:
        """
        Attempts to find a new selector for a field that returned no data.
        """
        logger.info(f"Attempting to heal selector for field '{field_name}' (Original: {original_selector})")
        
        # 1. Heuristic: Search by common text patterns (if field name is 'price', look for '$')
        if "price" in field_name.lower():
            price_tag = self._find_by_pattern(soup, ["$", "€", "£", "₹"], ["span", "div", "p"])
            if price_tag:
                return self._generate_css_path(price_tag)
                
        # 2. Heuristic: Search by tag name and neighboring text (placeholder logic)
        # In a real system, we'd use SelectorMeta (near_text, attributes)
        
        return None

    def _find_by_pattern(self, soup: BeautifulSoup, patterns: list, tags: list) -> Optional[Any]:
        for tag in tags:
            elements = soup.find_all(tag)
            for el in elements:
                text = el.get_text().strip()
                if any(p in text for p in patterns):
                    # Check if it's not a huge container
                    if len(text) < 50: 
                        return el
        return None

    def _generate_css_path(self, el: Any) -> str:
        """Generates a simple CSS path for an element."""
        parts = []
        curr = el
        while curr and curr.name != '[document]':
            part = curr.name
            if curr.get('id'):
                part += f"#{curr['id']}"
                parts.insert(0, part)
                break
            if curr.get('class'):
                part += f".{'.'.join(curr['class'])}"
            parts.insert(0, part)
            curr = curr.parent
        return " > ".join(parts)
