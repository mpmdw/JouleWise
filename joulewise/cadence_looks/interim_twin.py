"""The parent side of the RL-181 interim twin handshake."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from joulewise.cadence_looks.interim_release import TRIPWIRES

SCHEMA = "joulewise.cadence_twin_comparison.v1"
CHANNELS = ("dc_in", "gpu_rail")
BASE_COLUMNS = ("p1", "p2", "a0", "a1", "a2")
HEAT_COLUMNS = ("k_tf08", "k_fan", "k_tv0h")
READINGS = ("tf08_c", "fan_rpm", "tv0h_excess_c")
VECTORS = ("columns", "coefficients", "fold_coefficients")
FIT_VECTORS = (*VECTORS, "fold_coefficients_no_heat")
FOLD_DROPS = "lodo/folds_delta_dropped"
FOLD_WORDS = ("lodo/hot/verdict", "lodo/no_heat/hot/verdict", FOLD_DROPS)
FIT_WORDS = ("passes", "fails", "not_evaluable")


def _require(value):
    if not value:
        raise ValueError("invalid twin comparison frame")


def _keys(value, keys):
    _require(type(value) is dict and value.keys() == set(keys))


def _unique(pairs):
    values = dict(pairs)
    _require(len(values) == len(pairs))
    return values


def _number(value):
    return type(value) in (float, int) and math.isfinite(value)


def _float(token):
    value = float(token)
    _require(math.isfinite(value))
    return value


def _select(result, tree, prefix, fields):
    for field in fields:
        value = tree
        for key in field.split("/"):
            value = value[key]
        result[f"{prefix}/{field}"] = value


def primary_projections(stage1, coefficients, fit, step3):
    vectors, coverage, words = {}, {}, {}
    _select(words, coefficients, "C#", ("delta_column", "qualified_interim_half/verdict"))
    _select(words, fit, "F#", ("qualified_interim_half/verdict",))
    _select(words, step3, "D#", ("tripwire/decision", "tripwire/trips"))
    _select(words, stage1, "S1#", (f"tripwires/{key}/trips" for key in TRIPWIRES))
    cells = step3["cells"]
    words["D#/cells"] = {str(row["prompt_tokens"]): {key: row[key] for key in ("status", "gamma_estimable")}
                         for row in cells}
    _require(len(words["D#/cells"]) == len(cells))
    for channel in CHANNELS:
        c, f = coefficients["channels"][channel], fit["channels"][channel]
        x, z = f"F#/channels/{channel}", f"C#/channels/{channel}"
        vectors[channel], coverage[channel] = {}, {}
        _select(vectors[channel], c, z, VECTORS)
        _select(vectors[channel], f, x, (*FIT_VECTORS, "marked_sensitivity/coefficients_without"))
        _select(words, f, x, ("qualified", *FOLD_WORDS))
        _select(coverage[channel], f, x, ("trace_coverage",))
        marked = f["marked_sensitivity"]["fit_without"]
        if marked is not None:
            y = f"{x}/marked_sensitivity/fit_without"
            _select(vectors[channel], marked, y, FIT_VECTORS)
            _select(words, marked, y, FOLD_WORDS)
            _select(coverage[channel], marked, y, ("trace_coverage",))
    return {"coefficients": vectors, "censored_fit": {"C#/onset": coefficients["onset"]},
            "verdicts": words, "trace_coverage": coverage,
            "soak_retries": {"F#/soak_retries": fit["soak_retries"], "S1#/soak_retries": stage1["soak_retries"]}}


def _same_shape(left, right):
    """Verify the types and names of a closed record, allowing different numbers."""
    if type(left) is dict:
        return type(right) is dict and left.keys() == right.keys() and all(
            _same_shape(left[key], right[key]) for key in left)
    if type(left) is list:
        return type(right) is list and len(left) == len(right) and all(
            _same_shape(a, b) for a, b in zip(left, right))
    if _number(left):
        return _number(right)
    return type(left) is type(right) and left == right


def _exact(left, right):
    if not _same_shape(left, right):
        return False
    return left == right


def _differences(left, right):
    if type(left) is dict and type(right) is dict:
        for key in left.keys() & right.keys():
            yield from _differences(left[key], right[key])
    elif type(left) is list and type(right) is list:
        for a, b in zip(left, right):
            yield from _differences(a, b)
    elif _number(left) and _number(right):
        scale = max(abs(left), abs(right))
        if scale == 0:
            yield 0.0
        else:
            difference = abs(left - right)
            yield difference / scale if math.isfinite(difference) else abs(left / scale - right / scale)


def _vector(vector, allowed):
    _keys(vector, allowed)
    _require(all(_number(value) for value in vector.values()))


def _vectors(record, prefix, days, unheated_columns, *, includes_no_heat=True):
    columns = record[f"{prefix}/columns"]
    _require(columns in (unheated_columns, [*unheated_columns, "delta"]))
    _vector(record[f"{prefix}/coefficients"], columns)
    folds = record[f"{prefix}/fold_coefficients"]
    _keys(folds, days)
    unheated = set(columns) - {"delta"}
    for vector in folds.values():
        # The full and each held-out onset can make different estimability decisions.
        _require(type(vector) is dict and vector.keys() in (unheated, unheated | {"delta"}))
        _vector(vector, vector.keys())
    if includes_no_heat:
        baseline = record[f"{prefix}/fold_coefficients_no_heat"]
        _keys(baseline, days)
        for vector in baseline.values():
            _vector(vector, BASE_COLUMNS)


def _onset(value, days, predictors):
    _keys(value, ("status", "predictors", "coefficients", "sigma_s", "folds", "lodo_rms_s", "count_only_cut"))
    _require(value["predictors"] == predictors)
    if value["status"] == "estimable":
        _vector(value["coefficients"], predictors)
        _require(_number(value["sigma_s"]) and value["sigma_s"] > 0)
    else:
        _require(value["status"] == "not_estimable" and value["coefficients"] is None
                 and value["sigma_s"] is None and value["lodo_rms_s"] is None)
    _keys(value["folds"], days)
    for fold in value["folds"].values():
        if fold is not None:
            _keys(fold, ("coefficients", "sigma_s"))
            _vector(fold["coefficients"], predictors)
            _require(_number(fold["sigma_s"]) and fold["sigma_s"] > 0)
    cut = value["count_only_cut"]
    _keys(cut, ("form", "offset_s", "fixed_s"))
    if value["lodo_rms_s"] is None:
        _require(_exact(cut, {"form": "fixed_116_s", "offset_s": None, "fixed_s": 116.0}))
    else:
        _require(_number(value["lodo_rms_s"]) and value["lodo_rms_s"] >= 0
                 and cut["form"] == "tau_hat_minus_2rms" and _number(cut["offset_s"]) and cut["fixed_s"] is None)


def _coverage(value, channel):
    _keys(value, ("min", "n_legs_under_0_99"))
    _require(_number(value["min"]) and value["min"] >= 0 and (channel == "gpu_rail" or value["min"] <= 1)
             and type(value["n_legs_under_0_99"]) is int and value["n_legs_under_0_99"] >= 0)


def _soak(value, span_ids):
    _keys(value, ("spans", "spans_with_retry", "retried_by_kind", "accepted_after_retry", "stopped_by_soak"))
    _keys(value["spans"], span_ids)
    _keys(value["retried_by_kind"], ("slope", "load", "kind not recorded"))
    counts = [value[key] for key in ("spans_with_retry", "accepted_after_retry", "stopped_by_soak")]
    counts.extend(value["retried_by_kind"].values())
    for row in value["spans"].values():
        _keys(row, ("attempts", "field_present", "accepted", "retried"))
        counts.append(row["attempts"])
        _require(type(row["field_present"]) is bool and type(row["accepted"]) is bool
                 and type(row["retried"]) is list)
        for retry in row["retried"]:
            _keys(retry, ("attempt", "kind", "read_from"))
            counts.append(retry["attempt"])
            _require(retry["kind"] in value["retried_by_kind"]
                     and retry["read_from"] in (None, "receipt soak_refusals[].kind",
                                                "receipt soak_attempts[].refusal_kind"))
    _require(all(type(count) is int and count >= 0 for count in counts))


def _validate_twin(twin, stage1, primary):
    words = twin["verdicts"]
    base_words = {"C#/delta_column", "D#/cells", "D#/tripwire/decision", "D#/tripwire/trips",
                  "C#/qualified_interim_half/verdict", "F#/qualified_interim_half/verdict",
                  *(f"S1#/tripwires/{key}/trips" for key in TRIPWIRES)}
    active = stage1["active_readings"]
    predictors = ["intercept", *(key for key in READINGS if active[key]["active"]), "t_p_s"]
    columns = [*BASE_COLUMNS, *(tail for key, tail in zip(READINGS, HEAT_COLUMNS) if active[key]["active"])]
    days = set(stage1["roster"]["fit_days"])
    unmarked_days = {leg["day"] for leg in stage1["legs"] if leg["in_energy_fit"] and not leg["marks"]}
    marked_states = []
    fold_words = []
    for channel in CHANNELS:
        x, z = f"F#/channels/{channel}", f"C#/channels/{channel}"
        y = f"{x}/marked_sensitivity/fit_without"
        vectors, coverage = twin["coefficients"][channel], twin["trace_coverage"][channel]
        mark = f"{x}/marked_sensitivity/coefficients_without"
        marked = vectors[mark] is not None
        marked_states.append(marked)
        _keys(vectors, [mark, *(f"{z}/{key}" for key in VECTORS),
                        *(f"{prefix}/{key}" for prefix in ((x, y) if marked else (x,)) for key in FIT_VECTORS)])
        _vectors(vectors, z, days, columns, includes_no_heat=False)
        _vectors(vectors, x, days, columns)
        base_words.update((f"{x}/qualified", *(f"{x}/{key}" for key in FOLD_WORDS)))
        _require(words[f"{x}/qualified"] == "not_run")
        fold_words.append((x, days))
        if marked:
            _vectors(vectors, y, unmarked_days, columns)
            _vector(vectors[mark], vectors[f"{y}/columns"])
            base_words.update(f"{y}/{key}" for key in FOLD_WORDS)
            fold_words.append((y, unmarked_days))
        _keys(coverage, [f"{prefix}/trace_coverage" for prefix in ((x, y) if marked else (x,))])
        for value in coverage.values():
            _coverage(value, channel)
    _require(marked_states[0] == marked_states[1])
    _keys(words, base_words)
    for prefix, fold_days in fold_words:
        dropped = words[f"{prefix}/{FOLD_DROPS}"]
        _require(type(dropped) is list and len(set(dropped)) == len(dropped) and set(dropped) <= fold_days
                 and all(words[f"{prefix}/{key}"] in FIT_WORDS for key in FOLD_WORDS[:2]))
    _require(all(words[f"{source}#/qualified_interim_half/verdict"] in FIT_WORDS for source in ("C", "F")))
    _require(words["C#/delta_column"] in ("kept", "dropped_onset_not_estimable"))
    _require(all(type(words[f"S1#/tripwires/{key}/trips"]) is bool for key in TRIPWIRES))
    _require(words["D#/tripwire/decision"] in ("within", "to the research lead", "not_evaluable")
             and (words["D#/tripwire/trips"] is None or type(words["D#/tripwire/trips"]) is bool))
    cells = words["D#/cells"]
    # Membership belongs to the exact comparison. A well-formed extra cell is a disagreement.
    _require(type(cells) is dict)
    for key, cell in cells.items():
        _require(re.fullmatch(r"[1-9][0-9]*", key) is not None)
        _keys(cell, ("status", "gamma_estimable"))
        _require(cell["status"] in ("ok", "not_run")
                 and (cell["gamma_estimable"] is None or type(cell["gamma_estimable"]) is bool))
    _keys(twin["censored_fit"], ("C#/onset",))
    _onset(twin["censored_fit"]["C#/onset"], days, predictors)
    _keys(twin["soak_retries"], ("F#/soak_retries", "S1#/soak_retries"))
    for value in twin["soak_retries"].values():
        _soak(value, primary["soak_retries"]["S1#/soak_retries"]["spans"])


def compare(raw, stage1, coefficients, fit, step3):
    """Authenticate the child's primary projection and adjudicate the complete frame."""
    _require(raw.endswith(b"\n") and raw.count(b"\n") == 1)
    frame = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_float, parse_float=_float)
    primary = primary_projections(stage1, coefficients, fit, step3)
    maxima_keys = (*CHANNELS, "censored_fit")
    _keys(frame, ("schema", "max_relative_difference", *primary))
    _require(frame["schema"] == SCHEMA)
    _keys(frame["max_relative_difference"], maxima_keys)
    _require(all(value is None or (_number(value) and value >= 0)
                 for value in frame["max_relative_difference"].values()))

    def verify(pair, expected):
        _keys(pair, ("primary", "twin"))
        _require(_exact(pair["primary"], expected))
        return pair["twin"]

    twin = {}
    for field in ("coefficients", "trace_coverage"):
        _keys(frame[field], CHANNELS)
        twin[field] = {ch: verify(frame[field][ch], primary[field][ch]) for ch in CHANNELS}
    for field in ("censored_fit", "verdicts", "soak_retries"):
        twin[field] = verify(frame[field], primary[field])
    _validate_twin(twin, stage1, primary)
    maxima = {}
    agrees = all(_exact(primary[key], twin[key]) for key in ("verdicts", "trace_coverage", "soak_retries"))
    for name in maxima_keys:
        left, right = ((primary["coefficients"][name], twin["coefficients"][name]) if name in CHANNELS
                       else (primary[name], twin[name]))
        maxima[name] = max(_differences(left, right), default=None)
        tolerance = 1e-8 if name in CHANNELS else 1e-6
        agrees &= _same_shape(left, right) and (maxima[name] is None or maxima[name] <= tolerance)
    frame["max_relative_difference"] = maxima
    frame["agreement"] = "yes" if agrees else "no"
    return frame


