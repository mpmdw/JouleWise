"""Fixture-only G2-a harvest orchestration; no live hardware evidence claimed."""
from contextlib import ExitStack, redirect_stdout
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest import mock
from scripts import harvest_g2a_window as harvest
from scripts import generate_g2a_probe_inputs as producer
from scripts import summarize_g2a_prefill_probe as summary
from scripts.gen_g2_phase_d import G2A_CAMPAIGN_POLICY_PATH
from tests.test_gen_g2a_window import G2aFixture, tree
from tests import test_generate_g2a_probe_inputs as producer_tests
from tests.test_generate_g2a_probe_inputs import IDENTITY, T1, ACCEPTANCE
from tests.test_summarize_g2a_prefill_probe import retained_metadata, retained_summary, runner_config_bytes
from joulewise import calibration_ledger as real_ledger
from scripts import recover_calibration_ledger as recovery
from tests.git_fixture import init_git_fixture
from tests.test_calibration_bracketing import _unissued_acceptance_fixture, _unissued_acceptance_fixture_bytes


class G2aHarvestTests(unittest.TestCase):
    def setUp(self):
        self.f = G2aFixture()
        self.addCleanup(self.f.close)
        self.p = producer_tests.GenerateG2AProbeInputsTests('test_any_ledger_snapshot_refusal_is_fatal')
        self.p.setUp()
        self.addCleanup(self.p.doCleanups)
        self.p.root = self.f.g2a
        wp = self.f.g2a/'window-plan'
        for name in ('calibration_plan.json', 'identity-epoch.json', 't1-bindings.json'):
            (wp/name).unlink()
        self.p._build()
        self.ledger = self.f.measurement/'runs/calibration_observation_ledger.jsonl'
        self.pin = self.f.measurement/'configs/calibration/calibration_ledger_head.json'
        self.binding = {'ledger': {'path': str(self.ledger), 'sha256': harvest.sha(self.ledger),
                        'head_sequence': 1, 'head_digest': 'b'*64},
                        'head_pin': {'path': str(self.pin), 'sha256': harvest.sha(self.pin)}}
        with mock.patch.object(producer, '_derive_live_vectors', return_value=(IDENTITY, T1, ACCEPTANCE)), \
                mock.patch.object(producer, '_authenticate_ledger_and_acceptance', return_value=self.binding):
            producer.bind_window(root=self.f.g2a, ledger=self.ledger, head_pin=self.pin,
                campaign_policy=producer.REPO_ROOT/'configs/campaign_policies/quiet_mac_p2_production.json',
                power_policy='ac_high_power', window_id=self.f.plan_id,
                session_id=self.f.plan_id+'-calibration', evidence_root_id='evidence-'+self.f.plan_id)
        self.value = harvest.read(wp/'g2a-input-inventory.json')
        ladder = harvest.read(wp/'prefill-prompt-ladder.json')
        for stage in self.value['stages']:
            rung = next(row for row in ladder['rungs'] if row['prefill_tokens'] == stage['prefill_tokens'])
            for member in stage['members']:
                path = self.f.g2a/'runs'/member['run_id']
                path.mkdir(parents=True)
                config_raw = runner_config_bytes((self.f.g2a/'prefill-probe-configs'/member['config_path']).read_bytes())
                (path/'config.json').write_bytes(config_raw)
                data = retained_summary(6)
                data['status'] = 'succeeded'
                (path/'summary_metrics.json').write_text(json.dumps(data)+'\n')
                meta = retained_metadata(member['run_id'], rung, config_raw)
                meta['uncertainty_evidence'] = {'clock_anchor': {'status': 'bounded'}}
                (path/'metadata.json').write_text(json.dumps(meta)+'\n')
        night = self.f.night/'night'
        night.mkdir()
        (night/'courier.sent').write_text('delivered\n')
        (night/'chain.started').write_text('{"pgid": 999999}\n')
        (night/'chain.exited').write_text('{"exit_code":0}\n')
        off = {'schema': harvest.network_time_off.SCHEMA, 'argv': list(harvest.network_time_off.OFF_ARGV),
            'exit_code': 0, 'stdout': 'Network Time is already Off.\n', 'stderr': '',
            'plan_id': self.f.plan_id, 'window_id': self.f.plan_id, 'boot_id': 'fixture-boot',
            'epoch_s': 1000., 'monotonic_s': 900.}
        (night/'network_time_off.json').write_text(json.dumps(off)+'\n')
        self.session = SimpleNamespace(state='finalized', finalized_slots={},
            plan_sha256=harvest.sha(wp/'calibration_plan.json'), runs_root=str(self.f.g2a/'runs'))
        self.snapshot = SimpleNamespace(refusal_reasons=(), bracket_session_by_id={self.value['session_id']: self.session},
                                        is_governed_open_bracket_extension=True)
        self.args = SimpleNamespace(plan=self.f.plan_path, archive_root=self.f.base/'archive', operator_identity='fixture-operator')
        self.now = lambda: self.f.plan.t0_epoch_s+self.f.plan.window_max_s+300
        self.commands = []
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.real_bracket_for_bundles = harvest.brackets.calibration_bracket_for_bundles
        self.real_bracket_binding = harvest.brackets.build_calibration_bracket_binding
        for obj, name, kwargs in (
            (producer, 'check_harvest_inputs', {'return_value': None}),
            (harvest, 'terminal_head_pin_for_session', {'return_value': {'sequence': 1, 'head_digest': 'b'*64}, 'create': True}),
            (harvest, 'load_calibration_ledger_snapshot', {'return_value': self.snapshot}),
            (harvest, 'validate_bundle', {'return_value': []}),
            (harvest.brackets, 'load_calibration_acceptance_bound', {'return_value': copy.deepcopy(ACCEPTANCE)}),
            (harvest.brackets, 'build_calibration_bracket_binding', {'return_value': {'fixture': True}}),
            (harvest.brackets, 'calibration_bracket_for_bundles', {'return_value': ({'status': 'passed'}, ())}),
        ):
            setattr(self, name, self.stack.enter_context(mock.patch.object(obj, name, **kwargs)))
        self.check_inputs = self.check_harvest_inputs

    def runner(self, argv, **kwargs):
        self.commands.append(argv)
        if 'advance-head-pin' in argv:
            self.pin.write_text(json.dumps({'sequence': 1, 'head_digest': 'b'*64, 'advanced': True})+'\n')
        if 'abort-session' in argv:
            self.ledger.write_bytes(self.ledger.read_bytes()+b'{"fixture_abort":true}\n')
        result = {'sequence': 1, 'head_digest': 'b'*64} if 'terminal-pin' in argv else {}
        return subprocess.CompletedProcess(argv, 0, json.dumps(result), '')

    def run_harvest(self, **kwargs):
        return harvest.harvest(self.args, now=self.now, clear=lambda _: True, runner=self.runner, **kwargs)

    def test_complete_window_selects_archives_every_byte_and_advances_via_governed_procedure(self):
        before = tree(self.f.g2a)
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'SELECT')
        self.assertEqual(sum(row['valid'] for row in record['members']), 24)
        self.assertEqual(tree(self.f.g2a), before)
        self.assertTrue(record['pin_advance']['needs_operator_commit'])
        self.assertEqual(harvest.sha(Path(record['selection']['path'])), record['selection']['sha256'])
        self.assertEqual(harvest.read(record['selection']['path'])['selected_prefill_tokens'], 512)
        for line in (self.args.archive_root/'SHA256SUMS').read_text().splitlines():
            expected, name = line.split('  ', 1)
            self.assertEqual(harvest.sha(self.args.archive_root/name), expected)
        self.check_inputs.assert_called_once()
        self.assertEqual(self.check_inputs.call_args.kwargs['measurement_root'], self.f.measurement)
        self.assertEqual(self.validate_bundle.call_count, 24)
        self.assertTrue(all(call.kwargs['strict'] for call in self.validate_bundle.call_args_list))
        self.assertEqual(self.calibration_bracket_for_bundles.call_args.kwargs['mode'], 'read_replay')
        self.assertEqual([next(x for x in ('terminal-pin', 'advance-head-pin') if x in argv) for argv in self.commands],
                         ['terminal-pin', 'advance-head-pin'])
        advance = self.commands[-1]
        self.assertIn('--execute', advance)
        self.assertEqual(advance[advance.index('--operator-identity')+1], 'fixture-operator')

    def test_bracket_uses_window_inventory_policy_for_both_blocks(self):
        relative = Path('configs/campaign_policies/quiet_mac_p2_production.json')
        for path in (relative, G2A_CAMPAIGN_POLICY_PATH):
            with self.subTest(policy=path):
                policy_path = self.f.measurement / path
                self.value['campaign_policy'] = {'path': path.as_posix(), 'sha256': harvest.sha(policy_path)}
                (self.f.g2a/'window-plan/g2a-input-inventory.json').write_text(json.dumps(self.value)+'\n')
                self.args.archive_root = self.f.base / ('archive-' + path.stem)
                with mock.patch.object(harvest.CampaignPolicy, 'from_mapping',
                                       wraps=harvest.CampaignPolicy.from_mapping) as parse:
                    self.assertEqual(self.run_harvest()['verdict'], 'SELECT')
                parse.assert_called_once_with(harvest.read(policy_path))

    def test_harvest_refuses_inventory_policy_outside_measurement_policy_directory(self):
        self.value['campaign_policy'] = {'path': str(producer_tests.POLICY),
                                         'sha256': harvest.sha(producer_tests.POLICY)}
        (self.f.g2a/'window-plan/g2a-input-inventory.json').write_text(json.dumps(self.value)+'\n')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'REFUSED')
        self.assertEqual(record['fault']['detail'], 'campaign_policy_path_outside_policy_directory')
        self.calibration_bracket_for_bundles.assert_not_called()

    def test_harvest_refuses_an_inventory_policy_that_is_not_claim_grade(self):
        # The schema already refuses a production policy without a bracket or with
        # on_fail=flag; these two parse, and the harvest must refuse them.
        def admission_off(source):
            source['idle_admission']['enabled'] = False

        def exploratory(source):
            source['profile'] = 'exploratory'
            source['idle_admission_extension']['claim_bearing'] = False

        for name, change in (('admission_off', admission_off), ('exploratory', exploratory)):
            with self.subTest(policy=name):
                source = json.loads((self.f.measurement/'configs/campaign_policies/quiet_mac_p2_production.json').read_text())
                change(source)
                path = Path(f'configs/campaign_policies/not_claim_grade_{name}.json')
                (self.f.measurement/path).write_text(json.dumps(source, sort_keys=True, indent=2)+'\n')
                self.value['campaign_policy'] = {'path': path.as_posix(), 'sha256': harvest.sha(self.f.measurement/path)}
                (self.f.g2a/'window-plan/g2a-input-inventory.json').write_text(json.dumps(self.value)+'\n')
                self.args.archive_root = self.f.base / ('archive-refuse-' + name)
                record = self.run_harvest()
                self.assertEqual(record['verdict'], 'REFUSED')
                self.assertEqual(record['fault']['detail'], 'campaign_policy_not_claim_grade')
                self.calibration_bracket_for_bundles.assert_not_called()

    def test_nondefault_run_config_mismatch_refuses_summary_even_if_metadata_rebound(self):
        path = self.f.g2a/'runs/g2a-small-p0512-r01'
        config = harvest.read(path/'config.json')
        config['sampling']['power_hz'] += 1
        raw = runner_config_bytes(json.dumps(config).encode())
        (path/'config.json').write_bytes(raw)
        metadata = harvest.read(path/'metadata.json')
        metadata['config_sha256'] = hashlib.sha256(raw).hexdigest()
        (path/'metadata.json').write_text(json.dumps(metadata)+'\n')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'REFUSED')
        self.assertEqual(record['cause_codes'], ['summary_regeneration_failed'])

    def test_counts_under_three_are_valid_and_selector_uses_registered_floor(self):
        run_id = 'g2a-small-p0512-r01'
        path = self.f.g2a/'runs'/run_id/'summary_metrics.json'
        data = harvest.read(path)
        data['window_evidence_precheck']['phase']['prefill']['windows'][0]['in_window_sample_count'] = 2
        path.write_text(json.dumps(data)+'\n')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'SELECT')
        self.assertTrue(next(row for row in record['members'] if row['run_id'] == run_id)['valid'])
        receipt = harvest.read(self.args.archive_root/'derived/counts.json')
        self.assertEqual(next(row for row in receipt['runs'] if row['run_id'] == run_id)['in_window_sample_count'], 2)
        self.assertEqual(harvest.read(record['selection']['path'])['selected_prefill_tokens'], 1024)

    def test_time_delivery_and_process_gates_precede_archive_and_authentication(self):
        for case in ('early', 'delivery', 'alive'):
            with self.subTest(case=case):
                marker = self.f.night/'night/courier.sent'
                if case == 'delivery':
                    marker.unlink()
                with self.assertRaises(harvest.HarvestRefusal):
                    harvest.harvest(self.args, now=lambda: self.now()-(1 if case == 'early' else 0),
                                    clear=lambda _: case != 'alive', runner=self.runner)
                if case == 'delivery':
                    marker.write_text('delivered\n')
                self.assertFalse(self.args.archive_root.exists())
                self.check_inputs.assert_not_called()
        self.assertEqual(self.run_harvest()['verdict'], 'SELECT')

    def test_open_pre_screen_stop_recovers_and_uses_governed_abort_then_terminal_pin(self):
        self.session.state = 'open'
        self.snapshot.refusal_reasons = ('calibration_ledger_bracket_session_open',)
        log = self.f.g2a/'operator-logs/window-chain.log'
        log.parent.mkdir()
        log.write_text('pre_calibration_screen=failed\n')
        (self.f.night/'night/chain.exited').write_text('{"exit_code":1}\n')
        original = self.ledger.read_bytes()
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        self.assertIn('pre_screen_stop', record['cause_codes'])
        self.assertIn('abort-session', self.commands[0])
        self.assertEqual((self.args.archive_root/'physical-ledger/ledger.jsonl').read_bytes(), original)
        self.assertNotEqual((self.args.archive_root/'derived/terminal-ledger.jsonl').read_bytes(), original)

    def test_member_shortfall_recovers_and_summary_counts_only_valid_members(self):
        bad = 'g2a-small-p0512-r01'
        self.validate_bundle.side_effect = lambda path, **_: ['raw_mismatch'] if path.name == bad else []
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        self.assertIn('rung_valid_small_members_shortfall', record['cause_codes'])
        self.assertEqual(harvest.read(self.args.archive_root/'derived/summary.json')[0]['small_members'], 4)
        self.assertNotIn('selection', record)

    def test_invalid_member_clock_metadata_preserves_recovery_verdict(self):
        bad = 'g2a-small-p0512-r01'
        (self.f.g2a/'runs'/bad/'metadata.json').write_text('{broken fixture metadata')
        self.validate_bundle.side_effect = lambda path, **_: ['metadata_invalid'] if path.name == bad else []
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        rows = harvest.read(self.args.archive_root/'derived/network-time.json')['captures']
        row = next(row for row in rows if row['capture_id'] == bad)
        self.assertEqual(row['metadata_status'], 'unreadable')
        self.assertEqual(row['offset_comparison'], 'not comparable')

    def test_post_bracket_failure_recovers_without_selector(self):
        self.calibration_bracket_for_bundles.return_value = ({'status': 'failed'}, ('post_bracket_failure',))
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        self.assertEqual(record['cause_codes'], ['post_bracket_failure'])
        self.assertNotIn('selection', record)

    def test_bracket_acceptance_file_sha_must_match_frozen_plan(self):
        alternate = self.f.base/'different-acceptance.json'
        alternate.write_bytes(harvest.brackets.DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes() + b'\n')
        with mock.patch.object(harvest.brackets, 'DEFAULT_ACCEPTANCE_BOUND_PATH', alternate):
            record = self.run_harvest()
        self.assertEqual(self._causes(record), ('REFUSED', ['bracket_acceptance_plan_mismatch']))
        self.calibration_bracket_for_bundles.assert_not_called()
        self.assertEqual(self.commands, [])

    def test_bracket_acceptance_id_must_match_frozen_plan(self):
        self.load_calibration_acceptance_bound.return_value['acceptance_id'] = 'other-acceptance'
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('REFUSED', ['bracket_acceptance_plan_mismatch']))
        self.calibration_bracket_for_bundles.assert_not_called()

    def test_bracket_view_refusals_are_unfiltered_recovery_causes(self):
        refused = copy.copy(self.snapshot)
        refused.refusal_reasons = ('calibration_ledger_baseline_missing', 'calibration_ledger_custody_invalid')
        self.load_calibration_ledger_snapshot.side_effect = [self.snapshot, self.snapshot, refused]
        self.calibration_bracket_for_bundles.side_effect = lambda *_, **kwargs: (
            {'status': 'failed'}, kwargs['ledger_snapshot'].refusal_reasons)
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('RECOVER', list(refused.refusal_reasons)))
        self.build_calibration_bracket_binding.assert_not_called()
        self.assertIs(self.calibration_bracket_for_bundles.call_args.kwargs['ledger_snapshot'], refused)

    def test_finalized_session_after_acceptance_cutoff_uses_separate_bracket_view(self):
        # The existing crash fixture can authenticate PRE custody but leaves
        # POST unfilled. Complete that real session over a non-genesis seed.
        self.crash_after_pre(seed_past_cutoff=True, retain_members=True)
        post = self.fixture_capture('fixture-post')
        real_ledger.claim_bracket_session_slot(self.ledger, session_id=self.value['session_id'],
                                              slot='post', attempt_id='fixture-post')
        real_ledger.finalize_bracket_session_slot(self.ledger, session_id=self.value['session_id'],
            slot='post', disposition='valid', custody_locator=str(post),
            artifact_sha256=real_ledger.artifact_hashes(post), identity_epoch=IDENTITY,
            t1_bindings=T1, capture_wall_time_s='111.0', exact_bound_lexeme_s='0.026')
        (self.f.night/'night/chain.exited').write_text('{"exit_code":0}\n')
        for run_id in producer.harvest_roster(self.value):
            path = self.f.g2a/'runs'/run_id
            metadata = harvest.read(path/'metadata.json')
            metadata['instrument_calibration'] = {'bindings': T1}
            (path/'metadata.json').write_text(json.dumps(metadata)+'\n')
            (path/'events.jsonl').write_text('\n'.join(json.dumps({
                'phase': 'measured_run', 'event_type': event, 'timestamp_s': stamp,
                'message': '', 'metadata': {},
            }) for event, stamp in (('sampling_started', 100.), ('sampling_stopped', 110.)))+'\n')
        acceptance_path = self.f.base/'fixture-acceptance.json'
        acceptance_path.write_bytes(_unissued_acceptance_fixture_bytes())
        acceptance = _unissued_acceptance_fixture()
        self.load_calibration_acceptance_bound.return_value = acceptance
        frozen = self.f.g2a/'window-plan/calibration_plan.json'
        # Keep the session's plan binding intact: the fixture acceptance is
        # installed before the session is reserved in crash_after_pre below.
        self.assertEqual(harvest.read(frozen)['active_acceptance']['sha256'], harvest.sha(acceptance_path))
        self.build_calibration_bracket_binding.side_effect = self.real_bracket_binding
        self.calibration_bracket_for_bundles.side_effect = lambda *args, **kwargs: (
            self.real_bracket_for_bundles(*args, **kwargs, _allow_unissued_fixture=True))
        with mock.patch.object(harvest.brackets, 'DEFAULT_ACCEPTANCE_BOUND_PATH', acceptance_path):
            record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER', record.get('fault'))
        assessment = harvest.read(self.args.archive_root/'derived/bracket.json')
        self.assertNotIn('calibration_ledger_baseline_missing', assessment['reasons'])
        self.assertEqual(assessment['assessment']['acceptance']['ledger_snapshot']['baseline_sequence'],
                         acceptance['ledger_cutoff']['sequence'])
        snapshots = self.load_calibration_ledger_snapshot.call_args_list
        self.assertEqual([call.kwargs['baseline_sequence'] for call in snapshots], [4, 4, 0])
        self.assertEqual([call.kwargs['require_committed_pin'] for call in snapshots], [True, False, False])
        self.assertEqual(snapshots[1].args, snapshots[2].args)
        bracket_view = self.calibration_bracket_for_bundles.call_args.kwargs['ledger_snapshot']
        self.assertEqual(bracket_view.bracket_session_by_id[self.value['session_id']].state, 'finalized')
        self.assertGreater(bracket_view.head_sequence, 4)
        self.assertIs(self.build_calibration_bracket_binding.call_args.args[0], bracket_view)

    def test_valid_low_counts_at_every_rung_selects_registered_collect_4096_fallback(self):
        for stage in self.value['stages'][:4]:
            for member in stage['members']:
                path = self.f.g2a/'runs'/member['run_id']/'summary_metrics.json'
                value = retained_summary(2)
                value['status'] = 'succeeded'
                path.write_text(json.dumps(value)+'\n')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'SELECT')
        selection = harvest.read(record['selection']['path'])
        self.assertEqual(selection['collection_prefill_tokens'], 4096)
        self.assertEqual(selection['refusal']['fallback_action'], 'collect_at_4096')
        self.assertIsNone(selection['selected_prefill_tokens'])
        self.assertEqual(sum(row['valid'] for row in record['members']), 24)

    def set_anchor(self, run_id, status):
        path = self.f.g2a/'runs'/run_id/'metadata.json'
        value = harvest.read(path)
        value['uncertainty_evidence'] = {'clock_anchor': {'status': status}}
        path.write_text(json.dumps(value)+'\n')

    def write_chain_copies(self):
        wp = self.f.g2a/'window-plan'
        summary.main(['--config-root', str(self.f.g2a/'prefill-probe-configs'), '--input-inventory',
            str(wp/'g2a-input-inventory.json'), '--runs-root', str(self.f.g2a/'runs'), '--counts-output',
            str(wp/'d166-prefill-counts-receipt.json'), '--summary-output', str(wp/'d166-prefill-resolvability-summary.json')])

    def test_c1_clock_refused_small_members_are_invalid_and_window_recovers(self):
        small = [m['run_id'] for m in self.value['stages'][0]['members']]
        for run_id in small:
            self.set_anchor(run_id, 'unknown')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        self.assertIn('rung_valid_small_members_shortfall', record['cause_codes'])
        rows = {row['run_id']: row for row in record['members']}
        for run_id in small:
            self.assertFalse(rows[run_id]['valid'])
            self.assertEqual(rows[run_id]['clock_anchor_status'], 'unknown')
        self.assertNotIn('selection', record)

    def test_c1_missing_anchor_record_is_invalid(self):
        run_id = self.value['stages'][0]['members'][0]['run_id']
        path = self.f.g2a/'runs'/run_id/'metadata.json'
        value = harvest.read(path); value['uncertainty_evidence'] = None
        path.write_text(json.dumps(value)+'\n')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        self.assertEqual(next(r for r in record['members'] if r['run_id'] == run_id)['clock_anchor_status'], 'not recorded')

    def test_c1_clock_refused_large_member_leaves_select(self):
        large = next(s for s in self.value['stages'] if s['members'][0]['run_id'].startswith('g2a-large'))
        self.set_anchor(large['members'][0]['run_id'], 'unknown')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'SELECT')
        self.assertEqual(sum(row['valid'] for row in record['members']), 23)

    def test_c1_low_count_with_bounded_anchor_stays_valid(self):
        run_id = 'g2a-small-p0512-r01'
        path = self.f.g2a/'runs'/run_id/'summary_metrics.json'
        data = harvest.read(path)
        data['window_evidence_precheck']['phase']['prefill']['windows'][0]['in_window_sample_count'] = 2
        path.write_text(json.dumps(data)+'\n')
        record = self.run_harvest()
        self.assertTrue(next(row for row in record['members'] if row['run_id'] == run_id)['valid'])

    def test_c2_chain_copy_with_invalid_small_member_recovers_not_refused(self):
        self.write_chain_copies()
        self.set_anchor(self.value['stages'][0]['members'][0]['run_id'], 'unknown')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        self.assertIn('rung_valid_small_members_shortfall', record['cause_codes'])
        self.assertEqual(set(record['chain_summary_copy'].values()), {'differs_invalid_members_excluded'})

    def test_c2_chain_copy_with_invalid_large_member_selects(self):
        self.write_chain_copies()
        large = next(s for s in self.value['stages'] if s['members'][0]['run_id'].startswith('g2a-large'))
        self.set_anchor(large['members'][0]['run_id'], 'unknown')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'SELECT')
        self.assertIn('differs_invalid_members_excluded', record['chain_summary_copy'].values())

    def test_c2_chain_copy_equal_when_all_valid(self):
        self.write_chain_copies()
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'SELECT')
        self.assertEqual(set(record['chain_summary_copy'].values()), {'equal'})

    def test_t8_capture_made_is_recorded_from_the_archive_copy(self):
        self.assertFalse(self.run_harvest()['capture_made'])

    def test_t8_capture_file_under_raw_sets_capture_made(self):
        raw = self.f.g2a/'runs'/'g2a-small-p0512-r01'/'raw'
        raw.mkdir(parents=True, exist_ok=True)
        (raw/'powermetrics.plist').write_bytes(b'fixture')
        self.assertTrue(self.run_harvest()['capture_made'])

    def test_window_refused_before_chain_start_is_null_without_session_or_selection(self):
        (self.f.night/'night/chain.started').unlink()
        (self.f.night/'night/chain.exited').unlink()
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'NULL')
        self.assertEqual(record['cause_codes'], ['chain_never_started'])
        self.assertNotIn('selection', record)
        self.assertIsNone(record['pin_advance'])
        self.assertEqual(self.commands, [])
        self.assertEqual(harvest.read(self.args.archive_root/'harvest.json')['verdict'], 'NULL')

    def test_missing_or_unadmitted_OFF_receipt_recovers(self):
        (self.f.night/'night/network_time_off.json').unlink()
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER')
        self.assertIn('network_time_off_not_admitted', record['cause_codes'])

    def test_unfinalized_calibration_capture_retains_its_clock_outcome(self):
        self.session.state = 'open'
        self.snapshot.refusal_reasons = ('calibration_ledger_bracket_session_open',)
        (self.f.night/'night/chain.exited').write_text('{"exit_code":1}\n')
        attempt = self.f.g2a/'runs/instrument_validation/partial-calibration'
        (attempt/'raw').mkdir(parents=True)
        (attempt/'raw/powermetrics.plist').write_bytes(b'fixture partial capture')
        (attempt/'instrument_evidence.json').write_text(json.dumps({'clock_anchor': {'status': 'unresolved'}})+'\n')
        self.assertEqual(self.run_harvest()['verdict'], 'RECOVER')
        rows = harvest.read(self.args.archive_root/'derived/network-time.json')['captures']
        row = next(row for row in rows if row['capture_id'] == attempt.name)
        self.assertEqual(row['within_capture']['status'], 'unresolved')
        self.assertEqual(row['offset_comparison'], 'not comparable')

    def test_archive_coordinate_inside_source_refuses_without_changing_evidence(self):
        before = tree(self.f.g2a)
        output = io.StringIO()
        with redirect_stdout(output):
            code = harvest.main(['--plan', str(self.args.plan), '--archive-root', str(self.f.g2a/'bad-archive'),
                '--operator-identity', self.args.operator_identity], now=self.now, clear=lambda _: True, runner=self.runner)
        self.assertEqual(code, 3)
        self.assertEqual(tree(self.f.g2a), before)
        report = Path(output.getvalue().split('harvest=', 1)[1].split(' sha256=', 1)[0])
        self.addCleanup(lambda: harvest.shutil.rmtree(report.parent))
        self.assertEqual(harvest.read(report)['verdict'], 'REFUSED')

    def test_authentication_fault_refuses_and_preserves_archive_without_advancing_pin(self):
        self.check_inputs.side_effect = producer.G2AProbeError('fixture_binding_fault')
        before = self.pin.read_bytes()
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'REFUSED')
        self.assertEqual(self.pin.read_bytes(), before)
        self.assertEqual(self.commands, [])
        self.assertTrue((self.args.archive_root/'SHA256SUMS').exists())

    def test_existing_counts_and_summary_must_match_regenerated_bytes(self):
        wp = self.f.g2a/'window-plan'
        summary.main(['--config-root', str(self.f.g2a/'prefill-probe-configs'), '--input-inventory',
            str(wp/'g2a-input-inventory.json'), '--runs-root', str(self.f.g2a/'runs'), '--counts-output',
            str(wp/'d166-prefill-counts-receipt.json'), '--summary-output', str(wp/'d166-prefill-resolvability-summary.json')])
        self.assertEqual(self.run_harvest()['verdict'], 'SELECT')

    def test_summary_byte_tamper_refuses_with_original_bytes_archived(self):
        path = self.f.g2a/'window-plan/d166-prefill-resolvability-summary.json'
        path.write_text('[]\n')
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'REFUSED')
        self.assertEqual(self.commands, [])
        self.assertEqual((self.args.archive_root/'g2a-root/window-plan'/path.name).read_bytes(), path.read_bytes())

    def test_roster_omission_refuses_before_capture_validation(self):
        path = self.f.g2a/'window-plan/g2a-input-inventory.json'
        value = harvest.read(path)
        value['stages'][0]['members'].pop()
        path.write_text(json.dumps(value)+'\n')
        self.assertEqual(self.run_harvest()['verdict'], 'REFUSED')
        self.validate_bundle.assert_not_called()

    def test_copy_corruption_refuses_before_any_authentication(self):
        copytree = harvest.shutil.copytree
        def corrupt(source, target, *args, **kwargs):
            result = copytree(source, target, *args, **kwargs)
            target = Path(target)
            (target/'extra-fault').write_text('copy fault\n')
            return result
        with mock.patch.object(harvest.shutil, 'copytree', side_effect=corrupt), self.assertRaises(harvest.HarvestRefusal):
            self.run_harvest()
        self.check_inputs.assert_not_called()
        self.assertFalse(self.args.archive_root.exists())

    def test_archive_preserves_literal_symlink_without_following_it(self):
        link = self.f.g2a/'retained-link'
        link.symlink_to('window-plan/calibration_plan.json')
        self.assertEqual(self.run_harvest()['verdict'], 'SELECT')
        archived = self.args.archive_root/'g2a-root/retained-link'
        self.assertTrue(archived.is_symlink())
        self.assertEqual(os.readlink(archived), os.readlink(link))

    def test_stdout_is_custody_only(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = harvest.main(['--plan', str(self.args.plan), '--archive-root', str(self.args.archive_root),
                    '--operator-identity', self.args.operator_identity], now=self.now, clear=lambda _: True, runner=self.runner)
        self.assertEqual(code, 0)
        text = output.getvalue()
        self.assertIn('verdict=SELECT members=24/24', text)
        self.assertNotRegex(text, r'energy|fiducial|drift|in_window_sample_count|small_minimum_count')

    # Guards pinned from the cold Fable final pass on PR #458 (record 36, finding F1; its probes, lifted).
    def _causes(self, record): return record['verdict'], record['cause_codes']
    def test_guard_h3_non_succeeded_member_is_invalid(self):
        run_id = 'g2a-small-p0512-r01'; path = self.f.g2a/'runs'/run_id/'summary_metrics.json'
        data = harvest.read(path); data['status'] = 'failed'; path.write_text(json.dumps(data)+'\n')
        record = self.run_harvest()
        self.assertFalse(next(r for r in record['members'] if r['run_id'] == run_id)['valid'])
        self.assertEqual(self._causes(record), ('RECOVER', ['rung_valid_small_members_shortfall']))
        self.assertNotIn('selection', record)
    def test_guard_h4a_nonzero_exit_recovers(self):
        (self.f.night/'night/chain.exited').write_text('{"exit_code":1}\n')
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('RECOVER', ['chain_nonzero_or_missing_exit'])); self.assertNotIn('selection', record)
    def test_guard_h4b_missing_exit_recovers(self):
        (self.f.night/'night/chain.exited').unlink()
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('RECOVER', ['chain_nonzero_or_missing_exit'])); self.assertNotIn('selection', record)
    def test_guard_h4c_exit_code_true_or_string_zero_is_not_zero(self):
        (self.f.night/'night/chain.exited').write_text('{"exit_code":"0"}\n')
        self.assertEqual(self.run_harvest()['verdict'], 'RECOVER')
    def test_guard_h9_altered_registration_refuses_before_archive(self):
        reg = self.f.measurement/harvest.night_gate.D166_REGISTRATION_PATH
        reg.write_bytes(reg.read_bytes()+b' ')
        with self.assertRaises(harvest.HarvestRefusal): self.run_harvest()
        self.assertFalse(self.args.archive_root.exists())
    def test_guard_h10_chain_changed_after_sidecar_refuses_before_archive(self):
        self.f.chain.write_text(self.f.chain.read_text()+'# changed\n')
        with self.assertRaises(harvest.HarvestRefusal): self.run_harvest()
        self.assertFalse(self.args.archive_root.exists())
    def test_guard_h14_ledger_refusal_reason_refuses(self):
        self.snapshot.refusal_reasons = ('calibration_ledger_head_mismatch',)
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('REFUSED', ['ledger_authentication_failed'])); self.assertEqual(self.commands, [])
    def test_guard_h15_session_bound_to_other_plan_or_runs_root_refuses(self):
        self.session.plan_sha256 = '0'*64
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('REFUSED', ['bracket_session_binding_mismatch'])); self.assertEqual(self.commands, [])
    def test_guard_h18_inventory_for_other_window_refuses(self):
        path = self.f.g2a/'window-plan/g2a-input-inventory.json'
        value = harvest.read(path); value['window_id'] = 'other-window'; path.write_text(json.dumps(value)+'\n')
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('REFUSED', ['window_identity_mismatch'])); self.assertEqual(self.commands, [])
    def test_guard_h22_source_changed_during_harvest_refuses_without_pin_advance(self):
        real = harvest.selector.main
        def main(argv):
            (self.f.g2a/'runs/late-file').write_text('x'); return real(argv)
        with mock.patch.object(harvest.selector, 'main', side_effect=main):
            record = self.run_harvest()
        self.assertEqual(self._causes(record), ('REFUSED', ['source_or_process_ownership_changed'])); self.assertEqual(self.commands, [])
    def test_guard_open_session_never_selects(self):
        self.session.state = 'open'
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER'); self.assertIn('bracket_incomplete', record['cause_codes'])

    def fixture_capture(self, name):
        capture = self.f.g2a/'runs/instrument_validation'/name
        (capture/'raw').mkdir(parents=True)
        (capture/'raw/powermetrics.plist').write_bytes(b'synthetic calibration capture ' + name.encode())
        (capture/'events.jsonl').write_text('{"timestamp_s":99.0}\n')
        (capture/'instrument_evidence.json').write_text('{"b_fiducial_s":0.025}\n')
        (capture/'manifest.json').write_text(json.dumps({'fixture': True, 'name': name})+'\n')
        return capture

    def crash_after_pre(self, *, seed_past_cutoff=False, retain_members=False):
        """Leave the real mid-session slot-finalization tail that crashed w1."""
        if not retain_members:
            for run_id in producer.harvest_roster(self.value):
                harvest.shutil.rmtree(self.f.g2a/'runs'/run_id)
        self.ledger.write_bytes(b'')
        self.pin.write_text(json.dumps({'sequence': 0, 'head_digest': real_ledger.GENESIS_DIGEST,
                                       'ledger_schema': real_ledger.LEDGER_SCHEMA})+'\n')
        seed_sequence, seed_digest = 0, real_ledger.GENESIS_DIGEST
        if seed_past_cutoff:
            seed = self.fixture_capture('fixture-seed')
            real_ledger.append_pending_receipt(self.ledger, attempt_id='fixture-seed',
                custody_locator=str(seed), identity_epoch=IDENTITY, t1_bindings=T1,
                head_pin_path=self.pin, require_committed_pin=False, repo_root=self.f.measurement)
            terminal = real_ledger.finalize_attempt_receipt(self.ledger, attempt_id='fixture-seed',
                disposition='ordinary-invalid', custody_locator=str(seed),
                artifact_sha256=real_ledger.artifact_hashes(seed), identity_epoch=IDENTITY, t1_bindings=T1,
                capture_wall_time_s='1.0', exact_bound_lexeme_s='0.025')
            pin = real_ledger.head_pin_for_receipt(terminal)
            self.pin.write_text(json.dumps(pin)+'\n')
            seed_sequence, seed_digest = pin['sequence'], pin['head_digest']
        init_git_fixture(self.f.measurement, '-q')
        subprocess.run(['git', 'add', str(self.pin.relative_to(self.f.measurement))],
                       cwd=self.f.measurement, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'fixture seed'], cwd=self.f.measurement, check=True, capture_output=True)
        frozen = self.f.g2a/'window-plan/calibration_plan.json'
        plan = harvest.read(frozen)
        plan['calibration_ledger'].update(head_sequence=seed_sequence, head_digest=seed_digest)
        if seed_past_cutoff:
            fixture_acceptance = _unissued_acceptance_fixture()
            plan['active_acceptance'].update(
                sha256=hashlib.sha256(_unissued_acceptance_fixture_bytes()).hexdigest(),
                acceptance_id=fixture_acceptance['acceptance_id'])
        frozen.write_text(json.dumps(plan)+'\n')
        self.value['calibration_plan']['sha256'] = harvest.sha(frozen)
        (self.f.g2a/'window-plan/g2a-input-inventory.json').write_text(json.dumps(self.value)+'\n')
        capture = self.fixture_capture('fixture-pre')
        real_ledger.append_bracket_session_receipt(self.ledger, head_pin_path=self.pin,
            repo_root=self.f.measurement, session_id=self.value['session_id'], window_id=self.value['window_id'],
            plan_id=self.value['calibration_plan']['plan_id'], plan_sha256=harvest.sha(frozen),
            evidence_root_id=self.value['evidence_root_id'], runs_root=self.f.g2a/'runs',
            slots={slot: {'attempt_id':'fixture-'+slot,
                'custody_locator':str(self.f.g2a/'runs/instrument_validation'/('fixture-'+slot)),
                'identity_epoch':IDENTITY, 't1_bindings':T1} for slot in ('pre','post')})
        real_ledger.claim_bracket_session_slot(self.ledger, session_id=self.value['session_id'],
                                              slot='pre', attempt_id='fixture-pre')
        real_ledger.finalize_bracket_session_slot(self.ledger, session_id=self.value['session_id'],
            slot='pre', disposition='valid', custody_locator=str(capture),
            artifact_sha256=real_ledger.artifact_hashes(capture), identity_epoch=IDENTITY,
            t1_bindings=T1, capture_wall_time_s='99.0', exact_bound_lexeme_s='0.025')
        self.load_calibration_ledger_snapshot.side_effect = real_ledger.load_calibration_ledger_snapshot
        self.terminal_head_pin_for_session.side_effect = real_ledger.terminal_head_pin_for_session
        (self.f.night/'night/chain.exited').write_text('{"exit_code":1}\n')

    def test_crash_after_pre_capture_with_zero_members_recovers_and_closes_copied_session(self):
        self.crash_after_pre()
        before = tree(self.f.measurement), tree(self.f.g2a), tree(self.f.night)
        self.args.read_only_sources = True
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER', record.get('fault'))
        self.assertEqual(record['cause_codes'], ['bracket_incomplete', 'chain_nonzero_or_missing_exit',
                                                'rung_valid_small_members_shortfall'])
        self.assertTrue(record['capture_made'])
        self.assertFalse(any(row['valid'] for row in record['members']))
        self.assertEqual(self.commands, [])
        self.assertEqual((tree(self.f.measurement), tree(self.f.g2a), tree(self.f.night)), before)
        copied = self.args.archive_root/'derived/terminal-ledger.jsonl'
        pin = self.args.archive_root/'derived/terminal-pin.json'
        snapshot = real_ledger.load_calibration_ledger_snapshot(copied, pin, require_committed_pin=False)
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(snapshot.bracket_session_by_id[self.value['session_id']].state, 'aborted')
        self.assertEqual(snapshot.head_sequence, 8)  # open, claim, pre final, abort: two records each

    def test_crash_after_pre_capture_with_zero_members_uses_governed_source_abort_before_pin(self):
        self.crash_after_pre()
        def runner(argv, **kwargs):
            self.commands.append(argv)
            stdout = io.StringIO()
            with mock.patch.object(recovery, 'REPO_ROOT', self.f.measurement), redirect_stdout(stdout):
                code = recovery.main(list(map(str, argv[3:])))
            return subprocess.CompletedProcess(argv, code, stdout.getvalue(), '')
        record = harvest.harvest(self.args, now=self.now, clear=lambda _: True, runner=runner)
        self.assertEqual(record['verdict'], 'RECOVER', record.get('fault'))
        self.assertTrue(record['capture_made'])
        self.assertEqual([next(x for x in ('abort-session','terminal-pin','advance-head-pin') if x in argv)
                          for argv in self.commands], ['abort-session','terminal-pin','advance-head-pin'])
        snapshot = real_ledger.load_calibration_ledger_snapshot(self.ledger, self.pin, require_committed_pin=False)
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(snapshot.bracket_session_by_id[self.value['session_id']].state, 'aborted')
    def test_guard_missing_session_never_selects(self):
        self.snapshot.bracket_session_by_id = {}
        record = self.run_harvest()
        self.assertEqual(record['verdict'], 'RECOVER'); self.assertIn('bracket_incomplete', record['cause_codes']); self.assertEqual(self.commands, [])
    def test_guard_bracket_status_failed_with_empty_reasons_never_selects(self):
        self.calibration_bracket_for_bundles.return_value = ({'status': 'failed'}, ())
        record = self.run_harvest()
        self.assertEqual(self._causes(record), ('RECOVER', ['bracket_not_passed']))
    def test_guard_plan_outside_night_root_refuses(self):
        other = self.f.base/'elsewhere'; other.mkdir(); copy = other/'night_plan.json'; copy.write_bytes(self.f.plan_path.read_bytes())
        self.args.plan = copy
        with self.assertRaises(harvest.HarvestRefusal): self.run_harvest()
    def test_guard_bracket_judged_over_valid_members_only_and_all_24_strict(self):
        record = self.run_harvest()
        bundles = self.calibration_bracket_for_bundles.call_args.args[1]
        self.assertEqual(len(bundles), 24); self.assertEqual(record['verdict'], 'SELECT')
    def test_guard_main_stdout_shape_for_select(self):
        import io, re
        from contextlib import redirect_stdout
        out = io.StringIO()
        with redirect_stdout(out):
            code = harvest.main(['--plan', str(self.args.plan), '--archive-root', str(self.args.archive_root),
                                 '--operator-identity', 'fixture-operator'], now=self.now, clear=lambda _: True, runner=self.runner)
        self.assertEqual(code, 0)
        lines = out.getvalue().splitlines()
        self.assertEqual(lines[0], 'verdict=SELECT members=24/24')
        for line in lines[1:]:
            self.assertRegex(line, r'^(harvest|path)=\S+ sha256=[0-9a-f]{64}$')


