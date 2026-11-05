"""Opt-in ALIGN temperature task around the unchanged hazard monitor.

The ordinary monitor and its battery reader retain their issued source bytes.
Only the ALIGN launcher selects this extension; no module globals are patched.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import sys

from joulewise.align.apple import smc
from joulewise.hazards import battery, monitor as core, temperature, thermal
from joulewise.hazards.base import canonical_json, sha256_hex

monitor_dir = core.monitor_dir
read_journal = core.read_journal


def build_config(*, smc_temperature=None, **kwargs):
    config = core.build_config(**kwargs)
    if smc_temperature is not None:
        config['smc_temperature'] = temperature.validate_policy(smc_temperature)
    return config


def validate_config(config):
    config = core.validate_config(config)
    if 'smc_temperature' in config:
        temperature.validate_policy(config['smc_temperature'])
    return config


def load_journals(custody_dir):
    result = core.load_journals(custody_dir)
    directory = monitor_dir(custody_dir)
    if any((directory/name).exists() for name in ('temperature.jsonl', 'temperature.jsonl.zst')):
        result['temperature'] = read_journal(directory/'temperature.jsonl')[0]
    return result


class Monitor(core.Monitor):
    def __init__(self, config, **kwargs):
        super().__init__(validate_config(config), **kwargs)
        self.temperature_policy = self.config.get('smc_temperature')
        self.fast_tasks = core.FAST_TASKS
        if self.temperature_policy:
            self.temperature_keys = temperature.keys(self.temperature_policy)
            self.temperature_coverage = temperature.Coverage(self.started.monotonic_ns, self.temperature_keys)
            self.journals['temperature'] = core.Journal(self.directory/'temperature.jsonl',
                                                       fsync_interval_s=core.FSYNC_INTERVAL_S)
            self.seq['temperature'] = 0
            self.due['temperature'] = self.started.monotonic_ns
            self.cadence = {**self.cadence, 'temperature_s': 1.0}
            self.fast_tasks = (*core.FAST_TASKS, 'temperature')

    def open_session(self, argv=()):
        super().open_session(argv)
        if self.temperature_policy:
            self._write('temperature', 'session_start', values={
                'pid': os.getpid(), 'pgid': os.getpgrp(), 'ppid': os.getppid(), 'argv': list(argv),
                'config_sha256': sha256_hex(canonical_json(self.config)),
                'tree_roots': list(self.tree_roots), 'cadence': dict(self.cadence),
                'smc_temperature': self.temperature_policy})

    def close_session(self, reason):
        if self.temperature_policy:
            self._write('temperature', 'session_end', values={
                'reason': reason, 'coverage': self.temperature_coverage.report(self.ctx.clocks.monotonic_ns())})
        super().close_session(reason)

    def _loop(self, names, deadline):
        if names == core.FAST_TASKS:
            names = self.fast_tasks
        return super()._loop(names, deadline)

    def tick(self, now_ns, names=None):
        super().tick(now_ns, names)
        if (not self.stopping and self.temperature_policy and (names is None or 'temperature' in names)
                and now_ns >= self.due['temperature']):
            self.due['temperature'] += temperature.NS
            if self.due['temperature'] <= now_ns:
                self.due['temperature'] = now_ns + temperature.NS
            started = self.ctx.stamp()
            with self._smc_lock:
                values = temperature.sample(self.smc_reader, self.temperature_keys)
            finished = self.ctx.stamp()
            self.temperature_coverage.observe(started.monotonic_ns, finished.monotonic_ns, values)
            self._write('temperature', 'reading', started=started, finished=finished, values=values,
                        error='; '.join(f'{k}: {v}' for k, v in values['errors'].items()) or None)


def run_forever(config_path: Path, argv=()):
    config = validate_config(json.loads(Path(config_path).read_text()))
    try:
        notify_reader = thermal.NotifyReader()
    except OSError:
        notify_reader = None
    try:
        battery_reader = battery.RegistryReader()
    except OSError:
        battery_reader = None
    reader = smc.Reader() if sys.platform == 'darwin' else None
    observer = Monitor(config, smc_reader=reader, notify_reader=notify_reader, battery_reader=battery_reader)
    def stop(signum, frame):
        observer.stopping, observer.stop_signal = True, signum
    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)}
    try:
        observer.open_session(argv)
        observer.run(fast_thread=True)
    finally:
        try:
            observer.close_session(f"signal {getattr(observer, 'stop_signal', None)}")
        finally:
            if reader is not None:
                reader.close()
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    return 0
