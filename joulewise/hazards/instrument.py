"""Instrument hazard: powermetrics does not sample at its cadence in this context.

Measured directly: a real 300-frame powermetrics idle capture through the
production adapter, run inside the launchd job (the context that showed the
09-19 slow-cadence defect: 244-250 ms medians under a default-ProcessType
launchd job, against about 118 ms in a shell and 130 ms under block 3's
Interactive job).

Arm (plan §2.3): exit 0; exactly 300 frames within the 55 s bound; median
interval <= 150 ms; maximum <= 200 ms; and the capture's process group proven
gone afterwards.  Anything else refuses; a probe that could not run is
UNMEASURED and refuses.  Not used in the window: powermetrics runs inside
each member, whose per-member checks (``insufficient_in_window_samples``,
``cadence_ratio_below_threshold``) are unchanged.

The logic is copied from ``run_night._probe_cadence``
(``scripts/run_night.py:4684-4754``): the adapter's own command, count and
bound (``_command``, ``_idle_count``, ``_capture_timeout_s``), every frame kept
(the first included, as production counts it), the adapter's
``parse_powermetrics_records``.

The capture runs in a child Python process (``_child_main``).  The adapter
module imports the measurement core (``bundle.py``), which imports
``arm_readiness``; keeping that import in a child leaves the arm process's
own import graph free of the retired path (tests/hazards/test_import_graph.py).
"""

from __future__ import annotations

import json
import math
import os
import signal
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from joulewise.hazards.base import (
    PASS, REFUSE, UNMEASURED, Context, Measurement, RawRef, Verdict, require_thresholds,
    sha256_hex, row,
)

MODULE = "instrument"
POWERMETRICS = "/usr/bin/powermetrics"
PRIVILEGE_PREFIX = ("sudo", "-n")
CHILD_SCHEMA = "joulewise.hazard_instrument_capture.v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
CHILD_BOOTSTRAP = ("import sys; sys.path.insert(0, sys.argv[1]); "
                   "from joulewise.hazards.instrument import _child_main; "
                   "raise SystemExit(_child_main(sys.argv[2:]))")
CHILD_MARGIN_S = 30.0  # the child enforces the capture bound; this bounds the child itself

DEFAULT_THRESHOLDS: dict[str, Any] = {
    "frames": 300,          # production idle count: 30 s at 10 Hz
    "bound_s": 55.0,        # the adapter's bound: 300 x 0.1 x 1.5 + 10
    "median_ms_max": 150.0,
    "max_ms_max": 200.0,
}
THRESHOLD_KEYS = tuple(DEFAULT_THRESHOLDS)


# --------------------------------------------------------------------------
# Parent side


def child_argv(output: Path, *, executable: str, privilege_prefix: Sequence[str],
               python: str = sys.executable) -> list[str]:
    return [python, "-B", "-c", CHILD_BOOTSTRAP, str(REPO_ROOT), "--output", str(output),
            "--executable", executable, "--privilege-prefix", json.dumps(list(privilege_prefix))]


def measure(ctx: Context, *, executable: str = POWERMETRICS,
            privilege_prefix: Sequence[str] = PRIVILEGE_PREFIX,
            python: str = sys.executable) -> Measurement:
    started = ctx.stamp()
    temporary = None
    if ctx.raw_dir is not None:
        directory = Path(ctx.raw_dir)
        directory.mkdir(parents=True, exist_ok=True)
    else:
        temporary = tempfile.TemporaryDirectory(prefix="hazard-instrument-")
        directory = Path(temporary.name)
    prefix = f"{ctx.label}-" if ctx.label else ""
    output = directory / f"{prefix}powermetrics-idle.plist"
    values: dict[str, Any] = {"output": str(output)}
    raw: list[RawRef] = []
    error = None
    try:
        if output.exists():
            raise FileExistsError(f"capture output already exists: {output}")
        argv = child_argv(output, executable=executable, privilege_prefix=privilege_prefix,
                          python=python)
        completed = ctx.run(argv, DEFAULT_THRESHOLDS["bound_s"] + CHILD_MARGIN_S)
        values["child"] = {"returncode": completed.returncode, "timed_out": completed.timed_out,
                           "error": completed.error,
                           "stderr": completed.stderr.decode("utf-8", errors="replace")[-4000:]}
        if completed.error or completed.timed_out:
            error = f"cadence probe child failed: {completed.error or 'timed out'}"
        else:
            report = _last_json_line(completed.stdout)
            if report is None or report.get("schema") != CHILD_SCHEMA:
                error = f"cadence probe child returned no report (exit {completed.returncode})"
            else:
                values.update(report)
                values.update(cadence_statistics(report.get("intervals_ns") or []))
        if output.exists():
            data = output.read_bytes()
            raw.append(RawRef("powermetrics-idle.plist", sha256_hex(data), len(data),
                              _relative(output, ctx.custody_root)))
    except OSError as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if temporary is not None:
            temporary.cleanup()
    finished = ctx.stamp()
    return Measurement(MODULE, "instant", values, tuple(raw), started, finished, error)


