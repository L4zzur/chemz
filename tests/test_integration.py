"""End-to-end integration lifecycle tests on real MP3 and FLAC audio files."""

from __future__ import annotations

from pathlib import Path

from chemz import (
    AudioFile,
    delete_cover,
    read_cover_bytes,
    read_track,
    write_cover_bytes,
)


def test_real_mp3_full_lifecycle(
    sample_mp3: Path,
    cover_jpg_path: Path,
    cover_png_path: Path,
) -> None:
    """Verify end-to-end tag and cover modifications on real MP3 file."""
    # 1. Read initial state from real MP3
    audio = AudioFile(sample_mp3)
    assert audio.title == "london"
    assert audio.fmt == "MP3"
    assert audio.duration_sec > 400
    assert audio.bitrate_kbps > 0
    assert audio.cover is None

    # 2. Modify metadata and set JPEG cover art
    with AudioFile(sample_mp3) as track:
        track.title = "Ghost Hardware"
        track.artist = "Burial"
        track.album = "Untrue LP"
        track.genre = "Future Garage/4x4 Garage"
        track.year = "2007"
        track.bpm = "136"
        track.track_number = "4"
        track.track_total = "13"
        track.publisher = "Hyperdub"
        track.cover = cover_jpg_path

    # 3. Verify changes and JPEG cover persisted on disk
    reopened = AudioFile(sample_mp3)
    assert reopened.title == "Ghost Hardware"
    assert reopened.artist == "Burial"
    assert reopened.album == "Untrue LP"
    assert reopened.genre == "Future Garage/4x4 Garage"
    assert reopened.year == "2007"
    assert reopened.bpm == "136"
    assert reopened.track_number == "4"
    assert reopened.track_total == "13"
    assert reopened.publisher == "Hyperdub"
    assert reopened.cover == cover_jpg_path.read_bytes()

    rec = read_track(sample_mp3)
    assert rec.title == "Ghost Hardware"
    assert rec.artist == "Burial"

    # 4. Replace cover with PNG cover from str path
    with AudioFile(sample_mp3) as track:
        track.cover = str(cover_png_path)

    reopened_png = AudioFile(sample_mp3)
    assert reopened_png.cover == cover_png_path.read_bytes()

    # 5. Delete cover and verify deletion on disk
    reopened_png.delete_cover()
    reopened_png.save()

    reopened_after_del = AudioFile(sample_mp3)
    assert reopened_after_del.cover is None


def test_real_flac_full_lifecycle(
    sample_flac: Path,
    cover_jpg_path: Path,
    cover_png_path: Path,
) -> None:
    """Verify end-to-end tag and cover modifications on real FLAC file."""
    # 1. Read initial state from real FLAC
    audio = AudioFile(sample_flac)
    assert audio.artist == "Iwan 'qubodup' Gabovitch"
    assert audio.fmt == "FLAC"
    assert audio.duration_sec > 15
    assert audio.sample_rate == 48000
    assert audio.cover is None

    # 2. Modify metadata set PNG cover art
    with AudioFile(sample_flac) as track:
        track.title = "Heliov"
        track.artist = "acloudyskye"
        track.album = "Blood Rushing Like Current Through a Powerline"
        track.genre = "Lovestep"
        track.year = "2021"
        track.bpm = "150"
        track.isrc = "QZGWW2027435"
        track.cover = str(cover_png_path)

    # 3. Verify persistence of PNG cover
    reopened = AudioFile(sample_flac)
    assert reopened.title == "Heliov"
    assert reopened.artist == "acloudyskye"
    assert reopened.album == "Blood Rushing Like Current Through a Powerline"
    assert reopened.genre == "Lovestep"
    assert reopened.year == "2021"
    assert reopened.bpm == "150"
    assert reopened.isrc == "QZGWW2027435"
    assert reopened.cover == cover_png_path.read_bytes()

    # 4. Replace cover with JPEG cover from bytes
    with AudioFile(sample_flac) as track:
        track.cover = cover_jpg_path.read_bytes()

    reopened_jpg = AudioFile(sample_flac)
    assert reopened_jpg.cover == cover_jpg_path.read_bytes()

    # 5. Clear cover using del and verify
    del reopened_jpg.cover
    reopened_jpg.save()

    reopened_clean = AudioFile(sample_flac)
    assert reopened_clean.cover is None


def test_facade_cover_functions_on_real_files(
    sample_mp3: Path,
    sample_flac: Path,
    cover_jpg_path: Path,
    cover_png_path: Path,
) -> None:
    """Test read/write/delete cover functions directly on real MP3 and FLAC."""
    jpg_bytes = cover_jpg_path.read_bytes()
    png_bytes = cover_png_path.read_bytes()

    # MP3 direct cover facade
    assert read_cover_bytes(sample_mp3) is None
    write_cover_bytes(sample_mp3, jpg_bytes, mime="image/jpeg")
    assert read_cover_bytes(sample_mp3) == jpg_bytes
    delete_cover(sample_mp3)
    assert read_cover_bytes(sample_mp3) is None

    # FLAC direct cover facade
    assert read_cover_bytes(sample_flac) is None
    write_cover_bytes(sample_flac, png_bytes, mime="image/png")
    assert read_cover_bytes(sample_flac) == png_bytes
    delete_cover(sample_flac)
    assert read_cover_bytes(sample_flac) is None
