"""R11 delta6 Sol2: ruling witnesses, synthetic records only.

Contract assertions for F1-F4 are intentionally red at c742e5722. No native
commands, model weights, measurement data, network, or custody discovery.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk, v4_balance, v4_cadence, v4_contention
from scripts import align_pilot_session as pilot
from scripts import align_v4_next_arm_packet as builder
from scripts import align_v4_series as series
from scripts import align_v4_session as session
from scripts import align_v4_u3_export as u3_export
from tests.align.test_thermal_desk import member
from tests.align.test_v4_next_arm_packet import Scenario
from tests.align.v4_registration_fixtures import signed_bar

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SHA256 = '21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c'


def setUpModule():
    git_environment = patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': '/dev/null',
                                             'GIT_CONFIG_NOSYSTEM': '1', 'GIT_NO_LAZY_FETCH': '1'})
    git_environment.start()
    unittest.addModuleCleanup(git_environment.stop)


def calibration_row(name, *, count=7, bar=None):
    row = {'window': name, 'status': 'final', 'captured_members': 22,
           'eligible_benign': dict.fromkeys(v4_cadence.CAL_PAIRS, count)}
    if bar:
        row.update(barred=bar, eligible_benign=dict.fromkeys(v4_cadence.CAL_PAIRS, 0))
    return row


class ContentionWitnesses(unittest.TestCase):
    def common_member(self, code=None):
        return {'run_id': 'benign', 'task_pair': 'spam', 'condition': 'benign',
                'excluded': bool(code), 'exclusion_codes': [code] if code else [],
                'summary': {'energy': {'gpu': {'joules': 1., 'segment_sum_j': 1.}},
                            'flags': [], 'configuration': {'sampler': {}},
                            'window_evidence_precheck': {'eligible': True}}}

    def checks(self, row):
        checks, _, _ = pilot.instrument_checks([row])
        # The native common desk replaces this diagnostic with sampled I4'.
        checks.pop('I4_greedy_repeats_identical_tokens')
        return checks

    def test_f1_contention_only_common_desk_member_must_not_fail_full_desk(self):
        clean = self.common_member()
        self.assertTrue(session.full_desk_gate_pass(self.checks(clean), [clean]))
        for code in ('contention.request_overlap', 'contention.unmeasured'):
            with self.subTest(code=code):
                common = self.common_member(code)
                thermal = {'calibration_exclusions': [code], 'flags': []}
                # Exactly the new v4 hook's separate thermal-record normalization.
                with patch.object(v4_contention, 'bundle_disclosure', return_value={'flags': []}):
                    v4_contention.attach(thermal, Path('synthetic-unused'), ([], None, 0))
                self.assertFalse(thermal['excluded'])
                self.assertTrue(session.full_desk_gate_pass(self.checks(common), [common]),
                                'R22-1: the common desk still gates on a contention-only exclusion')

    def test_f4_balance_must_include_contention_events_moved_to_disclosure(self):
        record = {'id': 'benign', 'condition': 'benign', 'task_pair': 'spam',
                  'gross_latency_s': 100., 'flags': [],
                  'calibration_exclusions': ['contention.request_overlap']}
        with patch.object(v4_contention, 'bundle_disclosure', return_value={'flags': []}):
            v4_contention.attach(record, Path('synthetic-unused'), ([], None, 0))
        self.assertEqual(record['contention']['disclosed_codes'], ['contention.request_overlap'])
        self.assertFalse(record['excluded'])
        report = v4_balance.balance_check([record])
        self.assertEqual(report['by_condition']['benign']['events'], 1,
                         'R22-3: moving a contention event to disclosure must not erase it from balance')

    def test_other_exclusions_still_fail_the_full_desk(self):
        common = self.common_member('thermal.state_unobserved')
        self.assertFalse(session.full_desk_gate_pass(self.checks(common), [common]))


class ReserveU3Witnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bar = signed_bar()
        # The synthetic adopted bar uses the production policy-template roster.
        assert cls.bar['policy']['checks_by_window'] == u3_export.policy_template()['checks_by_window']

    def report(self, window):
        rows = [member('early', energy=30000.), member('late', energy=30000.)]
        for row in rows:
            row.update(role='D', window=window, identical_work_group='replay',
                       u3_configuration_sha256='b' * 64)
        return thermal_desk.window_report(rows, v4=True, u3_bar=self.bar)['model_windows'][f'synthetic/{window}']

    def test_f2_all_armable_reserve_windows_need_usable_u3_scope(self):
        self.assertEqual(self.report('C8')['U3']['status'], 'pass')
        for n in range(9, 15):
            with self.subTest(window=f'C{n}'):
                result = self.report(f'C{n}')
                self.assertEqual(result['U1']['status'], 'pass')
                self.assertEqual(result['U2']['status'], 'pass')
                self.assertEqual(result['U3']['status'], 'pass',
                                 'R24: a healthy reserve replay is outside the production U3 roster')

    def test_u5_inconclusive_does_not_request_more_sentinels(self):
        rows = [member('early'), member('late')]
        report = thermal_desk.acceptance(rows, pairs=[tuple(rows)], v4=True, u3_bar=self.bar,
                                        u4={'sentinels': {'status': 'pass'}},
                                        u5={'status': 'inconclusive'}, u6={'status': 'pass'})
        self.assertEqual(report['U5']['status'], 'inconclusive')
        self.assertNotEqual(report['consequence'], 'add 2 sentinels per remaining window')
        u4 = thermal_desk.acceptance(rows, pairs=[tuple(rows)], v4=True, u3_bar=self.bar,
                                     u4={'sentinels': {'status': 'inconclusive'}},
                                     u5={'status': 'pass'}, u6={'status': 'pass'})
        self.assertEqual(u4['consequence'], 'add 2 sentinels per remaining window')


class CommittedBarWitnesses(unittest.TestCase):
    def calibration(self, *, failed=False, pool=False):
        temp = tempfile.TemporaryDirectory(prefix='jw-delta6-sol2-')
        self.addCleanup(temp.cleanup)
        first = Scenario(temp.name, 'W1').finish()
        current = Scenario(temp.name, 'C1', previous=first)
        current.write(series.MANIFEST.as_posix(), series.raw_json(series.candidate()))
        current.next_plan['window'] = 'C2'
        for row in current.members:
            row['pool_role'] = 'calibration'
        if failed:
            current.sources['result']['verdict'] = 'CHAIN_STOPPED'
            current.sources['result']['chain_exit_code'] = 1
            current.sources['chain_exited']['exit_code'] = 1
        if pool:
            current.series['pool_members'] = [current.members[0]['run_id']]
        return current.finish()

    def test_f3_terminal_bar_must_also_refuse_partial_pool_entry(self):
        s = self.calibration(failed=True, pool=True)
        packet = s.build()
        row = packet['calibration_windows'][0]
        self.assertEqual(row['barred'], 'whole_window_capture_failure')
        self.assertEqual(row['eligible_benign'], {'spam': 0, 'bank': 0})
        self.assertEqual(packet['calibration_decision']['attempted'], 0)
        # (The seat's present-behavior assertions, preflight ready and a successful series bind, described the
        # defect and contradict the requirement; with the shared bar predicate the packet is refused.)
        self.assertEqual(packet['checks']['cohort_pool_rules']['status'], 'fail',
                         'R22-2: a barred terminal window still receives a passing nonempty pool check')
        self.assertIn('structurally barred window enters no pool', packet['checks']['cohort_pool_rules']['basis'])
        self.assertFalse(packet['packet_preflight']['ready'], packet['packet_preflight'])

    def test_empty_pool_after_terminal_bar_can_continue_to_the_next_primary(self):
        s = self.calibration(failed=True)
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['calibration_decision']['decision'], 'continue')
        series.bind_packet(s.root, 'C2', packet, authenticated_by_rebuild=True)

    def test_scores_and_counts_do_not_create_structural_bars(self):
        s = self.calibration()
        evidence = builder.GitEvidence(s.root)
        record = builder.WindowRecord(evidence, s.record_commit, s.record_path)
        original = record.source

        def source(name, **kwargs):
            result = deepcopy(original(name, **kwargs))
            if name == 'result':
                result.update(score=1e9, alarm=True, eligible_benign={'spam': 0, 'bank': 0})
            return result

        with patch.object(record, 'source', side_effect=source):
            self.assertIsNone(record.structural_bar(1))
            self.assertIsNone(record.structural_bar(22))


class FrozenAllocationAndStopTests(unittest.TestCase):
    def test_frozen_hash_base_windows_and_reserve_indices(self):
        raw = (ROOT / series.MANIFEST).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), MANIFEST_SHA256)
        manifest = series.load(ROOT)
        self.assertEqual(raw, series.raw_json(series.candidate()))
        old = subprocess.run(['git', 'show', '356c41c82:' + series.MANIFEST.as_posix()],
                             cwd=ROOT, check=True, capture_output=True).stdout
        import json
        current = {w['id']: w for w in manifest['windows']}
        for window in json.loads(old)['windows']:
            self.assertEqual(current[window['id']], window, window['id'])
        for n in range(9, 15):
            low = 100 + 8 * (n - 9)
            for pair in series.PAIRS:
                self.assertEqual([m['seed_index'] for m in current[f'C{n}']['members']
                                  if 6 <= m['ordinal'] <= 21 and m['pair'] == pair],
                                 list(range(low, low + 8)))

    def test_low_m_never_arms_a_reserve_and_seventh_bar_cannot_complete(self):
        rows = [calibration_row(f'C{i}', count=4) for i in range(1, 9)]
        result = v4_cadence.calibration_stop(rows)
        self.assertEqual((result['decision'], result['replacements_used']), ('insufficient_calibration', 0))
        history = [{'window_id': r['window'], 'attempt_id': r['window'], **r} for r in rows]
        with self.assertRaisesRegex(ValueError, 'skips/reorders'):
            series.calibration_rows(series.candidate(), [*history,
                {'window_id': 'C9', 'attempt_id': 'C9', **calibration_row('C9')}])
        seven = [calibration_row(f'C{i}', bar='u1_u3_fail') for i in range(1, 8)]
        self.assertEqual(v4_cadence.calibration_stop(seven)['decision'], 'insufficient_calibration')
        zeros = [{'window': f'C{i}{suffix}', 'status': 'final', 'captured_members': 0,
                  'eligible_benign': {'spam': 0, 'bank': 0}}
                 for i in range(1, 8) for suffix in ('', '#2')]
        self.assertEqual(v4_cadence.calibration_stop(zeros)['decision'], 'escalate_to_lead')

    def test_six_bars_require_reserves_in_order_and_exactly_eight_admitted(self):
        rows = [calibration_row(f'C{i}', bar='u1_u3_fail' if i <= 6 else None)
                for i in range(1, 9)]
        history = [{'window_id': r['window'], 'attempt_id': r['window'], **r} for r in rows]
        for n in range(9, 15):
            _, next_id, _, _ = series.calibration_rows(series.candidate(), history)
            self.assertEqual(next_id, f'C{n}')
            row = calibration_row(f'C{n}')
            rows.append(row)
            history.append({'window_id': row['window'], 'attempt_id': row['window'], **row})
        result = v4_cadence.calibration_stop(rows)
        self.assertEqual((result['decision'], result['attempted'], result['replacements_used']),
                         ('calibration_complete', 8, 6))
        self.assertEqual(series.calibration_rows(series.candidate(), history)[1], 'T1')


if __name__ == '__main__':
    unittest.main()
