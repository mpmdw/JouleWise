"""R12 next-arm packet builder and the arm's rebuild of it. Synthetic Git records only.

The arm rebuilds the packet from the identities the supplied one names (a packet is a pointer,
never trusted data), judges its own build, and refuses a supplied packet that differs. No
measurements, probes, models or network.
"""
import contextlib
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
from joulewise.align.apple import v4_registration as registration

INTERNAL = {r['id']: True for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.ARM}
CONFIG = dict(zip(builder.FROZEN_D_SLOT_KEYS, (4096, 30, 128, 4)))
IDENTITY = {'model_source': 'synthetic-tiny', 'model_revision': 'fixture',
            'runtime_sha256': 'a'*64, 'execution_policy_sha256': 'b'*64}
NOW = 111.0
CODE_PATH = 'scripts/run_night.py'      # a bound artifact: its bytes move the artifact-set digest


class Scenario:
    """One window record (and the series state that points at it) in a synthetic Git repository."""

    def __init__(self, directory, window='W1', *, previous=None, captured=True, eligible=True,
                 b_bar=True):
        self.root = Path(directory)
        if previous is None:
            self.git('init', '-q')
        self.previous = previous
        self.window = window
        self.dir = 'w-' + window.replace('#', '_')
        self.policy = {'idle_s': 300, 'delta_slow_c': 1., 'quantization_bits': 8}
        self.members = [{'run_id': f'{p}-{self.dir}', 'model_id': 'tiny', 'role': 'D', 'condition': 'benign',
                         'task_pair': p} for p in cad.CAL_PAIRS]
        ids = [m['run_id'] for m in self.members]
        plan_id = 'synthetic-' + self.dir
        self.sources = {
            'plan': {'plan_id': plan_id, 'receipt_class': 'HAZARD_PACK', 'custody_root': '/DO-NOT-FOLLOW/custody'},
            'collection_plan': {'members': self.members, 'thermal_policy': dict(self.policy)},
            'result': {'schema': 'joulewise.unattended_night_result.v1', 'plan_id': plan_id,
                       'receipt_class': 'HAZARD_PACK', 'verdict': 'GO', 'chain_exit_code': 0,
                       'chain_sha256': 'c'*64, 'ended_epoch_s': 100},
            'chain_started': {'pgid': 123}, 'chain_exited': {'exit_code': 0},
            'courier': {'sent': True}, 'courier_sent': b'',
            'watchdog_state': {},
            'pilot': {'status': 'instrument_ok', 'checks': {'synthetic_check': True}, 'extra_checks': {
                'thermal': {'schema': 'joulewise.align.thermal_desk.v1',
                    'model_windows': {f'tiny/{window}': {f'U{k}': {'status': 'pass' if k < 4 else 'inconclusive'}
                                                        for k in range(1, 6)}},
                    'members': [{'id': i, 'model': 'tiny', 'gated': True, 'role': 'D',
                        'window': window, 'configuration': dict(CONFIG), 'cohort_identity': dict(IDENTITY),
                        'excluded': False, 'calibration_exclusions': [], 'flags': [], 'coverage': [],
                        'pm_period_s': .1, 'pm_max_gap_s': .1, 'turn_observation': [],
                        'tokens': [[1, 2, 3]]} for i in ids]},
                'km003c': {'members': {i: {'status': 'available', 'flags': []} for i in ids}}}},
            'desk': {'plan_id': plan_id, 'pilot_status': 'instrument_ok',
                     'checks': {'synthetic_check': True, 'v4_B_bar': b_bar}, 'harvest_status': 'ok'},
            'exclusions': {'members_excluded': []}}
        self.record = {'schema': builder.RECORD_SCHEMA, 'window': window,
                       'role': 'development' if window in ('W1', 'R1') else 'calibration',
                       'finalized_at_epoch_s': 101, 'previous_record': previous.link if previous else None}
        self.quiet = {'observed_at_epoch_s': 110, 'cooldown_s': 300, 'display_off_s': 60,
                      'dwell_s': 60, 'active_work': []}
        self.next_plan = {'role': 'calibration', 'window': 'C1',
                          'configuration': {**CONFIG, 'cohort_identity': dict(IDENTITY)},
                          'thermal_policy': dict(self.policy),
                          'members': [{'run_id': f'sentinel-{i}', 'role': 'sentinel'} for i in range(4)]}
        self.series = {'schema': builder.SERIES_SCHEMA,
                       'quiet_requirements': {'cooldown_s': 300, 'display_off_s': 60, 'dwell_s': 60, 'max_age_s': 30},
                       'lead_rulings': [], 'pool_members': [],
                       'sentinel_ids': [f'sentinel-{i}' for i in range(4)], 'escalations': []}
        self.absent_captures = set() if captured else set(ids)
        self.omit_sources = set()
        self.raw_custody = False
        if not captured:
            self.sources['result'].update(verdict='REFUSED', chain_exit_code=None, chain_sha256=None)
            self.omit_sources.update(('chain_started', 'chain_exited'))
            for m in self.thermal['members']:
                m.update(excluded=True, calibration_exclusions=['member.runtime_failure'])
            self.sources['exclusions']['members_excluded'] = [{'run_id': i, 'codes': ['member.runtime_failure']} for i in ids]
        if not eligible:
            self.thermal['members'][0].update(excluded=True, calibration_exclusions=['thermal.state_unobserved'])
            self.sources['exclusions']['members_excluded'] = [{'run_id': ids[0], 'codes': ['thermal.state_unobserved']}]

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
        self.git('commit', '-qm', 'synthetic evidence', '--allow-empty')
        return self.git('rev-parse', 'HEAD')

    def finish(self, *, change_code=False, code=b'synthetic-code-v1\n'):
        self.write(CODE_PATH, code)
        self.record['code_commit'] = self.code_commit = self.commit()
        d = self.dir
        self.sources['watchdog_state'].setdefault('released_terminal_windows', [
            f"{self.sources['plan']['plan_id']}:/DO-NOT-FOLLOW/custody:"
            f"{builder.digest((json.dumps(self.sources['result'], sort_keys=True) + chr(10)).encode())}"])
        self.record['sources'] = {k: self.write(f'{d}/evidence/{k}.json', v)
                                  for k, v in self.sources.items() if k not in self.omit_sources}
        pairs = [m['run_id'] for m in self.members]
        self.record['captures'] = {i: None if i in self.absent_captures else (
            {'locator': '/DO-NOT-FOLLOW/' + i, 'sha256': builder.digest(b'synthetic'), 'bytes': 9}
            if self.raw_custody else self.write(f'{d}/captures/{i}.jsonl', b'{"monotonic_ns":1,"power_w":1}\n'))
            for i in pairs}
        self.record['raw_evidence'] = [self.write(f'{d}/raw/sidecar.jsonl', b'{"temperature_c":30}\n')]
        if self.raw_custody:
            self.record['raw_evidence'].extend(self.record['captures'].values())
        self.record_path = f'{d}/record.json'
        index = self.write(self.record_path, self.record)
        self.record_commit = self.commit()
        self.git('update-ref', 'refs/remotes/synthetic/records', self.record_commit)
        self.link = {'commit': self.record_commit, 'path': self.record_path, 'sha256': index['sha256']}
        self.series['last_passed_record'] = dict(self.link)
        if change_code:
            self.write(CODE_PATH, b'synthetic-code-v2\n')       # the working tree (the arm's code) moves on
        self.series.update(previous_record=dict(self.link),
                           quiet=self.write(f'{d}/series/quiet.json', self.quiet),
                           next_plan=self.write(f'{d}/series/next_plan.json', self.next_plan))
        self.series_path = builder.SERIES_PATH       # one canonical ledger, rewritten by each window
        self.write(self.series_path, self.series)
        self.series_commit = self.commit()
        return self

    def identities(self, **changes):
        args = dict(record_commit=self.record_commit, record_path=self.record_path,
                    series_commit=self.series_commit, series_path=self.series_path,
                    pushed_ref='refs/remotes/synthetic/records')
        args.update(changes)
        return args

    def build(self, *, now=NOW, current=None, **changes):
        current = current or registration.artifact_set_digest(self.root)
        return builder.build_packet(self.root, **self.identities(**changes), now_epoch_s=now,
                                    current_artifact_set_sha256=current)

    @property
    def thermal(self):
        return self.sources['pilot']['extra_checks']['thermal']


