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

# ✅ NEW IMPORTS FOR PREVIEW
from app.scraper.engines.static import StaticStrategy
from app.scraper.intelligence.preview import PreviewEngine

router = APIRouter()


# -------------------------------------------------------------------
# CREATE SCRAPE JOB
# -------------------------------------------------------------------
@router.post("/")
async def scrape_url(
    request: ScrapeRequest,
    db: AsyncSession = Depends(get_db)
):
    if request.max_pages > limits.MAX_PAGES_PER_URL:
        raise HTTPException(
            status_code=400,
            detail=f"Max pages exceeded. Platform limit: {limits.MAX_PAGES_PER_URL}",
        )

    urls = request.url_list if request.url_list else ([request.url] if request.url else [])
    if not urls:
        raise HTTPException(status_code=400, detail="No URL(s) provided")

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
        "message": f"Scraping job queued with {len(urls)} tasks.",
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

    tasks_result = await db.execute(select(Task).where(Task.job_id == job.id))
    tasks = tasks_result.scalars().all()

    return {
        "job_id": str(job.id),
        "status": job.status.value,
        "description": job.description,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "tasks": [
            {
                "task_id": str(t.id),
                "url": t.payload.get("url"),
                "status": t.status.value,
                "retry_count": t.retry_count,
                "failure_message": t.failure_message,
                "result": t.result,
            }
            for t in tasks
        ],
    }


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
# PREVIEW (STATIC ONLY – SAFE)
# -------------------------------------------------------------------
@router.post("/preview")
async def preview_scrape(request: ScrapeRequest):
    static = StaticStrategy()

    try:
        _, html, _ = await static.fetch(
            request.url,
            timeout=min(request.timeout or 10, 15),
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Preview fetch failed: {str(e)}",
        )

    # 🔍 DEBUG (TEMP – remove later)
    print("HTML LENGTH:", len(html))
    print("HTML SAMPLE:", html[:300])

    engine = PreviewEngine()
    return engine.preview(html, request.schema)



# -------------------------------------------------------------------
# AI SCHEMA
# -------------------------------------------------------------------
@router.post("/ai-schema")
async def build_ai_schema(prompt: str):
    builder = AISchemaBuilder()
    schema = await builder.build(prompt)
    return {
        "prompt": prompt,
        "generated_schema": schema,
    }
