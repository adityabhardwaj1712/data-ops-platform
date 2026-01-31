import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import uuid
from bs4 import BeautifulSoup

from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.logic.base import BaseScraper
from app.scraper.intelligence.analyzer import ScrapeAnalyzer
from app.scraper.utils.artifacts import ScrapeArtifacts
from app.scraper.utils.validator import ScrapeValidator
from app.scraper.extractors.auto_detect import AutoDetector
from app.scraper.recovery.selector_healer import SelectorHealer
from app.scraper.intelligence.preview import PreviewEngine
from app.scraper.intelligence.confidence import ConfidenceScorer
from app.scraper.engines.static import StaticStrategy
from app.scraper.extractors.auto import AutoExtractor
from app.scraper.extractors.config import ConfigExtractor
from app.scraper.utils.llm_client import LLMClient


logger = logging.getLogger(__name__)

class GenericScraper(BaseScraper):
    """
    The core scraping engine. Replaces engine.py with a more modular,
    artifact-heavy, and validated approach.
    Now implements the full Pro-Grade Ladder: Static -> Browser -> Stealth.
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
        self.auto_detector = AutoDetector()
        self.selector_healer = SelectorHealer()
        self.preview_engine = PreviewEngine()
        self.llm_client = LLMClient()

    async def can_handle(self, url: str) -> bool:
        # Default fallback, can handle everything
        return True

    def _load_browser(self):
        if not self.browser_strategy:
            from app.scraper.engines.browser import BrowserStrategy
            self.browser_strategy = BrowserStrategy()

    def _load_stealth(self):
        if not self.stealth_strategy:
            from app.scraper.engines.stealth import StealthStrategy
            self.stealth_strategy = StealthStrategy()

    def _detect_block(self, html: str, status_code: int = 200) -> bool:
        """
        Detects if the page content indicates a bot block.
        """
        if status_code in [403, 429]:
            return True
            
        lower_html = html.lower()
        block_keywords = [
            "captcha", "robot", "security check", "verify you are human",
            "access denied", "blocked", "incident id", "cloudflare"
        ]
        return any(kw in lower_html for kw in block_keywords)

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str = None,
        **kwargs
    ) -> ScrapeResult:
        
        job_id = job_id or str(uuid.uuid4())
        initial_strategy = kwargs.get("strategy", "auto")
        timeout = kwargs.get("timeout", 30)
        debug_mode = kwargs.get("debug", False)
        is_preview = kwargs.get("temp", False)
        
        # Debug initialization
        debug_info = {
            "escalation_path": [],
            "block_reasons": {},
            "engine_metrics": {},
            "start_time": datetime.now().isoformat()
        } if debug_mode else {}
        
        # 1. ANALYZE & APPLY MEMORY
        if initial_strategy == "auto":
            # Check domain memory (Silent Learning)
            db = kwargs.get("db")
            if db and not is_preview:
                from app.scraper.intelligence.memory import DomainMemoryManager
                if best_known:
                    logger.info(f"Using remembered strategy {best_known} for {url}")
                    initial_strategy = best_known
            
            if initial_strategy == "auto":
                initial_strategy = self.analyzer.detect_strategy(url, kwargs.get("stealth_mode", False))
        
        logger.info(f"Starting scrape for {url} (Initial strategy: {initial_strategy}, Job: {job_id})")

        # 2. ESCALATION LADDER: Static -> Browser -> Stealth
        content, page_html, screenshot = None, None, None
        ladder = ["static", "browser", "stealth"]
        
        # Start ladder at the detected or requested strategy
        try:
            start_index = ladder.index(initial_strategy)
            extra_strategies = ladder[start_index:]
        except ValueError:
            extra_strategies = [initial_strategy] # Fallback for unknown strategies

        used_strategy = initial_strategy
        
        for strategy in extra_strategies:
            engine_start = datetime.now()
            try:
                logger.info(f"Attempting {strategy} strategy...")
                
                if strategy == "static":
                    content, page_html, screenshot = await self.static_strategy.fetch(url, timeout=timeout)
                elif strategy == "browser":
                    self._load_browser()
                    content, page_html, screenshot = await self.fetch_with_retry(
                        self.browser_strategy.fetch,
                        url,
                        timeout=timeout,
                        take_screenshot=True
                    )
                elif strategy == "stealth":
                    self._load_stealth()
                    content, page_html, screenshot = await self.fetch_with_retry(
                        self.stealth_strategy.fetch,
                        url,
                        timeout=timeout + 15, # Stealth often takes longer
                        wait_for_selector=kwargs.get("wait_for_selector")
                    )
                
                # Validation: Does the content look like a block?
                if self._detect_block(page_html):
                    logger.warning(f"{strategy} strategy appears to be BLOCKED. Escalating...")
                    if debug_mode:
                        debug_info["block_reasons"][strategy] = "Content patterns detected as block"
                        debug_info["escalation_path"].append({"strategy": strategy, "status": "blocked"})
                    content, page_html, screenshot = None, None, None
                    continue # Try next step in ladder
                
                if debug_mode:
                    debug_info["escalation_path"].append({"strategy": strategy, "status": "success"})
                    debug_info["engine_metrics"][strategy] = (datetime.now() - engine_start).total_seconds()
                
                used_strategy = strategy
                break # Success! Exit ladder.

            except Exception as e:
                logger.warning(f"{strategy} fetch failed: {e}. Escalating...")
                if debug_mode:
                    debug_info["block_reasons"][strategy] = str(e)
                    debug_info["escalation_path"].append({"strategy": strategy, "status": "failed", "error": str(e)})
                content, page_html, screenshot = None, None, None
                continue

        if not page_html:
            return ScrapeResult(
                success=False,
                errors=["All strategies in escalation ladder failed."],
                failure_reason=ScrapeFailureReason.FETCH_FAILED,
                failure_message="Could not bypass site protection or fetch content.",
                metadata={"url": url, "job_id": job_id}
            )

        # 3. ARTIFACTS
        artifact_paths = []
        if page_html:
            html_path = self.artifacts.save_html(page_html, job_id)
            artifact_paths.append(html_path)
        
        if screenshot:
            artifact_paths.append(screenshot)

        # 4. EXTRACT
        extraction_config = kwargs.get("config") or schema
        soup = BeautifulSoup(page_html, 'lxml')
        
        # Debug Artifact
        if debug_mode:
            import json
            # Add HTML stats
            debug_info["raw_soup_stats"] = {
                "tag_count": len(soup.find_all()) if soup else 0,
                "link_count": len(soup.find_all('a')) if soup else 0,
                "text_length": len(content) if content else 0
            }
            debug_path = self.artifacts.save_json(debug_info, f"debug_{job_id}")
            artifact_paths.append(debug_path)
        
        auto_detect = kwargs.get("auto_detect", False) or not schema
        
        try:
            if auto_detect:
                detected_data, detect_confidence = self.auto_detector.detect(page_html, soup)
                extracted_data, ext_confidence = detected_data, detect_confidence
            elif self.config_extractor.is_applicable(extraction_config):
                extracted_data, ext_confidence = self.config_extractor.extract(soup, extraction_config)
                
                # Self-Healing: If fields are missing, try to heal
                missing_fields = [f for f, v in extracted_data.items() if not v]
                if missing_fields:
                    for field in missing_fields:
                        new_selector = self.selector_healer.heal(soup, extraction_config[field], field)
                        if new_selector:
                            # Re-attempt extraction for this field
                            el = soup.select_one(new_selector)
                            if el:
                                extracted_data[field] = el.get_text(strip=True)
                                logger.info(f"Successfully healed field '{field}' with new selector")
            elif kwargs.get("prompt"):
                extracted_data, ext_confidence = await self.llm_client.extract(
                    content=content, prompt=kwargs.get("prompt"), schema=schema, filters=kwargs.get("filters")
                )
            else:
                extracted_data, ext_confidence = await self.auto_extractor.extract(
                    html=page_html, markdown=content, schema=schema, filters=kwargs.get("filters")
                )
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return ScrapeResult(
                success=False,
                errors=[f"Extraction error: {str(e)}"],
                failure_reason=ScrapeFailureReason.SELECTOR_MISSING,
                metadata={"url": url, "job_id": job_id}
            )

        # 5. VALIDATE
        validation_report = self.validator.validate(extracted_data, schema)
        
        # 6. SCORE
        final_score, components = self.scorer.calculate_score(ext_confidence, validation_report)
        
        # 7. SMART SNAPSHOT (ONLY if needed)
        # Snapshot is already taken if browser/stealth was used or confidence is low
        final_screenshots = [screenshot] if screenshot else []
        if not final_screenshots and final_score < 70:
            # Low confidence but no screenshot yet? Try a quick one (optional implementation)
            pass

        # 8. UPDATE DOMAIN MEMORY
        db = kwargs.get("db")
        if db and not is_preview:
            from app.scraper.intelligence.memory import DomainMemoryManager
            start_time = datetime.fromisoformat(debug_info["start_time"]) if debug_mode else datetime.now()
            latency = (datetime.now() - start_time).total_seconds()
            await DomainMemoryManager.record_result(db, url, used_strategy, validation_report["valid"], latency)
            
            # 9. CHANGE DETECTION (SNAPSHOT)
            if validation_report["valid"]:
                from app.scraper.intelligence.snapshots import SnapshotManager
                await SnapshotManager.save_snapshot(db, job_id, url, extracted_data)

        return ScrapeResult(
            success=validation_report["valid"],
            status="success" if validation_report["valid"] else "failed",
            data=extracted_data,
            missing_fields=[f for f, v in extracted_data.items() if not v],
            strategy_used=used_strategy,
            confidence=final_score,
            confidence_components=components,
            screenshots=final_screenshots,
            artifact_paths=artifact_paths,
            validation_report=validation_report,
            failure_reason=None if validation_report["valid"] else ScrapeFailureReason.VALIDATION_FAILED,
            metadata={
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "job_id": job_id,
                "ladder_used": used_strategy != initial_strategy,
                "debug": debug_mode
            },
            debug_data=debug_info if debug_mode else None
        )
