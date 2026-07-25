#!/usr/bin/env python3
"""AEQ-OS Performance tier — opt-in background watcher (MEM-15/SEC-18 tier-awareness).

Never started by AEQ-OS itself. This process only exists if the user
explicitly registered it via install_watcher.sh (launchd/systemd) or ran it
directly. It is a bounded, owned loop with a clean shutdown path (CONST-17):
SIGTERM/SIGINT exit the loop instead of leaving anything orphaned, and
--max-iterations lets it be run to completion in a test without being killed.

Each iteration: reindex `.ai_os/memory/` if anything changed (cheap, every
--interval seconds) and, on a separate longer cadence, re-run the security
scan (--security-interval seconds, default 6h).

Usage:
    watcher.py --path DIR [--interval 300] [--security-interval 21600] [--max-iterations N]
"""
from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
import memory_index  # noqa: E402
import security_scan  # noqa: E402

_stop = False


def _handle_signal(signum, frame) -> None:  # noqa: ARG001
    global _stop
    _stop = True


def watch(root: Path, interval: float, security_interval: float, max_iterations: int | None) -> int:
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    mem_dir = lib.memory_dir(root)
    lib.ok(f"watcher started for {root} (interval={interval}s, security_interval={security_interval}s)")

    last_security_scan = 0.0
    iteration = 0

    while not _stop:
        iteration += 1
        known = {}
        db_path = memory_index.index_db_path(mem_dir)
        if db_path.exists():
            con = memory_index.open_db(mem_dir)
            known = dict(con.execute("SELECT path, mtime FROM files").fetchall())
            con.close()

        on_disk = memory_index.scan_files(mem_dir)
        changed = any(
            str(p.relative_to(mem_dir)) not in known
            or known[str(p.relative_to(mem_dir))] < p.stat().st_mtime
            for p in on_disk
        )
        removed = bool(known) and any(
            rel not in {str(p.relative_to(mem_dir)) for p in on_disk} for rel in known
        )

        if changed or removed or not db_path.exists():
            # no_embeddings=True always, on purpose: this loop runs unattended and
            # indefinitely, so it must never make an Ollama call that could compete
            # with RAM another already-running local-model workload needs. Embeddings
            # only ever happen when the user consciously runs `memory_index.py build`
            # themselves; the watcher keeps FTS5 fresh in between.
            args = argparse.Namespace(path=str(root), no_embeddings=True)
            memory_index.cmd_update(args)
            lib.info(f"[iter {iteration}] memory index updated (FTS5 only — embeddings never run unattended)")

        now = time.monotonic()
        if now - last_security_scan >= security_interval:
            report = security_scan.run_scan(root)
            flags = sum(1 for r in report["results"] if r["status"] == "FLAG")
            lib.info(f"[iter {iteration}] security scan complete — {flags} flag(s)")
            last_security_scan = now

        if max_iterations is not None and iteration >= max_iterations:
            break

        for _ in range(int(interval)):
            if _stop:
                break
            time.sleep(1)

    lib.ok(f"watcher stopped cleanly after {iteration} iteration(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", required=True, help="project path to watch")
    parser.add_argument("--interval", type=float, default=300, help="memory-index check interval, seconds")
    parser.add_argument("--security-interval", type=float, default=21600, help="security-scan interval, seconds")
    parser.add_argument("--max-iterations", type=int, default=None, help="stop after N iterations (testing)")
    args = parser.parse_args()

    root = lib.find_project_root(args.path)
    return watch(root, args.interval, args.security_interval, args.max_iterations)


if __name__ == "__main__":
    sys.exit(main())
