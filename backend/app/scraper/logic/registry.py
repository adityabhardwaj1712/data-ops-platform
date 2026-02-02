import logging
from typing import Dict, Any, List, Optional

from app.scraper.logic.base import BaseScraper

logger = logging.getLogger(__name__)


class ScraperRegistry:
    def __init__(self) -> None:
        self._scrapers: List[BaseScraper] = []
        self._default_scraper: Optional[BaseScraper] = None

    def register(self, scraper: BaseScraper, is_default: bool = False) -> None:
        """
        Register a scraper strategy.
        Order matters (first match wins).
        """
        self._scrapers.append(scraper)

        if is_default:
            self._default_scraper = scraper

        logger.info("Registered scraper: %s", scraper.__class__.__name__)

    async def run_with_fallback(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs: Any,
    ):
        """
        Runs scrapers in order until one succeeds.
        Strategy order:
        static → browser → stealth → domain → generic
        """
        last_error: Optional[str] = None
        attempted_strategies: List[str] = []

        for scraper in self._scrapers:
            if not scraper.can_handle(url):
                continue

            strategy_name = scraper.get_name()
            attempted_strategies.append(strategy_name)

            logger.info("Attempting %s for %s", strategy_name, url)

            try:
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
                logger.warning("%s failed: %s", strategy_name, last_error)

            except Exception as exc:
                last_error = str(exc)
                logger.exception(
                    "Unhandled error in %s for %s", strategy_name, url
                )

        # Fallback to default scraper if defined
        if self._default_scraper:
            logger.warning(
                "All strategies failed. Falling back to default scraper: %s",
                self._default_scraper.get_name(),
            )

            result = await self._default_scraper.scrape(
                url=url,
                schema=schema,
                job_id=job_id,
                **kwargs,
            )

            if result.metadata is None:
                result.metadata = {}

            result.metadata["attempted_strategies"] = attempted_strategies + [
                self._default_scraper.get_name()
            ]
            return result

        raise RuntimeError(f"All scraping strategies failed: {last_error}")


# -------------------------------------------------
# Registry initialization
# -------------------------------------------------

scraper_registry = ScraperRegistry()


def initialize_scrapers() -> None:
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
