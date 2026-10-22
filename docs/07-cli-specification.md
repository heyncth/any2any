# CLI Specification — Any2Any

**Status:** all commands below are **PROPOSED for Any2Any**. None were executed against 2anything. Original CLI syntax observed only as documented examples (labels: VERIFIED-as-documented, NOT TESTED).

---

## 1. Original CLI surface (evidence, for parity mapping)

| Documented example | Source | Label |
|---|---|---|
| `2anything book.pdf --to m4b` | audiobook blog | VERIFIED documented / NOT TESTED |
| `2anything data.csv --to json` | CSV blog | VERIFIED documented / NOT TESTED |
| `2anything *.csv --to json` | CSV blog | VERIFIED documented / NOT TESTED |
| `2anything export.json --to csv` | CSV blog | VERIFIED documented / NOT TESTED |
| `2anything *.eml --to pdf` | EML blog | VERIFIED documented / NOT TESTED |
| `2anything archive.mbox --to pdf` | EML blog | VERIFIED documented / NOT TESTED |
| `2anything report.pdf --to docx` | PDF blog | VERIFIED documented / NOT TESTED |
| `2anything *.pdf --to docx` | PDF blog | VERIFIED documented / NOT TESTED |
| `2anything --formats mail.eml` | EML blog | VERIFIED documented / NOT TESTED |
| `2anything --licenses` | release 0.22.1 | VERIFIED documented / NOT TESTED |
| `--set voice Samantha` / `--set bitrate 96k` / `--set chapter_minutes 30` | audiobook blog | VERIFIED documented / NOT TESTED |
| `--set value_labels codes` / `--set sheet <name>` | release 0.22.1 | VERIFIED documented / NOT TESTED |

Parity choices: keep `--to` (familiar), keep `--set k v` (two-token form as documented), keep `--formats <file>` semantics (show targets for an input), keep `--licenses`.

## 2. Proposed command set

Binary name: `any2any` (subcommand style for clarity).

```
any2any convert <inputs...> --to <format> [options]
any2any formats [file] [--json]
any2any plan <input> --to <format> [--explain]      # alias: convert --dry-run
any2any doctor [--json]
any2any licenses [--json]
any2any history [--limit N] [--json] [--clear]
any2any config get|set|list <key> [value]
any2any engines list|install <name> [--yes]
any2any --version
any2any --help
```

### 2.1 `convert`

```
any2any convert INPUTS... --to FORMAT
  --out-dir DIR            # default: beside source (parity with 2a: output next to original)
  --force | --on-conflict ask|skip|overwrite|fail|keep-both
                           # default: skip (CLI non-interactive safety)
  --set KEY VALUE          # repeatable; validated against adapter option schema
  --direct-only            # refuse chains
  --explain                # print plan(s) before running
  --accept-lossy           # required when plan lossy and stdin is not a TTY;
                           # on TTY, prompt once per pair unless flag passed
  --trust content|extension   # resolve sniff mismatch (default: warn+fail on TTY
                           # if mismatch, error E_EXTENSION_MISMATCH in non-TTY
                           # unless flag given)
  --dry-run                # plan + validation only, no writes
  --jobs N                 # batch parallelism (default core)
  --json                   # machine-readable results on stdout
  --quiet / --verbose / --debug
  --no-history             # do not append to history store
  --timeout SECONDS        # per-step timeout override
```

**Input forms:** single path, multiple paths, globs (shell-expanded; unquoted globs are the user's shell's job — CLI does not re-glob to avoid surprises; document this).

**Examples (proposed):**

```bash
any2any convert photo.heic --to jpg --set quality 90
any2any convert *.csv --to json --on-conflict keep-both
any2any convert data.csv --to json --set delimiter semicolon --json
any2any convert run.fit --to gpx --explain
any2any convert report.pdf --to docx --out-dir ./converted --force
any2any convert slide.pptx --to md --dry-run --explain
```

### 2.2 `formats`

- `any2any formats` — dump full registry: id, category, extensions, read/write flags (≈ `2anything --formats` without file).
- `any2any formats mail.eml` — for that input: targets with `steps`, `est` score, `chain` flag, `requires`, `direct_only` availability. JSON mirrors fields.

