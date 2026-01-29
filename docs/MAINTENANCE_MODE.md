# 🔧 MAINTENANCE MODE

**Purpose**: Define long-term maintenance strategy to keep the system healthy without constant attention.

> **PM Rule**: Good projects survive because owners know when to stop.

---

## What Runs Automatically

### System-Level Automation
✅ **Database cleanup**: SQLite auto-vacuums on connection close  
✅ **Log rotation**: Logs rotate daily (if configured)  
✅ **Artifact retention**: Old artifacts remain (manual cleanup only)  
✅ **Health checks**: Available on-demand via `/health` endpoint  

### Job-Level Automation
✅ **Retry logic**: Failed jobs retry up to 3 times automatically  
✅ **HITL timeout**: Tasks auto-skip after 24 hours  
✅ **Queue processing**: Workers poll and process jobs continuously  
✅ **Confidence scoring**: Every extraction scored automatically  

### What Does NOT Run Automatically
❌ **Artifact cleanup**: Must be done manually  
❌ **Database backups**: Must be scheduled externally  
❌ **Dependency updates**: Manual review required  
❌ **Performance tuning**: Limits must be adjusted manually  

---

## What Needs Manual Checks

### Weekly Checks (5 minutes)
Run these commands once per week:

```bash
# 1. Health check
python scripts/ops_check.py health

# 2. Disk usage
python scripts/ops_check.py disk

# 3. Queue depth
python scripts/ops_check.py queue
```

**What to look for**:
- Memory usage > 85% → Consider reducing concurrent jobs
- Disk usage > 80% → Clean up old artifacts
- Queue depth growing → Workers may be stuck

### Monthly Checks (15 minutes)

```bash
# 1. Review failure patterns
cat logs/app.log | grep "ERROR" | tail -50

# 2. Check artifact storage
du -sh data/artifacts/*

# 3. Database size
ls -lh data/dataops.db
```

**What to look for**:
- Repeated errors → Update FAILURE_PATTERNS.md
- Large artifact directories → Archive or delete old jobs
- Database > 1GB → Consider archiving old jobs

### Quarterly Checks (30 minutes)

1. **Review operational limits** (`docs/OPERATIONAL_LIMITS.md`)
   - Are current limits still appropriate?
   - Any limit changes needed based on usage?

2. **Update failure patterns** (`docs/FAILURE_PATTERNS.md`)
   - New failure modes discovered?
   - Existing fixes still working?

3. **Review HITL tasks**
   - Are confidence thresholds appropriate?
   - Too many/too few HITL tasks?

4. **Dependency audit**
   ```bash
   pip list --outdated
   ```
   - Security updates only (no feature updates)

---

## What You Can Safely Ignore

### System Warnings (Safe to Ignore)
✅ **"Worker X polling for jobs"** - Normal operation  
✅ **"No jobs available"** - Queue is empty (good)  
✅ **"Lazy-loading scraper engine"** - First-time load (expected)  
✅ **"HITL task created"** - Low confidence result (by design)  

### Transient Errors (Safe to Ignore)
✅ **Single scrape failures** - Retry logic handles it  
✅ **Browser timeout (< 3 retries)** - Will retry  
✅ **Network errors (temporary)** - Will retry  

### What You CANNOT Ignore
❌ **"Database connection failed"** - Critical, fix immediately  
❌ **"Worker crashed"** - Investigate logs  
❌ **"Orphan process detected"** - Clean up manually  
❌ **"Disk full"** - Free up space immediately  
❌ **"Memory exhausted"** - Reduce limits or upgrade hardware  

---

## Maintenance Tasks

### Daily (Automated)
- ✅ Workers process jobs
- ✅ Health checks available
- ✅ Logs written

### Weekly (5 min)
- 🔧 Run health check
- 🔧 Check disk usage
- 🔧 Review queue depth

### Monthly (15 min)
- 🔧 Review error logs
- 🔧 Check artifact storage
- 🔧 Database size check

### Quarterly (30 min)
- 🔧 Review operational limits
- 🔧 Update failure patterns
- 🔧 HITL threshold review
- 🔧 Dependency audit

### Annually (1 hour)
- 🔧 Full system audit
- 🔧 Documentation review
- 🔧 Archive old jobs
- 🔧 Performance baseline

---

## Refactoring Triggers

### When to Refactor
Only refactor if you hit these triggers:

