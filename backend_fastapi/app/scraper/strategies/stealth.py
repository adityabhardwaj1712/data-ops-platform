"""
Stealth Browser Strategy
Browser with anti-bot evasion techniques
Best for protected sites with bot detection
"""
import asyncio
import random
import trafilatura
from typing import Tuple, Optional
from playwright.async_api import async_playwright
from app.scraper.strategies.base import BaseStrategy
from app.scraper.antibot.fingerprint import get_stealth_config
from app.scraper.antibot.delays import human_like_delay, random_mouse_move
from app.scraper.antibot.headers import get_random_user_agent
import os
from datetime import datetime


class StealthStrategy(BaseStrategy):
    """
    Stealth browser strategy with anti-bot evasion.
    
    Techniques:
    - Randomized browser fingerprint
    - Human-like delays and mouse movements
    - Realistic user agent rotation
    - WebDriver detection bypass
    - Canvas/WebGL fingerprint randomization
    
    Best for:
    - Sites with Cloudflare/Akamai protection
    - LinkedIn, Amazon, Glassdoor
    - Any site with bot detection
    """
    
    def get_name(self) -> str:
        return "stealth"
    
    async def fetch(
        self,
        url: str,
        timeout: int = 30,
        wait_for_selector: Optional[str] = None,
        use_proxy: bool = False,
        **kwargs
    ) -> Tuple[str, str, Optional[str]]:
        """
        Fetch page content using stealth browser.
        
        Args:
            url: Target URL
            timeout: Page load timeout in seconds
            wait_for_selector: CSS selector to wait for before extraction
            use_proxy: Whether to use proxy rotation
            
        Returns:
            Tuple of (markdown_content, raw_html, screenshot_path)
        """
        screenshot_path = None
        stealth_config = get_stealth_config()
        
        async with async_playwright() as p:
            # Launch with stealth options
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # Create context with stealth settings
            context = await browser.new_context(
                viewport={
                    "width": stealth_config["viewport"]["width"],
                    "height": stealth_config["viewport"]["height"]
                },
                user_agent=get_random_user_agent(),
                locale=stealth_config["locale"],
                timezone_id=stealth_config["timezone"],
                geolocation=stealth_config.get("geolocation"),
                permissions=["geolocation"] if stealth_config.get("geolocation") else []
            )
            
            # Add stealth scripts to bypass detection
            await context.add_init_script("""
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override navigator.plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override navigator.languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Override chrome runtime
                window.chrome = {
                    runtime: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            page = await context.new_page()
            
            try:
                # Random delay before navigation (human behavior)
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # Navigate to page
                await page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                
                # Simulate human-like behavior
                await human_like_delay()
                await random_mouse_move(page)
                
                # Wait for network to settle
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                # Wait for specific selector if provided
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                
                # Random scroll (human behavior)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
                await human_like_delay()
                
                # Get page content
                html = await page.content()
                
                # Take screenshot
                screenshots_dir = os.path.join(os.getcwd(), "data", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(screenshots_dir, f"stealth_{timestamp}.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Extract markdown content
                markdown = trafilatura.extract(
                    html,
                    output_format="markdown",
                    include_links=True,
                    include_tables=True
                )
                
                return markdown or "", html, screenshot_path
                
            finally:
                await browser.close()
