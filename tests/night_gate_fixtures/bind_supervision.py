"""Disposable real-exec fault bench; invoked only by supervision regressions.

The control socket is separate from the production result pipe. Fake time
cannot advance until every launched worker acknowledges its fault point.
"""
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def frame(job_id, value):
    raw = json.dumps(dict(job_id=job_id, ok=True, result=value)).encode()
    return len(raw).to_bytes(4, 'big') + raw


def worker(args):
    from joulewise import quiet_admission as qa
    fd, control_fd = int(args[0]), int(args[1])
    spec = json.loads(args[2])
    qa.prepare_result_descriptor(fd)
    os.set_inheritable(control_fd, False)
    control = socket.socket(fileno=control_fd)
    with open(spec['registry'], 'a') as out:
        out.write(str(os.getpid()) + '\n')
    def ack(stage, **extra):
        control.sendall((json.dumps(dict(stage=stage, **extra)) + '\n').encode())
    mode = spec['mode']
    payload = frame(spec['id'], spec['value'])
    if mode.startswith('descendant'):
        # Only the separate liveness/control descriptor is intentionally inherited.
        os.set_inheritable(control_fd, True)
        child = subprocess.Popen([sys.executable, '-B', '-c',
            'import os,sys,time\ntry: os.fstat(int(sys.argv[1])); closed=False\n'
            'except OSError: closed=True\nprint(int(closed),flush=True)\ntime.sleep(3600)', str(fd)],
            stdout=subprocess.PIPE, close_fds=False, text=True)
        closed = child.stdout.readline().strip() == '1'
        child.stdout.close()
        ack('fault', descendant=child.pid, fd_closed=closed)
        if mode == 'descendant_exit':
            return
        time.sleep(3600)
    elif mode == 'partial_header':
        ack('fault')
        os.write(fd, payload[:2])
    elif mode == 'partial_body':
        ack('fault')
        os.write(fd, payload[:5])
    elif mode == 'recv_stall':
        os.write(fd, payload[:5])
        ack('fault')
        time.sleep(3600)
    elif mode == 'oversize':
        ack('fault')
        os.write(fd, (256 * 1024 + 1).to_bytes(4, 'big'))
        while True:
            os.write(fd, b'x' * 65536)
    elif mode == 'empty':
        ack('fault')
    elif mode == 'serialize_oversize':
        ack('fault')
        qa.publish_observation(fd, spec['id'], lambda: 'x' * (256 * 1024))
        return
    elif mode in ('startup_hang', 'presend_hang'):
        ack('fault')
        time.sleep(3600)
    elif mode == 'term_delay':
        def delayed_exit(signum, _frame):
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            ack('signalled')
            time.sleep(2.5)
            os._exit(0)
        signal.signal(signal.SIGTERM, delayed_exit)
        ack('fault')
        time.sleep(3600)
    elif mode == 'slow':
        ack('fault')
        chunks = (payload[:2], payload[2:5], payload[5:])
        for index, chunk in enumerate(chunks):
            control.recv(1)
            os.write(fd, chunk)
            ack('chunk', index=index)
        time.sleep(3600)
    else:
        ack('fault')
        if spec['kind'] == 'sample':
            control.recv(1)
        # Tell the bench before publishing; it cannot move fake time until
        # the frame is consumed. A complete frame requires neither EOF nor exit.
        ack('publishing')
        if mode == 'postsend_hang':
            os.write(fd, payload)
            ack('published')
            time.sleep(3600)
        else:
            qa.publish_observation(fd, spec['id'], lambda: spec['value'])
            return
    os.close(fd)


