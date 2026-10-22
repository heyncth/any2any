# Any2Any — Executive Summary

**Working name:** Any2Any  
**Type:** Independent, free, open-source, local-first file conversion application  
**Inspired by:** publicly observable capabilities of 2anything (https://2anything.app/)  
**Research date:** 2026-10-22  
**Status:** Specification only — no application code written.

---

## 1. Product overview

Any2Any is a local-first file conversion tool with a GUI and CLI. Files stay on the user's machine. No account, no subscription, no cloud backend, no mandatory AI API key. Conversions run offline once optional external engines are installed.

The product is designed as a modular conversion system: a format registry declares what can convert to what, a planner determines the route, and adapters execute each step. New formats are added by registering new adapters, without rewriting the application.

## 2. What 2anything demonstrably is (research subject)

| Attribute | Value | Label |
|---|---|---|
| Platform | macOS, Apple Silicon only | VERIFIED |
| Price | $39 one-time, 7-day trial | VERIFIED |
| Network use | License validation + update check only; both avoidable offline after activation | VERIFIED (privacy policy) |
| Telemetry | None | VERIFIED (privacy policy) |
| Architecture hint | Registry of >20 engines; scored multi-step route planning (fidelity scores, multiply, up to 3 fallback routes); intermediates in temp, deleted after | VERIFIED (EML-to-PDF blog) |
| CLI | `2anything file --to fmt`, `--set key value`, `--formats file`, `--licenses` | VERIFIED (blog + release notes) |
| GUI | Drop zone, output-format select, Advanced Settings, Convert button, conversion history | VERIFIED (homepage mockup + blog) |
| Output | Written next to source file, same basename, new extension | VERIFIED (multiple blog posts) |
| Copyleft strategy | No GPL/AGPL in-process; ffmpeg and pandoc ship as separate pinned binaries | VERIFIED (GitHub release 0.22.1 notes) |
| Internal source code | Not recovered; not claimed | — |

The original app was not executed during this research (Windows host, no Apple Silicon). All runtime behaviors are documented from official web sources. Behavioral test results are `NOT TESTED` and converted into proposed acceptance tests for Any2Any.

## 3. Research coverage

Inspected sources: homepage, /pricing/, /privacy/, /terms/, /refund-policy/, /blog/, 5 use-case pages (data-nerd, podcaster, paper-pusher, designer, explorer), 5 blog posts (audiobook, PDF-to-Word, EML-to-PDF, CSV-to-JSON, HEIC-to-JPG), GitHub release page for v0.22.1, plus license pages for candidate OSS dependencies (pandoc, whisper.cpp, pyreadstat, piper-tts). Full log: `docs/research/evidence-log.md`.

## 4. Main conclusions

1. The original product's core value is local-first conversion of a very wide format set through a scored conversion graph with transparent chaining.
2. The most reusable design patterns for Any2Any are: (a) registry of adapters with explicit directions, (b) multi-step planning with user-visible routes, (c) process isolation of heavy or copyleft external tools, (d) output next to source by default, (e) batch via glob in CLI and drag-drop in GUI.
3. A one-developer MVP is achievable by restricting scope to images, tabular data, text documents, subtitles, geo, and QR codes using permissively licensed libraries, deferring full PDF/DOCX fidelity, OCR, STT, TTS, and video to later milestones.
4. Any2Any can be strictly more private than the original: no license validation server, no update phone-home by default.

## 5. Biggest unknowns

1. Exact list of the original's >20 engines and their pairings (only partially disclosed).
2. Fidelity scoring function details (blog explains the concept; exact scores per edge are not published).
3. GUI advanced-settings panel contents (only a few setting names appear in release notes/blog: `pdf_engine`, `ocr_pages`, `block_remote_content`, `value_labels`, `sheet`, `voice`, `bitrate`, `chapter_minutes`).
4. Trial-mode UI restrictions (e.g., watermark, format lock) — not publicly documented in detail.
5. Whether the CLI supports non-macOS platforms (product is macOS-only; CLI is bundled inside the macOS app).

Open questions with impact: `docs/13-open-questions.md`.

## 6. Recommended approach for Any2Any

- **Core:** Python 3.12, package `any2any_core`.
- **GUI:** PySide6 (Qt 6, LGPL-3.0).
- **CLI:** Click, sharing the same core service layer.
- **External tools:** ffmpeg, pandoc, tesseract, resvg, (later) whisper.cpp and piper invoked as pinned, checksum-verified subprocesses; never linked in-process.
- **Core license:** MIT.
- **Privacy default:** zero network calls; optional update check and optional tool download, both explicit user actions.
- **MVP P0 formats:** PNG, JPEG, WebP, TIFF, BMP, ICO, SVG→raster; CSV, TSV, JSON, JSONL, YAML; TXT, Markdown, HTML; SRT, VTT; GPX, KML, GeoJSON; QR code generation.

## 7. Document map

| Document | Purpose |
|---|---|
| [01-product-requirements.md](01-product-requirements.md) | Personas, user stories, FR/NFR |
| [02-feature-inventory.md](02-feature-inventory.md) | Format matrix with evidence labels |
| [03-ui-ux-specification.md](03-ui-ux-specification.md) | Screen inventory and interaction states |
| [04-user-flows.md](04-user-flows.md) | Step-by-step flows and diagrams |
| [05-architecture.md](05-architecture.md) | System architecture and ADRs |
| [06-conversion-engine.md](06-conversion-engine.md) | Registry, planner, adapter contract |
| [07-cli-specification.md](07-cli-specification.md) | Proposed CLI commands |
| [08-data-storage-and-privacy.md](08-data-storage-and-privacy.md) | Storage, offline guarantees, privacy tests |
| [09-dependencies-and-licensing.md](09-dependencies-and-licensing.md) | Dependency and license audit |
| [10-test-plan.md](10-test-plan.md) | Test strategy and fixtures |
| [11-roadmap.md](11-roadmap.md) | Milestones M0–M6 |
| [12-competitive-analysis.md](12-competitive-analysis.md) | Alternatives and positioning |
| [13-open-questions.md](13-open-questions.md) | Unresolved questions |
| [14-acceptance-criteria.md](14-acceptance-criteria.md) | Testable release criteria |
| [research/evidence-log.md](research/evidence-log.md) | Source-by-source evidence |
| [research/test-results.md](research/test-results.md) | Executed vs. proposed tests |