def cadence_statistics(intervals_ns: Sequence[int]) -> dict[str, Any]:
    """Median, p95 and maximum frame interval in ms, as ``_probe_cadence`` reports them."""

    values = sorted(value / 1_000_000 for value in intervals_ns)
    if not values:
        return {"median_ms": None, "p95_ms": None, "max_ms": None}
    return {"median_ms": statistics.median(values),
            "p95_ms": values[min(len(values) - 1, math.ceil(0.95 * len(values)) - 1)],
            "max_ms": values[-1]}


def judge(measurement: Measurement, thresholds: Mapping[str, Any]) -> Verdict:
    limits = require_thresholds(MODULE, thresholds, THRESHOLD_KEYS)
    if measurement.module != MODULE:
        raise ValueError("instrument.judge received another module's measurement")
    if measurement.error:
        return Verdict(MODULE, UNMEASURED, (measurement.error,), limits)
    v = measurement.values
    reasons = []
    if v.get("spawn_error"):
        return Verdict(MODULE, UNMEASURED, (f"powermetrics could not start: {v['spawn_error']}",),
                       limits)
    if v.get("timed_out"):
        reasons.append(f"capture did not finish within {v.get('bound_s')} s")
    elif v.get("returncode") != 0:
        reasons.append(f"powermetrics exited {v.get('returncode')}: "
                       f"{(v.get('stderr') or '').strip()[:300]}")
    if v.get("parse_error"):
        reasons.append(f"capture unparsable: {v['parse_error']}")
    if v.get("count_expected") != limits["frames"]:
        reasons.append(f"production idle count {v.get('count_expected')} differs from the "
                       f"registered {limits['frames']}")
    if v.get("frames") != limits["frames"]:
        reasons.append(f"{v.get('frames')} frames captured, {limits['frames']} required")
    elapsed = v.get("elapsed_s")
    if elapsed is None or elapsed > limits["bound_s"]:
        reasons.append(f"elapsed {elapsed} s exceeds the {limits['bound_s']} s bound")
    if v.get("median_ms") is None or v["median_ms"] > limits["median_ms_max"]:
        reasons.append(f"median interval {v.get('median_ms')} ms > {limits['median_ms_max']} ms")
    if v.get("max_ms") is None or v["max_ms"] > limits["max_ms_max"]:
        reasons.append(f"maximum interval {v.get('max_ms')} ms > {limits['max_ms_max']} ms")
    if v.get("group_gone") is not True:
        reasons.append("the capture's process group was not proven gone: "
                       + "; ".join(v.get("group_census") or ["no census"]))
    observed = {key: v.get(key) for key in ("frames", "elapsed_s", "median_ms", "p95_ms",
                                            "max_ms", "returncode", "group_gone")}
    return Verdict(MODULE, REFUSE if reasons else PASS, tuple(reasons), limits, observed)


