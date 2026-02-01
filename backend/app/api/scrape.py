from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from app.db.session import get_db
from app.db.models import (
    Job,
    Task,
    TaskType,
    TaskStatus,
    JobConfig,
    JobStatus as DBJobStatus,
)
from app.schemas import ScrapeRequest
from app.scraper.logic.registry import scraper_registry
from app.llm.schema_builder import AISchemaBuilder
from app.core.limits import limits

router = APIRouter()


# -------------------------------------------------------------------
# CREATE SCRAPE JOB
# -------------------------------------------------------------------
@router.post("/")
async def scrape_url(
    request: ScrapeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a scraping job (async execution).
    Worker will pick it from DB.
    """

    if request.max_pages > limits.MAX_PAGES_PER_URL:
        raise HTTPException(
            status_code=400,
            detail=f"Max pages exceeded. Platform limit: {limits.MAX_PAGES_PER_URL}",
        )

    urls = request.url_list if request.url_list else ([request.url] if request.url else [])
    if not urls:
        raise HTTPException(status_code=400, detail="No URL(s) provided")

    # Create Job
    job = Job(
        description=f"Scrape {len(urls)} URL(s)",
        schema=request.schema,
        config={
            "urls": urls,
            "prompt": request.prompt,
            "strategy": request.strategy.value,
            "max_pages": request.max_pages,
            "stealth_mode": request.stealth_mode,
            "use_proxy": request.use_proxy,
            "wait_for_selector": request.wait_for_selector,
            "timeout": request.timeout,
            "filters": request.filters,
            "debug": request.debug,
            "auto_detect": request.auto_detect,
        },
        status=DBJobStatus.CREATED,
        sla_seconds=request.sla_seconds,
        webhook_url=request.webhook_url,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Create Tasks (ONE PER URL)
    for url in urls:
        task_payload = job.config.copy()
        task_payload["url"] = url
        task = Task(
            job_id=job.id,
            type=TaskType.SCRAPE,
            payload=task_payload,
            status=TaskStatus.PENDING,
            is_seed=1,
        )
        db.add(task)
    
    await db.commit()

    return {
        "job_id": str(job.id),
        "status": "queued",
        "url_count": len(urls),
        "message": f"Scraping job queued with {len(urls)} tasks. Use GET /api/scrape/{{job_id}} to check status.",
    }


# -------------------------------------------------------------------
# GET JOB STATUS
# -------------------------------------------------------------------
@router.get("/{job_id}")
async def get_scrape_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": str(job.id),
        "status": job.status.value,
        "description": job.description,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }

    # Attach result if available
    if job.config:
        if job.status == DBJobStatus.COMPLETED:
            response["result"] = job.config.get("result")
        if job.status == DBJobStatus.FAILED_FINAL:
            response["error"] = job.config.get("error")

    # Tasks info
    tasks_result = await db.execute(
        select(Task).where(Task.job_id == job.id)
    )
    tasks = tasks_result.scalars().all()
    
    response["tasks"] = [
        {
            "task_id": str(t.id),
            "url": t.payload.get("url"),
            "status": t.status.value,
            "retry_count": t.retry_count,
            "failure_message": t.failure_message,
            "result": t.result
        }
        for t in tasks
    ]

    # Consolidated results if completed
    if job.status == DBJobStatus.COMPLETED or job.status == DBJobStatus.FAILED_FINAL:
        results = [t.result for t in tasks if t.result]
        response["result"] = results if len(results) > 1 else (results[0] if results else None)

    return response


# -------------------------------------------------------------------
# RERUN JOB
# -------------------------------------------------------------------
@router.post("/{job_id}/rerun")
async def rerun_job(
    job_id: UUID,
    new_config: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if new_config and job.config != new_config:
        cfg_result = await db.execute(
            select(JobConfig)
            .where(JobConfig.job_id == job_id)
            .order_by(JobConfig.version.desc())
            .limit(1)
        )
        latest = cfg_result.scalar_one_or_none()
        version = (latest.version + 1) if latest else 1

        job.config.update(new_config)
        db.add(
            JobConfig(
                job_id=job_id,
                version=version,
                config=job.config,
                is_active=1,
            )
        )

    job.status = DBJobStatus.RERUNNING

    task = Task(
        job_id=job.id,
        type=TaskType.SCRAPE,
        payload=job.config,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    await db.commit()

    return {"status": "rerun_queued", "job_id": str(job_id)}


# -------------------------------------------------------------------
# REPLAY JOB
# -------------------------------------------------------------------
@router.post("/{job_id}/replay")
async def replay_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    new_job = Job(
        description=f"REPLAY: {job.description}",
        schema=job.schema,
        config=job.config.copy() if job.config else {},
        status=DBJobStatus.CREATED,
    )
    new_job.config.pop("result", None)
    new_job.config.pop("error", None)

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    task = Task(
        job_id=new_job.id,
        type=TaskType.SCRAPE,
        payload=new_job.config,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    await db.commit()

    return {
        "job_id": str(new_job.id),
        "status": "replay_queued",
        "parent_job_id": str(job_id),
    }


# -------------------------------------------------------------------
# PREFLIGHT
# -------------------------------------------------------------------
@router.post("/preflight")
async def preflight_test(request: ScrapeRequest):
    scraper = await scraper_registry.get_scraper(request.url)

    result = await scraper.scrape(
        url=request.url,
        schema=request.schema,
        job_id="preflight_" + str(uuid4()),
        strategy=request.strategy.value,
        stealth_mode=request.stealth_mode,
        timeout=request.timeout,
        filters=request.filters,
        prompt=request.prompt,
    )

    return {
        "success": result.success,
        "preview_data": result.data,
        "confidence": result.confidence,
        "confidence_components": result.confidence_components,
        "failure_reason": result.failure_reason,
        "failure_message": result.failure_message,
        "errors": result.errors,
    }


# -------------------------------------------------------------------
# PREVIEW
# -------------------------------------------------------------------
@router.post("/preview")
async def preview_scrape(request: ScrapeRequest):
    scraper = await scraper_registry.get_scraper(request.url)

    result = await scraper.scrape(
        url=request.url,
        schema=request.schema,
        job_id="preview_" + str(uuid4()),
        strategy="static",
        timeout=10,
        temp=True,
    )

    from app.scraper.intelligence.preview import PreviewEngine

    engine = PreviewEngine()
    return engine.preview(
        result.metadata.get("html", ""),
        request.schema,
    )


# -------------------------------------------------------------------
# AI SCHEMA
# -------------------------------------------------------------------
@router.post("/ai-schema")
async def build_ai_schema(prompt: str):
    builder = AISchemaBuilder()
    schema = await builder.build(prompt)
    return {"prompt": prompt, "generated_schema": schema}
