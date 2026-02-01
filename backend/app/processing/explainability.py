from typing import Dict, Any

def build_explainability_report(task_result: Dict[str, Any], confidence: float) -> Dict[str, Any]:
    """
    Builds a structured explanation for the extraction result.
    """
    reasons = []
    warnings = []
    
    if confidence > 0.9:
        reasons.append("High DOM stability detected.")
        reasons.append("Selectors matched all requested fields.")
    elif confidence > 0.6:
        reasons.append("Most fields extracted successfully.")
        warnings.append("Some selectors might be fragile.")
    else:
        reasons.append("Partial extraction successful.")
        warnings.append("Low confidence: structural changes detected on target page.")
        warnings.append("Manual review recommended.")

    # Check for specific field issues
    found_fields = [k for k in task_result.keys() if k != "_confidence"]
    if not found_fields:
        warnings.append("No data extracted from the target page.")

    return {
        "confidence": confidence,
        "reasons": reasons,
        "warnings": warnings,
        "status": "EXCELLENT" if confidence > 0.9 else "STABLE" if confidence > 0.6 else "FRAGILE"
    }
