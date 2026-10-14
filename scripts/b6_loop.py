#!/opt/homebrew/bin/python3.13
"""Block-6 controls. Merge supplies live runners and lane adapters."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.loop import DEFAULT_LOOP_ROOT, Loop


def main(argv=None, *, factory=Loop):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loop-root", default=os.environ.get("JW_B6_LOOP_ROOT", DEFAULT_LOOP_ROOT))
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--config")
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("tick", "status", "hold", "resume", "reharvested"):
        sub = subs.add_parser(name)
        # Support the override on either side of the subcommand.
        sub.add_argument("--loop-root", default=argparse.SUPPRESS)
        if name in {"resume", "hold"}:
            sub.add_argument("--pack")
        if name == "resume":
            sub.add_argument("--attempts", type=int, default=5)
        if name == "reharvested":
            sub.add_argument("session_id")
    args = parser.parse_args(argv)
    config = json.loads(Path(args.config).read_text()) if args.config else None
    loop = factory(args.repo_root, args.loop_root, config=config)
    if args.command == "status":
        print(json.dumps(loop.read_state(), indent=2))
        return 0
    if args.command == "tick":
        return loop.tick()
    return loop.control(args.command, pack=getattr(args, "pack", None), attempts=getattr(args, "attempts", 5),
                        session_id=getattr(args, "session_id", None))


if __name__ == "__main__":
    raise SystemExit(main())
