from __future__ import annotations
import json
from typing import List, Optional
from pydantic import BaseModel, Field

from config import settings
from providers.llm import LLMProvider, get_llm_provider
from schemas.canonical import (
    NarrativeBlueprint,
    NarrativeSection,
    StoryGraph,
)
from storygraph.graph_builder import StoryGraphAnalyzer


class RawBlueprintResult(BaseModel):
    sections: List[NarrativeSection] = Field(default_factory=list)
    ending_state: str = Field(description="Final state of the narrative resolution")


BLUEPRINT_SYSTEM_PROMPT = """You are an expert Narrative Architect and Story Editor for StoryBridge.
Your goal is to generate a structured Narrative Blueprint that compresses a story into a specific target duration.

Follow these strict storytelling compression principles:
1. Target Word Count & Pace: Adhere strictly to the requested duration and word count.
2. Causal Integrity: Never omit a cause event if its downstream effect is included.
3. Emotional Resonance: Ensure every section has a clear emotional tone.
4. Structure: Divide into 2-5 logically structured chapters/sections (e.g. Setup, Confrontation, Turning Point, Climax, Resolution).
5. Output STRICT JSON conforming to the requested schema.
"""


class NarrativePlanner:
    """Plans compressed narrative blueprints for quick, standard, and complete durations."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def create_blueprint(
        self,
        story_graph: StoryGraph,
        duration_preset: str = "standard",
    ) -> NarrativeBlueprint:
        preset_info = settings.DURATION_PRESETS.get(
            duration_preset.lower(),
            settings.DURATION_PRESETS["standard"],
        )
        target_mins = preset_info["target_minutes"]
        target_words = preset_info["target_words"]

        # Analyze graph for critical causal path
        analyzer = StoryGraphAnalyzer(story_graph)
        critical_event_ids = analyzer.get_critical_path()

        # Format events and entities for the prompt
        events_summary = "\n".join(
            f"- [{ev.id}] (Score: {ev.importance_score:.2f}, Crucial: {ev.is_crucial}) {ev.title}: {ev.description}"
            for ev in story_graph.events
        )
        entities_summary = "\n".join(
            f"- [{ent.id}] {ent.name} ({ent.type}): {ent.description}"
            for ent in story_graph.entities
        )
        causal_summary = "\n".join(
            f"- {c.cause_event_id} --({c.link_type})--> {c.effect_event_id}"
            for c in story_graph.causal_links
        )

        user_prompt = f"""Story: {story_graph.title}
Target Preset: {duration_preset.upper()}
Target Duration: {target_mins} minutes
Target Total Word Count: ~{target_words} words

Entities:
{entities_summary}

Story Events:
{events_summary}

Causal Dependencies:
{causal_summary}

Crucial Events Identified: {critical_event_ids}

Design a {len(critical_event_ids) if len(critical_event_ids) < 4 else 3}-section Narrative Blueprint.
Allocate target word counts per section summing to approximately {target_words} words."""

        raw_result: RawBlueprintResult = self.llm.generate_structured(
            prompt=user_prompt,
            response_model=RawBlueprintResult,
            system_prompt=BLUEPRINT_SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=2048,
        )

        all_section_events = []
        for s in raw_result.sections:
            all_section_events.extend(s.required_event_ids)

        all_graph_event_ids = {e.id for e in story_graph.events}
        excluded_ids = list(all_graph_event_ids - set(all_section_events))

        return NarrativeBlueprint(
            story_id=story_graph.story_id,
            duration_preset=duration_preset,
            target_duration_minutes=target_mins,
            target_word_count=target_words,
            sections=raw_result.sections,
            required_event_ids=all_section_events,
            excluded_event_ids=excluded_ids,
            ending_state=raw_result.ending_state,
        )
