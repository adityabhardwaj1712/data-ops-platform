"""
Table Extractor
Extracts data from HTML tables
"""
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup


class TableExtractor:
    """
    Extracts data from HTML tables.
    
    Handles various table formats:
    - Standard tables with headers
    - Key-value tables
    - Data tables
    """
    
    async def extract(
        self,
        soup: BeautifulSoup,
        schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract data from tables.
        
        Args:
            soup: BeautifulSoup parsed HTML
            schema: Expected data schema
            
        Returns:
            Extracted data or None
        """
        tables = soup.find_all('table')
        
        if not tables:
            return None
        
        all_extracted = {}
        
        for table in tables:
            # Try key-value extraction
            kv_data = self._extract_key_value(table, schema)
            if kv_data:
                all_extracted.update(kv_data)
            
            # Try header-based extraction
            header_data = self._extract_with_headers(table, schema)
            if header_data:
                all_extracted.update(header_data)
        
        return all_extracted if all_extracted else None
    
    def _extract_key_value(
        self,
        table,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract from key-value style tables (2 columns)"""
        data = {}
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) == 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                
                # Check if key matches any schema field
                for field_name in schema.keys():
                    if field_name.lower() in key or key in field_name.lower():
                        data[field_name] = value
                        break
        
        return data
    
    def _extract_with_headers(
        self,
        table,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract using table headers"""
        headers = []
        header_row = table.find('thead')
        
        if header_row:
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all('th')]
        else:
            # Try first row as headers
            first_row = table.find('tr')
            if first_row:
                headers = [cell.get_text(strip=True).lower() for cell in first_row.find_all(['th', 'td'])]
        
        if not headers:
            return {}
        
        # Map headers to schema fields
        header_to_field = {}
        for i, header in enumerate(headers):
            for field_name in schema.keys():
                if field_name.lower() in header or header in field_name.lower():
                    header_to_field[i] = field_name
                    break
        
        if not header_to_field:
            return {}
        
        # Extract first data row
        data = {}
        data_rows = table.find_all('tr')[1:]  # Skip header
        
        if data_rows:
            first_data_row = data_rows[0]
            cells = first_data_row.find_all(['td', 'th'])
            
            for col_idx, field_name in header_to_field.items():
                if col_idx < len(cells):
                    data[field_name] = cells[col_idx].get_text(strip=True)
        
        return data
    
    def extract_all_rows(
        self,
        soup: BeautifulSoup,
        schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract all rows from tables (for list data)"""
        tables = soup.find_all('table')
        all_rows = []
        
        for table in tables:
            headers = []
            header_row = table.find('thead')
            
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            else:
                first_row = table.find('tr')
                if first_row:
                    headers = [cell.get_text(strip=True) for cell in first_row.find_all(['th', 'td'])]
            
            if headers:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all(['td', 'th'])
                    row_data = {}
                    
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            row_data[headers[i]] = cell.get_text(strip=True)
                    
                    if row_data:
                        all_rows.append(row_data)
        
        return all_rows
