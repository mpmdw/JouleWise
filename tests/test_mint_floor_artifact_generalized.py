from __future__ import annotations

import copy
import gc
import hashlib
import io
import inspect
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import UTC, datetime, timedelta
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import detection_floor
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.analysis_engine.registry import (
    normalized_json_bytes,
    render_dispatch_receipt,
    render_strict_validation_evidence,
    sha256_bytes,
)
from joulewise.bundle_read import BundleReader
from joulewise.detection_floor import (
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
    complete_bundle_sha256,
)
from joulewise.calibration_bracketing import (
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    build_calibration_bracket_binding,
    calibration_bracket_for_bundles,
    load_calibration_acceptance_bound,
    load_calibration_candidate,
)
from joulewise.calibration_ledger import (
    CUSTODY_STORE_MANIFEST_NAME,
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    append_bracket_session_receipt,
    artifact_hashes,
    calibration_custody_store_manifest_bytes,
    content_id_from_artifact_hashes,
    finalize_bracket_session_slot,
    load_calibration_ledger_snapshot,
    terminal_head_pin_for_session,
)
from joulewise.controller import _load_instrument_calibration_attachment
from joulewise.campaign_provenance import campaign_provenance_attestation
from joulewise.floor_extraction import (
    CellReport,
    MemberReport,
    extract_cells,
    validate_d117_mint_consumption_report,
    validate_extraction_spec,
)
from joulewise.whole_window import (
    ADAPTER_CONTINUITY_SCHEMA,
    IDLE_ADMISSION_CORE_SCHEMA,
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    NEG8_BRACKET_SCHEMA,
    WHOLE_WINDOW_SCHEMA,
    AuthenticatedConsumptionSession,
    build_neg8_drift_bound_artifact,
    build_evaluation_basis,
    build_row_provenance,
    canonical_sha256,
    neg8_freshness_bindings_from_metadata,
    whole_window_refusal_reasons,
)
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
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


def _role_components(
    absolute: mint1.AuthenticatedComponent,
    comparative: mint1.AuthenticatedComponent,
    *,
    role: str,
    family_id: str,
    plan_id: str,
    plan_sha256: str,
) -> tuple[
    mint1.AuthenticatedComponent,
    mint1.AuthenticatedComponent,
    dict,
]:
    metric = f"phase_energy_j.{role}"
    source_binding = absolute.spec_cell["condition_family_definitions"]["all"]
    definition = copy.deepcopy(source_binding["condition_family_definition"])
    definition["condition_family_id"] = family_id
    family_sha256 = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition)
    binding = {
        "condition_family_id": family_id,
        "condition_family_definition": definition,
        "condition_family_sha256": family_sha256,
    }

    def convert(
        component: mint1.AuthenticatedComponent,
    ) -> mint1.AuthenticatedComponent:
        spec_cell = copy.deepcopy(component.spec_cell)
        calibration_cell_id = f"{component.calibration_cell_id}-{role}"
        spec_cell["cell_id"] = calibration_cell_id
        spec_cell["metric"] = metric
        spec_cell["condition_family_id"] = family_id
        spec_cell["condition_family_definitions"] = (
            {"all": binding}
            if component.kind == "absolute"
            else {"A": binding, "B": binding}
        )
        order_manifest = {
            **component.order_manifest,
            "plan_id": plan_id,
            "calibration_plan_sha256": plan_sha256,
        }
        return replace(
            component,
            calibration_cell_id=calibration_cell_id,
            spec_cell=spec_cell,
            order_manifest=order_manifest,
        )

    return convert(absolute), convert(comparative), binding


def _v2_component_pin(component: mint1.AuthenticatedComponent) -> dict:
    return {
        "evidence_root_id": component.evidence_root_id,
        "calibration_cell_id": component.calibration_cell_id,
        "evaluation_basis_sha256": (
            component.whole_window_evaluation_basis_sha256
        ),
        "evaluation_basis_members": component.evaluation_basis_member_count,
        "extraction_spec_sha256": component.spec_sha256,
        "extraction_spec_members": len(
            set(_fixture_spec_member_ids(component.spec))
        ),
        "expected_n": (
            len(component.members)
            if component.kind == "absolute"
            else len(component.members) // 4
        ),
        "drift_allowance_j": component.whole_window_drift_allowance[
            "allowance_j"
        ],
        "order_manifest_id": component.order_manifest["manifest_id"],
        "order_manifest_sha256": component.order_manifest_sha256,
        "consumption_semantics_id": component.consumption_semantics_id,
        "members": [
            {
                "bundle_id": member_row.bundle_id,
                "config_sha256": member_row.config_sha256,
            }
            for member_row in component.members
        ],
    }


def _production_report_cell(
    component: mint1.AuthenticatedComponent,
) -> dict:
    """Emit the exact governed CellReport wire used by extract_cells."""

    core = generalized._fresh_original_core()
    if component.kind == "absolute":
        estimate = core.absolute_false_effect_floor(
            [member_row.metric_value_j for member_row in component.members],
            admissible_half_widths_j=component.widths_j,
        )
    else:
        _blocks, deltas = core._comparative_blocks(component)
        estimate = core.comparative_false_effect_floor(
            deltas,
            admissible_half_widths_j=component.widths_j,
        )
    rows = tuple(
        MemberReport(
            slot=member_row.bundle_id,
            bundle_id=member_row.bundle_id,
            block_id=None,
            position=None,
            value_j=member_row.metric_value_j,
            cooldown_result="completed",
            cooldown_verified=True,
            cap_hit=False,
            excluded=False,
            reasons=(),
            anchor_shift_bound_j=0.0,
            operative_anchor_envelope=None,
            consumption_provenance=None,
            summary_sha256="0" * 64,
            bundle_sha256=member_row.bundle_sha256,
            config_sha256=member_row.config_sha256,
        )
        for member_row in component.members
    )
    return CellReport(
        cell_id=component.calibration_cell_id,
        kind=component.kind,
        metric=component.spec_cell["metric"],
        window_class=component.spec_cell["window_class"],
        cap_hit_policy="exclude_same_slot",
        members=rows,
        excluded_slots=(),
        n_planned=len(rows),
        n_admitted=len(rows),
        refusal_reasons=(),
        floor=estimate,
        anchor_shift_bound_max_j=max(component.widths_j, default=0.0),
        whole_window_drift_allowance=component.whole_window_drift_allowance,
    ).as_row()


def _fixture_spec_member_ids(spec: dict) -> tuple[str, ...]:
    """Independent physical-member projection for the golden pin fixture."""

    ids: list[str] = []
    for cell in spec.get("cells", []):
        if not isinstance(cell, dict):
            continue
        for row in cell.get("members", []):
            if isinstance(row, dict) and isinstance(row.get("bundle_id"), str):
                ids.append(row["bundle_id"])
        for block in cell.get("blocks", []):
            members = block.get("members") if isinstance(block, dict) else None
            if isinstance(members, dict):
                ids.extend(
                    bundle_id
                    for bundle_id in members.values()
                    if isinstance(bundle_id, str)
                )
    return tuple(ids)


def _v2_postcollection(
    absolute: mint1.AuthenticatedComponent,
    comparative: mint1.AuthenticatedComponent,
    *,
    bracket_binding: dict,
    bracket_binding_sha256: str,
    extraction_report_sha256: str,
) -> dict:
    absolute_full = "6.294380135190098"
    comparative_full = "13.998036715259254"
    return {
        "absolute_evaluation_basis_sha256": (
            absolute.whole_window_evaluation_basis_sha256
        ),
        "absolute_evaluation_basis_members": (
            absolute.evaluation_basis_member_count
        ),
        "comparative_evaluation_basis_sha256": (
            comparative.whole_window_evaluation_basis_sha256
        ),
        "comparative_evaluation_basis_members": (
            comparative.evaluation_basis_member_count
        ),
        "pre_receipt_sha256": bracket_binding["endpoints"]["pre"][
            "receipt_digest"
        ],
        "pre_content_sha256": bracket_binding["endpoints"]["pre"][
            "content_digest"
        ],
        "post_receipt_sha256": bracket_binding["endpoints"]["post"][
            "receipt_digest"
        ],
        "post_content_sha256": bracket_binding["endpoints"]["post"][
            "content_digest"
        ],
        "bracket_binding_sha256": bracket_binding_sha256,
        "terminal_ledger_head_sha256": bracket_binding["terminal_head"][
            "head_digest"
        ],
        "observed_drift_s": "0.001000",
        "allowance_rule": generalized.V2_ALLOWANCE_RULE,
        "bracket_screen_s": generalized.V2_BRACKET_SCREEN_S,
        "applied_allowance_s": generalized.V2_BRACKET_SCREEN_S,
        "allowance_embedding_count": 1,
        "extraction_report_sha256": extraction_report_sha256,
        "absolute_floor_full_precision": absolute_full,
        "comparative_floor_full_precision": comparative_full,
        "operative_floor_full_precision": comparative_full,
        "absolute_floor_six_decimal": "6.294380",
        "comparative_floor_six_decimal": "13.998037",
        "operative_floor_six_decimal": "13.998037",
    }


def _fixture_canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _fixture_artifact_sha256(value: object) -> str:
    payload = (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _synthetic_bracket_evidence(
    producer_index: int,
    *,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path,
    sequence_start: int,
) -> tuple[dict, list[dict], list[SimpleNamespace], SimpleNamespace]:
    digit_sets = (
        ("a", "b", "c", "d", "e"),
        ("4", "5", "6", "7", "8"),
        ("9", "0", "1", "2", "3"),
    )
    digits = digit_sets[producer_index % len(digit_sets)]
    capability_receipt = digits[0] * 64
    pre_receipt = digits[1] * 64
    pre_content = digits[2] * 64
    post_receipt = digits[3] * 64
    post_content = digits[4] * 64
    window_id = f"synthetic-window-{producer_index}"
    session_id = f"synthetic-session-{producer_index}"
    binding = {
        "schema_version": generalized.V2_BRACKET_BINDING_SCHEMA,
        "ledger_schema": "joulewise.calibration_observation_ledger.v1",
        "session_id": session_id,
        "window_id": window_id,
        "plan_id": plan_id,
        "plan_sha256": plan_sha256,
        "evidence_root_id": evidence_root_id,
        "runs_root": str(runs_root.resolve(strict=False)),
        "capability_receipt_digest": capability_receipt,
        "terminal_head": {
            "sequence": sequence_start + 2,
            "head_digest": post_receipt,
            "ledger_schema": "joulewise.calibration_observation_ledger.v1",
        },
        "endpoints": {
            "pre": {
                "attempt_id": f"attempt-{producer_index}-pre",
                "receipt_digest": pre_receipt,
                "content_digest": pre_content,
            },
            "post": {
                "attempt_id": f"attempt-{producer_index}-post",
                "receipt_digest": post_receipt,
                "content_digest": post_content,
            },
        },
    }
    binding["binding_digest"] = _fixture_canonical_sha256(binding)
    receipts = [
        {"receipt_digest": capability_receipt},
        {"receipt_digest": pre_receipt},
        {"receipt_digest": post_receipt},
    ]
    common = {
        "disposition": "valid",
        "bracket_session_id": session_id,
        "bracket_window_id": window_id,
        "bracket_plan_id": plan_id,
        "bracket_plan_sha256": plan_sha256,
        "bracket_evidence_root_id": evidence_root_id,
        "bracket_runs_root": str(runs_root.resolve(strict=False)),
    }
    observations = [
        SimpleNamespace(
            **common,
            sequence=sequence_start + 1,
            attempt_id=f"attempt-{producer_index}-pre",
            receipt_digest=pre_receipt,
            content_id=pre_content,
            exact_bound_lexeme_s="0.020000",
            bracket_slot="pre",
        ),
        SimpleNamespace(
            **common,
            sequence=sequence_start + 2,
            attempt_id=f"attempt-{producer_index}-post",
            receipt_digest=post_receipt,
            content_id=post_content,
            exact_bound_lexeme_s="0.021000",
            bracket_slot="post",
        ),
    ]
    session = SimpleNamespace(
        session_id=session_id,
        state="finalized",
        window_id=window_id,
        plan_id=plan_id,
        plan_sha256=plan_sha256,
        evidence_root_id=evidence_root_id,
        runs_root=str(runs_root.resolve(strict=False)),
        capability_receipt_digest=capability_receipt,
        finalized_slots={"pre": observations[0], "post": observations[1]},
    )
    return binding, receipts, observations, session


def _synthetic_verdict_bracket(
    observations: list[SimpleNamespace],
) -> dict:
    return {
        role: {
            "bracket_session_id": observation.bracket_session_id,
            "bracket_window_id": observation.bracket_window_id,
            "bracket_plan_id": observation.bracket_plan_id,
            "bracket_plan_sha256": observation.bracket_plan_sha256,
            "bracket_evidence_root_id": observation.bracket_evidence_root_id,
            "bracket_runs_root": observation.bracket_runs_root,
            "bracket_slot": observation.bracket_slot,
            "attempt_id": observation.attempt_id,
            "ledger_receipt_digest": observation.receipt_digest,
            "content_id": observation.content_id,
        }
        for role, observation in zip(("pre", "post"), observations)
    }


def synthetic_v2_fixture() -> tuple[
    dict,
    dict[str, generalized.V2ProducerInputs],
    SimpleNamespace,
]:
    base_plan, base_absolute, base_comparative = seven_b_components()
    producers = []
    inputs = {}
    all_cell_ids = []
    all_group_ids = []
    all_allowlists = []
    ledger_receipts: list[dict] = []
    ledger_observations: list[SimpleNamespace] = []
    ledger_sessions: dict[str, SimpleNamespace] = {}
    for producer_index in range(2):
        plan_id = f"synthetic-d117-floor-plan-{producer_index}"
        plan_sha256 = f"{producer_index + 2:x}" * 64
        declared_sha256 = plan_sha256
        sidecar_sha256 = f"{producer_index + 6:x}" * 64
        evidence_root_id = f"synthetic-d117-root-{producer_index}"
        evidence_root = Path(f"/synthetic/evidence/{evidence_root_id}")
        plan = {
            **base_plan,
            "plan_id": plan_id,
            "calibration_scope": "production_window",
        }
        binding, receipts, observations, session = _synthetic_bracket_evidence(
            producer_index,
            plan_id=plan_id,
            plan_sha256=plan_sha256,
            evidence_root_id=evidence_root_id,
            runs_root=evidence_root,
            sequence_start=1 + 3 * producer_index,
        )
        ledger_receipts.extend(receipts)
        ledger_observations.extend(observations)
        ledger_sessions[session.session_id] = session
        bracket_binding_sha256 = _fixture_artifact_sha256(binding)
        extraction_spec_sha256 = f"{producer_index + 2:x}" * 64
        role_rows = []
        for role in ("decode", "prefill"):
            family_id = f"synthetic-{producer_index}-{role}"
            absolute, comparative, family_binding = _role_components(
                replace(base_absolute, evidence_root_id=evidence_root_id),
                replace(base_comparative, evidence_root_id=evidence_root_id),
                role=role,
                family_id=family_id,
                plan_id=plan_id,
                plan_sha256=plan_sha256,
            )
            absolute = replace(absolute, spec_sha256=extraction_spec_sha256)
            comparative = replace(
                comparative, spec_sha256=extraction_spec_sha256
            )
            verdict_bracket = _synthetic_verdict_bracket(observations)
            absolute = replace(
                absolute,
                whole_window_calibration_bracket=verdict_bracket,
            )
            comparative = replace(
                comparative,
                whole_window_calibration_bracket=verdict_bracket,
            )
            cell_id = f"cell-{producer_index}-{role}"
            group_id = f"transport-{producer_index}-{role}"
            allowlist = [
                {
                    "condition_family_id": family_id,
                    "condition_family_sha256": family_binding[
                        "condition_family_sha256"
                    ],
                }
            ]
            role_rows.append(
                (role, cell_id, group_id, allowlist, family_binding, absolute, comparative)
            )
        report_cells = [
            _production_report_cell(component)
            for row in role_rows
            for component in (row[-2], row[-1])
        ]
        report = {
            "schema_version": mint1.EXTRACTION_SCHEMA_VERSION,
            "spec_schema_version": mint1.EXTRACTION_SPEC_SCHEMA_VERSION,
            "runs_root": str(evidence_root),
            "manifest_id": None,
            "consumption_semantics_id": MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            "consumption_provenance": {},
            "governance": {"d078_gate": "governed synthetic fixture"},
            "cells": report_cells,
            "spec_membership_refusals": [],
            "idle_admission_refusals": [],
            "whole_window_drift_allowances": {
                "gross_energy": dict(base_absolute.whole_window_drift_allowance)
            },
            "all_cells_extractable": True,
        }
        assert validate_d117_mint_consumption_report(report) == []
        report_sha256 = _fixture_artifact_sha256(report)
        role_inputs = {}
        cell_pins = []
        for (
            role,
            cell_id,
            group_id,
            allowlist,
            family_binding,
            absolute,
            comparative,
        ) in role_rows:
            absolute_cell = next(
                row for row in report_cells
                if row["cell_id"] == absolute.calibration_cell_id
            )
            comparative_cell = next(
                row for row in report_cells
                if row["cell_id"] == comparative.calibration_cell_id
            )
            absolute = replace(
                absolute,
                report=report,
                report_sha256=report_sha256,
                cell=absolute_cell,
            )
            comparative = replace(
                comparative,
                report=report,
                report_sha256=report_sha256,
                cell=comparative_cell,
            )
            cell_pins.append(
                {
                    "role": role,
                    "cell_id": cell_id,
                    "transport_group_id": group_id,
                    "condition_family_id": family_binding[
                        "condition_family_id"
                    ],
                    "condition_family_sha256": family_binding[
                        "condition_family_sha256"
                    ],
                    "metric": f"phase_energy_j.{role}",
                    "window_class": "phase",
                    "target_precheck_path": ["phase", role],
                    "allowed_consumer_condition_families": allowlist,
                    "absolute": _v2_component_pin(absolute),
                    "comparative": _v2_component_pin(comparative),
                    "postcollection": _v2_postcollection(
                        absolute,
                        comparative,
                        bracket_binding=binding,
                        bracket_binding_sha256=bracket_binding_sha256,
                        extraction_report_sha256=report_sha256,
                    ),
                }
            )
            role_inputs[role] = generalized.V2CellComponents(
                absolute=absolute,
                comparative=comparative,
                allowed_consumer_condition_families=(family_binding,),
            )
            all_cell_ids.append(cell_id)
            all_group_ids.append(group_id)
            all_allowlists.append(
                {
                    "transport_group_id": group_id,
                    "cell_ids": [cell_id],
                    "allowed_consumer_condition_families": allowlist,
                }
            )
        components = [
            component
            for role_input in role_inputs.values()
            for component in (role_input.absolute, role_input.comparative)
        ]
        unique_members = {
            member.bundle_id
            for component in components
            for member in component.members
        }
        runtime_identity_sha256 = components[0].source_regime[
            "stack_identity_sha256"
        ]
        acceptance = load_calibration_acceptance_bound()
        assert acceptance is not None
        acceptance_sha256 = file_sha256(DEFAULT_ACCEPTANCE_BOUND_PATH)
        producer = {
            "plan": {
                "plan_id": plan_id,
                "sha256": plan_sha256,
                "declared_sha256": declared_sha256,
                "sidecar_sha256": sidecar_sha256,
                "relative_path": f"plans/{plan_id}.json",
                "declared_calibration_scope": "production_window",
                "artifact_calibration_scope": "production_window",
            },
            "evidence_root_id": evidence_root_id,
            "component_artifact": {
                "artifact_id": f"component-artifact-{producer_index}",
                "sha256": "0" * 64,
            },
            "model_runtime_config": {
                "model_artifact_sha256": components[0].source_regime[
                    "stack_identity"
                ]["model_artifact_sha256"],
                "runtime_identity_sha256": runtime_identity_sha256,
                "config_set_sha256": components[
                    0
                ].scientific_config_identity_sha256,
            },
            "extraction_spec": {
                "sha256": extraction_spec_sha256,
                "member_count": len(unique_members),
            },
            "calibration_acceptance": {
                "acceptance_id": acceptance["acceptance_id"],
                "artifact_sha256": acceptance_sha256,
                "derivation_sha256": acceptance["derivation_sha256"],
                "derivation_rule_id": acceptance["schema_version"],
            },
            "cells": cell_pins,
        }
        producers.append(producer)
        inputs[plan_id] = generalized.V2ProducerInputs(
            plan=plan,
            cells=role_inputs,
            evidence_root=evidence_root,
            plan_sha256=plan_sha256,
            plan_declared_sha256=declared_sha256,
            plan_sidecar_sha256=sidecar_sha256,
            calibration_acceptance=acceptance,
            calibration_acceptance_sha256=acceptance_sha256,
            bracket_binding=binding,
            bracket_binding_sha256=bracket_binding_sha256,
            authenticated_pre_observation=observations[0],
            authenticated_post_observation=observations[1],
            calibration_allowance_projection=(
                {
                    **generalized.issued_calibration_allowance_projection(
                        acceptance,
                        pre_exact_bound_lexeme_s="0.020000",
                        post_exact_bound_lexeme_s="0.021000",
                    ),
                    "allowance_rule": generalized.V2_ALLOWANCE_RULE,
                }
            ),
        )
    pinset = {
        "schema_version": generalized.PINSET_SCHEMA_VERSION_V2,
        "mint_tool_version": generalized.V2_MINT_TOOL_VERSION,
        "producer_plans": producers,
        "aggregate": {
            "artifact_id": "synthetic-d117-four-cell-floor",
            "plan_set_id": "synthetic-d117-plan-set",
            "producer_set_sha256": "0" * 64,
            "calibration_scope": "production_window",
            "source_class": "prospective",
            "cell_composition_rule": generalized.V2_CELL_COMPOSITION_RULE,
            "consumer_floor_rule": generalized.V2_CONSUMER_FLOOR_RULE,
            "component_artifacts": [
                {
                    "plan_id": producer["plan"]["plan_id"],
                    "artifact_id": producer["component_artifact"][
                        "artifact_id"
                    ],
                    "sha256": "0" * 64,
                    "producer_pin_sha256": "0" * 64,
                }
                for producer in producers
            ],
            "cell_ids": all_cell_ids,
            "transport_allowlists": all_allowlists,
        },
    }
    ledger_snapshot = SimpleNamespace(
        valid=True,
        ledger_schema="joulewise.calibration_observation_ledger.v1",
        receipts=tuple(ledger_receipts),
        observations=tuple(ledger_observations),
        bracket_session_by_id=ledger_sessions,
        head_sequence=len(ledger_receipts),
        head_digest=ledger_receipts[-1]["receipt_digest"],
    )
    for producer in producers:
        for cell in producer["cells"]:
            cell["postcollection"]["terminal_ledger_head_sha256"] = (
                ledger_snapshot.head_digest
            )
    return pinset, inputs, ledger_snapshot


# Independent golden constants. They are regenerated only by an explicit
# fixture-review step, never by the mint implementation under test.
SYNTHETIC_COMPONENT_SHA256S = (
    "8ac980a543bfa7d61d4f1e8e849ba6ca12d6ac16320592ae081da2a2bca70495",
    "a8c195553895a7a3d178336e0a1b133f84488ed68c6726c394966e7be61a0d70",
)
SYNTHETIC_PRODUCER_PIN_SHA256S = (
    "7bcc2e10908b2d1b258bcf42c4fd099bcb0b222f826be077f1e01ee10f0cbeb2",
    "f8c3f664e76e3650f9fbe3dd40311d90ed563af66a143c4880f2675632bb0999",
)
SYNTHETIC_PRODUCER_SET_SHA256 = (
    "2e1d9e4ef1675fed8e89db98639ec40e1cc3617f933d7f1ddb29305cb0245163"
)
CLI_COMPONENT_SHA256S = (
    "6325b71a5b7826201e1d93a087a1a4e90854fb6edcf5149322bc50de4d272cf6",
    "258b512b3017d53bd260871eccdc43c1f6d473e58886dd3326c23a5f4e2359ca",
)


def _repair_v2_pinset_self_hashes(pinset: dict) -> None:
    """Repair only pinset self-hashes with an independent JSON oracle."""

    for producer, entry in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
    ):
        entry["producer_pin_sha256"] = _fixture_canonical_sha256(producer)
    pinset["aggregate"]["producer_set_sha256"] = _fixture_canonical_sha256(
        pinset["producer_plans"]
    )


def freeze_synthetic_v2_pinset(
    root: Path,
) -> tuple[
    Path,
    str,
    dict[str, generalized.V2ProducerInputs],
    SimpleNamespace,
]:
    pinset, inputs, ledger_snapshot = synthetic_v2_fixture()
    for producer, entry, component_sha256, producer_sha256 in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
        SYNTHETIC_COMPONENT_SHA256S,
        SYNTHETIC_PRODUCER_PIN_SHA256S,
    ):
        producer["component_artifact"]["sha256"] = component_sha256
        entry["sha256"] = component_sha256
        entry["producer_pin_sha256"] = producer_sha256
    pinset["aggregate"]["producer_set_sha256"] = (
        SYNTHETIC_PRODUCER_SET_SHA256
    )
    path, digest = write_pinset(root, pinset)
    return path, digest, inputs, ledger_snapshot


