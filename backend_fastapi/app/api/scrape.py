from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from app.db.session import get_db
from app.db.models import Job, Task, TaskType, TaskStatus
from app.db.models import JobStatus as DBJobStatus
from app.schemas import ScrapeRequest
from app.queue.job_queue import job_queue


router = APIRouter()


@router.post("/")
async def scrape_url(
    request: ScrapeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a scraping job (async execution).
    Returns job_id immediately, scraping happens in background worker.
    
    Use GET /scrape/{job_id} to check status and get results.
    """
    # Create a job for this scrape request
    job = Job(
        description=f"Scrape {request.url}",
        schema=request.schema,
        config={
            "url": request.url,
            "prompt": request.prompt,
            "strategy": request.strategy.value,
            "max_pages": request.max_pages,
            "stealth_mode": request.stealth_mode,
            "use_proxy": request.use_proxy,
            "wait_for_selector": request.wait_for_selector,
            "timeout": request.timeout
        },
        status=DBJobStatus.PENDING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Enqueue the job for background processing
    await job_queue.enqueue(
        job_id=job.id,
        job_type="SCRAPE",
        payload={
            "url": request.url,
            "schema": request.schema,
            "prompt": request.prompt,
            "strategy": request.strategy.value,
            "max_pages": request.max_pages,
            "stealth_mode": request.stealth_mode,
            "use_proxy": request.use_proxy,
            "wait_for_selector": request.wait_for_selector,
            "timeout": request.timeout
        },
        priority=5
    )
    
    return {
        "job_id": str(job.id),
        "status": "queued",
        "message": "Scraping job queued. Use GET /api/scrape/{job_id} to check status."
    }


@router.get("/{job_id}")
async def get_scrape_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scrape job status and results.
    
    Returns:
        - status: PENDING, RUNNING, COMPLETED, FAILED
        - result: Scraped data (if completed)
        - error: Error message (if failed)
    """
    # Get job from database
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get queue status
    queue_status = await job_queue.get_status(job_id)
    
    response = {
        "job_id": str(job.id),
        "status": job.status.value,
        "description": job.description,
        "created_at": job.created_at.isoformat() if job.created_at else None
    }
    
    # Add result if completed
    if job.status == DBJobStatus.COMPLETED and job.config:
        response["result"] = job.config.get("result")
    
    # Add error if failed
    if job.status == DBJobStatus.FAILED and job.config:
        response["error"] = job.config.get("result", {}).get("error")
    
    # Add queue info if available
    if queue_status:
        response["queue_info"] = {
            "queue_status": queue_status["status"],
            "retry_count": queue_status["retry_count"],
            "started_at": queue_status["started_at"].isoformat() if queue_status.get("started_at") else None,
            "completed_at": queue_status["completed_at"].isoformat() if queue_status.get("completed_at") else None
        }
    
    return response


@router.get("/strategies")
async def list_strategies():
    """List available scraping strategies"""
    return {
        "strategies": [
            {
                "id": "auto",
                "name": "Auto-Detect",
                "description": "Automatically selects best strategy based on URL"
            },
            {
                "id": "static",
                "name": "Static HTTP",
                "description": "Fast HTTP request, best for simple pages"
            },
            {
                "id": "browser",
                "name": "Browser",
                "description": "Full browser rendering for JS-heavy sites"
            },
            {
                "id": "stealth",
                "name": "Stealth Browser",
                "description": "Browser with anti-bot evasion techniques"
            }
        ]
    }
