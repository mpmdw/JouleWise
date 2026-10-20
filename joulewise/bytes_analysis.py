"""BYTES R3/R5 desk analysis. No runtime or measurement entry points.

Artifacts are analysis records, not Block-5 paper-custody capabilities.
"""
from __future__ import annotations

import bisect
import csv
import hashlib
import itertools
import json
import math
import re
import statistics
from pathlib import Path

from joulewise.analysis_engine.distributions import student_t_quantile

BOUNDARIES = ("rails", "DC input", "rest")
HYPOTHESES = ("bytes", "resident", "time")
DECODE_STEPS = 512
OUTPUT_LABEL = "512 decode forward passes, one of which yields no returned token"
H1_CHECKS = 21
# Addendum 4: separate primary families on each boundary.
H2_INTERVALS = {"rails": 9, "DC input": 9, "rest": 11}
SCHEMA = "joulewise.bytes_predictions.v1"
BOUND_KINDS = ("E_clock_anchor_shift_bound_j", "E_interpolation_joint_edge_bound_j",
               "E_whole_window_drift_allowance_j")


class AnalysisError(ValueError):
    """A member, cell or stage cannot support the requested calculation."""


def number(value, label="number", *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise AnalysisError(f"{label}: finite number required")
    if (positive and value <= 0) or (nonnegative and value < 0):
        raise AnalysisError(f"{label}: invalid sign")
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def line(xs, ys):
    """Intercept and slope of an OLS line, with centered arithmetic."""
    if len(xs) != len(ys) or len(xs) < 2:
        raise AnalysisError("line needs matching observations")
    xs, ys = [number(x) for x in xs], [number(y) for y in ys]
    xbar, ybar = statistics.fmean(xs), statistics.fmean(ys)
    xx = math.fsum((x - xbar) ** 2 for x in xs)
    if xx == 0:
        raise AnalysisError("singular line")
    slope = math.fsum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / xx
    return [ybar - slope * xbar, slope]


def predict(coefficients, x):
    return coefficients[0] + coefficients[1] * x


def freeze_lines(points):
    if len(points) != 3:
        raise AnalysisError("H1 requires exactly three fit models")
    result = {}
    for hypothesis in HYPOTHESES:
        xs = [p[hypothesis] for p in points]
        result[hypothesis] = {
            "line": line(xs, [p["e"] for p in points]),
            "corners": [line(xs, ys) for ys in itertools.product(
                *[(p["lower"], p["upper"]) for p in points])],
        }
    return result


def h1_point(frozen, point):
    checks = []
    for hypothesis in HYPOTHESES:
        item = frozen[hypothesis]
        predicted = predict(item["line"], point[hypothesis])
        corners = [predict(c, point[hypothesis]) for c in item["corners"]]
        lower, upper = min(corners), max(corners)
        consistent = point["lower"] <= upper and lower <= point["upper"]
        checks.append({"hypothesis": hypothesis, "predicted": predicted,
                       "prediction_lower": lower, "prediction_upper": upper,
                       "measured": point["e"], "measured_lower": point["lower"],
                       "measured_upper": point["upper"], "consistent": consistent,
                       "log_ratio": math.log(point["e"] / predicted)
                       if point["e"] > 0 and predicted > 0 else None,
                       "log_status": "computed" if point["e"] > 0 and predicted > 0
                       else "undefined_nonpositive"})
    matches = [c["hypothesis"] for c in checks if c["consistent"]]
    word = matches[0] if len(matches) == 1 else "unresolved" if matches else "neither"
    return {"word": word, "checks": checks}


def active_or_resident(results):
    if len(results) != 3:
        raise AnalysisError("active or resident requires all three MoE models")
    misses = []
    for model, result in results:
        checks = {c["hypothesis"]: c for c in result["checks"]}
        r, b = checks["resident"], checks["bytes"]
        misses.append({"model": model,
                       "resident_above": not r["consistent"] and r["prediction_lower"] > r["measured_upper"],
                       "bytes_below": not b["consistent"] and b["prediction_upper"] < b["measured_lower"]})
    word = "active" if all(m["resident_above"] for m in misses) else (
        "resident" if all(m["bytes_below"] for m in misses) else "mixed")
    return {"answer": word, "misses": misses}


def _inverse(matrix):
    n = len(matrix)
    a = [list(row) + [float(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        if abs(a[pivot][j]) < 1e-12:
            raise AnalysisError("singular H2 design")
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        a[j] = [x / scale for x in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [x - scale * y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def ols(predictors, response, *, family_size=9):
    """OLS point estimates; primary HC3 and labelled OLS Student-t intervals."""
    n, p = len(response), len(predictors[0]) + 1
    if n <= p or len(predictors) != n or any(len(row) != p - 1 for row in predictors):
        raise AnalysisError("H2 insufficient or ragged design")
    raw = [[number(v) for v in row] for row in predictors]
    y = [number(v) for v in response]
    means = [statistics.fmean(row[j] for row in raw) for j in range(p - 1)]
    scales = [math.sqrt(math.fsum((row[j] - means[j]) ** 2 for row in raw) / n)
              for j in range(p - 1)]
    if any(s == 0 for s in scales):
        raise AnalysisError("singular H2 design")
    design = [[1.0] + [(v - m) / s for v, m, s in zip(row, means, scales)] for row in raw]
    gram = [[math.fsum(row[i] * row[j] for row in design) for j in range(p)] for i in range(p)]
    inv = _inverse(gram)
    xy = [math.fsum(row[i] * v for row, v in zip(design, y)) for i in range(p)]
    beta = [math.fsum(a * b for a, b in zip(row, xy)) for row in inv]
    residual = [v - math.fsum(a * b for a, b in zip(row, beta)) for row, v in zip(design, y)]
    mse = math.fsum(r * r for r in residual) / (n - p)
    transform = [[1.0] + [-m / s for m, s in zip(means, scales)]]
    transform += [[0.0] + [1 / scales[i] if i == j else 0.0 for j in range(p - 1)]
                  for i in range(p - 1)]
    coefficients = [math.fsum(a * b for a, b in zip(row, beta)) for row in transform]
    ols_scaled = [[mse * v for v in row] for row in inv]
    # HC3 sandwich: sum_i (X'X)^-1 x_i x_i' (X'X)^-1 * (r_i/(1-h_ii))^2.
    influence = [[math.fsum(a * b for a, b in zip(row, x)) for row in inv]
                 for x in design]
    leverage = [math.fsum(a * b for a, b in zip(x, v)) for x, v in zip(design, influence)]
    if any(1 - h <= 1e-12 for h in leverage):
        raise AnalysisError("HC3 undefined at unit leverage")
    hc3_scaled = [[math.fsum(v[i] * v[j] * (r / (1 - h)) ** 2
                              for v, r, h in zip(influence, residual, leverage))
                   for j in range(p)] for i in range(p)]

    def transformed(cov):
        return [[math.fsum(transform[i][k] * cov[k][l] * transform[j][l]
                           for k in range(p) for l in range(p))
                 for j in range(p)] for i in range(p)]

    covariance, ols_covariance = transformed(hc3_scaled), transformed(ols_scaled)
    critical = student_t_quantile(1 - .05 / (2 * family_size), n - p)
    se = [math.sqrt(max(0.0, covariance[i][i])) for i in range(p)]
    ols_se = [math.sqrt(max(0.0, ols_covariance[i][i])) for i in range(p)]
    return {"n": n, "df": n - p, "coefficients": coefficients, "covariance": covariance,
            "se_method": "HC3", "standard_errors": se,
            "ols_covariance": ols_covariance, "ols_standard_errors": ols_se,
            "ols_intervals": [[v - critical * e, v + critical * e] for v, e in zip(coefficients, ols_se)],
            "mse": mse, "critical": critical, "family_size": family_size,
            "intervals": [[v - critical * e, v + critical * e] for v, e in zip(coefficients, se)]}


def deviation(fit, predictors, observed, measured_half_w=0.0):
    x = [1.0, *predictors]
    fitted = math.fsum(a * b for a, b in zip(x, fit["coefficients"]))
    variance = fit["mse"] + math.fsum(x[i] * fit["covariance"][i][j] * x[j]
                                      for i in range(len(x)) for j in range(len(x)))
    prediction_half = fit["critical"] * math.sqrt(max(0.0, variance))
    own = number(measured_half_w, "measured power half-width", nonnegative=True)
    half = prediction_half + own
    delta = observed - fitted
    return {"deviation_w": delta, "lower_w": delta - half, "upper_w": delta + half,
            "prediction_half_w": prediction_half, "measured_half_w": own, "predicted_w": fitted}


def _point_label(point):
    return {k: point[k] for k in ("model", "pass_status", "n_passes") if k in point}


def h2(points, rails_power, *, boundary=None, family_size=None):
    """Fit each available design separately; refused fits contribute no primary interval."""
    boundary = boundary or points[0]["boundary"]

    def attempt(rows, predictors):
        n, p = len(rows), len(predictors) + 1
        refused = {"status": "refused", "n": n, "p": p, "df": n - p,
                   "point_labels": [_point_label(row) for row in rows]}
        if n - p < 2:
            return {**refused, "reason": "n - p < 2"}
        try:
            fit = ols([[f(row) for f in predictors] for row in rows],
                      [row["power"] for row in rows], family_size=1)
        except AnalysisError as exc:
            return {**refused, "reason": str(exc)}
        return {**fit, "status": "computed", "p": p, "point_labels": refused["point_labels"]}

    bw, resident_rate = lambda p: p["BW"], lambda p: p["resident"] / p["time"]
    two = attempt(points, [bw])
    extended = attempt(points, [bw, resident_rate])
    tier_points = [p for p in points if p["tier"]]
    tier = attempt(tier_points, [bw, resident_rate])
    rest_points = [p for p in points if p["model"] in rails_power]
    rest = attempt(rest_points, [bw, lambda p: rails_power[p["model"]]]) if boundary == "rest" else None
    specs = [("epsilon", two, 1), ("extended_epsilon", extended, 1),
             ("rho", extended, 2), ("tier_epsilon", tier, 1), ("tier_rho", tier, 2)]
    if rest is not None:
        specs += [("rest_epsilon", rest, 1), ("lambda", rest, 2)]
    outside_points = [p for p in points if not p["tier"]]
    tier_ok = tier["status"] == "computed"
    k = sum(fit["status"] == "computed" for _, fit, _ in specs) + (len(outside_points) if tier_ok else 0)
    family = k if family_size is None else family_size
    for fit in (two, extended, tier, rest):
        if fit is None or fit["status"] != "computed":
            continue
        critical = student_t_quantile(1 - .05 / (2 * max(1, family)), fit["df"])
        fit.update(critical=critical, family_size=family)
        for key, errors in (("intervals", "standard_errors"), ("ols_intervals", "ols_standard_errors")):
            fit[key] = [[v - critical * e, v + critical * e]
                        for v, e in zip(fit["coefficients"], fit[errors])]
    outside = [{**_point_label(p), "status": "computed", **deviation(tier,
                [bw(p), resident_rate(p)], p["power"], p.get("power_half_w",
                (p.get("h_j", 0.0) + p.get("B_j", 0.0)) / p.get("duration_s", 1.0)))}
               if tier_ok else {**_point_label(p), "status": "refused", "reason": "tier fit refused"}
               for p in outside_points]
    if rest is not None and rest["status"] == "computed":
        corr = statistics.correlation([bw(p) for p in rest_points], [rails_power[p["model"]] for p in rest_points])
        rest.update(vif=1 / (1 - corr * corr) if abs(corr) < 1 else None,
                    vif_status="computed" if abs(corr) < 1 else "infinite", correlation=corr)
    loo = []
    for i, point in enumerate(points):
        fit = attempt(points[:i] + points[i + 1:], [bw])
        loo.append({**_point_label(point), "observed_w": point["power"], "status": fit["status"],
                    **({"predicted_w": predict(fit["coefficients"], bw(point))} if fit["status"] == "computed"
                       else {"reason": fit["reason"]})})
    primary = [{"term": name, "estimate": fit["coefficients"][index],
                "lower": fit["intervals"][index][0], "upper": fit["intervals"][index][1],
                "HC3_se": fit["standard_errors"][index], "OLS_se": fit["ols_standard_errors"][index]}
               for name, fit, index in specs[:5] if fit["status"] == "computed"]
    primary += [{"term": "tier_deviation:" + row["model"], **_point_label(row),
                 "estimate": row["deviation_w"], "lower": row["lower_w"], "upper": row["upper_w"]}
                for row in outside if row["status"] == "computed"]
    primary += [{"term": name, "estimate": fit["coefficients"][index],
                 "lower": fit["intervals"][index][0], "upper": fit["intervals"][index][1],
                 "HC3_se": fit["standard_errors"][index], "OLS_se": fit["ols_standard_errors"][index]}
                for name, fit, index in specs[5:] if fit["status"] == "computed"]
    adds_nothing = None
    if extended["status"] == "computed":
        rho = extended["coefficients"][2]
        lo, hi = extended["intervals"][2]
        adds_nothing = lo <= 0 <= hi or rho <= 0
    return {"n": len(points), "k": family, "point_labels": [_point_label(p) for p in points],
            "primary_intervals": primary, "two_term": two, "resident_extended": extended,
            "resident_adds_nothing": adds_nothing, "tier": tier, "tier_deviations": outside,
            "rest": rest, "loo_description": loo}


def validate_manifest(manifest):
    models = manifest["models"]
    if len(models) != 10 or len({m["model"] for m in models}) != 10:
        raise AnalysisError("manifest requires ten distinct models")
    if sum(m["role"] == "fit" for m in models) != 3 or sum(bool(m["moe"]) for m in models) != 3:
        raise AnalysisError("manifest requires three fit and three MoE models")
    if sum(bool(m["tier"]) for m in models) != 6:
        raise AnalysisError("manifest requires six Qwen3 4-bit tier models")
    cells = []
    for model in models:
        if model["role"] not in ("fit", "heldout") or (model["moe"] and model["role"] == "fit"):
            raise AnalysisError("invalid model role")
        for key in ("W_bytes", "KV_bytes", "R_bytes"):
            number(model[key], key, nonnegative=True)
        number(model["W_bytes"] + model["KV_bytes"], "bytes", positive=True)
        number(model["R_bytes"], "resident", positive=True)
        cells += model["cell_ids"]
    if len(cells) != len(set(cells)):
        raise AnalysisError("manifest cell ids overlap")
    return manifest


def _event_span(events, phase, metadata):
    stamps = metadata["uncertainty_evidence"]["clock_anchor"]["clock_stamps"]
    anchor = stamps["sampling_started"]
    def mapped(event):
        # Runtime phase events are wall stamps; controller stage markers may carry monotonic_ns.
        own = event.get("metadata", {}).get("monotonic_ns")
        return own if type(own) is int else round((anchor["monotonic_before_s"] +
                                                   event["timestamp_s"] - anchor["epoch_s"]) * 1e9)
    starts = [e for e in events if e.get("phase") == phase and e["event_type"] in ("phase_start", "stage_started")]
    ends = [e for e in events if e.get("phase") == phase and e["event_type"] in ("phase_end", "stage_completed")]
    if len(starts) != 1 or len(ends) != 1:
        raise AnalysisError(f"one complete {phase} span required")
    span = [mapped(starts[0]), mapped(ends[0])]
    if span[1] <= span[0]:
        raise AnalysisError("nonpositive phase duration")
    return span


def meter_decode(stream, decode_span, idle_span):
    """R3 DC input integration and the 2026-10-15 phase-edge ruling.

    Each edge takes the larger of its two adjacent sample powers, including
    the in-phase sample at an exactly aligned end. The bound covers both bases.
    It is an attribution bound, not a physical-energy confidence statement.
    """
    from joulewise.external import km003c_parse as kp
    offset = kp.raw_offset_ns(stream)
    if stream.fit is None or not stream.aligned or offset is None:
        raise AnalysisError("meter clock fit or raw/monotonic mapping unavailable" +
                            (": " + stream.fit_error if stream.fit_error else ""))
    spans = [[edge + offset for edge in span] for span in (decode_span, idle_span)]
    if any(span[0] < stream.host_ns[0] or span[1] > stream.host_ns[-1] or
           span[1] <= span[0] for span in spans):
        raise AnalysisError("meter does not cover decode and own idle spans")
    duration = (spans[0][1] - spans[0][0]) / 1e9
    idle_duration = (spans[1][1] - spans[1][0]) / 1e9
    gross, n = kp.integrate(stream.host_ns, stream.watts, *spans[0])
    base, nb = kp.integrate(stream.host_ns, stream.watts, *spans[1])
    if gross is None or base is None:
        raise AnalysisError("meter span has no samples")
    stats = stream.fit.stats
    residual = max(abs(number(stats[key], key)) for key in
                   ("excess_latency_ms_min", "excess_latency_ms_max")) / 1000
    interval = number(stream.samples.step_ms, "meter sample interval", positive=True) / 1000
    powers = []
    for edge in spans[0]:
        right = bisect.bisect_left(stream.host_ns, edge)
        adjacent = [i for i in (right - 1, right) if 0 <= i < len(stream.host_ns)]
        powers.append(max(number(stream.watts[i], "meter edge power", nonnegative=True) for i in adjacent))
    u = math.fsum(powers) * (residual + interval)
    return {"gross_j": gross, "secondary_j": gross - base / idle_duration * duration,
            "idle_power_w": base / idle_duration, "phase_edge_j": u,
            "edge_powers_w": powers, "r_max_s": residual, "sample_interval_s": interval,
            "n": n, "n_idle": nb, "clock_fit": stats}


def operative_summary(bundle, acceptance, *, synthetic=False, stored=None, physics_cache=None):
    """Consume B6's evaluated own-session bound; never recompute a bracket.

    B6 calibration.evaluate owns max(pre,post)+max(drift,screen). The existing
    output-free reducer seam owns re-derivation and rejects narrowed bounds.
    """
    from joulewise.reduce import _rederive_summary_for_authenticated_fiducial_bound
    cal = acceptance.get("calibration") or {}
    value = cal.get("operative_bound_s")
    if value is None or isinstance(value, bool):
        raise AnalysisError("operative-bracket join missing: b6-acceptance.calibration.operative_bound_s")
    bound = number(float(value), "harvest operative bound", nonnegative=True)
    summary = _rederive_summary_for_authenticated_fiducial_bound(
        bundle, authenticated_fiducial_bound_s=bound,
        _instrument_calibration_physics_cache=physics_cache)
    envelope = (summary.get("energy_anchor_shift_envelopes") or {}).get("/phase_energy_j/decode")
    # Mock telemetry has no native interval support, mint calibration, or
    # operative edge envelope. Only explicitly labelled simulation fixtures
    # may supply a timing bound; never treat that as live join validation.
    if synthetic and (stored or {}).get("bytes_synthetic_timing_fixture") is True:
        return stored, {"operative_bound_s": bound, "status": "synthetic_timing_fixture",
                        "missing": ["native powermetrics interval-support trace",
                                    "member instrument-calibration primary evidence",
                                    "operative decode envelope from that evidence"]}
    if summary.get("status") != "succeeded" or envelope is None:
        raise AnalysisError("operative-bracket re-reduction has no decode envelope; "
                            "requires native trace, clock stamps and valid member instrument calibration: " +
                            str(summary.get("failure_message") or summary.get("energy_uncertainty_status")))
    return summary, {"operative_bound_s": bound, "status": "rereduced"}


def _filtered_stream(path, spans):
    """Fit the clock from timing only; decode power only in selected run spans.

    The JSONL transport must be scanned, but payloads outside these spans are
    never unpacked into power samples or retained. Batch endpoint *sequence
    numbers* alone provide the same clock-fit points as the native parser.
    One sample on either side is retained for the ruled edge bound.
    """
    from joulewise.external import km003c_parse as kp
    header = trailer = None
    batches, newest, positions = [], [], []
    previous_seq = previous_rx = None
    current = 0
    payload_re = re.compile(r'"p"\s*:\s*"([0-9a-fA-F]*)"')
    with Path(path).open() as handle:
        for raw in handle:
            match = payload_re.search(raw)
            # Parse transport/timing without materializing the payload as JSON.
            item = json.loads(raw[:match.start(1)] + raw[match.end(1):] if match else raw)
            if item.get("k") == "h":
                header = item
            elif item.get("k") == "t":
                trailer = item
            elif item.get("k") == "b" and item.get("n") and match:
                payload = match.group(1)
                seq = int.from_bytes(bytes.fromhex(payload[-kp.SAMPLE.size * 2:][:4]), "little")
                if previous_seq is None:
                    first = int.from_bytes(bytes.fromhex(payload[:4]), "little")
                    current = (seq - first) % kp.WRAP
                else:
                    delta = ((seq - previous_seq + kp.WRAP // 2) % kp.WRAP) - kp.WRAP // 2
                    elapsed = (item["rx"] - previous_rx) / 1e6
                    if elapsed > kp.WRAP // 2:
                        delta += round((elapsed - delta) / kp.WRAP) * kp.WRAP
                    current += delta
                previous_seq, previous_rx = seq, item["rx"]
                newest.append(current)
                positions.append((seq, current))
                batches.append(item)
    if header is None or header.get("status", "streaming") != "streaming" or not batches:
        return kp.Stream(header, trailer, [], [], None, None, [], [], [], [])
    step = kp.STEP_MS[header["rate_idx"]]
    clock_samples = kp.Samples(newest, [], [], list(range(len(batches))), 0, step)
    try:
        fit = kp.clock_fit(clock_samples, batches)
    except ValueError as exc:
        return kp.Stream(header, trailer, [], [], None, None, [], [], [], [], str(exc))
    shell = kp.Stream(header, trailer, [], [], None, fit, [], [], [], [])
    offset = kp.raw_offset_ns(shell)
    if offset is None:
        return shell
    # Sorted disjoint time ranges permit O(log n) selection per sample.
    ranges = sorted((a + offset - step * 1_000_000, b + offset + step * 1_000_000) for a, b in spans)
    merged = []
    for a, b in ranges:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(b, merged[-1][1])
        else:
            merged.append([a, b])
    starts = [a for a, _ in merged]
    def selected(t):
        i = bisect.bisect_right(starts, t) - 1
        return i >= 0 and t <= merged[i][1]
    host, watts, devs = [], [], []
    index = 0
    with Path(path).open() as handle:
        for raw in handle:
            match = payload_re.search(raw)
            if not match:
                continue
            # First pass already established batch metadata and clock position.
            if index >= len(batches):
                break
            meta = json.loads(raw[:match.start(1)] + raw[match.end(1):])
            if meta.get("k") != "b" or not meta.get("n"):
                continue
            seq_last, dev_last = positions[index]
            index += 1
            payload = match.group(1)
            for pos in range(0, len(payload), kp.SAMPLE.size * 2):
                word = payload[pos:pos + kp.SAMPLE.size * 2]
                seq = int.from_bytes(bytes.fromhex(word[:4]), "little")
                dev = dev_last + ((seq - seq_last + kp.WRAP // 2) % kp.WRAP) - kp.WRAP // 2
                stamp = fit.host_ns(dev)
                if not selected(stamp) or (host and stamp <= host[-1]):
                    continue
                fields = kp.SAMPLE.unpack(bytes.fromhex(word))
                host.append(stamp)
                watts.append(fields[2] / 1e6 * fields[3] / 1e6)
                devs.append(dev)
    samples = kp.Samples(devs, [], [], [], 0, step)
    return kp.Stream(header, trailer, [], [], samples, fit, host, watts, [], [])


def _session_streams(root, spans):
    from joulewise.external import km003c_parse as kp
    directory = root / "sources/night-custody/hazards/meter"
    streams = []
    for path in sorted(directory.glob("stream-*.jsonl")):
        try:
            stream = _filtered_stream(path, spans)
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError) as exc:
            stream = kp.Stream(None, None, [], [], None, None, [], [], [], [], str(exc))
        streams.append((path.name, stream))
    return streams


# These exclusions establish absence or invalidity of the energy record.
# Other catalog exclusions, including NUMBER cooldown/idle/envelope flags,
# can be restored if the record itself passes the checks below.
INVALID_RECORD_CODES = frozenset({"member.bytes_missing", "member.bytes_ambiguous", "member.unreadable",
    "member.status_not_succeeded", "member.strict_validation_failed", "member.token_count_mismatch"})
REFERENCE_ROLES = ("corpus", "start", "midpoint", "end")


def _export_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _stage_export_rows(path, *, include_withheld=False):
    """Only a post-commit stage opens the group's already blinded store.

    A missing store is a recorded flag. Never recover its science rows from
    reductions or bundles: absence must remain visible to the model reducer.
    """
    path = Path(path)
    rows = _export_rows(path) if path.is_file() else []
    if not include_withheld:
        return rows, False
    sidecar = path.with_name(path.name.removesuffix(".runs.csv") + ".session.json")
    if not sidecar.is_file():
        return rows, False  # legacy exports contain all their science rows
    info = read_json(sidecar).get("blinding", {}).get("withheld")
    if info is None:
        return rows, False
    if not path.is_file():
        return rows, info
    try:
        merged = rows + _export_rows(path.parent / info["path"])
        return sorted(merged, key=lambda row: int(row["order_index"])), False
    except FileNotFoundError:
        return rows, info


def _withheld_counts(info, model):
    key_digest = hashlib.sha256(model.get("config_key", "").encode("utf-8")).hexdigest()
    count = info["config_key_sha256"].get(key_digest, 0) if info else 0
    return {"withheld_row_count": info["row_count"], "withheld_config_row_count": count} if count else {}


def _missing_withheld_records(info, manifest, session):
    """Census-only placeholders; no archive, key, energy or substitute reduction."""
    for model in manifest["models"]:
        counts = _withheld_counts(info, model)
        for index in range(counts.get("withheld_config_row_count", 0)):
            yield {"model": model["model"], "pass_id": session["pass_id"],
                "session_id": session["session_id"],
                "run_id": "withheld-missing:" + model["config_key"] + ":" + str(index),
                "stratum": "repeat" if index < 10 else "quad",
                "unit_id": str(index if index < 10 else (index - 10) // 4),
                "status": "unusable", "invalid_energy_record": True,
                "excluded": False, "harvest_excluded": False, "meter": None,
                "flags": ["bytes.withheld_missing"], **counts}


def _released_rows(rows, key_dir, *, blinded):
    from joulewise.b6 import blinding
    result = []
    for row in rows:
        if blinded:
            result.append(row)
            continue
        if (row.get("status") != "succeeded" or not row.get("model_name") or
                set(row.get("exclusion_codes", "").split(";")) & INVALID_RECORD_CODES):
            result.append(row)
            continue
        if key_dir is None:
            raise AnalysisError("released key directory required before meter join")
        # Presence of both files in the supplied release directory is authority.
        # Never draw keys, inspect the export's private key_dir, or trust synthetic.
        try:
            factor = blinding.stored_factor(key_dir, row["config_key"])
        except ValueError as exc:
            raise AnalysisError("configuration still blinded: " + row["config_key"]) from exc
        result.append(row if row.get("non_claim", "").lower() == "true" else blinding.unblind(row, factor))
    return result


def neg8_inputs(rows, *, streams=(), spans=None, test7_passed=False, blinded=False):
    """Recompute the two NEG-8 family allowances from native export rows.

    Block-5's owning count-adjusted bound supplies repeatability; allowance is
    max(bound, spread of start/midpoint/end means), separately for each family.
    Rails reference energies come from the export, never withheld summaries.
    DC/rest whole-request references use the authorized meter join.
    """
    from joulewise.whole_window import neg8_count_adjusted_bound
    kept = [r for r in rows if r["role"] in REFERENCE_ROLES and r.get("config_key") == "neg8_reference"
            and r.get("status") == "succeeded"
            and str(r.get("excluded", "")).lower() != "true"]
    values = []
    for row in kept:
        try:
            gross = number(float(row["gross_energy_j"]), "NEG-8 gross")
            secondary = number(float(row["idle_subtracted_energy_j"]), "NEG-8 secondary")
            duration = math.fsum(float(row.get("dur_" + phase + "_s") or 0)
                                 for phase in ("tokenize", "generation_setup", "prefill", "decode"))
            number(duration, "NEG-8 whole-request duration", positive=True)
        except (ValueError, TypeError, KeyError):
            continue
        item = {"run_id": row["run_id"], "role": row["role"], "duration_s": duration,
                "rails": {"gross": gross, "idle_subtracted": secondary}}
        if not blinded and spans and row["run_id"] in spans:
            request, idle = spans[row["run_id"]]
            # Events give the complete request duration, including phase gaps.
            item["duration_s"] = (request[1] - request[0]) / 1e9
            for _, stream in streams:
                try:
                    dc = meter_decode(stream, request, idle)
                except AnalysisError:
                    continue
                item["DC input"] = {"gross": dc["gross_j"], "idle_subtracted": dc["secondary_j"]}
                item["rest"] = {family: item["DC input"][family] - item["rails"][family]
                                for family in ("gross", "idle_subtracted")}
                break
        values.append(item)
    result = {"test7_passed": test7_passed, "references": values, "boundaries": {}}
    for boundary in (("rails",) if blinded else BOUNDARIES):
        available = [r for r in values if boundary in r]
        slots = {slot: [r for r in available if r["role"] == slot] for slot in REFERENCE_ROLES}
        # B6's registered corpus minimum/cap and survivor endpoint minimum.
        corpus = slots["corpus"][:12]
        if len(corpus) < 6 or min(len(slots["start"]), len(slots["end"])) < 2:
            continue
        references = slots["start"] + slots["midpoint"] + slots["end"]
        families = {}
        for family in ("gross", "idle_subtracted"):
            bound = neg8_count_adjusted_bound([r[boundary][family] for r in corpus],
                                            len(slots["start"]), len(slots["end"]))
            means = {slot: statistics.fmean(r[boundary][family] for r in slots[slot])
                     for slot in ("start", "midpoint", "end") if slots[slot]}
            if bound is None:
                continue
            families[family] = {"means_j": means, "bound_terms": bound,
                "allowance_j": max(bound["bound_j"], max(means.values()) - min(means.values()))}
        result["boundaries"][boundary] = {"families": families,
            "energy_j": statistics.fmean(r[boundary]["gross"] for r in references),
            "duration_s": statistics.fmean(r["duration_s"] for r in references),
            "reference_run_ids": [r["run_id"] for r in references],
            "corpus_run_ids": [r["run_id"] for r in corpus]}
    return result


def _record_base(model, session, session_id, member, exclusions, flags, window_flags):
    unit = next(u for u in member["units"] if u["cell_id"] in model["cell_ids"])
    codes = exclusions.get(member["run_id"], set())
    return {"model": model["model"], "pass_id": session["pass_id"], "session_id": session_id,
        "run_id": member["run_id"], "stratum": unit["stratum"], "unit_id": str(unit["unit_id"]),
        "excluded": bool(codes), "harvest_excluded": bool(codes),
        "invalid_energy_record": bool(codes & INVALID_RECORD_CODES),
        "flags": sorted(flags.get(member["run_id"], set()) | window_flags | codes),
        "status": "unusable", "meter": None}


def archive_records(root, manifest, session, *, stage, export_path=None, key_dir=None):
    """A bad member yields an unusable record; only its whole unit is removed."""
    if stage == "blinded":
        raise AnalysisError("blinded stage requires export ingress")
    from joulewise.b6.archive import bundle_of
    root = Path(root)
    roster = read_json(root / "derived/roster.json")
    acceptance = read_json(root / "derived/b6-acceptance.json")
    if acceptance.get("counting") is not True:
        raise AnalysisError("session is not a counting accepted attempt")
    selected = {cell: m for m in manifest["models"] for cell in m["cell_ids"]
                if stage in ("all", "blinded") or m["role"] == stage}
    exclusions, flags, window_flags = {}, {}, set()
    for e in acceptance.get("excluding", []):
        if e.get("scope") == "member":
            exclusions.setdefault(e["run_id"], set()).add(e["code"])
    flag_rows = [json.loads(raw) for raw in (root / "derived/flags.jsonl").read_text().splitlines() if raw.strip()]
    for flag in flag_rows + acceptance.get("emitted_flags", []):
        scope = flag.get("scope") or {}
        if scope.get("run_id"):
            flags.setdefault(scope["run_id"], set()).add(flag["code"])
        else:
            window_flags.add(flag["code"])
    export_path = export_path or root.parent / "export" / "bytes" / (acceptance["session_id"] + ".runs.csv")
    exports, withheld_missing = _stage_export_rows(export_path, include_withheld=stage in ("heldout", "all"))
    wanted_ids = {m["run_id"] for m in roster["members"]
                  if any(u["cell_id"] in selected for u in m.get("units", []))}
    selected_exports = [r for r in exports if r["run_id"] in wanted_ids or r["role"] in REFERENCE_ROLES]
    locator = key_dir or session.get("released_key_dir")
    release_dir = Path(locator) if locator is not None else None
    if release_dir is not None and not release_dir.is_absolute():
        release_dir = root / release_dir
    released = _released_rows(selected_exports, release_dir, blinded=stage == "blinded")
    by_id = {r["run_id"]: r for r in released}
    records, spans, physics_cache, seen = [], {}, {}, set()
    for member in roster["members"]:
        units = [u for u in member.get("units", []) if u["cell_id"] in selected]
        if not units:
            continue
        if len(units) != 1 or member["run_id"] in seen:
            raise AnalysisError("ambiguous BYTES member identity")
        seen.add(member["run_id"])
        model = selected[units[0]["cell_id"]]
        row = _record_base(model, session, acceptance["session_id"], member, exclusions, flags, window_flags)
        run_id = row["run_id"]
        counts = _withheld_counts(withheld_missing, model)
        if counts and run_id not in by_id:
            row.update(counts)
            row["flags"] = sorted(set(row["flags"]) | {"bytes.withheld_missing"})
        try:
            if run_id not in by_id:
                raise AnalysisError("planned run absent from export")
            if row["invalid_energy_record"]:
                raise AnalysisError("harvest status, bundle or validity failure")
            bundle = bundle_of(root, {}, run_id)
            if bundle is None:
                raise AnalysisError("selected bundle missing")
            config = read_json(bundle / "config.json")
            if config["model"]["name"] != model["model"]:
                raise AnalysisError("roster/config model mismatch")
            metadata = read_json(bundle / "metadata.json")
            if metadata.get("workload_observed", {}).get("output_token_count") != 512:
                raise AnalysisError("runtime-observed output count must be 512")
            events = [json.loads(t) for t in (bundle / "events.jsonl").read_text().splitlines() if t.strip()]
            stored = read_json(root / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json"))
            summary, operative = operative_summary(bundle, acceptance,
                synthetic=manifest.get("synthetic") is True, stored=stored, physics_cache=physics_cache)
            if summary.get("status") != "succeeded":
                raise AnalysisError("re-reduction not succeeded")
            energy = number(summary["phase_energy_j"]["decode"], "phase energy", nonnegative=True)
            envelope = summary["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"]
            anchor = number(envelope["max_abs_delta_j"], "decode anchor bound", nonnegative=True)
            if summary.get("energy_bound_terms_j", {}).get("E_interpolation_joint_edge_bound_j") != 0:
                raise AnalysisError("phase joint interpolation bound unavailable for non-interval trace")
            decode = _event_span(events, "decode", metadata)
            idle = _event_span(events, "idle_baseline", metadata)
            duration = (decode[1] - decode[0]) / 1e9
            own_idle = number(summary["idle_baseline"]["power_w_mean"], "own rails idle", nonnegative=True)
            row.update(status="succeeded", duration_s=duration, rails_j=energy,
                rails_secondary_j=energy - own_idle * duration, rails_anchor_j=anchor,
                rails_interpolation_j=0.0, operative=operative)
            spans[run_id] = (decode, idle)
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError) as exc:
            row.update(status="unusable", invalid_energy_record=True, unusable_reason=str(exc))
        records.append(row)
    if stage != "blinded":
        for ref in released:
            if ref["role"] not in REFERENCE_ROLES or ref["status"] != "succeeded" or ref["excluded"].lower() == "true":
                continue
            try:
                bundle = bundle_of(root, {}, ref["run_id"])
                metadata = read_json(bundle / "metadata.json")
                events = [json.loads(t) for t in (bundle / "events.jsonl").read_text().splitlines() if t.strip()]
                spans[ref["run_id"]] = (_event_span(events, "measured_run", metadata),
                                         _event_span(events, "idle_baseline", metadata))
            except (OSError, ValueError, KeyError, TypeError):
                continue
    streams = _session_streams(root, [span for pair in spans.values() for span in pair]) if spans else []
    refs = neg8_inputs(released, streams=streams, spans=spans,
                       test7_passed=session.get("test7_passed", False), blinded=stage == "blinded")
    for row in records:
        errors = []
        if row["status"] == "succeeded" and stage != "blinded":
            for name, stream in streams:
                try:
                    row["meter"] = {**meter_decode(stream, *spans[row["run_id"]]), "stream": name}
                    break
                except AnalysisError as exc:
                    errors.append(str(exc))
            if row["meter"] is None:
                row["flags"] = sorted(set(row["flags"]) | {"bytes.meter_decode_unavailable"})
        row["meter_unavailable_reason"] = "; ".join(errors) or "no raw KM003C streams" if row["meter"] is None else None
        row["neg8_inputs"] = refs
        yield row


def load_records(source, manifest, *, stage, key_dir=None, stage1_commit=None):
    """Read the export (including references); archive joins require released keys."""
    if isinstance(source, (list, tuple)):
        records = [r for item in source for r in load_records(item, manifest, stage=stage, key_dir=key_dir, stage1_commit=stage1_commit)]
        identities = [(r["session_id"], r["run_id"]) for r in records]
        if len(identities) != len(set(identities)):
            raise AnalysisError("duplicate records across inputs")
        return records
    source = Path(source)
    if source.name == "member-assessments.json":
        source = source.parent.parent
    by_session = {s["session_id"]: s for s in manifest["sessions"]}
    if (source / "derived/roster.json").is_file():
        session_id = read_json(source / "derived/b6-acceptance.json")["session_id"]
        return list(archive_records(source, manifest, by_session[session_id], stage=stage, key_dir=key_dir))
    # Session names can contain collection clocks. Traversal follows registered
    # pass identity and the manifest's plan-tree position instead.
    session_order = {s["session_id"]: index for index, s in enumerate(manifest["sessions"])}
    # Sidecars retain the collected-session census even if its CSV vanished.
    expected = set(source.rglob("*.runs.csv")) | {
        p.with_name(p.name.removesuffix(".session.json") + ".runs.csv")
        for p in source.rglob("*.session.json")}
    paths = sorted(expected, key=lambda p: (
        by_session.get(p.name.removesuffix(".runs.csv"), {}).get("pass_id", 0),
        session_order.get(p.name.removesuffix(".runs.csv"), len(session_order))))
    if not paths:
        raise AnalysisError("expected harvest archive or Block-6 export directory")
    records = []
    for path in paths:
        session_id = path.name.removesuffix(".runs.csv")
        if session_id not in by_session:
            raise AnalysisError("export session lacks archive locator")
        session = by_session[session_id]
        if stage == "blinded":
            # No archive reads whatsoever; roles, units and blinded rails are CSV inputs.
            exports, _ = _stage_export_rows(path, include_withheld=bool(stage1_commit))
            refs = neg8_inputs(exports, blinded=True, test7_passed=session.get("test7_passed", False))
            specs = {cell: m for m in manifest["models"] for cell in m["cell_ids"]}
            for exported in exports:
                cells = exported["cell_ids"].split(";")
                if not any(c in specs for c in cells):
                    continue
                if len(cells) != 1:
                    raise AnalysisError("ambiguous export unit")
                model = specs[cells[0]]
                member = {"run_id": exported["run_id"], "units": [{"cell_id": cells[0],
                    "stratum": exported["strata"], "unit_id": exported["unit_ids"]}]}
                codes = set(filter(None, exported["exclusion_codes"].split(";")))
                row = _record_base(model, session, session_id, member, {member["run_id"]: codes},
                    {member["run_id"]: set(filter(None, exported["flag_codes"].split(";")))}, set())
                try:
                    if row["invalid_energy_record"] or exported["status"] != "succeeded" or int(exported["emitted_tokens"]) != 512:
                        raise AnalysisError("export status, validity or token count invalid")
                    duration = number(float(exported["dur_decode_s"]), positive=True)
                    energy = number(float(exported["phase_decode_j"]), nonnegative=True)
                    idle = number(float(exported["idle_power_w"]), nonnegative=True)
                    anchor = number(float(exported["bound_E_clock_anchor_shift_bound_j"]), nonnegative=True)
                    joint = number(float(exported["bound_E_interpolation_joint_edge_bound_j"]), nonnegative=True)
                    row.update(status="succeeded", duration_s=duration, rails_j=energy,
                        rails_secondary_j=energy - idle * duration, rails_anchor_j=anchor,
                        rails_interpolation_j=joint, operative={"status": "blinded_export_bounds"})
                except (ValueError, KeyError, TypeError):
                    row.update(status="unusable", invalid_energy_record=True)
                row["neg8_inputs"] = refs
                records.append(row)
        else:
            records.extend(archive_records(Path(session["archive"]), manifest, session, stage=stage,
                                           export_path=path, key_dir=key_dir))
    return records


def _weighted(records, values):
    repeats, quads = [], {}
    for row, value in zip(records, values):
        if row["stratum"] == "repeat":
            repeats.append(value)
        elif row["stratum"] == "quad":
            quads.setdefault(row["unit_id"], []).append(value)
        else:
            raise AnalysisError("unexpected floor stratum")
    if not repeats or not quads or any(len(q) != 4 for q in quads.values()):
        raise AnalysisError("incomplete strata")
    return .2 * statistics.fmean(repeats) + .8 * statistics.fmean(statistics.fmean(q) for q in quads.values())


def _kept(records, inclusive):
    if len(records) != 50:
        raise AnalysisError("floor module requires 50 planned runs")
    units = {}
    for row in records:
        units.setdefault((row["stratum"], row["unit_id"]), []).append(row)
    if sum(k[0] == "repeat" for k in units) != 10 or sum(k[0] == "quad" for k in units) != 10:
        raise AnalysisError("floor module requires ten repeats and ten quads")
    kept, removed = [], []
    for (stratum, unit), rows in units.items():
        if len(rows) != (1 if stratum == "repeat" else 4):
            raise AnalysisError("floor unit census invalid")
        invalid = any(r["status"] != "succeeded" or r.get("invalid_energy_record", False)
                      or (r["excluded"] and not inclusive) for r in rows)
        (removed if invalid else kept).extend(rows)
    if sum(r["stratum"] == "repeat" for r in kept) < 5 or len({r["unit_id"] for r in kept if r["stratum"] == "quad"}) < 5:
        raise AnalysisError("fewer than five kept units per stratum")
    return kept, [r["run_id"] for r in removed]


def estimate_phase_energy(repeats, quads, repeat_bounds, quad_bounds, *, minimum_units=5):
    """Block-5 analysis_plan_block5.md §4 steps 1–5, generalized only in shape.

    No model identity, custody issuance, or inference dependency. Equivalence
    tests exercise every registered cell shape against the unchanged kernel.
    """
    n_r, n_b = len(repeats), len(quads)
    if min(n_r, n_b) < minimum_units or len(repeat_bounds) != n_r or len(quad_bounds) != n_b:
        raise AnalysisError("phase estimator requires five kept units per stratum and matching bounds")
    if any(len(q) != 4 for q in quads) or any(len(q) != 4 for q in quad_bounds):
        raise AnalysisError("phase estimator requires complete four-member quads")
    repeats = [number(e, "phase energy") for e in repeats]  # R3 secondary permits negative values.
    quads = [[number(e, "phase energy") for e in q] for q in quads]
    blocks = [statistics.fmean(q) for q in quads]
    flat = repeats + list(itertools.chain.from_iterable(quads))
    # §4.1: canonical full-module fmean; fixed strata weights after exclusions.
    mean = statistics.fmean(flat) if n_r == n_b == 10 else (
        .2 * statistics.fmean(repeats) + .8 * statistics.fmean(blocks))
    # §4.2–3: sample SD per independence stratum; conservative minimum df.
    s_r, s_b = statistics.stdev(repeats), statistics.stdev(blocks)
    variance = .2 ** 2 * s_r ** 2 / n_r + .8 ** 2 * s_b ** 2 / n_b
    df = min(n_r, n_b) - 1
    critical = 2.262157162798205 if df == 9 else student_t_quantile(.975, df)
    half = critical * math.sqrt(variance)
    # §4.4: every named kind mandatory; stratified means and math.fsum B.
    all_bounds = repeat_bounds + list(itertools.chain.from_iterable(quad_bounds))
    for bound in all_bounds:
        if set(bound) != set(BOUND_KINDS):
            raise AnalysisError("missing or extra phase bound kind")
        for kind in BOUND_KINDS:
            number(bound[kind], kind, nonnegative=True)
    terms = {}
    for kind in BOUND_KINDS:
        terms[kind] = statistics.fmean(b[kind] for b in all_bounds) if n_r == n_b == 10 else (
            .2 * statistics.fmean(b[kind] for b in repeat_bounds) +
            .8 * statistics.fmean(b[kind] for q in quad_bounds for b in q))
    bound = math.fsum(terms.values())
    # §4.5: subtract/add in registered order; never clamp secondary endpoints.
    result = {"mean_j": mean, "lower_j": mean - half - bound, "upper_j": mean + half + bound,
              "interval": {"n_r": n_r, "n_b": n_b, "df": df, "s_r": s_r, "s_b": s_b,
                           "variance": variance, "h_j": half, "kind_averages_j": terms, "B_j": bound}}
    json.dumps(result, allow_nan=False)
    return result


def _registered_estimate(records, energies, bounds, *, minimum_units=5):
    if not len(records) == len(energies) == len(bounds):
        raise AnalysisError("mismatched phase records")
    repeats, quads, repeat_bounds, quad_bounds = [], {}, [], {}
    for row, energy, bound in zip(records, energies, bounds):
        if row["stratum"] == "repeat":
            repeats.append(energy)
            repeat_bounds.append(bound)
        elif row["stratum"] == "quad":
            quads.setdefault(row["unit_id"], []).append(energy)
            quad_bounds.setdefault(row["unit_id"], []).append(bound)
        else:
            raise AnalysisError("unexpected floor stratum")
    return estimate_phase_energy(repeats, list(quads.values()), repeat_bounds, list(quad_bounds.values()),
                                 minimum_units=minimum_units)


def _phase_cell(kept, removed, module, boundary, secondary, *, minimum_units=5):
    """Identical estimator for the reported cell and its without-assisted diagnostic."""
    duration = _weighted(kept, [r["duration_s"] for r in kept])
    drift_inputs = module[0].get("neg8_inputs", {})
    reference = drift_inputs.get("boundaries", {}).get(boundary)
    if reference is None:
        raise AnalysisError("NEG-8 export references unavailable")
    rails = [r["rails_secondary_j"] if secondary else r["rails_j"] for r in kept]
    dc = [r["meter"]["secondary_j" if secondary else "gross_j"] for r in kept] if boundary != "rails" else []
    energies = rails if boundary == "rails" else dc if boundary == "DC input" else [d-r for d,r in zip(dc, rails)]
    gross_values = [r["rails_j"] if boundary == "rails" else r["meter"]["gross_j"]
                    if boundary == "DC input" else r["meter"]["gross_j"] - r["rails_j"] for r in kept]
    scale = 1.0 if drift_inputs["test7_passed"] else max(1.0,
        _weighted(kept, gross_values) / number(reference["energy_j"], "E_ref", positive=True),
        duration / number(reference["duration_s"], "T_ref", positive=True))
    family = "idle_subtracted" if secondary else "gross"
    drift = number(reference["families"][family]["allowance_j"], "NEG-8 allowance", nonnegative=True) * .5 * scale
    edge = [(r["rails_anchor_j"] if boundary != "DC input" else 0.0) +
            (r["meter"]["phase_edge_j"] if boundary != "rails" else 0.0) for r in kept]
    bounds = [dict(zip(BOUND_KINDS, (u, r.get("rails_interpolation_j", 0.0)
                 if boundary != "DC input" else 0.0, drift))) for u, r in zip(edge, kept)]
    n_r = sum(r["stratum"] == "repeat" for r in kept)
    n_b = len({r["unit_id"] for r in kept if r["stratum"] == "quad"})
    if min(n_r, n_b) < 2:
        return {"status": "undefined_interval", "n_r": n_r, "n_b": n_b,
                "mean_j": _weighted(kept, energies), "h_j": None, "B_j": math.fsum(_weighted(kept, [b[kind] for b in bounds]) for kind in BOUND_KINDS),
                "duration_s": duration, "lower_j": None, "upper_j": None,
                "reason": "sample variance requires at least two units per stratum"}
    estimate = _registered_estimate(kept, energies, bounds, minimum_units=minimum_units)
    interval = estimate["interval"]
    # R5 multiplicity widens h only; registered B is unchanged.
    h = student_t_quantile(1 - .05 / (2 * H1_CHECKS), interval["df"]) * math.sqrt(interval["variance"])
    bound, mean = interval["B_j"], estimate["mean_j"]
    return {"status": "computed", "mean_j": mean,
                 "lower_j": mean - h - bound, "upper_j": mean + h + bound,
                 "h_j": h, "B_j": bound, "kind_averages_j": interval["kind_averages_j"],
                 "meter_phase_edge_mean_j": _weighted(kept, [r["meter"]["phase_edge_j"] for r in kept]) if boundary != "rails" else 0.0,
                 "variance": interval["variance"], "df": interval["df"],
                 "duration_s": duration, "drift_scale": scale, "drift_family": family,
                 "neg8_inputs": drift_inputs, "n_r": interval["n_r"], "n_b": interval["n_b"],
                 "removed_runs": removed, "kept_runs": [r["run_id"] for r in kept],
                 "meter_unavailable": [{"run_id": r["run_id"], "reason": r.get("meter_unavailable_reason")}
                                       for r in module if r["meter"] is None],
                 "flags": sorted({f for r in kept for f in r["flags"]}),
                 "attribution_floor_j": max(edge),
                 "meter_attribution_floor_j": max(r["meter"]["phase_edge_j"] for r in kept) if boundary != "rails" else None,
                 "rails_attribution_floor_j": max(r["rails_anchor_j"] for r in kept) if boundary != "DC input" else None,
                 "operative": list({digest(r["operative"]): r["operative"] for r in kept}.values())}


def reduce_models(records, manifest, *, inclusive=False, boundaries=BOUNDARIES):
    grouped = {}
    for row in records:
        grouped.setdefault((row["model"], row["pass_id"], row["session_id"]), []).append(row)
    model_specs = {m["model"]: m for m in manifest["models"]}
    session_specs = {s["session_id"]: s for s in manifest["sessions"]}
    rows = []
    for (model, pass_id, session_id), module in sorted(grouped.items()):
        spec, session = model_specs[model], session_specs[session_id]
        for secondary, boundary in itertools.product((False, True), boundaries):
            base = {"model": model, "pass_id": pass_id, "session_id": session_id, "boundary": boundary,
                    "basis": "idle-subtracted secondary" if secondary else "gross primary",
                    "selection": "flagged-inclusive" if inclusive else "primary",
                    "bytes": (spec["W_bytes"] + spec["KV_bytes"]) / 1e9,
                    "resident": spec["R_bytes"] / 1e9, "role": spec["role"], "moe": spec["moe"], "tier": spec["tier"]}
            # §2.2: loss of one member removes its whole unit. Missing DC never
            # changes rails selection. Inclusive restores catalog exclusions, not invalid records.
            candidate = [dict(r, status="meter_unavailable") if boundary != "rails" and r["meter"] is None
                         else r for r in module]
            try:
                kept, removed = _kept(candidate, inclusive)
            except AnalysisError as exc:
                missing = next((r for r in module if "bytes.withheld_missing" in r["flags"]), None)
                rows.append({**base, "status": "missing" if missing else "unavailable",
                             "reason": "withheld rows missing" if missing else str(exc),
                             **({k: missing[k] for k in ("withheld_row_count", "withheld_config_row_count")} if missing else {}),
                             "unavailable_runs": [r["run_id"] for r in module if r["meter"] is None],
                             "flags": sorted({f for r in module for f in r["flags"]})})
                continue
            if module[0].get("neg8_inputs", {}).get("boundaries", {}).get(boundary) is None:
                rows.append({**base, "status": "unavailable", "reason": "NEG-8 export references unavailable",
                             "flags": sorted({f for r in module for f in r["flags"]})})
                continue
            cell = _phase_cell(kept, removed, module, boundary, secondary)
            assisted = [r for r in kept if "battery.assist" in r["flags"]]
            if assisted:
                units = {(r["stratum"], r["unit_id"]) for r in assisted}
                without = [r for r in kept if (r["stratum"], r["unit_id"]) not in units]
                n_r = sum(r["stratum"] == "repeat" for r in without)
                n_b = len({r["unit_id"] for r in without if r["stratum"] == "quad"})
                below = min(n_r, n_b) < 5
                diagnostic = _phase_cell(without, removed + [r["run_id"] for r in kept if r not in without],
                                         module, boundary, secondary, minimum_units=2) if n_r and n_b else {
                    "status": "undefined_estimate", "n_r": n_r, "n_b": n_b, "mean_j": None,
                    "h_j": None, "B_j": None, "lower_j": None, "upper_j": None,
                    "reason": "fixed stratum weights require both strata"}
                cell.update(assisted_member_counts={stratum: sum(r["stratum"] == stratum for r in assisted)
                                                    for stratum in ("repeat", "quad")},
                            assisted_unit_counts={stratum: sum(u[0] == stratum for u in units)
                                                  for stratum in ("repeat", "quad")},
                            with_assisted_label="with assisted members",
                            without_assisted={**diagnostic, "description_only": True,
                                "label": f"without assisted members (n_r = {n_r}, n_b = {n_b})" +
                                         ("; below the registered minimum of 5 units" if below else ""),
                                "below_minimum": below})
            rows.append({**base, **cell})
    return rows


def combine_passes(rows):
    groups = {}
    for row in rows:
        key = tuple(row[k] for k in ("model", "boundary", "basis", "selection"))
        groups.setdefault(key, []).append(row)
    points = []
    for group in groups.values():
        if len(group) not in (1, 2) or len({r["pass_id"] for r in group}) != len(group):
            raise AnalysisError("one or two distinct passes per model required")
        group.sort(key=lambda r: r["pass_id"])
        planned = group
        group = [r for r in planned if r.get("status") == "computed"]
        n = len(group)
        pass_status = "two_pass" if n == 2 else "one_pass" if n == 1 else "no_pass"
        planned = [dict(r, pass_status=pass_status, n_passes=n) for r in planned]
        point = {k: planned[0][k] for k in ("model", "boundary", "basis", "selection", "bytes", "resident", "role", "moe", "tier", "pass_status", "n_passes")}
        if not group:
            points.append({**point, "status": "unavailable", "reason": "all passes refused",
                           "passes": planned})
            continue
        mean = statistics.fmean(r["mean_j"] for r in group)
        # Addendum 4.4: average each pass's already adjusted h; no pooling.
        h = statistics.fmean(r["h_j"] for r in group)
        bound = statistics.fmean(r["B_j"] for r in group)
        meter_edge = statistics.fmean(r["meter_phase_edge_mean_j"] for r in group)
        duration = statistics.fmean(r["duration_s"] for r in group)
        point.update(mean_j=mean, lower_j=mean - h - bound, upper_j=mean + h + bound,
                     status="computed", h_j=h, B_j=bound, meter_phase_edge_mean_j=meter_edge, duration_s=duration,
                     attribution_floor_j=max(r["attribution_floor_j"] for r in group),
                     meter_attribution_floor_j=max((r["meter_attribution_floor_j"] for r in group
                         if r["meter_attribution_floor_j"] is not None), default=None),
                     pass_values_j=[r["mean_j"] for r in group],
                     pass_difference_j=group[1]["mean_j"] - group[0]["mean_j"] if n == 2 else None,
                     e=mean / DECODE_STEPS, lower=(mean - h - bound) / DECODE_STEPS,
                     upper=(mean + h + bound) / DECODE_STEPS,
                     printed_j_per_output_token=mean / 512, output_label=OUTPUT_LABEL,
                     power_half_w=(h + bound) / duration, passes=planned,
                     time=duration / DECODE_STEPS, power=mean / duration,
                     BW=point["bytes"] * DECODE_STEPS / duration)
        if any("without_assisted" in r for r in group):
            diagnostics = [r.get("without_assisted", r) for r in group]
            means = [r["mean_j"] for r in diagnostics]
            diagnostic_mean = statistics.fmean(means) if all(v is not None for v in means) else None
            diagnostic_h = statistics.fmean(r["h_j"] for r in diagnostics) if all(r["h_j"] is not None for r in diagnostics) else None
            diagnostic_bound = statistics.fmean(r["B_j"] for r in diagnostics) if all(r["B_j"] is not None for r in diagnostics) else None
            point["without_assisted"] = {
                "label": "without assisted members", **_point_label(point), "description_only": True,
                "below_minimum": any(r.get("below_minimum", False) for r in diagnostics),
                "mean_j": diagnostic_mean, "h_j": diagnostic_h, "B_j": diagnostic_bound,
                "lower_j": diagnostic_mean - diagnostic_h - diagnostic_bound if diagnostic_h is not None else None,
                "upper_j": diagnostic_mean + diagnostic_h + diagnostic_bound if diagnostic_h is not None else None,
                "printed_j_per_output_token": diagnostic_mean / 512 if diagnostic_mean is not None else None,
                "output_label": OUTPUT_LABEL,
                "passes": [{"pass_id": r["pass_id"], **d} for r, d in zip(group, diagnostics)]}
        points.append(point)
    return points


def frozen_predictions(points, manifest, neg8_inputs=None):
    if any(p["role"] != "fit" for p in points):
        raise AnalysisError("held-out point passed into freeze")
    lines = []
    for selection, basis, boundary in itertools.product(("primary", "flagged-inclusive"),
            ("gross primary", "idle-subtracted secondary"), BOUNDARIES):
        subset = [p for p in points if (p["selection"], p["basis"], p["boundary"]) == (selection, basis, boundary)]
        if not subset:
            continue
        lines.append({"selection": selection, "basis": basis, "boundary": boundary,
                      "lines": freeze_lines(subset) if all(p.get("status") != "unavailable" for p in subset) else None})
    return {"schema": SCHEMA, "manifest_sha256": digest(manifest), "H1_checks": H1_CHECKS,
            "H2_intervals": H2_INTERVALS,  # full-roster expectation; actual k is printed with each fit
            "bytes_analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "neg8_inputs": neg8_inputs or {}, "fit_points": points, "rival_lines": lines,
            "tier_fit_inputs": [{**_point_label(p), **{k: p[k] for k in ("model", "boundary", "basis", "selection", "BW", "power", "resident", "time")}}
                                for p in points if p["tier"] and p.get("status") != "unavailable"],
            "note": "Dense held-out models test linearity over the format-derived bytes range; their small rival splits do not identify the hypothesis."}


def evaluate(points, frozen):
    h1_rows, moe_rows, h2_rows, unavailable = [], [], [], []
    for group in frozen["rival_lines"]:
        key = tuple(group[k] for k in ("selection", "basis", "boundary"))
        labels = dict(zip(("selection", "basis", "boundary"), key))
        subset = [p for p in points if tuple(p[k] for k in labels) == key]
        if len(subset) != 10:
            raise AnalysisError("held-out analysis requires all ten model records, including refusals")
        missing = [p for p in subset if p.get("status") == "unavailable"]
        if group["lines"] is None or missing:
            unavailable.append({**labels, "models": [p["model"] for p in missing],
                "reason": "H1 requires complete fit cells" if group["lines"] is None else "models without a primary point",
                "refusals": [{**_point_label(p), "reason": p["reason"], "passes": p.get("passes", [])} for p in missing]})
        results = []
        for point in subset:
            if point.get("status") == "unavailable" or group["lines"] is None:
                continue
            result = h1_point(group["lines"], point)
            h1_rows.append({**_point_label(point), "role": point["role"], **labels,
                            "pass_id": "mean", "description_only": False, **result})
            if point["moe"]:
                results.append((point["model"], result))
        pass_ids = sorted({r["pass_id"] for p in subset for r in p.get("passes", [])})
        for pass_id in pass_ids:
            pass_rows = [r for p in subset for r in p.get("passes", []) if r["pass_id"] == pass_id]
            pass_points = combine_passes(pass_rows)
            fit = [p for p in pass_points if p["role"] == "fit"]
            if len(fit) != 3 or any(p["status"] != "computed" for p in fit):
                continue
            pass_lines = freeze_lines(fit)
            for point in pass_points:
                if point["status"] == "computed":
                    primary_point = next(p for p in subset if p["model"] == point["model"])
                    h1_rows.append({**_point_label(primary_point), "role": point["role"], **labels,
                        "pass_id": pass_id, "description_only": True, **h1_point(pass_lines, point)})
        if len(results) == 3:
            result = active_or_resident(results)
            for row in result["misses"]:
                row.update(_point_label(next(p for p in subset if p["model"] == row["model"])))
            moe_rows.append({**labels, **result})
        available = [p for p in subset if p.get("status") != "unavailable"]
        rails = {p["model"]: p["power"] for p in points if p.get("status") != "unavailable"
                 and (p["selection"], p["basis"], p["boundary"]) == (*key[:2], "rails")}
        result = h2(available, rails, boundary=key[2])
        h2_rows.append({**labels, "analysis": "primary", "description_only": False, **result})
        if missing or any(p.get("n_passes") == 1 for p in available):
            two_pass = [p for p in available if p["n_passes"] == 2]
            sensitivity = h2(two_pass, rails, boundary=key[2], family_size=result["k"])
            sensitivity["sensitivity_intervals"] = sensitivity.pop("primary_intervals")
            h2_rows.append({**labels, "analysis": "two_pass_sensitivity", "description_only": True, **sensitivity})
    return {"h1": h1_rows, "moe": moe_rows, "h2": h2_rows, "unavailable": unavailable}


def write_predictions(out, payload):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    path = out / "predictions.json"
    if path.exists() or path.with_suffix(".sha256").exists():
        raise AnalysisError("predictions already exist; choose a new output directory")
    path.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()
    path.with_suffix(".sha256").write_text(sha + "\n")
    return sha


def read_predictions(path, manifest):
    path = Path(path)
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if path.with_suffix(".sha256").read_text().strip() != sha:
        raise AnalysisError("predictions SHA-256 mismatch")
    frozen = json.loads(raw)
    if frozen["schema"] != SCHEMA or frozen["manifest_sha256"] != digest(manifest):
        raise AnalysisError("predictions manifest/schema mismatch")
    return frozen, sha
