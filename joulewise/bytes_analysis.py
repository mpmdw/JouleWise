"""BYTES R3/R5 desk analysis. No runtime or measurement entry points.

Artifacts are analysis records, not Block-5 paper-custody capabilities.
"""
from __future__ import annotations

import bisect
import hashlib
import itertools
import json
import math
import statistics
from pathlib import Path

from joulewise.analysis_engine.distributions import student_t_quantile

BOUNDARIES = ("rails", "DC input", "rest")
HYPOTHESES = ("bytes", "resident", "time")
DECODE_STEPS = 511
OUTPUT_LABEL = "512 output tokens, 511 generated in the decode phase"
H1_CHECKS = 21
# epsilon (all and tier), rho, four tier deviations per boundary; rest epsilon/lambda.
H2_INTERVALS = 3 * (1 + 1 + 1 + 4) + 2
SCHEMA = "joulewise.bytes_predictions.v1"


class AnalysisError(ValueError):
    """Input cannot support the requested analysis; no partial result is issued."""


def number(value, label="number", *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise AnalysisError(f"{label}: finite number required")
    if (positive and value <= 0) or (nonnegative and value < 0):
        raise AnalysisError(f"{label}: invalid sign")
    return float(value)


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


def ols(predictors, response, *, family_size=H2_INTERVALS):
    """OLS with centered/scaled columns and Student-t coefficient intervals."""
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
    covariance = [[mse * math.fsum(transform[i][k] * inv[k][l] * transform[j][l]
                                  for k in range(p) for l in range(p))
                   for j in range(p)] for i in range(p)]
    critical = student_t_quantile(1 - .05 / (2 * family_size), n - p)
    half = [critical * math.sqrt(max(0.0, covariance[i][i])) for i in range(p)]
    return {"n": n, "df": n - p, "coefficients": coefficients, "covariance": covariance,
            "mse": mse, "critical": critical, "family_size": family_size,
            "intervals": [[v - h, v + h] for v, h in zip(coefficients, half)]}


def deviation(fit, predictors, observed):
    x = [1.0, *predictors]
    fitted = math.fsum(a * b for a, b in zip(x, fit["coefficients"]))
    variance = fit["mse"] + math.fsum(x[i] * fit["covariance"][i][j] * x[j]
                                      for i in range(len(x)) for j in range(len(x)))
    half = fit["critical"] * math.sqrt(max(0.0, variance))
    delta = observed - fitted
    return {"deviation_w": delta, "lower_w": delta - half, "upper_w": delta + half,
            "predicted_w": fitted}


def h2(points, rails_power):
    xs, ys = [[p["BW"]] for p in points], [p["power"] for p in points]
    two = ols(xs, ys)
    extended = ols([[p["BW"], p["resident"] / p["time"]] for p in points], ys)
    rho = extended["coefficients"][2]
    lo, hi = extended["intervals"][2]
    tier_points = [p for p in points if p["tier"]]
    tier = ols([[p["BW"]] for p in tier_points], [p["power"] for p in tier_points])
    outside = [{"model": p["model"], **deviation(tier, [p["BW"]], p["power"])}
               for p in points if not p["tier"]]
    rest = ols([[p["BW"], rails_power[p["model"]]] for p in points], ys) if points[0]["boundary"] == "rest" else None
    loo = []
    for i, p in enumerate(points):
        f = ols(xs[:i] + xs[i + 1:], ys[:i] + ys[i + 1:])
        loo.append({"model": p["model"], "predicted_w": predict(f["coefficients"], p["BW"]),
                    "observed_w": p["power"]})
    primary = [
        {"term": name, "estimate": fit["coefficients"][index],
         "lower": fit["intervals"][index][0], "upper": fit["intervals"][index][1]}
        for name, fit, index in (("epsilon", two, 1), ("rho", extended, 2), ("tier_epsilon", tier, 1))]
    primary += [{"term": "tier_deviation:" + row["model"], "estimate": row["deviation_w"],
                 "lower": row["lower_w"], "upper": row["upper_w"]} for row in outside]
    if rest is not None:
        primary += [{"term": name, "estimate": rest["coefficients"][index],
                     "lower": rest["intervals"][index][0], "upper": rest["intervals"][index][1]}
                    for name, index in (("rest_epsilon", 1), ("lambda", 2))]
    return {"primary_intervals": primary, "two_term": two, "resident_extended": extended,
            "resident_adds_nothing": lo <= 0 <= hi or rho <= 0,
            "tier": tier, "tier_deviations": outside, "rest": rest, "loo_description": loo}


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


def _shift_values(times, spans, bound):
    # integrate changes only as an endpoint crosses a sample. Include both sides of each discontinuity.
    shifts = {-bound, 0, bound}
    for span in spans:
        for edge in span:
            lo, hi = bisect.bisect_left(times, edge - bound), bisect.bisect_right(times, edge + bound)
            for stamp in times[lo:hi]:
                d = stamp - edge
                shifts.update((max(-bound, d - 1), d, min(bound, d + 1)))
    return sorted(shifts)


def meter_decode(stream, decode_span, idle_span, *, clock_bound_ns):
    """DC input only, without a battery correction. Exact common-shift envelope.

    The bound is a required prospectively frozen input: km003c_parse supplies
    diagnostics, not an accepted uncertainty bound. No residual percentile is
    silently promoted to a coverage guarantee.
    """
    from joulewise.external import km003c_parse as kp
    bound = number(clock_bound_ns, "meter_clock_bound_ns", nonnegative=True)
    if int(bound) != bound:
        raise AnalysisError("meter clock bound must be integer nanoseconds")
    bound = int(bound)
    offset = kp.raw_offset_ns(stream)
    if not stream.aligned or offset is None:
        raise AnalysisError("meter raw/monotonic mapping unavailable")
    spans = [[edge + offset for edge in span] for span in (decode_span, idle_span)]
    if any(span[0] - bound < stream.host_ns[0] or span[1] + bound > stream.host_ns[-1] for span in spans):
        raise AnalysisError("meter does not cover decode and own idle spans plus uncertainty")
    duration = (spans[0][1] - spans[0][0]) / 1e9
    idle_duration = (spans[1][1] - spans[1][0]) / 1e9
    values = []
    for shift in _shift_values(stream.host_ns, spans, bound):
        gross, n = kp.integrate(stream.host_ns, stream.watts, *(edge + shift for edge in spans[0]))
        base, nb = kp.integrate(stream.host_ns, stream.watts, *(edge + shift for edge in spans[1]))
        if gross is None or base is None:
            raise AnalysisError("meter span has no samples")
        values.append((shift, gross, gross - base / idle_duration * duration, base / idle_duration, n, nb))
    point = next(v for v in values if v[0] == 0)
    return {"gross_j": point[1], "secondary_j": point[2], "idle_power_w": point[3],
            "gross_clock_j": max(abs(v[1] - point[1]) for v in values),
            "secondary_clock_j": max(abs(v[2] - point[2]) for v in values),
            "n": point[4], "n_idle": point[5], "clock_bound_ns": bound,
            "clock_fit": stream.fit.stats}


def _session_streams(root):
    from joulewise.external import km003c_parse as kp
    directory = root / "sources/night-custody/hazards/meter"
    paths = sorted(directory.glob("stream-*.jsonl"))
    if not paths:
        raise AnalysisError("archive has no raw KM003C streams")
    return [(path.name, kp.parse(path)) for path in paths]


def archive_records(root, manifest, session, *, stage):
    """Read harvest's roster, assessments, reductions and original bundle events.

    Selection uses only roster cell identities before opening any model's
    configuration, summary, metadata, or events. Streams are opened lazily.
    """
    from joulewise.b6.archive import bundle_of
    root = Path(root)
    roster = read_json(root / "derived/roster.json")
    acceptance = read_json(root / "derived/b6-acceptance.json")
    if acceptance.get("counting") is not True:
        raise AnalysisError("session is not a counting accepted attempt")
    selected = {cell: m for m in manifest["models"] for cell in m["cell_ids"]
                if stage == "all" or m["role"] == stage}
    exclusions = {e["run_id"] for e in acceptance.get("excluding", []) if e.get("scope") == "member"}
    flags, window_flags = {}, set()
    path = root / "derived/flags.jsonl"
    for raw in path.read_text().splitlines():
        flag = json.loads(raw)
        scope = flag.get("scope") or {}
        if scope.get("run_id"):
            flags.setdefault(scope["run_id"], set()).add(flag["code"])
        else:
            window_flags.add(flag["code"])
    streams = None
    seen = set()
    for member in roster["members"]:
        units = [u for u in member.get("units", []) if u["cell_id"] in selected]
        if not units:
            continue
        if len(units) != 1:
            raise AnalysisError("member belongs to multiple BYTES units")
        unit = units[0]
        model = selected[unit["cell_id"]]
        run_id = member["run_id"]
        if run_id in seen:
            raise AnalysisError("duplicate run id")
        seen.add(run_id)
        bundle = bundle_of(root, {}, run_id)
        if bundle is None:
            raise AnalysisError("selected bundle missing")
        config = read_json(bundle / "config.json")
        if config["model"]["name"] != model["model"]:
            raise AnalysisError("roster/config model mismatch")
        metadata = read_json(bundle / "metadata.json")
        events = [json.loads(s) for s in (bundle / "events.jsonl").read_text().splitlines() if s.strip()]
        summary = read_json(root / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json"))
        counts = metadata.get("workload_observed", {})
        if counts.get("output_token_count") != 512:
            raise AnalysisError("runtime-observed output count must be 512")
        decode = _event_span(events, "decode", metadata)
        idle = _event_span(events, "idle_baseline", metadata)
        duration = (decode[1] - decode[0]) / 1e9
        if streams is None:
            streams = _session_streams(root)
        meter = None
        errors = []
        for name, stream in streams:
            try:
                meter = meter_decode(stream, decode, idle, clock_bound_ns=session["meter_clock_bound_ns"])
                meter["stream"] = name
                break
            except AnalysisError as exc:
                errors.append(str(exc))
        if meter is None:
            raise AnalysisError("no usable decode meter stream: " + "; ".join(errors))
        energy = number(summary["phase_energy_j"]["decode"], "phase energy", nonnegative=True)
        envelope = summary["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"]
        anchor_bound = number(envelope["max_abs_delta_j"], "decode anchor bound", nonnegative=True)
        # Joint interpolation bounds are identically zero only for interval support.
        if summary.get("energy_bound_terms_j", {}).get("E_interpolation_joint_edge_bound_j") != 0:
            raise AnalysisError("phase joint interpolation bound unavailable for non-interval trace")
        own_idle = number(summary["idle_baseline"]["power_w_mean"], "own rails idle", nonnegative=True)
        run_flags = sorted(flags.get(run_id, set()) | window_flags)
        yield {"model": model["model"], "pass_id": session["pass_id"], "session_id": acceptance["session_id"],
               "run_id": run_id, "stratum": unit["stratum"], "unit_id": str(unit["unit_id"]),
               "duration_s": duration, "rails_j": energy, "rails_secondary_j": energy - own_idle * duration,
               "rails_anchor_j": anchor_bound, "meter": meter,
               "excluded": any(f in ("thermal.os_level_nonzero", "thermal.powermetrics_pressure_elevated") for f in run_flags),
               "harvest_excluded": run_id in exclusions, "flags": run_flags,
               "status": summary["status"]}


def load_records(source, manifest, *, stage):
    """Archive directory, harvest member-assessments path, or export directory.

    Exports need the matching archive locator in manifest.sessions: the stage-1
    CSV alone cannot recover decode meter energy or phase-specific bounds.
    """
    if isinstance(source, (list, tuple)):
        records = [r for item in source for r in load_records(item, manifest, stage=stage)]
        identities = [(r["session_id"], r["run_id"]) for r in records]
        if len(identities) != len(set(identities)):
            raise AnalysisError("duplicate records across inputs")
        return records
    source = Path(source)
    if source.name == "member-assessments.json":
        source = source.parent.parent
    roots = [source] if (source / "derived/roster.json").is_file() else []
    if not roots:
        # The export's filenames locate sessions without opening mixed/blinded CSVs.
        ids = {p.name.removesuffix(".runs.csv") for p in source.rglob("*.runs.csv")}
        if not ids:
            raise AnalysisError("expected harvest archive or Block-6 export directory")
        by_session = {s["session_id"]: s for s in manifest["sessions"]}
        if not ids <= by_session.keys():
            raise AnalysisError("export session lacks archive locator")
        roots = [Path(by_session[i]["archive"]) for i in sorted(ids)]
    by_session = {s["session_id"]: s for s in manifest["sessions"]}
    records = []
    for root in roots:
        session_id = read_json(root / "derived/b6-acceptance.json")["session_id"]
        if session_id not in by_session:
            raise AnalysisError("archive session missing from manifest")
        records.extend(archive_records(root, manifest, by_session[session_id], stage=stage))
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
        invalid = any(r["status"] != "succeeded" or (r["excluded"] and not inclusive) for r in rows)
        (removed if invalid else kept).extend(rows)
    if sum(r["stratum"] == "repeat" for r in kept) < 5 or len({r["unit_id"] for r in kept if r["stratum"] == "quad"}) < 5:
        raise AnalysisError("fewer than five kept units per stratum")
    return kept, [r["run_id"] for r in removed]


def _registered_estimate(records, energies, bounds):
    # The shared function is deliberately resolved lazily: importing BYTES has
    # no measurement dependencies. The current repository's fixed-cell kernel
    # cannot accept this general floor-module interface (contract documents it).
    from joulewise import paper_reported_energy
    function = getattr(paper_reported_energy, "estimate_phase_energy", None)
    if function is None:
        raise AnalysisError("Block-5 library lacks general estimate_phase_energy; shared-kernel scope addition required")
    repeats, quads, repeat_bounds, quad_bounds = [], {}, [], {}
    for row, energy, bound in zip(records, energies, bounds):
        if row["stratum"] == "repeat":
            repeats.append(energy)
            repeat_bounds.append(bound)
        else:
            quads.setdefault(row["unit_id"], []).append(energy)
            quad_bounds.setdefault(row["unit_id"], []).append(bound)
    return function(repeats, list(quads.values()), repeat_bounds, list(quad_bounds.values()))


def reduce_models(records, manifest, *, inclusive=False):
    if manifest.get("synthetic") is not True:
        raise AnalysisError("production R3 operative-bracket consumption join is not implemented; stored capture bounds cannot substitute")
    grouped = {}
    for row in records:
        grouped.setdefault((row["model"], row["pass_id"], row["session_id"]), []).append(row)
    model_specs = {m["model"]: m for m in manifest["models"]}
    session_specs = {s["session_id"]: s for s in manifest["sessions"]}
    rows = []
    for (model, pass_id, session_id), module in sorted(grouped.items()):
        kept, removed = _kept(module, inclusive)
        spec, session = model_specs[model], session_specs[session_id]
        duration = _weighted(kept, [r["duration_s"] for r in kept])
        reference = session["drift_reference"]
        for secondary in (False, True):
            rails = [r["rails_secondary_j"] if secondary else r["rails_j"] for r in kept]
            dc = [r["meter"]["secondary_j" if secondary else "gross_j"] for r in kept]
            clock = [r["meter"]["secondary_clock_j" if secondary else "gross_clock_j"] for r in kept]
            for boundary in BOUNDARIES:
                energies = rails if boundary == "rails" else dc if boundary == "DC input" else [d - r for d, r in zip(dc, rails)]
                gross_values = [r["rails_j"] if boundary == "rails" else r["meter"]["gross_j"]
                                if boundary == "DC input" else r["meter"]["gross_j"] - r["rails_j"] for r in kept]
                scale = 1.0 if reference["test7_passed"] else max(1.0,
                    _weighted(kept, gross_values) / number(reference["energy_j"][boundary], "E_ref", positive=True),
                    duration / number(reference["duration_s"], "T_ref", positive=True))
                drift = number(session["drift_allowance_j"][boundary], "drift allowance", nonnegative=True) * .5 * scale
                bounds = [{"E_clock_anchor_shift_bound_j": r["rails_anchor_j"] if boundary != "DC input" else 0.0,
                           "E_interpolation_joint_edge_bound_j": 0.0,
                           "E_whole_window_drift_allowance_j": drift} for r in kept]
                estimate = _registered_estimate(kept, energies, bounds)
                interval = estimate["interval"]
                h = student_t_quantile(1 - .05 / (2 * H1_CHECKS), interval["df"]) * math.sqrt(interval["variance"])
                clock_j = 0.0 if boundary == "rails" else _weighted(kept, clock)
                bound = interval["B_j"]
                mean = estimate["mean_j"]
                rows.append({"model": model, "pass_id": pass_id, "session_id": session_id,
                             "boundary": boundary, "basis": "idle-subtracted secondary" if secondary else "gross primary",
                             "selection": "flagged-inclusive" if inclusive else "primary",
                             "mean_j": mean, "lower_j": mean - h - bound - clock_j,
                             "upper_j": mean + h + bound + clock_j, "h_j": h, "B_j": bound,
                             "meter_clock_j": clock_j, "variance": interval["variance"], "df": interval["df"],
                             "duration_s": duration, "drift_scale": scale, "n_r": interval["n_r"], "n_b": interval["n_b"],
                             "removed_runs": removed, "flags": sorted({f for r in kept for f in r["flags"]}),
                             "attribution_floor_j": max(r["rails_anchor_j"] for r in kept) if boundary != "DC input" else 0.0,
                             "bytes": (spec["W_bytes"] + spec["KV_bytes"]) / 1e9,
                             "resident": spec["R_bytes"] / 1e9, "role": spec["role"], "moe": spec["moe"], "tier": spec["tier"]})
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
        n = len(group)
        point = {k: group[0][k] for k in ("model", "boundary", "basis", "selection", "bytes", "resident", "role", "moe", "tier")}
        mean = statistics.fmean(r["mean_j"] for r in group)
        # Independent sessions' sampling variances add; systematic allowances do not shrink.
        variance = math.fsum(r["variance"] for r in group) / n ** 2
        df = min(r["df"] for r in group)
        h = student_t_quantile(1 - .05 / (2 * H1_CHECKS), df) * math.sqrt(variance)
        bound, clock = (statistics.fmean(r[k] for r in group) for k in ("B_j", "meter_clock_j"))
        duration = statistics.fmean(r["duration_s"] for r in group)
        point.update(mean_j=mean, lower_j=mean - h - bound - clock, upper_j=mean + h + bound + clock,
                     h_j=h, B_j=bound, meter_clock_j=clock, duration_s=duration,
                     pass_values_j=[r["mean_j"] for r in group],
                     pass_difference_j=group[1]["mean_j"] - group[0]["mean_j"] if n == 2 else None,
                     e=mean / DECODE_STEPS, lower=(mean - h - bound - clock) / DECODE_STEPS,
                     upper=(mean + h + bound + clock) / DECODE_STEPS,
                     printed_j_per_output_token=mean / 512, output_label=OUTPUT_LABEL,
                     time=duration / DECODE_STEPS, power=mean / duration,
                     BW=point["bytes"] * DECODE_STEPS / duration)
        points.append(point)
    return points


def frozen_predictions(points, manifest):
    if any(p["role"] != "fit" for p in points):
        raise AnalysisError("held-out point passed into freeze")
    lines = []
    for selection, basis, boundary in itertools.product(("primary", "flagged-inclusive"),
            ("gross primary", "idle-subtracted secondary"), BOUNDARIES):
        subset = [p for p in points if (p["selection"], p["basis"], p["boundary"]) == (selection, basis, boundary)]
        lines.append({"selection": selection, "basis": basis, "boundary": boundary,
                      "lines": freeze_lines(subset)})
    return {"schema": SCHEMA, "manifest_sha256": digest(manifest), "H1_checks": H1_CHECKS,
            "H2_intervals": H2_INTERVALS, "fit_points": points, "rival_lines": lines,
            "tier_fit_inputs": [{k: p[k] for k in ("model", "boundary", "basis", "selection", "BW", "power")}
                                for p in points if p["tier"]],
            "note": "Dense held-out models test linearity over the format-derived bytes range; their small rival splits do not identify the hypothesis."}


def evaluate(points, frozen):
    h1_rows, moe_rows, h2_rows = [], [], []
    for group in frozen["rival_lines"]:
        key = tuple(group[k] for k in ("selection", "basis", "boundary"))
        subset = [p for p in points if tuple(p[k] for k in ("selection", "basis", "boundary")) == key]
        if len(subset) != 10:
            raise AnalysisError("held-out analysis requires all ten models")
        results = []
        for point in subset:
            result = h1_point(group["lines"], point)
            h1_rows.append({"model": point["model"], "role": point["role"],
                            **dict(zip(("selection", "basis", "boundary"), key)), **result})
            if point["moe"]:
                results.append((point["model"], result))
        moe_rows.append({**dict(zip(("selection", "basis", "boundary"), key)), **active_or_resident(results)})
        rails = {p["model"]: p["power"] for p in points if (p["selection"], p["basis"], p["boundary"]) == (*key[:2], "rails")}
        h2_rows.append({**dict(zip(("selection", "basis", "boundary"), key)), **h2(subset, rails)})
    return {"h1": h1_rows, "moe": moe_rows, "h2": h2_rows}


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
