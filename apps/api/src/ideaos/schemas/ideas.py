"""Idea schemas."""
from uuid import UUID
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class IdeaSourceResponse(BaseModel):
    """Schema for idea source response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    capture_id: Optional[UUID] = None
    asset_id: Optional[UUID] = None
    source_type: str
    content: Optional[str] = None
    metadata: Dict[str, Any]
    created_at: datetime


class IdeaRelationResponse(BaseModel):
    """Schema for idea relation response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    source_idea_id: UUID
    target_idea_id: UUID
    relation_type: str
    confidence: float
    explanation: str
    fusion_concept: Optional[str] = None
    content_opportunities: List[Dict[str, Any]]
    discovered_by: str
    is_active: bool
    created_at: datetime
    target_idea: Optional["IdeaBasic"] = None


class IdeaBasic(BaseModel):
    """Basic idea info for nested responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    summary: str
    main_topic: Optional[str] = None
    content_pillar: Optional[str] = None
    status: str


class IdeaCreate(BaseModel):
    """Schema for creating an idea."""
    title: str = Field(..., max_length=500)
    summary: str
    original_thought: str
    main_topic: Optional[str] = None
    supporting_context: Optional[str] = None
    target_audience: Optional[str] = None
    underlying_problem: Optional[str] = None
    key_opinion_insight: Optional[str] = None
    content_pillar: Optional[str] = None
    suggested_formats: List[str] = Field(default_factory=list)
    suggested_platforms: List[str] = Field(default_factory=list)
    keywords_entities: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "candidate"
    capture_id: Optional[UUID] = None


class IdeaUpdate(BaseModel):
    """Schema for updating an idea."""
    title: Optional[str] = None
    summary: Optional[str] = None
    original_thought: Optional[str] = None
    main_topic: Optional[str] = None
    supporting_context: Optional[str] = None
    target_audience: Optional[str] = None
    underlying_problem: Optional[str] = None
    key_opinion_insight: Optional[str] = None
    content_pillar: Optional[str] = None
    suggested_formats: Optional[List[str]] = None
    suggested_platforms: Optional[List[str]] = None
    keywords_entities: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None


class IdeaResponse(BaseModel):
    """Schema for idea response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    capture_id: Optional[UUID] = None
    title: str
    summary: str
    original_thought: str
    main_topic: Optional[str] = None
    supporting_context: Optional[str] = None
    target_audience: Optional[str] = None
    underlying_problem: Optional[str] = None
    key_opinion_insight: Optional[str] = None
    content_pillar: Optional[str] = None
    suggested_formats: List[str]
    suggested_platforms: List[str]
    keywords_entities: List[Dict[str, Any]]
    embedding: Optional[List[float]] = None
    status: str
    version: int
    parent_idea_id: Optional[UUID] = None
    fusion_source_ids: List[UUID]
    sources: List[IdeaSourceResponse] = []
    created_at: datetime
    updated_at: datetime


class IdeaListResponse(BaseModel):
    """Paginated idea list response."""
    data: List[IdeaResponse]
    next_cursor: Optional[str] = None
    has_more: bool


class IdeaConnectionsResponse(BaseModel):
    """Response for idea connections."""
    relations: List[IdeaRelationResponse]
    fusion_proposals: List["FusionProposalBasic"] = []


class FusionProposalBasic(BaseModel):
    """Basic fusion proposal for connections response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    confidence: float
    fusion_concept: str
    source_idea_ids: List[UUID]
    created_at: datetime


class FusionProposalResponse(BaseModel):
    """Schema for fusion proposal response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    new_idea_id: UUID
    source_idea_ids: List[UUID]
    relationships: List[Dict[str, Any]]
    fusion_concept: str
    content_opportunities: List[Dict[str, Any]]
    confidence: float
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    edited_fusion_concept: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FusionSuggestRequest(BaseModel):
    """Request for fusion suggestions."""
    idea_id: UUID
    max_candidates: int = 15
    min_confidence: float = 0.6


class FusionApproveRequest(BaseModel):
    """Request to approve a fusion proposal."""
    create_master_idea: bool = True
    master_idea_title: Optional[str] = None


class FusionRejectRequest(BaseModel):
    """Request to reject a fusion proposal."""
    reason: str


class FusionEditRequest(BaseModel):
    """Request to edit a fusion proposal."""
    fusion_concept: str
    create_master_idea: bool = True


# Resolve forward references
IdeaRelationResponse.model_rebuild()
IdeaConnectionsResponse.model_rebuild()