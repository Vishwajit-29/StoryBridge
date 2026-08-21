# Software Requirements Specification (SRS)

## Project: StoryBridge
### AI-Powered Multilingual Storytelling and Story Compression Platform

**Document Version:** 2.0  
**Status:** Updated Baseline Specification  
**Target:** Web-first MVP with extensible mobile architecture  
**Primary Audience:** Product owner, backend/frontend engineers, AI engineers, DevOps, QA, and future contributors

---

## 1. Introduction

### 1.1 Purpose

StoryBridge is a free, ad-supported, multilingual storytelling platform that reduces two major barriers to narrative content:

1. **Language barrier** — users may understand a story better in a native/regional language.
2. **Time barrier** — users may not have enough time to consume the full original work.

StoryBridge transforms legally usable source material into structured story representations, compressed narrative versions, native-language adaptations, and AI-narrated experiences.

The platform is intentionally designed so that **source format is separated from downstream story processing**. A video, subtitle file, web article, PDF, EPUB, or plain text source must ultimately be normalized into a common canonical representation before story understanding begins.

### 1.2 Product Vision

> **Every story. Your language. Your time.**

A user should be able to find a story and select:

- Preferred language.
- Desired narrative duration.
- Story depth.
- Spoiler level where supported.
- Narration style/voice where available.

StoryBridge then presents a coherent story experience rather than performing simple word-for-word translation.

### 1.3 Core Product Thesis

StoryBridge is **not primarily an AI dubbing platform** and is not merely an AI summarization tool.

The core system is:

> **Source → Story Understanding → Story Graph → Narrative Compression → Native-language Localization → Narration → Story Experience**

The Story Graph and narrative-compression pipeline are the central intellectual/product assets.

### 1.4 Initial Legal/Content Scope

The initial public platform shall process only content for which StoryBridge has a documented right to use, such as:

- Public-domain works.
- Content under compatible open licenses.
- Original content owned by StoryBridge.
- Creator/licensed content where the license explicitly permits the intended processing and distribution.

The system shall maintain source and rights metadata for every content item.

The platform shall **not assume that a work is permissible merely because it is summarized, transformed, or AI-generated**.

### 1.5 Initial Target Audience

Primary audiences:

- Users who prefer Indian regional languages.
- Users consuming foreign/international stories through translated or summarized formats.
- Users interested in mythology, folklore, public-domain literature, history, and licensed stories.
- Users who want to understand a long story in a shorter period.
- Anime/series/movie audiences in future licensed-content phases.

### 1.6 Scope of This SRS

This SRS specifies:

- Product requirements.
- Source ingestion architecture.
- Canonical data representations.
- AI processing pipeline.
- Story graph and narrative compression.
- Localization and TTS.
- Approval/workflow/versioning.
- User experience.
- Administration.
- APIs and data storage.
- Scalability and reliability requirements.
- Security and content-rights requirements.
- MVP and future-stage boundaries.

---

# 2. Definitions and Terminology

| Term | Definition |
|---|---|
| Source | Original input content supplied/imported into StoryBridge. |
| Source Adapter | Format-specific component that converts a source into the canonical normalized representation. |
| Canonical Source | Normalized, format-independent representation of the source content. |
| Segment | Small ordered unit of normalized source content. |
| Entity | Story-relevant object such as a character, location, organization, object, or concept. |
| Event | A meaningful occurrence in the story. |
| Relationship | Explicit or inferred relationship between entities. |
| Story Graph | Structured representation of characters, events, relationships, chronology, causality, and importance. |
| Narrative Blueprint | Structured plan for generating a story at a target duration/depth. |
| Canonical Story | Approved master narrative representation before language localization. |
| Localization | Native-language adaptation preserving story facts and narrative intent while allowing natural restructuring. |
| TTS | Text-to-speech synthesis. |
| Artifact | Versioned output produced by one pipeline stage. |
| Pipeline Job | Asynchronous processing task executed by a worker. |
| Approval Gate | Human or automated validation checkpoint. |
| Rights Record | Metadata describing why StoryBridge may process/distribute a source. |
| Story Mode | User-facing compressed narrative experience. |
| Quick Story | Very short version, approximately 3–7 minutes. |
| Standard Story | Main compressed narrative, approximately 10–20 minutes. |
| Complete Story | Long-form compressed narrative, approximately 30–60+ minutes. |

---

# 3. Product Goals and Non-Goals

## 3.1 Goals

1. Provide natural multilingual storytelling rather than literal translation.
2. Allow users to control narrative length.
3. Preserve important plot events, characters, causality, and emotional context.
4. Make source ingestion independent from downstream AI processing.
5. Make every pipeline stage independently retryable and versionable.
6. Support public-domain/openly licensed content as the initial content foundation.
7. Keep the service free to users and monetizable through advertising.
8. Support local/open-source AI components wherever practical.
9. Provide a scalable architecture that can later accept licensed movies, series, anime, books, and creator content.

## 3.2 Non-Goals for MVP

The MVP shall not attempt to:

- Build a proprietary foundation model.
- Train a proprietary TTS model.
- Support every language immediately.
- Automatically process arbitrary copyrighted movies from the public internet.
- Build a social network/community platform.
- Build a full video-editing platform.
- Build an AI avatar/lip-sync system.
- Build a native mobile application before the web experience is validated.
- Use a large microservice fleet without demonstrated scale requirements.

