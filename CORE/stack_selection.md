# Dynamic Stack Selection Protocol

AEQ-OS mandates no global language. It mandates a **procedure**. Rule IDs: `STACK-n`.

## 1. Procedure

- **STACK-1 — Extract parameters before choosing:** latency budget (p50/p99), throughput, concurrency shape (I/O fan-out vs CPU-bound vs lock-free hot path), ecosystem gravity (which libraries do 80% of the work), deployment target, operator fluency (who runs this at 3 a.m.), interop constraints.
- **STACK-2 — Score at least two candidate stacks** against the parameters. "I am most familiar with X" is an inadmissible argument; "the ecosystem for X does 80% of this work" is admissible.
- **STACK-3 — Write a Stack Decision Record (SDR)** at the project root (`SDR.md` or `docs/SDR.md`) **before the first line of code**. Template in §4.
- **STACK-4 — Polyglot at service boundaries only**, with schema'd contracts (protobuf / JSON Schema / OpenAPI) and one owning language per service. Never two languages inside one process's core logic without an SDR amendment.

## 2. Latency-tier defaults (rebuttable — but only in the SDR)

| Tier | Budget | Default candidates | Hard constraints |
|------|--------|--------------------|------------------|
| T0 — colocated / exchange-adjacent | < 100 µs | Rust, C++ | No GC on hot path; no allocation on hot path; kernel-bypass networking evaluated |
| T1 — low-latency execution | < 10 ms | Rust, Go | Bounded queues everywhere; GC behavior documented and tuned (Go); no reflection on hot path |
| T2 — soft-realtime / streaming | < 250 ms | Go, Rust, JVM (Kotlin) | Backpressure explicit end-to-end |
| T3 — human-time services & tooling | < 2 s | Python, TypeScript/Node, Go | Boundary validation; async task ownership |
| ML/AI loops & research | n/a | Python (+ Rust/C++ extensions for hot kernels) | `mypy --strict` on the pipeline skeleton even if notebooks stay loose |

Routing defaults: trailing-stop engines and order routers are **T1** (T0 if colocated). Agentic orchestration and RAG pipelines are **T3** with T2 ingestion paths. Backtest engines follow the data volume: vectorized Python for research, compiled T1 stack when sharing code with live execution (QT-DET-1).

## 3. Invariant packs (bind on selection — the chosen stack's pack becomes law for the project)

- **STACK-5 — Python:** `mypy --strict`; `ruff` with at minimum E, F, B, ASYNC, S rule groups; `pytest` + `hypothesis` for math; `decimal.Decimal` for money (CONST-11); every `asyncio.create_task` owned by a registry or supervisor with cancellation (CONST-17); lockfile via `uv` or `poetry`.
- **STACK-6 — Go:** `-race` in CI always; `context` cancellation propagated through every call chain; no naked `go func()` — every goroutine has an owner and a shutdown path (CONST-17); `golangci-lint` with `staticcheck` + `errcheck`; money as integer minor units or a documented decimal library.
- **STACK-7 — Rust:** `clippy -D warnings` (pedantic group reviewed, not blanket-allowed); `#![forbid(unsafe_code)]` unless the SDR exempts specific modules, each `unsafe` block carrying a `// SAFETY:` proof; `unwrap()`/`expect()` forbidden outside tests — typed errors with `thiserror`/`anyhow` at the edge; `loom` or equivalent for lock-free structures.
- **STACK-8 — TypeScript:** `"strict": true` plus `noUncheckedIndexedAccess`; `any` forbidden (CONST-9); `zod` at every boundary (CONST-10); ESLint `no-floating-promises`; money as integer minor units or `decimal.js` — never `number`.
- **STACK-9 — Cross-cutting, regardless of stack:** CONST-11 money rules, CONST-15 bounded queues, CONST-22 deterministic tests, CONST-8 zero warnings.

## 4. SDR template

    # Stack Decision Record — <project>
    Date: <YYYY-MM-DD>   Author: <agent + model id>   AEQ-OS: <version>

    ## Parameters
    latency=<budget> throughput=<estimate> concurrency=<shape>
    ecosystem=<decisive libraries> deploy=<target> operators=<who>

    ## Candidates & scores
    <stack A>: <one-line verdict per parameter>
    <stack B>: <one-line verdict per parameter>

    ## Decision
    <stack + key libraries + bound invariant pack STACK-n>

    ## Rejected because
    <per candidate, one honest line>

    ## Revisit trigger
    <the measurable change that reopens this decision>

- **STACK-10** — An SDR that lists only one candidate, or whose rejection lines are hollow ("less suitable"), fails review. The record must show a real decision.
