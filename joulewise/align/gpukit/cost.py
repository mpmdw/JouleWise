"""Cited work bounds, per-model layouts and explicitly priced calibration plans.

Unknown production volumes leave bounds unavailable. Off-box monitor/judge token
work never enters the measured GPU calculation. Rental prices are operator inputs.
"""

from __future__ import annotations

import argparse
import copy
import re
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from joulewise.align.gpukit.identity import model_identity_matches
from joulewise.align.gpukit.matrix import load_matrix, validate
from joulewise.align.gpukit.throughput import ceilings, display_number
from joulewise.align.records import read_episodes


@dataclass(frozen=True)
class Estimate:
    gpu_class: str
    trial_rows: int
    measured_episodes: int
    monitor_calls: int
    lower_bound_wall_seconds: float | None
    lower_bound_gpu_hours: float | None
    lower_bound_total_usd: float | None
    wall_seconds: float | None
    gpu_hours: float | None
    usd_per_gpu_hour: float | None
    total_usd: float | None
    flags: tuple[str, ...]
    model_load_count: int = 0
    monitor_gpu_hours: float | None = None
    monitor_total_usd: float | None = None
    generation_wall_seconds: float | None = None
    calibration_basis: dict[str, Any] = field(default_factory=dict)
    layouts: tuple[dict[str, Any], ...] = ()
    layout_alternatives: tuple[dict[str, Any], ...] = ()
    monitor_usd_per_gpu_hour: float | None = None


def work_counts(matrix: Mapping[str, Any]) -> dict[str, tuple[int, int]]:
    """Per model: fresh Episodes (not calls/Turns), and off-box monitor calls.

    budget/run.py at 58750718f calibrates each item once per repetition, without
    pairing or monitoring. Seven live conditions each generate hinted/no-hint;
    four deletion views reuse thinking_on. Each of eleven trial views is scored.
    A forced reasoning+answer pair is two Turns inside ONE generation Episode.
    """
    item_seeds = len(matrix["tasks"]) * len(matrix["seeds"])
    if matrix["kind"] == "budget":
        spec = matrix["budget"]
        episodes = (len(matrix["tasks"]) * spec["calibration_repetitions"]
                    + item_seeds * len(spec["live_conditions"]) * spec["paired_generations"])
        monitors = item_seeds * len(matrix["conditions"])
    else:
        episodes = item_seeds * len(matrix["conditions"])
        monitors = episodes * len(matrix["monitor_visibilities"])
    return {m["id"]: (episodes, monitors) for m in matrix["models"]}


def memory_fit(matrix: Mapping[str, Any], gpu_class: str,
               model: Mapping[str, Any]) -> dict[str, Any]:
    """Weight-only arithmetic, with separately supplied KV/allocator headroom."""
    parameters = matrix["model_parameters"][model["id"]]["total_parameters"]
    memory = matrix["gpu_classes"][gpu_class]["hardware"]["memory_bytes"]["value"]
    devices = model.get("tensor_parallel_size", 1)
    precision = model.get("weight_precision", "bf16")
    # BF16=16/8=2 bytes; FP8=8/8=1. Scales, activations and KV are NOT free:
    # the explicit headroom includes these, or the fit remains unverified.
    weights = parameters * (2 if precision == "bf16" else 1) if parameters is not None else None
    capacity = memory * devices if memory is not None else None
    remaining = capacity - weights if capacity is not None and weights is not None else None
    headroom = model.get("kv_headroom_bytes")
    return {"model": model["id"], "gpu_count": devices, "weight_precision": precision,
            "weight_bytes": weights, "capacity_bytes": capacity,
            "remaining_bytes": remaining, "kv_headroom_bytes": headroom,
            "fits": remaining >= headroom if remaining is not None and headroom is not None else None,
            "basis": "total_parameters * bytes_per_weight; capacity = cited memory_bytes * per-model tensor_parallel_size"}


def calibration_slice(matrix: Mapping[str, Any]) -> dict[str, Any]:
    """All agent models/pairs/conditions, first seed; retain model and task strata."""
    import copy
    result = copy.deepcopy(dict(matrix))
    result["seeds"] = matrix["seeds"][:1]
    result["name"] = (matrix.get("name") if isinstance(matrix.get("name"), str) else "campaign") + "-calibration"
    result["episode_count"] = len(result["models"]) * len(result["tasks"]) * len(result["conditions"])
    counts = work_counts(result)
    result["measured_episode_count"] = sum(n for n, _ in counts.values())
    result["monitor_call_count"] = sum(n for _, n in counts.values())
    return result


