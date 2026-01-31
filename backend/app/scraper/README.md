# 🚀 Enterprise Scraper Engine v2.0

This module is a pro-grade, autonomous scraping platform designed for high-fidelity data extraction across any website. It features an intelligent escalation ladder, self-healing capabilities, and domain-specific learning.

## 🏗️ Folder Structure

- **`engines/`**: The "Muscle" of the system.
    - `static.py`: Fast HTTP-based fetching (httpx + trafilatura).
    - `browser.py`: Full browser rendering (Playwright).
    - `stealth.py`: Advanced anti-bot evasion (Playwright + Stealth plugins).
    - `base.py`: Interface definition for all execution strategies.
- **`intelligence/`**: The "Brain" of the system.
    - `analyzer.py`: Detects the best engine for a given URL based on signatures.
    - `memory.py`: Remembers successful strategies per domain (Silent Learning).
    - `preview.py`: Dry-run engine for validating selectors without full execution.
    - `confidence.py`: Calculates multidimensional quality scores.
    - `snapshots.py`: Manages data snapshots for change detection and drift monitoring.
- **`logic/`**: The "Heart" (Orchestration).
    - `generic.py`: Core escalation logic (`Static -> Browser -> Stealth`).
    - `product.py`: Specialized extractor for high-fidelity e-commerce data.
    - `registry.py`: Central registration and selection of scrapers.
    - `base.py`: Base class for all scraper implementations.
    - `controller.py`: High-level job lifecycle management.
- **`extractors/`**: The "Eyes" (Data Parsing).
    - `auto.py`: Pattern-based fallback extraction.
    - `config.py`: Manual CSS selector-based extraction.
    - `auto_detect.py`: AI-powered field discovery.
- **`utils/`**: The "Tools".
    - `artifacts.py`: Handles saving HTML, screenshots, and logs.
    - `validator.py`: Pydantic-based extraction validation.
    - `llm_client.py`: Interface for AI-powered tasks.
    - `pagination.py`: Handles multi-page traversal logic.
- **`recovery/`**: The "Immune System".
    - `selector_healer.py`: Heuristic-based recovery for broken CSS selectors.
- **`antibot/`**: The "Invisibility Cloak".
    - Specialized modules for handling CAPTCHAs, Fingerprinting, and Human-like delays.

## 🛠️ How it Works

1. **Pre-flight**: The `ScrapeAnalyzer` checks the URL against known bot-protection signatures.
2. **Memory Check**: `DomainMemoryManager` looks up if this domain has a "best known strategy" from past successes.
3. **Escalation**: The `GenericScraper` starts with the lowest cost engine (Static). If it detects a block, it automatically escalates to Browser, then Stealth.
4. **Extraction**: Data is pulled using the best available method (Fixed Selectors -> Self-Healing -> Auto-Detect).
5. **Validation**: The extracted data is validated against the user's schema.
6. **Learning**: The result (success/failure, latency) is recorded in `DomainMemory` to optimize the next request.

## 🚀 Key Features

- **AI Schema Builder**: Convert natural language prompts into scraping JSON.
- **Preview Mode**: See extraction results in real-time before launching a production job.
- **Self-Healing**: Automatically finds new selectors if the website layout changes.
- **Silent Learning**: Becomes faster and more efficient over time as it learns domain signatures.
