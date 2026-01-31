from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any, Dict, List
import asyncio
import logging
import random
from urllib.parse import urlparse
import time
from app.schemas import ScrapeResult

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Base class for all scraping strategies.
    Provides common retry and anti-bot logic.
    """
    _last_request_time: Dict[str, float] = {}

    @abstractmethod
    async def can_handle(self, url: str) -> bool:
        """Determines if this scraper can handle the given URL."""
        pass

    @abstractmethod
    async def scrape(
        self, 
        url: str, 
        schema: Dict[str, Any], 
        job_id: str,
        **kwargs
    ) -> ScrapeResult:
        """Main scraping entry point."""
        pass

    async def throttle(self, url: str, min_delay: float = 1.5):
        """
        Enforces a minimum delay between requests to the same domain.
        """
        domain = urlparse(url).netloc
        now = time.time()
        
        last_time = self._last_request_time.get(domain, 0)
        elapsed = now - last_time
        
        if elapsed < min_delay:
            wait_time = min_delay - elapsed + (random.uniform(0.1, 0.5)) # Add jitter
            logger.debug(f"Throttling request to {domain}. Waiting {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
            
        self._last_request_time[domain] = time.time()

    async def fetch_with_retry(
        self, 
        fetch_func, 
        url: str, 
        max_retries: int = 3, 
        **kwargs
    ) -> Any:
        """
        Fetches content with exponential backoff and jitter.
        """
        # Always throttle before first attempt
        await self.throttle(url)
        
        last_err = None
        for attempt in range(max_retries):
            try:
                # Add human-like jitter on retries
                if attempt > 0:
                    import random
                    wait_time = (2 ** attempt) + random.uniform(1.0, 3.0) # Beefed up jitter for pro-grade
                    logger.info(f"Retrying in {wait_time:.2f}s...")
                    await asyncio.sleep(wait_time)
                
                return await fetch_func(url, **kwargs)
            except Exception as e:
                last_err = e
                logger.warning(f"Fetch failed (attempt {attempt+1}/{max_retries}): {e}")
        
        raise last_err
