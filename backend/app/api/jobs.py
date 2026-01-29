from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models import Job, Task, TaskType, TaskStatus, JobConfig
from app.db.models import JobStatus as DBJobStatus
from app.schemas import JobCreate, JobResponse, JobUpdate


router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new data collection job"""
    job = Job(
        description=job_data.description,
        schema=job_data.schema,
        config=job_data.config,
        status=DBJobStatus.PENDING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Create initial versioned config
    job_config = JobConfig(
        job_id=job.id,
        version=1,
        config=job_data.config or {},
        is_active=1
    )
    db.add(job_config)
    await db.commit()
    
    return job


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all jobs with optional status filter"""
    query = select(Job).order_by(Job.created_at.desc()).offset(offset).limit(limit)
    
    if status:
        query = query.where(Job.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific job by ID"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_data.description:
        job.description = job_data.description
    if job_data.status:
        job.status = job_data.status
    if job_data.config:
        # Check if config actually changed
        if job.config != job_data.config:
            # Get latest version
            config_result = await db.execute(
                select(JobConfig)
                .where(JobConfig.job_id == job_id)
                .order_by(JobConfig.version.desc())
                .limit(1)
            )
            latest_config = config_result.scalar_one_or_none()
            new_version = (latest_config.version + 1) if latest_config else 1
            
            # Deactivate old configs
            # (In a more complex system we might do this, but for now just add new one)
            
            job.config = job_data.config
            
            new_job_config = JobConfig(
                job_id=job_id,
                version=new_version,
                config=job_data.config,
                is_active=1
            )
            db.add(new_job_config)

    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a job and all related data"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.delete(job)
    await db.commit()


@router.get("/{job_id}/stats")
async def get_job_stats(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get statistics for a job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get task counts
    tasks_result = await db.execute(select(Task).where(Task.job_id == job_id))
    tasks = tasks_result.scalars().all()
    
    stats = {
        "total_tasks": len(tasks),
        "by_status": {},
        "by_type": {}
    }
    
    for task in tasks:
        status = task.status.value
        task_type = task.type.value
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        stats["by_type"][task_type] = stats["by_type"].get(task_type, 0) + 1
    
    return stats
