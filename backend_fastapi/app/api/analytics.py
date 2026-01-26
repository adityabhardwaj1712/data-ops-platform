"""
Analytics API endpoints
Platform metrics and business intelligence
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.analytics import analytics

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get overall platform statistics for dashboard"""
    return await analytics.get_dashboard_stats(db)


@router.get("/performance")
async def get_performance_metrics(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics for the last N days"""
    return await analytics.get_performance_metrics(db, days=days)


@router.get("/errors")
async def get_error_analysis(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Analyze errors and failures"""
    return await analytics.get_error_analysis(db, days=days)


@router.get("/exports")
async def get_export_statistics(db: AsyncSession = Depends(get_db)):
    """Get export statistics"""
    return await analytics.get_export_statistics(db)
