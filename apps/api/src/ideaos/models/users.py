"""User, Workspace, and WorkspaceMember models."""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    ForeignKey,
    Index,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ideaos.models.base import Base, TimestampMixin, UUIDPrimaryKey, utc_now


class User(Base, UUIDPrimaryKey, TimestampMixin):
    """User model - core identity."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    password_hash = Column(String(255), nullable=True)
    auth_provider = Column(String(50), default="email", nullable=False)
    auth_provider_id = Column(String(255), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    owned_workspaces = relationship("Workspace", back_populates="owner")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user", foreign_keys="[WorkspaceMember.user_id]")
    captures = relationship("Capture", back_populates="user")
    feedback_events = relationship("FeedbackEvent", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Workspace(Base, UUIDPrimaryKey, TimestampMixin):
    """Workspace model - multi-tenant container."""
    __tablename__ = "workspaces"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    settings = Column(JSONB, default=dict, nullable=False)
    subscription_tier = Column(String(50), default="free", nullable=False)
    subscription_status = Column(String(50), default="active", nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace")
    captures = relationship("Capture", back_populates="workspace")
    assets = relationship("Asset", back_populates="workspace")
    ideas = relationship("Idea", back_populates="workspace")
    idea_relations = relationship("IdeaRelation", back_populates="workspace")
    fusion_proposals = relationship("FusionProposal", back_populates="workspace")
    brand_profile = relationship("BrandProfile", back_populates="workspace", uselist=False)
    brand_rules = relationship("BrandRule", back_populates="workspace")
    content_outputs = relationship("ContentOutput", back_populates="workspace")
    calendar_items = relationship("CalendarItem", back_populates="workspace")
    feedback_events = relationship("FeedbackEvent", back_populates="workspace")
    processing_jobs = relationship("ProcessingJob", back_populates="workspace")

    def __repr__(self):
        return f"<Workspace(id={self.id}, name={self.name}, slug={self.slug})>"


class WorkspaceMember(Base, UUIDPrimaryKey, TimestampMixin):
    """Workspace membership with roles."""
    __tablename__ = "workspace_members"

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(
        String(50),
        nullable=False,
        default="member",
        # Enum: owner, admin, editor, member, viewer, contributor
    )
    invited_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    joined_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    # Constraints
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
        Index("idx_workspace_members_workspace", "workspace_id"),
        Index("idx_workspace_members_user", "user_id"),
    )

    def __repr__(self):
        return f"<WorkspaceMember(workspace_id={self.workspace_id}, user_id={self.user_id}, role={self.role})>"