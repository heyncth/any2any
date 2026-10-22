# Product Requirements — Any2Any

**Product:** Any2Any, a free, open-source, local-first file converter.  
**Evidence base:** publicly observable 2anything surface (see `research/evidence-log.md`), reinterpreted as independent requirements.  
**Date:** 2026-10-22

---

## 1. Personas

| Persona | Origin | Problem | Success looks like |
|---|---|---|---|
| P1 — The Data Nerd | Mirrors 2anything "Data Nerd" (VERIFIED marketing persona) | Data arrives as MATLAB/SPSS/Parquet/Excel; pipelines want something else; uploading research data may breach ethics approvals | One local tool converts tabular/scientific data without scripts |
| P2 — The Podcaster | Mirrors 2anything "Podcaster" | Needs captions/transcripts/audio format hops; tools demand subscriptions or upload unreleased audio | Transcribe and convert locally |
| P3 — The Paper Pusher | Mirrors 2anything "Paper Pusher" | Contracts, decks, manuscripts in wrong format; online converters see confidential text | Convert documents locally, PDF included |
| P4 — The Designer | Mirrors 2anything "Designer" | Icons, web formats, HEIC photos, vectorization across five web tools | Image/icon/font conversions in one place |
| P5 — The Explorer | Mirrors 2anything "Explorer" | Watch exports FIT; apps disagree on GPX/KML/GeoJSON; routes reveal home location | Local geo conversion |
| P6 — The Automator | Extended (INFERRED need: original markets CLI + batch) | Needs repeatable folder conversions in scripts/CI | Deterministic CLI, JSON output, exit codes |

## 2. User problems (core)

1. Converting a file usually means uploading it to an unknown server. Sensitive docs, research data, location tracks, and unreleased media should not travel.
2. Format X→Y pairs are scattered across dozens of single-purpose web tools with ads and limits.
3. Command-line users must remember different flags per tool (ffmpeg, pandoc, ImageMagick…).
4. Batch conversions become shell loops with poor error reporting and no cancellation.

## 3. Goals

- G1: Convert files locally, by GUI and CLI, with no account and no upload.
- G2: Transparent format support: user always sees whether a conversion is direct or chained, and what is lost.
- G3: Safe by default: no silent overwrite, no source modification, no leftover temp files, warnings on lossy steps.
- G4: Extensible: adding a format = registering an adapter; no core rewrite.
- G5: Automatable: CLI with stable exit codes and machine-readable output.
- G6: Honest privacy: zero network by default; any network action requires explicit user action and is disclosed.
- G7: Reproducible builds and complete third-party attribution (`--licenses`).

## 4. Non-goals

- Not a cloud converter, sync service, or account system.
- Not an exact clone: no 2anything branding, copy, assets, or proprietary code.
- Not a replacement for professional editors (Photoshop, Word, DaVinci): conversion, not authoring.
- Not guaranteed pixel-perfect PDF↔DOCX fidelity in MVP (later milestone, documented limits).
- Not "support every format ever made": the published matrix is the contract.
- No mandatory AI/API key: local models only, downloaded only with consent.
- No telemetry, ever (including crash reporting — default off; if ever added, opt-in).

## 5. User stories

### Epic A — Single conversion (GUI)
- A1: As a user, I drag a file onto the window and see which formats are available for *that* file.
- A2: I select an output format and see lossiness and option defaults before converting.
- A3: I press Convert and watch per-file progress with a working Cancel.
- A4: I get the output next to my file, same name, new extension — or a clear error.

### Epic B — Batch
- B1: I drop many files; each converts to the chosen format.
- B2: A batch with mixed valid/invalid files converts the valid ones and reports failures per file.
- B3: CLI equivalent: glob input, one command, summary at end.

### Epic C — Advanced options
- C1: I open Advanced Settings and set quality, metadata stripping, delimiter, sheet name, etc., only for formats where they apply.
- C2: Via CLI I use `--set key value` and can dump defaults with `--explain`.

### Epic D — Chained conversions
- D1: When no direct converter exists, I am shown the route ("via HTML") before or during conversion, with estimated fidelity.
- D2: I can opt out of chaining (`--direct-only`) and get a clear "unsupported" message.

### Epic E — History and settings
- E1: I can review past conversions (file, route, status, timestamp) and clear history.
- E2: I can set default output location, naming policy, and overwrite policy once.

### Epic F — Dependencies
- F1: When an optional engine (ffmpeg, pandoc…) is missing, the app tells me exactly what to install and offers to download a pinned build with my consent.
- F2: `any2any doctor` reports engine availability and versions.

### Epic G — Privacy and trust
- G1: I can use the app fully offline.
- G2: I can list every bundled component's license with one command.

## 6. Workflows (summary; detailed flows in `04-user-flows.md`)

W1 Single-file GUI conversion; W2 Batch GUI; W3 CLI single; W4 CLI batch; W5 Chain preview; W6 Missing dependency recovery; W7 Cancellation; W8 Existing output conflict; W9 History review; W10 Settings change.

## 7. Functional requirements

