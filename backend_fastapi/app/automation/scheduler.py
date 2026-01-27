"""
Job Scheduler (FREE)
Recurring job scheduling using APScheduler
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional, Dict, Any
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class JobScheduler:
    """
    Manage recurring jobs.
    Uses AsyncIOScheduler for lightweight in-process scheduling.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._initialized = False
    
    def start(self):
        """Start the scheduler."""
        if not self._initialized:
            self.scheduler.start()
            self._initialized = True
            logger.info("Job scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler."""
        if self._initialized:
            self.scheduler.shutdown()
            self._initialized = False
            logger.info("Job scheduler stopped")
    
    def add_job(self, job_id: str, cron_expression: str, func: Any, **kwargs):
        """
        Schedule a recurring job.
        
        Args:
            job_id: Unique ID for the job
            cron_expression: Cron string (e.g. "0 0 * * *")
            func: Async function to execute
            kwargs: Arguments for the function
        """
        try:
            self.scheduler.add_job(
                func,
                CronTrigger.from_crontab(cron_expression),
                id=str(job_id),
                replace_existing=True,
                kwargs=kwargs
            )
            logger.info(f"Scheduled job {job_id} with cron: {cron_expression}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule job {job_id}: {e}")
            return False
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(str(job_id))
            logger.info(f"Removed scheduled job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False
            
    def get_job(self, job_id: str):
        """Get job details."""
        return self.scheduler.get_job(str(job_id))
        
    def list_jobs(self):
        """List all scheduled jobs."""
        return self.scheduler.get_jobs()


# Global scheduler instance
scheduler = JobScheduler()
