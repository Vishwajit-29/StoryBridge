import pytest
from pathlib import Path
import sys

# Add ai-engine root to python path
ai_engine_path = Path(__file__).resolve().parent.parent
if str(ai_engine_path) not in sys.path:
    sys.path.insert(0, str(ai_engine_path))

from config import settings
from ingestion.text_adapter import TextAdapter
from ingestion.factory import get_adapter_for_source
from extraction.chunker import StoryChunker
from extraction.importance import ImportanceCalculator
from storygraph.graph_builder import StoryGraphAnalyzer
from providers.llm import MockLLMProvider
from providers.tts import MockTTSProvider
from schemas.canonical import (
    CanonicalSource,
    Entity,
    EntityType,
    Relationship,
    StoryEvent,
    StoryGraph,
    CausalLink,
    TimelineEntry,
)
from compression.planner import NarrativePlanner
from compression.canonical_generator import CanonicalStoryGenerator
from localization.localizer import StoryLocalizer
from qa.evaluators import SourceQAEvaluator, StoryQAEvaluator, LocalizationQAEvaluator, AudioQAEvaluator
from pipeline import StoryBridgePipeline


@pytest.fixture
def sample_fixture_path():
    return Path(__file__).resolve().parent.parent.parent / "shared" / "fixtures" / "the_monkey_and_the_wedge.md"


def test_text_adapter(sample_fixture_path):
    adapter = TextAdapter()
    source = adapter.parse(
        file_path_or_content=sample_fixture_path,
        title="The Monkey and the Wedge",
        story_id="story_panchatantra_01",
        language="en",
        author="Vishnu Sharma",
    )
    assert source.source.title == "The Monkey and the Wedge"
    assert len(source.segments) >= 4
    assert source.total_words > 100
    assert source.source.rights.verified is True


def test_source_qa_evaluator(sample_fixture_path):
    adapter = TextAdapter()
    source = adapter.parse(
        file_path_or_content=sample_fixture_path,
        title="The Monkey and the Wedge",
        story_id="story_01",
    )
    qa = SourceQAEvaluator()
    report = qa.evaluate(source)
    assert report.passed is True
    assert report.score >= 0.8


def test_chunker(sample_fixture_path):
    adapter = TextAdapter()
    source = adapter.parse(
        file_path_or_content=sample_fixture_path,
        title="The Monkey and the Wedge",
        story_id="story_01",
    )
    chunker = StoryChunker(target_chunk_words=100)
    chunks = chunker.chunk(source)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.combined_text
        assert len(chunk.segment_ids) > 0


def test_importance_calculator():
    calc = ImportanceCalculator()
    event = StoryEvent(
        id="ev_01",
        sequence=1,
        title="Monkey pulls wedge",
        description="The monkey pulls the wedge out",
        chronological_order=1,
        plot_relevance=0.9,
        causal_relevance=0.95,
        character_relevance=0.8,
        emotional_relevance=0.7,
        mystery_relevance=0.2,
    )
    score = calc.score_event(event)
    assert 0.7 <= score <= 1.0
    assert event.is_crucial is True


def test_story_graph_analyzer():
    story_graph = StoryGraph(
        story_id="story_01",
        title="The Monkey and the Wedge",
        summary="A monkey meddles with a carpenter's wedge.",
        entities=[
            Entity(id="char_01", name="Monkey", type=EntityType.CHARACTER, description="Curious monkey"),
            Entity(id="char_02", name="Carpenter", type=EntityType.CHARACTER, description="Master builder"),
            Entity(id="loc_01", name="Temple Site", type=EntityType.LOCATION, description="Construction grove"),
        ],
        events=[
            StoryEvent(
                id="ev_01",
                sequence=1,
                title="Carpenter places wedge",
                description="Carpenter leaves wedge in split log",
                chronological_order=1,
                is_crucial=True,
            ),
            StoryEvent(
                id="ev_02",
                sequence=2,
                title="Monkey pulls wedge",
                description="Monkey pulls out the wedge",
                chronological_order=2,
                is_crucial=True,
            ),
            StoryEvent(
                id="ev_03",
                sequence=3,
                title="Log snaps shut",
                description="The log traps the monkey",
                chronological_order=3,
                is_crucial=True,
            ),
        ],
        relationships=[
            Relationship(id="rel_01", source_entity_id="char_01", target_entity_id="char_02", relation_type="intrudes_on"),
        ],
        causal_links=[
            CausalLink(cause_event_id="ev_01", effect_event_id="ev_02", link_type="enables"),
            CausalLink(cause_event_id="ev_02", effect_event_id="ev_03", link_type="causes"),
        ],
    )

    analyzer = StoryGraphAnalyzer(story_graph)
    critical_path = analyzer.get_critical_path()
    assert "ev_01" in critical_path
    assert "ev_02" in critical_path
    assert "ev_03" in critical_path

    validation = analyzer.validate_graph()
    assert validation["is_valid_dag"] is True
    assert len(validation["cycles_detected"]) == 0


@pytest.mark.asyncio
async def test_full_pipeline_with_mock_providers(sample_fixture_path, tmp_path):
    mock_llm = MockLLMProvider()
    mock_tts = MockTTSProvider()
    
    pipeline = StoryBridgePipeline(
        llm_provider=mock_llm,
        tts_provider=mock_tts,
        storage_base_dir=tmp_path,
    )

    result = await pipeline.run_full_pipeline(
        source_path_or_content=sample_fixture_path,
        title="The Monkey and the Wedge",
        story_id="test_story_001",
        author="Vishnu Sharma",
        duration_presets=["quick"],
        languages=["hi"],
    )

    assert result["story_id"] == "test_story_001"
    assert (tmp_path / "test_story_001" / "normalized" / "canonical_source.json").exists()
    assert (tmp_path / "test_story_001" / "understanding" / "story_graph.json").exists()
    assert (tmp_path / "test_story_001" / "narrative" / "quick.json").exists()
    assert (tmp_path / "test_story_001" / "localization" / "hi" / "quick" / "script.json").exists()
    assert (tmp_path / "test_story_001" / "audio" / "hi" / "quick" / "asset_metadata.json").exists()
