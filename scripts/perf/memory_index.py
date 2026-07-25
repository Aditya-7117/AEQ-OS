#!/usr/bin/env python3
"""AEQ-OS Performance tier — memory search (closes MEM-15).

Lite tier (default, no install) is agent-driven grep/read over
`<project>/.ai_os/memory/`. This tool is the opt-in Performance-tier upgrade:
a SQLite FTS5 index (zero dependencies — stdlib only) as the floor, with an
auto-detected upgrade to local-embedding semantic search if an embedding
model is already available via a locally-running Ollama server. Never a
paid API, never installed silently — running `build` once is the opt-in.

Usage:
    memory_index.py build   [--path DIR] [--no-embeddings]
    memory_index.py update  [--path DIR]
    memory_index.py search  QUERY [--path DIR] [--semantic] [--limit N]
    memory_index.py status  [--path DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import struct
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

OLLAMA_BASE = "http://localhost:11434"
EMBED_MODEL_PATTERNS = ("embed",)  # nomic-embed-text, mxbai-embed-large, all-minilm, ...
PREFERRED_EMBED_MODELS = ("nomic-embed-text", "mxbai-embed-large", "all-minilm")
INDEXABLE_SUFFIXES = {".md", ".json", ".txt"}


def index_db_path(mem_dir: Path) -> Path:
    return mem_dir / "index.sqlite3"


def detect_ollama_embedding_model(timeout: float = 1.5) -> str | None:
    """Probe the local Ollama API only (no external network call). Returns
    an already-pulled embedding-capable model name, or None."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None

    names = [m.get("name", "") for m in data.get("models", [])]
    for preferred in PREFERRED_EMBED_MODELS:
        for name in names:
            if name.split(":")[0] == preferred:
                return name
    for name in names:
        if any(p in name.lower() for p in EMBED_MODEL_PATTERNS):
            return name
    return None


def compute_embedding(model: str, text: str, timeout: float = 30.0) -> list[float] | None:
    payload = json.dumps({"model": model, "prompt": text[:8000]}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/embeddings", data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None
    return data.get("embedding")


def pack_embedding(vec: list[float]) -> bytes:
    return struct.pack(f"<{len(vec)}f", *vec)


def unpack_embedding(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"<{n}f", blob))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def parse_tier(content: str) -> str:
    """Best-effort tag extraction, purely a display convenience — MEM-1
    already requires records to state their own tier; this never overrides
    that, it just surfaces it in search results when findable."""
    m = re.search(r"^\s*(?:type|tier)\s*:\s*(\w+)", content, re.MULTILINE)
    return m.group(1) if m else "unspecified"


def open_db(mem_dir: Path) -> sqlite3.Connection:
    mem_dir.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(index_db_path(mem_dir))
    con.execute(
        "CREATE TABLE IF NOT EXISTS files ("
        " path TEXT PRIMARY KEY, tier TEXT, mtime REAL, content_hash TEXT)"
    )
    con.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5("
        " path, tier, content)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS embeddings ("
        " path TEXT PRIMARY KEY, model TEXT, vector BLOB)"
    )
    return con


def scan_files(mem_dir: Path) -> list[Path]:
    if not mem_dir.exists():
        return []
    out = []
    for p in sorted(mem_dir.rglob("*")):
        if p.is_file() and p.suffix in INDEXABLE_SUFFIXES and p.name != "performance.json":
            out.append(p)
    return out


def index_file(con: sqlite3.Connection, mem_dir: Path, path: Path, embed_model: str | None) -> None:
    rel = str(path.relative_to(mem_dir))
    content = path.read_text(errors="replace")
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    tier = parse_tier(content)
    mtime = path.stat().st_mtime

    con.execute("DELETE FROM files WHERE path = ?", (rel,))
    con.execute("DELETE FROM memory_fts WHERE path = ?", (rel,))
    con.execute(
        "INSERT INTO files (path, tier, mtime, content_hash) VALUES (?, ?, ?, ?)",
        (rel, tier, mtime, content_hash),
    )
    con.execute(
        "INSERT INTO memory_fts (path, tier, content) VALUES (?, ?, ?)",
        (rel, tier, content),
    )

    if embed_model:
        vec = compute_embedding(embed_model, content)
        if vec:
            con.execute(
                "INSERT OR REPLACE INTO embeddings (path, model, vector) VALUES (?, ?, ?)",
                (rel, embed_model, pack_embedding(vec)),
            )


