"""
Enhanced Health Check Endpoint
Checks database, external services, and system health
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import httpx
from typing import Dict, Any

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint
    
    Returns:
        Health status with database, LLM, and system checks
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "checks": {}
    }
    
    # Database check
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": 0  # Could measure this
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # LLM service check (Ollama)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.OLLAMA_URL.replace("/api/generate", ""))
            health_status["checks"]["llm"] = {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "url": settings.OLLAMA_URL
            }
    except Exception as e:
        health_status["checks"]["llm"] = {
            "status": "unavailable",
            "error": str(e)
        }
        # LLM failure doesn't make the whole system unhealthy
    
    # System resources (basic)
    try:
        import psutil
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent
        }
    except ImportError:
        # psutil not installed, skip
        pass
    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    return health_status


@router.get("/health/liveness")
async def liveness_check():
    """Simple liveness probe for Kubernetes/Docker"""
    return {"status": "alive"}


@router.get("/health/readiness")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe - checks if service can accept requests"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi import Response
        return Response(
            content='{"status": "not_ready"}',
            status_code=503,
            media_type="application/json"
        )
