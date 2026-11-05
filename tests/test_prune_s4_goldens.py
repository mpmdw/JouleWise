"""Synthetic behavior goldens to run before and after Stage 4 pruning.

These do not certify a census of sealed records. Legacy identities are tested
through readers, without invoking their historical computation. The clamp
adapter currently targets whole_window; after the ruled canonical clamp lands,
only that adapter should need changing, never the expected numbers.
"""

from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_manifest as manifest_v1
from joulewise import analysis_manifest_v2 as manifest_v2
from joulewise import reduce as reducer
from joulewise.bundle_read import BundleReader, TracePoint, Window
from joulewise.schemas import summary_validation_problems
from joulewise.whole_window import (
    _clamped_corner_composed_anchor_shift_envelope as clamp,
)
from tests.oracle_l9_env_2_reduce_clamp import (
    _corner_composed_anchor_shift_envelope as parked_clamp,
)


ROOT = Path(__file__).resolve().parents[1]
METHOD = "common_trace_shift_plus_independent_edge_corners_v3"
LEGACY_VERSIONS = ("0.4.1", "0.4.2", "0.5.0", "0.5.1")
AXI_VERSIONS = ("0.6.0", "0.6.1", "0.6.2")


def envelope(point, lower, upper, independent, *, bound=1.25, span=0.25):
    """Hand-calculated expected values; no production arithmetic is used."""
    return {
        "method": METHOD,
        "anchor_bound_s": bound,
        "point_j": point,
        "lower_j": lower,
        "upper_j": upper,
        "max_abs_delta_j": max(point - lower, upper - point),
        "wall_minus_monotonic_independent_edge_span_s": span,
        "independent_edge_shift_bound_j": independent,
    }


def point_curve(power=10.0, epoch=0.0):
    return [TracePoint(epoch + t, power) for t in (-8.0, 0.0, 8.0)]


def legacy_summary(version):
    # A hand-authored successful v0.1 record, not output from an old reducer.
    return {
        "status": "succeeded",
        "energy_request_j": 8.0,
        "energy_token_j": 2.0,
        "energy_output_token_j": 4.0,
        "gross_energy_j": 10.0,
        "idle_subtracted_energy_j": 8.0,
        "ttft_s": 0.5,
        "decode_latency_s": 2.0,
        "throughput_tokens_s": 1.0,
        "idle_baseline": None,
        "uncertainty": None,
        "measurement_quality": None,
        "phase_energy_j": {"prefill": 4.0, "decode": 6.0},
        "failure_reason": None,
        "failure_message": None,
        "summary_provenance": {
            "summary_schema_version": "0.1",
            "reducer_id": "joulewise.reduce_bundle",
            "reducer_version": version,
            "config_schema_version": "0.1",
        },
    }


def registry_v1():
    # Synthetic registry declarations only; no source manifest or data paths.
    return {
        "schema_version": "joulewise.analysis_registry.v1",
        "registry_id": "slice_2m_ap2_v1",
        "freeze_status": "frozen",
        "plan_id": "AP-2",
        "family_id": "FAM-2M-SHAPE-CONTRASTS",
        "claim_role": "primary",
        "sampling_plan": {
            "design": "fixed_n",
            "planned_n_blocks": 5,
            "freeze_basis": "window_a_variance_mde_before_campaign_execution",
        },
        "multiplicity": {"method": "holm", "alpha": 0.05, "q": None},
        "metrics": [
            {"metric_tag": tag, "name": name, "window_class": window,
             "unit": "J", "ratio_estimand": None}
            for tag, name, window in (
                ("gross_request", "gross_energy_j", "request"),
                ("idle_request", "energy_request_j", "request"),
                ("gross_prefill", "phase_energy_j.prefill", "phase"),
                ("gross_decode", "phase_energy_j.decode", "phase"),
            )
        ],
        "condition_pairs": [
            {"condition_a": a, "condition_b": b}
            for a, b in (
                ("short_short", "long_short"), ("short_short", "short_long"),
                ("short_short", "mid_mid"), ("long_short", "short_long"),
                ("long_short", "mid_mid"), ("short_long", "mid_mid"),
            )
        ],
    }


