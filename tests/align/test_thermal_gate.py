"""Synthetic-only gates/holds: fake SMC transport, clock and native stream."""
from dataclasses import replace
import json
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple.budget import DeadmanExpired, EpisodeDeadman
from joulewise.align.apple.endpoint import _StreamObservation
from joulewise.align.apple.smc_reader import Reader
from joulewise.align.apple.thermal_gates import ThermalSession, drain_decode, slow_slope, validate_gate_policy as validate_policy
from joulewise.align.apple.workload import EpisodeRuntimeAdapter, EpisodeSpec
from joulewise.align.apple.diagnostics import end_state
from joulewise.align.records import Episode, from_json
from joulewise.clock import FakeClock
from joulewise.hazards import smc
from tests.align.test_apple_campaign import base_config, episode_spec
from joulewise.adapters.mock_runtime import MockRuntimeAdapter

NS = 10**9


def policy(**updates):
    return {'sensors': {'s_fast': 'Tfak', 's_slow': 'Tslw', 'fan_keys': [], 'r0_sha256': 'a'*64},
            'delta_fast_c': 1., 'delta_slow_c': 1., 'turn_cap_s': 30.,
            'per_turn': True, 'heavy': False, 'chunk_tokens': 256,
            'window_reference': {'role': 'capture'}, **updates}


class Transport:
    def __init__(self, clock, values=None):
        self.clock, self.values = clock, values or (lambda t: (40., 40.))
        self.closed = False

    def call(self, request):
        key = smc.type_name(request.key)
        reply = smc.SMCKeyData(key=request.key)
        reply.keyInfo.dataSize, reply.keyInfo.dataType = 4, smc.fourcc('flt ')
        if request.data8 == smc.CMD_READ_KEY:
            values = self.values(self.clock.now())
            value = values[0 if key == 'Tfak' else 1]
            if value is None:
                reply.result = smc.RESULT_KEY_NOT_FOUND
            else:
                for i, b in enumerate(struct.pack('<f', value)):
                    reply.bytes[i] = b
        return reply

    def close(self):
        self.closed = True


def session(*, values=None, config=None):
    clock = FakeClock()
    transport = Transport(clock, values)
    obj = ThermalSession(config or policy(), clock, reader=Reader(transport),
                         status_reader=lambda: {'os_level': 0, 'pm_state': 'Nominal', 'pm_observed_ns': round(obj.clock.now()*NS)})
    obj.start()
    for _ in range(60):
        clock.sleep(1)
        obj.sample()
    obj.capture_reference('first')
    return obj, clock


