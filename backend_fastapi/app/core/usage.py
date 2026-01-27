"""
Usage Tracking System
Track API usage, scrapes, storage, etc. for billing and analytics
"""

from datetime import datetime, date
from typing import Optional
from uuid import UUID
import logging

from app.core.config import settings
from app.core.cache import cache

logger = logging.getLogger(__name__)


class UsageTracker:
    """
    Track usage for billing and quota management.
    
    Lightweight implementation:
    - Increments counters in cache (fast)
    - Persists to database periodically (background task)
    - Checks quotas before expensive operations
    """
    
    async def track_scrape(self, org_id: str, user_id: Optional[str] = None):
        """Track a scrape operation."""
        today = date.today().isoformat()
        
        # Increment daily counter in cache
        cache_key = f"usage:{org_id}:{today}:scrapes"
        current = await cache.get(cache_key) or 0
        await cache.set(cache_key, int(current) + 1, ttl=86400)  # 24 hours
        
        logger.debug(f"Tracked scrape for org {org_id}")
        
        # Check quota
        await self._check_quota(org_id, "scrapes", int(current) + 1)
    
    async def track_storage(self, org_id: str, bytes_added: int):
        """Track storage usage."""
        cache_key = f"usage:{org_id}:storage"
        current = await cache.get(cache_key) or 0
        await cache.set(cache_key, int(current) + bytes_added)
        
        logger.debug(f"Tracked {bytes_added} bytes for org {org_id}")
    
    async def track_api_call(self, org_id: str, endpoint: str):
        """Track API call."""
        today = date.today().isoformat()
        cache_key = f"usage:{org_id}:{today}:api_calls"
        current = await cache.get(cache_key) or 0
        await cache.set(cache_key, int(current) + 1, ttl=86400)
    
    async def track_ai_query(self, org_id: str):
        """Track AI copilot query."""
        today = date.today().isoformat()
        cache_key = f"usage:{org_id}:{today}:ai_queries"
        current = await cache.get(cache_key) or 0
        await cache.set(cache_key, int(current) + 1, ttl=86400)
        
        # Check AI quota
        await self._check_quota(org_id, "ai_queries", int(current) + 1)
    
    async def get_usage(self, org_id: str, metric: str = "scrapes") -> int:
        """Get current usage for a metric."""
        today = date.today().isoformat()
        cache_key = f"usage:{org_id}:{today}:{metric}"
        return await cache.get(cache_key) or 0
    
    async def _check_quota(self, org_id: str, metric: str, current_usage: int):
        """Check if usage exceeds quota."""
        # Get org plan (would come from database in production)
        # For now, use default quotas from settings
        quota = settings.QUOTA_FREE_SCRAPES  # Default to free tier
        
        if current_usage >= quota:
            logger.warning(f"Quota exceeded for org {org_id}: {current_usage}/{quota} {metric}")
            # In production, would send alert or block request
            # For now, just log
    
    async def get_quota_status(self, org_id: str) -> dict:
        """Get quota status for all metrics."""
        scrapes = await self.get_usage(org_id, "scrapes")
        ai_queries = await self.get_usage(org_id, "ai_queries")
        
        return {
            "scrapes": {
                "used": scrapes,
                "limit": settings.QUOTA_FREE_SCRAPES,
                "percentage": (scrapes / settings.QUOTA_FREE_SCRAPES * 100) if settings.QUOTA_FREE_SCRAPES > 0 else 0
            },
            "ai_queries": {
                "used": ai_queries,
                "limit": 100,  # Default for free tier
                "percentage": (ai_queries / 100 * 100) if ai_queries else 0
            }
        }


# Global usage tracker instance
usage_tracker = UsageTracker()
