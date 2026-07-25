# Changelog

All notable changes to AEQ-OS are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/); versioning is manual semver (`MAJOR.MINOR.PATCH`) — bump `MINOR` on new rules/domains, `MAJOR` on any rule renumbering or removal (which `CONTRIBUTING.md` asks contributors to avoid entirely), `PATCH` on wording/doc fixes that change no rule's meaning.

## [1.5.0] — 2026-07-25

### Added
- `CORE/security_baseline.md` (`SEC-1..18`) — always-loaded security floor extending `CONST-26`/`CONST-27`: secrets lifecycle, least privilege, authn/authz baseline, sandboxing and destructive-action confirmation, data classification, supply-chain vetting, prompt-injection framing, and a security regression gate alongside `G1`–`G4`. Security is now a default system capability rather than something a project's route has to match into.
- `CORE/intent_resolution.md` (`INT-1..14`) — the prompt-abstraction layer: the agent classifies intent, implicated routes, and persona framing, and assembles context (rules → memory → repo ground truth) before acting, so terse requests get treated the way fully-specified ones would. No wire-level prompt rewriting and no daemon — this is agent behavior, consistent with AEQ-OS having no runtime.
- `CORE/memory_governance.md` (`MEM-1..15`) — a portable, four-tier memory model (working/episodic/semantic/procedural) on plain files any tool can read. Key rule: a recalled fact naming a specific file/symbol/config is verified before it's *acted on*, never assumed current just because it's remembered.
- `CORE/learning_engine.md` (`LEARN-1..14`) — the Mistake Learning Engine. Generalizes `DEP-19`'s "every rollback gets a postmortem that patches a gate" to every mistake: a fixed record schema (root cause required, not just the fix), recall-before-repeat, and pattern promotion — a mistake recurring twice becomes a proposed new or tightened rule instead of just another log entry.
- `DOMAINS/production_readiness.md` (`PROD-1..18`) — a pre-launch institutional-grade audit distinct from `deployment_and_audit.md`'s release mechanics: architecture/scalability, API security, secrets/environment, observability, error handling, performance baseline, backup/restore, attack surface, CI/CD pipeline privilege, compliance, and dependency/license audit, output as a scored PASS/FLAG/BLOCK report per pillar. Loads whenever `deployment_and_audit.md` loads (`deploy_rule`, extended). Mechanically-fixable findings are fixed directly in the same pass; design-decision findings are reported, not guessed at.
- All five new files wired into `ROUTER_MAP.json`: the four `CORE/*.md` files added to `always_load`; `production_readiness.md` added to the `deploy_release` route and the `deploy_rule` resolution text.
- Cross-tool compatibility expansion: `templates/windsurf-rules.md`, `templates/copilot-instructions.md`, `templates/clinerules.md` (also covers Roo Code), and `templates/aider-conventions.md`, alongside the existing Claude Code / Antigravity / Cursor / generic `AGENTS.md` coverage. `install.sh`/`install.ps1` and `BOOT.md`'s wiring table updated to reference all of them.
- `scripts/adopt-project.sh` — stamps a project with a project-root `AGENTS.md` pointer in one command, non-destructively (appends to an existing `AGENTS.md` rather than overwriting). Closes the gap where AEQ-OS only auto-loaded on machines that had personally run `install.sh`: a project-root pointer is discovered automatically by any compatible tool, with zero per-machine setup, even on a teammate's fresh clone.
- `scripts/status.sh` extended to report project-root pointer presence (not just global per-tool wiring) and to recognize the five new rule-ID prefixes in its git-history evidence check.
- Three pre-existing documentation staleness issues fixed while touching these files: `BOOT.md`'s version header was still `1.2.0` though `ROUTER_MAP.json` had already reached `1.4.0`; `BOOT.md`'s `Layout` tree and `templates/AGENTS.md` were both missing `portfolio_risk.md`, `market_data_quality.md`, `trading_compliance.md`, `model_lifecycle.md`, and `exhaustive_research.md`, added in v1.3.0/v1.4.0 but never added to either; and `docs/ARCHITECTURE.md`'s rule-index table listed `RESEARCH` as 20 rules when `RESEARCH-21` had already shipped in v1.4.0 — the table's own row was stale even though the grand total happened to already be counted correctly.
- Total: **418 rules across 22 files**, verified by `scripts/validate.py`.

### Notes
- All additions in this release are plain Markdown/JSON/text — no daemon, no background process, no dependency beyond what `install.sh`/`validate.py` already required. An opt-in, free, local-only "Performance tier" (faster memory search, optional background security scanning) is scoped as a distinct follow-up and tracked in the README roadmap; it is not part of this release.

## [1.4.0] — 2026-07-18

