# Quant Trading Engine — Domain Invariants

Applies to backtest, paper, and live engines alike (parity is the point — QT-DET-1). Live deployment additionally requires every item in `live_trading_gate.md` to PASS. Rule IDs: `QT-<AREA>-n`.

## 1. Architecture

- **QT-ARCH-1 — Event-driven core.** Strategy logic is a pure function `(State, Event) -> [Action]`. All inputs (feeds, fills, timers, clock) enter as events; all outputs (orders, cancels, alerts) leave as actions. This purity is what makes replay, backtest parity, and audit possible — protect it.
- **QT-ARCH-2 — Single-writer order state.** Exactly one task/thread owns each order's state machine; everyone else sends messages to it. No shared mutable order books or position maps across threads.
- **QT-ARCH-3 — Event log first.** Every inbound event and outbound action is appended to a sequenced, timestamped log *before* it is processed/dispatched. The engine must be reconstructible from the log alone.
- **QT-ARCH-4 — Hot path discipline (T0/T1 tiers).** The tick → decision → order path performs no allocation, takes no locks, makes no syscalls beyond the send, and does no logging I/O (ring buffer to a drain thread instead).

## 2. Concurrency

- **QT-CONC-1** — One documented owner per shared datum (CONST-14). Canonical flow: feeds → bounded SPSC/MPSC queues → strategy thread → order gateway. Per-queue policy declared (CONST-15): market-data queues may drop-oldest-with-metric; order/ack/fill queues never drop — they block or halt the engine.
- **QT-CONC-2** — No check-then-act across threads (CONST-16). Position checks, margin checks, and stop evaluation execute on the owning thread, atomically with the action they gate. A margin check on thread A gating an order sent from thread B is a race, full stop.
- **QT-CONC-3** — Race detector / TSAN / loom runs in CI for every concurrent module; a race finding is a build failure.
- **QT-CONC-4** — Shutdown is ordered: stop intake → drain decision queue → cancel or park open orders per policy → flush event log → exit. `kill -9` at any instant must be recoverable from the log (crash-only, CONST-5).

## 3. Market data & WebSocket state management

- **QT-WS-1 — Connection is a state machine:** `CONNECTING → AUTHENTICATED → SYNCING (snapshot + buffered deltas) → LIVE → DEGRADED → RESYNCING | CLOSED`. Trading decisions consume market data only in `LIVE`.
- **QT-WS-2 — Sequence integrity.** Track per-stream sequence numbers. Any gap → state `DEGRADED`, trigger snapshot resync. Never patch over a gap or interpolate a missing delta.
- **QT-WS-3 — Staleness.** Every feed declares a max age; a book older than threshold is not tradable input (→ `DEGRADED`). Heartbeats/pings are monitored; a missed heartbeat is `DEGRADED`, not a shrug.
- **QT-WS-4 — Reconnect protocol.** Exponential backoff with full jitter, capped; reconnect counts are metrics (CONST-29). On reconnect: re-authenticate, re-subscribe, snapshot resync, and order-state reconciliation (QT-ORD-4) — only then `LIVE`.
- **QT-WS-5 — Book construction is verified.** Snapshot+delta application is property-tested; where the venue provides a book checksum (e.g., CRC every N updates), verify it and treat mismatch as a gap (QT-WS-2).
- **QT-WS-6 — Parse to ticks at the boundary.** Prices and sizes parse directly from wire strings into integer ticks/lots (CONST-11). A float never appears downstream of the parser.

## 4. Order lifecycle

- **QT-ORD-1 — Idempotency keys.** Every order carries a client order ID unique per *intent*. A resubmission after timeout reuses the key, so venue-side duplicates are detectable instead of doubling exposure.
- **QT-ORD-2 — Explicit state machine:** `NEW → PENDING → OPEN → PARTIALLY_FILLED → FILLED | CANCELED | REJECTED | EXPIRED`, plus `UNKNOWN`. The legal-transition table is enforced in code; an illegal transition is an invariant crash (CONST-7).
- **QT-ORD-3 — UNKNOWN is first-class.** After a timeout or disconnect, an unacknowledged order is `UNKNOWN` and is treated as **live worst-case exposure** until the venue proves otherwise. Risk limits reserve capacity for UNKNOWN orders. Optimism here loses money; pessimism is mandatory.
- **QT-ORD-4 — Reconciliation.** On every connect and on a fixed interval: venue open orders, positions, and balances are truth. Divergence beyond tolerance → halt new risk and alert (LIVE-13, LGR-12).
- **QT-ORD-5 — Fills post to the ledger** (`financial_audit_ledger.md`) at ingestion time, preserving venue timestamps. Accounting is not a batch job bolted on later.

