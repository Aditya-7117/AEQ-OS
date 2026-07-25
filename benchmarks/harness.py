#!/usr/bin/env python3
"""Benchmark harness — runs the AEQ-OS failure-mode probe suite (tasks.json)
against a model, with and without AEQ-OS context loaded, N trials each.

SECURITY (Gemini backend): GEMINI_API_KEY is read from AEQ-OS's own
gitignored .env at runtime only, via os.environ or a minimal local parser
— never printed, never logged, never written to any output file. Gemini's
REST API takes the key as a URL query parameter, so every error path below
is deliberately written to convert exceptions into generic, pre-written
messages rather than ever surfacing the raw exception object or the
request URL, either of which could carry the key.

Reuses scripts/perf/watcher.should_pause() as-is (not reimplemented) so
local-Ollama trials defer to OmniApply exactly the way the watcher does —
one function backs both.

Usage:
    harness.py --backend ollama:qwen2.5-coder:7b --trials 3
    harness.py --backend gemini:gemini-2.5-flash --trials 3
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PERF_DIR = REPO_ROOT / "scripts" / "perf"
sys.path.insert(0, str(PERF_DIR))
import watcher  # noqa: E402 — should_pause() reused directly, not reimplemented

BENCH_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCH_DIR / "results"

AEQOS_CONTEXT_FILES = [
    REPO_ROOT / "CORE" / "constitution.md",
    REPO_ROOT / "CORE" / "security_baseline.md",
    REPO_ROOT / "CORE" / "model_adaptation.md",
]

OLLAMA_BASE = "http://localhost:11434"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

OMNIAPPLY_PIDFILE = str(Path.home() / "Projects" / "OmniApply" / "data" / "server.pid")
OMNIAPPLY_MODELS = ["deepseek-r1:32b", "qwen3:32b"]


def load_dotenv_value(key: str) -> str | None:
    """Minimal, dependency-free .env reader. Returns the value for `key` or
    None. Caller is responsible for never printing/logging the result."""
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return None
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return None


def load_aeqos_context() -> str:
    parts = [f"# {f.name}\n\n{f.read_text()}" for f in AEQOS_CONTEXT_FILES]
    return "\n\n---\n\n".join(parts)


def wait_for_omniapply(poll_seconds: float = 30.0) -> None:
    """Same standing rule as watcher.py: defer to OmniApply's heavy models
    rather than compete for RAM. Reuses watcher.should_pause() directly —
    same function, same behavior, not a second copy to drift out of sync."""
    while True:
        reason = watcher.should_pause([OMNIAPPLY_PIDFILE], OMNIAPPLY_MODELS)
        if not reason:
            return
        print(f"  · waiting — {reason}")
        time.sleep(poll_seconds)


def call_ollama(model: str, prompt: str, timeout: float = 180.0) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data.get("response", "")


def call_gemini(model: str, prompt: str, api_key: str, timeout: float = 60.0) -> str:
    url = f"{GEMINI_BASE}/{model}:generateContent?key={api_key}"
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except Exception:
        # Deliberately generic and exception-object-free: urllib's exceptions
        # can carry the request URL — which embeds the API key as a query
        # param — in their string form or .reason/.filename attributes.
        # `e` is never touched, printed, or included below, on purpose.
        raise RuntimeError("Gemini API call failed (connection, HTTP, or auth error)") from None
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("Gemini API returned an unexpected response shape") from None


def run_task(backend: str, model: str, prompt: str, condition: str, api_key: str | None) -> str:
    if condition == "aeqos":
        full_prompt = f"{load_aeqos_context()}\n\n---\n\nFollow the rules above. Now complete this task:\n\n{prompt}"
    else:
        full_prompt = prompt

    if backend == "ollama":
        wait_for_omniapply()
        return call_ollama(model, full_prompt)
    if backend == "gemini":
        assert api_key is not None
        return call_gemini(model, full_prompt, api_key)
    raise ValueError(f"unknown backend: {backend}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backend", required=True, help="ollama:<model> or gemini:<model>")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--tasks", default=str(BENCH_DIR / "tasks.json"))
    args = parser.parse_args()

    backend_kind, _, model = args.backend.partition(":")
    if backend_kind not in ("ollama", "gemini") or not model:
        print(f"error: --backend must be ollama:<model> or gemini:<model>, got '{args.backend}'", file=sys.stderr)
        return 1

    api_key = None
    if backend_kind == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY") or load_dotenv_value("GEMINI_API_KEY")
        if not api_key:
            print("error: GEMINI_API_KEY not found in environment or .env", file=sys.stderr)
            return 1

    tasks = json.loads(Path(args.tasks).read_text())["tasks"]
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"{backend_kind}-{model.replace(':', '_')}.json"

    results = []
    for task in tasks:
        for condition in ("baseline", "aeqos"):
            for trial in range(args.trials):
                print(f"[{model}] {task['id']} / {condition} / trial {trial + 1}")
                try:
                    output = run_task(backend_kind, model, task["prompt"], condition, api_key)
                    error = None
                except Exception as e:
                    output = None
                    error = str(e)
                    print(f"  ! {error}")
                results.append({
                    "task_id": task["id"], "rule": task["rule"], "confidence": task["confidence"],
                    "scorer": task["scorer"], "condition": condition, "trial": trial,
                    "output": output, "error": error,
                })

    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {len(results)} trial result(s) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
