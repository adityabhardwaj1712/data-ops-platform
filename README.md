# DataOps Scraping & Validation Platform

**Enterprise-grade data collection and validation platform** with 6-layer architecture, field-level confidence scoring, and comprehensive change detection.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- 8GB+ RAM recommended (for Ollama)

### Start Everything

```bash
# Clone and navigate
cd data-ops-platform-1

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f backend
```

### Access Points
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

## 🏗️ Architecture

### 6-Layer Pipeline
1. **Source Intelligence** - URL management, pagination, robots.txt
2. **Invisible Fetching** - Stealth browsing, proxy rotation
3. **Content Cleaning** - Trafilatura noise reduction
4. **Intent Extraction** - Heuristic + AI-powered extraction
5. **Quality Assurance** - Validation, deduplication, HITL routing
6. **Version Storage** - Immutable datasets with time travel

## 📊 Features

### ✅ Production-Ready
- **Structured Logging** - JSON logs for aggregation
- **Health Checks** - Liveness & readiness probes
- **Rate Limiting** - 120 requests/minute per IP
- **Error Handling** - Global exception middleware
- **Security Headers** - XSS protection, frame options
- **Resource Limits** - CPU/memory constraints

### ✅ Enterprise Features
- Field-level confidence scoring
- Crawl graph awareness
- Change detection between versions
- Intent templates
- Robots.txt compliance
- Excel export with source links

## 🛠️ Development

### Backend Development
```bash
cd backend_fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📝 Environment Variables

See `.env.example` files in each directory for configuration options.

## 🔒 Production Deployment

1. **Set secure secrets**:
   ```bash
   export SECRET_KEY=$(openssl rand -hex 32)
   export DATABASE_URL=postgresql://user:pass@host/db
   ```

2. **Update CORS origins** in `app/main.py`:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. **Enable JSON logging**:
   ```bash
   export LOG_JSON_FORMAT=true
   export LOG_LEVEL=INFO
   ```

4. **Deploy with Docker Compose**:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```

## 📚 API Documentation

Visit `/docs` endpoint for interactive Swagger documentation.

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs backend

# Restart service
docker compose restart backend
```

### Database connection issues
```bash
# Check database health
docker compose exec db pg_isready -U dataops

# Reset database (WARNING: deletes data)
docker compose down -v
docker compose up -d
```

### Frontend can't reach backend
- Ensure `NEXT_PUBLIC_API_URL` is set correctly
- Check network connectivity: `docker compose exec frontend ping backend`

## 📈 Monitoring

### Health Endpoints
- `/health` - Full health check
- `/health/liveness` - Simple liveness probe
- `/health/readiness` - Readiness check

### Metrics
- Request timing in `X-Process-Time` header
- Structured logs include timing and status codes

## 🔐 Security Notes

- Change `SECRET_KEY` in production
- Restrict CORS origins
- Use environment variables for secrets
- Enable rate limiting
- Review security headers

## 📄 License

MIT License - See LICENSE file
