# Production Readiness — Prototype-to-Institutional-Grade Gate

`deployment_and_audit.md` (`DEP-n`) owns *release mechanics* — build-once-promote, canary, drift, rollback. It does not own whether the system itself is institutional-grade before it ever ships. This file is that pre-launch audit: it cites existing rules rather than duplicating them, and it loads whenever `deployment_and_audit.md` loads (the `deploy_rule` in `ROUTER_MAP.json`) — a diff can be release-engineered correctly and still be running on an architecture that isn't production-grade; both checks are required, neither substitutes for the other. Rule IDs: `PROD-n`.

## 1. Architecture & scalability

- **PROD-1** — Before a first production deploy, and on any architecture-altering change after, produce a one-page readiness note: single points of failure (reusing `DEP-15`'s enumeration), the layer that breaks first under 10x load, and a stated capacity ceiling with the metric that will show it's approaching.
- **PROD-2** — Every externally reachable API enforces authentication and authorization on every route (`SEC-4`), input validation at the boundary (`CONST-10`, `SEC-14`), rate limiting per identity, and a documented contract (OpenAPI/protobuf) that CI checks for breaking changes (`FS-18`).

## 2. Secrets & environment

- **PROD-3** — Every credential reachable from the deploy target traces to a `SEC-1` lifecycle record. No credential appears in an env-var dump, a container image layer, or a build log — extends `CONST-26`/`DEP-13` with an explicit audit step, not just a policy statement.

## 3. Observability & auditing

- **PROD-4** — Observability floor: structured logs (`CONST-28`) plus metrics (`CONST-29`) plus at least one distributed trace path across the golden path. A production system with logs but no way to answer "why was request X slow" fails this gate.
- **PROD-5** — Every paging alert links to a runbook stating likely cause and the first three response steps. An alert with no runbook trains responders to ignore pages.

## 4. Error handling & recovery

- **PROD-6** — Every external call (network, database, third-party API) has a bounded timeout, a retry policy per `CONST-6`, and a fallback/degradation behavior that is itself tested — not assumed to work because it's there.
- **PROD-7** — A backup/restore drill has actually run, on a schedule, with recovery time recorded. An untested backup is a hypothesis, not a control.

## 5. Performance

- **PROD-8** — A performance baseline exists before launch: a load test against the stack's declared latency tier (`STACK-2`'s table), with results attached. "Should be fast enough" is banned-lexicon territory (`model_adaptation.md` §2) applied to non-functional requirements.

## 6. Attack surface & pipeline

- **PROD-9** — Every open port, public endpoint, and default credential is enumerated and justified; anything not explicitly needed is closed — `SEC-2`'s least-privilege principle applied at the infrastructure level.
- **PROD-10** — The CI/CD pipeline itself passes the same scrutiny as the code it ships: no manual steps in the critical path (`DEP-10`), secrets injected rather than embedded (`SEC-1`), and the pipeline's own permissions are least-privilege (`DEP-13`).
- **PROD-11** — Production credentials, data, and network paths are unreachable from staging/dev by construction — network policy or account boundary, never convention alone.

## 7. Compliance & dependencies

- **PROD-12** — Every restricted or confidential data store (`SEC-8`'s classification) has a retention policy, a deletion path, and an access-audit trail before it holds real user data.
- **PROD-13** — Production dependency trees are scanned for known CVEs and license compatibility (`SEC-11`/`SEC-12`) as a release-blocking check, not an advisory one.

## 8. Output & remediation

- **PROD-14** — This gate produces a scored report — PASS / FLAG / BLOCK per pillar — mirroring the evidence-table discipline of `VER-9`, attached to the deploy record (`DEP-18`). BLOCK items block release; FLAG items ship with an owner and a date.
- **PROD-15** — Mechanically-fixable findings (a missing timeout, an unpinned dependency, a missing rate limit) are fixed directly in the same pass and cited against the `PROD-n` item they close, rather than merely reported. Findings that require a design decision are reported, not guessed at (`INT-7`). This stays honest about the architecture: the fix happens because the agent edited files during a normal session, not because a new always-on enforcement service now exists.
- **PROD-16** — Re-audit trigger: a PASS is valid for the architecture it audited. A load-bearing change — a new external dependency, a new data store, a new public endpoint — invalidates it, the same way `VER-12` invalidates the base gates on any post-gate edit.

## 9. First launch

- **PROD-17** — For a system's *first* production launch specifically — as opposed to a routine deploy of an already-launched system — every pillar (`PROD-1` through `PROD-13`) must show PASS or an explicitly owned, dated FLAG before launch. This is the concrete prototype-to-institutional-grade transition the rest of the deploy pipeline assumes already happened.

## 10. Tiering

- **PROD-18 — Tier-awareness.** Lite tier (default) runs this audit on-demand, agent-driven, checklist-style. A Performance tier (opt-in, separate tooling) may script the mechanical portions — dependency/CVE scans, lockfile checks, timeout/rate-limit greps — into a real `scripts/` tool the way `validate.py` already scripts the rule-ID contiguity check. Same PASS/FLAG/BLOCK contract either way.
