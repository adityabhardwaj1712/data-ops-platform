# Optimization Guide

Goal: Reduce HITL Frequency and Increase Automated Trust.

## 1. Selector Specificity
Avoid overly generic selectors like `div.item`. Use unique data attributes or structural paths:
- ❌ `.product-title`
- ✅ `.product-grid > div[data-id] h3.title`

## 2. Dynamic Content Handling
If the success rate is low for a specific domain, refine the `strategy`:
- **Static First**: Try `static` with custom headers.
- **Wait for Elements**: If using `browser`, ensure the schema defines a `container` that only appears after JS renders.

## 3. Confidence Refinement
Adjust the `ConfidenceScorer` weights if validation is too strict or too loose for certain dataset types.

## 4. Anti-Bot Rotation
For high-volume jobs, consistently use the `stealth` strategy and consider rotating User-Agents if 403 errors increase.

---
*Predictable results require precise configs.*
