import httpx
import trafilatura
import logging
from typing import Dict, Any, Optional

from app.scraper.logic.base import BaseScraper
from app.scraper.antibot.headers import get_random_headers
from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.processing.field_extractor import extract_fields


logger = logging.getLogger(__name__)


class StaticStrategy(BaseScraper):
    """
    Static HTTP scraper (lowest priority).
    """

    def can_handle(self, url: str) -> bool:
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
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                http2=True,
                headers=headers or get_random_headers(),
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

            html = response.text

            markdown = trafilatura.extract(
                html,
                output_format="markdown",
                include_links=True,
                include_tables=True,
            ) or ""

            if not markdown.strip():
                return ScrapeResult(
                    success=False,
                    status="failed",
                    strategy_used="static",
                    failure_reason=ScrapeFailureReason.EMPTY_DATA,
                    failure_message="No content extracted",
                )

            return ScrapeResult(
                success=True,
                status="success",
                strategy_used="static",
                data={"_raw_markdown": markdown},
                confidence=60.0,
                metadata={"engine": "static"},
            )

        except Exception as e:
            logger.exception("Static scrape failed")
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="static",
                failure_reason=ScrapeFailureReason.FETCH_FAILED,
                failure_message=str(e),
                errors=[str(e)],
            )
