#!/usr/bin/env python3
"""Deterministically generate metrology-v1 sustained and extended-idle holds."""

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


N = 3
IDLE_SECONDS = (120, 300, 600)
IDLE_WORKLOAD_NAME = "mt_idle_extended"
PLAN_ID = "metrology-v1-long-holds-m3max"
RUNS_DIR = "runs/metrology_v1/long_holds"
HARDWARE = hardware("Sustained-load drift and extended-idle settle characterization on the current M3 Max")
STAGES = (
    {
        "subcampaign_id": "01_holds",
        "role": "sustained_decode_holds",
        "ordering_note": "Three fixed sustained decode repeats at 4096 output tokens.",
    },
    {
        "subcampaign_id": "02_idle_extended",
        "role": "extended_idle_observations",
        "ordering_note": "One fixed member each at 120, 300, and 600 idle seconds.",
    },
)


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_json(value))


def hold_family_id() -> str:
    return "mt-q15-decode-p0128-o4096"


def idle_family_id(idle_seconds: int) -> str:
    return f"mt-q15-decode-p0128-o0128-idle{idle_seconds:04d}"


def condition_family_definition(
    condition_family_id: str,
    output_tokens: int,
    *,
    workload_name: str = "df_ph_decode",
) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": condition_family_id,
        "workload_profile": workload(128, output_tokens, name=workload_name),
        "measurement_target": {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def definitions_and_hashes() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    definitions = {
        hold_family_id(): condition_family_definition(hold_family_id(), 4096),
        **{
            idle_family_id(idle_seconds): condition_family_definition(
                idle_family_id(idle_seconds),
                128,
                workload_name=IDLE_WORKLOAD_NAME,
            )
            for idle_seconds in IDLE_SECONDS
        },
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


def build_assembly() -> tuple[list[dict[str, Any]], list[str], dict[int, str]]:
    stages = [{**stage, "runs": []} for stage in STAGES]
    hold_ids: list[str] = []
    for replicate in range(1, N + 1):
        run_id = f"mthold-o4096-r{replicate:02d}"
        stages[0]["runs"].append(
            {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": replicate,
                "role": "absolute_sustained_decode_repeat",
                "block_index": replicate,
                "position_in_block": 1,
                "output_tokens": 4096,
                "idle_seconds": 30.0,
                "workload_name": "df_ph_decode",
                "condition_family_id": hold_family_id(),
                "collection_tags": [f"rep{replicate}", "sustained-decode-hold"],
            }
        )
        hold_ids.append(run_id)

    idle_ids: dict[int, str] = {}
    for index, idle_seconds in enumerate(IDLE_SECONDS, start=1):
        run_id = f"mtidle-i{idle_seconds:04d}-r01"
        stages[1]["runs"].append(
            {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": 1,
                "role": "absolute_extended_idle_observation",
                "block_index": index,
                "position_in_block": 1,
                "output_tokens": 128,
                "idle_seconds": float(idle_seconds),
                "workload_name": IDLE_WORKLOAD_NAME,
                "condition_family_id": idle_family_id(idle_seconds),
                "collection_tags": [
                    "rep1",
                    f"extended-idle-seconds={idle_seconds}",
                ],
            }
        )
        idle_ids[idle_seconds] = run_id
    return stages, hold_ids, idle_ids


def config_for(run: dict[str, Any], plan_sha256: str) -> dict[str, Any]:
    sampling = {**SAMPLING, "idle_seconds": run["idle_seconds"]}
    return config_document(
        run_id=run["run_id"],
        hardware_target=HARDWARE,
        workload_profile=workload(
            128, run["output_tokens"], name=run["workload_name"]
        ),
        sampling=sampling,
        campaign_slug="long-holds",
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
        "idle_seconds": run["idle_seconds"],
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
    stages, hold_ids, idle_ids = build_assembly()
    sampling_scope = {
        "power_hz": 10.0,
        "warmup_seconds": 5.0,
        "idle_seconds_by_condition_family": {
            hold_family_id(): 30.0,
            **{
                idle_family_id(idle_seconds): float(idle_seconds)
                for idle_seconds in IDLE_SECONDS
            },
        },
    }
    cells = [
        {
            "cell_id": "metrology-long-hold-decode-o4096",
            "df_rows": [],
            "kind": "absolute",
            "use_role": "staleness_sentinel",
            "minimum_claim_n": N,
            "window_class": "phase",
            "metric_selectors": ["phase_energy_j.decode"],
            "condition_family_id": hold_family_id(),
            "cluster_reducer": "single",
            "ordered_bundle_ids": hold_ids,
        },
        *[
            {
                "cell_id": f"metrology-extended-idle-i{idle_seconds:04d}",
                "df_rows": [],
                "kind": "absolute",
                "use_role": "staleness_sentinel",
                "minimum_claim_n": 1,
                "window_class": "phase",
                "metric_selectors": ["phase_energy_j.decode"],
                "condition_family_id": idle_family_id(idle_seconds),
                "cluster_reducer": "single",
                "ordered_bundle_ids": [idle_ids[idle_seconds]],
            }
            for idle_seconds in IDLE_SECONDS
        ],
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "freeze_status": "frozen_before_measurement",
        "ratification_note": "Ratified and frozen by the magistrate 2026-07-31 (D-096) before any member of this plan was measured.",
        "fixed_n": N,
        "stack_scope": stack_scope(definition_hashes, sampling=sampling_scope),
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
                "manifest_id": f"metrology-v1-long-holds-{stage_id}-order-v1",
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
            "manifest_id": "metrology-v1-long-holds-order-v1",
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
