#!/usr/bin/env python3
"""Normalized comparison of two block-5 blind-dry-run custody roots (L9-SPEEDUP-R1 stage 4).

Lead ruling (2026-11-01): a new analysis tag may change code identity. Every
recorded output must be byte-identical to the baseline EXCEPT pure source-identity
hashes and the digests mechanically derived from them. This script proves it:

1. Load every file of each tree: ``dry-run/B5-BLIND-DRY-RUN-RECORD.json`` and every
   file under ``dry-run/restricted/`` except ``logs/`` (restricted logs are not
   recorded outputs; ``--logs`` also compares them after replacing the custody
   root and TMPDIR path, which they quote).
2. Before normalization: list every differing file name, and for JSON files every
   differing field path (the "pre-normalization diff list").
3. Normalize each tree on its own: (a) replace the value of every SOURCE_IDENTITY_KEYS
   field, wherever it occurs in a JSON document, by a placeholder; (b) recompute
   digests bottom-up to a fixpoint: every file's original sha256, wherever it occurs
   (a value, a substring, or a content-addressed file name), is replaced by the sha256
   of that file's normalized bytes, until no digest changes.
4. After normalization the two trees must be identical (names and bytes). Any
   remaining difference, and any pre-normalization field difference whose leaf is not
   a source-identity field or a digest/name that normalization maps to the same value,
   is a failure (exit 1).

Usage: normalized_compare.py BASELINE_RUN CANDIDATE_RUN [--logs --tmp BASELINE_TMPDIR CANDIDATE_TMPDIR]
(each RUN is the directory that contains ``dry-run/``; with --logs, each run's custody root and
TMPDIR, which logs quote, are replaced by placeholders before comparison).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

SOURCE_IDENTITY_KEYS = frozenset({
    'validator_source_sha256',   # paper_custody._validator_source_sha256: whole-module source census
    'binder_source_sha256',      # paper_custody._floor_binder_source_sha256: inspect.getsource digest
})
PLACEHOLDER = '<source-identity>'
HEX64 = re.compile(r'[0-9a-f]{64}')
RECORD = 'B5-BLIND-DRY-RUN-RECORD.json'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(root: Path, logs: bool, tmp: str | None = None) -> dict[str, bytes]:
    run = root / 'dry-run'
    files = {RECORD: (run / RECORD).read_bytes()}
    restricted = run / 'restricted'
    for path in sorted(restricted.rglob('*')):
        if path.is_file():
            name = 'restricted/' + path.relative_to(restricted).as_posix()
            if name.startswith('restricted/logs/') and not logs:
                continue
            files[name] = path.read_bytes()
    if logs:
        for name in [n for n in files if n.startswith('restricted/logs/')]:
            files[name] = files[name].replace(str(root.resolve()).encode(), b'<custody>')
            if tmp:
                files[name] = files[name].replace(tmp.encode(), b'<tmpdir>')
    return files


def parse(data: bytes):
    try:
        return json.loads(data)
    except (ValueError, UnicodeDecodeError):
        return None


def field_diffs(a, b, path='$'):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        out = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f'{path}.{key}')
            else:
                out.extend(field_diffs(a[key], b[key], f'{path}.{key}'))
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [f'{path}[len]']
        out = []
        for index, (x, y) in enumerate(zip(a, b)):
            out.extend(field_diffs(x, y, f'{path}[{index}]'))
        return out
    return [] if a == b else [path]


def strip_identity(value):
    if isinstance(value, dict):
        return {key: PLACEHOLDER if key in SOURCE_IDENTITY_KEYS else strip_identity(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [strip_identity(item) for item in value]
    return value


def identity_normalized_bytes(name: str, data: bytes) -> bytes:
    """Replace source-identity values in place, keeping every other byte."""
    document = parse(data)
    if document is None:
        return data
    text = data.decode('utf-8')
    found = []

    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in SOURCE_IDENTITY_KEYS and isinstance(item, str):
                    found.append(item)
                else:
                    collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)
    collect(document)
    for value in found:
        # Every occurrence is the identity value itself: a 64-hex digest is
        # not also used for anything else in the same document.
        text = text.replace(value, PLACEHOLDER)
    if parse(text.encode()) != strip_identity(document):
        raise SystemExit(f'{name}: source-identity replacement was not exact')
    return text.encode('utf-8')


def normalize(files: dict[str, bytes]) -> dict[str, bytes]:
    base = {name: identity_normalized_bytes(name, data) for name, data in files.items()}
    original = {name: sha(data) for name, data in files.items()}
    mapping = {digest: digest for digest in original.values()}
    for _round in range(64):
        current = {}
        for name, data in base.items():
            text = data.decode('utf-8', errors='surrogateescape')
            text = HEX64.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)
            new_name = HEX64.sub(lambda m: mapping.get(m.group(0), m.group(0)), name)
            current[new_name] = (name, text.encode('utf-8', errors='surrogateescape'))
        updated = {original[name]: sha(data) for _new, (name, data) in current.items()}
        if updated == mapping:
            return {new: data for new, (_name, data) in current.items()}
        mapping = updated
    raise SystemExit('digest normalization did not reach a fixpoint')


def main(argv):
    import argparse
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--logs', action='store_true')
    parser.add_argument('--tmp', nargs=2, default=(None, None))
    args = parser.parse_args(argv)
    roots = [args.baseline, args.candidate]
    left = load(args.baseline, args.logs, args.tmp[0])
    right = load(args.candidate, args.logs, args.tmp[1])
    print('baseline ', roots[0])
    print('candidate', roots[1])
    print('files', len(left), len(right))
    print('record sha256', sha(left[RECORD]), sha(right[RECORD]))

    failures = []
    print('\n== before normalization: differing files and fields')
    only_left = sorted(set(left) - set(right))
    only_right = sorted(set(right) - set(left))
    for name in only_left:
        print('  only in baseline :', name)
    for name in only_right:
        print('  only in candidate:', name)
    for name in sorted(set(left) & set(right)):
        if left[name] == right[name]:
            continue
        a, b = parse(left[name]), parse(right[name])
        if a is None or b is None:
            print('  differs (non-JSON):', name)
            continue
        print('  differs:', name)
        for field in field_diffs(a, b):
            print('     field', field)

    nl, nr = normalize(left), normalize(right)
    print('\n== after normalization')
    if set(nl) != set(nr):
        failures.append('file names differ after normalization')
        for name in sorted(set(nl) ^ set(nr)):
            print('  name only on one side:', name)
    for name in sorted(set(nl) & set(nr)):
        if nl[name] != nr[name]:
            failures.append(f'{name} differs after normalization')
            a, b = parse(nl[name]), parse(nr[name])
            print('  STILL DIFFERS:', name, *(field_diffs(a, b) if a is not None and b is not None else []))
    identical = sum(left[n] == right[n] for n in set(left) & set(right))
    print(f'  {len(nl)} normalized files; {identical} were byte-identical before normalization')
    if failures:
        print('\nVERDICT: FAIL')
        for failure in failures:
            print('  ', failure)
        return 1
    print('\nVERDICT: PASS (identical after normalizing source-identity hashes and their derived digests)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
