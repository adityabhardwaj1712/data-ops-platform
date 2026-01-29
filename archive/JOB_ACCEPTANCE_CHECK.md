# Job Acceptance Checklist

**PM Rule**: Good money comes from saying no.

## Phase 1: The "Instant No" Filter
- [ ] Is the deadline > 3 days away? (No "Rush" jobs)
- [ ] Is the site public? (No "Login required" / Hacking)
- [ ] Is the request purely for **DATA**? (No Dashboards, No SaaS, No Analysis)
- [ ] Is the volume < 5,000 pages?

*If ANY answer is "No" → REJECT IMMEDIATELY.*

## Phase 2: The Technical Audit (15 Mins)
- [ ] **Data Locality**: Can I see the data in the source HTML/JSON?
- [ ] **Anti-Bot**: Does `curl -v [url]` work without a 403? (Simple check)
- [ ] **Structure**: Is the pagination standard (Next button / URL param)?

*If "No" to these, it shifts to TIER 3. REJECT for now.*

## Phase 3: The "Vibe" Check
- [ ] Does the client accept "Best Effort" quality?
- [ ] Do they understand we sell raw inputs, not business insights?

## Decision
- **PASS**: Send Quote (Tier 1 or 2).
- **FAIL**: Send "No-Go" Template.
