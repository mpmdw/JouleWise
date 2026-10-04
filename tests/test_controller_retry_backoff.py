"""Delayed retry ordering and strict admission checks with synthetic evidence."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest import mock

from joulewise import controller, environment_admission
from joulewise.adapters.powermetrics import anchor_records_from_powermetrics, parse_powermetrics_records
from joulewise.clock import ClockStamp, FakeClock
from joulewise.schemas import CampaignPolicy, RunStatus
from joulewise.uncertainty_evidence import CLOCK_METHOD_V3, derive_powermetrics_anchor_v3
from scripts.gen_g2_phase_d import G2A_CAMPAIGN_POLICY_PATH
from tests.test_controller import AdmissionIdleRegistry, campaign_policy_fixture, make_config

ROOT = Path(__file__).resolve().parents[1]


class RecordingClock(FakeClock):
    def __init__(self):
        super().__init__(start=1_700_000_000)
        self.trace = []

    def sleep(self, seconds):
        self.trace.append(('sleep', seconds, self.now()))
        super().sleep(seconds)


class RetryBackoffTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.runs = Path(self.temporary.name) / 'runs'

    def run_member(self, backoff=None, busy=(0.9, 0.1), *, failed_guard=None, strict_fixture=False):
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        if backoff is not None:
            policy = replace(policy, idle_admission=replace(policy.idle_admission, retry_backoff_s=backoff))
        if strict_fixture:
            relative = G2A_CAMPAIGN_POLICY_PATH if backoff else Path('configs/campaign_policies/quiet_mac_p2_production.json')
            raw = (ROOT / relative).read_bytes()
            policy = CampaignPolicy.from_mapping(json.loads(raw))
            binding.update(sha256=hashlib.sha256(raw).hexdigest(), policy_id=policy.policy_id,
                           source=str(ROOT / relative))
            preflight['policy_sha256'] = binding['sha256']
        config = make_config('retry-' + str(len(list(self.runs.glob('*')))))
        if strict_fixture:
            config = replace(config, sampling=replace(config.sampling, idle_seconds=75))
        clock = RecordingClock()
        registry = AdmissionIdleRegistry([False, False], cpu_busy_sequence=list(busy))
        resolve = registry.resolve_telemetry
        promotion = mock.Mock()

        def telemetry(*args):
            adapter, failure = resolve(*args)
            adapter.promote_idle_admission_attempt = promotion
            return adapter, failure

        registry.resolve_telemetry = telemetry
        original = controller._Execution._admission_guard_observation

        def guard(execution, phase):
            clock.trace.append(('guard', phase, clock.now()))
            row = original(execution, phase)
            if strict_fixture:
                row['capture_skipped'] = False
            if phase == failed_guard:
                row['display_power_state'] = 'any_awake'
            return row

        with mock.patch.object(controller._Execution, '_admission_guard_observation', guard):
            path, summary = controller.run_benchmark(config, self.runs, clock,
                registry=registry, environment_snapshot=snapshot, campaign_policy=policy,
                campaign_policy_binding=binding, campaign_environment_preflight=preflight)
        metadata = json.loads((path / 'metadata.json').read_bytes())
        return path, summary, metadata, clock, promotion

    def test_zero_backoff_preserves_legacy_record_and_has_no_inter_attempt_sleep(self):
        absent = self.run_member()
        zero = self.run_member(0)
        self.assertEqual(absent[2]['environment_admission'], zero[2]['environment_admission'])
        for _, summary, metadata, clock, _ in (absent, zero):
            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            admission = metadata['environment_admission']
            self.assertNotIn('retry_backoff', admission)
            # Pinned from the original controller at 871a43f6 with this harness.
            self.assertEqual(hashlib.sha256(json.dumps(admission, sort_keys=True).encode()).hexdigest(),
                             '8c2faf057456e0034704d92600dcdf7078af7cd26438274c0f25c43727ab2295')
            after1 = clock.trace.index(next(row for row in clock.trace if row[:2] == ('guard', 'after_attempt_1')))
            self.assertEqual(clock.trace[after1 + 1][:2], ('guard', 'before_attempt_2'))
            self.assertEqual(admission['attempts'][1]['start_s'], admission['attempts'][0]['end_s'])

    def test_rejected_first_attempt_waits_once_before_retry_guard_and_promotes_second(self):
        _, summary, metadata, clock, promotion = self.run_member(600)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        admission = metadata['environment_admission']
        self.assertEqual([row['admitted'] for row in admission['attempts']], [False, True])
        first, second = admission['attempts']
        self.assertEqual(admission['retry_backoff'],
                         {'requested_s': 600, 'start_s': first['end_s'], 'end_s': second['start_s']})
        self.assertEqual(second['start_s'] - first['end_s'], 600)
        sleeps = [row for row in clock.trace if row[:2] == ('sleep', 600)]
        self.assertEqual(len(sleeps), 1)
        index = clock.trace.index(sleeps[0])
        self.assertEqual(clock.trace[index - 1][:2], ('guard', 'after_attempt_1'))
        self.assertEqual(clock.trace[index + 1][:2], ('guard', 'before_attempt_2'))
        self.assertEqual([row['phase'] for row in admission['guard_observations']],
            ['before_attempt_1', 'after_attempt_1', 'before_attempt_2', 'after_attempt_2'])
        promotion.assert_called_once()
        self.assertEqual(promotion.call_args.kwargs['attempt'], 2)

    def test_admitted_first_attempt_never_waits_or_retries(self):
        _, summary, metadata, clock, promotion = self.run_member(600, busy=(0.1,))
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(len(metadata['environment_admission']['attempts']), 1)
        self.assertNotIn('retry_backoff', metadata['environment_admission'])
        self.assertNotIn(600, [row[1] for row in clock.trace if row[0] == 'sleep'])
        promotion.assert_not_called()

    def test_second_rejection_aborts_with_unchanged_reason_and_no_third_attempt(self):
        _, summary, metadata, clock, promotion = self.run_member(600, busy=(0.9, 0.8))
        self.assertEqual(summary.status, RunStatus.FAILED)
        admission = metadata['environment_admission']
        self.assertEqual(admission['failure'], 'idle environment admission failed after one retry')
        self.assertEqual(admission['decision'], 'abort')
        self.assertEqual(admission['claim_reason'], 'environment_admission_failed')
        self.assertEqual(len(admission['attempts']), 2)
        self.assertEqual(sum(row[:2] == ('sleep', 600) for row in clock.trace), 1)
        promotion.assert_not_called()

    def test_first_post_capture_guard_failure_aborts_without_wait(self):
        _, summary, metadata, clock, _ = self.run_member(600, failed_guard='after_attempt_1')
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(len(metadata['environment_admission']['attempts']), 1)
        self.assertNotIn('retry_backoff', metadata['environment_admission'])
        self.assertNotIn(600, [row[1] for row in clock.trace if row[0] == 'sleep'])

    def test_retry_guard_is_rechecked_after_wait_and_can_abort_before_capture(self):
        _, summary, metadata, clock, _ = self.run_member(600, failed_guard='before_attempt_2')
        self.assertEqual(summary.status, RunStatus.FAILED)
        admission = metadata['environment_admission']
        self.assertEqual(len(admission['attempts']), 1)
        self.assertIn('retry_backoff', admission)
        self.assertEqual(admission['failure'], 'display became or remained awake during idle admission')
        self.assertEqual(sum(row[:2] == ('sleep', 600) for row in clock.trace), 1)

    def test_backoff_bundle_passes_strict_admission_and_measured_window_checks(self):
        for backoff in (0, 300):
            with self.subTest(backoff=backoff):
                path, summary, metadata, clock, _ = self.run_member(backoff, strict_fixture=True)
                self.assertEqual(summary.status, RunStatus.SUCCEEDED)
                admission = metadata['environment_admission']
                self.assertEqual(environment_admission.environment_admission_refusals(
                    admission, require_attempt_timing=True), ())
                # Supply deterministic native telemetry for the controller-produced
                # admission. No validator, parser, or anchor solver is mocked.
                attempts = admission['attempts']
                start = attempts[0]['start_s']
                events = [json.loads(line) for line in (path/'events.jsonl').read_text().splitlines()]
                measured_start = next(row['timestamp_s'] for row in events if row['event_type'] == 'sampling_started')
                measured_end = next(row['timestamp_s'] for row in events if row['event_type'] == 'sampling_stopped')
                stream_end = math.ceil(measured_end)

                def native_stream(begin, end):
                    documents = []
                    for endpoint in range(int(begin) + 1, int(end) + 1):
                        documents.append(plistlib.dumps({
                            'timestamp': datetime.fromtimestamp(endpoint, timezone.utc).replace(tzinfo=None),
                            'elapsed_ns': 1_000_000_000, 'is_delta': True, 'thermal_pressure': 'Nominal',
                            'processor': {'cpu_power': 100, 'cpu_energy': 100, 'gpu_power': 0,
                                          'gpu_energy': 0, 'ane_power': 0, 'ane_energy': 0}}))
                    return b'\0'.join(documents)

                for attempt in attempts:
                    number = attempt['attempt']
                    suffix = '' if number == 1 else f'_attempt_{number}'
                    (path/'raw'/f'powermetrics_idle{suffix}.plist').write_bytes(
                        native_stream(attempt['start_s'], attempt['end_s']))
                    busy = 0.9 if number == 1 else 0.1
                    rows = [{'timestamp_s': end, 'elapsed_ns': 1_000_000_000,
                             'processor_combined_power_w': 0.1,
                             'clusters': [{'cpus': [{'idle_ratio': 1-busy, 'down_ratio': 0.0}]}]}
                            for end in range(int(attempt['start_s'])+1, int(attempt['end_s'])+1)]
                    (path/f'rich_telemetry_idle{suffix}.jsonl').write_text(
                        ''.join(json.dumps(row)+'\n' for row in rows))
                raw = native_stream(start, stream_end)
                (path/'raw/powermetrics.plist').write_bytes(raw)
                moments = {'pre_spawn': start, 'first_parse': start+1,
                           'sampling_started': measured_start, 'sampling_stopped': measured_end,
                           'post_parse': stream_end+0.01}
                stamps = {name: ClockStamp(value, value, value, 0, 0) for name, value in moments.items()}
                anchor = derive_powermetrics_anchor_v3(stamps=stamps,
                    records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)))
                self.assertEqual(anchor['status'], 'bounded', anchor)
                self.assertEqual(anchor['method'], CLOCK_METHOD_V3)
                metadata['uncertainty_evidence'] = {'clock_anchor': anchor}
                metadata['environment']['post_run_observation'] = {
                    'capture_skipped': False, 'errors': {}, 'captured_at_s': clock.now(),
                    'display_power_state': 'all_asleep', 'screensaver_engaged': False}
                (path/'metadata.json').write_text(json.dumps(metadata)+'\n')
                metadata = json.loads((path/'metadata.json').read_bytes())
                self.assertEqual(environment_admission.current_environment_refusals(metadata,
                    bundle_path=path, measured_window_start_s=measured_start,
                    measured_window_end_s=measured_end), ())


class RetryBackoffClockAnchorTests(unittest.TestCase):
    """The block-3 wait must keep a retried member's stream inside the v3 cap.

    The adapter keeps one sampler from attempt 1 through the measured window,
    so the wait lengthens the stream the clock anchor fits. The v3 method caps
    the effective bound (anchor half-width + wall-minus-monotonic span +
    padding) at 5 ms. Real inputs, from block 2's twelve completed members
    (window d117-g2a-prefill-probe-20261003T1748Z, read by the Fable final pass
    on PR #465): drift about 3.2 ppm, anchor half-width up to 2.31 ms, one idle
    attempt about 104 s of wall time. Synthetic records give a half-width of
    about 0.5 ms, so the test adds the difference to model the widest one.
    At 300 s the estimated longest stream is 683 s and the bound about 4.5 ms;
    the drift tolerance there is about 3.9 ppm.
    No estimator code is mocked.
    """

    DRIFT_PPM = 3.2
    WIDEST_HALF_WIDTH_S = 0.00231
    # Estimated longest retried stream (Qwen3-8B at 4096 prompt tokens). An
    # ESTIMATE, not an enforced worst case: two idle attempts of 104 s wall
    # time each (observed in block 2; the slice deadline allows up to ~123 s),
    # the wait, 45 s for three guards near their command timeouts, two
    # 4096-token prefills assumed <= 10 s each, 516 decoded tokens assumed at
    # >= 5 tokens/s, 5 s settle and 1 s post dwell; sampler start-up, drain and
    # parse are not budgeted. A longer real stream can void a retried member,
    # which fails closed (invalid member, RECOVER), never admits one.
    IDLE_ATTEMPT_S = 104
    GUARDS_S = 45
    PREFILLS_S = 2 * 10
    DECODE_S = 516 / 5
    SETTLE_AND_DWELL_S = 5 + 1

    @staticmethod
    def anchor(length_s, ppm):
        from joulewise.uncertainty_evidence import NativeAnchorRecord
        base = 1_700_000_000
        moments = {'pre_spawn': 0, 'first_parse': 1.001, 'sampling_started': length_s - 1,
                   'sampling_stopped': length_s - 0.5, 'post_parse': length_s + 0.01}
        stamps = {name: ClockStamp(base + t * (1 + ppm * 1e-6), 100 + t, 100 + t + 2e-6, 1e-6, 1e-6)
                  for name, t in moments.items()}
        records = [NativeAnchorRecord(elapsed_s=1.0, native_timestamp_s=base + i + 1, power_w=0.1,
                                      energy_j=0.1, is_delta=True, elapsed_ns=1_000_000_000,
                                      native_timestamp_ns=(base + i + 1) * 1_000_000_000)
                   for i in range(length_s)]
        return derive_powermetrics_anchor_v3(stamps=stamps, records=records)

    @classmethod
    def retried_stream_s(cls, backoff_s=None):
        policy = CampaignPolicy.from_mapping(json.loads((ROOT / G2A_CAMPAIGN_POLICY_PATH).read_bytes()))
        wait = policy.idle_admission.retry_backoff_s if backoff_s is None else backoff_s
        return math.ceil(2 * cls.IDLE_ATTEMPT_S + wait + cls.GUARDS_S + cls.PREFILLS_S
                         + cls.DECODE_S + cls.SETTLE_AND_DWELL_S)

    @classmethod
    def widest_bound_s(cls, anchor):
        return (anchor['effective_clock_anchor_bound_s'] - anchor['anchor_only_bound_s']
                + cls.WIDEST_HALF_WIDTH_S)

    def test_block3_retried_stream_stays_inside_the_cap_at_block2_drift(self):
        anchor = self.anchor(self.retried_stream_s(), self.DRIFT_PPM)
        self.assertEqual(anchor['status'], 'bounded', anchor)
        self.assertEqual(anchor['method'], CLOCK_METHOD_V3)
        self.assertLess(self.widest_bound_s(anchor), 0.0046)

    def test_a_600_second_wait_would_exceed_the_cap_for_the_widest_half_width(self):
        anchor = self.anchor(self.retried_stream_s(600), self.DRIFT_PPM)
        self.assertGreater(self.widest_bound_s(anchor), 0.005)


if __name__ == '__main__':
    unittest.main()
