#!/usr/bin/env bash
# Generates a launchd (macOS) or systemd --user (Linux) unit for the opt-in
# AEQ-OS Performance-tier watcher (watcher.py), for one specific project.
#
# This script writes the unit file and flips `.ai_os/performance.json`'s
# watcher.enabled flag to true (project-local JSON, reversible, not a
# system change) — but it deliberately does NOT register the unit with
# launchd/systemd itself. That's a persistent, reboot-surviving process,
# so activating it is one explicit command this script prints for you to
# run yourself, on your own schedule.
set -euo pipefail

PERF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="${1:?usage: install_watcher.sh <project-path> [--interval SECONDS]}"
INTERVAL="300"

shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --interval) INTERVAL="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

PROJECT="$(cd "$PROJECT" && pwd)"
LABEL_NAME="$(printf '%s' "$(basename "$PROJECT")" | tr -c 'a-zA-Z0-9-' '-' | tr 'A-Z' 'a-z')"
WATCHER_PY="$PERF_DIR/watcher.py"

if [ ! -f "$WATCHER_PY" ]; then
  echo "error: $WATCHER_PY not found — run this from a checkout of the AEQ-OS repo" >&2
  exit 1
fi

PYTHON_BIN="$(command -v python3)"

flip_config() {
  python3 - "$PROJECT" <<'PYEOF'
import json, sys
from pathlib import Path
project = Path(sys.argv[1])
cfg_path = project / ".ai_os" / "performance.json"
cfg_path.parent.mkdir(parents=True, exist_ok=True)
cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {
    "tier": "performance",
    "memory_index": {"backend": None, "embeddings": "none", "last_build": None},
    "watcher": {"enabled": False},
}
cfg["watcher"] = {"enabled": True}
cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
print(f"updated {cfg_path}")
PYEOF
}

OS="$(uname -s)"

if [ "$OS" = "Darwin" ]; then
  LABEL="com.aeq-os.watcher.${LABEL_NAME}"
  PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
  LOG_DIR="$PROJECT/.ai_os"
  mkdir -p "$LOG_DIR"

  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_BIN}</string>
        <string>${WATCHER_PY}</string>
        <string>--path</string>
        <string>${PROJECT}</string>
        <string>--interval</string>
        <string>${INTERVAL}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/watcher.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/watcher.log</string>
</dict>
</plist>
EOF

  flip_config
  echo "generated: $PLIST"
  echo
  echo "This has NOT been registered with launchd yet. To activate it, run:"
  echo "  launchctl load -w \"$PLIST\""
  echo
  echo "To check it's running:  launchctl list | grep ${LABEL}"
  echo "To stop and remove it:  scripts/perf/uninstall_watcher.sh \"$PROJECT\""

elif [ "$OS" = "Linux" ]; then
  UNIT_DIR="$HOME/.config/systemd/user"
  mkdir -p "$UNIT_DIR"
  UNIT="aeq-os-watcher-${LABEL_NAME}.service"
  UNIT_PATH="$UNIT_DIR/$UNIT"

  cat > "$UNIT_PATH" <<EOF
[Unit]
Description=AEQ-OS Performance-tier watcher for ${PROJECT}

[Service]
Type=simple
ExecStart=${PYTHON_BIN} ${WATCHER_PY} --path ${PROJECT} --interval ${INTERVAL}
Restart=on-failure

[Install]
WantedBy=default.target
EOF

  flip_config
  echo "generated: $UNIT_PATH"
  echo
  echo "This has NOT been registered with systemd yet. To activate it, run:"
  echo "  systemctl --user daemon-reload"
  echo "  systemctl --user enable --now ${UNIT}"
  echo
  echo "To check it's running:  systemctl --user status ${UNIT}"
  echo "To stop and remove it:  scripts/perf/uninstall_watcher.sh \"$PROJECT\""

else
  echo "No automated installer for '$OS' — this hasn't been tested against it."
  echo "Run the watcher directly instead, or wire it into your own scheduler"
  echo "(e.g. Windows Task Scheduler running):"
  echo "  ${PYTHON_BIN} \"${WATCHER_PY}\" --path \"${PROJECT}\" --interval ${INTERVAL}"
  exit 0
fi
