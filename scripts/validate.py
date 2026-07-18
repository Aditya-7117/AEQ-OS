#!/usr/bin/env python3
"""AEQ-OS self-validation: the same checks used before every release.

Checks:
  1. ROUTER_MAP.json is valid JSON and every path it references exists.
  2. Every rule-ID prefix used in a file is contiguous starting at 1 (no gaps,
     no accidental duplicates) — a broken sequence usually means a rule was
     deleted without renumbering, which VER-... style tooling should catch.
  3. The banned-lexicon list (META-2 section 2) doesn't appear anywhere.

Exit code is non-zero on any failure, for CI use.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BANNED_LEXICON = [
    "in a real implementation",
    "simplified for brevity",
    "left as an exercise",
    "you would need to",
    "for now",
    "placeholder",
    "should work",
    "probably works",
    "rest of the code remains",
    "... existing code ...",
]

# A rule is "defined" (not just cross-referenced) either as a bold bullet
# (`**CONST-1**`, `**QT-STOP-3**`) or as the leading cell of a markdown table
# row (`| META-1 |`). The optional `(?:-[A-Z]{2,10})?` group handles compound
# prefixes like QT-STOP / QT-ARCH so "QT-STOP-3" is tracked as its own
# contiguous namespace "QT-STOP", not misparsed as bare prefix "STOP".
DEFINED_RULE_ID_RE = re.compile(
    r"(?:\*\*|^\|\s*)([A-Z]{2,10}(?:-[A-Z]{2,10})?)-(\d+)\b", re.MULTILINE
)

# model_adaptation.md's entire purpose is to name these strings, not avoid them.
BANNED_LEXICON_EXEMPT = {"CORE/model_adaptation.md"}

RULE_FILE_DIRS = ("CORE", "DOMAINS")


def check_router_map() -> list[str]:
    errors = []
    path = REPO / "ROUTER_MAP.json"
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        return [f"ROUTER_MAP.json is not valid JSON: {e}"]

    boot = data.get("boot")
    if boot and not (REPO / boot).exists():
        errors.append(f"ROUTER_MAP.json 'boot' points at missing file: {boot}")

    for f in data.get("always_load", []):
        if not (REPO / f).exists():
            errors.append(f"always_load references missing file: {f}")

    for route in data.get("routes", []):
        for f in route.get("load", []):
            if not (REPO / f).exists():
                errors.append(f"route '{route.get('id')}' references missing file: {f}")

    return errors


def check_rule_id_contiguity() -> list[str]:
    """Only counts IDs *defined* in a file (bold `**PREFIX-n**` at declaration
    sites), not plain-text cross-references to rules defined elsewhere."""
    errors = []
    for md in sorted((REPO / "CORE").glob("*.md")) + sorted((REPO / "DOMAINS").glob("*.md")):
        text = md.read_text()
        by_prefix: dict[str, set[int]] = {}
        for prefix, num in DEFINED_RULE_ID_RE.findall(text):
            by_prefix.setdefault(prefix, set()).add(int(num))
        for prefix, nums in by_prefix.items():
            expected = set(range(1, max(nums) + 1))
            missing = expected - nums
            if missing:
                errors.append(
                    f"{md.relative_to(REPO)}: {prefix}-n has gaps at {sorted(missing)} "
                    f"(max is {prefix}-{max(nums)})"
                )
    return errors


def check_banned_lexicon() -> list[str]:
    """Scoped to CORE/ and DOMAINS/ — the actual rule content an agent treats
    as law. README/CONTRIBUTING/docs are human-facing prose that may need to
    *discuss* these failure modes by name; that's documentation, not a rule
    that ships the anti-pattern it's supposed to prevent."""
    errors = []
    files = []
    for d in RULE_FILE_DIRS:
        files += sorted((REPO / d).glob("*.md"))
    for md in files:
        rel = md.relative_to(REPO).as_posix()
        if rel in BANNED_LEXICON_EXEMPT:
            continue  # registry references the concept, not shipped rule content
        text = md.read_text().lower()
        for phrase in BANNED_LEXICON:
            if phrase in text:
                errors.append(f"{rel}: contains banned phrase '{phrase}'")
    return errors


def main() -> int:
    all_errors = []
    all_errors += check_router_map()
    all_errors += check_rule_id_contiguity()
    all_errors += check_banned_lexicon()

    if all_errors:
        print(f"FAILED — {len(all_errors)} issue(s):\n")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print("PASSED — ROUTER_MAP.json valid, all rule-ID sequences contiguous, no banned lexicon found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
