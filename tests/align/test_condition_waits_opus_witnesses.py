"""Failing-first witnesses from the Opus cold review of the R16 implementation.

docs/align/v4/condition-waits-impl-opus-review.md names each finding. Every
test here FAILS on align/2026-11-08-condition-waits-impl @ 4d7e5f9a9 and is the
acceptance check for its fix. Synthetic only: no hardware, weights or records.
"""
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import condition_waits as cw, condition_waits_native as native
from joulewise.hazards.base import Stamp
from tests.align.test_condition_waits import BASE, policy, sample, stamp


class F1PerTickSetupCensus(unittest.TestCase):
    """F1 (HIGH): registered_arm's setup_check runs a mount + diskutil census on
    every 1 Hz sample. Native Air witness: storagekitd (outside the arm tree)
    reached 0.090 CPU-s/s, over the 0.05 guard limit, only while it ran."""

    def test_setup_census_is_not_run_on_every_sample(self):
        calls = []
        captured = {}
        with tempfile.TemporaryDirectory() as d:
            custody = Path(d)
            p = policy(active=False, q=False)          # the fallback policy
            (custody/'condition_waits_inputs.json').write_text(json.dumps({
                'schema': 'joulewise.align.condition_waits.native_inputs.v1',
                'policy_sha256': cw.digest(p), 'attempt_id': 'synthetic-attempt',
                'battery_log': str(custody/'b.jsonl'), 'obc_off_attested_by': 'synthetic'}))
            def capture(config, policy_, h, sampler, **kwargs):
                captured['sampler'] = sampler
                return SimpleNamespace(go=False)
            from joulewise.align.apple import external_volume
            census = lambda run: calls.append('census') or {'mounts': [], 'external': [], 'errors': []}
            with patch.object(native, 'arm_with_start_state', capture), \
                    patch.object(native.NativeSampler, 'boot_id', lambda self: 'synthetic-boot'), \
                    patch.object(external_volume, 'census', census):
                native.registered_arm(SimpleNamespace(custody_dir=str(custody)), p,
                                      attempt_id='synthetic-attempt')
                for _ in range(10):                    # ten 1 Hz samples
                    captured['sampler'].setup_check()
        self.assertLessEqual(len(calls), 1, f'{len(calls)} mount/diskutil censuses in 10 samples')


class F2PowerStreamWholeSecondTimestamps(unittest.TestCase):
    """F2 (HIGH): powermetrics plist <date> is whole-second (see
    joulewise/adapters/powermetrics.py TIMESTAMP_DERIVATION and
    tests/fixtures/d117_v2_production/.../powermetrics_idle.plist); elapsed_ns
    is not exactly 1e9. The 0.1 s drift check then kills the stream."""

    def test_realistic_one_hertz_stream_survives_two_minutes(self):
        stream = native.PowerStream(SimpleNamespace())
        stream.anchor = Stamp(**stamp(0))
        true_end = 0.4                                 # sub-second phase of the first endpoint
        for k in range(120):
            elapsed = 1_004_000_000 if k % 2 else 1_001_000_000
            true_end += elapsed/cw.NS
            whole = datetime.fromtimestamp(int(BASE+true_end), timezone.utc)
            stream.accept({'timestamp': whole, 'elapsed_ns': elapsed,
                           'processor': {'combined_power': 500}, 'thermal_pressure': 'Nominal'})
        self.assertEqual(len(stream.sample()['power_intervals']), 120)


class F3ShadowAttemptHasNoBound(unittest.TestCase):
    """F3 (HIGH): in incumbent_shadow mode run_attempt never reaches not_ready,
    so with the default incumbent_ready it loops past the 1800 s ceiling."""

    def test_shadow_preliminary_attempt_terminates_by_the_ceiling(self):
        class Clock:
            t = 0.0
            def monotonic_ns(self):
                return round(self.t*cw.NS)
            def sleep(self, seconds):
                self.t += seconds
        clock = Clock()
        class Sampler:
            ctx = SimpleNamespace(clocks=clock, stamp=lambda: Stamp(**stamp(clock.t)))
            def start(self):
                pass
            def sample(self, *, attempt_id, boot_id):
                clock.t += .001
                r = sample(round(clock.t))
                r.update(started=stamp(clock.t), finished=stamp(clock.t))
                return r
            def close(self):
                pass
        h = dict(attempt_id='synthetic-attempt', boot_id='synthetic-boot', started=stamp(0),
                 quiet_start_ns=0)
        guard = lambda: clock.t > 2400                 # 600 s past the ceiling
        try:
            result = native.run_attempt(policy(active=False, q=False), h, Sampler(),
                                        journal=StringIO(), trace=StringIO(),
                                        final_checks=lambda: True, cancelled=guard)
        except InterruptedError:
            self.fail('shadow attempt still waiting 600 s after the 1800 s ceiling')
        self.assertIn(result['status'], ('released', 'not_ready'))


