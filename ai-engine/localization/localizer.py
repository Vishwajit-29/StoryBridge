from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from providers.llm import LLMProvider, get_llm_provider
from schemas.canonical import (
    CanonicalStory,
    LocalizedChapter,
    LocalizedScript,
    StoryGraph,
)

LANGUAGE_NAMES = {
    "hi": "Hindi (हिंदी)",
    "mr": "Marathi (मराठी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)",
    "en": "English",
}


class RawLocalizedResult(BaseModel):
    title: str = Field(description="Localized story title")
    synopsis: str = Field(description="Localized story synopsis")
    chapters: List[LocalizedChapter] = Field(description="Localized chapter scripts")
    entity_name_map: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from English character/entity names to native script names",
    )


LOCALIZATION_SYSTEM_PROMPT = """You are a Native Multilingual Storyteller and Localization Master for StoryBridge.
Your mission is to adapt the approved English CANONICAL STORY into natural, evocative storytelling in the target language (e.g. Hindi, Marathi).

CRITICAL LOCALIZATION RULES (SRS Section 13):
1. NOT Literal Translation: Adapt the narrative with rich, authentic local idioms and storytelling cadence (कथावाचन शैली / गोष्टी सांगण्याची शैली).
2. Fact & Causal Preservation: Keep all story facts, sequence of events, relationships, and plot turns 100% faithful to the canonical story.
3. Character Consistency: Transliterate/translate character names consistently in native script (Devanagari for Hindi/Marathi) and populate entity_name_map.
4. Audio Narration Readiness: Write prose that sounds natural and powerful when read aloud by Text-To-Speech (TTS).
5. Output: STRICT JSON matching the schema.
"""


class StoryLocalizer:
    """Adapts CanonicalStory into localized scripts in regional languages."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def localize(
        self,
        canonical_story: CanonicalStory,
        story_graph: StoryGraph,
        target_language: str = "hi",
    ) -> LocalizedScript:
        lang_name = LANGUAGE_NAMES.get(target_language.lower(), target_language)

        # Build chapter descriptions
        chapters_input = "\n\n".join(
            f"--- Chapter {ch.chapter_number}: {ch.title} ---\n{ch.content}"
            for ch in canonical_story.chapters
        )

        entities_input = ", ".join(f"{e.name} ({e.type})" for e in story_graph.entities)

        user_prompt = f"""Target Language: {lang_name} (Code: {target_language})
Story Title: {canonical_story.title}
Tagline: {canonical_story.tagline}
Synopsis: {canonical_story.synopsis}

Key Entities to adapt consistently:
{entities_input}

Canonical English Chapters:
{chapters_input}

Provide the complete native-language localized narrative script in {lang_name}."""

        raw_result: RawLocalizedResult = self.llm.generate_structured(
            prompt=user_prompt,
            response_model=RawLocalizedResult,
            system_prompt=LOCALIZATION_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4096,
        )

        total_words = 0
        total_duration_sec = 0

        for ch in raw_result.chapters:
            words = len(ch.content.split())
            ch.word_count = words
            # In Hindi/Marathi, syllable count and speed are ~120-130 wpm
            ch.estimated_duration_seconds = max(10, int(words / 2.0))
            total_words += words
            total_duration_sec += ch.estimated_duration_seconds

        return LocalizedScript(
            story_id=canonical_story.story_id,
            duration_preset=canonical_story.duration_preset,
            language=target_language,
            language_name=lang_name,
            title=raw_result.title,
            synopsis=raw_result.synopsis,
            chapters=raw_result.chapters,
            entity_name_map=raw_result.entity_name_map,
            total_word_count=total_words,
            estimated_total_duration_seconds=total_duration_sec,
            model_metadata={
                "provider": self.llm.__class__.__name__,
                "model": getattr(self.llm, "model_name", "unknown"),
            },
        )
