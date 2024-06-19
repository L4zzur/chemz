from abc import ABC, abstractmethod
from pathlib import Path

from PIL.Image import Image


class Track(ABC):
    """A class representing an audio track."""

    __slots__ = (
        "album",
        "albumartist",
        "artist",
        "bpm",
        "comment",
        "composer",
        "conductor",
        "contentgroup",
        "copyright",
        "cover",
        "disc",
        "encodedby",
        "genre",
        "initialkey",
        "isrc",
        "lyricist",
        "lyrics",
        "origartist",
        "path",
        "publisher",
        "remixedby",
        "subtitle",
        "title",
        "totaldiscs",
        "totaltracks",
        "track",
        "www",
        "year",
    )

    @abstractmethod
    def read(self) -> None:
        """Read track data from an external audio."""
        ...

    @abstractmethod
    def save(self) -> None:
        """Saves track data to an external audio."""
        ...

    @abstractmethod
    def read_cover(self) -> Image | None:
        """Reads the cover image.

        Returns:
            Image: The cover image. Returns None if no cover is found.
        """
        ...

    @abstractmethod
    def add_cover(self, path: Path, desc: str = "") -> None:
        """Adds a cover at the given path."""
        pass

    @abstractmethod
    def export_cover(self) -> Path:
        """Saves the cover image and returns the path.

        Returns:
            Path: The path where the cover image was saved.
        """
        ...

    @abstractmethod
    def remove_cover(self) -> None:
        """Removes the track cover."""
        ...

    @abstractmethod
    def delete_tag(self) -> None:
        """Delete the tag."""
        ...

    @abstractmethod
    def delete_tags(self) -> None:
        """Delete all tags."""
        ...

    def import_from_dict(self, _dict: dict) -> None:
        """Imports track data from a dictionary.

        Args:
            _dict (dict): The dictionary to import track data from.

        Raises:
            AttributeError: If a key in the dictionary does not match
            an attribute in the Track class.
        """
        for key, value in _dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute {key} not found in Track class")

    def export_to_dict(self) -> dict:
        """Exports track data to a dictionary.

        Returns:
            dict: A dictionary containing all track attributes, excluding 'path' and 'cover'.
        """
        _dict = {}
        for key in self.__slots__:
            if key not in {"path", "cover"}:
                _dict[key] = getattr(self, key, None)
        return _dict

    def call_method(self, method: str) -> None:
        """Calls a method on the track."""
        method_callable = getattr(self, method, None)
        if method_callable and callable(method_callable):
            method_callable()
        else:
            raise AttributeError(f"Method {method} not found in Track class")

    def __str__(self) -> str:
        """Returns a string representation of the track."""
        return (
            f"\tGeneral Info\n"
            f"Disc Number: {self.disc} Disc Total: {self.totaldiscs}\n"
            f"Track Number: {self.track} Track Total: {self.totaltracks}\n"
            f"Title: {self.title}\n"
            f"Artist: {self.artist}\n"
            f"Album: {self.album}\n"
            f"Album Artist: {self.albumartist}\n"
            f"Year: {self.year}\n"
            f"Track Genre: {self.genre}\n"
            f"Comment: {self.comment}\n"
            f"BPM: {self.bpm} Key: {self.initialkey}\n\n"
            f"\tExtended Info\n"
            f"Original Artist: {self.origartist}\n"
            f"Remixer: {self.remixedby}\n"
            f"Composer: {self.composer}\n"
            f"Conductor: {self.conductor}\n"
            f"Group: {self.contentgroup}\n"
            f"Subtitle: {self.subtitle}\n"
            f"ISRC: {self.isrc}\n"
            f"Publisher: {self.publisher}\n"
            f"Copyright: {self.copyright}\n"
            f"URL: {self.www}\n"
            f"Encoded By: {self.encodedby}\n\n"
            f"\tLyrics\n"
            f"Lyricist: {self.lyricist}\n"
            f"Lyrics: {self.lyrics}"
        )
