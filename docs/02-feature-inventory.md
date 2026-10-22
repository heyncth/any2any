# Feature Inventory & Format Matrix

**Legend — confidence labels**

- **VERIFIED**: claim appears in a primary source (official page, release notes, blog by the author).
- **INFERRED**: reasonable interpretation of observable evidence.
- **UNKNOWN**: insufficient public evidence.
- **NOT TESTED**: behavior could not be observed by execution.
- **2a-doc**: what 2anything's pages document (not executed).
- **2a-run**: what 2anything demonstrably does at runtime — none available; all NOT TESTED.
- **Any2Any plan**: proposed implementation with priority P0 (MVP) … P3.

Direction rules: "listed as supported" ≠ verified both directions. Input-only and output-only markings come from explicit source statements.

---

## A. Product, licensing, platform

| Item | 2anything documentation | Label | Any2Any plan |
|---|---|---|---|
| OS | macOS only, Apple Silicon required | VERIFIED (pricing) | P0: Windows, macOS, Linux; architecture not compromised for breadth |
| GUI | Menubar app, drag-drop, history | VERIFIED (homepage mockup, blog "menubar app") | P0: desktop window app |
| CLI | `2anything … --to …`, `--set`, `--formats`, `--licenses` | VERIFIED (blog, release) | P0: full CLI parity for core ops |
| Trial | 7 days free; license to keep converting | VERIFIED (pricing) | N/A (free forever) |
| Price | $39 one-time, Gumroad | VERIFIED | N/A (MIT) |
| Account | None | VERIFIED (pricing/privacy) | N/A |
| Telemetry | None | VERIFIED (privacy policy) | N/A (none, by requirement) |
| Network | Licence validation + update check; offline after activation | VERIFIED (privacy policy) | None by default; opt-in update check |
| Updates | Free within major version | VERIFIED (terms §8) | Standard OSS releases; optional update check opt-in |
| Trial UI limits | Unknown (watermark? format locks?) | UNKNOWN | — |
| CLI on non-macOS | Product is macOS-only | UNKNOWN whether CLI exists elsewhere | P0 cross-platform CLI |
| Version at inspection | v0.22.1 (13 Oct 2026); v0.23 referenced for audiobook | VERIFIED (GitHub) | — |

## B. Application interface

Source: homepage mockup (VERIFIED visual), blog descriptions (VERIFIED text).

| Screen/element | Evidence | Label | Any2Any |
|---|---|---|---|
| Drop zone "Drop files here or click to browse" | homepage mockup | VERIFIED | P0 |
| Output Format dropdown; placeholder "Select a file first" (options depend on selection) | homepage mockup | VERIFIED | P0 |
| Advanced Settings (collapsible) | homepage mockup | VERIFIED | P0 |
| Convert button | homepage mockup | VERIFIED | P0 |
| Conversion History table: File / Conversion / Status / Date | homepage mockup | VERIFIED | P0 |
| Time estimate during conversion | blog audiobook ("usual time estimate") | VERIFIED | P1 (progress + ETA) |
| Chapter-by-chapter progress for TTS | blog: "not yet" | VERIFIED (absence) | P2 |
| Settings/preferences pane details | not documented publicly | UNKNOWN | P0 minimal (output policy, overwrite, defaults) |
| Accessibility of original | not documented | UNKNOWN | P0 requirement (NFR-6) |
| Cancel control | not explicitly documented; ETA implies running job UI | INFERRED | P0 required |

## C. Format matrix by category

### C1. Documents and text