def _last_json_line(stdout: bytes) -> dict[str, Any] | None:
    for line in reversed(stdout.decode("utf-8", errors="replace").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except ValueError:
                return None
            return value if isinstance(value, dict) else None
    return None


def _relative(path: Path, root: Path | None) -> str:
    if root is None:
        return str(path)
    try:
        return str(path.resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------
# Child side (runs in its own Python process; imports the production adapter)


def _child_main(argv: Sequence[str]) -> int:
    import argparse
    from types import SimpleNamespace

    from joulewise.adapters.powermetrics import (
        PowermetricsTelemetryAdapter, parse_powermetrics_records,
    )

    parser = argparse.ArgumentParser(prog="hazard-instrument-capture")
    parser.add_argument("--output", required=True)
    parser.add_argument("--executable", required=True)
    parser.add_argument("--privilege-prefix", required=True)
    args = parser.parse_args(list(argv))
    prefix = tuple(json.loads(args.privilege_prefix))
    output = Path(args.output)
    config = SimpleNamespace(sampling=SimpleNamespace(power_hz=10.0, idle_seconds=30.0))
    adapter = PowermetricsTelemetryAdapter(None, executable=args.executable,
                                           privilege_prefix=prefix)
    count = adapter._idle_count(config)
    bound = adapter._capture_timeout_s(config, count)
    command = adapter._command(config, output, count=count)
    report: dict[str, Any] = {"schema": CHILD_SCHEMA, "argv": command, "count_expected": count,
                              "bound_s": bound, "returncode": None, "timed_out": False,
                              "spawn_error": None, "stderr": "", "elapsed_s": None,
                              "frames": 0, "intervals_ns": [], "thermal_pressure": [],
                              "parse_error": None, "pgid": None, "group_gone": None,
                              "group_census": []}
    started = time.monotonic()
    process = None
    try:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        report["pgid"] = process.pid
        _stdout, stderr = process.communicate(timeout=bound)
        report["returncode"] = process.returncode
        report["stderr"] = stderr.decode("utf-8", errors="replace")[-4000:]
    except subprocess.TimeoutExpired:
        report["timed_out"] = True
        _term_then_kill(process.pid)
        try:
            process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        report["returncode"] = process.returncode
    except OSError as exc:
        report["spawn_error"] = f"{type(exc).__name__}: {exc}"
    report["elapsed_s"] = time.monotonic() - started
    if process is not None:
        gone, lines = group_absent(process.pid)
        report["group_gone"], report["group_census"] = gone, lines
    else:
        report["group_gone"] = True
    try:
        if output.exists():
            records = parse_powermetrics_records(output.read_bytes())
            report["frames"] = len(records)
            report["intervals_ns"] = [record.elapsed_ns for record in records]
            report["thermal_pressure"] = sorted({str(record.thermal_pressure)
                                                 for record in records})
    except (OSError, ValueError) as exc:
        report["parse_error"] = f"{type(exc).__name__}: {exc}"
    sys.stdout.write(json.dumps(report, sort_keys=True) + "\n")
    sys.stdout.flush()
    return 0


def _term_then_kill(pgid: int) -> None:
    """Give sudo a chance to relay TERM before a bounded KILL (run_night's form)."""

    try:
        os.killpg(pgid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        if group_absent(pgid)[0]:
            return
        time.sleep(0.05)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def group_absent(pgid: int, timeout_s: float = 2.0) -> tuple[bool, list[str]]:
    """Absent only when ``pgrep -g`` exits 1 with no output (run_night ``_group_census``)."""

    deadline = time.monotonic() + timeout_s
    while True:
        try:
            result = subprocess.run(["/usr/bin/pgrep", "-lf", "-g", str(pgid), "."],
                                    capture_output=True, text=True, timeout=timeout_s, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            return False, [f"census_failed: {type(exc).__name__}: {exc}"]
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if result.returncode == 1 and not lines:
            return True, []
        if time.monotonic() >= deadline:
            if result.returncode not in (0, 1):
                lines = [f"census_exit_{result.returncode}: {result.stderr.strip()}", *lines]
            return False, lines
        time.sleep(0.05)


# Inventory rows (configs/gates/physics_rows.json) whose physical check this
# module performs.  tests/hazards/test_physics_coverage.py keeps the two in step.
PROTECTS: tuple[tuple[str, str, str, int], ...] = (
    # base line 1933: Instrument: `sudo -n powermetrics -i 200 -n 1` did not exit 0 (the instrument can...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_powermetrics",
        "evidence_author_t0_powermetrics_probe_underivable", 1),
)

# Proxy rows on paths block 5 no longer runs that this module's direct
# measurement replaces (configs/gates/physics_rows.json, "retired_proxy").
SUPERSEDES: tuple[tuple[str, str, str, int], ...] = (
    # base line 1132: The exact reviewed 'sudo -n powermetrics' command exits 0.
    row("joulewise/arm_readiness.py", "<module>",
        "predicate t0.passwordless_powermetrics.v1", 1),
    # base line 7168: The POWERMETRICS_PROBE receipt records the exact sudo -n powermetrics command and...
    row("joulewise/arm_readiness.py", "_evaluate_rows",
        "readiness_dependency_refused (row t0.passwordless_powermetrics)", 1),
    # base line 411: the powermetrics binary exists and is executable, and sudoers allows it non-inter...
    row("joulewise/doctor.py", "build_doctor_report",
        "powermetrics check fail (required by config and not present/executable/sudo -n -l ok)", 1),
    # base line 897: powermetrics inter-sample cadence measured by the launchd probe job, up to 6 h ea...
    row("joulewise/night_agent_install.py", "validate_probe_receipt",
        "probe cadence median_ms>150 or max_ms>200 (Refused 2)", 1),
)
