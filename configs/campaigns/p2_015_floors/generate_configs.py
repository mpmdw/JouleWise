#!/usr/bin/env python3
"""Deterministically generate the P2-015 Window-A floor campaign assembly.

This generator writes only below its own directory.  It freezes one calibration
plan before any measurement, emits one order manifest per checkpointable
sub-campaign, and emits a root order manifest for later P2-039 evidence binding.
It deliberately does not synthesize DF-TELEM-ONOFF: the current BenchmarkConfig
and powermetrics adapter expose no per-config extra-sampler setting.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
N = 10
MODEL_TAG = "qwen25-1p5b-mlx"
PLAN_ID = "p2-015-window-a-m3max-qwen25-1p5b-v1"
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
RUNS_DIR = "runs/p2_015_floors_window_a"
SUITE_REF = "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json"
SUITE_SHA256 = "0316283dde8afd5fc0dea66b56037a1aea34b42d415aec57af4831a119af8471"


MODEL = {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
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
        "P2-015 Window-A floor calibration on the current M3 Max; "
        "normal powermetrics sampler set only."
    ),
}
SAMPLING = {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0}


PROFILES: dict[str, dict[str, Any]] = {
    "df-rq-mid": {
        "name": "df_rq_mid",
        "prompt_tokens": 1024,
        "output_tokens": 256,
        "df_rows": ["DF-RQ-GROSS-MID", "DF-RQ-IDLE-MID"],
        "metrics": ["gross_energy_j", "energy_request_j", "idle_subtracted_energy_j"],
        "window_class": "request",
        "use_role": "primary_claim_gate",
    },
    "df-rq-short": {
        "name": "df_rq_short",
        "prompt_tokens": 128,
        "output_tokens": 64,
        "df_rows": ["DF-RQ-GROSS-SHORT", "DF-RQ-IDLE-SHORT"],
        "metrics": ["gross_energy_j", "energy_request_j", "idle_subtracted_energy_j"],
        "window_class": "request",
        "use_role": "primary_claim_gate",
    },
    "df-rq-long-prompt": {
        "name": "df_rq_long_prompt",
        "prompt_tokens": 4096,
        "output_tokens": 64,
        "df_rows": ["DF-RQ-GROSS-LONG-PROMPT", "DF-RQ-IDLE-LONG-PROMPT"],
        "metrics": ["gross_energy_j", "energy_request_j", "idle_subtracted_energy_j"],
        "window_class": "request",
        "use_role": "optional_direct_coverage",
    },
    "df-rq-long-decode": {
        "name": "df_rq_long_decode",
        "prompt_tokens": 128,
        "output_tokens": 512,
        "df_rows": ["DF-RQ-GROSS-LONG-DECODE", "DF-RQ-IDLE-LONG-DECODE"],
        "metrics": ["gross_energy_j", "energy_request_j", "idle_subtracted_energy_j"],
        "window_class": "request",
        "use_role": "optional_direct_coverage",
    },
    "df-ph-prefill": {
        "name": "df_ph_prefill",
        "prompt_tokens": 4096,
        "output_tokens": 64,
        "df_rows": ["DF-PH-PREFILL"],
        "metrics": ["phase_energy_j.prefill"],
        "window_class": "phase",
        "use_role": "primary_claim_gate",
    },
    "df-ph-decode": {
        "name": "df_ph_decode",
        "prompt_tokens": 128,
        "output_tokens": 512,
        "df_rows": ["DF-PH-DECODE"],
        "metrics": ["phase_energy_j.decode"],
        "window_class": "phase",
        "use_role": "primary_claim_gate",
    },
    "df-ph-short-prefill": {
        "name": "df_ph_short_prefill",
        "prompt_tokens": 128,
        "output_tokens": 64,
        "df_rows": ["DF-PH-SHORT-PREFILL"],
        "metrics": ["phase_energy_j.prefill"],
        "window_class": "phase",
        "use_role": "identifiability_and_floor_if_eligible",
    },
    "df-su-sentinel": {
        "name": "df_su_sentinel",
        "suite_manifest_ref": SUITE_REF,
        "suite_manifest_sha256": SUITE_SHA256,
        "df_rows": ["DF-SU-ITEM", "DF-SU-LEVEL"],
        "metrics": [
            "suite_metrics.items[*].gross_energy_j",
            "suite_metrics.levels[*].gross_energy_j",
        ],
        "window_class": "item_and_level",
        "use_role": "primary_claim_gate",
    },
}


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_json(value))


def new_subcampaign(
    subcampaign_id: str,
    title: str,
    *,
    role: str,
    optional: bool = False,
    ordering_note: str,
) -> dict[str, Any]:
    return {
        "subcampaign_id": subcampaign_id,
        "title": title,
        "role": role,
        "optional": optional,
        "ordering_note": ordering_note,
        "runs": [],
    }


def add_run(
    subcampaign: dict[str, Any],
    *,
    run_id: str,
    condition_id: str,
    rep: int,
    role: str,
    block_index: int,
    position_in_block: int,
    collection_tags: list[str],
    sentinel_position: str | None = None,
) -> dict[str, Any]:
    filename = f"{run_id}.json"
    run = {
        "run_id": run_id,
        "filename": filename,
        "condition_id": condition_id,
        "rep": rep,
        "role": role,
        "block_index": block_index,
        "position_in_block": position_in_block,
        "collection_tags": collection_tags,
        "sentinel_position": sentinel_position,
    }
    subcampaign["runs"].append(run)
    return run


def add_absolute_round_robin(
    subcampaign: dict[str, Any], condition_ids: list[str]
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    by_condition: dict[str, list[str]] = {condition_id: [] for condition_id in condition_ids}
    for rep in range(1, N + 1):
        offset = (rep - 1) % len(condition_ids)
        order = condition_ids[offset:] + condition_ids[:offset]
        for position, condition_id in enumerate(order, start=1):
            run_id = f"p2015-{condition_id}-abs-r{rep:02d}"
            add_run(
                subcampaign,
                run_id=run_id,
                condition_id=condition_id,
                rep=rep,
                role="absolute_repeat",
                block_index=rep,
                position_in_block=position,
                collection_tags=[f"rep{rep}"],
            )
            by_condition[condition_id].append(run_id)
    for condition_id in condition_ids:
        profile = PROFILES[condition_id]
        cells.append(
            {
                "cell_id": f"{condition_id}-absolute",
                "df_rows": profile["df_rows"],
                "kind": "absolute",
                "use_role": profile["use_role"],
                "minimum_claim_n": N,
                "window_class": profile["window_class"],
                "metric_selectors": profile["metrics"],
                "condition_family_id": condition_id,
                "cluster_reducer": "mean" if condition_id == "df-su-sentinel" else "single",
                "ordered_bundle_ids": by_condition[condition_id],
            }
        )
    return cells


def add_abba(
    subcampaign: dict[str, Any],
    *,
    condition_id: str,
    comparative_cell_id: str,
    df_rows: list[str],
    metrics: list[str],
    window_class: str,
    use_role: str,
) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        block_id = f"{comparative_cell_id}-b{block:02d}"
        members = []
        for sequence_index, (label, position) in enumerate(
            (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2")),
            start=1,
        ):
            run_id = f"p2015-{comparative_cell_id}-b{block:02d}-{position.lower()}"
            add_run(
                subcampaign,
                run_id=run_id,
                condition_id=condition_id,
                rep=block,
                role="comparative_abba_member",
                block_index=block,
                position_in_block=sequence_index,
                collection_tags=[
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={label}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            )
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
    return {
        "cell_id": comparative_cell_id,
        "df_rows": df_rows,
        "kind": "comparative_abba",
        "use_role": use_role,
        "minimum_claim_n": N,
        "window_class": window_class,
        "metric_selectors": metrics,
        "condition_family_id": condition_id,
        "cluster_reducer": "mean" if condition_id == "df-su-sentinel" else "single",
        "ordered_blocks": blocks,
    }


def build_assembly() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    subcampaigns: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []

    neg8_start = new_subcampaign(
        "00_neg8_start",
        "NEG-8 fixed daily reference at Window-A start",
        role="neg8_daily_reference_start",
        ordering_note="Fixed first position; scientific condition matches the end reference.",
    )
    add_run(
        neg8_start,
        run_id="p2015-neg8-reference-start",
        condition_id="df-rq-mid",
        rep=1,
        role="neg8_daily_reference",
        block_index=1,
        position_in_block=1,
        collection_tags=[],
        sentinel_position="start",
    )
    subcampaigns.append(neg8_start)

    request_abs = new_subcampaign(
        "01_request_absolute_core",
        "Core mid/short gross and idle-subtracted request repeats",
        role="absolute_request_core",
        ordering_note="Two-condition round-robin alternates the leading condition by repetition.",
    )
    cells.extend(add_absolute_round_robin(request_abs, ["df-rq-mid", "df-rq-short"]))
    subcampaigns.append(request_abs)

    phase_abs = new_subcampaign(
        "02_phase_absolute",
        "Prefill, decode, and short-prefill absolute repeats",
        role="absolute_phase",
        ordering_note=(
            "Three-condition cyclic round-robin rotates the leading condition; n=10 leaves "
            "the predeclared one-position imbalance visible in the manifest."
        ),
    )
    cells.extend(
        add_absolute_round_robin(
            phase_abs, ["df-ph-prefill", "df-ph-decode", "df-ph-short-prefill"]
        )
    )
    subcampaigns.append(phase_abs)

    request_abba = new_subcampaign(
        "03_request_abba",
        "Same-condition request ABBA blocks",
        role="comparative_request",
        ordering_note="Ten contiguous A/B/B/A blocks; A and B are aliases of df-rq-mid.",
    )
    cells.append(
        add_abba(
            request_abba,
            condition_id="df-rq-mid",
            comparative_cell_id="df-cmp-abba-rq",
            df_rows=["DF-CMP-ABBA-RQ"],
            metrics=["gross_energy_j", "energy_request_j"],
            window_class="request",
            use_role="primary_claim_gate",
        )
    )
    subcampaigns.append(request_abba)

    phase_prefill_abba = new_subcampaign(
        "04_phase_prefill_abba",
        "Same-condition prefill-phase ABBA blocks",
        role="comparative_phase_prefill",
        ordering_note="Ten contiguous A/B/B/A blocks over the exact df-ph-prefill profile.",
    )
    cells.append(
        add_abba(
            phase_prefill_abba,
            condition_id="df-ph-prefill",
            comparative_cell_id="df-cmp-abba-ph-prefill",
            df_rows=["DF-CMP-ABBA-PH"],
            metrics=["phase_energy_j.prefill"],
            window_class="phase",
            use_role="primary_claim_gate",
        )
    )
    subcampaigns.append(phase_prefill_abba)

    phase_decode_abba = new_subcampaign(
        "05_phase_decode_abba",
        "Same-condition decode-phase ABBA blocks",
        role="comparative_phase_decode",
        ordering_note="Ten contiguous A/B/B/A blocks over the exact df-ph-decode profile.",
    )
    cells.append(
        add_abba(
            phase_decode_abba,
            condition_id="df-ph-decode",
            comparative_cell_id="df-cmp-abba-ph-decode",
            df_rows=["DF-CMP-ABBA-PH"],
            metrics=["phase_energy_j.decode"],
            window_class="phase",
            use_role="primary_claim_gate",
        )
    )
    subcampaigns.append(phase_decode_abba)

    suite_abs = new_subcampaign(
        "06_suite_absolute",
        "Tiny-suite item/level absolute repeats",
        role="absolute_suite",
        ordering_note=(
            "One frozen five-item same-shape suite condition repeated in ten independent bundles; "
            "items inside a bundle never increase n."
        ),
    )
    cells.extend(add_absolute_round_robin(suite_abs, ["df-su-sentinel"]))
    subcampaigns.append(suite_abs)

    suite_abba = new_subcampaign(
        "07_suite_abba",
        "Tiny-suite item/level same-condition ABBA blocks",
        role="comparative_suite",
        ordering_note="Ten contiguous A/B/B/A blocks over the exact frozen suite condition.",
    )
    cells.append(
        add_abba(
            suite_abba,
            condition_id="df-su-sentinel",
            comparative_cell_id="df-cmp-abba-su",
            df_rows=["DF-CMP-ABBA-SU"],
            metrics=[
                "suite_metrics.items[*].gross_energy_j",
                "suite_metrics.levels[*].gross_energy_j",
            ],
            window_class="item_and_level",
            use_role="primary_claim_gate",
        )
    )
    subcampaigns.append(suite_abba)

    optional_long_abs = new_subcampaign(
        "08_optional_long_request_absolute",
        "Optional AP-2 long-prompt/long-decode request repeats",
        role="absolute_request_optional_direct_coverage",
        optional=True,
        ordering_note="Two-condition round-robin alternates the leading condition by repetition.",
    )
    cells.extend(
        add_absolute_round_robin(
            optional_long_abs, ["df-rq-long-prompt", "df-rq-long-decode"]
        )
    )
    subcampaigns.append(optional_long_abs)

    optional_short_abba = new_subcampaign(
        "09_optional_short_prefill_abba",
        "Optional short-prefill stress ABBA blocks",
        role="comparative_phase_short_prefill_optional",
        optional=True,
        ordering_note="Ten contiguous A/B/B/A blocks over the exact short-prefill stress profile.",
    )
    cells.append(
        add_abba(
            optional_short_abba,
            condition_id="df-ph-short-prefill",
            comparative_cell_id="df-cmp-abba-ph-short-prefill",
            df_rows=["DF-CMP-ABBA-PH"],
            metrics=["phase_energy_j.prefill"],
            window_class="phase",
            use_role="optional_short_prefill_comparative_claim_gate",
        )
    )
    subcampaigns.append(optional_short_abba)

    neg8_end = new_subcampaign(
        "11_neg8_end",
        "NEG-8 fixed daily reference at Window-A end",
        role="neg8_daily_reference_end",
        ordering_note="Fixed final position; scientific condition matches the start reference.",
    )
    add_run(
        neg8_end,
        run_id="p2015-neg8-reference-end",
        condition_id="df-rq-mid",
        rep=2,
        role="neg8_daily_reference",
        block_index=1,
        position_in_block=1,
        collection_tags=[],
        sentinel_position="end",
    )
    subcampaigns.append(neg8_end)
    return subcampaigns, cells


def workload_for(condition_id: str) -> dict[str, Any]:
    profile = PROFILES[condition_id]
    workload: dict[str, Any] = {
        "name": profile["name"],
        "repetitions": 1,
        "warmup_runs": 1,
    }
    if "suite_manifest_ref" in profile:
        workload["suite_manifest_ref"] = profile["suite_manifest_ref"]
        workload["suite_manifest_sha256"] = profile["suite_manifest_sha256"]
    else:
        workload["prompt_tokens"] = profile["prompt_tokens"]
        workload["output_tokens"] = profile["output_tokens"]
    return workload


def config_for(run: dict[str, Any], plan_sha256: str) -> dict[str, Any]:
    common_tags = [
        "phase2",
        "p2-015",
        "window-a",
        "floor-calibration",
        f"df-condition={run['condition_id']}",
        f"calibration-plan-sha256={plan_sha256}",
    ]
    return {
        "schema_version": "0.1",
        "run_id": run["run_id"],
        "model": MODEL,
        "quantization": QUANTIZATION,
        "hardware_target": HARDWARE,
        "workload_profile": workload_for(run["condition_id"]),
        "interconnect": {"name": "local"},
        "sampling": SAMPLING,
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": common_tags + run["collection_tags"],
        },
    }


def manifest_entry(run: dict[str, Any], index: int, *, config: str) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "index": index,
        "config": config,
        "run_id": run["run_id"],
        "model_tag": MODEL_TAG,
        "rep": run["rep"],
        "workload": run["condition_id"],
        "role": run["role"],
        "block_index": run["block_index"],
        "position_in_block": run["position_in_block"],
    }
    if run["sentinel_position"] is not None:
        entry["sentinel_position"] = run["sentinel_position"]
    return entry


def main() -> int:
    subcampaigns, cells = build_assembly()
    full_ids = [campaign["subcampaign_id"] for campaign in subcampaigns]
    core_ids = [
        campaign["subcampaign_id"]
        for campaign in subcampaigns
        if not campaign["optional"]
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "plan_id": PLAN_ID,
        "calibration_scope": "window_a",
        "freeze_status": "frozen_before_measurement",
        "fixed_n": N,
        "stack_scope": {
            "hardware_target": "macbook_m3_max",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "model_name": MODEL["name"],
            "model_revision": MODEL["revision"],
            "model_source": MODEL["source"],
            "quantization": "int4",
            "sampling": SAMPLING,
            "suite_manifest_ref": SUITE_REF,
            "suite_manifest_sha256": SUITE_SHA256,
        },
        "replacement_rule": {
            "policy": "technical_invalid_same_slot_only",
            "predeclared_before_data": True,
            "outcome_dependent_top_up": "forbidden_and_demotes_contrast_to_exploratory",
        },
        "execution_modes": {
            "expanded_window_a": {
                "selected_for_this_frozen_plan": True,
                "ordered_subcampaign_ids": full_ids,
                "planned_bundles": 282,
            },
            "core_claim_subset_if_lead_rejects_optional_cost_before_command_00": {
                "selected_for_this_frozen_plan": False,
                "ordered_subcampaign_ids": core_ids,
                "planned_bundles": 222,
                "claim_caps": [
                    "No direct AP-2 long-prompt or long-decode request floor rows.",
                    "No short-prefill comparative L2/L3 floor row.",
                ],
            },
        },
        "cells": cells,
        "neg8_daily_reference": {
            "condition_family_id": "df-rq-mid",
            "start_bundle_id": "p2015-neg8-reference-start",
            "end_bundle_id": "p2015-neg8-reference-end",
            "session_id_is_blocking_factor": True,
        },
        "unavailable_cells": [
            {
                "cell_id": "df-telem-onoff-current-hardware",
                "df_rows": ["DF-TELEM-ONOFF"],
                "status": "not_runnable_from_existing_machinery",
                "reason": (
                    "BenchmarkConfig has no extra-sampler field and the powermetrics adapter "
                    "uses a process-global fixed sampler set without tasks."
                ),
                "floor_output": "unknown",
            }
        ],
        "runs_dir": RUNS_DIR,
        "order_manifest": "order_manifest.json",
        "campaign_log": f"{RUNS_DIR}/campaign_log.jsonl",
    }
    plan_bytes = render_json(plan)
    plan_sha256 = hashlib.sha256(plan_bytes).hexdigest()
    (OUT / "calibration_plan.json").write_bytes(plan_bytes)
    (OUT / "calibration_plan.sha256").write_text(
        f"{plan_sha256}  calibration_plan.json\n", encoding="utf-8"
    )

    root_entries: list[dict[str, Any]] = []
    root_index = 1
    for campaign in subcampaigns:
        directory = OUT / campaign["subcampaign_id"]
        directory.mkdir(parents=True, exist_ok=True)
        local_entries = []
        for local_index, run in enumerate(campaign["runs"], start=1):
            config = config_for(run, plan_sha256)
            write_json(directory / run["filename"], config)
            local_entries.append(
                manifest_entry(run, local_index, config=run["filename"])
            )
            root_entries.append(
                manifest_entry(
                    run,
                    root_index,
                    config=f"{campaign['subcampaign_id']}/{run['filename']}",
                )
            )
            root_index += 1
        leaf_manifest = {
            "schema_version": ORDER_SCHEMA,
            "manifest_id": f"p2-015-{campaign['subcampaign_id']}-order-v1",
            "plan_id": PLAN_ID,
            "calibration_plan_sha256": plan_sha256,
            "ordering_note": campaign["ordering_note"],
            "planned_n_bundles": len(local_entries),
            "executed_order": local_entries,
        }
        write_json(directory / "order_manifest.json", leaf_manifest)

    root_manifest = {
        "schema_version": ORDER_SCHEMA,
        "manifest_id": "p2-015-window-a-expanded-order-v1",
        "plan_id": PLAN_ID,
        "calibration_plan_sha256": plan_sha256,
        "planned_n_bundles": len(root_entries),
        "subcampaign_order": [
            {
                "index": index,
                "subcampaign_id": campaign["subcampaign_id"],
                "role": campaign["role"],
                "optional": campaign["optional"],
                "planned_n_bundles": len(campaign["runs"]),
                "ordering_note": campaign["ordering_note"],
            }
            for index, campaign in enumerate(subcampaigns, start=1)
        ],
        "unavailable_gap": {
            "subcampaign_id": "10_df_telem_onoff_unavailable",
            "df_row": "DF-TELEM-ONOFF",
            "planned_n_blocks_if_implemented": 10,
            "planned_n_bundles_if_implemented": 40,
            "status": "not_in_executed_order",
        },
        "executed_order": root_entries,
    }
    write_json(OUT / "order_manifest.json", root_manifest)

    unavailable = OUT / "10_df_telem_onoff_unavailable"
    unavailable.mkdir(parents=True, exist_ok=True)
    (unavailable / "README.md").write_text(
        "# DF-TELEM-ONOFF unavailable\n\n"
        "No runnable config is emitted here. The current config schema cannot select "
        "the extra `tasks` sampler, and the powermetrics adapter uses the fixed sampler "
        "set `cpu_power,gpu_power,ane_power,thermal`. Running a normal-telemetry alias "
        "as B would not measure telemetry perturbation. The current-hardware layer and "
        "C-015/R2 smoke therefore remain unsatisfied; its floor is `unknown`.\n",
        encoding="utf-8",
    )
    print(
        f"generated {len(root_entries)} runnable configs across {len(subcampaigns)} "
        f"subcampaigns; calibration_plan_sha256={plan_sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
