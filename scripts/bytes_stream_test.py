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


def not_defined(reason):
    return f"not defined ({reason})"


def idle_statistics(rows, start_ns, end_ns, stream):
    """Native idle support; polls use arithmetic means, rails clipped intervals.

    Poll rows: stamp_ns, power_w. Rails/GPU rows: start_ns, end_ns, power_w.
    No joint meter/battery series is constructed. All rows are in RAW time.
    """
    from joulewise.idle_dependence import estimate_newey_west_bartlett
    length = (end_ns-start_ns)/1e9
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
    if len(powers) < 2 or not intervals or min(intervals) <= 0:
        return {"reason": stream+" insufficient native samples"}
    cadence_ns = statistics.median(intervals)
    lags = math.floor(10_000_000_000/cadence_ns)
    if length < 30 or len(powers) < 3*(lags+1):
        return {"reason": stream+" support below three 10 s bandwidths"}
    estimate = estimate_newey_west_bartlett(powers, lags, durations)
    mean = (math.fsum(powers)/len(powers) if stream in ("meter","battery") else
            math.fsum(p*d for p,d in zip(powers,durations))/math.fsum(durations))
    return {"mean_w": mean,
            "variance_w2": estimate.governed_variance_of_mean_w2,
            "sample_count": len(powers), "lag_count": lags,
            "native_interval_ns": cadence_ns, "support_durations_s": durations,
            "method": "duration_weighted_newey_west_bartlett_10s_iid_floor_v2"}


def combined_idle(pre, post):
    """Mean of span means; SEs add for meter+battery correlation +1."""
    result = {}
    for stream in ("rails", "gpu", "meter", "battery"):
        a,b = pre[stream],post[stream]
        if "reason" in a or "reason" in b:
            result[stream] = {"reason": a.get("reason", b.get("reason"))}
        else:
            result[stream] = {"pre_w": a["mean_w"], "post_w": b["mean_w"],
                              "se_w": math.sqrt(a["variance_w2"]+b["variance_w2"])/2}
    m,b = result["meter"], result["battery"]
    if "reason" in m or "reason" in b:
        result["dc"] = {"reason": m.get("reason",b.get("reason"))}
    else:
        result["dc"] = {"pre_w": m["pre_w"]+b["pre_w"],
                        "post_w": m["post_w"]+b["post_w"], "se_w": m["se_w"]+b["se_w"]}
    return result


def meter_gap_bound(gaps, *, duration_s, idle_lengths_s, adapter_max_w,
                    adapter_source, battery_max_w, battery_source):
    """§3 R5: missing samples × 20 ms × (adapter rating + battery maximum)."""
    if not adapter_source or not battery_source:
        raise ValueError("gap power sources must be named")
    battery_max_w = max(0, battery_max_w)
    pmax = adapter_max_w+battery_max_w
    terms = []
    for gap in gaps:
        n,span = gap["missing_samples"],gap["span"]
        if type(n) is not int or n < 0 or span not in ("stream", "pre", "post"):
            raise ValueError("gap needs nonnegative integer missing samples and named span")
        weight = 1 if span == "stream" else duration_s/(2*idle_lengths_s[span])
        terms.append({**gap, "missing_s": n*.020, "weight": weight, "bound_j": n*.020*pmax*weight})
    return {"bound_j": math.fsum(t["bound_j"] for t in terms), "terms": terms,
            "P_max_w": pmax, "adapter_max_w": adapter_max_w, "adapter_source": adapter_source,
            "battery_max_w": battery_max_w, "battery_source": battery_source}


def describe_share(rails, dc):
    if dc is None or dc["delta"]-dc["halfwidth"] <= 0:
        return {"f": not_defined("DC contrast not valid"), "df": not_defined("DC contrast not valid")}
    if rails is None:
        return {"f": not_defined("rails contrast missing"), "df": not_defined("rails contrast missing")}
    f = rails["delta"]/dc["delta"]
    return {"f": f, "df": (rails["halfwidth"]+abs(f)*dc["halfwidth"])/abs(dc["delta"])}


