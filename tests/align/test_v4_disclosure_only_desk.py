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
                'members_excluded': [{'run_id': 'a', 'codes': ['contention.request_overlap']},
                                     {'run_id': 'b', 'codes': ['contention.unmeasured']}],
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

    def test_a_desk_that_disagrees_with_the_harvest_is_an_inconsistent_record_and_refuses(self):
        # delta7: the desk's own exclusions must be the SAME set (members and codes) as the harvest's
        cases = {
            'real exclusion in the desk': [{'run_id': 'a', 'codes': ['member.runtime_failure']},
                                           {'run_id': 'b', 'codes': ['contention.unmeasured']}],
            'a different member': [{'run_id': 'a', 'codes': ['contention.request_overlap']},
                                   {'run_id': 'z', 'codes': ['contention.unmeasured']}],
            'different codes': [{'run_id': 'a', 'codes': ['contention.unmeasured']},
                                {'run_id': 'b', 'codes': ['contention.unmeasured']}],
            'a member missing': [{'run_id': 'a', 'codes': ['contention.request_overlap']}],
            'a member too many': [*self.OLD_DESK['members_excluded'], {'run_id': 'c', 'codes': ['contention.unmeasured']}],
            'no record at all': [],
            'malformed': 'not a list',
        }
        for label, listed in cases.items():
            with self.subTest(label=label):
                desk = {**self.OLD_DESK, 'members_excluded': listed}
                with self.assertRaisesRegex(ValueError, 'disagree'):
                    builder.effective_desk(desk, self.CONTENTION_ONLY)
        absent = {k: v for k, v in self.OLD_DESK.items() if k != 'members_excluded'}
        with self.assertRaisesRegex(ValueError, 'disagree'):
            builder.effective_desk(absent, self.CONTENTION_ONLY)

    def test_the_new_native_desk_records_its_disclosure_only_members_and_matches(self):
        # the exclusion policy keeps contention-only members out of members_excluded and lists them apart
        desk = {**self.OLD_DESK, 'members_excluded': [], 'pilot_status': 'instrument_ok', 'harvest_status': 'ok',
                'full_desk_gate': {'pass': True}, 'checks': {'no_member_exclusions': True, 'chain_eligibility': True},
                'members_disclosure_only': {'a': ['contention.request_overlap'], 'b': ['contention.unmeasured']}}
        self.assertTrue(builder.desk_passes(builder.effective_desk(desk, self.CONTENTION_ONLY)))
        for wrong in ({'a': ['contention.request_overlap']}, {'a': ['contention.unmeasured'], 'b': ['contention.unmeasured']},
                      {'a': ['contention.request_overlap'], 'q': ['contention.unmeasured']}):
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ValueError, 'disagree'):
                builder.effective_desk({**desk, 'members_disclosure_only': wrong}, self.CONTENTION_ONLY)


class CommittedProbeTests(unittest.TestCase):
    """The delta7 seat's four probes, through the real builder, the arm's rebuild and the cadence."""

    def probe(self, desk_codes, harvest_codes, *, desk_member=0):
        import tempfile
        from tests.align.test_v4_next_arm_packet import Scenario, evaluate
        with tempfile.TemporaryDirectory(prefix='jw-delta7-probe-') as tmp:
            s = Scenario(tmp)
            victim, other = s.members[0]['run_id'], s.members[1]['run_id']
            s.sources['exclusions']['members_excluded'] = [{'run_id': victim, 'codes': harvest_codes}]
            desk_run = victim if desk_member == 0 else other
            s.sources['desk'].update(
                pilot_status='instrument_incomplete', harvest_status='members_excluded',
                members_excluded=[{'run_id': desk_run, 'codes': desk_codes}],
                checks={'synthetic_check': True, 'chain_eligibility': False, 'no_member_exclusions': False,
                        'v4_B_bar': True}, full_desk_gate={'pass': False})
            s.finish()
            packet = s.build()
            result = evaluate(s, packet)
            return packet['checks']['full_desk_gate']['status'], packet['packet_preflight']['ready'], result['admitted']

    def test_contention_in_desk_and_harvest_for_the_same_member_passes(self):
        self.assertEqual(self.probe(['contention.request_overlap'], ['contention.request_overlap']), ('pass', True, True))

    def test_a_real_exclusion_in_both_fails(self):
        status, ready, admitted = self.probe(['member.runtime_failure'], ['member.runtime_failure'])
        self.assertEqual((status, ready, admitted), ('fail', False, False))

    def test_a_real_exclusion_in_a_stale_desk_against_a_contention_harvest_refuses(self):
        status, ready, admitted = self.probe(['member.runtime_failure'], ['contention.request_overlap'])
        self.assertEqual((status, ready, admitted), ('fail', False, False))

    def test_contention_recorded_for_a_different_member_refuses(self):
        status, ready, admitted = self.probe(['contention.request_overlap'], ['contention.request_overlap'], desk_member=1)
        self.assertEqual((status, ready, admitted), ('fail', False, False))


class BalanceTests(unittest.TestCase):
    def test_disclosed_contention_events_are_counted_once(self):
        row = {'id': 'm', 'condition': 'benign', 'task_pair': 'spam', 'gross_latency_s': 60., 'flags': ['contention.unmeasured'],
               'calibration_exclusions': [], 'contention': {'disclosed_codes': ['contention.request_overlap', 'contention.unmeasured'],
                                                          'flags': ['contention.unmeasured']}}
        report = v4_balance.balance_check([row])
        self.assertEqual(report['by_condition']['benign']['events'], 2)        # the unmeasured code is in three places


if __name__ == '__main__':
    unittest.main()
