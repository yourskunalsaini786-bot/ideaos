"""Feedback schemas."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class FeedbackEventBase(BaseModel):
    """Base feedback event fields."""
    entity_type: str = Field(..., pattern="^(idea|fusion_proposal|content_output|calendar_item)$")
    entity_id: UUID
    action: str = Field(..., pattern="^(approved|rejected|edited|regenerated|scheduled|published)$")
    reason_category: Optional[str] = Field(None, max_length=100)
    reason_text: Optional[str] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None


class FeedbackEventCreate(FeedbackEventBase):
    """Create feedback event."""
    pass


class FeedbackEventResponse(FeedbackEventBase):
    """Feedback event response."""
    id: UUID
    workspace_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackEventListResponse(BaseModel):
    """Paginated feedback event list."""
    data: List[FeedbackEventResponse]
    next_cursor: Optional[str] = None
    has_more: bool


class FeedbackAnalyticsRequest(BaseModel):
    """Request for feedback analytics."""
    entity_type: Optional[str] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)


class FeedbackAnalyticsResponse(BaseModel):
    """Feedback analytics response."""
    total_events: int
    by_action: Dict[str, int]
    by_entity_type: Dict[str, int]
    top_reason_categories: List[Dict[str, Any]]
    recent_events: List[FeedbackEventResponse]