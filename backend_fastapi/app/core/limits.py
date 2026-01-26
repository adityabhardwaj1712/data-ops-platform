"""
8️⃣ SAFE DEFAULTS - Platform Limits
Configuration for platform-wide limits to protect resources

Protects:
- Your EC2
- Your Docker containers
- Your sanity
"""
from pydantic_settings import BaseSettings
from typing import Optional


class PlatformLimits(BaseSettings):
    """
    Platform-wide limits and defaults.
    All limits can be overridden via environment variables.
    """
    
    # ═══════════════════════════════════════════════════════════════
    # JOB LIMITS
    # ═══════════════════════════════════════════════════════════════
    
    # Maximum URLs per single job
    MAX_URLS_PER_JOB: int = 50
    
    # Maximum pages to scrape per URL
    MAX_PAGES_PER_URL: int = 20
    
    # Maximum total pages per job (URLs × pages)
    MAX_TOTAL_PAGES_PER_JOB: int = 500
    
    # Maximum concurrent jobs
    MAX_CONCURRENT_JOBS: int = 10
    
    # ═══════════════════════════════════════════════════════════════
    # SCRAPING LIMITS
    # ═══════════════════════════════════════════════════════════════
    
    # Maximum concurrent scrapes across all jobs
    MAX_CONCURRENT_SCRAPES: int = 5
    
    # Maximum requests per domain per minute
    REQUESTS_PER_DOMAIN_PER_MINUTE: int = 10
    
    # Maximum retries per scrape
    MAX_SCRAPE_RETRIES: int = 3
    
    # Request timeout in seconds
    REQUEST_TIMEOUT: int = 30
    
    # Maximum page load time for browser scrapes
    BROWSER_TIMEOUT: int = 60
    
    # ═══════════════════════════════════════════════════════════════
    # CONTENT LIMITS
    # ═══════════════════════════════════════════════════════════════
    
    # Maximum HTML size to process (10MB)
    MAX_HTML_SIZE_BYTES: int = 10 * 1024 * 1024
    
    # Maximum content length for LLM extraction (8000 chars)
    MAX_LLM_CONTENT_LENGTH: int = 8000
    
    # Maximum items per extraction
    MAX_ITEMS_PER_EXTRACTION: int = 100
    
    # ═══════════════════════════════════════════════════════════════
    # QUALITY LIMITS
    # ═══════════════════════════════════════════════════════════════
    
    # Minimum confidence to auto-accept (0.9 = 90%)
    CONFIDENCE_AUTO_ACCEPT: float = 0.9
    
    # Minimum confidence for optional human review
    CONFIDENCE_OPTIONAL_REVIEW: float = 0.5
    
    # Below this, mandatory human review
    CONFIDENCE_MANDATORY_REVIEW: float = 0.5
    
    # Maximum time for HITL task before auto-skip (hours)
    HITL_TIMEOUT_HOURS: int = 24
    
    # ═══════════════════════════════════════════════════════════════
    # RESOURCE LIMITS
    # ═══════════════════════════════════════════════════════════════
    
    # Maximum memory per browser instance (MB)
    BROWSER_MEMORY_LIMIT_MB: int = 512
    
    # Maximum screenshot file size (MB)
    MAX_SCREENSHOT_SIZE_MB: int = 5
    
    # Maximum stored versions per job
    MAX_VERSIONS_PER_JOB: int = 50
    
    # ═══════════════════════════════════════════════════════════════
    # RATE LIMITING (API)
    # ═══════════════════════════════════════════════════════════════
    
    # Maximum API requests per minute per user
    API_RATE_LIMIT_PER_MINUTE: int = 60
    
    # Maximum pipeline requests per hour
    PIPELINE_RATE_LIMIT_PER_HOUR: int = 100
    
    class Config:
        env_file = ".env"
        env_prefix = "LIMIT_"


# Global instance with defaults
limits = PlatformLimits()


def validate_job_request(
    urls: list,
    max_pages_per_url: int = 1
) -> tuple[bool, str]:
    """
    Validate a job request against platform limits.
    
    Returns:
        (is_valid, error_message)
    """
    if len(urls) > limits.MAX_URLS_PER_JOB:
        return False, f"Too many URLs. Maximum: {limits.MAX_URLS_PER_JOB}"
    
    if max_pages_per_url > limits.MAX_PAGES_PER_URL:
        return False, f"Too many pages per URL. Maximum: {limits.MAX_PAGES_PER_URL}"
    
    total_pages = len(urls) * max_pages_per_url
    if total_pages > limits.MAX_TOTAL_PAGES_PER_JOB:
        return False, f"Too many total pages. Maximum: {limits.MAX_TOTAL_PAGES_PER_JOB}"
    
    return True, ""


def get_confidence_action(confidence: float) -> str:
    """
    Determine action based on confidence score.
    
    Returns:
        "auto_accept" | "optional_review" | "mandatory_review"
    """
    if confidence >= limits.CONFIDENCE_AUTO_ACCEPT:
        return "auto_accept"
    elif confidence >= limits.CONFIDENCE_OPTIONAL_REVIEW:
        return "optional_review"
    else:
        return "mandatory_review"
