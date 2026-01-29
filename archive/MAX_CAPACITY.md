# Max Capacity Rules (Sprint 7)

**PM Rule**: Capacity before demand.

## Weekly Throughput Limits
- **Max Active Jobs**: 3 (Concurrent)
- **Max New Starts / Week**: 2
- **Buffer Day**: Wednesday (No new starts, clean up only)

## Daily Operational Limits
- **Max HITL Time**: 2.0 Hours / Day
    - *Why?* Cognitive fatigue sets in after 2 hours of inspecting JSON/HTML.
    - *Action*: If HITL > 2h, stop and resume tomorrow.
- **Max Coding/Config Time**: 4 Hours / Day

## Complexity Constraints
- **Allowed Tiers**: Tier 1 (Static) and Tier 2 (Light JS).
- **Prohibited**: Tier 3 (Heavy Anti-Bot/Custom Auth).
    - *Why?* Tier 3 jobs destroy margins and sanity. We scale on "Easy", not "Hard".

## Fatigue Triggers (Stop scaling if:)
- [ ] You dread opening the laptop.
- [ ] You skip the "Job Acceptance Check".
- [ ] You delay invoicing.
