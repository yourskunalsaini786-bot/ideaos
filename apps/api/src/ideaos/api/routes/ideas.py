"""Idea routes."""
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from pgvector.sqlalchemy import Vector

from ideaos.core.database import get_db
from ideaos.models import Idea, IdeaSource, IdeaRelation, FusionProposal
from ideaos.schemas.ideas import (
    IdeaResponse,
    IdeaListResponse,
    IdeaConnectionsResponse,
    IdeaUpdate,
    FusionProposalResponse,
    FusionSuggestRequest,
    FusionApproveRequest,
    FusionRejectRequest,
    FusionEditRequest,
)

from ideaos.core.config import get_settings

settings = get_settings()
router = APIRouter()


async def get_current_workspace_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract workspace_id from request state with dev fallback."""
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


async def get_current_user_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract user_id from request state with dev fallback."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return UUID(str(user_id))
    if settings.ENVIRONMENT == "development":
        from ideaos.models import User
        result = await db.execute(select(User.id).limit(1))
        u_id = result.scalar_one_or_none()
        if u_id:
            return u_id
        return UUID("00000000-0000-0000-0000-000000000002")
    raise HTTPException(status_code=401, detail="Authentication required")


@router.get("", response_model=IdeaListResponse)
async def list_ideas(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    status: Optional[str] = Query(None),
    content_pillar: Optional[str] = Query(None),
    main_topic: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort: str = Query("created_desc"),
):
    """List ideas with filtering and pagination."""
    query = select(Idea).where(Idea.workspace_id == workspace_id)

    if status:
        query = query.where(Idea.status == status)
    if content_pillar:
        query = query.where(Idea.content_pillar == content_pillar)
    if main_topic:
        query = query.where(Idea.main_topic == main_topic)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Idea.title.ilike(search_term),
                Idea.summary.ilike(search_term),
                Idea.original_thought.ilike(search_term),
            )
        )

    # Sorting
    if sort == "created_desc":
        query = query.order_by(Idea.created_at.desc())
    elif sort == "created_asc":
        query = query.order_by(Idea.created_at.asc())
    elif sort == "updated_desc":
        query = query.order_by(Idea.updated_at.desc())
    else:
        query = query.order_by(Idea.created_at.desc())

    # Cursor pagination
    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            if sort.endswith("_desc"):
                query = query.where(Idea.created_at < cursor_dt)
            else:
                query = query.where(Idea.created_at > cursor_dt)
        except ValueError:
            pass

    query = query.options(
        selectinload(Idea.sources).selectinload(IdeaSource.capture),
        selectinload(Idea.sources).selectinload(IdeaSource.asset),
    ).limit(limit + 1)

    result = await db.execute(query)
    ideas = result.scalars().all()

    has_more = len(ideas) > limit
    if has_more:
        ideas = ideas[:limit]

    next_cursor = None
    if has_more and ideas:
        next_cursor = ideas[-1].created_at.isoformat()

    return IdeaListResponse(data=ideas, next_cursor=next_cursor, has_more=has_more)


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    idea_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get idea by ID with sources."""
    result = await db.execute(
        select(Idea)
        .where(Idea.id == idea_id, Idea.workspace_id == workspace_id)
        .options(
            selectinload(Idea.sources).selectinload(IdeaSource.capture),
            selectinload(Idea.sources).selectinload(IdeaSource.asset),
        )
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.get("/{idea_id}/connections", response_model=IdeaConnectionsResponse)
async def get_idea_connections(
    idea_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    include_proposals: bool = Query(True),
    relation_types: Optional[List[str]] = Query(None),
    min_confidence: float = Query(0.5),
):
    """Get related ideas and fusion proposals for an idea."""
    # Verify idea exists
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.workspace_id == workspace_id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Get relations
    query = select(IdeaRelation).where(
        IdeaRelation.workspace_id == workspace_id,
        or_(
            IdeaRelation.source_idea_id == idea_id,
            IdeaRelation.target_idea_id == idea_id,
        ),
        IdeaRelation.is_active == True,
        IdeaRelation.confidence >= min_confidence,
    )

    if relation_types:
        query = query.where(IdeaRelation.relation_type.in_(relation_types))

    query = query.options(
        selectinload(IdeaRelation.source_idea),
        selectinload(IdeaRelation.target_idea),
    ).order_by(IdeaRelation.confidence.desc())

    result = await db.execute(query)
    relations = result.scalars().all()

    # Get fusion proposals
    proposals = []
    if include_proposals:
        result = await db.execute(
            select(FusionProposal)
            .where(
                FusionProposal.workspace_id == workspace_id,
                FusionProposal.new_idea_id == idea_id,
                FusionProposal.status == "pending",
            )
            .order_by(FusionProposal.confidence.desc())
        )
        proposals = result.scalars().all()

    return IdeaConnectionsResponse(relations=relations, fusion_proposals=proposals)


@router.patch("/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: UUID,
    idea_in: IdeaUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Update idea metadata."""
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.workspace_id == workspace_id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    update_data = idea_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(idea, field, value)

    idea.version += 1
    await db.commit()
    await db.refresh(idea)
    return idea


# Fusion endpoints
@router.post("/fusion/suggest", response_model=List[FusionProposalResponse])
async def suggest_fusions(
    request_in: FusionSuggestRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Trigger fusion analysis for an idea."""
    # Verify idea exists
    result = await db.execute(
        select(Idea).where(Idea.id == request_in.idea_id, Idea.workspace_id == workspace_id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # TODO: Trigger async fusion job via Temporal/Celery
    # For now, return existing proposals
    result = await db.execute(
        select(FusionProposal)
        .where(
            FusionProposal.workspace_id == workspace_id,
            FusionProposal.new_idea_id == request_in.idea_id,
            FusionProposal.confidence >= request_in.min_confidence,
        )
        .order_by(FusionProposal.confidence.desc())
        .limit(request_in.max_candidates)
    )
    proposals = result.scalars().all()
    return proposals


@router.get("/fusion/proposals", response_model=List[FusionProposalResponse])
async def list_fusion_proposals(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
):
    """List fusion proposals for workspace."""
    query = select(FusionProposal).where(FusionProposal.workspace_id == workspace_id)

    if status:
        query = query.where(FusionProposal.status == status)

    query = query.order_by(FusionProposal.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/fusion/{proposal_id}/approve", response_model=FusionProposalResponse)
async def approve_fusion(
    proposal_id: UUID,
    request_in: FusionApproveRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    user_id: UUID = Depends(get_current_user_id),
):
    """Approve a fusion proposal."""
    result = await db.execute(
        select(FusionProposal)
        .where(FusionProposal.id == proposal_id, FusionProposal.workspace_id == workspace_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="Fusion proposal not found")

    if proposal.status != "pending":
        raise HTTPException(status_code=400, detail="Proposal already processed")

    proposal.status = "approved"
    proposal.approved_by = user_id
    proposal.approved_at = func.now()

    if request_in.create_master_idea:
        # Create master idea from fusion
        master_idea = Idea(
            workspace_id=workspace_id,
            title=request_in.master_idea_title or proposal.fusion_concept[:100],
            summary=proposal.fusion_concept,
            original_thought=proposal.fusion_concept,
            content_pillar=proposal.content_opportunities[0].get("pillar") if proposal.content_opportunities else None,
            suggested_formats=[op.get("format") for op in proposal.content_opportunities if op.get("format")],
            suggested_platforms=[op.get("platform") for op in proposal.content_opportunities if op.get("platform")],
            status="approved",
            parent_idea_id=proposal.new_idea_id,
            fusion_source_ids=proposal.source_idea_ids,
        )
        db.add(master_idea)
        await db.flush()
        proposal.new_idea_id = master_idea.id

    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.post("/fusion/{proposal_id}/reject", response_model=FusionProposalResponse)
async def reject_fusion(
    proposal_id: UUID,
    request_in: FusionRejectRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Reject a fusion proposal."""
    result = await db.execute(
        select(FusionProposal)
        .where(FusionProposal.id == proposal_id, FusionProposal.workspace_id == workspace_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="Fusion proposal not found")

    if proposal.status != "pending":
        raise HTTPException(status_code=400, detail="Proposal already processed")

    proposal.status = "rejected"
    proposal.rejected_reason = request_in.reason
    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.post("/fusion/{proposal_id}/edit", response_model=FusionProposalResponse)
async def edit_fusion(
    proposal_id: UUID,
    request_in: FusionEditRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Edit a fusion proposal."""
    result = await db.execute(
        select(FusionProposal)
        .where(FusionProposal.id == proposal_id, FusionProposal.workspace_id == workspace_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="Fusion proposal not found")

    proposal.status = "edited"
    proposal.edited_fusion_concept = request_in.fusion_concept

    if request_in.create_master_idea:
        master_idea = Idea(
            workspace_id=workspace_id,
            title=request_in.fusion_concept[:100],
            summary=request_in.fusion_concept,
            original_thought=request_in.fusion_concept,
            status="approved",
            parent_idea_id=proposal.new_idea_id,
            fusion_source_ids=proposal.source_idea_ids,
        )
        db.add(master_idea)
        await db.flush()
        proposal.new_idea_id = master_idea.id

    await db.commit()
    await db.refresh(proposal)
    return proposal