---

# 4. High-Level System Flow

```text
                         ┌─────────────────────┐
                         │      ADMIN/CMS       │
                         │ Upload / Import     │
                         │ Metadata / Rights   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   INGESTION LAYER   │
                         │                     │
                         │ Video Adapter       │
                         │ Web Adapter         │
                         │ PDF Adapter         │
                         │ EPUB Adapter        │
                         │ SRT/VTT Adapter     │
                         │ Text/Markdown       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ CANONICAL SOURCE    │
                         │ transcript.json     │
                         │ metadata.json       │
                         │ provenance.json     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ STORY UNDERSTANDING │
                         │ chunking            │
                         │ entities            │
                         │ events              │
                         │ relationships       │
                         │ timeline            │
                         │ causality           │
                         │ importance          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     STORY GRAPH     │
                         │ canonical semantic  │
                         │ representation      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ NARRATIVE PLANNER   │
                         │ 5m / 15m / 30m /    │
                         │ 60m+ / custom       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ CANONICAL STORY     │
                         │ Master narrative    │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
                  Hindi          Marathi          Tamil
                     │              │              │
                     ▼              ▼              ▼
               Localized QA   Localized QA    Localized QA
                     │              │              │
                     └──────────────┼──────────────┘
                                    ▼
                                  TTS
                                    │
                                    ▼
                               Audio QA
                                    │
                                    ▼
                                  Publish
                                    │
                                    ▼
                                 USERS
```

### 4.1 Fundamental Architectural Rule

**All source formats must converge into one canonical source representation before story understanding.**

This prevents the AI pipeline from developing separate logic for video, web, PDF, EPUB, subtitle, and text inputs.

---

# 5. Source Ingestion Requirements

## 5.1 Supported Initial Source Types

| Source | MVP | Future |
|---|---:|---:|
| TXT | Yes | — |
| Markdown | Yes | — |
| PDF | Yes | — |
| EPUB | Yes | — |
| SRT | Yes | — |
| VTT | Yes | — |
| Web page | Yes | — |
| Audio | Optional | Yes |
| Video | Limited/experimental | Yes |
| DOCX | Optional | Yes |
| YouTube/API-based licensed import | No | Yes |

## 5.2 Source Adapter Architecture

Each adapter shall implement a common contract:

```text
SourceAdapter
 ├── TextAdapter
 ├── MarkdownAdapter
 ├── PDFAdapter
 ├── EPUBAdapter
 ├── SubtitleAdapter
 ├── WebAdapter
 ├── AudioAdapter
 └── VideoAdapter
```

Each adapter shall output a `CanonicalSource` artifact.

### Required Adapter Responsibilities

- Validate the input.
- Identify language when possible.
- Extract the content.
- Preserve source ordering.
- Preserve provenance.
- Preserve timestamps where applicable.
- Preserve chapter/page/scene references where available.
- Normalize encoding and whitespace.
- Remove non-content boilerplate.
- Calculate source checksum/hash.
- Report extraction quality and warnings.

---

# 6. Canonical Source Representation

JSON shall be the primary machine-readable interchange format between pipeline stages.

A canonical source is not required to look identical for every source, but the same schema contract shall be maintained.

## 6.1 Example

```json
{
  "schema_version": "1.0",
  "source": {
    "id": "source_001",
    "type": "video",
    "title": "Example Story",
    "language": "en",
    "rights": {
      "type": "public_domain",
      "verified": true
    }
  },
  "segments": [
    {
      "id": "seg_001",
      "sequence": 1,
      "chapter": "Chapter 1",
      "scene_id": "scene_001",
      "start_ms": 0,
      "end_ms": 15400,
      "speaker": null,
      "text": "...",
      "source_ref": {
        "page": null,
        "url": null
      }
    }
  ]
}
```

## 6.2 Source-Specific Extensions

Video may contain:

```json
{
  "visual_events": [
    {
      "id": "ve_001",
      "timestamp_ms": 520000,
      "description": "Character A gives Character B a ring"
    }
  ]
}
```

Text sources may contain:

```json
{
  "chapter": "Chapter 4",
  "paragraph_index": 12
}
```

The downstream story pipeline shall not depend on the original file format.

---

# 7. Recommended Ingestion Technologies

## 7.1 Text / Markdown

- Python standard parsing and controlled normalization.

## 7.2 PDF

- **PyMuPDF** for text extraction.
- OCR shall only be invoked for scanned/image-based documents or poor extraction quality.

## 7.3 EPUB

- EPUB/HTML parsing libraries.
- Preserve chapter hierarchy.

## 7.4 Web

- `trafilatura` or equivalent main-content extraction.
- Playwright only where JavaScript rendering is necessary.
- Store original URL and retrieval timestamp.

## 7.5 SRT/VTT

- Dedicated subtitle parsers.
- Merge excessively fragmented subtitle entries where appropriate.
- Preserve timestamps.

## 7.6 Audio/Video

- **FFmpeg** for media extraction and normalization.
- **faster-whisper** for speech-to-text.
- **pyannote.audio** for speaker diarization when needed.
- **PySceneDetect** for scene boundaries.
- Vision-language model processing only on selected representative frames/scenes initially.

