"""Media Repurposing Studio Router - End-to-end workflow."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ideaos.core.database import get_db
from ideaos.models import (
    User,
    Workspace,
    WorkspaceMember,
    Capture,
    Idea,
    ContentOutput,
    CalendarItem,
    BrandProfile,
    BrandRule,
    FeedbackEvent,
)
from ideaos.schemas.repurpose import (
    MediaIngestRequest,
    MediaIngestResponse,
    ClipGenerateRequest,
    ClipGenerateResponse,
    CreatorEditAndApproveRequest,
    CreatorEditAndApproveResponse,
    PerformanceFeedbackRequest,
    PerformanceFeedbackResponse,
)
from ideaos.services.ai_service import ai_service

router = APIRouter()


async def get_or_create_default_workspace(db: AsyncSession, request: Request) -> Workspace:
    """Ensure a valid workspace context exists, creating a default one for local/demo runs."""
    ws_id = getattr(request.state, "workspace_id", None)
    if ws_id:
        try:
            ws_uuid = uuid.UUID(str(ws_id))
            result = await db.execute(select(Workspace).where(Workspace.id == ws_uuid))
            ws = result.scalar_one_or_none()
            if ws:
                return ws
        except Exception:
            pass

    # Find first existing workspace or create default demo workspace
    result = await db.execute(select(Workspace).limit(1))
    ws = result.scalar_one_or_none()
    if ws:
        return ws

    # Create default demo user and workspace
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()
    if not user:
        user = User(
            email="creator@ideaos.local",
            name="Demo Creator",
        )
        db.add(user)
        await db.flush()

    ws = Workspace(
        name="Demo Creator Studio",
        slug="demo-creator-studio",
        owner_id=user.id,
        settings={"default_voice": "Authoritative and concise"},
    )
    db.add(ws)
    await db.flush()

    member = WorkspaceMember(
        workspace_id=ws.id,
        user_id=user.id,
        role="owner",
    )
    db.add(member)

    # Initialize default brand profile
    profile = BrandProfile(
        workspace_id=ws.id,
        voice_description="Direct, tactical, no-fluff insights for high-velocity creators and founders.",
        target_audience="Founders, creators, and operators building in public.",
        value_propositions=["10x content leverage through persistent brand intelligence"],
        prohibited_phrases=["synergy", "paradigm shift", "circle back"],
    )
    db.add(profile)
    await db.commit()
    await db.refresh(ws)
    return ws


@router.post("/ingest", response_model=MediaIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_media(
    request_in: MediaIngestRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 1 & 2 & 3 & 4: Ingest long-form media, extract timestamped transcript,
    and generate explainable clip candidates.
    """
    ws = await get_or_create_default_workspace(db, request)

    # 1. AI processing: Transcription, topic segmentation, and timestamp extraction
    transcript_data = await ai_service.transcribe_and_segment(
        media_text_or_filename=request_in.title or "Ingested Media",
        raw_text=request_in.content,
    )

    # 2. Extract clip opportunities with explicit rationale for each selection
    clips = await ai_service.extract_clip_opportunities(transcript_data)

    # 3. Create Capture record
    user_id = ws.owner_id
    capture = Capture(
        workspace_id=ws.id,
        user_id=user_id,
        type=request_in.media_type,
        status="completed",
        source_text=request_in.content,
        metadata={
            "transcript_data": transcript_data,
            "clips": clips,
            "duration_seconds": transcript_data.get("duration_seconds", 600),
        },
    )
    db.add(capture)
    await db.flush()

    # 4. Create Idea record representing this enriched media source
    title = request_in.title or transcript_data.get("title", "Ingested Media Highlights")
    idea = Idea(
        workspace_id=ws.id,
        capture_id=capture.id,
        title=title,
        summary=transcript_data.get("summary", ""),
        original_thought=request_in.content[:1000],
        main_topic=transcript_data.get("main_topic", "Media Repurposing"),
        content_pillar=request_in.content_pillar,
        suggested_formats=["reel", "post", "shorts", "thread"],
        suggested_platforms=["instagram", "linkedin", "youtube", "x"],
        keywords_entities=transcript_data.get("key_takeaways", []),
        status="approved",
    )
    db.add(idea)
    await db.flush()

    capture.idea_id = idea.id
    await db.commit()
    await db.refresh(capture)
    await db.refresh(idea)

    return MediaIngestResponse(
        capture_id=capture.id,
        idea_id=idea.id,
        title=idea.title,
        summary=idea.summary,
        main_topic=idea.main_topic,
        duration_seconds=float(transcript_data.get("duration_seconds", 600)),
        segments=transcript_data.get("segments", []),
        clip_opportunities=clips,
    )


