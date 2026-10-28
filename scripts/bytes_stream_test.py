#!/usr/bin/env python3
"""Non-claim MLX streaming probe; receipt contract: known-bytes reading rule §2.

Counts logical uint8 payload reads, not memory-controller traffic. Capture rails
and KM003C continuously across the eight calls. At harvest, compare_stack() must
receive the concurrent capture's stack identity; the probe cannot attest to it.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import statistics
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


# Registered pass-1 projection, never loaded from the running checkout.
REFERENCE_COMMIT = "6731d5249"
REFERENCE_SOURCES = {'configs/b6/registration/identity_pins.json': '95d07401bb5d7c7e44e9dc27984bc3da4fb04642ec7cf80bf3c6ecadaf2efc6e', 'configs/bytes/identity_pins.json': '0760eded0603782b5367ad56721faf96417b9ea87bb698dc520835f34e03b2b2'}
REFERENCE_STACK = {'os_version': 'macOS-26.6.2-arm64-arm-64bit-Mach-O', 'hardware_unit': {'machine': 'arm64', 'device': 'macbook_m3_max'}, 'runtime_version': {'name': 'mlx', 'version': '0.31.2'}, 'kernel_library': 'unavailable', 'telemetry_backend': 'powermetrics', 'measurement_boundary_label': {'rails': ['cpu_power', 'gpu_power', 'ane_power']}}
REFERENCE_VERSIONS = {'packages': {'mlx': '0.31.2', 'mlx-lm': '0.31.3', 'mlx-metal': '0.31.2', 'numpy': '2.5.1', 'safetensors': '0.8.0', 'tokenizers': '0.22.2', 'transformers': '5.12.1'}, 'python': '3.13.1'}
PHYSICAL_FIELDS = ("os_version", "hardware_unit.machine", "hardware_unit.device",
                   "runtime_version.name", "runtime_version.version", "packages.mlx", "packages.mlx-metal")


def registered_stack(repo_root=ROOT):
    """Return independent copies of the pinned projection, regardless of checkout."""
    return deepcopy(REFERENCE_STACK), deepcopy(REFERENCE_VERSIONS)


def checkout_reference_check(repo_root=ROOT):
    """Disclose every unit's projection against the embedded reference; never veto."""
    result = {"commit": REFERENCE_COMMIT, "sources": REFERENCE_SOURCES,
              "units": {}, "errors": [], "versions": None}
    for path in REFERENCE_SOURCES:
        try:
            value = json.loads((Path(repo_root)/path).read_text())
            if path.startswith("configs/b6/"):
                for name, unit in value["units"].items():
                    result["units"][name] = compare_stack(
                        unit["stack_identity"], REFERENCE_STACK, REFERENCE_VERSIONS,
                        capture_stack=unit["stack_identity"])
                    # Unit records do not contain runtime_versions; compare those separately.
                    check = result["units"][name]
                    check["comparison"] = [row for row in check["comparison"]
                                           if row["field"] in LOCAL_FIELDS+CAPTURE_FIELDS]
                    for key in ("differences", "physical_differences", "disclosure_differences"):
                        check[key] = [f for f in check[key] if f in LOCAL_FIELDS+CAPTURE_FIELDS]
                    check["status"] = "differs" if check["differences"] else "match"
                if not value["units"]:
                    result["errors"].append(path+": no units")
            else:
                local = deepcopy(REFERENCE_STACK)
                local.update(value["runtime_versions"])
                result["versions"] = compare_stack(local, REFERENCE_STACK, REFERENCE_VERSIONS,
                                                    capture_stack=REFERENCE_STACK)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            result["errors"].append(path+": "+str(exc))
    return result


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
    differences, comparison = [], []
    for field in LOCAL_FIELDS:
        actual, expected = _field(stack, field), _field(reference, field)
        comparison.append({"field": field, "actual": actual, "expected": expected})
        if actual is None or expected is None or actual != expected:
            differences.append(field)
    comparison.append({"field": "python", "actual": stack.get("python"), "expected": versions.get("python")})
    if stack.get("python") is None or stack.get("python") != versions.get("python"):
        differences.append("python")
    actual_packages = stack.get("packages") or {}
    expected_packages = versions["packages"]
    for package in sorted(actual_packages.keys() | expected_packages.keys()):
        comparison.append({"field": "packages."+package, "actual": actual_packages.get(package),
                           "expected": expected_packages.get(package)})
        # A null observed version cannot stand in for an installed pinned package.
        if (package not in actual_packages or package not in expected_packages
                or actual_packages[package] != expected_packages[package]):
            differences.append("packages." + package)
    pending = []
    for field in CAPTURE_FIELDS:
        actual = _field(capture_stack, field)
        comparison.append({"field": field, "actual": actual, "expected": _field(reference, field)})
        if actual is None:
            pending.append(field)
        elif _field(reference, field) is None or actual != _field(reference, field):
            differences.append(field)
    return {"status": "differs" if differences else ("pending_capture" if pending else "match"),
            "differences": differences, "pending_fields": pending,
            "physical_differences": [f for f in differences if f in PHYSICAL_FIELDS],
            "disclosure_differences": [f for f in differences if f not in PHYSICAL_FIELDS],
            "comparison": comparison}