class F4ArmTickCadenceDefeatsCoverage(unittest.TestCase):
    """F4 (HIGH): run_dwell sleeps a full tick AFTER on_tick, so the joint
    sample period is 1 s + sample cost. Above ~10 ms the 99 % one-second-cell
    coverage can never hold and the native arm runs to the 1800 s ceiling.
    The native sources alone (two ioreg, pmset, pgrep, sysctl, SMC) cost
    ~50 ms on the Air, before F1's ~0.7-0.9 s census."""

    def test_native_arm_releases_with_a_realistic_50_ms_sample(self):
        from tests.align import test_condition_waits_arm as harness
        original = harness.Sampler.sample
        def realistic(self, *, attempt_id, boot_id):
            self.ctx.clocks.sleep(.05)
            return original(self, attempt_id=attempt_id, boot_id=boot_id)
        with patch.object(harness.Sampler, 'sample', realistic):
            case = harness.NativeArmTests('test_native_guard_and_band_share_one_interval_before_go')
            result, gate, _sampler = case.run_arm()
        self.assertTrue(result.go, (result.refused_at, gate.receipt and gate.receipt['reasons']))


class F6TopupGoesStaleOnceTheBatterySamplerStops(unittest.TestCase):
    """F6 (HIGH): the frozen quiet_start_state row stops the between-window
    battery sampler before the dwell; v4_topup refuses a latest row older than
    300 s; R16 re-derives top-up on every sample and its floor is >= 300 s
    after dwell start. A condition release therefore can never occur."""

    def test_registered_topup_reader_admits_after_the_sampler_has_stopped(self):
        from joulewise.align.apple import v4_topup
        captured = {}
        with tempfile.TemporaryDirectory() as d:
            custody = Path(d)
            log = custody/'battery.jsonl'
            rows = [{'schema': v4_topup.SCHEMA, 'probe_error': False, 'wall_time_s': BASE+t,
                     'external_connected': True, 'is_charging': t == 0,
                     'current_capacity_pct': 98 if t == 0 else 100} for t in range(0, 601, 60)]
            log.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            p = policy(active=False, q=False)
            (custody/'condition_waits_inputs.json').write_text(json.dumps({
                'schema': 'joulewise.align.condition_waits.native_inputs.v1',
                'policy_sha256': cw.digest(p), 'attempt_id': 'synthetic-attempt',
                'battery_log': str(log), 'obc_off_attested_by': 'synthetic'}))
            def capture(config, policy_, h, sampler, **kwargs):
                captured['sampler'] = sampler
                return SimpleNamespace(go=False)
            with patch.object(native, 'arm_with_start_state', capture), \
                    patch.object(native.NativeSampler, 'boot_id', lambda self: 'synthetic-boot'):
                native.registered_arm(SimpleNamespace(custody_dir=str(custody)), p,
                                      attempt_id='synthetic-attempt')
            topup = captured['sampler'].topup_reader
            self.assertIsNotNone(topup(BASE+600+60), 'control: fresh log admits')
            # Sampler stopped at BASE+600 (before the dwell); R16 floor ends >= 300 s later.
            self.assertIsNotNone(topup(BASE+600+301), 'top-up refused at the earliest R16 release')


class F7SameRunReferenceCannotQualify(unittest.TestCase):
    """F7 (HIGH, part b): the agreement (D3/D11) lets CW-1's soak supply Q when
    R1 changed mode or picks. execute_kit records band_sha256 from the policy it
    ran under (condition_waits_cw1.py:195); parse_run requires that to equal the
    parsing policy's band (:167). A Q frozen from the same run's soak always
    changes the band, so one authorized CW-1 can never qualify that Q."""

    def test_reference_capture_run_can_qualify_its_own_frozen_q(self):
        from joulewise.align.apple import condition_waits_cw1 as kit
        from tests.align.test_condition_waits import q_reference
        capture = policy(active=False, q=False)        # Q absent during the reference capture
        frozen = cw.registration_policy(cohort='synthetic-v4', q=q_reference(), cw1=None,
                                         incumbent_policy_sha256='a'*64)
        run = {'schema': kit.CW1, 'band_sha256': capture['band_sha256'], 'r1_sha256': '2'*64,
               'recoveries': {}}
        report = kit.parse_run(frozen, run, {})
        self.assertEqual(run['band_sha256'], report['band_sha256'],
                         'the run recorded under the capture policy can never match the frozen-Q band')


class F5PacketBuilderEmitsNoReceiptBinding(unittest.TestCase):
    """F5 (HIGH, integration): on the v4 head the arm rebuilds the packet and
    judges its own build. That builder's quiet() emits no receipt fields, so an
    R16 policy refuses every arm. Runs only after the v4-head merge."""

    def test_rebuilt_quiet_entry_can_carry_the_receipt_binding(self):
        try:
            from scripts import align_v4_next_arm_packet as builder
        except ImportError:
            self.skipTest('pre-merge tree: v4-head packet builder absent')
        import inspect
        source = inspect.getsource(builder)
        quiet = source[source.index('    def quiet():'):source.index('    def meter_coverage():')]
        for field in ('receipt_sha256', 'policy_sha256', 'attempt_id', 'boot_id'):
            self.assertIn(field, quiet, 'packet builder quiet() never emits ' + field)


if __name__ == '__main__':
    unittest.main()
