# Dependencies & Licensing Audit — Any2Any

**Principle:** open source ≠ free for every use. Every candidate below carries license, obligations, and redistribution notes. Core app targets **MIT**; copyleft components are only acceptable when process-isolated (never linked) and distributed with full license texts and source offers where required. **This is engineering guidance, not legal advice** — items marked ⚠ need counsel review before a commercial-adjacent release.

**Inspection date:** 2026-10-22. Maintenance notes from GitHub/PyPI state on that date.

---

## 1. Core runtime (linked into Any2Any — must be MIT-compatible)

| Component | Repo | License | Maint status | Role | Redistribution | Notes |
|---|---|---|---|---|---|---|
| Python 3.12+ | python.org | PSF-2.0 | active | runtime | fine | bundle runtime in PyInstaller |
| PySide6 (Qt) | pyside.io / code.qt.io | LGPL-3.0-only (with exceptions) / GPL-3.0-or-later dual, parts BSD-3 | active (Qt Company) | GUI | LGPL ok if dynamic linking + notices + relink ability | ship Qt LGPL texts; keep Qt as shared libs |
| Click | pallets/click | BSD-3 | active | CLI | fine | |
| Pillow | python-pillow/Pillow | MIT-CMU (HPND-ish) | very active | images P0 | fine | includes zlib/libjpeg-turbo under permissive licenses; some optional codecs have patent notes (see §4) |
| PyYAML | yaml/pyyaml | MIT | moderate (maintained) | YAML P0 | fine | use safe_load only (SEC) |
| markdown-it-py | markdown-it/markdown-it-py | MIT | active | MD P0 | fine | |
| gpxpy | tkrajina/gpxpy | Apache-2.0 | moderate | geo P0 | fine | |
| lxml | lxml/lxml | BSD-3 AND GPL-3.0 (dual) ⚠ | very active | XML/KML P0 | choosing BSD-3 branch allowed | lxml is dual-licensed; use BSD-3 option explicitly; record decision in NOTICE |
| qrcode | lincolnloop/python-qrcode | BSD-3 | moderate | QR P0 | fine | PIL backend needed for raster |
| pysrt / webvtt-py | | MIT / BSD-3 (verify at pin) | moderate | subtitles P0 | fine | pin then re-verify |
| packaging / platformdirs | | Apache-2.0 / MIT | active | paths | fine | |
| pytest + plugins | | MIT | active | dev | not shipped | |

## 2. P1/P2 Python libraries (same policy: permissive only in-process)

