"""
Base Strategy Interface
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class BaseStrategy(ABC):
    """Abstract base class for scraping strategies"""
    
    @abstractmethod
    async def fetch(self, url: str, **kwargs) -> Tuple[str, str, Optional[str]]:
        """
        Fetch content from a URL.
        
        Returns:
            Tuple of (markdown_content, raw_html, screenshot_path)
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the strategy name"""
        pass
