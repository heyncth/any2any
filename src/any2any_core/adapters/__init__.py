"""Builtin adapters: register formats + adapters on a Registry."""

from __future__ import annotations

from ..models import FormatDecl


def register_builtins(reg) -> None:
    from .documents import register as reg_docs
    from .geo import register as reg_geo
    from .images import register as reg_images
    from .qr import register as reg_qr
    from .subtitles import register as reg_subtitles
    from .tabular import register as reg_tabular

    _register_core_formats(reg)
    reg_images(reg)
    reg_tabular(reg)
    reg_docs(reg)
    reg_subtitles(reg)
    reg_geo(reg)
    reg_qr(reg)


def _register_core_formats(reg) -> None:
    """P0 format declarations (docs/02 matrix)."""
    image = "image"
    data = "data"
    document = "document"
    subtitle = "subtitle"
    geo = "geo"
    util = "util"

    decls = [
        # images
        FormatDecl("png", image, (".png",), "image/png", False, encoding="binary"),
        FormatDecl("jpeg", image, (".jpg", ".jpeg"), "image/jpeg", True, "lossy re-encode", "binary"),
        FormatDecl("webp", image, (".webp",), "image/webp", True, "lossy unless lossless flag", "binary"),
        FormatDecl("tiff", image, (".tiff", ".tif"), "image/tiff", False, encoding="binary"),
        FormatDecl("bmp", image, (".bmp",), "image/bmp", False, encoding="binary"),
        FormatDecl("ico", image, (".ico",), "image/x-icon", False, encoding="binary"),
        FormatDecl("svg", image, (".svg",), "image/svg+xml", False, encoding="text"),
        # tabular
        FormatDecl("csv", data, (".csv",), "text/csv", False, encoding="text"),
        FormatDecl("tsv", data, (".tsv",), "text/tab-separated-values", False, encoding="text"),
        FormatDecl("json", data, (".json",), "application/json", False, encoding="text"),
        FormatDecl("jsonl", data, (".jsonl", ".ndjson"), "application/jsonl", False, encoding="text"),
        FormatDecl("yaml", data, (".yaml", ".yml"), "application/yaml", False, encoding="text"),
        # documents
        FormatDecl("txt", document, (".txt",), "text/plain", False, encoding="text"),
        FormatDecl("md", document, (".md", ".markdown"), "text/markdown", False, encoding="text"),
        FormatDecl("html", document, (".html", ".htm"), "text/html", False, encoding="text"),
        # subtitles
        FormatDecl("srt", subtitle, (".srt",), "application/x-subrip", False, encoding="text"),
        FormatDecl("vtt", subtitle, (".vtt",), "text/vtt", False, encoding="text"),
        # geo
        FormatDecl("gpx", geo, (".gpx",), "application/gpx+xml", False, encoding="structured"),
        FormatDecl("kml", geo, (".kml",), "application/vnd.google-earth.kml+xml", False, encoding="structured"),
        FormatDecl("geojson", geo, (".geojson",), "application/geo+json", False, encoding="structured"),
        # util / QR output
        FormatDecl("qr", util, (".png",), "image/png", False, encoding="binary"),
    ]
    for d in decls:
        reg.register_format(d)