1. **Same bug fixed 3+ times** → Root cause needs addressing
2. **Limit hit repeatedly** → Architecture may need rethinking
3. **New job type fails consistently** → Scraper needs enhancement
4. **HITL rate > 50%** → Confidence scoring needs tuning

### When NOT to Refactor
❌ **"I could make this cleaner"** - No  
❌ **"New framework released"** - No  
❌ **"This code is old"** - Age ≠ bad  
❌ **"I'm bored"** - Definitely no  

**Rule**: If it works and isn't causing problems, leave it alone.

---

## Feature Freeze Criteria

### When to Say "No More Features"

You should freeze features when:
1. ✅ System meets core requirements
2. ✅ No critical bugs
3. ✅ Documentation complete
4. ✅ Operational confidence high
5. ✅ No urge to add features

**Current Status**: ✅ Feature freeze in effect (v1.0)

### Exceptions to Feature Freeze
Only add features if:
1. **Paid client requests it** (and pays for it)
2. **Regulatory requirement** (compliance, legal)
3. **Critical security fix** (not a feature, a fix)

**Rule**: Features must be justified by revenue or risk, not curiosity.

---

## Long-Term Maintenance Strategy

### Year 1 (Current)
- **Focus**: Stability, reliability, operational confidence
- **Changes**: Bug fixes only, no features
- **Effort**: ~2 hours/month

### Year 2+
- **Focus**: Minimal maintenance, archive mode
- **Changes**: Security updates only
- **Effort**: ~1 hour/quarter

### End-of-Life Triggers
Consider archiving the project if:
- No jobs run for 6+ months
- Better alternative found
- No longer needed for work
- Maintenance burden too high

**Rule**: It's okay to sunset projects. Archive, don't delete.

---

## Backup Strategy

### What to Backup
1. **Database**: `data/dataops.db`
2. **Artifacts**: `data/artifacts/` (selective)
3. **Configuration**: `.env`, `docker-compose.yml`
4. **Documentation**: `docs/` directory

### Backup Frequency
- **Database**: Weekly (automated via cron)
- **Artifacts**: Monthly (manual, selective)
- **Configuration**: On change (git commit)
- **Documentation**: On change (git commit)

### Backup Command
```bash
# Simple backup script
tar -czf backup_$(date +%Y%m%d).tar.gz \
    data/dataops.db \
    data/artifacts/ \
    .env \
    docker-compose.yml \
    docs/
```

---

## Monitoring Checklist

### Green (Healthy)
✅ Memory < 80%  
✅ Disk < 75%  
✅ Queue depth < max concurrent jobs  
✅ No repeated errors in logs  
✅ Workers responding  

### Yellow (Warning)
⚠️ Memory 80-90%  
⚠️ Disk 75-85%  
⚠️ Queue depth growing slowly  
⚠️ Occasional errors (< 5% failure rate)  

### Red (Critical)
🚨 Memory > 90%  
🚨 Disk > 85%  
🚨 Queue depth > 2x max concurrent jobs  
🚨 Repeated errors (> 10% failure rate)  
🚨 Workers not responding  

---

## Emergency Procedures

### System Unresponsive
```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Check workers
python scripts/ops_check.py workers

# 3. Restart (last resort)
docker-compose restart
```

### Disk Full
```bash
# 1. Check usage
python scripts/ops_check.py disk

# 2. Clean old artifacts
rm -rf data/artifacts/<old-job-ids>

# 3. Vacuum database
sqlite3 data/dataops.db "VACUUM;"
```

### Memory Exhaustion
```bash
# 1. Check current usage
python scripts/ops_check.py health

# 2. Reduce limits
export LIMIT_MAX_CONCURRENT_JOBS=5
export LIMIT_MAX_BROWSER_INSTANCES=1

# 3. Restart
docker-compose restart
```

---

## Maintenance Philosophy

> **"The best maintenance is the maintenance you don't have to do."**

This system is designed to require minimal attention:
- **Bounded resources** prevent runaway growth
- **Graceful degradation** prevents catastrophic failures
- **Comprehensive logging** makes debugging easy
- **Clear documentation** reduces guesswork

**Goal**: Spend < 2 hours/month on maintenance.

If you're spending more, something is wrong. Review architecture or limits.

---

## Maintenance Log

| Date | Task | Duration | Notes |
|------|------|----------|-------|
| 2026-01-29 | Initial setup | - | System deployed |
| | | | |

**Rule**: Log all maintenance activities here for future reference.

---

**Last Updated**: 2026-01-29  
**Maintenance Mode**: Active  
**Next Review**: 2026-02-05 (weekly check)
