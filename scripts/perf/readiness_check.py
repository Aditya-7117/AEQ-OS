#!/usr/bin/env python3
"""AEQ-OS Performance tier — mechanical PROD-n checks (closes PROD-18).

The Lite tier default is the agent running production_readiness.md's
checklist by hand (PROD-1..17). This tool scripts only the pillars that are
actually mechanically checkable: dependency/CVE scanning (delegates to
security_scan.py), unpinned dependency detection, a missing-timeout
heuristic on common HTTP client calls, and `:latest` image tags in deploy
manifests. Pillars that require judgment (architecture readiness, runbook
quality, backup drills, compliance review) are reported as REQUIRES REVIEW,
never silently skipped and never faked as PASS — PROD-14's PASS/FLAG/BLOCK
table only covers what evidence actually supports.

Usage:
    readiness_check.py [--path DIR] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
import security_scan  # noqa: E402

HTTP_CALL_RE = re.compile(
    r"\b(requests\.(get|post|put|delete|patch)|axios\.\w+|fetch)\s*\("
)
TIMEOUT_HINT_RE = re.compile(r"timeout\s*[:=]")
LATEST_TAG_RE = re.compile(r":latest\b")
DEPLOY_MANIFEST_GLOBS = ("Dockerfile*", "docker-compose*.yml", "docker-compose*.yaml", "*.k8s.yaml", "*.k8s.yml")
CODE_GLOBS = ("*.py", "*.ts", "*.js", "*.tsx", "*.jsx")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".ai_os"}


def _iter_files(root: Path, globs: tuple[str, ...]):
    for g in globs:
        for p in root.rglob(g):
            if not any(part in SKIP_DIRS for part in p.parts):
                yield p


def check_unpinned_dependencies(root: Path) -> dict:
    unpinned = []
    req = root / "requirements.txt"
    if req.exists():
        for line in req.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not re.search(r"[=<>~!]", line):
                unpinned.append(f"requirements.txt: {line}")
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
        for section in ("dependencies", "devDependencies"):
            for name, version in data.get(section, {}).items():
                if version in ("*", "latest"):
                    unpinned.append(f"package.json: {name}@{version}")

    status = "PASS" if not unpinned else "FLAG"
    return {"pillar": "Unpinned dependencies", "status": status, "findings": unpinned[:10]}


def check_missing_timeouts(root: Path) -> dict:
    findings = []
    for f in _iter_files(root, CODE_GLOBS):
        try:
            text = f.read_text(errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if HTTP_CALL_RE.search(line) and not TIMEOUT_HINT_RE.search(line):
                findings.append(f"{f.relative_to(root)}:{i}: {line.strip()[:80]}")

    status = "PASS" if not findings else "FLAG"
    return {
        "pillar": "Missing timeouts on external calls (heuristic — same-line only, review before trusting)",
        "status": status, "findings": findings[:10],
    }


def check_latest_tags(root: Path) -> dict:
    findings = []
    for f in _iter_files(root, DEPLOY_MANIFEST_GLOBS):
        try:
            text = f.read_text(errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if LATEST_TAG_RE.search(line):
                findings.append(f"{f.relative_to(root)}:{i}: {line.strip()[:80]}")

    status = "PASS" if not findings else "FLAG"
    return {"pillar": "`:latest` tags in deploy manifests", "status": status, "findings": findings[:10]}


REQUIRES_REVIEW = [
    "Architecture/scalability readiness note (PROD-1) — needs a human/agent judgment call, not scannable",
    "Observability floor & runbook linkage (PROD-4/PROD-5) — requires checking actual dashboards/alerting, not files",
    "Backup/restore drill evidence (PROD-7) — requires a real drill having run, not inferable from source",
    "Attack surface / least-privilege review (PROD-9) — requires infrastructure access this tool doesn't have",
    "Environment isolation (PROD-11) — requires infrastructure/account-boundary review",
    "Compliance & retention checklist (PROD-12) — requires data-classification review per SEC-8",
]


def run_readiness(root: Path) -> dict:
    scan = security_scan.run_scan(root)
    dep_status = "PASS"
    if any(r["status"] == "FLAG" for r in scan["results"]):
        dep_status = "FLAG"

    pillars = [
        {"pillar": "Dependency/CVE audit (PROD-13, via security_scan.py)", "status": dep_status,
         "findings": [f"{r['stack']}/{r['tool']}: {r['status']}" for r in scan["results"]]},
        check_unpinned_dependencies(root),
        check_missing_timeouts(root),
        check_latest_tags(root),
    ]
    return {"root": str(root), "pillars": pillars, "requires_review": REQUIRES_REVIEW}


def print_report(report: dict) -> None:
    for p in report["pillars"]:
        if p["status"] == "PASS":
            lib.ok(f"{p['pillar']} — PASS")
        else:
            lib.bad(f"{p['pillar']} — FLAG")
            for finding in p["findings"]:
                lib.info(f"    {finding}")

    print()
    lib.info("Pillars requiring human/agent judgment (not mechanically checkable — never faked as PASS):")
    for item in report["requires_review"]:
        lib.info(f"  - {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", help="project path (default: auto-detect from cwd)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = lib.find_project_root(args.path)
    report = run_readiness(root)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    any_flag = any(p["status"] == "FLAG" for p in report["pillars"])
    return 1 if any_flag else 0


if __name__ == "__main__":
    sys.exit(main())
