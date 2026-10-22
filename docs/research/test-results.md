# Test Results

**Environment for original product testing:** Windows 11 host, no Apple Silicon Mac, no macOS virtualization, application binary not downloaded (clean-room rules: no extraction of proprietary resources, no license bypass).  
**Date:** 2026-10-22

## Summary

| Category | Original (2anything) | Any2Any proposed |
|---|---|---|
| Behavioral tests executed | 0 | 0 (implementation not started) |
| Tests blocked by access | 22 | — |
| Tests converted to acceptance criteria | 22 | see `docs/10-test-plan.md` |

**No test in this document has been executed against the original application.** Every row is either NOT TESTED (blocked) or a proposed acceptance test for Any2Any. Nothing below may be reported as a pass for 2anything.

## Part A — Tests designed for 2anything, blocked (all NOT TESTED)

Test IDs map to `docs/10-test-plan.md` edge-case matrix (EC-01 … EC-16).

| ID | Preconditions | Steps | Expected (hypothesized from public docs) | Observed | Status |
|---|---|---|---|---|---|
| EC-01 | Valid PNG sample | Drop PNG, select JPG, Convert | JPG created next to source, same basename | not observed | NOT TESTED (no macOS) |
| EC-02 | Corrupted JPEG (random bytes, .jpg ext) | Convert to PNG | Error message, no partial output left, source untouched | not observed | NOT TESTED |
| EC-03 | File with unsupported extension (e.g., `.xyz`) | Drop file | Format list limited or "unsupported" message | not observed | NOT TESTED |
| EC-04 | CSV content with `.png` extension | Convert to JSON | Content-based detection warns or errors clearly (behavior UNKNOWN) | not observed | NOT TESTED |
| EC-05 | 0-byte file | Convert | Clear empty-file error | not observed | NOT TESTED |
| EC-06 | Large file (1 GB CSV) | Convert to JSON | Succeeds if RAM allows (blog documents RAM constraint); memory error otherwise | not observed | NOT TESTED |
| EC-07 | Unicode filename `日本語-файл-café.png` | Convert | Output keeps basename, no mojibake | not observed | NOT TESTED |
| EC-08 | Duplicate target name (output exists) | Convert again | Behavior UNKNOWN: overwrite, skip, or rename — not publicly documented | not observed | NOT TESTED (UNKNOWN) |
| EC-09 | Read-only input directory | Convert to same dir | Error about write permission; source preserved | not observed | NOT TESTED |
| EC-10 | Missing output directory | CLI with output dir flag | Behavior UNKNOWN (output-next-to-source default; flag existence UNKNOWN) | not observed | NOT TESTED (UNKNOWN) |
| EC-11 | Cancel mid-conversion (GUI Cancel or Ctrl-C CLI) | Start long TTS, cancel | Temp files removed; partial output removed; source intact | not observed | NOT TESTED |
| EC-12 | Batch with 1 valid + 1 invalid file | `2anything * --to png` | Valid file converts; invalid reported; exit code nonzero | not observed | NOT TESTED |
| EC-13 | Repeated identical conversion | Run twice | Same output or documented conflict behavior (see EC-08) | not observed | NOT TESTED |
| EC-14 | Lossy conversion (PNG→JPG quality 85) | Convert, inspect | Quality setting honored; user informed conversion is lossy (warning presence UNKNOWN) | not observed | NOT TESTED |
| EC-15 | Offline (network disabled after install) | Convert | Works; only activation needs network (per privacy policy) | not observed | NOT TESTED |
| EC-16 | Missing external dependency (ffmpeg removed) | Audio conversion | Error naming missing tool (behavior UNKNOWN — app bundles tools, so hard to simulate) | not observed | NOT TESTED |
| EC-17 | Insufficient disk space for output | Convert large file | Error; temp cleaned; no corrupt output file | not observed | NOT TESTED |
| EC-18 | Malformed JSON / malformed CSV | Convert to counterpart | Parse error with line number (quality UNKNOWN) | not observed | NOT TESTED |
| EC-19 | Password-protected PDF (open-password) | PDF→DOCX | Documented: message saying password-protected; no conversion — VERIFIED as documented behavior, not executed | not executed | NOT TESTED (documented claim) |
| EC-20 | Password-protected Office/OpenDocument file | Convert | Behavior UNKNOWN | not observed | NOT TESTED (UNKNOWN) |
| EC-21 | GUI keyboard-only navigation | Tab through all controls | All controls reachable; Convert reachable without mouse (a11y UNKNOWN) | not observed | NOT TESTED (UNKNOWN) |
| EC-22 | Existing output + history state | Convert same file twice, view history | History shows both or updated row (behavior UNKNOWN) | not observed | NOT TESTED (UNKNOWN) |

## Part B — Documented claims not executed (evidence type: written primary source)

These are VERIFIED as *published claims*, NOT TESTED as *behaviors*:

1. "The conversion runs entirely on your Mac and makes no network calls" (CSV blog) — VERIFIED claim / NOT TESTED behavior.
2. Multi-step route with temp intermediate deleted even on failure (EML blog) — VERIFIED claim / NOT TESTED behavior.
3. Up to 3 fallback routes when a step fails (EML blog) — VERIFIED claim / NOT TESTED behavior.
4. Automatic OCR only on image/garbled PDF pages (PDF-to-Word blog) — VERIFIED claim / NOT TESTED behavior.
5. HEIC keeps Display P3, orientation, EXIF, GPS (release 0.22.1) — VERIFIED claim / NOT TESTED behavior.
6. No GPL/AGPL in-process; ffmpeg/pandoc pinned with checksums (release 0.22.1) — VERIFIED claim / NOT TESTED (binary not inspected).

## Part C — Any2Any tests actually executed

None. No implementation exists at the time of writing. Rows will be added as milestones land, with environment, evidence (log path or screenshot), and pass/fail.

| Test ID | Milestone | Status |
|---|---|---|
| (none yet) | M1+ | PENDING IMPLEMENTATION |

## Part D — Environment notes for future runs

- Original: requires macOS 14+ (assumed; exact minimum OS UNKNOWN) on Apple Silicon; install via signed/notarized .dmg from GitHub releases; 7-day trial, no key required for trial (activation flow for trial UNKNOWN).
- Any2Any targets: Windows 10/11, macOS 13+, Ubuntu 22.04+/Fedora (to be confirmed in M5 packaging); offline tests run with network namespace disabled or firewall rule blocking the binary.
