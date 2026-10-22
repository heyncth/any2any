"""Service facade: single API for GUI and CLI (docs/05 §1). No conversion logic in frontends."""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from . import __version__
from .detector import detect_file
from .errors import (
    Any2AnyError,
    Cancelled,
    ConflictOutput,
    Error_,
    InternalError,
    UnsupportedPair,
    Warning_,
    W_EXTENSION_MISMATCH_ACCEPTED,
    W_LOSSY,
)
from .filemanager import atomic_finalize, job_temp, resolve_output, sweep_stale_temps
from .history import HistoryStore
from .models import Plan, Result, utcnow
from .planner import plan as build_plan
from .registry import Registry, build_registry
from .safety import ensure_writable_dir, validate_options
from .settings import load_settings

log = logging.getLogger(__name__)

LICENSE_NOTICES = [
    {"component": "any2any-core", "version": __version__, "license": "MIT", "url": "https://github.com/", "kind": "self"},
    {"component": "pillow", "license": "MIT-CMU", "kind": "python"},
    {"component": "pyyaml", "license": "MIT", "kind": "python"},
    {"component": "gpxpy", "license": "Apache-2.0", "kind": "python"},
    {"component": "qrcode", "license": "BSD-3", "kind": "python"},
    {"component": "markdown-it-py", "license": "MIT", "kind": "python"},
    {"component": "click", "license": "BSD-3", "kind": "python"},
    {"component": "platformdirs", "license": "MIT", "kind": "python"},
]


@dataclass
class LoadResult:
    path: Path
    format_id: str
    mismatch: bool = False
    error: Error_ | None = None


@dataclass
class ConvertOptions:
    out_dir: Path | None = None
    conflict: str = "skip"
    direct_only: bool = False
    accept_lossy: bool = False
    trust: str | None = None
    set_options: dict[str, Any] = field(default_factory=dict)
    write_history: bool = True
    dry_run: bool = False


