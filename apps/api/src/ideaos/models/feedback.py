"""FeedbackEvent model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ideaos.models.base import Base, UUIDPrimaryKey, WorkspaceMixin


class FeedbackEvent(Base, UUIDPrimaryKey, WorkspaceMixin):
    """FeedbackEvent model - user feedback for learning loop."""
    __tablename__ = "feedback_events"

    entity_type = Column(
        String(50),
        nullable=False,
        # Enum: idea, fusion_proposal, content_output, calendar_item
    )
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(
        String(50),
        nullable=False,
        # Enum: approved, rejected, edited, regenerated, scheduled, published
    )
    reason_category = Column(String(100), nullable=True)
    reason_text = Column(Text, nullable=True)
    before_state = Column(JSONB, nullable=True)
    after_state = Column(JSONB, nullable=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="feedback_events")
    user = relationship("User", back_populates="feedback_events")

    __table_args__ = (
        Index("idx_feedback_workspace", "workspace_id"),
        Index("idx_feedback_entity", "entity_type", "entity_id"),
        Index("idx_feedback_action", "action"),
        Index("idx_feedback_user", "user_id"),
        Index("idx_feedback_created", "created_at"),
    )

    def __repr__(self):
        return f"<FeedbackEvent(entity={self.entity_type}:{self.entity_id}, action={self.action})>"