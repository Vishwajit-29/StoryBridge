from __future__ import annotations
from pathlib import Path
from typing import Optional
import pysrt
import webvtt

from ingestion.base import SourceAdapter
from schemas.canonical import (
    CanonicalSource,
    RightsRecord,
    Segment,
    SourceMetadata,
    SourceRef,
)


class SubtitleAdapter(SourceAdapter):
    """Adapter for Subtitle files (.srt, .vtt) with timestamp preservation and merging."""

    def parse(
        self,
        file_path_or_content: str | Path,
        title: str,
        story_id: str,
        language: str = "en",
        author: Optional[str] = None,
        rights: Optional[RightsRecord] = None,
    ) -> CanonicalSource:
        path = Path(file_path_or_content)
        if not path.exists():
            raise FileNotFoundError(f"Subtitle file not found: {path}")

        raw_bytes = path.read_bytes()
        checksum = self.calculate_sha256(raw_bytes)
        ext = path.suffix.lower()

        segments: list[Segment] = []
        seq = 1

        if ext == ".vtt":
            vtt = webvtt.read(str(path))
            # Merge close consecutive subtitles into coherent chunks (approx 20-30s blocks or sentence boundaries)
            current_texts: list[str] = []
            chunk_start_ms = 0
            chunk_end_ms = 0

            def vtt_time_to_ms(t_str: str) -> int:
                parts = t_str.split(":")
                if len(parts) == 3:
                    h, m, s_ms = parts
                    s, ms = s_ms.split(".")
                    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
                elif len(parts) == 2:
                    m, s_ms = parts
                    s, ms = s_ms.split(".")
                    return int(m) * 60000 + int(s) * 1000 + int(ms)
                return 0

            for caption in vtt:
                text = " ".join(caption.text.split())
                start_ms = vtt_time_to_ms(caption.start)
                end_ms = vtt_time_to_ms(caption.end)

                if not current_texts:
                    chunk_start_ms = start_ms

                current_texts.append(text)
                chunk_end_ms = end_ms

                # Flush when chunk reaches ~25 seconds or sentence ends
                if (chunk_end_ms - chunk_start_ms >= 25000) or text.endswith((".", "!", "?")):
                    combined = " ".join(current_texts)
                    segments.append(
                        Segment(
                            id=f"seg_{seq:04d}",
                            sequence=seq,
                            start_ms=chunk_start_ms,
                            end_ms=chunk_end_ms,
                            text=combined,
                            source_ref=SourceRef(timestamp_ms=chunk_start_ms),
                        )
                    )
                    seq += 1
                    current_texts = []

            if current_texts:
                segments.append(
                    Segment(
                        id=f"seg_{seq:04d}",
                        sequence=seq,
                        start_ms=chunk_start_ms,
                        end_ms=chunk_end_ms,
                        text=" ".join(current_texts),
                        source_ref=SourceRef(timestamp_ms=chunk_start_ms),
                    )
                )

        else:  # .srt
            subs = pysrt.open(str(path), encoding="utf-8")
            current_texts = []
            chunk_start_ms = 0
            chunk_end_ms = 0

            for sub in subs:
                text = " ".join(sub.text.split())
                start_ms = sub.start.ordinal
                end_ms = sub.end.ordinal

                if not current_texts:
                    chunk_start_ms = start_ms

                current_texts.append(text)
                chunk_end_ms = end_ms

                if (chunk_end_ms - chunk_start_ms >= 25000) or text.endswith((".", "!", "?")):
                    combined = " ".join(current_texts)
                    segments.append(
                        Segment(
                            id=f"seg_{seq:04d}",
                            sequence=seq,
                            start_ms=chunk_start_ms,
                            end_ms=chunk_end_ms,
                            text=combined,
                            source_ref=SourceRef(timestamp_ms=chunk_start_ms),
                        )
                    )
                    seq += 1
                    current_texts = []

            if current_texts:
                segments.append(
                    Segment(
                        id=f"seg_{seq:04d}",
                        sequence=seq,
                        start_ms=chunk_start_ms,
                        end_ms=chunk_end_ms,
                        text=" ".join(current_texts),
                        source_ref=SourceRef(timestamp_ms=chunk_start_ms),
                    )
                )

        total_chars = sum(len(s.text) for s in segments)
        total_words = sum(len(s.text.split()) for s in segments)

        return CanonicalSource(
            source=SourceMetadata(
                id=story_id,
                type="subtitle",
                title=title,
                author=author,
                language=language,
                checksum_sha256=checksum,
                original_filename=path.name,
                rights=rights or RightsRecord(),
            ),
            segments=segments,
            total_characters=total_chars,
            total_words=total_words,
        )
