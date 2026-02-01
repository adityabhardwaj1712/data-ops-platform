import asyncio
import random
import os
from datetime import datetime
from typing import Dict, Any

import trafilatura
from playwright.async_api import async_playwright

from app.scraper.logic.base import BaseScraper
from app.scraper.antibot.fingerprint import get_stealth_config
from app.scraper.antibot.delays import human_like_delay, random_mouse_move
from app.scraper.antibot.headers import get_random_user_agent
from app.schemas import ScrapeResult, ScrapeFailureReason


class StealthStrategy(BaseScraper):
    """
    Anti-bot stealth browser scraper.
    """

    def can_handle(self, url: str) -> bool:
        return True

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        timeout: int = 40,
        **kwargs,
    ) -> ScrapeResult:

        try:
            stealth = get_stealth_config()

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    head **less=True,
                    args=["--disable-blink-features=AutomationControlled"],
                )

                context = await browser.new_context(
                    viewport=stealth["viewport"],
                    user_agent=get_random_user_agent(),
                    locale=stealth["locale"],
                    timezone_id=stealth["timezone"],
                )

                page = await context.new_page()
                await asyncio.sleep(random.uniform(1.0, 2.0))
                await page.goto(url, timeout=timeout * 1000, wait_until="networkidle")

                await human_like_delay(800, 2000)
                await random_mouse_move(page)

                html = await page.content()
                markdown = trafilatura.extract(html) or ""

                if not markdown.strip():
                    return ScrapeResult(
                        success=False,
                        status="failed",
                        strategy_used="stealth",
                        failure_reason=ScrapeFailureReason.ANTI_BOT_SUSPECTED,
                        failure_message="Page rendered but content blocked",
                    )

                screenshot_dir = "/app/data/artifacts/screenshots"
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = f"{screenshot_dir}/{job_id}_stealth.png"
                await page.screenshot(path=screenshot_path, full_page=True)

                await browser.close()

                return ScrapeResult(
                    success=True,
                    status="success",
                    strategy_used="stealth",
                    data={"_raw_markdown": markdown},
                    screenshots=[screenshot_path],
                    confidence=90.0,
                    metadata={"engine": "stealth"},
                )

        except Exception as e:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="stealth",
                failure_reason=ScrapeFailureReason.ANTI_BOT_SUSPECTED,
                failure_message=str(e),
                errors=[str(e)],
            )
