"""Retain v4 transcripts under the energy outcomes' withheld-custody convention.

Only existence, hashes and structural flags leave ``withheld/``. No monitor,
transcript rendering, scoring or release operation lives here. The v5 lead
owns release after registration; filesystem modes are not a same-user sandbox.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from joulewise.desk_compress import read_bytes

SCHEMA = 'joulewise.align.v4_transcript_custody.v1'
RECEIPT = Path('collection/align-transcripts.json')
WITHHELD = Path('withheld/align-transcripts')
LOGS = ('align_transcript.jsonl', 'align_turns.jsonl')


def _json(value):
    return (json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':')) + '\n').encode()


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _seal(path, raw):
    """Publish complete, fsynced, owner-only bytes once; verify exact replays."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink() or path.is_symlink():
        raise ValueError('transcript custody must not be a symlink')
    descriptor, name = tempfile.mkstemp(prefix='.transcript-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(name, path)
        except FileExistsError:
            if path.read_bytes() != raw:
                raise ValueError('transcript custody differs from its first seal')
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(name)


def _structural_flags(logs):
    """Validate coverage only. Never interpret reasoning, actions or outcomes."""
    flags = []
    if LOGS[0] not in logs:
        flags.append('transcript.missing')
    if LOGS[1] not in logs:
        flags.append('transcript.turns_missing')
    try:
        messages = [json.loads(line) for line in logs.get(LOGS[0], b'').splitlines() if line.strip()]
        turns = [json.loads(line) for line in logs.get(LOGS[1], b'').splitlines() if line.strip()]
        if LOGS[0] in logs and (not messages or any(
                not isinstance(m, dict) or not isinstance(m.get('content'), str) for m in messages)):
            raise ValueError('malformed history')
        if any(not isinstance(t, dict) for t in turns):
            raise ValueError('malformed turns')
        if any(not isinstance(t.get('raw_text'), str) for t in turns):
            flags.append('transcript.raw_completion_missing')
        if len(turns) != sum(m.get('role') == 'assistant' for m in messages):
            flags.append('transcript.turn_count_mismatch')
        if any(any(str(f).startswith(('endpoint_error:', 'episode.deadman:'))
                   for f in t.get('flags', ())) for t in turns):
            flags.append('transcript.generation_incomplete')
    except (ValueError, UnicodeError, TypeError, AttributeError):
        flags.append('transcript.malformed')
    return flags


def seal_window(custody_root, runs_root, members, *, window_id):
    """Copy both existing logs losslessly for *all planned* members, even Xs.

    The per-member transcript is a canonical JSON envelope of base64-encoded
    original files, preserving even malformed UTF-8/JSON bytes. Its SHA-256
    binds the full history and the raw completions, with source hashes too.
    A missing transcript remains a flag, never a new v4 eligibility rule.
    No timestamps or scores enter the receipt, so retries verify first bytes.
    """
    custody, runs = Path(custody_root), Path(runs_root)
    ids = [m['run_id'] for m in members]
    if any(
            not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name)
            for name in ids) or len(ids) != len(set(ids)):
        raise ValueError('invalid or duplicate transcript member id')
    rows = []
    for name in ids:
        logs, flags = {}, []
        for filename in LOGS:
            try:
                logs[filename] = read_bytes(runs / name / 'outputs' / filename)
            except FileNotFoundError:
                pass
            except OSError:
                flags.append('transcript.unreadable')
        flags.extend(_structural_flags(logs))
        relative, digest = None, None
        if logs:
            relative = (WITHHELD / (name + '.json')).as_posix()
            payload = _json({'schema': SCHEMA, 'run_id': name,
                             'files': {key: base64.b64encode(raw).decode('ascii') for key, raw in logs.items()}})
            _seal(custody / relative, payload)
            digest = _digest(payload)
        rows.append({'run_id': name, 'exists': LOGS[0] in logs,
                     'complete': not flags, 'path': relative, 'sha256': digest,
                     'source_sha256': {key: _digest(raw) for key, raw in logs.items()},
                     'flags': sorted(set(flags))})
    record = {'schema': SCHEMA, 'window_id': window_id, 'status': 'sealed_unscored',
              'release_after': 'v5_registration', 'members': rows}
    _seal(custody / RECEIPT, _json(record))
    return record


def seal_v4_window(plan):
    """The W1/D night-driver seam; other packs never open a transcript path."""
    pack = plan.hazard_window['pack']
    if not (pack['pack_id'] == 'align-v4' or pack['pack_id'].startswith('align-v4-')):
        return None
    members = json.loads((Path(pack['pack_root']) / 'collection_plan.json').read_bytes())['members']
    return seal_window(plan.custody_root, plan.hazard_window['runs_roots']['claim'], members,
                       window_id=plan.plan_id)


def withhold_desk_transcripts(members):
    """Close the desk's transcript/token-ID disclosure paths after its checks.

    The episode bundles and sealed logs retain the original evidence. Numeric
    task scores and every v4 instrument result are unchanged. Thermal token
    identity remains comparable between exported records via SHA-256 of the
    token sequence, without publishing a decodable copy.
    """
    for member in members:
        summary = member.get('summary') or {}
        for key in ('identity_turns', 'per_turn_prompt_token_ids', 'per_turn_output_token_ids'):
            if key in summary:
                summary[key + '_sha256'] = _digest(_json(summary.pop(key)))
        diagnostics = summary.get('task_diagnostics') or {}
        if 'evaluation_outputs' in diagnostics:
            diagnostics['evaluation_outputs_sha256'] = _digest(_json(diagnostics.pop('evaluation_outputs')))
        if member.get('tokens') is not None:
            member['tokens'] = {'sealed_sha256': _digest(_json(member['tokens']))}
