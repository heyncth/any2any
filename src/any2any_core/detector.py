"""Content detection: extension fast path, magic-byte confirm (ADR-008)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import EmptyFile, ExtensionMismatch, UnsupportedInput
from .registry import Registry

MAGICS: list[tuple[str, bytes, int]] = [
    ("png", b"\x89PNG\r\n\x1a\n", 0),
    ("jpeg", b"\xff\xd8\xff", 0),
    ("gif", b"GIF8", 0),
    ("bmp", b"BM", 0),
    ("pdf", b"%PDF", 0),
    ("ico", b"\x00\x00\x01\x00", 0),
    ("tiff_le", b"II*\x00", 0),
    ("tiff_be", b"MM\x00*", 0),
    ("zip", b"PK\x03\x04", 0),
]


@dataclass
class Detection:
    format_id: str
    trusted: str  # "extension" | "content" | "both"
    mismatch: bool = False


def detect_file(path: Path, reg: Registry, *, trust: str | None = None) -> Detection:
    """Return format id for path. Raises EmptyFile / UnsupportedInput / ExtensionMismatch."""
    if not path.is_file():
        raise UnsupportedInput(f"not a file: {path}")
    size = path.stat().st_size
    if size == 0:
        raise EmptyFile(str(path))

    ext = path.suffix.lower()
    ext_fmts = reg.formats_for_ext(ext)

    head = path.open("rb").read(16)
    magic_fmt = _magic_format(head)

    if ext_fmts:
        primary = ext_fmts[0]
        # magic confirm for binary formats that have a magic registered under same id
        if magic_fmt and magic_fmt != primary and magic_fmt in reg.formats:
            # content disagrees with extension
            if trust == "content":
                return Detection(magic_fmt, "content", mismatch=True)
            if trust == "extension":
                return Detection(primary, "extension", mismatch=True)
            raise ExtensionMismatch(
                f"{path.name}: extension {ext} but content looks like {magic_fmt}",
                hint="pass --trust content|extension",
            )
        if magic_fmt == primary or magic_fmt is None:
            return Detection(primary, "both" if magic_fmt else "extension")
        # unknown magic for this ext family — trust extension
        return Detection(primary, "extension")

    # no usable extension: fall back to content
    if magic_fmt and magic_fmt in reg.formats:
        return Detection(magic_fmt, "content")
    if magic_fmt is None and _looks_like_text(path):
        tid = _sniff_text(path, reg)
        if tid:
            return Detection(tid, "content")
    raise UnsupportedInput(
        f"cannot detect type of {path.name}",
        hint="rename with a known extension or use a supported format",
    )


def _magic_format(head: bytes) -> str | None:
    for name, magic, off in MAGICS:
        if head[off : off + len(magic)] == magic:
            if name in ("tiff_le", "tiff_be"):
                return "tiff"
            return name
    if len(head) >= 12 and head[0:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


def _looks_like_text(path: Path) -> bool:
    chunk = path.open("rb").read(8192)
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
        return True
    except UnicodeDecodeError:
        try:
            chunk.decode("utf-8-sig")
            return True
        except UnicodeDecodeError:
            return False


def _sniff_text(path: Path, reg: Registry) -> str | None:
    """Best-effort text content sniffing for structured formats without magic."""
    try:
        text = path.open("r", encoding="utf-8-sig", errors="strict").read(65536)
    except (UnicodeDecodeError, OSError):
        return None
    stripped = text.lstrip()
    if not stripped:
        return None
    if stripped.startswith("{") or stripped.startswith("["):
        import json

        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
            return "geojson" if _looks_geojson(text) else "json"
        except Exception:
            return "json"  # extension-less invalid json still detected as json for E_PARSE
    if stripped.startswith("---") or stripped.rstrip().endswith(("|", ":", "value")):
        try:
            import yaml

            yaml.safe_load(text)
            return "yaml"
        except Exception:
            pass
    if stripped.startswith("<?xml") or stripped.startswith("<gpx") or stripped.startswith("<kml"):
        if "<gpx" in text:
            return "gpx"
        if "<kml" in text:
            return "kml"
        return "xml"
    if stripped.startswith("WEBVTT"):
        return "vtt"
    # SRT: "1\n00:00:"
    lines = stripped.splitlines()
    if len(lines) >= 2 and lines[0].strip().isdigit() and "-->" in (lines[1] if len(lines) > 1 else ""):
        return "srt"
    # CSV heuristic
    first = lines[0] if lines else ""
    if "," in first and "\t" not in first:
        return "csv"
    if "\t" in first:
        return "tsv"
    if "html" in stripped[:200].lower() or stripped.startswith("<!DOCTYPE html") or stripped.startswith("<html"):
        return "html"
    return "txt"
