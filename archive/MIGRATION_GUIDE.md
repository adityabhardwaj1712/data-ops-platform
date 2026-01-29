# Migration Guide: Monolithic → Lightweight Architecture

## Overview

This guide helps you migrate from the monolithic architecture to the new lightweight architecture with separated API and Worker services.

## What Changed

### Architecture
- **Before**: Single monolithic service (~2GB, slow startup)
- **After**: Separated API (~200MB) + Worker (~1.5GB) services

### Job Execution
- **Before**: Synchronous (API waits for job completion)
- **After**: Asynchronous (API returns immediately, worker processes in background)

### Dependencies
- **Before**: All dependencies loaded at startup
- **After**: Core dependencies in API, heavy dependencies lazy-loaded in worker

## Migration Steps

### 1. Backup Your Data

```bash
# Backup database
cp backend_fastapi/data/dataops.db backend_fastapi/data/dataops.db.backup

# Backup exports
tar -czf exports_backup.tar.gz backend_fastapi/exports/
```

### 2. Stop Existing Services

```bash
# Stop old services
docker compose down

# Optional: Remove old images
docker compose down --rmi all
```

### 3. Pull Latest Code

```bash
# If using git
git pull origin main

# Or download latest code manually
```

### 4. Build New Images

```bash
# Build API and Worker images
docker compose build api worker

# Verify images were created
docker images | grep dataops
```

### 5. Start New Services

```bash
# Start API + Worker
docker compose up -d api worker

# Check status
docker compose ps

# View logs
docker compose logs -f api
docker compose logs -f worker
```

### 6. Verify Migration

```bash
# Test API health
curl http://localhost:8000/health

# Test job creation
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "schema": {"title": "string"},
    "strategy": "static"
  }'

# Should return: {"job_id": "...", "status": "queued"}
```

## API Changes

### Scraping Endpoint

**Old (Synchronous)**:
```bash
POST /api/scrape
# Returns result immediately after scraping completes
```

**New (Asynchronous)**:
```bash
# 1. Create job
POST /api/scrape
Response: {"job_id": "abc-123", "status": "queued"}

# 2. Check status
GET /api/scrape/abc-123
Response: {"status": "running", ...}

# 3. Get result
GET /api/scrape/abc-123
Response: {"status": "completed", "result": {...}}
```

### Pipeline Endpoint

**Old**:
```bash
POST /api/pipeline/run
# Waits for pipeline completion
```

**New**:
```bash
# 1. Create pipeline job
POST /api/pipeline/run
Response: {"job_id": "xyz-789", "status": "queued"}

# 2. Check status
GET /api/jobs/xyz-789
Response: {"status": "running", ...}
```

## Frontend Updates

If you're using the frontend, update your API calls:

### Before
```typescript
const result = await fetch('/api/scrape', {
  method: 'POST',
  body: JSON.stringify(scrapeRequest)
});
const data = await result.json();
// data contains scraping results
```

### After
```typescript
// 1. Create job
const createResponse = await fetch('/api/scrape', {
  method: 'POST',
  body: JSON.stringify(scrapeRequest)
});
const { job_id } = await createResponse.json();

// 2. Poll for results
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(`/api/scrape/${job_id}`);
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    clearInterval(pollInterval);
    // Use status.result
  } else if (status.status === 'failed') {
    clearInterval(pollInterval);
    // Handle error
  }
}, 2000); // Poll every 2 seconds
```

## Configuration

### Environment Variables

Create `.env` file in `backend_fastapi/`:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/dataops.db

# Logging
LOG_LEVEL=INFO

# Worker settings (for worker service only)
WORKER_ENABLED=true
WORKER_CONCURRENCY=2
WORKER_POLL_INTERVAL=5
```

## Troubleshooting

### Issue: API starts but worker doesn't process jobs

**Solution**:
```bash
# Check worker logs
docker compose logs worker

# Verify worker is running
docker compose ps worker

# Restart worker
docker compose restart worker
```

### Issue: Out of memory

**Solution**:
```bash
# Reduce worker concurrency
# Edit docker-compose.yml:
# WORKER_CONCURRENCY: 1

# Restart worker
docker compose up -d worker
```

### Issue: Jobs stuck in "queued" status

**Solution**:
```bash
# Check if worker is running
docker compose ps worker

# If not running, start it
docker compose up -d worker

# Check worker logs for errors
docker compose logs worker
```

### Issue: Database errors after migration

**Solution**:
```bash
# Stop services
docker compose down

# Restore backup
cp backend_fastapi/data/dataops.db.backup backend_fastapi/data/dataops.db

# Restart services
docker compose up -d api worker
```

## Rollback Plan

If you need to rollback to the old architecture:

```bash
# 1. Stop new services
docker compose down

# 2. Restore database backup
cp backend_fastapi/data/dataops.db.backup backend_fastapi/data/dataops.db

# 3. Checkout previous version
git checkout <previous-commit-hash>

# 4. Rebuild and start
docker compose build
docker compose up -d
```

## Performance Comparison

| Metric | Before | After |
|--------|--------|-------|
| API Startup | 30-60s | <5s |
| API Memory | 1.5-2GB | <200MB |
| Total Disk | 8GB+ | <3GB |
| Job Response | Slow (waits) | Fast (immediate) |

## Next Steps

1. ✅ Verify all services are running
2. ✅ Test job creation and execution
3. ✅ Monitor resource usage with `docker stats`
4. ✅ Update frontend to use async API pattern
5. ✅ Deploy to AWS free tier

## Support

If you encounter issues:
1. Check logs: `docker compose logs api worker`
2. Verify configuration in `docker-compose.yml`
3. Ensure database is accessible
4. Check disk space: `df -h`

## Summary

The migration preserves all functionality while dramatically reducing resource usage:
- ✅ 90% reduction in API memory usage
- ✅ 60% reduction in total disk usage
- ✅ AWS free tier compatible
- ✅ All features preserved