| Component | Repo | License | Role | Flags |
|---|---|---|---|---|
| pyarrow | apache/arrow | Apache-2.0 | Parquet/Feather/Arrow | fine; large binary wheels |
| openpyxl | | MIT (check current) | XLSX | pure-python, slow for huge sheets (documented limit) |
| sqlite3 | stdlib | PD | SQLite | fine |
| pillow-heif | | LGPL-3.0 ⚠ | HEIC | **LGPL**: prefer dynamic/loading pattern acceptable for desktop app; alternatives: subprocess to `sips`(macOS-only) / `heif-convert`. Decision M4. |
| pillow-avif-plugin | | BSD-3? (verify pin) | AVIF | verify at pin; codec AV1 is royalty concerns only for encoders — see §4 |
| pyreadstat | Roche/pyreadstat | Apache-2.0 (bundles ReadStat MIT) | SPSS/Stata/SAS | fine; sas7bdat write unsupported upstream (matches 2a input-only claim) |
| h5py | | BSD-3 | HDF5 | HDF5 lib itself: BSD-3-style `COPYING` — fine |
| numpy | | BSD-3 | npy/npz | fine |
| scipy | | BSD-3 | .mat | fine (GPL historically? — BSD-3 since 1.0) |
| cbor2 / pymongo bson / msgpack | | MIT / Apache-2.0 / MIT | binary JSON | fine |
| fitparse | | Apache-2.0 | FIT | fine |
| openpyxl vs libreoffice | | — | Excel fidelity | headless LibreOffice (MPL-2.0) as external process if needed ⚠ MPL file-level obligations if modified (we don't modify) |
| cryptography | pyca/cryptography | Apache-2.0 OR BSD-3 | certificates P2 | OpenSSL/Rust under Apache-2.0 — fine |

## 3. External binaries (process-isolated, optionally bundled/downloaded)

| Tool | License | Strategy | Pinning | Why isolated |
|---|---|---|---|---|
| ffmpeg | LGPL-2.1+ core; **GPL parts if configured `--enable-gpl`** ⚠ | ship/build **LGPL configuration only** (no `--enable-gpl`, no nonfree); or use system ffmpeg | version + sha256 in manifest | avoids copyleft propagation into our work; audio/video P1 |
| pandoc | **GPL-2.0-or-later** ⚠ | external process only; distribute unmodified binary + license texts + **written offer/source URL for corresponding source** (GPL §6 when distributing) | version + sha256 | documents hub P1; same strategy 2anything publicly adopted (VERIFIED release note) |
| typst | Apache-2.0 | external process (PDF typesetting) | sha256 | permissive; good HTML/MD→PDF candidate |
| tesseract | Apache-2.0 | external process; language data files have own licenses (mostly Apache) — check each traineddata | model manifest | OCR P2 |
| resvg | MPL-2.0 | external process (file-level copyleft; unmodified binary = only notice obligations) | sha256 | SVG→raster P0 *optional dep* |
| vtracer / potrace | GPL-3.0 (vtracer) / GPL-2.0+ (potrace) ⚠ | external process only; binary + source offer | sha256 | raster→SVG P2 |
| whisper.cpp | MIT | external process | version+sha256 | STT P2; **model weights separate licenses** (OpenAI Whisper weights: MIT-mit? actual model card terms — verify per model, ⚠) |
| piper-tts | **GPL-3.0-or-later** runtime; voice weights MIT (separate repo) ⚠ | external process; **per-voice dataset license audit** (some voices trained on non-commercial corpora) | manifest per voice | TTS P2/P3; counsel review before bundling |
| LibreOffice (headless) | MPL-2.0 + many bundled components ⚠ | external, usually *user-installed*, never bundled by us (size/patents) | detect only | optional `pdf_engine`-style fallback (parity with 2a VERIFIED `pdf_engine` setting) |
| macOS Vision / `say` / `sips` | Apple OS frameworks | use via public APIs/subprocess on macOS only | n/a | OCR/TTS/HEIC parity with 2a strategies; no redistribution |

## 4. Codec / patent / data caveats

1. **HEVC (HEIC decode/encode):** patent pools; Apple ships decoder on macOS. Windows redistribution of decoders may need purchases (HEVC Video Extensions precedent). Mitigation: use user-installed/system codecs or document OS prerequisite; do not bundle proprietary decoders. ⚠
2. **AV1 encode:** royalty-free (AOM) — safe; watch encoder impl license.
3. **MP3:** patents expired (2017) — fine.
4. **Fonts:** bundling Carlito/Caladea (as 2a does, VERIFIED) → both are **OFL-1.1** (verify at pin) — OFL permits bundling with attribution; keep font licenses. Do not bundle Microsoft fonts (Calibri metrics — Carlito is the clean-room metric clone, OFL).
5. **OCR models:** tesseract tessdata mostly Apache-2.0; some community models differ — per-file manifest.
6. **STT/TTS models:** each model card audited before enabling in installer (whisper weights license, piper voice dataset clauses). Until audited → status UNKNOWN → not offered.
7. **Qt LGPL relinking:** AppImage/deb must allow users to replace Qt libs (standard dynamic linking satisfies this; document how).

## 5. License obligations summary (what Any2Any must ship)

| Obligation | Trigger | Artifact |
|---|---|---|
| Attribution + license texts for all bundled deps | any distribution | `share/any2any/licenses/` + `any2any licenses` command |
| Qt LGPL: notices, dynamic linking, relink info | bundling PySide6 | LICENSES/PySide6*, README section |
| GPL binaries (pandoc, vtracer, potrace, piper): license text + source offer or pointer | distributing those binaries in installers | `THIRD_PARTY_NOTICES.md` with URLs + written offer text (or link if network distribution allowed per GPL practice — counsel ⚠) |
| ffmpeg LGPL build: notices, ability to relink/replace | bundling | build config documented, scripts published |
| OFL fonts: license text + no modification claim | bundling fonts | OFL.txt + README |
| MPL files: unmodified notice | bundling resvg/libreoffice | notices file |
| No 2anything assets/text | always | clean-room review checklist |

**SBOM:** generate CycloneDX at release; includes versions + licenses (tool: `cyclonedx-bom` or syft in CI).

## 6. Copyleft isolation rules (engineering law of the project)

1. GPL/AGPL **components never become importable modules** of `any2any_core`. Enforced by: architecture review + CI license-gate on `requirements.lock` (fail on GPL entries in core extra) + subprocess-only invocation sites.
2. Distribution boundary: if we ship a GPL binary in the installer, the installer must satisfy that binary's own license (texts + source) **without** relicensing our MIT code; do not create a combined work by linking (this is the standard separation-of-processes approach used by many tools; still ⚠ counsel for final shipping form).
3. LGPL libraries in-process (PySide6, maybe pillow-heif): comply via dynamic linking + notices + user override.
4. Any new dependency enters via PR with license row added to this doc *before* code merge (process requirement).

## 7. Maintenance watchlist (as of 2026-10-22)

- whisper.cpp: packaging/CI gaps raised by upstream maintainer (VERIFIED discussion #2788) — risk: bitrot; mitigation: pin known-good version, wrap with our own release testing.
- PyYAML: maintenance slower — mitigation: consider ruamel.yaml (MIT) if issues; safe-load only anyway.
- pysrt/webvtt-py: small maintainers — mitigation: contract tests; possible in-house minimal SRT/VTT codecs (they are simple text formats — fallback is ~200 lines, P0-friendly).
