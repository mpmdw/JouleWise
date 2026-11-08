#!/usr/bin/env python3
"""Derive a prospective R03 bar from an explicit, lead-authorized replay export.

Input: {"pairs": [{"session": "p4", "ordinals": [5, 17],
"token_identical": true, "energies_j": [Ea, Eb]}, ...]}. No discovery.
With an explicit ``policy``, produce the frozen predictive/OC draft. Without
policy retain the historical descriptive PENDING export. Never discover or
open pilot/R1/W1 records. Adopt a draft only with a supplied lead signature and
an independent JSON gate naming its derivation digest. See W1-BLOCKERS-sol.md.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple.v4_registration import derive_u3, digest, validate_u3


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sources = p.add_mutually_exclusive_group(required=True)
    sources.add_argument('--input', type=Path)
    sources.add_argument('--adopt-draft', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-key', help='repo-relative export locator; defaults to input relative to repo, else basename')
    p.add_argument('--supporting-source', type=Path, action='append', default=[],
                   help='explicit D transfer justification/report to bind (repeatable)')
    p.add_argument('--lead-signature')
    p.add_argument('--gate', type=Path, help='independent ADMIT JSON under docs/align/v4/')
    args = p.parse_args(argv)
    if args.input:
        if args.lead_signature or args.gate:
            p.error('derive first; adoption requires --adopt-draft')
        raw = args.input.read_bytes()
        data = json.loads(raw)
        key = args.source_key or (str(args.input.resolve().relative_to(ROOT))
                                 if args.input.resolve().is_relative_to(ROOT) else args.input.name)
        bindings = {key: digest(raw)}
        for source in args.supporting_source:
            source_key = str(source.resolve().relative_to(ROOT)) if source.resolve().is_relative_to(ROOT) else source.name
            if source_key in bindings:
                p.error('duplicate source locator')
            bindings[source_key] = digest(source.read_bytes())
        result = derive_u3(data['pairs'], bindings, policy=data.get('policy'))
    else:
        if not args.lead_signature or not args.gate:
            p.error('adoption requires --lead-signature and --gate')
        raw = args.gate.read_bytes()
        gate = json.loads(raw)
        result = json.loads(args.adopt_draft.read_bytes())
        result.update(status='registered', lead_signature=args.lead_signature,
                      independent_gate={**gate, 'path': str(args.gate.resolve().relative_to(ROOT)),
                                        'sha256': digest(raw)})
        validate_u3(result, root=ROOT)
    # An existing bar is immutable; a new prospective derivation needs a new path.
    with args.output.open('x') as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
