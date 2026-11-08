"""Create-once smoke transcripts and a fail-closed parser; no study analysis.

The recorder takes an injected command runner. The parser reopens the named,
hashed smoke artifacts and derives verdicts; it never accepts a supplied PASS.
An unrun case, an unrelated refusal, a timeout, or missing teardown is a FAIL.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time

SCHEMA = 'joulewise.align_v4.smoke.v1'
CASES = ('window', 'triage-stale', 'triage-edited', 'receipt-digest', 'disk-image',
         'cpu-contender', 'meter-killed', 'missing-topup', 'r1-chain')
REFUSALS = {
    'triage-stale': (1, 'next_arm_triage'),
    'triage-edited': (1, 'next_arm_triage'),
    'receipt-digest': (1, 'registration_receipt digest drift'),
    'disk-image': (1, 'external_volume'),
    'cpu-contender': (3, 'contention'),
    'missing-topup': (1, 'top-up'),
}


def local(root, relative):
    p = Path(relative)
    if (p.is_absolute() or not p.parts or
            any(x in ('..', 'restricted', 'night-custody', 'night-archive') for x in p.parts)):
        raise ValueError('smoke artifact must be a safe relative path')
    current = Path(root)
    for part in p.parts:
        current /= part
        if current.is_symlink():
            raise ValueError('smoke artifacts may not traverse symlinks')
    return current


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def bounded_run(argv, *, timeout, **kwargs):
    """Own the command group so a recorder timeout also stops its descendants.

    This does not claim to uninstall detached launchd jobs; the native recipe
    still owes explicit per-attempt teardown and absence verification.
    """
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        for sig, grace in ((signal.SIGTERM, 5), (signal.SIGKILL, 5)):
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass
            try:
                stdout, stderr = process.communicate(timeout=grace)
                break
            except subprocess.TimeoutExpired:
                continue
        else:
            raise RuntimeError('smoke command group did not close after TERM/KILL')
        raise subprocess.TimeoutExpired(argv, timeout, output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)


def init(root, candidate):
    root = Path(root)
    if len(candidate) != 40 or any(c not in '0123456789abcdef' for c in candidate):
        raise ValueError('candidate must be a full commit SHA')
    root.mkdir(parents=True, exist_ok=False)
    write_once(root / 'SMOKE.json', {'schema': SCHEMA, 'candidate': candidate,
        'label': 'smoke', 'registrable': False, 'pool_eligible': False,
        'analysis_eligible': False, 'created_epoch_s': time.time(),
        'warning': 'NON-REGISTRABLE; never pool or analyse'})


def capture(root, case, argv, *, artifacts=(), chain_start=None, timeout_s=120,
            run=bounded_run, clock=time.monotonic):
    """Run ONE operator-specified attempt and retain argv/stdout/stderr/exit.

    Setup/teardown belong to the exact-case checklist. ``teardown.json`` must
    subsequently carry the actual teardown command results; absence fails.
    This API never labels a failed injection a success by its return code alone.
    """
    root = Path(root)
    if case not in CASES or not argv or not 0 < timeout_s <= 2700:
        raise ValueError('unknown case, empty command or unbounded timeout')
    label = json.loads((root / 'SMOKE.json').read_bytes())
    if (not isinstance(label, dict) or label.get('schema') != SCHEMA or
            label.get('label') != 'smoke' or label.get('registrable') is not False):
        raise ValueError('unlabelled output; initialize an isolated smoke root first')
    out = local(root, case)
    out.mkdir(exist_ok=False)
    started = clock()
    try:
        result = run(argv, capture_output=True, text=True, timeout=timeout_s, check=False)
        record = {'argv': list(argv), 'returncode': result.returncode,
                  'stdout': result.stdout, 'stderr': result.stderr, 'timed_out': False}
    except subprocess.TimeoutExpired as exc:
        record = {'argv': list(argv), 'returncode': None, 'stdout': str(exc.stdout or ''),
                  'stderr': str(exc.stderr or ''), 'timed_out': True}
    record.update(schema=SCHEMA, case=case, candidate=label['candidate'], seconds=clock() - started, artifacts={})
    if chain_start is not None:
        record['chain_start'] = {'path': chain_start, 'present': local(root, chain_start).exists()}
    for name, relative in artifacts:
        try:
            raw = local(root, relative).read_bytes()
            record['artifacts'][name] = {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest()}
        except (OSError, ValueError) as exc:
            record['artifacts'][name] = {'error': str(exc)}
    write_once(out / 'command.json', record)
    return record


def teardown(root, case, commands, *, run=subprocess.run):
    """Retain cleanup AND verification commands, even when one command fails.

    Commands are supplied explicitly by the operator (no PID/name searches,
    wildcard kills, forced detach, or implicit uninstallation).
    """
    rows = []
    for argv in commands:
        try:
            p = run(argv, capture_output=True, text=True, timeout=30, check=False)
            rows.append({'argv': argv, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
        except (OSError, subprocess.SubprocessError) as exc:
            rows.append({'argv': argv, 'returncode': None, 'error': str(exc)})
    write_once(local(root, case + '/teardown.json'), {'schema': SCHEMA, 'commands': rows,
                                                    'ended_epoch_s': time.time()})
    return rows


def artifacts(root, record):
    out = {}
    for name, locator in record.get('artifacts', {}).items():
        if 'error' in locator:
            raise ValueError('missing artifact ' + name)
        raw = local(root, locator['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != locator.get('sha256'):
            raise ValueError('edited artifact ' + name)
        out[name] = json.loads(raw)
    return out


def evaluate(case, record, evidence):
    if record.get('case') != case or record.get('schema') != SCHEMA or record.get('timed_out') is not False:
        raise ValueError('wrong case/schema or timed-out attempt')
    rc = record.get('returncode')
    if type(rc) is not int:
        raise ValueError('missing exit code')
    if case in REFUSALS:
        expected, reason = REFUSALS[case]
        observation = evidence.get('refusal')
        if case == 'receipt-digest':
            # require_registration raises before an arm record exists. Keep
            # that actual exception transcript, rather than inventing one.
            observation = {'admitted': False, 'reasons': [record.get('stderr', '')]}
        if not isinstance(observation, dict):
            raise ValueError('missing production refusal artifact')
        text = json.dumps(observation).lower() + str(record.get('stderr', '')).lower()
        refused = (observation.get('admitted') is False or observation.get('verdict') == 'REFUSED'
                   or case == 'receipt-digest' and reason in text)
        if rc != expected or not refused or reason.lower() not in text:
            raise ValueError('expected specific refusal was not observed: ' + reason)
        observed = record.get('chain_start')
        if not isinstance(observed, dict) or observed.get('present') is not False:
            raise ValueError('negative arm unexpectedly launched the chain')
        return 'documented refusal, no chain launch'
    if rc != 0:
        raise ValueError(f'command failed ({rc})')
    if case in ('window', 'meter-killed'):
        result, hazard = evidence['night_result'], evidence['hazard_result']
        if result.get('verdict') != 'GO' or result.get('chain_exit_code') != 0 or result.get('aborted_reason'):
            raise ValueError('window did not complete successfully')
        meter = hazard.get('meter') or {}
        if not (meter.get('streams') and (meter.get('stop') or {}).get('proven_stopped') is True):
            raise ValueError('meter capture/stop custody is missing')
        members = evidence['dc_members'].get('members') or {}
        if not 1 <= len(members) <= 2:
            raise ValueError('smoke must execute one or two tiny members')
        gpu = evidence['gpu_members']
        if set(gpu) != set(members):
            raise ValueError('GPU evidence does not cover every executed member')
        for run_id, member in members.items():
            if member.get('powermetrics_admissibility_unchanged') is not True:
                raise ValueError('DC diagnostics changed GPU admissibility')
            channel = gpu[run_id].get('energy', {}).get('powermetrics:gpu_power') or {}
            joules = channel.get('joules')
            flags = gpu[run_id].get('flags', []) + channel.get('flags', [])
            if (type(joules) not in (int, float) or not math.isfinite(joules) or joules < 0
                    or any(str(f).startswith(('power_unavailable', 'trace.missing', 'trace.ambiguous',
                                               'clock_anchor_unresolved')) for f in flags)):
                raise ValueError('GPU channel was unavailable or inadmissible')
        if case == 'meter-killed':
            if not any(m.get('status') == 'missing' and any(str(f).startswith('meter.') for f in m.get('flags', []))
                       for m in members.values()):
                raise ValueError('reader death did not produce a DC-missing member flag')
        elif any(m.get('status') != 'available' for m in members.values()):
            raise ValueError('baseline smoke has missing DC samples')
        # Keep each artifact distinct; direct-child exit is not terminal completion.
        if evidence['finalize'].get('status') != 'ok' or evidence['terminal'].get('terminal') is not True:
            raise ValueError('finalize/terminal completion not observed')
        return 'completed; meter custody and per-member DC checked'
    chain = evidence['chain']
    steps = ('export', 'backfill-x-g', 'backfill-turn-counts', 'derive-contrast', 'kit-check')
    if chain.get('synthetic_only') is not True or chain.get('steps') != dict.fromkeys(steps, 0):
        raise ValueError('all five R1 dry-run steps must complete')
    return 'five synthetic R1-to-W1 steps completed'


def report(root):
    root = Path(root)
    label = json.loads((root / 'SMOKE.json').read_bytes())
    if (not isinstance(label, dict) or label.get('schema') != SCHEMA or label.get('label') != 'smoke' or any(
            label.get(k) is not False for k in ('registrable', 'pool_eligible', 'analysis_eligible'))):
        raise ValueError('not an isolated NON-REGISTRABLE smoke output')
    rows, total = [], 0.
    begin = label.get('created_epoch_s')
    if type(begin) not in (int, float) or not math.isfinite(begin):
        raise ValueError('missing smoke start time')
    end = begin
    for case in CASES:
        try:
            raw = local(root, case + '/command.json').read_bytes()
            record = json.loads(raw)
            if record.get('candidate') != label.get('candidate'):
                raise ValueError('case belongs to a different candidate')
            seconds = record.get('seconds')
            if type(seconds) not in (int, float) or not 0 <= seconds <= 2700:
                raise ValueError('invalid wall time')
            total += seconds
            cleanup = json.loads(local(root, case + '/teardown.json').read_bytes())
            commands = cleanup.get('commands')
            if (cleanup.get('schema') != SCHEMA or not isinstance(commands, list) or not commands
                    or any(c.get('returncode') != 0 or not c.get('argv') for c in commands)):
                raise ValueError('teardown/verification missing or failed')
            stamp = cleanup.get('ended_epoch_s')
            if type(stamp) not in (int, float) or not math.isfinite(stamp) or stamp < begin:
                raise ValueError('invalid teardown time')
            end = max(end, stamp)
            if case in REFUSALS and local(root, record['chain_start']['path']).exists():
                raise ValueError('negative arm chain marker appeared after recording')
            detail = evaluate(case, record, artifacts(root, record))
            rows.append({'check': case, 'status': 'pass', 'detail': detail})
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            rows.append({'check': case, 'status': 'fail', 'detail': str(exc)})
    elapsed = max(total, end - begin)
    rows.append({'check': 'wall-time', 'status': 'pass' if elapsed <= 2700 else 'fail',
                 'detail': f'{elapsed:.1f} seconds including recorded setup/teardown span (target <=2700)'})
    return {'schema': SCHEMA, 'status': 'pass' if all(r['status'] == 'pass' for r in rows) else 'fail',
            'label': label, 'checks': rows}


def table(result):
    return '\n'.join(['| Check | Result | Detail |', '|---|---|---|'] +
                     [f"| {r['check']} | {r['status'].upper()} | {r['detail'].replace('|', '/').replace(chr(10), ' ')} |"
                      for r in result['checks']])
