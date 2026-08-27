"""Data models and conversion utilities for audio tracks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


AUDIO_EXTENSIONS: set[str] = {".mp3", ".flac"}


@dataclass(slots=True)
class TrackRecord:
    """Represents a comprehensive snapshot of audio metadata and stream information.

    Attributes:
        path: Absolute or relative filesystem path to the audio file.
        filename: Name of the file with extension.
        artist: Lead artist or performer.
        title: Title of the song or audio track.
        album: Name of the album or release.
        album_artist: Primary artist credited for the whole album.
        year: Year or date of the release.
        genre: Musical genre.
        track_number: Track index on the medium.
        track_total: Total number of tracks on the medium.
        disc_number: Disc index in a multi-disc set.
        disc_total: Total number of discs in the set.
        bpm: Beats per minute (tempo).
        initial_key: Initial musical key notation (e.g. '8A', 'C#m').
        comment: User comment or description.
        original_artist: Original artist for cover versions or remixes.
        remixer: Name of the remixer or producer.
        composer: Name of the composer.
        conductor: Name of the orchestra or ensemble conductor.
        group_description: Content group or grouping description.
        subtitle: Subtitle or version description (e.g. 'Radio Edit').
        isrc: International Standard Recording Code.
        publisher: Record label or publisher organization.
        copyright_text: Copyright and legal notice text.
        url: Official website or audio source URL.
        encoder: Encoder tool or encoding settings used.
        lyrics: Unsynchronized lyrics text.
        fmt: Uppercase format extension (e.g. 'MP3', 'FLAC').
        duration_sec: Playback duration in seconds.
        bitrate_kbps: Bitrate in kilobits per second.
        sample_rate: Audio sample rate in Hertz (Hz).
        channels: Number of audio channels (e.g. 1 for mono, 2 for stereo).
        bits_per_sample: Bit depth per sample (e.g. 16, 24).
        tag_type: Formatted tag specification version (e.g. 'ID3v2.4 utf8').
        tags: Raw dictionary of tags extracted by the underlying engine.
    """

    path: Path
    filename: str
    artist: str = ""
    title: str = ""
    album: str = ""
    album_artist: str = ""
    year: str = ""
    genre: str = ""
    track_number: str = ""
    track_total: str = ""
    disc_number: str = ""
    disc_total: str = ""
    bpm: str = ""
    initial_key: str = ""
    comment: str = ""
    original_artist: str = ""
    remixer: str = ""
    composer: str = ""
    conductor: str = ""
    group_description: str = ""
    subtitle: str = ""
    isrc: str = ""
    publisher: str = ""
    copyright_text: str = ""
    url: str = ""
    encoder: str = ""
    lyrics: str = ""
    fmt: str = ""
    duration_sec: float = 0.0
    bitrate_kbps: int = 0
    sample_rate: int = 0
    channels: int = 0
    bits_per_sample: int = 0
    tag_type: str = ""
    tags: dict[str, Any] = field(default_factory=dict)


def record_to_payload(record: TrackRecord) -> dict[str, str]:
    """Convert a TrackRecord instance into a dictionary payload for writing tags.

    Maps all metadata fields from the record to standardized keys expected
    by the format handlers (e.g., mapping `copyright_text` to `rights`).

    Args:
        record: The TrackRecord instance to convert.

    Returns:
        A dictionary mapping tag field names to their string values.
    """
    return {
        "artist": record.artist,
        "title": record.title,
        "album": record.album,
        "album_artist": record.album_artist,
        "year": record.year,
        "genre": record.genre,
        "track_number": record.track_number,
        "track_total": record.track_total,
        "disc_number": record.disc_number,
        "disc_total": record.disc_total,
        "bpm": record.bpm,
        "initial_key": record.initial_key,
        "comment": record.comment,
        "original_artist": record.original_artist,
        "remixer": record.remixer,
        "composer": record.composer,
        "conductor": record.conductor,
        "group_description": record.group_description,
        "subtitle": record.subtitle,
        "isrc": record.isrc,
        "publisher": record.publisher,
        "rights": record.copyright_text,
        "url": record.url,
        "encoder": record.encoder,
        "lyrics": record.lyrics,
    }
