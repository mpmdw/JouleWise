#!/usr/bin/env python3
"""Deterministically generate a floor campaign from one campaign specification.

The default specification reproduces the frozen P2-015 Window-A assembly.  A
different model, repetition count, workload size, block order, suite reference,
or run-ID prefix is supplied by changing the specification, not this module.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DEFAULT_SPEC = OUT / "campaign_spec.json"
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
SPEC_SCHEMA = "joulewise.campaign_spec.v1"
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class CampaignSpecError(ValueError):
    """The campaign specification cannot produce a governed assembly."""


@dataclass(frozen=True)
class CampaignSpec:
    path: Path
    value: Mapping[str, Any]

    @property
    def campaign(self) -> Mapping[str, Any]:
        return self.value["campaign"]

    @property
    def model(self) -> Mapping[str, Any]:
        return self.value["model"]

    @property
    def hardware(self) -> Mapping[str, Any]:
        return self.value["hardware_target"]

    @property
    def n(self) -> int:
        return self.campaign["n"]

    @property
    def run_id_prefix(self) -> str:
        return self.campaign["run_id_prefix"]

    @property
    def model_tag(self) -> str:
        return self.model["tag"]

    @property
    def plan_id(self) -> str:
        return "-".join(
            (
                self.campaign["campaign_id"],
                self.hardware["plan_tag"],
                self.model["plan_tag"],
                self.campaign["plan_revision"],
            )
        )

    @property
    def profiles(self) -> Mapping[str, Mapping[str, Any]]:
        return self.value["profiles"]

    @property
    def block_pattern(self) -> Sequence[Mapping[str, str]]:
        return self.value["block_pattern"]


def _require_keys(value: object, keys: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CampaignSpecError(f"{where}: expected an object")
    if set(value) != keys:
        raise CampaignSpecError(
            f"{where}: expected keys {sorted(keys)}, got {sorted(value)}"
        )
    return value


def _identifier(value: object, where: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise CampaignSpecError(f"{where}: invalid identifier")
    return value


def load_campaign_spec(path: Path) -> CampaignSpec:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except OSError as exc:
        raise CampaignSpecError(f"cannot read campaign specification {path}: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CampaignSpecError(f"{path}: invalid UTF-8 JSON: {exc}") from exc
    root = _require_keys(
        value,
        {
            "schema_version",
            "campaign",
            "model",
            "quantization",
            "hardware_target",
            "sampling",
            "suite_manifest",
            "block_pattern",
            "profiles",
        },
        "campaign_spec",
    )
    if root["schema_version"] != SPEC_SCHEMA:
        raise CampaignSpecError(f"campaign_spec.schema_version: expected {SPEC_SCHEMA!r}")
    campaign = _require_keys(
        root["campaign"],
        {"campaign_id", "plan_revision", "run_id_prefix", "runs_dir", "n"},
        "campaign_spec.campaign",
    )
    for key in ("campaign_id", "plan_revision", "run_id_prefix"):
        _identifier(campaign[key], f"campaign_spec.campaign.{key}")
    if not isinstance(campaign["runs_dir"], str) or not campaign["runs_dir"].strip():
        raise CampaignSpecError("campaign_spec.campaign.runs_dir: expected nonempty text")
    if isinstance(campaign["n"], bool) or not isinstance(campaign["n"], int) or campaign["n"] < 1:
        raise CampaignSpecError("campaign_spec.campaign.n: expected a positive integer")

    model = _require_keys(root["model"], {"tag", "plan_tag", "config"}, "campaign_spec.model")
    _identifier(model["tag"], "campaign_spec.model.tag")
    _identifier(model["plan_tag"], "campaign_spec.model.plan_tag")
    model_config = _require_keys(
        model["config"],
        {"name", "family", "source", "revision", "weight_format", "context_window"},
        "campaign_spec.model.config",
    )
    for key in ("name", "family", "source", "revision", "weight_format"):
        if not isinstance(model_config[key], str) or not model_config[key].strip():
            raise CampaignSpecError(f"campaign_spec.model.config.{key}: expected nonempty text")
    if (
        isinstance(model_config["context_window"], bool)
        or not isinstance(model_config["context_window"], int)
        or model_config["context_window"] < 1
    ):
        raise CampaignSpecError("campaign_spec.model.config.context_window: expected a positive integer")

    hardware = _require_keys(
        root["hardware_target"], {"plan_tag", "config"}, "campaign_spec.hardware_target"
    )
    _identifier(hardware["plan_tag"], "campaign_spec.hardware_target.plan_tag")
    hardware_config = hardware["config"]
    if not isinstance(hardware_config, Mapping) or not hardware_config:
        raise CampaignSpecError("campaign_spec.hardware_target.config: expected a nonempty object")
    for required in ("id", "runtime_backend", "telemetry_backend"):
        if not isinstance(hardware_config.get(required), str) or not hardware_config[required].strip():
            raise CampaignSpecError(
                f"campaign_spec.hardware_target.config.{required}: expected nonempty text"
            )
    for key in ("quantization", "sampling"):
        if not isinstance(root[key], Mapping) or not root[key]:
            raise CampaignSpecError(f"campaign_spec.{key}: expected a nonempty object")
    suite = _require_keys(root["suite_manifest"], {"ref", "sha256"}, "campaign_spec.suite_manifest")
    if not isinstance(suite["ref"], str) or not suite["ref"].strip():
        raise CampaignSpecError("campaign_spec.suite_manifest.ref: expected nonempty text")
    if not isinstance(suite["sha256"], str) or not _SHA_RE.fullmatch(suite["sha256"]):
        raise CampaignSpecError("campaign_spec.suite_manifest.sha256: expected 64 lowercase hex characters")

    pattern = root["block_pattern"]
    if not isinstance(pattern, list) or not pattern:
        raise CampaignSpecError("campaign_spec.block_pattern: expected a nonempty array")
    positions: list[str] = []
    for index, item in enumerate(pattern):
        row = _require_keys(item, {"label", "position"}, f"campaign_spec.block_pattern[{index}]")
        for key in ("label", "position"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise CampaignSpecError(
                    f"campaign_spec.block_pattern[{index}].{key}: expected nonempty text"
                )
        positions.append(row["position"])
    if len(positions) != len(set(positions)):
        raise CampaignSpecError("campaign_spec.block_pattern: duplicate position")

    profiles = root["profiles"]
    if not isinstance(profiles, Mapping) or not profiles:
        raise CampaignSpecError("campaign_spec.profiles: expected a nonempty object")
    for profile_id, profile in profiles.items():
        _identifier(profile_id, f"campaign_spec.profiles[{profile_id!r}]")
        if not isinstance(profile, Mapping):
            raise CampaignSpecError(f"campaign_spec.profiles.{profile_id}: expected an object")
        common = {"name", "df_rows", "metrics", "window_class", "use_role", "cluster_reducer"}
        workload_keys = set(profile) - common
        if workload_keys not in (
            {"prompt_tokens", "output_tokens"},
            {"suite_manifest"},
        ):
            raise CampaignSpecError(
                f"campaign_spec.profiles.{profile_id}: expected prompt/output sizes or suite_manifest=true"
            )
        for key in common:
            if key not in profile:
                raise CampaignSpecError(f"campaign_spec.profiles.{profile_id}: missing {key!r}")
        if workload_keys == {"suite_manifest"}:
            if profile["suite_manifest"] is not True:
                raise CampaignSpecError(
                    f"campaign_spec.profiles.{profile_id}.suite_manifest: expected true"
                )
        else:
            for key in ("prompt_tokens", "output_tokens"):
                number = profile[key]
                if isinstance(number, bool) or not isinstance(number, int) or number < 1:
                    raise CampaignSpecError(
                        f"campaign_spec.profiles.{profile_id}.{key}: expected a positive integer"
                    )
        if not isinstance(profile["df_rows"], list) or not profile["df_rows"]:
            raise CampaignSpecError(f"campaign_spec.profiles.{profile_id}.df_rows: expected a nonempty array")
        if not isinstance(profile["metrics"], list) or not profile["metrics"]:
            raise CampaignSpecError(f"campaign_spec.profiles.{profile_id}.metrics: expected a nonempty array")
    return CampaignSpec(path=path, value=copy.deepcopy(root))


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
    subcampaign: dict[str, Any], condition_ids: list[str], spec: CampaignSpec
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    by_condition: dict[str, list[str]] = {condition_id: [] for condition_id in condition_ids}
    for rep in range(1, spec.n + 1):
        offset = (rep - 1) % len(condition_ids)
        order = condition_ids[offset:] + condition_ids[:offset]
        for position, condition_id in enumerate(order, start=1):
            run_id = f"{spec.run_id_prefix}-{condition_id}-abs-r{rep:02d}"
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
        profile = spec.profiles[condition_id]
        cells.append(
            {
                "cell_id": f"{condition_id}-absolute",
                "df_rows": profile["df_rows"],
                "kind": "absolute",
                "use_role": profile["use_role"],
                "minimum_claim_n": spec.n,
                "window_class": profile["window_class"],
                "metric_selectors": profile["metrics"],
                "condition_family_id": condition_id,
                "cluster_reducer": profile["cluster_reducer"],
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
    spec: CampaignSpec,
) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in range(1, spec.n + 1):
        block_id = f"{comparative_cell_id}-b{block:02d}"
        members = []
        for sequence_index, pattern_member in enumerate(spec.block_pattern, start=1):
            label = pattern_member["label"]
            position = pattern_member["position"]
            run_id = (
                f"{spec.run_id_prefix}-{comparative_cell_id}-"
                f"b{block:02d}-{position.lower()}"
            )
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
                "executed_labels": [member["label"] for member in spec.block_pattern],
                "members": members,
            }
        )
    return {
        "cell_id": comparative_cell_id,
        "df_rows": df_rows,
        "kind": "comparative_abba",
        "use_role": use_role,
        "minimum_claim_n": spec.n,
        "window_class": window_class,
        "metric_selectors": metrics,
        "condition_family_id": condition_id,
        "cluster_reducer": spec.profiles[condition_id]["cluster_reducer"],
        "ordered_blocks": blocks,
    }


def build_assembly(spec: CampaignSpec) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    subcampaigns: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    block_count_text = "Ten" if spec.n == 10 else str(spec.n)
    pattern_text = "/".join(member["label"] for member in spec.block_pattern)

    neg8_start = new_subcampaign(
        "00_neg8_start",
        "NEG-8 fixed daily reference at Window-A start",
        role="neg8_daily_reference_start",
        ordering_note="Fixed first position; scientific condition matches the end reference.",
    )
    add_run(
        neg8_start,
        run_id=f"{spec.run_id_prefix}-neg8-reference-start",
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
    cells.extend(
        add_absolute_round_robin(
            request_abs, ["df-rq-mid", "df-rq-short"], spec
        )
    )
    subcampaigns.append(request_abs)

    phase_abs = new_subcampaign(
        "02_phase_absolute",
        "Prefill, decode, and short-prefill absolute repeats",
        role="absolute_phase",
        ordering_note=(
            f"Three-condition cyclic round-robin rotates the leading condition; n={spec.n} leaves "
            "the predeclared one-position imbalance visible in the manifest."
        ),
    )
    cells.extend(
        add_absolute_round_robin(
            phase_abs,
            ["df-ph-prefill", "df-ph-decode", "df-ph-short-prefill"],
            spec,
        )
    )
    subcampaigns.append(phase_abs)

    request_abba = new_subcampaign(
        "03_request_abba",
        "Same-condition request ABBA blocks",
        role="comparative_request",
        ordering_note=(
            f"{block_count_text} contiguous {pattern_text} blocks; A and B are aliases of df-rq-mid."
        ),
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
            spec=spec,
        )
    )
    subcampaigns.append(request_abba)

    phase_prefill_abba = new_subcampaign(
        "04_phase_prefill_abba",
        "Same-condition prefill-phase ABBA blocks",
        role="comparative_phase_prefill",
        ordering_note=f"{block_count_text} contiguous {pattern_text} blocks over the exact df-ph-prefill profile.",
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
            spec=spec,
        )
    )
    subcampaigns.append(phase_prefill_abba)

    phase_decode_abba = new_subcampaign(
        "05_phase_decode_abba",
        "Same-condition decode-phase ABBA blocks",
        role="comparative_phase_decode",
        ordering_note=f"{block_count_text} contiguous {pattern_text} blocks over the exact df-ph-decode profile.",
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
            spec=spec,
        )
    )
    subcampaigns.append(phase_decode_abba)

    suite_abs = new_subcampaign(
        "06_suite_absolute",
        "Tiny-suite item/level absolute repeats",
        role="absolute_suite",
        ordering_note=(
            f"One frozen five-item same-shape suite condition repeated in {block_count_text.lower()} independent bundles; "
            "items inside a bundle never increase n."
        ),
    )
    cells.extend(add_absolute_round_robin(suite_abs, ["df-su-sentinel"], spec))
    subcampaigns.append(suite_abs)

    suite_abba = new_subcampaign(
        "07_suite_abba",
        "Tiny-suite item/level same-condition ABBA blocks",
        role="comparative_suite",
        ordering_note=f"{block_count_text} contiguous {pattern_text} blocks over the exact frozen suite condition.",
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
            spec=spec,
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
            optional_long_abs,
            ["df-rq-long-prompt", "df-rq-long-decode"],
            spec,
        )
    )
    subcampaigns.append(optional_long_abs)

    optional_short_abba = new_subcampaign(
        "09_optional_short_prefill_abba",
        "Optional short-prefill stress ABBA blocks",
        role="comparative_phase_short_prefill_optional",
        optional=True,
        ordering_note=f"{block_count_text} contiguous {pattern_text} blocks over the exact short-prefill stress profile.",
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
            spec=spec,
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
        run_id=f"{spec.run_id_prefix}-neg8-reference-end",
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


def workload_for(spec: CampaignSpec, condition_id: str) -> dict[str, Any]:
    profile = spec.profiles[condition_id]
    workload: dict[str, Any] = {
        "name": profile["name"],
        "repetitions": 1,
        "warmup_runs": 1,
    }
    if profile.get("suite_manifest") is True:
        workload["suite_manifest_ref"] = spec.value["suite_manifest"]["ref"]
        workload["suite_manifest_sha256"] = spec.value["suite_manifest"]["sha256"]
    else:
        workload["prompt_tokens"] = profile["prompt_tokens"]
        workload["output_tokens"] = profile["output_tokens"]
    return workload


def config_for(
    spec: CampaignSpec,
    run: dict[str, Any],
    plan_sha256: str,
) -> dict[str, Any]:
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
        "model": dict(spec.model["config"]),
        "quantization": dict(spec.value["quantization"]),
        "hardware_target": dict(spec.hardware["config"]),
        "workload_profile": workload_for(spec, run["condition_id"]),
        "interconnect": {"name": "local"},
        "sampling": dict(spec.value["sampling"]),
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": common_tags + run["collection_tags"],
        },
    }


def manifest_entry(
    spec: CampaignSpec,
    run: dict[str, Any],
    index: int,
    *,
    config: str,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "index": index,
        "config": config,
        "run_id": run["run_id"],
        "model_tag": spec.model_tag,
        "rep": run["rep"],
        "workload": run["condition_id"],
        "role": run["role"],
        "block_index": run["block_index"],
        "position_in_block": run["position_in_block"],
    }
    if run["sentinel_position"] is not None:
        entry["sentinel_position"] = run["sentinel_position"]
    return entry


def generate_campaign(spec: CampaignSpec, out_dir: Path) -> tuple[int, str]:
    """Write one deterministic campaign assembly and return count plus plan hash."""

    try:
        subcampaigns, cells = build_assembly(spec)
    except KeyError as exc:
        raise CampaignSpecError(
            f"campaign_spec.profiles: missing generator-required profile {exc.args[0]!r}"
        ) from exc
    full_ids = [campaign["subcampaign_id"] for campaign in subcampaigns]
    core_ids = [
        campaign["subcampaign_id"]
        for campaign in subcampaigns
        if not campaign["optional"]
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "plan_id": spec.plan_id,
        "calibration_scope": "window_a",
        "freeze_status": "frozen_before_measurement",
        "fixed_n": spec.n,
        "stack_scope": {
            "hardware_target": spec.hardware["config"]["id"],
            "runtime_backend": spec.hardware["config"]["runtime_backend"],
            "telemetry_backend": spec.hardware["config"]["telemetry_backend"],
            "model_name": spec.model["config"]["name"],
            "model_revision": spec.model["config"]["revision"],
            "model_source": spec.model["config"]["source"],
            "quantization": spec.value["quantization"]["name"],
            "sampling": dict(spec.value["sampling"]),
            "suite_manifest_ref": spec.value["suite_manifest"]["ref"],
            "suite_manifest_sha256": spec.value["suite_manifest"]["sha256"],
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
                "planned_bundles": sum(len(item["runs"]) for item in subcampaigns),
            },
            "core_claim_subset_if_lead_rejects_optional_cost_before_command_00": {
                "selected_for_this_frozen_plan": False,
                "ordered_subcampaign_ids": core_ids,
                "planned_bundles": sum(
                    len(item["runs"]) for item in subcampaigns if not item["optional"]
                ),
                "claim_caps": [
                    "No direct AP-2 long-prompt or long-decode request floor rows.",
                    "No short-prefill comparative L2/L3 floor row.",
                ],
            },
        },
        "cells": cells,
        "neg8_daily_reference": {
            "condition_family_id": "df-rq-mid",
            "start_bundle_id": f"{spec.run_id_prefix}-neg8-reference-start",
            "end_bundle_id": f"{spec.run_id_prefix}-neg8-reference-end",
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
        "runs_dir": spec.campaign["runs_dir"],
        "order_manifest": "order_manifest.json",
        "campaign_log": f"{spec.campaign['runs_dir']}/campaign_log.jsonl",
    }
    plan_bytes = render_json(plan)
    plan_sha256 = hashlib.sha256(plan_bytes).hexdigest()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "calibration_plan.json").write_bytes(plan_bytes)
    (out_dir / "calibration_plan.sha256").write_text(
        f"{plan_sha256}  calibration_plan.json\n", encoding="utf-8"
    )

    root_entries: list[dict[str, Any]] = []
    root_index = 1
    for campaign in subcampaigns:
        directory = out_dir / campaign["subcampaign_id"]
        directory.mkdir(parents=True, exist_ok=True)
        local_entries = []
        for local_index, run in enumerate(campaign["runs"], start=1):
            config = config_for(spec, run, plan_sha256)
            write_json(directory / run["filename"], config)
            local_entries.append(
                manifest_entry(spec, run, local_index, config=run["filename"])
            )
            root_entries.append(
                manifest_entry(
                    spec,
                    run,
                    root_index,
                    config=f"{campaign['subcampaign_id']}/{run['filename']}",
                )
            )
            root_index += 1
        leaf_manifest = {
            "schema_version": ORDER_SCHEMA,
            "manifest_id": f"p2-015-{campaign['subcampaign_id']}-order-v1",
            "plan_id": spec.plan_id,
            "calibration_plan_sha256": plan_sha256,
            "ordering_note": campaign["ordering_note"],
            "planned_n_bundles": len(local_entries),
            "executed_order": local_entries,
        }
        write_json(directory / "order_manifest.json", leaf_manifest)

    root_manifest = {
        "schema_version": ORDER_SCHEMA,
        "manifest_id": "p2-015-window-a-expanded-order-v1",
        "plan_id": spec.plan_id,
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
            "planned_n_blocks_if_implemented": spec.n,
            "planned_n_bundles_if_implemented": spec.n * len(spec.block_pattern),
            "status": "not_in_executed_order",
        },
        "executed_order": root_entries,
    }
    write_json(out_dir / "order_manifest.json", root_manifest)

    unavailable = out_dir / "10_df_telem_onoff_unavailable"
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
    return len(root_entries), plan_sha256


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--campaign-spec",
        type=Path,
        default=DEFAULT_SPEC,
        help="campaign specification JSON (default: sibling campaign_spec.json)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT,
        help="output directory (default: the frozen P2-015 campaign directory)",
    )
    args = parser.parse_args(argv)
    try:
        spec = load_campaign_spec(args.campaign_spec)
        count, plan_sha256 = generate_campaign(spec, args.out_dir)
    except CampaignSpecError as exc:
        print(f"campaign specification error: {exc}", file=sys.stderr)
        return 2
    print(
        f"generated {count} runnable configs; "
        f"model_tag={spec.model_tag}; plan_id={spec.plan_id}; "
        f"calibration_plan_sha256={plan_sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
