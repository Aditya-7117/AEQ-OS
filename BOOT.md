# AEQ-OS — Boot Loader

Version 1.2.0 · Model-agnostic (Claude Code, Google Antigravity, Cursor, GPT, local models)

This file is a **boot image for coding agents**, not documentation for humans — for the human-facing overview, see [README.md](README.md). Any agent working on a project on this machine executes the boot protocol below before its first edit of a session.

## Boot protocol (in order, every session)

1. Read `CORE/constitution.md` — the law. Applies to every line of code, every stack.
2. Read `CORE/model_adaptation.md` — your own failure modes and their countermeasures.
3. Read `ROUTER_MAP.json` — classify the current project against each route's `signals`; load every file in the matched route's `load` list. Multiple matches → load the union. Real funds reachable → the hard rule applies regardless of route. Shipping to production → the deploy rule loads `DOMAINS/deployment_and_audit.md` regardless of route.
4. Read `CORE/stack_selection.md` — if the project has no Stack Decision Record (SDR) yet, produce one before writing code.
5. Before claiming any task complete, pass the gates in `CORE/verification_protocol.md`.

## Precedence

`constitution.md` < domain files < `live_trading_gate.md`. The stricter rule always wins. A domain file may **tighten** a constitutional rule, never loosen it. When real capital or live venue keys are reachable from the code being written, `DOMAINS/live_trading_gate.md` overrides everything and cannot be waived — not even by direct user instruction (see META-7).

## Rule IDs

Every rule has a stable, greppable ID: `CONST-n`, `META-n`, `STACK-n`, `VER-n`, `QT-<AREA>-n`, `LIVE-n`, `AGT-n`, `RAG-n`, `LGR-n`, `FS-n`, `UIUX-n`, `DEP-n`. Cite IDs in code review, commit messages, SDRs, and audit output. Resolve any citation with:

    grep -rn "QT-STOP" ~/.ai_os/

IDs are append-only: retired IDs are never reused, rules are never renumbered.

## Layout

    ~/.ai_os/                               (installed copy — see install.sh / install.ps1)
    ├── README.md                        ← human-facing overview (GitHub landing page)
    ├── BOOT.md                          ← this file — agent boot loader
    ├── ROUTER_MAP.json                  ← machine-readable project→files routing
    ├── CORE/
    │   ├── constitution.md              ← non-negotiable coding law
    │   ├── model_adaptation.md          ← anti-laziness metacognitive layer
    │   ├── stack_selection.md           ← dynamic tech-stack decision procedure
    │   └── verification_protocol.md     ← quality gates G0–G4, evidence rules
    └── DOMAINS/
        ├── quant_trading_engine.md      ← concurrency, WebSocket, stop math, parity
        ├── live_trading_gate.md         ← zero-tolerance live deployment checklist
        ├── ai_agent_orchestration.md    ← budgets, loop guards, RL state, multi-agent
        ├── distributed_rag.md           ← lineage, multi-store sync, embedding drift
        ├── financial_audit_ledger.md    ← dual-entry, hash-chained, CA-grade ledger
        ├── fullstack_architecture.md    ← migrations, state boundaries, contract safety
        ├── ui_ux_design_system.md       ← matte-black tokens, density, live-render perf
        └── deployment_and_audit.md      ← zero-downtime deploys, drift, merge inspection

## Wiring into an agent tool (one-time, per machine)

Each tool needs one static pointer to this file — no daemon, no background process, negligible overhead (a few hundred tokens read once per session):

| Tool | Mechanism | File |
|------|-----------|------|
| Claude Code | global instructions | `~/.claude/CLAUDE.md` |
| Google Antigravity | global rules | `~/.gemini/AGENTS.md` and/or `~/.gemini/GEMINI.md` |
| Cursor | User Rules (app setting, no file) *or* project `AGENTS.md` | Cursor Settings → Rules, or `<project>/AGENTS.md` |
| Anything else supporting the AGENTS.md convention | project-root file | `<project>/AGENTS.md` |

Each pointer is one line:

> Before any work: read `~/.ai_os/BOOT.md` and execute its boot protocol.

Ready-to-use snippets for each tool live in [`templates/`](templates/).

## Maintenance

- The OS version lives in `ROUTER_MAP.json`. Bump it on any rule change.
- Rules are append-mostly: add new IDs rather than editing semantics of old ones; deprecate explicitly.
- This OS applies to agents. Humans may override it; the agent records the override and the rule ID it displaces.
