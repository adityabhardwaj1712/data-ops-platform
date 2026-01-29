# 📊 EVIDENCE

**Purpose**: Proof of work—screenshots, logs, metrics, and examples that demonstrate system capabilities.

> **PM Rule**: Serious engineers show evidence, not demos.

---

## Directory Structure

```
EVIDENCE/
├── README.md (this file)
├── screenshots/
│   ├── hitl_review_interface.png
│   ├── job_lifecycle.png
│   ├── health_check_output.png
│   └── confidence_scoring.png
├── logs/
│   ├── successful_run_example.log
│   ├── failure_recovery_example.log
│   └── browser_crash_retry.log
├── metrics/
│   ├── automation_before_after.md
│   ├── confidence_distribution.csv
│   └── resource_usage.md
└── examples/
    ├── failure_fix_example_1.md
    ├── failure_fix_example_2.md
    └── hitl_validation_example.md
```

---

## What to Collect

### Screenshots
Capture these key interfaces:
- [ ] HITL review interface (showing screenshot + data side-by-side)
- [ ] Job lifecycle progression (created → running → completed)
- [ ] Health check output (all green)
- [ ] Confidence scoring in action
- [ ] Worker status dashboard
- [ ] Queue depth monitoring

### Logs
Save examples of:
- [ ] Successful multi-page scrape
- [ ] Graceful failure recovery
- [ ] Browser crash with retry
- [ ] HITL task creation and completion
- [ ] Resource limit enforcement

### Metrics
Document:
- [ ] Before/after automation (manual vs automated time)
- [ ] Confidence score distribution (histogram)
- [ ] Resource usage over time (memory, CPU, disk)
- [ ] HITL rate (% of jobs requiring human review)
- [ ] Failure rate by category

### Examples
Write up:
- [ ] Failure pattern → fix example (network timeout)
- [ ] Failure pattern → fix example (parsing error)
- [ ] HITL validation example (low confidence → human review → delivery)

---

## How to Use This Evidence

### For Interviews
**Question**: "Tell me about a complex system you built."

**Answer**: Show `SYSTEM_STORY.md` + evidence from this directory.

**Specific Examples**:
- "Here's a screenshot of the HITL interface I built..."
- "This log shows how the system recovered from a browser crash..."
- "These metrics show 80% reduction in manual work..."

### For Clients
**Question**: "How do I know your system is reliable?"

**Answer**: Show evidence of:
- Successful runs (logs)
- Failure recovery (logs)
- Quality validation (HITL examples)
- Resource safety (health checks)

### For Your Future Self
**Question**: "Did this system actually work?"

**Answer**: Yes. Here's the proof.

---

## Evidence Collection Checklist

### Phase 1: Basic Functionality
- [ ] Run a simple scrape job (1 URL, 1 page)
- [ ] Capture screenshot of job completion
- [ ] Save log output
- [ ] Export data (CSV, JSON)

### Phase 2: HITL Workflow
- [ ] Create job with low-confidence result
- [ ] Capture screenshot of HITL task
- [ ] Perform human review
- [ ] Capture screenshot of version comparison
- [ ] Save audit trail

### Phase 3: Failure Recovery
- [ ] Simulate browser crash (kill process mid-scrape)
- [ ] Capture log of retry logic
- [ ] Verify partial artifacts preserved
- [ ] Document recovery process

### Phase 4: Resource Limits
- [ ] Run health check (all green)
- [ ] Run worker status (show limits enforced)
- [ ] Run queue depth (show bounded)
- [ ] Run disk usage (show artifact tracking)

### Phase 5: Metrics Collection
- [ ] Run 10 jobs, track confidence scores
- [ ] Calculate HITL rate
- [ ] Measure resource usage
- [ ] Document automation time savings

---

## Template: Failure → Fix Example

```markdown
## Failure Pattern: [Name]

### What Happened
[Description of the failure]

### Why It Happened
[Root cause analysis]

### How It Was Fixed
[Solution implemented]

### Evidence
- **Log**: [Link to log file]
- **Code**: [Link to fix commit]
- **Test**: [How to verify fix]

### Lesson Learned
[Key takeaway]
```

---

## Template: HITL Validation Example

```markdown
## HITL Validation: [Job Name]

### Initial Extraction
- **Confidence**: [Score]%
- **Issues**: [What was wrong]
- **Screenshot**: [Link to screenshot]

### Human Review
- **Reviewer**: [Name/ID]
- **Changes Made**: [List of edits]
- **Time Spent**: [Minutes]

### Final Result
- **Confidence**: 100% (human-validated)
- **Delivered**: [Format]
- **Screenshot**: [Link to final data]

### Value Add
[Why human review was necessary and valuable]
```

---

## Metrics to Track

### Automation Efficiency
| Metric | Before Automation | After Automation | Improvement |
|--------|-------------------|------------------|-------------|
| Time per job | [X hours] | [Y minutes] | [Z%] |
| Error rate | [X%] | [Y%] | [Z%] |
| Manual steps | [X] | [Y] | [Z%] |

### Quality Metrics
| Metric | Value |
|--------|-------|
| Average confidence | [X%] |
| HITL rate | [Y%] |
| Auto-accept rate | [Z%] |
| Failure rate | [W%] |

### Resource Metrics
| Resource | Average | Peak | Limit |
|----------|---------|------|-------|
| Memory | [X MB] | [Y MB] | [Z MB] |
| CPU | [X%] | [Y%] | 100% |
| Disk | [X GB] | [Y GB] | [Z GB] |

---

## Evidence Maintenance

### When to Update
- After each major job run
- After fixing a new failure pattern
- Monthly metrics collection
- Before interviews or client meetings

### What to Archive
- Old screenshots (keep latest only)
- Redundant logs (keep examples only)
- Outdated metrics (keep trends)

### What to Keep Forever
- First successful run
- First HITL validation
- First failure recovery
- Key metrics milestones

---

## Current Status

**Evidence Collected**: 0/20 items

**Next Steps**:
1. Run test jobs to generate evidence
2. Capture screenshots of key interfaces
3. Save example logs
4. Document metrics

**Target**: Complete evidence collection before first client engagement.

---

**Last Updated**: 2026-01-29  
**Status**: Directory created, collection pending