class Bench:
    def __init__(self, scenario, directory):
        from scripts import run_night as driver
        from joulewise import night_gate
        from tests.test_night_gate import FakeProbeSource, make_plan, REGISTRATION_TEXT
        from tests.test_quiet_admission import POLICY
        self.driver, self.gate = driver, night_gate
        self.scenario, self.directory = scenario, directory
        self.registry = str(directory / 'workers')
        self.now = 400.0 if scenario.endswith('_late') else 0.0
        self.tasks, self.samples, self.census_ticks = [], 0, []
        self.round_start = self.now
        self.source = FakeProbeSource()
        self.plan = dataclasses.replace(make_plan(), window_max_s=9600,
            quiet_admission=dict(POLICY, busy_core_max=0.05, consecutive_quiet_samples=1))
        self.probes = dataclasses.replace(self.source.probes(), now_epoch_s=lambda: 1000+self.now,
                                        monotonic_ns=lambda: int(self.now*1e9))
        night_gate.D166_REGISTRATION_SHA256 = hashlib.sha256(REGISTRATION_TEXT.encode()).hexdigest()
        self.tick_cost = []
        self.chunk_early = []
        self.chunk_deadlines = []
        self.result_probes = []
        self.blocked_writer = None
        self.block_event = None
        self.writer_entered = threading.Event()
        self.expiry_wall = None

    def dispatch(self, kind, job_id, call, request, launcher):
        from tests.test_quiet_admission import metrics
        from tests.test_run_night import BOOT_UUID
        control, child = socket.socketpair()
        control.setblocking(False)
        mode = 'normal'
        if kind == 'sample':
            self.samples += 1
            mode = self.scenario.removesuffix('_late')
            if mode in ('journal_block', 'journal_error', 'journal_system_exit', 'journal_saturation', 'census_hit', 'round_cost', 'large_frame', 'census_stall_hit', 'journal_late_power'):
                mode = 'normal'
            if self.scenario == 'presend_hang' and self.samples > 1:
                mode = 'normal'
            value = dict(wall_start=1000+self.now, wall_end=1030+self.now,
                monotonic_start=self.now, monotonic_end=self.now+30, interval_s=30,
                boot_identity=BOOT_UUID, census=dict(exit_code=1, stdout='', stderr=''),
                raw_sha256=dict(ps_before='a'*64, ps_after='b'*64, top='c'*64),
                metrics=metrics(.02), load_avg_diagnostic={'raw':'3.7'})
            if self.scenario == 'large_frame':
                value['load_avg_diagnostic']['raw'] = 'x' * 200000
        elif kind == 'census':
            self.census_ticks.append(self.now)
            value = call()
            if self.scenario in ('census_hit', 'census_stall_hit') and self.now >= 90:
                value['refusal'] = dict(reason='night_refused_agent_present', detail='fixture census hit', evidence=[])
        else:
            value = json.loads(call().to_json_bytes())
        if self.scenario == 'census_stall_hit' and kind == 'census' and self.now == 0:
            mode = 'presend_hang'
        if self.scenario == 'census_hit' and kind == 'sample':
            mode = 'presend_hang'
        if self.scenario == 'startup_hang' and kind == 'static':
            mode = 'startup_hang'
        spec = dict(id=job_id, kind=kind, mode=mode, value=value, registry=self.registry)
        task = self.driver._BindTask(job_id, lambda fd: (
            sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(fd),
            str(child.fileno()), json.dumps(spec)), launcher, test_pass_fds=(child.fileno(),))
        self.tasks.append(dict(task=task, kind=kind, mode=mode, control=control, child=child,
            buffer=b'', events=[], ack=False, eof=False, sent=0, began=self.now, max_bytes=0, max_reads=0, max_buffer=0,
            ack_until=time.monotonic()+1, result_checked=False))
        return task

    def controls(self):
        for row in self.tasks:
            if row['task'].launch_done and row['child'] is not None:
                row['child'].close()
                row['child'] = None
            while True:
                try:
                    data = row['control'].recv(65536)
                except BlockingIOError:
                    break
                if not data:
                    row['eof'] = True
                    break
                row['buffer'] += data
            while b'\n' in row['buffer']:
                line, row['buffer'] = row['buffer'].split(b'\n', 1)
                event = json.loads(line)
                row['events'].append(event)
                if event['stage'] == 'fault':
                    row['ack'] = True
            row['max_reads'] = max(row['max_reads'], row['task'].reads_last_tick)
            row['max_bytes'] = max(row['max_bytes'], row['task'].bytes_last_tick)
            row['max_buffer'] = max(row['max_buffer'], len(row['task'].buffer))

    def sleep(self, duration):
        self.controls()
        if self.blocked_writer is not None:
            assert self.writer_entered.is_set(), 'journal barrier fault not acknowledged'
        if self.scenario == 'slow':
            # Inspect the actual ticker's local deadline, including after every
            # transport chunk; checking only the receipt's epoch misses resets.
            ticker = sys._getframe(1)
            assert ticker.f_code.co_name == 'bind_until_quiet'
            actual = ticker.f_locals['deadline']
            chunks = sum(e['stage'] == 'chunk' for r in self.tasks for e in r['events'])
            assert actual == 600, f'bind deadline changed after chunk {chunks}: {actual} != 600'
            if chunks and chunks > len(self.chunk_deadlines):
                self.chunk_deadlines.append([chunks, actual])
        if self.scenario == 'journal_late_power' and self.now >= 60 and self.blocked_writer is not None:
            argv = self.gate.PMSET_BATT_ARGV
            self.source.results[argv] = self.gate.ProbeResult(argv, 0, "Now drawing from 'Battery Power'", '', 0)
            self.block_event.set()
            self.blocked_writer = None
        # Test-only waits yield to real subprocesses; fake time is frozen until
        # the separate control channel acknowledges each actual fault point.
        for row in self.tasks:
            task = row['task']
            # Cancellation is NOT evidence that the injected fault was reached.
            # Fault workers must ACK even if a complete/invalid frame cancelled
            # them before this sleep call; unlaunched normal jobs have no fault.
            if not row['ack'] and (not task.cancelled or row['mode'] != 'normal'):
                assert time.monotonic() < row['ack_until'], f"fault ACK missing: {row['mode']} {task.job_id}"
                time.sleep(.001)
                return
            if task.cancelled:
                continue
            if row['mode'] == 'startup_hang' and not row['result_checked']:
                assert task.process.poll() is None, 'startup fault worker exited'
                began = time.perf_counter()
                try:
                    task.result()
                except self.gate.ProbeError as error:
                    assert 'not published' in str(error)
                else:
                    raise AssertionError('unpublished result was accepted')
                elapsed = time.perf_counter()-began
                assert elapsed < .05, f'result() waited on startup worker: {elapsed}'
                row['result_checked'] = True
                self.result_probes.append(['startup', elapsed])
            if row['kind'] != 'sample' and row['mode'] not in ('startup_hang', 'presend_hang') and not task.ready():
                time.sleep(.001)
                return
            if row['kind'] == 'sample' and row['mode'] in ('normal', 'postsend_hang', 'slow'):
                age = self.now - row['began']
                if row['mode'] == 'slow':
                    chunks = sum(e['stage'] == 'chunk' for e in row['events'])
                    if chunks < row['sent']:
                        time.sleep(.001)
                        return
                    if row['sent'] < 3 and age >= (row['sent'] + 1) * 10:
                        self.chunk_early.append((row['sent'], task.ready(), self.now))
                        row['control'].send(b'x')
                        row['sent'] += 1
                        time.sleep(.001)
                        return
                    if row['sent'] == 3 and not task.ready():
                        time.sleep(.001)
                        return
                elif age >= 30 and not task.ready():
                    first_release = not row['sent']
                    if first_release:
                        row['control'].send(b'x')
                        row['sent'] = 1
                    if row['mode'] == 'postsend_hang' and first_release:
                        until = time.monotonic() + .5
                        while not any(e['stage'] == 'published' for e in row['events']) and time.monotonic() < until:
                            self.controls()
                            time.sleep(.001)
                        assert any(e['stage'] == 'published' for e in row['events']), 'publication fault not acknowledged'
                        task.advance()
                        assert task.ready(), 'published frame was not consumed'
                        assert task.process.poll() is None, 'post-publication worker exited'
                        began = time.perf_counter()
                        task.result()  # exercise the real cached accessor BEFORE cancellation
                        elapsed = time.perf_counter()-began
                        assert elapsed < .05, f'result() waited on published worker: {elapsed}'
                        self.result_probes.append(['published', elapsed])
                    if first_release or row['mode'] != 'postsend_hang':
                        time.sleep(.001)
                        return
                    # Publication is independently acknowledged. A mutant that
                    # waits for child exit must not freeze the test's clock.
        live_samples = [row for row in self.tasks if not row['task'].cancelled and
                        (row['kind'] == 'sample' or row['mode'] in ('startup_hang', 'presend_hang'))]
        # Once fsync has acknowledged its injected fault, fake time must also
        # run while awaiting an ACK that a swallowed-exception mutant lost.
        failed_write = self.scenario in ('journal_error', 'journal_system_exit') and self.writer_entered.is_set()
        if live_samples or failed_write or (self.blocked_writer is not None and not self.blocked_writer.failure and self.now < 600):
            for row in self.tasks:
                if row['mode'] != 'normal':
                    assert row['ack'], f"fake time advanced without fault ACK: {row['mode']}"
            self.now = min(600, self.now + 5)
            if self.now == 600 and self.expiry_wall is None:
                self.expiry_wall = time.perf_counter()
        time.sleep(.001)

    def journal_factory(self, directory):
        outer = self
        class Blocked(self.driver._BindJournal):
            def _run(self):
                if outer.scenario == 'journal_saturation':
                    import queue
                    self.requests = queue.Queue(maxsize=1)
                # A barrier holds actual journal I/O off the deadline thread.
                # It is released only after the supervisor returns its refusal.
                outer.writer_entered.set()
                outer.block_event.wait()
                super()._run()
        self.block_event = threading.Event()
        if self.scenario in ('journal_error', 'journal_system_exit'):
            # The real writer/handler runs; only the fsync boundary raises.
            return self.driver._BindJournal(directory)
        writer = Blocked(directory)
        assert self.writer_entered.wait(1), 'journal barrier fault not acknowledged'
        self.blocked_writer = writer
        return writer

    def run(self):
        writer_args = {'journal_factory': self.journal_factory} if self.scenario.startswith('journal_') else {}
        original_killpg = os.killpg
        def signal_boundary(pid, sig):
            if self.scenario == 'term_delay_late' and any(
                    r['mode'] == 'term_delay' and getattr(r['task'].process, 'pid', None) == pid for r in self.tasks):
                sig = signal.SIGTERM
            return original_killpg(pid, sig)
        original_fsync = os.fsync
        def write_boundary(fd):
            if self.scenario in ('journal_error', 'journal_system_exit'):
                self.writer_entered.set()
                error = SystemExit if self.scenario == 'journal_system_exit' else OSError
                raise error('injected journal write failure')
            return original_fsync(fd)
        before = self.driver._bind_cpu()
        with mock.patch.object(os, 'fsync', write_boundary), mock.patch.object(os, 'killpg', signal_boundary):
            receipt = self.driver.bind_until_quiet(self.plan, self.probes, self.directory,
                test_dispatch=self.dispatch, monotonic=lambda: self.now, sleep=self.sleep, wall_clock=lambda: 1000+self.now, **writer_args)
        returned_after_expiry = time.perf_counter()-self.expiry_wall if self.expiry_wall is not None else None
        after = self.driver._bind_cpu()
        self.controls()
        if self.scenario == 'slow' and receipt.refusal:
            # The ticker catches callback assertions as probe errors. Surface
            # this exact invariant assertion again outside that catch boundary.
            assert 'bind deadline changed' not in receipt.refusal.detail, receipt.refusal.detail
        if self.scenario == 'term_delay_late':
            assert returned_after_expiry <= 1.05, f'expiry-to-receipt exceeded tick + cleanup budget: {returned_after_expiry:.3f}s'
            assert receipt.admission.get('supervision_residue'), 'unreaped child omitted from receipt'
            sample = next(r for r in self.tasks if r['kind'] == 'sample')
            assert sample['ack'] and {'stage': 'signalled'} in sample['events'], 'signal fault not acknowledged'
            task = sample['task']
            assert task.process.poll() is None, 'slow-exit child exited before receipt'
            original_killpg(task.process.pid, signal.SIGKILL)
            task.process.wait(timeout=1)
            task.reaped = True
        if self.scenario.startswith('descendant'):
            until = time.monotonic() + .5
            while not all(row['eof'] for row in self.tasks) and time.monotonic() < until:
                self.controls()
                time.sleep(.001)
        if self.block_event:
            self.block_event.set()
        value = json.loads(receipt.to_json_bytes())
        assert not self.gate.validate_receipt(value), self.gate.validate_receipt(value)
        tasks = []
        for row in self.tasks:
            task = row['task']
            pid = getattr(task.process, 'pid', None)
            if row['mode'] != 'normal':
                assert row['ack'], f"fault ACK missing: {row['mode']} {task.job_id}"
            assert task.closed, 'worker was not reaped'
            if pid is not None:
                try:
                    found = os.waitpid(pid, os.WNOHANG)
                except ChildProcessError:
                    pass
                else:
                    raise AssertionError(f'direct child was not reaped: {pid}: {found}')
            tasks.append(dict(id=task.job_id, kind=row['kind'], events=row['events'],
                ready=task.ready(), control_eof=row['eof'], max_bytes=row['max_bytes'], max_buffer=row['max_buffer'], max_reads=row['max_reads'],
                reaped=task.reaped, pid=pid))
            row['control'].close()
        samples_path = self.directory/'quiet_samples.jsonl'
        samples = [json.loads(line) for line in samples_path.read_text().splitlines()] if samples_path.exists() else []
        return dict(receipt=value, samples=samples, tasks=tasks, now=self.now,
                    census_ticks=self.census_ticks, sample_jobs=self.samples,
                    chunk_early=self.chunk_early, chunk_deadlines=self.chunk_deadlines,
                    result_probes=self.result_probes, returned_after_expiry=returned_after_expiry,
                    journal_entered=self.writer_entered.is_set(), measured_cpu=after-before)


