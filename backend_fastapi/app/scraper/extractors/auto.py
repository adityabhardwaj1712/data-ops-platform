"""
Auto Extractor
Automatically selects best extraction method based on content
"""
from typing import Dict, Any, Tuple, Optional
import json
import re
from bs4 import BeautifulSoup

from app.scraper.extractors.css import CSSExtractor
from app.scraper.extractors.json_ld import JSONLDExtractor
from app.scraper.extractors.table import TableExtractor


class AutoExtractor:
    """
    Intelligent auto-extractor that chooses the best extraction method.
    
    Tries in order:
    1. JSON-LD (structured data)
    2. CSS selectors (if schema hints available)
    3. Table extraction (for tabular data)
    4. Falls back to raw content
    """
    
    def __init__(self):
        self.css_extractor = CSSExtractor()
        self.json_ld_extractor = JSONLDExtractor()
        self.table_extractor = TableExtractor()
    
    async def extract(
        self,
        html: str,
        markdown: str,
        schema: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Extract data using the most appropriate method.
        
        Args:
            html: Raw HTML content
            markdown: Cleaned markdown content
            schema: Expected data schema
            
        Returns:
            Tuple of (extracted_data, confidence_score)
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Try JSON-LD first (most reliable)
        json_ld_data = await self.json_ld_extractor.extract(soup, schema)
        if json_ld_data:
            return json_ld_data, 0.95
        
        # Try table extraction if schema looks tabular
        if self._is_tabular_schema(schema):
            table_data = await self.table_extractor.extract(soup, schema)
            if table_data:
                return table_data, 0.85
        
        # Try CSS extraction with common patterns
        css_data = await self.css_extractor.extract(soup, schema)
        if css_data and self._validate_extraction(css_data, schema):
            return css_data, 0.75
        
        # Fallback: extract from markdown using regex patterns
        fallback_data = self._extract_from_markdown(markdown, schema)
        if fallback_data:
            return fallback_data, 0.5
        
        return None, 0.0
    
    def _is_tabular_schema(self, schema: Dict[str, Any]) -> bool:
        """Check if schema looks like it expects tabular data"""
        table_keywords = ['rows', 'items', 'entries', 'records', 'list']
        return any(kw in str(schema).lower() for kw in table_keywords)
    
    def _validate_extraction(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate that extracted data matches schema structure"""
        if not data:
            return False
        
        schema_keys = set(schema.keys())
        data_keys = set(data.keys())
        
        # At least 50% of schema fields should be present
        overlap = len(schema_keys & data_keys)
        return overlap >= len(schema_keys) * 0.5
    
    def _extract_from_markdown(
        self,
        markdown: str,
        schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback extraction using regex patterns on markdown.
        """
        if not markdown:
            return None
        
        data = {}
        
        for field_name, field_def in schema.items():
            # Create patterns based on field name
            patterns = [
                rf'{field_name}[:\s]+([^\n]+)',
                rf'\*\*{field_name}\*\*[:\s]+([^\n]+)',
                rf'#{1,3}\s*{field_name}[:\s]*([^\n]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, markdown, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Clean up the value
                    value = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', value)  # Remove markdown links
                    data[field_name] = value
                    break
        
        return data if data else None