| Format | Read (2a-doc) | Write (2a-doc) | Label | Any2Any plan |
|---|---|---|---|---|
| PDF | yes | yes | VERIFIED (use case) | P1 (PDF→text/DOCX complex; MVP: render/split later) |
| DOCX | yes | yes | VERIFIED | P1 via pandoc subprocess |
| DOC (legacy) | yes, input only → PDF only | no | VERIFIED (explicit) | P3 (skip; rare) |
| ODT | yes | yes | VERIFIED | P1 (pandoc) |
| RTF | yes | yes | VERIFIED | P1 (pandoc) |
| PPTX | yes | yes; input brings slide titles/text only | VERIFIED | P2 (text extraction) |
| EPUB | yes | yes | VERIFIED | P1 (pandoc) |
| Markdown `.md` | yes | yes | VERIFIED | P0 (native, markdown-it style) |
| HTML | yes | yes | VERIFIED | P0 (native) |
| TXT | yes | yes | VERIFIED | P0 |
| reStructuredText | yes | yes | VERIFIED | P1 (pandoc) |
| LaTeX `.tex` | yes | yes | VERIFIED | P1 (pandoc) |
| EML / MBOX | yes | — (converts to PDF/DOCX/ODT/images) | VERIFIED (blog) | P1 |
| PDF→DOCX fidelity | tagged/printed/scanned paths; OCR auto | — | VERIFIED (blog, untested) | P2 (big effort; separate milestone) |
| Scanned PDF OCR | auto via macOS Vision | — | VERIFIED (release) | P2 (tesseract subprocess) |
| Password PDF (open) | rejected with message | — | VERIFIED (FAQ) | P1 same behavior |

### C2. Images and vectors

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| PNG | yes | yes | VERIFIED | P0 (Pillow) |
| JPG/JPEG | yes | yes | VERIFIED | P0 (quality option default 85 per HEIC blog) |
| WebP | yes | yes | VERIFIED | P0 (Pillow) |
| AVIF | yes | yes | VERIFIED | P1 (pillow-avif plugin or subprocess) |
| TIFF | yes | yes | VERIFIED | P0 (Pillow) |
| GIF | yes | yes | VERIFIED | P0 static frames; animation P2 |
| BMP | yes | yes | VERIFIED | P0 |
| HEIC/HEIF | yes | yes (since 0.22.1) | VERIFIED (input-only earlier, both later) | P1 (pillow-heif) |
| SVG | yes (rasterize) | yes (vectorize from raster) | VERIFIED | P0: SVG→raster (resvg subprocess); P2: raster→SVG (vtracer/potrace) |
| ICO | yes | yes | VERIFIED | P0 (Pillow) |
| Metadata (EXIF/ICC) | kept by default; strip option | VERIFIED (HEIC blog) | P0 same semantics |
| Spectrograms, waveforms, contact sheets, frames | yes (exports) | — | VERIFIED (podcaster/designer) | P2 |
| Images→PDF / PDF pages→images | yes | — | VERIFIED | P1 |

### C3. Audio

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| MP3, WAV, FLAC, AAC, M4A, OGG, Opus, AIFF | yes | yes | VERIFIED (podcaster) | P1 (ffmpeg subprocess) |
| M4B (audiobook) | yes | yes (create w/ chapters) | VERIFIED (blog) | P3 |
| WMA | yes | input only | VERIFIED | P1 |
| Extract audio from video | — | yes | VERIFIED | P1 |

### C4. Video

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| MP4, MOV, MKV, WebM, AVI | yes | yes | VERIFIED | P1 (ffmpeg) |
| FLV, WMV, M4V | yes | input only | VERIFIED | P1 |
| Video→GIF | — | yes | VERIFIED | P2 |
| Contact sheets, frame export | — | yes | VERIFIED | P2 |

### C5. Structured data and spreadsheets

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| CSV / TSV | yes | yes | VERIFIED | P0 (native; delimiter detect, encoding fallback, BOM strip — semantics from blog) |
| JSON | yes | yes | VERIFIED | P0 (array-of-objects shapes per blog) |
| JSONL | yes | yes | VERIFIED | P0 |
| YAML | yes | yes | VERIFIED | P0 (PyYAML) |
| XML | yes | yes | VERIFIED | P0→simple XML→JSON (documented limitation: root-child records only); full XML P2 |
| XLSX / XLSM | yes | yes | VERIFIED | P1 (openpyxl or libreoffice subprocess for fidelity) |
| SQLite `.sqlite/.sqlite3/.db` | yes | yes | VERIFIED | P1 (stdlib sqlite3) |
| SQL script export | — | output only | VERIFIED | P1 |
| HTML table / DOCX table / PDF table exports | — | output only | VERIFIED | P1 |
| YAML↔JSON nested structure preserved | yes | yes | VERIFIED (blog) | P0 same |

