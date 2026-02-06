"""
Streaming Scraper - Real-time monitoring and polling

Continuously monitors URLs for changes and triggers alerts.
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult, ScrapeFailureReason, StreamingConfig
from app.scraper.engines.static import StaticStrategy

logger = logging.getLogger(__name__)


class StreamingScraper(BaseScraper):
    """
    Real-time monitoring scraper with change detection.
    Polls URLs at intervals and alerts on changes.
    """
    
    # Class-level storage for active monitoring jobs
    _active_jobs: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self):
        self.static_scraper = StaticStrategy()
    
    def get_name(self) -> str:
        return "streaming"
    
    def can_handle(self, url: str) -> bool:
        """Requires explicit strategy selection"""
        return False
    
    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs
    ) -> ScrapeResult:
        """
        Start monitoring URL for changes
        
        Args:
            url: URL to monitor
            schema: Data extraction schema
            job_id: Job identifier
            **kwargs: streaming_config (StreamingConfig)
        """
        logger.info(f"Starting streaming monitor for {url}")
        
        streaming_config: StreamingConfig = kwargs.get('streaming_config')
        if not streaming_config:
            streaming_config = StreamingConfig()
        
        try:
            # Start monitoring in background
            job_id = await self.start_monitoring(url, streaming_config, schema)
            
            return ScrapeResult(
                success=True,
                status="success",
                data={
                    "monitoring_job_id": job_id,
                    "status": "active",
                    "poll_interval": streaming_config.poll_interval_seconds,
                    "max_duration": streaming_config.max_duration_minutes
                },
                strategy_used=self.get_name(),
                confidence=1.0,
                metadata={
                    "url": url,
                    "started_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Streaming setup failed: {e}", exc_info=True)
            return self.failure(
                reason=ScrapeFailureReason.UNKNOWN,
                message=f"Streaming error: {str(e)}",
                errors=[str(e)]
            )
    
    async def start_monitoring(
        self,
        url: str,
        config: StreamingConfig,
        schema: Dict[str, Any]
    ) -> str:
        """
        Start background monitoring task
        
        Returns:
            job_id: Monitoring job identifier
        """
        import uuid
        
        job_id = str(uuid.uuid4())
        
        # Store job info
        self._active_jobs[job_id] = {
            "url": url,
            "config": config,
            "schema": schema,
            "started_at": datetime.utcnow(),
            "last_check": None,
            "last_data": None,
            "last_hash": None,
            "check_count": 0,
            "changes_detected": 0,
            "status": "active"
        }
        
        # Start monitoring loop in background
        asyncio.create_task(self._monitoring_loop(job_id))
        
        logger.info(f"Started monitoring job {job_id} for {url}")
        return job_id
    
    async def _monitoring_loop(self, job_id: str):
        """Background monitoring loop"""
        job = self._active_jobs.get(job_id)
        if not job:
            return
        
        url = job["url"]
        config = job["config"]
        schema = job["schema"]
        
        end_time = datetime.utcnow() + timedelta(minutes=config.max_duration_minutes)
        
        logger.info(f"Monitoring loop started for job {job_id}")
        
        try:
            while datetime.utcnow() < end_time:
                # Check if job was stopped
                if job.get("status") != "active":
                    break
                
                try:
                    # Fetch current data
                    _, html, _ = await self.static_scraper.fetch(url, timeout=30)
                    
                    if html:
                        # Extract data
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html, 'lxml')
                        
                        current_data = {}
                        for field_name, selector in schema.items():
                            element = soup.select_one(selector)
                            if element:
                                current_data[field_name] = element.get_text().strip()
                        
                        # Calculate hash for change detection
                        data_str = str(sorted(current_data.items()))
                        current_hash = hashlib.md5(data_str.encode()).hexdigest()
                        
                        # Update job info
                        job["last_check"] = datetime.utcnow()
                        job["check_count"] += 1
                        
                        # Detect changes
                        if job["last_hash"] and current_hash != job["last_hash"]:
                            change_percentage = self._calculate_change(
                                job["last_data"],
                                current_data
                            )
                            
                            if change_percentage >= config.change_threshold:
                                job["changes_detected"] += 1
                                logger.info(f"Change detected in job {job_id}: {change_percentage:.1%}")
                                
                                # Trigger alert
                                if config.alert_on_change:
                                    await self._send_alert(
                                        job_id,
                                        url,
                                        job["last_data"],
                                        current_data,
                                        change_percentage,
                                        config.webhook_url
                                    )
                        
                        # Update stored data
                        job["last_data"] = current_data
                        job["last_hash"] = current_hash
                    
                except Exception as e:
                    logger.error(f"Monitoring check failed for job {job_id}: {e}")
                
                # Wait for next poll
                await asyncio.sleep(config.poll_interval_seconds)
            
            # Mark as completed
            job["status"] = "completed"
            logger.info(f"Monitoring job {job_id} completed after {job['check_count']} checks")
            
        except Exception as e:
            logger.error(f"Monitoring loop error for job {job_id}: {e}", exc_info=True)
            job["status"] = "error"
    
    def _calculate_change(
        self,
        old_data: Optional[Dict[str, Any]],
        new_data: Dict[str, Any]
    ) -> float:
        """
        Calculate percentage of fields that changed
        
        Returns:
            float: Change percentage (0.0 to 1.0)
        """
        if not old_data:
            return 1.0  # 100% change if no previous data
        
        total_fields = len(new_data)
        if total_fields == 0:
            return 0.0
        
        changed_fields = 0
        for key, new_value in new_data.items():
            old_value = old_data.get(key)
            if old_value != new_value:
                changed_fields += 1
        
        return changed_fields / total_fields
    
    async def _send_alert(
        self,
        job_id: str,
        url: str,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        change_percentage: float,
        webhook_url: Optional[str]
    ):
        """Send alert when change detected"""
        alert_data = {
            "job_id": job_id,
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "change_percentage": change_percentage,
            "old_data": old_data,
            "new_data": new_data
        }
        
        logger.info(f"Alert triggered for job {job_id}: {change_percentage:.1%} change")
        
        # Send webhook if configured
        if webhook_url:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(webhook_url, json=alert_data)
                logger.info(f"Webhook sent to {webhook_url}")
            except Exception as e:
                logger.error(f"Webhook failed: {e}")
    
    @classmethod
    async def stop_monitoring(cls, job_id: str):
        """Stop a monitoring job"""
        if job_id in cls._active_jobs:
            cls._active_jobs[job_id]["status"] = "stopped"
            logger.info(f"Stopped monitoring job {job_id}")
    
    @classmethod
    def get_job_status(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a monitoring job"""
        return cls._active_jobs.get(job_id)
    
    @classmethod
    def list_active_jobs(cls) -> Dict[str, Dict[str, Any]]:
        """List all active monitoring jobs"""
        return {
            jid: job for jid, job in cls._active_jobs.items()
            if job.get("status") == "active"
        }
