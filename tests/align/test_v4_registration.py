"""Registration blockers: synthetic records only; no native probes or weights."""
from tests.git_fixture import init_git_fixture
from tests.align.test_v4_arm_watchdog_check import acceptance as _watchdog_acceptance
from contextlib import ExitStack
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
from joulewise.align.apple import thermal_desk, v4_estimands, v4_registration as reg
from tests.align.test_thermal_desk import member, contrast


class RegistrationTests(unittest.TestCase):
    def test_w1_requires_registration_even_when_all_old_gates_pass(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(kit, 'read_inputs', return_value={}), \
             patch.object(kit, 'pending_inputs', return_value=['WP11.identity_unit']), \
             patch.object(kit, 'read_r1_slots', return_value={}), \
             patch.object(kit, 'require_ready'), patch.object(kit, 'require_sizing'), \
             patch.object(kit, 'check_w1_record_keys'), \
             patch.object(kit, 'validate_wp18_fixtures'):
            # check_w1_record_keys (RL-84 P-2) is witnessed in tests.align.test_w1_tf08_record; this test
            # isolates the registration requirement, like the other gates patched above.
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
            init_git_fixture(root, '-q')
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
        from tests.align.test_v4_cadence import arm_seams, passing_packet, write_battery_log
        packet = passing_packet()
        yes = lambda root, commit: True
        bound = lambda root, packet: True
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        with tempfile.TemporaryDirectory() as tmp, \
             patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'synthetic raw')) as observe, \
             patch.object(session, 'held_window_check', return_value={'ok': True, 'reasons': [], 'synthetic': True}):
            run = lambda argv: subprocess.CompletedProcess(argv, 0, 'synthetic pmset', '')
            log = write_battery_log(Path(tmp) / 'battery.jsonl', 5000., completion_age=100)        # (a) completed charge
            floated = write_battery_log(Path(tmp) / 'float.jsonl', 5000., completion_age=2400)     # (b) continuous float
            stale = write_battery_log(Path(tmp) / 'stale.jsonl', 5000., completion_age=2400, end_age=900)
            arm = lambda **kw: session.arm_checks('.', {}, obc_off_attested_by=kw.pop('obc', 'synthetic'), runner=run,
                                                  now=lambda: 5000., **arm_seams(), **kw)
            self.assertFalse(session.arm_checks('.', {}, watchdog_check=_watchdog_acceptance, runner=run, meter_probe=lambda root: {'live': False})['admitted'])
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
                                          battery_log=log, next_arm_triage=packet, **arm_seams())
            self.assertTrue(with_bad['admitted'], with_bad['reasons'])
            self.assertTrue(with_bad['battery']['pmset_batt']['evidence_only'])
            self.assertEqual(set(record['next_arm_triage']['checks']), set(__import__(
                'joulewise.align.apple.v4_cadence', fromlist=['x']).TRIAGE_IDS))
            # R12 B2: the triage list gates the arm itself.
            self.assertFalse(arm(battery_log=log)['admitted'])
            bad = passing_packet()
            bad['checks']['capture_faults']['status'] = 'fail'
            refused = arm(battery_log=log, next_arm_triage=bad)
            self.assertFalse(refused['admitted'])
            self.assertIn('next_arm_triage: triage capture_faults failed', refused['reasons'])
            # the live meter is arm-computed (R12 B2 / lead ruling): a dead one refuses whatever the packet says
            dead = session.arm_checks('.', {}, obc_off_attested_by='synthetic', runner=run, now=lambda: 5000.,
                                      battery_log=log, next_arm_triage=packet,
                                      **{**arm_seams(), 'meter_probe': lambda root: {'live': False}})
            self.assertFalse(dead['admitted'])
            self.assertIn('next_arm_triage: triage meter_reader_live failed', dead['reasons'])
            self.assertEqual(record['battery']['raw_ioreg'], 'synthetic raw')
            self.assertEqual(observe.call_args.kwargs['phase'], 'arm_check')

    def test_arm_derives_float_across_a_window_from_its_own_smc_journal(self):
        # Lead ruling: no sampler during a window; the window's 1 Hz SMC capture carries the float.
        import json as _json
        from scripts import align_v4_session as session
        from tests.align.test_v4_cadence import arm_seams, passing_packet
        from tests.align.test_v4_topup import window_journal
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        now = 50000.
        with tempfile.TemporaryDirectory() as tmp, \
             patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'raw')), \
             patch.object(session, 'held_window_check', return_value={'ok': True, 'reasons': [], 'synthetic': True}):
            run = lambda argv: subprocess.CompletedProcess(argv, 0, 'pmset', '')
            rows = lambda start, end, charge_until=None: [
                {'schema': 'joulewise.battery_float.v1', 'probe_error': False, 'wall_time_s': float(t),
                 'external_connected': True, 'is_charging': charge_until is not None and t < charge_until,
                 'current_capacity_pct': 97 if charge_until is not None and t < charge_until else 100}
                for t in range(start, end+1, 100)]
            first = Path(tmp) / 'first.jsonl'
            first.write_text(''.join(_json.dumps(r) + '\n' for r in rows(1000, 1900, charge_until=1200)))
            second = Path(tmp) / 'second.jsonl'
            second.write_text(''.join(_json.dumps(r) + '\n' for r in rows(46000, 50000)))
            journal = Path(tmp) / 'window-battery.jsonl'
            journal.write_text(''.join(_json.dumps(r) + '\n' for r in window_journal(2000, 45900)))
            arm = lambda **kw: session.arm_checks(
                '.', {}, obc_off_attested_by='synthetic', runner=run, now=lambda: now,
                next_arm_triage=passing_packet(), **arm_seams(), **kw)
            record = arm(battery_log=[first, second], window_battery_journal=[journal])
            self.assertTrue(record['admitted'], record['reasons'])
            evidence = record['battery']['topup_evidence']
            self.assertEqual(evidence['basis'], 'continuous_float')
            self.assertEqual(evidence['sources'], {'between_window_logs': 2, 'window_journals': 1,
                                                   'source_sha256': evidence['sources']['source_sha256']})
            self.assertEqual(len(evidence['sources']['source_sha256']), 3)
            missing = arm(battery_log=[first, second])                      # the window journal is missing
            self.assertFalse(missing['admitted'])
            self.assertIn('gap above', missing['battery']['topup_evidence']['reasons'][0])

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
        self.assertFalse(reg.desk_diagnostics(records)['battery_windows']['synthetic/W1']['bar_pass'])

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
        from tests.align.v4_registration_fixtures import signed_bar, battery_policy
        bar = signed_bar()
        rows = [{'run_id': str(i), 'role': 'D', 'ordinal': i, 'ac_powermode': 0,
                 **({'replay_of': '5'} if i == 17 else {})} for i in (5, 17)]
        records = [member(str(i), energy=30000+(200 if i==17 else 0)) for i in (5, 17)]
        for record in records:
            record.update(configuration=dict(max_tokens=4096, max_turns=12, deadman_s=1000,
                                              max_episode_decode_tokens=6144),
                          cache_statistics={'rebuilds': 0}, u3_configuration_sha256='b'*64,
                          battery={'status': 'observed', 'source_sha256': 'a'*64, 'flags': []},
                          cohort_identity=dict(model_source='tiny', model_revision='synthetic',
                          runtime_sha256='a'*64, execution_policy_sha256='b'*64))
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(session.pilot, '_member_rows', return_value=rows), \
             patch.object(session, 'bundle_ac_powermode', return_value=0), \
             patch('scripts.align_v4_thermal_desk.registration_evidence', return_value=(bar, {})), \
             patch('scripts.align_v4_thermal_desk.enrich_record', side_effect=lambda r, p: r), \
             patch('joulewise.align.apple.v4_battery.attach', side_effect=lambda r, p, j: r), \
             patch('scripts.align_v4_thermal_desk.r1_soak_c', return_value={}), \
             patch('joulewise.align.apple.thermal_desk.read_bundle_record', side_effect=lambda p: deepcopy(records[0 if p.name=='5' else 1])), \
             patch.object(kit, 'read_inputs', return_value={'R1': {'thermal_policy': {'delta_slow_c': 2}}}):
            registration_dir = Path(tmp)/kit.KIT/'registration'
            registration_dir.mkdir(parents=True)
            (registration_dir/'battery_window_policy.json').write_text(json.dumps(battery_policy()))
            def check():
                return session.powermode_desk_check(state={'measurement_root': tmp}, members=[],
                                                   runs_root=tmp, kit_path=kit.KIT)[0]
            result = check()
            self.assertTrue(result['v4_synthetic/W1_U3'])
            self.assertTrue(result['v4_B_bar'])
            self.assertTrue(result['v4_D_cohort'])
            records[1]['configuration']['max_turns'] = 11
            self.assertFalse(check()['v4_D_cohort'])


