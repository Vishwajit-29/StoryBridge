from __future__ import annotations
import asyncio
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict

from config import settings


def clean_storytelling_text(text: str) -> str:
    """
    Cleans narrative text so that NO XML tags, metadata, or JSON keys are spoken.
    Ensures natural punctuation and paragraph pauses for expressive storytelling.
    """
    if not text:
        return ""

    # Strip any accidental HTML or XML tags (e.g. <break...>, <speak...>)
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalize paragraph breaks to clean double newlines
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    cleaned = "\n\n".join(paragraphs)
    return cleaned.strip()


class TTSProvider(ABC):
    """
    Abstract Base Class for all StoryBridge TTS Synthesis Engines.
    Designed modularly to support Edge-TTS, Qwen-TTS / CosyVoice, OpenAI, ElevenLabs, etc.
    """

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        voice: Optional[str] = None,
        rate: str = "-4%",
    ) -> float:
        """
        Synthesize text to audio file at output_path.
        Returns: duration in seconds.
        """
        pass


class EdgeTTSProvider(TTSProvider):
    """
    Microsoft Edge Neural TTS Provider.
    Produces studio-grade 48kHz neural speech across Indian and global languages.
    """

    VOICE_MAP: Dict[str, str] = {
        "en": "en-IN-NeerjaNeural",         # Indian English Female Narrator
        "en-in-female": "en-IN-NeerjaNeural",
        "en-in-male": "en-IN-PrabhatNeural",# Indian English Male Narrator
        "en-us": "en-US-AvaMultilingualNeural",
        "hi": "hi-IN-SwaraNeural",          # Hindi Female Narrator
        "hi-male": "hi-IN-MadhurNeural",    # Hindi Male Narrator
        "mr": "mr-IN-AarohiNeural",         # Marathi Female Narrator
        "mr-male": "mr-IN-ManoharNeural",   # Marathi Male Narrator
        "ta": "ta-IN-PallaviNeural",        # Tamil
        "te": "te-IN-ShrutiNeural",         # Telugu
        "bn": "bn-IN-TanishaaNeural",       # Bengali
        "gu": "gu-IN-DhwaniNeural",         # Gujarati
        "kn": "kn-IN-SapnaNeural",          # Kannada
        "ml": "ml-IN-SobhanaNeural",        # Malayalam
    }

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        voice: Optional[str] = None,
        rate: str = "-4%",
    ) -> float:
        import edge_tts
        output_path.parent.mkdir(parents=True, exist_ok=True)
        selected_voice = voice or self.VOICE_MAP.get(language.lower(), "en-IN-NeerjaNeural")

        # Clean text completely: NO XML or metadata spoken
        clean_text = clean_storytelling_text(text)
        if not clean_text:
            clean_text = "Chapter."

        try:
            communicate = edge_tts.Communicate(text=clean_text, voice=selected_voice, rate=rate)
            await asyncio.wait_for(communicate.save(str(output_path)), timeout=30.0)
        except Exception:
            # Fallback to guaranteed valid MP3
            gtts_provider = GTTSSProvider()
            return await gtts_provider.synthesize(clean_text, output_path, language=language, voice=voice, rate=rate)

        words = len(clean_text.split())
        estimated_duration = max(2.0, (words / 2.16) + (clean_text.count("\n") * 0.5))
        return estimated_duration


