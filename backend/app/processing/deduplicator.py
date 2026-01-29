"""
5️⃣ DEDUPLICATION ENGINE
Removes duplicate entries from scraped data

If you scrape 10 sites, same item appears multiple times.
This keeps the best-confidence record and discards duplicates.

MANDATORY for real datasets.
"""
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import hashlib
import json


@dataclass
class DedupeResult:
    """Result of deduplication"""
    unique_items: List[Dict[str, Any]]
    duplicates_removed: int
    original_count: int
    duplicate_groups: Dict[str, List[Dict[str, Any]]]  # hash -> items


class Deduplicator:
    """
    Deduplication engine for scraped data.
    
    Logic:
    - Hash key fields (e.g., title + company + location)
    - Keep the record with highest confidence
    - Discard duplicates
    """
    
    def __init__(self, key_fields: List[str] = None):
        """
        Args:
            key_fields: Fields to use for deduplication hash.
                       If None, uses all fields.
        """
        self.key_fields = key_fields
    
    def deduplicate(
        self,
        items: List[Dict[str, Any]],
        key_fields: List[str] = None,
        keep: str = "highest_confidence"
    ) -> DedupeResult:
        """
        Deduplicate a list of items.
        
        Args:
            items: List of extracted items
            key_fields: Fields to use for hash (overrides init)
            keep: Strategy - "highest_confidence", "first", "last"
            
        Returns:
            DedupeResult with unique items
        """
        fields = key_fields or self.key_fields
        
        # Group by hash
        groups: Dict[str, List[Dict[str, Any]]] = {}
        
        for item in items:
            item_hash = self._compute_hash(item, fields)
            if item_hash not in groups:
                groups[item_hash] = []
            groups[item_hash].append(item)
        
        # Select best from each group
        unique_items = []
        
        for item_hash, group in groups.items():
            if len(group) == 1:
                unique_items.append(group[0])
            else:
                best = self._select_best(group, keep)
                unique_items.append(best)
        
        return DedupeResult(
            unique_items=unique_items,
            duplicates_removed=len(items) - len(unique_items),
            original_count=len(items),
            duplicate_groups={k: v for k, v in groups.items() if len(v) > 1}
        )
    
    def _compute_hash(self, item: Dict[str, Any], key_fields: List[str] = None) -> str:
        """Compute hash for an item based on key fields"""
        if key_fields:
            # Use only specified fields
            hash_data = {k: self._normalize_for_hash(item.get(k, '')) for k in key_fields}
        else:
            # Use all fields except metadata
            hash_data = {
                k: self._normalize_for_hash(v)
                for k, v in item.items()
                if not k.startswith('_')  # Skip metadata fields
            }
        
        # Create stable JSON string
        json_str = json.dumps(hash_data, sort_keys=True, default=str)
        
        # Compute hash
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def _normalize_for_hash(self, value: Any) -> str:
        """Normalize value for consistent hashing"""
        if value is None:
            return ""
        
        if isinstance(value, str):
            # Lowercase, remove extra whitespace, remove punctuation
            import re
            normalized = value.lower().strip()
            normalized = re.sub(r'\s+', ' ', normalized)
            normalized = re.sub(r'[^\w\s]', '', normalized)
            return normalized
        
        return str(value)
    
    def _select_best(self, group: List[Dict[str, Any]], keep: str) -> Dict[str, Any]:
        """Select the best item from a duplicate group"""
        if keep == "first":
            return group[0]
        
        elif keep == "last":
            return group[-1]
        
        elif keep == "highest_confidence":
            # Sort by confidence (highest first)
            sorted_group = sorted(
                group,
                key=lambda x: x.get('_confidence', x.get('confidence', 0)),
                reverse=True
            )
            return sorted_group[0]
        
        else:
            return group[0]
    
    def find_similar(
        self,
        item: Dict[str, Any],
        items: List[Dict[str, Any]],
        key_fields: List[str] = None,
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find items similar to the given item.
        Uses fuzzy matching instead of exact hash.
        """
        from difflib import SequenceMatcher
        
        fields = key_fields or self.key_fields or list(item.keys())
        similar = []
        
        item_text = ' '.join(str(item.get(f, '')) for f in fields)
        
        for other in items:
            if other is item:
                continue
            
            other_text = ' '.join(str(other.get(f, '')) for f in fields)
            
            ratio = SequenceMatcher(None, item_text.lower(), other_text.lower()).ratio()
            
            if ratio >= threshold:
                similar.append(other)
        
        return similar


# Default instance with common job listing fields
job_deduplicator = Deduplicator(key_fields=['title', 'company', 'location'])

# Generic deduplicator
deduplicator = Deduplicator()