def evaluate(scenario, packet, now=NOW, internal=INTERNAL):
    """The gate the arm applies: rebuild from the packet's named identities, compare, judge the rebuild."""
    current = registration.artifact_set_digest(scenario.root)
    try:
        built, matches = builder.rebuild_and_compare(scenario.root, packet, now_epoch_s=now,
                                                     current_artifact_set_sha256=current)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return {'admitted': False, 'reasons': [f'packet could not be rebuilt from its named sources: {exc}']}
    result = cad.next_arm_triage(built, internal, {
        'artifact_set_sha256': current, 'record_commit_exists': True, 'record_bound': True}, now_epoch_s=now)
    if not matches:
        result['admitted'] = False
        result['reasons'].append('packet does not match its committed sources')
    return result


class Base(unittest.TestCase):
    def scenario(self, window='W1', **kwargs):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-synthetic-')
        self.addCleanup(temp.cleanup)
        return Scenario(temp.name, window, **kwargs)

    def calibration_series(self, specs):
        """Successive calibration records in one repository; specs = [(window, captured, eligible), ...]."""
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-series-')
        self.addCleanup(temp.cleanup)
        first = Scenario(temp.name, 'W1').finish()
        previous = first
        for window, captured, eligible, *rest in specs:
            current = Scenario(temp.name, window, previous=previous, captured=captured, eligible=eligible,
                               b_bar=rest[0] if rest else True).finish()
            previous = current
        return previous