class Service:
    def __init__(self, reg: Registry | None = None, history: HistoryStore | None = None):
        self.reg = reg or build_registry()
        self.settings = load_settings()
        self.history = history
        self._cancel_tokens: dict[str, threading.Event] = {}

    def _hist(self) -> HistoryStore | None:
        if not self.settings.get("history.enabled", True):
            return None
        if self.history is None:
            self.history = HistoryStore()
        return self.history

    # -- formats / doctor / licenses ------------------------------------

    def formats(self) -> list[dict]:
        out = []
        for fid, f in sorted(self.reg.formats.items()):
            out.append(
                {
                    "id": fid,
                    "category": f.category,
                    "extensions": list(f.extensions),
                    "mime": f.mime,
                    "lossy": f.lossy,
                    "read": any(s == fid for (s, _) in self.reg.edges),
                    "write": any(t == fid for (_, t) in self.reg.edges),
                }
            )
        return out

    def targets_for_file(self, path: Path, trust: str | None = None) -> dict:
        det = detect_file(path, self.reg, trust=trust)
        targets = []
        for tgt in self.reg.targets_for(det.format_id):
            try:
                p = build_plan(self.reg, det.format_id, tgt)
                targets.append(
                    {
                        "target": tgt,
                        "steps": len(p.steps),
                        "est": round(p.score, 3),
                        "chain": p.chained,
                        "lossy": p.lossy,
                        "blocked": p.blocked.to_dict() if p.blocked else None,
                    }
                )
            except UnsupportedPair:
                continue
        return {"source": str(path), "format": det.format_id, "targets": targets}

    def doctor(self) -> dict:
        import importlib.util
        import platform
        import shutil
        import sys

        reqs = {}
        for meta in self.reg.adapters.values():
            for r in meta.requires:
                key = f"{r.kind}:{r.name}"
                if r.kind == "python":
                    from .planner import IMPORT_NAME

                    mod = IMPORT_NAME.get(r.name, r.name.replace("-", "_"))
                    found = mod == "python" or importlib.util.find_spec(mod) is not None
                elif r.kind == "binary":
                    found = shutil.which(r.name) is not None
                else:
                    found = True
                reqs[key] = {"kind": r.kind, "name": r.name, "found": found, "license": r.license}
        missing = [k for k, v in reqs.items() if not v["found"]]
        return {
            "any2any_version": __version__,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "registry": {
                "formats": len(self.reg.formats),
                "adapters": len(self.reg.adapters),
                "pairs": len(self.reg.edges),
                "broken_adapters": self.reg.broken,
            },
            "requirements": list(reqs.values()),
            "missing": missing,
            "config_path": str(self.settings and __import__("any2any_core.settings", fromlist=["config_path"]).config_path()),
            "network": "not used",
            "exit_hint": 0 if not missing else 4,
        }

    def licenses(self) -> list[dict]:
        return list(LICENSE_NOTICES)

    # -- load / plan ----------------------------------------------------

    def load(self, paths: list[Path], trust: str | None = None) -> list[LoadResult]:
        results = []
        for p in paths:
            try:
                det = detect_file(p, self.reg, trust=trust)
                results.append(LoadResult(path=p, format_id=det.format_id, mismatch=det.mismatch))
            except Any2AnyError as e:
                results.append(LoadResult(path=p, format_id="", error=Error_.from_exc(e)))
        return results

    def plan(self, src_fmt: str, tgt_fmt: str, *, direct_only: bool = False, options: dict | None = None) -> Plan:
        return build_plan(self.reg, src_fmt, tgt_fmt, direct_only=direct_only, options=options or {})

    # -- convert --------------------------------------------------------

    def convert_path(self, path: Path, tgt_fmt: str, opts: ConvertOptions, *, job_id: str | None = None) -> Result:
        t0 = time.monotonic()
        item_id = uuid.uuid4().hex[:12]
        job_id = job_id or item_id
        token = self._cancel_tokens.setdefault(job_id, threading.Event())
        bytes_in = path.stat().st_size if path.is_file() else 0

        def elapsed() -> int:
            return int((time.monotonic() - t0) * 1000)

        def finish(status, output=None, plan=None, warnings=None, error=None) -> Result:
            r = Result(
                item_id=item_id,
                status=status,
                source=path,
                output=output,
                plan_used=plan,
                warnings=warnings or [],
                error=error,
                duration_ms=elapsed(),
                bytes_in=bytes_in,
                bytes_out=output.stat().st_size if output and output.is_file() else None,
            )
            if opts.write_history:
                h = self._hist()
                if h:
                    try:
                        h.append(r)
                    except Exception:
                        log.debug("history append failed", exc_info=True)
            return r

        try:
            det = detect_file(path, self.reg, trust=opts.trust)
        except Any2AnyError as e:
            return finish("failed", error=Error_.from_exc(e))

        warnings: list[Warning_] = []
        if det.mismatch:
            warnings.append(Warning_(W_EXTENSION_MISMATCH_ACCEPTED, "content and extension disagree; trusted per --trust"))

        try:
            plan_ = build_plan(self.reg, det.format_id, tgt_fmt, direct_only=opts.direct_only)
        except Any2AnyError as e:
            return finish("failed", warnings=warnings, error=Error_.from_exc(e))

        if plan_.blocked:
            return finish("failed", warnings=warnings + plan_.warnings, error=plan_.blocked, plan=plan_)

        if plan_.lossy and not opts.accept_lossy:
            # caller (CLI) should have prompted; treat as warning + proceed only if accept_lossy
            return finish(
                "failed",
                warnings=warnings + plan_.warnings,
                error=Error_("E_USAGE", "Lossy conversion", "plan is lossy", hint="pass --accept-lossy"),
                plan=plan_,
            )

        warnings.extend(plan_.warnings)

        if opts.dry_run:
            return finish("success", output=None, plan=plan_, warnings=warnings)

        if token.is_set():
            return finish("cancelled", warnings=warnings, error=Error_.from_exc(Cancelled(str(path))), plan=plan_)

        try:
            out_ext = self.reg.primary_ext(tgt_fmt)
            if opts.out_dir is not None:
                ensure_writable_dir(opts.out_dir)
            out_path = resolve_output(path, out_ext, out_dir=opts.out_dir, conflict=opts.conflict)
        except Any2AnyError as e:
            return finish("failed", warnings=warnings, error=Error_.from_exc(e), plan=plan_)

        # validate options against first adapter's schema
        try:
            first_meta = self.reg.adapters[plan_.steps[0].adapter_id]
            validated = validate_options(first_meta.options, opts.set_options)
            for st in plan_.steps:
                st.options = dict(validated)
        except Any2AnyError as e:
            return finish("failed", warnings=warnings, error=Error_.from_exc(e), plan=plan_)

        try:
            from .adapters.images import StepContext as _AnyStepContext

            with job_temp(job_id) as tmp:
                current = path
                for i, step in enumerate(plan_.steps):
                    meta = self.reg.adapters[step.adapter_id]
                    if meta.execute is None:
                        raise InternalError(f"adapter {meta.id} has no execute")
                    nxt_ext = self.reg.primary_ext(step.target)
                    step_out = tmp / f"step{i}{nxt_ext}"
                    ctx = _AnyStepContext(
                        input_path=current,
                        output_path=step_out,
                        options=step.options,
                        temp_dir=tmp,
                        token=token,
                    )
                    if token.is_set():
                        raise Cancelled(str(path))
                    meta.execute(ctx)
                    if not step_out.is_file() or step_out.stat().st_size == 0:
                        from .errors import EngineFailed

                        raise EngineFailed(f"adapter {meta.id} produced no output for {step.source}->{step.target}")
                    current = step_out
                if token.is_set():
                    raise Cancelled(str(path))
                atomic_finalize(current, out_path)
            return finish("success", output=out_path, plan=plan_, warnings=warnings)
        except Any2AnyError as e:
            code = e.code
            status = "cancelled" if code == "E_CANCELLED" else "failed"
            return finish(status, warnings=warnings, error=Error_.from_exc(e), plan=plan_)
        except Exception as e:
            log.exception("internal error")
            return finish("failed", warnings=warnings, error=Error_.from_exc(e), plan=plan_)

    def convert_many(
        self,
        paths: list[Path],
        tgt_fmt: str,
        opts: ConvertOptions,
        on_result: Callable[[Result], None] | None = None,
    ) -> list[Result]:
        sweep_stale_temps()
        job_id = uuid.uuid4().hex[:12]
        self._cancel_tokens[job_id] = threading.Event()
        results: list[Result] = []
        try:
            for p in paths:
                r = self.convert_path(p, tgt_fmt, opts, job_id=job_id)
                results.append(r)
                if on_result:
                    on_result(r)
        finally:
            self._cancel_tokens.pop(job_id, None)
        return results

    def cancel(self, job_id: str) -> bool:
        tok = self._cancel_tokens.get(job_id)
        if tok:
            tok.set()
            return True
        return False
