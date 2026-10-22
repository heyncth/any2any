"""Shared data models (docs/06)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .errors import Error_, Warning_


@dataclass(frozen=True)
class FormatDecl:
    id: str
    category: str
    extensions: tuple[str, ...]
    mime: str | None
    lossy: bool
    loss_notes: str | None = None
    encoding: str = "binary"


@dataclass(frozen=True)
class OptionSpec:
    key: str
    type: Literal["str", "int", "float", "bool", "choice"]
    default: Any = None
    choices: tuple[str, ...] | None = None
    help: str = ""


@dataclass(frozen=True)
class Requirement:
    kind: Literal["binary", "python", "model", "datafile"]
    name: str
    version_pin: str | None = None
    sha256: str | None = None
    license: str | None = None
    download_url: str | None = None
    required_for: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PairSpec:
    source: str
    target: str
    direct: bool = True
    constraints_in: str | None = None
    constraints_out: str | None = None
    input_lossiness_notes: str | None = None
    test_fixture: str = ""
    fidelity: float = 0.9


@dataclass
class Step:
    adapter_id: str
    source: str
    target: str
    options: dict[str, Any] = field(default_factory=dict)
    fidelity: float = 0.9


@dataclass
class Plan:
    source_format: str
    target_format: str
    steps: list[Step]
    score: float
    lossy: bool
    requirements: list[Requirement] = field(default_factory=list)
    alternatives: list[Plan] = field(default_factory=list)
    warnings: list[Warning_] = field(default_factory=list)
    blocked: Error_ | None = None

    @property
    def chained(self) -> bool:
        return len(self.steps) > 1

    def to_dict(self) -> dict:
        return {
            "source_format": self.source_format,
            "target_format": self.target_format,
            "steps": [
                {"adapter_id": s.adapter_id, "source": s.source, "target": s.target, "fidelity": s.fidelity}
                for s in self.steps
            ],
            "score": round(self.score, 4),
            "lossy": self.lossy,
            "chained": self.chained,
            "blocked": self.blocked.to_dict() if self.blocked else None,
            "requirements": [
                {"kind": r.kind, "name": r.name, "version_pin": r.version_pin} for r in self.requirements
            ],
        }


@dataclass
class Result:
    item_id: str
    status: Literal["success", "failed", "skipped", "cancelled"]
    source: Path
    output: Path | None
    plan_used: Plan | None
    warnings: list[Warning_] = field(default_factory=list)
    error: Error_ | None = None
    duration_ms: int = 0
    bytes_in: int = 0
    bytes_out: int | None = None

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "status": self.status,
            "source": str(self.source),
            "output": str(self.output) if self.output else None,
            "plan": self.plan_used.to_dict() if self.plan_used else None,
            "warnings": [w.to_dict() for w in self.warnings],
            "error": self.error.to_dict() if self.error else None,
            "duration_ms": self.duration_ms,
            "bytes_in": self.bytes_in,
            "bytes_out": self.bytes_out,
        }


@dataclass
class Job:
    job_id: str
    created_at: datetime
    mode: Literal["single", "batch"] = "single"
    conflict_policy: str = "skip"
    out_dir: Path | None = None
    direct_only: bool = False
    accept_lossy: bool = False


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
