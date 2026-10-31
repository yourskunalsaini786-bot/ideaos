"""Fusion schemas."""
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ContentOpportunity(BaseModel):
    """Content opportunity from fusion analysis."""
    pillar: str
    format: str
    platform: str
    angle: Optional[str] = None
    hook_suggestion: Optional[str] = None


class FusionProposalBase(BaseModel):
    """Base fusion proposal fields."""
    source_idea_ids: List[UUID] = Field(..., min_items=2, max_items=10)
    fusion_concept: str = Field(..., min_length=10, max_length=5000)
    confidence: float = Field(..., ge=0.0, le=1.0)
    relation_types: List[str] = Field(default_factory=list)
    content_opportunities: List[ContentOpportunity] = Field(default_factory=list)
    reasoning: Optional[str] = None


class FusionProposalCreate(FusionProposalBase):
    """Create fusion proposal."""
    new_idea_id: Optional[UUID] = None


class FusionProposalUpdate(BaseModel):
    """Update fusion proposal."""
    status: Optional[str] = None
    edited_fusion_concept: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None


class FusionProposalResponse(FusionProposalBase):
    """Fusion proposal response."""
    id: UUID
    workspace_id: UUID
    new_idea_id: Optional[UUID] = None
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    edited_fusion_concept: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FusionSuggestRequest(BaseModel):
    """Request to suggest fusions for an idea."""
    idea_id: UUID
    min_confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    max_candidates: int = Field(default=10, ge=1, le=50)
    relation_types: Optional[List[str]] = None


class FusionApproveRequest(BaseModel):
    """Approve fusion proposal."""
    create_master_idea: bool = True
    master_idea_title: Optional[str] = None


class FusionRejectRequest(BaseModel):
    """Reject fusion proposal."""
    reason: str = Field(..., min_length=1, max_length=1000)


class FusionEditRequest(BaseModel):
    """Edit fusion proposal."""
    fusion_concept: str = Field(..., min_length=10, max_length=5000)
    create_master_idea: bool = False


class IdeaRelationResponse(BaseModel):
    """Idea relation response."""
    id: UUID
    workspace_id: UUID
    source_idea_id: UUID
    target_idea_id: UUID
    relation_type: str
    confidence: float
    evidence: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IdeaConnectionsResponse(BaseModel):
    """Idea connections response."""
    relations: List[IdeaRelationResponse]
    fusion_proposals: List[FusionProposalResponse]