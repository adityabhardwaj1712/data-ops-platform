from datetime import datetime, timedelta, timezone
import logging
from sqlalchemy import select, update
from app.db.models import Task, TaskStatus

logger = logging.getLogger(__name__)

async def recover_stuck_tasks(db):
    """
    Finds tasks that have been in RUNNING state for too long
    and resets them to RETRYING or FAILED.
    """
    # 15 minutes cutoff
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)

    stmt = (
        select(Task)
        .where(
            Task.status == TaskStatus.RUNNING,
            Task.started_at < cutoff
        )
    )
    
    res = await db.execute(stmt)
    stuck_tasks = res.scalars().all()

    if not stuck_tasks:
        return

    logger.info(f"Found {len(stuck_tasks)} stuck tasks. Resetting...")

    for task in stuck_tasks:
        if task.retry_count < 3: # Max retries
            task.status = TaskStatus.RETRYING
            task.retry_count += 1
            logger.warning(f"Task {task.id} reset to RETRYING (retry {task.retry_count})")
        else:
            task.status = TaskStatus.FAILED
            task.failure_reason = "TIMEOUT"
            task.failure_message = "Task exceeded maximum run time and retry limit."
            logger.error(f"Task {task.id} failed after maximum retries in recovery supervisor.")
    
    await db.commit()
