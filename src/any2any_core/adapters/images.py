"""Image adapter — Pillow. Pairs: png/jpeg/webp/tiff/bmp/ico (docs/02)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..errors import EngineFailed, ParseError, TimeoutError_, Warning_, W_LOSSY
from ..models import OptionSpec, PairSpec, Requirement
from ..registry import AdapterMeta, Registry

FORMATS = ("png", "jpeg", "webp", "tiff", "bmp", "ico")
# (src, tgt) -> fidelity
_F = 0.90
_F_LOSSY = 0.85


@dataclass
class StepContext:
    input_path: Path
    output_path: Path
    options: dict[str, Any]
    temp_dir: Path
    token: Any = None  # threading.Event
    progress: Any = None

    def cancelled(self) -> bool:
        return bool(self.token is not None and getattr(self.token, "is_set", lambda: False)())


def _pairs() -> dict[tuple[str, str], PairSpec]:
    pairs = {}
    for s in FORMATS:
        for t in FORMATS:
            if s == t:
                continue
            lossy = t in ("jpeg", "webp")
            pairs[(s, t)] = PairSpec(
                source=s,
                target=t,
                fidelity=_F_LOSSY if lossy else _F,
                test_fixture=f"tests/fixtures/image/good.{s if s != 'jpeg' else 'jpg'}",
            )
    return pairs


def execute(ctx: StepContext) -> None:
    from PIL import Image

    if ctx.cancelled():
        raise TimeoutError_("cancelled")  # mapped to E_CANCELLED by engine via token check
    try:
        img = Image.open(ctx.input_path)
        img.load()
    except Exception as e:
        raise ParseError(f"{ctx.input_path.name}: {e}") from e

    if ctx.cancelled():
        from ..errors import Cancelled

        raise Cancelled(str(ctx.input_path))

    tgt = ctx.output_path.suffix.lstrip(".").lower()
    pil_format = {
        "png": "PNG",
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "webp": "WEBP",
        "tiff": "TIFF",
        "tif": "TIFF",
        "bmp": "BMP",
        "ico": "ICO",
    }.get(tgt, tgt.upper())

    kwargs: dict[str, Any] = {}
    quality = ctx.options.get("quality")
    if quality is not None and pil_format in ("JPEG", "WEBP"):
        kwargs["quality"] = int(quality)
        if pil_format == "WEBP":
            kwargs["lossless"] = bool(ctx.options.get("lossless", False))
    if pil_format == "PNG":
        kwargs["optimize"] = True

    # mode fixes for formats that require specific modes
    if pil_format == "JPEG" and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    if pil_format == "BMP" and img.mode == "P":
        img = img.convert("RGBA")

    try:
        save_kwargs = dict(kwargs)
        if pil_format in ("JPEG", "PNG", "WEBP", "ICO") and img.mode == "RGBA" and pil_format == "JPEG":
            save_kwargs.pop("quality", None)
        img.save(ctx.output_path, format=pil_format, **save_kwargs)
    except Exception as e:
        raise EngineFailed(f"pillow save failed: {e}") from e


def register(reg: Registry) -> None:
    meta = AdapterMeta(
        id="pillow_images",
        sources=FORMATS,
        targets=FORMATS,
        pairs=_pairs(),
        requires=(Requirement(kind="python", name="pillow", license="MIT-CMU"),),
        options=(
            OptionSpec("quality", "int", default=85, help="lossy quality 1-100"),
            OptionSpec("lossless", "bool", default=False, help="webp lossless"),
        ),
        max_concurrency=4,
        execute=execute,
    )
    reg.register_adapter(meta)
