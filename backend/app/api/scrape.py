from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from app.db.session import get_db
from app.db.models import Job, Task, TaskType, TaskStatus, JobConfig
from app.db.models import JobStatus as DBJobStatus
from app.schemas import ScrapeRequest
from app.queue.job_queue import job_queue
from app.scraper.logic.registry import scraper_registry, initialize_scrapers
from app.llm.schema_builder import AISchemaBuilder
from app.core.limits import limits


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
    # Enforce platform limits
    if request.max_pages > limits.MAX_PAGES_PER_URL:
        raise HTTPException(
            status_code=400, 
            detail=f"Max pages exceeded. Platform limit: {limits.MAX_PAGES_PER_URL}"
        )
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
            "timeout": request.timeout,
            "filters": request.filters,
            "debug": request.debug,
            "auto_detect": request.auto_detect
        },
        status=DBJobStatus.CREATED
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
            "timeout": request.timeout,
            "filters": request.filters,
            "debug": request.debug,
            "auto_detect": request.auto_detect
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
    if job.status == DBJobStatus.FAILED_FINAL and job.config:
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
@router.post("/{job_id}/rerun")
async def rerun_job(
    job_id: UUID,
    new_config: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Rerun a job, optionally with a new configuration (e.g. fixed selectors).
    Used in Human-In-The-Loop flow.
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if new_config:
        # Check if config actually changed
        if job.config != new_config:
            # Get latest version
            config_result = await db.execute(
                select(JobConfig)
                .where(JobConfig.job_id == job_id)
                .order_by(JobConfig.version.desc())
                .limit(1)
            )
            latest_config = config_result.scalar_one_or_none()
            new_version = (latest_config.version + 1) if latest_config else 1
            
            # Update job and create new config record
            job.config.update(new_config)
            
            new_job_config = JobConfig(
                job_id=job_id,
                version=new_version,
                config=job.config,
                is_active=1
            )
            db.add(new_job_config)
        
    job.status = DBJobStatus.RERUNNING
    await db.commit()
    
    # Enqueue again
    payload = job.config.copy()
    await job_queue.enqueue(
        job_id=job.id,
        job_type="SCRAPE",
        payload=payload,
        priority=10 # High priority for manual reruns
    )
    
    return {"status": "rerun_queued", "job_id": str(job_id)}


@router.post("/{job_id}/replay")
async def replay_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Developer Superpower: Replay a past job exactly as it was.
    Inherits all original configuration, proxies, and headers.
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Create a new job based on the old one
    new_job = Job(
        description=f"REPLAY: {job.description}",
        schema=job.schema,
        config=job.config.copy() if job.config else {},
        status=DBJobStatus.CREATED
    )
    # Remove previous results/errors from new job config
    if "result" in new_job.config:
        del new_job.config["result"]
    if "error" in new_job.config:
        del new_job.config["error"]
        
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Enqueue with high priority
    await job_queue.enqueue(
        job_id=new_job.id,
        job_type="SCRAPE",
        payload=new_job.config,
        priority=1 # Developer intervention priority
    )
    
    return {
        "job_id": str(new_job.id),
        "status": "replay_queued",
        "parent_job_id": str(job_id)
    }


@router.post("/preflight")
async def preflight_test(
    request: ScrapeRequest
):
    """
    Test selectors on a single page before a full run.
    Returns preview data and confidence breakdown.
    """
    scraper = await scraper_registry.get_scraper(request.url)
    
    # Force max_pages to 1 for preflight
    preflight_result = await scraper.scrape(
        url=request.url,
        schema=request.schema,
        job_id="preflight_" + str(uuid4()),
        strategy=request.strategy.value,
        stealth_mode=request.stealth_mode,
        timeout=request.timeout,
        filters=request.filters,
        prompt=request.prompt
    )
    
    return {
        "success": preflight_result.success,
        "preview_data": preflight_result.data,
        "confidence": preflight_result.confidence,
        "confidence_components": preflight_result.confidence_components,
        "failure_reason": preflight_result.failure_reason,
        "failure_message": preflight_result.failure_message,
        "errors": preflight_result.errors
    }


@router.post("/preview")
async def preview_scrape(
    request: ScrapeRequest
):
    """
    Dry-run extraction to see what data would be picked up.
    Returns preview data and success/missing field report.
    """
    scraper = await scraper_registry.get_scraper(request.url)
    
    # Run a quick fetch (static first)
    preflight_result = await scraper.scrape(
        url=request.url,
        schema=request.schema,
        job_id="preview_" + str(uuid4()),
        strategy="static", # Preview is always fast
        timeout=10,
        temp=True # Flag to not save stats/snapshots
    )
    
    # Use the preview engine for a detailed report
    from app.scraper.intelligence.preview import PreviewEngine
    preview_engine = PreviewEngine()
    
    # Note: GenericScraper already has result.data, but PreviewEngine gives status/missing
    # We could also use scraper.preview_engine if exposed
    
    return preview_engine.preview(preflight_result.metadata.get("html", ""), request.schema)


@router.post("/ai-schema")
async def build_ai_schema(
    prompt: str
):
    """
    AI Superpower: Convert NL into high-quality scraping JSON.
    """
    builder = AISchemaBuilder()
    schema = await builder.build(prompt)
    
    return {
        "prompt": prompt,
        "generated_schema": schema
    }
