"""
Scrape Job Executor
Lazy-loads heavy scraping dependencies only when needed
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ScrapeExecutor:
    """
    Executes scraping jobs with lazy-loaded dependencies.
    
    Heavy libraries are imported only when this executor is first used.
    """
    
    def __init__(self):
        self._engine = None
    
    def _load_engine(self):
        """Lazy-load the scraper engine (HEAVY)."""
        if self._engine is None:
            logger.info("Loading scraper engine (heavy dependencies)...")
            
            # Import heavy libraries only when needed
            from app.scraper.engine import ScraperEngine
            self._engine = ScraperEngine()
            
            logger.info("Scraper engine loaded successfully")
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a scraping job.
        
        Args:
            payload: Job payload containing:
                - url: Target URL
                - schema: Expected data schema
                - prompt: Optional extraction prompt
                - strategy: Scraping strategy (auto/static/browser/stealth)
                - Other scraping options
        
        Returns:
            Scraping result with extracted data
        """
        # Lazy-load engine on first use
        self._load_engine()
        
        # Extract parameters from payload
        url = payload.get("url")
        schema = payload.get("schema", {})
        prompt = payload.get("prompt")
        strategy = payload.get("strategy", "auto")
        max_pages = payload.get("max_pages", 1)
        stealth_mode = payload.get("stealth_mode", False)
        use_proxy = payload.get("use_proxy", False)
        wait_for_selector = payload.get("wait_for_selector")
        timeout = payload.get("timeout", 30)
        
        logger.info(f"Executing scrape job for URL: {url}")
        
        # Execute scraping
        result = await self._engine.scrape(
            url=url,
            schema=schema,
            prompt=prompt,
            strategy=strategy,
            max_pages=max_pages,
            stealth_mode=stealth_mode,
            use_proxy=use_proxy,
            wait_for_selector=wait_for_selector,
            timeout=timeout
        )
        
        # Convert ScrapeResult to dict
        result_dict = {
            "success": result.success,
            "data": result.data,
            "pages_scraped": result.pages_scraped,
            "strategy_used": result.strategy_used,
            "confidence": result.confidence,
            "screenshots": result.screenshots,
            "errors": result.errors,
            "metadata": result.metadata
        }
        
        logger.info(f"Scrape job completed: success={result.success}, confidence={result.confidence}")
        
        return result_dict
