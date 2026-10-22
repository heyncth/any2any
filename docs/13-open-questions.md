# Open Questions — Any2Any

| # | Question | Impact | Priority | How to answer |
|---|---|---|---|---|
| Q1 | Final product name & trademark clearance (Any2Any is working name) | branding, domains, package names | High (before public release) | trademark search per jurisdiction; PyPI/GitHub name availability check |
| Q2 | PDF pipeline choice for P1: Typst (Apache-2.0, fast) vs WeasyPrint (BSD, CSS) vs headless LibreOffice (user-installed) vs pandoc+extra | M4 scope, licenses, fidelity | High (block M4 planning) | build 3 spikes on same fixtures; score layout fidelity + packaging weight |
| Q3 | PDF→DOCX fidelity engine (M7): vendor MIT layout engine (2a claims one exists — VERIFIED as their claim, ours must be independent), pdfium+pdfplumber+own heuristics, or LibreOffice round-trip | big milestone cost | Medium | prototype tagged-PDF path first; measure on open corpora |
| Q4 | Raster→SVG vectorizer choice: vtracer (GPL-3, subprocess) vs potrace (GPL-2+, subprocess) vs own (cost high) | M6 license surface | Medium | compare output on logo fixtures; counsel note on bundling GPL binaries |
| Q5 | HEIC strategy on Windows/Linux (patents): pillow-heif (LGPL in-process), system dependency, or macOS-only feature | platform parity claims | Medium (M4) | spike wheel availability + license compliance review |
| Q6 | Should history DB be SQLite (default plan) or JSONL (simpler, greppable)? | M1 build | Low | both trivial; decide by 50k-row benchmark (planned M1) |
| Q7 | GIF animation support in P0 or drop animated GIF (treat first frame)? | P0 scope honesty | Low (decide M2) | check fixture effort; if anim needed, defer to M6 with warning |
| Q8 | Distribution channel priority: GitHub Releases only vs also Homebrew/winget/scoop/flathub | M5 | Medium | maintainer bandwidth; flathub review time is long (INFERRED) |
| Q9 | Model weight licenses for STT/TTS (whisper model cards, piper voice datasets) | M7 features legal | High before M7 | per-model audit table; skip non-commercial voices |
| Q10 | Minimum OS versions to claim (macOS 13? Ubuntu 22.04? Win10?) | support matrix | Medium (M5) | CI matrix + manual smoke per OS |
| Q11 | Config file format: TOML (plan) vs YAML vs JSON | trivial churn | Low | pick TOML at M1, revisit never unless parser pain |
| Q12 | Does `convert` glob support belong in CLI (shell does it) — Windows cmd doesn't glob | UX on Windows | Medium (M3) | test cmd/pwsh; likely add opt-in `--glob` if Windows story weak |
| Q13 | Update story long-term: none (plan) vs opt-in check | privacy doc accuracy | Low (M2+ revisit) | if added: opt-in, version-only, documented test |
| Q14 | i18n at 1.0 or later | string architecture cost | Low | externalize strings from M3 anyway (NFR-10) |
| Q15 | Exact original trial limits & settings pane (UNKNOWN per evidence log) | parity claims | Low — we don't need parity here | would require running original on macOS; optional Phase B if hardware appears |
| Q16 | Bundle size policy: PyInstaller one-folder size vs minimal core + optional engine downloads | user experience, mirrors 2a ~500MB lesson (VERIFIED release note) | Medium (M4/M5) | measure; likely: small base + optional downloads |

## Research gaps (from evidence log) that don't block architecture but matter for docs

- Fidelity score calibration: our numbers in `06-conversion-engine.md` are starting guesses (INFERRED class). Recalibrate with pairwise user studies or error-rate measurements when adapters land.
- Full original engine list: only ~30+ formats across pages documented; >20 engines claimed (VERIFIED count claim) but identities UNKNOWN — no action needed for clean-room scope.
- Blog index shows more posts (titles only fetched): revisit for format edge-case documentation if needed later.
