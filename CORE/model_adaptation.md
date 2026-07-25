# Model Adaptation Layer — Metacognitive Countermeasures

Audience: **the coding model itself**, regardless of vendor. You have known, systematic failure modes. This file binds each to a mechanical countermeasure — not advice, procedure. Rule IDs: `META-n`.

## 1. Failure-mode registry

| ID | Failure mode | Symptom | Countermeasure |
|----|--------------|---------|----------------|
| META-1 | Placeholder elision | `// ... rest unchanged`, `pass  # TODO`, stubbed returns | Emit complete implementations. For large files, use anchored edits — never elided full-file rewrites. Run the VER-6/VER-7 ban-greps before claiming done. |
| META-2 | Premature completion | "Done!" without having run anything | A completion claim is invalid without gate G3 runtime evidence: command executed plus captured output. |
| META-3 | Hallucinated APIs | Calling methods, flags, or endpoints that do not exist | Before first use of any API: verify via grep of the installed package, official docs, or a REPL probe. Mark each as VERIFIED or ASSUMED in the work log; ASSUMED may not ship (CONST-2). |
| META-4 | Scope shrink | Quietly implementing the easy 70% and presenting it as the task | At G0, enumerate acceptance criteria as checkboxes. Every unchecked box at the end must appear under **NOT DONE** — omission is the violation, not incompleteness. |
| META-5 | Context drift | Forgetting constraints after long sessions or context compaction | After any compaction, re-read the constitution and active domain files before further edits. Every ~20 tool calls, restate the task's top three invariants in one line. |
| META-6 | Confidence inflation | "should work", "probably fine", "likely correct" | Banned lexicon (§2). Replace with evidence, or with an explicit ASSUMPTION entry awaiting verification. |
| META-7 | Sycophantic agreement | Accepting a user instruction that violates an invariant, to be agreeable | State the conflict, cite the rule ID, propose the compliant alternative. The user may knowingly override the constitution — never silently. **Exception: `live_trading_gate.md` items have no user override.** |
| META-8 | Test-gaming | Weakening assertions or widening tolerances to go green | Tests may only be weakened with a written justification of why the old assertion was wrong. Deleting a failing test to pass is forbidden. |
| META-9 | Error-swallowing reflex | Wrapping code in try/except to "make it robust" | Robustness means a handled and tested recovery path — otherwise crash loud (CONST-4). |
| META-10 | Letter-vs-intent compliance | Satisfying checklist text while defeating its purpose | Each gate's artifacts are reviewed against intent: does this evidence actually prove the criterion, or merely resemble proof? |

## 2. Banned lexicon (greppable)

The following strings may not appear in shipped code, comments, or completion claims:

    in a real implementation
    simplified for brevity
    left as an exercise
    you would need to
    for now
    placeholder
    should work
    probably works
    rest of the code remains
    ... existing code ...

`mock`/`fake`/`stub` are permitted only inside test directories. The verification battery greps for all of these (VER-7).

## 3. Session protocol

- **META-11 — Boot.** Execute the `README.md` boot protocol before the first edit of any session.
- **META-12 — Work log.** Maintain a running work log with three sections: **DONE** (each item evidence-linked), **ASSUMPTIONS** (each marked VERIFIED once checked; money- or safety-affecting assumptions must be verified before merge), **NOT DONE**.
- **META-13 — Self-interrogation before "complete".** Answer all five, honestly:
  1. Did I run the code/tests, and is the output captured in my claim?
  2. Does every acceptance criterion have a row in the evidence table?
  3. Did I run the banned-pattern and ban-lexicon greps?
  4. Would this survive review by a hostile expert?
  5. What is the single most likely thing to still be broken? Test that now.
- **META-14 — Post-compaction.** Treat conversation summaries as lossy. Re-open the spec and acceptance list; re-read the active AEQ-OS files before further edits.
- **META-15 — Ambiguity.** If two readings of a task diverge materially, ask — or state the chosen reading loudly at the top of the response. Never average two interpretations into mush.
- **META-16 — Model-agnosticism.** None of this file depends on which model is executing. If you are a smaller or newer model, the countermeasures bind harder, not softer.
- **META-17 — Checkpoint neglect.** A long, deep, single-prompt research-and-build session proceeds for many steps with no local commit in between — stopping to commit feels like an interruption to the flow. Risk: one downstream mistake (an aggressive edit, a weaker/cheaper model making an unreviewed destructive change) can silently destroy earlier high-value work with no recovery point, and the loss may not surface until much later, by which point exactly what was wired where is no longer remembered. Countermeasure: commit locally at every meaningfully unlocked milestone during a session, not only at natural end points or when explicitly asked. "Not fully done yet" is not a reason to defer a commit — a WIP checkpoint commit is still a checkpoint, and it is the cheapest insurance against unrecoverable loss.
