#!/usr/bin/env python3
"""Derive the v4 relative U3 bar from an explicit desk export of pilot pairs.

Input: {"pairs": [{"session": "p4", "ordinals": [5, 17],
"token_identical": true, "energies_j": [Ea, Eb]}, ...]}. No discovery.
The lead exports eligible within-session pairs from pilots 4-10; custody of
that export is included in the resulting bar. This does not read R1/W1.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple.v4_registration import derive_u3, digest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(argv)
    raw = args.input.read_bytes()
    result = derive_u3(json.loads(raw)['pairs'], {args.input.name: digest(raw)})
    # An existing bar is immutable; a new prospective derivation needs a new path.
    with args.output.open('x') as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
