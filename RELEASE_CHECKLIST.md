# Release Checklist

Run through this before tagging any new version — including the first public push. Not a one-time document; reused on every release.

## Content
- [ ] `python3 scripts/validate.py` passes clean
- [ ] Every new/changed rule has a rule ID, appended after the current max for its prefix
- [ ] `docs/ARCHITECTURE.md`'s rule index matches the real counts (re-derive, don't hand-edit)
- [ ] `README.md`'s rule-count badge and prose match the same real counts
- [ ] `CHANGELOG.md` has an entry for the version being tagged

## Security
- [ ] `grep -rniE "api[_-]?key|secret|password|token|BEGIN.*PRIVATE KEY"` over the repo returns nothing but rule text *about* those concepts
- [ ] No personal email, absolute home-directory path, or machine-specific identifier anywhere in tracked files
- [ ] `.gitignore` covers local backups (`*.bak-*`), OS cruft (`.DS_Store`), and anything env/secret-shaped
- [ ] `git log --all --oneline` reviewed for anything staged-then-removed that might still be reachable in history

## Repo hygiene
- [ ] `LICENSE`, `SECURITY.md`, `CODEOWNERS`, `CONTRIBUTING.md` present and current
- [ ] Issue templates and PR template render correctly on GitHub (preview before push)
- [ ] CI workflow (`validate.yml`) green on the branch being tagged
- [ ] `install.sh` and `install.ps1` tested on a clean-ish state (backup path exercised, not just the happy path)

## Versioning
- [ ] Version bumped in `ROUTER_MAP.json` (`version` field) to match the tag
- [ ] Tag follows manual semver per `CHANGELOG.md`'s header note

## Release
- [ ] `git tag -a vX.Y.Z -m "..."` on the commit that passed every item above
- [ ] GitHub Release notes are the `CHANGELOG.md` section for this version, not regenerated ad hoc
- [ ] If this is the **first public push**: repository visibility is deliberately set to Public (not left Private by default), and the URL has been sanity-checked by opening it logged out