class PacketTests(Base):
    def test_w1_record_admits_and_binds_all_raw_bytes_without_following_custody(self):
        s = self.scenario().finish()
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight']['reasons'])
        result = evaluate(s, packet)
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertEqual(packet['record_commit'], s.record_commit)
        self.assertEqual(packet['checks']['sentinel_roster']['sentinel_ids'], s.series['sentinel_ids'])
        self.assertEqual(set(packet['checks']), {r['id'] for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.PACKET})
        self.assertEqual(set(packet['entry_sources']), set(cad.TRIAGE_IDS))
        self.assertEqual(len(cad.TRIAGE_IDS), 16)      # 15 gating + non-gating meter_coverage (battery_window added by ruling 9)
        self.assertEqual(packet['arm_pending'], list(INTERNAL))
        self.assertIn('meter_reader_live', packet['arm_pending'])
        self.assertEqual(packet, s.build())          # reproducible: the arm's clock is not embedded
        for source in packet['evidence']:
            actual = subprocess.run(['git', '-C', str(s.root), 'show', source['commit'] + ':' + source['path']],
                                    check=True, capture_output=True).stdout
            self.assertEqual(hashlib.sha256(actual).hexdigest(), source['sha256'])
        paths = {r['path'] for r in packet['evidence']}
        self.assertTrue({s.record_path, s.series_path, f'{s.dir}/raw/sidecar.jsonl'} <= paths)

    def test_each_packet_entry_refuses_for_its_documented_reason(self):
        mutations = {
            'record_committed': (lambda s: s.record.pop('finalized_at_epoch_s'), 'record finalization missing'),
            'terminal_completion': (lambda s: s.sources['watchdog_state'].update(released_terminal_windows=[]), 'watchdog empty-process'),
            'quiet_start_state': (lambda s: s.quiet.update(active_work=['hashing']), 'evidence traffic remains'),
            'capture_faults': (lambda s: s.thermal['members'][0].pop('coverage'), 'X1-X8 tabulation missing'),
            'thermal_escalation': (lambda s: s.thermal['model_windows']['tiny/W1']['U1'].update(status='fail'), 'prospective recorded escalation'),
            'cohort_pool_rules': (lambda s: s.thermal['members'][0]['configuration'].update(max_turns=5), 'four-slot cohort'),
            'sentinel_roster': (lambda s: s.next_plan['members'].pop(), 'two extra sentinels'),
            'member_eligibility': (lambda s: s.thermal['members'][0].update(excluded=True), 'final exclusions disagree'),
            'full_desk_gate': (lambda s: s.sources['desk'].update(pilot_status='instrument_incomplete'), 'no passing desk'),
        }
        for name, (mutate, reason) in mutations.items():
            with self.subTest(name=name):
                s = self.scenario()
                mutate(s)
                packet = s.finish().build()
                self.assertEqual(packet['checks'][name]['status'], 'fail')
                self.assertIn(reason, packet['checks'][name]['basis'])
                self.assertFalse(packet['packet_preflight']['ready'])
                self.assertIn('triage ' + name + ' failed', evaluate(s, packet)['reasons'])
        s = self.scenario().finish()
        packet = s.build()
        for name in INTERNAL:
            with self.subTest(name=name):
                self.assertIn('triage ' + name + ' failed or unevaluated',
                              evaluate(s, packet, internal={**INTERNAL, name: False})['reasons'])
        packet['next_window_role'] = 'test'
        self.assertFalse(evaluate(s, packet)['admitted'])

    def test_raw_digest_mismatch_and_unpushed_record_refuse(self):
        s = self.scenario().finish()
        record = copy.deepcopy(s.record)
        record['raw_evidence'][0]['sha256'] = '0'*64
        index = s.write(s.record_path, record)
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, 'path': s.record_path, 'sha256': index['sha256']}
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        self.assertIn('SHA-256 mismatch', s.build()['checks']['record_committed']['basis'])
        s = self.scenario().finish()
        self.assertEqual(s.build(pushed_ref='refs/remotes/missing/records')['checks']['record_committed']['status'], 'fail')
        self.assertIn('remote-tracking', s.build(pushed_ref='HEAD')['checks']['record_committed']['basis'])

    def test_dirty_worktree_does_not_change_committed_evidence(self):
        s = self.scenario().finish()
        original = s.build()
        s.write(f'{s.dir}/evidence/result.json', {'forged': True})
        self.assertEqual(s.build(current=registration.artifact_set_digest(s.root)), original)

    def test_large_raw_custody_digests_are_retained_without_opening_locators(self):
        s = self.scenario()
        s.raw_custody = True
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        rows = [r for r in packet['evidence'] if r.get('locator')]
        self.assertEqual(len(rows), 2)
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
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        with self.assertRaisesRegex(ValueError, 'binding mismatch'):
            s.build()

    def test_secondary_meter_coverage_never_blocks_even_when_missing(self):
        s = self.scenario()
        s.sources['pilot']['extra_checks']['km003c']['members'][s.members[0]['run_id']] = {
            'status': 'missing', 'flags': ['meter.member_gap', 'meter.clock_unresolved']}
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['checks']['meter_coverage']['status'], 'recorded')
        self.assertEqual(packet['checks']['meter_coverage']['gaps'][s.members[0]['run_id']],
                         ['meter.member_gap', 'meter.clock_unresolved'])
        s = self.scenario()
        del s.sources['pilot']['extra_checks']['km003c']['members'][s.members[0]['run_id']]
        packet = s.finish().build()
        self.assertEqual(packet['checks']['meter_coverage']['status'], 'recorded')
        self.assertTrue(packet['packet_preflight']['ready'])
        s = self.scenario()
        del s.sources['pilot']['extra_checks']['km003c']             # no tabulation at all (R1 -> W1)
        packet = s.finish().build()
        self.assertEqual(packet['checks']['meter_coverage']['tabulation'], 'missing')
        self.assertTrue(evaluate(s, packet)['admitted'])

    def test_first_w1_packet_uses_r1_coverage_without_claiming_u_checks(self):
        s = self.scenario('R1')
        s.next_plan.update(window='W1', role='development')
        del s.thermal['model_windows']
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        evaluated = evaluate(s, packet)
        self.assertTrue(evaluated['admitted'], evaluated['reasons'])
        self.assertEqual(evaluated['checks']['calibration_stop']['status'], 'not_applicable')
        for name in ('thermal_escalation', 'cohort_pool_rules', 'sentinel_roster', 'member_eligibility'):
            self.assertEqual(packet['checks'][name]['status'], 'not_applicable')

    def test_quiet_cannot_use_old_or_future_observations_judged_at_the_arms_clock(self):
        for epoch in (90, 112, 100):
            with self.subTest(epoch=epoch):
                s = self.scenario()
                s.quiet['observed_at_epoch_s'] = epoch
                s.series['quiet_requirements']['max_age_s'] = 5
                self.assertEqual(s.finish().build()['checks']['quiet_start_state']['status'], 'fail')
        s = self.scenario().finish()
        self.assertEqual(s.build(now=140.0)['checks']['quiet_start_state']['status'], 'pass')   # 30 s old: at the limit
        self.assertEqual(s.build(now=141.0)['checks']['quiet_start_state']['status'], 'fail')

    def test_counts_derived_from_capture_and_final_exclusions_not_series_assertions(self):
        s = self.calibration_series([('C1', True, False)])
        s.series['eligible_benign'] = {'spam': 7, 'bank': 7}          # deliberately ignored
        packet = s.build()
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
        self.assertEqual(s.finish().build()['checks']['member_eligibility']['status'], 'pass')

    def test_l1_a_failing_u1_u3_gives_that_model_zero_eligible_from_the_window(self):
        s = self.calibration_series([])
        s2 = Scenario(s.root, 'C1', previous=s)
        s2.thermal['model_windows']['tiny/C1']['U2']['status'] = 'fail'
        s2.finish()
        self.assertEqual(s2.build()['calibration_windows'][0]['eligible_benign'], {'spam': 0, 'bank': 0})

    def test_template_is_fail_closed_and_cli_never_overwrites(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(builder.main(['--emit-triage-template']), 0)
        template = json.loads(output.getvalue())
        self.assertFalse(cad.next_arm_triage(template['packet'], INTERNAL, now_epoch_s=NOW)['admitted'])
        self.assertIn('record', template)
        self.assertIsNone(template['record']['previous_record'])
        self.assertIn('lead_rulings', template['series'])
        s = self.scenario().finish()
        target = s.root / 'packet.json'
        argv = ['--repo', str(s.root), '--record-commit', s.record_commit, '--record-path', s.record_path,
                '--series-commit', s.series_commit, '--series-path', s.series_path,
                '--pushed-ref', 'refs/remotes/synthetic/records', '--output', str(target)]
        with patch('time.time', return_value=NOW):
            self.assertEqual(builder.main(argv), 0)
            self.assertTrue(json.loads(target.read_text())['packet_preflight']['ready'])
            with self.assertRaises(FileExistsError):
                builder.main(argv)

    def test_duplicate_keys_and_nonfinite_json_refuse(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                builder.decode(raw)

    def test_missing_source_and_symlink_refuse(self):
        s = self.scenario()
        s.omit_sources.add('courier')
        self.assertEqual(s.finish().build()['checks']['terminal_completion']['status'], 'fail')
        s = self.scenario().finish()
        (s.root / 'link.json').symlink_to('/DO-NOT-OPEN')
        commit = s.commit()
        with self.assertRaisesRegex(ValueError, 'regular blob'):
            builder.GitEvidence(s.root).read(commit, 'link.json')


class HistoryChainTests(Base):
    def test_hash_linked_history_gives_counted_windows_in_order_and_detects_omission(self):
        s = self.calibration_series([('C1', True, True), ('C2', True, True), ('C3', True, True)])
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['window'] for r in packet['calibration_windows']], ['C1', 'C2', 'C3'])
        self.assertEqual(packet['calibration_decision']['attempted'], 3)
        # an omitted attempt (C2 missing between C1 and C3) cannot be hidden: the link is the history
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-omit-')
        self.addCleanup(temp.cleanup)
        first = Scenario(temp.name, 'W1').finish()
        c1 = Scenario(temp.name, 'C1', previous=first).finish()
        c3 = Scenario(temp.name, 'C3', previous=c1).finish()
        omitted = c3.build()
        self.assertFalse(omitted['packet_preflight']['ready'])
        self.assertIn('omitted', omitted['calibration_error'])

    def test_a_forged_link_digest_and_a_chain_that_never_reaches_w1_refuse(self):
        s = self.calibration_series([('C1', True, True)])
        record = copy.deepcopy(s.record)
        record['previous_record'] = {**record['previous_record'], 'sha256': '0'*64}
        index = s.write(s.record_path, record)
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, 'path': s.record_path, 'sha256': index['sha256']}
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('link digest mismatch', packet['calibration_error'])
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-nochain-')
        self.addCleanup(temp.cleanup)
        orphan = Scenario(temp.name, 'C1').finish()          # a first record that is not R1/W1
        packet = orphan.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('first v4 record', packet['calibration_error'])

    def test_zero_capture_retry_keeps_the_window_id_with_an_attempt_suffix(self):
        s = self.calibration_series([('C1', True, True), ('C2', False, True), ('C2#2', True, True)])
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['window'] for r in packet['calibration_windows']], ['C1', 'C2', 'C2#2'])
        decision = packet['calibration_decision']
        self.assertEqual((decision['attempted'], decision['zero_capture_refusals']), (2, 1))
        # the frozen order is unchanged: a retry cannot take the next number or skip its own
        for bad in ([('C1', True, True), ('C2', False, True), ('C3', True, True)],
                    [('C1', True, True), ('C1#3', False, True)],
                    [('C1', True, True), ('C1#2', True, True)]):
            with self.subTest(bad=[b[0] for b in bad]):
                self.assertFalse(self.calibration_series(bad).build()['packet_preflight']['ready'])

    def test_battery_window_follows_the_desk_b_bar_along_the_chain(self):
        # Lead ruling 9 (W1-BLOCKERS): pass; first non-pass resumes automatically; a second
        # consecutive non-pass needs a signed battery ruling whose text digest the builder computes.
        passed = self.calibration_series([('C1', True, True)]).build()
        self.assertEqual(passed['checks']['battery_window']['status'], 'pass')
        first = self.calibration_series([('C1', True, True), ('C2', True, True, False)]).build()
        self.assertEqual(first['checks']['battery_window']['consecutive_non_pass'], 1)
        self.assertTrue(first['packet_preflight']['ready'], first['packet_preflight'])      # automatic_resume
        s = self.calibration_series([('C1', True, True, False), ('C2', True, True, False)])
        second = s.build()
        self.assertEqual(second['checks']['battery_window']['consecutive_non_pass'], 2)
        self.assertFalse(second['packet_preflight']['ready'])
        text = b'LEAD BATTERY DISPOSITION SYNTHETIC-B1: resume after two non-passing B windows\n'
        ref = s.write(f'{s.dir}/rulings/battery-1.txt', text)
        s.series['battery_rulings'] = [{'ruling_id': 'SYNTHETIC-B1', 'after_window': 'C2', 'text': ref,
                                        'lead_signature': 'lead: synthetic-battery 2026-11-08'}]
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        ruled = s.build()
        self.assertEqual(ruled['battery_rulings'], [{
            'ruling_id': 'SYNTHETIC-B1', 'text_sha256': hashlib.sha256(text).hexdigest(), 'after_window': 'C2',
            'lead_signature': 'lead: synthetic-battery 2026-11-08'}])
        self.assertTrue(ruled['packet_preflight']['ready'], ruled['packet_preflight'])
        # a passing window in between resets the streak; a ruling for another window does not resume
        reset = self.calibration_series([('C1', True, True, False), ('C2', True, True), ('C3', True, True, False)]).build()
        self.assertEqual(reset['checks']['battery_window']['consecutive_non_pass'], 1)
        s.series['battery_rulings'][0]['after_window'] = 'C1'
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        self.assertFalse(s.build()['packet_preflight']['ready'])
        # a failed B bar alone does not fail the full desk (the exempt key matches the session's)
        from scripts import align_v4_session as session
        self.assertEqual(builder.FULL_DESK_GATE_EXEMPT, session.FULL_DESK_GATE_EXEMPT)
        self.assertEqual(first['checks']['full_desk_gate']['status'], 'pass')

    def test_two_zero_capture_attempts_escalate_until_a_ruling_with_a_committed_text(self):
        s = self.calibration_series([('C1', False, True), ('C1#2', False, True)])
        packet = s.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertEqual(packet['calibration_decision']['decision'], 'escalate_to_lead')
        text = b'LEAD RULING SYNTHETIC-1: re-arm C1 after two zero-capture refusals\n'
        ref = s.write(f'{s.dir}/rulings/synthetic-1.txt', text)
        s.series['lead_rulings'] = [{'ruling_id': 'SYNTHETIC-1', 'after_window': 'C1#2', 'text': ref,
                                     'lead_signature': 'lead: synthetic-ruling 2026-11-08'}]
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertEqual(packet['lead_rulings'], [{
            'ruling_id': 'SYNTHETIC-1', 'text_sha256': hashlib.sha256(text).hexdigest(),
            'resets': 'zero_capture_escalation', 'after_window': 'C1#2',
            'lead_signature': 'lead: synthetic-ruling 2026-11-08'}])        # the digest is computed, not entered
        self.assertEqual(packet['calibration_decision']['decision'], 'continue')
        self.assertEqual(packet['calibration_decision']['zero_capture_refusals'], 2)
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        for bad in ({'ruling_id': 'X', 'after_window': 'C9', 'text': ref, 'lead_signature': 'lead: s 2026-11-08'},
                    {'ruling_id': 'X', 'after_window': 'C1#2', 'text': {**ref, 'sha256': '0'*64},
                     'lead_signature': 'lead: s 2026-11-08'},
                    {'ruling_id': 'X', 'after_window': 'C1#2', 'text': ref, 'lead_signature': 'PENDING'},
                    {'ruling_id': 'X', 'after_window': 'C1#2', 'text': ref}):
            s.series['lead_rulings'] = [bad]
            s.write(s.series_path, s.series)
            s.series_commit = s.commit()
            with self.subTest(bad=str(bad)[:60]):
                self.assertFalse(s.build()['packet_preflight']['ready'])


