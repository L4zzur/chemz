"""chemz: Ergonomic, strictly-typed audio metadata & cover art manager (MP3, FLAC)."""

from __future__ import annotations

from .base import AudioFormatHandler
from .core import (
    delete_cover,
    get_handler,
    read_cover_bytes,
    read_track,
    write_cover_bytes,
    write_track_tags,
)
from .formats.id3 import ID3Handler
from .formats.vorbis import VorbisHandler
from .models import AUDIO_EXTENSIONS, TrackRecord, record_to_payload
from .track import AudioFile


__version__ = "0.1.0"

__all__ = [
    "AUDIO_EXTENSIONS",
    "AudioFile",
    "AudioFormatHandler",
    "ID3Handler",
    "TrackRecord",
    "VorbisHandler",
    "delete_cover",
    "get_handler",
    "read_cover_bytes",
    "read_track",
    "record_to_payload",
    "write_cover_bytes",
    "write_track_tags",
]
