from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Rights & Provenance Enums & Models
# ---------------------------------------------------------------------------

class RightsType(str, Enum):
    PUBLIC_DOMAIN = "PUBLIC_DOMAIN"
    OPEN_LICENSE = "OPEN_LICENSE"
    ORIGINAL = "ORIGINAL"
    LICENSED = "LICENSED"
    UNKNOWN = "UNKNOWN"
    RESTRICTED = "RESTRICTED"


class RightsRecord(BaseModel):
    type: RightsType = RightsType.PUBLIC_DOMAIN
    verified: bool = True
    evidence_url_or_note: Optional[str] = None
    attribution: Optional[str] = None
    license_identifier: Optional[str] = "CC0 / Public Domain"


class SourceRef(BaseModel):
    page: Optional[int] = None
    chapter: Optional[str] = None
    paragraph_index: Optional[int] = None
    url: Optional[str] = None
    timestamp_ms: Optional[int] = None


class Segment(BaseModel):
    id: str
    sequence: int
    chapter: Optional[str] = None
    scene_id: Optional[str] = None
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None
    speaker: Optional[str] = None
    text: str
    source_ref: Optional[SourceRef] = None


class SourceMetadata(BaseModel):
    id: str
    type: str  # text, markdown, pdf, epub, subtitle, web, audio, video
    title: str
    author: Optional[str] = None
    language: str = "en"
    checksum_sha256: Optional[str] = None
    original_filename: Optional[str] = None
    rights: RightsRecord = Field(default_factory=RightsRecord)


class CanonicalSource(BaseModel):
    schema_version: str = "1.0"
    source: SourceMetadata
    segments: List[Segment] = Field(default_factory=list)
    extraction_warnings: List[str] = Field(default_factory=list)
    total_characters: int = 0
    total_words: int = 0


# ---------------------------------------------------------------------------
# Story Graph & Understanding Models
# ---------------------------------------------------------------------------

class EntityType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    ORGANIZATION = "organization"
    OBJECT = "object"
    CONCEPT = "concept"


class Entity(BaseModel):
    id: str
    name: str
    type: EntityType = EntityType.CHARACTER
    aliases: List[str] = Field(default_factory=list)
    description: str
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    source_segment_ids: List[str] = Field(default_factory=list)


class Relationship(BaseModel):
    id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str  # friend_of, enemy_of, mentor_of, sibling_of, parent_of, loyal_to, betrays, etc.
    description: Optional[str] = None
    source_segment_ids: List[str] = Field(default_factory=list)


class CausalLink(BaseModel):
    cause_event_id: str
    effect_event_id: str
    link_type: str = "causes"  # causes, enables, triggers, resolves, prevents
    explanation: Optional[str] = None


class StoryEvent(BaseModel):
    id: str
    sequence: int
    title: str
    description: str
    chronological_order: int
    participant_entity_ids: List[str] = Field(default_factory=list)
    location_entity_id: Optional[str] = None
    source_segment_ids: List[str] = Field(default_factory=list)
    
    # Detailed Importance Scoring (0.0 to 1.0)
    plot_relevance: float = 0.5
    character_relevance: float = 0.5
    causal_relevance: float = 0.5
    emotional_relevance: float = 0.5
    mystery_relevance: float = 0.5
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    is_spoiler: bool = False
    is_crucial: bool = False  # If true, cannot be dropped in Quick/Standard summaries


class TimelineEntry(BaseModel):
    event_id: str
    narrative_order: int
    story_chronology_order: int
    is_flashback: bool = False
    is_parallel: bool = False


class StoryGraph(BaseModel):
    schema_version: str = "1.0"
    story_id: str
    title: str
    summary: str
    entities: List[Entity] = Field(default_factory=list)
    events: List[StoryEvent] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    causal_links: List[CausalLink] = Field(default_factory=list)
    timeline: List[TimelineEntry] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    model_metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Narrative Compression & Blueprint Models
# ---------------------------------------------------------------------------

class NarrativeSection(BaseModel):
    section_id: str
    title: str
    required_event_ids: List[str] = Field(default_factory=list)
    featured_entity_ids: List[str] = Field(default_factory=list)
    key_plot_points: List[str] = Field(default_factory=list)
    emotional_tone: str
    target_words: int


