from __future__ import annotations
from pathlib import Path
from typing import Optional
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from ingestion.base import SourceAdapter
from schemas.canonical import (
    CanonicalSource,
    RightsRecord,
    Segment,
    SourceMetadata,
    SourceRef,
)


class EPUBAdapter(SourceAdapter):
    """Adapter for EPUB books preserving chapter hierarchy."""

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
            raise FileNotFoundError(f"EPUB file not found: {path}")

        raw_bytes = path.read_bytes()
        checksum = self.calculate_sha256(raw_bytes)

        book = epub.read_epub(str(path))
        extracted_author = author
        if not extracted_author:
            creator_meta = book.get_metadata("DC", "creator")
            if creator_meta:
                extracted_author = creator_meta[0][0]

        segments: list[Segment] = []
        seq = 1

        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            
            # Identify chapter heading if present
            heading_elem = soup.find(["h1", "h2", "h3"])
            chapter_title = heading_elem.get_text().strip() if heading_elem else f"Section {seq}"

            # Extract paragraphs
            paragraphs = soup.find_all("p")
            if not paragraphs:
                # If no <p> tags, extract whole body text
                body_text = soup.get_text().strip()
                if body_text:
                    paragraphs = [soup]

            for p_idx, p in enumerate(paragraphs):
                text = " ".join(p.get_text().split())
                if len(text) < 10:
                    continue

                segments.append(
                    Segment(
                        id=f"seg_{seq:04d}",
                        sequence=seq,
                        chapter=chapter_title,
                        text=text,
                        source_ref=SourceRef(
                            chapter=chapter_title,
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
                type="epub",
                title=title,
                author=extracted_author,
                language=language,
                checksum_sha256=checksum,
                original_filename=path.name,
                rights=rights or RightsRecord(),
            ),
            segments=segments,
            total_characters=total_chars,
            total_words=total_words,
        )
