"""In-process hardware fakes; no fixture process can outlive a desk test."""
from __future__ import annotations

import json
from pathlib import Path

from joulewise.quiet_kit.paths import append, atomic_json, read_json
from joulewise.quiet_kit.runner import Seams, Interrupted
from .fixtures import EPOCH, RAW, power_attempt, synthetic_capture, capture_meter_stream


class FakeHardware:
    def __init__(self, *, scale=.01):
        self.time = 0.
        self.scale = scale
        self.collected = []
        self.actions = []
        self.wakes = []
        self.clock = None
        self.clock_next = 0.
        self.probes = []
        self.census_calls = 0
        self.dirty_census_calls = set()
        self.bad_probes = {}
        self.interrupt_test = None
        self.agent_in_test = None
        self.control = None
        self.meter_present = True
        self.cleanup_calls = 0
        self._capture = None

    def now(self):
        return self.time

    def raw_ns(self):
        return round((RAW+self.time)*1e9)

    def utc(self):
        return f'2026-10-14T00:00:{self.time:09.6f}+00:00'

    def sleep(self, seconds):
        self.time += seconds
        self.log_clock()

    def log_clock(self):
        if self.clock is None:
            return
        while self.clock_next <= self.time:
            raw_ns = round((RAW+self.clock_next)*1e9)
            append(self.clock/'clock.jsonl', {'kind': 'measurement', 'boot_session_uuid': 'fake-boot',
                'anchor': {'monotonic_raw_ns': raw_ns, 'realtime_ns': round(EPOCH*1e9)+raw_ns+round(2.72e-6*raw_ns),
                           'read_skew_ns': 100}, 'frequency': {'frequency_ppm': 2.72}})
            self.clock_next += max(.1, 10*self.scale)

    def census(self, directory):
        self.census_calls += 1
        dirty = self.census_calls in self.dirty_census_calls
        if self.control and self.agent_in_test and self.control.runner.current == self.agent_in_test:
            dirty = True
            self.agent_in_test = None
        return {'clean': not dirty, 'stdout': '4242 codex' if dirty else '', 'detail': 'agent present' if dirty else 'clean'}

    def probe(self, name, directory, parameters):
        self.probes.append((name, parameters['duration_s'], parameters['record_only']))
        statuses = self.bad_probes.get(name, [])
        status = statuses.pop(0) if statuses else 'PASS'
        return {'measurement': {'values': {'battery_current_ma': 250 if status == 'REFUSE' else 0}},
                'verdict': {'status': status, 'reasons': ['measured hazard'] if status != 'PASS' else []}}

    def observe(self, directory):
        return {'analysis_agents': {'mediaanalysisd': {'present': False, 'cpu_seconds': 0, 'identities': []},
                                    'photoanalysisd': {'present': False, 'cpu_seconds': 0, 'identities': []}},
                'hid_idle_ns': round((100+self.time)*1e9), 'display_state': 0, 'screensaver_present': False,
                'meter_present': self.meter_present, 'os_build': 'fake-build', 'boot_session_uuid': 'fake-boot'}

    def watch(self, directory):
        return {'thermal_level': 0, 'battery_current_ma': 0}

    def code(self, model):
        return {'git_commit': 'fake-commit', 'dirty': False, 'python': '/opt/homebrew/bin/python3.13',
                'model_python': '/fake/model-python', 'mlx_versions': {'mlx': 'fake'} if model else {}}

    def action(self, name, directory):
        self.actions.append(name)
        return {'action': name, 'returncode': 0}

    def clock_start(self, directory, kind):
        self.clock = directory
        self.clock_next = self.time
        self.log_clock()
        return directory

    def clock_stop(self, handle):
        self.log_clock()
        self.clock = None

    def cleanup(self):
        self.cleanup_calls += 1
        return [{'pgid': 'in-process fake; no child', 'gone': True}]

    def wake(self, content, logfile):
        self.wakes.append(content)

    def collect(self, plan, attempt, scale, control, kind):
        self.collected.append(plan.test_id)
        self.control = control
        try:
            if self.agent_in_test == plan.test_id:
                control.wait(31*scale)
            if self.interrupt_test == plan.test_id:
                self.interrupt_test = None
                control.runner._signal(__import__('signal').SIGTERM, None)
                control.check()
            control.tick()
            control.check()
            if plan.test_id == 'm9-time-server':
                for q in range(10):
                    for server, offset in [('time.apple.com', .012), ('time.cloudflare.com', .010)]:
                        append(attempt/'sntp.jsonl', {'query': q, 'server': server, 'time_s': q*60.,
                            'stdout': f'+{offset:.6f} +/- 0.0001 {server}', 'offset_s': offset})
                atomic_json(attempt/'collection.json', {'kind':kind,'test_id':plan.test_id,'queries_file':'sntp.jsonl'})
            elif plan.captures:
                if self._capture is None:
                    self._capture = synthetic_capture()
                raw, events, anchor, protocol = self._capture
                captures = []
                for i, s in enumerate(plan.segments):
                    d = attempt/f'capture-{i:03d}'
                    (d/'raw').mkdir(parents=True)
                    (d/'raw/powermetrics.plist').write_bytes(raw)
                    (d/'events.jsonl').write_bytes(events)
                    atomic_json(d/'raw/sampler.json', {'clock_anchor': anchor,
                        'start': {'epoch_s': EPOCH, 'raw_s': RAW}})
                    atomic_json(d/'capture.json', {'protocol_id': protocol, 'scale': 1.,
                        'cadence_median_ms': 248 if s.get('condition') == 'utility' else 100})
                    captures.append({**s, 'id':d.name, 'directory':d.name})
                atomic_json(attempt/'collection.json', {'kind':kind,'test_id':plan.test_id,'captures':captures,
                    'meter_file': 'meter.jsonl' if plan.meter else None, 'sampler_spans_s':[200.]})
                if plan.meter:
                    from .fixtures import meter_stream
                    (attempt/'meter.jsonl').write_bytes(capture_meter_stream(events))
            elif plan.model_runs:
                runs = []
                for i, s in enumerate(plan.segments):
                    if s['kind'] != 'model':
                        continue
                    run_id = f'qk-{i}'
                    directory = attempt/'runs'/run_id
                    directory.mkdir(parents=True)
                    w = s['workload']
                    energy = {'R':10.,'A':20.,'B':40.}[w]
                    energy += .3 if s.get('arm') == 'L' or s.get('block') == 'end' else 0
                    atomic_json(directory/'summary_metrics.json', {'status':'succeeded', 'phase_energy_j':
                        {'prefill':energy, 'decode':2*energy}, 'ttft_s':1., 'decode_latency_s':149., 'throughput_tokens_s':24.})
                    runs.append({**s,'id':run_id,'bundle':f'runs/{run_id}'})
                atomic_json(attempt/'collection.json', {'kind':kind,'test_id':plan.test_id,'runs':runs})
            else:
                segments = []
                for spec in plan.segments:
                    duration = 20. if spec['kind'] == 'burst' else 2.
                    duty = spec.get('duty', 0.)
                    power = .05 + (5*duty if spec['kind'] in ('cpu', 'mixed') else 0) + (10*duty if spec['kind'] in ('gpu', 'mixed') else 0)
                    segments.append({**spec, 'duration_s': duration, 'power': power,
                        'gpu': 10*duty if spec['kind'] in ('gpu', 'mixed') else 0.,
                        'cpu_seconds': duration*duty, 'meter_power': 28+power})
                power_attempt(attempt, segments, meter=plan.meter, kind=kind)
                doc = read_json(attempt/'collection.json')
                doc['test_id'] = plan.test_id
                atomic_json(attempt/'collection.json',doc)
            if plan.meter and not self.meter_present:
                (attempt/'meter.jsonl').write_text('{"k":"h","status":"absent"}\n')
            control.wait((plan.estimate_s-300)*scale)
        finally:
            self.control = None

    def seams(self):
        return Seams(self.census, self.probe, self.observe, self.watch, self.collect,
            self.clock_start, self.clock_stop, self.action, self.wake, self.code,
            now=self.now, raw_ns=self.raw_ns, utc=self.utc, sleep=self.sleep, cleanup=self.cleanup)
