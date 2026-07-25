Aider has no automatic project-root convention file today — point it at a
conventions file explicitly, either per-invocation or via config.

Per-invocation:

    aider --read CONVENTIONS.md

Or persist it in `<project>/.aider.conf.yml`:

    read: CONVENTIONS.md

Create `<project>/CONVENTIONS.md` with:

---

Before any work: read `~/.ai_os/BOOT.md` and execute its boot protocol.

AEQ-OS classifies this project against `~/.ai_os/ROUTER_MAP.json` and loads the matching rule files (constitution, security baseline, model-adaptation, intent resolution, memory governance, learning engine, stack selection, verification gates, plus the domain files this project's signals match). Cite rule IDs (e.g. `CONST-11`, `SEC-4`, `QT-STOP-3`) in code review and commit messages.

If `~/.ai_os/` is not installed on this machine, see https://github.com/Aditya-7117/AEQ-OS for setup.

---

Note: unlike the other templates in this directory, Aider needs the explicit
`--read`/`.aider.conf.yml` step above even for project-root wiring — it does
not yet auto-discover `AGENTS.md` or a similarly-named file on its own.
