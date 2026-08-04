from __future__ import annotations

import copy
import hashlib
import inspect
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.detection_floor import (
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
    complete_bundle_sha256,
)
from joulewise.floor_extraction import validate_extraction_spec
from joulewise.whole_window import (
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
)
from scripts import mint_floor_artifact as mint1
from scripts import mint_floor_artifact_generalized as generalized
from tests.test_mint_floor_artifact import (
    PLAN_SOURCE,
    allowance,
    authenticated_components,
    member,
    report_floor,
    source_regime,
    stack_identity,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
MINT1_PINSET = REPO_ROOT / "scripts" / "floor_mint_pinsets" / "mint1.json"
SEVEN_B_CONFIG_ROOT = (
    REPO_ROOT / "configs" / "campaigns" / "qwen25_7b_decode_floor_v1"
)
SEVEN_B_PLAN = SEVEN_B_CONFIG_ROOT / "calibration_plan.json"
SEVEN_B_FAMILY = (
    SEVEN_B_CONFIG_ROOT
    / "condition_families"
    / "condition_family_df_ph_decode_qwen25_7b.json"
)
SEVEN_B_BASIS_SHA256 = (
    "3ff9128b170136c57eea1376e954d32736d82d319d0d82bd1b64a78e616f1173"
)
SEVEN_B_ABSOLUTE_FLOOR_J = 6.294380135190098
SEVEN_B_COMPARATIVE_FLOOR_J = 13.998036715259254
SEVEN_B_OPERATIVE_LITERAL = "13.998037"
SEVEN_B_ABSOLUTE_ALLOWANCE_J = 0.4
SEVEN_B_COMPARATIVE_ALLOWANCE_J = SEVEN_B_ABSOLUTE_ALLOWANCE_J
SEVEN_B_EVIDENCE_ROOT_ID = "window_7bfloor_20260729"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_pinset(root: Path, value: dict) -> tuple[Path, str]:
    path = root / "pinset.json"
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path, file_sha256(path)


def seven_b_pinset() -> dict:
    plan_sha256 = file_sha256(SEVEN_B_PLAN)
    family = load_json(SEVEN_B_FAMILY)
    family_sha256 = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, family)
    return {
        "schema_version": generalized.PINSET_SCHEMA_VERSION,
        "mint_tool_version": "joulewise.floor_mint.generalized.v1",
        "plan": {
            "plan_id": "qwen25-7b-decode-floor-v1-m3max",
            "sha256": plan_sha256,
            "declared_calibration_scope": "production_window",
            "artifact_calibration_scope": "production_window",
        },
        "artifact": {
            "cell_id": "df-ph-decode-qwen25-7b-floor",
            "transport_group_id": (
                "tg-df-ph-decode-qwen25-7b-production-v1"
            ),
            "source_class": "prospective",
        },
        "cell": {
            "condition_family_id": "df-ph-decode-qwen25-7b",
            "condition_family_sha256": family_sha256,
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
            "target_precheck_path": ["phase", "decode"],
            "operative_floor_six_decimal": SEVEN_B_OPERATIVE_LITERAL,
        },
        "absolute": {
            "evidence_root_id": SEVEN_B_EVIDENCE_ROOT_ID,
            "calibration_cell_id": (
                "df-ph-decode-qwen25-7b-absolute"
            ),
            "evaluation_basis_sha256": SEVEN_B_BASIS_SHA256,
            "evaluation_basis_members": 59,
            "extraction_spec_members": 50,
            "expected_n": 10,
            "drift_allowance_j": SEVEN_B_ABSOLUTE_ALLOWANCE_J,
            "order_manifest_id": "qwen25-7b-decode-floor-v1-order-v1",
        },
        "comparative": {
            "evidence_root_id": SEVEN_B_EVIDENCE_ROOT_ID,
            "calibration_cell_id": (
                "df-cmp-abba-ph-decode-qwen25-7b"
            ),
            "evaluation_basis_sha256": SEVEN_B_BASIS_SHA256,
            "evaluation_basis_members": 59,
            "extraction_spec_members": 50,
            "expected_n": 10,
            "drift_allowance_j": SEVEN_B_COMPARATIVE_ALLOWANCE_J,
            "order_manifest_id": "qwen25-7b-decode-floor-v1-order-v1",
        },
    }


