import hashlib
from pathlib import Path

import pytest

from any2any_core.adapters.images import StepContext
from any2any_core.errors import EmptyFile, ExtensionMismatch, ParseError, UnsupportedInput
from any2any_core.service import ConvertOptions, Service


@pytest.fixture
def svc():
    return Service(history=None)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_png_to_webp(svc, fixtures_dir, tmp_path):
    src = fixtures_dir / "image" / "good.png"
    before = _sha(src)
    opts = ConvertOptions(out_dir=tmp_path, conflict="overwrite", accept_lossy=True)
    r = svc.convert_path(src, "webp", opts)
    assert r.status == "success", r.error and r.error.detail
    assert r.output and r.output.is_file()
    assert r.output.suffix == ".webp"
    assert _sha(src) == before  # input unchanged
    assert any(w.code == "W_LOSSY" for w in r.warnings)


def test_csv_to_json_and_back(svc, fixtures_dir, tmp_path):
    src = fixtures_dir / "data" / "good.csv"
    opts = ConvertOptions(out_dir=tmp_path, conflict="overwrite", accept_lossy=True)
    r = svc.convert_path(src, "json", opts)
    assert r.status == "success", r.error and r.error.detail
    back = svc.convert_path(r.output, "csv", ConvertOptions(out_dir=tmp_path / "back", conflict="overwrite"))
    assert back.status == "success"


def test_bad_json_parse_error(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "data" / "bad.json", "csv", ConvertOptions(out_dir=tmp_path, conflict="overwrite", accept_lossy=True))
    assert r.status == "failed"
    assert r.error.code == "E_PARSE"
    assert "line" in r.error.detail


def test_empty_file(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "image" / "0-byte.png", "webp", ConvertOptions(out_dir=tmp_path, accept_lossy=True))
    assert r.status == "failed"
    assert r.error.code == "E_EMPTY_FILE"


def test_extension_mismatch(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(
        fixtures_dir / "image" / "extension-lie.png",
        "webp",
        ConvertOptions(out_dir=tmp_path, accept_lossy=True),
    )
    assert r.status == "failed"
    assert r.error.code == "E_EXTENSION_MISMATCH"


def test_extension_mismatch_trust_content(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(
        fixtures_dir / "image" / "extension-lie.png",
        "webp",
        ConvertOptions(out_dir=tmp_path, accept_lossy=True, trust="content"),
    )
    assert r.status == "success"
    assert any(w.code == "W_EXTENSION_MISMATCH_ACCEPTED" for w in r.warnings)


def test_corrupt_jpeg(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(
        fixtures_dir / "image" / "corrupt.jpg",
        "png",
        ConvertOptions(out_dir=tmp_path, accept_lossy=True),
    )
    assert r.status == "failed"
    assert r.error.code in ("E_PARSE", "E_ENGINE_FAILED")


def test_conflict_skip_then_keep_both(svc, fixtures_dir, tmp_path):
    src = fixtures_dir / "image" / "good.png"
    opts = ConvertOptions(out_dir=tmp_path, conflict="overwrite")
    r1 = svc.convert_path(src, "bmp", opts)
    assert r1.status == "success"
    r2 = svc.convert_path(src, "bmp", ConvertOptions(out_dir=tmp_path, conflict="skip"))
    assert r2.status == "failed"
    assert r2.error.code == "E_CONFLICT_OUTPUT"
    r3 = svc.convert_path(src, "bmp", ConvertOptions(out_dir=tmp_path, conflict="keep-both"))
    assert r3.status == "success"
    assert r3.output != r1.output


def test_lossy_requires_ack(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "image" / "good.png", "jpeg", ConvertOptions(out_dir=tmp_path, accept_lossy=False))
    assert r.status == "failed"
    assert r.error.code == "E_USAGE"


def test_dry_run_no_write(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "image" / "good.png", "webp", ConvertOptions(out_dir=tmp_path, accept_lossy=True, dry_run=True))
    assert r.status == "success"
    assert r.output is None
    assert list(tmp_path.iterdir()) == []


def test_unicode_filename(svc, fixtures_dir, tmp_path):
    import shutil

    src = tmp_path / "名前.png"
    shutil.copy(fixtures_dir / "image" / "good.png", src)
    r = svc.convert_path(src, "bmp", ConvertOptions(out_dir=tmp_path / "out", conflict="overwrite"))
    assert r.status == "success"
    assert r.output.name == "名前.bmp"


def test_srt_vtt_roundtrip(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "sub" / "a.srt", "vtt", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r.status == "success", r.error and r.error.detail
    text = r.output.read_text(encoding="utf-8")
    assert text.startswith("WEBVTT")
    r2 = svc.convert_path(r.output, "srt", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r2.status == "success"


def test_bad_srt(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "sub" / "bad.srt", "vtt", ConvertOptions(out_dir=tmp_path))
    assert r.status == "failed"
    assert r.error.code == "E_PARSE"


def test_geo_gpx_to_geojson(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "geo" / "track.gpx", "geojson", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r.status == "success", r.error and r.error.detail
    import json

    data = json.loads(r.output.read_text(encoding="utf-8"))
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2


def test_geo_kml_to_gpx(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "geo" / "route.kml", "gpx", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r.status == "success", r.error and r.error.detail
    assert "<gpx" in r.output.read_text(encoding="utf-8")


def test_malformed_gpx(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "geo" / "malformed.gpx", "geojson", ConvertOptions(out_dir=tmp_path))
    assert r.status == "failed"
    assert r.error.code == "E_PARSE"


def test_md_to_html(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "doc" / "note.md", "html", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r.status == "success"
    html = r.output.read_text(encoding="utf-8")
    assert "<h1>" in html or "<strong>" in html


def test_html_to_txt(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "doc" / "page.html", "txt", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r.status == "success"
    assert "Hi" in r.output.read_text(encoding="utf-8")


def test_qr_from_txt(svc, fixtures_dir, tmp_path):
    r = svc.convert_path(fixtures_dir / "qr" / "url.txt", "qr", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r.status == "success", r.error and r.error.detail
    assert r.output.suffix == ".png"
    assert r.output.stat().st_size > 0


def test_history_append(svc, fixtures_dir, tmp_path):
    from any2any_core.history import HistoryStore

    db = tmp_path / "h.db"
    store = HistoryStore(db)
    svc.history = store
    svc.settings["history.enabled"] = True
    r = svc.convert_path(fixtures_dir / "image" / "good.bmp", "png", ConvertOptions(out_dir=tmp_path, conflict="overwrite", write_history=True))
    assert r.status == "success"
    rows = store.list(10)
    assert rows and rows[0]["status"] == "success"
    store.close()


def test_safety_temp_cleanup(svc, fixtures_dir, tmp_path):
    import tempfile
    from pathlib import Path

    r = svc.convert_path(fixtures_dir / "image" / "good.png", "bmp", ConvertOptions(out_dir=tmp_path, conflict="overwrite"))
    assert r.status == "success"
    root = Path(tempfile.gettempdir()) / "any2any"
    leftovers = list(root.glob("any2any-*")) if root.is_dir() else []
    assert leftovers == []
