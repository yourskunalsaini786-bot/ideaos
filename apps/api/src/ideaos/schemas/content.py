"""Content and Calendar schemas."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ContentOutputBase(BaseModel):
    """Base content output fields."""
    idea_id: UUID
    platform: str = Field(..., pattern="^(instagram_reel|instagram_carousel|linkedin_post|linkedin_article|youtube_shorts|youtube_outline|x_thread|newsletter)$")
    format: str = Field(..., pattern="^(reel|carousel|post|article|shorts|outline|thread|newsletter)$")
    title: Optional[str] = Field(None, max_length=500)
    hook: Optional[str] = None
    body: str = Field(..., min_length=1)
    cta: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    visual_notes: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_duration_seconds: Optional[int] = None
    character_count: Optional[int] = None
    generation_model: Optional[str] = None
    generation_prompt_hash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentOutputCreate(ContentOutputBase):
    """Create content output."""
    pass


class ContentOutputUpdate(BaseModel):
    """Update content output."""
    title: Optional[str] = Field(None, max_length=500)
    hook: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None
    hashtags: Optional[List[str]] = None
    visual_notes: Optional[List[Dict[str, Any]]] = None
    estimated_duration_seconds: Optional[int] = None
    character_count: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(draft|reviewing|approved|scheduled|published|archived)$")
    quality_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    quality_warnings: Optional[List[str]] = None
    quality_passed: Optional[bool] = None
    published_url: Optional[str] = None
    published_at: Optional[datetime] = None
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentOutputResponse(ContentOutputBase):
    """Content output response."""
    id: UUID
    workspace_id: UUID
    quality_score: Optional[float] = None
    quality_warnings: List[str] = Field(default_factory=list)
    quality_passed: Optional[bool] = None
    status: str
    version: int
    parent_output_id: Optional[UUID] = None
    published_url: Optional[str] = None
    published_at: Optional[datetime] = None
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentOutputListResponse(BaseModel):
    """Paginated content output list."""
    data: List[ContentOutputResponse]
    next_cursor: Optional[str] = None
    has_more: bool


class CalendarItemBase(BaseModel):
    """Base calendar item fields."""
    content_output_id: UUID
    platform: str
    status: str = Field(default="captured", pattern="^(captured|developing|ready_for_production|scheduled|published|recycle_or_improve)$")
    scheduled_at: Optional[datetime] = None
    sort_order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CalendarItemCreate(CalendarItemBase):
    """Create calendar item."""
    pass


class CalendarItemUpdate(BaseModel):
    """Update calendar item."""
    status: Optional[str] = Field(None, pattern="^(captured|developing|ready_for_production|scheduled|published|recycle_or_improve)$")
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    sort_order: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CalendarItemResponse(CalendarItemBase):
    """Calendar item response."""
    id: UUID
    workspace_id: UUID
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalendarItemListResponse(BaseModel):
    """Paginated calendar item list."""
    data: List[CalendarItemResponse]
    next_cursor: Optional[str] = None
    has_more: bool


class CalendarBatchScheduleRequest(BaseModel):
    """Batch schedule calendar items."""
    items: List[CalendarItemCreate]
    auto_schedule: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    platforms: Optional[List[str]] = None


class ContentGenerationRequest(BaseModel):
    """Request to generate content from an idea."""
    idea_id: UUID
    platforms: List[str] = Field(..., min_items=1)
    brand_profile_id: Optional[UUID] = None
    hook_formulas: Optional[List[str]] = None
    max_variants_per_platform: int = Field(default=3, ge=1, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)