from __future__ import annotations

import json
import math
import random
import unittest
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from joulewise.clock import ClockStamp
from joulewise.detection_floor import _validate_idle_drift_guard
from joulewise.uncertainty_evidence import (
    derive_idle_drift_evidence,
    derive_powermetrics_clock_evidence,
    interim_idle_drift_guard,
    prediction_guard_w,
)


def stamp(epoch: float, monotonic: float, width: float = 0.0) -> ClockStamp:
    return ClockStamp(epoch, monotonic, monotonic + width, 0.001, 0.0001)


class ClockEvidenceTests(unittest.TestCase):
    def evidence(self, *, stop_epoch: float = 103.0):
        stamps = {
            "pre_spawn": stamp(100.0, 10.0),
            "first_parse": stamp(100.2, 10.2),
            "sampling_started": stamp(100.21, 10.21),
            "sampling_stopped": stamp(stop_epoch, 13.0),
            "post_parse": stamp(stop_epoch + 0.1, 13.1),
        }
        return derive_powermetrics_clock_evidence(
            stamps=stamps,
            elapsed_s=[0.1, 1.0, 1.0],
            plist_timestamp_s=[100.0, 101.0, 102.0],
        )

    def test_paired_stamp_envelope_and_midpoint_timestamp_arithmetic(self) -> None:
        evidence, point = self.evidence()
        clock = evidence["clock_anchor"]
        self.assertEqual(clock["status"], "bounded")
        self.assertAlmostEqual(clock["wall_minus_monotonic_lower_s"], 89.999)
        self.assertAlmostEqual(clock["wall_minus_monotonic_upper_s"], 90.001)
        self.assertAlmostEqual(point, 100.1)
        self.assertNotAlmostEqual(point, 100.2)  # no d0 double advance

    def test_wall_clock_step_enlarges_envelope(self) -> None:
        baseline, _ = self.evidence()
        stamps = {
            "pre_spawn": stamp(100.0, 10.0),
            "first_parse": stamp(100.2, 10.2),
            "sampling_started": stamp(105.21, 10.21),
            "sampling_stopped": stamp(108.0, 13.0),
            "post_parse": stamp(108.1, 13.1),
        }
        stepped, _ = derive_powermetrics_clock_evidence(
            stamps=stamps,
            elapsed_s=[0.1, 1.0, 1.0],
            plist_timestamp_s=[100.0, 101.0, 102.0],
        )
        self.assertGreater(
            stepped["clock_anchor"]["anchor_only_bound_s"],
            baseline["clock_anchor"]["anchor_only_bound_s"],
        )

    def test_nonfinite_or_reversed_stamp_is_unknown(self) -> None:
        stamps = {name: stamp(100.0, 10.0) for name in (
            "pre_spawn", "first_parse", "sampling_started", "sampling_stopped", "post_parse"
        )}
        stamps["first_parse"] = ClockStamp(100.0, 11.0, 10.0, 0.0, 0.0)
        evidence, point = derive_powermetrics_clock_evidence(
            stamps=stamps, elapsed_s=[1.0], plist_timestamp_s=[100.0]
        )
        self.assertIsNone(point)
        self.assertEqual(evidence["clock_anchor"]["reason"], "clock_stamp_invalid")

    def test_plist_date_is_consistency_only_and_cannot_tighten_anchor(self) -> None:
        evidence, _ = self.evidence()
        self.assertAlmostEqual(evidence["clock_anchor"]["anchor_only_bound_s"], 0.101)
        inconsistent, point = derive_powermetrics_clock_evidence(
            stamps={
                "pre_spawn": stamp(100.0, 10.0),
                "first_parse": stamp(100.2, 10.2),
                "sampling_started": stamp(100.21, 10.21),
                "sampling_stopped": stamp(103.0, 13.0),
                "post_parse": stamp(103.1, 13.1),
            },
            elapsed_s=[0.1, 1.0, 1.0],
            plist_timestamp_s=[500.0, 501.0, 502.0],
        )
        self.assertIsNotNone(point)
        self.assertEqual(inconsistent["clock_anchor"]["status"], "unknown")
        self.assertEqual(
            inconsistent["clock_anchor"]["reason"], "plist_timestamp_inconsistent"
        )

    def test_phase_bounds_and_reconstructed_endpoints_match_independent_fixture_math(self) -> None:
        evidence, first_endpoint = self.evidence()
        clock = evidence["clock_anchor"]
        phase = evidence["sample_phase"]
        self.assertAlmostEqual(phase["marker_to_first_sample_phase_bound_s"], 0.312)
        self.assertAlmostEqual(phase["marker_to_last_sample_phase_bound_s"], 2.002)
        self.assertAlmostEqual(clock["effective_clock_anchor_bound_s"], 2.002)
        self.assertEqual(
            [round(first_endpoint + offset, 10) for offset in (0.0, 1.0, 2.0)],
            [100.1, 101.1, 102.1],
        )


class IdleDriftEvidenceTests(unittest.TestCase):
    def test_pending_guard_matches_p2039_validator_wire_contract(self) -> None:
        guard = interim_idle_drift_guard()
        self.assertEqual(
            guard,
            {
                "calibration_status": "pending_calibration",
                "method": "p2_015_prediction_guard_v1",
                "guard_w": None,
                "n_bundles": 0,
                "bundle_sha256": [],
                "cell_id": None,
                "artifact_sha256": None,
            },
        )
        errors: list[str] = []
        _validate_idle_drift_guard(guard, "idle_drift_guard", errors)
        self.assertEqual(errors, [])

    def test_full_pre_post_envelope_retains_large_sample(self) -> None:
        evidence, guard, bound = derive_idle_drift_evidence(
            pre_power_w=[9.0, 10.0, 11.0],
            post_power_w=[10.0, 12.0, 50.0],
            pre_power_w_mean=10.0,
            pre_idle_window_suspect=False,
            post_idle_window_suspect=False,
        )
        self.assertEqual(bound, 40.0)
        self.assertEqual(evidence["run_observed_envelope_w"], 40.0)
        self.assertEqual(guard["n_bundles"], 0)

    def test_contamination_or_too_few_samples_withholds_scalar(self) -> None:
        for kwargs in (
            {"pre_idle_window_suspect": True, "post_idle_window_suspect": False},
            {"pre_idle_window_suspect": False, "post_idle_window_suspect": True},
        ):
            evidence, _guard, bound = derive_idle_drift_evidence(
                pre_power_w=[1.0, 1.0, 1.0],
                post_power_w=[1.0, 1.0, 1.0],
                pre_power_w_mean=1.0,
                **kwargs,
            )
            self.assertIsNone(bound)
            self.assertEqual(evidence["reason"], "sentinel_contaminated")
        evidence, _guard, bound = derive_idle_drift_evidence(
            pre_power_w=[1.0, 1.0],
            post_power_w=[1.0, 1.0, 1.0],
            pre_power_w_mean=1.0,
            pre_idle_window_suspect=False,
            post_idle_window_suspect=False,
        )
        self.assertIsNone(bound)
        self.assertEqual(evidence["reason"], "insufficient_idle_samples")

    def test_unknown_contamination_evidence_withholds_scalar_with_named_reason(self) -> None:
        for pre_status, post_status in ((None, False), (False, None), (None, None)):
            with self.subTest(pre=pre_status, post=post_status):
                evidence, _guard, bound = derive_idle_drift_evidence(
                    pre_power_w=[1.0, 1.0, 1.0],
                    post_power_w=[1.0, 1.0, 1.0],
                    pre_power_w_mean=1.0,
                    pre_idle_window_suspect=pre_status,
                    post_idle_window_suspect=post_status,
                )
                self.assertIsNone(bound)
                self.assertEqual(
                    evidence,
                    {
                        "status": "unknown",
                        "reason": "contamination_evidence_unknown",
                    },
                )

    def test_calibration_combination_is_exact_max_and_guard_formula(self) -> None:
        guard = {
            "status": "applied",
            "method": "p2_015_prediction_guard_v1",
            "guard_w": 5.0,
            "n_bundles": 5,
            "bundle_sha256": ["a" * 64],
            "cell_id": "cell",
            "artifact_sha256": "b" * 64,
        }
        evidence, _guard, bound = derive_idle_drift_evidence(
            pre_power_w=[0.0, 1.0, 2.0],
            post_power_w=[0.0, 1.0, 2.0],
            pre_power_w_mean=1.0,
            pre_idle_window_suspect=False,
            post_idle_window_suspect=False,
            calibration_guard=guard,
        )
        self.assertEqual(bound, 5.0)
        self.assertEqual(evidence["effective_bound_w"], 5.0)
        self.assertTrue(math.isfinite(prediction_guard_w([1.0, 2.0, 3.0], 4.303)))


