"""Schemas for the unified Media Repurposing and Brand Memory workflow."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MediaIngestRequest(BaseModel):
    """Request to ingest long-form video or podcast content."""
    title: Optional[str] = None
    content: str = Field(..., min_length=10, description="Full transcript or long-form media text")
    media_type: str = Field(default="podcast", description="video, podcast, audio, or text")
    content_pillar: Optional[str] = "Thought Leadership"


class MediaIngestResponse(BaseModel):
    """Response containing extracted segments and initial clip opportunities."""
    capture_id: UUID
    idea_id: UUID
    title: str
    summary: str
    main_topic: str
    duration_seconds: float
    segments: List[Dict[str, Any]]
    clip_opportunities: List[Dict[str, Any]]


class ClipGenerateRequest(BaseModel):
    """Request to generate platform-specific copy for a selected clip."""
    idea_id: UUID
    clip_title: str
    key_quote: str
    selection_reason: str
    start_time: float
    end_time: float
    platform: str = Field(..., description="instagram_reel, linkedin_post, youtube_shorts, x_thread")
    format: str = Field(..., description="reel, post, shorts, thread")


class ClipGenerateResponse(BaseModel):
    """Platform-specific copy with Brand Guardian validation score."""
    idea_id: UUID
    platform: str
    format: str
    title: str
    hook: str
    body: str
    cta: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    quality_score: float
    quality_passed: bool
    quality_warnings: List[str] = Field(default_factory=list)
    visual_notes: List[Dict[str, Any]] = Field(default_factory=list)


class CreatorEditAndApproveRequest(BaseModel):
    """Request where creator reviews, edits, and approves content, training brand memory."""
    idea_id: UUID
    platform: str
    format: str
    original_content: str
    edited_content: str
    title: Optional[str] = None
    schedule_time: Optional[datetime] = None


class CreatorEditAndApproveResponse(BaseModel):
    """Response confirming content creation, calendar scheduling, and extracted brand rules."""
    content_output_id: UUID
    calendar_item_id: Optional[UUID] = None
    status: str
    learned_brand_rules: List[Dict[str, Any]] = Field(default_factory=list)
    message: str


class PerformanceFeedbackRequest(BaseModel):
    """Request recording actual post performance metrics."""
    content_output_id: UUID
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    retention_rate: Optional[float] = None


class PerformanceFeedbackResponse(BaseModel):
    """Response confirming recorded performance and feedback loop status."""
    feedback_event_id: UUID
    content_output_id: UUID
    performance_score: float
    status: str
    recommendation_impact: str
