# Operator Runbook — Standard Operating Procedures (SOP)

This runbook defines the procedures for a human operator to run the DataOps platform predictably and safely.

## 1. Starting a New Job
1. **Define Schema**: Use one of the templates in `docs/USE_CASES.md`.
2. **Preflight Test**: Always run a `POST /api/scrape/preflight` first to verify selectors on a single page.
3. **Check Robots**: Verify crawl permission via `POST /api/robots/check`.
4. **Create Job**: Submit the job via `POST /api/scrape/`. Record the `job_id`.

## 2. Monitoring & HITL
1. **Monitor Flow**: Check job status regularly (`GET /api/scrape/{job_id}`).
2. **Identify Review Tasks**: If a job moves to `NEEDS_HITL`, fetch the task from `GET /api/hitl/pending`.
3. **Perform Audit**:
    - Compare the extracted JSON with the provided Screenshot.
    - Check for missing values or truncated text.
    - If selectors are broken, identify new ones (SOP: [Failure Patterns](file:///c:/Users/Lenovo/Desktop/data-ops-platform/data-ops-platform/docs/failure_patterns.md)).
4. **Submit Fix**: Use `POST /api/hitl/{task_id}/submit` with corrected data.
5. **Rerun if necessary**: If a config change was made, use `POST /api/scrape/{job_id}/rerun`.

## 3. Quality Gate & Delivery
1. **Final Audit**: Ensure job status is `COMPLETED`.
2. **Generate Package**: call `POST /api/export/` with `is_client_package: true`.
3. **Verify Bundle**: Download the ZIP and verify:
    - `data.csv` is not empty.
    - `metadata.json` shows >90% confidence or `human_reviewed: true`.
    - `artifacts/` folder contains clear screenshots of the source.

## 4. Archival & Cleanup
1. **Archive**: Once delivered, mark the job as `ARCHIVED` (via `PATCH /api/jobs/{job_id}`).
2. **Cleanup**: Exports are automatically deleted after 7 days. Monthly manual cleanup of `backend_fastapi/artifacts/` is recommended.

---
> [!IMPORTANT]
> **Safety First**: Never exceed 50 pages per job without explicit permission for the specific target domain.
