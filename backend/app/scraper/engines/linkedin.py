import asyncio
import os
import random
import json
from typing import Dict, Any, Optional
from datetime import datetime

from playwright.async_api import async_playwright
import trafilatura

from app.scraper.engines.stealth import StealthStrategy
from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.antibot.headers import get_random_user_agent
from app.scraper.antibot.delays import human_like_delay, random_mouse_move
from app.scraper.processing.field_extractor import extract_fields

class LinkedInScraper(StealthStrategy):
    """
    Specialized scraper for LinkedIn.
    Handles login, session persistence, and anti-bot.
    """

    def get_name(self) -> str:
        return "linkedin"

    def can_handle(self, url: str) -> bool:
        return "linkedin.com" in url.lower()

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        timeout: int = 60,
        wait_for_selector: Optional[str] = None,
        login: bool = False,
        **kwargs,
    ) -> ScrapeResult:
        
        # LinkedIn is very aggressive, needs longer timeouts and more stealth
        await self.throttle(url)
        
        session_file = os.path.join(os.getcwd(), "data", "sessions", "linkedin_session.json")
        os.makedirs(os.path.dirname(session_file), exist_ok=True)
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-infobars",
                    ],
                )
                
                # Try to load existing session
                context_args = {
                    "user_agent": get_random_user_agent(),
                    "viewport": {"width": 1366, "height": 768},
                    "locale": "en-US",
                }
                
                if os.path.exists(session_file):
                    context = await browser.new_context(storage_state=session_file, **context_args)
                else:
                    context = await browser.new_context(**context_args)
                
                page = await context.new_page()
                
                # Check if we need to login
                if login:
                    await page.goto("https://www.linkedin.com/login", wait_until="networkidle")
                    
                    # Check if already logged in by checking for search bar or something
                    if await page.query_selector(".global-nav__search") is None:
                        user = os.getenv("LINKEDIN_USER")
                        pw = os.getenv("LINKEDIN_PASS")
                        
                        if user and pw:
                            await page.fill("#username", user)
                            await page.fill("#password", pw)
                            await page.click("button[type=submit]")
                            await page.wait_for_timeout(5000)
                            
                            # Save session
                            await context.storage_state(path=session_file)
                
                # Navigate to target URL
                await page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
                await human_like_delay(2000, 5000)
                
                # Human-like scrolling
                for _ in range(3):
                    await page.mouse.wheel(0, random.randint(300, 700))
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=15000)
                
                html = await page.content()
                
                # Screenshot
                screenshots_dir = os.path.join(os.getcwd(), "data", "artifacts", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshots_dir, f"linkedin_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                
                extracted = await extract_fields(html, schema) if schema else {}
                
                await context.close()
                await browser.close()
                
                return ScrapeResult(
                    success=True,
                    status="success",
                    strategy_used="linkedin",
                    data=extracted,
                    confidence=0.9,
                    screenshots=[screenshot_path],
                )
                
        except Exception as e:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="linkedin",
                failure_reason=ScrapeFailureReason.UNKNOWN,
                failure_message=str(e),
            )
