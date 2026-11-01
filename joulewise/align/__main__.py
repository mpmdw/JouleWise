"""Command line entry points for alignment matrices and log-tamper datasets."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Sequence

from joulewise.align.records import read_episodes, write_episodes
from joulewise.align.runner import run_matrix
from joulewise.align.tamper import delete_turns, drop_tool_calls, hide_scratchpad, random_tamper


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m joulewise.align")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run or resume a JSON matrix")
    run.add_argument("--matrix", type=Path, required=True)
    tamper = subparsers.add_parser("tamper", help="write a marked copy of episode JSONL")
    tamper.add_argument("--input", type=Path, required=True)
    tamper.add_argument("--output", type=Path, required=True)
    tamper.add_argument("--kind", choices=("delete_turns", "drop_tool_calls", "hide_scratchpad"),
                        required=True)
    tamper.add_argument("--indices", help="comma-separated zero-based indices for delete_turns")
    tamper.add_argument("--tool-name", action="append", default=[],
                        help="tool names to mark unlogged; repeat as needed")
    tamper.add_argument("--fraction", type=float, help="random selection fraction, in [0,1]")
    tamper.add_argument("--seed", type=int, default=0)
    arguments = parser.parse_args(argv)
    if arguments.command == "run":
        print(run_matrix(arguments.matrix))
        return 0
    episodes = read_episodes(arguments.input)
    rng = random.Random(arguments.seed)
    transformed = []
    for episode in episodes:
        if arguments.fraction is not None:
            episode = random_tamper(episode, rng, arguments.kind, arguments.fraction)
        elif arguments.kind == "delete_turns":
            indices = [int(index) for index in (arguments.indices or "").split(",") if index]
            episode = delete_turns(episode, indices)
        elif arguments.kind == "drop_tool_calls":
            episode = drop_tool_calls(episode, lambda call: call.name in arguments.tool_name)
        else:
            episode = hide_scratchpad(episode)
        transformed.append(episode)
    count = write_episodes(arguments.output, transformed)
    print(json.dumps({"output": str(arguments.output), "episodes": count}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
