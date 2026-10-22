# Roadmap — Any2Any

Principle: small reliable core over large weak coverage. Engine (registry/planner/jobs) is complete by M2 so format growth (M6+) never requires rewrites.

---

## Milestone 0 — Research & architecture (this package)

| | |
|---|---|
| Deliverables | All 17 docs in this repo; evidence log; MVP scope locked; name decision |
| Dependencies | public web sources only |
| Acceptance | quality gate in `14-acceptance-criteria.md` §0 passes |
| Risks | unknown original behaviors misread → mitigated by labels; PDF strategy undecided → open question |
| Excluded | any application code |

## Milestone 1 — Skeleton & local file handling

| | |
|---|---|
| Deliverables | `any2any_core` package skeleton; FormatDecl/adapter protocol; registry loader; detector (magic+ext); file/temp manager with atomic finalize; settings + history stores; safety guards; `any2any doctor/formats/config/history` stubs; CI (lint, type, test, license-gate) |
| Dependencies | Python toolchain; GitHub Actions |
| Acceptance | contract-test harness runs with a dummy adapter; EC-05/07/09/13 unit-covered; PRIV-07 green; `pip install -e .` works |
| Risks | platform path differences → use `platformdirs` early |
| Excluded | real conversions, GUI |

## Milestone 2 — Planner + first adapters (P0 core)

| | |
|---|---|
| Deliverables | planner (direct + multi-step, scores, ≤3 alternatives, direct-only); adapters: images (Pillow), tabular (CSV/TSV/JSON/JSONL/YAML), documents text (TXT/MD/HTML), subtitles SRT/VTT, geo GPX/KML/GeoJSON, QR; lossy warnings; conflict policies; `any2any convert` full flag set; golden fixtures |
| Dependencies | M1; Pillow/PyYAML/gpxpy/qrcode pins |
| Acceptance | P0 compatibility matrix (test-plan §4) green; planner unit suite green; every pair has fixture + golden; EC-01..08,14,18 covered; no external binaries yet |
| Risks | KML edge cases (styles) → scope to geometry+name; XML→JSON limitation documented |
| Excluded | GUI, pandoc/ffmpeg, OCR, chains beyond trivial (allow csv→md table chain if registered, shown as chain) |

## Milestone 3 — Usable GUI + CLI polish

| | |
|---|---|
| Deliverables | PySide6 app: S1 main window (drop, list, format, advanced, convert, progress/cancel, results, history table); S2 dynamic options; S3 settings; S4 history detail; S6 about/licenses; keyboard a11y; CLI `--json` schema + `plan --explain`; chained-plan chips |
| Dependencies | M2; PySide6 |
| Acceptance | GUI smoke suite (pytest-qt) for flows 1,2,3(partial),4,8,9; EC-21 checklist manual pass; CLI golden exit codes 0–7; NFR-8 startup |
| Risks | Qt packaging/licensing compliance → validate in M5; a11y gaps |
| Excluded | engine installer S5 (no engines yet), P1 formats |

## Milestone 4 — Batch, jobs, cancellation, history depth, P1 media/doc hub

| | |
|---|---|
| Deliverables | job manager parallelism + cancellation end-to-end (subprocess terminate); engine manager (detect, doctor deep, S5 consent installer, checksums); **ffmpeg hub**: audio convert + extract audio + basic video convert; **pandoc hub**: MD/HTML/TXT↔DOCX/ODT/RTF/EPUB/RST/TeX + PDF out via typst/latex presence; EML→(HTML)→PDF chain demo; HEIC (pillow-heif decision); history detail re-run |
| Dependencies | M3; external tool pins; counsel-ish review of GPL bundling notes (`09-…`) |
| Acceptance | EC-11,12,16 green; chains display+cleanup verified (fail-step test: intermediate deleted); PRIV-03 consent path; batch 100-file stability |
| Risks | GPL bundling mechanics; ffmpeg LGPL build config; HEIC codec patents → OS-prereq fallback |
| Excluded | OCR/STT/TTS, scientific formats, PDF→DOCX fidelity |

## Milestone 5 — Security, edge cases, packaging, automation

| | |
|---|---|
| Deliverables | T-SEC-01..08 suite; fuzz nightly; disk-full simulation; atomicity kill-tests; PyInstaller builds ×3 OS + signing/notarization setup; SBOM + `licenses` complete; offline E2E checklist; perf baselines; error-message editorial pass |
| Dependencies | M4; signing certificates (cost) |
| Acceptance | `14-acceptance-criteria.md` MVP sections green on 3 OS; zero network during full offline session; crash-residue clean |
| Risks | signing/notarization delays; PyInstaller one-folder quirks per OS |
| Excluded | any new format category |

## Milestone 6 — Expanded formats & advanced utilities

| | |
|---|---|
| Deliverables | Parquet/Feather/Arrow (pyarrow); SQLite + SQL export; Excel (openpyxl; optional LO headless); XML full; AVIF; vectorization (vtracer subprocess); archives ZIP with protections; PDF basics (split/merge/image-render via pypdf+pillow, then hub growth); ASS subtitles; certificates PEM/DER; data-hub table exports (html/docx-table at pandoc presence) |
| Dependencies | M5 stable base |
| Acceptance | each new adapter passes contract suite + fixtures; feature inventory rows flip to implemented with version tags; docs matrix updated |
| Risks | scope creep → strict admission: new format only with fixtures+tests+docs row |
| Excluded | OCR/STT/TTS (M7+), stats packages (M7), video editors, map PNG rendering (P3, evaluate separately) |

## M7+ (backlog, not committed)

- OCR (tesseract + consent models), STT (whisper.cpp + model audit), TTS (platform voices; piper only after license/voice audit), document→M4B audiobook class features, FIT, statistics packages via pyreadstat, fonts via fontTools, spectograms/contact sheets, Linux packaging polish, translations, plugin marketplace (**no — plugins are local packages only; no store, no network**).

## Milestone dependency graph

```mermaid
flowchart LR
    M0[M0 research] --> M1[M1 skeleton]
    M1 --> M2[M2 planner + P0 adapters]
    M2 --> M3[M3 GUI + CLI polish]
    M3 --> M4[M4 jobs + media/doc hubs]
    M4 --> M5[M5 security + packaging]
    M5 --> M6[M6 expanded formats]
    M6 --> M7[M7+ speech/OCR/stats backlog]
```

## Why this P0 set (rationale)

- **Usefulness:** covers the daily cases without heavyweight engines — image assets for web, tabular data for scripts, text docs, captions, routes, QR. Matches highest-frequency blog use cases (CSV↔JSON, image converts) that need no external tools.
- **Effort:** pure/short-stdlib + 6 permissive libraries; one dev can land M0–M3 in weeks not months.
- **Testability:** deterministic lossless goldens; small fixtures; no models.
- **Dependency complexity:** zero external binaries in MVP → offline test trivially green before any GPL/LGPL surface appears.
- **Balance:** every P1+ format is an adapter plug-in; engine was built for it (separation of engine from format roadmap).
