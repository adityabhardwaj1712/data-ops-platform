"""
LAYER 1 - SOURCE MANAGER
Handles multiple URLs, pagination, and fan-out task creation

Input:
{
    "what_i_want": "DevOps fresher jobs",
    "from_where": ["url1", "url2", "url3"]
}

Output:
Creates SCRAPE tasks for each URL
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import httpx
import asyncio
from app.db.session import async_session_factory
from app.db.source_health import SourceHealth
from sqlalchemy import select


class SourceType(str, Enum):
    SINGLE_PAGE = "single_page"
    PAGINATED = "paginated"
    SITEMAP = "sitemap"
    API = "api"


@dataclass
class Source:
    """Represents a scraping source"""
    url: str
    source_type: SourceType = SourceType.SINGLE_PAGE
    max_pages: int = 1
    pagination_pattern: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_url: Optional[str] = None  # For crawl graph awareness
    depth: int = 0  # Crawl depth from seed URL


@dataclass
class ScrapeIntent:
    """User's scraping intent"""
    what_i_want: str
    from_where: List[str]
    schema: Dict[str, Any]
    max_pages_per_source: int = 10
    
    def to_sources(self) -> List[Source]:
        """Convert URLs to Source objects"""
        return [
            Source(
                url=url,
                max_pages=self.max_pages_per_source
            )
            for url in self.from_where
        ]