@router.post("/generate", response_model=ClipGenerateResponse)
async def generate_clip_content(
    request_in: ClipGenerateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 5 & 6: Generate platform-specific copy tailored for Instagram, LinkedIn,
    YouTube Shorts, or X, applying persistent brand memory.
    """
    ws = await get_or_create_default_workspace(db, request)

    # Fetch active brand profile and rules
    bp_result = await db.execute(
        select(BrandProfile).where(BrandProfile.workspace_id == ws.id)
    )
    brand_profile = bp_result.scalar_one_or_none()

    rules_result = await db.execute(
        select(BrandRule).where(BrandRule.workspace_id == ws.id, BrandRule.is_active == True)
    )
    brand_rules = rules_result.scalars().all()

    bp_dict = {
        "voice_description": brand_profile.voice_description if brand_profile else "Authoritative & punchy",
        "target_audience": brand_profile.target_audience if brand_profile else "Modern creators and builders",
    }
    rules_list = [
        {
            "rule_type": r.rule_type,
            "pattern": r.pattern,
            "message": r.message,
            "is_active": r.is_active,
        }
        for r in brand_rules
    ]

    clip_dict = {
        "title": request_in.clip_title,
        "key_quote": request_in.key_quote,
        "selection_reason": request_in.selection_reason,
        "start_time": request_in.start_time,
        "end_time": request_in.end_time,
    }

    # Generate tailored platform copy
    generated = await ai_service.generate_platform_content(
        clip_data=clip_dict,
        platform=request_in.platform,
        format_type=request_in.format,
        brand_profile=bp_dict,
        brand_rules=rules_list,
    )

    return ClipGenerateResponse(
        idea_id=request_in.idea_id,
        platform=request_in.platform,
        format=request_in.format,
        title=generated.get("title", request_in.clip_title),
        hook=generated.get("hook", ""),
        body=generated.get("body", ""),
        cta=generated.get("cta"),
        hashtags=generated.get("hashtags", []),
        quality_score=float(generated.get("quality_score", 9.0)),
        quality_passed=bool(generated.get("quality_passed", True)),
        quality_warnings=generated.get("quality_warnings", []),
        visual_notes=generated.get("visual_notes", []),
    )


@router.post("/edit-and-approve", response_model=CreatorEditAndApproveResponse)
async def edit_and_approve_content(
    request_in: CreatorEditAndApproveRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 6, 7 & 8: Creator reviews and edits generated content.
    - Learns new Brand Rules from the creator's edits.
    - Saves ContentOutput.
    - Schedules on the Content Calendar.
    """
    ws = await get_or_create_default_workspace(db, request)

    # 1. Create approved ContentOutput record
    content_output = ContentOutput(
        workspace_id=ws.id,
        idea_id=request_in.idea_id,
        platform=request_in.platform,
        format=request_in.format,
        title=request_in.title or f"{request_in.platform} Repurposed Clip",
        hook=request_in.edited_content.split("\n")[0][:100],
        body=request_in.edited_content,
        status="approved" if not request_in.schedule_time else "scheduled",
        metadata={
            "original_content": request_in.original_content,
            "was_edited": request_in.original_content != request_in.edited_content,
        },
    )
    db.add(content_output)
    await db.flush()

    # 2. Add to Content Calendar if scheduling date is supplied
    calendar_item = None
    if request_in.schedule_time:
        calendar_item = CalendarItem(
            workspace_id=ws.id,
            content_output_id=content_output.id,
            platform=request_in.platform,
            status="scheduled",
            scheduled_at=request_in.schedule_time,
            metadata={"source_idea_id": str(request_in.idea_id)},
        )
        db.add(calendar_item)
        await db.flush()

    # 3. Extract and persist brand memory rules learned from creator's edits
    learned_rules = []
    if request_in.original_content != request_in.edited_content:
        extracted = await ai_service.learn_brand_rules_from_edit(
            original_content=request_in.original_content,
            edited_content=request_in.edited_content,
            platform=request_in.platform,
            format_type=request_in.format,
        )
        for r in extracted:
            brand_rule = BrandRule(
                workspace_id=ws.id,
                rule_type=r.get("rule_type", "must_avoid"),
                pattern=r.get("pattern"),
                severity=r.get("severity", "warning"),
                message=r.get("message", "Rule learned from creator edit"),
                examples=r.get("examples", []),
                applies_to=r.get("applies_to", [request_in.platform]),
                is_active=True,
                created_by=ws.owner_id,
            )
            db.add(brand_rule)
            learned_rules.append(r)

    # 4. Record feedback event
    event = FeedbackEvent(
        workspace_id=ws.id,
        user_id=ws.owner_id,
        entity_type="content_output",
        entity_id=content_output.id,
        action="edited_and_approved",
        before_state={"body": request_in.original_content},
        after_state={"body": request_in.edited_content},
    )
    db.add(event)

    await db.commit()
    await db.refresh(content_output)
    if calendar_item:
        await db.refresh(calendar_item)

    return CreatorEditAndApproveResponse(
        content_output_id=content_output.id,
        calendar_item_id=calendar_item.id if calendar_item else None,
        status="scheduled" if calendar_item else "approved",
        learned_brand_rules=learned_rules,
        message=f"Content approved. Extracted {len(learned_rules)} brand memory rules.",
    )


@router.post("/performance", response_model=PerformanceFeedbackResponse)
async def record_performance_feedback(
    request_in: PerformanceFeedbackRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 9: Performance feedback loop. Records engagement metrics
    to improve future recommendations and rankings.
    """
    ws = await get_or_create_default_workspace(db, request)

    # Verify content output exists
    result = await db.execute(
        select(ContentOutput).where(
            ContentOutput.id == request_in.content_output_id,
            ContentOutput.workspace_id == ws.id,
        )
    )
    content_output = result.scalar_one_or_none()
    if not content_output:
        raise HTTPException(status_code=404, detail="Content output not found")

    # Compute performance composite index
    views = max(1, request_in.views)
    engagement_points = (
        request_in.likes * 2 +
        request_in.comments * 4 +
        request_in.shares * 6
    )
    engagement_rate = (engagement_points / views) * 100
    retention_score = request_in.retention_rate or 0.65
    performance_score = round(min(10.0, (engagement_rate * 0.7) + (retention_score * 10.0 * 0.3)), 2)

    # Record feedback event
    event = FeedbackEvent(
        workspace_id=ws.id,
        user_id=ws.owner_id,
        entity_type="content_output",
        entity_id=content_output.id,
        action="performance_logged",
        before_state={"status": content_output.status},
        after_state={
            "performance_score": performance_score,
            "views": request_in.views,
            "likes": request_in.likes,
            "shares": request_in.shares,
            "comments": request_in.comments,
        },
    )
    db.add(event)

    # Update content output metadata with performance tag
    existing_meta = dict(content_output.metadata or {})
    existing_meta["performance_score"] = performance_score
    existing_meta["performance_tier"] = "top_performer" if performance_score >= 7.5 else "average"
    content_output.metadata = existing_meta

    await db.commit()
    await db.refresh(event)

    return PerformanceFeedbackResponse(
        feedback_event_id=event.id,
        content_output_id=content_output.id,
        performance_score=performance_score,
        status="recorded",
        recommendation_impact="Future clip selection and hook generators will prioritize patterns matching this high-performing post.",
    )
