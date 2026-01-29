# 🛡️ OPERATIONAL LIMITS

**Purpose**: Protect system resources and prevent unbounded growth.

> **PM Rule**: Unbounded systems crash. Bounded systems degrade gracefully.

---

## 📊 RESOURCE HARD LIMITS

### Browser Instances
- **Maximum Browser Instances**: 3 (global hard cap)
- **Local Mode**: 1 browser instance
- **Production Mode**: 3 browser instances
- **Memory per Browser**: 512 MB

**Why**: Browser instances are the #1 memory consumer. Limiting them prevents WSL crashes and OOM errors.

### Worker Processes
- **Maximum Worker Memory**: 1024 MB per worker
- **Local Mode Workers**: 2
- **Production Mode Workers**: 5

**Why**: Workers can leak memory over time. Hard caps force cleanup and prevent runaway processes.

### Job Limits
- **Maximum Concurrent Jobs**: 10
- **Maximum URLs per Job**: 50
- **Maximum Pages per URL**: 20
- **Maximum Total Pages per Job**: 500 (production) / 20 (local)

**Why**: Jobs multiply resource usage. Capping them ensures predictable load.

---

## 🔧 MODE-BASED CONFIGURATION

### Local Mode (Default)
**Use when**: Running on WSL, laptop, or limited infrastructure

```
DEPLOYMENT_MODE=local
```

**Limits**:
- Workers: 2
- Browser Instances: 1
- Browser Parallelism: Disabled
- Max Pages per Job: 20
- Request Timeout: 20s

**Behavior**: Conservative, safe, prevents crashes

### Production Mode
**Use when**: Running on dedicated server, EC2, or cloud infrastructure

```
DEPLOYMENT_MODE=production
```

**Limits**:
- Workers: 5
- Browser Instances: 3
- Browser Parallelism: Enabled
- Max Pages per Job: 500
- Request Timeout: 30s

**Behavior**: Aggressive, optimized for throughput

---

## 🚦 SCRAPING LIMITS

### Rate Limiting
- **Requests per Domain per Minute**: 10
- **Maximum Scrape Retries**: 3
- **Request Timeout**: 30s (production) / 20s (local)
- **Browser Timeout**: 60s

**Why**: Prevents IP bans, respects target sites, avoids detection.

### Content Limits
- **Maximum HTML Size**: 10 MB
- **Maximum LLM Content Length**: 8000 characters
- **Maximum Items per Extraction**: 100

**Why**: Large content kills performance and costs money (LLM tokens).

---

## 💾 STORAGE LIMITS

### Artifacts
- **Maximum Artifact Storage per Job**: 100 MB
- **Maximum Screenshot Size**: 5 MB
- **Maximum Versions per Job**: 50

**Why**: Disk fills up fast. Limits prevent storage exhaustion.

---

## 🎯 QUALITY GATES

### Confidence Thresholds
- **Auto-Accept**: ≥ 90% confidence
- **Optional Review**: ≥ 50% confidence
- **Mandatory Review**: < 50% confidence

### HITL Timeout
- **Maximum HITL Task Duration**: 24 hours
- **Action on Timeout**: Auto-skip with notification

**Why**: Prevents jobs from hanging indefinitely waiting for human input.

---

## 🔄 API RATE LIMITS

### User Limits
- **API Requests per Minute**: 60
- **Pipeline Requests per Hour**: 100

**Why**: Prevents abuse, ensures fair usage, protects backend.

---

## 🛠️ HOW TO USE LIMITS

### In Code
```python
from app.core.limits import limits, get_mode_specific_limits, get_effective_browser_limit

# Get current mode limits
mode_limits = get_mode_specific_limits()
print(f"Max workers: {mode_limits['max_workers']}")

# Get effective browser limit
browser_limit = get_effective_browser_limit()
print(f"Browser instances allowed: {browser_limit}")

# Validate job request
from app.core.limits import validate_job_request
is_valid, error = validate_job_request(urls=["url1", "url2"], max_pages_per_url=10)
if not is_valid:
    raise ValueError(error)
```

### Environment Variables
Override any limit via environment variables with `LIMIT_` prefix:

```bash
LIMIT_DEPLOYMENT_MODE=production
LIMIT_MAX_BROWSER_INSTANCES=5
LIMIT_MAX_CONCURRENT_JOBS=20
```

---

## ⚠️ CRITICAL WARNINGS

### DO NOT
- ❌ Remove limits "just to see what happens"
- ❌ Set `MAX_BROWSER_INSTANCES` > 5 on WSL
- ❌ Run production mode on laptop/WSL
- ❌ Disable retries (causes silent failures)

### DO
- ✅ Start with local mode
- ✅ Monitor resource usage before increasing limits
- ✅ Test limit changes on small jobs first
- ✅ Document why you changed a limit

---

## 📈 MONITORING LIMITS

### Check Current Usage
```bash
# Health check (includes resource usage)
curl http://localhost:8000/health

# Worker status
# (See OPERATOR_RUNBOOK.md for commands)
```

### Signs You Need to Adjust Limits
- **Increase limits if**: Jobs consistently fail due to limits, not errors
- **Decrease limits if**: System becomes unstable, memory spikes, crashes

---

## 🧠 PHILOSOPHY

> "A system with no limits is a system waiting to fail."

Limits are not restrictions—they are **safety rails**.

They ensure:
1. **Predictability**: You know the worst-case resource usage
2. **Stability**: System degrades gracefully under load
3. **Recovery**: Failures are contained, not cascading
4. **Trust**: You can sleep while jobs run

---

## 📝 LIMIT CHANGE LOG

| Date | Limit Changed | Old Value | New Value | Reason |
|------|---------------|-----------|-----------|--------|
| 2026-01-29 | Initial limits | N/A | See above | Sprint 15 production hardening |

**Rule**: Every limit change must be logged here with justification.

---

## 🎯 SPRINT 15 COMPLETION CRITERIA

- [x] All limits documented
- [x] Mode-based configuration implemented
- [x] Helper functions created
- [ ] Limits enforced in worker code
- [ ] Limits tested under stress
- [ ] WSL safe mode verified

**Next**: Implement graceful failure handling and startup/shutdown safety.
