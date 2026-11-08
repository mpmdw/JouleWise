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
from pathlib import Path
import time

_current = ContextVar('align_desk_execution', default=None)


def current_execution():
    return _current.get()


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
                with Path(self.profile).open('x') as handle:
                    handle.write(json.dumps(record, indent=2, sort_keys=True)+'\n')
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
