# AI Evaluation — Golden Datasets, Judged Scoring, Honest Disclosure

Eval concerns already exist scattered across this rulebook — `AGT-20`'s golden-task suite, `RAG-11`'s lineage, `RESEARCH-*`'s overfitting guards, `MDL-*`'s promotion criteria — but no file until now treats evaluation itself as a first-class discipline with its own failure modes. This one is not written from the abstract: it is distilled directly from building this repo's own `benchmarks/` suite, including a scorer bug found and disclosed rather than quietly patched away, and a surprising result reported exactly as measured. Loads for any project that evaluates prompts, agents, retrieval pipelines, or models — not only research contexts. Rule IDs: `EVAL-n`.

## 1. Golden datasets

- **EVAL-1** — Every AI feature (prompt, agent, retrieval pipeline) ships with a golden-task evaluation set before it ships to production — extends `AGT-20`'s "a golden-task eval suite runs on every prompt/model/orchestration change" from a regression check into a standing requirement.
- **EVAL-2** — Golden tasks are versioned with lineage, generalizing `RAG-11`'s convention beyond retrieval specifically: an eval number is only comparable to another eval number run against the same task-set version.
- **EVAL-3** — Golden tasks are adversarial by design wherever they can be — chosen to probe named failure modes (this rulebook's own `META` registry, or a project's own failure history via `LEARN-n`), not only typical happy-path cases that pass by default and tell you nothing.

## 2. Mechanical vs. judged scoring — never conflated

- **EVAL-4** — Mechanical scoring (objective, deterministic, reproducible — a grep, a schema check, an exact match) and model-judged scoring (subjective, LLM-as-judge) are two separate tracks, reported separately, never averaged or blended into one number. A judged opinion is not a measurement, and presenting it as one is a form of confidence inflation (`META-6`).
- **EVAL-5** — A judge model never judges its own output. Self-preference bias is a documented, measurable effect — cross-model judging (or a separate, disinterested rubric-based check) is mandatory wherever an LLM-as-judge step exists.
- **EVAL-6** — Judged comparisons are blind: the judge sees unlabeled candidates (e.g. "Output A" / "Output B" with randomized assignment), never which condition or model produced which. Labeling upfront invites a halo effect toward whichever output merely looks like it followed more instructions, independent of actual quality.
- **EVAL-7** — A judge's rubric is fixed and stated before judging begins, not adjusted after seeing results. Rubric criteria are specific and checkable ("error-handling depth," "correctness confidence") rather than a bare "rate 1-10."

## 3. Honesty under a disappointing result

- **EVAL-9** — A surprising or unflattering result gets investigated and disclosed with the evidence that explains it — never silently discarded, never re-run until favorable, and never used as grounds to retroactively adjust the scoring methodology after the fact. If the scoring method itself turns out to be flawed, the fix is disclosed alongside the original result and the reasoning that motivated it, and takes effect prospectively on the next run — never applied backward just to make an inconvenient number disappear.
- **EVAL-10** — A scorer's known limitations are documented in the same place the results are reported, not buried in a code comment only a maintainer will find. "This mechanical check has a known false-positive pattern on X" belongs next to the number it affects, not three files away.
- **EVAL-8** — Sample size is stated plainly next to every reported rate or score, with the practical consequence spelled out (e.g. "3 trials means a single flipped result moves the rate by 33 points"). A percentage without its denominator is not evidence, it's decoration.
- **EVAL-14** — Eval reports state exactly which models were tested and which were not. A claim about an untested model's likely behavior is clearly labeled as a prediction, never presented with the confidence of a measured result, and carries its own stated confidence level.

## 4. Regression gating

- **EVAL-11** — A prompt, model, or pipeline change that drops the golden-task pass rate blocks merge exactly like a failing unit test (`AGT-20`; `DEP-7`'s eval-regression-blocks-deploy extended to the eval step itself). An explained regression still requires a stated, reviewed justification before it ships — the same discipline `META-7` already requires for knowingly bending any other rule.

## 5. Eval infrastructure is held to the same bar as production code

- **EVAL-12** — Eval infrastructure defers to other RAM/compute-heavy local workloads exactly like any other local process (`SEC-18`/`MEM-15`'s tier-awareness pattern) — an eval run using local models checks for and waits on other active local-model work rather than competing for resources silently.
- **EVAL-13** — Any model, dataset, or tool pulled specifically to run an evaluation and not otherwise needed is removed after the run completes, and its removal is verified. An eval run is not a license to accumulate disk or resource debt.
- **EVAL-15** — Cost and time budget for an eval run is stated up front — API spend, wall-clock time, local compute. `CONST-1`'s "correct, loud, observable, fast, in that order" applies to evals too: correctness of the measurement comes before speed of getting a number.
- **EVAL-16** — An eval harness's own code is held to the same bar as production code: no bare `except`, no hardcoded secrets, no silent failure on a malformed model response. An untested eval harness produces untrustworthy eval numbers regardless of how rigorous the methodology looks on paper.
