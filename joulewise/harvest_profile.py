"""Opt-in engineering timings, kept outside immutable harvest/custody output."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time


class StageProfile:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else None
        self.stream = None

    def __enter__(self):
        if self.path is not None:
            self.stream = self.path.open('x', encoding='utf-8')
            self.observe({'schema': 'joulewise.harvest_profile.v1',
                          'cpu': 'parent only; excludes subprocess/worker CPU',
                          'inclusive': ['harvest.total', 'cli.total', 'archive']})
        self.start = time.monotonic()
        return self

    def observe(self, row):
        if self.stream is not None:
            self.stream.write(json.dumps(row, sort_keys=True) + '\n')
            self.stream.flush()

    @contextmanager
    def stage(self, name):
        start, cpu, failed = time.monotonic(), time.process_time(), True
        try:
            yield
            failed = False
        finally:
            self.observe({'stage': name, 'wall_s': time.monotonic()-start,
                          'parent_cpu_s': time.process_time()-cpu, 'failed': failed})

    def __exit__(self, kind, value, traceback):
        if self.stream is not None:
            try:
                self.observe({'stage': 'cli.total', 'wall_s': time.monotonic()-self.start,
                              'failed': kind is not None})
                os.fsync(self.stream.fileno())
            finally:
                self.stream.close()
