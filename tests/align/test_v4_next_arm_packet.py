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
import time
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
                 b_bar=True, provisional=False, previous_final=False):
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
            'pilot': {'plan_id': plan_id, 'status': 'instrument_ok', 'checks': {'synthetic_check': True}, 'extra_checks': {
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
        if window not in ('W1', 'R1'):
            # The desk's committed provisional counts: a permissive upper bound by default (7 per pair).
            self.sources['pilot']['extra_checks']['series_desk_row'] = {
                'window_id': window.split('#')[0], 'status': 'provisional', 'flags': [],
                'captured_members': 0, 'desk_eligible_benign': dict.fromkeys(cad.CAL_PAIRS, 7)}
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
        self.provisional, self.previous_final = provisional, previous_final
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
        if self.provisional:
            # R17: committed before the Air full desk finished; the light triage stands in.
            self.final_sources = {k: copy.deepcopy(self.sources[k]) for k in builder.FINAL_SOURCES}
            light_thermal = copy.deepcopy(self.thermal)
            for m in light_thermal['members']:
                m['excluded'] = bool(m['calibration_exclusions'])
            self.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': self.window,
                'thermal': light_thermal, 'checks': {'v4_B_bar': self.sources['desk']['checks']['v4_B_bar']},
                'km003c': self.sources['pilot']['extra_checks']['km003c'],
                'series_desk_row': self.sources['pilot']['extra_checks'].get('series_desk_row')}
            self.sources['desk'] = {'plan_id': self.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
            self.omit_sources.update(('pilot', 'exclusions'))
        if self.previous_final:
            prior = self.previous
            self.record['previous_final'] = {'record_sha256': prior.link['sha256'], 'sources': {
                k: self.write(f'{d}/previous-final/{k}.json', v) for k, v in prior.final_sources.items()}}
        self.record['sources'] = {k: self.write(f'{d}/evidence/{k}.json', v)
                                  for k, v in self.sources.items() if k not in self.omit_sources}
        pairs = [m['run_id'] for m in self.members]
        self.record['captures'] = {i: None if i in self.absent_captures else (
            {'locator': '/DO-NOT-FOLLOW/' + i, 'sha256': builder.digest(b'synthetic'), 'bytes': 9}
            if self.raw_custody else self.write(f'{d}/captures/{i}.jsonl', b'{"monotonic_ns":1,"power_w":1}\n'))
            for i in pairs}
        self.record['raw_evidence'] = [self.write(f'{d}/raw/sidecar.jsonl', b'{"temperature_c":30}\n')]
        if self.window != 'R1' and not getattr(self, 'omit_finalized_manifest', False):
            # R17 review F2: the record binds the finalized (record-bound) tree manifest, canonical bytes.
            finalized = {'schema': builder.FINALIZED_MANIFEST_SCHEMA, 'source_root': '/DO-NOT-FOLLOW/session-' + d,
                         'entries': {'raw/sidecar.jsonl': {'sha256': 'f' * 64, 'size': 21}},
                         'closure': {'links': {}, 'files': {}, 'inputs': [], 'mirror': None}}
            self.record['finalized_manifest'] = self.write(
                f'{d}/evidence/finalized_manifest.json',
                json.dumps(finalized, sort_keys=True, separators=(',', ':')).encode())
        if self.raw_custody:
            self.record['raw_evidence'].extend(self.record['captures'].values())
        self.record_path = f'{d}/record.json'
        index = self.write(self.record_path, self.record)
        self.record_commit = self.commit()
        self.git('update-ref', 'refs/remotes/synthetic/records', self.record_commit)
        self.link = {'commit': self.record_commit, 'path': self.record_path, 'sha256': index['sha256']}
        self.series['last_passed_record'] = dict(self.link)
        if self.provisional:
            # Its desk has not passed yet: the last desk-passed state is the previous record's.
            prior = self.previous
            self.series['last_passed_record'] = dict(prior.passed_ref)
        self.passed_ref = dict(self.series['last_passed_record'])
        if self.previous_final:
            # The previous window's desk passed off the MBP and rides in this record.
            self.previous.passed_ref = {**self.previous.link, 'final_record': dict(self.link)}
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

    def test_a_zero_capture_retry_that_is_also_zero_bars_the_slot_and_a_replacement_is_owed(self):
        # R22-2: a zero-capture refusal beyond the retry is a STRUCTURAL bar: the slot is replaced (C9), not
        # escalated, and nothing depends on scores or counts.
        s = self.calibration_series([('C1', False, True), ('C1#2', False, True)])
        packet = s.build()
        decision = packet['calibration_decision']
        self.assertEqual(decision['decision'], 'continue')
        self.assertEqual((decision['barred_windows'], decision['replacements_used']), (['C1#2'], 1))
        self.assertEqual(decision['attempted'], 0)
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])

    def test_a_seventh_zero_capture_bar_escalates_until_a_ruling_with_a_committed_text(self):
        # R24: six replacement windows (C9-C14) absorb six bars; the seventh escalates
        spec = [(f'C{n}{suffix}', False, True) for n in range(1, 8) for suffix in ('', '#2')]
        s = self.calibration_series(spec)
        packet = s.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertEqual(packet['calibration_decision']['decision'], 'escalate_to_lead')
        text = b'LEAD RULING SYNTHETIC-1: seven zero-capture bars, all six replacement windows exhausted\n'
        ref = s.write(f'{s.dir}/rulings/synthetic-1.txt', text)
        s.series['lead_rulings'] = [{'ruling_id': 'SYNTHETIC-1', 'after_window': 'C7#2', 'text': ref,
                                     'lead_signature': 'lead: synthetic-ruling 2026-11-08'}]
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertEqual(packet['lead_rulings'], [{
            'ruling_id': 'SYNTHETIC-1', 'text_sha256': hashlib.sha256(text).hexdigest(),
            'resets': 'zero_capture_escalation', 'after_window': 'C7#2',
            'lead_signature': 'lead: synthetic-ruling 2026-11-08'}])        # the digest is computed, not entered
        # the ruling resets the trailing refusal count but cannot repair calibration: 8 counted windows are
        # out of reach once more than two windows are barred
        self.assertEqual(packet['calibration_decision']['decision'], 'insufficient_calibration')
        self.assertEqual(packet['calibration_decision']['zero_capture_refusals'], 14)
        self.assertFalse(packet['packet_preflight']['ready'])
        for bad in ({'ruling_id': 'X', 'after_window': 'C9', 'text': ref, 'lead_signature': 'lead: s 2026-11-08'},
                    {'ruling_id': 'X', 'after_window': 'C7#2', 'text': {**ref, 'sha256': '0'*64},
                     'lead_signature': 'lead: s 2026-11-08'},
                    {'ruling_id': 'X', 'after_window': 'C7#2', 'text': ref, 'lead_signature': 'PENDING'},
                    {'ruling_id': 'X', 'after_window': 'C7#2', 'text': ref}):
            s.series['lead_rulings'] = [bad]
            s.write(s.series_path, s.series)
            s.series_commit = s.commit()
            with self.subTest(bad=str(bad)[:60]):
                self.assertFalse(s.build()['packet_preflight']['ready'])


