"""Offline reduction of OSCTX diagnostic cells using production telemetry math."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import statistics
import sys

try:
    from .common import load_config, write_json
except ImportError:  # direct CLI execution
    from common import load_config, write_json

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from joulewise.adapters.powermetrics import (  # noqa: E402
    anchor_records_from_powermetrics, decode_rich_telemetry,
    parse_powermetrics_records, samples_from_raw_powermetrics,
)
from joulewise.bundle_read import TracePoint  # noqa: E402
from joulewise.clock import ClockStamp  # noqa: E402
from joulewise.reduce import _integrate  # noqa: E402
from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD, resolve_clock_evidence_deriver  # noqa: E402


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)]


def windows(boundaries: list[dict]) -> dict[tuple[str, int], tuple[float, float]]:
    grouped = defaultdict(dict)
    for item in boundaries:
        grouped[item["name"], item["repeat"]][item["edge"]] = item["wall_ns"] / 1e9
    result = {}
    for key, edges in grouped.items():
        if set(edges) != {"start", "end"} or edges["end"] <= edges["start"]:
            raise ValueError(f"invalid boundary pair: {key}")
        result[key] = edges["start"], edges["end"]
    return result


def cadence(records, start: float, end: float) -> dict:
    # Record i reports the gap since record i-1. Record 0 has no observed
    # predecessor in this stream, so exclude it as production pilot did.
    gaps = [r.elapsed_ns / 1e6 for r in records[1:] if start <= r.timestamp_s <= end]
    return {"n": len(gaps), "median_ms": statistics.median(gaps) if gaps else None,
            "p95_ms": percentile(gaps, .95)}


def cluster_metrics(rich: list[dict], start: float, end: float) -> dict:
    totals = defaultdict(lambda: {"active": 0.0, "duration": 0.0, "freq_active": 0.0, "freq_weight": 0.0})
    for record in rich:
        right = record["timestamp_s"]
        left = right - record["elapsed_ns"] / 1e9
        overlap = max(0.0, min(end, right) - max(start, left))
        if overlap == 0:
            continue
        for cluster in record["clusters"]:
            name = cluster.get("name") or ""
            kind = "E" if name.startswith("E") else "P" if name.startswith("P") else None
            if kind is None:
                continue
            # The cluster idle_ratio can describe cluster on-line state. Per
            # core idle ratios are the active-residency evidence.
            cpus = cluster.get("cpus") or []
            active = statistics.mean(max(0.0, 1.0 - float(cpu["idle_ratio"]) - float(cpu.get("down_ratio") or 0))
                                     for cpu in cpus if cpu.get("idle_ratio") is not None) if cpus else None
            if active is None:
                continue
            totals[kind]["active"] += active * overlap * len(cpus)
            totals[kind]["duration"] += overlap * len(cpus)
            freq = cluster.get("freq_hz")
            if isinstance(freq, (int, float)) and freq > 0:
                totals[kind]["freq_active"] += freq * active * overlap * len(cpus)
                totals[kind]["freq_weight"] += active * overlap * len(cpus)
    return {kind: {"active_residency": value["active"] / value["duration"] if value["duration"] else None,
                   "active_frequency_hz": value["freq_active"] / value["freq_weight"] if value["freq_weight"] else None}
            for kind, value in totals.items()}


def reduce_trace(raw: bytes, boundary_records: list[dict], endpoint: float) -> dict:
    """Use production parser, interval-support samples and reducer integrator."""
    records = parse_powermetrics_records(raw, first_record_endpoint_s=endpoint)
    samples = samples_from_raw_powermetrics(raw, first_record_endpoint_s=endpoint)
    rich = decode_rich_telemetry(raw, first_record_endpoint_s=endpoint)
    by_window = windows(boundary_records)
    curve_by_rail = defaultdict(list)
    for sample in samples:
        curve_by_rail[sample.rail].append(TracePoint(sample.timestamp_s, sample.power_w,
                                                   sample.interval_start_s, sample.interval_end_s))
    result = {}
    for (name, repeat), (start, end) in by_window.items():
        rails = {rail: _integrate(curve, start, end) for rail, curve in curve_by_rail.items()}
        result[f"{name}.{repeat}"] = {"duration_s": end - start, "energy_j": math.fsum(rails.values()),
                                      "rail_energy_j": rails}
        if name in {"idle", "lm"}:
            result[f"{name}.{repeat}"]["cadence"] = cadence(records, start, end)
        if name in {"cpu", "lm"}:
            result[f"{name}.{repeat}"]["clusters"] = cluster_metrics(rich, start, end)
    return result


def derive_endpoint(raw: bytes, cell: dict) -> tuple[float, dict]:
    stamps = {key: ClockStamp(**value) for key, value in cell["clock_stamps"].items()}
    native = parse_powermetrics_records(raw)
    evidence, endpoint = resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)(
        stamps=stamps, records=anchor_records_from_powermetrics(native))
    if endpoint is None:
        raise ValueError(f"production clock anchor unresolved: {evidence['clock_anchor']}")
    return endpoint, evidence


def analyze_cell(directory: Path) -> dict:
    cell = json.loads((directory / "cell.json").read_text())
    if not json.loads((directory / "done.json").read_text())["ok"]:
        raise ValueError("cell failed")
    raw = (directory / "powermetrics.plist").read_bytes()
    endpoint, evidence = derive_endpoint(raw, cell)
    segments = reduce_trace(raw, cell["boundaries"], endpoint)
    metrics = {}
    for name in ("cpu", "gpu", "lm"):
        repeats = cell["repeats"].get(name, [])
        metrics[f"{name}_seconds"] = statistics.median(x["seconds"] for x in repeats)
        metrics[f"{name}_energy_j"] = statistics.median(segments[f"{name}.{x['repeat']}"]["energy_j"] for x in repeats)
    lm_tokens = sum(x["output_tokens"] for x in cell["repeats"]["lm"])
    lm_energy = sum(segments[f"lm.{x['repeat']}"]["energy_j"] for x in cell["repeats"]["lm"])
    metrics["lm_j_per_token"] = lm_energy / lm_tokens
    metrics["lm_output_tokens"] = lm_tokens
    metrics["lm_prefill_tps"] = statistics.median(x["prefill_tps"] for x in cell["repeats"]["lm"])
    metrics["lm_decode_tps"] = statistics.median(x["decode_tps"] for x in cell["repeats"]["lm"])
    for name in ("idle", "lm"):
        values = [v["cadence"] for key, v in segments.items() if key.startswith(name + ".")]
        metrics[f"{name}_cadence_median_ms"] = statistics.median(v["median_ms"] for v in values if v["median_ms"] is not None)
        metrics[f"{name}_cadence_p95_ms"] = statistics.median(v["p95_ms"] for v in values if v["p95_ms"] is not None)
    return {"state": cell["state"], "context": cell["context"], "cell_id": cell["cell_id"],
            "pid": cell["pid"], "powermetrics_pid": cell.get("powermetrics_pid"),
            "dir": str(directory), "metrics": metrics, "segments": segments, "clock_anchor": evidence["clock_anchor"],
            "start_wall_ns": min(x["wall_ns"] for x in cell["boundaries"]),
            "end_wall_ns": max(x["wall_ns"] for x in cell["boundaries"])}


def ratio(left: float | None, right: float | None) -> float | None:
    return left / right if left is not None and right is not None and right > 0 else None


def direction(value: float | None) -> str:
    return "+" if value is not None and value > 1 else "-" if value is not None and value < 1 else "=" if value == 1 else "?"


def decision_table(rows: list[dict], config: dict) -> dict:
    thresholds = config["thresholds"]
    grouped = defaultdict(dict)
    for row in rows:
        grouped[row["state"], row["context"]][row["cell_id"]] = row["metrics"]
    states = {}
    metric_names = ["cpu_seconds", "gpu_seconds", "lm_seconds", "lm_j_per_token"]
    for state in config["states"]:
        state_result = {"ratios": {}, "pairs": {}}
        for comparison, left, right in (("D/I", "D", "I"), ("B/I", "B", "I")):
            lrows, rrows = grouped[state, left], grouped[state, right]
            for metric in metric_names:
                if len(lrows) != len(rrows) or len(lrows) != config["order"].count(left):
                    state_result["ratios"].setdefault(comparison, {})[metric] = None
                    continue
                pair_ratios = [ratio(lrows[n].get(metric), rrows[n].get(metric)) for n in sorted(lrows)]
                state_result["pairs"].setdefault(comparison, {})[metric] = [direction(x) for x in pair_ratios]
                state_result["ratios"].setdefault(comparison, {})[metric] = ratio(
                    statistics.median(x[metric] for x in lrows.values()),
                    statistics.median(x[metric] for x in rrows.values()))
        states[state] = state_result
    def material(state):
        for metric, value in states[state]["ratios"].get("D/I", {}).items():
            same = states[state]["pairs"].get("D/I", {}).get(metric, [])
            if value is not None and (value < thresholds["materiality_lower"] or value > thresholds["materiality_upper"]):
                if len(same) == config["order"].count("D") and len(set(same)) == 1 and same[0] in {"+", "-"}:
                    return True
        return False
    control = states.get("U", {}).get("ratios", {}).get("B/I", {}).get("cpu_seconds")
    if control is None:
        control = states.get("A", {}).get("ratios", {}).get("B/I", {}).get("cpu_seconds")
    verdicts = {"harness": "PENDING", "q1": "PENDING", "q2": "PENDING"}
    if control is not None:
        verdicts["harness"] = "HARNESS FAILURE" if control < thresholds["background_cpu_ratio"] else "PASS"
    if verdicts["harness"] == "HARNESS FAILURE":
        return {"states": states, "verdicts": verdicts}
    complete_u = all(states["U"]["ratios"].get("D/I", {}).get(m) is not None for m in metric_names)
    complete_s = all(states["S"]["ratios"].get("D/I", {}).get(m) is not None for m in metric_names)
    if complete_u:
        verdicts["q1"] = "COMPROMISED" if material("U") else "WITHIN BAR" if complete_s and not material("S") and all(
            thresholds["materiality_lower"] <= states[s]["ratios"]["D/I"][m] <= thresholds["materiality_upper"]
            for s in ("U", "S") for m in metric_names) else "COUNCIL"
    attended_i = grouped["A", "I"]
    unattended_i = grouped["U", "I"]
    if len(attended_i) == len(unattended_i) == config["order"].count("I"):
        comparisons = {m: ratio(statistics.median(x[m] for x in unattended_i.values()),
                                 statistics.median(x[m] for x in attended_i.values())) for m in metric_names}
        cadence_ms = statistics.median(x["lm_cadence_median_ms"] for x in unattended_i.values())
        verdicts["q2"] = "CURE CONFIRMED" if cadence_ms <= thresholds["interactive_cadence_ms"] and all(
            thresholds["materiality_lower"] <= r <= thresholds["materiality_upper"] for r in comparisons.values()) else "COUNCIL"
        verdicts["q2_evidence"] = {"U/A_interactive_ratios": comparisons, "U_interactive_lm_cadence_ms": cadence_ms}
    return {"states": states, "verdicts": verdicts}


def census_flags(path: Path, cells: list[dict], config: dict) -> dict[str, list[dict]]:
    flags = defaultdict(list)
    if not path.exists():
        return flags
    os_names = {"kernel_task", "WindowServer", "mds", "mdworker", "photoanalysisd", "backupd", "fseventsd", "XProtect", "top"}
    for line in path.read_text().splitlines():
        record = json.loads(line)
        stamp = record["wall_ns"]
        for process_line in record.get("stdout", "").splitlines():
            match = re.match(r"\s*(\d+)\s+(\S+)\s+([\d.]+)\s+", process_line)
            if not match or float(match.group(3)) <= config["thresholds"]["non_os_cpu_percent"]:
                continue
            name = match.group(2)
            if name in os_names or name.startswith(("/System/", "/usr/libexec/", "com.apple.")):
                continue
            for cell in cells:
                if cell["start_wall_ns"] <= stamp <= cell["end_wall_ns"]:
                    if int(match.group(1)) in {cell["pid"], cell.get("powermetrics_pid")}:
                        continue
                    flags[cell["dir"]].append({"pid": int(match.group(1)), "name": name,
                                               "cpu_percent": float(match.group(3)), "wall_ns": stamp})
    return flags


def markdown(rows: list[dict], decision: dict, errors: list[dict]) -> str:
    output = ["# OSCTX diagnostic summary", "", "Diagnostic only; not claim-bearing.", ""]
    for state, table in decision["states"].items():
        output += [f"## State {state}", "", "| Cell | CPU s | GPU s | LM s | LM J/token | Idle cadence ms | LM cadence ms | Census flag |",
                   "|---|---:|---:|---:|---:|---:|---:|---|"]
        for row in rows:
            if row["state"] != state:
                continue
            m = row["metrics"]
            output.append(f"| {row['context']}{row['cell_id']} | {m['cpu_seconds']:.3f} | {m['gpu_seconds']:.3f} | {m['lm_seconds']:.3f} | {m['lm_j_per_token']:.6f} | {m['idle_cadence_median_ms']:.1f} | {m['lm_cadence_median_ms']:.1f} | {'YES' if row.get('census_flags') else ''} |")
        output += ["", "| Comparison | Metric | Median ratio | Pair directions |", "|---|---|---:|---|"]
        for comparison, metrics in table["ratios"].items():
            for metric, value in metrics.items():
                output.append(f"| {comparison} | {metric} | {value:.4f} | {','.join(table['pairs'].get(comparison, {}).get(metric, []))} |" if value is not None else f"| {comparison} | {metric} | pending | |")
        output.append("")
    output += ["## Verdicts", ""] + [f"- {key}: {value}" for key, value in decision["verdicts"].items() if isinstance(value, str)]
    if errors:
        output += ["", "## Cell errors", ""] + [f"- {x['cell']}: {x['error']}" for x in errors]
    return "\n".join(output) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    args = parser.parse_args(argv)
    config = load_config(args.config)
    rows, errors = [], []
    for cell_path in sorted(args.out.glob("*.*.*/cell.json")):
        try:
            rows.append(analyze_cell(cell_path.parent))
        except Exception as exc:
            errors.append({"cell": str(cell_path.parent), "error": str(exc)})
    flags = census_flags(args.out / "census.jsonl", rows, config)
    for row in rows:
        row["census_flags"] = flags.get(row["dir"], [])
    decision = decision_table(rows, config)
    write_json(args.out / "summary.json", {"cells": rows, "errors": errors, **decision})
    (args.out / "summary.md").write_text(markdown(rows, decision, errors))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
