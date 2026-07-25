#!/usr/bin/env python3
"""AEQ-OS Performance tier — security scan orchestration (closes SEC-18).

SEC-15 requires a dependency/CVE scan and a static security lint for
anything touching authn/z, secrets, or PII. The Lite tier default is the
agent running those tools by hand, on demand. This tool orchestrates
whatever free/open-source scanners are already installed for the stacks
present in the target project — it never bundles or reimplements a
scanner, and it never fakes a PASS for one that's missing: a missing
scanner is reported as MISSING with its free install command.

Usage:
    security_scan.py [--path DIR] [--json]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

# (stack, manifest file, [(tool, install_hint, command)])
CHECKS = {
    "python": {
        "manifests": ("requirements.txt", "pyproject.toml", "Pipfile"),
        "tools": [
            ("bandit", "pip install bandit", ["bandit", "-r", ".", "-q"]),
            ("pip-audit", "pip install pip-audit", ["pip-audit"]),
        ],
    },
    "node": {
        "manifests": ("package.json",),
        "tools": [
            ("npm audit", "npm ships with Node — install Node to get it",
             ["npm", "audit", "--audit-level=high"]),
        ],
    },
    "rust": {
        "manifests": ("Cargo.toml",),
        "tools": [
            ("cargo-audit", "cargo install cargo-audit", ["cargo", "audit"]),
        ],
    },
    "go": {
        "manifests": ("go.mod",),
        "tools": [
            ("gosec", "go install github.com/securego/gosec/v2/cmd/gosec@latest",
             ["gosec", "./..."]),
        ],
    },
}


def detect_stacks(root: Path) -> list[str]:
    return [
        stack for stack, cfg in CHECKS.items()
        if any((root / m).exists() for m in cfg["manifests"])
    ]


def tool_binary(cmd: list[str]) -> str:
    return cmd[0]


def run_scan(root: Path, timeout: float = 120.0) -> dict:
    """Returns a structured report; also used by readiness_check.py."""
    stacks = detect_stacks(root)
    report: dict = {"root": str(root), "stacks": stacks, "results": []}

    for stack in stacks:
        for tool_name, install_hint, cmd in CHECKS[stack]["tools"]:
            binary = tool_binary(cmd)
            if not shutil.which(binary):
                report["results"].append({
                    "stack": stack, "tool": tool_name, "status": "MISSING",
                    "install": install_hint,
                })
                continue
            try:
                proc = subprocess.run(
                    cmd, cwd=root, capture_output=True, text=True, timeout=timeout,
                )
                status = "PASS" if proc.returncode == 0 else "FLAG"
                report["results"].append({
                    "stack": stack, "tool": tool_name, "status": status,
                    "returncode": proc.returncode,
                    "summary": (proc.stdout or proc.stderr).strip().splitlines()[:5],
                })
            except subprocess.TimeoutExpired:
                report["results"].append({
                    "stack": stack, "tool": tool_name, "status": "FLAG",
                    "summary": [f"timed out after {timeout}s"],
                })

    return report


def print_report(report: dict) -> None:
    if not report["stacks"]:
        lib.info("no recognized stack manifests found (Python/Node/Rust/Go) — nothing to scan")
        return

    lib.info(f"detected stacks: {', '.join(report['stacks'])}")
    for r in report["results"]:
        if r["status"] == "PASS":
            lib.ok(f"[{r['stack']}] {r['tool']} — PASS")
        elif r["status"] == "MISSING":
            lib.warn(f"[{r['stack']}] {r['tool']} — MISSING, install with: {r['install']}")
        else:
            lib.bad(f"[{r['stack']}] {r['tool']} — FLAG")
            for line in r.get("summary", []):
                lib.info(f"    {line}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", help="project path (default: auto-detect from cwd)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of the human report")
    args = parser.parse_args()

    root = lib.find_project_root(args.path)
    report = run_scan(root)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    any_flag = any(r["status"] == "FLAG" for r in report["results"])
    return 1 if any_flag else 0


if __name__ == "__main__":
    sys.exit(main())
