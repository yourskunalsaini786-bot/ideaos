"""Feedback routes."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from ideaos.core.database import get_db
from ideaos.models import FeedbackEvent
from ideaos.schemas.feedback import (
    FeedbackEventCreate,
    FeedbackEventResponse,
    FeedbackEventListResponse,
    FeedbackAnalyticsRequest,
    FeedbackAnalyticsResponse,
)

router = APIRouter()


async def get_current_workspace_id(request: Request) -> UUID:
    """Extract workspace_id from request state."""
    workspace_id = getattr(request.state, "workspace_id", None)
    if not workspace_id:
        raise HTTPException(status_code=401, detail="Workspace context required")
    return UUID(workspace_id)


async def get_current_user_id(request: Request) -> UUID:
    """Extract user_id from request state."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return UUID(user_id)


@router.post("", response_model=FeedbackEventResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback_event(
    event_in: FeedbackEventCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a feedback event."""
    event = FeedbackEvent(
        workspace_id=workspace_id,
        user_id=user_id,
        **event_in.model_dump(),
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("", response_model=FeedbackEventListResponse)
async def list_feedback_events(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    user_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    cursor: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    """List feedback events with filtering and pagination."""
    query = select(FeedbackEvent).where(FeedbackEvent.workspace_id == workspace_id)

    if entity_type:
        query = query.where(FeedbackEvent.entity_type == entity_type)
    if action:
        query = query.where(FeedbackEvent.action == action)
    if user_id:
        query = query.where(FeedbackEvent.user_id == user_id)
    if start_date:
        query = query.where(FeedbackEvent.created_at >= start_date)
    if end_date:
        query = query.where(FeedbackEvent.created_at <= end_date)
    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            query = query.where(FeedbackEvent.created_at < cursor_dt)
        except ValueError:
            pass

    query = query.order_by(FeedbackEvent.created_at.desc()).limit(limit + 1)
    result = await db.execute(query)
    events = result.scalars().all()

    has_more = len(events) > limit
    if has_more:
        events = events[:limit]

    next_cursor = None
    if has_more and events:
        next_cursor = events[-1].created_at.isoformat()

    return FeedbackEventListResponse(data=events, next_cursor=next_cursor, has_more=has_more)


@router.get("/{event_id}", response_model=FeedbackEventResponse)
async def get_feedback_event(
    event_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get feedback event by ID."""
    result = await db.execute(
        select(FeedbackEvent)
        .where(FeedbackEvent.id == event_id, FeedbackEvent.workspace_id == workspace_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Feedback event not found")
    return event


@router.get("/analytics/summary", response_model=FeedbackAnalyticsResponse)
async def get_feedback_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Get feedback analytics summary."""
    base_query = select(FeedbackEvent).where(FeedbackEvent.workspace_id == workspace_id)

    if entity_type:
        base_query = base_query.where(FeedbackEvent.entity_type == entity_type)
    if action:
        base_query = base_query.where(FeedbackEvent.action == action)
    if start_date:
        base_query = base_query.where(FeedbackEvent.created_at >= start_date)
    if end_date:
        base_query = base_query.where(FeedbackEvent.created_at <= end_date)

    # Total count
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total_events = total_result.scalar() or 0

    # By action
    action_result = await db.execute(
        select(FeedbackEvent.action, func.count(FeedbackEvent.id))
        .where(FeedbackEvent.workspace_id == workspace_id)
        .group_by(FeedbackEvent.action)
    )
    by_action = {row[0]: row[1] for row in action_result.all()}

    # By entity type
    entity_result = await db.execute(
        select(FeedbackEvent.entity_type, func.count(FeedbackEvent.id))
        .where(FeedbackEvent.workspace_id == workspace_id)
        .group_by(FeedbackEvent.entity_type)
    )
    by_entity_type = {row[0]: row[1] for row in entity_result.all()}

    # Top reason categories
    reason_result = await db.execute(
        select(FeedbackEvent.reason_category, func.count(FeedbackEvent.id))
        .where(
            FeedbackEvent.workspace_id == workspace_id,
            FeedbackEvent.reason_category.isnot(None),
        )
        .group_by(FeedbackEvent.reason_category)
        .order_by(func.count(FeedbackEvent.id).desc())
        .limit(10)
    )
    top_reason_categories = [
        {"category": row[0], "count": row[1]} for row in reason_result.all()
    ]

    # Recent events
    recent_query = base_query.order_by(FeedbackEvent.created_at.desc()).limit(limit)
    recent_result = await db.execute(recent_query)
    recent_events = recent_result.scalars().all()

    return FeedbackAnalyticsResponse(
        total_events=total_events,
        by_action=by_action,
        by_entity_type=by_entity_type,
        top_reason_categories=top_reason_categories,
        recent_events=recent_events,
    )


@router.get("/entity/{entity_type}/{entity_id}", response_model=FeedbackEventListResponse)
async def get_feedback_for_entity(
    entity_type: str,
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    limit: int = Query(50, le=200),
):
    """Get all feedback events for a specific entity."""
    query = select(FeedbackEvent).where(
        FeedbackEvent.workspace_id == workspace_id,
        FeedbackEvent.entity_type == entity_type,
        FeedbackEvent.entity_id == entity_id,
    ).order_by(FeedbackEvent.created_at.desc()).limit(limit)

    result = await db.execute(query)
    events = result.scalars().all()

    return FeedbackEventListResponse(data=events, next_cursor=None, has_more=False)