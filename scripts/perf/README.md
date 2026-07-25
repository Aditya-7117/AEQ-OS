# AEQ-OS Performance Tier (opt-in)

Real local tooling that closes `MEM-15`, `SEC-18`, and `PROD-18`'s tier-awareness
rules — never required, never a paid API or subscription, never a background
process unless you explicitly register one. The Lite tier (agent-driven
grep/read, on-demand checklists) stays fully functional and is never
deprecated; these tools only make it faster.

Every tool here operates on whatever project you point it at (default: the
current directory, walking up to the nearest `.git/` or existing `.ai_os/`),
not on the AEQ-OS repo itself.

## Memory search — `memory_index.py`

```bash
scripts/perf/memory_index.py build            # index .ai_os/memory/ into SQLite FTS5
scripts/perf/memory_index.py update            # incremental reindex (add/changed/removed)
scripts/perf/memory_index.py search "query"    # full-text search
scripts/perf/memory_index.py search "query" --semantic   # embedding-based, if available
scripts/perf/memory_index.py status            # index state for the current project
```

`build` always creates a zero-dependency SQLite FTS5 index (Python's stdlib
`sqlite3` — nothing to install). It also probes `http://localhost:11434`
(a local-only call, never external) for an already-pulled Ollama embedding
model (`nomic-embed-text`, `mxbai-embed-large`, `all-minilm`, or anything
with "embed" in its name). If one's found, `search --semantic` becomes
available; if not, FTS5-only search still works and the tool says so — it
never errors and never nags you to install anything.

## Security scan orchestration — `security_scan.py`

```bash
scripts/perf/security_scan.py            # human-readable report
scripts/perf/security_scan.py --json     # machine-readable
```

Detects which stacks are present (Python/Node/Rust/Go, by manifest file) and
runs the free scanner `SEC-15` already names for each — `bandit`+`pip-audit`
for Python, `npm audit` for Node, `cargo audit` for Rust, `gosec` for Go —
if it's installed. A missing scanner is reported as MISSING with its exact
free install command; this tool never bundles a scanner itself and never
reports PASS for one it didn't actually run.

## Production readiness — `readiness_check.py`

```bash
scripts/perf/readiness_check.py
```

Scripts the mechanical subset of `production_readiness.md`'s `PROD-n`
checklist: dependency/CVE audit (via `security_scan.py`), unpinned
dependency detection, a same-line missing-timeout heuristic on common HTTP
client calls, and `:latest` tags in deploy manifests. Pillars that need
judgment — architecture readiness, runbook quality, backup drills, attack
surface review, compliance — are listed as REQUIRES REVIEW, never faked as
PASS.

## Opt-in background watcher — `watcher.py` + installers

```bash
scripts/perf/watcher.py --path <project> --interval 300   # run in the foreground
scripts/perf/install_watcher.sh <project> [--interval SECONDS]   # generate a unit, don't register it
scripts/perf/uninstall_watcher.sh <project>                      # remove a generated unit
```

`watcher.py` is a bounded polling loop with a clean shutdown path (`SIGTERM`/
`SIGINT` exit it immediately, no orphaned process) — it re-indexes memory
when files change and re-runs the security scan on a longer interval
(`--security-interval`, default 6h).

`install_watcher.sh` generates a launchd plist (macOS) or a systemd `--user`
unit (Linux), uniquely labeled per project (`com.aeq-os.watcher.<project>`),
and flips `.ai_os/performance.json`'s `watcher.enabled` flag — but it does
**not** register the unit with launchd/systemd itself. It prints the exact
one-line command (`launchctl load -w ...` / `systemctl --user enable --now
...`) for you to run when you're ready to actually start it. `uninstall_
watcher.sh` refuses to delete a currently-loaded unit's file out from under
launchd/systemd — it tells you to unload/stop it first, then remove it.
Windows has no automated installer (untested in this toolkit's development
environment); the tool prints the `watcher.py` command to wire into Task
Scheduler yourself.

## Config

Each project that opts in gets `.ai_os/performance.json`, created by the
first `build`/`install_watcher.sh` run:

```json
{
  "tier": "performance",
  "memory_index": {"backend": "fts5", "embeddings": "none", "last_build": "..."},
  "watcher": {"enabled": false}
}
```

`scripts/status.sh`, run from inside a project, reports this file's state
alongside the existing global/project-root pointer checks.
