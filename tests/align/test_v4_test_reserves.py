"""Option B test reserves at the arm (RUN_STATE 251; claim contract B6). Synthetic Git records only.

The packet builder derives a STRUCTURAL bar for a committed T window from its own record (the shared R22-2
predicate), so the series ledger owes T4 after a barred T1 and never arms a reserve otherwise.
"""
import unittest

from scripts import align_v4_series as series
from tests.align.test_v4_next_arm_packet import Base, Scenario


class TestReserveHistoryTests(Base):
    def chain(self, t1_u1):
        import tempfile
        temp = tempfile.TemporaryDirectory(prefix='jw-test-reserve-')
        self.addCleanup(temp.cleanup)
        previous = Scenario(temp.name, 'W1').finish()
        for n in range(1, 9):
            previous = Scenario(temp.name, f'C{n}', previous=previous).finish()
        t1 = Scenario(temp.name, 'T1', previous=previous)
        t1.record['role'] = 'test'
        t1.thermal['model_windows']['tiny/T1']['U1']['status'] = t1_u1
        return t1.finish()

    def test_a_u1_u3_failed_t_window_is_barred_in_the_rebuilt_history_and_owes_t4(self):
        packet = self.chain('fail').build()
        t1 = [h for h in packet['series_history'] if h.get('window_id') == 'T1']
        self.assertEqual(len(t1), 1, packet.get('calibration_error'))
        self.assertEqual(t1[0]['barred'], 'u1_u3_fail')
        manifest = series.candidate()
        history = [*packet['series_history'], {'window_id': 'T2', 'attempt_id': 'T2', 'status': 'final',
                   'captured_members': 22, 'eligible_benign': {'spam': 0, 'bank': 0}},
                   {'window_id': 'T3', 'attempt_id': 'T3', 'status': 'final', 'captured_members': 22,
                    'eligible_benign': {'spam': 0, 'bank': 0}}]
        self.assertEqual(series.calibration_rows(manifest, history)[1], 'T4')

    def test_a_passing_or_inconclusive_t_window_is_not_barred(self):
        for status in ('pass', 'inconclusive'):           # A23: only FAIL bars (the shared predicate)
            with self.subTest(status):
                packet = self.chain(status).build()
                t1 = [h for h in packet['series_history'] if h.get('window_id') == 'T1']
                self.assertEqual(len(t1), 1, packet.get('calibration_error'))
                self.assertNotIn('barred', t1[0])


if __name__ == '__main__':
    unittest.main()