class GateTests(unittest.TestCase):
    def test_gate_windows_use_sidecar_grid_across_caller_slot_boundaries(self):
        from joulewise.hazards.base import Stamp
        # Every valid 70 ms read crosses the caller's phase-anchored slot.
        obj, clock = session()
        self.addCleanup(obj.close)
        obj.sidecar.readings.clear()
        for second in range(61):
            # Use explicit three-clock stamps: the collector's grid starts at 0.
            values = {'sensors': {'Tfak': 40., 'Tslw': 40.}, 'errors': {},
                      'status': {'os_level': 0, 'pm_state': 'Nominal', 'pm_observed_ns': second * NS}}
            obj.sidecar.readings.append({'module': 'temperature', 'kind': 'reading', 'values': values,
                                        'started': Stamp(second*NS, second*NS, second*NS).to_json(),
                                        'finished': Stamp(second*NS+70_000_000, second*NS+70_000_000,
                                                          second*NS+70_000_000).to_json()})
        clock.sleep(.03)
        obj.reference = None
        obj.capture_reference('first')
        self.assertEqual(obj.reference['fast_c'], 40.)
        self.assertEqual(slow_slope(obj.rows, round(clock.now()*NS), 'Tslw'), 0.)
        self.assertEqual(obj.wait('G0')['outcome'], 'released')

    def test_batched_samples_cannot_skip_an_out_of_band_read(self):
        obj, clock = session()
        obj.wait('G0')
        sleep = clock.sleep
        calls = 0
        def advance(seconds):
            nonlocal calls
            calls += 1
            if calls == 1:
                sleep(seconds/2)
                obj.reader._transport.values = lambda t: (60, 60)
                obj.sample()
                sleep(seconds/2)
            else:
                sleep(seconds)
            obj.reader._transport.values = lambda t: (40, 40)
            obj.sample()
        clock.sleep = advance
        obj.sidecar._thread = object()  # advance() supplies asynchronous batches.
        gate = obj.wait('G1', turn=1)
        self.assertEqual(gate['outcome'], 'released')
        self.assertEqual(gate['duration_s'], 5)

    def test_g0_rejects_a_dead_pm_samplers_stale_nominal_state(self):
        obj, clock = session()
        obj.status_reader = lambda: {'os_level': 0, 'pm_state': 'Nominal', 'pm_observed_ns': 0}
        obj.sample()
        self.assertEqual(obj.wait('G0')['outcome'], 'timeout')

    def test_fixed_rate_sampling_with_parse_cost_and_phase_jitter(self):
        p = policy()
        clock = FakeClock()
        def read(keys):
            clock.sleep(.0002)
            return {'values': {k: 40. for k in keys}}
        reader = SimpleNamespace(read=read, close=lambda: None)
        def status():
            clock.sleep(.11)  # PM parsing must not lengthen the SMC bracket.
            return {'os_level': 0, 'pm_state': 'Nominal', 'pm_observed_ns': round(clock.now()*NS)}
        obj = ThermalSession(p, clock, reader=reader, status_reader=status)
        obj.start()
        class Stop:
            calls = 0
            def is_set(self):
                return self.calls >= 120
            def wait(self, delay):
                self.calls += 1
                if self.calls > 120:
                    return True
                clock.sleep(delay + (.003 if self.calls % 2 else .001))
                return False
        obj.sidecar._stop = Stop()
        obj.sidecar._loop()
        self.assertLess(clock.now(), 121)
        self.assertTrue(all(r['finished']['monotonic_after_ns'] - r['monotonic_ns'] == 200_000 for r in obj.rows))
        from joulewise.align.apple.thermal_desk import _coverage
        self.assertGreaterEqual(_coverage(obj.rows, 0, 120*NS, ('Tfak', 'Tslw'))['sample_fraction'], .99)
        obj.capture_reference('first')
        self.assertEqual(obj.reference['slow_c'], 40.)
        self.assertEqual(obj.wait('G0')['outcome'], 'released')

    def test_reference_accepts_ninety_percent_complete_slots(self):
        p = policy()
        obj, _ = session(config=p)
        for _ in range(6):
            obj.sidecar.readings.popleft()
        obj.capture_reference('first')
        self.assertIsNotNone(obj.reference)

    def test_g0_requires_ten_samples_slope_and_nominal_status(self):
        obj, clock = session()
        gate = obj.wait('G0')
        self.assertEqual(gate['outcome'], 'released')
        self.assertEqual(gate['duration_s'], 9)
        self.assertEqual(gate['slope_c_per_min'], 0)
        self.assertEqual(gate['start_ns'], 60*NS)
        self.assertEqual(gate['end_ns'], 69*NS)
        self.assertEqual(obj.episode_reference, {'fast_c': 40., 'slow_c': 40.})
        obj.status_reader = lambda: {'os_level': 1, 'pm_state': 'Nominal'}
        obj.sample()
        failed = obj.wait('G0')
        self.assertEqual(failed['duration_s'], 600)
        self.assertEqual(failed['outcome'], 'timeout')
        self.assertIn('thermal.start_gate_timeout', obj.flags)
        obj.close()

    def test_hot_g0_timeout_proceeds_and_fast_sensor_also_gates(self):
        obj, _ = session()
        obj.reader._transport.values = lambda t: (45, 40)
        gate = obj.wait('G0')
        self.assertEqual(gate['duration_s'], 600)
        self.assertEqual(gate['outcome'], 'timeout')
        self.assertEqual(obj.episode_reference['fast_c'], 45)
        self.assertIn('thermal.start_gate_timeout', obj.flags)

    def test_unsettled_slope_prevents_g0_release(self):
        obj, clock = session(values=lambda t: (40, 38 + .01*t))
        self.assertAlmostEqual(slow_slope(obj.rows, 60*NS, 'Tslw'), .6, places=5)
        gate = obj.wait('G0')
        self.assertEqual(gate['outcome'], 'timeout')
        self.assertGreater(clock.now(), 600)

    def test_g1_never_ratchets_after_each_turn(self):
        obj, clock = session()
        obj.wait('G0')
        obj.reader._transport.values = lambda t: (40.8, 40.8)
        gate = obj.wait('G1', turn=1)
        self.assertEqual(gate['outcome'], 'released')
        obj.reader._transport.values = lambda t: (41.5, 41.5)
        obj.sample()
        second = obj.wait('G1', turn=2)
        self.assertEqual(second['outcome'], 'timeout')
        self.assertEqual(second['reference'], {'fast_c': 40., 'slow_c': 40.})
        self.assertIn('thermal.gate_timeout:2', obj.flags)

    def test_missing_sensor_timed_wait_is_distinct(self):
        obj, _ = session(values=lambda t: (None, 40))
        gate = obj.wait('G0')
        self.assertEqual(gate['duration_s'], 300)
        self.assertEqual(gate['outcome'], 'unobserved')
        self.assertEqual(obj.flags, ['thermal.state_unobserved'])
        gate = obj.wait('G1', turn=1)
        self.assertEqual(gate['duration_s'], 30)
        self.assertEqual(gate['outcome'], 'unobserved')

    def test_idle_reference_is_last_sixty_seconds_and_is_not_replaced(self):
        p = policy()
        obj, clock = session(values=lambda t: (38 + t/60, 40 + t/60), config=p)
        obj.capture_reference('window-first')
        self.assertEqual(obj.reference['span_ns'], [0, 60*NS])
        ref = dict(obj.reference)
        clock.sleep(100)
        obj.capture_reference('later')
        self.assertEqual(obj.reference, ref)

    def test_policy_is_opt_in_and_validated(self):
        spec = episode_spec(hidden=False)
        self.assertNotIn('thermal', json.loads(spec.to_text()))
        for update in ({'turn_cap_s': 301}, {'chunk_tokens': 10}, {'heavy': True, 'per_turn': False}):
            with self.assertRaises(ValueError):
                validate_policy(policy(**update))
        with self.assertRaisesRegex(ValueError, 'neutral'):
            EpisodeSpec.from_text(replace(spec, thermal=policy()).to_text())


