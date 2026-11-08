"""Project ONLY process/timing fields from explicit committed R0 receipt blobs.

No filesystem locator in a receipt is followed. Power/energy/score/model outputs
are never projected, printed, or used for a label. Mixed reports are parsed as
JSON solely to select census fields and the CPU-only NotQuiet diagnostic.
"""
from __future__ import annotations

import ast
import json
import re

from joulewise.guard_replay import JOURNAL_FIXTURES, SCHEMA, blob, git

CPU_KEYS = {"elapsed_s", "clean", "error", "host_error", "interval", "max_outside",
            "outside_over_limit", "outside_listed", "outside_total_cpu_s_per_s",
            "kernel_task_cpu_s_per_s", "host_busy_cpu_s_per_s", "outside_aggregate_cpu_s_per_s",
            "cpu_limit_s_per_s", "aggregate_cpu_limit_s_per_s", "aggregate_over_limit"}
PROCESS_KEYS = {"pid", "command", "start", "cpu_s_per_s", "basis"}
FIXTURE_REVISION = "dcfa4c59351615cdf3879a0ef68c5800f56f53a7"


class OpaqueNumber(str):
    """Unselected numeric JSON tokens stay opaque, including every outcome value."""


def host_numbers(value):
    """Convert numeric tokens only AFTER selecting an allowlisted host field."""
    if isinstance(value, OpaqueNumber):
        return float(value) if any(ch in value for ch in ".eE") else int(value)
    if isinstance(value, list):
        return [host_numbers(v) for v in value]
    if isinstance(value, dict):
        return {k: host_numbers(v) for k, v in value.items()}
    return value


def project_cpu(value):
    result = {k: v for k, v in value.items() if k in CPU_KEYS}
    for field in ("max_outside", "outside_over_limit", "outside_listed"):
        v = result.get(field)
        if isinstance(v, dict):
            result[field] = {k: x for k, x in v.items() if k in PROCESS_KEYS}
        elif isinstance(v, list):
            result[field] = [{k: x for k, x in row.items() if k in PROCESS_KEYS} for row in v]
    return result


def project_receipt(data, source, *, benign=False):
    """One record = one trial; overlapping censuses never inflate the denominator."""
    frames = []
    for i, census in enumerate(data.get("census", [])):
        frame = {"t": host_numbers(census["monotonic_s"]), "receipt_index": i}
        diagnostic = census.get("pcpu_diagnostic", census.get("busy"))
        if diagnostic is not None:
            # pcpu diagnostic is already a list of the over-limit matching rows.
            frame["pcpu_busy"] = host_numbers(diagnostic)
        if "cpu_interval" in census and "busy" in census:
            frame["quiet_busy"] = [
                {k: host_numbers(v) for k, v in row.items() if k in PROCESS_KEYS} for row in census["busy"]]
            frame["quiet_interval"] = {k: host_numbers(v) for k, v in census["cpu_interval"].items()
                                       if k in ("start_monotonic_s", "end_monotonic_s", "elapsed_s")}
        frames.append(frame)
    seen = set()
    for i, check in enumerate(data.get("checks", [])):
        for field in ("stderr", "stdout"):
            # This guard emits a Python CPU-metrics dictionary after this exact prefix.
            # Do not copy arbitrary stdout/stderr (SMC/model outputs live there too).
            phrase = "outside-tree CPU contention or unmeasured host CPU:"
            text = check.get(field, "")
            start = text.find(phrase)
            if start < 0:
                continue
            literal = text[start + len(phrase):].splitlines()[0]
            try:
                cpu = project_cpu(ast.literal_eval(literal))
            except (ValueError, SyntaxError):
                continue
            fingerprint = json.dumps(cpu, sort_keys=True)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            t = cpu["interval"]["monotonic_ns"][1] / 1e9
            frames.append({"t": t, "smc_cpu": cpu, "check_index": i,
                           "cpu_era": "pre691" if cpu.get("aggregate_cpu_limit_s_per_s") == .05 else "prel3"})
    frames.sort(key=lambda f: f["t"])
    # Selected stopped attempts do not cover a run-length observation. Keep all gaps.
    return {"id": source["path"].split("/")[-2], "label": "benign" if benign else "unknown",
            "label_basis": ("Ed guard-replay brief: routine macOS burst/display/location incident; "
                            "engineering-benign, not a claim of absence of physical load" if benign else
                            "No independent idle/contended label; excluded from accuracy rates"),
            "stratum": "recorded_incident", "complete": False,
            "duration_s": frames[-1]["t"] - frames[0]["t"] if frames else 0,
            "source": source, "frames": frames}


def collect():
    refs = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/records").decode().splitlines()
    sources, runs = [], []
    for ref in sorted(refs):
        match = re.fullmatch(r"origin/records/(2026-11-0[678])-align-r0-v4(-rerun\d*)?", ref)
        if not match:
            continue
        date, suffix = match.groups()
        folder = date + (suffix or "")
        path = f"docs/align/r0/{folder}/report.json"
        # An absent committed report is a documented corpus gap, never a disk fallback.
        paths = git("ls-tree", "--name-only", ref, path).decode().splitlines()
        if path not in paths:
            sources.append({"ref": ref, "path": path, "available": False})
            continue
        raw, source = blob(ref, path)
        source.update(ref=ref, available=True)
        sources.append(source)
        runs.append(project_receipt(json.loads(raw, parse_float=OpaqueNumber, parse_int=OpaqueNumber), source, benign=folder in {
            "2026-11-07-rerun3", "2026-11-07-rerun4", "2026-11-07-rerun8",
            "2026-11-07-rerun9", "2026-11-07-rerun10"}))
    frames, fixture_sources = [], []
    for path in JOURNAL_FIXTURES:
        raw, source = blob(FIXTURE_REVISION, path)
        source.update(available=True, origin="FakeMac synthetic fixture; README.md lines 61-68")
        fixture_sources.append(source)
        sources.append(source)
        for line in raw.splitlines():
            row = json.loads(line, parse_float=OpaqueNumber, parse_int=OpaqueNumber)
            values = row.get("values") or {}
            if path.endswith("contention.jsonl") and row["kind"] == "interval":
                # Select first, convert only host fields, and never retain raw-path locators.
                cpu = host_numbers(project_cpu(values))
                frames.append({"t": cpu["interval"]["monotonic_ns"][1] / 1e9,
                               "contention_interval": cpu})
            elif path.endswith("thermal.jsonl") and row["kind"] == "reading":
                frames.append({"t": host_numbers(row["started"]["monotonic_ns"]) / 1e9,
                               "thermal": {"level": host_numbers(values.get("level")), "error": row.get("error")}})
    frames.sort(key=lambda f: f["t"])
    runs.append({"id": "fakemac-monitor-journals", "label": "contended", "stratum": "synthetic_fixture",
                 "label_basis": "Committed README: FakeMac injects fseventsd burst and OS thermal level 1",
                 "complete": True, "duration_s": frames[-1]["t"] - frames[0]["t"],
                 "sources": fixture_sources, "frames": frames})
    return {"schema": SCHEMA, "provenance": "committed Git host-state projections only",
            "sources": sources, "runs": runs}
