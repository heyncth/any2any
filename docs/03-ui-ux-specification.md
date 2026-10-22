# UI/UX Specification — Any2Any

**Evidence:** 2anything homepage mockup (VERIFIED elements: drop zone, format select, Advanced Settings, Convert, history table), blog texts (time estimate, menubar references), PDF-to-Word/EML steps (VERIFIED documented flow: drop → choose format → Convert → output next to source).  
**Design status:** UI layout and states below are Any2Any's own design; where an element maps to an observed 2anything element, it is marked `[2a:VERIFIED]`.

---

## 1. Design principles

1. **One primary action** per state: Convert (when files loaded) or "Load files" (when empty).
2. **Format follows selection:** output list always derived from selected inputs; unavailable directions disabled with reason, never hidden silently `[2a:VERIFIED: "Select a file first"]`.
3. **Show the plan:** if chained, show "via HTML" style badges and estimated fidelity before the run starts.
4. **Warn before loss:** lossy conversion warning before first convert of a format pair; remember per-pair acknowledgment.
5. **Never destroy:** no source writes; no overwrite without policy decision.
6. **Honest states:** every failure has an error code, plain-language title, detail, and (if engine-related) fix hint.
7. **Keyboard first, mouse friendly, screen-reader labelled** (NFR-6).
8. **Local by design:** no network-triggered UI (no remote images, no update nags by default).

## 2. Screen inventory

### S1 — Main window (Convert)

| Element | Behavior | Label |
|---|---|---|
| Drop zone (center) | Drag files/folders in; click opens file picker; accepts multiple; shows count after load | `[2a:VERIFIED]` |
| Input file list | Rows: icon, name, size, detected type, per-row status; remove-row button; "Clear all" | INFERRED extension of mockup |
| Output format combo | Options = union of supported targets for selection; group by category; disabled options show tooltip reason (e.g., "needs ffmpeg: not installed") | `[2a:VERIFIED]` |
| Advanced settings disclosure | Collapsible panel; options filtered to active format pair (e.g., JPEG quality only when target JPEG) | `[2a:VERIFIED]` |
| Convert button | Enabled only when files + valid target; shows plan badge if chain | `[2a:VERIFIED]` |
| Progress area | Per-file bar, overall count `3/10`, step text `via HTML (2/2)`, ETA when known, Cancel button | ETA `[2a:VERIFIED]`; rest Any2Any |
| Result summary | Successes/failures counts; "Open output folder"; "Show details" (per-file errors) | Any2Any |
| History table | Columns: File, Conversion, Status, Date; double-click row reveals details; clear-history action | `[2a:VERIFIED]` |

**States:** `EMPTY` → `LOADED` → `PLAN_READY` → `RUNNING` → `DONE | DONE_WITH_ERRORS | CANCELLED`.  
Transitions guarded: format change re-evaluates plan; file removal during run blocked (rows locked).

### S2 — Advanced settings (per-pair option schema)

Rendered dynamically from adapter option declarations (type, default, range):

| Option (examples) | Type | Default | Evidence |
|---|---|---|---|
| quality (JPEG/WebP/AVIF) | int 1–100 | 85 | 2a default 85 VERIFIED (HEIC blog) |
| strip_metadata | bool | false | 2a keep EXIF default VERIFIED (HEIC blog) |
| delimiter (CSV out) | enum auto/comma/semicolon/tab/pipe | auto | 2a auto-detect VERIFIED (CSV blog) |
| sheet (Excel) | string/enum | all | 2a `--set sheet` VERIFIED (release) |
| value_labels (SPSS/Stata/SAS) | bool | true | 2a default on VERIFIED (release) |
| block_remote_content (email) | bool | true | 2a default on VERIFIED (release) |
| direct_only | bool | false | Any2Any addition (chain transparency) |

### S3 — Settings dialog

Categories: General (default output location: beside source | chosen folder; overwrite policy: ask/skip/overwrite; language), Privacy (update check: OFF default; clear history on exit: off), Engines (list detected engines, versions, path; "Verify checksums"; "Install optional engine…" opens S5), Advanced (parallelism, temp directory, log level).

### S4 — History detail modal

Shows: source path, target path, plan (steps + scores), options used, duration, warnings, error (if any), log excerpt. Action: Re-run with same options.

### S5 — Optional engine installer

Triggered by `E_MISSING_ENGINE`. Lists: engine name, version, size, license, source URL, checksum. Buttons: "Download and install" (explicit consent, progress) / "I'll install myself" (shows command for package manager). After download: verify checksum → register adapter → re-check plan. All network activity happens only here, never during conversion.

### S6 — First-run / About

About dialog shows version, OSS license, "Licences" action opening `--licenses` equivalent view (third-party notices). No account, no key field.

## 3. Error and warning states (UI presentation)

| Code | UI treatment | Example copy |
|---|---|---|
| E_UNSUPPORTED_PAIR | Blocking, lists nearest supported targets | "Cannot convert FIT to DOCX. Supported FIT targets: GPX, KML, GeoJSON, CSV." |
| E_UNSUPPORTED_DIRECTION | Blocking with explanation | "HEIC is read-only in this build." (when applicable) |
| E_MISSING_ENGINE | Blocking + S5 offer | "Video conversion needs ffmpeg (pinned 7.x). Install or let Any2Any download it." |
| E_CONFLICT_OUTPUT | Choice dialog | "report.pdf exists. Overwrite / Keep both (report (1).pdf) / Skip" (default Keep both in GUI) |
| E_PARSE | Row error + details | "JSON parse error at line 42: expected ','" |
| E_EMPTY_FILE | Row error | "File is empty (0 bytes)." |
| E_EXTENSION_MISMATCH | Warning, user chooses | "report.png contains JPEG data. Convert as JPEG?" |
| E_LOSSY | Warning once per pair | "JPEG is lossy; quality 85 will discard some detail." |
| E_CANCELLED | Neutral status | "Cancelled. Temporary files removed." |
| E_IO / E_PERMISSION | Row error + hint | "Cannot write to read-only folder: choose another output location." |

## 4. Accessibility

- Full tab order: drop zone → file list → format → advanced → convert → results → history.
- All icon buttons have accessible names; status conveyed by text + icon (not color alone).
- Progress: `role="progressbar"` with aria-valuenow; failures announced via live region once.
- Contrast ≥ 4.5:1; respects system reduced-motion; respects system font scaling.
- Acceptance: keyboard-only walkthrough of S1–S5 completes all primary tasks (test A11Y-01 in `10-test-plan.md`).

## 5. Responsive / platform behavior

- Desktop app; min window 900×600; layout adapts to 1280×800 reference.
- macOS: optional menu-bar quick-drop (parity with 2a menubar VERIFIED) — P1.
- Windows/Linux: standard window + system tray not required in MVP.
- Dark mode follows system palette.

## 6. Loading and empty states

- EMPTY: drop zone focused by default; recent-history link.
- Long plans: spinner with plan text; no fake progress (percent only when step count known).
- History: paginated after 500 rows (local SQLite/JSON performance).

## 7. Explicitly not copied

No 2anything logo, color scheme, screenshots, or marketing strings. Sample history rows in mockup (PNG→ICO etc.) are treated as evidence of *feature types*, not content to reuse.
