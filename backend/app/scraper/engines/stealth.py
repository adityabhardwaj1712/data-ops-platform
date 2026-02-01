import asyncio
import random
import os
from datetime import datetime
from typing import Dict, Any, Optional

import trafilatura
from playwright.async_api import async_playwright

from app.scraper.logic.base import BaseScraper
from app.scraper.antibot.fingerprint import get_stealth_config
from app.scraper.antibot.delays import human_like_delay, random_mouse_move
from app.scraper.antibot.headers import get_random_user_agent
from app.schemas import ScrapeResult


class StealthStrategy(BaseScraper):
    """
    Stealth scraper for bot-protected sites.
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
            stealth = get_stealth_config()

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                    ],
                )

                context = await browser.new_context(
                    viewport=stealth["viewport"],
                    user_agent=get_random_user_agent(),
                    locale=stealth["locale"],
                    timezone_id=stealth["timezone"],
                )

                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.chrome = { runtime: {} };
                """)

                page = await context.new_page()

                await asyncio.sleep(random.uniform(1.0, 2.5))
                await page.goto(url, timeout=timeout * 1000, wait_until="networkidle")

                await human_like_delay(1000, 3000)
                await random_mouse_move(page)

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
                        "_strategy": "stealth",
                        "_confidence": 0.9,
                    },
                )

        except Exception as e:
            return ScrapeResult(
                success=False,
                failure_reason="stealth_failed",
                failure_message=str(e),
            )