def freeze_production_extracted_v2_pinset(
    root: Path,
) -> tuple[
    Path,
    str,
    dict[str, generalized.V2ProducerInputs],
    SimpleNamespace,
]:
    """Drive ``extract_cells`` into the decisive v2 mint fixture."""

    pinset, source_inputs, ledger_snapshot = synthetic_v2_fixture()
    extracted_inputs: dict[str, generalized.V2ProducerInputs] = {}
    for producer in pinset["producer_plans"]:
        plan_id = producer["plan"]["plan_id"]
        source = source_inputs[plan_id]

        def role_scoped_component(
            component: mint1.AuthenticatedComponent,
            role: str,
        ) -> mint1.AuthenticatedComponent:
            if role == "decode":
                return component
            renamed = {
                member.bundle_id: f"{member.bundle_id}-{role}"
                for member in component.members
            }
            spec_cell = copy.deepcopy(component.spec_cell)
            for member in spec_cell.get("members", []):
                member["bundle_id"] = renamed[member["bundle_id"]]
                member["slot"] = renamed.get(member.get("slot"), member.get("slot"))
            for block in spec_cell.get("blocks", []):
                block["members"] = {
                    position: renamed[bundle_id]
                    for position, bundle_id in block["members"].items()
                }
            return replace(
                component,
                spec_cell=spec_cell,
                members=tuple(
                    replace(member, bundle_id=renamed[member.bundle_id])
                    for member in component.members
                ),
            )

        prefill = source.cells["prefill"]
        source = replace(
            source,
            cells={
                **source.cells,
                "prefill": generalized.V2CellComponents(
                    absolute=role_scoped_component(
                        prefill.absolute, "prefill"
                    ),
                    comparative=role_scoped_component(
                        prefill.comparative, "prefill"
                    ),
                    allowed_consumer_condition_families=(
                        prefill.allowed_consumer_condition_families
                    ),
                ),
            },
        )
        evidence_root = root / f"production-extractor-{plan_id}"
        evidence_root.mkdir()
        spec_cells = [
            copy.deepcopy(component.spec_cell)
            for role in ("decode", "prefill")
            for component in (
                source.cells[role].absolute,
                source.cells[role].comparative,
            )
        ]
        for spec_cell in spec_cells:
            definitions = spec_cell["condition_family_definitions"]
            for binding in definitions.values():
                definition = binding["condition_family_definition"]
                definition["measurement_target"]["metric"] = spec_cell[
                    "metric"
                ]
                binding["condition_family_sha256"] = canonical_domain_sha256(
                    CONDITION_FAMILY_DOMAIN,
                    definition,
                )
        spec = {
            "schema_version": mint1.EXTRACTION_SPEC_SCHEMA_VERSION,
            "cells": spec_cells,
        }
        (evidence_root / "production-extraction-spec.json").write_text(
            json.dumps(spec, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        bundle_rows: dict[str, dict] = {}
        for role in ("decode", "prefill"):
            cell = source.cells[role]
            for index, member_row in enumerate(cell.absolute.members):
                bundle_rows.setdefault(member_row.bundle_id, {}).update(
                    {
                        "value": 100.0 + member_row.metric_value_j,
                        "width": cell.absolute.widths_j[index],
                        "block_id": None,
                        "position": None,
                    }
                )
            member_by_id = {
                member_row.bundle_id: member_row
                for member_row in cell.comparative.members
            }
            for block_index, block in enumerate(cell.comparative.spec_cell["blocks"]):
                member_width = cell.comparative.widths_j[block_index] / 2.0
                for position, bundle_id in block["members"].items():
                    bundle_rows.setdefault(bundle_id, {}).update(
                        {
                            "value": 100.0
                            + member_by_id[bundle_id].metric_value_j,
                            "width": member_width,
                            "block_id": block["block_id"],
                            "position": position,
                        }
                    )
        for bundle_id, row in bundle_rows.items():
            bundle_path = evidence_root / bundle_id
            bundle_path.mkdir()
            tags = [
                f"calibration-plan-sha256={producer['plan']['sha256']}"
            ]
            if row["block_id"] is not None:
                position = row["position"]
                tags.extend(
                    [
                        f"calibration-abba-block-id={row['block_id']}",
                        f"calibration-abba-label={position[0]}",
                        (
                            "calibration-abba-sequence-index="
                            f"{('A1', 'B1', 'B2', 'A2').index(position) + 1}"
                        ),
                    ]
                )
            # The production extractor is the surface under test here; this
            # fixture explicitly supplies a permissive strict validator, so a
            # config-unbound wire keeps the synthetic bundle outside the live
            # telemetry predicate while still exercising report generation.
            config = {
                "run_id": bundle_id,
                "run_metadata": {"tags": tags},
                "hardware_target": {"telemetry_backend": "mock"},
            }
            value = row["value"]
            width = row["width"]
            summary = {
                "status": "succeeded",
                "energy_uncertainty_status": "bounded",
                "summary_provenance": {"reducer_version": "0.5.2"},
                "measurement_quality": {"telemetry_source": "mock"},
                "phase_energy_j": {"decode": value, "prefill": value},
                "energy_anchor_shift_envelopes": {
                    f"/phase_energy_j/{role}": {
                        "method": (
                            "common_trace_shift_plus_independent_edge_corners_v3"
                        ),
                        "anchor_bound_s": 0.05,
                        "point_j": value,
                        "lower_j": value - width,
                        "upper_j": value + width,
                        "max_abs_delta_j": width,
                    }
                    for role in ("decode", "prefill")
                },
                "energy_bound_terms_j": {
                    "E_interpolation_joint_edge_bound_j": 0.0
                },
                "window_evidence_precheck": {
                    "phase": {
                        role: {
                            "eligible": True,
                            "reasons": [],
                            "windows": [
                                {
                                    "window_duration_s": 1.0,
                                    "observed_window_p95_sample_gap_s": 0.1,
                                    "observed_bracketing_max_sample_gap_s": 0.2,
                                    "cadence_ratio": 1.5,
                                    "clock_anchor_bound_s": 0.01,
                                    "interpolation_joint_edge_bound_j": 0.0,
                                }
                            ]
                        }
                        for role in ("decode", "prefill")
                    }
                },
            }
            for name, value_object in (
                ("config.json", config),
                (
                    "metadata.json",
                    {
                        "uncertainty_evidence": {
                            "clock_anchor": {"status": "resolved"}
                        }
                    },
                ),
                ("summary_metrics.json", summary),
            ):
                (bundle_path / name).write_text(
                    json.dumps(value_object, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
        cooldowns = {
            bundle_id: {
                "result": "recovered",
                "verified": True,
                "manifest": f"{plan_id}-production-extractor",
            }
            for bundle_id in bundle_rows
        }
        allowance_record = dict(
            source.cells["decode"].absolute.whole_window_drift_allowance
        )
        with (
            mock.patch(
                "joulewise.floor_extraction.campaign_cooldown_evidence",
                return_value=cooldowns,
            ),
            mock.patch(
                "joulewise.floor_extraction._whole_window_extraction_refusals",
                return_value=(),
            ),
            mock.patch(
                "joulewise.floor_extraction.whole_window_drift_allowances",
                return_value=SimpleNamespace(
                    status="allowances",
                    allowances={"gross_energy": allowance_record},
                ),
            ),
        ):
            report = extract_cells(
                evidence_root,
                spec,
                evaluation_basis_sha256=(
                    source.cells[
                        "decode"
                    ].absolute.whole_window_evaluation_basis_sha256
                ),
                consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                hash_bundles=True,
                strict_validator=lambda _path, _strict: [],
            )
        profile_errors = validate_d117_mint_consumption_report(report)
        if profile_errors:
            raise AssertionError(profile_errors)
        report_path = evidence_root / "extraction-report.json"
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        report = load_json(report_path)
        report_sha256 = file_sha256(report_path)
        report_cells = {row["cell_id"]: row for row in report["cells"]}
        missing_floors = [
            (row["cell_id"], row["refusal_reasons"])
            for row in report["cells"]
            if row["floor"] is None
        ]
        if missing_floors:
            raise AssertionError(missing_floors)
        updated_cells = {}
        for role in ("decode", "prefill"):
            source_cell = source.cells[role]
            updated_components = {}
            for kind, component in (
                ("absolute", source_cell.absolute),
                ("comparative", source_cell.comparative),
            ):
                report_cell = report_cells[component.calibration_cell_id]
                report_members = {
                    row["bundle_id"]: row for row in report_cell["members"]
                }
                updated_members = tuple(
                    replace(
                        member_row,
                        bundle_sha256=report_members[member_row.bundle_id][
                            "bundle_sha256"
                        ],
                        config_sha256=report_members[member_row.bundle_id][
                            "config_sha256"
                        ],
                        metric_value_j=report_members[member_row.bundle_id][
                            "metric_value_j"
                        ],
                    )
                    for member_row in component.members
                )
                updated_components[kind] = replace(
                    component,
                    report=report,
                    report_sha256=report_sha256,
                    spec=spec,
                    spec_sha256=file_sha256(
                        evidence_root / "production-extraction-spec.json"
                    ),
                    cell=report_cell,
                    members=updated_members,
                    evaluation_basis_member_count=len(bundle_rows),
                    widths_j=tuple(
                        report_cell["floor"]["admissible_half_widths_j"]
                    ),
                )
            updated_cells[role] = generalized.V2CellComponents(
                absolute=updated_components["absolute"],
                comparative=updated_components["comparative"],
                allowed_consumer_condition_families=(
                    source_cell.allowed_consumer_condition_families
                ),
            )
        updated_source = replace(source, cells=updated_cells)
        extracted_inputs[plan_id] = updated_source
        for cell_pin in producer["cells"]:
            role = cell_pin["role"]
            cell = updated_cells[role]
            cell_pin["absolute"] = _v2_component_pin(cell.absolute)
            cell_pin["comparative"] = _v2_component_pin(cell.comparative)
            postcollection = _v2_postcollection(
                cell.absolute,
                cell.comparative,
                bracket_binding=updated_source.bracket_binding,
                bracket_binding_sha256=(
                    updated_source.bracket_binding_sha256
                ),
                extraction_report_sha256=report_sha256,
            )
            absolute_floor = str(
                cell.absolute.cell["floor"]["drift_widened_guarded_floor_j"]
            )
            comparative_floor = str(
                cell.comparative.cell["floor"][
                    "drift_widened_guarded_floor_j"
                ]
            )
            operative_floor = str(
                max(float(absolute_floor), float(comparative_floor))
            )
            postcollection.update(
                {
                    "absolute_floor_full_precision": absolute_floor,
                    "comparative_floor_full_precision": comparative_floor,
                    "operative_floor_full_precision": operative_floor,
                    "absolute_floor_six_decimal": (
                        f"{float(absolute_floor):.6f}"
                    ),
                    "comparative_floor_six_decimal": (
                        f"{float(comparative_floor):.6f}"
                    ),
                    "operative_floor_six_decimal": (
                        f"{float(operative_floor):.6f}"
                    ),
                }
            )
            cell_pin["postcollection"] = postcollection
        producer["extraction_spec"].update(
            {
                "sha256": file_sha256(
                    evidence_root / "production-extraction-spec.json"
                ),
                "member_count": len(bundle_rows),
            }
        )

    for producer in pinset["producer_plans"]:
        for cell_pin in producer["cells"]:
            cell_pin["postcollection"]["terminal_ledger_head_sha256"] = (
                ledger_snapshot.head_digest
            )
    _repair_v2_pinset_self_hashes(pinset)
    provisional_path, provisional_digest = write_pinset(root, pinset)
    loaded = generalized.load_pinset(provisional_path, provisional_digest)
    assert isinstance(loaded, generalized.V2Pinset)
    _artifact, components = generalized._build_v2_artifacts(
        pinset=loaded,
        pinset_path=provisional_path,
        pinset_sha256=provisional_digest,
        producer_inputs=extracted_inputs,
        calibration_ledger_snapshot=ledger_snapshot,
        project_commit="0" * 40,
        project_tree_state="clean",
    )
    for producer, aggregate, component in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
        components,
    ):
        component_sha256 = generalized._artifact_sha256(component)
        producer["component_artifact"]["sha256"] = component_sha256
        aggregate["sha256"] = component_sha256
    _repair_v2_pinset_self_hashes(pinset)
    final_path, final_digest = write_pinset(root, pinset)
    return final_path, final_digest, extracted_inputs, ledger_snapshot


def install_production_extracted_v2_cli_fixture(root: Path):
    """Install extractor-produced inputs behind the production v2 CLI."""

    provisional_path, _digest, extracted_inputs, _snapshot = (
        freeze_production_extracted_v2_pinset(root)
    )
    pinset = load_json(provisional_path)
    acceptance_path = root / "production-acceptance.json"
    acceptance_path.write_bytes(DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes())
    acceptance = load_calibration_acceptance_bound(acceptance_path)
    assert acceptance is not None

    ledger_path = root / "production-ledger.jsonl"
    head_path = root / "production-ledger.head.json"
    head_path.write_text(
        json.dumps(
            {
                "sequence": 0,
                "head_digest": GENESIS_DIGEST,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    epoch = {
        "os_build": "fixture-os",
        "hardware_model": "fixture-hardware",
        "power_policy": "fixture-power-policy",
        "sampling_interval_ms": 100,
        "estimator_revision": "fixture-estimator",
        "pulse_protocol_id": "fixture-pulse",
    }
    t1 = {field: f"fixture-{field}" for field in V2_BINDING_FIELDS}
    t1.update(epoch)
    authenticated_inputs: dict[str, generalized.V2ProducerInputs] = {}
    manifest_producers = []

    def custody(evidence_root: Path, attempt_id: str) -> Path:
        path = evidence_root / "instrument_validation" / attempt_id
        (path / "raw").mkdir(parents=True)
        (path / "raw" / "powermetrics.plist").write_bytes(
            f"raw-{attempt_id}".encode("utf-8")
        )
        (path / "events.jsonl").write_text(
            json.dumps({"timestamp_s": 1.0}) + "\n",
            encoding="utf-8",
        )
        (path / "instrument_evidence.json").write_text(
            json.dumps({"attempt_id": attempt_id}) + "\n",
            encoding="utf-8",
        )
        (path / "manifest.json").write_text(
            json.dumps({"attempt_id": attempt_id}) + "\n",
            encoding="utf-8",
        )
        return path

    for producer_index, producer in enumerate(pinset["producer_plans"]):
        plan_id = producer["plan"]["plan_id"]
        source = extracted_inputs[plan_id]
        evidence_root = Path(source.cells["decode"].absolute.report["runs_root"])
        plan_path = root / f"{plan_id}.production-plan.json"
        plan_path.write_text(
            json.dumps(source.plan, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        plan_sha256 = file_sha256(plan_path)
        sidecar_path = root / f"{plan_id}.production-plan.sha256"
        sidecar_path.write_text(
            f"{plan_sha256}  {plan_path.name}\n",
            encoding="utf-8",
        )
        sidecar_sha256 = file_sha256(sidecar_path)

        session_id = f"production-session-{producer_index}"
        window_id = f"production-window-{producer_index}"
        slot_paths = {
            role: custody(evidence_root, f"{session_id}-{role}")
            for role in ("pre", "post")
        }
        append_bracket_session_receipt(
            ledger_path,
            session_id=session_id,
            window_id=window_id,
            plan_id=plan_id,
            plan_sha256=plan_sha256,
            evidence_root_id=producer["evidence_root_id"],
            runs_root=evidence_root,
            slots={
                role: {
                    "attempt_id": f"{session_id}-{role}",
                    "custody_locator": str(slot_paths[role]),
                    "identity_epoch": epoch,
                    "t1_bindings": t1,
                }
                for role in ("pre", "post")
            },
            head_pin_path=head_path,
            require_committed_pin=False,
        )
        for role, exact_bound in (("pre", "0.020000"), ("post", "0.021000")):
            finalize_bracket_session_slot(
                ledger_path,
                session_id=session_id,
                slot=role,
                disposition="valid",
                custody_locator=str(slot_paths[role]),
                artifact_sha256=artifact_hashes(slot_paths[role]),
                identity_epoch=epoch,
                t1_bindings=t1,
                capture_wall_time_s=("1.0" if role == "pre" else "2.0"),
                exact_bound_lexeme_s=exact_bound,
            )
        terminal_pin = terminal_head_pin_for_session(
            ledger_path,
            session_id=session_id,
        )
        head_path.write_text(
            json.dumps(terminal_pin) + "\n",
            encoding="utf-8",
        )
        interim_snapshot = load_calibration_ledger_snapshot(
            ledger_path,
            head_path,
            require_committed_pin=False,
            verify_custody=False,
        )
        assert interim_snapshot.valid
        binding = build_calibration_bracket_binding(
            interim_snapshot,
            session_id=session_id,
            window_id=window_id,
            plan_id=plan_id,
            plan_sha256=plan_sha256,
            evidence_root_id=producer["evidence_root_id"],
            runs_root=evidence_root,
        )
        binding_path = root / f"{plan_id}.production-binding.json"
        binding_path.write_text(
            json.dumps(binding, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        binding_sha256 = file_sha256(binding_path)
        session = interim_snapshot.bracket_session_by_id[session_id]
        observations = tuple(
            session.finalized_slots[role] for role in ("pre", "post")
        )
        verdict_bracket = _synthetic_verdict_bracket(list(observations))

        spec_path = evidence_root / "production-extraction-spec.json"
        spec = load_json(spec_path)
        spec_sha256 = file_sha256(spec_path)
        ordered_bundle_ids = list(dict.fromkeys(mint1._spec_member_ids(spec)))
        order = {
            **source.cells["decode"].absolute.order_manifest,
            "plan_id": plan_id,
            "calibration_plan_sha256": plan_sha256,
            "executed_order": [
                {"run_id": bundle_id} for bundle_id in ordered_bundle_ids
            ],
        }
        order_path = evidence_root / "order-manifest.json"
        order_path.write_text(
            json.dumps(order, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        order_sha256 = file_sha256(order_path)
        for bundle_id in ordered_bundle_ids:
            config_path = evidence_root / bundle_id / "config.json"
            config = load_json(config_path)
            tags = config["run_metadata"]["tags"]
            config["run_metadata"]["tags"] = [
                (
                    f"calibration-plan-sha256={plan_sha256}"
                    if tag.startswith("calibration-plan-sha256=")
                    else tag
                )
                for tag in tags
            ]
            config_path.write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        cooldowns = {
            bundle_id: {
                "result": "recovered",
                "verified": True,
                "manifest": f"{plan_id}-production-extractor",
            }
            for bundle_id in ordered_bundle_ids
        }
        allowance_record = dict(
            source.cells["decode"].absolute.whole_window_drift_allowance
        )
        with (
            mock.patch(
                "joulewise.floor_extraction.campaign_cooldown_evidence",
                return_value=cooldowns,
            ),
            mock.patch(
                "joulewise.floor_extraction._whole_window_extraction_refusals",
                return_value=(),
            ),
            mock.patch(
                "joulewise.floor_extraction.whole_window_drift_allowances",
                return_value=SimpleNamespace(
                    status="allowances",
                    allowances={"gross_energy": allowance_record},
                ),
            ),
        ):
            report = extract_cells(
                evidence_root,
                spec,
                evaluation_basis_sha256=(
                    source.cells[
                        "decode"
                    ].absolute.whole_window_evaluation_basis_sha256
                ),
                consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                hash_bundles=True,
                strict_validator=lambda _path, _strict: [],
            )
        profile_errors = validate_d117_mint_consumption_report(report)
        if profile_errors:
            raise AssertionError(profile_errors)
        report_path = evidence_root / "extraction-report.json"
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        basis_sha256 = source.cells[
            "decode"
        ].absolute.whole_window_evaluation_basis_sha256
        basis_count = source.cells[
            "decode"
        ].absolute.evaluation_basis_member_count
        basis_ids = [
            *ordered_bundle_ids,
            *(
                f"{plan_id}-reference-{index}"
                for index in range(basis_count - len(ordered_bundle_ids))
            ),
        ]
        policy_sha256 = "a" * 64
        manifest_dir = evidence_root / "campaign_manifests"
        manifest_dir.mkdir(exist_ok=True)
        source_manifest_path = manifest_dir / "production-source.json"
        source_manifest = {
            "schema_version": "joulewise.campaign_provenance.v2",
            "session_id": f"production-source-{producer_index}",
            "campaign_policy": {"sha256": policy_sha256},
            "members": [
                {
                    "execution": "invoked",
                    "run_id": f"production-source-{producer_index}",
                    "bundle_ids": basis_ids,
                }
            ],
        }
        source_manifest_path.write_text(
            json.dumps(source_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        source_manifest_raw = source_manifest_path.read_bytes()
        attestation = campaign_provenance_attestation(
            manifest_path=source_manifest_path,
            raw_manifest_bytes=source_manifest_raw,
            manifest=source_manifest,
            timestamp="2026-08-07T12:00:00Z",
        )
        verdict = {
            "record_type": "idle_admission_whole_window_verdict",
            "schema_version": WHOLE_WINDOW_SCHEMA,
            "status": "passed",
            "campaign_policy": {"sha256": policy_sha256},
            "bundle_ids": basis_ids,
            "idle_admission_core": {
                "schema_version": IDLE_ADMISSION_CORE_SCHEMA,
                "policy_sha256": policy_sha256,
                "members": [
                    {
                        "bundle_id": bundle_id,
                        "cpu_admission": {"decision": "admitted"},
                    }
                    for bundle_id in basis_ids
                ],
                "adapter_wattage_continuity": {
                    "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                    "decision": "stable",
                },
                "neg8_bracket": {
                    "schema_version": NEG8_BRACKET_SCHEMA,
                    "decision": "passed",
                    "policy": {"require_bracket": True},
                },
            },
        }
        verdict["row_provenance"] = build_row_provenance(
            policy_sha256=policy_sha256,
            bundle_ids=basis_ids,
            source_manifests=[
                {
                    "path": "campaign_manifests/production-source.json",
                    "sha256": hashlib.sha256(source_manifest_raw).hexdigest(),
                }
            ],
        )
        basis_row = {
            "evaluation_basis": {
                "sha256": basis_sha256,
                "member_occurrences": [
                    {"bundle_id": bundle_id, "bundle_path": bundle_id}
                    for bundle_id in basis_ids
                ],
                "calibration_bracket_set": verdict_bracket,
            }
        }
        campaign_path = evidence_root / "campaign_log.jsonl"
        campaign_path.write_text(
            "".join(
                json.dumps(row) + "\n"
                for row in (attestation, verdict, basis_row)
            ),
            encoding="utf-8",
        )
        campaign_sha256 = file_sha256(campaign_path)
        report_sha256 = file_sha256(report_path)
        report_value = load_json(report_path)
        report_cells = {
            row["cell_id"]: row for row in report_value["cells"]
        }

        role_inputs = {}
        manifest_cells = []
        for cell_pin in producer["cells"]:
            role = cell_pin["role"]
            source_cell = source.cells[role]
            components = {}
            component_paths = {}
            for component_name, component in (
                ("absolute", source_cell.absolute),
                ("comparative", source_cell.comparative),
            ):
                report_cell = report_cells[component.calibration_cell_id]
                report_members = {
                    row["bundle_id"]: row for row in report_cell["members"]
                }
                updated = replace(
                    component,
                    report=report_value,
                    report_sha256=report_sha256,
                    spec=spec,
                    spec_sha256=spec_sha256,
                    order_manifest=order,
                    order_manifest_sha256=order_sha256,
                    campaign_log_sha256=campaign_sha256,
                    cell=report_cell,
                    spec_cell=next(
                        row
                        for row in spec["cells"]
                        if row["cell_id"] == component.calibration_cell_id
                    ),
                    members=tuple(
                        replace(
                            member,
                            bundle_sha256=report_members[member.bundle_id][
                                "bundle_sha256"
                            ],
                            config_sha256=report_members[member.bundle_id][
                                "config_sha256"
                            ],
                            metric_value_j=report_members[member.bundle_id][
                                "metric_value_j"
                            ],
                        )
                        for member in component.members
                    ),
                    widths_j=tuple(
                        report_cell["floor"]["admissible_half_widths_j"]
                    ),
                    consumption_semantics_id=report_value[
                        "consumption_semantics_id"
                    ],
                    scientific_config_identity_sha256=hashlib.sha256(
                        b'{"synthetic":"same"}'
                    ).hexdigest(),
                    whole_window_calibration_bracket=verdict_bracket,
                )
                components[component_name] = updated
                component_paths[component_name] = {
                    "evidence_root": str(evidence_root),
                    "report": str(report_path),
                    "spec": str(spec_path),
                    "order_manifest": str(order_path),
                }
                cell_pin[component_name] = _v2_component_pin(updated)
            family_binding = components["absolute"].spec_cell[
                "condition_family_definitions"
            ]["all"]
            allowlist = [
                {
                    "condition_family_id": family_binding[
                        "condition_family_id"
                    ],
                    "condition_family_sha256": family_binding[
                        "condition_family_sha256"
                    ],
                }
            ]
            cell_pin.update(
                {
                    "condition_family_id": family_binding[
                        "condition_family_id"
                    ],
                    "condition_family_sha256": family_binding[
                        "condition_family_sha256"
                    ],
                    "allowed_consumer_condition_families": allowlist,
                }
            )
            for transport in pinset["aggregate"]["transport_allowlists"]:
                if (
                    transport["transport_group_id"]
                    == cell_pin["transport_group_id"]
                ):
                    transport["allowed_consumer_condition_families"] = allowlist
            postcollection = _v2_postcollection(
                components["absolute"],
                components["comparative"],
                bracket_binding=binding,
                bracket_binding_sha256=binding_sha256,
                extraction_report_sha256=report_sha256,
            )
            absolute_floor = str(
                components["absolute"].cell["floor"][
                    "drift_widened_guarded_floor_j"
                ]
            )
            comparative_floor = str(
                components["comparative"].cell["floor"][
                    "drift_widened_guarded_floor_j"
                ]
            )
            operative_floor = str(
                max(float(absolute_floor), float(comparative_floor))
            )
            postcollection.update(
                {
                    "absolute_floor_full_precision": absolute_floor,
                    "comparative_floor_full_precision": comparative_floor,
                    "operative_floor_full_precision": operative_floor,
                    "absolute_floor_six_decimal": f"{float(absolute_floor):.6f}",
                    "comparative_floor_six_decimal": (
                        f"{float(comparative_floor):.6f}"
                    ),
                    "operative_floor_six_decimal": f"{float(operative_floor):.6f}",
                }
            )
            cell_pin["postcollection"] = postcollection
            role_inputs[role] = generalized.V2CellComponents(
                absolute=components["absolute"],
                comparative=components["comparative"],
                allowed_consumer_condition_families=(family_binding,),
            )
            manifest_cells.append(
                {
                    "role": role,
                    **component_paths,
                    "allowed_consumer_condition_families": [family_binding],
                }
            )
        plan = {**source.plan, "plan_id": plan_id}
        authenticated_inputs[plan_id] = replace(
            source,
            plan=plan,
            cells=role_inputs,
            evidence_root=evidence_root,
            plan_sha256=plan_sha256,
            plan_declared_sha256=plan_sha256,
            plan_sidecar_sha256=sidecar_sha256,
            calibration_acceptance=acceptance,
            calibration_acceptance_sha256=file_sha256(acceptance_path),
            bracket_binding=binding,
            bracket_binding_sha256=binding_sha256,
            authenticated_pre_observation=observations[0],
            authenticated_post_observation=observations[1],
            calibration_allowance_projection={
                **generalized.issued_calibration_allowance_projection(
                    acceptance,
                    pre_exact_bound_lexeme_s="0.020000",
                    post_exact_bound_lexeme_s="0.021000",
                ),
                "allowance_rule": generalized.V2_ALLOWANCE_RULE,
            },
        )
        producer["plan"].update(
            {
                "sha256": plan_sha256,
                "declared_sha256": plan_sha256,
                "sidecar_sha256": sidecar_sha256,
            }
        )
        producer["extraction_spec"].update(
            {"sha256": spec_sha256, "member_count": len(ordered_bundle_ids)}
        )
        producer["model_runtime_config"]["config_set_sha256"] = hashlib.sha256(
            b'{"synthetic":"same"}'
        ).hexdigest()
        manifest_producers.append(
            {
                "plan_id": plan_id,
                "calibration_plan": str(plan_path),
                "calibration_plan_sidecar": str(sidecar_path),
                "bracket_binding": str(binding_path),
                "cells": manifest_cells,
            }
        )

    ledger_snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_path,
        require_committed_pin=False,
        verify_custody=False,
    )
    assert ledger_snapshot.valid
    for producer in pinset["producer_plans"]:
        for cell in producer["cells"]:
            cell["postcollection"]["terminal_ledger_head_sha256"] = (
                ledger_snapshot.head_digest
            )
    _repair_v2_pinset_self_hashes(pinset)
    provisional_path, provisional_digest = write_pinset(root, pinset)
    loaded = generalized.load_pinset(provisional_path, provisional_digest)
    assert isinstance(loaded, generalized.V2Pinset)
    _artifact, components = generalized._build_v2_artifacts(
        pinset=loaded,
        pinset_path=provisional_path,
        pinset_sha256=provisional_digest,
        producer_inputs=authenticated_inputs,
        calibration_ledger_snapshot=ledger_snapshot,
        project_commit="0" * 40,
        project_tree_state="clean",
    )
    for producer, aggregate, component in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
        components,
    ):
        component_sha256 = generalized._artifact_sha256(component)
        producer["component_artifact"]["sha256"] = component_sha256
        aggregate["sha256"] = component_sha256
    _repair_v2_pinset_self_hashes(pinset)
    pinset_path, pinset_sha256 = write_pinset(root, pinset)
    manifest_path = root / "production-input-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "joulewise.floor_mint_inputs.v2",
                "calibration_acceptance": str(acceptance_path),
                "calibration_ledger": str(ledger_path),
                "calibration_ledger_head_pin": str(head_path),
                "producer_plans": manifest_producers,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    original_core_loader = generalized._fresh_original_core

    def load_test_core():
        core = original_core_loader()
        original_authenticate = core._authenticate_component

        def authenticate(paths, **kwargs):
            kwargs["strict_validator"] = lambda _path, _strict: []

            def production_consumption(
                runs_root,
                referenced_bundle_ids,
                evaluation_basis_sha256,
                **consumption_kwargs,
            ):
                session = AuthenticatedConsumptionSession(
                    runs_root,
                    referenced_bundle_ids,
                    evaluation_basis_sha256=evaluation_basis_sha256,
                    consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
                    calibration_ledger_snapshot=consumption_kwargs.get(
                        "calibration_ledger_snapshot"
                    ),
                )
                session._prepared = True
                session._preparation_identity = tuple(
                    sorted(
                        (
                            bundle_id,
                            str((Path(runs_root) / bundle_id).resolve()),
                        )
                        for bundle_id in referenced_bundle_ids
                    )
                )
                session._summaries = {
                    bundle_id: load_json(
                        Path(runs_root) / bundle_id / "summary_metrics.json"
                    )
                    for bundle_id in referenced_bundle_ids
                }
                with (
                    mock.patch(
                        "joulewise.whole_window._registered_bracket_policy",
                        return_value={"require_bracket": True},
                    ),
                    mock.patch(
                        "joulewise.whole_window._derived_neg8_decision",
                        return_value=("passed", None),
                    ),
                ):
                    reasons = whole_window_refusal_reasons(
                        runs_root,
                        referenced_bundle_ids,
                        evaluation_basis_sha256=evaluation_basis_sha256,
                        consumption_session=session,
                        consumption_semantics_id=(
                            MINTED_CONSUMPTION_SEMANTICS_ID
                        ),
                    )
                if reasons:
                    raise core.MintError(
                        "authenticated whole-window consumption refused: "
                        + reasons[0]
                    )
                return session._summaries, MINTED_CONSUMPTION_SEMANTICS_ID

            return original_authenticate(
                paths,
                **kwargs,
                consumption_authenticator=production_consumption,
                allowance_deriver=_synthetic_allowances,
            )

        core._authenticate_component = authenticate
        core._derive_stack_identity = lambda _config, _metadata: stack_identity()
        core.scientific_config_identity = lambda _config: {"synthetic": "same"}
        core.load_calibration_ledger_snapshot = lambda **kwargs: (
            load_calibration_ledger_snapshot(
                kwargs["ledger_path"],
                kwargs["head_pin_path"],
                require_committed_pin=False,
                verify_custody=False,
            )
        )
        core.bind_floor_artifact_evidence = lambda *_args, **_kwargs: {}
        return core

    with mock.patch.object(
        generalized,
        "_fresh_original_core",
        side_effect=load_test_core,
    ):
        loaded = generalized.load_pinset(pinset_path, pinset_sha256)
        assert isinstance(loaded, generalized.V2Pinset)
        file_inputs, _roots, file_snapshot = generalized._authenticate_v2_inputs(
            pinset=loaded,
            pinset_path=pinset_path,
            pinset_sha256=pinset_sha256,
            input_manifest_path=manifest_path,
            strict_validator=lambda _path, _strict: [],
            consumption_semantics_id=None,
        )
        _artifact, file_components = generalized._build_v2_artifacts(
            pinset=loaded,
            pinset_path=pinset_path,
            pinset_sha256=pinset_sha256,
            producer_inputs=file_inputs,
            calibration_ledger_snapshot=file_snapshot,
            project_commit="0" * 40,
            project_tree_state="clean",
        )
    for producer, aggregate, component in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
        file_components,
    ):
        component_sha256 = generalized._artifact_sha256(component)
        producer["component_artifact"]["sha256"] = component_sha256
        aggregate["sha256"] = component_sha256
    _repair_v2_pinset_self_hashes(pinset)
    pinset_path, pinset_sha256 = write_pinset(root, pinset)

    return (
        pinset_path,
        pinset_sha256,
        manifest_path,
        load_test_core,
    )


def install_v2_cli_fixture(root: Path):
    """Install file-backed v2 inputs and a narrow v1-core test adapter."""

    pinset, source_inputs, _source_snapshot = synthetic_v2_fixture()
    acceptance = next(iter(source_inputs.values())).calibration_acceptance
    acceptance_path = root / "acceptance.json"
    acceptance_path.write_text(
        json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    acceptance_sha256 = file_sha256(acceptance_path)
    ledger_path = root / "ledger.jsonl"
    ledger_path.write_text("{}\n", encoding="utf-8")
    head_path = root / "ledger.head.json"
    head_path.write_text("{}\n", encoding="utf-8")

    component_by_source = {}
    manifest_producers = []
    ledger_receipts = []
    ledger_observations = []
    ledger_sessions = {}
    for producer_index, producer in enumerate(pinset["producer_plans"]):
        plan_id = producer["plan"]["plan_id"]
        source = source_inputs[plan_id]
        plan_path = root / f"{plan_id}.json"
        plan_path.write_text(
            json.dumps(source.plan, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        plan_sha256 = file_sha256(plan_path)
        sidecar_path = root / f"{plan_id}.sha256"
        sidecar_path.write_text(
            f"{plan_sha256}  {plan_path.name}\n",
            encoding="utf-8",
        )
        producer["plan"].update(
            {
                "sha256": plan_sha256,
                "declared_sha256": plan_sha256,
                "sidecar_sha256": file_sha256(sidecar_path),
            }
        )
        producer["calibration_acceptance"]["artifact_sha256"] = (
            acceptance_sha256
        )

        evidence_root = root / f"{plan_id}-root"
        evidence_root.mkdir()
        campaign_path = evidence_root / "campaign_log.jsonl"
        campaign_path.write_text("{}\n", encoding="utf-8")
        campaign_sha256 = file_sha256(campaign_path)
        bundle_ids = {
            bundle_id
            for cell in source.cells.values()
            for component in (cell.absolute, cell.comparative)
            for bundle_id in generalized._v2_spec_member_ids(component.spec)
        }
        for bundle_id in bundle_ids:
            bundle = evidence_root / bundle_id
            bundle.mkdir(exist_ok=True)
            for name in ("config.json", "metadata.json", "summary_metrics.json"):
                (bundle / name).write_text("{}\n", encoding="utf-8")
        binding, receipts, observations, session = _synthetic_bracket_evidence(
            producer_index,
            plan_id=plan_id,
            plan_sha256=plan_sha256,
            evidence_root_id=producer["evidence_root_id"],
            runs_root=evidence_root,
            sequence_start=1 + 3 * producer_index,
        )
        ledger_receipts.extend(receipts)
        ledger_observations.extend(observations)
        ledger_sessions[session.session_id] = session
        binding_path = root / f"{plan_id}.binding.json"
        binding_path.write_text(
            json.dumps(binding, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        binding_sha256 = file_sha256(binding_path)

        role_inputs = {}
        manifest_cells = []
        for cell_pin in producer["cells"]:
            role = cell_pin["role"]
            source_cell = source.cells[role]
            components = {}
            component_paths = {}
            for component_name, source_component in (
                ("absolute", source_cell.absolute),
                ("comparative", source_cell.comparative),
            ):
                label = f"{plan_id}-{role}-{component_name}"
                report_path = root / f"{label}-report.json"
                report_path.write_text(
                    json.dumps(
                        source_component.report,
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                spec_path = root / f"{label}-spec.json"
                spec_path.write_text(
                    json.dumps(
                        source_component.spec,
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                order = {
                    **source_component.order_manifest,
                    "calibration_plan_sha256": plan_sha256,
                }
                order_path = root / f"{label}-order.json"
                order_path.write_text(
                    json.dumps(order, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                component = replace(
                    source_component,
                    report_sha256=file_sha256(report_path),
                    spec_sha256=file_sha256(spec_path),
                    order_manifest=order,
                    order_manifest_sha256=file_sha256(order_path),
                    campaign_log_sha256=campaign_sha256,
                    whole_window_calibration_bracket=(
                        _synthetic_verdict_bracket(observations)
                    ),
                )
                components[component_name] = component
                component_paths[component_name] = {
                    "evidence_root": str(evidence_root),
                    "report": str(report_path),
                    "spec": str(spec_path),
                    "order_manifest": str(order_path),
                }
                component_by_source[
                    (
                        component.calibration_cell_id,
                        str(evidence_root.resolve()),
                    )
                ] = component
                cell_pin[component_name] = _v2_component_pin(component)
            cell_pin["postcollection"] = _v2_postcollection(
                components["absolute"],
                components["comparative"],
                bracket_binding=binding,
                bracket_binding_sha256=binding_sha256,
                extraction_report_sha256=components[
                    "absolute"
                ].report_sha256,
            )
            role_inputs[role] = generalized.V2CellComponents(
                absolute=components["absolute"],
                comparative=components["comparative"],
                allowed_consumer_condition_families=(
                    source_cell.allowed_consumer_condition_families
                ),
            )
            manifest_cells.append(
                {
                    "role": role,
                    **component_paths,
                    "allowed_consumer_condition_families": list(
                        source_cell.allowed_consumer_condition_families
                    ),
                }
            )
        components = [
            component
            for role_input in role_inputs.values()
            for component in (role_input.absolute, role_input.comparative)
        ]
        producer["extraction_spec"].update(
            {
                "sha256": components[0].spec_sha256,
                "member_count": len(
                    {
                        member_row.bundle_id
                        for component in components
                        for member_row in component.members
                    }
                ),
            }
        )
        manifest_producers.append(
            {
                "plan_id": plan_id,
                "calibration_plan": str(plan_path),
                "calibration_plan_sidecar": str(sidecar_path),
                "bracket_binding": str(binding_path),
                "cells": manifest_cells,
            }
        )

    ledger_snapshot = SimpleNamespace(
        valid=True,
        ledger_schema="joulewise.calibration_observation_ledger.v1",
        receipts=tuple(ledger_receipts),
        observations=tuple(ledger_observations),
        bracket_session_by_id=ledger_sessions,
        head_sequence=len(ledger_receipts),
        head_digest=ledger_receipts[-1]["receipt_digest"],
    )
    for producer in pinset["producer_plans"]:
        for cell in producer["cells"]:
            cell["postcollection"]["terminal_ledger_head_sha256"] = (
                ledger_snapshot.head_digest
            )
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "joulewise.floor_mint_inputs.v2",
                "calibration_acceptance": str(acceptance_path),
                "calibration_ledger": str(ledger_path),
                "calibration_ledger_head_pin": str(head_path),
                "producer_plans": manifest_producers,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    original_core_loader = generalized._fresh_original_core

    def load_test_core():
        core = original_core_loader()

        def load_acceptance(path):
            if Path(path).read_bytes() != acceptance_path.read_bytes():
                return None
            return acceptance

        def authenticate(paths, **kwargs):
            source_key = (
                paths.calibration_cell_id,
                str(paths.evidence_root.resolve()),
            )
            expected = component_by_source.get(source_key)
            if expected is None:
                raise core.MintError("unexpected component cell/evidence root")
            for path, expected_sha256 in (
                (paths.report_path, expected.report_sha256),
                (paths.spec_path, expected.spec_sha256),
                (paths.order_manifest_path, expected.order_manifest_sha256),
            ):
                if file_sha256(path) != expected_sha256:
                    raise core.MintError("component artifact bytes mismatch")
            if kwargs.get("expected_basis_sha256") != (
                expected.whole_window_evaluation_basis_sha256
            ):
                raise core.MintError("component basis dispatch mismatch")
            if kwargs.get("expected_consumption_semantics_id") != (
                expected.consumption_semantics_id
            ):
                raise core.MintError("component semantics dispatch mismatch")
            if kwargs.get("calibration_ledger_snapshot") is not ledger_snapshot:
                raise core.MintError("component ledger snapshot identity mismatch")
            return expected

        core.load_calibration_acceptance_bound = load_acceptance
        core.load_calibration_ledger_snapshot = lambda **_kwargs: ledger_snapshot
        core._authenticate_component = authenticate
        core.bind_floor_artifact_evidence = lambda *_args, **_kwargs: {}
        return core

    for producer, entry, component_sha256 in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
        CLI_COMPONENT_SHA256S,
    ):
        producer["component_artifact"]["sha256"] = component_sha256
        entry["sha256"] = component_sha256
    _repair_v2_pinset_self_hashes(pinset)
    pinset_path, pinset_sha256 = write_pinset(root, pinset)
    return pinset_path, pinset_sha256, manifest_path, load_test_core


D117_PRODUCTION_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "d117_v2_production"
D117_PRODUCTION_CALIBRATION_CONTENT_ID = (
    "029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee"
)


def _d117_production_custody_store() -> Path:
    override = os.environ.get("JOULEWISE_D117_CUSTODY_STORE")
    if override:
        return Path(override).resolve()
    return D117_PRODUCTION_FIXTURE / "custody_store"


def _write_fixture_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _hardlink_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, copy_function=os.link)


def _shift_fixture_epoch(value: object, delta_s: float) -> object:
    if isinstance(value, dict):
        return {
            key: (
                item + delta_s
                if isinstance(item, (int, float))
                and not isinstance(item, bool)
                and (
                    key in {"timestamp_s", "epoch_s", "capture_wall_time_s"}
                    or key.endswith("_epoch_s")
                    or key.startswith("wall_minus_monotonic_")
                )
                else _shift_fixture_epoch(item, delta_s)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_shift_fixture_epoch(item, delta_s) for item in value]
    return value


def _install_shifted_calibration(
    destination: Path,
    *,
    capture_time_s: float,
    executable: Path,
    slot: str,
) -> tuple[dict, object]:
    """Derive a small, physically re-verifiable live-session endpoint."""

    source = (
        _d117_production_custody_store()
        / D117_PRODUCTION_CALIBRATION_CONTENT_ID
    )
    destination.mkdir(parents=True)
    (destination / "raw").mkdir()
    original_evidence = load_json(source / "instrument_evidence.json")
    delta_s = float(
        int(capture_time_s - float(original_evidence["capture_wall_time_s"]))
    )
    event_rows = [
        _shift_fixture_epoch(json.loads(line), delta_s)
        for line in (source / "events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    events_raw = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        for row in event_rows
    ).encode("utf-8")
    (destination / "events.jsonl").write_bytes(events_raw)
    shutil.copy2(source / "power_trace.csv", destination / "power_trace.csv")

    powermetrics_path = destination / "raw" / "powermetrics.plist"
    first_frame = True
    buffered = b""
    with (
        (source / "raw" / "powermetrics.plist").open("rb") as input_handle,
        powermetrics_path.open("wb") as output_handle,
    ):
        while chunk := input_handle.read(1024 * 1024):
            buffered += chunk
            frames = buffered.split(b"\0")
            buffered = frames.pop()
            for frame in frames:
                if not frame.strip():
                    continue
                document = plistlib.loads(frame)
                processor = document["processor"]
                slim = plistlib.dumps(
                    {
                        "is_delta": document["is_delta"],
                        "elapsed_ns": document["elapsed_ns"],
                        "timestamp": document["timestamp"]
                        + timedelta(seconds=delta_s),
                        "processor": {
                            key: processor[key]
                            for key in (
                                "cpu_power",
                                "gpu_power",
                                "ane_power",
                                "cpu_energy",
                                "gpu_energy",
                                "ane_energy",
                                "combined_power",
                            )
                        },
                    },
                    sort_keys=True,
                )
                if not first_frame:
                    output_handle.write(b"\0")
                output_handle.write(slim)
                first_frame = False
        if buffered.strip():
            document = plistlib.loads(buffered)
            processor = document["processor"]
            slim = plistlib.dumps(
                {
                    "is_delta": document["is_delta"],
                    "elapsed_ns": document["elapsed_ns"],
                    "timestamp": document["timestamp"]
                    + timedelta(seconds=delta_s),
                    "processor": {
                        key: processor[key]
                        for key in (
                            "cpu_power",
                            "gpu_power",
                            "ane_power",
                            "cpu_energy",
                            "gpu_energy",
                            "ane_energy",
                            "combined_power",
                        )
                    },
                },
                sort_keys=True,
            )
            if not first_frame:
                output_handle.write(b"\0")
            output_handle.write(slim)
    powermetrics_sha256 = file_sha256(powermetrics_path)

    evidence = _shift_fixture_epoch(original_evidence, delta_s)
    assert isinstance(evidence, dict)
    executable_sha256 = file_sha256(executable)
    evidence["validation_id"] = f"d117-v2-production-{slot}"
    evidence["bindings"]["powermetrics_sha256"] = executable_sha256
    evidence["binding_evidence"]["powermetrics_binary"] = {
        "path": str(executable.resolve()),
        "sha256": executable_sha256,
    }
    evidence["binding_evidence"]["binding_vector_sha256"] = hashlib.sha256(
        json.dumps(
            evidence["bindings"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    evidence["artifact_sha256"]["events.jsonl"] = hashlib.sha256(
        events_raw
    ).hexdigest()
    evidence["artifact_sha256"]["raw/powermetrics.plist"] = powermetrics_sha256
    evidence_raw = (
        json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    (destination / "instrument_evidence.json").write_bytes(evidence_raw)

    manifest = load_json(source / "manifest.json")
    manifest["fixture_slot"] = slot
    for name in (
        "events.jsonl",
        "instrument_evidence.json",
        "power_trace.csv",
        "raw/powermetrics.plist",
    ):
        manifest["artifacts"][name] = file_sha256(destination / name)
    _write_fixture_json(destination / "manifest.json", manifest)
    candidate = load_calibration_candidate(
        destination, runs_root=destination.parent
    )
    if candidate is None:
        raise AssertionError(f"shifted {slot} calibration is not authentic")
    return evidence, candidate


def _stretch_fixture_measurement_windows(bundle_path: Path) -> None:
    """Use the seed's recorded telemetry tail for claim-eligible phase windows."""

    events_path = bundle_path / "events.jsonl"
    event_rows = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    measured_start_s = next(
        float(row["timestamp_s"])
        for row in event_rows
        if row.get("event_type") == "stage_started"
        and row.get("phase") == "measured_run"
    )
    token_index = 0
    sampling_stopped_s = measured_start_s + 1.235
    for row in event_rows:
        replacement: float | None = None
        event_type = row.get("event_type")
        phase = row.get("phase")
        if event_type == "phase_start" and phase == "prefill":
            replacement = measured_start_s + 0.000036
        elif event_type == "phase_end" and phase == "prefill":
            replacement = measured_start_s + 0.435
        elif event_type == "phase_start" and phase == "decode":
            replacement = measured_start_s + 0.43501
        elif event_type == "token" and phase == "decode":
            replacement = measured_start_s + 0.50 + token_index * 0.09
            token_index += 1
        elif event_type == "phase_end" and phase == "decode":
            replacement = measured_start_s + 1.185
        elif event_type == "sampling_stopped" and phase == "measured_run":
            replacement = sampling_stopped_s
        if replacement is not None:
            row["timestamp_s"] = replacement
    events_path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in event_rows
        ),
        encoding="utf-8",
    )

    tokens_path = bundle_path / "outputs" / "tokens.jsonl"
    tokens = [
        json.loads(line)
        for line in tokens_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for index, row in enumerate(tokens):
        row["timestamp_s"] = measured_start_s + 0.50 + index * 0.09
    tokens_path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in tokens
        ),
        encoding="utf-8",
    )

    from joulewise.adapters.powermetrics import (
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )
    from joulewise.uncertainty_evidence import (
        derive_powermetrics_clock_evidence_v2,
        stamp_from_mapping,
    )

    metadata_path = bundle_path / "metadata.json"
    metadata = load_json(metadata_path)
    uncertainty = metadata["uncertainty_evidence"]
    stopped_stamp = uncertainty["clock_anchor"]["clock_stamps"][
        "sampling_stopped"
    ]
    stamp_delta_s = sampling_stopped_s - float(stopped_stamp["epoch_s"])
    stopped_stamp["epoch_s"] = sampling_stopped_s
    stopped_stamp["monotonic_before_s"] += stamp_delta_s
    stopped_stamp["monotonic_after_s"] += stamp_delta_s
    stamps = {
        name: stamp_from_mapping(value)
        for name, value in uncertainty["clock_anchor"]["clock_stamps"].items()
    }
    records = parse_powermetrics_records(
        (bundle_path / "raw" / "powermetrics.plist").read_bytes()
    )
    expected, _point = derive_powermetrics_clock_evidence_v2(
        stamps=stamps,
        records=anchor_records_from_powermetrics(records),
    )
    uncertainty["clock_anchor"] = expected["clock_anchor"]
    uncertainty["sample_phase"] = expected["sample_phase"]
    metadata["marker_to_first_sample_phase_bound_s"] = expected[
        "sample_phase"
    ]["marker_to_first_sample_phase_bound_s"]
    metadata["marker_to_last_sample_phase_bound_s"] = expected[
        "sample_phase"
    ]["marker_to_last_sample_phase_bound_s"]
    _write_fixture_json(metadata_path, metadata)


def _lower_fixture_idle_baseline(bundle_path: Path) -> None:
    """Derive a strict-valid low-idle fixture from the recorded idle plists."""

    from joulewise.adapters.powermetrics import (
        decode_rich_telemetry,
        idle_window_gpu_quality,
        parse_powermetrics_records,
    )
    from joulewise.idle_dependence import (
        duration_weighted_mean_and_sample_variance,
    )
    from joulewise.uncertainty_evidence import derive_idle_drift_evidence

    def scaled(value: object) -> object:
        if isinstance(value, dict):
            return {
                key: (
                    item * 0.2
                    if isinstance(item, (int, float))
                    and not isinstance(item, bool)
                    and (
                        key.endswith("_power")
                        or key.endswith("_energy")
                        or key == "combined_power"
                    )
                    else scaled(item)
                )
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [scaled(item) for item in value]
        return value

    raw_payloads: dict[str, bytes] = {}
    for name in ("powermetrics_idle.plist", "powermetrics_idle_post.plist"):
        path = bundle_path / "raw" / name
        frames = [
            scaled(plistlib.loads(frame))
            for frame in path.read_bytes().split(b"\0")
            if frame.strip()
        ]
        raw = b"\0".join(
            plistlib.dumps(frame, sort_keys=True) for frame in frames
        )
        path.write_bytes(raw)
        raw_payloads[name] = raw

    pre_records = parse_powermetrics_records(
        raw_payloads["powermetrics_idle.plist"]
    )
    post_records = parse_powermetrics_records(
        raw_payloads["powermetrics_idle_post.plist"]
    )
    pre_power_w = [record.combined_power_w for record in pre_records]
    post_power_w = [record.combined_power_w for record in post_records]
    intervals_s = [record.elapsed_ns / 1_000_000_000.0 for record in pre_records]
    mean_w, variance_w2 = duration_weighted_mean_and_sample_variance(
        pre_power_w, intervals_s
    )
    metadata_path = bundle_path / "metadata.json"
    metadata = load_json(metadata_path)
    baseline = metadata["idle_baseline"]
    baseline.update(
        {
            "duration_s": sum(intervals_s),
            "power_w_mean": mean_w,
            "power_w_stddev": variance_w2**0.5,
            "sample_count": len(pre_records),
        }
    )
    uncertainty = metadata["uncertainty_evidence"]
    pre_quality = idle_window_gpu_quality(
        decode_rich_telemetry(raw_payloads["powermetrics_idle.plist"])
    )
    post_quality = idle_window_gpu_quality(
        decode_rich_telemetry(raw_payloads["powermetrics_idle_post.plist"])
    )
    idle_drift, idle_guard, idle_bound_w = derive_idle_drift_evidence(
        pre_power_w=pre_power_w,
        post_power_w=post_power_w,
        pre_power_w_mean=mean_w,
        pre_idle_window_suspect=pre_quality["idle_window_suspect"],
        post_idle_window_suspect=post_quality["idle_window_suspect"],
        calibration_guard=uncertainty["idle_drift_guard"],
    )
    uncertainty["idle_drift"] = idle_drift
    uncertainty["idle_drift_guard"] = idle_guard
    metadata["idle_drift_bound_w"] = idle_bound_w
    _write_fixture_json(metadata_path, metadata)

    events_path = bundle_path / "events.jsonl"
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for row in events:
        if (
            row.get("event_type") == "stage_completed"
            and row.get("phase") == "idle_baseline"
        ):
            row["metadata"]["power_w_mean"] = mean_w
            row["metadata"]["duration_s"] = sum(intervals_s)
    events_path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in events
        ),
        encoding="utf-8",
    )


def _copy_repository_without_large_custody(destination: Path) -> None:
    ignored_roots = {".git", ".pytest_cache", "__pycache__"}
    for source in REPO_ROOT.rglob("*"):
        relative = source.relative_to(REPO_ROOT)
        if any(part in ignored_roots for part in relative.parts):
            continue
        if relative.parts[:4] == (
            "tests",
            "fixtures",
            "d117_v2_production",
            "custody_store",
        ):
            continue
        target = destination / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _install_recovered_campaign_manifest(
    runs_root: Path,
    bundle_ids: list[str],
    *,
    policy_sha256: str,
    neg8_scientific_config_sha256: str,
    analysis_manifest_id: str = "d117-production-analysis",
) -> None:
    manifest_root = runs_root / "campaign_manifests"
    raw_root = manifest_root / "raw"
    raw_root.mkdir(parents=True)
    members = []
    for index, bundle_id in enumerate(bundle_ids):
        raw = (
            json.dumps(
                {
                    "rolling_mean_power_w": 0.05,
                    "release": True,
                    "release_criteria_met_late": False,
                    "timestamp_s": float(index),
                }
            )
            + "\n"
        ).encode("utf-8")
        raw_name = f"d117-production__cooldown_before_{bundle_id}.jsonl"
        (raw_root / raw_name).write_bytes(raw)
        member = {
            "run_id": bundle_id,
            "bundle_ids": [bundle_id],
            "execution": "invoked",
            "preceding_campaign_cooldown": (
                {
                    "result": "first_run_exempt",
                    "session_id": "d117-production",
                    "following_run_id": bundle_id,
                }
                if index == 0
                else {
                    "result": "recovered",
                    "session_id": "d117-production",
                    "following_run_id": bundle_id,
                    "raw_artifact": {
                        "path": f"raw/{raw_name}",
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "records": 1,
                    },
                }
            ),
        }
        if index == 0:
            member.update(
                {
                    "role": "neg8_daily_reference_start",
                    "sentinel_position": "start",
                    "canonical_neg8_workload": True,
                    "scientific_config_sha256": neg8_scientific_config_sha256,
                }
            )
        elif index == len(bundle_ids) - 1:
            member.update(
                {
                    "role": "neg8_daily_reference_end",
                    "sentinel_position": "end",
                    "canonical_neg8_workload": True,
                    "scientific_config_sha256": neg8_scientific_config_sha256,
                }
            )
        members.append(member)
    _write_fixture_json(
        manifest_root / "d117-production.json",
        {
            "schema_version": "joulewise.campaign_provenance.v2",
            "session_id": "d117-production",
            "analysis_manifest_id": analysis_manifest_id,
            "campaign_policy": {"sha256": policy_sha256},
            "first_physical_run_id": bundle_ids[0],
            "members": members,
            "cooldown_gates": [],
        },
    )


def _install_attempt_authentication_fixture(
    runs_root: Path, *, policy_sha256: str
) -> SimpleNamespace:
    """Install authenticated attempt custody that is outside the floor basis."""

    analysis_manifest_source = (
        REPO_ROOT
        / "tests"
        / "fixtures"
        / "axi_ap_spec"
        / "draft_analysis_manifest.json"
    )
    analysis_manifest = load_json(analysis_manifest_source)
    entry = analysis_manifest["entries"][0]
    manifest_id = analysis_manifest["manifest_id"]
    evidence_root = runs_root / "axi_attempt_evidence" / manifest_id
    receipt_root = evidence_root / "dispatch_receipts"
    strict_root = evidence_root / "strict_validation"
    receipt_root.mkdir(parents=True)
    strict_root.mkdir()
    analysis_manifest_path = evidence_root / "analysis_manifest.json"
    analysis_manifest_path.write_bytes(analysis_manifest_source.read_bytes())

    bundle_source = REPO_ROOT / "tests" / "fixtures" / "axi_valid_burst"
    attempt_root = (
        runs_root
        / "axi_attempt_bundles"
        / manifest_id
        / entry["entry_id"]
    )
    unselected_run_id = "d117-attempt-unselected"
    selected_run_id = "d117-attempt-selected"
    unselected_bundle = attempt_root / "a0" / unselected_run_id
    selected_bundle = attempt_root / "a1" / selected_run_id
    for run_id, bundle in (
        (unselected_run_id, unselected_bundle),
        (selected_run_id, selected_bundle),
    ):
        shutil.copytree(bundle_source, bundle)
        metadata = load_json(bundle / "metadata.json")
        metadata["run_id"] = run_id
        (bundle / "metadata.json").write_bytes(normalized_json_bytes(metadata))
    invalid_summary = load_json(unselected_bundle / "summary_metrics.json")
    invalid_summary["status"] = "failed"
    (unselected_bundle / "summary_metrics.json").write_bytes(
        normalized_json_bytes(invalid_summary)
    )

    def receipt(attempt: int, run_id: str) -> dict:
        return {
            "schema_version": "joulewise.dispatch_receipt.v1",
            "manifest_id": manifest_id,
            "entry_id": entry["entry_id"],
            "pair_id": entry["pair_id"],
            "arm": entry["arm"],
            "attempt_ordinal": attempt,
            "dispatch_started": True,
            "transport_status": "ok",
            "process_exit_code": 0,
            "admitted_request_count": 1,
            "finalized_run_id": run_id,
        }

    strict_evidence = {
        "schema_version": "joulewise.strict_validation_attempt_evidence.v1",
        "manifest_id": manifest_id,
        "entry_id": entry["entry_id"],
        "pair_id": entry["pair_id"],
        "arm": entry["arm"],
        "attempt_ordinal": 0,
        "run_id": unselected_run_id,
        "validated_bundle_sha256": complete_bundle_sha256(unselected_bundle),
        "valid": False,
        "validator_reason_codes": ["request_output_count_mismatch"],
    }
    strict_raw = render_strict_validation_evidence(strict_evidence)
    strict_sha256 = sha256_bytes(strict_raw)
    strict_path = strict_root / f"{strict_sha256}.json"
    strict_path.write_bytes(strict_raw)

    ledger_rows = []
    receipt_paths = []
    for attempt, run_id, eligible in (
        (0, unselected_run_id, False),
        (1, selected_run_id, True),
    ):
        receipt_raw = render_dispatch_receipt(receipt(attempt, run_id))
        receipt_sha256 = sha256_bytes(receipt_raw)
        receipt_path = receipt_root / f"{receipt_sha256}.json"
        receipt_path.write_bytes(receipt_raw)
        receipt_paths.append(receipt_path)
        ledger_rows.append(
            {
                "schema_version": "joulewise.attempt_ledger.v1",
                "manifest_id": manifest_id,
                "entry_id": entry["entry_id"],
                "pair_id": entry["pair_id"],
                "arm": entry["arm"],
                "attempt_ordinal": attempt,
                "run_id": run_id,
                "dispatch_receipt_sha256": receipt_sha256,
                "technical_invalid_reason_code": (
                    None if eligible else "strict_bundle_invalid"
                ),
                "reason_evidence_sha256": None if eligible else strict_sha256,
                "eligible_for_analysis": eligible,
            }
        )
    ledger_raw = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        for row in ledger_rows
    ).encode("utf-8")
    ledger_path = evidence_root / "attempt_ledger.jsonl"
    ledger_path.write_bytes(ledger_raw)

    selected_bundle_id = (
        f"{entry['entry_id']}__a1__{selected_run_id}"
    )
    selection = {
        "schema_version": "joulewise.attempt_ledger_selection.v1",
        "attempt_ledger_path": ledger_path.relative_to(runs_root).as_posix(),
        "attempt_ledger_sha256": hashlib.sha256(ledger_raw).hexdigest(),
        "analysis_manifest_path": analysis_manifest_path.relative_to(
            runs_root
        ).as_posix(),
        "analysis_manifest_sha256": file_sha256(analysis_manifest_path),
        "selected_bundle_ids": [selected_bundle_id],
        "selected_membership_sha256": canonical_sha256([selected_bundle_id]),
        "selected_bundles": [
            {
                "bundle_id": selected_bundle_id,
                "path": selected_bundle.relative_to(runs_root).as_posix(),
                "entry_id": entry["entry_id"],
                "attempt_ordinal": 1,
                "run_id": selected_run_id,
            }
        ],
        "quarantined_attempts": [
            {
                "entry_id": entry["entry_id"],
                "attempt_ordinal": 0,
                "run_id": unselected_run_id,
                "properly_quarantined": True,
                "recovery_continuity_verified": True,
            }
        ],
    }
    campaign_manifest_path = (
        runs_root / "campaign_manifests" / "d117-attempt-coverage.json"
    )
    _write_fixture_json(
        campaign_manifest_path,
        {
            "schema_version": "joulewise.campaign_provenance.v2",
            "session_id": "d117-attempt-authentication-coverage",
            "analysis_manifest_id": manifest_id,
            "campaign_policy": {"sha256": policy_sha256},
            "first_physical_run_id": selected_bundle_id,
            "members": [],
            "cooldown_gates": [],
            "attempt_ledger_selection": selection,
        },
    )
    return SimpleNamespace(
        campaign_manifest_path=campaign_manifest_path,
        analysis_manifest_path=analysis_manifest_path,
        ledger_path=ledger_path,
        receipt_paths=tuple(receipt_paths),
        strict_path=strict_path,
        selected_metadata_path=selected_bundle / "metadata.json",
        unselected_metadata_path=unselected_bundle / "metadata.json",
    )


def _run_fixture_command(
    command: list[str], *, cwd: Path, expected: set[int] = {0}
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in expected:
        raise AssertionError(
            f"fixture command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def build_d117_production_fixture(root: Path) -> SimpleNamespace:
    """Build one clean-repository, unpatched-production v2 mint fixture."""

    repository = root / "clean-repository"
    evidence_root = root / "mutable-evidence"
    second_evidence_root = root / "mutable-evidence-second"
    custody_store = root / "mutable-custody-store"
    inputs_root = root / "mint-inputs"
    _copy_repository_without_large_custody(repository)
    evidence_root.mkdir()
    second_evidence_root.mkdir()
    inputs_root.mkdir()

    fixture_pinset, fixture_inputs, _fixture_snapshot = synthetic_v2_fixture()
    producer = copy.deepcopy(fixture_pinset["producer_plans"][0])
    plan_id = producer["plan"]["plan_id"]
    source = fixture_inputs[plan_id]
    reference_ids = ["d117-neg8-start", "d117-neg8-end"]
    plan = copy.deepcopy(source.plan)
    plan["fixed_n"] = 10
    for plan_cell in plan["cells"]:
        plan_cell["minimum_claim_n"] = 10
        if plan_cell["kind"] == "absolute":
            plan_cell["ordered_bundle_ids"] = plan_cell["ordered_bundle_ids"][:10]
        else:
            plan_cell["ordered_blocks"] = plan_cell["ordered_blocks"][:10]
    plan_path = inputs_root / "production-plan.json"
    _write_fixture_json(plan_path, plan)
    plan_sha256 = file_sha256(plan_path)
    sidecar_path = inputs_root / "production-plan.sha256"
    sidecar_path.write_text(
        f"{plan_sha256}  {plan_path.name}\n", encoding="utf-8"
    )
    second_plan = copy.deepcopy(plan)
    second_plan_id = f"{plan_id}-second"
    second_plan["plan_id"] = second_plan_id
    second_plan_path = inputs_root / "production-plan-second.json"
    _write_fixture_json(second_plan_path, second_plan)
    second_plan_sha256 = file_sha256(second_plan_path)
    second_sidecar_path = inputs_root / "production-plan-second.sha256"
    second_sidecar_path.write_text(
        f"{second_plan_sha256}  {second_plan_path.name}\n", encoding="utf-8"
    )

    spec_cells = [
        copy.deepcopy(component.spec_cell)
        for role in ("decode", "prefill")
        for component in (
            source.cells[role].absolute,
            source.cells[role].comparative,
        )
    ]
    for spec_cell in spec_cells:
        if spec_cell["kind"] == "absolute":
            spec_cell["members"] = spec_cell["members"][:10]
        else:
            spec_cell["blocks"] = spec_cell["blocks"][:10]
        for binding in spec_cell["condition_family_definitions"].values():
            definition = binding["condition_family_definition"]
            definition["workload_profile"] = {
                "name": "df_ph_decode",
                "prompt_tokens": 128,
                "output_tokens": 512,
                "repetitions": 1,
                "warmup_runs": 1,
            }
            definition["measurement_target"]["metric"] = spec_cell["metric"]
            binding["condition_family_sha256"] = canonical_domain_sha256(
                CONDITION_FAMILY_DOMAIN, definition
            )
    ordered_bundle_ids = list(
        dict.fromkeys(mint1._spec_member_ids({"cells": spec_cells}))
    )
    all_spec_bundle_ids = [
        reference_ids[0], *ordered_bundle_ids, reference_ids[1]
    ]
    # The NEG8 sentinels are first-class members of the authenticated
    # campaign basis.  Give them a governed, non-mint-target extraction cell
    # so the production extractor reads and authenticates them without
    # changing the four fixed-n cells consumed by the mint.
    reference_cell = copy.deepcopy(spec_cells[0])
    reference_cell["cell_id"] = "d117-neg8-reference-coverage"
    reference_cell["members"] = [
        {"slot": "reference-start", "bundle_id": reference_ids[0]},
        {"slot": "reference-end", "bundle_id": reference_ids[1]},
    ]
    reference_cell["condition_family_id"] = "d117-neg8-reference"
    reference_family = reference_cell["condition_family_definitions"]["all"]
    reference_definition = reference_family["condition_family_definition"]
    reference_definition["condition_family_id"] = "d117-neg8-reference"
    reference_definition["workload_profile"] = {
        "name": "df_rq_mid",
        "prompt_tokens": 1024,
        "output_tokens": 256,
        "repetitions": 1,
        "warmup_runs": 1,
    }
    reference_family["condition_family_id"] = "d117-neg8-reference"
    reference_family["condition_family_sha256"] = canonical_domain_sha256(
        CONDITION_FAMILY_DOMAIN, reference_definition
    )
    spec = {
        "schema_version": mint1.EXTRACTION_SPEC_SCHEMA_VERSION,
        "cells": [*spec_cells, reference_cell],
    }
    spec_path = evidence_root / "production-extraction-spec.json"
    _write_fixture_json(spec_path, spec)
    spec_sha256 = file_sha256(spec_path)
    second_spec_cells = copy.deepcopy(spec_cells)
    for spec_cell in second_spec_cells:
        second_family_id = f'{spec_cell["condition_family_id"]}-second'
        spec_cell["condition_family_id"] = second_family_id
        for binding in spec_cell["condition_family_definitions"].values():
            binding["condition_family_id"] = second_family_id
            definition = binding["condition_family_definition"]
            definition["condition_family_id"] = second_family_id
            binding["condition_family_sha256"] = canonical_domain_sha256(
                CONDITION_FAMILY_DOMAIN, definition
            )
    second_reference_cell = copy.deepcopy(reference_cell)
    second_reference_family_id = (
        f'{second_reference_cell["condition_family_id"]}-second'
    )
    second_reference_cell["condition_family_id"] = (
        second_reference_family_id
    )
    second_reference_family = second_reference_cell[
        "condition_family_definitions"
    ]["all"]
    second_reference_family["condition_family_id"] = (
        second_reference_family_id
    )
    second_reference_definition = second_reference_family[
        "condition_family_definition"
    ]
    second_reference_definition["condition_family_id"] = (
        second_reference_family_id
    )
    second_reference_family["condition_family_sha256"] = (
        canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN, second_reference_definition
        )
    )
    second_spec = {
        "schema_version": mint1.EXTRACTION_SPEC_SCHEMA_VERSION,
        "cells": [*second_spec_cells, second_reference_cell],
    }
    second_spec_path = (
        second_evidence_root / "production-extraction-spec-second.json"
    )
    _write_fixture_json(second_spec_path, second_spec)
    second_spec_sha256 = file_sha256(second_spec_path)
    order = {
        "manifest_id": "d117-v2-production-order-v1",
        "calibration_plan_sha256": plan_sha256,
        "plan_id": plan_id,
        "executed_order": [
            {"run_id": bundle_id} for bundle_id in all_spec_bundle_ids
        ],
    }
    order_path = evidence_root / "order-manifest.json"
    _write_fixture_json(order_path, order)
    second_order = copy.deepcopy(order)
    second_order["manifest_id"] = "d117-v2-production-order-second-v1"
    second_order["calibration_plan_sha256"] = second_plan_sha256
    second_order["plan_id"] = second_plan_id
    second_order_path = second_evidence_root / "order-manifest-second.json"
    _write_fixture_json(second_order_path, second_order)

    seed_reader = BundleReader(D117_PRODUCTION_FIXTURE / "strict_seed_bundle")
    seed_window = seed_reader.measured_window()
    if seed_window is None:
        raise AssertionError("strict seed has no measured window")
    executable = repository / "tests" / "fixtures" / "fake_powermetrics_process.py"
    calibration_root = evidence_root / "instrument_validation"
    pre_path = calibration_root / "pre"
    post_path = calibration_root / "post"
    pre_evidence, pre_candidate = _install_shifted_calibration(
        pre_path,
        capture_time_s=seed_window.start_s - 60.0,
        executable=executable,
        slot="pre",
    )
    post_evidence, post_candidate = _install_shifted_calibration(
        post_path,
        capture_time_s=seed_window.end_s + 60.0,
        executable=executable,
        slot="post",
    )
    second_calibration_root = second_evidence_root / "instrument_validation"
    second_pre_path = second_calibration_root / "pre"
    second_post_path = second_calibration_root / "post"
    second_pre_evidence, second_pre_candidate = _install_shifted_calibration(
        second_pre_path,
        capture_time_s=seed_window.start_s - 90.0,
        executable=executable,
        slot="pre",
    )
    second_post_evidence, second_post_candidate = _install_shifted_calibration(
        second_post_path,
        capture_time_s=seed_window.end_s + 90.0,
        executable=executable,
        slot="post",
    )
    gc.collect()

    target_seed = root / "target-seed"
    shutil.copytree(D117_PRODUCTION_FIXTURE / "strict_seed_bundle", target_seed)
    attachment = _load_instrument_calibration_attachment(
        pre_path,
        power_policy="ac_high_power",
        runtime_powermetrics_sha256=file_sha256(executable),
        runtime_power_policy="ac_high_power",
    )
    if attachment is None:
        raise AssertionError("calibration attachment was not created")
    attachment.install(target_seed)
    target_config = load_json(target_seed / "config.json")
    target_config["workload_profile"].update(
        {"name": "df_ph_decode", "prompt_tokens": 128, "output_tokens": 512}
    )
    target_config["sampling"]["power_hz"] = 10.0
    target_config["run_metadata"]["tags"] = ["d117-production-fixture"]
    _write_fixture_json(target_seed / "config.json", target_config)
    target_metadata = load_json(target_seed / "metadata.json")
    target_metadata["instrument_calibration"] = attachment.metadata
    target_metadata["device"]["kern_osversion"] = attachment.metadata[
        "bindings"
    ]["os_build"]
    target_metadata["device"]["powermetrics"]["executable_path"] = str(
        executable.resolve()
    )
    preflight = target_metadata["campaign_environment_preflight"]
    preflight["snapshot"]["python_packages"] = {
        "mlx": {"version": attachment.metadata["bindings"]["mlx_version"]}
    }
    preflight["evaluation"]["snapshot_sha256"] = hashlib.sha256(
        json.dumps(
            preflight["snapshot"],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    target_metadata["environment"]["power"].update(
        {
            "adapter_description": "synthetic adapter",
            "adapter_watts": 140.0,
        }
    )
    target_metadata["environment"]["build_version"] = attachment.metadata[
        "bindings"
    ]["os_build"]
    target_metadata["workload_provenance"]["sampler"] = {
        "algorithm": "greedy",
        "temperature": 0.0,
        "top_p": 1.0,
    }
    target_metadata["config_sha256"] = file_sha256(target_seed / "config.json")
    _write_fixture_json(target_seed / "metadata.json", target_metadata)
    _stretch_fixture_measurement_windows(target_seed)
    _lower_fixture_idle_baseline(target_seed)
    (target_seed / "summary_metrics.json").unlink()
    target_summary_path = root / "target-seed-summary.json"
    _run_fixture_command(
        [
            sys.executable,
            "-m",
            "joulewise",
            "reduce",
            str(target_seed),
            "--output",
            str(target_summary_path),
        ],
        cwd=REPO_ROOT,
    )
    shutil.move(target_summary_path, target_seed / "summary_metrics.json")
    _run_fixture_command(
        [
            sys.executable,
            "-m",
            "joulewise",
            "validate-bundle",
            "--strict",
            str(target_seed),
        ],
        cwd=REPO_ROOT,
    )
    target_metadata = load_json(target_seed / "metadata.json")
    gc.collect()

    abba_tags: dict[str, tuple[str, str]] = {}
    for spec_cell in spec_cells:
        if spec_cell["kind"] != "comparative":
            continue
        for block in spec_cell["blocks"]:
            for position, bundle_id in block["members"].items():
                abba_tags[bundle_id] = (block["block_id"], position)
    for bundle_id in ordered_bundle_ids:
        bundle_path = evidence_root / bundle_id
        _hardlink_tree(target_seed, bundle_path)
        config = copy.deepcopy(target_config)
        config["run_id"] = bundle_id
        tags = [
            "d117-production-fixture",
            f"calibration-plan-sha256={plan_sha256}",
        ]
        if bundle_id in abba_tags:
            block_id, position = abba_tags[bundle_id]
            tags.extend(
                [
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={position[0]}",
                    "calibration-abba-sequence-index="
                    f"{('A1', 'B1', 'B2', 'A2').index(position) + 1}",
                ]
            )
        config["run_metadata"]["tags"] = tags
        (bundle_path / "config.json").unlink()
        _write_fixture_json(bundle_path / "config.json", config)
        metadata = copy.deepcopy(target_metadata)
        metadata["run_id"] = bundle_id
        metadata["config_sha256"] = file_sha256(bundle_path / "config.json")
        (bundle_path / "metadata.json").unlink()
        _write_fixture_json(bundle_path / "metadata.json", metadata)

    for reference_id in reference_ids:
        reference_path = evidence_root / reference_id
        _hardlink_tree(target_seed, reference_path)
        config = copy.deepcopy(target_config)
        config["run_id"] = reference_id
        config["workload_profile"].update(
            {"name": "df_rq_mid", "prompt_tokens": 1024, "output_tokens": 256}
        )
        (reference_path / "config.json").unlink()
        _write_fixture_json(reference_path / "config.json", config)
        metadata = copy.deepcopy(target_metadata)
        metadata["run_id"] = reference_id
        metadata["config_sha256"] = file_sha256(reference_path / "config.json")
        (reference_path / "metadata.json").unlink()
        _write_fixture_json(reference_path / "metadata.json", metadata)
        (reference_path / "summary_metrics.json").unlink()
        reference_summary_path = root / f"{reference_id}-summary.json"
        _run_fixture_command(
            [
                sys.executable,
                "-m",
                "joulewise",
                "reduce",
                str(reference_path),
                "--output",
                str(reference_summary_path),
            ],
            cwd=REPO_ROOT,
        )
        shutil.move(
            reference_summary_path, reference_path / "summary_metrics.json"
        )
        gc.collect()

    for bundle_id in all_spec_bundle_ids:
        _hardlink_tree(
            evidence_root / bundle_id,
            second_evidence_root / bundle_id,
        )
    for bundle_id in ordered_bundle_ids:
        bundle_path = second_evidence_root / bundle_id
        config_path = bundle_path / "config.json"
        config = load_json(config_path)
        tags = config["run_metadata"]["tags"]
        config["run_metadata"]["tags"] = [
            (
                f"calibration-plan-sha256={second_plan_sha256}"
                if tag.startswith("calibration-plan-sha256=")
                else tag
            )
            for tag in tags
        ]
        config_path.unlink()
        _write_fixture_json(config_path, config)
        metadata_path = bundle_path / "metadata.json"
        metadata = load_json(metadata_path)
        metadata["config_sha256"] = file_sha256(config_path)
        metadata_path.unlink()
        _write_fixture_json(metadata_path, metadata)

    acceptance_path = repository / "configs" / "calibration" / "calibration_acceptance_d079_v2.json"
    acceptance = load_calibration_acceptance_bound(acceptance_path)
    if acceptance is None:
        raise AssertionError("issued acceptance artifact did not authenticate")
    cutoff = acceptance["ledger_cutoff"]
    issued_root = D117_PRODUCTION_FIXTURE / "issued"
    ledger_path = inputs_root / "calibration_observation_ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(issued_root / "calibration_observation_ledger.jsonl", ledger_path)
    head_path = repository / "configs" / "calibration" / "calibration_ledger_head.json"
    shutil.copy2(issued_root / "calibration_ledger_head.json", head_path)
    epoch = {
        key: pre_evidence["bindings"][key]
        for key in (
            "os_build",
            "hardware_model",
            "power_policy",
            "sampling_interval_ms",
            "estimator_revision",
            "pulse_protocol_id",
        )
    }
    t1 = dict(pre_evidence["bindings"])
    session_id = "d117-production-session"
    window_id = "d117-production-window"
    evidence_root_id = "d117-production-evidence"
    second_session_id = "d117-production-session-second"
    second_window_id = "d117-production-window-second"
    second_evidence_root_id = "d117-production-evidence-second"
    session_rows = (
        (
            session_id,
            window_id,
            plan_id,
            plan_sha256,
            evidence_root_id,
            evidence_root,
            (
                ("pre", "d117-production-pre", pre_path, pre_candidate),
                ("post", "d117-production-post", post_path, post_candidate),
            ),
        ),
        (
            second_session_id,
            second_window_id,
            second_plan_id,
            second_plan_sha256,
            second_evidence_root_id,
            second_evidence_root,
            (
                (
                    "pre",
                    "d117-production-pre-second",
                    second_pre_path,
                    second_pre_candidate,
                ),
                (
                    "post",
                    "d117-production-post-second",
                    second_post_path,
                    second_post_candidate,
                ),
            ),
        ),
    )
    for (
        receipt_session_id,
        receipt_window_id,
        receipt_plan_id,
        receipt_plan_sha256,
        receipt_evidence_root_id,
        receipt_runs_root,
        receipt_slots,
    ) in session_rows:
        append_bracket_session_receipt(
            ledger_path,
            session_id=receipt_session_id,
            window_id=receipt_window_id,
            plan_id=receipt_plan_id,
            plan_sha256=receipt_plan_sha256,
            evidence_root_id=receipt_evidence_root_id,
            runs_root=receipt_runs_root,
            slots={
                slot: {
                    "attempt_id": attempt_id,
                    "custody_locator": str(path),
                    "identity_epoch": epoch,
                    "t1_bindings": t1,
                }
                for slot, attempt_id, path, _candidate in receipt_slots
            },
            head_pin_path=head_path,
            require_committed_pin=False,
        )
        for slot, _attempt_id, path, candidate in receipt_slots:
            finalize_bracket_session_slot(
                ledger_path,
                session_id=receipt_session_id,
                slot=slot,
                disposition="valid",
                custody_locator=str(path),
                artifact_sha256=artifact_hashes(path),
                identity_epoch=epoch,
                t1_bindings=t1,
                capture_wall_time_s=str(candidate.capture_wall_time_s),
                exact_bound_lexeme_s=str(candidate.b_fiducial_s),
            )
        _write_fixture_json(
            head_path,
            terminal_head_pin_for_session(
                ledger_path, session_id=receipt_session_id
            ),
        )
        session_snapshot = load_calibration_ledger_snapshot(
            ledger_path,
            head_path,
            baseline_sequence=cutoff["sequence"],
            baseline_digest=cutoff["head_digest"],
            require_committed_pin=False,
            verify_custody=False,
        )
        if not session_snapshot.valid:
            raise AssertionError(session_snapshot.refusal_reasons)
        session_binding = build_calibration_bracket_binding(
            session_snapshot,
            session_id=receipt_session_id,
            window_id=receipt_window_id,
            plan_id=receipt_plan_id,
            plan_sha256=receipt_plan_sha256,
            evidence_root_id=receipt_evidence_root_id,
            runs_root=receipt_runs_root,
        )
        session_binding_path = inputs_root / (
            "bracket-binding.json"
            if receipt_session_id == session_id
            else "bracket-binding-second.json"
        )
        _write_fixture_json(session_binding_path, session_binding)
    _write_fixture_json(
        head_path,
        terminal_head_pin_for_session(
            ledger_path, session_id=second_session_id
        ),
    )
    snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_path,
        baseline_sequence=cutoff["sequence"],
        baseline_digest=cutoff["head_digest"],
        require_committed_pin=False,
        verify_custody=False,
    )
    if not snapshot.valid:
        raise AssertionError(snapshot.refusal_reasons)

    source_store = _d117_production_custody_store()
    custody_store.mkdir()
    for content_dir in source_store.iterdir():
        if content_dir.is_dir():
            _hardlink_tree(content_dir, custody_store / content_dir.name)
    for path in (pre_path, post_path, second_pre_path, second_post_path):
        content_id = content_id_from_artifact_hashes(artifact_hashes(path))
        if content_id is None:
            raise AssertionError("new session custody has no content identity")
        _hardlink_tree(path, custody_store / content_id)
    (custody_store / CUSTODY_STORE_MANIFEST_NAME).write_bytes(
        calibration_custody_store_manifest_bytes(snapshot)
    )
    store_snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_path,
        baseline_sequence=cutoff["sequence"],
        baseline_digest=cutoff["head_digest"],
        require_committed_pin=False,
        calibration_custody_store=custody_store,
    )
    if not store_snapshot.valid:
        raise AssertionError(store_snapshot.refusal_reasons)
    binding_path = inputs_root / "bracket-binding.json"
    second_binding_path = inputs_root / "bracket-binding-second.json"
    binding = load_json(binding_path)
    second_binding = load_json(second_binding_path)

    _run_fixture_command(["git", "init", "-q"], cwd=repository)
    _run_fixture_command(["git", "config", "user.name", "D117 Fixture"], cwd=repository)
    _run_fixture_command(["git", "config", "user.email", "d117@example.invalid"], cwd=repository)
    _run_fixture_command(["git", "add", "."], cwd=repository)
    _run_fixture_command(["git", "commit", "-q", "-m", "d117 production fixture"], cwd=repository)
    commit = _run_fixture_command(
        ["git", "rev-parse", "HEAD"], cwd=repository
    ).stdout.strip()
    committed_head = _run_fixture_command(
        ["git", "show", f"HEAD:{head_path.relative_to(repository).as_posix()}"],
        cwd=repository,
    ).stdout.encode("utf-8")
    if committed_head != head_path.read_bytes():
        raise AssertionError("committed terminal ledger head differs from worktree")

    policy_path = (
        repository
        / "configs"
        / "campaign_policies"
        / "quiet_mac_p2_production.json"
    )
    policy_sha256 = file_sha256(policy_path)
    basis_bundle_ids = [reference_ids[0], *ordered_bundle_ids, reference_ids[1]]
    from scripts.run_campaign import (
        _normalized_benchmark_config,
        _scientific_config_sha256,
    )

    reference_config = load_json(evidence_root / reference_ids[0] / "config.json")
    neg8_scientific_config_sha256 = _scientific_config_sha256(
        _normalized_benchmark_config(reference_config)
    )
    reference_metadata = load_json(
        evidence_root / reference_ids[0] / "metadata.json"
    )
    freshness_bindings = neg8_freshness_bindings_from_metadata(
        reference_metadata
    )
    if neg8_scientific_config_sha256 is None or freshness_bindings is None:
        raise AssertionError("fixture NEG-8 identities are unavailable")
    reference_summary = load_json(
        evidence_root / reference_ids[0] / "summary_metrics.json"
    )
    gross_point = float(reference_summary["gross_energy_j"])
    idle_subtracted_point = float(
        reference_summary["idle_subtracted_energy_j"]
    )
    reference_evidence_sha256 = complete_bundle_sha256(
        evidence_root / reference_ids[0]
    )
    neg8_corpus_members = [
        {
            "bundle_id": f"d117-settled-neg8-reference-{index:02d}",
            "point_gross_j": gross_point + (index * 1e-6),
            "point_idle_subtracted_j": idle_subtracted_point + (index * 1e-6),
            "bundle_evidence_sha256": reference_evidence_sha256,
        }
        for index in range(10)
    ]
    neg8_manifest_sha256 = hashlib.sha256(
        json.dumps(
            neg8_corpus_members,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    neg8_drift_bound_path = inputs_root / "neg8-drift-bound.json"
    _write_fixture_json(
        neg8_drift_bound_path,
        build_neg8_drift_bound_artifact(
            corpus_id="d117-settled-neg8-reference-corpus",
            condition_id="df_rq_mid",
            manifest_sha256=neg8_manifest_sha256,
            scientific_config_sha256=neg8_scientific_config_sha256,
            members=neg8_corpus_members,
            derivation_timestamp_s=time.time(),
            freshness_bindings=freshness_bindings,
        ),
    )
    _install_recovered_campaign_manifest(
        evidence_root,
        basis_bundle_ids,
        policy_sha256=policy_sha256,
        neg8_scientific_config_sha256=neg8_scientific_config_sha256,
    )
    _install_recovered_campaign_manifest(
        second_evidence_root,
        basis_bundle_ids,
        policy_sha256=policy_sha256,
        neg8_scientific_config_sha256=neg8_scientific_config_sha256,
        analysis_manifest_id="d117-production-analysis-second",
    )
    campaign_path = evidence_root / "campaign_log.jsonl"
    campaign_manifest_path = (
        evidence_root / "campaign_manifests" / "d117-production.json"
    )
    campaign_manifest = load_json(campaign_manifest_path)
    campaign_attestation = campaign_provenance_attestation(
        manifest_path=campaign_manifest_path,
        raw_manifest_bytes=campaign_manifest_path.read_bytes(),
        manifest=campaign_manifest,
        timestamp="2026-08-08T12:00:00Z",
    )
    second_campaign_path = second_evidence_root / "campaign_log.jsonl"
    second_campaign_manifest_path = (
        second_evidence_root / "campaign_manifests" / "d117-production.json"
    )
    second_campaign_manifest = load_json(second_campaign_manifest_path)
    second_campaign_attestation = campaign_provenance_attestation(
        manifest_path=second_campaign_manifest_path,
        raw_manifest_bytes=second_campaign_manifest_path.read_bytes(),
        manifest=second_campaign_manifest,
        timestamp="2026-08-08T12:00:00Z",
    )
    campaign_path.write_text(
        json.dumps(campaign_attestation, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    campaign_arguments = [
            "--runs-dir",
            str(evidence_root),
            "--log",
            str(campaign_path),
            "--campaign-policy",
            str(policy_path),
            "--neg8-drift-bound",
            str(neg8_drift_bound_path),
            "--whole-window-verdict",
    ]
    runner_ledger_path = (
        repository / "runs" / "calibration_observation_ledger.jsonl"
    )
    runner_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ledger_path, runner_ledger_path)
    campaign_result = _run_fixture_command(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from joulewise.authentication_io import "
                "V2AuthenticationReadSession; "
                "from scripts.run_campaign import main; "
                "session=V2AuthenticationReadSession(); "
                "session.__enter__(); "
                "code=main(sys.argv[1:]); "
                "session.__exit__(None,None,None); "
                "raise SystemExit(code)"
            ),
            *campaign_arguments,
        ],
        cwd=repository,
        expected={0, 1},
    )
    runner_ledger_path.unlink()
    campaign_code = campaign_result.returncode
    campaign_rows = [
        json.loads(line)
        for line in campaign_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    verdict_rows = [
        row
        for row in campaign_rows
        if row.get("record_type") == "idle_admission_whole_window_verdict"
    ]
    if len(verdict_rows) != 1:
        raise AssertionError("production whole-window runner wrote an unexpected log")
    verdict = verdict_rows[0]
    second_verdict = copy.deepcopy(verdict)
    attempt_fixture = _install_attempt_authentication_fixture(
        evidence_root, policy_sha256=policy_sha256
    )
    attempt_campaign_manifest = load_json(
        attempt_fixture.campaign_manifest_path
    )
    attempt_campaign_attestation = campaign_provenance_attestation(
        manifest_path=attempt_fixture.campaign_manifest_path,
        raw_manifest_bytes=attempt_fixture.campaign_manifest_path.read_bytes(),
        manifest=attempt_campaign_manifest,
        timestamp="2026-08-08T12:00:01Z",
    )
    verdict["row_provenance"]["source_campaign_manifests"].append(
        {
            "path": "campaign_manifests/d117-attempt-coverage.json",
            "sha256": file_sha256(attempt_fixture.campaign_manifest_path),
        }
    )
    from scripts.run_campaign import load_campaign_policy

    policy_binding = load_campaign_policy(policy_path)
    bracket, bracket_reasons = calibration_bracket_for_bundles(
        evidence_root,
        [evidence_root / bundle_id for bundle_id in basis_bundle_ids],
        policy_binding.policy.calibration_bracketing,
        ledger_snapshot=store_snapshot,
        bracket_binding=binding,
        bracket_window_id=window_id,
        bracket_plan_id=plan_id,
        bracket_plan_sha256=plan_sha256,
        bracket_evidence_root_id=evidence_root_id,
    )
    if bracket_reasons:
        raise AssertionError(bracket_reasons)
    second_bracket, second_bracket_reasons = calibration_bracket_for_bundles(
        second_evidence_root,
        [second_evidence_root / bundle_id for bundle_id in basis_bundle_ids],
        policy_binding.policy.calibration_bracketing,
        ledger_snapshot=store_snapshot,
        bracket_binding=second_binding,
        bracket_window_id=second_window_id,
        bracket_plan_id=second_plan_id,
        bracket_plan_sha256=second_plan_sha256,
        bracket_evidence_root_id=second_evidence_root_id,
    )
    if second_bracket_reasons:
        raise AssertionError(second_bracket_reasons)
    core = verdict["idle_admission_core"]
    non_calibration_conditions = [
        reason
        for reason in core["conditions"]
        if reason not in {
            "instrument_calibration_bracket_missing",
            "calibration_bracket_binding_missing",
        }
    ]
    if non_calibration_conditions:
        raise AssertionError(
            f"production verdict has unrelated conditions: {non_calibration_conditions}; "
            f"exit_code={campaign_code}"
        )
    core["instrument_calibration_bracket"] = bracket
    core["conditions"] = []
    verdict["status"] = "passed"
    old_basis = verdict["evaluation_basis"]
    verdict["evaluation_basis"] = build_evaluation_basis(
        policy_sha256=policy_sha256,
        member_occurrences=old_basis["member_occurrences"],
        calibration_bracket=bracket,
        consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
    )
    second_core = second_verdict["idle_admission_core"]
    second_non_calibration_conditions = [
        reason
        for reason in second_core["conditions"]
        if reason not in {
            "instrument_calibration_bracket_missing",
            "calibration_bracket_binding_missing",
        }
    ]
    if second_non_calibration_conditions:
        raise AssertionError(
            "production verdict has unrelated second-session conditions: "
            f"{second_non_calibration_conditions}; exit_code={campaign_code}"
        )
    second_core["instrument_calibration_bracket"] = second_bracket
    second_core["conditions"] = []
    second_verdict["status"] = "passed"
    second_old_basis = second_verdict["evaluation_basis"]
    second_occurrences = copy.deepcopy(
        second_old_basis["member_occurrences"]
    )
    for occurrence in second_occurrences:
        bundle_path = second_evidence_root / occurrence["bundle_path"]
        for name, field in (
            ("config.json", "config_sha256"),
            ("metadata.json", "metadata_sha256"),
            ("summary_metrics.json", "summary_sha256"),
        ):
            occurrence[field] = file_sha256(bundle_path / name)
    second_verdict["evaluation_basis"] = build_evaluation_basis(
        policy_sha256=policy_sha256,
        member_occurrences=second_occurrences,
        calibration_bracket=second_bracket,
        consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
    )
    second_verdict["evaluation_scope"]["runs_root"] = str(
        second_evidence_root.resolve()
    )
    second_verdict["row_provenance"]["source_campaign_manifests"] = [
        {
            "path": "campaign_manifests/d117-production.json",
            "sha256": file_sha256(second_campaign_manifest_path),
        }
    ]
    campaign_path.write_text(
        json.dumps(
            campaign_attestation, sort_keys=True, separators=(",", ":")
        )
        + "\n"
        + json.dumps(
            attempt_campaign_attestation,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        + json.dumps(verdict, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    second_campaign_path.write_text(
        json.dumps(
            second_campaign_attestation,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        + json.dumps(second_verdict, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    basis_sha256 = verdict["evaluation_basis"]["sha256"]
    second_basis_sha256 = second_verdict["evaluation_basis"]["sha256"]

    report_path = evidence_root / "extraction-report.json"
    with V2AuthenticationReadSession():
        report = extract_cells(
            evidence_root,
            spec,
            manifest_id="d117-production-analysis",
            evaluation_basis_sha256=basis_sha256,
            consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
            hash_bundles=True,
            calibration_ledger_snapshot=store_snapshot,
        )
    _write_fixture_json(report_path, report)
    profile_errors = validate_d117_mint_consumption_report(report)
    if profile_errors:
        raise AssertionError(profile_errors)
    report_cells = {cell["cell_id"]: cell for cell in report["cells"]}
    second_report_path = second_evidence_root / "extraction-report-second.json"
    with V2AuthenticationReadSession():
        second_report = extract_cells(
            second_evidence_root,
            second_spec,
            manifest_id="d117-production-analysis-second",
            evaluation_basis_sha256=second_basis_sha256,
            consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
            hash_bundles=True,
            calibration_ledger_snapshot=store_snapshot,
        )
    _write_fixture_json(second_report_path, second_report)
    second_profile_errors = validate_d117_mint_consumption_report(
        second_report
    )
    if second_profile_errors:
        raise AssertionError(second_profile_errors)
    second_report_cells = {
        cell["cell_id"]: cell for cell in second_report["cells"]
    }
    unmintable_second_cells = {
        cell_id: {
            "refusal_reasons": cell["refusal_reasons"],
            "floor": cell["floor"],
        }
        for cell_id, cell in second_report_cells.items()
        if cell_id != "d117-neg8-reference-coverage" and cell["floor"] is None
    }
    if unmintable_second_cells:
        raise AssertionError(
            "second production extraction did not form mintable cells: "
            f"{unmintable_second_cells}; "
            "idle_admission_refusals="
            f"{second_report['idle_admission_refusals']}"
        )

    producer["plan"].update(
        {
            "sha256": plan_sha256,
            "declared_sha256": plan_sha256,
            "sidecar_sha256": file_sha256(sidecar_path),
            "relative_path": plan_path.name,
        }
    )
    producer["evidence_root_id"] = evidence_root_id
    producer["extraction_spec"].update(
        {"sha256": spec_sha256, "member_count": len(all_spec_bundle_ids)}
    )
    seed_stack = mint1._derive_stack_identity(
        load_json(evidence_root / ordered_bundle_ids[0] / "config.json"),
        load_json(evidence_root / ordered_bundle_ids[0] / "metadata.json"),
    )
    scientific = mint1.scientific_config_identity(
        load_json(evidence_root / ordered_bundle_ids[0] / "config.json")
    )
    if scientific is None:
        raise AssertionError("fixture scientific identity is unavailable")
    producer["model_runtime_config"] = {
        "model_artifact_sha256": seed_stack["model_artifact_sha256"],
        "runtime_identity_sha256": canonical_domain_sha256(
            mint1.STACK_IDENTITY_DOMAIN, seed_stack
        ),
        "config_set_sha256": hashlib.sha256(
            json.dumps(
                scientific,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest(),
    }
    producer["calibration_acceptance"] = {
        "acceptance_id": acceptance["acceptance_id"],
        "artifact_sha256": file_sha256(acceptance_path),
        "derivation_sha256": acceptance["derivation_sha256"],
        "derivation_rule_id": acceptance["schema_version"],
    }
    manifest_cells = []
    manifest_family_by_role = {}
    for cell_pin in producer["cells"]:
        role = cell_pin["role"]
        cell_pin["absolute"]["expected_n"] = 10
        cell_pin["comparative"]["expected_n"] = 10
        role_components = {}
        for component_name in ("absolute", "comparative"):
            template = getattr(source.cells[role], component_name)
            report_cell = report_cells[template.calibration_cell_id]
            component_pin = cell_pin[component_name]
            component_pin.update(
                {
                    "evidence_root_id": evidence_root_id,
                    "evaluation_basis_sha256": basis_sha256,
                    "evaluation_basis_members": len(basis_bundle_ids),
                    "extraction_spec_sha256": spec_sha256,
                    "extraction_spec_members": len(all_spec_bundle_ids),
                    "order_manifest_id": order["manifest_id"],
                    "order_manifest_sha256": file_sha256(order_path),
                    "consumption_semantics_id": MINTED_CONSUMPTION_SEMANTICS_ID,
                    "drift_allowance_j": report_cell[
                        "whole_window_drift_allowance"
                    ]["allowance_j"],
                    "members": [
                        {
                            "bundle_id": row["bundle_id"],
                            "config_sha256": row["config_sha256"],
                        }
                        for row in report_cell["members"]
                    ],
                }
            )
            role_components[component_name] = component_pin
        family = spec_cells[0 if role == "decode" else 2][
            "condition_family_definitions"
        ]["all"]
        manifest_family_by_role[role] = family
        family_pin = {
            "condition_family_id": family["condition_family_id"],
            "condition_family_sha256": family["condition_family_sha256"],
        }
        cell_pin.update(
            {
                "condition_family_id": family["condition_family_id"],
                "condition_family_sha256": family["condition_family_sha256"],
                "allowed_consumer_condition_families": [family_pin],
            }
        )
        post = cell_pin["postcollection"]
        pre_observation = store_snapshot.bracket_session_by_id[session_id].finalized_slots["pre"]
        post_observation = store_snapshot.bracket_session_by_id[session_id].finalized_slots["post"]
        allowance = bracket["acceptance"]["allowance"]
        absolute_floor = report_cells[
            role_components["absolute"]["calibration_cell_id"]
        ]["floor"]["drift_widened_guarded_floor_j"]
        comparative_floor = report_cells[
            role_components["comparative"]["calibration_cell_id"]
        ]["floor"]["drift_widened_guarded_floor_j"]
        operative_floor = max(float(absolute_floor), float(comparative_floor))
        post.update(
            {
                "absolute_evaluation_basis_sha256": basis_sha256,
                "absolute_evaluation_basis_members": len(basis_bundle_ids),
                "comparative_evaluation_basis_sha256": basis_sha256,
                "comparative_evaluation_basis_members": len(basis_bundle_ids),
                "pre_receipt_sha256": pre_observation.receipt_digest,
                "pre_content_sha256": pre_observation.content_id,
                "post_receipt_sha256": post_observation.receipt_digest,
                "post_content_sha256": post_observation.content_id,
                "bracket_binding_sha256": file_sha256(binding_path),
                "terminal_ledger_head_sha256": store_snapshot.head_digest,
                "observed_drift_s": format(
                    Decimal(bracket["acceptance"]["drift"]["observed_s"]),
                    "f",
                ),
                "allowance_rule": generalized.V2_ALLOWANCE_RULE,
                "bracket_screen_s": bracket["acceptance"]["drift"]["screen_s"],
                "applied_allowance_s": allowance["value_s"],
                "allowance_embedding_count": allowance["embedding_count"],
                "extraction_report_sha256": file_sha256(report_path),
                "absolute_floor_full_precision": str(absolute_floor),
                "comparative_floor_full_precision": str(comparative_floor),
                "operative_floor_full_precision": str(operative_floor),
                "absolute_floor_six_decimal": f"{float(absolute_floor):.6f}",
                "comparative_floor_six_decimal": f"{float(comparative_floor):.6f}",
                "operative_floor_six_decimal": f"{float(operative_floor):.6f}",
            }
        )
        manifest_cells.append(
            {
                "role": role,
                "absolute": {
                    "evidence_root": str(evidence_root),
                    "report": str(report_path),
                    "spec": str(spec_path),
                    "order_manifest": str(order_path),
                },
                "comparative": {
                    "evidence_root": str(evidence_root),
                    "report": str(report_path),
                    "spec": str(spec_path),
                    "order_manifest": str(order_path),
                },
                "allowed_consumer_condition_families": [family],
            }
        )

    second_producer = copy.deepcopy(producer)
    second_producer["plan"].update(
        {
            "plan_id": second_plan_id,
            "sha256": second_plan_sha256,
            "declared_sha256": second_plan_sha256,
            "sidecar_sha256": file_sha256(second_sidecar_path),
            "relative_path": second_plan_path.name,
        }
    )
    second_producer["evidence_root_id"] = second_evidence_root_id
    second_producer["component_artifact"]["artifact_id"] += "-second"
    second_producer["extraction_spec"].update(
        {
            "sha256": second_spec_sha256,
            "member_count": len(all_spec_bundle_ids),
        }
    )
    second_pre_observation = store_snapshot.bracket_session_by_id[
        second_session_id
    ].finalized_slots["pre"]
    second_post_observation = store_snapshot.bracket_session_by_id[
        second_session_id
    ].finalized_slots["post"]
    second_allowance = second_bracket["acceptance"]["allowance"]
    second_manifest_cells = []
    for cell_pin in second_producer["cells"]:
        role = cell_pin["role"]
        cell_pin["cell_id"] += "-second"
        cell_pin["transport_group_id"] += "-second"
        second_family = second_spec_cells[0 if role == "decode" else 2][
            "condition_family_definitions"
        ]["all"]
        second_family_pin = {
            "condition_family_id": second_family["condition_family_id"],
            "condition_family_sha256": second_family[
                "condition_family_sha256"
            ],
        }
        cell_pin.update(
            {
                "condition_family_id": second_family[
                    "condition_family_id"
                ],
                "condition_family_sha256": second_family[
                    "condition_family_sha256"
                ],
                "allowed_consumer_condition_families": [second_family_pin],
            }
        )
        for component_name in ("absolute", "comparative"):
            component_pin = cell_pin[component_name]
            report_cell = second_report_cells[
                component_pin["calibration_cell_id"]
            ]
            component_pin.update(
                {
                    "evidence_root_id": second_evidence_root_id,
                    "evaluation_basis_sha256": second_basis_sha256,
                    "extraction_spec_sha256": second_spec_sha256,
                    "extraction_spec_members": len(all_spec_bundle_ids),
                    "order_manifest_id": second_order["manifest_id"],
                    "order_manifest_sha256": file_sha256(
                        second_order_path
                    ),
                    "drift_allowance_j": report_cell[
                        "whole_window_drift_allowance"
                    ]["allowance_j"],
                    "members": [
                        {
                            "bundle_id": row["bundle_id"],
                            "config_sha256": row["config_sha256"],
                        }
                        for row in report_cell["members"]
                    ],
                }
            )
        post = cell_pin["postcollection"]
        absolute_floor = second_report_cells[
            cell_pin["absolute"]["calibration_cell_id"]
        ]["floor"]["drift_widened_guarded_floor_j"]
        comparative_floor = second_report_cells[
            cell_pin["comparative"]["calibration_cell_id"]
        ]["floor"]["drift_widened_guarded_floor_j"]
        operative_floor = max(float(absolute_floor), float(comparative_floor))
        post.update(
            {
                "absolute_evaluation_basis_sha256": second_basis_sha256,
                "comparative_evaluation_basis_sha256": second_basis_sha256,
                "pre_receipt_sha256": second_pre_observation.receipt_digest,
                "pre_content_sha256": second_pre_observation.content_id,
                "post_receipt_sha256": second_post_observation.receipt_digest,
                "post_content_sha256": second_post_observation.content_id,
                "bracket_binding_sha256": file_sha256(second_binding_path),
                "terminal_ledger_head_sha256": store_snapshot.head_digest,
                "observed_drift_s": format(
                    Decimal(
                        second_bracket["acceptance"]["drift"]["observed_s"]
                    ),
                    "f",
                ),
                "allowance_rule": generalized.V2_ALLOWANCE_RULE,
                "bracket_screen_s": second_bracket["acceptance"]["drift"][
                    "screen_s"
                ],
                "applied_allowance_s": second_allowance["value_s"],
                "allowance_embedding_count": second_allowance[
                    "embedding_count"
                ],
                "extraction_report_sha256": file_sha256(second_report_path),
                "absolute_floor_full_precision": str(absolute_floor),
                "comparative_floor_full_precision": str(comparative_floor),
                "operative_floor_full_precision": str(operative_floor),
                "absolute_floor_six_decimal": f"{float(absolute_floor):.6f}",
                "comparative_floor_six_decimal": (
                    f"{float(comparative_floor):.6f}"
                ),
                "operative_floor_six_decimal": f"{operative_floor:.6f}",
            }
        )
        second_manifest_cells.append(
            {
                "role": role,
                "absolute": {
                    "evidence_root": str(second_evidence_root),
                    "report": str(second_report_path),
                    "spec": str(second_spec_path),
                    "order_manifest": str(second_order_path),
                },
                "comparative": {
                    "evidence_root": str(second_evidence_root),
                    "report": str(second_report_path),
                    "spec": str(second_spec_path),
                    "order_manifest": str(second_order_path),
                },
                "allowed_consumer_condition_families": [
                    second_family
                ],
            }
        )

    pinset = {
        "schema_version": generalized.PINSET_SCHEMA_VERSION_V2,
        "mint_tool_version": generalized.V2_MINT_TOOL_VERSION,
        "producer_plans": [producer, second_producer],
        "aggregate": copy.deepcopy(fixture_pinset["aggregate"]),
    }
    pinset["aggregate"]["artifact_id"] = "d117-production-authentic-floor"
    pinset["aggregate"]["plan_set_id"] = "d117-production-plan-set"
    pinset["aggregate"]["component_artifacts"] = [
        {
            "plan_id": item["plan"]["plan_id"],
            "artifact_id": item["component_artifact"]["artifact_id"],
            "sha256": "0" * 64,
            "producer_pin_sha256": "0" * 64,
        }
        for item in (producer, second_producer)
    ]
    pinset["aggregate"]["cell_ids"] = [
        cell["cell_id"]
        for item in (producer, second_producer)
        for cell in item["cells"]
    ]
    pinset["aggregate"]["transport_allowlists"] = [
        {
            "transport_group_id": cell["transport_group_id"],
            "cell_ids": [cell["cell_id"]],
            "allowed_consumer_condition_families": cell[
                "allowed_consumer_condition_families"
            ],
        }
        for item in (producer, second_producer)
        for cell in item["cells"]
    ]
    _repair_v2_pinset_self_hashes(pinset)
    pinset_path, pinset_sha256 = write_pinset(inputs_root, pinset)
    input_manifest_path = inputs_root / "production-input-manifest.json"
    _write_fixture_json(
        input_manifest_path,
        {
            "schema_version": "joulewise.floor_mint_inputs.v2",
            "calibration_acceptance": str(acceptance_path),
            "calibration_ledger": str(ledger_path),
            "calibration_ledger_head_pin": str(head_path),
            "producer_plans": [
                {
                    "plan_id": plan_id,
                    "calibration_plan": str(plan_path),
                    "calibration_plan_sidecar": str(sidecar_path),
                    "bracket_binding": str(binding_path),
                    "cells": manifest_cells,
                },
                {
                    "plan_id": second_plan_id,
                    "calibration_plan": str(second_plan_path),
                    "calibration_plan_sidecar": str(second_sidecar_path),
                    "bracket_binding": str(second_binding_path),
                    "cells": second_manifest_cells,
                },
            ],
        },
    )
    # Freeze the component hashes from one production-authenticated build,
    # then repair only the independently-defined pinset self hashes.  The
    # subsequent acceptance test still invokes the unpatched production CLI
    # from scratch and requires the frozen bytes to verify.
    bootstrap_code = r'''
import hashlib, json, sys
from pathlib import Path
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.cli import validate_bundle
from scripts import mint_floor_artifact_generalized as generalized

loaded = generalized.load_pinset(Path(sys.argv[1]), sys.argv[2])
if not isinstance(loaded, generalized.V2Pinset):
    raise AssertionError("production fixture did not form a final v2 pinset")
with V2AuthenticationReadSession():
    inputs, _roots, snapshot = generalized._authenticate_v2_inputs(
        pinset=loaded,
        pinset_path=Path(sys.argv[1]),
        pinset_sha256=sys.argv[2],
        input_manifest_path=Path(sys.argv[3]),
        strict_validator=lambda path, strict: validate_bundle(path, strict=strict),
        consumption_semantics_id=None,
        calibration_custody_store=Path(sys.argv[4]),
    )
    _artifact, components = generalized._build_v2_artifacts(
        pinset=loaded,
        pinset_path=Path(sys.argv[1]),
        pinset_sha256=sys.argv[2],
        producer_inputs=inputs,
        calibration_ledger_snapshot=snapshot,
        project_commit=sys.argv[5],
        project_tree_state="clean",
        origin_main_contains_head=False,
        head_pin_commit_contained_in_origin_main=False,
    )
hashes = []
for component in components:
    payload = (json.dumps(component, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    hashes.append(hashlib.sha256(payload).hexdigest())
print("COMPONENT_SHA256S=" + json.dumps(hashes))
'''
    bootstrap = _run_fixture_command(
        [
            sys.executable,
            "-c",
            bootstrap_code,
            str(pinset_path),
            pinset_sha256,
            str(input_manifest_path),
            str(custody_store),
            commit,
        ],
        cwd=repository,
    )
    component_sha256s = json.loads(
        next(
            line
            for line in bootstrap.stdout.splitlines()
            if line.startswith("COMPONENT_SHA256S=")
        ).removeprefix("COMPONENT_SHA256S=")
    )
    if len(component_sha256s) != 2:
        raise AssertionError("production fixture did not build two components")
    for item, entry, component_sha256 in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
        component_sha256s,
        strict=True,
    ):
        item["component_artifact"]["sha256"] = component_sha256
        entry["sha256"] = component_sha256
    _repair_v2_pinset_self_hashes(pinset)
    pinset_path, pinset_sha256 = write_pinset(inputs_root, pinset)
    return SimpleNamespace(
        repository=repository,
        evidence_root=evidence_root,
        second_evidence_root=second_evidence_root,
        custody_store=custody_store,
        inputs_root=inputs_root,
        pinset_path=pinset_path,
        pinset_sha256=pinset_sha256,
        input_manifest_path=input_manifest_path,
        floor_path=inputs_root / "floor.json",
        statement_path=inputs_root / "single-count.txt",
        project_commit=commit,
        producer=producer,
        second_producer=second_producer,
        report_path=report_path,
        second_report_path=second_report_path,
        campaign_path=campaign_path,
        second_campaign_path=second_campaign_path,
        acceptance_path=acceptance_path,
        ledger_path=ledger_path,
        head_path=head_path,
        binding_path=binding_path,
        second_binding_path=second_binding_path,
        spec_path=spec_path,
        order_path=order_path,
        second_order_path=second_order_path,
        plan_path=plan_path,
        second_plan_path=second_plan_path,
        bundle_ids=ordered_bundle_ids,
        basis_bundle_ids=basis_bundle_ids,
        ledger_snapshot=store_snapshot,
        attempt_fixture=attempt_fixture,
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


class V2PinsetAndMintTests(unittest.TestCase):
    def test_configured_core_rederives_the_pinned_phase_metric(self) -> None:
        summary = {
            "phase_energy_j": {"decode": 2.0, "prefill": 3.0},
            "energy_anchor_shift_envelopes": {
                "/phase_energy_j/decode": {
                    "point_j": 2.0,
                    "lower_j": 1.5,
                    "upper_j": 2.5,
                    "max_abs_delta_j": 0.5,
                },
                "/phase_energy_j/prefill": {
                    "point_j": 3.0,
                    "lower_j": 2.0,
                    "upper_j": 4.0,
                    "max_abs_delta_j": 1.0,
                },
            },
            "energy_bound_terms_j": {
                "E_interpolation_joint_edge_bound_j": 0.25
            },
        }
        with mock.patch.object(mint1, "METRIC", "phase_energy_j.prefill"):
            self.assertEqual(mint1._metric_value(summary), 3.0)
            self.assertEqual(
                mint1._source_admissible_half_width(summary, "bundle"),
                1.25,
            )

    def test_order_manifest_counts_shared_multimetric_members_once(self) -> None:
        mint1._validate_order(
            {
                "executed_order": [
                    {"run_id": "bundle-a"},
                    {"run_id": "bundle-b"},
                ]
            },
            target_ids=["bundle-a", "bundle-b"],
            spec_ids=["bundle-a", "bundle-b", "bundle-a", "bundle-b"],
        )

    def test_v2_pinset_can_pin_governed_non_mint_spec_members(self) -> None:
        pinset, _inputs, _snapshot = synthetic_v2_fixture()
        producer = pinset["producer_plans"][0]
        unique_mint_members = producer["extraction_spec"]["member_count"]
        producer["extraction_spec"]["member_count"] = unique_mint_members + 1
        for cell in producer["cells"]:
            for component_name in ("absolute", "comparative"):
                cell[component_name]["extraction_spec_members"] = (
                    unique_mint_members + 1
                )
        _repair_v2_pinset_self_hashes(pinset)
        self.assertIsNotNone(detection_floor._project_floor_mint_pinset_v2(pinset))
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = write_pinset(Path(tmp), pinset)
            self.assertIsInstance(
                generalized.load_pinset(path, digest), generalized.V2Pinset
            )

    def test_producer_inventory_covers_governed_non_mint_spec_members(
        self,
    ) -> None:
        component = SimpleNamespace(
            spec_sha256="s" * 64,
            spec={
                "cells": [
                    {
                        "kind": "absolute",
                        "members": [
                            {"bundle_id": "mint-member"},
                            {"bundle_id": "governed-reference"},
                        ],
                    }
                ]
            },
            members=(SimpleNamespace(bundle_id="mint-member"),),
            source_regime={
                "stack_identity": {"model_artifact_sha256": "m" * 64},
                "stack_identity_sha256": "r" * 64,
            },
            scientific_config_identity_sha256="c" * 64,
        )
        producer = {
            "plan": {
                "plan_id": "plan",
                "sha256": "p" * 64,
                "declared_sha256": "p" * 64,
                "sidecar_sha256": "d" * 64,
                "declared_calibration_scope": "production_window",
            },
            "calibration_acceptance": {
                "acceptance_id": "acceptance",
                "artifact_sha256": "a" * 64,
                "derivation_sha256": "b" * 64,
                "derivation_rule_id": "rule",
            },
            "extraction_spec": {"sha256": "s" * 64, "member_count": 2},
            "model_runtime_config": {
                "model_artifact_sha256": "m" * 64,
                "runtime_identity_sha256": "r" * 64,
                "config_set_sha256": "c" * 64,
            },
        }
        inputs = SimpleNamespace(
            plan_sha256="p" * 64,
            plan_declared_sha256="p" * 64,
            plan_sidecar_sha256="d" * 64,
            plan={
                "plan_id": "plan",
                "calibration_scope": "production_window",
            },
            calibration_acceptance={
                "acceptance_id": "acceptance",
                "derivation_sha256": "b" * 64,
                "schema_version": "rule",
            },
            calibration_acceptance_sha256="a" * 64,
            cells={
                "decode": SimpleNamespace(
                    absolute=component,
                    comparative=component,
                )
            },
        )
        generalized._v2_gate_producer_inventory(producer, inputs)

    def test_synthetic_hash_oracle_is_literal_and_builder_independent(
        self,
    ) -> None:
        helper_source = "\n".join(
            inspect.getsource(helper)
            for helper in (
                synthetic_v2_fixture,
                freeze_synthetic_v2_pinset,
                _repair_v2_pinset_self_hashes,
                _fixture_spec_member_ids,
            )
        )
        self.assertNotIn("generalized._", helper_source)
        self.assertNotIn("generalized._build_v2_artifacts", helper_source)
        self.assertNotIn("generalized._artifact_sha256", helper_source)
        self.assertTrue(
            all(value != "0" * 64 for value in SYNTHETIC_COMPONENT_SHA256S)
        )
        self.assertTrue(
            all(value != "0" * 64 for value in SYNTHETIC_PRODUCER_PIN_SHA256S)
        )
        self.assertNotEqual(SYNTHETIC_PRODUCER_SET_SHA256, "0" * 64)

    def test_desk_stage_is_structurally_disjoint_and_cannot_mint(self) -> None:
        final, _inputs, _ledger_snapshot = synthetic_v2_fixture()
        desk = copy.deepcopy(final)
        desk["schema_version"] = generalized.PIN_REQUIREMENTS_SCHEMA_VERSION_V2
        for producer in desk["producer_plans"]:
            producer["component_artifact_id"] = producer.pop(
                "component_artifact"
            )["artifact_id"]
            for cell in producer["cells"]:
                cell["allowance_contract"] = {
                    "allowance_rule": generalized.V2_ALLOWANCE_RULE,
                    "bracket_screen_s": generalized.V2_BRACKET_SCREEN_S,
                    "allowance_embedding_count": 1,
                }
                for component_name in ("absolute", "comparative"):
                    component = cell[component_name]
                    for field in (
                        "evaluation_basis_sha256",
                        "evaluation_basis_members",
                        "drift_allowance_j",
                    ):
                        component.pop(field)
                cell["postcollection"] = {"status": "unresolved"}
        aggregate = desk["aggregate"]
        for field in ("producer_set_sha256", "component_artifacts"):
            aggregate.pop(field)
        aggregate["postcollection"] = {"status": "unresolved"}
        schema = load_json(
            REPO_ROOT / "scripts" / "floor_mint_pinsets" / "schema_v2.json"
        )
        self.assertNotEqual(
            schema["$defs"]["pinRequirements"]["properties"][
                "schema_version"
            ]["const"],
            schema["$defs"]["finalPinset"]["properties"]["schema_version"][
                "const"
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = write_pinset(Path(tmp), desk)
            with self.assertRaisesRegex(
                generalized.MintError, "desk-stage.*non-mintable"
            ):
                generalized.load_pinset(path, digest)

    def test_synthetic_two_plan_four_cell_mint_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, digest, inputs, ledger_snapshot = freeze_synthetic_v2_pinset(
                Path(tmp)
            )
            artifact = generalized.mint_multi_cell_authenticated_artifact(
                pinset_path=path,
                pinset_sha256=digest,
                producer_inputs=inputs,
                calibration_ledger_snapshot=ledger_snapshot,
                project_commit="0" * 40,
                project_tree_state="clean",
            )
            self.assertEqual(
                generalized.validate_floor_artifact(
                    artifact=artifact,
                    pinset_path=path,
                    pinset_sha256=digest,
                ),
                [],
            )
        self.assertEqual(len(artifact["cells"]), 4)
        self.assertEqual(len(artifact["transport_groups"]), 4)
        self.assertEqual(
            {cell["key"]["metric"] for cell in artifact["cells"]},
            {"phase_energy_j.decode", "phase_energy_j.prefill"},
        )
        self.assertTrue(
            all(
                group["source_cell_ids"] == [cell["cell_id"]]
                for group, cell in zip(
                    artifact["transport_groups"], artifact["cells"]
                )
            )
        )

    def test_v2_mint_recomputes_rendering_but_never_fills_pins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(Path(tmp))
            )
            artifact = generalized.mint_multi_cell_authenticated_artifact(
                pinset_path=path,
                pinset_sha256=digest,
                producer_inputs=inputs,
                calibration_ledger_snapshot=ledger_snapshot,
                project_commit="0" * 40,
                project_tree_state="clean",
            )
        self.assertEqual(len(artifact["cells"]), 4)
        self.assertEqual(
            artifact["provenance"]["assurance"],
            generalized.V2_ASSURANCE_PROFILE,
        )

    def test_v2_assurance_and_git_containment_are_required_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(Path(tmp))
            )
            artifact = generalized.mint_multi_cell_authenticated_artifact(
                pinset_path=path,
                pinset_sha256=digest,
                producer_inputs=inputs,
                calibration_ledger_snapshot=ledger_snapshot,
                project_commit="0" * 40,
                project_tree_state="clean",
            )
            for field in ("assurance",):
                with self.subTest(field=field):
                    attacked = copy.deepcopy(artifact)
                    attacked["provenance"].pop(field)
                    errors = generalized.validate_floor_artifact(
                        artifact=attacked,
                        pinset_path=path,
                        pinset_sha256=digest,
                    )
                    self.assertTrue(
                        any("assurance" in error for error in errors), errors
                    )
            for containment_field in (
                "mint_commit_contained_in_origin_main",
                "head_pin_commit_contained_in_origin_main",
            ):
                with self.subTest(containment_field=containment_field):
                    unknown = copy.deepcopy(artifact)
                    unknown["provenance"]["implementation"][
                        containment_field
                    ] = None
                    self.assertEqual(
                        generalized.validate_floor_artifact(
                            artifact=unknown,
                            pinset_path=path,
                            pinset_sha256=digest,
                        ),
                        [],
                    )
                    attacked = copy.deepcopy(artifact)
                    attacked["provenance"]["implementation"].pop(
                        containment_field
                    )
                    errors = generalized.validate_floor_artifact(
                        artifact=attacked,
                        pinset_path=path,
                        pinset_sha256=digest,
                    )
                    self.assertTrue(
                        any(containment_field in error for error in errors),
                        errors,
                    )

    def test_actual_git_state_refuses_dirty_tree_and_records_containment(self) -> None:
        head = "a" * 40
        result = lambda returncode=0, stdout="": SimpleNamespace(
            returncode=returncode, stdout=stdout, stderr=""
        )
        with mock.patch.object(
            generalized.subprocess,
            "run",
            side_effect=(
                result(stdout=head + "\n"),
                result(stdout=" M evidence.json\n"),
            ),
        ):
            with self.assertRaisesRegex(
                generalized.MintError, "clean Git working tree"
            ):
                generalized._actual_v2_git_state()

        with mock.patch.object(
            generalized.subprocess,
            "run",
            side_effect=(
                result(stdout=head + "\n"),
                result(),
                result(stdout="b" * 40 + "\n"),
                result(returncode=1),
            ),
        ):
            self.assertEqual(
                generalized._actual_v2_git_state(),
                (head, False),
            )

        head_pin_path = REPO_ROOT / "configs" / "calibration_ledger.head.json"
        head_pin_commit = "c" * 40
        with mock.patch.object(
            generalized.subprocess,
            "run",
            side_effect=(
                result(stdout="b" * 40 + "\n"),
                result(stdout=head_pin_commit + "\n"),
                result(returncode=0),
            ),
        ) as run:
            self.assertTrue(
                generalized._head_pin_commit_containment_in_origin_main(
                    head_pin_path
                )
            )
            self.assertEqual(
                run.call_args_list[1].args[0],
                (
                    "git",
                    "-C",
                    str(REPO_ROOT),
                    "log",
                    "-1",
                    "--format=%H",
                    "--",
                    "configs/calibration_ledger.head.json",
                ),
            )

        with mock.patch.object(
            generalized,
            "_actual_v2_git_state",
            return_value=(head, True),
        ):
            with self.assertRaisesRegex(
                generalized.MintError, "claimed project commit differs"
            ):
                generalized.mint_multi_cell_floor_artifact(
                    pinset_path=Path("unreached-pinset.json"),
                    pinset_sha256="0" * 64,
                    input_manifest_path=Path("unreached-inputs.json"),
                    floor_path=Path("unreached-floor.json"),
                    statement_path=Path("unreached-statement.txt"),
                    project_commit="c" * 40,
                    project_tree_state="clean",
                    strict_validator=lambda _path, _strict: [],
                )

    def test_all_v2_json_routes_reject_duplicate_and_nonfinite_values(self) -> None:
        for label, raw, message in (
            ("duplicate", b'{"x": 1, "x": 2}', "duplicate JSON key"),
            ("nonfinite", b'{"x": NaN}', "non-finite JSON number"),
        ):
            with self.subTest(label=label):
                with self.assertRaisesRegex(generalized.MintError, message):
                    generalized._strict_json_value(raw, "authenticated input")
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "manifest.json"
                    path.write_bytes(raw)
                    with self.assertRaisesRegex(
                        generalized.MintError, message
                    ):
                        generalized._load_v2_input_manifest(path)

    def test_each_genuine_source_mutation_has_a_domain_specific_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(Path(tmp))
            )
            plan_id = next(iter(inputs))
            source = inputs[plan_id]

            def with_decode_cell(
                updated: generalized.V2CellComponents,
            ) -> dict[str, generalized.V2ProducerInputs]:
                return {
                    **inputs,
                    plan_id: replace(
                        source,
                        cells={**source.cells, "decode": updated},
                    ),
                }

            decode = source.cells["decode"]
            mutated_member = replace(
                decode.absolute.members[0],
                metric_value_j=decode.absolute.members[0].metric_value_j + 1.0,
            )
            member_component = replace(
                decode.absolute,
                members=(mutated_member, *decode.absolute.members[1:]),
            )
            basis_component = replace(
                decode.absolute,
                whole_window_evaluation_basis_sha256="f" * 64,
            )
            report_component = replace(
                decode.absolute,
                report_sha256="f" * 64,
            )
            report_comparative = replace(
                decode.comparative,
                report_sha256="f" * 64,
            )
            bad_ledger_values = dict(vars(ledger_snapshot))
            bad_ledger_values["head_digest"] = "f" * 64
            cases = (
                (
                    "acceptance",
                    {
                        **inputs,
                        plan_id: replace(
                            source, calibration_acceptance_sha256="f" * 64
                        ),
                    },
                    ledger_snapshot,
                    "calibration acceptance evidence mismatch",
                ),
                (
                    "binding",
                    {
                        **inputs,
                        plan_id: replace(
                            source, bracket_binding_sha256="f" * 64
                        ),
                    },
                    ledger_snapshot,
                    "bracket_binding_sha256 mismatch",
                ),
                (
                    "verdict-basis",
                    with_decode_cell(
                        replace(decode, absolute=basis_component)
                    ),
                    ledger_snapshot,
                    "absolute_evaluation_basis_sha256 mismatch",
                ),
                (
                    "member-bytes",
                    with_decode_cell(
                        replace(decode, absolute=member_component)
                    ),
                    ledger_snapshot,
                    "report cell floor differs from authenticated absolute member evidence",
                ),
                (
                    "report-bytes",
                    with_decode_cell(
                        replace(
                            decode,
                            absolute=report_component,
                            comparative=report_comparative,
                        )
                    ),
                    ledger_snapshot,
                    "extraction_report_sha256 mismatch",
                ),
                (
                    "ledger-head",
                    inputs,
                    SimpleNamespace(**bad_ledger_values),
                    "terminal_ledger_head_sha256 mismatch",
                ),
            )
            for label, candidate_inputs, candidate_ledger, message in cases:
                with self.subTest(label=label):
                    with self.assertRaisesRegex(generalized.MintError, message):
                        generalized.mint_multi_cell_authenticated_artifact(
                            pinset_path=path,
                            pinset_sha256=digest,
                            producer_inputs=candidate_inputs,
                            calibration_ledger_snapshot=candidate_ledger,
                            project_commit="0" * 40,
                            project_tree_state="clean",
                        )

    def test_fabricated_postcollection_pins_refuse_after_self_hash_repair(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(root)
            )
            fabricated = load_json(path)
            custody_hashes = (
                "pre_receipt_sha256",
                "pre_content_sha256",
                "post_receipt_sha256",
                "post_content_sha256",
                "bracket_binding_sha256",
                "terminal_ledger_head_sha256",
                "extraction_report_sha256",
            )
            for producer_index, producer in enumerate(
                fabricated["producer_plans"]
            ):
                for cell in producer["cells"]:
                    post = cell["postcollection"]
                    for hash_index, field in enumerate(custody_hashes):
                        post[field] = format(
                            producer_index * len(custody_hashes)
                            + hash_index
                            + 1,
                            "x",
                        ) * 64
                    post["observed_drift_s"] = "0.012000"
                    post["applied_allowance_s"] = "0.012000"
            _repair_v2_pinset_self_hashes(fabricated)
            candidate_path, candidate_digest = write_pinset(root, fabricated)
            with self.assertRaisesRegex(
                generalized.MintError,
                "postcollection_evidence_mismatch",
            ):
                generalized.mint_multi_cell_authenticated_artifact(
                    pinset_path=candidate_path,
                    pinset_sha256=candidate_digest,
                    producer_inputs=inputs,
                    calibration_ledger_snapshot=ledger_snapshot,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )

    def test_floor_rendering_and_extraction_record_mismatches_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(root)
            )
            source = load_json(path)
            for field, replacement, message in (
                (
                    "absolute_floor_six_decimal",
                    "6.294381",
                    r"absolute_floor\.six_decimal must equal the \.6f rendering",
                ),
                (
                    "comparative_floor_six_decimal",
                    "13.998036",
                    r"comparative_floor\.six_decimal must equal the \.6f rendering",
                ),
                (
                    "operative_floor_six_decimal",
                    "13.998036",
                    r"operative_floor\.six_decimal must equal the \.6f rendering",
                ),
                (
                    "absolute_floor_full_precision",
                    "6.294380135190099",
                    "absolute_floor_full_precision mismatch",
                ),
            ):
                with self.subTest(field=field):
                    candidate = copy.deepcopy(source)
                    candidate["producer_plans"][0]["cells"][0][
                        "postcollection"
                    ][field] = replacement
                    _repair_v2_pinset_self_hashes(candidate)
                    candidate_path, candidate_digest = write_pinset(
                        root, candidate
                    )
                    with self.assertRaisesRegex(
                        generalized.MintError,
                        message,
                    ):
                        generalized.mint_multi_cell_authenticated_artifact(
                            pinset_path=candidate_path,
                            pinset_sha256=candidate_digest,
                            producer_inputs=inputs,
                            calibration_ledger_snapshot=ledger_snapshot,
                            project_commit="0" * 40,
                            project_tree_state="clean",
                        )

    def test_coordinated_report_and_pin_change_refuses_against_floor_evidence(
        self,
    ) -> None:
        custody_store = _d117_production_custody_store()
        required_member = (
            custody_store
            / D117_PRODUCTION_CALIBRATION_CONTENT_ID
            / "manifest.json"
        )
        if not required_member.is_file():
            message = "full-fixture proof runs in d117-production-proof"
            if os.environ.get("JOULEWISE_REQUIRE_D117_FULL_FIXTURE") == "1":
                self.fail(f"{message}: required custody member is absent")
            self.skipTest(message)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = build_d117_production_fixture(root)
            source_pinset = load_json(fixture.pinset_path)
            input_manifest = load_json(fixture.input_manifest_path)
            report_path = fixture.report_path
            original_report_raw = report_path.read_bytes()

            def write_attack_pinset(
                label: str, value: dict
            ) -> tuple[Path, str]:
                destination = fixture.inputs_root / f"pinset-{label}"
                destination.mkdir(exist_ok=True)
                return write_pinset(destination, value)

            def cli_command(
                label: str,
                pinset_path: Path = fixture.pinset_path,
                pinset_sha256: str = fixture.pinset_sha256,
                input_manifest_path: Path | None = None,
                project_commit: str | None = None,
            ) -> tuple[list[str], Path, Path]:
                floor = fixture.inputs_root / f"{label}-floor.json"
                statement = fixture.inputs_root / f"{label}-single-count.txt"
                return (
                    [
                        sys.executable,
                        "scripts/mint_floor_artifact_generalized.py",
                        "--pinset",
                        str(pinset_path),
                        "--pinset-sha256",
                        pinset_sha256,
                        "--v2-input-manifest",
                        str(input_manifest_path or fixture.input_manifest_path),
                        "--calibration-custody-store",
                        str(fixture.custody_store),
                        "--out",
                        str(floor),
                        "--single-count-out",
                        str(statement),
                        "--project-commit",
                        project_commit or fixture.project_commit,
                        "--project-tree-state",
                        "clean",
                    ],
                    floor,
                    statement,
                )

            def run_refusal(
                label: str,
                message: str,
                pinset_path: Path = fixture.pinset_path,
                pinset_sha256: str = fixture.pinset_sha256,
                input_manifest_path: Path | None = None,
                project_commit: str | None = None,
            ) -> str:
                command, floor, statement = cli_command(
                    label,
                    pinset_path,
                    pinset_sha256,
                    input_manifest_path,
                    project_commit,
                )
                result = _run_fixture_command(
                    command, cwd=fixture.repository, expected={2}
                )
                self.assertIn(message, result.stderr)
                self.assertFalse(floor.exists())
                self.assertFalse(statement.exists())
                return result.stderr

            authentic_command, authentic_floor, authentic_statement = (
                cli_command("authentic")
            )
            _run_fixture_command(authentic_command, cwd=fixture.repository)
            self.assertEqual(len(load_json(authentic_floor)["cells"]), 4)
            self.assertTrue(authentic_statement.is_file())
            self.assertEqual(
                _run_fixture_command(
                    ["git", "status", "--porcelain"], cwd=fixture.repository
                ).stdout,
                "",
            )

            audit_floor = fixture.inputs_root / "audit-floor.json"
            audit_statement = fixture.inputs_root / "audit-single-count.txt"
            audit_code = r'''
import builtins, json, os, stat, sys
from pathlib import Path
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.cli import validate_bundle
from scripts.mint_floor_artifact_generalized import mint_multi_cell_floor_artifact

roots = tuple(Path(value).resolve() for value in sys.argv[1:6])
observed = set()
original_builtin_open = builtins.open
original_os_open = os.open
directory_paths = {}

def keep(path):
    candidate = Path(path).resolve(strict=False)
    return (
        any(candidate == root or root in candidate.parents for root in roots)
        and ".git" not in candidate.parts
        and "__pycache__" not in candidate.parts
        and candidate.suffix != ".pyc"
    )

def note(file, mode):
    if isinstance(file, (str, bytes, os.PathLike)) and ("r" in mode or "+" in mode):
        candidate = Path(file).resolve(strict=False)
        if keep(candidate):
            observed.add(str(candidate))

def builtin_open(file, mode="r", *args, **kwargs):
    handle = original_builtin_open(file, mode, *args, **kwargs)
    note(file, mode)
    return handle

def os_open(file, flags, mode=0o777, *, dir_fd=None):
    descriptor = original_os_open(file, flags, mode, dir_fd=dir_fd)
    candidate = Path(file)
    if not candidate.is_absolute() and dir_fd in directory_paths:
        candidate = directory_paths[dir_fd] / candidate
    candidate = candidate.resolve(strict=False)
    opened_mode = os.fstat(descriptor).st_mode
    if stat.S_ISDIR(opened_mode):
        directory_paths[descriptor] = candidate
    elif not flags & (os.O_WRONLY | os.O_RDWR) and stat.S_ISREG(opened_mode):
        if keep(candidate):
            observed.add(str(candidate))
    return descriptor

builtins.open = builtin_open
os.open = os_open
session = V2AuthenticationReadSession()
try:
    with session:
        mint_multi_cell_floor_artifact(
            pinset_path=Path(sys.argv[6]),
            pinset_sha256=sys.argv[7],
            input_manifest_path=Path(sys.argv[8]),
            calibration_custody_store=Path(sys.argv[9]),
            floor_path=Path(sys.argv[10]),
            statement_path=Path(sys.argv[11]),
            project_commit=sys.argv[12],
            project_tree_state="clean",
            strict_validator=lambda path, strict: validate_bundle(path, strict=strict),
        )
finally:
    builtins.open = original_builtin_open
    os.open = original_os_open
registered = {
    identity for identity in session.records
    if not identity.startswith("git:") and keep(identity)
}
print("AUDIT=" + json.dumps({"observed": sorted(observed), "registered": sorted(registered)}))
'''
            audit_result = _run_fixture_command(
                [
                    sys.executable,
                    "-c",
                    audit_code,
                    str(fixture.repository),
                    str(fixture.evidence_root),
                    str(fixture.second_evidence_root),
                    str(fixture.custody_store),
                    str(fixture.inputs_root),
                    str(fixture.pinset_path),
                    fixture.pinset_sha256,
                    str(fixture.input_manifest_path),
                    str(fixture.custody_store),
                    str(audit_floor),
                    str(audit_statement),
                    fixture.project_commit,
                ],
                cwd=fixture.repository,
            )
            audit_line = next(
                line
                for line in audit_result.stdout.splitlines()
                if line.startswith("AUDIT=")
            )
            audit = json.loads(audit_line.removeprefix("AUDIT="))
            self.assertEqual(audit["observed"], audit["registered"])

            genuine_paths = [
                fixture.acceptance_path,
                fixture.ledger_path,
                fixture.head_path,
                fixture.binding_path,
                fixture.second_binding_path,
                fixture.campaign_path,
                fixture.second_campaign_path,
                (
                    fixture.evidence_root
                    / "campaign_manifests"
                    / "d117-production.json"
                ),
                (
                    fixture.second_evidence_root
                    / "campaign_manifests"
                    / "d117-production.json"
                ),
                fixture.attempt_fixture.campaign_manifest_path,
                fixture.attempt_fixture.analysis_manifest_path,
                fixture.attempt_fixture.ledger_path,
                *fixture.attempt_fixture.receipt_paths,
                fixture.attempt_fixture.strict_path,
                fixture.attempt_fixture.selected_metadata_path,
                fixture.attempt_fixture.unselected_metadata_path,
            ]
            for bundle_id in fixture.basis_bundle_ids:
                genuine_paths.extend(
                    path
                    for path in (fixture.evidence_root / bundle_id).rglob("*")
                    if path.is_file()
                )
                genuine_paths.extend(
                    path
                    for path in (
                        fixture.second_evidence_root / bundle_id
                    ).rglob("*")
                    if path.is_file()
                )
            genuine_inventory = {
                str(path): file_sha256(path) for path in genuine_paths
            }

            attacked_report = json.loads(original_report_raw)
            attacked_report["floor_mint_postcollection"] = {
                "observed_drift_s": "999.000000",
                "applied_allowance_s": "999.000000",
            }
            for report_cell in attacked_report["cells"]:
                # A guarded floor may legitimately be None (absent guarded
                # basis — detection_floor emits None, never 0.0). For such
                # cells the coordinated attack FABRICATES a guarded floor
                # where none exists — a strictly stronger tamper the
                # auditor must refuse; float cells keep the +epsilon form.
                for tampered_key, container in (
                    ("drift_widened_guarded_floor_j", report_cell["floor"]),
                    ("operative_floor_j", report_cell),
                ):
                    if container[tampered_key] is None:
                        container[tampered_key] = 0.000001
                    else:
                        container[tampered_key] += 0.000001
            _write_fixture_json(report_path, attacked_report)
            attacked_report_sha256 = file_sha256(report_path)
            attacked_pinset = copy.deepcopy(source_pinset)
            attacked_cells = {
                cell["cell_id"]: cell for cell in attacked_report["cells"]
            }
            for cell_pin in attacked_pinset["producer_plans"][0]["cells"]:
                absolute_floor = attacked_cells[
                    cell_pin["absolute"]["calibration_cell_id"]
                ]["floor"]["drift_widened_guarded_floor_j"]
                comparative_floor = attacked_cells[
                    cell_pin["comparative"]["calibration_cell_id"]
                ]["floor"]["drift_widened_guarded_floor_j"]
                operative_floor = max(absolute_floor, comparative_floor)
                post = cell_pin["postcollection"]
                post.update(
                    {
                        "observed_drift_s": "999.000000",
                        "applied_allowance_s": "999.000000",
                        "extraction_report_sha256": attacked_report_sha256,
                        "absolute_floor_full_precision": str(absolute_floor),
                        "comparative_floor_full_precision": str(
                            comparative_floor
                        ),
                        "operative_floor_full_precision": str(operative_floor),
                        "absolute_floor_six_decimal": f"{absolute_floor:.6f}",
                        "comparative_floor_six_decimal": (
                            f"{comparative_floor:.6f}"
                        ),
                        "operative_floor_six_decimal": f"{operative_floor:.6f}",
                    }
                )
            _repair_v2_pinset_self_hashes(attacked_pinset)
            attacked_path, attacked_digest = write_attack_pinset(
                "coordinated-step8", attacked_pinset
            )
            attacked_loaded = generalized.load_pinset(
                attacked_path, attacked_digest
            )
            self.assertIsInstance(attacked_loaded, generalized.V2Pinset)
            generalized._validate_v2_pin_hashes(attacked_loaded)
            self.assertEqual(
                attacked_pinset["producer_plans"][0]["cells"][0][
                    "postcollection"
                ]["extraction_report_sha256"],
                file_sha256(report_path),
            )
            self.assertEqual(
                {str(path): file_sha256(path) for path in genuine_paths},
                genuine_inventory,
            )
            self.assertEqual(
                _run_fixture_command(
                    ["git", "status", "--porcelain"],
                    cwd=fixture.repository,
                ).stdout,
                "",
            )
            run_refusal(
                "coordinated-step8",
                "floor_mint_postcollection",
                attacked_path,
                attacked_digest,
            )
            self.assertEqual(
                {str(path): file_sha256(path) for path in genuine_paths},
                genuine_inventory,
            )

            attacked_report.pop("floor_mint_postcollection")
            _write_fixture_json(report_path, attacked_report)
            for cell_pin in attacked_pinset["producer_plans"][0]["cells"]:
                cell_pin["postcollection"]["extraction_report_sha256"] = (
                    file_sha256(report_path)
                )
            _repair_v2_pinset_self_hashes(attacked_pinset)
            attacked_path, attacked_digest = write_attack_pinset(
                "coordinated-step9", attacked_pinset
            )
            run_refusal(
                "coordinated-step9",
                "report cell floor differs from authenticated",
                attacked_path,
                attacked_digest,
            )

            report_path.write_bytes(original_report_raw)
            for cell_pin in attacked_pinset["producer_plans"][0]["cells"]:
                cell_pin["postcollection"]["extraction_report_sha256"] = (
                    file_sha256(report_path)
                )
            _repair_v2_pinset_self_hashes(attacked_pinset)
            attacked_path, attacked_digest = write_attack_pinset(
                "coordinated-step10", attacked_pinset
            )
            run_refusal(
                "coordinated-step10",
                "observed_drift_s mismatch against domain-owned verification projection",
                attacked_path,
                attacked_digest,
            )

            precision_pinset = copy.deepcopy(source_pinset)
            precision_post = precision_pinset["producer_plans"][0]["cells"][0][
                "postcollection"
            ]
            precision_post["absolute_floor_full_precision"] = str(
                float(precision_post["absolute_floor_full_precision"]) + 1e-9
            )
            _repair_v2_pinset_self_hashes(precision_pinset)
            precision_path, precision_digest = write_attack_pinset(
                "coordinated-step10-floor", precision_pinset
            )
            run_refusal(
                "coordinated-step10-floor",
                "absolute_floor_full_precision mismatch",
                precision_path,
                precision_digest,
            )

            allowance_report = json.loads(original_report_raw)
            allowance_cell = allowance_report["cells"][0]
            allowance_cell["whole_window_drift_allowance"]["allowance_j"] += 1.0
            allowance_cell["floor"]["whole_window_drift_allowance_j"] += 1.0
            allowance_cell["floor"][
                "whole_window_drift_allowance_provenance"
            ]["allowance_j"] += 1.0
            _write_fixture_json(report_path, allowance_report)
            allowance_pinset = copy.deepcopy(source_pinset)
            for cell_pin in allowance_pinset["producer_plans"][0]["cells"]:
                cell_pin["postcollection"]["extraction_report_sha256"] = (
                    file_sha256(report_path)
                )
            _repair_v2_pinset_self_hashes(allowance_pinset)
            allowance_path, allowance_digest = write_attack_pinset(
                "coordinated-allowance", allowance_pinset
            )
            run_refusal(
                "coordinated-allowance",
                "whole-window drift allowance",
                allowance_path,
                allowance_digest,
            )
            report_path.write_bytes(original_report_raw)
            self.assertEqual(
                {str(path): file_sha256(path) for path in genuine_paths},
                genuine_inventory,
            )

            first_manifest_producer = input_manifest["producer_plans"][0]
            campaign_manifest_path = (
                fixture.evidence_root
                / "campaign_manifests"
                / "d117-production.json"
            )
            # Blank JSONL rows leave event interpretation and the
            # config/metadata/summary evaluation-basis triplet unchanged,
            # but complete-bundle hashing still covers the added byte.
            primary_events_path = (
                fixture.evidence_root
                / fixture.bundle_ids[0]
                / "events.jsonl"
            )
            newest_session = fixture.ledger_snapshot.bracket_session_by_id[
                "d117-production-session-second"
            ]
            custody_artifact_path = (
                fixture.custody_store
                / newest_session.finalized_slots["pre"].content_id
                / "manifest.json"
            )
            attacked_acceptance_path = (
                fixture.inputs_root / "domain-acceptance.json"
            )
            attacked_acceptance_path.write_bytes(
                fixture.acceptance_path.read_bytes()
            )
            domain_paths = {
                "acceptance": attacked_acceptance_path,
                "ledger": fixture.ledger_path,
                "head": fixture.head_path,
                "binding": Path(first_manifest_producer["bracket_binding"]),
                "verdict": fixture.campaign_path,
                "campaign": campaign_manifest_path,
                "analysis_manifest": (
                    fixture.attempt_fixture.analysis_manifest_path
                ),
                "attempt_ledger": fixture.attempt_fixture.ledger_path,
                "attempt_receipt": fixture.attempt_fixture.receipt_paths[0],
                "attempt_strict": fixture.attempt_fixture.strict_path,
                "attempt_selected_metadata": (
                    fixture.attempt_fixture.selected_metadata_path
                ),
                "attempt_unselected_metadata": (
                    fixture.attempt_fixture.unselected_metadata_path
                ),
                "primary": primary_events_path,
                "report": report_path,
                "custody": custody_artifact_path,
            }
            domain_messages = {
                "acceptance": "calibration acceptance",
                "ledger": "calibration ledger",
                "head": "v2 calibration ledger snapshot is not authenticated",
                "binding": "calibration_bracket_binding_invalid",
                "verdict": "whole_window_neg8_verdict_missing",
                "campaign": "whole_window_verdict_conflict",
                # These six mutations also collect
                # whole_window_verdict_provenance_invalid. The CLI renders
                # only the first sorted reason, so conflict is the observable
                # fragment while the provenance discriminator still runs.
                "analysis_manifest": "whole_window_verdict_conflict",
                "attempt_ledger": "whole_window_verdict_conflict",
                "attempt_receipt": "whole_window_verdict_conflict",
                "attempt_strict": "whole_window_verdict_conflict",
                "attempt_selected_metadata": (
                    "whole_window_verdict_conflict"
                ),
                "attempt_unselected_metadata": (
                    "whole_window_verdict_conflict"
                ),
                "primary": "bundle_sha256",
                "report": "floor_mint_postcollection",
                "custody": (
                    "v2 calibration ledger snapshot is not authenticated"
                ),
            }
            for label, evidence_path in domain_paths.items():
                with self.subTest(domain=label):
                    original_raw = evidence_path.read_bytes()
                    matrix_pinset = source_pinset
                    matrix_path = fixture.pinset_path
                    matrix_digest = fixture.pinset_sha256
                    matrix_manifest_path: Path | None = None
                    matrix_project_commit: str | None = None
                    if label in {"ledger", "attempt_ledger"}:
                        evidence_path.write_bytes(original_raw + b"{}\n")
                    elif label == "verdict":
                        rows = [
                            json.loads(line)
                            for line in original_raw.decode("utf-8").splitlines()
                        ]
                        verdict_row = next(
                            row for row in rows if "evaluation_basis" in row
                        )
                        verdict_row["evaluation_basis"]["sha256"] = "f" * 64
                        evidence_path.write_text(
                            "".join(
                                json.dumps(row, sort_keys=True, separators=(",", ":"))
                                + "\n"
                                for row in rows
                            ),
                            encoding="utf-8",
                        )
                    elif label in {"campaign", "primary", "custody"}:
                        evidence_path.write_bytes(original_raw + b"\n")
                    else:
                        value = json.loads(original_raw)
                        if label in {
                            "attempt_selected_metadata",
                            "attempt_unselected_metadata",
                        }:
                            value["run_id"] += "-attacked"
                        else:
                            value["floor_mint_postcollection"] = label
                        _write_fixture_json(evidence_path, value)
                        if label == "report":
                            matrix_pinset = copy.deepcopy(source_pinset)
                            for cell_pin in matrix_pinset["producer_plans"][0][
                                "cells"
                            ]:
                                cell_pin["postcollection"][
                                    "extraction_report_sha256"
                                ] = file_sha256(evidence_path)
                            _repair_v2_pinset_self_hashes(matrix_pinset)
                            matrix_path, matrix_digest = write_attack_pinset(
                                "domain-report", matrix_pinset
                            )
                        elif label == "acceptance":
                            matrix_manifest = copy.deepcopy(input_manifest)
                            matrix_manifest["calibration_acceptance"] = str(
                                evidence_path
                            )
                            matrix_manifest_path = (
                                fixture.inputs_root
                                / "domain-acceptance-input-manifest.json"
                            )
                            _write_fixture_json(
                                matrix_manifest_path, matrix_manifest
                            )
                        elif label == "head":
                            _run_fixture_command(
                                ["git", "add", str(evidence_path)],
                                cwd=fixture.repository,
                            )
                            _run_fixture_command(
                                [
                                    "git",
                                    "commit",
                                    "-q",
                                    "-m",
                                    "mutate committed head for domain test",
                                ],
                                cwd=fixture.repository,
                            )
                            matrix_project_commit = _run_fixture_command(
                                ["git", "rev-parse", "HEAD"],
                                cwd=fixture.repository,
                            ).stdout.strip()
                    try:
                        run_refusal(
                            f"domain-{label}",
                            domain_messages[label],
                            matrix_path,
                            matrix_digest,
                            matrix_manifest_path,
                            matrix_project_commit,
                        )
                    finally:
                        evidence_path.write_bytes(original_raw)
                        if label == "head":
                            _run_fixture_command(
                                ["git", "add", str(evidence_path)],
                                cwd=fixture.repository,
                            )
                            _run_fixture_command(
                                [
                                    "git",
                                    "commit",
                                    "-q",
                                    "-m",
                                    "restore committed head after domain test",
                                ],
                                cwd=fixture.repository,
                            )
                            fixture.project_commit = _run_fixture_command(
                                ["git", "rev-parse", "HEAD"],
                                cwd=fixture.repository,
                            ).stdout.strip()
            self.assertEqual(
                {str(path): file_sha256(path) for path in genuine_paths},
                genuine_inventory,
            )

            self.assertEqual(
                _run_fixture_command(
                    ["git", "status", "--porcelain"],
                    cwd=fixture.repository,
                ).stdout,
                "",
            )

    def test_verdict_bracket_refuses_repin_to_earlier_authentic_session(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pinset, inputs, original_snapshot = synthetic_v2_fixture()
            producer = pinset["producer_plans"][0]
            plan_id = producer["plan"]["plan_id"]
            original = inputs[plan_id]

            # The fixture's original finalized session becomes the authentic
            # earlier window.  Append a second finalized session for the same
            # plan/root, and make only that later session verdict-owned.
            later_binding, later_receipts, later_observations, later_session = (
                _synthetic_bracket_evidence(
                    2,
                    plan_id=plan_id,
                    plan_sha256=producer["plan"]["sha256"],
                    evidence_root_id=producer["evidence_root_id"],
                    runs_root=original.evidence_root,
                    sequence_start=len(original_snapshot.receipts) + 1,
                )
            )
            receipts = (*original_snapshot.receipts, *later_receipts)
            sessions = dict(original_snapshot.bracket_session_by_id)
            sessions[later_session.session_id] = later_session
            snapshot = SimpleNamespace(
                **{
                    **vars(original_snapshot),
                    "receipts": receipts,
                    "observations": (
                        *original_snapshot.observations,
                        *later_observations,
                    ),
                    "bracket_session_by_id": sessions,
                    "head_sequence": len(receipts),
                    "head_digest": later_observations[1].receipt_digest,
                }
            )
            later_verdict_bracket = _synthetic_verdict_bracket(
                later_observations
            )
            correct_cells = {
                role: generalized.V2CellComponents(
                    absolute=replace(
                        cell.absolute,
                        whole_window_calibration_bracket=later_verdict_bracket,
                    ),
                    comparative=replace(
                        cell.comparative,
                        whole_window_calibration_bracket=later_verdict_bracket,
                    ),
                    allowed_consumer_condition_families=(
                        cell.allowed_consumer_condition_families
                    ),
                )
                for role, cell in original.cells.items()
            }
            later_binding_sha256 = _fixture_artifact_sha256(later_binding)
            later_projection = {
                **generalized.issued_calibration_allowance_projection(
                    original.calibration_acceptance,
                    pre_exact_bound_lexeme_s=(
                        later_observations[0].exact_bound_lexeme_s
                    ),
                    post_exact_bound_lexeme_s=(
                        later_observations[1].exact_bound_lexeme_s
                    ),
                ),
                "allowance_rule": generalized.V2_ALLOWANCE_RULE,
            }
            correct = replace(
                original,
                cells=correct_cells,
                bracket_binding=later_binding,
                bracket_binding_sha256=later_binding_sha256,
                authenticated_pre_observation=later_observations[0],
                authenticated_post_observation=later_observations[1],
                calibration_allowance_projection=later_projection,
            )
            correct_inputs = {**inputs, plan_id: correct}
            for cell_pin in producer["cells"]:
                role_cell = correct_cells[cell_pin["role"]]
                cell_pin["postcollection"] = _v2_postcollection(
                    role_cell.absolute,
                    role_cell.comparative,
                    bracket_binding=later_binding,
                    bracket_binding_sha256=later_binding_sha256,
                    extraction_report_sha256=(
                        role_cell.absolute.report_sha256
                    ),
                )
            for producer_row in pinset["producer_plans"]:
                for cell_pin in producer_row["cells"]:
                    cell_pin["postcollection"][
                        "terminal_ledger_head_sha256"
                    ] = snapshot.head_digest
            for producer_row, aggregate_row, component_sha256 in zip(
                pinset["producer_plans"],
                pinset["aggregate"]["component_artifacts"],
                SYNTHETIC_COMPONENT_SHA256S,
            ):
                producer_row["component_artifact"]["sha256"] = component_sha256
                aggregate_row["sha256"] = component_sha256
            _repair_v2_pinset_self_hashes(pinset)
            correct_path, correct_digest = write_pinset(root, pinset)
            generalized.mint_multi_cell_authenticated_artifact(
                pinset_path=correct_path,
                pinset_sha256=correct_digest,
                producer_inputs=correct_inputs,
                calibration_ledger_snapshot=snapshot,
                project_commit="0" * 40,
                project_tree_state="clean",
            )

            # Coordinated attack: choose the earlier authentic binding and
            # repair its endpoint/drift/allowance/report pins and all pinset
            # self-hashes.  Ledger, acceptance, report, and verdict stay fixed.
            attacked_pinset = copy.deepcopy(pinset)
            attacked_producer = attacked_pinset["producer_plans"][0]
            earlier_binding = original.bracket_binding
            earlier_binding_sha256 = original.bracket_binding_sha256
            attacked = replace(
                correct,
                bracket_binding=earlier_binding,
                bracket_binding_sha256=earlier_binding_sha256,
                authenticated_pre_observation=(
                    original.authenticated_pre_observation
                ),
                authenticated_post_observation=(
                    original.authenticated_post_observation
                ),
                calibration_allowance_projection=(
                    original.calibration_allowance_projection
                ),
            )
            for cell_pin in attacked_producer["cells"]:
                role_cell = correct_cells[cell_pin["role"]]
                attacked_post = _v2_postcollection(
                    role_cell.absolute,
                    role_cell.comparative,
                    bracket_binding=earlier_binding,
                    bracket_binding_sha256=earlier_binding_sha256,
                    extraction_report_sha256=(
                        role_cell.absolute.report_sha256
                    ),
                )
                attacked_post["terminal_ledger_head_sha256"] = (
                    snapshot.head_digest
                )
                cell_pin["postcollection"] = attacked_post
            _repair_v2_pinset_self_hashes(attacked_pinset)
            attacked_path, attacked_digest = write_pinset(
                root, attacked_pinset
            )
            with self.assertRaisesRegex(
                generalized.MintError,
                "verdict/bracket cross-check refused binding session_id",
            ):
                generalized.mint_multi_cell_authenticated_artifact(
                    pinset_path=attacked_path,
                    pinset_sha256=attacked_digest,
                    producer_inputs={**correct_inputs, plan_id: attacked},
                    calibration_ledger_snapshot=snapshot,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )

    def test_per_component_consumption_semantics_pin_is_evidence_bound(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(root)
            )
            candidate = load_json(path)
            candidate["producer_plans"][0]["cells"][0]["absolute"][
                "consumption_semantics_id"
            ] = MINTED_CONSUMPTION_SEMANTICS_ID
            _repair_v2_pinset_self_hashes(candidate)
            candidate_path, candidate_digest = write_pinset(root, candidate)
            with self.assertRaisesRegex(
                generalized.MintError,
                "consumption semantics mismatch",
            ):
                generalized.mint_multi_cell_authenticated_artifact(
                    pinset_path=candidate_path,
                    pinset_sha256=candidate_digest,
                    producer_inputs=inputs,
                    calibration_ledger_snapshot=ledger_snapshot,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )

    def test_false_producer_inventory_pins_refuse_after_self_hash_repair(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(root)
            )
            source = load_json(path)
            cases = (
                (
                    "plan-sidecar",
                    lambda producer: producer["plan"].__setitem__(
                        "sidecar_sha256", "f" * 64
                    ),
                    "plan sidecar sha256 mismatch",
                ),
                (
                    "runtime",
                    lambda producer: producer["model_runtime_config"].__setitem__(
                        "runtime_identity_sha256", "f" * 64
                    ),
                    "runtime identity inventory mismatch",
                ),
                (
                    "acceptance",
                    lambda producer: producer["calibration_acceptance"].__setitem__(
                        "artifact_sha256", "f" * 64
                    ),
                    "calibration acceptance evidence mismatch",
                ),
            )
            for label, mutate, message in cases:
                with self.subTest(label=label):
                    candidate = copy.deepcopy(source)
                    mutate(candidate["producer_plans"][0])
                    _repair_v2_pinset_self_hashes(candidate)
                    candidate_path, candidate_digest = write_pinset(
                        root, candidate
                    )
                    with self.assertRaisesRegex(generalized.MintError, message):
                        generalized.mint_multi_cell_authenticated_artifact(
                            pinset_path=candidate_path,
                            pinset_sha256=candidate_digest,
                            producer_inputs=inputs,
                            calibration_ledger_snapshot=ledger_snapshot,
                            project_commit="0" * 40,
                            project_tree_state="clean",
                        )

    def test_v2_cli_requires_an_explicit_input_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, digest, _inputs, _snapshot = freeze_synthetic_v2_pinset(root)
            stderr = io.StringIO()
            with mock.patch("sys.stderr", stderr):
                exit_code = generalized.main(
                    [
                        "--pinset",
                        str(path),
                        "--pinset-sha256",
                        digest,
                        "--out",
                        str(root / "floor.json"),
                        "--single-count-out",
                        str(root / "single-count.txt"),
                        "--project-commit",
                        "0" * 40,
                        "--project-tree-state",
                        "clean",
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("requires --v2-input-manifest", stderr.getvalue())

    def test_production_cli_mints_and_names_every_custody_mismatch(self) -> None:
        self.enterContext(
            mock.patch.object(
                generalized,
                "_actual_v2_git_state",
                return_value=("0" * 40, True),
            )
        )
        self.enterContext(
            mock.patch.object(
                generalized,
                "_head_pin_commit_containment_in_origin_main",
                return_value=True,
            )
        )

        def validate_binding(binding, snapshot, **_kwargs):
            resolved = []
            for role in ("pre", "post"):
                receipt = binding["endpoints"][role]["receipt_digest"]
                resolved.append(
                    next(
                        observation
                        for observation in snapshot.observations
                        if observation.receipt_digest == receipt
                    )
                )
            return tuple(resolved)

        self.enterContext(
            mock.patch.object(
                generalized,
                "validate_calibration_bracket_binding",
                side_effect=validate_binding,
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pinset_path, pinset_sha256, manifest_path, load_test_core = (
                install_v2_cli_fixture(root)
            )
            source = load_json(pinset_path)

            def cli_args(label: str, path: Path, digest: str) -> list[str]:
                return [
                    "--pinset",
                    str(path),
                    "--pinset-sha256",
                    digest,
                    "--v2-input-manifest",
                    str(manifest_path),
                    "--out",
                    str(root / f"{label}-floor.json"),
                    "--single-count-out",
                    str(root / f"{label}-single-count.txt"),
                    "--project-commit",
                    "0" * 40,
                    "--project-tree-state",
                    "clean",
                ]

            with mock.patch.object(
                generalized,
                "_fresh_original_core",
                side_effect=load_test_core,
            ):
                self.assertEqual(
                    generalized.main(
                        cli_args("correct", pinset_path, pinset_sha256)
                    ),
                    0,
                )
            self.assertTrue((root / "correct-floor.json").is_file())
            self.assertTrue((root / "correct-single-count.txt").is_file())
            minted = load_json(root / "correct-floor.json")
            self.assertTrue(
                minted["provenance"]["implementation"][
                    "mint_commit_contained_in_origin_main"
                ]
            )
            self.assertTrue(
                minted["provenance"]["implementation"][
                    "head_pin_commit_contained_in_origin_main"
                ]
            )
            self.assertEqual(
                minted["provenance"]["assurance"],
                generalized.V2_ASSURANCE_PROFILE,
            )

            with (
                mock.patch.object(
                    generalized,
                    "_actual_v2_git_state",
                    return_value=("0" * 40, None),
                ),
                mock.patch.object(
                    generalized,
                    "_head_pin_commit_containment_in_origin_main",
                    return_value=None,
                ),
                mock.patch.object(
                    generalized,
                    "_fresh_original_core",
                    side_effect=load_test_core,
                ),
            ):
                self.assertEqual(
                    generalized.main(
                        cli_args(
                            "unknown-containment",
                            pinset_path,
                            pinset_sha256,
                        )
                    ),
                    0,
                )
            unknown_containment = load_json(
                root / "unknown-containment-floor.json"
            )
            self.assertIsNone(
                unknown_containment["provenance"]["implementation"][
                    "mint_commit_contained_in_origin_main"
                ]
            )
            self.assertIsNone(
                unknown_containment["provenance"]["implementation"][
                    "head_pin_commit_contained_in_origin_main"
                ]
            )

            mismatch_values = {
                "pre_receipt_sha256": "0" * 64,
                "pre_content_sha256": "0" * 64,
                "post_receipt_sha256": "0" * 64,
                "post_content_sha256": "0" * 64,
                "bracket_binding_sha256": "0" * 64,
                "terminal_ledger_head_sha256": "0" * 64,
                "extraction_report_sha256": "0" * 64,
                "observed_drift_s": "0.002000",
                # Decimal-equivalent spelling preserves the never-zero rule
                # while still testing exact report-string authentication.
                "applied_allowance_s": "0.0108180",
            }
            for field, replacement in mismatch_values.items():
                with self.subTest(field=field):
                    candidate = copy.deepcopy(source)
                    for cell in candidate["producer_plans"][0]["cells"]:
                        cell["postcollection"][field] = replacement
                    _repair_v2_pinset_self_hashes(candidate)
                    candidate_path, candidate_digest = write_pinset(
                        root, candidate
                    )
                    stderr = io.StringIO()
                    with (
                        mock.patch.object(
                            generalized,
                            "_fresh_original_core",
                            side_effect=load_test_core,
                        ),
                        mock.patch("sys.stderr", stderr),
                    ):
                        exit_code = generalized.main(
                            cli_args(field, candidate_path, candidate_digest)
                        )
                    self.assertEqual(exit_code, 2)
                    self.assertIn(field, stderr.getvalue())
                    self.assertFalse((root / f"{field}-floor.json").exists())
                    self.assertFalse(
                        (root / f"{field}-single-count.txt").exists()
                    )

    def test_v2_input_manifest_routes_all_authenticated_evidence_files(
        self,
    ) -> None:
        pinset, source_inputs, ledger_snapshot = synthetic_v2_fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            acceptance = next(iter(source_inputs.values())).calibration_acceptance
            acceptance_path = root / "acceptance.json"
            acceptance_path.write_text(
                json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            acceptance_sha256 = file_sha256(acceptance_path)
            ledger_path = root / "ledger.jsonl"
            ledger_path.write_text("{}\n", encoding="utf-8")
            head_path = root / "ledger.head.json"
            head_path.write_text("{}\n", encoding="utf-8")
            component_by_cell_id = {}
            verdict_bracket_by_cell_id = {}
            expected_report_text = {}
            manifest_producers = []
            for producer, component_sha256 in zip(
                pinset["producer_plans"], SYNTHETIC_COMPONENT_SHA256S
            ):
                producer["component_artifact"]["sha256"] = component_sha256
                plan_id = producer["plan"]["plan_id"]
                source = source_inputs[plan_id]
                plan_path = root / f"{plan_id}.json"
                plan_path.write_text(
                    json.dumps(source.plan, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                plan_sha256 = file_sha256(plan_path)
                declared_sha256 = plan_sha256
                sidecar_path = root / f"{plan_id}.sha256"
                sidecar_path.write_text(
                    f"{declared_sha256}  {plan_path.name}\n",
                    encoding="utf-8",
                )
                producer["plan"].update(
                    {
                        "sha256": plan_sha256,
                        "declared_sha256": declared_sha256,
                        "sidecar_sha256": file_sha256(sidecar_path),
                    }
                )
                producer["calibration_acceptance"][
                    "artifact_sha256"
                ] = acceptance_sha256
                binding = copy.deepcopy(source.bracket_binding)
                binding["plan_sha256"] = plan_sha256
                producer_evidence_root = root / f"{plan_id}-root"
                producer_evidence_root.mkdir()
                campaign_path = producer_evidence_root / "campaign_log.jsonl"
                campaign_path.write_text("{}\n", encoding="utf-8")
                binding["runs_root"] = str(
                    producer_evidence_root.resolve(strict=False)
                )
                binding["binding_digest"] = _fixture_canonical_sha256(
                    {
                        key: value
                        for key, value in binding.items()
                        if key != "binding_digest"
                    }
                )
                binding_path = root / f"{plan_id}.binding.json"
                binding_path.write_text(
                    json.dumps(binding, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                binding_sha256 = file_sha256(binding_path)
                manifest_cells = []
                for cell_pin in producer["cells"]:
                    role = cell_pin["role"]
                    source_cell = source.cells[role]
                    component_rows = {}
                    for component_name, component in (
                        ("absolute", source_cell.absolute),
                        ("comparative", source_cell.comparative),
                    ):
                        label = f"{plan_id}-{role}-{component_name}"
                        paths = {
                            "evidence_root": str(producer_evidence_root),
                            "report": str(root / f"{label}-report.json"),
                            "spec": str(root / f"{label}-spec.json"),
                            "order_manifest": str(root / f"{label}-order.json"),
                        }
                        for field in ("report", "spec", "order_manifest"):
                            value = {
                                "report": component.report,
                                "spec": component.spec,
                                "order_manifest": component.order_manifest,
                            }[field]
                            Path(paths[field]).write_text(
                                json.dumps(value, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8",
                            )
                        component_rows[component_name] = paths
                        source_key = (
                            component.calibration_cell_id,
                            str(producer_evidence_root.resolve()),
                        )
                        component_by_cell_id[source_key] = component
                        verdict_bracket = copy.deepcopy(
                            component.whole_window_calibration_bracket
                        )
                        for endpoint in verdict_bracket.values():
                            endpoint["bracket_plan_sha256"] = plan_sha256
                            endpoint["bracket_runs_root"] = str(
                                producer_evidence_root.resolve()
                            )
                        verdict_bracket_by_cell_id[source_key] = (
                            verdict_bracket
                        )
                        expected_report_text[source_key] = Path(
                            paths["report"]
                        ).read_text(encoding="utf-8")
                    cell_pin["postcollection"][
                        "bracket_binding_sha256"
                    ] = binding_sha256
                    manifest_cells.append(
                        {
                            "role": role,
                            **component_rows,
                            "allowed_consumer_condition_families": list(
                                source_cell.allowed_consumer_condition_families
                            ),
                        }
                    )
                manifest_producers.append(
                    {
                        "plan_id": plan_id,
                        "calibration_plan": str(plan_path),
                        "calibration_plan_sidecar": str(sidecar_path),
                        "bracket_binding": str(binding_path),
                        "cells": manifest_cells,
                    }
                )
            for entry, component_sha256 in zip(
                pinset["aggregate"]["component_artifacts"],
                SYNTHETIC_COMPONENT_SHA256S,
            ):
                entry["sha256"] = component_sha256
            _repair_v2_pinset_self_hashes(pinset)
            pinset_path, pinset_sha256 = write_pinset(root, pinset)
            loaded = generalized.load_pinset(pinset_path, pinset_sha256)
            manifest = {
                "schema_version": "joulewise.floor_mint_inputs.v2",
                "calibration_acceptance": str(acceptance_path),
                "calibration_ledger": str(ledger_path),
                "calibration_ledger_head_pin": str(head_path),
                "producer_plans": manifest_producers,
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            evidence_core = SimpleNamespace(
                load_calibration_acceptance_bound=mock.Mock(
                    return_value=acceptance
                ),
                load_calibration_ledger_snapshot=mock.Mock(
                    return_value=ledger_snapshot
                ),
            )

            def authenticate(paths, **kwargs):
                source_key = (
                    paths.calibration_cell_id,
                    str(paths.evidence_root.resolve()),
                )
                expected = component_by_cell_id[source_key]
                self.assertEqual(
                    paths.report_path.read_text(encoding="utf-8"),
                    expected_report_text[source_key],
                )
                self.assertEqual(
                    kwargs["expected_consumption_semantics_id"],
                    expected.consumption_semantics_id,
                )
                self.assertIs(
                    kwargs["calibration_ledger_snapshot"], ledger_snapshot
                )
                return replace(
                    expected,
                    report_sha256=file_sha256(paths.report_path),
                    spec_sha256=file_sha256(paths.spec_path),
                    order_manifest_sha256=file_sha256(
                        paths.order_manifest_path
                    ),
                    campaign_log_sha256=file_sha256(
                        paths.evidence_root / "campaign_log.jsonl"
                    ),
                    whole_window_calibration_bracket=(
                        verdict_bracket_by_cell_id[source_key]
                    ),
                )

            component_core = SimpleNamespace(
                MintError=mint1.MintError,
                ComponentPaths=mint1.ComponentPaths,
                _authenticate_component=mock.Mock(side_effect=authenticate),
            )
            with (
                mock.patch.object(
                    generalized,
                    "_fresh_original_core",
                    return_value=evidence_core,
                ),
                mock.patch.object(
                    generalized,
                    "_configured_core",
                    return_value=component_core,
                ),
                mock.patch.object(
                    generalized,
                    "_v2_spec_member_ids",
                    return_value=(),
                ),
                mock.patch.object(
                    generalized,
                    "validate_calibration_bracket_binding",
                    side_effect=lambda binding, snapshot, **_kwargs: tuple(
                        next(
                            observation
                            for observation in snapshot.observations
                            if observation.receipt_digest
                            == binding["endpoints"][role]["receipt_digest"]
                        )
                        for role in ("pre", "post")
                    ),
                ),
            ):
                authenticated, roots, observed_snapshot = (
                    generalized._authenticate_v2_inputs(
                        pinset=loaded,
                        pinset_path=pinset_path,
                        pinset_sha256=pinset_sha256,
                        input_manifest_path=manifest_path,
                        strict_validator=lambda _path, _strict: [],
                        consumption_semantics_id=None,
                    )
                )
        self.assertEqual(set(authenticated), set(source_inputs))
        self.assertEqual(len(roots), 2)
        self.assertIs(observed_snapshot, ledger_snapshot)
        self.assertEqual(component_core._authenticate_component.call_count, 8)
        evidence_core.load_calibration_acceptance_bound.assert_called_once_with(
            acceptance_path
        )
        evidence_core.load_calibration_ledger_snapshot.assert_called_once()

    def test_missing_unresolved_and_derived_literal_attempts_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, _inputs, _snapshot = freeze_synthetic_v2_pinset(root)
            source = load_json(path)
            cases = {}
            missing = copy.deepcopy(source)
            del missing["producer_plans"][0]["cells"][0]["postcollection"][
                "pre_receipt_sha256"
            ]
            cases["missing"] = (missing, "schema mismatch")
            unresolved = copy.deepcopy(source)
            unresolved["producer_plans"][0]["cells"][0]["postcollection"] = {
                "status": "unresolved"
            }
            cases["unresolved"] = (unresolved, "schema mismatch")
            derived = copy.deepcopy(source)
            derived["producer_plans"][0]["cells"][0]["postcollection"][
                "operative_floor_six_decimal"
            ] = {"derive_from": "component_max"}
            cases["derived"] = (derived, "six-decimal literal")
            for label, (candidate, message) in cases.items():
                with self.subTest(label=label):
                    candidate_path, candidate_digest = write_pinset(
                        root, candidate
                    )
                    with self.assertRaisesRegex(generalized.MintError, message):
                        generalized.load_pinset(
                            candidate_path, candidate_digest
                        )

    def test_sum_allowance_and_metric_refusal_vectors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, _inputs, _snapshot = freeze_synthetic_v2_pinset(root)
            source = load_json(path)
            cases = {}
            summed = copy.deepcopy(source)
            post = summed["producer_plans"][0]["cells"][0][
                "postcollection"
            ]
            post["operative_floor_full_precision"] = "20.292416850449352"
            post["operative_floor_six_decimal"] = "20.292417"
            cases["sum"] = (summed, "maximum, never a sum")
            omitted = copy.deepcopy(source)
            del omitted["producer_plans"][0]["cells"][0]["postcollection"][
                "allowance_embedding_count"
            ]
            cases["allowance-omitted"] = (omitted, "schema mismatch")
            twice = copy.deepcopy(source)
            twice["producer_plans"][0]["cells"][0]["postcollection"][
                "allowance_embedding_count"
            ] = 2
            cases["allowance-twice"] = (twice, "once per cell")
            truthy = copy.deepcopy(source)
            truthy["producer_plans"][0]["cells"][0]["postcollection"][
                "allowance_embedding_count"
            ] = True
            cases["allowance-boolean"] = (truthy, "once per cell")
            wrong_metric = copy.deepcopy(source)
            wrong_metric["producer_plans"][0]["cells"][0]["metric"] = (
                "phase_energy_j.prefill"
            )
            cases["wrong-metric"] = (wrong_metric, "metric must equal")
            wrong_precheck = copy.deepcopy(source)
            wrong_precheck["producer_plans"][0]["cells"][0][
                "target_precheck_path"
            ] = ["phase", "prefill"]
            cases["wrong-precheck"] = (
                wrong_precheck,
                "target_precheck_path must equal",
            )
            for label, (candidate, message) in cases.items():
                with self.subTest(label=label):
                    candidate_path, candidate_digest = write_pinset(
                        root, candidate
                    )
                    with self.assertRaisesRegex(generalized.MintError, message):
                        generalized.load_pinset(
                            candidate_path, candidate_digest
                        )

    def test_v2_decimal_pins_require_plain_unsigned_strings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, _inputs, _snapshot = freeze_synthetic_v2_pinset(root)
            source = load_json(path)
            for label, observed, applied in (
                ("negative-zero", "-0", generalized.V2_BRACKET_SCREEN_S),
                ("exponent", "0", "1.0818E-2"),
                ("leading-plus", "+0", generalized.V2_BRACKET_SCREEN_S),
            ):
                with self.subTest(label=label):
                    candidate = copy.deepcopy(source)
                    post = candidate["producer_plans"][0]["cells"][0][
                        "postcollection"
                    ]
                    post["observed_drift_s"] = observed
                    post["applied_allowance_s"] = applied
                    candidate_path, candidate_digest = write_pinset(
                        root, candidate
                    )
                    with self.assertRaisesRegex(
                        generalized.MintError,
                        "plain unsigned decimal string",
                    ):
                        generalized.load_pinset(
                            candidate_path, candidate_digest
                        )

    def test_retired_literal_refuses_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, _inputs, _snapshot = freeze_synthetic_v2_pinset(root)
            candidate = load_json(path)
            candidate["producer_plans"][0]["cells"][0]["postcollection"][
                "operative_floor_six_decimal"
            ] = generalized.RETIRED_OPERATIVE_FLOOR_LITERAL
            candidate_path, candidate_digest = write_pinset(root, candidate)
            with self.assertRaisesRegex(
                generalized.MintError, "reuses retired literal 7.377086"
            ):
                generalized.load_pinset(candidate_path, candidate_digest)

    def test_aggregate_and_component_hash_mismatches_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(root)
            )
            source = load_json(path)
            aggregate_bad = copy.deepcopy(source)
            aggregate_bad["aggregate"]["producer_set_sha256"] = "f" * 64
            aggregate_path, aggregate_digest = write_pinset(root, aggregate_bad)
            with self.assertRaisesRegex(
                generalized.MintError, "aggregate hash mismatch"
            ):
                generalized.mint_multi_cell_authenticated_artifact(
                    pinset_path=aggregate_path,
                    pinset_sha256=aggregate_digest,
                    producer_inputs=inputs,
                    calibration_ledger_snapshot=ledger_snapshot,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )

            allowlist_bad = copy.deepcopy(source)
            allowlist_bad["aggregate"]["transport_allowlists"][0][
                "allowed_consumer_condition_families"
            ] = [
                {
                    "condition_family_id": "aggregate-only-family",
                    "condition_family_sha256": "f" * 64,
                }
            ]
            allowlist_path, allowlist_digest = write_pinset(
                root, allowlist_bad
            )
            with self.assertRaisesRegex(
                generalized.MintError,
                "contradicts the component cell allowlist",
            ):
                generalized.mint_multi_cell_authenticated_artifact(
                    pinset_path=allowlist_path,
                    pinset_sha256=allowlist_digest,
                    producer_inputs=inputs,
                    calibration_ledger_snapshot=ledger_snapshot,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )

            component_bad = copy.deepcopy(source)
            replacement = "f" * 64
            component_bad["producer_plans"][0]["component_artifact"][
                "sha256"
            ] = replacement
            component_bad["aggregate"]["component_artifacts"][0][
                "sha256"
            ] = replacement
            _repair_v2_pinset_self_hashes(component_bad)
            component_path, component_digest = write_pinset(
                root, component_bad
            )
            with self.assertRaisesRegex(
                generalized.MintError, "component artifact 0"
            ):
                generalized.mint_multi_cell_authenticated_artifact(
                    pinset_path=component_path,
                    pinset_sha256=component_digest,
                    producer_inputs=inputs,
                    calibration_ledger_snapshot=ledger_snapshot,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )

    def test_shared_v2_projection_rejects_nested_extra_fields(self) -> None:
        candidate, _inputs, _snapshot = synthetic_v2_fixture()
        for producer, component_sha256 in zip(
            candidate["producer_plans"], SYNTHETIC_COMPONENT_SHA256S
        ):
            producer["component_artifact"]["sha256"] = component_sha256
        for entry, component_sha256 in zip(
            candidate["aggregate"]["component_artifacts"],
            SYNTHETIC_COMPONENT_SHA256S,
        ):
            entry["sha256"] = component_sha256
        candidate["producer_plans"][0]["plan"][
            "silently_ignored_extra"
        ] = True
        _repair_v2_pinset_self_hashes(candidate)
        self.assertIsNone(
            detection_floor._project_floor_mint_pinset_v2(candidate)
        )

    def test_malformed_v2_producer_provenance_returns_errors_not_crash(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, digest, inputs, ledger_snapshot = (
                freeze_synthetic_v2_pinset(Path(tmp))
            )
            artifact = generalized.mint_multi_cell_authenticated_artifact(
                pinset_path=path,
                pinset_sha256=digest,
                producer_inputs=inputs,
                calibration_ledger_snapshot=ledger_snapshot,
                project_commit="0" * 40,
                project_tree_state="clean",
            )
            malformed = copy.deepcopy(artifact)
            malformed["provenance"]["producer_calibration_plans"][0][
                "plan_id"
            ] = []
            errors = detection_floor.validate_floor_artifact(
                malformed,
                pinset_path=path,
                expected_pinset_sha256=digest,
            )
        self.assertTrue(any("plan_id" in error for error in errors), errors)


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
