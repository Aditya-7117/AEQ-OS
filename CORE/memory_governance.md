# Memory Governance — Portable, Tiered Recall

A memory architecture any tool wired to `BOOT.md` can use identically — plain files on disk, not a proprietary feature of any one vendor's agent. Recall is what lets an agent skip re-deriving what it already learned; the rules below govern what gets written, what gets trusted, and what gets forgotten. Rule IDs: `MEM-n`.

## 1. Tier model

- **MEM-1 — Four tiers.** *Working* (current session/task state), *episodic* (project-specific decisions and history), *semantic* (durable facts about the user/environment that outlive any one project), *procedural* (mistake- and success-pattern records, schema owned by `CORE/learning_engine.md`). Every persisted record is tagged with its tier — an untagged record is unrecallable by scope and defeats `MEM-14`.
- **MEM-2 — Portable storage.** Records live at a project-local, plain-file path (`.ai_os/memory/`-style) so any tool reading `BOOT.md` gets the same store. Episodic/decision memory worth surviving a clone may be committed; semantic/user memory that's machine- or person-specific stays local (gitignored) by default.

## 2. Write discipline

- **MEM-3** — Persist a fact only if it is non-derivable from the code or git history and would change a future agent's behavior. Code patterns, file structure, and who-changed-what are re-derivable by reading the repo (`git log`/`git blame`) — writing them to memory is redundant weight, not recall.
- **MEM-4** — Every record carries provenance: who or what stated it, when (absolute date, not "yesterday"), and why. An unattributed fact is not a memory, it's a guess wearing a memory's clothes.
- **MEM-5 — Recall before write.** Check whether an existing record already covers the fact; update it in place with a changelog line rather than writing a duplicate that can silently drift from the original.

## 3. Trust discipline

- **MEM-6 — Staleness is the default assumption.** A recalled memory naming a specific file, symbol, config value, or external state is a claim about the past. Verify it before *acting* on it — grep, read, or re-check — never before merely *discussing* it. "Memory says X" is not the same claim as "X is true now."
- **MEM-7** — Current observed state always overrides a stale record. When they conflict, update or delete the record; never act on both as if they agreed.
- **MEM-8 — No fabricated memory.** Inventing a memory record to sound more informed than the evidence supports is a memory-specific instance of `CONST-2`/`META-3` — no invented reality applies to the agent's own recollection, not only to APIs.

## 4. Retrieval discipline

- **MEM-9 — Intent-scoped retrieval.** Pull only the tier/records relevant to the classified intent and route (`INT-14`), not the entire store. A memory system that dumps its full contents into every context defeats the token-budget discipline `AGT-1` already asks of everything else.
- **MEM-10** — Index or summarize first, fetch the full record only on demand — the same two-stage discipline as loading a domain file only when `ROUTER_MAP.json` actually matches it, applied to memory instead of rules.

## 5. Exclusions & minimization

- **MEM-11** — Secrets and credentials never enter any memory tier, in any form. A write pipeline that could capture one needs a redaction step before persistence, not after (`CONST-26`, `SEC-10`).
- **MEM-12** — Memory about the user is scoped to what materially improves collaboration — role, preferences, domain expertise — never stored for its own sake, and never presented as certain when it's actually inferred.

## 6. Lifecycle

- **MEM-13 — Expiry and pruning.** Episodic and semantic records get reviewed at a defined cadence (a milestone close, a new session block); records that no longer reflect the project are removed or marked superseded. Procedural (`LEARN`) records are the exception — append-only, never pruned, because the entire point is not repeating a mistake even after the project that produced it has moved on.
- **MEM-14 — Cross-tool continuity.** The plain-file store is the portable source of truth every tool falls back to. A tool with a richer native memory feature may layer on top of it, but never instead of it — a fact written by one tool must be recallable by another.

## 7. Tiering

- **MEM-15 — Tier-awareness.** The rules above bind regardless of implementation. Lite tier (default) recall is agent-driven grep/read over the plain-file store. A Performance tier (opt-in, separate tooling) may back the same store with a local search index for faster or smarter recall — never a paid API or subscription, never installed without explicit opt-in, and never changing what gets written or what a record means.
