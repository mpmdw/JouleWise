"""Fixed-work synthetic MLX operand ladder; plan/dry paths need no MLX.

Only B changes: X[M,K] is fixed and W[N,K] is synthetic. Dense dispatches
compute X @ W.T; quantized dispatches use MLX's affine packed-weight path,
as mlx-lm QuantizedLinear does. FLOPs are dense-equivalent 2*M*N*K, not a
claim that 4/8-bit kernels execute identical instructions to dense kernels.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys
import time

from joulewise.clock import SystemClock
from ._common import require_numpy as _numpy
from joulewise.interp_energy.operand_stats import (
    bfloat16_bits, bfloat16_values, combine_statistics, operand_statistics,
)

DTYPES = ("bf16", "fp16", "int8", "int4")
CONDITIONS = ("normal", "normal_copy", "zeros", "constant", "zeros_50", "zeros_90",
              "sign_flipped", "scaled_025", "scaled_4", "low_hamming", "high_hamming",
              "sorted_rows", "weight_like")
GEOMETRIES = ("gemm", "gemv-ring")
SCHEMA = "joulewise.interp_energy.rail_data_dependence.v1"


@dataclass(frozen=True)
class Settings:
    dtypes: tuple[str, ...] = DTYPES
    geometries: tuple[str, ...] = GEOMETRIES
    conditions: tuple[str, ...] = CONDITIONS
    seed: int = 714
    rounds: int = 1
    slot_seconds: float = 10.0
    gap_seconds: float = 0.5
    baseline_seconds: float = 15.0
    window_seconds: float = 5400.0
    setup_reserve_seconds: float = 600.0
    ring_bytes: int = 1 << 30
    dry: bool = False

    def validate(self):
        for values, choices, name in ((self.dtypes, DTYPES, "dtypes"),
                                      (self.geometries, GEOMETRIES, "geometries"),
                                      (self.conditions, CONDITIONS, "conditions")):
            if not values or len(set(values)) != len(values) or not set(values) <= set(choices):
                raise ValueError(f"{name} must be nonempty, unique, and selected from {choices}")
        if "normal" not in self.conditions or len(self.conditions) < 2:
            raise ValueError("conditions must include normal and at least one comparator")
        if self.rounds < 1 or self.ring_bytes < 1:
            raise ValueError("rounds and ring_bytes must be positive")
        for name in ("slot_seconds", "gap_seconds", "baseline_seconds", "window_seconds",
                     "setup_reserve_seconds"):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0 or (name in ("slot_seconds", "window_seconds") and value == 0):
                raise ValueError(f"invalid {name}")
        if not self.dry and "gemv-ring" in self.geometries and self.ring_bytes < 1 << 30:
            raise ValueError("native GEMV weight ring must contain at least 1 GiB per condition")


def weight_bytes(n: int, k: int, dtype: str, group_size: int = 64) -> int:
    if dtype in ("bf16", "fp16"):
        return n * k * 2
    # Packed codes plus fp16 scale and affine bias per group, no fake int8 MAC.
    return n * k * int(dtype[3:]) // 8 + n * (k // group_size) * 4


def abba_schedule(conditions=CONDITIONS, *, rounds=1, seed=714) -> list[dict]:
    """Seeded comparator order and ABBA/BAAB orientation, interleaved by round."""
    rng = random.Random(seed)
    slots = []
    for repeat in range(rounds):
        comparators = [c for c in conditions if c != "normal"]
        rng.shuffle(comparators)
        for comparator in comparators:
            order = ("A", "B", "B", "A") if rng.getrandbits(1) else ("B", "A", "A", "B")
            block = len(slots) // 4
            for position, arm in enumerate(order):
                slots.append({"slot": len(slots), "round": repeat, "abba_block": block,
                              "position": position, "arm": arm, "comparator": comparator,
                              "condition": "normal" if arm == "A" else comparator})
    return slots


def make_plan(settings: Settings) -> dict:
    settings.validate()
    blocks = []
    for geometry in settings.geometries:
        m, n, k = ((8, 64, 64) if geometry == "gemm" else (1, 64, 64)) if settings.dry else (
            (2048, 2048, 2048) if geometry == "gemm" else (1, 4096, 4096))
        for dtype in settings.dtypes:
            matrix_bytes = weight_bytes(n, k, dtype)
            ring_size = (2 if settings.dry else math.ceil(settings.ring_bytes / matrix_bytes)) if geometry == "gemv-ring" else 1
            schedule = abba_schedule(settings.conditions, rounds=settings.rounds,
                                     seed=settings.seed + len(blocks))
            blocks.append({"id": f"{geometry}-{dtype}", "geometry": geometry, "dtype": dtype,
                           "shape_mnk": [m, n, k], "group_size": 64, "ring_size": ring_size,
                           "weight_bytes_per_condition": matrix_bytes * ring_size,
                           "resident_weight_bytes": matrix_bytes * ring_size * len(settings.conditions),
                           "dense_equivalent_flops_per_dispatch": 2 * m * n * k,
                           "activation_dtype": "bf16" if dtype == "bf16" else "fp16",
                           "weight_format": "affine uint32 packed codes + fp16 scales/biases" if dtype.startswith("int") else dtype,
                           "schedule": schedule})
    slots = sum(len(b["schedule"]) for b in blocks)
    estimate = (slots * (settings.slot_seconds + settings.gap_seconds) +
                len(blocks) * 2 * settings.baseline_seconds + settings.setup_reserve_seconds)
    if not settings.dry and estimate > settings.window_seconds:
        raise ValueError(f"planned {estimate:.1f}s exceeds window {settings.window_seconds:.1f}s")
    return {"schema": SCHEMA, "status": "PROVISIONAL diagnostic; no energy inference",
            "mode": "dry_numpy_float32_surrogate" if settings.dry else "native_mlx_gpu",
            "settings": asdict(settings), "blocks": blocks, "slot_count": slots,
            "estimated_seconds": estimate, "peak_resident_weight_bytes": max(b["resident_weight_bytes"] for b in blocks),
            "repetition_rule": "calibrate whole reference ring; same integer full-ring cycles in every slot of a geometry/dtype",
            "comparability": "within geometry/dtype only; timing, frequency, thermal and residency must be checked later",
            "statistics": "exact host storage counts; aligned C-order tile proxy, not observed hardware toggles",
            "capture_hooks": {
                "powermetrics": "joulewise.adapters.powermetrics.PowermetricsTelemetryAdapter (current-era stop_sampling_with_evidence)",
                "km003c": "scripts/km003c_monitor.py --out <block>/raw/km003c.jsonl --poll-ms 200 --rate 2",
                "ioreport": "no independent IOReport collector added; powermetrics is the existing rail path",
                "scope": "native only; warmup/statistics before capture; idle bracket and slot spans retained; no reduction"}}


def _seed(seed, index):
    return int.from_bytes(hashlib.sha256(f"{seed}:{index}".encode()).digest()[:8], "little")


def synthetic_weight(condition: str, shape, *, seed: int, dtype: str):
    """Deterministic related fills, from scratch; never loads model weights."""
    np = _numpy()
    if condition not in CONDITIONS or dtype not in DTYPES:
        raise ValueError("unknown condition or dtype")
    rng = np.random.default_rng(seed)
    normal = rng.normal(0, 0.02, size=shape).astype(np.float32)
    if condition in ("normal", "normal_copy"):
        return normal
    if condition == "zeros":
        normal.fill(0)  # actual host writes; transferred and evaluated before timing
        return normal
    if condition == "constant":
        normal.fill(0.02)
        return normal
    if condition.startswith("zeros_"):
        count = normal.size * int(condition.split("_")[1]) // 100
        normal.reshape(-1)[rng.permutation(normal.size)[:count]] = 0
    elif condition == "sign_flipped":
        normal *= -1
    elif condition.startswith("scaled_"):
        normal *= 0.25 if condition == "scaled_025" else 4
    elif condition == "sorted_rows":
        normal.sort(axis=-1)
    elif condition == "weight_like":
        # Normal bulk + synthetic 1% heavy-tailed outliers; no empirical fit.
        mask = rng.random(shape) < 0.01
        normal[mask] *= 12
    elif condition in ("low_hamming", "high_hamming"):
        # Finite normal IEEE values only. These also change values/sign; they
        # are extreme-fill controls, not isolated causal bit-toggle probes.
        word = (0x3F80 if dtype == "bf16" else 0x3C00) if condition == "low_hamming" else 0xBFFF
        words = np.full(shape, word, dtype=np.uint16)
        return bfloat16_values(words) if dtype == "bf16" else words.view(np.float16).astype(np.float32)
    return normal


def _logical_storage(values, dtype):
    np = _numpy()
    if dtype == "bf16":
        words = bfloat16_bits(values)
        return bfloat16_values(words), words
    values = np.asarray(values, dtype=np.float16)
    return values, values


def packed_hamming_word(bits: int, *, high: bool) -> int:
    """One vs bits-1 set bits per affine code, repeated in each uint32 word."""
    if bits not in (4, 8):
        raise ValueError("bits must be 4 or 8")
    code = (1 << bits) - 2 if high else 1
    return sum(code << shift for shift in range(0, 32, bits))


class NumpyDryBackend:
    """Tiny actual CPU timing; never impersonates bf16 or quantized execution."""

    name = "numpy-float32-surrogate"

    def prepare(self, block, conditions, seed):
        np = _numpy()
        m, n, k = block["shape_mnk"]
        x = np.random.default_rng(seed).normal(0, 0.02, (m, k)).astype(np.float32)
        prepared, stats = {}, {}
        for condition in conditions:
            ring = [synthetic_weight(condition, (n, k), seed=_seed(seed, i), dtype=block["dtype"])
                    for i in range(block["ring_size"])]
            prepared[condition] = (x, ring)
            stats[condition] = {"weight": combine_statistics([operand_statistics(w) for w in ring]),
                                "encoding": "dry float32 source only; target quantization not exercised"}
        stats["fixed_activation"] = operand_statistics(x)
        return prepared, stats

    def cycle(self, prepared):
        np = _numpy()
        x, ring = prepared
        for weight in ring:
            # Tiny reference contraction, bypassing platform BLAS dispatch.
            result = np.einsum("mk,nk->mn", x, weight, optimize=False)
        return result

    def check(self, result):
        np = _numpy()
        if not np.isfinite(result).all():
            raise RuntimeError("nonfinite synthetic output")

    def release(self):
        pass

    def metadata(self):
        return {"numpy_version": _numpy().__version__, "execution": "float32 einsum reference; no target-dtype validation"}


class MLXBackend:
    """Native MLX GPU only; all materialization/quantization outside slots."""

    name = "mlx-gpu"

    def __init__(self):
        try:
            import mlx.core as mx
        except ImportError as exc:
            raise RuntimeError("native mode requires MLX and a Metal-capable Mac") from exc
        self.mx = mx
        mx.set_default_device(mx.gpu)

    def prepare(self, block, conditions, seed):
        np, mx = _numpy(), self.mx
        m, n, k = block["shape_mnk"]
        dtype = block["dtype"]
        target = mx.bfloat16 if dtype == "bf16" else mx.float16
        source = np.random.default_rng(seed).normal(0, 0.02, (m, k)).astype(np.float32)
        x = mx.array(source, dtype=target)
        mx.eval(x)
        logical, encoded = _logical_storage(source, dtype)
        stats = {"fixed_activation": operand_statistics(logical, storage=encoded)}
        prepared = {}
        for condition in conditions:
            ring, weight_stats, scale_stats, bias_stats = [], [], [], []
            for index in range(block["ring_size"]):
                source = synthetic_weight(condition, (n, k), seed=_seed(seed, index), dtype=dtype)
                weight = mx.array(source, dtype=target)
                mx.eval(weight)
                if dtype.startswith("int"):
                    bits = int(dtype[3:])
                    packed, scales, biases = mx.quantize(weight, group_size=64, bits=bits)
                    if condition in ("low_hamming", "high_hamming"):
                        # Same affine metadata in both arms, exact chosen code
                        # patterns. Reuse the mlx-lm layout, not a signed int MAC.
                        packed = mx.array(np.full((n, k * bits // 32),
                            packed_hamming_word(bits, high=condition == "high_hamming"), dtype=np.uint32))
                        scales = mx.array(np.full((n, k // 64), 1 / ((1 << bits) - 1), dtype=np.float16))
                        biases = mx.array(np.full((n, k // 64), -0.5, dtype=np.float16))
                    mx.eval(packed, scales, biases)
                    logical = mx.dequantize(packed, scales, biases, group_size=64, bits=bits)
                    mx.eval(logical)
                    weight_stats.append(operand_statistics(np.array(logical.astype(mx.float32)), storage=np.array(packed)))
                    scale_stats.append(operand_statistics(np.array(scales)))
                    bias_stats.append(operand_statistics(np.array(biases)))
                    ring.append((packed, scales, biases))
                    del logical, weight
                else:
                    logical, encoded = _logical_storage(source, dtype)
                    weight_stats.append(operand_statistics(logical, storage=encoded))
                    ring.append(weight)
            stats[condition] = {"weight": combine_statistics(weight_stats)}
            if scale_stats:
                stats[condition].update(scales=combine_statistics(scale_stats), biases=combine_statistics(bias_stats))
            prepared[condition] = (x, ring, dtype)
        return prepared, stats

    def cycle(self, prepared):
        mx = self.mx
        x, ring, dtype = prepared
        for weight in ring:
            if dtype.startswith("int"):
                result = mx.quantized_matmul(x, *weight, transpose=True, group_size=64, bits=int(dtype[3:]))
            else:
                result = mx.matmul(x, weight.T)
            # Construct a fresh graph on every dispatch. eval waits for actual
            # GPU completion; never time just lazy graph construction.
            mx.eval(result)
        return result

    def check(self, result):
        if not bool(self.mx.all(self.mx.isfinite(result)).item()):
            raise RuntimeError("nonfinite synthetic output")

    def release(self):
        self.mx.clear_cache()

    def metadata(self):
        result = {"execution": "GPU, fresh matmul graph and eval on every dispatch"}
        for name in ("get_active_memory", "get_peak_memory", "get_cache_memory"):
            function = getattr(self.mx, name, None)
            result[name + "_bytes"] = int(function()) if function else None
        return result


# Compatibility for wave-1 callers; new code uses the same MLX spelling as replay.
MlxBackend = MLXBackend


def stamp(clock) -> dict:
    paired = asdict(clock.stamp())
    paired["monotonic_ns"] = time.monotonic_ns()
    raw = getattr(time, "CLOCK_MONOTONIC_RAW", None)
    paired["monotonic_raw_ns"] = time.clock_gettime_ns(raw) if raw is not None else None
    return paired


def execute_plan(plan, output: Path, *, backend=None, capture_factory=None, clock=None):
    """Run a fresh output directory. Preserve partial timing records on error.

    capture_factory(block_directory, clock) is an optional context manager
    yielding capture metadata. It wraps existing capture machinery only.
    """
    from contextlib import nullcontext

    settings = Settings(**{**plan["settings"], **{k: tuple(plan["settings"][k]) for k in ("dtypes", "geometries", "conditions")}})
    if settings.dry and capture_factory is not None:
        raise ValueError("dry mode cannot start capture hooks")
    clock = clock or SystemClock()
    backend = backend or (NumpyDryBackend() if settings.dry else MLXBackend())
    output.mkdir(parents=True, exist_ok=False)
    (output / "plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    start = time.perf_counter()
    with (output / "timings.jsonl").open("x") as stream:
        def emit(record):
            stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
            stream.flush()

        try:
            for index, block in enumerate(plan["blocks"]):
                prepared, stats = backend.prepare(block, settings.conditions, settings.seed + index)
                # Warm every condition, outside sampler/capture and timing.
                for operand in prepared.values():
                    backend.check(backend.cycle(operand))
                del operand
                calibration = []
                for _ in range(3):
                    t0 = time.perf_counter_ns()
                    result = backend.cycle(prepared["normal"])
                    calibration.append(max(1, time.perf_counter_ns() - t0))
                    backend.check(result)
                    del result
                cycle_ns = statistics.median(calibration)
                cycles = 1 if settings.dry else max(1, round(settings.slot_seconds * 1e9 / cycle_ns))
                emit({"kind": "setup", "block": block["id"], "backend": backend.name,
                      "statistics": stats, "calibration_cycle_ns": cycle_ns, "cycles_per_slot": cycles,
                      "calibration_cycle_samples_ns": calibration, "backend_metadata": backend.metadata(),
                      "executed_dtype": "float32" if settings.dry else block["activation_dtype"]})
                future = plan["blocks"][index+1:]
                projected = (time.perf_counter() - start +
                             len(block["schedule"]) * (cycles * cycle_ns / 1e9 + settings.gap_seconds) +
                             sum(len(b["schedule"]) for b in future) * (settings.slot_seconds + settings.gap_seconds) +
                             (1 + len(future)) * 2 * settings.baseline_seconds)
                if not settings.dry and projected > settings.window_seconds:
                    raise RuntimeError("calibrated work exceeds remaining window; stop and resize prospectively")
                capture_dir = output / block["id"]
                context = capture_factory(capture_dir, clock) if capture_factory else nullcontext({"capture": "disabled"})
                durations = {}
                with context as capture:
                    emit({"kind": "capture_start", "block": block["id"], "stamp": stamp(clock)})
                    if not settings.dry:
                        clock.sleep(settings.baseline_seconds)
                    for slot in block["schedule"]:
                        if not settings.dry and time.perf_counter() - start + cycles * cycle_ns / 1e9 + settings.baseline_seconds >= settings.window_seconds:
                            raise RuntimeError("window budget exhausted; partial schedule retained")
                        before = stamp(clock)
                        t0 = time.perf_counter_ns()
                        for _ in range(cycles):
                            result = backend.cycle(prepared[slot["condition"]])
                        elapsed = time.perf_counter_ns() - t0
                        after = stamp(clock)
                        backend.check(result)  # outside measured span
                        del result
                        dispatches = cycles * block["ring_size"]
                        durations.setdefault(slot["condition"], []).append(elapsed / dispatches)
                        emit({"kind": "timing", "block": block["id"], **slot, "start": before, "end": after,
                              "elapsed_ns": elapsed, "dispatches": dispatches,
                              "dense_equivalent_flops": dispatches * block["dense_equivalent_flops_per_dispatch"],
                              "ns_per_dispatch": elapsed / dispatches,
                              "backend": backend.name, "mode": plan["mode"]})
                        if not settings.dry:
                            clock.sleep(settings.gap_seconds)
                    if not settings.dry:
                        clock.sleep(settings.baseline_seconds)
                emit({"kind": "capture_stop", "block": block["id"], "stamp": stamp(clock), "metadata": capture})
                reference = statistics.median(durations["normal"])
                emit({"kind": "timing_comparison", "block": block["id"],
                      "median_time_ratios_to_normal": {c: statistics.median(v) / reference for c, v in durations.items()},
                      "validity": "requires lead review of time/frequency/residency; not an isolated switching-power claim"})
                del prepared
                backend.release()
            emit({"kind": "complete", "stamp": stamp(clock)})
        except BaseException as exc:
            emit({"kind": "aborted", "error": f"{type(exc).__name__}: {exc}", "stamp": stamp(clock)})
            raise


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry", "--dry-run", action="store_true", help="tiny NumPy float32 surrogate; no capture or MLX")
    mode.add_argument("--plan-only", action="store_true", help="emit native plan only; no optional dependencies")
    mode.add_argument("--execute", action="store_true", help="native GPU workload, only in a lead-controlled quiet window")
    ap.add_argument("--quiet-mac-confirmed", action="store_true", help="operator confirms agents stopped and quiet-Mac lane granted")
    ap.add_argument("--out", type=Path, required=True, help="new output directory, never overwritten")
    ap.add_argument("--dtypes", nargs="+", choices=DTYPES, default=DTYPES)
    ap.add_argument("--geometries", nargs="+", choices=GEOMETRIES, default=GEOMETRIES)
    ap.add_argument("--conditions", nargs="+", choices=CONDITIONS, default=CONDITIONS)
    ap.add_argument("--seed", type=int, default=714)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--slot-seconds", type=float, default=10)
    ap.add_argument("--window-seconds", type=float, default=5400)
    ap.add_argument("--powermetrics", action="store_true", help="use existing powermetrics adapter")
    ap.add_argument("--km003c", action="store_true", help="use existing KM003C monitor")
    args = ap.parse_args(argv)
    if args.execute and not args.quiet_mac_confirmed:
        ap.error("--execute requires --quiet-mac-confirmed; never run from an active agent session")
    if (args.powermetrics or args.km003c) and not args.execute:
        ap.error("capture hooks require --execute; dry/plan-only never capture")
    try:
        settings = Settings(dtypes=tuple(args.dtypes), geometries=tuple(args.geometries),
                            conditions=tuple(args.conditions), seed=args.seed, rounds=args.rounds,
                            slot_seconds=args.slot_seconds, window_seconds=args.window_seconds, dry=args.dry)
        plan = make_plan(settings)
        if args.plan_only:
            args.out.mkdir(parents=True, exist_ok=False)
            (args.out / "plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
        else:
            factory = None
            if args.powermetrics or args.km003c:
                from joulewise.interp_energy.capture_hooks import existing_capture
                factory = lambda path, clock: existing_capture(path, clock, powermetrics=args.powermetrics, km003c=args.km003c)
            execute_plan(plan, args.out, capture_factory=factory)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"rail_data_dependence: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(args.out), "mode": plan["mode"], "slots": plan["slot_count"],
                      "estimated_seconds": plan["estimated_seconds"]}, sort_keys=True))
    return 0
