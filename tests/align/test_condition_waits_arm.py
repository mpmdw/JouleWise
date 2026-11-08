"""The real native arm/dwell with synthetic clocks, SMC/status and CPU table."""
from io import StringIO
from pathlib import Path
import tempfile
import unittest
import json
import subprocess
import sys
import types
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.align.apple import condition_waits as cw, condition_waits_native as native
from joulewise.hazards import arm, base
from tests.align.test_condition_waits import policy, sample
from tests.hazards.test_arm import Rig
from tests.hazards.fakes import BOOT_UUID


class Sampler:
    def __init__(self, ctx, *, disturb_final=False, stale_cleanup=False):
        self.ctx = ctx
        self.last = None
        self.closed = False
        self.disturb_final, self.stale_cleanup = disturb_final, stale_cleanup

    def start(self):
        self.start_ns = self.ctx.clocks.monotonic_ns()
        self.topup_epoch = self.ctx.stamp().wall_ns/cw.NS

    def boot_id(self):
        return BOOT_UUID

    def sample(self, *, attempt_id, boot_id):
        self.ctx.clocks.sleep(.001)
        s = self.ctx.stamp().to_json()
        now = s['monotonic_ns']
        r = sample(0)
        r.update(attempt_id=attempt_id, boot_id=boot_id, started=s, finished=s,
                 pm_observed_ns=now, battery_observed_ns=now,
                 topup={'completed_at_epoch_s': self.topup_epoch, 'source': 'synthetic charge log'},
                 power_intervals=[{'start_ns': self.last if self.last is not None else self.start_ns,
                                   'end_ns': now, 'watts': .5}], guard_intervals=[])
        if self.disturb_final and self.last is not None and now-self.last < cw.NS//10:
            r['sensors']['F0Ac'] = 20
        self.last = now
        return r

    def close(self):
        self.closed = True
        if self.stale_cleanup:
            self.ctx.clocks.sleep(3)


