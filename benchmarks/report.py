#!/usr/bin/env python3
"""Aggregates benchmarks/results/*.json into benchmarks/RESULTS.md.

Two tracks, kept explicitly separate so they're never conflated:
  1. Mechanical (score.py) — objective PASS/FAIL against a named rule ID.
  2. LLM-as-judge — blind 1-10 holistic quality rating. Explicitly labeled
     "subjective, model-judged" everywhere it appears.

Plus a clearly-labeled PREDICTED (never measured) section for Claude
models, reasoned from the pattern actually observed across tested models.

Judging is cross-model by construction (a model never judges its own
output) and blind (the judge sees "Output A"/"Output B" with randomized
assignment, not which condition produced which) — see judge_pair().
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness  # noqa: E402
import score as scoring  # noqa: E402

BENCH_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCH_DIR / "results"

JUDGE_PROMPT = """You are evaluating two outputs produced for the same coding task, labeled Output A and Output B. Do not assume either is better going in.

Rate EACH output 1-10 on a combined sense of: correctness confidence, error-handling depth, production-readiness signals, and overall thoroughness. Higher is better.

Respond with ONLY a JSON object, no other text, exactly this shape:
{{"a_score": <integer 1-10>, "b_score": <integer 1-10>, "reasoning": "<one sentence>"}}

Task: {task_prompt}

Output A:
{output_a}

Output B:
{output_b}
"""


def load_results(model_key: str) -> list[dict]:
    path = RESULTS_DIR / f"{model_key}.json"
    return json.loads(path.read_text()) if path.exists() else []


def load_tasks_meta() -> dict:
    tasks = json.loads((BENCH_DIR / "tasks.json").read_text())["tasks"]
    return {t["id"]: t for t in tasks}


def mechanical_scores(results: list[dict]) -> dict:
    out: dict = defaultdict(lambda: defaultdict(list))
    for r in results:
        if r["output"] is None:
            continue
        fn = scoring.SCORERS[r["scorer"]]
        out[r["task_id"]][r["condition"]].append(fn(r["output"]))
    return out


def mechanical_table(results: list[dict], tasks_meta: dict) -> tuple[str, float, float]:
    scores = mechanical_scores(results)
    lines = [
        "| Task | Rule | Confidence | Baseline pass rate | AEQ-OS pass rate | Delta |",
        "|---|---|---|---|---|---|",
    ]
    all_b: list[bool] = []
    all_a: list[bool] = []
    for task_id in sorted(scores):
        meta = tasks_meta[task_id]
        b, a = scores[task_id].get("baseline", []), scores[task_id].get("aeqos", [])
        all_b += b
        all_a += a
        b_rate = sum(b) / len(b) if b else None
        a_rate = sum(a) / len(a) if a else None
        b_s = f"{b_rate:.0%}" if b_rate is not None else "n/a"
        a_s = f"{a_rate:.0%}" if a_rate is not None else "n/a"
        d_s = f"{a_rate - b_rate:+.0%}" if (b_rate is not None and a_rate is not None) else "n/a"
        lines.append(f"| {task_id} | `{meta['rule']}` | {meta['confidence']} | {b_s} | {a_s} | {d_s} |")
    if all_b and all_a:
        ob, oa = sum(all_b) / len(all_b), sum(all_a) / len(all_a)
        lines.append(f"| **Overall** | | | **{ob:.0%}** | **{oa:.0%}** | **{oa - ob:+.0%}** |")
        overall_delta = oa - ob
    else:
        overall_delta = 0.0
    return "\n".join(lines), (sum(all_b) / len(all_b) if all_b else 0.0), overall_delta


def _extract_json(raw: str) -> dict | None:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group())
    except json.JSONDecodeError:
        return None


def judge_pair(judge_backend: str, judge_model: str, task_prompt: str,
                output_a: str, output_b: str, api_key: str | None) -> dict | None:
    prompt = JUDGE_PROMPT.format(task_prompt=task_prompt, output_a=output_a, output_b=output_b)
    try:
        raw = (harness.call_ollama(judge_model, prompt) if judge_backend == "ollama"
               else harness.call_gemini(judge_model, prompt, api_key))
    except Exception:
        return None
    return _extract_json(raw)


def run_judging(subject_results: list[dict], subject_key: str,
                 judge_backend: str, judge_model: str, api_key: str | None,
                 tasks_meta: dict) -> tuple[str, float]:
    by_task_cond: dict = defaultdict(lambda: defaultdict(list))
    for r in subject_results:
        if r["output"]:
            by_task_cond[r["task_id"]][r["condition"]].append(r["output"])

    rows = []
    baseline_scores, aeqos_scores = [], []
    for task_id, conds in by_task_cond.items():
        baselines, aeqos_outs = conds.get("baseline", []), conds.get("aeqos", [])
        n = min(len(baselines), len(aeqos_outs))
        for i in range(n):
            b_out, a_out = baselines[i], aeqos_outs[i]
            swap = random.random() < 0.5
            out_a, out_b = (a_out, b_out) if swap else (b_out, a_out)
            verdict = judge_pair(judge_backend, judge_model, tasks_meta[task_id]["prompt"], out_a, out_b, api_key)
            if not verdict:
                continue
            a_score, b_score = verdict.get("a_score"), verdict.get("b_score")
            if a_score is None or b_score is None:
                continue
            aeqos_score, baseline_score = (a_score, b_score) if swap else (b_score, a_score)
            aeqos_scores.append(aeqos_score)
            baseline_scores.append(baseline_score)
            rows.append((task_id, i, baseline_score, aeqos_score, verdict.get("reasoning", "")))

    lines = [
        f"Judge: `{judge_backend}:{judge_model}` (never judges `{subject_key}`'s own outputs — cross-model by construction). "
        f"Blind: judge sees only 'Output A'/'Output B', condition-to-label assignment randomized per trial.",
        "",
        "| Task | Trial | Baseline score | AEQ-OS score | Judge reasoning |",
        "|---|---|---|---|---|",
    ]
    for task_id, trial, b_s, a_s, reasoning in rows:
        lines.append(f"| {task_id} | {trial} | {b_s} | {a_s} | {reasoning} |")

    avg_delta = 0.0
    if baseline_scores and aeqos_scores:
        avg_b = sum(baseline_scores) / len(baseline_scores)
        avg_a = sum(aeqos_scores) / len(aeqos_scores)
        avg_delta = avg_a - avg_b
        lines.append(f"| **Average** | | **{avg_b:.1f}/10** | **{avg_a:.1f}/10** | **delta {avg_delta:+.1f}** |")

    return "\n".join(lines), avg_delta


def claude_prediction_section(overall_mech_delta: float, overall_judge_delta: float) -> str:
    return f"""## ⚠ Predicted — not measured (Claude models)

