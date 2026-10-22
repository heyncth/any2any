# Competitive Analysis — Any2Any

No superiority claims without evidence. Labels: VERIFIED = observed in primary source; INFERRED; UNKNOWN.

---

## 1. Alternatives considered

### 1.1 2anything (direct inspiration)

| Aspect | Observation | Label |
|---|---|---|
| Positioning | macOS local-first converter, $39 once, wide format set, GUI+CLI | VERIFIED (site) |
| Strengths | very broad format coverage incl. science stats + OCR/STT/TTS; documented fidelity-engineering (Word→PDF scoring, chunked TTS); honest policy pages; changelog-grade blog | VERIFIED (docs) |
| Weaknesses (relative to our goals) | paid license; license-key network validation; macOS/Apple Silicon only; trial conversion restrictions UNKNOWN; chain transparency to user INFERRED low (blog says user need not know); TTS options CLI-only; no chapter cancel (documented) | VERIFIED/INFERRED mix |
| Evidence quality | unusually good public documentation for a closed app | VERIFIED |

### 1.2 Online converters (CloudConvert, Convertio, and similar)

- Strength: zero install, huge format lists. UNKNOWN specifics per product (not audited).
- Weakness vs Any2Any: requires upload of file content to third party — directly conflicts with privacy requirement; network dependency; usage limits/pricing common (INFERRED from market pattern, not audited).
- We do not claim they are unsafe; we claim a different architecture (local vs uploaded) which is objectively different.

### 1.3 FFmpeg / ImageMagick / pandoc (raw tools)

- Strengths: maximal control, ubiquitous, permissive-ish licenses (ffmpeg LGPL config, IM Apache-2.0, pandoc GPL).
- Weaknesses: steep learning, per-tool flag knowledge, no unified history/plan/progress (VERIFIED facts about these tools' nature; INFERRED user friction).
- Any2Any relationship: wraps such engines; not a replacement for power users who want raw flags.

### 1.4 File Converter (Windows app), per-utility GUIs

- Existence of desktop single-purpose converters: common knowledge, not audited here (UNKNOWN details). Do not assert rankings.

### 1.5 LibreOffice headless, pandoc CLI, Ghostscript

- Strengths: mature document pipelines. Weaknesses: footprint, invocation complexity. Any2Any may invoke LibreOffice as optional engine (parity: 2anything `pdf_engine` VERIFIED).

## 2. Differentiators (Any2Any, proposed — each testable)

| # | Differentiator | Mechanism | Test |
|---|---|---|---|
| D1 | Fully free + OSS (vs 2a paid) | MIT, no key | repo license, no activation code path |
| D2 | Zero network by default (stricter than 2a: no license/update traffic) | ADR-009, PRIV-* | offline E2E |
| D3 | Cross-platform core (2a = macOS-only) | Python/Qt | builds ×3 OS |
| D4 | Transparent conversion plans with visible chains + scores | planner + UI chips | flow 4 tests |
| D5 | Unified engine for GUI and CLI (no feature drift) | shared facade | CLI/GUI parity checklist |
| D6 | Honest format matrix with direction rules + confidence labels | docs + registry errors | EC-03/unsupported messaging |
| D7 | First-class safety defaults (no silent overwrite, atomic outputs, temp hygiene) | conflict policies, part+rename | EC-08/11/17 |
| D8 | Adapter plugins: formats ship decoupled from releases | entry points | M2 acceptance |

## 3. Honest weaknesses (vs alternatives)

- Format breadth at MVP is far below 2anything (mission deliberately caps P0). Until M6+, 2a covers more.
- No OCR/STT/TTS in near term (2a has them today — VERIFIED marketing).
- No mature installer/signing yet; PyInstaller footprint larger than a native Swift app (INFERRED).
- Fidelity of document conversions initially depends on pandoc-class tools — same as many competitors, but we must earn documented parity.
- No track record, no user base, no support SLA.

## 4. Positioning statement (draft)

For privacy-sensitive individuals and teams who need to convert files between formats on their own machines, **Any2Any** is a free open-source local-first converter that, unlike hosted services, never uploads files and, unlike paid desktop tools, requires no license — with a transparent conversion planner and one engine behind both GUI and CLI.

Evidence boundary: claims about hosted services' data handling rest on the structural fact of upload (definitional), not on audits of any specific provider.
