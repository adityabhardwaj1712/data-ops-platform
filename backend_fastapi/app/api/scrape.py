from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.session import get_db
from app.db.models import Job, Task, AuditLog, TaskType, TaskStatus
from app.db.models import JobStatus as DBJobStatus
from app.schemas import ScrapeRequest, ScrapeResult
from app.scraper.engine import ScraperEngine
from app.services.router import route_task


router = APIRouter()


@router.post("/", response_model=ScrapeResult)
async def scrape_url(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a scraping operation.
    Can be run standalone or as part of a job.
    """
    engine = ScraperEngine()
    
    result = await engine.scrape(
        url=request.url,
        schema=request.schema,
        prompt=request.prompt,
        strategy=request.strategy.value,
        max_pages=request.max_pages,
        stealth_mode=request.stealth_mode,
        use_proxy=request.use_proxy,
        wait_for_selector=request.wait_for_selector,
        timeout=request.timeout
    )
    
    return result


@router.post("/job/{job_id}", response_model=ScrapeResult)
async def scrape_for_job(
    job_id: UUID,
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute scraping as part of a job pipeline.
    Creates a task and runs through the full workflow.
    """
    # Get job
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update job status
    job.status = DBJobStatus.RUNNING
    await db.commit()
    
    # Create scrape task
    task = Task(
        job_id=job_id,
        type=TaskType.SCRAPE,
        payload={
            "url": request.url,
            "prompt": request.prompt,
            "strategy": request.strategy.value,
            "max_pages": request.max_pages,
            "stealth_mode": request.stealth_mode
        }
    )
    task.status = TaskStatus.RUNNING
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Execute scraping
    engine = ScraperEngine()
    scrape_result = await engine.scrape(
        url=request.url,
        schema=job.schema,
        prompt=request.prompt,
        strategy=request.strategy.value,
        max_pages=request.max_pages,
        stealth_mode=request.stealth_mode,
        use_proxy=request.use_proxy,
        wait_for_selector=request.wait_for_selector,
        timeout=request.timeout
    )
    
    # Update task with result
    task.result = scrape_result.data
    task.confidence = scrape_result.confidence
    task.status = TaskStatus.COMPLETED if scrape_result.success else TaskStatus.FAILED
    
    # Create audit log
    audit = AuditLog(
        task_id=task.id,
        action="scrape_completed" if scrape_result.success else "scrape_failed",
        changes={"url": request.url, "strategy": scrape_result.strategy_used}
    )
    db.add(audit)
    await db.commit()
    
    # Route to next task in pipeline (background)
    background_tasks.add_task(route_task, task.id, db)
    
    return scrape_result


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
