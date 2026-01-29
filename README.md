# DataOps Scraper: Reliable, Human-Verified Data Extraction

A pro-level web scraping system designed for trust, reliability, and human oversight. This project implements a modular, config-driven architecture that ensures data integrity through strict validation and an integrated Human-In-The-Loop (HITL) flow.

## 🏗️ Core Architecture

The system is built on a modular "Fetch-Validate-Score" pipeline, replacing monolithic scraping engines with specialized components.

### 📁 File Structure

```text
backend_fastapi/
├── app/
│   ├── scraper/                # Core Scraping Logic
│   │   ├── analyzer.py         # Strategy detection (Static vs Browser vs Stealth)
│   │   ├── base.py             # Base scraper strategies with retry logic
│   │   ├── generic.py          # Central Orchestrator (The "Brain")
│   │   ├── validator.py        # Strict post-scrape integrity checks
│   │   ├── confidence.py       # 0-100 Scoring logic
│   │   ├── artifacts.py        # Local storage for HTML/Screenshots
│   │   └── extractors/         # Data extraction strategies
│   │       ├── config.py       # Strict CSS selector-based extraction
│   │       └── auto.py         # Heuristic & Regex based extraction
│   ├── worker/                 # Background job processing
│   │   └── executors/
│   │       └── scrape_executor.py  # Orchestrates GenericScraper in workers
│   └── api/                    # Lean REST API endpoints
│       ├── scrape.py           # Job submission & status
│       └── hitl.py             # Human-In-The-Loop management
└── data/
    ├── artifacts/              # HTML dumps and screenshots (Job IDs)
    └── deliveries/             # Final validated data versions
```

## 🚀 Key Features

### 1. Modular Fetching Pipeline
The system automatically chooses the lightest fetch strategy possible:
- **Static**: Fast HTTP requests for simple sites.
- **Browser**: Full JS rendering using Playwright.
- **Stealth**: Advanced anti-bot evasion for protected sites.

### 2. Strict Data Validation
Every scrape results in a validation report checking for:
- Empty fields or missing required data.
- Duplicate rows.
- Schema compliance.

### 3. Confidence Scoring & HITL
If a scrape has a confidence score < 85 or fails validation, it is automatically routed to the **Human review queue**.
- Inspect screenshots of what the scraper saw.
- Edit CSS selectors in real-time.
- Re-run the job with high priority.

## 🛠️ Quick Start

### Start the System
```bash
docker compose up -d api worker
```

### Start a Scrape (Config-Driven)
```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/products",
    "schema": {
      "container": ".product-card",
      "fields": {
        "title": "h2.title",
        "price": ".price-tag"
      }
    }
  }'
```

### Review Jobs (Frontend)
Visit `http://localhost:3000/review/[job_id]` to use the Human-In-The-Loop interface for failed or low-confidence scrapes.

## 🔒 Security & Reliability
- **Retry Mechanism**: Exponential backoff on fetch failures.
- **Robots.txt**: Full compliance with target domain rules.
- **Artifact Auditing**: Full transparency into what was scraped and why it was scored.

---
© 2026 DataOps Reliable Scraper System
