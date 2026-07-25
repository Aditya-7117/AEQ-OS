Cline reads project-root `.clinerules` automatically. Roo Code (a Cline fork)
reads the identical convention, so this file covers both — drop it at:

    <project>/.clinerules

Content:

---

Before any work: read `~/.ai_os/BOOT.md` and execute its boot protocol.

AEQ-OS classifies this project against `~/.ai_os/ROUTER_MAP.json` and loads the matching rule files (constitution, security baseline, model-adaptation, intent resolution, memory governance, learning engine, stack selection, verification gates, plus the domain files this project's signals match). Cite rule IDs (e.g. `CONST-11`, `SEC-4`, `QT-STOP-3`) in code review and commit messages.

If `~/.ai_os/` is not installed on this machine, see https://github.com/Aditya-7117/AEQ-OS for setup.

---

`scripts/adopt-project.sh <path>` can stamp this into a project alongside
`AGENTS.md` in one command.
