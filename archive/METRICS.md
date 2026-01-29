# System "Silence" Metrics
*Scalability by Depth*

The goal of this system is to become "boring" and "quiet." A silent system is a scalable system.

## Core Silence Metrics

### 1. Days Since Last Panic
**Definition**: Number of days without a "P0" incident (operator forced to intervene outside of standard HITL).
- **Goal**: Infinity.
- **Why**: Reliability allows the operator to focus on sales/strategy, not firefighting.

### 2. "Just Worked" Ratio
**Definition**: Percentage of jobs that go from `CREATED` -> `COMPLETED` (or `DELIVERED`) without ever entering `NEEDS_HITL`.
- **Goal**: > 95% for mature domains.
- **Formula**: `(Total Jobs - HITL Jobs) / Total Jobs`

### 3. HITL Friction (Time/Page)
**Definition**: Average time an operator spends resolving a HITL task.
- **Goal**: < 30 seconds per task.
- **Why**: Low friction means we can handle 10x volume with the same human team.

### 4. Code Touches per Month
**Definition**: Number of commits/edits to `app/core` or `app/scraper` (excluding new features).
- **Goal**: Trending to 0.
- **Why**: Core stability means we aren't patching bugs constantly.

## Automation Impact (Sprint 12)

### 5. HITL Time Saved
**Definition**: `(Manual Time Est. - Actual HITL Time) / Manual Time Est.`
- **Goal**: > 50%
- **Why**: Validates that automation is truly helping.

### 6. Rework Rate
**Definition**: % of Delivered Packages rejected or fixed after delivery.
- **Goal**: < 1%
- **Why**: Automation must be correct, not just fast.

## Operational Health

| Metric | Healthy | Warning | Critical |
|/---|---|---|---|
| **Success Rate (Fetch)** | > 98% | < 95% | < 80% |
| **Trust Engine Confidence** | > 90% | < 80% | < 60% |
| **P95 Latency** | < 30s | > 60s | > 120s |
