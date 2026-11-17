#!/usr/bin/env python3
"""Campaign leg runtime entrypoint (runner kind ``cadence-legs-v1``; RL-149 section 2.2 type A).

    python -B scripts/cadence_leg_runtime.py --config configs/align/v4/r1_runtime.json \
        --leg-spec SPEC.json --r1-kind cadence-leg --output DIR --soak-reference FILE

Prints one JSON object on stdout and writes DIR/runtime_result.json and the
terminal DIR/runtime_custody.json, exactly as ``scripts/align_r1_runtime.py``
does. The implementation is ``joulewise.align.apple.cadence_leg``. Started only
by ``scripts/cadence_legs_runner.py``.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def main(argv=None):
    from joulewise.align.apple import cadence_leg, cadence_ctl
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        path, _, _ = cadence_leg._split_leg_spec(args)
        spec = cadence_leg.load_leg_spec(path)
    except (SystemExit, OSError, ValueError):
        return cadence_leg.main(args)
    if spec["schema"] == "joulewise.cadence_leg_spec.ctl.v1":
        return cadence_ctl.main(args)
    return cadence_leg.main(args)

if __name__ == "__main__":
    raise SystemExit(main())