if __name__ == "__main__":
    unittest.main()


class AnchorV2Tests(unittest.TestCase):
    """D-078 censored-intersection estimator: value oracle + fail-closed matrix."""

    @staticmethod
    def record(
        elapsed_s: float = 1.0,
        native_s: float = 1000.0,
        power_w: float = 1.0,
        energy_j: float | None = None,
        is_delta: bool | None = True,
    ):
        from joulewise.uncertainty_evidence import NativeAnchorRecord

        return NativeAnchorRecord(
            elapsed_s=elapsed_s,
            native_timestamp_s=native_s,
            power_w=power_w,
            energy_j=(power_w * elapsed_s if energy_j is None else energy_j),
            is_delta=is_delta,
        )

    @staticmethod
    def exact_stamp(epoch: float) -> ClockStamp:
        return ClockStamp(epoch, epoch, epoch, 0.0, 0.0)

    def stamps(
        self,
        *,
        pre_spawn: float = 999.0,
        first_parse: float = 1000.3,
    ) -> dict[str, ClockStamp]:
        return {
            "pre_spawn": self.exact_stamp(pre_spawn),
            "first_parse": self.exact_stamp(first_parse),
            "sampling_started": self.exact_stamp(first_parse + 0.1),
            "sampling_stopped": self.exact_stamp(first_parse + 3.0),
            "post_parse": self.exact_stamp(first_parse + 3.1),
        }

    def records(self):
        return [
            self.record(native_s=1000.0),
            self.record(native_s=1001.0),
            self.record(native_s=1002.0),
        ]

    def derive(self, stamps=None, records=None):
        from joulewise.uncertainty_evidence import derive_powermetrics_anchor_v2

        return derive_powermetrics_anchor_v2(
            stamps=self.stamps() if stamps is None else stamps,
            records=self.records() if records is None else records,
        )

    def assert_unresolved(self, result, detail: str) -> None:
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["reason"], "clock_anchor_unresolved")
        self.assertEqual(result["detail"], detail)

    def test_hand_computed_intersection_midpoint_and_bound(self) -> None:
        result = self.derive()
        self.assertEqual(result["status"], "bounded")
        # N = [1000, 1001); C = [999 + 1.0, 1000.3] -> I = [1000, 1000.3].
        self.assertEqual(result["native_intersection_lower_epoch_s"], 1000.0)
        self.assertEqual(result["native_intersection_upper_epoch_s"], 1001.0)
        self.assertEqual(result["admissible_lower_epoch_s"], 1000.0)
        self.assertAlmostEqual(result["admissible_upper_epoch_s"], 1000.3, places=12)
        self.assertAlmostEqual(
            result["first_sample_end_point_epoch_s"], 1000.15, places=12
        )
        self.assertAlmostEqual(result["anchor_only_bound_s"], 0.15, places=12)
        self.assertAlmostEqual(
            result["effective_clock_anchor_bound_s"], 0.15, places=12
        )
        self.assertAlmostEqual(result["first_parse_lag_s"], 0.0, places=12)
        self.assertEqual(result["native_rollover_count"], 2)

    def test_irregular_elapsed_tightens_native_intersection(self) -> None:
        records = [
            self.record(elapsed_s=1.0, native_s=1000.0),
            self.record(elapsed_s=0.9, native_s=1000.0),
            self.record(elapsed_s=1.05, native_s=1001.0),
        ]
        # q = [0, 0.9, 1.95]; N = [max(1000, 999.1, 999.05),
        #                          min(1001, 1000.1, 1000.05)) = [1000, 1000.05)
        result = self.derive(records=records)
        self.assertEqual(result["status"], "bounded")
        self.assertEqual(result["native_intersection_lower_epoch_s"], 1000.0)
        self.assertAlmostEqual(
            result["native_intersection_upper_epoch_s"], 1000.05, places=9
        )

    def test_missing_stamp_fails_closed(self) -> None:
        stamps = self.stamps()
        del stamps["post_parse"]
        self.assert_unresolved(self.derive(stamps=stamps), "clock_stamp_unavailable")

    def test_no_rollover_fails_closed(self) -> None:
        records = [self.record(native_s=1000.0), self.record(native_s=1000.0)]
        self.assert_unresolved(
            self.derive(records=records), "no_native_second_rollover"
        )

    def test_non_monotone_native_stamps_fail_closed(self) -> None:
        records = [
            self.record(native_s=1001.0),
            self.record(native_s=1000.0),
            self.record(native_s=1002.0),
        ]
        self.assert_unresolved(
            self.derive(records=records), "native_timestamps_non_monotone"
        )

    def test_nonpositive_elapsed_fails_closed(self) -> None:
        records = self.records()
        records[1] = self.record(elapsed_s=0.0, native_s=1001.0)
        self.assert_unresolved(
            self.derive(records=records), "native_record_malformed"
        )

    def test_not_delta_aggregate_fails_closed(self) -> None:
        records = self.records()
        records[0] = self.record(is_delta=None)
        self.assert_unresolved(
            self.derive(records=records), "native_record_not_delta_aggregate"
        )

    def test_energy_power_inconsistency_fails_closed_without_outlier_deletion(
        self,
    ) -> None:
        # One inconsistent record kills the whole derivation - it is never
        # dropped as an outlier.
        records = self.records()
        records[2] = self.record(native_s=1002.0, power_w=5.0, energy_j=1.0)
        self.assert_unresolved(
            self.derive(records=records), "native_energy_power_inconsistent"
        )

    def test_contradicting_later_record_empties_native_intersection(self) -> None:
        # Record 2's censored constraint [1002 - 1, 1003 - 1) does not meet
        # record 0's [1000, 1001): a later record contradicting the pre-start
        # estimate fails closed.
        records = [
            self.record(native_s=1000.0),
            self.record(native_s=1002.0),
        ]
        self.assert_unresolved(
            self.derive(records=records), "native_intersection_empty"
        )

    def test_empty_causal_intersection_fails_closed(self) -> None:
        stamps = self.stamps(pre_spawn=1000.5, first_parse=1000.9)
        # C = [1001.5, 1000.9] is empty against N = [1000, 1001).
        self.assert_unresolved(
            self.derive(stamps=stamps), "admissible_interval_empty"
        )

    def test_wall_minus_monotonic_step_fails_closed(self) -> None:
        stamps = self.stamps()
        stamps["post_parse"] = ClockStamp(1003.4 + 0.010, 1003.4, 1003.4, 0.0, 0.0)
        result = self.derive(stamps=stamps)
        self.assert_unresolved(result, "wall_minus_monotonic_span_exceeded")
        self.assertGreater(result["wall_minus_monotonic_span_s"], 0.005)

    def test_first_parse_lag_beyond_limit_fails_closed(self) -> None:
        stamps = self.stamps(first_parse=1001.5)
        # U = min(N_U, C_U) = 1001; lag = 1001.5 - 1001 = 0.5 > 0.25.
        result = self.derive(stamps=stamps)
        self.assert_unresolved(result, "first_parse_lag_exceeded")
        self.assertAlmostEqual(result["first_parse_lag_s"], 0.5, places=9)

    def test_full_evidence_wrapper_reports_v2_schema_and_phase(self) -> None:
        from joulewise.uncertainty_evidence import (
            SCHEMA_VERSION_V2,
            derive_powermetrics_clock_evidence_v2,
        )

        evidence, point = derive_powermetrics_clock_evidence_v2(
            stamps=self.stamps(), records=self.records()
        )
        self.assertEqual(evidence["schema_version"], SCHEMA_VERSION_V2)
        self.assertAlmostEqual(point, 1000.15, places=12)
        self.assertEqual(evidence["sample_phase"]["status"], "bounded")
        unresolved, no_point = derive_powermetrics_clock_evidence_v2(
            stamps={}, records=[]
        )
        self.assertIsNone(no_point)
        self.assertEqual(
            unresolved["sample_phase"],
            {"status": "unknown", "reason": "clock_anchor_unresolved"},
        )


