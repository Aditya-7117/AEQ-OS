# AEQ-OS Benchmark Suite

Real, evidence-based numbers on what loading AEQ-OS actually changes about
a model's output — not asserted, run and scored. Written to the same
standard the rulebook itself asks of code: evidence over assertion
(`VER-9`, `META-6`, `CONST-2`).

## What this measures (and doesn't)

AEQ-OS is a correctness/quality layer, not a speed layer — its own
constitution says "correct, loud, observable, fast, *in that order*." So
this suite does not measure throughput or latency. It measures two things,
kept in explicitly separate tracks so they're never conflated:

1. **Mechanical failure-mode incidence** (`score.py`) — for a fixed set of
   adversarial probe tasks, each designed to tempt a baseline model into
   one specific, *objectively checkable* mistake a rule already names
   (float for money, silently swallowing an exception, an unbounded retry
   loop, a hardcoded secret, and so on) — does loading AEQ-OS context
   change the PASS/FAIL rate. This track is a grep/regex check against the
   actual output, not a judgment call.
2. **Holistic quality rating** (LLM-as-judge, in `report.py`) — a blind,
   cross-model 1-10 rating on overall thoroughness/production-readiness,
   for the broader "does this read as more seriously executed" question
   mechanical checks can't capture. Explicitly labeled subjective
   throughout — a judged opinion, never dressed up as a measured fact.

## Methodology

- **Tasks** (`tasks.json`): 10 short prompts, each tagged with the rule ID
  it probes and a `confidence` label (`strong` = exact/reliable mechanical
  check, `heuristic` = approximate — both reported, never presented as
  equally certain).
- **Conditions:** *baseline* (prompt only) vs. *AEQ-OS-loaded* (prompt plus
  `CORE/constitution.md` + `CORE/security_baseline.md` +
  `CORE/model_adaptation.md` injected as context — the three always-loaded
  files relevant to every task here, mirroring what `BOOT.md`'s protocol
  actually loads for a generic project).
- **Trials:** 3 per task per condition — model outputs are stochastic, so
  this reports a rate, not a single anecdote. Still a modest sample; the
  report says so rather than implying more precision than it has.
- **Judging:** cross-model by construction (a model never judges its own
  output, to avoid self-preference bias) and blind (the judge sees
  "Output A"/"Output B" with randomized assignment, no indication of which
  condition produced which, to avoid a halo effect toward "looks more
  instruction-following").

## Models

- A small free local model via Ollama, pulled *specifically for this
  benchmark* and deleted immediately after — never the user's existing
  large local models (which belong to an unrelated, already
  resource-heavy project and are never touched by this suite).
- Gemini, via `GEMINI_API_KEY` (see Security below).
- **Claude: not called.** No API key, real cost avoided. Instead, the
  report includes a clearly-labeled **prediction** section, reasoned from
  the pattern actually observed across the tested models — never
  presented as a measured result.

## Security — the Gemini key

`GEMINI_API_KEY` is read only via `os.environ`/a local `.env` parser at
runtime inside `harness.py`, never printed, logged, or written to any
output file. Gemini's REST API takes the key as a URL query parameter, so
every error path in `harness.py` deliberately converts exceptions into
pre-written generic messages rather than ever surfacing the raw exception
object or request URL, either of which could carry it. This was verified
programmatically (not just asserted) before any real benchmark run: a
throwaway script called the real API and an intentionally-broken one,
captured all output, and asserted the key value never appeared in it.

## Deference to other local workloads

`harness.py` reuses `scripts/perf/watcher.should_pause()` directly (not a
second copy) before any local-Ollama trial — the same standing rule that
backs the watcher's `--pause-if-pidfile`/`--pause-if-ollama-model` applies
here too: if another RAM-heavy local-model workload is active, the harness
waits rather than competing for memory.

## Running it

```bash
python3 benchmarks/test_score.py                                   # scorer self-test, run first
python3 benchmarks/harness.py --backend ollama:<model> --trials 3
python3 benchmarks/harness.py --backend gemini:<model> --trials 3
python3 benchmarks/report.py --subject ollama:<model> --judge gemini:<model>
python3 benchmarks/report.py --subject gemini:<model> --judge ollama:<model>
```

Raw per-trial outputs land in `benchmarks/results/` (gitignored — local
working data, not a deliverable). `RESULTS-<subject>.md` is the aggregate
report; the top-level `RESULTS.md` is the reviewed, published version.
