"""
Backup & Restore API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.services.backup import backup_service

router = APIRouter()


@router.post("/create/{job_id}")
async def create_backup(
    job_id: UUID,
    include_data: bool = Query(True, description="Include dataset files"),
    db: AsyncSession = Depends(get_db)
):
    """Create a backup of a job"""
    try:
        return await backup_service.create_backup(db, job_id, include_data=include_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.get("/list")
async def list_backups():
    """List all available backups"""
    return await backup_service.list_backups()


@router.post("/restore")
async def restore_backup(
    backup_file: str = Query(..., description="Path to backup file"),
    db: AsyncSession = Depends(get_db)
):
    """Restore a backup"""
    try:
        return await backup_service.restore_backup(db, backup_file)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")