def seven_b_components() -> tuple[
    dict, mint1.AuthenticatedComponent, mint1.AuthenticatedComponent
]:
    plan = load_json(SEVEN_B_PLAN)
    definition = load_json(SEVEN_B_FAMILY)
    definition_sha256 = canonical_domain_sha256(
        CONDITION_FAMILY_DOMAIN, definition
    )
    binding = {
        "condition_family_id": definition["condition_family_id"],
        "condition_family_definition": definition,
        "condition_family_sha256": definition_sha256,
    }
    absolute_plan = next(
        cell for cell in plan["cells"] if cell["kind"] == "absolute"
    )
    comparative_plan = next(
        cell
        for cell in plan["cells"]
        if cell["kind"] == "comparative_abba"
    )
    absolute_spec_cell = {
        "cell_id": absolute_plan["cell_id"],
        "kind": "absolute",
        "metric": "phase_energy_j.decode",
        "window_class": "phase",
        "condition_family_id": definition["condition_family_id"],
        "condition_family_definitions": {"all": binding},
        "members": [
            {"slot": bundle_id, "bundle_id": bundle_id}
            for bundle_id in absolute_plan["ordered_bundle_ids"]
        ],
    }
    comparative_spec_cell = {
        "cell_id": comparative_plan["cell_id"],
        "kind": "comparative",
        "metric": "phase_energy_j.decode",
        "window_class": "phase",
        "condition_family_id": definition["condition_family_id"],
        "condition_family_definitions": {"A": binding, "B": binding},
        "blocks": [
            {
                "block_id": block["block_id"],
                "members": {
                    member_row["position"]: member_row["bundle_id"]
                    for member_row in block["members"]
                },
            }
            for block in comparative_plan["ordered_blocks"]
        ],
    }
    combined_spec = {
        "schema_version": "joulewise.detection_floor_extraction_spec.v1",
        "cells": [absolute_spec_cell, comparative_spec_cell],
    }

    absolute_attribution_j = (
        SEVEN_B_ABSOLUTE_FLOOR_J - SEVEN_B_ABSOLUTE_ALLOWANCE_J
    )
    absolute_last = absolute_attribution_j / 0.9
    absolute_members = tuple(
        member(
            row["bundle_id"],
            absolute_last if index == 9 else 0.0,
        )
        for index, row in enumerate(absolute_spec_cell["members"])
    )
    comparative_ids = [
        block["members"][position]
        for block in comparative_spec_cell["blocks"]
        for position in ("A1", "B1", "B2", "A2")
    ]
    comparative_members = tuple(
        member(bundle_id, 0.0) for bundle_id in comparative_ids
    )
    comparative_attribution_j = (
        SEVEN_B_COMPARATIVE_FLOOR_J - SEVEN_B_COMPARATIVE_ALLOWANCE_J
    )
    absolute_allowance = allowance(
        SEVEN_B_ABSOLUTE_ALLOWANCE_J, SEVEN_B_BASIS_SHA256
    )
    comparative_allowance = allowance(
        SEVEN_B_COMPARATIVE_ALLOWANCE_J, SEVEN_B_BASIS_SHA256
    )
    regime = source_regime()
    order_manifest = {
        "manifest_id": "qwen25-7b-decode-floor-v1-order-v1",
        "calibration_plan_sha256": file_sha256(SEVEN_B_PLAN),
        "plan_id": plan["plan_id"],
    }
    absolute = mint1.AuthenticatedComponent(
        evidence_root_id=SEVEN_B_EVIDENCE_ROOT_ID,
        calibration_cell_id=absolute_plan["cell_id"],
        kind="absolute",
        report={"diagnostics": {"published_claim_floor": False}},
        report_sha256="1" * 64,
        spec=combined_spec,
        spec_sha256="2" * 64,
        order_manifest=order_manifest,
        order_manifest_sha256="3" * 64,
        campaign_log_sha256="4" * 64,
        cell={
            "floor": report_floor(
                n=10,
                widths=[0.0] * 10,
                drift_widened_guarded_floor_j=SEVEN_B_ABSOLUTE_FLOOR_J,
            )
        },
        spec_cell=absolute_spec_cell,
        members=absolute_members,
        widths_j=(0.0,) * 10,
        whole_window_evaluation_basis_sha256=SEVEN_B_BASIS_SHA256,
        evaluation_basis_member_count=59,
        consumption_semantics_id=(
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        ),
        whole_window_drift_allowance=absolute_allowance,
        source_regime=regime,
        scientific_config_identity_sha256="5" * 64,
        backend="powermetrics",
    )
    comparative = mint1.AuthenticatedComponent(
        evidence_root_id=SEVEN_B_EVIDENCE_ROOT_ID,
        calibration_cell_id=comparative_plan["cell_id"],
        kind="comparative",
        report={"diagnostics": {"published_claim_floor": False}},
        report_sha256="6" * 64,
        spec=combined_spec,
        spec_sha256="7" * 64,
        order_manifest=order_manifest,
        order_manifest_sha256="8" * 64,
        campaign_log_sha256="9" * 64,
        cell={
            "floor": report_floor(
                n=10,
                widths=[comparative_attribution_j, *([0.0] * 9)],
                drift_widened_guarded_floor_j=(
                    SEVEN_B_COMPARATIVE_FLOOR_J
                ),
            ),
            "point_floor_diagnostic": {
                "label": "repeatability_diagnostic",
                "published_claim_floor": False,
            },
        },
        spec_cell=comparative_spec_cell,
        members=comparative_members,
        widths_j=(comparative_attribution_j, *([0.0] * 9)),
        whole_window_evaluation_basis_sha256=SEVEN_B_BASIS_SHA256,
        evaluation_basis_member_count=59,
        consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        whole_window_drift_allowance=comparative_allowance,
        source_regime=regime,
        scientific_config_identity_sha256="5" * 64,
        backend="powermetrics",
    )
    return plan, absolute, comparative


