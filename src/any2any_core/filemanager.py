"""File & temp manager: per-job temp dirs, atomic finalize, stale sweep (ADR-007)."""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

from .errors import DiskFull, PermissionDenied


@contextmanager
def job_temp(job_id: str):
    root = Path(tempfile.gettempdir()) / "any2any" / f"any2any-{job_id}"
    root.mkdir(parents=True, exist_ok=True)
    try:
        _chmod_user_only(root)
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _chmod_user_only(path: Path) -> None:
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass


def resolve_output(
    source: Path,
    target_ext: str,
    *,
    out_dir: Path | None,
    conflict: str,
) -> Path:
    """Compute final output path under conflict policy. Never silently overwrite."""
    stem = source.stem
    parent = out_dir if out_dir is not None else source.parent
    base = parent / f"{stem}{target_ext}"
    if not base.exists():
        return base
    if conflict == "overwrite":
        return base
    if conflict == "skip":
        from .errors import ConflictOutput

        raise ConflictOutput(f"{base} exists", hint="use --force or --on-conflict keep-both")
    if conflict == "fail":
        from .errors import ConflictOutput

        raise ConflictOutput(f"{base} exists", hint="use --force or --on-conflict keep-both")
    if conflict == "keep-both":
        n = 1
        while True:
            cand = parent / f"{stem} ({n}){target_ext}"
            if not cand.exists():
                return cand
            n += 1
    if conflict == "ask":
        from .errors import ConflictOutput

        raise ConflictOutput(f"{base} exists", hint="resolve conflict (ask is GUI-only; CLI uses skip/force/keep-both)")
    from .errors import UsageError

    raise UsageError(f"unknown conflict policy: {conflict}")


def atomic_finalize(src_temp: Path, dest: Path) -> None:
    """Write as .part next to dest, then os.replace. Never leave partial finals."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.parent / f".{dest.name}.part"
    try:
        shutil.copyfile(src_temp, part)
        os.replace(part, dest)
    except OSError as e:
        try:
            part.unlink(missing_ok=True)
        except OSError:
            pass
        if getattr(e, "errno", None) == 28:  # ENOSPC
            raise DiskFull(str(dest)) from e
        if isinstance(e, PermissionError):
            raise PermissionDenied(str(dest)) from e
        raise


def sweep_stale_temps(max_age_hours: float = 24.0) -> int:
    """Remove orphaned any2any-* temp dirs older than max_age_hours. Returns count removed."""
    root = Path(tempfile.gettempdir()) / "any2any"
    if not root.is_dir():
        return 0
    cutoff = time.time() - max_age_hours * 3600
    removed = 0
    for child in root.glob("any2any-*"):
        try:
            if child.stat().st_mtime < cutoff:
                shutil.rmtree(child, ignore_errors=True)
                removed += 1
        except OSError:
            continue
    return removed
