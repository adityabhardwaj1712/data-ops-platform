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

    async def run_with_fallback(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs,
    ):
        """
        Runs scrapers in order until one succeeds.
        Static -> Browser -> Stealth
        """
        last_error = None
        attempted_strategies = []

        for scraper in self._scrapers:
            try:
                if not scraper.can_handle(url):
                    continue

                logger.info(f"Attempting {scraper.get_name()} for {url}")
                attempted_strategies.append(scraper.get_name())
                
                result = await scraper.scrape(
                    url=url,
                    schema=schema,
                    job_id=job_id,
                    **kwargs,
                )

                if result.success:
                    if result.metadata is None:
                        result.metadata = {}
                    result.metadata["attempted_strategies"] = attempted_strategies
                    return result

                last_error = result.failure_message
                logger.warning(f"{scraper.get_name()} failed: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"Error in {scraper.get_name()}: {last_error}")

        raise RuntimeError(f"All strategies failed: {last_error}")


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
    from app.scraper.engines.linkedin import LinkedInScraper
    from app.scraper.logic.product import ProductScraper
    from app.scraper.logic.generic import GenericScraper

    scraper_registry.register(LinkedInScraper())
    scraper_registry.register(StaticStrategy())
    scraper_registry.register(BrowserStrategy())
    scraper_registry.register(StealthStrategy())
    scraper_registry.register(ProductScraper())
    scraper_registry.register(GenericScraper(), is_default=True)


initialize_scrapers()
