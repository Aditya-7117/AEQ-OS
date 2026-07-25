# AEQ-OS Benchmark Results

Real, measured numbers on what loading AEQ-OS actually changes about a
model's output — not asserted, run and scored. See `README.md` for full
methodology.

**Models tested:** `qwen2.5-coder:7b` (free, local, pulled specifically for
this run and deleted immediately after each run — see Models below) and
`gemini-2.5-flash` (cloud, via API). **Claude: not tested** — no API key,
real cost avoided; see the predicted section at the bottom, clearly marked
as a prediction, not a result.

**Sample size:** 10 tasks × 5 trials × 2 conditions × 2 models = 200
generation trials, plus 100 blind cross-model judge calls. Larger than the
first run (3 trials) specifically to reduce single-trial noise — read
percentages as indicative, not definitive; several task-level cells still
move by 20 percentage points per flipped trial.

## This is a revised run — here's exactly what changed and why

The first run of this benchmark showed a **flat-to-slightly-negative**
mechanical result (qwen: 63%→60%, Gemini: 80%→79%) alongside a
consistently positive judged-quality result. Investigating the mechanical
result surfaced a real bug: the `unjustified-any` scorer flagged
TypeScript's idiomatic `catch (e: any)` — a standard pattern for catching
thrown errors — as if it were the lazy signature-level `any` `CONST-9`
actually targets. The AEQ-OS condition wrote more self-test code (more
`catch` blocks), so it got penalized for being more thorough. Two
independent blind judges had already rated those exact outputs as clearly
better, which is what prompted the investigation.

**The fix was scoped and applied before this re-run, not after seeing what
it would do to the topline number** — verified with a new unit test
(`benchmarks/test_score.py`) proving the exclusion is precise: a bare
`payload: any` on a function signature still fails, only the catch-clause
pattern is excused. Re-scoring the *original* run's raw outputs with the
fixed scorer (no new model calls) showed a small, real, honest shift —
Gemini's mechanical delta moved from -1% to +2%, qwen's stayed flat at
-3% — proof the fix wasn't a swing either direction on its own. This run
adds a genuinely larger sample (5 trials, not 3) on top of that fix. Both
changes are disclosed, not just the one that happened to produce a bigger
number.

## TL;DR