class NarrativeBlueprint(BaseModel):
    schema_version: str = "1.0"
    story_id: str
    duration_preset: str  # quick (3-7m), standard (10-20m), complete (30-60m)
    target_duration_minutes: int
    target_word_count: int
    sections: List[NarrativeSection] = Field(default_factory=list)
    required_event_ids: List[str] = Field(default_factory=list)
    excluded_event_ids: List[str] = Field(default_factory=list)
    ending_state: str


class CanonicalChapter(BaseModel):
    chapter_id: str
    chapter_number: int
    title: str
    content: str
    word_count: int
    estimated_duration_seconds: int
    event_ids: List[str] = Field(default_factory=list)
    character_ids: List[str] = Field(default_factory=list)


class CanonicalStory(BaseModel):
    schema_version: str = "1.0"
    story_id: str
    duration_preset: str
    title: str
    tagline: str
    synopsis: str
    chapters: List[CanonicalChapter] = Field(default_factory=list)
    total_word_count: int = 0
    estimated_total_duration_seconds: int = 0
    model_metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Localization & Native Adaptation Models
# ---------------------------------------------------------------------------

class LocalizedChapter(BaseModel):
    chapter_id: str
    chapter_number: int
    title: str
    content: str
    cultural_notes: Optional[str] = None
    word_count: int = 0
    estimated_duration_seconds: int = 0


class LocalizedScript(BaseModel):
    schema_version: str = "1.0"
    story_id: str
    duration_preset: str
    language: str  # hi, mr, en, etc.
    language_name: str  # Hindi, Marathi, English
    title: str
    synopsis: str
    chapters: List[LocalizedChapter] = Field(default_factory=list)
    entity_name_map: Dict[str, str] = Field(default_factory=dict)
    total_word_count: int = 0
    estimated_total_duration_seconds: int = 0
    model_metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# QA & Validation Models
# ---------------------------------------------------------------------------

class QASeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class QAIssue(BaseModel):
    stage: str  # source, story_graph, narrative, localization, audio
    severity: QASeverity = QASeverity.INFO
    code: str
    message: str
    context: Optional[Dict[str, Any]] = None


class QAReport(BaseModel):
    stage: str
    passed: bool
    score: float = Field(default=1.0, ge=0.0, le=1.0)
    issues: List[QAIssue] = Field(default_factory=list)
    summary: str


# ---------------------------------------------------------------------------
# Audio & Delivery Models
# ---------------------------------------------------------------------------

class AudioChapter(BaseModel):
    chapter_id: str
    chapter_number: int
    title: str
    audio_path: str
    audio_format: str = "mp3"
    duration_seconds: float
    file_size_bytes: int


class AudioAsset(BaseModel):
    story_id: str
    language: str
    duration_preset: str
    voice_id: str
    chapters: List[AudioChapter] = Field(default_factory=list)
    total_duration_seconds: float = 0.0
    created_at: str


# ---------------------------------------------------------------------------
# Pipeline State & Workflow
# ---------------------------------------------------------------------------

class PipelineStage(str, Enum):
    IMPORTED = "IMPORTED"
    NORMALIZED = "NORMALIZED"
    UNDERSTANDING_READY = "UNDERSTANDING_READY"
    UNDERSTORY_REVIEW = "UNDERSTORY_REVIEW"
    STORY_APPROVED = "STORY_APPROVED"
    NARRATIVE_GENERATED = "NARRATIVE_GENERATED"
    NARRATIVE_APPROVED = "NARRATIVE_APPROVED"
    LOCALIZATION_GENERATED = "LOCALIZATION_GENERATED"
    LOCALIZATION_APPROVED = "LOCALIZATION_APPROVED"
    AUDIO_GENERATED = "AUDIO_GENERATED"
    AUDIO_APPROVED = "AUDIO_APPROVED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    REVISION_REQUIRED = "REVISION_REQUIRED"


class PipelineJobStatus(BaseModel):
    job_id: str
    story_id: str
    stage: PipelineStage
    progress_percentage: int = 0
    current_step: str = ""
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
