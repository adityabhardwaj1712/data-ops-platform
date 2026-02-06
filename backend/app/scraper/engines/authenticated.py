"""
Authenticated Scraper - Login-required scraping

Handles scraping behind authentication walls using cookies, form login, or API tokens.
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult, ScrapeFailureReason, AuthConfig, AuthMethod
from app.scraper.engines.browser import BrowserStrategy

logger = logging.getLogger(__name__)


class AuthenticatedScraper(BaseScraper):
    """
    Scrape content behind login walls.
    
    WARNING: Only use with explicit permission. Violating ToS may have legal consequences.
    """
    
    def __init__(self):
        self.browser_strategy = BrowserStrategy()
    
    def get_name(self) -> str:
        return "authenticated"
    
    def can_handle(self, url: str) -> bool:
        """Requires explicit strategy selection"""
        return False  # Never auto-select authenticated scraping
    
    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs
    ) -> ScrapeResult:
        """
        Scrape authenticated content
        
        Args:
            url: Target URL (behind login)
            schema: Data extraction schema
            job_id: Job identifier
            **kwargs: Must include 'auth_config' (AuthConfig object)
        """
        logger.warning(f"Starting authenticated scrape for {url} - ensure you have permission!")
        
        auth_config: AuthConfig = kwargs.get('auth_config')
        if not auth_config:
            return self.failure(
                reason=ScrapeFailureReason.VALIDATION_FAILED,
                message="auth_config is required for authenticated scraping"
            )
        
        try:
            # Authenticate based on method
            if auth_config.method == AuthMethod.COOKIES:
                return await self._scrape_with_cookies(url, schema, auth_config, **kwargs)
            
            elif auth_config.method == AuthMethod.FORM_LOGIN:
                return await self._scrape_with_form_login(url, schema, auth_config, **kwargs)
            
            elif auth_config.method in [AuthMethod.API_TOKEN, AuthMethod.BEARER]:
                return await self._scrape_with_token(url, schema, auth_config, **kwargs)
            
            else:
                return self.failure(
                    reason=ScrapeFailureReason.VALIDATION_FAILED,
                    message=f"Unsupported auth method: {auth_config.method}"
                )
            
        except Exception as e:
            logger.error(f"Authenticated scraping failed: {e}", exc_info=True)
            return self.failure(
                reason=ScrapeFailureReason.UNKNOWN,
                message=f"Authentication error: {str(e)}",
                errors=[str(e)]
            )
    
    async def _scrape_with_cookies(
        self,
        url: str,
        schema: Dict[str, Any],
        auth_config: AuthConfig,
        **kwargs
    ) -> ScrapeResult:
        """Scrape using pre-existing cookies"""
        if not auth_config.cookies:
            return self.failure(
                reason=ScrapeFailureReason.VALIDATION_FAILED,
                message="Cookies required for cookie-based auth"
            )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # Add cookies
            await context.add_cookies(auth_config.cookies)
            
            page = await context.new_page()
            
            try:
                # Navigate to target page
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)  # Wait for dynamic content
                
                # Extract data
                html = await page.content()
                data = self._extract_from_html(html, schema)
                
                return ScrapeResult(
                    success=True,
                    status="success",
                    data=data,
                    strategy_used=self.get_name(),
                    confidence=0.85,
                    metadata={
                        "auth_method": "cookies",
                        "url": url
                    }
                )
                
            finally:
                await browser.close()
    
    async def _scrape_with_form_login(
        self,
        url: str,
        schema: Dict[str, Any],
        auth_config: AuthConfig,
        **kwargs
    ) -> ScrapeResult:
        """Scrape after logging in via form"""
        if not auth_config.login_url or not auth_config.credentials:
            return self.failure(
                reason=ScrapeFailureReason.VALIDATION_FAILED,
                message="login_url and credentials required for form login"
            )
        
        username = auth_config.credentials.get('username')
        password = auth_config.credentials.get('password')
        
        if not username or not password:
            return self.failure(
                reason=ScrapeFailureReason.VALIDATION_FAILED,
                message="username and password required"
            )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to login page
                logger.info(f"Navigating to login page: {auth_config.login_url}")
                await page.goto(auth_config.login_url, wait_until="domcontentloaded")
                
                # Fill login form (common selectors)
                username_selectors = [
                    'input[name="username"]',
                    'input[name="email"]',
                    'input[type="email"]',
                    'input[id="username"]',
                    'input[id="email"]'
                ]
                
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[id="password"]'
                ]
                
                # Try to find and fill username field
                for selector in username_selectors:
                    try:
                        await page.fill(selector, username, timeout=2000)
                        logger.info(f"Filled username with selector: {selector}")
                        break
                    except:
                        continue
                
                # Try to find and fill password field
                for selector in password_selectors:
                    try:
                        await page.fill(selector, password, timeout=2000)
                        logger.info(f"Filled password with selector: {selector}")
                        break
                    except:
                        continue
                
                # Submit form
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Log in")',
                    'button:has-text("Sign in")'
                ]
                
                for selector in submit_selectors:
                    try:
                        await page.click(selector, timeout=2000)
                        logger.info(f"Clicked submit with selector: {selector}")
                        break
                    except:
                        continue
                
                # Wait for navigation after login
                await page.wait_for_timeout(3000)
                
                # Navigate to target page
                logger.info(f"Navigating to target page: {url}")
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                
                # Extract data
                html = await page.content()
                data = self._extract_from_html(html, schema)
                
                return ScrapeResult(
                    success=True,
                    status="success",
                    data=data,
                    strategy_used=self.get_name(),
                    confidence=0.80,
                    metadata={
                        "auth_method": "form_login",
                        "url": url
                    }
                )
                
            finally:
                await browser.close()
    
    async def _scrape_with_token(
        self,
        url: str,
        schema: Dict[str, Any],
        auth_config: AuthConfig,
        **kwargs
    ) -> ScrapeResult:
        """Scrape using API token or Bearer token"""
        import httpx
        from bs4 import BeautifulSoup
        
        if not auth_config.credentials:
            return self.failure(
                reason=ScrapeFailureReason.VALIDATION_FAILED,
                message="credentials required for token auth"
            )
        
        token = auth_config.credentials.get('token') or auth_config.credentials.get('api_key')
        
        if not token:
            return self.failure(
                reason=ScrapeFailureReason.VALIDATION_FAILED,
                message="token or api_key required in credentials"
            )
        
        # Build headers
        headers = auth_config.headers or {}
        
        if auth_config.method == AuthMethod.BEARER:
            headers['Authorization'] = f'Bearer {token}'
        elif auth_config.method == AuthMethod.API_TOKEN:
            headers['X-API-Key'] = token
        
        # Fetch page
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            html = response.text
            data = self._extract_from_html(html, schema)
            
            return ScrapeResult(
                success=True,
                status="success",
                data=data,
                strategy_used=self.get_name(),
                confidence=0.90,
                metadata={
                    "auth_method": auth_config.method.value,
                    "url": url
                }
            )
    
    def _extract_from_html(
        self,
        html: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract data from HTML using schema"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'lxml')
        extracted = {}
        
        for field_name, selector in schema.items():
            try:
                element = soup.select_one(selector)
                if element:
                    extracted[field_name] = element.get_text().strip()
                else:
                    extracted[field_name] = None
            except Exception as e:
                logger.debug(f"Failed to extract {field_name}: {e}")
                extracted[field_name] = None
        
        return extracted