# Epoch-scale fixture for the float64 representation pricing (cold science
# review Q1c / condition 2).  The synthetic AnchorV3ExactTests fixtures live at
# epoch 1000 s, where a binary64 ulp is ~1.1e-13 s and the representation error
# the review priced is invisible.  Real captures sit near 1.76e9 s, inside the
# binade [2**30, 2**31) where one ulp is 2**-22 s ~= 238.4 ns.
EPOCH_SCALE_BASE_S = 1_760_000_000
EPOCH_SCALE_ANCHOR_NS = (EPOCH_SCALE_BASE_S + 1) * 1_000_000_000
EPOCH_SCALE_STAMP_RESOLUTION_S = 1e-4


def epoch_scale_records(count: int = 61):
    """Native records whose first endpoint sits at a real-world epoch."""

    from joulewise.uncertainty_evidence import NativeAnchorRecord

    result = []
    q_ns = 0
    for index in range(count):
        elapsed_ns = 999_000_000 if index == 0 else 1_000_000_000
        if index > 0:
            q_ns += elapsed_ns
        native_ns = (
            (EPOCH_SCALE_ANCHOR_NS + q_ns) // 1_000_000_000 * 1_000_000_000
        )
        elapsed_s = elapsed_ns / 1_000_000_000.0
        result.append(
            NativeAnchorRecord(
                elapsed_s=elapsed_s,
                native_timestamp_s=native_ns / 1_000_000_000.0,
                power_w=1.0,
                energy_j=elapsed_s,
                is_delta=True,
                elapsed_ns=elapsed_ns,
                native_timestamp_ns=native_ns,
            )
        )
    return result


def epoch_scale_stamps() -> dict[str, ClockStamp]:
    def make(monotonic: Fraction) -> ClockStamp:
        epoch = Fraction(EPOCH_SCALE_BASE_S) + (monotonic - 100)
        return ClockStamp(
            float(epoch),
            float(monotonic),
            float(monotonic),
            EPOCH_SCALE_STAMP_RESOLUTION_S,
            EPOCH_SCALE_STAMP_RESOLUTION_S,
        )

    first = Fraction(100) + Fraction(1) + Fraction(1, 1024)
    return {
        "pre_spawn": make(Fraction(100)),
        "first_parse": make(first),
        "sampling_started": make(max(first, Fraction(102))),
        "sampling_stopped": make(Fraction(160)),
        "post_parse": make(Fraction(161)),
    }


EPOCH_SCALE_STAMPS = epoch_scale_stamps()


