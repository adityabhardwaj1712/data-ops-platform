import asyncio
import os
import random
from datetime import datetime
from typing import Dict, Any, Optional

import trafilatura
from playwright.async_api import async_playwright

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult


class BrowserStrategy(BaseScraper):
    """
    Browser-based scraper for JS-heavy sites.
    """

    def can_handle(self, url: str) -> bool:
        return True

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        timeout: int = 30,
        wait_for_selector: Optional[str] = None,
        **kwargs,
    ) -> ScrapeResult:

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                    ],
                )

                width = random.randint(1280, 1920)
                height = random.randint(720, 1080)

                context = await browser.new_context(
                    viewport={"width": width, "height": height},
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                )

                page = await context.new_page()

                async def block_resources(route):
                    if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
                        await route.abort()
                    else:
                        await route.continue_()

                await page.route("**/*", block_resources)

                await asyncio.sleep(random.uniform(0.5, 1.5))
                await page.goto(url, timeout=timeout * 1000)

                if wait_for_selector:
                    try:
                        await page.wait_for_selector(wait_for_selector, timeout=10_000)
                    except Exception:
                        pass

                html = await page.content()

                markdown = trafilatura.extract(
                    html,
                    output_format="markdown",
                    include_links=True,
                    include_tables=True,
                ) or ""

                await context.close()
                await browser.close()

                return ScrapeResult(
                    success=True,
                    data={
                        "_raw_markdown": markdown,
                        "_strategy": "browser",
                        "_confidence": 0.8,
                    },
                )

        except Exception as e:
            return ScrapeResult(
                success=False,
                failure_reason="browser_failed",
                failure_message=str(e),
            )
