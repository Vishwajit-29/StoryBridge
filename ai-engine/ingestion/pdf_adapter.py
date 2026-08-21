from __future__ import annotations
from pathlib import Path
from typing import Optional
import pymupdf as fitz

from ingestion.base import SourceAdapter
from schemas.canonical import (
    CanonicalSource,
    RightsRecord,
    Segment,
    SourceMetadata,
    SourceRef,
)


class PDFAdapter(SourceAdapter):
    """Adapter for PDF documents using PyMuPDF."""

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
            raise FileNotFoundError(f"PDF file not found: {path}")

        raw_bytes = path.read_bytes()
        checksum = self.calculate_sha256(raw_bytes)

        doc = fitz.open(str(path))
        segments: list[Segment] = []
        seq = 1
        current_chapter = "Page 1"

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if not text:
                continue

            # Split page text into reasonable paragraph chunks
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for p_idx, para in enumerate(paragraphs):
                # Clean multiple internal newlines
                clean_para = " ".join(para.split())
                if len(clean_para) < 5:
                    continue

                segments.append(
                    Segment(
                        id=f"seg_{seq:04d}",
                        sequence=seq,
                        chapter=f"Page {page_num + 1}",
                        text=clean_para,
                        source_ref=SourceRef(
                            page=page_num + 1,
                            paragraph_index=p_idx,
                        ),
                    )
                )
                seq += 1

        total_chars = sum(len(s.text) for s in segments)
        total_words = sum(len(s.text.split()) for s in segments)

        return CanonicalSource(
            source=SourceMetadata(
                id=story_id,
                type="pdf",
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
