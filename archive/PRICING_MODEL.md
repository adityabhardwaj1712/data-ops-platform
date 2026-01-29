# Internal Pricing Model (v1.0)

This model is used to calculate the internal cost and the suggested client price for data delivery jobs.

## 1. Internal Cost Components
- **Base Overhead**: $0.50 (Compute, storage, and platform maintenance).
- **Automated Extraction**: $0.05 per page/task.
- **Human Verification (HITL)**: $2.00 per task (Covers manual audit and correction time).

## 2. Pricing Tiers (Client-Facing)

| Tier | Characteristics | Suggested Price |
| :--- | :--- | :--- |
| **Standard** | Static sites, high confidence, no HITL needed. | $0.20 per row |
| **Professional** | JS-heavy (Browser), moderate complexity, sample validation. | $0.50 per row |
| **Elite (Full Audit)** | Anti-bot / Stealth required, 100% HITL verification. | $1.50 per row |

## 3. Calculation Example
**Job**: 100 LinkedIn Profiles (Stealth + HITL)
- **Internal Cost**: $0.50 (Base) + (100 * $0.10 [Stealth]) + (100 * $2.00 [HITL]) = **$210.50**
- **Client Price**: 100 * $2.50 (Custom Tier) = **$250.00**
- **Profit**: $39.50 (15.8% margin)

---
> [!WARNING]
> These are **Internal Guidelines**. Final pricing should always be quoted based on site difficulty and data rarity.
