"""Bounded, roster-ordered read preparation; publication stays in the caller.

One pool per desk, explicit spawn on every platform, no persistent input cache.
Timing receipts are separate from scientific reports and include failed stages.
"""
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from contextvars import ContextVar
import json
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys
import time

_current = ContextVar('align_desk_execution', default=None)


def current_execution():
    return _current.get()


@contextmanager
def host_desk_guard(workers):
    """Keep parallel host desks out of both armed and measuring Mac windows.

    Retain the night lock through shutdown/publication so a concurrent install
    cannot arm between the check and the work. Plan-0 nights do not hold that
    lock, so also require the shared launchd night job to be absent. Replay
    over portable exports deliberately does not use this host admission path.
    """
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('desk workers must be an integer from 1 to 8')
    if workers == 1 or sys.platform != 'darwin':
        yield
        return
    from joulewise.align.apple.powermode import HostLock
    lock = HostLock(role='parallel-desk')
    try:
        if not lock.acquire():
            raise ValueError('parallel desk refused: a window holds the host night lock')
        label = 'com.joulewise.night'
        job = subprocess.run(['launchctl', 'print', f'gui/{os.getuid()}/{label}'],
                             capture_output=True, text=True, check=False, timeout=10)
        absent = f'Could not find service "{label}" in domain for user gui: {os.getuid()}'
        if job.returncode != 113 or absent not in (job.stderr or '').splitlines():
            raise ValueError('parallel desk refused: night job is armed/measuring or its state is unknown')
        yield
    finally:
        lock.release()


def _call(function, task):
    started, cpu = time.perf_counter(), time.process_time()
    value = function(task)
    return value, time.perf_counter()-started, time.process_time()-cpu


class DeskExecution:
    def __init__(self, workers=1, profile=None):
        if type(workers) is not int or not 1 <= workers <= 8:
            raise ValueError('desk workers must be an integer from 1 to 8')
        self.workers, self.profile = workers, profile
        self.stages, self.pool = [], None

    def __enter__(self):
        if self.profile is not None and Path(self.profile).exists():
            raise ValueError('desk profile already exists')
        if self.profile is not None and not Path(self.profile).parent.is_dir():
            raise ValueError('desk profile parent directory must exist')
        self.token = _current.set(self)
        self.started = time.perf_counter()
        return self

    def __exit__(self, kind, value, traceback):
        try:
            if self.pool is not None:
                self.pool.shutdown(wait=True, cancel_futures=True)
            if self.profile is not None:
                record = {'schema': 'joulewise.align.desk_timing.v1', 'workers': self.workers,
                          'wall_s': time.perf_counter()-self.started,
                          'status': 'ok' if kind is None else kind.__name__, 'stages': self.stages}
                try:
                    with Path(self.profile).open('x') as handle:
                        handle.write(json.dumps(record, indent=2, sort_keys=True)+'\n')
                except OSError as error:
                    if value is None:
                        raise
                    value.add_note(f'desk timing receipt failed: {error}')
        finally:
            _current.reset(self.token)

    @contextmanager
    def stage(self, name):
        started, cpu = time.perf_counter(), time.process_time()
        row = {'name': name, 'status': 'ok'}
        try:
            yield row
        except BaseException as exc:
            row['status'] = type(exc).__name__
            raise
        finally:
            row.update(wall_s=time.perf_counter()-started, parent_cpu_s=time.process_time()-cpu)
            self.stages.append(row)

    def map(self, name, function, tasks):
        """At most 2*workers submitted reads, results/errors in roster order."""
        with self.stage(name) as row:
            row.update(items=0, task_wall_s=0., task_cpu_s=0., tasks=[])
            values = []
            if self.workers == 1:
                results = (_call(function, task) for task in tasks)
            else:
                if self.pool is None:
                    self.pool = ProcessPoolExecutor(max_workers=self.workers,
                        mp_context=multiprocessing.get_context('spawn'))
                results = self._ordered(function, iter(tasks))
            for value, wall, cpu in results:
                values.append(value)
                row['tasks'].append({'ordinal': row['items'], 'wall_s': wall, 'cpu_s': cpu})
                row['items'] += 1
                row['task_wall_s'] += wall
                row['task_cpu_s'] += cpu
            return values

    def call(self, name, function, *args, **kwargs):
        with self.stage(name):
            return function(*args, **kwargs)

    def _ordered(self, function, tasks):
        pending = deque()
        try:
            for _ in range(2*self.workers):
                try:
                    task = next(tasks)
                except StopIteration:
                    break
                pending.append(self.pool.submit(_call, function, task))
            while pending:
                yield pending.popleft().result()
                try:
                    task = next(tasks)
                except StopIteration:
                    continue
                pending.append(self.pool.submit(_call, function, task))
        finally:
            for future in pending:
                future.cancel()
