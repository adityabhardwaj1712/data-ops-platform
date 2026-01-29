# DataOps Platform - Multi-Functionality Features

## 🎯 Core Features

### 1. **6-Layer Scraping Pipeline**
- Source Intelligence & Management
- Invisible Fetching Engine
- Content Cleaning & Noise Reduction
- Intent-Based Data Extraction
- Data Quality & Trust Engine
- Dataset Versioning & Automation

### 2. **Enterprise Data Management**
- ✅ Field-level confidence scoring
- ✅ Crawl graph awareness
- ✅ Change detection between versions
- ✅ Intent templates
- ✅ Robots.txt compliance
- ✅ Excel/CSV/JSON export with source links

## 🚀 New Multi-Functionality Features

### 3. **Search & Discovery**
- **Full-text search** across jobs, tasks, and datasets
- **Global search** across all entities
- **Filtered search** by status, type, date range
- **API Endpoints:**
  - `GET /api/search/jobs?q=query`
  - `GET /api/search/tasks?q=query`
  - `GET /api/search/datasets?q=query`
  - `GET /api/search/global?q=query`

### 4. **Backup & Restore**
- **Create backups** of jobs and datasets
- **List all backups** with metadata
- **Restore backups** to new jobs
- **Automatic data file backup**
- **API Endpoints:**
  - `POST /api/backup/create/{job_id}`
  - `GET /api/backup/list`
  - `POST /api/backup/restore?backup_file=path`

### 5. **Notification System**
- **Real-time notifications** for job events
- **Notification types:** job completed, failed, low confidence, export ready
- **Unread notification tracking**
- **Mark as read** functionality
- **API Endpoints:**
  - `GET /api/notifications/`
  - `GET /api/notifications/unread/count`
  - `POST /api/notifications/{id}/read`
  - `POST /api/notifications/read-all`

### 6. **Batch Operations**
- **Batch cancel** multiple jobs/tasks
- **Batch delete** multiple jobs/tasks
- **Batch retry** failed jobs/tasks
- **Efficient bulk operations**
- **API Endpoints:**
  - `POST /api/batch/jobs` - Batch job operations
  - `POST /api/batch/tasks` - Batch task operations

### 7. **Analytics & Metrics**
- **Dashboard statistics** (total jobs, tasks, datasets)
- **Performance metrics** (last N days)
- **Error analysis** (failed tasks/jobs)
- **Export statistics**
- **API Endpoints:**
  - `GET /api/analytics/dashboard`
  - `GET /api/analytics/performance?days=7`
  - `GET /api/analytics/errors?days=7`
  - `GET /api/analytics/exports`

### 8. **Real-Time Updates (WebSocket)**
- **Live job progress** updates
- **Extraction events** broadcasting
- **Connection management**
- **Ping/pong keepalive**
- **WebSocket Endpoint:**
  - `WS /ws` - Real-time updates

### 9. **Scheduled Jobs**
- **Recurring job scheduling** (hourly, daily, weekly, custom)
- **Automatic job execution**
- **Schedule management**
- **Next run calculation**
- **Background scheduler** service

### 10. **Production Features**
- ✅ **Structured logging** (JSON format)
- ✅ **Request logging** middleware
- ✅ **Error handling** middleware
- ✅ **Rate limiting** (120 req/min)
- ✅ **Security headers** (XSS protection, frame options)
- ✅ **Health checks** (liveness, readiness)
- ✅ **Resource limits** (CPU, memory)
- ✅ **Non-root user** in Docker
- ✅ **Auto-restart** on failure

## 📊 API Summary

### Core APIs
- `/api/jobs` - Job management
- `/api/tasks` - Task management
- `/api/scrape` - Single URL scraping
- `/api/pipeline` - Full pipeline execution
- `/api/hitl` - Human-in-the-loop review
- `/api/audit` - Audit logs and version comparison
- `/api/robots` - Robots.txt checking
- `/api/export` - Data export (Excel/CSV/JSON)
- `/api/templates` - Intent templates

### New Multi-Function APIs
- `/api/search` - Full-text search
- `/api/backup` - Backup & restore
- `/api/notifications` - Notification system
- `/api/batch` - Batch operations
- `/api/analytics` - Analytics & metrics
- `/ws` - WebSocket for real-time updates

## 🔧 Usage Examples

### Search Example
```bash
# Search for jobs
curl "http://localhost:8000/api/search/jobs?q=devops&limit=10"

# Global search
curl "http://localhost:8000/api/search/global?q=react"
```

### Backup Example
```bash
# Create backup
curl -X POST "http://localhost:8000/api/backup/create/{job_id}?include_data=true"

# List backups
curl "http://localhost:8000/api/backup/list"

# Restore backup
curl -X POST "http://localhost:8000/api/backup/restore?backup_file=backups/backup_xxx.json"
```

### Batch Operations Example
```bash
# Cancel multiple jobs
curl -X POST "http://localhost:8000/api/batch/jobs" \
  -H "Content-Type: application/json" \
  -d '{"job_ids": ["uuid1", "uuid2"], "action": "cancel"}'

# Retry failed tasks
curl -X POST "http://localhost:8000/api/batch/tasks" \
  -H "Content-Type: application/json" \
  -d '{"task_ids": ["uuid1", "uuid2"], "action": "retry"}'
```

### Notifications Example
```bash
# Get unread notifications
curl "http://localhost:8000/api/notifications/?unread_only=true"

# Mark as read
curl -X POST "http://localhost:8000/api/notifications/123/read"
```

## 🐳 Docker Deployment

All features are containerized and production-ready:

```bash
# Start all services
docker compose up -d

# Check health
curl http://localhost:8000/health

# View logs
docker compose logs -f backend
```

## 📈 Performance

- **Concurrent jobs:** Up to 10 simultaneous jobs
- **Rate limiting:** 120 requests/minute per IP
- **Search:** Fast full-text search across all entities
- **Backup:** Efficient file-based backups
- **WebSocket:** Real-time updates with connection pooling

## 🔒 Security

- **Security headers:** XSS protection, frame options
- **Rate limiting:** Prevents abuse
- **Error handling:** No sensitive data leakage
- **Non-root containers:** Enhanced security
- **Input validation:** All endpoints validated

## 🎨 Frontend Integration

All APIs are ready for frontend integration:
- Search UI components
- Notification center
- Backup management panel
- Batch operation interface
- Real-time dashboard updates
