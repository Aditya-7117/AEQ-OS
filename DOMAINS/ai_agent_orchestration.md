# AI Agent Orchestration — Domain Invariants

For agentic systems: LLM loops, tool-using assistants, multi-agent pipelines, RL training and serving. Rule IDs: `AGT-n`.

## 1. Monetary budget caps — hard, in code, pre-dispatch

- **AGT-1** — Every run/session/day has a currency-denominated ceiling enforced by a metering layer that computes tokens × price (versioned price table) plus tool costs **before dispatching each call**. At 80%: warn and apply the degrade policy if one is defined (cheaper model, smaller context). At 100%: hard stop mid-task, checkpoint state, surface partial results. There is no "finish the current thought" grace call.
- **AGT-2** — Spend posts to the dual-entry ledger schema (`financial_audit_ledger.md` §6) with attribution `{run_id, agent_id, task_id, model, tokens_in, tokens_out}`. Budget reports reconcile to provider invoices monthly; breaks are investigated like LGR-12 breaks.
- **AGT-3** — Price tables and model IDs are reviewed config commits, never hardcoded at call sites. A model swap is a diff, not an edit-in-place.

## 2. Loop & recursion protection

- **AGT-4** — Every loop has ALL three: a max-iteration bound, a wall-clock timeout, and a **progress predicate** — a defined state-diff metric (files changed, tests passing, plan items completed). Three consecutive iterations without progress → halt with a `NO_PROGRESS` report. Silent continuation is forbidden.
- **AGT-5** — Agent-spawns-agent has a depth cap and a global concurrent-agent cap. Every inter-agent message carries a hop TTL; TTL exhaustion terminates the exchange. This is what kills two agents politely ping-ponging forever.
- **AGT-6** — An identical tool call (same tool, same arguments, same target state) repeated three times is a loop signature → halt. Bounded backoff retries are exempt only for idempotent reads failing with transient errors.

## 3. Determinism & replay

- **AGT-7 — Prompts are code:** versioned files, reviewed diffs, changelog. No inline prompt-string hotfixes without a version bump.
- **AGT-8 — Full transcript logging:** every model call records `{prompt_version, model_id, params (temperature/seed), input_hash, output, tool_calls, latency, cost}`. A run is replayable from its transcript alone.
- **AGT-9** — Evaluation runs pin temperature, seed, and model snapshot where the provider allows. Eval numbers without pinned config are not comparable and may not be cited.
- **AGT-10** — Side-effecting tools require idempotency keys; a retry never double-executes (payments, orders, sends, deletes). Non-idempotent tools without keys may not be auto-retried — escalate instead.

## 4. State management

- **AGT-11** — Agent state is an explicit, typed state machine persisted at checkpoints — never implicit in conversation history alone. Resume-from-checkpoint is a tested path: kill the run mid-task in CI, resume, verify equivalence.
- **AGT-12** — Every LLM output that enters program state passes schema validation (CONST-10). Free text goes through typed extraction with a bounded retry budget, then escalates — never `json.loads` and hope.

## 5. Reinforcement learning state rules

- **AGT-13** — Transitions `(s, a, r, s', done, info)` append to an immutable log carrying the environment seed and version. Training datasets are reconstructible byte-identically; replay buffers are checksummed.
- **AGT-14** — Reward functions are versioned and unit-tested, including **anti-hacking probes**: known degenerate policies (do-nothing, oscillate, self-collude, exploit-the-metric) must score poorly, by test. Reward is bounded; an unbounded reward function is a NO-GO.
- **AGT-15** — Train/eval environment parity is documented; every wrapper (observation normalization, frame skip, action repeat) is config, not code drift. Evaluation uses held-out seeds only.
- **AGT-16** — Nondeterminism sources (GPU kernels, parallel rollouts) are enumerated. Where exact replay is impossible, statistical replay bounds are defined and tested instead of shrugged at.

## 6. Multi-agent orchestration

- **AGT-17** — A supervisor owns the lifecycle: spawn, budget hand-down (children's budgets sum to ≤ the parent's remaining budget), timeout, kill, and result validation. Orphan agents are leaks (CONST-17 applied to agents).
- **AGT-18** — Inter-agent messages have typed schemas; consumers validate (AGT-12). One agent's crash cannot corrupt shared state: mutations flow through the supervisor or a transactional store, never direct shared-memory scribbling.
- **AGT-19** — Irreversible actions — spend above threshold, deletes, external sends/publishes, live orders — require an allowlist entry or human approval. The allowlist is config under change control, not a constant in the code.

## 7. Quality & regression

- **AGT-20** — A golden-task eval suite runs on every prompt, model, or orchestration change; regressions block merge exactly like failing tests. Eval sets are versioned with lineage (see RAG-11 for the retrieval analog).
