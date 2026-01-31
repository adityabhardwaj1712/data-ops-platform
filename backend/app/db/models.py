from sqlalchemy import Column, String, Text, JSON, DateTime, Float, Integer, ForeignKey, Enum as SQLEnum, TypeDecorator, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid
import enum

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as string without hyphens.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class JobStatus(str, enum.Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    VALIDATING = "VALIDATING"
    NEEDS_HITL = "NEEDS_HITL"
    RERUNNING = "RERUNNING"
    COMPLETED = "COMPLETED"
    FAILED_FINAL = "FAILED_FINAL"
    ARCHIVED = "ARCHIVED"


class TaskType(str, enum.Enum):
    SCRAPE = "SCRAPE"
    VERIFY = "VERIFY"
    HUMAN = "HUMAN"
    QUALITY = "QUALITY"


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEEDS_HITL = "NEEDS_HITL"


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(Integer, nullable=True)  # Optional user reference
    description = Column(Text, nullable=False)
    schema = Column(JSON, nullable=False)
    config = Column(JSON, nullable=True)
    config_metadata = Column(JSON, nullable=True)  # Stores sustainability stats
    status = Column(SQLEnum(JobStatus), default=JobStatus.CREATED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="job", cascade="all, delete-orphan")
    versions = relationship("DatasetVersion", back_populates="job", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(GUID(), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    is_seed = Column(Integer, default=0, nullable=False)  # Using 0/1 for SQLite compatibility
    type = Column(SQLEnum(TaskType), nullable=False)
    payload = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    confidence = Column(Float, nullable=True)  # Overall record confidence
    confidence_components = Column(JSON, nullable=True)  # Breakdown: row_count, field_completeness, etc.
    field_confidence = Column(JSON, nullable=True)  # Per-field confidence scores
    failure_reason = Column(String(50), nullable=True)  # Enum value
    failure_message = Column(Text, nullable=True)      # Human-readable
    retry_count = Column(Integer, default=0)
    config_version = Column(Integer, nullable=True)    # Which config version was used
    assigned_to = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="tasks")
    children = relationship("Task", backref=relationship("parent", remote_side=[id]))
    audit_logs = relationship("AuditLog", back_populates="task", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    task_id = Column(GUID(), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    actor_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    changes = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="audit_logs")


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    data_location = Column(String(255), nullable=False)
    row_count = Column(Integer, nullable=False)
    confidence_summary = Column(JSON, nullable=True)
    change_summary = Column(JSON, nullable=True)  # Track what changed from previous version
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="versions")


class RobotsTxt(Base):
    """Store robots.txt information for domains"""
    __tablename__ = "robots_txt"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    crawl_delay = Column(Float, nullable=True)
    sitemap_urls = Column(JSON, nullable=True)  # List of sitemap URLs
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class IntentTemplate(Base):
    """Predefined intent templates for common use cases"""
    __tablename__ = "intent_templates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    intent_type = Column(String(50), nullable=False)  # JOB_LISTING, PRODUCT, NEWS, etc.
    description = Column(Text, nullable=False)
    template_schema = Column(JSON, nullable=False)  # Expected data structure
    filters = Column(JSON, nullable=True)  # Default filters for this template
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobConfig(Base):
    """Versioned configurations for a job"""
    __tablename__ = "job_configs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    config = Column(JSON, nullable=False)
    config_metadata = Column(JSON, nullable=True)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)


class DomainMemory(Base):
    """Silent Learning Engine: Remembers best strategies per domain"""
    __tablename__ = "domain_memory"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), nullable=False, unique=True)
    best_strategy = Column(String(50), nullable=False)
    success_rate = Column(Float, default=0.0)
    avg_latency = Column(Float, default=0.0)
    job_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class DataSnapshot(Base):
    """Change Detection Engine: Stores data hashes for diffing"""
    __tablename__ = "data_snapshots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(2048), nullable=False)
    data_hash = Column(String(64), nullable=False)  # SHA-256
    data_json = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
