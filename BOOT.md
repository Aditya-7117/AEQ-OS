# AEQ-OS — Boot Loader

Version 1.6.0 · Model-agnostic (Claude Code, Google Antigravity, Cursor, Windsurf, GitHub Copilot, Cline/Roo Code, Aider, GPT, local/open-source models, any AGENTS.md-reading tool)

This file is a **boot image for coding agents**, not documentation for humans — for the human-facing overview, see [README.md](README.md). Any agent working on a project on this machine executes the boot protocol below before its first edit of a session.

## Boot protocol (in order, every session)

1. Read `CORE/constitution.md` — the law. Applies to every line of code, every stack.
2. Read `CORE/security_baseline.md` — the security floor. Same tier as the law: always loaded, not something a project's route has to match into.
3. Read `CORE/model_adaptation.md` — your own failure modes and their countermeasures.
4. Read `CORE/intent_resolution.md` — classify the request's intent, implicated route(s), and persona framing, and assemble context before acting. Runs before router classification narrows the loaded rule set (`INT-14`).
5. Read `CORE/memory_governance.md` — recall relevant project/user memory (working/episodic/semantic/procedural tiers), scoped to the intent classified in step 4. Verify anything recalled against current repo state before acting on it (`MEM-6`).
6. Read `CORE/learning_engine.md` — check existing mistake/success records relevant to the classified route before proceeding (`LEARN-6`). A new record is written whenever a gate fails, a user correction occurs, or a postmortem is warranted during the session (`LEARN-4`).
7. Read `ROUTER_MAP.json` — classify the current project against each route's `signals`; load every file in the matched route's `load` list. Multiple matches → load the union. Real funds reachable → the hard rule applies regardless of route. Shipping to production → the deploy rule loads `DOMAINS/deployment_and_audit.md` and `DOMAINS/production_readiness.md` regardless of route.
8. Read `CORE/stack_selection.md` — if the project has no Stack Decision Record (SDR) yet, produce one before writing code.
9. Before claiming any task complete, pass the gates in `CORE/verification_protocol.md` — for a first production launch, `DOMAINS/production_readiness.md`'s `PROD-17` gate applies on top.

## Precedence

`constitution.md` < domain files < `live_trading_gate.md`. The stricter rule always wins. A domain file may **tighten** a constitutional rule, never loosen it. When real capital or live venue keys are reachable from the code being written, `DOMAINS/live_trading_gate.md` overrides everything and cannot be waived — not even by direct user instruction (see META-7).

## Rule IDs

Every rule has a stable, greppable ID: `CONST-n`, `SEC-n`, `META-n`, `INT-n`, `MEM-n`, `LEARN-n`, `STACK-n`, `VER-n`, `QT-<AREA>-n`, `LIVE-n`, `RESEARCH-n`, `PORT-n`, `DATA-n`, `COMP-n`, `MDL-n`, `AGT-n`, `RAG-n`, `LGR-n`, `FS-n`, `UIUX-n`, `DEP-n`, `PROD-n`. Cite IDs in code review, commit messages, SDRs, and audit output. Resolve any citation with:

    grep -rn "QT-STOP" ~/.ai_os/

IDs are append-only: retired IDs are never reused, rules are never renumbered.

