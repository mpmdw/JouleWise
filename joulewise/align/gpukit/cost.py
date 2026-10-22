"""Serial campaign wall time and GPU-hour cost from explicit planning parameters.

No prices are embedded. Output is PROVISIONAL until throughput and overheads
are measured on the approved provider. Missing prices produce flags and nulls.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from joulewise.align.gpukit.matrix import load_matrix, validate


@dataclass(frozen=True)
class Estimate:
    gpu_class: str
    trial_rows: int
    measured_episodes: int
    monitor_calls: int
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
    """Estimate serial on-box time, including local monitor, loads and setup."""
    flags = list(validate(matrix))
    price = usd_per_gpu_hour
    if price is None:
        flags.append("price_not_supplied")
    elif isinstance(price, bool) or not math.isfinite(price) or price < 0:
        flags.append("price_invalid")
        price = None
    if gpu_class not in matrix.get("gpu_classes", {}):
        flags.append("gpu_class_unknown")
    if any(f.startswith(("matrix_", "gpu_class_")) for f in flags):
        return Estimate(gpu_class, matrix.get("episode_count", 0), 0, 0,
                        None, None, price, None, tuple(sorted(set(flags))))
    gpu, work = matrix["gpu_classes"][gpu_class], matrix["workload"]
    counts = work_counts(matrix)
    parts = [gpu["setup_s"]]
    monitor_calls = 0
    for model, (episodes, monitors) in counts.items():
        rate = gpu["throughput"][model]
        duration = (work["prefill_tokens"] / rate["prefill_tps"]
                    + work["decode_tokens"] / rate["decode_tps"]
                    + work["tool_wait_s"] + work["host_overhead_s"])
        if matrix["kind"] == "moe_stage_a":
            duration *= 1 + gpu["router_overhead_fraction"]
        parts.append(episodes * duration)
        monitor_calls += monitors
    monitor_rate = gpu["throughput"][matrix["monitor_model"]]
    parts.append(monitor_calls * (
        work["monitor_prefill_tokens"] / monitor_rate["prefill_tps"]
        + work["monitor_decode_tokens"] / monitor_rate["decode_tps"]))
    # Serial agent/monitor swaps: two loads per model campaign, plus the first
    # agent load. Deliberately parameterized; no overlap or free monitor assumed.
    parts.append((2 * len(counts) + 1) * gpu["model_load_s"])
    seconds = math.fsum(parts)
    hours = seconds / 3600 * gpu["gpu_count"]  # 3600 seconds per hour, all allocated GPUs billed.
    flags.extend(matrix.get("flags", ()))
    flags.append("provisional_planning_estimate")
    return Estimate(gpu_class, matrix["episode_count"],
                    sum(n for n, _ in counts.values()), monitor_calls, seconds,
                    hours, price, hours * price if price is not None else None,
                    tuple(sorted(set(flags))))


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
    print(json.dumps(asdict(result), indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
