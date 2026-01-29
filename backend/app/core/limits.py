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
    
    # Maximum browser instances (CRITICAL: prevents memory exhaustion)
    MAX_BROWSER_INSTANCES: int = 3
    
    # Maximum memory per browser instance (MB)
    BROWSER_MEMORY_LIMIT_MB: int = 512
    
    # Maximum memory per worker process (MB)
    MAX_WORKER_MEMORY_MB: int = 1024
    
    # Maximum screenshot file size (MB)
    MAX_SCREENSHOT_SIZE_MB: int = 5
    
    # Maximum stored versions per job
    MAX_VERSIONS_PER_JOB: int = 50
    
    # Maximum artifact storage per job (MB)
    MAX_ARTIFACT_STORAGE_MB: int = 100
    
    # ═══════════════════════════════════════════════════════════════
    # MODE-BASED CONFIGURATION (LOCAL vs PRODUCTION)
    # ═══════════════════════════════════════════════════════════════
    
    # Deployment mode: local | production
    DEPLOYMENT_MODE: str = "local"
    
    # Local mode overrides (for WSL / low-infra safety)
    LOCAL_MODE_MAX_WORKERS: int = 2
    LOCAL_MODE_MAX_BROWSER_INSTANCES: int = 1
    LOCAL_MODE_BROWSER_PARALLELISM: bool = False
    LOCAL_MODE_MAX_PAGES_PER_JOB: int = 20
    LOCAL_MODE_REQUEST_TIMEOUT: int = 20
    
    # Production mode settings
    PRODUCTION_MODE_MAX_WORKERS: int = 5
    PRODUCTION_MODE_MAX_BROWSER_INSTANCES: int = 3
    PRODUCTION_MODE_BROWSER_PARALLELISM: bool = True
    PRODUCTION_MODE_MAX_PAGES_PER_JOB: int = 500
    PRODUCTION_MODE_REQUEST_TIMEOUT: int = 30
    
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


class GuardrailRules:
    """
    Auto-decision logic for system safety.
    """
    @staticmethod
    def should_force_hitl(
        confidence: float, 
        consecutive_failures: int = 0,
        pages_without_data: int = 0
    ) -> tuple[bool, str]:
        """
        Check if HITL should be forced regardless of other settings.
        """
        # Rule 1: Confidence too low for auto-delivery
        if confidence < limits.CONFIDENCE_AUTO_ACCEPT:
            # Note: This just confirms we can't auto-accept. 
            # Real forcing happens if it's below mandatory threshold.
            if confidence < limits.CONFIDENCE_MANDATORY_REVIEW:
                return True, "Confidence below mandatory threshold"
        
        # Rule 2: Consecutive failures logic (placeholder for DB check)
        if consecutive_failures >= 2:
            return True, "2+ consecutive failures detected"
            
        # Rule 3: Scraped pages but got no data (Layout change?)
        if pages_without_data >= 3:
            return True, "Scraped 3+ pages with empty results"
            

        
        return False, ""


class AutomationRules:
    """
    Determininstic rules for safe automation (Sprint 12).
    """
    @staticmethod
    def should_use_stable_config(metadata: Optional[dict]) -> bool:
        """
        Check if we should reuse a config without asking.
        Criteria: Success >= 3, Stability Score >= 4.
        """
        if not metadata:
            return False
            
        success_count = metadata.get("success_count", 0)
        stability_score = metadata.get("stability_score", 0)
        
        return success_count >= 3 and stability_score >= 4

    @staticmethod
    def recommend_strategy(site_type: str, current_fails: int = 0) -> str:
        """
        Recommend scrape strategy based on site type and failure history.
        """
        # If simple requests failing, switch to browser
        if current_fails > 0:
            return "browser"
            
        if site_type == "ecommerce":
            return "browser"  # Safer default for ecomm
        elif site_type == "listing":
            return "static"   # Faster for paginated lists
            
        return "auto"




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


def get_mode_specific_limits() -> dict:
    """
    Get resource limits based on deployment mode.
    
    Returns:
        Dictionary with mode-specific limits
    """
    mode = limits.DEPLOYMENT_MODE.lower()
    
    if mode == "production":
        return {
            "max_workers": limits.PRODUCTION_MODE_MAX_WORKERS,
            "max_browser_instances": limits.PRODUCTION_MODE_MAX_BROWSER_INSTANCES,
            "browser_parallelism": limits.PRODUCTION_MODE_BROWSER_PARALLELISM,
            "max_pages_per_job": limits.PRODUCTION_MODE_MAX_PAGES_PER_JOB,
            "request_timeout": limits.PRODUCTION_MODE_REQUEST_TIMEOUT,
        }
    else:  # local mode (default)
        return {
            "max_workers": limits.LOCAL_MODE_MAX_WORKERS,
            "max_browser_instances": limits.LOCAL_MODE_MAX_BROWSER_INSTANCES,
            "browser_parallelism": limits.LOCAL_MODE_BROWSER_PARALLELISM,
            "max_pages_per_job": limits.LOCAL_MODE_MAX_PAGES_PER_JOB,
            "request_timeout": limits.LOCAL_MODE_REQUEST_TIMEOUT,
        }


def get_effective_browser_limit() -> int:
    """
    Get effective browser instance limit based on mode.
    """
    mode_limits = get_mode_specific_limits()
    return min(
        limits.MAX_BROWSER_INSTANCES,
        mode_limits["max_browser_instances"]
    )


def get_effective_worker_limit() -> int:
    """
    Get effective worker limit based on mode.
    """
    mode_limits = get_mode_specific_limits()
    return mode_limits["max_workers"]

