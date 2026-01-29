from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Base class for all scraping strategies.
    Provides common retry and timeout logic.
    """
    
    @abstractmethod
    async def fetch(self, url: str, **kwargs) -> Tuple[str, str, Optional[str]]:
        """
        Fetches page content.
        Returns: (markdown_content, raw_html, screenshot_path)
        """
        pass

    async def fetch_with_retry(self, url: str, max_retries: int = 3, **kwargs) -> Tuple[str, str, Optional[str]]:
        """
        Fetches content with exponential backoff.
        """
        last_err = None
        for attempt in range(max_retries):
            try:
                return await self.fetch(url, **kwargs)
            except Exception as e:
                last_err = e
                wait_time = (2 ** attempt) + 1
                logger.warning(f"Fetch failed (attempt {attempt+1}/{max_retries}): {e}. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        raise last_err
