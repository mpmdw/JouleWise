#!/usr/bin/env python3
"""U3 bar (R03 / RUN_STATE 212 R11-2): frozen derivation, then lead signature.

derive: --input {"pairs": [...], "transfer_pairs": [...]} --parameters {lead-frozen
        series_pair_tests, series_false_fail_budget, min_pairs, oc_seed, oc_reps}.
        Pairs: {"session", "family", "ordinals": [early, late], "token_identical": true,
        "energies_j": [E_early, E_late]}; derivation pairs >= 3 ordinals apart, one family
        (30B pilots 4-10); transfer pairs another family (R1 D_spam a/b). No discovery:
        the lead exports both files; their bytes are digested into the bar.
sign:   attaches the lead signature and the independent gate receipt, and validates.
Procedure and rulings: docs/align/v4/W1-BLOCKERS-opus.md section 1.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple.v4_registration import derive_u3, digest, sign_u3


def _write_new(path, value):
    # An existing bar is immutable; a new prospective derivation needs a new path.
    with Path(path).open('x') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)
    d = sub.add_parser('derive')
    d.add_argument('--input', type=Path, required=True)
    d.add_argument('--parameters', type=Path, required=True)
    d.add_argument('--output', type=Path, required=True)
    d.add_argument('--synthetic', action='store_true', help='label a dry-run bar; registration refuses it')
    s = sub.add_parser('sign')
    s.add_argument('--bar', type=Path, required=True)
    s.add_argument('--signature', required=True, help="'lead: <name> <YYYY-MM-DD>'")
    s.add_argument('--gate-path', required=True, help='docs/align/v4/... independent gate report')
    s.add_argument('--gate-sha256', required=True)
    s.add_argument('--output', type=Path, required=True)
    args = p.parse_args(argv)
    if args.command == 'derive':
        if args.output.exists():
            raise FileExistsError(args.output)
        raw, params = args.input.read_bytes(), args.parameters.read_bytes()
        data = json.loads(raw)
        bar = derive_u3(data['pairs'], {args.input.name: digest(raw), args.parameters.name: digest(params)},
                        parameters=json.loads(params), transfer_pairs=data.get('transfer_pairs', []),
                        synthetic=args.synthetic)
    else:
        bar = sign_u3(json.loads(args.bar.read_bytes()), lead_signature=args.signature,
                      gate={'verdict': 'ADMIT', 'path': args.gate_path, 'sha256': args.gate_sha256})
    _write_new(args.output, bar)
    print(json.dumps({k: bar[k] for k in ('status', 'n', 'rms_relative_scale', 'series_quantile_q',
                                          'relative_bar', 'scope')}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