class R1ExecutedSourceTests(unittest.TestCase):
    def test_condition13_names_exactly_the_ten_ruled_sources(self):
        self.assertEqual(set(reg.R1_EXECUTED_SOURCES), {
            "scripts/align_r1_rehearsal.py", "joulewise/align/apple/r1_runtime.py",
            "configs/align/v4/r1_runtime.json", "joulewise/align/apple/r1_phase_table.py",
            "joulewise/align/apple/workload.py", "joulewise/align/apple/thermal.py",
            "joulewise/align/apple/thermal_gates.py",
            "scripts/align_r1_runtime.py", "joulewise/align/apple/r1_runtime_contract.py",
            "joulewise/align/apple/smc_enumeration.py",
        })
        self.assertEqual(len(reg.R1_EXECUTED_SOURCES), 10)

    def test_condition13_changes_each_file_commit_and_missing_phase_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
            from tests.git_fixture import init_git_fixture
            init_git_fixture(root, "-q")
            for path in reg.R1_EXECUTED_SOURCES:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(path + "\n")
            git("add", ".")
            git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid", "commit", "-qm", "fixture")
            commit = git("rev-parse", "HEAD")
            reg.verify_r1_executed_sources(root, {"executed_commit": commit})
            for path in reg.R1_EXECUTED_SOURCES:
                target = root / path
                raw = target.read_bytes()
                target.write_bytes(raw + b"x")
                with self.subTest(path=path), self.assertRaisesRegex(ValueError, "differs"):
                    reg.verify_r1_executed_sources(root, {"executed_commit": commit})
                target.write_bytes(raw)
            with self.assertRaises(ValueError):
                reg.verify_r1_executed_sources(root, {"executed_commit": "0" * 40})
            (root / "joulewise/align/apple/r1_phase_table.py").unlink()
            with self.assertRaisesRegex(ValueError, "missing"):
                reg.verify_r1_executed_sources(root, {"executed_commit": commit})


