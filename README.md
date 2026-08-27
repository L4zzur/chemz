# chemz

<img height="100px" src="https://raw.githubusercontent.com/L4zzur/chemz/main/docs/assets/logo.png" alt="chemz Logo" align="right" />

[![CI](https://github.com/L4zzur/chemz/actions/workflows/ci.yml/badge.svg)](https://github.com/L4zzur/chemz/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/chemz.svg)](https://pypi.org/project/chemz/)
[![Python versions](https://img.shields.io/pypi/pyversions/chemz.svg)](https://pypi.org/project/chemz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Typed: PEP 561](https://img.shields.io/badge/typing-PEP%20561-blueviolet.svg)](src/chemz/py.typed)

`chemz` is a strictly-typed Python library for reading, updating, and managing audio metadata (tags) and embedded cover art across **MP3** (ID3v2) and **FLAC** (Vorbis Comments) files.

---

## Installation

```bash
# uv
uv add chemz

# pip
pip install chemz
```

---

## Usage

### 1. `AudioFile` Interface

`AudioFile` provides an object-oriented wrapper with property getters and setters for all common metadata fields, read-only stream technical properties, and context manager support for automatic persistence:

```python
from pathlib import Path
from chemz import AudioFile

# Context manager automatically saves changes on exit
with AudioFile("track.mp3") as audio:
    audio.artist = "Burial"
    audio.title = "Chemz"
    audio.album = "Chemz / Dolphinz"
    audio.year = 2021
    audio.genre = "Atmospheric Breaks/Breakbeat/Big Beat"
    audio.bpm = 146
    audio.track_number = 1
    audio.track_total = 2
    audio.isrc = "GBLZC2000101"
    
    # Assign cover from Path or str (automatically detects MIME type)
    audio.cover = "cover.jpg"
```

Manual save and reload:

```python
audio = AudioFile("track.flac")
audio.title = "Spill"
audio.artist = "acloudyskye"
audio.save()    # Writes changes to disk

audio.title = "Temporary Title"
audio.reload()  # Discards unsaved changes
```

### 2. Audio Stream Properties

Technical stream attributes are extracted directly from the audio header and exposed as read-only properties:

```python
audio = AudioFile("recording.flac")

duration: float = audio.duration_sec   # Length in seconds (e.g. 248.5)
bitrate: int    = audio.bitrate_kbps   # Bitrate in kbps (e.g. 320 or FLAC stream rate)
sample_rate: int = audio.sample_rate   # Sampling rate in Hz (e.g. 44100, 48000)
channels: int   = audio.channels       # Channel count (1 for mono, 2 for stereo)
fmt: str        = audio.fmt            # Format identifier ("MP3" or "FLAC")
```

### 3. Cover Art Management

Cover art can be read, updated, or removed using the `cover` property or dedicated methods:

```python
audio = AudioFile("track.mp3")

# Read cover art as raw bytes (returns None if no cover exists)
cover_bytes: bytes | None = audio.cover

# Assign cover from raw bytes, Path, or string path
audio.cover = Path("artwork.png")   # Inferred MIME: image/png
audio.cover = "artwork.webp"        # Inferred MIME: image/webp
audio.cover = b"..."                # Explicit bytes (default MIME: image/jpeg)

# Delete cover art
del audio.cover
# or: audio.cover = None
# or: audio.delete_cover()

audio.save()
```

### 4. Functional API

For procedural scripts, `chemz` provides direct stateless facade functions:

```python
from chemz import read_track, write_track_tags, read_cover_bytes, write_cover_bytes, delete_cover

# Read metadata snapshot into a TrackRecord dataclass
record = read_track("track.mp3")
print(record.artist, record.title, record.duration_sec)

# Write dictionary of tags
write_track_tags("track.mp3", {
    "artist": "Burial",
    "title": "Chemz",
    "bpm": "146",
})

# Cover operations
cover = read_cover_bytes("track.mp3")
write_cover_bytes("track.flac", cover, mime="image/jpeg")
delete_cover("track.mp3")
```

---

## Supported Formats & Fields

| Format | Extension | Metadata Engine | Cover Art Implementation |
| :--- | :--- | :--- | :--- |
| **MP3** | `.mp3` | ID3v2.3 / ID3v2.4 | `APIC` frame |
| **FLAC** | `.flac` | Vorbis Comments | `METADATA_BLOCK_PICTURE` |

### Tag Mapping Reference

| Field | MP3 (ID3v2 Frame) | FLAC (Vorbis Comment) |
| :--- | :--- | :--- |
| `title` | `TIT2` | `TITLE` |
| `artist` | `TPE1` | `ARTIST` |
| `album` | `TALB` | `ALBUM` |
| `album_artist` | `TPE2` | `ALBUMARTIST` |
| `year` | `TDRC` / `TYER` | `DATE` / `YEAR` |
| `genre` | `TCON` | `GENRE` |
| `track_number` / `track_total` | `TRCK` (`n/total`) | `TRACKNUMBER` / `TRACKTOTAL` |
| `disc_number` / `disc_total` | `TPOS` (`n/total`) | `DISCNUMBER` / `DISCTOTAL` |
| `bpm` | `TBPM` | `BPM` |
| `initial_key` | `TKEY` | `INITIALKEY` / `KEY` |
| `comment` | `COMM` | `COMMENT` / `DESCRIPTION` |
| `isrc` | `TSRC` | `ISRC` |
| `publisher` | `TPUB` | `ORGANIZATION` / `PUBLISHER` |
| `copyright_text` (`rights`) | `TCOP` | `COPYRIGHT` / `RIGHTS` |
| `composer` | `TCOM` | `COMPOSER` |
| `conductor` | `TPE3` | `CONDUCTOR` |
| `remixer` | `TPE4` | `REMIXER` / `MIXARTIST` |
| `original_artist` | `TOPE` | `ORIGINALARTIST` |
| `subtitle` | `TIT3` | `SUBTITLE` |
| `group_description` | `TIT1` | `GROUPING` |
| `lyrics` | `USLT` | `LYRICS` / `UNSYNCEDLYRICS` |
| `url` | `WXXX:URL` / `WOAR` | `URL` / `WEBSITE` |
| `encoder` | `TSSE` | `ENCODER` / `ENCODED-BY` |

---

## Development

### Setup

```bash
git clone https://github.com/L4zzur/chemz.git
cd chemz
uv sync
```

### Running Checks

```bash
# Test suite
uv run pytest

# Static type checking
uv run ty check

# Linting and formatting
uv run ruff check .
uv run ruff format --check .
```

---

## License

chemz is licensed under the [MIT License](LICENSE).