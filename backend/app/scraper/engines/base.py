from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio
import logging
import random
import time
from urllib.parse import urlparse

from app.schemas import ScrapeResult

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Canonical base class for ALL scrapers.
    Registry, worker, and API depend on this.
    """

    _last_request_time: Dict[str, float] = {}

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """SYNC method — DO NOT make async"""
        pass

    @abstractmethod
    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs,
    ) -> ScrapeResult:
        pass

    async def throttle(self, url: str, min_delay: float = 1.5):
        domain = urlparse(url).netloc
        now = time.time()

        last = self._last_request_time.get(domain, 0)
        elapsed = now - last

        if elapsed < min_delay:
            wait = min_delay - elapsed + random.uniform(0.1, 0.5)
            logger.debug(f"Throttling {domain} for {wait:.2f}s")
            await asyncio.sleep(wait)

        self._last_request_time[domain] = time.time()

    async def fetch_with_retry(self, coro, *args, retries=3, **kwargs):
        await self.throttle(args[0])

        last_err = None
        for attempt in range(retries):
            try:
                if attempt > 0:
                    delay = (2 ** attempt) + random.uniform(1, 3)
                    await asyncio.sleep(delay)

                return await coro(*args, **kwargs)
            except Exception as e:
                last_err = e
                logger.warning(f"Retry {attempt + 1}/{retries} failed: {e}")

        raise last_err
