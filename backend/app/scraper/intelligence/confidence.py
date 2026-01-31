from typing import Dict, Any, List, Tuple

class ConfidenceScorer:
    """
    Calculates a numeric confidence score (0-100) for scraped data.
    """
    
    @staticmethod
    def calculate_score(extraction_confidence: float, validation_report: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Calculates a robust confidence score based on:
        (fields_found / fields_requested) - empty_penalty - error_penalty
        """
        row_count = validation_report.get("item_count", 0)
        errors = validation_report.get("errors", [])
        
        if row_count == 0:
            return 0.0, {"row_count": 0.0, "completeness": 0.0, "validity": 0.0}

        # 1. Completeness Score
        # We assume a base of 1.0 and penalize for empty/missing fields
        empty_field_errors = [e for e in errors if "empty" in e.lower() or "missing" in e.lower()]
        # Penalty: 0.1 per empty field, capped at 0.5 total penalty for completeness
        completeness_penalty = min(0.5, len(empty_field_errors) * 0.1)
        completeness_score = (1.0 - completeness_penalty) * 100

        # 2. Validity Score
        # Penalize for other errors like type mismatch or duplicate data
        other_errors = [e for e in errors if e not in empty_field_errors]
        # Penalty: 0.2 per validity error, capped at 0.5 total penalty
        validity_penalty = min(0.5, len(other_errors) * 0.2)
        validity_score = (1.0 - validity_penalty) * 100

        # 3. Extraction Base
        # Factor in the raw confidence from the extractor (LLM or Regex)
        base_score = extraction_confidence * 100

        components = {
            "completeness": float(round(completeness_score, 2)),
            "validity": float(round(validity_score, 2)),
            "extraction_base": float(round(base_score, 2))
        }

        # Final Weighted Formula
        # (Completeness * 0.4) + (Validity * 0.4) + (Extraction * 0.2)
        final_score = (completeness_score * 0.4) + (validity_score * 0.4) + (base_score * 0.2)
        
        return round(final_score, 2), components

    @staticmethod
    def needs_review(score: float, threshold: float = 85.0) -> bool:
        """Decides if the job needs human-in-the-loop review."""
        return score < threshold
