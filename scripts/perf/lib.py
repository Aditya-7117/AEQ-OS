"""Shared foundation for the AEQ-OS Performance tier (opt-in, MEM-15/SEC-18/PROD-18).

Every tool here operates on whatever project the caller is currently working
in, not on the AEQ-OS repo itself. Project root is the nearest ancestor
directory containing `.git/` or an existing `.ai_os/`, falling back to the
given/current directory if neither is found.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def ok(msg: str) -> None:
    print(f"  {_c('32', '✓')} {msg}")


def bad(msg: str) -> None:
    print(f"  {_c('31', '✗')} {msg}")


def info(msg: str) -> None:
    print(f"  {_c('2', '·')} {msg}")


def warn(msg: str) -> None:
    print(f"  {_c('33', '!')} {msg}")


def find_project_root(start: str | Path | None = None) -> Path:
    """Walk up from `start` (default: cwd) looking for `.git/` or `.ai_os/`.
    Falls back to `start` itself if neither is found anywhere above it —
    the caller may still be a valid target (e.g. `memory_index.py build`
    creating `.ai_os/memory/` for the first time)."""
    here = Path(start).resolve() if start else Path.cwd()
    for candidate in [here, *here.parents]:
        if (candidate / ".git").exists() or (candidate / ".ai_os").exists():
            return candidate
    return here


def memory_dir(project_root: Path) -> Path:
    return project_root / ".ai_os" / "memory"


def performance_config_path(project_root: Path) -> Path:
    return project_root / ".ai_os" / "performance.json"


def load_performance_config(project_root: Path) -> dict:
    path = performance_config_path(project_root)
    if not path.exists():
        return {
            "tier": "lite",
            "memory_index": {"backend": None, "embeddings": "none", "last_build": None},
            "watcher": {"enabled": False},
        }
    return json.loads(path.read_text())


def save_performance_config(project_root: Path, config: dict) -> None:
    path = performance_config_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
