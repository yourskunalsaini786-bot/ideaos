"""Tests for Idea Fusion differentiator."""
import asyncio
from httpx import ASGITransport, AsyncClient
from ideaos.main import app
from ideaos.core.database import init_db, close_db


def test_idea_fusion_lifecycle():
    async def run():
        await init_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Ingest Idea A
            resp_a = await client.post("/api/v1/repurpose/ingest", json={
                "title": "Audio Deep Work Strategy",
                "content": "Long podcast session exploring how uninterrupted creative sessions lead to exponential leverage for software engineers.",
                "media_type": "podcast"
            })
            assert resp_a.status_code == 201
            idea_a_id = resp_a.json()["idea_id"]

            # 2. Ingest Idea B
            resp_b = await client.post("/api/v1/repurpose/ingest", json={
                "title": "AI Agent Orchestration",
                "content": "Discussion on how multi-agent durable workflows replace human coordination bottlenecks in modern studios.",
                "media_type": "podcast"
            })
            assert resp_b.status_code == 201
            idea_b_id = resp_b.json()["idea_id"]

            # 3. Request Fusion suggestions for Idea B connecting to existing ideas
            fusion_resp = await client.post("/api/v1/fusion/suggest", json={
                "idea_id": idea_b_id,
                "max_candidates": 5,
                "min_confidence": 0.5
            })
            assert fusion_resp.status_code == 200, fusion_resp.text
            proposals = fusion_resp.json()
            assert isinstance(proposals, list)
            assert len(proposals) > 0
            first_proposal = proposals[0]
            assert "fusion_concept" in first_proposal
            assert "confidence" in first_proposal
            assert len(first_proposal["content_opportunities"]) > 0
            proposal_id = first_proposal["id"]
            print("\n[VERIFIED FUSION PROPOSAL]:", first_proposal["fusion_concept"])

            # 4. Approve Fusion Proposal into a Master Idea
            approve_resp = await client.post(f"/api/v1/fusion/{proposal_id}/approve", json={
                "create_master_idea": True,
                "master_idea_title": "Master Synthesis: Deep Work via Autonomous Agent Teams"
            })
            assert approve_resp.status_code == 200, approve_resp.text
            approved_data = approve_resp.json()
            assert approved_data["status"] == "approved"
            print("[VERIFIED FUSION APPROVAL]: Proposal approved into master idea.")

        await close_db()

    asyncio.run(run())
