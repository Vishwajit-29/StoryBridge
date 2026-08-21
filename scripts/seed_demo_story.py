#!/usr/bin/env python3
"""
StoryBridge Seed Script:
Runs a sample public-domain story (The Monkey and the Wedge) through the StoryBridge pipeline
and generates canonical artifacts (Story Graph, Narratives, Hindi & Marathi localizations, and TTS audio).
"""

import asyncio
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add ai-engine to path
root_dir = Path(__file__).resolve().parent.parent
ai_engine_dir = root_dir / "ai-engine"
sys.path.insert(0, str(ai_engine_dir))

from config import settings
from pipeline import StoryBridgePipeline
from providers.llm import NvidiaNimProvider, MockLLMProvider
from providers.tts import EdgeTTSProvider, MockTTSProvider
from schemas.canonical import RightsRecord, RightsType


async def main():
    print("=" * 60)
    print("StoryBridge: Seeding Sample Public Domain Story")
    print("=" * 60)

    # Check if NVIDIA NIM API key is present
    has_nim_key = bool(
        settings.NVIDIA_API_KEY
        and settings.NVIDIA_API_KEY != "your_nvidia_nim_api_key_here"
    )

    if has_nim_key:
        print(f"[AI] Using NVIDIA NIM Provider with model: {settings.NIM_MODEL_NAME}")
        llm = NvidiaNimProvider()
    else:
        print("[AI] NVIDIA_API_KEY not configured yet in .env; using MockLLMProvider for demo structure.")
        llm = MockLLMProvider()

    # TTS provider (EdgeTTS or Mock)
    try:
        tts = EdgeTTSProvider()
    except Exception:
        tts = MockTTSProvider()

    storage_dir = root_dir / "storage" / "artifacts"
    pipeline = StoryBridgePipeline(
        llm_provider=llm,
        tts_provider=tts,
        storage_base_dir=storage_dir,
    )

    fixture_path = root_dir / "shared" / "fixtures" / "the_monkey_and_the_wedge.md"
    if not fixture_path.exists():
        print(f"Error: Fixture file not found at {fixture_path}")
        return

    story_id = "story_panchatantra_monkey_wedge"
    title = "The Monkey and the Wedge"
    author = "Vishnu Sharma (The Panchatantra)"

    rights = RightsRecord(
        type=RightsType.PUBLIC_DOMAIN,
        verified=True,
        evidence_url_or_note="Ancient Sanskrit fable in universal public domain (>2000 years old)",
        license_identifier="Public Domain / CC0",
    )

    print(f"\nProcessing '{title}' ({story_id})...")
    result = await pipeline.run_full_pipeline(
        source_path_or_content=fixture_path,
        title=title,
        story_id=story_id,
        author=author,
        rights=rights,
        duration_presets=["quick", "standard"],
        languages=["hi", "mr"],
    )

    print("\n" + "=" * 60)
    print(f"Demo Story Generation Completed Successfully!")
    print(f"Story Artifacts Saved to: {storage_dir / story_id}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
