# AEQ-OS Benchmark Results — gemini:gemini-2.5-flash

Generated 2026-07-25T15:31:16+00:00. See `benchmarks/README.md` for full methodology. Sample size: 10 tasks × 3 trials × 2 conditions — a real but modest sample; treat rates as indicative, not definitive.

## Track 1 — Mechanical (objective, PASS/FAIL against a named rule ID)

| Task | Rule | Confidence | Baseline pass rate | AEQ-OS pass rate | Delta |
|---|---|---|---|---|---|
| ambiguity-handling | `META-15` | heuristic | 40% | 0% | -40% |
| banned-lexicon | `META-6` | strong | 100% | 100% | +0% |
| hardcoded-secret | `CONST-26` | strong | 100% | 100% | +0% |
| missing-boundary-validation | `CONST-10` | heuristic | 40% | 100% | +60% |
| money-float | `CONST-11` | strong | 0% | 100% | +100% |
| retry-forever | `CONST-6` | heuristic | 80% | 100% | +20% |
| silent-except | `CONST-4` | strong | 100% | 100% | +0% |
| unjustified-any | `CONST-9` | strong | 80% | 100% | +20% |
| unverified-api | `CONST-2` | strong | 100% | 100% | +0% |
| vague-error | `CONST-19` | heuristic | 100% | 80% | -20% |
| **Overall** | | | **74%** | **88%** | **+14%** |

## Track 2 — Holistic quality rating (subjective, model-judged — NOT a mechanical measurement)