class HoldTests(unittest.TestCase):
    def test_unobserved_hold_is_a_timed_wait_then_decode_continues(self):
        obj, clock = session(config=policy(heavy=True))
        obj.wait('G0')
        obj.reader._transport.values = lambda t: (None, 40)
        # Dropout covers enough of the evaluation window to latch X4.
        for _ in range(7):
            clock.sleep(1)
            obj.sample()
        observation = _StreamObservation(SimpleNamespace(stream_generate=lambda: self.stream(300, clock)),
                                         max_tokens=300, thermal=obj)
        with patch('joulewise.align.apple.thermal_gates.drain_decode', lambda stream: None):
            self.assertEqual(len(list(observation.stream_generate())), 300)
        self.assertFalse(observation.thermal_aborted)
        self.assertIn('thermal.state_unobserved', obj.flags)
        self.assertEqual(obj.intervals[-1]['outcome'], 'unobserved')

    def stream(self, n, clock):
        for i in range(n):
            clock.sleep(.001)
            yield SimpleNamespace(token=i, finish_reason='stop' if i == n-1 else None)

    def test_fixed_token_holds_do_not_change_ids_and_drain_before_stamp(self):
        obj, clock = session(config=policy(heavy=True))
        obj.wait('G0')
        drained = []
        def drain(stream):
            clock.sleep(.09)  # pending lookahead work remains owned
            drained.append(clock.now())
        native = SimpleNamespace(stream_generate=lambda: self.stream(600, clock))
        observation = _StreamObservation(native, max_tokens=600, thermal=obj)
        with patch('joulewise.align.apple.thermal_gates.drain_decode', drain):
            tokens = [r.token for r in observation.stream_generate()]
        self.assertEqual(tokens, list(range(600)))
        holds = [r for r in obj.intervals if r['kind'] == 'H']
        self.assertEqual([h['token_count'] for h in holds], [256, 512])
        for hold, drained_at in zip(holds, drained):
            self.assertEqual(hold['start_ns'], round(drained_at*NS))
            # Absolute collector ticks retain their phase across hold entry.
            # The latest pre-entry sample plus four new ticks qualify.
            samples = [r for r in obj.rows if hold['start_ns']-NS < r['monotonic_ns'] <= hold['exit_sample_ns']]
            self.assertGreaterEqual(len(samples), 5)
        self.assertFalse(observation.deadman_expired)

    def test_hold_timeout_returns_partial_tokens_and_closes_generator(self):
        obj, clock = session(config=policy(heavy=True))
        obj.wait('G0')
        obj.reader._transport.values = lambda t: (60, 60)
        obj.sample()
        closed = []
        def stream():
            try:
                yield from self.stream(600, clock)
            finally:
                closed.append(True)
        observation = _StreamObservation(SimpleNamespace(stream_generate=stream), max_tokens=600, thermal=obj)
        with patch('joulewise.align.apple.thermal_gates.drain_decode', lambda stream: None):
            tokens = list(observation.stream_generate())
        self.assertEqual(len(tokens), 256)
        self.assertTrue(observation.thermal_aborted)
        self.assertEqual(closed, [True])
        self.assertIn('thermal.hold_timeout:0', obj.flags)

    def test_deadman_during_drain_retains_every_returned_token(self):
        obj, clock = session(config=policy(heavy=True))
        obj.wait('G0')
        closed = []
        def stream():
            try:
                yield from self.stream(600, clock)
            finally:
                closed.append(True)
        observation = _StreamObservation(SimpleNamespace(stream_generate=stream), max_tokens=600, thermal=obj,
                                         deadman=EpisodeDeadman(clock, clock.stamp(), 100))
        with patch('joulewise.align.apple.thermal_gates.drain_decode', side_effect=DeadmanExpired):
            self.assertEqual([r.token for r in observation.stream_generate()], list(range(256)))
        self.assertTrue(observation.deadman_expired)
        self.assertEqual(observation.finish_reason, 'episode.deadman')
        self.assertEqual(closed, [True])

    def test_hold_exit_includes_bookkeeping_until_next_dispatch(self):
        obj, clock = session(config=policy(heavy=True))
        obj.wait('G0')
        wait = obj.wait
        def delayed_return(*args, **kwargs):
            row = wait(*args, **kwargs)
            clock.sleep(.25)  # CPU bookkeeping after the condition is met
            return row
        obj.wait = delayed_return
        dispatches = []
        def stream():
            for i in range(300):
                dispatches.append(round(clock.now()*NS))
                yield SimpleNamespace(token=i, finish_reason=None)
        observation = _StreamObservation(SimpleNamespace(stream_generate=stream), max_tokens=300, thermal=obj)
        with patch('joulewise.align.apple.thermal_gates.drain_decode', lambda stream: None):
            self.assertEqual(len(list(observation.stream_generate())), 300)
        hold = obj.intervals[-1]
        self.assertEqual(hold['end_ns'], dispatches[256])
        self.assertEqual(hold['end_ns']-hold['condition_met_stamp']['monotonic_after_ns'], NS//4)

    def test_deadman_bounds_wall_time_without_an_alarm_running_in_hold(self):
        obj, clock = session(config=policy(heavy=True))
        obj.wait('G0')
        deadman = EpisodeDeadman(clock, clock.stamp(), 100)
        observation = _StreamObservation(SimpleNamespace(stream_generate=lambda: self.stream(300, clock)),
                                         max_tokens=300, thermal=obj, deadman=deadman)
        with patch('joulewise.align.apple.thermal_gates.drain_decode', lambda stream: None):
            self.assertEqual(len(list(observation.stream_generate())), 300)
        self.assertFalse(deadman.expired())
        obj.reader._transport.values = lambda t: (60, 60)
        obj.sample()
        short = EpisodeDeadman(clock, clock.stamp(), 3)
        gate = obj.wait('H', turn=1, token_count=256, deadman=short)
        self.assertEqual(gate['outcome'], 'deadman')
        self.assertAlmostEqual(gate['duration_s'], 3)
        self.assertIn('episode.deadman:1', obj.flags)
        self.assertNotIn('thermal.hold_timeout:1', obj.flags)

    def test_drain_visits_nested_suspended_lookahead_without_advancing(self):
        arrays, visits = [], []
        class Array:
            pass
        def inner():
            lookahead = Array()
            arrays.append(lookahead)
            yield 1
            visits.append('dispatched')
        def outer():
            stream = inner()
            for item in stream:
                yield item
        stream = outer()
        next(stream)
        evaluated = []
        mx = SimpleNamespace(array=Array, eval=lambda *a: evaluated.extend(a), synchronize=lambda: visits.append('sync'))
        drain_decode(stream, mx)
        self.assertEqual(evaluated, arrays)
        self.assertEqual(visits, ['sync'])

    def test_drain_synchronizes_native_generation_stream_or_refuses(self):
        # A for-loop's temporary inner generator need not be in f_locals.
        # Synchronizing its module stream still drains asynchronous lookahead.
        stream = object()
        namespace = {'__name__': 'mlx_lm.generate', 'generation_stream': stream}
        exec('def native():\n    yield 1\n', namespace)
        generator = namespace['native']()
        next(generator)
        synchronized = []
        mx = SimpleNamespace(array=type('Array', (), {}), eval=lambda *a: None,
                             synchronize=lambda *s: synchronized.append(s))
        drain_decode(generator, mx)
        self.assertEqual(synchronized, [(stream,), ()])
        del namespace['generation_stream']
        with self.assertRaisesRegex(RuntimeError, 'stream_unobserved'):
            drain_decode(generator, mx)


class WorkloadTests(unittest.TestCase):
    def run_episode(self, *, fail_g1=False, g0_hot=False, long_episode=False, deadman_s=1000, dropout=False):
        class SamplingClock(FakeClock):
            observer = None
            def sleep(self, seconds):
                while seconds > 0:
                    step = min(1, seconds)
                    super().sleep(step)
                    seconds -= step
                    if self.observer is not None:
                        self.observer.sample()
        clock = SamplingClock()
        holders = []
        def factory(p, c, context):
            obj, _ = session(config=p)
            # Rebase clock and seed a 60 s baseline before adapter prepare.
            obj.clock = c
            obj.reader._transport.clock = c
            clock.sleep(60)
            holders.append(obj)
            clock.observer = obj
            obj.start = lambda: None
            if g0_hot:
                obj.reader._transport.values = lambda t: (60, 60)
            return obj
        spec = replace(episode_spec(hidden=False), thermal=policy(), warmup_condition='benign',
                       max_episode_decode_tokens=4096, deadman_s=deadman_s)
        config = replace(base_config(), workload_profile=replace(base_config().workload_profile,
                         name='align_episode', prompt_text=spec.to_text()))
        adapter = EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock, thermal_factory=factory)
        self.assertTrue(adapter.prepare(config).ok)
        self.assertTrue(adapter.warmup(config).ok)
        # Fake native generation advances the sidecar's samples on demand.
        orig = adapter.runtime.run_workload
        def runtime_run(*args, **kwargs):
            result = orig(*args, **kwargs)
            if long_episode:
                clock.sleep(500)
            if fail_g1:
                holders[0].reader._transport.values = lambda t: (60, 60)
            if dropout:
                holders[0].reader._transport.values = lambda t: (None, 40)
            holders[0].sample()
            return result
        adapter.runtime.run_workload = runtime_run
        from joulewise.interfaces import AdapterFailure
        try:
            result = adapter.run_workload(config)
        except AdapterFailure:
            if not long_episode:
                raise
            result = adapter._failed_episode_result
        ep = from_json(Episode, result.output_artifacts['align_episode.json'])
        adapter.cleanup(config)
        return ep, result

    def test_g1_timeout_stops_before_next_chat_and_preserves_evidence(self):
        ep, result = self.run_episode(fail_g1=True)
        self.assertEqual(len(ep.turns), 1)
        self.assertIn('thermal.gate_timeout:1', ep.flags)
        self.assertEqual(result.metadata['align_episode']['stop_condition'], 'thermal.incomplete')
        self.assertIsNotNone(ep.main_task_score)

    def test_unobserved_g1_keeps_capability_trajectory(self):
        ep, result = self.run_episode(dropout=True)
        self.assertGreater(len(ep.turns), 1)
        self.assertIn('thermal.state_unobserved', ep.flags)
        self.assertEqual(result.metadata['align_episode']['stop_condition'], 'episode_returned')
        self.assertEqual(end_state(ep), 'returned_without_tool_call')
        artifact = from_json(Episode, result.output_artifacts['align_episode.json'])
        self.assertEqual(end_state(artifact), 'returned_without_tool_call')
        self.assertIsNotNone(ep.main_task_score)

    def test_g0_timeout_proceeds_with_calibration_exclusion(self):
        ep, _ = self.run_episode(g0_hot=True)
        self.assertGreater(len(ep.turns), 0)
        self.assertIn('thermal.start_gate_timeout', ep.flags)
        self.assertLessEqual(ep.hardware['thermal']['intervals'][0]['end_ns'], ep.start_ns)

    def test_g0_timeout_consumes_deadman_slack_before_long_episode(self):
        ep, result = self.run_episode(g0_hot=True, long_episode=True, deadman_s=1086)
        g0 = ep.hardware['thermal']['intervals'][0]
        self.assertEqual(g0['duration_s'], 600)
        self.assertIn('thermal.start_gate_timeout', ep.flags)
        self.assertIn('episode.deadman:0', ep.flags)
        # A fake blocking call can overshoot at its return boundary; it must
        # not receive another full 1086 seconds after spending 600 in G0.
        self.assertEqual(len(ep.turns), 1)
        self.assertLess((ep.end_ns-g0['start_ns'])/NS, 1200)
        self.assertEqual(result.metadata['align_episode']['stop_condition'], 'episode.deadman')


