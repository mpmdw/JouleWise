"""Synthetic ordinal and public count-validation regressions."""
import unittest

from joulewise.b5_analysis import kept_units as ku
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s1 as fx


class KeptUnitBoundaryTests(unittest.TestCase):
    def case(self):
        case = fx.Case(fx.cached())
        self.addCleanup(case.close)
        return case

    def load(self, case, handle=None):
        return ku.load_kept_units(handle or case.handle(),
            sealed_catalog_sha256=fx.CATALOG.sha256, planned_units=case.planned)

    def test_each_reported_quad_has_its_own_four_ordinals(self):
        """Reported quads partition positions 11 through 50. Kills M04670."""
        view = self.load(self.case())
        spec = {"cells": [
            {"kind": "absolute", "condition_family_id": "df-b5t-family"},
            {"kind": "comparative", "condition_family_id": "df-b5t-family"},
        ]}
        selected = view.for_reported_cell(spec, 0)
        expected = ((11, 12, 13, 14), (15, 16, 17, 18), (19, 20, 21, 22),
                    (23, 24, 25, 26), (27, 28, 29, 30), (31, 32, 33, 34),
                    (35, 36, 37, 38), (39, 40, 41, 42), (43, 44, 45, 46),
                    (47, 48, 49, 50))
        # Exact integer oracle; M04670 adds at least four wrong positions.
        self.assertEqual(selected.kept_quad_ordinals, expected)
        self.assertEqual(tuple(len(quad) for quad in selected.kept_quad_ordinals), (4,) * 10)

    def test_zero_flag_count_is_a_supported_public_consumer(self):
        """Loading exclusions preserves a supported zero count. Kills M04204."""
        case = self.case()
        selected = case.handle()
        case.exclusions["flag_counts"]["by_code"]["member.retried"] = 0
        case.exclusions["flag_counts"]["by_family"]["ROSTER"] = 0
        case.write()
        # S0 omits zero-valued flag keys from its exact accounting projection.
        # The named S1 seam reaches load_kept_units' supported zero-count input
        # with real output digests and a previously selected window.
        view = self.load(case, ku.ArchiveHandle(selected.window, case.harvest, {}))
        self.assertEqual(view.structure_codes["member.retried"], 0)
        self.assertIs(type(view.structure_codes["member.retried"]), int)

    def test_negative_and_boolean_flag_counts_are_refused(self):
        """Count validation rejects -1 and booleans through the loader. Kills M04256."""
        for value in (-1, True, False):
            with self.subTest(value=value):
                case = self.case()
                selected = case.handle()
                case.exclusions["flag_counts"]["by_code"]["member.retried"] = value
                case.write()
                # Named S1 seam: retain a previously selected window and real
                # output digests to reach the loader's independent count guard.
                handle = ku.ArchiveHandle(selected.window, case.harvest, {})
                with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_schema_invalid$"):
                    self.load(case, handle)
