"""cw-fix adversarial checks. Tiny synthetic observations only; no native probes."""
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import condition_waits as cw, condition_waits_native as native
from joulewise.align.apple import condition_waits_cw1 as kit, condition_waits_ledger as ledger
from joulewise.align.apple.condition_waits_status import battery_record, profile_mode
from tests.align.test_condition_waits import policy, header, rows, sample, stamp, observer_proof, meter_export, BASE


class FixTests(unittest.TestCase):
    def test_every_policy_mode_is_inert_until_bound_native_lead_ruling(self):
        from scripts import align_v4_session as session
        for mode in (False, True):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root = Path(d); reg = root/'configs/campaigns/align_v4/registration'
                reg.mkdir(parents=True)
                frozen = policy(active=mode, q=mode)
                (reg/'condition_waits_policy.json').write_bytes(cw.canonical(frozen))
                (root/'session.json').write_text(json.dumps({'measurement_root': d}))
                with patch.object(session.kit, 'generate', side_effect=AssertionError('too late')):
                    with self.assertRaisesRegex(ValueError, 'INERT'):
                        session.install(root)
                ruling = {'schema': 'joulewise.align.condition_waits.lead_ruling.v1', 'enabled': True,
                    'h1_h7_fixed': True, 'native_dry_arm_passed': True, 'r18_shadow_exposure_passed': True,
                    'policy_sha256': cw.digest(frozen), 'ruled_by': 'synthetic lead',
                    'native_evidence_sha256': 'a'*64, 'observer_accounting': observer_proof()}
                path = reg/'condition_waits_lead_ruling.json'
                path.write_bytes(cw.canonical(ruling))
                cw.require_install_enabled(root)
                for field in ('native_dry_arm_passed', 'r18_shadow_exposure_passed', 'h1_h7_fixed'):
                    bad = {**ruling, field: False}; path.write_bytes(cw.canonical(bad))
                    with self.assertRaisesRegex(ValueError, 'INERT'):
                        cw.require_install_enabled(root)

    def test_no_policy_keeps_install_gate_inert(self):
        with tempfile.TemporaryDirectory() as d:
            cw.require_install_enabled(d)

    def test_committed_packet_builder_replays_receipt_and_emits_exact_binding(self):
        from tests.align.test_v4_next_arm_packet import Scenario
        frozen = policy()
        trace = rows()
        receipt = cw.replay(frozen, header(), trace)
        with tempfile.TemporaryDirectory() as d:
            s = Scenario(d)
            s.quiet = {'schema': 'joulewise.align.condition_waits.evidence.v1',
                       'header': header(), 'rows': trace, 'receipt': receipt}
            s.series['condition_waits_policy'] = s.write('series/wait-policy.json', frozen)
            s.finish()
            entry = s.build(now=BASE+301)['checks']['quiet_start_state']
            self.assertEqual(entry['status'], 'pass', entry['basis'])
            for k, value in {'receipt_sha256': cw.digest(receipt), 'policy_sha256': cw.digest(frozen),
                             'attempt_id': 'synthetic-attempt', 'boot_id': 'synthetic-boot'}.items():
                self.assertEqual(entry[k], value)
            s.quiet['rows'][100]['sensors']['TV0h'] = 50
            s.finish()
            self.assertEqual(s.build(now=BASE+301)['checks']['quiet_start_state']['status'], 'fail')

    def test_retry_reservation_survives_reinstall_and_cannot_reset_to_one(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'series/state.json'; path.parent.mkdir()
            path.write_text(json.dumps({'schema': 'joulewise.align_v4.series_state.v1'}))
            first = dict(window='C1', attempt_id='a1', ambient_check=None, started=stamp(0))
            self.assertEqual(ledger.reserve(path, **first), 1)
            self.assertEqual(ledger.reserve(path, **first), 1)  # same reservation only
            with self.assertRaisesRegex(ValueError, 'unresolved'):
                ledger.reserve(path, **{**first, 'attempt_id': 'a2'})
            receipt = {'attempt_id': 'a1', 'attempt_number': 1, 'status': 'not_ready'}
            ledger.finish(path, 'C1', receipt)
            with self.assertRaises(ValueError): ledger.reserve(path, **first)
            check = {'previous_not_ready_sha256': cw.digest(receipt), 'check_sha256': 'b'*64,
                     'checked_by': 'synthetic', 'checked_at_epoch_s': BASE}
            second = {**first, 'attempt_id': 'a2', 'ambient_check': check}
            self.assertEqual(ledger.reserve(path, **second), 2)
            ledger.finish(path, 'C1', {'attempt_id': 'a2', 'attempt_number': 2, 'status': 'not_ready'})
            check['previous_not_ready_sha256'] = cw.digest({'attempt_id': 'a2', 'attempt_number': 2, 'status': 'not_ready'})
            with self.assertRaisesRegex(ValueError, 'two attempts'):
                ledger.reserve(path, **{**second, 'attempt_id': 'a3'})
            self.assertEqual(len(json.loads(path.read_bytes())['condition_waits_attempts']['C1']), 2)

    def test_native_sampler_has_no_per_tick_commands_or_censuses(self):
        from joulewise.hazards.base import Stamp
        calls = []
        class SMC:
            def read(self, keys):
                return {'values': sample(0)['sensors'], 'errors': {},
                        'raw': {k: {'data_type': 'fpe2' if k.startswith('F') else 'flt '} for k in keys}}
            def close(self): pass
        status = SimpleNamespace(boot='synthetic-boot', close=lambda: None,
            sample=lambda wall: {k: sample(0)[k] for k in (
                'battery', 'display_asleep', 'ac_powermode', 'screensaver_engaged')})
        power = SimpleNamespace(start=lambda: None, close=lambda: None, sample=lambda: {})
        ctx = SimpleNamespace(stamp=lambda: Stamp(**stamp(1)),
                              clocks=SimpleNamespace(monotonic_ns=lambda: cw.NS))
        s = native.NativeSampler(policy(), ctx=ctx, smc=SMC(), status_reader=status,
            notify=SimpleNamespace(read=lambda: 0, close=lambda: None), power=power,
            run=lambda argv: self.fail('per-sample subprocess: '+str(argv)),
            topup_reader=lambda now: calls.append('topup') or sample(0)['topup'],
            setup_check=lambda: calls.append('census') or {'passed': True, 'setup_sha256': '4'*64},
            obc_off_attested_by='synthetic', guard_reader=lambda: [])
        s.start()
        for _ in range(20):
            row = s.sample(attempt_id='synthetic-attempt', boot_id='synthetic-boot')
            self.assertNotIn('raw_ioreg', row)
        self.assertEqual(calls, ['census', 'topup'])
        self.assertTrue(s.release_check())
        self.assertEqual(calls, ['census', 'topup', 'census'])
        s.close()

    def test_observer_accounting_rejects_cost_and_outside_daemon_activation(self):
        clean = [{'outside_processes': [{'pid': 1, 'start': 'same', 'command': 'storagekitd', 'cpu_s_per_s': 0}]}]
        args = dict(cpu_before=0, cpu_after=1, elapsed_s=300, baseline=clean, observed=clean,
                    all_children_reaped=True)
        self.assertTrue(native.observer_accounting(**args)['qualified'])
        for changes in ({'cpu_after': 1.5}, {'all_children_reaped': False},
                        {'observed': [{'outside_processes': [{**clean[0]['outside_processes'][0], 'cpu_s_per_s': .001}]}]}):
            self.assertFalse(native.observer_accounting(**{**args, **changes})['qualified'])
        with self.assertRaises(ValueError):
            native.observer_accounting(**{**args, 'observed': [{'outside_over_limit': []}]})

    def test_float_continues_from_arm_evidence_and_breaks_on_recharging(self):
        trace = rows(1800)
        for r in trace:
            r['topup'] = {'completed_at_epoch_s': BASE-1790, 'source': 'synthetic arm source'}
            r['arm_topup'] = {'admitted_at_epoch_s': BASE}
            r['float_continuity_passed'] = True
        self.assertTrue(cw.replay(policy(), header(), trace[:901])['band_ready'])
        trace[500]['battery']['is_charging'] = True
        self.assertIn('float_continuity_broken', cw.replay(policy(), header(), trace[:901])['reasons'])

    def test_display_wake_does_not_make_older_owner_marker_permanently_fatal(self):
        trace = rows(660)
        trace[10]['display_asleep'] = False
        for r in trace: r['last_disruptive_ns'] = 0
        result = cw.replay(policy(), header(), trace)
        self.assertTrue(result['band_ready'], result['reasons'])
        self.assertNotIn('disruptive_boundary', result['reasons'])

    def test_raw_cooldown_observations_overlap_display_and_quiet_floors(self):
        history = [sample(t) for t in range(-300, 0)]
        h = {**header(), 'quiet_start_ns': -300*cw.NS, 'cooldown_rows': history}
        result = cw.replay(policy(), h, rows(240))
        self.assertTrue(result['band_ready'], result['reasons'])
        self.assertFalse(cw.replay(policy(), header(), rows(240))['band_ready'])
        for r in history: r['boot_id'] = 'other-boot'
        self.assertIn('display_floor', cw.replay(policy(), h, rows(240))['reasons'])

    def test_native_battery_types_and_signed_current(self):
        p = {'ExternalConnected': True, 'IsCharging': False, 'InstantAmperage': 2**64-100,
             'UpdateTime': BASE, 'CurrentCapacity': 100}
        self.assertEqual(battery_record(p, BASE)['instant_amperage_ma'], -100)
        self.assertFalse(battery_record(p, BASE+181)['passed'])
        with self.assertRaises(ValueError): battery_record({**p, 'ExternalConnected': 1}, BASE)
        self.assertEqual(profile_mode({'LowPowerMode': 0, 'HighPowerMode': 1}), 2)
        self.assertEqual(profile_mode({'LowPowerMode': 0, 'HighPowerMode': 0}), 0)
        self.assertIsNone(profile_mode({}))
        self.assertIsNone(profile_mode({'LowPowerMode': 1, 'HighPowerMode': 1}))

    def test_power_cleanup_confirms_reparented_children_and_never_kills_sudo(self):
        import signal
        import subprocess
        from joulewise.align.apple import r1_runtime
        for after, clean in (('', True), ('124 1 powermetrics\n', False)):
            stream = native.PowerStream(SimpleNamespace())
            stream.process = SimpleNamespace(pid=123, wait=lambda **kw: 0,
                                             stdout=SimpleNamespace(close=lambda: None))
            snapshots = [SimpleNamespace(stdout='123 1 sudo powermetrics\n124 123 powermetrics\n'),
                         SimpleNamespace(stdout=after)]
            with patch.object(r1_runtime, 'stop_powermetrics_descendants', return_value=[]), \
                    patch.object(native.subprocess, 'run', side_effect=snapshots), \
                    patch.object(native.os, 'killpg') as kill:
                if clean: stream.close()
                else:
                    with self.assertRaisesRegex(RuntimeError, 'still alive'): stream.close()
                kill.assert_called_once_with(123, signal.SIGTERM)
        stream = native.PowerStream(SimpleNamespace())
        def timeout(**kw): raise subprocess.TimeoutExpired('synthetic sudo', 5)
        stream.process = SimpleNamespace(pid=123, wait=timeout)
        with patch.object(r1_runtime, 'stop_powermetrics_descendants', return_value=[]), \
                patch.object(native.subprocess, 'run', return_value=SimpleNamespace(stdout='')), \
                patch.object(native.os, 'killpg') as kill:
            with self.assertRaisesRegex(RuntimeError, 'did not terminate'): stream.close()
            kill.assert_called_once_with(123, signal.SIGTERM)

    def test_legacy_idle_export_never_invents_missing_channels(self):
        trace = rows(360)
        source = {'header': header(), 'ended_ns': 360*cw.NS,
                  'smc': [{'finished': r['finished'], 'sensors': r['sensors']} for r in trace],
                  'status': trace, 'power_intervals': [p for r in trace for p in r['power_intervals']],
                  'guard_intervals': [g for r in trace for g in r['guard_intervals']]}
        record = kit.export_idle('r1_soak', source)
        idle = {k: [record] for k in kit.IDLE_SOURCES}
        self.assertTrue(kit.guard_replay(policy(), idle)['qualified'])
        missing = kit.export_idle('r0_rerun11_idle', {**source, 'status': []})
        self.assertNotIn('battery', missing['rows'][100])
        self.assertFalse(kit.guard_replay(policy(), {**idle, 'r0_rerun11_idle': [missing]})['qualified'])

    def test_dc_in_is_secondary_and_not_the_q_channel(self):
        report = kit.dc_in_report(meter_export())
        self.assertEqual(report['dc_in_energy_j'], 5)
        self.assertEqual(report['mean_w'], 5)
        self.assertTrue(report['print_only'])
        self.assertEqual(kit.dc_in_report(None)['status'], 'missing')
        self.assertEqual(policy()['q']['power']['channel'], 'processor_combined_power')

    def test_shadow_new_final_checks_and_slow_cleanup_cannot_refuse(self):
        from tests.align.test_condition_waits_arm import NativeArmTests
        case = NativeArmTests(); self.addCleanup(case.doCleanups)
        result, _, _ = case.run_arm(shadow=True, stale_cleanup=True, disturb_final=True)
        self.assertTrue(result.go, result.reasons)

    def test_tick_cost_150_ms_still_releases(self):
        from tests.align import test_condition_waits_arm as harness
        original = harness.Sampler.sample
        def slow(s, **kwargs):
            s.ctx.clocks.sleep(.15)
            return original(s, **kwargs)
        case = harness.NativeArmTests(); self.addCleanup(case.doCleanups)
        with patch.object(harness.Sampler, 'sample', slow):
            result, gate, _ = case.run_arm()
        self.assertTrue(result.go, gate.receipt['reasons'])


if __name__ == '__main__': unittest.main()
