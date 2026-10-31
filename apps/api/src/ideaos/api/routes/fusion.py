"""Fusion routes."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from ideaos.core.config import get_settings
from ideaos.core.database import get_db
from ideaos.models import Idea, IdeaRelation, FusionProposal, Workspace
from ideaos.services.ai_service import ai_service
from ideaos.schemas.fusion import (
    FusionProposalResponse,
    FusionSuggestRequest,
    FusionApproveRequest,
    FusionRejectRequest,
    FusionEditRequest,
    IdeaConnectionsResponse,
    IdeaRelationResponse,
)

router = APIRouter()
settings = get_settings()


async def get_current_workspace_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract workspace_id from request state or fallback to default workspace in development."""
    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id:
        return UUID(str(workspace_id))
    if settings.ENVIRONMENT == "development":
        result = await db.execute(select(Workspace.id).limit(1))
        ws_id = result.scalar_one_or_none()
        if ws_id:
            return ws_id
    raise HTTPException(status_code=401, detail="Workspace context required")


async def get_current_user_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract user_id from request state or fallback to default workspace owner in development."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return UUID(str(user_id))
    if settings.ENVIRONMENT == "development":
        result = await db.execute(select(Workspace.owner_id).limit(1))
        u_id = result.scalar_one_or_none()
        if u_id:
            return u_id
    raise HTTPException(status_code=401, detail="Authentication required")


@router.get("/proposals", response_model=List[FusionProposalResponse])
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


@router.post("/suggest", response_model=List[FusionProposalResponse])
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

    # Fetch existing proposals
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
    proposals = list(result.scalars().all())

    if not proposals:
        # Fetch other ideas in workspace to run fusion synthesis
        cand_result = await db.execute(
            select(Idea)
            .where(Idea.workspace_id == workspace_id, Idea.id != request_in.idea_id)
            .limit(5)
        )
        candidates = cand_result.scalars().all()

        if candidates:
            new_idea_dict = {"title": idea.title, "summary": idea.summary}
            cand_dicts = [{"id": str(c.id), "title": c.title, "summary": c.summary} for c in candidates]
            generated_fusions = await ai_service.generate_idea_fusion(new_idea_dict, cand_dicts)

            for gf in generated_fusions:
                # Include both the new idea and candidate ideas so source_idea_ids >= 2
                source_uuids = [idea.id]
                for sid in gf.get("source_idea_ids", []):
                    try:
                        uid = UUID(str(sid))
                        if uid not in source_uuids:
                            source_uuids.append(uid)
                    except Exception:
                        pass
                if len(source_uuids) < 2 and candidates:
                    for c in candidates:
                        if c.id not in source_uuids:
                            source_uuids.append(c.id)
                        if len(source_uuids) >= 2:
                            break

                proposal = FusionProposal(
                    workspace_id=workspace_id,
                    new_idea_id=idea.id,
                    source_idea_ids=source_uuids,
                    relationships=gf.get("relationships", []),
                    fusion_concept=gf.get("fusion_concept", "Synthesized Master Concept"),
                    content_opportunities=gf.get("content_opportunities", []),
                    confidence=gf.get("confidence", 0.85),
                    status="pending",
                )
                db.add(proposal)
                proposals.append(proposal)

            await db.commit()
            for p in proposals:
                await db.refresh(p)

    return proposals


@router.post("/{proposal_id}/approve", response_model=FusionProposalResponse)
async def approve_fusion(
    proposal_id: UUID,
    request_in: FusionApproveRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    user_id: UUID = Depends(get_current_user_id),
):
    """Approve a fusion proposal."""
    from sqlalchemy import func

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


@router.post("/{proposal_id}/reject", response_model=FusionProposalResponse)
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


@router.post("/{proposal_id}/edit", response_model=FusionProposalResponse)
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


@router.get("/ideas/{idea_id}/connections", response_model=IdeaConnectionsResponse)
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


@router.get("/relations", response_model=List[IdeaRelationResponse])
async def list_idea_relations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    relation_type: Optional[str] = Query(None),
    min_confidence: float = Query(0.5),
    limit: int = Query(100, le=500),
):
    """List all idea relations in workspace."""
    query = select(IdeaRelation).where(
        IdeaRelation.workspace_id == workspace_id,
        IdeaRelation.is_active == True,
        IdeaRelation.confidence >= min_confidence,
    )

    if relation_type:
        query = query.where(IdeaRelation.relation_type == relation_type)

    query = query.options(
        selectinload(IdeaRelation.source_idea),
        selectinload(IdeaRelation.target_idea),
    ).order_by(IdeaRelation.confidence.desc()).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()