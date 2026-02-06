"""
Crawler - Multi-page scraping with link following

Systematically crawls websites following links and extracting data from multiple pages.
"""
import logging
import asyncio
from typing import Dict, Any, Set, List, Optional
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult, ScrapeFailureReason, CrawlConfig
from app.scraper.engines.static import StaticStrategy
from app.scraper.utils.robots_checker import robots_checker

logger = logging.getLogger(__name__)


class CrawlerScraper(BaseScraper):
    """
    Multi-page crawler with depth-limited link following.
    Ideal for scraping entire product catalogs or directory listings.
    """
    
    def __init__(self):
        self.static_scraper = StaticStrategy()
        self.visited_urls: Set[str] = set()
    
    def get_name(self) -> str:
        return "crawler"
    
    def can_handle(self, url: str) -> bool:
        """Crawler can handle any URL"""
        return True
    
    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs
    ) -> ScrapeResult:
        """
        Crawl website starting from URL
        
        Args:
            url: Starting URL
            schema: Data extraction schema
            job_id: Job identifier
            **kwargs: Must include 'crawl_config' (CrawlConfig object)
        """
        logger.info(f"Starting crawl from {url}")
        
        crawl_config: CrawlConfig = kwargs.get('crawl_config')
        if not crawl_config:
            crawl_config = CrawlConfig()  # Use defaults
        
        self.visited_urls = set()
        all_results = []
        
        try:
            # Check robots.txt if enabled
            if crawl_config.respect_robots_txt:
                allowed = await robots_checker.check_url_allowed(url)
                if not allowed:
                    return self.failure(
                        reason=ScrapeFailureReason.ANTI_BOT_SUSPECTED,
                        message=f"Crawling disallowed by robots.txt"
                    )
            
            # Start crawling
            results = await self._crawl_recursive(
                url=url,
                schema=schema,
                config=crawl_config,
                current_depth=0
            )
            
            all_results.extend(results)
            
            return ScrapeResult(
                success=True,
                status="success",
                data=all_results,
                strategy_used=self.get_name(),
                pages_scraped=len(self.visited_urls),
                confidence=0.85,
                metadata={
                    "total_pages_crawled": len(self.visited_urls),
                    "max_depth_reached": crawl_config.max_depth,
                    "urls_visited": list(self.visited_urls)[:50]  # First 50 for reference
                }
            )
            
        except Exception as e:
            logger.error(f"Crawling failed: {e}", exc_info=True)
            return self.failure(
                reason=ScrapeFailureReason.UNKNOWN,
                message=f"Crawl error: {str(e)}",
                errors=[str(e)]
            )
    
    async def _crawl_recursive(
        self,
        url: str,
        schema: Dict[str, Any],
        config: CrawlConfig,
        current_depth: int
    ) -> List[Dict[str, Any]]:
        """
        Recursively crawl pages
        
        Returns:
            List of extracted data from all crawled pages
        """
        results = []
        
        # Stop conditions
        if current_depth > config.max_depth:
            logger.debug(f"Max depth {config.max_depth} reached")
            return results
        
        if len(self.visited_urls) >= config.max_pages:
            logger.debug(f"Max pages {config.max_pages} reached")
            return results
        
        if url in self.visited_urls:
            return results
        
        # Mark as visited
        self.visited_urls.add(url)
        logger.info(f"Crawling [{len(self.visited_urls)}/{config.max_pages}]: {url}")
        
        try:
            # Fetch page
            await self.throttle(url, min_delay=config.crawl_delay_seconds)
            
            _, html, _ = await self.static_scraper.fetch(url, timeout=30)
            
            if not html:
                logger.warning(f"Empty HTML from {url}")
                return results
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract data from current page
            page_data = self._extract_data(soup, schema, url)
            if page_data:
                results.append(page_data)
            
            # Find links to follow
            if current_depth < config.max_depth:
                links = self._extract_links(soup, url, config)
                
                # Crawl child pages
                for link in links:
                    if len(self.visited_urls) >= config.max_pages:
                        break
                    
                    child_results = await self._crawl_recursive(
                        url=link,
                        schema=schema,
                        config=config,
                        current_depth=current_depth + 1
                    )
                    results.extend(child_results)
            
        except Exception as e:
            logger.warning(f"Failed to crawl {url}: {e}")
        
        return results
    
    def _extract_data(
        self,
        soup: BeautifulSoup,
        schema: Dict[str, Any],
        url: str
    ) -> Optional[Dict[str, Any]]:
        """Extract data from page according to schema"""
        extracted = {"_source_url": url}
        
        for field_name, selector in schema.items():
            try:
                element = soup.select_one(selector)
                if element:
                    extracted[field_name] = element.get_text().strip()
                else:
                    extracted[field_name] = None
            except Exception as e:
                logger.debug(f"Failed to extract {field_name}: {e}")
                extracted[field_name] = None
        
        # Only return if we extracted at least one field
        if any(v for k, v in extracted.items() if k != "_source_url"):
            return extracted
        
        return None
    
    def _extract_links(
        self,
        soup: BeautifulSoup,
        base_url: str,
        config: CrawlConfig
    ) -> List[str]:
        """
        Extract links to follow from page
        
        Returns:
            List of absolute URLs to crawl
        """
        links = []
        base_domain = urlparse(base_url).netloc
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Parse URL
            parsed = urlparse(absolute_url)
            
            # Skip non-HTTP(S) links
            if parsed.scheme not in ['http', 'https']:
                continue
            
            # Check external links
            if not config.follow_external_links:
                if parsed.netloc != base_domain:
                    continue
            
            # Check URL patterns if specified
            if config.url_patterns:
                if not any(re.search(pattern, absolute_url) for pattern in config.url_patterns):
                    continue
            
            # Skip already visited
            if absolute_url in self.visited_urls:
                continue
            
            # Skip common non-content URLs
            skip_patterns = [
                r'/login', r'/logout', r'/signin', r'/signup',
                r'/cart', r'/checkout', r'/account',
                r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$',
                r'/search\?', r'/filter\?'
            ]
            if any(re.search(pattern, absolute_url, re.I) for pattern in skip_patterns):
                continue
            
            links.append(absolute_url)
        
        return links
    
    async def crawl(
        self,
        start_url: str,
        crawl_config: CrawlConfig,
        extract_schema: Dict[str, str]
    ) -> ScrapeResult:
        """
        Public method for starting a crawl
        
        Convenience wrapper around scrape()
        """
        return await self.scrape(
            url=start_url,
            schema=extract_schema,
            job_id="crawler",
            crawl_config=crawl_config
        )
