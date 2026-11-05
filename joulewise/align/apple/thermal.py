"""Opt-in ALIGN thermal gates, fixed-token holds and auditable exclusion clocks.

Council FINAL-DESIGN §2.6. No hardware is opened on import. The status feed is
an explicit observer capability: absent OS/PM evidence never means Nominal.
"""
from __future__ import annotations

from collections.abc import Mapping
from contextlib import nullcontext
import json
import math
from statistics import median
import threading
from types import GeneratorType

from joulewise.align.apple.sampler import monotonic_ns, _stamp_record
from joulewise.align.apple.budget import DeadmanExpired
from joulewise.clock import SystemClock
from joulewise.align.apple import smc
from joulewise.hazards import temperature
from joulewise.interfaces import RuntimeEvent

NS = 1_000_000_000


def validate_policy(value):
    required = {'sensors', 'delta_fast_c', 'delta_slow_c', 'turn_cap_s', 'per_turn', 'heavy', 'chunk_tokens'}
    if not isinstance(value, Mapping) or not required <= value.keys() or set(value) - required - {'window_reference'}:
        raise ValueError('thermal policy has missing or unknown fields')
    policy = dict(value)
    policy['sensors'] = temperature.validate_policy(policy['sensors'])
    for name in ('delta_fast_c', 'delta_slow_c', 'turn_cap_s'):
        v = policy[name]
        if type(v) not in (int, float) or not math.isfinite(v) or v <= 0:
            raise ValueError(f'thermal.{name} must be finite and positive')
    if policy['turn_cap_s'] > 300:
        raise ValueError('thermal.turn_cap_s exceeds 300')
    for name in ('per_turn', 'heavy'):
        if type(policy[name]) is not bool:
            raise ValueError(f'thermal.{name} must be boolean')
    chunk = policy['chunk_tokens']
    if type(chunk) is not int or chunk < 256 or chunk % 256:
        raise ValueError('thermal.chunk_tokens must be a positive multiple of 256')
    if policy['heavy'] and not policy['per_turn']:
        raise ValueError('heavy cells require per-turn gates and holds')
    if 'window_reference' in policy:
        ref = policy['window_reference']
        if (not isinstance(ref, Mapping) or set(ref) != {'fast_c', 'slow_c', 'source_member', 'span_ns'}
                or not isinstance(ref['source_member'], str) or not ref['source_member']
                or not isinstance(ref['span_ns'], list) or len(ref['span_ns']) != 2
                or any(type(t) is not int for t in ref['span_ns'])
                or ref['span_ns'][1] - ref['span_ns'][0] != 60 * NS
                or any(not temperature.valid_value('Tref', ref[k]) for k in ('fast_c', 'slow_c'))):
            raise ValueError('thermal.window_reference requires temperatures and 60 s custody provenance')
        policy['window_reference'] = dict(ref)
    return policy


def _good_window_rows(rows, end_ns, keys):
    start = end_ns - 60 * NS
    return [r for r in rows if start <= r['monotonic_ns'] < end_ns
            and (r['finished']['monotonic_after_ns'] - start) // NS == (r['monotonic_ns'] - start) // NS
            and all(k not in r.get('errors', {}) and temperature.valid_value(k, r['sensors'].get(k)) for k in keys)]