### 2.3 `doctor`

Prints: Python version, Any2Any version, per-requirement status (found/version/OK-mismatch/missing/path), registry health (broken adapters), config path, history size, and `network: not used`. `--json` for scripts. Exit 0 if all *required-for-installed-features* satisfied, 4 if any missing for registered features.

### 2.4 `licenses`

Third-party notices: component, version, license id, source URL, whether bundled or external process, link to full text in share dir. Parity: `2anything --licenses` (VERIFIED documented).

### 2.5 `history` / `config` / `engines`

- history: list recent Results; `--clear` double-confirms on TTY (single `--yes` to skip).
- config: typed get/set for settings from `08-data-storage-and-privacy.md`.
- engines: `list` (same data as doctor), `install` performs consented download of pinned binary (checksum verified); prints URL before fetching; requires `--yes` for non-interactive.

## 3. Output format

**Human (default):** per-file lines `[ok] photo.png -> photo.webp (1.2s)`, warnings `[warn] W_LOSSY ...`, errors `[fail] E_PARSE data.json: line 42 ...`, final summary `done: 8 ok, 1 failed, 1 skipped`.

**`--json`:** single document to stdout (logs go to stderr):

```json
{
  "schema": "any2any.result/1",
  "command": "convert",
  "plan_summary": [{"source": "png", "target": "webp", "steps": 1, "score": 0.85}],
  "results": [
    {"item_id": "…", "source": "/in/photo.png", "output": "/in/photo.webp",
     "status": "success", "warnings": [{"code": "W_LOSSY"}],
     "duration_ms": 1210, "bytes_in": 4096, "bytes_out": 3100}
  ],
  "counts": {"success": 1, "failed": 0, "skipped": 0, "cancelled": 0},
  "exit_code": 0
}
```

Progress in JSON mode: optional `--progress events` writes NDJSON events to stderr.

## 4. Exit codes

| Code | Meaning |
|---|---|
| 0 | all items success (or dry-run success) |
| 1 | usage error (bad flags/args) — `E_USAGE` |
| 2 | partial failure (≥1 success, ≥1 failed) |
| 3 | total failure (all items failed / fatal `E_PLAN_FAILED`) |
| 4 | missing engine / requirement — `E_MISSING_ENGINE` |
| 5 | cancelled (SIGINT/SIGTERM) — `E_CANCELLED` |
| 6 | conflict refused under policy — `E_CONFLICT_OUTPUT` |
| 7 | unsupported pair/direction/input when *single* target requested and *no* files could proceed — `E_UNSUPPORTED_*` (multi-file mix of unsupported+ok → 2) |

Rationale: scripts need to distinguish "nothing happened because unsupported" (7) from "dependency missing, install first" (4).

## 5. Batch behavior

- All inputs validated first (two-phase: plan all → report → execute all unless `--fail-fast`).
- Default continues past per-file errors; `--fail-fast` stops scheduling new items after first failure (running ones finish or cancel per `--fail-fast-mode stop|cancel-running`).
- Exit code aggregates worst severity in order: 5 > 4 > 6 > 3 > 2 > 0 (1 preempts all, parse time).
- Deterministic ordering of JSON results = input order.

## 6. Automation recipes

```bash
# CI: convert all csv in data/ to json, fail if any issue
any2any convert data/*.csv --to json --on-conflict overwrite --json > report.json
case $? in 0) ;; *) exit 1;; esac

# Nightly audit: what would convert to what
any2any formats --json | jq '.formats[] | select(.category=="geo")'

# Safe batch with keep-both and no history
any2any convert inbox/*.eml --to pdf --on-conflict keep-both --no-history

# Environment pinning
any2any config set default.conflict overwrite
export ANY2ANY_OFFLINE=1   # hard-disable even optional downloads (default already off)
```

## 7. Conventions and non-goals

- Unicode paths: full support; JSON output always UTF-8.
- `--` terminator supported for paths starting with `-`.
- No global daemon; each invocation is independent.
- No shell interpolation inside Any2Any: external tools receive argv arrays (FR-8.1).
- Not mirroring every unknown 2anything flag; only documented ones are treated as parity targets.
