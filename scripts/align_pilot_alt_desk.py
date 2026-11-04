#!/usr/bin/env python3
"""Read only PILOT members and print a labelled, non-claim desk alternative."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple.pilot_analysis import alternative_residual_analysis

# Set to the source-freeze commit after implementation verification. This pin
# identifies the implementation, not the later report/metadata-only commit.
FROZEN_COMMIT = 'PENDING_SOURCE_FREEZE'


def load_members(pilots):
    """Pool in argument/member order; prefix IDs without changing trajectory keys.

    A PILOT.json's session directory (above inspection, if present) names it;
    other JSON filenames use their stem. Labels must be unique. Only members are read from JSON payloads.
    Deduplication/eligibility remain the analysis function's responsibility.
    """
    members, labels = [], set()
    for filename in pilots:
        path = Path(filename).absolute()
        session_dir = path.parent.parent if path.parent.name == 'inspection' else path.parent
        label = session_dir.name if path.name == 'PILOT.json' else path.stem
        if label in labels:
            raise ValueError(f'duplicate session label: {label!r}')
        labels.add(label)
        for member in json.loads(path.read_text())['members']:
            members.append({**member, 'run_id': f"{label}/{member['run_id']}"})
    return members


def _number(value):
    return 'NA' if value is None else f'{value:.9g}'


def print_tables(analysis):
    """Plain tables retain score, curve, threshold and support witnesses in stdout."""
    for configuration in analysis:
        print('configuration ' + json.dumps(configuration['configuration'], sort_keys=True))
        for scope, result in configuration['scopes'].items():
            for group in result['groups']:
                pair = group['task_pair'] if group['task_pair'] is not None else 'POOLED_DIAGNOSTIC'
                for design, conventions in group['designs'].items():
                    for convention, values in conventions.items():
                        print(f'\n{scope} | {pair} | {design} | {convention}')
                        print('s_r_J df e_J_per_token e_SE LOO_threshold rank m flags')
                        t = values['loo_threshold']
                        print(' '.join((_number(values['s_r_j']), str(values['s_r_df']),
                            _number(values['e_j_per_decode_token']), _number(values['e_se']),
                            _number(t['value']), str(t['rank']), str(t['n_scores']), ','.join(t['flags']) or '-')))
                        print('training_support ' + json.dumps(values['training_support'], sort_keys=True))
                        print('run method residual_J score out_of_support')
                        for r in values['residuals']:
                            print(f"{r['run_id']} {r['method']} {_number(r['residual_j'])} {_number(r['score'])} {r['support']['out_of_support']}")
                            print('support ' + json.dumps({'run_id': r['run_id'], **r['support']}, sort_keys=True))
                        print('tamper_starting_log counts_logged; run k H residual_J score above_threshold out_of_support')
                        for r in values['tamper_detection_curve']:
                            print(f"{r['run_id']} {r['k']} {r['H']} {_number(r['residual_j'])} {_number(r['score'])} {r['above_threshold']} {r['support']['out_of_support']}")
                            if r['support']['out_of_support']:
                                print('support ' + json.dumps({'run_id': r['run_id'], 'k': r['k'], **r['support']}, sort_keys=True))
                        print('crossing run status k H detection')
                        for r in values['crossings']:
                            print(f"{r['run_id']} {r['status']} {r['k']} {r['H']} {r['detection']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', type=Path, action='append', required=True,
                        help='PILOT.json; list reference session first')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    label = f'LABELLED ALTERNATIVE (frozen {FROZEN_COMMIT}) - not the registered headline'
    print(label)
    analysis = alternative_residual_analysis(load_members(args.pilot))
    args.out.write_text(json.dumps({'label': label, 'frozen_commit': FROZEN_COMMIT,
                                   'analysis': analysis}, indent=2, allow_nan=False) + '\n')
    print_tables(analysis)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
