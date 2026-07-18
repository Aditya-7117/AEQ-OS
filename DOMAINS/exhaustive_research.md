# Exhaustive Backtesting Research — Domain Invariants

For strategy research and backtesting. The premise: a literal request to "test X" is one point in a hypothesis space, not the whole task. A research agent that only ever answers the exact question asked will hand back a cherry-picked, overfit, silently-fragile result — and that result is the thing someone eventually risks real capital on. This file exists to make "exhaustive" mean something specific and bounded, not a vibe. Rule IDs: `RESEARCH-n`.

## 1. Scope the space before answering the point

- **RESEARCH-1 — The request is a point, not the task.** When asked to test a strategy or parameter set, treat the literal ask as one point in a neighborhood. Default to sweeping a defined range/grid around it (parameter values, lookback windows, entry/exit thresholds) unless the user has explicitly scoped the task to exactly that one configuration ("only test these exact params, nothing else").
- **RESEARCH-2 — Declare the explored manifest.** Every research output states, explicitly, what was actually swept: parameter ranges, regime splits, cost models, date ranges, universe. The user must be able to see the boundary of what was searched, not just the winning result inside it.
- **RESEARCH-12 — Exhaustiveness is budget-bounded.** "Explore the space" is never unbounded. A compute/time/API-cost budget is set before the sweep starts (ties to `AGT-1`), and the manifest (`RESEARCH-2`) states what was left unexplored *because of the budget* — never silently omitted as if it didn't matter.
- **RESEARCH-20 — Diminishing-returns stop rule.** The sweep stops when a defined marginal-improvement threshold isn't cleared across successive rounds (ties to `AGT-4`'s no-progress loop guard) — "be exhaustive" is not a license for an unbounded fishing expedition.

## 2. Report the shape of the result, not a point estimate

- **RESEARCH-3 — Regime decomposition.** Report performance broken out by at least trend/range and high/low volatility regimes (or the domain's natural split) — never only the blended aggregate. A strategy profitable in one regime out of four is a different claim than "profitable," and the blended number alone hides which claim is true.
- **RESEARCH-4 — Cost sensitivity band.** Every headline result is re-run under a pessimistic and an optimistic cost/slippage assumption; report the range, not a single number computed under whichever assumption happened to be default.
- **RESEARCH-7 — Parameter sensitivity surface.** Report how performance changes across the neighborhood of the chosen parameters, not just at the point. A result that collapses under a small parameter nudge — a cliff — is flagged explicitly as fragile even when the point estimate looks excellent. A robust plateau and a lucky spike look identical as a single number.
- **RESEARCH-10 — Sample-size / power check.** Before a metric (Sharpe, win rate, profit factor) is reported as meaningful, state the number of independent trades or periods behind it, with an explicit flag when it's too low to support the claimed confidence.

## 3. Guard against fooling yourself

- **RESEARCH-5 — Out-of-sample holdout stays untouched.** A holdout window is set aside *before* any parameter search begins and is evaluated exactly once, at the end. Re-running the search after seeing holdout results and then calling the new result "final" is the holdout leaking into the fit — treat it as a fresh, unvalidated claim requiring a new holdout.
- **RESEARCH-6 — Walk-forward over single split.** Multi-window walk-forward validation is the default. A single train/test split is preliminary evidence, never confirmatory — label it as such if that's all that's been run.
- **RESEARCH-8 — Multiple-comparisons correction.** When N variants were tried, the reported statistic is corrected for having picked the best of N (deflated Sharpe ratio, White's Reality Check, or at minimum an explicit "N configurations were tried" disclosure alongside the winner). Reporting the winner's raw statistic as if it were the only thing tested is a well-known way to manufacture an edge that isn't there.
- **RESEARCH-9 — Baseline comparison is mandatory.** Every result is reported alongside a trivial baseline — buy-and-hold, random-entry cost-matched, or the prior production strategy. "Beats nothing" is not a result.
- **RESEARCH-13 — Look-ahead and survivorship checks precede everything else.** Before any result is trusted, confirm the universe and data used could have been known point-in-time: no survivorship bias, no restated fundamentals, no corporate actions applied retroactively. Extends `QT-DET-3`'s look-ahead guard from the code level to the dataset level — a leak here invalidates every result built on top of it.

## 4. Don't stop at the first negative, and don't hide the trail

- **RESEARCH-11 — Negative results are reported, not discarded.** Configurations tried and rejected are listed with why, in a table analogous to `VER-9`'s evidence table. Cherry-picking the winner and deleting the trail of what failed is exactly the failure mode this file exists to prevent — the failed 90% of the sweep is part of the answer, not noise to clean up.
- **RESEARCH-15 — Propose the next informative variant.** When a result is inconclusive or marginal, propose — don't silently drop — the next most informative thing to test (a different regime split, an alternate signal transform, a different holding period). "The requested test didn't show an edge" is a stopping point only if `RESEARCH-16` says the search was broad enough to be informative.
- **RESEARCH-16 — Distinguish "didn't find an edge" from "isn't there."** A negative result states explicitly whether the searched space (per the `RESEARCH-2` manifest) was broad enough to be informative, or whether the absence of evidence just reflects an under-searched space. Never conflate the two in the write-up.

## 5. Reproducibility and live-readiness

- **RESEARCH-14 — Deterministic reproducibility of the whole sweep.** The exact grid, seeds, and data snapshot used are recorded so the entire sweep — not just one winning run — can be replayed byte-for-byte. Extends `QT-DET-2` from a single backtest to the search process that produced it.
- **RESEARCH-17 — Live-readiness gate.** A backtest result may not be represented as ready for paper/live promotion until it has cleared `RESEARCH-4` (cost sensitivity), `RESEARCH-6` (walk-forward), `RESEARCH-8` (multiple-comparisons correction), and `RESEARCH-9` (baseline comparison). A single in-sample backtest is explicitly insufficient grounds — this is the gate `live_trading_gate.md`'s `LIVE-17` shadow-stage ramp assumes was already satisfied before shadow trading even begins.

## 6. Communicating results honestly

- **RESEARCH-18 — Report format.** A research write-up carries, in order: the explored manifest (`RESEARCH-2`), the headline result with its cost and regime bands, the parameter sensitivity surface, the negative-result table, and an explicit "not yet explored" section. This mirrors `VER-9`'s evidence-table discipline, applied to research instead of code completion — the format itself is what keeps a result honest under time pressure.
- **RESEARCH-19 — Confidence-calibrated framing.** The headline framing matches the search breadth, not the best number found: "promising in 2 of 4 regimes, cost-sensitive above 8bps, N=340 trades" beats "Sharpe 2.1" as the actual headline — the single number is supporting detail, not the claim.
