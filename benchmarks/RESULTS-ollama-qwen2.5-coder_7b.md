# AEQ-OS Benchmark Results — ollama:qwen2.5-coder:7b

Generated 2026-07-25T15:26:56+00:00. See `benchmarks/README.md` for full methodology. Sample size: 10 tasks × 3 trials × 2 conditions — a real but modest sample; treat rates as indicative, not definitive.

## Track 1 — Mechanical (objective, PASS/FAIL against a named rule ID)

| Task | Rule | Confidence | Baseline pass rate | AEQ-OS pass rate | Delta |
|---|---|---|---|---|---|
| ambiguity-handling | `META-15` | heuristic | 0% | 20% | +20% |
| banned-lexicon | `META-6` | strong | 100% | 100% | +0% |
| hardcoded-secret | `CONST-26` | strong | 0% | 60% | +60% |
| missing-boundary-validation | `CONST-10` | heuristic | 20% | 60% | +40% |
| money-float | `CONST-11` | strong | 0% | 0% | +0% |
| retry-forever | `CONST-6` | heuristic | 100% | 100% | +0% |
| silent-except | `CONST-4` | strong | 100% | 100% | +0% |
| unjustified-any | `CONST-9` | strong | 100% | 40% | -60% |
| unverified-api | `CONST-2` | strong | 100% | 100% | +0% |
| vague-error | `CONST-19` | heuristic | 100% | 80% | -20% |
| **Overall** | | | **62%** | **66%** | **+4%** |

## Track 2 — Holistic quality rating (subjective, model-judged — NOT a mechanical measurement)

