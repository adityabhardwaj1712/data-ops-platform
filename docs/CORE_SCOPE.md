# Project Core Scope: Reliable Scraper System

> [!IMPORTANT]
> This project is currently in a **FEATURE FREEZE**. All development must focus on stability, reliability, and hardening of existing core features.

## Current Project Goal
To build a reliable, human-verified web scraping system that produces clean, trustworthy data.

## Core Scope Boundaries
The following features are the **ONLY** core components of the system:
1.  **Reliable Scraping**: Modular engine supporting Static, Browser, and Stealth fetches with automatic strategy detection.
2.  **Strict Validation**: Post-scrape checks for data integrity (no emptiness, no duplicates).
3.  **Human-In-The-Loop (HITL)**: Simplified UI for inspecting failures, editing selectors, and re-running jobs.
4.  **Clean Output**: Versioned, schema-compliant data delivery with confidence scoring.

## Future Phases (OUT OF SCOPE)
The following ideas are deferred to future development cycles to prevent scope creep:
- `FUTURE_PHASE`: Advanced Analytics & Visualization (Charts, Aggregates)
- `FUTURE_PHASE`: Global Search across datasets
- `FUTURE_PHASE`: Automated Backup & Migration tools
- `FUTURE_PHASE`: Multi-tenant / SaaS-ready features (Billing, Teams)
- `FUTURE_PHASE`: AI-driven "Insights" and summarization

---
*Depth over breadth. Trust over features.*
