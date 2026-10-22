"""Serial BF16 work bounds and optional planning costs from cited inputs.

A roofline lower bound is not a rental budget. Planning requires a cited
efficiency; prices are always supplied by the operator.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from joulewise.align.gpukit.matrix import load_matrix, validate
from joulewise.align.gpukit.throughput import ceilings, display_number


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


def work_counts(matrix: Mapping[str, Any]) -> dict[str, tuple[int, int]]:
    """Map agent model to (generation episodes, monitor calls).

    Budget deletion controls reuse the thinking-on generation. Calibration is
    per item/model, independent of trial seeds. Each live trial has a hinted
    and no-hint generation; each trial row, including deletion, has a monitor.
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
    return {model["id"]: (episodes, monitors) for model in matrix["models"]}


def estimate(matrix: Mapping[str, Any], gpu_class: str, *,
             usd_per_gpu_hour: float | None = None) -> Estimate:
    """Return full-precision bounds and, with sourced efficiencies, a plan.

    Serial single-stream inference is assumed, with one resident model on one
    GPU. gpu_count multiplies billing only; no tensor-parallel speedup is implied.
    Setup, loads, waits and router overhead enter only the planning calculation.
    """
    flags = list(validate(matrix))
    price = usd_per_gpu_hour
    if price is None:
        flags.append("price_not_supplied")
    elif isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price < 0:
        flags.append("price_invalid")
        price = None
    if gpu_class not in matrix.get("gpu_classes", {}):
        flags.append("gpu_class_unknown")
    if any(f.startswith(("matrix_", "gpu_class_")) for f in flags):
        return Estimate(gpu_class, matrix.get("episode_count", 0), 0, 0,
                        None, None, None, None, None, price, None, tuple(sorted(set(flags))))
    gpu, work = matrix["gpu_classes"][gpu_class], matrix["workload"]
    counts = work_counts(matrix)
    bounds: list[float] = []
    plans: list[float] = []
    bound_available = True
    plan_available = True

    def duration(model: str, prefill: float, decode: float) -> tuple[float, float]:
        nonlocal bound_available, plan_available
        ceiling = ceilings(matrix, gpu_class, model)
        if ceiling is None:
            flags.append("throughput_source_unavailable")
            bound_available = plan_available = False
            return 0.0, 0.0
        prefill_tps, decode_tps = ceiling
        bound = prefill / prefill_tps + decode / decode_tps
        rate = gpu["throughput"][model]
        efficiency = rate["efficiency"]
        if efficiency is None:
            flags.append("throughput_efficiency_not_supplied")
            plan_available = False
            return bound, 0.0
        return bound, bound / efficiency

    monitor_calls = 0
    for model, (episodes, monitors) in counts.items():
        total = matrix["model_parameters"][model]["total_parameters"]
        memory = gpu["hardware"]["memory_bytes"]["value"]
        # Fit uses total resident BF16 weights, not the MoE active subset.
        # Two bytes/weight is a physical storage conversion, before KV/allocator use.
        if total is not None and memory is not None and 2 * total > memory:
            flags.append("model_bf16_weights_exceed_device_memory:" + model)
        bound, plan = duration(model, work["prefill_tokens"], work["decode_tokens"])
        bounds.append(episodes * bound)
        plan += work["tool_wait_s"] + work["host_overhead_s"]
        if matrix["kind"] == "moe_stage_a":
            plan *= 1 + gpu["router_overhead_fraction"]
        plans.append(episodes * plan)
        monitor_calls += monitors
    # Monitor/judge execute off the measured GPU; never bill their tokens here.
    # Serial swap policy is an explicit planning parameter, not a physical bound.
    plans.extend((gpu["setup_s"], len(counts) * gpu["model_load_s"]))
    lower = math.fsum(bounds) if bound_available else None
    seconds = math.fsum(plans) if plan_available else None
    # 3600 seconds/hour; all allocated GPUs accrue the same serial wall time.
    hours = seconds / 3600 * gpu["gpu_count"] if seconds is not None else None
    lower_hours = lower / 3600 * gpu["gpu_count"] if lower is not None else None
    flags.extend(matrix.get("flags", ()))
    # Config flags describe missing defaults; evaluate actual supplied inputs.
    if plan_available:
        flags = [f for f in flags if f != "throughput_efficiency_not_supplied"]
    flags.append("provisional_single_stream_bf16_bound")
    return Estimate(gpu_class, matrix["episode_count"],
                    sum(n for n, _ in counts.values()), monitor_calls, lower, lower_hours,
                    lower_hours * price if lower_hours is not None and price is not None else None,
                    seconds, hours, price, hours * price if hours is not None and price is not None else None,
                    tuple(sorted(set(flags))))


def printable(result: Estimate) -> dict[str, Any]:
    """Render derived times/hours/costs at the two-digit input precision."""
    output = asdict(result)
    for key in ("lower_bound_wall_seconds", "lower_bound_gpu_hours", "lower_bound_total_usd",
                "wall_seconds", "gpu_hours", "total_usd"):
        output[key] = display_number(output[key], lower_bound=key.startswith("lower_bound_"))
    output["rounding"] = "Two significant digits; lower bounds downward, planning values nearest."
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--gpu-class", required=True)
    parser.add_argument("--usd-per-gpu-hour", type=float)
    args = parser.parse_args(argv)
    matrix, flags = load_matrix(args.matrix)
    if not matrix:
        print(json.dumps({"flags": flags, "total_usd": None}))
        return 0
    result = estimate(matrix, args.gpu_class, usd_per_gpu_hour=args.usd_per_gpu_hour)
    print(json.dumps(printable(result), indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
