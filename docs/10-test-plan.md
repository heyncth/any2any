# Test Plan — Any2Any

No original-application tests have been executed (see `research/test-results.md` — all original rows NOT TESTED). Everything below is the proposed automated/manual suite for Any2Any, converting those blocked tests into acceptance tests.

---

## 1. Strategy

| Layer | Scope | Tools | When |
|---|---|---|---|
| Unit | planner math, registry validation, detection, safety guards, option validation | pytest | every PR |
| Contract | every adapter × 8 contract tests (`06-conversion-engine.md` §3) | pytest parametrized | every PR |
| Integration | CLI golden runs (stdout/exit codes/JSON schema) | pytest + subprocess | every PR |
| GUI smoke | load, plan display, convert, cancel, history | pytest-qt | every PR (headless CI) |
| Security | traversal, bombs, injection property tests | pytest | every PR |
| Privacy | socket-trap suite PRIV-01..08 | pytest | every PR |
| Fuzz | malformed structured inputs | hypothesis | nightly |
| Performance | baselines NFR-3 | pytest-benchmark | nightly / release |
| E2E manual | a11y walkthrough, offline firewall session, engine installer UX | checklist §6 | per milestone |

## 2. Fixtures

Stored `tests/fixtures/<format>/` tiny, synthetic, license-clean:

- `image/`: valid png/jpg/webp/tiff/bmp/ico; corrupt.jpg (truncated); bomb.png (declared huge dimensions, small file); 0-byte.png; extension-lie.png (JPEG bytes); unicode-名前.png; 4K.png for perf.
- `data/`: good.csv, semicolon-eu.csv, utf16-bom.csv (expect fallback/fail per spec: we support UTF-8+1252 parity → utf16 = E_PARSE with hint), ragged.csv, dup-headers.csv, empty.csv, good.json, bad.json (line 42), jsonl, nested.json, good.yaml, yaml-bomb.yml, simple.xml, weird-headers.csv.
- `doc/`: note.md, page.html, plain.txt, utf8-emoji.md.
- `geo/`: track.gpx, route.kml, points.geojson, empty.gpx, malformed.gpx.
- `sub/`: a.srt, a.vtt, offset.srt, bad.srt.
- `qr/`: payloads: url.txt, vcard.txt, long.txt.
- `zip/` (P2): safe.zip, slip.zip (../evil), bomb.zip, deep-nesting.zip.
- Large-file generator script (not stored): 1 GB csv via `make big` (skipped in CI unless label `slow`).

Golden outputs: for lossless pairs store expected bytes/hashes; for lossy store perceptual bounds (e.g., PSNR threshold) + metadata assertions.

## 3. Edge-case matrix (mission §6 → acceptance tests)

| ID | Case | Expected (Any2Any) | Priority |
|---|---|---|---|
| EC-01 | valid input | output correct, next to source (default), history row success | P0 |
| EC-02 | corrupted input | E_PARSE/E_ENGINE_FAILED; no residue; source unchanged | P0 |
| EC-03 | unsupported extension | E_UNSUPPORTED_INPUT or sniff fallback message | P0 |
| EC-04 | extension ≠ content | mismatch warning path; user choice honored; CLI non-TTY → E_EXTENSION_MISMATCH | P0 |
| EC-05 | empty file | E_EMPTY_FILE | P0 |
| EC-06 | large file | succeeds while memory allows; W_LARGE_FILE_MEMORY warns; controlled E_MEMORY/E_DISK_FULL otherwise | P1 (perf tier) |
| EC-07 | unicode filename | output keeps basename, UTF-8 safe on all 3 OSes | P0 |
| EC-08 | existing output | policy honored (GUI ask/keep-both, CLI skip/fail/force); never silent overwrite | P0 |
| EC-09 | read-only input dir | works if out-dir elsewhere; E_PERMISSION if writing beside source | P0 |
| EC-10 | missing out dir | E_PERMISSION/E_USAGE with hint; no auto-mkdir unless `--out-dir` given? **Decision: auto-create `--out-dir` if parent exists** (document) | P0 |
| EC-11 | cancel | E_CANCELLED; temps gone; partial outputs of cancelled item gone; siblings kept | P0 |
| EC-12 | mixed batch | per-item statuses; exit 2; JSON counts | P0 |
| EC-13 | repeated conversion | second run follows conflict policy deterministically | P0 |
| EC-14 | lossy conversion | W_LOSSY + ack policy; quality option respected (verify measured quality) | P0 |
| EC-15 | offline | full suite passes network-blocked; PRIV-01/02 | P0 |
| EC-16 | missing engine | E_MISSING_ENGINE + doctor + installer path (or manual hint) | P0 for adapters with deps |
| EC-17 | insufficient disk | E_DISK_FULL; part file removed; no corrupt final | P0 (simulate via small tmpfs/quotas) |
| EC-18 | malformed structured data | E_PARSE with position; process survives | P0 |
| EC-19 | open-password PDF | E_INPUT_PROTECTED (specialize taxonomy in P1 when PDF lands) | P1 |
| EC-20 | encrypted office files | mapped clear error, not stack trace | P1 |
| EC-21 | keyboard-only a11y | A11Y-01 checklist passes | P0 |
| EC-22 | double-run + history | both attempts visible or updated per design (decision: append both) | P0 |