def _synthetic_consumption(
    root: Path,
    _member_ids: set[str],
    basis_sha256: str,
    **_kwargs: object,
) -> tuple[dict[str, dict], str]:
    summaries = {
        bundle.name: load_json(bundle / "summary_metrics.json")
        for bundle in root.iterdir()
        if bundle.is_dir() and (bundle / "summary_metrics.json").is_file()
    }
    semantics = (
        MINTED_CONSUMPTION_SEMANTICS_ID
        if basis_sha256 == mint1.WINDOW_C_EVALUATION_BASIS_SHA256
        else MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
    )
    return summaries, semantics


def _synthetic_allowances(
    _root: Path,
    _member_ids: set[str],
    *,
    evaluation_basis_sha256: str,
    **_kwargs: object,
) -> mock.Mock:
    if evaluation_basis_sha256 == mint1.A10_EVALUATION_BASIS_SHA256:
        value = mint1.A10_DRIFT_ALLOWANCE_J
    elif evaluation_basis_sha256 == mint1.WINDOW_C_EVALUATION_BASIS_SHA256:
        value = mint1.WINDOW_C_DRIFT_ALLOWANCE_J
    else:
        value = SEVEN_B_ABSOLUTE_ALLOWANCE_J
    return mock.Mock(
        status="allowances",
        allowances={
            "gross_energy": allowance(value, evaluation_basis_sha256)
        },
    )


def _configure_fixture_core(core: object) -> object:
    original_authenticate = core._authenticate_component

    def authenticate(paths, **kwargs):
        return original_authenticate(
            paths,
            **kwargs,
            consumption_authenticator=_synthetic_consumption,
            allowance_deriver=_synthetic_allowances,
        )

    core._authenticate_component = authenticate
    core._derive_stack_identity = lambda _config, _metadata: stack_identity()
    core.scientific_config_identity = lambda _config: {"synthetic": "same"}
    return core


