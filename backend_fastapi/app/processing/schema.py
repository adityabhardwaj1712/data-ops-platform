"""
Schema Inference Engine (FREE)
Automatically detect data structure and types
"""

from typing import Dict, List, Any, Optional
from collections import Counter
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SchemaInference:
    """
    Infer schema from data samples.
    
    Detects:
    - Data types (string, number, boolean, date, etc.)
    - Patterns (email, URL, phone, etc.)
    - Constraints (nullable, unique, etc.)
    """
    
    def infer(self, data: List[Dict[str, Any]], sample_size: int = 100) -> Dict[str, Any]:
        """
        Infer schema from data.
        
        Args:
            data: List of data rows
            sample_size: Number of rows to analyze
        
        Returns:
            Inferred schema
        """
        if not data:
            return {}
        
        # Sample data
        sample = data[:min(sample_size, len(data))]
        
        # Get all fields
        all_fields = set()
        for row in sample:
            all_fields.update(row.keys())
        
        schema = {}
        for field in all_fields:
            schema[field] = self._infer_field(field, sample)
        
        return schema
    
    def _infer_field(self, field: str, sample: List[Dict]) -> Dict[str, Any]:
        """Infer schema for a single field."""
        values = [row.get(field) for row in sample]
        non_null_values = [v for v in values if v is not None and v != ""]
        
        # Basic stats
        total = len(values)
        non_null = len(non_null_values)
        null_count = total - non_null
        
        # Infer type
        inferred_type = self._infer_type(non_null_values)
        
        # Detect patterns
        pattern = self._detect_pattern(non_null_values)
        
        # Check uniqueness
        is_unique = len(set(str(v) for v in non_null_values)) == non_null
        
        return {
            "type": inferred_type,
            "pattern": pattern,
            "nullable": null_count > 0,
            "null_percentage": (null_count / total * 100) if total > 0 else 0,
            "unique": is_unique,
            "sample_values": non_null_values[:5] if non_null_values else []
        }
    
    def _infer_type(self, values: List[Any]) -> str:
        """Infer data type from values."""
        if not values:
            return "unknown"
        
        type_counts = Counter()
        
        for value in values:
            if isinstance(value, bool):
                type_counts["boolean"] += 1
            elif isinstance(value, int):
                type_counts["integer"] += 1
            elif isinstance(value, float):
                type_counts["number"] += 1
            elif isinstance(value, str):
                # Try to parse as number
                try:
                    float(value)
                    type_counts["number"] += 1
                except ValueError:
                    # Try to parse as date
                    if self._is_date(value):
                        type_counts["date"] += 1
                    else:
                        type_counts["string"] += 1
            else:
                type_counts["unknown"] += 1
        
        # Return most common type
        if type_counts:
            return type_counts.most_common(1)[0][0]
        return "unknown"
    
    def _detect_pattern(self, values: List[Any]) -> Optional[str]:
        """Detect common patterns (email, URL, phone, etc.)."""
        if not values:
            return None
        
        str_values = [str(v) for v in values if v]
        if not str_values:
            return None
        
        # Email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if sum(1 for v in str_values if re.match(email_pattern, v)) / len(str_values) > 0.8:
            return "email"
        
        # URL pattern
        url_pattern = r'^https?://[^\s]+$'
        if sum(1 for v in str_values if re.match(url_pattern, v)) / len(str_values) > 0.8:
            return "url"
        
        # Phone pattern
        phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
        if sum(1 for v in str_values if re.match(phone_pattern, v)) / len(str_values) > 0.8:
            return "phone"
        
        # UUID pattern
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if sum(1 for v in str_values if re.match(uuid_pattern, v.lower())) / len(str_values) > 0.8:
            return "uuid"
        
        return None
    
    def _is_date(self, value: str) -> bool:
        """Check if value is a date."""
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        
        return False


class SchemaDriftDetector:
    """
    Detect schema changes between versions.
    
    Detects:
    - New fields
    - Removed fields
    - Type changes
    - Pattern changes
    """
    
    def detect_drift(self, old_schema: Dict, new_schema: Dict) -> Dict[str, Any]:
        """
        Detect schema drift.
        
        Returns:
            Drift report
        """
        old_fields = set(old_schema.keys())
        new_fields = set(new_schema.keys())
        
        # New and removed fields
        added_fields = new_fields - old_fields
        removed_fields = old_fields - new_fields
        common_fields = old_fields & new_fields
        
        # Type changes
        type_changes = []
        for field in common_fields:
            old_type = old_schema[field].get("type")
            new_type = new_schema[field].get("type")
            if old_type != new_type:
                type_changes.append({
                    "field": field,
                    "old_type": old_type,
                    "new_type": new_type
                })
        
        # Nullability changes
        nullability_changes = []
        for field in common_fields:
            old_nullable = old_schema[field].get("nullable", True)
            new_nullable = new_schema[field].get("nullable", True)
            if old_nullable != new_nullable:
                nullability_changes.append({
                    "field": field,
                    "old_nullable": old_nullable,
                    "new_nullable": new_nullable
                })
        
        # Calculate drift severity
        severity = self._calculate_severity(
            len(added_fields),
            len(removed_fields),
            len(type_changes),
            len(nullability_changes)
        )
        
        return {
            "has_drift": bool(added_fields or removed_fields or type_changes or nullability_changes),
            "severity": severity,
            "added_fields": list(added_fields),
            "removed_fields": list(removed_fields),
            "type_changes": type_changes,
            "nullability_changes": nullability_changes,
            "summary": self._generate_summary(
                added_fields, removed_fields, type_changes, nullability_changes
            )
        }
    
    def _calculate_severity(self, added: int, removed: int, type_changes: int, null_changes: int) -> str:
        """Calculate drift severity."""
        # Breaking changes (removed fields, type changes)
        breaking = removed + type_changes
        
        if breaking > 0:
            return "high"  # Breaking changes
        elif added > 0 or null_changes > 0:
            return "medium"  # Non-breaking changes
        else:
            return "low"  # No changes
    
    def _generate_summary(self, added, removed, type_changes, null_changes) -> str:
        """Generate human-readable summary."""
        parts = []
        
        if added:
            parts.append(f"{len(added)} field(s) added")
        if removed:
            parts.append(f"{len(removed)} field(s) removed")
        if type_changes:
            parts.append(f"{len(type_changes)} type change(s)")
        if null_changes:
            parts.append(f"{len(null_changes)} nullability change(s)")
        
        if not parts:
            return "No schema changes detected"
        
        return ", ".join(parts)