class G2aClockReportTests(unittest.TestCase):
    def test_comparable_system_clock_delta_and_different_sources(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for name, kind, offset in (('steady', 'system', 100.01), ('moved', 'system', 100.02), ('synthetic', 'fake', 100.02)):
                path = root/name
                path.mkdir()
                (path/'metadata.json').write_text(json.dumps({'clock': {'kind': kind,
                    'wall_minus_monotonic_start_s': offset, 'wall_minus_monotonic_end_s': offset},
                    'uncertainty_evidence': {'clock_anchor': {'status': 'bounded'}}}))
                paths.append((name, path))
            record = harvest.clock_report({'epoch_s': 1000., 'monotonic_s': 900.}, paths)
        rows = record['captures']
        self.assertFalse(rows[0]['flagged_above_0_015_s'])
        self.assertTrue(rows[1]['flagged_above_0_015_s'])
        self.assertEqual(rows[2]['offset_comparison'], 'not comparable')
        self.assertEqual(rows[0]['within_capture']['status'], 'bounded')

    def test_group_probe_refuses_alive_and_unknown_and_accepts_gone(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            night = Path(temporary)
            (night/'chain.started').write_text('{"pgid":12345}')
            for error, expected in ((None, False), (PermissionError(), False), (ProcessLookupError(), True)):
                with mock.patch.object(harvest.os, 'killpg', side_effect=error):
                    self.assertEqual(harvest.group_clear(night), expected)
