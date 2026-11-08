"""Synthetic Git records only: no measurements, probes, models or network."""
import contextlib
import base64
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_v4_next_arm_packet as builder
from joulewise.align.apple import v4_cadence as cad

INTERNAL = {r['id']: True for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.ARM}
CONFIG = dict(zip(builder.FROZEN_D_SLOT_KEYS, (4096, 30, 128, 4)))
IDENTITY = {'model_source': 'synthetic-tiny', 'model_revision': 'fixture',
            'runtime_sha256': 'a'*64, 'execution_policy_sha256': 'b'*64}


class Scenario:
    def __init__(self, directory, window='W1'):
        self.root = Path(directory)
        self.git('init', '-q')
        self.window = window
        self.policy = {'idle_s': 300, 'delta_slow_c': 1., 'quantization_bits': 8}
        self.members = [{'run_id': p, 'model_id': 'tiny', 'role': 'D', 'condition': 'benign',
                         'task_pair': p} for p in cad.CAL_PAIRS]
        self.sources = {
            'plan': {'plan_id': 'synthetic-' + window, 'receipt_class': 'HAZARD_PACK',
                     'custody_root': '/DO-NOT-FOLLOW/custody'},
            'collection_plan': {'members': self.members, 'thermal_policy': dict(self.policy)},
            'result': {'schema': 'joulewise.unattended_night_result.v1', 'plan_id': 'synthetic-' + window,
                       'receipt_class': 'HAZARD_PACK', 'verdict': 'GO', 'chain_exit_code': 0,
                       'chain_sha256': 'c'*64, 'ended_epoch_s': 100},
            'chain_started': {'pgid': 123}, 'chain_exited': {'exit_code': 0},
            'courier': {'sent': True}, 'courier_sent': b'',
            'watchdog_state': {},
            'pilot': {'status': 'instrument_ok', 'checks': {'synthetic_check': True}, 'extra_checks': {
                'thermal': {'schema': 'joulewise.align.thermal_desk.v1',
                    'model_windows': {'tiny/' + window: {f'U{k}': {'status': 'pass' if k < 4 else 'inconclusive'}
                                                        for k in range(1, 6)}},
                    'members': [{'id': p, 'model': 'tiny', 'gated': True, 'role': 'D',
                        'window': window, 'configuration': dict(CONFIG), 'cohort_identity': dict(IDENTITY),
                        'excluded': False, 'calibration_exclusions': [], 'flags': [], 'coverage': [],
                        'pm_period_s': .1, 'pm_max_gap_s': .1, 'turn_observation': [],
                        'tokens': [[1, 2, 3]]} for p in cad.CAL_PAIRS]},
                'km003c': {'members': {p: {'status': 'available', 'flags': []} for p in cad.CAL_PAIRS}}}},
            'desk': {'plan_id': 'synthetic-' + window, 'pilot_status': 'instrument_ok',
                     'checks': {'synthetic_check': True}, 'harvest_status': 'ok'},
            'exclusions': {'members_excluded': []}}
        self.record = {'schema': builder.RECORD_SCHEMA, 'window': window,
                       'role': 'development' if window in ('W1', 'R1') else 'calibration',
                       'finalized_at_epoch_s': 101}
        self.quiet = {'observed_at_epoch_s': 110, 'cooldown_s': 300, 'display_off_s': 60,
                      'dwell_s': 60, 'active_work': []}
        self.live = {'observed_at_epoch_s': 110, 'sample_count': 3, 'raw_offset_ns': 100}
        self.next_plan = {'role': 'calibration', 'window': 'C1',
                          'configuration': {**CONFIG, 'cohort_identity': dict(IDENTITY)},
                          'thermal_policy': dict(self.policy),
                          'members': [{'run_id': f'sentinel-{i}', 'role': 'sentinel'} for i in range(4)]}
        self.series = {'schema': builder.SERIES_SCHEMA, 'prepared_at_epoch_s': 111,
                       'quiet_requirements': {'cooldown_s': 300, 'display_off_s': 60, 'dwell_s': 60, 'max_age_s': 30},
                       'history': [], 'pool_members': [], 'sentinel_ids': [f'sentinel-{i}' for i in range(4)],
                       'escalations': []}
        self.absent_captures = set()
        self.omit_sources = set()
        self.raw_custody = False

    def git(self, *args):
        result = subprocess.run(['git', '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                                 '-C', str(self.root), *args], check=True, capture_output=True,
                                env={**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'})
        return result.stdout.decode().strip()

    def write(self, path, value):
        raw = value if isinstance(value, bytes) else (json.dumps(value, sort_keys=True) + '\n').encode()
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'synthetic evidence')
        return self.git('rev-parse', 'HEAD')

    def finish(self, *, change_code=False):
        code = self.write('code.txt', b'synthetic-code-v1\n')
        self.record['code_config'] = [code]
        self.sources['watchdog_state'].setdefault('released_terminal_windows', [
            f"synthetic-{self.window}:/DO-NOT-FOLLOW/custody:{builder.digest((json.dumps(self.sources['result'], sort_keys=True) + chr(10)).encode())}"])
        self.record['sources'] = {k: self.write('evidence/' + k + '.json', v)
                                  for k, v in self.sources.items() if k not in self.omit_sources}
        self.record['captures'] = {p: None if p in self.absent_captures else (
            {'locator': '/DO-NOT-FOLLOW/' + p, 'sha256': builder.digest(b'synthetic'), 'bytes': 9}
            if self.raw_custody else self.write(
            'captures/' + p + '.jsonl', b'{"monotonic_ns":1,"power_w":1}\n')) for p in cad.CAL_PAIRS}
        self.record['raw_evidence'] = [self.write('raw/sidecar.jsonl', b'{"temperature_c":30}\n')]
        if self.raw_custody:
            self.record['raw_evidence'].extend(self.record['captures'].values())
        index = self.write('record.json', self.record)
        self.record_commit = self.commit()
        self.git('update-ref', 'refs/remotes/synthetic/records', self.record_commit)
        self.series['last_passed_record'] = {'commit': self.record_commit, **index}
        if change_code:
            code = self.write('code.txt', b'synthetic-code-v2\n')
        self.next_plan['code_config'] = [code]
        self.series.update(previous_record={'commit': self.record_commit, **index},
                           quiet=self.write('series/quiet.json', self.quiet),
                           meter_live=self.write('series/meter_live.json', self.live),
                           next_plan=self.write('series/next_plan.json', self.next_plan))
        if self.record['role'] == 'calibration':
            self.series['history'].append({'record_commit': self.record_commit, 'record_path': 'record.json'})
        self.write('series.json', self.series)
        self.series_commit = self.commit()
        return self

    def build(self, **changes):
        args = dict(record_commit=self.record_commit, record_path='record.json',
                    series_commit=self.series_commit, series_path='series.json',
                    pushed_ref='refs/remotes/synthetic/records')
        args.update(changes)
        return builder.build_packet(self.root, **args)

    @property
    def thermal(self):
        return self.sources['pilot']['extra_checks']['thermal']


class PacketTests(unittest.TestCase):
    def scenario(self, window='W1'):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-synthetic-')
        self.addCleanup(temp.cleanup)
        return Scenario(temp.name, window)

    def test_w1_record_admits_and_binds_all_raw_bytes_without_following_custody(self):
        s = self.scenario().finish()
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight']['reasons'])
        self.assertTrue(cad.next_arm_triage(packet, INTERNAL, now_epoch_s=111)['admitted'])
        self.assertEqual(packet['record_commit'], s.record_commit)
        self.assertEqual(packet['checks']['sentinel_roster']['sentinel_ids'], s.series['sentinel_ids'])
        self.assertEqual(set(packet['checks']), {r['id'] for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.PACKET})
        self.assertEqual(set(packet['entry_sources']), set(cad.TRIAGE_IDS))
        self.assertEqual(packet['arm_pending'], list(INTERNAL))
        self.assertEqual(packet, s.build())  # reproducible; no current-clock dependency
        for source in packet['evidence']:
            actual = subprocess.run(['git', '-C', str(s.root), 'show', source['commit'] + ':' + source['path']],
                                    check=True, capture_output=True).stdout
            self.assertEqual(hashlib.sha256(actual).hexdigest(), source['sha256'])
        paths = {r['path'] for r in packet['evidence']}
        self.assertTrue({'record.json', 'series.json', 'raw/sidecar.jsonl', 'captures/spam.jsonl'} <= paths)

    def test_each_of_fourteen_entries_refuses_for_documented_reason(self):
        mutations = {
            'record_committed': (lambda s: s.record.pop('finalized_at_epoch_s'), 'record finalization missing'),
            'terminal_completion': (lambda s: s.sources['watchdog_state'].update(released_terminal_windows=[]), 'watchdog empty-process'),
            'quiet_start_state': (lambda s: s.quiet.update(active_work=['hashing']), 'evidence traffic remains'),
            'meter_samples_clock': (lambda s: s.live.update(sample_count=0), 'meter not verified live'),
            'capture_faults': (lambda s: s.thermal['members'][0].pop('coverage'), 'X1-X8 tabulation missing'),
            'thermal_escalation': (lambda s: s.thermal['model_windows']['tiny/W1']['U1'].update(status='fail'), 'prospective recorded escalation'),
            'cohort_pool_rules': (lambda s: s.thermal['members'][0]['configuration'].update(max_turns=5), 'four-slot cohort'),
            'sentinel_roster': (lambda s: s.next_plan['members'].pop(), 'two extra sentinels'),
            'member_eligibility': (lambda s: s.thermal['members'][0].update(excluded=True), 'final exclusions disagree'),
            'full_desk_gate': (lambda s: s.sources['desk'].update(pilot_status='instrument_incomplete'), 'full desk must complete and pass'),
        }
        for name, (mutate, reason) in mutations.items():
            with self.subTest(name=name):
                s = self.scenario()
                mutate(s)
                packet = s.finish().build()
                self.assertEqual(packet['checks'][name]['status'], 'fail')
                self.assertIn(reason, packet['checks'][name]['basis'])
                self.assertFalse(packet['packet_preflight']['ready'])
                result = cad.next_arm_triage(packet, INTERNAL, now_epoch_s=111)
                self.assertIn('triage ' + name + ' failed', result['reasons'])
        packet = self.scenario().finish().build()
        for name in INTERNAL:
            with self.subTest(name=name):
                result = cad.next_arm_triage(packet, {**INTERNAL, name: False}, now_epoch_s=111)
                self.assertIn('triage ' + name + ' failed or unevaluated', result['reasons'])
        packet['next_window_role'] = 'test'
        result = cad.next_arm_triage(packet, INTERNAL, now_epoch_s=111)
        self.assertIn("triage calibration_stop: continue does not allow a 'test' arm", result['reasons'])

    def test_raw_digest_mismatch_and_unpushed_record_refuse(self):
        s = self.scenario()
        # A raw source is committed under a wrong digest, rather than editing an immutable bundle.
        s.finish()
        record = copy.deepcopy(s.record)
        record['raw_evidence'][0]['sha256'] = '0'*64
        index = s.write('record.json', record)
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, **index}
        s.write('series.json', s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertIn('SHA-256 mismatch', packet['checks']['record_committed']['basis'])
        s = self.scenario().finish()
        self.assertEqual(s.build(pushed_ref='refs/remotes/missing/records')['checks']['record_committed']['status'], 'fail')
        self.assertIn('remote-tracking', s.build(pushed_ref='HEAD')['checks']['record_committed']['basis'])

    def test_dirty_worktree_does_not_change_committed_evidence(self):
        s = self.scenario().finish()
        original = s.build()
        s.write('evidence/result.json', {'forged': True})
        self.assertEqual(s.build(), original)

    def test_large_raw_custody_digests_are_retained_without_opening_locators(self):
        s = self.scenario()
        s.raw_custody = True
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        rows = [r for r in packet['evidence'] if r.get('locator')]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r['locator'] for r in rows}, {'/DO-NOT-FOLLOW/spam', '/DO-NOT-FOLLOW/bank'})
        self.assertTrue(all(r['verification'] == 'committed_digest_inventory_only' for r in rows))

    def test_binding_mismatch_nonexistent_commit_and_unsafe_paths_refuse(self):
        s = self.scenario().finish()
        with self.assertRaisesRegex(ValueError, 'Git evidence unavailable'):
            s.build(record_commit='0'*40)
        for path in ('/Users/edr/DO-NOT-READ', '../record.json', 'restricted/record.json',
                     'night-custody/record.json', 'jw-b5-fake/record.json'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'safe repository-relative'):
                s.build(record_path=path)
        s.series['previous_record']['sha256'] = '0'*64
        s.write('series.json', s.series)
        s.series_commit = s.commit()
        with self.assertRaisesRegex(ValueError, 'binding mismatch'):
            s.build()

    def test_secondary_meter_gaps_do_not_block_and_all_members_are_listed(self):
        s = self.scenario()
        s.sources['pilot']['extra_checks']['km003c']['members']['spam'] = {
            'status': 'missing', 'flags': ['meter.member_gap', 'meter.clock_unresolved']}
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['checks']['meter_samples_clock']['gaps']['spam'],
                         ['meter.member_gap', 'meter.clock_unresolved'])
        s = self.scenario()
        del s.sources['pilot']['extra_checks']['km003c']['members']['spam']
        self.assertEqual(s.finish().build()['checks']['meter_samples_clock']['status'], 'fail')

    def test_first_w1_packet_uses_r1_coverage_without_claiming_u_checks(self):
        s = self.scenario('R1')
        s.next_plan.update(window='W1', role='development')
        del s.thermal['model_windows']
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        evaluated = cad.next_arm_triage(packet, INTERNAL, now_epoch_s=111)
        self.assertTrue(evaluated['admitted'], evaluated['reasons'])
        self.assertEqual(evaluated['checks']['calibration_stop']['status'], 'not_applicable')
        for name in ('thermal_escalation', 'cohort_pool_rules', 'sentinel_roster', 'member_eligibility'):
            self.assertEqual(packet['checks'][name]['status'], 'not_applicable')

    def test_two_zero_records_and_lead_ruling_remain_in_packet_history(self):
        s = self.scenario('C1-refusal-1')
        def refuse(scenario):
            scenario.absent_captures = set(cad.CAL_PAIRS)
            scenario.sources['result'].update(verdict='REFUSED', chain_exit_code=None, chain_sha256=None)
            scenario.omit_sources.update(('chain_started', 'chain_exited'))
            for m in scenario.thermal['members']:
                m.update(excluded=True, calibration_exclusions=['member.runtime_failure'])
            scenario.sources['exclusions']['members_excluded'] = [
                {'run_id': p, 'codes': ['member.runtime_failure']} for p in cad.CAL_PAIRS]
        refuse(s)
        s.finish()
        first = {'record_commit': s.record_commit, 'record_path': 'record.json'}
        s2 = Scenario(s.root, 'C1-refusal-2')
        refuse(s2)
        s2.series['history'] = [first]
        s2.finish()
        packet = s2.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertEqual(packet['calibration_decision']['decision'], 'escalate_to_lead')
        ruling = {'type': 'lead_ruling', 'ruling_id': 'LEAD-SYNTHETIC-1', 'after_window': s2.window}
        s2.series['history'].append(ruling)
        s2.write('series.json', s2.series)
        s2.series_commit = s2.commit()
        packet = s2.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['calibration_windows'][-1], ruling)
        self.assertEqual(packet['calibration_decision']['attempted'], 0)
        self.assertEqual(packet['calibration_decision']['zero_capture_refusals'], 2)

    def test_missing_source_symlink_and_broken_r1_history_refuse(self):
        s = self.scenario('R1')
        s.next_plan.update(window='W1', role='development')
        s.series['history'] = [{'record_commit': '0'*40, 'record_path': 'record.json'}]
        packet = s.finish().build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertFalse(cad.next_arm_triage(packet, INTERNAL, now_epoch_s=111)['admitted'])
        s = self.scenario()
        s.omit_sources.add('courier')
        self.assertEqual(s.finish().build()['checks']['terminal_completion']['status'], 'fail')
        s = self.scenario().finish()
        (s.root / 'link.json').symlink_to('/DO-NOT-OPEN')
        commit = s.commit()
        with self.assertRaisesRegex(ValueError, 'regular blob'):
            builder.GitEvidence(s.root).read(commit, 'link.json')

    def test_quiet_and_live_meter_cannot_use_old_or_future_observations(self):
        for name in ('quiet', 'live'):
            for epoch in (90, 112, 100):
                with self.subTest(name=name, epoch=epoch):
                    s = self.scenario()
                    getattr(s, name)['observed_at_epoch_s'] = epoch
                    s.series['quiet_requirements']['max_age_s'] = 5
                    packet = s.finish().build()
                    check = 'quiet_start_state' if name == 'quiet' else 'meter_samples_clock'
                    self.assertEqual(packet['checks'][check]['status'], 'fail')

    def test_desk_deferral_only_later_unchanged_and_changed_code_requires_new_pass(self):
        s = self.scenario('C1')
        # A separate last-passed desk remains available while this desk runs off MBP.
        s.finish()
        s.sources['desk'].update(status='running_off_mbp', pilot_status='instrument_incomplete')
        desk_ref = s.write('evidence/desk.json', s.sources['desk'])
        s.record['sources']['desk'] = desk_ref
        record_ref = s.write('record.json', s.record)
        old_record = s.record_commit
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, **record_ref}
        s.series['history'] = [{'record_commit': s.record_commit, 'record_path': 'record.json'}]
        s.write('series.json', s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertFalse(packet['code_or_config_changed'])
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'deferred')
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertNotEqual(old_record, s.record_commit)
        s = self.scenario().finish(change_code=True)
        packet = s.build()
        self.assertTrue(packet['code_or_config_changed'])
        self.assertIn('does not cover next', packet['checks']['full_desk_gate']['basis'])

    def test_counts_derived_from_capture_and_final_exclusions_not_series_assertions(self):
        s = self.scenario('C1')
        s.thermal['members'][0].update(excluded=True, calibration_exclusions=['thermal.state_unobserved'])
        s.sources['exclusions']['members_excluded'] = [{'run_id': 'spam', 'codes': ['thermal.state_unobserved']}]
        s.series['eligible_benign'] = {'spam': 7, 'bank': 7}  # deliberately ignored
        packet = s.finish().build()
        self.assertEqual(packet['calibration_windows'][0]['eligible_benign'], {'spam': 0, 'bank': 1})
        self.assertEqual(packet['calibration_windows'][0]['captured_members'], 2)

    def test_divergent_u3_pair_requires_x5_adjudication_not_new_member_exclusions(self):
        s = self.scenario()
        for member in s.thermal['members']:
            member['identical_work_group'] = 'pair'
        s.thermal['members'][0]['tokens'] = [[9]]
        self.assertEqual(s.finish().build()['checks']['member_eligibility']['status'], 'fail')
        s = self.scenario()
        for member in s.thermal['members']:
            member['identical_work_group'] = 'pair'
        s.thermal['members'][0]['tokens'] = [[9]]
        s.thermal['model_windows']['tiny/W1']['U3']['pairs'] = [
            {'status': 'excluded', 'exclusion': 'X5', 'token_identical': False}]
        packet = s.finish().build()
        self.assertEqual(packet['checks']['member_eligibility']['status'], 'pass')

    def test_template_is_fail_closed_and_cli_never_overwrites(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(builder.main(['--emit-triage-template']), 0)
        self.assertFalse(cad.next_arm_triage(json.loads(output.getvalue())['packet'], INTERNAL)['admitted'])
        s = self.scenario().finish()
        target = s.root / 'packet.json'
        argv = ['--repo', str(s.root), '--record-commit', s.record_commit, '--record-path', 'record.json',
                '--series-commit', s.series_commit, '--series-path', 'series.json',
                '--pushed-ref', 'refs/remotes/synthetic/records', '--output', str(target)]
        self.assertEqual(builder.main(argv), 0)
        self.assertTrue(json.loads(target.read_text())['packet_preflight']['ready'])
        with self.assertRaises(FileExistsError):
            builder.main(argv)

    def test_duplicate_keys_and_nonfinite_json_refuse(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                builder.decode(raw)

    def test_packet_observation_expiry_is_rechecked_by_arm_consumer(self):
        packet = self.scenario().finish().build()
        self.assertEqual(packet['valid_until_epoch_s'], 140)
        self.assertTrue(cad.next_arm_triage(packet, INTERNAL, now_epoch_s=140)['admitted'])
        self.assertIn('triage packet quiet/meter observations expired or malformed',
                      cad.next_arm_triage(packet, INTERNAL, now_epoch_s=141)['reasons'])

    def test_real_arm_consumer_retains_packet_bytes_digest_commit_and_checks_expiry(self):
        from scripts import align_v4_session as session
        s = self.scenario().finish()
        packet = s.build()
        raw = (json.dumps(packet, indent=2) + '\n').encode()
        path = s.root / 'packet.json'
        path.write_bytes(raw)
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        with patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'synthetic raw')):
            def arm(epoch):
                return session.arm_checks(s.root, {}, next_arm_triage=path, now=lambda: epoch,
                    runner=lambda argv: subprocess.CompletedProcess(argv, 0, 'synthetic', ''),
                    obc_off_attested_by='synthetic', topup_completed_at=100, topup_source='synthetic')
            record = arm(111)
            self.assertTrue(record['admitted'], record['reasons'])
            source = record['next_arm_triage_source']
            self.assertEqual(base64.b64decode(source['bytes_base64']), raw)
            self.assertEqual(source['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(source['record_commit'], s.record_commit)
            self.assertFalse(arm(141)['admitted'])


class LeadRulingTests(unittest.TestCase):
    def test_two_zeros_escalate_until_bound_lead_ruling_without_changing_counts(self):
        rows = [{'window': f'C1-refusal-{i}', 'status': 'final', 'captured_members': 0,
                 'eligible_benign': {'spam': 0, 'bank': 0}} for i in (1, 2)]
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'escalate_to_lead')
        ruling = {'type': 'lead_ruling', 'ruling_id': 'synthetic-lead-1', 'after_window': 'C1-refusal-2'}
        ruled = cad.calibration_stop(rows + [ruling])
        self.assertEqual((ruled['decision'], ruled['attempted'], ruled['zero_capture_refusals']), ('continue', 0, 2))
        for bad in ({**ruling, 'ruling_id': ''}, {**ruling, 'after_window': 'wrong'}, ruling):
            candidate = rows + [bad] if bad != ruling else rows[:1] + [bad]
            with self.assertRaisesRegex(ValueError, 'lead_ruling'):
                cad.calibration_stop(candidate)
        self.assertEqual(cad.calibration_stop(rows + [ruling] + [dict(rows[0], window='third'),
                         dict(rows[0], window='fourth')])['decision'], 'escalate_to_lead')
        eight = [{'window': f'C{i}', 'status': 'final', 'captured_members': 14,
                  'eligible_benign': {'spam': 7, 'bank': 7}} for i in range(1, 9)]
        self.assertEqual(cad.calibration_stop(rows + [ruling] + eight)['decision'], 'calibration_complete')
        with self.assertRaises(ValueError):
            cad.calibration_stop(rows + [ruling] + eight + [dict(eight[0], window='C9')])


if __name__ == '__main__':
    unittest.main()
