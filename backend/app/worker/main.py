import asyncio
import logging

from app.worker.worker_service import worker_service
from app.db import models
from app.db.session import engine

logging.basicConfig(level=logging.INFO)


async def main():
    # ✅ Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    await worker_service.start()
    logging.info("🟢 Worker running and waiting for jobs")

    # Keep container alive forever
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