def _calibration(path: Path, counts: Mapping[str, tuple[int, int]]) -> tuple[dict[str, Any], list[str]]:
    flags: list[str] = []
    basis: dict[str, Any] = {}
    try:
        paths = sorted(path.glob("model-*/episodes.jsonl")) if path.is_dir() else [path]
        episodes = [e for file in paths for e in read_episodes(file)]
        for model, (count, _) in counts.items():
            rows = [e for e in episodes if model_identity_matches(e.agent_model, model)]
            if not rows:
                flags.append("calibration_model_missing:" + model)
                continue
            # These are episode brackets (model/tool work), excluding monitor scoring.
            seconds = math.fsum((e.end_ns - e.start_ns) / 1e9 for e in rows) / len(rows)
            basis[model] = {
                "observed_episodes": len(rows), "mean_episode_seconds": seconds,
                "mean_prefill_tokens": math.fsum(e.totals()["prefill_tokens"] for e in rows) / len(rows),
                "mean_decode_tokens": math.fsum(e.totals()["decode_tokens"] for e in rows) / len(rows),
                "projected_episode_seconds": count * seconds,
                "basis": str(path), "flags": sorted({f for e in rows for f in e.flags})}
        flags.append("calibration_extrapolation_not_a_bound")
        # Episode JSON alone cannot establish paid setup/load/monitor-wait time.
        flags.append("calibration_setup_load_and_offbox_waits_unavailable")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        flags.append("calibration_unreadable:" + type(exc).__name__)
    return basis, flags


def _unsourced_inputs(matrix: Mapping[str, Any], flags: list[str]) -> dict[str, Any]:
    """Mask only unsourced numerical inputs, preserving independent figures."""
    result = copy.deepcopy(dict(matrix))
    paths = {f.removeprefix("matrix_numeric_source_missing:") for f in flags
             if f.startswith("matrix_numeric_source_missing:")}
    for flag in tuple(flags):
        if flag.startswith("matrix_throughput_efficiency_source_missing:"):
            gpu, model = flag.removeprefix("matrix_throughput_efficiency_source_missing:").split(":", 1)
            paths.add(f"gpu_classes.{gpu}.throughput.{model}.efficiency")
        elif flag.startswith("matrix_hardware_source_missing:"):
            gpu, key = flag.removeprefix("matrix_hardware_source_missing:").split(":", 1)
            paths.add(f"gpu_classes.{gpu}.hardware.{key}.value")
        elif flag.startswith("matrix_model_source_missing:"):
            model = flag.removeprefix("matrix_model_source_missing:")
            for key in ("total_parameters", "active_parameters"):
                paths.add(f"model_parameters.{model}.{key}")

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, leaf in value.items():
                where = path + "." + key if path else key
                if where in paths and leaf is not None:
                    value[key] = None
                    flags.append("planning_input_unsourced:" + where)
                else:
                    walk(leaf, where)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, path + "." + str(index))
    walk(result, "")
    # Decode weights depend on the cited dimensions/counts in this same row.
    # A syntactically valid formula cannot resurrect an unsourced operand.
    parameters = result.get("model_parameters")
    for model, params in (parameters.items() if isinstance(parameters, dict) else ()):
        if not isinstance(params, dict):
            continue
        for key, value in tuple(params.items()):
            derivation = params.get(key + "_derivation")
            if isinstance(value, (int, float)) and isinstance(derivation, str):
                missing = any(other != key and operand is None and
                              re.search(r"(?<!\w)" + re.escape(other) + r"(?!\w)", derivation)
                              for other, operand in params.items())
                if missing:
                    params[key] = None
                    flags.append(f"planning_input_unsourced:model_parameters.{model}.{key}")
    return result


