"""Tabular adapter: CSV/TSV/JSON/JSONL/YAML (stdlib + PyYAML). Values stay text for CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ..errors import ParseError
from ..models import OptionSpec, PairSpec, Requirement
from ..registry import AdapterMeta, Registry

FORMATS = ("csv", "tsv", "json", "jsonl", "yaml")


class StepContext:
    def __init__(self, input_path: Path, output_path: Path, options: dict, temp_dir: Path, token=None, progress=None):
        self.input_path = input_path
        self.output_path = output_path
        self.options = options
        self.temp_dir = temp_dir
        self.token = token
        self.progress = progress

    def cancelled(self) -> bool:
        return bool(self.token is not None and getattr(self.token, "is_set", lambda: False)())


def _read_table(path: Path, options: dict) -> tuple[list[str], list[dict[str, str]]]:
    """CSV/TSV → header + rows (all values as strings, per CSV semantics)."""
    delimiter = options.get("delimiter")
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:65536]
    if delimiter:
        delim = {"tab": "\t", "semicolon": ";", "comma": ","}.get(delimiter, delimiter)
    else:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            delim = dialect.delimiter
        except csv.Error:
            delim = "\t" if sample.count("\t") > sample.count(",") else ","
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            if reader.fieldnames is None:
                raise ParseError(f"{path.name}: no header row")
            rows = []
            for row in reader:
                # None key = ragged extra values
                if None in row:
                    extras = row.pop(None)
                    if any(extras):
                        row["_extra"] = " ".join(x for x in extras if x)
                rows.append({(k or ""): (v if v is not None else "") for k, v in row.items()})
            return list(reader.fieldnames), rows
    except csv.Error as e:
        raise ParseError(f"{path.name}: {e}") from e


def _write_csv(rows: list[dict], path: Path, delimiter: str = ",") -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for r in rows:
        for k in r:
            if k not in fieldnames:
                fieldnames.append(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _as_rows(data: Any, path: Path) -> list[dict]:
    if isinstance(data, list):
        out = []
        for item in data:
            if isinstance(item, dict):
                out.append({str(k): "" if v is None else (json.dumps(v) if isinstance(v, (dict, list)) else str(v)) for k, v in item.items()})
            else:
                out.append({"value": json.dumps(item) if isinstance(item, (dict, list)) else str(item)})
        return out
    if isinstance(data, dict):
        return [{str(k): "" if v is None else (json.dumps(v) if isinstance(v, (dict, list)) else str(v)) for k, v in data.items()}]
    raise ParseError(f"{path.name}: expected list or object at top level")


def execute(ctx: StepContext) -> None:
    src, tgt = ctx.input_path.suffix.lower().lstrip("."), ctx.output_path.suffix.lower().lstrip(".").lstrip("j")
    # normalize: .yml -> yaml handled by format primary ext; detect from paths
    src = _fmt_of(ctx.input_path)
    tgt = _fmt_of(ctx.output_path)

    if src in ("csv", "tsv"):
        _, rows = _read_table(ctx.input_path, ctx.options)
        if tgt == "csv":
            _write_csv(rows, ctx.output_path, ",")
        elif tgt == "tsv":
            _write_csv(rows, ctx.output_path, "\t")
        elif tgt == "json":
            ctx.output_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        elif tgt == "jsonl":
            with ctx.output_path.open("w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        elif tgt == "yaml":
            import yaml

            ctx.output_path.write_text(yaml.safe_dump(rows, allow_unicode=True, sort_keys=False), encoding="utf-8")
        else:
            raise ParseError(f"unsupported target {tgt}")
    elif src == "json":
        try:
            data = json.loads(ctx.input_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as e:
            raise ParseError(f"{ctx.input_path.name}: line {e.lineno}: {e.msg}") from e
        rows = _as_rows(data, ctx.input_path)
        if tgt == "csv":
            _write_csv(rows, ctx.output_path, ",")
        elif tgt == "tsv":
            _write_csv(rows, ctx.output_path, "\t")
        elif tgt == "jsonl":
            with ctx.output_path.open("w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        elif tgt == "yaml":
            import yaml

            ctx.output_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        else:
            raise ParseError(f"unsupported target {tgt}")
    elif src == "jsonl":
        rows = []
        for i, line in enumerate(ctx.input_path.read_text(encoding="utf-8-sig").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ParseError(f"{ctx.input_path.name}: line {i}: {e.msg}") from e
            if not isinstance(obj, dict):
                obj = {"value": json.dumps(obj) if isinstance(obj, (list,)) else str(obj)}
            rows.append({str(k): "" if v is None else (json.dumps(v) if isinstance(v, (dict, list)) else str(v)) for k, v in obj.items()})
        if tgt == "csv":
            _write_csv(rows, ctx.output_path, ",")
        elif tgt == "tsv":
            _write_csv(rows, ctx.output_path, "\t")
        elif tgt == "json":
            ctx.output_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        elif tgt == "yaml":
            import yaml

            ctx.output_path.write_text(yaml.safe_dump(rows, allow_unicode=True, sort_keys=False), encoding="utf-8")
        else:
            raise ParseError(f"unsupported target {tgt}")
    elif src == "yaml":
        import yaml

        try:
            data = yaml.safe_load(ctx.input_path.read_text(encoding="utf-8-sig"))
        except yaml.YAMLError as e:
            raise ParseError(f"{ctx.input_path.name}: {e}") from e
        if data is None:
            data = []
        if tgt in ("csv", "tsv"):
            _write_csv(_as_rows(data, ctx.input_path), ctx.output_path, "\t" if tgt == "tsv" else ",")
        elif tgt == "json":
            ctx.output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        elif tgt == "jsonl":
            with ctx.output_path.open("w", encoding="utf-8") as f:
                if isinstance(data, list):
                    for item in data:
                        f.write(json.dumps(item, ensure_ascii=False) + "\n")
                else:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
        else:
            raise ParseError(f"unsupported target {tgt}")
    else:
        raise ParseError(f"unsupported source {src}")


def _fmt_of(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return {"yml": "yaml", "ndjson": "jsonl", "tif": "tiff", "jpeg": "jpeg", "htm": "html", "markdown": "md"}.get(ext, ext)


def _pairs() -> dict[tuple[str, str], PairSpec]:
    lossy_semantic = {("csv", "json"), ("tsv", "json"), ("csv", "yaml"), ("tsv", "yaml"), ("json", "csv"), ("json", "tsv"), ("jsonl", "csv"), ("jsonl", "tsv"), ("yaml", "csv"), ("yaml", "tsv")}
    pairs = {}
    for s in FORMATS:
        for t in FORMATS:
            if s == t:
                continue
            pairs[(s, t)] = PairSpec(source=s, target=t, fidelity=0.80 if (s, t) in lossy_semantic else 0.95, test_fixture=f"tests/fixtures/data/good.{s if s != 'yaml' else 'yaml'}")
    return pairs


def register(reg: Registry) -> None:
    reg.register_adapter(
        AdapterMeta(
            id="tabular",
            sources=FORMATS,
            targets=FORMATS,
            pairs=_pairs(),
            requires=(Requirement(kind="python", name="pyyaml", license="MIT"),),
            options=(OptionSpec("delimiter", "choice", choices=("comma", "semicolon", "tab"), help="input delimiter override"),),
            execute=execute,
        )
    )
