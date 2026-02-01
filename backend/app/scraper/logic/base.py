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
    Base class for ALL scrapers & strategies.
    Registry depends on this class.
    """

    _last_request_time: Dict[str, float] = {}

    # -----------------------
    # ROUTING (SYNC)
    # -----------------------
    def can_handle(self, url: str) -> bool:
        """
        Decide if this scraper can handle the URL.
        Must be FAST and SYNC.
        """
        return True  # default fallback behavior

    # -----------------------
    # EXECUTION (ASYNC)
    # -----------------------
    @abstractmethod
    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs,
    ) -> ScrapeResult:
        pass

    # -----------------------
    # HELPERS
    # -----------------------
    async def throttle(self, url: str, min_delay: float = 1.5):
        domain = urlparse(url).netloc
        now = time.time()

        last = self._last_request_time.get(domain, 0)
        elapsed = now - last

        if elapsed < min_delay:
            wait = min_delay - elapsed + random.uniform(0.1, 0.4)
            logger.debug(f"Throttling {domain} for {wait:.2f}s")
            await asyncio.sleep(wait)

        self._last_request_time[domain] = time.time()
