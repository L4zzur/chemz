"""Unit tests for chemz core, models, base helpers, and format handlers."""

from __future__ import annotations

from pathlib import Path

import pytest

from chemz.base import AudioFormatHandler
from chemz.core import (
    delete_cover,
    get_handler,
    read_cover_bytes,
    read_track,
    write_cover_bytes,
    write_track_tags,
)
from chemz.formats.id3 import ID3Handler
from chemz.formats.vorbis import VorbisHandler
from chemz.models import AUDIO_EXTENSIONS, TrackRecord, record_to_payload


# --- Models and Base Helpers Tests ---


def test_audio_extensions_and_track_record() -> None:
    """Verify AUDIO_EXTENSIONS set and TrackRecord defaults."""
    assert ".mp3" in AUDIO_EXTENSIONS
    assert ".flac" in AUDIO_EXTENSIONS

    rec = TrackRecord(
        path=Path("chemz.mp3"),
        filename="chemz.mp3",
        artist="Burial",
        title="Chemz",
        album="Chemz / Dolphinz",
        year="2021",
        genre="Atmospheric Breaks/Breakbeat/Big Beat",
        copyright_text="2021 Hyperdub Records",
    )
    assert rec.artist == "Burial"
    assert rec.title == "Chemz"
    assert rec.album == "Chemz / Dolphinz"
    assert rec.copyright_text == "2021 Hyperdub Records"
    assert rec.duration_sec == 0.0

    payload = record_to_payload(rec)
    assert payload["artist"] == "Burial"
    assert payload["title"] == "Chemz"
    assert payload["rights"] == "2021 Hyperdub Records"
    assert "copyright_text" not in payload


def test_base_first_tag_value_fallback() -> None:
    """Test AudioFormatHandler._first_tag_value logic with various value types."""

    class DummyHandler(AudioFormatHandler):
        def read_metadata(self, path: Path) -> dict[str, str]:
            return {}

        def write_metadata(self, path: Path, payload: dict[str, str]) -> None:
            pass

        def read_cover(self, path: Path) -> bytes | None:
            return None

        def write_cover(
            self, path: Path, data: bytes, mime: str = "image/jpeg"
        ) -> None:
            pass

        def delete_cover(self, path: Path) -> None:
            pass

    handler = DummyHandler()

    # Empty dictionary
    assert handler._first_tag_value({}, ("artist", "title")) == ""

    # Various candidate values
    tags = {
        "empty_list": [],
        "none_val": None,
        "valid_list": ["  Burial  "],
        "direct_str": " Chemz ",
    }
    assert handler._first_tag_value(tags, ("empty_list", "none_val")) == ""
    assert handler._first_tag_value(tags, ("empty_list", "valid_list")) == "Burial"
    assert handler._first_tag_value(tags, ("direct_str",)) == "Chemz"


def test_base_split_number_total() -> None:
    """Test AudioFormatHandler._split_number_total parsing track/disc numbers."""

    class DummyHandler(AudioFormatHandler):
        def read_metadata(self, path: Path) -> dict[str, str]:
            return {}

        def write_metadata(self, path: Path, payload: dict[str, str]) -> None:
            pass

        def read_cover(self, path: Path) -> bytes | None:
            return None

        def write_cover(
            self, path: Path, data: bytes, mime: str = "image/jpeg"
        ) -> None:
            pass

        def delete_cover(self, path: Path) -> None:
            pass

    handler = DummyHandler()

    assert handler._split_number_total("") == ("", "")
    assert handler._split_number_total("1") == ("1", "")
    assert handler._split_number_total("1/2") == ("1", "2")
    assert handler._split_number_total(" 3 / 10 ") == ("3", "10")


# --- Format Handlers Factory Tests ---


def test_get_handler_supported_formats() -> None:
    """Verify get_handler returns appropriate handlers for supported extensions."""
    assert isinstance(get_handler(Path("audio.mp3")), ID3Handler)
    assert isinstance(get_handler(Path("AUDIO.MP3")), ID3Handler)
    assert isinstance(get_handler(Path("audio.flac")), VorbisHandler)
    assert isinstance(get_handler(Path("AUDIO.FLAC")), VorbisHandler)


