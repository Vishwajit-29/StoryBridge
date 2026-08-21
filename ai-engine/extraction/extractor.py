from __future__ import annotations
import json
from typing import List, Optional
from pydantic import BaseModel, Field

from config import settings
from extraction.chunker import StoryChunker
from extraction.importance import ImportanceCalculator
from providers.llm import LLMProvider, get_llm_provider
from schemas.canonical import (
    CanonicalSource,
    CausalLink,
    Entity,
    EntityType,
    Relationship,
    StoryEvent,
    StoryGraph,
    TimelineEntry,
)


class RawExtractionResult(BaseModel):
    summary: str = Field(description="High-level narrative summary of the story")
    themes: List[str] = Field(default_factory=list, description="Core themes of the story")
    entities: List[Entity] = Field(default_factory=list, description="All identified characters, locations, objects")
    events: List[StoryEvent] = Field(default_factory=list, description="Ordered chronological story events")
    relationships: List[Relationship] = Field(default_factory=list, description="Key relationships between entities")
    causal_links: List[CausalLink] = Field(default_factory=list, description="Causal dependencies between events")
    timeline: List[TimelineEntry] = Field(default_factory=list, description="Timeline order and flashbacks")


EXTRACTION_SYSTEM_PROMPT = """You are an expert Story Analyst and Narrative Intelligence Engine for StoryBridge.
Your role is to deeply analyze canonical story text and construct a high-fidelity Story Graph.

Analyze the given story and extract:
1. Summary: A 2-3 paragraph coherent narrative summary.
2. Themes: Main thematic elements.
3. Entities: Characters (with clear roles, traits, aliases), Locations, Organizations, Objects.
4. Events: Major plot points with relevance scores (plot_relevance, character_relevance, causal_relevance, emotional_relevance, mystery_relevance from 0.0 to 1.0).
5. Relationships: Explicit character-to-character dynamics (family_of, ally_of, enemy_of, mentor_of, loves, betrays, etc.).
6. Causal Links: What event caused or enabled subsequent events (crucial for narrative compression).
7. Timeline: Narrative sequence versus chronological story order.

Be accurate, preserve proper character names faithfully, and output STRICT structured JSON.
"""


class StoryExtractor:
    """Extracts Entities, Events, Relationships, Causality, and Timeline from CanonicalSource."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()
        self.chunker = StoryChunker()
        self.importance_calc = ImportanceCalculator()

    def extract(self, source: CanonicalSource) -> StoryGraph:
        chunks = self.chunker.chunk(source)
        
        # Combine text or sample representative text if source is large
        all_text = "\n\n".join(
            f"--- {chunk.chapter} (Chunk {chunk.chunk_id}) ---\n{chunk.combined_text}"
            for chunk in chunks
        )

        # For long sources, keep prompt within context window
        max_prompt_chars = 45000
        if len(all_text) > max_prompt_chars:
            all_text = all_text[:max_prompt_chars] + "\n\n[... Source truncated for extraction ...]"

        user_prompt = f"""Story Title: {source.source.title}
Author: {source.source.author or 'Unknown'}
Language: {source.source.language}

Source Text:
{all_text}

Extract the complete Story Graph according to the schema. Make sure all entity IDs (e.g. char_01) and event IDs (e.g. ev_01) are consistent across relationships and causal links."""

        # Call LLM via provider (NVIDIA NIM)
        extraction: RawExtractionResult = self.llm.generate_structured(
            prompt=user_prompt,
            response_model=RawExtractionResult,
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            temperature=0.1,
            max_tokens=4096,
        )

        # Recalculate composite importance scores for each event
        for event in extraction.events:
            self.importance_calc.score_event(event)

        # If timeline was empty, construct linear timeline from events
        if not extraction.timeline and extraction.events:
            for idx, ev in enumerate(extraction.events):
                extraction.timeline.append(
                    TimelineEntry(
                        event_id=ev.id,
                        narrative_order=idx + 1,
                        story_chronology_order=ev.chronological_order or (idx + 1),
                    )
                )

        return StoryGraph(
            story_id=source.source.id,
            title=source.source.title,
            summary=extraction.summary,
            entities=extraction.entities,
            events=extraction.events,
            relationships=extraction.relationships,
            causal_links=extraction.causal_links,
            timeline=extraction.timeline,
            themes=extraction.themes,
            model_metadata={
                "provider": self.llm.__class__.__name__,
                "model": getattr(self.llm, "model_name", "unknown"),
                "total_source_words": source.total_words,
            },
        )
