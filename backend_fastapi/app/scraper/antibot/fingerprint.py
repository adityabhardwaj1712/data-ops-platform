"""
Browser Fingerprint Randomization
Generates realistic browser fingerprints to avoid detection
"""
import random
from typing import Dict, Any, Optional


# Common screen resolutions
VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
    {"width": 2560, "height": 1440},
]

# Common timezones
TIMEZONES = [
    "America/New_York",
    "America/Los_Angeles",
    "America/Chicago",
    "Europe/London",
    "Europe/Paris",
    "Asia/Tokyo",
]

# Common locales
LOCALES = [
    "en-US",
    "en-GB",
    "en-CA",
]

# Common geolocations (optional, for sites that check)
GEOLOCATIONS = [
    {"latitude": 40.7128, "longitude": -74.0060},  # New York
    {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles
    {"latitude": 51.5074, "longitude": -0.1278},  # London
    {"latitude": 48.8566, "longitude": 2.3522},  # Paris
]


def get_stealth_config() -> Dict[str, Any]:
    """
    Generate a randomized browser configuration for stealth scraping.
    
    Returns:
        Dictionary with viewport, timezone, locale, and optional geolocation
    """
    config = {
        "viewport": random.choice(VIEWPORTS),
        "timezone": random.choice(TIMEZONES),
        "locale": random.choice(LOCALES),
    }
    
    # 30% chance to include geolocation
    if random.random() < 0.3:
        config["geolocation"] = random.choice(GEOLOCATIONS)
    
    return config


def get_webgl_fingerprint() -> Dict[str, str]:
    """
    Generate fake WebGL fingerprint data.
    Used to spoof canvas fingerprinting detection.
    """
    vendors = [
        "Google Inc. (NVIDIA)",
        "Google Inc. (Intel)",
        "Google Inc. (AMD)",
    ]
    
    renderers = [
        "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)",
    ]
    
    return {
        "vendor": random.choice(vendors),
        "renderer": random.choice(renderers)
    }

def get_hardware_config() -> Dict[str, Any]:
    """
    Generate hardware-level fingerprints (memory, cpu, battery).
    """
    return {
        "memory": random.choice([4, 8, 16, 32]),
        "cpu": random.choice([2, 4, 8, 12, 16]),
        "battery_level": round(random.uniform(0.1, 1.0), 2),
        "is_charging": random.choice([True, False]),
        "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"])
    }
