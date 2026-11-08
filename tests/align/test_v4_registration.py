"""Registration blockers: synthetic records only; no native probes or weights."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_v4_kit as kit
from joulewise.align.apple import thermal_desk, v4_estimands
from tests.align.test_thermal_desk import member, contrast


class RegistrationTests(unittest.TestCase):
    def test_w1_requires_registration_even_when_all_old_gates_pass(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(kit, 'read_inputs', return_value={}), \
             patch.object(kit, 'pending_inputs', return_value=['WP11.identity_unit']), \
             patch.object(kit, 'read_r1_slots', return_value={}), \
             patch.object(kit, 'read_ruling_1f_receipt', return_value=None), \
             patch.object(kit, 'require_ready'), patch.object(kit, 'require_sizing'), \
             patch.object(kit, 'validate_wp18_fixtures'):
            plan = Path(tmp)/kit.KIT/'collection_plan.json'
            plan.parent.mkdir(parents=True)
            plan.write_text(json.dumps({'runtime_requirements': {'km003c': kit.km003c.REQUIREMENT}}))
            with self.assertRaisesRegex(ValueError, 'registration_receipt'):
                kit.require_w1_ready(tmp)

    def test_receipt_binds_every_artifact_and_both_gate_reports(self):
        from joulewise.align.apple import v4_registration as reg
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in reg.ARTIFACTS:
                p = root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('synthetic\n')
            for stage in ('A', 'B'):
                p = root / f'docs/align/v4/gate-{stage}.md'
                p.write_text('synthetic gate\n')
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, check=True, capture_output=True).stdout.decode().strip()
            git('init', '-q')
            git('add', '.')
            git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                'commit', '-qm', 'Synthetic registration fixture')
            commit = git('rev-parse', 'HEAD')
            receipt = {'schema': reg.RECEIPT_SCHEMA, 'status': 'registered', 'commit': commit,
                       'artifacts': {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in reg.ARTIFACTS},
                       'rulings': {str(n): 'installed' for n in reg.RULINGS},
                       'gates': {s: {'verdict': 'ADMIT', 'path': f'docs/align/v4/gate-{s}.md',
                                    'sha256': hashlib.sha256((root/f'docs/align/v4/gate-{s}.md').read_bytes()).hexdigest()}
                                 for s in ('A', 'B')},
                       'lead_signature': 'lead: synthetic-test 2026-11-08'}
            reg.validate_receipt(receipt, root)
            for path in reg.ARTIFACTS:
                old = (root/path).read_bytes()
                (root/path).write_bytes(old+b'drift')
                with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'digest|drift'):
                    reg.validate_receipt(receipt, root)
                (root/path).write_bytes(old)
            for change in ('unsigned', 'gate', 'ruling', 'commit', 'path'):
                bad = deepcopy(receipt)
                if change == 'unsigned': bad['lead_signature'] = kit.UNSIGNED
                if change == 'gate': bad['gates']['B']['verdict'] = 'REFUSE'
                if change == 'ruling': bad['rulings']['4'] = 'pending'
                if change == 'commit': bad['commit'] = '0'*40
                if change == 'path': bad['gates']['A']['path'] = '../outside'
                with self.subTest(change=change), self.assertRaises(ValueError):
                    reg.validate_receipt(bad, root)

    def test_u3_is_pending_and_preserves_only_descriptive_replay_summaries(self):
        from joulewise.align.apple import v4_registration as reg
        pairs = [dict(session='p4', ordinals=[i, i+3], token_identical=True,
                      energies_j=[1000*(1-r/2), 1000*(1+r/2)])
                 for i, r in enumerate([-.004, -.002, 0, .002, .004, .006], 1)]
        result = reg.derive_u3(pairs, {'synthetic': 'a'*64})
        import statistics
        self.assertAlmostEqual(result['s_rel_sample'], statistics.stdev([-.004, -.002, 0, .002, .004, .006]))
        self.assertEqual(result['status'], 'PENDING')
        with self.assertRaisesRegex(ValueError, 'PENDING'):
            reg.u3_margin(30000, result)
        for field, value in [('token_identical', False), ('ordinals', [1, 2]), ('energies_j', [0, 1])]:
            bad = deepcopy(pairs)
            bad[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                reg.derive_u3(bad, {'synthetic': 'a'*64})

    def test_e_ref_rejects_ordinal_18(self):
        with self.assertRaisesRegex(ValueError, '5 and 17'):
            v4_estimands.u4_reference([10, 12], {5: 11, 18: 13}, {})
        self.assertEqual(v4_estimands.u4_reference([10, 12], {5: 11, 17: 13}, {})['E_ref_j'], 11.5)

    def test_v4_contrast_delivery_stage_and_positive_direction(self):
        runs = contrast(effect=15, noise=.1)
        for i, r in enumerate(runs):
            r.update(stage='a' if i < 4 else 'b', admission_slow_c=42 if r['arm']=='S' else 40,
                     g1_wait_s_by_turn=[1, 1])
        result = thermal_desk.deciding_experiment(runs, v4=True, delta_slow_c=2)
        self.assertEqual(result['verdict'], 'T CONFIRMED')
        self.assertEqual(result['df'], 3)
        for r in runs:
            r['turn_owned_j'] -= 30 if r['arm']=='S' else 0
        self.assertNotEqual(thermal_desk.deciding_experiment(runs, v4=True, delta_slow_c=2)['verdict'], 'T CONFIRMED')
        for r in runs:
            r.update(admission_slow_c=40, g1_wait_s_by_turn=[0, 0])
        self.assertEqual(thermal_desk.deciding_experiment(runs, v4=True, delta_slow_c=2)['reason'], 'treatment not delivered')

    def test_battery_topup_and_obc_attestation(self):
        from joulewise.align.apple import v4_registration as reg
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        topup = {'completed_at_epoch_s': 1000., 'source': 'synthetic'}
        self.assertTrue(reg.battery_arm(good, 'synthetic', topup, now_epoch_s=1060.)['admitted'])
        for key, value in [('current_capacity_pct', 98), ('instant_amperage_ma', 201),
                           ('is_charging', True), ('update_age_s', -1), ('update_age_s', 181),
                           ('passed', False), ('current_capacity_pct', None)]:
            with self.subTest(key=key, value=value):
                self.assertFalse(reg.battery_arm({**good, key: value}, 'synthetic', topup, now_epoch_s=1060.)['admitted'])
        self.assertFalse(reg.battery_arm(good, '', topup, now_epoch_s=1060.)['admitted'])
        # R02: completed-top-up timing is source/time-bound and fail-closed.
        self.assertFalse(reg.battery_arm(good, 'synthetic', None, now_epoch_s=1060.)['admitted'])
        self.assertFalse(reg.battery_arm(good, 'synthetic', topup)['admitted'])
        self.assertFalse(reg.battery_arm(good, 'synthetic', {**topup, 'source': ' '}, now_epoch_s=1060.)['admitted'])
        self.assertFalse(reg.battery_arm(good, 'synthetic', {**topup, 'completed_at_epoch_s': None}, now_epoch_s=1060.)['admitted'])
        self.assertFalse(reg.battery_arm(good, 'synthetic', topup, now_epoch_s=999.)['admitted'])
        self.assertTrue(reg.battery_arm(good, 'synthetic', topup, now_epoch_s=2800.)['admitted'])
        self.assertFalse(reg.battery_arm(good, 'synthetic', topup, now_epoch_s=2800.5)['admitted'])

    def test_wp19_requires_all_turns_and_live_x_with_static_proof(self):
        from joulewise.align.apple import v4_registration as reg
        fixtures = {arm: {'turns': [{'turn': i, 'prompt_token_ids': [i+1], 'output_token_ids': [i+2]} for i in range(3)]}
                    for arm in ('X', 'Y')}
        rendered = {arm: [t['prompt_token_ids'] for t in f['turns']] for arm, f in fixtures.items()}
        record = reg.wp19_identity(fixtures, rendered, fixtures['X']['turns'], live_source_sha256='b'*64)
        self.assertEqual(record['verdict'], 'pass')
        rendered['Y'][2] = [999]
        failed = reg.wp19_identity(fixtures, rendered, fixtures['X']['turns'][:2], live_source_sha256='b'*64)
        self.assertEqual(failed['verdict'], 'fail')
        self.assertEqual(failed['live_x_turns_compared'], 2)
        self.assertEqual(failed['contrast_predeclared'], 'INCONCLUSIVE: identity broken')

    def test_wp19_zero_native_turns_is_a_retained_nonveto_failure_never_a_pass(self):
        from joulewise.align.apple import v4_registration as reg
        fixtures = {arm: {'turns': [{'turn': i, 'prompt_token_ids': [i+1], 'output_token_ids': [i+2]} for i in range(3)]}
                    for arm in ('X', 'Y')}
        rendered = {arm: [t['prompt_token_ids'] for t in f['turns']] for arm, f in fixtures.items()}
        empty = reg.wp19_identity(fixtures, rendered, [], live_source_sha256='b'*64)
        self.assertEqual(reg.validate_wp19(empty), empty)
        for forged in ({'verdict': 'pass'}, {'live_x_complete': True}, {'live_x_identical': True},
                       {'live_x_turns_compared': -1}, {'contrast_predeclared': None}):
            with self.subTest(forged=forged), self.assertRaises(ValueError):
                reg.validate_wp19({**empty, **forged})
        full = reg.wp19_identity(fixtures, rendered, fixtures['X']['turns'], live_source_sha256='b'*64)
        with self.assertRaises(ValueError):
            reg.validate_wp19({**full, 'live_x_turns_compared': 0})

    def test_install_rechecks_generated_kit_before_host_operations(self):
        from scripts import align_v4_session as session
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'session.json').write_text(json.dumps({'measurement_root': tmp}))
            with patch.object(kit, 'generate', side_effect=ValueError('generated drift')) as checked:
                with self.assertRaisesRegex(ValueError, 'generated drift'):
                    session.install(tmp)
            checked.assert_called_once_with(tmp, check=True, source_root=tmp)

    def test_arm_records_battery_and_refuses_missing_attestation(self):
        from scripts import align_v4_session as session
        from tests.align.test_v4_cadence import passing_packet, write_battery_log
        packet = passing_packet()
        yes = lambda root, commit: True
        bound = lambda root, packet: True
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        with tempfile.TemporaryDirectory() as tmp, \
             patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'synthetic raw')) as observe:
            run = lambda argv: subprocess.CompletedProcess(argv, 0, 'synthetic pmset', '')
            log = write_battery_log(Path(tmp) / 'battery.jsonl', 5000., completion_age=100)        # (a) completed charge
            floated = write_battery_log(Path(tmp) / 'float.jsonl', 5000., completion_age=2400)     # (b) continuous float
            stale = write_battery_log(Path(tmp) / 'stale.jsonl', 5000., completion_age=2400, end_age=900)
            arm = lambda **kw: session.arm_checks('.', {}, obc_off_attested_by=kw.pop('obc', 'synthetic'), runner=run,
                                                  now=lambda: 5000., commit_check=yes, record_check=bound, **kw)
            self.assertFalse(session.arm_checks('.', {}, runner=run)['admitted'])
            self.assertFalse(arm(obc='', battery_log=log, next_arm_triage=packet)['admitted'])     # no attestation
            self.assertFalse(arm(next_arm_triage=packet)['admitted'])                              # no battery evidence
            record = arm(battery_log=log, next_arm_triage=packet)
            self.assertTrue(record['admitted'], record['reasons'])
            evidence = record['battery']['topup_evidence']
            self.assertEqual(evidence['basis'], 'completed_charge')
            self.assertTrue(evidence['source'].startswith('battery_log:completed_charge:'))
            self.assertEqual(record['battery']['topup']['source'], evidence['source'])
            record = arm(battery_log=floated, next_arm_triage=packet)
            self.assertTrue(record['admitted'], record['reasons'])
            self.assertEqual(record['battery']['topup_evidence']['basis'], 'continuous_float')
            self.assertFalse(arm(battery_log=stale, next_arm_triage=packet)['admitted'])           # stale latest observation
            self.assertFalse(arm(battery_log=Path(tmp) / 'missing.jsonl', next_arm_triage=packet)['admitted'])
            # L8: a failing pmset is evidence only
            bad_pmset = lambda argv: subprocess.CompletedProcess(argv, 1, '', 'pmset failed')
            with_bad = session.arm_checks('.', {}, obc_off_attested_by='synthetic', runner=bad_pmset, now=lambda: 5000.,
                                          commit_check=yes, record_check=bound, battery_log=log, next_arm_triage=packet)
            self.assertTrue(with_bad['admitted'], with_bad['reasons'])
            self.assertTrue(with_bad['battery']['pmset_batt']['evidence_only'])
            self.assertEqual(set(record['next_arm_triage']['checks']), set(__import__(
                'joulewise.align.apple.v4_cadence', fromlist=['x']).TRIAGE_IDS))
            # R12 B2: the triage list gates the arm itself.
            self.assertFalse(arm(battery_log=log)['admitted'])
            bad = passing_packet()
            bad['checks']['meter_reader_live']['status'] = 'fail'
            refused = arm(battery_log=log, next_arm_triage=bad)
            self.assertFalse(refused['admitted'])
            self.assertIn('next_arm_triage: triage meter_reader_live failed', refused['reasons'])
            self.assertEqual(record['battery']['raw_ioreg'], 'synthetic raw')
            self.assertEqual(observe.call_args.kwargs['phase'], 'arm_check')

    def test_hand_entered_topup_time_is_not_an_arm_input(self):
        from scripts import align_v4_session as session
        with self.assertRaises(TypeError):
            session.arm_checks('.', {}, topup_completed_at=4900., topup_source='typed by hand')

    def test_disk_gate_rejects_implicit_empty_offloads(self):
        from scripts import align_v4_session as session
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'config.json'
            path.write_text('{}')
            with patch('joulewise.align.r0_runner.validate_config', return_value={'offloads': []}):
                with self.assertRaisesRegex(ValueError, 'offloads'):
                    session.w1_disk_check(path, gate=lambda c: {'status': 'pass'})

    def test_d_max_turns_is_part_of_frozen_kit(self):
        plan = json.loads(kit.build_files()[kit.KIT/'collection_plan.json'])
        plan['members'][4]['spec']['max_turns'] = 11
        with self.assertRaisesRegex(ValueError, 'max_turns'):
            kit.check_window_reference_roles(plan)

    def test_u3_script_records_source_bytes(self):
        from scripts import align_v4_u3_bar as script
        pairs = [dict(session='synthetic', ordinals=[i, i+3], token_identical=True,
                      energies_j=[1000, 1000+i]) for i in (1, 2, 3)]
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp)/'pairs.json', Path(tmp)/'bar.json'
            source.write_text(json.dumps({'pairs': pairs}))
            self.assertEqual(script.main(['--input', str(source), '--output', str(output)]), 0)
            self.assertEqual(json.loads(output.read_bytes())['source_sha256'],
                             {'pairs.json': hashlib.sha256(source.read_bytes()).hexdigest()})

    def test_wp19_renders_fresh_history_from_recorded_outputs(self):
        from scripts import align_v4_wp19 as script
        from joulewise.align.interfaces import ChatMessage
        class Task:
            def reset(self, seed): self.seed = seed
            def system_prompt(self, condition): return 'system'
            def user_prompt(self): return 'user'
            def tool_schemas(self): return []
        class Tokenizer:
            def encode(self, text, **kwargs): return [len(text)]
            def decode(self, ids, **kwargs):
                assert kwargs.get('skip_special_tokens') is False, 'retain reasoning/tool markers'
                return 'recorded answer'
        class Endpoint:
            model_family = 'qwen3'
            def _render_prompt(self, history, tools):
                return '/'.join(m.content for m in history)
            def assistant_history_message(self, result):
                return ChatMessage('assistant', result.raw_usage['raw_text'])
        fixture = {'turns': [{'turn': i, 'prompt_token_ids': [0], 'output_token_ids': [1]} for i in range(2)]}
        rendered = script.render_fixture(fixture, Tokenizer(), Endpoint(), Task(), condition='benign', seed=1)
        self.assertEqual(rendered, [[len('system/user')], [len('system/user/recorded answer')]])

    def test_daytime_offloads_are_fresh_and_bound_without_live_rehash(self):
        from scripts import align_v4_session as session
        config = {'offloads': [{'label': 'synthetic', 'inventory': '/synthetic/inventory',
                               'destination': '/synthetic/destination'}], 'disk_path': '/synthetic/disk'}
        with tempfile.TemporaryDirectory() as tmp:
            path, receipt_path = Path(tmp)/'config.json', Path(tmp)/'receipt.json'
            freshness = {'max_age_s': 100, 'lead_signature': 'lead: synthetic 2026-11-08'}
            path.write_text(json.dumps({**config, 'daytime_offload_receipt': str(receipt_path),
                                        'daytime_offload_freshness': freshness}))
            receipt = session.daytime_offload_receipt(config, now=lambda: 1000, freshness_policy=freshness,
                gate=lambda c: {'status': 'pass', 'offloads': [{'label': 'synthetic', 'pass': True,
                    'observed': [{'path': 'fixture', 'sha256': 'a'*64}]}]})
            receipt_path.write_text(json.dumps(receipt))
            with patch('joulewise.align.r0_runner.validate_config', side_effect=lambda c: c), \
                 patch('shutil.disk_usage', return_value=type('Disk', (), {'free': 100_000_000_000})()), \
                 patch('joulewise.align.r0_host.w1_disk_gate', side_effect=AssertionError('must not rehash')):
                self.assertEqual(session.w1_disk_check(path, now=lambda: 1001)['status'], 'pass')
                with self.assertRaisesRegex(ValueError, 'stale'):
                    session.w1_disk_check(path, now=lambda: 1000+86401)
                receipt['config_sha256'] = 'f'*64
                receipt_path.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(ValueError, 'binding'):
                    session.w1_disk_check(path, now=lambda: 1001)

    def test_desk_selects_sentinel_and_prints_warm_reference_and_b_counts(self):
        from joulewise.align.apple import v4_registration as reg
        records = []
        for ordinal in (5, 17, 18):
            r = member(str(ordinal))
            r.update(ordinal=ordinal, role='D', status='completed', turns=3, x_flags=[],
                     window_reference={'fast_c': 41, 'slow_c': 43},
                     cache_statistics={'rebuilds': 1, 'trims': 2},
                     battery={'soc_pct': 100, 'charger_w': 90}, configuration={
                         'max_turns': 12, 'max_tokens': 4096, 'deadman_s': 1000,
                         'max_episode_decode_tokens': 6144})
            records.append(r)
        report = reg.desk_diagnostics(records, r1_soak={'fast_c': 40, 'slow_c': 42})
        self.assertEqual(report['sentinel']['ordinal'], 5)
        self.assertTrue(report['warm_reference']['thermal.reference_warm'])
        self.assertEqual(report['rebuilds'][0]['cache_statistics']['rebuilds'], 1)
        records[0]['x_flags'] = ['X2']
        self.assertEqual(reg.desk_diagnostics(records)['sentinel']['ordinal'], 18)
        records[2]['x_flags'] = ['X7']
        self.assertIsNone(reg.desk_diagnostics(records)['sentinel']['ordinal'])
        records[0]['flags'] = ['battery.member_span']
        records[1]['flags'] = ['battery.member_span']
        self.assertFalse(reg.desk_diagnostics(records)['battery_windows']['synthetic']['bar_pass'])

    def test_v4_thermal_cli_refuses_missing_registered_bar(self):
        from scripts import align_v4_thermal_desk as script
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'manifest.json'
            path.write_text('{"members": []}')
            with self.assertRaisesRegex(ValueError, 'u3_bar'):
                script.main(['--manifest', str(path), '--output', str(Path(tmp)/'out'),
                             '--registration-dir', str(Path(tmp))])

    def test_v4_u4_does_not_gate_on_anchor_sigma_and_positions_need_six_trajectories(self):
        r = member()
        r['window'] = 'D3'
        result = thermal_desk.window_report([r], v4=True, cross_windows={
            'synthetic': {'anchors': {'status': 'fail'}, 'sentinels': {'status': 'pass'}}})
        self.assertEqual(result['model_windows']['synthetic/D3']['U4']['status'], 'pass')
        rows = [{'turn_position': 1, 'residual_j': 1, 'trajectory': 'one'} for _ in range(6)]
        positions = v4_estimands.d_turn_position_means(rows)
        self.assertFalse(positions['evaluable'][1])
        for i, row in enumerate(rows): row['trajectory'] = str(i)
        self.assertTrue(v4_estimands.d_turn_position_means(rows)['evaluable'][1])

    def test_warm_reference_uses_explicit_registered_r1_soak(self):
        from scripts import align_v4_thermal_desk as script
        from joulewise.align.apple.r1_runtime import SOAK_REFERENCE_SCHEMA
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'inputs.json').write_text(json.dumps({'R1': {'thermal_policy': {
                'sensors': {'s_fast': 'fast', 's_slow': 'slow'}}}}))
            (root/'r1_soak_reference.json').write_text(json.dumps({'schema': SOAK_REFERENCE_SCHEMA,
                'sensors_c': {'fast': 40, 'slow': 42}}))
            self.assertEqual(script.r1_soak_c(root), {'fast_c': 40, 'slow_c': 42})

    def test_session_desk_applies_relative_u3_and_frozen_d_cohort(self):
        from scripts import align_v4_session as session
        from joulewise.align.apple.v4_registration import derive_u3
        bar = derive_u3([dict(session='p4', ordinals=[i, i+3], token_identical=True,
            energies_j=[1000, 1000+i*2]) for i in range(1, 7)], {'synthetic': 'a'*64})
        rows = [{'run_id': str(i), 'role': 'D', 'ordinal': i, 'ac_powermode': 0,
                 **({'replay_of': '5'} if i == 17 else {})} for i in (5, 17)]
        records = [member(str(i), energy=30000+(200 if i==17 else 0)) for i in (5, 17)]
        for record in records:
            record.update(configuration=dict(max_tokens=4096, max_turns=12, deadman_s=1000,
                                              max_episode_decode_tokens=6144),
                          cache_statistics={'rebuilds': 0}, cohort_identity=dict(model_source='tiny', model_revision='synthetic',
                          runtime_sha256='a'*64, execution_policy_sha256='b'*64))
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(session.pilot, '_member_rows', return_value=rows), \
             patch.object(session, 'bundle_ac_powermode', return_value=0), \
             patch('scripts.align_v4_thermal_desk.registration_evidence', return_value=(bar, {})), \
             patch('scripts.align_v4_thermal_desk.enrich_record', side_effect=lambda r, p: r), \
             patch('scripts.align_v4_thermal_desk.r1_soak_c', return_value={}), \
             patch('joulewise.align.apple.thermal_desk.read_bundle_record', side_effect=lambda p: deepcopy(records[0 if p.name=='5' else 1])), \
             patch.object(kit, 'read_inputs', return_value={'R1': {'thermal_policy': {'delta_slow_c': 2}}}):
            def check():
                return session.powermode_desk_check(state={'measurement_root': tmp}, members=[],
                                                   runs_root=tmp, kit_path=kit.KIT)[0]
            result = check()
            self.assertFalse(result['v4_synthetic/W1_U3'])  # R11 leaves U3 pending; no historical constant
            self.assertTrue(result['v4_D_cohort'])
            records[1]['configuration']['max_turns'] = 11
            self.assertFalse(check()['v4_D_cohort'])


if __name__ == '__main__':
    unittest.main()
