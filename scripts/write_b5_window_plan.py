#!/usr/bin/env python3
"""Write one block-5 HAZARD_PACK window plan at the desk; never arms or launches.

Usage::

    python scripts/write_b5_window_plan.py --inputs INPUTS.json

INPUTS.json is a reviewed ``joulewise.b5_window_plan_inputs.v2`` object (see
``joulewise/b5/plan.py``). The command creates the custody root, the fresh
claim and bound runs roots, ``window.env``, the chain and its sidecar, the
``night_plan.json`` HAZARD_PACK plan and a plan record, then prints the record.
Exit 0 on success; exit 2 with ``{"status": "REFUSED", ...}`` when the inputs or
the pack cannot produce a plan (nothing is written in that case).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.b5 import plan as b5_plan  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inputs", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        inputs = json.loads(args.inputs.read_text(encoding="utf-8"))
        record = b5_plan.write_window_plan(inputs)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": type(exc).__name__, "detail": str(exc)},
                         sort_keys=True))
        return 2
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
