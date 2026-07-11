"""Tests for D-014 cross-repetition uncertainty aggregation."""

from __future__ import annotations

import json
import math
import statistics
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise.aggregate import aggregate_experiment, student_t_critical_95


STANDARD_METRICS = (
    "energy_request_j",
    "energy_token_j",
    "energy_output_token_j",
    "gross_energy_j",
    "idle_subtracted_energy_j",
    "ttft_s",
    "decode_latency_s",
    "throughput_tokens_s",
    "inter_token_throughput_tokens_s",
)


def _write_summary(runs_root: Path, member: str, summary: dict[str, Any]) -> None:
    bundle = runs_root / member
    bundle.mkdir(parents=True, exist_ok=True)
    bundle.joinpath("summary_metrics.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )


def _summary(value: Any, *, status: str = "succeeded", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": status, "energy_request_j": value}
    payload.update(extra)
    return payload


def _assert_strict_json_serializable(testcase: unittest.TestCase, value: Any) -> None:
    try:
        json.dumps(value, allow_nan=False)
    except ValueError as exc:
        testcase.fail(f"aggregate contains a non-finite JSON value: {exc}")


class AggregateTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.runs_root.mkdir()

    def aggregate_values(self, values: list[Any]) -> dict[str, Any]:
        members = []
        for index, value in enumerate(values, start=1):
            member = f"r{index}"
            members.append(member)
            _write_summary(self.runs_root, member, _summary(value))
        return aggregate_experiment(self.runs_root, {"members": members})


class ConfidenceIntervalTests(AggregateTestCase):
    def test_ci_math_matches_hand_computed_five_value_interval(self) -> None:
        aggregate = self.aggregate_values([10.0, 12.0, 14.0, 16.0, 18.0])
        metric = aggregate["metrics"]["energy_request_j"]

        expected_stddev = math.sqrt(10.0)
        expected_half_width = 2.776 * expected_stddev / math.sqrt(5.0)
        self.assertEqual(metric["method"], "mean_sample_stddev_student_t_95")
        self.assertEqual(metric["repetitions"], 5)
        self.assertAlmostEqual(metric["mean"], 14.0, places=12)
        self.assertAlmostEqual(metric["stddev"], expected_stddev, places=12)
        self.assertAlmostEqual(metric["lower"], 14.0 - expected_half_width, places=12)
        self.assertAlmostEqual(metric["upper"], 14.0 + expected_half_width, places=12)
        self.assertEqual(metric["interval_status"], "computed")
        self.assertTrue(metric["interval_available"])
        self.assertFalse(metric["below_headline_protocol"])
        self.assertFalse(metric["below_minimum_protocol"])

    def test_t_table_spot_checks_and_floor_fallback(self) -> None:
        self.assertEqual(student_t_critical_95(1), 12.706)
        self.assertEqual(student_t_critical_95(4), 2.776)
        self.assertEqual(student_t_critical_95(31), 2.042)
        self.assertEqual(student_t_critical_95(41), 2.021)
        self.assertEqual(student_t_critical_95(121), 1.980)
        with self.assertRaisesRegex(ValueError, "df"):
            student_t_critical_95(0)

    def test_n_two_uses_df_one_interval(self) -> None:
        aggregate = self.aggregate_values([10.0, 12.0])
        metric = aggregate["metrics"]["energy_request_j"]

        expected_stddev = math.sqrt(2.0)
        expected_half_width = 12.706 * expected_stddev / math.sqrt(2.0)
        self.assertEqual(metric["repetitions"], 2)
        self.assertAlmostEqual(metric["mean"], 11.0, places=12)
        self.assertAlmostEqual(metric["stddev"], expected_stddev, places=12)
        self.assertAlmostEqual(metric["lower"], 11.0 - expected_half_width, places=12)
        self.assertAlmostEqual(metric["upper"], 11.0 + expected_half_width, places=12)
        self.assertEqual(metric["interval_status"], "computed")
        self.assertTrue(metric["interval_available"])
        self.assertTrue(metric["below_headline_protocol"])
        self.assertTrue(metric["below_minimum_protocol"])

    def test_zero_variance_values_have_point_interval_and_mad_zero_status(self) -> None:
        aggregate = self.aggregate_values([7.5, 7.5, 7.5, 7.5, 7.5])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["repetitions"], 5)
        self.assertEqual(metric["mean"], 7.5)
        self.assertEqual(metric["stddev"], 0.0)
        self.assertEqual(metric["lower"], 7.5)
        self.assertEqual(metric["upper"], 7.5)
        self.assertEqual(metric["interval_status"], "computed")
        self.assertTrue(metric["interval_available"])
        self.assertEqual(metric["outlier_method_status"], "mad_zero_all_equal")
        self.assertEqual(metric["outliers"], [])

    def test_negative_and_mixed_sign_values_aggregate_normally(self) -> None:
        aggregate = self.aggregate_values([-5.0, -3.0, 0.0, 2.0, 4.0])
        metric = aggregate["metrics"]["energy_request_j"]

        expected_stddev = statistics.stdev([-5.0, -3.0, 0.0, 2.0, 4.0])
        expected_half_width = 2.776 * expected_stddev / math.sqrt(5.0)
        self.assertEqual(metric["repetitions"], 5)
        self.assertAlmostEqual(metric["mean"], -0.4, places=12)
        self.assertAlmostEqual(metric["stddev"], expected_stddev, places=12)
        self.assertAlmostEqual(metric["lower"], -0.4 - expected_half_width, places=12)
        self.assertAlmostEqual(metric["upper"], -0.4 + expected_half_width, places=12)
        self.assertEqual(metric["interval_status"], "computed")

    def test_t_table_boundaries_and_floor_fallbacks(self) -> None:
        cases = {
            30: 2.042,
            31: 2.042,
            40: 2.021,
            41: 2.021,
            60: 2.000,
            61: 2.000,
            120: 1.980,
            121: 1.980,
            10_000: 1.980,
        }
        for df, expected in cases.items():
            with self.subTest(df=df):
                self.assertEqual(student_t_critical_95(df), expected)
        for df in (0, -1):
            with self.subTest(df=df):
                with self.assertRaisesRegex(ValueError, "df"):
                    student_t_critical_95(df)


class ProtocolLadderTests(AggregateTestCase):
    def test_n_ladder_flags_are_explicit(self) -> None:
        cases = [
            (0, [], False, True, True),
            (1, [10.0], False, True, True),
            (2, [10.0, 12.0], True, True, True),
            (3, [10.0, 12.0, 14.0], True, True, False),
            (5, [10.0, 12.0, 14.0, 16.0, 18.0], True, False, False),
        ]
        for n, values, interval_available, below_headline, below_minimum in cases:
            with self.subTest(n=n):
                aggregate = self.aggregate_values(values)
                metric = aggregate["metrics"]["energy_request_j"]
                self.assertEqual(metric["repetitions"], n)
                self.assertIs(metric["interval_available"], interval_available)
                self.assertIs(metric["below_headline_protocol"], below_headline)
                self.assertIs(metric["below_minimum_protocol"], below_minimum)
                if n == 0:
                    self.assertIsNone(metric["mean"])
                    self.assertIsNone(metric["stddev"])
                    self.assertIsNone(metric["lower"])
                    self.assertIsNone(metric["upper"])
                    self.assertEqual(metric["interval_status"], "unavailable")
                elif n == 1:
                    self.assertEqual(metric["mean"], 10.0)
                    self.assertIsNone(metric["stddev"])
                    self.assertIsNone(metric["lower"])
                    self.assertIsNone(metric["upper"])
                    self.assertEqual(metric["interval_status"], "unavailable")
                else:
                    self.assertIsNotNone(metric["stddev"])
                    self.assertIsNotNone(metric["lower"])
                    self.assertIsNotNone(metric["upper"])
                    self.assertEqual(metric["interval_status"], "computed")

    def test_n_one_entry_is_mean_only_with_all_flags_explicit(self) -> None:
        aggregate = self.aggregate_values([42.0])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["method"], "mean_sample_stddev_student_t_95")
        self.assertEqual(metric["repetitions"], 1)
        self.assertEqual(metric["mean"], 42.0)
        self.assertIsNone(metric["stddev"])
        self.assertIsNone(metric["lower"])
        self.assertIsNone(metric["upper"])
        self.assertEqual(metric["interval_status"], "unavailable")
        self.assertIs(metric["interval_available"], False)
        self.assertIs(metric["below_headline_protocol"], True)
        self.assertIs(metric["below_minimum_protocol"], True)


