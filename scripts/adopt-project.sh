#!/usr/bin/env bash
# Stamps a project with a project-root AGENTS.md pointer to ~/.ai_os/BOOT.md,
# so any tool that auto-reads a project-root instruction file (Claude Code,
# Cursor, and the broader AGENTS.md-adopting ecosystem) discovers AEQ-OS with
# zero chat prompting and zero per-machine setup — even on a teammate's clone
# that never ran install.sh. Non-destructive: appends to an existing AGENTS.md
# rather than overwriting it, same backup-never-delete ethos as install.sh.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${1:-$(pwd)}"

if [ ! -d "$TARGET_DIR" ]; then
  echo "error: $TARGET_DIR is not a directory" >&2
  exit 1
fi

SNIPPET_SRC="$REPO_DIR/templates/AGENTS.md"
if [ ! -f "$SNIPPET_SRC" ]; then
  echo "error: $SNIPPET_SRC not found — run this script from a checkout of the AEQ-OS repo" >&2
  exit 1
fi

TARGET_FILE="$TARGET_DIR/AGENTS.md"

if [ -f "$TARGET_FILE" ]; then
  if grep -q "ai_os/BOOT.md" "$TARGET_FILE" 2>/dev/null; then
    echo "$TARGET_FILE already points at BOOT.md. Nothing to do."
    exit 0
  fi
  echo "$TARGET_FILE already exists — appending the AEQ-OS pointer (never overwriting)."
  {
    echo ""
    echo "---"
    echo ""
    cat "$SNIPPET_SRC"
  } >> "$TARGET_FILE"
else
  cp "$SNIPPET_SRC" "$TARGET_FILE"
  echo "created $TARGET_FILE"
fi

echo
echo "Verify: grep -n 'ai_os/BOOT.md' \"$TARGET_FILE\""
echo "Anyone who opens $TARGET_DIR in an AGENTS.md-reading tool now gets AEQ-OS automatically, with no per-machine setup."
