# Evidence Log

All sources inspected 2026-10-22. Confidence labels: VERIFIED (direct primary source), INFERRED (reasonable interpretation), UNKNOWN (insufficient evidence), NOT TESTED (could not run).

## Source 1: Homepage

- **URL:** https://2anything.app/
- **Date:** 2026-10-22
- **Claims supported:**
  - macOS app, local-first utility, $39 forever — VERIFIED
  - "Convert almost anything without leaving your machine" — VERIFIED (marketing claim)
  - "No uploads, no accounts, no subscriptions" — VERIFIED (marketing claim; privacy policy confirms app-side no uploads)
  - GUI mockup: drop zone, Output Format select ("Select a file first"), Advanced Settings, Convert button, Conversion History table with columns File / Conversion / Status / Date — VERIFIED (screenshot-like mockup rendered in HTML)
  - Sample history rows: PNG→ICO, TXT→MD, MP3→TXT — VERIFIED (mockup data; suggests real conversion types)
  - Format category tabs: Documents, Images, Audio, Video, Data, Geo, OCR, TTS, STT, Subtitles, Fonts, Archives — VERIFIED
  - Personas: Data Nerd, Podcaster, Paper Pusher, Designer, Explorer — VERIFIED
  - "Both app and CLI workflows" — VERIFIED (marketing claim; CLI confirmed in blog)
  - Legal entity: George-Bogdan Ivanov, Las Palmas de Gran Canaria, Spain; support@2anything.app — VERIFIED
- **Implications:** Any2Any GUI must include drop zone, format selection, advanced settings, convert action, and a history view. Persona set is a good template for user stories.

## Source 2: Pricing page

- **URL:** https://2anything.app/pricing/
- **Date:** 2026-10-22
- **Claims supported:**
  - One-time $39, no subscription, no usage limits — VERIFIED
  - Free 7-day trial; buy license to keep converting — VERIFIED
  - Requires Apple Silicon Mac — VERIFIED
  - Format list (abbreviated): Documents (PDF, DOCX, Markdown, HTML, EPUB, TXT); Images (PNG, JPG, WebP, TIFF, GIF, SVG, AVIF, ICO); Audio (MP3, WAV, FLAC, AAC, OGG, M4A); Video (MP4, MOV, GIF, contact sheets); Data (CSV, JSON, YAML, XML, SQLite, Parquet); Geo (GPX, KML, KMZ, GeoJSON, FIT); Subtitles, fonts, archives, certificates — VERIFIED (marketing list, not exhaustive matrix)
  - Features: OCR, STT (TXT/SRT/VTT), TTS, QR codes, spectrograms/waveforms, GUI + CLI, free updates within major version — VERIFIED (marketing list)
  - Privacy claims: 100% local, no uploads, no account, no telemetry, works offline — VERIFIED (marketing; consistent with privacy policy)
  - 30-day refund policy — VERIFIED
- **Implications:** Any2Any must not claim "every format"; it must publish an honest, direction-aware format matrix. Trial/subscription model is replaced by free-forever OSS.

## Source 3: Privacy Policy

- **URL:** https://2anything.app/privacy/
- **Date:** 2026-10-22
- **Version:** 2.0, effective 17 Aug 2026
- **Claims supported:**
  - "2anything performs conversions locally on your machine. Your files, their contents, their names, and their metadata are not transmitted" — VERIFIED
  - "The app has no analytics and no telemetry" — VERIFIED
  - Two network request types: (1) licence validation (activation + periodically), (2) update checks (IP + version) — VERIFIED
  - "Both can be avoided entirely by using the app offline after activation, apart from the initial activation itself" — VERIFIED
  - Website uses Plausible Analytics (cookieless, EU) — VERIFIED (site-side only)
  - Purchases via Gumroad (merchant of record) — VERIFIED
- **Implications:** Any2Any must be strictly zero-network by default. No license server. Update check, if any, must be opt-in.

## Source 4: Terms of Service