class OutlierTests(AggregateTestCase):
    def test_modified_z_outlier_is_flagged_but_kept_in_headline(self) -> None:
        aggregate = self.aggregate_values([10.0, 11.0, 12.0, 13.0, 100.0])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["outlier_method"], "modified_z_mad_3.5")
        self.assertEqual(metric["outlier_method_status"], "computed")
        self.assertEqual(metric["outlier_count"], 1)
        self.assertEqual(metric["outliers"][0]["member"], "r5")
        self.assertEqual(metric["outliers"][0]["value"], 100.0)
        self.assertAlmostEqual(metric["outliers"][0]["modified_z"], 59.356, places=12)
        self.assertTrue(metric["headline_includes_outliers"])
        self.assertAlmostEqual(metric["mean"], 29.2, places=12)
        expected_stddev = math.sqrt(
            sum((value - 29.2) ** 2 for value in [10.0, 11.0, 12.0, 13.0, 100.0])
            / 4.0
        )
        expected_half_width = 2.776 * expected_stddev / math.sqrt(5.0)
        self.assertAlmostEqual(metric["stddev"], expected_stddev, places=12)
        self.assertAlmostEqual(metric["lower"], 29.2 - expected_half_width, places=12)
        self.assertAlmostEqual(metric["upper"], 29.2 + expected_half_width, places=12)

    def test_negative_modified_z_outlier_is_flagged(self) -> None:
        aggregate = self.aggregate_values([10.0, 11.0, 12.0, 13.0, -100.0])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["outlier_method_status"], "computed")
        self.assertEqual(metric["outlier_count"], 1)
        self.assertEqual(metric["outliers"][0]["member"], "r5")
        self.assertEqual(metric["outliers"][0]["value"], -100.0)
        self.assertLess(metric["outliers"][0]["modified_z"], -3.5)

    def test_mad_zero_path_records_status_without_fake_z_scores(self) -> None:
        # P2-040 FIX-5: MAD zero with an off-median point emits a review-only
        # flag with modified_z=null instead of hiding it.
        aggregate = self.aggregate_values([5.0, 5.0, 5.0, 100.0])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["outlier_method_status"], "mad_zero_fallback_applied")
        self.assertEqual(metric["outlier_count"], 1)
        flag = metric["outliers"][0]
        self.assertEqual(flag["member"], "r4")
        self.assertEqual(flag["value"], 100.0)
        self.assertIsNone(flag["modified_z"])
        self.assertEqual(flag["flag_basis"], "mad_zero_off_median_review")
        self.assertIs(flag["review_only"], True)
        self.assertTrue(metric["headline_includes_outliers"])

    def test_zero_mad_fallback_flags_off_median_point_but_keeps_it_in_headline(self) -> None:
        # P2-040 FIX-5 mutation test: [5,5,5,5,100] flags r5 for review while
        # the headline aggregate keeps every point.
        aggregate = self.aggregate_values([5.0, 5.0, 5.0, 5.0, 100.0])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["outlier_method_status"], "mad_zero_fallback_applied")
        self.assertEqual(metric["outlier_count"], 1)
        flag = metric["outliers"][0]
        self.assertEqual(flag["member"], "r5")
        self.assertEqual(flag["value"], 100.0)
        self.assertIsNone(flag["modified_z"])
        self.assertEqual(flag["flag_basis"], "mad_zero_off_median_review")
        self.assertIs(flag["review_only"], True)
        self.assertTrue(metric["headline_includes_outliers"])
        self.assertAlmostEqual(metric["mean"], 24.0, places=12)
        self.assertEqual(metric["repetitions"], 5)
        # Keep-all interval: computed over all five points, flag excluded from
        # nothing.
        self.assertEqual(metric["interval_status"], "computed")
        self.assertLess(metric["lower"], 24.0)
        self.assertGreater(metric["upper"], 24.0)

    def test_extreme_outlier_modified_z_stays_finite(self) -> None:
        aggregate = self.aggregate_values([0.0, 1.0, 2.0, 3.0, 1.0e100])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["outlier_count"], 1)
        modified_z = metric["outliers"][0]["modified_z"]
        self.assertTrue(math.isfinite(modified_z))
        self.assertGreater(modified_z, 1.0e90)

    def test_even_n_tied_deviations_and_strict_threshold_boundary(self) -> None:
        # Even-n median is 2.5 and MAD is 1.5 with tied middle deviations; the
        # last value is constructed so its modified z-score is exactly the
        # D-014 threshold. The predicate is strict > 3.5, so it is not flagged.
        threshold_value = 2.5 + 3.5 * 1.5 / 0.6745
        aggregate = self.aggregate_values([0.0, 1.0, 2.0, 3.0, 4.0, threshold_value])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["outlier_method_status"], "computed")
        self.assertEqual(metric["outlier_count"], 0)
        self.assertEqual(metric["outliers"], [])

    def test_subnormal_mad_overflow_records_outlier_without_nonfinite_z(self) -> None:
        aggregate = self.aggregate_values([0.0, 5e-324, 1.0e308])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["outlier_method_status"], "computed")
        self.assertEqual(metric["outlier_count"], 1)
        self.assertEqual(metric["outliers"][0]["member"], "r3")
        self.assertEqual(metric["outliers"][0]["value"], 1.0e308)
        self.assertIsNone(metric["outliers"][0]["modified_z"])
        _assert_strict_json_serializable(self, aggregate)


