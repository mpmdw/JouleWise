#!/usr/bin/env python3
"""Deterministically generate the metrology-v1 additivity shapes."""

from __future__ import annotations

import hashlib
import json
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
    MODEL_TAG,
    ORDER_SCHEMA,
    PLAN_SCHEMA,
    SAMPLING,
    campaign_policy,
    config_document,
    hardware,
    references,
    replacement_rule,
    stack_scope,
    workload,
)


N = 8
SHAPES = ((2048, 128), (512, 512), (128, 2048))
TARGETS = {
    "decode": ("phase_energy_j.decode", "phase"),
    "prefill": ("phase_energy_j.prefill", "phase"),
    "request": ("energy_request_j", "request"),
}
WORKLOAD_NAME = "df_ph_decode"
PLAN_ID = "metrology-v1-additivity-shapes-m3max"
RUNS_DIR = "runs/metrology_v1/additivity_shapes"
HARDWARE = hardware("Additivity and shape-invariance characterization on the current M3 Max")
STAGES = (
    {
        "subcampaign_id": "01_shapes",
        "role": "additivity_shapes",
        "ordering_note": (
            "Eight fixed rotated replicate-blocks; each block contains each "
            "prompt/output shape exactly once."
        ),
    },
)

# Auditable fixed order: eight sequential three-shape replicate-blocks.
SHAPE_ORDER = [
    (2048, 128), (512, 512), (128, 2048),
    (512, 512), (128, 2048), (2048, 128),
    (128, 2048), (2048, 128), (512, 512),
    (2048, 128), (512, 512), (128, 2048),
    (512, 512), (128, 2048), (2048, 128),
    (128, 2048), (2048, 128), (512, 512),
    (2048, 128), (512, 512), (128, 2048),
    (512, 512), (128, 2048), (2048, 128),
]


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_json(value))


def family_id(target: str, prompt_tokens: int, output_tokens: int) -> str:
    return f"mt-q15-{target}-p{prompt_tokens:04d}-o{output_tokens:04d}"


