# Prompt Engineering — Prompts as Versioned, Tested Artifacts

`AGT-7` states "prompts are code" in one line; this file is what that line actually requires. For most AI engineering work, the prompt is the single artifact touched most often — and the one most often treated as a string literal instead of a reviewed, versioned, regression-tested asset. Loads for any project that constructs, ships, or iterates on LLM prompts (system prompts, tool descriptions, few-shot blocks, structured-output templates). Rule IDs: `PROMPT-n`.

## 1. Prompts as versioned artifacts

- **PROMPT-1** — Every prompt template that ships (system prompts, tool descriptions, few-shot blocks) lives in a versioned file, not a string literal scattered through call sites. A prompt change is a diff with a version bump, same as `AGT-7` requires — the version travels with the transcript logging `AGT-8` already requires, so any output is traceable back to the exact prompt text that produced it.
- **PROMPT-11** — Every prompt template declares which model(s) it's validated against. A prompt tuned for one model's quirks is not assumed portable to another without re-validation — model-specific prompt engineering is real, and an undisclosed portability claim is a form of confidence inflation (`META-6`).
- **PROMPT-13** — A prompt's changelog entry states what failure mode motivated the change, mirroring this repo's own `CONTRIBUTING.md` standard: justify by the failure mode closed, not "this seems better." A prompt change with no stated reason doesn't ship.
- **PROMPT-14 — Rollback path.** A prompt version that regresses in production has a one-line revert; the prior version stays retrievable (git history or an explicit version registry), never overwritten in place.

## 2. Change & regression discipline

- **PROMPT-2** — Prompt changes get regression-tested before shipping, against the same golden-task suite an eval-worthy change would run (`ai_evaluation.md`, when loaded) — a prompt diff is a behavior change, and `CONST-32` already forbids landing a behavior change without evidence it does what's intended.
- **PROMPT-3** — A/B or before/after comparison is mandatory for any change to a production system prompt: run both versions against the same task set and compare failure rates, not impressions. "The new wording feels clearer" is not evidence (`META-6`).

## 3. Few-shot example curation

- **PROMPT-4** — Few-shot examples are versioned alongside the prompt they belong to, sourced from real (or realistic, clearly labeled synthetic) cases — never fabricated to look plausible without being checked against ground truth. `CONST-2`'s no-invented-reality standard applies to examples, not only to APIs.
- **PROMPT-5** — Few-shot sets are audited for drift: an example added to patch one failure mode can silently bias behavior on unrelated inputs. A new example is tested against the existing eval set, not only the case it was added to fix.
- **PROMPT-6** — Example count and ordering are deliberate, documented choices — recency and position bias in few-shot prompting are real and measurable — not accumulated ad hoc until someone notices the prompt got long.

## 4. Template construction & injection safety

- **PROMPT-7** — Template construction never string-concatenates untrusted input directly into an instruction-bearing position. User input, retrieved documents, and tool output are all untrusted (`SEC-13`) — they populate clearly delimited data slots, never the instruction scaffold around them.
- **PROMPT-8** — A prompt-injection test is part of the regression suite for any prompt that ingests untrusted content: known injection patterns (instruction-override attempts, role-play jailbreaks, delimiter-breaking payloads) are exercised, and must not change the model's tool-use scope or safety behavior.
- **PROMPT-16** — Prompts that assemble multiple sources (system instructions, retrieved context, conversation history, tool results) declare and test the precedence order when sources conflict — the same "no silent averaging of two readings" standard `META-15` sets for ambiguous user requests, applied here to prompt assembly.

## 5. Context budget

- **PROMPT-9** — Context-window budget is a first-class, versioned constraint per prompt, distinct from `AGT-1`'s dollar budget: state the target model's context limit, the reserved headroom for the response, and what gets truncated first, and how, when input exceeds budget. Silent truncation that cuts mid-instruction is forbidden.
- **PROMPT-10** — Long-context prompts (system prompt + tool defs + few-shot + retrieved context) are position-tested: critical instructions are not left where "lost in the middle" effects are known to degrade recall — restructure or move them up rather than trust position alone.

## 6. Output handling & disclosure

- **PROMPT-12** — Structured-output prompts (JSON mode, function-calling schemas) validate the model's own output against the declared schema before it enters program state — `CONST-10`'s boundary-validation requirement applied specifically to LLM output, the same discipline `AGT-12` already requires.
- **PROMPT-15** — Secrets, internal rule IDs, and system-only instructions never leak verbatim into a response meant for an end user unless explicitly and intentionally surfaced. A prompt that references this rulebook's own vocabulary internally must ensure that vocabulary doesn't leak into user-facing prose untranslated — this exact failure mode was observed directly in this project's own benchmark run (see `ai_evaluation.md`).
