# Trading Model & Strategy Lifecycle — Domain Invariants

Distinct from `ai_agent_orchestration.md` (LLM agents) and `deployment_and_audit.md` (infra deploys): this file governs the lifecycle of a trading **model or strategy itself** — versioning, promotion, decay, and retirement — whether it's a rule-based strategy or an ML-based signal. Rule IDs: `MDL-n`.

## 1. Versioning and the registry

- **MDL-1 — Every strategy/model has an immutable version identifier.** A "same strategy, different version" claim must be provable by diff against the registry entry, never just asserted from memory.
- **MDL-7 — A model registry is the source of truth.** Every deployed version, its training-data snapshot, hyperparameters, and backtest evidence (`RESEARCH-18`'s report) are stored in a queryable registry — not scattered across notebooks, spreadsheets, and chat history.
- **MDL-6 — Feature and signal inputs are versioned.** A model trained against feature-set v1 is never silently fed feature-set v2 inputs in production — same embedder-version isolation principle as `RAG-9`/`RAG-10`, applied to trading features.
- **MDL-16 — Training/serving skew is checked directly.** The exact code path used to compute a feature at training time is used at serving time (or is verified byte-equivalent) — extends `QT-DET-1`'s backtest/live parity principle specifically to ML feature pipelines, where skew is a well-known, silent source of live underperformance.

## 2. Promotion and capital

- **MDL-2 — Shadow deployment precedes promotion.** A new model version runs in shadow — real data, no real orders — alongside the production version for a minimum declared period before promotion, mirroring `LIVE-17`'s shadow stage but scoped to model *swaps*, not just first-ever deployment.
- **MDL-9 — Champion/challenger with pre-declared promotion criteria.** A new version is a "challenger" until it beats the "champion" on **live**, not just backtest, performance over a defined evaluation window. The promotion bar is stated in advance — never decided post hoc by whichever number happens to look better once the data is in.
- **MDL-3 — Staged capital allocation.** A new model version starts with a small capital/risk allocation and earns more only after clearing the pre-declared live bar — the mechanical implementation of `PORT-20`'s "new strategies earn capital" rule.
- **MDL-10 — Ensemble and blend transitions are tested for discontinuities.** Moving from a single model to an ensemble, or changing ensemble weights, is checked for a sudden position jump at the swap moment — the crash-safe-state-transition principle `QT-STOP-8` applies to trailing stops applies here to portfolio composition changes.

## 3. Monitoring and decay

- **MDL-4 — Continuous decay monitoring against explicit thresholds.** Rolling Sharpe, hit rate, and slippage-vs-backtest-expectation are monitored in production with pre-declared alert thresholds — decay is expected eventually; silent decay is not acceptable.
- **MDL-12 — Data drift is monitored on live inputs.** The statistical distribution of live input features is compared against the training distribution; significant drift is flagged before it silently degrades the model — the `RAG` embedding-drift concept, applied to trading model features.
- **MDL-5 — Retraining triggers are explicit and declared in advance**: scheduled, decay-triggered, or regime-change-triggered. "Let's retrain because it feels stale" is not a trigger.
- **MDL-17 — Claimed PnL attribution reconciles to the ledger.** A model's claimed PnL contribution reconciles against the actual booked PnL in `financial_audit_ledger.md`/`QT-PNL` — no model gets credited for PnL it didn't actually produce, however good its dashboard looks.

## 4. Risk-awareness and interpretability

- **MDL-11 — Explainability is part of the registry entry.** For any model whose decisions aren't fully interpretable (ML-based signals), a feature-attribution or sensitivity report ships alongside the model — a black-box signal still needs an explanation of what's driving it, for both risk review and `trading_compliance.md`'s audit needs.
- **MDL-14 — Cross-model correlation is monitored**, feeding directly into `PORT-14` — two "different" models that are secretly highly correlated are one point of failure wearing two names, and that fact belongs in the registry, not discovered during a shared drawdown.
- **MDL-18 — Capacity is capped before market impact erodes the edge.** A model's live capital allocation is capped at the point where its own market impact would materially degrade its backtested edge — informed by `PORT-9`'s liquidity/ADV participation constraint. Scaling a strategy past its own capacity doesn't produce more of the same edge; it produces a different, worse strategy.

## 5. Rollback and retirement

- **MDL-8 — Rollback is a tested, one-command operation**, mirroring `DEP-3`'s rollback discipline — reverting to a prior model version should be exactly as fast and safe as a code rollback, because it's the same category of operation.
- **MDL-13 — Retirement is formal, not silent.** A deprecated model version has its capital reduced to zero and is formally retired — with monitoring continuing briefly afterward to confirm no residual positions or effects remain — rather than simply being stopped and assumed clean, following the same lifecycle discipline `QT-ORD-2` applies to individual orders.
- **MDL-15 — Manual overrides of a live model signal are logged with operator identity and reason**, at the same rigor `META-7` requires for any rule override — a human overriding a model's live decision is exactly the kind of event that needs to be reconstructible later.