class ClampGoldenTests(unittest.TestCase):
    def assert_golden(self, contributions, bounds, expected):
        actual = clamp(contributions, *bounds)
        self.assertEqual(actual, expected)
        self.assertEqual(json.dumps(actual), json.dumps(expected))
        # Independent test-only implementation of the parked ruled clamp.
        self.assertEqual(parked_clamp(contributions, *bounds), expected)

    def test_short_equal_long_and_zero_windows(self):
        # 10 W constant power. Edge uncertainty is 1 s, common shift 0.25 s.
        for start, end, expected in (
            (2.0, 3.0, envelope(10.0, 0.0, 30.0, 20.0)),
            (2.0, 4.0, envelope(20.0, 0.0, 40.0, 20.0)),
            (2.0, 6.0, envelope(40.0, 20.0, 60.0, 20.0)),
            (3.0, 3.0, envelope(0.0, 0.0, 20.0, 20.0)),
        ):
            with self.subTest(start=start, end=end):
                self.assert_golden(
                    [(point_curve(), [Window(start, end)])],
                    (0.25, 0.75, 0.25), expected,
                )

    def test_interval_support_and_large_epoch_preserve_exact_values(self):
        for epoch in (0.0, 1_800_000_000.0):
            curve = [
                TracePoint(epoch, 10.0, epoch - 8.0, epoch),
                TracePoint(epoch + 8.0, 10.0, epoch, epoch + 8.0),
            ]
            with self.subTest(epoch=epoch):
                self.assert_golden(
                    [(curve, [Window(epoch + 2.0, epoch + 3.0)])],
                    (0.25, 0.75, 0.25), envelope(10.0, 0.0, 30.0, 20.0),
                )

    def test_multiple_intervals_and_sources_share_the_shift(self):
        self.assert_golden(
            [(point_curve(), [Window(2.0, 3.0), Window(4.0, 6.0)])],
            (0.25, 0.75, 0.25), envelope(30.0, 0.0, 70.0, 40.0),
        )
        self.assert_golden(
            [(point_curve(), [Window(2.0, 3.0)]),
             (point_curve(4.0), [Window(4.0, 6.0)])],
            (0.25, 0.75, 0.25), envelope(18.0, 0.0, 46.0, 28.0),
        )

    def test_nonconstant_trace_has_an_interior_extremum(self):
        # Triangle of total area 16 J. Integrate by subtracting the two tails.
        self.assert_golden(
            [([TracePoint(0.0, 0.0), TracePoint(2.0, 8.0), TracePoint(4.0, 0.0)],
              [Window(1.0, 3.0)])],
            (0.25, 0.25, 0.0),
            envelope(12.0, 9.5, 13.75, 2.25, bound=0.5, span=0.0),
        )

    def test_noninverting_result_matches_the_current_reducer(self):
        contributions = [(point_curve(), [Window(2.0, 6.0)])]
        expected = envelope(40.0, 20.0, 60.0, 20.0)
        self.assertEqual(
            reducer._corner_composed_anchor_shift_envelope(
                contributions, 0.25, 0.75, 0.25), expected,
        )
        self.assert_golden(contributions, (0.25, 0.75, 0.25), expected)

    def test_invalid_inputs_and_uncovered_trace_still_refuse(self):
        valid = [(point_curve(), [Window(2.0, 3.0)])]
        for bounds in ((None, 0.75, 0.25), (0.25, None, 0.25),
                       (-0.25, 0.75, 0.25), (0.25, -0.75, 0.25),
                       (math.nan, 0.75, 0.25), (0.25, math.inf, 0.25),
                       (0.25, 0.75, -0.25), (0.25, 0.75, math.inf)):
            with self.subTest(bounds=bounds):
                self.assertIsNone(clamp(valid, *bounds))
        for contributions in (
            [], [([], [Window(2.0, 3.0)])], [(point_curve(), [])],
            [(point_curve(-1.0), [Window(2.0, 3.0)])],
            [(point_curve(), [Window(3.0, 2.0)])],
            [([TracePoint(2.0, 10.0), TracePoint(3.0, 10.0)], [Window(2.0, 3.0)])],
        ):
            with self.subTest(contributions=contributions):
                self.assertIsNone(clamp(contributions, 0.25, 0.75, 0.25))


class SyntheticBundleCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="prune-s4-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def reader(self, *, axi=False, summary=None):
        (self.root / "config.json").write_text(json.dumps(
            {"schema_extensions": ["joulewise.axi_decode_config.v1"]} if axi else {}
        ))
        (self.root / "metadata.json").write_text(json.dumps(
            {"event_semantics_version": "joulewise.events.v2"} if axi else {}
        ))
        if summary is not None:
            (self.root / "summary_metrics.json").write_text(json.dumps(summary))
        return BundleReader(self.root)


