#!/usr/bin/env python3
"""Deterministically generate parameterized metrology-v1 micro-delta stages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SUITE = OUT.parent
for bootstrap in (ROOT, SUITE):
    if str(bootstrap) not in sys.path:
        sys.path.insert(0, str(bootstrap))

from joulewise.detection_floor import (  # noqa: E402
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
)
from joulewise.floor_extraction import (  # noqa: E402
    validate_condition_family_definition,
)
from _shared import (  # noqa: E402
    MODEL,
    MODEL_TAG,
    ORDER_SCHEMA,
    PLAN_SCHEMA,
    SAMPLING,
    campaign_policy,
    config_document,
    hardware,
    references,
    replacement_rule,
    workload,
)


N = 5
BASE_OUTPUT_TOKENS = 512
PLAN_ID = "metrology-v1-micro-delta-m3max"
RUNS_DIR = "runs/metrology_v1/micro_delta"
HARDWARE = hardware("Parameterized micro-delta instrument sensitivity characterization on the current M3 Max")


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_json(value))


def canonicalize_k_values(values: list[int]) -> list[int]:
    """Validate and canonicalize a set of requested output-token deltas."""
    if any(value <= 0 for value in values):
        raise ValueError("every --k value must be a positive integer")
    if any(BASE_OUTPUT_TOKENS + value > MODEL["context_window"] for value in values):
        raise ValueError("512+k must not exceed the model context window")
    return sorted(set(values))


def parse_k_values(argv: list[str] | None = None) -> list[int]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--k",
        action="append",
        type=int,
        dest="k_values",
        help="positive output-token delta; repeat for multiple planned slots",
    )
    values = parser.parse_args(argv).k_values or [64]
    return canonicalize_k_values(values)


def family_id(output_tokens: int) -> str:
    return f"mt-q15-decode-p0128-o{output_tokens:04d}"


def condition_family_definition(output_tokens: int) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": family_id(output_tokens),
        "workload_profile": workload(128, output_tokens),
        "measurement_target": {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def definitions_and_hashes(
    k_values: list[int],
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    output_values = [BASE_OUTPUT_TOKENS, *[BASE_OUTPUT_TOKENS + k for k in k_values]]
    definitions = {
        family_id(output_tokens): condition_family_definition(output_tokens)
        for output_tokens in sorted(set(output_values))
    }
    hashes: dict[str, str] = {}
    for condition_family_id in sorted(definitions):
        definition = definitions[condition_family_id]
        errors = validate_condition_family_definition(definition)
        if errors:
            joined = "; ".join(errors)
            raise ValueError(
                f"condition-family definition {condition_family_id} is invalid: {joined}"
            )
        hashes[condition_family_id] = canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN, definition
        )
    return definitions, hashes


def build_assembly(
    k_values: list[int],
) -> tuple[list[dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    stages: list[dict[str, Any]] = []
    blocks_by_k: dict[int, list[dict[str, Any]]] = {}
    for k_value in k_values:
        stage = {
            "subcampaign_id": f"k{k_value:04d}",
            "role": f"micro_delta_k{k_value:04d}",
            "ordering_note": (
                f"DRAFT-PENDING-SLOPE: five fixed contiguous A/B/B/A blocks "
                f"with A=512 and B={BASE_OUTPUT_TOKENS + k_value} output tokens."
            ),
            "runs": [],
        }
        blocks: list[dict[str, Any]] = []
        for block in range(1, N + 1):
            block_id = f"mt-mdelta-k{k_value:04d}-b{block:02d}"
            members: list[dict[str, Any]] = []
            for sequence_index, (arm, position) in enumerate(
                (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2")),
                start=1,
            ):
                output_tokens = (
                    BASE_OUTPUT_TOKENS if arm == "A" else BASE_OUTPUT_TOKENS + k_value
                )
                run_id = f"mtmd-k{k_value:04d}-b{block:02d}-{position.lower()}"
                run = {
                    "run_id": run_id,
                    "filename": f"{run_id}.json",
                    "arm": arm,
                    "rep": block,
                    "role": "comparative_contrast_member",
                    "block_index": block,
                    "position_in_block": sequence_index,
                    "k": k_value,
                    "output_tokens": output_tokens,
                    "condition_family_id": family_id(output_tokens),
                    "collection_tags": [
                        f"rep{block}",
                        f"calibration-abba-block-id={block_id}",
                        f"calibration-abba-label={arm}",
                        f"calibration-abba-sequence-index={sequence_index}",
                        "DRAFT-PENDING-SLOPE",
                    ],
                }
                stage["runs"].append(run)
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
        stages.append(stage)
        blocks_by_k[k_value] = blocks
    return stages, blocks_by_k


def arm_plan(
    arm: str, k_values: list[int], definition_hashes: dict[str, str]
) -> dict[str, Any]:
    output_by_k = {
        f"k{k_value:04d}": (
            BASE_OUTPUT_TOKENS if arm == "A" else BASE_OUTPUT_TOKENS + k_value
        )
        for k_value in k_values
    }
    family_ids = sorted({family_id(output_tokens) for output_tokens in output_by_k.values()})
    return {
        "model_name": MODEL["name"],
        "model_family": MODEL["family"],
        "model_revision": MODEL["revision"],
        "model_source": MODEL["source"],
        "weight_format": MODEL["weight_format"],
        "model_tag": MODEL_TAG,
        "condition_families": [
            {
                "condition_family_id": condition_family_id,
                "condition_family_sha256": definition_hashes[condition_family_id],
            }
            for condition_family_id in family_ids
        ],
        "output_tokens_by_k": output_by_k,
    }


def config_for(run: dict[str, Any], plan_sha256: str) -> dict[str, Any]:
    return config_document(
        run_id=run["run_id"],
        hardware_target=HARDWARE,
        workload_profile=workload(128, run["output_tokens"]),
        sampling=SAMPLING,
        campaign_slug="micro-delta",
        condition_family_ids=[run["condition_family_id"]],
        plan_sha256=plan_sha256,
        collection_tags=run["collection_tags"],
    )


def manifest_entry(run: dict[str, Any], index: int, config: str) -> dict[str, Any]:
    return {
        "index": index,
        "config": config,
        "run_id": run["run_id"],
        "model_tag": MODEL_TAG,
        "rep": run["rep"],
        "workload": run["condition_family_id"],
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
    indexes = [entry.get("index") for entry in entries]
    if indexes != list(range(1, len(entries) + 1)):
        raise ValueError(f"{manifest_path}: indexes must be contiguous 1..{len(entries)}")
    actual_configs = sorted(
        path.name for path in directory.glob("*.json")
        if path.name != "order_manifest.json"
    )
    if sorted(manifest_configs) != actual_configs:
        raise ValueError(
            f"{manifest_path}: manifest/config file mismatch: "
            f"manifest={sorted(manifest_configs)!r}, files={actual_configs!r}"
        )


def refuse_stale_outputs(
    out: Path,
    stages: list[dict[str, Any]],
    definitions: dict[str, dict[str, Any]],
) -> None:
    """Refuse a mixed generation before writing, without deleting user data."""
    if not out.exists():
        return

    expected_stage_ids = {stage["subcampaign_id"] for stage in stages}
    stale: list[Path] = []
    for path in out.iterdir():
        if path.is_dir() and re.fullmatch(r"k[0-9]+", path.name):
            if path.name not in expected_stage_ids:
                stale.append(path)

    family_dir = out / "condition_families"
    expected_family_files = {
        f"condition_family_{condition_family_id.replace('-', '_')}.json"
        for condition_family_id in definitions
    }
    if family_dir.is_dir():
        for path in family_dir.iterdir():
            if re.fullmatch(
                r"condition_family_mt_q15_decode_p0128_o[0-9]+[.]json", path.name
            ) and path.name not in expected_family_files:
                stale.append(path)

    stages_by_id = {stage["subcampaign_id"]: stage for stage in stages}
    for stage_id in sorted(expected_stage_ids):
        directory = out / stage_id
        if not directory.is_dir():
            continue
        expected_json = {
            "order_manifest.json",
            *(run["filename"] for run in stages_by_id[stage_id]["runs"]),
        }
        stale.extend(
            path
            for path in directory.glob("*.json")
            if path.name not in expected_json
        )

    if stale:
        rendered = ", ".join(str(path.relative_to(out)) for path in sorted(stale))
        raise ValueError(
            "refusing to mix requested --k outputs with stale or unexpected "
            f"k-valued outputs: {rendered}; move them aside and rerun"
        )


def generate_configs(
    k_values: list[int], out: Path = OUT
) -> tuple[int, str, dict[str, str]]:
    k_values = canonicalize_k_values(k_values)
    definitions, definition_hashes = definitions_and_hashes(k_values)
    stages, blocks_by_k = build_assembly(k_values)
    refuse_stale_outputs(out, stages, definitions)
    out.mkdir(parents=True, exist_ok=True)
    cells = [
        {
            "cell_id": f"metrology-micro-delta-k{k_value:04d}",
            "df_rows": [],
            "kind": "comparative_contrast",
            "null_alias": False,
            "use_role": "staleness_sentinel",
            "minimum_claim_n": N,
            "window_class": "phase",
            "metric_selectors": ["phase_energy_j.decode"],
            "condition_family_ids": [
                family_id(BASE_OUTPUT_TOKENS),
                family_id(BASE_OUTPUT_TOKENS + k_value),
            ],
            "difference_orientation": "condition_b_minus_condition_a",
            "cluster_reducer": "single",
            "ordered_blocks": blocks_by_k[k_value],
        }
        for k_value in k_values
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "freeze_status": "draft_pending_slope",
        "draft_note": (
            "DRAFT-PENDING-SLOPE: k is set from the linearity_ramp fitted slope so "
            "the induced ΔE lands at 0.5× / 1× / 1.5× / 3× the published floor "
            "(paper §5 C3); the magistrate ratifies the resulting slots before any window."
        ),
        "DRAFT-PENDING-SLOPE": True,
        "fixed_n": N,
        "stack_scope": {
            "hardware_target": "macbook_m3_max",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "quantization": "int4",
            "sampling": SAMPLING,
            "arms": {
                arm: arm_plan(arm, k_values, definition_hashes)
                for arm in ("A", "B")
            },
            "note": (
                "Both arms use the identical Qwen2.5-1.5B-Instruct-4bit stack; "
                "the arms differ only in output length (A=512, B=512+k)."
            ),
        },
        "replacement_rule": replacement_rule(),
        "cells": cells,
        "execution_modes": {
            "production_metrology_window": {
                "selected_for_this_frozen_plan": True,
                "ordered_subcampaign_ids": [stage["subcampaign_id"] for stage in stages],
                "planned_bundles": sum(len(stage["runs"]) for stage in stages),
            }
        },
        "references": references(),
        "runs_dir": RUNS_DIR,
        "order_manifest": "order_manifest.json",
        "campaign_log": f"{RUNS_DIR}/campaign_log.jsonl",
        "campaign_policy": campaign_policy(),
    }
    plan_bytes = render_json(plan)
    plan_sha256 = hashlib.sha256(plan_bytes).hexdigest()
    (out / "calibration_plan.json").write_bytes(plan_bytes)
    (out / "calibration_plan.sha256").write_text(
        f"{plan_sha256}  calibration_plan.json\n", encoding="utf-8"
    )
    for condition_family_id in sorted(definitions):
        write_json(
            out
            / "condition_families"
            / f"condition_family_{condition_family_id.replace('-', '_')}.json",
            definitions[condition_family_id],
        )

    root_entries: list[dict[str, Any]] = []
    root_index = 1
    for stage in stages:
        stage_id = stage["subcampaign_id"]
        directory = out / stage_id
        directory.mkdir(parents=True, exist_ok=True)
        local_entries: list[dict[str, Any]] = []
        for local_index, run in enumerate(stage["runs"], start=1):
            write_json(directory / run["filename"], config_for(run, plan_sha256))
            local_entries.append(manifest_entry(run, local_index, run["filename"]))
            root_entries.append(
                manifest_entry(run, root_index, f"{stage_id}/{run['filename']}")
            )
            root_index += 1
        write_json(
            directory / "order_manifest.json",
            {
                "schema_version": ORDER_SCHEMA,
                "manifest_id": f"metrology-v1-micro-delta-{stage_id}-order-v1",
                "plan_id": PLAN_ID,
                "calibration_plan_sha256": plan_sha256,
                "ordering_note": stage["ordering_note"],
                "planned_n_bundles": len(local_entries),
                "executed_order": local_entries,
            },
        )
        verify_stage(directory)

    write_json(
        out / "order_manifest.json",
        {
            "schema_version": ORDER_SCHEMA,
            "manifest_id": "metrology-v1-micro-delta-order-v1",
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
        },
    )
    return len(root_entries), plan_sha256, definition_hashes


def main(argv: list[str] | None = None, out: Path = OUT) -> int:
    k_values = parse_k_values(argv)
    config_count, plan_sha256, definition_hashes = generate_configs(k_values, out)
    print(
        f"generated {config_count} runnable configs across {len(k_values)} "
        f"subcampaigns; calibration_plan_sha256={plan_sha256}"
    )
    for condition_family_id in sorted(definition_hashes):
        print(f"{condition_family_id}: {definition_hashes[condition_family_id]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"generation failed: {exc}") from exc