class AnchorV3ExactTests(unittest.TestCase):
    """Exact LP, elimination, containment, and refusal kill evidence."""

    A_NS = 1_001_000_000_000

    @staticmethod
    def record(elapsed_ns: int, native_ns: int):
        from joulewise.uncertainty_evidence import NativeAnchorRecord

        elapsed_s = elapsed_ns / 1_000_000_000.0
        return NativeAnchorRecord(
            elapsed_s=elapsed_s,
            native_timestamp_s=native_ns / 1_000_000_000.0,
            power_w=1.0,
            energy_j=elapsed_s,
            is_delta=True,
            elapsed_ns=elapsed_ns,
            native_timestamp_ns=native_ns,
        )

    def records(
        self,
        *,
        count: int = 61,
        first_elapsed_ns: int = 999_000_000,
        later_elapsed_ns: int = 1_000_000_000,
        rate: Fraction = Fraction(1),
    ):
        result = []
        q_ns = 0
        for index in range(count):
            elapsed_ns = first_elapsed_ns if index == 0 else later_elapsed_ns
            if index > 0:
                q_ns += elapsed_ns
            endpoint_ns = Fraction(self.A_NS) + rate * q_ns
            native_ns = (
                endpoint_ns.numerator
                // endpoint_ns.denominator
                // 1_000_000_000
                * 1_000_000_000
            )
            result.append(self.record(elapsed_ns, native_ns))
        return result

    @staticmethod
    def stamps(
        *,
        rate: Fraction = Fraction(1),
        first_delta: Fraction = Fraction(1) + Fraction(1, 1024),
        base_epoch: Fraction = Fraction(1000),
        resolution: float = 0.0,
    ) -> dict[str, ClockStamp]:
        def make(monotonic: Fraction) -> ClockStamp:
            epoch = base_epoch + rate * (monotonic - 100)
            return ClockStamp(
                float(epoch),
                float(monotonic),
                float(monotonic),
                resolution,
                resolution,
            )

        first = Fraction(100) + first_delta
        return {
            "pre_spawn": make(Fraction(100)),
            "first_parse": make(first),
            "sampling_started": make(max(first, Fraction(102))),
            "sampling_stopped": make(Fraction(160)),
            "post_parse": make(Fraction(161)),
        }

    def derive(self, *, stamps=None, records=None):
        from joulewise.uncertainty_evidence import derive_powermetrics_anchor_v3

        return derive_powermetrics_anchor_v3(
            stamps=self.stamps() if stamps is None else stamps,
            records=self.records() if records is None else records,
        )

    def assert_unresolved(self, result, detail: str) -> None:
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["reason"], "clock_anchor_unresolved")
        self.assertEqual(result["detail"], detail)
        self.assertEqual(result["method"], CLOCK_METHOD_V3)

    def test_lp2_matches_brute_force_vertices_on_200_rational_instances(self) -> None:
        from joulewise.uncertainty_evidence import _lp2

        rng = random.Random(9341)
        box = (Fraction(-3), Fraction(3), Fraction(-4), Fraction(4))
        box_rows = [
            (Fraction(-1), Fraction(0), Fraction(3)),
            (Fraction(1), Fraction(0), Fraction(3)),
            (Fraction(0), Fraction(-1), Fraction(4)),
            (Fraction(0), Fraction(1), Fraction(4)),
        ]
        objectives = {
            "min beta": (Fraction(1), Fraction(0), min),
            "max beta": (Fraction(1), Fraction(0), max),
            "min A": (Fraction(0), Fraction(1), min),
            "max A": (Fraction(0), Fraction(1), max),
        }
        for case in range(200):
            rows = []
            for _ in range(rng.randrange(1, 10)):
                rows.append(
                    (
                        Fraction(rng.randint(-4, 4)),
                        Fraction(rng.randint(-4, 4)),
                        Fraction(rng.randint(-10, 10)),
                    )
                )
            all_rows = [*rows, *box_rows]
            vertices = []
            for left, right in combinations(all_rows, 2):
                determinant = left[0] * right[1] - right[0] * left[1]
                if determinant == 0:
                    continue
                beta = (left[2] * right[1] - right[2] * left[1]) / determinant
                anchor = (left[0] * right[2] - right[0] * left[2]) / determinant
                if all(
                    c_beta * beta + c_anchor * anchor <= rhs
                    for c_beta, c_anchor, rhs in all_rows
                ):
                    vertices.append((beta, anchor))
            for name, (c_beta, c_anchor, extremum) in objectives.items():
                values = [
                    c_beta * beta + c_anchor * anchor
                    for beta, anchor in vertices
                ]
                expected = extremum(values) if values else None
                with self.subTest(case=case, objective=name):
                    self.assertEqual(_lp2(rows, name, box=box), expected)
                    self.assertEqual(_lp2(rows, name, box=box), expected)

    def test_alpha_elimination_matches_direct_three_variable_feasibility(self) -> None:
        from joulewise.uncertainty_evidence import _eliminate_alpha_v3

        uppers = [(Fraction(10), Fraction(-2)), (Fraction(12), Fraction(1))]
        lowers = [(Fraction(8), Fraction(-1)), (Fraction(9), Fraction(2))]
        k_pre = Fraction(-1)
        k_first = Fraction(3)
        stamp_rows, causal_rows = _eliminate_alpha_v3(
            uppers, lowers, k_pre, k_first
        )
        self.assertEqual(len(stamp_rows), 4)
        self.assertEqual(len(causal_rows), 4)
        # The v3 solver box is strictly positive; under that domain the
        # separately asserted k_pre <= k_first row is redundant.
        for beta_numerator in range(1, 7):
            beta = Fraction(beta_numerator, 4)
            for anchor in map(Fraction, range(0, 21)):
                eliminated = all(
                    c_beta * beta + c_anchor * anchor <= rhs
                    for c_beta, c_anchor, rhs in (*stamp_rows, *causal_rows)
                )
                direct_lower = max(
                    *(constant + slope * beta for constant, slope in lowers),
                    anchor - beta * k_first,
                )
                direct_upper = min(
                    *(constant + slope * beta for constant, slope in uppers),
                    anchor - beta * k_pre,
                )
                self.assertEqual(eliminated, direct_lower <= direct_upper)

    def test_outward_rounding_never_rounds_inward(self) -> None:
        from joulewise.uncertainty_evidence import (
            _round_outward_down,
            _round_outward_up,
        )

        just_above_one = Fraction(1) + Fraction(1, 1 << 1075)
        just_below_one = Fraction(1) - Fraction(1, 1 << 1075)
        self.assertEqual(_round_outward_up(just_above_one), math.nextafter(1.0, math.inf))
        self.assertEqual(
            _round_outward_down(just_below_one), math.nextafter(1.0, -math.inf)
        )
        self.assertGreaterEqual(Fraction(_round_outward_up(just_above_one)), just_above_one)
        self.assertLessEqual(Fraction(_round_outward_down(just_below_one)), just_below_one)

    def test_full_departure_allowance_is_charged_even_when_observed_residual_is_zero(self) -> None:
        from joulewise.uncertainty_evidence import (
            MAX_AFFINE_CLOCK_RESIDUAL_S,
            _round_outward_up,
        )

        result = self.derive()
        self.assertEqual(result["status"], "bounded")
        full_charge = Fraction(MAX_AFFINE_CLOCK_RESIDUAL_S)
        expected = _round_outward_up((Fraction(1, 1024) + full_charge) / 2)
        zero_residual_mutant = float(Fraction(1, 2048))
        self.assertEqual(result["anchor_only_bound_s"], expected)
        self.assertGreater(result["anchor_only_bound_s"], zero_residual_mutant)
        self.assertLessEqual(
            result["min_l_infinity_residual_upper_bound_s"],
            MAX_AFFINE_CLOCK_RESIDUAL_S / (1 << 24) * 1.000001,
        )

    def test_infeasible_affine_residual_refuses(self) -> None:
        records = self.records(first_elapsed_ns=500_000_000)
        result = self.derive(
            stamps=self.stamps(first_delta=Fraction(3, 4)), records=records
        )
        self.assert_unresolved(result, "affine_clock_residual_exceeded")

    def test_wall_minus_monotonic_span_rule_still_refuses_under_v3(self) -> None:
        stamps = self.stamps()
        post = stamps["post_parse"]
        stamps["post_parse"] = replace(post, epoch_s=post.epoch_s + 0.006)
        result = self.derive(stamps=stamps)
        self.assert_unresolved(result, "wall_minus_monotonic_span_exceeded")
        self.assertGreater(result["wall_minus_monotonic_span_s"], 0.005)

    def test_empty_native_rate_set_refuses(self) -> None:
        records = [
            self.record(
                999_000_000 if index == 0 else 1_000_000_000,
                self.A_NS + 2 * index * 1_000_000_000,
            )
            for index in range(61)
        ]
        self.assert_unresolved(
            self.derive(records=records), "rate_aware_native_set_empty"
        )

    def test_non_affine_stamp_set_refuses(self) -> None:
        stamps = self.stamps()
        sample = stamps["sampling_started"]
        stamps["sampling_started"] = replace(
            sample, epoch_s=sample.epoch_s + 1 / 1024
        )
        self.assert_unresolved(
            self.derive(stamps=stamps), "affine_clock_fit_empty"
        )

    def test_rate_outside_limit_refuses_instead_of_clipping_beta(self) -> None:
        rate = Fraction(1) + Fraction(1, 16384)
        result = self.derive(
            stamps=self.stamps(rate=rate), records=self.records(rate=rate)
        )
        self.assert_unresolved(result, "clock_rate_limit_exceeded")
        self.assertGreater(result["rate_lower"], 1.0 + 50e-6)

    def test_solver_box_contact_refuses_instead_of_clipping(self) -> None:
        result = self.derive(stamps=self.stamps(resolution=1.0))
        self.assert_unresolved(result, "clock_fit_unbounded")

    def test_insufficient_rate_span_refuses(self) -> None:
        result = self.derive(records=self.records(count=10))
        self.assert_unresolved(result, "clock_fit_span_insufficient")

    def test_native_backward_step_refuses(self) -> None:
        records = self.records()
        records[20] = replace(
            records[20],
            native_timestamp_s=records[19].native_timestamp_s - 1.0,
            native_timestamp_ns=records[19].native_timestamp_ns - 1_000_000_000,
        )
        self.assert_unresolved(
            self.derive(records=records), "native_timestamps_non_monotone"
        )

    def test_impossible_forward_rollover_refuses(self) -> None:
        records = self.records()
        records[1:] = [
            replace(
                record,
                native_timestamp_s=record.native_timestamp_s + 2.0,
                native_timestamp_ns=record.native_timestamp_ns + 2_000_000_000,
            )
            for record in records[1:]
        ]
        self.assert_unresolved(self.derive(records=records), "native_rollover_anomalous")

    def test_zero_rollovers_refuses(self) -> None:
        records = [
            replace(
                record,
                native_timestamp_s=self.A_NS / 1_000_000_000,
                native_timestamp_ns=self.A_NS,
            )
            for record in self.records()
        ]
        self.assert_unresolved(self.derive(records=records), "no_native_second_rollover")

    def test_causal_set_empty_even_with_one_second_relaxation_refuses(self) -> None:
        result = self.derive(
            stamps=self.stamps(
                base_epoch=Fraction(998), first_delta=Fraction(9, 8)
            )
        )
        self.assert_unresolved(result, "admissible_interval_empty")

    def test_first_parse_lag_over_quarter_second_refuses(self) -> None:
        result = self.derive(stamps=self.stamps(first_delta=Fraction(3, 2)))
        self.assert_unresolved(result, "first_parse_lag_exceeded")
        self.assertGreater(result["first_parse_lag_s"], 0.25)

    def test_effective_bound_over_five_milliseconds_refuses(self) -> None:
        result = self.derive(
            stamps=self.stamps(first_delta=Fraction(65, 64))
        )
        self.assert_unresolved(result, "effective_clock_anchor_bound_exceeded")
        self.assertGreater(result["effective_clock_anchor_bound_s"], 0.005)

    def test_exact_native_fields_and_whole_second_labels_fail_closed(self) -> None:
        missing = self.records()
        missing[0] = replace(missing[0], elapsed_ns=None)
        self.assert_unresolved(
            self.derive(records=missing), "native_exact_inputs_unavailable"
        )
        nonwhole = self.records()
        nonwhole[0] = replace(nonwhole[0], native_timestamp_ns=self.A_NS + 1)
        self.assert_unresolved(
            self.derive(records=nonwhole), "native_label_not_whole_second"
        )

    def test_every_record_participates_deleting_one_constraint_changes_oracle(self) -> None:
        from joulewise.uncertainty_evidence import (
            MAX_AFFINE_CLOCK_RESIDUAL_S,
            _lp2,
            _native_v3_constraints,
        )

        records = self.records(count=62, later_elapsed_ns=999_000_000)
        native = [record.native_timestamp_ns for record in records]
        cumulative = [0]
        for record in records[1:]:
            cumulative.append(cumulative[-1] + record.elapsed_ns)
        rows = _native_v3_constraints(
            native,
            cumulative,
            Fraction(MAX_AFFINE_CLOCK_RESIDUAL_S) * 1_000_000_000,
        )
        beta_one = [
            (Fraction(1), Fraction(0), Fraction(1)),
            (Fraction(-1), Fraction(0), Fraction(-1)),
        ]
        box = (
            Fraction(999, 1000),
            Fraction(1001, 1000),
            Fraction(self.A_NS - 2_000_000_000),
            Fraction(self.A_NS + 2_000_000_000),
        )
        full_upper = _lp2([*rows, *beta_one], "max A", box=box)
        without_record_one = _lp2(
            [*rows[:2], *rows[4:], *beta_one], "max A", box=box
        )
        self.assertIsNotNone(full_upper)
        self.assertIsNotNone(without_record_one)
        self.assertGreater(without_record_one, full_upper)

    def test_midpoint_native_timestamp_mutation_would_break_bounded_fixture(self) -> None:
        result = self.derive()
        self.assertEqual(result["status"], "bounded")
        self.assertLess(result["anchor_upper_epoch_s"], 1001.01)
        self.assertGreater(abs(result["first_sample_end_point_epoch_s"] - 1001.5), 0.49)

    def test_numeric_padding_is_priced_for_epoch_scale_representation(self) -> None:
        """Cold science review Q1c / condition 2: the float64 span/epoch
        representation error is priced by the constant, and the constant's
        sufficiency is checked against the capture's own epoch scale."""

        from joulewise.uncertainty_evidence import (
            EPOCH_REPRESENTATION_ULP_COUNT,
            NUMERIC_PADDING_S,
        )

        # The review's explicit floor, and the derivation behind it: at most
        # four epoch-scale ulps can lean inward, and one ulp anywhere in the
        # binade [2**30, 2**31) s (through 2038-01-19) is 2**-22 s.
        self.assertGreaterEqual(NUMERIC_PADDING_S, 1e-6)
        self.assertEqual(EPOCH_REPRESENTATION_ULP_COUNT, 4)
        self.assertEqual(math.ulp(float(2**31 - 1024)), 2.0**-22)
        self.assertGreaterEqual(
            NUMERIC_PADDING_S,
            EPOCH_REPRESENTATION_ULP_COUNT * math.ulp(float(2**31 - 1024)),
        )
        self.assertLess(
            EPOCH_REPRESENTATION_ULP_COUNT * math.ulp(float(2**31 - 1024)),
            1e-6,
        )

    def test_epoch_scale_capture_charges_the_priced_padding(self) -> None:
        from joulewise.uncertainty_evidence import (
            NUMERIC_PADDING_S,
            _round_outward_up,
        )

        result = self.derive(
            stamps=EPOCH_SCALE_STAMPS, records=epoch_scale_records()
        )
        self.assertEqual(result["status"], "bounded")
        self.assertEqual(result["numeric_padding_s"], NUMERIC_PADDING_S)
        self.assertEqual(result["epoch_representation_term_s"], 2.0**-20)
        self.assertGreaterEqual(
            result["numeric_padding_s"], result["epoch_representation_term_s"]
        )
        composed = (
            Fraction(result["anchor_only_bound_s"])
            + Fraction(result["wall_minus_monotonic_span_s"])
            + Fraction(result["stamp_resolution_s"])
        )
        # The padding is charged outward and is not absorbed by rounding: the
        # emitted bound exceeds the unpadded composition by at least the
        # representation term the review demanded be priced.  ``composed`` uses
        # the already-outward-rounded half-width, so the exact half-width is
        # pinned from below by one ulp of it.
        exact_half_width_floor = Fraction(
            result["anchor_only_bound_s"]
        ) - Fraction(math.ulp(result["anchor_only_bound_s"]))
        self.assertGreaterEqual(
            Fraction(result["effective_clock_anchor_bound_s"]),
            exact_half_width_floor
            + Fraction(result["wall_minus_monotonic_span_s"])
            + Fraction(result["stamp_resolution_s"])
            + Fraction(NUMERIC_PADDING_S),
        )
        self.assertGreater(
            result["effective_clock_anchor_bound_s"] - float(composed),
            result["epoch_representation_term_s"],
        )
        self.assertLessEqual(
            Fraction(result["effective_clock_anchor_bound_s"]),
            Fraction(
                _round_outward_up(composed + Fraction(NUMERIC_PADDING_S))
            ),
        )

    def test_padding_smaller_than_representation_term_refuses(self) -> None:
        """Kill evidence: the retired 1e-9 padding does not cover an
        epoch-scale capture and must refuse rather than emit a bound."""

        import joulewise.uncertainty_evidence as module

        original = module.NUMERIC_PADDING_S
        try:
            module.NUMERIC_PADDING_S = 1e-9
            mutant = self.derive(
                stamps=EPOCH_SCALE_STAMPS, records=epoch_scale_records()
            )
            self.assert_unresolved(mutant, "numeric_padding_insufficient")
            self.assertEqual(mutant["epoch_representation_term_s"], 2.0**-20)
            self.assertEqual(mutant["numeric_padding_s"], 1e-9)
            # The guard is scale-aware, not a blanket rejection: the same
            # padding covers a small-epoch synthetic fixture.
            self.assertEqual(self.derive()["status"], "bounded")
        finally:
            module.NUMERIC_PADDING_S = original

    def test_v3_wrapper_and_registered_dispatch(self) -> None:
        from joulewise.uncertainty_evidence import (
            ACTIVE_CAPTURE_ANCHOR_METHOD,
            ANCHOR_METHOD_DERIVERS,
            ANCHOR_METHOD_VERSIONS,
            CLOCK_METHOD_V2,
            CLOCK_METHOD_V3,
            SCHEMA_VERSION_V3,
            derive_powermetrics_anchor_v3,
            derive_powermetrics_clock_evidence_v3,
            resolve_anchor_deriver,
        )

        evidence, point = derive_powermetrics_clock_evidence_v3(
            stamps=self.stamps(), records=self.records()
        )
        self.assertEqual(evidence["schema_version"], SCHEMA_VERSION_V3)
        self.assertEqual(evidence["clock_anchor"]["method"], CLOCK_METHOD_V3)
        self.assertIsNotNone(point)
        self.assertEqual(ANCHOR_METHOD_VERSIONS, {CLOCK_METHOD_V2, CLOCK_METHOD_V3})
        self.assertIs(resolve_anchor_deriver(CLOCK_METHOD_V3), derive_powermetrics_anchor_v3)
        self.assertEqual(ACTIVE_CAPTURE_ANCHOR_METHOD, CLOCK_METHOD_V3)
        self.assertIn(ACTIVE_CAPTURE_ANCHOR_METHOD, ANCHOR_METHOD_DERIVERS)
        self.assertIs(
            resolve_anchor_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD),
            derive_powermetrics_anchor_v3,
        )
        with self.assertRaisesRegex(ValueError, "unregistered"):
            resolve_anchor_deriver("unknown")


