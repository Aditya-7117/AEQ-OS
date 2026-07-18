# Contributing to AEQ-OS

AEQ-OS is a set of instruction files, not application code — but the review bar is the same one it asks agents to hold themselves to: every claim needs evidence, every rule needs a reason.

## Before you open a PR

1. Run the validator locally:

       python3 scripts/validate.py

   It checks `ROUTER_MAP.json` validity and path references, rule-ID contiguity (no gaps, no accidental renumbering), and the banned-lexicon list. CI runs the same script — a PR that fails it won't be reviewed until it passes.

2. If you're changing `DOMAINS/live_trading_gate.md`: state explicitly, in the PR description, that no PASS criterion was weakened. This file has no user-override by design (`META-7`) — changes to it get the highest scrutiny in this repo.

## Adding a rule to an existing file

- Append after the current highest number for that prefix. IDs are never renumbered and never reused, even for rules that get superseded — mark a superseded rule `[DEPRECATED — see PREFIX-n]` instead of deleting it, so old citations in commit history and code comments still resolve.
- State the failure mode the rule closes. "This seems like good practice" is not sufficient justification — cite the concrete scenario ("a receding trailing stop widens risk silently" for `QT-STOP-3`, for example).
- Keep the same register as the surrounding file: terse, imperative, ID-citable. A rule that takes three sentences to state usually wants splitting into two rules.

## Adding a new domain file

Open a **New domain proposal** issue first (template provided) — new rule-ID prefixes are a bigger surface than a single rule, and the router wiring benefits from discussion before code. See `ROUTER_MAP.json`'s `routes` array for the shape a new route takes, including how it composes with existing routes via the `combination_examples`.

## Style

- Every rule gets a stable ID: `PREFIX-n`, bold at its definition site (`- **CONST-1** — ...`) or as the leading cell of a table row (the failure-mode registry in `model_adaptation.md` is the template) — the validator only counts definitions in one of those two forms.
- Cite other rules by ID in parentheses, not by re-explaining them: `(CONST-16)` not "per the check-then-act rule."
- No hedging language. `CORE/model_adaptation.md` §2 lists the specific banned phrases; the validator enforces it.

## What won't get merged

- A rule that only says "be careful" or "make sure it's correct" without a mechanical test for compliance (grep pattern, gate, or checklist item).
- A weakened `live_trading_gate.md` criterion, for any reason, including "this makes onboarding easier."
- Style-only rewrites that don't change what an agent would actually do differently.
