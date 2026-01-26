"""
CSS Selector Extractor
Extracts data using CSS selectors with intelligent pattern matching
"""
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup


# Common CSS selector patterns for various data types
COMMON_SELECTORS = {
    "title": ["h1", ".title", ".headline", "[itemprop='name']", ".product-title"],
    "name": ["h1", ".name", "[itemprop='name']", ".product-name"],
    "price": [".price", "[itemprop='price']", ".product-price", ".cost", "[data-price]"],
    "description": [".description", "[itemprop='description']", ".product-description", ".desc", "p.description"],
    "image": ["img[itemprop='image']", ".product-image img", ".main-image img", "img.primary"],
    "rating": [".rating", "[itemprop='ratingValue']", ".stars", ".review-rating"],
    "author": [".author", "[itemprop='author']", ".byline", ".writer"],
    "date": [".date", "[itemprop='datePublished']", "time", ".published"],
    "company": [".company", ".company-name", ".employer"],
    "location": [".location", "[itemprop='address']", ".job-location", ".address"],
    "salary": [".salary", ".compensation", ".pay", ".wage"],
}


class CSSExtractor:
    """
    CSS selector-based data extractor.
    
    Uses common patterns and intelligent guessing to extract
    data based on schema field names.
    """
    
    async def extract(
        self,
        soup: BeautifulSoup,
        schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract data using CSS selectors.
        
        Args:
            soup: BeautifulSoup parsed HTML
            schema: Expected data schema
            
        Returns:
            Extracted data dictionary or None
        """
        data = {}
        
        for field_name, field_def in schema.items():
            value = self._extract_field(soup, field_name)
            if value:
                data[field_name] = value
        
        return data if data else None
    
    def _extract_field(self, soup: BeautifulSoup, field_name: str) -> Optional[str]:
        """Extract a single field using various selector strategies"""
        field_lower = field_name.lower()
        
        # Try known selectors for this field type
        if field_lower in COMMON_SELECTORS:
            for selector in COMMON_SELECTORS[field_lower]:
                element = soup.select_one(selector)
                if element:
                    return self._get_element_value(element)
        
        # Try class/id matching
        selectors_to_try = [
            f".{field_name}",
            f".{field_lower}",
            f"#{field_name}",
            f"#{field_lower}",
            f"[class*='{field_lower}']",
            f"[id*='{field_lower}']",
            f"[itemprop='{field_lower}']",
            f"[data-{field_lower}]",
        ]
        
        for selector in selectors_to_try:
            try:
                element = soup.select_one(selector)
                if element:
                    return self._get_element_value(element)
            except Exception:
                continue
        
        return None
    
    def _get_element_value(self, element) -> str:
        """Get the value from an element (text, attribute, etc.)"""
        # Check for specific attributes first
        if element.get('content'):
            return element['content']
        if element.get('value'):
            return element['value']
        if element.name == 'img':
            return element.get('src', element.get('data-src', ''))
        if element.name == 'a':
            return element.get('href', element.get_text(strip=True))
        if element.get('datetime'):
            return element['datetime']
        
        # Default to text content
        return element.get_text(strip=True)
    
    def extract_with_selectors(
        self,
        soup: BeautifulSoup,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract using explicit selector mapping.
        
        Args:
            soup: BeautifulSoup parsed HTML
            selectors: Mapping of field names to CSS selectors
            
        Returns:
            Extracted data
        """
        data = {}
        
        for field_name, selector in selectors.items():
            element = soup.select_one(selector)
            if element:
                data[field_name] = self._get_element_value(element)
        
        return data