class DeskDerivationTests(Base):
    def test_last_desk_digest_is_computed_from_committed_bytes_and_drives_the_desk_requirement(self):
        s = self.calibration_series([('C1', True, True)])
        s.series['last_passed_record'] = dict(s.link)
        packet = s.build()
        self.assertEqual(packet['last_desk_passed_artifact_set_sha256'],
                         registration.artifact_set_digest_at(s.root, s.code_commit))
        self.assertNotIn('code_or_config_changed', packet)
        self.assertNotIn('previous_window_is_w1', packet)
        self.assertEqual(packet['last_desk_passed_artifact_set_sha256'], registration.artifact_set_digest(s.root))
        # unchanged later window: a desk still running off the MBP defers
        deferred = s.sources['desk'].update(status='running_off_mbp', pilot_status='instrument_incomplete')
        self.assertIsNone(deferred)
        s.write(f'{s.dir}/evidence/desk.json', s.sources['desk'])
        s.record['sources']['desk'] = {'path': f'{s.dir}/evidence/desk.json',
                                       'sha256': hashlib.sha256((s.root / f'{s.dir}/evidence/desk.json').read_bytes()).hexdigest()}
        index = s.write(s.record_path, s.record)
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, 'path': s.record_path, 'sha256': index['sha256']}
        s.series['last_passed_record'] = {'commit': first_commit(s), 'path': 'w-W1/record.json',
                                          'sha256': hashlib.sha256(subprocess.run(
                                              ['git', '-C', str(s.root), 'show', f'{first_commit(s)}:w-W1/record.json'],
                                              capture_output=True, check=True).stdout).hexdigest()}
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'deferred', packet['checks']['full_desk_gate'])

    def test_after_w1_or_a_code_change_the_full_desk_must_have_passed_on_the_current_state(self):
        s = self.scenario().finish()                                   # previous window W1, desk passed, same code
        self.assertEqual(s.build()['checks']['full_desk_gate']['status'], 'pass')
        changed = s.build(current=registration.artifact_set_digest(s.root).replace('0', '1', 1) or 'f'*64)
        if changed['checks']['full_desk_gate']['status'] == 'pass':      # digest happened to lack a 0
            changed = s.build(current='f'*64)
        self.assertEqual(changed['checks']['full_desk_gate']['status'], 'fail')
        self.assertIn('different code/config state', changed['checks']['full_desk_gate']['basis'])