---

# 8. Story Understanding Pipeline

Once a `CanonicalSource` exists, all source types enter the same pipeline.

```text
CanonicalSource
      ↓
Chunking
      ↓
Entity Extraction
      ↓
Event Extraction
      ↓
Relationship Extraction
      ↓
Timeline Construction
      ↓
Causality Detection
      ↓
Importance Scoring
      ↓
Story Graph
```

## 8.1 Chunking

Requirements:

- Chunks shall respect chapter/scene boundaries where possible.
- Chunk overlap shall be configurable.
- Chunk identifiers shall be deterministic.
- Chunk-to-source provenance shall be preserved.

## 8.2 Entity Extraction

The system shall identify, where applicable:

- Characters.
- Locations.
- Organizations/groups.
- Objects.
- Concepts relevant to the plot.

Entities shall support aliases and references to source segments.

## 8.3 Event Extraction

Each meaningful event should capture:

- Event ID.
- Description.
- Participants.
- Location.
- Approximate chronology.
- Source references.
- Importance score.
- Dependencies.

## 8.4 Relationship Extraction

Examples:

- family_of
- friend_of
- enemy_of
- loyal_to
- works_for
- loves
- betrays
- parent_of
- sibling_of
- mentor_of

Relationships must preserve source references where feasible.

## 8.5 Timeline

The system shall represent:

- Source chronology.
- Story chronology when different.
- Flashbacks.
- Time jumps.
- Parallel events where detectable.

## 8.6 Causality

The system should identify dependencies such as:

```text
Event A → causes → Event B
Event B → enables → Event C
```

Causality shall be considered during compression so that removing an upstream event does not make a downstream event unintelligible.

---

# 9. Story Graph

The Story Graph is the platform's canonical semantic model of a story.

It shall contain at minimum:

```text
Story
 ├── Entities
 │    ├── Characters
 │    ├── Locations
 │    ├── Groups
 │    └── Objects
 │
 ├── Events
 ├── Relationships
 ├── Timeline
 ├── Causal Links
 └── Importance Scores
```

## 9.1 Why Story Graphs Are Required

A direct summarization approach is insufficient for long/complex stories because it may:

- Remove necessary setup.
- Lose character identities.
- Break causal relationships.
- Change chronology.
- Spoil information unintentionally.
- Produce inconsistent versions between languages.

The Story Graph becomes the shared source of truth for all narrative versions.

---

# 10. AI Model Architecture

## 10.1 Model Provider Abstraction

AI systems shall be accessed through provider interfaces rather than hard-coded vendor APIs.

Example:

```text
LLMProvider
 ├── OllamaProvider
 ├── VLLMProvider
 ├── OpenAIProvider
 └── OtherProvider
```

Similarly:

```text
TTSProvider
 ├── PiperProvider
 ├── CoquiProvider
 └── CommercialProvider
```

This is required to avoid vendor/model lock-in.

## 10.2 LLM Requirements

The LLM shall support:

- Structured JSON output where possible.
- Long-context processing or controlled chunking.
- Multilingual generation.
- Instruction following.
- Repeatable low-temperature extraction where deterministic behavior is desirable.

### Recommended Initial Approach

Use a strong multilingual open instruct model through **Ollama** for development and experimentation.

For future higher-throughput deployment, evaluate **vLLM**.

The precise model shall remain configurable and shall be selected through benchmark results rather than permanently hard-coded.

## 10.3 Vision Model

For video sources, a vision-language model may analyze selected frames/scene representatives to capture important non-dialogue information.

The system should initially avoid frame-by-frame vision inference because of cost and latency.

A suitable open VLM family such as **Qwen-VL** may be evaluated for this role.

---

# 11. Importance Scoring

Each event should receive an importance score based on a combination of:

```text
Importance =
    Plot Relevance
  + Character Relevance
  + Causal Relevance
  + Emotional Relevance
  + Future Dependency
  + Mystery/Twist Relevance
```

The exact weighting shall be configurable and experimentally validated.

The system should support normalized scores such as `0.0–1.0`.

High-importance events should be difficult for the compression engine to remove.

---

# 12. Narrative Compression Engine

## 12.1 Objective

Produce a shorter narrative while preserving enough information for the selected target experience to remain coherent.

## 12.2 Target Durations

Initial presets:

- Quick: 3–7 minutes.
- Standard: 10–20 minutes.
- Complete: 30–60+ minutes.

A custom target duration may be supported later.

## 12.3 Compression Architecture

```text
Story Graph
    ↓
Target Duration
    ↓
Required Events
    ↓
Optional Events
    ↓
Narrative Ordering
    ↓
Narrative Blueprint
    ↓
Canonical Story
```

## 12.4 Narrative Blueprint

The planner shall produce structured output containing:

- Ordered sections.
- Required events.
- Selected characters.
- Required facts.
- Emotional progression.
- Spoiler boundaries.
- Ending state.
- Target duration.

## 12.5 Canonical Story

The canonical story is the approved master narrative before language-specific localization.

All language versions shall derive from the canonical story rather than independently summarizing the original source.

This prevents large semantic drift between languages.

---

# 13. Localization Pipeline

