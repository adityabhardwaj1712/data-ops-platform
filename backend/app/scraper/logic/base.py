from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio
import logging
import random
import time
from urllib.parse import urlparse

from app.schemas import ScrapeResult, ScrapeFailureReason

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Base class for ALL scrapers & strategies.
    Registry, routing, and SLA logic depend on this class.
    """

    _last_request_time: Dict[str, float] = {}

    # -----------------------
    # IDENTITY (SYNC)
    # -----------------------
    def get_name(self) -> str:
        """
        Stable identifier for this strategy.
        MUST be overridden in child classes.
        """
        return self.__class__.__name__.replace("Strategy", "").lower()

    # -----------------------
    # ROUTING (SYNC)
    # -----------------------
    def can_handle(self, url: str) -> bool:
        """
        Decide if this scraper can handle the URL.
        MUST be fast, synchronous, and side-effect free.
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
        """
        Perform scraping and return a fully-formed ScrapeResult.
        MUST NEVER raise uncaught exceptions.
        """
        raise NotImplementedError

    # -----------------------
    # SAFETY HELPERS
    # -----------------------
    async def throttle(self, url: str, min_delay: float = 1.5):
        """
        Per-domain rate limiting to avoid bans.
        """
        domain = urlparse(url).netloc
        now = time.time()

        last = self._last_request_time.get(domain, 0)
        elapsed = now - last

        if elapsed < min_delay:
            wait = min_delay - elapsed + random.uniform(0.1, 0.4)
            logger.debug(f"Throttling {domain} for {wait:.2f}s")
            await asyncio.sleep(wait)

        self._last_request_time[domain] = time.time()

    # -----------------------
    # STANDARD FAILURE FACTORY
    # -----------------------
    def failure(
        self,
        *,
        reason: ScrapeFailureReason,
        message: str,
        errors: list[str] | None = None,
    ) -> ScrapeResult:
        """
        Canonical way to return failures.
        Prevents schema drift & enum bugs.
        """
        return ScrapeResult(
            success=False,
            status="failed",
            strategy_used=self.get_name(),
            failure_reason=reason,
            failure_message=message,
            errors=errors or [],
        )