def condition_family_definition(
    target: str, prompt_tokens: int, output_tokens: int
) -> dict[str, Any]:
    metric, window_class = TARGETS[target]
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": family_id(target, prompt_tokens, output_tokens),
        "workload_profile": workload(
            prompt_tokens, output_tokens, name=WORKLOAD_NAME
        ),
        "measurement_target": {
            "metric": metric,
            "window_class": window_class,
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def definitions_and_hashes() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    definitions = {
        family_id(target, prompt_tokens, output_tokens): condition_family_definition(
            target, prompt_tokens, output_tokens
        )
        for prompt_tokens, output_tokens in SHAPES
        for target in TARGETS
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


def verify_counterbalance() -> None:
    if len(SHAPE_ORDER) != N * len(SHAPES):
        raise ValueError("additivity order must contain exactly 24 shapes")
    blocks = [
        SHAPE_ORDER[index:index + len(SHAPES)]
        for index in range(0, len(SHAPE_ORDER), len(SHAPES))
    ]
    for block in blocks:
        if sorted(block) != sorted(SHAPES):
            raise ValueError("each additivity replicate-block must contain every shape once")
    for shape in SHAPES:
        mean_position = sum(block.index(shape) + 1 for block in blocks) / N
        if abs(mean_position - 2.0) > 0.5:
            raise ValueError(
                f"shape {shape} mean position {mean_position} is not within ±0.5 of 2.0"
            )


def build_assembly() -> tuple[list[dict[str, Any]], dict[tuple[int, int], list[str]]]:
    verify_counterbalance()
    stages = [{**stage, "runs": []} for stage in STAGES]
    ordered_ids = {shape: [] for shape in SHAPES}
    for index, (prompt_tokens, output_tokens) in enumerate(SHAPE_ORDER):
        replicate = index // len(SHAPES) + 1
        run_id = f"mtadd-p{prompt_tokens:04d}o{output_tokens:04d}-r{replicate:02d}"
        family_ids = [
            family_id(target, prompt_tokens, output_tokens) for target in TARGETS
        ]
        run = {
            "run_id": run_id,
            "filename": f"{run_id}.json",
            "rep": replicate,
            "role": "absolute_shape_repeat",
            "block_index": replicate,
            "position_in_block": index % len(SHAPES) + 1,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "condition_family_ids": family_ids,
            "collection_tags": [
                f"rep{replicate}",
                f"shape-prompt-tokens={prompt_tokens}",
                f"shape-output-tokens={output_tokens}",
            ],
        }
        stages[0]["runs"].append(run)
        ordered_ids[(prompt_tokens, output_tokens)].append(run_id)
    return stages, ordered_ids


def config_for(run: dict[str, Any], plan_sha256: str) -> dict[str, Any]:
    return config_document(
        run_id=run["run_id"],
        hardware_target=HARDWARE,
        workload_profile=workload(
            run["prompt_tokens"], run["output_tokens"], name=WORKLOAD_NAME
        ),
        sampling=SAMPLING,
        campaign_slug="additivity-shapes",
        condition_family_ids=run["condition_family_ids"],
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
        "workload": family_id("request", run["prompt_tokens"], run["output_tokens"]),
        "condition_family_ids": run["condition_family_ids"],
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


def main() -> int:
    definitions, definition_hashes = definitions_and_hashes()
    stages, ordered_ids = build_assembly()
    cells: list[dict[str, Any]] = []
    for prompt_tokens, output_tokens in SHAPES:
        for target, (metric, window_class) in TARGETS.items():
            cells.append(
                {
                    "cell_id": f"metrology-additivity-{target}-p{prompt_tokens:04d}-o{output_tokens:04d}",
                    "df_rows": [],
                    "kind": "absolute",
                    "use_role": "staleness_sentinel",
                    "minimum_claim_n": N,
                    "window_class": window_class,
                    "metric_selectors": [metric],
                    "condition_family_id": family_id(
                        target, prompt_tokens, output_tokens
                    ),
                    "cluster_reducer": "single",
                    "ordered_bundle_ids": ordered_ids[(prompt_tokens, output_tokens)],
                }
            )
    plan = {
        "schema_version": PLAN_SCHEMA,
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "freeze_status": "frozen_before_measurement",
        "ratification_note": "Ratified and frozen by the magistrate 2026-07-31 (D-096) before any member of this plan was measured.",
        "fixed_n": N,
        "stack_scope": stack_scope(definition_hashes),
        "replacement_rule": replacement_rule(),
        "cells": cells,
        "execution_modes": {
            "production_metrology_window": {
                "selected_for_this_frozen_plan": True,
                "ordered_subcampaign_ids": [stage["subcampaign_id"] for stage in stages],
                "planned_bundles": len(SHAPE_ORDER),
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
    (OUT / "calibration_plan.json").write_bytes(plan_bytes)
    (OUT / "calibration_plan.sha256").write_text(
        f"{plan_sha256}  calibration_plan.json\n", encoding="utf-8"
    )
    for condition_family_id in sorted(definitions):
        write_json(
            OUT / "condition_families" / f"condition_family_{condition_family_id.replace('-', '_')}.json",
            definitions[condition_family_id],
        )

    root_entries: list[dict[str, Any]] = []
    root_index = 1
    for stage in stages:
        stage_id = stage["subcampaign_id"]
        directory = OUT / stage_id
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
                "manifest_id": f"metrology-v1-additivity-shapes-{stage_id}-order-v1",
                "plan_id": PLAN_ID,
                "calibration_plan_sha256": plan_sha256,
                "ordering_note": stage["ordering_note"],
                "planned_n_bundles": len(local_entries),
                "executed_order": local_entries,
            },
        )
        verify_stage(directory)

    write_json(
        OUT / "order_manifest.json",
        {
            "schema_version": ORDER_SCHEMA,
            "manifest_id": "metrology-v1-additivity-shapes-order-v1",
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
    print(
        f"generated {len(root_entries)} runnable configs across {len(stages)} "
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
