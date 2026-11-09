#!/usr/bin/env python3
"""Synthetic R14/R25 N=16 versus N=22 sensitivity; never reads measurements.

Reproduce U3-transfer.md using the unchanged v4_u3 arithmetic and OC procedure.
Only the six reserve roster entries differ between policies. Digest fields are
synthetic stand-ins, never evidence or a candidate signed bar. No input files,
model libraries, bundle readers or hardware interfaces are used.
"""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple import v4_u3
from scripts.align_v4_u3_export import policy_template


def normal_model(q, n, counts, factor, scale, shift):
    """Marginal normal-model power, integrating the same shared RMS as R14."""
    def d_tail(u):
        limit = factor*q*u
        return (math.erfc((limit-shift)/(scale*math.sqrt(2)))
                + math.erfc((limit+shift)/(scale*math.sqrt(2))))/2

    def series_tail(u):
        log_survival = (counts['30B']*math.log1p(-min(v4_u3._tail(q*u), 1-1e-16))
                        + counts['D']*math.log1p(-min(d_tail(u), 1-1e-16)))
        return -math.expm1(log_survival)

    return {'D_true_scale': scale, 'D_shift_pilot_sd': shift,
            'D_pair_failure_probability': v4_u3._chi_expect(n, d_tail),
            'series_failure_probability': v4_u3._chi_expect(n, series_tail)}


def comparison():
    current = deepcopy(policy_template())
    # Importability/shape validation only: these digests bind no real artifact.
    for key in ('d_configuration_sha256', 'r1_configuration_sha256',
                'transfer_justification_sha256'):
        current[key] = '0'*64
    previous = deepcopy(current)
    for i in range(9, 15):
        del previous['checks_by_window'][f'C{i}']
    cases = []
    for policy in (previous, current):
        counts = v4_u3.policy_checks(policy)
        tests = sum(counts.values())
        for n, beta in ((7, .05), (7, .025), (5, .05), (6, .05)):
            q = v4_u3.series_quantile(n, tests, beta)
            cases.append({
                'N': tests, 'n': n, 'series_beta': beta,
                'beta_over_N_reference_only': beta/tests,
                'series_quantile_q': q,
                'bar_30B_in_s0_units': q,
                'bar_D_in_s0_units': policy['d_transfer_factor']*q,
                'pair_false_fail_at_assumed_scale': v4_u3.per_pair_false_fail(q, n),
                'series_false_fail_at_assumed_scale': v4_u3.series_false_fail(q, n, tests),
                'normal_model': [normal_model(q, n, counts, policy['d_transfer_factor'], a, d)
                                 for a, d in ((1., 0.), (1.5, 0.), (2., 0.), (3., 0.),
                                              (1., 2.), (1., 8.))],
                'oc': v4_u3.operating_characteristics(policy, {'n': n, 'series_quantile_q': q}),
            })
    return {'label': 'SYNTHETIC DESIGN ONLY; no measurements, adoption or hardware validation',
            'roster_source': 'origin/align/2026-11-08-v4-r11 @ 33932b391:scripts/align_v4_u3_export.py',
            'policies': {'16': previous, '22': current}, 'cases': cases,
            'limitation': 'Fixed-beta sensitivity; the OC does not reapply the leave-one-out '
                          'trigger in each replicate. Probabilities integrate calibration scale; '
                          'they are not guarantees conditional on a realized scale or trigger.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(args.output)
    result = comparison()
    with args.output.open('x') as out:
        out.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
