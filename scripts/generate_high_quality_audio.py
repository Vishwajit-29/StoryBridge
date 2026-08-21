import asyncio
import json
import sys
from pathlib import Path

# Setup paths and UTF-8 output
root_dir = Path(__file__).resolve().parent.parent
ai_engine_dir = root_dir / "ai-engine"
sys.path.insert(0, str(ai_engine_dir))

if sys.platform == "win32":
    import io
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from providers.tts import EdgeTTSProvider, clean_storytelling_text

async def regenerate_all_audio():
    print("=" * 60)
    print("StoryBridge: Synthesizing Studio-Grade Audio with SSML Pauses")
    print("=" * 60)

    tts = EdgeTTSProvider()
    artifacts_dir = root_dir / "storage" / "artifacts"
    story_dirs = [d for d in artifacts_dir.iterdir() if d.is_dir()]

    if not story_dirs:
        print("No story artifact directories found in storage/artifacts.")
        return

    for story_dir in story_dirs:
        story_id = story_dir.name
        print(f"\nProcessing Story: {story_id}")

        loc_dir = story_dir / "localization"
        if not loc_dir.exists():
            continue

        for lang_dir in loc_dir.iterdir():
            if not lang_dir.is_dir():
                continue
            lang = lang_dir.name

            for preset_dir in lang_dir.iterdir():
                if not preset_dir.is_dir():
                    continue
                preset = preset_dir.name
                script_file = preset_dir / "script.json"

                if not script_file.exists():
                    continue

                try:
                    script_data = json.loads(script_file.read_text(encoding="utf-8"))
                except Exception as e:
                    print(f"Error reading {script_file}: {e}")
                    continue

                chapters = script_data.get("chapters", [])
                audio_out_dir = story_dir / "audio" / lang / preset
                audio_out_dir.mkdir(parents=True, exist_ok=True)

                print(f"  -> Synthesizing [{lang}] [{preset}] ({len(chapters)} chapters)...")
                chapter_audio_records = []
                total_duration = 0.0

                for idx, ch in enumerate(chapters, 1):
                    ch_filename = f"ch{idx:02d}.mp3"
                    ch_audio_path = audio_out_dir / ch_filename
                    title = ch.get("title", f"Chapter {idx}")
                    content = ch.get("content", "")
                    narration_text = f"{title}.\n\n{content}"

                    print(f"     Chapter {idx}: {title}...")
                    dur = await tts.synthesize(
                        text=narration_text,
                        output_path=ch_audio_path,
                        language=lang,
                    )
                    file_size = ch_audio_path.stat().st_size
                    print(f"     -> Generated {ch_filename}: {file_size} bytes, ~{dur:.1f}s")

                    chapter_audio_records.append({
                        "chapter_id": ch.get("chapter_id", f"ch_{idx:02d}"),
                        "chapter_number": idx,
                        "title": title,
                        "audio_file": ch_filename,
                        "storage_path": str(ch_audio_path.relative_to(root_dir)).replace("\\", "/"),
                        "duration_seconds": dur,
                        "file_size_bytes": file_size,
                    })
                    total_duration += dur

                # Save asset metadata
                metadata = {
                    "story_id": story_id,
                    "language_code": lang,
                    "duration_preset": preset,
                    "voice_id": tts.VOICE_MAP.get(lang, "en-IN-NeerjaNeural"),
                    "total_duration_seconds": total_duration,
                    "chapters": chapter_audio_records,
                }
                (audio_out_dir / "asset_metadata.json").write_text(
                    json.dumps(metadata, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                print(f"  ✓ Saved audio metadata to {audio_out_dir / 'asset_metadata.json'}")

    print("\n" + "=" * 60)
    print("All Story Audio Assets Synthesized Successfully with Real Neural Voices!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(regenerate_all_audio())