class MissingAndMemberProblemTests(AggregateTestCase):
    def test_missing_metric_taxonomy(self) -> None:
        _write_summary(self.runs_root, "null", _summary(None))
        _write_summary(self.runs_root, "failed", {"status": "failed"})
        (self.runs_root / "bad").mkdir()
        (self.runs_root / "bad" / "summary_metrics.json").write_text("{not json")
        _write_summary(self.runs_root, "nonnumeric", _summary("not-a-number"))
        _write_summary(self.runs_root, "ok", _summary(12.0))

        aggregate = aggregate_experiment(
            self.runs_root,
            {"members": ["null", "failed", "bad", "nonnumeric", "ok"]},
        )
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["repetitions"], 1)
        self.assertTrue(metric["partial_metric"])
        self.assertEqual(
            {(item["member"], item["reason"]) for item in metric["missing"]},
            {
                ("null", "metric_null"),
                ("failed", "member_failed"),
                ("bad", "summary_unreadable"),
                ("nonnumeric", "metric_non_numeric"),
            },
        )
        self.assertEqual(
            aggregate["member_problems"],
            [{"member": "bad", "problem": "summary_metrics.json missing or unreadable"}],
        )

    def test_missing_metric_taxonomy_completion(self) -> None:
        _write_summary(self.runs_root, "unsupported", _summary(1.0, status="unsupported"))
        _write_summary(self.runs_root, "bool", _summary(True))
        _write_summary(self.runs_root, "invalid-status", _summary(2.0, status="weird"))
        _write_summary(self.runs_root, "missing-status", {"energy_request_j": 3.0})
        _write_summary(self.runs_root, "nan", _summary(float("nan")))
        _write_summary(self.runs_root, "inf", _summary(float("inf")))

        aggregate = aggregate_experiment(
            self.runs_root,
            {
                "members": [
                    "unsupported",
                    "bool",
                    "invalid-status",
                    "missing-status",
                    "nan",
                    "inf",
                ]
            },
        )
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(aggregate["members_unsupported"], 1)
        self.assertEqual(metric["repetitions"], 0)
        self.assertEqual(
            {(item["member"], item["reason"]) for item in metric["missing"]},
            {
                ("unsupported", "member_unsupported"),
                ("bool", "metric_non_numeric"),
                ("invalid-status", "summary_unreadable"),
                ("missing-status", "summary_unreadable"),
                ("nan", "metric_non_numeric"),
                ("inf", "metric_non_numeric"),
            },
        )
        self.assertEqual(
            {(item["member"], item["problem"]) for item in aggregate["member_problems"]},
            {
                ("invalid-status", "summary status missing or invalid"),
                ("missing-status", "summary status missing or invalid"),
            },
        )
        _assert_strict_json_serializable(self, aggregate)

    def test_member_name_structural_rejections_do_not_escape_runs_root(self) -> None:
        cases: list[tuple[Any, str]] = [
            ("", ""),
            (".", "."),
            ("..", ".."),
            ("a/b", "a/b"),
            ("a\\b", "a\\b"),
            (42, "42"),
        ]
        for member, reported_member in cases:
            with self.subTest(member=member):
                aggregate = aggregate_experiment(self.runs_root, {"members": [member]})
                metric = aggregate["metrics"]["energy_request_j"]

                self.assertEqual(aggregate["members_total"], 1)
                self.assertEqual(aggregate["members_read"], 0)
                self.assertEqual(
                    aggregate["member_problems"],
                    [{"member": reported_member, "problem": "invalid member name"}],
                )
                self.assertEqual(metric["repetitions"], 0)
                self.assertEqual(
                    metric["missing"],
                    [{"member": reported_member, "reason": "summary_unreadable"}],
                )

    def test_phase_metrics_are_discovered_from_successful_summaries(self) -> None:
        _write_summary(
            self.runs_root,
            "r1",
            _summary(1.0, phase_energy_j={"prefill": 10.0, "decode": 20.0}),
        )
        _write_summary(
            self.runs_root,
            "r2",
            _summary(2.0, phase_energy_j={"prefill": 12.0}),
        )

        aggregate = aggregate_experiment(self.runs_root, {"members": ["r1", "r2"]})

        self.assertIn("phase_energy_j.prefill", aggregate["metrics"])
        self.assertIn("phase_energy_j.decode", aggregate["metrics"])
        self.assertEqual(
            aggregate["metrics"]["phase_energy_j.prefill"]["repetitions"], 2
        )
        expected_stddev = math.sqrt(2.0)
        expected_half_width = 12.706 * expected_stddev / math.sqrt(2.0)
        prefill = aggregate["metrics"]["phase_energy_j.prefill"]
        self.assertAlmostEqual(prefill["mean"], 11.0, places=12)
        self.assertAlmostEqual(prefill["stddev"], expected_stddev, places=12)
        self.assertAlmostEqual(prefill["lower"], 11.0 - expected_half_width, places=12)
        self.assertAlmostEqual(prefill["upper"], 11.0 + expected_half_width, places=12)
        self.assertEqual(aggregate["metrics"]["phase_energy_j.decode"]["repetitions"], 1)
        self.assertEqual(aggregate["metrics"]["phase_energy_j.decode"]["mean"], 20.0)
        self.assertEqual(
            aggregate["metrics"]["phase_energy_j.decode"]["missing"],
            [{"member": "r2", "reason": "metric_null"}],
        )

    def test_plain_missing_member_directory_is_structured_unreadable(self) -> None:
        aggregate = aggregate_experiment(self.runs_root, {"members": ["missing-dir"]})
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(aggregate["members_total"], 1)
        self.assertEqual(aggregate["members_read"], 0)
        self.assertEqual(
            aggregate["member_problems"],
            [
                {
                    "member": "missing-dir",
                    "problem": "summary_metrics.json missing or unreadable",
                }
            ],
        )
        self.assertEqual(metric["repetitions"], 0)
        self.assertEqual(
            metric["missing"],
            [{"member": "missing-dir", "reason": "summary_unreadable"}],
        )

    def test_mixed_status_counts_and_metric_missing_reason(self) -> None:
        _write_summary(self.runs_root, "ok", _summary(3.0))
        _write_summary(
            self.runs_root,
            "failed",
            {
                "status": "failed",
                "failure_reason": "unknown_error",
                "failure_message": "synthetic failure",
            },
        )

        aggregate = aggregate_experiment(self.runs_root, {"members": ["ok", "failed"]})
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(aggregate["members_total"], 2)
        self.assertEqual(aggregate["members_read"], 2)
        self.assertEqual(aggregate["members_succeeded"], 1)
        self.assertEqual(aggregate["members_failed"], 1)
        self.assertEqual(aggregate["members_unsupported"], 0)
        self.assertEqual(metric["repetitions"], 1)
        self.assertEqual(metric["missing"], [{"member": "failed", "reason": "member_failed"}])

    def test_standard_metrics_are_aggregated_independently(self) -> None:
        _write_summary(
            self.runs_root,
            "r1",
            {
                "status": "succeeded",
                "energy_request_j": 10.0,
                "energy_token_j": 1.0,
                "energy_output_token_j": 2.0,
                "gross_energy_j": 100.0,
                "idle_subtracted_energy_j": 90.0,
                "ttft_s": 0.5,
                "decode_latency_s": 1.5,
                "throughput_tokens_s": 20.0,
                "inter_token_throughput_tokens_s": 17.5,
            },
        )
        _write_summary(
            self.runs_root,
            "r2",
            {
                "status": "succeeded",
                "energy_request_j": 20.0,
                "energy_token_j": 3.0,
                "energy_output_token_j": 6.0,
                "gross_energy_j": 140.0,
                "idle_subtracted_energy_j": 110.0,
                "ttft_s": 0.7,
                "decode_latency_s": 2.5,
                "throughput_tokens_s": 30.0,
                "inter_token_throughput_tokens_s": 27.5,
            },
        )

        aggregate = aggregate_experiment(self.runs_root, {"members": ["r1", "r2"]})

        for metric_name in STANDARD_METRICS:
            self.assertIn(metric_name, aggregate["metrics"])
        expected_means = {
            "energy_request_j": 15.0,
            "energy_token_j": 2.0,
            "energy_output_token_j": 4.0,
            "gross_energy_j": 120.0,
            "idle_subtracted_energy_j": 100.0,
            "ttft_s": 0.6,
            "decode_latency_s": 2.0,
            "throughput_tokens_s": 25.0,
            "inter_token_throughput_tokens_s": 22.5,
        }
        for metric_name, expected_mean in expected_means.items():
            with self.subTest(metric=metric_name):
                self.assertAlmostEqual(
                    aggregate["metrics"][metric_name]["mean"],
                    expected_mean,
                    places=12,
                )

    def test_phase_metric_partial_and_non_numeric_values(self) -> None:
        _write_summary(
            self.runs_root,
            "phase-ok",
            _summary(1.0, phase_energy_j={"prefill": 10.0, "decode": "bad"}),
        )
        _write_summary(
            self.runs_root,
            "phase-missing",
            _summary(2.0, phase_energy_j={"decode": 5.0}),
        )

        aggregate = aggregate_experiment(
            self.runs_root,
            {"members": ["phase-ok", "phase-missing"]},
        )
        prefill = aggregate["metrics"]["phase_energy_j.prefill"]
        decode = aggregate["metrics"]["phase_energy_j.decode"]

        self.assertTrue(prefill["partial_metric"])
        self.assertEqual(prefill["repetitions"], 1)
        self.assertEqual(
            prefill["missing"],
            [{"member": "phase-missing", "reason": "metric_null"}],
        )
        self.assertTrue(decode["partial_metric"])
        self.assertEqual(decode["repetitions"], 1)
        self.assertEqual(
            decode["missing"],
            [{"member": "phase-ok", "reason": "metric_non_numeric"}],
        )