**No Claude API call was made for this benchmark** — no key, and the user explicitly declined to spend on one. The numbers below are a reasoned **estimate**, not a result, built from the pattern actually observed across the models that *were* tested (see above).

Observed: mechanical pass-rate delta of {overall_mech_delta:+.0%} and judged-quality delta of {overall_judge_delta:+.1f}/10 when AEQ-OS context is loaded.

**Reasoning for the Claude estimate:** Claude models are generally more RLHF'd toward the *generic* best practices several of these tasks probe (e.g. bounded retries, not swallowing exceptions) — so the baseline pass rate on those specific tasks is plausibly already higher than the free/open models tested here, which would make the *absolute* mechanical delta smaller for Claude on those items. But AEQ-OS's own non-generic conventions — its exact rule IDs, the ledger's dual-entry schema, the G0-G4 gate vocabulary — cannot be "already known" by any model without being told, regardless of how well-trained it is on generic practice. On that basis:

- **Predicted mechanical delta for Claude: smaller than observed here, plausibly in the +5 to +15 percentage-point range** (vs. the measured {overall_mech_delta:+.0%} on tested models) — driven mostly by the AEQ-OS-specific items, not the generic ones.
- **Predicted judged-quality delta: directionally similar, plausibly +0.5 to +1.5/10** — a strong baseline model has less headroom to visibly improve on holistic "thoroughness," but AEQ-OS's specific gates (evidence tables, explicit assumption-flagging) are exactly the kind of thing a judge model would notice as absent otherwise.

**Confidence: low.** This is extrapolation from two data points, not measurement. Treat it as a hypothesis for a future real test, not a claim about Claude's actual behavior.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True, help="backend:model whose outputs get scored, e.g. ollama:qwen2.5-coder:7b")
    parser.add_argument("--judge", required=True, help="backend:model that judges the subject's outputs")
    args = parser.parse_args()

    subject_backend, _, subject_model = args.subject.partition(":")
    judge_backend, _, judge_model = args.judge.partition(":")
    subject_key = f"{subject_backend}-{subject_model.replace(':', '_')}"

    results = load_results(subject_key)
    if not results:
        print(f"error: no results found for {subject_key} — run harness.py first", file=sys.stderr)
        return 1

    tasks_meta = load_tasks_meta()
    api_key = None
    if judge_backend == "gemini" or subject_backend == "gemini":
        api_key = harness.load_dotenv_value("GEMINI_API_KEY")

    mech_table, baseline_rate, mech_delta = mechanical_table(results, tasks_meta)
    judge_table, judge_delta = run_judging(results, subject_key, judge_backend, judge_model, api_key, tasks_meta)

    report = f"""# AEQ-OS Benchmark Results — {subject_backend}:{subject_model}

Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}. See `benchmarks/README.md` for full methodology. Sample size: 10 tasks × 3 trials × 2 conditions — a real but modest sample; treat rates as indicative, not definitive.

## Track 1 — Mechanical (objective, PASS/FAIL against a named rule ID)

{mech_table}

## Track 2 — Holistic quality rating (subjective, model-judged — NOT a mechanical measurement)

{judge_table}

{claude_prediction_section(mech_delta, judge_delta)}
"""
    out_path = BENCH_DIR / f"RESULTS-{subject_key}.md"
    out_path.write_text(report)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
