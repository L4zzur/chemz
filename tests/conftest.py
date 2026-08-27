"""Shared pytest fixtures and test helpers for chemz test suite."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def mp3_fixture_path() -> Path:
    """Path to the master MP3 fixture file."""
    return FIXTURES_DIR / "18021__walter_odington__london.mp3"


@pytest.fixture
def flac_fixture_path() -> Path:
    """Path to the master FLAC fixture file."""
    return FIXTURES_DIR / "211624__qubodup__magic-wand-glitter.flac"


@pytest.fixture
def cover_jpg_path() -> Path:
    """Path to the master JPG cover fixture file."""
    return FIXTURES_DIR / "cover.jpg"


@pytest.fixture
def cover_png_path() -> Path:
    """Path to the master PNG cover fixture file."""
    return FIXTURES_DIR / "cover.png"


@pytest.fixture
def cover_webp_path() -> Path:
    """Path to the master WebP cover fixture file."""
    return FIXTURES_DIR / "cover.webp"


@pytest.fixture
def sample_mp3(tmp_path: Path, mp3_fixture_path: Path) -> Path:
    """Provide an isolated, temporary copy of the real MP3 fixture file."""
    dest = tmp_path / "test_track.mp3"
    shutil.copyfile(mp3_fixture_path, dest)
    return dest


@pytest.fixture
def sample_flac(tmp_path: Path, flac_fixture_path: Path) -> Path:
    """Provide an isolated, temporary copy of the real FLAC fixture file."""
    dest = tmp_path / "test_track.flac"
    shutil.copyfile(flac_fixture_path, dest)
    return dest
