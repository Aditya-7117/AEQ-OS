## What this changes

<!-- One or two sentences: which file(s), what rule(s), why. -->

## Rule IDs touched

<!-- New: NEW-PREFIX-n · Modified: PREFIX-n, PREFIX-m · (list every one — reviewers grep for these) -->

## Why this rule is correct

<!-- The failure mode this closes, or the gap it fills. If it tightens an
     existing rule rather than adding a new one, say what broke without it. -->

## Checklist

- [ ] `python3 scripts/validate.py` passes locally
- [ ] New rule IDs are appended after the current max for their prefix (never renumbered, never reused)
- [ ] `ROUTER_MAP.json` updated if this file should load under a route that doesn't already include it
- [ ] No banned-lexicon phrases introduced (see `CORE/model_adaptation.md` §2)
- [ ] If this changes `DOMAINS/live_trading_gate.md`: explicitly confirms no PASS criterion was weakened
