# Data Storage, Privacy & Offline Guarantees — Any2Any

---

## 1. Storage locations

Platform dirs (respect XDG on Linux, app-support conventions elsewhere):

| Data | Location | Format | Retention |
|---|---|---|---|
| Settings | `<config>/any2any/config.toml` | TOML | until user deletes |
| History | `<state>/any2any/history.db` | SQLite (table `results`, schema mirrors Result model + `schema_version`) | until cleared; cap: prune oldest beyond 50,000 rows |
| Logs | `<state>/any2any/logs/any2any.log` (rotating, 5 MB × 3) | text, paths truncated to basename by default | 14 days |
| Engine binaries | `<data>/any2any/engines/<name>/<version>/` | binary + `manifest.json` (url, sha256, license, version) | persistent until uninstalled |
| Model files (P2+: whisper etc.) | `<data>/any2any/models/` | model blobs + manifest | explicit delete; never auto-fetched |
| Temp jobs | OS temp `any2any-<uid>/` | files | deleted at job end; startup sweep >24h |
| Desktop entries/icons | platform standard | — | package lifetime |

Windows: `%APPDATA%\any2any\config.toml`, `%LOCALAPPDATA%\any2any\…`.  
macOS: `~/Library/Application Support/any2any/…`, config in `~/Library/Preferences` or same tree (choose one in M1 and document).

**Invariants:** never store file *contents* anywhere except outputs and temps; history stores paths, basenames optional flag `history.store_full_paths` (default true, can be false for privacy-conscious users → store basenames only).

## 2. Configuration model (defaults)

```toml
[output]
default_mode = "beside_source"   # or: fixed_dir
fixed_dir = ""
conflict = "ask"                 # GUI dialog; CLI flag overrides; non-TTY CLI defaults skip

[privacy]
telemetry = false                # hard-wired false; no code path exists
update_check = false             # no update checker in MVP at all (ADR-009)
history_full_paths = true
history_enabled = true

[conversion]
jobs = 0                         # 0 = auto min(4, cpus)
direct_only = false
accept_lossy_pairs = []          # e.g. ["png->jpeg"]
trust_content = "ask"            # ask|content|extension

[engine.ffmpeg]
mode = "auto"                    # auto|system|bundled|off
path = ""
```

## 3. Networking policy

| Scenario | Allowed by default? | Disclosure |
|---|---|---|
| File conversion (any adapter) | **Never** | contract test forbids sockets |
| Telemetry/analytics/crash upload | **Never** | no code path; policy statement in README |
| Update check | **No** (feature absent in MVP) | if ever added: opt-in, version-only payload, documented in privacy doc |
| Engine/model download (`engines install`) | Only after explicit user action + consent dialog/`--yes` + shown URL + checksum | S5 UI / CLI prints URL first |
| Opening docs/help URLs in browser | User action (Help menu) | standard `xdg-open`/`open` |

**Hard control:** `ANY2ANY_OFFLINE=1` makes *any* socket connect in core+GUI raise `E_INTERNAL` (dev safety net also used by tests).

**Comparison note (evidence):** 2anything performs licence validation + optional update checks (VERIFIED, privacy policy §2); Any2Any has neither, so its offline story is stricter.

## 4. Temporary-file safety

1. Job dirs created with user-only permissions (0700 / ACL equivalent).
2. Intermediate names are fixed-format (`step-01.html`), no user-controlled path segments → traversal impossible inside temp.
3. Cleanup in `finally` + startup sweep; crash recovery sweep validates dir marker file `<job>.json` before deletion.
4. Outputs: refuse to write outside chosen output root after `realpath` normalization; reject paths containing `..` after normalization escaping root (defense in depth for crafted archives).
5. Multi-file outputs from containers (e.g., mbox→pdf, zip extract P2): each entry name sanitized (no absolute paths, no `..`, no reserved device names on Windows), size/count limits enforced.

## 5. Source preservation

- Adapters open inputs read-only; contract test asserts checksum unchanged.
- No in-place mode exists in the product (non-goal).
- Overwrite only affects *output paths* under policy.

## 6. Malicious-input defenses

| Threat | Mitigation | Test |
|---|---|---|
| Zip-slip / path traversal | entry name sanitization + root check | T-SEC-01 |
| Zip bomb / decompression bomb | max entries (10,000), max expanded bytes (config default 4 GB), max ratio | T-SEC-02 |
| Billion laughs / XML bomb | forbid custom entities; size cap on XML | T-SEC-03 |
| ReDoS in parsers | timeouts on parse steps; avoid catastrophic regexes; fuzz | T-SEC-04 |
| Shell injection via filename | argv arrays only; property test on weird names | T-SEC-05 |
| Symlink escape (output dir) | resolve+containment check before final rename | T-SEC-06 |
| Huge CSV memory | `W_LARGE_FILE_MEMORY` warning above threshold; documented in-memory limit (parity: 2anything blog VERIFIED states memory-bound behavior) | T-SEC-07 |
| Decoder crashes (image bombs) | Pillow decompression-bomb guard (MAX_IMAGE_PIXELS), subprocess isolation for risky formats | T-SEC-08 |

## 7. Logging & diagnostics

- Levels: ERROR/WARN/INFO/DEBUG (`--debug`).
- Default record: timestamp, level, code, job/item id, format pair, engine name, duration, exit status. **No file contents, no document text, no full env.**
- Paths: logged as basename only unless `--debug` (then full path, local only).
- Bug-report export command (`any2any history --last-error --redact` planned P1): redacts usernames in paths automatically.
- Subprocess stderr captured to per-step log under temp, deleted with job unless `--debug` keeps it (disclosed in log).

## 8. Privacy tests (automated)

| ID | Test | Method |
|---|---|---|
| PRIV-01 | Conversion makes zero network connections | monkeypatch `socket.socket` to raise; run full P0 fixture suite |
| PRIV-02 | Fresh install makes zero connections on GUI open / CLI `--help` | same socket trap; plus OS-level: Linux `unshare -n` smoke |
| PRIV-03 | `engines install` is the only code path calling network; requires consent | unit test with fake HTTP, assert refusal without `--yes`/dialog |
| PRIV-04 | Logs contain no file contents | convert fixture with unique sentinel string; grep log dir for sentinel → absent |
| PRIV-05 | History respects `history_full_paths=false` | set flag, convert, inspect DB → basename only |
| PRIV-06 | Temp dir removed after success/failure/cancel | assert dir list empty post-run |
| PRIV-07 | Source checksum unchanged (all adapters) | contract suite |
| PRIV-08 | Offline env var blocks even installer | `ANY2ANY_OFFLINE=1` + install attempt → `E_INTERNAL`/blocked |

Manual/offline verification: run GUI with firewall rule deny for `any2any` binary; perform full session (convert, history, settings); confirm no prompts/failures.