class SourceManager:
    """
    Layer 1 - Source Manager
    
    Responsibilities:
    - Accept multiple URLs
    - Detect pagination patterns
    - Normalize sources
    - Create fan-out tasks
    - Enforce robots.txt and Sitemap limits
    """
    
    def __init__(self):
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.max_sitemap_urls = 500  # Safety cap
        
    async def process_intent(
        self,
        intent: ScrapeIntent
    ) -> List[Dict[str, Any]]:
        """
        Process a scraping intent and create task payloads.
        
        Args:
            intent: User's scraping intent
            
        Returns:
            List of task payloads ready for the fetch engine
        """
        sources = intent.to_sources()
        tasks = []
        
        for source in sources:
            # 1. Check domain health
            if await self._is_blocked(source.url):
                continue
                
            # 2. Check robots.txt (Ethical Guardrail)
            if not await self._check_robots(source.url):
                print(f"Skipping robots-blocked URL: {source.url}")
                continue
                
            # Detect source type and pagination
            source = await self._analyze_source(source)
            
            # Generate task payloads
            if source.source_type == SourceType.PAGINATED:
                # Create tasks for multiple pages
                page_tasks = self._create_paginated_tasks(source, intent)
                tasks.extend(page_tasks)
            else:
                # Single page task
                tasks.append(self._create_task_payload(source, intent, page=1))
        
        return tasks
    
    async def _analyze_source(self, source: Source) -> Source:
        """
        Analyze a source to detect its type and pagination pattern.
        """
        url = source.url
        
        # Detect common pagination patterns
        pagination_indicators = [
            ('?page=', SourceType.PAGINATED),
            ('?p=', SourceType.PAGINATED),
            ('/page/', SourceType.PAGINATED),
            ('/sitemap', SourceType.SITEMAP),
            ('/api/', SourceType.API),
            ('/v1/', SourceType.API),
            ('/v2/', SourceType.API),
        ]
        
        for pattern, source_type in pagination_indicators:
            if pattern in url.lower():
                source.source_type = source_type
                source.pagination_pattern = pattern
                break
        
        return source
    
    def _create_paginated_tasks(
        self,
        source: Source,
        intent: ScrapeIntent
    ) -> List[Dict[str, Any]]:
        """Create tasks for each page of a paginated source"""
        tasks = []
        
        for page in range(1, source.max_pages + 1):
            url = self._build_page_url(source.url, page)
            tasks.append(self._create_task_payload(
                Source(url=url, source_type=source.source_type),
                intent,
                page=page
            ))
        
        return tasks
    
    def _build_page_url(self, base_url: str, page: int) -> str:
        """Build URL for a specific page number"""
        if '?page=' in base_url:
            # Replace existing page number
            import re
            return re.sub(r'\?page=\d+', f'?page={page}', base_url)
        elif '?' in base_url:
            return f"{base_url}&page={page}"
        else:
            return f"{base_url}?page={page}"
    
    def _create_task_payload(
        self,
        source: Source,
        intent: ScrapeIntent,
        page: int = 1,
        parent_task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a task payload for the fetch engine with crawl graph awareness"""
        return {
            "url": source.url,
            "intent": intent.what_i_want,
            "schema": intent.schema,
            "page": page,
            "source_type": source.source_type.value,
            "parent_task_id": parent_task_id,  # For crawl graph
            "crawl_depth": source.depth,
            "metadata": {
                "original_url": source.url,
                "page_number": page,
                "parent_url": source.parent_url,
                "crawl_depth": source.depth,
                "is_seed_url": source.depth == 0
            }
        }
    
    def normalize_urls(self, urls: List[str]) -> List[str]:
        """
        Normalize a list of URLs.
        - Add https if missing
        - Remove trailing slashes
        - Deduplicate
        """
        normalized = []
        seen = set()
        
        for url in urls:
            # Add scheme if missing
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            # Remove trailing slash
            url = url.rstrip('/')
            
            # Deduplicate
            if url not in seen:
                seen.add(url)
                normalized.append(url)
        
        return normalized
    
    async def expand_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Expand a sitemap URL to individual page URLs.
        """
        import httpx
        import xml.etree.ElementTree as ET
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(sitemap_url)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                
                # Handle both sitemap index and urlset
                namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                urls = []
                for loc in root.findall('.//ns:loc', namespaces):
                    urls.append(loc.text)
                    if len(urls) >= self.max_sitemap_urls:
                        break
                
                return urls
        except Exception:
            return [sitemap_url]

    async def _check_robots(self, url: str) -> bool:
        """
        Check if scraping is allowed by robots.txt.
        Uses a cache to avoid redundant hits.
        """
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        if base_url not in self.robots_cache:
            rp = RobotFileParser()
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    resp = await client.get(base_url)
                    if resp.status_code == 200:
                        rp.parse(resp.text.splitlines())
                    else:
                        # If no robots.txt or error, assume allow (standard behavior)
                        rp.allow_all = True
            except Exception:
                rp.allow_all = True
            self.robots_cache[base_url] = rp
            
        return self.robots_cache[base_url].can_fetch("*", url)
    async def _is_blocked(self, url: str) -> bool:
        """Check if domain is blocked in SourceHealth"""
        domain = urlparse(url).netloc.lower()
        
        async with async_session_factory() as db:
            result = await db.execute(select(SourceHealth).where(SourceHealth.domain == domain))
            health = result.scalar_one_or_none()
            
            if health and health.is_blocked:
                return True
        
        return False

    def expand_crawl_graph(
        self,
        parent_task_payload: Dict[str, Any],
        discovered_urls: List[str],
        intent: ScrapeIntent,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Expand the crawl graph by creating child tasks from discovered URLs.

        This is used for follow-up links found during scraping (e.g., from category pages to detail pages).
        """
        child_tasks = []
        parent_url = parent_task_payload["url"]
        parent_depth = parent_task_payload.get("crawl_depth", 0)

        # Don't crawl deeper than max_depth
        if parent_depth >= max_depth:
            return child_tasks

        for url in discovered_urls:
            # Normalize and validate URL
            normalized_urls = self.normalize_urls([url])
            if not normalized_urls:
                continue

            normalized_url = normalized_urls[0]

            # Skip if it's the same as parent
            if normalized_url == parent_url:
                continue

            # Create child source
            child_source = Source(
                url=normalized_url,
                parent_url=parent_url,
                depth=parent_depth + 1,
                max_pages=1  # Child pages are usually single pages
            )

            # Analyze the child source
            child_source = self._analyze_source_sync(child_source)

            # Create task payload
            task_payload = self._create_task_payload(
                child_source,
                intent,
                page=1,
                parent_task_id=parent_task_payload.get("task_id")
            )

            child_tasks.append(task_payload)

        return child_tasks

    def _analyze_source_sync(self, source: Source) -> Source:
        """
        Synchronous version of source analysis for crawl graph expansion.
        """
        url = source.url

        # Detect common pagination patterns (same logic as async version)
        pagination_indicators = [
            ('?page=', SourceType.PAGINATED),
            ('?p=', SourceType.PAGINATED),
            ('/page/', SourceType.PAGINATED),
            ('/sitemap', SourceType.SITEMAP),
            ('/api/', SourceType.API),
            ('/v1/', SourceType.API),
            ('/v2/', SourceType.API),
        ]

        for pattern, source_type in pagination_indicators:
            if pattern in url.lower():
                source.source_type = source_type
                source.pagination_pattern = pattern
                break

        return source

    def detect_pagination_from_content(
        self,
        content: str,
        base_url: str
    ) -> List[str]:
        """
        Detect pagination links from page content and return additional URLs to crawl.
        """
        import re
        from urllib.parse import urljoin

        pagination_urls = []

        # Common pagination patterns
        patterns = [
            r'href="([^"]*page=\d+[^"]*)"',
            r'href="([^"]*/page/\d+[^"]*)"',
            r'href="([^"]*\?p=\d+[^"]*)"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                full_url = urljoin(base_url, match)
                if full_url not in pagination_urls:
                    pagination_urls.append(full_url)

        return pagination_urls[:10]  # Limit to prevent explosion