def knee_scan(receipts):
    """§1: three calls per doubling size; uncertainties are endpoint bounds.

    Return every input and comparison, including undefined pairs, for printing.
    Only the receipt's integer-ns resolution and observed spread set the bars.
    """
    grouped = {}
    for receipt in receipts:
        grouped.setdefault(receipt["bytes_per_read"], []).append(receipt)
    sizes = sorted(grouped)
    if len(sizes) < 2 or any(hi != 2*lo for lo, hi in zip(sizes, sizes[1:])):
        raise ValueError("scan needs consecutive doubling sizes")
    times = {}
    for size, calls in sorted(grouped.items()):
        if len(calls) != 3:
            raise ValueError("scan needs three calls per size")
        values = [(c["end_ns"]-c["start_ns"])/1e9/c["repeats"] for c in calls]
        if any(c["repeats"] <= 0 or v <= 0 for c, v in zip(calls, values)):
            raise ValueError("scan counts and durations must be positive")
        mean = statistics.mean(values)
        uncertainty = max(abs(v-mean) for v in values) + statistics.mean(1e-9/c["repeats"] for c in calls)
        times[size] = {"t_s": mean, "dt_s": uncertainty, "calls": calls}
    pairs = []
    for lo, hi in zip(sizes, sizes[1:]):
        d = times[hi]["t_s"]-times[lo]["t_s"]
        dd = times[hi]["dt_s"]+times[lo]["dt_s"]
        pair = {"size": hi, "difference_s": d, "uncertainty_s": dd,
                "m_bytes_s": None, "dm_bytes_s": None, "above": False}
        if d <= dd:
            pair["description"] = "not defined (dispatch-time difference not separated from zero)"
        else:
            pair.update(m_bytes_s=(hi-lo)/d, dm_bytes_s=(hi-lo)*dd/(d*(d-dd)))
        pairs.append(pair)
    result = {"status": "knee not found", "K": None, "sizes": times, "pairs": pairs,
              "threshold": None, "threshold_uncertainty": None}
    defined = [p for p in pairs if p["m_bytes_s"] is not None]
    if pairs[-1]["m_bytes_s"] is None:
        result["reason"] = "top pair undefined"
        return result
    peak = max(defined, key=lambda p: p["m_bytes_s"])
    md, ud = pairs[-1]["m_bytes_s"], pairs[-1]["dm_bytes_s"]
    mc, uc = peak["m_bytes_s"], peak["dm_bytes_s"]
    if md <= ud or mc <= uc:
        result["reason"] = "reference lower endpoint nonpositive"
        return result
    def h(x, y):
        return 1 / ((63/64)/x + (1/64)/y)
    threshold = h(md, mc)
    dth = max(h(md+ud, mc+uc)-threshold, threshold-h(md-ud, mc-uc))
    result.update(threshold=threshold, threshold_uncertainty=dth)
    for pair in defined:
        margin, bar = pair["m_bytes_s"]-threshold, pair["dm_bytes_s"]+dth
        pair.update(margin=margin, bar=bar, above=margin > bar)
    above = [p["size"] for p in pairs if p["above"]]
    k = next((s for s in sizes[1:] if not any(a >= s for a in above)), None)
    if not above:
        result["reason"] = "no resolved cache evidence"
    elif k is None or 64*k > sizes[-1]:
        result["reason"] = "64 K > s_max"
    else:
        result.update(status="knee found", K=k, B=max(2**32, 64*k),
                      Bc1=k//16, Bc3=k//8, Bc2=k//4, phi=k/max(2**32, 64*k))
    return result


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
    reference_check = checkout_reference_check(repo_root)

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
            "stack": stack, "stack_check": check, "reference_check": reference_check}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "scan":
        parser = argparse.ArgumentParser(description="Read §1 scan receipts; print full timing comparisons")
        parser.add_argument("receipts", type=Path, help="JSON list of three receipts per size")
        args = parser.parse_args(argv[1:])
        print(json.dumps(knee_scan(json.loads(args.receipts.read_text())), allow_nan=False, indent=2))
        return 0
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
