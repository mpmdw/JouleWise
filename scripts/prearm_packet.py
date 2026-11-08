#!/usr/bin/env python3
"""Build off-MBP or verify a pinned static packet; never arm or run a measurement."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.prearm_packet import PacketError, build, verify  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--recipe-sha256", required=True, help="digest from independently reviewed handoff")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--packet-sha256", help="reviewed packet digest; required to verify")
    args = parser.parse_args(argv)
    if args.command == "verify" and not args.packet_sha256:
        parser.error("verify requires --packet-sha256 from the reviewed handoff")
    try:
        raw = args.recipe.read_bytes()
        if hashlib.sha256(raw).hexdigest() != args.recipe_sha256:
            raise PacketError("recipe digest mismatch")
        recipe = json.loads(raw)
        result = (build(args.root, recipe, args.packet) if args.command == "build" else
                  verify(args.root, recipe, args.packet, args.packet_sha256))
        print(json.dumps({"packet_sha256": result} if args.command == "build" else
                         {"status": "STATIC_VERIFIED", "results": result}, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as error:
        print(f"prearm packet refused: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
