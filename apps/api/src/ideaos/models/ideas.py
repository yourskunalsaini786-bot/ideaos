"""Idea, IdeaSource, IdeaRelation, and FusionProposal models."""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Index,
    Enum as SQLEnum,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from ideaos.models.base import Base, TimestampMixin, UUIDPrimaryKey, SoftDeleteMixin, WorkspaceMixin, CompatibleArray, utc_now


class IdeaStatus(str):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    ARCHIVED = "archived"
    FUSED = "fused"


class RelationType(str):
    SIMILAR = "similar"
    COMPLEMENTARY = "complementary"
    CONTINUATION = "continuation"
    CONTRADICTORY = "contradictory"
    COMMON_THEME = "common_theme"
    NEW_ANGLE = "new_angle"


class FusionStatus(str):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class Idea(Base, UUIDPrimaryKey, TimestampMixin, SoftDeleteMixin, WorkspaceMixin):
    """Idea model - structured, enriched representation of a capture."""
    __tablename__ = "ideas"

    capture_id = Column(
        UUID(as_uuid=True),
        ForeignKey("captures.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    original_thought = Column(Text, nullable=False)
    main_topic = Column(String(255), nullable=True, index=True)
    supporting_context = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    underlying_problem = Column(Text, nullable=True)
    key_opinion_insight = Column(Text, nullable=True)
    content_pillar = Column(String(255), nullable=True, index=True)
    suggested_formats = Column(JSONB, default=list, nullable=False)
    suggested_platforms = Column(JSONB, default=list, nullable=False)
    keywords_entities = Column(JSONB, default=list, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    status = Column(
        String(50),
        nullable=False,
        default=IdeaStatus.CANDIDATE,
        index=True,
    )
    version = Column(Integer, default=1, nullable=False)
    parent_idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="SET NULL"),
        nullable=True,
    )
    fusion_source_ids = Column(CompatibleArray(UUID(as_uuid=True)), default=list, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="ideas")
    capture = relationship("Capture", back_populates="idea", foreign_keys="Capture.idea_id")
    sources = relationship("IdeaSource", back_populates="idea")
    relations_as_source = relationship("IdeaRelation", back_populates="source_idea", foreign_keys="IdeaRelation.source_idea_id")
    relations_as_target = relationship("IdeaRelation", back_populates="target_idea", foreign_keys="IdeaRelation.target_idea_id")
    fusion_proposals = relationship("FusionProposal", back_populates="new_idea")
    content_outputs = relationship("ContentOutput", back_populates="idea")
    children = relationship("Idea", backref="parent", remote_side="Idea.id")

    __table_args__ = (
        Index("idx_ideas_workspace_status", "workspace_id", "status"),
        Index("idx_ideas_pillar", "content_pillar"),
        Index("idx_ideas_parent", "parent_idea_id"),
        Index("idx_ideas_created", "created_at"),
        # Vector index created separately via migration
    )

    def __repr__(self):
        return f"<Idea(id={self.id}, title={self.title[:50]}, status={self.status})>"


class IdeaSource(Base, UUIDPrimaryKey, TimestampMixin):
    """IdeaSource model - links ideas to their source captures/assets."""
    __tablename__ = "idea_sources"

    idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    capture_id = Column(
        UUID(as_uuid=True),
        ForeignKey("captures.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    asset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_type = Column(
        String(50),
        nullable=False,
        # Enum: capture, asset, external_url, manual
    )
    content = Column(Text, nullable=True)
    metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    idea = relationship("Idea", back_populates="sources")
    capture = relationship("Capture", back_populates="sources")
    asset = relationship("Asset", back_populates="sources")

    __table_args__ = (
        Index("idx_idea_sources_idea", "idea_id"),
        Index("idx_idea_sources_capture", "capture_id"),
    )

    def __repr__(self):
        return f"<IdeaSource(idea_id={self.idea_id}, type={self.source_type})>"


class IdeaRelation(Base, UUIDPrimaryKey, TimestampMixin, WorkspaceMixin):
    """IdeaRelation model - connections between ideas."""
    __tablename__ = "idea_relations"

    source_idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relation_type = Column(
        String(50),
        nullable=False,
        # Enum: similar, complementary, continuation, contradictory, common_theme, new_angle
    )
    confidence = Column(Numeric(3, 2), nullable=False)
    explanation = Column(Text, nullable=False)
    fusion_concept = Column(Text, nullable=True)
    content_opportunities = Column(JSONB, default=list, nullable=False)
    discovered_by = Column(String(50), default="fusion_engine", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="idea_relations")
    source_idea = relationship("Idea", back_populates="relations_as_source", foreign_keys=[source_idea_id])
    target_idea = relationship("Idea", back_populates="relations_as_target", foreign_keys=[target_idea_id])

    __table_args__ = (
        UniqueConstraint("source_idea_id", "target_idea_id", "relation_type", name="uq_idea_relation"),
        Index("idx_idea_relations_workspace", "workspace_id"),
        Index("idx_idea_relations_type", "relation_type"),
        Index("idx_idea_relations_confidence", "confidence"),
    )

    def __repr__(self):
        return f"<IdeaRelation(source={self.source_idea_id}, target={self.target_idea_id}, type={self.relation_type})>"


class FusionProposal(Base, UUIDPrimaryKey, TimestampMixin, WorkspaceMixin):
    """FusionProposal model - AI-suggested idea fusions."""
    __tablename__ = "fusion_proposals"

    new_idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_idea_ids = Column(CompatibleArray(UUID(as_uuid=True)), nullable=False)
    relationships = Column(JSONB, nullable=False)
    fusion_concept = Column(Text, nullable=False)
    content_opportunities = Column(JSONB, default=list, nullable=False)
    confidence = Column(Numeric(3, 2), nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default=FusionStatus.PENDING,
        index=True,
    )
    approved_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_reason = Column(Text, nullable=True)
    edited_fusion_concept = Column(Text, nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="fusion_proposals")
    new_idea = relationship("Idea", back_populates="fusion_proposals")
    approver = relationship("User", foreign_keys=[approved_by])

    __table_args__ = (
        Index("idx_fusion_workspace", "workspace_id"),
        Index("idx_fusion_new_idea", "new_idea_id"),
        Index("idx_fusion_status", "status"),
        Index("idx_fusion_created", "created_at"),
    )

    def __repr__(self):
        return f"<FusionProposal(id={self.id}, new_idea={self.new_idea_id}, status={self.status})>"