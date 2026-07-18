# Full-Stack Architecture — Domain Invariants

For backend services, APIs, databases, and platform-grade systems (enterprise ledgers, manufacturing, asset inventories). The theme is one idea applied everywhere: **derived state must be rebuildable from a single source of record, and every boundary is a contract.** Rule IDs: `FS-n`.

## 1. Schema migration safety

- **FS-1** — Migrations are versioned, in-repo, forward-only artifacts. Every migration ships with a tested rollback, or an explicit `IRREVERSIBLE:` marker plus the recovery plan (restore point, backfill procedure). An unmarked irreversible migration is a violation, not an oversight.
- **FS-2 — Expand → migrate → contract.** Never rename, retype, or drop in one step. Add the new column/table → dual-write → backfill → switch reads → drop the old shape in a *later* release. Application versions N and N+1 must both run correctly against the schema at every intermediate step (DEP-4 depends on this).
- **FS-3** — Destructive migrations (DROP, type narrowing, adding NOT NULL to populated columns) require a pre-flight data audit (row counts, violating-row query returning zero) and a verified restore point, and run only through the DEP gates.
- **FS-4** — Every migration states its **lock profile**. No long-running exclusive locks on hot tables: `lock_timeout` set, indexes created `CONCURRENTLY`, table rewrites identified in review (in Postgres, know which `ALTER` forms rewrite). A migration that can stall production traffic is a NO-GO until reworked.
- **FS-5** — Schema is the contract: ORM models / generated types are regenerated from the schema (or the schema from a single model source) in CI. Drift between code models and the live schema is a build failure, not a runtime surprise.

## 2. Stateless vs stateful boundaries

- **FS-6** — Every service declares itself STATELESS or STATEFUL in its README/header. Stateless services hold no request-surviving state: no in-memory sessions, no local files as truth, no "temporary" caches that became load-bearing. All durable state lives in declared stores.
- **FS-7** — Sticky-session dependence is forbidden. Any instance can serve any request; instance death mid-request is recoverable by retry (which requires FS-11 idempotency).
- **FS-8** — Stateful components (databases, queues, caches, object stores) are enumerated in one topology document with owner, durability class, and the date of the last successful **restore drill** — a backup that has never been restored is a hope, not a backup.
- **FS-9** — Caches are ephemeral by contract: the system must be *correct* (if slower) with every cache cold. Correctness may never depend on cache contents (see FS-16 for financial values).

## 3. Asynchronous event reconciliation

- **FS-10** — Cross-store writes go through a transactional outbox or CDC — never dual-write (`DB commit` + `publish` as two independent operations is the same divergence bug as RAG-6). The event is part of the transaction or it does not exist.
- **FS-11** — Delivery is at-least-once everywhere; every consumer is idempotent by key. A claim of exactly-once is a design smell: prove the dedupe mechanism or design for redelivery.
- **FS-12** — Every async flow has a **reconciler**: a scheduled sweeper comparing source-of-record against derived state, repairing or alerting on divergence (the same pattern family as LGR-12 and RAG-7). Eventual consistency without a reconciler is just divergence with optimism.
- **FS-13** — Dead-letter queues are monitored with age and depth alerts. A DLQ nobody drains is silent data loss wearing a uniform (CONST-4).

## 4. Platform-grade transactions & zero-drift caching

- **FS-14** — Mutations of money, inventory, or asset quantities run at `SERIALIZABLE`, or under explicit row locking (`SELECT ... FOR UPDATE`) with a documented lock order (CONST-16). Default `READ COMMITTED` is inadmissible for balance math — read-compute-write across two transactions is the check-then-act race at database scale.
- **FS-15** — Quantity updates are set-based atomic operations (`UPDATE ... SET qty = qty - :n WHERE id = :id AND qty >= :n`, then assert one row affected) or serializable transactions with a bounded, jittered retry-on-conflict loop (CONST-6). Read-modify-write in application memory is forbidden for these fields.
- **FS-16 — Zero-drift caching.** Cached entries for ledger/inventory/position values carry the row version they were read at; invalidation is key-based on write, with TTL as a backstop only — TTL is never the consistency strategy. **Decisions never read the cache:** any code path that authorizes spending, allocation, or orders reads the store (or a version-checked read-through that hits the store on mismatch). Dashboards may be stale; decisions may not.

## 5. API contract safety — anti-cascade rules

- **FS-17** — Contracts are schema-first artifacts in the repo (OpenAPI / protobuf / GraphQL SDL). Server and all clients generate their types from the artifact; a hand-written duplicate of a wire type is a bug even while it happens to match.
- **FS-18** — A contract diff checker runs in CI with backward-compatibility rules: no removed or renamed fields, no type changes, no new *required* fields on existing endpoints. Breaking changes require a new version and a deprecation window with consumer sign-off — a micro-change that breaks an unseen consumer is not micro.
- **FS-19** — Compile-time types do not survive the wire: every boundary keeps its runtime validation wrapper (CONST-10) even in fully typed stacks. The generated types say what *should* arrive; the validator establishes what *did*.
- **FS-20 — Blast-radius map.** Every contract lists its consumers — including non-obvious ones like RAG ingestion jobs (RAG-15 freshness depends on your API) and trading pipelines (QT-WS-6 parsers). A contract-changing PR names the affected consumers and links their verification evidence (VER-9 rows). Unknown consumers are the cascade; the map is the countermeasure.
