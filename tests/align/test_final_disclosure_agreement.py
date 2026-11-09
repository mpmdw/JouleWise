"""R17 finality and effective_desk share one disclosure-aware exclusion comparison (R22-1; Sol merge-c84 review F1)."""
import unittest

from joulewise.align.apple import light_triage, v4_contention
from scripts import align_v4_next_arm_packet as packet


def entry(run_id, *codes):
    return {'run_id': run_id, 'codes': list(codes)}


CONTENTION = 'contention.unmeasured'
REAL = 'clock.step'


def desk_and_pilot(excluded, disclosed):
    record = {'plan_id': 'W1', 'harvest_status': 'members_excluded' if excluded else 'ok',
              'members_excluded': excluded, 'members_disclosure_only': disclosed, 'status': 'instrument_ok'}
    return dict(record), dict(record)


def final_error(excluded, disclosed, harvest):
    desk, pilot = desk_and_pilot(excluded, disclosed)
    return light_triage.final_adjudication_error(desk, pilot, {'members_excluded': harvest}, 'W1', captured=True)


class FinalityAgreementTests(unittest.TestCase):
    def test_a_contention_only_desk_is_final(self):
        self.assertIsNone(final_error([], {'a': [CONTENTION]}, [entry('a', CONTENTION)]))

    def test_a_contention_only_member_beside_a_real_exclusion_is_final(self):
        self.assertIsNone(final_error([entry('b', REAL)], {'a': [CONTENTION]},
                                      [entry('a', CONTENTION), entry('b', REAL)]))

    def test_a_member_with_real_and_contention_codes_is_final(self):
        self.assertIsNone(final_error([entry('b', REAL, CONTENTION)], {'b': [CONTENTION]},
                                      [entry('b', CONTENTION, REAL)]))

    def test_real_exclusions_still_have_to_agree_exactly(self):
        for label, excluded, disclosed, harvest in (
                ('real code missing from the desk', [], {}, [entry('b', REAL)]),
                ('desk names another member', [entry('c', REAL)], {}, [entry('b', REAL)]),
                ('desk names other codes', [entry('b', 'clock.jump')], {}, [entry('b', REAL)]),
                ('contention hides a real exclusion', [], {'b': [CONTENTION]}, [entry('b', REAL, CONTENTION)]),
                ('disclosure names a member the harvest does not', [], {'z': [CONTENTION]}, [entry('a', CONTENTION)]),
                ('disclosed contention missing', [], {}, [entry('a', CONTENTION)])):
            with self.subTest(label):
                self.assertEqual(final_error(excluded, disclosed, harvest),
                                 'desk, PILOT.json and exclusions disagree')

    def test_a_desk_without_an_exclusion_record_is_still_not_compared(self):
        desk, pilot = {'plan_id': 'W1', 'harvest_status': 'ok'}, {'plan_id': 'W1', 'status': 'instrument_ok'}
        self.assertIsNone(light_triage.final_adjudication_error(
            desk, pilot, {'members_excluded': [entry('a', CONTENTION)]}, 'W1', captured=True))

    def test_effective_desk_and_finality_read_the_same_record(self):
        desk, _pilot = desk_and_pilot([entry('b', REAL)], {'a': [CONTENTION]})
        self.assertEqual(v4_contention.recorded_exclusion_map(desk), {'a': [CONTENTION], 'b': [REAL]})
        # The same record, against a harvest holding only contention, is a mismatch for both consumers.
        self.assertFalse(v4_contention.records_agree_with_harvest(desk, [entry('a', CONTENTION)]))
        with self.assertRaises(ValueError):
            packet.effective_desk({**desk, 'members_excluded': [], 'harvest_status': 'members_excluded'},
                                  {'members_excluded': [entry('a', CONTENTION), entry('q', CONTENTION)]})


if __name__ == '__main__':
    unittest.main()
