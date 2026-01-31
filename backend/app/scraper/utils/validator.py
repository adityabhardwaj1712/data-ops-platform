from typing import List, Dict, Any, Optional

class ScrapeValidator:
    """
    Performs strict data validation after scraping.
    """
    
    @staticmethod
    def validate(data: Any, schema: Dict[str, Any], required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validates extracted data against rules.
        Returns a report of errors found.
        """
        errors = []
        
        # 1. Row count sanity check
        if not data:
            errors.append("No data extracted")
            return {"valid": False, "errors": errors}

        items = data if isinstance(data, list) else [data]
        
        # 2. Empty field check & Required field presence
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"Item {i} is not a dictionary")
                continue
                
            for field, value in item.items():
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"Field '{field}' is empty in item {i}")
            
            if required_fields:
                for rf in required_fields:
                    if rf not in item or item[rf] is None:
                        errors.append(f"Required field '{rf}' is missing in item {i}")

        # 3. Duplicate row check
        if isinstance(data, list) and len(data) > 1:
            # Simple string representation comparison for duplicates
            seen = set()
            for i, item in enumerate(data):
                item_str = str(item)
                if item_str in seen:
                    errors.append(f"Duplicate item found at index {i}")
                seen.add(item_str)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "item_count": len(items)
        }
