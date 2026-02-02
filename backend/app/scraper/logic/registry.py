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
        """
        Select first scraper that can handle the URL.
        can_handle() is SYNC by design.
        """
        for scraper in self._scrapers:
            try:
                if scraper.can_handle(url):
                    logger.info(
                        f"Selected scraper {scraper.__class__.__name__} for {url}"
                    )
                    return scraper
            except Exception as e:
                logger.warning(
                    f"Scraper {scraper.__class__.__name__} can_handle() failed: {e}"
                )

        if self._default_scraper:
            logger.info(
                f"No specialized scraper found for {url}. "
                f"Using default scraper: {self._default_scraper.__class__.__name__}"
            )
            return self._default_scraper

        raise ValueError("No suitable scraper found.")


# -------------------------------------------------
# Registry initialization
# -------------------------------------------------

scraper_registry = ScraperRegistry()


def initialize_scrapers():
    """
    Order matters:
    static → browser → stealth → domain → generic
    """
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


initialize_scrapers()
