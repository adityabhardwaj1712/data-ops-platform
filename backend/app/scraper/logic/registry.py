import logging
from typing import List, Optional
from app.scraper.logic.base import BaseScraper

logger = logging.getLogger(__name__)

class ScraperRegistry:
    def __init__(self):
        self._scrapers: List[BaseScraper] = []
        self._default_scraper: Optional[BaseScraper] = None

    def register(self, scraper: BaseScraper, is_default: bool = False):
        self._scrapers.append(scraper)
        if is_default:
            self._default_scraper = scraper
        logger.info(f"Registered scraper: {scraper.__class__.__name__}")

    async def get_scraper(self, url: str) -> BaseScraper:
        for scraper in self._scrapers:
            if await scraper.can_handle(url):
                return scraper
        
        # Fallback to default scraper if none specialized found
        if self._default_scraper:
            logger.info(f"No specialized scraper found for {url}. Using default scraper: {self._default_scraper.__class__.__name__}")
            return self._default_scraper
        
        # If no default scraper is registered, raise an error or return a generic one
        logger.error(f"No specialized scraper found for {url} and no default scraper registered.")
        raise ValueError("No suitable scraper found and no default scraper registered.")

scraper_registry = ScraperRegistry()

# Initialize registry
def initialize_scrapers():
    from app.scraper.engines.static import StaticStrategy
    from app.scraper.engines.browser import BrowserStrategy
    from app.scraper.engines.stealth import StealthStrategy
    from app.scraper.logic.product import ProductScraper
    from app.scraper.logic.generic import GenericScraper

    scraper_registry.register(StaticStrategy())
    scraper_registry.register(BrowserStrategy())
    scraper_registry.register(StealthStrategy())
    scraper_registry.register(ProductScraper())
    scraper_registry.register(GenericScraper(), is_default=True)

# Auto-initialize on import
initialize_scrapers()
