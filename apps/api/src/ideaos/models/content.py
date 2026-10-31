"""ContentOutput and CalendarItem models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    Index,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ideaos.models.base import Base, TimestampMixin, UUIDPrimaryKey, SoftDeleteMixin, WorkspaceMixin, utc_now


class ContentStatus(str):
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CalendarStatus(str):
    CAPTURED = "captured"
    DEVELOPING = "developing"
    READY_FOR_PRODUCTION = "ready_for_production"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    RECYCLE_OR_IMPROVE = "recycle_or_improve"


class ContentOutput(Base, UUIDPrimaryKey, TimestampMixin, SoftDeleteMixin, WorkspaceMixin):
    """ContentOutput model - generated platform-specific content."""
    __tablename__ = "content_outputs"

    idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform = Column(
        String(50),
        nullable=False,
        # Enum: instagram_reel, instagram_carousel, linkedin_post, linkedin_article,
        # youtube_shorts, youtube_outline, x_thread, newsletter
        index=True,
    )
    format = Column(
        String(50),
        nullable=False,
        # Enum: reel, carousel, post, article, shorts, outline, thread, newsletter
    )
    title = Column(String(500), nullable=True)
    hook = Column(Text, nullable=True)
    body = Column(Text, nullable=False)
    cta = Column(Text, nullable=True)
    hashtags = Column(JSONB, default=list, nullable=False)
    visual_notes = Column(JSONB, default=list, nullable=False)
    estimated_duration_seconds = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)

    # Quality
    quality_score = Column(Numeric(3, 2), nullable=True)
    quality_warnings = Column(JSONB, default=list, nullable=False)
    quality_passed = Column(Boolean, nullable=True)

    # Status
    status = Column(
        String(50),
        nullable=False,
        default=ContentStatus.DRAFT,
        index=True,
    )
    version = Column(Integer, default=1, nullable=False)
    parent_output_id = Column(
        UUID(as_uuid=True),
        ForeignKey("content_outputs.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Publishing
    published_url = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    external_id = Column(String(255), nullable=True)

    # Metadata
    generation_model = Column(String(100), nullable=True)
    generation_prompt_hash = Column(String(64), nullable=True)
    metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="content_outputs")
    idea = relationship("Idea", back_populates="content_outputs")
    calendar_items = relationship("CalendarItem", back_populates="content_output")
    parent = relationship("ContentOutput", remote_side="ContentOutput.id")

    __table_args__ = (
        Index("idx_content_workspace_status", "workspace_id", "status"),
        Index("idx_content_platform", "platform"),
        Index("idx_content_quality", "quality_score"),
        Index("idx_content_created", "created_at"),
    )

    def __repr__(self):
        return f"<ContentOutput(id={self.id}, platform={self.platform}, status={self.status})>"


class CalendarItem(Base, UUIDPrimaryKey, TimestampMixin, WorkspaceMixin):
    """CalendarItem model - editorial calendar entries."""
    __tablename__ = "calendar_items"

    content_output_id = Column(
        UUID(as_uuid=True),
        ForeignKey("content_outputs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(50),
        nullable=False,
        default=CalendarStatus.CAPTURED,
        index=True,
    )
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    platform = Column(String(50), nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
    metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="calendar_items")
    content_output = relationship("ContentOutput", back_populates="calendar_items")

    __table_args__ = (
        Index("idx_calendar_workspace_status", "workspace_id", "status"),
        Index("idx_calendar_scheduled", "scheduled_at"),
        Index("idx_calendar_platform_date", "platform", "scheduled_at"),
    )

    def __repr__(self):
        return f"<CalendarItem(id={self.id}, platform={self.platform}, status={self.status})>"