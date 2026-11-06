#!/usr/bin/env python3
"""External log volume CLI (DRAFT amendment; default OFF).

  census                       list mounted volumes and their class
  arm-check [--config C]       PASS/REFUSE under the external-volume rule; exit 0 on PASS, 3 on REFUSE
  route --config C --internal-session-root R --session-id S
                               where each window write would go (prints JSON)
  prepare-plan --device diskN [--name JW-EXT]
                               print the volume preparation commands; executes nothing

Without --config the rule is today's: any external volume mounted refuses.
See docs/align/v4/DRAFT-AMENDMENT-external-log-volume.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple import external_volume as ev  # noqa: E402

REFUSE_EXIT = 3


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("census")
    check = sub.add_parser("arm-check")
    check.add_argument("--config", type=Path)
    routing = sub.add_parser("route")
    routing.add_argument("--config", type=Path, required=True)
    routing.add_argument("--internal-session-root", type=Path, required=True)
    routing.add_argument("--session-id", required=True)
    prep = sub.add_parser("prepare-plan")
    prep.add_argument("--device", required=True)
    prep.add_argument("--name", default="JW-EXT")
    args = parser.parse_args(argv)

    if args.command == "prepare-plan":
        try:
            print("\n".join(ev.prepare_plan(args.device, name=args.name)))
        except ev.ConfigError as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 2
        return 0
    if args.command == "census":
        print(json.dumps(ev.census(), indent=2, sort_keys=True, default=str))
        return 0
    try:
        config = ev.load_config(args.config)
    except ev.ConfigError as exc:
        print(json.dumps({"verdict": ev.REFUSE, "reasons": [f"config_invalid:{exc}"]}, sort_keys=True))
        return REFUSE_EXIT
    verdict = ev.arm_check(config, ev.census())
    if args.command == "arm-check":
        print(json.dumps(verdict, indent=2, sort_keys=True, default=str))
        return 0 if verdict["verdict"] == ev.PASS else REFUSE_EXIT
    routed = ev.route(config, verdict, internal_session_root=args.internal_session_root,
                      session_id=args.session_id)
    print(json.dumps({"verdict": verdict["verdict"], "reasons": verdict["reasons"], "route": routed},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
