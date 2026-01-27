"""
Pipeline Job Executor
Lazy-loads heavy pipeline dependencies only when needed
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """
    Executes full 6-layer pipeline jobs with lazy-loaded dependencies.
    """
    
    def __init__(self):
        self._pipeline = None
    
    def _load_pipeline(self):
        """Lazy-load the pipeline (HEAVY)."""
        if self._pipeline is None:
            logger.info("Loading scraper pipeline (heavy dependencies)...")
            
            # Import heavy libraries only when needed
            from app.scraper.layers.pipeline import ScraperPipeline
            self._pipeline = ScraperPipeline()
            
            logger.info("Scraper pipeline loaded successfully")
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a full pipeline job.
        
        Args:
            payload: Job payload containing:
                - what_i_want: Natural language description
                - from_where: List of URLs
                - schema: Expected data schema
                - extraction_mode: HEURISTIC or AI
                - max_pages_per_source: Max pages to scrape per URL
                - webhook_url: Optional webhook for results
        
        Returns:
            Pipeline result with extracted data
        """
        # Lazy-load pipeline on first use
        self._load_pipeline()
        
        # Extract parameters from payload
        what_i_want = payload.get("what_i_want", "")
        from_where = payload.get("from_where", [])
        schema = payload.get("schema", {})
        extraction_mode = payload.get("extraction_mode", "HEURISTIC")
        max_pages_per_source = payload.get("max_pages_per_source", 5)
        webhook_url = payload.get("webhook_url")
        
        logger.info(f"Executing pipeline job: {what_i_want} from {len(from_where)} sources")
        
        # Import extraction mode enum
        from app.scraper.layers.intent_extractor import ExtractionMode
        mode = ExtractionMode.AI if extraction_mode == "AI" else ExtractionMode.HEURISTIC
        
        # Execute pipeline
        result = await self._pipeline.run(
            what_i_want=what_i_want,
            from_where=from_where,
            schema=schema,
            extraction_mode=mode,
            max_pages_per_source=max_pages_per_source,
            webhook_url=webhook_url
        )
        
        # Convert PipelineResult to dict
        result_dict = {
            "success": result.success,
            "data": result.data,
            "sources_processed": result.sources_processed,
            "sources_successful": result.sources_successful,
            "total_confidence": result.total_confidence,
            "urls_discovered": result.urls_discovered,
            "cleaning_stats": result.cleaning_stats,
            "extraction_stats": result.extraction_stats,
            "confidence_action": result.confidence_action,
            "version_id": result.version_id,
            "errors": result.errors
        }
        
        logger.info(
            f"Pipeline job completed: {result.sources_successful}/{result.sources_processed} sources successful"
        )
        
        return result_dict
