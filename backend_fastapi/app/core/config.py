from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ============================================
    # CORE SETTINGS
    # ============================================
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/dataops.db"
    SECRET_KEY: str = "dev-only-secret-key" # Moved from App section

    # ============================================
    # FEATURE FLAGS (Enable/Disable Features)
    # ============================================
    # Core features (always enabled)
    ENABLE_SCRAPING: bool = True
    ENABLE_JOBS: bool = True
    ENABLE_BACKGROUND_JOBS: bool = True # Existing, moved here

    # Visualization features
    ENABLE_VISUALIZATION: bool = True
    ENABLE_ADVANCED_CHARTS: bool = True

    # AI features (Enabled via Groq)
    ENABLE_AI_COPILOT: bool = True
    AI_MODEL: str = "llama3-70b-8192"  # Groq model
    AI_BASE_URL: str = "https://api.groq.com/openai/v1"

    # Data quality features
    ENABLE_QUALITY_CHECKS: bool = True
    ENABLE_ANOMALY_DETECTION: bool = True  # Enabled (Free via Groq)

    # Cost & usage analytics
    ENABLE_COST_ANALYTICS: bool = True
    ENABLE_USAGE_ALERTS: bool = True

    # Enterprise features (Enabled for "Project Safe" mode)
    ENABLE_SSO: bool = False # Keep disabled for local/solo use unless requested
    ENABLE_AUDIT_LOGS: bool = True
    ENABLE_MULTI_TENANCY: bool = False

    # =====================
    # LLM (Groq – SAFE) - Existing section, kept
    # =====================
    # Optional on purpose → no crash if missing
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-70b-8192"

    # (Future fallback – not required)
    OPENAI_API_KEY: Optional[str] = None

    # =====================
    # Scraping - Existing section, kept
    # =====================
    DEFAULT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    MAX_PAGES: int = 100

    # =====================
    # Proxy (optional)
    # =====================
    PROXY_URL: Optional[str] = None
    PROXY_ROTATION_ENABLED: bool = False

    # =====================
    # App
    # =====================
    DEBUG: bool = False
    SECRET_KEY: str = "dev-only-secret-key"

    # =====================
    # Logging
    # =====================
    LOG_LEVEL: str = "INFO"
    LOG_JSON_FORMAT: bool = False

    # =====================
    # Rate Limiting
    # =====================
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 120

    # =====================
    # Background Jobs
    # =====================
    ENABLE_BACKGROUND_JOBS: bool = True
    MAX_CONCURRENT_JOBS: int = 10

    # =====================
    # Export
    # =====================
    EXPORT_DIR: str = "exports"
    EXPORT_CLEANUP_DAYS: int = 7

    # =====================
    # Webhooks
    # =====================
    WEBHOOK_TIMEOUT: int = 10
    WEBHOOK_MAX_RETRIES: int = 3

    class Config:
        # .env is OPTIONAL, not required
        env_file = ".env"
        case_sensitive = False


settings = Settings()