def test_get_handler_unsupported_formats() -> None:
    """Verify get_handler raises ValueError for unsupported audio extensions."""
    with pytest.raises(ValueError, match=r"Unsupported audio format: \.wav"):
        get_handler(Path("audio.wav"))

    with pytest.raises(ValueError, match=r"Unsupported audio format: \.m4a"):
        get_handler(Path("audio.m4a"))

    with pytest.raises(ValueError, match=r"Unsupported audio format: \.ogg"):
        get_handler(Path("audio.ogg"))


# --- ID3Handler on Real MP3 File (Burial metadata) ---


def test_id3_handler_read_and_write(sample_mp3: Path) -> None:
    """Test ID3Handler reading and writing metadata on a real MP3 file."""
    handler = ID3Handler()

    # 1. Read initial state
    initial_meta = handler.read_metadata(sample_mp3)
    assert initial_meta["title"] == "london"
    assert initial_meta["tag_type"].startswith("ID3")

    # 2. Write full payload of authentic Burial tags
    payload = {
        "artist": "Burial",
        "title": "Chemz",
        "album": "Chemz / Dolphinz",
        "album_artist": "Burial",
        "year": "2021",
        "genre": "Atmospheric Breaks/Breakbeat/Big Beat",
        "track_number": "1",
        "track_total": "2",
        "disc_number": "1",
        "disc_total": "1",
        "bpm": "146",
        "initial_key": "F min",
        "comment": "Release Day: 21 May",
        "original_artist": "Burial",
        "remixer": "William Bevan",
        "composer": "William Bevan",
        "conductor": "Kode9",
        "group_description": "Hyperdub Releases",
        "subtitle": "A/B Single",
        "isrc": "GBLZC2000101",
        "publisher": "Hyperdub",
        "rights": "2021 Hyperdub Records",
        "url": "https://hyperdub.net",
        "encoder": "chemz-engine",
        "lyrics": "Don't know what I'd do if I would lose you now",
    }
    handler.write_metadata(sample_mp3, payload)

    # 3. Re-read and verify all tags persisted
    meta = handler.read_metadata(sample_mp3)
    assert meta["artist"] == "Burial"
    assert meta["title"] == "Chemz"
    assert meta["album"] == "Chemz / Dolphinz"
    assert meta["album_artist"] == "Burial"
    assert meta["year"] == "2021"
    assert meta["genre"] == "Atmospheric Breaks/Breakbeat/Big Beat"
    assert meta["track_number"] == "1"
    assert meta["track_total"] == "2"
    assert meta["disc_number"] == "1"
    assert meta["disc_total"] == "1"
    assert meta["bpm"] == "146"
    assert meta["initial_key"] == "F min"
    assert meta["comment"] == "Release Day: 21 May"
    assert meta["original_artist"] == "Burial"
    assert meta["remixer"] == "William Bevan"
    assert meta["composer"] == "William Bevan"
    assert meta["conductor"] == "Kode9"
    assert meta["group_description"] == "Hyperdub Releases"
    assert meta["subtitle"] == "A/B Single"
    assert meta["isrc"] == "GBLZC2000101"
    assert meta["publisher"] == "Hyperdub"
    assert meta["copyright_text"] == "2021 Hyperdub Records"
    assert meta["url"] == "https://hyperdub.net"
    assert meta["encoder"] == "chemz-engine"
    assert meta["lyrics"] == "Don't know what I'd do if I would lose you now"


def test_id3_handler_covers(sample_mp3: Path, cover_jpg_path: Path) -> None:
    """Test ID3Handler cover art operations on a real MP3 file."""
    handler = ID3Handler()
    cover_data = cover_jpg_path.read_bytes()

    # Initial cover should be None
    assert handler.read_cover(sample_mp3) is None

    # Write cover
    handler.write_cover(sample_mp3, cover_data, mime="image/jpeg")
    assert handler.read_cover(sample_mp3) == cover_data

    # Delete cover
    handler.delete_cover(sample_mp3)
    assert handler.read_cover(sample_mp3) is None


# --- VorbisHandler on Real FLAC File ---


