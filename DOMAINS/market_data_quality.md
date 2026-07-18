# Market Data Quality — Domain Invariants

`exhaustive_research.md` assumes clean, point-in-time-correct data going in — this file is what makes that assumption actually true. Bad data doesn't look like a crash; it looks like a great backtest that dies in production. Rule IDs: `DATA-n`.

## 1. Point-in-time correctness

- **DATA-1 — Point-in-time correctness for everything, not just prices.** Any fundamental, reference, or metadata field used in a backtest must reflect the value as it was known at that historical date — never a later-restated value. Extends `QT-DET-3`'s look-ahead guard from code down to the data layer, where the leak is invisible unless checked explicitly.
- **DATA-3 — Survivorship-bias-free universes.** Backtests use the historical constituent list of an index or universe as it existed at each point in time, including names that were later delisted or went bankrupt — not today's survivors projected backward.
- **DATA-10 — Point-in-time snapshots are immutable.** Once a research run references a specific data snapshot, that snapshot is never mutated in place. New data creates a new versioned snapshot — the reproducibility `RESEARCH-14` requires depends on the snapshot it cited still existing exactly as it was.
- **DATA-13 — Universe definitions are versioned.** The exact rule defining "the tradable universe" (market cap, liquidity, listing status) is versioned. Changing it retroactively silently changes every historical backtest that relied on "the universe" — a definition change is a migration (`FS-1`/`FS-2` style), not a config tweak.

## 2. Corporate actions and adjustments

- **DATA-2 — Corporate actions are applied consistently and deliberately.** Splits, dividends, mergers, spin-offs, and symbol changes adjust historical prices correctly, with the adjustment method (forward vs. backward) a documented, deliberate choice — not whatever the data vendor happened to default to.
- **DATA-17 — Benchmark and index data get the same integrity bar.** Benchmark series used for `RESEARCH-9`'s baseline comparison are themselves versioned and point-in-time correct. A silently reconstituted index shouldn't quietly change your historical Sharpe-vs-benchmark.

## 3. Quality, gaps, and outliers

- **DATA-5 — Missing data is never silently disguised as real data.** A gap is flagged, not forward-filled or interpolated by default. If interpolation is used, it's a documented, tested methodology applied deliberately, distinguishable after the fact from genuine observations.
- **DATA-8 — Bad-tick and outlier detection is explicit and tested.** Erroneous prints (fat-finger trades, exchange glitches) are filtered before reaching any strategy or backtest — and the filter's false-positive rate is itself monitored, because rejecting a real sharp move is also a bug.
- **DATA-15 — Cross-venue price consistency is checked.** An unusual spread between venues for the same instrument, beyond a defined threshold, flags for review — it's either bad data or a real arbitrage signal, and either way it needs a look before being trusted silently.

## 4. Lineage, versioning, and vendors

- **DATA-9 — Full lineage on every derived dataset.** Adjusted prices, computed features, and any transformation trace back to their raw source and the exact transformation applied — the `RAG-1` chunk-lineage discipline, applied to market data instead of RAG chunks.
- **DATA-7 — A vendor schema change is a migration, not a silent adaptation.** When a data vendor changes format, it's versioned and handled explicitly (`FS-1`/`FS-2`), never patched around quietly downstream where the next engineer won't know why the logic looks odd.
- **DATA-4 — Multi-vendor reconciliation is a scheduled job.** When more than one data source exists for the same instrument, a reconciliation job flags divergence beyond tolerance — same reconciliation pattern family as `LGR-12`, `QT-ORD-4`, `RAG-7`, `FS-12`, applied here to market data.
- **DATA-19 — Vendor failover has a documented, reconciled path.** For any critical live feed, a secondary-vendor failover exists, and format differences between primary and secondary are reconciled by the same schema-versioning discipline (`DATA-7`) — a failover that hands the strategy differently-shaped data is not a safe failover.
- **DATA-16 — Alternative and unstructured data get no exemption.** News, sentiment, and alt-data ingestion follow the same lineage (`DATA-9`) and point-in-time (`DATA-1`) rules as structured market data — "it's soft data" is not a reason to skip the discipline.
- **DATA-18 — Raw data is retained, not just derived/adjusted data.** Retaining the raw feed means any adjustment methodology can be re-derived or corrected later without re-sourcing history from a vendor that may no longer have it available or may have changed its own historical record.

## 5. Timing, completeness, and parity

- **DATA-6 — Timestamps are normalized to UTC with the exchange calendar modeled explicitly** (holidays, half-days, DST transitions) — an off-by-one-session bug from an unmodeled holiday is a silent, hard-to-spot error class.
- **DATA-14 — Feed completeness has a monitored SLA.** A feed's expected update cadence is known; staleness beyond it is a monitored metric — the market-data equivalent of `RAG-15`'s freshness SLO. A stale feed used unknowingly in a live decision is worse than a feed that's visibly down.
- **DATA-11 — Live and historical data share a code path where possible**, mirroring `QT-DET-1`'s backtest/live parity principle. Divergent pipelines for live feeds versus historical backtests are a well-known source of bugs that only appear in production.
- **DATA-20 — Periodic backtest-vs-live data parity audit.** A strategy's live-consumed data is periodically diffed against what a backtest would have seen for the same period, to catch silent pipeline drift before it silently degrades a live strategy's edge.
- **DATA-12 — Data licensing and redistribution rights are tracked per vendor contract**, as part of the same vendor-reconciliation discipline as `DATA-4` — relevant the moment data crosses a desk, product, or client boundary within a firm.