class NativeArmTests(unittest.TestCase):
    def run_arm(self, *, disturb_final=False, stale_cleanup=False, census_dirty=False, shadow=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        rig = Rig(Path(tmp.name))
        if census_dirty:
            rig.census = (0, b'1 codex\n')
        ctx = base.Context(run=rig.runner, clocks=rig.clocks)
        sampler = Sampler(ctx, disturb_final=disturb_final, stale_cleanup=stale_cleanup)
        h = {'attempt_id': 'synthetic-native-arm', 'boot_id': BOOT_UUID,
             'started': ctx.stamp().to_json(), 'quiet_start_ns': ctx.clocks.monotonic_ns()}
        config = rig.config(thresholds=arm.default_thresholds())
        gate = native.ArmWait(policy(active=not shadow, q=not shadow), h, sampler,
                              journal=StringIO(), trace=StringIO(), incumbent_ready=lambda: shadow)
        # Rig.run drives the native instrument against a tiny committed fake.
        # Instrument collection is independent of R16. Stub it at its native
        # seam as well: sandbox process-group census cannot inspect the host.
        def measured(*args, **kwargs):
            s = ctx.stamp()
            return base.Measurement('instrument', 'probe', {}, (), s, s, None)
        with patch.object(arm.instrument, 'measure', side_effect=measured), patch.object(
                arm.instrument, 'judge', return_value=base.Verdict('instrument', base.PASS, (), {}, {})):
            result = rig.run(thresholds=config.thresholds, start_state=gate)
        return result, gate, sampler

    def test_native_guard_and_band_share_one_interval_before_go(self):
        result, gate, sampler = self.run_arm()
        self.assertTrue(result.go, result.reasons)
        receipt = result.document['condition_waits']
        self.assertTrue(receipt['go'])
        elapsed = (receipt['finished']['monotonic_ns']-receipt['quiet_start_ns'])/cw.NS
        self.assertGreaterEqual(elapsed, 300)
        self.assertLess(elapsed, 340)  # neither an added 180 nor another display dwell
        self.assertTrue(sampler.closed)
        rows = [__import__('json').loads(line) for line in gate.trace.getvalue().splitlines()]
        self.assertEqual(cw.replay(policy(), gate.header, rows), receipt)

    def test_final_read_disturbance_cannot_go(self):
        result, _gate, sampler = self.run_arm(disturb_final=True)
        self.assertFalse(result.go)
        self.assertEqual(result.refused_at, 'condition_waits')
        self.assertTrue(sampler.closed)

    def test_slow_cleanup_cannot_authorize_stale_go(self):
        result, _gate, _sampler = self.run_arm(stale_cleanup=True)
        self.assertFalse(result.go)
        self.assertIn('stale after native cleanup', result.reasons[0])

    def test_early_arm_refusal_never_starts_collectors(self):
        result, gate, sampler = self.run_arm(census_dirty=True)
        self.assertFalse(result.go)
        self.assertIsNone(gate.receipt)
        self.assertTrue(sampler.closed)

    def test_unqualified_shadow_keeps_the_incumbent_native_guard_duration(self):
        result, gate, _sampler = self.run_arm(shadow=True)
        self.assertTrue(result.go, result.reasons)
        self.assertFalse(gate.receipt['band_ready'])
        elapsed = (gate.receipt['finished']['monotonic_ns']-gate.receipt['started']['monotonic_ns'])/cw.NS
        self.assertGreaterEqual(elapsed, 180)
        self.assertLess(elapsed, 210)

    def test_driver_selects_registered_native_entry_only_for_explicit_align_policy(self):
        from joulewise.b5 import driver
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            pack = root/'align-v4'
            pack.mkdir()
            context = SimpleNamespace(
                plan=SimpleNamespace(measurement_root=str(root), plan_id='synthetic-driver'),
                record_root=root/'hazards', disk_targets=[], measurement_tree_pids=(4000,),
                record_only_argv=(), thresholds=arm.default_thresholds(),
                planned_bytes=0, t_stream_max_s=1000,
                hazard_window={'pack': {'pack_id': 'align-v4', 'pack_root': str(pack)}})
            result = SimpleNamespace(go=True, document={}, reasons=(), refused_at=None, path=root/'arm.json')
            for frozen in (None, policy()):
                (pack/'collection_plan.json').write_text(json.dumps({
                    'runtime_requirements': {'condition_waits': frozen} if frozen else {}}))
                with patch.object(arm, 'run', return_value=result) as ordinary, patch.object(
                        native, 'registered_arm', return_value=result) as registered:
                    self.assertTrue(driver._production_arm(context)['go'])
                    self.assertEqual(registered.call_count, int(frozen is not None))
                    self.assertEqual(ordinary.call_count, int(frozen is None))

    def test_disabled_dwell_hooks_are_byte_identical_to_the_pinned_base(self):
        from tests.hazards.test_arm_dwell_clean_run import machine
        from joulewise.hazards import contention
        # Read code objects only from the allowed Git store, never telemetry.
        source = subprocess.run(['git', 'show',
            'origin/align/2026-11-08-v4-r11:joulewise/hazards/contention.py'],
            cwd=Path(__file__).resolve().parents[2], check=True, capture_output=True).stdout
        reference = types.ModuleType('synthetic_cw_reference_contention')
        sys.modules[reference.__name__] = reference
        self.addCleanup(sys.modules.pop, reference.__name__)
        exec(compile(source, '<pinned-repository-contention>', 'exec'), reference.__dict__)
        for scenario in ('quiet', 'burst', 'persistent'):
            results = []
            for implementation in (reference, contention):
                _clock, table, ctx = machine()
                if scenario == 'burst':
                    table.processes[360].schedule = [(60.0, 90.0, .368)]
                if scenario == 'persistent':
                    table.processes[340].cpu_per_s = .06
                measurement = implementation.run_dwell(ctx, arm.default_thresholds()['contention'],
                                                       tree_roots=[4000], host_reader=None)
                results.append(cw.canonical(measurement.to_json()))
            self.assertEqual(*results, scenario)


if __name__ == '__main__':
    unittest.main()