def first_commit(scenario):
    return scenario.git('log', '--format=%H', '--reverse', '--', 'w-W1/record.json').splitlines()[0]


class ArmRebuildTests(Base):
    """The arm calls the builder itself; a supplied packet is a pointer, never trusted data."""

    def arm(self, s, packet, *, now=NOW, **kwargs):
        from scripts import align_v4_session as session
        from tests.align.test_v4_cadence import write_battery_log
        path = s.root / 'supplied-packet.json'
        if path.exists():
            path.unlink()
        path.write_text(json.dumps(packet, indent=2))
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        with patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'raw')):
            log = write_battery_log(Path(tempfile.mkdtemp(dir=s.root.parent)) / 'battery.jsonl', now)
            return session.arm_checks(s.root, {}, next_arm_triage=path, now=lambda: now, battery_log=log,
                                      runner=lambda argv: subprocess.CompletedProcess(argv, 0, 'pmset', ''),
                                      obc_off_attested_by='synthetic',
                                      meter_probe=kwargs.pop('meter_probe', lambda root: {'live': True, 'samples': 40}),
                                      **kwargs)

    def test_honest_packet_admits_and_the_arm_record_retains_its_own_build(self):
        s = self.scenario().finish()
        record = self.arm(s, s.build())
        self.assertTrue(record['admitted'], record['reasons'])
        triage = record['next_arm_triage']
        self.assertTrue(triage['supplied_packet_matches_rebuild'])
        self.assertEqual(triage['packet']['record_commit'], s.record_commit)
        self.assertEqual(triage['meter_live_evidence']['live'], True)
        self.assertEqual(triage['packet_sha256'], cad._canonical_sha256(triage['packet']))

    def test_edited_status_swapped_commit_forged_rows_and_planted_desk_digest_all_refuse(self):
        # Opus packet review HIGH-1: each of these armed on the v4 head before the arm rebuilt the packet.
        s = self.scenario()
        s.quiet.update(active_work=['hashing'])
        s.finish()
        honest = s.build()
        self.assertFalse(self.arm(s, honest)['admitted'])
        edited = copy.deepcopy(honest)
        edited['checks']['quiet_start_state'] = {'status': 'pass', 'basis': 'quiet start verified'}
        refused = self.arm(s, edited)
        self.assertFalse(refused['admitted'])
        self.assertFalse(refused['next_arm_triage']['supplied_packet_matches_rebuild'])
        self.assertIn('quiet_start_state', ' '.join(refused['reasons']))          # judged on the arm's own build
        s2 = self.scenario().finish()
        good = s2.build()
        swapped = copy.deepcopy(good)
        swapped['record_commit'] = s2.code_commit                                     # an unrelated commit that exists
        self.assertFalse(self.arm(s2, swapped)['admitted'])
        forged = copy.deepcopy(good)
        forged['calibration_windows'] = [{'window': f'C{i}', 'status': 'final', 'captured_members': 14,
                                          'eligible_benign': {'spam': 7, 'bank': 7}} for i in range(1, 9)]
        forged['next_window_role'] = 'test'
        out = self.arm(s2, forged)
        self.assertFalse(out['admitted'])
        self.assertNotEqual(out['next_arm_triage']['calibration']['decision'], 'calibration_complete')
        planted = copy.deepcopy(good)
        planted['last_desk_passed_artifact_set_sha256'] = registration.artifact_set_digest(s2.root)
        s2.write(CODE_PATH, b'synthetic-code-v2\n')                                   # the code moved after the desk passed
        moved = self.arm(s2, planted)
        self.assertFalse(moved['admitted'])

    def test_stale_packet_expired_packet_and_missing_expiry_refuse(self):
        s = self.scenario().finish()
        packet = s.build()
        self.assertTrue(self.arm(s, packet)['admitted'])
        late = self.arm(s, packet, now=141.0)                  # past the quiet observation's max age
        self.assertFalse(late['admitted'])
        no_expiry = copy.deepcopy(packet)
        del no_expiry['valid_until_epoch_s']
        self.assertFalse(self.arm(s, no_expiry)['admitted'])   # the rebuild restores it, but the supplied one differs
        self.assertFalse(self.arm(s, no_expiry)['next_arm_triage']['supplied_packet_matches_rebuild'])

    def test_unrebuildable_packets_and_a_dead_meter_refuse(self):
        s = self.scenario().finish()
        for bad in (None, {}, {'record_commit': s.record_commit}, {**s.build(), 'series_path': 'nope.json'}):
            with self.subTest(bad=str(bad)[:40]):
                record = self.arm(s, bad)
                self.assertFalse(record['admitted'])
                self.assertIsNotNone(record['next_arm_triage']['rebuild_error'])
        dead = self.arm(s, s.build(), meter_probe=lambda root: {'live': False, 'reason': 'no samples'})
        self.assertFalse(dead['admitted'])
        self.assertIn('next_arm_triage: triage meter_reader_live failed', dead['reasons'])
        broken = self.arm(s, s.build(), meter_probe=lambda root: (_ for _ in ()).throw(OSError('usb')))
        self.assertFalse(broken['admitted'])

    def test_the_default_live_meter_probe_runs_the_monitor_and_parses_its_stream(self):
        from scripts import align_v4_session as session
        from tests.align.test_km003c import fake_stream
        with tempfile.TemporaryDirectory() as tmp:
            def runner(argv, **kwargs):
                fake_stream(Path(argv[argv.index('--out')+1]))
                return subprocess.CompletedProcess(argv, 0, b'', b'')
            result = session._probe_meter_live(tmp, runner=runner)
            self.assertTrue(result['live'], result)
            self.assertGreater(result['samples'], 0)
            def absent(argv, **kwargs):
                fake_stream(Path(argv[argv.index('--out')+1]), status='absent')
                return subprocess.CompletedProcess(argv, 0, b'', b'')
            self.assertFalse(session._probe_meter_live(tmp, runner=absent)['live'])
            self.assertFalse(session._probe_meter_live(tmp, runner=lambda argv, **k: subprocess.CompletedProcess(argv, 2, b'', b''))['live'])


if __name__ == '__main__':
    unittest.main()