## Layout

    ~/.ai_os/                               (installed copy — see install.sh / install.ps1)
    ├── README.md                        ← human-facing overview (GitHub landing page)
    ├── BOOT.md                          ← this file — agent boot loader
    ├── ROUTER_MAP.json                  ← machine-readable project→files routing
    ├── CORE/
    │   ├── constitution.md              ← non-negotiable coding law
    │   ├── security_baseline.md         ← always-on security floor: secrets, authn/z, sandboxing, data protection
    │   ├── model_adaptation.md          ← anti-laziness metacognitive layer
    │   ├── intent_resolution.md         ← prompt-abstraction layer: intent/persona classification, context assembly
    │   ├── memory_governance.md         ← portable tiered memory: working/episodic/semantic/procedural
    │   ├── learning_engine.md           ← mistake learning engine: record schema, recall, pattern promotion
    │   ├── stack_selection.md           ← dynamic tech-stack decision procedure
    │   └── verification_protocol.md     ← quality gates G0–G4, evidence rules
    └── DOMAINS/
        ├── quant_trading_engine.md      ← concurrency, WebSocket, stop math, parity
        ├── live_trading_gate.md         ← zero-tolerance live deployment checklist
        ├── exhaustive_research.md       ← hypothesis-space breadth, overfitting guards
        ├── portfolio_risk.md            ← position sizing, VaR/drawdown caps, tail risk
        ├── market_data_quality.md       ← point-in-time correctness, survivorship bias, lineage
        ├── trading_compliance.md        ← audit trail, manipulation-pattern self-checks
        ├── model_lifecycle.md           ← model versioning, decay, champion/challenger
        ├── ai_agent_orchestration.md    ← budgets, loop guards, RL state, multi-agent
        ├── distributed_rag.md           ← lineage, multi-store sync, embedding drift
        ├── financial_audit_ledger.md    ← dual-entry, hash-chained, CA-grade ledger
        ├── fullstack_architecture.md    ← migrations, state boundaries, contract safety
        ├── ui_ux_design_system.md       ← matte-black tokens, density, live-render perf
        ├── deployment_and_audit.md      ← zero-downtime deploys, drift, merge inspection
        └── production_readiness.md      ← prototype-to-institutional-grade pre-launch audit

## Wiring into an agent tool (one-time, per machine)

Each tool needs one static pointer to this file — no daemon, no background process, negligible overhead (a few hundred tokens read once per session). Two ways to wire it — both fire automatically, with zero chat prompting, once set up:

- **Global (per machine, covers every project you open in that tool):**

  | Tool | Mechanism | File |
  |------|-----------|------|
  | Claude Code | global instructions | `~/.claude/CLAUDE.md` |
  | Google Antigravity / Gemini CLI | global rules | `~/.gemini/AGENTS.md` and/or `~/.gemini/GEMINI.md` |
  | Cursor | User Rules (app setting, no file) | Cursor Settings → Rules → User Rules |
  | Windsurf | global rules | `~/.codeium/windsurf/memories/global_rules.md` |
  | GitHub Copilot | personal custom instructions | GitHub → Settings → Copilot → Custom instructions |

- **Project-root (covers anyone who opens this specific project, on any machine, in any compatible tool — no per-machine setup required):**

  | Tool | File |
  |------|------|
  | Claude Code, Cursor, and any AGENTS.md-adopting tool (OpenAI Codex CLI, Amp, Jules, and a growing list of others) | `<project>/AGENTS.md` |
  | GitHub Copilot | `<project>/.github/copilot-instructions.md` |
  | Windsurf | `<project>/.windsurfrules` or `<project>/.windsurf/rules/*.md` |
  | Cline / Roo Code | `<project>/.clinerules` |
  | Aider | `<project>/CONVENTIONS.md` (loaded via `--read` or `.aider.conf.yml`) |

  Run `scripts/adopt-project.sh <path>` to stamp a project with its `AGENTS.md` pointer in one command (non-destructive — appends if one already exists, never overwrites).

- **Open-source / local models (Ollama, LM Studio, vLLM, and similar):** not a separate integration point. Whichever of the tools above is running the model reads the same pointer file the same way regardless of which model backs it — AEQ-OS is plain text, read identically no matter the model.

Each pointer is one line:

> Before any work: read `~/.ai_os/BOOT.md` and execute its boot protocol.

Ready-to-use snippets for each tool live in [`templates/`](templates/). Run `scripts/status.sh` to check which pointers are actually wired, globally and for the current project.

## Maintenance

- The OS version lives in `ROUTER_MAP.json`. Bump it on any rule change.
- Rules are append-mostly: add new IDs rather than editing semantics of old ones; deprecate explicitly.
- This OS applies to agents. Humans may override it; the agent records the override and the rule ID it displaces.
