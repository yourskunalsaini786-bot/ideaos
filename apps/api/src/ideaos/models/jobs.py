"""ProcessingJob model."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Integer,
    ForeignKey,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ideaos.models.base import Base, UUIDPrimaryKey, WorkspaceMixin


class JobStatus(str):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class JobType(str):
    TRANSCRIBE = "transcribe"
    EXTRACT = "extract"
    EMBED = "embed"
    FUSION = "fusion"
    GENERATE = "generate"
    QUALITY_CHECK = "quality_check"


class ProcessingJob(Base, UUIDPrimaryKey, WorkspaceMixin):
    """ProcessingJob model - background job tracking."""
    __tablename__ = "processing_jobs"

    capture_id = Column(
        UUID(as_uuid=True),
        ForeignKey("captures.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    job_type = Column(
        String(50),
        nullable=False,
        # Enum: transcribe, extract, embed, fusion, generate, quality_check
        index=True,
    )
    status = Column(
        String(50),
        nullable=False,
        default=JobStatus.PENDING,
        index=True,
    )
    payload = Column(JSONB, nullable=False)
    result = Column(JSONB, nullable=True)
    error = Column(Text, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True, index=True)
    celery_task_id = Column(String(255), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="processing_jobs")
    capture = relationship("Capture", back_populates="processing_jobs")

    __table_args__ = (
        Index("idx_jobs_workspace_status", "workspace_id", "status"),
        Index("idx_jobs_capture", "capture_id"),
        Index("idx_jobs_next_retry", "next_retry_at"),
        Index("idx_jobs_type_status", "job_type", "status"),
    )

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, type={self.job_type}, status={self.status})>"