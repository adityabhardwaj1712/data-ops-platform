"""
Job Scheduler Service
Schedule recurring scraping jobs and automated tasks
"""
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Job, JobStatus
from app.db.session import async_session_factory

logger = logging.getLogger(__name__)


class JobScheduler:
    """Schedule and manage recurring jobs"""
    
    def __init__(self):
        self.scheduled_jobs: Dict[UUID, Dict[str, Any]] = {}
        self.running = False
        self._task: Optional[asyncio.Task] = None
    
    async def schedule_job(
        self,
        job_id: UUID,
        schedule_type: str,  # "daily", "weekly", "hourly", "custom"
        schedule_config: Dict[str, Any],
        job_function: Callable
    ):
        """
        Schedule a job to run at specified intervals
        
        Args:
            job_id: Job ID to schedule
            schedule_type: Type of schedule (daily, weekly, hourly, custom)
            schedule_config: Configuration for the schedule
            job_function: Async function to execute
        """
        self.scheduled_jobs[job_id] = {
            "schedule_type": schedule_type,
            "schedule_config": schedule_config,
            "job_function": job_function,
            "last_run": None,
            "next_run": self._calculate_next_run(schedule_type, schedule_config)
        }
        
        logger.info(f"Scheduled job {job_id} with schedule {schedule_type}")
    
    def _calculate_next_run(self, schedule_type: str, config: Dict[str, Any]) -> datetime:
        """Calculate next run time based on schedule type"""
        now = datetime.utcnow()
        
        if schedule_type == "hourly":
            return now + timedelta(hours=config.get("interval", 1))
        elif schedule_type == "daily":
            hour = config.get("hour", 0)
            minute = config.get("minute", 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        elif schedule_type == "weekly":
            days_ahead = config.get("day_of_week", 0) - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=config.get("hour", 0), minute=config.get("minute", 0))
            return next_run
        elif schedule_type == "custom":
            interval_seconds = config.get("interval_seconds", 3600)
            return now + timedelta(seconds=interval_seconds)
        
        return now + timedelta(hours=1)  # Default: hourly
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Job scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Job scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                now = datetime.utcnow()
                
                for job_id, job_info in list(self.scheduled_jobs.items()):
                    if job_info["next_run"] <= now:
                        # Execute job
                        try:
                            await job_info["job_function"](job_id)
                            job_info["last_run"] = now
                            job_info["next_run"] = self._calculate_next_run(
                                job_info["schedule_type"],
                                job_info["schedule_config"]
                            )
                            logger.info(f"Executed scheduled job {job_id}")
                        except Exception as e:
                            logger.error(f"Error executing scheduled job {job_id}: {e}", exc_info=True)
                
                # Sleep for 60 seconds before checking again
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def unschedule_job(self, job_id: UUID):
        """Remove a job from the schedule"""
        if job_id in self.scheduled_jobs:
            del self.scheduled_jobs[job_id]
            logger.info(f"Unscheduled job {job_id}")
    
    def get_scheduled_jobs(self) -> Dict[UUID, Dict[str, Any]]:
        """Get all scheduled jobs"""
        return {
            job_id: {
                "schedule_type": info["schedule_type"],
                "last_run": info["last_run"],
                "next_run": info["next_run"]
            }
            for job_id, info in self.scheduled_jobs.items()
        }


# Global scheduler instance
scheduler = JobScheduler()
