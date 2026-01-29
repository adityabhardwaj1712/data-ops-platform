# Job Cost Model (Internal)

## Purpose
To track actual effort against perceived complexity, enabling accurate pricing.

## Job Log

| Job ID | Date | Description | Complexity | Auto Scrape Time | HITL Time | Total Time | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **JOB-001** | *YYYY-MM-DD* | *Example: Books 500 pages* | Easy | 0.5h | 0.2h | 0.7h | *Smooth run* |
| **JOB-002** | *YYYY-MM-DD* | *Reference Job (Sprint 5)* | Easy | *TBD* | *TBD* | *TBD* | *Baseline* |
| **JOB-003** | *YYYY-MM-DD* | *Repeat Job (Sprint 6)* | Easy | *TBD* | *TBD* | *TBD* | *Comparison* |

## Complexity Definitions
- **Easy**: Static HTML, standard pagination, no blocking. (< 1h HITL)
- **Medium**: Dynamic content (API/JSON), light transformations, minor blocking. (1-2h HITL)
- **Hard**: Heavy JS, complex User-Agent rotation needed, custom headers, deep cleaning. (> 2h HITL)
