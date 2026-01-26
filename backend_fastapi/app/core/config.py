from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # =====================
    # Database
    # =====================
    DATABASE_URL: str = "sqlite+aiosqlite:///./dataops.db"

    # =====================
    # LLM (Groq – SAFE)
    # =====================
    # Optional on purpose → no crash if missing
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-70b-8192"

    # (Future fallback – not required)
    OPENAI_API_KEY: Optional[str] = None

    # =====================
    # Scraping
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
