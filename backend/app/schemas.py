from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID
from enum import Enum


# ======================================================
# ENUMS
# ======================================================

class JobStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    VALIDATING = "VALIDATING"
    NEEDS_HITL = "NEEDS_HITL"
    RERUNNING = "RERUNNING"
    COMPLETED = "COMPLETED"
    FAILED_FINAL = "FAILED_FINAL"
    ARCHIVED = "ARCHIVED"


class ScrapeFailureReason(str, Enum):
    FETCH_FAILED = "FETCH_FAILED"
    JS_TIMEOUT = "JS_TIMEOUT"
    SELECTOR_MISSING = "SELECTOR_MISSING"
    EMPTY_DATA = "EMPTY_DATA"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    ANTI_BOT_SUSPECTED = "ANTI_BOT_SUSPECTED"
    UNKNOWN = "UNKNOWN"


class TaskType(str, Enum):
    SCRAPE = "SCRAPE"
    VERIFY = "VERIFY"
    HUMAN = "HUMAN"
    QUALITY = "QUALITY"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEEDS_HITL = "NEEDS_HITL"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ======================================================
# CONFIG METADATA
# ======================================================

class ScrapeConfigMetadata(BaseModel):
    site_type: Optional[str] = None
    pagination_type: Optional[str] = None
    stability_score: int = Field(default=0, ge=0, le=5)
    success_count: int = 0
    failure_count: int = 0
    last_success_at: Optional[datetime] = None


# ======================================================
# JOB SCHEMAS
# ======================================================

class JobCreate(BaseModel):
    description: str
    extract_schema: Dict[str, Any] = Field(..., alias="schema")
    config: Optional[Dict[str, Any]] = None
    config_metadata: Optional[ScrapeConfigMetadata] = None

    class Config:
        populate_by_name = True


class JobUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    extract_schema: Optional[Dict[str, Any]] = Field(None, alias="schema")
    config: Optional[Dict[str, Any]] = None
    config_metadata: Optional[ScrapeConfigMetadata] = None

    class Config:
        populate_by_name = True


class JobResponse(BaseModel):
    id: UUID
    description: str
    extract_schema: Dict[str, Any] = Field(..., alias="schema")
    config: Optional[Dict[str, Any]]
    config_metadata: Optional[ScrapeConfigMetadata] = None
    status: JobStatus
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


# ======================================================
# TASK SCHEMAS
# ======================================================

class TaskCreate(BaseModel):
    job_id: UUID
    type: TaskType
    payload: Dict[str, Any]


class TaskResponse(BaseModel):
    id: UUID
    job_id: UUID
    type: TaskType
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    status: TaskStatus
    confidence: Optional[float]
    confidence_components: Optional[Dict[str, float]] = None
    field_confidence: Optional[Dict[str, float]] = None
    failure_reason: Optional[str] = None
    failure_message: Optional[str] = None
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ======================================================
# SCRAPE SCHEMAS
# ======================================================

class ScrapeStrategy(str, Enum):
    AUTO = "auto"              # Auto-detect best strategy
    STATIC = "static"          # BeautifulSoup for server-rendered HTML
    BROWSER = "browser"        # Playwright for JS-heavy sites
    API = "api"                # Direct JSON API scraping
    AUTHENTICATED = "auth"     # Login-required scraping
    CRAWLER = "crawler"        # Multi-page crawling with link following
    DOCUMENT = "document"      # PDF/Excel/CSV extraction
    OCR = "ocr"                # Image-to-text extraction
    STREAMING = "streaming"    # Real-time monitoring/polling
    HYBRID = "hybrid"          # Combination approach
    STEALTH = "stealth"


# ======================================================
# STRATEGY-SPECIFIC CONFIGURATION MODELS
# ======================================================

class AuthMethod(str, Enum):
    COOKIES = "cookies"
    FORM_LOGIN = "form_login"
    API_TOKEN = "api_token"
    BEARER = "bearer"


class AuthConfig(BaseModel):
    """Configuration for authenticated scraping"""
    method: AuthMethod
    credentials: Optional[Dict[str, str]] = None  # username/password or token
    login_url: Optional[str] = None
    cookies: Optional[List[Dict[str, str]]] = None
    headers: Optional[Dict[str, str]] = None