### C6. Data engineering and scientific

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| Parquet | yes | yes (compression choice) | VERIFIED | P1 (pyarrow) |
| Feather / Arrow IPC | yes | yes | VERIFIED | P1 (pyarrow) |
| MessagePack | yes | yes | VERIFIED | P2 |
| HDF5 `.h5` | yes | yes | VERIFIED | P2 (h5py) |
| HDF5 `.hdf5` | yes | input only | VERIFIED | P2 |
| NumPy `.npy`/`.npz` | yes | yes | VERIFIED | P2 (numpy) |
| MATLAB `.mat` | yes | yes | VERIFIED | P2 (scipy.io) |
| NetCDF `.nc` | yes | input only | VERIFIED | P3 (netCDF4) |
| BSON / CBOR | yes | yes | VERIFIED | P2 (cbor2/bson) |

### C7. Statistics packages

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| SPSS `.sav` `.zsav` | yes | yes | VERIFIED | P2 (pyreadstat, Apache-2.0) |
| SPSS `.por` | yes | yes | VERIFIED | P2 (pyreadstat) |
| Stata `.dta` | yes | yes | VERIFIED | P2 (pyreadstat) |
| SAS `.xpt` | yes | yes | VERIFIED | P2 (pyreadstat) |
| SAS `.sas7bdat` | yes | input only | VERIFIED (also matches pyreadstat limitation) | P2 read-only |
| Value labels default on; raw codes option | — | — | VERIFIED (release `--set value_labels codes`) | P2 same option |

### C8. Geographic and GPS

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| GPX | yes | yes | VERIFIED | P0 (gpxpy) |
| KML / KMZ | yes | yes | VERIFIED | P0 (KML via lxml); KMZ P1 |
| GeoJSON | yes | yes | VERIFIED | P0 (native json + validation) |
| FIT | yes | input only | VERIFIED | P2 (fitparse subprocess/lib) |
| CSV of points export | — | output only | VERIFIED | P1 |
| PNG map image export | — | output only | VERIFIED | P3 (map rendering heavy) |

### C9. Subtitles

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| SRT | yes | yes | VERIFIED | P0 |
| VTT | yes | yes | VERIFIED | P0 |
| ASS / SSA / SUB | yes | yes | VERIFIED | P1 |
| Sub→JSON / plain text | — | yes | VERIFIED | P1 |

### C10. Fonts

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| TTF, OTF, WOFF, WOFF2 | yes | yes | VERIFIED | P2 (fontTools; caveat: TTF→OTF/CFF not possible losslessly — same limitation as 2anything, VERIFIED) |

### C11. Archives

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| Archives category mentioned (ZIP etc. not enumerated) | yes? | yes? | INFERRED (category listed; specifics UNKNOWN) | P2 ZIP create/extract with zip-slip protections |

### C12. Certificates

| Format | Read | Write | Label | Any2Any plan |
|---|---|---|---|---|
| Certificates category mentioned (PEM/CRT not enumerated) | yes? | yes? | INFERRED (category listed; specifics UNKNOWN) | P2 (PEM→DER etc. via cryptography lib) |

### C13. OCR

| Capability | 2a-doc | Label | Any2Any plan |
|---|---|---|---|
| Image→text (macOS Vision; BCP-47 `lang`) | yes | VERIFIED (release) | P2 (tesseract subprocess; model download disclosed) |
| PDF OCR (auto on image/garbled pages; `ocr_pages`) | yes | VERIFIED (blog/release) | P2 |

### C14. Speech-to-text

| Capability | 2a-doc | Label | Any2Any plan |
|---|---|---|---|
| Audio/video→TXT/SRT/VTT, offline | yes | VERIFIED (marketing; engine not named → UNKNOWN which engine) | P2 (whisper.cpp subprocess, MIT; model download consent) |

