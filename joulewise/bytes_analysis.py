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
import struct
import sys
from pathlib import Path

from joulewise.analysis_engine.distributions import student_t_quantile
from joulewise.desk_compress import read_bytes
from joulewise import desk_restore
from joulewise.desk_restore import readable_run

BOUNDARIES = ("rails", "DC input", "rest")
HYPOTHESES = ("bytes", "resident", "time")
DECODE_STEPS = 512
OUTPUT_LABEL = "512 decode forward passes, one of which yields no returned token"
DC_BOUNDARY_DESCRIPTION = ("whole-machine DC input plus the battery term, measured at the USB-C input; "
                           "the adapter's AC-to-DC loss is not included")
H1_CHECKS = 21
T_SMC_S = 1.0  # BAT-2 §3; km003c_parse's published SMC cadence.
# Addendum 4: separate primary families on each boundary.
H2_INTERVALS = {"rails": 9, "DC input": 9, "rest": 11}
REGISTERED_MODELS = frozenset((
    "Qwen3-1.7B-4bit", "Qwen3-4B-4bit", "Qwen3-8B-4bit", "Qwen3-14B-4bit",
    "Qwen3-32B-4bit", "Qwen3-8B-8bit", "Llama-3.3-70B-Instruct-4bit",
    "Qwen3-30B-A3B-4bit", "Qwen3-Next-80B-A3B-Instruct-4bit", "Qwen3.5-122B-A10B-4bit"))
