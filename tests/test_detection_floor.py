"""Tests for the P2-039 detection-floor calculator (D-054 false-effect guard).

Hand-computed fixtures come directly from the DRAFT spec
``docs/specs/c027/p2-039_floor_artifact.md`` Units 9.1/9.2 and the C-027
worked example.
"""

import json
import math
import tempfile
import unittest
from pathlib import Path

from joulewise.detection_floor import (
    CONDITION_FAMILY_DOMAIN,
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
    small_sample_guard_factor,
    transport_refusal_reasons,
    validate_floor_artifact,
)

TOL = 1e-12
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64


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
        est = absolute_false_effect_floor(FIXTURE_A_ENERGIES)
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
        est = absolute_false_effect_floor([10, 10, 10, 10, 20])
        self.assertEqual(list(est.deviations_j), [-2, -2, -2, -2, 8])
        self.assertTrue(close(est.sample_stddev_j, math.sqrt(20)))
        self.assertAlmostEqual(est.unguarded_floor_j, 13.60, places=2)
        self.assertTrue(close(est.guarded_floor_j, FIXTURE_A_GUARDED))

    def test_guard_applied_after_max_not_inside(self):
        # n=9 with one large residual: max|r| = 8 dominates the prediction
        # component (~7.29). Applying g inside the max would give 8;
        # the spec's after-max rule gives g(9)*8.
        energies = [18.0] + [9.0] * 8
        est = absolute_false_effect_floor(energies)
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
        point = absolute_false_effect_floor(energies)
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
        est = absolute_false_effect_floor([10.0, 12.0, 11.0])
        self.assertIsNone(est.guard_factor)
        self.assertIsNone(est.guarded_floor_j)
        self.assertGreater(est.unguarded_floor_j, 0.0)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            absolute_false_effect_floor([10.0, float("nan"), 11.0, 12.0, 13.0])
        with self.assertRaises(ValueError):
            absolute_false_effect_floor([10.0, float("inf"), 11.0, 12.0, 13.0])
        with self.assertRaises(TypeError):
            absolute_false_effect_floor([10.0, True, 11.0, 12.0, 13.0])
        with self.assertRaises(ValueError):
            absolute_false_effect_floor([10.0])


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
        est = comparative_false_effect_floor(FIXTURE_B_DELTAS)
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
        point = comparative_false_effect_floor(deltas)
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
                comparative_false_effect_floor(negated).guarded_floor_j,
                FIXTURE_B_GUARDED,
            )
        )

    def test_mean_shift_included_not_centered_away(self):
        # Fixture B deltas shifted by +1: same spread, mean 1. An
        # implementation that centers deltas first would reproduce the
        # fixture-B prediction; the spec requires abs(mean) to be added.
        shifted = [d + 1.0 for d in FIXTURE_B_DELTAS]
        est = comparative_false_effect_floor(shifted)
        self.assertTrue(close(est.mean_j, 1.0))
        self.assertTrue(close(est.sample_stddev_j, FIXTURE_B_STDDEV))
        self.assertTrue(close(est.prediction_component_j, 1.0 + FIXTURE_B_PREDICTION))
        self.assertGreater(est.prediction_component_j, FIXTURE_B_PREDICTION)


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


def make_cell(cell_id="cell-1", energies=None, deltas=None, regime=None, condition="cf-1"):
    energies = FIXTURE_A_ENERGIES if energies is None else energies
    deltas = FIXTURE_B_DELTAS if deltas is None else deltas
    abs_est = absolute_false_effect_floor(energies)
    observations = [
        {
            "bundle_id": f"{cell_id}-r{i}",
            "bundle_sha256": HEX_A,
            "config_sha256": HEX_B,
            "metric_value_j": value,
        }
        for i, value in enumerate(energies)
    ]
    cmp_est = comparative_false_effect_floor(deltas)
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
            "metric": "energy_wall_j",
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
        absolute=build_absolute_record(abs_est, observations),
        comparative=build_comparative_record(cmp_est, blocks),
        source_regime=regime if regime is not None else make_regime(),
        transport_group_id="tg-1",
        provenance={
            "absolute_calibration_cell_id": f"{cell_id}-abs",
            "comparative_calibration_cell_id": f"{cell_id}-cmp",
            "bundle_ids": [obs["bundle_id"] for obs in observations],
            "bundle_sha256s": [HEX_A] * len(observations),
        },
    )


def make_artifact(cells=None):
    cells = [make_cell()] if cells is None else cells
    group = build_transport_group(
        transport_group_id="tg-1",
        backend="powermetrics",
        metric="energy_wall_j",
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
        provenance={
            "calibration_plan": {"plan_id": "plan-1", "sha256": HEX_A},
            "order_manifest": {"manifest_id": "manifest-1", "sha256": HEX_A},
            "campaign_log": {"sha256": HEX_A},
            "implementation": {
                "project_commit": "0" * 40,
                "project_tree_state": "clean",
                "python_package": "joulewise",
            },
        },
        cells=cells,
        transport_groups=[group],
    )


class TestArtifactEmitValidate(unittest.TestCase):
    def test_valid_artifact_passes_and_round_trips(self):
        artifact = make_artifact()
        self.assertEqual(validate_floor_artifact(artifact), [])
        round_tripped = json.loads(json.dumps(artifact, sort_keys=True))
        self.assertEqual(validate_floor_artifact(round_tripped), [])

    def test_artifact_records_plan_hash_and_per_member_abba_sequence(self):
        artifact = make_artifact()
        block = artifact["cells"][0]["comparative"]["blocks"][0]
        self.assertEqual(block["calibration_plan_sha256"], HEX_A)
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
        bundle_ids = artifact["cells"][0]["provenance"]["bundle_ids"]
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


def make_consumer(**overrides):
    stack = make_stack_identity()
    family = condition_family("cf-2")
    consumer = {
        "backend": "powermetrics",
        "metric": "energy_wall_j",
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
        self.assertEqual(SCHEMA_VERSION, "joulewise.detection_floor_artifact.v1")


if __name__ == "__main__":
    unittest.main()
