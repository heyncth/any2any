# Any2Any

Local-first file conversion. Free, open source (MIT core). Inspired by the public capabilities of [2anything](https://2anything.app/) — not affiliated.

Files stay on your machine. No account, no cloud, no telemetry. Registry-driven conversion engine: adapters declare pairs, a planner finds the best route (≤3 steps, fidelity-scored), jobs run in temp dirs and finalize atomically.

## Status

M2 — core engine + P0 adapters (images, tabular, text docs, subtitles, geo, QR). No GUI yet.

## Install

```bash
pip install -e .[dev]
```

## Use

```bash
any2any convert photo.png --to webp
any2any convert data.csv --to json --explain
any2any formats
any2any formats mail.eml
any2any doctor
any2any licenses
any2any plan run.csv --to json --dry-run
```

Full specs: `docs/`.

## License

MIT (core). External engines, when added, stay process-isolated — see `docs/09-dependencies-and-licensing.md`.
