#!/usr/bin/env python3
"""CLI for the synthetic operand ladder. See --help; native runs are QUIET-MAC."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.interp_energy.rail_data_dependence import main


if __name__ == "__main__":
    raise SystemExit(main())
