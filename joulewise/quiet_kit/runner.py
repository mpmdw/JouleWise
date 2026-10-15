"""Resumable launchd runner. Hardware and child creation have explicit seams."""
from __future__ import annotations

import dataclasses
import datetime
import fcntl
import os
import signal
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Callable

from . import analysis
from .cli import complete
from .paths import append, atomic, atomic_json, children, create_once, executable, fence, inventory, mkdir, read_bytes, read_json
from .schedule import BY_ID, PLANS
from .processes import TeardownBlocked


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


@dataclasses.dataclass
class Seams:
    """Tests replace hardware actions, keeping disk and analysis production code."""
    census: Callable
    probe: Callable
    observe: Callable
    watch: Callable
    collect: Callable
    clock_start: Callable
    clock_stop: Callable
    action: Callable
    wake: Callable
    code: Callable
    now: Callable = lambda: time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
    raw_ns: Callable = lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    utc: Callable = utc
    sleep: Callable = time.sleep
    cleanup: Callable = lambda: []
    bind_cancel: Callable = lambda callback: None
    recover: Callable = lambda root: []


def production_seams(repo: Path, model_python: str) -> Seams:
    from .hardware import Hardware
    hw = Hardware(repo, model_python)
    return Seams(hw.census, hw.probe, hw.observe, hw.watch, hw.collect,
                 hw.clock_start, hw.clock_stop, hw.action, hw.wake, hw.code,
                 cleanup=hw.cleanup, bind_cancel=hw.bind_cancel, recover=hw.recover)


class Interrupted(Exception):
    pass


class Deadline(Exception):
    pass


class Control:
    def __init__(self, runner, attempt: Path, *, plumbing=False):
        self.runner, self.attempt, self.plumbing = runner, attempt, plumbing
        self.reason = None
        self.rows = []
        self._lock = threading.Lock()
        self._next_agents = self._next_physics = runner.seams.now()
        self._stop = threading.Event()
        self._thread = None
        self.segment = None
        self.teardown_error = None

    def check(self, *, watch=True):
        if self.teardown_error:
            raise self.teardown_error
        if self.runner.stop:
            raise Interrupted(self.runner.stop)
        if self.reason:
            raise Interrupted(self.reason)
        if self.runner.seams.now() >= self.runner.deadline:
            raise Deadline('deadline')
        if watch:
            self.tick()
        if self.teardown_error:
            raise self.teardown_error
        if self.reason:
            raise Interrupted(self.reason)

    def wait(self, seconds, *, watch=True):
        until = self.runner.seams.now()+max(0., seconds)
        while self.runner.seams.now() < until:
            self.check(watch=watch)
            self.runner.seams.sleep(min(.25, max(0., until-self.runner.seams.now())))
        self.check(watch=watch)

    def tick(self):
        with self._lock:
            now = self.runner.seams.now()
            if now >= self._next_physics:
                try:
                    reading = self.runner.seams.watch(self.attempt)
                except TeardownBlocked as exc:
                    self.teardown_error = exc
                    return
                except Exception as e:
                    reading = {'error': f'{type(e).__name__}: {e}'}
                row = {'kind': self.runner.kind, 'stamp': self.runner.stamp(), 'physics': reading,
                       'segment': self.segment}
                self.rows.append(row)
                append(self.attempt / 'watch.jsonl', row)
                self._next_physics = now+10*self.runner.scale
            if now >= self._next_agents:
                try:
                    reading = self.runner.seams.census(self.attempt)
                except TeardownBlocked as exc:
                    self.teardown_error = exc
                    return
                except Exception as e:
                    reading = {'clean': False, 'error': str(e)}
                row = {'kind': self.runner.kind, 'stamp': self.runner.stamp(), 'agents': reading,
                       'segment': self.segment}
                self.rows.append(row)
                append(self.attempt / 'watch.jsonl', row)
                if not reading.get('clean') and not self.plumbing:
                    self.reason = 'agent'
                    self.runner.last_agent = now
                self._next_agents = now+30*self.runner.scale

    def start(self):
        self.tick()
        def loop():
            while not self._stop.wait(min(1., max(.01, self.runner.scale))):
                self.tick()
                if self.reason or self.runner.stop:
                    try:
                        self.runner.seams.cleanup()
                    except TeardownBlocked as exc:
                        self.teardown_error = exc
                    return
        self._thread = threading.Thread(target=loop, name='quiet-kit-watcher', daemon=True)
        self._thread.start()

    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=15)
            if self._thread.is_alive():
                raise RuntimeError('watcher did not stop')


