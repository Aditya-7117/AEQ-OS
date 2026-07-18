# Portfolio & Risk Management — Domain Invariants

`quant_trading_engine.md` governs one strategy's execution. This file governs risk **across a book of strategies and positions** — the layer a prop desk or fund actually lives or dies by. Rule IDs: `PORT-n`.

## 1. Sizing and allocation

- **PORT-1 — Position sizing is a named, justified methodology.** Kelly-fraction (capped, never full Kelly), volatility-targeting, or fixed-fractional — chosen and documented, never ad hoc. The methodology and its parameters live in versioned config, not a magic number in a function call.
- **PORT-2 — Capital allocation across strategies is a documented, versioned process.** Reallocating capital between strategies is a reviewed change (`DEP`-style change control), not an informal adjustment. A strategy's allocation history is queryable.
- **PORT-20 — New strategies start small and earn capital.** A strategy enters live trading at minimum allocated risk budget and earns more only after a defined live track record clears a pre-declared bar — this is the promotion criterion `DOMAINS/model_lifecycle.md`'s champion/challenger process (`MDL-9`) implements mechanically, and it presumes the strategy already cleared `exhaustive_research.md`'s live-readiness gate (`RESEARCH-17`).

## 2. Portfolio-level limits

- **PORT-3 — Portfolio-level exposure caps, enforced pre-trade.** Gross and net exposure limits apply across the whole book, not just per-instrument (`LIVE-10` is per-order/per-instrument; this is the portfolio-wide superset). Checked before every new order, against the live portfolio state, same fail-closed discipline as `LIVE-11`.
- **PORT-4 — VaR / Expected Shortfall computed and capped at portfolio level**, recomputed on every position change — a risk number older than the position it's supposed to bound is worse than no number.
- **PORT-5 — Portfolio-level drawdown circuit breaker**, distinct from any single strategy's own breaker (`LIVE-6` is per-strategy). A portfolio-level breach halts new risk **across every strategy**, not just the one that tripped it — correlated strategies can all be losing for the same underlying reason simultaneously.
- **PORT-6 — Correlation and concentration limits.** No more than a declared percentage of capital in positions correlated above a declared threshold; explicit single-name and sector concentration caps.
- **PORT-7 — Factor exposure is monitored and bounded** (market beta, sector, style factors) — a book of "independent" strategies can still be one unintentional macro bet in disguise.
- **PORT-11 — Cross-strategy netting, not naive summation.** When multiple strategies trade correlated or identical instruments, portfolio risk uses netted exposure. Summing each strategy's risk independently double-counts the shared position and understates true concentration.
- **PORT-14 — Cross-model correlation is monitored.** Two strategies that are secretly 95% correlated are one point of failure wearing two names — surfaced as a metric, not discovered after both draw down together (ties to `MDL-14`).

## 3. Leverage, liquidity, and tail risk

- **PORT-8 — Leverage limits are explicit per asset class**, with a margin-call simulation run before any leverage increase is approved — never raise leverage on the assumption that margin will "probably be fine."
- **PORT-9 — Liquidity risk is bounded by participation rate.** Position sizes are capped as a percentage of average daily volume, with an explicit estimated unwind time under stressed liquidity — a position you can't exit in a crisis isn't sized correctly even if VaR says it's fine.
- **PORT-10 — Stress testing against real and hypothetical scenarios** (2008, 2020 COVID crash, flash-crash-style liquidity gaps, and scenarios specific to the strategy's instruments) is required before scaling capital, not optional due diligence.
- **PORT-15 — Tail risk gets its own number, not just VaR.** VaR underestimates tail risk by construction. A defined maximum-plausible-loss scenario (beyond VaR's confidence interval) is computed and checked against the firm's stated risk appetite — a portfolio that's "fine" at 95% VaR and catastrophic at the 99.9th percentile is not fine.
- **PORT-16 — Minimum diversification before scaling.** A minimum number of genuinely uncorrelated (per `PORT-14`) strategies or instruments is required before capital scales up — prevents a single point of failure in "the" alpha source.

## 4. Process discipline

- **PORT-12 — Risk breaches post to the audit trail** with the same rigor as `LIVE-21` — every limit breach, near-breach, and override is a recorded event, not a Slack message that evaporates.
- **PORT-13 — Every risk limit exposes a metric.** If a limit can be breached, it's observable before it is (`CONST-29` applied to portfolio risk specifically) — dashboards exist for limits, not just for PnL.
- **PORT-17 — Rebalancing is scheduled and cost-aware, not discretionary.** Rebalance triggers and cadence are explicit config; the rebalance decision itself accounts for the trading cost it incurs, so rebalancing doesn't quietly bleed the portfolio it's meant to protect.
- **PORT-18 — The risk model itself is versioned.** VaR methodology, correlation estimation window, and factor model choice are versioned and their assumptions documented — a risk number is only as trustworthy as the model behind it, and a silently changed model produces a discontinuous, misleading risk number.
- **PORT-19 — Portfolio-level kill switches share the same architecture as `LIVE-6/7/8`**, not a parallel bespoke system. One kill-switch design, invoked at both the strategy and portfolio level, is auditable; two independent implementations are two things that can each fail differently.