### C15. Text-to-speech

| Capability | 2a-doc | Label | Any2Any plan |
|---|---|---|---|
| Text/MD→audio via macOS `say` | yes | VERIFIED (blog) | P2 (cross-platform: platform TTS or piper GPL subprocess — see license audit) |
| Document→M4B audiobook w/ chapters | yes (v0.23) | VERIFIED (blog) | P3 |
| Options voice/bitrate/chapter_minutes CLI-only | yes | VERIFIED (blog) | CLI-first options policy documented |

### C16. Utilities

| Capability | 2a-doc | Label | Any2Any plan |
|---|---|---|---|
| QR generation (text/URL/vCard/JSON/CSV → PNG/JPG/WebP/SVG) | yes | VERIFIED (designer page) | P0 (qrcode lib: PNG/SVG; JPG/WebP via Pillow) |
| QR decode | not documented | UNKNOWN | not planned (P3) |

## D. Documented conversion directions (special rules)

From Paper Pusher page (VERIFIED doc claim):

1. "Every format [DOCX, ODT, RTF, PPTX, PDF, Markdown, HTML, TXT, RST, LaTeX, EPUB] converts to every other" **except**:
2. PDF → everything **except** PPTX.
3. Legacy DOC → **PDF only**.
4. PPTX input: only slide titles and text carried.

From Designer page (VERIFIED doc claim):

5. SVG → raster formats direct; raster → SVG only by vectorizing.
6. TTF → OTF not possible (needs CFF outlines).

From Explorer page (VERIFIED doc claim): FIT input-only; CSV/PNG exports output-only.

**Any2Any must publish equivalent explicit direction rules per adapter and refuse unsupported directions with `E_UNSUPPORTED_DIRECTION`.**

## E. Use-case workflows (documented → proposed parity)

| # | Workflow (2a-doc, VERIFIED) | Config/edges | Any2Any milestone |
|---|---|---|---|
| U1 | MATLAB `.mat` → Parquet | data hub | P2 |
| U2 | SPSS `.sav` → CSV | value labels default | P2 |
| U3 | JSONL → Feather | compression option | P1 |
| U4 | MP3 → SRT (transcribe) | STT engine | P2 |
| U5 | Markdown → audio (TTS) | voices | P2 |
| U6 | WAV → MP3 | ffmpeg, bitrate | P1 |
| U7 | PDF → DOCX (OCR if scanned) | layout engine | P2 |
| U8 | Markdown → EPUB | pandoc | P1 |
| U9 | PPTX → Markdown (titles/text) | extractor | P2 |
| U10 | PNG → SVG (vectorize) | vectorizer | P2 |
| U11 | PNG → ICO | Pillow sizes | P0 |
| U12 | PNG → WebP (quality) | Pillow | P0 |
| U13 | FIT → GPX | fitparse | P2 |
| U14 | GPX → KML | gpxpy + kml writer | P0 |
| U15 | KML → GeoJSON | parser | P0 |
| U16 | EML → PDF (chain via HTML) | email parser + document hub | P1 |
| U17 | CSV ↔ JSON | semantics above | P0 |
| U18 | HEIC → JPG (quality 85, EXIF keep/strip) | pillow-heif | P1 |
| U19 | Document → M4B audiobook | TTS + ffmpeg | P3 |
| U20 | QR from text/URL | qrcode | P0 |

## F. Explicit gaps vs. 2anything (honest scope)

Any2Any MVP does **not** claim: full PDF↔DOCX/EPUB fidelity, OCR, STT, TTS/audiobook, video, spectrograms, contact sheets, fonts, archives, certificates, scientific array formats, statistics packages, Excel, SQLite, FIT, KMZ, HEIC, AVIF, ASS/SQL exports. These are roadmap items (see `11-roadmap.md`). The mission requires separating the engine from the format roadmap: all of these plug in as adapters without core changes.
