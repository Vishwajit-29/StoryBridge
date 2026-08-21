from __future__ import annotations
from pathlib import Path
from typing import Optional

from ingestion.base import SourceAdapter
from ingestion.epub_adapter import EPUBAdapter
from ingestion.pdf_adapter import PDFAdapter
from ingestion.subtitle_adapter import SubtitleAdapter
from ingestion.text_adapter import TextAdapter
from ingestion.web_adapter import WebAdapter


def get_adapter_for_source(source_path_or_url: str | Path) -> SourceAdapter:
    """Factory to retrieve appropriate SourceAdapter for input source."""
    if not source_path_or_url:
        return TextAdapter()

    source_str = str(source_path_or_url).strip()

    if source_str.lower().startswith(("http://", "https://")):
        return WebAdapter()

    if "\n" not in source_str and len(source_str) < 500:
        try:
            path = Path(source_path_or_url)
            if path.is_file():
                suffix = path.suffix.lower()
                if suffix in (".txt", ".md", ".markdown", ".text"):
                    return TextAdapter()
                elif suffix == ".pdf":
                    return PDFAdapter()
                elif suffix in (".epub",):
                    return EPUBAdapter()
                elif suffix in (".srt", ".vtt"):
                    return SubtitleAdapter()
                elif suffix in (".html", ".htm"):
                    return WebAdapter()
        except Exception:
            pass

    # Default to TextAdapter for raw text content
    return TextAdapter()
