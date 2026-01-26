"""
Batch Operations API
Perform operations on multiple jobs/tasks at once
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import Job, Task, JobStatus, TaskStatus

router = APIRouter()


class BatchJobRequest(BaseModel):
    job_ids: List[UUID]
    action: str  # "cancel", "delete", "retry"


class BatchTaskRequest(BaseModel):
    task_ids: List[UUID]
    action: str  # "cancel", "retry", "delete"


@router.post("/jobs")
async def batch_job_operation(
    request: BatchJobRequest,
    db: AsyncSession = Depends(get_db)
):
    """Perform batch operations on jobs"""
    if request.action == "cancel":
        stmt = update(Job).where(
            Job.id.in_(request.job_ids),
            Job.status == JobStatus.RUNNING
        ).values(status=JobStatus.CANCELLED)
        
        result = await db.execute(stmt)
        await db.commit()
        
        return {"updated": result.rowcount, "action": "cancel"}
    
    elif request.action == "delete":
        stmt = select(Job).where(Job.id.in_(request.job_ids))
        result = await db.execute(stmt)
        jobs = result.scalars().all()
        
        for job in jobs:
            await db.delete(job)
        
        await db.commit()
        
        return {"deleted": len(jobs), "action": "delete"}
    
    elif request.action == "retry":
        stmt = update(Job).where(
            Job.id.in_(request.job_ids),
            Job.status == JobStatus.FAILED
        ).values(status=JobStatus.PENDING)
        
        result = await db.execute(stmt)
        await db.commit()
        
        return {"updated": result.rowcount, "action": "retry"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")


@router.post("/tasks")
async def batch_task_operation(
    request: BatchTaskRequest,
    db: AsyncSession = Depends(get_db)
):
    """Perform batch operations on tasks"""
    if request.action == "cancel":
        stmt = update(Task).where(
            Task.id.in_(request.task_ids),
            Task.status == TaskStatus.PENDING
        ).values(status=TaskStatus.CANCELLED)
        
        result = await db.execute(stmt)
        await db.commit()
        
        return {"updated": result.rowcount, "action": "cancel"}
    
    elif request.action == "retry":
        stmt = update(Task).where(
            Task.id.in_(request.task_ids),
            Task.status == TaskStatus.FAILED
        ).values(status=TaskStatus.PENDING, retry_count=0)
        
        result = await db.execute(stmt)
        await db.commit()
        
        return {"updated": result.rowcount, "action": "retry"}
    
    elif request.action == "delete":
        stmt = select(Task).where(Task.id.in_(request.task_ids))
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        for task in tasks:
            await db.delete(task)
        
        await db.commit()
        
        return {"deleted": len(tasks), "action": "delete"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
