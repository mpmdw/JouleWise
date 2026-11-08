"""Synthetic R16 tests. No hardware, model weights, network or study records."""
from copy import deepcopy
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import json
import plistlib
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import condition_waits as cw
from joulewise.align.apple import condition_waits_cw1 as char
from joulewise.align.apple import condition_waits_native as native
from joulewise.hazards.base import Stamp

BASE = 10000


def stamp(t):
    return {'monotonic_ns': round(t*cw.NS), 'monotonic_raw_ns': round(t*cw.NS),
            'wall_ns': round((BASE+t)*cw.NS)}


def q_reference():
    return {'schema': 'joulewise.align.condition_waits.q.v1', 'qualified': True,
        'reference_authority': 'synthetic prospective reference ruling', 'reference_seconds': 1200,
        'source_sha256': '1'*64, 'r1_sha256': '2'*64, 'classification_sha256': '3'*64,
        'setup_sha256': '4'*64, 'ac_powermode': 2,
        'temperatures': {'fast': {'key': 'TV0h', 'aliases': ['TV1h'], 'unit': 'degC',
                                    'decoder': 'flt ', 'q': 35, 'sd': .1, 'delta': 1},
                         'slow': {'key': 'Tf08', 'unit': 'degC', 'decoder': 'flt ',
                                  'q': 30, 'sd': .1, 'delta': 1}},
        'fans': {'F0Ac': {'q': 0, 'sd': 0, 'unit': 'rpm', 'decoder': 'fpe2'},
                 'F1Ac': {'q': 1000, 'sd': 50, 'unit': 'rpm', 'decoder': 'fpe2'}},
        'power': {'channel': 'processor_combined_power', 'unit': 'W',
                  'decoder': 'powermetrics.processor.combined_power_mW/1000',
                  'q': .5, 'sd': .02, 'idle_upper_w': 1},
        'display_decoder': 'IODisplayWrangler.CurrentPowerState<=1'}


def policy(active=True, q=True):
    p = cw.registration_policy(cohort='synthetic-v4', q=q_reference() if q else None,
                                cw1=None, incumbent_policy_sha256='a'*64)
    if active:
        proof = {'qualified': True, 'band_sha256': p['band_sha256'], 'evidence_sha256': 'b'*64,
                 'guard_replay': {'qualified': True}}
        p = cw.registration_policy(cohort='synthetic-v4', q=p['q'], cw1=proof,
                                    incumbent_policy_sha256='a'*64)
    return p


def header(**overrides):
    return dict(attempt_id='synthetic-attempt', boot_id='synthetic-boot', started=stamp(0),
                quiet_start_ns=0, **overrides)


def interval(a, b, clean=True, **extra):
    return {'interval': {'monotonic_ns': [round(a*cw.NS), round(b*cw.NS)]}, 'clean': clean,
            'error': None, 'outside_over_limit': [], 'aggregate_over_limit': False,
            'unaccounted': [], **extra}


def sample(t):
    return {'schema': cw.SAMPLE, 'attempt_id': 'synthetic-attempt', 'boot_id': 'synthetic-boot',
        'started': stamp(t), 'finished': stamp(t),
        'sensors': {'TV0h': 35, 'Tf08': 30, 'F0Ac': 0, 'F1Ac': 1000},
        'power_intervals': [{'start_ns': round((t-1)*cw.NS), 'end_ns': round(t*cw.NS), 'watts': .5}] if t else [],
        'os_level': 0, 'pm_state': 'Nominal', 'pm_observed_ns': round(t*cw.NS),
        'ac_powermode': 2, 'setup_sha256': '4'*64, 'display_asleep': True,
        'screensaver_engaged': False, 'final_checks_passed': True,
        'battery': {'passed': True, 'probe_error': False, 'external_connected': True,
                    'is_charging': False, 'update_age_s': 0, 'current_capacity_pct': 100,
                    'instant_amperage_ma': 0},
        'battery_observed_ns': round(t*cw.NS), 'obc_off_attested_by': 'synthetic operator',
        'topup': {'completed_at_epoch_s': BASE, 'source': 'synthetic completed-charge log'},
        'guard_intervals': [interval(t-30, t)] if t and t % 30 == 0 else []}


