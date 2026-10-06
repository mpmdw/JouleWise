#!/usr/bin/env python3
"""Continuous in-window hazard monitor (gate-prune plan §2.1).

Started by the driver through ``joulewise.hazards.monitor.Supervisor``, in its
own process group under ``taskpolicy -b``; stopped with SIGTERM after the
chain's process group is proven gone.  Writes one JSON-lines journal per
module under ``<custody>/hazards/monitor/``.

    hazard_monitor.py --config <custody>/hazards/monitor/config.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.hazards import monitor  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args(argv)
    return monitor.run_forever(args.config, argv=sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
