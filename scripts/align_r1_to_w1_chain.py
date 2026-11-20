#!/usr/bin/env python3
"""Run (or print) the R1 -> W1 chain after R1 closes: docs/align/R1-TO-W1-CHAIN.md as a script.

Steps, in order (the doc's command block is tested against ``render``):

  1 export           per-turn counts from the gated D runs' bundles
  2 backfill-x-g     X-G evidence into the R1 record (R10-4)
  3 backfill-counts  per-turn counts into the gated rows (R11/R16)
  4 install-slots    copy the completed record to registration/r1_slots.json
  5 derive-contrast  print the contrast cap/fit for inputs.json (``--write-contrast`` merges it)
  6 decide           the budget procedure (RL-148 section 2; prints the step, drafts nothing)
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
        ('decide', f'{budget} decide'),
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

    def add_missing_contrast(raw, printed):
        def unique_members(pairs):
            members = {}
            for key, value in pairs:
                if key in members:
                    raise ValueError(f'duplicate JSON key {key!r}')
                members[key] = value
            return members

        # Compare number tokens without rounding or conflating them with strings or bools.
        decoder = json.JSONDecoder(parse_int=tuple, parse_float=tuple, object_pairs_hook=unique_members)

        def skip_space(source, pos):
            while source[pos] in ' \t\r\n':
                pos += 1
            return pos

        def member_spans(source, opening):
            # The entire document has already been parsed. Skip nested values with the decoder.
            spans = {}
            pos = skip_space(source, opening + 1)
            while source[pos] != '}':
                key, end = decoder.raw_decode(source, pos)
                start = skip_space(source, skip_space(source, end) + 1)
                _, end = decoder.raw_decode(source, start)
                spans[key] = start, end
                pos = skip_space(source, end)
                if source[pos] == ',':
                    pos = skip_space(source, pos + 1)
            return spans

        encoding = json.detect_encoding(raw)
        # Select a BOM-free codec and keep any original BOM in the byte prefix.
        if encoding == 'utf-8-sig':
            encoding = 'utf-8'
        elif encoding in ('utf-16', 'utf-32'):
            encoding += '-le' if raw.startswith(b'\xff\xfe') else '-be'
        text = raw.decode(encoding, 'surrogatepass')
        body_start = int(text.startswith('\ufeff'))
        data = decoder.decode(text[body_start:])
        r1 = data.get('R1') if isinstance(data, dict) else None
        policy = r1.get('thermal_policy') if isinstance(r1, dict) else None
        if not isinstance(policy, dict):
            raise ValueError('R1.thermal_policy must be an object')

        derived = decoder.decode(printed)
        for field, value in derived.items():
            if field in policy and policy[field] != value:
                raise ValueError(f'R1.thermal_policy.{field} differs from derivation')
        missing = derived.keys() - policy.keys()
        if not missing:
            return raw

        r1_start, _ = member_spans(text, skip_space(text, body_start))['R1']
        policy_start, _ = member_spans(text, r1_start)['thermal_policy']
        fields = member_spans(printed, skip_space(printed, 0))
        pos = policy_start + 1
        spacing = text[pos:skip_space(text, pos)]
        inserted = []
        for field, (start, end) in fields.items():
            if field in missing:
                value_text = printed[start:end]
                inserted.append(f'{spacing}{json.dumps(field)}: {value_text}')
        addition = ','.join(inserted) + (',' if policy else '')
        offset = len(text[:pos].encode(encoding, 'surrogatepass'))
        return raw[:offset] + addition.encode(encoding, 'surrogatepass') + raw[offset:]

    args.work.mkdir(parents=True, exist_ok=False)
    for step, command in commands:
        print(f'== {step}', flush=True)
        result = runner(shlex.split(command), cwd=root, capture_output=step == 'derive-contrast', text=True)
        code = getattr(result, 'returncode', 0)
        if step == 'derive-contrast' and code == 0 and getattr(result, 'stdout', None):
            print(result.stdout)
            if args.write_contrast:
                inputs = Path(root) / REGISTRATION / 'inputs.json'
                raw = inputs.read_bytes()
                try:
                    updated = add_missing_contrast(raw, result.stdout)
                except ValueError as exc:
                    print(f'step derive-contrast refused: {exc}', file=sys.stderr)
                    return 1
                if updated != raw:
                    inputs.write_bytes(updated)
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