def rows(end=300):
    return [sample(t) for t in range(end+1)]


def evaluate(trace, p=None, h=None):
    return cw.replay(p or policy(), h or header(), trace)


class PolicyTests(unittest.TestCase):
    def test_kit_embeds_explicit_fallback_and_refuses_q_in_pending_r1_mode(self):
        from scripts import align_v4_kit as kit
        root = Path(__file__).resolve().parents[2]
        frozen = policy(active=False, q=False)
        locator = root/kit.KIT/'registration/condition_waits_policy.json'
        original_read = Path.read_bytes
        def read(path):
            return cw.canonical(frozen) if path == locator else original_read(path)
        with patch.object(kit, 'read_condition_waits_policy', return_value=frozen), patch.object(Path, 'read_bytes', read):
            built = kit.build_files(root)
        plan = json.loads(built[kit.KIT/'collection_plan.json'])
        self.assertEqual(plan['runtime_requirements']['condition_waits'], frozen)
        with patch.object(kit, 'read_condition_waits_policy', return_value=policy()):
            with self.assertRaisesRegex(ValueError, 'final R1 series AC powermode'):
                kit.build_files(root)

    def test_registration_fallback_is_cohort_frozen_and_no_timer_is_invented(self):
        p = policy(active=False, q=False)
        self.assertEqual(p['mode'], 'incumbent_shadow')
        self.assertIsNone(p['q'])
        self.assertNotIn('incumbent_seconds', p)
        self.assertEqual(policy(active=False)['mode'], 'incumbent_shadow')
        self.assertEqual(policy()['mode'], 'condition')
        with self.assertRaises(ValueError):
            cw.registration_policy(cohort='x', q=None, cw1=None, incumbent_policy_sha256=None)

    def test_missing_and_ambiguous_channels_are_not_qualified(self):
        for modify in (lambda q: q['fans'].clear(),
                       lambda q: q['temperatures']['slow'].update(key='TV1h'),
                       lambda q: q['power'].update(channel='km003c'),
                       lambda q: q.update(ac_powermode=1),
                       lambda q: q.update(reference_seconds=1199),
                       lambda q: q.update(classification_sha256=None),
                       lambda q: q['power'].update(q=0)):
            q = q_reference()
            modify(q)
            with self.assertRaises(ValueError):
                cw.validate_q(q)

    def test_digest_covers_band_guard_mode_and_final_sensor_picks(self):
        p = policy()
        for modify in (lambda p: p['q']['temperatures']['slow'].update(delta=2),
                       lambda p: p['q'].update(ac_powermode=0),
                       lambda p: p['guard'].update(clean_s=120)):
            broken = deepcopy(p)
            modify(broken)
            with self.assertRaises(ValueError):
                cw.validate_policy(broken)

    def test_one_retry_requires_ambient_receipt_then_lead(self):
        with self.assertRaises(ValueError):
            cw.Attempt(policy(), **header(attempt_number=2))
        ambient = {'previous_not_ready_sha256': 'a'*64, 'check_sha256': 'b'*64,
                   'checked_by': 'synthetic magistrate', 'checked_at_epoch_s': BASE}
        cw.Attempt(policy(), **header(attempt_number=2, ambient_check=ambient))
        with self.assertRaises(ValueError):
            cw.Attempt(policy(), **header(attempt_number=3, ambient_check=ambient))


