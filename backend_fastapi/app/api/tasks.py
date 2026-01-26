from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models import Task, Job
from app.schemas import TaskCreate, TaskResponse


router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task for a job"""
    # Verify job exists
    result = await db.execute(select(Job).where(Job.id == task_data.job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    task = Task(
        job_id=task_data.job_id,
        type=task_data.type,
        payload=task_data.payload
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    job_id: UUID = None,
    status: str = None,
    task_type: str = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List tasks with optional filters"""
    query = select(Task).order_by(Task.created_at.desc()).offset(offset).limit(limit)
    
    if job_id:
        query = query.where(Task.job_id == job_id)
    if status:
        query = query.where(Task.status == status)
    if task_type:
        query = query.where(Task.type == task_type)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific task"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retry a failed task"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status.value not in ["FAILED", "BLOCKED"]:
        raise HTTPException(status_code=400, detail="Can only retry failed or blocked tasks")
    
    task.status = "PENDING"
    task.retry_count += 1
    task.result = None
    
    await db.commit()
    await db.refresh(task)
    return task
