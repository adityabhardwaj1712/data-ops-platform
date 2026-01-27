"""
Automation API Endpoints
Manage recurring jobs and scheduler
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from uuid import UUID

from app.core.config import settings
from app.services.scheduler import scheduler

router = APIRouter()


class ScheduleJobRequest(BaseModel):
    job_id: UUID
    schedule_type: str  # daily, weekly, hourly, custom
    schedule_config: Dict[str, Any]
    # We can't pass a function via API, so we'll likely schedule based on job template/type
    # For now, let's assume we are scheduling based on existing job definitions or templates
    # This might need refinement to work with the Scheduler's expected Callable
    # The Scheduler expects a callable, which makes it hard to expose directly via API without a registry.
    # We will assume there's a way to resolve job_id to a function or we create a wrapper.


@router.get("/jobs")
async def get_scheduled_jobs():
    """Get all scheduled jobs."""
    return {"jobs": scheduler.get_scheduled_jobs()}


@router.delete("/jobs/{job_id}")
async def unschedule_job(job_id: UUID):
    """Remove a job from the schedule."""
    await scheduler.unschedule_job(job_id)
    return {"status": "success", "message": f"Job {job_id} unscheduled"}


@router.post("/jobs/{job_id}/schedule")
async def schedule_job(job_id: UUID, request: ScheduleJobRequest):
    """
    Schedule a job.
    
    Note: In a real implementation, we would need to map the job_id to a specific execution function.
    For this implementation, we'll assume a generic job runner wrapper.
    """
    if not settings.ENABLE_BACKGROUND_JOBS:
        raise HTTPException(status_code=400, detail="Background jobs are disabled")

    # This is a placeholder for the actual job execution logic
    # In a real app, you'd lookup the job definition and pass `run_job_wrapper`
    async def dummy_job_runner(jid):
        print(f"Running job {jid}")
    
    await scheduler.schedule_job(
        job_id=job_id,
        schedule_type=request.schedule_type,
        schedule_config=request.schedule_config,
        job_function=dummy_job_runner 
    )
    
    return {"status": "success", "message": f"Job {job_id} scheduled"}