Localization shall occur **after narrative compression**.

Correct sequence:

```text
Source
 ↓
Story Graph
 ↓
Narrative Compression
 ↓
Canonical Story
 ↓
Localization
 ↓
TTS
```

Incorrect sequence to avoid:

```text
Source
 ↓
Translate everything
 ↓
Summarize translated content
```

The latter wastes compute and increases semantic drift.

## 13.1 Localization Requirements

Localization must preserve:

- Story facts.
- Character identity.
- Chronology.
- Causality.
- Key relationships.
- Required plot events.
- Spoiler policy.

Localization may change:

- Sentence structure.
- Idiomatic phrasing.
- Narrative rhythm.
- Local-language storytelling style.

## 13.2 Indian Language Support

Initial target languages should be selected from measurable user demand.

The platform shall evaluate multilingual LLMs and Indian-language models such as **IndicTrans2/AI4Bharat** models against real StoryBridge content.

No model shall be considered production-ready until it passes automated and human quality benchmarks.

---

# 14. TTS Pipeline

## 14.1 TTS Requirements

TTS shall support:

- Language selection.
- Voice selection.
- Configurable speaking rate.
- Chapter-level generation.
- Repeatable regeneration.

## 14.2 Recommended Initial Engine

**Piper** is recommended for the first local/open-source implementation where compatible voices are available.

A provider abstraction shall allow replacement or addition of other TTS engines later.

## 14.3 Audio Generation Strategy

Audio shall be generated chapter-by-chapter rather than as one giant file.

Advantages:

- Retry failed chapters.
- Replace a corrected chapter without regenerating everything.
- Stream progressively.
- Support chapter navigation.
- Parallelize generation.

---

# 15. Automated Quality Assurance

Every major stage shall perform automatic validation.

## 15.1 Source QA

Check:

- File integrity.
- Extraction success.
- Empty/low-quality segments.
- Language detection.
- Duplicate content.
- Missing chapters/pages/scenes.

## 15.2 Story QA

Check:

- Character consistency.
- Required event inclusion.
- Chronology conflicts.
- Unsupported facts.
- Broken causal chains.
- Excessive hallucination.

## 15.3 Localization QA

Check:

- Missing entities.
- Changed names.
- Changed numbers/dates.
- Changed relationships.
- Added unsupported facts.
- Translation completeness.
- Target language correctness.
- Estimated duration.

## 15.4 Audio QA

Check:

- Empty audio.
- Duration mismatch.
- Excessive silence.
- Clipping.
- File corruption.
- Chapter ordering.
- Optional pronunciation checks.

---

# 16. Human Approval Workflow

The platform shall use a state-machine workflow.

```text
IMPORTED
   ↓
NORMALIZED
   ↓
UNDERSTANDING_READY
   ↓
UNDERSTORY_REVIEW
   ↓
STORY_APPROVED
   ↓
NARRATIVE_GENERATED
   ↓
NARRATIVE_APPROVED
   ↓
LOCALIZATION_GENERATED
   ↓
LOCALIZATION_APPROVED
   ↓
AUDIO_GENERATED
   ↓
AUDIO_APPROVED
   ↓
PUBLISHED
```

Any stage may transition to:

- `FAILED`
- `REJECTED`
- `REVISION_REQUIRED`

## 16.1 Human-in-the-Loop Principle

The initial system shall require human approval for publication.

Over time, automation may replace some approval gates when confidence thresholds are demonstrably reliable.

The system should never require a human to manually edit every generated artifact at scale; humans should focus on exceptions and quality-control decisions.

---

# 17. Versioning and Provenance

Every generated artifact shall be immutable once published and shall have a version.

Example:

```text
canonical_story_v3
hindi_script_v2
marathi_script_v5
audio_hi_standard_v1
```

Each artifact shall record:

- Source artifact ID.
- Parent artifact ID.
- Schema version.
- Model provider.
- Model identifier.
- Prompt version.
- Generation parameters where relevant.
- Creation timestamp.
- Approval metadata.

This allows reproducibility and rollback.

---

# 18. Artifact Storage Structure

A logical artifact tree shall resemble:

```text
story_001/
├── source/
│   ├── raw/
│   ├── metadata.json
│   └── rights.json
│
├── normalized/
│   ├── transcript.json
│   └── segments.json
│
├── understanding/
│   ├── entities.json
│   ├── events.json
│   ├── relations.json
│   ├── timeline.json
│   └── story_graph.json
│
├── narrative/
│   ├── quick.json
│   ├── standard.json
│   └── complete.json
│
├── localization/
│   ├── hi/
│   │   ├── script.json
│   │   └── qa.json
│   └── mr/
│       ├── script.json
│       └── qa.json
│
└── audio/
    ├── hi/
    │   └── standard/
    │       ├── ch01.wav
    │       └── ch02.wav
    └── mr/
```

Object storage shall hold large/raw artifacts; PostgreSQL shall hold metadata and queryable entities.

---

# 19. User-Facing Features

## 19.1 Home

The homepage shall communicate the value proposition immediately:

> **Understand every story — in your language, in your time.**

Functions:

- Search.
- Featured stories.
- Categories.
- Languages.
- Duration-based discovery.

## 19.2 Search

Search shall support:

