"""Offline W1 pre-arm checks. No model, sensor or measurement-data discovery.

Synthetic path probes and candidate evidence are separate rows. A successful
synthetic probe cannot substitute for a missing registration or planned series.
The command runner is injectable; commands are argv lists, never shell text.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration

SERIES_SCHEMA = 'joulewise.align_v4.smoke_series_plan.v1'
ENTRIES = ('joulewise/align/apple/endpoint.py', 'scripts/run_night.py',
           'scripts/align_v4_session.py')


def read_local(root, relative):
    """Only explicit repository-relative, non-symlink inputs; never glob data."""
    return registration._local(root, relative).read_bytes()


def closure(root):
    """Recompute the first-party static import closure, including lazy imports."""
    root = Path(root)
    seen, todo = set(), list(ENTRIES)
    while todo:
        relative = todo.pop()
        if relative in seen:
            continue
        seen.add(relative)
        parts = relative[:-3].split('/')[:-1]
        for node in ast.walk(ast.parse(read_local(root, relative))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = parts[:len(parts) - node.level + 1] if node.level else []
                name = '.'.join(base + ([node.module] if node.module else []))
                names = [name] + [name + '.' + a.name for a in node.names]
            for name in names:
                components = name.split('.')
                if components[0] not in ('joulewise', 'scripts'):
                    continue
                for end in range(1, len(components) + 1):
                    prefix = '/'.join(components[:end])
                    for candidate in (prefix + '.py', prefix + '/__init__.py'):
                        path = registration._local(root, candidate)
                        if path.is_file() and candidate not in seen:
                            todo.append(candidate)
    return seen


def receipt_check(ctx):
    missing = sorted(p for p in closure(ctx.repo) if p.startswith('joulewise/')
                     and p not in registration.ARTIFACTS)
    if missing:
        raise ValueError('executed modules absent from registration: ' + ', '.join(missing))
    receipt = json.loads(read_local(ctx.repo, registration.REGISTRATION + 'registration_receipt.json'))
    registration.validate_receipt(receipt, ctx.repo)
    candidate = ctx.w1_candidate or command(ctx, ['git', 'rev-parse', 'HEAD']).stdout.strip()
    candidate = command(ctx, ['git', 'rev-parse', '--verify', candidate + '^{commit}']).stdout.strip()
    if receipt['commit'] != candidate:
        raise ValueError('registration receipt does not bind the requested candidate commit')
    if command(ctx, ['git', 'status', '--porcelain']).stdout.strip():
        raise ValueError('candidate checkout is dirty')
    return {'status': 'pass', 'candidate': candidate, 'executed_modules': len(closure(ctx.repo)),
            'receipt_sha256': hashlib.sha256(read_local(
                ctx.repo, registration.REGISTRATION + 'registration_receipt.json')).hexdigest()}


def command(ctx, argv, *, timeout=120):
    result = ctx.w1_run(argv, cwd=ctx.repo, capture_output=True, text=True,
                        timeout=timeout, check=False)
    if result.returncode:
        raise ValueError(f'command failed ({result.returncode}): {argv!r}\n{result.stderr[-4000:]}')
    return result


def probe(ctx, targets):
    """Run bounded synthetic unittest probes; even a skipped native test is no pass."""
    result = command(ctx, [ctx.python_bin, '-B', '-m', 'unittest', '-v', *targets], timeout=180)
    if 'skipped=' in result.stderr or '... skipped ' in result.stderr or 'Ran 0 tests' in result.stderr:
        raise ValueError('required synthetic probe did not execute: ' + result.stderr[-4000:])
    return {'status': 'pass', 'synthetic_only': True, 'targets': targets,
            'output': result.stderr[-6000:]}


def arm_check(ctx):
    return probe(ctx, ['tests.align.test_w1_smoke_paths.ArmPathTests'])


def triage_integrity_check(ctx):
    # Probe the current schema, rather than claiming that malformed/failed
    # check entries stand in for stale-but-valid evidence.
    from tests.align.test_v4_cadence import passing_packet, INTERNAL
    packet = passing_packet()
    packet['created_at_epoch_s'] = 1
    verdict = cadence.next_arm_triage(packet, INTERNAL)
    return {'status': 'fail' if verdict['admitted'] else 'pass', 'synthetic_only': True,
            'stale_valid_packet_admitted': verdict['admitted'],
            'reason': 'Production triage v1 has no freshness/record-digest binding; lead ruling required.'}


def r1_chain_check(ctx):
    return probe(ctx, ['tests.align.test_w1_smoke_paths.R1ChainTests'])


def meter_check(ctx):
    return probe(ctx, ['tests.align.test_w1_smoke_paths.MeterPathTests'])


def number(value, name):
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
    return value


def validate_series(plan):
    """Check a planning-only projection, never outcomes or a live series record.

    The lead supplies this projection of the frozen series. It deliberately has
    no energy/score fields and is not a new registration authority.
    """
    if plan.get('schema') != SERIES_SCHEMA:
        raise ValueError('missing planning-only series projection')
    windows = plan.get('windows')
    if not isinstance(windows, list) or not windows:
        raise ValueError('series projection needs windows in frozen order')
    ids = [w.get('window') for w in windows]
    if any(not isinstance(w, str) or not w.strip() for w in ids) or len(set(ids)) != len(ids):
        raise ValueError('series window ids must be nonempty and unique')
    calibration = [w for w in windows if w.get('role') == 'calibration']
    if [w['window'] for w in calibration] != [f'C{i}' for i in range(1, 9)]:
        raise ValueError('planned calibration must be fixed C1-C8 in order')
    roles = [w.get('role') for w in windows]
    if any(r not in ('w1', 'calibration', 'test') for r in roles):
        raise ValueError('unknown series role')
    if roles != sorted(roles, key={'w1': 0, 'calibration': 1, 'test': 2}.get) or roles.count('w1') != 1:
        raise ValueError('freeze one W1, then calibration, then test windows')
    if 'test' not in roles:
        raise ValueError('test cohort must be declared separately')
    rows = []
    for w in calibration:
        if w.get('benign_per_pair') != {'spam': 7, 'bank': 7}:
            raise ValueError('planned default calibration roster needs seven benign per pair')
        rows.append({'window': w['window'], 'status': 'final', 'captured_members': 22,
                     'eligible_benign': dict(w['benign_per_pair'])})
    decisions = [cadence.calibration_stop(rows[:n])['decision'] for n in range(9)]
    if decisions != ['continue'] * 8 + ['calibration_complete']:
        raise ValueError('calibration predicate is not fixed-8')
    zero = {'window': 'zero', 'status': 'final', 'captured_members': 0,
            'eligible_benign': {'spam': 0, 'bank': 0}}
    if cadence.calibration_stop(rows[:1] + [zero])['attempted'] != 1:
        raise ValueError('zero capture consumed a calibration slot')
    if cadence.calibration_stop([zero, {**zero, 'window': 'zero2'}])['decision'] != 'escalate_to_lead':
        raise ValueError('two consecutive zero captures did not escalate')
    if cadence.calibration_stop([{**zero, 'captured_members': 1}])['attempted'] != 1:
        raise ValueError('partial capture did not consume a slot')
    short = [{**w, 'eligible_benign': {'spam': 7, 'bank': 4}} for w in rows]
    if cadence.calibration_stop(short)['decision'] != 'insufficient_calibration':
        raise ValueError('insufficient pair did not stop at eight')
    pending = rows[:-1] + [{**rows[-1], 'status': 'provisional'}]
    if cadence.calibration_stop(pending)['decision'] != 'pending_final_eligibility':
        raise ValueError('pending eighth-window eligibility did not refuse')
    return {'calibration_order': [w['window'] for w in calibration], 'decisions': decisions,
            'zero_capture_does_not_count': True, 'two_zero_captures_escalate': True}


def series_check(ctx):
    if not ctx.w1_series:
        raise ValueError('--w1-series is required; never infer the planned series from outcomes')
    raw = read_local(ctx.repo, ctx.w1_series)
    value = json.loads(raw)
    source = value.get('source') or {}
    if hashlib.sha256(read_local(ctx.repo, source.get('path', ''))).hexdigest() != source.get('sha256'):
        raise ValueError('series projection does not bind its frozen source manifest bytes')
    return {'status': 'pass', 'projection_sha256': hashlib.sha256(raw).hexdigest(),
            **validate_series(value)}


def validate_deadline(plan):
    """Size from explicit segments, including every possible encounter/redo.

    RUN_STATE 215/216's 67,371/96,427 floors are R1-only. Applying them to
    W1 would confuse two different programs. W1 keeps its own installed span.
    """
    maximum = number(plan.get('window_max_s'), 'window_max_s')
    budget = plan.get('smoke_deadline_projection')
    if not isinstance(budget, dict) or budget.get('kind') not in ('r1', 'w1'):
        raise ValueError('installed plan needs a smoke_deadline_projection (r1 or w1)')
    segments = budget.get('segments')
    if not isinstance(segments, list) or not segments:
        raise ValueError('deadline projection needs actual segment/retry schedule')
    total, retries, encounters = 0., 0, 0
    for s in segments:
        attempts = s.get('attempts')
        if type(attempts) is not int or attempts < 1:
            raise ValueError('segment attempts must include all permitted retries')
        possible = s.get('batch_encounters')
        if type(possible) is not int or not 0 <= possible <= attempts:
            raise ValueError('batch_encounters must cover every attempt that can meet the blackout')
        retries += attempts - 1
        encounters += possible
        total += attempts * number(s.get('bound_s'), 'segment bound_s') + possible * 11164
    overhead = sum(number(budget.get(k), k) for k in ('bracket_s', 'close_s', 'harvest_s'))
    required = total + overhead
    if budget['kind'] == 'r1':
        required = max(required, (96427 if retries else 67371) + overhead)
    if maximum < required:
        raise ValueError(f'window_max_s {maximum} < corrected requirement {required} s')
    return {'required_s': required, 'window_max_s': maximum, 'kind': budget['kind'],
            'encounters': encounters, 'retries': retries, 'overhead_s': overhead,
            'authority': 'RUN_STATE 215/216; R1 floors are not W1 floors'}


def deadline_check(ctx):
    if not ctx.w1_window_plan:
        raise ValueError('--w1-window-plan is required; check installed bytes, not the stale R1 display')
    raw = read_local(ctx.repo, ctx.w1_window_plan)
    return {'status': 'pass', 'plan_sha256': hashlib.sha256(raw).hexdigest(),
            **validate_deadline(json.loads(raw))}


CHECKS = (('w1-arm-cli', arm_check), ('w1-executed-receipt', receipt_check),
          ('w1-calibration-series', series_check), ('w1-r1-chain', r1_chain_check),
          ('w1-meter-launch', meter_check), ('w1-window-deadline', deadline_check),
          ('w1-triage-integrity', triage_integrity_check))
