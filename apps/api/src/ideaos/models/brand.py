"""BrandProfile and BrandRule models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    ForeignKey,
    Integer,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ideaos.models.base import Base, TimestampMixin, UUIDPrimaryKey, WorkspaceMixin, utc_now


class BrandProfile(Base, UUIDPrimaryKey, TimestampMixin, WorkspaceMixin):
    """BrandProfile model - workspace-level brand DNA."""
    __tablename__ = "brand_profiles"

    # One-to-one with workspace
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Voice & Tone
    voice_description = Column(Text, nullable=True)
    tone_attributes = Column(JSONB, default=list, nullable=False)
    style_guidelines = Column(Text, nullable=True)
    vocabulary_preferences = Column(JSONB, default=dict, nullable=False)

    # Audience & Positioning
    target_audience = Column(Text, nullable=True)
    audience_personas = Column(JSONB, default=list, nullable=False)
    positioning_statement = Column(Text, nullable=True)
    value_propositions = Column(JSONB, default=list, nullable=False)

    # Opinions & Beliefs
    core_opinions = Column(JSONB, default=list, nullable=False)
    prohibited_topics = Column(JSONB, default=list, nullable=False)
    prohibited_phrases = Column(JSONB, default=list, nullable=False)

    # Visual Preferences
    visual_style = Column(JSONB, default=dict, nullable=False)
    brand_colors = Column(JSONB, default=list, nullable=False)

    # Versioning
    version = Column(Integer, default=1, nullable=False)
    previous_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("brand_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    workspace = relationship("Workspace", back_populates="brand_profile")
    rules = relationship("BrandRule", back_populates="brand_profile")
    previous_version = relationship("BrandProfile", remote_side="BrandProfile.id")

    __table_args__ = (
        Index("idx_brand_profiles_workspace", "workspace_id"),
    )

    def __repr__(self):
        return f"<BrandProfile(workspace_id={self.workspace_id}, version={self.version})>"


class BrandRule(Base, UUIDPrimaryKey, TimestampMixin, WorkspaceMixin):
    """BrandRule model - deterministic rules for brand consistency."""
    __tablename__ = "brand_rules"

    brand_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("brand_profiles.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    rule_type = Column(
        String(50),
        nullable=False,
        # Enum: must_include, must_avoid, tone_check, format_rule, legal
        index=True,
    )
    pattern = Column(String(500), nullable=True)
    severity = Column(
        String(20),
        nullable=False,
        default="warning",
        # Enum: error, warning, info
    )
    message = Column(Text, nullable=False)
    examples = Column(JSONB, default=list, nullable=False)
    applies_to = Column(JSONB, default=list, nullable=False)  # ["all", "instagram", "linkedin", "x"]
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    workspace = relationship("Workspace", back_populates="brand_rules")
    brand_profile = relationship("BrandProfile", back_populates="rules")
    creator = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("idx_brand_rules_workspace", "workspace_id"),
        Index("idx_brand_rules_type", "rule_type"),
        Index("idx_brand_rules_active", "is_active"),
    )

    def __repr__(self):
        return f"<BrandRule(type={self.rule_type}, severity={self.severity})>"