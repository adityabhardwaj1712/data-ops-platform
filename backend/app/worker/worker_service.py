import asyncio
import logging
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select, or_

from app.db.session import AsyncSessionLocal
from app.db.models import Task, TaskStatus, Job, JobStatus, DatasetVersion
from app.scraper.logic.registry import scraper_registry
from app.core.recovery import recover_stuck_tasks

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class WorkerService:
    def __init__(self, concurrency: int = 5):
        self.concurrency = concurrency

    async def start(self):
        logger.info(f"Starting worker with {self.concurrency} threads")

        # Start recovery supervisor in the background
        asyncio.create_task(self.recovery_loop())

        tasks = [
            asyncio.create_task(self.worker_loop(i))
            for i in range(self.concurrency)
        ]

        await asyncio.gather(*tasks)

    async def recovery_loop(self):
        """Periodically check for stuck tasks."""
        while True:
            try:
                async with AsyncSessionLocal() as db:
                    await recover_stuck_tasks(db)
            except Exception as e:
                logger.error(f"Recovery loop error: {e}")
            await asyncio.sleep(60 * 5) # Every 5 minutes

    async def worker_loop(self, worker_id: int):
        logger.info(f"Worker {worker_id} started")

        while True:
            try:
                async with AsyncSessionLocal() as db:
                    task = await self.fetch_task(db)

                    if not task:
                        await asyncio.sleep(1)
                        continue

                    logger.info(f"Worker {worker_id} executing task {task.id}")

                    task.status = TaskStatus.RUNNING
                    await db.commit()

                    try:
                        # 1. Get Job
                        job_stmt = select(Job).where(Job.id == task.job_id)
                        job_res = await db.execute(job_stmt)
                        job = job_res.scalar_one_or_none()

                        if not job:
                            raise ValueError(f"Job {task.job_id} not found for task {task.id}")

                        # 2. Get Scraper
                        url = task.payload.get("url")
                        scraper = await scraper_registry.get_scraper(url)

                        # 3. Execute Scrape
                        result = await scraper.scrape(
                            url=url,
                            schema=job.schema,
                            job_id=str(job.id),
                            db=db,
                            **task.payload
                        )

                        # 4. Update Task
                        # HITL Routing: if confidence < 0.6, needs review
                        confidence = result.data.get("_confidence", 1.0) if result.success else 0.0
                        
                        if result.success:
                            if confidence < 0.6:
                                task.status = TaskStatus.NEEDS_REVIEW
                                logger.info(f"Task {task.id} routed to NEEDS_REVIEW (confidence: {confidence})")
                            else:
                                task.status = TaskStatus.COMPLETED
                            task.result = result.data
                        else:
                            task.status = TaskStatus.FAILED
                            task.failure_reason = result.failure_reason
                            task.failure_message = result.failure_message
                        
                        await db.commit()

                        # 4.5 Trigger Webhook if present
                        if task.status == TaskStatus.COMPLETED and job.webhook_url:
                            logger.info(f"Triggering webhook for job {job.id} at {job.webhook_url}")
                            # In real world, use httpx.post(job.webhook_url, json=...)

                        # 5. Check if all tasks for this job are done
                        check_stmt = select(Task).where(Task.job_id == job.id)
                        tasks_res = await db.execute(check_stmt)
                        all_tasks = tasks_res.scalars().all()
                        
                        if all(t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] for t in all_tasks):
                            if any(t.status == TaskStatus.COMPLETED for t in all_tasks):
                                job.status = JobStatus.COMPLETED
                                
                                # Aggregate and flatten results
                                results = []
                                for t in all_tasks:
                                    if t.result:
                                        if isinstance(t.result, list):
                                            results.extend(t.result)
                                        else:
                                            # Add source URL to result if not present
                                            res = t.result.copy()
                                            if "_source_url" not in res:
                                                res["_source_url"] = t.payload.get("url")
                                            results.append(res)
                                
                                # Save to file for export
                                os.makedirs("/app/data/artifacts", exist_ok=True)
                                data_filename = f"job_{job.id}_results.json"
                                data_path = Path("/app/data/artifacts") / data_filename
                                
                                with open(data_path, "w", encoding="utf-8") as f:
                                    json.dump(results, f, indent=2)
                                
                                # Calculate average confidence
                                task_confidences = [t.result.get("_confidence", 100) for t in all_tasks if t.result and isinstance(t.result, dict)]
                                avg_confidence = sum(task_confidences) / len(task_confidences) if task_confidences else 100

                                # Create DatasetVersion
                                dv = DatasetVersion(
                                    job_id=job.id,
                                    version=1,
                                    data_location=str(data_path),
                                    row_count=len(results),
                                    change_summary={"avg_confidence": avg_confidence}
                                )
                                db.add(dv)
                            else:
                                job.status = JobStatus.FAILED_FINAL
                            await db.commit()

                    except Exception as e:
                        logger.error(f"Task {task.id} execution failed: {e}")
                        task.status = TaskStatus.FAILED
                        task.failure_message = str(e)
                        await db.commit()

            except Exception as e:
                logger.exception(f"Worker {worker_id} crashed: {e}")
                await asyncio.sleep(2)

    async def fetch_task(self, db):
        """
        Priority-based polling with SLA consideration.
        """
        stmt = (
            select(Task, Job)
            .join(Job, Task.job_id == Job.id)
            .where(
                or_(
                    Task.status == TaskStatus.PENDING,
                    Task.status == TaskStatus.RETRYING
                )
            )
            .order_by(
                (Task.created_at + Job.sla_seconds * (asyncio.Future().set_result(None) or 1)).asc(), # Placeholder for SQL interval if needed, but for now simple order is fine
                Task.priority.desc(),
                Task.created_at.asc()
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        )

        res = await db.execute(stmt)
        row = res.one_or_none()
        
        if row:
            task, job = row
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            await db.commit()
            return task
            
        return None


# global instance
worker_service = WorkerService()
