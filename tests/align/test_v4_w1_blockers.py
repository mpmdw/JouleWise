"""Prospective W1 blocker contract; entirely synthetic, no hardware probes."""
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_registration as reg
from tests.align.v4_registration_fixtures import export, signed_bar, battery_policy


class U3Tests(unittest.TestCase):
    def test_source_export_report_and_gate_are_bound_to_same_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            data = export()
            report = root/'transfer.md'
            report.write_text('Synthetic transfer justification\n')
            data['policy']['transfer_justification_sha256'] = reg.digest(report.read_bytes())
            source = root/'pairs.json'
            source.write_text(json.dumps(data))
            from scripts import align_v4_u3_bar as cli
            draft, adopted = root/'draft.json', root/'bar.json'
            with patch.object(cli, 'ROOT', root):
                self.assertEqual(cli.main(['--input', str(source), '--supporting-source', str(report),
                                           '--output', str(draft)]), 0)
            bar = json.loads(draft.read_bytes())
            gate = root/'docs/align/v4/gate.json'
            gate.parent.mkdir(parents=True)
            gate.write_text(json.dumps({'verdict': 'ADMIT', 'derivation_sha256': bar['derivation_sha256']}))
            with patch.object(cli, 'ROOT', root):
                argv = ['--adopt-draft', str(draft), '--gate', str(gate),
                        '--lead-signature', 'lead: synthetic 2026-11-08', '--output', str(adopted)]
                self.assertEqual(cli.main(argv), 0)
                with self.assertRaises(FileExistsError):
                    cli.main(argv)
            bar = json.loads(adopted.read_bytes())
            original_gate = gate.read_bytes()
            gate.write_text(json.dumps({'verdict': 'REFUSE', 'derivation_sha256': bar['derivation_sha256']}))
            forged = deepcopy(bar)
            forged['independent_gate']['sha256'] = reg.digest(gate.read_bytes())
            with self.assertRaisesRegex(ValueError, 'gate bytes'):
                reg.validate_u3(forged, root=root)
            gate.write_bytes(original_gate)
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, capture_output=True, check=True).stdout.decode().strip()
            git('init', '-q')
            git('add', '.')
            git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                'commit', '-qm', 'synthetic source custody')
            commit = git('rev-parse', 'HEAD')
            reg.validate_u3(bar, root=root, commit=commit)
            for path in (source, report, gate):
                original = path.read_bytes()
                path.write_bytes(original+b'drift')
                with self.subTest(path=path.name), self.assertRaises(ValueError):
                    reg.validate_u3(bar, root=root, commit=commit)
                path.write_bytes(original)
            with self.assertRaises(ValueError):
                reg.validate_u3(bar, root=root, commit='0'*40)

    def test_series_quantile_is_exact_under_the_model(self):
        # Opus arithmetic (ruling 4): the series false-fail equals beta, integrating the
        # shared RMS scale once; the per-pair rate is the exact Student-t(n) tail.
        from joulewise.align.apple import v4_u3
        q = v4_u3.series_quantile(7, 16, .05)
        self.assertAlmostEqual(v4_u3.series_false_fail(q, 7, 16), .05, places=9)
        self.assertAlmostEqual(v4_u3.per_pair_false_fail(2.228139, 10), .05, places=5)
        self.assertGreater(v4_u3.series_quantile(5, 16, .05), v4_u3.series_quantile(20, 16, .05))
        self.assertGreater(v4_u3.series_quantile(7, 19, .05), v4_u3.series_quantile(7, 16, .05))
        for constant in (3, 2.576):
            self.assertNotAlmostEqual(q, constant, places=2)

    def test_signed_predictive_derivation_accepts_and_scales(self):
        bar = signed_bar()
        self.assertIs(reg.validate_u3(bar), bar)
        p = bar['prediction']
        self.assertEqual((p['n'], p['df'], p['series_comparisons']), (7, 7, 24))   # RL-16: all C/T reserves, N = 24
        rel = [r for r, pair in zip([(e[1]-e[0])/((e[0]+e[1])/2) for e in (x['energies_j'] for x in bar['pairs'])],
                                     bar['pairs']) if pair['phase'] == 'pilot']
        s0 = math.sqrt(sum(r*r for r in rel)/len(rel))
        self.assertAlmostEqual(p['rms_rel'], s0, places=12)
        self.assertAlmostEqual(p['relative_bar_30B'], p['series_quantile_q']*s0, places=12)
        self.assertAlmostEqual(p['relative_bar_D'], 1.5*p['relative_bar_30B'], places=12)   # ruling 6: f = 1.5
        self.assertEqual(p['d_screen'], 'not_refuted')
        self.assertFalse(p['heavy_tail_rule_applied'])
        self.assertAlmostEqual(reg.u3_margin(60000, bar, population='D'),
                               2*reg.u3_margin(30000, bar, population='D'))
        self.assertEqual({row['name'] for row in bar['oc']['scenarios']} >= {
            'D_true_scale_1.0', 'D_true_scale_1.5', 'D_true_scale_2.0', 'D_true_scale_3.0'}, True)

    def test_refuted_or_missing_d_screen_leaves_30b_valid_and_d_inconclusive(self):
        data = export()
        refuted = deepcopy(data)
        refuted['pairs'][-1]['energies_j'] = [100, 200]
        missing = deepcopy(data)
        missing['pairs'].pop()
        for name, case in (('refuted', refuted), ('missing', missing)):
            bar = reg.derive_u3(case['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=case['policy'])
            bar.update(status='registered', lead_signature='lead: synthetic 2026-11-08',
                       independent_gate={'verdict': 'ADMIT', 'path': 'docs/align/v4/g.json', 'sha256': 'd'*64,
                                         'derivation_sha256': bar['derivation_sha256']})
            with self.subTest(screen=name):
                self.assertEqual(bar['prediction']['d_screen'], name)
                reg.validate_u3(bar)
                self.assertGreater(reg.u3_margin(2000, bar, population='30B'), 0)
                with self.assertRaisesRegex(ValueError, 'inconclusive'):
                    reg.u3_margin(30000, bar, population='D')

    def test_heavy_tail_rule_halves_beta_and_min_sessions(self):
        data = export()
        heavy = deepcopy(data)
        values = [-.001, -.001, .001, .001, -.001, .001, .02]
        for pair, r in zip(heavy['pairs'], values):
            pair['energies_j'] = [1000*(1-r/2), 1000*(1+r/2)]
        bar = reg.derive_u3(heavy['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=heavy['policy'])
        self.assertTrue(bar['prediction']['heavy_tail_rule_applied'])
        self.assertEqual(bar['prediction']['series_beta'], .025)
        few = deepcopy(data)
        del few['pairs'][3:6]
        with self.assertRaisesRegex(ValueError, '>=5'):
            reg.derive_u3(few['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=few['policy'])

    def test_rl16_expands_scope_without_changing_scale_or_beta(self):
        from joulewise.align.apple import v4_u3
        for heavy in (False, True):
            data = export()
            if heavy:
                data['pairs'][6]['energies_j'] = [990., 1010.]
            after = v4_u3.prediction(data['pairs'], data['policy'])
            beta = .025 if heavy else .05
            historical_q = v4_u3.series_quantile(7, 22, beta)
            self.assertEqual(after['series_comparisons'], 24)
            self.assertEqual(after['heavy_tail_rule_applied'], heavy)
            self.assertEqual(after['series_beta'], beta)
            self.assertGreater(after['series_quantile_q'], historical_q)
            self.assertAlmostEqual(after['relative_bar_D'], 1.5*after['series_quantile_q']*after['rms_rel'])
            self.assertAlmostEqual(after['series_false_fail'], beta, places=9)

    def test_d_replay_checks_target_identity_battery_and_frozen_window_scope(self):
        from tests.align.test_thermal_desk import member
        from joulewise.align.apple import thermal_desk
        a, b = member('a', energy=30000), member('b', energy=30030)
        for row in (a, b):
            row.update(role='D', window='W1', identical_work_group='same', u3_configuration_sha256='b'*64)
        bar = signed_bar()
        self.assertEqual(thermal_desk.identical_pair(a, b, u3_bar=bar)['status'], 'pass')
        b['u3_configuration_sha256'] = 'e'*64
        self.assertEqual(thermal_desk.identical_pair(a, b, u3_bar=bar)['status'], 'inconclusive')
        b['u3_configuration_sha256'] = 'b'*64
        b['calibration_exclusions'] = ['battery.member_span']
        self.assertEqual(thermal_desk.identical_pair(a, b, u3_bar=bar)['status'], 'inconclusive')
        b['calibration_exclusions'] = []
        a['window'] = b['window'] = 'UNREGISTERED'
        result = thermal_desk.window_report([a, b], v4=True, u3_bar=bar)['model_windows']['synthetic/UNREGISTERED']
        self.assertEqual(result['U3']['status'], 'inconclusive')
        self.assertIn('scope', result['U3']['reason'])

    def test_refuses_pending_unsigned_forged_unqualified_or_self_calibrated(self):
        bar = signed_bar()
        for change in ('pending', 'signature', 'gate', 'margin', 'oc', 'D', 'W1', 'duplicate'):
            bad = deepcopy(bar)
            if change == 'pending': bad['status'] = 'PENDING'
            if change == 'signature': bad['lead_signature'] = ''
            if change == 'gate': bad['independent_gate']['derivation_sha256'] = 'e'*64
            if change == 'margin': bad['prediction']['relative_bar_30B'] *= 2
            if change == 'oc': bad['oc']['scenarios'][0]['series_failures'] += 1
            if change == 'D': bad['pairs'][-1]['configuration_sha256'] = 'e'*64
            if change == 'W1': bad['pairs'][0]['phase'] = 'W1'
            if change == 'duplicate': bad['pairs'][1]['session'] = bad['pairs'][0]['session']
            with self.subTest(change=change), self.assertRaises(ValueError):
                reg.validate_u3(bad)
        for energy in (0, -1, math.nan, math.inf, True):
            with self.subTest(energy=energy), self.assertRaises(ValueError):
                reg.u3_margin(energy, bar)

    def test_smaller_sample_widens_prediction_and_unregistered_roster_refuses(self):
        data = export()
        base = reg.derive_u3(data['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=data['policy'])
        small = deepcopy(data)
        del small['pairs'][3]
        wider = reg.derive_u3(small['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=small['policy'])
        self.assertGreater(wider['prediction']['series_quantile_q'], base['prediction']['series_quantile_q'])
        wrong = deepcopy(data)
        wrong['policy']['checks_by_window']['T4'] = {'30B': 0, 'D': 10}
        with self.assertRaisesRegex(ValueError, 'registered roster'):
            reg.derive_u3(wrong['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=wrong['policy'])
        data['pairs'][-1]['energies_j'] = [100, 200]
        bad = reg.derive_u3(data['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=data['policy'])
        self.assertEqual(bad['prediction']['d_screen'], 'refuted')


class ExportTests(unittest.TestCase):
    def test_policy_template_is_the_ruled_roster_and_assemble_refuses_placeholders(self):
        from scripts import align_v4_u3_export as export_cli
        policy = export_cli.policy_template()
        self.assertEqual(sum(sum(w.values()) for w in policy['checks_by_window'].values()), 24)   # RL-16: N = 24
        self.assertEqual((policy['series_alpha'], policy['d_transfer_factor']), (.05, 1.5))     # rulings 1, 6
        self.assertEqual(sorted(policy['checks_by_window']), sorted(['W1', *[f'C{i}' for i in range(1, 15)],
                                                                     *[f'T{i}' for i in range(1, 6)]]))
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp/'policy.json').write_text(json.dumps(policy))
            (tmp/'pilot.json').write_text(json.dumps({'pairs': []}))
            (tmp/'r1.json').write_text(json.dumps({'pairs': []}))
            with self.assertRaisesRegex(ValueError, 'FILL'):
                export_cli.main(['assemble', '--pilot', str(tmp/'pilot.json'), '--r1', str(tmp/'r1.json'),
                                 '--policy', str(tmp/'policy.json'), '--output', str(tmp/'pairs.json')])

    def test_selection_is_by_design_position_and_never_substitutes(self):
        from scripts import align_v4_u3_export as export_cli
        measured = []
        def fake_measure(early, late):
            measured.append((early, late))
            ok = early != 'bad-early'
            return {'eligible': ok, 'reasons': [] if ok else ['token identity unavailable or divergent'],
                    'energies_j': [1000., 1001.], 'clock_difference_fraction': 0., 'token_identical': ok,
                    'configuration_sha256': 'b'*64, 'source_sha256': 'c'*64}
        selection = {'sessions': [
            {'session': 'p4', 'candidates': [{'ordinals': [9, 10], 'early_bundle': 'adjacent', 'late_bundle': 'x'},
                                             {'ordinals': [5, 17], 'early_bundle': 'p4-5', 'late_bundle': 'p4-17'},
                                             {'ordinals': [6, 16], 'early_bundle': 'p4-6', 'late_bundle': 'p4-16'}]},
            {'session': 'p5', 'candidates': [{'ordinals': [5, 17], 'early_bundle': 'bad-early', 'late_bundle': 'y'},
                                             {'ordinals': [6, 16], 'early_bundle': 'p5-6', 'late_bundle': 'p5-16'}]}]}
        with patch.object(export_cli, 'measure_pair', side_effect=fake_measure):
            result = export_cli.pilot_pairs(selection)
        # Only the selected pair of each session is ever read; the ineligible p5 pair is not replaced.
        self.assertEqual(measured, [('p4-5', 'p4-17'), ('bad-early', 'y')])
        self.assertEqual([p['session'] for p in result['pairs']], ['p4'])
        self.assertEqual(result['unavailable_sessions'][0]['session'], 'p5')


class CompressedEpisodeTests(unittest.TestCase):
    @unittest.skipUnless(__import__('shutil').which('zstd') or Path('/opt/homebrew/bin/zstd').exists(), 'zstd CLI')
    def test_zstd_compressed_episode_is_refused_explicitly_then_reads_after_restore(self):
        from joulewise.align.apple.workload import read_episode_bundle
        from joulewise.authentication_io import CompressedBundleRequiresRestore
        from joulewise.desk_compress import zstd_path
        from tests.align.test_thermal_gate import NativeIntegrationTests
        helper = NativeIntegrationTests('test_real_workload_endpoint_budget_and_held_stream_keep_exact_tokens')
        with tempfile.TemporaryDirectory() as tmp:
            bundle, status, _ = helper.held_run(Path(tmp)/'member')
            plain = Path(bundle)/'outputs/align_episode.json'
            before = read_episode_bundle(bundle)
            subprocess.run([zstd_path(), '-q', '--rm', str(plain)], check=True)
            self.assertFalse(plain.exists())
            self.assertTrue(Path(str(plain)+'.zst').exists())
            with self.assertRaises(CompressedBundleRequiresRestore):
                read_episode_bundle(bundle)
            subprocess.run([zstd_path(), '-q', '-d', '--rm', str(plain)+'.zst'], check=True)
            self.assertEqual(read_episode_bundle(bundle).episode_id, before.episode_id)


class BatteryTests(unittest.TestCase):
    def test_raw_span_join_observes_idle_charging_assist_missing_and_malformed(self):
        from joulewise.align.apple import v4_battery as battery
        from joulewise.b5.harvest import JOURNAL_SCHEMA
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'metadata.json').write_text(json.dumps({'uncertainty_evidence': {'clock_anchor': {
                'clock_stamps': {'pre_spawn': {'monotonic_before_s': 2},
                                 'post_parse': {'monotonic_after_s': 10},
                                 'sampling_started': {'monotonic_before_s': 3},
                                 'sampling_stopped': {'monotonic_after_s': 9}}}}}))
            (root/'events.jsonl').write_text('\n'.join(json.dumps(r) for r in (
                {'event_type': 'stage_started', 'phase': 'idle_baseline', 'metadata': {'monotonic_ns': 10**9}},
                {'event_type': 'stage_completed', 'phase': 'idle_drift_sentinel', 'metadata': {'monotonic_ns': 12*10**9}})))
            path = root/'journal.jsonl'
            for mode in ('clean', 'assist', 'charge_idle', 'ac_loss', 'missing', 'malformed'):
                rows = []
                for sec in range(14):
                    stamp = dict(wall_ns=sec*10**9, monotonic_ns=sec*10**9, monotonic_raw_ns=sec*10**9)
                    current = -500 if mode == 'assist' else 500 if mode == 'charge_idle' and sec < 2 else 0
                    values = dict(update_time_s=sec, instant_amperage_ma=0, external_connected=mode != 'ac_loss',
                                  is_charging=False, current_capacity_pct=100, voltage_mv=12000,
                                  smc={'values': {'B0AC': current, 'B0AV': 12000+sec%2}, 'errors': {}})
                    rows.append(json.dumps(dict(schema=JOURNAL_SCHEMA, module='battery', kind='reading',
                                                started=stamp, finished=stamp, values=values, error=None)))
                path.write_text('' if mode == 'missing' else '\n'.join(rows)+('\ninvalid' if mode == 'malformed' else ''))
                evidence = battery.bundle_evidence(root, battery.load_journal(path))
                with self.subTest(mode=mode):
                    if mode in ('missing', 'malformed'):
                        self.assertEqual(evidence['status'], 'unavailable')
                    else:
                        self.assertEqual(evidence['status'], 'observed', evidence)
                        if mode == 'assist': self.assertIn('battery.assist', evidence['flags'])
                        if mode in ('charge_idle', 'ac_loss'): self.assertIn('battery.member_span', evidence['flags'])
                        if mode == 'clean': self.assertNotIn('battery.member_span', evidence['flags'])

    def test_clean_pass_assist_disclosed_charging_fail_missing_inconclusive(self):
        row = {'id': 'one', 'model': 'D', 'window': 'W1', 'flags': [],
               'battery': {'status': 'observed', 'source_sha256': 'a'*64, 'flags': [],
                           'soc_pct': [100], 'charger_w': [140]}}
        def check(r):
            return reg.desk_diagnostics([r], battery_policy=battery_policy())['battery_windows']['D/W1']
        self.assertIs(check(row)['bar_pass'], True)
        assisted = deepcopy(row)
        assisted['battery']['flags'] = ['battery.assist']
        self.assertIs(check(assisted)['bar_pass'], True)
        self.assertEqual(check(assisted)['assist_count'], 1)
        charging = deepcopy(row)
        charging['battery']['flags'] = ['battery.member_span']
        self.assertIs(check(charging)['bar_pass'], False)
        self.assertIn('automatic resume', check(charging)['consequence'])      # ruling 9
        self.assertNotIn('no pool entry', check(charging)['consequence'])
        excursion = deepcopy(row)
        excursion['battery']['flags'] = ['battery.accumulator_excursion']   # ruling 8
        self.assertIs(check(excursion)['bar_pass'], False)
        row.pop('battery')
        self.assertIsNone(check(row)['bar_pass'])
        self.assertIsNone(reg.desk_diagnostics([row])['battery_windows']['D/W1']['bar_pass'])

    def test_empty_window_never_vacuously_passes(self):
        from scripts import align_v4_session as session
        self.assertFalse(session.battery_windows_pass({}))

    def test_v4_desk_writes_the_evidence_aware_full_desk_verdict(self):
        from scripts import align_v4_session as session
        with tempfile.TemporaryDirectory() as tmp:
            pilot_path = Path(tmp)/'PILOT.json'
            charged = {'run_id': 'c', 'excluded': True, 'exclusion_codes': ['battery.member_span'],
                       'task_pair': 'p', 'condition': 'benign',
                       'summary': {'energy': {'gpu': {'joules': 1., 'segment_sum_j': 1.}}, 'flags': [],
                                   'configuration': {'sampler': {}}, 'window_evidence_precheck': {'eligible': True}}}
            pilot_path.write_text(json.dumps({'members': [charged]}))
            status = {'pilot': str(pilot_path), 'checks': {
                'I1_all_bundles_readable': True, 'I2_energy_on_every_episode': True,
                'I3_attribution_tiles_episode': True, 'chain_eligibility': False,
                'no_member_exclusions': False, 'v4_B_bar': False}}
            with patch.object(session.pilot, 'desk', return_value=status):
                result = session.desk(tmp, harvest=False)
            self.assertIs(result['full_desk_gate']['pass'], True)
            self.assertEqual(result['full_desk_gate']['charging_only_members_removed'], ['c'])
            self.assertTrue(json.loads((Path(tmp)/'desk.json').read_text())['full_desk_gate']['pass'])

    def test_false_b_bar_alone_does_not_fail_the_full_desk_gate(self):
        # Ruling 9: v4_B_bar is recorded false, the full-desk gate ignores it,
        # and v4_cadence battery_window governs the resume.
        from scripts import align_v4_session as session
        self.assertTrue(session.full_desk_gate_pass({'v4_B_bar': False, 'v4_D_cohort': True}))
        self.assertFalse(session.full_desk_gate_pass({'v4_B_bar': True, 'v4_D_cohort': False}))
        self.assertFalse(session.full_desk_gate_pass({'v4_B_bar': False}))


if __name__ == '__main__':
    unittest.main()
