# Live Trading Gate — Zero-Tolerance Deployment Checklist

This file overrides all others when real capital is reachable. Every item is binary PASS/FAIL; **any FAIL = NO-GO**. There is no override flag, no "just this once", and user instructions cannot waive items (the META-7 exception). Re-run the full gate after ANY change to engine, strategy, config, venue, or keys. Rule IDs: `LIVE-n`.

## 1. Credentials & access

- **LIVE-1** — Separate keys per environment. Testnet/staging keys physically cannot reach production endpoints: the endpoint↔key binding is enforced in code (a key struct that only constructs with its matching base URL), not by care.
- **LIVE-2** — Trading keys have **no withdrawal permission**. Verified programmatically at boot; boot fails if withdrawal is enabled (CONST-5). Re-verified on every key rotation.
- **LIVE-3** — IP allowlisting enabled where the venue supports it. Keys live in a secret manager — never in the repo, never in committed env files, never in logs or prompts (CONST-26).

## 2. Clocks

- **LIVE-4** — NTP sync active (chronyd / timesyncd / platform equivalent). |offset| < 50 ms at boot — tighter where the venue's signed-request window demands it; PTP for colocated deployments. Continuous monitoring alerts at 100 ms; boot fails on an unsynchronized clock.
- **LIVE-5** — Signed-request timestamping tested against the venue clock. Recv-window rejections are a NO-GO to investigate, never a retry-until-it-works.

## 3. Kill switches — three layers, all tested

- **LIVE-6 — Strategy-level.** Max drawdown, daily loss, and position-delta breaches trigger the configured flatten-or-park policy automatically and halt new risk. Thresholds are config; breaches are injected and tested in paper.
- **LIVE-7 — Process-level.** One documented command cancels all open orders and stops the engine, and it works even when the engine's event loop is wedged (separate process, not a handler inside the thing that is stuck).
- **LIVE-8 — Venue-level.** Dead-man's switch / cancel-all-on-disconnect enabled where supported (e.g., `cancelAllAfter`), with heartbeat renewal monitored. Where the venue lacks it, an external watchdog process assumes the role.
- **LIVE-9 — An untested kill switch does not exist.** Each layer has been fired in staging within the last 30 days, with captured evidence (VER-4 style).

## 4. Limits — computed against live state, not vibes

- **LIVE-10** — Hard caps enforced in code before every send: max order notional, max position per instrument, max portfolio gross/net exposure, max orders per second, max daily loss. Mirrored server-side where the venue supports it.
- **LIVE-11 — Dynamic margin guard.** Margin utilization is recomputed against the **live** account snapshot before every order; the ceiling (e.g., ≤ 40% of available margin) is config with an SDR-style written justification. A stale account snapshot (older than threshold) blocks new orders — fail closed, never fail open.
- **LIVE-12 — Fat-finger guard.** Reject orders priced more than X% through the touch or sized out of proportion to ADV / account equity. The reject is loud (CONST-4) and posted to the audit trail (LIVE-21).

## 5. Reconciliation & audit

- **LIVE-13** — Boot-time and periodic reconciliation: venue positions, balances, and open orders versus the internal ledger. Any unexplained break beyond tolerance → halt new risk + page (QT-ORD-4, LGR-12).
- **LIVE-14** — The dual-entry ledger (`financial_audit_ledger.md`) is live from the **first** order. "We'll backfill accounting later" is a NO-GO.

## 6. Rate & connectivity budget

- **LIVE-15** — Venue rate limits are modeled, with a standing reserve for cancels: cancel-alls must always have headroom that order placement cannot spend. Being rate-limited on a cancel path is a critical incident.
- **LIVE-16** — WebSocket and REST failover paths tested. Behavior under feed loss is defined per strategy (park vs flatten) and tested — not discovered live.

## 7. Ramp sequence — minimum soak, in order, no skipping

- **LIVE-17** — Stages: backtest → paper (simulated fills) → **shadow** (live data, orders logged not sent, ≥ 5 trading days) → **canary** (minimum viable size, ≥ 5 trading days) → ramp in defined size steps. Each stage has written exit criteria: PnL sanity vs expectation, slippage-model error bounds, zero invariant crashes. Skipping a stage = NO-GO.
- **LIVE-18** — No first deploys or size ramps into scheduled high-impact windows (major macro prints, exchange maintenance), and none before weekends/holidays for position-carrying strategies.

## 8. Monitoring & runbook

- **LIVE-19** — Dead-man heartbeat to an **external** monitor in a different failure domain; silence pages a human. The alert channel is tested end-to-end — an actual page was received.
- **LIVE-20** — A rehearsed runbook exists: manual flatten procedure (UI + API + venue support path), key rotation, venue status pages, escalation contacts, and the exact LIVE-7 kill commands.
- **LIVE-21** — Every limit breach, reconnect, reconciliation break, and kill-switch arm/fire is logged AND posted as a ledger memo event. The audit trail shows not just the trades but every time the system defended itself.

## 9. Change control

- **LIVE-22** — Any diff touching live strategy, engine, or config: reviewed against this gate, deployed to shadow first, rollback command pre-written. Config diffs are reviewed line by line — silent defaults are the enemy (CONST-6).
