import logging
import asyncio
from typing import Dict, Any, Optional
from app.scraper.logic.registry import scraper_registry, initialize_scrapers
from app.schemas import ScrapeResult

logger = logging.getLogger(__name__)

# Initialize scrapers on module load
initialize_scrapers()

class ScrapeExecutor:
    """
    Executes scraping jobs by selecting the appropriate scraper
    from the registry and running it.
    """
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = payload.get("url")
        schema = payload.get("schema", {})
        job_id = payload.get("job_id", "background_job")
        
        if not url:
            return {"success": False, "error": "No URL provided"}

        logger.info(f"Executing scrape job for URL: {url}")
        
        try:
            # 1. Get appropriate scraper from registry
            scraper = await scraper_registry.get_scraper(url)
            logger.info(f"Using scraper: {scraper.__class__.__name__}")
            
            # 2. Run the scraper
            result: ScrapeResult = await scraper.scrape(
                url=url,
                schema=schema,
                job_id=job_id,
                **payload # Pass all additional parameters
            )
            
            # 3. Return results as dict for the worker
            return result.model_dump()
            
        except Exception as e:
            logger.exception(f"ScrapeExecutor failed for {url}")
            return {
                "success": False,
                "error": str(e),
                "failure_reason": "executor_failed"
            }
