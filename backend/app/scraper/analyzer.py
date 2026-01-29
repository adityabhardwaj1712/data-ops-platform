import re
from urllib.parse import urlparse
from typing import List

# Sites known to require special handling
BROWSER_REQUIRED_PATTERNS = [
    r'twitter\.com', r'x\.com',
    r'linkedin\.com',
    r'facebook\.com',
    r'instagram\.com',
    r'.*spa.*',
    r'react\.',
    r'angular\.'
]

STEALTH_REQUIRED_PATTERNS = [
    r'amazon\.',
    r'cloudflare',
    r'linkedin\.com',
    r'zillow\.com',
    r'glassdoor\.com'
]

class ScrapeAnalyzer:
    """
    Analyzes URLs and page content to determine the best scraping strategy.
    """
    
    @staticmethod
    def detect_strategy(url: str, stealth_mode: bool = False) -> str:
        """
        Detects the appropriate strategy (static, browser, stealth) for a URL.
        """
        if stealth_mode:
            return "stealth"

        domain = urlparse(url).netloc.lower()

        for pattern in STEALTH_REQUIRED_PATTERNS:
            if re.search(pattern, domain, re.IGNORECASE):
                return "stealth"

        for pattern in BROWSER_REQUIRED_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return "browser"

        return "static"

    @staticmethod
    def analyze_complexity(html: str) -> dict:
        """
        Optional: Analyze extracted HTML to suggest if a switch to a heavier 
        strategy is needed (e.g., detecting CAPTCHAs or empty content).
        """
        complexity = {
            "is_empty": len(html.strip()) < 500,
            "has_captcha": any(kw in html.lower() for kw in ["captcha", "robot", "security check"]),
            "is_js_heavy": "javascript" in html.lower() and len(html) < 2000
        }
        return complexity
