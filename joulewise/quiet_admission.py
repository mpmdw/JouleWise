"""Interval CPU observations for explicit packless night-plan v4 admission.

No policy defaults: the sealed plan supplies every admission parameter. Live
observation is separate from the pure parser/accounting core and never arms a
night. Observer CPU is included. Load is diagnostic, including load errors.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import time
from datetime import datetime
from typing import Mapping


POLICY_KEYS = {"policy_id", "bind_max_s", "sample_interval_s",
               "consecutive_quiet_samples", "busy_core_max", "post_bind_budget_s"}
PS_ARGV = ("/bin/ps", "-Ao", "pid,ppid,lstart,time,comm")


def validate_policy(value, *, window_max_s=None):
    if not isinstance(value, Mapping) or set(value) != POLICY_KEYS:
        raise ValueError("quiet_admission must have exactly all six policy keys")
    if value["policy_id"] != "cpu_interval_v1":
        raise ValueError("unknown quiet_admission policy_id")
    for key in POLICY_KEYS - {"policy_id"}:
        number = value[key]
        if (isinstance(number, bool) or not isinstance(number, (int, float))
                or not math.isfinite(number) or number <= 0):
            raise ValueError(f"quiet_admission.{key} must be finite and positive")
    if type(value["consecutive_quiet_samples"]) is not int:
        raise ValueError("consecutive_quiet_samples must be an integer >= 1")
    if value["bind_max_s"] < value["sample_interval_s"] * value["consecutive_quiet_samples"]:
        raise ValueError("bind_max_s cannot hold the consecutive quiet samples")
    if window_max_s is not None and window_max_s < value["bind_max_s"] + value["post_bind_budget_s"]:
        raise ValueError("window_max_s must hold bind_max_s + post_bind_budget_s")
    return dict(value)


def bind_deadline_epoch(plan):
    policy = validate_policy(plan.quiet_admission, window_max_s=plan.window_max_s)
    return min(plan.t0_epoch_s + policy["bind_max_s"],
               plan.t0_epoch_s + plan.window_max_s - policy["post_bind_budget_s"])


def _cpu_seconds(text):
    """Darwin ps TIME: [days-][hours:]minutes:seconds[.fraction]."""
    match = re.fullmatch(r"(?:(\d+)-)?(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)", text)
    if match is None:
        raise ValueError(f"malformed cumulative CPU time: {text!r}")
    days, hours, minutes, seconds = match.groups()
    return int(days or 0) * 86400 + int(hours or 0) * 3600 + int(minutes) * 60 + float(seconds)


def parse_ps(text):
    """Use lstart, not PID alone; ppid labels the observer's descendant tree.

    LC_ALL=C fixes the five-token lstart layout; split at most eight times so
    command paths containing spaces remain intact. TIME is cumulative, unlike
    the decaying average reported by %CPU.
    """
    result = {}
    lines = text.strip().splitlines()
    if not lines or not lines[0].split()[:2] == ["PID", "PPID"]:
        raise ValueError("ps header missing")
    for line in lines[1:]:
        parts = line.split(None, 8)
        if len(parts) != 9:
            raise ValueError(f"malformed ps row: {line!r}")
        pid, ppid = int(parts[0]), int(parts[1])
        start = " ".join(parts[2:7])
        epoch = datetime.strptime(start, "%a %b %d %H:%M:%S %Y").timestamp()
        identity = (pid, start)
        if identity in result or pid < 0 or ppid < 0:
            raise ValueError("duplicate or invalid process identity")
        result[identity] = dict(pid=pid, ppid=ppid, start_identity=start,
                                start_epoch_s=epoch, command=parts[8],
                                cumulative_cpu_seconds=_cpu_seconds(parts[7]))
    if not result:
        raise ValueError("ps contains no processes")
    return result


def second_top_idle_fraction(text):
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("CPU usage:")]
    if len(lines) != 2:
        raise ValueError("top must contain exactly two CPU samples")
    match = re.fullmatch(r"CPU usage:\s*([\d.]+)% user,\s*([\d.]+)% sys,\s*([\d.]+)% idle", lines[1])
    if match is None:
        raise ValueError("malformed second top CPU sample")
    percentages = [float(item) for item in match.groups()]
    if any(not math.isfinite(item) or not 0 <= item <= 100 for item in percentages):
        raise ValueError("invalid top CPU percentage")
    if abs(sum(percentages) - 100) > 0.1:
        raise ValueError("top CPU percentages do not sum to 100")
    return percentages[2] / 100


def interval_metrics(before, after, *, interval_s, idle_fraction, logical_cpu,
                     observer_pid, wall_start, last_seen=None):
    """Account for the union of identities; last_seen may include exit evidence.

    Without a measurable exit counter, list the process as unaccounted. Host
    busy time still counts that work. New processes count their lifetime CPU
    only when their start identity places them within this interval.
    """
    if (not math.isfinite(interval_s) or interval_s <= 0
            or not math.isfinite(idle_fraction) or not 0 <= idle_fraction <= 1
            or type(logical_cpu) is not int or logical_cpu <= 0):
        raise ValueError("invalid interval/host observation")
    last_seen = last_seen or {}
    all_rows = {**before, **last_seen, **after}
    observers = {observer_pid}
    while True:
        extended = observers | {row["pid"] for row in all_rows.values() if row["ppid"] in observers}
        if extended == observers:
            break
        observers = extended
    consumers, unaccounted = [], []
    for identity in sorted(set(before) | set(after) | set(last_seen)):
        first = before.get(identity)
        final = after.get(identity, last_seen.get(identity))
        row = final or first
        if final is None or (first is None and row["start_epoch_s"] < wall_start):
            unaccounted.append(dict(pid=row["pid"], start_identity=row["start_identity"],
                                    command=row["command"], reason="no measurable interval delta"))
            continue
        delta = final["cumulative_cpu_seconds"] - (first["cumulative_cpu_seconds"] if first else 0)
        if not math.isfinite(delta) or delta < 0:
            raise ValueError("CPU counter regressed for the same process identity")
        consumers.append(dict(pid=row["pid"], start_identity=row["start_identity"],
                              command=row["command"], busy_cores=delta / interval_s,
                              observer=row["pid"] in observers))
    process_busy = sum(item["busy_cores"] for item in consumers)
    host_busy = logical_cpu * (1 - idle_fraction)
    return dict(process_busy_cores=process_busy, host_busy_cores=host_busy,
                busy_cores=max(process_busy, host_busy), logical_cpu=logical_cpu,
                idle_fraction=idle_fraction, unaccounted=unaccounted,
                top_consumers=sorted(consumers, key=lambda item: (-item["busy_cores"], item["pid"]))[:10])


def is_quiet(metrics, policy):
    busy = metrics["busy_cores"]
    if isinstance(busy, bool) or not isinstance(busy, (int, float)) or not math.isfinite(busy) or busy < 0:
        raise ValueError("invalid busy_cores")
    return busy <= policy["busy_core_max"]


def validate_observation(value, policy):
    """Reject missing or non-finite worker evidence before it can be quiet."""
    required = {"wall_start", "wall_end", "monotonic_start", "monotonic_end", "interval_s",
                "boot_identity", "raw_sha256", "metrics", "load_avg_diagnostic"}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("sampler observation keys are not exact")
    for key in ("wall_start", "wall_end", "monotonic_start", "monotonic_end", "interval_s"):
        if type(value[key]) not in (int, float) or not math.isfinite(value[key]):
            raise ValueError(f"invalid sampler {key}")
    if (value["interval_s"] < policy["sample_interval_s"]
            or value["monotonic_end"] - value["monotonic_start"] < value["interval_s"]
            or value["wall_end"] < value["wall_start"]):
        raise ValueError("sampler interval incomplete or clocks regressed")
    import uuid
    if str(uuid.UUID(value["boot_identity"])) != value["boot_identity"]:
        raise ValueError("invalid sampler boot identity")
    raw = value["raw_sha256"]
    if (not isinstance(raw, dict) or set(raw) != {"ps_before", "ps_after", "top"}
            or any(not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                   for digest in raw.values())):
        raise ValueError("missing raw observation digests")
    metrics = value["metrics"]
    for key in ("process_busy_cores", "host_busy_cores", "busy_cores", "idle_fraction"):
        number = metrics[key]
        if type(number) not in (int, float) or not math.isfinite(number) or number < 0:
            raise ValueError(f"invalid sampler metric {key}")
    if (type(metrics["logical_cpu"]) is not int or metrics["logical_cpu"] < 1
            or metrics["idle_fraction"] > 1
            or not math.isclose(metrics["host_busy_cores"], metrics["logical_cpu"] * (1 - metrics["idle_fraction"]), abs_tol=1e-12)
            or metrics["busy_cores"] != max(metrics["process_busy_cores"], metrics["host_busy_cores"])):
        raise ValueError("inconsistent sampler host/aggregate CPU metrics")
    if not isinstance(metrics["top_consumers"], list) or len(metrics["top_consumers"]) > 10:
        raise ValueError("invalid top consumers")
    for item in metrics["top_consumers"]:
        if (type(item.get("pid")) is not int or not isinstance(item.get("command"), str)
                or type(item.get("observer")) is not bool
                or type(item.get("busy_cores")) not in (int, float)
                or not math.isfinite(item["busy_cores"]) or item["busy_cores"] < 0):
            raise ValueError("malformed top consumer")
    if not isinstance(metrics["unaccounted"], list) or not isinstance(value["load_avg_diagnostic"], dict):
        raise ValueError("missing accounting/load diagnostics")


def sample_interval(interval_s, *, observer_pid=None):
    """One read-only live observation. The caller supervises this whole worker.

    top's first CPU sample is invalid; only its second line is used. Every
    command has a local bound too, but the driver's absolute deadline and
    concurrent census are independent of those command bounds.
    """
    if not math.isfinite(interval_s) or interval_s <= 0:
        raise ValueError("sample interval must be finite and positive")
    observer_pid = os.getpid() if observer_pid is None else observer_pid
    def run(argv, timeout=30):
        return subprocess.run(argv, capture_output=True, text=True, check=True,
                              timeout=timeout, env={**os.environ, "LC_ALL": "C"}).stdout
    wall_start, mono_start = time.time(), time.monotonic()
    boot = run(("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")).strip()
    before_text = run(PS_ARGV)
    ps_start = time.monotonic()
    top_text = run(("/usr/bin/top", "-l", "2", "-s", str(interval_s), "-n", "0"), interval_s + 30)
    after_text = run(PS_ARGV)
    ps_end = time.monotonic()
    logical_cpu = int(run(("/usr/sbin/sysctl", "-n", "hw.logicalcpu")).strip())
    # Failure of loadavg is diagnostic; it cannot authorize or veto admission.
    try:
        load = {"raw": run(("/usr/sbin/sysctl", "-n", "vm.loadavg")).strip()}
    except (OSError, subprocess.SubprocessError) as error:
        load = {"error": str(error)}
    metrics = interval_metrics(parse_ps(before_text), parse_ps(after_text),
        interval_s=ps_end - ps_start, idle_fraction=second_top_idle_fraction(top_text),
        logical_cpu=logical_cpu, observer_pid=observer_pid, wall_start=wall_start)
    return dict(wall_start=wall_start, wall_end=time.time(),
                monotonic_start=mono_start, monotonic_end=time.monotonic(),
                interval_s=ps_end - ps_start, boot_identity=boot,
                raw_sha256={name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in
                            (("ps_before", before_text), ("ps_after", after_text), ("top", top_text))},
                metrics=metrics, load_avg_diagnostic=load)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-interval-s", type=float, required=True)
    args = parser.parse_args()
    print(json.dumps(sample_interval(args.sample_interval_s), sort_keys=True, allow_nan=False))