class Runner:
    def __init__(self, repo: Path, root: Path, model_python: str, seams: Seams,
                 *, deadline_hours=48., scale=1., plans=PLANS, emit=print):
        self.repo, self.root = fence(repo), fence(root)
        self.model_python = executable(model_python)
        self.seams, self.scale, self.plans, self.emit = seams, scale, plans, emit
        self.deadline_hours = deadline_hours
        self.started = seams.now()
        self.deadline = self.started+deadline_hours*3600
        self.last_agent = None
        self.stop = None
        self.current = None
        self.active_attempt = None
        self.clock_attempt = None
        self.clock_source_attempt = None
        self.clock_handle = None
        self.clock_info = None
        self.kind = 'measurement'
        self.network = None
        self.caffeinate = None
        self._previous_signals = {}
        self._last_status = None
        self.job_id = uuid.uuid4().hex
        self.recovery = []
        self.director_actions = []
        self.seams.bind_cancel(lambda: bool(self.stop) or self.seams.now() >= self.deadline)

    def stamp(self):
        return {'utc': self.seams.utc(), 'monotonic_raw_ns': self.seams.raw_ns()}

    def state(self, state, **fields):
        row = {'schema': 'joulewise.quiet_kit.status.v1', 'kind': self.kind,
               'state': state, 'current_test': self.current, 'current_wait': None,
               'since': self.stamp(), 'updated_at': self.stamp(), **fields}
        if self.director_actions:
            row['director_actions'] = self.director_actions
            row['director_action'] = ('root_sampler_orphan' if any(
                a['director_action'] == 'root_sampler_orphan' for a in self.director_actions)
                else self.director_actions[0]['director_action'])
        keys = ('state', 'current_test', 'current_wait')
        if self._last_status and all(row.get(k) == self._last_status.get(k) for k in keys):
            row['since'] = self._last_status['since']
        self._last_status = row
        if self.kind == 'measurement':
            atomic_json(self.root / 'STATUS.json', row)
        self.emit(f'{row["since"]["utc"]} {state} {self.current or ""}')

    def record_teardown_block(self, exc):
        fresh = [a for a in exc.actions if a not in self.director_actions]
        if not fresh:
            return
        self.director_actions.extend(fresh)
        reason = ('root_sampler_orphan' if any(a['director_action'] == 'root_sampler_orphan'
                                              for a in self.director_actions)
                  else 'owned_process_group_unverifiable')
        row = {'kind': self.kind, 'event': 'director_action', 'job_id': self.job_id,
               'stamp': self.stamp(), 'reason': reason, 'director_action': reason, 'director_actions': fresh,
               'process_groups': exc.groups}
        append(self.root/'journal.jsonl', row)
        if self.active_attempt:
            info = read_json(self.active_attempt/'attempt.json', {})
            atomic_json(self.active_attempt/'attempt.json', {**info, 'state': 'incomplete',
                'reason': reason, 'director_action': reason, 'director_actions': self.director_actions,
                'process_groups': exc.groups, 'end': self.stamp()})
        self.state('director_action_required', reason=reason, process_groups=exc.groups)
        self.emit('DIRECTOR ACTION REQUIRED: '+reason+' '+str(fresh))

    def cleanup_test(self):
        try:
            return self.seams.cleanup()
        except TeardownBlocked as exc:
            self.record_teardown_block(exc)
            return exc.groups

    def new_attempt(self, test_id, root=None):
        directory = fence((root or self.root / test_id) / 'attempts')
        mkdir(directory)
        numbers = [int(p.name) for p in children(directory) if p.name.isdigit()]
        n = max(numbers, default=0)+1
        path = fence(directory / str(n))
        path.mkdir()  # exclusive; never reused, even after a crash
        atomic_json(path / 'attempt.json', {'kind': self.kind, 'test_id': test_id,
                    'attempt': n, 'job_id': self.job_id, 'state': 'started', 'start': self.stamp()})
        return path

    def _signal(self, signum, _frame):
        self.stop = signal.Signals(signum).name
        # Never wait/reap in a signal callback: it can interrupt Popen while
        # its waitpid lock is held. Bounded probe/collector waits observe this
        # flag, then normal exception teardown kills and proves the groups gone.

    def _signals(self):
        if threading.current_thread() is threading.main_thread():
            for sig in (signal.SIGTERM, signal.SIGINT):
                self._previous_signals[sig] = signal.signal(sig, self._signal)

    def _restore_signals(self):
        for sig, handler in self._previous_signals.items():
            signal.signal(sig, handler)

    def wait(self, hazard, reading, reasons, seconds, attempt, preflight):
        start = self.stamp()
        self.state('waiting', current_wait=hazard, reading=reading, seconds=seconds)
        try:
            Control(self, attempt).wait(seconds*self.scale, watch=False)
        finally:
            row = {'kind': self.kind, 'hazard': hazard, 'reading': reading,
                   'job_id': self.job_id, 'verdict_reasons': list(reasons), 'start': start, 'end': self.stamp()}
            append(self.root / 'journal.jsonl', row)
            preflight['waits'].append(row)
            atomic_json(attempt / 'preflight.json', preflight)

    def clean_agents(self, attempt, preflight, *, initial=False):
        clean_since = None
        seen = False
        while True:
            Control(self, attempt).check(watch=False)
            row = self.seams.census(attempt)
            preflight['census'].append({'stamp': self.stamp(), **row})
            now = self.seams.now()
            if not row.get('clean'):
                seen = True
                self.last_agent = now
                clean_since = None
                self.wait('agents', row, [row.get('detail', 'agent census not clean')], 30, attempt, preflight)
                continue
            if clean_since is None:
                clean_since = now
            if not initial and self.last_agent is None:
                return seen
            if now-clean_since >= 600*self.scale:
                self.last_agent = None
                return seen
            self.wait('agent_handoff', row, ['10 minutes continuously clean required'], 30, attempt, preflight)

    def preflight(self, plan, attempt, *, record_only=False):
        record = {'kind': self.kind, 'record_only': record_only, 'reads': [], 'waits': [],
                  'census': [], 'flags': [], 'shortened_probe_seconds': 20 if record_only else None}
        unmeasured = {}
        waits = {'battery': 60, 'thermal': 60, 'disk': 600, 'contention': 60,
                 'instrument': 300, 'clock': 600}
        cycle = 0
        try:
            while True:
                Control(self, attempt).check(watch=False)
                cycle += 1
                self.state('preflight', cycle=cycle)
                if record_only:
                    census = self.seams.census(attempt)
                    record['census'].append(census)
                    if not census.get('clean'):
                        record['flags'].append({'reason': 'agents would wait', 'reading': census})
                else:
                    self.clean_agents(attempt, record)
                retry = False
                for name in ('battery', 'thermal', 'disk', 'contention', 'instrument', 'clock'):
                    Control(self, attempt).check(watch=False)
                    self.state('preflight', cycle=cycle, current_wait=name+'_probe')
                    probe_dir = mkdir(attempt / 'preflight-raw' / str(cycle) / name)
                    try:
                        reading = self.seams.probe(name, probe_dir, {
                            'record_only': record_only, 'duration_s': 20 if record_only else
                                {'contention': 180, 'instrument': 60, 'clock': 60}.get(name, 0),
                            'tree_roots': [os.getpid()], 'planned_bytes': plan.planned_bytes,
                            'archive': str(self.root), 'deadline': self.deadline,
                            'cancel': lambda: bool(self.stop) or self.seams.now() >= self.deadline})
                    except TeardownBlocked:
                        raise
                    except (Interrupted, Deadline) as exc:
                        if self.stop:
                            # Instrument callbacks share a cancellation seam;
                            # a signal remains a stop, never a deadline wake.
                            raise Interrupted(self.stop) from exc
                        raise
                    except Exception as exc:
                        reading = {'measurement': {'error': f'{type(exc).__name__}: {exc}'},
                                   'verdict': {'status': 'UNMEASURED', 'reasons': [str(exc)]}}
                    record['reads'].append({'module': name, 'stamp': self.stamp(), **reading})
                    status = reading.get('verdict', {}).get('status', 'UNMEASURED')
                    reasons = reading.get('verdict', {}).get('reasons', ['probe failed'])
                    unmeasured[name] = unmeasured.get(name, 0)+1 if status == 'UNMEASURED' else 0
                    if status != 'PASS':
                        if record_only:
                            record['flags'].append({'reason': f'{name} would wait', 'verdict': reading.get('verdict')})
                        elif status == 'UNMEASURED' and name != 'instrument' and unmeasured[name] >= 3:
                            record['flags'].append({'reason': f'{name} unmeasured on 3 consecutive probes',
                                                    'verdict': reading.get('verdict')})
                        else:
                            self.wait(name, reading, reasons, waits[name], attempt, record)
                            retry = True
                            break
                if retry:
                    continue
                # A census at the end covers agents appearing during the long
                # dwell/probes, before any load can begin.
                if not record_only:
                    if self.clean_agents(attempt, record):
                        continue  # remeasure physics after the agent clears
                record['diagnostics_start'] = self.seams.observe(attempt)
                return record
        finally:
            atomic_json(attempt / 'preflight.json', record)

    def _flags(self, preflight, watched, before, after):
        flags = list(preflight.get('flags', []))
        for row in watched:
            if row.get('error'):
                flags.append({'reason': 'watch journal malformed', 'reading': row})
            values = row.get('physics', {})
            if values.get('thermal_level', 0) not in (None, 0):
                flags.append({'reason': 'thermal pressure during test', 'stamp': row['stamp'], 'reading': values})
            if values.get('battery_current_ma') is not None and abs(values['battery_current_ma']) > 200:
                flags.append({'reason': 'battery current over 200 mA during test', 'stamp': row['stamp'], 'reading': values})
            if values.get('error'):
                flags.append({'reason': 'watch probe unmeasured', 'stamp': row['stamp'], 'reading': values})
        if before.get('hid_idle_ns') is not None and after.get('hid_idle_ns') is not None and after['hid_idle_ns'] < before['hid_idle_ns']:
            flags.append({'reason': 'HID idle decreased; input during test'})
        if before.get('display_state') is not None and after.get('display_state') is not None and after.get('display_state') != before.get('display_state'):
            flags.append({'reason': 'display power state changed during test'})
        for endpoint, observed in (('start', before), ('end', after)):
            if observed.get('display_state') is None:
                flags.append({'reason': 'display power state unmeasured', 'endpoint': endpoint,
                              'detail': observed.get('display_state_reason')})
        return flags

    def publish(self, plan, attempt, *, target=None):
        from .readers import read_attempt, flag_segments
        data = read_attempt(attempt)
        preflight = read_json(attempt / 'preflight.json', {})
        conditions = read_json(attempt / 'conditions.json', {})
        collection = read_json(attempt/'collection.json', {})
        from .readers import relative
        watch = read_json_lines(relative(attempt, collection.get('watch_file', 'watch.jsonl')))
        data = flag_segments(data, watch)
        fn = analysis.FUNCTIONS[plan.test_id]
        measured = fn(data)
        clean_data = {**data, 'segments': [s for s in data.get('segments', []) if not s.get('hazard_flags')],
                      'runs': [r for r in data.get('runs', []) if not r.get('hazard_flags')],
                      'captures': [c for c in data.get('captures', []) if not c.get('hazard_flags')],
                      'clock': data.get('clock_clean', data.get('clock', []))}
        without = fn(clean_data)
        attempt_info = read_json(attempt / 'attempt.json', {})
        collection = read_json(attempt / 'collection.json', {})
        reason = collection.get('incomplete_reason')
        if plan.test_id == 'm2b-short-baseline' and measured.get('incomplete_reason'):
            reason = measured['incomplete_reason']
        if not conditions.get('end_stamp'):
            reason = 'collection_not_finished'
        if attempt_info.get('failure_stage') == 'collection':
            reason = attempt_info.get('reason', 'collection did not finish')
        if attempt_info.get('state') == 'interrupted':
            reason = 'interrupted: ' + attempt_info.get('reason', 'unknown')
        if plan.meter and data.get('meter_present') is not True:
            reason = 'meter_absent'
        if plan.test_id == 'm3-clock-rate' and measured.get('span_s', 0) < 10800*self.scale:
            reason = 'clock_span_under_3h'
        before, after = conditions.get('start', {}), conditions.get('end', {})
        agents = {}
        for name in ('mediaanalysisd', 'photoanalysisd'):
            a, b = before.get('analysis_agents', {}).get(name, {}), after.get('analysis_agents', {}).get(name, {})
            agents[name] = {'start': a, 'end': b,
                           'cpu_time_delta_s': b.get('cpu_seconds', 0)-a.get('cpu_seconds', 0)
                               if a.get('identities') == b.get('identities') else None,
                           'identity_continuous': a.get('identities') == b.get('identities')}
        flags = self._flags(preflight, watch, before, after) + data.get('flags', [])
        for name, reading in (('network-time OFF action', self.network or conditions.get('network_time_setter')),
                              ('no-sleep assertion', self.caffeinate or conditions.get('caffeinate')),
                              ('clock logger', self.clock_info or conditions.get('clock_logger'))):
            if reading and (reading.get('error') or reading.get('returncode') not in (0, None)):
                flags.append({'reason': name+' failed', 'reading': reading})
        for name, values in agents.items():
            if values['start'].get('present') or values['end'].get('present'):
                flags.append({'reason': name+' present at an endpoint', 'reading': values})
            if not values['identity_continuous']:
                flags.append({'reason': name+' CPU-time delta undefined after identity change'})
        if before.get('screensaver_present') or after.get('screensaver_present'):
            flags.append({'reason': 'screen saver present at an endpoint'})
        clock_step = plan.test_id == 'm3-clock-rate' and collection.get('clock_file') == 'clock-step.jsonl'
        if clock_step:
            if not fence(attempt/'conditions-step.json').exists():
                atomic_json(attempt/'conditions-step.json', conditions)
            if not fence(attempt/'collection-step.json').exists():
                atomic_json(attempt/'collection-step.json', collection)
        result = {'schema': 'joulewise.quiet_kit.result.v1', 'test_id': plan.test_id, 'kind': self.kind,
            'complete': reason is None, 'incomplete_reason': reason, 'attempt': int(attempt.name),
            'start': attempt_info.get('start'), 'end': conditions.get('end_stamp', self.stamp()),
            'measured': measured, 'without_flagged_segments': without,
            'flags': flags,
            'conditions': {'preflight': preflight, 'watcher_spans': watch, 'start': before, 'end': after,
                'clock_sources': read_json(relative(attempt, collection['clock_sources_file']), [])
                    if collection.get('clock_sources_file') else [],
                'job_waits': read_json_lines(relative(attempt, collection['job_waits_file']))
                    if collection.get('job_waits_file') else [],
                'analysis_agents': agents, 'network_time_setter': self.network or conditions.get('network_time_setter'),
                'display_sleep': conditions.get('display_sleep'), 'caffeinate': self.caffeinate or conditions.get('caffeinate'),
                'clock_logger': self.clock_info or conditions.get('clock_logger'),
                'battery_current_range_ma': numeric_range([r.get('physics', {}).get('battery_current_ma') for r in watch]),
                'thermal_levels': sorted({r['physics']['thermal_level'] for r in watch
                                          if r.get('physics', {}).get('thermal_level') is not None})},
            'raw': [{**r, 'kind': self.kind} for r in inventory(attempt) if not (clock_step and r['path'] in (
                    'clock.jsonl', 'children.jsonl', 'watch.jsonl', 'conditions.json', 'collection.json'))],
            'raw_relative_to': f'attempts/{attempt.name}',
            'code': read_json(attempt / 'code.json', {}),
            'analysis_function': f'{fn.__module__}.{fn.__name__}',
            'analysis_parameters': {'scale': self.scale, 'F_min_J': 'parameter; no block-5 outcome',
                                    'segment_plan': list(plan.segments)}}
        atomic_json(attempt / 'analysis.result.json', result)
        if plan.test_id == 'm3-clock-rate' and collection.get('clock_file') == 'clock-end.jsonl':
            atomic_json(attempt / 'analysis-end.result.json', result)
        if reason:
            atomic_json(attempt / 'attempt.json', {**attempt_info, 'state': 'incomplete', 'reason': reason})
            if self.kind == 'plumbing_check':
                destination = fence(target or self.root)
                atomic_json(destination/'result.json', result)
                atomic(destination/'summary.md', summary(result).encode())
            return result
        destination = fence(target or self.root / plan.test_id)
        # Persist everything else first; result and summary are the final two
        # writes. Remove no earlier complete result and never mutate raw files.
        atomic_json(attempt / 'attempt.json', {**attempt_info, 'state': 'complete'})
        atomic_json(destination / 'result.json', result)
        atomic(destination / 'summary.md', summary(result).encode())
        return result

    def test(self, plan, *, attempt=None, target=None, record_only=False):
        try:
            return self._test(plan, attempt=attempt, target=target, record_only=record_only)
        except TeardownBlocked as exc:
            self.record_teardown_block(exc)
            raise
        except (Interrupted, Deadline) as exc:
            if self.active_attempt:
                info = read_json(self.active_attempt/'attempt.json', {})
                if info.get('state') != 'interrupted':
                    groups = self.seams.cleanup()
                    atomic_json(self.active_attempt/'attempt.json', {**info, 'state': 'interrupted',
                                'reason': str(exc), 'end': self.stamp(), 'process_groups': groups})
            raise

    def _test(self, plan, *, attempt=None, target=None, record_only=False):
        self.current = plan.test_id
        attempt = attempt or self.new_attempt(plan.test_id, root=target)
        self.active_attempt = attempt
        if plan.ruling_required:
            reason = 'needs_ruling: ' + plan.ruling_required
            atomic_json(attempt/'attempt.json', {**read_json(attempt/'attempt.json', {}),
                        'state': 'incomplete', 'reason': reason})
            return {'complete': False, 'incomplete_reason': reason}
        preflight = self.preflight(plan, attempt, record_only=record_only)
        Control(self, attempt).check(watch=False)
        before = preflight['diagnostics_start']
        if plan.test_id == 'm3-clock-rate' and not record_only:
            before = read_json(attempt/'job-start-conditions.json', before)
        use_model = bool(plan.model_runs or plan.captures or any(s.get('kind') in ('gpu', 'mixed') for s in plan.segments))
        atomic_json(attempt / 'code.json', {**self.seams.code(use_model), 'kind': self.kind})
        Control(self, attempt).check(watch=False)
        display = None
        if not record_only:
            display = self.seams.action('display_sleep', attempt)
            if plan.test_id != 'm3-clock-rate':
                # The deliberate sleep request is outside the test endpoints;
                # a later wake is a change in the measured conditions.
                before = self.seams.observe(attempt)
        control = Control(self, attempt, plumbing=record_only)
        conditions = {'kind': self.kind, 'start': before, 'network_time_setter': self.network,
                      'caffeinate': self.caffeinate, 'clock_logger': self.clock_info, 'display_sleep': display}
        atomic_json(attempt / 'conditions.json', conditions)
        try:
            self.state('collecting', attempt=str(attempt))
            control.start()
            control.check()
            if plan.test_id == 'm3-clock-rate':
                # The child has already logged throughout M4/M5/M1/M2.
                if record_only:
                    handle = self.seams.clock_start(attempt, self.kind)
                    try:
                        control.wait(min(180., 10800*self.scale))
                    finally:
                        self.seams.clock_stop(handle)
                else:
                    while True:
                        series = analysis.m3({'clock': self._clock_rows()[0]})
                        if series['span_s'] >= 10800*self.scale:
                            break
                        if self.seams.now()-self.started >= 10800*self.scale:
                            break  # failed/gapped clock probe must not stall later tests
                        self.state('waiting', current_wait='clock_span', minimum_seconds=10800)
                        control.wait(10*self.scale)
                if record_only:
                    atomic(attempt/'clock-step.jsonl', read_bytes(attempt/'clock.jsonl'))
                else:
                    self._clock_snapshot(attempt, 'step')
                atomic_json(attempt / 'collection.json', {**read_json(attempt/'collection.json', {}),
                    'kind': self.kind, 'test_id': plan.test_id, 'clock_file': 'clock-step.jsonl',
                    'scale': self.scale, 'longest_sampler_s': self.longest_sampler(), 'segments': []})
                self._clock_watch_snapshot(attempt, 'step')
            else:
                self.seams.collect(plan, attempt, self.scale, control, self.kind)
            control.check()
            conditions.update(end=self.seams.observe(attempt), end_stamp=self.stamp())
            atomic_json(attempt / 'conditions.json', conditions)
            self.state('analyzing')
            return self.publish(plan, attempt, target=target)
        except (Interrupted, Deadline) as exc:
            gone = self.seams.cleanup()
            info = read_json(attempt / 'attempt.json', {})
            atomic_json(attempt / 'attempt.json', {**info, 'state': 'interrupted', 'reason': str(exc),
                                                  'process_groups': gone, 'end': self.stamp()})
            self.state('interrupted', reason=str(exc), process_groups=gone)
            raise
        except Exception as exc:
            if isinstance(exc, TeardownBlocked):
                raise
            if control.reason or self.stop:
                raise Interrupted(control.reason or self.stop) from exc
            if self.seams.now() >= self.deadline:
                raise Deadline('deadline') from exc
            gone = self.seams.cleanup()
            info = read_json(attempt / 'attempt.json', {})
            reason = f'{type(exc).__name__}: {exc}'
            atomic_json(attempt / 'attempt.json', {**info, 'state': 'incomplete', 'reason': reason,
                                                  'failure_stage': 'analysis' if conditions.get('end_stamp') else 'collection',
                                                  'process_groups': gone, 'end': self.stamp()})
            self.state('incomplete', reason=reason)
            return {'complete': False, 'incomplete_reason': reason}
        finally:
            control.close()

    def longest_sampler(self):
        spans = []
        for plan in self.plans:
            for p in children(self.root / plan.test_id / 'attempts'):
                doc = read_json(p / 'collection.json', {})
                spans += doc.get('sampler_spans_s', [])
        return max(spans, default=0.)

    def _clock_rows(self):
        rows, sources = [], []
        directories = [p for p in children(self.root/'m3-clock-rate/attempts') if p.name.isdigit() and p.is_dir()]
        for source in sorted(directories, key=lambda p:int(p.name)):
            info = read_json(source/'attempt.json', {})
            if info.get('test_id') != 'm3-clock-rate' or info.get('kind') != 'measurement':
                continue
            captured = read_json_lines(source/'clock.jsonl')
            if not captured:
                continue
            rows += [{**r, 'source_attempt': int(source.name), 'source_job_id': info.get('job_id')} for r in captured]
            sources.append({'attempt':int(source.name), 'job_id':info.get('job_id'), 'start':info.get('start'),
                'code':read_json(source/'code.json', {}),
                'job_start_conditions':read_json(source/'job-start-conditions.json', {}),
                'conditions':read_json(source/'conditions.json', {})})
        return rows, sources

    def _clock_snapshot(self, attempt, phase):
        import json
        rows, sources = self._clock_rows()
        filename = f'clock-{phase}.jsonl'
        atomic(attempt/filename, ''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows).encode())
        atomic_json(attempt/f'clock-sources-{phase}.json',sources)
        doc = read_json(attempt/'collection.json', {})
        atomic_json(attempt/'collection.json',{**doc,'clock_file':filename,
                    'clock_sources_file':f'clock-sources-{phase}.json'})

    def _clock_attempt_for_test(self):
        if read_json(self.clock_attempt/'attempt.json', {}).get('state') != 'started':
            self.clock_attempt = self.new_attempt('m3-clock-rate')
            for filename in ('code.json','job-start-conditions.json'):
                atomic(self.clock_attempt/filename, read_bytes(self.clock_source_attempt/filename))
        return self.clock_attempt

    def _clock_watch_snapshot(self, attempt, phase):
        import json
        job_id = read_json(attempt/'attempt.json', {}).get('job_id')
        doc = read_json(attempt/'collection.json', {})
        sources = read_json(attempt/doc['clock_sources_file'], []) if doc.get('clock_sources_file') else []
        job_ids = {source.get('job_id') for source in sources} or {job_id}
        rows = []
        for plan in self.plans:
            for source in children(self.root/plan.test_id/'attempts'):
                source_job = read_json(source/'attempt.json', {}).get('job_id')
                if source_job in job_ids:
                    rows += [{**r, 'source_job_id': source_job} for r in read_json_lines(source/'watch.jsonl')]
        if self.kind == 'plumbing_check':
            rows = read_json_lines(attempt/'watch.jsonl')
        rows.sort(key=lambda r: r.get('stamp', {}).get('monotonic_raw_ns', 0))
        path = attempt/f'job-watch-{phase}.jsonl'
        atomic(path, ''.join(json.dumps(r, sort_keys=True)+'\n' for r in rows).encode())
        doc = read_json(attempt/'collection.json', {})
        waits = [r for r in read_json_lines(self.root/'journal.jsonl') if r.get('job_id') in job_ids]
        wait_path = attempt/f'job-waits-{phase}.jsonl'
        atomic(wait_path, ''.join(json.dumps(r, sort_keys=True)+'\n' for r in waits).encode())
        atomic_json(attempt/'collection.json', {**doc, 'watch_file': path.name, 'job_waits_file': wait_path.name})

    def _final_clock(self):
        if self.clock_handle is not None:
            self.seams.clock_stop(self.clock_handle)
            self.clock_handle = None
        if self.clock_attempt and self.clock_source_attempt and fence(self.clock_source_attempt / 'clock.jsonl').exists():
            plan = BY_ID['m3-clock-rate']
            self._clock_snapshot(self.clock_attempt, 'end')
            doc = read_json(self.clock_attempt / 'collection.json', {})
            atomic_json(self.clock_attempt / 'collection.json', {**doc, 'kind': self.kind,
                        'test_id': plan.test_id, 'scale': self.scale,
                        'longest_sampler_s': self.longest_sampler(), 'segments': []})
            prior = read_json(self.clock_attempt / 'analysis.result.json')
            if prior:
                atomic_json(self.clock_attempt / 'analysis-step.result.json', prior)
            conditions = read_json(self.clock_attempt/'conditions.json', {})
            atomic_json(self.clock_attempt/'conditions.json', {**conditions, 'kind': self.kind,
                'start': read_json(self.clock_attempt/'job-start-conditions.json', conditions.get('start', {})),
                'end': self.seams.observe(self.clock_attempt), 'end_stamp': self.stamp()})
            self._clock_watch_snapshot(self.clock_attempt, 'end')
            self.publish(plan, self.clock_attempt)

    def finish(self):
        self.cleanup_test()
        if not self.director_actions:
            try:
                self._final_clock()
            except TeardownBlocked as exc:
                self.record_teardown_block(exc)
        done, incomplete = [], []
        for p in self.plans:
            if complete(self.root, p.test_id):
                done.append(p.test_id)
            else:
                attempts = [a for a in children(self.root / p.test_id / 'attempts') if a.name.isdigit()]
                last = read_json(max(attempts, key=lambda a: int(a.name)) / 'attempt.json', {}) if attempts else {}
                incomplete.append({'test_id': p.test_id, 'last_reason': last.get('reason',
                    'root_sampler_orphan' if any(a['director_action'] == 'root_sampler_orphan' for a in self.director_actions) else
                    'recovery_needs_director' if any(r.get('blocking') for r in self.recovery) else
                    'deadline before test' if self.seams.now() >= self.deadline else 'not started')})
        record = {'kind': self.kind, 'complete_tests': done, 'incomplete_tests': incomplete,
                  'wall_time_s': self.seams.now()-self.started, 'end_time': self.stamp(), 'recovery': self.recovery,
                  'director_actions': self.director_actions}
        atomic_json(self.root / 'DONE', record)
        self.current = None
        self.state('done', **record)
        wake = fence(self.root / 'WAKE_CMD')
        if wake.is_file() and not fence(self.root / 'WAKE_DONE').exists():
            content = read_bytes(wake).decode()
            if create_once(self.root / 'WAKE_DONE', (self.seams.utc()+'\n').encode()):
                self.seams.wake(content, fence(self.root / 'wake.log'))
        return 0

    def run(self):
        mkdir(self.root)
        with fence(self.root / '.lock').open('a+b') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                self.emit('quiet kit already running; exiting 0')
                return 0
            self.started = self.seams.now()
            self.deadline = self.started+self.deadline_hours*3600
            self._signals()
            self.state('starting')
            try:
                recovered = self.seams.recover(self.root)
            except Exception as exc:
                recovered = [{'blocking': True, 'reason': 'restart recovery failed', 'error': str(exc)}]
            self.recovery = recovered
            for row in recovered:
                if row.get('director_actions'):
                    self.record_teardown_block(TeardownBlocked(row.get('groups', [row])))
            if self.stop:
                self.state('stopped', reason=self.stop)
                self._restore_signals()
                return 128+int(getattr(signal, self.stop, signal.SIGTERM))
            if recovered:
                atomic_json(self.root/'recovery.json', {'kind': self.kind, 'outcomes': recovered})
            if any(row.get('blocking') for row in recovered):
                self.state('recovery_needs_director', outcomes=recovered)
                try:
                    return self.finish()
                finally:
                    self._restore_signals()
            if all(complete(self.root, p.test_id) for p in self.plans):
                try:
                    return self.finish()
                finally:
                    self._restore_signals()
            try:
                self.caffeinate = self.seams.action('caffeinate', self.root)
                self.network = self.seams.action('network_time_off', self.root)
                if any(p.test_id == 'm3-clock-rate' for p in self.plans):
                    self.clock_attempt = self.new_attempt('m3-clock-rate')
                    self.clock_source_attempt = self.clock_attempt
                    atomic_json(self.clock_attempt/'job-start-conditions.json', self.seams.observe(self.clock_attempt))
                    atomic_json(self.clock_attempt / 'code.json', {**self.seams.code(False), 'kind': self.kind})
                    try:
                        self.clock_handle = self.seams.clock_start(self.clock_attempt, self.kind)
                        self.clock_info = {'pid': getattr(self.clock_handle, 'pid', None), 'started': True}
                    except OSError as exc:
                        self.clock_info = {'started': False, 'error': str(exc)}
                        atomic_json(self.clock_attempt/'clock-error.json', self.clock_info)
                handoff = self.new_attempt('_handoff')
                record = {'kind': self.kind, 'reads': [], 'waits': [], 'census': [], 'flags': []}
                self.clean_agents(handoff, record, initial=True)
                atomic_json(handoff / 'preflight.json', record)
                counts = {}
                for pass_number in (1, 2):
                    for plan in self.plans:
                        if complete(self.root, plan.test_id):
                            continue
                        while counts.get(plan.test_id, 0) < 3:
                            Control(self, self.root).check(watch=False)
                            counts[plan.test_id] = counts.get(plan.test_id, 0)+1
                            try:
                                result = self.test(plan, attempt=self._clock_attempt_for_test() if plan.test_id == 'm3-clock-rate' else None)
                            except Interrupted as exc:
                                if str(exc) != 'agent':
                                    raise
                                # Fresh preflight applies the 10-minute clean
                                # handoff rule before the retry.
                                continue
                            break  # incomplete non-agent result gets later pass
                return self.finish()
            except TeardownBlocked as exc:
                self.record_teardown_block(exc)
                return self.finish()
            except Deadline:
                return self.finish()
            except Interrupted as exc:
                self.state('stopped', reason=str(exc))
                return 128+int(getattr(signal, self.stop, signal.SIGTERM)) if self.stop else 130
            finally:
                if self.clock_handle is not None:
                    try:
                        self.seams.clock_stop(self.clock_handle)
                    except TeardownBlocked as exc:
                        self.record_teardown_block(exc)
                    self.clock_handle = None
                self.cleanup_test()
                try:
                    self.seams.action('stop_caffeinate', self.root)
                except TeardownBlocked as exc:
                    self.record_teardown_block(exc)
                self._restore_signals()

    def reanalyze(self, test_id):
        plan = BY_ID[test_id]
        attempts = [p for p in children(self.root / test_id / 'attempts')
                    if p.name.isdigit() and fence(p / 'collection.json').is_file()]
        if not attempts:
            self.emit('no captured attempt to reanalyze')
            return 1
        attempt = max(attempts, key=lambda a: int(a.name))
        meta = read_json(attempt / 'collection.json', {})
        self.kind = meta.get('kind', 'measurement')
        self.scale = meta.get('scale', self.scale)
        result = self.publish(plan, attempt)
        self.emit(f'{test_id}: recomputed from attempt {attempt.name}')
        return 0 if result['complete'] else 1

    def plumbing(self, test_id, scale=None):
        self.kind = 'plumbing_check'
        plan = BY_ID[test_id]
        # Default m5: 20+20+20 s shortened probes, segments ~180 s, overhead.
        self.scale = scale if scale is not None else 180/(10800 if test_id == 'm3-clock-rate' else max(plan.estimate_s-300, 1))
        self.deadline = self.seams.now()+570
        stamp = self.seams.utc().replace(':', '').replace('+', '_')
        parent = mkdir(self.root / '_plumbing' / stamp)
        # Journal is local too. No STATUS, DONE or wake state touches archive.
        self.root = parent
        atomic_json(parent / 'kind.json', {'kind': self.kind, 'test_id': test_id,
                                          'scale': self.scale, 'measurement': False})
        self._signals()
        try:
            result = self.test(plan, target=parent, record_only=True)
            self.cleanup_test()
            if self.director_actions:
                return 1
            return 0 if result['complete'] else 1
        except TeardownBlocked as exc:
            self.record_teardown_block(exc)
            return 1
        except (Deadline, Interrupted) as exc:
            if self.active_attempt:
                attempt = self.active_attempt
                doc = read_json(attempt/'collection.json', {})
                atomic_json(attempt/'collection.json', {**doc, 'kind': self.kind, 'scale': self.scale,
                            'test_id': test_id, 'incomplete_reason': str(exc)})
                conditions = read_json(attempt/'conditions.json', {})
                atomic_json(attempt/'conditions.json', {**conditions, 'kind': self.kind,
                            'end': self.seams.observe(attempt), 'end_stamp': self.stamp()})
                self.publish(plan, attempt, target=parent)
            return 1
        finally:
            self.cleanup_test()
            self._restore_signals()