Judge: `ollama:qwen2.5-coder:7b` (never judges `gemini-gemini-2.5-flash`'s own outputs — cross-model by construction). Blind: judge sees only 'Output A'/'Output B', condition-to-label assignment randomized per trial.

| Task | Trial | Baseline score | AEQ-OS score | Judge reasoning |
|---|---|---|---|---|
| money-float | 0 | 8 | 9 | Output B receives a higher score due to its use of Decimal for financial calculations, which provides greater precision and avoids common pitfalls with floating-point arithmetic. It also includes more detailed error handling and adheres to additional best practices for robustness. |
| money-float | 1 | 8 | 9 | Output A adheres more strictly to the constraints and provides comprehensive error handling, while Output B is simpler but might introduce floating-point inaccuracies. |
| money-float | 2 | 8 | 9 | Output B is rated higher for adhering more strictly to the AEQ-OS Constitution and providing comprehensive testing, while Output A receives a slightly lower score due to not fully utilizing Decimal for monetary calculations. |
| money-float | 3 | 6 | 9 | Output A is more thorough and follows stricter monetary calculation rules, while Output B is simpler but less rigorous. |
| money-float | 4 | 7 | 9 | Output A is more thorough and adheres to best practices for financial calculations, while Output B is simpler but lacks the precision and robust error handling of Output A. |
| silent-except | 0 | 8 | 9 | Output A includes additional AEQ-OS Constitution rules and more detailed error handling messages, while Output B provides a straightforward implementation with type hints and basic error handling. |
| silent-except | 1 | 8 | 9 | Output B demonstrates a more thorough and structured approach with type hints, structured logging, and detailed error handling. Output A is simpler but still correct. |
| silent-except | 2 | 9 | 8 | Output A provides a more concise implementation with fewer comments, which can be easier to understand quickly. Output B includes detailed documentation and structured logging, which adds value but makes the code slightly longer. |
| silent-except | 3 | 8 | 7 | Output A provides more comprehensive error handling and is more production-ready due to its detailed exception messages and explicit type hints. Output B lacks some of these features but is structured with clear constants, which could be useful for documentation. |
| silent-except | 4 | 7 | 8 | Output A provides more detailed error handling, context in exception messages, and uses type hints, making it slightly more robust. Output B includes basic testing examples but lacks the level of detail and explicitness found in Output A. |
| retry-forever | 0 | 7 | 9 | Output A is more detailed with structured logging and type hints, while Output B is simpler with basic logging and does not include as many error handling details. |
| retry-forever | 1 | 8 | 9 | Output B provides a more robust and well-documented function with additional features such as input validation, logging, and structured error handling. Output A is straightforward but lacks some of the advanced features and best practices found in Output B. |
| retry-forever | 2 | 7 | 8 | Output A is more comprehensive with detailed logging, custom exceptions, and extensive comments. Output B is simpler but provides a good starting point. |
| retry-forever | 3 | 5 | 9 | Output A provides a more robust and compliant implementation with bounded retries, proper error handling, structured logging, and observability metrics. Output B lacks important security practices, does not handle input validation, and uses infinite retries without addressing the rules against it. |
| retry-forever | 4 | 7 | 8 | Output A adheres more closely to the given constraints, including bounded retries, jittered backoff, and structured logging. It also provides a custom exception class which is useful for error handling. Output B, while functional, lacks some of these features and does not adhere as strictly to the provided guidelines. |
| hardcoded-secret | 0 | 8 | 9 | Output B receives a slightly higher score for its more thorough adherence to best practices, including structured logging, custom exceptions, and robust error handling. However, Output A is still very strong with comprehensive error handling and detailed instructions. |
| hardcoded-secret | 1 | 8 | 9 | Output B provides a more detailed and comprehensive approach to handling errors, configuration, and security compared to Output A. |
| hardcoded-secret | 2 | 6 | 9 | Output A provides a more detailed, structured, and comprehensive solution that adheres to various security, error-handling, and production-readiness best practices. Output B is basic and lacks the depth of explanation and comprehensive coverage required for a robust solution. |
| hardcoded-secret | 3 | 8 | 9 | Output B provides a more detailed and secure approach with comprehensive error handling, type hints, and better security practices. |
| hardcoded-secret | 4 | 9 | 8 | Output A is more straightforward and easier to understand, while Output B includes more advanced features like structured logging and strict adherence to operational guidelines. |
| vague-error | 0 | 6 | 8 | Output A demonstrates more thorough error handling and includes a test suite, while Output B provides basic functionality with limited error handling. |
| vague-error | 1 | 9 | 10 | Output B provides both the function implementation and a comprehensive set of unit tests following best practices for testing, making it more production-ready. |
| vague-error | 2 | 8 | 9 | Output B demonstrates a deeper understanding of error-handling depth and adherence to AEQ-OS Constitution rules. |
| vague-error | 3 | 8 | 9 | Output A provides more comprehensive error handling and detailed exception messages, while Output B is simpler but still functional. |
| vague-error | 4 | 8 | 9 | Output B provides a more detailed error handling mechanism with custom exceptions, enhanced documentation, and a comprehensive test suite. |
| banned-lexicon | 0 | 7 | 8 | Output A provides a detailed explanation with multiple reasons why the function is not ready for production use, including non-negotiable rules violations. Output B concisely identifies key issues such as JSON format mismatch and hardcoded filename but lacks the depth of explanation found in Output A. |
| banned-lexicon | 1 | 7 | 8 | Output A provides more specific details about security and observability concerns that are critical in production environments. Output B correctly identifies the primary issue with JSON serialization but lacks some of the detailed reasoning provided in Output A. |
| banned-lexicon | 2 | 7 | 8 | Both outputs correctly identify issues with the function, but Output B provides a more comprehensive and detailed analysis, including specific AEQ-OS principles that are violated. |
| banned-lexicon | 3 | 9 | 7 | Both outputs correctly identify key issues but Output B provides more specific and actionable feedback, including the use of `json.dumps()` for proper JSON serialization and handling common I/O errors. |
| banned-lexicon | 4 | 7 | 8 | Output A provides a concise explanation of the issues with the function, while Output B offers more detailed reasoning and additional points to consider. |
| unjustified-any | 0 | 7 | 8 | Output A demonstrates more advanced techniques with schema validation using Zod, while Output B focuses on basic type guards without the additional security and clarity that comes with schema validation. |
| unjustified-any | 1 | 8 | 9 | Output B provides more robust error handling and structured logging, adhering to security and operational best practices. |
| unjustified-any | 2 | 8 | 7 | Output A provides a clear, concise, and thorough implementation of the `handleWebhook` function with detailed type checking and error handling. Output B is more verbose and includes an extensive test suite, but it doesn't provide as much clarity in its reasoning and explanation. |
| unjustified-any | 3 | 9 | 8 | Output A demonstrates a good balance of type safety, error handling, and thoroughness. Output B adds structured logging and dependency management but has some redundancy and unnecessary complexity. |
| unjustified-any | 4 | 9 | 8 | Output A provides a comprehensive and robust solution with detailed runtime type checking, clear error handling, and thorough logging. Output B uses schema validation which is an effective approach for ensuring input integrity but lacks the explicit runtime type checks and in-depth error handling found in Output A. |
| missing-boundary-validation | 0 | 7 | 9 | Output A demonstrates a more complete and robust solution with schema validation, correlation IDs, logging, and error handling. Output B is a simplified example that lacks some of these features but provides a basic understanding of how to handle the task. |
| missing-boundary-validation | 1 | 7 | 9 | Output B demonstrates a higher level of correctness confidence, error-handling depth, production-readiness signals, and overall thoroughness. It includes robust input validation, detailed structured logging with correlation IDs, and explicit handling for various failure cases. |
| missing-boundary-validation | 2 | 7 | 9 | Output B demonstrates a more thorough approach with TypeScript, structured error handling, input validation, and comprehensive logging, while Output A is simpler and lacks these features. |
| missing-boundary-validation | 3 | 7 | 9 | Output A provides more thoroughness with TypeScript, error handling, logging, and observability, while Output B is simpler and lacks some of these advanced features. |
| missing-boundary-validation | 4 | 8 | 9 | Output B provides a more comprehensive and secure implementation, including input validation, structured logging, error handling, and authorization middleware. Output A is simpler but lacks some of the advanced features for production-readiness. |
| unverified-api | 0 | 8 | 9 | Output A is rated higher due to its comprehensive error handling, detailed logging, and adherence to the AEQ-OS Constitution. Output B is solid but lacks some of the advanced features and structure found in Output A. |
| unverified-api | 1 | 8 | 9 | Output A provides more detailed and specific error handling, custom exceptions, and comprehensive logging, while Output B offers a straightforward approach with basic error handling. |
| unverified-api | 2 | 8 | 9 | Output A provides more detailed error handling, includes custom exceptions with context, and is generally more thorough. Output B lacks some of the advanced features and structure present in Output A. |
| unverified-api | 3 | 9 | 8 | Output A is more straightforward and covers the basic requirements well. Output B introduces unnecessary complexity and structured logging that may not be needed for this simple task. |
| unverified-api | 4 | 9 | 8 | Output A is rated higher due to its more comprehensive error handling and better logging, while Output B has a more structured approach with custom exceptions. |
| ambiguity-handling | 0 | 9 | 10 | Both outputs provide accurate summaries of the function's purpose and behavior. Output A explicitly states the role of `flag`, while Output B also correctly identifies it as a switch or toggle between 'active' and 'pending'. Both are equally thorough in their explanations. |
| ambiguity-handling | 1 | 9 | 9 | Both outputs accurately describe the function's behavior and provide a clear explanation of what the `flag` parameter is for. |
| ambiguity-handling | 2 | 8 | 9 | Both outputs provide accurate and detailed explanations of the function's behavior, with Output A being slightly more concise. |
| ambiguity-handling | 3 | 8 | 9 | Both outputs provide a correct summary of the function, with Output B being slightly more thorough and precise. |
| ambiguity-handling | 4 | 10 | 9 | Both outputs correctly summarize the function's behavior and explain that `flag` acts as a switch between using the `active` and `pending` attributes for filtering. |
| **Average** | | **7.8/10** | **8.6/10** | **delta +0.8** |

## ⚠ Predicted — not measured (Claude models)

**No Claude API call was made for this benchmark** — no key, and the user explicitly declined to spend on one. The numbers below are a reasoned **estimate**, not a result, built from the pattern actually observed across the models that *were* tested (see above).

Observed: mechanical pass-rate delta of +14% and judged-quality delta of +0.8/10 when AEQ-OS context is loaded.

**Reasoning for the Claude estimate:** Claude models are generally more RLHF'd toward the *generic* best practices several of these tasks probe (e.g. bounded retries, not swallowing exceptions) — so the baseline pass rate on those specific tasks is plausibly already higher than the free/open models tested here, which would make the *absolute* mechanical delta smaller for Claude on those items. But AEQ-OS's own non-generic conventions — its exact rule IDs, the ledger's dual-entry schema, the G0-G4 gate vocabulary — cannot be "already known" by any model without being told, regardless of how well-trained it is on generic practice. On that basis:

- **Predicted mechanical delta for Claude: smaller than observed here, plausibly in the +5 to +15 percentage-point range** (vs. the measured +14% on tested models) — driven mostly by the AEQ-OS-specific items, not the generic ones.
- **Predicted judged-quality delta: directionally similar, plausibly +0.5 to +1.5/10** — a strong baseline model has less headroom to visibly improve on holistic "thoroughness," but AEQ-OS's specific gates (evidence tables, explicit assumption-flagging) are exactly the kind of thing a judge model would notice as absent otherwise.

**Confidence: low.** This is extrapolation from two data points, not measurement. Treat it as a hypothesis for a future real test, not a claim about Claude's actual behavior.

