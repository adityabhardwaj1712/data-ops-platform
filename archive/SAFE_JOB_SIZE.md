# Safe Job Size Constraints (Sprint 5)

## Quantitative Limits
- **Websites**: ≤ 1 single domain per job.
- **Volume**: ≤ 300–500 pages total.
- **Pagination**: ≤ 1 pagination type (e.g., just "Next" button or just Infinite Scroll, not mixed).
- **HITL Rounds**: ≤ 2 rounds max. If it takes more, the job is too complex.

## Complexity Limits
- **No Login Walls**: Public data only.
- **No Complex JS Interaction**: If it needs 5 clicks to see the data, it's a skip.
- **No Captcha Heavy Sites**: Avoid sites with aggressive Akamai/Cloudflare protections that require commercial brute-force solutions we aren't using yet.

## PM Rule
> Boundaries protect quality. If a job exceeds these limits, reject it or negotiate it down.
