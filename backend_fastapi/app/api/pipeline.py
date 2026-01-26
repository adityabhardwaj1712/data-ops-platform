from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.db.models import Job, Task, AuditLog, TaskType, TaskStatus
from app.db.models import JobStatus as DBJobStatus
from app.scraper.layers import ScraperPipeline, ExtractionMode
from app.services.router import route_task
from app.core.limits import limits, validate_job_request


router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# SCHEMAS FOR 5-LAYER PIPELINE
# ═══════════════════════════════════════════════════════════════════

class PipelineRequest(BaseModel):
    """Request for 5-layer scraping pipeline"""
    what_i_want: str = Field(..., description="Natural language description of what to extract")
    from_where: List[str] = Field(..., description="List of URLs to scrape")
    schema: Dict[str, Any] = Field(..., description="Expected data schema")
    extraction_mode: str = Field(default="heuristic", description="heuristic or ai")
    max_pages_per_source: int = Field(default=5, ge=1, le=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "what_i_want": "DevOps fresher jobs in India",
                "from_where": [
                    "https://example.com/jobs",
                    "https://anothersite.com/careers"
                ],
                "schema": {
                    "title": "str",
                    "company": "str",
                    "location": "str",
                    "salary": "str"
                },
                "extraction_mode": "heuristic",
                "max_pages_per_source": 5
            }
        }


class PipelineResponse(BaseModel):
    """Response from 5-layer pipeline"""
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

@router.post("/", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest):
    """
    Run the 5-layer scraping pipeline.
    
    This is the main entry point for intelligent scraping.
    
    Layers:
    1. Source Manager - Handles multiple URLs + pagination
    2. Fetch Engine - Gets HTML (no parsing)
    3. Content Cleaner - Removes noise, gets clean markdown
    4. Intent Extractor - Extracts data based on natural language intent
    5. Trust Engine - Validates + sends to HITL if needed
    
    Modes:
    - heuristic: FREE, no AI, uses pattern matching
    - ai: Uses LLM for extraction (requires Ollama)
    """
    # Validate request against platform limits
    is_valid, error = validate_job_request(request.from_where, request.max_pages_per_source)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
        
    pipeline = ScraperPipeline()
    
    # Map string to enum
    mode = ExtractionMode.AI_ASSISTED if request.extraction_mode == "ai" else ExtractionMode.HEURISTIC
    
    result = await pipeline.run(
        what_i_want=request.what_i_want,
        from_where=request.from_where,
        schema=request.schema,
        extraction_mode=mode,
        max_pages_per_source=request.max_pages_per_source
    )
    
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


@router.post("/with-job", response_model=PipelineResponse)
async def run_pipeline_with_job(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Run pipeline and create a Job for tracking.
    
    This creates a full audit trail and enables:
    - Dataset versioning
    - HITL review if confidence is low
    - Quality validation
    """
    # Create job
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
    
    # Run pipeline
    pipeline = ScraperPipeline()
    mode = ExtractionMode.AI_ASSISTED if request.extraction_mode == "ai" else ExtractionMode.HEURISTIC
    
    result = await pipeline.run(
        what_i_want=request.what_i_want,
        from_where=request.from_where,
        schema=request.schema,
        extraction_mode=mode,
        max_pages_per_source=request.max_pages_per_source
    )
    
    # Create tasks based on confidence action
    for item_data in result.data:
        confidence = item_data.pop("_confidence", result.total_confidence)
        source_url = item_data.pop("_source_url", "")
        
        task_type = TaskType.QUALITY
        reason = None
        
        if result.confidence_action == "mandatory_review":
            task_type = TaskType.HUMAN
            reason = f"Low confidence ({confidence:.0%})"
        elif result.confidence_action == "optional_review":
            # Still quality, but maybe flag for review
            reason = "Optional human review recommended"
        
        task = Task(
            job_id=job.id,
            type=task_type,
            payload={
                **item_data,
                "_source_url": source_url,
                "_reason": reason
            },
            confidence=confidence,
            status=TaskStatus.PENDING
        )
        db.add(task)
    
    # Update job status
    if result.success:
        job.status = DBJobStatus.RUNNING  # Will be marked complete after quality checks
    else:
        job.status = DBJobStatus.FAILED
    
    # Audit log
    audit = AuditLog(
        task_id=task.id if result.data else None,
        action="pipeline_completed",
        changes={
            "sources_processed": result.sources_processed,
            "items_extracted": len(result.data),
            "mode": request.extraction_mode
        }
    )
    if result.data:
        db.add(audit)
    
    await db.commit()
    
    # Route tasks to quality/HITL in background
    for task in await db.execute(select(Task).where(Task.job_id == job.id)):
        background_tasks.add_task(route_task, task[0].id, db)
    
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
    """List available extraction modes"""
    return {
        "modes": [
            {
                "id": "heuristic",
                "name": "Heuristic (FREE)",
                "description": "Uses pattern matching - no AI required, works offline"
            },
            {
                "id": "ai",
                "name": "AI-Assisted",
                "description": "Uses LLM for intelligent extraction - requires Ollama"
            }
        ]
    }