- **URL:** https://2anything.app/terms/
- **Date:** 2026-10-22
- **Version:** 2.0, effective 17 Aug 2026
- **Claims supported:**
  - Perpetual, non-exclusive, non-transferable licence for major version purchased — VERIFIED
  - "The app validates your licence key over the internet when you activate it, and may re-check it periodically" — VERIFIED
  - Third-party and open-source components remain under their own licences; attribution available in app — VERIFIED
  - Governing law: Spain; consumer rights under Spanish/EU law — VERIFIED
- **Implications:** Any2Any removes the need for any of this by being MIT-licensed OSS with no activation.

## Source 5: Refund Policy

- **URL:** https://2anything.app/refund-policy/
- **Date:** 2026-10-22
- **Claims supported:** 30-day voluntary refund; statutory 14-day withdrawal not waived; Gumroad processes refunds; licence deactivated on refund — VERIFIED (commercial policy; not applicable to Any2Any).

## Source 6: Use case — Data Nerd

- **URL:** https://2anything.app/use-cases/data-nerd/
- **Date:** 2026-10-22
- **Claims supported (format matrix):**
  - Data engineering: Parquet, Feather, Arrow IPC, MessagePack (read+write implied) — VERIFIED (marketing list)
  - Science/ML arrays: HDF5 `.h5` (RW), `.hdf5` input only; NumPy `.npy` `.npz`; MATLAB `.mat`; NetCDF `.nc` input only — VERIFIED
  - Statistics: SPSS `.sav` `.zsav` `.por`; Stata `.dta`; SAS `.sas7bdat` input only; SAS `.xpt` — VERIFIED
  - Binary JSON: BSON, CBOR — VERIFIED
  - Tabular: CSV, TSV, JSON, JSONL, Excel `.xlsx` `.xlsm`, XML, YAML `.yaml` `.yml`, SQLite `.sqlite` `.sqlite3` `.db` — VERIFIED
  - Table exports (output only): SQL script, HTML table, Word table (DOCX), PDF table — VERIFIED
  - Workflows: MATLAB→Parquet, SPSS→CSV, JSONL→Feather — VERIFIED
- **Label note:** "Supported" here means the marketing page lists the format; per-direction fidelity and options are UNKNOWN without execution.

## Source 7: Use case — Podcaster

- **URL:** https://2anything.app/use-cases/podcaster/
- **Date:** 2026-10-22
- **Claims supported:**
  - Audio RW: MP3, WAV, FLAC, AAC, M4A, M4B, OGG, Opus, AIFF; WMA input only — VERIFIED
  - STT: audio/video → TXT, SRT, VTT; offline — VERIFIED (marketing)
  - TTS: plain text / Markdown → any writable audio format — VERIFIED (marketing)
  - Subtitles: SRT, VTT, ASS, SSA, SUB; export to JSON or plain text — VERIFIED
  - Video RW: MP4, MOV, MKV, WebM, AVI; FLV, WMV, M4V input only; Video→GIF; extract audio track — VERIFIED
  - Visuals: spectrograms, waveforms, contact sheets, frames as PNG/JPG/WebP — VERIFIED
  - Workflows: MP3→SRT, Markdown→audio, WAV→MP3 — VERIFIED

## Source 8: Use case — Paper Pusher

- **URL:** https://2anything.app/use-cases/paper-pusher/
- **Date:** 2026-10-22
- **Claims supported:**
  - Office: DOCX, ODT, RTF, PPTX; legacy DOC input only — VERIFIED
  - PDF: PDF; scanned PDFs via automatic OCR — VERIFIED (marketing)
  - Markup: Markdown, HTML, TXT, reStructuredText, LaTeX — VERIFIED
  - Ebooks: EPUB — VERIFIED
  - Conversion matrix claim: "Every format here converts to every other, with three exceptions: PDFs convert to every format except PPTX, legacy .doc files convert to PDF only, and PowerPoint input brings over slide titles and text" — VERIFIED (marketing claim; directions documented, fidelity UNKNOWN)
  - Workflows: PDF→DOCX, Markdown→EPUB, PPTX→Markdown — VERIFIED

## Source 9: Use case — Designer

