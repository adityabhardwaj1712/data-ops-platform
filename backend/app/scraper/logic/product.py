import logging
import random
import asyncio
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.utils.validator import ScrapeValidator
from app.scraper.intelligence.confidence import ConfidenceScorer
from app.scraper.engines.browser import BrowserStrategy

logger = logging.getLogger(__name__)

class ProductScraper(BaseScraper):
    """
    Specialized scraper for e-commerce and product pages.
    Uses pattern-based fallbacks for common fields like Price and Title.
    """
    def __init__(self):
        self.browser_strategy = BrowserStrategy()
        self.validator = ScrapeValidator()
        self.scorer = ConfidenceScorer()

    async def can_handle(self, url: str) -> bool:
        # Matches Amazon, eBay, Walmart, Target, BestBuy, etc.
        patterns = [
            "amazon.", "ebay.", "walmart.", "target.com", 
            "bestbuy.com", "aliexpress.", "etsy.com"
        ]
        return any(p in url.lower() for p in patterns)

    async def scrape(
        self, 
        url: str, 
        schema: Dict[str, Any], 
        job_id: str,
        **kwargs
    ) -> ScrapeResult:
        logger.info(f"Starting Product specialized scrape for {url}")
        
        try:
            # Product sites almost always need browser for reliable pricedata
            content, html, screenshot = await self.fetch_with_retry(
                self.browser_strategy.fetch,
                url,
                timeout=kwargs.get("timeout", 45),
                take_screenshot=True,
                wait_until="networkidle"
            )

            if not html:
                raise Exception("Failed to fetch HTML from product page")

            # Deep Fallback Selectors for Price
            PRICE_SELECTORS = [
                # Amazon
                "span.a-price-whole", "#priceblock_ourprice", "span.a-offscreen",
                # eBay
                "#prcIsum", "#mm-saleDscPrc",
                # Walmart
                ".price-characteristic", ".item-price",
                # Generic / Schema.org
                "[itemprop='price']", ".product-price", ".price", ".current-price",
                "span:contains('$')", "div:contains('$')"
            ]
            
            TITLE_SELECTORS = [
                "#productTitle", "#itemTitle", "h1.prod-ProductTitle", 
                "h1", ".product-name", "[itemprop='name']"
            ]

            soup = BeautifulSoup(html, "lxml")
            extracted_data = {}
            
            # Universal Title Extraction
            title = None
            for sel in TITLE_SELECTORS:
                el = soup.select_one(sel)
                if el:
                    title = el.get_text().strip()
                    if title: break
            extracted_data["title"] = title

            # Universal Price Extraction
            price = None
            for sel in PRICE_SELECTORS:
                try:
                    el = soup.select_one(sel)
                    if el:
                        price_text = el.get_text().strip()
                        # Clean currency and formatting
                        digits = "".join(c for c in price_text if c.isdigit() or c == '.')
                        if digits and '.' in digits:
                            price = digits
                            break
                        elif digits:
                            price = digits
                except:
                    continue
            
            extracted_data["price"] = price
            
            # Fill other requested fields from schema if they exist
            for field in schema:
                if field not in extracted_data:
                    el = soup.select_one(schema[field])
                    extracted_data[field] = el.get_text().strip() if el else None

            # Validation & Scoring
            validation_report = self.validator.validate(extracted_data, schema)
            ext_confidence = 0.8 if price and title else 0.4
            final_score, components = self.scorer.calculate_score(ext_confidence, validation_report)

            return ScrapeResult(
                success=validation_report["valid"],
                status="success" if validation_report["valid"] else "partial",
                data=extracted_data,
                strategy_used="product_specialized",
                confidence=final_score,
                confidence_components=components,
                screenshots=[screenshot] if screenshot else [],
                validation_report=validation_report,
                metadata={
                    "url": url,
                    "job_id": job_id,
                    "engine": "playwright",
                    "type": "e-commerce"
                }
            )

        except Exception as e:
            logger.error(f"Product specialized scrape failed: {e}")
            return ScrapeResult(
                success=False,
                status="failed",
                errors=[str(e)],
                failure_reason=ScrapeFailureReason.FETCH_FAILED,
                failure_message=f"Product scrape failed: {str(e)}"
            )
