from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class RobotsChecker:
    """
    Check robots.txt compliance for URLs.
    """
    
    async def check_url_allowed(self, url: str) -> bool:
        """
        Check whether scraping is allowed for a URL.
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if allowed, False otherwise
        """
        parsed = urlparse(url)
        
        # Future: fetch and parse robots.txt here
        # Currently allow all
        logger.debug(f"Robots.txt check for {parsed.netloc}: allowed")
        return True


# Global instance
robots_checker = RobotsChecker()