def _write_bundle(
    root: Path,
    *,
    bundle_id: str,
    metric_value_j: float,
    half_width_j: float,
    plan_sha256: str,
    block_id: str | None = None,
    position: str | None = None,
) -> tuple[str, str]:
    bundle = root / bundle_id
    bundle.mkdir(parents=True, exist_ok=True)
    tags = [f"calibration-plan-sha256={plan_sha256}"]
    if block_id is not None and position is not None:
        tags.extend(
            [
                f"calibration-abba-block-id={block_id}",
                f"calibration-abba-label={position[0]}",
                (
                    "calibration-abba-sequence-index="
                    f"{('A1', 'B1', 'B2', 'A2').index(position) + 1}"
                ),
            ]
        )
    config = {
        "run_id": bundle_id,
        "run_metadata": {"tags": tags},
        "hardware_target": {"telemetry_backend": "powermetrics"},
    }
    summary = {
        "status": "succeeded",
        "phase_energy_j": {"decode": metric_value_j},
        "energy_anchor_shift_envelopes": {
            "/phase_energy_j/decode": {
                "point_j": metric_value_j,
                "lower_j": metric_value_j - half_width_j,
                "upper_j": metric_value_j + half_width_j,
                "max_abs_delta_j": half_width_j,
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
        json.dumps(config, sort_keys=True), encoding="utf-8"
    )
    (bundle / "metadata.json").write_text("{}", encoding="utf-8")
    (bundle / "summary_metrics.json").write_text(
        json.dumps(summary, sort_keys=True), encoding="utf-8"
    )
    return (
        complete_bundle_sha256(bundle),
        hashlib.sha256((bundle / "config.json").read_bytes()).hexdigest(),
    )


def _install_component_fixture(
    base: Path,
    label: str,
    component: mint1.AuthenticatedComponent,
    *,
    evidence_root: Path | None = None,
) -> generalized.ComponentInputs:
    root = evidence_root or (base / f"{label}-root")
    root.mkdir(parents=True, exist_ok=True)
    spec_path = base / f"{label}-spec.json"
    spec_path.write_text(json.dumps(component.spec), encoding="utf-8")
    member_by_id = {member.bundle_id: member for member in component.members}
    rows = []
    if component.kind == "absolute":
        for index, spec_row in enumerate(component.spec_cell["members"]):
            member = member_by_id[spec_row["bundle_id"]]
            width = component.widths_j[index]
            bundle_sha256, config_sha256 = _write_bundle(
                root,
                bundle_id=member.bundle_id,
                metric_value_j=member.metric_value_j,
                half_width_j=width,
                plan_sha256=component.order_manifest["calibration_plan_sha256"],
            )
            rows.append(
                {
                    "bundle_id": member.bundle_id,
                    "bundle_sha256": bundle_sha256,
                    "config_sha256": config_sha256,
                    "metric_value_j": member.metric_value_j,
                    "anchor_shift_bound_j": width,
                    "excluded": False,
                    "reasons": [],
                }
            )
    else:
        for block_index, block in enumerate(component.spec_cell["blocks"]):
            member_width = component.widths_j[block_index] / 2.0
            for position in ("A1", "B1", "B2", "A2"):
                member = member_by_id[block["members"][position]]
                bundle_sha256, config_sha256 = _write_bundle(
                    root,
                    bundle_id=member.bundle_id,
                    metric_value_j=member.metric_value_j,
                    half_width_j=member_width,
                    plan_sha256=(
                        component.order_manifest["calibration_plan_sha256"]
                    ),
                    block_id=block["block_id"],
                    position=position,
                )
                rows.append(
                    {
                        "bundle_id": member.bundle_id,
                        "bundle_sha256": bundle_sha256,
                        "config_sha256": config_sha256,
                        "metric_value_j": member.metric_value_j,
                        "anchor_shift_bound_j": member_width,
                        "block_id": block["block_id"],
                        "position": position,
                        "excluded": False,
                        "reasons": [],
                    }
                )
    cell = copy.deepcopy(component.cell)
    cell["floor"]["whole_window_drift_allowance_provenance"] = dict(
        component.whole_window_drift_allowance
    )
    cell.update(
        {
            "cell_id": component.calibration_cell_id,
            "kind": component.kind,
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
            "extractable": True,
            "refusal_reasons": [],
            "members": rows,
            "whole_window_drift_allowance": dict(
                component.whole_window_drift_allowance
            ),
        }
    )
    report = {
        "schema_version": mint1.EXTRACTION_SCHEMA_VERSION,
        "spec_schema_version": mint1.EXTRACTION_SPEC_SCHEMA_VERSION,
        "runs_root": str(root),
        "consumption_semantics_id": component.consumption_semantics_id,
        "spec_membership_refusals": [],
        "idle_admission_refusals": [],
        "cells": [cell],
    }
    report_path = base / f"{label}-report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    order = {
        **component.order_manifest,
        "executed_order": [
            {"run_id": bundle_id}
            for bundle_id in mint1._spec_member_ids(component.spec)
        ],
    }
    order_path = base / f"{label}-order.json"
    order_path.write_text(json.dumps(order), encoding="utf-8")
    spec_ids = mint1._spec_member_ids(component.spec)
    reference_count = component.evaluation_basis_member_count - len(spec_ids)
    basis_ids = [
        *spec_ids,
        *(f"{label}-reference-{index}" for index in range(reference_count)),
    ]
    (root / "campaign_log.jsonl").write_text(
        json.dumps(
            {
                "evaluation_basis": {
                    "sha256": component.whole_window_evaluation_basis_sha256,
                    "member_occurrences": [
                        {"bundle_id": bundle_id} for bundle_id in basis_ids
                    ],
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return generalized.ComponentInputs(
        evidence_root=root,
        report_path=report_path,
        spec_path=spec_path,
        order_manifest_path=order_path,
    )


class PinsetTests(unittest.TestCase):
    def test_mint1_pinset_is_exactly_the_original_hard_pin_set(self) -> None:
        pinset = generalized.load_pinset(
            MINT1_PINSET, file_sha256(MINT1_PINSET)
        )
        self.assertEqual(pinset.plan.sha256, mint1.PLAN_SHA256)
        self.assertEqual(pinset.artifact.cell_id, mint1.CELL_ID)
        self.assertEqual(
            pinset.absolute.evaluation_basis_sha256,
            mint1.A10_EVALUATION_BASIS_SHA256,
        )
        self.assertEqual(
            pinset.comparative.evaluation_basis_sha256,
            mint1.WINDOW_C_EVALUATION_BASIS_SHA256,
        )
        self.assertEqual(
            pinset.cell.operative_floor_six_decimal,
            mint1.EXPECTED_OPERATIVE_FLOOR_TEXT,
        )

    def test_pinset_digest_mismatch_refuses(self) -> None:
        with self.assertRaisesRegex(generalized.MintError, "sha256 mismatch"):
            generalized.load_pinset(MINT1_PINSET, "0" * 64)

    def test_pinset_missing_or_extra_fields_refuse(self) -> None:
        source = load_json(MINT1_PINSET)
        cases = {}
        missing = copy.deepcopy(source)
        del missing["cell"]["operative_floor_six_decimal"]
        cases["missing"] = missing
        extra = copy.deepcopy(source)
        extra["absolute"]["derive_floor_from_report"] = True
        cases["extra"] = extra
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for label, value in cases.items():
                with self.subTest(label=label):
                    path, digest = write_pinset(root, value)
                    with self.assertRaisesRegex(
                        generalized.MintError, "schema mismatch"
                    ):
                        generalized.load_pinset(path, digest)

    def test_operative_floor_pin_requires_six_decimal_string(self) -> None:
        value = load_json(MINT1_PINSET)
        value["cell"]["operative_floor_six_decimal"] = 7.377086
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = write_pinset(Path(tmp), value)
            with self.assertRaisesRegex(
                generalized.MintError, "six-decimal literal"
            ):
                generalized.load_pinset(path, digest)

    def test_pinset_cannot_weaken_fixed_decode_contract(self) -> None:
        source = load_json(MINT1_PINSET)
        cases = {
            "metric": ("metric", "phase_energy_j.prefill"),
            "source_class": ("source_class", "retrospective"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for label, (field, replacement) in cases.items():
                with self.subTest(label=label):
                    value = copy.deepcopy(source)
                    if field == "metric":
                        value["cell"]["metric"] = replacement
                    elif field == "source_class":
                        value["artifact"]["source_class"] = replacement
                    path, digest = write_pinset(root, value)
                    with self.assertRaisesRegex(
                        generalized.MintError, "must equal"
                    ):
                        generalized.load_pinset(path, digest)


class GeneralizedMintTests(unittest.TestCase):
    def test_mint1_builder_path_is_byte_identical(self) -> None:
        plan, absolute, comparative = authenticated_components()
        expected = mint1.mint_authenticated_artifact(
            artifact_id="synthetic-mint-1",
            plan=plan,
            plan_sha256=mint1.PLAN_SHA256,
            calibration_plan_relative_path="calibration_plan.json",
            absolute=absolute,
            comparative=comparative,
            project_commit="0" * 40,
            project_tree_state="clean",
        )
        actual = generalized.mint_authenticated_artifact(
            pinset_path=MINT1_PINSET,
            pinset_sha256=file_sha256(MINT1_PINSET),
            artifact_id="synthetic-mint-1",
            plan=plan,
            plan_sha256=mint1.PLAN_SHA256,
            calibration_plan_relative_path="calibration_plan.json",
            absolute=absolute,
            comparative=comparative,
            project_commit="0" * 40,
            project_tree_state="clean",
        )
        expected_bytes = (
            json.dumps(expected, indent=2, sort_keys=True, allow_nan=False)
            + "\n"
        ).encode("utf-8")
        actual_bytes = (
            json.dumps(actual, indent=2, sort_keys=True, allow_nan=False)
            + "\n"
        ).encode("utf-8")
        self.assertEqual(actual_bytes, expected_bytes)

    def test_7b_shaped_gate_build_and_validator_path_passes(self) -> None:
        plan, absolute, comparative = seven_b_components()
        self.assertEqual(validate_extraction_spec(absolute.spec), [])
        root_order_manifest = load_json(SEVEN_B_CONFIG_ROOT / "order_manifest.json")
        spec_ids = mint1._spec_member_ids(absolute.spec)
        mint1._validate_order(
            root_order_manifest,
            target_ids=[row.bundle_id for row in absolute.members],
            spec_ids=spec_ids,
        )
        mint1._validate_order(
            root_order_manifest,
            target_ids=[row.bundle_id for row in comparative.members],
            spec_ids=spec_ids,
        )
        with tempfile.TemporaryDirectory() as tmp:
            pinset_path, pinset_sha256 = write_pinset(
                Path(tmp), seven_b_pinset()
            )
            generalized.pre_registration_gate(
                pinset_path=pinset_path,
                pinset_sha256=pinset_sha256,
                plan=plan,
                plan_sha256=file_sha256(SEVEN_B_PLAN),
                absolute=absolute,
                comparative=comparative,
            )
            artifact = generalized.mint_authenticated_artifact(
                pinset_path=pinset_path,
                pinset_sha256=pinset_sha256,
                artifact_id="synthetic-7b-decode-floor",
                plan=plan,
                plan_sha256=file_sha256(SEVEN_B_PLAN),
                calibration_plan_relative_path="calibration_plan.json",
                absolute=absolute,
                comparative=comparative,
                project_commit="0" * 40,
                project_tree_state="clean",
            )
            validation_errors = generalized.validate_floor_artifact(
                artifact=artifact,
                pinset_path=pinset_path,
                pinset_sha256=pinset_sha256,
            )
        self.assertEqual(validation_errors, [])
        self.assertEqual(artifact["calibration_scope"], "production_window")
        self.assertEqual(
            artifact["provenance"]["calibration_plan"][
                "declared_calibration_scope"
            ],
            "production_window",
        )
        self.assertEqual(
            artifact["cells"][0]["key"]["condition_family_id"],
            "df-ph-decode-qwen25-7b",
        )
        self.assertEqual(
            format(artifact["cells"][0]["floor_gate_j"], ".6f"),
            SEVEN_B_OPERATIVE_LITERAL,
        )
        provenance = artifact["cells"][0]["provenance"]
        self.assertEqual(
            provenance["absolute"]["evidence_root_id"],
            SEVEN_B_EVIDENCE_ROOT_ID,
        )
        self.assertEqual(
            provenance["comparative"]["evidence_root_id"],
            SEVEN_B_EVIDENCE_ROOT_ID,
        )

    def test_7b_mismatched_operative_pin_refuses(self) -> None:
        plan, absolute, comparative = seven_b_components()
        pins = seven_b_pinset()
        pins["cell"]["operative_floor_six_decimal"] = "13.998038"
        with tempfile.TemporaryDirectory() as tmp:
            pinset_path, pinset_sha256 = write_pinset(Path(tmp), pins)
            with self.assertRaisesRegex(
                generalized.MintError, "formatted operative floor mismatch"
            ):
                generalized.mint_authenticated_artifact(
                    pinset_path=pinset_path,
                    pinset_sha256=pinset_sha256,
                    artifact_id="must-refuse",
                    plan=plan,
                    plan_sha256=file_sha256(SEVEN_B_PLAN),
                    calibration_plan_relative_path="calibration_plan.json",
                    absolute=absolute,
                    comparative=comparative,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )

    def test_7b_mismatched_plan_and_manifest_pins_refuse(self) -> None:
        plan, absolute, comparative = seven_b_components()
        cases = {
            "plan": (
                "calibration plan identity mismatch",
                {**plan, "plan_id": "wrong"},
                absolute,
            ),
            "manifest": (
                "order manifest plan id mismatch",
                plan,
                replace(
                    absolute,
                    order_manifest={**absolute.order_manifest, "plan_id": "wrong"},
                ),
            ),
        }
        with tempfile.TemporaryDirectory() as tmp:
            pinset_path, pinset_sha256 = write_pinset(
                Path(tmp), seven_b_pinset()
            )
            for label, (message, candidate_plan, candidate_absolute) in cases.items():
                with self.subTest(label=label):
                    with self.assertRaisesRegex(generalized.MintError, message):
                        generalized.pre_registration_gate(
                            pinset_path=pinset_path,
                            pinset_sha256=pinset_sha256,
                            plan=candidate_plan,
                            plan_sha256=file_sha256(SEVEN_B_PLAN),
                            absolute=candidate_absolute,
                            comparative=comparative,
                        )


class FullPathTests(unittest.TestCase):
    @staticmethod
    def _dummy_inputs(root: Path) -> generalized.ComponentInputs:
        return generalized.ComponentInputs(
            evidence_root=root / "unused-root",
            report_path=root / "unused-report.json",
            spec_path=root / "unused-spec.json",
            order_manifest_path=root / "unused-order.json",
        )

    def _call_generalized(
        self,
        *,
        root: Path,
        pinset_path: Path,
        pinset_sha256: str,
        plan_path: Path | None = None,
        absolute_inputs: generalized.ComponentInputs | None = None,
        comparative_inputs: generalized.ComponentInputs | None = None,
        floor_path: Path | None = None,
        statement_path: Path | None = None,
    ) -> dict:
        dummy = self._dummy_inputs(root)
        return generalized.mint_floor_artifact(
            pinset_path=pinset_path,
            pinset_sha256=pinset_sha256,
            artifact_id="full-path-fixture",
            floor_path=floor_path or (root / "floor.json"),
            statement_path=statement_path or (root / "single-count.txt"),
            calibration_plan_path=plan_path or (root / "unused-plan.json"),
            calibration_plan_relative_path="calibration_plan.json",
            absolute_inputs=absolute_inputs or dummy,
            comparative_inputs=comparative_inputs or dummy,
            project_commit="0" * 40,
            project_tree_state="clean",
            strict_validator=lambda _path, _strict: (),
        )

    @staticmethod
    def _patched_fresh_loader():
        original_loader = generalized._fresh_original_core

        def load():
            return _configure_fixture_core(original_loader())

        return mock.patch.object(
            generalized, "_fresh_original_core", side_effect=load
        )

    def test_mint1_full_path_is_byte_identical_to_review_pinned_mint_core(
        self,
    ) -> None:
        plan, absolute, comparative = authenticated_components()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "source-plan.json"
            plan_path.write_bytes(PLAN_SOURCE.read_bytes())
            absolute_inputs = _install_component_fixture(
                root, "absolute", absolute
            )
            comparative_inputs = _install_component_fixture(
                root, "comparative", comparative
            )
            expected_dir = root / "expected"
            actual_dir = root / "actual"
            expected_dir.mkdir()
            actual_dir.mkdir()
            for directory in (expected_dir, actual_dir):
                (directory / "calibration_plan.json").write_bytes(
                    PLAN_SOURCE.read_bytes()
                )
            expected_floor = expected_dir / "floor.json"
            expected_statement = expected_dir / "single-count.txt"
            original_authenticate = mint1._authenticate_component

            def authenticate(paths, **kwargs):
                return original_authenticate(
                    paths,
                    **kwargs,
                    consumption_authenticator=_synthetic_consumption,
                    allowance_deriver=_synthetic_allowances,
                )

            with (
                mock.patch.object(
                    mint1,
                    "_authenticate_component",
                    side_effect=authenticate,
                ),
                mock.patch.object(
                    mint1, "_derive_stack_identity", return_value=stack_identity()
                ),
                mock.patch.object(
                    mint1,
                    "scientific_config_identity",
                    return_value={"synthetic": "same"},
                ),
            ):
                mint1.mint_floor_artifact(
                    artifact_id="full-path-fixture",
                    floor_path=expected_floor,
                    statement_path=expected_statement,
                    calibration_plan_path=plan_path,
                    calibration_plan_relative_path="calibration_plan.json",
                    absolute_paths=mint1.ComponentPaths(
                        evidence_root_id="a10",
                        evidence_root=absolute_inputs.evidence_root,
                        report_path=absolute_inputs.report_path,
                        spec_path=absolute_inputs.spec_path,
                        order_manifest_path=absolute_inputs.order_manifest_path,
                        calibration_cell_id=mint1.A10_CELL_ID,
                        expected_kind="absolute",
                    ),
                    comparative_paths=mint1.ComponentPaths(
                        evidence_root_id="window_c",
                        evidence_root=comparative_inputs.evidence_root,
                        report_path=comparative_inputs.report_path,
                        spec_path=comparative_inputs.spec_path,
                        order_manifest_path=(
                            comparative_inputs.order_manifest_path
                        ),
                        calibration_cell_id=mint1.WINDOW_C_CELL_ID,
                        expected_kind="comparative",
                    ),
                    project_commit="0" * 40,
                    project_tree_state="clean",
                    strict_validator=lambda _path, _strict: (),
                )
            actual_floor = actual_dir / "floor.json"
            actual_statement = actual_dir / "single-count.txt"
            with self._patched_fresh_loader():
                self._call_generalized(
                    root=root,
                    pinset_path=MINT1_PINSET,
                    pinset_sha256=file_sha256(MINT1_PINSET),
                    plan_path=plan_path,
                    absolute_inputs=absolute_inputs,
                    comparative_inputs=comparative_inputs,
                    floor_path=actual_floor,
                    statement_path=actual_statement,
                )
            self.assertEqual(actual_floor.read_bytes(), expected_floor.read_bytes())
            self.assertEqual(
                actual_statement.read_bytes(), expected_statement.read_bytes()
            )

    def test_truthful_7b_fixture_mints_through_full_path(self) -> None:
        plan, absolute, comparative = seven_b_components()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "source-plan.json"
            plan_path.write_bytes(SEVEN_B_PLAN.read_bytes())
            output = root / "output"
            output.mkdir()
            (output / "calibration_plan.json").write_bytes(
                SEVEN_B_PLAN.read_bytes()
            )
            evidence_root = root / SEVEN_B_EVIDENCE_ROOT_ID
            absolute_inputs = _install_component_fixture(
                root,
                "seven-b-absolute",
                absolute,
                evidence_root=evidence_root,
            )
            comparative_inputs = _install_component_fixture(
                root,
                "seven-b-comparative",
                comparative,
                evidence_root=evidence_root,
            )
            pinset_path, pinset_sha256 = write_pinset(
                root, seven_b_pinset()
            )
            with self._patched_fresh_loader():
                artifact = self._call_generalized(
                    root=root,
                    pinset_path=pinset_path,
                    pinset_sha256=pinset_sha256,
                    plan_path=plan_path,
                    absolute_inputs=absolute_inputs,
                    comparative_inputs=comparative_inputs,
                    floor_path=output / "floor.json",
                    statement_path=output / "single-count.txt",
                )
            self.assertEqual(
                generalized.validate_floor_artifact(
                    artifact=artifact,
                    pinset_path=pinset_path,
                    pinset_sha256=pinset_sha256,
                ),
                [],
            )
            provenance = artifact["cells"][0]["provenance"]
            self.assertEqual(
                {
                    provenance["absolute"]["evidence_root_id"],
                    provenance["comparative"]["evidence_root_id"],
                },
                {SEVEN_B_EVIDENCE_ROOT_ID},
            )

    def test_bad_pinset_digest_refuses_at_full_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(generalized.MintError, "sha256 mismatch"):
                self._call_generalized(
                    root=root,
                    pinset_path=MINT1_PINSET,
                    pinset_sha256="0" * 64,
                )

    def test_duplicate_nonfinite_and_malformed_json_refuse_at_full_path(self) -> None:
        source = MINT1_PINSET.read_text(encoding="utf-8")
        duplicate = (
            '{"schema_version":"duplicate",' + source.lstrip()[1:]
        ).encode("utf-8")
        nonfinite_value = load_json(MINT1_PINSET)
        nonfinite_value["absolute"]["drift_allowance_j"] = float("nan")
        cases = {
            "duplicate": (duplicate, "duplicate JSON key"),
            "nonfinite": (
                json.dumps(nonfinite_value).encode("utf-8"),
                "non-finite JSON number",
            ),
            "malformed": (b'{"schema_version":', "not valid UTF-8 JSON"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for label, (raw, message) in cases.items():
                with self.subTest(label=label):
                    path = root / f"{label}.json"
                    path.write_bytes(raw)
                    # The pinset-load refusal must fire on its own merits:
                    # assert the load-stage message so a missing downstream
                    # plan cannot satisfy this test with an unrelated
                    # MintError.
                    with self.assertRaisesRegex(
                        generalized.MintError, message
                    ):
                        self._call_generalized(
                            root=root,
                            pinset_path=path,
                            pinset_sha256=hashlib.sha256(raw).hexdigest(),
                        )

    def test_every_pinset_key_is_required_at_full_path(self) -> None:
        source = load_json(MINT1_PINSET)

        def key_paths(value: dict, prefix: tuple[str, ...] = ()):
            for key, child in value.items():
                path = (*prefix, key)
                yield path
                if isinstance(child, dict):
                    yield from key_paths(child, path)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path_parts in key_paths(source):
                with self.subTest(path=".".join(path_parts)):
                    candidate = copy.deepcopy(source)
                    parent = candidate
                    for part in path_parts[:-1]:
                        parent = parent[part]
                    del parent[path_parts[-1]]
                    path, digest = write_pinset(root, candidate)
                    with self.assertRaisesRegex(
                        generalized.MintError, "schema mismatch"
                    ):
                        self._call_generalized(
                            root=root,
                            pinset_path=path,
                            pinset_sha256=digest,
                        )

    def test_binding_and_exclusive_write_refuse_at_full_path(self) -> None:
        _plan, absolute, comparative = authenticated_components()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "source-plan.json"
            plan_path.write_bytes(PLAN_SOURCE.read_bytes())
            absolute_inputs = _install_component_fixture(
                root, "absolute", absolute
            )
            comparative_inputs = _install_component_fixture(
                root, "comparative", comparative
            )
            output = root / "output"
            output.mkdir()
            persisted_plan = output / "calibration_plan.json"
            persisted_plan.write_text("{}", encoding="utf-8")
            floor = output / "floor.json"
            statement = output / "single-count.txt"
            with (
                self._patched_fresh_loader(),
                self.assertRaisesRegex(
                    generalized.MintError, "plan bytes do not match"
                ),
            ):
                self._call_generalized(
                    root=root,
                    pinset_path=MINT1_PINSET,
                    pinset_sha256=file_sha256(MINT1_PINSET),
                    plan_path=plan_path,
                    absolute_inputs=absolute_inputs,
                    comparative_inputs=comparative_inputs,
                    floor_path=floor,
                    statement_path=statement,
                )
            persisted_plan.write_bytes(PLAN_SOURCE.read_bytes())
            with self._patched_fresh_loader():
                self._call_generalized(
                    root=root,
                    pinset_path=MINT1_PINSET,
                    pinset_sha256=file_sha256(MINT1_PINSET),
                    plan_path=plan_path,
                    absolute_inputs=absolute_inputs,
                    comparative_inputs=comparative_inputs,
                    floor_path=floor,
                    statement_path=statement,
                )
            original = floor.read_bytes()
            with (
                self._patched_fresh_loader(),
                self.assertRaisesRegex(generalized.MintError, "overwrite"),
            ):
                self._call_generalized(
                    root=root,
                    pinset_path=MINT1_PINSET,
                    pinset_sha256=file_sha256(MINT1_PINSET),
                    plan_path=plan_path,
                    absolute_inputs=absolute_inputs,
                    comparative_inputs=comparative_inputs,
                    floor_path=floor,
                    statement_path=statement,
                )
            self.assertEqual(floor.read_bytes(), original)


class CoreCompatibilityTests(unittest.TestCase):
    def test_mint_floor_artifact_signature_is_review_pinned(self) -> None:
        expected = (
            "(*, artifact_id: 'str', floor_path: 'Path', statement_path: 'Path', "
            "calibration_plan_path: 'Path', "
            "calibration_plan_relative_path: 'str', "
            "absolute_paths: 'ComponentPaths', comparative_paths: 'ComponentPaths', "
            "project_commit: 'str', project_tree_state: 'str', "
            "strict_validator: 'StrictValidator', "
            "consumption_semantics_id: 'str | None' = None, "
            "calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None) "
            "-> 'Mapping[str, Any]'"
        )
        self.assertEqual(
            str(inspect.signature(mint1.mint_floor_artifact)),
            expected,
        )
        self.assertEqual(
            generalized._CORE_SIGNATURES["mint_floor_artifact"],
            expected,
        )

    def test_fresh_core_is_removed_from_sys_modules_after_load(self) -> None:
        core = generalized._fresh_original_core()
        self.assertNotIn(core.__name__, sys.modules)

    def test_missing_or_renamed_core_symbol_refuses_loudly(self) -> None:
        with self.assertRaisesRegex(
            generalized.MintError, "missing or renamed symbols"
        ):
            generalized._assert_core_interface(SimpleNamespace())

    def test_core_signature_drift_refuses_loudly(self) -> None:
        core = generalized._fresh_original_core()
        core.mint_floor_artifact = lambda: None
        with self.assertRaisesRegex(
            generalized.MintError, "mint_floor_artifact signature expected"
        ):
            generalized._assert_core_interface(core)

    def test_repr_spoofed_sentinel_default_refuses_loudly(self) -> None:
        class _FauxNone:
            def __repr__(self) -> str:
                return "None"

        core = generalized._fresh_original_core()
        core.mint_floor_artifact.__kwdefaults__[
            "calibration_ledger_snapshot"
        ] = _FauxNone()
        self.assertEqual(
            str(inspect.signature(core.mint_floor_artifact)),
            generalized._CORE_SIGNATURES["mint_floor_artifact"],
        )
        with self.assertRaisesRegex(
            generalized.MintError,
            "calibration_ledger_snapshot default is not the None sentinel",
        ):
            generalized._assert_core_interface(core)


if __name__ == "__main__":
    unittest.main()
