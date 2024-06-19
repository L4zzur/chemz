from functools import wraps
from io import BytesIO
from pathlib import Path

from mutagen.flac import FLAC, Picture
from PIL import Image

from icecream import ic

from .base import Track
from .exceptions import (
    NoCoverFoundError,
    WrongFLACAttributeError,
    WrongPictureFormatError,
)


class FLACTrack(Track):

    __slots__ = Track.__slots__ + ("flac",)

    attrs = {
        "album": "album",
        "albumartist": "albumartist",
        "artist": "artist",
        "bpm": "bpm",
        "comment": "comment",
        "composer": "composer",
        "conductor": "conductor",
        "contentgroup": "contentgroup",
        "copyright": "copyright",
        "disc": "discnumber",
        "encodedby": "encodedby",
        "genre": "genre",
        "initialkey": "initialkey",
        "isrc": "isrc",
        "lyricist": "lyricist",
        "lyrics": "lyrics",
        "origartist": "origartist",
        "publisher": "organization",
        "remixedby": "remixedby",
        "subtitle": "subtitle",
        "title": "title",
        "totaldiscs": "disctotal",
        "totaltracks": "tracktotal",
        "track": "tracknumber",
        "www": "location",
        "year": "date",
    }

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.flac = FLAC(path)
        self.read()
        self.read_cover()

    def export_to_dict(self) -> dict:
        _dict = super().export_to_dict()
        _dict.pop("flac", None)
        return _dict

    def read(self) -> None:
        for key, value in self.attrs.items():
            self.__setattr__(key, self.flac.get(value, [None])[0])

    def save(self):
        for key, value in self.attrs.items():
            attr_value = getattr(self, key, "")
            if attr_value is None:
                attr_value = ""
            self.flac[value] = attr_value
        self.flac.save(self.path)

    def delete_tag(self, tag: str):
        if tag in self.attrs.items():
            self.flac.pop(tag)
        else:
            raise WrongFLACAttributeError()

    def delete_tags(self):
        self.flac.delete()

    def read_cover(self) -> Image.Image | None:
        if self.flac.pictures:
            self.cover = Image.open(BytesIO(self.flac.pictures[0].data))
            return self.cover
        return None

    def add_cover(self, path: Path) -> None:
        if path.suffix in [".jpg", ".jpeg", ".png"]:
            cover = Picture()
            with open(path, "rb") as file:
                cover.data = file.read()
            cover.mime = "image/png" if path.suffix == ".png" else "image/jpeg"
            self.remove_cover()
            self.flac.add_picture(cover)
            self.flac.save()
        else:
            raise WrongPictureFormatError(
                "Supported extensions are 'jpg', 'jpeg', 'png'."
            )

    def resize_cover(self, width: int, extension: str = None) -> None:
        if extension not in {None, "jpg", "jpeg", "png"}:
            raise WrongPictureFormatError(
                "Supported extensions are 'jpg', 'jpeg', 'png' or None."
            )

        image = self.read_cover()
        if not image:
            raise NoCoverFoundError("No cover found to resize")

        exif = image.getexif()
        exif[305] = "Chemz v. 0.1.0"
        exif[315] = "Blinzy a.k.a L4zzur"

        if extension:
            suffix = extension.lower().replace("e", "")
            image_format = "PNG" if suffix == "png" else "JPEG"
        else:
            suffix = "png" if image.format == "PNG" else "jpg"
            image_format = image.format

        aspect_ratio = image.width / image.height
        height = int(width / aspect_ratio)

        image.thumbnail((width, height), Image.Resampling.LANCZOS)

        temp_path = self.path.parent / f"temp_cover.{suffix}"
        image.save(temp_path, format=image_format, quality=100, exif=exif)

        self.add_cover(temp_path)
        temp_path.unlink()

    def export_cover(self, path: Path = None) -> Path:
        if not self.flac.pictures:
            return None
        suffix = "png" if self.flac.pictures[0].mime == "image/png" else "jpg"
        print(self.path.parent)
        if path is None:
            path = Path(f"{self.path.parent}/cover.{suffix}")

        with open(path, "wb") as file:
            file.write(self.flac.pictures[0].data)

        return path

    def remove_cover(self) -> None:
        self.flac.clear_pictures()
        self.flac.save()

    def __setattr__(self, name, value):
        if name in self.__slots__ or name in self.attrs:
            super().__setattr__(name, value)
        else:
            raise AttributeError(f"Cannot set unknown attribute '{name}'")

    def __getattr__(self, name):
        if name.startswith("set_"):
            attr_name = name[4:]
            flac_key = self.attrs.get(attr_name)
            if flac_key:

                @wraps(self.flac.__setitem__)
                def setter(value):
                    """Sets the FLAC tag for the attribute."""
                    self.flac[flac_key] = value

                return setter
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __setitem__(self, key, value):
        if key in self.attrs:
            self.flac[self.attrs[key]] = value
        else:
            raise KeyError(f"'{key}' is not a valid attribute key")

    def __getitem__(self, key):
        if key in self.attrs:
            return self.flac.get(self.attrs[key], [""])[0]
        else:
            raise KeyError(f"'{key}' is not a valid attribute key")
