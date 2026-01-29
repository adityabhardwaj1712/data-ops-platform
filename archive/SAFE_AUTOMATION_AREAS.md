# Safe Automation Areas
*Criteria for enabling automated decisions in Sprint 12*

**Principle**: "We do not automate uncertainty. We automate repetition."

## 1. Safe to Automate (Green Light)
These actions are deterministic, low-risk, and have been manually performed 10+ times successfully.

| Area | Manual Trigger | Automated Rule | Failsafe |
|---|---|---|---|
| **Strategy Selection** | "This is an ecommerce site, use `BROWSER`." | `if site_type == 'ecommerce' and fails_http: use BROWSER` | Timeout > 60s → HITL |
| **Pagination** | "It has `?page=1` in URL." | `if url_has_param('page'): use URL_PARAM strategy` | Page 2 == Page 1 → Stop |
| **Config Reuse** | "This site worked perfectly last week." | `if config.success_count >= 3 and config.is_stable: reuse` | Data < 10% expected → New Scrape |
| **Retry Logic** | "Just a network blip, try again." | `if error == 'NETWORK_TIMEOUT': retry(1)` | Max retries = 3 → Fail |

## 2. Testing Required (Yellow Light)
These require `AUTOMATION_MODE=SAFE` and active monitoring.

- **Auto-Normalization**: Convert "$10.99" -> `10.99`. (Safe if regex is strict).
- **Auto-Deduplication**: Remove exact duplicates. (Safe if primary keys are reliable).

## 3. Do NOT Automate (Red Light)
These require human intuition or are too risky.

- **Selector Guessing**: "Maybe the title is `h2.class-xyz`?" (AI hallucinations common).
- **Captcha Solving**: Too expensive/risky to do blindly.
- **Login Flows**: Security risk if automated poorly.
- **Data Quality Judgment**: "Does this look like a valid JD?" (Context required).

## Success Metrics for Automation
- **HITL Time Saved**: Should reduce simple tasks (e.g., config selection) by 80%.
- **False Positives**: < 1% of automated decisions should be wrong.
