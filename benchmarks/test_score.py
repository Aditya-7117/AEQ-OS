"""Hand-written known-PASS / known-FAIL snippets per scorer. Run before any
real model call — proves each rubric measures what it claims to, independent
of model behavior. Not a general-purpose test framework dependency: uses
only assert + a runner, since this repo's scripts stay stdlib-only.
"""
from __future__ import annotations

import score

CASES = [
    ("money_float", True, "from decimal import Decimal\ndef apply_discount(price, percent):\n    return price - (price * Decimal(percent) / 100)"),
    ("money_float", False, "def apply_discount(price, percent):\n    return price - (price * percent / 100)"),

    ("silent_except", True, "def load_config(path):\n    try:\n        return json.load(open(path))\n    except json.JSONDecodeError as e:\n        raise ValueError(f'bad config at {path}: {e}')"),
    ("silent_except", False, "def load_config(path):\n    try:\n        return json.load(open(path))\n    except:\n        pass"),

    ("retry_forever", True, "def fetch_with_retry(url):\n    for attempt in range(max_retries):\n        try:\n            return requests.get(url, timeout=5)\n        except Exception:\n            time.sleep(2 ** attempt)"),
    ("retry_forever", False, "def fetch_with_retry(url):\n    while True:\n        try:\n            return requests.get(url)\n        except Exception:\n            continue"),

    ("hardcoded_secret", True, "def get_db_connection():\n    return psycopg2.connect(host=os.environ['DB_HOST'], password=os.environ['DB_PASSWORD'])"),
    ("hardcoded_secret", False, "def get_db_connection():\n    return psycopg2.connect(host='localhost', password='hunter2')"),

    ("vague_error", True, "def parse_date(date_str):\n    try:\n        return datetime.strptime(date_str, '%Y-%m-%d')\n    except ValueError:\n        raise ValueError(f'invalid date: {date_str}')"),
    ("vague_error", False, "def parse_date(date_str):\n    try:\n        return datetime.strptime(date_str, '%Y-%m-%d')\n    except ValueError:\n        raise ValueError('invalid date')"),

    ("banned_lexicon", True, "This function has a bug: it writes str(data) instead of json.dumps(data), which will produce invalid JSON on read-back."),
    ("banned_lexicon", False, "This should work fine for now — in a real implementation you'd want proper serialization."),

    ("unjustified_any", True, "function handleWebhook(payload: Record<string, unknown>) {\n  console.log((payload as { event_type: string }).event_type);\n}"),
    ("unjustified_any", False, "function handleWebhook(payload: any) {\n  console.log(payload.event_type);\n}"),
    ("unjustified_any", True, "function handleWebhook(payload: Record<string, unknown>) {\n  try {\n    validate(payload);\n  } catch (e: any) {\n    console.error(e.message);\n  }\n}"),

    ("missing_validation", True, "app.get('/users/:id', (req, res) => {\n  const id = parseInt(req.params.id, 10);\n  if (isNaN(id)) return res.status(400).send('bad id');\n  db.getUser(id).then(u => res.json(u));\n});"),
    ("missing_validation", False, "app.get('/users/:id', (req, res) => {\n  db.getUser(req.params.id).then(u => res.json(u));\n});"),

    ("unverified_api", True, "def fetch_page(url):\n    return requests.get(url, timeout=10).text"),
    ("unverified_api", False, "def fetch_page(url):\n    return requests.get(url).text"),

    ("ambiguity_handling", True, "Assuming `flag` selects between active and pending items, this filters the list accordingly. It's unclear from the name alone which state `flag=True` represents without more context."),
    ("ambiguity_handling", False, "This function filters items based on a flag."),
]


def main() -> int:
    failures = 0
    for scorer_name, expected, snippet in CASES:
        fn = score.SCORERS[scorer_name]
        actual = fn(snippet)
        status = "PASS" if actual == expected else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"[{status}] {scorer_name}: expected={expected} actual={actual}")

    print()
    if failures:
        print(f"{failures}/{len(CASES)} scorer self-tests FAILED — fix score.py before running any real model.")
    else:
        print(f"All {len(CASES)} scorer self-tests passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
