from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api import (
    jobs, scrape, hitl, robots, export
    # FUTURE_PHASE: analytics, search, backup, notifications, batch, visualization, ai, quality, automation, templates
)
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
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
        # from app.services.scheduler import scheduler
        # await scheduler.start()
        # logger.info("Scheduler started")
        pass

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
        # from app.services.scheduler import scheduler
        # await scheduler.stop()
        # logger.info("Scheduler stopped")
        pass

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
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open CORS for dev/codespaces
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape.router, prefix="/api/scrape", tags=["scrape"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
# app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(hitl.router, prefix="/api/hitl", tags=["hitl"])
# app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(robots.router, prefix="/api/robots", tags=["robots"])
# app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# Health Checks & Static Files
# -------------------------------------------------
from fastapi.staticfiles import StaticFiles
os.makedirs("/app/data/artifacts", exist_ok=True)
os.makedirs("/app/data/exports", exist_ok=True)
app.mount("/data", StaticFiles(directory="/app/data"), name="data")

app.include_router(health_router, tags=["health"])

