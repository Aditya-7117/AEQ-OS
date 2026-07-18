# Changelog

All notable changes to AEQ-OS are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/); versioning is manual semver (`MAJOR.MINOR.PATCH`) — bump `MINOR` on new rules/domains, `MAJOR` on any rule renumbering or removal (which `CONTRIBUTING.md` asks contributors to avoid entirely), `PATCH` on wording/doc fixes that change no rule's meaning.

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