Judge: `gemini:gemini-2.5-flash` (never judges `ollama-qwen2.5-coder_7b`'s own outputs — cross-model by construction). Blind: judge sees only 'Output A'/'Output B', condition-to-label assignment randomized per trial.

| Task | Trial | Baseline score | AEQ-OS score | Judge reasoning |
|---|---|---|---|---|
| money-float | 0 | 4 | 10 | Output A is superior due to its robust input validation, comprehensive docstring, and clear explanation, addressing error handling and production readiness signals thoroughly, while Output B correctly calculates the discount but lacks any error handling or internal documentation. |
| money-float | 1 | 3 | 9 | Output A demonstrates strong production-readiness with type hints, a detailed docstring, and robust error handling for invalid inputs, whereas Output B only provides the core calculation without any validation or documentation. |
| money-float | 2 | 7 | 9 | Output B is more production-ready due to the inclusion of type hints and crucial rounding for financial calculations, although Output A provides more contextual explanation and examples. |
| money-float | 3 | 5 | 9 | Output B provides robust error handling, type hints, and a comprehensive docstring, making it significantly more production-ready and thorough than Output A, which only offers the basic correct calculation. |
| money-float | 4 | 4 | 9 | Output B is significantly more robust and production-ready, featuring type hints, a comprehensive docstring with examples, error handling for invalid percentages, and practical rounding for financial calculations, while Output A provides only the basic correct logic without any of these enhancements. |
| silent-except | 0 | 4 | 9 | Output B is superior due to its comprehensive error handling for `FileNotFoundError` and `json.JSONDecodeError`, making it far more production-ready and thorough than Output A which lacks any error handling. |
| silent-except | 1 | 4 | 6 | Output A demonstrates robust error handling, detailed documentation, and example usage, but contains a critical missing import (`os`), whereas Output B is concise and functionally correct for the happy path but completely lacks error handling and production-readiness features. |
| silent-except | 2 | 6 | 9 | Output B provides robust error handling for common file and JSON parsing issues, making it significantly more production-ready and thorough than Output A, which lacks any explicit error handling. |
| silent-except | 3 | 4 | 9 | Output B is significantly more robust and production-ready due to its comprehensive error handling for file not found and JSON decoding issues, whereas Output A lacks any error handling. |
| silent-except | 4 | 4 | 10 | Output A is significantly superior due to its comprehensive error handling for `FileNotFoundError` and `json.JSONDecodeError`, along with a thorough docstring and clear production-readiness signals, while Output B lacks any error handling or proper documentation. |
| retry-forever | 0 | 5 | 9 | Output B is superior due to its use of exponential backoff with jitter, specific exception handling including HTTP status codes, configurable parameters, and comprehensive docstring, making it significantly more production-ready and robust than Output A's basic fixed-delay retry. |
| retry-forever | 1 | 6 | 5 | Output A is slightly better due to implementing exponential backoff, which is a stronger strategy for handling flaky network calls, though both outputs critically miss incorporating request timeouts for production readiness. |
| retry-forever | 2 | 6 | 9 | Output B provides a production-ready solution leveraging the `tenacity` library for robust retries with exponential backoff and proper HTTP status code handling, whereas Output A offers a basic, self-implemented loop lacking crucial features like backoff and specific error handling details. |
| retry-forever | 3 | 6 | 2 | Output A's simulated network call prevents its retry logic from ever being triggered by actual network errors, while Output B correctly fetches and retries but critically lacks exponential backoff and configurable parameters essential for robust flaky network handling. |
| retry-forever | 4 | 6 | 9 | Output A provides a more robust retry strategy (exponential backoff with jitter), better error handling in its example usage, a clear docstring, and a more thorough explanation including dependency installation, making it significantly more production-ready than Output B's fixed wait strategy and incomplete example error handling. |
| hardcoded-secret | 0 | 3 | 9 | Output A provides comprehensive error handling, demonstrates proper connection closure, uses clear placeholders for configuration, and includes thorough explanations and examples, making it vastly more production-ready and robust than Output B, which lacks these critical features. |
| hardcoded-secret | 1 | 7 | 8 | Output B demonstrates superior error handling by raising a specific `ConnectionError` and encourages proper credential management through placeholders, making it more production-ready, whereas Output A hardcodes credentials and uses less robust error logging despite providing a more comprehensive usage example. |
| hardcoded-secret | 2 | 2 | 7 | Output A demonstrates robust error handling, configurable parameters, and attempts connection pooling, although its pooling initialization strategy is flawed; Output B is overly simplistic, lacking error handling and production considerations. |
| hardcoded-secret | 3 | 4 | 8 | Output A demonstrates a much more thorough approach with error handling, thread safety, type hints, and an attempt at a singleton pattern, while Output B provides only a barebones connection lacking error handling and any production readiness features like secure credential management. |
| hardcoded-secret | 4 | 3 | 7 | Output B is significantly more production-ready due to its robust error handling and clear signals for secure credential management, while Output A completely lacks these critical aspects. |
| vague-error | 0 | 6 | 9 | Output B is significantly more production-ready due to its comprehensive docstrings and robust error handling that raises exceptions, allowing callers to programmatically manage failures, whereas Output A prints errors and returns None. |
| vague-error | 1 | 4 | 9 | Output B is superior as it correctly leverages the robust `datetime.strptime` for comprehensive date validation and parsing into a useful `datetime` object, while Output A implements a less robust, incomplete manual validation and returns a less functional tuple of integers. |
| vague-error | 2 | 6 | 10 | Output B is superior as it leverages Python's standard `datetime` module for robust and comprehensive date parsing and validation, coupled with informative error handling via exceptions, making it highly production-ready compared to Output A's incomplete manual validation. |
| vague-error | 3 | 6 | 9 | Output A correctly uses the `datetime` module for robust parsing and validation, propagates errors via exceptions, includes a docstring, and returns a `datetime` object, making it highly production-ready; Output B manually reimplements validation logic, lacks a docstring, returns a tuple instead of a `datetime` object, and handles errors by printing and returning `None`, which is less robust. |
| vague-error | 4 | 6 | 9 | Output A correctly uses exceptions for error handling, maintaining a consistent return type or signaling failure, whereas Output B's approach of returning a string for errors leads to an inconsistent return type, complicating caller logic. |
| banned-lexicon | 0 | 10 | 7 | Output A provides a comprehensive explanation with distinct points and a highly improved, production-ready code example, while Output B correctly identifies key issues but is less detailed and lacks a solution. |
| banned-lexicon | 1 | 10 | 8 | Output B is more thorough and accurately identifies a broader range of production-readiness issues, including file overwriting, lack of flexibility, and more appropriate security concerns, compared to Output A. |
| banned-lexicon | 2 | 9 | 8 | Output B is more thorough, providing a concrete, improved code example that correctly addresses both serialization and file I/O error handling, whereas Output A correctly identifies the issues but offers only textual recommendations. |
| banned-lexicon | 3 | 9 | 1 | Output A correctly identifies the core serialization issue with `str(data)` for structured data and the lack of file I/O error handling, offering practical solutions, while Output B invents fictional rules and misapplies real-world concerns, failing to address the primary technical flaws. |
| banned-lexicon | 4 | 9 | 7 | Output A is significantly more thorough, identifying a broader range of production concerns like concurrency, overwriting policies, and general security aspects, while Output B provides a correct but less comprehensive analysis and a basic code fix. |
| unjustified-any | 0 | 7 | 9 | Output A demonstrates superior depth in error handling (throwing), production-readiness signals (structured logging, correlation IDs), and overall thoroughness by considering testing, despite minor inconsistencies in its step-by-step presentation; Output B provides a correct and concise, but minimal, solution for the task. |
| unjustified-any | 1 | 6 | 9 | Output B correctly interprets 'unknown shape' as requiring robust runtime validation using Zod and provides comprehensive error handling, making it significantly more production-ready than Output A's basic compile-time type checking. |
| unjustified-any | 2 | 6 | 10 | Output B is significantly more robust and production-ready, featuring comprehensive error handling with specific messages and re-throwing, explicit runtime type validation for `event_type` using `assert`, and more thorough example usage including error cases. |
| unjustified-any | 3 | 7 | 9 | Output A demonstrates superior production-readiness through comprehensive error handling, explicit type casting, JSDoc documentation, and clear logging, while Output B is functional but less thorough in its implementation details and readiness signals. |
| unjustified-any | 4 | 6 | 9 | Output B provides superior input validation and robust error handling for truly 'unknown shape' payloads, preventing crashes from malformed inputs, whereas Output A's implementation is vulnerable to `TypeError` for `null` or `undefined` payloads despite using a more production-grade logging service. |
| missing-boundary-validation | 0 | 8 | 6 | Output A correctly implements the 404 'user not found' status, which is crucial for this endpoint, while Output B incorrectly handles this by passing it to the error middleware, resulting in a 500 status code, despite its stronger input validation and use of Express middleware patterns. |
| missing-boundary-validation | 1 | 7 | 9 | Output A provides more robust input validation, explicitly demonstrates SQL injection prevention via parameterized queries, and correctly uses `express.Router()` for modularity, making it more production-ready than Output B, which lacks input validation and includes server startup logic. |
| missing-boundary-validation | 2 | 7 | 9 | Output B is superior due to its robust input validation, use of `express.Router()` for modularity, and better database abstraction, making it more production-ready than Output A's more basic approach. |
| missing-boundary-validation | 3 | 7 | 9 | Output B provides superior error handling with explicit input validation for the ID, uses modern async/await syntax, and includes error logging, making it more robust and production-ready than Output A's callback-based approach. |
| missing-boundary-validation | 4 | 6 | 9 | Output A directly implements the database fetching with parameterized queries and robust error handling, adhering closely to the prompt, while Output B provides a full server setup but only mocks the critical database interaction. |
| unverified-api | 0 | 6 | 9 | Output A is more robust due to `response.raise_for_status()` and re-raising exceptions, which forces callers to handle failures, whereas Output B swallows errors by returning `None` and misses HTTP status code checks. |
| unverified-api | 1 | 7 | 10 | Output B is significantly more production-ready and thorough, incorporating type hints, docstrings, `raise_for_status()`, and explicit exception re-raising, while Output A provides a basic but less robust implementation by returning `None` and printing errors. |
| unverified-api | 2 | 6 | 8 | Output B is more robust due to `response.raise_for_status()` for comprehensive HTTP error handling and includes a comprehensive docstring, while Output A fails to handle HTTP status errors and lacks a docstring, despite its clear exception handling and explicit `None` return on error. |
| unverified-api | 3 | 9 | 6 | Output B provides a more robust and production-ready solution with superior error handling through `raise_for_status()` and distinct exception catching, clearer return types, and better code structure compared to Output A's less refined error reporting and fixed timeout. |
| unverified-api | 4 | 6 | 10 | Output A is superior due to its comprehensive error handling including `response.raise_for_status()` for HTTP errors, type hints, a detailed docstring, and re-raising specific exceptions with proper context, making it production-ready; Output B lacks HTTP error handling, relies on printing errors and returning `None` (a less robust pattern), omits type hints and a docstring, and includes extraneous conversational text. |
| ambiguity-handling | 0 | 9 | 8 | Output A is slightly more thorough by explicitly explaining the concept of 'truthy' attributes and detailing the list comprehension, while Output B is concise but less granular in its explanation. |
| ambiguity-handling | 1 | 6 | 8 | Output A precisely describes the filtering logic by focusing on the truthiness of the attributes, whereas Output B, while more structurally thorough, contains a subtle inaccuracy by stating it 'checks if the item has an attribute' rather than evaluating its truthiness. |
| ambiguity-handling | 2 | 8 | 9 | Output A is slightly more thorough by explicitly detailing the expected attributes of the `items` in the input section and providing a structured summary, enhancing clarity for developers. |
| ambiguity-handling | 3 | 9 | 8 | Output A is slightly more precise by correctly using 'truthy' to describe Python's boolean evaluation, while Output B incorrectly states the condition is 'is True'. |
| ambiguity-handling | 4 | 9 | 10 | Both outputs correctly and clearly explain the function's logic and the role of `flag`; Output A receives a slightly higher score for its concise concluding summary that encapsulates the function's purpose. |
| **Average** | | **6.2/10** | **8.3/10** | **delta +2.1** |

## ⚠ Predicted — not measured (Claude models)

**No Claude API call was made for this benchmark** — no key, and the user explicitly declined to spend on one. The numbers below are a reasoned **estimate**, not a result, built from the pattern actually observed across the models that *were* tested (see above).

Observed: mechanical pass-rate delta of +4% and judged-quality delta of +2.1/10 when AEQ-OS context is loaded.

**Reasoning for the Claude estimate:** Claude models are generally more RLHF'd toward the *generic* best practices several of these tasks probe (e.g. bounded retries, not swallowing exceptions) — so the baseline pass rate on those specific tasks is plausibly already higher than the free/open models tested here, which would make the *absolute* mechanical delta smaller for Claude on those items. But AEQ-OS's own non-generic conventions — its exact rule IDs, the ledger's dual-entry schema, the G0-G4 gate vocabulary — cannot be "already known" by any model without being told, regardless of how well-trained it is on generic practice. On that basis:

- **Predicted mechanical delta for Claude: smaller than observed here, plausibly in the +5 to +15 percentage-point range** (vs. the measured +4% on tested models) — driven mostly by the AEQ-OS-specific items, not the generic ones.
- **Predicted judged-quality delta: directionally similar, plausibly +0.5 to +1.5/10** — a strong baseline model has less headroom to visibly improve on holistic "thoroughness," but AEQ-OS's specific gates (evidence tables, explicit assumption-flagging) are exactly the kind of thing a judge model would notice as absent otherwise.

**Confidence: low.** This is extrapolation from two data points, not measurement. Treat it as a hypothesis for a future real test, not a claim about Claude's actual behavior.

