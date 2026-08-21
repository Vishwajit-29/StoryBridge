import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root or current working directory
root_dir = Path(__file__).resolve().parent.parent
dotenv_path = root_dir / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()

class Settings:
    # NVIDIA NIM LLM Configuration
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", os.getenv("NIM_API_KEY", ""))
    NIM_BASE_URL: str = os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NIM_MODEL_NAME: str = os.getenv("NIM_MODEL_NAME", "meta/llama-3.3-70b-instruct")

    # LLM Provider selection: "nvidia", "openai", "ollama", "mock"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "nvidia")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # TTS Provider selection: "edge", "piper", "gtts", "mock"
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "edge")
    PIPER_BINARY_PATH: str = os.getenv("PIPER_BINARY_PATH", "piper")
    PIPER_MODELS_DIR: str = os.getenv("PIPER_MODELS_DIR", str(root_dir / "storage" / "tts_models"))

    # Service & Storage
    AI_ENGINE_HOST: str = os.getenv("AI_ENGINE_HOST", "0.0.0.0")
    AI_ENGINE_PORT: int = int(os.getenv("AI_ENGINE_PORT", "8000"))
    STORAGE_DIR: Path = Path(os.getenv("STORAGE_DIR", str(root_dir / "storage" / "artifacts")))

    # Supported Languages
    SUPPORTED_LANGUAGES: list[str] = ["en", "hi", "mr", "ta", "te", "bn"]

    # Target Durations in Minutes
    DURATION_PRESETS: dict[str, dict] = {
        "quick": {"target_minutes": 5, "min_minutes": 3, "max_minutes": 7, "target_words": 650},
        "standard": {"target_minutes": 15, "min_minutes": 10, "max_minutes": 20, "target_words": 1950},
        "complete": {"target_minutes": 45, "min_minutes": 30, "max_minutes": 60, "target_words": 5850},
    }

settings = Settings()
