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
import time

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
        os.write(fd, payload[:2])
        ack('fault')
    elif mode == 'partial_body':
        os.write(fd, payload[:5])
        ack('fault')
    elif mode == 'recv_stall':
        os.write(fd, payload[:5])
        ack('fault')
        time.sleep(3600)
    elif mode == 'oversize':
        os.write(fd, (256 * 1024 + 1).to_bytes(4, 'big'))
        ack('fault')
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
        self.blocked_writer = None
        self.block_event = None

    def dispatch(self, kind, job_id, call, request, launcher):
        from tests.test_quiet_admission import metrics
        from tests.test_run_night import BOOT_UUID
        control, child = socket.socketpair()
        control.setblocking(False)
        mode = 'normal'
        if kind == 'sample':
            self.samples += 1
            mode = self.scenario.removesuffix('_late')
            if mode in ('journal_block', 'journal_error', 'journal_saturation', 'census_hit', 'round_cost', 'large_frame', 'census_stall_hit', 'journal_late_power'):
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
            buffer=b'', events=[], ack=False, eof=False, sent=0, began=self.now, max_bytes=0, max_reads=0, max_buffer=0))
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
        if self.scenario == 'journal_late_power' and self.now >= 60 and self.blocked_writer is not None:
            argv = self.gate.PMSET_BATT_ARGV
            self.source.results[argv] = self.gate.ProbeResult(argv, 0, "Now drawing from 'Battery Power'", '', 0)
            self.block_event.set()
            self.blocked_writer = None
        # Test-only waits yield to real subprocesses; fake time is frozen until
        # the separate control channel acknowledges each actual fault point.
        for row in self.tasks:
            task = row['task']
            if task.cancelled:
                continue
            if not row['ack']:
                time.sleep(.001)
                return
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
                    if first_release or row['mode'] != 'postsend_hang':
                        time.sleep(.001)
                        return
                    # Publication is independently acknowledged. A mutant that
                    # waits for child exit must not freeze the test's clock.
        live_samples = [row for row in self.tasks if not row['task'].cancelled and
                        (row['kind'] == 'sample' or row['mode'] in ('startup_hang', 'presend_hang'))]
        if live_samples or (self.blocked_writer is not None and not self.blocked_writer.failure and self.now < 600):
            self.now = min(600, self.now + 5)
        time.sleep(.001)

    def journal_factory(self, directory):
        import threading
        outer = self
        class Blocked(self.driver._BindJournal):
            def _run(self):
                if outer.scenario == 'journal_error':
                    self.failure = 'OSError: injected journal write failure'
                    self.done = True
                    return
                if outer.scenario == 'journal_saturation':
                    import queue
                    self.requests = queue.Queue(maxsize=1)
                # A barrier holds actual journal I/O off the deadline thread.
                # It is released only after the supervisor returns its refusal.
                outer.block_event.wait()
                super()._run()
        self.block_event = threading.Event()
        writer = Blocked(directory)
        self.blocked_writer = writer
        return writer

    def run(self):
        writer_args = {'journal_factory': self.journal_factory} if self.scenario.startswith('journal_') else {}
        before = self.driver._bind_cpu()
        receipt = self.driver.bind_until_quiet(self.plan, self.probes, self.directory,
            test_dispatch=self.dispatch, monotonic=lambda: self.now, sleep=self.sleep, wall_clock=lambda: 1000+self.now, **writer_args)
        after = self.driver._bind_cpu()
        self.controls()
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
                    chunk_early=self.chunk_early, measured_cpu=after-before)


if __name__ == '__main__':
    if sys.argv[1] == '--worker':
        worker(sys.argv[2:])
    else:
        bench = Bench(sys.argv[1], Path(sys.argv[2]))
        print(json.dumps(bench.run()), flush=True)
