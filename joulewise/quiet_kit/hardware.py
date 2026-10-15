"""Production seams. Importing this module starts no instruments."""
from __future__ import annotations

import dataclasses
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from .paths import append, atomic_json, executable, fence, mkdir, read_bytes
from .processes import Processes


class Hardware:
    def __init__(self, repo: Path, model_python: str):
        self.repo, self.model_python = fence(repo), executable(model_python)
        self.processes = Processes(self.repo)
        self.caffeine = None
        self.index = 0
        self.now = lambda: time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        self.current_directory = None
        self.cancel_hook = lambda: False
        self.root_cancel_hook = lambda: False

    def bind_cancel(self, callback):
        self.root_cancel_hook = callback

    def stamp(self):
        from .collectors import stamp
        return stamp()

    def sampler(self, directory, control):
        from .collectors import Sampler
        return Sampler(self, directory, control)

    def host_cpu(self):
        from joulewise.hazards.contention import read_host_cpu
        return read_host_cpu()

    def ctx(self, directory=None, *, probe_directory=None):
        from joulewise.hazards.base import Context
        class FencedContext(Context):
            def keep_raw(self, name, data):
                if self.raw_dir is not None:
                    fence(Path(self.raw_dir) / ((f'{self.label}-' if self.label else '') + name))
                return super().keep_raw(name, data)
        self.index += 1
        probe_directory = probe_directory or directory or self.current_directory
        return FencedContext(run=lambda argv, timeout: self._owned_probe(argv, timeout, probe_directory),
                             raw_dir=mkdir(directory) if directory else None,
                             custody_root=fence(directory) if directory else None, label=f'qk-{self.index:06d}')

    def run_probe(self, argv, timeout):
        return self._owned_probe(argv, timeout, self.current_directory)

    def _owned_probe(self, argv, timeout, directory):
        from joulewise.hazards.base import Completed
        for a in argv:
            if str(a).startswith('/'):
                fence(a)
        if directory is None:
            raise ValueError('probe output directory is required')
        output = mkdir(fence(directory)/'probe-children')
        argv = tuple(str(a) for a in argv)
        try:
            child = self.processes.spawn(argv, output)
        except OSError as exc:
            return Completed(argv, None, b'', b'', error=f'{type(exc).__name__}: {exc}')
        deadline = self.now()+timeout
        timed_out = False
        error = None
        try:
            while child.poll() is None:
                if self.root_cancel_hook() or self.cancel_hook() or self.now() >= deadline:
                    timed_out = self.now() >= deadline
                    error = 'probe cancelled' if not timed_out else None
                    self.processes.stop(child, graceful=True)
                    break
                time.sleep(.05)
            stdout = read_bytes(child.quiet_kit_stdout)
            stderr = read_bytes(child.quiet_kit_stderr)
            self.processes.stop(child, graceful=True)
            return Completed(argv, child.returncode, stdout, stderr, timed_out=timed_out, error=error)
        except BaseException:
            self.processes.stop(child, graceful=True)
            raise

    def census(self, directory):
        from joulewise.hazards.arm import agent_census
        return agent_census(self.ctx(probe_directory=directory))

    def probe(self, name, directory, parameters):
        from joulewise.hazards import arm, battery, clock, contention, disk, instrument, smc, thermal
        self.current_directory = fence(directory)
        self.cancel_hook = parameters['cancel']
        modules = dict(battery=battery, clock=clock, contention=contention, disk=disk, instrument=instrument, thermal=thermal)
        module, ctx = modules[name], self.ctx(directory)
        thresholds = arm.default_thresholds()[name]
        duration = parameters['duration_s']
        if name == 'battery':
            measurement = battery.measure(ctx, smc_read=smc.read_once)
        elif name == 'thermal':
            measurement = thermal.measure(ctx)
        elif name == 'disk':
            root = fence(parameters['archive'])
            thresholds.update(planned_bytes=parameters['planned_bytes'], headroom_bytes=20*1024**3)
            measurement = disk.measure(ctx, targets=[{'path': str(root), 'copies': 1}],
                statvfs=lambda p: os.statvfs(fence(p)), stat=lambda p: os.stat(fence(p)))
        elif name == 'contention':
            if parameters['record_only']:
                thresholds.update(clean_s=duration, interval_s=10., cap_s=duration)
            else:
                # Bound each dwell by the job deadline; the existing module
                # already waits for 180 continuous clean seconds.
                thresholds['cap_s'] = min(thresholds['cap_s'], max(1., parameters['deadline']-self.now()))
            def on_tick():
                if parameters['cancel']():
                    from .runner import Deadline
                    raise Deadline('stopped during contention dwell')
            measurement = contention.run_dwell(ctx, thresholds, tree_roots=parameters['tree_roots'], on_tick=on_tick)
        elif name == 'instrument':
            if not parameters['record_only']:
                measurement = instrument.measure(ctx, python=sys.executable,
                    privilege_prefix=('/usr/bin/sudo', '-n'))
            else:
                measurement, thresholds = self.short_sampler(ctx, duration, thresholds)
        else:
            started = ctx.stamp()
            boot = clock.read_boot_session(ctx)
            readings = []
            stop = time.monotonic()+duration
            while time.monotonic() < stop:
                if parameters['cancel']():
                    from .runner import Deadline
                    raise Deadline('stopped during clock probe')
                readings.append(clock.sample(ctx))
                time.sleep(min(1., max(0., stop-time.monotonic())))
            readings.append(clock.sample(ctx))
            measurement = clock.series(readings, boot_start=boot, boot_end=clock.read_boot_session(ctx),
                                       started=started, finished=ctx.stamp())
        return {'measurement': measurement.to_json(), 'verdict': module.judge(measurement, thresholds).to_json(),
                'shortened': parameters['record_only'] and name in ('contention', 'instrument', 'clock')}

    def short_sampler(self, ctx, seconds, thresholds):
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter, parse_powermetrics_records
        from joulewise.hazards.base import Measurement
        from joulewise.hazards.instrument import cadence_statistics
        output = fence(ctx.raw_dir / 'short-sampler.plist')
        adapter = PowermetricsTelemetryAdapter(None, privilege_prefix=('/usr/bin/sudo', '-n'))
        # At the delivered ~130 ms cadence, 154 production-shaped records
        # take about 20 s. This is explicitly a shortened plumbing probe.
        count = max(1, round(seconds/.1305))
        limits = {**thresholds, 'frames': count, 'bound_s': seconds+10}
        argv = adapter._command(None, output, count=count, interval_ms=100)
        started = ctx.stamp()
        completed = self._owned_probe(argv, seconds+10, ctx.raw_dir)
        error = completed.error or ('shortened sampler timed out' if completed.timed_out else None)
        values = {'argv': argv, 'count_expected': count, 'frames': 0, 'returncode': completed.returncode,
                  'elapsed_s': (ctx.stamp().monotonic_ns-started.monotonic_ns)/1e9,
                  'group_gone': True, 'group_census': [], 'bound_s': seconds+10}
        try:
            records = parse_powermetrics_records(read_bytes(output))
            values.update(frames=len(records), **cadence_statistics([r.elapsed_ns for r in records]))
        except (ValueError, OSError) as e:
            error = str(e)
        return Measurement('instrument', 'instant', values, (), started, ctx.stamp(), error), limits

    def watch(self, directory):
        from joulewise.hazards import smc, thermal
        reading = thermal.measure(self.ctx(probe_directory=directory))
        level = reading.values.get('level')
        sample = smc.read_once()
        errors = list((sample.get('errors') or {}).values())
        if reading.error:
            errors.append(reading.error)
        return {'thermal_level': level, 'battery_current_ma': sample.get('values', {}).get('B0AC'),
                'smc': sample, 'error': '; '.join(str(e) for e in errors) or None}

    def observe(self, directory):
        from joulewise.hazards import clock, contention
        ctx = self.ctx(probe_directory=directory)
        snapshot = contention.take_snapshot(ctx, host_reader=None)
        agents = {}
        for name in ('mediaanalysisd', 'photoanalysisd'):
            rows = [r for r in snapshot.rows.values() if name in r.get('command', '')]
            agents[name] = {'present': bool(rows), 'cpu_seconds': sum(r['cumulative_cpu_seconds'] for r in rows),
                            'identities': [[r['pid'], r.get('start_identity')] for r in rows]}
        def probe(argv):
            completed = ctx.run(argv, 10.)
            return {'argv': argv, 'returncode': completed.returncode, 'error': completed.error,
                    'stdout': completed.stdout.decode(errors='replace'), 'stderr': completed.stderr.decode(errors='replace')}
        hid = probe(['/usr/sbin/ioreg', '-c', 'IOHIDSystem', '-l'])
        display = probe(['/usr/sbin/ioreg', '-r', '-c', 'IODisplayWrangler', '-l'])
        usb = probe(['/usr/sbin/ioreg', '-p', 'IOUSB', '-l'])
        osbuild = probe(['/usr/sbin/sysctl', '-n', 'kern.osversion'])
        match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', hid['stdout'])
        state = re.search(r'"CurrentPowerState"\s*=\s*(\d+)', display['stdout'])
        try:
            boot = clock.read_boot_session(ctx)
        except Exception:
            boot = None
        return {'analysis_agents': agents, 'screensaver_present': any('ScreenSaverEngin' in r.get('command', '')
                   for r in snapshot.rows.values()), 'hid_idle_ns': int(match[1]) if match else None,
                'display_state': int(state[1]) if state else None,
                'meter_present': bool(re.search('KM003C|POWER.?Z', usb['stdout'], re.I)),
                'os_build': osbuild['stdout'].strip() or None, 'boot_session_uuid': boot,
                'diagnostics': {'hid': hid, 'display': display, 'usb': usb, 'os_build': osbuild},
                'ps_error': snapshot.error}

    def action(self, name, directory):
        from joulewise.hazards.arm import NETWORK_TIME_OFF_ARGV
        self.current_directory = fence(directory)
        if name == 'caffeinate':
            argv = ['/usr/bin/caffeinate', '-i', '-s', '-w', str(os.getpid())]
            try:
                self.caffeine = self.processes.spawn(argv, directory, role='job')
            except OSError as exc:
                return {'argv': argv, 'pid': None, 'error': str(exc)}
            return {'argv': argv, 'pid': self.caffeine.pid}
        if name == 'stop_caffeinate':
            if self.caffeine:
                return self.processes.stop(self.caffeine, graceful=True)
            return []
        argv = list(NETWORK_TIME_OFF_ARGV) if name == 'network_time_off' else ['/usr/bin/pmset', 'displaysleepnow']
        completed = self.run_probe(argv, 30.)
        row = {'argv': argv, 'returncode': completed.returncode, 'stdout': completed.stdout.decode(errors='replace'),
               'stderr': completed.stderr.decode(errors='replace'), 'error': completed.error, 'timed_out': completed.timed_out}
        append(directory / 'actions.jsonl', row)
        return row

    def code(self, model=False):
        def git(args):
            p = subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True, timeout=10)
            return p.stdout.decode().strip()
        commit, dirty = git(['rev-parse', 'HEAD']), git(['status', '--porcelain'])
        versions = {}
        if model:
            payload = ('import importlib.metadata,json; '
                       'names=("mlx","mlx_lm","mlx-metal"); out={}; '
                       '\nfor n in names:\n try: out[n]=importlib.metadata.version(n)\n except importlib.metadata.PackageNotFoundError: out[n]=None'
                       '\nprint(json.dumps(out))')
            reply = self.run_probe([self.model_python, '-c', payload], 20.)
            try:
                versions = json.loads(reply.stdout)
            except ValueError:
                versions = {'error': reply.stderr.decode(errors='replace') or reply.error}
        return {'git_commit': commit, 'dirty': bool(dirty), 'git_status_porcelain': dirty,
                'python': sys.executable, 'model_python': self.model_python, 'mlx_versions': versions}

    def clock_start(self, attempt, kind):
        return self.processes.spawn([sys.executable, '-m', 'joulewise.quiet_kit.clocklog',
            '--out', str(fence(attempt / 'clock.jsonl')), '--kind', kind,
            '--parent-pid', str(os.getpid())], attempt, role='job')

    def clock_stop(self, process):
        return self.processes.stop(process, graceful=True)

    def collect(self, plan, attempt, scale, control, kind):
        from .collectors import collect
        self.current_directory = fence(attempt)
        self.cancel_hook = lambda: bool(control.reason or control.runner.stop) or self.now() >= control.runner.deadline
        return collect(self, plan, attempt, scale, control, kind)

    def cleanup(self):
        return self.processes.cleanup(role='test')

    def recover(self, root):
        return self.processes.recover(root)

    def wake(self, content, logfile):
        with fence(logfile).open('ab') as handle:
            process = subprocess.Popen(['/bin/zsh', '-c', content], stdin=subprocess.DEVNULL,
                stdout=handle, stderr=handle, start_new_session=True,
                cwd=self.repo, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        return {'pid': process.pid, 'detached': True}
