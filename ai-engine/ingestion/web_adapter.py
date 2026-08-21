from __future__ import annotations
from pathlib import Path
from typing import Optional
import trafilatura
import httpx

from ingestion.base import SourceAdapter
from schemas.canonical import (
    CanonicalSource,
    RightsRecord,
    Segment,
    SourceMetadata,
    SourceRef,
)


class WebAdapter(SourceAdapter):
    """Adapter for Web URLs and raw HTML documents using trafilatura."""

    def parse(
        self,
        file_path_or_content: str | Path,
        title: str,
        story_id: str,
        language: str = "en",
        author: Optional[str] = None,
        rights: Optional[RightsRecord] = None,
    ) -> CanonicalSource:
        url_or_str = str(file_path_or_content)
        downloaded_html = ""
        source_url = None

        if url_or_str.startswith(("http://", "https://")):
            source_url = url_or_str
            resp = httpx.get(url_or_str, timeout=30.0, follow_redirects=True)
            resp.raise_for_status()
            downloaded_html = resp.text
        elif Path(url_or_str).exists():
            downloaded_html = Path(url_or_str).read_text(encoding="utf-8", errors="replace")
        else:
            downloaded_html = url_or_str

        extracted_text = trafilatura.extract(
            downloaded_html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        ) or ""

        checksum = self.calculate_sha256(extracted_text)

        # Split into segments
        paragraphs = [p.strip() for p in extracted_text.split("\n\n") if p.strip()]
        segments: list[Segment] = []
        seq = 1

        for p_idx, para in enumerate(paragraphs):
            clean_para = " ".join(para.split())
            if len(clean_para) < 10:
                continue

            segments.append(
                Segment(
                    id=f"seg_{seq:04d}",
                    sequence=seq,
                    chapter="Web Article",
                    text=clean_para,
                    source_ref=SourceRef(
                        url=source_url,
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
                type="web",
                title=title,
                author=author,
                language=language,
                checksum_sha256=checksum,
                original_filename=source_url or "web_content.html",
                rights=rights or RightsRecord(),
            ),
            segments=segments,
            total_characters=total_chars,
            total_words=total_words,
        )