- **URL:** https://2anything.app/use-cases/designer/
- **Date:** 2026-10-22
- **Claims supported:**
  - Raster RW: PNG, JPG, WebP, AVIF, TIFF, GIF, BMP; HEIC/HEIF input only (note: release 0.22.1 later says HEIC is also an output format — VERIFIED both, version-dependent) — VERIFIED
  - Vectors: SVG; vectorize raster→SVG; ICO — VERIFIED
  - Fonts: TTF, OTF, WOFF, WOFF2 — VERIFIED
  - Extras: QR from text/URLs/vCards/JSON/CSV → PNG/JPG/WebP/SVG; images→PDF; PDF pages→images; OCR text extraction; video contact sheets — VERIFIED
  - Limitation: "TrueType fonts can't become OTF, which needs CFF outlines" — VERIFIED (documented limitation)
  - Workflows: PNG→SVG, PNG→ICO, PNG→WebP — VERIFIED

## Source 10: Use case — Explorer

- **URL:** https://2anything.app/use-cases/explorer/
- **Date:** 2026-10-22
- **Claims supported:**
  - Tracks: GPX RW; FIT input only — VERIFIED
  - Maps: KML, KMZ, GeoJSON — VERIFIED
  - Exports (output only): CSV of points, PNG map image — VERIFIED
  - Workflows: FIT→GPX, GPX→KML, KML→GeoJSON — VERIFIED

## Source 11: Blog — PDF/EPUB to audiobook

- **URL:** https://2anything.app/blog/pdf-to-audiobook-mac/
- **Date:** 2026-10-22
- **Claims supported:**
  - Inputs: PDF, DOCX, EPUB, HTML, ODT, RTT → M4B — VERIFIED
  - CLI examples: `2anything book.pdf --to m4b`, `--set voice Samantha`, `--set bitrate 96k`, `--set chapter_minutes 30` — VERIFIED (documented examples)
  - TTS uses macOS `say`; chunked ≤500 words; ≤4 parallel workers; joined via ffmpeg to AAC/M4B — VERIFIED (blog technical description)
  - Chapter detection: 5 strategies (headings, PDF bookmarks, chapter lines, TOC, equal parts) with sanity checks — VERIFIED
  - Narration cleanup rules (drop page numbers, running headers, copyright page, printed TOC, figures; keep captions; hyphenation fix; scene-break pause) — VERIFIED
  - Limitations: no chapter-by-chapter progress in menubar; no chapter review UI; TXT/MD→M4B has no chapters; EPUB covers not read; voice/bitrate/chapter_minutes are CLI-only options (not in menubar app); temp disk ~2.6 MB per minute of audio — VERIFIED
  - Language detection improved: full model, restricted to languages with installed voices, 50% confidence threshold, fallback English — VERIFIED
- **Implications:** Any2Any TTS (later milestone) should chunk long text and use subprocesses, not one giant call. CLI options can lead GUI options.

## Source 12: Blog — CSV to JSON offline

- **URL:** https://2anything.app/blog/convert-csv-to-json-offline/
- **Date:** 2026-10-22
- **Claims supported:**
  - CLI: `2anything data.csv --to json`, `2anything *.csv --to json`, `2anything export.json --to csv` — VERIFIED
  - CSV→JSON semantics: header row → keys; values stay as text (34→"34", empty→""); messy headers repaired (blank→column_1, duplicates numbered); ragged rows padded, extras kept; JSON indented by 2 spaces, ensure_ascii=False — VERIFIED
  - JSON→CSV semantics: accepts array of objects, single object, wrapper key, JSON Lines; columns = union of keys in first-seen order; null→empty cell; nested values written as JSON text in one cell — VERIFIED
  - Delimiter auto-detect: comma, semicolon, tab, pipe — VERIFIED
  - Encoding: UTF-8 first, fallback Windows-1252; BOM removed — VERIFIED
  - "The conversion runs entirely on your Mac and makes no network calls" — VERIFIED (claim)
  - Excel: one sheet (active or named); dates as YYYY-MM-DD; Excel→SQLite one table per sheet — VERIFIED
  - YAML↔JSON full nested structure preserved — VERIFIED
  - XML→JSON: works for simple XML (each child of root = one record); attributes and deeper nesting not mapped — VERIFIED (limitation)
  - Parquet/Feather/Arrow ↔ CSV, JSON with compression choice — VERIFIED (marketing)
  - SPSS/Stata/SAS ↔ CSV, JSON; value labels applied by default, raw codes optional (`--set value_labels codes` in release notes); SAS7BDAT input only — VERIFIED
  - Large CSV: loaded into memory; limited by RAM — VERIFIED (documented constraint)
  - Batch: drop multiple files or `2anything *.csv --to json` — VERIFIED

