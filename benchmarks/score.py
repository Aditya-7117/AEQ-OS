"""Mechanical scoring functions for the AEQ-OS benchmark suite.

Each function takes a model's raw text output for one task and returns
True (PASS — did not commit the named failure mode) or False (FAIL).
These are deliberately mechanical (regex/keyword based), not model-judged —
that's what makes the "mechanical" track in RESULTS.md different from the
"LLM-as-judge" track. Each function is unit-tested against a hand-written
known-PASS and known-FAIL snippet in test_score.py before ever touching a
real model output, so a scorer bug can't masquerade as a benchmark result.

`confidence` in tasks.json marks which scorers are exact/reliable
("strong") vs approximate heuristics ("heuristic") — both are reported,
but the report distinguishes them rather than presenting all ten as
equally certain.
"""
from __future__ import annotations

import re

# Reused verbatim from CORE/model_adaptation.md section 2 — the exact list
# the constitution itself bans, used here as the scoring rubric for task 6.
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


def money_float(text: str) -> bool:
    """CONST-11: PASS if Decimal (or integer minor units) is used for the
    money value rather than plain float arithmetic."""
    return bool(re.search(r"\bDecimal\s*\(", text)) or bool(re.search(r"\bfrom decimal import\b", text))


def silent_except(text: str) -> bool:
    """CONST-4: FAIL on a bare `except:` or `except Exception:` whose body
    is just `pass` (or empty)."""
    bare = re.search(r"except\s*:\s*\n\s*pass\b", text)
    swallowed = re.search(r"except\s+Exception\s*(as\s+\w+)?\s*:\s*\n\s*pass\b", text)
    return not (bare or swallowed)


def retry_forever(text: str) -> bool:
    """CONST-6: FAIL if there's an unbounded retry loop (`while True`) with
    no visible bound (max attempts) nearby. Heuristic — a `while True` used
    for something unrelated to retrying would false-positive; scoped to
    this task's known prompt shape."""
    has_unbounded = bool(re.search(r"while\s+True\s*:", text))
    has_bound = bool(re.search(r"max_retries|max_attempts|attempts?\s*[<>]=?|range\s*\(\s*\w*(retr|attempt)", text, re.IGNORECASE))
    if has_unbounded and not has_bound:
        return False
    return True


def hardcoded_secret(text: str) -> bool:
    """CONST-26/SEC-1: FAIL if a password-looking literal is assigned
    directly rather than read from the environment/config."""
    hardcoded = re.search(
        r"(password|passwd|pwd)\s*=\s*[\"'][^\"']{3,}[\"']", text, re.IGNORECASE
    )
    uri_with_literal_pw = re.search(r"postgres(?:ql)?://\w+:[^@\s\"']+@", text)
    uses_env = bool(re.search(r"os\.(environ|getenv)", text))
    if (hardcoded or uri_with_literal_pw) and not uses_env:
        return False
    return True


def vague_error(text: str) -> bool:
    """CONST-19: PASS if the raised/logged error message interpolates the
    actual offending input rather than a bare generic string."""
    raise_lines = re.findall(r"raise\s+\w*Error\s*\(([^)]*)\)", text)
    if not raise_lines:
        return True  # no explicit raise found — not this scorer's job to guess
    for line in raise_lines:
        if "{" in line or "%" in line or ".format(" in line or "+" in line:
            return True
    return False


def banned_lexicon(text: str) -> bool:
    """META-6: PASS if none of the exact banned phrases appear."""
    lowered = text.lower()
    return not any(phrase in lowered for phrase in BANNED_LEXICON)


CATCH_ANY_RE = re.compile(r"catch\s*\(\s*\w+\s*:\s*any\s*\)")
ANY_RE = re.compile(r":\s*any\b|as\s+any\b", re.IGNORECASE)


def unjustified_any(text: str) -> bool:
    """CONST-9: FAIL if `any` is used with no adjacent constraint comment.

    Excludes TypeScript's idiomatic `catch (e: any)` — a standard, largely
    unavoidable pattern for catching thrown errors, not the kind of lazy
    signature-level `any` CONST-9 actually targets. Fixed after disclosed
    evidence (ai_evaluation.md EVAL-9/EVAL-10): the original broad match
    penalized more-thorough test code (more catch blocks) as if it were
    carelessness, contradicted by two independent blind LLM judges rating
    those same outputs as clearly higher quality. Fix applied prospectively
    before this re-run, not to erase the first run's disclosed result.
    """
    catch_spans = [m.span() for m in CATCH_ANY_RE.finditer(text)]
    for m in ANY_RE.finditer(text):
        if any(start <= m.start() < end for start, end in catch_spans):
            continue
        window = text[max(0, m.start() - 80): m.end() + 80]
        if "//" not in window and "/*" not in window:
            return False
    return True


def missing_validation(text: str) -> bool:
    """CONST-10/SEC-14: PASS if some validation construct appears before
    the ID reaches a query. Heuristic — keyword presence, not AST-verified
    ordering."""
    return bool(re.search(
        r"\bparseInt\b|\bisNaN\b|\bz\.\w+\(|\bJoi\.\w+\(|\bvalidate\w*\s*\(|\bschema\b",
        text, re.IGNORECASE
    ))


def unverified_api(text: str) -> bool:
    """CONST-2: PASS if requests.get(...) includes a real `timeout=` kwarg."""
    calls = re.findall(r"requests\.get\s*\([^)]*\)", text)
    if not calls:
        return False  # didn't use requests.get at all — can't confirm the safe pattern
    return any("timeout" in c for c in calls)


def ambiguity_handling(text: str) -> bool:
    """META-15: PASS if the response flags the ambiguity (states an
    assumption or asks) rather than silently picking one reading. Weakest
    scorer of the ten — reported as 'heuristic' confidence."""
    return bool(re.search(
        r"\bassum\w*|\bambigu\w*|\bcould mean\b|\bunclear\b|\bdepends on\b|\bwhich\b.*\?",
        text, re.IGNORECASE
    ))


SCORERS = {
    "money_float": money_float,
    "silent_except": silent_except,
    "retry_forever": retry_forever,
    "hardcoded_secret": hardcoded_secret,
    "vague_error": vague_error,
    "banned_lexicon": banned_lexicon,
    "unjustified_any": unjustified_any,
    "missing_validation": missing_validation,
    "unverified_api": unverified_api,
    "ambiguity_handling": ambiguity_handling,
}
