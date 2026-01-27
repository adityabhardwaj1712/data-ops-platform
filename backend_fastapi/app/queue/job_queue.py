"""
Lightweight In-Memory Job Queue
No Redis required - uses asyncio.Queue for simplicity
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

logger = logging.getLogger(__name__)


class QueueStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobQueue:
    """
    In-memory job queue for background task processing.
    
    Features:
    - Priority queue support
    - Retry logic for failed jobs
    - Status tracking
    - Lightweight (no external dependencies)
    """
    
    def __init__(self, max_size: int = 1000):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_size)
        self._jobs: Dict[UUID, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
    async def enqueue(
        self,
        job_id: UUID,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = 5
    ) -> bool:
        """
        Add a job to the queue.
        
        Args:
            job_id: Unique job identifier
            job_type: Type of job (SCRAPE, EXPORT, PIPELINE, etc.)
            payload: Job data
            priority: Lower number = higher priority (1-10)
        
        Returns:
            True if enqueued successfully
        """
        async with self._lock:
            if job_id in self._jobs:
                logger.warning(f"Job {job_id} already in queue")
                return False
            
            job_data = {
                "job_id": job_id,
                "job_type": job_type,
                "payload": payload,
                "status": QueueStatus.PENDING,
                "priority": priority,
                "retry_count": 0,
                "created_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None,
                "error": None
            }
            
            self._jobs[job_id] = job_data
            
            # Add to priority queue (priority, timestamp, job_id)
            await self._queue.put((priority, datetime.utcnow().timestamp(), job_id))
            
            logger.info(f"Enqueued job {job_id} (type={job_type}, priority={priority})")
            return True
    
    async def dequeue(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Get the next job from the queue.
        
        Args:
            timeout: Max seconds to wait for a job (None = wait forever)
        
        Returns:
            Job data or None if timeout
        """
        try:
            # Get highest priority job
            if timeout:
                priority, timestamp, job_id = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=timeout
                )
            else:
                priority, timestamp, job_id = await self._queue.get()
            
            async with self._lock:
                if job_id not in self._jobs:
                    logger.error(f"Job {job_id} not found in jobs dict")
                    return None
                
                job_data = self._jobs[job_id]
                job_data["status"] = QueueStatus.RUNNING
                job_data["started_at"] = datetime.utcnow()
                
                logger.info(f"Dequeued job {job_id} (type={job_data['job_type']})")
                return job_data
                
        except asyncio.TimeoutError:
            return None
    
    async def complete(self, job_id: UUID, result: Optional[Dict[str, Any]] = None):
        """Mark a job as completed."""
        async with self._lock:
            if job_id not in self._jobs:
                logger.warning(f"Cannot complete unknown job {job_id}")
                return
            
            self._jobs[job_id]["status"] = QueueStatus.COMPLETED
            self._jobs[job_id]["completed_at"] = datetime.utcnow()
            self._jobs[job_id]["result"] = result
            
            logger.info(f"Job {job_id} completed successfully")
    
    async def fail(
        self,
        job_id: UUID,
        error: str,
        retry: bool = True,
        max_retries: int = 3
    ):
        """
        Mark a job as failed and optionally retry.
        
        Args:
            job_id: Job identifier
            error: Error message
            retry: Whether to retry the job
            max_retries: Maximum retry attempts
        """
        async with self._lock:
            if job_id not in self._jobs:
                logger.warning(f"Cannot fail unknown job {job_id}")
                return
            
            job_data = self._jobs[job_id]
            job_data["retry_count"] += 1
            job_data["error"] = error
            
            if retry and job_data["retry_count"] < max_retries:
                # Re-enqueue with lower priority
                new_priority = min(job_data["priority"] + 2, 10)
                job_data["status"] = QueueStatus.PENDING
                job_data["priority"] = new_priority
                
                await self._queue.put((
                    new_priority,
                    datetime.utcnow().timestamp(),
                    job_id
                ))
                
                logger.warning(
                    f"Job {job_id} failed (retry {job_data['retry_count']}/{max_retries}): {error}"
                )
            else:
                job_data["status"] = QueueStatus.FAILED
                job_data["completed_at"] = datetime.utcnow()
                
                logger.error(
                    f"Job {job_id} failed permanently after {job_data['retry_count']} retries: {error}"
                )
    
    async def get_status(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        """Get job status and metadata."""
        async with self._lock:
            return self._jobs.get(job_id)
    
    async def get_queue_size(self) -> int:
        """Get number of pending jobs."""
        return self._queue.qsize()
    
    async def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        async with self._lock:
            stats = {
                "total": len(self._jobs),
                "pending": sum(1 for j in self._jobs.values() if j["status"] == QueueStatus.PENDING),
                "running": sum(1 for j in self._jobs.values() if j["status"] == QueueStatus.RUNNING),
                "completed": sum(1 for j in self._jobs.values() if j["status"] == QueueStatus.COMPLETED),
                "failed": sum(1 for j in self._jobs.values() if j["status"] == QueueStatus.FAILED),
            }
            return stats
    
    async def clear_completed(self, older_than_hours: int = 24):
        """Remove completed jobs older than specified hours."""
        async with self._lock:
            cutoff = datetime.utcnow().timestamp() - (older_than_hours * 3600)
            
            to_remove = [
                job_id for job_id, job_data in self._jobs.items()
                if job_data["status"] in [QueueStatus.COMPLETED, QueueStatus.FAILED]
                and job_data.get("completed_at")
                and job_data["completed_at"].timestamp() < cutoff
            ]
            
            for job_id in to_remove:
                del self._jobs[job_id]
            
            if to_remove:
                logger.info(f"Cleared {len(to_remove)} old jobs from queue")


# Global job queue instance
job_queue = JobQueue()
