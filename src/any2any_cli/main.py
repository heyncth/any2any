"""Any2Any CLI — presentation only; all logic in any2any_core.Service."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from any2any_core import __version__
from any2any_core.errors import Any2AnyError
from any2any_core.models import Result
from any2any_core.service import ConvertOptions, Service

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_PARTIAL = 2
EXIT_FAIL = 3
EXIT_MISSING_ENGINE = 4
EXIT_CANCELLED = 5
EXIT_CONFLICT = 6
EXIT_UNSUPPORTED = 7


def _svc() -> Service:
    return Service()


def _exit_for(results: list[Result]) -> int:
    if not results:
        return EXIT_USAGE
    statuses = [r.status for r in results]
    codes = {r.error.code for r in results if r.error}
    if all(s == "cancelled" for s in statuses):
        return EXIT_CANCELLED
    if "E_MISSING_ENGINE" in codes and all(s != "success" for s in statuses):
        return EXIT_MISSING_ENGINE
    if "E_CONFLICT_OUTPUT" in codes and all(s != "success" for s in statuses):
        return EXIT_CONFLICT
    if codes & {"E_UNSUPPORTED_INPUT", "E_UNSUPPORTED_PAIR", "E_UNSUPPORTED_DIRECTION"} and all(
        s != "success" for s in statuses
    ):
        return EXIT_UNSUPPORTED
    if all(s == "success" for s in statuses):
        return EXIT_OK
    if any(s == "success" for s in statuses):
        return EXIT_PARTIAL
    return EXIT_FAIL


def _print_result_line(r: Result, quiet: bool = False) -> None:
    if r.status == "success":
        out = r.output or "(dry-run)"
        secs = r.duration_ms / 1000
        click.echo(f"[ok] {r.source.name} -> {Path(out).name if r.output else 'plan'} ({secs:.1f}s)")
        for w in r.warnings:
            click.echo(f"[warn] {w.code} {w.message}", err=True)
    elif r.status == "skipped":
        click.echo(f"[skip] {r.source.name}")
    elif r.status == "cancelled":
        click.echo(f"[cancelled] {r.source.name}", err=True)
    else:
        err = r.error
        code = err.code if err else "E_INTERNAL"
        detail = err.detail if err else ""
        click.echo(f"[fail] {code} {r.source.name}: {detail}", err=True)
        if err and err.hint and not quiet:
            click.echo(f"       hint: {err.hint}", err=True)


@click.group()
@click.version_option(__version__, prog_name="any2any")
@click.option("--debug", is_flag=True, help="verbose logging to stderr")
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """Any2Any — local-first file converter."""
    import logging

    logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING, stream=sys.stderr)


@cli.command()
@click.argument("inputs", nargs=-1, type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--to", "target", required=True, help="target format id")
@click.option("--out-dir", type=click.Path(path_type=Path), default=None)
@click.option("--force", is_flag=True, help="overwrite existing outputs")
@click.option("--on-conflict", type=click.Choice(["ask", "skip", "overwrite", "fail", "keep-both"]), default=None)
@click.option("--set", "set_opts", nargs=2, multiple=True, metavar="KEY VALUE", help="adapter option")
@click.option("--direct-only", is_flag=True, help="refuse multi-step chains")
@click.option("--explain", is_flag=True, help="print plan before running")
@click.option("--accept-lossy", is_flag=True, help="acknowledge lossy conversion")
@click.option("--trust", type=click.Choice(["content", "extension"]), default=None)
@click.option("--dry-run", is_flag=True, help="plan + validation only")
@click.option("--json", "json_out", is_flag=True, help="machine-readable results")
@click.option("--no-history", is_flag=True)
def convert(inputs, target, out_dir, force, on_conflict, set_opts, direct_only, explain, accept_lossy, trust, dry_run, json_out, no_history):
    """Convert INPUTS to TARGET format."""
    svc = _svc()
    conflict = "overwrite" if force else (on_conflict or "skip")
    set_options = {k: v for k, v in set_opts}
    opts = ConvertOptions(
        out_dir=out_dir,
        conflict=conflict,
        direct_only=direct_only,
        accept_lossy=accept_lossy,
        trust=trust,
        set_options=set_options,
        write_history=not no_history,
        dry_run=dry_run,
    )

    # resolve lossy ack interactively once per pair
    if not accept_lossy and sys.stdin.isatty() and not dry_run:
        first = True
        for p in inputs:
            loads = svc.load([p], trust=trust)
            if loads[0].error or not loads[0].format_id:
                continue
            try:
                pl = svc.plan(loads[0].format_id, target, direct_only=direct_only)
            except Any2AnyError:
                continue
            if pl.lossy and first:
                if click.confirm(f"{loads[0].format_id}->{target} is lossy. Continue?", default=False):
                    opts.accept_lossy = True
                first = False

    if explain or dry_run:
        for p in inputs:
            loads = svc.load([p], trust=trust)
            lr = loads[0]
            if lr.error:
                click.echo(f"[fail] {lr.error.code} {p.name}: {lr.error.detail}", err=True)
                continue
            try:
                pl = svc.plan(lr.format_id, target, direct_only=direct_only)
            except Any2AnyError as e:
                click.echo(f"[fail] {e.code} {p.name}: {e.detail}", err=True)
                if e.hint:
                    click.echo(f"       hint: {e.hint}", err=True)
                continue
            chain = " -> ".join([pl.source_format] + [s.target for s in pl.steps])
            click.echo(f"[plan] {p.name}: {chain} (est. {pl.score:.2f})")
            for w in pl.warnings:
                click.echo(f"[warn] {w.code} {w.message}", err=True)

    if dry_run:
        if json_out:
            click.echo(json.dumps({"schema": "any2any.result/1", "command": "convert", "dry_run": True, "results": [], "exit_code": 0}, ensure_ascii=False))
        sys.exit(EXIT_OK)

    results = svc.convert_many(list(inputs), target, opts)

    if json_out:
        doc = {
            "schema": "any2any.result/1",
            "command": "convert",
            "results": [r.to_dict() for r in results],
            "counts": {
                "success": sum(1 for r in results if r.status == "success"),
                "failed": sum(1 for r in results if r.status == "failed"),
                "skipped": sum(1 for r in results if r.status == "skipped"),
                "cancelled": sum(1 for r in results if r.status == "cancelled"),
            },
            "exit_code": _exit_for(results),
        }
        click.echo(json.dumps(doc, ensure_ascii=False, indent=2))
    else:
        for r in results:
            _print_result_line(r)
        ok = sum(1 for r in results if r.status == "success")
        fail = sum(1 for r in results if r.status == "failed")
        skip = sum(1 for r in results if r.status == "skipped")
        click.echo(f"done: {ok} ok, {fail} failed, {skip} skipped", err=True)

    sys.exit(_exit_for(results))


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--json", "json_out", is_flag=True)
def formats(file, json_out):
    """List formats, or targets for FILE."""
    svc = _svc()
    if file:
        data = svc.targets_for_file(file)
        if json_out:
            click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            click.echo(f"{data['source']}: {data['format']}")
            for t in data["targets"]:
                chain = " (chain)" if t["chain"] else ""
                blocked = " [missing engine]" if t["blocked"] else ""
                click.echo(f"  -> {t['target']:<12} steps={t['steps']} est={t['est']}{chain}{blocked}")
        return
    data = svc.formats()
    if json_out:
        click.echo(json.dumps({"schema": "any2any.formats/1", "formats": data}, ensure_ascii=False, indent=2))
    else:
        for f in data:
            rw = ("r" if f["read"] else "-") + ("w" if f["write"] else "-")
            lossy = " lossy" if f["lossy"] else ""
            click.echo(f"{rw} {f['id']:<12} {f['category']:<10} {','.join(f['extensions'])}{lossy}")


@cli.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--to", "target", required=True)
@click.option("--explain", is_flag=True, default=True)
@click.option("--direct-only", is_flag=True)
@click.option("--json", "json_out", is_flag=True)
def plan(input, target, explain, direct_only, json_out):
    """Show conversion plan for INPUT without writing."""
    svc = _svc()
    loads = svc.load([input])
    lr = loads[0]
    if lr.error:
        click.echo(f"[fail] {lr.error.code}: {lr.error.detail}", err=True)
        sys.exit(EXIT_UNSUPPORTED)
    try:
        pl = svc.plan(lr.format_id, target, direct_only=direct_only)
    except Any2AnyError as e:
        click.echo(f"[fail] {e.code}: {e.detail}", err=True)
        if e.hint:
            click.echo(f"hint: {e.hint}", err=True)
        sys.exit(EXIT_UNSUPPORTED)
    if json_out:
        click.echo(json.dumps(pl.to_dict(), ensure_ascii=False, indent=2))
    else:
        chain = " -> ".join([pl.source_format] + [s.target for s in pl.steps])
        click.echo(f"{chain} (est. {pl.score:.2f})")
        for s in pl.steps:
            click.echo(f"  step: {s.adapter_id} {s.source}->{s.target} fidelity={s.fidelity}")
        for w in pl.warnings:
            click.echo(f"[warn] {w.code} {w.message}", err=True)
    sys.exit(EXIT_OK)


@cli.command()
@click.option("--json", "json_out", is_flag=True)
def doctor(json_out):
    """Check requirements and registry health."""
    svc = _svc()
    d = svc.doctor()
    if json_out:
        click.echo(json.dumps(d, ensure_ascii=False, indent=2))
    else:
        click.echo(f"any2any {d['any2any_version']} / python {d['python']} / {d['platform']}")
        click.echo(f"registry: {d['registry']['formats']} formats, {d['registry']['adapters']} adapters, {d['registry']['pairs']} pairs")
        if d["registry"]["broken_adapters"]:
            for b in d["registry"]["broken_adapters"]:
                click.echo(f"[broken] {b['adapter']}: {b['error']}", err=True)
        for r in d["requirements"]:
            mark = "ok" if r["found"] else "MISSING"
            click.echo(f"  [{mark}] {r['kind']}:{r['name']}")
        click.echo(f"network: {d['network']}")
    sys.exit(int(d["exit_hint"]))


@cli.command()
@click.option("--json", "json_out", is_flag=True)
def licenses(json_out):
    """Print third-party license notices."""
    data = _svc().licenses()
    if json_out:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for n in data:
            click.echo(f"{n['component']:<16} {n['license']:<12} {n.get('kind', '')}")


@cli.command()
@click.option("--limit", default=20, show_default=True)
@click.option("--json", "json_out", is_flag=True)
@click.option("--clear", is_flag=True)
@click.option("--yes", is_flag=True)
def history(limit, json_out, clear, yes):
    """Show or clear conversion history."""
    from any2any_core.history import HistoryStore

    store = HistoryStore()
    if clear:
        if sys.stdin.isatty() and not yes:
            if not click.confirm("Clear all history?"):
                sys.exit(EXIT_USAGE)
        n = store.clear()
        click.echo(f"cleared {n} rows")
        return
    rows = store.list(limit)
    if json_out:
        click.echo(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            click.echo(f"{row['ts']}  {row['status']:<9} {Path(row['source']).name} -> {Path(row['output']).name if row['output'] else '-'}")
    store.close()


@cli.group()
def config():
    """Get/set settings."""


@config.command("list")
def config_list():
    from any2any_core.settings import load_settings

    for k, v in sorted(load_settings().items()):
        click.echo(f"{k} = {v}")


@config.command("get")
@click.argument("key")
def config_get(key):
    from any2any_core.settings import get_setting

    try:
        click.echo(get_setting(key))
    except Any2AnyError as e:
        click.echo(f"[fail] {e.code}: {e.detail}", err=True)
        sys.exit(EXIT_USAGE)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    from any2any_core.settings import set_setting

    try:
        v = set_setting(key, value)
        click.echo(f"{key} = {v}")
    except Any2AnyError as e:
        click.echo(f"[fail] {e.code}: {e.detail}", err=True)
        sys.exit(EXIT_USAGE)


@cli.group()
def engines():
    """List / install external engines (M4+)."""


@engines.command("list")
def engines_list():
    d = _svc().doctor()
    for r in d["requirements"]:
        if r["kind"] == "binary":
            mark = "ok" if r["found"] else "missing"
            click.echo(f"[{mark}] {r['name']}")


@engines.command("install")
@click.argument("name")
@click.option("--yes", is_flag=True)
def engines_install(name, yes):
    click.echo(f"engine installer not implemented yet (M4): {name}", err=True)
    sys.exit(EXIT_USAGE)


if __name__ == "__main__":
    cli()
