"""Cold-review round 3: deterministic, synthetic witnesses; no host setters."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import signal
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt, v4_registration as reg
from scripts import align_r1_followup_kit as kit, align_r1_rehearsal as r1, align_v4_kit as v4
from tests.align.test_r1_round2 import classified
from tests.align import test_r1_rehearsal as rehearsal
from tests.align import r1_synthetic as syn

PHASES = ('pre_warmup_idle', 'quiet', 'load', 'recovery')


class CoverageBarTests(unittest.TestCase):
    def test_each_bar_independently_refuses_in_every_phase(self):
        spans = {name: (i * 2000 * rt.NS, (i * 2000 + 1000) * rt.NS)
                 for i, name in enumerate(PHASES)}
        rows = [{"started": {"monotonic_ns": start + i * rt.NS},
                 "finished": {"monotonic_ns": start + i * rt.NS},
                 "values": {"sensors": {"TV0h": 40.}, "errors": {}}}
                for start, _ in spans.values() for i in range(1000)]
        self.assertTrue(kit.phase_coverage(rows, ['TV0h'], spans)['pass'])
        for phase, (start, end) in spans.items():
            for case in ('coverage_98_pct', 'read_errors_1_pct', 'consecutive_empty'):
                bad = deepcopy(rows)
                missing = ({50 + 40 * i for i in range(20)} if case == 'coverage_98_pct' else
                           {500, 501} if case == 'consecutive_empty' else set())
                bad = [r for r in bad if not (start <= r['started']['monotonic_ns'] < end
                           and (r['started']['monotonic_ns'] - start) // rt.NS in missing)]
                if case == 'read_errors_1_pct':
                    for row in bad:
                        if row['started']['monotonic_ns'] in {start + (50 + 80 * i) * rt.NS for i in range(10)}:
                            row['values']['errors']['TV0h'] = 'synthetic read failure'
                report = kit.phase_coverage(bad, ['TV0h'], spans)
                cell = report['phases'][phase]['TV0h']
                with self.subTest(phase=phase, case=case):
                    # All other bars pass: a failure cannot be incidental.
                    if case == 'coverage_98_pct':
                        self.assertAlmostEqual(cell['sample_fraction'], .98)
                    else:
                        self.assertGreaterEqual(cell['sample_fraction'], .99)
                    if case == 'read_errors_1_pct':
                        self.assertAlmostEqual(cell['read_error_fraction'], .01)
                    else:
                        self.assertLess(cell['read_error_fraction'], .01)
                    self.assertEqual(cell['max_consecutive_empty_cells'], 2 if case == 'consecutive_empty' else 1)
                    self.assertFalse(cell['pass'])
                    self.assertFalse(report['pass'])
                    self.assertTrue(all(report['phases'][other]['TV0h']['pass'] for other in PHASES if other != phase))

    def test_smoke_table_emits_exactly_all_four_rl76_phases(self):
        c = classified()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'inventory').mkdir()
            bundle = out / 'runs/member'
            bundle.mkdir(parents=True)
            (bundle / 'events.jsonl').write_text('')
            (out / rt.RESULT_NAME).write_text(json.dumps({'bundle': 'runs/member'}))
            saved = {'classification': c, 'inventory': {'keys': [{'key': 'TV0h', 'unit': 'degC'}]}}
            (out / 'inventory/r1_classification.json').write_text(json.dumps(saved))
            (out / 'inventory/inventory_journal.jsonl').write_text('')
            journal = {'rows': [], 's_fast': 'TV0h', 's_slow': 'Tf08', 'g0': [{'start_ns': 0, 'end_ns': rt.NS}]}
            with patch.object(kit.replay, 'read_journal', return_value=journal), patch.object(
                    kit.replay, 'Session'), patch.object(kit.replay, 'warmup_anchor', return_value=300 * rt.NS), patch.object(
                    kit.replay, 'candidate_replays', return_value=[]):
                report = kit.smoke_table(out)
            self.assertEqual(set(report['coverage']['phases']), set(PHASES))


class RuntimeWiringTests(unittest.TestCase):
    def test_night_confirms_and_reports_smoke_pair_and_refuses_inadmissible_pair(self):
        c = classified()
        picks = {role: c[role] for role in ('s_fast', 's_slow')}
        keys = [r['key'] for r in c['ranking']]
        c.update(s_fast='Tnew', s_slow='Ttop')
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'inventory').mkdir()
            segment = object.__new__(rt.Segment)
            segment.out = out
            segment.config = {'sensors': {**picks, 'fan_keys': [], 'r0_sha256': 'a' * 64}, 'r0_classified_keys': keys}
            segment.inventory = SimpleNamespace(inventory={'keys': keys}, rows=[], keys=keys)
            segment.stop_inventory = lambda: None
            member = SimpleNamespace(ep=SimpleNamespace(turns=[SimpleNamespace(start_ns=1000, end_ns=2000)]))
            for admissible in (True, False):
                result = deepcopy(c)
                if not admissible:
                    next(r for r in result['ranking'] if r['key'] == picks['s_slow'])['t_band_s'] = 301
                with patch.object(rt, 'classify_step', return_value=result):
                    summary = segment.thermometry(member, label='step-d', record_only=False)
                self.assertEqual({role: summary[role] for role in picks}, picks)
                self.assertEqual(summary['registered_picks'], {'s_fast': 'Tnew', 's_slow': 'Ttop'})
                self.assertEqual(summary['night_confirmation']['ok'], admissible)
                self.assertEqual(summary['status'], 'pass' if admissible else 'fail')
                saved = json.loads((out / 'inventory/r1_classification.json').read_text())
                self.assertEqual({role: saved['night_confirmation'][role] for role in picks}, picks)
                self.assertEqual(saved['night_confirmation']['ok'], admissible)
                record = r1.thermometry_record('step-d', {'thermometry': summary})
                self.assertEqual(record['night_confirmation'], summary['night_confirmation'])
                if not admissible:
                    self.assertIn('r1.sensor_inadmissible', record['flags'])
                    with self.assertRaisesRegex(ValueError, 'thermometry bar did not pass'):
                        v4.check_r1_evidence({'R1': {'I_D': 1}}, {
                            'schema': v4.R1_SLOTS_SCHEMA, 'source': v4.R1_HARDWARE_SOURCE,
                            'inconclusive_segments': {}, 'slots': {'I_D': 1},
                            'high_power': {'verdict': 'not_adopted'}, 'ac_powermode': 0, 'slots_ac_powermode': 0,
                            'thermometry': {'bar': record['status'], 'D': record}})

    def test_gated_d_and_xg_reference_hooks_do_not_dispatch_timed_out_turns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config, digest = rt.load_config(syn.synthetic_config(root / 'cfg'))
            template, tspec = rt.read_template(config['templates']['d_spam'])
            policy = rt.gate_policy(config['sensors'], {'delta_fast_c': 1., 'delta_slow_c': 1.5},
                                    turn_cap_s=300, chunk_tokens=256, heavy=False, per_turn=False)
            spec = rt.step_spec(tspec, {**config['step'], 'decode_tokens': 8}, policy, deadman_s=1580)
            for kind in (*rt.contract.GATED_D_KINDS, 'x-g'):
                backend = syn.SyntheticBackend(config)
                try:
                    segment = rt.Segment(kind=kind, out=root / kind, duration_s=None, soak=None,
                                         config=config, config_sha256=digest, backend=backend)
                    segment.consume_d_reference = lambda session: {'fast_c': 0., 'slow_c': 0., 'source_member': 'synthetic'}
                    reference = {}
                    hook = segment.reference_hook(reference)
                    def install(session):
                        session.reference = {'fast_c': 0., 'slow_c': 0., 'source_member': 'synthetic'}
                        hook(session)
                    member = rt.member_config(template, spec, run_id=kind, kind=kind)
                    bundle, _ = backend.run_member(member, root / 'runs', install)
                    from joulewise.align.apple.workload import read_episode_bundle
                    ep = read_episode_bundle(bundle)
                    self.assertEqual(len(ep.turns), 0, kind)
                    self.assertIn('thermal.start_gate_timeout', ep.flags)
                    self.assertNotIn('r1.g0_timeout_run', ep.flags)
                finally:
                    backend.close()

    def test_production_s6_record_never_transfers_the_tf08_receipt(self):
        segment = object.__new__(rt.Segment)
        segment.config = {'sensors': {'s_fast': 'TV0h', 's_slow': 'TV0s', 'fan_keys': [], 'r0_sha256': 'a' * 64}}
        segment.backend = SimpleNamespace(name='production')
        segment.soak = {}
        segment.start_inventory = lambda: None
        segment.k_step = lambda *a, **kw: (SimpleNamespace(wall_s=1, ep=SimpleNamespace(
            turns=[SimpleNamespace(start_ns=0, end_ns=1)], start_ns=0, end_ns=1)),
            {'t_decline_status': 'observed', 't_decline_s': 1, 'operating_reference': {},
             'decode_energy_j': 2, 'decode_tokens': 1})
        segment.bands = lambda: {'delta_fast_c': 1., 'delta_slow_c': 1.}
        segment.observe_recovery = lambda member: []
        segment.thermometry = lambda *a, **kw: {'classification_sha256': 'a' * 64}
        with patch.object(rt, 'step_response', return_value={'peak_ns': 1}), patch.object(
                rt, 'recovery_time', return_value=(10, False)), patch.object(rt, 'bands_c', return_value={}), patch.object(
                rt, 'derive_step_d_slots', return_value=({}, {'S6_tuning': {'status': 'adopted', 'S6_now': 1.5}})):
            result = segment.k_step_d()
        self.assertEqual(result['slot_detail']['S6_tuning'], {
            'status': 'new_sensor_default', 'authority': 'RL-78 default band',
            'S6_now': 1., 'receipt_transferred': False})

    def test_post_g0_watchdog_fits_realistic_d_turn_and_is_installed(self):
        budget = rt.smoke_post_g0_budget(rt.STEP_QUIET_S, 1580)
        self.assertEqual(budget, {'quiet': 300, 'turn': 1580, 'recovery': 600,
                                 'classification_and_close': 120, 'total': 2600})
        # A 1,000 s D turn plus quiet and recovery cannot fit the old 1,200 s.
        self.assertGreater(300 + 1000 + 600, 1200)
        self.assertLess(300 + 1000 + 600 + 120, budget['total'])
        for turn_bound in (900, 1580, 2000):
            with tempfile.TemporaryDirectory() as tmp:
                segment = object.__new__(rt.Segment)
                segment.kind = 'step-d'
                segment.out = Path(tmp)
                segment.smoke_part = 'B'
                segment.smoke_started = 0
                segment.quiet_spans = []
                segment.clock = SimpleNamespace(sleep=lambda s: None)
                segment.now_ns = unittest.mock.Mock(side_effect=[0, 300 * rt.NS, 300 * rt.NS])
                session = SimpleNamespace(reference={'fast_c': 40., 'slow_c': 40.},
                                          wait=lambda *a, **kw: {'outcome': 'released'})
                with patch.object(rt.time, 'monotonic', return_value=1), patch.object(rt.signal, 'setitimer') as timer:
                    segment.reference_hook({}, quiet_s=300, rearm_s=turn_bound, capture=True)(session)
                    session.wait('G0')
                expected = 300 + turn_bound + rt.RECOVERY_CAP_S + 120
                timer.assert_called_once_with(signal.ITIMER_REAL, expected)
                self.assertEqual(json.loads((segment.out / 'smoke_part_a.json').read_text())['post_g0_budget_s']['total'], expected)


class PreparePacketTests(unittest.TestCase):
    def packet(self, path):
        packet = {'schema': 'joulewise.align.r1_followup_prepare.v1', 'status': 'FOR_LEAD_ARM',
                  'executed_commit': r1.executed_commit(r1.ROOT),
                  'weight_digests': {'ok': True, 'roots': {}}, 'runtime_stack': {'ok': True, 'versions': {}},
                  'bound_files': {name: rt.sha256_file(r1.ROOT / name) for name in reg.R1_EXECUTED_SOURCES}}
        path.write_text(json.dumps(packet))
        return packet

    def test_requires_matching_commit_and_both_ok_and_records_packet_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'prepare.json'
            packet = self.packet(path)
            record = r1.require_prepare_packet(path)
            self.assertEqual(record['path'], str(path.resolve()))
            self.assertEqual(record['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            for name in ('weight_digests', 'runtime_stack'):
                self.assertEqual(record[name], packet[name])
                for bad in (None, {}, {'ok': False}, {'ok': 'true'}, {'ok': 1}):
                    mutant = deepcopy(packet)
                    mutant[name] = bad
                    path.write_text(json.dumps(mutant))
                    with self.subTest(check=name, bad=bad), self.assertRaisesRegex(r1.Refusal, 'r1.prepare_packet.' + name):
                        r1.require_prepare_packet(path)
            for field, value in (('status', 'REFUSED'), ('executed_commit', '0' * 40), ('bound_files', {})):
                mutant = {**packet, field: value}
                path.write_text(json.dumps(mutant))
                with self.subTest(field=field), self.assertRaisesRegex(r1.Refusal, 'r1.prepare_packet.' + field):
                    r1.require_prepare_packet(path)
            with self.assertRaisesRegex(r1.Refusal, 'r1.prepare_packet.missing'):
                r1.require_prepare_packet(None)
            path.unlink()
            with self.assertRaisesRegex(r1.Refusal, 'r1.prepare_packet.unreadable'):
                r1.require_prepare_packet(path)

    def test_production_driver_refuses_before_any_host_command_without_prepare(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = rehearsal.R1Tests.args(None, tmp, synthetic=False)
            with patch.object(r1, '_run', side_effect=AssertionError('host command before prepare')):
                self.assertEqual(r1.run(args), 3)
            record = json.loads((args.output / 'r1_result.json').read_text())
            self.assertIn('r1.prepare_packet.missing', record['error'])
