"""Owned subprocess groups, bounded waits and observable teardown."""
from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from types import SimpleNamespace

from .paths import append, fence, files, mkdir, read_bytes

CHILD_SCHEMA = 'joulewise.quiet_kit.child.v1'


def process_identity(pid):
    """Reuse the repository's microsecond-resolution Darwin birth identity."""
    from joulewise.quiet_guard_process import SysctlDarwinProcessReader
    from joulewise.hazards.clock import read_boot_session_inprocess
    row = SysctlDarwinProcessReader()._process_row(pid)
    if row is None:
        return None
    return {'pid': row.pid, 'start_time': row.start_time, 'boot_session_uuid': read_boot_session_inprocess()}


class Processes:
    def __init__(self, repo: Path, *, identity_reader=process_identity):
        self.repo = fence(repo)
        self.processes = {}
        self.lock = threading.RLock()
        self.serial = 0
        self.identity_reader = identity_reader

    def spawn(self, argv, directory, *, role='test', env=None):
        argv = [str(a) for a in argv]
        for arg in argv:
            if arg.startswith('/'):
                fence(arg)
        directory = mkdir(directory)
        with self.lock:
            self.serial += 1
            stem = f'child-{self.serial:04d}'
            output = fence(directory / (stem + '.stdout'))
            error = fence(directory / (stem + '.stderr'))
            with output.open('ab') as out, error.open('ab') as err:
                p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                    cwd=self.repo, env={**os.environ, 'PYTHONPATH': str(self.repo),
                        'PYTHONDONTWRITEBYTECODE': '1', 'LC_ALL': 'C', **(env or {})}, start_new_session=True)
            self.processes[p.pid] = (p, role, directory)
            try:
                identity = self.identity_reader(p.pid)
            except Exception as exc:
                identity = {'error': str(exc)}
            p.quiet_kit_identity = identity
            append(directory / 'children.jsonl', {'schema': CHILD_SCHEMA, 'event': 'spawn', 'argv': argv, 'pid': p.pid,
                                                  'pgid': p.pid, 'identity': identity,
                                                  'role': role,
                                                  'stdout': output.name, 'stderr': error.name})
            p.quiet_kit_stdout = output
            p.quiet_kit_stderr = error
            return p

    def wait(self, p, control, timeout=3600):
        start = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        while p.poll() is None:
            control.check()
            if time.clock_gettime(time.CLOCK_MONOTONIC_RAW)-start > timeout:
                self.stop(p)
                raise TimeoutError(f'child {p.pid} exceeded {timeout} s')
            control.wait(.1)
        return p.returncode

    def stop(self, p, *, graceful=False):
        from joulewise.hazards.instrument import group_absent
        with self.lock:
            entry = self.processes.get(p.pid)
            if entry is None:
                return [{'pgid': p.pid, 'gone': True, 'already_reaped': True}]
            # Discover descendants while the parent still exists: imported
            # instruments may create a separate session for their own child.
            from joulewise.hazards import contention
            from joulewise.hazards.base import Context
            snapshot = contention.take_snapshot(Context(), host_reader=None)
            owned = contention.tree_identities(snapshot.rows.values(), [p.pid]) if not snapshot.error else {p.pid}
            groups = {p.pid}
            for pid in owned:
                try:
                    pgid = os.getpgid(pid)
                    if pgid != os.getpgrp():
                        groups.add(pgid)
                except ProcessLookupError:
                    pass
            first = signal.SIGTERM if graceful else signal.SIGINT
            for pgid in groups:
                try:
                    os.killpg(pgid, first)
                except ProcessLookupError:
                    pass
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            evidence = []
            for pgid in sorted(groups):
                gone, lines = group_absent(pgid, timeout_s=.2)
                if not gone:
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    p.wait(timeout=5)
                    gone, lines = group_absent(pgid, timeout_s=2)
                evidence.append({'pgid': pgid, 'gone': gone, 'census': lines})
            if entry:
                append(entry[2] / 'children.jsonl', {'schema': CHILD_SCHEMA, 'event': 'stop', 'pid': p.pid,
                                                    'identity': getattr(p, 'quiet_kit_identity', None),
                                                    'returncode': p.returncode, 'groups': evidence})
            if any(not e['gone'] for e in evidence):
                raise RuntimeError(f'owned process group not gone: {evidence}')
            self.processes.pop(p.pid, None)
            return evidence

    def cleanup(self, *, role='test'):
        rows = []
        with self.lock:
            for p, r, directory in list(self.processes.values()):
                if r == role:
                    rows += self.stop(p, graceful=True)
        return rows

    def recover(self, root):
        """Reap only verified children recorded by earlier crashed kit jobs.

No PID is signalled from a command-name match alone. A changed birth identity
or boot is recorded and left alone; an unreadable identity is a restart block
handed back to the director, rather than authority to signal another process.
"""
        import json
        outcomes = []
        for journal in files(fence(root)):
            if journal.name != 'children.jsonl':
                continue
            pending = {}
            for line in read_bytes(journal).splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(row, dict) or row.get('schema') != CHILD_SCHEMA:
                    continue
                if row.get('event') == 'spawn':
                    pending[row['pid']] = row
                elif row.get('event') == 'stop' and row.get('groups') and all(g.get('gone') for g in row['groups']):
                    pending.pop(row.get('pid'), None)
            for pid, row in pending.items():
                expected = row.get('identity') or {}
                try:
                    actual = self.identity_reader(pid)
                except Exception as exc:
                    outcomes.append({'pid': pid, 'blocking': True, 'reason': 'orphan identity unreadable', 'error': str(exc)})
                    continue
                if actual is None:
                    # Without a leader, do not signal an unverified group.
                    from joulewise.hazards.instrument import group_absent
                    gone, census = group_absent(row.get('pgid', pid))
                    outcome = {'pid': pid, 'gone': gone, 'blocking': not gone, 'census': census,
                               'reason': 'recorded leader gone'}
                elif not expected.get('start_time') or not expected.get('boot_session_uuid'):
                    outcome = {'pid': pid, 'blocking': True, 'reason': 'recorded birth identity missing'}
                elif (actual.get('start_time'), actual.get('boot_session_uuid')) != (
                        expected['start_time'], expected['boot_session_uuid']):
                    outcome = {'pid': pid, 'gone': True, 'blocking': False,
                               'reason': 'recorded process is gone; PID or boot changed; replacement not signalled'}
                else:
                    def wait(timeout, pid=pid):
                        until = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)+timeout
                        while time.clock_gettime(time.CLOCK_MONOTONIC_RAW) < until:
                            observed = self.identity_reader(pid)
                            if observed is None or observed.get('start_time') != expected['start_time']:
                                return None
                            time.sleep(.05)
                        return None
                    process = SimpleNamespace(pid=pid, returncode=None, wait=wait, quiet_kit_identity=expected)
                    self.processes[pid] = (process, 'test', journal.parent)
                    try:
                        evidence = self.stop(process, graceful=True)
                        outcome = {'pid': pid, 'gone': True, 'blocking': False, 'groups': evidence,
                                   'reason': 'verified prior-job child stopped'}
                    except Exception as exc:
                        outcome = {'pid': pid, 'blocking': True, 'reason': 'prior-job child teardown failed', 'error': str(exc)}
                outcomes.append(outcome)
                if outcome.get('gone'):
                    append(journal, {'schema': CHILD_SCHEMA, 'event': 'stop', 'pid': pid, 'identity': expected,
                                     'groups': [{'pgid': row.get('pgid', pid), 'gone': True}], 'recovery': outcome})
        return outcomes
