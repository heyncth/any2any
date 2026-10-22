"""Conversion planner: direct edge + multi-step search, ≤3 alternatives (docs/06 §2)."""

from __future__ import annotations

from .errors import MissingEngine, UnsupportedPair, Warning_, W_CHAINED, W_LOSSY
from .models import Plan, Requirement, Step
from .registry import AdapterMeta, Registry

MAX_HOPS = 3
TOP_K = 3


def plan(
    reg: Registry,
    src: str,
    tgt: str,
    *,
    direct_only: bool = False,
    options: dict | None = None,
) -> Plan:
    if src not in reg.formats:
        raise UnsupportedPair(f"unknown source format: {src}")
    if tgt not in reg.formats:
        raise UnsupportedPair(f"unknown target format: {tgt}", hint=f"known: {', '.join(sorted(reg.formats)[:20])}")

    options = options or {}
    # Direct edge always wins (docs/06 §2.1 step 2)
    if not direct_only and reg.adapter_for(src, tgt) is not None:
        candidates = [([(src, tgt, reg.adapter_for(src, tgt))], reg.pair_specs[(src, tgt)].fidelity)]
    else:
        candidates = _enumerate_paths(reg, src, tgt, MAX_HOPS if not direct_only else 1)
    if not candidates:
        alts = reg.suggestions(src)
        raise UnsupportedPair(
            f"no path {src}->{tgt}",
            hint=f"targets from {src}: {', '.join(alts) if alts else '(none)'}",
        )

    candidates.sort(key=lambda c: (-c[1], len(c[0])))
    best = _to_plan(reg, candidates[0], options)
    alts = [_to_plan(reg, c, options) for c in candidates[1:TOP_K]]
    best.alternatives = alts
    return best


def _enumerate_paths(reg: Registry, src: str, tgt: str, max_hops: int) -> list[tuple[list[tuple[str, str, AdapterMeta]], float]]:
    """All simple paths src→tgt with ≤ max_hops edges; (edges, product-score)."""
    out: list[tuple[list[tuple[str, str, AdapterMeta]], float]] = []

    def dfs(node: str, visited: frozenset[str], path: list[tuple[str, str, AdapterMeta]], score: float) -> None:
        if len(path) >= max_hops:
            return
        for (s, t), meta in reg.edges.items():
            if s != node or t in visited:
                continue
            spec = reg.pair_specs[(s, t)]
            ns = score * spec.fidelity
            npath = path + [(s, t, meta)]
            if t == tgt:
                out.append((npath, ns))
            else:
                dfs(t, visited | {t}, npath, ns)

    dfs(src, frozenset({src}), [], 1.0)
    return out


def _to_plan(reg: Registry, candidate: tuple[list[tuple[str, str, AdapterMeta]], float], options: dict) -> Plan:
    edges, score = candidate
    steps: list[Step] = []
    reqs: list[Requirement] = []
    lossy = False
    warnings: list[Warning_] = []
    seen_req: set[str] = set()

    for src, tgt, meta in edges:
        spec = reg.pair_specs[(src, tgt)]
        steps.append(
            Step(adapter_id=meta.id, source=src, target=tgt, options=dict(options), fidelity=spec.fidelity)
        )
        if reg.formats[src].lossy or reg.formats[tgt].lossy:
            lossy = True
        for r in meta.requires:
            key = f"{r.kind}:{r.name}"
            if key not in seen_req:
                seen_req.add(key)
                reqs.append(r)

    if len(steps) > 1:
        warnings.append(Warning_(W_CHAINED, f"route: {' -> '.join([src] + [s.target for s in steps])} (est. {score:.2f})"))
    if lossy or any(reg.formats[s.target].lossy for s in steps):
        warnings.append(Warning_(W_LOSSY, _lossy_note(reg, steps)))

    blocked = None
    missing = _missing_requirements(reqs)
    if missing:
        from .errors import Error_

        blocked = Error_(
            code="E_MISSING_ENGINE",
            title="Missing requirement",
            detail=", ".join(missing),
            hint="run: any2any doctor",
        )

    return Plan(
        source_format=steps[0].source if steps else src,
        target_format=steps[-1].target if steps else tgt,
        steps=steps,
        score=score,
        lossy=lossy,
        requirements=reqs,
        warnings=warnings,
        blocked=blocked,
    )


def _lossy_note(reg: Registry, steps: list[Step]) -> str:
    notes = []
    for s in steps:
        f = reg.formats[s.target]
        if f.loss_notes:
            notes.append(f.loss_notes)
    return "; ".join(notes) if notes else "conversion is lossy"


# pip name → importable module name (only where they differ)
IMPORT_NAME = {
    "pillow": "PIL",
    "pyyaml": "yaml",
    "markdown-it-py": "markdown_it",
    "pillow-heif": "pillow_heif",
    "pyreadstat": "pyreadstat",
}


def _missing_requirements(reqs: list[Requirement]) -> list[str]:
    import importlib.util
    import shutil

    missing = []
    for r in reqs:
        if r.kind == "python":
            mod = IMPORT_NAME.get(r.name, r.name.replace("-", "_"))
            if mod == "python":  # stdlib placeholder
                continue
            try:
                if importlib.util.find_spec(mod) is None:
                    missing.append(r.name)
            except (ImportError, ValueError):
                missing.append(r.name)
        elif r.kind == "binary":
            if shutil.which(r.name) is None:
                missing.append(r.name)
    return missing


def check_requirements(plan_: Plan) -> None:
    """Raise MissingEngine if plan is blocked."""
    if plan_.blocked:
        raise MissingEngine(plan_.blocked.detail, hint=plan_.blocked.hint)
