"""Search schemas."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SearchRequest(BaseModel):
    """Universal search request."""
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: Optional[List[str]] = Field(
        None,
        description="Filter by entity types: capture, idea, content_output, calendar_item, brand_profile, brand_rule"
    )
    workspace_id: Optional[UUID] = None  # If None, use current workspace from context
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_highlights: bool = True


class SearchResultItem(BaseModel):
    """Individual search result."""
    id: UUID
    entity_type: str
    title: str
    snippet: str
    highlights: Optional[Dict[str, List[str]]] = None
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    total_results: int
    results: List[SearchResultItem]
    took_ms: int
    facets: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class SemanticSearchRequest(BaseModel):
    """Semantic/vector search request."""
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: Optional[List[str]] = None
    workspace_id: Optional[UUID] = None
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    limit: int = Field(default=20, ge=1, le=100)


class HybridSearchRequest(BaseModel):
    """Hybrid search request (keyword + vector)."""
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: Optional[List[str]] = None
    workspace_id: Optional[UUID] = None
    keyword_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    vector_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    limit: int = Field(default=20, ge=1, le=100)


class SearchSuggestionRequest(BaseModel):
    """Search suggestions/autocomplete request."""
    query: str = Field(..., min_length=1, max_length=100)
    entity_types: Optional[List[str]] = None
    limit: int = Field(default=10, ge=1, le=20)


class SearchSuggestionResponse(BaseModel):
    """Search suggestions response."""
    suggestions: List[str]
    query: str