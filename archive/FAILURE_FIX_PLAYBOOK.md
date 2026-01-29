# Failure Error Code & Fix Playbook

This document links system error codes to actionable fixes for operators.

## 1. FETCH_FAILED (Network/Access)
**Symptoms**: Job fails immediately, no HTML retrieved.
**Common Causes & Fixes**:
- **403 Forbidden / 429 Too Many Requests**: 
  - *Fix*: Enable "Stealth Mode" or "Use Proxy" in Config.
  - *Ref*: Check `config_ecommerce_stealth` template.
- **Timeout**:
  - *Fix*: Increase `timeout` in Config (default 30s -> 60s).
- **DNS/Connection Error**:
  - *Fix*: Verify URL is correct and site is up manually.

## 2. SELECTOR_MISSING (Extraction)
**Symptoms**: Fetch succeeds, but "Data extraction failed" or empty fields.
**Common Causes & Fixes**:
- **Layout Change**: Site updated its CSS classes.
  - *Fix*: Use HITL to select new elements.
  - *Action*: Run `verify_selectors` local script if available.
- **Dynamic Content**: Data loads after JS execution.
  - *Fix*: Change `strategy` to `BROWSER` (Playwright) or add `wait_for_selector`.
- **Wrong Page**: Redirected to login/captcha.
  - *Fix*: Check screenshots. If Captcha, enable anti-bot.

## 3. EMPTY_DATA (Logic)
**Symptoms**: Scraper runs but returns 0 rows.
**Common Causes & Fixes**:
- **Pagination Dead End**: Pagination selector exists but is not clickable or hidden.
  - *Unit*: Check `pagination` config.
- **Filters too Aggressive**:
  - *Fix*: Remove filters in Config.

## 4. VALIDATION_FAILED (Quality)
**Symptoms**: Data extracted but rejected by Trust Engine.
**Common Causes & Fixes**:
- **Missing Required Fields**:
  - *Fix*: Mark field as `optional` in Schema if strictly not always present.
- **Data Type Mismatch**:
  - *Fix*: Update Schema (e.g., Expect `string` instead of `float` for prices with currency symbols).

## 5. REPEATED_FAILURES (System)
**Symptoms**: Same job fails 2+ times in a row.
**Action**:
- **FORCE HITL**: Do not retry automatically.
- **Clone Job**: Create a fresh job with `BROWSER` strategy to debug visually.
