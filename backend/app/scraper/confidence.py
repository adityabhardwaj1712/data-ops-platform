from typing import Dict, Any, List, Tuple

class ConfidenceScorer:
    """
    Calculates a numeric confidence score (0-100) for scraped data.
    """
    
    @staticmethod
    def calculate_score(extraction_confidence: float, validation_report: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Combines model confidence with validation results.
        
        Returns: (final_score, components)
        """
        # 1. Row Count Score (0-100)
        # Assuming we expect at least 1 row if extraction_confidence > 0
        row_count = validation_report.get("item_count", 0)
        row_count_score = 100 if row_count > 0 else 0
        
        # 2. Field Completeness (0-100)
        # Based on validation errors related to empty fields
        errors = validation_report.get("errors", [])
        empty_field_errors = [e for e in errors if "empty" in e.lower() or "missing" in e.lower()]
        
        total_fields_checked = row_count * 5 # Representative number if we don't know schema size
        # Better: calculate completeness from validation report if possible
        # For now, 10-point penalty per empty field error
        field_completeness = max(0, 100 - (len(empty_field_errors) * 10))
        
        # 3. Schema Match (0-100)
        # Non-empty field errors (type mismatches, etc.)
        schema_errors = [e for e in errors if e not in empty_field_errors]
        schema_match = max(0, 100 - (len(schema_errors) * 20))
        
        # Weighted average or strategy-based score
        # base_score = extraction_confidence * 100
        # For professional system, we use these components:
        components = {
            "row_count": float(row_count_score),
            "field_completeness": float(field_completeness),
            "schema_match": float(schema_match)
        }
        
        # Final score is weighted average
        final_score = (row_count_score * 0.2) + (field_completeness * 0.4) + (schema_match * 0.4)
        
        # Factor in extraction confidence (e.g. LLM confidence)
        final_score = (final_score + (extraction_confidence * 100)) / 2
        
        return round(final_score, 2), components

    @staticmethod
    def needs_review(score: float, threshold: float = 85.0) -> bool:
        """Decides if the job needs human-in-the-loop review."""
        return score < threshold
