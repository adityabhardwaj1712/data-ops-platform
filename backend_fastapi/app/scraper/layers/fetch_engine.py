"""
LAYER 2 - FETCH ENGINE
Gets the page HTML without any parsing

KEY RULE:
❌ No parsing here
❌ No logic here
✅ Just return HTML

This makes the system stable.
"""
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import httpx
from playwright.async_api import async_playwright

from app.scraper.antibot.headers import get_random_headers
from app.scraper.antibot.fingerprint import get_stealth_config
from app.scraper.antibot.delays import human_like_delay
from app.scraper.controller import scrape_controller
from app.db.session import async_session_factory
from app.db.source_health import SourceHealth
from app.scraper.antibot.proxies import proxy_manager
from app.scraper.antibot.captcha import captcha_detector
from sqlalchemy import select
import time
import random
import asyncio


class FetchMethod(str, Enum):
    STATIC = "static"
    BROWSER = "browser"
    STEALTH = "stealth"
    REQUESTS = "requests"  # Legacy/Simple fallback


@dataclass
class FetchResult:
    """Raw fetch result - HTML only"""
    success: bool
    html: str = ""
    status_code: int = 0
    url: str = ""
    method_used: FetchMethod = FetchMethod.STATIC
    is_captcha: bool = False
    captcha_type: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FetchEngine:
    """
    Layer 2 - Fetch Engine
    
    ONLY fetches HTML. No parsing, no extraction.
    This separation ensures stability.
    
    Integrated with:
    - ScrapeController: Concurrency & Rate limiting
    - SourceHealth: Health tracking per domain
    """
    
    def __init__(self):
        self.timeout = 30
    
    async def fetch(
        self,
        url: str,
        method: FetchMethod = FetchMethod.STATIC,
        timeout: int = 30
    ) -> FetchResult:
        """
        Fetch a URL and return raw HTML with controller protection.
        """
        self.timeout = timeout
        start_time = time.time()
        
        try:
            # Wrap fetch logic with ScrapeController
            result = await scrape_controller.execute(
                url,
                self._do_fetch,
                method
            )
            
            # Record success in SourceHealth
            duration_ms = (time.time() - start_time) * 1000
            await self._update_health(url, True, duration_ms, len(result.html) if result.success else 0)
            
            return result
            
        except Exception as e:
            # Record failure in SourceHealth
            await self._update_health(url, False)
            
            return FetchResult(
                success=False,
                url=url,
                method_used=method,
                error=str(e)
            )

    async def _do_fetch(self, url: str, method: FetchMethod) -> FetchResult:
        """The actual fetch logic (called by controller)"""
        if method == FetchMethod.STATIC:
            return await self._fetch_static(url)
        elif method == FetchMethod.BROWSER:
            return await self._fetch_browser(url)
        elif method == FetchMethod.STEALTH:
            return await self._fetch_stealth(url)
        else:
            return await self._fetch_legacy(url)

    async def _update_health(self, url: str, success: bool, duration_ms: float = None, size: int = None):
        """Update domain health in database"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        async with async_session_factory() as db:
            result = await db.execute(select(SourceHealth).where(SourceHealth.domain == domain))
            health = result.scalar_one_or_none()
            
            if not health:
                health = SourceHealth(domain=domain)
                db.add(health)
            
            health.update_stats(success, duration_ms, size)
            await db.commit()
    
    async def _fetch_static(self, url: str) -> FetchResult:
        """
        Fast HTTP fetch using httpx.
        Best for static sites without JavaScript.
        """
        headers = get_random_headers()
        
        # PRO: Proxy Rotation
        proxy = proxy_manager.get_proxy(urlparse(url).netloc)
        proxies = {"http://": proxy, "https://": proxy} if proxy else None
        
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            http2=True,
            proxies=proxies
        ) as client:
            try:
                response = await client.get(url, headers=headers)
                
                # PRO: CAPTCHA Detection
                is_blocked = captcha_detector.is_captcha(response.text)
                captcha_type = captcha_detector.get_type(response.text) if is_blocked else None
                
                if is_blocked and proxy:
                    proxy_manager.report_failure(proxy)
                elif not is_blocked and proxy:
                    proxy_manager.report_success(proxy)
                
                return FetchResult(
                    success=response.status_code == 200 and not is_blocked,
                    html=response.text,
                    status_code=response.status_code,
                    url=str(response.url),
                    method_used=FetchMethod.STATIC,
                    is_captcha=is_blocked,
                    captcha_type=captcha_type,
                    metadata={
                        "content_type": response.headers.get("content-type", ""),
                        "content_length": len(response.text),
                        "proxy_used": proxy is not None,
                        "blocked_by_captcha": is_blocked
                    }
                )
            except Exception as e:
                if proxy:
                    proxy_manager.report_failure(proxy)
                raise e
            
    async def _fetch_legacy(self, url: str) -> FetchResult:
        """
        Legacy fetch using the 'requests' library.
        Simple, synchronous (wrapped in thread), good for basic sites.
        """
        import requests
        import asyncio
        
        headers = get_random_headers()
        
        # Run synchronous requests in a thread to keep it async-friendly
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(url, headers=headers, timeout=self.timeout)
            )
            
            return FetchResult(
                success=response.status_code == 200,
                html=response.text,
                status_code=response.status_code,
                url=response.url,
                method_used=FetchMethod.REQUESTS,
                metadata={
                    "content_length": len(response.text),
                    "library": "requests"
                }
            )
        except Exception as e:
            raise e
    
    async def _fetch_browser(self, url: str) -> FetchResult:
        """
        Browser fetch using Playwright.
        For JavaScript-heavy sites.
        """
        # PRO: Proxy Rotation
        proxy = proxy_manager.get_proxy(urlparse(url).netloc)
        proxy_config = {"server": proxy} if proxy else None
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                proxy=proxy_config
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=get_random_headers()["User-Agent"]
            )
            page = await context.new_page()
            
            try:
                response = await page.goto(
                    url,
                    timeout=self.timeout * 1000,
                    wait_until="networkidle"
                )
                
                html = await page.content()
                
                # PRO: CAPTCHA Detection
                is_blocked = captcha_detector.is_captcha(html)
                
                if is_blocked and proxy:
                    proxy_manager.report_failure(proxy)
                elif not is_blocked and proxy:
                    proxy_manager.report_success(proxy)
                
                return FetchResult(
                    success=response.status == 200 if (response and not is_blocked) else False,
                    html=html,
                    status_code=response.status if response else 0,
                    url=page.url,
                    method_used=FetchMethod.BROWSER,
                    is_captcha=is_blocked,
                    captcha_type=captcha_detector.get_type(html) if is_blocked else None,
                    metadata={
                        "final_url": page.url,
                        "content_length": len(html),
                        "proxy_used": proxy is not None
                    }
                )
            except Exception as e:
                if proxy:
                    proxy_manager.report_failure(proxy)
                raise e
            finally:
                await browser.close()
    
    async def _fetch_stealth(self, url: str) -> FetchResult:
        """
        Stealth browser fetch with anti-bot evasion.
        For protected sites.
        """
        config = get_stealth_config()
        
        # PRO: Proxy Rotation
        proxy = proxy_manager.get_proxy(urlparse(url).netloc)
        proxy_config = {"server": proxy} if proxy else None
        
        # PRO: Deep Fingerprinting
        from app.scraper.antibot.fingerprint import get_hardware_config, get_webgl_fingerprint
        hw = get_hardware_config()
        gl = get_webgl_fingerprint()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                proxy=proxy_config,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            context = await browser.new_context(
                viewport=config["viewport"],
                user_agent=get_random_headers()["User-Agent"],
                locale=config["locale"],
                timezone_id=config["timezone"]
            )
            
            # Inject anti-detection scripts (Stealth 2.0)
            await context.add_init_script(f"""
                Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
                Object.defineProperty(navigator, 'deviceMemory', {{get: () => {hw['memory']}}});
                Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {hw['cpu']}}});
                Object.defineProperty(navigator, 'platform', {{get: () => '{hw['platform']}'}});
                
                // WebGL spoofing
                const getParameter = HTMLCanvasElement.prototype.getContext('2d').constructor.prototype.getParameter;
                HTMLCanvasElement.prototype.getContext('webgl').constructor.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) return '{gl['vendor']}';
                    if (parameter === 37446) return '{gl['renderer']}';
                    return getParameter(parameter);
                }};

                // Mock battery status
                navigator.getBattery = () => Promise.resolve({{
                    charging: {str(hw['is_charging']).lower()},
                    level: {hw['battery_level']},
                    chargingTime: 0,
                    dischargingTime: Infinity
                }});
                
                window.chrome = {{runtime: {{}}}};
            """)
            
            page = await context.new_page()
            
            try:
                # --- STEALTH 2.0: Human-like behavior ---
                await human_like_delay(0.5, 1.5)
                
                # Random mouse movements (simulation)
                await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                
                response = await page.goto(
                    url,
                    timeout=self.timeout * 1000,
                    wait_until="domcontentloaded"
                )
                
                # Humanized interactions
                await page.mouse.wheel(0, random.randint(300, 700))
                await human_like_delay(1, 2)
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                html = await page.content()
                
                # PRO: CAPTCHA Detection
                is_blocked = captcha_detector.is_captcha(html)
                
                if is_blocked and proxy:
                    proxy_manager.report_failure(proxy)
                elif not is_blocked and proxy:
                    proxy_manager.report_success(proxy)
                
                return FetchResult(
                    success=response.status == 200 if (response and not is_blocked) else False,
                    html=html,
                    status_code=response.status if response else 0,
                    url=page.url,
                    method_used=FetchMethod.STEALTH,
                    is_captcha=is_blocked,
                    captcha_type=captcha_detector.get_type(html) if is_blocked else None,
                    metadata={
                        "final_url": page.url,
                        "content_length": len(html),
                        "proxy_used": proxy is not None,
                        "stealth_2_0": True
                    }
                )
            except Exception as e:
                if proxy:
                    proxy_manager.report_failure(proxy)
                raise e
            finally:
                await browser.close()
    
    def detect_method(self, url: str) -> FetchMethod:
        """
        Auto-detect the best fetch method for a URL.
        """
        # Sites that need browser
        js_sites = [
            'linkedin.com', 'twitter.com', 'x.com',
            'facebook.com', 'instagram.com'
        ]
        
        # Sites that need stealth
        protected_sites = [
            'amazon.', 'glassdoor.', 'zillow.',
            'cloudflare'
        ]
        
        url_lower = url.lower()
        
        for site in protected_sites:
            if site in url_lower:
                return FetchMethod.STEALTH
        
        for site in js_sites:
            if site in url_lower:
                return FetchMethod.BROWSER
        
        return FetchMethod.STATIC
