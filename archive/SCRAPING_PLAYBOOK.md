# Scraping Playbook — Reliability Best Practices

This document outlines the standard operating procedures for maintaining a high-reliability scraping system.

## 1. Failure Classification
Every scrape failure must be classified into one of the following:
- **SELECTOR_NOT_FOUND**: The page layout changed. Fix CSS selectors.
- **TIMEOUT**: Network or site slowness. Retry once.
- **BOT_DETECTED**: Blocked by WAF/Captcha. Switch to `Stealth` strategy.
- **VALIDATION_FAILED**: Data was found but didn't meet schema (e.g., empty fields).

## 2. Confidence Scoring
Confidence index (0-100) is calculated based on:
- **Model Confidence**: LLM's certainty in extraction.
- **Row Count**: Did we find at least one record?
- **Field Completeness**: Are required fields populated?
- **Schema Match**: Does the data type match the definition?

> [!IMPORTANT]
> Any score < 85 triggers a **NEEDS_HITL** (Human-In-The-Loop) status.

## 3. Human-In-The-Loop (HITL) Workflow
When a job enters `NEEDS_HITL`:
1. **Analyze Artifacts**: View the HTML/Screenshot to see what the scraper "saw".
2. **Preflight Test**: Update selectors in the UI and click "Preflight" to test on 1 page.
3. **Full Re-run**: Once preflight is successful, commit to a full re-run.

## 4. Bot Evasion Strategies
- **Browser Strategy**: Use for SPA/Javascript heavy sites.
- **Stealth Strategy**: Use for sites with Cloudflare/Perimeter81. Includes rotating headers and mouse movement.

## 5. Metrics to Track
- **Success Rate**: Aim for > 95% automated success.
- **HITL Frequency**: Aim for < 10% manual intervention.
- **Mean Time to Repair (MTTR)**: Aim for < 5 minutes per human fix.