## 4. Conversion compatibility matrix (P0 excerpt)

Legend: ✔ must pass golden test; ⚠ semantic test (structure/content assertions, not byte-equal); ✖ not supported (must error correctly).

| src\tgt | png | jpeg | webp | tiff | bmp | ico | svg-raster | csv | json | jsonl | yaml | txt | md | html | srt | vtt | gpx | kml | geojson | qr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| png | — | ✔ | ✔ | ✔ | ✔ | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ |
| jpeg | ✔ | — | ✔ | ✔ | ✔ | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ |
| svg | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | — | ✖ | ✖ | ✖ | ✖ | ⚠(text extract P2) | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ |
| csv | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | — | ⚠ | ✔ | ⚠ | ⚠ | ⚠ | ⚠(P1) | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ |
| json | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠ | — | ✔ | ✔ | ⚠ | ⚠ | ⚠ | ✖ | ✖ | ✖ | ✖ | ⚠(geojson→) | ✖ |
| md | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠(P1 tables) | ⚠(P1) | ✖ | ⚠ | ✔ | — | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ |
| html | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠(P1) | ⚠(P1) | ✖ | ⚠ | ✔ | ✔ | — | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ |
| txt | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠(single col) | ⚠ | ⚠ | ✔ | — | ✔ | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ | ✔(payload) |
| srt | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠(P1) | ✖ | ⚠ | ✔ | ✔ | ⚠(P1) | — | ✔ | ✖ | ✖ | ✖ | ✖ |
| vtt | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠ | ✖ | ⚠ | ✔ | ✔ | ⚠ | ✔ | — | ✖ | ✖ | ✖ | ✖ |
| gpx | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠(P1) | ✔ | ✖ | ✔ | ⚠ | ✖ | ✖ | ✖ | ✖ | — | ✔ | ✔ | ✖ |
| kml | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠(P1) | ✔ | ✖ | ✔ | ⚠ | ✖ | ✖ | ✖ | ✖ | ✔ | — | ✔ | ✖ |
| geojson | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ⚠(P1) | ✔ | ✖ | ✔ | ⚠ | ✖ | ✖ | ✖ | ✖ | ✔ | ✔ | — | ✖ |

Full matrix including P1+ formats lives in `02-feature-inventory.md`; this table defines the P0 release gate. Chained rows (e.g., txt→pdf at P1) must declare `W_CHAINED` + plan display.

## 5. Acceptance tests mapped to features

- FR-1 planning: planner unit tests + `formats`/`plan --explain` golden outputs.
- FR-2 files: EC-01..10, PRIV-07.
- FR-3 jobs: EC-11,12,13 + parallelism stress (100-file batch).
- FR-4 CLI: golden suite covering every flag in `07-cli-specification.md`, exit codes 0–7 each provoked at least once.
- FR-5 GUI: pytest-qt scripts per flow in `04-user-flows.md`.
- FR-6 engines: doctor JSON contract; installer consent refusal test; checksum-corrupt download rejected.
- FR-7/8 privacy/security: PRIV-*, T-SEC-*.
- NFR-3 perf: benchmark jobs; regression gate ±20%.

## 6. Manual E2E checklists (per milestone release)

1. **Offline session (NFR-1/2):** firewall-denied machine/VM → install → convert P0 set → history → settings → close; confirm no network errors anywhere; packet capture shows zero app-originated connections.
2. **A11Y walkthrough (EC-21):** keyboard only through S1–S5; screen reader spot-check (VoiceOver/NVDA) on main window.
3. **Missing-engine recovery (EC-16):** hide ffmpeg → convert mp3 → see S5 → install → convert succeeds; corrupt the checksum → rejected.
4. **Crash residue:** kill -9 during batch → relaunch → sweep removes temps; outputs either absent or complete (atomicity).
5. **Three-OS smoke:** same fixture set on Windows/macOS/Linux; unicode names; path lengths (Windows 260-char guard).

## 7. Untested assumptions (carry into 13-open-questions.md)

- Exact fidelity of md→html on exotic Markdown (GFM tables, footnotes): decided by chosen parser; tests added when parser pinned.
- Pillow EXIF transpose behavior on HEIC once pillow-heif lands (P1).
- GUI rendering under high-DPI mixed-monitor setups (manual check M3).
