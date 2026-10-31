"""Tests for AI Service capabilities (transcription, clips, platform copy, brand memory)."""
import asyncio
from ideaos.services.ai_service import ai_service


def test_transcribe_and_segment():
    async def run():
        raw_podcast = """
        Welcome to episode 42 of the Founder Journey. Today we discuss the core problem in modern content creation.
        Most creators spend 40 hours a week recording high-value interviews, but their repurposing strategy is completely broken.
        They hand off the episode to an agency that extracts random 30-second clips with no context and no hook.
        The result is low reach, disconnected ideas, and brand drift.
        What you need is an intelligent repurposing studio with persistent brand memory.
        """
        result = await ai_service.transcribe_and_segment(raw_podcast)
        assert "title" in result
        assert "summary" in result
        assert "segments" in result
        assert len(result["segments"]) > 0
        seg = result["segments"][0]
        assert "start_time" in seg
        assert "end_time" in seg
        assert "speaker" in seg

    asyncio.run(run())


def test_extract_clip_opportunities_with_explanations():
    async def run():
        sample_transcript = {
            "title": "Podcast Episode 42",
            "segments": [
                {
                    "start_time": 10.0,
                    "end_time": 68.0,
                    "text": "The single biggest bottleneck in content repurposing is losing the authentic brand voice.",
                },
                {
                    "start_time": 75.0,
                    "end_time": 140.0,
                    "text": "If a clip cannot stand on its own without requiring 5 minutes of backstory, it will never go viral on LinkedIn or Reels.",
                }
            ]
        }
        clips = await ai_service.extract_clip_opportunities(sample_transcript, min_clips=2)
        assert isinstance(clips, list)
        assert len(clips) >= 2
        for clip in clips:
            assert "title" in clip
            assert "start_time" in clip
            assert "end_time" in clip
            assert "hook_strength" in clip
            assert "selection_reason" in clip
            # Mandatory requirement: explicit explanation for why clip was selected
            assert len(clip["selection_reason"]) > 10

    asyncio.run(run())


def test_generate_platform_content():
    async def run():
        clip = {
            "title": "Brand Voice Bottleneck",
            "key_quote": "Most creators lose their voice when repurposing.",
            "selection_reason": "High contrarian hook with immediate actionable resolution.",
        }
        brand_profile = {
            "voice_description": "Direct, punchy, tactical advice for creators.",
            "target_audience": "B2B SaaS Founders",
        }
        brand_rules = [
            {
                "rule_type": "must_avoid",
                "pattern": "synergy",
                "message": "Do not use corporate jargon like synergy",
                "is_active": True,
            }
        ]

        linkedin_content = await ai_service.generate_platform_content(
            clip_data=clip,
            platform="linkedin",
            format_type="post",
            brand_profile=brand_profile,
            brand_rules=brand_rules,
        )
        assert "body" in linkedin_content
        assert "quality_score" in linkedin_content
        assert linkedin_content["quality_passed"] is True
        assert len(linkedin_content["hashtags"]) > 0

    asyncio.run(run())


def test_learn_brand_rules_from_edit():
    async def run():
        original = "In order to maximize your content synergy, we should leverage AI tools."
        edited = "To get 10x content leverage, use smart AI workflows."
        rules = await ai_service.learn_brand_rules_from_edit(
            original_content=original,
            edited_content=edited,
            platform="linkedin",
        )
        assert isinstance(rules, list)
        assert len(rules) > 0
        rule = rules[0]
        assert "rule_type" in rule
        assert "message" in rule
        assert "applies_to" in rule

    asyncio.run(run())


def test_transcribe_audio_bytes():
    async def run():
        # Test audio bytes transcription pipeline
        dummy_audio = b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f\x00\x00\x01\xff\xfeL\x00a\x00v\x00f\x005\x008\x00.\x002\x009\x00.\x001\x000\x000\x00"
        result = await ai_service.transcribe_audio_bytes(dummy_audio, mime_type="audio/mp3", filename="test_episode.mp3")
        assert "title" in result
        assert "summary" in result
        assert "segments" in result
        assert len(result["segments"]) > 0
        seg = result["segments"][0]
        assert "start_time" in seg
        assert "end_time" in seg
        assert "speaker" in seg

    asyncio.run(run())
