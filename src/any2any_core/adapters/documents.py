"""Documents adapter: TXT / Markdown / HTML (markdown-it-py + stdlib html.parser)."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from ..errors import ParseError
from ..models import OptionSpec, PairSpec, Requirement
from ..registry import AdapterMeta, Registry

FORMATS = ("txt", "md", "html")


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


class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks: list[str] = []
        self._skip = 0
        self._block = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article"}

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag in self._block:
            self._chunks.append("\n")
        if tag == "br":
            self._chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if tag in self._block:
            self._chunks.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._chunks.append(data)

    def text(self) -> str:
        raw = "".join(self._chunks)
        lines = [ln.strip() for ln in raw.splitlines()]
        out: list[str] = []
        blank = False
        for ln in lines:
            if not ln:
                if not blank:
                    out.append("")
                blank = True
            else:
                out.append(ln)
                blank = False
        return "\n".join(out).strip() + "\n"


def _md_to_html(text: str, title: str = "document") -> str:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    body = md.render(text)
    return f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n<title>{title}</title>\n</head>\n<body>\n{body}\n</body>\n</html>\n"


def _md_to_txt(text: str) -> str:
    """Markdown → plain text via markdown-it render + HTML stripper."""
    from markdown_it import MarkdownIt

    html = MarkdownIt("commonmark").render(text)
    return _html_to_txt(html)


def _html_to_txt(html: str) -> str:
    p = _HTMLTextExtractor()
    p.feed(html)
    return p.text()


def _txt_to_md(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def _txt_to_html(text: str) -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    body = "\n".join(f"<p>{ln}</p>" if ln else "" for ln in escaped.splitlines())
    return f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n<title>document</title>\n</head>\n<body>\n{body}\n</body>\n</html>\n"


def _fmt_of(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return {"yml": "yaml", "htm": "html", "markdown": "md"}.get(ext, ext)


def execute(ctx: StepContext) -> None:
    src = _fmt_of(ctx.input_path)
    tgt = _fmt_of(ctx.output_path)
    try:
        text = ctx.input_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise ParseError(f"{ctx.input_path.name}: not valid UTF-8 text") from e

    if src == "md" and tgt == "html":
        ctx.output_path.write_text(_md_to_html(text, ctx.input_path.stem), encoding="utf-8")
    elif src == "md" and tgt == "txt":
        ctx.output_path.write_text(_md_to_txt(text), encoding="utf-8")
    elif src == "html" and tgt == "txt":
        ctx.output_path.write_text(_html_to_txt(text), encoding="utf-8")
    elif src == "html" and tgt == "md":
        ctx.output_path.write_text(_html_to_txt(text), encoding="utf-8")
    elif src == "txt" and tgt == "md":
        ctx.output_path.write_text(_txt_to_md(text), encoding="utf-8")
    elif src == "txt" and tgt == "html":
        ctx.output_path.write_text(_txt_to_html(text), encoding="utf-8")
    else:
        raise ParseError(f"unsupported pair {src}->{tgt}")


def _pairs() -> dict[tuple[str, str], PairSpec]:
    scores = {
        ("txt", "md"): 0.95, ("txt", "html"): 0.95,
        ("md", "txt"): 0.90, ("md", "html"): 0.95,
        ("html", "txt"): 0.90, ("html", "md"): 0.90,
    }
    return {
        (s, t): PairSpec(source=s, target=t, fidelity=scores[(s, t)], test_fixture=f"tests/fixtures/doc/good.{'md' if s == 'md' else s}")
        for (s, t) in scores
    }


def register(reg: Registry) -> None:
    reg.register_adapter(
        AdapterMeta(
            id="documents",
            sources=FORMATS,
            targets=FORMATS,
            pairs=_pairs(),
            requires=(Requirement(kind="python", name="markdown-it-py", license="MIT"),),
            options=(),
            execute=execute,
        )
    )
