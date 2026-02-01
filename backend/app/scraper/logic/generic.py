import logging
import uuid
from datetime import datetime
from typing import Dict, Any

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

# ✅ ADD THIS IMPORT
from app.scraper.processing.field_extractor import extract_fields

logger = logging.getLogger(__name__)


class GenericScraper(BaseScraper):
    """
    Core scraping engine with escalation ladder and smart extraction.
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
        if status_code in [403, 429]:
            return True

        lower_html = html.lower()
        return any(k in lower_html for k in [
            "captcha", "verify you are human", "access denied",
            "cloudflare", "blocked", "security check"
        ])

    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str = None,
        **kwargs
    ) -> ScrapeResult:

        job_id = job_id or str(uuid.uuid4())
        timeout = kwargs.get("timeout", 30)
        initial_strategy = kwargs.get("strategy", "auto")

        ladder = ["static", "browser", "stealth"]
        used_strategy = None

        content = html = screenshot = None

        for strategy in ladder:
            try:
                if strategy == "static":
                    content, html, screenshot = await self.static_strategy.fetch(url, timeout=timeout)
                elif strategy == "browser":
                    self._load_browser()
                    content, html, screenshot = await self.browser_strategy.fetch(url, timeout=timeout)
                elif strategy == "stealth":
                    self._load_stealth()
                    content, html, screenshot = await self.stealth_strategy.fetch(
                        url,
                        timeout=timeout + 15,
                        wait_for_selector=kwargs.get("wait_for_selector")
                    )

                if not html or self._detect_block(html):
                    continue

                used_strategy = strategy
                break

            except Exception as e:
                logger.warning(f"{strategy} failed: {e}")
                continue

        if not html:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used="none",
                failure_reason=ScrapeFailureReason.FETCH_FAILED,
                failure_message="All strategies failed",
                metadata={"url": url, "job_id": job_id}
            )

        # ---------- ARTIFACTS ----------
        artifact_paths = []
        html_path = self.artifacts.save_html(html, job_id)
        artifact_paths.append(html_path)

        if screenshot:
            artifact_paths.append(screenshot)

        # ---------- EXTRACTION ----------
        soup = BeautifulSoup(html, "lxml")

        try:
            # ✅ PRIMARY FIX: SIMPLE FIELD EXTRACTION
            extracted_data = extract_fields(html, schema)

            # If nothing extracted → fallback to existing advanced logic
            if not extracted_data:
                extracted_data, ext_confidence = await self.auto_extractor.extract(
                    html=html,
                    markdown=content,
                    schema=schema,
                    filters=kwargs.get("filters")
                )
            else:
                ext_confidence = 1.0

        except Exception as e:
            return ScrapeResult(
                success=False,
                status="failed",
                strategy_used=used_strategy,
                failure_reason=ScrapeFailureReason.SELECTOR_MISSING,
                failure_message=str(e),
                metadata={"url": url, "job_id": job_id}
            )

        # ---------- VALIDATION ----------
        validation_report = self.validator.validate(extracted_data, schema)
        final_score, components = self.scorer.calculate_score(ext_confidence, validation_report)

        missing_fields = [k for k in schema if not extracted_data.get(k)]

        return ScrapeResult(
            success=len(extracted_data) > 0,
            status="success" if not missing_fields else "partial",
            data=extracted_data,
            missing_fields=missing_fields,
            strategy_used=used_strategy,
            confidence=final_score,
            confidence_components=components,
            artifact_paths=artifact_paths,
            screenshots=[screenshot] if screenshot else [],
            validation_report=validation_report,
            metadata={
                "url": url,
                "job_id": job_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
