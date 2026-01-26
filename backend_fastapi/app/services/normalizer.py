"""
4️⃣ DATA NORMALIZER
Normalizes data for consistency across sources

Different sites say:
- "Bengaluru" / "Bangalore" / "BLR"
- "Microsoft Corporation" / "Microsoft" / "MSFT"

This normalizer makes datasets clean and usable.
"""
from typing import Dict, Any, Optional, List
import re


class DataNormalizer:
    """
    Normalizes extracted data for consistency.
    
    Responsibilities:
    - Normalize locations
    - Normalize company names
    - Normalize currencies
    - Normalize dates
    - Clean whitespace
    """
    
    # Location aliases
    LOCATION_ALIASES = {
        # India
        "blr": "Bangalore",
        "bengaluru": "Bangalore",
        "bglr": "Bangalore",
        "hyd": "Hyderabad",
        "ncr": "Delhi NCR",
        "del": "Delhi",
        "new delhi": "Delhi",
        "mum": "Mumbai",
        "bombay": "Mumbai",
        "chn": "Chennai",
        "madras": "Chennai",
        "pun": "Pune",
        "kol": "Kolkata",
        "calcutta": "Kolkata",
        "gurgaon": "Gurugram",
        "ggn": "Gurugram",
        "noida": "Noida",
        
        # US
        "nyc": "New York City",
        "ny": "New York",
        "la": "Los Angeles",
        "sf": "San Francisco",
        "sfo": "San Francisco",
        "sea": "Seattle",
        "aus": "Austin",
        
        # Remote
        "wfh": "Remote",
        "work from home": "Remote",
        "remote work": "Remote",
        "anywhere": "Remote",
        "global": "Remote",
    }
    
    # Company name standardization
    COMPANY_ALIASES = {
        "msft": "Microsoft",
        "microsoft corporation": "Microsoft",
        "microsoft corp": "Microsoft",
        "goog": "Google",
        "google llc": "Google",
        "alphabet": "Google",
        "amzn": "Amazon",
        "amazon.com": "Amazon",
        "aws": "Amazon Web Services",
        "fb": "Meta",
        "facebook": "Meta",
        "meta platforms": "Meta",
        "aapl": "Apple",
        "apple inc": "Apple",
        "ibm corp": "IBM",
        "tcs": "Tata Consultancy Services",
        "infy": "Infosys",
        "wipro ltd": "Wipro",
        "hcl tech": "HCL Technologies",
    }
    
    # Currency normalization
    CURRENCY_PATTERNS = [
        (r'rs\.?\s*', '₹'),
        (r'inr\s*', '₹'),
        (r'rupees?\s*', '₹'),
        (r'usd\s*', '$'),
        (r'dollars?\s*', '$'),
        (r'eur\s*', '€'),
        (r'euros?\s*', '€'),
        (r'gbp\s*', '£'),
        (r'pounds?\s*', '£'),
    ]
    
    def normalize(self, data: Dict[str, Any], schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Normalize all fields in the data.
        
        Args:
            data: Raw extracted data
            schema: Optional schema with field hints
            
        Returns:
            Normalized data
        """
        normalized = {}
        
        for key, value in data.items():
            if value is None:
                normalized[key] = None
                continue
            
            # Clean whitespace first
            if isinstance(value, str):
                value = self._clean_whitespace(value)
            
            key_lower = key.lower()
            
            # Apply field-specific normalization
            if any(loc in key_lower for loc in ['location', 'city', 'place', 'address']):
                normalized[key] = self.normalize_location(value)
            
            elif any(comp in key_lower for comp in ['company', 'employer', 'organization']):
                normalized[key] = self.normalize_company(value)
            
            elif any(sal in key_lower for sal in ['salary', 'pay', 'compensation', 'price', 'cost']):
                normalized[key] = self.normalize_currency(value)
            
            elif any(date in key_lower for date in ['date', 'posted', 'created', 'updated']):
                normalized[key] = self.normalize_date(value)
            
            else:
                normalized[key] = value
        
        return normalized
    
    def normalize_location(self, location: str) -> str:
        """Normalize location string"""
        if not location:
            return location
        
        location_lower = location.lower().strip()
        
        # Check aliases
        for alias, standard in self.LOCATION_ALIASES.items():
            if alias in location_lower or location_lower == alias:
                # Preserve additional context
                if ',' in location:
                    parts = location.split(',')
                    parts[0] = standard
                    return ', '.join(p.strip() for p in parts)
                return standard
        
        # Title case
        return location.title()
    
    def normalize_company(self, company: str) -> str:
        """Normalize company name"""
        if not company:
            return company
        
        company_lower = company.lower().strip()
        
        # Check aliases
        for alias, standard in self.COMPANY_ALIASES.items():
            if alias == company_lower or alias in company_lower:
                return standard
        
        # Remove common suffixes for cleaner display
        suffixes = [' inc', ' inc.', ' llc', ' ltd', ' ltd.', ' corp', ' corp.', ' limited', ' pvt', ' private']
        result = company
        for suffix in suffixes:
            if result.lower().endswith(suffix):
                result = result[:-len(suffix)]
        
        return result.strip()
    
    def normalize_currency(self, value: str) -> str:
        """Normalize currency values"""
        if not value:
            return value
        
        result = value.lower()
        
        # Apply currency patterns
        for pattern, replacement in self.CURRENCY_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Normalize LPA/Lakh
        result = re.sub(r'(\d+)\s*lpa', r'\1 LPA', result, flags=re.IGNORECASE)
        result = re.sub(r'(\d+)\s*lakhs?', r'\1 Lakh', result, flags=re.IGNORECASE)
        result = re.sub(r'(\d+)\s*k\b', r'\1K', result, flags=re.IGNORECASE)
        
        # Format numbers with commas
        result = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1,', result)
        
        return result
    
    def normalize_date(self, date_str: str) -> str:
        """Normalize date strings to ISO format"""
        if not date_str:
            return date_str
        
        # Already ISO format
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        
        # Common patterns
        patterns = [
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', r'\3-\2-\1'),
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})', r'20\3-\2-\1'),
        ]
        
        for pattern, replacement in patterns:
            match = re.match(pattern, date_str)
            if match:
                return re.sub(pattern, replacement, date_str)
        
        return date_str
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean excessive whitespace"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    def normalize_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize a batch of items"""
        return [self.normalize(item) for item in items]


# Global instance
normalizer = DataNormalizer()