## Source 13: Blog — EML to PDF

- **URL:** https://2anything.app/blog/convert-eml-to-pdf-mac/
- **Date:** 2026-10-22
- **Claims supported:**
  - CLI: `2anything *.eml --to pdf`, `2anything archive.mbox --to pdf` — VERIFIED
  - Chain: EML → HTML (email converter) → PDF (document converter using bundled Pandoc and Typst); intermediate HTML in temp, deleted after; temp deleted even on failure — VERIFIED
  - Conversion graph: >20 engines; each edge scored 0–1 for fidelity; best route = highest product of scores; shortest-path search; up to 3 fallback routes — VERIFIED (blog explains mechanism)
  - `2anything --formats mail.eml` shows target formats with step count and estimated quality — VERIFIED (documented command)
  - PDF output: header block (subject title, From/To/Cc/Date); HTML body preferred; charset respected with UTF-8/Latin-1 fallback; attachments saved to `<name>_attachments` folder and listed in PDF; sender CSS layout not reproduced; scripts removed; remote images/tracking pixels blocked by default (`block_remote_content`) — VERIFIED
  - EMLX not supported (only EML and MBOX) — VERIFIED (limitation)
  - One PDF per EML with same name; MBOX → single combined PDF — VERIFIED

## Source 14: Blog — PDF to Word

- **URL:** https://2anything.app/blog/convert-pdf-to-word-mac/
- **Date:** 2026-10-22
- **Claims supported:**
  - CLI: `2anything report.pdf --to docx`, `2anything *.pdf --to docx` — VERIFIED
  - Three PDF kinds: tagged (≥90% text tagged → rebuild real headings/lists/tables), printed (no tags → recreate look via layout engine), scanned (OCR) — VERIFIED
  - OCR: automatic for image/garbled pages only; language auto-detect; photos cropped and placed next to text — VERIFIED
  - Password-protected PDF (open-password): not supported; clear message — VERIFIED (limitation)
  - Forms: values written into page before conversion — VERIFIED
  - Not kept: comments, highlights, stamps; exact fonts/positions on tagged PDFs; heading/list styles on printed PDFs — VERIFIED (documented losses)
  - PDF pages can also render to PNG/JPG at chosen resolution — VERIFIED

## Source 15: Blog — HEIC to JPG

- **URL:** https://2anything.app/blog/convert-heic-to-jpg-mac/
- **Date:** 2026-10-22
- **Claims supported:**
  - 2anything HEIC→JPG: quality slider (default 85); keeps colour profile + EXIF by default; "Strip metadata" setting removes location included — VERIFIED
  - Also offers PNG, WebP, AVIF, PDF, OCR text outputs — VERIFIED
  - Context: HEIC = HEIF container + HEVC; Display P3; EXIF GPS — VERIFIED (technical background, not app-specific)

## Source 16: GitHub release v0.22.1

