# Learning Engine — Mistake Learning & Pattern Promotion

Generalizes `DEP-19`'s "every rollback gets a postmortem that patches a gate" from deploys to every mistake, and gives `memory_governance.md`'s procedural tier its concrete schema. The point is not a diary — it's closing the loop so a mistake made once cannot recur silently a second time. Rule IDs: `LEARN-n`.

## 1. Record schema

- **LEARN-1** — A mistake record is a fixed structure: `{what happened, why it happened, root cause, correct solution, prevention, context/trigger, rule IDs involved, recurrence count}`. All fields are required; a record missing `root cause` or `prevention` is incomplete, not merely terse.
- **LEARN-2 — Root cause, not symptom.** A record stating only the proximate fix ("added a null check") without the causal chain ("what upstream contract allowed the null in the first place") fails the same bar `CONTRIBUTING.md` sets for justifying a new rule — "this seems like good practice" is not sufficient there either.
- **LEARN-3 — No secrets, no PII, no blame.** Records describe the exposure class, never the value, when a mistake involved a secret (`SEC-10`). They describe the failure mode and mechanism, never characterize a user or a prior session's competence — failure modes are named, not judged, the same tone discipline `model_adaptation.md`'s registry already holds.

## 2. Triggers

- **LEARN-4** — Every gate failure (`VER-10`), every user correction of the agent's approach, and every postmortem produces a record before the session ends. This is not optional and not deferred to "if there's time" — `DEP-19` already requires it for deploy rollbacks specifically; this generalizes the requirement to any mistake, in any session.
- **LEARN-5 — Success patterns count too.** A non-obvious approach the user explicitly confirmed worked — not just silently accepted — gets recorded with the same rigor as a mistake. Skipping this means the model regresses toward a worse default the next time the same situation comes up.

## 3. Recall & promotion

- **LEARN-6 — Recall before repeat.** Before starting work in a domain or file with existing records, check them first — the same "grep before you build" discipline `BOOT.md` already applies to rule IDs, applied here to past errors instead of active constraints.
- **LEARN-7 — Pattern promotion.** A mistake recurring twice or more, with the same root cause across different sessions, is a signal the rulebook itself has a gap. Propose a new or tightened rule ID in the relevant `CORE`/`DOMAINS` file, following `CONTRIBUTING.md`'s append-only discipline, rather than trusting the log alone to prevent a third occurrence.
- **LEARN-8 — Scope discipline.** A project-local mistake (a wrong assumption about this specific codebase) stays in project-local episodic memory. A mistake that reveals a general LLM behavior — not a project fact — is a candidate for `CORE/model_adaptation.md`'s `META` registry instead, escalated the same way as `LEARN-7`.
- **LEARN-9** — `LEARN-n` is the general case; `DEP-19`'s deploy postmortem is a specific instance of it. Both share one schema (§1), so a deploy postmortem written to satisfy `DEP-19` is automatically a valid `LEARN` record — no duplicate bookkeeping required.

## 4. What actually prevents recurrence

- **LEARN-10** — The record states what evidence would have caught the mistake earlier — which gate, which test, which rule. This field is the one that actually prevents repetition; the description of the mistake itself is context, not the mechanism.
- **LEARN-11 — An unenforced prevention step is a mistake waiting to recur.** At natural project checkpoints (milestone close, pre-deploy), scan open records for `prevention` items that were logged but never actually wired into a gate, a test, or a rule (`LEARN-7`).

## 5. Format

- **LEARN-12 — Append-only, greppable.** Same convention as rule IDs: never edited to look better in hindsight. A wrong initial diagnosis stays visible, with a follow-up correction entry rather than a silent rewrite.
- **LEARN-13 — Portable format.** Same plain-file, tool-agnostic requirement as `MEM-2`/`MEM-14` — the learning log is not locked to any one agent tool's proprietary memory feature.

## 6. Tiering

- **LEARN-14 — Tier-awareness.** Records live in `memory_governance.md`'s procedural tier and inherit whatever retrieval tier (Lite or Performance) is active for that store — `LEARN` does not define a separate search mechanism of its own.
