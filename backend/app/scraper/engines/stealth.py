import asyncio
import random
import os
from datetime import datetime
from typing import Tuple, Optional

import trafilatura
from playwright.async_api import async_playwright

from app.scraper.logic.base import BaseScraper
from app.scraper.antibot.fingerprint import get_stealth_config
from app.scraper.antibot.delays import human_like_delay, random_mouse_move
from app.scraper.antibot.headers import get_random_user_agent


class StealthStrategy(BaseScraper):
    """
    Stealth browser strategy with anti-bot evasion.
    Best for protected websites.
    """

    def get_name(self) -> str:
        return "stealth"

    def can_handle(self, url: str) -> bool:
        # Used for protected / bot-detected sites
        return True

    async def fetch(
        self,
        url: str,
        timeout: int = 30,
        wait_for_selector: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, str, Optional[str]]:

        screenshot_path = None
        stealth_config = get_stealth_config()

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

            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [{ name: 'Chrome PDF Viewer' }]
                });
                window.chrome = { runtime: {} };
            """)

            page = await context.new_page()

            try:
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
                )

                return markdown or "", html, screenshot_path

            finally:
                await context.close()
                await browser.close()
