"""
Intent Templates API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import IntentTemplate
from app.schemas import (
    IntentTemplateCreate,
    IntentTemplateResponse,
    IntentTemplateApply
)

router = APIRouter()


@router.post("/", response_model=IntentTemplateResponse)
async def create_template(
    template: IntentTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new intent template"""
    # Check if template name already exists
    stmt = select(IntentTemplate).where(IntentTemplate.name == template.name)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")

    db_template = IntentTemplate(
        name=template.name,
        intent_type=template.intent_type,
        description=template.description,
        template_schema=template.template_schema,
        filters=template.filters
    )

    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)

    # Let FastAPI + Pydantic handle ORM conversion via from_attributes
    return db_template


@router.get("/", response_model=List[IntentTemplateResponse])
async def list_templates(
    intent_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all intent templates, optionally filtered by type"""
    stmt = select(IntentTemplate)
    if intent_type:
        stmt = stmt.where(IntentTemplate.intent_type == intent_type)

    result = await db.execute(stmt)
    templates = result.scalars().all()

    return templates


@router.get("/{template_id}", response_model=IntentTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific intent template"""
    stmt = select(IntentTemplate).where(IntentTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an intent template"""
    stmt = select(IntentTemplate).where(IntentTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.delete(template)
    await db.commit()

    return {"message": "Template deleted successfully"}


@router.post("/apply")
async def apply_template(
    request: IntentTemplateApply,
    db: AsyncSession = Depends(get_db)
):
    """
    Apply an intent template to create a job

    This endpoint converts a template + filters into a job configuration
    that can be executed by the pipeline.
    """
    # Get the template
    stmt = select(IntentTemplate).where(IntentTemplate.id == request.template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Merge template filters with request filters
    filters = template.filters or {}
    if request.filters:
        filters.update(request.filters)

    # Create job description from template
    job_description = f"{template.intent_type}: {template.description}"
    if filters:
        job_description += f" (filters: {filters})"

    # Convert template to job schema
    job_config = {
        "template_id": str(request.template_id),
        "intent_type": template.intent_type,
        "filters": filters,
        "sources": request.sources,
        "max_pages_per_source": request.max_pages_per_source,
        "schema": template.template_schema
    }

    return {
        "job_description": job_description,
        "schema": template.template_schema,
        "config": job_config,
        "ready_to_execute": True
    }