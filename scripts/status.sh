#!/usr/bin/env bash
# On-demand health check — not a dashboard. There is no background process to
# monitor; this script verifies real, current facts each time you run it:
# is the install wired correctly, does the rulebook validate, and is it
# showing up in your actual project history.
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS="0"
FAIL="0"

ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; PASS=$((PASS + 1)); }
bad()  { printf "  \033[31m✗\033[0m %s\n" "$1"; FAIL=$((FAIL + 1)); }
info() { printf "  \033[2m·\033[0m %s\n" "$1"; }

echo "AEQ-OS status — $(date '+%Y-%m-%d %H:%M:%S')"
echo

echo "Install wiring:"
TARGET="$HOME/.ai_os"
if [ -L "$TARGET" ] && [ "$(readlink "$TARGET")" = "$REPO_DIR" ]; then
  ok "~/.ai_os -> $REPO_DIR"
elif [ -L "$TARGET" ]; then
  bad "~/.ai_os is a symlink but points elsewhere: $(readlink "$TARGET")"
elif [ -e "$TARGET" ]; then
  bad "~/.ai_os exists but is a real directory, not a symlink to this repo — run install.sh"
else
  bad "~/.ai_os does not exist — run install.sh"
fi

VERSION=$(python3 -c "import json; print(json.load(open('$REPO_DIR/ROUTER_MAP.json'))['version'])" 2>/dev/null)
if [ -n "$VERSION" ]; then
  ok "ROUTER_MAP.json version $VERSION"
else
  bad "could not read version from ROUTER_MAP.json"
fi
echo

echo "Per-tool pointers:"
if [ -f "$HOME/.claude/CLAUDE.md" ] && grep -q "ai_os/BOOT.md" "$HOME/.claude/CLAUDE.md" 2>/dev/null; then
  ok "Claude Code — ~/.claude/CLAUDE.md points at BOOT.md"
else
  bad "Claude Code — ~/.claude/CLAUDE.md missing or not pointing at BOOT.md (see templates/CLAUDE.md-snippet.md)"
fi

if [ -f "$HOME/.gemini/AGENTS.md" ] && grep -q "ai_os/BOOT.md" "$HOME/.gemini/AGENTS.md" 2>/dev/null; then
  ok "Google Antigravity — ~/.gemini/AGENTS.md points at BOOT.md"
else
  bad "Google Antigravity — ~/.gemini/AGENTS.md missing or not pointing at BOOT.md (see templates/AGENTS.md)"
fi

info "Cursor — global User Rules live in app settings, not a file; can't be checked from disk. See templates/cursor-user-rules.txt."
echo

echo "Rulebook integrity:"
if python3 "$REPO_DIR/scripts/validate.py" >/tmp/aeq-os-validate.$$  2>&1; then
  ok "scripts/validate.py passed"
else
  bad "scripts/validate.py failed — see /tmp/aeq-os-validate.$$"
fi
echo

echo "Evidence of real use (rule-ID citations in your project git history):"
FOUND_ANY=0
if [ -d "$HOME/Projects" ]; then
  for proj in "$HOME"/Projects/*/; do
    [ -d "${proj}.git" ] || continue
    [ "$proj" = "$REPO_DIR/" ] && continue
    HITS=$(git -C "$proj" log --all --oneline -i \
      --grep='CONST-[0-9]' --grep='QT-[A-Z]*-[0-9]' --grep='LIVE-[0-9]' \
      --grep='AGT-[0-9]' --grep='RAG-[0-9]' --grep='LGR-[0-9]' \
      --grep='FS-[0-9]' --grep='UIUX-[0-9]' --grep='DEP-[0-9]' --grep='RESEARCH-[0-9]' \
      2>/dev/null | wc -l | tr -d ' ')
    if [ "${HITS:-0}" -gt 0 ]; then
      ok "$(basename "$proj") — $HITS commit(s) citing a rule ID"
      FOUND_ANY=1
    fi
  done
fi
if [ "$FOUND_ANY" -eq 0 ]; then
  info "no rule-ID citations found yet in ~/Projects/*/.git history — expected until you've done work in a wired-up session"
fi
echo

echo "----"
echo "$PASS check(s) passed, $FAIL failed."
[ "$FAIL" -eq 0 ]
