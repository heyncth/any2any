"""Settings store: single JSON file in user config dir (ADR-004)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from platformdirs import user_config_path

from .errors import UsageError

DEFAULTS: dict[str, Any] = {
    "default.conflict": "skip",
    "default.out_dir": "",  # empty = beside source
    "history.enabled": True,
    "history.limit": 10000,
    "offline": True,
}


def config_path() -> Path:
    return user_config_path("any2any", appauthor=False) / "settings.json"


def load_settings(path: Path | None = None) -> dict[str, Any]:
    p = path or config_path()
    data = dict(DEFAULTS)
    if p.is_file():
        try:
            loaded = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update({k: v for k, v in loaded.items() if k in DEFAULTS})
        except (OSError, json.JSONDecodeError):
            pass
    return data


def save_settings(data: dict[str, Any], path: Path | None = None) -> Path:
    p = path or config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    filtered = {k: data.get(k, DEFAULTS[k]) for k in DEFAULTS}
    p.write_text(json.dumps(filtered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def get_setting(key: str, settings: dict | None = None) -> Any:
    data = settings or load_settings()
    if key not in DEFAULTS:
        raise UsageError(f"unknown setting: {key}", hint=f"known: {', '.join(sorted(DEFAULTS))}")
    return data.get(key, DEFAULTS[key])


def set_setting(key: str, value: str, path: Path | None = None) -> Any:
    if key not in DEFAULTS:
        raise UsageError(f"unknown setting: {key}", hint=f"known: {', '.join(sorted(DEFAULTS))}")
    default = DEFAULTS[key]
    coerced: Any = value
    if isinstance(default, bool) or default is True or default is False:
        coerced = value.lower() in ("1", "true", "yes", "on")
    elif isinstance(default, int):
        try:
            coerced = int(value)
        except ValueError as e:
            raise UsageError(f"setting {key}: {e}") from e
    data = load_settings(path)
    data[key] = coerced
    save_settings(data, path)
    return coerced
