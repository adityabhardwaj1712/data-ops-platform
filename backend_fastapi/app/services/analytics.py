"""
Analytics & Metrics Service
Track platform usage, performance metrics, and business intelligence
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.models import Job, Task, DatasetVersion, AuditLog, TaskStatus, JobStatus

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for collecting and analyzing platform metrics"""
    
    async def get_dashboard_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get overall platform statistics"""
        stats = {}
        
        # Job statistics
        total_jobs = await db.execute(select(func.count(Job.id)))
        stats["total_jobs"] = total_jobs.scalar() or 0
        
        running_jobs = await db.execute(
            select(func.count(Job.id)).where(Job.status == JobStatus.RUNNING)
        )
        stats["running_jobs"] = running_jobs.scalar() or 0
        
        completed_jobs = await db.execute(
            select(func.count(Job.id)).where(Job.status == JobStatus.COMPLETED)
        )
        stats["completed_jobs"] = completed_jobs.scalar() or 0
        
        # Task statistics
        total_tasks = await db.execute(select(func.count(Task.id)))
        stats["total_tasks"] = total_tasks.scalar() or 0
        
        pending_tasks = await db.execute(
            select(func.count(Task.id)).where(Task.status == TaskStatus.PENDING)
        )
        stats["pending_tasks"] = pending_tasks.scalar() or 0
        
        # Dataset statistics
        total_datasets = await db.execute(select(func.count(DatasetVersion.id)))
        stats["total_datasets"] = total_datasets.scalar() or 0
        
        total_records = await db.execute(select(func.sum(DatasetVersion.row_count)))
        stats["total_records"] = total_records.scalar() or 0
        
        return stats
    
    async def get_performance_metrics(
        self,
        db: AsyncSession,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get performance metrics for the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Jobs created
        jobs_created = await db.execute(
            select(func.count(Job.id)).where(Job.created_at >= cutoff_date)
        )
        
        # Tasks completed
        tasks_completed = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.status == TaskStatus.COMPLETED,
                    Task.created_at >= cutoff_date
                )
            )
        )
        
        # Average confidence
        avg_confidence = await db.execute(
            select(func.avg(Task.confidence)).where(
                and_(
                    Task.confidence.isnot(None),
                    Task.created_at >= cutoff_date
                )
            )
        )
        
        return {
            "period_days": days,
            "jobs_created": jobs_created.scalar() or 0,
            "tasks_completed": tasks_completed.scalar() or 0,
            "average_confidence": round(avg_confidence.scalar() or 0, 2)
        }
    
    async def get_top_sources(self, db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently scraped sources"""
        # This would require tracking source URLs in tasks
        # For now, return empty list
        return []
    
    async def get_error_analysis(
        self,
        db: AsyncSession,
        days: int = 7
    ) -> Dict[str, Any]:
        """Analyze errors and failures"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Failed tasks
        failed_tasks = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.status == TaskStatus.FAILED,
                    Task.created_at >= cutoff_date
                )
            )
        )
        
        # Failed jobs
        failed_jobs = await db.execute(
            select(func.count(Job.id)).where(
                and_(
                    Job.status == JobStatus.FAILED,
                    Job.created_at >= cutoff_date
                )
            )
        )
        
        return {
            "failed_tasks": failed_tasks.scalar() or 0,
            "failed_jobs": failed_jobs.scalar() or 0,
            "period_days": days
        }
    
    async def get_export_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get export statistics"""
        # Count dataset versions (each represents an exportable dataset)
        total_exports = await db.execute(select(func.count(DatasetVersion.id)))
        
        # Total records exported
        total_records = await db.execute(select(func.sum(DatasetVersion.row_count)))
        
        return {
            "total_exports": total_exports.scalar() or 0,
            "total_records_exported": total_records.scalar() or 0
        }


# Global instance
analytics = AnalyticsService()