def _relative(left, right):
    _require(_number(left) and _number(right))
    scale = max(abs(left), abs(right))
    if not scale:
        return 0.0
    distance = abs(left - right)
    return distance / scale if math.isfinite(distance) else abs(left / scale - right / scale)


def post_no(stage1, fit, energy, frame):
    """RL-184 §3.4 diagnostics under the private boundary. The comparison word is fixed."""
    from joulewise.cadence_looks import fit_interim as F

    _require(frame["agreement"] == "no")
    legs = [leg for leg in stage1["legs"] if leg["in_energy_fit"]]
    onsets = {side: frame["censored_fit"][side]["C#/onset"] for side in ("primary", "twin")}

    def estimates(leg, vector, onset):
        model = F._onset_model(onset, onsets["primary"]["predictors"])
        timing = F._onsets((leg,), model).get(leg["leg_key"])
        return [math.fsum(a * b for a, b in zip(F._design_row(leg, seg, seg["kind"], vector, timing), vector.values()))
                for seg in leg["segments"]]

    fits = []
    sides = ("primary", "twin")
    onset_differences = []
    comparable_onsets = True
    for leg in legs:
        for held_out in (False, True):
            day = leg["day"]
            selected = {side: onsets[side]["folds"][day] if held_out else onsets[side] for side in sides}
            models = [F._onset_model(selected[side], onsets[side]["predictors"]) for side in sides]
            if all(value is not None for value in models):
                onset_differences.append(_relative(*(max(0.0, F.linear_predictor(leg, model)) for model in models)))
            else:
                comparable_onsets &= all(value is None for value in models)
            for channel in CHANNELS:
                projection = frame["coefficients"][channel]
                key = f"C#/channels/{channel}/" + ("fold_coefficients" if held_out else "coefficients")
                vectors = [projection[side][key][day] if held_out else projection[side][key] for side in sides]
                fits.append(_relative(*(math.fsum(estimates(leg, vector, selected[side]))
                                        for side, vector in zip(sides, vectors))))
    onset_max = max(onset_differences, default=0.0) if comparable_onsets else None
    fit_max = max(fits)

    primary, twin = (frame["verdicts"][side] for side in sides)
    disagreements = {key for key in primary.keys() | twin.keys() if primary.get(key) != twin.get(key)}
    hot_keys = {"F#/channels/gpu_rail/lodo/hot/verdict", "C#/qualified_interim_half/verdict",
                "F#/qualified_interim_half/verdict"}
    boundary = False
    if disagreements and disagreements <= hot_keys and all({primary[key], twin[key]} == {"passes", "fails"}
                                                             for key in disagreements):
        hot = {}
        folds = frame["coefficients"]["gpu_rail"]["twin"]["C#/channels/gpu_rail/fold_coefficients"]
        for leg in legs:
            indices = [i for i, seg in enumerate(leg["segments"]) if seg["hot"]]
            if indices:
                day = leg["day"]
                values = estimates(leg, folds[day], onsets["twin"]["folds"][day])
                responses = energy["legs"][leg["leg_key"]]["gpu_rail"]["segments"]
                hot.setdefault(day, []).append((math.fsum(values[i] for i in indices),
                                                math.fsum(responses[i] for i in indices)))
        counted = [values for values in hot.values() if len(values) >= F.MIN_HOT_LEGS_PER_DAY]
        a = fit["qualified_interim_half"]["value"]
        if len(counted) >= F.MIN_COUNTED_DAYS and _number(a):
            b = max(abs((math.fsum(p for p, _ in values) - math.fsum(y for _, y in values)) /
                        math.fsum(y for _, y in values)) for values in counted)
            boundary = (_relative(a, b) <= 1e-8 and all(abs(value - F.QUALIFIED_THRESHOLD) <= 1e-12 for value in (a, b)))
    return {"fitted_values_max_relative_difference": fit_max, "predicted_onsets_max_relative_difference": onset_max,
            "predictions_within_tolerances": fit_max <= 1e-8 and onset_max is not None and onset_max <= 1e-6,
            "verdicts_within_boundary": boundary}