def estimate(matrix: Mapping[str, Any], gpu_class: str, *,
             usd_per_gpu_hour: float | None = None, calibration: Path | None = None,
             monitor_placement: str = "none",
             monitor_usd_per_gpu_hour: float | None = None) -> Estimate:
    """Compute agent-only bounds/plans; an extra monitor GPU has its own line."""
    flags = list(validate(matrix))
    matrix = _unsourced_inputs(matrix, flags)
    price = usd_per_gpu_hour
    if price is None:
        flags.append("price_not_supplied")
    elif isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price < 0:
        flags.append("price_invalid")
        price = None
    if gpu_class not in matrix.get("gpu_classes", {}):
        flags.append("gpu_class_unknown")
    def blocks_cost(flag: str) -> bool:
        if "_source_missing" in flag or flag in {
                "matrix_episode_count_mismatch", "matrix_measured_episode_count_mismatch",
                "matrix_monitor_call_count_mismatch"}:
            return False
        return flag.startswith(("matrix_", "gpu_class_"))
    if any(blocks_cost(f) for f in flags):
        return Estimate(gpu_class, matrix.get("episode_count", 0), 0, 0,
                        None, None, None, None, None, price, None, tuple(sorted(set(flags))),
                        monitor_usd_per_gpu_hour=monitor_usd_per_gpu_hour)
    gpu, work = matrix["gpu_classes"][gpu_class], matrix["workload"]
    counts = work_counts(matrix)
    layouts = tuple(memory_fit(matrix, gpu_class, m) for m in matrix["models"])
    alternatives = tuple(
        {**memory_fit(matrix, gpu_class, {**model, **option}),
         "checkpoint": option.get("checkpoint", model["id"]),
         "derivation": option.get("derivation", "")}
        for model in matrix["models"] for option in model.get("layout_options", ()))
    for layout in layouts:
        if layout["remaining_bytes"] is not None and layout["remaining_bytes"] < 0:
            flags.append("model_bf16_weights_exceed_device_memory:" + layout["model"])
        if layout["fits"] is None:
            flags.append("model_kv_headroom_not_supplied:" + layout["model"])
        elif not layout["fits"]:
            flags.append("model_memory_layout_insufficient:" + layout["model"])
    bound_available = plan_available = True
    bounds, plans, lower_hours, plan_hours = [], [], [], []
    for model in matrix["models"]:
        name, devices = model["id"], model.get("tensor_parallel_size", 1)
        episodes = counts[name][0]
        ceiling = ceilings(matrix, gpu_class, name)
        if ceiling is None:
            flags.append("throughput_source_unavailable")
            bound_available = plan_available = False
            continue
        if model.get("weight_precision", "bf16") != "bf16":
            flags.append("fp8_compute_bound_unavailable:" + name)
            bound_available = plan_available = False
            continue
        if work["prefill_tokens"] is None or work["decode_tokens"] is None:
            flags.append("workload_token_volumes_unavailable:prefill_tokens,decode_tokens")
            bound_available = plan_available = False
            continue
        # Optimistically aggregate N GPUs' FLOP/s and bandwidth for the lower
        # bound. This is NOT a claimed TP speedup or usable throughput estimate.
        bound = episodes * (work["prefill_tokens"] / ceiling[0] + work["decode_tokens"] / ceiling[1]) / devices
        bounds.append(bound)
        lower_hours.append(bound * devices / 3600)
        rate = gpu["throughput"][name]
        efficiency = rate["efficiency"]
        if efficiency is None:
            flags.append("throughput_efficiency_not_supplied")
            plan_available = False
            continue
        missing = [k for k in ("tool_wait_s", "host_overhead_s") if work[k] is None]
        missing += [k for k in ("setup_s", "model_load_s", "router_overhead_fraction") if gpu[k] is None]
        if missing:
            flags.extend("planning_input_unavailable:" + k for k in missing)
            plan_available = False
            continue
        plan = bound / efficiency + episodes * (work["tool_wait_s"] + work["host_overhead_s"])
        if matrix["kind"] == "moe_stage_a":
            plan *= 1 + gpu["router_overhead_fraction"]
        # Exactly one load per agent model. No monitor/model swaps.
        plan += gpu["model_load_s"]
        plans.append(plan)
        plan_hours.append(plan * devices / 3600)
    for k in ("setup_s", "model_load_s", "router_overhead_fraction"):
        if gpu[k] is None:
            flags.append("planning_input_unavailable:" + k)
            plan_available = False
    for key in ("prefill_tokens", "decode_tokens", "tool_wait_s", "host_overhead_s"):
        if work[key] is None:
            flags.append("planning_input_unavailable:" + key)
    # Null token volumes take precedence over efficiency: both are missing inputs.
    if any(gpu["throughput"][m]["efficiency"] is None for m in counts):
        flags.append("throughput_efficiency_not_supplied")
    lower = math.fsum(bounds) if bound_available else None
    lh = math.fsum(lower_hours) if bound_available else None
    seconds = math.fsum(plans) + gpu["setup_s"] if plan_available else None
    # A whole box holds every allocated measured GPU across serial model runs.
    # Idle held devices still bill. Each model also has its active-device layout.
    held = max(m.get("tensor_parallel_size", 1) for m in matrix["models"])
    hours = seconds * held / 3600 if seconds is not None else None
    basis, generation_seconds = {}, None
    if calibration is not None:
        basis, calibration_flags = _calibration(Path(calibration), counts)
        flags.extend(calibration_flags)
        if matrix["kind"] == "budget":
            flags.append("budget_calibration_strata_unavailable")
            for row in basis.values():
                row["projected_episode_seconds"] = None
        elif len(basis) == len(counts):
            generation_seconds = math.fsum(b["projected_episode_seconds"] for b in basis.values())
        # No invented setup/load allowance turns an episode extrapolation into a
        # complete rental plan. Operator timeout bounds cover this paid pilot.
    monitor_hours = seconds / 3600 if monitor_placement == "gpu" and seconds is not None else None
    monitor_total = (monitor_hours * monitor_usd_per_gpu_hour
                     if monitor_hours is not None and monitor_usd_per_gpu_hour is not None else None)
    # These static missing-input labels describe the committed template. This
    # estimate has evaluated the selected GPU's efficiencies and agent token
    # volumes above; preserve that current verdict instead of stale labels.
    evaluated_input_flags = {"throughput_efficiency_not_supplied",
                             "workload_token_volumes_unavailable"}
    flags.extend(f for f in matrix.get("flags", ()) if f not in evaluated_input_flags)
    flags.append("provisional_single_stream_bf16_bound")
    return Estimate(gpu_class, matrix["episode_count"], sum(n for n, _ in counts.values()),
                    sum(n for _, n in counts.values()), lower, lh,
                    lh * price if lh is not None and price is not None else None,
                    seconds, hours, price, hours * price if hours is not None and price is not None else None,
                    tuple(sorted(set(flags))), len(counts), monitor_hours, monitor_total,
                    generation_seconds, basis, layouts, alternatives, monitor_usd_per_gpu_hour)


