from __future__ import annotations
import asyncio
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from pipeline import StoryBridgePipeline
from providers.llm import get_llm_provider
from providers.tts import get_tts_provider
from schemas.canonical import (
    AudioAsset,
    CanonicalSource,
    CanonicalStory,
    LocalizedScript,
    NarrativeBlueprint,
    RightsRecord,
    StoryGraph,
)

app = FastAPI(
    title="StoryBridge AI Engine API",
    version="2.0.0",
    description="Story Understanding, Compression, Localization, and TTS synthesis engine for StoryBridge",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = StoryBridgePipeline()

# In-memory job registry for async jobs
jobs: Dict[str, dict] = {}


class IngestRequest(BaseModel):
    story_id: str
    title: str
    author: Optional[str] = None
    language: str = "en"
    content_or_path: str
    rights: Optional[RightsRecord] = None


class ExtractGraphRequest(BaseModel):
    canonical_source: CanonicalSource


class CompressRequest(BaseModel):
    story_graph: StoryGraph
    duration_presets: List[str] = Field(default_factory=lambda: ["quick", "standard"])


class LocalizeRequest(BaseModel):
    canonical_story: CanonicalStory
    story_graph: StoryGraph
    target_languages: List[str] = Field(default_factory=lambda: ["hi", "mr"])


class SynthesizeAudioRequest(BaseModel):
    localized_scripts: Dict[str, LocalizedScript]
    voice_map: Optional[Dict[str, str]] = None


class RunPipelineRequest(BaseModel):
    story_id: str = Field(default_factory=lambda: f"story_{uuid.uuid4().hex[:8]}")
    title: str = "Untitled Story"
    author: Optional[str] = "Unknown"
    content_or_path: str = ""
    rights: Optional[RightsRecord] = None
    duration_presets: List[str] = Field(default_factory=lambda: ["quick", "standard"])
    languages: List[str] = Field(default_factory=lambda: ["hi", "mr"])


@app.get("/api/v1/health")
def health_check():
    has_key = bool(settings.NVIDIA_API_KEY and settings.NVIDIA_API_KEY != "your_nvidia_nim_api_key_here")
    return {
        "status": "healthy",
        "service": "StoryBridge AI Engine",
        "llm_provider": settings.LLM_PROVIDER,
        "nim_model": settings.NIM_MODEL_NAME,
        "nim_key_configured": has_key,
        "tts_provider": settings.TTS_PROVIDER,
        "supported_languages": settings.SUPPORTED_LANGUAGES,
    }


@app.post("/api/v1/ingest", response_model=CanonicalSource)
def ingest_source(req: IngestRequest):
    try:
        return pipeline.stage_ingest(
            source_path_or_content=req.content_or_path,
            title=req.title,
            story_id=req.story_id,
            language=req.language,
            author=req.author,
            rights=req.rights,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/extract-graph", response_model=StoryGraph)
def extract_story_graph(req: ExtractGraphRequest):
    try:
        return pipeline.stage_understand(req.canonical_source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/compress", response_model=Dict[str, CanonicalStory])
def compress_narrative(req: CompressRequest):
    try:
        return pipeline.stage_compress(req.story_graph, presets=req.duration_presets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/localize", response_model=Dict[str, LocalizedScript])
def localize_story(req: LocalizeRequest):
    try:
        return pipeline.stage_localize(
            canonical_story=req.canonical_story,
            story_graph=req.story_graph,
            languages=req.target_languages,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/synthesize-audio", response_model=Dict[str, AudioAsset])
async def synthesize_audio(req: SynthesizeAudioRequest):
    try:
        return await pipeline.stage_synthesize_audio(
            localized_scripts=req.localized_scripts,
            voice_map=req.voice_map,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _run_pipeline_task(job_id: str, req: RunPipelineRequest):
    try:
        jobs[job_id]["status"] = "PROCESSING"
        jobs[job_id]["step"] = "Executing Pipeline"
        result = await pipeline.run_full_pipeline(
            source_path_or_content=req.content_or_path,
            title=req.title,
            story_id=req.story_id,
            author=req.author,
            rights=req.rights,
            duration_presets=req.duration_presets,
            languages=req.languages,
        )
        jobs[job_id]["status"] = "COMPLETED"
        jobs[job_id]["result"] = {
            "story_id": result["story_id"],
            "title": result["title"],
            "total_words": result["canonical_source"].total_words,
            "entities_count": len(result["story_graph"].entities),
            "events_count": len(result["story_graph"].events),
            "presets_generated": list(result["canonical_stories"].keys()),
        }
    except Exception as e:
        jobs[job_id]["status"] = "FAILED"
        jobs[job_id]["error"] = str(e)


@app.post("/api/v1/pipeline/run")
async def trigger_pipeline_job(request: Request, background_tasks: BackgroundTasks):
    import logging
    app_logger = logging.getLogger("storybridge.app")

    raw_bytes = await request.body()
    raw_text = raw_bytes.decode("utf-8", errors="replace")
    
    body = {}
    if raw_text.strip():
        try:
            body = json.loads(raw_text)
            if isinstance(body, str):
                body = json.loads(body)
        except Exception as e:
            app_logger.warning(f"Failed to parse JSON body from raw text '{raw_text[:200]}': {e}")
            body = {}

    if not isinstance(body, dict):
        body = {}

    story_id = (
        body.get("story_id")
        or request.query_params.get("story_id")
        or f"story_{uuid.uuid4().hex[:8]}"
    )
    title = (
        body.get("title")
        or request.query_params.get("title")
        or "Untitled Story"
    )
    author = (
        body.get("author")
        or request.query_params.get("author")
        or "Unknown"
    )
    content_or_path = (
        body.get("content_or_path")
        or request.query_params.get("content_or_path")
        or ""
    )
    duration_presets = (
        body.get("duration_presets")
        or ["quick", "standard"]
    )
    languages = (
        body.get("languages")
        or ["hi", "mr"]
    )

    req = RunPipelineRequest(
        story_id=story_id,
        title=title,
        author=author,
        content_or_path=content_or_path,
        rights=body.get("rights"),
        duration_presets=duration_presets,
        languages=languages,
    )

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    jobs[job_id] = {
        "job_id": job_id,
        "story_id": req.story_id,
        "status": "QUEUED",
        "step": "Initializing",
    }
    app_logger.info(f"Triggering pipeline job {job_id} for story_id='{req.story_id}', title='{req.title}'")
    background_tasks.add_task(_run_pipeline_task, job_id, req)
    return {"job_id": job_id, "status": "QUEUED", "story_id": req.story_id}


@app.get("/api/v1/pipeline/jobs/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.AI_ENGINE_HOST, port=settings.AI_ENGINE_PORT)
