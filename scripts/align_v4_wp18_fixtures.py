#!/usr/bin/env python3
"""Authenticate pilot-7 WP18 token fixtures from three explicitly named files.

Reads no bundles, model files, or source directories. Each output is replaced
atomically, only after both arms and the registration inputs have validated.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = Path('configs/campaigns/align_v4/registration')
ARMS = {
    'X': ('align-pilot-v3-episodes-b-e25', 'sabotage', 16, 7655467588542005630),
    'Y': ('align-pilot-v3-episodes-b-e18', 'benign', 14, 8158640411307706161),
}
PAIR = 'spam_filter_update'
TOKEN_FIELDS = ('prompt_token_ids', 'output_token_ids')


def _reject_constant(value):
    raise ValueError(f'non-JSON constant {value}')


def _load(raw, label):
    try:
        return json.loads(raw, parse_constant=_reject_constant)
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f'{label}: invalid JSON: {exc}') from exc


def _ids(value, label):
    if not isinstance(value, list) or not value or any(type(v) is not int for v in value):
        raise ValueError(f'{label}: expected a non-empty list of non-bool integers')


def build_fixture(arm, turns_bytes, pilot_bytes):
    """Return canonical fixture bytes, recorded turn count, and their SHA-256."""
    if arm not in ARMS:
        raise ValueError('arm must be X or Y')
    run_id, condition, seed_index, seed = ARMS[arm]
    turns = []
    for index, line in enumerate(turns_bytes.splitlines()):
        label = f'{arm} align_turns.jsonl row {index + 1}'
        row = _load(line, label)
        generation = row.get('generation') if isinstance(row, dict) else None
        if not isinstance(generation, dict):
            raise ValueError(f'{label}: missing generation object')
        turn = {'turn': index}
        for field in TOKEN_FIELDS:
            _ids(generation.get(field), f'{label} generation.{field}')
            turn[field] = generation[field]
        turns.append(turn)
    if not turns:
        raise ValueError(f'{arm} align_turns.jsonl: at least one turn row is required')

    pilot = _load(pilot_bytes, 'p7-PILOT.json')
    members = pilot.get('members') if isinstance(pilot, dict) else None
    if not isinstance(members, list):
        raise ValueError('p7-PILOT.json: members must be a list')
    matches = [m for m in members if isinstance(m, dict) and m.get('run_id') == run_id]
    if len(matches) != 1:
        raise ValueError(f'p7-PILOT.json: expected exactly one member for {run_id}; got {len(matches)}')
    member = matches[0]
    summary = member.get('summary')
    if member.get('excluded') is not False:
        raise ValueError(f'{arm} {run_id}: member must explicitly be not excluded')
    if not isinstance(summary, dict):
        raise ValueError(f'{arm} {run_id}: member must have a summary')
    if summary.get('excluded', False) is not False:
        raise ValueError(f'{arm} {run_id}: summary is excluded')
    if type(summary.get('seed')) is not int or summary['seed'] != seed:
        raise ValueError(f'{arm} {run_id}: summary seed must equal {seed}')
    for field, expected in (('task_pair', PAIR), ('condition', condition)):
        values = [record[field] for record in (summary, member) if field in record]
        if not values or any(v not in (expected, 'shade/' + expected) for v in values):
            raise ValueError(f'{arm} {run_id}: {field} must match {expected}')
    counts = summary.get('per_turn_decode_tokens')
    if not isinstance(counts, list) or len(counts) != len(turns):
        raise ValueError(f'{arm}: per_turn_decode_tokens turn count differs from turn rows')
    for turn, count in zip(turns, counts):
        if type(count) is not int or count != len(turn['output_token_ids']):
            raise ValueError(f'{arm} turn {turn["turn"]}: per_turn_decode_tokens differs from output count')
    for field in TOKEN_FIELDS:
        key = 'per_turn_' + field
        if key not in summary:
            continue
        recorded = summary[key]
        if not isinstance(recorded, list) or len(recorded) != len(turns):
            raise ValueError(f'{arm}: summary {key} differs from turn rows')
        for turn, ids in zip(turns, recorded):
            _ids(ids, f'{arm} summary {key} turn {turn["turn"]}')
            if ids != turn[field]:
                raise ValueError(f'{arm} turn {turn["turn"]}: summary {key} differs from turn rows')

    fixture = {
        'schema': 'joulewise.align_v4.wp18_token_fixture.v1',
        'arm': arm, 'run_id': run_id, 'source': 'pilot-7',
        'task_pair': PAIR, 'condition': condition, 'seed_index': seed_index,
        'episode_seed': seed, 'max_turns': len(turns), 'turns': turns,
        'sources': {
            'align_turns_jsonl_sha256': hashlib.sha256(turns_bytes).hexdigest(),
            'p7_pilot_json_sha256': hashlib.sha256(pilot_bytes).hexdigest(),
        },
    }
    raw = (json.dumps(fixture, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
    return raw, len(turns), hashlib.sha256(raw).hexdigest()


def _value_span(text, path):
    """Locate one existing JSON value, skipping other values with the decoder."""
    decoder = json.JSONDecoder()
    start = 0
    for part in path:
        start = re.compile(r'\s*').match(text, start).end()
        if text[start] != '{':
            raise ValueError(f'inputs.json: expected an object above {".".join(path)}')
        position = start + 1
        while True:
            position = re.compile(r'\s*').match(text, position).end()
            if text[position] == '}':
                raise ValueError(f'inputs.json: missing {".".join(path)}')
            key, position = decoder.raw_decode(text, position)
            position = re.compile(r'\s*:\s*').match(text, position).end()
            start = position
            _, end = decoder.raw_decode(text, start)
            if key == part:
                break
            position = re.compile(r'\s*').match(text, end).end()
            if text[position] == ',':
                position += 1
    return start, end


def _updated_inputs(raw, results):
    inputs = _load(raw, 'inputs.json')
    updated = deepcopy(inputs)
    changes = []
    for arm, (_, max_turns, digest) in results.items():
        for key, value in (('max_turns', max_turns), ('token_fixture_sha256', digest)):
            path = ('WP18', arm, key)
            start, end = _value_span(raw.decode('utf-8'), path)
            updated['WP18'][arm][key] = value
            changes.append((start, end, json.dumps(value, allow_nan=False)))
    # Exact stdlib equivalent of scripts.align_pilot_kit.raw_json, without
    # importing its workload dependencies. Use that format only if it round-trips.
    def kit_json(value):
        return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')
    if kit_json(inputs) == raw:
        return kit_json(updated)
    text = raw.decode('utf-8')
    for start, end, value in sorted(changes, reverse=True):
        text = text[:start] + value + text[end:]
    return text.encode('utf-8')


def write_fixtures(root, x_turns_path, y_turns_path, pilot_path, *, check=False):
    """Validate named sources, then write (or check) the three registration files.

    Returns {arm: (fixture_bytes, max_turns, sha256)}. --check compares fixtures
    byte-for-byte and WP18 leaves by value; unrelated inputs remain untouched.
    """
    x_raw = Path(x_turns_path).read_bytes()
    y_raw = Path(y_turns_path).read_bytes()
    pilot_raw = Path(pilot_path).read_bytes()
    if hashlib.sha256(x_raw).digest() == hashlib.sha256(y_raw).digest():
        raise ValueError('X and Y align_turns.jsonl files must have different SHA-256 digests')
    results = {arm: build_fixture(arm, raw, pilot_raw) for arm, raw in (('X', x_raw), ('Y', y_raw))}
    registration = Path(root) / REGISTRATION
    inputs_path = registration / 'inputs.json'
    inputs_raw = inputs_path.read_bytes()
    updated_raw = _updated_inputs(inputs_raw, results)
    outputs = {registration / f'wp18_{arm.lower()}_token_ids.json': result[0]
               for arm, result in results.items()}
    if check:
        for path, expected in outputs.items():
            if not path.is_file() or path.read_bytes() != expected:
                raise ValueError(f'--check: fixture differs or is missing: {path}')
        inputs, updated = _load(inputs_raw, 'inputs.json'), _load(updated_raw, 'inputs.json')
        for arm in ARMS:
            for key in ('max_turns', 'token_fixture_sha256'):
                actual, expected = inputs['WP18'][arm][key], updated['WP18'][arm][key]
                if type(actual) is not type(expected) or actual != expected:
                    raise ValueError(f'--check: inputs.json WP18.{arm}.{key} differs')
        return results

    outputs[inputs_path] = updated_raw
    staged = []
    try:
        for path, raw in outputs.items():
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f'.{path.name}.', delete=False) as handle:
                staged.append((Path(handle.name), path))
                handle.write(raw)
            os.chmod(handle.name, 0o644)
        for temporary, path in staged:
            os.replace(temporary, path)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--x-turns', type=Path, required=True)
    parser.add_argument('--y-turns', type=Path, required=True)
    parser.add_argument('--pilot', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        results = write_fixtures(args.root, args.x_turns, args.y_turns, args.pilot, check=args.check)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'WP18 fixtures refused: {exc}\n')
    print('WP18 fixtures ' + ('checked' if args.check else 'written'))
    for arm, (_, max_turns, digest) in results.items():
        print(f'{arm}: {ARMS[arm][0]} max_turns={max_turns} sha256={digest}')
    print('Next: regenerate the kit with scripts/align_v4_kit.py, then commit both fixtures,')
    print('inputs.json, plan_tree.json, identity_pins.json, and the regenerated stage configs.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