class EvaluatorTests(unittest.TestCase):
    def test_joint_release_at_300_not_300_plus_180(self):
        self.assertFalse(evaluate(rows(299))['band_ready'])
        result = evaluate(rows(300))
        self.assertEqual(result['status'], 'released')
        self.assertTrue(result['band_ready'])
        self.assertEqual(result['guard_clean_from_ns'], 0)

    def test_exact_ceiling_and_after_ceiling_never_arm(self):
        trace = rows(1800)
        for r in trace:
            r['sensors']['Tf08'] = 40
        for t in range(1560, 1801):
            trace[t]['sensors']['Tf08'] = 30
        result = evaluate(trace)
        self.assertEqual(result['status'], 'not_ready')
        self.assertIn('ceiling', result['reasons'])
        self.assertFalse(result['go'])
        self.assertEqual(result['next_action'], 'ambient_check_then_one_retry')

    def test_warm_and_cold_are_both_rejected(self):
        for v in (33.9, 36.1):
            trace = rows()
            for r in trace:
                r['sensors']['TV0h'] = v
            self.assertIn('temperature:TV0h', evaluate(trace)['reasons'])

    def test_band_edges_inclusive(self):
        trace = rows()
        for r in trace:
            r['sensors'].update(TV0h=34, Tf08=31, F1Ac=1150)
        self.assertTrue(evaluate(trace)['band_ready'])

    def test_reexit_resets_physical_stability(self):
        trace = rows(480)
        trace[300]['sensors']['TV0h'] = 38
        self.assertFalse(evaluate(trace[:480])['band_ready'])
        self.assertFalse(evaluate(trace)['band_ready'])  # only 179 s good since 301
        self.assertTrue(evaluate(rows(300))['band_ready'])

    def test_slope_uses_actual_times_and_slow_sensor(self):
        trace = rows()
        for r in trace:
            t = r['finished']['monotonic_ns']/cw.NS
            r['sensors']['Tf08'] = 29+t*.21/60
        self.assertIn('slow_slope', evaluate(trace)['reasons'])

    def test_stopped_and_running_fans_missing_power_and_idle_ceiling(self):
        for key, value in (('F0Ac', 1), ('F1Ac', 800), ('F0Ac', None)):
            trace = rows()
            trace[-1]['sensors'][key] = value
            self.assertIn('fan:'+key, evaluate(trace)['reasons'])
        for modify in (lambda r: r.update(power_intervals=[]),
                       lambda r: r['power_intervals'][0].update(watts=1.2)):
            trace = rows()
            for r in trace[1:]:
                modify(r)
            self.assertIn('power', evaluate(trace)['reasons'])

    def test_power_is_duration_weighted_and_requires_full_interval(self):
        segments = [{'start_ns': 0, 'end_ns': 10*cw.NS, 'watts': .2},
                    {'start_ns': 10*cw.NS, 'end_ns': 30*cw.NS, 'watts': .8}]
        self.assertAlmostEqual(cw._mean_power(segments, 30*cw.NS), .6)
        self.assertIsNone(cw._mean_power(segments[1:], 30*cw.NS))
        self.assertIsNone(cw._mean_power(segments+segments, 30*cw.NS))

    def test_disruption_resets_floor_but_does_not_extend_attempt(self):
        trace = rows(600)
        trace[299]['last_disruptive_ns'] = 299*cw.NS
        self.assertFalse(evaluate(trace[:599])['band_ready'])
        # At 600 the unchanged guard boundary and new 300 s floor both hold.
        self.assertTrue(evaluate(trace)['band_ready'])
        late = rows(1800)
        late[1790]['last_disruptive_ns'] = 1790*cw.NS
        self.assertEqual(evaluate(late)['status'], 'not_ready')

    def test_display_wake_unknown_screensaver_and_reset(self):
        for field, value in (('display_asleep', None), ('display_asleep', False),
                             ('screensaver_engaged', True)):
            trace = rows()
            trace[-1][field] = value
            self.assertFalse(evaluate(trace)['band_ready'])
        trace = rows(600)
        trace[299]['display_asleep'] = False
        self.assertTrue(evaluate(trace)['band_ready'])

    def test_one_missing_cell_allowed_large_gap_rejected(self):
        trace = rows()
        # The independent PM stream retains complete intervals across a missed
        # SMC/status tick; a power coverage gap must still refuse.
        trace[201]['power_intervals'] = trace[200]['power_intervals'] + trace[201]['power_intervals']
        del trace[200]
        self.assertTrue(evaluate(trace)['band_ready'])
        trace = rows()
        del trace[200:203]
        self.assertFalse(evaluate(trace)['band_ready'])

    def test_clock_reset_sleep_wall_step_and_bad_brackets_are_terminal(self):
        for change in (lambda r: r['finished'].update(monotonic_ns=1),
                       lambda r: r['finished'].update(monotonic_raw_ns=500*cw.NS),
                       lambda r: r['finished'].update(wall_ns=(BASE+500)*cw.NS),
                       lambda r: r.update(started=stamp(303))):
            trace = rows()
            change(trace[-1])
            self.assertEqual(evaluate(trace)['status'], 'not_ready')
        trace = rows()
        trace[-1]['finished'] = {}
        self.assertEqual(evaluate(trace)['status'], 'not_ready')

    def test_stale_pm_battery_mode_and_setup_refuse(self):
        for field, value in (('pm_observed_ns', 297*cw.NS), ('pm_state', None), ('os_level', 1),
                             ('battery_observed_ns', 297*cw.NS), ('ac_powermode', 0),
                             ('setup_sha256', 'f'*64), ('final_checks_passed', False)):
            trace = rows()
            trace[-1][field] = value
            self.assertFalse(evaluate(trace)['band_ready'])
        for battery in ({'update_age_s': 181}, {'is_charging': True}, {'external_connected': False},
                        {'current_capacity_pct': 98}, {'instant_amperage_ma': 201}):
            trace = rows()
            trace[-1]['battery'].update(battery)
            self.assertIn('battery', evaluate(trace)['reasons'])

    def test_topup_expiry_at_actual_go_is_not_a_fresh_ioreg_read(self):
        trace = rows()
        trace[-1]['topup']['completed_at_epoch_s'] = BASE-1501
        self.assertIn('battery', evaluate(trace)['reasons'])

    def test_dirty_and_counter_regressed_native_intervals_cannot_share_clean_time(self):
        for clean, extra in ((False, {}), (None, {'error': contention_error(),
                    'unaccounted': [{'reason': 'counter regressed'}]})):
            trace = rows()
            trace[180]['guard_intervals'] = [interval(150, 180, clean, **extra)]
            self.assertFalse(evaluate(trace)['band_ready'])

    def test_fallback_does_not_wait_for_missing_or_failed_band(self):
        trace = rows(10)
        trace[-1].update(go=True, incumbent_ready=True)
        result = evaluate(trace, policy(active=False, q=False))
        self.assertTrue(result['go'])
        self.assertFalse(result['band_ready'])
        trace = rows(1801)
        trace[-1].update(go=True, incumbent_ready=True)
        result = evaluate(trace, policy(active=False, q=False))
        self.assertTrue(result['go'])  # no new 1800 s deadline for incumbent

    def test_final_go_is_recomputed_and_closed(self):
        attempt = cw.Attempt(policy(), **header())
        for r in rows():
            result = attempt.feed(r)
        self.assertTrue(result['band_ready'])
        final = sample(300.01)
        final['power_intervals'] = []
        self.assertTrue(attempt.feed(final, go=True)['go'])
        with self.assertRaises(ValueError):
            attempt.feed(sample(301))
        trace = rows()
        trace[-1].update(go=True, final_checks_passed=False)
        self.assertFalse(evaluate(trace)['go'])

    def test_receipt_replay_byte_identity_tampering_and_attempt_boot_binding(self):
        trace = rows()
        trace[-1]['go'] = True
        p, h = policy(), header()
        receipt = evaluate(trace, p, h)
        self.assertEqual(cw.canonical(receipt), cw.canonical(evaluate(deepcopy(trace), p, h)))
        entry = {'receipt_sha256': cw.digest(receipt), 'policy_sha256': cw.digest(p),
                 'attempt_id': h['attempt_id'], 'boot_id': h['boot_id']}
        self.assertTrue(cw.verify_binding(p, h, trace, receipt, entry, at_ns=301*cw.NS))
        self.assertFalse(cw.verify_binding(p, h, trace, receipt, entry, at_ns=303*cw.NS))
        trace[200]['sensors']['F0Ac'] = 1
        self.assertFalse(cw.verify_binding(p, h, trace, receipt, entry))
        entry['attempt_id'] = 'old-attempt'
        self.assertFalse(cw.verify_binding(p, h, rows(), receipt, entry))