def _retain_stdout(data):
    if data:
        with os.fdopen(os.dup(1), "wb") as private_stdout:
            private_stdout.write(data)


def run(path, *, manifest, manifest_sha, commit, stage1_path, stage1_sha, custody, overrides,
        restricted, coefficient_sha, deadline, stage1, coefficients, fit, step3, wrapper):
    """Launch the verified child once, through its pin-checking wrapper. Stderr inherits the reserved descriptor.

    RL-194 condition 4: ``wrapper`` (scripts/cadence_interim_twin_pins.py) checks every roster file against the
    look's pins with its own code and then becomes the reviewed child ``path``, byte-identical, with the arguments
    below untouched. The wrapper reads the pin list from the manifest it is given; there is no other."""
    argv = [sys.executable, "-I", "-B", str(wrapper)]
    argv += ["--manifest", str(Path(manifest).resolve()), "--manifest-sha256", manifest_sha,
            "--ledger-commit", commit, "--stage1", str(Path(stage1_path).resolve()), "--stage1-sha256", stage1_sha,
            "--custody", str(Path(custody).resolve())]
    del path                                # the wrapper finds the child by the manifest's own pin
    for span_id, location in overrides:
        argv.extend(("--span-dir", f"{span_id}={location}"))
    argv.extend(("--coefficients", str(restricted / "coefficients.json"), "--coefficients-sha256", coefficient_sha,
                 "--fit", str(restricted / "fit.json"), "--step3", str(restricted / "step3.json")))
    fallback = {"agreement": "not_evaluable"}
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return fallback
    try:
        child = subprocess.run(argv, stdout=subprocess.PIPE, timeout=remaining, check=False)
    except subprocess.TimeoutExpired as error:
        _retain_stdout(error.output)
        return fallback
    except OSError:
        return fallback
    _retain_stdout(child.stdout)
    if child.returncode:
        return fallback
    try:
        return compare(child.stdout, stage1, coefficients, fit, step3)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
        return fallback
