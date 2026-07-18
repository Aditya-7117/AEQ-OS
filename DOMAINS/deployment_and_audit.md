# Deployment & Audit — Production Change Control

Extends `verification_protocol.md`: gates G0–G4 certify a diff; this file governs how a certified diff reaches production and how production stays certified. Loads whenever a task merges to a deployed branch or ships to production, regardless of route. Rule IDs: `DEP-n`.

## 1. Gate integration

- **DEP-1** — Nothing deploys unless G0–G4 passed **on the exact commit SHA being deployed**. Any edit after the gates ran invalidates them (VER-12); CI records gate attestation per SHA, and the deploy tool refuses unattested SHAs.
- **DEP-2 — Build once, promote.** The artifact tested in staging is byte-identical (by digest) to the artifact deployed to production. Rebuilding between environments reintroduces every variable the gates just eliminated.

## 2. Atomic micro-changes without downtime

- **DEP-3** — Production changes ship as the smallest independently releasable unit, each with a pre-written, pre-tested rollback command (the LIVE-22 discipline, generalized). If the rollback for a change cannot be stated in one line, the change is too big.
- **DEP-4 — N/N+1 coexistence.** Every deploy must be safe with both the old and new version running simultaneously (rolling/blue-green/canary all imply this window). Database changes follow expand→migrate→contract (FS-2); message and API schemas tolerate producers/consumers one version apart (FS-18).
- **DEP-5 — Flags decouple deploy from release.** Behavior changes ship dark behind flags defaulting off; the flip is a separate, individually reversible event. Dead flags are removed within a defined window — flag debt is dead code (CONST-30).
- **DEP-6** — Config changes are deploys: versioned, diffed line-by-line, gated, and rollback-able exactly like code (CONST-6 — silent defaults are the enemy).

## 3. Regression & structural validation loops

- **DEP-7** — Every deploy candidate runs the full regression battery: G2 suites, golden-path E2E smoke against staging, and — for AI systems — the AGT-20 / RAG-11 eval suites. An eval regression blocks a deploy exactly like a failing unit test.
- **DEP-8 — Post-deploy validation is automated, not observed.** After every deploy, a structural validation loop runs without a human driving it: health checks, synthetic transactions through the golden path, and domain invariant probes (trial balance LGR-10, index drift RAG-7, order reconciliation QT-ORD-4). A probe failure triggers automatic rollback and pages — the deploy is not "done" until the loop passes (VER-4 applied to production).
- **DEP-9 — Canary analysis is quantitative.** Error rate, latency percentiles, and the relevant business metrics compared against baseline with pre-declared abort thresholds. Promotion is a gate decision with evidence attached; "it soaked for an hour and nobody screamed" is not analysis.

## 4. Infrastructure drift tracking

- **DEP-10** — Infrastructure is code. Manual console or SSH mutations to production are forbidden outside break-glass — and break-glass actions are logged, ticketed, and reconciled back into code within 24 hours or reverted.
- **DEP-11** — Drift detection runs on schedule: `terraform plan -detailed-exitcode` (or the stack's equivalent) against unchanged code. A non-empty plan is a drift alert; drift is either adopted into code or reverted — never left as ambient state (the FS-12 reconciler pattern, applied to infra).
- **DEP-12** — Everything pinned: base images by digest, dependencies by lockfile (CONST-24), provider versions constrained. `latest` tags in production manifests are a violation on sight.
- **DEP-13** — Deploy identities are least-privilege and auditable; secrets rotate on schedule and on every personnel/agent scope change (CONST-26). The deploy pipeline can deploy — it cannot read production data.

## 5. Pre-merge isolated inspection (before triggering the merge tool)

- **DEP-14 — Isolation.** The final inspection runs in a fresh worktree/clone of the deployment branch — no local uncommitted state, no dirty caches. The full gate battery (G1–G4) re-runs there, and the merge decision may cite only evidence produced in that isolated pass.
- **DEP-15 — Redundancy inspection.** Enumerate the single points of failure the diff introduces or touches: new singleton services, sole consumers, unique locks, one-instance schedulers. Each SPOF is either eliminated or explicitly justified in the PR with its failure story (what happens when it dies, who gets paged, how it recovers).
- **DEP-16 — Deadlock/livelock inspection.** Over the diff: list every new lock acquisition and check it against the documented lock order (CONST-16); scan for await-while-holding-lock, unbuffered channel sends on shutdown paths, and synchronous circular service calls (A → B → A). Mechanical evidence required: the race detector / TSAN suite (QT-CONC-3) runs in the isolated pass, and its output is attached.
- **DEP-17 — Storm check.** Any new connection, retry, or restart logic is verified for herd behavior: jittered backoff (CONST-6), bounded reconnect rates (QT-WS-4), and crash-loop protection. Ten instances restarting politely is recovery; ten instances restarting simultaneously is an outage's second act.

## 6. Deploy audit trail

- **DEP-18** — Every deploy is an append-only recorded event: `{sha, artifact_digest, deployer identity (human or agent), gate attestation links, rollback command, start/end timestamps, result}` — the LGR-2 spirit applied to releases. The deploy log answers "what was running at 14:32 last Tuesday" in one query.
- **DEP-19 — Self-improving audit.** Every rollback and hotfix gets a postmortem that names which gate should have caught the defect — and patches that gate (a new probe, a new banned pattern, a new eval case). An incident that doesn't strengthen a gate will repeat.
- **DEP-20 — Freeze conditions are programmatic.** An open Sev-1, an unexplained reconciliation break (LGR-12), or a live-trading gate breach (any LIVE-n FAIL) blocks all deploys except the fix itself — enforced by the pipeline, honored by the agent, subject to the LIVE-18 calendar windows.
