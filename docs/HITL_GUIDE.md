# HITL Guide (Human-In-The-Loop)

This guide is for human reviewers responsible for fixing failed or low-confidence scrapes.

## 1. Entering the Flow
When a job is routed to `HUMAN` review (Confidence < 85), navigate to:
`http://localhost:3000/review/[job_id]`

## 2. Inspection Steps
1. **View Screenshot**: Look at the "Screenshot" tab to see exactly what the scraper saw. Was it blocked? Did the page load correctly?
2. **Audit Data**: Review the "Extracted Data" tab. Are fields missing? Is the format wrong?
3. **Check Validation**: Look at the "Validation Failures" list for specific guidance (e.g., "Field 'price' is empty").

## 3. Fixing & Re-running
1. Locate the **Fix Selectors** panel.
2. Update the CSS selectors based on your inspection of the artifact.
3. Click **Re-run Scrape**.

## 4. Successful Review
- If the re-run succeeds and confidence is high, the data is automatically versioned and delivered to `data/deliveries/`.
- The metadata will be tagged with `"human_reviewed": true`.

---
*Clean data, human-guaranteed.*
