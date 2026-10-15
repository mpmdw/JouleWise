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
TERM_GRACE_S = {'sampler': 10., 'model': 60., 'capture': 30., 'child': 10.}


class TeardownBlocked(RuntimeError):
    """A live or unverifiable group needs the director; never kill its relay."""
    def __init__(self, groups):
        self.groups = groups
        self.actions = [a for g in groups for a in g.get('director_actions', [])]
        super().__init__(f'owned process group not gone: {groups}')


def group_members(pgid):
    """UID census is required before escalation; an unreadable census forbids KILL."""
    try:
        reply = subprocess.run([str(fence('/bin/ps')), '-o', 'pid=,uid=,command=', '-g', str(pgid)],
                               capture_output=True, text=True, timeout=2, check=False)
        if reply.returncode not in (0, 1):
            return None
        members = []
        for line in reply.stdout.splitlines():
            pid, uid, command = line.strip().split(None, 2)
            members.append({'pid': int(pid), 'uid': int(uid), 'argv': command, 'pgid': pgid})
        return members
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def shutdown_kind(argv):
    if 'joulewise' in argv and 'run' in argv:
        return 'model'
    if any('joulewise.hazards.instrument' in str(a) or a == 'joulewise.quiet_kit.capture' for a in argv):
        return 'capture'
    if any(Path(str(a)).name == 'powermetrics' for a in argv):
        return 'sampler'
    return 'child'


def require_group_absent(pgid, *, member_reader=group_members):
    """A child-reported leftover is evidence to stop, never signal authority."""
    from joulewise.hazards.instrument import group_absent
    gone, census = group_absent(pgid, timeout_s=.2)
    if gone:
        return
    members = member_reader(pgid)
    actions = [{'director_action': 'root_sampler_orphan', **m, 'group': pgid}
               for m in (members or []) if m['uid'] == 0]
    if not actions:
        actions = [{'director_action': 'owned_process_group_unverifiable', 'pid': pgid,
                    'pgid': pgid, 'group': pgid, 'argv': None, 'census': census}]
    raise TeardownBlocked([{'pgid': pgid, 'gone': False, 'census': census,
                            'members': members, 'director_actions': actions}])


def check_capture_teardown(directory):
    """A finished capture can leave a separate sudo group in its own journal."""
    import json
    journal = fence(Path(directory)/'raw/children.jsonl')
    if not journal.is_file():
        return
    pending = set()
    for line in read_bytes(journal).splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict) or row.get('schema') != CHILD_SCHEMA:
            continue
        if row.get('event') == 'spawn':
            pending.add(row['pgid'])
        elif row.get('event') == 'stop':
            for group in row.get('groups', []):
                if group.get('gone'):
                    pending.discard(group['pgid'])
                else:
                    pending.add(group['pgid'])
    for pgid in sorted(pending):
        require_group_absent(pgid)


def process_identity(pid):
    """Reuse the repository's microsecond-resolution Darwin birth identity."""
    from joulewise.quiet_guard_process import SysctlDarwinProcessReader
    from joulewise.hazards.clock import read_boot_session_inprocess
    row = SysctlDarwinProcessReader()._process_row(pid)
    if row is None:
        return None
    return {'pid': row.pid, 'start_time': row.start_time, 'boot_session_uuid': read_boot_session_inprocess()}


