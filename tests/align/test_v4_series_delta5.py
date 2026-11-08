"""Delta5 follow-ups: retry slot normalization and the committed desk ceiling being mandatory. Synthetic only."""
import tempfile
import unittest

from scripts import align_v4_series as series
from tests.align.test_v4_next_arm_packet import Scenario


class SlotTests(unittest.TestCase):
    def test_only_a_registered_retry_id_is_normalized_to_its_slot(self):
        for attempt, slot in (('C3#2', 'C3'), ('T1#4', 'T1'), ('D2#1', 'D2'), ('C3', 'C3'), ('W1', 'W1'), ('R1', 'R1')):
            self.assertEqual(series.slot_of(attempt), slot)
        for odd in ('C3-a2', 'C03#2', 'C3#0', 'C3#', 'C3#2#3', 'X3#2', '', None, 7):
            self.assertEqual(series.slot_of(odd), odd)


class DeskCeilingTests(unittest.TestCase):
    def build(self, *, drop=False):
        temp = tempfile.TemporaryDirectory(prefix='jw-delta5-')
        self.addCleanup(temp.cleanup)
        first = Scenario(temp.name, 'W1').finish()
        c1 = Scenario(temp.name, 'C1', previous=first)
        if drop:
            del c1.sources['pilot']['extra_checks']['series_desk_row']
        return c1.finish().build()

    def test_the_provisional_ceiling_is_carried_into_the_history(self):
        packet = self.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['series_history'][0]['desk_eligible_benign'], {'spam': 7, 'bank': 7})

    def test_a_calibration_record_without_its_desk_row_cannot_drop_the_ceiling(self):
        packet = self.build(drop=True)
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('series_desk_row', packet['calibration_error'])
        self.assertEqual(packet['series_history'], [])


if __name__ == '__main__':
    unittest.main()
