"""Core functional facade for reading and manipulating audio metadata and covers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from mutagen import File

from .base import AudioFormatHandler
from .formats.id3 import ID3Handler
from .formats.vorbis import VorbisHandler
from .models import TrackRecord


_HANDLERS: dict[str, AudioFormatHandler] = {
    ".mp3": ID3Handler(),
    ".flac": VorbisHandler(),
}


def get_handler(path: Path) -> AudioFormatHandler:
    """Retrieve the format-specific handler for the given audio file path.

    Args:
        path: Path to the audio file.

    Returns:
        The matching AudioFormatHandler instance.

    Raises:
        ValueError: If the file extension is not supported.
    """
    suffix = path.suffix.lower()
    handler = _HANDLERS.get(suffix)
    if not handler:
        raise ValueError(f"Unsupported audio format: {suffix}")
    return handler


def _first_tag_value(tags: Mapping[str, Any] | Any, keys: tuple[str, ...]) -> str:
    """Helper to extract the first non-empty tag value from candidate keys."""
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


def read_track(path: Path) -> TrackRecord:
    """Read metadata tags, cover info, and audio stream properties from a file.

    Extracts technical properties (duration, bitrate, sample rate, channels, bit depth)
    as well as normalized metadata tags across all supported formats.

    Args:
        path: Path to the audio file.

    Returns:
        A fully populated TrackRecord instance representing the track.
    """
    audio = File(str(path), easy=True)
    tags: dict[str, Any] = {}
    duration = 0.0
    bitrate = 0
    sample_rate = 0
    channels = 0
    bits_per_sample = 0

    if audio is not None and getattr(audio, "info", None):
        info = audio.info
        duration = float(getattr(info, "length", 0.0) or 0.0)
        raw_bitrate = int(getattr(info, "bitrate", 0) or 0)
        bitrate = int(raw_bitrate / 1000) if raw_bitrate > 0 else 0
        sample_rate = int(getattr(info, "sample_rate", 0) or 0)
        channels = int(getattr(info, "channels", 0) or 0)
        bits_per_sample = int(getattr(info, "bits_per_sample", 0) or 0)

    if audio is not None and getattr(audio, "tags", None):
        tags = dict(audio.tags)

    try:
        handler = get_handler(path)
        fmt_meta = handler.read_metadata(path)
    except ValueError:
        fmt_meta = {}

    common_url = _first_tag_value(tags, ("www", "website", "url", "location"))
    url_value = (
        fmt_meta.get("url") or common_url
        if path.suffix.lower() == ".mp3"
        else common_url
    )

    track_number_raw = _first_tag_value(tags, ("tracknumber",))
    disc_number_raw = _first_tag_value(tags, ("discnumber",))

    def _split_number_total(val: str) -> tuple[str, str]:
        if not val:
            return "", ""
        parts = [p.strip() for p in val.split("/", 1)]
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]

    track_number, track_total = _split_number_total(track_number_raw)
    disc_number, disc_total = _split_number_total(disc_number_raw)

    if path.suffix.lower() == ".flac":
        if not track_total:
            track_total = _first_tag_value(tags, ("tracktotal", "totaltracks"))
        if not disc_total:
            disc_total = _first_tag_value(tags, ("disctotal", "totaldiscs"))

    return TrackRecord(
        path=path,
        filename=path.name,
        artist=fmt_meta.get("artist") or _first_tag_value(tags, ("artist",)),
        title=fmt_meta.get("title") or _first_tag_value(tags, ("title",)),
        album=fmt_meta.get("album") or _first_tag_value(tags, ("album",)),
        album_artist=fmt_meta.get("album_artist")
        or _first_tag_value(tags, ("albumartist", "album artist")),
        year=fmt_meta.get("year") or _first_tag_value(tags, ("date", "year")),
        genre=fmt_meta.get("genre") or _first_tag_value(tags, ("genre",)),
        track_number=fmt_meta.get("track_number") or track_number,
        track_total=fmt_meta.get("track_total") or track_total,
        disc_number=fmt_meta.get("disc_number") or disc_number,
        disc_total=fmt_meta.get("disc_total") or disc_total,
        bpm=fmt_meta.get("bpm") or _first_tag_value(tags, ("bpm",)),
        initial_key=fmt_meta.get("initial_key")
        or _first_tag_value(tags, ("initialkey", "key")),
        comment=fmt_meta.get("comment")
        or _first_tag_value(tags, ("comment", "description")),
        original_artist=fmt_meta.get("original_artist")
        or _first_tag_value(tags, ("origartist", "originalartist", "original artist")),
        remixer=fmt_meta.get("remixer")
        or _first_tag_value(tags, ("remixer", "remixedby")),
        composer=fmt_meta.get("composer") or _first_tag_value(tags, ("composer",)),
        conductor=fmt_meta.get("conductor") or _first_tag_value(tags, ("conductor",)),
        group_description=fmt_meta.get("group_description")
        or _first_tag_value(tags, ("grouping", "contentgroup")),
        subtitle=fmt_meta.get("subtitle")
        or _first_tag_value(tags, ("subtitle", "version")),
        isrc=fmt_meta.get("isrc") or _first_tag_value(tags, ("isrc",)),
        publisher=fmt_meta.get("publisher")
        or _first_tag_value(tags, ("organization", "publisher")),
        copyright_text=fmt_meta.get("copyright_text")
        or _first_tag_value(tags, ("copyright",)),
        url=url_value,
        encoder=fmt_meta.get("encoder")
        or _first_tag_value(tags, ("encodedby", "encoder")),
        lyrics=fmt_meta.get("lyrics") or _first_tag_value(tags, ("lyrics",)),
        fmt=path.suffix.lstrip(".").upper(),
        duration_sec=duration,
        bitrate_kbps=bitrate,
        sample_rate=sample_rate,
        channels=channels,
        bits_per_sample=bits_per_sample,
        tag_type=fmt_meta.get("tag_type", ""),
        tags=tags,
    )


def write_track_tags(path: Path, payload: dict[str, str]) -> None:
    """Write metadata tags to the specified audio file.

    Args:
        path: Path to the target audio file.
        payload: Dictionary of tag names and their new string values.
    """
    handler = get_handler(path)
    handler.write_metadata(path, payload)


def read_cover_bytes(path: Path) -> bytes | None:
    """Extract embedded cover art raw bytes from the specified audio file.

    Args:
        path: Path to the target audio file.

    Returns:
        Raw bytes of the embedded cover image, or None if no cover is found.
    """
    handler = get_handler(path)
    return handler.read_cover(path)


def write_cover_bytes(path: Path, data: bytes, mime: str = "image/jpeg") -> None:
    """Embed or replace cover art in the specified audio file.

    Args:
        path: Path to the target audio file.
        data: Raw image bytes.
        mime: MIME type of the image (default is 'image/jpeg').
    """
    handler = get_handler(path)
    handler.write_cover(path, data, mime)


def delete_cover(path: Path) -> None:
    """Remove all embedded cover art from the specified audio file.

    Args:
        path: Path to the target audio file.
    """
    handler = get_handler(path)
    handler.delete_cover(path)
