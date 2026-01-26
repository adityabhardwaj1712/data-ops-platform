"""
Robots.txt Checker Service

Handles robots.txt parsing, caching, and compliance checking.
Ensures ethical scraping practices.
"""
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.models import RobotsTxt
from app.db.session import get_db


class RobotsChecker:
    """Service for checking and respecting robots.txt"""

    def __init__(self):
        self.cache: Dict[str, RobotsTxt] = {}
        self.cache_timeout = timedelta(hours=24)  # Cache robots.txt for 24 hours

    async def check_url_allowed(
        self,
        url: str,
        user_agent: str = "*",
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Check if URL is allowed by robots.txt

        Args:
            url: URL to check
            user_agent: User agent string
            db: Database session (optional)

        Returns:
            Dict with allowed status, crawl delay, and sitemap URLs
        """
        domain = self._extract_domain(url)

        # Check cache first
        cached = self._get_cached_robots(domain)
        if cached and self._is_cache_valid(cached):
            return self._parse_cached_result(cached, url, user_agent)

        # Fetch from database or web
        robots_data = await self._fetch_robots_data(domain, db)

        if robots_data:
            # Cache in memory
            self.cache[domain] = robots_data
            return self._parse_cached_result(robots_data, url, user_agent)

        # If no robots.txt found, assume allowed
        return {
            "allowed": True,
            "crawl_delay": None,
            "sitemap_urls": [],
            "checked_at": datetime.utcnow(),
            "source": "default"
        }

    async def _fetch_robots_data(self, domain: str, db: Optional[AsyncSession] = None) -> Optional[RobotsTxt]:
        """Fetch robots.txt data from database or web"""
        # Try database first
        if db:
            stmt = select(RobotsTxt).where(RobotsTxt.domain == domain)
            result = await db.execute(stmt)
            robots_data = result.scalar_one_or_none()

            if robots_data and self._is_cache_valid(robots_data):
                return robots_data

        # Fetch from web
        robots_url = f"https://{domain}/robots.txt"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(robots_url)

                if response.status_code == 200:
                    content = response.text
                    crawl_delay, sitemap_urls = self._parse_robots_content(content)

                    # Save to database
                    if db:
                        robots_data = RobotsTxt(
                            domain=domain,
                            content=content,
                            crawl_delay=crawl_delay,
                            sitemap_urls=sitemap_urls,
                            expires_at=datetime.utcnow() + self.cache_timeout
                        )
                        db.add(robots_data)
                        await db.commit()
                        await db.refresh(robots_data)
                        return robots_data
                    else:
                        # Return in-memory object
                        return RobotsTxt(
                            domain=domain,
                            content=content,
                            crawl_delay=crawl_delay,
                            sitemap_urls=sitemap_urls,
                            expires_at=datetime.utcnow() + self.cache_timeout
                        )

        except Exception as e:
            # Log error but don't fail - assume allowed if robots.txt unavailable
            print(f"Error fetching robots.txt for {domain}: {e}")

        return None

    def _parse_robots_content(self, content: str) -> tuple[Optional[float], List[str]]:
        """Parse robots.txt content to extract crawl delay and sitemap URLs"""
        crawl_delay = None
        sitemap_urls = []

        lines = content.split('\n')
        current_user_agent = None

        for line in lines:
            line = line.strip().lower()
            if not line or line.startswith('#'):
                continue

            if line.startswith('user-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            elif line.startswith('crawl-delay:') and current_user_agent in ['*', 'googlebot']:
                try:
                    crawl_delay = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                if sitemap_url:
                    sitemap_urls.append(sitemap_url)

        return crawl_delay, sitemap_urls

    def _parse_cached_result(self, robots_data: RobotsTxt, url: str, user_agent: str) -> Dict[str, Any]:
        """Parse cached robots.txt data and check URL allowance"""
        try:
            # Use Python's RobotFileParser to check allowance
            parser = RobotFileParser()
            parser.parse(robots_data.content.split('\n'))

            allowed = parser.can_fetch(user_agent, url)

            return {
                "allowed": allowed,
                "crawl_delay": robots_data.crawl_delay,
                "sitemap_urls": robots_data.sitemap_urls or [],
                "checked_at": robots_data.last_updated or datetime.utcnow(),
                "source": "cached"
            }
        except Exception:
            # If parsing fails, assume allowed
            return {
                "allowed": True,
                "crawl_delay": robots_data.crawl_delay,
                "sitemap_urls": robots_data.sitemap_urls or [],
                "checked_at": robots_data.last_updated or datetime.utcnow(),
                "source": "cached_parse_error"
            }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc

    def _get_cached_robots(self, domain: str) -> Optional[RobotsTxt]:
        """Get robots data from memory cache"""
        return self.cache.get(domain)

    def _is_cache_valid(self, robots_data: RobotsTxt) -> bool:
        """Check if cached robots data is still valid"""
        if not robots_data.expires_at:
            return False
        return datetime.utcnow() < robots_data.expires_at

    async def get_respectful_delay(self, url: str, user_agent: str = "*", db: Optional[AsyncSession] = None) -> float:
        """
        Get the crawl delay that should be respected for this URL

        Returns delay in seconds, minimum 1 second
        """
        result = await self.check_url_allowed(url, user_agent, db)
        delay = result.get("crawl_delay", 1.0)
        return max(delay or 1.0, 1.0)  # Minimum 1 second delay


# Global instance
robots_checker = RobotsChecker()