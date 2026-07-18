# Trading Compliance & Audit — Domain Invariants

Engineering support for a firm's compliance and market-access obligations. This file is defensive by design: it exists so a strategy or a bug never *accidentally* produces a pattern regulators treat as manipulative, and so every order is reconstructible for a regulator after the fact. It does not describe how to manipulate markets — the rules below exist specifically to detect and refuse that class of pattern, intentional or not. Rule IDs: `COMP-n`.

## 1. Audit trail

- **COMP-1 — Regulator-grade audit trail on every order event.** Every order, modification, and cancellation is logged with enough detail — timestamp, price, size, and the triggering condition or strategy signal — to reconstruct intent after the fact. This extends `QT-ARCH-3`'s event log with a specific target reader: a regulator or auditor who wasn't in the room.
- **COMP-9 — Record retention meets the applicable regulatory period**, typically 5–7 years depending on jurisdiction, immutably, and distinct from the shorter operational retention an event log might otherwise use for storage-cost reasons.
- **COMP-13 — Test and simulated orders are unambiguously tagged**, in a namespace that can never be confused with production order flow in an audit. Sharing an order-ID scheme between test and live environments is the kind of ambiguity an auditor — or an incident review — cannot resolve after the fact.

## 2. Manipulation-pattern self-checks

- **COMP-2 — Automated pre-trade and post-trade checks for manipulative patterns**: layering and spoofing (orders placed with no realistic intent to execute), wash trading (trading with yourself or a coordinated counterparty), and momentum ignition. The system flags or refuses orders matching these signatures — including when the pattern emerges accidentally from a strategy bug, which is the far more common real-world case than deliberate manipulation.
- **COMP-3 — Cancel-to-fill ratio is monitored against a compliance-motivated cap**, not just an infrastructure rate limit. An excessive cancel ratio is a known regulatory red flag and often an exchange-penalized pattern in its own right — extend `LIVE-15`'s rate budgeting with this ratio specifically.
- **COMP-16 — The manipulation-pattern checks are never a specification.** The codebase must not implement, simulate, or test manipulative order patterns for any purpose, including research — `COMP-2`'s detectors exist to catch this pattern class, not to provide a template for producing it.
- **COMP-15 — Compliance checks are periodically tested with known-bad synthetic sequences**, mirroring `VER-8`'s mutation spot-check: feed the manipulation-pattern detector (`COMP-2`) and the cancel-ratio monitor (`COMP-3`) synthetic sequences that should trip them, and confirm they do. An untested detector is exactly as trustworthy as an untested test suite.

## 3. Regulatory limits and thresholds

- **COMP-4 — Best-execution rationale is logged per order.** For firms with a best-execution obligation, the routing/execution logic's decision rationale — which venue, why — is logged per order, so a best-execution claim is auditable after the fact rather than asserted from the design docs alone.
- **COMP-5 — Regulatory position and reporting thresholds are tracked and alert before breach** (large-trader reporting, beneficial-ownership disclosure triggers) — discovered in advance, never after the filing deadline has passed.
- **COMP-6 — Account-type regulatory limits are enforced in code**, not assumed to be caught by the broker: Pattern Day Trader rules, Reg T margin limits, and equivalent jurisdiction-specific constraints fail closed if a limit would be breached.
- **COMP-11 — Engineering limits are a superset of the regulatory minimum, never a subset.** Where a jurisdiction mandates specific categories of pre-trade risk check (e.g., market-access control rules), `LIVE-10` and `PORT-3`'s limits are cross-checked against that mandated minimum — the firm's own limits may be stricter, never looser.
- **COMP-7 — Jurisdiction is explicit per venue.** An order routed to a venue in a different regulatory jurisdiction carries that jurisdiction's applicable rule set explicitly; the project's Stack Decision Record (`stack_selection.md`) names every jurisdiction in scope, since the compliance surface changes per jurisdiction, not just the tech stack.
- **COMP-10 — Kill switches are mapped to their regulatory justification.** `LIVE-6/7/8`'s kill-switch layers are documented against whichever market-access control requirement they're meant to satisfy (e.g., SEC Rule 15c3-5-style obligations) — an explicit mapping, not an assumption that "we have a kill switch" automatically means "we're compliant."

## 4. Access, information, and change control

- **COMP-8 — Information barriers are enforced in code, not policy alone.** Where the firm has non-public material information workflows (research, corporate access), trading systems enforce access control on the relevant strategies or desks — same ACL pre-filter pattern as `RAG-13`, applied to information-barrier boundaries.
- **COMP-18 — Personal and restricted-account trading checks.** Where personal trading restrictions apply (blackout periods, restricted lists), the system enforces or at minimum flags a check against the restricted list before an order tied to a restricted account executes.
- **COMP-12 — Compliance-relevant code changes get compliance-visible review.** Changes to order logic, risk limits, or the manipulation-pattern checks (`COMP-2`) route through a review step visible to compliance, extending `CODEOWNERS`-style review specifically for this category of change.
- **COMP-14 — Trade-relevant communications are captured where required.** If a human or agent communication (e.g., a chat message triggering a manual trade override) leads to a trade, that communication is captured in the same audit trail as the trade itself — extends `META-7`'s override-recording requirement into compliance visibility.
- **COMP-17 — Vendor compliance posture is tracked.** A data or execution vendor's relevant compliance credentials (e.g., SOC 2, applicable licenses) are tracked as part of the same vendor-reconciliation discipline as `DATA-4` — a firm's compliance surface includes its vendors, not just its own code.
