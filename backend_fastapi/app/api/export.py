"""
Export API endpoints
"""
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models import Job, DatasetVersion
from app.schemas import ExportRequest, ExportResponse
from app.services.exporter import exporter
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=ExportResponse)
async def export_dataset(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Export a dataset version to Excel/CSV/JSON"""
    try:
        # Get job information
        stmt = select(Job).where(Job.id == request.job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get dataset version
        version_stmt = select(DatasetVersion).where(
            DatasetVersion.job_id == request.job_id
        )

        if request.version:
            version_stmt = version_stmt.where(DatasetVersion.version == request.version)
        else:
            # Get latest version
            version_stmt = version_stmt.order_by(desc(DatasetVersion.version)).limit(1)

        result = await db.execute(version_stmt)
        dataset_version = result.scalar_one_or_none()

        if not dataset_version:
            raise HTTPException(status_code=404, detail="Dataset version not found")

        # Load the actual data (assuming it's stored as JSON file)
        data_path = Path(dataset_version.data_location)
        if not data_path.exists():
            raise HTTPException(status_code=404, detail="Dataset file not found")

        # Read data from file
        import json
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]  # Ensure it's a list

        # Export the data
        export_response = await exporter.export_dataset(
            data=data,
            request=request,
            job_name=job.description.replace(' ', '_').lower()[:30]
        )

        return export_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/download/{filename}")
async def download_export(filename: str):
    """Download an exported file"""
    filepath = Path("exports") / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine content type based on extension
    if filename.endswith('.xlsx'):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith('.csv'):
        media_type = "text/csv"
    elif filename.endswith('.json'):
        media_type = "application/json"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=filepath,
        media_type=media_type,
        filename=filename
    )


@router.get("/jobs/{job_id}/versions")
async def list_exportable_versions(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all versions available for export for a job"""
    stmt = select(DatasetVersion).where(
        DatasetVersion.job_id == job_id
    ).order_by(desc(DatasetVersion.version))

    result = await db.execute(stmt)
    versions = result.scalars().all()

    return [
        {
            "version": v.version,
            "row_count": v.row_count,
            "created_at": v.created_at,
            "has_change_summary": v.change_summary is not None
        }
        for v in versions
    ]


@router.delete("/cleanup")
async def cleanup_exports(max_age_days: int = Query(7, ge=1, le=30)):
    """Clean up old export files (admin function)"""
    try:
        exporter.cleanup_old_exports(max_age_days)
        return {"message": f"Cleaned up exports older than {max_age_days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")