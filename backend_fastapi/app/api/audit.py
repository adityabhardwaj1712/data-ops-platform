from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
import os
import json

from app.db.session import get_db
from app.db.models import AuditLog, Task, DatasetVersion
from app.schemas import AuditLogResponse, VersionComparisonRequest, VersionDiff
from app.services.change_detector import change_detector


router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    job_id: UUID = None,
    task_id: UUID = None,
    action: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List audit logs with filters"""
    query = select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)
    
    if task_id:
        query = query.where(AuditLog.task_id == task_id)
    
    if action:
        query = query.where(AuditLog.action == action)
    
    if job_id:
        # Need to join with Task to filter by job_id
        query = query.join(Task).where(Task.job_id == job_id)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(log_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific audit log entry"""
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return log


@router.get("/actions/list")
async def list_action_types(db: AsyncSession = Depends(get_db)):
    """List all unique action types in audit logs"""
    result = await db.execute(
        select(AuditLog.action).distinct()
    )
    actions = [row[0] for row in result.all()]
    return {"actions": actions}


@router.post("/versions/compare", response_model=VersionDiff)
async def compare_dataset_versions(
    request: VersionComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """Compare two dataset versions to detect changes"""
    try:
        # Get the versions to compare
        stmt = select(DatasetVersion).where(DatasetVersion.job_id == request.job_id)

        if request.from_version:
            stmt = stmt.where(DatasetVersion.version == request.from_version)
        else:
            # Get latest two versions
            stmt = stmt.order_by(DatasetVersion.version.desc()).limit(2)

        if request.to_version:
            # If specific versions requested, get both
            versions = []
            for version_num in [request.from_version, request.to_version]:
                if version_num:
                    v_stmt = select(DatasetVersion).where(
                        DatasetVersion.job_id == request.job_id,
                        DatasetVersion.version == version_num
                    )
                    result = await db.execute(v_stmt)
                    version = result.scalar_one_or_none()
                    if version:
                        versions.append(version)
            
            # Ensure versions are sorted by version number (older first, newer second)
            versions.sort(key=lambda v: v.version)
        else:
            result = await db.execute(stmt)
            versions = result.scalars().all()
            # Versions are already sorted descending from query, but we need older first
            versions = list(reversed(versions))

        if len(versions) < 2:
            raise HTTPException(status_code=404, detail="Need at least two versions to compare")

        # Load the data from both versions
        # After sorting, versions[0] is always older, versions[1] is always newer
        old_version = versions[0]  # Older version
        new_version = versions[1]  # Newer version

        # Read data from files
        old_data = []
        new_data = []

        if old_version.data_location and os.path.exists(old_version.data_location):
            with open(old_version.data_location, 'r', encoding='utf-8') as f:
                old_data = json.load(f)

        if new_version.data_location and os.path.exists(new_version.data_location):
            with open(new_version.data_location, 'r', encoding='utf-8') as f:
                new_data = json.load(f)

        # Compare the datasets
        diff = change_detector.compare_datasets(
            old_data=old_data,
            new_data=new_data
        )

        # Update version numbers in diff
        diff.from_version = old_version.version
        diff.to_version = new_version.version

        return diff

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Version comparison failed: {str(e)}")


@router.get("/versions/{job_id}/{version}/changes")
async def get_version_changes(
    job_id: UUID,
    version: int,
    db: AsyncSession = Depends(get_db)
):
    """Get the change summary for a specific version"""
    stmt = select(DatasetVersion).where(
        DatasetVersion.job_id == job_id,
        DatasetVersion.version == version
    )

    result = await db.execute(stmt)
    dataset_version = result.scalar_one_or_none()

    if not dataset_version:
        raise HTTPException(status_code=404, detail="Version not found")

    if not dataset_version.change_summary:
        return {"message": "No change summary available for this version"}

    return dataset_version.change_summary
