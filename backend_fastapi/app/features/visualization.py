"""
Visualization Engine
Generate charts and metrics for datasets, jobs, and quality
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import logging

from app.core.cache import cache

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Generate visualization data for frontend charts.
    
    All metrics are pre-computed and cached for performance.
    """
    
    @cache.cached(ttl=300, key_prefix="viz")
    async def get_dataset_summary(self, dataset_id: UUID, db) -> Dict[str, Any]:
        """
        Get dataset summary metrics.
        
        Returns:
            - row_count: Total rows
            - field_completeness: % non-null per field
            - confidence_distribution: Histogram of confidence scores
            - last_updated: Timestamp
        """
        from sqlalchemy import select, func
        from app.db.models import Task
        
        # Get tasks for this dataset
        stmt = select(Task).where(Task.job_id == dataset_id)
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        if not tasks:
            return {
                "row_count": 0,
                "field_completeness": {},
                "confidence_distribution": [],
                "last_updated": None
            }
        
        # Calculate metrics
        row_count = len(tasks)
        
        # Field completeness
        field_completeness = self._calculate_field_completeness(tasks)
        
        # Confidence distribution
        confidence_dist = self._calculate_confidence_distribution(tasks)
        
        return {
            "row_count": row_count,
            "field_completeness": field_completeness,
            "confidence_distribution": confidence_dist,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    @cache.cached(ttl=300, key_prefix="viz")
    async def get_job_performance(self, job_id: UUID, db) -> Dict[str, Any]:
        """
        Get job performance metrics.
        
        Returns:
            - execution_time: Average execution time
            - success_rate: % successful tasks
            - retry_count: Total retries
            - stage_timing: Time per pipeline stage
        """
        from sqlalchemy import select
        from app.db.models import Task, TaskStatus
        
        stmt = select(Task).where(Task.job_id == job_id)
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        if not tasks:
            return {
                "execution_time": 0,
                "success_rate": 0,
                "retry_count": 0,
                "stage_timing": {}
            }
        
        # Calculate metrics
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED]
        
        success_rate = (len(completed) / len(tasks) * 100) if tasks else 0
        
        return {
            "execution_time": 0,  # Would calculate from timestamps
            "success_rate": round(success_rate, 2),
            "retry_count": 0,  # Would track retries
            "stage_timing": {}
        }
    
    @cache.cached(ttl=300, key_prefix="viz")
    async def get_quality_trends(self, org_id: str, db, days: int = 7) -> List[Dict]:
        """
        Get data quality trends over time.
        
        Returns list of daily quality scores.
        """
        # Generate sample data for now
        # In production, would query actual quality scores from database
        trends = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            trends.append({
                "date": date.isoformat(),
                "quality_score": 85 + (i % 10),  # Sample data
                "completeness": 90 + (i % 5),
                "accuracy": 88 + (i % 7)
            })
        
        return trends
    
    @cache.cached(ttl=60, key_prefix="viz")
    async def get_usage_metrics(self, org_id: str) -> Dict[str, Any]:
        """
        Get usage metrics for cost analytics.
        
        Returns:
            - scrapes_used: Current month scrapes
            - scrapes_limit: Plan limit
            - storage_used: Bytes used
            - api_calls: Total API calls
        """
        from app.core.usage import usage_tracker
        
        quota_status = await usage_tracker.get_quota_status(org_id)
        
        return {
            "scrapes": quota_status["scrapes"],
            "ai_queries": quota_status["ai_queries"],
            "storage_used": 0,  # Would track actual storage
            "api_calls": 0  # Would track actual API calls
        }
    
    def _calculate_field_completeness(self, tasks: List) -> Dict[str, float]:
        """Calculate % non-null for each field."""
        if not tasks:
            return {}
        
        field_counts = {}
        total = len(tasks)
        
        for task in tasks:
            if task.result:
                for field, value in task.result.items():
                    if field not in field_counts:
                        field_counts[field] = 0
                    if value is not None:
                        field_counts[field] += 1
        
        return {
            field: round(count / total * 100, 2)
            for field, count in field_counts.items()
        }
    
    def _calculate_confidence_distribution(self, tasks: List) -> List[Dict]:
        """Calculate confidence score distribution."""
        # Group by confidence ranges
        ranges = {
            "0-20%": 0,
            "20-40%": 0,
            "40-60%": 0,
            "60-80%": 0,
            "80-100%": 0
        }
        
        for task in tasks:
            if task.confidence is not None:
                conf = task.confidence * 100
                if conf < 20:
                    ranges["0-20%"] += 1
                elif conf < 40:
                    ranges["20-40%"] += 1
                elif conf < 60:
                    ranges["40-60%"] += 1
                elif conf < 80:
                    ranges["60-80%"] += 1
                else:
                    ranges["80-100%"] += 1
        
        return [
            {"range": range_name, "count": count}
            for range_name, count in ranges.items()
        ]
