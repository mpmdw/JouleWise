"""Tests for the P2-039 detection-floor calculator (D-054 false-effect guard).

Hand-computed fixtures come directly from the DRAFT spec
``docs/specs/c027/p2-039_floor_artifact.md`` Units 9.1/9.2 and the C-027
worked example.
"""

import json
import hashlib
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import joulewise.detection_floor as detection_floor
from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    COMMON_MODE_ESTIMATOR_ID,
    COMMON_MODE_PARAMETER_SHA256,
    CommonModeEstimatorRefusal,
    CONDITION_FAMILY_DOMAIN,
    FLOOR_METRIC_CATALOG,
    GUARD_MINIMUM_N,
    GUARD_REFERENCE_N,
    SCHEMA_VERSION,
    STACK_IDENTITY_DOMAIN,
    TRANSPORT_REASON_CODES,
    TRANSPORT_RULE_ID,
    abba_delta,
    absolute_false_effect_floor,
    build_absolute_record,
    build_comparative_record,
    build_floor_artifact,
    build_floor_cell,
    build_transport_group,
    canonical_domain_sha256,
    compose_transport_group,
    comparative_false_effect_floor,
    complete_bundle_sha256,
    registered_common_mode_operative_bound,
    small_sample_guard_factor,
    attribution_single_count_discipline,
    transport_refusal_reasons,
    two_shared_edge_common_mode_floor,
    two_shared_edge_common_mode_registration,
    validate_floor_artifact,
)
from joulewise.floor_extraction import (
    ANCHOR_FALLBACK_MEMBER_REFUSAL,
    CELL_REFUSAL_CODES,
    CellReport,
    EXTRACTION_SPEC_SCHEMA_VERSION,
    extract_absolute_cell,
    extract_cells,
)
from joulewise.whole_window import (
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    WholeWindowDriftAllowanceResult,
    neg8_claim_family_for_metric,
)

TOL = 1e-12
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
HEX_D = "d" * 64
MINT1_PLAN_ID = "p2-015-window-a-m3max-qwen25-1p5b-v1"
MINT1_PLAN_SHA256 = (
    "e529a0624b7618edaade511dd610ae0837f31de299dde642a055974c382681ab"
)
MINT1_TOOL_VERSION = "joulewise.floor_mint.v1"
MINT1_PINSET_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "floor_mint_pinsets"
    / "mint1.json"
)
MINT1_PINSET_SHA256 = (
    "4c58e64636863379f26bcf0fe03503ddfcf3bcf9bfa184fe0d385ca47b459a67"
)


