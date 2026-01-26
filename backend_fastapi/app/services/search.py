"""
Search Service
Full-text search across jobs, tasks, and extracted data
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from datetime import datetime
import logging

from app.db.models import Job, Task, DatasetVersion

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching across platform data"""
    
    async def search_jobs(
        self,
        db: AsyncSession,
        query: str,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs by name, intent, or description"""
        stmt = select(Job).where(
            or_(
                Job.name.ilike(f"%{query}%"),
                Job.intent.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%")
            )
        )
        
        if status:
            stmt = stmt.where(Job.status == status)
        
        stmt = stmt.limit(limit)
        
        result = await db.execute(stmt)
        jobs = result.scalars().all()
        
        return [
            {
                "id": str(job.id),
                "name": job.name,
                "status": job.status.value,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ]
    
    async def search_tasks(
        self,
        db: AsyncSession,
        query: str,
        job_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search tasks by URL or extracted data"""
        stmt = select(Task).where(
            or_(
                Task.payload['url'].astext.ilike(f"%{query}%"),
                Task.result.ilike(f"%{query}%")
            )
        )
        
        if job_id:
            stmt = stmt.where(Task.job_id == job_id)
        
        stmt = stmt.limit(limit)
        
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        return [
            {
                "id": str(task.id),
                "url": task.payload.get("url"),
                "status": task.status.value,
                "confidence": task.confidence
            }
            for task in tasks
        ]
    
    async def search_datasets(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search datasets by job name or metadata"""
        stmt = select(DatasetVersion).join(Job).where(
            Job.name.ilike(f"%{query}%")
        ).limit(limit)
        
        result = await db.execute(stmt)
        datasets = result.scalars().all()
        
        return [
            {
                "id": str(dataset.id),
                "job_id": str(dataset.job_id),
                "version": dataset.version,
                "row_count": dataset.row_count,
                "created_at": dataset.created_at.isoformat()
            }
            for dataset in datasets
        ]
    
    async def global_search(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Perform global search across all entities"""
        return {
            "jobs": await self.search_jobs(db, query, limit=limit),
            "tasks": await self.search_tasks(db, query, limit=limit),
            "datasets": await self.search_datasets(db, query, limit=limit)
        }


# Global instance
search_service = SearchService()