- Title.
- Character.
- Genre/category.
- Language.
- Semantic query where supported.

Example:

> `warrior abandoned by his mother`

may return a semantically related story.

## 19.3 Story Page

A story page shall provide:

- Title.
- Description.
- Source/rights information where appropriate.
- Available languages.
- Available durations.
- Chapters.
- Play button.
- Bookmark.
- Story Graph entry points.

## 19.4 Duration Selection

The UI should make time control prominent:

```text
How much time do you have?

5m ───────●──────── 60m
```

Preset durations shall be available in MVP.

## 19.5 Story Player

The player shall support:

- Play/pause.
- Seek.
- Chapter navigation.
- Playback speed.
- Language selection when already generated.
- Current story progress.
- Continue listening.
.

## 19.6 Story Map / Character Explorer

Users should be able to inspect:

- Characters.
- Relationships.
- Important events.
- Locations.

This feature may be MVP+ depending on implementation effort.

## 19.7 Ask the Story

A story-grounded question-answering feature should answer questions using the story graph and canonical narrative rather than unrestricted general LLM knowledge.

Examples:

- Why did Karna support Duryodhana?
- Who killed Bhishma?
- What happened before the war?

## 19.8 Spoiler Control

Where supported, users may select:

- No/limited spoilers.
- Current story position.
- Full-story knowledge.

## 19.9 User Account

Authentication is optional for basic listening.

Unauthenticated users may:

- Browse.
- Search.
- Listen.

Accounts provide:

- History.
- Bookmarks.
- Playlists.
- Personalized recommendations.
.

---

# 20. Administration and CMS

The admin panel shall support:

### Content

- Create/import story.
- Upload source.
- Edit metadata.
- Set categories.
- Set languages.
- Set publication status.

### Rights

- Set rights type.
- Upload rights evidence where required.
- Record verification status.
- Prevent publication when rights are unverified.

### Pipeline

- View job state.
- Retry failed jobs.
- Cancel jobs.
- View artifacts.
- View model/prompt versions.

### Review

- Review extracted characters/events.
- Approve/reject story graph.
- Review narrative versions.
- Review localized scripts.
- Review audio.

### Publishing

- Publish/unpublish.
- Schedule future publication if required.
- Roll back to a previous approved version.

---

# 21. Backend Architecture

## 21.1 Recommended Backend

- **Java 21**
- **Spring Boot**
- Spring Security
- REST APIs
- Optional SSE/WebSocket for job progress

Core modules:

```text
backend/
├── auth
├── users
├── stories
├── sources
├── rights
├── workflow
├── approvals
├── jobs
├── catalog
├── recommendations
└── analytics
```

## 21.2 AI Service

- **Python**
- **FastAPI**
- PyTorch/Transformers ecosystem

Modules:

```text
ai-engine/
├── ingestion
├── normalization
├── extraction
├── storygraph
├── compression
├── localization
├── tts
└── qa
```

The backend shall not directly implement heavy AI/media processing.

---

# 22. Recommended Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React + TypeScript | Mature, fast web development, extensible to React Native |
| Styling | Tailwind CSS | Rapid consistent UI |
| Backend | Java 21 + Spring Boot | Strong fit for transactional/API-heavy platform and existing skillset |
| AI service | Python + FastAPI | AI/ML ecosystem and asynchronous workers |
| LLM dev serving | Ollama | Simple local experimentation and model switching |
| LLM production serving | vLLM evaluation | Better throughput/concurrency for model serving |
| ASR | faster-whisper | Local timestamped transcription |
| Diarization | pyannote.audio | Speaker separation for audio/video |
| Scene detection | PySceneDetect | Useful video segmentation |
| Vision | Qwen-VL family or equivalent | Open multimodal analysis for selected frames |
| Localization | Multilingual LLM + IndicTrans2/AI4Bharat evaluation | Regional-language support and native adaptation |
| TTS | Piper initially | Local/open architecture and low operating cost |
| Database | PostgreSQL | Strong relational model for stories/workflows/users |
| Vector search | pgvector | Semantic retrieval without a separate vector database initially |
| Cache | Valkey | Caching, rate limiting, transient state |
| Queue | RabbitMQ | Reliable asynchronous pipeline jobs |
| Storage | S3 / MinIO | Large artifact/audio/media storage |
| Media | FFmpeg | Media conversion and assembly |
| Reverse proxy | Nginx | TLS, routing, static/media delivery |
| Containers | Docker | Reproducible deployment |
| CI/CD | GitHub Actions | Automated build/test/deploy |
| Monitoring | Prometheus + Grafana | System and worker observability |

---

# 23. Asynchronous Processing Architecture

Pipeline operations shall not run as long synchronous HTTP requests.

Example:

```text
POST /sources/{id}/process
          ↓
       job_id
          ↓
       RabbitMQ
          ↓
   ┌──────┼────────┐
   ▼      ▼        ▼
Ingest  Story    Media
Worker  Worker   Worker
```

The system shall support:

- Idempotent jobs.
- Retries.
- Dead-letter handling.
- Job cancellation where safe.
- Progress reporting.
- Per-stage logging.

---

# 24. Database Requirements

PostgreSQL shall contain at minimum:

