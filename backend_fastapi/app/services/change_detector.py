"""
Change Detection Service

Compares dataset versions to detect what changed between them.
Useful for monitoring data evolution and detecting new/removed items.
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass

from deepdiff import DeepDiff
import pandas as pd

from app.schemas import ChangeType, FieldChange, RecordChange, VersionDiff


@dataclass
class DatasetRecord:
    """Represents a record in a dataset"""
    id: str
    data: Dict[str, Any]
    confidence: float = 1.0


class ChangeDetector:
    """Service for detecting changes between dataset versions"""

    def __init__(self):
        self.id_fields = ['id', 'url', 'link', 'job_id', 'product_id']  # Common ID fields

    def compare_datasets(
        self,
        old_data: List[Dict[str, Any]],
        new_data: List[Dict[str, Any]],
        id_field: Optional[str] = None
    ) -> VersionDiff:
        """
        Compare two datasets and return the differences

        Args:
            old_data: Previous version data
            new_data: New version data
            id_field: Field to use as record identifier

        Returns:
            VersionDiff with detailed changes
        """
        # Convert to DatasetRecord objects
        old_records = self._normalize_records(old_data, id_field)
        new_records = self._normalize_records(new_data, id_field)

        # Create lookup dictionaries
        old_lookup = {record.id: record for record in old_records}
        new_lookup = {record.id: record for record in new_records}

        changes = []
        summary = defaultdict(int)

        # Find added and modified records
        for new_id, new_record in new_lookup.items():
            if new_id not in old_lookup:
                # New record added
                changes.append(RecordChange(
                    record_id=new_id,
                    change_type=ChangeType.ADDED,
                    field_changes=[],
                    overall_confidence=new_record.confidence
                ))
                summary[ChangeType.ADDED] += 1
            else:
                # Check for modifications
                old_record = old_lookup[new_id]
                field_changes = self._compare_records(old_record, new_record)

                if field_changes:
                    changes.append(RecordChange(
                        record_id=new_id,
                        change_type=ChangeType.MODIFIED,
                        field_changes=field_changes,
                        overall_confidence=new_record.confidence
                    ))
                    summary[ChangeType.MODIFIED] += 1
                else:
                    summary[ChangeType.UNCHANGED] += 1

        # Find removed records
        for old_id in old_lookup.keys():
            if old_id not in new_lookup:
                changes.append(RecordChange(
                    record_id=old_id,
                    change_type=ChangeType.REMOVED,
                    field_changes=[],
                    overall_confidence=old_lookup[old_id].confidence
                ))
                summary[ChangeType.REMOVED] += 1

        return VersionDiff(
            from_version=1,  # Will be set by caller
            to_version=2,    # Will be set by caller
            changes=changes,
            summary=dict(summary)
        )

    def _normalize_records(
        self,
        data: List[Dict[str, Any]],
        id_field: Optional[str] = None
    ) -> List[DatasetRecord]:
        """Convert raw data to DatasetRecord objects"""
        records = []

        for i, item in enumerate(data):
            # Determine record ID
            record_id = self._extract_record_id(item, id_field, i)

            # Extract confidence if available
            confidence = item.get('_confidence', item.get('confidence', 1.0))

            # Remove metadata fields from data
            clean_data = self._clean_metadata_fields(item)

            records.append(DatasetRecord(
                id=record_id,
                data=clean_data,
                confidence=confidence
            ))

        return records

    def _extract_record_id(self, item: Dict[str, Any], id_field: Optional[str], index: int) -> str:
        """Extract or generate a unique ID for the record"""
        if id_field and id_field in item:
            return str(item[id_field])

        # Try common ID fields
        for field in self.id_fields:
            if field in item and item[field]:
                return str(item[field])

        # Generate ID based on content hash or index
        content_str = json.dumps(item, sort_keys=True, default=str)
        return f"record_{index}_{hash(content_str) % 1000000}"

    def _clean_metadata_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Remove metadata fields from record data"""
        metadata_fields = {
            '_confidence', 'confidence', '_source_url', '_page',
            'source_url', 'page', 'extracted_at', 'created_at'
        }

        return {
            k: v for k, v in item.items()
            if k not in metadata_fields
        }

    def _compare_records(self, old_record: DatasetRecord, new_record: DatasetRecord) -> List[FieldChange]:
        """Compare two records and return field-level changes"""
        changes = []

        # Get all unique fields
        all_fields = set(old_record.data.keys()) | set(new_record.data.keys())

        for field in all_fields:
            old_value = old_record.data.get(field)
            new_value = new_record.data.get(field)

            # Handle None values
            if old_value is None and new_value is None:
                continue
            elif old_value is None:
                changes.append(FieldChange(
                    field=field,
                    old_value=None,
                    new_value=new_value,
                    change_type=ChangeType.MODIFIED,
                    confidence=new_record.confidence
                ))
            elif new_value is None:
                changes.append(FieldChange(
                    field=field,
                    old_value=old_value,
                    new_value=None,
                    change_type=ChangeType.MODIFIED,
                    confidence=new_record.confidence
                ))
            elif old_value != new_value:
                # Use deep diff for complex objects
                if isinstance(old_value, (dict, list)) or isinstance(new_value, (dict, list)):
                    diff = DeepDiff(old_value, new_value, ignore_order=True)
                    if diff:
                        changes.append(FieldChange(
                            field=field,
                            old_value=old_value,
                            new_value=new_value,
                            change_type=ChangeType.MODIFIED,
                            confidence=new_record.confidence
                        ))
                else:
                    changes.append(FieldChange(
                        field=field,
                        old_value=old_value,
                        new_value=new_value,
                        change_type=ChangeType.MODIFIED,
                        confidence=new_record.confidence
                    ))

        return changes

    def generate_change_report(self, diff: VersionDiff) -> Dict[str, Any]:
        """Generate a human-readable change report"""
        report = {
            "summary": {
                "total_changes": len(diff.changes),
                "added": diff.summary.get(ChangeType.ADDED, 0),
                "removed": diff.summary.get(ChangeType.REMOVED, 0),
                "modified": diff.summary.get(ChangeType.MODIFIED, 0),
                "unchanged": diff.summary.get(ChangeType.UNCHANGED, 0)
            },
            "significant_changes": []
        }

        # Find most significant changes
        for change in diff.changes:
            if change.change_type in [ChangeType.ADDED, ChangeType.REMOVED]:
                report["significant_changes"].append({
                    "type": change.change_type.value,
                    "record_id": change.record_id,
                    "confidence": change.overall_confidence
                })
            elif change.change_type == ChangeType.MODIFIED and change.field_changes:
                # Only include if there are actual field changes
                report["significant_changes"].append({
                    "type": change.change_type.value,
                    "record_id": change.record_id,
                    "fields_changed": len(change.field_changes),
                    "confidence": change.overall_confidence
                })

        # Sort by significance
        report["significant_changes"].sort(
            key=lambda x: x.get("confidence", 0),
            reverse=True
        )

        return report


# Global instance
change_detector = ChangeDetector()