def contention_error():
    from joulewise.hazards.contention import REGRESSED_COUNTER_ERROR
    return REGRESSED_COUNTER_ERROR


class CharacterizationTests(unittest.TestCase):
    def test_kit_orchestrator_observes_both_full_recoveries_and_closes_sources(self):
        class Clock:
            t = 0
            def monotonic_ns(self):
                return round(self.t*cw.NS)
            def sleep(self, seconds):
                self.t += seconds
        clock = Clock()
        asleep = [True]
        class Sources:
            ctx = SimpleNamespace(clocks=clock, stamp=lambda: Stamp(**stamp(clock.t)))
            channels = q_reference()
            closed = False
            def start(self):
                pass
            def boot_id(self):
                return 'synthetic-boot'
            def sample(self, *, attempt_id, boot_id):
                r = sample(clock.t)
                r.update(attempt_id=attempt_id, boot_id=boot_id, display_asleep=asleep[0])
                return r
            def close(self):
                self.closed = True
        s, saved, pulses = Sources(), [], []
        k = char.run_kit(python='python3', r0_config='synthetic.json', output='synthetic',
                        r1_sha256='2'*64, reference_authority='synthetic ruling')
        def pulse(phase):
            pulses.append(phase['phase'])
            return SimpleNamespace(poll=lambda: 0)
        def transition(which):
            asleep[0] = which == 'sleep'
            return True
        result = char.execute_kit(k, policy(), s, pulse=pulse, preflight=lambda: True,
            display_transition=transition, final_checks=lambda: True, journal=StringIO(), save=saved.append,
            observer_cost=lambda: .001)
        self.assertTrue(s.closed)
        self.assertEqual(pulses, ['pulse_d', 'pulse_finalize'])
        self.assertEqual(result['status'], 'complete')
        self.assertTrue(result['display_transition_observed'])
        for record in result['recoveries'].values():
            self.assertEqual((record['rows'][-1]['finished']['monotonic_ns']-
                              record['header']['quiet_start_ns'])/cw.NS, 1800)
        self.assertEqual(result['observer_cpu_s_per_s'], .001)
        self.assertEqual(len(saved), 1)

    def test_kit_is_two_hours_bounded_two_pulses_batch_one_no_scoring(self):
        k = char.run_kit(python='python3.13', r0_config='synthetic-config.json', output='synthetic',
                        r1_sha256='2'*64, reference_authority='synthetic ruling')
        self.assertLessEqual(sum(p.get('cap_s', p.get('duration_s')) for p in k['phases']), 7200)
        rec = [p for p in k['phases'] if p['phase'].startswith('recovery')]
        self.assertEqual([p['duration_s'] for p in rec], [1800, 1800])
        argv = next(p['argv'] for p in k['phases'] if p['phase'] == 'pulse_d')
        self.assertIn('joulewise.align.r0_runner', argv)
        self.assertEqual(argv[argv.index('--long-decode-attempts')+1], '1')

    def test_candidate_reference_missing_short_and_valid(self):
        self.assertFalse(char.q_candidates(q_reference(), rows())['qualified'])
        result = char.q_candidates(q_reference(), rows(1200))
        self.assertTrue(result['qualified'], result)
        self.assertFalse(result['registration_authority'])
        self.assertEqual(result['candidates']['temperatures']['slow']['delta_candidate'], 1)

    def test_recovery_requires_full_horizon_no_reexits_and_post_release_evidence(self):
        self.assertFalse(char.recovery(policy(), header(), rows(1000))['qualified'])
        self.assertTrue(char.recovery(policy(), header(), rows(1800))['qualified'])
        bad = rows(1800)
        bad[900]['sensors']['TV0h'] = 40
        result = char.recovery(policy(), header(), bad)
        self.assertFalse(result['qualified'])
        self.assertTrue(result['reexits'])
        for r in bad:
            r['sensors']['TV0h'] = 50
        self.assertTrue(char.recovery(policy(), header(), bad)['right_censored'])

    def test_idle_replay_requires_all_sources_and_zero_holds(self):
        p = policy()
        self.assertFalse(char.guard_replay(p, {})['qualified'])
        record = {'header': header(), 'rows': rows(360)}
        traces = {key: [deepcopy(record)] for key in char.IDLE_SOURCES}
        self.assertTrue(char.guard_replay(p, traces)['qualified'])
        traces['r1_soak'][0]['rows'] = rows(1800)
        self.assertTrue(char.guard_replay(p, traces)['qualified'])  # ceiling isn't an eligible arm instant
        traces['r1_soak'][0]['rows'][330]['sensors']['TV0h'] = 40
        self.assertFalse(char.guard_replay(p, traces)['qualified'])

    def test_parser_requires_cpu_cost_final_reads_r1_and_two_recoveries(self):
        p = policy()
        record = {'header': header(), 'rows': rows(1800)}
        run = {'schema': char.CW1, 'r1_sha256': '2'*64, 'band_sha256': p['band_sha256'],
               'elapsed_s': 6900, 'observer_cpu_s_per_s': .004,
               'final_reads_undisturbed': True, 'pulse_d_r0_passed': True,
               'display_transition_observed': True, 'recoveries': {
                   'recovery_d': record, 'recovery_finalize': record}, 'soak': []}
        idle = {key: [{'header': header(), 'rows': rows(330)}] for key in char.IDLE_SOURCES}
        self.assertTrue(char.parse_run(p, run, idle)['qualified'])
        for key, value in (('observer_cpu_s_per_s', None), ('observer_cpu_s_per_s', .006),
                           ('elapsed_s', 7201), ('r1_sha256', 'f'*64),
                           ('final_reads_undisturbed', False), ('pulse_d_r0_passed', False)):
            broken = {**run, key: value}
            self.assertFalse(char.parse_run(p, broken, idle)['qualified'])

    def test_synthetic_standin_hash_and_compressed_bytes_are_identical(self):
        from scripts.align_v4_condition_waits import finalize_standin
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/'a', Path(d)/'b'
            self.assertEqual(finalize_standin(a, blocks=1), finalize_standin(b, blocks=1))
            self.assertEqual((a/'offload.gz').read_bytes(), (b/'offload.gz').read_bytes())


