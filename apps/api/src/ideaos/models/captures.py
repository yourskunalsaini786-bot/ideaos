"""Capture and Asset models."""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    BigInteger,
    ForeignKey,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from ideaos.models.base import Base, TimestampMixin, UUIDPrimaryKey, SoftDeleteMixin, WorkspaceMixin, utc_now


class CaptureStatus(str):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CaptureType(str):
    VOICE = "voice"
    IMAGE = "image"
    FILE = "file"
    LINK = "link"
    TEXT = "text"


class Capture(Base, UUIDPrimaryKey, TimestampMixin, SoftDeleteMixin, WorkspaceMixin):
    """Capture model - raw user input before processing."""
    __tablename__ = "captures"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    type = Column(
        String(50),
        nullable=False,
        # Enum: voice, image, file, link, text
    )
    status = Column(
        String(50),
        nullable=False,
        default=CaptureStatus.UPLOADING,
        index=True,
    )
    source_text = Column(Text, nullable=True)  # Original transcribed/extracted text
    metadata = Column(JSONB, default=dict, nullable=False)
    asset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="SET NULL"),
        nullable=True,
    )
    error_message = Column(Text, nullable=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="captures")
    user = relationship("User", back_populates="captures")
    asset = relationship("Asset", back_populates="capture", foreign_keys=[asset_id])
    idea = relationship("Idea", back_populates="capture", foreign_keys=[idea_id])
    sources = relationship("IdeaSource", back_populates="capture")
    processing_jobs = relationship("ProcessingJob", back_populates="capture")

    __table_args__ = (
        Index("idx_captures_workspace_status", "workspace_id", "status"),
        Index("idx_captures_created", "created_at"),
        Index("idx_captures_type", "type"),
    )

    def __repr__(self):
        return f"<Capture(id={self.id}, type={self.type}, status={self.status})>"


class AssetStatus(str):
    PENDING = "pending"
    READY = "ready"
    SCANNED = "scanned"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class Asset(Base, UUIDPrimaryKey, TimestampMixin, WorkspaceMixin):
    """Asset model - stored media files."""
    __tablename__ = "assets"

    capture_id = Column(
        UUID(as_uuid=True),
        ForeignKey("captures.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    storage_key = Column(String(512), nullable=False)
    bucket = Column(String(100), default="ideaos-assets", nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    checksum = Column(String(64), nullable=False, index=True)
    original_filename = Column(String(255), nullable=True)
    status = Column(
        String(50),
        nullable=False,
        default=AssetStatus.PENDING,
        index=True,
    )
    scan_result = Column(JSONB, nullable=True)
    metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="assets")
    capture = relationship("Capture", back_populates="asset", foreign_keys=[Capture.asset_id])
    sources = relationship("IdeaSource", back_populates="asset")

    __table_args__ = (
        Index("idx_assets_workspace", "workspace_id"),
        Index("idx_assets_capture", "capture_id"),
        Index("idx_assets_checksum", "checksum"),
        Index("idx_assets_status", "status"),
    )

    def __repr__(self):
        return f"<Asset(id={self.id}, mime_type={self.mime_type}, size={self.size_bytes})>"