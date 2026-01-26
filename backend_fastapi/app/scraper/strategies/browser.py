"""
Browser Strategy
Playwright-based rendering (SAFE for Docker / WSL)
"""
import asyncio
import os
from datetime import datetime
from typing import Tuple, Optional

import trafilatura
from playwright.async_api import async_playwright

from app.scraper.strategies.base import BaseStrategy


class BrowserStrategy(BaseStrategy):
    """
    Full browser rendering using Playwright.
    Enabled only when explicitly needed.
    """

    def get_name(self) -> str:
        return "browser"

    async def fetch(
        self,
        url: str,
        timeout: int = 30,
        wait_for_selector: Optional[str] = None,
        take_screenshot: bool = False,
        **kwargs
    ) -> Tuple[str, str, Optional[str]]:

        screenshot_path = None

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--disable-background-networking",
                    "--disable-sync",
                    "--no-first-run",
                    "--single-process",
                ],
            )

            context = await browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )

            page = await context.new_page()

            try:
                await page.goto(
                    url,
                    timeout=timeout * 1000,
                    wait_until="domcontentloaded",
                )

                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=10_000)

                await asyncio.sleep(0.5)

                html = await page.content()

                if take_screenshot:
                    screenshots_dir = os.path.join(os.getcwd(), "data", "screenshots")
                    os.makedirs(screenshots_dir, exist_ok=True)
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = os.path.join(
                        screenshots_dir, f"scrape_{timestamp}.png"
                    )
                    await page.screenshot(path=screenshot_path, full_page=False)

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

