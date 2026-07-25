#!/usr/bin/env bash
# Removes the generated watcher unit for one project. Only ever touches the
# AEQ-OS-labeled unit it (or install_watcher.sh) created — never any other
# LaunchAgent/systemd unit on the machine. If the unit is currently loaded,
# this refuses to delete the file out from under launchd/systemd (that
# would leave the already-loaded job running from memory until reboot) and
# instead prints the unload command to run first — consistent with this
# toolkit never calling launchctl/systemctl's mutating commands itself.
set -euo pipefail

PROJECT="${1:?usage: uninstall_watcher.sh <project-path>}"
PROJECT="$(cd "$PROJECT" && pwd)"
LABEL_NAME="$(printf '%s' "$(basename "$PROJECT")" | tr -c 'a-zA-Z0-9-' '-' | tr 'A-Z' 'a-z')"

OS="$(uname -s)"

if [ "$OS" = "Darwin" ]; then
  LABEL="com.aeq-os.watcher.${LABEL_NAME}"
  PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"

  if [ ! -f "$PLIST" ]; then
    echo "no watcher installed for $PROJECT ($PLIST not found)"
    exit 0
  fi

  if launchctl list 2>/dev/null | grep -q "$LABEL"; then
    echo "the watcher is currently loaded in launchd. Unload it first:"
    echo "  launchctl unload -w \"$PLIST\""
    echo "then re-run this script to remove the generated plist."
    exit 1
  fi

  rm "$PLIST"
  echo "removed: $PLIST"

elif [ "$OS" = "Linux" ]; then
  UNIT="aeq-os-watcher-${LABEL_NAME}.service"
  UNIT_PATH="$HOME/.config/systemd/user/$UNIT"

  if [ ! -f "$UNIT_PATH" ]; then
    echo "no watcher installed for $PROJECT ($UNIT_PATH not found)"
    exit 0
  fi

  if systemctl --user is-active --quiet "$UNIT" 2>/dev/null; then
    echo "the watcher is currently active in systemd. Stop it first:"
    echo "  systemctl --user disable --now $UNIT"
    echo "then re-run this script to remove the generated unit."
    exit 1
  fi

  rm "$UNIT_PATH"
  echo "removed: $UNIT_PATH"
  echo "run 'systemctl --user daemon-reload' to fully clear it"

else
  echo "no automated installer/uninstaller exists for '$OS' — nothing to remove here."
fi

CONFIG="$PROJECT/.ai_os/performance.json"
if [ -f "$CONFIG" ]; then
  python3 - "$CONFIG" <<'PYEOF'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
cfg = json.loads(p.read_text())
cfg["watcher"] = {"enabled": False}
p.write_text(json.dumps(cfg, indent=2) + "\n")
PYEOF
  echo "updated: $CONFIG (watcher.enabled = false)"
fi
