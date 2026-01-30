"""
Background Worker Service
Processes jobs from the queue with lazy-loaded heavy dependencies
"""

import asyncio
import logging
from typing import Optional
from uuid import UUID

from app.queue.job_queue import job_queue, QueueStatus
from app.db.session import get_db
from app.db.models import Job, JobStatus
from sqlalchemy import select

from app.core.limits import limits

logger = logging.getLogger(__name__)


class WorkerService:
    """
    Background worker that processes jobs from the queue.
    
    Features:
    - Lazy-loads heavy libraries only when needed
    - Processes jobs asynchronously
    - Handles retries and error recovery
    - Updates job status in database
    """
    
    def __init__(self, concurrency: Optional[int] = None, poll_interval: int = 5):
        self.concurrency = concurrency or limits.MAX_CONCURRENT_JOBS
        # Cap concurrency to platform limit
        self.concurrency = min(self.concurrency, limits.MAX_CONCURRENT_JOBS)
        self.poll_interval = poll_interval
        self.running = False
        self._workers = []
        
        # Lazy-loaded executors (loaded on first use)
        self._scrape_executor = None
        self._export_executor = None
        self._pipeline_executor = None
    
    async def start(self):
        """Start the worker service."""
        if self.running:
            logger.warning("Worker service already running")
            return
        
        self.running = True
        logger.info(f"Starting worker service with {self.concurrency} workers")
        
        # Start worker tasks
        for i in range(self.concurrency):
            worker_task = asyncio.create_task(self._worker_loop(worker_id=i))
            self._workers.append(worker_task)
        
        logger.info(f"Worker service started with {self.concurrency} workers")
    
    async def stop(self):
        """Stop the worker service."""
        if not self.running:
            return
        
        logger.info("Stopping worker service...")
        self.running = False
        
        # Cancel all worker tasks
        for worker in self._workers:
            worker.cancel()
        
        # Wait for all workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
        logger.info("Worker service stopped")
    
    async def _worker_loop(self, worker_id: int):
        """Main worker loop that processes jobs from the queue."""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get next job from queue (with timeout)
                job_data = await job_queue.dequeue(timeout=self.poll_interval)
                
                if not job_data:
                    # No jobs available, continue polling
                    continue
                
                job_id = job_data["job_id"]
                job_type = job_data["job_type"]
                
                logger.info(f"Worker {worker_id} processing job {job_id} (type={job_type})")
                
                try:
                    # Execute the job based on type
                    result = await self._execute_job(job_data)
                    
                    # Determine final status based on result confidence
                    final_status = JobStatus.COMPLETED
                    if result.get("success") and result.get("confidence", 100) < 85:
                        final_status = JobStatus.NEEDS_HITL
                    elif not result.get("success"):
                        final_status = JobStatus.FAILED_FINAL
                    # Mark job as completed in queue and DB
                    await job_queue.complete(job_id, result)
                    await self._update_job_status(job_id, final_status, result)
                    
                    logger.info(f"Worker {worker_id} completed job {job_id} with status {final_status}")
                
                except Exception as e:
                    error_msg = f"Job execution failed: {str(e)}"
                    logger.error(f"Worker {worker_id} failed job {job_id}: {error_msg}", exc_info=True)
                    
                    # Mark job as failed (with retry)
                    await job_queue.fail(job_id, error_msg, retry=True)
                    # We keep it as RUNNING or set back to CREATED if retrying, 
                    # but for now we'll set to FAILED_FINAL if it's a permanent exception
                    await self._update_job_status(job_id, JobStatus.FAILED_FINAL, {"error": error_msg})
            
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break
            
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Brief pause before retrying
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _execute_job(self, job_data: dict) -> dict:
        """
        Execute a job based on its type.
        Lazy-loads heavy executors only when needed.
        """
        job_type = job_data["job_type"]
        payload = job_data["payload"]
        
        if job_type == "SCRAPE":
            return await self._execute_scrape_job(payload)
        
        elif job_type == "PIPELINE":
            return await self._execute_pipeline_job(payload)
        
        elif job_type == "EXPORT":
            return await self._execute_export_job(payload)
        
        else:
            raise ValueError(f"Unknown job type: {job_type}")
    
    async def _execute_scrape_job(self, payload: dict) -> dict:
        """Execute a scraping job with lazy-loaded scraper."""
        # Lazy-load scraper engine (heavy dependencies)
        if not self._scrape_executor:
            logger.info("Lazy-loading scraper engine...")
            from app.worker.executors.scrape_executor import ScrapeExecutor
            self._scrape_executor = ScrapeExecutor()
        
        result = await self._scrape_executor.execute(payload)
        return result
    
    async def _execute_pipeline_job(self, payload: dict) -> dict:
        """Execute a pipeline job with lazy-loaded pipeline."""
        # Lazy-load pipeline executor (heavy dependencies)
        if not self._pipeline_executor:
            logger.info("Lazy-loading pipeline executor...")
            from app.worker.executors.pipeline_executor import PipelineExecutor
            self._pipeline_executor = PipelineExecutor()
        
        result = await self._pipeline_executor.execute(payload)
        return result
    
    async def _execute_export_job(self, payload: dict) -> dict:
        """Execute an export job with lazy-loaded exporter."""
        # Lazy-load export executor (heavy dependencies)
        if not self._export_executor:
            logger.info("Lazy-loading export executor...")
            from app.worker.executors.export_executor import ExportExecutor
            self._export_executor = ExportExecutor()
        
        result = await self._export_executor.execute(payload)
        return result
    
    async def _update_job_status(
        self,
        job_id: UUID,
        status: JobStatus,
        result: Optional[dict] = None
    ):
        """Update job status in database."""
        try:
            async for db in get_db():
                stmt = select(Job).where(Job.id == job_id)
                result_obj = await db.execute(stmt)
                job = result_obj.scalar_one_or_none()
                
                if job:
                    job.status = status
                    if result:
                        # Store result in job config
                        if not job.config:
                            job.config = {}
                        job.config["result"] = result
                        # Also sync failure info if applicable
                        if status == JobStatus.FAILED:
                            job.config["error"] = result.get("failure_message") or result.get("errors", ["Unknown error"])[0]
                    
                    await db.commit()
                    logger.debug(f"Updated job {job_id} status to {status}")
                else:
                    logger.warning(f"Job {job_id} not found in database")
                
                break  # Exit after first iteration
        
        except Exception as e:
            logger.error(f"Failed to update job status: {e}", exc_info=True)


# Global worker service instance
worker_service = WorkerService()