class StatusWiringTests(unittest.TestCase):
    def test_pm_tap_parses_only_latest_complete_frame(self):
        import plistlib
        from joulewise.align.apple.thermal_gates import PowermetricsStatus
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'fake.plist'
            frame = plistlib.dumps({'thermal_pressure': 'Nominal'})
            latest = plistlib.dumps({'thermal_pressure': 'Serious'})
            path.write_bytes((frame+b'\0')*9 + latest + b'\0' + frame[:40])
            feed = PowermetricsStatus(SimpleNamespace(_capture_path=path), FakeClock(),
                                      notify_reader=SimpleNamespace(read=lambda: 0))
            with patch('plistlib.loads', wraps=plistlib.loads) as parse:
                self.assertEqual(feed()['pm_state'], 'Serious')
                self.assertEqual(parse.call_count, 1)
                feed()
                self.assertEqual(parse.call_count, 1)

    def test_pm_tap_reads_only_complete_frames_and_observes_new_capture(self):
        import plistlib
        from joulewise.align.apple.thermal_gates import PowermetricsStatus
        class Notify:
            closed = False
            def read(self):
                return 0
            def close(self):
                self.closed = True
        clock = FakeClock()
        notify = Notify()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'fake.plist'
            raw = plistlib.dumps({'thermal_pressure': 'Nominal'})
            path.write_bytes(raw[:30])
            telemetry = SimpleNamespace(_capture_path=path)
            feed = PowermetricsStatus(telemetry, clock, notify_reader=notify)
            self.assertIsNone(feed()['pm_state'])
            path.write_bytes(raw+b'\0')
            self.assertEqual(feed()['pm_state'], 'Nominal')
            with path.open('ab') as f:
                f.write(plistlib.dumps({'thermal_pressure': 'Serious'})+b'\0')
            self.assertEqual(feed()['pm_state'], 'Serious')
            other = Path(d)/'next.plist'
            other.write_bytes(b'')
            telemetry._capture_path = other
            self.assertIsNone(feed()['pm_state'])
            feed.close()
            self.assertTrue(notify.closed)

    def test_registry_binds_the_same_telemetry_in_either_resolution_order(self):
        from joulewise.align.apple.thermal_gates import ThermalRegistry
        clock = FakeClock()
        runtime = EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock)
        telemetry = object()
        delegate = SimpleNamespace(resolve_runtime=lambda c, k: (runtime, None),
                                   resolve_telemetry=lambda c, k: (telemetry, None), marker='delegate')
        for order in (('resolve_runtime', 'resolve_telemetry'), ('resolve_telemetry', 'resolve_runtime')):
            bindings = []
            registry = ThermalRegistry(delegate, status_factory=lambda t, c: bindings.append((t, c)) or 'feed')
            for name in order:
                getattr(registry, name)(base_config(), clock)
            self.assertEqual(bindings, [(telemetry, clock)])
            self.assertEqual(runtime.thermal_status_reader, 'feed')
            self.assertEqual(registry.marker, 'delegate')


