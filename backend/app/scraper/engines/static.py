import httpx
import trafilatura
import logging
from typing import Dict, Any, Optional

from app.scraper.logic.base import BaseScraper
from app.scraper.antibot.headers import get_random_headers
from app.schemas import ScrapeResult

logger = logging.getLogger(__name__)


class StaticStrategy(BaseScraper):
    """
    Static HTTP scraper.
    LAST priority.
    """

    def can_handle(self, url: str) -> bool:
        # Avoid JS-heavy ecommerce
        blocked = ["flipkart", "amazon", "myntra", "ajio"]
        return not any(b in url.lower() for b in blocked)

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ScrapeResult:
        try:
            request_headers = headers or get_random_headers()

            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                http2=True,
            ) as client:
                response = await client.get(url, headers=request_headers)
                response.raise_for_status()

            html = response.text

            markdown = trafilatura.extract(
                html,
                output_format="markdown",
                include_links=True,
                include_tables=True,
            ) or ""

            return ScrapeResult(
                success=True,
                data={
                    "_raw_markdown": markdown,
                    "_strategy": "static",
                    "_confidence": 0.6,
                },
            )

        except Exception as e:
            logger.exception("StaticStrategy failed")
            return ScrapeResult(
                success=False,
                failure_reason="static_failed",
                failure_message=str(e),
            )