def test_vorbis_handler_read_and_write(sample_flac: Path) -> None:
    """Test VorbisHandler reading and writing comments on a real FLAC file."""
    handler = VorbisHandler()

    # 1. Read initial state
    initial_meta = handler.read_metadata(sample_flac)
    assert initial_meta["artist"] == "Iwan 'qubodup' Gabovitch"
    assert initial_meta["tag_type"] == "VORBIS"

    # 2. Write full payload of authentic Vorbis comments
    payload = {
        "artist": "acloudyskye",
        "title": "Spill",
        "album": "This Won't Be The Last Time LP",
        "album_artist": "acloudyskye",
        "year": "2021",
        "genre": "Acoustic/Post-Rock/Melodic Midtempo",
        "track_number": "7",
        "track_total": "9",
        "disc_number": "1",
        "disc_total": "1",
        "bpm": "150",
        "initial_key": "F# maj",
        "comment": "Release Day: 14 February",
        "original_artist": "acloudyskye",
        "remixer": "Skye Kothari",
        "composer": "Skye Kothari",
        "conductor": "Skye Kothari",
        "group_description": "Concept Album",
        "subtitle": "Original Mix",
        "isrc": "QZTBE2428265",
        "publisher": "acloudyskye",
        "rights": "2025 acloudyskye",
        "url": "https://acloudyskye.bandcamp.com",
        "encoder": "chemz-flac",
        "lyrics": "Turn your head away \\ Slowly from me",
    }
    handler.write_metadata(sample_flac, payload)

    # 3. Re-read and verify all comments persisted
    meta = handler.read_metadata(sample_flac)
    assert meta["artist"] == "acloudyskye"
    assert meta["title"] == "Spill"
    assert meta["album"] == "This Won't Be The Last Time LP"
    assert meta["album_artist"] == "acloudyskye"
    assert meta["year"] == "2021"
    assert meta["genre"] == "Acoustic/Post-Rock/Melodic Midtempo"
    assert meta["track_number"] == "7"
    assert meta["track_total"] == "9"
    assert meta["disc_number"] == "1"
    assert meta["disc_total"] == "1"
    assert meta["bpm"] == "150"
    assert meta["initial_key"] == "F# maj"
    assert meta["comment"] == "Release Day: 14 February"
    assert meta["original_artist"] == "acloudyskye"
    assert meta["remixer"] == "Skye Kothari"
    assert meta["composer"] == "Skye Kothari"
    assert meta["conductor"] == "Skye Kothari"
    assert meta["group_description"] == "Concept Album"
    assert meta["subtitle"] == "Original Mix"
    assert meta["isrc"] == "QZTBE2428265"
    assert meta["publisher"] == "acloudyskye"
    assert meta["copyright_text"] == "2025 acloudyskye"
    assert meta["url"] == "https://acloudyskye.bandcamp.com"
    assert meta["encoder"] == "chemz-flac"
    assert meta["lyrics"] == "Turn your head away \\ Slowly from me"


def test_vorbis_handler_covers(sample_flac: Path, cover_png_path: Path) -> None:
    """Test VorbisHandler picture block operations on a real FLAC file."""
    handler = VorbisHandler()
    cover_data = cover_png_path.read_bytes()

    # Initial cover should be None
    assert handler.read_cover(sample_flac) is None

    # Write cover
    handler.write_cover(sample_flac, cover_data, mime="image/png")
    assert handler.read_cover(sample_flac) == cover_data

    # Delete cover
    handler.delete_cover(sample_flac)
    assert handler.read_cover(sample_flac) is None


def test_id3_write_empty_deletes_tags(sample_mp3: Path) -> None:
    """Test that writing empty strings removes existing ID3 frames."""
    handler = ID3Handler()
    # Write initial tags
    handler.write_metadata(
        sample_mp3,
        {
            "artist": "Burial",
            "title": "Archangel",
            "album": "Untrue",
            "year": "2007",
            "genre": "Dubstep",
            "comment": "Hyperdub HDBLP002",
            "bpm": "138",
            "initial_key": "C#m",
            "original_artist": "Burial",
            "remixer": "William Bevan",
            "composer": "William Bevan",
            "conductor": "Kode9",
            "group_description": "Untrue LP",
            "subtitle": "Album Version",
            "isrc": "GBBBN0700021",
            "publisher": "Hyperdub",
            "rights": "2007 Hyperdub",
            "url": "https://hyperdub.net",
            "encoder": "chemz",
            "lyrics": "Holding you...",
            "track_number": "2",
            "track_total": "13",
            "disc_number": "1",
            "disc_total": "1",
        },
    )

    # Now clear all tags by writing empty strings
    empty_payload = {
        k: ""
        for k in [
            "artist",
            "title",
            "album",
            "album_artist",
            "year",
            "genre",
            "comment",
            "bpm",
            "initial_key",
            "original_artist",
            "remixer",
            "composer",
            "conductor",
            "group_description",
            "subtitle",
            "isrc",
            "publisher",
            "rights",
            "url",
            "encoder",
            "lyrics",
            "track_number",
            "track_total",
            "disc_number",
            "disc_total",
        ]
    }
    handler.write_metadata(sample_mp3, empty_payload)

    # Verify all are cleared
    cleared = handler.read_metadata(sample_mp3)
    assert cleared["artist"] == ""
    assert cleared["title"] == ""
    assert cleared["album"] == ""
    assert cleared["genre"] == ""
    assert cleared["lyrics"] == ""


