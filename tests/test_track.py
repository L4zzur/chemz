"""Comprehensive unit and functional tests for AudioFile high-level interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from chemz.track import AudioFile


def test_audiofile_initialization_and_stream_props(sample_mp3: Path) -> None:
    """Test AudioFile properties read accurately from real audio files."""
    # From string path
    audio_str = AudioFile(str(sample_mp3))
    assert audio_str.path == sample_mp3
    assert audio_str.filename == sample_mp3.name
    assert audio_str.fmt == "MP3"
    assert audio_str.duration_sec > 400.0
    assert audio_str.duration == audio_str.duration_sec
    assert audio_str.bitrate_kbps == 160
    assert audio_str.bitrate == 160
    assert audio_str.sample_rate == 44100
    assert audio_str.channels == 2
    assert audio_str.tag_type.startswith("ID3")
    assert isinstance(audio_str.tags, dict)
    assert audio_str.record.filename == sample_mp3.name

    # From Path object
    audio_path = AudioFile(sample_mp3)
    assert audio_path.path == sample_mp3


def test_audiofile_all_tag_getters_and_setters(sample_mp3: Path) -> None:
    """Test getting, setting, and type coercion of all supported metadata tags."""
    audio = AudioFile(sample_mp3)

    # Initial getter check
    assert audio.title == "london"
    assert audio.artist == ""

    # Set all 22+ tag fields with release information
    audio.artist = "Burial"
    audio.title = "Chemz"
    audio.album = "Chemz / Dolphinz"
    audio.album_artist = "Burial"
    audio.year = 2021
    audio.genre = "Future Garage"
    audio.track_number = 1
    audio.track_total = 2
    audio.disc_number = 1
    audio.disc_total = 1
    audio.bpm = 135.0
    audio.initial_key = "Fm"
    audio.comment = "Mastered at Transition Mastering Studios"
    audio.original_artist = "Burial"
    audio.remixer = "William Bevan"
    audio.composer = "William Bevan"
    audio.conductor = "Kode9"
    audio.group_description = "Hyperdub Releases"
    audio.subtitle = "Club Mix"
    audio.isrc = "GBLZC2000101"
    audio.publisher = "Hyperdub"
    audio.rights = "2021 Hyperdub Records"
    audio.url = "https://hyperdub.net"
    audio.encoder = "chemz-engine"
    audio.lyrics = "Love you so..."

    # Assert getters return new updated values
    assert audio.artist == "Burial"
    assert audio.title == "Chemz"
    assert audio.album == "Chemz / Dolphinz"
    assert audio.album_artist == "Burial"
    assert audio.year == "2021"
    assert audio.genre == "Future Garage"
    assert audio.track_number == "1"
    assert audio.track_total == "2"
    assert audio.disc_number == "1"
    assert audio.disc_total == "1"
    assert audio.bpm == "135.0"
    assert audio.initial_key == "Fm"
    assert audio.comment == "Mastered at Transition Mastering Studios"
    assert audio.original_artist == "Burial"
    assert audio.remixer == "William Bevan"
    assert audio.composer == "William Bevan"
    assert audio.conductor == "Kode9"
    assert audio.group_description == "Hyperdub Releases"
    assert audio.subtitle == "Club Mix"
    assert audio.isrc == "GBLZC2000101"
    assert audio.publisher == "Hyperdub"
    assert audio.copyright_text == "2021 Hyperdub Records"
    assert audio.rights == "2021 Hyperdub Records"
    assert audio.url == "https://hyperdub.net"
    assert audio.encoder == "chemz-engine"
    assert audio.lyrics == "Love you so..."

    # Setting None clears the property to empty string
    audio.artist = None
    assert audio.artist == ""


def test_audiofile_save_and_reload(sample_mp3: Path) -> None:
    """Test save() writing changes to disk and reload() discarding unsaved changes."""
    audio = AudioFile(sample_mp3)

    # 1. Modify and reload without saving -> reverts to original
    audio.title = "Unsaved Temporary Title"
    assert audio.title == "Unsaved Temporary Title"
    audio.reload()
    assert audio.title == "london"

    # 2. Modify and save -> persists on disk
    audio.title = "Archangel"
    audio.artist = "Burial"
    audio.save()

    # Re-open independent instance to verify disk persistence
    reopened = AudioFile(sample_mp3)
    assert reopened.title == "Archangel"
    assert reopened.artist == "Burial"


def test_audiofile_context_manager_auto_save(sample_mp3: Path) -> None:
    """Test context manager automatically saving changes upon clean block exit."""
    with AudioFile(sample_mp3) as track:
        track.artist = "Burial"
        track.album = "Untrue"
        track.bpm = "138"

    # Verify on fresh instance
    reopened = AudioFile(sample_mp3)
    assert reopened.artist == "Burial"
    assert reopened.album == "Untrue"
    assert reopened.bpm == "138"


def test_audiofile_context_manager_exception_rollback(sample_mp3: Path) -> None:
    """Test context manager does NOT save changes when an exception occurs."""
    with pytest.raises(RuntimeError, match="Intentional failure"):
        with AudioFile(sample_mp3) as track:
            track.album = "Aborted Album"
            raise RuntimeError("Intentional failure")

    # Verify original value remained intact
    reopened = AudioFile(sample_mp3)
    assert reopened.album == ""


def test_audiofile_cover_operations(
    sample_mp3: Path,
    cover_jpg_path: Path,
    cover_png_path: Path,
) -> None:
    """Test full cover art lifecycle on AudioFile."""
    audio = AudioFile(sample_mp3)
    jpg_bytes = cover_jpg_path.read_bytes()
    png_bytes = cover_png_path.read_bytes()

    # 1. Initial cover is None
    assert audio.cover is None

    # 2. Set cover via bytes and save
    audio.cover = jpg_bytes
    assert audio.cover == jpg_bytes
    audio.save()

    reopened_1 = AudioFile(sample_mp3)
    assert reopened_1.cover == jpg_bytes

    # 3. Set cover via Path object and save
    reopened_1.cover = cover_png_path
    assert reopened_1.cover == png_bytes
    reopened_1.save()

    reopened_2 = AudioFile(sample_mp3)
    assert reopened_2.cover == png_bytes

    # 4. Set cover via string path
    reopened_2.cover = str(cover_jpg_path)
    assert reopened_2.cover == jpg_bytes
    reopened_2.save()

    reopened_3 = AudioFile(sample_mp3)
    assert reopened_3.cover == jpg_bytes

    # 5. Delete cover via setter None
    reopened_3.cover = None
    assert reopened_3.cover is None
    reopened_3.save()

    reopened_4 = AudioFile(sample_mp3)
    assert reopened_4.cover is None

    # 6. Delete cover via del
    reopened_4.cover = jpg_bytes
    reopened_4.save()
    del reopened_4.cover
    reopened_4.save()

    reopened_5 = AudioFile(sample_mp3)
    assert reopened_5.cover is None

    # 7. Invalid type raises TypeError
    with pytest.raises(TypeError, match="Cover data must be bytes, Path, str, or None"):
        audio.cover = cast(Any, 12345)


def test_audiofile_cover_webp_inference(
    sample_mp3: Path,
    cover_webp_path: Path,
) -> None:
    """Test automatic MIME type detection for real WebP images in set_cover."""
    webp_bytes = cover_webp_path.read_bytes()

    audio = AudioFile(sample_mp3)
    audio.set_cover(cover_webp_path)
    assert audio.cover == webp_bytes
    audio.save()

    reopened = AudioFile(sample_mp3)
    assert reopened.cover == webp_bytes


def test_audiofile_utilities(sample_mp3: Path) -> None:
    """Test AudioFile to_dict() and __repr__() utilities."""
    audio = AudioFile(sample_mp3)
    audio.artist = "Burial"
    audio.title = "Chemz"

    # __repr__
    repr_str = repr(audio)
    assert "AudioFile(" in repr_str
    assert "Burial" in repr_str
    assert "Chemz" in repr_str
    assert "MP3" in repr_str

    # to_dict
    d = audio.to_dict()
    assert d["artist"] == "Burial"
    assert d["title"] == "Chemz"
    assert d["fmt"] == "MP3"
    assert d["duration_sec"] > 400.0
