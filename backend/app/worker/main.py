import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.worker.worker_service import worker_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def wait_for_db(engine, retries=30, delay=2):
    for i in range(retries):
        try:
            async with engine.connect():
                logger.info("✅ Database is ready")
                return
        except Exception:
            logger.info(f"⏳ Waiting for DB... ({i+1}/{retries})")
            await asyncio.sleep(delay)
    raise RuntimeError("❌ Database not reachable")


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # ⏳ WAIT FOR POSTGRES
    await wait_for_db(engine)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start worker
    await worker_service.start()


if __name__ == "__main__":
    asyncio.run(main())
