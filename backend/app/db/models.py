from sqlalchemy import (
    Column,
    String,
    Text,
    JSON,
    DateTime,
    Float,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    TypeDecorator,
    CHAR,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid
import enum


# =========================
# UUID / GUID TYPE
# =========================

class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return f"{value.int:032x}"

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


# =========================
# ENUMS
# =========================

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
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEEDS_HITL = "NEEDS_HITL"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# =========================
# JOB
# =========================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    schema = Column(JSON, nullable=False)
    config = Column(JSON, nullable=True)
    config_metadata = Column(JSON, nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.CREATED, nullable=False)
    
    sla_seconds = Column(Integer, default=300, nullable=False)
    webhook_url = Column(String(512), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tasks = relationship(
        "Task",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    versions = relationship(
        "DatasetVersion",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# =========================
# TASK  (FIXED SELF-RELATION)
# =========================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        GUID(),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    parent_id = Column(
        GUID(),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_seed = Column(Integer, default=0, nullable=False)
    type = Column(SQLEnum(TaskType), nullable=False)
    payload = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)

    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)

    confidence = Column(Float, nullable=True)
    confidence_components = Column(JSON, nullable=True)
    field_confidence = Column(JSON, nullable=True)

    failure_reason = Column(String(50), nullable=True)
    failure_message = Column(Text, nullable=True)

    retry_count = Column(Integer, default=0)
    priority = Column(Integer, default=0, nullable=False)
    explanation = Column(JSON, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    config_version = Column(Integer, nullable=True)
    assigned_to = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔥 THIS FIXES YOUR ERROR
    parent = relationship(
        "Task",
        remote_side=[id],
        back_populates="children",
    )

    children = relationship(
        "Task",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    job = relationship("Job", back_populates="tasks")

    audit_logs = relationship(
        "AuditLog",
        back_populates="task",
        cascade="all, delete-orphan",
    )


# =========================
# AUDIT LOG
# =========================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    task_id = Column(
        GUID(),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    actor_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    changes = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="audit_logs")


# =========================
# DATASET VERSIONING
# =========================

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        GUID(),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    version = Column(Integer, nullable=False)
    data_location = Column(String(255), nullable=False)
    row_count = Column(Integer, nullable=False)

    confidence_summary = Column(JSON, nullable=True)
    change_summary = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="versions")


# =========================
# JOB CONFIG (RESTORED)
# =========================

class JobConfig(Base):
    __tablename__ = "job_configs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        GUID(),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    version = Column(Integer, nullable=False)
    config = Column(JSON, nullable=False)
    config_metadata = Column(JSON, nullable=True)

    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)

    job = relationship("Job")


# =========================
# ROBOTS.TXT CACHE
# =========================

class RobotsTxt(Base):
    __tablename__ = "robots_txt"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    crawl_delay = Column(Float, nullable=True)
    sitemap_urls = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


# =========================
# DOMAIN MEMORY (SILENT LEARNING)
# =========================

class DomainMemory(Base):
    __tablename__ = "domain_memory"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False)
    best_strategy = Column(String(50), nullable=False)
    success_rate = Column(Float, default=0.0)
    avg_latency = Column(Float, default=0.0)
    job_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


# =========================
# DATA SNAPSHOT (CHANGE DETECTION)
# =========================

class DataSnapshot(Base):
    __tablename__ = "data_snapshots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        GUID(),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    url = Column(String(2048), nullable=False)
    data_hash = Column(String(64), nullable=False)
    data_json = Column(JSON, nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())
