from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # ======================
    # APP
    # ======================
    APP_NAME: str = "DataOps Platform"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ======================
    # DATABASE
    # ======================
    DATABASE_URL: str = "sqlite+aiosqlite:////app/data/dataops.db"

    # ======================
    # REDIS (OPTIONAL)
    # ======================
    ENABLE_REDIS: bool = False
    REDIS_URL: Optional[str] = None
    CACHE_TTL_DEFAULT: int = 300

    # ======================
    # BACKGROUND JOBS
    # ======================
    ENABLE_BACKGROUND_JOBS: bool = True

    # ======================
    # AI / GROQ
    # ======================
    ENABLE_AI_COPILOT: bool = False
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-70b-8192"  # ✅ REQUIRED DEFAULT

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