def test_vorbis_write_empty_deletes_tags(sample_flac: Path) -> None:
    """Test that writing empty strings removes existing Vorbis comments."""
    handler = VorbisHandler()
    # Write initial comments
    handler.write_metadata(
        sample_flac,
        {
            "artist": "acloudyskye",
            "title": "Spill",
            "album": "This Won't Be The Last Time LP",
            "year": "2025",
            "genre": "Acoustic/Post-Rock/Melodic Midtempo",
            "comment": "This Won't Be The Last Time LP",
            "bpm": "150",
            "initial_key": "F# maj",
            "original_artist": "acloudyskye",
            "remixer": "Skye Kothari",
            "composer": "Skye Kothari",
            "conductor": "Skye Kothari",
            "group_description": "Concept Album",
            "subtitle": "Original Mix",
            "isrc": "QZNWR2218677",
            "publisher": "Self-Release",
            "rights": "2025 acloudyskye",
            "url": "https://acloudyskye.bandcamp.com",
            "encoder": "chemz",
            "lyrics": "Turn your head away \\ Slowly from me",
        },
    )

    # Clear all comments with empty strings
    empty_payload = {
        k: ""
        for k in [
            "artist",
            "title",
            "album",
            "album_artist",
            "year",
            "genre",
            "comment",
            "bpm",
            "initial_key",
            "original_artist",
            "remixer",
            "composer",
            "conductor",
            "group_description",
            "subtitle",
            "isrc",
            "publisher",
            "rights",
            "url",
            "encoder",
            "lyrics",
        ]
    }
    handler.write_metadata(sample_flac, empty_payload)

    cleared = handler.read_metadata(sample_flac)
    assert cleared["artist"] == ""
    assert cleared["title"] == ""
    assert cleared["album"] == ""
    assert cleared["lyrics"] == ""


def test_format_handlers_corrupted_files(tmp_path: Path) -> None:
    """Test handlers graceful handling when reading non-audio or corrupt files."""
    corrupt_file = tmp_path / "corrupt.bin"
    corrupt_file.write_bytes(b"NOT_AN_AUDIO_FILE")

    id3_handler = ID3Handler()
    assert id3_handler.read_metadata(corrupt_file)["artist"] == ""
    assert id3_handler.read_cover(corrupt_file) is None

    vorbis_handler = VorbisHandler()
    assert vorbis_handler.read_metadata(corrupt_file)["artist"] == ""
    assert vorbis_handler.read_cover(corrupt_file) is None


# --- Core Facade Functions on Real Files ---


def test_core_facade_read_and_write(sample_mp3: Path, cover_jpg_path: Path) -> None:
    """Test read_track, write_track_tags, and cover facade on real files."""
    # 1. read_track extracts technical stream info
    record = read_track(sample_mp3)
    assert record.fmt == "MP3"
    assert record.duration_sec > 400.0
    assert record.bitrate_kbps == 160
    assert record.sample_rate == 44100
    assert record.channels == 2
    assert record.title == "london"

    # 2. write_track_tags with Burial data
    write_track_tags(sample_mp3, {"title": "Chemz", "artist": "Burial"})
    updated_record = read_track(sample_mp3)
    assert updated_record.title == "Chemz"
    assert updated_record.artist == "Burial"

    # 3. cover facade functions
    cover_bytes = cover_jpg_path.read_bytes()
    assert read_cover_bytes(sample_mp3) is None
    write_cover_bytes(sample_mp3, cover_bytes, mime="image/jpeg")
    assert read_cover_bytes(sample_mp3) == cover_bytes
    delete_cover(sample_mp3)
    assert read_cover_bytes(sample_mp3) is None
