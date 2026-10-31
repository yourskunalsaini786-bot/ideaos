"""Search routes."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, text
from sqlalchemy.orm import selectinload
from datetime import datetime
import time

from ideaos.core.database import get_db
from ideaos.models import (
    Capture, Idea, ContentOutput, CalendarItem,
    BrandProfile, BrandRule, Workspace
)
from ideaos.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    SemanticSearchRequest,
    HybridSearchRequest,
    SearchSuggestionRequest,
    SearchSuggestionResponse,
)

router = APIRouter()


from ideaos.core.config import get_settings

settings = get_settings()


async def get_current_workspace_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract workspace_id from request state or dev workspace fallback."""
    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id:
        return UUID(str(workspace_id))
    if settings.ENVIRONMENT == "development":
        from ideaos.models import Workspace
        result = await db.execute(select(Workspace.id).order_by(Workspace.created_at.asc()).limit(1))
        ws_id = result.scalar_one_or_none()
        if ws_id:
            return ws_id
        return UUID("00000000-0000-0000-0000-000000000001")
    raise HTTPException(status_code=401, detail="Workspace context required")


# Universal keyword search
@router.post("", response_model=SearchResponse)
async def universal_search(
    request_in: SearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Universal keyword search across all entity types."""
    start_time = time.time()
    ws_id = request_in.workspace_id or workspace_id
    query = request_in.query
    search_term = f"%{query}%"

    results = []
    facets = {}

    entity_types = request_in.entity_types or [
        "capture", "idea", "content_output", "calendar_item", "brand_profile", "brand_rule"
    ]

    # Search captures
    if "capture" in entity_types:
        capture_query = select(Capture).where(
            Capture.workspace_id == ws_id,
            or_(
                Capture.source_text.ilike(search_term),
                Capture.metadata.cast(text).ilike(search_term),
            )
        ).order_by(Capture.created_at.desc()).limit(request_in.limit)
        capture_result = await db.execute(capture_query)
        captures = capture_result.scalars().all()
        for c in captures:
            results.append(SearchResultItem(
                id=c.id,
                entity_type="capture",
                title=f"Capture: {c.type}",
                snippet=(c.source_text or "")[:200] + "..." if c.source_text and len(c.source_text) > 200 else (c.source_text or ""),
                score=1.0,  # Placeholder
                metadata={"type": c.type, "status": c.status},
                created_at=c.created_at,
                updated_at=c.updated_at,
            ))
        facets["capture"] = len(captures)

    # Search ideas
    if "idea" in entity_types:
        idea_query = select(Idea).where(
            Idea.workspace_id == ws_id,
            or_(
                Idea.title.ilike(search_term),
                Idea.summary.ilike(search_term),
                Idea.original_thought.ilike(search_term),
            )
        ).order_by(Idea.created_at.desc()).limit(request_in.limit)
        idea_result = await db.execute(idea_query)
        ideas = idea_result.scalars().all()
        for i in ideas:
            results.append(SearchResultItem(
                id=i.id,
                entity_type="idea",
                title=i.title or "Untitled Idea",
                snippet=(i.summary or i.original_thought or "")[:200] + "..." if (i.summary or i.original_thought) and len(i.summary or i.original_thought or "") > 200 else (i.summary or i.original_thought or ""),
                score=1.0,
                metadata={"content_pillar": i.content_pillar, "status": i.status},
                created_at=i.created_at,
                updated_at=i.updated_at,
            ))
        facets["idea"] = len(ideas)

    # Search content outputs
    if "content_output" in entity_types:
        content_query = select(ContentOutput).where(
            ContentOutput.workspace_id == ws_id,
            or_(
                ContentOutput.title.ilike(search_term),
                ContentOutput.body.ilike(search_term),
                ContentOutput.hook.ilike(search_term),
            )
        ).order_by(ContentOutput.created_at.desc()).limit(request_in.limit)
        content_result = await db.execute(content_query)
        contents = content_result.scalars().all()
        for c in contents:
            results.append(SearchResultItem(
                id=c.id,
                entity_type="content_output",
                title=c.title or f"{c.platform} content",
                snippet=(c.body or "")[:200] + "..." if c.body and len(c.body) > 200 else (c.body or ""),
                score=1.0,
                metadata={"platform": c.platform, "format": c.format, "status": c.status},
                created_at=c.created_at,
                updated_at=c.updated_at,
            ))
        facets["content_output"] = len(contents)

    # Search calendar items
    if "calendar_item" in entity_types:
        cal_query = select(CalendarItem).where(
            CalendarItem.workspace_id == ws_id,
            CalendarItem.metadata.cast(text).ilike(search_term),
        ).order_by(CalendarItem.scheduled_at.desc().nullslast()).limit(request_in.limit)
        cal_result = await db.execute(cal_query)
        cals = cal_result.scalars().all()
        for c in cals:
            results.append(SearchResultItem(
                id=c.id,
                entity_type="calendar_item",
                title=f"Calendar: {c.platform}",
                snippet=c.metadata.get("description", "")[:200] if c.metadata.get("description") else "",
                score=1.0,
                metadata={"platform": c.platform, "status": c.status, "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None},
                created_at=c.created_at,
                updated_at=c.updated_at,
            ))
        facets["calendar_item"] = len(cals)

    # Search brand profiles
    if "brand_profile" in entity_types:
        brand_query = select(BrandProfile).where(
            BrandProfile.workspace_id == ws_id,
            or_(
                BrandProfile.voice_description.ilike(search_term),
                BrandProfile.style_guidelines.ilike(search_term),
                BrandProfile.positioning_statement.ilike(search_term),
            )
        ).limit(request_in.limit)
        brand_result = await db.execute(brand_query)
        brands = brand_result.scalars().all()
        for b in brands:
            results.append(SearchResultItem(
                id=b.id,
                entity_type="brand_profile",
                title="Brand Profile",
                snippet=(b.voice_description or b.style_guidelines or "")[:200],
                score=1.0,
                metadata={"version": b.version},
                created_at=b.created_at,
                updated_at=b.updated_at,
            ))
        facets["brand_profile"] = len(brands)

    # Search brand rules
    if "brand_rule" in entity_types:
        rule_query = select(BrandRule).where(
            BrandRule.workspace_id == ws_id,
            or_(
                BrandRule.message.ilike(search_term),
                BrandRule.pattern.ilike(search_term),
            )
        ).limit(request_in.limit)
        rule_result = await db.execute(rule_query)
        rules = rule_result.scalars().all()
        for r in rules:
            results.append(SearchResultItem(
                id=r.id,
                entity_type="brand_rule",
                title=f"Rule: {r.rule_type}",
                snippet=r.message[:200],
                score=1.0,
                metadata={"rule_type": r.rule_type, "severity": r.severity, "is_active": r.is_active},
                created_at=r.created_at,
                updated_at=r.updated_at,
            ))
        facets["brand_rule"] = len(rules)

    # Sort by score (placeholder - would use actual relevance scoring)
    results.sort(key=lambda x: x.score, reverse=True)

    # Apply pagination
    total_results = len(results)
    results = results[request_in.offset:request_in.offset + request_in.limit]

    took_ms = int((time.time() - start_time) * 1000)

    return SearchResponse(
        query=query,
        total_results=total_results,
        results=results,
        took_ms=took_ms,
        facets={k: {"count": v} for k, v in facets.items()},
    )


# Semantic/vector search (placeholder - requires pgvector)
@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request_in: SemanticSearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Semantic/vector search using embeddings (placeholder)."""
    start_time = time.time()
    ws_id = request_in.workspace_id or workspace_id

    # TODO: Implement actual vector search using pgvector
    # This would use the embedding columns on entities
    # For now, fall back to keyword search

    # Create a keyword search request and delegate
    keyword_request = SearchRequest(
        query=request_in.query,
        entity_types=request_in.entity_types,
        workspace_id=ws_id,
        limit=request_in.limit,
    )

    result = await universal_search(keyword_request, request, db, ws_id)
    result.took_ms = int((time.time() - start_time) * 1000)
    return result


# Hybrid search (keyword + vector)
@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request_in: HybridSearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Hybrid search combining keyword and vector search (placeholder)."""
    start_time = time.time()
    ws_id = request_in.workspace_id or workspace_id

    # TODO: Implement actual hybrid search
    # Would combine keyword search results with vector search results
    # using the provided weights

    keyword_request = SearchRequest(
        query=request_in.query,
        entity_types=request_in.entity_types,
        workspace_id=ws_id,
        limit=request_in.limit,
    )

    result = await universal_search(keyword_request, request, db, ws_id)
    result.took_ms = int((time.time() - start_time) * 1000)
    return result


# Search suggestions/autocomplete
@router.post("/suggestions", response_model=SearchSuggestionResponse)
async def search_suggestions(
    request_in: SearchSuggestionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get search suggestions/autocomplete."""
    ws_id = request_in.workspace_id or workspace_id
    query = request_in.query.lower()

    suggestions = set()

    # Get suggestions from ideas titles
    if not request_in.entity_types or "idea" in request_in.entity_types:
        idea_query = select(Idea.title).where(
            Idea.workspace_id == ws_id,
            Idea.title.ilike(f"%{query}%"),
        ).limit(request_in.limit)
        idea_result = await db.execute(idea_query)
        for title in idea_result.scalars().all():
            if title:
                suggestions.add(title)

    # Get suggestions from content outputs titles
    if not request_in.entity_types or "content_output" in request_in.entity_types:
        content_query = select(ContentOutput.title).where(
            ContentOutput.workspace_id == ws_id,
            ContentOutput.title.ilike(f"%{query}%"),
        ).limit(request_in.limit)
        content_result = await db.execute(content_query)
        for title in content_result.scalars().all():
            if title:
                suggestions.add(title)

    # Get suggestions from brand profile terms
    if not request_in.entity_types or "brand_profile" in request_in.entity_types:
        brand_query = select(BrandProfile.value_propositions).where(
            BrandProfile.workspace_id == ws_id,
        ).limit(1)
        brand_result = await db.execute(brand_query)
        brand = brand_result.scalar_one_or_none()
        if brand:
            for vp in brand:
                if query in vp.lower():
                    suggestions.add(vp)

    # Get suggestions from captures source_text (first few words)
    if not request_in.entity_types or "capture" in request_in.entity_types:
        capture_query = select(Capture.source_text).where(
            Capture.workspace_id == ws_id,
            Capture.source_text.ilike(f"%{query}%"),
        ).limit(request_in.limit)
        capture_result = await db.execute(capture_query)
        for text in capture_result.scalars().all():
            if text:
                # Extract first sentence as suggestion
                first_sentence = text.split(".")[0].strip()
                if len(first_sentence) > 10 and len(first_sentence) < 100:
                    suggestions.add(first_sentence)

    return SearchSuggestionResponse(
        suggestions=list(suggestions)[:request_in.limit],
        query=query,
    )