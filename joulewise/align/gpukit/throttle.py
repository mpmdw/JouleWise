"""Snapshot NVIDIA clock-event reasons, counters and board power limits.

Field names: NVIDIA nvsmi_device_v7.dtd (embedded driver DTD mirrored at
https://github.com/rai-project/nvidia-smi/blob/864eb441c9ae3171601e2e9df942b9ca386612c0/_fixtures/example2.xml)
and v13 driver XML names corroborated by
https://github.com/influxdata/telegraf/blob/2156aa5089436522eec36b05fad94d850c728388/plugins/inputs/nvidia_smi/schema_v13/types.go .
Semantics: https://docs.nvidia.com/deploy/nvidia-smi/index.html#clocks-event-reasons
and #clocks-event-reason-counters. Accessed through the public GitHub mirrors
2026-10-22; direct NVIDIA documentation was unavailable in this build seat.
Raw XML with --dtd is retained for the actual installed driver's definitions.
All missing evidence and throttle observations are flags, never refusals.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

# Old drivers say "throttle"; current ones say "event". Keep original names in
# the payload, alongside semantic categories so counter deltas survive a rename.
REASONS = ("hw_power_brake_slowdown", "hw_slowdown", "sw_power_cap")
COUNTERS = ("hw_power_brake", "hw_therm_slowdown", "sw_power_cap")
POWER_FIELDS = {
    "default": ("default_power_limit",),
    "enforced": ("enforced_power_limit",),
    "current": ("current_power_limit", "power_limit"),
}


def parse_snapshot(xml: str) -> dict[str, Any]:
    """Parse exact printed counter values and raw reason/limit fields."""
    flags: list[str] = []
    result: dict[str, Any] = {
        "reasons": {}, "counters_us": {}, "power_limits": {}, "fields": {}, "flags": flags}
    root = ET.fromstring(xml)
    gpu = root.find("gpu")
    if gpu is None:
        flags.append("throttle_gpu_missing")
        return result
    leaves = {node.tag: (node.text or "").strip() for node in gpu.iter() if len(node) == 0}
    result["fields"] = {k: v for k, v in leaves.items()
                        if ("clocks_event_reason" in k or "clocks_throttle_reason" in k
                            or k.endswith("power_limit"))}
    for reason in REASONS:
        values = [v for k, v in leaves.items() if k.endswith("_reason_" + reason)]
        if not values or any(v.lower() not in ("active", "not active") for v in values):
            result["reasons"][reason] = None
            flags.append("throttle_reason_unavailable:" + reason)
        else:
            active = any(v.lower() == "active" for v in values)
            result["reasons"][reason] = active
            if active and reason.startswith("hw_"):
                flags.append("throttle_hardware_active:" + reason)
    # v13's cumulative event-reason counters are integer microseconds, not event
    # counts. Parse their printed units; never compare a delta after a unit guess.
    for counter in COUNTERS:
        key = "clocks_event_reasons_counters_" + counter
        raw = leaves.get(key)
        if raw is None:
            flags.append("throttle_counter_unavailable:" + counter)
            result["counters_us"][counter] = None
            continue
        match = re.fullmatch(r"([0-9]+)(?:\s*(us|ms|ns|s))?", raw)
        if match is None:
            flags.append("throttle_counter_unavailable:" + counter)
            result["counters_us"][counter] = None
        else:
            # The v13 XML field itself specifies microseconds when unitless.
            scale = {None: Decimal(1), "us": Decimal(1), "ms": Decimal(1000),
                     "ns": Decimal("0.001"), "s": Decimal(1000000)}[match[2]]
            result["counters_us"][counter] = str(Decimal(match[1]) * scale)
    for label, names in POWER_FIELDS.items():
        raw = next((leaves[n] for n in names if n in leaves), None)
        result["power_limits"][label] = raw
        if raw is None or raw.lower() in ("n/a", "[n/a]", "not supported"):
            flags.append("throttle_power_limit_unavailable:" + label)
    return result


def snapshot(*, gpu_index: int, directory: Path, label: str,
             timeout_s: float) -> dict[str, Any]:
    """Read one measured device, preserving command, XML and parse evidence."""
    result: dict[str, Any] = {"gpu_index": gpu_index, "label": label,
                              "time_ns": time.monotonic_ns(), "flags": []}
    argv = ["nvidia-smi", "-i", str(gpu_index), "-q", "-x", "--dtd"]
    result["argv"] = argv
    try:
        raw = subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s, check=False)
        (directory / f"{label}-gpu{gpu_index}.xml").write_text(raw.stdout, encoding="utf-8")
        result["returncode"] = raw.returncode
        if raw.returncode:
            result["flags"].append("throttle_read_failed")
        else:
            result.update(parse_snapshot(raw.stdout))
            if "<!ELEMENT" not in raw.stdout:
                result["flags"].append("throttle_driver_dtd_unavailable")
    except (OSError, subprocess.TimeoutExpired, ET.ParseError) as exc:
        result["flags"].append("throttle_read_unavailable:" + type(exc).__name__)
    (directory / f"{label}-gpu{gpu_index}.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def compare(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    """Record every counter delta; any positive hardware duration is an event."""
    flags = list(before.get("flags", ())) + list(after.get("flags", ()))
    deltas = {}
    for key in COUNTERS:
        a = before.get("counters_us", {}).get(key)
        b = after.get("counters_us", {}).get(key)
        if a is None or b is None:
            deltas[key] = None
            flags.append("throttle_counter_delta_unavailable:" + key)
            continue
        try:
            delta = Decimal(b) - Decimal(a)
        except InvalidOperation:
            deltas[key] = None
            flags.append("throttle_counter_delta_unavailable:" + key)
            continue
        deltas[key] = str(delta)
        # Cumulative integer microseconds: any positive tick is evidence. Zero
        # exactly means no advancement in the driver's printed counter, not that
        # a shorter event never occurred. A reset is evidence loss, not a wrap guess.
        if delta < 0:
            flags.append("throttle_counter_reset:" + key)
        elif delta > 0 and key.startswith("hw_"):
            flags.append("throttle_hardware_counter_advanced:" + key)
    return {"gpu_index": before["gpu_index"], "counter_deltas_us": deltas,
            "flags": sorted(set(flags))}
