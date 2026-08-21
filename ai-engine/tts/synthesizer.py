from __future__ import annotations
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from providers.tts import TTSProvider, get_tts_provider
from schemas.canonical import AudioAsset, AudioChapter, LocalizedScript


class ChapterAudioSynthesizer:
    """Synthesizes LocalizedScript into chapter-by-chapter audio files per SRS Section 14."""

    def __init__(self, tts_provider: Optional[TTSProvider] = None):
        self.tts = tts_provider or get_tts_provider()

    async def synthesize_script(
        self,
        script: LocalizedScript,
        output_dir: Path,
        voice_id: Optional[str] = None,
    ) -> AudioAsset:
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_chapters: List[AudioChapter] = []
        total_duration = 0.0

        for ch in script.chapters:
            filename = f"ch{ch.chapter_number:02d}.mp3"
            file_path = output_dir / filename

            # Narrate title + content
            narration_text = f"{ch.title}.\n\n{ch.content}"

            duration_sec = await self.tts.synthesize(
                text=narration_text,
                output_path=file_path,
                language=script.language,
                voice=voice_id,
            )

            file_size = file_path.stat().st_size if file_path.exists() else 0
            total_duration += duration_sec

            audio_chapters.append(
                AudioChapter(
                    chapter_id=ch.chapter_id,
                    chapter_number=ch.chapter_number,
                    title=ch.title,
                    audio_path=str(file_path),
                    audio_format="mp3",
                    duration_seconds=duration_sec,
                    file_size_bytes=file_size,
                )
            )

        return AudioAsset(
            story_id=script.story_id,
            language=script.language,
            duration_preset=script.duration_preset,
            voice_id=voice_id or "default",
            chapters=audio_chapters,
            total_duration_seconds=total_duration,
            created_at=datetime.utcnow().isoformat(),
        )
