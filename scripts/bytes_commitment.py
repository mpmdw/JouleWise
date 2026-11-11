#!/usr/bin/env python3
"""Offline BYTES commitment preflight, outside the registered estimator.

Only named prediction/provenance files, Git objects/refs, and the canonical
metadata journal are read. No exports, archives, factors or outcomes are read.
Local origin refs are an offline snapshot; pushed_utc is an operator attestation,
not a timestamp authenticated by Git. See docs/design/bytes_commitment.md.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
METADATA = 'docs/bytes/stage1'
JOURNAL = METADATA + '/unblinding.jsonl'
RELEASE = METADATA + '/heldout-release.json'
ESTIMATORS = {'joulewise/bytes_analysis.py': '18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71'}


def _git(repo, *args):
    env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_NO_LAZY_FETCH': '1', 'GIT_TERMINAL_PROMPT': '0', 'GIT_NO_REPLACE_OBJECTS': '1',
           'GIT_OPTIONAL_LOCKS': '0'}
    result = subprocess.run(['git', *args], cwd=repo, env=env, capture_output=True, check=False)
    if result.returncode:
        raise ValueError('BYTES commitment: Git check failed: ' + args[0])
    return result.stdout


def _ancestor(repo, older, newer):
    # rev-list avoids treating a Git execution failure as an ordinary nonancestor.
    return not _git(repo, 'rev-list', '--max-count=1', older, '--not', newer).strip()


def _commit(repo, value):
    if not isinstance(value, str) or not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', value):
        raise ValueError('BYTES commitment requires a full lowercase commit object id')
    resolved = _git(repo, 'rev-parse', '--verify', value + '^{commit}').decode().strip()
    if resolved != value:
        raise ValueError('BYTES commitment object must itself be a commit')
    return resolved


def _blob(repo, commit, path, *, optional=False):
    entry = _git(repo, 'ls-tree', commit, '--', path).decode().strip()
    if not entry and optional:
        return None
    if not entry or entry.split()[0:2] != ['100644', 'blob'] or entry.partition('\t')[2] != path:
        raise ValueError('BYTES commitment missing regular blob: ' + path)
    return _git(repo, 'cat-file', 'blob', entry.split()[2])


def _utc(value):
    if not isinstance(value, str):
        raise ValueError('BYTES commitment requires a UTC timestamp')
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
        raise ValueError('BYTES commitment requires a UTC timestamp')
    return stamp


def _events(raw, path):
    if path.endswith('.jsonl'):
        return [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    record = json.loads(raw)
    if not isinstance(record, dict):
        raise ValueError('BYTES commitment: malformed release record')
    if record.get('stage') == 'fit':
        return []  # Fit-key release is required BEFORE the commitment, not an unblind.
    if record.get('stage') != 'heldout':
        raise ValueError('BYTES commitment: unrecognized release record')
    return [{'event': 'heldout_keys', 'unblinded_utc': record['released_utc']}]


def _check_events(events, committed, pushed, now):
    for event in events:
        if not isinstance(event, dict) or event.get('event') not in ('heldout_rows', 'heldout_keys', 'heldout_analysis'):
            raise ValueError('BYTES commitment: unrecognized unblinding event')
        stamp = _utc(event['unblinded_utc'])
        if not committed < stamp or not pushed < stamp or stamp > now:
            raise ValueError('BYTES commitment/push must predate every unblinding record')


def verify_commitment(commit, predictions=None, *, repo=ROOT, receipt=None, unblinding_records=()):
    repo = Path(repo).resolve()
    commit = _commit(repo, commit)
    head = _git(repo, 'rev-parse', '--verify', 'HEAD^{commit}').decode().strip()
    if not _ancestor(repo, commit, head):
        raise ValueError('BYTES commitment is not an ancestor of the analysis head')
    record = receipt if isinstance(receipt, dict) else json.loads(
        Path(receipt or repo / METADATA / 'push-receipt.json').read_bytes())
    if record['schema'] != 'joulewise.bytes_push_receipt.v1' or record['stage1_commit'] != commit:
        raise ValueError('BYTES commitment push receipt does not name this commit')
    origin_ref = record['origin_ref']
    refs = _git(repo, 'for-each-ref', '--format=%(refname)', '--contains=' + commit,
                'refs/remotes/origin/').decode().splitlines()
    if origin_ref not in refs or origin_ref == 'refs/remotes/origin/HEAD':
        raise ValueError('BYTES commitment is not reachable from the recorded origin ref')
    origin_tip = _commit(repo, record['origin_tip'])
    current_tip = _git(repo, 'rev-parse', '--verify', origin_ref + '^{commit}').decode().strip()
    if not _ancestor(repo, commit, origin_tip) or not _ancestor(repo, origin_tip, current_tip):
        raise ValueError('BYTES commitment origin receipt is not on the current origin lineage')
    committed = datetime.fromisoformat(_git(repo, 'show', '-s', '--format=%cI', commit).decode().strip()).astimezone(timezone.utc)
    pushed, now = _utc(record['pushed_utc']), datetime.now(timezone.utc)
    if not committed <= pushed <= now:
        raise ValueError('BYTES commitment push time precedes commit or is in the future')
    path = record['predictions_path']
    if not isinstance(path, str) or str(PurePosixPath(path)) != path or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts:
        raise ValueError('BYTES commitment requires a repository-relative predictions path')
    if PurePosixPath(path).name != 'predictions.json':
        raise ValueError('BYTES commitment requires predictions.json')
    raw = _blob(repo, commit, path)
    digest = hashlib.sha256(raw).hexdigest()
    side = str(PurePosixPath(path).with_suffix('.sha256'))
    if _blob(repo, commit, side).decode().strip() != digest:
        raise ValueError('BYTES commitment predictions.sha256 does not match committed predictions')
    local = Path(predictions) if predictions is not None else repo / path
    if local.read_bytes() != raw or local.with_suffix('.sha256').read_text().strip() != digest:
        raise ValueError('BYTES commitment predictions differ from the committed blob/digest')
    frozen = json.loads(raw)
    for estimator, expected in ESTIMATORS.items():
        if hashlib.sha256(_blob(repo, commit, estimator)).hexdigest() != expected:
            raise ValueError('BYTES commitment estimator differs from its registered digest')
    if frozen['bytes_analysis_sha256'] != ESTIMATORS['joulewise/bytes_analysis.py']:
        raise ValueError('BYTES commitment predictions name an unregistered estimator')
    # Require an explicitly initialized journal. Missing evidence is not an empty history.
    journal = repo / JOURNAL
    _check_events(_events(journal.read_bytes(), JOURNAL), committed, pushed, now)
    files = [repo / RELEASE, *map(Path, unblinding_records)]
    for file in files:
        if file.is_file():
            _check_events(_events(file.read_bytes(), str(file)), committed, pushed, now)
    # Read EVERY retained revision at these two metadata paths, including deleted
    # records and side branches. No history of exports/outcomes is inspected.
    history = _git(repo, 'rev-list', '--all', '--full-history', '--', JOURNAL, RELEASE).decode().splitlines()
    revisions = 0
    for revision in history:
        for name in (JOURNAL, RELEASE):
            payload = _blob(repo, revision, name, optional=True)
            if payload is None:
                continue
            events = _events(payload, name)
            if events and (revision == commit or not _ancestor(repo, commit, revision)):
                raise ValueError('BYTES commitment must precede the Git unblinding-record history')
            _check_events(events, committed, pushed, now)
            revisions += 1
    return {'stage1_commit': commit, 'analysis_head': head, 'predictions_sha256': digest,
            'estimator_sha256': dict(ESTIMATORS), 'origin_ref': origin_ref, 'origin_tip_at_push': origin_tip,
            'origin_tip_checked': current_tip, 'pushed_utc': record['pushed_utc'],
            'push_time_authority': 'operator attestation; origin refs are an offline snapshot',
            'unblinding_journal': JOURNAL, 'historical_metadata_revisions_checked': revisions,
            'checked_utc': now.isoformat()}


def add_arguments(parser):
    parser.add_argument('--commitment-repo', type=Path, help='analysis Git checkout (default: script checkout)')
    parser.add_argument('--stage1-receipt', type=Path, help='push receipt (default: docs/bytes/stage1/push-receipt.json)')


def admit(args, event, *, repo=ROOT, unblinding_records=()):
    """Validate and durably record the attempt BEFORE any held-out read or key copy."""
    import fcntl
    repo = args.commitment_repo or repo
    result = verify_commitment(args.stage1_commit, getattr(args, 'predictions', None), repo=repo,
                               receipt=args.stage1_receipt, unblinding_records=unblinding_records)
    journal = Path(repo) / JOURNAL
    with journal.open('r+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        now = datetime.now(timezone.utc)
        prior = stream.read()
        _check_events(_events(prior.encode(), JOURNAL),
                      datetime.fromisoformat(_git(repo, 'show', '-s', '--format=%cI', result['stage1_commit']).decode().strip()).astimezone(timezone.utc),
                      _utc(result['pushed_utc']), now)
        stream.seek(0, os.SEEK_END)
        if prior and not prior.endswith('\n'):
            stream.write('\n')
        stream.write(json.dumps({'event': event, 'unblinded_utc': now.isoformat(),
                                 'stage1_commit': result['stage1_commit']}, sort_keys=True) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'record-push', 'admit'))
    parser.add_argument('--stage1-commit', required=True)
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--pushed-utc', help='operator-recorded UTC push time; required by record-push')
    parser.add_argument('--origin-ref', default='refs/remotes/origin/records/2026-11-bytes-stage1')
    parser.add_argument('--predictions-path', default=METADATA + '/predictions.json')
    parser.add_argument('--event', choices=('heldout_rows', 'heldout_keys', 'heldout_analysis'))
    parser.add_argument('--unblinding-record', action='append', default=[], type=Path)
    add_arguments(parser)
    args = parser.parse_args(argv)
    repo = args.commitment_repo or ROOT
    receipt = args.stage1_receipt or repo / METADATA / 'push-receipt.json'
    try:
        if args.command == 'record-push':
            record = {'schema': 'joulewise.bytes_push_receipt.v1', 'stage1_commit': args.stage1_commit,
                      'pushed_utc': args.pushed_utc, 'origin_ref': args.origin_ref,
                      'origin_tip': _git(repo, 'rev-parse', '--verify', args.origin_ref + '^{commit}').decode().strip(),
                      'predictions_path': args.predictions_path}
            result = verify_commitment(args.stage1_commit, args.predictions, repo=repo, receipt=record)
            with Path(receipt).open('x') as stream:
                stream.write(json.dumps(record, sort_keys=True, indent=2) + '\n')
        elif args.command == 'admit':
            if args.event is None:
                raise ValueError('BYTES commitment admission requires an event')
            result = admit(args, args.event, repo=repo, unblinding_records=args.unblinding_record)
        else:
            result = verify_commitment(args.stage1_commit, args.predictions, repo=repo, receipt=receipt,
                                       unblinding_records=args.unblinding_record)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('BYTES commitment refused: ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
