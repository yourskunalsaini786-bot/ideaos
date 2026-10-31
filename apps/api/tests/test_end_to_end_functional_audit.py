"""End-to-End Functional Audit Test Suite for IdeaOS.

Validates:
- Phase 1: Keywords schema compatibility, environment isolation, workspace security
- Phase 2: Real database persistence across closed sessions
- Phase 3: Idea Fusion synthesis with real DB records and proposal approval lifecycle
- Phase 4: Controlled transcript media ingestion, timestamping, explainable clips, multi-platform generation
- Phase 5: Brand Memory learning loop from creator edits and persistent rule retrieval
- Phase 6: Calendar scheduling and empirical performance feedback recording
"""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from ideaos.main import app
from ideaos.core.config import get_settings
from ideaos.core.database import init_db, close_db, get_db_context
from ideaos.models import (
    Workspace,
    User,
    WorkspaceMember,
    Capture,
    Idea,
    ContentOutput,
    CalendarItem,
    BrandRule,
    FeedbackEvent,
    FusionProposal,
)
from ideaos.schemas.ideas import IdeaResponse

settings = get_settings()


def test_phase1_environment_isolation_and_schemas():
    """Verify production workspace isolation and keywords_entities schema compatibility."""
    async def run():
        await init_db()

        # 1. Verify keywords_entities accepts both dict and string formats
        schema_test_dict = {
            "id": uuid.uuid4(),
            "workspace_id": uuid.uuid4(),
            "title": "Schema Test Idea",
            "summary": "Testing schema resilience",
            "original_thought": "Robust schema verification",
            "suggested_formats": ["post"],
            "suggested_platforms": ["linkedin"],
            "keywords_entities": [
                {"entity": "IdeaOS", "type": "product"},
                "plain string keyword",
                "another keyword entity"
            ],
            "status": "active",
            "version": 1,
            "fusion_source_ids": [],
            "sources": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        validated = IdeaResponse.model_validate(schema_test_dict)
        assert len(validated.keywords_entities) == 3
        assert isinstance(validated.keywords_entities[0], dict)
        assert isinstance(validated.keywords_entities[1], str)

        # 2. Verify that in production mode, missing workspace context returns 401
        original_env = settings.ENVIRONMENT
        try:
            settings.ENVIRONMENT = "production"
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                res = await client.get("/api/v1/captures")
                assert res.status_code == 401, f"Expected 401 in production, got {res.status_code}"
                assert "Workspace context required" in res.text

                res_brand = await client.get("/api/v1/brand/rules")
                assert res_brand.status_code == 401, f"Expected 401 in production, got {res_brand.status_code}"
        finally:
            settings.ENVIRONMENT = original_env

    asyncio.run(run())


def test_phase2_real_database_persistence():
    """Verify real database record persistence across completely closed sessions."""
    async def run():
        await init_db()
        test_content = f"QA_TEST_CAPTURE_{uuid.uuid4().hex[:8]}"

        # Step 1: Create a dedicated test workspace and user
        async with get_db_context() as session:
            test_user = User(
                email=f"qa-{uuid.uuid4().hex[:6]}@ideaos.test",
                name="QA Persistence Tester",
            )
            session.add(test_user)
            await session.flush()

            test_ws = Workspace(
                name="QA Isolation Studio",
                slug=f"qa-studio-{uuid.uuid4().hex[:6]}",
                owner_id=test_user.id,
                settings={"voice": "analytical"},
            )
            session.add(test_ws)
            await session.flush()

            member = WorkspaceMember(
                workspace_id=test_ws.id,
                user_id=test_user.id,
                role="owner",
            )
            session.add(member)

            # Insert capture directly or via API with workspace context
            capture = Capture(
                workspace_id=test_ws.id,
                user_id=test_user.id,
                type="note",
                status="processed",
                source_text=test_content,
                metadata={"test_run": True, "tag": "phase2_qa"},
            )
            session.add(capture)
            await session.commit()
            capture_id = capture.id
            ws_id = test_ws.id

        # Step 2: The session is completely closed. Re-query with a brand new session.
        async with get_db_context() as fresh_session:
            result = await fresh_session.execute(
                select(Capture).where(Capture.id == capture_id)
            )
            persisted_capture = result.scalar_one_or_none()
            assert persisted_capture is not None, "Capture failed to persist after session close"
            assert persisted_capture.id == capture_id
            assert persisted_capture.source_text == test_content
            assert persisted_capture.workspace_id == ws_id

            # Update the record (re-assigning dictionary for SQLAlchemy change detection)
            updated_meta = dict(persisted_capture.metadata)
            updated_meta["status_updated"] = True
            persisted_capture.metadata = updated_meta
            persisted_capture.status = "archived"
            await fresh_session.commit()

        # Step 3: Re-verify the update in a third independent session
        async with get_db_context() as verify_session:
            result = await verify_session.execute(
                select(Capture).where(Capture.id == capture_id)
            )
            updated_capture = result.scalar_one()
            assert updated_capture.status == "archived"
            assert updated_capture.metadata.get("status_updated") is True

    asyncio.run(run())


def test_phase3_idea_fusion_lifecycle():
    """Verify Idea Fusion proposal generation, retrieval of real records, and approval."""
    async def run():
        await init_db()

        async with get_db_context() as session:
            # Create a dedicated workspace
            user = User(email=f"fusion-qa-{uuid.uuid4().hex[:6]}@ideaos.test", name="Fusion QA")
            session.add(user)
            await session.flush()

            ws = Workspace(name="Fusion QA Studio", slug=f"fusion-qa-{uuid.uuid4().hex[:6]}", owner_id=user.id)
            session.add(ws)
            await session.flush()

            session.add(WorkspaceMember(workspace_id=ws.id, user_id=user.id, role="owner"))

            # Create 2 distinct ideas
            idea1 = Idea(
                workspace_id=ws.id,
                title="Mobile Authenticity in B2B Media",
                summary="Over-engineered studio video creates psychological defense barriers.",
                original_thought="Raw handheld clips get 43% higher comment velocity.",
                main_topic="Video Production",
                content_pillar="Distribution",
                suggested_formats=["post"],
                suggested_platforms=["linkedin"],
                status="active",
            )
            idea2 = Idea(
                workspace_id=ws.id,
                title="Micro-Cohort ARR Compounding",
                summary="Niche cohorts of 3,000 operators generate more revenue than 100k passive subscribers.",
                original_thought="Vanity metrics don't convert to pipeline.",
                main_topic="Monetization",
                content_pillar="Audience Economics",
                suggested_formats=["thread"],
                suggested_platforms=["twitter"],
                status="active",
            )
            session.add(idea1)
            session.add(idea2)
            await session.commit()
            idea1_id = idea1.id
            ws_id = ws.id

        # Pass X-Workspace-Id to ensure exact workspace scoping
        headers = {"X-Workspace-Id": str(ws_id)}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Request fusion proposal for idea1
            suggest_resp = await client.post(
                "/api/v1/fusion/suggest",
                json={"idea_id": str(idea1_id), "max_candidates": 5},
                headers=headers,
            )
            assert suggest_resp.status_code == 200, suggest_resp.text
            proposals = suggest_resp.json()
            assert len(proposals) > 0

            target_prop = proposals[0]
            proposal_id = target_prop["id"]
            assert "source_idea_ids" in target_prop
            assert len(target_prop["source_idea_ids"]) >= 2
            assert "fusion_concept" in target_prop
            assert len(target_prop["content_opportunities"]) > 0

            # Approve the proposal
            approve_resp = await client.post(
                f"/api/v1/fusion/{proposal_id}/approve",
                json={"create_master_idea": True, "master_idea_title": "Master Synthesis: Lo-Fi B2B Leverage"},
                headers=headers,
            )
            assert approve_resp.status_code == 200, approve_resp.text
            approve_data = approve_resp.json()
            assert approve_data["status"] == "approved"
            assert "new_idea_id" in approve_data

            # Verify invalid proposal rejection does not return 200
            fake_id = str(uuid.uuid4())
            invalid_resp = await client.post(
                f"/api/v1/fusion/{fake_id}/approve",
                json={"create_master_idea": True},
                headers=headers,
            )
            assert invalid_resp.status_code == 404, "Invalid proposal approval must return 404"

        # Verify database record updated
        async with get_db_context() as verify_session:
            p_res = await verify_session.execute(
                select(FusionProposal).where(FusionProposal.id == uuid.UUID(proposal_id))
            )
            saved_p = p_res.scalar_one_or_none()
            assert saved_p is not None
            assert saved_p.status == "approved"
            assert saved_p.new_idea_id is not None

    asyncio.run(run())


def test_phase4_media_repurpose_workflow():
    """Verify controlled transcript ingestion, topic segmenting, clip explanation, and multi-platform drafts."""
    async def run():
        await init_db()

        test_transcript = (
            "Speaker A [00:00]: Today on the Creator Operating System, we analyze attention mechanics. "
            "Speaker B [01:10]: The counter-intuitive finding across 5 million views is that high-end studio polish "
            "causes a 400ms defense barrier. When prospective buyers see cinematic ads, they scroll away. "
            "Speaker A [04:15]: So raw vulnerability and direct lens contact outperforms $20,000 production sets? "
            "Speaker B [04:30]: Exactly. Mirror neurons activate in 200ms on authentic human gaze. "
            "Speaker A [12:00]: Let's discuss micro-cohort economics. 3,000 operators yield 5x ARR compared to 100k passive followers."
        )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Ingest
            ingest_res = await client.post(
                "/api/v1/repurpose/ingest",
                json={
                    "title": "QA Test Podcast: Attention Mechanics",
                    "content": test_transcript,
                    "media_type": "podcast",
                    "content_pillar": "Creator Economics",
                },
            )
            assert ingest_res.status_code == 201, ingest_res.text
            ingest_data = ingest_res.json()

            # 2. Verify segments and timestamps
            assert len(ingest_data["segments"]) >= 2
            for seg in ingest_data["segments"]:
                assert seg["start_time"] >= 0
                assert seg["end_time"] > seg["start_time"]
                assert seg["speaker"]

            # 3. Verify clip explanations
            clips = ingest_data["clip_opportunities"]
            assert len(clips) >= 1
            clip = clips[0]
            assert "selection_reason" in clip
            assert len(clip["selection_reason"]) > 15
            assert "viral_potential" in clip

            # 4. Generate multi-platform drafts
            for plat in ["linkedin", "twitter"]:
                gen_res = await client.post(
                    "/api/v1/repurpose/generate",
                    json={
                        "idea_id": ingest_data["idea_id"],
                        "clip_title": clip["title"],
                        "key_quote": clip["key_quote"],
                        "selection_reason": clip["selection_reason"],
                        "start_time": clip["start_time"],
                        "end_time": clip["end_time"],
                        "platform": plat,
                        "format": "thread" if plat == "twitter" else "post",
                    },
                )
                assert gen_res.status_code == 200, gen_res.text
                gen_data = gen_res.json()
                assert gen_data["hook"]
                assert gen_data["body"]
                assert gen_data["quality_score"] >= 5.0

    asyncio.run(run())


def test_phase5_brand_memory_and_learning_loop():
    """Verify that editing AI drafts extracts brand rules and persists them into Brand Memory."""
    async def run():
        await init_db()

        original_draft = (
            "In this fast-paced digital era, we delve deep into why creators must unlock synergistic content. "
            "Furthermore, it is a testament to the power of video marketing."
        )
        creator_edited = (
            "4M views showed that 4K studio productions generated 43% lower comment velocity than raw smartphone clips. "
            "Authenticity is an algorithmic distribution moat."
        )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            edit_res = await client.post(
                "/api/v1/repurpose/edit-and-approve",
                json={
                    "idea_id": str(uuid.uuid4()),
                    "platform": "linkedin",
                    "format": "post",
                    "original_content": original_draft,
                    "edited_content": creator_edited,
                    "title": "Attention Moat Post",
                    "schedule_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                },
            )
            assert edit_res.status_code == 200, edit_res.text
            edit_data = edit_res.json()
            assert edit_data["status"] in ["approved", "scheduled"]
            assert "content_output_id" in edit_data

            # Verify brand rules were extracted
            learned = edit_data["learned_brand_rules"]
            assert len(learned) > 0, "Brand memory must extract rules from creator edits"

            # Verify rules are retrievable via GET /api/v1/brand/rules
            rules_res = await client.get("/api/v1/brand/rules")
            assert rules_res.status_code == 200, rules_res.text
            rules_data = rules_res.json()
            assert len(rules_data["data"]) > 0

    asyncio.run(run())


def test_phase6_calendar_and_performance_feedback():
    """Verify calendar scheduling and performance metrics recording into closed-loop feedback."""
    async def run():
        await init_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Create and approve real content to produce a real content_output_id
            approval_res = await client.post(
                "/api/v1/repurpose/edit-and-approve",
                json={
                    "idea_id": str(uuid.uuid4()),
                    "platform": "linkedin",
                    "format": "post",
                    "original_content": "Draft content for real calendar scheduling.",
                    "edited_content": "Final approved content ready for LinkedIn publishing pipeline.",
                    "title": "Real Scheduled Post",
                    "schedule_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
                },
            )
            assert approval_res.status_code == 200, approval_res.text
            appr_data = approval_res.json()
            real_content_output_id = appr_data["content_output_id"]
            cal_item_id = appr_data.get("calendar_item_id")
            assert cal_item_id is not None

            # 2. Verify calendar endpoint lists this real scheduled item
            cal_res = await client.get("/api/v1/calendar")
            assert cal_res.status_code == 200, cal_res.text
            cal_data = cal_res.json()
            matching = [item for item in cal_data["data"] if item["id"] == cal_item_id]
            assert len(matching) == 1
            assert matching[0]["platform"] == "linkedin"
            assert matching[0]["status"] == "scheduled"

            # 3. Submit real performance metrics against the real content_output_id
            perf_payload = {
                "content_output_id": real_content_output_id,
                "views": 48200,
                "likes": 3120,
                "shares": 450,
                "comments": 290,
                "retention_rate": 72.5,
            }
            perf_res = await client.post("/api/v1/repurpose/performance", json=perf_payload)
            assert perf_res.status_code == 200, perf_res.text
            perf_data = perf_res.json()
            assert perf_data["status"] == "recorded"
            assert "performance_score" in perf_data
            assert "recommendation_impact" in perf_data

        # 4. Verify database record is persisted in feedback_events table across session close
        async with get_db_context() as session:
            f_res = await session.execute(
                select(FeedbackEvent).where(
                    FeedbackEvent.entity_id == uuid.UUID(real_content_output_id),
                    FeedbackEvent.action == "performance_logged",
                )
            )
            feedback = f_res.scalar_one_or_none()
            assert feedback is not None, "Feedback event must be persisted in database"
            assert feedback.after_state["views"] == 48200
            assert feedback.after_state["likes"] == 3120

    asyncio.run(run())