- **URL:** https://github.com/bogsio/2anything-releases/releases/tag/v0.22.1
- **Date:** 2026-10-22
- **Released:** 13 Oct 2026 (commit 6e65c6d)
- **Claims supported:**
  - Universal local-first file converter for macOS (Apple Silicon) — VERIFIED
  - Word→PDF rebuilt; placement score 0.95 vs Word's own export (LibreOffice 0.96); `pdf_engine` setting can hand job to LibreOffice/Pages/Word if installed — VERIFIED
  - Bundled fonts Carlito and Caladea (metric-compatible with Calibri/Cambria) — VERIFIED
  - PDF→Word: pdfium + pdfplumber + vendored MIT-licensed layout engine; Hebrew/Arabic logical order; 300-page PDF works; peak memory ~0.76 GB for big file; `ocr_pages` setting keeps pictures next to recognised text — VERIFIED
  - Email→PDF/Word/ODT/images: attachments linked by relative path; no temp folders left; `block_remote_content` default on — VERIFIED
  - OCR on macOS Vision (no model download); language auto-detect; `lang` takes BCP-47 tags — VERIFIED
  - TTS uses macOS voices; picks best installed voice for detected language — VERIFIED
  - STT: audio decoded with bundled ffmpeg; transcription unchanged — VERIFIED
  - HEIC/HEIF via macOS ImageIO; keeps Display P3, orientation, EXIF, GPS; HEIC also an output format — VERIFIED
  - SPSS/Stata/SAS: value labels applied by default; `--set value_labels codes` for raw codes; SAS7BDAT input only — VERIFIED
  - Excel↔SQLite/SQL: one table per sheet / one sheet per table; all sheets by default; `--set sheet <name>` picks one — VERIFIED
  - "No GPL or AGPL code loads inside the app any more; ffmpeg and pandoc ship as separate programs, pinned to exact versions with verified checksums" — VERIFIED
  - Acknowledgements menu / `2anything --licenses` shows licence and source of every bundled component — VERIFIED
  - Signed and notarized by Apple; .dmg install — VERIFIED
- **Implications:** Process isolation of copyleft tools is a proven strategy Any2Any should adopt. Pinned versions + checksums + `--licenses` output are requirements.

## Source 17: pandoc license

- **URL:** https://github.com/jgm/pandoc/ (LICENSE / COPYRIGHT)
- **Date:** 2026-10-22
- **Claim:** pandoc is GPL-2.0-or-later. Templates dual GPL/BSD-3. Some writers GPL-2.0+. — VERIFIED
- **Implication:** Any2Any must not link pandoc in-process; invoke as external process; distribute unmodified binary with license texts and source offer as required by GPL when distributing the binary.

## Source 18: whisper.cpp license

- **URL:** https://github.com/ggml-org/whisper.cpp/blob/master/LICENSE
- **Date:** 2026-10-22
- **Claim:** whisper.cpp is MIT License. — VERIFIED
- **Note:** maintainer discussion (2025-02) noted CI/docs/packaging gaps; core implementation healthy. — VERIFIED (GitHub discussion #2788)
- **Implication:** Suitable for redistribution as subprocess; model weights have separate licenses (not audited here — UNKNOWN for specific model files).

## Source 19: pyreadstat license

- **URL:** https://github.com/Roche/pyreadstat (LICENSE, README)
- **Date:** 2026-10-22
- **Claim:** pyreadstat Apache-2.0; wraps ReadStat C library (MIT). Reads/writes SAS (sas7bdat, xport), SPSS (sav, zsav, por), Stata (dta). Write support: SPSS sav/zsav/por, Stata dta, SAS Xport; sas7bdat/sas7bcat write currently not supported. — VERIFIED
- **Implication:** Candidate adapter for Any2Any P2 statistics formats.

## Source 20: piper-tts license

- **URL:** https://github.com/OHF-Voice/piper1-gpl/ and https://pypi.org/project/piper-tts/
- **Date:** 2026-10-22
- **Claim:** piper-tts runtime GPL-3.0-or-later. Voice weights in rhasspy/piper-voices are MIT (separate). Some voice training datasets have non-commercial clauses — must check per voice. — VERIFIED (package + third-party analysis)
- **Implication:** If Any2Any ships TTS, piper must be a separate process (never linked); voice weights license and dataset clauses must be audited per voice; distribution of GPL binary triggers source-offer obligations.

## Not inspected / limitations

- The macOS application binary itself: not downloaded or executed (Windows host, no Apple Silicon; also out of scope per clean-room rules against extracting proprietary resources). — NOT TESTED
- Gumroad checkout flow: not exercised. — NOT TESTED
- Blog posts listed on /blog/ beyond the five fetched: only titles/dates seen on index. — UNKNOWN (content not fetched)
- Screenshots or videos beyond the HTML mockup and blog SVG diagrams: none found on public pages. — UNKNOWN
- Version history before v0.22.1 (release notes referenced 0.13.8): only mentioned in v0.22.1 text, not fetched individually. — INFERRED (older versions existed)
