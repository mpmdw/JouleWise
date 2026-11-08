#!/usr/bin/env python3
"""Fresh-seed synthetic validation of discovery-selected R22 margin cases.

Run after simulate_r22_sol1.py and the discovery audit/selection recorded in
r22-fix-selection-sol1.json. No measurement data, model, or runtime imports.
The 1.25 margin is an explicitly post-discovery extension, not an initial-grid
choice. This checks selected stress settings, not every possible mechanism.
"""
import hashlib
import json
from pathlib import Path
import time

import simulate_r22_sol1 as sim


def main():
    dest = Path(__file__).resolve().parent
    selection = json.loads((dest/'r22-fix-selection-sol1.json').read_text())
    sim.MARGINS = tuple(selection['validation_margins'])
    started = time.monotonic()
    rows = []
    for setting in selection['validation_scenarios']:
        _, scores, fixes = sim.simulate(*setting, selection['validation_trials'], sim.BATCH,
                                       seed=selection['validation_seed'])
        for row in fixes:
            if row['margin'] == 0:
                continue
            oracle = next(r for r in scores if r['design'] == 'oracle8'
                          and r['pair'] == 'pair_mean' and r['rule'] == row['rule'])
            delta = row['fpr'][0]-oracle['fpr'][0]
            # Cauchy bound on the SE of two dependent conditional mean risks;
            # conservative pointwise asymptotic 95% CI, without pretending the
            # two own-qualification populations are the paired intersection.
            half = row['fpr'][2]-row['fpr'][0] + oracle['fpr'][2]-oracle['fpr'][0]
            rows.append(dict(**row, oracle_fpr=oracle['fpr'],
                             delta_population=[delta, delta-half, delta+half]))
        print('validated', *setting, flush=True)
    result = dict(seed=selection['validation_seed'], trials_per_setting=selection['validation_trials'],
        settings=selection['validation_scenarios'], margins=list(sim.MARGINS), rows=rows,
        elapsed_seconds=time.monotonic()-started,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        simulator_sha256=hashlib.sha256((dest/'simulate_r22_sol1.py').read_bytes()).hexdigest(),
        selection_sha256=hashlib.sha256((dest/'r22-fix-selection-sol1.json').read_bytes()).hexdigest(),
        ci='Pointwise 95% MC; whole study is the unit; population-difference CI uses conservative Cauchy SE bound',
        scope='Fresh-seed validation of selected discovery stress cases only; 1.25 is a post-discovery extension')
    (dest/'r22-validation-sol1.json').write_text(json.dumps(result, indent=2)+'\n')
    print(f'SYNTHETIC VALIDATION seed={result["seed"]} studies/setting={result["trials_per_setting"]} '
          f'settings={len(result["settings"])} elapsed={result["elapsed_seconds"]:.1f}s')
    for row in rows:
        print(row['member_p'], row['trend'], row['margin'], row['rule'],
              'FPR', sim.fmt(row['fpr']), 'population-delta', sim.fmt(row['delta_population']),
              'paired-delta', sim.fmt(row['delta_oracle']))


if __name__ == '__main__':
    main()
