# Capacity Limits
*Hard boundaries to prevent system collapse under load (Sprint 13).*

**Principle**: "Unbounded concurrency causes silent failures."

## 1. Concurrency Limits
These limits are enforced by `limits.py` and the Queue Manager.

| Metric | Soft Limit (Warning) | Hard Limit (Block/Queue) | Why? |
|---|---|---|---|
| **Concurrent Jobs** | 8 | 10 | Docker container memory exhaustion. |
| **Concurrent Domains** | 3 | 5 | Prevent IP blacklisting ("Botnet" behavior). |
| **Browser Instances** | 4 | 5 | Chrome is RAM hungry (500MB+ per tab). |

## 2. Queue Discipline
- **Priority Override**: `PRIORITY_HIGH` jobs always jump ahead of `PRIORITY_NORMAL` in the queue.
- **Domain Throttling**: If 2 jobs for `example.com` are running, a 3rd must wait, even if slots are open.

## 3. Human Bottlenecks (HITL)
Humans cannot scale like containers. We protect them aggressively.

| Metric | Limit | Action if Exceeded |
|---|---|---|
| **Active HITL Tasks** | 2 per operator | New tasks queue as `PENDING_ASSIGNMENT`. |
| **Daily Review Cap** | 50 per operator | Alert Manager to hire/pause. |
| **Task Time** | 5 mins | Auto-release task back to queue. |

## 4. Resource Guardrails
Checked before *every* heavy operation (Browser launch, LLM call).

- **RAM**: If System RAM > 85% → Pause new workers.
- **CPU**: If Load > 80% → Throttle standard requests.
- **Disk**: If Free < 1GB → Stop all versions/logging to prevent corruption.

## 5. Back-Pressure Signals
How the system says "Stop".

- **Queue Depth > 100**: API returns `503 Service Unavailable` for new non-critical jobs.
- **HITL Queue > 10**: Pipeline degrades to `CONFIDENCE_STRICT` (rejects ambiguous items automatically).