```text
users
stories
story_versions
sources
source_versions
rights_records
segments
characters
entities
events
relationships
story_graph_versions
narrative_versions
localizations
languages
voices
audio_assets
pipeline_jobs
approval_records
bookmarks
listening_history
```

## 24.1 Semantic Search

pgvector shall store embeddings for selected content such as:

- Stories.
- Events.
- Characters.
- Chapters.
- Searchable narrative segments.

Embeddings shall be versioned because embedding models can change.

---

# 25. Storage Requirements

Large binaries shall not be stored directly in PostgreSQL.

Object storage shall hold:

- Raw documents.
- Raw audio/video.
- Extracted media.
- JSON artifacts.
- Generated audio.
- Optional generated video.
- Thumbnails.

All object references shall use stable internal identifiers rather than exposing arbitrary internal filesystem paths.

---

# 26. API Requirements

Representative APIs:

### Public

```text
GET    /api/stories
GET    /api/stories/{id}
GET    /api/stories/{id}/versions
GET    /api/stories/{id}/languages
GET    /api/stories/{id}/narratives
GET    /api/search?q=...
GET    /api/stories/{id}/chapters
```

### User

```text
POST   /api/auth/register
POST   /api/auth/login
GET    /api/me/history
POST   /api/me/bookmarks
DELETE /api/me/bookmarks/{storyId}
```

### Admin

```text
POST   /api/admin/sources
POST   /api/admin/stories
POST   /api/admin/jobs
POST   /api/admin/jobs/{id}/retry
POST   /api/admin/approvals/{id}
POST   /api/admin/stories/{id}/publish
POST   /api/admin/stories/{id}/unpublish
```

The API contract shall use versioned schemas.

---

# 27. Security Requirements

The system shall:

- Use HTTPS in production.
- Use secure password hashing.
- Use JWT or secure session-based authentication.
- Enforce role-based access control.
- Restrict administrative endpoints.
- Validate uploaded files.
- Enforce file size/type limits.
- Sandbox media processing jobs where appropriate.
- Prevent arbitrary command execution through uploaded media metadata.
- Protect internal object storage.
- Rate-limit public APIs.
- Rate-limit costly AI operations.
- Audit administrative actions.

Roles should initially include:

```text
USER
ADMIN
REVIEWER
```

A future granular permission model may be added.

---

# 28. Content Rights Requirements

Each source shall contain a rights record.

Example categories:

```text
PUBLIC_DOMAIN
OPEN_LICENSE
ORIGINAL
LICENSED
UNKNOWN
RESTRICTED
```

Rules:

1. `UNKNOWN` shall not be publishable.
2. `RESTRICTED` shall not be publishable.
3. Publication shall require a verified rights state.
4. The system shall retain source provenance.
5. Rights metadata shall be visible to admins.
6. Rights changes shall be versioned/audited.

The platform shall not automatically treat internet availability as permission to process or redistribute content.

---

# 29. Quality Requirements

## 29.1 Story Quality

The system should target:

- High character consistency.
- High event coverage for important events.
- Minimal invented facts.
- Causal coherence.
- Chronological consistency.
- Appropriate narrative pacing.

Automated metrics should be supplemented by human evaluation.

## 29.2 Localization Quality

Quality evaluations should include:

- Semantic fidelity.
- Naturalness.
- Grammar.
- Name preservation.
- Cultural appropriateness.
- TTS pronunciation.

## 29.3 TTS Quality

Evaluate:

- Intelligibility.
- Pronunciation.
- Prosody.
- Pacing.
- Voice consistency.

---

# 30. Non-Functional Requirements

## 30.1 Scalability

The architecture shall allow AI workers to scale horizontally without modifying the core API service.

Target architecture:

```text
API instances: horizontally scalable
AI workers: horizontally scalable
TTS workers: horizontally scalable
Media workers: horizontally scalable
```

## 30.2 Reliability

Pipeline jobs shall be retryable and idempotent.

A failure in one language shall not invalidate already-approved versions in another language.

Example:

```text
Hindi generation FAILED

Marathi APPROVED
Tamil APPROVED
```

The story remains partially publishable according to product policy.

## 30.3 Performance

Typical browsing/API requests should target sub-second response times where cached data is available.

AI generation is asynchronous and shall not be treated as a synchronous latency requirement.

## 30.4 Observability

Logs shall include:

- Request ID.
- Story ID.
- Artifact ID.
- Job ID.
- Worker ID.
- Model/version.
- Processing duration.
- Failure reason.

Metrics should include:

- Jobs processed.
- Job failures.
- Average processing duration.
- AI inference time.
- TTS duration.
- Queue depth.
- API latency.
- Playback errors.
.

---

# 31. Caching Strategy

Generated content should generally be generated once and reused.

For example:

```text
Mahabharata
 └── Marathi
      └── Standard
           └── Approved Audio
```

10,000 users should not trigger 10,000 TTS generations.

The system shall cache/reference approved artifacts by content version + language + narrative version + voice configuration.

---

# 32. Cost-Control Requirements

The system shall minimize expensive model calls through:

- Deterministic parsing before LLM usage.
- Chunk-level processing.
- Reuse of Story Graph outputs.
- Canonical narrative reuse across languages.
- Artifact caching.
- Chapter-level regeneration.
- Queue-based batch processing.
- Local models where operationally practical.
- Selective vision-model usage.

