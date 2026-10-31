"""Content routes."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from ideaos.core.database import get_db
from ideaos.models import ContentOutput, CalendarItem
from ideaos.schemas.content import (
    ContentOutputCreate,
    ContentOutputUpdate,
    ContentOutputResponse,
    ContentOutputListResponse,
    CalendarItemCreate,
    CalendarItemUpdate,
    CalendarItemResponse,
    CalendarItemListResponse,
    CalendarBatchScheduleRequest,
    ContentGenerationRequest,
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


# Content Output routes
@router.post("", response_model=ContentOutputResponse, status_code=status.HTTP_201_CREATED)
async def create_content_output(
    content_in: ContentOutputCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a content output."""
    # Verify idea exists and belongs to workspace
    from ideaos.models import Idea
    result = await db.execute(
        select(Idea).where(Idea.id == content_in.idea_id, Idea.workspace_id == workspace_id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    content = ContentOutput(
        workspace_id=workspace_id,
        **content_in.model_dump(),
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return content


@router.get("", response_model=ContentOutputListResponse)
async def list_content_outputs(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    idea_id: Optional[UUID] = Query(None),
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
):
    """List content outputs with filtering and pagination."""
    query = select(ContentOutput).where(ContentOutput.workspace_id == workspace_id)

    if idea_id:
        query = query.where(ContentOutput.idea_id == idea_id)
    if platform:
        query = query.where(ContentOutput.platform == platform)
    if status:
        query = query.where(ContentOutput.status == status)
    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            query = query.where(ContentOutput.created_at < cursor_dt)
        except ValueError:
            pass

    query = query.order_by(ContentOutput.created_at.desc()).limit(limit + 1)
    result = await db.execute(query)
    contents = result.scalars().all()

    has_more = len(contents) > limit
    if has_more:
        contents = contents[:limit]

    next_cursor = None
    if has_more and contents:
        next_cursor = contents[-1].created_at.isoformat()

    return ContentOutputListResponse(data=contents, next_cursor=next_cursor, has_more=has_more)


@router.get("/{content_id}", response_model=ContentOutputResponse)
async def get_content_output(
    content_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get content output by ID."""
    result = await db.execute(
        select(ContentOutput)
        .where(ContentOutput.id == content_id, ContentOutput.workspace_id == workspace_id)
        .options(selectinload(ContentOutput.calendar_items))
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content output not found")
    return content


@router.patch("/{content_id}", response_model=ContentOutputResponse)
async def update_content_output(
    content_id: UUID,
    content_in: ContentOutputUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Update content output."""
    result = await db.execute(
        select(ContentOutput).where(ContentOutput.id == content_id, ContentOutput.workspace_id == workspace_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content output not found")

    update_data = content_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)

    content.version += 1
    await db.commit()
    await db.refresh(content)
    return content


@router.delete("/{content_id}")
async def delete_content_output(
    content_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Delete (soft delete) content output."""
    result = await db.execute(
        select(ContentOutput).where(ContentOutput.id == content_id, ContentOutput.workspace_id == workspace_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content output not found")

    content.deleted_at = func.now()
    await db.commit()
    return {"message": "Content output deleted"}


@router.post("/generate", response_model=List[ContentOutputResponse])
async def generate_content(
    request_in: ContentGenerationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Generate content from an idea (placeholder - actual generation via Temporal)."""
    # Verify idea exists
    from ideaos.models import Idea
    result = await db.execute(
        select(Idea).where(Idea.id == request_in.idea_id, Idea.workspace_id == workspace_id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # TODO: Trigger async content generation job via Temporal/Celery
    # For now, return empty list - actual implementation would create ContentOutput records
    return []


# Calendar routes
@router.post("/calendar", response_model=CalendarItemResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar_item(
    item_in: CalendarItemCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Create a calendar item."""
    # Verify content output exists and belongs to workspace
    result = await db.execute(
        select(ContentOutput).where(ContentOutput.id == item_in.content_output_id, ContentOutput.workspace_id == workspace_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content output not found")

    item = CalendarItem(
        workspace_id=workspace_id,
        **item_in.model_dump(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/calendar", response_model=CalendarItemListResponse)
async def list_calendar_items(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    cursor: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    """List calendar items with filtering and pagination."""
    query = select(CalendarItem).where(CalendarItem.workspace_id == workspace_id)

    if platform:
        query = query.where(CalendarItem.platform == platform)
    if status:
        query = query.where(CalendarItem.status == status)
    if start_date:
        query = query.where(CalendarItem.scheduled_at >= start_date)
    if end_date:
        query = query.where(CalendarItem.scheduled_at <= end_date)
    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            query = query.where(CalendarItem.scheduled_at < cursor_dt)
        except ValueError:
            pass

    query = query.order_by(CalendarItem.scheduled_at.asc().nullslast()).limit(limit + 1)
    result = await db.execute(query)
    items = result.scalars().all()

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    next_cursor = None
    if has_more and items:
        next_cursor = items[-1].scheduled_at.isoformat() if items[-1].scheduled_at else items[-1].created_at.isoformat()

    return CalendarItemListResponse(data=items, next_cursor=next_cursor, has_more=has_more)


@router.get("/calendar/{item_id}", response_model=CalendarItemResponse)
async def get_calendar_item(
    item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get calendar item by ID."""
    result = await db.execute(
        select(CalendarItem)
        .where(CalendarItem.id == item_id, CalendarItem.workspace_id == workspace_id)
        .options(selectinload(CalendarItem.content_output))
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Calendar item not found")
    return item


@router.patch("/calendar/{item_id}", response_model=CalendarItemResponse)
async def update_calendar_item(
    item_id: UUID,
    item_in: CalendarItemUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Update calendar item."""
    result = await db.execute(
        select(CalendarItem).where(CalendarItem.id == item_id, CalendarItem.workspace_id == workspace_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Calendar item not found")

    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    if item.status == "published" and item.published_at is None:
        item.published_at = func.now()

    await db.commit()
    await db.refresh(item)
    return item


@router.post("/calendar/batch", response_model=List[CalendarItemResponse])
async def batch_create_calendar_items(
    request_in: CalendarBatchScheduleRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Batch create calendar items."""
    items = []
    for item_in in request_in.items:
        # Verify content output exists
        result = await db.execute(
            select(ContentOutput).where(ContentOutput.id == item_in.content_output_id, ContentOutput.workspace_id == workspace_id)
        )
        content = result.scalar_one_or_none()
        if not content:
            raise HTTPException(status_code=404, detail=f"Content output {item_in.content_output_id} not found")

        item = CalendarItem(
            workspace_id=workspace_id,
            **item_in.model_dump(),
        )
        db.add(item)
        items.append(item)

    await db.commit()
    for item in items:
        await db.refresh(item)
    return items


@router.delete("/calendar/{item_id}")
async def delete_calendar_item(
    item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Delete calendar item."""
    result = await db.execute(
        select(CalendarItem).where(CalendarItem.id == item_id, CalendarItem.workspace_id == workspace_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Calendar item not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Calendar item deleted"}