class SentinelTriggerTests(Base):
    """A15 / R21: the R20 escalation sentinels trigger on a U4 inconclusive only; U5 never does."""

    def roster_check(self, u4, u5):
        s = self.calibration_series([('C1', True, True)])
        s.next_plan['members'] = s.next_plan['members'][:2]                   # the ordinary two sentinels only
        s.series['sentinel_ids'] = s.series['sentinel_ids'][:2]
        s.thermal['model_windows']['tiny/C1']['U4']['status'] = u4
        s.thermal['model_windows']['tiny/C1']['U5']['status'] = u5
        s.finish()
        return s.build()['checks']['sentinel_roster']

    def test_a_u5_inconclusive_alone_does_not_require_the_escalation_sentinels(self):
        self.assertEqual(self.roster_check('pass', 'inconclusive')['status'], 'pass')
        self.assertEqual(self.roster_check('pass', 'pass')['status'], 'pass')

    def test_a_u4_inconclusive_requires_them(self):
        check = self.roster_check('inconclusive', 'pass')
        self.assertEqual(check['status'], 'fail')
        self.assertIn('two extra sentinels after a U4 inconclusive', check['basis'])
        self.assertEqual(self.roster_check('inconclusive', 'inconclusive')['status'], 'fail')

    def test_the_desk_consequence_adds_sentinels_for_u4_only(self):
        from joulewise.align.apple import thermal_desk
        from tests.align.test_thermal_desk import member
        rows = []
        for ordinal in (5, 22):
            row = member(str(ordinal))
            row.update(window='C1', role='D', u3_configuration_sha256='a' * 64)
            rows.append(row)
        for key, cross, expected in (
                ('u4', {'synthetic': {'sentinels': {'status': 'inconclusive'}}}, 'add 2 sentinels per remaining window'),
                ('u5', {'synthetic': {'sentinels': {'status': 'pass', 'W': 8, 'df': 7}}}, None)):
            report = thermal_desk.window_report(rows, v4=True, cross_windows=cross,
                                                sensitivity={'synthetic': {'status': 'inconclusive'}} if key == 'u5' else None)
            consequence = next(iter(report['model_windows'].values()))['consequence']
            if key == 'u4':
                self.assertEqual(consequence, expected)
            else:
                self.assertNotEqual(consequence, 'add 2 sentinels per remaining window')


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

    def test_the_meter_probe_ends_before_the_quiet_dwell_starts_and_never_during_it(self):
        # Lead ruling 2026-11-08: the 3 s monitor launch is USB and process activity; it runs before the
        # quiet/display dwell starts. The arm stamps both on one monotonic clock and records the order.
        s = self.scenario().finish()
        record = self.arm(s, s.build())
        self.assertTrue(record['admitted'], record['reasons'])
        dwell = record['quiet_dwell']
        self.assertTrue(dwell['meter_probe_before_dwell'])
        evidence = record['next_arm_triage']['meter_live_evidence']
        self.assertLess(evidence['probe_started_ns'], evidence['probe_ended_ns'])
        self.assertLess(evidence['probe_ended_ns'], dwell['start_ns'])
        self.assertEqual(dwell['meter_probe_ended_ns'], evidence['probe_ended_ns'])
        # a dwell that started at or before the probe's end refuses the arm, whatever the meter says
        for label, start in (('dwell already running', lambda: 1), ('dwell starts as the probe ends', None)):
            with self.subTest(label=label):
                kwargs = {'dwell_start': start} if start else {
                    'meter_probe': lambda root: {'live': True, 'probe_ended_ns': 10**15},
                    'dwell_start': lambda: 10**15}
                refused = self.arm(s, s.build(), **kwargs)
                self.assertFalse(refused['admitted'])
                self.assertFalse(refused['quiet_dwell']['meter_probe_before_dwell'])
                self.assertTrue(any('meter probe did not end before the quiet dwell' in r for r in refused['reasons']))
        # a probe that reports a non-integer end (or none that the arm can order) cannot satisfy the ordering
        bad = self.arm(s, s.build(), meter_probe=lambda root: {'live': True, 'probe_ended_ns': 'later'})
        self.assertFalse(bad['admitted'])

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