def classify(delta, halfwidth, phi, *, reason=None):
    """§4 ordered classes, in J/GB; undefined descriptions do not enter here."""
    if reason:
        return {"class": "UNDETERMINED", "reason": reason}
    if delta+halfwidth < 0:
        return {"class": "UNDETERMINED", "reason": "contrast negative"}
    if delta-halfwidth > 0:
        return {"class": "RESOLVED"}
    epsilon0 = 1e9/(512*39_852_331_520)
    if max(abs(delta-halfwidth),abs(delta+halfwidth))/(1-phi) <= epsilon0:
        return {"class": "BELOW ATTRIBUTION LEVEL"}
    return {"class": "NOT RESOLVED", "upper_limit": (delta+halfwidth)/(1-phi)}


def reduce_boundary(calls, sizes, boundary):
    """§3 excess/dispatch, repeatability, residual and worst-case propagation."""
    arms = {}
    for arm in ("S", "C1", "C3", "C2"):
        rows = [c for c in calls if c["arm"] == arm]
        if len(rows) != 2 or any(boundary not in c["boundaries"] for c in rows):
            return None
        n = sum(c["N"] for c in rows)
        xi = [c["boundaries"][boundary]["excess_j"]/c["N"] for c in rows]
        rep = abs(xi[0]-xi[1])*max(c["N"] for c in rows)/n
        arms[arm] = {"x": sum(c["boundaries"][boundary]["excess_j"] for c in rows)/n,
                     "dx": sum(c["boundaries"][boundary]["bound_j"] for c in rows)/n+rep,
                     "xi": xi, "rep": rep}
    xs,x1,x3,x2 = (arms[a]["x"] for a in ("S","C1","C3","C2"))
    ds,d1,d2 = (arms[a]["dx"] for a in ("S","C1","C2"))
    b,c1,c3,c2 = (sizes[a] for a in ("S","C1","C3","C2"))
    gc = (x2-x1)/(c2-c1)
    alpha = x1-gc*c1
    residual = x3-alpha-gc*c3
    gd = (xs-alpha)/b
    dgc = (d1+d2+abs(residual))/(c2-c1)
    da = d1+abs(residual)+dgc*c1
    delta = (gd-gc)*1e9
    width = ((ds+da+abs(alpha))/b+dgc)*1e9
    eps = width/1e9*(c2-c1)/(1-c1/b)
    return {"delta": delta, "halfwidth": width, "alpha": alpha, "gamma_c": gc*1e9,
            "gamma_d": gd*1e9, "r": residual, "epsilon_flip": eps,
            "epsilon_flip_over_alpha": eps/alpha if alpha else not_defined("alpha is zero"),
            "arms": arms,
            "raw_stream_j_per_byte": sum(c["boundaries"][boundary]["excess_j"] for c in calls if c["arm"]=="S")/
                                      (sum(c["N"] for c in calls if c["arm"]=="S")*b)}


