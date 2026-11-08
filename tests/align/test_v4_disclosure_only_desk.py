"""R22-1 end to end: no contention.* code affects any desk verdict, gate, count or packet decision. Synthetic only."""
import copy
import unittest

from joulewise.align.apple import v4_balance, v4_contention
from scripts import align_pilot_session as pilot, align_v4_next_arm_packet as builder, align_v4_session as session


class CommonDeskPolicyTests(unittest.TestCase):
    ENTRIES = [{'run_id': 'a', 'codes': ['contention.request_overlap']},
               {'run_id': 'b', 'codes': ['contention.unmeasured', 'member.runtime_failure']},
               {'run_id': 'c', 'codes': ['member.runtime_failure']},
               {'run_id': 'd', 'codes': []},
               {'run_id': 'e', 'codes': ['contention.unmeasured', 'contention.request_overlap']}]

    def test_the_v3_default_keeps_every_code_an_exclusion(self):
        excluded, disclosed = pilot.apply_exclusion_policy(self.ENTRIES)
        self.assertEqual(sorted(excluded), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(disclosed, {})

    def test_the_v4_policy_moves_only_contention_out_of_every_exclusion_decision(self):
        excluded, disclosed = pilot.apply_exclusion_policy(self.ENTRIES, v4_contention.split_codes)
        self.assertEqual(excluded, {'b': ['member.runtime_failure'], 'c': ['member.runtime_failure'], 'd': []})
        self.assertEqual(sorted(disclosed), ['a', 'b', 'e'])                     # the raw codes stay as disclosure
        self.assertEqual(disclosed['a'], ['contention.request_overlap'])
        self.assertNotIn('a', excluded)
        self.assertNotIn('e', excluded)

    def test_the_v4_desk_wrapper_defaults_to_the_disclosure_policy(self):
        import inspect
        source = inspect.getsource(session.desk)
        self.assertIn("exclusion_policy', v4_contention.split_codes", source)

    def test_a_contention_only_member_passes_the_native_full_desk_but_a_real_exclusion_fails(self):
        def member(codes):
            return {'run_id': 'm', 'task_pair': 'spam', 'condition': 'benign', 'excluded': bool(codes),
                    'exclusion_codes': codes,
                    'summary': {'energy': {'gpu': {'joules': 1., 'segment_sum_j': 1.}}, 'flags': [],
                                'configuration': {'sampler': {}}, 'window_evidence_precheck': {'eligible': True},
                                'excluded': bool(codes), 'exclusion_codes': codes}}
        for codes, passes in ((['contention.request_overlap'], True), (['contention.unmeasured'], True),
                              (['contention.request_overlap', 'battery.accumulator_excursion'], True),
                              (['member.runtime_failure'], False),
                              (['contention.unmeasured', 'member.runtime_failure'], False)):
            with self.subTest(codes=codes):
                victim = member(codes)
                checks = pilot.instrument_checks([victim])[0]
                checks.pop('I4_greedy_repeats_identical_tokens')
                checks['chain_eligibility'] = False
                self.assertEqual(session.full_desk_gate_pass(checks, [victim]), passes)


class PacketReaderTests(unittest.TestCase):
    CONTENTION_ONLY = {'members_excluded': [{'run_id': 'a', 'codes': ['contention.request_overlap']},
                                            {'run_id': 'b', 'codes': ['contention.unmeasured']}]}
    OLD_DESK = {'plan_id': 'p', 'pilot_status': 'instrument_incomplete', 'harvest_status': 'members_excluded',
                'full_desk_gate': {'pass': False},
                'checks': {'no_member_exclusions': False, 'chain_eligibility': False, 'other': True, 'v4_B_bar': True}}

    def test_a_desk_that_listed_only_contention_exclusions_is_reconciled_with_the_committed_harvest(self):
        self.assertFalse(builder.desk_passes(self.OLD_DESK))
        effective = builder.effective_desk(self.OLD_DESK, self.CONTENTION_ONLY)
        self.assertTrue(builder.desk_passes(effective))
        self.assertEqual((effective['harvest_status'], effective['pilot_status']), ('ok', 'instrument_ok'))
        self.assertEqual(self.OLD_DESK['harvest_status'], 'members_excluded')       # the committed bytes are not mutated

    def test_a_real_exclusion_or_another_failing_check_keeps_the_desk_failing(self):
        real = {'members_excluded': [{'run_id': 'a', 'codes': ['contention.unmeasured']},
                                     {'run_id': 'b', 'codes': ['member.runtime_failure']}]}
        self.assertIs(builder.effective_desk(self.OLD_DESK, real), self.OLD_DESK)
        no_codes = {'members_excluded': [{'run_id': 'a', 'codes': []}]}
        self.assertIs(builder.effective_desk(self.OLD_DESK, no_codes), self.OLD_DESK)
        other = copy.deepcopy(self.OLD_DESK)
        other['checks']['other'] = False
        self.assertFalse(builder.desk_passes(builder.effective_desk(other, self.CONTENTION_ONLY)))
        self.assertIs(builder.effective_desk(self.OLD_DESK, {'members_excluded': []}), self.OLD_DESK)
        self.assertIs(builder.effective_desk(self.OLD_DESK, None), self.OLD_DESK)


class BalanceTests(unittest.TestCase):
    def test_disclosed_contention_events_are_counted_once(self):
        row = {'id': 'm', 'condition': 'benign', 'task_pair': 'spam', 'gross_latency_s': 60., 'flags': ['contention.unmeasured'],
               'calibration_exclusions': [], 'contention': {'disclosed_codes': ['contention.request_overlap', 'contention.unmeasured'],
                                                          'flags': ['contention.unmeasured']}}
        report = v4_balance.balance_check([row])
        self.assertEqual(report['by_condition']['benign']['events'], 2)        # the unmeasured code is in three places


if __name__ == '__main__':
    unittest.main()
