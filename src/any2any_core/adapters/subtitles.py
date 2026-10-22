"""Subtitles adapter: SRT ↔ VTT (in-house minimal codecs, ~no external deps)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ..errors import ParseError
from ..models import PairSpec, Requirement
from ..registry import AdapterMeta, Registry

FORMATS = ("srt", "vtt")

_TIME_SRT = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")
_TIME_VTT = re.compile(r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})")


@dataclass
class Cue:
    start: str  # normalized HH:MM:SS.mmm
    end: str
    text: str


class StepContext:
    def __init__(self, input_path, output_path, options, temp_dir, token=None, progress=None):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.options = options
        self.temp_dir = temp_dir
        self.token = token
        self.progress = progress

    def cancelled(self) -> bool:
        return bool(self.token is not None and getattr(self.token, "is_set", lambda: False)())


def _norm_time(h: str, m: str, s: str, ms: str) -> str:
    return f"{h}:{m}:{s}.{ms}"


def parse_srt(text: str) -> list[Cue]:
    cues: list[Cue] = []
    blocks = re.split(r"\n\s*\n", text.strip(), flags=re.MULTILINE)
    for bi, block in enumerate(blocks, 1):
        lines = [ln for ln in block.splitlines() if ln.strip() != "" or True]
        lines = block.splitlines()
        # drop index line if present
        idx = 0
        if idx < len(lines) and lines[idx].strip().isdigit():
            idx += 1
        if idx >= len(lines):
            continue
        m = re.match(
            r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
            lines[idx].strip(),
        )
        if not m:
            raise ParseError(f"bad SRT cue near block {bi}")
        g = m.groups()
        start = _norm_time(*g[0:4])
        end = _norm_time(*g[4:8])
        body = "\n".join(lines[idx + 1 :]).strip()
        if not body:
            raise ParseError(f"empty cue text at block {bi}")
        cues.append(Cue(start, end, body))
    if not cues:
        raise ParseError("no cues found")
    return cues


def parse_vtt(text: str) -> list[Cue]:
    if not text.lstrip("﻿").startswith("WEBVTT"):
        raise ParseError("missing WEBVTT header")
    body = re.sub(r"^WEBVTT.*\n", "", text.lstrip("﻿"), count=1)
    cues: list[Cue] = []
    blocks = re.split(r"\n\s*\n", body.strip())
    for bi, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if not lines:
            continue
        idx = 0
        if "-->" not in lines[idx] and idx + 1 < len(lines) and "-->" in lines[idx + 1]:
            idx += 1  # skip cue id
        if idx >= len(lines) or "-->" not in lines[idx]:
            # NOTE / STYLE blocks
            continue
        m = re.match(
            r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})",
            lines[idx].strip(),
        )
        if not m:
            raise ParseError(f"bad VTT cue near block {bi}")
        g = m.groups()
        start = _norm_time(*g[0:4])
        end = _norm_time(*g[4:8])
        body_txt = "\n".join(lines[idx + 1 :]).strip()
        if not body_txt:
            raise ParseError(f"empty cue text at block {bi}")
        cues.append(Cue(start, end, body_txt))
    if not cues:
        raise ParseError("no cues found")
    return cues


def write_srt(cues: list[Cue]) -> str:
    parts = []
    for i, c in enumerate(cues, 1):
        s = c.start.replace(".", ",")
        e = c.end.replace(".", ",")
        parts.append(f"{i}\n{s} --> {e}\n{c.text}\n")
    return "\n".join(parts)


def write_vtt(cues: list[Cue]) -> str:
    parts = ["WEBVTT\n"]
    for c in cues:
        parts.append(f"{c.start} --> {c.end}\n{c.text}\n")
    return "\n".join(parts)


def execute(ctx: StepContext) -> None:
    src = ctx.input_path.suffix.lower().lstrip(".")
    tgt = ctx.output_path.suffix.lower().lstrip(".")
    text = ctx.input_path.read_text(encoding="utf-8-sig")
    cues = parse_srt(text) if src == "srt" else parse_vtt(text)
    out = write_srt(cues) if tgt == "srt" else write_vtt(cues)
    ctx.output_path.write_text(out, encoding="utf-8")


def register(reg: Registry) -> None:
    reg.register_adapter(
        AdapterMeta(
            id="subtitles",
            sources=FORMATS,
            targets=FORMATS,
            pairs={
                ("srt", "vtt"): PairSpec(source="srt", target="vtt", fidelity=0.95, test_fixture="tests/fixtures/sub/a.srt"),
                ("vtt", "srt"): PairSpec(source="vtt", target="srt", fidelity=0.95, test_fixture="tests/fixtures/sub/a.vtt"),
            },
            requires=(Requirement(kind="python", name="python", license="PSF-2.0"),),
            options=(),
            execute=execute,
        )
    )