class NativeIntegrationTests(unittest.TestCase):
    def held_run(self, root, *, timeout=False, expire_drain=False, dropout=False):
        from tests.align.test_apple_endpoint import run_native_review
        class TickClock(FakeClock):
            sidecar = None
            next_tick = None
            def sleep(self, seconds):
                end = self.now()+seconds
                while self.sidecar is not None and self.next_tick <= end:
                    super().sleep(max(0, self.next_tick-self.now()))
                    self.sidecar.sample()
                    self.next_tick += 1
                super().sleep(max(0, end-self.now()))
        clock = TickClock()
        original_init, original_start = ThermalSession.__init__, ThermalSession.start
        def init(obj, p, c, context=None, **kwargs):
            original_init(obj, p, c, context, reader=Reader(Transport(c)),
                          status_reader=lambda: {'os_level': 0, 'pm_state': 'Nominal', 'pm_observed_ns': round(c.now()*NS)})
        def start(obj):
            # Seed the real prepare-to-warmup history on a fake clock only.
            # The readiness projector can construct another adapter; it does
            # no generation and must not create a live thread or hardware read.
            if not isinstance(obj.clock, FakeClock):
                return
            original_start(obj)
            for _ in range(60):
                obj.clock.sleep(1)
                obj.sample()
            obj.clock.sidecar, obj.clock.next_tick = obj, obj.clock.now()+1
        def drain(stream):
            clock.sleep(.09)
            if expire_drain:
                raise DeadmanExpired()
            if timeout:
                clock.sidecar.reader._transport.values = lambda t: (60, 60)
                clock.sidecar.sample()
            if dropout:
                clock.sidecar.reader._transport.values = lambda t: (None, 40)
                clock.sidecar.sample()
        with patch.object(ThermalSession, '__init__', init), patch.object(ThermalSession, 'start', start), patch(
            'joulewise.align.apple.thermal_gates.drain_decode', drain
        ):
            return run_native_review(root, 'think', clock, spec_updates={
                'thermal': policy(heavy=True), 'warmup_condition': 'benign',
                'max_episode_decode_tokens': 181, 'deadman_s': 1000})

    def test_real_workload_endpoint_budget_and_held_stream_keep_exact_tokens(self):
        from tests.align.test_apple_endpoint import run_native_review
        from joulewise.align.apple.workload import read_episode_bundle
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plain, status, _ = run_native_review(root/'plain', 'think', FakeClock(),
                spec_updates={'max_episode_decode_tokens': 181, 'deadman_s': 1000})
            self.assertEqual(status.status.value, 'succeeded')
            held, status, _ = self.held_run(root/'held')
            self.assertEqual(status.status.value, 'succeeded', status)
            ep = read_episode_bundle(held)
            self.assertEqual([t.decode_tokens for t in ep.turns], [180, 260])
            self.assertIn('episode.decode_budget:2', ep.flags)
            self.assertFalse(any(f.startswith(('episode.deadman:', 'thermal.')) for f in ep.flags), ep.flags)
            a, b = ([json.loads(line)['generation']['output_token_ids'] for line in
                     (path/'outputs/align_turns.jsonl').read_text().splitlines()] for path in (plain, held))
            self.assertEqual(a, b)
            self.assertEqual((plain/'outputs/align_transcript.jsonl').read_bytes(),
                             (held/'outputs/align_transcript.jsonl').read_bytes())
            intervals = ep.hardware['thermal']['intervals']
            self.assertEqual([r['kind'] for r in intervals], ['G0', 'G1', 'H'])
            self.assertEqual(intervals[-1]['token_count'], 256)
            journal = [json.loads(line) for line in (held/'outputs/align_thermal.jsonl').read_text().splitlines()]
            self.assertEqual((journal[0]['kind'], journal[-1]['kind']), ('session_start', 'session_end'))
            phases = [r for r in journal if r['kind'] in ('align_thermal_gate', 'align_thermal_hold')]
            self.assertEqual([r['values']['state'] for r in phases], ['begin', 'end']*3)
            self.assertEqual([r['values']['gate'] for r in phases if r['values']['state'] == 'end'], intervals)
            self.assertTrue(all(r['schema'] == 'joulewise.align_thermal.v1' for r in journal))
            reading = next(r for r in journal if r['kind'] == 'reading')
            self.assertEqual(reading['values']['readings']['Tfak']['data_type'], 'flt ')
            self.assertEqual(reading['values']['readings']['Tfak']['raw_hex'], struct.pack('<f', 40.).hex())

    def test_native_hold_timeout_preserves_partial_ids_and_dispatches_no_tools(self):
        from joulewise.align.apple.workload import read_episode_bundle
        with tempfile.TemporaryDirectory() as d:
            bundle, status, _ = self.held_run(Path(d), timeout=True)
            ep = read_episode_bundle(bundle)
            self.assertEqual(status.status.value, 'succeeded', status)
            self.assertEqual([t.decode_tokens for t in ep.turns], [180, 256])
            self.assertEqual(ep.turns[-1].tool_calls, ())
            self.assertIn('thermal.hold_timeout:1', ep.flags)
            self.assertIsNotNone(ep.main_task_score)
            self.assertTrue(ep.hardware['token_budget']['incomplete'])
            self.assertEqual(ep.hardware['token_budget']['decode_tokens_used'], 436)

    def test_unobserved_hold_keeps_completed_tools_and_capability(self):
        from joulewise.align.apple.workload import read_episode_bundle
        with tempfile.TemporaryDirectory() as d:
            bundle, status, _ = self.held_run(Path(d), dropout=True)
            ep = read_episode_bundle(bundle)
            self.assertEqual(status.status.value, 'succeeded')
            self.assertEqual([t.decode_tokens for t in ep.turns], [180, 260])
            self.assertIn('thermal.state_unobserved', ep.flags)
            self.assertTrue(ep.turns[-1].tool_calls)
            self.assertFalse(ep.hardware['token_budget']['incomplete'])
            self.assertEqual(ep.hardware['thermal']['intervals'][-1]['outcome'], 'unobserved')
            self.assertEqual(end_state(ep), 'episode.decode_budget:2')
            from scripts.align_pilot_session import episode_summary
            summary = episode_summary(bundle)
            self.assertEqual(summary['end_state'], 'episode.decode_budget:2')
            self.assertIsNotNone(ep.main_task_score)

    def test_endpoint_records_partial_turn_when_drain_alarm_fires(self):
        from joulewise.align.apple.workload import read_episode_bundle
        with tempfile.TemporaryDirectory() as d:
            bundle, status, _ = self.held_run(Path(d), expire_drain=True)
            ep = read_episode_bundle(bundle)
            self.assertEqual(status.status.value, 'failed')
            self.assertEqual([t.decode_tokens for t in ep.turns], [180, 256])
            self.assertEqual(ep.turns[-1].tool_calls, ())
            self.assertIn('episode.deadman:1', ep.flags)
            rows = [json.loads(line) for line in (bundle/'outputs/align_turns.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows[-1]['generation']['output_token_ids']), 256)
            self.assertTrue((bundle/'outputs/align_runtime_events.jsonl').read_text())


if __name__ == '__main__':
    unittest.main()
