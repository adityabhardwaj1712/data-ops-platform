"""
Visualization API Endpoints
Provide data for charts and dashboards
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.core.features import feature_flags
from app.core.cache import cache

router = APIRouter()


@router.get("/dataset/{dataset_id}/summary")
async def get_dataset_summary(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get dataset summary metrics for visualization.
    
    Returns:
        - row_count
        - field_completeness
        - confidence_distribution
        - last_updated
    """
    if not feature_flags.is_enabled("visualization"):
        raise HTTPException(status_code=403, detail="Visualization feature not enabled")
    
    viz_engine = feature_flags.get_feature("visualization")
    if not viz_engine:
        raise HTTPException(status_code=500, detail="Visualization engine not available")
    
    return await viz_engine.get_dataset_summary(dataset_id, db)


@router.get("/job/{job_id}/performance")
async def get_job_performance(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get job performance metrics.
    
    Returns:
        - execution_time
        - success_rate
        - retry_count
        - stage_timing
    """
    if not feature_flags.is_enabled("visualization"):
        raise HTTPException(status_code=403, detail="Visualization feature not enabled")
    
    viz_engine = feature_flags.get_feature("visualization")
    return await viz_engine.get_job_performance(job_id, db)


@router.get("/quality/trends")
async def get_quality_trends(
    org_id: str = "default",
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """
    Get data quality trends over time.
    
    Premium feature for Business/Enterprise tiers.
    """
    if not feature_flags.is_enabled("visualization"):
        raise HTTPException(status_code=403, detail="Visualization feature not enabled")
    
    viz_engine = feature_flags.get_feature("visualization")
    return await viz_engine.get_quality_trends(org_id, db, days)


@router.get("/usage/metrics")
async def get_usage_metrics(org_id: str = "default"):
    """
    Get usage metrics for cost analytics.
    
    Returns:
        - scrapes_used
        - scrapes_limit
        - storage_used
        - api_calls
    """
    if not feature_flags.is_enabled("cost_analytics"):
        raise HTTPException(status_code=403, detail="Cost analytics feature not enabled")
    
    viz_engine = feature_flags.get_feature("visualization")
    return await viz_engine.get_usage_metrics(org_id)


@router.get("/overview")
async def get_overview(
    org_id: str = "default",
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview dashboard data.
    
    Returns aggregated metrics for the main dashboard.
    """
    from sqlalchemy import select, func
    from app.db.models import Job, JobStatus
    
    # Get job statistics
    total_jobs = await db.execute(select(func.count(Job.id)))
    total = total_jobs.scalar() or 0
    
    running_jobs = await db.execute(
        select(func.count(Job.id)).where(Job.status == JobStatus.RUNNING)
    )
    running = running_jobs.scalar() or 0
    
    completed_jobs = await db.execute(
        select(func.count(Job.id)).where(Job.status == JobStatus.COMPLETED)
    )
    completed = completed_jobs.scalar() or 0
    
    failed_jobs = await db.execute(
        select(func.count(Job.id)).where(Job.status == JobStatus.FAILED)
    )
    failed = failed_jobs.scalar() or 0
    
    success_rate = (completed / total * 100) if total > 0 else 0
    
    return {
        "total_jobs": total,
        "running_jobs": running,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "success_rate": round(success_rate, 2),
        "avg_confidence": 0.87  # Would calculate from actual data
    }
