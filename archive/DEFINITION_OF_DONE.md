# Definition of Done (DoD) - Scraping Jobs

A scraping job is considered **DONE** only when it satisfies all of the following criteria:

## 1. Data Integrity & Validation
- ✅ **Schema Compliance**: Extracted JSON matches the requested schema exactly.
- ✅ **Zero Emptiness**: All fields marked as `required` are populated with non-null, non-empty values.
- ✅ **No Duplicates**: The dataset contains zero duplicate rows (unless explicitly allowed).

## 2. Trust & Scoring
- ✅ **Confidence Threshold**: The numeric score must be ≥ 85 for automated completion.
- ✅ **Human-Approved**: If Score < 85, a human has reviewed the artifacts, corrected selectors, and re-run the job.
- ✅ **Final Metadata**: Output contains `"human_reviewed": true` (if applicable) and a valid timestamp.

## 3. Artifact Auditing
- ✅ **HTML Dump**: A full HTML artifact exists in `data/artifacts/[job_id].html`.
- ✅ **Screenshot**: At least one screenshot exists showing the rendered state of the target URL.

## 4. Delivery & Export
- ✅ **Versioned Storage**: The final data is saved to `data/deliveries/job_[id]_v[N].json`.
- ✅ **Exported**: The data has been successfully exported to the requested target (Excel/CSV/JSON) if required.

---
*If it’s not valid, it’s not delivered.*