# --------------------------------------------------------------------------
# A267 QPE01-CLOCK-DISCIPLINE-ANCHOR-01 — cold-gate regressions 1-5 and 8-12
# (packet 2026-09-22, ruling 10 Q2/Q4 as amended by rebuttal ruling 14
# R1/R2/R3/R5).  Fixtures are the twelve archived envelopes of the pilot night
# qpe01-pilot-n1-20260922-0217; see tests/fixtures/.../SOURCES.md for the
# archive digests.
# --------------------------------------------------------------------------

PILOT_FIXTURES = (
    Path(__file__).resolve().parent / "fixtures" / "qpe01_pilot_n1_20260922"
)


def pilot_envelope(index: int) -> dict:
    return json.loads((PILOT_FIXTURES / f"envelope-{index:02d}.json").read_text())


def pilot_stamps(fixture: dict) -> dict[str, ClockStamp]:
    return {name: ClockStamp(**value)
            for name, value in fixture["clock_stamps"].items()}


def pilot_records(fixture: dict):
    from joulewise.uncertainty_evidence import NativeAnchorRecord

    return [
        NativeAnchorRecord(
            elapsed_s=elapsed_ns / 1e9,
            native_timestamp_s=native_ns / 1e9,
            power_w=power_w,
            energy_j=energy_j,
            is_delta=is_delta,
            elapsed_ns=elapsed_ns,
            native_timestamp_ns=native_ns,
        )
        for elapsed_ns, native_ns, power_w, energy_j, is_delta in fixture["records"]
    ]


