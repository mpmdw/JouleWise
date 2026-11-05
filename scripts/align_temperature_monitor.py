#!/usr/bin/env python3
"""Run the opt-in ALIGN temperature extension around the pinned hazard monitor."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple.temperature_monitor import run_forever


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    args = parser.parse_args(argv)
    return run_forever(args.config, argv=sys.argv)


if __name__ == '__main__':
    raise SystemExit(main())