---

# 33. Content Delivery and Ads

The public platform shall be free to users in the initial business model.

Potential monetization:

- Display advertising.
- Audio/video advertising.
- Sponsorships in later stages.

Advertising must not block the core storytelling experience excessively.

Ads shall not be inserted into internally generated narration unless explicitly designed and tested as part of the product experience.

---

# 34. Recommended MVP Scope

## MVP 1

### Inputs

- TXT/Markdown.
- PDF.
- EPUB.
- SRT/VTT.
- Selected web pages.

### Content

- Public-domain stories.
- Openly licensed stories.
- Original stories.

### Languages

- English.
- Hindi.
- Marathi.

### Story Durations

- Quick.
- Standard.
- Complete.

### User Features

- Search.
- Browse categories.
- Story page.
- Language selection.
- Duration selection.
- Audio player.
- History.
- Bookmarks.

### Admin Features

- Import source.
- Rights metadata.
- Pipeline status.
- Story graph review.
- Narrative review.
- Localization review.
- Audio review.
- Publish/unpublish.

---

# 35. MVP-Plus

Add:

- Story Graph visualization.
- Ask the Story.
- Spoiler control.
- Semantic search.
- Better recommendations.
- Tamil/Telugu/Bengali or other demand-driven languages.
- Audio analytics.
- More TTS voice choices.

---

# 36. Future Product Expansion

Once the pipeline is validated:

```text
Public Domain
      ↓
Open License
      ↓
Original Stories
      ↓
Creator Partnerships
      ↓
Licensed Books
      ↓
Licensed Series
      ↓
Licensed Movies
      ↓
Licensed Anime
```

Future source types:

- Audiobooks.
- Movies.
- Series episodes.
- Anime.
- Creator videos.
- Web novels.
- Interactive stories.

Future experiences:

- Character-specific stories.
- Arc-specific stories.
- Relationship explainers.
- Event explainers.
- "Continue from here" for series.
- Personalized compression.
- User-controlled storytelling depth.

---

# 37. Acceptance Criteria for the Core Pipeline

A core MVP implementation is successful when the system can:

1. Accept a permitted text/PDF/EPUB/web source.
2. Normalize the source into the canonical schema.
3. Preserve source provenance.
4. Build a story graph containing meaningful entities/events/relationships.
5. Identify important story events.
6. Generate a narrative blueprint for multiple target durations.
7. Generate one approved canonical narrative.
8. Generate Hindi and Marathi localized versions from the canonical narrative.
9. Validate that important story facts remain consistent across languages.
10. Generate chapter-level TTS audio.
11. Allow administrator review before publication.
12. Publish an approved version for public playback.
13. Re-run only failed/rejected stages without rebuilding unrelated artifacts.
14. Maintain version and model/prompt provenance.

---

# 38. Example End-to-End Processing Scenario

Source:

> Public-domain EPUB containing a mythology story.

### Step 1 — Import

Admin uploads EPUB and records rights as `PUBLIC_DOMAIN`.

### Step 2 — Normalize

EPUB adapter extracts chapters and paragraphs into `CanonicalSource`.

### Step 3 — Understanding

Workers extract entities, events, relationships, chronology, and causal links.

### Step 4 — Story Graph

The resulting semantic graph is stored and reviewed.

### Step 5 — Compression

The planner generates:

- Quick version.
- Standard version.
- Complete version.

### Step 6 — Canonical Story

A master narrative is generated and approved.

### Step 7 — Localization

The canonical story is adapted into:

- Hindi.
- Marathi.

### Step 8 — Language QA

The system compares required entities/events/facts against the canonical version.

### Step 9 — TTS

Each language is synthesized chapter-by-chapter.

### Step 10 — Audio QA

Files are checked and reviewed.

### Step 11 — Publish

Only approved versions become publicly playable.

---

# 39. Engineering Principles

The project shall follow these principles:

### 39.1 Format Agnostic Downstream Processing

Only ingestion knows whether the source was a video, PDF, EPUB, web page, or subtitle file.

### 39.2 Canonical Representation Before AI Reasoning

AI reasoning should operate on normalized, structured data rather than raw heterogeneous inputs whenever possible.

### 39.3 Story Graph Before Compression

Complex stories should not be directly summarized without structured semantic understanding.

### 39.4 Compress Before Localize

Do not translate content that the compression stage will later discard.

### 39.5 Localize Before TTS

Audio should always be generated from an approved localized script.

### 39.6 Human Approval Before Public Release

AI-generated content shall not automatically become public during the early stages of the project.

### 39.7 Version Everything Important

Models, prompts, schemas, scripts, story graphs, audio assets, and approvals shall be versioned.

### 39.8 Cache Generated Content

Approved artifacts must be reused across users.

### 39.9 Prefer Open/Local AI Where Practical

The architecture should avoid unavoidable dependency on one proprietary AI provider.

### 39.10 Start Simple

The initial implementation should use a modular monolith plus separate AI/worker processes rather than prematurely creating many microservices.

---

# 40. Proposed Repository Structure

