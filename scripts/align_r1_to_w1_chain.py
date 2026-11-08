#!/usr/bin/env python3
"""Run (or print) the R1 -> W1 chain after R1 closes: docs/align/R1-TO-W1-CHAIN.md as a script.

Steps, in order (the doc's command block is tested against ``render``):

  1 export           per-turn counts from the gated D runs' bundles
  2 backfill-x-g     X-G evidence into the R1 record (R10-4)
  3 backfill-counts  per-turn counts into the gated rows (R11/R16)
  4 install-slots    copy the completed record to registration/r1_slots.json
  5 derive-contrast  print the contrast cap/fit for inputs.json (``--write-contrast`` merges it)
  6 decide           the R10-2 budget procedure (writes a receipt draft when needed)
  7 regenerate-kit   scripts/align_v4_kit.py (regenerates the committed kit from the new slots)
  8 kit-check        scripts/align_v4_kit.py --check (fails closed while inputs are pending)

Smoke G2: the kit is regenerated between installing the slots and ``--check``. Runs from the
repository root on the laptop; reads copies, launches nothing native.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = 'configs/campaigns/align_v4/registration'
STEPS = ('export', 'backfill-x-g', 'backfill-counts', 'install-slots', 'derive-contrast', 'decide',
         'regenerate-kit', 'kit-check')


def render(run='$RUN', slots='$SLOTS', work='$WORK', python='python3.13 -B'):
    """The ordered (step, command string) list with the given operands."""
    budget = f'{python} scripts/align_w1_budget_procedure.py'
    return [
        ('export', f'{python} scripts/align_r1_turn_counts_export.py --run-dir {run} --out {work}/turn_counts_export.json'),
        ('backfill-x-g', f'{budget} backfill-x-g --r1-slots {slots} --r1-result {run}/r1_result.json '
                         f'--out {work}/r1_slots.xg.json'),
        ('backfill-counts', f'{budget} backfill-turn-counts --r1-slots {work}/r1_slots.xg.json '
                            f'--counts-export {work}/turn_counts_export.json --out {work}/r1_slots.json'),
        ('install-slots', f'cp {work}/r1_slots.json {REGISTRATION}/r1_slots.json'),
        ('derive-contrast', f'{budget} derive-contrast'),
        ('decide', f'{budget} decide --draft-out {work}/ruling_1f_draft.json'),
        ('regenerate-kit', f'{python} scripts/align_v4_kit.py'),
        ('kit-check', f'{python} scripts/align_v4_kit.py --check'),
    ]


def main(argv=None, *, runner=subprocess.run, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run-dir', type=Path, required=True, help='the R1 output directory (r1_result.json and phase directories)')
    parser.add_argument('--slots', type=Path, required=True, help="the driver's registration/r1_slots.json")
    parser.add_argument('--work', type=Path, required=True, help='a new empty directory')
    parser.add_argument('--dry-run', action='store_true', help='print the commands only')
    parser.add_argument('--until', choices=STEPS, help='stop after this step')
    parser.add_argument('--write-contrast', action='store_true',
                        help="merge derive-contrast's output into registration/inputs.json R1.thermal_policy")
    args = parser.parse_args(argv)
    commands = render(shlex.quote(str(args.run_dir)), shlex.quote(str(args.slots)), shlex.quote(str(args.work)))
    if args.dry_run:
        for step, command in commands:
            print(f'# {step}\n{command}')
        return 0
    args.work.mkdir(parents=True, exist_ok=False)
    for step, command in commands:
        print(f'== {step}', flush=True)
        result = runner(shlex.split(command), cwd=root, capture_output=step == 'derive-contrast', text=True)
        code = getattr(result, 'returncode', 0)
        if step == 'derive-contrast' and code == 0 and getattr(result, 'stdout', None):
            print(result.stdout)
            if args.write_contrast:
                inputs = Path(root) / REGISTRATION / 'inputs.json'
                data = json.loads(inputs.read_bytes())
                data['R1']['thermal_policy'].update(json.loads(result.stdout))
                inputs.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
                print(f'wrote contrast fields to {inputs}')
        if code != 0:
            if step == 'kit-check':
                print('kit --check refused (expected until every pending input, signature and gate is supplied)')
            else:
                print(f'step {step} failed with exit {code}', file=sys.stderr)
            return code
        if args.until == step:
            break
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