class AnchorV31ColdGateTests(unittest.TestCase):
    """The v3.1 evidence identity: what it admits, what it refuses, and why.

    Every refusal here is a REFUSAL, not a clipped value: the anchor either
    bounds the first sample's endpoint on the wall timeline or says it cannot.
    """

    DURATION_S = Fraction(600)
    # Real captures stamp a wall read with a finite resolution; a zero-width
    # bracket would force five exact float equalities on two unknowns.
    RESOLUTION_S = 1e-6

    def derive(self, **kwargs):
        from joulewise.uncertainty_evidence import derive_powermetrics_anchor_v3

        return derive_powermetrics_anchor_v3(**kwargs)

    def v3_1(self, *, stamps, records):
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3_1

        return self.derive(stamps=stamps, records=records, method=CLOCK_METHOD_V3_1)

    def synthetic(self, *, rate_ppm=0, duration_s=None, step_s=Fraction(0),
                  resolution_s=None):
        """A capture whose wall clock runs at a known rate, with optional step.

        ``rate_ppm`` tilts wall against monotonic over the whole capture (the
        residual frequency correction a network-time-OFF machine keeps
        applying); ``step_s`` moves the wall clock once, between
        ``sampling_started`` and ``sampling_stopped``, with native rows on
        both sides.
        """
        duration = self.DURATION_S if duration_s is None else Fraction(duration_s)
        resolution = self.RESOLUTION_S if resolution_s is None else resolution_s
        rate = Fraction(1) + Fraction(int(rate_ppm), 10 ** 6)
        base_epoch = Fraction(1000)
        anchor_ns = 1_001_000_000_000

        def make(monotonic: Fraction, offset: Fraction = Fraction(0)) -> ClockStamp:
            epoch = base_epoch + rate * (monotonic - 100) + offset
            return ClockStamp(float(epoch), float(monotonic), float(monotonic),
                              resolution, resolution)

        first = Fraction(100) + Fraction(1) + Fraction(1, 1024)
        stamps = {
            "pre_spawn": make(Fraction(100)),
            "first_parse": make(first),
            "sampling_started": make(max(first, Fraction(102))),
            "sampling_stopped": make(Fraction(100) + duration, step_s),
            "post_parse": make(Fraction(101) + duration, step_s),
        }
        from joulewise.uncertainty_evidence import NativeAnchorRecord

        records, elapsed_total = [], 0
        for index in range(int(duration) + 1):
            elapsed_ns = 999_000_000 if index == 0 else 1_000_000_000
            if index:
                elapsed_total += elapsed_ns
            endpoint = Fraction(anchor_ns) + rate * elapsed_total
            native_ns = (endpoint.numerator // endpoint.denominator
                         // 1_000_000_000 * 1_000_000_000)
            records.append(NativeAnchorRecord(
                elapsed_s=elapsed_ns / 1e9, native_timestamp_s=native_ns / 1e9,
                power_w=1.0, energy_j=elapsed_ns / 1e9, is_delta=True,
                elapsed_ns=elapsed_ns, native_timestamp_ns=native_ns))
        return stamps, records

    # -- regression 1 ------------------------------------------------------
    def test_envelope_08_is_bounded_under_v3_1_with_the_drift_priced_in(self) -> None:
        from joulewise.uncertainty_evidence import (
            CLOCK_METHOD_V3_1, SCHEMA_VERSION_V3_1, V3_1_CAPS,
        )

        fixture = pilot_envelope(8)
        record = self.v3_1(stamps=pilot_stamps(fixture),
                           records=pilot_records(fixture))
        self.assertEqual(record["status"], "bounded", record.get("detail"))
        self.assertEqual(record["method"], CLOCK_METHOD_V3_1)
        self.assertEqual(record["clock_anchor_method"], CLOCK_METHOD_V3_1)
        self.assertEqual(record["schema_version"], SCHEMA_VERSION_V3_1)
        self.assertEqual(record["caps"], dict(V3_1_CAPS))
        self.assertEqual(len(record["caps"]), 4)
        # The night's own -7.60 ppm residual frequency correction over a 591 s
        # capture: 4.54 ms of wall-versus-monotonic drift.
        self.assertGreaterEqual(record["wall_minus_monotonic_span_s"], 0.00454)
        self.assertLessEqual(record["wall_minus_monotonic_span_s"], 0.00455)
        # The drift is PRICED, not clipped: it is the dominant term of the
        # emitted bound.  Restoring an absolute 5 ms cap on the bound would
        # refuse this envelope (regression 2); dropping the span term from the
        # bound would leave under 1 ms and understate the mapping error.
        self.assertGreaterEqual(record["effective_clock_anchor_bound_s"], 0.0050)
        self.assertLessEqual(record["effective_clock_anchor_bound_s"], 0.0052)
        self.assertLess(record["anchor_only_bound_s"], 0.001)
        self.assertLess(record["placement_bound_s"],
                        V3_1_CAPS["max_placement_bound_s"])

    # -- regression 2 ------------------------------------------------------
    def test_envelope_08_still_refuses_under_the_default_v3_identity(self) -> None:
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

        fixture = pilot_envelope(8)
        record = self.derive(stamps=pilot_stamps(fixture),
                             records=pilot_records(fixture))
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["detail"], "effective_clock_anchor_bound_exceeded")
        self.assertEqual(record["method"], CLOCK_METHOD_V3)
        self.assertAlmostEqual(record["effective_clock_anchor_bound_s"],
                               0.0050768, places=6)
        # v3 records gain no identity key at all (review condition 6).
        for key in ("clock_anchor_method", "schema_version", "caps",
                    "placement_bound_s", "first_sample_end_point_epoch_ns"):
            self.assertNotIn(key, record)

    # -- regression 3 ------------------------------------------------------
    def test_envelope_07_refuses_pre_fit_and_reports_its_38_ppm_rate(self) -> None:
        """The night's 20 ms adjtime slew: refused before the fit is attempted.

        Ruling 14 R1 puts the frozen 15 ms span backstop BEFORE the 25 ppm
        rate gate, so this 22.36 ms excursion is caught by the backstop; the
        sustained rate is emitted on both rate-aware refusals so the evidence
        a reader needs is never deleted by whichever gate fires first.
        """
        fixture = pilot_envelope(7)
        record = self.v3_1(stamps=pilot_stamps(fixture),
                           records=pilot_records(fixture))
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["detail"], "wall_minus_monotonic_span_exceeded")
        self.assertGreaterEqual(record["wall_minus_monotonic_rate_ppm"], 37)
        self.assertLessEqual(record["wall_minus_monotonic_rate_ppm"], 39)
        self.assertEqual(record["max_wall_minus_monotonic_span_s"], 0.015)
        self.assertAlmostEqual(record["wall_minus_monotonic_span_s"], 0.0223608,
                               places=6)
        self.assertGreater(record["rate_fit_baseline_s"], 500)

    # -- regression 4 ------------------------------------------------------
    def test_six_millisecond_wall_step_refuses_and_two_tenths_is_bounded(self) -> None:
        stamps, records = self.synthetic(step_s=Fraction(6, 1000))
        stepped = self.v3_1(stamps=stamps, records=records)
        self.assertEqual(stepped["status"], "unknown")
        # Observed detail on first run; pinned exactly thereafter.  Both
        # members of the ruled pair are fit refusals, not gate refusals.
        self.assertEqual(stepped["detail"], "affine_clock_fit_empty")
        self.assertIn(stepped["detail"],
                      {"rate_aware_native_set_empty", "affine_clock_fit_empty"})
        small, records = self.synthetic(step_s=Fraction(2, 10_000))
        bounded = self.v3_1(stamps=small, records=records)
        self.assertEqual(bounded["status"], "bounded", bounded.get("detail"))
        self.assertAlmostEqual(bounded["wall_minus_monotonic_span_s"], 0.0002,
                               places=7)

    # -- regressions 5 and 9 ----------------------------------------------
    def test_thirty_ppm_refuses_and_twenty_ppm_is_bounded_with_its_drift(self) -> None:
        stamps, records = self.synthetic(rate_ppm=30)
        refused = self.v3_1(stamps=stamps, records=records)
        self.assertEqual(refused["status"], "unknown")
        # 30 ppm over 600 s is 18 ms, which the 15 ms backstop catches first.
        self.assertEqual(refused["detail"], "wall_minus_monotonic_span_exceeded")
        self.assertAlmostEqual(refused["wall_minus_monotonic_rate_ppm"], 30.05,
                               places=2)
        stamps, records = self.synthetic(rate_ppm=20)
        bounded = self.v3_1(stamps=stamps, records=records)
        self.assertEqual(bounded["status"], "bounded", bounded.get("detail"))
        self.assertAlmostEqual(bounded["wall_minus_monotonic_span_s"], 0.01202,
                               places=5)
        # The 12 ms of drift is inside the emitted bound, not discarded.
        self.assertGreater(bounded["effective_clock_anchor_bound_s"],
                           bounded["wall_minus_monotonic_span_s"])
        self.assertLess(bounded["effective_clock_anchor_bound_s"], 0.013)

    def test_the_twenty_five_ppm_rate_gate_refuses_a_short_fast_capture(self) -> None:
        """The rate gate's own kill: 30 ppm over 300 s is 9 ms, under the
        backstop, and must still refuse."""
        stamps, records = self.synthetic(rate_ppm=30, duration_s=300)
        record = self.v3_1(stamps=stamps, records=records)
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["detail"], "wall_minus_monotonic_rate_exceeded")
        self.assertAlmostEqual(record["wall_minus_monotonic_rate_ppm"], 30.1,
                               places=2)
        self.assertEqual(record["max_sustained_rate_ppm"], 25.0)
        self.assertLess(record["wall_minus_monotonic_span_s"], 0.015)
        self.assertAlmostEqual(record["rate_fit_baseline_s"], 300, places=6)

    # -- regression 8 ------------------------------------------------------
    def test_all_twelve_archived_envelopes_replay_v3_byte_identical(self) -> None:
        """Ruling 14 R3(i): zero delta on twelve real members, refusals
        included, under the default method."""
        for index in range(1, 13):
            with self.subTest(envelope=index):
                fixture = pilot_envelope(index)
                self.assertEqual(
                    self.derive(stamps=pilot_stamps(fixture),
                                records=pilot_records(fixture)),
                    fixture["recorded_anchor"],
                )

    # -- regression 10 -----------------------------------------------------
    def test_placement_over_five_milliseconds_refuses_at_a_lawful_rate(self) -> None:
        """A 6 ms stamp resolution places the endpoint no better than 6 ms.

        The rate is zero, so neither the backstop nor the rate gate fires:
        only the placement cap stands between this capture and a bound it has
        not earned.
        """
        stamps, records = self.synthetic(resolution_s=0.006)
        record = self.v3_1(stamps=stamps, records=records)
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["detail"], "effective_clock_anchor_bound_exceeded")
        self.assertEqual(record["wall_minus_monotonic_span_s"], 0.0)
        self.assertGreater(record["placement_bound_s"], 0.005)
        self.assertGreater(record["stamp_resolution_s"], 0.005)

    # -- regression 11 -----------------------------------------------------
    def test_lawful_rate_over_a_long_capture_still_trips_the_backstop(self) -> None:
        """20 ppm is admissible; 20 ppm for 900 s is 18 ms of drift and is not.

        Deleting the backstop would leave this capture bounded, with 18 ms of
        unpriced rigid shift (0.72 J at the 40 W loaded bracket edge).
        """
        stamps, records = self.synthetic(rate_ppm=20, duration_s=900)
        record = self.v3_1(stamps=stamps, records=records)
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["detail"], "wall_minus_monotonic_span_exceeded")
        self.assertAlmostEqual(record["wall_minus_monotonic_span_s"], 0.01802,
                               places=5)
        self.assertLess(record["wall_minus_monotonic_rate_ppm"], 25.0)

    # -- regression 12 (deriver half) --------------------------------------
    def test_caps_are_frozen_to_their_identity_and_never_caller_supplied(self) -> None:
        from joulewise.uncertainty_evidence import (
            ANCHOR_CAPS_BY_METHOD, CLOCK_METHOD_V3, CLOCK_METHOD_V3_1,
            SCHEMA_FOR_ANCHOR_METHOD, SCHEMA_VERSION_V3_1, V3_1_CAPS, V3_CAPS,
        )
        import inspect
        from joulewise.uncertainty_evidence import derive_powermetrics_anchor_v3

        self.assertEqual(set(ANCHOR_CAPS_BY_METHOD),
                         {CLOCK_METHOD_V3, CLOCK_METHOD_V3_1})
        with self.assertRaises(TypeError):
            ANCHOR_CAPS_BY_METHOD[CLOCK_METHOD_V3] = dict(V3_1_CAPS)
        with self.assertRaises(TypeError):
            V3_1_CAPS["max_sustained_rate_ppm"] = 1000.0
        self.assertEqual(dict(V3_CAPS), {
            "form": "absolute",
            "max_wall_minus_monotonic_span_s": 0.005,
            "max_effective_clock_anchor_bound_s": 0.005})
        self.assertEqual(dict(V3_1_CAPS), {
            "form": "rate_and_placement",
            "max_sustained_rate_ppm": 25.0,
            "max_placement_bound_s": 0.005,
            "max_wall_minus_monotonic_span_s": 0.015})
        self.assertEqual(SCHEMA_FOR_ANCHOR_METHOD[CLOCK_METHOD_V3_1],
                         SCHEMA_VERSION_V3_1)
        self.assertEqual(CLOCK_METHOD_V3_1,
                         "powermetrics_native_second_rate_aware_set_membership_v1.1")
        self.assertEqual(SCHEMA_VERSION_V3_1, "p2-038.4")
        # No caps argument exists: an identity is the only way to name limits.
        parameters = inspect.signature(derive_powermetrics_anchor_v3).parameters
        self.assertNotIn("caps", parameters)
        self.assertEqual(parameters["method"].default, CLOCK_METHOD_V3)
        fixture = pilot_envelope(2)
        stamps, records = pilot_stamps(fixture), pilot_records(fixture)
        with self.assertRaisesRegex(ValueError, "unregistered anchor method"):
            self.derive(stamps=stamps, records=records, method="v9")
        self.assertEqual(self.derive(stamps=stamps, records=records),
                         self.derive(stamps=stamps, records=records,
                                     method=CLOCK_METHOD_V3))

    def test_v3_1_emits_the_exact_integer_endpoint_of_its_own_midpoint(self) -> None:
        fixture = pilot_envelope(2)
        record = self.v3_1(stamps=pilot_stamps(fixture),
                           records=pilot_records(fixture))
        exact_ns = record["first_sample_end_point_epoch_ns"]
        self.assertIsInstance(exact_ns, int)
        # Within one float64 ulp at epoch scale of the recorded float field,
        # and not merely a re-rounding of it.
        self.assertLess(abs(exact_ns - record["first_sample_end_point_epoch_s"] * 1e9), 512)
        self.assertGreaterEqual(exact_ns, round(record["admissible_lower_epoch_s"] * 1e9))
        self.assertLessEqual(exact_ns, round(record["admissible_upper_epoch_s"] * 1e9))
