"""Brand schemas."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BrandProfileBase(BaseModel):
    """Base brand profile fields."""
    voice_description: Optional[str] = None
    tone_attributes: List[str] = Field(default_factory=list)
    style_guidelines: Optional[str] = None
    vocabulary_preferences: Dict[str, Any] = Field(default_factory=dict)
    target_audience: Optional[str] = None
    audience_personas: List[Dict[str, Any]] = Field(default_factory=list)
    positioning_statement: Optional[str] = None
    value_propositions: List[str] = Field(default_factory=list)
    core_opinions: List[str] = Field(default_factory=list)
    prohibited_topics: List[str] = Field(default_factory=list)
    prohibited_phrases: List[str] = Field(default_factory=list)
    visual_style: Dict[str, Any] = Field(default_factory=dict)
    brand_colors: List[str] = Field(default_factory=list)


class BrandProfileCreate(BrandProfileBase):
    """Create brand profile."""
    pass


class BrandProfileUpdate(BaseModel):
    """Update brand profile."""
    voice_description: Optional[str] = None
    tone_attributes: Optional[List[str]] = None
    style_guidelines: Optional[str] = None
    vocabulary_preferences: Optional[Dict[str, Any]] = None
    target_audience: Optional[str] = None
    audience_personas: Optional[List[Dict[str, Any]]] = None
    positioning_statement: Optional[str] = None
    value_propositions: Optional[List[str]] = None
    core_opinions: Optional[List[str]] = None
    prohibited_topics: Optional[List[str]] = None
    prohibited_phrases: Optional[List[str]] = None
    visual_style: Optional[Dict[str, Any]] = None
    brand_colors: Optional[List[str]] = None


class BrandProfileResponse(BrandProfileBase):
    """Brand profile response."""
    id: UUID
    workspace_id: UUID
    version: int
    previous_version_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandRuleBase(BaseModel):
    """Base brand rule fields."""
    rule_type: str = Field(..., pattern="^(must_include|must_avoid|tone_check|format_rule|legal)$")
    pattern: Optional[str] = Field(None, max_length=500)
    severity: str = Field(default="warning", pattern="^(error|warning|info)$")
    message: str = Field(..., min_length=1, max_length=1000)
    examples: List[str] = Field(default_factory=list)
    applies_to: List[str] = Field(default_factory=list)
    is_active: bool = True


class BrandRuleCreate(BrandRuleBase):
    """Create brand rule."""
    pass


class BrandRuleUpdate(BaseModel):
    """Update brand rule."""
    pattern: Optional[str] = Field(None, max_length=500)
    severity: Optional[str] = Field(None, pattern="^(error|warning|info)$")
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    examples: Optional[List[str]] = None
    applies_to: Optional[List[str]] = None
    is_active: Optional[bool] = None


class BrandRuleResponse(BrandRuleBase):
    """Brand rule response."""
    id: UUID
    workspace_id: UUID
    brand_profile_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandRuleListResponse(BaseModel):
    """Paginated brand rule list."""
    data: List[BrandRuleResponse]
    next_cursor: Optional[str] = None
    has_more: bool


class BrandValidationRequest(BaseModel):
    """Request to validate content against brand rules."""
    content: str
    platform: Optional[str] = None
    format: Optional[str] = None
    content_output_id: Optional[UUID] = None


class BrandValidationResult(BaseModel):
    """Brand validation result."""
    passed: bool
    score: float = Field(..., ge=0.0, le=10.0)
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class BrandExtractRulesRequest(BaseModel):
    """Request to extract rules from edit diff."""
    original_content: str
    edited_content: str
    platform: str
    format: str


class BrandExtractRulesResponse(BaseModel):
    """Response with extracted brand rules."""
    proposed_rules: List[BrandRuleCreate]
    summary: str