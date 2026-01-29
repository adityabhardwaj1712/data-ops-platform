from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.session import get_db
from app.db.models import Task, AuditLog, TaskType, TaskStatus
from app.schemas import HITLTaskResponse, HITLSubmit
from app.services.router import route_task


router = APIRouter()


@router.get("/pending", response_model=HITLTaskResponse)
async def get_pending_task(db: AsyncSession = Depends(get_db)):
    MAX_ACTIVE_HITL_TASKS = 2  # Hard limit per Sprint 13 spec (Task 102)

    # 1. Check current load (Task 102)
    active_tasks = await db.execute(
        select(Task)
        .where(Task.type == TaskType.HUMAN)
        .where(Task.status == TaskStatus.RUNNING)
    )
    if len(active_tasks.scalars().all()) >= MAX_ACTIVE_HITL_TASKS:
        # Operator overloaded. Don't assign new work.
        raise HTTPException(status_code=429, detail="Too many active review tasks. Finish existing ones first.")

    result = await db.execute(
        select(Task)
        .where(Task.type == TaskType.HUMAN)
        .where(Task.status == TaskStatus.PENDING)
        .order_by(Task.created_at.asc())
        .limit(1)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="No pending tasks")
    
    # Mark as running
    task.status = TaskStatus.RUNNING
    await db.commit()
    
    return HITLTaskResponse(
        task_id=task.id,
        job_id=task.job_id,
        payload=task.payload,
        current_data=task.payload.get("current_data")
    )


@router.get("/queue")
async def get_queue_stats(db: AsyncSession = Depends(get_db)):
    """Get HITL queue statistics"""
    pending = await db.execute(
        select(Task)
        .where(Task.type == TaskType.HUMAN)
        .where(Task.status == TaskStatus.PENDING)
    )
    running = await db.execute(
        select(Task)
        .where(Task.type == TaskType.HUMAN)
        .where(Task.status == TaskStatus.RUNNING)
    )
    
    return {
        "pending_count": len(pending.scalars().all()),
        "in_progress_count": len(running.scalars().all())
    }


@router.post("/{task_id}/submit")
async def submit_review(
    task_id: UUID,
    submission: HITLSubmit,
    db: AsyncSession = Depends(get_db)
):
    """Submit human review result"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.type != TaskType.HUMAN:
        raise HTTPException(status_code=400, detail="Not a HITL task")
    
    # Update task
    task.result = submission.data
    task.status = TaskStatus.COMPLETED
    task.confidence = 1.0  # Human-verified = full confidence
    
    # Audit log
    audit = AuditLog(
        task_id=task.id,
        action="human_review_completed",
        changes={"notes": submission.notes} if submission.notes else None
    )
    db.add(audit)
    await db.commit()
    
    # Route to next step
    await route_task(task.id, db)
    
    # Calculate turnaround time
    if task.created_at:
        import datetime
        turnaround_time = (datetime.datetime.now(datetime.timezone.utc) - task.created_at).total_seconds()
        # logger.info(f"HITL Task {task_id} resolved. Turnaround time: {turnaround_time:.2f}s")
        # TODO: Add proper logger

    return {"success": True, "task_id": str(task_id)}


@router.post("/{task_id}/skip")
async def skip_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Skip a HITL task (mark as blocked)"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = TaskStatus.BLOCKED
    
    audit = AuditLog(
        task_id=task.id,
        action="human_review_skipped"
    )
    db.add(audit)
    await db.commit()
    
    return {"success": True, "message": "Task skipped"}
