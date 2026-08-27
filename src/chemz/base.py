"""Abstract base class and shared helpers for format-specific audio handlers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class AudioFormatHandler(ABC):
    """Abstract base class defining the contract for audio format handlers.

    Handles reading, writing, and manipulating metadata tags and embedded
    cover art for specific audio file formats.
    """

    @abstractmethod
    def read_metadata(self, path: Path) -> dict[str, Any]:
        """Read all metadata tags from the audio file.

        Args:
            path: Path to the target audio file.

        Returns:
            A dictionary containing parsed metadata key-value pairs.
        """
        pass

    @abstractmethod
    def write_metadata(self, path: Path, payload: dict[str, str]) -> None:
        """Write metadata tags to the audio file based on the provided payload.

        Args:
            path: Path to the target audio file.
            payload: Dictionary of tag names and their new string values.
        """
        pass

    @abstractmethod
    def read_cover(self, path: Path) -> bytes | None:
        """Read and return embedded cover art bytes from the audio file.

        Args:
            path: Path to the target audio file.

        Returns:
            Raw image bytes if cover art exists, otherwise None.
        """
        pass

    @abstractmethod
    def write_cover(self, path: Path, data: bytes, mime: str = "image/jpeg") -> None:
        """Write or replace embedded cover art in the audio file.

        Args:
            path: Path to the target audio file.
            data: Raw image bytes to embed.
            mime: MIME type of the image (e.g., 'image/jpeg', 'image/png').
        """
        pass

    @abstractmethod
    def delete_cover(self, path: Path) -> None:
        """Remove all embedded cover art from the audio file.

        Args:
            path: Path to the target audio file.
        """
        pass

    def _first_tag_value(
        self, tags: Mapping[str, Any] | Any, keys: tuple[str, ...]
    ) -> str:
        """Extract the first non-empty tag value matching any of the specified keys.

        Args:
            tags: Dictionary or mapping of raw tags.
            keys: Tuple of tag key candidates to inspect in priority order.

        Returns:
            The stripped string value of the first matching tag, or an empty string.
        """
        for key in keys:
            raw = tags.get(key)
            if raw is None:
                continue
            if isinstance(raw, list):
                if not raw:
                    continue
                value = raw[0]
            else:
                value = raw
            if value is None:
                continue
            return str(value).strip()
        return ""

    def _split_number_total(self, value: str) -> tuple[str, str]:
        """Split combined number/total strings like '1/10' into separate components.

        Args:
            value: Raw string containing index or combined index/total (e.g. '3/12').

        Returns:
            A tuple of (number, total) where total may be an empty string.
        """
        if not value:
            return "", ""
        parts = [part.strip() for part in value.split("/", 1)]
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]
