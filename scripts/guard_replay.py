#!/usr/bin/env python3
"""Replay refusing guards offline, or project host-only evidence from local Git."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).absolute().parent.parent))
from joulewise.guard_replay import BUILTINS, REPO, replay


def local_read(name):
    """No symlinks or outside-tree inputs; reject forbidden components BEFORE open/stat."""
    path = Path(name)
    if path.is_absolute():
        path = path.relative_to(REPO)
    if not path.parts or any(p in ("..", "restricted", "night-custody", "night-archive")
                             or p.startswith(("jw-b5-", "night-")) for p in path.parts):
        raise ValueError("replay inputs must be unrestricted files inside this clone")
    fd = os.open(REPO, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        child = os.open(path.parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
        with os.fdopen(child, "rb") as stream:
            return stream.read()
    finally:
        os.close(fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("collect", help="JSON host-only projection of allowlisted local committed R0 reports")
    run = sub.add_parser("run", help="evaluate imported guard implementations; JSON to stdout")
    run.add_argument("corpus")
    run.add_argument("--guard", action="append", help="built-in name or trusted repository module:function")
    run.add_argument("--run-seconds", type=float, required=True)
    run.add_argument("--idle-bound", type=float, default=.05)
    run.add_argument("--require-qualified", action="store_true",
                     help="exit 2 unless each guard has a qualified representative benign stratum")
    sub.add_parser("list", help="list built-in adapters")
    args = parser.parse_args(argv)
    if args.command == "list":
        print("\n".join(BUILTINS))
        return 0
    if args.command == "collect":
        from joulewise.guard_replay_corpus import collect
        result = collect()
    else:
        raw = local_read(args.corpus)
        result = replay(json.loads(raw), args.guard or list(BUILTINS),
                        run_seconds=args.run_seconds, bound=args.idle_bound)
        result["corpus_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    if args.command == "run" and args.require_qualified:
        return 0 if all(any(s["assessment"] == "WITHIN_BOUND" for s in g["strata"])
                        and not any(s["assessment"] == "ABOVE_BOUND" for s in g["strata"])
                        for g in result["guards"]) else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
