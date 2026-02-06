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
    JobStatus as DBJobStatus,
)
from app.schemas import ScrapeRequest
from app.scraper.logic.registry import scraper_registry
from app.llm.schema_builder import AISchemaBuilder
from app.core.limits import limits

# Preview (STATIC ONLY)
from app.scraper.engines.static import StaticStrategy
from app.scraper.intelligence.preview import PreviewEngine

router = APIRouter()

# =====================================================
# CREATE SCRAPE JOB (NO SLASH BUG — FIXED)
# =====================================================
@router.post("", summary="Create scrape job")
@router.post("/", include_in_schema=False)
async def scrape_url(
    request: ScrapeRequest,
    db: AsyncSession = Depends(get_db),
):
    if request.max_pages > limits.MAX_PAGES_PER_URL:
        raise HTTPException(
            status_code=400,
            detail=f"Max pages exceeded. Platform limit: {limits.MAX_PAGES_PER_URL}",
        )

    urls = (
        request.url_list
        if request.url_list
        else ([request.url] if request.url else [])
    )

    if not urls:
        raise HTTPException(status_code=400, detail="No URL(s) provided")

    job = Job(
        description=f"Scrape {len(urls)} URL(s)",
        schema=request.extract_schema,
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

    # Create tasks
    for url in urls:
        payload = job.config.copy()
        payload["url"] = url

        task = Task(
            job_id=job.id,
            type=TaskType.SCRAPE,
            payload=payload,
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

# =====================================================
# GET JOB STATUS
# =====================================================
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

# =====================================================
# RERUN JOB
# =====================================================
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

    payload = job.config.copy()
    if new_config:
        payload.update(new_config)

    task = Task(
        job_id=job.id,
        type=TaskType.SCRAPE,
        payload=payload,
        status=TaskStatus.PENDING,
    )

    db.add(task)
    await db.commit()

    return {"status": "rerun_queued", "job_id": str(job_id)}

# =====================================================
# PREFLIGHT (USES REAL STRATEGY, SAFE)
# =====================================================
@router.post("/preflight")
async def preflight_test(request: ScrapeRequest):
    scraper = await scraper_registry.get_scraper(request.url)

    result = await scraper.scrape(
        url=request.url,
        schema=request.extract_schema,
        job_id="preflight_" + str(uuid4()),
        timeout=request.timeout,
        stealth_mode=request.stealth_mode,
        wait_for_selector=request.wait_for_selector,
        filters=request.filters,
        prompt=request.prompt,
    )

    return {
        "success": result.success,
        "preview_data": result.data,
        "confidence": result.confidence,
        "failure_reason": result.failure_reason,
        "failure_message": result.failure_message,
        "errors": result.errors,
    }

# =====================================================
# PREVIEW (STATIC ONLY – SAFE & FAST)
# =====================================================
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

    engine = PreviewEngine()
    return engine.preview(html, request.schema)

# =====================================================
# AI SCHEMA BUILDER
# =====================================================
@router.post("/ai-schema")
async def build_ai_schema(prompt: str):
    builder = AISchemaBuilder()
    schema = await builder.build(prompt)
    return {
        "prompt": prompt,
        "generated_schema": schema,
    }

# =====================================================
# API SCRAPING
# =====================================================
@router.post("/api-scrape")
async def scrape_api(
    api_url: str,
    extract_schema: Dict[str, str],
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    max_pages: int = 1
):
    """
    Direct API scraping endpoint for JSON endpoints
    """
    from app.scraper.engines.api_scraper import APIScraper
    
    scraper = APIScraper()
    result = await scraper.scrape(
        url=api_url,
        schema=extract_schema,
        job_id="api_" + str(uuid4()),
        headers=headers,
        params=params,
        max_pages=max_pages
    )
    
    return {
        "success": result.success,
        "data": result.data,
        "pages_scraped": result.pages_scraped,
        "confidence": result.confidence,
        "metadata": result.metadata
    }

# =====================================================
# MULTI-PAGE CRAWLING
# =====================================================
@router.post("/crawl")
async def start_crawl(
    start_url: str,
    extract_schema: Dict[str, str],
    max_depth: int = 2,
    max_pages: int = 50,
    follow_external_links: bool = False,
    url_patterns: Optional[List[str]] = None
):
    """
    Multi-page crawling endpoint
    """
    from app.scraper.engines.crawler import CrawlerScraper
    from app.schemas import CrawlConfig
    
    crawl_config = CrawlConfig(
        max_depth=max_depth,
        max_pages=max_pages,
        follow_external_links=follow_external_links,
        url_patterns=url_patterns
    )
    
    scraper = CrawlerScraper()
    result = await scraper.crawl(start_url, crawl_config, extract_schema)
    
    return {
        "success": result.success,
        "data": result.data,
        "pages_crawled": result.pages_scraped,
        "metadata": result.metadata
    }

# =====================================================
# DOCUMENT EXTRACTION
# =====================================================
@router.post("/document-extract")
async def extract_document(
    document_url: str,
    extract_tables: bool = True,
    extract_text: bool = True,
    page_range: Optional[str] = None
):
    """
    PDF/Excel/CSV extraction endpoint
    """
    from app.scraper.engines.document_scraper import DocumentScraper
    from app.schemas import DocumentConfig
    
    doc_config = DocumentConfig(
        extract_tables=extract_tables,
        extract_text=extract_text,
        page_range=page_range
    )
    
    scraper = DocumentScraper()
    result = await scraper.extract(document_url, extract_tables, extract_text)
    
    return {
        "success": result.success,
        "data": result.data,
        "metadata": result.metadata
    }

# =====================================================
# REAL-TIME STREAMING
# =====================================================
@router.post("/streaming/start")
async def start_streaming(
    url: str,
    extract_schema: Dict[str, str],
    poll_interval_seconds: int = 60,
    max_duration_minutes: int = 60,
    change_threshold: float = 0.1,
    webhook_url: Optional[str] = None
):
    """
    Start real-time monitoring
    """
    from app.scraper.engines.streaming_scraper import StreamingScraper
    from app.schemas import StreamingConfig
    
    streaming_config = StreamingConfig(
        poll_interval_seconds=poll_interval_seconds,
        max_duration_minutes=max_duration_minutes,
        change_threshold=change_threshold,
        webhook_url=webhook_url
    )
    
    scraper = StreamingScraper()
    job_id = await scraper.start_monitoring(url, streaming_config, extract_schema)
    
    return {
        "job_id": job_id,
        "status": "monitoring_started",
        "config": {
            "poll_interval": poll_interval_seconds,
            "max_duration": max_duration_minutes
        }
    }

@router.post("/streaming/{job_id}/stop")
async def stop_streaming(job_id: UUID):
    """
    Stop real-time monitoring
    """
    from app.scraper.engines.streaming_scraper import StreamingScraper
    
    await StreamingScraper.stop_monitoring(str(job_id))
    return {"status": "stopped", "job_id": str(job_id)}

@router.get("/streaming/{job_id}/status")
async def get_streaming_status(job_id: UUID):
    """
    Get status of streaming job
    """
    from app.scraper.engines.streaming_scraper import StreamingScraper
    
    status = StreamingScraper.get_job_status(str(job_id))
    
    if not status:
        raise HTTPException(status_code=404, detail="Streaming job not found")
    
    return {
        "job_id": str(job_id),
        "status": status.get("status"),
        "check_count": status.get("check_count"),
        "changes_detected": status.get("changes_detected"),
        "last_check": status.get("last_check").isoformat() if status.get("last_check") else None
    }
