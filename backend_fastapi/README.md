# DataOps Scraping & Validation Platform

A **production-grade, enterprise-level** data collection and validation platform that goes beyond basic web scraping. This system treats data as versioned, auditable assets with field-level confidence scoring, crawl graph awareness, and comprehensive change detection.

## 🏗️ Architecture Overview

### 6-Layer Enterprise Architecture

1. **🛡️ Source Intelligence & Management** - Multi-URL handling, pagination detection, robots.txt compliance
2. **👻 Invisible Fetching Engine** - Stealth browsing, proxy rotation, CAPTCHA detection
3. **🧹 Content Cleaning & Noise Reduction** - Trafilatura-powered content isolation
4. **🧠 Intent-Based Data Extraction** - Heuristic + AI-powered extraction with field-level confidence
5. **💎 Data Quality & Trust Engine** - Pydantic validation, deduplication, HITL routing
6. **📦 Dataset Versioning & Automation** - Time travel, audit trails, webhooks

## 🚀 New Enterprise Features

### ✅ Field-Level Confidence Scoring
```python
{
  "title": {"value": "Software Engineer", "confidence": 0.95},
  "company": {"value": "Tech Corp", "confidence": 0.87},
  "location": {"value": "New York", "confidence": 0.60}  # Needs HITL review
}
```

### ✅ Crawl Graph Awareness
- **Parent-child relationships** between scraped pages
- **Smart deduplication** across crawl depths
- **Pagination detection** from content analysis
- **Depth-limited crawling** to prevent explosion

### ✅ Change Detection & Version Intelligence
```bash
# Compare dataset versions
GET /api/audit/versions/compare

# Detect: new jobs, removed jobs, price changes, etc.
{
  "changes": [
    {"type": "ADDED", "record_id": "job_123", "confidence": 0.92},
    {"type": "MODIFIED", "record_id": "job_456", "fields_changed": ["salary"]},
    {"type": "REMOVED", "record_id": "job_789"}
  ]
}
```

### ✅ Intent Templates (No More Free-Text)
```python
# Instead of: "Find DevOps jobs in India"
POST /api/templates/apply
{
  "template_id": "job_listing_template",
  "filters": {"role": "DevOps", "location": "India", "experience": "fresher"}
}
```

### ✅ Robots.txt Compliance & Ethical Scraping
```python
# Automatic robots.txt checking
GET /api/robots/check?domain=linkedin.com

# Respectful crawl delays
GET /api/robots/delay/linkedin.com  # Returns minimum delay seconds
```

### ✅ Excel Export with Source Links
```python
POST /api/export/
{
  "job_id": "uuid",
  "format": "excel",
  "include_source_links": true,
  "include_confidence": true
}
# Downloads: Job_Data_v2_20241201.xlsx with source URLs & confidence scores
```

## 🛠️ Quick Start

```bash
# Install dependencies (includes Excel, robots parsing, change detection)
pip install -r requirements.txt

# Run the platform
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 API Endpoints

### Core Scraping
- `POST /api/scrape/` - Single URL scraping
- `POST /api/pipeline/run` - Full 6-layer pipeline
- `POST /api/jobs/` - Create scraping jobs

### New Enterprise Features
- `POST /api/templates/` - Create intent templates
- `POST /api/templates/apply` - Use templates
- `POST /api/export/` - Export datasets (Excel/CSV/JSON)
- `POST /api/robots/check` - Robots.txt compliance
- `POST /api/audit/versions/compare` - Change detection

### Human-in-the-Loop
- `GET /api/hitl/pending` - Get items needing review
- `POST /api/hitl/submit` - Submit human-reviewed data

## 🎯 Usage Examples

### 1. Using Intent Templates
```python
# Create a job listing template
POST /api/templates/
{
  "name": "tech_jobs",
  "intent_type": "JOB_LISTING",
  "description": "Technical job listings",
  "template_schema": {
    "title": "str", "company": "str", "location": "str",
    "salary": "str", "description": "str"
  },
  "filters": {"type": "technical"}
}

# Apply template to scrape
POST /api/templates/apply
{
  "template_id": "uuid-from-above",
  "filters": {"role": "DevOps", "location": "India"},
  "sources": ["https://example.com/jobs"]
}
```

### 2. Export with Source Links
```python
POST /api/export/
{
  "job_id": "your-job-uuid",
  "version": 2,
  "format": "excel",
  "include_source_links": true,
  "include_confidence": true
}
# Result: Excel file with columns like:
# Title | Company | Location | Source_URL | Confidence_Score | title_confidence | ...
```

### 3. Change Detection
```python
POST /api/audit/versions/compare
{
  "job_id": "your-job-uuid",
  "from_version": 1,
  "to_version": 2
}
# Returns detailed diff with added/modified/removed records
```

## 🔒 Production Features

- **Stealth 2.0**: Deep hardware spoofing, behavioral mimicry
- **Global Limits**: Prevent system overload
- **Audit Trails**: Every decision logged and auditable
- **Version Control**: Time travel across dataset versions
- **Webhook Integration**: Automated downstream delivery
- **Ethical Compliance**: Robots.txt respect, crawl delays

## 📈 Performance & Reliability

- **Confidence-weighted deduplication**
- **Memory-efficient processing**
- **Error recovery and retries**
- **Background job processing**
- **Real-time monitoring**

## 🏢 Enterprise Positioning

This isn't just a scraper—it's a **Managed Data Collection & Validation Platform** suitable for:
- Enterprise data pipelines
- Regulatory compliance (GDPR, CCPA)
- Audit requirements
- Multi-stakeholder data validation
- Production ML training data collection

## 📚 API Documentation

Visit `http://localhost:8000/docs` for comprehensive interactive API documentation with examples.
