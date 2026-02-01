import asyncio
import os
import random
from datetime import datetime
from typing import Tuple, Optional

import trafilatura
from playwright.async_api import async_playwright

from app.scraper.logic.base import BaseScraper


class BrowserStrategy(BaseScraper):
    """
    Full browser rendering using Playwright.
    Optimized for JS-heavy websites.
    """

    def get_name(self) -> str:
        return "browser"

    def can_handle(self, url: str) -> bool:
        # Browser can handle any URL, but is slower than static
        return True

    async def fetch(
        self,
        url: str,
        timeout: int = 30,
        wait_for_selector: Optional[str] = None,
        take_screenshot: bool = False,
        wait_until: str = "domcontentloaded",
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

            try:
                await asyncio.sleep(random.uniform(0.5, 1.5))

                await page.goto(
                    url,
                    timeout=timeout * 1000,
                    wait_until=wait_until,
                )

                if wait_for_selector:
                    try:
                        await page.wait_for_selector(wait_for_selector, timeout=10_000)
                    except Exception:
                        pass

                await page.mouse.move(
                    random.randint(0, width),
                    random.randint(0, height),
                )

                html = await page.content()

                if take_screenshot:
                    screenshots_dir = os.path.join(
                        os.getcwd(), "data", "artifacts", "snapshots"
                    )
                    os.makedirs(screenshots_dir, exist_ok=True)
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = os.path.join(
                        screenshots_dir, f"snap_{timestamp}.png"
                    )
                    await page.screenshot(path=screenshot_path)

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