class ArmOrderWitness(Base):
    """Lead ruling on R17 review open item 5: the full order of one real arm through _arm_and_install.

    Every subprocess, file write and disk_usage of the arm precedes the dwell stamp. After it come
    only the single dwell-record write (the stamp value) and the installer handoff. Recorded with a
    Python audit hook (subprocess.Popen, open-for-write, os.rename/replace/remove/mkdir) plus the
    host-observation seams, which stand for subprocesses on the MBP.
    """

    def test_every_subprocess_write_and_disk_usage_precedes_the_dwell_stamp(self):
        import shutil
        import sys
        from scripts import align_v4_session as session, align_v4_kit as kit
        from tests.align.test_v4_cadence import write_battery_log
        from scripts import align_v4_series as series
        s = self.scenario()
        s.write(series.MANIFEST.as_posix(), series.raw_json(series.candidate()))   # W1 -> C1 binds the frozen series
        s.finish()
        packet = s.build()
        target = Path(tempfile.mkdtemp(dir=s.root.parent)) / 'session'
        target.mkdir()
        log = write_battery_log(target.parent / 'battery.jsonl', NOW)
        events, state = [], {'on': False}
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC

        def hook(event, args):
            if not state['on']:
                return
            if event == 'subprocess.Popen':
                events.append(('subprocess', ' '.join(map(str, args[1] or [args[0]]))[:60]))
            elif event == 'open' and len(args) >= 3:
                mode, flags = args[1], args[2]
                if (isinstance(mode, str) and any(c in mode for c in 'wxa+')) or (
                        mode is None and isinstance(flags, int) and flags & write_flags):
                    events.append(('write', str(args[0])))
            elif event in ('os.rename', 'os.replace', 'os.remove', 'os.mkdir', 'shutil.copyfile'):
                events.append(('write', f'{event}:{args[0]}'))
        sys.addaudithook(hook)
        real_usage = shutil.disk_usage

        def usage(path):
            events.append(('disk_usage', str(path)))
            return real_usage(path)

        def seam(name, value):
            def call(*_args, **_kwargs):
                events.append(('subprocess', 'seam:' + name))
                return value
            return call

        def disk_gate(config, gate=None):
            Path(log).read_bytes()                       # the gate's reads
            shutil.disk_usage(target)
            return {'status': 'pass'}

        def stamp():
            events.append(('DWELL', 'stamp'))
            return time.monotonic_ns()
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        arm_state = {'v4_series': {'window_id': 'C1'}, 'source_measurement_root': str(s.root)}
        with patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(target.parent / 'host')}), \
             patch('joulewise.align.apple.powermode.admit_ac_powermode',
                   side_effect=seam('powermode', {'admitted': True, 'observed': 0})), \
             patch('joulewise.align.apple.external_volume.census', side_effect=seam('volumes', {})), \
             patch('joulewise.align.apple.external_volume.arm_check',
                   return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', side_effect=seam('battery', (good, b'synthetic'))), \
             patch.object(kit, 'arm_powermode_check', side_effect=seam('powermode_check', None)), \
             patch.object(session, 'w1_disk_check', side_effect=disk_gate), \
             patch('shutil.disk_usage', side_effect=usage), \
             patch.object(session.pilot, 'install', side_effect=seam('INSTALL', {'synthetic': True})):
            state['on'] = True
            try:
                session._arm_and_install(target, arm_state, s.root, s.next_plan, None,
                    runner=lambda argv: subprocess.CompletedProcess(argv, 0, '', ''), volume_runner=None,
                    now=lambda: NOW, w1_disk_config=None, disk_gate=None, battery_log=log,
                    obc_off_attested_by='synthetic', next_arm_triage=packet,
                    meter_probe=seam('meter_probe', {'live': True, 'samples': 40}), dwell_start=stamp)
            finally:
                state['on'] = False
        kinds = [kind for kind, _ in events]
        self.assertEqual(kinds.count('DWELL'), 1, events)
        cut = kinds.index('DWELL')
        before, after = events[:cut], events[cut + 1:]
        dwell_record = str(target / 'staging/v4-arm-001.dwell.json')
        # After the stamp: exactly the one dwell-record write, then the installer handoff; after the
        # installer returns, only that same dwell record is rewritten with installer_end_ns (lead ruling).
        def dwell_write(event):
            return event[0] == 'write' and dwell_record in event[1]
        install = after.index(('subprocess', 'seam:INSTALL'))
        self.assertEqual(after[:install], [('write', dwell_record)], after)
        self.assertTrue(after[install + 1:] and all(dwell_write(e) for e in after[install + 1:]), after)
        # Before it: the Git work, every host seam, the disk gate's disk_usage and every record write.
        self.assertTrue(any(k == 'subprocess' and 'git' in v for k, v in before), before)
        for name in ('powermode', 'volumes', 'battery', 'meter_probe', 'powermode_check'):
            self.assertIn(('subprocess', 'seam:' + name), before)
        self.assertIn(('disk_usage', str(target)), before)
        written = {v for k, v in before if k == 'write'}
        for name in ('staging/v4-arm-001.json', 'session.json', 'staging/w1_disk_gate.json'):
            # pilot.h.write publishes through a hidden temporary and a rename
            self.assertTrue(any(name.rsplit('/', 1)[-1] in v for v in written), (name, sorted(written)))
        dwell = json.loads(Path(dwell_record).read_bytes())
        self.assertTrue(dwell['admitted'])
        self.assertTrue(dwell['quiet_dwell']['meter_probe_before_dwell'])
        self.assertTrue(dwell['quiet_dwell']['record_checks_and_writes_before_dwell'])
        self.assertEqual(dwell['quiet_dwell']['installer_outcome'], 'returned')
        self.assertGreater(dwell['quiet_dwell']['installer_end_ns'], dwell['quiet_dwell']['start_ns'])
        record = json.loads((target / 'staging/v4-arm-001.json').read_bytes())
        self.assertIsNone(record['quiet_dwell']['start_ns'])
        self.assertEqual(record['quiet_dwell']['dwell_record'], dwell_record)


class R17ProvisionalTests(Base):
    """RUN_STATE 228 R17: provisional eligibility at the arm; window k final before the arm of k+2."""

    def series_of(self, specs):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17-')
        self.addCleanup(temp.cleanup)
        previous = Scenario(temp.name, 'W1').finish()
        for window, kwargs in specs:
            previous = Scenario(temp.name, window, previous=previous, **kwargs).finish()
        return previous

    def test_previous_window_arms_on_the_light_triage(self):
        s = self.series_of([('C1', {}), ('C2', {'provisional': True})])
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'provisional'])
        self.assertIn('R17 provisional', packet['checks']['member_eligibility']['basis'])
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'deferred')
        self.assertTrue(evaluate(s, packet)['admitted'])

    def test_window_k_must_be_final_before_the_arm_of_k_plus_2(self):
        stale = self.series_of([('C1', {'provisional': True}), ('C2', {})])
        packet = stale.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        bound = self.series_of([('C1', {'provisional': True}), ('C2', {'previous_final': True})])
        packet = bound.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'final'])

    def test_final_counts_come_from_the_successor_and_may_only_be_lower(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17b-')
        self.addCleanup(temp.cleanup)
        w1 = Scenario(temp.name, 'W1').finish()
        c1 = Scenario(temp.name, 'C1', previous=w1, provisional=True)
        c1.sources['exclusions']['members_excluded'] = [{'run_id': c1.members[0]['run_id'], 'codes': ['clock.step']}]
        c1.thermal['members'][0]['excluded'] = True          # the harvest excluded one member
        c1.finish()
        c2 = Scenario(temp.name, 'C2', previous=c1, previous_final=True).finish()
        rows = c2.build()['calibration_windows']
        self.assertEqual(rows[0]['status'], 'final')
        self.assertEqual(sum(rows[0]['eligible_benign'].values()), 1)
        self.assertEqual(sum(c1.build()['calibration_windows'][0]['eligible_benign'].values()), 2)  # provisional

    def test_full_desk_due_refuses_the_provisional_adjudication(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17d-')
        self.addCleanup(temp.cleanup)
        w1 = Scenario(temp.name, 'W1').finish()
        w1.passed_ref = dict(w1.link)
        c1 = Scenario(temp.name, 'C1', previous=w1, provisional=True).finish()
        changed = c1.build(current='f' * 64)          # code/config moved since the last desk pass
        self.assertFalse(changed['packet_preflight']['ready'])
        self.assertIn('member_eligibility', ' '.join(changed['packet_preflight']['reasons']))
        provisional_w1 = Scenario(tempfile.mkdtemp(prefix='jw-triage-r17w-', dir=temp.name), 'W1')
        provisional_w1.provisional = True
        provisional_w1.previous = w1                  # only for its passed_ref; W1 always needs the full desk
        packet = provisional_w1.finish().build()
        self.assertFalse(packet['packet_preflight']['ready'])

    def test_previous_final_must_name_the_record_it_finalizes(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17e-')
        self.addCleanup(temp.cleanup)
        w1 = Scenario(temp.name, 'W1').finish()
        c1 = Scenario(temp.name, 'C1', previous=w1, provisional=True).finish()
        c2 = Scenario(temp.name, 'C2', previous=c1, previous_final=True).finish()
        record = copy.deepcopy(c2.record)
        record['previous_final']['record_sha256'] = '0' * 64
        index = c2.write(c2.record_path, record)
        c2.record_commit = c2.commit()
        c2.git('update-ref', 'refs/remotes/synthetic/records', c2.record_commit)
        c2.series['previous_record'] = {'commit': c2.record_commit, 'path': c2.record_path, 'sha256': index['sha256']}
        c2.write(c2.series_path, c2.series)
        c2.series_commit = c2.commit()
        packet = c2.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('previous_final must name this record', packet['calibration_error'])

    def test_schema_constants_match_the_light_triage_module(self):
        from joulewise.align.apple import light_triage
        self.assertEqual(builder.LIGHT_TRIAGE_SCHEMA, light_triage.SCHEMA)


class R17ReviewFinalityTests(Base):
    """R17 review (Sol seats 1 and 2): what counts as final, and the record-bound manifest."""

    def root(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17r-')
        self.addCleanup(temp.cleanup)
        return temp.name

    def test_constants_match_the_runner_and_the_offload_module(self):
        from joulewise.align.apple import harvest_offload
        from scripts import align_v4_harvest_off as runner
        self.assertEqual(builder.COMPLETED_HARVEST, runner.COMPLETED_HARVEST)
        self.assertEqual(builder.FINALIZED_MANIFEST_SCHEMA, harvest_offload.FINALIZED_SCHEMA)

    def light_with_stale_final_sources(self, root, w1):
        # F4: PILOT/exclusions present, desk still running off the MBP, honest light triage.
        c1 = Scenario(root, 'C1', previous=w1)
        light = copy.deepcopy(c1.thermal)
        for m in light['members']:
            m['excluded'] = bool(m['calibration_exclusions'])
        c1.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': 'C1', 'thermal': light,
            'checks': {'v4_B_bar': True}, 'km003c': c1.sources['pilot']['extra_checks']['km003c'],
            'series_desk_row': c1.sources['pilot']['extra_checks']['series_desk_row']}
        c1.sources['desk'] = {'plan_id': c1.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
        c1.finish()
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.passed_ref = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        return c1

    def test_stale_final_sources_with_a_running_desk_are_provisional_not_final(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = self.light_with_stale_final_sources(root, w1)
        first = c1.build()
        self.assertEqual(first['calibration_windows'][-1]['status'], 'provisional')
        self.assertTrue(evaluate(c1, first)['admitted'])          # the one allowed unfinished window
        c2 = Scenario(root, 'C2', previous=c1).finish()
        packet = c2.build()
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        self.assertIn('no completed harvest', packet['calibration_error'])
        self.assertFalse(evaluate(c2, packet)['admitted'])

    def test_a_completed_non_passing_desk_is_final(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = Scenario(root, 'C1', previous=w1)
        c1.sources['pilot']['status'] = 'instrument_incomplete'
        c1.sources['desk'].update(pilot_status='instrument_incomplete', checks={'synthetic_check': False})
        c1.finish()
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        c2 = Scenario(root, 'C2', previous=c1).finish()
        packet = c2.build()
        self.assertNotIn('calibration_error', packet)
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'final'])

    def test_a_zero_capture_attempt_needs_no_harvest_to_be_final(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = Scenario(root, 'C1', previous=w1, captured=False)
        c1.sources['desk']['harvest_status'] = 'not_run'        # nothing was captured, so nothing harvested
        c1.finish()
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        c2 = Scenario(root, 'C1#2', previous=c1).finish()
        packet = c2.build()
        self.assertNotIn('calibration_error', packet)
        self.assertNotEqual(packet['checks']['member_eligibility']['status'], 'fail')
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'final'])

    def test_previous_final_sources_must_evidence_a_completed_plan_bound_harvest(self):
        for label, change in (('running desk', lambda c: c.final_sources.__setitem__(
                                   'desk', {'plan_id': c.sources['plan']['plan_id'], 'status': 'running_off_mbp'})),
                              ('program fault', lambda c: c.final_sources['desk'].update(harvest_status='program_fault')),
                              ('other plan', lambda c: c.final_sources['desk'].update(plan_id='synthetic-other')),
                              ('other pilot', lambda c: c.final_sources['pilot'].update(plan_id='synthetic-other'))):
            with self.subTest(label):
                root = self.root()
                w1 = Scenario(root, 'W1').finish()
                c1 = Scenario(root, 'C1', previous=w1, provisional=True).finish()
                change(c1)
                c2 = Scenario(root, 'C2', previous=c1, previous_final=True).finish()
                packet = c2.build()
                self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
                self.assertFalse(evaluate(c2, packet)['admitted'])

    def test_record_must_bind_a_canonical_finalized_manifest(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = Scenario(root, 'C1', previous=w1)
        c1.omit_finalized_manifest = True
        c1.finish()
        with self.assertRaisesRegex(ValueError, 'must bind the finalized tree manifest'):
            c1.build()
        c1b = Scenario(self.root(), 'W1')
        c1b.omit_finalized_manifest = True
        c1b.record['finalized_manifest'] = c1b.write('w-W1/evidence/finalized_manifest.json', {
            'schema': builder.FINALIZED_MANIFEST_SCHEMA, 'source_root': '/x', 'entries': {}, 'closure': {}})
        c1b.finish()
        with self.assertRaisesRegex(ValueError, 'not a canonical'):
            c1b.build()


if __name__ == '__main__':
    unittest.main()
