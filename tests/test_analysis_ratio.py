"""Absolute/B8 metric vocabulary controls; synthetic, non-issuing inputs."""
import unittest

from joulewise.analysis_engine.ratio import (
    ABSOLUTE_METRIC_UNIT, RATIO_METRIC_UNIT, validate_metric_unit_and_ratio,
)
from tests.test_analysis_manifest import ratio_estimand


class MetricUnitTests(unittest.TestCase):
    def test_exact_unit_pairings(self):
        self.assertEqual(ABSOLUTE_METRIC_UNIT, "J")
        self.assertEqual(RATIO_METRIC_UNIT, "J/token")
        self.assertIsNone(validate_metric_unit_and_ratio("J", None))
        for form in ("mean_of_request_ratios", "ratio_of_totals"):
            ratio = ratio_estimand(form)
            with self.subTest(form=form):
                self.assertIs(validate_metric_unit_and_ratio("J/token", ratio), ratio)
            for unit in ("J", "J/parsecs", "J/committed_output_token",
                         "J/accepted_draft_token", "", None, 1, True, [], {}):
                for value in (None, ratio):
                    if unit == "J" and value is None:
                        continue
                    with self.subTest(form=form, unit=unit, ratio=value):
                        with self.assertRaises((TypeError, ValueError)):
                            validate_metric_unit_and_ratio(unit, value)

    def test_ratio_requires_exact_b8_mapping(self):
        for form in ("mean_of_request_ratios", "ratio_of_totals"):
            valid = ratio_estimand(form)
            invalid = [None, form, {"form": form}, dict(valid, extra="value")]
            for key in valid:
                invalid.append({name: value for name, value in valid.items() if name != key})
                invalid.append(dict(valid, **{key: "invented"}))
            for ratio in invalid:
                with self.subTest(form=form, ratio=ratio):
                    with self.assertRaises((TypeError, ValueError)):
                        validate_metric_unit_and_ratio("J/token", ratio)
