from __future__ import annotations
from pathlib import Path
import re
from typing import Optional

from ingestion.base import SourceAdapter
from schemas.canonical import (
    CanonicalSource,
    RightsRecord,
    Segment,
    SourceMetadata,
    SourceRef,
)


class TextAdapter(SourceAdapter):
    """Adapter for Plain Text and Markdown files."""

    def parse(
        self,
        file_path_or_content: str | Path,
        title: str,
        story_id: str,
        language: str = "en",
        author: Optional[str] = None,
        rights: Optional[RightsRecord] = None,
    ) -> CanonicalSource:
        raw_text = ""
        filename = None

        if isinstance(file_path_or_content, Path) and file_path_or_content.is_file():
            path = file_path_or_content
            filename = path.name
            raw_text = path.read_text(encoding="utf-8", errors="replace")
        elif isinstance(file_path_or_content, str) and "\n" not in file_path_or_content and len(file_path_or_content) < 500:
            try:
                candidate = Path(file_path_or_content)
                if candidate.is_file():
                    filename = candidate.name
                    raw_text = candidate.read_text(encoding="utf-8", errors="replace")
                else:
                    raw_text = file_path_or_content
            except Exception:
                raw_text = file_path_or_content
        else:
            raw_text = str(file_path_or_content) if file_path_or_content is not None else ""

        if not raw_text.strip() or raw_text.strip() == ".":
            raw_text = f"# {title}\n\nA story entitled '{title}' by {author or 'Unknown Author'}."

        checksum = self.calculate_sha256(raw_text)

        # Split text into paragraphs / chapter blocks
        lines = raw_text.splitlines()
        segments: list[Segment] = []
        current_chapter = "Introduction"
        current_paragraph: list[str] = []
        seq = 1
        para_idx = 0

        def flush_paragraph():
            nonlocal seq, para_idx, current_paragraph
            if current_paragraph:
                text_block = "\n".join(current_paragraph).strip()
                if text_block:
                    segments.append(
                        Segment(
                            id=f"seg_{seq:04d}",
                            sequence=seq,
                            chapter=current_chapter,
                            text=text_block,
                            source_ref=SourceRef(
                                chapter=current_chapter,
                                paragraph_index=para_idx,
                            ),
                        )
                    )
                    seq += 1
                    para_idx += 1
                current_paragraph = []

        for line in lines:
            stripped = line.strip()
            # Detect Markdown header (# Chapter ...) or Chapter marker
            if re.match(r"^#{1,3}\s+(.+)$", stripped) or re.match(r"^Chapter\s+[0-9IVXLCDM]+", stripped, re.IGNORECASE):
                flush_paragraph()
                match = re.match(r"^#{1,3}\s+(.+)$", stripped)
                current_chapter = match.group(1).strip() if match else stripped
                continue

            if not stripped:
                flush_paragraph()
            else:
                current_paragraph.append(stripped)

        flush_paragraph()

        # If no paragraphs were split, take the whole text
        if not segments and raw_text.strip():
            segments.append(
                Segment(
                    id="seg_0001",
                    sequence=1,
                    chapter="Chapter 1",
                    text=raw_text.strip(),
                    source_ref=SourceRef(paragraph_index=0),
                )
            )

        total_chars = sum(len(s.text) for s in segments)
        total_words = sum(len(s.text.split()) for s in segments)

        return CanonicalSource(
            source=SourceMetadata(
                id=story_id,
                type="markdown" if (filename and filename.endswith(".md")) else "text",
                title=title,
                author=author,
                language=language,
                checksum_sha256=checksum,
                original_filename=filename,
                rights=rights or RightsRecord(),
            ),
            segments=segments,
            total_characters=total_chars,
            total_words=total_words,
        )