```text
storybridge/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── src/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── stories/
│   │   ├── sources/
│   │   ├── rights/
│   │   ├── workflow/
│   │   ├── approvals/
│   │   ├── jobs/
│   │   └── analytics/
│   └── pom.xml
│
├── ai-engine/
│   ├── ingestion/
│   ├── normalization/
│   ├── extraction/
│   ├── storygraph/
│   ├── compression/
│   ├── localization/
│   ├── tts/
│   ├── qa/
│   └── requirements.txt
│
├── workers/
│   ├── ingestion-worker/
│   ├── story-worker/
│   ├── localization-worker/
│   ├── tts-worker/
│   └── media-worker/
│
├── shared/
│   ├── schemas/
│   ├── prompts/
│   └── test-fixtures/
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   ├── postgres/
│   ├── rabbitmq/
│   └── monitoring/
│
└── docs/
    ├── architecture/
    ├── api/
    ├── ai/
    └── content-rights/
```

---

# 41. Development Phases

## Phase 0 — AI Proof of Concept

Goal:

> Prove that StoryBridge can create a coherent shortened story.

Build only:

```text
Text
 ↓
Story Graph
 ↓
5/15/30 min narrative
 ↓
Hindi/Marathi localization
 ↓
Piper TTS
```

No public website required beyond a basic test UI/CLI.

## Phase 1 — Core Platform

Add:

- Spring Boot backend.
- React frontend.
- PostgreSQL.
- Authentication.
- Admin CMS.
- Artifact/version system.
- RabbitMQ.
- MinIO.

## Phase 2 — Content Pipeline

Add:

- PDF.
- EPUB.
- SRT/VTT.
- Web ingestion.
- Automated QA.

## Phase 3 — Consumer Product

Add:

- Search.
- Player.
- History.
- Bookmarks.
- Story Graph exploration.
- Semantic search.

## Phase 4 — Audio/Video Sources

Add:

- Whisper.
- Speaker diarization.
- Scene detection.
- Selected-frame VLM analysis.

## Phase 5 — Scale and Content Partnerships

Add:

- More languages.
- Creator licensing.
- Commercial rights management.
- Larger worker pool.
- CDN optimization.
- Recommendation engine.

---

# 42. Key Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| AI hallucination | High | Story graph + source grounding + QA |
| Bad compression | High | Event importance + causal dependency modelling |
| Language drift | High | Canonical story + cross-language QA |
| Poor TTS pronunciation | Medium/High | Voice evaluation + pronunciation dictionaries |
| Copyright/rights failure | Critical | Rights metadata + verification gate |
| AI provider changes | Medium | Provider abstraction |
| Generation cost | High | Caching + local models + asynchronous jobs |
| Pipeline fragility | High | Versioned artifacts + idempotent stages |
| Video processing cost | High | Selective scene/frame processing |
| Poor user retention | Critical | Validate Story Mode usefulness before scaling content |

---

# 43. Final System Blueprint

The intended long-term system can be summarized as:

```text
                        SOURCE
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
      Text             Document           Media
       │                  │                  │
       ├── TXT/MD        ├── PDF            ├── Audio
       ├── Web           └── EPUB           └── Video
       │                                      │
       └──────────────────┬───────────────────┘
                          ▼
                   SOURCE ADAPTERS
                          │
                          ▼
                 CANONICAL SOURCE
                          │
                          ▼
                  STORY UNDERSTANDING
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
      ENTITIES          EVENTS        RELATIONSHIPS
          └───────────────┼────────────────┘
                          ▼
                     STORY GRAPH
                          │
                          ▼
                IMPORTANCE / CAUSALITY
                          │
                          ▼
                 NARRATIVE PLANNER
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
            5m           15m          30m+
             └────────────┼────────────┘
                          ▼
                   CANONICAL STORY
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
      HINDI            MARATHI             TAMIL
        │                 │                  │
        ▼                 ▼                  ▼
   LANGUAGE QA       LANGUAGE QA       LANGUAGE QA
        │                 │                  │
        └─────────────────┼──────────────────┘
                          ▼
                         TTS
                          │
                          ▼
                      AUDIO QA
                          │
                          ▼
                       PUBLISH
                          │
                          ▼
                    STORY PLAYER
```

---

# 44. Conclusion

StoryBridge should be implemented as a **pipeline-driven story intelligence platform**, not as a collection of independent AI features.

The most important architectural decisions are:

1. **Normalize every source type into one canonical representation.**
2. **Build a Story Graph before compressing the story.**
3. **Generate one canonical narrative before localization.**
4. **Localize naturally rather than performing literal translation.**
5. **Generate TTS only after script approval.**
6. **Represent every stage as a versioned, retryable artifact.**
7. **Use asynchronous workers for expensive AI/media processing.**
8. **Keep source rights explicit and block publishing when rights are unverified.**
9. **Cache approved generated content so users do not trigger repeated AI costs.**
10. **Begin with public-domain, open-license, original, and explicitly licensed content; expand into commercial entertainment only after rights and business relationships are established.**

The first technical milestone is therefore not the consumer website. It is a reliable proof that the pipeline can take one legally usable story and produce **coherent 5-, 15-, and 30-minute narratives in multiple languages with minimal semantic drift**. Once that works consistently, the web platform becomes the delivery layer around a proven Story Intelligence Engine.

---

**End of SRS — StoryBridge v2.0**
