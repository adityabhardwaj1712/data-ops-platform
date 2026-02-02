import httpx
import trafilatura
import logging
from typing import Dict, Any, Optional, Tuple

from app.scraper.logic.base import BaseScraper
from app.scraper.antibot.headers import get_random_headers
from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.processing.field_extractor import extract_fields

logger = logging.getLogger(__name__)


class StaticStrategy(BaseScraper):
    """
    Static HTTP scraper (lowest priority).

    Used for:
    - Preview
    - Preflight
    - Non-JS websites
    """

    # ------------------------------------------------------------------
    # CAPABILITY CHECK
    # ------------------------------------------------------------------
    def can_handle(self, url: str) -> bool:
        blocked = ["flipkart", "amazon", "myntra", "ajio"]
        return not any(b in url.lower() for b in blocked)

    # ------------------------------------------------------------------
    # FETCH (USED BY PREVIEW / PREFLIGHT)
    # ------------------------------------------------------------------
    async def fetch(
        self,
        url: str,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Tuple[str, str, Optional[str]]:
        """
        Fetch raw HTML.

        Returns:
            content     -> raw HTML (same for static)
            html        -> raw HTML
            screenshot  -> None
        """

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers=headers or get_random_headers(),
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

            html = response.text or ""

            logger.info(
                f"[STATIC] fetch ok | url={url} | html_len={len(html)}"
            )

            return html, html, None

        except Exception as e:
            logger.exception("[STATIC] fetch failed")
            raise RuntimeError(f"Static fetch failed: {e}")

    # ------------------------------------------------------------------
    # SCRAPE (USED BY WORKER)
    # ------------------------------------------------------------------
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
            html, _, _ = await self.fetch(
                url=url,
                timeout=timeout,
                headers=headers,
            )

            if not html.strip():
                return ScrapeResult(
                    success=False,
                    status="failed",
                    strategy_used="static",
                    failure_reason=ScrapeFailureReason.EMPTY_DATA,
                    failure_message="Empty HTML response",
                )

            markdown = trafilatura.extract(
                html,
                output_format="markdown",
                include_links=True,
                include_tables=True,
            ) or ""

            extracted = extract_fields(html, schema) if schema else {}

            return ScrapeResult(
                success=True,
                status="success",
                strategy_used="static",
                data={
                    **extracted,
                    "_raw_markdown": markdown,
                },
                confidence=60.0,
                metadata={
                    "engine": "static",
                    "html_length": len(html),
                },
            )

        except Exception as e:
            logger.exception("[STATIC] scrape failed")
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="static",
                failure_reason=ScrapeFailureReason.FETCH_FAILED,
                failure_message=str(e),
                errors=[str(e)],
            )
