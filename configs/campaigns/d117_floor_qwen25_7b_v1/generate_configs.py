#!/usr/bin/env python3
"""Generate the D-117 Qwen2.5-7B floor campaign draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
PACK_REL = Path("configs/campaigns/d117_floor_qwen25_7b_v1")
SPEC_REL = Path("configs/floor_mint/d117_qwen25_7b_extraction_spec.json")
SOURCE_GENERATOR = Path(__file__).resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.detection_floor import (  # noqa: E402
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
)
from joulewise.floor_extraction import (  # noqa: E402
    validate_condition_family_definition,
    validate_extraction_spec,
)


N = 10
PLAN_ID = "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen25-7b-v1"
CLAIM_ROOT_LEAF = "runs_d117_floor_qwen25_7b_v1"
BOUND_ROOT_LEAF = "runs_d117_floor_qwen25_7b_v1_bound"
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
PLAN_TREE_SCHEMA = "joulewise.d117_plan_tree.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
FAMILY_SCHEMA = "joulewise.condition_family_definition.v1"
MODEL_TAG = "qwen25-7b-mlx"
DECODE_FAMILY_ID = "df-ph-decode-qwen25-7b"
PREFILL_FAMILY_ID = "df-ph-prefill-p128-qwen25-7b"
CAMPAIGN_TAG = "d117-floor-qwen25-7b-v1"
TODO_BRANCH = "impl/d117-ledger-recovery"
D124_ESTIMATOR_ID = "d124_two_shared_edge_common_mode.v1"
D124_ASSUMPTION_ID = "d124_block_bracket_edges_shared_within_abba.v1"
IDENTITY_PROJECTION_WORK_ORDER = "D117-U11-IDPIN-PROJECTION"

PLAN_SET_ID = "plan-set-d117-qwen25-1p5b-7b-phase-floor-v1"
AGGREGATE_ARTIFACT_ID = "d117-qwen25-phase-floor-set-v1"
COMPONENT_ARTIFACT_ID = "d117-qwen25-7b-phase-floor-component-v1"

DECODE_ARTIFACT_CELL_ID = "d117-qwen25-7b-decode-floor-v1"
PREFILL_ARTIFACT_CELL_ID = "d117-qwen25-7b-prefill-p128-floor-v1"
DECODE_TRANSPORT_ID = "tg-d117-qwen25-7b-decode-v1"
PREFILL_TRANSPORT_ID = "tg-d117-qwen25-7b-prefill-p128-v1"

DECODE_ABSOLUTE_CELL = "d117-df-ph-decode-qwen25-7b-absolute"
DECODE_COMPARATIVE_CELL = "d117-df-cmp-abba-ph-decode-qwen25-7b"
PREFILL_ABSOLUTE_CELL = "d117-df-ph-prefill-p128-qwen25-7b-absolute"
PREFILL_COMPARATIVE_CELL = (
    "d117-df-cmp-abba-ph-prefill-p128-qwen25-7b"
)

MODEL = {
    "name": "Qwen2.5-7B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
    "revision": "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
    "weight_format": "mlx",
    "context_window": 32768,
}
REFERENCE_MODEL = {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
}
QUANTIZATION = {"name": "int4", "bits": 4}
HARDWARE = {
    "id": "macbook_m3_max",
    "transport": "local",
    "runtime_backend": "mlx",
    "telemetry_backend": "powermetrics",
    "device_kind": "apple_silicon_unified_memory",
    "notes": (
        "D-117 beta Qwen2.5-7B phase-floor campaign on the current "
        "M3 Max; normal powermetrics sampler set only."
    ),
}
WORKLOAD = {
    "name": "df_ph_decode",
    "repetitions": 1,
    "warmup_runs": 1,
    "prompt_tokens": 128,
    "output_tokens": 512,
}
SAMPLING = {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0}

STAGES = (
    {
        "subcampaign_id": "01_phase_decode_absolute",
        "role": "absolute_phase_decode",
        "ordering_note": "Ten fixed absolute decode repeats in repetition order.",
    },
    {
        "subcampaign_id": "02_phase_decode_abba_blocks_01_05",
        "role": "comparative_phase_decode_first_half",
        "ordering_note": (
            "Fixed contiguous same-condition A/B/B/A decode blocks 1-5."
        ),
    },
    {
        "subcampaign_id": "03_phase_decode_abba_blocks_06_10",
        "role": "comparative_phase_decode_second_half",
        "ordering_note": (
            "Fixed contiguous same-condition A/B/B/A decode blocks 6-10."
        ),
    },
)

POLICY_REL = Path("configs/campaign_policies/quiet_mac_p2_production.json")
ACCEPTANCE_REL = Path("configs/calibration/calibration_acceptance_d079_v2.json")
LEDGER_HEAD_REL = Path("configs/calibration/calibration_ledger_head.json")
NEG8_MANIFEST_REL = Path("configs/campaigns/neg8_reference_corpus/order_manifest.json")
NEG8_CORPUS_REL = Path(
    "configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json"
)
START_MANIFEST_REL = Path(
    "configs/campaigns/window_references/start_triplet/order_manifest.json"
)
MID_MANIFEST_REL = Path(
    "configs/campaigns/window_references/midpoint/order_manifest.json"
)
END_MANIFEST_REL = Path(
    "configs/campaigns/window_references/end_triplet/order_manifest.json"
)
DECODE_TEMPLATE_REL = Path(
    "configs/campaigns/qwen25_7b_decode_floor_v1/condition_families/"
    "condition_family_df_ph_decode_qwen25_7b.json"
)

EXPECTED_EXTERNAL_SHA256 = {
    POLICY_REL.as_posix(): "b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd",
    ACCEPTANCE_REL.as_posix(): "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
    LEDGER_HEAD_REL.as_posix(): "6bbe26258165bbd11ca996324a5862c2e6e34faae7999b6c06f5e12f27ac2902",
    NEG8_MANIFEST_REL.as_posix(): "0ec9d68aa4265cc9378bb682091a973fc92879b76506fa25af828050a608509f",
    NEG8_CORPUS_REL.as_posix(): "74ccdaec74497c3aa7c074ef1129ec2bf2cc01d8ac14d3d07be77ab468599688",
    START_MANIFEST_REL.as_posix(): "9cac197255bdc9a0a1a0b8ee8ceb587ba3c8cabc20b976b2543dc3a400d37cb0",
    MID_MANIFEST_REL.as_posix(): "9ccedd91307985ba5641e791f4ac89f4e250fca414a4ba713cc7977ced6abb21",
    END_MANIFEST_REL.as_posix(): "8e65a4347aafa0722a60a2bd58c7e8061b860db66fa06f6acec24d1a1ade5c67",
    DECODE_TEMPLATE_REL.as_posix(): "d90b8fec2ccc74f1e982e573789a32116cda78d625ce84e72f2717926edc0cdb",
}

EXPECTED_DECODE_DOMAIN_SHA256 = (
    "a20018d57f06d69ffcc14e1e9365ab0121b73804ec480f9b08302384bd583843"
)
EXPECTED_PREFILL_FILE_SHA256 = (
    "e896aeae5eff911dbe14d09de9ebddcafe37b20c67ba059b2a6b7f6d3a6cee25"
)
EXPECTED_PREFILL_DOMAIN_SHA256 = (
    "b95688675b5518ab6675b8688ce4475b0d756653ecfb10ec80fa913ee49d69f1"
)


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sidecar_bytes(digest: str, filename: str) -> bytes:
    return f"{digest}  {filename}\n".encode("utf-8")


def verify_external_inputs() -> None:
    for relative, expected in EXPECTED_EXTERNAL_SHA256.items():
        observed = sha256_file(REPO_ROOT / relative)
        if observed != expected:
            raise ValueError(
                f"external input drift for {relative}: {observed} != {expected}"
            )


def condition_families() -> tuple[dict[str, Any], dict[str, Any], str, str]:
    decode_raw = (REPO_ROOT / DECODE_TEMPLATE_REL).read_bytes()
    decode = json.loads(decode_raw)
    prefill = {
        "schema_version": FAMILY_SCHEMA,
        "condition_family_id": PREFILL_FAMILY_ID,
        "workload_profile": {
            "name": "df_ph_decode",
            "prompt_tokens": 128,
            "output_tokens": 512,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "measurement_target": {
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }
    for name, value in (("decode", decode), ("prefill", prefill)):
        errors = validate_condition_family_definition(value)
        if errors:
            raise ValueError(f"{name} family invalid: {'; '.join(errors)}")
    decode_domain = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, decode)
    prefill_domain = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, prefill)
    if decode_domain != EXPECTED_DECODE_DOMAIN_SHA256:
        raise ValueError("D-085 decode condition-family domain changed")
    if sha256_bytes(render_json(prefill)) != EXPECTED_PREFILL_FILE_SHA256:
        raise ValueError("prefill-rider bytes changed")
    if prefill_domain != EXPECTED_PREFILL_DOMAIN_SHA256:
        raise ValueError("prefill-rider condition-family domain changed")
    return decode, prefill, decode_domain, prefill_domain


def build_science() -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    stages = [{**stage, "runs": []} for stage in STAGES]
    absolute_ids: list[str] = []
    for rep in range(1, N + 1):
        run_id = f"d117f7-df-ph-decode-abs-r{rep:02d}"
        stages[0]["runs"].append(
            {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": rep,
                "role": "absolute_repeat",
                "block_index": rep,
                "position_in_block": 1,
                "position": None,
                "label": None,
                "collection_tags": [f"rep{rep}"],
            }
        )
        absolute_ids.append(run_id)

    blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        block_id = f"d117-df-cmp-abba-ph-decode-qwen25-7b-b{block:02d}"
        members: list[dict[str, Any]] = []
        for sequence_index, (label, position) in enumerate(
            (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2")),
            start=1,
        ):
            run_id = (
                f"d117f7-df-cmp-abba-ph-decode-b{block:02d}-"
                f"{position.lower()}"
            )
            run = {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": block,
                "role": "comparative_abba_member",
                "block_index": block,
                "position_in_block": sequence_index,
                "position": position,
                "label": label,
                "collection_tags": [
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={label}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            }
            stages[1 if block <= 5 else 2]["runs"].append(run)
            members.append(
                {
                    "position": position,
                    "plan_label": label,
                    "plan_sequence_index": sequence_index,
                    "bundle_id": run_id,
                }
            )
        blocks.append(
            {
                "block_id": block_id,
                "executed_labels": ["A", "B", "B", "A"],
                "members": members,
            }
        )
    return stages, absolute_ids, blocks


def config_for(run: Mapping[str, Any], plan_sha256: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "run_id": run["run_id"],
        "model": MODEL,
        "quantization": QUANTIZATION,
        "hardware_target": HARDWARE,
        "workload_profile": WORKLOAD,
        "interconnect": {"name": "local"},
        "sampling": SAMPLING,
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": [
                "phase2",
                "splitwise-decode-floor-v1",
                CAMPAIGN_TAG,
                "production-window",
                "floor-calibration",
                f"df-condition={DECODE_FAMILY_ID}",
                f"calibration-plan-sha256={plan_sha256}",
                *run["collection_tags"],
            ],
        },
    }


def manifest_entry(
    run: Mapping[str, Any], index: int, config_path: str, config_sha256: str
) -> dict[str, Any]:
    block_id = (
        f"d117-df-cmp-abba-ph-decode-qwen25-7b-b{run['block_index']:02d}"
        if run["role"] == "comparative_abba_member"
        else None
    )
    return {
        "index": index,
        "config": config_path,
        "config_sha256": config_sha256,
        "run_id": run["run_id"],
        "model_tag": MODEL_TAG,
        "rep": run["rep"],
        "workload": DECODE_FAMILY_ID,
        "role": run["role"],
        "block_id": block_id,
        "block_index": run["block_index"],
        "position": run["position"],
        "position_in_block": run["position_in_block"],
        "arm": run["label"],
    }


def family_binding(
    definition: Mapping[str, Any], domain_sha256: str
) -> dict[str, Any]:
    return {
        "condition_family_id": definition["condition_family_id"],
        "condition_family_definition": definition,
        "condition_family_sha256": domain_sha256,
    }


def calibration_basis() -> dict[str, Any]:
    return {
        "calibration_scope": "production_window",
        "acceptance_selection": (
            "issued_or_authenticated_d102_descendant_before_member_1"
        ),
        "issued_acceptance": {
            "path": ACCEPTANCE_REL.as_posix(),
            "acceptance_id": "d079_calibration_acceptance_v2_n19",
            "artifact_sha256": EXPECTED_EXTERNAL_SHA256[ACCEPTANCE_REL.as_posix()],
            "derivation_sha256": (
                "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
            ),
            "schema_version": "joulewise.calibration_acceptance_bound.v2",
        },
        "allowance_rule": "max(observed_drift_s,0.010818)",
        "allowance_embedding_count": 1,
        "component_composition": "componentwise_max_never_sum.v1",
    }


def common_mode_registration() -> dict[str, Any]:
    return {
        "estimator_id": D124_ESTIMATOR_ID,
        "status": "candidate_pending_implementation_identity_confirmation",
        "transfer_assumption": {
            "assumption_id": D124_ASSUMPTION_ID,
            "statement": (
                "Within an ABBA block governed by one calibration bracket, onset "
                "and offset fiducial terms are shared edges; bundle-specific "
                "residual terms remain adversarial."
            ),
            "evidence": [
                (
                    "docs/process_traces/2026-08-08-attribution-debate/"
                    "COMMONMODE-REPLAY.md"
                ),
                "docs/decision_log.md#d-124",
            ],
            "limitation": (
                "Historical evidence records uncertainty bounds, not realized "
                "member-level timing errors."
            ),
        },
        "covariance_treatment": (
            "two_shared_edges_plus_bundle_specific_adversarial_terms"
        ),
        "never_zero_allowance_application_count": 1,
    }


def extraction_spec(
    *,
    decode: Mapping[str, Any],
    prefill: Mapping[str, Any],
    decode_domain: str,
    prefill_domain: str,
    absolute_rows: Sequence[Mapping[str, Any]],
    comparative_rows: Sequence[Mapping[str, Any]],
    root_manifest_id: str,
    root_manifest_sha256: str,
) -> dict[str, Any]:
    root_pin = {
        "path": f"{PACK_REL.as_posix()}/order_manifest.json",
        "manifest_id": root_manifest_id,
        "sha256": root_manifest_sha256,
    }
    def member_hashes(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
        return [
            {
                "bundle_id": row["run_id"],
                "config_sha256": row["config_sha256"],
            }
            for row in rows
        ]

    comparative_blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        selected = [row for row in comparative_rows if row["block_index"] == block]
        comparative_blocks.append(
            {
                "block_id": (
                    f"d117-df-cmp-abba-ph-decode-qwen25-7b-b{block:02d}"
                ),
                "members": {
                    position: next(
                        row["run_id"]
                        for row in selected
                        if row["position"] == position
                    )
                    for position in ("A1", "B1", "B2", "A2")
                },
            }
        )

    def absolute_cell(
        cell_id: str,
        metric: str,
        precheck: list[str],
        definition: Mapping[str, Any],
        domain_sha: str,
    ) -> dict[str, Any]:
        return {
            "cell_id": cell_id,
            "kind": "absolute",
            "metric": metric,
            "window_class": "phase",
            "target_precheck_path": precheck,
            "condition_family_id": definition["condition_family_id"],
            "condition_family_definitions": {
                "all": family_binding(definition, domain_sha)
            },
            "expected_n": N,
            "estimator": "d054_false_effect_guard.v1",
            "order_manifest": root_pin,
            "evidence_root_id": EVIDENCE_ROOT_ID,
            "member_config_sha256": member_hashes(absolute_rows),
            "calibration_basis": calibration_basis(),
            "members": [
                {"slot": row["run_id"], "bundle_id": row["run_id"]}
                for row in absolute_rows
            ],
        }

    def comparative_cell(
        cell_id: str,
        metric: str,
        precheck: list[str],
        definition: Mapping[str, Any],
        domain_sha: str,
    ) -> dict[str, Any]:
        family = family_binding(definition, domain_sha)
        return {
            "cell_id": cell_id,
            "kind": "comparative",
            "metric": metric,
            "window_class": "phase",
            "target_precheck_path": precheck,
            "condition_family_id": definition["condition_family_id"],
            "condition_family_definitions": {"A": family, "B": dict(family)},
            "expected_n": N,
            "estimator": D124_ESTIMATOR_ID,
            "estimator_registration": common_mode_registration(),
            "order_manifest": root_pin,
            "evidence_root_id": EVIDENCE_ROOT_ID,
            "member_config_sha256": member_hashes(comparative_rows),
            "calibration_basis": calibration_basis(),
            "blocks": comparative_blocks,
        }

    cells = [
        absolute_cell(
            DECODE_ABSOLUTE_CELL,
            "phase_energy_j.decode",
            ["phase", "decode"],
            decode,
            decode_domain,
        ),
        comparative_cell(
            DECODE_COMPARATIVE_CELL,
            "phase_energy_j.decode",
            ["phase", "decode"],
            decode,
            decode_domain,
        ),
        absolute_cell(
            PREFILL_ABSOLUTE_CELL,
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            prefill,
            prefill_domain,
        ),
        comparative_cell(
            PREFILL_COMPARATIVE_CELL,
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            prefill,
            prefill_domain,
        ),
    ]
    all_rows = [*absolute_rows, *comparative_rows]
    reported_members = [
        {
            "ordinal": index,
            "bundle_id": row["run_id"],
            "config_sha256": row["config_sha256"],
        }
        for index, row in enumerate(all_rows, start=1)
    ]
    reported_cells = [
        {
            "cell_id": "d117-reported-mean-ph-decode-qwen25-7b",
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
            "target_precheck_path": ["phase", "decode"],
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "expected_n": 50,
            "members": reported_members,
            "missing_or_invalid_member": "refuse_reported_mean",
            "numeric_value": None,
        },
        {
            "cell_id": "d117-reported-mean-ph-prefill-p128-qwen25-7b",
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
            "target_precheck_path": ["phase", "prefill"],
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "expected_n": 50,
            "members": reported_members,
            "missing_or_invalid_member": "refuse_reported_mean",
            "numeric_value": None,
        },
    ]
    spec = {
        "schema_version": "joulewise.detection_floor_extraction_spec.v1",
        "draft_status": "unfrozen_draft",
        "cells": cells,
        "reported_energy_cells": reported_cells,
        "reported_energy_registration": {
            "authority": "D-123",
            "procedure_only": True,
            "postcollection_numeric_values": (
                "structurally_absent_until_governed_reduction"
            ),
            "floor_projection_sha256": canonical_sha256(cells),
            "no_semantics_change_rule": (
                "Floor extraction consumes only cells; reported_energy_cells is "
                "a disjoint registered projection over the same physical bundle "
                "universe."
            ),
        },
        "reference_counts": {
            "floor_cell_references": 100,
            "reported_energy_references": 100,
            "total_registered_references": 200,
            "unique_physical_bundles": 50,
            "unique_config_paths": 50,
        },
        "phase_presence_contract": {
            "required_metrics": ["phase_energy_j.decode", "phase_energy_j.prefill"],
            "required_precheck_paths": [
                ["phase", "decode"],
                ["phase", "prefill"],
            ],
            "missing_registered_phase": (
                "refuse_before_floor_or_reported_mean_emission"
            ),
        },
    }
    errors = validate_extraction_spec(spec)
    if errors:
        raise ValueError(f"generated extraction spec is invalid: {errors[0]}")
    return spec


def producer_contract(
    *,
    plan_sha256: str,
    plan_sidecar_sha256: str,
    spec_sha256: str,
    root_manifest_id: str,
    root_manifest_sha256: str,
    config_set_sha256: str,
    decode_domain: str,
    prefill_domain: str,
    absolute_rows: Sequence[Mapping[str, Any]],
    comparative_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    config_rows = [
        {"bundle_id": row["run_id"], "config_sha256": row["config_sha256"]}
        for row in [*absolute_rows, *comparative_rows]
    ]
    expected_config_set_sha256 = canonical_sha256(config_rows)
    if config_set_sha256 != expected_config_set_sha256:
        raise ValueError("config-set SHA does not match the ordered member projection")

    return {
        "schema_version": "joulewise.d117_floor_producer_contract.v1",
        "draft_status": "unfrozen_draft",
        "plan_set_id": PLAN_SET_ID,
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "producer_index": 2,
        "component_artifact_id": COMPONENT_ARTIFACT_ID,
        "cell_composition_rule": "componentwise_max_never_sum.v1",
        "consumer_floor_rule": "cross_stack_armwise_max.v1",
        "plan": {
            "path": f"{PACK_REL.as_posix()}/calibration_plan.json",
            "plan_id": PLAN_ID,
            "sha256": plan_sha256,
            "sidecar_sha256": plan_sidecar_sha256,
        },
        "evidence_root_id": EVIDENCE_ROOT_ID,
        "stack_identity": {
            "hardware_target": HARDWARE["id"],
            "runtime_backend": HARDWARE["runtime_backend"],
            "telemetry_backend": HARDWARE["telemetry_backend"],
            "model_name": MODEL["name"],
            "model_source": MODEL["source"],
            "model_revision": MODEL["revision"],
            "quantization": "int4",
            "workload_profile": WORKLOAD,
        },
        "order_manifest": {
            "path": f"{PACK_REL.as_posix()}/order_manifest.json",
            "manifest_id": root_manifest_id,
            "sha256": root_manifest_sha256,
        },
        "extraction_spec": {
            "path": SPEC_REL.as_posix(),
            "sha256": spec_sha256,
            "member_count": 50,
            "floor_cell_count": 4,
            "floor_cell_member_references": 100,
            "reported_energy_cell_count": 2,
        },
        "config_set_sha256": config_set_sha256,
        "roles": [
            {
                "role": "decode",
                "artifact_cell_id": DECODE_ARTIFACT_CELL_ID,
                "transport_group_id": DECODE_TRANSPORT_ID,
                "metric": "phase_energy_j.decode",
                "target_precheck_path": ["phase", "decode"],
                "condition_family_id": DECODE_FAMILY_ID,
                "absolute_calibration_cell_id": DECODE_ABSOLUTE_CELL,
                "comparative_calibration_cell_id": DECODE_COMPARATIVE_CELL,
                "allowed_consumer_families": ["sw-decode-b-qwen25-7b"],
                "members": config_rows,
            },
            {
                "role": "prefill",
                "artifact_cell_id": PREFILL_ARTIFACT_CELL_ID,
                "transport_group_id": PREFILL_TRANSPORT_ID,
                "metric": "phase_energy_j.prefill",
                "target_precheck_path": ["phase", "prefill"],
                "condition_family_id": PREFILL_FAMILY_ID,
                "absolute_calibration_cell_id": PREFILL_ABSOLUTE_CELL,
                "comparative_calibration_cell_id": PREFILL_COMPARATIVE_CELL,
                "allowed_consumer_families": [PREFILL_FAMILY_ID],
                "members": config_rows,
            },
        ],
        "identity_pin_projection": {
            "work_order": IDENTITY_PROJECTION_WORK_ORDER,
            "mode": "derive_never_operator_enter",
            "required_before_arm": True,
            "expected_config_set_sha256": config_set_sha256,
            "projected_pins": {
                "model_artifact_sha256": None,
                "runtime_identity_sha256": None,
                "config_set_sha256": None,
            },
            "projection_receipt": None,
        },
        "postcollection": {"status": "unresolved"},
        "dependencies": [
            "D117-POSTCOLLECTION-TRUST-01 before mint",
            "D117-U2 successor engine before arm",
            f"{IDENTITY_PROJECTION_WORK_ORDER} before arm",
            "shared-bundle unique-physical-union mint order repair before mint",
        ],
    }


def token(kind: str, value: str, relative: str | None = None) -> dict[str, str]:
    row = {"kind": kind, "value": value}
    if relative is not None:
        row["relative"] = relative
    return row


def launch(
    *,
    command_id: str,
    command_kind: str,
    tool_id: str,
    interface_id: str,
    arguments: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.stage_launch.v1",
        "commands": [
            {
                "command_id": command_id,
                "command_kind": command_kind,
                "argv_template": {
                    "tool_id": tool_id,
                    "interface_id": interface_id,
                    "arguments": arguments,
                },
                "cwd": {"kind": "binding", "value": "repo_root"},
                "success_exit_codes": [0],
            }
        ],
    }


def collection_arguments(config_path: str, runs_binding: str) -> list[dict[str, str]]:
    return [
        token("repo_path", config_path),
        token("literal", "--runs-dir"),
        token("binding", runs_binding),
        token("literal", "--log"),
        token("binding_path", runs_binding, "campaign_log.jsonl"),
        token("literal", "--campaign-policy"),
        token("repo_path", POLICY_REL.as_posix()),
        token("literal", "--instrument-calibration-dir"),
        token("binding", "pre_calibration_dir"),
        token("literal", "--instrument-power-policy"),
        token("literal", "ac_high_power"),
        token("literal", "--arm-quiet-mode"),
        token("literal", "--arm-countdown-s"),
        token("literal", "20"),
        token("literal", "--max-failures"),
        token("literal", "1"),
    ]


def stage_graph(
    stage_manifest_refs: Mapping[str, Mapping[str, Any]],
    external_manifest_refs: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    stage_specs: list[tuple[str, str, int, dict[str, Any], str | None]] = []
    stage_specs.append(
        (
            "beta-bracket-reservation",
            "bracket_reservation",
            1,
            launch(
                command_id="beta-bracket-reservation.reserve",
                command_kind="bracket_reservation",
                tool_id="bracket_reserver",
                interface_id=(
                    "joulewise.calibration_window_bracket_reservation.cli.v1"
                ),
                arguments=[
                    token("literal", "--ledger"),
                    token("binding", "ledger_path"),
                    token("literal", "--head-pin"),
                    token("repo_path", LEDGER_HEAD_REL.as_posix()),
                    token("literal", "--session-id"),
                    token("binding", "bracket_session_id"),
                    token("literal", "--window-id"),
                    token("tree_pointer", "/window_identity/window_id"),
                    token("literal", "--plan-id"),
                    token("tree_pointer", "/plan/plan_id"),
                    token("literal", "--plan-sha256"),
                    token("tree_pointer", "/plan/actual_sha256"),
                    token("literal", "--evidence-root-id"),
                    token("tree_pointer", "/window_identity/evidence_root_id"),
                    token("literal", "--runs-root"),
                    token("binding", "claim_runs_root"),
                    token("literal", "--pre-attempt-id"),
                    token("binding", "pre_attempt_id"),
                    token("literal", "--post-attempt-id"),
                    token("binding", "post_attempt_id"),
                    token("literal", "--pre-custody-locator"),
                    token("binding", "pre_calibration_dir"),
                    token("literal", "--post-custody-locator"),
                    token("binding", "post_calibration_dir"),
                    token("literal", "--identity-epoch-json"),
                    token("binding", "identity_epoch_json"),
                    token("literal", "--t1-bindings-json"),
                    token("binding", "t1_bindings_json"),
                    token("literal", "--execute"),
                ],
            ),
            None,
        )
    )
    for slot, attempt in (("pre", "pre_attempt_id"),):
        stage_specs.append(
            (
                "beta-pre-calibration",
                "calibration_capture",
                1,
                launch(
                    command_id="beta-pre-calibration.capture",
                    command_kind="calibration_capture",
                    tool_id="fiducial_capture",
                    interface_id="joulewise.powermetrics_fiducial.cli.v1",
                    arguments=[
                        token("literal", "--allow-live"),
                        token("literal", "--output-root"),
                        token(
                            "binding_path",
                            "claim_runs_root",
                            "instrument_validation",
                        ),
                        token("literal", "--session-id"),
                        token("binding", "bracket_session_id"),
                        token("literal", "--slot"),
                        token("literal", slot),
                        token("literal", "--attempt-id"),
                        token("binding", attempt),
                        token("literal", "--power-policy"),
                        token("literal", "ac_high_power"),
                    ],
                ),
                None,
            )
        )
    collection_stages = (
        (
            "beta-bound-collection",
            12,
            "configs/campaigns/neg8_reference_corpus",
            "bound_runs_root",
            NEG8_MANIFEST_REL.as_posix(),
        ),
        (
            "beta-reference-start",
            3,
            "configs/campaigns/window_references/start_triplet",
            "claim_runs_root",
            START_MANIFEST_REL.as_posix(),
        ),
        (
            "beta-science-absolute",
            10,
            f"{PACK_REL.as_posix()}/01_phase_decode_absolute",
            "claim_runs_root",
            f"{PACK_REL.as_posix()}/01_phase_decode_absolute/order_manifest.json",
        ),
        (
            "beta-science-abba-01-05",
            20,
            f"{PACK_REL.as_posix()}/02_phase_decode_abba_blocks_01_05",
            "claim_runs_root",
            (
                f"{PACK_REL.as_posix()}/02_phase_decode_abba_blocks_01_05/"
                "order_manifest.json"
            ),
        ),
        (
            "beta-reference-midpoint",
            1,
            "configs/campaigns/window_references/midpoint",
            "claim_runs_root",
            MID_MANIFEST_REL.as_posix(),
        ),
        (
            "beta-science-abba-06-10",
            20,
            f"{PACK_REL.as_posix()}/03_phase_decode_abba_blocks_06_10",
            "claim_runs_root",
            (
                f"{PACK_REL.as_posix()}/03_phase_decode_abba_blocks_06_10/"
                "order_manifest.json"
            ),
        ),
        (
            "beta-reference-end",
            3,
            "configs/campaigns/window_references/end_triplet",
            "claim_runs_root",
            END_MANIFEST_REL.as_posix(),
        ),
    )
    for index, (stage_id, count, config_path, root_binding, manifest) in enumerate(
        collection_stages
    ):
        stage_specs.append(
            (
                stage_id,
                "campaign_collection",
                count,
                launch(
                    command_id=f"{stage_id}.collect",
                    command_kind="campaign_collection",
                    tool_id="campaign_runner",
                    interface_id="joulewise.run_campaign.cli.v1",
                    arguments=collection_arguments(config_path, root_binding),
                ),
                manifest,
            )
        )
        if index == 0:
            stage_specs.append(
                (
                    "beta-bound-derivation",
                    "bound_derivation",
                    1,
                    launch(
                        command_id="beta-bound-derivation.derive",
                        command_kind="bound_derivation",
                        tool_id="campaign_runner",
                        interface_id="joulewise.run_campaign.cli.v1",
                        arguments=[
                            token("literal", "--derive-neg8-drift-bound"),
                            token("repo_path", NEG8_CORPUS_REL.as_posix()),
                            token("literal", "--neg8-drift-bound-output"),
                            token(
                                "binding_path",
                                "bound_runs_root",
                                "neg8-drift-bound.json",
                            ),
                            token("literal", "--runs-dir"),
                            token("binding", "bound_runs_root"),
                        ],
                    ),
                    NEG8_CORPUS_REL.as_posix(),
                )
            )

    stage_specs.append(
        (
            "beta-post-calibration",
            "calibration_capture",
            1,
            launch(
                command_id="beta-post-calibration.capture",
                command_kind="calibration_capture",
                tool_id="fiducial_capture",
                interface_id="joulewise.powermetrics_fiducial.cli.v1",
                arguments=[
                    token("literal", "--allow-live"),
                    token("literal", "--output-root"),
                    token(
                        "binding_path", "claim_runs_root", "instrument_validation"
                    ),
                    token("literal", "--session-id"),
                    token("binding", "bracket_session_id"),
                    token("literal", "--slot"),
                    token("literal", "post"),
                    token("literal", "--attempt-id"),
                    token("binding", "post_attempt_id"),
                    token("literal", "--power-policy"),
                    token("literal", "ac_high_power"),
                ],
            ),
            None,
        )
    )
    stage_specs.append(
        (
            "beta-whole-window-verdict",
            "whole_window_verdict",
            1,
            launch(
                command_id="beta-whole-window-verdict.evaluate",
                command_kind="whole_window_verdict",
                tool_id="campaign_runner",
                interface_id="joulewise.run_campaign.cli.v1",
                arguments=[
                    token("literal", "--whole-window-verdict"),
                    token("literal", "--runs-dir"),
                    token("binding", "claim_runs_root"),
                    token("literal", "--log"),
                    token(
                        "binding_path", "claim_runs_root", "campaign_log.jsonl"
                    ),
                    token("literal", "--campaign-policy"),
                    token("repo_path", POLICY_REL.as_posix()),
                    token("literal", "--neg8-drift-bound"),
                    token(
                        "binding_path", "bound_runs_root", "neg8-drift-bound.json"
                    ),
                ],
            ),
            None,
        )
    )
    backup_launch = launch(
        command_id="beta-backup.claim",
        command_kind="backup",
        tool_id="backup_runs",
        interface_id="joulewise.backup_runs.cli.v1",
        arguments=[
            token("binding", "claim_runs_root"),
            token("binding", "claim_backup_destination"),
        ],
    )
    backup_launch["commands"].append(
        {
            "command_id": "beta-backup.bound",
            "command_kind": "backup",
            "argv_template": {
                "tool_id": "backup_runs",
                "interface_id": "joulewise.backup_runs.cli.v1",
                "arguments": [
                    token("binding", "bound_runs_root"),
                    token("binding", "bound_backup_destination"),
                ],
            },
            "cwd": {"kind": "binding", "value": "repo_root"},
            "success_exit_codes": [0],
        }
    )
    stage_specs.append(
        ("beta-backup", "backup", 2, backup_launch, None)
    )

    rows: list[dict[str, Any]] = []
    for ordinal, (stage_id, kind, count, recipe, reference) in enumerate(
        stage_specs, start=1
    ):
        if reference is None:
            if stage_id in ("beta-pre-calibration", "beta-post-calibration"):
                stage_input: dict[str, Any] = {
                    "kind": "arm_bindings",
                    "slot": "pre" if stage_id == "beta-pre-calibration" else "post",
                }
            elif stage_id == "beta-bracket-reservation":
                stage_input = {"kind": "arm_bindings"}
            else:
                stage_input = {"kind": "collected_roots"}
        elif reference == NEG8_CORPUS_REL.as_posix():
            stage_input = {
                "kind": "external_artifact",
                "path": reference,
                "sha256": EXPECTED_EXTERNAL_SHA256[reference],
            }
        elif reference == NEG8_MANIFEST_REL.as_posix():
            stage_input = dict(external_manifest_refs["neg8_bound"]["manifest"])
        elif reference == START_MANIFEST_REL.as_posix():
            stage_input = dict(external_manifest_refs["start_reference"]["manifest"])
        elif reference == MID_MANIFEST_REL.as_posix():
            stage_input = dict(
                external_manifest_refs["midpoint_reference"]["manifest"]
            )
        elif reference == END_MANIFEST_REL.as_posix():
            stage_input = dict(external_manifest_refs["end_reference"]["manifest"])
        else:
            matching = [
                dict(value)
                for value in stage_manifest_refs.values()
                if value["path"] == reference
            ]
            if len(matching) != 1:
                raise ValueError(f"unresolved stage input: {reference}")
            stage_input = matching[0]
        row = {
            "stage_id": stage_id,
            "ordinal": ordinal,
            "kind": kind,
            "expected_count": count,
            "predecessor": stage_specs[ordinal - 2][0] if ordinal > 1 else None,
            "successor": (
                stage_specs[ordinal][0] if ordinal < len(stage_specs) else None
            ),
            "input": stage_input,
            "launch": recipe,
        }
        rows.append(row)
    return rows


def external_input(input_id: str, manifest: Path) -> dict[str, Any]:
    manifest_data = json.loads((REPO_ROOT / manifest).read_text(encoding="utf-8"))
    executed_order = manifest_data.get("executed_order")
    if not isinstance(executed_order, list):
        raise ValueError(f"external manifest has no executed_order: {manifest}")
    members = []
    for ordinal, row in enumerate(executed_order, start=1):
        if not isinstance(row, Mapping):
            raise ValueError(f"malformed external manifest row: {manifest}")
        config = row.get("config")
        run_id = row.get("run_id")
        if not isinstance(config, str) or not isinstance(run_id, str):
            raise ValueError(f"malformed external manifest row: {manifest}")
        member_path = manifest.parent / config
        members.append(
            {
                "ordinal": ordinal,
                "run_id": run_id,
                "path": member_path.as_posix(),
                "sha256": sha256_file(REPO_ROOT / member_path),
            }
        )
    return {
        "external_input_id": input_id,
        "manifest": {
            "path": manifest.as_posix(),
            "manifest_id": manifest_data.get("manifest_id"),
            "sha256": EXPECTED_EXTERNAL_SHA256[manifest.as_posix()],
        },
        "expected_count": len(members),
        "members": members,
    }


def external_inputs() -> dict[str, dict[str, Any]]:
    return {
        "neg8_bound": external_input("neg8_bound", NEG8_MANIFEST_REL),
        "start_reference": external_input("start_reference", START_MANIFEST_REL),
        "midpoint_reference": external_input(
            "midpoint_reference", MID_MANIFEST_REL
        ),
        "end_reference": external_input("end_reference", END_MANIFEST_REL),
    }


def binding(binding_id: str, binding_type: str, constraints: list[str]) -> dict[str, Any]:
    return {
        "binding_id": binding_id,
        "type": binding_type,
        "constraints": constraints,
    }


def plan_tree(
    *,
    generator_sha256: str,
    plan_sha256: str,
    plan_sidecar_sha256: str,
    family_rows: list[dict[str, str]],
    science_rows: Sequence[Mapping[str, Any]],
    spec_sha256: str,
    producer_sha256: str,
    config_set_sha256: str,
    stage_manifest_refs: Mapping[str, Mapping[str, Any]],
    external_manifest_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": PLAN_TREE_SCHEMA,
        "draft_status": "unfrozen_draft",
        "plan": {
            "path": f"{PACK_REL.as_posix()}/calibration_plan.json",
            "plan_id": PLAN_ID,
            "actual_sha256": plan_sha256,
            "declared_sha256": plan_sha256,
            "sidecar_path": f"{PACK_REL.as_posix()}/calibration_plan.sha256",
            "sidecar_sha256": plan_sidecar_sha256,
        },
        "generator": {
            "path": f"{PACK_REL.as_posix()}/generate_configs.py",
            "sha256": generator_sha256,
        },
        "window_identity": {
            "window_id": PLAN_ID,
            "evidence_root_id": EVIDENCE_ROOT_ID,
        },
        "roots": {
            "claim_root_leaf": CLAIM_ROOT_LEAF,
            "bound_root_leaf": BOUND_ROOT_LEAF,
        },
        "campaign_policy": {
            "path": POLICY_REL.as_posix(),
            "sha256": EXPECTED_EXTERNAL_SHA256[POLICY_REL.as_posix()],
        },
        "acceptance_policy": {
            "selection": "issued_or_authenticated_d102_descendant_before_member_1",
            "issued_acceptance": calibration_basis()["issued_acceptance"],
            "issued_ledger_head": {
                "path": LEDGER_HEAD_REL.as_posix(),
                "file_sha256": EXPECTED_EXTERNAL_SHA256[LEDGER_HEAD_REL.as_posix()],
                "head_sha256": (
                    "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
                ),
            },
            "successor_effect": (
                "invalidate_and_reissue_readiness_and_pin_projection"
            ),
            "arming_prerequisites": [
                {"id": "D117-U2", "status": "required_before_arm"},
                {
                    "id": "D117-POSTCOLLECTION-TRUST-01",
                    "status": "required_before_mint",
                },
                {
                    "id": IDENTITY_PROJECTION_WORK_ORDER,
                    "status": "required_before_arm",
                },
                {
                    "id": "FLOOR-COMMONMODE-01",
                    "status": "implementation_identity_required_before_release",
                },
                {"id": TODO_BRANCH, "status": "unmerged_arm_blocker"},
            ],
        },
        "condition_families": family_rows,
        "science": [dict(row) for row in science_rows],
        "stage_graph": stage_graph(stage_manifest_refs, external_manifest_refs),
        "external_inputs": {
            "manifests": list(external_manifest_refs.values()),
            "artifacts": [
                {
                    "path": NEG8_CORPUS_REL.as_posix(),
                    "sha256": EXPECTED_EXTERNAL_SHA256[
                        NEG8_CORPUS_REL.as_posix()
                    ],
                }
            ],
        },
        "attempt_policy": {
            "policy": "abort_window_on_any_required_member_failure",
            "predeclared_before_data": True,
            "calibration_retries": 0,
            "science_member_replacements": 0,
            "outcome_dependent_top_up": "forbidden",
            "missing_failed_or_strict_invalid_member": "abort_non_claim_bearing",
        },
        "arm_attachments": {
            "launch": {
                "schema_version": "joulewise.stage_launch_bindings.v1",
                "bindings": [
                    {"name": "repo_root", "type": "existing_absolute_directory"},
                    {"name": "ledger_path", "type": "existing_absolute_file"},
                    {
                        "name": "claim_runs_root",
                        "type": "fresh_absolute_directory",
                        "leaf": CLAIM_ROOT_LEAF,
                    },
                    {
                        "name": "bound_runs_root",
                        "type": "fresh_absolute_directory",
                        "leaf": BOUND_ROOT_LEAF,
                    },
                    {"name": "operator_log_root", "type": "absolute_directory"},
                    {"name": "pre_calibration_dir", "type": "absolute_directory"},
                    {"name": "post_calibration_dir", "type": "absolute_directory"},
                    {"name": "claim_backup_destination", "type": "absolute_path"},
                    {"name": "bound_backup_destination", "type": "absolute_path"},
                    {"name": "bracket_session_id", "type": "nonempty_string"},
                    {"name": "pre_attempt_id", "type": "nonempty_string"},
                    {"name": "post_attempt_id", "type": "nonempty_string"},
                    {
                        "name": "identity_epoch_json",
                        "type": "authenticated_absolute_file",
                    },
                    {
                        "name": "t1_bindings_json",
                        "type": "authenticated_absolute_file",
                    },
                ],
                "derived_path_rules": [
                    (
                        "pre_calibration_dir=claim_runs_root/"
                        "instrument_validation/pre_attempt_id"
                    ),
                    (
                        "post_calibration_dir=claim_runs_root/"
                        "instrument_validation/post_attempt_id"
                    ),
                ],
            },
            "identity_pin_projection": {
                "work_order": IDENTITY_PROJECTION_WORK_ORDER,
                "mode": "derive_never_operator_enter",
                "required_before_arm": True,
                "expected_config_set_sha256": config_set_sha256,
                "projected_pins": {
                    "model_artifact_sha256": None,
                    "runtime_identity_sha256": None,
                    "config_set_sha256": None,
                },
                "projection_receipt": None,
            },
            "receipt_oracle": {
                "status": "blocked_on_unmerged_branch",
                "branch": TODO_BRANCH,
                "todo": (
                    f"TODO({TODO_BRANCH}): re-derive cadence and populate only "
                    "during lead-owned arm materialization after that branch lands."
                ),
                "receipt_count": None,
                "terminal_sequence": None,
                "arm_time_receipts": [],
            },
        },
        "closeout_attachments": {
            "bracket_binding_sha256": None,
            "terminal_ledger_head": None,
            "whole_window_verdict_sha256": None,
            "evaluation_basis_sha256": None,
            "extraction_report_sha256": None,
            "postcollection_receipt_digests": [],
            "todo": (
                f"TODO({TODO_BRANCH}): leave receipt-derived closeout fields empty "
                "until the landed recovery oracle and a completed claim window "
                "supply them."
            ),
            "backup_requirements": {
                "claim_root_verified": True,
                "bound_root_verified": True,
                "required_successful_backups": 2,
            },
        },
        "downstream_contract": {
            "extraction_spec": {
                "path": SPEC_REL.as_posix(),
                "sha256": spec_sha256,
            },
            "producer_contract": {
                "path": f"{PACK_REL.as_posix()}/producer_contract.json",
                "sha256": producer_sha256,
            },
            "prefill_phase_presence": "required_for_all_50_physical_bundles",
            "missing_registered_phase": "refuse",
        },
        "runtime_budget": {
            "planning_estimate_minutes_with_margin": 194.4,
            "planning_estimate_hours_with_margin": 3.24,
            "margin_percent": 20,
            "margin_authority": "time_headroom_only_never_member_replacement",
            "science_count": 50,
            "bound_count": 12,
            "reference_count": 7,
            "calibration_observation_count": 2,
        },
    }


def readme() -> bytes:
    return (
        "# D-117 Qwen2.5-7B phase-floor campaign — UNFROZEN DRAFT\n\n"
        "This pack pre-registers the beta window's 10 absolute decode members, "
        "ten null A/B/B/A blocks (40 members), and a zero-member prefill metric "
        "rider over the same 50 physical bundles. It retains the D-085 7B stack "
        "and condition-family identity and registers the two D-123 reported "
        "phase-energy means without adding collection.\n\n"
        "The pack is not armable. The receipt oracle is intentionally empty "
        f"pending `{TODO_BRANCH}`, arm-time identities require U11 projection, "
        "the D-124 estimator identity still requires implementation confirmation, "
        "and lead review must complete before any later release step.\n\n"
        "Regenerate or check with:\n\n"
        "```text\n"
        "python3 configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py\n"
        "python3 configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py --check\n"
        "```\n\n"
        "Integrity SHA-256 values in this draft detect drift; they do not mark release.\n"
    ).encode("utf-8")


def expected_pack_files() -> list[Path]:
    paths = [
        Path("README.md"),
        Path("generate_configs.py"),
        Path("calibration_plan.json"),
        Path("calibration_plan.sha256"),
        Path("order_manifest.json"),
        Path("plan_tree.json"),
        Path("plan_tree.sha256"),
        Path("producer_contract.json"),
        Path("condition_families/condition_family_df_ph_decode_qwen25_7b.json"),
        Path(
            "condition_families/"
            "condition_family_df_ph_prefill_p128_qwen25_7b.json"
        ),
    ]
    paths.append(Path("01_phase_decode_absolute/order_manifest.json"))
    paths.extend(
        Path(
            f"01_phase_decode_absolute/"
            f"d117f7-df-ph-decode-abs-r{rep:02d}.json"
        )
        for rep in range(1, 11)
    )
    for stage, first, last in (
        ("02_phase_decode_abba_blocks_01_05", 1, 5),
        ("03_phase_decode_abba_blocks_06_10", 6, 10),
    ):
        paths.append(Path(f"{stage}/order_manifest.json"))
        for block in range(first, last + 1):
            for position in ("a1", "b1", "b2", "a2"):
                paths.append(
                    Path(
                        f"{stage}/d117f7-df-cmp-abba-ph-decode-"
                        f"b{block:02d}-{position}.json"
                    )
                )
    return paths


def build_artifacts() -> dict[Path, bytes]:
    verify_external_inputs()
    decode, prefill, decode_domain, prefill_domain = condition_families()
    stages, absolute_ids, blocks = build_science()

    plan = {
        "schema_version": PLAN_SCHEMA,
        "draft_status": "unfrozen_draft",
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "fixed_n": N,
        "authorities": ["D-116", "D-117", "D-123", "D-124"],
        "stack_scope": {
            "hardware_target": "macbook_m3_max",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "model_name": MODEL["name"],
            "model_revision": MODEL["revision"],
            "model_source": MODEL["source"],
            "quantization": "int4",
            "sampling": SAMPLING,
            "decode_condition_family_id": DECODE_FAMILY_ID,
            "decode_condition_family_sha256": decode_domain,
            "prefill_condition_family_id": PREFILL_FAMILY_ID,
            "prefill_condition_family_sha256": prefill_domain,
        },
        "replacement_rule": {
            "policy": "abort_window_on_any_required_member_failure",
            "predeclared_before_data": True,
            "calibration_retries": 0,
            "science_member_replacements": 0,
            "outcome_dependent_top_up": "forbidden",
        },
        "floor_cells": [
            {
                "cell_id": DECODE_ABSOLUTE_CELL,
                "kind": "absolute",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": DECODE_COMPARATIVE_CELL,
                "kind": "comparative_abba",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_blocks": blocks,
                "estimator": D124_ESTIMATOR_ID,
            },
            {
                "cell_id": PREFILL_ABSOLUTE_CELL,
                "kind": "absolute",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": PREFILL_COMPARATIVE_CELL,
                "kind": "comparative_abba",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_blocks": blocks,
                "estimator": D124_ESTIMATOR_ID,
            },
        ],
        "reported_energy_cells": [
            {
                "cell_id": "d117-reported-mean-ph-decode-qwen25-7b",
                "metric": "phase_energy_j.decode",
                "measurand": "gross_phase_energy_j",
                "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
                "ordered_bundle_ids": [
                    *absolute_ids,
                    *[
                        member["bundle_id"]
                        for block in blocks
                        for member in block["members"]
                    ],
                ],
            },
            {
                "cell_id": "d117-reported-mean-ph-prefill-p128-qwen25-7b",
                "metric": "phase_energy_j.prefill",
                "measurand": "gross_phase_energy_j",
                "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
                "ordered_bundle_ids": [
                    *absolute_ids,
                    *[
                        member["bundle_id"]
                        for block in blocks
                        for member in block["members"]
                    ],
                ],
            },
        ],
        "execution_mode": {
            "ordered_science_stage_ids": [
                stage["subcampaign_id"] for stage in stages
            ],
            "planned_science_bundles": 50,
            "planned_bound_bundles": 12,
            "planned_reference_bundles": 7,
            "planned_calibration_observations": 2,
        },
        "roots": {
            "claim_root_leaf": CLAIM_ROOT_LEAF,
            "bound_root_leaf": BOUND_ROOT_LEAF,
        },
        "runs_dir": CLAIM_ROOT_LEAF,
        "order_manifest": "order_manifest.json",
        "campaign_log": f"{CLAIM_ROOT_LEAF}/campaign_log.jsonl",
        "campaign_policy": {
            "policy_id": "quiet-mac-p2-production",
            "path": POLICY_REL.as_posix(),
            "sha256": EXPECTED_EXTERNAL_SHA256[POLICY_REL.as_posix()],
        },
    }
    plan_bytes = render_json(plan)
    plan_sha = sha256_bytes(plan_bytes)
    plan_sidecar = sidecar_bytes(plan_sha, "calibration_plan.json")

    artifacts: dict[Path, bytes] = {
        PACK_REL / "README.md": readme(),
        PACK_REL / "generate_configs.py": SOURCE_GENERATOR.read_bytes(),
        PACK_REL / "calibration_plan.json": plan_bytes,
        PACK_REL / "calibration_plan.sha256": plan_sidecar,
        PACK_REL
        / "condition_families/condition_family_df_ph_decode_qwen25_7b.json": (
            REPO_ROOT / DECODE_TEMPLATE_REL
        ).read_bytes(),
        PACK_REL
        / "condition_families/condition_family_df_ph_prefill_p128_qwen25_7b.json": render_json(
            prefill
        ),
    }

    root_rows: list[dict[str, Any]] = []
    root_science: list[dict[str, Any]] = []
    stage_manifest_rows: list[dict[str, Any]] = []
    root_index = 1
    for stage in stages:
        stage_id = stage["subcampaign_id"]
        local_rows: list[dict[str, Any]] = []
        for local_index, run in enumerate(stage["runs"], start=1):
            config = config_for(run, plan_sha)
            config_bytes = render_json(config)
            config_sha = sha256_bytes(config_bytes)
            config_rel = Path(stage_id) / run["filename"]
            artifacts[PACK_REL / config_rel] = config_bytes
            local = manifest_entry(run, local_index, run["filename"], config_sha)
            root = manifest_entry(
                run, root_index, config_rel.as_posix(), config_sha
            )
            local_rows.append(local)
            root_rows.append(root)
            root_science.append(
                {
                    "ordinal": root_index,
                    "stage_id": stage_id,
                    "config_path": (PACK_REL / config_rel).as_posix(),
                    "config_sha256": config_sha,
                    "run_id": run["run_id"],
                    "role": run["role"],
                    "block_id": (
                        f"d117-df-cmp-abba-ph-decode-qwen25-7b-"
                        f"b{run['block_index']:02d}"
                        if run["role"] == "comparative_abba_member"
                        else None
                    ),
                    "block_index": run["block_index"],
                    "position": run["position"],
                    "arm": run["label"],
                }
            )
            root_index += 1
        manifest_id = (
            f"d117-floor-qwen25-7b-v1-{stage_id.replace('_', '-')}-order-v1"
        )
        leaf_manifest = {
            "schema_version": ORDER_SCHEMA,
            "manifest_id": manifest_id,
            "plan_id": PLAN_ID,
            "calibration_plan_sha256": plan_sha,
            "ordering_note": stage["ordering_note"],
            "planned_n_bundles": len(local_rows),
            "executed_order": local_rows,
        }
        leaf_bytes = render_json(leaf_manifest)
        leaf_rel = Path(stage_id) / "order_manifest.json"
        artifacts[PACK_REL / leaf_rel] = leaf_bytes
        stage_manifest_rows.append(
            {
                "stage_id": stage_id,
                "kind": "manifest",
                "path": (PACK_REL / leaf_rel).as_posix(),
                "manifest_id": manifest_id,
                "sha256": sha256_bytes(leaf_bytes),
            }
        )

    root_manifest_id = "d117-floor-qwen25-7b-v1-order-v1"
    root_manifest = {
        "schema_version": ORDER_SCHEMA,
        "manifest_id": root_manifest_id,
        "plan_id": PLAN_ID,
        "calibration_plan_sha256": plan_sha,
        "planned_n_bundles": len(root_rows),
        "subcampaign_order": [
            {
                "index": index,
                "subcampaign_id": stage["subcampaign_id"],
                "role": stage["role"],
                "optional": False,
                "planned_n_bundles": len(stage["runs"]),
                "ordering_note": stage["ordering_note"],
                "manifest_path": stage_manifest_rows[index - 1]["path"],
                "manifest_id": stage_manifest_rows[index - 1]["manifest_id"],
                "manifest_sha256": stage_manifest_rows[index - 1]["sha256"],
            }
            for index, stage in enumerate(stages, start=1)
        ],
        "executed_order": root_rows,
    }
    root_bytes = render_json(root_manifest)
    root_sha = sha256_bytes(root_bytes)
    artifacts[PACK_REL / "order_manifest.json"] = root_bytes

    absolute_rows = root_science[:10]
    comparative_rows = root_science[10:]
    spec = extraction_spec(
        decode=decode,
        prefill=prefill,
        decode_domain=decode_domain,
        prefill_domain=prefill_domain,
        absolute_rows=absolute_rows,
        comparative_rows=comparative_rows,
        root_manifest_id=root_manifest_id,
        root_manifest_sha256=root_sha,
    )
    spec_bytes = render_json(spec)
    spec_sha = sha256_bytes(spec_bytes)
    artifacts[SPEC_REL] = spec_bytes

    config_rows = [
        {"bundle_id": row["run_id"], "config_sha256": row["config_sha256"]}
        for row in root_science
    ]
    config_set_sha = canonical_sha256(config_rows)
    producer = producer_contract(
        plan_sha256=plan_sha,
        plan_sidecar_sha256=sha256_bytes(plan_sidecar),
        spec_sha256=spec_sha,
        root_manifest_id=root_manifest_id,
        root_manifest_sha256=root_sha,
        config_set_sha256=config_set_sha,
        decode_domain=decode_domain,
        prefill_domain=prefill_domain,
        absolute_rows=absolute_rows,
        comparative_rows=comparative_rows,
    )
    producer_bytes = render_json(producer)
    producer_sha = sha256_bytes(producer_bytes)
    artifacts[PACK_REL / "producer_contract.json"] = producer_bytes

    family_rows = [
        {
            "path": (
                f"{PACK_REL.as_posix()}/condition_families/"
                "condition_family_df_ph_decode_qwen25_7b.json"
            ),
            "byte_sha256": EXPECTED_EXTERNAL_SHA256[
                DECODE_TEMPLATE_REL.as_posix()
            ],
            "condition_family_id": DECODE_FAMILY_ID,
            "domain_sha256": decode_domain,
        },
        {
            "path": (
                f"{PACK_REL.as_posix()}/condition_families/"
                "condition_family_df_ph_prefill_p128_qwen25_7b.json"
            ),
            "byte_sha256": sha256_bytes(render_json(prefill)),
            "condition_family_id": PREFILL_FAMILY_ID,
            "domain_sha256": prefill_domain,
        },
    ]
    stage_manifest_refs = {
        row["stage_id"]: {
            "kind": row["kind"],
            "path": row["path"],
            "manifest_id": row["manifest_id"],
            "sha256": row["sha256"],
        }
        for row in stage_manifest_rows
    }
    external_manifest_refs = external_inputs()
    tree = plan_tree(
        generator_sha256=sha256_file(SOURCE_GENERATOR),
        plan_sha256=plan_sha,
        plan_sidecar_sha256=sha256_bytes(plan_sidecar),
        family_rows=family_rows,
        science_rows=root_science,
        spec_sha256=spec_sha,
        producer_sha256=producer_sha,
        config_set_sha256=config_set_sha,
        stage_manifest_refs=stage_manifest_refs,
        external_manifest_refs=external_manifest_refs,
    )
    tree_bytes = render_json(tree)
    tree_sha = sha256_bytes(tree_bytes)
    artifacts[PACK_REL / "plan_tree.json"] = tree_bytes
    artifacts[PACK_REL / "plan_tree.sha256"] = sidecar_bytes(
        tree_sha, "plan_tree.json"
    )
    return artifacts


def write_artifacts(output_root: Path, artifacts: Mapping[Path, bytes]) -> None:
    for relative, content in artifacts.items():
        path = output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def compare_artifacts(output_root: Path, artifacts: Mapping[Path, bytes]) -> None:
    problems: list[str] = []
    for relative, expected in artifacts.items():
        path = output_root / relative
        try:
            observed = path.read_bytes()
        except OSError as exc:
            problems.append(f"{relative}: unreadable: {exc}")
            continue
        if observed != expected:
            problems.append(f"{relative}: bytes differ")
    if problems:
        raise ValueError("generated draft check failed: " + "; ".join(problems))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    if args.check and args.output_root is not None:
        parser.error("--check and --output-root are mutually exclusive")
    return args


def main() -> int:
    args = parse_args()
    artifacts = build_artifacts()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="d117-floor-7b-check-") as temp:
            temp_root = Path(temp)
            write_artifacts(temp_root, artifacts)
            compare_artifacts(REPO_ROOT, artifacts)
            compare_artifacts(temp_root, artifacts)
        print(
            "draft check passed: 50 science configs, 4 floor cells, "
            "2 reporting cells"
        )
        return 0
    output_root = args.output_root.resolve() if args.output_root else REPO_ROOT
    write_artifacts(output_root, artifacts)
    pack_count = sum(1 for path in artifacts if PACK_REL in path.parents)
    print(
        f"generated {pack_count} pack files and {SPEC_REL.as_posix()}; "
        "science_configs=50"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"generation failed: {exc}") from exc
