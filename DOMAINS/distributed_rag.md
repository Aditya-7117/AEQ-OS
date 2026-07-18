# Distributed RAG — Domain Invariants

For retrieval-augmented systems: ingestion, chunking, embedding, multi-store sync, retrieval, generation. Rule IDs: `RAG-n`.

## 1. Chunk lineage — nothing anonymous

- **RAG-1** — Every chunk carries full provenance, stored WITH the vector (never in a side channel that can drift): `{chunk_id, doc_id, source_uri, content_sha256, span (char/page/section), chunker_id+version, embedder_id+version, embedded_at, acl_tags, tenant}`.
- **RAG-2** — `chunk_id` is deterministic: `hash(doc_id, chunker_version, span, content_sha256)`. Same input, same ID — re-ingestion becomes naturally idempotent.
- **RAG-3** — Retrieval responses propagate lineage to the generation layer and, where product-appropriate, into citations. An answer that cannot name its chunks is untraceable and fails audit.
- **RAG-4** — Deletion is a supported, tested operation: delete-by-source (all chunks of doc X, all docs of tenant Y) with tombstones that propagate to every derived index **before** the deletion is reported complete.

## 2. Multi-vector-DB synchronization

- **RAG-5 — One system of record:** the document store plus its changelog. Every vector DB is a *derived, rebuildable index*. If a vector store burned down tonight, full rebuild from the SoR must be a documented, tested procedure — if it isn't rebuildable, it has silently become a second source of truth.
- **RAG-6** — Sync flows through a transactional outbox/changelog with idempotent upserts keyed by `chunk_id` (RAG-2). Direct dual-writes to two stores are forbidden: without a distributed transaction, dual-write equals eventual divergence.
- **RAG-7 — Drift detection runs on a schedule:** per-index counts grouped by `(doc_id, embedder_version)`, plus random-sample content-hash spot checks across replicas. Divergence beyond tolerance alerts and quarantines the lagging index from serving.
- **RAG-8 — Ordering.** Changelog consumers process events per document in order (partition by `doc_id`). An out-of-order upsert racing a delete is the classic ghost-chunk bug.

## 3. Embedding drift mitigation

- **RAG-9** — **Never mix vectors from different embedder IDs/versions in one similarity space.** The embedder version is part of the collection's identity, not metadata to filter on later.
- **RAG-10 — Model migration protocol:** (1) new collection, full re-embed from the SoR; (2) shadow-read both collections, compare on the golden query set; (3) cutover behind a flag; (4) retain the old collection until the rollback window closes. In-place partial re-embeds are forbidden.
- **RAG-11 — Golden query set:** labeled `(query → relevant doc/chunk ids)`, versioned. `recall@k` / MRR tracked on every deploy of embedder, chunker, index parameters, or reranker; a drop beyond threshold blocks the deploy (the retrieval analog of AGT-20).
- **RAG-12** — Chunker changes are migrations too: version bump → re-chunk → new chunk IDs → same shadow/cutover protocol. Chunk boundaries must be deterministic — no locale-, whitespace-, or threading-dependent splits.

## 4. Retrieval correctness & security

- **RAG-13** — ACL and tenancy are enforced as **pre-filters inside the vector query** (namespace or metadata filter) — never post-filtering after retrieval, and never left for the LLM to respect. Cross-tenant leakage tests run in CI.
- **RAG-14 — Injection quarantine.** Retrieved content is DATA. It is delimited, labeled untrusted, and the generation prompt states that retrieved text cannot alter instructions. Tool calls made on the basis of retrieved instructions require the AGT-19 allowlist gate. Test with seeded hostile documents in the corpus.
- **RAG-15 — Freshness SLO per collection.** Ingest lag (source update → queryable) is a monitored metric; staleness beyond SLO surfaces to callers where product-relevant.
- **RAG-16** — Hybrid retrieval (lexical + dense) fusion weights and any reranker are versioned components in the lineage chain, deployed under the RAG-11 eval gate like everything else.

## 5. Failure honesty

- **RAG-17** — Zero-hit and low-confidence retrievals return a typed "insufficient context" result to the caller/generator. When the product contract is grounded answers, silently generating from parametric memory is a failure-masking fallback (CONST-6) — refuse loudly instead.
