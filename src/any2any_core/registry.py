"""Format registry: formats + adapter bindings + validation (docs/06 §1)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from importlib.metadata import entry_points

from .errors import InternalError
from .models import FormatDecl, OptionSpec, PairSpec, Requirement

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class AdapterMeta:
    id: str
    sources: tuple[str, ...]
    targets: tuple[str, ...]
    pairs: dict[tuple[str, str], PairSpec]
    requires: tuple[Requirement, ...]
    options: tuple[OptionSpec, ...]
    max_concurrency: int = 4
    execute: object = None  # callable(StepContext) -> None; kept untyped to avoid cycle


@dataclass
class Registry:
    formats: dict[str, FormatDecl] = field(default_factory=dict)
    adapters: dict[str, AdapterMeta] = field(default_factory=dict)
    edges: dict[tuple[str, str], AdapterMeta] = field(default_factory=dict)
    pair_specs: dict[tuple[str, str], PairSpec] = field(default_factory=dict)
    broken: list[dict] = field(default_factory=list)
    ext_index: dict[str, list[str]] = field(default_factory=dict)

    def register_format(self, fmt: FormatDecl) -> None:
        if fmt.id in self.formats:
            raise InternalError(f"duplicate format id: {fmt.id}")
        self.formats[fmt.id] = fmt
        for ext in fmt.extensions:
            self.ext_index.setdefault(ext, []).append(fmt.id)

    def register_adapter(self, meta: AdapterMeta) -> None:
        """Register adapter; validate schema. Broken adapter disables only itself."""
        try:
            for fid in meta.sources + meta.targets:
                if fid not in self.formats:
                    raise InternalError(f"unknown format id '{fid}' in adapter {meta.id}")
            pairs = meta.pairs or {
                (s, t): PairSpec(source=s, target=t)
                for s in meta.sources
                for t in meta.targets
                if s != t
            }
            for key, spec in pairs.items():
                src, tgt = key
                if src not in meta.sources or tgt not in meta.targets:
                    raise InternalError(f"pair {src}->{tgt} outside sources/targets of {meta.id}")
                if not (0.0 < spec.fidelity <= 1.0):
                    raise InternalError(f"fidelity out of range for {src}->{tgt}")
                if key in self.edges:
                    raise InternalError(f"duplicate pair {src}->{tgt} (adapter {meta.id})")
                self.edges[key] = meta
                self.pair_specs[key] = spec
            for opt in meta.options:
                if opt.type == "choice" and not opt.choices:
                    raise InternalError(f"choice option {opt.key} has no choices")
            self.adapters[meta.id] = meta
        except Exception as e:
            self.broken.append({"adapter": meta.id, "error": str(e)})
            log.warning("adapter %s disabled: %s", meta.id, e)

    def load_entry_points(self) -> None:
        """Load external format packs via any2any.adapters entry points."""
        try:
            for ep in entry_points(group="any2any.adapters"):
                try:
                    register = ep.load()
                    register(self)
                except Exception as e:
                    self.broken.append({"adapter": ep.name, "error": str(e)})
                    log.warning("entry point %s failed: %s", ep.name, e)
        except Exception as e:
            log.debug("entry points unavailable: %s", e)

    def adapter_for(self, src: str, tgt: str) -> AdapterMeta | None:
        return self.edges.get((src, tgt))

    def targets_for(self, src: str) -> list[str]:
        return sorted(t for (s, t) in self.edges if s == src)

    def sources_for(self, tgt: str) -> list[str]:
        return sorted(s for (s, t) in self.edges if t == tgt)

    def formats_for_ext(self, ext: str) -> list[str]:
        return list(self.ext_index.get(ext.lower(), []))

    def primary_ext(self, fmt_id: str) -> str:
        return self.formats[fmt_id].extensions[0]

    def suggestions(self, src: str) -> list[str]:
        """Nearest targets for unsupported pair: same category first."""
        src_fmt = self.formats.get(src)
        direct = self.targets_for(src)
        if direct:
            return direct
        if not src_fmt:
            return []
        same_cat = [
            t
            for t, f in self.formats.items()
            if f.category == src_fmt.category and self.adapter_for(src, t)
        ]
        return sorted(same_cat)


def build_registry(load_plugins: bool = True) -> Registry:
    """Registry with builtin P0 formats + adapters registered."""
    from .adapters import register_builtins

    reg = Registry()
    register_builtins(reg)
    if load_plugins:
        reg.load_entry_points()
    return reg
