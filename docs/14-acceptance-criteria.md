# Acceptance Criteria — Any2Any

Testable statements only. Each criterion: ID, requirement, verification method. "MVP" = after M5. Labels for original-app comparisons: none — these gate Any2Any only.

---

## 0. Quality gate for this documentation package (M0 exit)

| ID | Criterion | Verification |
|---|---|---|
| G-01 | All 17 requested files exist under `docs/` | file listing |
| G-02 | Every major product claim carries VERIFIED/INFERRED/UNKNOWN/NOT TESTED | label grep across docs; manual read |
| G-03 | No marketing claim of 2anything presented as tested behavior | read `00`, `02`, `research/*` |
| G-04 | No unsupported conversion direction asserted as supported | cross-check `02` vs `10` matrices |
| G-05 | Original internals not invented as fact; inferences labeled | scan `05` ADRs ("informed by observable") |
| G-06 | Every proposed feature has acceptance criteria | `01`+`10`+this file coverage |
| G-07 | MVP scope achievable by one developer | roadmap effort sanity review (M1–M3 feature cap) |
| G-08 | No mandatory AI API or hosted service anywhere in MVP | search for api-key/network requirements in MVP items → none |
| G-09 | Privacy claims list concrete tests | `08` §8 PRIV-01..08 |
| G-10 | Third-party licenses documented with obligations | `09` |
| G-11 | Roadmap excludes advanced features from MVP | `11` exclusions per milestone |
| G-12 | Executive summary links to all other docs | link check in `00` §7 |

## 1. Milestone gates

### M1 — skeleton

- AC-1.1: `pip install -e .` succeeds on Win/macOS/Linux CI.
- AC-1.2: registry loads with ≥1 dummy adapter; invalid adapter self-disables with logged error.
- AC-1.3: temp job dir created 0700 and removed after success/failure paths (unit).
- AC-1.4: history write+read round-trip; settings load defaults on missing file.
- AC-1.5: license-gate CI job fails if GPL entry appears in core requirements lock.
- AC-1.6: `any2any doctor`, `formats`, `config` exit 0 with JSON variants schema-valid.

### M2 — planner + P0 adapters

- AC-2.1: P0 compatibility matrix (`10` §4) all ✔/⚠ cases pass; all ✖ cases raise correct taxonomy codes.
- AC-2.2: planner: direct score, multi-step product search, K=3 alternatives, direct-only mode — unit tested incl. cycle graph.
- AC-2.3: EC-01,02,03,04,05,07,08,13,14,18 pass.
- AC-2.4: source checksum unchanged for every adapter (contract).
- AC-2.5: conflict policy CLI defaults: skip (warn), `--force` overwrites, `--on-conflict fail` → exit 6.
- AC-2.6: lossy pairs emit W_LOSSY; non-TTY convert without `--accept-lossy` fails with guidance.
- AC-2.7: PRIV-01,04,06,07 green.
- AC-2.8: golden JSON output schema matches `07` §3 example shape.

### M3 — GUI + CLI polish

- AC-3.1: pytest-qt covers flows 1,2,4,8,9 headless in CI.
- AC-3.2: chain plan visible before convert; `--explain`/`--dry-run` parity output.
- AC-3.3: EC-21 keyboard walkthrough checklist signed off (manual, recorded in release notes).
- AC-3.4: all CLI exit codes 0–7 exercised by automated tests.
- AC-3.5: settings changes take effect for next job without restart.
- AC-3.6: NFR-8: CLI `--help` < 500 ms; GUI cold start < 2.5 s on reference machine (recorded numbers).

### M4 — jobs + media/doc hubs + engine manager

- AC-4.1: EC-11 cancel: no temp residue, no part files, siblings kept — automated.
- AC-4.2: EC-12 mixed batch exit 2 + JSON counts.
- AC-4.3: EC-16: missing ffmpeg → E_MISSING_ENGINE; installer refuses without consent; checksum mismatch rejected (simulated).
- AC-4.4: chain failure test: step 2 fails → intermediate deleted, E_PLAN_FAILED includes per-route reasons (≤3 routes attempted).
- AC-4.5: ffmpeg adapter passes contract suite with pinned binary; pandoc likewise; licenses command lists both with GPL texts present in bundle.
- AC-4.6: EML→PDF (or MD→PDF) chain documented in feature inventory updated with implemented tag.
- AC-4.7: PRIV-03 green (network only in installer path).

### M5 — security, packaging, MVP release

- AC-5.1: T-SEC-01..08 pass.
- AC-5.2: offline E2E checklist (`10` §6.1) executed on 3 OS, artifacts attached to release.
- AC-5.3: crash kill-test: relaunch → sweep clean; no corrupt outputs (atomicity).
- AC-5.4: installable artifacts: signed where platform requires (macOS notarized, Windows sig) or explicitly documented unsigned status (risk accepted, noted).
- AC-5.5: SBOM published; `any2any licenses` complete vs SBOM diff = empty.
- AC-5.6: NFR-3 perf baselines recorded and within thresholds.
- AC-5.7: fuzz nightly 24h zero crashes on structured parsers (or all findings fixed/wontfix with notes).
- AC-5.8: EC-17 disk-full simulated pass.

### M6 — expanded formats

- AC-6.1: each new adapter: contract suite + fixtures + inventory row marked implemented with version.
- AC-6.2: no core module changes required by any M6 adapter (diff review: adapters/ only + registry lists).
- AC-6.3: parity spot-check: for formats also documented by original (PARQUET etc.), our matrix explicitly marks directions + limits; no claim of identity with original results.

## 2. Feature-level acceptance (examples)

| Feature | Acceptance criteria |
|---|---|
| QR generation | url.txt → qr.png decodable by independent decoder (e.g., zxing/pyzbar) round-trip in test; SVG variant parses as XML |
| SRT→VTT | timing values converted (`,`→`.`), cue IDs dropped per WebVTT spec; golden diff |
| CSV→JSON | blog-documented semantics: values as strings, header repair, ragged padding — test cases mirror `02`/evidence |
| GPX→KML | track points preserved within float tolerance; file valid against basic XSD check |
| History | 1000 conversions → query < 50ms; clear works; redaction flag respected |
| Planner transparency | every GUI convert of a 2-step plan shows chip; every CLI run prints or JSON-contains plan steps |

## 3. Release-level criteria (any public release)

- R-1: README states exact format matrix (generated from registry — docs/registry drift test).
- R-2: CONTRIBUTING explains adding an adapter (per `06` §9) with template.
- R-3: Security policy + private disclosure contact.
- R-4: All G-01..G-12 still hold; evidence log updated with any new external claims.
- R-5: No 2anything trademarks/assets/text in tree (grep checklist + eyeball).
