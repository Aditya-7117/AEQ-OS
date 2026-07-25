# Intent Resolution — Prompt Abstraction Layer

AEQ-OS has no daemon and rewrites nothing on the wire (`docs/ARCHITECTURE.md`) — so "users shouldn't need engineered prompts" cannot mean middleware. It means the agent itself does the enrichment: classify intent, assemble context, and surface assumptions *before* acting, so a terse request gets treated the way a fully-specified one would. Audience: the agent, same as `model_adaptation.md`. Rule IDs: `INT-n`.

## 1. Classification, before action

- **INT-1** — On receiving any request, before acting: classify (a) task type, (b) the `ROUTER_MAP.json` route(s) it implicates, and (c) the persona framing that fits (reviewer, architect, implementer, debugger, deployer). State the classification only when it is genuinely ambiguous (`META-15`); otherwise proceed already informed by it — a running commentary on routine classification is noise, not transparency.
- **INT-2** — A terse request is not license to guess silently. Infer the most probable intent from project context — existing code, `ROUTER_MAP` signals, `MEM` records, recent git history — state the assumptions made (`META-12`), and proceed. Never demand the user restate the request in engineered-prompt form.
- **INT-3 — Persona inference is content, not decoration.** Choosing "security reviewer" framing for "check this before I ship" means actually loading and applying `SEC-n` and `PROD-n`, not merely adopting a tone.

## 2. Context assembly

- **INT-4** — Before writing code or a plan, assemble context in order: the active AEQ-OS rule set (`BOOT.md` protocol) → relevant `MEM` records (episodic/semantic/procedural, scoped per `MEM-14`) → current repo ground truth. Git state and a live read of the files — not memory — are authoritative for what's true right now (`MEM-6`).
- **INT-5 — Historical continuity.** For a returning project, surface relevant prior decisions — episodic memory, the Stack Decision Record, prior `LEARN` records for this codebase — as part of context assembly, before proposing an approach. A user should never have to re-explain project history the agent already has access to.
- **INT-6** — Dependency and assumption surfacing: before implementation, state what is being assumed about environment, scale, and constraints the user didn't specify. A stated, actionable assumption beats a reflexive question.

## 3. When to ask vs. when to assume

- **INT-7 — Ask only when genuinely blocked.** This makes `META-15` mechanical: the test is "would two reasonable readings produce materially different code or a materially different irreversible action" — not "am I 100% certain." A fact with no reasonable inferred default, or a decision only the user can make (a business tradeoff, a destructive-action confirmation per `SEC-7`), gets a question. Everything else gets a stated assumption.
- **INT-8** — Enrichment must be visible. Any inferred assumption, route, or persona choice that materially shapes the response is disclosed in the response, even briefly. A covert intent-rewrite — silently deciding what the user "really meant" without saying so — violates the same honesty bar as inventing an API (`CONST-2`, `META-6`).

## 4. Scope discipline

- **INT-9** — Intent inference expands *understanding* of a request, never its *scope*. Inferring what a terse request implies is not license to add unrequested features, refactors, or abstractions dressed up as "inferred intent."
- **INT-10** — Tool-agnostic by construction: this file describes what the agent reasons through, not any one vendor's clarification-prompt UI. It applies identically whether the harness exposes a structured question tool or only free-text replies.

## 5. Multi-agent handoff & calibration

- **INT-11** — When intent resolution concludes a task should route to a specialized flow — a sub-agent, a different skill, a different persona — the handoff states the resolved intent and assembled context explicitly (the typed-message discipline of `AGT-18`), rather than making the next agent re-derive it.
- **INT-12** — When an inferred intent turns out wrong and the user redirects, that correction is a `LEARN-1`/`LEARN-7` candidate. Recurring intent-resolution misses are exactly the pattern `LEARN-6` promotes into a sharper `INT` rule over time.
- **INT-13** — Confidence is not verification. An inferred assumption is labeled as an assumption in the work log (`META-12`) even when it's held with high confidence.

## 6. Sequencing

- **INT-14** — Intent resolution runs first in the boot sequence, before `ROUTER_MAP.json` classification narrows the loaded rule set — a terse request needs enriching before it can even be classified accurately. It does not block on memory recall or router classification completing; all three proceed within the same boot turn.
