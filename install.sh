#!/usr/bin/env bash
# Installs AEQ-OS into ~/.ai_os as a symlink to this repo, so editing the repo
# is editing the live installed OS. Existing ~/.ai_os content is backed up,
# never deleted.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HOME/.ai_os"

for f in BOOT.md ROUTER_MAP.json CORE DOMAINS; do
  if [ ! -e "$REPO_DIR/$f" ]; then
    echo "error: $REPO_DIR/$f not found — run this script from a checkout of the AEQ-OS repo" >&2
    exit 1
  fi
done

if [ -L "$TARGET" ]; then
  echo "~/.ai_os is already a symlink -> $(readlink "$TARGET")"
  if [ "$(readlink "$TARGET")" = "$REPO_DIR" ]; then
    echo "already installed from this checkout. Nothing to do."
    exit 0
  fi
  echo "repointing to this checkout."
  rm "$TARGET"
elif [ -e "$TARGET" ]; then
  BACKUP="$HOME/.ai_os.backup-$(date +%Y%m%d%H%M%S)"
  echo "~/.ai_os already exists as a real directory — backing it up to $BACKUP"
  mv "$TARGET" "$BACKUP"
fi

ln -s "$REPO_DIR" "$TARGET"
echo "installed: ~/.ai_os -> $REPO_DIR"

echo
echo "Next step — wire this into your agent tools (one-time, per tool):"
echo "  Claude Code:  append templates/CLAUDE.md-snippet.md's line to ~/.claude/CLAUDE.md"
echo "  Antigravity:  mkdir -p ~/.gemini && cp \"$REPO_DIR/templates/AGENTS.md\" ~/.gemini/AGENTS.md"
echo "  Cursor:       paste templates/cursor-user-rules.txt into Settings -> Rules -> User Rules"
echo
echo "Verify: grep -rn \"QT-STOP-3\" ~/.ai_os/  should return a match."
