"""Validate and expand the gpukit campaign format until the runner lane lands.

Matrices contain planning inputs, never measured throughput or admission rules.
Validation returns flags; callers retain malformed campaigns in their receipts.
"""

from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, get_args

from joulewise.align.records import Condition, Visibility

SCHEMA = "joulewise.align.gpukit.matrix.v2"
# budget/conditions.py default_conditions at 58750718f; keep effort labels local.
BUDGET_CONDITIONS = ("thinking_on", "thinking_off", "concise", "budget_1", "budget_0.6",
                     "budget_0.4", "budget_0.3", "deletion_1", "deletion_0.6",
                     "deletion_0.4", "deletion_0.3")


@dataclass(frozen=True)
class Run:
    model: str
    task_pair: str
    condition: str
    seed: int


def expand(matrix: Mapping[str, Any]) -> tuple[Run, ...]:
    """Expand requested trial rows; budget calibration/pairs are separate work."""
    return tuple(Run(m["id"], task, condition, seed)
                 for m, task, condition, seed in itertools.product(
                     matrix["models"], matrix["tasks"], matrix["conditions"], matrix["seeds"]))


def _citation(value: Any) -> bool:
    """Require a dated public source for a claimed physical or measured value."""
    return (isinstance(value, Mapping) and isinstance(value.get("url"), str)
            and value["url"].startswith("https://") and bool(value.get("accessed"))
            and bool(value.get("quote") or value.get("note")))


def numeric_provenance(matrix: Mapping[str, Any]) -> tuple[str, ...]:
    """Require each numeric input's sibling citation or formula referencing sources."""
    flags: list[str] = []

    def walk(value: Any, path: str) -> None:
        if not isinstance(value, Mapping):
            return
        for key, leaf in value.items():
            if key.endswith(("_source", "_derivation")) or key in ("source", "derivation"):
                continue
            where = path + "." + key
            if isinstance(leaf, Mapping):
                walk(leaf, where)
            elif isinstance(leaf, (int, float)) and not isinstance(leaf, bool):
                source = value.get(key + "_source", value.get("source"))
                derivation = value.get(key + "_derivation", value.get("derivation"))
                if not _citation(source) and not (isinstance(derivation, str) and derivation.strip()):
                    flags.append("matrix_numeric_source_missing:" + where)
            elif isinstance(leaf, list):
                for index, item in enumerate(leaf):
                    if isinstance(item, Mapping):
                        walk(item, where + "." + str(index))
    for section in ("workload", "gpu_classes", "model_parameters"):
        walk(matrix.get(section, {}), section)
    return tuple(flags)