DROPPABLE_MODEL = "Qwen3-8B-8bit"
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
    return json.loads(read_bytes(Path(path)).decode("utf-8"))


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
    # The centered/unit-variance Gram matrix has scale O(number of runs).
    # A length-n elimination accumulates O(n*epsilon*max|a|) roundoff;
    # compare pivots in that matrix's units, never to an absolute joule bar.
    pivot_noise = n * sys.float_info.epsilon * max(abs(v) for row in matrix for v in row)
    a = [list(row) + [float(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        if abs(a[pivot][j]) <= pivot_noise:
            raise AnalysisError("singular H2 design")
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        a[j] = [x / scale for x in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [x - scale * y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def ols(predictors, response, *, family_size=9, response_bounds=None):
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
    # Leverage is dimensionless. Forming X'X sums n products, so its
    # resolution is n*epsilon relative; HC3 divides by the unresolved 1-h.
    if any(1 - h <= n * sys.float_info.epsilon * max(1.0, abs(h)) for h in leverage):
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
    result = {"n": n, "df": n - p, "coefficients": coefficients, "covariance": covariance,
            "se_method": "HC3", "standard_errors": se,
            "ols_covariance": ols_covariance, "ols_standard_errors": ols_se,
            "ols_intervals": [[v - critical * e, v + critical * e] for v, e in zip(coefficients, ols_se)],
            "mse": mse, "critical": critical, "family_size": family_size,
            "intervals": [[v - critical * e, v + critical * e] for v, e in zip(coefficients, se)]}

    if response_bounds is not None:
        try:
            bounds = [number(v, "H2 coherent meter-edge power bound", nonnegative=True)
                      for v in response_bounds]
        except (AnalysisError, TypeError) as exc:
            result["systematics_flag"] = "response bounds unavailable: " + str(exc)
        else:
            if len(bounds) != n:
                result["systematics_flag"] = "response bounds unavailable: row count mismatch"
            else:
                # beta = A y. Convert the existing normalized influences to
                # printed coefficient units; C is the exact response-box support.
                result["coefficient_C"] = [math.fsum(
                    abs(math.fsum(t * v for t, v in zip(row, unit))) * bound
                    for unit, bound in zip(influence, bounds)) for row in transform]
                for target, source in (("offset_intervals", "intervals"),
                                       ("offset_ols_intervals", "ols_intervals")):
                    result[target] = [[lo - c, hi + c]
                                      for (lo, hi), c in zip(result[source], result["coefficient_C"])]
    return result


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
    return {k: point[k] for k in ("model", "pass_status", "n_passes", "flags") if k in point}


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
                      [row["power"] for row in rows], family_size=1,
                      response_bounds=[row.get("meter_offset_bound_w") for row in rows]
                      if boundary != "rails" else None)
        except AnalysisError as exc:
            return {**refused, "reason": str(exc)}
        if boundary != "rails":
            for flag in ("systematics_flag", "sensitivity_flag"):
                reasons = list(dict.fromkeys(row[flag] for row in rows if flag in row))
                if reasons:
                    fit[flag] = "; ".join(reasons)
            try:
                if "sensitivity_flag" in fit:
                    raise AnalysisError(fit["sensitivity_flag"])
                # The response derivative is (P_before_start-P_before_end)/T.
                # OLS is linear at fixed X. Divide by 1000 for per-ms units.
                sensitivity = ols([[f(row) for f in predictors] for row in rows],
                    [number(row.get("meter_offset_sensitivity_w"),
                            "adjacent-before-edge power difference") / row["duration_s"] for row in rows],
                    family_size=1)
                coefficients = [number(v / 1000, "coefficient sensitivity")
                                for v in sensitivity["coefficients"]]
            except AnalysisError as exc:
                fit["sensitivity_flag"] = str(exc)
            else:
                fit["d_beta_d_delta_per_ms"] = coefficients
                fit["sensitivity_units"] = ["W per ms", "J/GB per ms"] + (
                    ["J/GB per ms"] if p == 3 else [])
        return {**fit, "status": "computed", "p": p, "point_labels": refused["point_labels"]}

    bw, resident_rate = lambda p: p["BW"], lambda p: p["resident"] / p["time"]
    two = attempt(points, [bw])
    extended = attempt(points, [bw, resident_rate])
    tier_points = [p for p in points if p["tier"]]
    tier = attempt(tier_points, [bw, resident_rate])
    rest_points = [p for p in points if p["model"] in rails_power]
    rest = attempt(rest_points, [bw, lambda p: rails_power[p["model"]]]) if boundary == "rest" else None
    if rest is not None and "sensitivity_units" in rest:
        rest["sensitivity_units"][2] = "per ms"
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
        fit["interval_scope"] = "statistical; conditional on the mapped meter energies"
        if boundary != "rails":
            fit["offset_scope"] = "coherent meter label offset; observed regressors fixed"
            if "coefficient_C" in fit:
                for target, source in (("offset_intervals", "intervals"),
                                       ("offset_ols_intervals", "ols_intervals")):
                    fit[target] = [[lo - c, hi + c]
                                   for (lo, hi), c in zip(fit[source], fit["coefficient_C"])]
                # The same zero/sign rule is printed for both interval choices.
                decision = lambda interval: "positive" if interval[0] > 0 else (
                    "negative" if interval[1] < 0 else "contains zero")
                fit["coefficient_decisions"] = [decision(v) for v in fit["intervals"]]
                fit["offset_decisions"] = [decision(v) for v in fit["offset_intervals"]]
            else:
                fit.setdefault("systematics_flag", "missing response bounds; alternative unavailable")
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
    for name, fit, index in specs:
        if fit["status"] == "computed" and boundary != "rails":
            item = next(row for row in primary if row["term"] == name)
            if "coefficient_C" in fit:
                item.update(coefficient_C=fit["coefficient_C"][index],
                    offset_intervals=fit["offset_intervals"][index],
                    offset_ols_intervals=fit["offset_ols_intervals"][index],
                    coefficient_decision=fit["coefficient_decisions"][index],
                    offset_decision=fit["offset_decisions"][index])
            else:
                item["systematics_flag"] = fit["systematics_flag"]
            if "d_beta_d_delta_per_ms" in fit:
                item.update(d_beta_d_delta_per_ms=fit["d_beta_d_delta_per_ms"][index],
                            sensitivity_units=fit["sensitivity_units"][index])
            elif "sensitivity_flag" in fit:
                item["sensitivity_flag"] = fit["sensitivity_flag"]
    adds_nothing_offset = None
    if extended["status"] == "computed" and "offset_intervals" in extended:
        lo, hi = extended["offset_intervals"][2]
        adds_nothing_offset = lo <= 0 <= hi or extended["coefficients"][2] <= 0
    adds_nothing = None
    if extended["status"] == "computed":
        rho = extended["coefficients"][2]
        lo, hi = extended["intervals"][2]
        adds_nothing = lo <= 0 <= hi or rho <= 0
    # Judge section 2.1 (reports/b2-nr1-judge/fable.md): Delta_t plus the
    # poll round trip is 21.8 to 24.9 ms on the two committed recordings,
    # rounded to 22 to 25 ms in the disclosure below (at 50 SPS).
    offset_output = {} if boundary == "rails" else {
        "resident_adds_nothing_offset": adds_nothing_offset,
        "offset_disclosure": "Meter label offset delta is unmeasured (block-6 M13); structural bound "
            "is one sample period plus the poll round trip, 22 to 25 ms on recorded 50 SPS streams. "
            "Registered intervals are statistical; conditional on the mapped meter energies. "
            "d_beta_d_delta_per_ms prints signed fixed-design sensitivity; response bounds do not "
            "model uncertainty in regressors (including the separate rest fit's measured rails predictor)."}
    return {"n": len(points), "k": family, **offset_output, "point_labels": [_point_label(p) for p in points],
            "primary_intervals": primary, "two_term": two, "resident_extended": extended,
            "resident_adds_nothing": adds_nothing, "tier": tier, "tier_deviations": outside,
            "rest": rest, "loo_description": loo}


def h1_checks(manifest):
    """R5/registration §10: the frozen roster defines the family, even for missing rows."""
    # Arithmetic-only callers historically freeze with an empty manifest stub;
    # CLI manifests always pass validate_manifest before reaching this helper.
    if not manifest.get("models"):
        return H1_CHECKS
    return len(HYPOTHESES) * sum(m["role"] == "heldout" for m in manifest["models"])


def validate_manifest(manifest):
    models = manifest["models"]
    names = {m["model"] for m in models}
    if len(names) != len(models) or names not in (
            REGISTERED_MODELS, REGISTERED_MODELS - {DROPPABLE_MODEL}):
        raise AnalysisError("manifest requires the registered roster, optionally without Qwen3-8B-8bit")
    if sum(m["role"] == "fit" for m in models) != 3 or sum(bool(m["moe"]) for m in models) != 3:
        raise AnalysisError("manifest requires three fit and three MoE models")
    if sum(bool(m["tier"]) for m in models) != 6:
        raise AnalysisError("manifest requires six Qwen3 4-bit tier models")
    cells = []
    for model in models:
        if not isinstance(model.get("config_key"), str) or not model["config_key"].strip():
            raise AnalysisError("manifest model requires non-empty string config_key")
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


def _battery_stream_data(stream):
    times, watts = stream.battery_watts()
    interval = max((b - a for a, b in zip(stream.poll_ns, stream.poll_ns[1:])), default=0) / 1e9
    return times, watts, interval


def _battery_delay_ns(stream):
    # One second averaged, one held, then the stream's largest poll interval.
    # Keep window boundaries on the poll clock; seconds are display values.
    return round(2 * T_SMC_S * 1e9) + max(
        (b - a for a, b in zip(stream.poll_ns, stream.poll_ns[1:])), default=0)


def _decode_battery_marker(stream, raw_span, tau_ns):
    # BAT-2 §4 defines the marker by current, independently of whether a
    # voltage was available to calculate energy at that poll.
    lo = bisect.bisect_left(stream.poll_ns, raw_span[0] + tau_ns)
    hi = bisect.bisect_left(stream.poll_ns, raw_span[1] + tau_ns)
    currents = [values["B0AC"] for values in stream.smc[lo:hi]
                if values.get("B0AC") is not None]
    return any(current < 0 for current in currents) if currents else None


def meter_decode(stream, decode_span, idle_span, *, battery_readings=None):
    """R3 DC input, including BAT-2's signed SMC battery term and edge v.

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
    battery_times, battery_watts, poll_interval = (_battery_stream_data(stream)
        if battery_readings is None else battery_readings)
    battery, battery_n = kp.integrate(battery_times, battery_watts, *spans[0])
    battery_base, battery_nb = kp.integrate(battery_times, battery_watts, *spans[1])
    if battery is None or battery_base is None:
        # The archive join records this through its existing boundary-only
        # unavailable flag; rails survive and no refusal is introduced.
        raise AnalysisError("battery reading missing")
    battery_idle = battery_base / idle_duration
    battery_secondary = battery - battery_idle * duration
    # BAT-2 §3: one averaged second, one held second, then the stream's own
    # largest poll interval, over ALL polls (including incomplete SMC reads).
    tau_ns = _battery_delay_ns(stream)
    tau = tau_ns / 1e9  # display from the integer poll clock (no float tail)
    battery_edges = []
    for edge in spans[0]:
        lo = bisect.bisect_left(battery_times, edge)
        hi = bisect.bisect_left(battery_times, edge + tau_ns)
        battery_edges.append(duration / battery_n * sum(abs(w) for w in battery_watts[lo:hi]))
    v = sum(battery_edges)
    assisted = _decode_battery_marker(stream, spans[0], tau_ns)
    stats = stream.fit.stats
    residual = max(abs(number(stats[key], key)) for key in
                   ("excess_latency_ms_min", "excess_latency_ms_max")) / 1000
    interval = number(stream.samples.step_ms, "meter sample interval", positive=True) / 1000
    powers, before = [], []
    for edge in spans[0]:
        right = bisect.bisect_left(stream.host_ns, edge)
        adjacent = [i for i in (right - 1, right) if 0 <= i < len(stream.host_ns)]
        powers.append(max(number(stream.watts[i], "meter edge power", nonnegative=True) for i in adjacent))
        before.append(stream.watts[max(0, right - 1)])
    u = math.fsum(powers) * (residual + interval)
    meter_secondary = gross - base / idle_duration * duration
    return {"gross_j": gross + battery, "secondary_j": meter_secondary + battery_secondary,
            "idle_power_w": base / idle_duration + battery_idle, "phase_edge_j": u + v,
            "meter_gross_j": gross, "meter_secondary_j": meter_secondary,
            "meter_idle_power_w": base / idle_duration, "meter_phase_edge_j": u,
            "battery_gross_j": battery, "battery_secondary_j": battery_secondary,
            "battery_idle_power_w": battery_idle, "battery_phase_edge_j": v,
            "battery_v_start_j": battery_edges[0], "battery_v_end_j": battery_edges[1],
            "battery_tau_s": tau, "battery_poll_interval_max_s": poll_interval,
            "battery_end_window_complete": bool(stream.poll_ns and
                stream.poll_ns[-1] >= spans[0][1] + tau_ns),
            "battery_n": battery_n, "battery_n_idle": battery_nb,
            "decode_battery_assist": bool(assisted),
            "edge_powers_w": powers, "r_max_s": residual, "sample_interval_s": interval,
            # One slice is swapped under a coherent offset, hence max, not
            # the sum in u. NR1 adopts the existing (r_max + interval) factor.
            "offset_bound_j": max(powers) * (residual + interval) + max(battery_edges),
            "offset_sensitivity_w": before[0] - before[1],
            "adjacent_before_edge_powers_w": before,
            "n": n, "n_idle": nb, "clock_fit": stats}


def operative_summary(bundle, acceptance, *, synthetic=False, stored=None, physics_cache=None):
    """Consume B6's evaluated own-session bound; never recompute a bracket.

    B6 calibration.evaluate owns max(pre,post)+max(drift,screen). The existing
    output-free reducer seam owns re-derivation and rejects narrowed bounds.
    """
    from joulewise.reduce import _rederive_summary_for_authenticated_fiducial_bound
    from joulewise.desk_restore import readable_run
    cal = acceptance.get("calibration") or {}
    value = cal.get("operative_bound_s")
    if value is None or isinstance(value, bool):
        raise AnalysisError("operative-bracket join missing: b6-acceptance.calibration.operative_bound_s")
    bound = number(float(value), "harvest operative bound", nonnegative=True)
    with readable_run(bundle) as plain:
        summary = _rederive_summary_for_authenticated_fiducial_bound(
            plain, authenticated_fiducial_bound_s=bound,
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
    """Read native samples/fit points, retaining only selected run spans.

    Native samples() owns decoding, unwrap and replay filtering; clock_fit()
    consumes its last kept sample in each original batch. A timing-only native
    pass zeroes power fields, so unreleased power is never decoded. A second
    native pass decodes only selected words. One nearest sample on each side is kept
    for the ruled meter edge bound, including across dropped-sample gaps.
    All poll receive times are retained for BAT-2's largest poll interval.
    SMC readings are retained only in selected raw-clock [start, end + tau)
    windows using the header/trailer raw/monotonic mapping, independently of
    sample decoding and the meter clock fit. Without that mapping, none are
    retained. Invalid sample payloads leave the polls available to the marker.
    """
    from joulewise.external import km003c_parse as kp
    header = trailer = None
    polls = []
    with Path(path).open() as handle:
        for raw in handle:
            item = json.loads(raw)
            kind = item.get("k")
            if kind == "h":
                header = item
            elif kind == "t":
                trailer = item
            elif kind == "b":
                polls.append(item)
    if header is not None and "status" not in header:
        header = {**header, "status": "streaming"}
    # Match km003c_parse.parse: transport line order is not receive order.
    polls.sort(key=lambda item: item["rx"])
    poll_ns = [item["rx"] for item in polls]
    smc = [{} for _ in polls]
    shell = kp.Stream(header, trailer, [], [], None, None, [], [], poll_ns, smc)
    offset = kp.raw_offset_ns(shell)
    if offset is not None:
        tau_ns = _battery_delay_ns(shell)
        for a, b in spans:
            lo = bisect.bisect_left(poll_ns, a + offset)
            hi = bisect.bisect_left(poll_ns, b + offset + tau_ns)
            for i in range(lo, hi):
                smc[i] = dict(polls[i].get("smc") or {})
    if header is None or header.get("status") != "streaming":
        return shell
    batches = [item for item in polls if item.get("n")]
    # A bad rate is a transport/header failure, as before. Sample failures
    # affect only the energy join: BAT-2 still reads the mapped polls.
    kp.STEP_MS[header["rate_idx"]]
    word_batches = []
    def native_batches(selected=None):
        # Give each word its own native batch index, so samples().batch tells
        # us exactly which raw words survived native replay filtering. Splitting
        # a batch preserves the native k==0 stall rule: subsequent words have
        # the same rx, hence zero host gap. Fit uses the ORIGINAL batch indices.
        word_index = 0
        for j, batch in enumerate(batches):
            raw = bytes.fromhex(batch["p"]) if batch.get("p") else b""
            for start in range(0, len(raw), kp.SAMPLE.size):
                word = raw[start:start + kp.SAMPLE.size]
                if selected is None:
                    word_batches.append(j)
                if selected is None or word_index not in selected:
                    # Preserve the sequence and length (including partial
                    # words); no voltage/current from this word is decoded.
                    word = word[:2] + bytes(max(0, len(word) - 2))
                yield {"rx": batch["rx"], "p": word.hex()}
                word_index += 1
    try:
        samples = kp.samples(header, native_batches())
    except (ValueError, TypeError, struct.error) as exc:
        shell.fit_error = str(exc)
        return shell
    words = samples.batch
    samples.batch = [word_batches[i] for i in words]
    try:
        # Native parse catches only ValueError here; a non-numeric transport
        # field (n, tx) is a transport failure that discards the stream.
        fit = kp.clock_fit(samples, batches)
    except ValueError as exc:
        shell.fit_error = str(exc)
        return shell
    shell.fit = fit
    if offset is None:
        return shell
    host = [fit.host_ns(dev) for dev in samples.dev_ms]
    # Indices, rather than a fixed time margin, keep the actual neighbours
    # when a device sample next to an edge was dropped.
    ranges = sorted((max(0, bisect.bisect_left(host, a + offset) - 1),
                     min(len(host), bisect.bisect_left(host, b + offset) + 1))
                    for a, b in spans)
    merged = []
    for lo, hi in ranges:
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(hi, merged[-1][1])
        else:
            merged.append([lo, hi])
    indices = [i for lo, hi in merged for i in range(lo, hi)]
    decoded = kp.samples(header, native_batches({words[i] for i in indices}))
    shell.samples = kp.Samples([decoded.dev_ms[i] for i in indices],
                               [decoded.vbus_v[i] for i in indices],
                               [decoded.ibus_a[i] for i in indices],
                               [samples.batch[i] for i in indices],
                               samples.duplicates, samples.step_ms)
    shell.host_ns = [host[i] for i in indices]
    shell.watts = shell.samples.watts
    return shell


def _session_streams(root, spans):
    from joulewise.external import km003c_parse as kp
    directory = root / "sources/night-custody/hazards/meter"
    streams = []
    for path in sorted(directory.glob("stream-*.jsonl")):
        try:
            stream = _filtered_stream(path, spans)
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError, struct.error) as exc:
            stream = kp.Stream(None, None, [], [], None, None, [], [], [], [], str(exc))
        streams.append((path.name, stream))
    return streams


# These exclusions establish absence or invalidity of the energy record.
# Other catalog exclusions, including NUMBER cooldown/idle/envelope flags,
# can be restored if the record itself passes the checks below.
INVALID_RECORD_CODES = frozenset({"member.bytes_missing", "member.bytes_ambiguous", "member.unreadable",
    "member.status_not_succeeded", "member.strict_validation_failed", "member.token_count_mismatch",
    # F15: a fallback anchor cannot place a valid energy record on the phase clock.
    "member.anchor_not_bounded"})
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
    info = {**info, "withheld_path_checked": str((path.parent / info["path"]).resolve())}
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
    return {"withheld_row_count": info["row_count"], "withheld_config_row_count": count,
            **({"withheld_path_checked": info["withheld_path_checked"]}
               if "withheld_path_checked" in info else {})} if count else {}


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
            if by_id[run_id]["status"] != "succeeded":
                raise AnalysisError("export status not succeeded")
            if row["invalid_energy_record"]:
                raise AnalysisError("harvest status, bundle or validity failure")
            bundle = bundle_of(root, {}, run_id)
            if bundle is None:
                raise AnalysisError("selected bundle missing")
            with readable_run(bundle, compression_records=Path(str(root) + ".desk") / "compression.jsonl") as bundle:
                config = read_json(bundle / "config.json")
                if config["model"]["name"] != model["model"]:
                    raise AnalysisError("roster/config model mismatch")
                metadata = read_json(bundle / "metadata.json")
                if metadata.get("workload_observed", {}).get("output_token_count") != 512:
                    raise AnalysisError("runtime-observed output count must be 512")
                events = [json.loads(t) for t in read_bytes(bundle / "events.jsonl").decode("utf-8").splitlines() if t.strip()]
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
                with readable_run(bundle, compression_records=Path(str(root) + ".desk") / "compression.jsonl") as bundle:
                    metadata = read_json(bundle / "metadata.json")
                    events = [json.loads(t) for t in read_bytes(bundle / "events.jsonl").decode("utf-8").splitlines() if t.strip()]
                    spans[ref["run_id"]] = (_event_span(events, "measured_run", metadata),
                                             _event_span(events, "idle_baseline", metadata))
            except (OSError, ValueError, KeyError, TypeError):
                continue
    streams = _session_streams(root, [span for pair in spans.values() for span in pair]) if spans else []
    refs = neg8_inputs(released, streams=streams, spans=spans,
                       test7_passed=session.get("test7_passed", False), blinded=stage == "blinded")
    # Prepare immutable stream inputs once for this reduction, not once per
    # run. Direct meter_decode callers always see their stream's current data.
    prepared_streams = [(name, stream, _battery_stream_data(stream)) for name, stream in streams]
    for row in records:
        errors = []
        if row["status"] == "succeeded" and stage != "blinded":
            for name, stream, battery_readings in prepared_streams:
                try:
                    row["meter"] = {**meter_decode(stream, *spans[row["run_id"]],
                                                  battery_readings=battery_readings), "stream": name}
                    from joulewise.external import km003c_parse as kp
                    raw_span = [edge + kp.raw_offset_ns(stream) for edge in spans[row["run_id"]][0]]
                    if _decode_battery_marker(stream, raw_span, _battery_delay_ns(stream)) is None:
                        row["decode_assist_evaluated"] = False
                        row["decode_assist_evaluated_reason"] = (
                            "decode marker not evaluated: selected meter stream has no polls carrying B0AC"
                            f" in the marker window (run {row['run_id']})")
                    if row["meter"]["decode_battery_assist"]:
                        row["flags"] = sorted(set(row["flags"]) | {"bytes.decode_battery_assist"})
                    break
                except AnalysisError as exc:
                    errors.append(str(exc))
            if row["meter"] is None:
                row["flags"] = sorted(set(row["flags"]) | {"bytes.meter_decode_unavailable"})
                from joulewise.external import km003c_parse as kp
                marker_windows = []
                for name, stream, battery_readings in prepared_streams:
                    offset = kp.raw_offset_ns(stream)
                    if offset is None:
                        continue
                    raw_span = [edge + offset for edge in spans[row["run_id"]][0]]
                    tau_ns = _battery_delay_ns(stream)
                    marker = _decode_battery_marker(stream, raw_span, tau_ns)
                    if marker is None:
                        continue
                    marker_windows.append(stream.poll_ns[-1] >= raw_span[1] + tau_ns)
                    if marker:
                        row["flags"] = sorted(set(row["flags"]) | {"bytes.decode_battery_assist"})
                row["decode_assist_evaluated"] = bool(marker_windows)
                row["battery_end_window_complete"] = any(marker_windows)
                if not marker_windows:
                    row["decode_assist_evaluated_reason"] = (
                        "decode marker not evaluated: no mapped meter stream has polls carrying B0AC in the marker window"
                        f" (run {row['run_id']})")
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
            exports, withheld_missing = _stage_export_rows(path, include_withheld=bool(stage1_commit))
            records.extend(_missing_withheld_records(withheld_missing, manifest, session))
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
                row["decode_assist_evaluated"] = False
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


def _phase_cell(kept, removed, module, boundary, secondary, *, minimum_units=5, h1_family=H1_CHECKS):
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
    battery_column = {}
    if boundary != "rails":
        terms = [r["meter"]["battery_secondary_j" if secondary else "battery_gross_j"] for r in kept]
        battery_column = {"boundary_description": DC_BOUNDARY_DESCRIPTION,
            "battery_term_mean_j": _weighted(kept, terms), "battery_term_max_j": max(terms),
            "battery_nonzero_run_count": sum(value != 0 for value in terms),
            "battery_phase_edge_max_j": max(r["meter"]["battery_phase_edge_j"] for r in kept),
            "meter_run_terms": [{"run_id": r["run_id"], **r["meter"]} for r in kept]}
    n_r = sum(r["stratum"] == "repeat" for r in kept)
    n_b = len({r["unit_id"] for r in kept if r["stratum"] == "quad"})
    if min(n_r, n_b) < 2:
        return {"status": "undefined_interval", **battery_column, "n_r": n_r, "n_b": n_b,
                "mean_j": _weighted(kept, energies), "h_j": None, "B_j": math.fsum(_weighted(kept, [b[kind] for b in bounds]) for kind in BOUND_KINDS),
                "duration_s": duration, "lower_j": None, "upper_j": None,
                "reason": "sample variance requires at least two units per stratum"}
    estimate = _registered_estimate(kept, energies, bounds, minimum_units=minimum_units)
    interval = estimate["interval"]
    # R5 multiplicity widens h only; registered B is unchanged.
    h = student_t_quantile(1 - .05 / (2 * h1_family), interval["df"]) * math.sqrt(interval["variance"])
    bound, mean = interval["B_j"], estimate["mean_j"]
    offset = {}
    if boundary != "rails":
        for field, flag in (("bound_j", "systematics_flag"),
                            ("sensitivity_w", "sensitivity_flag")):
            values, reasons = [], []
            for row in kept:
                try:
                    # Validate each run before weighting: a negative bound may
                    # otherwise disappear inside a positive mean. Signed
                    # sensitivity is valid, but missing/non-finite values are not.
                    values.append(number(row["meter"].get("offset_" + field),
                        "meter offset " + field, nonnegative=field == "bound_j"))
                except AnalysisError as exc:
                    reasons.append(f"run {row['run_id']}: {exc}")
            offset["meter_offset_" + field] = None if reasons else _weighted(kept, values)
            if reasons:
                offset[flag] = "; ".join(reasons)
    return {"status": "computed", **offset, **battery_column, "mean_j": mean,
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
            if boundary != "rails":
                base["boundary_description"] = DC_BOUNDARY_DESCRIPTION
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
                             **({k: missing[k] for k in ("withheld_row_count", "withheld_config_row_count", "withheld_path_checked") if k in missing} if missing else {}),
                             "unavailable_runs": [r["run_id"] for r in module if r["meter"] is None],
                             "flags": sorted({f for r in module for f in r["flags"]})})
                continue
            if module[0].get("neg8_inputs", {}).get("boundaries", {}).get(boundary) is None:
                rows.append({**base, "status": "unavailable", "reason": "NEG-8 export references unavailable",
                             "flags": sorted({f for r in module for f in r["flags"]})})
                continue
            cell = _phase_cell(kept, removed, module, boundary, secondary, h1_family=h1_checks(manifest))
            assisted = [r for r in kept if "bytes.decode_battery_assist" in r["flags"]]
            cell.update(decode_assisted_member_counts={stratum: sum(r["stratum"] == stratum for r in assisted)
                                                       for stratum in ("repeat", "quad")},
                        harvest_assisted_member_counts={stratum: sum(r["stratum"] == stratum and
                            "battery.assist" in r["flags"] for r in kept) for stratum in ("repeat", "quad")})
            if any(r.get("decode_assist_evaluated") is False for r in kept):
                reason = "; ".join(sorted({r.get("decode_assist_evaluated_reason",
                    "not evaluated at the blinded stage") for r in kept
                    if r.get("decode_assist_evaluated") is False}))
                cell.update(decode_assisted_member_counts=None,
                    decode_assisted_member_counts_reason=reason,
                    with_assisted_label="with assisted members",
                    without_assisted={"status": "not_evaluated", "reason": reason,
                        "description_only": True, "label": "without assisted members; " + reason,
                        **dict.fromkeys(("n_r", "n_b", "mean_j", "h_j", "B_j", "lower_j", "upper_j"))})
            elif assisted:
                units = {(r["stratum"], r["unit_id"]) for r in assisted}
                without = [r for r in kept if (r["stratum"], r["unit_id"]) not in units]
                n_r = sum(r["stratum"] == "repeat" for r in without)
                n_b = len({r["unit_id"] for r in without if r["stratum"] == "quad"})
                below = min(n_r, n_b) < 5
                # Two units are the smallest sample with an estimable sample variance.
                diagnostic = _phase_cell(without, removed + [r["run_id"] for r in kept if r not in without],
                                         module, boundary, secondary, minimum_units=2,
                                         h1_family=h1_checks(manifest)) if n_r and n_b else {
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
        if point["boundary"] != "rails":
            point.update(boundary_description=DC_BOUNDARY_DESCRIPTION,
                battery_term_mean_j=statistics.fmean(r["battery_term_mean_j"] for r in group),
                battery_term_max_j=max(r["battery_term_max_j"] for r in group),
                battery_nonzero_run_count=sum(r["battery_nonzero_run_count"] for r in group),
                battery_phase_edge_max_j=max(r["battery_phase_edge_max_j"] for r in group))
            # Average available per-pass terms just as B; no sqrt(n) or t.
            for field, flag in (("meter_offset_bound_j", "systematics_flag"),
                                ("meter_offset_sensitivity_w", "sensitivity_flag")):
                reasons = list(dict.fromkeys(r[flag] for r in group if flag in r))
                try:
                    values = [number(r.get(field), field,
                        nonnegative=field == "meter_offset_bound_j") for r in group]
                except AnalysisError as exc:
                    point[field] = None
                    point[flag] = "; ".join(reasons) if reasons else str(exc)
                else:
                    point[field] = statistics.fmean(values)
            # Coherent energy support uses the registered ratio of means: the
            # pass-averaged joules divided by the point's mean decode time.
            value = point["meter_offset_bound_j"]
            point["meter_offset_bound_w"] = value / duration if value is not None else None
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
            if any(d.get("status") == "not_evaluated" for d in diagnostics):
                reasons = [(r["pass_id"], d.get("reason", "not evaluated at the blinded stage"))
                           for r, d in zip(group, diagnostics) if d.get("status") == "not_evaluated"]
                reason = ("not evaluated at the blinded stage" if all(
                    text == "not evaluated at the blinded stage" for _, text in reasons) else
                    "; ".join(f"pass {pass_id}: {text}" for pass_id, text in reasons))
                point["without_assisted"].update(status="not_evaluated",
                    reason=reason, label="without assisted members; " + reason)
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
    models = manifest.get("models", [])
    dropped = len(models) == 9 and all(m["model"] != DROPPABLE_MODEL for m in models)
    return {"schema": SCHEMA, "manifest_sha256": digest(manifest), "H1_checks": h1_checks(manifest),
            "H2_intervals": {boundary: k - int(dropped) for boundary, k in H2_INTERVALS.items()},
            # Roster expectation; actual k is printed with each fit (Addendum 7 D9).
            "bytes_analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "desk_restore_sha256": hashlib.sha256(Path(desk_restore.__file__).read_bytes()).hexdigest(),
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
        # Three fit models plus the manifest's frozen held-out family (three checks each).
        if len(subset) != 3 + frozen["H1_checks"] // len(HYPOTHESES):
            raise AnalysisError("held-out analysis requires all manifest model records, including refusals")
        missing = [p for p in subset if p.get("status") != "computed"]
        if group["lines"] is None or missing:
            unavailable.append({**labels, "models": [p["model"] for p in missing],
                "reason": "H1 requires complete fit cells" if group["lines"] is None else "models without a primary point",
                "refusals": [{**_point_label(p), "reason": p["reason"], "passes": p.get("passes", [])} for p in missing]})
        results = []
        for point in subset:
            if point.get("status") != "computed":
                h1_rows.append({**_point_label(point), "role": point["role"], **labels,
                    "pass_id": "mean", "description_only": False, "status": "missing",
                    "reason": point["reason"], "flags": sorted(set(point.get("flags", [])) | {
                        flag for row in point.get("passes", []) for flag in row.get("flags", [])})})
                continue
            if group["lines"] is None:
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
        else:
            moe_rows.append({**labels, "status": "missing", "answer": "missing",
                "reason": "H1 requires complete fit cells" if group["lines"] is None else
                          "active or resident requires all three MoE points",
                "missing_models": [_point_label(p) for p in missing if p["moe"] or group["lines"] is None],
                "flags": sorted({flag for p in missing for row in p.get("passes", [])
                                 for flag in row.get("flags", [])})})
        available = [p for p in subset if p.get("status") == "computed"]
        rails = {p["model"]: p["power"] for p in points if p.get("status") == "computed"
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
