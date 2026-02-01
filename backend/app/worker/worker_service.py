import asyncio
import logging
import os
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select, or_, desc, func, text

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

        # Recovery supervisor
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
            await asyncio.sleep(300)  # 5 minutes

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

                    try:
                        # Fetch job
                        job = await db.get(Job, task.job_id)
                        if not job:
                            raise ValueError(f"Job {task.job_id} not found")

                        # Select scraper
                        url = task.payload.get("url")
                        scraper = await scraper_registry.get_scraper(url)

                        # Execute scrape
                        result = await scraper.scrape(
                            url=url,
                            schema=job.schema,
                            job_id=str(job.id),
                            db=db,
                            **task.payload,
                        )

                        confidence = (
                            result.data.get("_confidence", 1.0)
                            if result.success and isinstance(result.data, dict)
                            else 0.0
                        )

                        if result.success:
                            task.status = (
                                TaskStatus.NEEDS_REVIEW
                                if confidence < 0.6
                                else TaskStatus.COMPLETED
                            )
                            task.result = result.data
                        else:
                            task.status = TaskStatus.FAILED
                            task.failure_reason = result.failure_reason
                            task.failure_message = result.failure_message

                        await db.commit()

                        # Finalize job if needed
                        await self.finalize_job_if_done(db, job)

                    except Exception as e:
                        logger.exception(f"Task {task.id} execution failed")
                        task.status = TaskStatus.FAILED
                        task.failure_message = str(e)
                        await db.commit()

            except Exception:
                logger.exception(f"Worker {worker_id} crashed")
                await asyncio.sleep(2)

    async def fetch_task(self, db):
        """
        Priority-based polling with SLA-aware ordering.
        Compatible with SQLAlchemy 1.4 + PostgreSQL.
        """
        stmt = (
            select(Task)
            .join(Job, Task.job_id == Job.id)
            .where(
                or_(
                    Task.status == TaskStatus.PENDING,
                    Task.status == TaskStatus.RETRYING,
                )
            )
            .order_by(
                # ✅ CORRECT SLA LOGIC (NO make_interval)
                Task.created_at
                + func.coalesce(Job.sla_seconds, 0) * text("INTERVAL '1 second'"),
                desc(Task.priority),
                Task.created_at,
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        )

        res = await db.execute(stmt)
        task = res.scalar_one_or_none()

        if task:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            await db.commit()
            return task

        return None

    async def finalize_job_if_done(self, db, job: Job):
        stmt = select(Task).where(Task.job_id == job.id)
        res = await db.execute(stmt)
        tasks = res.scalars().all()

        if not tasks:
            return

        if all(t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED) for t in tasks):
            if any(t.status == TaskStatus.COMPLETED for t in tasks):
                job.status = JobStatus.COMPLETED

                results = []
                for t in tasks:
                    if t.result:
                        if isinstance(t.result, list):
                            results.extend(t.result)
                        elif isinstance(t.result, dict):
                            r = t.result.copy()
                            r.setdefault("_source_url", t.payload.get("url"))
                            results.append(r)

                os.makedirs("/app/data/artifacts", exist_ok=True)
                path = Path(f"/app/data/artifacts/job_{job.id}_results.json")

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)

                confidences = [
                    t.result.get("_confidence", 100)
                    for t in tasks
                    if isinstance(t.result, dict)
                ]
                avg_conf = sum(confidences) / len(confidences) if confidences else 100

                dv = DatasetVersion(
                    job_id=job.id,
                    version=1,
                    data_location=str(path),
                    row_count=len(results),
                    change_summary={"avg_confidence": avg_conf},
                )
                db.add(dv)

            else:
                job.status = JobStatus.FAILED_FINAL

            await db.commit()


# Global instance
worker_service = WorkerService()
