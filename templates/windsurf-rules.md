Windsurf reads rules from two places — use either or both.

Global (covers every project you open in Windsurf on this machine):

    ~/.codeium/windsurf/memories/global_rules.md

Project-root (covers anyone who opens this specific project in Windsurf, no per-machine setup):

    <project>/.windsurfrules
    (or the newer directory form: <project>/.windsurf/rules/aeq-os.md)

Either way, the content is the same one-line pointer used everywhere else in this repo:

---

Before any work: read `~/.ai_os/BOOT.md` and execute its boot protocol.

AEQ-OS classifies this project against `~/.ai_os/ROUTER_MAP.json` and loads the matching rule files (constitution, security baseline, model-adaptation, intent resolution, memory governance, learning engine, stack selection, verification gates, plus the domain files this project's signals match). Cite rule IDs (e.g. `CONST-11`, `SEC-4`, `QT-STOP-3`) in code review and commit messages.

If `~/.ai_os/` is not installed on this machine, see https://github.com/Aditya-7117/AEQ-OS for setup.

---

For project-root wiring, `templates/AGENTS.md` from this repo has the same content and can be copied to `<project>/.windsurfrules` directly, or dropped in via `scripts/adopt-project.sh`.