class CrawlConfig(BaseModel):
    """Configuration for multi-page crawling"""
    max_depth: int = Field(default=2, ge=1, le=5)
    max_pages: int = Field(default=50, ge=1, le=500)
    follow_external_links: bool = False
    url_patterns: Optional[List[str]] = None  # Regex patterns to match
    respect_robots_txt: bool = True
    crawl_delay_seconds: float = Field(default=2.0, ge=0.5, le=10.0)


class StreamingConfig(BaseModel):
    """Configuration for real-time monitoring"""
    poll_interval_seconds: int = Field(default=60, ge=10, le=3600)
    max_duration_minutes: int = Field(default=60, ge=1, le=1440)
    change_threshold: float = Field(default=0.1, ge=0.0, le=1.0)
    alert_on_change: bool = True
    webhook_url: Optional[str] = None


class DocumentConfig(BaseModel):
    """Configuration for document extraction"""
    extract_tables: bool = True
    extract_text: bool = True
    extract_images: bool = False
    page_range: Optional[str] = None  # e.g., "1-5" or "all"


class OCRConfig(BaseModel):
    """Configuration for OCR extraction"""
    language: str = "eng"  # Tesseract language code
    preprocess: bool = True  # Image preprocessing (denoising, deskewing)
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)


class ScrapeRequest(BaseModel):
    url: Optional[str] = None
    url_list: Optional[List[str]] = None
    prompt: Optional[str] = None

    extract_schema: Dict[str, Any] = Field(..., alias="schema")

    strategy: ScrapeStrategy = ScrapeStrategy.AUTO
    max_pages: int = Field(default=1, ge=1, le=100)
    stealth_mode: bool = False
    use_proxy: bool = False
    wait_for_selector: Optional[str] = None
    timeout: int = Field(default=30, ge=5, le=120)
    filters: Optional[Dict[str, Any]] = None
    debug: bool = False
    auto_detect: bool = False
    sla_seconds: int = Field(default=300, ge=30)
    webhook_url: Optional[str] = None
    
    # Strategy-specific configurations
    auth_config: Optional[AuthConfig] = None
    crawl_config: Optional[CrawlConfig] = None
    streaming_config: Optional[StreamingConfig] = None
    document_config: Optional[DocumentConfig] = None
    ocr_config: Optional[OCRConfig] = None
    api_endpoint: Optional[str] = None  # For API scraping

    class Config:
        populate_by_name = True


class ScrapeResult(BaseModel):
    success: bool
    status: Literal["success", "partial", "failed"] = "success"
    data: Optional[Dict[str, Any]] = None
    missing_fields: List[str] = []
    pages_scraped: int = 1
    strategy_used: str
    confidence: float = 0.0
    confidence_components: Dict[str, float] = {}
    screenshots: List[str] = []
    artifact_paths: List[str] = []
    validation_report: Optional[Dict[str, Any]] = None
    failure_reason: Optional[ScrapeFailureReason] = None
    failure_message: Optional[str] = None
    errors: List[str] = []
    metadata: Dict[str, Any] = {}
    debug_data: Optional[Dict[str, Any]] = None

# ======================================================
# HITL SCHEMAS
# ======================================================

class HITLTaskResponse(BaseModel):
    task_id: UUID
    job_id: UUID
    payload: Dict[str, Any]
    current_data: Optional[Dict[str, Any]] = None

class HITLSubmit(BaseModel):
    data: Dict[str, Any]
    notes: Optional[str] = None

# ======================================================
# ROBOTS.TXT SCHEMAS
# ======================================================

class RobotsCheckRequest(BaseModel):
    domain: str

class RobotsCheckResponse(BaseModel):
    domain: str
    allowed: bool
    crawl_delay: Optional[float] = None
    sitemap_urls: Optional[List[str]] = None
    checked_at: datetime

# ======================================================
# EXPORT SCHEMAS
# ======================================================

class ExportFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

class ExportRequest(BaseModel):
    job_id: UUID
    version: Optional[int] = None
    format: ExportFormat = ExportFormat.EXCEL
    include_confidence: bool = True
    is_client_package: bool = False

class ExportResponse(BaseModel):
    job_id: UUID
    version: int
    format: ExportFormat
    file_url: str
    row_count: int
    created_at: datetime