class Processes:
    def __init__(self, repo: Path, *, identity_reader=process_identity,
                 member_reader=group_members, now=time.monotonic, sleep=time.sleep):
        self.repo = fence(repo)
        self.processes = {}
        self.lock = threading.RLock()
        self.serial = 0
        self.identity_reader = identity_reader
        self.member_reader, self.now, self.sleep = member_reader, now, sleep
        self.blocked = {}

    def spawn(self, argv, directory, *, role='test', env=None, shutdown=None):
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
            p.quiet_kit_shutdown = shutdown or shutdown_kind(argv)
            p.quiet_kit_argv = argv
            append(directory / 'children.jsonl', {'schema': CHILD_SCHEMA, 'event': 'spawn', 'argv': argv, 'pid': p.pid,
                                                  'pgid': p.pid, 'identity': identity,
                                                  'role': role,
                                                  'shutdown': p.quiet_kit_shutdown,
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

    def stop(self, p):
        from joulewise.hazards.instrument import group_absent
        with self.lock:
            entry = self.processes.get(p.pid)
            if entry is None:
                return [{'pgid': p.pid, 'gone': True, 'already_reaped': True}]
            if p.pid in self.blocked:
                raise TeardownBlocked(self.blocked[p.pid])
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
                except (ProcessLookupError, PermissionError):
                    pass
            def term_leader(pgid):
                try:
                    os.kill(pgid, signal.SIGTERM)
                except (ProcessLookupError, PermissionError):
                    pass

            for pgid in groups:
                try:
                    os.killpg(pgid, signal.SIGTERM)
                except PermissionError:
                    # sudo can relay TERM to a root child that killpg cannot
                    # signal. INT does not have this relay behaviour.
                    term_leader(pgid)
                except ProcessLookupError:
                    pass
            started = self.now()
            grace = TERM_GRACE_S[getattr(p, 'quiet_kit_shutdown', 'model')]
            retry = False
            pending, evidence = set(groups), {}
            while pending:
                # Reap the leader before censusing: a zombie is not a live
                # sampler, and must not unnecessarily consume the grace.
                try:
                    p.wait(timeout=0)
                except subprocess.TimeoutExpired:
                    pass
                for pgid in list(pending):
                    gone, lines = group_absent(pgid, timeout_s=.05)
                    evidence[pgid] = {'pgid': pgid, 'gone': gone, 'census': lines, 'term_grace_s': grace}
                    if gone:
                        pending.remove(pgid)
                if not pending:
                    break
                if not retry and self.now()-started >= grace/2:
                    for pgid in pending:
                        term_leader(pgid)
                    retry = True
                if self.now()-started >= grace:
                    break
                self.sleep(min(.25, max(0., started+grace-self.now())))
            # Snapshot every surviving group before escalating any of them.
            # A separate-session root descendant also protects its controller.
            members = {pgid: self.member_reader(pgid) for pgid in pending}
            roots = [m for rows in members.values() for m in (rows or []) if m['uid'] == 0]
            all_owned = all(rows and all(m['uid'] == os.getuid() for m in rows) for rows in members.values())
            for pgid in sorted(pending):
                rows = members[pgid]
                evidence[pgid]['members'] = rows
                gone, lines = group_absent(pgid, timeout_s=.05)
                if gone:
                    evidence[pgid].update(gone=True, census=[])
                    continue
                if all_owned and not roots:
                    # Re-read immediately before KILL, never authorize it from
                    # a missing UID or from the leader's ownership alone.
                    live = self.member_reader(pgid)
                    if not live or any(m['uid'] != os.getuid() for m in live):
                        evidence[pgid]['members'] = live
                        continue
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                    try:
                        p.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        pass
                    gone, lines = group_absent(pgid, timeout_s=2)
                    evidence[pgid].update(gone=gone, census=lines)
            evidence = list(evidence.values())
            for row in evidence:
                if not row['gone']:
                    root_rows = [m for m in (row.get('members') or []) if m['uid'] == 0]
                    row['director_actions'] = [
                        {'director_action': 'root_sampler_orphan', **m, 'group': m['pgid']} for m in root_rows]
                    if not root_rows:
                        row['director_actions'] = [{'director_action': 'owned_process_group_unverifiable',
                            'pid': p.pid, 'pgid': row['pgid'], 'group': row['pgid'],
                            'argv': getattr(p, 'quiet_kit_argv', None), 'census': row['census']}]
            if entry:
                append(entry[2] / 'children.jsonl', {'schema': CHILD_SCHEMA, 'event': 'stop', 'pid': p.pid,
                                                    'identity': getattr(p, 'quiet_kit_identity', None),
                                                    'returncode': p.returncode, 'groups': evidence})
            if any(not e['gone'] for e in evidence):
                self.blocked[p.pid] = evidence
                raise TeardownBlocked(evidence)
            self.processes.pop(p.pid, None)
            return evidence

    def cleanup(self, *, role='test'):
        rows = []
        blocked = False
        with self.lock:
            for p, r, directory in list(self.processes.values()):
                if r == role:
                    try:
                        rows += self.stop(p)
                    except TeardownBlocked as exc:
                        rows += exc.groups
                        blocked = True
        if blocked:
            raise TeardownBlocked(rows)
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
                    if not gone:
                        pgid = row.get('pgid', pid)
                        members = self.member_reader(pgid)
                        actions = [{'director_action': 'root_sampler_orphan', **m, 'group': pgid}
                                   for m in (members or []) if m['uid'] == 0]
                        outcome.update(director_actions=actions, groups=[{'pgid': pgid, 'gone': False,
                            'census': census, 'members': members, 'director_actions': actions}])
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
                    process = SimpleNamespace(pid=pid, returncode=None, wait=wait, quiet_kit_identity=expected,
                        quiet_kit_shutdown=row.get('shutdown', shutdown_kind(row.get('argv', []))),
                        quiet_kit_argv=row.get('argv'))
                    self.processes[pid] = (process, 'test', journal.parent)
                    try:
                        evidence = self.stop(process)
                        outcome = {'pid': pid, 'gone': True, 'blocking': False, 'groups': evidence,
                                   'reason': 'verified prior-job child stopped'}
                    except TeardownBlocked as exc:
                        outcome = {'pid': pid, 'blocking': True, 'reason': 'prior-job child teardown failed',
                                   'groups': exc.groups, 'director_actions': exc.actions}
                    except Exception as exc:
                        outcome = {'pid': pid, 'blocking': True, 'reason': 'prior-job child teardown failed', 'error': str(exc)}
                outcomes.append(outcome)
                if outcome.get('gone'):
                    append(journal, {'schema': CHILD_SCHEMA, 'event': 'stop', 'pid': pid, 'identity': expected,
                                     'groups': [{'pgid': row.get('pgid', pid), 'gone': True}], 'recovery': outcome})
        return outcomes
