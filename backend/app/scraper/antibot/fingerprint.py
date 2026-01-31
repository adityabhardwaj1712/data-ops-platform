import random
from typing import Dict, Any

def get_stealth_config() -> Dict[str, Any]:
    """
    Returns a randomized stealth configuration for browser contexts.
    Includes viewport, locale, timezone, and geolocation.
    """
    # Pro-grade viewport pool
    viewports = [
        {"width": 1920, "height": 1080},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
        {"width": 1366, "height": 768},
        {"width": 1280, "height": 720}
    ]
    
    # Pro-grade locale/timezone pool
    configs = [
        {"locale": "en-US", "timezone": "America/New_York"},
        {"locale": "en-GB", "timezone": "Europe/London"},
        {"locale": "en-IN", "timezone": "Asia/Kolkata"},
        {"locale": "de-DE", "timezone": "Europe/Berlin"},
        {"locale": "fr-FR", "timezone": "Europe/Paris"}
    ]
    
    selected_config = random.choice(configs)
    
    return {
        "viewport": random.choice(viewports),
        "locale": selected_config["locale"],
        "timezone": selected_config["timezone"],
        "geolocation": None, # Could be added for proxy-specific locales
    }
