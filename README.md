# DataOps Platform - Lightweight Architecture

## 🚀 Quick Start

### Option 1: API + Worker (Recommended for AWS Free Tier)
```bash
# Start API and Worker services
docker compose up -d api worker

# Check status
docker compose ps

# View logs
docker compose logs -f api
docker compose logs -f worker
```

### Option 2: Full Stack (includes Frontend)
```bash
# Start all services
docker compose --profile full up -d
```

### Option 3: API Only (Minimal Resources)
```bash
# Start only the API (no background processing)
docker compose up -d api
```

## 📊 Resource Usage

| Service | Memory | Disk | Startup Time |
|---------|--------|------|--------------|
| API | <200MB | ~200MB | <5s |
| Worker | <1GB (idle) | ~1.5GB | ~10s |
| Frontend | ~300MB | ~300MB | ~5s |
| **Total** | **<1.5GB** | **<3GB** | **<20s** |

✅ **AWS Free Tier Compatible** (8GB volume limit)

## 🏗️ Architecture

### Lightweight API Core (Always Running)
- Handles HTTP requests
- Manages job queue
- Updates job status
- Serves WebSocket connections
- **No heavy dependencies loaded**

### Background Worker (On-Demand)
- Processes jobs from queue
- Lazy-loads heavy libraries only when needed
- Executes scraping, pipeline, export jobs
- Can be scaled horizontally

### Job Flow
```
1. User → POST /api/scrape → API creates job → Returns job_id immediately
2. API → Enqueues job → Job queue
3. Worker → Dequeues job → Lazy-loads scraper → Executes → Updates status
4. User → GET /api/scrape/{job_id} → Gets result
```

## 📝 API Changes

### Before (Synchronous)
```bash
POST /api/scrape
# Waits 30-60s for scraping to complete
# Returns result immediately
```

### After (Asynchronous)
```bash
# 1. Create job (returns immediately)
POST /api/scrape
Response: {"job_id": "...", "status": "queued"}

# 2. Check status (poll every few seconds)
GET /api/scrape/{job_id}
Response: {"status": "running", ...}

# 3. Get result when completed
GET /api/scrape/{job_id}
Response: {"status": "completed", "result": {...}}
```

## 🔧 Configuration

### Environment Variables

**API Service:**
```env
DATABASE_URL=sqlite+aiosqlite:///./data/dataops.db
LOG_LEVEL=INFO
WORKER_ENABLED=false  # API doesn't run workers
```

**Worker Service:**
```env
DATABASE_URL=sqlite+aiosqlite:///./data/dataops.db
LOG_LEVEL=INFO
WORKER_ENABLED=true
WORKER_CONCURRENCY=2  # Number of parallel workers
WORKER_POLL_INTERVAL=5  # Seconds between queue polls
```

## 🐳 Docker Commands

```bash
# Build images
docker compose build

# Start services
docker compose up -d api worker

# Scale workers
docker compose up -d --scale worker=2

# Stop worker to save resources
docker compose stop worker

# Monitor resource usage
docker stats

# View logs
docker compose logs -f api
docker compose logs -f worker

# Restart services
docker compose restart api worker

# Clean up
docker compose down
docker compose down -v  # Remove volumes too
```

## 📦 Deployment

### AWS Free Tier (t2.micro, 8GB volume)
```bash
# 1. SSH into EC2 instance
ssh -i key.pem ec2-user@your-instance

# 2. Clone repository
git clone <your-repo>
cd data-ops-platform-1

# 3. Start services (API + Worker only)
docker compose up -d api worker

# 4. Verify
curl http://localhost:8000/health
```

### Resource Monitoring
```bash
# Check disk usage
du -sh .
df -h

# Check memory usage
free -h
docker stats

# Check running containers
docker compose ps
```

## 🧪 Testing

### Test API Startup
```bash
# Should start in <5 seconds
time docker compose up -d api

# Check health
curl http://localhost:8000/health/liveness
```

### Test Job Execution
```bash
# 1. Create a scraping job
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "schema": {"title": "string"},
    "strategy": "static"
  }'

# Response: {"job_id": "...", "status": "queued"}

# 2. Check job status
curl http://localhost:8000/api/scrape/{job_id}

# 3. Get results (when status=completed)
curl http://localhost:8000/api/scrape/{job_id}
```

## 🔍 Troubleshooting

### API won't start
```bash
# Check logs
docker compose logs api

# Verify dependencies
docker compose exec api pip list
```

### Worker not processing jobs
```bash
# Check worker logs
docker compose logs worker

# Verify worker is running
docker compose ps worker

# Check queue status
curl http://localhost:8000/api/analytics/dashboard
```

### Out of memory
```bash
# Stop worker temporarily
docker compose stop worker

# Reduce worker concurrency
# Edit docker-compose.yml: WORKER_CONCURRENCY=1
docker compose up -d worker
```

### Disk space issues
```bash
# Check disk usage
df -h

# Clean up old Docker images
docker system prune -a

# Remove old exports
rm -rf backend_fastapi/exports/*
```

## 📈 Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API Startup | 30-60s | <5s | **90% faster** |
| API Memory | 1.5-2GB | <200MB | **90% reduction** |
| Docker Image (API) | 2GB+ | <300MB | **85% reduction** |
| Total Disk | 8GB+ | <3GB | **60% reduction** |
| AWS Free Tier | ❌ No | ✅ Yes | **Achieved** |

## ✅ Features Preserved

All features remain 100% functional:
- ✅ Scraping (static, browser, stealth)
- ✅ 6-layer pipeline
- ✅ HITL review
- ✅ Export (Excel, CSV, JSON)
- ✅ Analytics dashboard
- ✅ WebSocket updates
- ✅ Search functionality
- ✅ Backup/restore
- ✅ Batch operations
- ✅ Notifications

## 🔐 Security

- Non-root containers
- Resource limits enforced
- Rate limiting enabled
- Security headers configured
- Secrets via environment variables

## 📄 License

MIT License
