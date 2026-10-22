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
from typing import Any, Mapping

SCHEMA = "joulewise.align.gpukit.matrix.v1"


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
        for key in ("prefill_tokens", "decode_tokens", "tool_wait_s", "host_overhead_s",
                    "monitor_prefill_tokens", "monitor_decode_tokens"):
            value = matrix["workload"][key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                flags.append(f"matrix_workload_invalid:{key}")
        if not matrix["workload"]["source"]:
            flags.append("matrix_workload_source_missing")
        for gpu, profile in matrix["gpu_classes"].items():
            for key in ("setup_s", "model_load_s", "router_overhead_fraction"):
                value = profile[key]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    flags.append(f"matrix_gpu_parameter_invalid:{gpu}:{key}")
            if type(profile["gpu_count"]) is not int or profile["gpu_count"] < 1:
                flags.append(f"matrix_gpu_count_invalid:{gpu}")
            for model in [m["id"] for m in matrix["models"]] + [matrix["monitor_model"]]:
                rate = profile["throughput"][model]
                for key in ("prefill_tps", "decode_tps"):
                    value = rate[key]
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                        flags.append(f"matrix_throughput_invalid:{gpu}:{model}:{key}")
                if not rate["source"]:
                    flags.append(f"matrix_throughput_source_missing:{gpu}:{model}")
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
