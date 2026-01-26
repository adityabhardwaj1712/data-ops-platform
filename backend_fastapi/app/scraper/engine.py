"""
Pro-Level Universal Scraper Engine
Auto-selects best strategy based on target URL and requirements
(Lazy-loads browser strategies to avoid heavy startup)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import re
from urllib.parse import urlparse

from app.schemas import ScrapeResult
from app.scraper.strategies.static import StaticStrategy
from app.scraper.extractors.auto import AutoExtractor
from app.scraper.llm_client import LLMClient


# Sites known to require special handling
BROWSER_REQUIRED_PATTERNS = [
    r'twitter\.com', r'x\.com',
    r'linkedin\.com',
    r'facebook\.com',
    r'instagram\.com',
    r'.*spa.*',
    r'react\.',
    r'angular\.'
]

STEALTH_REQUIRED_PATTERNS = [
    r'amazon\.',
    r'cloudflare',
    r'linkedin\.com',
    r'zillow\.com',
    r'glassdoor\.com'
]


@dataclass
class ScrapeConfig:
    url: str
    schema: Dict[str, Any]
    prompt: Optional[str] = None
    strategy: str = "auto"
    max_pages: int = 1
    stealth_mode: bool = False
    use_proxy: bool = False
    wait_for_selector: Optional[str] = None
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)


class ScraperEngine:
    """
    Universal scraper engine with lazy-loaded browser strategies.

    Strategies:
    - static  → lightweight, fast (default)
    - browser → Playwright (loaded only when needed)
    - stealth → Playwright + evasion (loaded only when needed)
    """

    def __init__(self):
        self.static_strategy = StaticStrategy()
        self.browser_strategy = None
        self.stealth_strategy = None

        self.extractor = AutoExtractor()
        self.llm_client = LLMClient()

    def _detect_strategy(self, url: str, stealth_mode: bool = False) -> str:
        if stealth_mode:
            return "stealth"

        domain = urlparse(url).netloc.lower()

        for pattern in STEALTH_REQUIRED_PATTERNS:
            if re.search(pattern, domain, re.IGNORECASE):
                return "stealth"

        for pattern in BROWSER_REQUIRED_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return "browser"

        return "static"

    def _load_browser(self):
        if not self.browser_strategy:
            from app.scraper.strategies.browser import BrowserStrategy
            self.browser_strategy = BrowserStrategy()

    def _load_stealth(self):
        if not self.stealth_strategy:
            from app.scraper.strategies.stealth import StealthStrategy
            self.stealth_strategy = StealthStrategy()

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        prompt: Optional[str] = None,
        strategy: str = "auto",
        max_pages: int = 1,
        stealth_mode: bool = False,
        use_proxy: bool = False,
        wait_for_selector: Optional[str] = None,
        timeout: int = 30
    ) -> ScrapeResult:

        errors: List[str] = []
        screenshots: List[str] = []

        if strategy == "auto":
            strategy = self._detect_strategy(url, stealth_mode)

        try:
            if strategy == "static":
                content, page_html = await self.static_strategy.fetch(
                    url=url,
                    timeout=timeout,
                    use_proxy=use_proxy
                )

            elif strategy == "browser":
                self._load_browser()
                content, page_html, screenshot = await self.browser_strategy.fetch(
                    url=url,
                    timeout=timeout,
                    wait_for_selector=wait_for_selector
                )
                if screenshot:
                    screenshots.append(screenshot)

            else:  # stealth
                self._load_stealth()
                content, page_html, screenshot = await self.stealth_strategy.fetch(
                    url=url,
                    timeout=timeout,
                    wait_for_selector=wait_for_selector,
                    use_proxy=use_proxy
                )
                if screenshot:
                    screenshots.append(screenshot)

            if not content:
                return ScrapeResult(
                    success=False,
                    strategy_used=strategy,
                    errors=["No content extracted"]
                )

            if prompt:
                extracted_data, confidence = await self.llm_client.extract(
                    content=content,
                    prompt=prompt,
                    schema=schema
                )
            else:
                extracted_data, confidence = await self.extractor.extract(
                    html=page_html,
                    markdown=content,
                    schema=schema
                )

            if not extracted_data:
                return ScrapeResult(
                    success=False,
                    strategy_used=strategy,
                    confidence=0.0,
                    errors=["Schema extraction failed"],
                    screenshots=screenshots
                )

            return ScrapeResult(
                success=True,
                data=extracted_data,
                pages_scraped=1,
                strategy_used=strategy,
                confidence=confidence,
                screenshots=screenshots,
                metadata={
                    "url": url,
                    "content_length": len(content)
                }
            )

        except Exception as e:
            errors.append(str(e))
            return ScrapeResult(
                success=False,
                strategy_used=strategy,
                errors=errors,
                screenshots=screenshots
            )

