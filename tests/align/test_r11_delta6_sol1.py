"""Independent delta6 review witnesses; synthetic records only, no hardware.

The three witnesses for the two sites of F1 and for F2 were expected failures on the reviewed head; the
decorators are removed now that the fixes are applied (see the note inside the committed-harvest witness).
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk, v4_balance, v4_cadence as cad, v4_contention
from scripts import align_pilot_session as pilot, align_v4_next_arm_packet as builder
from scripts import align_v4_series as series, align_v4_session as session
from tests.align.test_thermal_desk import member
from tests.align.test_v4_next_arm_packet import Scenario

ROOT = Path(__file__).resolve().parents[2]
# RUN_STATE 251 option B regenerated the R24 bytes (21313cc2...): seeded sabotage ordinals, test reserves T4-T5.
from tests.align.v4_option_b import OPTION_B_MANIFEST_SHA256 as MANIFEST_SHA, assert_seed_preserved


def ledger_row(n, *, bar=None, eligible=7):
    return dict(window_id=f'C{n}', attempt_id=f'C{n}', status='final', captured_members=22,
                eligible_benign=dict.fromkeys(cad.CAL_PAIRS, 0 if bar else eligible),
                **({'barred': bar} if bar else {}))


def common_member():
    return {'run_id': 'synthetic', 'task_pair': 'spam', 'condition': 'benign',
            'excluded': False, 'exclusion_codes': [],
            'summary': {'energy': {'gpu': {'joules': 1., 'segment_sum_j': 1.}},
                        'flags': [], 'configuration': {'sampler': {}},
                        'window_evidence_precheck': {'eligible': True}}}


class Delta6Witnesses(unittest.TestCase):
    def scenario(self, window='W1'):
        temp = tempfile.TemporaryDirectory(prefix='jw-delta6-sol1-')
        self.addCleanup(temp.cleanup)
        previous = Scenario(temp.name, 'W1').finish() if window != 'W1' else None
        scenario = Scenario(temp.name, window, previous=previous)
        if window != 'W1':
            for row in scenario.members:
                row['pool_role'] = 'calibration'
            scenario.next_plan['window'] = 'C2'
        return scenario

    def test_f1_contention_only_must_not_fail_the_native_full_desk_gate(self):
        control = common_member()
        checks = pilot.instrument_checks([control])[0]
        checks.pop('I4_greedy_repeats_identical_tokens')
        self.assertTrue(session.full_desk_gate_pass(checks, [control]))
        victim = deepcopy(control)
        victim.update(excluded=True, exclusion_codes=['contention.request_overlap'])
        victim['summary'].update(excluded=True, exclusion_codes=['contention.request_overlap'])
        checks = pilot.instrument_checks([victim])[0]
        checks.pop('I4_greedy_repeats_identical_tokens')
        checks['chain_eligibility'] = False  # common desk also applies `and not excluded`
        self.assertFalse(checks['no_member_exclusions'])
        self.assertTrue(session.full_desk_gate_pass(checks, [victim]),
                        'R22-1: a contention-only harvest exclusion still fails the native full desk')

    def test_f1_committed_contention_only_harvest_must_not_reblock_the_arm(self):
        scenario = self.scenario().finish()
        self.assertTrue(scenario.build()['packet_preflight']['ready'])
        victim = scenario.members[0]['run_id']
        scenario.sources['exclusions']['members_excluded'] = [
            {'run_id': victim, 'codes': ['contention.request_overlap']}]
        # The v4 thermal records have already stripped contention successfully.
        scenario.sources['desk'].update(
            harvest_status='members_excluded', pilot_status='instrument_incomplete',
            # delta7: the stale-style desk must record the SAME exclusion as the committed harvest to be reconciled
            members_excluded=[{'run_id': victim, 'codes': ['contention.request_overlap']}],
            full_desk_gate={'pass': False},
            checks={'no_member_exclusions': False, 'chain_eligibility': False, 'v4_B_bar': True})
        scenario.finish()
        packet = scenario.build()
        self.assertEqual(packet['checks']['member_eligibility']['status'], 'pass')
        # (The seat's two present-behavior assertions, full_desk_gate == 'fail' and desk_passes(...) is False,
        # described the defect and contradict the requirement below; they were removed with the decorators.)
        # The builder reconciles a desk that still lists the contention-only member with the committed
        # exclusions: harvest status and the exclusion-derived checks are disclosure-only (R22-1).
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'pass')
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])

    def test_f2_balance_must_include_contention_after_it_becomes_disclosure_only(self):
        row = dict(id='benign', condition='benign', task_pair='spam', gross_latency_s=60.,
                   flags=[], calibration_exclusions=['contention.request_overlap'])
        gap = v4_contention.disclose([], [0, 60 * 10**9])
        with patch.object(v4_contention, 'bundle_disclosure', return_value=gap):
            v4_contention.attach(row, Path('synthetic-unused'), ([], None, 0))
        self.assertFalse(row['excluded'])
        self.assertEqual(row['contention']['disclosed_codes'],
                         ['contention.request_overlap', 'contention.unmeasured'])
        report = v4_balance.balance_check([row])
        self.assertEqual(report['by_condition']['benign']['events'], 2,
                         'R22-3: both disclosed contention events disappear from the balance check')

    def test_manifest_bytes_and_old_windows_are_frozen_and_reserve_seeds_are_contiguous(self):
        raw = (ROOT / series.MANIFEST).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), MANIFEST_SHA)
        self.assertEqual(raw, series.raw_json(series.candidate()))
        old = json.loads(subprocess.check_output(
            ['git', 'show', '356c41c82:' + series.MANIFEST.as_posix()], cwd=ROOT))
        current = {w['id']: w for w in series.load(ROOT)['windows']}
        for window in old['windows']:
            assert_seed_preserved(self, window, current[window['id']])      # option B: seeds kept, placement moved
        for pair in series.PAIRS:
            seeds = [r['seed_index'] for n in range(9, 15)
                     for r in current[f'C{n}']['members'][5:21] if r['pair'] == pair]
            self.assertEqual(seeds, list(range(100, 148)))

    def test_committed_terminal_result_bars_all_partial_captures_even_if_worktree_is_rewritten(self):
        for verdict, exit_code in (('NO_GO', 0), ('GO', 1)):
            with self.subTest(verdict=verdict, exit_code=exit_code):
                scenario = self.scenario('C1')
                scenario.sources['result'].update(verdict=verdict, chain_exit_code=exit_code)
                scenario.sources['chain_exited']['exit_code'] = exit_code
                scenario.finish()
                scenario.sources['result'].update(verdict='GO', chain_exit_code=0)
                scenario.write(f'{scenario.dir}/evidence/result.json', scenario.sources['result'])
                packet = scenario.build()
                self.assertNotIn('calibration_error', packet)
                row = packet['calibration_windows'][0]
                self.assertEqual(row['barred'], 'whole_window_capture_failure')
                self.assertEqual(row['captured_members'], 2)
                self.assertEqual(row['eligible_benign'], dict.fromkeys(cad.CAL_PAIRS, 0))
                self.assertEqual(packet['calibration_decision']['attempted'], 0)

    def test_committed_u_failure_bars_the_entire_window(self):
        scenario = self.scenario('C1')
        scenario.thermal['model_windows']['tiny/C1']['U3']['status'] = 'fail'
        scenario.finish()
        packet = scenario.build()
        self.assertEqual(packet['calibration_windows'][0]['barred'], 'u1_u3_fail')
        self.assertEqual(packet['calibration_decision']['eligible_by_pair'], dict.fromkeys(cad.CAL_PAIRS, 0))

    def test_scores_and_low_counts_never_create_a_bar(self):
        scenario = self.scenario('C1')
        scenario.record.update(barred='whole_window_capture_failure', score=1e100)
        scenario.sources['result'].update(score=1e100, eligible_benign={'spam': 0, 'bank': 0})
        scenario.finish()
        packet = scenario.build()
        self.assertNotIn('barred', packet['calibration_windows'][0])
        self.assertEqual(packet['calibration_decision']['replacements_used'], 0)

    def test_reserves_follow_bars_in_order_and_stop_after_eight_admitted(self):
        manifest = series.candidate()
        history = [ledger_row(n, bar='u1_u3_fail' if n <= 6 else None) for n in range(1, 9)]
        for n in range(9, 15):
            self.assertEqual(series.calibration_rows(manifest, history)[1], f'C{n}')
            if n < 14:
                with self.assertRaisesRegex(ValueError, 'skips/reorders'):
                    series.calibration_rows(manifest, [*history, ledger_row(n + 1)])
            history.append(ledger_row(n))
        rows, next_id, _, _ = series.calibration_rows(manifest, history)
        self.assertEqual(next_id, 'T1')
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'calibration_complete')

    def test_low_m_after_eight_admitted_is_insufficient_and_cannot_arm_c9(self):
        manifest = series.candidate()
        history = [ledger_row(n, eligible=4) for n in range(1, 9)]
        rows, _, _, _ = series.calibration_rows(manifest, history)
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'insufficient_calibration')
        with self.assertRaisesRegex(ValueError, 'skips/reorders'):
            series.calibration_rows(manifest, [*history, ledger_row(9)])

    def test_seventh_structural_bar_is_insufficient_and_seventh_zero_bar_escalates(self):
        manifest = series.candidate()
        history = [ledger_row(n, bar='u1_u3_fail') for n in range(1, 8)]
        rows, next_id, _, _ = series.calibration_rows(manifest, history)
        self.assertIsNone(next_id)
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'insufficient_calibration')
        zeros = [dict(window_id=f'C{n}', attempt_id=f'C{n}{suffix}', status='final',
                      captured_members=0, eligible_benign=dict.fromkeys(cad.CAL_PAIRS, 0))
                 for n in range(1, 8) for suffix in ('', '#2')]
        with self.assertRaisesRegex(ValueError, 'escalate_to_lead'):
            series.calibration_rows(manifest, zeros)
        stop_rows = [dict(window=r['attempt_id'], **{k: r[k] for k in
                     ('status', 'captured_members', 'eligible_benign')}) for r in zeros]
        self.assertEqual(cad.calibration_stop(stop_rows)['decision'], 'escalate_to_lead')

    def test_u5_inconclusive_does_not_trigger_sentinels_but_u4_does(self):
        for u4, expected in (('pass', 'pass'), ('inconclusive', 'fail')):
            with self.subTest(u4=u4):
                scenario = self.scenario('C1')
                scenario.thermal['model_windows']['tiny/C1']['U4']['status'] = u4
                scenario.thermal['model_windows']['tiny/C1']['U5']['status'] = 'inconclusive'
                scenario.next_plan['members'] = scenario.next_plan['members'][:2]
                scenario.series['sentinel_ids'] = scenario.series['sentinel_ids'][:2]
                scenario.finish()
                self.assertEqual(scenario.build()['checks']['sentinel_roster']['status'], expected)
        rows = [member('a'), member('b')]
        for u4, extra in (('pass', False), ('inconclusive', True)):
            result = thermal_desk.acceptance(
                rows, pairs=[tuple(rows)], v4=True, u4={'sentinels': {'status': u4}},
                u5={'status': 'inconclusive'})
            self.assertEqual(result['consequence'] == 'add 2 sentinels per remaining window', extra)


if __name__ == '__main__':
    unittest.main()