## 5. Trailing stop-loss math (exact specification)

Per-position state: `side`, watermark `W`, trail (`d` absolute in ticks, or ratio `r`), stop `S`, optional activation price `A`, latched `triggered` flag.

- **QT-STOP-1 — Watermark.** LONG: `W = max(W, ref_price)`. SHORT: `W = min(W, ref_price)`. The reference price source (last trade / mark / mid / bid / ask) is pinned in config and never mixed between updates.
- **QT-STOP-2 — Stop derivation.** LONG: `S_raw = W − d` (or `W × (1 − r)`). SHORT: `S_raw = W + d` (or `W × (1 + r)`). Ratio math in Decimal, then converted to ticks.
- **QT-STOP-3 — Monotonicity invariant.** LONG stops never decrease; SHORT stops never increase: `S_new = max(S_old, S_raw)` for longs, `min` for shorts. A receding stop widens risk silently — enforce with a production assertion (CONST-7) and a property test.
- **QT-STOP-4 — Rounding never widens risk.** Converting `S_raw` to a valid tick: LONG stops round **up**, SHORT stops round **down** — the realized trail distance is never wider than configured. Direction is documented and tested.
- **QT-STOP-5 — Activation.** If `A` is set, trailing arms only once `ref_price` crosses `A` (LONG: `≥ A`). Before arming, no watermark updates occur.
- **QT-STOP-6 — Trigger is a latch.** LONG triggers when `ref_price ≤ S`; once triggered it cannot un-trigger on a bounce. Execution policy (market vs aggressive limit with a slippage budget) is explicit config. Record trigger price AND fill price separately; slippage beyond budget alerts.
- **QT-STOP-7 — Gaps.** If price gaps through `S`, the stop fires at the next evaluable price. The shortfall is expected, is visible in PnL attribution (LGR-11), and is never averaged away.
- **QT-STOP-8 — Crash safety.** `W` and `S` are persisted on every change, or exactly recoverable from the event log. On restart, `W` is restored — **never re-seeded from the current price**, which silently resets the trail and widens risk. This is the classic trailing-stop bug; test the restart path explicitly.
- **QT-STOP-9 — Evaluation site.** Stops are evaluated on the single-writer thread, on every qualifying event, atomically with order emission (QT-CONC-2). Timer-only stop checking is forbidden — a stop that polls can miss the move it exists for.
- **QT-STOP-10 — Required property tests:** monotonicity under random walks; `S` always exactly the rounded trail distance from the extreme of `W`; replaying the same event log reproduces identical `(W, S, triggered)` sequences; no un-trigger; restart mid-sequence preserves `W`.

## 6. PnL

- **QT-PNL-1** — PnL derives from fills and mark events only — never from intended orders. Realized and unrealized are separate; fees, funding, and borrow accrue as their own ledger legs (LGR §2).
- **QT-PNL-2** — Attribution reconciles: the sum of components equals the total, with no plug numbers (LGR-11).

## 7. Time

- **QT-TIME-1** — Monotonic clock for intervals and timeouts; NTP-disciplined UTC wall clock for stamps (CONST-13). Every event records the venue timestamp AND the local receive timestamp; their spread is a monitored metric.
- **QT-TIME-2** — Never compare timestamps across clocks or venues without an explicit offset model.

## 8. Determinism & backtest parity

- **QT-DET-1** — Backtest, paper, and live run the **same strategy code path**; only the event source and action sink differ. Divergence between a backtest and a replay of live logs through the same code is a release-blocking bug.
- **QT-DET-2** — Seeded randomness only; collection iteration order must be deterministic (beware hash-map ordering in Go/Python).
- **QT-DET-3** — Look-ahead bias guards: strategy code can only read events with sequence ≤ current. Accessors enforce it; tests probe it with crafted future-data traps.
