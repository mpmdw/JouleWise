"""Shared constants and deterministic helpers for metrology-v1 generators."""

from __future__ import annotations

from typing import Any


MODEL = {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
    "weight_format": "mlx",
    "context_window": 32768,
}
REFERENCE_MODEL = {
    "name": MODEL["name"],
    "source": MODEL["source"],
    "revision": MODEL["revision"],
}
QUANTIZATION = {"name": "int4", "bits": 4}
MODEL_TAG = "qwen25-1p5b-mlx"
SAMPLING = {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0}

PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"


def hardware(notes: str) -> dict[str, Any]:
    return {
        "id": "macbook_m3_max",
        "transport": "local",
        "runtime_backend": "mlx",
        "telemetry_backend": "powermetrics",
        "device_kind": "apple_silicon_unified_memory",
        "notes": f"{notes}; normal powermetrics sampler set only.",
    }


def workload(prompt_tokens: int, output_tokens: int, *, name: str = "df_ph_decode") -> dict[str, Any]:
    return {
        "name": name,
        "repetitions": 1,
        "warmup_runs": 1,
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
    }


def references() -> dict[str, Any]:
    common = {
        "condition_family_id": "df-rq-mid",
        "model_name": REFERENCE_MODEL["name"],
        "model_revision": REFERENCE_MODEL["revision"],
        "model_source": REFERENCE_MODEL["source"],
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


def replacement_rule() -> dict[str, Any]:
    return {
        "policy": "technical_invalid_same_slot_only",
        "predeclared_before_data": True,
        "outcome_dependent_top_up": "forbidden_and_demotes_contrast_to_exploratory",
    }


def campaign_policy() -> dict[str, Any]:
    return {
        "policy_id": "quiet-mac-p2-production",
        "path": "configs/campaign_policies/quiet_mac_p2_production.json",
        "binding": "operator passes --campaign-policy; no campaign artifact declares it",
    }


def stack_scope(
    condition_hashes: dict[str, str],
    *,
    sampling: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "hardware_target": "macbook_m3_max",
        "runtime_backend": "mlx",
        "telemetry_backend": "powermetrics",
        "model_name": MODEL["name"],
        "model_revision": MODEL["revision"],
        "model_source": MODEL["source"],
        "quantization": "int4",
        "sampling": SAMPLING if sampling is None else sampling,
        "condition_families": [
            {
                "condition_family_id": family_id,
                "condition_family_sha256": condition_hashes[family_id],
            }
            for family_id in sorted(condition_hashes)
        ],
    }


def config_document(
    *,
    run_id: str,
    hardware_target: dict[str, Any],
    workload_profile: dict[str, Any],
    sampling: dict[str, Any],
    campaign_slug: str,
    condition_family_ids: list[str],
    plan_sha256: str,
    collection_tags: list[str],
) -> dict[str, Any]:
    tags = [
        "phase2",
        "metrology-v1",
        campaign_slug,
        "production-window",
        "instrument-characterization",
        *[f"df-condition={family_id}" for family_id in condition_family_ids],
        f"calibration-plan-sha256={plan_sha256}",
        *collection_tags,
    ]
    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "model": MODEL,
        "quantization": QUANTIZATION,
        "hardware_target": hardware_target,
        "workload_profile": workload_profile,
        "interconnect": {"name": "local"},
        "sampling": sampling,
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": tags,
        },
    }
