#!/usr/bin/env python3
"""Export the R1 gated D runs' per-turn decode counts for ``backfill-turn-counts`` (R11/R16).

The R1 lane driver records only each gated run's total ``decode_tokens`` and
``admitted_turns``. This reads, per gated D run, exactly one turn-record file of
the run's bundle, ``<RUN>/<run name>/<result.bundle>/outputs/align_turns.jsonl``
(or its ``.zst`` sibling; when the result has no ``bundle`` key, the one such file
found under ``<RUN>/<run name>/``, refusing zero or several; ``source.found_by`` is
``result_key`` or ``discovered``), and from each row only: ``turn``, ``flags`` (the
``turn_token_budget_reached`` marker), and ``generation.output_token_ids`` (its
LENGTH) and ``generation.finish_reason``. No energy, power, thermal, residual or
score file is opened, and no token content is kept.

  turn_decode_counts[i] = len(generation.output_token_ids)
  turn_completed[i]     = finish_reason is a non-empty string that is not a
                          token-budget cut (length/max_tokens/max_new_tokens) and the
                          turn carries no ``turn_token_budget_reached:`` flag

The totals must agree with the driver's own record (decode_tokens, admitted_turns)
or the export refuses. The output maps each gated run to its counts plus a
``source`` block with the sha256 of every input file; ``backfill-turn-counts``
records the sha256 of this whole file.

  python3 scripts/align_r1_turn_counts_export.py --run-dir RUN --out export.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GATED_D_RUN_NAMES = ('D_spam_benign_s1_gated_held_a', 'D_spam_benign_s1_gated_held_b',
                     'D_bank_benign_s1_gated_held')
CUT_REASONS = ('length', 'max_tokens', 'max_new_tokens')
TURNS_FILE = 'outputs/align_turns.jsonl'


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _safe_relative(value, what):
    path = Path(value) if isinstance(value, str) else None
    if path is None or path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError(f'{what} must be a relative path inside the run directory')
    return path


def _stored(path):
    """(stored bytes, logical bytes): the plain file, else its .zst sibling."""
    path = Path(path)
    if path.is_file():
        raw = path.read_bytes()
        return raw, raw
    if Path(str(path) + '.zst').is_file():
        from joulewise.desk_compress import read_bytes
        return Path(str(path) + '.zst').read_bytes(), read_bytes(path)
    raise FileNotFoundError(f'{path} (or .zst) not found')


def discover_turns_file(phase_dir):
    """The one ``outputs/align_turns.jsonl`` (or ``.zst``) under ``phase_dir``.

    Used only when the result carries no ``bundle`` key. Symlinks are not followed.
    Zero or several distinct logical matches refuse.
    """
    found = set()
    for root, dirs, files in os.walk(phase_dir, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(root) / d).is_symlink()]
        if Path(root).name != 'outputs':
            continue
        for name in files:
            if name in ('align_turns.jsonl', 'align_turns.jsonl.zst') and not (Path(root) / name).is_symlink():
                found.add(Path(root) / 'align_turns.jsonl')    # .jsonl and .zst are one logical file
    if len(found) != 1:
        raise ValueError(f'{phase_dir}: expected exactly one {TURNS_FILE} under the run directory, found {len(found)}')
    return found.pop()


def turn_counts(rows):
    """Counts and completion flags from align_turns rows (see module docstring)."""
    counts, completed = [], []
    for index, row in enumerate(rows):
        generation = row.get('generation') if isinstance(row, dict) else None
        tokens = generation.get('output_token_ids') if isinstance(generation, dict) else None
        if row.get('turn') != index or not isinstance(tokens, list):
            raise ValueError(f'turn record {index} is out of order or has no output_token_ids list')
        reason = generation.get('finish_reason')
        flags = row.get('flags') if isinstance(row.get('flags'), list) else []
        counts.append(len(tokens))
        completed.append(isinstance(reason, str) and bool(reason) and reason not in CUT_REASONS
                         and not any(str(f).startswith('turn_token_budget_reached') for f in flags))
    return counts, completed


def export(run_dir):
    run_dir = Path(run_dir)
    result_raw = (run_dir / 'r1_result.json').read_bytes()
    phases = json.loads(result_raw).get('phases')
    if not isinstance(phases, list):
        raise ValueError('r1_result.json has no phases list')
    out = {}
    for name in GATED_D_RUN_NAMES:
        matches = [p for p in phases if isinstance(p, dict) and p.get('name') == name]
        if len(matches) != 1 or not isinstance(matches[0].get('result'), dict):
            raise ValueError(f'r1_result.json must hold exactly one {name} phase with a result')
        result = matches[0]['result']
        phase_dir = run_dir / _safe_relative(name, 'run name')
        if 'bundle' in result and result['bundle'] is not None:
            found_by = 'result_key'
            turns_path = phase_dir / _safe_relative(result['bundle'], f'{name} bundle') / TURNS_FILE
        else:
            # The lane's r1_result.json may not carry the bundle path: discover it.
            found_by = 'discovered'
            turns_path = discover_turns_file(phase_dir)
        stored, logical = _stored(turns_path)
        rows = [json.loads(line) for line in logical.splitlines() if line.strip()]
        counts, completed = turn_counts(rows)
        if len(counts) != result.get('admitted_turns') or sum(counts) != result.get('decode_tokens'):
            raise ValueError(f'{name}: bundle turn records ({len(counts)} turns, {sum(counts)} tokens) disagree with '
                             f'the driver record ({result.get("admitted_turns")} turns, {result.get("decode_tokens")} tokens)')
        out[name] = {'turn_decode_counts': counts, 'turn_completed': completed,
                     'source': {'r1_result_sha256': _digest(result_raw),
                                'align_turns_path': str(turns_path.relative_to(run_dir)),
                                'found_by': found_by,
                                'align_turns_stored_sha256': _digest(stored),
                                'align_turns_logical_sha256': _digest(logical)}}
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run-dir', type=Path, required=True, help='the R1 output directory holding r1_result.json')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        data = export(args.run_dir)
        with args.out.open('x') as handle:
            handle.write(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'align_r1_turn_counts_export: {exc}', file=sys.stderr)
        return 1
    print(f'wrote {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
