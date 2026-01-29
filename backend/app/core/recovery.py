"""
Graceful Failure & Recovery Module
Sprint 15 - Task 117

Ensures:
- Worker crashes don't kill jobs
- Browser crashes are retried safely
- Jobs resume or fail cleanly
- Partial artifacts are preserved
"""
import asyncio
import logging
import signal
import sys
from typing import Optional, Callable, Any
from functools import wraps
from pathlib import Path
import json
from datetime import datetime

from app.core.limits import limits
from app.db.session import get_db
from app.db.models import Job, JobStatus
from sqlalchemy import select

logger = logging.getLogger(__name__)


class GracefulShutdownHandler:
    """
    Handles graceful shutdown of the application.
    
    Ensures:
    - Clean shutdown sequence
    - No orphan processes
    - Queues drain safely
    """
    
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.shutdown_callbacks: list[Callable] = []
        self._shutdown_in_progress = False
    
    def register_callback(self, callback: Callable):
        """Register a callback to be called during shutdown."""
        self.shutdown_callbacks.append(callback)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Signal handlers registered for graceful shutdown")
    
    async def shutdown(self):
        """Execute graceful shutdown sequence."""
        if self._shutdown_in_progress:
            logger.warning("Shutdown already in progress")
            return
        
        self._shutdown_in_progress = True
        logger.info("Starting graceful shutdown sequence...")
        
        # Execute all registered callbacks
        for callback in self.shutdown_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error in shutdown callback: {e}", exc_info=True)
        
        logger.info("Graceful shutdown completed")


class JobRecoveryManager:
    """
    Manages job recovery and partial artifact preservation.
    
    Ensures jobs can resume or fail cleanly.
    """
    
    @staticmethod
    async def save_partial_artifacts(
        job_id: str,
        artifacts: dict,
        artifacts_dir: Path = Path("/app/data/artifacts")
    ):
        """
        Save partial artifacts for a job.
        
        Args:
            job_id: Job ID
            artifacts: Dictionary of artifacts to save
            artifacts_dir: Base artifacts directory
        """
        try:
            job_artifacts_dir = artifacts_dir / str(job_id)
            job_artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save partial artifacts with timestamp
            partial_file = job_artifacts_dir / f"partial_{datetime.utcnow().isoformat()}.json"
            
            with open(partial_file, "w") as f:
                json.dump({
                    "timestamp": datetime.utcnow().isoformat(),
                    "artifacts": artifacts,
                    "status": "partial"
                }, f, indent=2)
            
            logger.info(f"Saved partial artifacts for job {job_id} to {partial_file}")
            return str(partial_file)
        
        except Exception as e:
            logger.error(f"Failed to save partial artifacts for job {job_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def load_partial_artifacts(
        job_id: str,
        artifacts_dir: Path = Path("/app/data/artifacts")
    ) -> Optional[dict]:
        """
        Load partial artifacts for a job.
        
        Args:
            job_id: Job ID
            artifacts_dir: Base artifacts directory
        
        Returns:
            Dictionary of partial artifacts or None
        """
        try:
            job_artifacts_dir = artifacts_dir / str(job_id)
            
            if not job_artifacts_dir.exists():
                return None
            
            # Find most recent partial file
            partial_files = sorted(job_artifacts_dir.glob("partial_*.json"), reverse=True)
            
            if not partial_files:
                return None
            
            with open(partial_files[0], "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded partial artifacts for job {job_id} from {partial_files[0]}")
            return data.get("artifacts")
        
        except Exception as e:
            logger.error(f"Failed to load partial artifacts for job {job_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def mark_job_for_recovery(job_id: str, error: str):
        """
        Mark a job for recovery after a crash.
        
        Args:
            job_id: Job ID
            error: Error message
        """
        try:
            async for db in get_db():
                stmt = select(Job).where(Job.id == job_id)
                result = await db.execute(stmt)
                job = result.scalar_one_or_none()
                
                if job:
                    # Update job status to indicate recovery needed
                    job.status = JobStatus.FAILED
                    
                    if not job.config:
                        job.config = {}
                    
                    job.config["recovery_needed"] = True
                    job.config["last_error"] = error
                    job.config["last_failure_time"] = datetime.utcnow().isoformat()
                    
                    await db.commit()
                    logger.info(f"Marked job {job_id} for recovery")
                
                break
        
        except Exception as e:
            logger.error(f"Failed to mark job {job_id} for recovery: {e}", exc_info=True)


def with_retry(
    max_retries: Optional[int] = None,
    retry_on: tuple = (Exception,),
    backoff: float = 1.0
):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_retries: Maximum number of retries (defaults to limits.MAX_SCRAPE_RETRIES)
        retry_on: Tuple of exception types to retry on
        backoff: Backoff multiplier for retry delay
    """
    if max_retries is None:
        max_retries = limits.MAX_SCRAPE_RETRIES
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                
                except retry_on as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = backoff * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def with_browser_recovery(func):
    """
    Decorator to handle browser crashes gracefully.
    
    Ensures browser crashes are retried safely.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a browser-related error
            browser_errors = [
                "browser",
                "playwright",
                "chromium",
                "timeout",
                "navigation",
                "page crash"
            ]
            
            is_browser_error = any(err in error_msg for err in browser_errors)
            
            if is_browser_error:
                logger.warning(f"Browser error detected in {func.__name__}: {e}")
                
                # Try to clean up and retry once
                try:
                    # Give browser time to clean up
                    await asyncio.sleep(2)
                    
                    logger.info(f"Retrying {func.__name__} after browser error...")
                    return await func(*args, **kwargs)
                
                except Exception as retry_error:
                    logger.error(f"Retry failed for {func.__name__}: {retry_error}")
                    raise retry_error
            
            # Not a browser error, re-raise
            raise e
    
    return wrapper


async def cleanup_orphan_processes():
    """
    Clean up orphan browser processes.
    
    Called during shutdown to ensure no processes are left running.
    """
    try:
        import psutil
        
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        
        for child in children:
            try:
                # Check if it's a browser process
                if child.name() and any(
                    browser in child.name().lower()
                    for browser in ["chromium", "chrome", "firefox", "webkit"]
                ):
                    logger.info(f"Terminating orphan browser process: {child.pid}")
                    child.terminate()
                    
                    # Wait for termination
                    try:
                        child.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        logger.warning(f"Force killing browser process: {child.pid}")
                        child.kill()
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.info("Orphan process cleanup completed")
    
    except Exception as e:
        logger.error(f"Error during orphan process cleanup: {e}", exc_info=True)


# Global shutdown handler instance
shutdown_handler = GracefulShutdownHandler()
