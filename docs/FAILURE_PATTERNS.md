# Scraping Failure Patterns & HITL Fixes

This document catalogs common scraping failures, how to identify them, and how to fix them using the Human-In-The-Loop (HITL) interface.

## 1. Selector Drift (Most Common)
- **What it looks like**: `SELECTOR_MISSING` error or empty data for specific fields.
- **How to identify**: Check the validation report in the Scrape Result. If a field like `price` is consistently null, the CSS selector has likely changed.
- **HITL Fix**: 
    1. Open the job in HITL.
    2. Inspect the raw HTML/Screenshot provided.
    3. Update the CSS selector in the config (e.g., change `.price` to `.product-price-value`).
    4. Trigger a **Rerun**.

## 2. Dynamic Content / JS Latency
- **What it looks like**: `EMPTY_DATA` but the screenshot shows the page is still loading.
- **How to identify**: View the screenshot artifact. If you see loading spinners or incomplete text, the `timeout` was too short or the `wait_for_selector` was wrong.
- **HITL Fix**:
    1. Update `wait_for_selector` to a specific content element (e.g., `h1.product-title`).
    2. Increase `timeout` to `45` or `60` seconds.
    3. Switch strategy to `browser` if currently `static`.

## 3. Anti-Bot / CAPTCHA
- **What it looks like**: `ANTI_BOT_SUSPECTED` or `FETCH_FAILED`.
- **How to identify**: Screenshot shows a "Cloudflare" challenge, "Pardon Our Interruption" page, or a 403 Forbidden error.
- **HITL Fix**:
    1. Switch strategy to `stealth`.
    2. Enable `use_proxy`.
    3. If it persists, the IP range might be flagged; rotate proxy settings in global config.

## 4. Schema Mismatch
- **What it looks like**: `VALIDATION_FAILED`.
- **How to identify**: Data is extracted but doesn't match the format (e.g., expected a list of objects but got a single string).
- **HITL Fix**:
    1. Manually correct the data in the HITL JSON editor.
    2. Adjust the `schema` or `prompt` if using LLM-extraction to be more specific.

---
> [!TIP]
> **Proactive Fix**: If a selector is fragile (e.g., `div > div > span`), use the HITL stage to change it to a more stable class or ID before the job completes.
