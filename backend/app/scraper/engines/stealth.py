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
from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.processing.field_extractor import extract_fields



class StealthStrategy(BaseScraper):
    """
    Stealth browser strategy with anti-bot evasion.
    Used as LAST fallback.
    """

    def get_name(self) -> str:
        return "stealth"

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

        await self.throttle(url)

        stealth_config = get_stealth_config()
        screenshot_path = None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                    ],
                )

                context = await browser.new_context(
                    viewport=stealth_config["viewport"],
                    user_agent=get_random_user_agent(),
                    locale=stealth_config["locale"],
                    timezone_id=stealth_config["timezone"],
                )

                # Stealth JS injections
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [{ name: 'Chrome PDF Viewer' }]
                    });
                    window.chrome = { runtime: {} };
                """)

                page = await context.new_page()

                # Human-like delay
                await asyncio.sleep(random.uniform(1.0, 2.5))

                await page.goto(
                    url,
                    timeout=timeout * 1000,
                    wait_until="networkidle",
                )

                await human_like_delay(800, 2000)
                await random_mouse_move(page)

                if wait_for_selector:
                    try:
                        await page.wait_for_selector(wait_for_selector, timeout=10_000)
                    except Exception:
                        pass

                html = await page.content()

                # Screenshot
                screenshots_dir = os.path.join(
                    os.getcwd(), "data", "artifacts", "screenshots"
                )
                os.makedirs(screenshots_dir, exist_ok=True)
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(
                    screenshots_dir, f"stealth_{timestamp}.png"
                )
                await page.screenshot(path=screenshot_path, full_page=True)

                markdown = trafilatura.extract(
                    html,
                    output_format="markdown",
                    include_links=True,
                    include_tables=True,
                ) or ""

                await context.close()
                await browser.close()

                if not markdown.strip():
                    return ScrapeResult(
                        success=False,
                        status="failed",
                        strategy_used="stealth",
                        failure_reason=ScrapeFailureReason.EMPTY_DATA,
                        failure_message="No extractable content found",
                    )

                return ScrapeResult(
                    success=True,
                    status="success",
                    strategy_used="stealth",
                    data={
                        "_raw_markdown": markdown,
                        "_strategy": "stealth",
                    },
                    confidence=0.85,
                    screenshots=[screenshot_path] if screenshot_path else [],
                )

        except asyncio.TimeoutError:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="stealth",
                failure_reason=ScrapeFailureReason.JS_TIMEOUT,
                failure_message="Page load timed out",
            )

        except Exception as e:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="stealth",
                failure_reason=ScrapeFailureReason.UNKNOWN,
                failure_message=str(e),
            )