def validate(matrix: Mapping[str, Any]) -> tuple[str, ...]:
    """Return format and arithmetic flags without excluding requested rows."""
    flags: list[str] = []
    if matrix.get("schema") != SCHEMA:
        flags.append("matrix_schema_unknown")
    for field in ("models", "tasks", "conditions", "seeds"):
        values = matrix.get(field)
        if not isinstance(values, list) or not values:
            flags.append(f"matrix_{field}_empty_or_invalid")
    try:
        if len({m["id"] for m in matrix["models"]}) != len(matrix["models"]):
            flags.append("matrix_duplicate_models")
        for key in ("tasks", "conditions", "seeds"):
            if len(set(matrix[key])) != len(matrix[key]):
                flags.append(f"matrix_duplicate_{key}")
        if any(type(s) is not int for s in matrix["seeds"]):
            flags.append("matrix_seed_invalid")
        count = len(expand(matrix))
        if type(matrix.get("episode_count")) is not int or count != matrix["episode_count"]:
            flags.append("matrix_episode_count_mismatch")
        if matrix["kind"] not in ("shade", "moe_stage_a", "budget"):
            flags.append("matrix_kind_unknown")
        allowed = BUDGET_CONDITIONS if matrix["kind"] == "budget" else get_args(Condition)
        if not set(matrix["conditions"]) <= set(allowed):
            flags.append("matrix_conditions_invalid")
        if not set(matrix["monitor_visibilities"]) <= set(get_args(Visibility)):
            flags.append("matrix_monitor_visibilities_invalid")
        for model in matrix["models"]:
            if type(model.get("tensor_parallel_size", 1)) is not int or model.get("tensor_parallel_size", 1) < 1:
                flags.append("matrix_tensor_parallel_size_invalid")
            if model.get("weight_precision", "bf16") not in ("bf16", "fp8"):
                flags.append("matrix_weight_precision_invalid")
        for key in ("prefill_tokens", "decode_tokens", "tool_wait_s", "host_overhead_s",
                    "monitor_prefill_tokens", "monitor_decode_tokens"):
            value = matrix["workload"][key]
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                flags.append(f"matrix_workload_invalid:{key}")
        if not matrix["workload"]["source"]:
            flags.append("matrix_workload_source_missing")
        for gpu, profile in matrix["gpu_classes"].items():
            for key in ("setup_s", "model_load_s", "router_overhead_fraction"):
                value = profile[key]
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                    flags.append(f"matrix_gpu_parameter_invalid:{gpu}:{key}")
            if type(profile["gpu_count"]) is not int or profile["gpu_count"] < 1:
                flags.append(f"matrix_gpu_count_invalid:{gpu}")
            for key in ("memory_bandwidth_bytes_s", "dense_bf16_flops_s", "memory_bytes"):
                datum = profile["hardware"][key]
                value = datum["value"]
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                          or not math.isfinite(value) or value <= 0):
                    flags.append(f"matrix_hardware_invalid:{gpu}:{key}")
                if value is not None and not _citation(datum["source"]):
                    flags.append(f"matrix_hardware_source_missing:{gpu}:{key}")
            for model in [m["id"] for m in matrix["models"]]:
                rate = profile["throughput"][model]
                efficiency = rate["efficiency"]
                if efficiency is not None:
                    if (isinstance(efficiency, bool) or not isinstance(efficiency, (int, float))
                            or not math.isfinite(efficiency) or not 0 < efficiency <= 1):
                        flags.append(f"matrix_throughput_efficiency_invalid:{gpu}:{model}")
                    if not _citation(rate["efficiency_source"]):
                        flags.append(f"matrix_throughput_efficiency_source_missing:{gpu}:{model}")
                if not rate["source"]:
                    flags.append(f"matrix_throughput_source_missing:{gpu}:{model}")
                params = matrix["model_parameters"][model]
                values = [params[key] for key in ("total_parameters", "active_parameters")]
                for value in values:
                    if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                              or not math.isfinite(value) or value <= 0):
                        flags.append(f"matrix_model_parameters_invalid:{model}")
                if all(isinstance(v, (int, float)) for v in values) and values[1] > values[0]:
                    flags.append(f"matrix_active_exceeds_total:{model}")
                if any(v is not None for v in values) and not _citation(params["source"]):
                    flags.append(f"matrix_model_source_missing:{model}")
        if type(matrix["sampling"]["interval_ns"]) is not int or matrix["sampling"]["interval_ns"] <= 0:
            flags.append("matrix_sample_interval_invalid")
        if matrix["kind"] == "budget":
            spec = matrix["budget"]
            if type(spec["calibration_repetitions"]) is not int or spec["calibration_repetitions"] < 1:
                flags.append("matrix_calibration_repetitions_invalid")
            if not set(spec["live_conditions"]) <= set(matrix["conditions"]):
                flags.append("matrix_live_conditions_invalid")
            if len(spec["live_conditions"]) != len(set(spec["live_conditions"])):
                flags.append("matrix_live_conditions_duplicate")
            if spec["paired_generations"] != 2:
                flags.append("matrix_paired_generation_contract_mismatch")
        item_seeds = len(matrix["tasks"]) * len(matrix["seeds"])
        if matrix["kind"] == "budget":
            spec = matrix["budget"]
            measured = len(matrix["models"]) * (
                len(matrix["tasks"]) * spec["calibration_repetitions"]
                + item_seeds * len(spec["live_conditions"]) * spec["paired_generations"])
            monitor_calls = count
        else:
            measured = count
            monitor_calls = count * len(matrix["monitor_visibilities"])
        if matrix.get("measured_episode_count") != measured:
            flags.append("matrix_measured_episode_count_mismatch")
        if matrix.get("monitor_call_count") != monitor_calls:
            flags.append("matrix_monitor_call_count_mismatch")
    except (KeyError, TypeError, ValueError, OverflowError):
        flags.append("matrix_required_field_invalid")
    flags.extend(numeric_provenance(matrix))
    return tuple(sorted(set(flags)))


def load_matrix(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Read a matrix and return all validation flags; I/O failures remain visible."""
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            return {}, ("matrix_not_object",)
        return value, validate(value)
    except (OSError, ValueError) as exc:
        return {}, (f"matrix_read_failed:{type(exc).__name__}",)