def cmd_build(args: argparse.Namespace) -> int:
    root = lib.find_project_root(args.path)
    mem_dir = lib.memory_dir(root)
    files = scan_files(mem_dir)

    embed_model = None if args.no_embeddings else detect_ollama_embedding_model()

    db_path = index_db_path(mem_dir)
    if db_path.exists():
        db_path.unlink()
    con = open_db(mem_dir)
    for f in files:
        index_file(con, mem_dir, f, embed_model)
    con.commit()
    con.close()

    config = lib.load_performance_config(root)
    config["tier"] = "performance"
    config["memory_index"] = {
        "backend": "fts5",
        "embeddings": f"ollama:{embed_model}" if embed_model else "none",
        "last_build": lib.now_iso(),
    }
    lib.save_performance_config(root, config)

    lib.ok(f"indexed {len(files)} file(s) under {mem_dir}")
    if embed_model:
        lib.ok(f"semantic search enabled — local Ollama model: {embed_model}")
    elif args.no_embeddings:
        lib.info("FTS5 only — embeddings explicitly skipped (--no-embeddings). "
                  "Run `build` without that flag when you want semantic search.")
    else:
        lib.info("FTS5 only — no local embedding model detected. Not required; "
                  "install one free/open-source (e.g. `ollama pull nomic-embed-text`) "
                  "to enable `search --semantic`.")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    root = lib.find_project_root(args.path)
    mem_dir = lib.memory_dir(root)
    if not index_db_path(mem_dir).exists():
        lib.info("no index yet — running build instead")
        return cmd_build(args)

    config = lib.load_performance_config(root)
    embed_cfg = config.get("memory_index", {}).get("embeddings", "none")
    force_no_embed = getattr(args, "no_embeddings", False)
    embed_model = None if force_no_embed else (
        embed_cfg.split(":", 1)[1] if embed_cfg.startswith("ollama:") else None
    )

    con = open_db(mem_dir)
    known = dict(con.execute("SELECT path, mtime FROM files").fetchall())
    on_disk = scan_files(mem_dir)
    on_disk_rel = {str(p.relative_to(mem_dir)) for p in on_disk}

    changed = 0
    for p in on_disk:
        rel = str(p.relative_to(mem_dir))
        mtime = p.stat().st_mtime
        if rel not in known or known[rel] < mtime:
            index_file(con, mem_dir, p, embed_model)
            changed += 1

    removed = 0
    for rel in list(known):
        if rel not in on_disk_rel:
            con.execute("DELETE FROM files WHERE path = ?", (rel,))
            con.execute("DELETE FROM memory_fts WHERE path = ?", (rel,))
            con.execute("DELETE FROM embeddings WHERE path = ?", (rel,))
            removed += 1

    con.commit()
    con.close()

    config["memory_index"]["last_build"] = lib.now_iso()
    lib.save_performance_config(root, config)

    lib.ok(f"update complete — {changed} file(s) reindexed, {removed} removed")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    root = lib.find_project_root(args.path)
    mem_dir = lib.memory_dir(root)
    if not index_db_path(mem_dir).exists():
        lib.bad("no index found — run `memory_index.py build` first")
        return 1

    con = open_db(mem_dir)

    if args.semantic:
        row = con.execute("SELECT DISTINCT model FROM embeddings LIMIT 1").fetchone()
        if not row:
            lib.bad("no embeddings in this index — rebuild with a local Ollama "
                    "embedding model available, or drop --semantic for FTS5 search")
            return 1
        model = row[0]
        qvec = compute_embedding(model, args.query)
        if not qvec:
            lib.bad(f"could not reach Ollama model '{model}' for the query embedding "
                    "— falling back is not automatic; drop --semantic to use FTS5")
            return 1
        scored = []
        for rel, blob in con.execute("SELECT path, vector FROM embeddings"):
            sim = cosine_similarity(qvec, unpack_embedding(blob))
            scored.append((sim, rel))
        scored.sort(reverse=True)
        for sim, rel in scored[: args.limit]:
            print(f"  {sim:.3f}  {rel}")
        if not scored:
            lib.info("no results")
    else:
        rows = con.execute(
            "SELECT path, tier, snippet(memory_fts, 2, '[', ']', '...', 12) "
            "FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
            (args.query, args.limit),
        ).fetchall()
        for path, tier, snippet in rows:
            print(f"  [{tier}] {path}")
            print(f"      {snippet}")
        if not rows:
            lib.info("no results")

    con.close()
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = lib.find_project_root(args.path)
    mem_dir = lib.memory_dir(root)
    config = lib.load_performance_config(root)
    idx = config.get("memory_index", {})

    if not index_db_path(mem_dir).exists():
        lib.info(f"no Performance-tier index for {root} — Lite tier (grep/read) applies")
        return 0

    con = open_db(mem_dir)
    n_files = con.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    n_embed = con.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
    con.close()

    lib.ok(f"index present — {n_files} file(s), last build {idx.get('last_build')}")
    if idx.get("embeddings", "none") != "none":
        lib.ok(f"semantic search: {idx['embeddings']} ({n_embed} embedded)")
    else:
        lib.info("semantic search: not enabled (FTS5 only)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="rebuild the index from scratch")
    p_build.add_argument("--path", help="project path (default: auto-detect from cwd)")
    p_build.add_argument("--no-embeddings", action="store_true")
    p_build.set_defaults(func=cmd_build)

    p_update = sub.add_parser("update", help="incrementally reindex changed files")
    p_update.add_argument("--path", help="project path (default: auto-detect from cwd)")
    p_update.add_argument("--no-embeddings", action="store_true",
                           help="skip Ollama calls even if this project has embeddings configured "
                                "(used by watcher.py so the unattended background loop never "
                                "competes with other local-model RAM usage)")
    p_update.set_defaults(func=cmd_update)

    p_search = sub.add_parser("search", help="query the index")
    p_search.add_argument("query")
    p_search.add_argument("--path", help="project path (default: auto-detect from cwd)")
    p_search.add_argument("--semantic", action="store_true", help="use embeddings instead of FTS5")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.set_defaults(func=cmd_search)

    p_status = sub.add_parser("status", help="show index state for the current project")
    p_status.add_argument("--path", help="project path (default: auto-detect from cwd)")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
