from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

from providers.llm import LLMProvider, get_llm_provider
from schemas.canonical import (
    CanonicalChapter,
    CanonicalStory,
    NarrativeBlueprint,
    StoryGraph,
)


class RawCanonicalStoryResult(BaseModel):
    tagline: str = Field(description="One-line gripping hook or tagline")
    synopsis: str = Field(description="Short synopsis of this compressed narrative")
    chapters: List[CanonicalChapter] = Field(description="Generated chapter narratives")


CANONICAL_STORY_PROMPT = """You are a Master Storyteller and Narrative Writer for StoryBridge.
Your mission is to generate the CANONICAL MASTER NARRATIVE in English based strictly on the provided Narrative Blueprint and Story Graph.

Storytelling Rules:
1. Pacing & Flow: Write captivating, immersive prose suitable for audio narration. Avoid dry summarization; tell an actual engaging story.
2. Structure: Follow the blueprint sections as chapters.
3. Character & Plot Consistency: Preserve all specified characters, key actions, and emotional beats.
4. Word Count: Ensure each chapter matches its allocated word count closely.
5. Durations: Compute estimated duration assuming ~130 words per minute (approx 2.16 words/sec).
6. Output: STRICT JSON matching the schema.
"""


class CanonicalStoryGenerator:
    """Generates the Master Canonical Story from Blueprint and Story Graph."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def generate(
        self,
        story_graph: StoryGraph,
        blueprint: NarrativeBlueprint,
    ) -> CanonicalStory:
        # Build prompt from blueprint sections
        sections_desc = "\n\n".join(
            f"### Chapter {idx + 1}: {s.title}\n"
            f"- Target Words: {s.target_words}\n"
            f"- Emotional Tone: {s.emotional_tone}\n"
            f"- Key Plot Points: {', '.join(s.key_plot_points)}\n"
            f"- Required Events: {s.required_event_ids}\n"
            f"- Featured Characters: {s.featured_entity_ids}"
            for idx, s in enumerate(blueprint.sections)
        )

        user_prompt = f"""Story: {story_graph.title}
Target Preset: {blueprint.duration_preset.upper()} (Target ~{blueprint.target_word_count} words total)
Story Summary: {story_graph.summary}
Ending Resolution: {blueprint.ending_state}

Blueprint Plan:
{sections_desc}

Write the full, rich, chapter-by-chapter canonical narrative now."""

        raw_result: RawCanonicalStoryResult = self.llm.generate_structured(
            prompt=user_prompt,
            response_model=RawCanonicalStoryResult,
            system_prompt=CANONICAL_STORY_PROMPT,
            temperature=0.4,
            max_tokens=4096,
        )

        # Normalize words and durations
        total_words = 0
        total_duration_sec = 0

        for ch in raw_result.chapters:
            words = len(ch.content.split())
            ch.word_count = words
            ch.estimated_duration_seconds = max(10, int(words / 2.16))
            total_words += words
            total_duration_sec += ch.estimated_duration_seconds

        return CanonicalStory(
            story_id=story_graph.story_id,
            duration_preset=blueprint.duration_preset,
            title=story_graph.title,
            tagline=raw_result.tagline,
            synopsis=raw_result.synopsis,
            chapters=raw_result.chapters,
            total_word_count=total_words,
            estimated_total_duration_seconds=total_duration_sec,
            model_metadata={
                "provider": self.llm.__class__.__name__,
                "model": getattr(self.llm, "model_name", "unknown"),
            },
        )