def launch_pending_case(directory):
    """Block real Popen.__init__ in the real daemon, then permit the late exec."""
    bench = Bench('launch_pending', directory)
    entered, release = threading.Event(), threading.Event()
    original_init = subprocess.Popen.__init__
    def exec_boundary(process, *args, **kwargs):
        if threading.current_thread().name == 'night-bind-launch':
            entered.set()  # Separate launch-fault ACK; no child exists yet.
            release.wait()
        original_init(process, *args, **kwargs)
    expiry = None
    def tick_sleep(duration):
        nonlocal expiry
        assert entered.wait(1), 'exec fault not acknowledged'
        if bench.now < 600:
            bench.now += 5
            if bench.now == 600:
                expiry = time.perf_counter()
        time.sleep(.001)
    try:
        with mock.patch.object(subprocess.Popen, '__init__', exec_boundary):
            receipt = bench.driver.bind_until_quiet(bench.plan, bench.probes, directory,
                test_dispatch=bench.dispatch, monotonic=lambda: bench.now,
                sleep=tick_sleep, wall_clock=lambda: 1000+bench.now)
            elapsed = time.perf_counter()-expiry
            assert elapsed <= 1.05, f'expiry-to-receipt exceeded tick + cleanup budget: {elapsed:.3f}s'
            assert entered.is_set() and not release.is_set(), 'exec was not blocked through receipt'
            value = json.loads(receipt.to_json_bytes())
            assert value['verdict'] == 'REFUSED'
            residue = value.get('supervision_residue', [])
            assert residue and residue[0]['job_id'] == 'census-1', 'launch-pending job omitted from receipt'
            assert all(row['state'] == 'launch_pending' for row in residue), residue
            assert not bench.gate.validate_receipt(value), bench.gate.validate_receipt(value)
            release.set()
            until = time.monotonic()+1
            while not all(row['task'].launch_done for row in bench.tasks) and time.monotonic() < until:
                time.sleep(.001)
        tasks = []
        for row in bench.tasks:
            task = row['task']
            assert task.launch_done, 'late launcher did not finish'
            pid = getattr(task.process, 'pid', None)
            if pid is not None:
                assert task.reaped, 'late child was not reaped by launcher'
                assert task.process.returncode == -signal.SIGKILL, 'late child survived cancellation'
                try:
                    os.waitpid(pid, os.WNOHANG)
                except ChildProcessError:
                    pass
                else:
                    raise AssertionError('late child left a zombie')
            row['control'].close()
            row['child'].close()
            tasks.append(dict(id=task.job_id, kind=row['kind'], pid=pid, reaped=task.reaped,
                max_reads=0, max_bytes=0, max_buffer=0))
        return dict(receipt=value, tasks=tasks, now=bench.now, returned_after_expiry=elapsed,
                    census_ticks=bench.census_ticks, sample_jobs=0)
    finally:
        release.set()


if __name__ == '__main__':
    if sys.argv[1] == '--worker':
        worker(sys.argv[2:])
    elif sys.argv[1] == 'launch_pending':
        print(json.dumps(launch_pending_case(Path(sys.argv[2]))), flush=True)
    else:
        bench = Bench(sys.argv[1], Path(sys.argv[2]))
        print(json.dumps(bench.run()), flush=True)