### Added
- `DOMAINS/portfolio_risk.md` (`PORT-1..20`) — risk across a book of strategies, not just one: portfolio-level exposure/VaR/drawdown caps, correlation and concentration limits, tail-risk scenarios beyond VaR, leverage and liquidity bounds, staged capital allocation for new strategies.
- `DOMAINS/market_data_quality.md` (`DATA-1..20`) — point-in-time correctness, survivorship-bias-free universes, corporate-action adjustment, bad-tick/outlier filtering, multi-vendor reconciliation, data lineage.
- `DOMAINS/trading_compliance.md` (`COMP-1..18`) — regulator-grade audit trail, automated manipulation-pattern self-checks (layering/spoofing/wash-trading), regulatory position thresholds, information barriers. Defensive by design — detects and refuses the pattern class, never specifies it.
- `DOMAINS/model_lifecycle.md` (`MDL-1..18`) — trading model/strategy versioning distinct from `ai_agent_orchestration.md` (LLM agents): shadow deployment, champion/challenger promotion criteria, decay monitoring, training/serving skew checks, formal retirement.
- All four wired into `ROUTER_MAP.json`: `portfolio_risk.md`/`market_data_quality.md`/`model_lifecycle.md` load for `quant_research_backtest`; all four (plus `trading_compliance.md` via the `hard_rule`) load for `quant_live_execution`; `model_lifecycle.md` also loads for `rl_training`.
- `RESEARCH-21` — standard institutional metric suite (Sharpe, Sortino, Calmar, profit factor, CAGR, max drawdown, win rate) required in every strategy evaluation, reported together rather than optimized in isolation, to prevent single-metric overfitting.
- Fixed a cross-platform `install.ps1` bug found by actually executing it under PowerShell 7: `Get-Item` without `-Force` silently treats dot-prefixed paths (`.ai_os`) as hidden on every OS PowerShell runs on, so the existing-install detection never fired. Also replaced `Remove-Item -Force` with `.Delete()` on the reparse point directly, since `Remove-Item`'s cross-platform behavior on a directory-symlink is inconsistent and can require `-Recurse` — which would be dangerous here.
- Total: 339 rules across 17 files, verified by `scripts/validate.py`.

## [1.3.0] — 2026-07-18

### Added
- `DOMAINS/exhaustive_research.md` (`RESEARCH-1..20`) — pushes backtesting research past literally testing what was asked: hypothesis-space breadth (`RESEARCH-1/2`), cost/regime sensitivity bands (`RESEARCH-3/4`), overfitting guards (`RESEARCH-5/6/8`), negative-result reporting (`RESEARCH-11`), and a live-readiness gate (`RESEARCH-17`) feeding `LIVE-17`'s shadow-stage ramp.
- Loaded by both `quant_research_backtest` and `quant_live_execution` routes in `ROUTER_MAP.json`.
- `scripts/status.sh` — on-demand installation health check (symlink integrity, per-tool pointer wiring, `validate.py` result, rule-ID citation evidence from real project git history). Explicitly not a background dashboard — see `README.md` FAQ for why.

## [1.2.0] — 2026-07-18

### Added
- Public repository scaffold: `README.md` (human-facing), `LICENSE` (MIT), `CONTRIBUTING.md`, `SECURITY.md`, `CODEOWNERS`, issue/PR templates, CI workflow.
- `scripts/validate.py` — CI self-check for `ROUTER_MAP.json` integrity, rule-ID contiguity, and banned-lexicon absence.
- `install.sh` / `install.ps1` — cross-platform installer (symlink on macOS/Linux, junction on Windows) into `~/.ai_os`.
- `templates/` — drop-in integration snippets for Claude Code, Google Antigravity, and Cursor.
- `docs/ARCHITECTURE.md` — extended Mermaid diagrams, component table, rule index.

### Changed
- **Boot file renamed `README.md` → `BOOT.md`.** The former agent-facing boot loader now lives at `BOOT.md`; `README.md` is the human-facing GitHub landing page. All global pointers (`~/.claude/CLAUDE.md`, `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`) and `ROUTER_MAP.json`'s `boot` field were updated to match. **Any prior install must re-run the installer or manually update its pointer.**

## [1.1.0] — 2026-07-10

### Added
- `DOMAINS/fullstack_architecture.md` (`FS-1..20`) — migration safety, stateless/stateful boundaries, outbox reconciliation, API contract safety.
- `DOMAINS/ui_ux_design_system.md` (`UIUX-1..20`) — institutional design tokens, data hierarchy, low-latency rendering.
- `DOMAINS/deployment_and_audit.md` (`DEP-1..20`) — zero-downtime deploy discipline, drift tracking, pre-merge inspection.
- Router routes: `fullstack_platform`, `ui_frontend`, `deploy_release`; `deploy_rule` resolution entry forcing `deployment_and_audit.md` on any production-bound task.

## [1.0.0] — 2026-07-10

### Added
- Initial release: `CORE/constitution.md`, `CORE/model_adaptation.md`, `CORE/stack_selection.md`, `CORE/verification_protocol.md`.
- `DOMAINS/quant_trading_engine.md`, `DOMAINS/live_trading_gate.md`, `DOMAINS/ai_agent_orchestration.md`, `DOMAINS/distributed_rag.md`, `DOMAINS/financial_audit_ledger.md`.
- `ROUTER_MAP.json` and `BOOT.md` (then named `README.md`) boot protocol.
