# Verification Protocol — Quality Gates G0–G4

"Done" is a claim that requires evidence. Gates run in order; a failed gate blocks all later gates. Rule IDs: `VER-n`.

## G0 — Spec gate (before any code)

- **VER-1** — Enumerate acceptance criteria as a checklist before implementation. Each criterion must be *testable* — an outside observer could verify it. Unstated criteria get discovered now, not at review. Record assumptions per META-12.

## G1 — Static gate

- **VER-2** — Clean compile / typecheck / lint at the stack's maximum strictness (CONST-8) with zero warnings. The completion claim includes the exact command and its exit status.

## G2 — Test gate

- **VER-3** — For new logic: failure-path tests first (CONST-20), property-based tests for math (CONST-21), race detector / TSAN / loom for concurrent code (STACK-6/7). The suite passes deterministically **twice in a row**.

## G3 — Runtime gate

- **VER-4** — Execute the real entry path: the app boots, the job runs, the endpoint answers, the backtest completes. Capture command + output. Reasoning about what the code *would* do does not pass G3 — only what it *did* do.

## G4 — Audit gate

- **VER-5** — Self-review the full diff against the constitution. Any rule knowingly bent is cited with its ID and a justification; a silent bend is itself a violation.
- **VER-6** — Banned-pattern battery. Run at the repo root (adapt globs to the project; `grep -rn` if `rg` is unavailable) and expect empty output:

      rg -n "TODO|FIXME|XXX|HACK" src/ --glob '!*test*'          # CONST-30 (issue-linked TODOs excepted)
      rg -n "except\s*:\s*$|except Exception:\s*pass" -t py       # CONST-4
      rg -n ": any\b|as any\b" -t ts src/                         # CONST-9
      rg -n "\.unwrap\(\)|\.expect\(" -t rust src/ --glob '!*test*'  # STACK-7
      rg -n "go func\(\)" -t go | rg -v "owner|group|pool"        # STACK-6, review each hit

- **VER-7** — Ban-lexicon grep (META §2) over the diff **and over the completion message itself**.
- **VER-8** — Mutation spot-check for critical logic (money, stops, auth, budget caps, reward functions): flip one operator or constant, confirm the suite goes red, revert. Record which mutation was tried. A suite that stays green under mutation is decoration, not protection.
- **VER-9** — Evidence table in the completion claim:

      | Criterion | Evidence (command / output / file:line) | Status |
      |-----------|------------------------------------------|--------|

  Statuses are DONE, NOT-DONE, or BLOCKED — rows are never omitted (META-4).

## Meta-rules

- **VER-10** — If any gate fails, report the failure verbatim (CONST-33). Fix and re-run; never reword a failure into a success.
- **VER-11** — For trivial changes (docs, comments, renames with no behavior change), G2/G3 may be waived — the waiver is stated explicitly in the claim. **Code that touches money, live orders, or credentials has no waivers.**
- **VER-12** — Any edit made after the gates ran invalidates them. Gates certify a specific diff, not a session. Re-run from G1.
