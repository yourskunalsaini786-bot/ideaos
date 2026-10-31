"""Comprehensive End-to-End Test for the 9-Step Repurposing & Brand Memory Workflow.

Mandatory Hackathon Steps Tested:
1. Long video or podcast ingestion.
2. Transcription and timestamp extraction.
3. Intelligent clip selection.
4. Explanations for every clip recommendation.
5. Platform-specific content generation.
6. Brand memory and Brand Guardian quality check.
7. Creator edits and approval.
8. Addition of approved outputs to content calendar.
9. Performance feedback loop recording.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from httpx import ASGITransport, AsyncClient
from ideaos.main import app
from ideaos.core.database import init_db, close_db


def test_complete_end_to_end_workflow():
    async def run():
        await init_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Step 1: Upload a long-form podcast transcript
            raw_podcast_content = (
                "Welcome to Episode 10 of IdeaOS Unlocked. Today's deep dive is on AI content workflows. "
                "The biggest misconception creators have is thinking that more volume equals more leverage. "
                "In reality, blasting 50 generic clips across TikTok and Reels destroys your personal brand equity. "
                "Top creators identify the single contrarian insight with standalone narrative punch. "
                "When you capture that specific 45-second moment and adapt it cleanly for LinkedIn and Instagram, "
                "your engagement triples because you preserve authentic brand voice instead of generic fluff. "
                "Persistent brand memory ensures that every edit you make trains future generations."
            )

            ingest_payload = {
                "title": "IdeaOS Unlocked: Episode 10 - Content Leverage",
                "content": raw_podcast_content,
                "media_type": "podcast",
                "content_pillar": "Creator Strategy"
            }

            # Steps 1, 2, 3, 4: Ingest, Transcribe, Extract Clips with Explanations
            ingest_resp = await client.post("/api/v1/repurpose/ingest", json=ingest_payload)
            assert ingest_resp.status_code == 201, ingest_resp.text
            ingest_data = ingest_resp.json()

            # Verify Step 2: Timestamped segments extracted
            assert "capture_id" in ingest_data
            assert "idea_id" in ingest_data
            assert len(ingest_data["segments"]) > 0
            for seg in ingest_data["segments"]:
                assert "start_time" in seg
                assert "end_time" in seg
                assert "speaker" in seg

            # Verify Steps 3 & 4: Clip opportunities with explicit rationale
            clips = ingest_data["clip_opportunities"]
            assert len(clips) >= 2
            selected_clip = clips[0]
            assert "start_time" in selected_clip
            assert "end_time" in selected_clip
            assert "selection_reason" in selected_clip
            assert len(selected_clip["selection_reason"]) > 20
            print("\n[VERIFIED] Clip Selected with Rationale:", selected_clip["selection_reason"])

            # Step 5 & 6: Generate platform-specific content with persistent brand memory
            gen_payload = {
                "idea_id": ingest_data["idea_id"],
                "clip_title": selected_clip["title"],
                "key_quote": selected_clip.get("key_quote", "More volume destroys brand equity."),
                "selection_reason": selected_clip["selection_reason"],
                "start_time": selected_clip["start_time"],
                "end_time": selected_clip["end_time"],
                "platform": "linkedin_post",
                "format": "post"
            }
            gen_resp = await client.post("/api/v1/repurpose/generate", json=gen_payload)
            assert gen_resp.status_code == 200, gen_resp.text
            gen_data = gen_resp.json()
            assert "body" in gen_data
            assert "quality_passed" in gen_data
            assert gen_data["quality_score"] >= 7.0
            print("[VERIFIED] Generated Platform Copy Hook:", gen_data["hook"])

            # Step 7: Creator edits and approves content
            original_body = gen_data["body"]
            # Creator sharpens the wording to establish their brand preference
            edited_body = (
                original_body + "\n\nP.S. Always build in public and let your brand memory compound daily."
            )
            schedule_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

            approve_payload = {
                "idea_id": ingest_data["idea_id"],
                "platform": "linkedin_post",
                "format": "post",
                "original_content": original_body,
                "edited_content": edited_body,
                "title": gen_data["title"],
                "schedule_time": schedule_date
            }

            # Step 8: Edit, learn brand rules, and add to Content Calendar
            approve_resp = await client.post("/api/v1/repurpose/edit-and-approve", json=approve_payload)
            assert approve_resp.status_code == 200, approve_resp.text
            approve_data = approve_resp.json()
            assert "content_output_id" in approve_data
            assert approve_data["calendar_item_id"] is not None
            assert approve_data["status"] == "scheduled"
            # Verify brand memory rules were learned from creator edits
            learned_rules = approve_data["learned_brand_rules"]
            assert len(learned_rules) > 0
            print("[VERIFIED] Brand Rules Extracted from Edit:", learned_rules[0]["message"])

            # Verify calendar presence via calendar list API
            cal_resp = await client.get("/api/v1/calendar")
            assert cal_resp.status_code == 200
            cal_items = cal_resp.json()["data"]
            assert any(item["id"] == approve_data["calendar_item_id"] for item in cal_items)
            print("[VERIFIED] Content Output successfully scheduled on Calendar.")

            # Step 9: Performance feedback loop
            perf_payload = {
                "content_output_id": approve_data["content_output_id"],
                "views": 15420,
                "likes": 840,
                "shares": 190,
                "comments": 125,
                "retention_rate": 0.82
            }
            perf_resp = await client.post("/api/v1/repurpose/performance", json=perf_payload)
            assert perf_resp.status_code == 200, perf_resp.text
            perf_data = perf_resp.json()
            assert perf_data["status"] == "recorded"
            assert perf_data["performance_score"] > 0
            assert "recommendation_impact" in perf_data
            print(f"[VERIFIED] Performance Feedback Loop logged: Score {perf_data['performance_score']}/10")

        await close_db()

    asyncio.run(run())


def test_upload_media_audio_file():
    """Verify live multipart audio/video file upload and transcription."""
    async def run():
        await init_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            dummy_mp3 = b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f\x00\x00\x01\xff\xfeL\x00a\x00v\x00f\x005\x008\x00.\x002\x009\x00.\x001\x000\x000\x00"
            files = {"file": ("founder_masterclass.mp3", dummy_mp3, "audio/mp3")}
            data = {"title": "Live Upload Masterclass", "content_pillar": "Attention"}

            upload_resp = await client.post("/api/v1/repurpose/upload-media", files=files, data=data)
            assert upload_resp.status_code == 201, upload_resp.text
            ingest_data = upload_resp.json()

            assert "capture_id" in ingest_data
            assert "idea_id" in ingest_data
            assert len(ingest_data["segments"]) > 0
            assert len(ingest_data["clip_opportunities"]) > 0
            assert ingest_data["clip_opportunities"][0]["selection_reason"]
            print("\n[VERIFIED] Audio File Upload & Transcription:", ingest_data["title"])

        await close_db()

    asyncio.run(run())
