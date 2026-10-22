"""QR adapter: any text payload (txt) → qr (PNG via qrcode+Pillow)."""

from __future__ import annotations

from pathlib import Path

from ..errors import EngineFailed, ParseError
from ..models import OptionSpec, PairSpec, Requirement
from ..registry import AdapterMeta, Registry


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


def execute(ctx: StepContext) -> None:
    import qrcode

    try:
        payload = ctx.input_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise ParseError(f"{ctx.input_path.name}: not valid UTF-8 text") from e
    if not payload.strip():
        raise ParseError(f"{ctx.input_path.name}: empty payload")
    box = int(ctx.options.get("box_size", 8))
    border = int(ctx.options.get("border", 4))
    try:
        qr = qrcode.QRCode(box_size=box, border=border)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(ctx.output_path)
    except Exception as e:
        raise EngineFailed(f"qr encode failed: {e}") from e


def register(reg: Registry) -> None:
    reg.register_adapter(
        AdapterMeta(
            id="qr",
            sources=("txt",),
            targets=("qr",),
            pairs={("txt", "qr"): PairSpec("txt", "qr", fidelity=1.0, test_fixture="tests/fixtures/qr/url.txt")},
            requires=(
                Requirement(kind="python", name="qrcode", license="BSD-3"),
                Requirement(kind="python", name="pillow", license="MIT-CMU"),
            ),
            options=(
                OptionSpec("box_size", "int", default=8, help="px per module"),
                OptionSpec("border", "int", default=4, help="border modules"),
            ),
            execute=execute,
        )
    )
