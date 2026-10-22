"""Public tripwire accounting on synthetic reference memberships."""
import unittest

from joulewise.b5_analysis import context
from tests.b5_analysis import fixtures_s3b as fx


class TripwireCountTests(unittest.TestCase):
    def test_disjoint_survivors_and_exclusions_have_zero_intersection(self):
        """The public tripwire counts set intersection, not union. Kills M01153."""
        case = fx.Case()
        self.addCleanup(case.close)
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"]["reference_counts"] = {"start": 0, "midpoint": 1, "end": 3}
        case.write("derived/neg8-screen.json", screen)
        archive = case.handle()
        with self.assertRaises(context.TripwireRefusal) as caught:
            context.survivor_set(archive, case.row, case.roster(archive))
        public = caught.exception.to_structure_record()
        # Seven basis references survive; none is excluded, so their
        # intersection is empty. The mutant reports their seven-member union.
        self.assertEqual(public["stop"], "survivor_set_count_mismatch")
        self.assertEqual(public["survivor_count"], 7)
        self.assertEqual(public["excluded_reference_count"], 0)
        self.assertEqual(public["intersection_count"], 0)
