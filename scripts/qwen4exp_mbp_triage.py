#!/usr/bin/env python3
"""Classify a Saturday MBP probe without importing MLX or changing evidence.

The five evidence files are addressed from ``--out``; the only writes are the
new ``<out>.triage.json`` receipt and ``<out>.triage/`` attachment directory.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


CLASSES = ("PREFLIGHT_SWAP", "ABORT_SWAP", "ABORT_PRESSURE", "ABORT_FLOOR_ONLY",
           "ABORT_COMPRESSOR", "METAL_CAP", "PLE_CAP", "PREDICTION_FAIL",
           "JETSAM_KILL", "METAL_ERROR", "PY_EXCEPTION", "REFUSED",
           "SIGNAL_CRASH", "INCOMPLETE", "COMPLETED", "NO_EVIDENCE")

MAXFIT5 = "Use maxfit5; reboot first because swap is in use."
ACTIONS = {
    "PREFLIGHT_SWAP": MAXFIT5, "ABORT_SWAP": MAXFIT5,
    "ABORT_PRESSURE": "Use maxfit5; reboot first if swap is in use.",
    "ABORT_FLOOR_ONLY": "Use maxfit5; reboot first if swap is in use.",
    "ABORT_COMPRESSOR": "Use maxfit5; reboot first if swap is in use.",
    "METAL_CAP": "Use maxfit5; reboot first if swap is in use.",
    "JETSAM_KILL": "Use maxfit5; reboot first if swap is in use.",
    "PLE_CAP": "Stop and use the pread variant another day.",
    "PREDICTION_FAIL": "Continue, collect a memory breakdown, and send it to the lead for review.",
    "METAL_ERROR": "Rerun once under a new output name; if it repeats, run tests.align.test_qwen4_exp_canonical natively plus the smallest step, then send it to the lead.",
    "SIGNAL_CRASH": "Rerun once under a new output name; if it repeats, run tests.align.test_qwen4_exp_canonical natively plus the smallest step, then send it to the lead.",
    "PY_EXCEPTION": "Fix on the laptop branch, pull, and rerun.",
    "REFUSED": "Fix on the laptop branch, pull, and rerun.",
    "INCOMPLETE": "Preserve the evidence and have the lead choose the next step.",
    "COMPLETED": "Continue with the next runbook step.",
    "NO_EVIDENCE": ("No evidence file exists for this --out: check the path. A preflight refusal "
                    "writes nothing and prints its reason on the probe's terminal; rerun under a "
                    "new output name once that reason is cleared (reboot first if swap is in use)."),
}
# Worker verdicts of a finished run: memory/performance/paging/hosted write
# "completed"; quality/benchmark carry the e2e verdict ("pass" or, when every
# stage was skipped, "skipped"). "fail"/"incomplete" are not completions.
COMPLETED_WORKER_VERDICTS = ("completed", "pass", "skipped")


def _json(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def _jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _window(report, monitor, clock):
    values = [x.get("time") for x in monitor if isinstance(x.get("time"), (int, float))]
    for key in ("started_at", "start_time", "ended_at", "end_time"):
        value = report.get(key)
        if isinstance(value, (int, float)):
            values.append(value)
    now = clock()
    return (min(values) if values else now - 300, max(values) if values else now)


# The worker dies between the last two monitor samples; jetsam is logged then.
KERNEL_LOOKBACK_SECONDS = 600
# ReportCrash writes the .ips after the supervisor's final sample.
IPS_GRACE_SECONDS = 600
# `log show` accepts "YYYY-MM-DD HH:MM:SSZZZZZ", not ISO 8601 with "T" (exit 64).
LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"
# Kill lines name the victim's p_comm, e.g. "memorystatus: killing_top_process
# pid 123 [Python] ...". Other memorystatus lines (dirty tracking, idle kills
# of daemons) are routine and must not turn a SIGKILL into JETSAM_KILL.
JETSAM_KILL_RE = re.compile(r"memorystatus:.*\bkill\w*\b.*\bpid \d+ \[python[^\]]*\]", re.I)


def _log_show(start, end, runner):
    start = max(start, end - KERNEL_LOOKBACK_SECONDS)
    fmt = lambda value: dt.datetime.fromtimestamp(value).astimezone().strftime(LOG_TIME_FORMAT)
    argv = ["log", "show", "--style", "ndjson", "--start", fmt(start), "--end", fmt(end + 5),
            "--predicate", 'process == "kernel" AND eventMessage CONTAINS[c] "memorystatus"']
    try:
        result = runner(argv, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    return result.stdout if result.returncode == 0 else None


def _jetsam_kills(kernel):
    kills = []
    for line in kernel.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and JETSAM_KILL_RE.search(str(event.get("eventMessage", ""))):
            kills.append(event)
    return kills


def _swap_used_bytes(runner=subprocess.run):
    out = runner(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=10).stdout
    used = re.search(r"used\s*=\s*([\d.]+)([MG])", out)
    if not used:
        raise ValueError("cannot parse vm.swapusage")
    return float(used[1]) * (2**20 if used[2] == "M" else 2**30)


def _exception(log_text):
    marker = "Traceback (most recent call last):"
    if marker not in log_text:
        return None
    body = log_text.rsplit(marker, 1)[1]
    frames = re.findall(r'File "([^"]+)", line (\d+), in ([^\n]+)', body)
    types = re.findall(r"^([A-Za-z_][\w.]*(?:Error|Exception|Interrupt))(?::\s*(.*))?$", body, re.M)
    return {"type": types[-1][0] if types else "Exception",
            "message": types[-1][1] if types else "",
            "last_frame": ({"file": frames[-1][0], "line": int(frames[-1][1]),
                            "function": frames[-1][2].strip()} if frames else None)}


def classify(report, worker, log_text, monitor, rungs, *, log_runner=subprocess.run,
             ips_reader=None, clock=time.time, swap_reader=_swap_used_bytes):
    """Return the classification receipt; dependencies are injectable for tests."""
    def diagnostic_reports():
        directory = Path.home() / "Library/Logs/DiagnosticReports"
        return [p for p in directory.glob("*.ips")
                if p.name.lower().startswith("python") and not p.is_symlink()
                and p.resolve().parent == directory.resolve()]
    ips_reader = ips_reader or diagnostic_reports
    reason = str(report.get("abort") or "")
    combined = "\n".join((log_text, reason, json.dumps(worker or {})))
    low = combined.lower()
    rc = report.get("worker_returncode")
    initial_swap = float(report.get("initial_swap_used_bytes") or 0)
    details = {}

    # Specific signatures beat generic Python exceptions and return codes.
    if not report and not log_text and not monitor and not worker and not rungs:
        # Nothing to classify: a mistyped --out, or supervise() raised
        # "preflight: ..." before creating ANY evidence file (main() prints it
        # to the operator's terminal only). Live swap is context, not evidence.
        kind = "NO_EVIDENCE"
        details = {"no_evidence": True, "swap_used_bytes_at_triage": swap_reader()}
    elif "command buffer execution failed" in low or "kiogpucommandbuffercallbackerror" in low:
        kind = "METAL_ERROR"
    elif ((reason.lower().startswith("preflight") and "swap" in reason.lower())
          or initial_swap > 0 or "refused: preflight: swap" in low):
        kind = "PREFLIGHT_SWAP"
    elif reason and ("swap present" in reason.lower() or "swapout" in reason.lower()):
        kind = "ABORT_SWAP"
    elif reason and "pressure level" in reason.lower():
        kind = "ABORT_PRESSURE"
    elif reason and "free percentage" in reason.lower():
        levels = set(report.get("pressure_levels") or [x.get("pressure_level") for x in monitor])
        growth = float(report.get("max_compressor_growth_bytes") or 0)
        swap = initial_swap or float(report.get("swapouts_delta") or 0)
        kind = "ABORT_FLOOR_ONLY" if not swap and levels == {1} and growth <= 2e9 else "ABORT_PRESSURE"
    elif reason and "compressor" in reason.lower():
        kind = "ABORT_COMPRESSOR"
    elif "metal peak exceeds" in low or "working-set cap" in low:
        kind = "METAL_CAP"
    elif "ple resident file pages exceed" in low or "21.5 gb cap" in low:
        kind = "PLE_CAP"
    elif any(float(x.get("prediction", {}).get("relative_error", 0)) > .10 for x in rungs):
        kind = "PREDICTION_FAIL"
    elif rc == -9 and not reason:
        start, end = _window(report, monitor, clock)
        kernel = _log_show(start, end, log_runner)
        kills = _jetsam_kills(kernel or "")
        if kills:
            kind, details = "JETSAM_KILL", {"kernel_memorystatus": kills}
        else:
            kind = "SIGNAL_CRASH"
            details = {"kernel_log": "unavailable" if kernel is None else "no python jetsam kill"}
    elif (exc := _exception(log_text)) is not None:
        kind, details = "PY_EXCEPTION", {"exception": exc}
    elif "refused:" in low:
        kind = "REFUSED"
    elif isinstance(rc, int) and rc < 0:
        kind = "SIGNAL_CRASH"
    elif (report.get("verdict") == "completed" and rc == 0
          and (worker_verdict := (worker or report.get("results") or {}).get("verdict"))
          in COMPLETED_WORKER_VERDICTS):
        kind, details = "COMPLETED", {"worker_verdict": worker_verdict}
        if worker_verdict == "skipped":
            details["note"] = "every e2e stage was skipped: the run finished but carries no quality evidence"
    else:
        kind = "INCOMPLETE"

    receipt = {"schema": "qwen4exp-mbp-triage/v1", "classification": kind,
               "next_action": ACTIONS[kind], "worker_returncode": rc, **details}
    if kind == "SIGNAL_CRASH":
        start, end = _window(report, monitor, clock)
        candidates = []
        for path in ips_reader():
            stamp = path.stat().st_mtime
            if start <= stamp <= end + IPS_GRACE_SECONDS:
                candidates.append((stamp, path))
        receipt["ips_source"] = str(max(candidates)[1]) if candidates else None
    return receipt


def _validate_out(path):
    path = path.expanduser().absolute()
    root = Path("/Volumes/JW-EXT")
    if (path.is_symlink() or root not in (path, *path.parents)
            or root.resolve() not in (path.resolve(), *path.resolve().parents)):
        raise ValueError("--out must be a non-symlink path on /Volumes/JW-EXT")
    if any(part == "restricted" or part.startswith("night-") for part in path.parts):
        raise ValueError("restricted and night-* paths are never read")
    return path


def _evidence(path):
    if path.is_symlink() or any(part == "restricted" or part.startswith("night-") for part in path.parts):
        raise ValueError("evidence symlinks and restricted/night-* paths are never read")
    return path


def run(out, **injected):
    out = _validate_out(Path(out))
    report = _json(_evidence(out), {})
    worker = _json(_evidence(Path(str(out) + ".worker.json")), {})
    log_path = _evidence(Path(str(out) + ".worker.log"))
    monitor_path = _evidence(Path(str(out) + ".monitor.jsonl"))
    rungs_path = _evidence(Path(str(out) + ".rungs.jsonl"))
    receipt = classify(report, worker, log_path.read_text(errors="replace") if log_path.exists() else "",
                       _jsonl(monitor_path), _jsonl(rungs_path), **injected)
    destination = Path(str(out) + ".triage")
    receipt_path = Path(str(out) + ".triage.json")
    destination.mkdir(exist_ok=False)
    if source := receipt.get("ips_source"):
        copied = destination / Path(source).name
        shutil.copy2(source, copied)  # copy, never move, the crash report
        receipt["ips_copy"] = str(copied)
    with receipt_path.open("x") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(run(args.out), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
