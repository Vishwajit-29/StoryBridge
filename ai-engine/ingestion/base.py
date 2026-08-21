from __future__ import annotations
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from schemas.canonical import CanonicalSource, RightsRecord, SourceMetadata


class SourceAdapter(ABC):
    """
    Abstract Source Adapter Interface.
    Per SRS Section 5.2, all source formats must normalize into CanonicalSource.
    """

    @abstractmethod
    def parse(
        self,
        file_path_or_content: str | Path,
        title: str,
        story_id: str,
        language: str = "en",
        author: Optional[str] = None,
        rights: Optional[RightsRecord] = None,
    ) -> CanonicalSource:
        """Parse source content into CanonicalSource artifact."""
        pass

    @staticmethod
    def calculate_sha256(content: bytes | str) -> str:
        """Calculate SHA-256 checksum of raw input."""
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()
