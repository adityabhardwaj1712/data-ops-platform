"""
Search API endpoints
Full-text search across platform
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.services.search import search_service

router = APIRouter()


@router.get("/jobs")
async def search_jobs(
    q: str = Query(..., min_length=1, description="Search query"),
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search jobs"""
    return await search_service.search_jobs(db, q, status=status, limit=limit)


@router.get("/tasks")
async def search_tasks(
    q: str = Query(..., min_length=1, description="Search query"),
    job_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Search tasks"""
    return await search_service.search_tasks(db, q, job_id=job_id, limit=limit)


@router.get("/datasets")
async def search_datasets(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search datasets"""
    return await search_service.search_datasets(db, q, limit=limit)


@router.get("/global")
async def global_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Global search across all entities"""
    return await search_service.global_search(db, q, limit=limit)
