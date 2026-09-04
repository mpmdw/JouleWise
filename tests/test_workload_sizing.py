from __future__ import annotations

import math
import unittest

from joulewise.workload_sizing import measured_margin_ratios


class WorkloadSizingRatiosTests(unittest.TestCase):
    def test_reports_floor_and_disclosed_clearable_ratios_separately(self) -> None:
        result = measured_margin_ratios(
            effect_j=-12.0,
            operative_floor_j=3.0,
            claim_side_bound_j=1.0,
        )

        self.assertEqual(result.effect_magnitude_j, 12.0)
        self.assertEqual(result.effective_clearable_effect_j, 4.0)
        self.assertEqual(result.effect_to_floor_ratio, 4.0)
        self.assertEqual(result.effect_to_effective_clearable_ratio, 3.0)

    def test_zero_effect_is_preserved_as_a_measured_zero_margin(self) -> None:
        result = measured_margin_ratios(
            effect_j=0,
            operative_floor_j=2,
            claim_side_bound_j=0,
        )

        self.assertEqual(result.effect_to_floor_ratio, 0.0)
        self.assertEqual(result.effect_to_effective_clearable_ratio, 0.0)

    def test_record_contains_no_unruled_acceptance_or_selection_field(self) -> None:
        record = measured_margin_ratios(
            effect_j=8,
            operative_floor_j=2,
            claim_side_bound_j=2,
        ).to_dict()

        self.assertEqual(
            set(record),
            {
                "effect_magnitude_j",
                "operative_floor_j",
                "claim_side_bound_j",
                "effective_clearable_effect_j",
                "effect_to_floor_ratio",
                "effect_to_effective_clearable_ratio",
            },
        )
        self.assertFalse({"accepted", "passes", "selected"} & set(record))

    def test_nonpositive_floor_refuses(self) -> None:
        for floor in (0, -1):
            with self.subTest(floor=floor), self.assertRaisesRegex(
                ValueError, "operative_floor_j must be greater than zero"
            ):
                measured_margin_ratios(
                    effect_j=1,
                    operative_floor_j=floor,
                    claim_side_bound_j=0,
                )

    def test_negative_claim_side_bound_refuses(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be non-negative"):
            measured_margin_ratios(
                effect_j=1,
                operative_floor_j=1,
                claim_side_bound_j=-1,
            )

    def test_nonfinite_and_nonreal_inputs_refuse(self) -> None:
        for field, value in (
            ("effect_j", math.nan),
            ("effect_j", math.inf),
            ("operative_floor_j", math.inf),
            ("claim_side_bound_j", math.nan),
            ("effect_j", True),
            ("effect_j", "1"),
        ):
            arguments = {
                "effect_j": 1,
                "operative_floor_j": 1,
                "claim_side_bound_j": 0,
            }
            arguments[field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(
                ValueError, f"{field} must be a finite real number"
            ):
                measured_margin_ratios(**arguments)


if __name__ == "__main__":
    unittest.main()
