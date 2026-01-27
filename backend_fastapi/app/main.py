from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api import (
    jobs, tasks, scrape, hitl, audit, pipeline, robots, export, templates,
    analytics, websocket, search, backup, notifications, batch, visualization,
    ai, quality, automation
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

# -------------------------------------------------
# Logging
# -------------------------------------------------
logger = setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    json_format=not settings.DEBUG
)

# -------------------------------------------------
# Lifespan (Startup / Shutdown)
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DataOps Platform v2.0.0")

    # ✅ Create database tables
    # SQLite file will be created automatically by SQLAlchemy
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    logger.info("Database initialized")

    # -------------------------------------------------
    # Background Worker
    # -------------------------------------------------
    worker_enabled = os.getenv("WORKER_ENABLED", "false").lower() == "true"

    if worker_enabled:
        from app.worker.main import worker_service
        await worker_service.start()
        logger.info("Background worker started")
    else:
        logger.info("Worker disabled (API-only mode)")

    # -------------------------------------------------
    # Scheduler (API-only mode)
    # -------------------------------------------------
    if settings.ENABLE_BACKGROUND_JOBS and not worker_enabled:
        from app.services.scheduler import scheduler
        await scheduler.start()
        logger.info("Scheduler started")

    logger.info("Platform ready to accept requests")
    yield

    # -------------------------------------------------
    # Shutdown
    # -------------------------------------------------
    logger.info("Shutting down DataOps Platform")

    if worker_enabled:
        from app.worker.main import worker_service
        await worker_service.stop()
        logger.info("Background worker stopped")

    if settings.ENABLE_BACKGROUND_JOBS and not worker_enabled:
        from app.services.scheduler import scheduler
        await scheduler.stop()
        logger.info("Scheduler stopped")

    await engine.dispose()
    logger.info("Database engine disposed")

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="DataOps Platform",
    description="Pro-level data scraping and quality assurance platform",
    version="2.0.0",
    lifespan=lifespan,
)

# -------------------------------------------------
# Middleware (ORDER MATTERS)
# -------------------------------------------------
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(RequestLoggingMiddleware)

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(scrape.router, prefix="/api/scrape", tags=["scrape"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["visualization"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(backup.router, prefix="/api/backup", tags=["backup"])
app.include_router(hitl.router, prefix="/api/hitl", tags=["hitl"])
app.include_router(robots.router, prefix="/api/robots", tags=["robots"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(batch.router, prefix="/api/batch", tags=["batch"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(quality.router, prefix="/api/quality", tags=["quality"])
app.include_router(automation.router, prefix="/api/automation", tags=["automation"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# -------------------------------------------------
# Health Checks
# -------------------------------------------------
app.include_router(health_router, tags=["health"])