def read_json_lines(path):
    import json
    try:
        raw = read_bytes(path)
    except FileNotFoundError:
        return []
    rows = []
    for line in raw.splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({'error': 'truncated/malformed journal line'})
    return rows


def numeric_range(values):
    numbers = [v for v in values if isinstance(v, (int, float))]
    return [min(numbers), max(numbers)] if numbers else None


def summary(result):
    """One paragraph; M15 reports drift/ratios, never absolute workload energy."""
    measured = result['measured']
    numbers = []
    units = {'W':'watts', 'J':'joules', 'ms':'milliseconds', 'ppm':'parts per million',
             'CPU-s/s':'processor seconds per elapsed second',
             'W / (CPU-s/s)':'watts per processor second per elapsed second',
             '%':'percent', 'fraction':'fraction', 'ratio':'ratio', 'W/W':'watts per watt'}
    def label(name):
        tokens = name.replace('_',' ').split()
        words = {'gpu':'graphics processor', 'cpu':'processor', 'sd':'standard deviation',
                 'p95':'95th percentile', 'R':'reference workload',
                 'A':'1.7-billion-parameter workload', 'B':'8-billion-parameter workload'}
        return ' '.join(words.get(t,t) for t in tokens)
    def walk(value, name=''):
        if isinstance(value, dict):
            if 'value' in value and 'unit' in value:
                if isinstance(value['value'], (int, float)):
                    uncertainty = value.get('uncertainty', {})
                    uv = uncertainty.get('value')
                    utext = f'; {uncertainty.get("kind")} {uv}' if uv is not None else '; uncertainty undefined'
                    numbers.append(f'{label(name)}: {value["value"]:.6g} {units.get(value["unit"], value["unit"])}{utext}')
            else:
                for key, v in value.items():
                    if key not in ('run_table', 'captures', 'offsets', 'quiet_ordered_pairs', 'quiet_disturbed_ordered_pairs'):
                        walk(v, (name+' '+key).strip())
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, f'{name} {i+1}')
    walk(measured)
    methods = {'m1': 'the frozen pulse protocol and the shared interval detector',
               'm2': 'five ordinary, long, long, ordinary quads through the unchanged single-run path',
               'm2b': 'five ordinary, short, short, ordinary quads through the single-run path; '
                      'the short arm changes only sampling.idle_seconds to 50.0',
               'm3': 'a job-wide bracketed real-time and raw-monotonic clock series',
               'm4': 'bracketed processor loads and phase-length bursts, with true child CPU time',
               'm5': 'processor-only and graphics loads bracketed by idle power',
               'm9': 'query-only readings from two time servers with a linear trend removed',
               'm10': 'steady rail and input-meter levels with and without battery activity',
               'm13': 'frozen pulse trains and independent input-meter half-amplitude edges',
               'm14': 'input-meter and rail steps bracketed by idle baselines',
               'm15': 'start and end reference, 1.7-billion and 8-billion workload blocks around a 90-minute soak'}
    prefix = result['test_id'].split('-')[0]
    flags = len(result.get('flags', []))
    conditions = result.get('conditions', {})
    current_range = conditions.get('battery_current_range_ma')
    current_text = (f'Battery current ranged from {current_range[0]:g} to {current_range[1]:g} milliamperes'
                    if current_range else 'Battery current was unmeasured')
    thermal_text = ', '.join(str(v) for v in conditions.get('thermal_levels', [])) or 'unmeasured'
    return (f'This {result["kind"].replace("_", " ")} measured {result["test_id"]} using {methods[prefix]}. '
            + ('; '.join(numbers) if numbers else 'The requested quantities are undefined from the available observations')
            + f'. {current_text}; thermal pressure levels were {thermal_text}. '
            + f'The preflight, watcher and endpoint diagnostics carry {flags} condition flags; '
            'results including all observations and omitting flagged segments are retained. '
            'This is a non-claim calibration measurement; it establishes no registration, seal, instrument accuracy, '
            'or claim acceptance threshold.\n')
