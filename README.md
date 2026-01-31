# 🌐 DataOps Platform: Pro-Grade Scraper

An intelligent, autonomous data extraction platform designed for resilience, stealth, and high-fidelity output. This system evolves from a simple multi-layered scraper into a self-healing data delivery engine.

## 🚀 Phase 2 Features

- **🤖 AI Schema Builder**: Generate complex scraping schemas from natural language prompts.
- **🧠 Silent Learning**: Domain-specific memory that automatically optimizes engine selection (Static vs Browser vs Stealth).
- **🛠️ Self-Healing Selectors**: Intelligent recovery when website layouts change.
- **🔍 Preview Mode**: Dry-run extraction with real-time success metrics.
- **📈 Change Detection**: Snapshot-based monitoring for data drift.

## 🏗️ Core Architecture

The system is organized into a highly modular structure for maximum maintainability:

### 📦 Backend (FastAPI)
- **`app/scraper/`**: The core extraction engine.
    - `engines/`: Base fetchers (httpx, Playwright).
    - `intelligence/`: Domain memory, analyzer, and preview logic.
    - `logic/`: Orchestration and specialized scrapers (Generic, Product).
    - `recovery/`: Self-healing heuristic engine.
    - `utils/`: Common utilities (Artifacts, Validator, Pagination).
- **`app/api/`**: RESTful interface for the platform.
- **`app/worker/`**: Background job processing with Celery-like resilience.

### 🎨 Frontend (Next.js)
- **Glassmorphic UI**: A premium, high-performance dashboard.
- **Live Metrics**: Real-time feedback on engine performance and confidence.
- **AI Tools**: Interactive schema builder and preview panels.

## 🛠️ Getting Started

### Local Setup
1. **Infrastructure**: Start Docker dependencies (PostgreSQL/SQLite).
2. **Backend**: 
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. **Frontend**: 
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Verification
Run the verification script to ensure the registry and specialized scrapers are correctly mapped:
```bash
python verify_scrapers.py
```

## 📜 License
Proprietary Engine v2.5.0 STABLE
