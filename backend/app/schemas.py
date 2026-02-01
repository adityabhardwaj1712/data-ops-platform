from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID
from enum import Enum


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


class ScrapeConfigMetadata(BaseModel):
    site_type: Optional[str] = None  # e.g., "ecommerce", "profile"
    pagination_type: Optional[str] = None  # e.g., "url_param", "scroll"
    stability_score: int = Field(default=0, ge=0, le=5)
    success_count: int = 0
    failure_count: int = 0
    last_success_at: Optional[datetime] = None

# ============ JOB SCHEMAS ============

class JobCreate(BaseModel):
    description: str
    schema: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None
    config_metadata: Optional[ScrapeConfigMetadata] = None


class JobUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    config: Optional[Dict[str, Any]] = None
    config_metadata: Optional[ScrapeConfigMetadata] = None


class JobResponse(BaseModel):
    id: UUID
    description: str
    schema: Dict[str, Any]
    config: Optional[Dict[str, Any]]
    config_metadata: Optional[ScrapeConfigMetadata] = None
    status: JobStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ TASK SCHEMAS ============

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
    field_confidence: Optional[Dict[str, float]] = None  # Per-field confidence scores
    failure_reason: Optional[str] = None
    failure_message: Optional[str] = None
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ SCRAPE SCHEMAS ============

class ScrapeStrategy(str, Enum):
    AUTO = "auto"
    STATIC = "static"
    BROWSER = "browser"
    STEALTH = "stealth"


class ScrapeRequest(BaseModel):
    url: Optional[str] = None
    url_list: Optional[List[str]] = None
    prompt: Optional[str] = None
    schema: Dict[str, Any]
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


class ScrapeResult(BaseModel):
    success: bool
    status: Literal["success", "partial", "failed"] = "success"
    data: Optional[Dict[str, Any]] = None
    missing_fields: List[str] = []
    pages_scraped: int = 1
    strategy_used: str
    confidence: float = 0.0  # Numeric score: 0-100
    confidence_components: Dict[str, float] = {}
    screenshots: List[str] = []
    artifact_paths: List[str] = [] # HTML dumps, etc.
    validation_report: Optional[Dict[str, Any]] = None
    failure_reason: Optional[ScrapeFailureReason] = None
    failure_message: Optional[str] = None
    errors: List[str] = []
    metadata: Dict[str, Any] = {}
    debug_data: Optional[Dict[str, Any]] = None


# ============ HITL SCHEMAS ============

class HITLTaskResponse(BaseModel):
    task_id: UUID
    job_id: UUID
    payload: Dict[str, Any]
    current_data: Optional[Dict[str, Any]] = None


class HITLSubmit(BaseModel):
    data: Dict[str, Any]
    notes: Optional[str] = None


# ============ AUDIT SCHEMAS ============

class AuditLogResponse(BaseModel):
    id: UUID
    task_id: UUID
    action: str
    changes: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


# ============ FIELD-LEVEL CONFIDENCE SCHEMAS ============

class FieldConfidence(BaseModel):
    """Confidence score for individual fields"""
    value: Any
    confidence: float
    source: Optional[str] = None


class ConfidenceWeightedRecord(BaseModel):
    """Record with field-level confidence scores"""
    id: Optional[str] = None
    data: Dict[str, FieldConfidence]
    overall_confidence: float
    source_url: Optional[str] = None
    extracted_at: Optional[datetime] = None


# ============ INTENT TEMPLATE SCHEMAS ============

class IntentTemplateType(str, Enum):
    JOB_LISTING = "JOB_LISTING"
    PRODUCT = "PRODUCT"
    NEWS = "NEWS"
    EVENT = "EVENT"
    CONTACT = "CONTACT"
    CUSTOM = "CUSTOM"


class IntentTemplateCreate(BaseModel):
    name: str
    intent_type: IntentTemplateType
    description: str
    template_schema: Dict[str, Any]
    filters: Optional[Dict[str, Any]] = None


class IntentTemplateResponse(BaseModel):
    id: UUID
    name: str
    intent_type: IntentTemplateType
    description: str
    template_schema: Dict[str, Any]
    filters: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class IntentTemplateApply(BaseModel):
    template_id: UUID
    filters: Optional[Dict[str, Any]] = None
    sources: List[str]
    max_pages_per_source: int = Field(default=5, ge=1, le=100)


# ============ CHANGE DETECTION SCHEMAS ============

class ChangeType(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"


class FieldChange(BaseModel):
    field: str
    old_value: Any
    new_value: Any
    change_type: ChangeType
    confidence: Optional[float] = None


class RecordChange(BaseModel):
    record_id: str
    change_type: ChangeType
    field_changes: List[FieldChange]
    overall_confidence: float


class VersionDiff(BaseModel):
    from_version: int
    to_version: int
    changes: List[RecordChange]
    summary: Dict[str, int]  # Summary of change types


class VersionComparisonRequest(BaseModel):
    job_id: UUID
    from_version: Optional[int] = None  # If None, compare with previous version
    to_version: Optional[int] = None  # If None, compare with latest version


# ============ ROBOTS AWARENESS SCHEMAS ============

class RobotsCheckRequest(BaseModel):
    domain: str


class RobotsCheckResponse(BaseModel):
    domain: str
    allowed: bool
    crawl_delay: Optional[float] = None
    sitemap_urls: List[str] = []
    checked_at: datetime


# ============ EXPORT SCHEMAS ============

class ExportFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ExportRequest(BaseModel):
    job_id: UUID
    version: Optional[int] = None  # If None, export latest version
    format: ExportFormat = ExportFormat.EXCEL
    include_source_links: bool = True
    include_confidence: bool = True
    is_client_package: bool = False  # If True, bundles as professional ZIP


class ExportResponse(BaseModel):
    job_id: UUID
    version: int
    format: ExportFormat
    file_url: str
    row_count: int
    created_at: datetime
