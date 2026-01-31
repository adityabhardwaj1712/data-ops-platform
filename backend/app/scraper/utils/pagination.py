"""
Pagination Handler
Handles various pagination patterns for multi-page scraping
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode


class PaginationType(str, Enum):
    CLICK = "click"
    SCROLL = "scroll"
    URL_PATTERN = "url_pattern"
    CURSOR = "cursor"
    LOAD_MORE = "load_more"
    NONE = "none"


@dataclass
class PageInfo:
    url: str
    page_number: int
    has_next: bool
    next_url: Optional[str] = None
    next_selector: Optional[str] = None


class PaginationHandler:
    """
    Handles multiple pagination patterns.
    
    Patterns:
    - CLICK: Next button clicking (e.g., ".next", ".pagination-next")
    - SCROLL: Infinite scroll detection
    - URL_PATTERN: URL incrementing (?page=1, ?page=2)
    - CURSOR: API cursor-based pagination
    - LOAD_MORE: Load more button
    """
    
    # Common next button selectors
    NEXT_SELECTORS = [
        ".next",
        ".pagination-next",
        '[rel="next"]',
        'a[aria-label="Next"]',
        ".next-page",
        ".pagination a:last-child",
        "button.next",
        '[data-testid="next"]',
    ]
    
    # Common load more button selectors
    LOAD_MORE_SELECTORS = [
        ".load-more",
        ".show-more",
        "button.more",
        '[data-action="load-more"]',
        ".view-more",
    ]
    
    def detect_pagination_type(
        self,
        html: str,
        url: str
    ) -> PaginationType:
        """
        Auto-detect the pagination type used on a page.
        
        Args:
            html: Page HTML content
            url: Current page URL
            
        Returns:
            Detected pagination type
        """
        # Check for URL pattern (page parameter)
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if any(p in params for p in ['page', 'p', 'offset', 'start']):
            return PaginationType.URL_PATTERN
        
        # Check for next button in HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
        
        for selector in self.NEXT_SELECTORS:
            if soup.select_one(selector):
                return PaginationType.CLICK
        
        # Check for load more button
        for selector in self.LOAD_MORE_SELECTORS:
            if soup.select_one(selector):
                return PaginationType.LOAD_MORE
        
        # Check for infinite scroll indicators
        if self._detect_infinite_scroll(html):
            return PaginationType.SCROLL
        
        return PaginationType.NONE
    
    def get_next_page_url(
        self,
        html: str,
        current_url: str,
        page_number: int,
        pagination_type: Optional[PaginationType] = None
    ) -> Optional[str]:
        """
        Get the URL for the next page.
        
        Args:
            html: Current page HTML
            current_url: Current page URL
            page_number: Current page number (1-indexed)
            pagination_type: Optional known pagination type
            
        Returns:
            Next page URL or None
        """
        if pagination_type is None:
            pagination_type = self.detect_pagination_type(html, current_url)
        
        if pagination_type == PaginationType.URL_PATTERN:
            return self._get_url_pattern_next(current_url, page_number)
        
        elif pagination_type == PaginationType.CLICK:
            return self._get_click_next(html, current_url)
        
        return None
    
    def _get_url_pattern_next(
        self,
        current_url: str,
        page_number: int
    ) -> str:
        """Generate next URL using URL pattern"""
        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)
        
        # Find the page parameter
        for param in ['page', 'p']:
            if param in params:
                params[param] = [str(page_number + 1)]
                break
        else:
            # Add page parameter if not present
            params['page'] = [str(page_number + 1)]
        
        # Handle offset-based pagination
        if 'offset' in params:
            current_offset = int(params['offset'][0])
            # Assume 20 items per page
            params['offset'] = [str(current_offset + 20)]
        
        # Rebuild URL
        new_query = urlencode(params, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
    
    def _get_click_next(
        self,
        html: str,
        current_url: str
    ) -> Optional[str]:
        """Get next URL from next button link"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
        
        for selector in self.NEXT_SELECTORS:
            element = soup.select_one(selector)
            if element:
                href = element.get('href')
                if href:
                    return urljoin(current_url, href)
        
        return None
    
    def _detect_infinite_scroll(self, html: str) -> bool:
        """Detect if page uses infinite scroll"""
        scroll_indicators = [
            'infinite-scroll',
            'infinitescroll',
            'load-on-scroll',
            'data-infinite',
            'endless-scroll',
        ]
        html_lower = html.lower()
        return any(ind in html_lower for ind in scroll_indicators)
    
    async def get_next_selector(
        self,
        pagination_type: PaginationType
    ) -> Optional[str]:
        """Get the selector to click for next page"""
        if pagination_type == PaginationType.CLICK:
            return ' | '.join(self.NEXT_SELECTORS)
        elif pagination_type == PaginationType.LOAD_MORE:
            return ' | '.join(self.LOAD_MORE_SELECTORS)
        return None