def read_known_bytes(records, scan):
    """Read real receipts plus harvest products; no capture is invented here.

    Harvest supplies pass-1 span integrals/edge bounds, RAW native idle samples,
    capture stack, battery polls, and source-labelled adapter rating. The CLI
    prints this entire result, even when validity or a prerequisite fails.
    """
    sizes = {"S": scan.get("B"), "C1": scan.get("Bc1"), "C3": scan.get("Bc3"), "C2": scan.get("Bc2")}
    output = {"scan": scan, "calls": [], "boundaries": {}, "stack_comparisons": []}
    reasons = []
    if len(records) != 8:
        raise ValueError("the test requires all eight calls")
    if scan.get("K") is not None:
        order = [next((a for a,size in sizes.items() if size == r["receipt"]["bytes_per_read"]), None)
                 for r in records]
        if order != ["S","C1","C3","C2","C2","C3","C1","S"]:
            raise ValueError("records must be the complete stamped palindrome")
        if any(b["receipt"]["start_ns"] <= a["receipt"]["start_ns"] for a,b in zip(records,records[1:])):
            raise ValueError("records must be in stamped call order")
    if scan.get("K") is None:
        reasons.append("knee not found")
    for i, record in enumerate(records, 1):
        receipt,h = record["receipt"],record["harvest"]
        reference,versions = registered_stack()
        check = compare_stack(receipt["stack"], reference, versions, capture_stack=h.get("capture_stack"))
        output["stack_comparisons"].append(check)
        if check["physical_differences"]:
            reasons.append("stack differs in: "+", ".join(check["physical_differences"]))
        # Span integration/idle selection uses the same receipt clock. Long tau
        # trims the start of each idle exactly as §2 prescribes.
        trim_ns = round(max(0,h["tau_s"]-receipt["settle_s"])*1e9)
        spans = {name: (receipt["idle_"+name+"_start_ns"]+trim_ns, receipt["idle_"+name+"_end_ns"])
                 for name in ("pre","post")}
        prepost = {name: {stream: idle_statistics(h["idle"][name].get(stream,[]), *span, stream)
                          for stream in ("rails","gpu","meter","battery")}
                   for name,span in spans.items()}
        idle = combined_idle(prepost["pre"],prepost["post"])
        t = (receipt["end_ns"]-receipt["start_ns"])/1e9
        arm = next((a for a,size in sizes.items() if size == receipt["bytes_per_read"]), None)
        call = {"arm": arm, "N": receipt["repeats"], "T": t, "idle": idle,
                "native_idle": prepost, "boundaries": {}, "receipt": receipt}
        battery = [p for p in h.get("battery_samples",[]) if
                   receipt["idle_pre_start_ns"] <= p["stamp_ns"] < receipt["idle_post_end_ns"]]
        if (not battery or any(not h["idle"][name].get("battery") for name in ("pre","post"))
                or h["energy_j"].get("battery") is None):
            reasons.append(f"battery reading missing in call {i}")
            dc_available = False
        else:
            dc_available = True
        gaps = {"bound_j": 0, "terms": []}
        if h.get("meter_gaps") and dc_available:
            gaps = meter_gap_bound(h["meter_gaps"],duration_s=t,
                idle_lengths_s={name:(end-start)/1e9 for name,(start,end) in spans.items()},
                adapter_max_w=h["adapter_max_w"],adapter_source=h["adapter_source"],
                battery_max_w=max(p["power_w"] for p in battery),battery_source=h["battery_source"])
        call["meter_gaps"] = gaps
        for boundary in ("rails","gpu","dc"):
            if boundary == "dc" and not dc_available:
                continue
            stats = idle[boundary]
            if "reason" in stats:
                # GPU is a separate boundary; missing GPU samples do not veto rails.
                if boundary != "gpu":
                    reasons.append("idle variance not defined ("+stats["reason"]+")")
                continue
            energy = (h["energy_j"]["meter"]+h["energy_j"]["battery"] if boundary=="dc"
                      else h["energy_j"].get(boundary))
            if energy is None:
                continue
            if boundary == "dc":
                edge = sum(h["meter_edge_w"])*(h["r_max_s"]+.020)+sum(h["battery_edge_j"])
                edge += gaps["bound_j"]
            else:
                edge = h["anchor_shift_j"]
            baseline = t*(abs(stats["pre_w"]-stats["post_w"])/2+2*stats["se_w"])
            call["boundaries"][boundary] = {"excess_j": energy-t*(stats["pre_w"]+stats["post_w"])/2,
                                            "bound_j": edge+baseline}
        if all(b in call["boundaries"] for b in ("rails","dc")):
            r,d = (call["boundaries"][b] for b in ("rails","dc"))
            call["boundaries"]["rest"] = {"excess_j": d["excess_j"]-r["excess_j"],
                                            "bound_j": d["bound_j"]+r["bound_j"]}
        call["timing"] = {"r_max_s": h["r_max_s"], "tau_s": h["tau_s"],
                          "operative_timing_bound_s": h.get("operative_timing_bound_s",not_defined("operative timing bound missing"))}
        call["gpu_state"] = h.get("gpu_state",not_defined("GPU frequency/residency missing"))
        call["thermal"] = {"source": "hazards/monitor/thermal.jsonl",
                           "spans": h.get("thermal_spans",not_defined("thermal journal missing"))}
        output["calls"].append(call)
    if scan.get("K") is not None:
        for boundary in ("rails","gpu","dc","rest"):
            output["boundaries"][boundary] = reduce_boundary(output["calls"],sizes,boundary)
    dc = output["boundaries"].get("dc")
    if not reasons and (dc is None or dc["delta"]-dc["halfwidth"] <= 0):
        reasons.append("contrast not resolved")
    output["reasons"] = list(dict.fromkeys(reasons))
    reason = reasons[0] if reasons else None
    for boundary in ("rails","gpu","dc","rest"):
        value = output["boundaries"].get(boundary)
        if value is None:
            output["boundaries"][boundary] = {"class": "UNDETERMINED",
                "reason": reason or "boundary input missing", "description": not_defined(reason or "boundary input missing")}
        else:
            value.update(classify(value["delta"],value["halfwidth"],scan["phi"],reason=reason))
    output["share"] = describe_share(output["boundaries"].get("rails") if
                    "delta" in output["boundaries"]["rails"] else None, dc)
    gpu = [c for c in output["calls"] if c["arm"] in ("S","C2")]
    if len(gpu)==4 and all("gpu" in c["boundaries"] for c in gpu):
        power = {arm:sum(c["boundaries"]["gpu"]["excess_j"] for c in gpu if c["arm"]==arm)/
                     sum(c["T"] for c in gpu if c["arm"]==arm) for arm in ("S","C2")}
        output["gpu_power_contrast_w"] = power["S"]-power["C2"]
    else:
        output["gpu_power_contrast_w"] = not_defined("GPU spans missing")
    output["hour_as_run_s"] = records[0]["harvest"].get("hour_as_run_s",not_defined("session endpoints missing"))
    output["stamped_envelope_s"] = (records[-1]["receipt"]["idle_post_end_ns"]-
                                       records[0]["receipt"]["idle_pre_start_ns"])/1e9
    output["printed"] = printed_record(output)
    return output


