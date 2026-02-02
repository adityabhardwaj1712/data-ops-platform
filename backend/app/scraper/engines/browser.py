import asyncio
import random
import os
from datetime import datetime
from typing import Dict, Any

import trafilatura
from playwright.async_api import async_playwright

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.processing.field_extractor import extract_fields



class BrowserStrategy(BaseScraper):
    """
    JS-capable Playwright browser scraper.
    """

    def can_handle(self, url: str) -> bool:
        return True

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        timeout: int = 30,
        wait_for_selector: str | None = None,
        **kwargs,
    ) -> ScrapeResult:

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto(url, timeout=timeout * 1000)

                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=10_000)

                html = await page.content()

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
                        strategy_used="browser",
                        failure_reason=ScrapeFailureReason.EMPTY_DATA,
                        failure_message="Rendered page but no extractable content",
                    )

                extracted = await extract_fields(html, schema) if schema else {}

                screenshot_dir = os.path.join(os.getcwd(), "data", "artifacts", "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshot_dir, f"browser_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png")
                await page.screenshot(path=screenshot_path)

                await context.close()
                await browser.close()

                return ScrapeResult(
                    success=True,
                    status="success",
                    strategy_used="browser",
                    data={
                        **extracted,
                        "_raw_markdown": markdown
                    },
                    screenshots=[screenshot_path],
                    confidence=80.0,
                    metadata={"engine": "browser"},
                )

        except asyncio.TimeoutError:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="browser",
                failure_reason=ScrapeFailureReason.JS_TIMEOUT,
                failure_message="JS rendering timeout",
            )

        except Exception as e:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="browser",
                failure_reason=ScrapeFailureReason.UNKNOWN,
                failure_message=str(e),
                errors=[str(e)],
            )
