"""Analyze production JouleWise bundles by launch context."""
from __future__ import annotations

import argparse
import csv
import hashlib
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

LOWER, UPPER = math.log(.97), math.log(1.03)
CONFIDENCE = .99375


DECLARED_REASONS = {"environment_admission_failed", "environment_admission_missing", "instrument_calibration_missing"}


def bundle_hash(bundle: Path) -> tuple[str | None, int | None]:
    tokens = bundle / "outputs" / "tokens.jsonl"
    if tokens.exists():
        ids = [json.loads(line)["token_id"] for line in tokens.read_text().splitlines() if line.strip()]
        if any(type(token_id) is not int for token_id in ids):
            raise ValueError("output token IDs must be integers")
        return "token_ids:" + hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest(), len(ids)
    return None, None


def edge_bound(bundle: Path, idle_w: float) -> float:
    events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
    def marker(kind):
        found = [x["timestamp_s"] for x in events if x.get("event_type") == kind and x.get("phase") == "measured_run"]
        if len(found) != 1:
            raise ValueError(f"missing or duplicate {kind} marker")
        return found[0]
    boundaries = marker("sampling_started"), marker("sampling_stopped")
    with (bundle / "power_trace.csv").open(newline="") as stream:
        samples = list(csv.DictReader(stream))
    intervals = {}
    for row in samples:
        key = (float(row["interval_start_s"]), float(row["interval_end_s"]))
        intervals[key] = intervals.get(key, 0.) + float(row["power_w"])
    result = 0.
    for boundary in boundaries:
        crossing = [(key, power) for key, power in intervals.items() if key[0] <= boundary <= key[1]]
        if not crossing:
            raise ValueError("power trace does not bracket request edge")
        (left, right), power = min(crossing, key=lambda item: item[0][1] - item[0][0])
        result += .25 * abs(power - idle_w) * (right - left)
    if not math.isfinite(result):
        raise ValueError("nonfinite edge bound")
    return result


def bundle_evidence(bundle: Path, reference_hash: str | None = None) -> dict:
    summary = json.loads((bundle / "summary_metrics.json").read_text())
    precheck = summary.get("window_evidence_precheck", {}).get("idle_subtracted_request") or {}
    reasons = set(precheck.get("reasons", []))
    output_hash, count = bundle_hash(bundle)
    issues = []
    if summary.get("status") != "succeeded": issues.append("status")
    anchor = precheck.get("clock_anchor_bound_s")
    if not isinstance(anchor, (int, float)) or not math.isfinite(anchor) or anchor > .05 or anchor < 0:
        issues.append("clock_anchor")
    if not precheck: issues.append("precheck_missing")
    if reasons - DECLARED_REASONS: issues.append("precheck:" + ",".join(sorted(reasons - DECLARED_REASONS)))
    if precheck.get("eligible") is False and not reasons:
        issues.append("precheck_unexplained")
    if count != 512: issues.append("output_tokens")
    if output_hash is None: issues.append("output_hash_missing")
    if reference_hash is not None and output_hash != reference_hash: issues.append("output_hash_mismatch")
    idle = summary.get("idle_baseline") or {}
    bound_terms = summary.get("energy_bound_terms_j") or {}
    net = summary.get("idle_subtracted_energy_j")
    drift = bound_terms.get("E_drift_bound_j")
    ratio = drift / net if all(isinstance(x, (int, float)) and math.isfinite(x) for x in (drift, net)) and net > 0 else None
    diagnostic_issues = []
    if ratio is None: diagnostic_issues.append("drift_ratio_missing")
    anchor_j = bound_terms.get("E_clock_anchor_shift_bound_j")
    if not isinstance(anchor_j, (int, float)) or not math.isfinite(anchor_j): diagnostic_issues.append("anchor_energy_bound_missing")
    try:
        edge_j = edge_bound(bundle, idle["power_w_mean"])
    except (KeyError, OSError, ValueError, TypeError):
        edge_j = None
        diagnostic_issues.append("edge_bound_missing")
    return {"bundle": str(bundle), "status": summary.get("status"), "precheck": precheck,
            "metrics": {"E": summary.get("energy_output_token_j"), "R": summary.get("inter_token_throughput_tokens_s"),
                        "gross_energy_j": summary.get("gross_energy_j"), "idle_power_w_mean": idle.get("power_w_mean"),
                        "idle_power_w_stddev": idle.get("power_w_stddev"),
                        "median_sample_interval_s": (summary.get("idle_mean_uncertainty") or {}).get("median_sample_interval_s"),
                        "energy_bound_terms_j": bound_terms, "net_j": net, "drift_ratio": ratio,
                        "edge_bound_j": edge_j, "edge_bound_j_per_token": edge_j / 512 if edge_j is not None else None,
                        "attribution_bound_j": (anchor_j + drift + edge_j) if all(isinstance(x, (int, float)) for x in (anchor_j, drift, edge_j)) else None},
            "output_hash": output_hash, "output_tokens": count, "issues": issues,
            "diagnostic_issues": diagnostic_issues, "valid": not issues}


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
            owned = set(allow_pids) | {workload_pid, sampler_pid, census_pid}
            changed = True
            while changed:
                changed = False
                for pid, info in right.items():
                    if info["ppid"] in owned and pid not in owned:
                        owned.add(pid)
                        changed = True
            for pid in left.keys() & right.keys():
                if pid in owned:
                    continue
                delta_cpu = right[pid]["cpu_s"] - left[pid]["cpu_s"]
                if delta_cpu / delta_t >= fraction:
                    flags.append({"segment": f"{key[0]}.{key[1]}", "pid": pid,
                                  "comm": right[pid]["comm"], "core_fraction": delta_cpu / delta_t})
    return flags