def slow_slope(rows, end_ns, key):
    """OLS °C/min on actual times in the preceding 60 seconds; no interpolation."""
    selected = _good_window_rows(rows, end_ns, (key,))
    good = [(r['monotonic_ns'], r['sensors'][key]) for r in selected]
    if len({(t - end_ns + 60*NS) // NS for t, _ in good}) < 54:
        return None
    x = [(t - end_ns) / NS for t, _ in good]
    y = [v for _, v in good]
    xm, ym = sum(x) / len(x), sum(y) / len(y)
    denom = sum((t - xm) ** 2 for t in x)
    return 60 * sum((t - xm) * (v - ym) for t, v in zip(x, y)) / denom if denom else None


def drain_decode(stream, mx=None):
    """Evaluate live generator arrays, including MLX's asynchronous lookahead.

    Only suspended generator locals and their built-in containers are visited;
    model objects are not traversed. This drains queued work before hold entry,
    without requesting a token or consuming RNG state. R1 must qualify this on
    pinned mlx-lm 0.31.3, including token identity and resume transients.
    """
    if mx is None:
        import mlx.core as mx
    seen, arrays, streams = set(), [], []
    native_frame = False
    stream_type = getattr(mx, 'Stream', None)

    def visit(value):
        nonlocal native_frame
        if id(value) in seen:
            return
        seen.add(id(value))
        if isinstance(value, mx.array):
            arrays.append(value)
        elif isinstance(value, GeneratorType):
            if value.gi_frame is not None:
                globals_ = value.gi_frame.f_globals
                native_frame |= str(globals_.get('__name__', '')).startswith('mlx_lm')
                # The inner generate_step iterator can live only on Python's
                # evaluation stack, outside f_locals. Its queued lookahead is
                # still covered by the module's explicit generation stream.
                for candidate in tuple(globals_.values()):
                    if isinstance(stream_type, type) and isinstance(candidate, stream_type):
                        if all(candidate is not s for s in streams):
                            streams.append(candidate)
                generation_stream = globals_.get('generation_stream')
                if generation_stream is not None and all(generation_stream is not s for s in streams):
                    streams.append(generation_stream)
                for child in tuple(value.gi_frame.f_locals.values()):
                    visit(child)
            visit(value.gi_yieldfrom)
        elif isinstance(value, (tuple, list)):
            for child in value:
                visit(child)
        elif isinstance(value, dict):
            for child in value.values():
                visit(child)
    visit(stream)
    if arrays:
        mx.eval(*arrays)
    if native_frame and not streams:
        raise RuntimeError('thermal.lookahead_generation_stream_unobserved')
    for stream_ in streams:
        mx.synchronize(stream_)
    mx.synchronize()


class ThermalSession:
    """One prepare-to-cleanup sidecar, using the same injected clock as turns.

    SystemClock uses a 1 Hz thread. Fake clocks explicitly call sample() as
    time advances. status_reader returns observed os_level / pm_state, plus
    their optional source stamps; it may be bound by an ALIGN launch adapter.
    With no callback a bundle-local outputs/align_thermal_status.json supplies
    {os_level, pm_state, pm_observed_ns, monotonic_ns}.
    No path in the episode spec is followed.
    """
    def __init__(self, policy, clock, context=None, *, reader=None, status_reader=None):
        self.policy = validate_policy(policy)
        self.clock, self.context = clock, context
        self.reader = reader if reader is not None else smc.Reader()
        self.status_reader = status_reader
        self.rows, self.intervals, self.events, self.flags = [], [], [], []
        self.reference = self.policy.get('window_reference')
        self.episode_reference = None
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.thread = None
        self.handle = None

    def start(self):
        if self.context is not None:
            self.handle = (self.context.outputs_dir / 'align_thermal.jsonl').open('x', encoding='utf-8')
        self.next_due_ns = monotonic_ns(self.clock.stamp()) + NS
        self.sample()
        if isinstance(self.clock, SystemClock):
            self.thread = threading.Thread(target=self._loop, name='align-thermal', daemon=True)
            self.thread.start()

    def _loop(self):
        while not self.stop_event.wait(max(0, (self.next_due_ns - monotonic_ns(self.clock.stamp())) / NS)):
            self.sample()
            self.next_due_ns += NS
            # Resume from now after a stall; never fabricate catch-up samples.
            now = monotonic_ns(self.clock.stamp())
            if self.next_due_ns <= now:
                self.next_due_ns = now + NS

    def _status(self):
        if self.status_reader is not None:
            return dict(self.status_reader())
        if self.context is None:
            return {}
        try:
            value = json.loads((self.context.outputs_dir / 'align_thermal_status.json').read_text())
            age = monotonic_ns(self.clock.stamp()) - value['monotonic_ns']
            return value if 0 <= age <= 2 * NS else {}
        except (OSError, ValueError, KeyError, TypeError):
            return {}

    def sample(self):
        with self.lock:
            started = self.clock.stamp()
            values = temperature.sample(self.reader, temperature.keys(self.policy['sensors']))
            finished = self.clock.stamp()
            try:
                status = self._status()
            except Exception as exc:
                status = {'error': f'{type(exc).__name__}:{exc}'}
            row = {'kind': 'sample', 'monotonic_ns': monotonic_ns(started),
                   'epoch_ns': _stamp_record(started)['epoch_ns'],
                   'started': _stamp_record(started), 'finished': _stamp_record(finished),
                   **values, 'status': status,
                   'sensor_metadata': {k: {'data_type': v[1], 'size': v[0]}
                                       for k, v in getattr(self.reader, '_info', {}).items()}}
            self.rows.append(row)
            if self.handle is not None:
                self.handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + '\n')
                self.handle.flush()
            return row

    def capture_reference(self, member):
        """Called at warmup entry: the final 60 s of first member's idle."""
        if self.reference is not None:
            return
        now = monotonic_ns(self.clock.stamp())
        with self.lock:
            rows = [r for r in self.rows if now - 60 * NS <= r['monotonic_ns'] < now]
        sensors = self.policy['sensors']
        # Missing baseline never becomes a guessed release reference.
        good = _good_window_rows(rows, now, (sensors['s_fast'], sensors['s_slow']))
        if len({(r['monotonic_ns'] - now + 60 * NS) // NS for r in good}) < 54:
            self.flags.append('thermal.state_unobserved')
            return
        self.reference = {'fast_c': median(r['sensors'][sensors['s_fast']] for r in good),
                          'slow_c': median(r['sensors'][sensors['s_slow']] for r in good),
                          'source_member': member, 'span_ns': [now - 60 * NS, now]}

    def wait(self, kind, *, turn=0, token_count=None, deadman=None, defer_resume=False):
        """G0 proceeds on timeout; unobserved gates wait then proceed with X4.

        G1/H stop only on an actual timeout or the member deadman.
        """
        if kind not in ('G0', 'G1', 'H'):
            raise ValueError('unknown thermal gate')
        entry = self.clock.stamp()
        start = monotonic_ns(entry)
        entry_slope = slow_slope(self.rows, start, self.policy['sensors']['s_slow'])
        cap = 600 if kind == 'G0' else self.policy['turn_cap_s']
        reference = self.reference if kind == 'G0' else self.episode_reference
        required = 10 if kind == 'G0' else 5
        fast, slow = (self.policy['sensors'][k] for k in ('s_fast', 's_slow'))
        consecutive, last_ns, unobserved = 0, None, reference is None
        release = None
        reason = 'timeout'
        latest, slope = None, None
        try:
            with deadman.guard() if deadman is not None else nullcontext():
                while True:
                    now = monotonic_ns(self.clock.stamp())
                    with self.lock:
                        rows = list(self.rows)
                    latest = rows[-1] if rows else None
                    window = [r for r in rows if now - 60 * NS <= r['monotonic_ns'] <= now]
                    # Missing slots, late reads and missing keys all count as failed reads.
                    span_start = now - 60 * NS
                    expected = 60
                    good_slots = {(r['monotonic_ns'] - span_start) // NS
                                  for r in _good_window_rows(window, now, (fast, slow))}
                    if len(good_slots) < .90 * expected:
                        unobserved = True
                    slope = slow_slope(rows, now, slow)
                    # Consume every queued observation in order. Checking only
                    # the last row can hide an intervening out-of-band sample.
                    new_rows = (rows[-1:] if last_ns is None else
                                [r for r in rows if r['monotonic_ns'] > last_ns])
                    for sample in new_rows:
                        continuous = last_ns is None or 0 < sample['monotonic_ns'] - last_ns <= 2 * NS
                        last_ns = sample['monotonic_ns']
                        good = (not unobserved and continuous and 0 <= now - last_ns <= 2 * NS
                                and all(temperature.valid_value(k, sample['sensors'].get(k)) for k in (fast, slow))
                                and sample['sensors'][fast] <= reference['fast_c'] + self.policy['delta_fast_c']
                                and sample['sensors'][slow] <= reference['slow_c'] + self.policy['delta_slow_c'])
                        if kind == 'G0':
                            status = sample['status']
                            pm_ns = status.get('pm_observed_ns')
                            sample_slope = slow_slope(rows, last_ns, slow)
                            good = (good and sample_slope is not None and abs(sample_slope) <= .2
                                    and status.get('os_level') == 0 and status.get('pm_state') == 'Nominal'
                                    and type(pm_ns) is int and 0 <= now - pm_ns <= 2 * NS)
                        consecutive = consecutive + 1 if good else 0
                    if new_rows and consecutive >= required:
                        release, reason = new_rows[-1], 'released'
                        break
                    if deadman is not None and deadman.expired():
                        reason = 'deadman'
                        break
                    elapsed = (now - start) / NS
                    limit = 300 if unobserved and kind == 'G0' else cap
                    if elapsed >= limit:
                        break
                    delay = min(1, limit - elapsed)
                    if deadman is not None:
                        delay = min(delay, max(0, deadman.remaining_s()))
                    self.clock.sleep(delay)
                    if self.thread is None:
                        self.sample()
        except DeadmanExpired:
            reason = 'deadman'
        exit_stamp = self.clock.stamp()
        if unobserved:
            self.flags.append('thermal.state_unobserved')
        elif reason == 'timeout':
            self.flags.append('thermal.start_gate_timeout' if kind == 'G0' else
                              f'thermal.{"hold" if kind == "H" else "gate"}_timeout:{turn}')
        if reason == 'deadman':
            self.flags.append(f'episode.deadman:{turn}')
        values = release or latest
        release_values = ({'fast_c': values['sensors'].get(fast), 'slow_c': values['sensors'].get(slow)}
                          if values else {'fast_c': None, 'slow_c': None})
        if kind == 'G0':
            self.episode_reference = release_values if all(v is not None for v in release_values.values()) else None
        row = {'kind': kind, 'turn': turn, 'token_count': token_count,
               'start_ns': start, 'end_ns': monotonic_ns(exit_stamp),
               'entry_stamp': _stamp_record(entry), 'exit_stamp': _stamp_record(exit_stamp),
               'entry_epoch_s': entry.epoch_s, 'exit_epoch_s': exit_stamp.epoch_s,
               'clock': 'episode_monotonic_ns', 'duration_s': (monotonic_ns(exit_stamp) - start) / NS,
               'reference': reference, 'release': release_values, 'slope_c_per_min': slope,
               'entry_slope_c_per_min': entry_slope,
               'entry_sensors': self._entry_values(start),
               'exit_sample_ns': values['monotonic_ns'] if values else None,
               'outcome': 'unobserved' if unobserved and reason != 'deadman' else reason}
        self.intervals.append(row)
        if not (kind == 'H' and defer_resume and (reason == 'released' or (unobserved and reason != 'deadman'))):
            self.persist_interval(row)
        phase = 'align_thermal_hold' if kind == 'H' else 'align_thermal_gate'
        self.events.extend([RuntimeEvent(entry.epoch_s, 'phase_start', phase, kind, row),
                            RuntimeEvent(exit_stamp.epoch_s, 'phase_end', phase, kind, row)])
        return row

    def resume_hold(self, row):
        """Stamp at the stream dispatch boundary; perform no journal I/O here."""
        from dataclasses import replace
        stamp = self.clock.stamp()
        row['condition_met_stamp'] = row['exit_stamp']
        row.update(exit_stamp=_stamp_record(stamp), exit_epoch_s=stamp.epoch_s,
                   end_ns=monotonic_ns(stamp), duration_s=(monotonic_ns(stamp)-row['start_ns'])/NS)
        for i in range(len(self.events)-1, -1, -1):
            if self.events[i].metadata is row and self.events[i].event_type == 'phase_end':
                self.events[i] = replace(self.events[i], timestamp_s=stamp.epoch_s)
                break

    def persist_interval(self, row):
        """Publish a finalized interval after dispatch (or after cancellation)."""
        with self.lock:
            if self.handle is not None:
                self.handle.write(json.dumps({'kind': 'gate_event', 'gate': row}, sort_keys=True, allow_nan=False) + '\n')
                self.handle.flush()

    def _entry_values(self, start):
        prior = [r for r in self.rows if r['monotonic_ns'] <= start]
        return prior[-1]['sensors'] if prior else {}

    def record(self):
        return {'policy': self.policy, 'window_reference': self.reference,
                'episode_reference': self.episode_reference, 'intervals': list(self.intervals),
                'flags': list(dict.fromkeys(self.flags))}

    def close(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=5)
        with self.lock:
            if self.handle is not None:
                self.handle.close()
                self.handle = None
            self.reader.close()
            close = getattr(self.status_reader, 'close', None)
            if close is not None:
                close()


class PowermetricsStatus:
    """Read-only tap of the already-running telemetry adapter; starts no sampler.

    Bind with bind_thermal_status at v4 adapter construction. Read only that
    adapter's current capture capability, including complete NUL-framed plists;
    never search for a capture or infer Nominal from an absent status.
    """
    def __init__(self, telemetry, clock, *, notify_reader=None):
        self.telemetry, self.clock = telemetry, clock
        self.notify = notify_reader
        self.path, self.position, self.pending = None, 0, b''
        self.pm_state, self.pm_observed_ns = None, None

    def __call__(self):
        import plistlib
        from joulewise.hazards.thermal import NotifyReader
        if self.notify is None:
            self.notify = NotifyReader()
        level = self.notify.read()
        path = getattr(self.telemetry, '_capture_path', None)
        if path != self.path:
            self.path, self.position, self.pending = path, 0, b''
            self.pm_state, self.pm_observed_ns = None, None
        if path is not None:
            with path.open('rb') as handle:
                handle.seek(self.position)
                chunk = handle.read(8*1024*1024)
                self.position += len(chunk)
            self.pending += chunk
            if len(self.pending) > 8*1024*1024:
                raise ValueError('powermetrics status tap incomplete frame exceeds bound')
            # A complete XML document may precede its NUL separator.
            if b'</plist>' in self.pending:
                end = self.pending.rindex(b'</plist>') + len(b'</plist>')
                complete, self.pending = self.pending[:end], self.pending[end:].lstrip(b'\0\n\r ')
                previous = complete.rfind(b'</plist>', 0, end-len(b'</plist>'))
                raw = complete[previous+len(b'</plist>') if previous >= 0 else 0:].strip(b'\0\n\r ')
                document = plistlib.loads(raw)
                self.pm_state = document.get('thermal_pressure')
                self.pm_observed_ns = monotonic_ns(self.clock.stamp())
        return {'os_level': level, 'pm_state': self.pm_state,
                'pm_observed_ns': self.pm_observed_ns, 'monotonic_ns': monotonic_ns(self.clock.stamp())}

    def close(self):
        if self.notify is not None:
            self.notify.close()


def bind_thermal_status(episode_adapter, telemetry_adapter):
    """v4 launcher wiring; no pinned controller/telemetry changes required."""
    feed = PowermetricsStatus(telemetry_adapter, episode_adapter.clock)
    episode_adapter.thermal_status_reader = feed
    return feed


class ThermalRegistry:
    """Per-run ALIGN registry which binds the runtime to its actual telemetry.

    Pass registry=ThermalRegistry() to the existing run_benchmark. Delegates
    every other adapter method unchanged. The v4 launcher must select this
    registry; the legacy runner and anchors keep their default registry.
    """
    def __init__(self, delegate=None, *, thermal_factory=None, status_factory=None):
        if delegate is None:
            from joulewise import adapters
            delegate = adapters
        self.delegate = delegate
        self.runtime = self.telemetry = None
        self.thermal_factory = thermal_factory
        self.status_factory = status_factory or PowermetricsStatus

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def _bind(self):
        if self.runtime is None or self.telemetry is None:
            return
        from joulewise.align.apple.workload import EpisodeRuntimeAdapter
        if isinstance(self.runtime, EpisodeRuntimeAdapter):
            self.runtime.thermal_factory = self.thermal_factory
            self.runtime.thermal_status_reader = self.status_factory(self.telemetry, self.runtime.clock)

    def resolve_runtime(self, config, clock):
        self.runtime, failure = self.delegate.resolve_runtime(config, clock)
        self._bind()
        return self.runtime, failure

    def resolve_telemetry(self, config, clock):
        self.telemetry, failure = self.delegate.resolve_telemetry(config, clock)
        self._bind()
        return self.telemetry, failure


def split_decode_events(events, holds):
    """Represent holds beside decode phases, preserving pinned phase validation.

    The controller/reducer forbids overlapping phases on one power source.
    Keep native token/prefill events and split only decode start/end support;
    the thermal session supplies the intervening hold phase events.
    """
    from dataclasses import replace
    starts = [e for e in events if e.phase == 'decode' and e.event_type == 'phase_start']
    ends = [e for e in events if e.phase == 'decode' and e.event_type == 'phase_end']
    if not holds:
        return events
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError('held decode needs exactly one native decode phase')
    first, last = starts[0], ends[0]
    result = [e for e in events if not (e.phase == 'decode' and e.event_type in ('phase_start', 'phase_end'))]
    cursor = first.timestamp_s
    for hold in holds:
        a = hold.get('entry_epoch_s', hold['entry_stamp']['epoch_ns']/NS)
        b = hold.get('exit_epoch_s', hold['exit_stamp']['epoch_ns']/NS)
        if not cursor <= a <= b <= last.timestamp_s:
            raise ValueError('hold outside native decode phase')
        if cursor < a:
            result.extend([replace(first, timestamp_s=cursor), replace(last, timestamp_s=a)])
        cursor = b
    if cursor < last.timestamp_s:
        result.extend([replace(first, timestamp_s=cursor), last])
    return sorted(result, key=lambda e: e.timestamp_s)
