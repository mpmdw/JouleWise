#!/usr/bin/env python3
"""Deterministically generate the Splitwise decode cross-model campaign."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.detection_floor import (  # noqa: E402
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
)
from joulewise.floor_extraction import (  # noqa: E402
    validate_condition_family_definition,
)
from joulewise.analysis_manifest_v3 import (  # noqa: E402
    MANIFEST_NAME as ANALYSIS_MANIFEST_V3_NAME,
    build_analysis_manifest_v3,
    write_manifest_atomic as write_analysis_manifest_v3_atomic,
)


N = 10
PLAN_ID = "splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b"
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
RUNS_DIR = "runs/splitwise_decode_v1"

MODEL_A = {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
    "weight_format": "mlx",
    "context_window": 32768,
}
MODEL_B = {
    "name": "Qwen2.5-7B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
    "revision": "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
    "weight_format": "mlx",
    "context_window": 32768,
}
QUANTIZATION = {"name": "int4", "bits": 4}
HARDWARE = {
    "id": "macbook_m3_max",
    "transport": "local",
    "runtime_backend": "mlx",
    "telemetry_backend": "powermetrics",
    "device_kind": "apple_silicon_unified_memory",
    "notes": (
        "splitwise_decode_v1 cross-model decode contrast on the current M3 Max; "
        "normal powermetrics sampler set only."
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

ARMS = {
    "A": {
        "condition_family_id": "sw-decode-a-qwen25-1p5b",
        "model": MODEL_A,
        "model_tag": "qwen25-1p5b-mlx",
    },
    "B": {
        "condition_family_id": "sw-decode-b-qwen25-7b",
        "model": MODEL_B,
        "model_tag": "qwen25-7b-mlx",
    },
}
STAGES = (
    {
        "subcampaign_id": "01_decode_contrast_blocks_01_05",
        "role": "comparative_contrast_first_half",
        "first_block": 1,
        "last_block": 5,
        "ordering_note": "Fixed contiguous A/B/B/A blocks 1-5 of the cross-model decode contrast.",
    },
    {
        "subcampaign_id": "02_decode_contrast_blocks_06_10",
        "role": "comparative_contrast_second_half",
        "first_block": 6,
        "last_block": 10,
        "ordering_note": "Fixed contiguous A/B/B/A blocks 6-10 of the cross-model decode contrast.",
    },
)


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_json(value))


def condition_family_definition(condition_family_id: str) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": condition_family_id,
        "workload_profile": {
            "name": "df_ph_decode",
            "prompt_tokens": 128,
            "output_tokens": 512,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "measurement_target": {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def definitions_and_hashes() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    definitions = {
        arm: condition_family_definition(data["condition_family_id"])
        for arm, data in ARMS.items()
    }
    hashes: dict[str, str] = {}
    for arm, definition in definitions.items():
        errors = validate_condition_family_definition(definition)
        if errors:
            joined = "; ".join(errors)
            raise ValueError(f"condition-family definition {arm} is invalid: {joined}")
        hashes[arm] = canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN,
            definition,
        )
    return definitions, hashes


def build_assembly() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stages = [{**stage, "runs": []} for stage in STAGES]
    blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        block_id = f"sw-decode-contrast-b{block:02d}"
        members: list[dict[str, Any]] = []
        for sequence_index, (arm, position) in enumerate(
            (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2")),
            start=1,
        ):
            run_id = f"swdec-contrast-b{block:02d}-{position.lower()}"
            run = {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "arm": arm,
                "rep": block,
                "role": "comparative_contrast_member",
                "block_index": block,
                "position_in_block": sequence_index,
                "collection_tags": [
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={arm}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            }
            stage_index = 0 if block <= 5 else 1
            stages[stage_index]["runs"].append(run)
            members.append(
                {
                    "position": position,
                    "plan_label": arm,
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
    return stages, blocks


def arm_plan(arm: str, condition_hash: str) -> dict[str, Any]:
    data = ARMS[arm]
    model = data["model"]
    return {
        "condition_family_id": data["condition_family_id"],
        "condition_family_sha256": condition_hash,
        "model_name": model["name"],
        "model_family": model["family"],
        "model_revision": model["revision"],
        "model_source": model["source"],
        "weight_format": model["weight_format"],
        "model_tag": data["model_tag"],
    }


def references() -> dict[str, Any]:
    common = {
        "condition_family_id": "df-rq-mid",
        "model_name": MODEL_A["name"],
        "model_revision": MODEL_A["revision"],
        "model_source": MODEL_A["source"],
        "integration": "supplied_by_window_chain_not_science_stage",
    }
    return {
        "window_references": {
            "source": "configs/campaigns/window_references/",
            "member_layout": "3+1+3",
            **common,
        },
        "in_window_bound_corpus": {
            "source": "configs/campaigns/neg8_reference_corpus/",
            "planned_n_bundles": 12,
            **common,
        },
    }


def config_for(run: dict[str, Any], plan_sha256: str) -> dict[str, Any]:
    arm = ARMS[run["arm"]]
    tags = [
        "phase2",
        "splitwise-decode-v1",
        "production-window",
        "comparative-contrast",
        f"df-condition={arm['condition_family_id']}",
        f"calibration-plan-sha256={plan_sha256}",
        *run["collection_tags"],
    ]
    return {
        "schema_version": "0.1",
        "run_id": run["run_id"],
        "model": arm["model"],
        "quantization": QUANTIZATION,
        "hardware_target": HARDWARE,
        "workload_profile": WORKLOAD,
        "interconnect": {"name": "local"},
        "sampling": SAMPLING,
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": tags,
        },
    }


def manifest_entry(run: dict[str, Any], index: int, config: str) -> dict[str, Any]:
    arm = ARMS[run["arm"]]
    return {
        "index": index,
        "config": config,
        "run_id": run["run_id"],
        "model_tag": arm["model_tag"],
        "rep": run["rep"],
        "workload": arm["condition_family_id"],
        "role": run["role"],
        "block_index": run["block_index"],
        "position_in_block": run["position_in_block"],
    }


def verify_stage(directory: Path) -> None:
    manifest_path = directory / "order_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("executed_order")
    if not isinstance(entries, list):
        raise ValueError(f"{manifest_path}: executed_order must be a list")
    manifest_configs = [entry.get("config") for entry in entries]
    if len(manifest_configs) != len(set(manifest_configs)):
        raise ValueError(f"{manifest_path}: config entries are not unique")
    expected_indexes = list(range(1, len(entries) + 1))
    indexes = [entry.get("index") for entry in entries]
    if indexes != expected_indexes:
        raise ValueError(
            f"{manifest_path}: indexes must be contiguous 1..{len(entries)}"
        )
    actual_configs = sorted(
        path.name
        for path in directory.glob("*.json")
        if path.name != "order_manifest.json"
    )
    if sorted(manifest_configs) != actual_configs:
        raise ValueError(
            f"{manifest_path}: manifest/config file mismatch: "
            f"manifest={sorted(manifest_configs)!r}, files={actual_configs!r}"
        )


def main() -> int:
    definitions, definition_hashes = definitions_and_hashes()
    stages, blocks = build_assembly()
    stage_ids = [stage["subcampaign_id"] for stage in stages]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "freeze_status": "frozen_before_measurement",
        "fixed_n": N,
        "stack_scope": {
            "hardware_target": "macbook_m3_max",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "quantization": "int4",
            "sampling": SAMPLING,
            "arms": {
                arm: arm_plan(arm, definition_hashes[arm])
                for arm in ("A", "B")
            },
            "note": (
                "The single-model model_name/model_revision/model_source keys used by "
                "p2_015_floors are deliberately replaced by arms because this campaign "
                "spans two model stacks."
            ),
        },
        "replacement_rule": {
            "policy": "technical_invalid_same_slot_only",
            "predeclared_before_data": True,
            "outcome_dependent_top_up": "forbidden_and_demotes_contrast_to_exploratory",
        },
        "cells": [
            {
                "cell_id": "sw-decode-contrast-1p5b-vs-7b",
                "kind": "comparative_contrast",
                "null_alias": False,
                "df_rows": [],
                "use_role": "primary_claim_gate",
                "minimum_claim_n": N,
                "window_class": "phase",
                "metric_selectors": ["phase_energy_j.decode"],
                "condition_family_ids": [
                    ARMS["A"]["condition_family_id"],
                    ARMS["B"]["condition_family_id"],
                ],
                "difference_orientation": "condition_b_minus_condition_a",
                "cluster_reducer": "single",
                "ordered_blocks": blocks,
            }
        ],
        "execution_modes": {
            "production_contrast_window": {
                "selected_for_this_frozen_plan": True,
                "ordered_subcampaign_ids": stage_ids,
                "planned_bundles": 40,
            }
        },
        "references": references(),
        "runs_dir": RUNS_DIR,
        "order_manifest": "order_manifest.json",
        "campaign_log": f"{RUNS_DIR}/campaign_log.jsonl",
        "campaign_policy": {
            "policy_id": "quiet-mac-p2-production",
            "path": "configs/campaign_policies/quiet_mac_p2_production.json",
            "binding": (
                "operator passes --campaign-policy; no campaign artifact declares it"
            ),
        },
    }

    plan_bytes = render_json(plan)
    plan_sha256 = hashlib.sha256(plan_bytes).hexdigest()
    (OUT / "calibration_plan.json").write_bytes(plan_bytes)
    (OUT / "calibration_plan.sha256").write_text(
        f"{plan_sha256}  calibration_plan.json\n",
        encoding="utf-8",
    )

    definition_paths = {
        "A": (
            OUT
            / "condition_families"
            / "condition_family_sw_decode_a_qwen25_1p5b.json"
        ),
        "B": (
            OUT
            / "condition_families"
            / "condition_family_sw_decode_b_qwen25_7b.json"
        ),
    }
    for arm in ("A", "B"):
        write_json(definition_paths[arm], definitions[arm])

    root_entries: list[dict[str, Any]] = []
    root_index = 1
    for stage in stages:
        stage_id = stage["subcampaign_id"]
        directory = OUT / stage_id
        directory.mkdir(parents=True, exist_ok=True)
        local_entries: list[dict[str, Any]] = []
        for local_index, run in enumerate(stage["runs"], start=1):
            write_json(directory / run["filename"], config_for(run, plan_sha256))
            local_entries.append(
                manifest_entry(run, local_index, run["filename"])
            )
            root_entries.append(
                manifest_entry(
                    run,
                    root_index,
                    f"{stage_id}/{run['filename']}",
                )
            )
            root_index += 1
        leaf_manifest = {
            "schema_version": ORDER_SCHEMA,
            "manifest_id": f"splitwise-decode-v1-{stage_id}-order-v1",
            "plan_id": PLAN_ID,
            "calibration_plan_sha256": plan_sha256,
            "ordering_note": stage["ordering_note"],
            "planned_n_bundles": len(local_entries),
            "executed_order": local_entries,
        }
        write_json(directory / "order_manifest.json", leaf_manifest)
        verify_stage(directory)

    root_manifest = {
        "schema_version": ORDER_SCHEMA,
        "manifest_id": "splitwise-decode-v1-order-v1",
        "plan_id": PLAN_ID,
        "calibration_plan_sha256": plan_sha256,
        "planned_n_bundles": len(root_entries),
        "subcampaign_order": [
            {
                "index": index,
                "subcampaign_id": stage["subcampaign_id"],
                "role": stage["role"],
                "optional": False,
                "planned_n_bundles": len(stage["runs"]),
                "ordering_note": stage["ordering_note"],
            }
            for index, stage in enumerate(stages, start=1)
        ],
        "executed_order": root_entries,
    }
    write_json(OUT / "order_manifest.json", root_manifest)

    analysis_manifest_v3 = build_analysis_manifest_v3(OUT)
    write_analysis_manifest_v3_atomic(
        OUT / ANALYSIS_MANIFEST_V3_NAME,
        analysis_manifest_v3,
    )

    print(
        f"generated {len(root_entries)} runnable configs across {len(stages)} "
        f"subcampaigns plus {ANALYSIS_MANIFEST_V3_NAME}; "
        f"calibration_plan_sha256={plan_sha256}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"generation failed: {exc}") from exc
