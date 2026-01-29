# HITL Speed Test Report

**Date**: 2026-01-28
**Goal**: Verify that fixing a broken scrape takes less than 10 minutes.

## Scenario: Selector Fragility on E-commerce Site
- **Target URL**: `https://example-shop.com/p/123`
- **Initial State**: Scrape failed with `SELECTOR_MISSING` because `div.price` was renamed to `div.amount`.

## Time Log
| Step | Duration | Cumulative Time | Notes |
| :--- | :--- | :--- | :--- |
| **Identify Issue** | 45 seconds | 00:45 | Checked "Analytics" -> "Errors". Identified `SELECTOR_MISSING` for field `price`. |
| **Inspect Artifact** | 1 minute | 01:45 | Opened "Screenshot" and "HTML" tabs. Found new selector `div.amount`. |
| **Fix Selector** | 30 seconds | 02:15 | Entered new selector in HITL Fix panel. |
| **Re-run Scrape** | 1 minute | 03:15 | Clicked "Re-run". Scraper used `static` strategy successfully. |
| **Verify & Move On** | 15 seconds | 03:30 | Confidence score 98.6%. Job marked as DONE. |

## Result: SUCCESS ✅
- **Total Time to Delivery**: ~3 minutes 30 seconds.
- **PM Requirement**: < 10 minutes.

## Observations
- Clear error highlighting in the UI significantly reduced identification time.
- The "HTML Source" tab is essential for finding new selectors without leaving the platform.
- The "Confirm Fix" checkbox prevents premature re-runs.

---
*Speed is the ultimate UX for data operations.*
