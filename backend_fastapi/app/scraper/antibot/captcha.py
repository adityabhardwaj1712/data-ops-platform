"""
PRO FEATURE: CAPTCHA DETECTION
Detects security blocks and triggers HITL or AI solving.
"""
import re
from typing import Optional

class CaptchaDetector:
    """
    Identifies if a page response is a CAPTCHA challenge.
    """
    
    # Common captcha fingerprints in HTML
    PATTERNS = [
        r'g-recaptcha',
        r'h-captcha',
        r'cf-challenge',
        r'captcha',
        r'distil-captcha',
        r'px-captcha',
        r'verify-human',
        r'Robot Check',
        r'Checking your browser before accessing',
        r'Access to this page has been denied',
    ]

    def is_captcha(self, html: str) -> bool:
        """Check if HTML content contains a CAPTCHA"""
        if not html:
            return False
            
        for pattern in self.PATTERNS:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        return False

    def get_type(self, html: str) -> Optional[str]:
        """Identify the type of CAPTCHA detected"""
        if 'g-recaptcha' in html: return "Google reCAPTCHA"
        if 'h-captcha' in html: return "hCaptcha"
        if 'cf-challenge' in html: return "Cloudflare Challenge"
        if 'px-captcha' in html: return "PerimeterX"
        if 'distil' in html: return "Distil Networks"
        return "Generic CAPTCHA / Block"

# Global singleton
captcha_detector = CaptchaDetector()