class NativeSourceTests(unittest.TestCase):
    def test_power_uses_native_endpoints_not_delivery_time(self):
        from datetime import datetime, timezone
        stream = native.PowerStream(SimpleNamespace())
        stream.anchor = Stamp(**stamp(0))
        for t in (1, 2):
            stream.accept({'timestamp': datetime.fromtimestamp(BASE+t, timezone.utc),
                'elapsed_ns': cw.NS, 'processor': {'combined_power': 500}, 'thermal_pressure': 'Nominal'})
        result = stream.sample()
        self.assertEqual(result['pm_observed_ns'], 2*cw.NS)
        self.assertEqual(result['power_intervals'][1], {'start_ns': cw.NS, 'end_ns': 2*cw.NS, 'watts': .5})
        with self.assertRaises(ValueError):
            stream.accept({'timestamp': datetime.fromtimestamp(BASE+20, timezone.utc),
                'elapsed_ns': cw.NS, 'processor': {'combined_power': 500}, 'thermal_pressure': 'Nominal'})

    def test_injected_smc_pmset_ioreg_notify_and_power(self):
        class SMC:
            def read(self, keys):
                return {'values': sample(0)['sensors'], 'errors': {},
                        'raw': {k: {'data_type': 'fpe2' if k.startswith('F') else 'flt '} for k in keys}}
            def close(self):
                pass
        class Source:
            def start(self):
                return self
            def sample(self):
                return {'power_intervals': [], 'pm_state': 'Nominal', 'pm_observed_ns': 0}
            def close(self):
                pass
        def run(argv):
            if 'custom' in argv:
                return SimpleNamespace(returncode=0, stdout=b'AC Power:\n powermode 2\n')
            if 'IODisplayWrangler' in argv:
                return SimpleNamespace(returncode=0, stdout=plistlib.dumps([
                    {'IOPowerManagement': {'CurrentPowerState': 1}}]))
            return SimpleNamespace(returncode=1, stdout=b'')
        ctx = SimpleNamespace(stamp=lambda: Stamp(**stamp(1)),
                              clocks=SimpleNamespace(monotonic_ns=lambda: cw.NS))
        sampler = native.NativeSampler(policy(), ctx=ctx, smc=SMC(),
            notify=SimpleNamespace(read=lambda: 0, close=lambda: None), power=Source(), run=run,
            battery_reader=lambda: (sample(1)['battery'], b''), guard_reader=lambda: [],
            boot_reader=lambda: 'synthetic-boot', topup_reader=lambda t: sample(1)['topup'],
            setup_check=lambda: {'passed': True, 'setup_sha256': '4'*64}, obc_off_attested_by='synthetic')
        sampler.start()
        try:
            r = sampler.sample(attempt_id='synthetic-attempt', boot_id='synthetic-boot')
            self.assertTrue(r['display_asleep'])
            self.assertFalse(r['screensaver_engaged'])
            self.assertEqual(r['ac_powermode'], 2)
            self.assertTrue(r['final_checks_passed'])
        finally:
            sampler.close()

    def test_display_unknown_is_not_hid_idle(self):
        for data in ([], [{}], [{'IOPowerManagement': {'CurrentPowerState': 4}}]):
            run = lambda a: SimpleNamespace(returncode=0, stdout=plistlib.dumps(data))
            self.assertIsNot(native.display_state(run), True)

    def test_cancellation_closes_sources_and_only_emits_boundary_markers(self):
        closed = []
        fake = SimpleNamespace(ctx=SimpleNamespace(clocks=SimpleNamespace(monotonic_ns=lambda: 0),
                                                   stamp=lambda: Stamp(**stamp(0))),
                               start=lambda: None, close=lambda: closed.append(True))
        journal = StringIO()
        with self.assertRaises(InterruptedError):
            native.run_attempt(policy(), header(), fake, journal=journal, trace=StringIO(),
                               final_checks=lambda: True, cancelled=lambda: True)
        self.assertTrue(closed)
        for line in journal.getvalue().splitlines():
            self.assertEqual(set(json.loads(line)), {'phase', 'wall_ns', 'monotonic_ns'})


class TriageBindingTests(unittest.TestCase):
    def test_r16_requires_replayed_receipt_for_exact_policy_attempt_and_boot(self):
        from tests.align.test_v4_cadence import passing_packet, INTERNAL, IDENTITY
        from joulewise.align.apple import v4_cadence as cad
        packet = passing_packet()
        identity = {**IDENTITY, 'condition_waits_policy_sha256': 'a'*64}
        self.assertFalse(cad.next_arm_triage(packet, INTERNAL, identity)['admitted'])
        entry = {'receipt_sha256': 'b'*64, 'policy_sha256': 'a'*64,
                 'attempt_id': 'synthetic-attempt', 'boot_id': 'synthetic-boot'}
        packet['checks']['quiet_start_state'].update(entry)
        identity['quiet_start_state_binding'] = {'verified': True, **entry}
        self.assertTrue(cad.next_arm_triage(packet, INTERNAL, identity)['admitted'])
        packet['checks']['quiet_start_state']['receipt_sha256'] = 'c'*64
        self.assertFalse(cad.next_arm_triage(packet, INTERNAL, identity)['admitted'])


if __name__ == '__main__':
    unittest.main()
