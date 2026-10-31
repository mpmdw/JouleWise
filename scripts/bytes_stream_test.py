#!/usr/bin/env python3
"""Non-claim MLX streaming probe; receipt contract: known-bytes reading rule §2.

Counts logical uint8 payload reads, not memory-controller traffic. Capture rails
and KM003C continuously across the four calls. At harvest, compare_stack() must
receive the concurrent capture's stack identity; the probe cannot attest to it.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
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
                   "runtime_version.name", "runtime_version.version", "packages.mlx", "packages.mlx-metal", "measurement_boundary_label.rails")


def registered_stack(repo_root=ROOT):
    """Return independent copies of the pinned projection, regardless of checkout."""
    return deepcopy(REFERENCE_STACK), deepcopy(REFERENCE_VERSIONS)


def checkout_reference_check(repo_root=ROOT):
    """Disclose every unit's projection against the embedded reference; never veto."""
    result = {"commit": REFERENCE_COMMIT, "sources": deepcopy(REFERENCE_SOURCES),
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


# One input accessor for the read and check paths. Schemas describe prerequisites,
# not replacement measurements. Invalid collections are unavailable as a whole:
# dropping a bad sample would silently change support or reduce a bound.
ABSENT = object()
NUMBER = ("number", None)
NONNEG = ("number", 0)
POSITIVE = ("positive", 0)
COUNT = ("integer", 0)
POSCOUNT = ("positive_integer", 0)
TEXT = ("text", None)
EDGES = ("edges", 2)


def finite_number(value):
    try:
        return type(value) in (int, float) and math.isfinite(float(value))
    except (OverflowError, ValueError):
        return False


def input_value(value, schema, path):
    """Return (valid value, None), or (None, a leaf-naming missing reason)."""
    reason = path+" missing or invalid"
    if value is ABSENT or value is None:
        return None, reason
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            return None, reason
        result = dict(value)
        errors = []
        for key, spec in schema.items():
            result[key], error = input_value(value.get(key, ABSENT), spec, path+"."+key)
            if error:
                errors.append(error)
        if not errors:
            pairs = []
            if all(k in schema for k in RECEIPT_INPUTS):
                keys = ("idle_pre_start_ns", "idle_pre_end_ns", "start_ns", "end_ns",
                        "idle_post_start_ns", "idle_post_end_ns")
                pairs = [(a, b, a == "start_ns") for a, b in zip(keys, keys[1:])]
            elif "start_ns" in schema and "end_ns" in schema:
                pairs = [("start_ns", "end_ns", True)]
            for a, b, strict in pairs:
                if result[b] < result[a] or (strict and result[b] == result[a]):
                    errors.append(f"{path}.{a}/{b} invalid time order")
        return (None, "; ".join(errors)) if errors else (result, None)
    if isinstance(schema, list):
        if not isinstance(value, list) or not value:
            return None, reason
        result = []
        for i, row in enumerate(value):
            item, error = input_value(row, schema[0], f"{path}[{i}]")
            if error:
                return None, error
            result.append(item)
        return result, None
    kind, limit = schema
    if kind == "native":
        spec, start = limit
        rows, error = input_value(value, spec, path)
        if error:
            return None, error
        stamp = "stamp_ns" if "stamp_ns" in spec[0] else "start_ns"
        previous = None
        for i, row in enumerate(rows):
            v = row[stamp]
            if ((previous is not None and v < previous) or
                    (start is not None and v == 0 and start > 0)):
                return None, f"{path}[{i}].{stamp} invalid time order"
            previous = row.get("end_ns", v)
        return rows, None
    if kind == "json":
        if isinstance(value, dict):
            for key, item in value.items():
                _, error = input_value(item, schema, path+"."+key)
                if error:
                    return None, error
            return value, None
        if isinstance(value, list):
            for i, item in enumerate(value):
                _, error = input_value(item, schema, f"{path}[{i}]")
                if error:
                    return None, error
            return value, None
        valid = isinstance(value, (str, bool)) or (finite_number(value))
    elif kind == "text":
        valid = isinstance(value, str) and bool(value.strip())
    elif kind in ("edges", "signed_edges"):
        valid = isinstance(value, list) and len(value) == limit
        if valid:
            for i, item in enumerate(value):
                _, error = input_value(item, NUMBER if kind == "signed_edges" else NONNEG, f"{path}[{i}]")
                if error:
                    return None, error
    else:
        valid = finite_number(value)
        if kind in ("integer", "positive_integer"):
            valid = valid and type(value) is int
        if limit is not None:
            valid = valid and (value > limit if kind in ("positive", "positive_integer") else value >= limit)
    return (value, None) if valid else (None, reason)


RECEIPT_INPUTS = {**{k: COUNT for k in (
    "start_ns", "end_ns", "idle_pre_start_ns", "idle_pre_end_ns",
    "idle_post_start_ns", "idle_post_end_ns")},
    "bytes_per_read": POSCOUNT, "repeats": POSCOUNT, "bytes_read": POSCOUNT, "settle_s": NONNEG}
STACK_INPUTS = {"os_version": TEXT, "hardware_unit": {"machine": TEXT, "device": TEXT},
    "runtime_version": {"name": TEXT, "version": TEXT}, "kernel_library": TEXT,
    "python": TEXT, "packages": {key: TEXT for key in REFERENCE_VERSIONS["packages"]}}
CAPTURE_INPUTS = {"telemetry_backend": TEXT, "measurement_boundary_label": {"rails": [TEXT]}}
NATIVE_INPUTS = {stream: [{**({"stamp_ns": COUNT} if stream in ("meter", "battery") else
    {"start_ns": COUNT, "end_ns": COUNT}), "power_w": NUMBER if stream == "battery" else NONNEG}]
    for stream in ("rails", "gpu", "meter", "battery")}


def json_evidence(value):
    """Keep malformed numeric evidence serializable without inventing a number."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: json_evidence(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_evidence(v) for v in value]
    return value


def clock_metadata():
    """Record the actual clock, without inferring conversion from its return type."""
    result = {"clock": "CLOCK_MONOTONIC_RAW", "clock_resolution_s": None,
              "clock_tick_num_ns": None, "clock_tick_den": None,
              "clock_tick_source": "not applicable (non-macOS clock_getres)",
              "clock_ns_conversion": "unknown", "clock_ns_conversion_source": "unknown"}
    try:
        result["clock_resolution_s"] = time.clock_getres(time.CLOCK_MONOTONIC_RAW)
        if sys.platform == "darwin":
            import ctypes
            class Timebase(ctypes.Structure):
                _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]
            info = Timebase()
            lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
            lib.mach_timebase_info.argtypes = [ctypes.POINTER(Timebase)]
            lib.mach_timebase_info.restype = ctypes.c_int
            result["clock_tick_source"] = "mach_timebase_info"
            if lib.mach_timebase_info(ctypes.byref(info)) != 0 or not info.denom:
                raise ValueError("mach_timebase_info unavailable")
            result.update(clock_tick_num_ns=info.numer, clock_tick_den=info.denom)
        result["clock_duration_bound_ns"] = clock_duration_bound_ns(result)
    except (OSError, ValueError, AttributeError) as exc:
        result["clock_error"] = str(exc)
        result["clock_duration_bound_ns"] = not_defined(str(exc))
    return result


def clock_duration_bound_ns(receipt):
    """Two endpoints, each within r plus the 1 ns integer conversion unit."""
    receipt, error = input_value(receipt, {"clock":TEXT, "clock_resolution_s":POSITIVE,
        "clock_tick_source":TEXT}, "receipt")
    if error:
        raise ValueError(error+" (clock resolution missing or clock identity missing)")
    if receipt.get("clock") != "CLOCK_MONOTONIC_RAW":
        raise ValueError("clock identity missing or unsupported")
    res = receipt.get("clock_resolution_s")
    if not isinstance(res, (int, float)) or not math.isfinite(res) or res <= 0:
        raise ValueError("clock resolution missing")
    tick = 0
    if receipt.get("clock_tick_source") != "not applicable (non-macOS clock_getres)":
        num, error = input_value(receipt.get("clock_tick_num_ns", ABSENT), POSCOUNT, "receipt.clock_tick_num_ns")
        den, den_error = input_value(receipt.get("clock_tick_den", ABSENT), POSCOUNT, "receipt.clock_tick_den")
        if error or den_error:
            raise ValueError(error or den_error)
        if type(num) is not int or type(den) is not int or num <= 0 or den <= 0:
            raise ValueError("clock timebase missing")
        tick = num/den
    return 2*(max(res*1e9, tick)+1)


# Rule §1: the MLX v0.31.2 small-launch boundary; eight powers down to
# 128 threadgroups × 1024 threads × 4 bytes = 2**19 first-pass saturation.
SCHEMA = "joulewise.bytes_stream.v3"
GEOMETRY_BYTES = 2**26
GEOMETRY_SOURCE = "mlx v0.31.2 mlx/backend/metal/reduce.cpp all_reduce_dispatch: in.nbytes() <= (1 << 26)"
RING_BYTES = 2**35  # 64 × the admitted 512 MiB capacity envelope.
CAPACITY_BYTES = RING_BYTES // 64
PHI_U = CAPACITY_BYTES / RING_BYTES
LADDER = tuple(GEOMETRY_BYTES >> k for k in range(8))
ORDER = ("R", "C", "C", "R")
CHECK_CALL_S = 2  # Admitted scan's planning duration, carried into §1 R2.
CALL_S = 759.2  # (3573.6 - 4*(2*57.6 + 3*3 + 10))/4, §1.


def geometry_error(receipt, b=None):
    """Receipt-only v3 invariants; return the first named failed field."""
    def fail(field):
        return "geometry check failed ("+field+")"
    if not isinstance(receipt, dict):
        return fail("receipt")
    if receipt.get("schema_version") != SCHEMA:
        return fail("schema_version")
    own_b = receipt.get("bytes_per_read")
    if type(own_b) is not int or own_b <= 0 or own_b > GEOMETRY_BYTES or RING_BYTES % own_b:
        return fail("bytes_per_read")
    if b is not None and own_b != b:
        return fail("bytes_per_read")
    q = RING_BYTES // own_b
    # Counts, shapes and hashes are integer/exact contracts, not tolerances.
    expected = {"ring_bytes":RING_BYTES, "ring_shape":[q,own_b], "dtype":"uint8",
                "view_nbytes":own_b, "geometry_branch_bytes":GEOMETRY_BYTES,
                "geometry_source":GEOMETRY_SOURCE, "launch_side":"small"}
    for field, value in expected.items():
        actual = receipt.get(field)
        if actual != value or (isinstance(value,int) and type(actual) is not int):
            return fail(field)
        if field == "ring_shape" and any(type(axis) is not int for axis in actual):
            return fail(field)
    arm = receipt.get("arm")
    if arm not in ("R","C","check-R","check-C"):
        return fail("arm")
    if receipt.get("view_order") != ("rotate" if arm.endswith("R") else "repeat"):
        return fail("view_order")
    n = receipt.get("repeats")
    if type(n) is not int or n <= 0 or n % q:
        return fail("repeats")
    for field, value in (("sweeps",n//q),("bytes_read",own_b*n),("logical_bytes",own_b*n)):
        if type(receipt.get(field)) is not int or receipt[field] != value:
            return fail(field)
    for field in ("packages.mlx","packages.mlx-metal","runtime_version.version"):
        if _field(receipt.get("stack"),field) != "0.31.2":
            return fail("stack."+field)
    return None


def timing_summary(calls):
    """§1 R3: three observed spans plus their recorded endpoint clock bound."""
    if not isinstance(calls,list) or len(calls) != 3:
        raise ValueError("three timing calls required")
    values, qs = [], []
    for c in calls:
        c, error = input_value(c, {"start_ns":COUNT,"end_ns":COUNT,"repeats":POSCOUNT}, "receipt")
        if error:
            raise ValueError(error)
        values.append((c["end_ns"]-c["start_ns"])/1e9/c["repeats"])
        try:
            qs.append(clock_duration_bound_ns(c)/1e9/c["repeats"])
        except ValueError as exc:
            raise ValueError("clock prerequisite missing ("+str(exc)+")") from exc
    mean = statistics.mean(values)
    return {"t_s":mean, "dt_s":max(abs(v-mean) for v in values)+statistics.mean(qs),
            "d_s":values,"q_s":qs,"calls":calls}


def residency_rung(b, c, r):
    """§1 R4 and §3 bias; also used for explicitly labelled archive timing replays."""
    d = r["t_s"]-c["t_s"]
    dd = r["dt_s"]+c["dt_s"]
    row = {"b":b,"C":c,"R":r,"D_s":d,"dD_s":dd,"resolved":d > dd}
    if row["resolved"]:
        rho = (1-PHI_U)*(d-dd)/(r["t_s"]+r["dt_s"])
        row.update(rho_L=rho,kappa=1/rho)
    return row


def check_failure(reason, receipts, rungs=None):
    return {"status":"residency not resolved","reason":reason,"b":None,
            "W":RING_BYTES,"Q":None,"G":GEOMETRY_BYTES,"geometry_source":GEOMETRY_SOURCE,
            "phi_U":PHI_U,"phi_U_fraction":"1/64","receipts":json_evidence(receipts),
            "rungs":rungs or [],"geometry_checks":check_geometry(receipts)}


def check_geometry(receipts):
    return [{"ok":(error := geometry_error(receipt)) is None,"reason":error}
            for receipt in receipts] if isinstance(receipts,list) else []


def residency_check(receipts):
    """Strict v3, top-down C/R pilot+triplets, stopping at the first resolved rung.

    A partial/malformed rung stays in evidence and cannot be silently dropped.
    Allocation failures are authored by the stage before any receipt exists.
    """
    rungs = []
    def fault(reason):
        return check_failure(reason,receipts,rungs)
    if not isinstance(receipts,list):
        return fault("check-status fault (receipts must be a list)")
    pos = 0
    for k,b in enumerate(LADDER):
        modes = {}
        for arm in ("C","R"):
            own = []
            for phase in ("pilot","timing","timing","timing"):
                if pos >= len(receipts):
                    return fault("check-status fault (incomplete rung "+str(k)+")")
                receipt = receipts[pos]
                pos += 1
                error = geometry_error(receipt,b)
                if error:
                    return fault(error)
                if (receipt.get("arm") != "check-"+arm or receipt.get("rung_index") != k or
                        type(receipt.get("rung_index")) is not int or receipt.get("check_phase") != phase):
                    return fault("check-status fault (rung/mode/phase order)")
                if receipt.get("idle_s") != 0 or receipt.get("settle_s") != 0:
                    return fault("check-status fault (check idle/settle)")
                try:
                    clock_duration_bound_ns(receipt)
                except ValueError as exc:
                    return fault("clock prerequisite missing ("+str(exc)+")")
                _,error = input_value(receipt,RECEIPT_INPUTS,"receipt")
                if error:
                    return fault("check-status fault ("+error+")")
                if phase == "pilot":
                    if receipt["repeats"] != RING_BYTES//b:
                        return fault("check-status fault (pilot must be one sweep)")
                    t = (receipt["end_ns"]-receipt["start_ns"])/1e9/receipt["repeats"]
                    count = planned_repeats(b,t,CHECK_CALL_S,at_least_one=True)
                elif receipt["repeats"] != count:
                    return fault("check-status fault (pilot-derived repeats)")
                else:
                    own.append(receipt)
            try:
                modes[arm] = timing_summary(own)
            except ValueError as exc:
                return fault(str(exc))
        row = residency_rung(b,modes["C"],modes["R"])
        rungs.append(row)
        if row["resolved"]:
            if pos != len(receipts):
                return fault("check-status fault (receipts after first resolved rung)")
            return {"status":"residency resolved","b":b,"W":RING_BYTES,"Q":RING_BYTES//b,
                    "G":GEOMETRY_BYTES,"geometry_source":GEOMETRY_SOURCE,
                    "phi_U":PHI_U,"phi_U_fraction":"1/64","rho_L":row["rho_L"],
                    "kappa":row["kappa"],"rungs":rungs,"receipts":json_evidence(receipts),
                    "geometry_checks":check_geometry(receipts)}
    if pos != len(receipts):
        return fault("check-status fault (receipts after ladder)")
    return fault("residency not resolved")


def validated_check(check):
    """Recompute success from its evidence; never trust serialized κ or timings."""
    if not isinstance(check,dict):
        return check_failure("check-status fault (check missing)",[])
    if check.get("status") == "residency not resolved":
        # A failure is never promoted by re-reading its partial receipts.
        reason = check.get("reason")
        if not isinstance(reason,str) or not reason:
            reason = "check-status fault (failure reason missing)"
        return check_failure(reason,check.get("receipts",[]),check.get("rungs",[]))
    recomputed = residency_check(check.get("receipts"))
    if (check.get("status") != "residency resolved" or "reason" in check or
            recomputed["status"] != "residency resolved" or
            any(type(check.get(f)) is not int or check[f] != recomputed[f] for f in ("b","W","Q"))):
        reason = recomputed.get("reason","check-status fault (inconsistent success)")
        return check_failure(reason,check.get("receipts",[]),recomputed["rungs"])
    return recomputed


def planned_repeats(b, t_s, target_s, *, at_least_one=False):
    q = RING_BYTES//b
    sweeps = math.floor(target_s/(q*t_s))
    return q*(max(1,sweeps) if at_least_one else sweeps)


def not_defined(reason):
    return f"not defined ({reason})"


def idle_statistics(rows, start_ns, end_ns, stream):
    try:
        result = _idle_statistics(rows, start_ns, end_ns, stream)
        if any(not finite_number(result[key]) for key in ("mean_w", "variance_w2") if key in result):
            raise ValueError("non-finite idle mean or variance")
        return result
    except (OverflowError, ValueError) as exc:
        return {"reason": stream+" idle arithmetic unavailable: "+str(exc), "sample_count":len(rows)}


def _idle_statistics(rows, start_ns, end_ns, stream):
    """Native idle support; polls use arithmetic means, rails clipped intervals.

    Poll rows: stamp_ns, power_w. Rails/GPU rows: start_ns, end_ns, power_w.
    No joint meter/battery series is constructed. All rows are in RAW time.
    """
    from joulewise.idle_dependence import estimate_newey_west_bartlett
    length = (end_ns-start_ns)/1e9
    required = ("stamp_ns","power_w") if stream in ("meter","battery") else ("start_ns","end_ns","power_w")
    if any(any(r.get(k) is None for k in required) for r in rows):
        return {"reason":stream+" native row field missing", "sample_count":len(rows)}
    if stream in ("meter", "battery"):
        selected = sorted((r for r in rows if start_ns <= r["stamp_ns"] < end_ns),
                          key=lambda r: r["stamp_ns"])
        powers = [r["power_w"] for r in selected]
        intervals = [b["stamp_ns"]-a["stamp_ns"] for a,b in zip(selected, selected[1:])]
        durations = [length/len(powers)]*len(powers) if powers else []
    else:
        selected = sorted((r for r in rows if r["end_ns"] > start_ns and r["start_ns"] < end_ns),
                          key=lambda r: r["start_ns"])
        powers = [r["power_w"] for r in selected]
        intervals = [r["end_ns"]-r["start_ns"] for r in selected]
        durations = [(min(end_ns,r["end_ns"])-max(start_ns,r["start_ns"]))/1e9 for r in selected]
    duplicates = sum(v == 0 for v in intervals) if stream in ("meter", "battery") else 0
    positive = [v for v in intervals if v > 0]
    cadence_ns = statistics.median(positive) if positive else None
    lags = math.floor(10_000_000_000/cadence_ns) if cadence_ns else None
    result = {"sample_count": len(powers), "duplicate_stamp_count": duplicates,
              "native_interval_ns": cadence_ns, "lag_count": lags,
              "support_durations_s": durations,
              "method": "duration_weighted_newey_west_bartlett_10s_iid_floor_v2"}
    if powers and sum(durations) > 0:
        result["mean_w"] = (math.fsum(powers)/len(powers) if stream in ("meter","battery") else
                            math.fsum(p*d for p,d in zip(powers,durations))/math.fsum(durations))
    if len(powers) < 2 or not positive or length <= 0:
        result["reason"] = stream+" insufficient native samples"
    elif length < 30 or len(powers) < 3*(lags+1):
        result["reason"] = stream+" support below three 10 s bandwidths"
    else:
        estimate = estimate_newey_west_bartlett(powers, lags, durations)
        result["variance_w2"] = estimate.governed_variance_of_mean_w2
    return result


def combined_idle(pre, post):
    """Mean of span means; keep means even if an SE cannot be computed."""
    result = {}
    for stream in ("rails", "gpu", "meter", "battery"):
        a,b = pre[stream],post[stream]
        stats = result[stream] = {}
        try:
            if "mean_w" in a and "mean_w" in b:
                stats.update(pre_w=a["mean_w"],post_w=b["mean_w"])
            if "reason" in a or "reason" in b:
                stats["reason"] = a.get("reason",b.get("reason"))
            else:
                stats["se_w"] = math.sqrt(a["variance_w2"]+b["variance_w2"])/2
            arithmetic(stream+" idle pre/post", lambda: stats)
        except (ValueError, OverflowError) as exc:
            result[stream] = {"reason":stream+" idle power_w arithmetic unavailable: "+str(exc)}
    m,b = result["meter"],result["battery"]
    dc = result["dc"] = {}
    try:
        if "pre_w" in m and "pre_w" in b:
            dc.update(pre_w=m["pre_w"]+b["pre_w"],post_w=m["post_w"]+b["post_w"])
        if "reason" in m or "reason" in b:
            dc["reason"] = m.get("reason",b.get("reason"))
        else:
            dc["se_w"] = m["se_w"]+b["se_w"]
        arithmetic("meter/battery idle pre/post", lambda: dc)
    except (ValueError, OverflowError) as exc:
        result["dc"] = {"reason":"meter/battery idle power_w arithmetic unavailable: "+str(exc)}
    return result


def meter_gap_bound(gaps, *, duration_s, idle_lengths_s, adapter_max_w,
                    adapter_source, battery_max_w, battery_source):
    """§3 R5: missing samples × 20 ms × (adapter rating + battery maximum)."""
    result = {"gaps": gaps, "adapter_max_w": adapter_max_w, "adapter_source": adapter_source,
              "battery_max_w": battery_max_w, "battery_source": battery_source}
    reason = None
    if not adapter_source or not battery_source:
        reason = "gap power sources must be named"
    elif adapter_max_w is None:
        reason = "adapter rating missing"
    elif battery_max_w is None:
        reason = "battery maximum missing"
    if reason:
        return {**result, "reason": reason, "description": not_defined(reason), "bound_j": None}
    battery_max_w = max(0, battery_max_w)
    pmax = adapter_max_w+battery_max_w
    terms = []
    for gap in gaps:
        n,span = gap.get("missing_samples"),gap.get("span")
        if type(n) is not int or n < 0 or span not in ("stream", "pre", "post"):
            reason = "meter_gaps missing_samples needs a nonnegative integer and span must be stream/pre/post"
            return {**result, "reason":reason,"description":not_defined(reason),"bound_j":None,"terms":terms}
        if span != "stream" and idle_lengths_s.get(span,0) <= 0:
            reason = "gap idle span has no positive duration"
            return {**result, "reason":reason,"description":not_defined(reason),"bound_j":None,"terms":terms}
        weight = 1 if span == "stream" else duration_s/(2*idle_lengths_s[span])
        terms.append({**gap, "missing_s": n*.020, "weight": weight, "bound_j": n*.020*pmax*weight})
    return {**result,"bound_j": math.fsum(t["bound_j"] for t in terms), "terms": terms,
            "P_max_w": pmax,"battery_max_w": battery_max_w}


def describe_share(rails, dc):
    if dc is None or not isinstance(dc.get("halfwidth"),(int,float)) or dc["delta"]-dc["halfwidth"] <= 0:
        return {"f": not_defined("DC contrast not valid"), "df": not_defined("DC contrast not valid")}
    if rails is None or not isinstance(rails.get("halfwidth"),(int,float)):
        return {"f": not_defined("rails contrast missing"), "df": not_defined("rails contrast missing")}
    try:
        f = arithmetic("rails/DC delta share", lambda: rails["delta"]/dc["delta"])
        return arithmetic("rails/DC halfwidth share", lambda: {"f":f,
            "df": (rails["halfwidth"]+abs(f)*dc["halfwidth"])/abs(dc["delta"])})
    except ValueError as exc:
        return {key:not_defined(str(exc)) for key in ("f","df")}


def describe_gpu_arms(calls):
    """Native-interval means: residency over time, frequency over active time.

    The capture decoder supplies active_freq_mhz_weighted from DVFM states.
    No GPU state is reconstructed from power, and no class reads this result.
    """
    result = {}
    for arm in ("R","C"):
        try:
            own = [c for c in calls if c.get("arm") == arm]
            if len(own) != 2:
                raise ValueError("two complete GPU arm calls missing")
            total_ns = active_ns = weighted_mhz_ns = 0
            frequency_missing = False
            for call in own:
                receipt = call["receipt"]
                start,end = receipt["start_ns"],receipt["end_ns"]
                rows = call.get("gpu_state")
                if not isinstance(rows,list) or not rows:
                    raise ValueError("GPU frequency/residency missing")
                covered = 0
                previous = None
                for row in rows:
                    a,b = row["start_ns"],row["end_ns"]
                    if type(a) is not int or type(b) is not int or b <= a or previous is not None and a < previous:
                        raise ValueError("GPU native support invalid")
                    previous = b
                    length = max(0,min(b,end)-max(a,start))
                    if not length:
                        continue
                    idle = row["state"].get("idle_ratio")
                    freq = row["state"].get("active_freq_mhz_weighted")
                    if not finite_number(idle) or not 0 <= idle <= 1:
                        raise ValueError("GPU idle_ratio missing or invalid")
                    active = length*(1-idle)
                    covered += length
                    total_ns += length
                    active_ns += active
                    if not finite_number(freq) or freq < 0:
                        frequency_missing = True
                    else:
                        weighted_mhz_ns += active*freq
                if covered != end-start:
                    raise ValueError("GPU native support incomplete")
            result[arm] = arithmetic("GPU native frequency/residency means",lambda: {"active_residency":active_ns/total_ns,
                "active_frequency_mhz":(not_defined("GPU active frequency missing") if frequency_missing else
                    weighted_mhz_ns/active_ns if active_ns else not_defined("GPU active time is zero"))})
        except (KeyError,TypeError,ValueError,OverflowError,ZeroDivisionError) as exc:
            result[arm] = {key:not_defined(str(exc)) for key in ("active_frequency_mhz","active_residency")}
    return result


def classify(delta, halfwidth, kappa, *, reason=None):
    """§4 ordered classes, in J/GB; undefined descriptions do not enter here."""
    if reason:
        return {"class": "UNDETERMINED", "reason": reason}
    upper = arithmetic("delta/halfwidth upper endpoint", lambda: delta+halfwidth)
    lower = arithmetic("delta/halfwidth lower endpoint", lambda: delta-halfwidth)
    if upper < 0:
        return {"class": "UNDETERMINED", "reason": "contrast negative"}
    if lower > 0:
        return {"class": "RESOLVED"}
    epsilon0 = 1e9/(512*39_852_331_520)
    level = arithmetic("delta/halfwidth/check.kappa attribution ratio",
                       lambda: kappa*max(abs(lower),abs(upper)))
    if level <= epsilon0:
        return {"class": "BELOW ATTRIBUTION LEVEL"}
    return {"class": "NOT RESOLVED", "upper_limit": arithmetic("delta/halfwidth/check.kappa upper_limit", lambda: kappa*upper)}


# Executable dependency table: every derived reducer node is evaluated only
# after these exact parents are numeric. Arm nodes are expanded uniformly below.
REDUCER_DEPENDENCIES = {
    "{arm}.xi": ("{arm}.e0", "{arm}.e1", "{arm}.n0", "{arm}.n1"),
    "{arm}.x": ("{arm}.e0", "{arm}.e1", "{arm}.n0", "{arm}.n1"),
    "{arm}.rep": ("{arm}.xi", "{arm}.n0", "{arm}.n1"),
    "{arm}.dx": ("{arm}.u0", "{arm}.u1", "{arm}.n0", "{arm}.n1", "{arm}.rep"),
    "delta": ("R.x", "C.x"),
    "halfwidth": ("R.dx", "C.dx"),
    "upper_limit": ("delta", "halfwidth", "kappa"),
    "raw_stream_j_per_byte": ("R.x",),
}


def arithmetic(path, operation):
    """Guard a calculation and its numeric output; retain the input leaf path."""
    try:
        value = operation()
        def check(v):
            if isinstance(v, dict):
                for child in v.values(): check(child)
            elif isinstance(v, (list, tuple)):
                for child in v: check(child)
            elif type(v) in (int, float) and not finite_number(v):
                raise ValueError("non-finite arithmetic")
        check(value)
        return value
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(path+" arithmetic unavailable: "+str(exc)) from exc


def reduce_boundary(calls, sizes, boundary):
    """§3: evaluate the dependency graph, retaining independent H4 nodes."""
    nodes, arms, errors, origins = {}, {}, {}, {}
    def node(key, dependencies, operation, reason):
        origins[key] = tuple(dict.fromkeys(p for d in dependencies for p in origins.get(d, ())))
        reason += " from "+", ".join(origins[key])
        failure = next((errors[d] for d in dependencies if not finite_number(nodes.get(d))), None)
        try:
            if failure:
                raise ValueError(failure)
            nodes[key] = arithmetic(reason, operation)
        except ValueError as exc:
            errors[key] = str(exc)
            nodes[key] = not_defined(str(exc))
    for arm in ("R", "C"):
        rows = [c for c in calls if c["arm"] == arm]
        prefix = arm+"."
        for j in range(2):
            row = rows[j] if j < len(rows) else {}
            data = row.get("boundaries", {}).get(boundary, {})
            why = data.get("reason") or next(iter(row.get("prerequisites",{}).get(boundary,[])),
                                             "two complete arm calls missing")
            for key, value in (("e", data.get("excess_j")), ("u", data.get("bound_j")), ("n", row.get("N"))):
                name = prefix+key+str(j)
                position = next((i for i,c in enumerate(calls) if c is row), None)
                root = f"records[{position}]"
                native = ("meter","battery") if boundary == "dc" else ("rails","meter","battery") if boundary == "rest" else (boundary,)
                leaves = tuple(root+".harvest.energy_j."+b for b in native)
                origins[name] = ((root+".receipt.repeats",) if key == "n" else leaves+
                    tuple(root+".harvest.idle."+span+"."+b+".power_w" for span in ("pre","post") for b in native)+
                    ((root+".harvest.anchor_shift_j",root+".harvest.r_max_s",root+".harvest.meter_edge_w",
                      root+".harvest.battery_edge_j",root+".harvest.meter_gaps") if key == "u" else ()))
                nodes[name] = value if finite_number(value) else not_defined(why)
                if not finite_number(value): errors[name] = why
        e0,e1,u0,u1,n0,n1 = (prefix+k for k in ("e0","e1","u0","u1","n0","n1"))
        # These arm dependencies are instantiated identically for both arms.
        deps = {key.split(".")[1]:tuple(d.format(arm=arm) for d in parents)
                for key, parents in REDUCER_DEPENDENCIES.items() if "{arm}" in key}
        # xi is a pair, so register it separately from scalar graph parents.
        try:
            why = next((errors[d] for d in deps["xi"] if d in errors), None)
            if why: raise ValueError(why)
            xi = arithmetic(arm+" excess/N from "+", ".join(p for d in deps["xi"] for p in origins[d]), lambda: [nodes[e0]/nodes[n0],nodes[e1]/nodes[n1]])
            nodes[prefix+"xi"] = 1  # pair availability prerequisite
            origins[prefix+"xi"] = tuple(p for d in deps["xi"] for p in origins[d])
        except ValueError as exc:
            xi = not_defined(str(exc)); nodes[prefix+"xi"] = xi; errors[prefix+"xi"] = str(exc)
        node(prefix+"x", deps["x"], lambda: (nodes[e0]+nodes[e1])/(nodes[n0]+nodes[n1]), arm+" excess/N")
        node(prefix+"rep", deps["rep"], lambda: abs(xi[0]-xi[1])*max(nodes[n0],nodes[n1])/(nodes[n0]+nodes[n1]), arm+" repeatability")
        node(prefix+"dx", deps["dx"], lambda: (nodes[u0]+nodes[u1])/(nodes[n0]+nodes[n1])+nodes[prefix+"rep"], arm+" bound/N")
        arms[arm] = {k:nodes[prefix+k] for k in ("x","dx","rep")}
        arms[arm]["xi"] = xi
    b = sizes["R"]
    v = nodes
    operations = {
        "delta": lambda: (v["R.x"]-v["C.x"])/b*1e9,
        "halfwidth": lambda: (v["R.dx"]+v["C.dx"])/b*1e9,
        "raw_stream_j_per_byte": lambda: v["R.x"]/b,
    }
    for key, deps in REDUCER_DEPENDENCIES.items():
        if "{arm}" in key or key == "upper_limit": continue
        node(key, deps, operations[key], boundary+" "+key+" from records receipt/harvest")
    result = {key:v[key] for key in operations}
    result["arms"] = arms
    if "halfwidth" in errors:
        result.update(reason=errors["halfwidth"], description=not_defined(errors["halfwidth"]),
                      upper_limit=not_defined(errors["halfwidth"]))
    return result


def read_known_bytes(records, check):
    """Print every record and all computable values, even with absent prerequisites."""
    original_records, original_check = records, check
    validation = []
    def take(value, spec, path, betas, errors, empty=None):
        valid, reason = input_value(value, spec, path)
        if reason:
            labels = {"adapter_max_w":"adapter rating missing", "adapter_source":"gap power sources must be named",
                "battery_source":"gap power sources must be named", "r_max_s":"r_max missing",
                "meter_edge_w":"meter edge powers missing", "battery_edge_j":"battery edge energy missing or invalid",
                "anchor_shift_j":"anchor shift bound missing", "tau_s":"tau missing"}
            label = labels.get(path.rsplit(".",1)[-1])
            if label:
                reason += " ("+label+")"
            errors.append((betas, reason))
            return empty
        return valid
    names = ("rails","gpu","dc","rest")
    check_errors = []
    check = validated_check(check)
    check_reason = check.get("reason")
    if check_reason:
        check_errors.append((names,check_reason))
    records = take(records, [{}], "records", names, check_errors, []) if not isinstance(records,list) else records
    normalized = []
    for i, raw in enumerate(records):
        errors = list(check_errors)
        path = f"records[{i}]"
        raw = take(raw, {}, path, names, errors, {})
        r = dict(take(raw.get("receipt", ABSENT), {}, path+".receipt", names, errors, {}))
        h = dict(take(raw.get("harvest", ABSENT), {}, path+".harvest", names, errors, {}))
        geometry = geometry_error(r,check.get("b"))
        if geometry:
            check_errors.append((names,geometry))
            errors.append((names,geometry))
        try:
            clock_duration_bound_ns(r)
        except ValueError as exc:
            why = "clock prerequisite missing ("+str(exc)+")"
            check_errors.append((names,why))
            errors.append((names,why))
        for key, spec in RECEIPT_INPUTS.items():
            r[key] = take(r.get(key, ABSENT), spec, path+".receipt."+key, names, errors)
        if all(r[key] is not None for key in ("bytes_per_read", "repeats", "bytes_read")) and (
                r["bytes_read"] != r["bytes_per_read"]*r["repeats"]):
            errors.append((names, path+".receipt.repeats/bytes_read missing or invalid (bytes_read != bytes_per_read * repeats)"))
        def stack_leaves(value, spec, leaf_path, field=""):
            if isinstance(spec, dict):
                source = value if isinstance(value, dict) else {}
                return {**source, **{k: stack_leaves(source.get(k, ABSENT), child, leaf_path+"."+k,
                                       field+"."+k if field else k) for k, child in spec.items()}}
            betas = (("rails", "rest", "gpu") if field == "measurement_boundary_label.rails"
                     else names if field in PHYSICAL_FIELDS else ())
            valid, error = input_value(value, spec, leaf_path)
            if error:
                if betas:
                    errors.append((betas, error))
                    return None
                return "not recorded ("+error+")"
            return valid
        _, order_error = input_value(r, RECEIPT_INPUTS, path+".receipt")
        if order_error:
            errors.append((names, order_error))
        r["stack"] = stack_leaves(r.get("stack", ABSENT), STACK_INPUTS, path+".receipt.stack")
        h["capture_stack"] = stack_leaves(h.get("capture_stack", ABSENT), CAPTURE_INPUTS, path+".harvest.capture_stack")
        energy = take(h.get("energy_j", ABSENT), {}, path+".harvest.energy_j", names, errors, {})
        h["energy_j"] = {k: take(energy.get(k, ABSENT), NUMBER if k == "battery" else NONNEG, path+".harvest.energy_j."+k,
            ("dc",) if k in ("meter","battery") else (k,), errors) for k in NATIVE_INPUTS}
        idle = take(h.get("idle", ABSENT), {}, path+".harvest.idle", names, errors, {})
        h["idle"] = {}
        for span in ("pre", "post"):
            block = take(idle.get(span, ABSENT), {}, path+".harvest.idle."+span, names, errors, {})
            h["idle"][span] = {k: take(block.get(k, ABSENT), ("native", (spec,
                r.get("idle_"+span+"_start_ns"))),
                path+".harvest.idle."+span+"."+k, ("dc",) if k in ("meter","battery") else (k,), errors, [])
                for k, spec in NATIVE_INPUTS.items()}
        for key, spec, betas in (("tau_s",NONNEG,names), ("r_max_s",NONNEG,("dc",)),
            ("meter_edge_w",EDGES,("dc",)), ("battery_edge_j",EDGES,("dc",)),
            ("anchor_shift_j",NONNEG,("rails","gpu")),
            ("battery_samples",("native", (NATIVE_INPUTS["battery"],
                r.get("idle_pre_start_ns"))),("dc",))):
            h[key] = take(h.get(key, ABSENT), spec, path+".harvest."+key, betas, errors,
                          [] if key == "battery_samples" else None)
        gaps = h.get("meter_gaps", ABSENT)
        if gaps != []:
            gaps = take(gaps, [{"span":TEXT,"missing_samples":COUNT}], path+".harvest.meter_gaps", ("dc",), errors, [])
        h["meter_gaps"] = gaps
        if gaps:
            for key, spec in (("adapter_max_w",POSITIVE),("adapter_source",TEXT),("battery_source",TEXT)):
                h[key] = take(h.get(key, ABSENT), spec, path+".harvest."+key, ("dc",), errors)
        normalized.append({"receipt":r,"harvest":h})
        validation.append(errors)
    records = normalized
    sizes = {"R":check.get("b"),"C":check.get("b")}
    kappa = check.get("kappa")
    output = {"check":json_evidence(original_check),"residency":check,
              "input_records":json_evidence(original_records),"calls":[],"boundaries":{},
              "stack_comparisons":[],"geometry_checks":[]}
    reasons = [why for _, why in check_errors]
    affected = {b:[] for b in names}
    if len(records) != len(ORDER):
        reasons.append("the test requires all four calls")
    if check.get("b") is not None:
        order = [r.get("receipt",{}).get("arm") for r in records]
        if order != list(ORDER):
            reasons.append("records must be the complete stamped palindrome")
        stamps = [r.get("receipt",{}).get("start_ns") for r in records]
        if any(v is None for v in stamps) or any(b <= a for a,b in zip(stamps,stamps[1:])):
            reasons.append("records must be in stamped call order")
    reference,versions = registered_stack()
    for i,record in enumerate(records,1):
        receipt,h = record.get("receipt",{}),record.get("harvest",{})
        stack_check = compare_stack((receipt.get("stack") or {}),reference,versions,capture_stack=h.get("capture_stack"))
        output["stack_comparisons"].append(stack_check)
        error = geometry_error(receipt,check.get("b"))
        output["geometry_checks"].append({"ok":error is None,"reason":error})
        fields = [f for f in stack_check["physical_differences"] if f != "measurement_boundary_label.rails"]
        if fields:
            reasons.append("stack differs in: "+", ".join(fields))
        rail_field = "measurement_boundary_label.rails"
        if rail_field in stack_check["physical_differences"] or rail_field in stack_check["pending_fields"]:
            why = "measured rails boundary differs" if rail_field in stack_check["physical_differences"] else "measured rails boundary missing"
            for beta in ("rails","rest"):
                affected[beta].append(why+" (measurement_boundary_label.rails)")
        call = {"receipt":receipt,"arm":None,"boundaries":{},"prerequisites":{b:[] for b in names}}
        output["calls"].append(call)
        def missing(beta, reason):
            call["prerequisites"][beta].append(reason)
            affected[beta].append(reason)
        for betas, why in validation[i-1]:
            if tuple(betas) == names:
                reasons.insert(0, why)
            for beta in betas:
                missing(beta, why)
        rails = _field(h["capture_stack"], "measurement_boundary_label.rails")
        reference_rails, reference_error = input_value(_field(reference, "measurement_boundary_label.rails"),
                                                       [TEXT], "reference.measurement_boundary_label.rails")
        if rails is None or "gpu_power" not in rails or reference_error or "gpu_power" not in reference_rails:
            missing("gpu", "gpu_power missing from recorded rail set (measurement_boundary_label.rails)")
        try:
            _, error = input_value(receipt, RECEIPT_INPUTS, f"records[{i-1}].receipt")
            if error:
                raise ValueError(error)
            n = receipt["repeats"]
            t = (receipt["end_ns"]-receipt["start_ns"])/1e9
            if n <= 0 or t <= 0:
                raise ValueError("positive repeats and end_ns-start_ns required")
            arm = receipt.get("arm")
            arithmetic(f"records[{i-1}].receipt.end_ns/start_ns", lambda: t)
            call.update(arm=arm,N=n,T=t,t_s=t/n)
            if h.get("tau_s") is None:
                raise ValueError("tau missing")
            trim_ns = arithmetic(f"records[{i-1}].harvest.tau_s / records[{i-1}].receipt.settle_s",
                                 lambda: round(max(0,h["tau_s"]-receipt["settle_s"])*1e9))
            spans = {name:(receipt["idle_"+name+"_start_ns"]+trim_ns,receipt["idle_"+name+"_end_ns"])
                     for name in ("pre","post")}
        except (KeyError,TypeError,ValueError,OverflowError) as exc:
            why = "call prerequisite missing in call "+str(i)+": "+str(exc)
            reasons.append(why)
            call["description"] = not_defined(why)
            continue
        prepost = {name:{stream:idle_statistics(h.get("idle",{}).get(name,{}).get(stream,[]),*span,stream)
                         for stream in ("rails","gpu","meter","battery")} for name,span in spans.items()}
        for span, streams in prepost.items():
            for stream, stats in streams.items():
                if "reason" in stats:
                    stats["reason"] = f"records[{i-1}].harvest.idle.{span}.{stream}.power_w: "+stats["reason"]
        idle = combined_idle(prepost["pre"],prepost["post"])
        for stream, stats in idle.items():
            if "reason" in stats and "records[" not in stats["reason"]:
                stats["reason"] = f"records[{i-1}].harvest.idle.pre/post.{stream}.power_w: "+stats["reason"]
        call.update(idle=idle,native_idle=prepost)
        energy = h.get("energy_j",{})
        battery_rows = h.get("battery_samples",[])
        if any(p.get("stamp_ns") is None or p.get("power_w") is None for p in battery_rows):
            missing("dc","battery poll field missing")
        battery = [p for p in battery_rows if p.get("stamp_ns") is not None and p.get("power_w") is not None and
                   receipt["idle_pre_start_ns"] <= p["stamp_ns"] < receipt["idle_post_end_ns"]]
        if not battery or any(not h.get("idle",{}).get(name,{}).get("battery") for name in ("pre","post")) or energy.get("battery") is None:
            missing("dc",f"battery reading missing in call {i}")
        gap_reason = next((why for _, why in validation[i-1] if ".harvest.meter_gaps" in why), None)
        gaps = ({"bound_j":None,"reason":gap_reason,"description":not_defined(gap_reason),"terms":[]}
                if gap_reason else {"bound_j":0,"terms":[]})
        if h.get("meter_gaps"):
            try:
                gaps = meter_gap_bound(h["meter_gaps"],duration_s=t,
                    idle_lengths_s={name:(end-start)/1e9 for name,(start,end) in spans.items()},
                    adapter_max_w=h.get("adapter_max_w"),adapter_source=h.get("adapter_source"),
                    battery_max_w=max((p["power_w"] for p in battery),default=None),battery_source=h.get("battery_source"))
                arithmetic(f"records[{i-1}].harvest.meter_gaps/adapter_max_w/battery_samples.power_w", lambda: gaps)
            except (ValueError, OverflowError) as exc:
                why = f"records[{i-1}].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: {exc}"
                gaps = {"bound_j":None,"reason":why,"description":not_defined(why),"terms":[]}
            if "reason" in gaps:
                missing("dc",gaps["reason"])
        call["meter_gaps"] = gaps
        for beta in ("rails","gpu","dc"):
            try:
                stats = idle[beta]
                if "reason" in stats:
                    missing(beta,"idle variance not defined ("+stats["reason"]+")")
                if beta == "dc":
                    e = None if any(energy.get(k) is None for k in ("meter","battery")) else energy["meter"]+energy["battery"]
                    for key in ("meter","battery"):
                        if energy.get(key) is None:
                            missing(beta,key+" stream integral missing")
                    for key,label in (("r_max_s","r_max missing"),("meter_edge_w","meter edge powers missing"),
                                      ("battery_edge_j","battery edge energy missing")):
                        if h.get(key) is None:
                            missing(beta,label)
                    if not call["prerequisites"][beta]:
                        edge = sum(h["meter_edge_w"])*(h["r_max_s"]+.020)+sum(h["battery_edge_j"])+gaps["bound_j"]
                else:
                    e = energy.get(beta)
                    if e is None:
                        missing(beta,beta+" stream integral missing")
                    if h.get("anchor_shift_j") is None:
                        missing(beta,"anchor shift bound missing")
                    edge = h.get("anchor_shift_j")
                if e is None or "pre_w" not in stats:
                    continue
                row = {"excess_j": (not_defined(stats["reason"]) if "reason" in stats else
                        arithmetic(f"records[{i-1}].harvest.energy_j/idle.{beta}",
                                   lambda: e-t*(stats["pre_w"]+stats["post_w"])/2)), "bound_j":None}
                if call["prerequisites"][beta]:
                    row["reason"] = call["prerequisites"][beta][0]
                    row["description"] = not_defined(row["reason"])
                else:
                    baseline = t*(abs(stats["pre_w"]-stats["post_w"])/2+2*stats["se_w"])
                    row.update(bound_j=edge+baseline,edge_bound_j=edge,baseline_bound_j=baseline)
                call["boundaries"][beta] = row
                arithmetic(f"records[{i-1}].harvest energy_j/idle/edges.{beta}",
                           lambda: call["boundaries"].get(beta, {}))
            except (OverflowError, ValueError) as exc:
                why = f"records[{i-1}].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.{beta} arithmetic unavailable: {exc}"
                missing(beta, why)
                call["boundaries"][beta] = {"excess_j":not_defined(why), "bound_j":None,
                                            "reason":why, "description":not_defined(why)}
        if all(b in call["boundaries"] for b in ("rails","dc")):
            r,d = (call["boundaries"][b] for b in ("rails","dc"))
            try:
                rest = {"excess_j": (d["excess_j"]-r["excess_j"] if all(finite_number(v["excess_j"]) for v in (d,r))
                                         else not_defined(d.get("reason",r.get("reason","excess missing")))),"bound_j":None}
                if r["bound_j"] is not None and d["bound_j"] is not None:
                    rest["bound_j"] = d["bound_j"]+r["bound_j"]
                else:
                    rest["reason"] = d.get("reason",r.get("reason"))
                    rest["description"] = not_defined(rest["reason"])
                call["boundaries"]["rest"] = rest
                arithmetic(f"records[{i-1}].harvest.energy_j/idle rails/dc rest", lambda: rest)
            except (ValueError, OverflowError) as exc:
                why = f"records[{i-1}].harvest.energy_j/idle rails/dc rest arithmetic unavailable: {exc}"
                missing("rest",why)
                call["boundaries"]["rest"] = {"excess_j":not_defined(why),"bound_j":None,"reason":why,"description":not_defined(why)}
        call["timing"] = {}
        for key in ("r_max_s", "tau_s", "operative_timing_bound_s"):
            value, error = input_value(h.get(key, ABSENT), NONNEG, "harvest."+key)
            call["timing"][key] = not_defined(error) if error else value
        for key, label in (("gpu_state","GPU frequency/residency missing"), ("thermal_spans","thermal journal missing")):
            value, error = input_value(h.get(key, ABSENT), ("json", None), "harvest."+key)
            h[key] = (not_defined(label if key not in h else label+": "+error) if error else value)
        call["gpu_state"] = h["gpu_state"]
        call["thermal"] = {"source":"hazards/monitor/thermal.jsonl","spans":h["thermal_spans"]}
    for beta in names:
        if check.get("b") is not None and all(sizes.values()):
            output["boundaries"][beta] = reduce_boundary(output["calls"],sizes,beta)
            why = output["boundaries"][beta].get("reason", "")
            if "arithmetic unavailable" in why:
                affected[beta].append(why)
    dc = output["boundaries"].get("dc")
    # DC is the common validity prerequisite. Keep other boundaries' numbers.
    invalid_dc_width = False
    if affected["dc"]:
        reasons.extend(affected["dc"])
    elif dc is None or not finite_number(dc.get("halfwidth")) or dc["halfwidth"] < 0:
        reasons.append("DC contrast input missing")
        invalid_dc_width = True
    elif dc["delta"]-dc["halfwidth"] <= 0:
        reasons.append("contrast not resolved")
    affected["rest"].extend(affected["rails"]+affected["dc"])
    output["reasons"] = list(dict.fromkeys(reasons+[r for rs in affected.values() for r in rs]))
    for beta in names:
        value = output["boundaries"].get(beta)
        reason = next(iter([why for _, why in check_errors]+affected[beta]+reasons),None)
        if value is None:
            reason = reason or "boundary input missing"
            value = {"class":"UNDETERMINED","reason":reason,"description":not_defined(reason)}
            if check.get("b") is None:
                value.update({key:not_defined(check_reason or "residency not resolved") for key in
                    ("delta","halfwidth","raw_stream_j_per_byte","arms")})
            output["boundaries"][beta] = value
        elif check_errors or invalid_dc_width:
            value.update({"class":"UNDETERMINED","reason":reason,"description":not_defined(reason),
                          "halfwidth":not_defined(reason),"upper_limit":not_defined(reason)})
        elif isinstance(value.get("halfwidth"),(int,float)) and (
                not finite_number(value["halfwidth"]) or value["halfwidth"] < 0):
            reason = beta+" halfwidth missing or invalid (must be finite and nonnegative)"
            value.update({"class":"UNDETERMINED","reason":reason,"description":not_defined(reason),
                          "halfwidth":not_defined(reason),"upper_limit":not_defined(reason)})
        elif not isinstance(value.get("halfwidth"),(int,float)):
            reason = reason or value.get("reason","bound input missing")
            value.update({"class":"UNDETERMINED","reason":reason,"description":not_defined(reason)})
        else:
            try:
                arithmetic(beta+" delta/halfwidth/check.kappa class", lambda:
                           [value["delta"]+value["halfwidth"],value["delta"]-value["halfwidth"]])
                upper_inputs = {**value,"kappa":kappa}
                if not reason and not all(finite_number(upper_inputs.get(k))
                                          for k in REDUCER_DEPENDENCIES["upper_limit"]):
                    raise ValueError(beta+" delta/halfwidth/check.kappa upper_limit prerequisite missing")
                value.update(arithmetic(beta+" delta/halfwidth/check.kappa upper_limit", lambda:
                    classify(value["delta"],value["halfwidth"],kappa,reason=reason)))
            except (ValueError, TypeError) as exc:
                reason = str(exc)
                value.update({"class":"UNDETERMINED","reason":reason,"upper_limit":not_defined(reason)})
            if reason:
                value["description"] = not_defined(reason)
    if check.get("b") is None:
        output["share"] = {k:not_defined(check_reason or "residency not resolved") for k in ("f","df")}
        output["gpu_power_contrast_w"] = not_defined(check_reason or "residency not resolved")
    else:
        rails = output["boundaries"]["rails"]
        output["share"] = describe_share(rails if "delta" in rails else None,dc)
        gpu = [c for c in output["calls"] if c["arm"] in ("R","C")]
        if len(gpu)==4 and all(finite_number(c["boundaries"].get("gpu",{}).get("excess_j")) for c in gpu):
            try:
                power = {arm:sum(c["boundaries"]["gpu"]["excess_j"] for c in gpu if c["arm"]==arm)/
                         sum(c["T"] for c in gpu if c["arm"]==arm) for arm in ("R","C")}
                output["gpu_power_contrast_w"] = arithmetic(
                    "records.harvest.energy_j.gpu/receipt.end_ns/start_ns", lambda: power["R"]-power["C"])
                arithmetic("records.harvest.energy_j.gpu/receipt.end_ns/start_ns", lambda: power)
            except (ValueError, OverflowError) as exc:
                output["gpu_power_contrast_w"] = not_defined(str(exc))
        else:
            output["gpu_power_contrast_w"] = not_defined("GPU spans missing")
    output["sizes"] = sizes if check.get("b") is not None else {a:not_defined(check_reason or "residency not resolved") for a in sizes}
    output["gpu_arm_state"] = describe_gpu_arms(output["calls"])
    for field in ("b","W","Q","G","geometry_source","phi_U","phi_U_fraction","rho_L","kappa"):
        value = check.get(field)
        output[field] = value if value is not None else not_defined(check_reason or "residency not resolved")
    output["hour_timing"] = {}
    for arm in ("R","C"):
        own = [c for c in output["calls"] if c.get("arm") == arm and "T" in c]
        output["hour_timing"][arm] = (sum(c["T"] for c in own)/sum(c["N"] for c in own)
            if len(own) == 2 else not_defined("two complete arm calls missing"))
    timing = output["hour_timing"]
    timing["D_s"] = (timing["R"]-timing["C"] if all(finite_number(timing[a]) for a in ("R","C"))
                      else not_defined(check_reason or "two complete arm calls missing"))
    timing["check_D_s"] = (check["rungs"][-1]["D_s"] if check.get("b") is not None
                              else not_defined(check_reason or "residency not resolved"))
    output["receipt_sha256"] = [hashlib.sha256(json.dumps(json_evidence(row.get("receipt") if isinstance(row,dict) else row),sort_keys=True).encode()).hexdigest()
                                  for row in (original_records or [])] if isinstance(original_records,list) else []
    hour, error = input_value(records[0]["harvest"].get("hour_as_run_s", ABSENT) if records else ABSENT,
                              NONNEG, "harvest.hour_as_run_s")
    output["hour_as_run_s"] = not_defined("session endpoints missing: "+error) if error else hour
    try:
        output["stamped_envelope_s"] = arithmetic("records.receipt.idle_post_end_ns/idle_pre_start_ns", lambda: (records[-1]["receipt"]["idle_post_end_ns"]-records[0]["receipt"]["idle_pre_start_ns"])/1e9)
    except (IndexError,KeyError,TypeError,ValueError,OverflowError):
        output["stamped_envelope_s"] = not_defined("session endpoints missing")
    output = json_evidence(output)
    output["printed"] = printed_record(output)
    return output


def interval_places(halfwidth):
    # Zero has no significant digit; a fixed two-decimal display avoids repr.
    if halfwidth == 0:
        return 2
    return 1-math.floor(math.log10(float(format(halfwidth,".2g"))))


def format_interval(value, halfwidth):
    """§14 H2: two significant half-width digits; estimate at the same place."""
    if halfwidth == 0:
        return f"{value:.2f} ± 0.00"
    if not finite_number(halfwidth) or halfwidth < 0:
        raise ValueError("halfwidth must be finite and nonnegative")
    rounded = arithmetic("halfwidth print conversion", lambda: float(format(halfwidth, ".2g")))
    places = 1-math.floor(math.log10(rounded))
    return f"{round(value,places):.{max(0,places)}f} ± {round(halfwidth,places):.{max(0,places)}f}"


def printed_record(result):
    """Claim-side sentences and test-record descriptions; full numeric input stays above."""
    printed = {"claim_lines": {}, "contrasts": {}, "share": result["share"],
               "stack_comparisons": result["stack_comparisons"]}
    printed["geometry"] = {key:result[key] for key in ("b","W","Q","G","geometry_source","phi_U_fraction")}
    printed["bias"] = {key:(format(result[key],".4g") if finite_number(result[key]) else result[key])
                       for key in ("rho_L","kappa")}
    for boundary,value in result["boundaries"].items():
        try:
            if isinstance(value.get("halfwidth"),(int,float)) and (
                    not finite_number(value["halfwidth"]) or value["halfwidth"] < 0):
                raise ValueError("halfwidth must be finite and nonnegative")
            interval = (format_interval(value["delta"],value["halfwidth"]) if isinstance(value.get("halfwidth"),(int,float))
                        else ((f"{value['delta']} J/GB; " if isinstance(value.get("delta"),(int,float)) else "")+value["description"]))
        except (ValueError, OverflowError) as exc:
            why = boundary+" delta/halfwidth print arithmetic unavailable: "+str(exc)
            value.update({"class":"UNDETERMINED","reason":why,"description":not_defined(why),
                          "halfwidth":not_defined(why),"upper_limit":not_defined(why)})
            interval = not_defined(why)
        printed["contrasts"][boundary] = interval
        if boundary not in ("rails","rest") or value["class"] == "RESOLVED":
            continue
        if value["class"] == "UNDETERMINED":
            line = f"Known-bytes check: {boundary} memory-traffic attribution is undetermined ({value['reason']})."
        elif value["class"] == "BELOW ATTRIBUTION LEVEL":
            line = (f"Known-bytes check: {boundary} energy per DRAM-sourced byte differed from cache-sourced by {interval} J/GB "
                    f"(DRAM minus cache, {result['b']}-byte matched dispatches), within the 1 J-per-run attribution level ({1e9/(512*39_852_331_520):.4g} J/GB) "
                    f"after the contrast-fraction correction ×{result['kappa']:.4g}; {boundary} lines here carry no resolvable memory-traffic energy.")
        else:
            # The upper limit uses the estimate's printed decimal place.
            digits = interval_places(value["halfwidth"])
            line = (f"Known-bytes check: the {boundary} response to DRAM-sourced bytes is not resolved ({interval} J/GB, "
                    f"contrast-fraction-corrected upper limit {round(value['upper_limit'],digits):.{max(0,digits)}f} J/GB); "
                    f"whether {boundary} lines include memory-traffic energy is not established.")
        printed["claim_lines"][boundary] = line
    if isinstance(result["share"]["f"],(float,int)):
        try:
            if not finite_number(result["share"]["df"]) or result["share"]["df"] < 0:
                raise ValueError("share df must be finite and nonnegative")
            printed["share"] = format_interval(result["share"]["f"],result["share"]["df"])
        except (ValueError, OverflowError) as exc:
            result["share"] = {key:not_defined("rails/DC share print: "+str(exc)) for key in ("f","df")}
            printed["share"] = result["share"]
    return printed


def _seconds(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("idle and settle seconds must be finite nonnegative numbers")
    return value


# MLX array dimensions are signed 32-bit: a flat uint8 payload stops at
# 2**31 - 1 bytes, and mx.ones raises TypeError above it (KB attempt 2 stopped
# at its 2**31-byte scan size). A C-contiguous (rows, 2**30) payload holds the
# same bytes and mx.sum over all axes reads each once: measured on this Mac
# 2026-10-30, 369-400 GB/s from 2**30 to 2**33 B, sums exact mod 2**32.
PAYLOAD_ROW_BYTES = 2 ** 30


def payload_shape(byte_count):
    if byte_count < 2 ** 31:
        return (byte_count,)
    if byte_count % PAYLOAD_ROW_BYTES:
        raise ValueError("a payload of 2**31 bytes or more must be whole 2**30-byte rows")
    return (byte_count // PAYLOAD_ROW_BYTES, PAYLOAD_ROW_BYTES)


def allocate_ring(mx, b=GEOMETRY_BYTES):
    """Rule §1: (Q,b), both axes below the signed 32-bit MLX dimension limit."""
    try:
        ring = mx.ones((RING_BYTES//b,b),dtype=mx.uint8)
        mx.eval(ring)
        mx.synchronize()
        return ring
    except (MemoryError,RuntimeError) as exc:
        raise MemoryError(f"allocation failed ({RING_BYTES} B ring)") from exc


def ring_views(mx, ring, b):
    # reshape and row indexing share contiguous storage; no payload copy.
    ring = mx.reshape(ring,(RING_BYTES//b,b))
    rows = [ring[i] for i in range(RING_BYTES//b)]
    mx.eval(*rows)
    mx.synchronize()
    return rows


def stream(byte_count, repeats, *, device, arm="R", idle_s=57.6, settle_s=3,
           mx=None, clock_ns=None, sleep=None, repo_root=ROOT,
           prepared_views=None, warm=True, rung_index=None, check_phase=None):
    if (type(byte_count) is not int or byte_count <= 0 or byte_count > GEOMETRY_BYTES or
            RING_BYTES % byte_count or type(repeats) is not int or repeats <= 0 or
            repeats % (RING_BYTES//byte_count)):
        raise ValueError("payload must divide the ring, stay on the small launch, and repeats must be whole sweeps")
    if arm not in ("R","C","check-R","check-C"):
        raise ValueError("arm must be R, C, check-R or check-C")
    idle_s, settle_s = _seconds(idle_s), _seconds(settle_s)
    if not isinstance(device, str) or not device.strip():
        raise ValueError("device must be the checkout's hardware_target.id")
    if mx is None:
        import mlx.core as mx
    if clock_ns is None:
        clock_ns = lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    sleep = sleep or time.sleep
    stack = collect_stack(mx,device,repo_root=repo_root)
    reference,versions = registered_stack(repo_root)
    comparison = compare_stack(stack,reference,versions)
    reference_check = checkout_reference_check(repo_root)
    rows = prepared_views
    if rows is None:
        ring = allocate_ring(mx,byte_count)
        rows = ring_views(mx,ring,byte_count)
    q = RING_BYTES//byte_count
    if len(rows) != q:
        raise ValueError("prepared views must cover the ring")
    views = list(rows) if arm.endswith("R") else [rows[0]]*q
    # Record observed array leaves, rather than restating the requested size.
    view_nbytes = views[0].nbytes
    dtype = "uint8" if views[0].dtype == mx.uint8 else str(views[0].dtype)
    if warm:
        mx.eval(mx.sum(views[0]))
        mx.synchronize()
    if settle_s:
        sleep(settle_s)
    pre_start = clock_ns()
    if idle_s:
        sleep(idle_s)
    pre_end = clock_ns()
    if settle_s:
        sleep(settle_s)
    start = clock_ns()
    for k in range(repeats):
        result = mx.sum(views[k % q])
        mx.eval(result)
    mx.synchronize()
    end = clock_ns()
    if settle_s:
        sleep(settle_s)
    post_start = clock_ns()
    if idle_s:
        sleep(idle_s)
    post_end = clock_ns()
    stamps = (pre_start,pre_end,start,end,post_start,post_end)
    if any(type(t) is not int or t < 0 for t in stamps):
        raise ValueError("CLOCK_MONOTONIC_RAW stamps must be nonnegative integer nanoseconds")
    if any(b < a for a,b in zip(stamps,stamps[1:])) or end <= start:
        raise ValueError("stream has no positive ordered monotonic span")
    if idle_s and (pre_end <= pre_start or post_end <= post_start):
        raise ValueError("idle has no positive monotonic span")
    return {"schema_version":SCHEMA,"non_claim":True,**clock_metadata(),
            "start_ns":start,"end_ns":end,"idle_pre_start_ns":pre_start,"idle_pre_end_ns":pre_end,
            "idle_post_start_ns":post_start,"idle_post_end_ns":post_end,"idle_s":idle_s,"settle_s":settle_s,
            "duration_s":(end-start)/1e9,"bytes_per_read":byte_count,"repeats":repeats,
            "bytes_read":byte_count*repeats,"logical_bytes":byte_count*repeats,
            "arm":arm,"ring_bytes":RING_BYTES,"ring_shape":[q,byte_count],"dtype":dtype,
            "view_nbytes":view_nbytes,"view_order":"rotate" if arm.endswith("R") else "repeat",
            "sweeps":repeats//q,"geometry_branch_bytes":GEOMETRY_BYTES,
            "geometry_source":GEOMETRY_SOURCE,"launch_side":"small" if view_nbytes <= GEOMETRY_BYTES else "large",
            "rung_index":rung_index,"check_phase":check_phase,
            "boundary":"logical uint8 row-view reads; excludes initialization and reduction workspace",
            "stack":stack,"stack_check":comparison,"reference_check":reference_check}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "read":
        parser = argparse.ArgumentParser(description="Read §3/§4 receipts and native harvest products")
        parser.add_argument("input", type=Path, help="JSON object with check and records")
        args = parser.parse_args(argv[1:])
        data = json.loads(args.input.read_text())
        data, error = input_value(data, {}, "input")
        data = data if error is None else {}
        print(json.dumps(read_known_bytes(data.get("records"), data.get("check")), allow_nan=False, indent=2))
        return 0
    if argv and argv[0] == "check":
        parser = argparse.ArgumentParser(description="Read §1 v3 residency receipts, pilots and calls in run order")
        parser.add_argument("receipts",type=Path)
        args = parser.parse_args(argv[1:])
        print(json.dumps(residency_check(json.loads(args.receipts.read_text())),allow_nan=False,indent=2))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bytes", type=int, required=True, dest="byte_count")
    parser.add_argument("--repeats", type=int, required=True)
    parser.add_argument("--arm",choices=("R","C"),required=True)
    parser.add_argument("--device", required=True, help="hardware_target.id from the checkout's run config")
    parser.add_argument("--idle-s", type=float, default=57.6)
    parser.add_argument("--settle-s", type=float, default=3)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = stream(args.byte_count, args.repeats, device=args.device, arm=args.arm,
                    idle_s=args.idle_s, settle_s=args.settle_s)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
