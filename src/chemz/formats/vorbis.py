"""Vorbis comments and FLAC picture block metadata handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mutagen.flac import FLAC, Picture as FlacPicture

from ..base import AudioFormatHandler


class VorbisHandler(AudioFormatHandler):
    """Audio format handler for Vorbis comments and embedded pictures in FLAC files."""

    def _set_vorbis_tag(self, tags: FLAC, key: str, value: str) -> None:
        if value:
            tags[key] = [value]
        elif key in tags:
            del tags[key]

    def _delete_vorbis_keys(self, tags: FLAC, keys: tuple[str, ...]) -> None:
        for key in keys:
            if key in tags:
                del tags[key]

    def _set_vorbis_url(self, tags: FLAC, value: str) -> None:
        for key in ("www", "website", "url", "location"):
            if key in tags:
                del tags[key]
        if value:
            tags["www"] = [value]

    def read_metadata(self, path: Path) -> dict[str, Any]:
        """Read Vorbis metadata comments from a FLAC file.

        Args:
            path: Path to the target FLAC file.

        Returns:
            A dictionary containing parsed metadata key-value pairs.
        """
        result: dict[str, Any] = {
            "artist": "",
            "title": "",
            "album": "",
            "album_artist": "",
            "year": "",
            "genre": "",
            "track_number": "",
            "track_total": "",
            "disc_number": "",
            "disc_total": "",
            "bpm": "",
            "initial_key": "",
            "comment": "",
            "original_artist": "",
            "remixer": "",
            "composer": "",
            "conductor": "",
            "group_description": "",
            "subtitle": "",
            "isrc": "",
            "publisher": "",
            "copyright_text": "",
            "url": "",
            "encoder": "",
            "lyrics": "",
            "tag_type": "VORBIS",
        }

        try:
            flac = FLAC(str(path))
        except Exception:
            return result

        result["artist"] = self._first_tag_value(flac, ("artist",))
        result["title"] = self._first_tag_value(flac, ("title",))
        result["album"] = self._first_tag_value(flac, ("album",))
        result["album_artist"] = self._first_tag_value(
            flac, ("albumartist", "album artist")
        )
        result["year"] = self._first_tag_value(flac, ("date", "year"))
        result["genre"] = self._first_tag_value(flac, ("genre",))

        # Track and disc handling
        trk = self._first_tag_value(flac, ("tracknumber",))
        result["track_number"], _ = self._split_number_total(trk)
        result["track_total"] = self._first_tag_value(
            flac, ("tracktotal", "totaltracks")
        )

        dsc = self._first_tag_value(flac, ("discnumber",))
        result["disc_number"], _ = self._split_number_total(dsc)
        result["disc_total"] = self._first_tag_value(flac, ("disctotal", "totaldiscs"))

        result["bpm"] = self._first_tag_value(flac, ("bpm",))
        result["initial_key"] = self._first_tag_value(flac, ("initialkey", "key"))
        result["comment"] = self._first_tag_value(flac, ("comment", "description"))
        result["original_artist"] = self._first_tag_value(
            flac, ("origartist", "originalartist", "original artist")
        )
        result["remixer"] = self._first_tag_value(flac, ("remixer", "remixedby"))
        result["composer"] = self._first_tag_value(flac, ("composer",))
        result["conductor"] = self._first_tag_value(flac, ("conductor",))
        result["group_description"] = self._first_tag_value(
            flac, ("grouping", "contentgroup")
        )
        result["subtitle"] = self._first_tag_value(flac, ("subtitle", "version"))
        result["isrc"] = self._first_tag_value(flac, ("isrc",))
        result["publisher"] = self._first_tag_value(flac, ("organization", "publisher"))
        result["copyright_text"] = self._first_tag_value(flac, ("copyright",))
        result["url"] = self._first_tag_value(
            flac, ("www", "website", "url", "location")
        )
        result["encoder"] = self._first_tag_value(flac, ("encodedby", "encoder"))
        result["lyrics"] = self._first_tag_value(flac, ("lyrics",))

        return result

    def write_metadata(self, path: Path, payload: dict[str, str]) -> None:
        """Write Vorbis metadata comments to a FLAC file.

        Args:
            path: Path to the target FLAC file.
            payload: Dictionary of tag names and their new string values.
        """
        flac = FLAC(str(path))

        if "artist" in payload:
            self._set_vorbis_tag(flac, "artist", payload.get("artist", ""))
        if "title" in payload:
            self._set_vorbis_tag(flac, "title", payload.get("title", ""))
        if "album" in payload:
            self._set_vorbis_tag(flac, "album", payload.get("album", ""))
        if "album_artist" in payload:
            self._set_vorbis_tag(flac, "albumartist", payload.get("album_artist", ""))
        if "year" in payload:
            self._delete_vorbis_keys(flac, ("date", "year"))
            self._set_vorbis_tag(flac, "date", payload.get("year", ""))
        if "genre" in payload:
            self._set_vorbis_tag(flac, "genre", payload.get("genre", ""))
        if "comment" in payload:
            self._set_vorbis_tag(flac, "comment", payload.get("comment", ""))
        if "bpm" in payload:
            self._set_vorbis_tag(flac, "bpm", payload.get("bpm", ""))
        if "initial_key" in payload:
            self._set_vorbis_tag(flac, "initialkey", payload.get("initial_key", ""))
        if "original_artist" in payload:
            self._delete_vorbis_keys(flac, ("origartist", "originalartist"))
            self._set_vorbis_tag(flac, "origartist", payload.get("original_artist", ""))
        if "remixer" in payload:
            self._set_vorbis_tag(flac, "remixer", payload.get("remixer", ""))
        if "composer" in payload:
            self._set_vorbis_tag(flac, "composer", payload.get("composer", ""))
        if "conductor" in payload:
            self._set_vorbis_tag(flac, "conductor", payload.get("conductor", ""))
        if "group_description" in payload:
            self._delete_vorbis_keys(flac, ("grouping", "contentgroup"))
            self._set_vorbis_tag(
                flac, "contentgroup", payload.get("group_description", "")
            )
        if "subtitle" in payload:
            self._set_vorbis_tag(flac, "subtitle", payload.get("subtitle", ""))
        if "isrc" in payload:
            self._set_vorbis_tag(flac, "isrc", payload.get("isrc", ""))
        if "publisher" in payload:
            self._delete_vorbis_keys(flac, ("publisher", "organization", "label"))
            self._set_vorbis_tag(flac, "publisher", payload.get("publisher", ""))
        if "rights" in payload:
            self._set_vorbis_tag(flac, "copyright", payload.get("rights", ""))
        if "url" in payload:
            self._set_vorbis_url(flac, payload.get("url", ""))
        if "encoder" in payload:
            self._delete_vorbis_keys(flac, ("encodedby", "encoder", "encodersettings"))
            self._set_vorbis_tag(flac, "encodedby", payload.get("encoder", ""))
        if "lyrics" in payload:
            self._set_vorbis_tag(flac, "lyrics", payload.get("lyrics", ""))

        if "track_number" in payload or "track_total" in payload:
            # Preserve existing value for whichever half is absent from payload.
            existing_num = self._first_tag_value(flac, ("tracknumber",))
            existing_tot = self._first_tag_value(flac, ("tracktotal", "totaltracks"))
            num = payload.get("track_number", existing_num)
            tot = payload.get("track_total", existing_tot)
            self._set_vorbis_tag(flac, "tracknumber", num)
            self._set_vorbis_tag(flac, "tracktotal", tot)
        if "disc_number" in payload or "disc_total" in payload:
            # Preserve existing value for whichever half is absent from payload.
            existing_num = self._first_tag_value(flac, ("discnumber",))
            existing_tot = self._first_tag_value(flac, ("disctotal", "totaldiscs"))
            num = payload.get("disc_number", existing_num)
            tot = payload.get("disc_total", existing_tot)
            self._set_vorbis_tag(flac, "discnumber", num)
            self._set_vorbis_tag(flac, "disctotal", tot)

        flac.save()

    def read_cover(self, path: Path) -> bytes | None:
        """Read embedded cover picture bytes from a FLAC picture block.

        Args:
            path: Path to the target FLAC file.

        Returns:
            Raw image bytes if a picture block exists, otherwise None.
        """
        try:
            flac = FLAC(str(path))
            if flac.pictures:
                return flac.pictures[0].data
        except Exception:
            pass
        return None

    def write_cover(self, path: Path, data: bytes, mime: str = "image/jpeg") -> None:
        """Write or replace embedded cover picture block in a FLAC file.

        Args:
            path: Path to the target FLAC file.
            data: Raw image bytes to embed.
            mime: MIME type string of the image (default is 'image/jpeg').
        """
        flac = FLAC(str(path))
        pic = FlacPicture()
        pic.data = data
        pic.mime = mime
        pic.type = 3  # Cover (front)
        flac.clear_pictures()
        flac.add_picture(pic)
        flac.save()

    def delete_cover(self, path: Path) -> None:
        """Remove all embedded picture blocks from a FLAC file.

        Args:
            path: Path to the target FLAC file.
        """
        flac = FLAC(str(path))
        flac.clear_pictures()
        flac.save()
