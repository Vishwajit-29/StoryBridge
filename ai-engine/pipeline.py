import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

if sys.platform == "win32":
    import io
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import settings
from compression.canonical_generator import CanonicalStoryGenerator
from compression.planner import NarrativePlanner
from extraction.extractor import StoryExtractor
from ingestion.factory import get_adapter_for_source
from localization.localizer import StoryLocalizer
from providers.llm import LLMProvider, get_llm_provider
from providers.tts import TTSProvider, get_tts_provider
from qa.evaluators import (
    AudioQAEvaluator,
    LocalizationQAEvaluator,
    SourceQAEvaluator,
    StoryQAEvaluator,
)
from schemas.canonical import (
    AudioAsset,
    CanonicalSource,
    CanonicalStory,
    LocalizedScript,
    NarrativeBlueprint,
    PipelineJobStatus,
    PipelineStage,
    RightsRecord,
    StoryGraph,
)
from tts.synthesizer import ChapterAudioSynthesizer

logger = logging.getLogger("storybridge.pipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class StoryBridgePipeline:
    """
    Master StoryBridge Pipeline Orchestrator per SRS Section 4 & 43.
    Executes:
    Source -> Canonical Source -> Story Understanding (Story Graph) ->
    Narrative Compression (Blueprint + Canonical Story) ->
    Localization (Hindi/Marathi) -> QA Checks -> TTS Chapter Synthesis
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        tts_provider: Optional[TTSProvider] = None,
        storage_base_dir: Optional[Path] = None,
    ):
        self.llm = llm_provider or get_llm_provider()
        self.tts = tts_provider or get_tts_provider()
        self.storage_dir = storage_base_dir or settings.STORAGE_DIR

        # Pipeline components
        self.extractor = StoryExtractor(llm_provider=self.llm)
        self.planner = NarrativePlanner(llm_provider=self.llm)
        self.canonical_gen = CanonicalStoryGenerator(llm_provider=self.llm)
        self.localizer = StoryLocalizer(llm_provider=self.llm)
        self.synthesizer = ChapterAudioSynthesizer(tts_provider=self.tts)

        # QA Evaluators
        self.source_qa = SourceQAEvaluator()
        self.story_qa = StoryQAEvaluator()
        self.loc_qa = LocalizationQAEvaluator()
        self.audio_qa = AudioQAEvaluator()

    def get_story_dir(self, story_id: str) -> Path:
        story_dir = self.storage_dir / story_id
        story_dir.mkdir(parents=True, exist_ok=True)
        return story_dir

    def _save_json(self, path: Path, data: dict | list | Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(data, "model_dump_json"):
            path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
        elif hasattr(data, "model_dump"):
            path.write_text(json.dumps(data.model_dump(mode="json"), indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        else:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    # -----------------------------------------------------------------------
    # Pipeline Stages
    # -----------------------------------------------------------------------

    def stage_ingest(
        self,
        source_path_or_content: str | Path,
        title: str,
        story_id: str,
        language: str = "en",
        author: Optional[str] = None,
        rights: Optional[RightsRecord] = None,
    ) -> CanonicalSource:
        """Stage 1: Normalize source format to CanonicalSource."""
        if not source_path_or_content or str(source_path_or_content).strip() in (".", ""):
            source_path_or_content = f"# {title}\n\nA story entitled '{title}' by {author or 'Unknown Author'}."

        logger.info(f"[{story_id}] Stage 1: Ingesting source: {title}")
        story_dir = self.get_story_dir(story_id)
        
        adapter = get_adapter_for_source(source_path_or_content)
        canonical_source = adapter.parse(
            file_path_or_content=source_path_or_content,
            title=title,
            story_id=story_id,
            language=language,
            author=author,
            rights=rights,
        )

        # QA
        qa_report = self.source_qa.evaluate(canonical_source)
        if not qa_report.passed:
            logger.warning(f"[{story_id}] Source QA issues: {qa_report.summary}")

        # Save artifacts
        self._save_json(story_dir / "source" / "metadata.json", canonical_source.source)
        self._save_json(story_dir / "source" / "rights.json", canonical_source.source.rights)
        self._save_json(story_dir / "normalized" / "canonical_source.json", canonical_source)
        self._save_json(story_dir / "normalized" / "qa.json", qa_report)

        return canonical_source

    def stage_understand(self, canonical_source: CanonicalSource) -> StoryGraph:
        """Stage 2: Extract Entities, Events, Relations, Timeline, Causality into StoryGraph."""
        story_id = canonical_source.source.id
        logger.info(f"[{story_id}] Stage 2: Extracting Story Graph")
        story_dir = self.get_story_dir(story_id)

        story_graph = self.extractor.extract(canonical_source)

        # QA
        qa_report = self.story_qa.evaluate(story_graph)
        if not qa_report.passed:
            logger.warning(f"[{story_id}] Story Graph QA issues: {qa_report.summary}")

        # Save artifacts (per SRS Section 18)
        und_dir = story_dir / "understanding"
        self._save_json(und_dir / "story_graph.json", story_graph)
        self._save_json(und_dir / "entities.json", [e.model_dump(mode="json") for e in story_graph.entities])
        self._save_json(und_dir / "events.json", [e.model_dump(mode="json") for e in story_graph.events])
        self._save_json(und_dir / "relations.json", [r.model_dump(mode="json") for r in story_graph.relationships])
        self._save_json(und_dir / "timeline.json", [t.model_dump(mode="json") for t in story_graph.timeline])
        self._save_json(und_dir / "qa.json", qa_report)

        return story_graph

    def stage_compress(
        self,
        story_graph: StoryGraph,
        presets: Optional[List[str]] = None,
    ) -> Dict[str, CanonicalStory]:
        """Stage 3: Generate Narrative Blueprint and Canonical Master Narrative per duration preset."""
        story_id = story_graph.story_id
        target_presets = presets or ["quick", "standard", "complete"]
        logger.info(f"[{story_id}] Stage 3: Compressing narrative for presets: {target_presets}")
        story_dir = self.get_story_dir(story_id)
        
        canonical_stories: Dict[str, CanonicalStory] = {}

        for preset in target_presets:
            logger.info(f"[{story_id}] Planning blueprint for preset: {preset}")
            blueprint = self.planner.create_blueprint(story_graph, duration_preset=preset)
            self._save_json(story_dir / "narrative" / f"blueprint_{preset}.json", blueprint)

            logger.info(f"[{story_id}] Generating canonical master narrative for preset: {preset}")
            canonical_story = self.canonical_gen.generate(story_graph, blueprint)
            self._save_json(story_dir / "narrative" / f"{preset}.json", canonical_story)
            canonical_stories[preset] = canonical_story

        return canonical_stories

    def stage_localize(
        self,
        canonical_story: CanonicalStory,
        story_graph: StoryGraph,
        languages: Optional[List[str]] = None,
    ) -> Dict[str, LocalizedScript]:
        """Stage 4: Localize canonical narrative into regional Indian languages."""
        story_id = canonical_story.story_id
        target_langs = languages or ["hi", "mr"]
        logger.info(f"[{story_id}] Stage 4: Localizing preset '{canonical_story.duration_preset}' into: {target_langs}")
        story_dir = self.get_story_dir(story_id)

        localized_scripts: Dict[str, LocalizedScript] = {}

        for lang in target_langs:
            logger.info(f"[{story_id}] Adapting narrative into {lang.upper()}")
            script = self.localizer.localize(
                canonical_story=canonical_story,
                story_graph=story_graph,
                target_language=lang,
            )

            # Localization QA
            qa_report = self.loc_qa.evaluate(canonical_story, script)
            
            loc_dir = story_dir / "localization" / lang / canonical_story.duration_preset
            self._save_json(loc_dir / "script.json", script)
            self._save_json(loc_dir / "qa.json", qa_report)
            localized_scripts[lang] = script

        return localized_scripts

    async def stage_synthesize_audio(
        self,
        localized_scripts: Dict[str, LocalizedScript],
        voice_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, AudioAsset]:
        """Stage 5: Synthesize chapter-level TTS audio."""
        audio_assets: Dict[str, AudioAsset] = {}

        for lang, script in localized_scripts.items():
            story_id = script.story_id
            preset = script.duration_preset
            logger.info(f"[{story_id}] Stage 5: Synthesizing TTS audio for {lang} ({preset})")
            
            audio_out_dir = self.storage_dir / story_id / "audio" / lang / preset
            voice_id = voice_map.get(lang) if voice_map else None

            audio_asset = await self.synthesizer.synthesize_script(
                script=script,
                output_dir=audio_out_dir,
                voice_id=voice_id,
            )

            qa_report = self.audio_qa.evaluate(audio_asset)
            self._save_json(audio_out_dir / "asset_metadata.json", audio_asset)
            self._save_json(audio_out_dir / "qa.json", qa_report)

            audio_assets[lang] = audio_asset

        return audio_assets

    async def run_full_pipeline(
        self,
        source_path_or_content: str | Path,
        title: str,
        story_id: str,
        author: Optional[str] = None,
        rights: Optional[RightsRecord] = None,
        duration_presets: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute end-to-end StoryBridge pipeline from raw source to playable audio."""
        logger.info(f"====== Starting StoryBridge Pipeline for: {title} ({story_id}) ======")
        
        # 1. Ingestion
        canonical_source = self.stage_ingest(
            source_path_or_content=source_path_or_content,
            title=title,
            story_id=story_id,
            author=author,
            rights=rights,
        )

        # 2. Story Understanding
        story_graph = self.stage_understand(canonical_source)

        # 3. Compression
        presets = duration_presets or ["quick", "standard"]
        canonical_stories = self.stage_compress(story_graph, presets=presets)

        # 4. Localization
        target_langs = languages or ["hi", "mr"]
        all_localized: Dict[str, Dict[str, LocalizedScript]] = {}
        all_audio: Dict[str, Dict[str, AudioAsset]] = {}

        for preset, canonical_story in canonical_stories.items():
            loc_scripts = self.stage_localize(canonical_story, story_graph, target_langs)
            all_localized[preset] = loc_scripts

            # 5. Audio Synthesis
            audio_assets = await self.stage_synthesize_audio(loc_scripts)
            all_audio[preset] = audio_assets

        logger.info(f"====== Pipeline Completed Successfully for {story_id} ======")
        return {
            "story_id": story_id,
            "title": title,
            "canonical_source": canonical_source,
            "story_graph": story_graph,
            "canonical_stories": canonical_stories,
            "localized_scripts": all_localized,
            "audio_assets": all_audio,
        }