- **Mechanical failure-mode incidence (Track 1): now positive for both models** — `qwen2.5-coder:7b` 62%→66% (**+4%**), `gemini-2.5-flash` 74%→88% (**+14%**). Not every task moved positively — see the honest exceptions below.
- **Holistic quality rating (Track 2, blind, cross-model judged): consistently positive, and stronger with more data** — +2.1/10 (Gemini judging qwen, up from +1.5 in the first run) and +0.8/10 (qwen judging Gemini, up from +0.5).
- **Two tasks still show real negative deltas, disclosed, not hidden:** `unjustified-any` for qwen (-60%, even after the scorer fix — this model's outputs do contain additional unjustified `any` usage beyond the catch-clause pattern) and `ambiguity-handling` for both models (qwen +20%, Gemini **-40%** — this is `META-15`'s task, already labeled `heuristic` confidence, the weakest scorer of the ten; both runs show it's noisy).

## Track 1 — Mechanical (objective, PASS/FAIL against a named rule ID)

| Model | Baseline overall | AEQ-OS overall | Delta |
|---|---|---|---|
| `qwen2.5-coder:7b` | 62% | 66% | **+4%** |
| `gemini-2.5-flash` | 74% | 88% | **+14%** |

Full per-task tables: [`RESULTS-ollama-qwen2.5-coder_7b.md`](RESULTS-ollama-qwen2.5-coder_7b.md), [`RESULTS-gemini-gemini-2.5-flash.md`](RESULTS-gemini-gemini-2.5-flash.md).

Strongest, most consistent positive findings across both models: **`money-float` (`CONST-11`)** — both models went from 0% (never used `Decimal`) to 100% (always did) with AEQ-OS context loaded, reproduced identically across both runs. **`hardcoded-secret` (`CONST-26`)** and **`missing-boundary-validation` (`CONST-10`)** also moved strongly positive for qwen (+60%, +40%) and stayed at or near ceiling for Gemini.

Honest negative findings, not hidden: **`unjustified-any`** stayed negative for qwen (-60%) even with the scorer fix — manual inspection (see the note above) shows the fix removed the catch-clause false positives, but this model's outputs still contain genuine unjustified `any` elsewhere; this is a real finding about the model, not a scorer artifact this time. **`ambiguity-handling`** is volatile and net-negative for Gemini (-40%) — the weakest-confidence task in the suite by design (`heuristic` label), and the one place these numbers should be trusted least.

## Track 2 — Holistic quality rating (subjective, blind, cross-model judged)

| Subject | Judge | Baseline avg | AEQ-OS avg | Delta |
|---|---|---|---|---|
| `qwen2.5-coder:7b` | `gemini-2.5-flash` | 6.2/10 | 8.3/10 | **+2.1** |
| `gemini-2.5-flash` | `qwen2.5-coder:7b` | 7.8/10 | 8.6/10 | **+0.8** |

Consistent in both directions, and larger than the first run's +1.5/+0.5.
Judges independently cite the same things across nearly every trial: more
explicit error handling, input validation (frequently via a properly
justified dependency like `zod`, not manual checks), structured logging,
and self-written test cases in the AEQ-OS condition. Full per-trial
reasoning: same two files linked above.

## ⚠ Predicted — not measured (Claude models)

**No Claude API call was made.** No key, and the cost was explicitly
declined. The estimate below is reasoned from the two real patterns
observed above, not a measurement, and is presented as a range with low
confidence throughout.

Observed across both tested models: mechanical delta clearly positive
(+4% to +14%), judged-quality delta consistently positive and larger with
more data (+0.8 to +2.1/10).

**Reasoning:** Claude models are generally more RLHF'd toward the
*generic* best practices several of these tasks probe (bounded retries,
not swallowing exceptions), so baseline pass rates on those specific items
are plausibly already higher than the models tested here — meaning the
*absolute* mechanical delta for Claude may be smaller on the generic
items. But AEQ-OS's own non-generic conventions (exact rule IDs, the
ledger's dual-entry schema, G0-G4 gate vocabulary) cannot be "already
known" by any model without being told — so a nonzero effect there is
still a reasonable hypothesis, and the judged-quality pattern (more
validation, more tests, more structured error handling) seems more likely
to generalize than any single mechanical task.

- **Predicted mechanical delta for Claude: positive but smaller than observed here, plausibly +3% to +10%** — likely closer to the low end given a stronger generic-practice baseline, but the AEQ-OS-specific items should still move it.
- **Predicted judged-quality delta: plausibly +0.3 to +1.2/10** — smaller than the free-model deltas above (less headroom on a stronger baseline), same direction.
- **The `ambiguity-handling` volatility observed here is plausibly still present with Claude** — it's a scorer-confidence issue (heuristic, not strong), not obviously a model-capability issue that a stronger model would fix on its own.

**Confidence: low.** Two data points, both free/cheap models, is not
enough to predict a materially different model family with real
precision. Treat this as a hypothesis for a future real test, not a claim
about Claude's actual behavior.

## Models

- `qwen2.5-coder:7b` — pulled specifically for this benchmark (twice — once
  per run), used for both generation and judging, then deleted (`ollama rm`)
  immediately after each run's judging completed. Verified removed both
  times; the user's existing `qwen3:32b`/`deepseek-r1:32b` (unrelated,
  another project's) were never touched, verified before and after both
  runs.
- `gemini-2.5-flash` — via `GEMINI_API_KEY`, handled per the security
  protocol in `README.md`. 200/200 generation trials succeeded this run (the
  first run had 2 transient, sanitized connection errors out of 60 — none
  recurred).
