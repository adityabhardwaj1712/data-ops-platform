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
from app.scraper.engines.base import BaseStrategy
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
            
            # Add stealth scripts to bypass detection (Pro-Grade Evasion)
            await context.add_init_script("""
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Poison Canvas Fingerprinting
                const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
                CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
                    const result = originalGetImageData.apply(this, arguments);
                    result.data[0] = result.data[0] + (Math.random() > 0.5 ? 1 : -1);
                    return result;
                };

                // Override navigator.plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        { name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer' },
                        { name: 'YouTube Plug-in', filename: 'internal-youtube-plugin' }
                    ]
                });
                
                // Override navigator.languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Override chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // WebGL Fingerprint Poisoning
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Open Source Technology Center';
                    if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 520 (Skylake GT2)';
                    return getParameter.apply(this, arguments);
                };
            """)
            
            page = await context.new_page()
            
            try:
                # Random delay before navigation (human behavior)
                await asyncio.sleep(random.uniform(1.0, 2.5))
                
                # Navigate to page
                await page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
                
                # Simulate human-like behavior
                await human_like_delay(1000, 3000)
                await random_mouse_move(page)
                
                # Random scroll (human behavior)
                scroll_y = random.randint(300, 800)
                await page.evaluate(f"window.scrollTo(0, {scroll_y})")
                await human_like_delay(500, 1500)
                
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
