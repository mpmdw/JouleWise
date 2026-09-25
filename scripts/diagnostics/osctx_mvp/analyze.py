"""OSCTX reduction through production clock anchoring and interval integration."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import random
import re
import statistics
import sys

try:
    from .common import load_config, write_json
except ImportError:
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

LOWER, UPPER = math.log(.97), math.log(1.03)
CONFIDENCE = .99375


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)]


def windows(boundaries):
    grouped = defaultdict(dict)
    for item in boundaries:
        if item["edge"] in ("start", "end"):
            grouped[item["name"], item["repeat"]][item["edge"]] = item["wall_ns"] / 1e9
    result = {}
    for key, edges in grouped.items():
        if set(edges) != {"start", "end"} or edges["end"] <= edges["start"]:
            raise ValueError(f"invalid boundary pair: {key}")
        result[key] = edges["start"], edges["end"]
    return result


def cadence(records, start, end):
    gaps = [r.elapsed_ns / 1e6 for r in records[1:] if start <= r.timestamp_s <= end]
    return {"n": len(gaps), "median_ms": statistics.median(gaps) if gaps else None,
            "p95_ms": percentile(gaps, .95)}


def cluster_metrics(rich, start, end):
    totals = defaultdict(lambda: {"active": 0., "duration": 0., "freq_active": 0., "freq_weight": 0.})
    for record in rich:
        right = record["timestamp_s"]
        left = right - record["elapsed_ns"] / 1e9
        overlap = max(0., min(end, right) - max(start, left))
        if not overlap:
            continue
        for cluster in record["clusters"]:
            name = cluster.get("name") or ""
            kind = "E" if name.startswith("E") else "P" if name.startswith("P") else None
            if kind is None:
                continue
            cpus = cluster.get("cpus") or []
            active = [max(0., 1. - float(cpu["idle_ratio"]) - float(cpu.get("down_ratio") or 0))
                      for cpu in cpus if cpu.get("idle_ratio") is not None]
            if not active:
                continue
            mean = statistics.mean(active)
            totals[kind]["active"] += mean * overlap * len(active)
            totals[kind]["duration"] += overlap * len(active)
            freq = cluster.get("freq_hz")
            if isinstance(freq, (int, float)) and freq > 0:
                totals[kind]["freq_active"] += freq * mean * overlap * len(active)
                totals[kind]["freq_weight"] += mean * overlap * len(active)
    return {kind: {"active_residency": val["active"] / val["duration"] if val["duration"] else None,
                   "active_frequency_hz": val["freq_active"] / val["freq_weight"] if val["freq_weight"] else None}
            for kind, val in totals.items()}


def interval_checks(records, start, end):
    counter, boundary = 0., 0.
    for record in records:
        right = record.timestamp_s
        left = right - record.elapsed_ns / 1e9
        duration = right - left
        if duration <= 0:
            continue
        overlap = max(0., min(end, right) - max(start, left))
        if overlap:
            counter += sum(record.rail_energy_mj.values()) / 1000 * overlap / duration
        if left < start < right:
            boundary += record.combined_power_w * (start - left)
        if left < end < right:
            boundary += record.combined_power_w * (right - end)
    return counter, boundary


def reduce_trace(raw: bytes, boundary_records: list[dict], endpoint: float) -> dict:
    records = parse_powermetrics_records(raw, first_record_endpoint_s=endpoint)
    samples = samples_from_raw_powermetrics(raw, first_record_endpoint_s=endpoint)
    rich = decode_rich_telemetry(raw, first_record_endpoint_s=endpoint)
    curves = defaultdict(list)
    for sample in samples:
        curves[sample.rail].append(TracePoint(sample.timestamp_s, sample.power_w,
                                             sample.interval_start_s, sample.interval_end_s))
    result = {}
    for (name, repeat), (start, end) in windows(boundary_records).items():
        rails = {rail: _integrate(curve, start, end) for rail, curve in curves.items()}
        gross = math.fsum(rails.values())
        counter, boundary = interval_checks(records, start, end)
        result[f"{name}.{repeat}"] = {"duration_s": end - start, "energy_j": gross,
                                       "rail_energy_j": rails, "counter_energy_j": counter,
                                       "integral_disagreement_j": abs(gross-counter),
                                       "boundary_uncertainty_j": boundary,
                                       "cadence": cadence(records, start, end),
                                       "thermal_pressure": [r.thermal_pressure for r in records
                                                            if start <= r.timestamp_s <= end],
                                       "clusters": cluster_metrics(rich, start, end)}
    return result


def derive_endpoint(raw, cell):
    stamps = {key: ClockStamp(**value) for key, value in cell["clock_stamps"].items()}
    native = parse_powermetrics_records(raw)
    evidence, endpoint = resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)(
        stamps=stamps, records=anchor_records_from_powermetrics(native))
    if endpoint is None:
        raise ValueError(f"production clock anchor unresolved: {evidence['clock_anchor']}")
    return endpoint, evidence


def request_metrics(segments, repeats, config):
    idle = segments["idle.1"]
    idle_w = idle["energy_j"] / idle["duration_s"]
    values, flags = [], []
    for repeat in repeats:
        number = repeat["repeat"]
        segment = segments[f"lm.{number}"]
        gross = segment["energy_j"]
        net = gross - idle_w * segment["duration_s"]
        item = {"repeat": number, "gross_j": gross, "net_j": net,
                "j_per_token": net / repeat["output_tokens"] if net > 0 and repeat["output_tokens"] else None,
                "generation_tps": repeat["generation_tps"], "prompt_tps": repeat["prompt_tps"],
                "output_hash": repeat["output_hash"], "output_tokens": repeat["output_tokens"],
                "boundary_uncertainty_j": segment["boundary_uncertainty_j"],
                "integral_disagreement_j": segment["integral_disagreement_j"]}
        if net <= 0:
            flags.append(f"nonpositive_net_energy:lm.{number}")
        if segment["boundary_uncertainty_j"] > config["thresholds"]["boundary_fraction"] * net:
            flags.append(f"boundary_uncertainty:lm.{number}")
        if segment["integral_disagreement_j"] > config["thresholds"]["integral_j"]:
            flags.append(f"two_integral_disagreement:lm.{number}")
        if repeat["output_tokens"] != config["segments"]["lm_tokens"] or repeat.get("flags"):
            flags.append(f"token_integrity:lm.{number}")
        values.append(item)
    return values, flags


def parse_cpu_time(value):
    try:
        days = 0
        if "-" in value:
            day_text, value = value.split("-", 1)
            days = int(day_text)
        parts = value.split(":")
        return days*86400 + sum(float(part) * 60 ** i for i, part in enumerate(reversed(parts)))
    except ValueError:
        return None


def parse_ps(text):
    result = {}
    for line in text.splitlines()[1:]:
        match = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(.+)$", line)
        if match:
            seconds = parse_cpu_time(match.group(3))
            if seconds is not None:
                result[int(match.group(1))] = {"ppid": int(match.group(2)), "cpu_s": seconds, "comm": match.group(4)}
    return result


def census_cpu_flags(records, windows_by_key, *, workload_pid, sampler_pid, allow_pids, fraction=.05):
    flags = []
    parsed = [(r["wall_ns"] / 1e9, parse_ps(r.get("ps", {}).get("stdout", "")), r.get("ps", {}).get("pid")) for r in records]
    for (left_t, left, _), (right_t, right, census_pid) in zip(parsed, parsed[1:]):
        delta_t = right_t - left_t
        if delta_t <= 0:
            continue
        for key, (start, end) in windows_by_key.items():
            if min(end, right_t) <= max(start, left_t):
                continue
            for pid in left.keys() & right.keys():
                if pid in set(allow_pids) | {workload_pid, sampler_pid, census_pid}:
                    continue
                delta_cpu = right[pid]["cpu_s"] - left[pid]["cpu_s"]
                if delta_cpu / delta_t >= fraction:
                    flags.append({"segment": f"{key[0]}.{key[1]}", "pid": pid,
                                  "comm": right[pid]["comm"], "core_fraction": delta_cpu / delta_t})
    return flags


def analyze_cell(directory: Path, config: dict) -> dict:
    cell = json.loads((directory / "cell.json").read_text())
    done = json.loads((directory / "done.json").read_text())
    if not done["ok"] or done.get("interrupted") or cell.get("interrupted"):
        raise ValueError("cell failed or interrupted")
    raw = (directory / "powermetrics.plist").read_bytes()
    endpoint, evidence = derive_endpoint(raw, cell)
    segments = reduce_trace(raw, cell["boundaries"], endpoint)
    requests, flags = request_metrics(segments, cell["repeats"]["lm"], config)
    flags += [f"two_integral_disagreement:{key}" for key, segment in segments.items()
              if segment["integral_disagreement_j"] > config["thresholds"]["integral_j"]]
    flags += cell.get("flags", [])
    census_path = directory / "census.jsonl"
    census = [json.loads(line) for line in census_path.read_text().splitlines()] if census_path.exists() else []
    cpu_flags = census_cpu_flags(census, windows(cell["boundaries"]),
                                 workload_pid=cell["pid"], sampler_pid=cell.get("powermetrics_pid"),
                                 allow_pids=cell.get("allow_pids", []),
                                 fraction=config["thresholds"]["census_core_fraction"])
    flags += [f"census_cpu:{item['segment']}:{item['pid']}" for item in cpu_flags]
    if any(r.get("interrupted") for r in census):
        flags.append("interrupted")
    valid_e = all(x["j_per_token"] is not None for x in requests)
    valid_tokens = not any(flag.startswith("token_integrity") or flag in ("token_count_mismatch", "early_finish")
                           for flag in flags)
    metrics = {"E": statistics.median(x["j_per_token"] for x in requests) if valid_e else None,
               "R": statistics.median(x["generation_tps"] for x in requests) if valid_tokens else None,
               "gross_j": statistics.median(x["gross_j"] for x in requests),
               "cpu_seconds": statistics.median(x["seconds"] for x in cell["repeats"]["cpu"]),
               "lm_cadence_median_ms": statistics.median(v["cadence"]["median_ms"] for k, v in segments.items()
                                                       if k.startswith("lm.") and v["cadence"]["median_ms"] is not None)}
    if not valid_tokens:
        metrics["E"] = None
    block_name = directory.name.split(".")[0]
    phase = int(re.search(r"S-p(\d)-", block_name).group(1)) if re.search(r"S-p(\d)-", block_name) else None
    return {"stage": cell["stage"], "state": cell["state"], "context": cell["context"],
            "block": block_name, "phase": phase,
            "pid": cell["pid"], "dir": str(directory), "metrics": metrics,
            "requests": requests, "segments": segments, "clock_anchor": evidence["clock_anchor"],
            "flags": sorted(set(flags)), "census_cpu_flags": cpu_flags, "allow_pids": cell.get("allow_pids", [])}


# Regularized incomplete beta and Student-t CDF; no optional statistics package.
def _betacf(a, b, x):
    qab, qap, qam = a+b, a+1, a-1
    c, d = 1., 1. - qab*x/qap
    if abs(d) < 1e-300:
        d = 1e-300
    d = 1./d
    h = d
    for m in range(1, 301):
        m2 = 2*m
        aa = m*(b-m)*x/((qam+m2)*(a+m2))
        d = 1.+aa*d
        if abs(d) < 1e-300: d = 1e-300
        c = 1.+aa/c
        if abs(c) < 1e-300: c = 1e-300
        d = 1./d
        h *= d*c
        aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2))
        d = 1.+aa*d
        if abs(d) < 1e-300: d = 1e-300
        c = 1.+aa/c
        if abs(c) < 1e-300: c = 1e-300
        d = 1./d
        delta = d*c
        h *= delta
        if abs(delta-1.) < 3e-14:
            break
    return h


def _betai(a, b, x):
    if x <= 0: return 0.
    if x >= 1: return 1.
    front = math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    if x < (a+1)/(a+b+2):
        return front*_betacf(a,b,x)/a
    return 1-front*_betacf(b,a,1-x)/b


def student_t_cdf(t, df):
    tail = .5*_betai(df/2, .5, df/(df+t*t))
    return 1-tail if t >= 0 else tail


def student_t_ppf(p, df):
    lo, hi = -100., 100.
    for _ in range(90):
        mid = (lo+hi)/2
        if student_t_cdf(mid, df) < p: lo = mid
        else: hi = mid
    return (lo+hi)/2


def paired_interval(log_ratios, confidence=CONFIDENCE):
    n = len(log_ratios)
    if n < 2: return None
    mean = statistics.mean(log_ratios)
    sd = statistics.stdev(log_ratios)
    half = student_t_ppf((1+confidence)/2, n-1)*sd/math.sqrt(n)
    return {"n": n, "mean_log": mean, "sd_log": sd, "lower_log": mean-half, "upper_log": mean+half,
            "ratio": math.exp(mean), "lower_ratio": math.exp(mean-half), "upper_ratio": math.exp(mean+half)}


def verdict(interval):
    if interval is None: return "INCONCLUSIVE"
    if interval["lower_log"] > UPPER or interval["upper_log"] < LOWER:
        return "DIFFERENT"
    if interval["lower_log"] >= LOWER and interval["upper_log"] <= UPPER:
        return "EQUIVALENT"
    return "INCONCLUSIVE"


def paired_rows(rows, comparison, endpoint):
    left_arm, right_arm = comparison.split("/")
    groups = defaultdict(dict)
    for row in rows:
        groups[row["block"]][row["context"]] = row
    logs, absolute, flagged = [], [], []
    for block, arms in sorted(groups.items()):
        if left_arm not in arms or right_arm not in arms:
            continue
        left, right = (arms[arm]["metrics"].get(endpoint) for arm in (left_arm, right_arm))
        if left is None or right is None or left <= 0 or right <= 0:
            flagged.append(block)
            continue
        logs.append(math.log(left/right))
        absolute.append(left-right)
    return logs, absolute, flagged


def decision_table(rows, config):
    verdicts, intervals, flags = {}, {}, []
    u1 = [row for row in rows if row["stage"] == "U1"]
    u2 = [row for row in rows if row["stage"] == "U2"]
    eligible = [row for row in u1+u2 if row["context"] in ("D", "I", "SH")]
    stage = "U2" if u2 else "U1" if u1 else None
    if u1:
        for comparison in ("D/I", "SH/I"):
            for endpoint in ("E", "R"):
                key = f"{comparison}:{endpoint}"
                logs, absolute, flagged = paired_rows(eligible, comparison, endpoint)
                interval = paired_interval(logs) if len(logs) in (6, 12) else None
                if interval and endpoint == "E":
                    interval["absolute_j_per_token"] = statistics.mean(absolute)
                    # Paired absolute interval is descriptive and retains the same confidence rule.
                    critical = student_t_ppf((1+CONFIDENCE)/2, len(absolute)-1)
                    half = critical*statistics.stdev(absolute)/math.sqrt(len(absolute))
                    interval["absolute_interval_j_per_token"] = [statistics.mean(absolute)-half, statistics.mean(absolute)+half]
                if interval:
                    # Descriptive, Gaussian paired approximation to an 80%-power effect.
                    mde = (student_t_ppf((1+CONFIDENCE)/2, len(logs)-1) +
                           student_t_ppf(.8, len(logs)-1)) * interval["sd_log"] / math.sqrt(len(logs))
                    interval["approx_80pct_mde_ratio"] = math.exp(UPPER + mde)
                intervals[key] = interval
                verdicts[key] = verdict(interval)
                flags += [f"invalid_log_block:{block}" for block in flagged]
    sandwich = {}
    s_rows = [r for r in rows if r["stage"] == "S"]
    for endpoint in ("E", "R"):
        by_phase = defaultdict(list)
        for row in s_rows:
            if row.get("phase") is not None and row["metrics"].get(endpoint) is not None:
                by_phase[row["phase"]].append(row["metrics"][endpoint])
        if all(len(by_phase[p]) == config["sizes"]["sandwich_cells"] for p in (0, 1, 2)):
            logs = [math.log(s / math.sqrt(u1*u2)) for u1, s, u2 in zip(by_phase[0], by_phase[1], by_phase[2])]
            sandwich[endpoint] = paired_interval(logs)
        else:
            sandwich[endpoint] = None
    b_cpu = [r["metrics"].get("cpu_seconds") for r in u1 if r["context"] == "B"]
    i_cpu = [r["metrics"].get("cpu_seconds") for r in u1 if r["context"] == "I"]
    b_control = (statistics.median(b_cpu) / statistics.median(i_cpu)
                 if len(b_cpu) == config["sizes"]["background_cells"] and i_cpu and
                 all(isinstance(x, (int, float)) and x > 0 for x in b_cpu+i_cpu) else None)
    if b_control is not None and b_control < config["thresholds"]["background_cpu_ratio"]:
        flags.append("background_control_investigate")
    i_cadence = [r["metrics"].get("lm_cadence_median_ms") for r in eligible if r["context"] == "I"]
    i_cadence = [x for x in i_cadence if isinstance(x, (int, float))]
    median_i_cadence = statistics.median(i_cadence) if i_cadence else None
    interpretation = {
        "default_context_compromised": any(verdicts.get(f"D/I:{endpoint}") == "DIFFERENT" for endpoint in ("E", "R")),
        "cure_supported_for_tested_shell": bool(u1) and all(verdicts.get(f"SH/I:{endpoint}") == "EQUIVALENT" for endpoint in ("E", "R"))
            and median_i_cadence is not None and median_i_cadence <= config["thresholds"]["interactive_cadence_ms"],
        "interactive_cadence_median_ms": median_i_cadence,
    }
    return {"stage": stage, "verdicts": verdicts, "intervals": intervals,
            "sandwich_intervals": sandwich, "background_cpu_ratio": b_control,
            "interpretation": interpretation, "flags": sorted(set(flags))}


def equivalence_power(sd, n, draws=20000, seed=20260924):
    """Monte Carlo exact Gaussian paired model with Student-t interval, >=20k draws."""
    if draws < 20000: raise ValueError("at least 20,000 draws required")
    if sd < 0: raise ValueError("SD must be nonnegative")
    if sd == 0: return 1.
    rng = random.Random(seed)
    critical = student_t_ppf((1+CONFIDENCE)/2, n-1)
    wins = 0
    for _ in range(draws):
        values = [rng.gauss(0, sd) for _ in range(n)]
        mean = statistics.mean(values)
        half = critical*statistics.stdev(values)/math.sqrt(n)
        wins += mean-half >= LOWER and mean+half <= UPPER
    return wins/draws


def power_table(sd_e, sd_r):
    return [{"endpoint": endpoint, "n": n, "sd_multiplier": multiplier, "sd_log": sd*multiplier,
             "power": equivalence_power(sd*multiplier, n), "method": "20000-draw seeded Gaussian paired simulation"}
            for endpoint, sd in (("E", sd_e), ("R", sd_r)) for n in (6, 12) for multiplier in (1., 1.5)]


def markdown(rows, decision, errors, discarded):
    lines = ["# OSCTX diagnostic summary", "", "Diagnostic only; not claim-bearing.", ""]
    for stage in ("stage0", "U1", "U2", "S"):
        stage_rows = [r for r in rows if r["stage"] == stage]
        if not stage_rows: continue
        lines += [f"## {stage}", "", "| Block | Arm | E J/token | R token/s | Flags |", "|---|---|---:|---:|---|"]
        for row in stage_rows:
            m = row["metrics"]
            energy = f"{m['E']:.6f}" if m.get("E") is not None else "invalid"
            rate = f"{m['R']:.3f}" if m.get("R") is not None else "invalid"
            lines.append(f"| {row['block']} | {row['context']} | {energy} | {rate} | {', '.join(row['flags'])} |")
        lines.append("")
        if stage in ("U1", "U2"):
            lines += ["| Contrast | Verdict | Ratio 99.375% interval | Absolute J/token contrast 99.375% interval | Approx. 80% MDE ratio |",
                      "|---|---|---|---|---:|"]
            for key, interval in decision["intervals"].items():
                if interval:
                    absolute = interval.get("absolute_interval_j_per_token", "")
                    lines.append(f"| {key} | {decision['verdicts'][key]} | {interval['ratio']:.5f} [{interval['lower_ratio']:.5f}, {interval['upper_ratio']:.5f}] | {interval.get('absolute_j_per_token', '')} {absolute} | {interval['approx_80pct_mde_ratio']:.5f} |")
                else:
                    lines.append(f"| {key} | INCONCLUSIVE | unavailable | unavailable | unavailable |")
            lines.append("")
            lines += [f"Interactive LM cadence: {decision['interpretation']['interactive_cadence_median_ms']} ms; "
                      f"tested-shell cure supported: {decision['interpretation']['cure_supported_for_tested_shell']}; "
                      f"default context compromised: {decision['interpretation']['default_context_compromised']}.", ""]
        if stage == "S":
            lines += ["Exploratory S versus geometric mean of bracketing U cells; no verdict.", "",
                      "| Endpoint | Ratio 99.375% interval |", "|---|---|"]
            for endpoint, interval in decision["sandwich_intervals"].items():
                lines.append(f"| {endpoint} | {interval['ratio']:.5f} [{interval['lower_ratio']:.5f}, {interval['upper_ratio']:.5f}] |" if interval else f"| {endpoint} | unavailable |")
            lines.append("")
    all_flags = sorted(set(decision["flags"] + [f"{r['dir']}: {flag}" for r in rows for flag in r["flags"]]))
    if all_flags:
        lines += ["## Flags", ""] + [f"- {flag}" for flag in all_flags]
    if errors:
        lines += ["", "## Cell errors and discarded attempts", ""] + [f"- {e['cell']}: {e['error']}" for e in errors]
    if discarded:
        lines += ["", "## Discarded interrupted attempts", ""] + [f"- {path}" for path in discarded]
    return "\n".join(lines) + "\n"


def analyze_directory(out: Path, config: dict, *, analyzer_backend=None):
    rows, errors, discarded = [], [], []
    for path in sorted(out.rglob("cell.json")):
        try:
            if (path.parent / "discarded.json").exists():
                discarded.append(str(path.parent))
                continue
            row = analyzer_backend(path.parent, config) if analyzer_backend else analyze_cell(path.parent, config)
            if row.get("stage") == "U1" and "warmup" in row.get("block", ""):
                continue
            rows.append(row)
        except Exception as exc:
            errors.append({"cell": str(path.parent), "error": str(exc)})
    references = {}
    for row in rows:
        stage = row["stage"]
        for request in row.get("requests", []):
            reference = references.setdefault(stage, request["output_hash"])
            if request["output_hash"] != reference:
                row["flags"].append("output_hash_mismatch")
                row["metrics"]["E"] = None
                row["metrics"]["R"] = None
    decision = decision_table(rows, config)
    report = {"cells": rows, "errors": errors, "discarded": discarded,
              **decision, "stage_references": references}
    write_json(out / "summary.json", report)
    (out / "summary.md").write_text(markdown(rows, decision, errors, discarded))
    return report


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "power":
        power = argparse.ArgumentParser(prog="analyze.py power")
        power.add_argument("--stage0-summary", type=Path)
        power.add_argument("--sd-e", type=float)
        power.add_argument("--sd-r", type=float)
        args = power.parse_args(argv[1:])
        if args.stage0_summary:
            rows = json.loads(args.stage0_summary.read_text())["cells"]
            sd_e = statistics.stdev(paired_rows(rows, "SH/I", "E")[0])
            sd_r = statistics.stdev(paired_rows(rows, "SH/I", "R")[0])
        elif args.sd_e is not None and args.sd_r is not None:
            sd_e, sd_r = args.sd_e, args.sd_r
        else:
            power.error("provide --stage0-summary or both paired SDs")
        print(json.dumps(power_table(sd_e, sd_r), indent=2))
        return 0
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    args = parser.parse_args(argv)
    report = analyze_directory(args.out, load_config(args.config))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
