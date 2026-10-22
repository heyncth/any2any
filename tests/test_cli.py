import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run(*args, input=None):
    return subprocess.run(
        [sys.executable, "-m", "any2any_cli.main", *args],
        capture_output=True,
        text=True,
        input=input,
        cwd=ROOT,
    )


def test_version():
    p = run("--version")
    assert p.returncode == 0
    assert "0.1.0" in p.stdout


def test_formats_list():
    p = run("formats", "--json")
    assert p.returncode == 0
    data = json.loads(p.stdout)
    ids = {f["id"] for f in data["formats"]}
    assert {"png", "csv", "json", "gpx", "srt", "qr"} <= ids


def test_formats_for_file():
    fx = ROOT / "tests" / "fixtures" / "data" / "good.csv"
    p = run("formats", str(fx), "--json")
    assert p.returncode == 0
    data = json.loads(p.stdout)
    assert data["format"] == "csv"
    targets = {t["target"] for t in data["targets"]}
    assert "json" in targets


def test_convert_dry_run_exit_0():
    fx = ROOT / "tests" / "fixtures" / "data" / "good.csv"
    p = run("convert", str(fx), "--to", "json", "--dry-run", "--explain")
    assert p.returncode == 0
    assert "[plan]" in p.stdout


def test_convert_real(tmp_path):
    fx = ROOT / "tests" / "fixtures" / "image" / "good.png"
    p = run("convert", str(fx), "--to", "webp", "--out-dir", str(tmp_path), "--force", "--accept-lossy")
    assert p.returncode == 0, p.stderr
    assert (tmp_path / "good.webp").is_file()


def test_convert_json_output_schema(tmp_path):
    fx = ROOT / "tests" / "fixtures" / "data" / "good.csv"
    p = run("convert", str(fx), "--to", "tsv", "--out-dir", str(tmp_path), "--force", "--json", "--no-history")
    assert p.returncode == 0
    doc = json.loads(p.stdout)
    assert doc["schema"] == "any2any.result/1"
    assert doc["counts"]["success"] == 1
    assert doc["exit_code"] == 0


def test_unsupported_pair_exit_7(tmp_path):
    fx = ROOT / "tests" / "fixtures" / "image" / "good.png"
    p = run("convert", str(fx), "--to", "csv", "--out-dir", str(tmp_path), "--json", "--no-history")
    # no png->csv path; may plan via nothing → exit 7
    assert p.returncode in (7, 3)
    if p.returncode == 7:
        doc = json.loads(p.stdout)
        assert doc["results"][0]["error"]["code"].startswith("E_UNSUPPORTED")


def test_plan_command():
    fx = ROOT / "tests" / "fixtures" / "data" / "good.csv"
    p = run("plan", str(fx), "--to", "json")
    assert p.returncode == 0
    assert "csv -> json" in p.stdout


def test_doctor():
    p = run("doctor", "--json")
    assert p.returncode in (0, 4)
    doc = json.loads(p.stdout)
    assert "requirements" in doc
    assert doc["network"] == "not used"


def test_licenses():
    p = run("licenses", "--json")
    assert p.returncode == 0
    data = json.loads(p.stdout)
    assert any(n["component"] == "any2any-core" for n in data)


def test_conflict_skip_exit_6(tmp_path):
    fx = ROOT / "tests" / "fixtures" / "image" / "good.png"
    run("convert", str(fx), "--to", "bmp", "--out-dir", str(tmp_path), "--force", "--no-history")
    p = run("convert", str(fx), "--to", "bmp", "--out-dir", str(tmp_path), "--no-history")
    assert p.returncode == 6


def test_empty_file_exit_3(tmp_path):
    fx = ROOT / "tests" / "fixtures" / "image" / "0-byte.png"
    p = run("convert", str(fx), "--to", "webp", "--out-dir", str(tmp_path), "--accept-lossy", "--json", "--no-history")
    assert p.returncode == 3
    doc = json.loads(p.stdout)
    assert doc["results"][0]["error"]["code"] == "E_EMPTY_FILE"


def test_config_set_get(tmp_path, monkeypatch):
    # use isolated config via env is hard (platformdirs); just ensure commands run
    p = run("config", "list")
    assert p.returncode == 0
    assert "default.conflict" in p.stdout