class CurrentVersionRoutingGoldenTests(SyntheticBundleCase):
    def test_new_bundles_select_current_versions(self):
        for axi, version in ((False, "0.5.2"), (True, "0.6.2")):
            with self.subTest(axi=axi):
                reader = self.reader(axi=axi)
                self.assertEqual(reducer._resolve_reducer_version(reader, None), version)
                self.assertEqual(reducer._resolve_reducer_version(reader, version), version)

    def test_finalized_current_identity_routes_unchanged(self):
        for axi, version in ((False, "0.5.2"), (True, "0.6.2")):
            with self.subTest(axi=axi):
                reader = self.reader(axi=axi, summary={
                    "summary_provenance": {"reducer_version": version}})
                self.assertEqual(reducer._resolve_reducer_version(reader, None), version)

    def test_missing_finalized_identity_and_unknown_version_refuse(self):
        reader = self.reader(axi=True, summary={"status": "succeeded"})
        with self.assertRaisesRegex(reducer.ReducerVersionError, "refuses to guess"):
            reducer._resolve_reducer_version(reader, None)
        with self.assertRaisesRegex(reducer.ReducerVersionError, "unsupported reducer version"):
            reducer._resolve_reducer_version(reader, "99.0.0")

    def test_current_versions_cannot_cross_event_semantics(self):
        for axi, version in ((False, "0.6.2"), (True, "0.5.2")):
            with self.subTest(axi=axi):
                with self.assertRaises(reducer.ReducerVersionError):
                    reducer._resolve_reducer_version(self.reader(axi=axi), version)


class StoredSummaryReaderGoldenTests(SyntheticBundleCase):
    def assert_readable_without_computing(self, value, *, axi=False):
        reader = self.reader(axi=axi, summary=value)
        path = self.root / "summary_metrics.json"
        before = path.read_bytes()
        with mock.patch.object(reducer, "reduce_bundle", side_effect=AssertionError(
            "a stored-format reader must not re-run any reducer")):
            observed = reader.raw_summary()
            self.assertEqual(observed, value)
            self.assertEqual(summary_validation_problems(observed), [])
        self.assertEqual(path.read_bytes(), before)

    def test_all_legacy_and_current_non_axi_identities_remain_readable(self):
        for version in (*LEGACY_VERSIONS, "0.5.2"):
            with self.subTest(version=version):
                self.assert_readable_without_computing(legacy_summary(version))

    def test_all_axi_identities_keep_their_stored_burst_fields(self):
        for version in AXI_VERSIONS:
            with self.subTest(version=version):
                # Existing hand-authored synthetic golden; no historical mint.
                value = json.loads((ROOT / "tests/goldens/axi_summary_v060.json").read_bytes())
                value["summary_provenance"]["reducer_version"] = version
                self.assert_readable_without_computing(value, axi=True)

    def test_unknown_stored_identity_is_read_verbatim_but_not_admitted(self):
        value = legacy_summary("99.0.0")
        reader = self.reader(summary=value)
        self.assertEqual(reader.raw_summary(), value)
        self.assertEqual(summary_validation_problems(value), [
            "summary provenance reducer_version is unsupported: '99.0.0'"])

    def test_stored_axi_identity_cannot_lose_its_event_pairing(self):
        value = json.loads((ROOT / "tests/goldens/axi_summary_v060.json").read_bytes())
        value["summary_provenance"].pop("event_semantics_version")
        self.assertEqual(summary_validation_problems(value), [
            "summary provenance reducer/event semantics pairing is invalid: "
            "0.6.0 requires 'joulewise.events.v2'"])


class StoredRegistryReaderGoldenTests(unittest.TestCase):
    def test_frozen_v1_declarations_keep_both_reader_results(self):
        value = registry_v1()
        before = copy.deepcopy(value)
        self.assertEqual(manifest_v1.validate_analysis_registry(value), [])
        self.assertEqual(manifest_v2.validate_analysis_registry(value), [])
        self.assertEqual(value, before)

    def test_successor_declarations_still_need_the_v2_reader(self):
        value = registry_v1()
        value["metrics"].append({
            "metric_tag": "idle_subtracted_request", "name": "idle_subtracted_energy_j",
            "window_class": "request", "unit": "J", "ratio_estimand": None,
        })
        before = copy.deepcopy(value)
        self.assertEqual(manifest_v1.validate_analysis_registry(value), [
            "registry.metrics: must contain the four frozen AP-2 metric rows"])
        self.assertEqual(manifest_v2.validate_analysis_registry(value), [])
        self.assertEqual(value, before)

    def test_unregistered_successor_metric_still_refuses(self):
        value = registry_v1()
        value["metrics"].append({
            "metric_tag": "unknown", "name": "phase_energy_j.unknown",
            "window_class": "phase", "unit": "J", "ratio_estimand": None,
        })
        self.assertEqual(manifest_v2.validate_analysis_registry(value), [
            "registry.metrics[4].name: not declared by the authenticated detection-floor registry"])


if __name__ == "__main__":
    unittest.main()
