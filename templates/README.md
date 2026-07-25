# Templates

Drop-in snippets for wiring AEQ-OS into a specific tool or workflow. See [BOOT.md](../BOOT.md#wiring-into-an-agent-tool-one-time-per-machine) for the full per-tool compatibility matrix.

## Agent tool pointers

| File | Tool |
|---|---|
| `CLAUDE.md-snippet.md` | Claude Code (global) |
| `AGENTS.md` | Google Antigravity, and any AGENTS.md-adopting tool — also usable as a project-root pointer for Claude Code/Cursor |
| `cursor-user-rules.txt` | Cursor (global User Rules) |
| `windsurf-rules.md` | Windsurf |
| `copilot-instructions.md` | GitHub Copilot |
| `clinerules.md` | Cline / Roo Code |
| `aider-conventions.md` | Aider |

## `ci-github-actions.yml` — enforcement, not just instruction

Drop this into **your own project's** `.github/workflows/aeqos-gate.yml` (not AEQ-OS's own repo) to turn a mechanical subset of the rulebook from "an agent might follow this" into "a CI check that actually fails the PR": the banned-lexicon grep, `scripts/perf/security_scan.py`, and `scripts/perf/readiness_check.py`, all running against your code on every pull request.

This is the honesty boundary the tools it runs already draw: only mechanically-checkable items gate the build. A `MISSING` scanner (one your project's stack could use but doesn't have installed) is reported, not treated as a failure — the job output tells you the exact free install command if you want that coverage. Judgment-requiring items (architecture review, runbook quality, and the rest of `production_readiness.md`'s non-mechanical pillars) are never faked as automated.
