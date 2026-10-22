"""Synthetic reported-energy attribution extrema."""
import unittest

from joulewise import paper_reported_energy as energy
from tests.b5_analysis.test_reported_cell import case


class AttributionMaximumTests(unittest.TestCase):
    def test_interior_member_attains_the_attribution_floor(self):
        """The attribution floor names the largest interior bound. Kills M05883."""
        _cell, rows, _binding, kept = case((), (5, 9))
        for index, row in enumerate(rows):
            row["bounds_j"][energy.BOUND_KINDS[0]] = .5 if index == 3 else .01
        estimate = energy.estimate_reported_cell(rows, kept)
        # The only .500 J bound is the fourth kept member; every other bound
        # is .010 J. .5 is exactly representable in binary64.
        # COMMON bar would be 5e-7 J; mutant shift .49 J = 980,000 bars.
        self.assertEqual(estimate.attribution_floor["value_j"], .5)
        self.assertEqual(estimate.attribution_floor["attained_by"], rows[3]["member"]["bundle_id"])
