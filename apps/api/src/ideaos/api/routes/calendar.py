"""Calendar routes - dedicated calendar endpoints."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from ideaos.core.database import get_db
from ideaos.models import CalendarItem, ContentOutput
from ideaos.schemas.content import (
    CalendarItemCreate,
    CalendarItemUpdate,
    CalendarItemResponse,
    CalendarItemListResponse,
    CalendarBatchScheduleRequest,
)

router = APIRouter()


from ideaos.core.config import get_settings

settings = get_settings()


async def get_current_workspace_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract workspace_id from request state or fallback to default workspace in development."""
    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id:
        return UUID(str(workspace_id))
    if settings.ENVIRONMENT == "development":
        from ideaos.models import Workspace
        result = await db.execute(select(Workspace.id).order_by(Workspace.created_at.asc()).limit(1))
        ws_id = result.scalar_one_or_none()
        if ws_id:
            return ws_id
    raise HTTPException(status_code=401, detail="Workspace context required")


async def get_current_user_id(request: Request) -> UUID:
    """Extract user_id from request state."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return UUID(user_id)


@router.post("", response_model=CalendarItemResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=CalendarItemListResponse)
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


@router.get("/{item_id}", response_model=CalendarItemResponse)
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


@router.patch("/{item_id}", response_model=CalendarItemResponse)
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


@router.post("/batch", response_model=List[CalendarItemResponse])
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


@router.delete("/{item_id}")
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


@router.get("/week/view", response_model=CalendarItemListResponse)
async def get_week_view(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    week_start: datetime = Query(...),
):
    """Get calendar items for a specific week."""
    from datetime import timedelta
    week_end = week_start + timedelta(days=7)

    result = await db.execute(
        select(CalendarItem)
        .where(
            CalendarItem.workspace_id == workspace_id,
            CalendarItem.scheduled_at >= week_start,
            CalendarItem.scheduled_at < week_end,
        )
        .order_by(CalendarItem.scheduled_at.asc())
    )
    items = result.scalars().all()

    return CalendarItemListResponse(data=items, next_cursor=None, has_more=False)


@router.get("/month/view", response_model=CalendarItemListResponse)
async def get_month_view(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    month_start: datetime = Query(...),
):
    """Get calendar items for a specific month."""
    from datetime import timedelta
    # Calculate month end (first day of next month)
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1)

    result = await db.execute(
        select(CalendarItem)
        .where(
            CalendarItem.workspace_id == workspace_id,
            CalendarItem.scheduled_at >= month_start,
            CalendarItem.scheduled_at < month_end,
        )
        .order_by(CalendarItem.scheduled_at.asc())
    )
    items = result.scalars().all()

    return CalendarItemListResponse(data=items, next_cursor=None, has_more=False)