class QwenTTSProvider(TTSProvider):
    """
    Modular Qwen TTS / CosyVoice Provider.
    Ready for integration with Qwen Audio / CosyVoice endpoints.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: str = "qwen-tts-cosyvoice",
    ):
        self.api_url = api_url or os.getenv("QWEN_TTS_URL", "http://localhost:9000/v1/audio/speech")
        self.api_key = api_key or os.getenv("QWEN_TTS_API_KEY", "")
        self.model_name = model_name

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        voice: Optional[str] = None,
        rate: str = "-4%",
    ) -> float:
        import urllib.request
        import json

        output_path.parent.mkdir(parents=True, exist_ok=True)
        clean_text = clean_storytelling_text(text)

        payload = {
            "model": self.model_name,
            "input": clean_text,
            "voice": voice or "storyteller_expressive",
            "language": language,
            "response_format": "mp3",
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                },
            )
            loop = asyncio.get_event_loop()

            def _do_request():
                with urllib.request.urlopen(req, timeout=30) as resp:
                    output_path.write_bytes(resp.read())

            await loop.run_in_executor(None, _do_request)
        except Exception:
            # Graceful fallback to EdgeTTS until Qwen server endpoint is configured
            fallback = EdgeTTSProvider()
            return await fallback.synthesize(clean_text, output_path, language=language, voice=voice, rate=rate)

        words = len(clean_text.split())
        return max(2.0, words / 2.16)


class OpenAITTSProvider(TTSProvider):
    """
    OpenAI Studio TTS Provider (tts-1-hd).
    Supports voices: fable (storytelling), alloy, echo, onyx, nova, shimmer.
    """

    VOICE_MAP: Dict[str, str] = {
        "en": "fable",
        "hi": "nova",
        "mr": "alloy",
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "tts-1-hd"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        voice: Optional[str] = None,
        rate: str = "-4%",
    ) -> float:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        selected_voice = voice or self.VOICE_MAP.get(language.lower(), "fable")
        clean_text = clean_storytelling_text(text)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        response = client.audio.speech.create(
            model=self.model,
            voice=selected_voice,
            input=clean_text,
        )
        response.stream_to_file(str(output_path))
        words = len(clean_text.split())
        return max(2.0, words / 2.16)


class ElevenLabsTTSProvider(TTSProvider):
    """
    ElevenLabs Multilingual Storyteller TTS Provider.
    """

    def __init__(self, api_key: Optional[str] = None, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.voice_id = voice_id

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        voice: Optional[str] = None,
        rate: str = "-4%",
    ) -> float:
        import urllib.request
        import json

        selected_voice = voice or self.voice_id
        clean_text = clean_storytelling_text(text)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        payload = {
            "text": clean_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.35,
                "use_speaker_boost": True,
            },
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        loop = asyncio.get_event_loop()

        def _do_request():
            with urllib.request.urlopen(req) as resp:
                output_path.write_bytes(resp.read())

        await loop.run_in_executor(None, _do_request)
        words = len(clean_text.split())
        return max(2.0, words / 2.16)


class GTTSSProvider(TTSProvider):
    """Google TTS Fallback Provider (Generates 100% valid MP3 files)."""

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        voice: Optional[str] = None,
        rate: str = "-4%",
    ) -> float:
        from gtts import gTTS
        output_path.parent.mkdir(parents=True, exist_ok=True)
        clean_text = clean_storytelling_text(text)
        
        loop = asyncio.get_event_loop()
        lang_code = "hi" if language == "hi" else ("mr" if language == "mr" else "en")
        
        def _run_gtts():
            tts = gTTS(text=clean_text, lang=lang_code, slow=False)
            tts.save(str(output_path))

        await loop.run_in_executor(None, _run_gtts)
        words = len(clean_text.split())
        return max(2.0, words / 2.16)


class MockTTSProvider(TTSProvider):
    """Mock TTS Provider for unit testing."""

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        voice: Optional[str] = None,
        rate: str = "-4%",
    ) -> float:
        clean_text = clean_storytelling_text(text)
        try:
            from gtts import gTTS
            tts = gTTS(text=clean_text[:50] or "Story chapter", lang="en", slow=False)
            tts.save(str(output_path))
        except Exception:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(
                b"\xff\xfb\x90d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" * 38
            )
        words = len(clean_text.split())
        return max(2.0, words / 2.5)


def get_tts_provider(provider_type: Optional[str] = None) -> TTSProvider:
    """Factory method for modular TTS provider selection."""
    provider = (provider_type or settings.TTS_PROVIDER).lower()
    if provider in ("edge", "edgetts"):
        return EdgeTTSProvider()
    elif provider in ("qwen", "qwen_tts", "cosyvoice"):
        return QwenTTSProvider()
    elif provider in ("openai", "openai_tts"):
        return OpenAITTSProvider()
    elif provider in ("elevenlabs", "eleven"):
        return ElevenLabsTTSProvider()
    elif provider == "gtts":
        return GTTSSProvider()
    elif provider == "mock":
        return MockTTSProvider()
    return EdgeTTSProvider()
