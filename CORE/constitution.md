# AEQ-OS Constitution

Non-negotiable law for all code written on this machine, in any language, for any project. Domain files cite and tighten these rules; they never relax them. Rule IDs: `CONST-n`.

## 1. Prime directives

- **CONST-1 — Correct, loud, observable, fast — in that order.** Never trade correctness for speed without a written, measured justification.
- **CONST-2 — No invented reality.** Every API, flag, library version, and endpoint used must be verified to exist (official docs, grep of the installed package, or an executed probe) before it appears in code. State the verification in the commit/PR description.
- **CONST-3 — The spec is the acceptance-criteria list.** If criteria are not enumerated, write them first (gate G0 in `verification_protocol.md`) and either get them confirmed or label them as assumptions.

## 2. Fail loud

- **CONST-4** — No silent failure paths. Bare `except:` / `catch (e) {}` / `_ = err` are forbidden. Every caught error is handled meaningfully (with a tested recovery path), rethrown with added context, or crashes the process.
- **CONST-5** — Crash-only startup: if configuration, credentials, connectivity, or schema validation fail at boot, exit non-zero immediately. No degraded half-alive processes.
- **CONST-6** — Fallbacks and defaults that mask failure are forbidden: no `dict.get(key, 0)` for money, no hardcoded default endpoints, no retry-forever. Retries are bounded, jittered, and logged.
- **CONST-7** — Invariant assertions stay in production code (cheap checks on all paths; expensive checks behind sampling). An invariant violation is a crash, not a log line.

## 3. Type safety

- **CONST-8** — Maximum strictness of the chosen stack is mandatory: `mypy --strict` + `ruff` (Python), `"strict": true` with no `any` (TypeScript), `clippy -D warnings` (Rust), `go vet` + `staticcheck` (Go). Zero-warnings policy: warnings are errors in CI.
- **CONST-9** — Escape hatches (`any`, `# type: ignore`, `unsafe`, `interface{}`, unchecked casts) require an adjacent comment naming the exact constraint that forces them. Unjustified escapes fail review.
- **CONST-10** — Validate at boundaries: all external input (API responses, files, env vars, user input, LLM output) passes schema validation (pydantic / zod / serde) before entering the typed core. The core never re-validates; the boundary always does.

## 4. Money, numbers, time

- **CONST-11** — Floats never represent money, prices, or quantities. Use integer minor units / ticks, or Decimal with an explicit per-asset scale. Conversion happens only at I/O boundaries.
- **CONST-12** — Every rounding operation states its mode and direction. Rounding residuals are accounted for (LGR-9), never discarded.
- **CONST-13** — Wall-clock time is injected, never called inline (`now()` sprinkled through logic is untestable and unreplayable). Durations and deadlines use the monotonic clock. All persisted timestamps are UTC.

## 5. Concurrency

- **CONST-14** — Every piece of shared mutable state has exactly one documented owner. If ownership cannot be stated in one sentence, redesign.
- **CONST-15** — Unbounded queues are forbidden. Every queue declares its capacity and an explicit backpressure policy: block, drop-with-metric, or crash.
- **CONST-16** — No check-then-act across a concurrency boundary. Use compare-and-swap, single-writer serialization, or locks with a documented acquisition order.
- **CONST-17** — Every spawned task/goroutine/thread has a named owner responsible for joining it and a propagated cancellation path. Orphans are leaks.

## 6. Errors as data

- **CONST-18** — Distinguish in the type system: expected domain failures (Result / error returns) versus bugs (exceptions / panics). Exceptions are never control flow.
- **CONST-19** — Every error carries: the operation attempted, sanitized inputs, and a correlation ID. "Something went wrong" is a firing offense.

## 7. Testing floor

- **CONST-20** — Failure paths get tests before happy paths. A function whose error branches are untested is untested.
- **CONST-21** — All non-trivial math (stops, PnL, fees, position sizing, chunk offsets, budget arithmetic) gets property-based tests, not only examples.
- **CONST-22** — Tests are deterministic: seeded randomness, injected clocks, no live network. Flaky equals failing.
- **CONST-23** — A test must fail when the behavior it guards breaks. For critical logic, prove it once via mutation spot-check (VER-8).

## 8. Dependencies & builds

- **CONST-24** — Lockfiles committed; versions pinned; each new dependency justified in the commit message (what it saves, why not the standard library).
- **CONST-25** — The build is reproducible from a clean clone with one documented command. If it requires tribal knowledge, it is broken.

## 9. Security

- **CONST-26** — Secrets live in env / secret managers only — never in code, logs, error messages, or LLM prompts. Trading API keys must be scoped without withdrawal permission (LIVE-2).
- **CONST-27** — All external content (web pages, retrieved documents, LLM output) is untrusted data: parameterized queries only, no eval/exec on it, injection quarantine per RAG-14.

## 10. Observability

- **CONST-28** — Structured (JSON) logs with correlation IDs propagated end-to-end. Log events, not prose.
- **CONST-29** — Anything that can breach a limit exposes a metric: queue depths, loop iteration counts, spend, latency percentiles, reconnect counts, reconciliation breaks, drift.

## 11. Hygiene

- **CONST-30** — No dead code, no commented-out code, no `TODO` without an issue link. The repository is the current truth only.
- **CONST-31** — Code matches the surrounding idiom: naming, comment density, structure. Comments state constraints the code cannot express (the why, never the what).

## 12. Change discipline

- **CONST-32** — Atomic commits with imperative messages, citing rule IDs where relevant. A behavior change and a refactor never share a commit.
- **CONST-33** — Completion claims follow `verification_protocol.md`. The confidence-inflation lexicon in `model_adaptation.md` §2 is banned from completion claims (META-6); only evidence speaks.