def analyze_cell(directory: Path, config: dict, reference_hash: str | None = None) -> dict:
    cell = json.loads((directory / "cell.json").read_text())
    done = json.loads((directory / "done.json").read_text())
    runs = [bundle_evidence(Path(item["bundle"]), reference_hash) for item in cell["runs"]]
    if len(runs) != config["runs_per_cell"][cell["stage"]]:
        raise ValueError("wrong number of production bundles")
    flags = list(cell.get("flags", []))
    if not done.get("ok") or done.get("interrupted") or cell.get("interrupted"):
        flags.append("interrupted")
    if any(not run["valid"] for run in runs):
        flags.append("bundle_invalid")
    hashes = {run["output_hash"] for run in runs}
    if len(hashes) > 1:
        flags.extend(("output_hash_mismatch", "bundle_invalid"))
    census_path = directory / "census.jsonl"
    census = [json.loads(line) for line in census_path.read_text().splitlines()] if census_path.exists() else []
    if any(record.get("interrupted") for record in census):
        flags.append("interrupted")
    windows_by_key = {}
    for number, run in enumerate(runs, 1):
        try:
            events = [json.loads(line) for line in (Path(run["bundle"]) / "events.jsonl").read_text().splitlines()]
        except (OSError, ValueError):
            events = []
        idle_starts = [x["timestamp_s"] for x in events if x.get("event_type") == "stage_started" and x.get("phase") == "idle_baseline"]
        idle_ends = [x["timestamp_s"] for x in events if x.get("event_type") == "stage_completed" and x.get("phase") == "idle_baseline"]
        if len(idle_starts) == len(idle_ends) == 1 and idle_starts[0] < idle_ends[0]:
            windows_by_key[("idle", number)] = (idle_starts[0], idle_ends[0])
        else:
            flags.append(f"census_idle_window_missing:r{number}")
        starts = [x["timestamp_s"] for x in events if x.get("event_type") == "sampling_started" and x.get("phase") == "measured_run"]
        ends = [x["timestamp_s"] for x in events if x.get("event_type") == "sampling_stopped" and x.get("phase") == "measured_run"]
        if len(starts) == len(ends) == 1:
            windows_by_key[("run", number)] = (starts[0], ends[0])
        else:
            flags.append(f"census_window_missing:r{number}")
    child_pids = [item["child"]["pid"] for item in cell["runs"] if item.get("child", {}).get("pid")]
    cpu_flags = census_cpu_flags(census, windows_by_key, workload_pid=cell["pid"], sampler_pid=None,
                                 allow_pids=cell.get("allow_pids", []) + child_pids,
                                 fraction=config["thresholds"]["census_core_fraction"])
    if cpu_flags: flags.append("census_cpu")
    valid = not any(flag in ("interrupted", "bundle_invalid", "output_hash_mismatch") for flag in flags)
    def mean_metric(key):
        values = [run["metrics"].get(key) for run in runs]
        return statistics.mean(values) if valid and all(isinstance(x, (int, float)) and math.isfinite(x) for x in values) else None
    term_keys = set().union(*(run["metrics"]["energy_bound_terms_j"] for run in runs))
    energy_bound_terms = {}
    for key in term_keys:
        values = [run["metrics"]["energy_bound_terms_j"].get(key) for run in runs]
        energy_bound_terms[key] = (statistics.mean(values) if valid and
                                   all(isinstance(x, (int, float)) and math.isfinite(x) for x in values) else None)
    metrics = {"E": mean_metric("E"), "R": mean_metric("R"), "gross_energy_j": mean_metric("gross_energy_j"),
               "idle_power_w_mean": mean_metric("idle_power_w_mean"),
               "idle_power_w_stddev": mean_metric("idle_power_w_stddev"),
               "median_sample_interval_s": mean_metric("median_sample_interval_s"),
               "net_j": mean_metric("net_j"), "edge_bound_j_per_token": mean_metric("edge_bound_j_per_token"),
               "attribution_bound_j": mean_metric("attribution_bound_j"),
               "energy_bound_terms_j": energy_bound_terms,
               "drift_ratio": None,
               "max_run_drift_ratio": max((run["metrics"]["drift_ratio"] for run in runs if run["metrics"]["drift_ratio"] is not None), default=None),
               "cpu_seconds": statistics.mean(x["seconds"] for x in cell.get("cpu", [])) if cell.get("cpu") else None}
    if metrics["net_j"] and energy_bound_terms.get("E_drift_bound_j") is not None:
        metrics["drift_ratio"] = energy_bound_terms["E_drift_bound_j"] / metrics["net_j"]
    block_name = directory.name.split(".")[0]
    match = re.search(r"S-p(\d)-", block_name)
    return {"stage": cell["stage"], "state": cell["state"], "context": cell["context"],
            "block": block_name, "phase": int(match.group(1)) if match else None,
            "pid": cell["pid"], "cell_id": cell["cell_id"], "dir": str(directory), "metrics": metrics, "runs": runs,
            "requests": [{"output_hash": run["output_hash"]} for run in runs],
            "flags": sorted(set(flags)), "census_cpu_flags": cpu_flags,
            "allow_pids": cell.get("allow_pids", [])}


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
        key = (row["stage"], row["block"])
        if row["context"] in groups[key]:
            raise ValueError(f"duplicate pairing arm: {key} {row['context']}")
        groups[key][row["context"]] = row
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
                expected_pairs = config["sizes"]["u_blocks"] * (2 if u2 else 1)
                interval = paired_interval(logs) if len(logs) == expected_pairs else None
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
                result = verdict(interval)
                if interval:
                    arm_a, arm_b = comparison.split("/")
                    groups = defaultdict(dict)
                    for row in eligible:
                        key_pair = (row["stage"], row["block"])
                        if row["context"] in groups[key_pair]:
                            raise ValueError(f"duplicate pairing arm: {key_pair} {row['context']}")
                        groups[key_pair][row["context"]] = row
                    pairs = [(arms[arm_a], arms[arm_b]) for arms in groups.values()
                             if arm_a in arms and arm_b in arms and
                             all(arms[arm]["metrics"].get(endpoint) is not None for arm in (arm_a, arm_b))]
                    def log_bound(row):
                        m = row["metrics"]
                        bound, net = m.get("attribution_bound_j"), m.get("net_j")
                        if (not isinstance(bound, (int, float)) or not isinstance(net, (int, float)) or
                            not math.isfinite(bound) or not math.isfinite(net) or net <= bound):
                            return float("inf")
                        return -math.log1p(-bound/net)
                    if endpoint == "E":
                        widened_by = statistics.mean(log_bound(a) + log_bound(b) for a, b in pairs)
                        if math.isfinite(widened_by):
                            interval["widened_lower_log"] = interval["lower_log"] - widened_by
                            interval["widened_upper_log"] = interval["upper_log"] + widened_by
                            interval["widened_lower_ratio"] = math.exp(interval["widened_lower_log"])
                            interval["widened_upper_ratio"] = math.exp(interval["widened_upper_log"])
                        else:
                            interval["widened_lower_log"] = interval["widened_upper_log"] = None
                            interval["widened_lower_ratio"] = interval["widened_upper_ratio"] = None
                            interval["widened_status"] = "unbounded"
                        drift_ratios = [row["metrics"].get("drift_ratio") for pair in pairs for row in pair]
                        interval["max_cell_drift_ratio"] = max(drift_ratios) if all(x is not None for x in drift_ratios) else None
                        interval["mean_edge_bound_j_per_token_by_arm"] = {
                            arm: statistics.mean(row["metrics"].get("edge_bound_j_per_token") or 0.
                                                 for pair in pairs for row in pair if row["context"] == arm)
                            for arm in (arm_a, arm_b)}
                        if result == "EQUIVALENT" and (interval["max_cell_drift_ratio"] is None or
                                                       interval["max_cell_drift_ratio"] > .03):
                            result = "INCONCLUSIVE-by-attribution"
                    if result == "DIFFERENT" and endpoint == "E" and comparison == "D/I":
                        edges = interval["mean_edge_bound_j_per_token_by_arm"]
                        if any(row["metrics"].get("edge_bound_j_per_token") is None for pair in pairs for row in pair):
                            result = "INCONCLUSIVE"
                            flags.append(f"edge_bound_missing:{key}")
                        elif abs(interval["absolute_j_per_token"]) < abs(edges[arm_a] - edges[arm_b]):
                            result = "INCONCLUSIVE"
                            flags.append(f"edge_bound_downgrade:{key}")
                verdicts[key] = result
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
    i_cadence = [1000 * r["metrics"].get("median_sample_interval_s") for r in eligible
                 if r["context"] == "I" and r["metrics"].get("median_sample_interval_s") is not None]
    i_cadence = [x for x in i_cadence if isinstance(x, (int, float))]
    median_i_cadence = statistics.median(i_cadence) if i_cadence else None
    interpretation = {
        "default_context_compromised": any(verdicts.get(f"D/I:{endpoint}") == "DIFFERENT" for endpoint in ("E", "R")),
        "cure_supported_for_tested_shell": bool(u1) and all(verdicts.get(f"SH/I:{endpoint}") == "EQUIVALENT" for endpoint in ("E", "R"))
            and median_i_cadence is not None and median_i_cadence <= config["thresholds"]["interactive_cadence_ms"],
        "interactive_cadence_median_ms": median_i_cadence,
    }
    invalid_counts = {arm: sum("bundle_invalid" in row.get("flags", []) for row in rows if row.get("context") == arm)
                      for arm in ("D", "I", "SH", "B")}
    return {"stage": stage, "verdicts": verdicts, "intervals": intervals, "invalid_cell_counts": invalid_counts,
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


def power_table(sd_e, sd_r, n_values=(6, 12), *, runs_per_cell_u=1):
    if isinstance(sd_e, (int, float)):
        estimates = {contrast: {"E": sd_e, "R": sd_r} for contrast in ("D/I", "SH/I")}
    else:
        estimates = sd_e
    table = []
    for contrast, endpoints in estimates.items():
        for endpoint, sd in endpoints.items():
            for n in n_values:
                for multiplier in (1., 1.5, 2.):
                    scaled = sd * multiplier
                    power = equivalence_power(scaled, n)
                    mde = math.exp(UPPER + (student_t_ppf((1+CONFIDENCE)/2, n-1) +
                                            student_t_ppf(.8, n-1)) * scaled / math.sqrt(n))
                    table.append({"contrast": contrast, "endpoint": endpoint, "n": n,
                                  "runs_per_cell_U": runs_per_cell_u,
                                  "sd_multiplier": multiplier, "sd_log": scaled,
                                  "equivalence_power": power,
                                  "equivalence_power_mc_se": math.sqrt(power*(1-power)/20000),
                                  "approx_80pct_material_difference_mde_ratio": mde,
                                  "method": "20000-draw seeded Gaussian paired simulation"})
    return table


def u_replication_spread(stage0, runs_per_cell_u: int, stage0_runs_per_cell: int = 2):
    """Paired variance = between-block component + 2*within-arm variance / runs per cell."""
    result = {}
    for endpoint, observed_sd in stage0["between_cell_paired_sd_log"].items():
        within_sd = stage0["within_run_sd_log"][endpoint]
        if observed_sd is None or within_sd is None:
            result[endpoint] = None
            continue
        between_variance = max(0., observed_sd**2 - 2*within_sd**2/stage0_runs_per_cell)
        result[endpoint] = math.sqrt(between_variance + 2*within_sd**2/runs_per_cell_u)
    return result


def stage0_spread(rows):
    rows = [r for r in rows if r["stage"] == "stage0" and all(r["metrics"].get(k) is not None for k in ("E", "R"))]
    within, between, bootstrap = {}, {}, {}
    for endpoint in ("E", "R"):
        diffs = [math.log(r["runs"][0]["metrics"][endpoint] / r["runs"][1]["metrics"][endpoint])
                 for r in rows if len(r.get("runs", [])) == 2]
        within[endpoint] = math.sqrt(statistics.mean(d*d / 2 for d in diffs)) if diffs else None
        logs = paired_rows(rows, "SH/I", endpoint)[0]
        between[endpoint] = statistics.stdev(logs) if len(logs) >= 2 else None
        if len(logs) >= 2:
            rng = random.Random(f"20260924:{endpoint}")
            draws = [statistics.stdev(rng.choices(logs, k=len(logs))) for _ in range(5000)]
            draws.sort()
            bootstrap[endpoint] = [draws[124], draws[4874]]
        else:
            bootstrap[endpoint] = None
    return {"within_run_sd_log": within, "between_cell_paired_sd_log": between,
            "paired_sd_bootstrap_95pct": bootstrap,
            "paired_block_count": len(paired_rows(rows, "SH/I", "E")[0]),
            "max_stage0_drift_ratio": max((r["metrics"].get("drift_ratio") or 0. for r in rows), default=None),
            "max_stage0_attribution_bound_ratio": max((r["metrics"]["attribution_bound_j"] / r["metrics"]["net_j"]
                                                        for r in rows if r["metrics"].get("attribution_bound_j") is not None
                                                        and r["metrics"].get("net_j")), default=None),
            "D/I_proxy": "SH/I stage0 spread; stage0 contains no D arm",
            "stage0_context": "attended, agents active; drift may be an upper bound, spread is not presumed conservative"}


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
        lines += ["| Block | Arm | Bundle status | Idle-request precheck reasons | Gross J | Idle W mean / SD | Idle cadence s | Energy bound terms J |",
                  "|---|---|---|---|---:|---|---:|---|"]
        for row in stage_rows:
            m = row["metrics"]
            statuses = ", ".join(str(run["status"]) for run in row.get("runs", []))
            reasons = ", ".join(sorted({reason for run in row.get("runs", [])
                                         for reason in run["precheck"].get("reasons", [])}))
            terms = json.dumps(m.get("energy_bound_terms_j"), sort_keys=True)
            lines.append(f"| {row['block']} | {row['context']} | {statuses} | {reasons} | "
                         f"{m.get('gross_energy_j')} | {m.get('idle_power_w_mean')} / {m.get('idle_power_w_stddev')} | "
                         f"{m.get('median_sample_interval_s')} | {terms} |")
        lines.append("")
        lines += ["| Arm | Invalid cells | Mean idle W | Mean edge J/token | Max drift ratio |",
                  "|---|---:|---:|---:|---:|"]
        for arm in sorted({r["context"] for r in stage_rows}):
            arm_rows = [r for r in stage_rows if r["context"] == arm]
            def aggregate(key):
                values = [r["metrics"].get(key) for r in arm_rows]
                values = [v for v in values if isinstance(v, (int, float))]
                return statistics.mean(values) if values else None
            ratios = [r["metrics"].get("drift_ratio") for r in arm_rows]
            ratios = [v for v in ratios if isinstance(v, (int, float))]
            lines.append(f"| {arm} | {sum('bundle_invalid' in r['flags'] for r in arm_rows)} | "
                         f"{aggregate('idle_power_w_mean')} | {aggregate('edge_bound_j_per_token')} | "
                         f"{max(ratios) if ratios else None} |")
        lines.append("")
        if stage in ("U1", "U2"):
            lines += ["| Contrast | Verdict | Ratio 99.375% interval | Widened E interval | Absolute J/token contrast 99.375% interval | Approx. 80% MDE ratio |",
                      "|---|---|---|---|---|---:|"]
            for key, interval in decision["intervals"].items():
                if interval:
                    absolute = interval.get("absolute_interval_j_per_token", "")
                    widened = (f"[{interval['widened_lower_ratio']:.5f}, {interval['widened_upper_ratio']:.5f}]"
                               if interval.get("widened_lower_ratio") is not None else
                               "unbounded" if key.endswith(":E") else "n/a")
                    lines.append(f"| {key} | {decision['verdicts'][key]} | {interval['ratio']:.5f} [{interval['lower_ratio']:.5f}, {interval['upper_ratio']:.5f}] | {widened} | {interval.get('absolute_j_per_token', '')} {absolute} | {interval['approx_80pct_mde_ratio']:.5f} |")
                else:
                    lines.append(f"| {key} | INCONCLUSIVE | unavailable | unavailable | unavailable | unavailable |")
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
        lines += ["", "## Discarded attempts", ""] + [f"- {item['cell']}: {item['reason']}" for item in discarded]
    return "\n".join(lines) + "\n"


def stage_schedules(source: Path) -> dict[Path, dict]:
    """Only a rendered stage, or the registered U1+U2 parent, is analyzable."""
    direct = source / "command_sequence.json"
    if direct.is_file():
        locations = [source]
    elif (source / "U1" / "command_sequence.json").is_file() and (source / "U2" / "command_sequence.json").is_file():
        locations = [source / "U1", source / "U2"]
    else:
        raise ValueError("analysis requires a stage command_sequence.json or a U1+U2 parent")
    schedules = {}
    for location in locations:
        schedule = json.loads((location / "command_sequence.json").read_text())
        stage = schedule.get("stage")
        if stage not in ("stage0", "U1", "U2", "S") or (len(locations) == 2 and stage != location.name):
            raise ValueError(f"invalid stage schedule: {location}")
        actions = {}
        for action in schedule["actions"]:
            key = (action["block"], action["cell_id"])
            if (action.get("stage") != stage or action.get("attempt") != 1 or key in actions or
                Path(action["cell_dir"]).resolve() != (location / f"{action['block']}.{action['cell_id']}.{action['context']}.a1").resolve()):
                raise ValueError(f"invalid scheduled action: {action}")
            actions[key] = action
        schedules[location.resolve()] = {"stage": stage, "actions": actions}
    return schedules


def validate_cell(directory: Path, record: dict, schedules: dict, config: dict, used_bundles: set,
                  *, verify_runs: bool = True) -> dict:
    owner = next((data for root, data in schedules.items() if directory.parent.resolve() == root), None)
    if owner is None:
        raise ValueError("cell is outside a scheduled stage directory")
    match = re.fullmatch(r"(.+)\.(\d+)\.(D|I|SH|B)\.a([1-3])", directory.name)
    if match is None:
        raise ValueError("cell directory does not identify a scheduled attempt")
    block, slot_text, arm, attempt_text = match.groups()
    slot, attempt = int(slot_text), int(attempt_text)
    action = owner["actions"].get((block, slot))
    if action is None or action["context"] != arm:
        raise ValueError("cell is not a scheduled block and slot")
    stage = owner["stage"]
    if (record.get("stage"), record.get("state"), record.get("context"), record.get("cell_id")) != (stage, action["state"], arm, slot):
        raise ValueError("cell record disagrees with scheduled stage, state, slot, or arm")
    if attempt > 1:
        previous = directory.parent / f"{block}.{slot}.{arm}.a{attempt-1}" / "discarded.json"
        if not previous.is_file():
            raise ValueError(f"attempt {attempt} has no discarded predecessor")
        discard = json.loads(previous.read_text())
        if discard.get("block") != block or discard.get("attempt") != attempt-1:
            raise ValueError(f"attempt {attempt} has invalid retry predecessor")
    if not verify_runs:
        return action
    runs = record.get("runs", [])
    if len(runs) != config["runs_per_cell"][stage]:
        raise ValueError("wrong number of production bundles")
    for number, run in enumerate(runs, 1):
        run_id = f"osctx-{stage.lower()}-{block.lower()}-{slot}-{arm.lower()}-r{number}"
        expected_bundle = (directory / "runs" / run_id).resolve()
        expected_config = (directory / f"run-r{number}.json").resolve()
        if run.get("run_id") != run_id or Path(run.get("bundle", "")).resolve() != expected_bundle:
            raise ValueError(f"run r{number} has foreign bundle or run_id")
        if Path(run.get("config", "")).resolve() != expected_config:
            raise ValueError(f"run r{number} has foreign materialized config")
        if not expected_config.is_file() or hashlib.sha256(expected_config.read_bytes()).hexdigest() != run.get("materialized_sha256"):
            raise ValueError(f"run r{number} materialized-config sha256 mismatch")
        if json.loads(expected_config.read_text()).get("run_id") != run_id:
            raise ValueError(f"run r{number} materialized-config run_id mismatch")
        metadata_path = expected_bundle / "metadata.json"
        if not metadata_path.is_file() or json.loads(metadata_path.read_text()).get("run_id") != run_id:
            raise ValueError(f"run r{number} bundle metadata run_id mismatch")
        if expected_bundle in used_bundles:
            raise ValueError(f"duplicate bundle: {expected_bundle}")
        used_bundles.add(expected_bundle)
    return action


def analyze_directory(out: Path, config: dict, *, analyzer_backend=None, output_dir: Path | None = None):
    schedules = stage_schedules(out)
    rows, errors, discarded = [], [], []
    invalid_cell_counts = defaultdict(int)
    used_bundles, seen_cells = set(), set()
    for path in sorted(out.rglob("cell.json")):
        try:
            record = json.loads(path.read_text())
            has_discard = (path.parent / "discarded.json").exists()
            action = validate_cell(path.parent, record, schedules, config, used_bundles,
                                   verify_runs=not has_discard)
            match = re.fullmatch(r"(.+)\.(\d+)\.(D|I|SH|B)\.a([1-3])", path.parent.name)
            key = (record["stage"], match.group(1), int(match.group(2)), int(match.group(4)))
            if key in seen_cells:
                raise ValueError(f"duplicate cell attempt: {key}")
            seen_cells.add(key)
            if has_discard:
                discard = json.loads((path.parent / "discarded.json").read_text())
                discarded.append({"cell": str(path.parent), "reason": discard.get("reason", "unspecified")})
                if discard.get("reason") == "bundle_invalid":
                    invalid_cell_counts[(record["stage"], record["context"])] += 1
                continue
            row = analyzer_backend(path.parent, config) if analyzer_backend else analyze_cell(path.parent, config)
            if action["discard"]:
                discarded.append({"cell": str(path.parent), "reason": "preregistered discard"})
                continue
            rows.append(row)
        except Exception as exc:
            errors.append({"cell": str(path.parent), "error": str(exc)})
    references = {}
    for row in rows:
        if "bundle_invalid" not in row.get("flags", []):
            for request in row.get("requests", []):
                if request.get("output_hash"):
                    references.setdefault(row["stage"], request["output_hash"])
                    break
    for row in rows:
        reference = references.get(row["stage"])
        if reference and any(request.get("output_hash") != reference for request in row.get("requests", [])):
            row["flags"].extend(("output_hash_mismatch", "bundle_invalid"))
            row["metrics"]["E"] = None
            row["metrics"]["R"] = None
    decision = decision_table(rows, config)
    for row in rows:
        if "bundle_invalid" in row.get("flags", []):
            invalid_cell_counts[(row["stage"], row["context"])] += 1
    decision["invalid_cell_counts_by_stage"] = {
        stage: {arm: invalid_cell_counts[(stage, arm)]
                for arm in ("D", "I", "SH", "B")}
        for stage in ("stage0", "U1", "U2", "S")}
    decision["invalid_cell_counts"] = {arm: sum(counts[arm] for counts in decision["invalid_cell_counts_by_stage"].values())
                                       for arm in ("D", "I", "SH", "B")}
    report = {"cells": rows, "errors": errors, "discarded": discarded,
              **decision, "stage_references": references}
    destination = output_dir or out
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "summary.json", report)
    (destination / "summary.md").write_text(markdown(rows, decision, errors, discarded))
    return report


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "power":
        power = argparse.ArgumentParser(prog="analyze.py power")
        power.add_argument("--stage0-summary", type=Path)
        power.add_argument("--sd-e", type=float)
        power.add_argument("--sd-r", type=float)
        power.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
        args = power.parse_args(argv[1:])
        if args.stage0_summary:
            rows = json.loads(args.stage0_summary.read_text())["cells"]
            spread = stage0_spread(rows)
            config = load_config(args.config)
            replication = config["runs_per_cell"]["U1"]
            if config["runs_per_cell"]["U2"] != replication:
                power.error("U1 and U2 must have equal replication for the combined power table")
            u_spread = u_replication_spread(spread, replication, config["runs_per_cell"]["stage0"])
            spread["U_paired_sd_log"] = u_spread
            spread["variance_component_formula"] = "max(0, stage0_paired_sd^2 - 2*within_run_sd^2/stage0_runs_per_cell) + 2*within_run_sd^2/runs_per_cell_U"
            estimates = {contrast: u_spread for contrast in ("D/I", "SH/I")}
            if any(value is None for pair in estimates.values() for value in pair.values()):
                power.error("stage0 needs at least two valid paired blocks")
        elif args.sd_e is not None and args.sd_r is not None:
            estimates = {contrast: {"E": args.sd_e, "R": args.sd_r} for contrast in ("D/I", "SH/I")}
            spread = None
            replication = load_config(args.config)["runs_per_cell"]["U1"]
        else:
            power.error("provide --stage0-summary or both paired SDs")
        size = load_config(args.config)["sizes"]["u_blocks"]
        print(json.dumps({"spread": spread, "table": power_table(estimates, None, (size, size * 2), runs_per_cell_u=replication)}, indent=2))
        return 0
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--out", dest="output_dir", type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    args = parser.parse_args(argv)
    report = analyze_directory(args.out, load_config(args.config), output_dir=args.output_dir)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
