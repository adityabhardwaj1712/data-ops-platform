"""
JSON-LD Extractor
Extracts structured data from JSON-LD and Schema.org markup
"""
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import json


class JSONLDExtractor:
    """
    Extracts structured data from JSON-LD markup.
    
    JSON-LD is the most reliable source of structured data
    as it's explicitly defined by the page author.
    """
    
    SCHEMA_TYPE_MAPPINGS = {
        "Product": ["name", "price", "description", "image", "brand", "sku"],
        "Article": ["headline", "author", "datePublished", "description", "image"],
        "JobPosting": ["title", "description", "datePosted", "employmentType", "hiringOrganization", "jobLocation"],
        "Person": ["name", "email", "telephone", "address", "jobTitle"],
        "Organization": ["name", "url", "logo", "address", "telephone"],
        "LocalBusiness": ["name", "address", "telephone", "openingHours", "priceRange"],
        "Recipe": ["name", "description", "image", "prepTime", "cookTime", "ingredients"],
        "Event": ["name", "startDate", "endDate", "location", "description"],
    }
    
    async def extract(
        self,
        soup: BeautifulSoup,
        schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract data from JSON-LD scripts.
        
        Args:
            soup: BeautifulSoup parsed HTML
            schema: Expected data schema
            
        Returns:
            Extracted data or None
        """
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        if not json_ld_scripts:
            return None
        
        all_data = []
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle @graph arrays
                if isinstance(data, dict) and '@graph' in data:
                    all_data.extend(data['@graph'])
                elif isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        
        if not all_data:
            return None
        
        # Try to find the best matching JSON-LD object
        best_match = self._find_best_match(all_data, schema)
        
        if best_match:
            return self._map_to_schema(best_match, schema)
        
        return None
    
    def _find_best_match(
        self,
        json_ld_objects: List[Dict],
        schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find the JSON-LD object that best matches the expected schema"""
        schema_fields = set(field.lower() for field in schema.keys())
        
        best_match = None
        best_score = 0
        
        for obj in json_ld_objects:
            if not isinstance(obj, dict):
                continue
            
            # Calculate match score
            obj_fields = set(key.lower().replace('@', '') for key in obj.keys())
            overlap = len(schema_fields & obj_fields)
            
            # Bonus for having @type
            if '@type' in obj:
                overlap += 0.5
            
            if overlap > best_score:
                best_score = overlap
                best_match = obj
        
        return best_match
    
    def _map_to_schema(
        self,
        json_ld: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map JSON-LD data to the expected schema"""
        result = {}
        
        for field_name in schema.keys():
            # Try direct mapping
            if field_name in json_ld:
                result[field_name] = self._clean_value(json_ld[field_name])
            # Try lowercase
            elif field_name.lower() in {k.lower(): k for k in json_ld}:
                for k, v in json_ld.items():
                    if k.lower() == field_name.lower():
                        result[field_name] = self._clean_value(v)
                        break
            # Try common aliases
            else:
                alias = self._get_alias(field_name)
                if alias and alias in json_ld:
                    result[field_name] = self._clean_value(json_ld[alias])
        
        return result
    
    def _clean_value(self, value: Any) -> Any:
        """Clean up a JSON-LD value"""
        if isinstance(value, dict):
            # Handle nested objects like {"@type": "Person", "name": "John"}
            if 'name' in value:
                return value['name']
            if '@value' in value:
                return value['@value']
            return str(value)
        elif isinstance(value, list):
            if len(value) == 1:
                return self._clean_value(value[0])
            return [self._clean_value(v) for v in value]
        return value
    
    def _get_alias(self, field_name: str) -> Optional[str]:
        """Get common field aliases"""
        aliases = {
            "title": "headline",
            "name": "headline",
            "price": "offers",
            "image": "thumbnailUrl",
            "date": "datePublished",
            "author": "creator",
        }
        return aliases.get(field_name.lower())
