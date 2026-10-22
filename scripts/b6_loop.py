#!/opt/homebrew/bin/python3.13
"""Block-6 controls with live Git/GitHub runners; merge supplies lane adapters."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.loop import DEFAULT_LOOP_ROOT, Loop
from joulewise.b6.mailer import GitHubTransport, Mailer
from joulewise.flags.catalog import load_catalog


def live_run(argv, **kwargs):
    try:
        return subprocess.run(argv, **{"capture_output": True, "text": True, "timeout": 120,
                                       "check": False, **kwargs})
    except subprocess.TimeoutExpired:
        if kwargs.get("check"):
            raise
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="command_timeout")


def main(argv=None, *, factory=Loop):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loop-root", default=os.environ.get("JW_B6_LOOP_ROOT"))
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
    repo = Path(args.repo_root)
    config = json.loads((Path(args.config) if args.config else repo / "configs/b6/loop.json").read_text())
    args.loop_root = args.loop_root or config.get("loop_root", DEFAULT_LOOP_ROOT)
    catalog = load_catalog(repo / config["flag_catalog"])
    mailer = Mailer(args.loop_root, catalog, clock=time.time, transport=GitHubTransport(config["github_repo"], live_run))
    loop = factory(args.repo_root, args.loop_root, config=config, run=live_run, mailer=mailer)
    if args.command == "status":
        print(json.dumps(loop.read_state(), indent=2))
        return 0
    if args.command == "tick":
        return loop.tick()
    return loop.control(args.command, pack=getattr(args, "pack", None), attempts=getattr(args, "attempts", 5),
                        session_id=getattr(args, "session_id", None))


if __name__ == "__main__":
    raise SystemExit(main())
