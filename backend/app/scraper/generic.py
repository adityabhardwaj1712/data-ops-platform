import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
from bs4 import BeautifulSoup

from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.analyzer import ScrapeAnalyzer
from app.scraper.artifacts import ScrapeArtifacts
from app.scraper.validator import ScrapeValidator
from app.scraper.confidence import ConfidenceScorer
from app.scraper.strategies.static import StaticStrategy
from app.scraper.extractors.auto import AutoExtractor
from app.scraper.extractors.config import ConfigExtractor
from app.scraper.llm_client import LLMClient
from app.scraper.extractors.config import ConfigExtractor


logger = logging.getLogger(__name__)

class GenericScraper:
    """
    The core scraping engine. Replaces engine.py with a more modular,
    artifact-heavy, and validated approach.
    """
    
    def __init__(self):
        self.analyzer = ScrapeAnalyzer()
        self.artifacts = ScrapeArtifacts()
        self.validator = ScrapeValidator()
        self.scorer = ConfidenceScorer()
        
        self.static_strategy = StaticStrategy()
        self.browser_strategy = None
        self.stealth_strategy = None
        
        self.config_extractor = ConfigExtractor()
        self.auto_extractor = AutoExtractor()
        self.llm_client = LLMClient()

    def _load_browser(self):
        if not self.browser_strategy:
            from app.scraper.strategies.browser import BrowserStrategy
            self.browser_strategy = BrowserStrategy()

    def _load_stealth(self):
        if not self.stealth_strategy:
            from app.scraper.strategies.stealth import StealthStrategy
            self.stealth_strategy = StealthStrategy()

    async def run(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str = None,
        strategy: str = "auto",
        stealth_mode: bool = False,
        timeout: int = 30,
        filters: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> ScrapeResult:
        
        job_id = job_id or str(uuid.uuid4())
        errors = []
        artifact_paths = []
        screenshots = []
        
        # 1. ANALYZE
        if strategy == "auto":
            strategy = self.analyzer.detect_strategy(url, stealth_mode)
        
        logger.info(f"Scraping {url} using {strategy} strategy (Job: {job_id})")

        try:
            # 2. FETCH with Retry
            max_retries = 3
            content, page_html, screenshot = None, None, None
            
            for attempt in range(max_retries):
                try:
                    if strategy == "static":
                        content, page_html, screenshot = await self.static_strategy.fetch(url, timeout=timeout)
                    elif strategy == "browser":
                        self._load_browser()
                        content, page_html, screenshot = await self.browser_strategy.fetch(url, timeout=timeout)
                    else: # stealth
                        self._load_stealth()
                        content, page_html, screenshot = await self.stealth_strategy.fetch(url, timeout=timeout)
                    
                    if content: # Success
                        break
                except Exception as e:
                    # TASK 110: Service Engine Hardening
                    # Removed detailed exception trace for retries, keeping it calm.
                    logger.warning(f"Fetch attempt {attempt+1}/{max_retries} failed: {type(e).__name__} (Retrying in {2**attempt}s)")
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt + 1)

            # 3. ARTIFACTS
            if page_html:
                # Save HTML even if extraction fails later
                html_path = self.artifacts.save_html(page_html, job_id)
                artifact_paths.append(html_path)
            
            if screenshot:
                artifact_paths.append(screenshot)
                screenshots.append(screenshot)

            if not content:
                raise Exception("No content fetched from target URL")

            # 4. EXTRACT
            extracted_data, ext_confidence = None, 0.0
            
            # Priority 1: Config-driven (Explicit selectors from config OR schema)
            # Check config first for corrected selectors
            extraction_config = config if self.config_extractor.is_applicable(config) else schema
            
            if self.config_extractor.is_applicable(extraction_config):
                soup = BeautifulSoup(page_html, 'lxml')
                extracted_data, ext_confidence = self.config_extractor.extract(soup, extraction_config)
            
            # Priority 2: Prompt-driven (LLM)
            elif prompt:
                extracted_data, ext_confidence = await self.llm_client.extract(
                    content=content, prompt=prompt, schema=schema, filters=filters
                )
            
            # Priority 3: Auto-extraction (Heuristics)
            else:
                extracted_data, ext_confidence = await self.auto_extractor.extract(
                    html=page_html, markdown=content, schema=schema, filters=filters
                )

            # 5. VALIDATE
            validation_report = self.validator.validate(extracted_data, schema)
            
            # 6. SCORE
            final_score, components = self.scorer.calculate_score(ext_confidence, validation_report)
            
            return ScrapeResult(
                success=validation_report["valid"],
                data=extracted_data,
                strategy_used=strategy,
                confidence=final_score,
                confidence_components=components,
                screenshots=screenshots,
                artifact_paths=artifact_paths,
                validation_report=validation_report,
                failure_reason=None if validation_report["valid"] else ScrapeFailureReason.VALIDATION_FAILED,
                failure_message=None if validation_report["valid"] else f"The extracted data is missing some information or contains duplicates: {', '.join(validation_report['errors'][:3])}",
                errors=validation_report["errors"],
                metadata={
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "job_id": job_id,
                    "human_reviewed": False
                }
            )

        except Exception as e:
            error_str = str(e)
            reason = ScrapeFailureReason.UNKNOWN
            
            if "403" in error_str or "captcha" in error_str.lower():
                reason = ScrapeFailureReason.ANTI_BOT_SUSPECTED
            elif "Selector" in error_str or "not found" in error_str.lower():
                reason = ScrapeFailureReason.SELECTOR_MISSING
            elif "timeout" in error_str.lower():
                reason = ScrapeFailureReason.JS_TIMEOUT
            elif "dns" in error_str.lower() or "connection" in error_str.lower():
                reason = ScrapeFailureReason.FETCH_FAILED
            
            logger.error(f"Scrape failed [{reason}] for {url}: {e}")
            
            return ScrapeResult(
                success=False,
                strategy_used=strategy,
                errors=[error_str],
                artifact_paths=artifact_paths,
                failure_reason=reason,
                failure_message=self._humanize_error(reason, error_str),
                metadata={
                    "url": url,
                    "error_category": reason.value,
                    "timestamp": datetime.now().isoformat()
                }
            )

    def _humanize_error(self, reason: ScrapeFailureReason, error_str: str) -> str:
        """Translates technical errors into calm, actionable messages."""
        mapping = {
            ScrapeFailureReason.ANTI_BOT_SUSPECTED: "Access was denied. The website might be using anti-bot protection. Try switching to 'Stealth' mode.",
            ScrapeFailureReason.SELECTOR_MISSING: "We couldn't find the requested data. The website's layout might have changed or the selectors are incorrect.",
            ScrapeFailureReason.JS_TIMEOUT: "The page took too long to load. This can happen with heavy websites or slow connections.",
            ScrapeFailureReason.FETCH_FAILED: "We couldn't reach the website. Please check if the URL is correct and the site is online.",
            ScrapeFailureReason.VALIDATION_FAILED: "The data we found doesn't match the required format (e.g., missing prices or titles).",
            ScrapeFailureReason.UNKNOWN: f"An unexpected issue occurred: {error_str}. We recommend checking the artifacts and retrying."
        }
        return mapping.get(reason, mapping[ScrapeFailureReason.UNKNOWN])
