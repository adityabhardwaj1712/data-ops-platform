# Standard Scrape Job Definition

This document defines the lifecycle and requirements of a "Standard Scrape Job" within the DataOps Platform (Consulting Engine Mode).

## 1. Input Requirements
To start a job, the following information is **MANDATORY**:
- **Source URL**: The exact starting point for data extraction.
- **Data Type**: One of `listing`, `directory`, or `search_results`.
- **Target Schema**: A JSON definition of the fields required (e.g., `title`, `price`).
- **Required Fields**: Specification of which fields MUST be present for automated success.

## 2. Step-by-Step Lifecycle
1.  **Job Creation**: Request submitted via API or CLI.
2.  **Strategy Detection**: The `Analyzer` selects the most efficient strategy (`static`, `browser`, or `stealth`) based on site protection and dynamic content.
3.  **Content Fetch**: The system attempts to fetch the page content.
4.  **Extraction**: Data is extracted using the defined schema (prioritizing CSS selectors).
5.  **Validation**: Strict checks for schema compliance, non-empty required fields, and data types.
6.  **Confidence Check**: A score (0-100) is calculated based on extraction quality and validation results.
7.  **Routing**:
    -   If Score ≥ 85: Direct delivery.
    -   If Score < 85: Job routed to **Human-In-The-Loop (HITL)** for manual fix.
8.  **Final Output**: Clean, versioned data is delivered to a standardized location.

## 3. Definition of DONE
A job is considered **DONE** only if:
- ✅ Data passes all validation rules.
- ✅ Confidence score is ≥ 85 OR a human has explicitly approved the extraction.
- ✅ Full artifacts (HTML dump & Screenshot) are stored for audit.
- ✅ Output is delivered with mandatory audit metadata.

---
*Predictability is the foundation of data trust.*