class ManifestShapeTests(AggregateTestCase):
    def test_aggregate_json_round_trip_is_exact_and_recomputable(self) -> None:
        _write_summary(self.runs_root, "r1", _summary(1.25))
        _write_summary(self.runs_root, "r2", _summary(2.5))
        manifest = {"experiment_id": "round-trip", "members": ["r1", "r2"]}

        aggregate = aggregate_experiment(self.runs_root, manifest)
        round_tripped = json.loads(json.dumps(aggregate, sort_keys=True))

        self.assertEqual(round_tripped, aggregate)
        manifest["aggregate"] = {"poison": "must be ignored"}
        self.assertEqual(aggregate_experiment(self.runs_root, manifest), aggregate)

    def test_non_prefix_member_subset_uses_listed_member_identities(self) -> None:
        _write_summary(self.runs_root, "r1", _summary(10.0))
        _write_summary(self.runs_root, "r2", _summary(1000.0))
        _write_summary(self.runs_root, "r3", _summary(30.0))

        aggregate = aggregate_experiment(self.runs_root, {"members": ["r1", "r3"]})
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(aggregate["members_total"], 2)
        self.assertEqual(metric["repetitions"], 2)
        self.assertAlmostEqual(metric["mean"], 20.0, places=12)

    def test_huge_json_int_is_metric_non_numeric_not_crash(self) -> None:
        _write_summary(self.runs_root, "huge", _summary(10**400))

        aggregate = aggregate_experiment(self.runs_root, {"members": ["huge"]})
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["repetitions"], 0)
        self.assertEqual(
            metric["missing"],
            [{"member": "huge", "reason": "metric_non_numeric"}],
        )
        _assert_strict_json_serializable(self, aggregate)

    def test_extreme_spread_nulls_nonfinite_interval(self) -> None:
        aggregate = self.aggregate_values([-1.0e308, 1.0e308])
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["repetitions"], 2)
        self.assertEqual(metric["mean"], 0.0)
        self.assertIsNone(metric["stddev"])
        self.assertIsNone(metric["lower"])
        self.assertIsNone(metric["upper"])
        self.assertFalse(metric["interval_available"])
        self.assertEqual(metric["interval_status"], "non_finite_overflow")
        self.assertTrue(metric["below_headline_protocol"])
        self.assertTrue(metric["below_minimum_protocol"])
        _assert_strict_json_serializable(self, aggregate)

    def test_degenerate_manifest_member_shapes_are_structured(self) -> None:
        cases = [
            ({}, 0),
            ({"members": "r1"}, 0),
            ({"members": []}, 0),
        ]
        for manifest, expected_total in cases:
            with self.subTest(manifest=manifest):
                aggregate = aggregate_experiment(self.runs_root, manifest)
                metric = aggregate["metrics"]["energy_request_j"]
                self.assertEqual(aggregate["members_total"], expected_total)
                self.assertEqual(aggregate["members_read"], 0)
                self.assertEqual(aggregate["members_succeeded"], 0)
                self.assertEqual(aggregate["member_problems"], [])
                self.assertEqual(metric["repetitions"], 0)
                self.assertFalse(metric["interval_available"])
                self.assertEqual(metric["interval_status"], "unavailable")
                self.assertTrue(metric["below_headline_protocol"])
                self.assertTrue(metric["below_minimum_protocol"])


if __name__ == "__main__":
    unittest.main()
