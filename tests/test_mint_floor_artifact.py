from __future__ import annotations

import copy
import hashlib
import inspect
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from joulewise.detection_floor import (
    STACK_IDENTITY_DOMAIN,
    attribution_single_count_discipline,
    canonical_domain_sha256,
    complete_bundle_sha256,
    validate_floor_artifact,
)
from joulewise.whole_window import (
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
)
from scripts import mint_floor_artifact as mint


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = REPO_ROOT / "configs" / "floor_mint"
PLAN_SOURCE = (
    REPO_ROOT
    / "configs"
    / "campaigns"
    / "p2_015_floors"
    / "calibration_plan.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def allowance(value: float, basis_sha256: str) -> dict:
    return {
        "claim_family": "gross_energy",
        "allowance_j": value,
        "observed_trajectory_excursion_j": value,
        "derived_repeatability_bound_j": value - 0.01,
        "provenance": {
            "bound_derivation_sha256": "b" * 64,
            "observed_component": "trajectory_excursion_max_j",
            "derived_component": "derived_repeatability_bound_j",
        },
        "whole_window_evaluation_basis_sha256": basis_sha256,
    }


def stack_identity() -> dict:
    return {
        "hardware_unit": "synthetic-m3-max",
        "os_version": "synthetic-macos",
        "runtime_version": "mlx-test",
        "kernel_library": "metal-test",
        "model_artifact_sha256": "c" * 64,
        "quantization": "int4",
        "tokenizer_identity": "synthetic-tokenizer",
        "sampler_output_policy": "greedy",
        "batching_concurrency_policy": "single-request sequential",
        "measurement_boundary_label": "phase-decode",
        "telemetry_backend": "powermetrics",
    }


def source_regime() -> dict:
    stack = stack_identity()
    return {
        "stack_identity": stack,
        "stack_identity_sha256": canonical_domain_sha256(
            STACK_IDENTITY_DOMAIN, stack
        ),
        "stress_observed": {
            "mean_power_w_min": 3.0,
            "mean_power_w_max": 7.0,
            "window_duration_s_min": 1.0,
            "window_duration_s_max": 2.0,
            "p95_sample_gap_s_max": 0.2,
            "bracketing_sample_gap_s_max": 0.3,
            "cadence_ratio_min": 1.5,
            "bound_terms": {
                "clock_anchor_bound_s": {
                    "applicability": "required",
                    "maximum": 0.01,
                },
                "interpolation_bound_j": {
                    "applicability": "required",
                    "maximum": 0.02,
                },
                "idle_drift_bound_j": {
                    "applicability": "not_applicable",
                    "maximum": None,
                },
            },
        },
    }


def member(
    bundle_id: str,
    value: float,
    *,
    bundle_sha256: str = "a" * 64,
    config_sha256: str = "d" * 64,
) -> mint.AuthenticatedMember:
    return mint.AuthenticatedMember(
        bundle_id=bundle_id,
        bundle_sha256=bundle_sha256,
        config_sha256=config_sha256,
        metric_value_j=value,
        raw_config={},
        metadata={},
        summary={},
    )


def report_floor(
    *,
    n: int,
    widths: list[float],
    drift_widened_guarded_floor_j: float,
) -> dict:
    return {
        "n": n,
        "admissible_half_widths_j": widths,
        "drift_widened_guarded_floor_j": drift_widened_guarded_floor_j,
    }


def authenticated_components() -> tuple[
    dict, mint.AuthenticatedComponent, mint.AuthenticatedComponent
]:
    plan = load_json(PLAN_SOURCE)
    a10_spec = load_json(CONFIG_ROOT / "a10_extraction_spec.json")
    window_c_spec = load_json(CONFIG_ROOT / "window_c_extraction_spec.json")
    a10_spec_cell = next(
        row for row in a10_spec["cells"] if row["cell_id"] == mint.A10_CELL_ID
    )
    window_c_spec_cell = window_c_spec["cells"][0]

    # With nine zeros and this final point, the n=10 absolute guarded floor is
    # exactly 2.939866246634162 J; adding the pinned allowance gives 3.592138.
    absolute_last = (
        float(mint.EXPECTED_OPERATIVE_FLOOR_TEXT)
        - mint.A10_DRIFT_ALLOWANCE_J
    ) / 0.9
    absolute_members = tuple(
        member(
            row["bundle_id"],
            absolute_last if index == 9 else 0.0,
        )
        for index, row in enumerate(a10_spec_cell["members"])
    )
    comparative_ids = [
        block["members"][position]
        for block in window_c_spec_cell["blocks"]
        for position in ("A1", "B1", "B2", "A2")
    ]
    comparative_members = tuple(member(bundle_id, 0.0) for bundle_id in comparative_ids)

    abs_allowance = allowance(
        mint.A10_DRIFT_ALLOWANCE_J,
        mint.A10_EVALUATION_BASIS_SHA256,
    )
    cmp_allowance = allowance(
        0.2,
        mint.WINDOW_C_EVALUATION_BASIS_SHA256,
    )
    absolute_cell = {
        "floor": report_floor(
            n=10,
            widths=[0.0] * 10,
            drift_widened_guarded_floor_j=float(
                mint.EXPECTED_OPERATIVE_FLOOR_TEXT
            ),
        )
    }
    comparative_cell = {
        "floor": report_floor(
            n=10,
            widths=[0.1] * 10,
            drift_widened_guarded_floor_j=0.46919615703584565,
        ),
        "point_floor_diagnostic": {
            "label": "repeatability_diagnostic",
            "published_claim_floor": False,
        },
    }
    regime = source_regime()
    absolute = mint.AuthenticatedComponent(
        evidence_root_id="a10",
        calibration_cell_id=mint.A10_CELL_ID,
        kind="absolute",
        report={"diagnostics": {"published_claim_floor": False}},
        report_sha256="1" * 64,
        spec=a10_spec,
        spec_sha256="2" * 64,
        order_manifest={
            "manifest_id": mint.A10_ORDER_MANIFEST_ID,
            "calibration_plan_sha256": mint.PLAN_SHA256,
            "plan_id": plan["plan_id"],
        },
        order_manifest_sha256="3" * 64,
        campaign_log_sha256="4" * 64,
        cell=absolute_cell,
        spec_cell=a10_spec_cell,
        members=absolute_members,
        widths_j=(0.0,) * 10,
        whole_window_evaluation_basis_sha256=(
            mint.A10_EVALUATION_BASIS_SHA256
        ),
        evaluation_basis_member_count=mint.A10_EVALUATION_BASIS_MEMBERS,
        consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        whole_window_drift_allowance=abs_allowance,
        source_regime=regime,
        scientific_config_identity_sha256="5" * 64,
        backend="powermetrics",
    )
    comparative = mint.AuthenticatedComponent(
        evidence_root_id="window_c",
        calibration_cell_id=mint.WINDOW_C_CELL_ID,
        kind="comparative",
        report={"diagnostics": {"published_claim_floor": False}},
        report_sha256="6" * 64,
        spec=window_c_spec,
        spec_sha256="7" * 64,
        order_manifest={
            "manifest_id": mint.WINDOW_C_ORDER_MANIFEST_ID,
            "calibration_plan_sha256": mint.PLAN_SHA256,
            "plan_id": plan["plan_id"],
        },
        order_manifest_sha256="8" * 64,
        campaign_log_sha256="9" * 64,
        cell=comparative_cell,
        spec_cell=window_c_spec_cell,
        members=comparative_members,
        widths_j=(0.1,) * 10,
        whole_window_evaluation_basis_sha256=(
            mint.WINDOW_C_EVALUATION_BASIS_SHA256
        ),
        evaluation_basis_member_count=mint.WINDOW_C_EVALUATION_BASIS_MEMBERS,
        consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
        whole_window_drift_allowance=cmp_allowance,
        source_regime=regime,
        scientific_config_identity_sha256="5" * 64,
        backend="powermetrics",
    )
    return plan, absolute, comparative


def make_artifact() -> dict:
    plan, absolute, comparative = authenticated_components()
    return mint.mint_authenticated_artifact(
        artifact_id="synthetic-mint-1",
        plan=plan,
        plan_sha256=mint.PLAN_SHA256,
        calibration_plan_relative_path="calibration_plan.json",
        absolute=absolute,
        comparative=comparative,
        project_commit="0" * 40,
        project_tree_state="clean",
    )


class PreRegistrationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan, self.absolute, self.comparative = authenticated_components()

    def gate(
        self,
        *,
        absolute: mint.AuthenticatedComponent | None = None,
        comparative: mint.AuthenticatedComponent | None = None,
    ) -> None:
        mint.pre_registration_gate(
            plan=self.plan,
            plan_sha256=mint.PLAN_SHA256,
            absolute=absolute or self.absolute,
            comparative=comparative or self.comparative,
        )

    def test_pinned_inputs_pass_and_consumption_semantics_are_report_values(self) -> None:
        self.gate()
        self.assertEqual(
            self.absolute.consumption_semantics_id,
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        )
        self.assertEqual(
            self.comparative.consumption_semantics_id,
            MINTED_CONSUMPTION_SEMANTICS_ID,
        )

    def test_swapped_component_bases_fail_before_any_builder_call(self) -> None:
        swapped_absolute = replace(
            self.absolute,
            whole_window_evaluation_basis_sha256=(
                mint.WINDOW_C_EVALUATION_BASIS_SHA256
            ),
        )
        swapped_comparative = replace(
            self.comparative,
            whole_window_evaluation_basis_sha256=(
                mint.A10_EVALUATION_BASIS_SHA256
            ),
        )
        with (
            mock.patch.object(mint, "build_absolute_record") as absolute_builder,
            mock.patch.object(mint, "build_comparative_record") as cmp_builder,
            self.assertRaisesRegex(mint.MintError, "evaluation bases"),
        ):
            mint.mint_authenticated_artifact(
                artifact_id="must-not-build",
                plan=self.plan,
                plan_sha256=mint.PLAN_SHA256,
                calibration_plan_relative_path="calibration_plan.json",
                absolute=swapped_absolute,
                comparative=swapped_comparative,
                project_commit="0" * 40,
                project_tree_state="clean",
            )
        absolute_builder.assert_not_called()
        cmp_builder.assert_not_called()

    def test_swapped_order_manifests_fail(self) -> None:
        swapped = replace(
            self.absolute,
            order_manifest={
                "manifest_id": mint.WINDOW_C_ORDER_MANIFEST_ID,
                "calibration_plan_sha256": mint.PLAN_SHA256,
                "plan_id": self.plan["plan_id"],
            },
        )
        with self.assertRaisesRegex(mint.MintError, "a10 order manifest"):
            self.gate(absolute=swapped)

    def test_one_root_only_regime_construction_fails(self) -> None:
        one_root = replace(self.comparative, evidence_root_id="a10")
        with self.assertRaisesRegex(mint.MintError, "distinct a10/window_c"):
            self.gate(comparative=one_root)

    def test_width_substitution_is_rejected_element_for_element(self) -> None:
        cell = copy.deepcopy(self.comparative.cell)
        cell["floor"]["admissible_half_widths_j"][4] = 0.1000001
        with self.assertRaisesRegex(mint.MintError, "element-for-element"):
            mint._verify_report_widths(cell, self.comparative.widths_j)

    def test_published_diagnostic_is_rejected(self) -> None:
        report = copy.deepcopy(self.comparative.report)
        report["diagnostics"]["published_claim_floor"] = True
        with self.assertRaisesRegex(mint.MintError, "diagnostic floor"):
            self.gate(comparative=replace(self.comparative, report=report))


class AuthenticationTests(unittest.TestCase):
    @staticmethod
    def _synthetic_consumption(
        root: Path,
        _member_ids: set[str],
        _basis_sha256: str,
        **_kwargs: object,
    ) -> tuple[dict[str, dict], str]:
        summaries = {
            bundle.name: load_json(bundle / "summary_metrics.json")
            for bundle in root.iterdir()
            if bundle.is_dir() and (bundle / "summary_metrics.json").is_file()
        }
        return summaries, MAX_BRACKET_CONSUMPTION_SEMANTICS_ID

    def _a10_tree(self, tmp: str) -> mint.ComponentPaths:
        root = Path(tmp) / "a10"
        root.mkdir()
        spec = load_json(CONFIG_ROOT / "a10_extraction_spec.json")
        spec_path = Path(tmp) / "a10-spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        cell_spec = next(
            cell for cell in spec["cells"] if cell["cell_id"] == mint.A10_CELL_ID
        )
        member_rows = []
        for index, spec_member in enumerate(cell_spec["members"]):
            bundle_id = spec_member["bundle_id"]
            bundle = root / bundle_id
            bundle.mkdir()
            config = {
                "run_id": bundle_id,
                "run_metadata": {
                    "tags": [
                        f"calibration-plan-sha256={mint.PLAN_SHA256}",
                        f"rep{index + 1}",
                    ]
                },
                "hardware_target": {"telemetry_backend": "powermetrics"},
            }
            summary = {
                "status": "succeeded",
                "phase_energy_j": {"decode": float(index)},
                "energy_anchor_shift_envelopes": {
                    "/phase_energy_j/decode": {
                        "point_j": float(index),
                        "lower_j": float(index) - 0.01,
                        "upper_j": float(index) + 0.01,
                        "max_abs_delta_j": 0.01,
                    }
                },
                "energy_bound_terms_j": {
                    "E_interpolation_joint_edge_bound_j": 0.0
                },
                "window_evidence_precheck": {
                    "phase": {
                        "decode": {
                            "windows": [
                                {
                                    "window_duration_s": 1.0,
                                    "observed_window_p95_sample_gap_s": 0.1,
                                    "observed_bracketing_max_sample_gap_s": 0.2,
                                    "cadence_ratio": 1.5,
                                    "clock_anchor_bound_s": 0.01,
                                    "interpolation_joint_edge_bound_j": 0.02,
                                }
                            ]
                        }
                    }
                },
            }
            (bundle / "config.json").write_text(
                json.dumps(config), encoding="utf-8"
            )
            (bundle / "metadata.json").write_text("{}", encoding="utf-8")
            (bundle / "summary_metrics.json").write_text(
                json.dumps(summary), encoding="utf-8"
            )
            member_rows.append(
                {
                    "bundle_id": bundle_id,
                    "bundle_sha256": complete_bundle_sha256(bundle),
                    "config_sha256": hashlib.sha256(
                        (bundle / "config.json").read_bytes()
                    ).hexdigest(),
                    "metric_value_j": float(index),
                    "anchor_shift_bound_j": 0.01,
                    "excluded": False,
                    "reasons": [],
                }
            )
        component_allowance = allowance(
            mint.A10_DRIFT_ALLOWANCE_J,
            mint.A10_EVALUATION_BASIS_SHA256,
        )
        report = {
            "schema_version": mint.EXTRACTION_SCHEMA_VERSION,
            "spec_schema_version": mint.EXTRACTION_SPEC_SCHEMA_VERSION,
            "runs_root": str(root),
            "consumption_semantics_id": MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            "spec_membership_refusals": [],
            "idle_admission_refusals": [],
            "cells": [
                {
                    "cell_id": mint.A10_CELL_ID,
                    "kind": "absolute",
                    "metric": mint.METRIC,
                    "window_class": mint.WINDOW_CLASS,
                    "extractable": True,
                    "refusal_reasons": [],
                    "floor": {
                        "n": 10,
                        "admissible_half_widths_j": [0.01] * 10,
                        "whole_window_drift_allowance_provenance": (
                            component_allowance
                        ),
                    },
                    "whole_window_drift_allowance": component_allowance,
                    "members": member_rows,
                }
            ],
        }
        report_path = Path(tmp) / "a10-report.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        all_spec_ids = mint._spec_member_ids(spec)
        order = {
            "manifest_id": mint.A10_ORDER_MANIFEST_ID,
            "plan_id": "p2-015-window-a-m3max-qwen25-1p5b-v1",
            "calibration_plan_sha256": mint.PLAN_SHA256,
            "executed_order": [
                {"run_id": bundle_id} for bundle_id in all_spec_ids
            ],
        }
        order_path = Path(tmp) / "a10-order.json"
        order_path.write_text(json.dumps(order), encoding="utf-8")
        basis_members = [
            *all_spec_ids,
            *(f"neg8-reference-{index}" for index in range(7)),
        ]
        (root / "campaign_log.jsonl").write_text(
            json.dumps(
                {
                    "evaluation_basis": {
                        "sha256": mint.A10_EVALUATION_BASIS_SHA256,
                        "member_occurrences": [
                            {"bundle_id": bundle_id}
                            for bundle_id in basis_members
                        ],
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return mint.ComponentPaths(
            evidence_root_id="a10",
            evidence_root=root,
            report_path=report_path,
            spec_path=spec_path,
            order_manifest_path=order_path,
            calibration_cell_id=mint.A10_CELL_ID,
            expected_kind="absolute",
        )

    def test_authenticated_replay_does_not_import_prefill_refusal(
        self,
    ) -> None:
        class LocalRefusalSession:
            ready = True
            refusal_reasons: tuple[str, ...] = ()
            path_refusal_reasons = {
                "member": {
                    ("phase", "prefill"): (
                        "clock_bound_exceeds_quarter_window",
                    )
                }
            }

            def __init__(self, *_args, **_kwargs) -> None:
                pass

            @staticmethod
            def summary_for(_bundle_id: str) -> dict:
                return {
                    "status": "succeeded",
                    "phase_energy_j": {"decode": 10.0},
                }

        with (
            mock.patch.object(
                mint,
                "AuthenticatedConsumptionSession",
                LocalRefusalSession,
            ),
            mock.patch.object(
                mint, "whole_window_refusal_reasons", return_value=()
            ),
        ):
            summaries, semantics = (
                mint._authenticated_consumption_summaries(
                    Path("/unused"),
                    {"member"},
                    "a" * 64,
                    target_bundle_ids={"member"},
                )
            )

        self.assertEqual(set(summaries), {"member"})
        self.assertEqual(
            semantics, MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        )

    def test_authenticated_replay_rejects_unrecorded_target_envelope(
        self,
    ) -> None:
        class LocalRefusalSession:
            ready = True
            refusal_reasons: tuple[str, ...] = ()
            path_refusal_reasons = {
                "member": {
                    ("phase", "decode"): (
                        "anchor_energy_envelope_unrecorded",
                    )
                }
            }

            def __init__(self, *_args, **_kwargs) -> None:
                pass

            @staticmethod
            def summary_for(_bundle_id: str) -> dict:
                return {
                    "status": "succeeded",
                    "phase_energy_j": {"decode": 10.0},
                }

        with (
            mock.patch.object(
                mint,
                "AuthenticatedConsumptionSession",
                LocalRefusalSession,
            ),
            mock.patch.object(
                mint, "whole_window_refusal_reasons", return_value=()
            ),
            self.assertRaisesRegex(
                mint.MintError,
                "authenticated target metric refused: "
                "anchor_energy_envelope_unrecorded",
            ),
        ):
            mint._authenticated_consumption_summaries(
                Path("/unused"),
                {"member"},
                "a" * 64,
                target_bundle_ids={"member"},
            )

    def test_authenticated_replay_requires_target_bundle_ids(
        self,
    ) -> None:
        parameter = inspect.signature(
            mint._authenticated_consumption_summaries
        ).parameters["target_bundle_ids"]
        self.assertIs(parameter.default, inspect.Parameter.empty)

    def test_report_spec_and_source_bytes_authenticate_before_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._a10_tree(tmp)
            with (
                mock.patch.object(
                    mint, "_derive_stack_identity", return_value=stack_identity()
                ),
                mock.patch.object(
                    mint,
                    "scientific_config_identity",
                    return_value={"synthetic": "same"},
                ),
            ):
                component = mint._authenticate_component(
                    paths,
                    expected_cell_id=mint.A10_CELL_ID,
                    expected_basis_sha256=mint.A10_EVALUATION_BASIS_SHA256,
                    strict_validator=lambda _path, _strict: (),
                    consumption_authenticator=self._synthetic_consumption,
                )
        self.assertEqual(component.evaluation_basis_member_count, 37)
        self.assertEqual(len(component.members), 10)
        self.assertEqual(component.widths_j, (0.01,) * 10)
        self.assertEqual(
            component.consumption_semantics_id,
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        )

    def test_missing_report_semantics_is_not_guessed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._a10_tree(tmp)
            report = load_json(paths.report_path)
            del report["consumption_semantics_id"]
            paths.report_path.write_text(json.dumps(report), encoding="utf-8")
            with (
                mock.patch.object(
                    mint, "_derive_stack_identity", return_value=stack_identity()
                ),
                mock.patch.object(
                    mint,
                    "scientific_config_identity",
                    return_value={"synthetic": "same"},
                ),
                self.assertRaisesRegex(
                    mint.MintError, "consumption_semantics_id"
                ),
            ):
                mint._authenticate_component(
                    paths,
                    expected_cell_id=mint.A10_CELL_ID,
                    expected_basis_sha256=mint.A10_EVALUATION_BASIS_SHA256,
                    strict_validator=lambda _path, _strict: (),
                    consumption_authenticator=self._synthetic_consumption,
                )

    def test_comparative_source_order_tags_are_evidence_derived(self) -> None:
        source = member(
            "cmp-b01-b2",
            1.0,
        )
        source = replace(
            source,
            raw_config={
                "run_metadata": {
                    "tags": [
                        f"calibration-plan-sha256={mint.PLAN_SHA256}",
                        "calibration-abba-block-id=b01",
                        "calibration-abba-label=B",
                        "calibration-abba-sequence-index=3",
                    ]
                }
            },
        )
        mint._verify_source_order_tags(
            source,
            {"block_id": "b01", "position": "B2"},
            comparative=True,
        )
        bad = replace(
            source,
            raw_config={
                "run_metadata": {
                    "tags": [
                        f"calibration-plan-sha256={mint.PLAN_SHA256}",
                        "calibration-abba-block-id=b01",
                        "calibration-abba-label=A",
                        "calibration-abba-sequence-index=3",
                    ]
                }
            },
        )
        with self.assertRaisesRegex(mint.MintError, "ABBA label"):
            mint._verify_source_order_tags(
                bad,
                {"block_id": "b01", "position": "B2"},
                comparative=True,
            )


class ConstructionTests(unittest.TestCase):
    def test_constructs_exact_cross_window_cell_and_composed_group(self) -> None:
        artifact = make_artifact()
        self.assertEqual(validate_floor_artifact(artifact), [])
        self.assertEqual(artifact["calibration_scope"], "production_window")
        self.assertEqual(artifact["source_class"], "prospective")
        self.assertEqual(len(artifact["cells"]), 1)
        self.assertEqual(artifact["cells"][0]["cell_id"], mint.CELL_ID)
        self.assertEqual(
            format(artifact["cells"][0]["floor_gate_j"], ".6f"),
            mint.EXPECTED_OPERATIVE_FLOOR_TEXT,
        )
        group = artifact["transport_groups"][0]
        self.assertEqual(group["transport_group_id"], mint.TRANSPORT_GROUP_ID)
        self.assertEqual(group["source_cell_ids"], [mint.CELL_ID])
        self.assertEqual(
            group["allowed_consumer_condition_families"],
            [
                {
                    "condition_family_id": mint.CONDITION_FAMILY_ID,
                    "condition_family_definition": artifact["cells"][0]["key"][
                        "condition_family_definition"
                    ],
                    "condition_family_sha256": mint.CONDITION_FAMILY_SHA256,
                }
            ],
        )
        self.assertEqual(
            group["composed_floor_gate_j"], artifact["cells"][0]["floor_gate_j"]
        )

    def test_single_count_statement_renders_from_canonical_object(self) -> None:
        artifact = make_artifact()
        statement = mint.render_single_count_statement(artifact)
        canonical = attribution_single_count_discipline()
        self.assertIn(canonical["statement"], statement)
        self.assertIn(canonical["effective_clearable_effect_formula"], statement)

        artifact["cells"][0]["single_count_discipline"]["statement"] = "tampered"
        with self.assertRaisesRegex(mint.MintError, "not canonical"):
            mint.render_single_count_statement(artifact)

    def test_exclusive_outputs_refuse_overwrite(self) -> None:
        artifact = make_artifact()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            floor = root / "floor.json"
            statement = root / "single-count.txt"
            mint.write_outputs_exclusive(artifact, floor, statement)
            original = floor.read_bytes()
            with self.assertRaisesRegex(mint.MintError, "overwrite"):
                mint.write_outputs_exclusive(artifact, floor, statement)
            self.assertEqual(floor.read_bytes(), original)

    def test_absolute_paths_and_unsafe_relative_paths_are_rejected(self) -> None:
        artifact = make_artifact()
        artifact["provenance"]["calibration_plan"]["relative_path"] = "../plan.json"
        with self.assertRaisesRegex(mint.MintError, "safe-relative POSIX"):
            mint._assert_path_independent(artifact)

        artifact = make_artifact()
        artifact["provenance"]["calibration_plan"]["relative_path"] = "/tmp/plan.json"
        with self.assertRaisesRegex(mint.MintError, "safe-relative POSIX"):
            mint._assert_path_independent(artifact)


class BinderTests(unittest.TestCase):
    @staticmethod
    def _synthetic_consumption(
        root: Path,
        member_ids: set[str],
        basis_sha256: str,
        **_kwargs: object,
    ) -> tuple[dict[str, dict], str]:
        summaries = {
            bundle_id: load_json(root / bundle_id / "summary_metrics.json")
            for bundle_id in member_ids
        }
        semantics = (
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
            if basis_sha256 == mint.A10_EVALUATION_BASIS_SHA256
            else MINTED_CONSUMPTION_SEMANTICS_ID
        )
        return summaries, semantics

    def _install_bundle(
        self,
        root: Path,
        row: dict,
        *,
        stack: dict,
        half_width_j: float,
    ) -> None:
        bundle = root / row["bundle_id"]
        bundle.mkdir(parents=True)
        config = {
            "run_id": row["bundle_id"],
            "hardware_target": {"telemetry_backend": "powermetrics"},
        }
        summary = {
            "status": "succeeded",
            "phase_energy_j": {"decode": row["metric_value_j"]},
            "energy_anchor_shift_envelopes": {
                "/phase_energy_j/decode": {
                    "point_j": row["metric_value_j"],
                    "lower_j": row["metric_value_j"] - half_width_j,
                    "upper_j": row["metric_value_j"] + half_width_j,
                    "max_abs_delta_j": half_width_j,
                }
            },
            "energy_bound_terms_j": {
                "E_interpolation_joint_edge_bound_j": 0.0
            },
        }
        (bundle / "config.json").write_text(
            json.dumps(config, sort_keys=True), encoding="utf-8"
        )
        (bundle / "metadata.json").write_text(
            json.dumps({"stack": stack}, sort_keys=True), encoding="utf-8"
        )
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, sort_keys=True), encoding="utf-8"
        )
        row["config_sha256"] = hashlib.sha256(
            (bundle / "config.json").read_bytes()
        ).hexdigest()
        row["bundle_sha256"] = complete_bundle_sha256(bundle)

    def _tree(self, tmp: str) -> tuple[dict, Path, dict[str, Path]]:
        base = Path(tmp)
        artifact = make_artifact()
        floor_path = base / "floor.json"
        plan_raw = PLAN_SOURCE.read_bytes()
        self.assertEqual(hashlib.sha256(plan_raw).hexdigest(), mint.PLAN_SHA256)
        (base / "calibration_plan.json").write_bytes(plan_raw)
        roots = {"a10": base / "a10", "window_c": base / "window_c"}
        for root in roots.values():
            root.mkdir()
            (root / "campaign_log.jsonl").write_text(
                json.dumps({"synthetic": True}) + "\n", encoding="utf-8"
            )
        stack = artifact["cells"][0]["source_regime"]["stack_identity"]
        cell = artifact["cells"][0]
        for component_name, root_id in (
            ("absolute", "a10"),
            ("comparative", "window_c"),
        ):
            rows = mint._record_rows(component_name, cell)
            member_half_width = 0.0 if component_name == "absolute" else 0.05
            for row in rows:
                self._install_bundle(
                    roots[root_id],
                    row,
                    stack=stack,
                    half_width_j=member_half_width,
                )
            provenance = cell["provenance"][component_name]
            provenance["bundle_sha256s"] = [
                row["bundle_sha256"] for row in rows
            ]
            provenance["campaign_log"]["sha256"] = hashlib.sha256(
                (roots[root_id] / "campaign_log.jsonl").read_bytes()
            ).hexdigest()
        self.assertEqual(validate_floor_artifact(artifact), [])
        return artifact, floor_path, roots

    def test_missing_evidence_root_mapping_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact, floor_path, roots = self._tree(tmp)
            with (
                mock.patch.object(
                    mint,
                    "_derive_stack_identity",
                    return_value=artifact["cells"][0]["source_regime"][
                        "stack_identity"
                    ],
                ),
                mock.patch.object(
                    mint,
                    "_authenticated_consumption_summaries",
                    side_effect=self._synthetic_consumption,
                ),
                self.assertRaisesRegex(mint.MintError, "missing evidence-root"),
            ):
                mint.bind_floor_artifact_evidence(
                    artifact,
                    floor_path,
                    {"a10": roots["a10"]},
                    strict_validator=lambda _path, _strict: (),
                )

    def test_binder_accepts_production_window_with_window_a_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact, floor_path, roots = self._tree(tmp)
            self.assertEqual(artifact["calibration_scope"], "production_window")
            self.assertEqual(
                artifact["provenance"]["calibration_plan"][
                    "declared_calibration_scope"
                ],
                "window_a",
            )
            with (
                mock.patch.object(
                    mint,
                    "_derive_stack_identity",
                    return_value=artifact["cells"][0]["source_regime"][
                        "stack_identity"
                    ],
                ),
                mock.patch.object(
                    mint,
                    "_authenticated_consumption_summaries",
                    side_effect=self._synthetic_consumption,
                ),
            ):
                rebound = mint.bind_floor_artifact_evidence(
                    artifact,
                    floor_path,
                    roots,
                    strict_validator=lambda _path, _strict: (),
                )
            self.assertEqual(set(rebound), {"absolute", "comparative"})

    def test_binder_rejects_source_byte_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact, floor_path, roots = self._tree(tmp)
            first_id = artifact["cells"][0]["provenance"]["absolute"][
                "bundle_ids"
            ][0]
            summary_path = roots["a10"] / first_id / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["phase_energy_j"]["decode"] += 1.0
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            with (
                mock.patch.object(
                    mint,
                    "_derive_stack_identity",
                    return_value=artifact["cells"][0]["source_regime"][
                        "stack_identity"
                    ],
                ),
                mock.patch.object(
                    mint,
                    "_authenticated_consumption_summaries",
                    side_effect=self._synthetic_consumption,
                ),
                self.assertRaisesRegex(mint.MintError, "bundle_sha256"),
            ):
                mint.bind_floor_artifact_evidence(
                    artifact,
                    floor_path,
                    roots,
                    strict_validator=lambda _path, _strict: (),
                )


if __name__ == "__main__":
    unittest.main()
