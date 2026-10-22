"""Safety guards: path traversal, disk-space precheck, subprocess hardening helpers."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .errors import DiskFull, PermissionDenied, UsageError


def safe_child(parent: Path, child: Path) -> bool:
    """True if child resolves inside parent (no traversal)."""
    try:
        parent_r = parent.resolve()
        child_r = child.resolve()
        return parent_r == child_r or parent_r in child_r.parents
    except OSError:
        return False


def ensure_writable_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise PermissionDenied(str(path), cause=type(e).__name__) from e
    if not os.access(path, os.W_OK):
        raise PermissionDenied(str(path))


def check_disk_space(path: Path, needed_bytes: int) -> None:
    """Best-effort free-space precheck; skip if statvfs unavailable (Windows)."""
    if needed_bytes <= 0:
        return
    try:
        usage = shutil.disk_usage(path if path.exists() else path.parent)
    except OSError:
        return
    if usage.free < needed_bytes:
        raise DiskFull(f"need ~{needed_bytes} bytes free at {path}")


def validate_options(option_specs, options: dict) -> dict:
    """Validate/coerce user options against adapter OptionSpec schema."""
    from .errors import UsageError

    known = {s.key: s for s in option_specs}
    out: dict = {}
    for k, v in options.items():
        spec = known.get(k)
        if spec is None:
            raise UsageError(f"unknown option: {k}", hint=f"known: {', '.join(sorted(known)) or '(none)'}")
        try:
            if spec.type == "int":
                out[k] = int(v)
            elif spec.type == "float":
                out[k] = float(v)
            elif spec.type == "bool":
                out[k] = str(v).lower() in ("1", "true", "yes", "on")
            elif spec.type == "choice":
                if str(v) not in (spec.choices or ()):
                    raise UsageError(f"option {k}: invalid choice {v!r}", hint=f"choices: {', '.join(spec.choices or ())}")
                out[k] = str(v)
            else:
                out[k] = str(v)
        except ValueError as e:
            raise UsageError(f"option {k}: {e}") from e
    for k, spec in known.items():
        if k not in out and spec.default is not None:
            out[k] = spec.default
    return out
