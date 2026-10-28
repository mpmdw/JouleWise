#!/usr/bin/env python3
"""Non-claim MLX streaming probe; receipt contract: known-bytes reading rule §2.

Counts logical uint8 payload reads, not memory-controller traffic. Capture rails
and KM003C continuously across the eight calls. At harvest, compare_stack() must
receive the concurrent capture's stack identity; the probe cannot attest to it.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.flags.collect import runtime_versions

NOT_APPLICABLE = (
    "model_artifact_sha256", "quantization", "tokenizer_identity",
    "sampler_output_policy", "batching_concurrency_policy",
)
LOCAL_FIELDS = (
    "os_version", "hardware_unit.machine", "hardware_unit.device",
    "runtime_version.name", "runtime_version.version", "kernel_library",
)
CAPTURE_FIELDS = ("telemetry_backend", "measurement_boundary_label.rails")


def _field(value, path):
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def registered_stack(repo_root=ROOT):
    """Read the §2 reference projections, checking that any unit is equivalent."""
    root = Path(repo_root)
    pins = json.loads((root / "configs/b6/registration/identity_pins.json").read_text())
    versions = json.loads((root / "configs/bytes/identity_pins.json").read_text())["runtime_versions"]
    stacks = [unit["stack_identity"] for unit in pins["units"].values()]
    if not stacks:
        raise ValueError("registered stack has no units")
    reference = stacks[0]
    for field in LOCAL_FIELDS + CAPTURE_FIELDS:
        expected = _field(reference, field)
        if expected is None or any(_field(stack, field) != expected for stack in stacks):
            raise ValueError(f"registered stack units lack one common {field}")
    return reference, versions


def collect_stack(mx, device, *, repo_root=ROOT, prepare=None):
    """Use pass-1 sources, outside all stamped spans; no model is prepared here."""
    versions = runtime_versions(sys.executable)
    stack = {
        "os_version": platform.platform(),
        "hardware_unit": {"machine": platform.machine(), "device": device},
        "runtime_version": {"name": "mlx", "version": mx.__version__},
        # build_stack_identity uses this same prepare-field fallback.
        "kernel_library": str((prepare or {}).get("kernel_library") or "unavailable"),
        "python": versions["python"], "packages": versions["packages"],
        "git_commit": subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip(),
    }
    stack.update({field: "not_applicable" for field in NOT_APPLICABLE})
    return stack


def compare_stack(stack, reference, versions, *, capture_stack=None):
    """§2 projections only; capture fields must come from harvest, never a guess.

    A pending capture is not a successful comparison. A mismatch is recorded,
    not an exception that would discard the receipt or its measured numbers.
    """
    differences = []
    for field in LOCAL_FIELDS:
        actual, expected = _field(stack, field), _field(reference, field)
        if actual is None or expected is None or actual != expected:
            differences.append(field)
    if stack.get("python") is None or stack.get("python") != versions.get("python"):
        differences.append("python")
    actual_packages = stack.get("packages") or {}
    expected_packages = versions["packages"]
    for package in sorted(actual_packages.keys() | expected_packages.keys()):
        # A null observed version cannot stand in for an installed pinned package.
        if (package not in actual_packages or package not in expected_packages
                or actual_packages[package] != expected_packages[package]):
            differences.append("packages." + package)
    pending = []
    for field in CAPTURE_FIELDS:
        actual = _field(capture_stack, field)
        if actual is None:
            pending.append(field)
        elif _field(reference, field) is None or actual != _field(reference, field):
            differences.append(field)
    return {"status": "differs" if differences else ("pending_capture" if pending else "match"),
            "differences": differences, "pending_fields": pending}


def _seconds(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("idle and settle seconds must be finite nonnegative numbers")
    return value


def stream(byte_count, repeats, *, device, idle_s=57.6, settle_s=3,
           mx=None, clock_ns=None, sleep=None, repo_root=ROOT):
    if type(byte_count) is not int or byte_count <= 0 or type(repeats) is not int or repeats <= 0:
        raise ValueError("byte count and repeats must be positive integer counts")
    idle_s, settle_s = _seconds(idle_s), _seconds(settle_s)
    if not isinstance(device, str) or not device.strip():
        raise ValueError("device must be the checkout's hardware_target.id")
    if mx is None:
        import mlx.core as mx  # Lazy: help, comparison and fake tests need no Metal.
    if clock_ns is None:
        clock_ns = lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    if sleep is None:
        sleep = time.sleep
    stack = collect_stack(mx, device, repo_root=repo_root)
    reference, versions = registered_stack(repo_root)
    check = compare_stack(stack, reference, versions)

    data = mx.ones((byte_count,), dtype=mx.uint8)
    mx.eval(data)
    mx.synchronize()
    warm = mx.sum(data)
    mx.eval(warm)
    mx.synchronize()

    pre_start = clock_ns()
    if idle_s:
        sleep(idle_s)
    pre_end = clock_ns()
    if settle_s:
        sleep(settle_s)
    start = clock_ns()
    for _ in range(repeats):
        # A fresh, immediately evaluated reduction per dispatch; no reuse of
        # the warm result or of one cached lazy result. No payload-sized output.
        result = mx.sum(data)
        mx.eval(result)
    mx.synchronize()
    end = clock_ns()
    if settle_s:
        sleep(settle_s)
    post_start = clock_ns()
    if idle_s:
        sleep(idle_s)  # data stays resident through this span.
    post_end = clock_ns()

    stamps = (pre_start, pre_end, start, end, post_start, post_end)
    if any(type(stamp) is not int or stamp < 0 for stamp in stamps):
        raise ValueError("CLOCK_MONOTONIC_RAW stamps must be nonnegative integer nanoseconds")
    if any(b < a for a, b in zip(stamps, stamps[1:])) or end <= start:
        raise ValueError("stream has no positive ordered monotonic span")
    if idle_s and (pre_end <= pre_start or post_end <= post_start):
        raise ValueError("idle has no positive monotonic span")
    return {"schema_version": "joulewise.bytes_stream.v2", "non_claim": True,
            "clock": "CLOCK_MONOTONIC_RAW", "start_ns": start, "end_ns": end,
            "idle_pre_start_ns": pre_start, "idle_pre_end_ns": pre_end,
            "idle_post_start_ns": post_start, "idle_post_end_ns": post_end,
            "idle_s": idle_s, "settle_s": settle_s,
            "duration_s": (end - start) / 1_000_000_000,
            "bytes_per_read": byte_count, "repeats": repeats, "bytes_read": byte_count * repeats,
            "boundary": "logical uint8 payload reads; excludes initialization and reduction workspace",
            "stack": stack, "stack_check": check}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bytes", type=int, required=True, dest="byte_count")
    parser.add_argument("--repeats", type=int, required=True)
    parser.add_argument("--device", required=True, help="hardware_target.id from the checkout's run config")
    parser.add_argument("--idle-s", type=float, default=57.6)
    parser.add_argument("--settle-s", type=float, default=3)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = stream(args.byte_count, args.repeats, device=args.device,
                    idle_s=args.idle_s, settle_s=args.settle_s)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
