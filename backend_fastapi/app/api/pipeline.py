from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.db.models import Job, Task, AuditLog, TaskType, TaskStatus
from app.db.models import JobStatus as DBJobStatus
from app.services.router import route_task
from app.core.limits import limits, validate_job_request

router = APIRouter()

# ═══════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class PipelineRequest(BaseModel):
    what_i_want: str
    from_where: List[str]
    schema: Dict[str, Any]
    extraction_mode: str = "heuristic"
    max_pages_per_source: int = Field(default=5, ge=1, le=50)


class PipelineResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    sources_processed: int
    sources_successful: int
    average_confidence: float
    confidence_action: str
    cleaning_stats: Dict[str, Any]
    extraction_stats: Dict[str, Any]
    errors: List[str]


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@router.post("/run")
async def run_pipeline(
    request: PipelineRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    CORRECT PATH (PRODUCTION):
    API only creates a job and queues it.
    Worker executes scraper + Playwright.
    """

    is_valid, error = validate_job_request(
        request.from_where,
        request.max_pages_per_source
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    job = Job(
        description=request.what_i_want,
        schema=request.schema,
        config={
            "urls": request.from_where,
            "extraction_mode": request.extraction_mode,
            "max_pages": request.max_pages_per_source
        },
        status=DBJobStatus.PENDING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Lazy import – queue only (NO scraper code)
    from app.queue.job_queue import job_queue

    await job_queue.enqueue(
        job_id=job.id,
        job_type="PIPELINE",
        payload={
            "what_i_want": request.what_i_want,
            "from_where": request.from_where,
            "schema": request.schema,
            "extraction_mode": request.extraction_mode,
            "max_pages_per_source": request.max_pages_per_source
        },
        priority=3
    )

    return {
        "job_id": str(job.id),
        "status": "queued",
        "message": "Pipeline job queued for worker execution",
        "sources": len(request.from_where),
        "extraction_mode": request.extraction_mode
    }


@router.post("/with-job", response_model=PipelineResponse)
async def run_pipeline_with_job(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    DEV / INTERNAL USE ONLY:
    Runs pipeline inside API process.
    This REQUIRES scraper dependencies installed.
    """

    # 🔥 LAZY IMPORT — prevents API startup crash
    from app.scraper.layers import ScraperPipeline, ExtractionMode

    job = Job(
        description=request.what_i_want,
        schema=request.schema,
        config={
            "urls": request.from_where,
            "extraction_mode": request.extraction_mode,
            "max_pages": request.max_pages_per_source
        },
        status=DBJobStatus.RUNNING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    pipeline = ScraperPipeline()
    mode = (
        ExtractionMode.AI_ASSISTED
        if request.extraction_mode == "ai"
        else ExtractionMode.HEURISTIC
    )

    result = await pipeline.run(
        what_i_want=request.what_i_want,
        from_where=request.from_where,
        schema=request.schema,
        extraction_mode=mode,
        max_pages_per_source=request.max_pages_per_source
    )

    for item_data in result.data:
        confidence = item_data.pop("_confidence", result.total_confidence)
        source_url = item_data.pop("_source_url", "")

        task = Task(
            job_id=job.id,
            type=TaskType.QUALITY,
            payload={
                **item_data,
                "_source_url": source_url
            },
            confidence=confidence,
            status=TaskStatus.PENDING
        )
        db.add(task)

    job.status = (
        DBJobStatus.RUNNING if result.success else DBJobStatus.FAILED
    )

    await db.commit()

    return PipelineResponse(
        success=result.success,
        data=result.data,
        sources_processed=result.sources_processed,
        sources_successful=result.sources_successful,
        average_confidence=round(result.total_confidence, 2),
        confidence_action=result.confidence_action,
        cleaning_stats=result.cleaning_stats,
        extraction_stats=result.extraction_stats,
        errors=result.errors
    )


@router.get("/modes")
async def list_extraction_modes():
    return {
        "modes": [
            {
                "id": "heuristic",
                "name": "Heuristic (FREE)",
                "description": "Pattern-based extraction, no AI"
            },
            {
                "id": "ai",
                "name": "AI-Assisted",
                "description": "LLM-based extraction (requires Ollama)"
            }
        ]
    }

