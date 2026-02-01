import asyncio
import logging
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Task, TaskStatus

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class WorkerService:
    def __init__(self, concurrency: int = 5):
        self.concurrency = concurrency

    async def start(self):
        logger.info(f"Starting worker with {self.concurrency} threads")

        tasks = [
            asyncio.create_task(self.worker_loop(i))
            for i in range(self.concurrency)
        ]

        await asyncio.gather(*tasks)

    async def worker_loop(self, worker_id: int):
        logger.info(f"Worker {worker_id} started")

        while True:
            try:
                async for db in get_db():
                    task = await self.fetch_task(db)

                    if not task:
                        await asyncio.sleep(1)
                        continue

                    logger.info(f"Worker {worker_id} executing task {task.id}")

                    task.status = TaskStatus.RUNNING
                    await db.commit()

                    # 🔥 ACTUAL EXECUTION (mock for now)
                    await asyncio.sleep(5)

                    task.status = TaskStatus.COMPLETED
                    task.result = {"success": True}
                    await db.commit()

            except Exception as e:
                logger.exception(f"Worker {worker_id} crashed: {e}")
                await asyncio.sleep(2)

    async def fetch_task(self, db):
        stmt = (
            select(Task)
            .where(Task.status == TaskStatus.PENDING)
            .order_by(Task.created_at)
            .limit(1)
        )

        res = await db.execute(stmt)
        return res.scalar_one_or_none()


# global instance
worker_service = WorkerService()
