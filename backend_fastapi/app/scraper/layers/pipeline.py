"""
5-LAYER SCRAPER PIPELINE ORCHESTRATOR

Combines all 5 layers into a unified pipeline:

Layer 1: Source Manager    → Multiple URLs + pagination
Layer 2: Fetch Engine      → Get HTML (no parsing)
Layer 3: Content Cleaner   → Remove noise, get clean text
Layer 4: Intent Extractor  → Extract data based on intent
Layer 5: Trust Engine      → Validate + HITL + Version
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.scraper.layers.source_manager import SourceManager, ScrapeIntent
from app.scraper.layers.fetch_engine import FetchEngine, FetchMethod, FetchResult
from app.scraper.layers.content_cleaner import ContentCleaner, CleanedContent
from app.scraper.layers.intent_extractor import IntentExtractor, ExtractionMode, ExtractionResult
from app.core.limits import get_confidence_action, limits
from app.services.aggregator import aggregator
from app.services.webhooks import webhook_service


@dataclass
class PipelineResult:
    """Result of the complete scraping pipeline"""
    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    sources_processed: int = 0
    sources_successful: int = 0
    total_confidence: float = 0.0
    
    # Per-layer statistics
    fetch_results: List[Dict] = field(default_factory=list)
    cleaning_stats: Dict[str, Any] = field(default_factory=dict)
    extraction_stats: Dict[str, Any] = field(default_factory=dict)
    
    # Trust Engine results
    confidence_action: str = "auto_accept"  # auto_accept, optional_review, mandatory_review
    version_id: Optional[int] = None
    
    errors: List[str] = field(default_factory=list)


class ScraperPipeline:
    """
    5-Layer Scraper Pipeline
    
    Usage:
    ```python
    pipeline = ScraperPipeline()
    result = await pipeline.run(
        what_i_want="DevOps fresher jobs in India",
        from_where=["url1", "url2"],
        schema={"title": "str", "company": "str"}
    )
    ```
    """
    
    def __init__(self):
        # Initialize all layers
        self.source_manager = SourceManager()
        self.fetch_engine = FetchEngine()
        self.content_cleaner = ContentCleaner()
        self.intent_extractor = IntentExtractor()
    
    async def run(
        self,
        what_i_want: str,
        from_where: List[str],
        schema: Dict[str, Any],
        extraction_mode: ExtractionMode = ExtractionMode.HEURISTIC,
        max_pages_per_source: int = 5,
        webhook_url: Optional[str] = None
    ) -> PipelineResult:
        """
        Run the complete 5-layer scraping pipeline.
        
        Args:
            what_i_want: Natural language description of what to extract
            from_where: List of URLs to scrape
            schema: Expected data schema
            extraction_mode: heuristic (free) or AI-assisted
            max_pages_per_source: Max pages to scrape per source
            
        Returns:
            PipelineResult with all extracted data
        """
        result = PipelineResult(success=False)
        all_data = []
        
        # ═══════════════════════════════════════════════════════════
        # LAYER 1: SOURCE MANAGER
        # ═══════════════════════════════════════════════════════════
        intent = ScrapeIntent(
            what_i_want=what_i_want,
            from_where=self.source_manager.normalize_urls(from_where),
            schema=schema,
            max_pages_per_source=max_pages_per_source
        )
        
        task_payloads = await self.source_manager.process_intent(intent)
        result.sources_processed = len(task_payloads)
        
        # ═══════════════════════════════════════════════════════════
        # PROCESS EACH SOURCE
        # ═══════════════════════════════════════════════════════════
        total_original_size = 0
        total_cleaned_size = 0
        
        for task in task_payloads:
            try:
                # ─────────────────────────────────────────────────────
                # LAYER 2: FETCH ENGINE
                # ─────────────────────────────────────────────────────
                url = task["url"]
                fetch_method = self.fetch_engine.detect_method(url)
                
                fetch_result = await self.fetch_engine.fetch(
                    url=url,
                    method=fetch_method
                )
                
                result.fetch_results.append({
                    "url": url,
                    "success": fetch_result.success,
                    "method": fetch_result.method_used.value
                })
                
                if not fetch_result.success:
                    result.errors.append(f"Fetch failed for {url}: {fetch_result.error}")
                    continue
                
                # ─────────────────────────────────────────────────────
                # LAYER 3: CONTENT CLEANER
                # ─────────────────────────────────────────────────────
                cleaned = self.content_cleaner.clean(fetch_result.html)
                
                total_original_size += cleaned.original_size
                total_cleaned_size += cleaned.cleaned_size
                
                if not cleaned.success or not cleaned.markdown:
                    result.errors.append(f"Cleaning failed for {url}")
                    continue
                
                # ─────────────────────────────────────────────────────
                # LAYER 4: INTENT-BASED EXTRACTOR
                # ─────────────────────────────────────────────────────
                extraction = await self.intent_extractor.extract(
                    content=cleaned.markdown,
                    intent=what_i_want,
                    schema=schema,
                    mode=extraction_mode
                )
                
                if extraction.success and extraction.data:
                    # Add source metadata
                    extraction.data["_source_url"] = url
                    extraction.data["_page"] = task.get("page", 1)
                    extraction.data["_confidence"] = extraction.confidence
                    
                    all_data.append(extraction.data)
                    result.sources_successful += 1
                    result.total_confidence += extraction.confidence
                    
            except Exception as e:
                result.errors.append(f"Error processing {task.get('url', 'unknown')}: {str(e)}")
        
        # ═══════════════════════════════════════════════════════════
        # AGGREGATE RESULTS & TRUST ENGINE
        # ═══════════════════════════════════════════════════════════
        result.data = all_data
        result.success = len(all_data) > 0
        
        if result.sources_successful > 0:
            result.total_confidence /= result.sources_successful
        
        # Determine confidence action (Layer 5: Trust Engine Decision)
        result.confidence_action = get_confidence_action(result.total_confidence)
        
        # Apply Normalization & Deduplication to final set
        if result.data:
            # Note: We use the standalone services here for immediate feedback, 
            # while the Aggregator handles permanent storage/versioning later.
            from app.services.normalizer import normalizer
            from app.services.deduplicator import deduplicator
            
            result.data = normalizer.normalize_batch(result.data)
            dedupe_res = deduplicator.deduplicate(result.data)
            result.data = dedupe_res.unique_items
            
            # Update stats
            result.extraction_stats["unique_items"] = len(result.data)
            result.extraction_stats["duplicates_removed"] = dedupe_res.duplicates_removed
        
        # Cleaning statistics summary
        if total_original_size > 0:
            reduction = ((total_original_size - total_cleaned_size) / total_original_size) * 100
            result.cleaning_stats = {
                "original_size": total_original_size,
                "cleaned_size": total_cleaned_size,
                "reduction_percent": round(reduction, 1)
            }
        
        result.extraction_stats |= {
            "mode": extraction_mode.value,
            "items_extracted": len(all_data),
            "average_confidence": round(result.total_confidence, 2),
            "action_required": result.confidence_action
        }
        
        # PRO: Trigger Webhook
        if webhook_url and result.success:
            await webhook_service.send(webhook_url, {
                "intent": what_i_want,
                "data_count": len(result.data),
                "confidence": result.total_confidence,
                "data": result.data[:10]  # Send sample for preview
            })
        
        return result
    
    async def run_single(
        self,
        url: str,
        what_i_want: str,
        schema: Dict[str, Any],
        extraction_mode: ExtractionMode = ExtractionMode.HEURISTIC
    ) -> Dict[str, Any]:
        """
        Run pipeline for a single URL (convenience method).
        """
        result = await self.run(
            what_i_want=what_i_want,
            from_where=[url],
            schema=schema,
            extraction_mode=extraction_mode
        )
        
        if result.data:
            return result.data[0]
        return {}