class C1ArmReceiptTests(unittest.TestCase):
    EXECUTABLES = (
        'scripts/align_v4_series_release.py',
        'joulewise/align/apple/s_rows.py',
        'joulewise/align/apple/rl176.py',
        'joulewise/align/apple/rl176_phases.py',
    )
    SHARED_DEPENDENCY = 'joulewise/align/apple/harvest_offload.py'
    RECEIPT_PATH = reg.REGISTRATION + 'registration_receipt.json'

    def setUp(self):
        from joulewise.align.apple import powermode
        from scripts import align_v4_series as series, align_v4_session as session
        from tests.align import v4_registration_fixtures as fixtures

        self.series, self.session = series, session
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo = self.root / 'source'
        self.repo.mkdir()
        init_git_fixture(self.repo, '-q')
        self.git('config', 'user.name', 'Synthetic')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')

        self.expanded = set(reg.ARTIFACTS) | set(self.EXECUTABLES) | {self.SHARED_DEPENDENCY}
        for path in self.expanded:
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f'# Inert fixture for {path}\n')
        self.plan_paths = {window: directory / 'collection_plan.json'
                           for window, directory in [('W1', kit.KIT), ('C1', series.kit_path('C1'))]}
        for window, path in self.plan_paths.items():
            self.write_json(path, {'synthetic_window': window, 'runtime_requirements': {
                'ac_powermode': 0, 'km003c': kit.km003c.REQUIREMENT,
            }})
        manifest = series.candidate()
        (self.repo / series.MANIFEST).write_bytes(series.raw_json(manifest))
        evidence_raw = b'{"synthetic":"pass"}'
        self.write_json(series.ADMISSION, {
            'schema': series.ADMISSION_SCHEMA, 'lead_signature': 'lead: synthetic 2026-11-19',
            'manifest_sha256': self.sha(series.MANIFEST),
            'w1_collection_sha256': self.sha(self.plan_paths['W1']),
            'choices': {k: manifest[k] for k in ('d_mapping', 'test_windows', 'test_shape', 'sentinel')},
            'evidence': {k: {'content_utf8': evidence_raw.decode(), 'sha256': reg.digest(evidence_raw),
                             'pointer': '/synthetic'} for k in ('scorer_fit_contract', 'seed_allocation',
                                'r13_r14_gate', 'paired_build_agreement', 'w1_clearance')},
        })
        gates = {}
        for stage in ('A', 'B'):
            path = f'docs/align/v4/synthetic-{stage}.json'
            self.write_json(path, {'synthetic_stage': stage, 'verdict': 'ADMIT'})
            gates[stage] = {'verdict': 'ADMIT', 'path': path, 'sha256': self.sha(path)}
        r1_commit = self.commit('Synthetic executed sources')
        self.write_json(reg.REGISTRATION + 'r1_slots.json', {'executed_commit': r1_commit})
        export = fixtures.export()
        transfer = 'synthetic-transfer.json'
        source = 'synthetic-u3.json'
        self.write_json(transfer, {'transfer': 'synthetic'})
        export['policy']['transfer_justification_sha256'] = self.sha(transfer)
        self.write_json(source, export)
        bar = reg.derive_u3(export['pairs'], {p: self.sha(p) for p in (transfer, source)}, policy=export['policy'])
        u3_gate = 'docs/align/v4/synthetic-u3-gate.json'
        gate = {'verdict': 'ADMIT', 'derivation_sha256': bar['derivation_sha256']}
        self.write_json(u3_gate, gate)
        bar.update(status='registered', lead_signature='lead: synthetic 2026-11-19',
                   independent_gate={**gate, 'path': u3_gate, 'sha256': self.sha(u3_gate)})
        self.write_json(reg.REGISTRATION + 'u3_bar.json', bar)
        self.write_json(reg.REGISTRATION + 'battery_window_policy.json', fixtures.battery_policy())
        self.write_json(reg.REGISTRATION + 'wp19_receipt.json',
                        reg.wp19_identity({arm: {'turns': [{'turn': 0, 'prompt_token_ids': [1],
                                                          'output_token_ids': [2]}]} for arm in ('X', 'Y')},
                                          {}, [], live_source_sha256='a' * 64))
        self.signed_commit = self.commit('Synthetic reviewed bytes and reports')
        self.combined = dict(schema=reg.RECEIPT_SCHEMA, status='registered', commit=self.signed_commit,
                             artifacts={p: self.sha(p) for p in sorted(self.expanded)}, gates=gates,
                             rulings={str(n): 'installed' for n in reg.RULINGS},
                             lead_signature='lead: synthetic 2026-11-19')
        self.legacy = {**self.combined, 'artifacts': {p: self.combined['artifacts'][p] for p in reg.ARTIFACTS}}

        stack = self.enterContext(ExitStack())
        # Leave the generated-byte comparisons, registration and series admission real.
        # The stand-in materializers never run an inventoried source file.
        plans = {window: {path: (self.repo / path).read_bytes()} for window, path in self.plan_paths.items()}
        stack.enter_context(patch.object(kit, 'build_files', return_value=plans['W1']))
        stack.enter_context(patch.object(series, 'build_files', side_effect=lambda root, manifest, name, **_: plans[name]))
        stack.enter_context(patch.object(kit, 'read_inputs', return_value={}))
        stack.enter_context(patch.object(kit, 'pending_inputs', return_value=['WP11.identity_unit']))
        stack.enter_context(patch.object(kit, 'read_r1_slots', return_value={}))
        for check in ('check_w1_record_keys', 'require_ready', 'require_sizing', 'validate_wp18_fixtures'):
            stack.enter_context(patch.object(kit, check))
        self.stager = stack.enter_context(patch.object(session.pilot, 'prepare', side_effect=self.stage))
        self.installer = stack.enter_context(patch.object(session.pilot, 'install', return_value={'exit_code': 0}))
        stack.enter_context(patch.object(session, '_arm_and_install',
                                         side_effect=lambda path, *_args, **_kw: self.installer(path)))
        stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
        stack.enter_context(patch.object(session, '_prepare_weight_digests', return_value={'ok': True, 'reasons': []}))
        stack.enter_context(patch.object(session, 'runtime_stack_preflight', return_value={'ok': True, 'reasons': []}))
        stack.enter_context(patch.object(session, 'frequency_word_preflight', return_value={'ok': True}))
        stack.enter_context(patch.object(session, '_termination_handlers', return_value=(lambda: None, lambda: None)))
        stack.enter_context(patch.object(powermode, 'host_lock_preflight', return_value={'synthetic': True}))
        stack.enter_context(patch.object(powermode, 'host_state_override', return_value=self.root))
        self.host_marker = stack.enter_context(patch.object(powermode, 'host_marker_path',
                                                            return_value=self.root / 'synthetic-host-marker'))
        host_lock = stack.enter_context(patch.object(powermode, 'HostLock'))
        host_lock.return_value.acquire.return_value = True
        stack.enter_context(patch.object(powermode, 'enter_high_power', side_effect=self.no_host))
        stack.enter_context(patch.object(session, '_require_night_job_absent', side_effect=self.no_host))

    @staticmethod
    def no_host(*_args, **_kwargs):
        raise AssertionError('external host command called')

    @staticmethod
    def stage(root, session_root, *, kit, pack_id, **_):
        view = session_root / 'measurement'
        return dict(measurement_root=str(view), source_measurement_root=str(root),
                    registration_dir=str(view / kit / 'registration'), preparation_status='STAGED',
                    inputs={'pack_root': str(view / 'configs/campaigns' / pack_id)})

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, text=True).strip()

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')

    def write_json(self, path, value):
        path = self.repo / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + '\n')

    def sha(self, path):
        return reg.digest((self.repo / path).read_bytes())

    def prepare(self, window):
        work = Path(tempfile.mkdtemp(dir=self.root))
        state = self.session.prepare(self.repo, work, window_id=window, power_runner=self.no_host)
        self.assertEqual(state['v4_series']['window_id'], window)
        return work, state

    def install(self, work):
        with patch.object(self.session, 'validate_series_state',
                          wraps=self.session.validate_series_state) as recheck:
            self.assertEqual(self.session.install(work, runner=self.no_host), {'exit_code': 0})
        recheck.assert_called_once()
        self.installer.assert_called_once_with(work)

    def assert_prepare_refuses(self, receipt, reason, *, window='C1'):
        self.write_json(self.RECEIPT_PATH, receipt)
        with self.assertRaisesRegex(ValueError, reason):
            self.prepare(window)
        self.stager.assert_not_called()
        self.installer.assert_not_called()

    def assert_recheck_refuses(self, work, state, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.session.validate_series_state(state)
        self.session.pilot.h.write(work / 'session.json', state)
        with self.assertRaisesRegex(ValueError, reason):
            self.session.install(work, runner=self.no_host)
        self.host_marker.assert_not_called()
        self.installer.assert_not_called()

    def test_legacy_w1_receipt_only_admits_w1(self):
        self.write_json(self.RECEIPT_PATH, self.legacy)
        work, state = self.prepare('W1')
        self.assertEqual(self.session.validate_series_state(state)['synthetic_window'], 'W1')
        self.install(work)
        self.stager.reset_mock()
        self.installer.reset_mock()
        self.assert_prepare_refuses({**self.legacy, 'series_release': False}, 'artifact set incomplete')

    def test_combined_receipt_admits_w1_and_c1(self):
        self.write_json(self.RECEIPT_PATH, self.combined)
        kit.generate(self.repo, check=True, source_root=self.repo)
        for window in ('W1', 'C1'):
            with self.subTest(window=window):
                work, state = self.prepare(window)
                self.assertEqual(self.session.validate_series_state(state)['synthetic_window'], window)
                self.install(work)
                self.installer.reset_mock()

    def test_every_c1_executable_binding_is_checked_at_prepare(self):
        for path in self.EXECUTABLES:
            for defect, reason in [('missing', 'artifact set incomplete'), ('null', 'invalid digest'),
                                   ('wrong sha256', 'digest drift')]:
                with self.subTest(path=path, defect=defect):
                    receipt = deepcopy(self.combined)
                    if defect == 'missing':
                        del receipt['artifacts'][path]
                    else:
                        receipt['artifacts'][path] = None if defect == 'null' else reg.digest(b'wrong bytes')
                    self.assert_prepare_refuses(receipt, reason)

    def test_every_c1_executable_is_rechecked_for_working_byte_drift(self):
        self.write_json(self.RECEIPT_PATH, self.combined)
        work, state = self.prepare('C1')
        for path in self.EXECUTABLES:
            with self.subTest(path=path):
                target = self.repo / path
                original = target.read_bytes()
                target.write_bytes(original + b'# working copy drift\n')
                try:
                    self.assert_recheck_refuses(work, state, 'digest drift: ' + path)
                finally:
                    target.write_bytes(original)

    def test_current_bytes_cannot_replace_the_signed_commit_binding(self):
        path = self.EXECUTABLES[0]
        (self.repo / path).write_bytes(b'# Different working source, never committed\n')
        receipt = deepcopy(self.combined)
        receipt['artifacts'][path] = self.sha(path)
        self.assert_prepare_refuses(receipt, 'digest drift: ' + path)

    def test_invalid_commit_gate_dependency_and_extra_key_refuse(self):
        for defect in ('missing commit', 'unknown commit', 'gate report', 'shared dependency', 'extra key'):
            with self.subTest(defect=defect):
                receipt = deepcopy(self.combined)
                if defect == 'missing commit':
                    del receipt['commit']
                    reason = 'requires a full commit'
                elif defect == 'unknown commit':
                    receipt['commit'] = '0' * 40
                    reason = 'missing committed artifact'
                elif defect == 'gate report':
                    receipt['gates']['B']['sha256'] = receipt['gates']['A']['sha256']
                    reason = 'digest drift: docs/align/v4/synthetic-B.json'
                else:
                    reason = 'artifact set incomplete'
                    if defect == 'shared dependency':
                        del receipt['artifacts'][self.SHARED_DEPENDENCY]
                    else:
                        receipt['artifacts']['synthetic-extra.py'] = reg.digest(b'extra')
                self.assert_prepare_refuses(receipt, reason)

    def test_gate_report_cannot_override_an_inventoried_digest(self):
        path = 'docs/align/v4/DEVIATIONS.md'
        for window, form in [('W1', self.legacy), ('C1', self.combined)]:
            with self.subTest(window=window):
                receipt = deepcopy(form)
                receipt['artifacts'][path] = None
                receipt['gates']['B'].update(path=path, sha256=self.sha(path))
                self.assert_prepare_refuses(receipt, 'invalid digest: ' + path, window=window)

    def test_recheck_refuses_legacy_substitution_and_selected_window_downgrade(self):
        self.write_json(self.RECEIPT_PATH, self.combined)
        work, state = self.prepare('C1')
        self.write_json(self.RECEIPT_PATH, self.legacy)
        self.assert_recheck_refuses(work, state, 'artifact set incomplete')
        altered = deepcopy(state)
        altered['v4_series'].update(window_id='W1', role='selection')
        self.assert_recheck_refuses(work, altered, 'prepared series.*(window|kit)')
        del altered['v4_series']
        self.session.pilot.h.write(work / 'session.json', altered)
        with self.assertRaisesRegex(ValueError, 'prepared series.*(window|kit)'):
            self.session.install(work, runner=self.no_host)
        self.host_marker.assert_not_called()
        self.installer.assert_not_called()

    def test_w1_does_not_retry_an_invalid_combined_receipt_as_legacy(self):
        for path in self.EXECUTABLES:
            with self.subTest(path=path):
                receipt = deepcopy(self.combined)
                receipt['artifacts'][path] = None
                self.assert_prepare_refuses(receipt, 'invalid digest: ' + path, window='W1')

    def test_two_receipts_bind_distinct_git_identities_before_c1(self):
        self.write_json(self.RECEIPT_PATH, self.legacy)
        legacy_pin = self.commit('Synthetic W1 receipt issued')
        with patch.object(reg, 'validate_receipt', wraps=reg.validate_receipt) as checked:
            self.prepare('W1')
        checked.assert_called_once()
        self.assertEqual(checked.call_args.args[0], self.legacy)
        # The earlier receipt remains in history. The second signature selects
        # a different Git commit, before the first series member is prepared.
        expanded_receipt = {**self.combined, 'commit': legacy_pin}
        self.write_json(self.RECEIPT_PATH, expanded_receipt)
        expanded_pin = self.commit('Synthetic combined receipt issued before C1')
        self.git('merge-base', '--is-ancestor', legacy_pin, expanded_pin)
        with patch.object(reg, 'validate_receipt', wraps=reg.validate_receipt) as checked:
            work, state = self.prepare('C1')
        checked.assert_called_once()
        self.assertEqual(checked.call_args.args[0], expanded_receipt)
        self.assertEqual(self.session.validate_series_state(state)['synthetic_window'], 'C1')
        self.install(work)
        self.git_witness = {
            'legacy_receipt_commit': legacy_pin,
            'legacy_receipt_blob': self.git('rev-parse', f'{legacy_pin}:{self.RECEIPT_PATH}'),
            'combined_receipt_commit': expanded_pin,
            'combined_receipt_blob': self.git('rev-parse', f'{expanded_pin}:{self.RECEIPT_PATH}'),
            'legacy_signed_commit': self.signed_commit,
            'combined_signed_commit': expanded_receipt['commit'],
        }
        self.assertNotEqual(self.git_witness['legacy_receipt_blob'], self.git_witness['combined_receipt_blob'])


if __name__ == '__main__':
    unittest.main()
