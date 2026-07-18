# Security Policy

AEQ-OS is a set of instruction files consumed by coding agents (Claude Code, Google Antigravity, Cursor, and any AGENTS.md-compatible tool). It contains no executable runtime, no server, and no dependency graph in the traditional sense — but it directly shapes how agents write code for **live trading systems and financial ledgers**, so a defect here has real downstream blast radius.

## What counts as a security issue here

- A rule in `CORE/` or `DOMAINS/` that, if followed exactly as written, would produce an insecure pattern (e.g., a credential-handling rule that's actually wrong, a race condition the concurrency rules fail to close, a `live_trading_gate.md` gap that would let unsafe code ship to a live venue).
- `scripts/validate.py` or the CI workflow silently passing on content that violates its own stated invariants (rule-ID contiguity, banned-lexicon, JSON schema).
- `install.sh` / `install.ps1` doing anything beyond copying/symlinking files into `~/.ai_os` (e.g., unexpected network calls, privilege escalation, clobbering unrelated files without a backup).

## What is *not* a security issue

- Disagreement with a specific rule's design (open an issue instead — see `CONTRIBUTING.md`).
- Missing coverage for a domain AEQ-OS doesn't yet address.

## Reporting

Please **do not open a public issue** for a suspected security-relevant defect (e.g., a `LIVE-n` gate gap that could let unsafe live-trading code ship). Instead, use GitHub's private vulnerability reporting: **Security → Report a vulnerability** on this repository. You'll get an acknowledgment within a reasonable timeframe and credit in the fix's changelog entry unless you ask to remain anonymous.

## Scope note

AEQ-OS instructs agents; it does not enforce anything at runtime. Following every rule in this repository is not a substitute for your own security review, static analysis, and — for anything in `DOMAINS/live_trading_gate.md` — independent sign-off before real capital is at risk.