def write_pinset(
    directory: Path,
    value: object,
    *,
    name: str = "pinset.json",
) -> tuple[Path, str]:
    raw = (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    path = directory / name
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


def whole_window_allowance(
    value=0.4,
    observed=0.3,
    derived=0.4,
    *,
    basis_sha256=HEX_C,
):
    return {
        "claim_family": "gross_energy",
        "allowance_j": value,
        "observed_trajectory_excursion_j": observed,
        "derived_repeatability_bound_j": derived,
        "provenance": {
            "bound_derivation_sha256": HEX_B,
            "observed_component": "trajectory_excursion_max_j",
            "derived_component": "derived_repeatability_bound_j",
        },
        "whole_window_evaluation_basis_sha256": basis_sha256,
    }


class TestCompleteBundleHash(unittest.TestCase):
    def test_hash_binds_all_regular_file_bytes_and_is_relocation_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first"
            second = root / "second"
            for bundle in (first, second):
                (bundle / "raw").mkdir(parents=True)
                (bundle / "metadata.json").write_text('{"value":1}\n', encoding="utf-8")
                (bundle / "raw" / "samples.bin").write_bytes(b"abc\x00def")
            original = complete_bundle_sha256(first)
            self.assertEqual(original, complete_bundle_sha256(second))
            (second / "raw" / "samples.bin").write_bytes(b"abc\x00changed")
            self.assertNotEqual(original, complete_bundle_sha256(second))

    def test_symlink_member_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            bundle.mkdir()
            (bundle / "payload").write_text("evidence\n", encoding="utf-8")
            (bundle / "alias").symlink_to("payload")
            with self.assertRaisesRegex(ValueError, "not a regular file"):
                complete_bundle_sha256(bundle)


class TestAnchorFallbackFloorMemberGate(unittest.TestCase):
    @staticmethod
    def _summary(value: float, *, fallback: bool = False) -> dict:
        return {
            "status": "succeeded",
            "summary_provenance": {"reducer_version": "0.5.2"},
            "measurement_quality": {
                "telemetry_source": "powermetrics",
                "cooldown_cap_hit": None,
                "idle_window_suspect": False,
            },
            "energy_uncertainty_status": (
                "not_estimable" if fallback else "bounded"
            ),
            "gross_energy_j": value,
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {
                    "method": "common_trace_shift_plus_independent_edge_corners_v3",
                    "anchor_bound_s": 0.01,
                    "point_j": value,
                    "lower_j": value - 0.01,
                    "upper_j": value + 0.01,
                    "max_abs_delta_j": 0.01,
                }
            },
            "window_evidence_precheck": {
                "gross_request": {
                    "eligible": not fallback,
                    "reasons": (
                        ["clock_anchor_unresolved"] if fallback else []
                    ),
                }
            },
        }

    @staticmethod
    def _write_member(
        root: Path, bundle_id: str, value: float, *, fallback: bool = False
    ) -> None:
        bundle = root / bundle_id
        bundle.mkdir()
        config = json.loads(
            Path("tests/fixtures/d078_r01/config.json").read_text(
                encoding="utf-8"
            )
        )
        config["run_id"] = bundle_id
        config_raw = (
            json.dumps(config, sort_keys=True) + "\n"
        ).encode("utf-8")
        (bundle / "config.json").write_bytes(config_raw)
        (bundle / "summary_metrics.json").write_text(
            json.dumps(
                TestAnchorFallbackFloorMemberGate._summary(
                    value, fallback=fallback
                ),
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        anchor = (
            {
                "status": "unresolved",
                "trace_fallback_method": "legacy_spawn_bracket_midpoint_v1",
            }
            if fallback
            else {"status": "bounded"}
        )
        (bundle / "metadata.json").write_text(
            json.dumps(
                {
                    "config_sha256": hashlib.sha256(config_raw).hexdigest(),
                    "adapters": {"telemetry": {"name": "powermetrics"}},
                    "uncertainty_evidence": {"clock_anchor": anchor},
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _extract(self, root: Path, values: list[float], *, fallback_at=None):
        bundle_ids = [f"member-{index}" for index in range(len(values))]
        for index, (bundle_id, value) in enumerate(
            zip(bundle_ids, values, strict=True)
        ):
            self._write_member(
                root,
                bundle_id,
                value,
                fallback=index == fallback_at,
            )
        cooldowns = {
            bundle_id: {"result": "recovered", "verified": True}
            for bundle_id in bundle_ids
        }
        with (
            patch(
                "joulewise.floor_extraction._cpu_admission_bundle_reasons",
                return_value=(),
            ),
            patch(
                "joulewise.floor_extraction.window_evidence_precheck",
                return_value={"eligible": True, "reasons": []},
            ),
            patch(
                "joulewise.floor_extraction.deterministic_bounds",
                return_value=(
                    {"E_interpolation_joint_edge_bound_j": 0.0},
                    (),
                ),
            ),
        ):
            return extract_absolute_cell(
                cell_id="anchor-member-gate",
                metric="gross_energy_j",
                window_class="request",
                members=[
                    {"slot": f"r{index + 1}", "bundle_id": bundle_id}
                    for index, bundle_id in enumerate(bundle_ids)
                ],
                runs_root=root,
                cooldowns=cooldowns,
                strict_validator=lambda path, strict: [],
            )

    def test_fallback_member_is_excluded_and_remaining_members_define_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            values = [10.0, 10.1, 10.2, 10.3, 10.4, 0.01]
            report = self._extract(root, values, fallback_at=5)
        self.assertTrue(report.extractable)
        self.assertEqual(report.n_admitted, 5)
        self.assertEqual(report.excluded_slots, ("r6",))
        excluded = next(member for member in report.members if member.excluded)
        self.assertIn(ANCHOR_FALLBACK_MEMBER_REFUSAL, excluded.reasons)
        self.assertIn(ANCHOR_FALLBACK_MEMBER_REFUSAL, CELL_REFUSAL_CODES)
        self.assertEqual(
            report.floor,
            absolute_false_effect_floor(
                values[:5], admissible_half_widths_j=[0.01] * 5
            ),
        )

    def test_fully_anchored_cell_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            values = [10.0, 10.1, 10.2, 10.3, 10.4, 10.5]
            report = self._extract(root, values)
        self.assertTrue(report.extractable)
        self.assertEqual(report.n_admitted, 6)
        self.assertEqual(report.excluded_slots, ())
        self.assertEqual(
            report.floor,
            absolute_false_effect_floor(
                values, admissible_half_widths_j=[0.01] * 6
            ),
        )


def condition_family(condition_id):
    definition = {
        "condition_id": condition_id,
        "comparison_policy": "same_condition_repeat",
    }
    return {
        "condition_family_id": condition_id,
        "condition_family_definition": definition,
        "condition_family_sha256": canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN, definition
        ),
    }


def make_stack_identity(**overrides):
    identity = {
        "hardware_unit": "mac-unit-1 / Apple M3 Max",
        "os_version": "macOS 15.5 (24F74)",
        "runtime_version": "mlx 1.0",
        "kernel_library": "metal/default",
        "model_artifact_sha256": HEX_C,
        "quantization": "none",
        "tokenizer_identity": "qwen2.5/revision-test/class-test/vocab-test",
        "sampler_output_policy": "greedy/max_new_tokens=64",
        "batching_concurrency_policy": "single-request sequential",
        "measurement_boundary_label": "wall-d018",
        "telemetry_backend": "powermetrics 14.0",
    }
    identity.update(overrides)
    return identity

# Spec Unit 9.1 (also the C-027 worked example).
FIXTURE_A_ENERGIES = [10.0, 10.0, 10.0, 10.0, 20.0]
FIXTURE_A_RESIDUALS = (-2.0, -2.0, -2.0, -2.0, 8.0)
FIXTURE_A_STDDEV = 4.472135954999580  # sqrt(20)
FIXTURE_A_PREDICTION = 13.599567051932203
FIXTURE_A_UNGUARDED = 13.599567051932203
FIXTURE_A_GUARDED = 20.399350577898304

# Spec Unit 9.2.
FIXTURE_B_BLOCKS = [
    ("b1", 100.0, 101.0, 103.0, 102.0, 1.0),
    ("b2", 100.0, 99.0, 101.0, 102.0, -1.0),
    ("b3", 100.0, 102.0, 104.0, 102.0, 2.0),
    ("b4", 100.0, 98.0, 100.0, 102.0, -2.0),
    ("b5", 100.0, 101.0, 101.0, 102.0, 0.0),
]
FIXTURE_B_DELTAS = [1.0, -1.0, 2.0, -2.0, 0.0]
FIXTURE_B_STDDEV = 1.581138830084190  # sqrt(2.5)
FIXTURE_B_PREDICTION = 4.808173041811203
FIXTURE_B_GUARDED = 7.212259562716805


def close(actual, expected):
    return abs(actual - expected) <= max(TOL, TOL * abs(expected))


class TestSmallSampleGuardFactor(unittest.TestCase):
    def test_spec_required_values_n5_to_n10(self):
        expected = {
            5: 1.5,
            6: 1.3416407864998738,
            7: 1.2247448713915890,
            8: 1.1338934190276817,
            9: 1.0606601717798212,
            10: 1.0,
        }
        for n, value in expected.items():
            self.assertTrue(
                math.isclose(small_sample_guard_factor(n), value, rel_tol=1e-15),
                msg=f"g({n})",
            )

    def test_exact_join_at_reference_n_and_above(self):
        self.assertEqual(small_sample_guard_factor(GUARD_REFERENCE_N), 1.0)
        self.assertEqual(small_sample_guard_factor(11), 1.0)
        self.assertEqual(small_sample_guard_factor(1000), 1.0)
        # Monotone nonincreasing on the guarded range.
        values = [small_sample_guard_factor(n) for n in range(5, 12)]
        self.assertEqual(values, sorted(values, reverse=True))

    def test_invalid_n_rejected(self):
        with self.assertRaises(ValueError):
            small_sample_guard_factor(GUARD_MINIMUM_N - 1)
        with self.assertRaises(TypeError):
            small_sample_guard_factor(True)
        with self.assertRaises(TypeError):
            small_sample_guard_factor(5.0)


class TestAbsoluteFloor(unittest.TestCase):
    def test_fixture_a_every_intermediate_value(self):
        est = absolute_false_effect_floor(
            FIXTURE_A_ENERGIES,
            admissible_half_widths_j=[0.0] * len(FIXTURE_A_ENERGIES),
        )
        self.assertEqual(est.n, 5)
        self.assertTrue(close(est.mean_j, 12.0))
        self.assertEqual(est.deviations_j, FIXTURE_A_RESIDUALS)
        self.assertTrue(close(est.sample_stddev_j, FIXTURE_A_STDDEV))
        self.assertTrue(close(est.max_abs_deviation_j, 8.0))
        self.assertTrue(close(est.t_critical, 2.776))
        self.assertTrue(close(est.prediction_component_j, FIXTURE_A_PREDICTION))
        self.assertTrue(close(est.unguarded_floor_j, FIXTURE_A_UNGUARDED))
        self.assertTrue(close(est.guard_factor, 1.5))
        self.assertTrue(close(est.guarded_floor_j, FIXTURE_A_GUARDED))

    def test_c027_worked_example(self):
        # C-027: energies [10,10,10,10,20] -> residuals [-2,-2,-2,-2,8],
        # s_r = sqrt(20), unguarded floor ~= 13.60 J.
        est = absolute_false_effect_floor(
            [10, 10, 10, 10, 20],
            admissible_half_widths_j=[0.0] * 5,
        )
        self.assertEqual(list(est.deviations_j), [-2, -2, -2, -2, 8])
        self.assertTrue(close(est.sample_stddev_j, math.sqrt(20)))
        self.assertAlmostEqual(est.unguarded_floor_j, 13.60, places=2)
        self.assertTrue(close(est.guarded_floor_j, FIXTURE_A_GUARDED))

    def test_guard_applied_after_max_not_inside(self):
        # n=9 with one large residual: max|r| = 8 dominates the prediction
        # component (~7.29). Applying g inside the max would give 8;
        # the spec's after-max rule gives g(9)*8.
        energies = [18.0] + [9.0] * 8
        est = absolute_false_effect_floor(
            energies,
            admissible_half_widths_j=[0.0] * len(energies),
        )
        self.assertEqual(est.n, 9)
        self.assertTrue(close(est.max_abs_deviation_j, 8.0))
        self.assertLess(est.prediction_component_j, 8.0)
        self.assertTrue(close(est.unguarded_floor_j, 8.0))
        after_max = small_sample_guard_factor(9) * 8.0
        inside_max = max(8.0, small_sample_guard_factor(9) * est.prediction_component_j)
        self.assertTrue(close(est.guarded_floor_j, after_max))
        self.assertGreater(est.guarded_floor_j, inside_max)

    def test_member_interval_corners_widen_residual_not_just_member_width(self):
        # G1 defect shape: ten alternating point energies have +/-0.5 J point
        # residuals, but independent +/-1 J member intervals can move one
        # member against the sample mean by 1.8 J.  The attainable residual is
        # therefore 0.5 + 1.8 = 2.3 J; the old max(widths)==1 shortcut missed it.
        energies = [99.5, 100.5] * 5
        estimate = absolute_false_effect_floor(
            energies,
            admissible_half_widths_j=[1.0] * 10,
        )
        self.assertGreaterEqual(estimate.unguarded_floor_j, 2.3 - TOL)

    def test_joint_corners_raise_full_floor_when_prediction_component_dominates(self):
        # K1 counterexample: the point floor is 3.2254 J guarded and the
        # round-4 linear-residual widening remains below it. A joint corner
        # instead maximizes the Student-t prediction term, so the COMPLETE
        # guarded floor must rise to 5.2008 J.
        energies = [101.0, 99.0, 100.0, 100.0, 100.0]
        point = absolute_false_effect_floor(
            energies,
            admissible_half_widths_j=[0.0] * len(energies),
        )
        widened = absolute_false_effect_floor(
            energies,
            admissible_half_widths_j=[0.5] * 5,
        )
        self.assertAlmostEqual(point.guarded_floor_j, 3.2254205307215367)
        self.assertGreaterEqual(widened.guarded_floor_j, 5.2008)

    def test_more_than_sixteen_nonzero_member_widths_refuse_approximation(self):
        with self.assertRaisesRegex(ValueError, "capped at n=16"):
            absolute_false_effect_floor(
                [100.0] * 17,
                admissible_half_widths_j=[0.5] * 17,
            )


    def test_below_five_is_smoke_only(self):
        est = absolute_false_effect_floor(
            [10.0, 12.0, 11.0],
            admissible_half_widths_j=[0.0] * 3,
        )
        self.assertIsNone(est.guard_factor)
        self.assertIsNone(est.guarded_floor_j)
        self.assertGreater(est.unguarded_floor_j, 0.0)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            absolute_false_effect_floor(
                [10.0, float("nan"), 11.0, 12.0, 13.0],
                admissible_half_widths_j=[0.0] * 5,
            )
        with self.assertRaises(ValueError):
            absolute_false_effect_floor(
                [10.0, float("inf"), 11.0, 12.0, 13.0],
                admissible_half_widths_j=[0.0] * 5,
            )
        with self.assertRaises(TypeError):
            absolute_false_effect_floor(
                [10.0, True, 11.0, 12.0, 13.0],
                admissible_half_widths_j=[0.0] * 5,
            )
        with self.assertRaises(ValueError):
            absolute_false_effect_floor(
                [10.0],
                admissible_half_widths_j=[0.0],
            )


class TestAbbaDelta(unittest.TestCase):
    def test_fixture_b_rows(self):
        for _, a1, b1, b2, a2, expected in FIXTURE_B_BLOCKS:
            self.assertTrue(close(abba_delta(a1, b1, b2, a2), expected))

    def test_sign_is_b_minus_a(self):
        self.assertEqual(abba_delta(0.0, 1.0, 1.0, 0.0), 1.0)
        self.assertEqual(abba_delta(1.0, 0.0, 0.0, 1.0), -1.0)

    def test_cancels_linear_position_drift(self):
        # Additive drift d per executed position, zero true effect:
        # A1=+d, B1=+2d, B2=+3d, A2=+4d -> delta must be exactly 0.
        d = 7.0
        base = 100.0
        self.assertEqual(abba_delta(base + d, base + 2 * d, base + 3 * d, base + 4 * d), 0.0)

    def test_nonfinite_member_rejected(self):
        with self.assertRaises(ValueError):
            abba_delta(1.0, float("nan"), 1.0, 1.0)


class TestComparativeFloor(unittest.TestCase):
    def test_fixture_b_every_intermediate_value(self):
        est = comparative_false_effect_floor(
            FIXTURE_B_DELTAS,
            admissible_half_widths_j=[0.0] * len(FIXTURE_B_DELTAS),
        )
        self.assertEqual(est.n, 5)
        self.assertTrue(close(est.mean_j, 0.0))
        self.assertTrue(close(est.sample_stddev_j, FIXTURE_B_STDDEV))
        self.assertTrue(close(est.max_abs_deviation_j, 2.0))
        self.assertTrue(close(est.t_critical, 2.776))
        self.assertTrue(close(est.prediction_component_j, FIXTURE_B_PREDICTION))
        self.assertTrue(close(est.unguarded_floor_j, FIXTURE_B_PREDICTION))
        self.assertTrue(close(est.guard_factor, 1.5))
        self.assertTrue(close(est.guarded_floor_j, FIXTURE_B_GUARDED))

    def test_block_interval_corner_widens_the_observed_delta(self):
        # A linear block contrast ranges over point_delta +/- sum(|c_i|w_i).
        # The operative floor must cover the point magnitude plus that width,
        # rather than comparing the width alone to the point-only floor.
        estimate = comparative_false_effect_floor(
            [2.0] * 5,
            admissible_half_widths_j=[1.0] * 5,
        )
        self.assertGreaterEqual(estimate.unguarded_floor_j, 3.0 - TOL)

    def test_joint_corners_raise_comparative_prediction_component(self):
        # K1 comparative counterexample derived from the same member-energy
        # pattern: point deltas [1,-1,0,0,0] have a 3.2254 J guarded floor,
        # while +/-0.5 J delta widths put the full corner maximum at 5.4468 J.
        deltas = [1.0, -1.0, 0.0, 0.0, 0.0]
        point = comparative_false_effect_floor(
            deltas,
            admissible_half_widths_j=[0.0] * len(deltas),
        )
        widened = comparative_false_effect_floor(
            deltas,
            admissible_half_widths_j=[0.5] * 5,
        )
        self.assertAlmostEqual(point.guarded_floor_j, 3.2254205307215367)
        self.assertGreaterEqual(widened.guarded_floor_j, 5.4468 - TOL)

    def test_label_swap_leaves_floor_unchanged(self):
        negated = [-d for d in FIXTURE_B_DELTAS]
        self.assertTrue(
            close(
                comparative_false_effect_floor(
                    negated,
                    admissible_half_widths_j=[0.0] * len(negated),
                ).guarded_floor_j,
                FIXTURE_B_GUARDED,
            )
        )

    def test_mean_shift_included_not_centered_away(self):
        # Fixture B deltas shifted by +1: same spread, mean 1. An
        # implementation that centers deltas first would reproduce the
        # fixture-B prediction; the spec requires abs(mean) to be added.
        shifted = [d + 1.0 for d in FIXTURE_B_DELTAS]
        est = comparative_false_effect_floor(
            shifted,
            admissible_half_widths_j=[0.0] * len(shifted),
        )
        self.assertTrue(close(est.mean_j, 1.0))
        self.assertTrue(close(est.sample_stddev_j, FIXTURE_B_STDDEV))
        self.assertTrue(close(est.prediction_component_j, 1.0 + FIXTURE_B_PREDICTION))
        self.assertGreater(est.prediction_component_j, FIXTURE_B_PREDICTION)


class TestTwoSharedEdgeCommonModeFloor(unittest.TestCase):
    # Exact a5 decode replay inputs/result promoted by D-124 (NON-CLAIM).
    REPLAY_DELTAS = [
        0.21462565134537215,
        0.40725474817919505,
        0.200636842871301,
        0.1818229541742724,
        -0.28350582988500506,
        -0.322865812458879,
        -0.12114331409931722,
        0.03839204680550168,
        0.17627096532869402,
        -0.05977483946883666,
    ]
    REPLAY_SHARED_WIDTHS = [
        0.26176933418208037,
        0.6153099135270779,
        0.5500344898387226,
        0.3842344343774471,
        0.24605527369687863,
        0.6026698109174475,
        0.18273227773791945,
        0.12636064142994385,
        0.1474527499846232,
        0.3727437267655951,
    ]
    REPLAY_LOCAL_WIDTHS = [
        0.048579253149348745,
        0.13567764585702236,
        0.08492622688504525,
        0.13637666530562242,
        0.042590466778161584,
        0.11543017866479133,
        0.13821068512976353,
        0.16019344030436855,
        0.031195747566393095,
        0.11402070739890391,
    ]
    REPLAY_TOTAL_WIDTHS = [
        0.3103485873314291,
        0.7509875593841002,
        0.6349607167237679,
        0.5206110996830695,
        0.2886457404750402,
        0.7180999895822389,
        0.320942962867683,
        0.2865540817343124,
        0.1786484975510163,
        0.486764434164499,
    ]
    ENDPOINT_BOUND_S = 0.025964638697819786
    ALLOWANCE_S = 0.010818
    OPERATIVE_BOUND_S = 0.03678263869781979

    @classmethod
    def bracket(cls) -> dict:
        return {
            "status": "passed",
            "endpoint_max_b_fiducial_s": cls.ENDPOINT_BOUND_S,
            "calibration_drift_allowance_s": cls.ALLOWANCE_S,
            "b_fiducial_s": cls.OPERATIVE_BOUND_S,
            "acceptance": {
                "allowance": {
                    "rule": "max(observed_drift_s,bracket_screen_s)",
                    "value_s": "0.010818",
                    "embedding_count": 1,
                    "embedded_in": "b_fiducial_s",
                }
            },
        }

    @classmethod
    def replay_inputs(cls):
        onset = [
            [delta, delta + width]
            for delta, width in zip(
                cls.REPLAY_DELTAS, cls.REPLAY_SHARED_WIDTHS, strict=True
            )
        ]
        offset = [[delta, delta] for delta in cls.REPLAY_DELTAS]
        residuals = [
            [2.0 * width, 0.0, 0.0, 0.0]
            for width in cls.REPLAY_LOCAL_WIDTHS
        ]
        return onset, offset, residuals

    def test_replay_arithmetic_pins_promoted_two_edge_floor(self):
        onset, offset, residuals = self.replay_inputs()
        estimate = two_shared_edge_common_mode_floor(
            self.REPLAY_DELTAS,
            onset_sweeps_j=onset,
            offset_sweeps_j=offset,
            bundle_residual_half_widths_j=residuals,
            calibration_bracket=self.bracket(),
            shared_edge_bound_s=self.OPERATIVE_BOUND_S,
        )
        self.assertEqual(
            estimate.admissible_half_widths_j,
            tuple(self.REPLAY_TOTAL_WIDTHS),
        )
        self.assertEqual(estimate.guarded_floor_j, 1.8695016260113408)
        self.assertEqual(
            estimate.estimator_registration,
            two_shared_edge_common_mode_registration(),
        )

    def test_identity_version_parameter_hash_and_assumption_are_stable(self):
        first = two_shared_edge_common_mode_registration()
        second = two_shared_edge_common_mode_registration()
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertEqual(first["estimator_id"], COMMON_MODE_ESTIMATOR_ID)
        self.assertEqual(first["version"], "v1")
        self.assertEqual(
            COMMON_MODE_PARAMETER_SHA256,
            "ea4aa669b8814ec6a267f924f02fe0c862edd14c33b2ecfd4ae5b4bf1e8c7480",
        )
        self.assertEqual(first["parameter_sha256"], COMMON_MODE_PARAMETER_SHA256)
        assumption = first["stationarity_transfer_assumption"]
        self.assertIn("COMMONMODE-REPLAY.md", assumption["evidence_reference"])
        self.assertIn(
            "bounds, not realized member-level boundary errors",
            assumption["evidentiary_limit"],
        )

    def test_double_allowance_application_refuses_with_typed_reason(self):
        bracket = self.bracket()
        bracket["b_fiducial_s"] = (
            self.ENDPOINT_BOUND_S + 2.0 * self.ALLOWANCE_S
        )
        with self.assertRaises(CommonModeEstimatorRefusal) as caught:
            registered_common_mode_operative_bound(bracket)
        self.assertEqual(
            caught.exception.reason,
            "common_mode_allowance_application_invalid",
        )

    def test_calibration_and_consumer_use_one_identical_code_path(self):
        onset, offset, residuals = self.replay_inputs()
        inputs = {
            "onset_sweeps_j": onset,
            "offset_sweeps_j": offset,
            "bundle_residual_half_widths_j": residuals,
            "calibration_bracket": self.bracket(),
            "shared_edge_bound_s": self.OPERATIVE_BOUND_S,
        }
        calibration = two_shared_edge_common_mode_floor(
            self.REPLAY_DELTAS, **inputs
        )
        consumer = two_shared_edge_common_mode_floor(
            self.REPLAY_DELTAS, **inputs
        )
        self.assertEqual(calibration, consumer)
        registration = calibration.estimator_registration
        self.assertEqual(
            registration["calibration_treatment"],
            registration["consuming_contrast_treatment"],
        )

    def test_inputs_are_immutable_and_registration_surfaces_in_record(self):
        onset, offset, residuals = self.replay_inputs()
        bracket = self.bracket()
        before = json.loads(json.dumps([onset, offset, residuals, bracket]))
        estimate = two_shared_edge_common_mode_floor(
            self.REPLAY_DELTAS,
            onset_sweeps_j=onset,
            offset_sweeps_j=offset,
            bundle_residual_half_widths_j=residuals,
            calibration_bracket=bracket,
            shared_edge_bound_s=self.OPERATIVE_BOUND_S,
        )
        self.assertEqual([onset, offset, residuals, bracket], before)
        record = build_comparative_record(
            estimate,
            [{} for _ in self.REPLAY_DELTAS],
            consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
            whole_window_drift_allowance=whole_window_allowance(),
        )
        self.assertEqual(
            record["estimator_registration"],
            two_shared_edge_common_mode_registration(),
        )

    def test_registered_precondition_failure_does_not_fall_back(self):
        onset, offset, residuals = self.replay_inputs()
        onset[0] = [999.0, 1000.0]
        with self.assertRaises(CommonModeEstimatorRefusal) as caught:
            two_shared_edge_common_mode_floor(
                self.REPLAY_DELTAS,
                onset_sweeps_j=onset,
                offset_sweeps_j=offset,
                bundle_residual_half_widths_j=residuals,
                calibration_bracket=self.bracket(),
                shared_edge_bound_s=self.OPERATIVE_BOUND_S,
            )
        self.assertEqual(
            caught.exception.reason, "common_mode_precondition_failed"
        )
        default = comparative_false_effect_floor(
            self.REPLAY_DELTAS,
            admissible_half_widths_j=self.REPLAY_TOTAL_WIDTHS,
        )
        self.assertIsNone(default.estimator_registration)


class TestWidthClosure(unittest.TestCase):
    @staticmethod
    def _build_absolute(estimate):
        return build_absolute_record(
            estimate,
            [{} for _ in range(estimate.n)],
            consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
            whole_window_drift_allowance=whole_window_allowance(),
        )

    @staticmethod
    def _build_comparative(estimate):
        return build_comparative_record(
            estimate,
            [{} for _ in range(estimate.n)],
            consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
            whole_window_drift_allowance=whole_window_allowance(),
        )

    def test_estimator_widths_are_required_and_never_defaulted(self):
        constructors = (
            (absolute_false_effect_floor, FIXTURE_A_ENERGIES),
            (comparative_false_effect_floor, FIXTURE_B_DELTAS),
        )
        for constructor, values in constructors:
            with self.subTest(constructor=constructor.__name__, case="omitted"):
                with self.assertRaises(TypeError):
                    constructor(values)
            with self.subTest(constructor=constructor.__name__, case="none"):
                with self.assertRaisesRegex(ValueError, "half-widths are required"):
                    constructor(values, admissible_half_widths_j=None)
            with self.subTest(constructor=constructor.__name__, case="empty"):
                with self.assertRaises(ValueError):
                    constructor(values, admissible_half_widths_j=[])
            with self.subTest(
                constructor=constructor.__name__,
                case="wrong_length",
            ):
                with self.assertRaisesRegex(ValueError, "count must match"):
                    constructor(
                        values,
                        admissible_half_widths_j=[0.0] * (len(values) - 1),
                    )

    def test_salvage_semantics_is_a_registered_floor_record_dispatch(self):
        estimate = absolute_false_effect_floor(
            FIXTURE_A_ENERGIES,
            admissible_half_widths_j=[0.0] * len(FIXTURE_A_ENERGIES),
        )
        record = build_absolute_record(
            estimate,
            [{} for _ in range(estimate.n)],
            consumption_semantics_id=SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
            whole_window_drift_allowance=whole_window_allowance(),
        )
        self.assertEqual(
            record["consumption_semantics_id"],
            SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
        )
    def test_builders_reject_missing_empty_or_wrong_length_widths(self):
        absolute = absolute_false_effect_floor(
            FIXTURE_A_ENERGIES,
            admissible_half_widths_j=[0.0] * len(FIXTURE_A_ENERGIES),
        )
        comparative = comparative_false_effect_floor(
            FIXTURE_B_DELTAS,
            admissible_half_widths_j=[0.0] * len(FIXTURE_B_DELTAS),
        )
        cases = (
            (
                self._build_absolute,
                replace(absolute, admissible_half_widths_j=()),
                "nonempty authenticated",
            ),
            (
                self._build_absolute,
                replace(
                    absolute,
                    admissible_half_widths_j=(
                        absolute.admissible_half_widths_j[:-1]
                    ),
                ),
                "count must equal",
            ),
            (
                self._build_comparative,
                replace(comparative, admissible_half_widths_j=()),
                "nonempty authenticated",
            ),
            (
                self._build_comparative,
                replace(
                    comparative,
                    admissible_half_widths_j=(
                        comparative.admissible_half_widths_j[:-1]
                    ),
                ),
                "count must equal",
            ),
        )
        for builder, estimate, expected in cases:
            with self.subTest(builder=builder.__name__, expected=expected):
                with self.assertRaisesRegex(ValueError, expected):
                    builder(estimate)

    def test_dead_gate_accepts_only_valid_guarded_and_smoke_pairings(self):
        guarded = absolute_false_effect_floor(
            FIXTURE_A_ENERGIES,
            admissible_half_widths_j=[0.1] * len(FIXTURE_A_ENERGIES),
        )
        guarded_record = self._build_absolute(guarded)
        self.assertEqual(
            guarded_record["corner_widened_guarded_floor_j"],
            guarded.guard_factor
            * guarded_record["corner_widened_unguarded_floor_j"],
        )

        smoke = absolute_false_effect_floor(
            [10.0, 11.0, 12.0],
            admissible_half_widths_j=[0.1] * 3,
        )
        smoke_record = self._build_absolute(smoke)
        self.assertIsNotNone(
            smoke_record["corner_widened_unguarded_floor_j"]
        )
        self.assertIsNone(smoke_record["corner_widened_guarded_floor_j"])

        invalid_guarded = {
            "missing_corner_unguarded": replace(
                guarded,
                corner_widened_unguarded_floor_j=None,
            ),
            "missing_corner_guarded": replace(
                guarded,
                corner_widened_guarded_floor_j=None,
            ),
            "corner_product_mismatch": replace(
                guarded,
                corner_widened_guarded_floor_j=(
                    guarded.corner_widened_guarded_floor_j + 1.0
                ),
            ),
            "missing_guard_factor": replace(guarded, guard_factor=None),
            "missing_guarded_floor": replace(guarded, guarded_floor_j=None),
            "guarded_product_mismatch": replace(
                guarded,
                guarded_floor_j=guarded.guarded_floor_j + 1.0,
            ),
            "guarded_disguised_as_smoke": replace(
                guarded,
                guard_factor=None,
                guarded_floor_j=None,
                corner_widened_guarded_floor_j=None,
            ),
        }
        for case, estimate in invalid_guarded.items():
            with self.subTest(estimate="guarded", case=case):
                with self.assertRaises(ValueError):
                    self._build_absolute(estimate)

        invalid_smoke = {
            "missing_corner_unguarded": replace(
                smoke,
                corner_widened_unguarded_floor_j=None,
            ),
            "corner_guarded_present": replace(
                smoke,
                corner_widened_guarded_floor_j=(
                    smoke.corner_widened_unguarded_floor_j
                ),
            ),
            "guard_factor_present": replace(smoke, guard_factor=1.0),
            "guarded_floor_present": replace(
                smoke,
                guarded_floor_j=smoke.unguarded_floor_j,
            ),
            "smoke_disguised_as_guarded": replace(
                smoke,
                guard_factor=1.0,
                guarded_floor_j=smoke.unguarded_floor_j,
                corner_widened_guarded_floor_j=(
                    smoke.corner_widened_unguarded_floor_j
                ),
            ),
        }
        for case, estimate in invalid_smoke.items():
            with self.subTest(estimate="smoke", case=case):
                with self.assertRaises(ValueError):
                    self._build_absolute(estimate)


def make_regime(
    stack_identity=None,
    power=(5.0, 10.0),
    duration=(1.0, 4.0),
    p95_gap=0.3,
    bracket_gap=0.5,
    cadence=2.0,
    clock=("required", 0.002),
    interp=("required", 1.5),
    drift=("not_applicable", None),
):
    def term(pair):
        return {"applicability": pair[0], "maximum": pair[1]}

    stack = stack_identity or make_stack_identity()
    return {
        "stack_identity": stack,
        "stack_identity_sha256": canonical_domain_sha256(
            STACK_IDENTITY_DOMAIN, stack
        ),
        "stress_observed": {
            "mean_power_w_min": power[0],
            "mean_power_w_max": power[1],
            "window_duration_s_min": duration[0],
            "window_duration_s_max": duration[1],
            "p95_sample_gap_s_max": p95_gap,
            "bracketing_sample_gap_s_max": bracket_gap,
            "cadence_ratio_min": cadence,
            "bound_terms": {
                "clock_anchor_bound_s": term(clock),
                "interpolation_bound_j": term(interp),
                "idle_drift_bound_j": term(drift),
            },
        },
    }


def make_cell(
    cell_id="cell-1",
    energies=None,
    deltas=None,
    regime=None,
    condition="cf-1",
    metric="gross_energy_j",
    absolute_half_widths=(0.0,) * len(FIXTURE_A_ENERGIES),
    comparative_half_widths=(0.0,) * len(FIXTURE_B_DELTAS),
    whole_window_drift_allowance=None,
    absolute_whole_window_drift_allowance=None,
    comparative_whole_window_drift_allowance=None,
    absolute_consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
    comparative_consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
    absolute_regime=None,
    comparative_regime=None,
):
    if (
        whole_window_drift_allowance is None
        and absolute_whole_window_drift_allowance is None
        and comparative_whole_window_drift_allowance is None
    ):
        # Claim-ready fixtures must carry the clause-9 current allowance
        # group. The smallest positive float preserves the historical fixture
        # floor values while still exercising the complete governed wire.
        whole_window_drift_allowance = whole_window_allowance(
            value=5e-324,
            observed=0.0,
            derived=5e-324,
        )
    absolute_allowance = (
        absolute_whole_window_drift_allowance
        if absolute_whole_window_drift_allowance is not None
        else whole_window_drift_allowance
    )
    comparative_allowance = (
        comparative_whole_window_drift_allowance
        if comparative_whole_window_drift_allowance is not None
        else whole_window_drift_allowance
    )
    if absolute_allowance is None or comparative_allowance is None:
        raise ValueError("test cells require both component allowances")
    shared_regime = regime if regime is not None else make_regime()
    absolute_source_regime = (
        absolute_regime if absolute_regime is not None else shared_regime
    )
    comparative_source_regime = (
        comparative_regime if comparative_regime is not None else shared_regime
    )
    energies = FIXTURE_A_ENERGIES if energies is None else energies
    deltas = FIXTURE_B_DELTAS if deltas is None else deltas
    abs_est = absolute_false_effect_floor(
        energies, admissible_half_widths_j=absolute_half_widths
    )
    observations = [
        {
            "bundle_id": f"{cell_id}-r{i}",
            "bundle_sha256": HEX_A,
            "config_sha256": HEX_B,
            "metric_value_j": value,
        }
        for i, value in enumerate(energies)
    ]
    cmp_est = comparative_false_effect_floor(
        deltas, admissible_half_widths_j=comparative_half_widths
    )
    blocks = []
    for i, delta in enumerate(deltas):
        a, b = 100.0, 100.0 + delta
        blocks.append(
            {
                "block_id": f"{cell_id}-b{i}",
                "executed_labels": ["A", "B", "B", "A"],
                "members": [
                    {
                        "position": position,
                        "bundle_id": f"{cell_id}-b{i}-{position}",
                        "bundle_sha256": HEX_A,
                        "config_sha256": HEX_B,
                        "metric_value_j": value,
                    }
                    for position, value in (("A1", a), ("B1", b), ("B2", b), ("A2", a))
                ],
                "delta_j": delta,
            }
        )
    return build_floor_cell(
        cell_id=cell_id,
        key={
            "backend": "powermetrics",
            "metric": metric,
            "window_class": "request",
            **condition_family(condition),
        },
        eligibility={
            "use_role": "primary_claim_gate",
            "minimum_claim_n": 5,
            "status": "claim_ready",
            "claim_usable": True,
            "reason_codes": [],
        },
        absolute=build_absolute_record(
            abs_est,
            observations,
            consumption_semantics_id=absolute_consumption_semantics_id,
            whole_window_drift_allowance=absolute_allowance,
        ),
        comparative=build_comparative_record(
            cmp_est,
            blocks,
            consumption_semantics_id=comparative_consumption_semantics_id,
            whole_window_drift_allowance=comparative_allowance,
        ),
        transport_group_id="tg-1",
        provenance={
            "absolute": {
                "calibration_cell_id": f"{cell_id}-abs",
                "evidence_root_id": "a10",
                "order_manifest": {
                    "manifest_id": f"{cell_id}-abs-order",
                    "sha256": HEX_A,
                },
                "campaign_log": {"sha256": HEX_B},
                "extraction_report": {"sha256": HEX_C},
                "extraction_spec": {"sha256": HEX_D},
                "bundle_ids": [obs["bundle_id"] for obs in observations],
                "bundle_sha256s": [
                    obs["bundle_sha256"] for obs in observations
                ],
                "source_regime": absolute_source_regime,
            },
            "comparative": {
                "calibration_cell_id": f"{cell_id}-cmp",
                "evidence_root_id": "window_c",
                "order_manifest": {
                    "manifest_id": f"{cell_id}-cmp-order",
                    "sha256": HEX_B,
                },
                "campaign_log": {"sha256": HEX_C},
                "extraction_report": {"sha256": HEX_D},
                "extraction_spec": {"sha256": HEX_A},
                "bundle_ids": [
                    member["bundle_id"]
                    for block in blocks
                    for member in block["members"]
                ],
                "bundle_sha256s": [
                    member["bundle_sha256"]
                    for block in blocks
                    for member in block["members"]
                ],
                "source_regime": comparative_source_regime,
            },
        },
    )


def make_artifact(cells=None):
    cells = [make_cell()] if cells is None else cells
    group = build_transport_group(
        transport_group_id="tg-1",
        backend="powermetrics",
        metric=cells[0]["key"]["metric"],
        window_class="request",
        stack_identity=cells[0]["source_regime"]["stack_identity"],
        source_cells=cells,
        allowed_consumer_condition_families=[
            condition_family("cf-1"),
            condition_family("cf-2"),
        ],
    )
    return build_floor_artifact(
        artifact_id="floor-artifact-test-1",
        calibration_scope="smoke",
        source_class="synthetic",
        provenance={
            "calibration_plan": {
                "plan_id": MINT1_PLAN_ID,
                "declared_calibration_scope": "window_a",
                "relative_path": "configs/calibration-plan.json",
                "sha256": MINT1_PLAN_SHA256,
            },
            "mint_tool_version": MINT1_TOOL_VERSION,
            "implementation": {
                "project_commit": "0" * 40,
                "project_tree_state": "clean",
                "python_package": "joulewise",
            },
        },
        cells=cells,
        transport_groups=[group],
    )


def make_cross_window_cell(**overrides):
    arguments = {
        "absolute_whole_window_drift_allowance": whole_window_allowance(
            value=0.4,
            observed=0.3,
            derived=0.4,
            basis_sha256=HEX_C,
        ),
        "comparative_whole_window_drift_allowance": whole_window_allowance(
            value=0.6,
            observed=0.2,
            derived=0.6,
            basis_sha256=HEX_D,
        ),
        "absolute_consumption_semantics_id": (
            MINTED_CONSUMPTION_SEMANTICS_ID
        ),
        "comparative_consumption_semantics_id": (
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        ),
    }
    arguments.update(overrides)
    return make_cell(**arguments)


class TestArtifactEmitValidate(unittest.TestCase):
    def test_floor_metric_catalog_is_exact_and_governs_artifact_cells(self):
        expected_pairs = (
            ("gross_energy_j", "request"),
            ("energy_request_j", "request"),
            ("idle_subtracted_energy_j", "request"),
            ("phase_energy_j.tokenize", "phase"),
            ("phase_energy_j.prefill", "phase"),
            ("phase_energy_j.decode", "phase"),
            ("phase_energy_j.serialize", "phase"),
            ("phase_energy_j.transfer", "phase"),
            ("phase_energy_j.deserialize", "phase"),
        )
        self.assertEqual(
            FLOOR_METRIC_CATALOG,
            tuple(metric for metric, _ in expected_pairs),
        )

        for metric, window_class in expected_pairs:
            with self.subTest(metric=metric):
                artifact = make_artifact()
                artifact["cells"][0]["key"]["metric"] = metric
                artifact["cells"][0]["key"]["window_class"] = window_class
                artifact["transport_groups"][0]["metric"] = metric
                artifact["transport_groups"][0]["window_class"] = window_class
                for component in ("absolute", "comparative"):
                    artifact["cells"][0][component][
                        "whole_window_drift_allowance"
                    ]["claim_family"] = neg8_claim_family_for_metric(metric)
                self.assertEqual(validate_floor_artifact(artifact), [])

    def test_excluded_metrics_are_rejected_by_artifact_validator(self):
        for metric, window_class in (
            ("split_total_energy_j", "request"),
            ("phase_energy_j.idle", "phase"),
            ("phase_energy_j.warmup", "phase"),
            ("phase_energy_j.cleanup", "phase"),
            ("phase_energy_j.failure", "phase"),
        ):
            with self.subTest(metric=metric):
                artifact = make_artifact()
                artifact["cells"][0]["key"]["metric"] = metric
                artifact["cells"][0]["key"]["window_class"] = window_class
                artifact["transport_groups"][0]["metric"] = metric
                artifact["transport_groups"][0]["window_class"] = window_class
                self.assert_invalid(artifact, "not in FLOOR_METRIC_CATALOG")

    def test_valid_artifact_passes_and_round_trips(self):
        artifact = make_artifact()
        self.assertEqual(
            artifact["schema_version"],
            "joulewise.detection_floor_artifact.v2",
        )
        self.assertEqual(validate_floor_artifact(artifact), [])
        self.assertEqual(artifact["source_class"], "synthetic")
        round_tripped = json.loads(json.dumps(artifact, sort_keys=True))
        self.assertEqual(validate_floor_artifact(round_tripped), [])

    def test_mint1_pinset_preserves_byte_stable_empty_finding_set(self):
        self.assertEqual(
            hashlib.sha256(MINT1_PINSET_PATH.read_bytes()).hexdigest(),
            MINT1_PINSET_SHA256,
        )
        findings = validate_floor_artifact(make_artifact())
        self.assertEqual(
            json.dumps(findings, separators=(",", ":")).encode("utf-8"),
            b"[]",
        )

    def test_evidence_root_outside_artifact_family_pinset_refuses(self):
        artifact = make_artifact()
        artifact["cells"][0]["provenance"]["absolute"][
            "evidence_root_id"
        ] = "unreviewed_root"
        self.assertEqual(
            validate_floor_artifact(artifact),
            [
                "cells[0].provenance.absolute.evidence_root_id: "
                "not pinned by artifact family pinset"
            ],
        )

    def test_artifact_without_resolvable_pinset_refuses(self):
        artifact = make_artifact()
        artifact["provenance"]["calibration_plan"]["plan_id"] = (
            "unregistered-plan"
        )
        self.assertEqual(
            validate_floor_artifact(artifact),
            ["artifact.pinset: no pinset matches artifact family identity"],
        )

    def test_multiple_matching_pinsets_refuse(self):
        pinset_bytes = MINT1_PINSET_PATH.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            pinset_directory = Path(tmp)
            (pinset_directory / "first.json").write_bytes(pinset_bytes)
            (pinset_directory / "second.json").write_bytes(pinset_bytes)
            with patch.object(
                detection_floor,
                "_FLOOR_MINT_PINSET_DIRECTORY",
                pinset_directory,
            ):
                findings = validate_floor_artifact(make_artifact())
        self.assertEqual(
            findings,
            ["artifact.pinset: multiple pinsets match artifact family identity"],
        )

    def test_repository_symlinked_pinset_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "outside-pinset"
            target.write_bytes(MINT1_PINSET_PATH.read_bytes())
            pinset_directory = root / "repository"
            pinset_directory.mkdir()
            (pinset_directory / "mint1.json").symlink_to(target)
            with patch.object(
                detection_floor,
                "_FLOOR_MINT_PINSET_DIRECTORY",
                pinset_directory,
            ):
                findings = validate_floor_artifact(make_artifact())
        self.assertEqual(
            findings,
            [
                "artifact.pinset: repository pinset 'mint1.json': "
                "pinset file must not be a symlink"
            ],
        )

    def test_explicit_symlinked_pinset_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.json"
            target.write_bytes(MINT1_PINSET_PATH.read_bytes())
            symlink = root / "pinset.json"
            symlink.symlink_to(target)
            findings = validate_floor_artifact(
                make_artifact(),
                pinset_path=symlink,
                expected_pinset_sha256=MINT1_PINSET_SHA256,
            )
        self.assertEqual(
            findings,
            [
                "artifact.pinset: explicit pinset: "
                "pinset file must not be a symlink"
            ],
        )

    def test_malformed_repository_pinset_refuses_instead_of_skipping(self):
        with tempfile.TemporaryDirectory() as tmp:
            pinset_directory = Path(tmp)
            (pinset_directory / "garbage.json").write_text(
                "this is not JSON",
                encoding="utf-8",
            )
            with patch.object(
                detection_floor,
                "_FLOOR_MINT_PINSET_DIRECTORY",
                pinset_directory,
            ):
                findings = validate_floor_artifact(make_artifact())
        self.assertEqual(len(findings), 1)
        self.assertIn(
            "artifact.pinset: repository pinset 'garbage.json': "
            "pinset is not valid UTF-8 JSON",
            findings[0],
        )

    def test_explicit_pinset_digest_mismatch_refuses_forged_roots(self):
        pinset = json.loads(MINT1_PINSET_PATH.read_text(encoding="utf-8"))
        artifact = make_artifact()
        for component_name in ("absolute", "comparative"):
            artifact["cells"][0]["provenance"][component_name][
                "evidence_root_id"
            ] = "attacker_root"
            pinset[component_name]["evidence_root_id"] = "attacker_root"
        with tempfile.TemporaryDirectory() as tmp:
            forged_path, forged_digest = write_pinset(Path(tmp), pinset)
            self.assertNotEqual(forged_digest, MINT1_PINSET_SHA256)
            findings = validate_floor_artifact(
                artifact,
                pinset_path=forged_path,
                expected_pinset_sha256=MINT1_PINSET_SHA256,
            )
        self.assertEqual(len(findings), 1)
        self.assertIn("pinset sha256 mismatch", findings[0])

    def test_synthetic_second_pinset_is_family_scoped(self):
        pinset = json.loads(MINT1_PINSET_PATH.read_text(encoding="utf-8"))
        pinset["mint_tool_version"] = "joulewise.floor_mint.synthetic.v1"
        pinset["plan"]["plan_id"] = "synthetic-second-family"
        pinset["plan"]["sha256"] = HEX_D
        for component_name in ("absolute", "comparative"):
            pinset[component_name]["evidence_root_id"] = "synthetic_root"

        own_artifact = make_artifact()
        own_artifact["provenance"]["mint_tool_version"] = pinset[
            "mint_tool_version"
        ]
        own_artifact["provenance"]["calibration_plan"].update(
            {
                "plan_id": pinset["plan"]["plan_id"],
                "sha256": pinset["plan"]["sha256"],
            }
        )
        for block in own_artifact["cells"][0]["comparative"]["blocks"]:
            block["calibration_plan_sha256"] = pinset["plan"]["sha256"]
        for component_name in ("absolute", "comparative"):
            own_artifact["cells"][0]["provenance"][component_name][
                "evidence_root_id"
            ] = "synthetic_root"
        with tempfile.TemporaryDirectory() as tmp:
            pinset_directory = Path(tmp)
            (pinset_directory / "family-a.json").write_bytes(
                MINT1_PINSET_PATH.read_bytes()
            )
            family_b_path, family_b_digest = write_pinset(
                pinset_directory,
                pinset,
                name="family-b.json",
            )
            self.assertEqual(
                validate_floor_artifact(
                    own_artifact,
                    pinset_path=family_b_path,
                    expected_pinset_sha256=family_b_digest,
                ),
                [],
            )

            confused_family_a = make_artifact()
            for component_name in ("absolute", "comparative"):
                confused_family_a["cells"][0]["provenance"][component_name][
                    "evidence_root_id"
                ] = "synthetic_root"
            with patch.object(
                detection_floor,
                "_FLOOR_MINT_PINSET_DIRECTORY",
                pinset_directory,
            ):
                findings = validate_floor_artifact(confused_family_a)
        self.assertEqual(
            findings,
            [
                "cells[0].provenance.absolute.evidence_root_id: "
                "not pinned by artifact family pinset",
                "cells[0].provenance.comparative.evidence_root_id: "
                "not pinned by artifact family pinset",
            ],
        )

    def test_pinset_io_errors_do_not_leak_absolute_paths(self):
        secret = "/private/lead/custody/hidden-pinset.json"
        artifact = make_artifact()
        findings = validate_floor_artifact(
            artifact,
            pinset_path=secret,
            expected_pinset_sha256="0" * 64,
        )
        self.assertTrue(findings)
        for finding in findings:
            self.assertNotIn(secret, finding)
            self.assertNotIn("/private/lead", finding)

    def test_evidence_root_global_hardcode_is_removed(self):
        self.assertFalse(hasattr(detection_floor, "_EVIDENCE_ROOT_IDS"))

    def test_cross_window_component_bases_and_semantics_are_independent(self):
        artifact = make_artifact([make_cross_window_cell()])
        absolute = artifact["cells"][0]["absolute"]
        comparative = artifact["cells"][0]["comparative"]

        self.assertNotEqual(
            absolute["whole_window_evaluation_basis_sha256"],
            comparative["whole_window_evaluation_basis_sha256"],
        )
        self.assertNotEqual(
            absolute["consumption_semantics_id"],
            comparative["consumption_semantics_id"],
        )
        self.assertNotEqual(
            absolute["whole_window_drift_allowance"],
            comparative["whole_window_drift_allowance"],
        )
        self.assertEqual(validate_floor_artifact(artifact), [])

        swapped = json.loads(json.dumps(artifact))
        (
            swapped["cells"][0]["absolute"][
                "whole_window_evaluation_basis_sha256"
            ],
            swapped["cells"][0]["comparative"][
                "whole_window_evaluation_basis_sha256"
            ],
        ) = (
            swapped["cells"][0]["comparative"][
                "whole_window_evaluation_basis_sha256"
            ],
            swapped["cells"][0]["absolute"][
                "whole_window_evaluation_basis_sha256"
            ],
        )
        self.assert_invalid(swapped, "does not match record basis")

    def test_v2_rejects_missing_or_unknown_consumption_semantics(self):
        missing = make_artifact([make_cross_window_cell()])
        del missing["cells"][0]["absolute"]["consumption_semantics_id"]
        self.assert_invalid(missing, "missing key 'consumption_semantics_id'")

        unknown = make_artifact([make_cross_window_cell()])
        unknown["cells"][0]["comparative"][
            "consumption_semantics_id"
        ] = "unknown_semantics"
        self.assert_invalid(
            unknown,
            "unknown whole-window consumption semantics",
        )

    def test_copied_component_allowance_cannot_bypass_recomputation(self):
        artifact = make_artifact([make_cross_window_cell()])
        absolute = artifact["cells"][0]["absolute"]
        comparative = artifact["cells"][0]["comparative"]
        copied = json.loads(json.dumps(absolute["whole_window_drift_allowance"]))
        copied["whole_window_evaluation_basis_sha256"] = comparative[
            "whole_window_evaluation_basis_sha256"
        ]
        comparative["whole_window_drift_allowance"] = copied

        self.assert_invalid(
            artifact,
            "drift_widened_guarded_floor_j must equal",
        )

    def test_artifact_and_plan_calibration_scopes_are_not_equated(self):
        artifact = make_artifact([make_cross_window_cell()])
        artifact["calibration_scope"] = "production_window"
        self.assertEqual(
            artifact["provenance"]["calibration_plan"][
                "declared_calibration_scope"
            ],
            "window_a",
        )
        self.assertEqual(validate_floor_artifact(artifact), [])

    def test_floor_gate_is_max_of_component_drift_floors_never_sum(self):
        artifact = make_artifact([make_cross_window_cell()])
        cell = artifact["cells"][0]
        absolute = cell["absolute"]
        comparative = cell["comparative"]
        expected = max(
            absolute["drift_widened_guarded_floor_j"],
            comparative["drift_widened_guarded_floor_j"],
        )
        summed_allowances = (
            max(
                absolute["corner_widened_guarded_floor_j"],
                comparative["corner_widened_guarded_floor_j"],
            )
            + absolute["whole_window_drift_allowance"]["allowance_j"]
            + comparative["whole_window_drift_allowance"]["allowance_j"]
        )
        self.assertTrue(close(cell["floor_gate_j"], expected))
        self.assertFalse(close(cell["floor_gate_j"], summed_allowances))
        self.assertNotIn(
            "whole_window_drift_allowance",
            artifact["transport_groups"][0],
        )

        cell["floor_gate_j"] = summed_allowances
        artifact["transport_groups"][0][
            "composed_floor_gate_j"
        ] = summed_allowances
        self.assert_invalid(
            artifact,
            "floor_gate_j must equal max(floor_abs_j, floor_cmp_j)",
        )

    def test_component_provenance_is_positional_and_disjoint(self):
        reordered = make_artifact([make_cross_window_cell()])
        comparative_provenance = reordered["cells"][0]["provenance"][
            "comparative"
        ]
        comparative_provenance["bundle_ids"][0:2] = reversed(
            comparative_provenance["bundle_ids"][0:2]
        )
        self.assert_invalid(
            reordered,
            "bundle_ids: must positionally equal component members",
        )

        wrong_hash = make_artifact([make_cross_window_cell()])
        wrong_hash["cells"][0]["provenance"]["absolute"][
            "bundle_sha256s"
        ][0] = HEX_B
        self.assert_invalid(
            wrong_hash,
            "bundle_sha256s: must positionally equal component members",
        )

        overlapping = make_artifact([make_cross_window_cell()])
        cell = overlapping["cells"][0]
        absolute_bundle_id = cell["absolute"]["bundle_observations"][0][
            "bundle_id"
        ]
        cell["comparative"]["blocks"][0]["members"][0][
            "bundle_id"
        ] = absolute_bundle_id
        cell["provenance"]["comparative"]["bundle_ids"][
            0
        ] = absolute_bundle_id
        self.assert_invalid(
            overlapping,
            "absolute and comparative bundle members must be disjoint",
        )

    def test_component_regimes_compose_conservatively_and_fail_closed(self):
        absolute_regime = make_regime(
            power=(5.0, 8.0),
            duration=(1.0, 3.0),
            p95_gap=0.2,
            bracket_gap=0.3,
            cadence=2.5,
            clock=("required", 0.001),
            interp=("not_applicable", None),
        )
        comparative_regime = make_regime(
            power=(6.0, 10.0),
            duration=(2.0, 4.0),
            p95_gap=0.4,
            bracket_gap=0.5,
            cadence=1.5,
            clock=("required", 0.002),
            interp=("required", 1.5),
        )
        artifact = make_artifact(
            [
                make_cross_window_cell(
                    absolute_regime=absolute_regime,
                    comparative_regime=comparative_regime,
                )
            ]
        )
        observed = artifact["cells"][0]["source_regime"]["stress_observed"]
        self.assertEqual(observed["mean_power_w_min"], 5.0)
        self.assertEqual(observed["mean_power_w_max"], 10.0)
        self.assertEqual(observed["window_duration_s_min"], 1.0)
        self.assertEqual(observed["window_duration_s_max"], 4.0)
        self.assertEqual(observed["p95_sample_gap_s_max"], 0.4)
        self.assertEqual(observed["bracketing_sample_gap_s_max"], 0.5)
        self.assertEqual(observed["cadence_ratio_min"], 1.5)
        self.assertEqual(
            observed["bound_terms"]["clock_anchor_bound_s"],
            {"applicability": "required", "maximum": 0.002},
        )
        self.assertEqual(
            observed["bound_terms"]["interpolation_bound_j"],
            {"applicability": "required", "maximum": 1.5},
        )
        self.assertEqual(validate_floor_artifact(artifact), [])

        unknown_cell = make_cross_window_cell(
            absolute_regime=absolute_regime,
            comparative_regime=make_regime(
                drift=("unknown", None),
            ),
        )
        self.assertEqual(
            unknown_cell["source_regime"]["stress_observed"]["bound_terms"][
                "idle_drift_bound_j"
            ],
            {"applicability": "unknown", "maximum": None},
        )
        unknown_cell["eligibility"].update(
            {
                "use_role": "smoke_only",
                "status": "smoke_only",
                "claim_usable": False,
            }
        )
        self.assertEqual(
            validate_floor_artifact(make_artifact([unknown_cell])),
            [],
        )

        mismatched_stack = json.loads(json.dumps(artifact))
        component_regime = mismatched_stack["cells"][0]["provenance"][
            "comparative"
        ]["source_regime"]
        component_regime["stack_identity"][
            "runtime_version"
        ] = "different-runtime"
        component_regime["stack_identity_sha256"] = canonical_domain_sha256(
            STACK_IDENTITY_DOMAIN,
            component_regime["stack_identity"],
        )
        self.assert_invalid(
            mismatched_stack,
            "stack identity must match the cell",
        )

    def test_claim_ready_requires_both_component_records_and_provenance(self):
        missing_provenance = make_artifact([make_cross_window_cell()])
        missing_provenance["cells"][0]["provenance"]["comparative"] = None
        self.assert_invalid(
            missing_provenance,
            "required for the component record",
        )
        self.assert_invalid(
            missing_provenance,
            "claim_ready requires component-scoped provenance for both components",
        )

        artifact = make_artifact([make_cross_window_cell()])
        cell = artifact["cells"][0]
        cell["comparative"] = None
        cell["provenance"]["comparative"] = None
        cell["floor_cmp_j"] = None
        cell["floor_gate_j"] = None
        self.assert_invalid(
            artifact,
            "claim_ready requires both absolute and comparative components",
        )

    def test_v1_schema_version_is_rejected_without_migration(self):
        artifact = make_artifact()
        artifact["schema_version"] = "joulewise.detection_floor_artifact.v1"
        self.assertEqual(
            validate_floor_artifact(artifact),
            [
                "artifact: schema_version must be "
                "'joulewise.detection_floor_artifact.v2'"
            ],
        )

    def test_source_class_is_closed_data_vocabulary(self):
        for source_class in ("prospective", "retrospective", "synthetic"):
            artifact = make_artifact()
            artifact["source_class"] = source_class
            self.assertEqual(validate_floor_artifact(artifact), [])

        artifact = make_artifact()
        artifact["source_class"] = "claim_eligible"
        self.assert_invalid(artifact, "invalid source_class")

        artifact = make_artifact()
        del artifact["source_class"]
        self.assert_invalid(artifact, "missing key 'source_class'")

    def test_build_floor_artifact_requires_source_class(self):
        artifact = make_artifact()
        with self.assertRaises(TypeError):
            build_floor_artifact(
                artifact_id=artifact["artifact_id"],
                calibration_scope=artifact["calibration_scope"],
                provenance=artifact["provenance"],
                cells=artifact["cells"],
                transport_groups=artifact["transport_groups"],
            )

    def test_provenance_precondition_pins_are_structurally_validated(self):
        mutations = (
            (
                lambda artifact: artifact["provenance"][
                    "calibration_plan"
                ].__setitem__(
                    "plan_id", ""
                ),
                "calibration_plan.plan_id: must be a nonempty string",
            ),
            (
                lambda artifact: artifact["provenance"][
                    "calibration_plan"
                ].__setitem__(
                    "sha256", "short"
                ),
                "calibration_plan.sha256: must be 64 lowercase hex chars",
            ),
            (
                lambda artifact: artifact["provenance"][
                    "calibration_plan"
                ].__setitem__(
                    "declared_calibration_scope", "unknown"
                ),
                "declared_calibration_scope: must be a recognized calibration scope",
            ),
            (
                lambda artifact: artifact["provenance"][
                    "calibration_plan"
                ].__setitem__(
                    "relative_path", ""
                ),
                "calibration_plan.relative_path: must be a nonempty string",
            ),
            (
                lambda artifact: artifact["cells"][0]["provenance"]["absolute"][
                    "order_manifest"
                ].__setitem__(
                    "manifest_id", ""
                ),
                "order_manifest.manifest_id: must be a nonempty string",
            ),
            (
                lambda artifact: artifact["cells"][0]["provenance"]["absolute"][
                    "order_manifest"
                ].__setitem__("sha256", HEX_A.upper()),
                "order_manifest.sha256: must be 64 lowercase hex chars",
            ),
            (
                lambda artifact: artifact["cells"][0]["provenance"]["absolute"][
                    "campaign_log"
                ].__setitem__("sha256", "short"),
                "campaign_log.sha256: must be 64 lowercase hex chars",
            ),
            (
                lambda artifact: artifact["cells"][0]["provenance"]["absolute"].pop(
                    "extraction_report"
                ),
                "missing key 'extraction_report'",
            ),
            (
                lambda artifact: artifact["cells"][0]["provenance"]["absolute"][
                    "extraction_report"
                ].__setitem__("sha256", HEX_A.upper()),
                "extraction_report.sha256: must be 64 lowercase hex chars",
            ),
            (
                lambda artifact: artifact["cells"][0]["provenance"]["absolute"][
                    "extraction_spec"
                ].__setitem__("sha256", "short"),
                "extraction_spec.sha256: must be 64 lowercase hex chars",
            ),
            (
                lambda artifact: artifact["cells"][0]["provenance"]["absolute"].__setitem__(
                    "evidence_root_id", "other"
                ),
                "evidence_root_id: not pinned by artifact family pinset",
            ),
            (
                lambda artifact: artifact["provenance"].__setitem__(
                    "mint_tool_version", " "
                ),
                "mint_tool_version: must be a nonempty string",
            ),
            (
                lambda artifact: artifact["provenance"][
                    "implementation"
                ].__setitem__(
                    "project_commit", "0" * 39
                ),
                "project_commit: must be 40 lowercase hex chars",
            ),
            (
                lambda artifact: artifact["provenance"][
                    "implementation"
                ].__setitem__(
                    "project_tree_state", "unknown"
                ),
                "project_tree_state: must be 'clean' or 'dirty'",
            ),
            (
                lambda artifact: artifact["provenance"][
                    "implementation"
                ].__setitem__(
                    "python_package", "other"
                ),
                "python_package: must be 'joulewise'",
            ),
        )
        for mutate, expected in mutations:
            with self.subTest(expected=expected):
                artifact = make_artifact()
                mutate(artifact)
                self.assert_invalid(artifact, expected)

    def test_canonical_metric_vocabulary_rejects_unresolvable_typo(self):
        artifact = make_artifact()
        artifact["cells"][0]["key"]["metric"] = "gross_energy_j_typo"
        self.assert_invalid(artifact, "invalid metric")

    def test_widened_floor_fields_are_required_even_when_widths_are_zero(self):
        zero_width_artifact = make_artifact()
        for record_name in ("absolute", "comparative"):
            record = zero_width_artifact["cells"][0][record_name]
            expected_n = record["n"] if record_name == "absolute" else record["n_blocks"]
            self.assertEqual(record["admissible_half_widths_j"], [0.0] * expected_n)

        for record_name in ("absolute", "comparative"):
            for field in (
                "admissible_half_widths_j",
                "corner_widened_unguarded_floor_j",
                "corner_widened_guarded_floor_j",
            ):
                with self.subTest(record=record_name, field=field):
                    artifact = make_artifact()
                    del artifact["cells"][0][record_name][field]
                    self.assert_invalid(artifact, f"missing key {field!r}")

    def test_widened_floor_record_round_trips_and_rejects_tampering(self):
        cell = make_cell(
            energies=[0.0, 1.0, -1.0, 0.0, 0.0],
            deltas=[0.0] * 5,
            absolute_half_widths=[0.01] * 5,
        )
        artifact = make_artifact([cell])
        record = artifact["cells"][0]["absolute"]
        self.assertEqual(record["admissible_half_widths_j"], [0.01] * 5)
        self.assertEqual(
            record["corner_widened_guarded_floor_j"], 3.2578982723565812
        )
        self.assertEqual(validate_floor_artifact(artifact), [])

        record["corner_widened_guarded_floor_j"] -= 0.1
        self.assertTrue(
            any(
                "full corner enumeration" in error
                for error in validate_floor_artifact(artifact)
            )
        )

    def test_attribution_limited_artifact_is_labelled_and_single_counted(self):
        cell = make_cell(
            energies=[0.0] * 5,
            deltas=[0.0] * 5,
            absolute_half_widths=[0.5] * 5,
            comparative_half_widths=[0.5] * 5,
        )
        artifact = make_artifact([cell])
        self.assertEqual(validate_floor_artifact(artifact), [])
        stored = artifact["cells"][0]
        self.assertEqual(
            stored["floor_limit_class"],
            ATTRIBUTION_LIMIT_CLASS,
        )
        self.assertEqual(stored["floor_source"], ATTRIBUTION_FLOOR_SOURCE)
        self.assertEqual(
            stored["single_count_discipline"],
            attribution_single_count_discipline(),
        )
        for component in ("absolute", "comparative"):
            record = stored[component]
            self.assertEqual(
                record["point_floor_diagnostic"],
                {
                    "label": "repeatability_diagnostic",
                    "published_claim_floor": False,
                    "unguarded_floor_j": 0.0,
                    "guard_factor": 1.5,
                    "guarded_floor_j": 0.0,
                },
            )
            self.assertGreater(
                record["corner_widened_guarded_floor_j"],
                record["point_floor_diagnostic"]["guarded_floor_j"],
            )
        group = artifact["transport_groups"][0]
        self.assertEqual(
            group["single_count_discipline"],
            attribution_single_count_discipline(),
        )

        del stored["absolute"]["single_count_discipline"]
        self.assertTrue(
            any(
                "attribution-limit metadata fields must be present together"
                in error
                for error in validate_floor_artifact(artifact)
            )
        )

    def test_non_dominating_widened_cell_keeps_frozen_bytes(self):
        cell = make_cell(
            # Historical noncanonical label retained only for this byte pin.
            # This cell is deliberately not passed to artifact validation.
            metric="energy_wall_j",
            absolute_half_widths=[0.001] * len(FIXTURE_A_ENERGIES),
            comparative_half_widths=[0.001] * len(FIXTURE_B_DELTAS),
        )
        self.assertNotIn("floor_limit_class", cell)
        rendered = json.dumps(
            cell,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(rendered).hexdigest(),
            "17f4ed63add651e7010d4df09c429e371e6c08d943ef5ea829d6d6123fdb9d51",
        )

    def test_comparative_widened_floor_round_trips_and_rejects_tampering(self):
        cell = make_cell(
            energies=[0.0] * 5,
            deltas=[1.0, -1.0, 0.0, 0.0, 0.0],
            comparative_half_widths=[0.5] * 5,
        )
        artifact = make_artifact([cell])
        record = artifact["cells"][0]["comparative"]
        self.assertEqual(record["admissible_half_widths_j"], [0.5] * 5)
        self.assertEqual(
            record["corner_widened_guarded_floor_j"], 5.446799999999999
        )
        self.assertEqual(
            artifact["cells"][0]["floor_gate_j"],
            record["corner_widened_guarded_floor_j"],
        )
        round_tripped = json.loads(json.dumps(artifact, sort_keys=True))
        self.assertEqual(validate_floor_artifact(round_tripped), [])

        round_tripped["cells"][0]["comparative"][
            "corner_widened_guarded_floor_j"
        ] -= 0.1
        self.assertTrue(
            any(
                "full corner enumeration" in error
                for error in validate_floor_artifact(round_tripped)
            )
        )

    def test_artifact_records_plan_hash_and_per_member_abba_sequence(self):
        artifact = make_artifact()
        block = artifact["cells"][0]["comparative"]["blocks"][0]
        self.assertEqual(block["calibration_plan_sha256"], MINT1_PLAN_SHA256)
        self.assertEqual(
            [member["plan_label"] for member in block["members"]],
            ["A", "B", "B", "A"],
        )
        self.assertEqual(
            [member["plan_sequence_index"] for member in block["members"]],
            [1, 2, 3, 4],
        )

    def test_mutable_plan_sequence_fields_are_structurally_rejected(self):
        artifact = make_artifact()
        block = artifact["cells"][0]["comparative"]["blocks"][0]
        block["calibration_plan_sha256"] = HEX_B
        block["members"][0]["plan_label"] = "B"
        block["members"][1]["plan_sequence_index"] = 3
        self.assert_invalid(artifact, "does not match artifact provenance")
        self.assert_invalid(artifact, "does not match executed label sequence")
        self.assert_invalid(artifact, "must match member order")

    def test_cell_floor_fields_match_fixtures(self):
        cell = make_cell()
        self.assertTrue(close(cell["floor_abs_j"], FIXTURE_A_GUARDED))
        self.assertTrue(close(cell["floor_cmp_j"], FIXTURE_B_GUARDED))
        self.assertTrue(close(cell["floor_gate_j"], FIXTURE_A_GUARDED))

    def test_method_uses_neutral_t_quantile_parameter(self):
        method = make_artifact()["method"]
        self.assertEqual(method["t_quantile"], 0.975)
        self.assertNotIn("confidence", method)

    def assert_invalid(self, artifact, fragment):
        errors = validate_floor_artifact(artifact)
        self.assertTrue(
            any(fragment in error for error in errors),
            msg=f"expected {fragment!r} in {errors!r}",
        )

    def test_rejections(self):
        artifact = make_artifact()
        self.assertEqual(validate_floor_artifact(artifact), [])

        def variant():
            return json.loads(json.dumps(make_artifact()))

        bad = variant()
        bad["surprise"] = 1
        self.assert_invalid(bad, "unrecognized key")

        bad = variant()
        bad["schema_version"] = "joulewise.detection_floor_artifact.v0"
        self.assert_invalid(bad, "schema_version")

        bad = variant()
        bad["method"]["method_id"] = "other.v1"
        self.assert_invalid(bad, "method block")

        bad = variant()
        bad["cells"][0]["absolute"]["guarded_floor_j"] += 1.0
        self.assert_invalid(bad, "guarded_floor_j")

        bad = variant()
        bad["cells"][0]["floor_gate_j"] = 1.0
        self.assert_invalid(bad, "floor_gate_j")

        bad = variant()
        bad["cells"][0]["absolute"]["guard_factor"] = 1.4
        self.assert_invalid(bad, "guard_factor")

        bad = variant()
        bad["cells"][0]["absolute"]["bundle_observations"][0]["bundle_sha256"] = HEX_A.upper()
        self.assert_invalid(bad, "lowercase hex")

        bad = variant()
        bad["cells"][0]["absolute"]["residuals_j"].pop()
        self.assert_invalid(bad, "lengths disagree")

        bad = variant()
        bad["cells"][0]["absolute"]["bundle_observations"][0]["metric_value_j"] = float("nan")
        self.assert_invalid(bad, "finite")

        bad = variant()
        bad["cells"][0]["comparative"]["blocks"][0]["delta_j"] += 0.5
        self.assert_invalid(bad, "delta_j")

        bad = variant()
        members = bad["cells"][0]["comparative"]["blocks"][0]["members"]
        members[1], members[2] = members[2], members[1]
        members[1]["position"], members[2]["position"] = "B2", "B1"
        bad["cells"][0]["comparative"]["blocks"][0]["members"] = members
        # Same numbers, wrong provenance order: validation failure, not a
        # different estimate.
        self.assert_invalid(bad, "A1/B1/B2/A2")

        bad = variant()
        bad["cells"].append(json.loads(json.dumps(bad["cells"][0])))
        bad["transport_groups"][0]["source_cell_ids"] = ["cell-1"]
        self.assert_invalid(bad, "duplicate cell_id")
        self.assert_invalid(bad, "duplicate cell key")

        bad = variant()
        bad["cells"][0]["transport_group_id"] = "tg-missing"
        self.assert_invalid(bad, "references no transport group")

        bad = variant()
        bad["transport_groups"][0]["composed_floor_gate_j"] += 1.0
        self.assert_invalid(bad, "composed_floor_gate_j")

        bad = variant()
        bad["transport_groups"][0]["rule_id"] = "lenient.v1"
        self.assert_invalid(bad, "rule_id")

        bad = variant()
        drift = bad["cells"][0]["source_regime"]["stress_observed"]["bound_terms"]["idle_drift_bound_j"]
        drift["applicability"] = "required"  # required must carry a numeric max
        self.assert_invalid(bad, "idle_drift_bound_j")

    def test_hash_derived_identity_objects_match(self):
        artifact = make_artifact()
        stack = artifact["cells"][0]["source_regime"]["stack_identity"]
        self.assertEqual(
            artifact["cells"][0]["source_regime"]["stack_identity_sha256"],
            canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack),
        )
        family = artifact["cells"][0]["key"]
        self.assertEqual(
            family["condition_family_sha256"],
            canonical_domain_sha256(
                CONDITION_FAMILY_DOMAIN, family["condition_family_definition"]
            ),
        )
        self.assertEqual(validate_floor_artifact(artifact), [])

    def test_analyst_supplied_hash_label_stuffing_rejected(self):
        artifact = make_artifact()
        artifact["cells"][0]["source_regime"]["stack_identity_sha256"] = HEX_C
        self.assert_invalid(artifact, "does not match recomputed joulewise.stack_identity.v1")

    def test_stack_identity_single_field_mutation_rejected(self):
        artifact = make_artifact()
        artifact["cells"][0]["source_regime"]["stack_identity"][
            "runtime_version"
        ] = "mlx 1.0-mutated"
        self.assert_invalid(artifact, "does not match recomputed joulewise.stack_identity.v1")

    def test_condition_family_definition_mutation_rejected(self):
        artifact = make_artifact()
        artifact["cells"][0]["key"]["condition_family_definition"][
            "comparison_policy"
        ] = "post_hoc_wildcard"
        self.assert_invalid(artifact, "does not match recomputed joulewise.condition_family.v1")

    def test_claim_ready_rejects_smoke_only_role(self):
        artifact = make_artifact()
        artifact["cells"][0]["eligibility"]["use_role"] = "smoke_only"
        self.assert_invalid(artifact, "claim_ready requires primary_claim_gate")

    def test_claim_ready_rejects_minimum_n_above_stored_n(self):
        artifact = make_artifact()
        artifact["cells"][0]["eligibility"]["minimum_claim_n"] = 6
        self.assert_invalid(artifact, "absolute n is below minimum_claim_n")
        self.assert_invalid(artifact, "comparative n is below minimum_claim_n")

    def test_claim_ready_rejects_duplicate_source_bundles(self):
        artifact = make_artifact()
        bundle_ids = artifact["cells"][0]["provenance"]["absolute"][
            "bundle_ids"
        ]
        bundle_ids[1] = bundle_ids[0]
        self.assert_invalid(artifact, "source bundle_ids must be unique")

    def test_claim_ready_rejects_duplicate_observation_bundle_ids(self):
        artifact = make_artifact()
        observations = artifact["cells"][0]["absolute"]["bundle_observations"]
        observations[1]["bundle_id"] = observations[0]["bundle_id"]
        self.assert_invalid(artifact, "absolute: source bundle_ids must be unique")

    def test_claim_ready_rejects_unknown_regime_term(self):
        artifact = make_artifact()
        term = artifact["cells"][0]["source_regime"]["stress_observed"][
            "bound_terms"
        ]["clock_anchor_bound_s"]
        term.update({"applicability": "unknown", "maximum": None})
        self.assert_invalid(artifact, "claim_ready forbids unknown regime terms")

    def test_claim_ready_rejects_incomplete_transport_membership(self):
        artifact = make_artifact()
        artifact["transport_groups"][0]["source_cell_ids"] = ["missing-cell"]
        self.assert_invalid(artifact, "source cell 'missing-cell' not found")
        self.assert_invalid(artifact, "claim_ready requires complete transport membership")

    def test_claim_ready_rejects_condition_missing_from_transport_group(self):
        artifact = make_artifact()
        artifact["transport_groups"][0]["allowed_consumer_condition_families"] = [
            condition_family("cf-2")
        ]
        self.assert_invalid(artifact, "condition family missing from transport group")

    def test_claim_usable_is_derived_from_ready_and_staleness(self):
        artifact = make_artifact()
        artifact["cells"][0]["eligibility"]["claim_usable"] = False
        self.assert_invalid(artifact, "claim_usable must equal claim_ready and not stale")

        artifact = make_artifact()
        artifact["cells"][0]["eligibility"].update(
            {"status": "stale", "claim_usable": True}
        )
        self.assert_invalid(artifact, "claim_usable must equal claim_ready and not stale")

    def test_absolute_n_zero_is_named_validation_error_not_exception(self):
        artifact = make_artifact()
        record = artifact["cells"][0]["absolute"]
        record.update({"n": 0, "residuals_j": [], "bundle_observations": []})
        self.assert_invalid(artifact, "absolute: n must be at least 2")

    def test_absolute_n_one_is_named_validation_error_not_exception(self):
        artifact = make_artifact()
        record = artifact["cells"][0]["absolute"]
        record.update(
            {
                "n": 1,
                "residuals_j": record["residuals_j"][:1],
                "bundle_observations": record["bundle_observations"][:1],
            }
        )
        self.assert_invalid(artifact, "absolute: n must be at least 2")

    def test_absolute_empty_arrays_are_named_validation_errors(self):
        artifact = make_artifact()
        artifact["cells"][0]["absolute"]["residuals_j"] = []
        artifact["cells"][0]["absolute"]["bundle_observations"] = []
        self.assert_invalid(artifact, "residuals_j must be a nonempty array")
        self.assert_invalid(artifact, "bundle_observations must be a nonempty array")

    def test_comparative_count_length_mismatch_is_named_validation_error(self):
        artifact = make_artifact()
        artifact["cells"][0]["comparative"]["blocks"].pop()
        self.assert_invalid(artifact, "n_blocks, block_deltas_j, and blocks lengths disagree")

    def test_large_magnitude_one_joule_alteration_rejected(self):
        artifact = make_artifact(
            [
                make_cell(
                    energies=[
                        1e12,
                        1e12 + 1.0,
                        1e12 - 1.0,
                        1e12 + 2.0,
                        1e12 - 2.0,
                    ]
                )
            ]
        )
        self.assertEqual(validate_floor_artifact(artifact), [])
        artifact["cells"][0]["absolute"]["mean_j"] += 1.0
        self.assert_invalid(artifact, "stored mean_j does not match observations")

    def test_idle_drift_guard_pending_and_calibrated_shapes(self):
        pending = make_artifact()
        self.assertEqual(validate_floor_artifact(pending), [])

        calibrated = make_artifact()
        calibrated["idle_drift_guard"] = {
            "calibration_status": "calibrated",
            "method": "p2_015_prediction_guard_v1",
            "guard_w": 0.25,
            "n_bundles": 2,
            "bundle_sha256": [HEX_A, HEX_B],
            "cell_id": "idle-cell-1",
            "artifact_sha256": HEX_C,
        }
        self.assertEqual(validate_floor_artifact(calibrated), [])

    def test_idle_drift_guard_internal_inconsistency_rejected(self):
        artifact = make_artifact()
        artifact["idle_drift_guard"]["n_bundles"] = 1
        self.assert_invalid(artifact, "n_bundles and bundle_sha256 length disagree")

    def test_whole_window_allowance_is_additive_and_recomputed(self):
        allowance = whole_window_allowance()
        cell = make_cell(whole_window_drift_allowance=allowance)
        artifact = make_artifact([cell])
        self.assertEqual(validate_floor_artifact(artifact), [])

        for record_name in ("absolute", "comparative"):
            record = cell[record_name]
            self.assertEqual(record["whole_window_drift_allowance"], allowance)
            self.assertTrue(
                close(
                    record["drift_widened_unguarded_floor_j"],
                    record["corner_widened_unguarded_floor_j"]
                    + allowance["allowance_j"],
                )
            )
            self.assertTrue(
                close(
                    record["drift_widened_guarded_floor_j"],
                    record["corner_widened_guarded_floor_j"]
                    + allowance["allowance_j"],
                )
            )

        tampered = json.loads(json.dumps(artifact))
        tampered["cells"][0]["absolute"][
            "drift_widened_guarded_floor_j"
        ] -= 0.1
        self.assert_invalid(
            tampered,
            "drift_widened_guarded_floor_j must equal",
        )

        understated = json.loads(json.dumps(artifact))
        understated["cells"][0]["comparative"][
            "whole_window_drift_allowance"
        ]["allowance_j"] = 0.2
        self.assert_invalid(
            understated,
            "must equal max(observed, derived)",
        )

        mismatched_family = json.loads(json.dumps(artifact))
        for record_name in ("absolute", "comparative"):
            mismatched_family["cells"][0][record_name][
                "whole_window_drift_allowance"
            ]["claim_family"] = "idle_subtracted_energy"
        self.assert_invalid(
            mismatched_family,
            "claim_family does not match metric",
        )

        malformed_basis = json.loads(json.dumps(artifact))
        for record_name in ("absolute", "comparative"):
            malformed_basis["cells"][0][record_name][
                "whole_window_evaluation_basis_sha256"
            ] = ["not", "hashable"]
        malformed_errors = validate_floor_artifact(malformed_basis)
        self.assertTrue(
            any(
                "whole_window_evaluation_basis_sha256: must be 64 lowercase hex chars"
                in error
                for error in malformed_errors
            ),
            malformed_errors,
        )

        for record_name in ("absolute", "comparative"):
            for field in (
                "whole_window_evaluation_basis_sha256",
                "consumption_semantics_id",
                "whole_window_drift_allowance",
                "drift_widened_unguarded_floor_j",
                "drift_widened_guarded_floor_j",
            ):
                with self.subTest(record=record_name, field=field):
                    missing = json.loads(json.dumps(artifact))
                    del missing["cells"][0][record_name][field]
                    self.assert_invalid(missing, f"missing key {field!r}")

    def test_basis_passing_extraction_refuses_absent_allowances(self):
        floor = absolute_false_effect_floor(
            [1.0, 1.1],
            admissible_half_widths_j=[0.0, 0.0],
        )
        report = CellReport(
            cell_id="basis-cell",
            kind="absolute",
            metric="gross_energy_j",
            window_class="request",
            cap_hit_policy="exclude_same_slot",
            members=(),
            excluded_slots=(),
            n_planned=2,
            n_admitted=2,
            refusal_reasons=(),
            floor=floor,
            anchor_shift_bound_max_j=0.01,
        )
        spec = {
            "schema_version": EXTRACTION_SPEC_SCHEMA_VERSION,
            "cells": [
                {
                    "cell_id": "basis-cell",
                    "kind": "absolute",
                    "metric": "gross_energy_j",
                    "window_class": "request",
                    "members": [{"slot": "A", "bundle_id": "A"}],
                }
            ],
        }
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch(
                "joulewise.floor_extraction.campaign_cooldown_evidence",
                return_value={},
            ),
            patch(
                "joulewise.floor_extraction.extract_absolute_cell",
                return_value=report,
            ),
            patch(
                "joulewise.floor_extraction._whole_window_extraction_refusals",
                return_value=(),
            ),
            patch(
                "joulewise.floor_extraction.whole_window_drift_allowances",
                return_value=WholeWindowDriftAllowanceResult("absent", {}),
            ),
        ):
            extracted = extract_cells(Path(tmp), spec)
        self.assertFalse(extracted["all_cells_extractable"])
        self.assertIn(
            "whole_window_drift_allowance_unrecorded",
            extracted["cells"][0]["refusal_reasons"],
        )
        self.assertIsNone(extracted["cells"][0]["floor"])
        self.assertIn(
            "whole_window_drift_allowance_unrecorded",
            CELL_REFUSAL_CODES,
        )


def make_consumer(**overrides):
    stack = make_stack_identity()
    family = condition_family("cf-2")
    consumer = {
        "backend": "powermetrics",
        "metric": "gross_energy_j",
        "window_class": "request",
        "stack_identity_sha256": canonical_domain_sha256(
            STACK_IDENTITY_DOMAIN, stack
        ),
        "condition_family_id": family["condition_family_id"],
        "condition_family_sha256": family["condition_family_sha256"],
        "mean_power_w_min": 6.0,
        "mean_power_w_max": 9.0,
        "window_duration_s_min": 1.5,
        "window_duration_s_max": 3.0,
        "p95_sample_gap_s_max": 0.2,
        "bracketing_sample_gap_s_max": 0.4,
        "cadence_ratio_min": 2.5,
        "bound_terms": {
            "clock_anchor_bound_s": {"applicability": "required", "maximum": 0.001},
            "interpolation_bound_j": {"applicability": "required", "maximum": 1.0},
            "idle_drift_bound_j": {"applicability": "not_applicable", "maximum": None},
        },
    }
    consumer.update(overrides)
    return consumer


class TestTransportRule(unittest.TestCase):
    def setUp(self):
        self.artifact = make_artifact()
        self.group = self.artifact["transport_groups"][0]
        self.cells_by_id = {cell["cell_id"]: cell for cell in self.artifact["cells"]}

    def check(self, consumer, *expected):
        reasons = transport_refusal_reasons(consumer, self.group, self.cells_by_id)
        self.assertEqual(set(reasons), set(expected))
        for reason in reasons:
            self.assertIn(reason, TRANSPORT_REASON_CODES)

    def test_predeclared_in_envelope_consumer_is_allowed(self):
        self.check(make_consumer())

    def test_artifact_hash_mismatch_reason_is_reachable(self):
        reasons = transport_refusal_reasons(
            make_consumer(),
            self.group,
            self.cells_by_id,
            artifact_sha256=HEX_A,
            expected_artifact_sha256=HEX_B,
        )
        self.assertEqual(set(reasons), {"artifact_hash_mismatch"})

    def test_artifact_schema_invalid_reason_is_reachable(self):
        reasons = transport_refusal_reasons(
            make_consumer(),
            self.group,
            self.cells_by_id,
            artifact_schema_valid=False,
        )
        self.assertEqual(set(reasons), {"artifact_schema_invalid"})

    def test_stack_mismatch_1p5b_vs_122b(self):
        # Same Mac, same telemetry backend, different model artifact ->
        # different stack identity hash -> refusal, never silent transport.
        self.check(make_consumer(stack_identity_sha256=HEX_B), "stack_mismatch")

    def test_condition_family_not_predeclared(self):
        self.check(make_consumer(condition_family_id="cf-rogue"), "condition_not_predeclared")

    def test_power_unbracketed_on_either_side(self):
        self.check(make_consumer(mean_power_w_min=4.0), "power_outside_calibrated_envelope")
        self.check(make_consumer(mean_power_w_max=11.0), "power_outside_calibrated_envelope")

    def test_duration_escape_shorter_and_longer(self):
        self.check(make_consumer(window_duration_s_min=0.5), "duration_outside_calibrated_envelope")
        self.check(make_consumer(window_duration_s_max=5.0), "duration_outside_calibrated_envelope")

    def test_cadence_harder_than_calibration(self):
        self.check(make_consumer(p95_sample_gap_s_max=0.9), "cadence_harder_than_calibration")
        self.check(make_consumer(bracketing_sample_gap_s_max=0.9), "cadence_harder_than_calibration")
        self.check(make_consumer(cadence_ratio_min=1.0), "cadence_harder_than_calibration")

    def test_bound_terms_harder_than_calibration(self):
        clock = {"clock_anchor_bound_s": {"applicability": "required", "maximum": 0.01}}
        consumer = make_consumer()
        consumer["bound_terms"] = {**consumer["bound_terms"], **clock}
        self.check(consumer, "clock_anchor_harder_than_calibration")

        interp = {"interpolation_bound_j": {"applicability": "required", "maximum": 5.0}}
        consumer = make_consumer()
        consumer["bound_terms"] = {**consumer["bound_terms"], **interp}
        self.check(consumer, "interpolation_harder_than_calibration")

        # Calibration has no drift evidence (not_applicable), so a consumer
        # that requires an idle-drift bound must be refused, not defaulted.
        drift = {"idle_drift_bound_j": {"applicability": "required", "maximum": 0.1}}
        consumer = make_consumer()
        consumer["bound_terms"] = {**consumer["bound_terms"], **drift}
        self.check(consumer, "drift_harder_than_calibration")

    def test_unknown_consumer_terms_refuse(self):
        consumer = make_consumer()
        del consumer["mean_power_w_min"]
        self.check(consumer, "consumer_term_unknown")

        consumer = make_consumer()
        consumer["bound_terms"]["clock_anchor_bound_s"] = {
            "applicability": "unknown",
            "maximum": None,
        }
        self.check(consumer, "consumer_term_unknown")

    def test_source_cell_health(self):
        stale = json.loads(json.dumps(self.cells_by_id))
        stale["cell-1"]["eligibility"]["status"] = "stale"
        reasons = transport_refusal_reasons(make_consumer(), self.group, stale)
        self.assertEqual(set(reasons), {"cell_stale"})

        smoke = json.loads(json.dumps(self.cells_by_id))
        smoke["cell-1"]["eligibility"]["status"] = "smoke_only"
        reasons = transport_refusal_reasons(make_consumer(), self.group, smoke)
        self.assertEqual(set(reasons), {"cell_not_claim_ready"})

        reasons = transport_refusal_reasons(make_consumer(), self.group, {})
        self.assertEqual(set(reasons), {"cell_missing"})

        empty_group = dict(self.group, source_cell_ids=[])
        reasons = transport_refusal_reasons(make_consumer(), empty_group, self.cells_by_id)
        self.assertIn("transport_group_incomplete", reasons)

    def test_composition_takes_worst_case_from_different_cells(self):
        # Cell X: big floors, narrow benign envelope. Cell Y: small floors,
        # wide adverse envelope. The group must compose X's floor with Y's
        # adverse evidence rather than pick one favorable source.
        cell_x = make_cell(
            "cell-x",
            regime=make_regime(
                power=(5.0, 8.0),
                duration=(1.0, 2.0),
                p95_gap=0.2,
                bracket_gap=0.3,
                cadence=3.0,
                clock=("required", 0.001),
                interp=("required", 1.0),
            ),
        )
        cell_y = make_cell(
            "cell-y",
            energies=[1.0, 1.0, 1.0, 1.0, 2.0],
            deltas=[0.1, -0.1, 0.2, -0.2, 0.0],
            regime=make_regime(
                power=(4.0, 12.0),
                duration=(0.5, 6.0),
                p95_gap=0.5,
                bracket_gap=0.8,
                cadence=1.5,
                clock=("required", 0.004),
                interp=("required", 2.0),
            ),
            condition="cf-2",
        )
        self.assertGreater(cell_x["floor_gate_j"], cell_y["floor_gate_j"])
        composed = compose_transport_group([cell_x, cell_y])
        self.assertTrue(close(composed["composed_floor_abs_j"], cell_x["floor_abs_j"]))
        self.assertTrue(close(composed["composed_floor_cmp_j"], cell_x["floor_cmp_j"]))
        self.assertTrue(close(composed["composed_floor_gate_j"], cell_x["floor_gate_j"]))
        envelope = composed["stress_envelope"]
        self.assertEqual(envelope["mean_power_w_min"], 4.0)
        self.assertEqual(envelope["mean_power_w_max"], 12.0)
        self.assertEqual(envelope["window_duration_s_min"], 0.5)
        self.assertEqual(envelope["window_duration_s_max"], 6.0)
        self.assertEqual(envelope["p95_sample_gap_s_max"], 0.5)
        self.assertEqual(envelope["bracketing_sample_gap_s_max"], 0.8)
        self.assertEqual(envelope["cadence_ratio_min"], 1.5)
        self.assertEqual(envelope["bound_term_maxima"]["clock_anchor_bound_s"], 0.004)
        self.assertEqual(envelope["bound_term_maxima"]["interpolation_bound_j"], 2.0)
        self.assertIsNone(envelope["bound_term_maxima"]["idle_drift_bound_j"])

        # The two-cell artifact also validates end to end.
        artifact = make_artifact([cell_x, cell_y])
        self.assertEqual(validate_floor_artifact(artifact), [])

    def test_reason_code_set_is_closed_v1_set(self):
        self.assertEqual(
            set(TRANSPORT_REASON_CODES),
            {
                "artifact_hash_mismatch",
                "artifact_schema_invalid",
                "cell_missing",
                "cell_not_claim_ready",
                "cell_stale",
                "condition_not_predeclared",
                "stack_mismatch",
                "power_outside_calibrated_envelope",
                "duration_outside_calibrated_envelope",
                "cadence_harder_than_calibration",
                "clock_anchor_harder_than_calibration",
                "interpolation_harder_than_calibration",
                "drift_harder_than_calibration",
                "consumer_term_unknown",
                "transport_group_incomplete",
            },
        )
        self.assertEqual(TRANSPORT_RULE_ID, "same_stack_componentwise_worst_case.v1")
        self.assertEqual(SCHEMA_VERSION, "joulewise.detection_floor_artifact.v2")


if __name__ == "__main__":
    unittest.main()
