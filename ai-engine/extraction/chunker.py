from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field

from schemas.canonical import CanonicalSource, Segment


class StoryChunk(BaseModel):
    chunk_id: str
    chapter: str
    segment_ids: List[str] = Field(default_factory=list)
    combined_text: str
    word_count: int


class StoryChunker:
    """
    Splits CanonicalSource into manageable semantic chunks for LLM processing,
    preserving chapter boundaries and segment provenance.
    """

    def __init__(self, target_chunk_words: int = 1200, overlap_words: int = 150):
        self.target_chunk_words = target_chunk_words
        self.overlap_words = overlap_words

    def chunk(self, source: CanonicalSource) -> List[StoryChunk]:
        chunks: List[StoryChunk] = []
        
        # Group segments by chapter if present, else process linearly
        chapter_groups: dict[str, list[Segment]] = {}
        for seg in source.segments:
            ch_name = seg.chapter or "Default Chapter"
            if ch_name not in chapter_groups:
                chapter_groups[ch_name] = []
            chapter_groups[ch_name].append(seg)

        chunk_idx = 1
        for ch_name, segs in chapter_groups.items():
            current_segs: list[Segment] = []
            current_words = 0

            for seg in segs:
                seg_words = len(seg.text.split())
                if current_words + seg_words > self.target_chunk_words and current_segs:
                    # Form chunk
                    chunk_text = "\n\n".join(s.text for s in current_segs)
                    chunks.append(
                        StoryChunk(
                            chunk_id=f"chunk_{chunk_idx:03d}",
                            chapter=ch_name,
                            segment_ids=[s.id for s in current_segs],
                            combined_text=chunk_text,
                            word_count=len(chunk_text.split()),
                        )
                    )
                    chunk_idx += 1
                    
                    # Prepare next chunk with overlap if needed
                    current_segs = [current_segs[-1]] if len(current_segs) > 1 else []
                    current_words = sum(len(s.text.split()) for s in current_segs)

                current_segs.append(seg)
                current_words += seg_words

            if current_segs:
                chunk_text = "\n\n".join(s.text for s in current_segs)
                chunks.append(
                    StoryChunk(
                        chunk_id=f"chunk_{chunk_idx:03d}",
                        chapter=ch_name,
                        segment_ids=[s.id for s in current_segs],
                        combined_text=chunk_text,
                        word_count=len(chunk_text.split()),
                    )
                )
                chunk_idx += 1

        return chunks
