"""R16 per-window attempt accounting in the canonical series ledger.

A reservation survives a reinstall/crash. It is never an admission decision.
The lead commits the updated series state before rebuilding the arm packet.
"""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path

from joulewise.align.apple import condition_waits as cw


@contextmanager
def locked(path):
    path = Path(path)
    if path.name != 'state.json' or path.parent.name != 'series':
        raise ValueError('R16 attempts require the canonical series/state.json')
    with (path.parent/'.condition-waits.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(path.read_bytes())
        if state.get('schema') != 'joulewise.align_v4.series_state.v1':
            raise ValueError('wrong series ledger schema')
        yield state
        temporary = path.with_name('state.json.condition-waits.tmp')
        with temporary.open('x') as handle:
            handle.write(json.dumps(state, sort_keys=True, indent=2, allow_nan=False)+'\n')
        os.replace(temporary, path)


def reserve(path, *, window, attempt_id, ambient_check, started):
    if not isinstance(window, str) or not window.strip():
        raise ValueError('fixed series window identity required')
    with locked(path) as state:
        rows = state.setdefault('condition_waits_attempts', {}).setdefault(window, [])
        if rows and rows[-1]['attempt_id'] == attempt_id:
            if rows[-1].get('status') != 'reserved':
                raise ValueError('R16 attempt already ended; reinstall cannot repeat it')
            return rows[-1]['attempt_number']
        number = len(rows)+1
        if rows and (rows[-1].get('status') != 'not_ready'
                or (ambient_check or {}).get('previous_not_ready_sha256') != rows[-1].get('receipt_sha256')):
            raise ValueError('prior R16 attempt unresolved; lead ruling required')
        # Reuse the exact freshness/two-attempt validation, never a new rule.
        cw.Attempt(cw.registration_policy(cohort='ledger-validation', q=None, cw1=None,
                   incumbent_policy_sha256='0'*64), attempt_id=attempt_id, boot_id='ledger',
                   started=started, quiet_start_ns=started['monotonic_ns'],
                   attempt_number=number, ambient_check=ambient_check)
        rows.append({'attempt_id': attempt_id, 'attempt_number': number, 'status': 'reserved',
                     'ambient_check': ambient_check})
        return number


def finish(path, window, receipt):
    with locked(path) as state:
        rows = state['condition_waits_attempts'][window]
        row = rows[-1]
        if (row['attempt_id'] != receipt['attempt_id'] or row['attempt_number'] != receipt['attempt_number']
                or row['status'] not in ('reserved', 'released')):
            raise ValueError('receipt does not bind the reserved R16 attempt')
        row.update(status=receipt['status'], receipt_sha256=cw.digest(receipt))


def verify(state, window, header):
    rows = state.get('condition_waits_attempts', {}).get(window, [])
    return bool(rows and len(rows) <= 2 and rows[-1]['attempt_id'] == header['attempt_id']
                and rows[-1]['attempt_number'] == header.get('attempt_number', 1)
                and rows[-1].get('ambient_check') == header.get('ambient_check')
                and rows[-1]['status'] in ('reserved', 'released'))
