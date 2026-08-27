"""ID3 metadata and cover art handler for MP3 files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mutagen.id3 import (
    APIC,
    COMM,
    ID3,
    TALB,
    TBPM,
    TCOM,
    TCON,
    TCOP,
    TDRC,
    TENC,
    TIT1,
    TIT2,
    TIT3,
    TKEY,
    TOPE,
    TPE1,
    TPE2,
    TPE3,
    TPE4,
    TPOS,
    TPUB,
    TRCK,
    TSRC,
    TSSE,
    TXXX,
    TYER,
    USLT,
    WXXX,
    ID3NoHeaderError,
)

from ..base import AudioFormatHandler


class ID3Handler(AudioFormatHandler):
    """Audio format handler for ID3v2.3 and ID3v2.4 tags in MP3 files."""

    def _id3_first_text(self, id3: ID3, frame_id: str) -> str:
        """Extract first text value from a specific ID3 frame ID."""
        frames = id3.getall(frame_id)
        if not frames:
            return ""
        frame = frames[0]
        text = getattr(frame, "text", None)
        if isinstance(text, list) and text:
            return str(text[0]).strip()
        if text is not None:
            return str(text).strip()
        return ""

    def _id3_first_comment(self, id3: ID3) -> str:
        frames = id3.getall("COMM")
        if not frames:
            return ""
        text = getattr(frames[0], "text", "")
        if isinstance(text, list) and text:
            return str(text[0]).strip()
        return str(text).strip() if text else ""

    def _id3_first_lyrics(self, id3: ID3) -> str:
        frames = id3.getall("USLT")
        if not frames:
            return ""
        text = getattr(frames[0], "text", "")
        return str(text).strip() if text else ""

    def _id3_first_url(self, id3: ID3) -> str:
        wxxx = id3.getall("WXXX")
        if wxxx:
            preferred: list[str] = []
            other: list[str] = []
            for frame in wxxx:
                url = str(getattr(frame, "url", "")).strip()
                if not url:
                    continue
                desc = str(getattr(frame, "desc", "")).strip().lower()
                if desc in {"", "www", "url"}:
                    preferred.append(url)
                else:
                    other.append(url)
            if preferred:
                return preferred[0]
            if other:
                return other[0]
        for frame_id in ("WOAR", "WOAS", "WOAF", "WORS", "WPUB"):
            frames = id3.getall(frame_id)
            if not frames:
                continue
            url = getattr(frames[0], "url", None)
            if url:
                return str(url).strip()
        return ""

    def _id3_first_user_text(self, id3: ID3, descriptions: tuple[str, ...]) -> str:
        desc_set = {x.lower() for x in descriptions}
        for frame in id3.getall("TXXX"):
            desc = str(getattr(frame, "desc", "")).strip().lower()
            if desc not in desc_set:
                continue
            text = getattr(frame, "text", None)
            if isinstance(text, list) and text:
                return str(text[0]).strip()
            if text is not None:
                return str(text).strip()
        return ""

    def _remove_txxx_descriptions(
        self, id3: ID3, descriptions: tuple[str, ...]
    ) -> None:
        desc_set = {x.lower() for x in descriptions}
        keep: list[TXXX] = []
        for frame in id3.getall("TXXX"):
            desc = str(getattr(frame, "desc", "")).strip().lower()
            if desc in desc_set:
                continue
            keep.append(frame)
        id3.delall("TXXX")
        for frame in keep:
            id3.add(frame)

    def _set_id3_text(self, id3: ID3, frame_id: str, frame) -> None:
        id3.delall(frame_id)
        id3.add(frame)

    def read_metadata(self, path: Path) -> dict[str, Any]:
        """Read ID3 metadata tags from an MP3 file.

        Args:
            path: Path to the target MP3 file.

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
            "tag_type": "ID3",
        }

        try:
            id3 = ID3(str(path))
        except Exception:
            return result

        ver = getattr(id3, "version", None)
        if isinstance(ver, tuple) and len(ver) >= 2:
            major, revision = ver[0], ver[1]
            encoding_text = ""
            for frame in id3.values():
                encoding = getattr(frame, "encoding", None)
                if encoding is None:
                    continue
                encoding_map = {0: "latin1", 1: "utf16", 2: "utf16be", 3: "utf8"}
                encoding_text = encoding_map.get(int(encoding), "")
                if encoding_text:
                    break
            if encoding_text:
                result["tag_type"] = f"ID3v{major}.{revision} {encoding_text}"
            else:
                result["tag_type"] = f"ID3v{major}.{revision}"

        result["artist"] = self._id3_first_text(id3, "TPE1")
        result["title"] = self._id3_first_text(id3, "TIT2")
        result["album"] = self._id3_first_text(id3, "TALB")
        result["album_artist"] = self._id3_first_text(id3, "TPE2")
        result["year"] = (
            self._id3_first_text(id3, "TDRC")
            or self._id3_first_text(id3, "TYER")
            or self._id3_first_user_text(id3, ("year", "date"))
        )
        result["genre"] = self._id3_first_text(id3, "TCON")

        trck = self._id3_first_text(id3, "TRCK")
        result["track_number"], result["track_total"] = self._split_number_total(trck)

        tpos = self._id3_first_text(id3, "TPOS")
        result["disc_number"], result["disc_total"] = self._split_number_total(tpos)

        result["bpm"] = self._id3_first_text(id3, "TBPM")
        result["comment"] = self._id3_first_comment(id3)
        result["initial_key"] = self._id3_first_text(id3, "TKEY")
        result["original_artist"] = self._id3_first_text(id3, "TOPE")
        result["remixer"] = self._id3_first_text(id3, "TPE4")
        result["composer"] = self._id3_first_text(id3, "TCOM")
        result["conductor"] = self._id3_first_text(id3, "TPE3")
        result["group_description"] = self._id3_first_text(id3, "TIT1")
        result["subtitle"] = self._id3_first_text(id3, "TIT3")
        result["isrc"] = self._id3_first_text(id3, "TSRC")
        result["publisher"] = self._id3_first_text(
            id3, "TPUB"
        ) or self._id3_first_user_text(id3, ("publisher", "organization", "label"))
        result["copyright_text"] = self._id3_first_text(id3, "TCOP")
        result["url"] = self._id3_first_url(id3)
        result["encoder"] = self._id3_first_text(id3, "TENC") or self._id3_first_text(
            id3, "TSSE"
        )
        result["lyrics"] = self._id3_first_lyrics(id3)

        return result

    def write_metadata(self, path: Path, payload: dict[str, str]) -> None:
        """Write ID3 metadata tags to an MP3 file.

        Args:
            path: Path to the target MP3 file.
            payload: Dictionary of tag names and their new string values.
        """
        try:
            id3 = ID3(str(path))
        except ID3NoHeaderError:
            id3 = ID3()

        if "artist" in payload:
            val = payload.get("artist", "")
            if val:
                self._set_id3_text(id3, "TPE1", TPE1(encoding=3, text=val))
            else:
                id3.delall("TPE1")
            self._remove_txxx_descriptions(id3, ("artist",))

        if "title" in payload:
            val = payload.get("title", "")
            if val:
                self._set_id3_text(id3, "TIT2", TIT2(encoding=3, text=val))
            else:
                id3.delall("TIT2")
            self._remove_txxx_descriptions(id3, ("title",))

        if "album" in payload:
            val = payload.get("album", "")
            if val:
                self._set_id3_text(id3, "TALB", TALB(encoding=3, text=val))
            else:
                id3.delall("TALB")
            self._remove_txxx_descriptions(id3, ("album",))

        if "album_artist" in payload:
            val = payload.get("album_artist", "")
            if val:
                self._set_id3_text(id3, "TPE2", TPE2(encoding=3, text=val))
            else:
                id3.delall("TPE2")
            self._remove_txxx_descriptions(id3, ("albumartist", "album artist"))

        if "year" in payload:
            val = payload.get("year", "")
            if val:
                self._set_id3_text(id3, "TDRC", TDRC(encoding=3, text=val))
                self._set_id3_text(id3, "TYER", TYER(encoding=3, text=val))
            else:
                id3.delall("TDRC")
                id3.delall("TYER")
            self._remove_txxx_descriptions(id3, ("year", "date"))

        if "genre" in payload:
            val = payload.get("genre", "")
            if val:
                self._set_id3_text(id3, "TCON", TCON(encoding=3, text=val))
            else:
                id3.delall("TCON")
            self._remove_txxx_descriptions(id3, ("genre",))

        if "comment" in payload:
            val = payload.get("comment", "")
            if val:
                self._set_id3_text(
                    id3, "COMM", COMM(encoding=3, lang="eng", desc="", text=val)
                )
            else:
                id3.delall("COMM")
            self._remove_txxx_descriptions(id3, ("comment", "description"))

        if "bpm" in payload:
            val = payload.get("bpm", "")
            if val:
                self._set_id3_text(id3, "TBPM", TBPM(encoding=3, text=val))
            else:
                id3.delall("TBPM")
            self._remove_txxx_descriptions(id3, ("bpm",))

        if "initial_key" in payload:
            val = payload.get("initial_key", "")
            if val:
                self._set_id3_text(id3, "TKEY", TKEY(encoding=3, text=val))
            else:
                id3.delall("TKEY")
            self._remove_txxx_descriptions(id3, ("key", "initialkey", "initial key"))

        if "original_artist" in payload:
            val = payload.get("original_artist", "")
            if val:
                self._set_id3_text(id3, "TOPE", TOPE(encoding=3, text=val))
            else:
                id3.delall("TOPE")
            self._remove_txxx_descriptions(
                id3, ("origartist", "originalartist", "original artist")
            )

        if "remixer" in payload:
            val = payload.get("remixer", "")
            if val:
                self._set_id3_text(id3, "TPE4", TPE4(encoding=3, text=val))
            else:
                id3.delall("TPE4")
            self._remove_txxx_descriptions(id3, ("remixedby", "remixer"))

        if "composer" in payload:
            val = payload.get("composer", "")
            if val:
                self._set_id3_text(id3, "TCOM", TCOM(encoding=3, text=val))
            else:
                id3.delall("TCOM")
            self._remove_txxx_descriptions(id3, ("composer",))

        if "conductor" in payload:
            val = payload.get("conductor", "")
            if val:
                self._set_id3_text(id3, "TPE3", TPE3(encoding=3, text=val))
            else:
                id3.delall("TPE3")
            self._remove_txxx_descriptions(id3, ("conductor",))

        if "group_description" in payload:
            val = payload.get("group_description", "")
            if val:
                self._set_id3_text(id3, "TIT1", TIT1(encoding=3, text=val))
            else:
                id3.delall("TIT1")
            self._remove_txxx_descriptions(
                id3, ("contentgroup", "grouping", "group description")
            )

        if "subtitle" in payload:
            val = payload.get("subtitle", "")
            if val:
                self._set_id3_text(id3, "TIT3", TIT3(encoding=3, text=val))
            else:
                id3.delall("TIT3")
            self._remove_txxx_descriptions(id3, ("subtitle", "version"))

        if "isrc" in payload:
            val = payload.get("isrc", "")
            if val:
                self._set_id3_text(id3, "TSRC", TSRC(encoding=3, text=val))
            else:
                id3.delall("TSRC")
            self._remove_txxx_descriptions(id3, ("isrc",))

        if "publisher" in payload:
            val = payload.get("publisher", "")
            if val:
                self._set_id3_text(id3, "TPUB", TPUB(encoding=3, text=val))
            else:
                id3.delall("TPUB")
            self._remove_txxx_descriptions(id3, ("publisher", "organization", "label"))

        if "rights" in payload:
            val = payload.get("rights", "")
            if val:
                self._set_id3_text(id3, "TCOP", TCOP(encoding=3, text=val))
            else:
                id3.delall("TCOP")
            self._remove_txxx_descriptions(id3, ("copyright", "rights"))

        if "url" in payload:
            val = payload.get("url", "")
            if val:
                self._set_id3_text(id3, "WXXX", WXXX(encoding=3, desc="", url=val))
            else:
                id3.delall("WXXX")
            self._remove_txxx_descriptions(id3, ("url", "website", "www", "location"))
            for frame_id in ("WOAR", "WOAS", "WOAF", "WORS", "WPUB"):
                id3.delall(frame_id)

        if "encoder" in payload:
            val = payload.get("encoder", "")
            if val:
                self._set_id3_text(id3, "TENC", TENC(encoding=3, text=val))
                self._set_id3_text(id3, "TSSE", TSSE(encoding=3, text=val))
            else:
                id3.delall("TENC")
                id3.delall("TSSE")
            self._remove_txxx_descriptions(id3, ("encodedby", "encoder"))

        if "lyrics" in payload:
            val = payload.get("lyrics", "")
            if val:
                self._set_id3_text(
                    id3, "USLT", USLT(encoding=3, lang="eng", desc="", text=val)
                )
            else:
                id3.delall("USLT")
            self._remove_txxx_descriptions(id3, ("lyrics", "uslt"))

        if "track_number" in payload or "track_total" in payload:
            # Preserve existing value for whichever half is absent from payload.
            existing_trck = self._id3_first_text(id3, "TRCK")
            existing_num, existing_tot = self._split_number_total(existing_trck)
            num = payload.get("track_number", existing_num)
            tot = payload.get("track_total", existing_tot)
            track_val = f"{num}/{tot}" if num and tot else num
            if track_val:
                self._set_id3_text(id3, "TRCK", TRCK(encoding=3, text=track_val))
            else:
                id3.delall("TRCK")

        if "disc_number" in payload or "disc_total" in payload:
            # Preserve existing value for whichever half is absent from payload.
            existing_tpos = self._id3_first_text(id3, "TPOS")
            existing_num, existing_tot = self._split_number_total(existing_tpos)
            num = payload.get("disc_number", existing_num)
            tot = payload.get("disc_total", existing_tot)
            disc_val = f"{num}/{tot}" if num and tot else num
            if disc_val:
                self._set_id3_text(id3, "TPOS", TPOS(encoding=3, text=disc_val))
            else:
                id3.delall("TPOS")

        id3.save(str(path))

    def read_cover(self, path: Path) -> bytes | None:
        """Read embedded cover art image bytes from an MP3 file APIC frame.

        Args:
            path: Path to the target MP3 file.

        Returns:
            Image raw bytes if APIC frame exists, otherwise None.
        """
        try:
            id3 = ID3(str(path))
            for frame in id3.values():
                if isinstance(frame, APIC):
                    return frame.data
        except Exception:
            pass
        return None

    def write_cover(self, path: Path, data: bytes, mime: str = "image/jpeg") -> None:
        """Write or replace embedded cover art in an MP3 file APIC frame.

        Args:
            path: Path to the target MP3 file.
            data: Raw image bytes to embed.
            mime: MIME type string of the image (default is 'image/jpeg').
        """
        try:
            id3 = ID3(str(path))
        except ID3NoHeaderError:
            id3 = ID3()
        id3.delall("APIC")
        id3.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=data))
        id3.save(str(path))

    def delete_cover(self, path: Path) -> None:
        """Remove all embedded APIC cover art frames from an MP3 file.

        Args:
            path: Path to the target MP3 file.
        """
        try:
            id3 = ID3(str(path))
        except ID3NoHeaderError:
            return
        id3.delall("APIC")
        id3.save(str(path))