### FR-1: Core conversion
- FR-1.1: Registry declares formats with category, extensions, MIME, direction support (read/write/both), adapter binding, options, lossiness notes, required engines.
- FR-1.2: Planner resolves source→target: direct edge, or scored multi-step path (documented algorithm, `06-conversion-engine.md`).
- FR-1.3: Multi-step plans are user-visible (GUI badge/tooltip; CLI `--explain` output).
- FR-1.4: Direct-only mode available; unsupported pairs return a structured error listing closest alternatives.
- FR-1.5: Conversion result model identical for GUI and CLI: per-file status (success/skipped/failed/cancelled), output paths, warnings, errors with category, duration, plan used.

### FR-2: File handling
- FR-2.1: Source files are never modified or deleted.
- FR-2.2: Output written next to source by default; overridable (`--out-dir`, GUI setting).
- FR-2.3: Existing outputs trigger conflict policy: `ask` (GUI default), `skip`, `overwrite` (CLI default `skip`, `--force` to overwrite). No silent overwrite in GUI.
- FR-2.4: Content sniffing (magic bytes) supplements extension; mismatch → warning, user can proceed or cancel.
- FR-2.5: Empty files, unreadable files, unsupported extensions produce specific error codes.

### FR-3: Batch and jobs
- FR-3.1: Batch accepts lists/globs (CLI) and multi-drop (GUI).
- FR-3.2: Per-file progress events (started, step k of n, percent, done/failed).
- FR-3.3: Cancellation: cooperative token checked between steps and passed to subprocesses (terminate child processes); temp cleaned.
- FR-3.4: Parallelism configurable (default: min(4, cpu_count)) for batch; heavy media tools limited to 1–2 concurrent.

### FR-4: CLI
- FR-4.1: Commands per `07-cli-specification.md`; stable exit codes; `--json` machine output; `--quiet`/`--verbose`.
- FR-4.2: Every GUI capability needed for automation has a CLI path (quality, out-dir, force, direct-only, set options).

### FR-5: GUI
- FR-5.1: Screens and states per `03-ui-ux-specification.md`.
- FR-5.2: Drag-and-drop and file-picker input; format list filtered by selection.
- FR-5.3: Conversion history persisted; settings dialog.

### FR-6: Dependencies and engines
- FR-6.1: Core (zero external tools) must handle the entire P0 format set.
- FR-6.2: Optional engines detected at runtime; missing engine → error `E_MISSING_ENGINE` with install hint and optional download (explicit consent, pinned checksum).
- FR-6.3: Engine versions pinned in lockfile; `any2any licenses` lists all with license texts.

### FR-7: Privacy
- FR-7.1: Default build performs zero network I/O during conversion (enforceable by test).
- FR-7.2: No telemetry, no analytics, no account.
- FR-7.3: Update check (if shipped) default OFF; enabling is explicit; ping contains version only, documented.
- FR-7.4: Logs never contain file contents; paths redacted in shared bug reports only after user action.

### FR-8: Security
- FR-8.1: External tools invoked with argument arrays, never through a shell string.
- FR-8.2: Archive/extraction paths validated against traversal (zip-slip) and decompression limits (entry count, expanded bytes ratio).
- FR-8.3: Temp files in per-job directories with user-only permissions; removed on success, failure, cancel, and startup sweep (stale >24h).
- FR-8.4: Malformed structured data must fail with parse errors, not crashes (fuzz fixtures).

### FR-9: Transparency
- FR-9.1: Lossy conversions show a warning (dismissible per-format, remembered).
- FR-9.2: Data-shape changes (e.g., CSV→JSON keeps all values as strings; nested JSON→CSV cell serialization) documented in-product ("What changes" panel) and in `02-feature-inventory.md`.

## 8. Non-functional requirements

| ID | Requirement | Measure |
|---|---|---|
| NFR-1 | Offline operation | All P0 conversions pass with network blocked |
| NFR-2 | Privacy | Network monitor test: 0 connections during conversion session |
| NFR-3 | Performance | PNG→WebP 4K image < 1s; CSV(50MB)→JSON < 10s on reference laptop (M5 baseline) |
| NFR-4 | Reliability | Cancellation leaves 0 temp files; crash leaves only swept temp dirs |
| NFR-5 | Portability | Windows 10/11, macOS 13+, Ubuntu 22.04+ for P0 (defer rather than compromise architecture) |
| NFR-6 | Accessibility | Full keyboard operation; ARIA/accessible names on all controls; contrast ≥ 4.5:1 |
| NFR-7 | Determinism | Same input + same options → same output bytes for lossless conversions (timestamp-bearing formats excluded, documented) |
| NFR-8 | Startup | CLI `--help` < 500ms; GUI cold start < 2.5s |
| NFR-9 | Reproducibility | Pinned dependencies; lockfile; build instructions yield matching hashes where the toolchain allows |
| NFR-10 | Localization | English first; UI strings externalized from day one |

## 9. Compliance notes

- All dependencies documented in `09-dependencies-and-licensing.md`; copyleft tools process-isolated.
- No trademarks, screenshots, or marketing text from 2anything are reused.
- Clean-room: implementation will follow this spec, not disassembled artifacts.