def printable(result: Estimate) -> dict[str, Any]:
    """Derived figures use two significant digits; input prices/counts stay exact."""
    output = asdict(result)
    for key in ("lower_bound_wall_seconds", "lower_bound_gpu_hours", "lower_bound_total_usd",
                "wall_seconds", "gpu_hours", "total_usd",
                "monitor_gpu_hours", "monitor_total_usd", "generation_wall_seconds"):
        output[key] = display_number(output[key], lower_bound=key.startswith("lower_bound_"))
    def rounded(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: rounded(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [rounded(v) for v in value]
        return display_number(value) if type(value) is float else value
    output["calibration_basis"] = rounded(output["calibration_basis"])
    output["layouts"] = rounded(output["layouts"])
    output["layout_alternatives"] = rounded(output["layout_alternatives"])
    output["lower_bound_status"] = "available" if result.lower_bound_wall_seconds is not None else "unavailable"
    output["plan_status"] = "available" if result.wall_seconds is not None else "unavailable"
    output["rounding"] = "Derived figures: two significant digits; lower bounds downward; input prices and integer counts/bytes exact."
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--gpu-class", required=True)
    parser.add_argument("--usd-per-gpu-hour", type=float)
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--monitor-placement", choices=("external", "gpu", "none"), default="none")
    parser.add_argument("--monitor-usd-per-gpu-hour", type=float)
    args = parser.parse_args(argv)
    matrix, flags = load_matrix(args.matrix)
    if not matrix:
        print(json.dumps({"flags": flags, "total_usd": None}))
        return 0
    result = estimate(matrix, args.gpu_class, usd_per_gpu_hour=args.usd_per_gpu_hour,
                      calibration=args.calibration, monitor_placement=args.monitor_placement,
                      monitor_usd_per_gpu_hour=args.monitor_usd_per_gpu_hour)
    print(json.dumps(printable(result), indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
