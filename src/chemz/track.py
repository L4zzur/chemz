"""High-level object-oriented interface for audio metadata and cover art management."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from .core import (
    delete_cover,
    read_cover_bytes,
    read_track,
    write_cover_bytes,
    write_track_tags,
)
from .models import TrackRecord


class AudioFile:
    """High-level object-oriented interface for audio metadata and cover art management.

    Provides intuitive property getters and setters for all common metadata tags,
    read-only stream properties, cover art manipulation, and automatic saving
    via context manager support.

    Attributes:
        path: Path to the audio file.
        filename: Filename of the audio file.
        duration_sec: Playback duration in seconds.
        duration: Alias for duration_sec.
        bitrate_kbps: Bitrate in kilobits per second.
        bitrate: Alias for bitrate_kbps.
        sample_rate: Sample rate in Hz.
        channels: Number of audio channels.
        bits_per_sample: Bits per sample.
        fmt: Uppercase format extension (e.g. 'MP3', 'FLAC').
        tag_type: Detected tag specification.
        tags: Raw dictionary of tags.
        record: Current underlying TrackRecord instance.
        cover: Embedded cover art image bytes, or None.
        artist: Lead artist or performer.
        title: Title of the song or track.
        album: Album name.
        album_artist: Primary album artist.
        year: Year or release date.
        genre: Musical genre.
        track_number: Track index.
        track_total: Total number of tracks.
        disc_number: Disc index.
        disc_total: Total number of discs.
        bpm: Beats per minute.
        initial_key: Musical key notation.
        comment: User comment text.
        original_artist: Original artist name.
        remixer: Remixer or producer name.
        composer: Composer name.
        conductor: Conductor name.
        group_description: Content group description.
        subtitle: Subtitle or version text.
        isrc: ISRC code.
        publisher: Label or publisher organization.
        copyright_text: Legal copyright notice.
        rights: Alias for copyright_text.
        url: Source or website URL.
        encoder: Encoding tool or settings.
        lyrics: Unsynchronized lyrics.
    """

    __slots__ = (
        "_cached_cover",
        "_changes",
        "_cover_action",
        "_cover_loaded",
        "_new_cover_data",
        "_new_cover_mime",
        "_path",
        "_record",
    )

    def __init__(self, path: str | Path) -> None:
        """Initialize an AudioFile instance and load its metadata.

        Args:
            path: Filesystem path to the audio file (string or Path object).
        """
        self._path: Path = Path(path)
        self._changes: dict[str, str] = {}
        self._cover_action: Literal["keep", "set", "delete"] = "keep"
        self._new_cover_data: bytes | None = None
        self._new_cover_mime: str = "image/jpeg"
        self._cached_cover: bytes | None = None
        self._cover_loaded: bool = False
        self._record: TrackRecord
        self.reload()

    def reload(self) -> AudioFile:
        """Reload metadata from the disk, discarding any unsaved changes.

        Returns:
            The current AudioFile instance with refreshed metadata.
        """
        self._record = read_track(self._path)
        self._changes.clear()
        self._cover_action = "keep"
        self._new_cover_data = None
        self._new_cover_mime = "image/jpeg"
        self._cached_cover = None
        self._cover_loaded = False
        return self

    def save(self) -> None:
        """Save pending tag changes and cover art updates to disk.

        Flushes all accumulated modifications to the underlying audio file
        and performs a reload to synchronize internal state.
        """
        if self._changes:
            write_track_tags(self._path, dict(self._changes))

        if self._cover_action == "delete":
            delete_cover(self._path)
        elif self._cover_action == "set" and self._new_cover_data is not None:
            write_cover_bytes(self._path, self._new_cover_data, self._new_cover_mime)

        self.reload()

    def __enter__(self) -> AudioFile:
        """Enter context manager block."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit context manager block, saving changes if no exception occurred."""
        if exc_type is None:
            self.save()

    # --- Read-Only Stream & File Info ---

    @property
    def path(self) -> Path:
        """Path: Filesystem path to the audio file."""
        return self._path

    @property
    def filename(self) -> str:
        """str: Filename of the audio file with extension."""
        return self._path.name

    @property
    def duration_sec(self) -> float:
        """float: Playback duration in seconds."""
        return self._record.duration_sec

    @property
    def duration(self) -> float:
        """float: Alias for duration_sec."""
        return self._record.duration_sec

    @property
    def bitrate_kbps(self) -> int:
        """int: Audio bitrate in kbps."""
        return self._record.bitrate_kbps

    @property
    def bitrate(self) -> int:
        """int: Alias for bitrate_kbps."""
        return self._record.bitrate_kbps

    @property
    def sample_rate(self) -> int:
        """int: Audio sample rate in Hz."""
        return self._record.sample_rate

    @property
    def channels(self) -> int:
        """int: Number of audio channels (e.g. 1 for mono, 2 for stereo)."""
        return self._record.channels

    @property
    def bits_per_sample(self) -> int:
        """int: Bit depth per audio sample (e.g. 16, 24)."""
        return self._record.bits_per_sample

    @property
    def fmt(self) -> str:
        """str: Uppercase format extension (e.g. 'MP3', 'FLAC')."""
        return self._record.fmt

    @property
    def tag_type(self) -> str:
        """str: Formatted tag specification version (e.g. 'ID3v2.4 utf8', 'VORBIS')."""
        return self._record.tag_type

    @property
    def tags(self) -> dict[str, Any]:
        """dict[str, Any]: Raw tag dictionary from the underlying engine."""
        return self._record.tags

    @property
    def record(self) -> TrackRecord:
        """TrackRecord: Current underlying data snapshot."""
        return self._record

    # --- Metadata Tag Properties (Getters & Setters) ---

    @property
    def artist(self) -> str:
        """str: Lead artist or performer."""
        return self._changes.get("artist", self._record.artist)

    @artist.setter
    def artist(self, value: Any) -> None:
        self._changes["artist"] = "" if value is None else str(value)

    @property
    def title(self) -> str:
        """str: Title of the track."""
        return self._changes.get("title", self._record.title)

    @title.setter
    def title(self, value: Any) -> None:
        self._changes["title"] = "" if value is None else str(value)

    @property
    def album(self) -> str:
        """str: Album or release name."""
        return self._changes.get("album", self._record.album)

    @album.setter
    def album(self, value: Any) -> None:
        self._changes["album"] = "" if value is None else str(value)

    @property
    def album_artist(self) -> str:
        """str: Primary artist for the whole album."""
        return self._changes.get("album_artist", self._record.album_artist)

    @album_artist.setter
    def album_artist(self, value: Any) -> None:
        self._changes["album_artist"] = "" if value is None else str(value)

    @property
    def year(self) -> str:
        """str: Release year or date."""
        return self._changes.get("year", self._record.year)

    @year.setter
    def year(self, value: Any) -> None:
        self._changes["year"] = "" if value is None else str(value)

    @property
    def genre(self) -> str:
        """str: Musical genre."""
        return self._changes.get("genre", self._record.genre)

    @genre.setter
    def genre(self, value: Any) -> None:
        self._changes["genre"] = "" if value is None else str(value)

    @property
    def track_number(self) -> str:
        """str: Track index on the medium."""
        return self._changes.get("track_number", self._record.track_number)

    @track_number.setter
    def track_number(self, value: Any) -> None:
        self._changes["track_number"] = "" if value is None else str(value)

    @property
    def track_total(self) -> str:
        """str: Total number of tracks on the medium."""
        return self._changes.get("track_total", self._record.track_total)

    @track_total.setter
    def track_total(self, value: Any) -> None:
        self._changes["track_total"] = "" if value is None else str(value)

    @property
    def disc_number(self) -> str:
        """str: Disc index in a multi-disc set."""
        return self._changes.get("disc_number", self._record.disc_number)

    @disc_number.setter
    def disc_number(self, value: Any) -> None:
        self._changes["disc_number"] = "" if value is None else str(value)

    @property
    def disc_total(self) -> str:
        """str: Total number of discs in the set."""
        return self._changes.get("disc_total", self._record.disc_total)

    @disc_total.setter
    def disc_total(self, value: Any) -> None:
        self._changes["disc_total"] = "" if value is None else str(value)

    @property
    def bpm(self) -> str:
        """str: Tempo in beats per minute."""
        return self._changes.get("bpm", self._record.bpm)

    @bpm.setter
    def bpm(self, value: Any) -> None:
        self._changes["bpm"] = "" if value is None else str(value)

    @property
    def initial_key(self) -> str:
        """str: Initial musical key notation (e.g. '8A', 'C#m')."""
        return self._changes.get("initial_key", self._record.initial_key)

    @initial_key.setter
    def initial_key(self, value: Any) -> None:
        self._changes["initial_key"] = "" if value is None else str(value)

    @property
    def comment(self) -> str:
        """str: User comment or description."""
        return self._changes.get("comment", self._record.comment)

    @comment.setter
    def comment(self, value: Any) -> None:
        self._changes["comment"] = "" if value is None else str(value)

    @property
    def original_artist(self) -> str:
        """str: Original artist for cover versions or remixes."""
        return self._changes.get("original_artist", self._record.original_artist)

    @original_artist.setter
    def original_artist(self, value: Any) -> None:
        self._changes["original_artist"] = "" if value is None else str(value)

    @property
    def remixer(self) -> str:
        """str: Remixer or producer name."""
        return self._changes.get("remixer", self._record.remixer)

    @remixer.setter
    def remixer(self, value: Any) -> None:
        self._changes["remixer"] = "" if value is None else str(value)

    @property
    def composer(self) -> str:
        """str: Composer name."""
        return self._changes.get("composer", self._record.composer)

    @composer.setter
    def composer(self, value: Any) -> None:
        self._changes["composer"] = "" if value is None else str(value)

    @property
    def conductor(self) -> str:
        """str: Conductor name."""
        return self._changes.get("conductor", self._record.conductor)

    @conductor.setter
    def conductor(self, value: Any) -> None:
        self._changes["conductor"] = "" if value is None else str(value)

    @property
    def group_description(self) -> str:
        """str: Content group or grouping description."""
        return self._changes.get("group_description", self._record.group_description)

    @group_description.setter
    def group_description(self, value: Any) -> None:
        self._changes["group_description"] = "" if value is None else str(value)

    @property
    def subtitle(self) -> str:
        """str: Subtitle or version description."""
        return self._changes.get("subtitle", self._record.subtitle)

    @subtitle.setter
    def subtitle(self, value: Any) -> None:
        self._changes["subtitle"] = "" if value is None else str(value)

    @property
    def isrc(self) -> str:
        """str: International Standard Recording Code."""
        return self._changes.get("isrc", self._record.isrc)

    @isrc.setter
    def isrc(self, value: Any) -> None:
        self._changes["isrc"] = "" if value is None else str(value)

    @property
    def publisher(self) -> str:
        """str: Record label or publisher organization."""
        return self._changes.get("publisher", self._record.publisher)

    @publisher.setter
    def publisher(self, value: Any) -> None:
        self._changes["publisher"] = "" if value is None else str(value)

    @property
    def copyright_text(self) -> str:
        """str: Copyright and legal notice text."""
        return self._changes.get("rights", self._record.copyright_text)

    @copyright_text.setter
    def copyright_text(self, value: Any) -> None:
        self._changes["rights"] = "" if value is None else str(value)

    @property
    def rights(self) -> str:
        """str: Alias for copyright_text."""
        return self.copyright_text

    @rights.setter
    def rights(self, value: Any) -> None:
        self.copyright_text = value

    @property
    def url(self) -> str:
        """str: Official source or website URL."""
        return self._changes.get("url", self._record.url)

    @url.setter
    def url(self, value: Any) -> None:
        self._changes["url"] = "" if value is None else str(value)

    @property
    def encoder(self) -> str:
        """str: Encoder tool or encoding settings used."""
        return self._changes.get("encoder", self._record.encoder)

    @encoder.setter
    def encoder(self, value: Any) -> None:
        self._changes["encoder"] = "" if value is None else str(value)

    @property
    def lyrics(self) -> str:
        """str: Unsynchronized lyrics text."""
        return self._changes.get("lyrics", self._record.lyrics)

    @lyrics.setter
    def lyrics(self, value: Any) -> None:
        self._changes["lyrics"] = "" if value is None else str(value)

    # --- Cover Art Management ---

    @property
    def cover(self) -> bytes | None:
        """bytes | None: Embedded cover art image bytes, or None if not present."""
        if self._cover_action == "delete":
            return None
        if self._cover_action == "set":
            return self._new_cover_data
        if not self._cover_loaded:
            self._cached_cover = read_cover_bytes(self._path)
            self._cover_loaded = True
        return self._cached_cover

    @cover.setter
    def cover(self, data: bytes | Path | str | None) -> None:
        if data is None:
            self.delete_cover()
        else:
            self.set_cover(data)

    @cover.deleter
    def cover(self) -> None:
        self.delete_cover()

    def set_cover(
        self,
        data: bytes | Path | str,
        mime: str = "image/jpeg",
    ) -> None:
        """Set cover art from image bytes or a file path.

        Automatically infers MIME type for .png and .webp files if mime is default.

        Args:
            data: Raw image bytes, or Path/string pointing to an image file.
            mime: MIME type string (default is 'image/jpeg').

        Raises:
            TypeError: If data is not bytes, Path, or str.
        """
        if isinstance(data, (str, Path)):
            path_obj = Path(data)
            raw_data = path_obj.read_bytes()
            suffix = path_obj.suffix.lower()
            if mime == "image/jpeg":
                if suffix == ".png":
                    mime = "image/png"
                elif suffix == ".webp":
                    mime = "image/webp"
            data = raw_data
        elif not isinstance(data, bytes):
            raise TypeError("Cover data must be bytes, Path, str, or None")

        self._cover_action = "set"
        self._new_cover_data = data
        self._new_cover_mime = mime

    def delete_cover(self) -> None:
        """Mark embedded cover art for deletion upon save."""
        self._cover_action = "delete"
        self._new_cover_data = None

    # --- Representations & Export ---

    def to_dict(self) -> dict[str, Any]:
        """Convert current track metadata and audio properties to a dictionary.

        Returns:
            A dictionary containing all current metadata and technical stream fields.
        """
        return {
            "path": self.path,
            "filename": self.filename,
            "artist": self.artist,
            "title": self.title,
            "album": self.album,
            "album_artist": self.album_artist,
            "year": self.year,
            "genre": self.genre,
            "track_number": self.track_number,
            "track_total": self.track_total,
            "disc_number": self.disc_number,
            "disc_total": self.disc_total,
            "bpm": self.bpm,
            "initial_key": self.initial_key,
            "comment": self.comment,
            "original_artist": self.original_artist,
            "remixer": self.remixer,
            "composer": self.composer,
            "conductor": self.conductor,
            "group_description": self.group_description,
            "subtitle": self.subtitle,
            "isrc": self.isrc,
            "publisher": self.publisher,
            "copyright_text": self.copyright_text,
            "url": self.url,
            "encoder": self.encoder,
            "lyrics": self.lyrics,
            "fmt": self.fmt,
            "duration_sec": self.duration_sec,
            "bitrate_kbps": self.bitrate_kbps,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bits_per_sample": self.bits_per_sample,
            "tag_type": self.tag_type,
        }

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the AudioFile."""
        return (
            f"AudioFile(path={self._path!r}, "
            f"artist={self.artist!r}, "
            f"title={self.title!r}, "
            f"fmt={self.fmt!r})"
        )
