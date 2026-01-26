"""
Static HTTP Strategy
Fast and lightweight scraping using httpx
Best for simple HTML pages without JavaScript rendering
"""
import httpx
import trafilatura
from typing import Tuple, Optional, Dict
from app.scraper.strategies.base import BaseStrategy
from app.scraper.antibot.headers import get_random_headers


class StaticStrategy(BaseStrategy):
    """
    Fast HTTP-based scraping strategy.
    
    Uses httpx for async requests and trafilatura for content extraction.
    Best for:
    - Static HTML pages
    - News articles
    - Blogs
    - Documentation sites
    """
    
    def get_name(self) -> str:
        return "static"
    
    async def fetch(
        self,
        url: str,
        timeout: int = 30,
        use_proxy: bool = False,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Fetch page content using HTTP request.
        
        Args:
            url: Target URL
            timeout: Request timeout in seconds
            use_proxy: Whether to use proxy (not implemented yet)
            headers: Custom headers to use
            
        Returns:
            Tuple of (markdown_content, raw_html)
        """
        # Use random realistic headers
        request_headers = headers or get_random_headers()
        
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            http2=True
        ) as client:
            response = await client.get(url, headers=request_headers)
            response.raise_for_status()
            
            html = response.text
            
            # Extract main content as markdown
            markdown = trafilatura.extract(
                html,
                output_format="markdown",
                include_links=True,
                include_tables=True,
                include_images=True
            )
            
            if not markdown:
                # Fallback: try with less strict settings
                markdown = trafilatura.extract(
                    html,
                    output_format="markdown",
                    no_fallback=False
                )
            
            return markdown or "", html
