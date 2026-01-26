from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import (
    jobs, tasks, scrape, hitl, audit, pipeline, robots, export, templates,
    analytics, websocket, search, backup, notifications, batch
)
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware
)
from app.core.health import router as health_router
from app.db.session import engine
from app.db import models

# Setup logging
logger = setup_logging(level="INFO" if not settings.DEBUG else "DEBUG", json_format=not settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting DataOps Platform v2.0.0")
    
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    logger.info("Database tables initialized")
    
    # Start background services
    if settings.ENABLE_BACKGROUND_JOBS:
        from app.services.scheduler import scheduler
        await scheduler.start()
        logger.info("Background job scheduler started")
    
    logger.info("Platform ready to accept requests")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down DataOps Platform")
    
    # Stop background services
    if settings.ENABLE_BACKGROUND_JOBS:
        from app.services.scheduler import scheduler
        await scheduler.stop()
    
    await engine.dispose()


app = FastAPI(
    title="DataOps Platform",
    description="Pro-level data scraping and quality assurance platform with 5-layer architecture",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware (order matters!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(RequestLoggingMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["Scraping"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["5-Layer Pipeline"])
app.include_router(hitl.router, prefix="/api/hitl", tags=["Human-in-the-Loop"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(robots.router, prefix="/api/robots", tags=["Robots.txt"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(templates.router, prefix="/api/templates", tags=["Intent Templates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backup & Restore"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(batch.router, prefix="/api/batch", tags=["Batch Operations"])

# Health check routes
app.include_router(health_router, tags=["Health"])
