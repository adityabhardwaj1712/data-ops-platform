import asyncio
import logging

from app.worker.worker_service import worker_service

logging.basicConfig(level=logging.INFO)


async def main():
    await worker_service.start()
    logging.info("🟢 Worker running and waiting for jobs")

    # Keep container alive forever
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
