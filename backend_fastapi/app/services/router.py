"""
Task Router - Orchestrates task pipeline flow
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import json
import os
from datetime import datetime

from app.db.models import Task, Job, DatasetVersion, AuditLog, TaskType, TaskStatus
from app.db.models import JobStatus as DBJobStatus


MAX_RETRIES = 3


async def route_task(task_id: UUID, db: AsyncSession):
    """
    Routes a completed task to the next step in the pipeline.
    
    Pipeline Flow:
    SCRAPE → QUALITY → (if failed) VERIFY → QUALITY
                    → (if blocked) HUMAN → QUALITY
                    → (if passed) Dataset Version Created
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        return
    
    # Get job
    job_result = await db.execute(select(Job).where(Job.id == task.job_id))
    job = job_result.scalar_one_or_none()
    
    # Global retry guard
    if task.retry_count >= MAX_RETRIES:
        job.status = DBJobStatus.FAILED
        await db.commit()
        return
    
    # SCRAPE completed
    if task.type == TaskType.SCRAPE:
        if task.status == TaskStatus.COMPLETED:
            # Create quality check task
            quality_task = Task(
                job_id=task.job_id,
                type=TaskType.QUALITY,
                payload=task.result or {}
            )
            db.add(quality_task)
            await db.commit()
            
            # Run quality check
            from app.services.quality import run_quality_check
            await run_quality_check(quality_task.id, db)
            
        elif task.status == TaskStatus.BLOCKED:
            # Create human review task
            human_task = Task(
                job_id=task.job_id,
                type=TaskType.HUMAN,
                payload={
                    "original_payload": task.payload,
                    "current_data": task.result,
                    "reason": "Scraping blocked - requires human intervention"
                }
            )
            db.add(human_task)
            await db.commit()
    
    # HUMAN completed
    elif task.type == TaskType.HUMAN and task.status == TaskStatus.COMPLETED:
        # Create quality check task
        quality_task = Task(
            job_id=task.job_id,
            type=TaskType.QUALITY,
            payload=task.result or {}
        )
        db.add(quality_task)
        await db.commit()
        
        from app.services.quality import run_quality_check
        await run_quality_check(quality_task.id, db)
    
    # QUALITY check result
    elif task.type == TaskType.QUALITY:
        if task.status == TaskStatus.FAILED:
            # Create verify/retry task
            verify_task = Task(
                job_id=task.job_id,
                type=TaskType.VERIFY,
                payload=task.payload,
                retry_count=task.retry_count + 1
            )
            db.add(verify_task)
            await db.commit()
            
        elif task.status == TaskStatus.COMPLETED:
            # Success! Create dataset version
            job.status = DBJobStatus.COMPLETED
            
            # Get latest version number
            versions_result = await db.execute(
                select(DatasetVersion)
                .where(DatasetVersion.job_id == task.job_id)
                .order_by(DatasetVersion.version.desc())
            )
            versions = versions_result.scalars().all()
            latest_version = versions[0].version if versions else 0
            new_version = latest_version + 1
            
            # Save to file
            base_path = os.path.join(os.getcwd(), "data", "versions")
            os.makedirs(base_path, exist_ok=True)
            
            file_path = os.path.join(base_path, f"job_{task.job_id}_v{new_version}.json")
            with open(file_path, "w") as f:
                json.dump(task.result.get("validated_data", task.result), f, indent=2)
            
            # Create version record
            dataset_version = DatasetVersion(
                job_id=task.job_id,
                version=new_version,
                data_location=file_path,
                row_count=1,
                confidence_summary={"avg_confidence": task.confidence or 1.0}
            )
            db.add(dataset_version)
            
            # Audit log
            audit = AuditLog(
                task_id=task.id,
                action="dataset_version_created",
                changes={"version": new_version, "location": file_path}
            )
            db.add(audit)
            
            await db.commit()
