# Weekly Review Ritual

Goal: Continuous improvement of the scraping engine through data-driven reflection.

## Schedule
**Frequency**: Once per week (e.g., Friday Afternoon).
**Duration**: 30-45 minutes.

## Checklist

### 1. Review Failure Reasons
-   Filter jobs from the last 7 days by `JobStatus.FAILED`.
-   Tally the `failure_reason` counts.
-   **Action**: If `ANTI_BOT_SUSPECTED` is > 20%, investigate proxy health or user-agent rotation.

### 2. Analyze HITL Frequency
-   Compare the number of `SCRAPE` tasks vs `HUMAN` review tasks.
-   **Action**: Identify the top 3 domains requiring human intervention. Can we improve their specific `JOB_TEMPLATES`?

### 3. Verification Accuracy
-   Spot-check 5 "Self-Validated" jobs (Confidence > 90).
-   **Action**: Did the system miss any errors? If yes, tighten the `ScrapeValidator` rules for that field type.

### 4. Template Refinement
-   Update `docs/JOB_TEMPLATES.md` based on new patterns found during the week.
-   **Action**: Add specific CSS selector tips for tricky sites.

### 5. Success Story
-   Note one job that was "unscrapable" before but is now automated.
-   **Resource**: Update `docs/FAILURE_PATTERNS.md` with the fix.

---
*Stability is built one reflection at a time.*
