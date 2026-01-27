"""
Worker Service Entry Point
Run this module to start the background worker service standalone
"""

import asyncio
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging_config import setup_logging
from app.worker.main import worker_service
from app.db.session import engine
from app.db import models

# Setup logging
logger = setup_logging(level="INFO", json_format=False)


async def main():
    """Main entry point for worker service."""
    logger.info("=" * 60)
    logger.info("DataOps Platform - Background Worker Service")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    logger.info("Database initialized")
    
    # Get worker configuration from environment
    concurrency = int(os.getenv("WORKER_CONCURRENCY", "2"))
    poll_interval = int(os.getenv("WORKER_POLL_INTERVAL", "5"))
    
    logger.info(f"Worker configuration:")
    logger.info(f"  - Concurrency: {concurrency}")
    logger.info(f"  - Poll interval: {poll_interval}s")
    
    # Configure worker
    worker_service.concurrency = concurrency
    worker_service.poll_interval = poll_interval
    
    # Start worker service
    try:
        await worker_service.start()
        
        # Keep running until interrupted
        logger.info("Worker service running. Press Ctrl+C to stop.")
        while worker_service.running:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    
    except Exception as e:
        logger.error(f"Worker service error: {e}", exc_info=True)
    
    finally:
        # Cleanup
        logger.info("Shutting down worker service...")
        await worker_service.stop()
        await engine.dispose()
        logger.info("Worker service stopped")


if __name__ == "__main__":
    asyncio.run(main())