def format_interval(value, halfwidth):
    """§14 H2: two significant half-width digits; estimate at the same place."""
    if halfwidth == 0:
        return f"{value} ± 0"
    rounded = float(format(halfwidth, ".2g"))
    places = 1-math.floor(math.log10(rounded))
    return f"{round(value,places):.{max(0,places)}f} ± {round(halfwidth,places):.{max(0,places)}f}"


def printed_record(result):
    """Claim-side sentences and test-record descriptions; full numeric input stays above."""
    printed = {"claim_lines": {}, "contrasts": {}, "share": result["share"],
               "stack_comparisons": result["stack_comparisons"]}
    for boundary,value in result["boundaries"].items():
        interval = format_interval(value["delta"],value["halfwidth"]) if "delta" in value else value["description"]
        printed["contrasts"][boundary] = interval
        if boundary not in ("rails","rest") or value["class"] == "RESOLVED":
            continue
        if value["class"] == "UNDETERMINED":
            line = f"Known-bytes check: {boundary} memory-traffic attribution is undetermined ({value['reason']})."
        elif value["class"] == "BELOW ATTRIBUTION LEVEL":
            line = (f"Known-bytes check: {boundary} energy per DRAM-sourced byte differed from cache-sourced by {interval} J/GB "
                    f"(DRAM minus cache), within the 1 J-per-run attribution level ({1e9/(512*39_852_331_520):.4g} J/GB); "
                    f"{boundary} lines here carry no resolvable memory-traffic energy.")
        else:
            # The upper limit uses the estimate's printed decimal place.
            digits = max(0,1-math.floor(math.log10(value["halfwidth"])))
            line = (f"Known-bytes check: the {boundary} response to DRAM-sourced bytes is not resolved ({interval} J/GB, "
                    f"cache-bias-corrected upper limit {value['upper_limit']:.{digits}f} J/GB); "
                    f"whether {boundary} lines include memory-traffic energy is not established.")
        printed["claim_lines"][boundary] = line
    if isinstance(result["share"]["f"],(float,int)):
        printed["share"] = format_interval(result["share"]["f"],result["share"]["df"])
    return printed


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

    if settle_s:
        sleep(settle_s)
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
    if argv and argv[0] == "read":
        parser = argparse.ArgumentParser(description="Read §3/§4 receipts and native harvest products")
        parser.add_argument("input", type=Path, help="JSON object with scan and records")
        args = parser.parse_args(argv[1:])
        data = json.loads(args.input.read_text())
        print(json.dumps(read_known_bytes(data["records"], data["scan"]), allow_nan=False, indent=2))
        return 0
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
