# Financial Audit Ledger — CA-Grade Accounting Layer

Dual-entry, append-only, tamper-evident. Shared by trading engines (fills, fees, funding) AND agent systems (LLM spend metering per AGT-2). Institutional Chartered-Accountancy discipline: every unit of value has a from-account and a to-account, history is immutable, and the books must prove themselves daily. Rule IDs: `LGR-n`.

## 1. Core invariants

- **LGR-1 — Dual-entry.** Every economic event posts ≥ 2 legs expressed as signed deltas; the legs sum to exactly zero per unit. Multi-asset events (a BTC/USDT fill) carry cost-basis legs in the reporting unit with quantities as leg metadata (see §2), so the zero-sum invariant always holds. An unbalanced entry is rejected with a crash-level error at write time — never "logged for later cleanup".
- **LGR-2 — Append-only journal.** No UPDATE, no DELETE, ever. Corrections are explicit reversing entries referencing the original `entry_id`, followed by the corrected entry. The history shows the mistake AND the fix — that is the point.
- **LGR-3 — Tamper evidence.** Each entry embeds `hash_prev` (hash chain per journal). Chain verification is a scheduled job and a mandatory pre-audit step.
- **LGR-4 — Idempotent ingestion.** Entries carry a `source.event_id` (fill ID, invoice line ID, API call ID). Re-ingesting the same source event is a no-op, not a duplicate.

## 2. Entry schema

    {
      "entry_id": "<uuid7>",
      "ts_event": "<venue/provider UTC timestamp>",
      "ts_recorded": "<local UTC timestamp>",
      "source": {"system": "binance", "event_id": "<venue fill id>", "kind": "fill"},
      "legs": [
        {"account": "assets:exchange:binance:USDT", "delta": "-1000.00", "unit": "USDT"},
        {"account": "positions:BTCUSDT:cost",       "delta": "999.00",   "unit": "USDT",
         "qty": "0.01523000", "qty_unit": "BTC"},
        {"account": "expenses:fees:binance:taker",  "delta": "1.00",     "unit": "USDT"}
      ],
      "memo": "<free text, never load-bearing>",
      "hash_prev": "<sha256 of previous entry>",
      "reverses": null
    }

`kind` values: `fill | fee | funding | borrow | transfer | llm_call | adjustment | reversal`. Legs sum to zero in `unit` (here: −1000.00 + 999.00 + 1.00 = 0).

- **LGR-5 — Chart of accounts is explicit and versioned:** `assets:` (per venue per asset), `positions:` (per instrument, cost + qty), `expenses:` (fees / funding / borrow / llm per provider), `income:` (realized PnL per strategy), `equity:`, `suspense:`, `residual:`. New accounts arrive via reviewed config, never as ad-hoc strings at a call site.
- **LGR-6 — Suspense is loud.** Unclassifiable events post to `suspense:` with an alert — never dropped. Suspense must reach zero before any period close.

## 3. Precision

- **LGR-7** — Amounts are Decimal strings or integer minor units with per-asset scale from instrument metadata. Float is forbidden end-to-end in the ledger path (CONST-11), **including serialization**: amounts are JSON strings, never JSON numbers.
- **LGR-8** — Rounding mode per venue is documented (round-half-even unless the venue truncates); every currency conversion records its rate source and rate timestamp.
- **LGR-9** — Rounding residuals post to the dedicated `residual:` account. Nothing vanishes — and a residual account growing abnormally is itself a bug detector.

## 4. Reconciliation & close

- **LGR-10 — Trial balance daily:** all accounts sum to zero per unit. Failure means data corruption: halt and investigate, do not "adjust".
- **LGR-11 — PnL attribution reconciles:** realized + unrealized + fees + funding + residual = equity delta, exactly. No plug numbers; an unexplained gap is a break, not a footnote.
- **LGR-12 — Three-way reconciliation** per venue per day: internal ledger vs venue trade history vs venue balance snapshot. Breaks are aged — T+0 investigate, T+1 escalate; a break beyond threshold halts new risk (LIVE-13). Every break resolves with an auditable entry (reclass or reversal), end to end.
- **LGR-13 — Period close:** monthly hash-chain verification + trial balance + reconciliation sign-off, exported as an immutable report (CSV/parquet + summary), retained ≥ 7 years.

## 5. Time & scope

- **LGR-14** — UTC everywhere; venue-local times stored as annotations only. The `ts_event` vs `ts_recorded` spread is a monitored metric (QT-TIME-1).
- **LGR-15** — One journal per economic scope (entity/account). Cross-scope transfers are paired entries in both journals, each referencing the other.

## 6. Agent spend metering (reuse of this layer)

- **LGR-16** — LLM and tool spend posts as `kind: llm_call`: debit `expenses:llm:<provider>:<model>`, credit `liabilities:payable:<provider>`, amounts from the versioned price table (AGT-3). Provider invoices reconcile monthly against the journal exactly like a venue (LGR-12). This is what turns an agent budget cap from advisory prose into an auditable control.
