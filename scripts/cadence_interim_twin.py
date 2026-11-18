#!/usr/bin/env python3
"""Independent lm-interim-01 arithmetic and isolated child output boundary.

The parent owns reservation, descriptor capture, the comparison decision,
and all result files. This child only opens inputs and emits one frame.
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True

import argparse
from bisect import bisect_left, bisect_right
import builtins
from collections import Counter
import csv
from dataclasses import dataclass, replace
import hashlib
import io
import json
import math
import os
from pathlib import Path
import plistlib
import re
from types import ModuleType


CHANNELS = {"gpu_rail", "dc_in"}
BASE_COLUMNS = ("p1", "p2", "a0", "a1", "a2")
COMPARISON_SCHEMA = "joulewise.cadence_twin_comparison.v1"
TRIPWIRES = ("dev_included_below_45", "days_below_4", "cell_below_10",
             "start_reading_invalid_over_10pct", "hp01_below_9")
READINGS = {"tf08_c": "k_tf08", "fan_rpm": "k_fan", "tv0h_excess_c": "k_tv0h"}
COEFFICIENT_KEYS = {
    "schema", "look_id", "synthetic", "manifest_sha256", "stage1_sha256", "fit_sha256",
    "code_sha256", "numpy_version", "block_tokens", "prefix", "rates", "centring",
    "calibrated_range", "active_readings", "onset", "delta_column", "channels",
    "qualified_interim_half",
}
BUILTIN_ERRORS = {value: name for name, value in vars(builtins).items()
                  if isinstance(value, type) and issubclass(value, BaseException) and name == value.__name__}
DECODER_PATH = "joulewise/external/km003c_parse.py"
DECODER_PACKAGE_PATH = "joulewise/external/__init__.py"
METER_PERIODS = {0: 0.5, 1: 0.1, 2: 0.02, 3: 0.001}
SQRT_TWO = math.sqrt(2)
LOG_SQRT_TWO_PI = math.log(2 * math.pi) / 2


@dataclass(frozen=True)
class FitLeg:
    """Decoded counts, timestamps in seconds, and active centred readings."""

    day: str
    prompt_tokens: int
    readings: tuple[float, ...]
    turn_start_s: float
    first_token_s: float
    decode_tokens: int
    last_token_s: float
    start_out_of_state: bool = False


@dataclass(frozen=True)
class OnsetFit:
    coefficients: tuple[float, ...]
    sigma_s: float

    def mean(self, readings, prefill_s):
        return math.fsum(a * b for a, b in zip(
            self.coefficients, (1, *readings, prefill_s), strict=True,
        ))


@dataclass(frozen=True)
class OnsetRow:
    day: str
    cell: str
    readings: tuple[float, ...]
    prefill_s: float
    end_s: float
    observed: bool


class RankDeficient(ValueError):
    """A sensitivity fit can be unavailable even with valid inputs."""


def token_rates(legs):
    """RL-166 Q5 and RL-166a R-1, using all included development legs."""
    legs = tuple(legs)
    if not legs or any(
        leg.prompt_tokens <= 0 or leg.decode_tokens < 2
        or not all(map(math.isfinite, (leg.turn_start_s, leg.first_token_s, leg.last_token_s)))
        or not leg.turn_start_s < leg.first_token_s < leg.last_token_s
        for leg in legs
    ):
        raise ValueError("invalid rate roster")
    return (
        sum(leg.prompt_tokens for leg in legs)
        / math.fsum(leg.first_token_s - leg.turn_start_s for leg in legs),
        sum(leg.decode_tokens - 1 for leg in legs)
        / math.fsum(leg.last_token_s - leg.first_token_s for leg in legs),
    )


def expected_hot_seconds(start, end, mean, sigma):
    """RL-166b B-1. Split off the linear part to reduce tail cancellation."""
    def normal_antiderivative_tail(x):
        return math.exp(-0.5 * x * x - LOG_SQRT_TWO_PI) + x * math.erfc(-x / SQRT_TWO) / 2

    if sigma < 1e-6:
        return max(0, end - max(start, mean))
    overlap = max(0, end - max(start, mean))
    left = -abs((start - mean) / sigma)
    right = -abs((end - mean) / sigma)
    correction = sigma * (normal_antiderivative_tail(right) - normal_antiderivative_tail(left))
    return min(end - start, max(0, overlap + correction))


def design_rows(leg, rates, active_columns, onset=None):
    """Count-clock prefill and decode segments, including a prefix tail."""
    prefill_rate, decode_rate = rates
    prompt = leg.prompt_tokens
    prefill = prompt / prefill_rate
    columns = BASE_COLUMNS + tuple(active_columns) + (("delta",) if onset else ())
    if len(active_columns) != len(leg.readings):
        raise ValueError("start readings do not match the active columns")
    mean = onset.mean(leg.readings, prefill) if onset and not leg.start_out_of_state else None

    def temperature_columns(start, end):
        ramp = (end - start) * (start + end) / 2
        readings = tuple(ramp * reading for reading in leg.readings)
        if onset is None:
            return readings
        hot = end - start if mean is None else expected_hot_seconds(start, end, mean, onset.sigma_s)
        return (*readings, hot)

    rows = [(prompt, prompt**2, 0, 0, 0, *temperature_columns(0, prefill))]
    left = 0
    for last_token in range(255, leg.decode_tokens + 255, 256):
        right = min(last_token, leg.decode_tokens - 1)
        if right == left:
            break
        count = right - left
        context = prompt + (left + 1 + right) / 2
        start = prefill + left / decode_rate
        end = prefill + right / decode_rate
        rows.append((0, 0, count, count * context, count * prompt, *temperature_columns(start, end)))
        left = right
        if right == leg.decode_tokens - 1:
            break
    return columns, rows


def fit_channel(columns, design, response):
    """RL-166 Q2 and RL-166b B-6. Solve in RMS-scaled units."""
    import numpy as np

    matrix = np.asarray(design, dtype=float)
    response = np.asarray(response, dtype=float)
    if matrix.shape != (len(response), len(columns)) or response.ndim != 1:
        raise ValueError("inconsistent energy design")
    if not np.isfinite(matrix).all() or not np.isfinite(response).all():
        raise ValueError("invalid energy rows")
    if matrix.shape[0] < matrix.shape[1]:
        raise RankDeficient("insufficient energy rows")
    scales = np.sqrt(np.mean(matrix**2, axis=0))
    if np.any(scales == 0):
        raise RankDeficient("empty energy column")
    left, singular, right = np.linalg.svd(matrix / scales, full_matrices=False)
    if singular[-1] < 1e-10 * singular[0]:
        raise RankDeficient("rank-deficient energy design")
    solution = right.T @ ((left.T @ response) / singular)
    return dict(zip(columns, (float(value) for value in solution / scales), strict=True))


def predict(leg, rates, active_columns, coefficients, onset=None):
    """Return turn heat and the segment predictions on the count clock."""
    columns, rows = design_rows(leg, rates, active_columns, onset)
    weights = tuple(coefficients[name] for name in columns)
    contributions = [tuple(a * b for a, b in zip(row, weights, strict=True)) for row in rows]
    heat = math.fsum(value for row in contributions for value in row[len(BASE_COLUMNS):])
    return heat, [math.fsum(row) for row in contributions]


def _cdf_terms(x):
    """Return log Φ, its derivative, and the negative second derivative."""
    log_density = -0.5 * x * x - LOG_SQRT_TWO_PI
    if x >= -10:
        log_cdf = math.log(math.erfc(-x / SQRT_TWO) / 2)
        slope = math.exp(log_density - log_cdf)
        return log_cdf, slope, slope * (x + slope)

    # The normal Mills ratio has a continued fraction in the far left tail.
    # Retaining the remainder gives the curvature even when x + slope rounds to zero.
    remainder = 0.0
    for order in range(24, 0, -1):
        remainder = order / (remainder - x)
    slope = remainder - x
    return log_density - math.log(slope), slope, slope * remainder


def censored_normal(design, end_s, observed):
    """Right-censored normal MLE in the scaled Olsen coordinates (B-5).

    The caller supplies the registered, eligible onset rows. A missing estimate
    signals that the registered convergence test could not be met.
    """
    import numpy as np

    x, y = np.asarray(design, dtype=float), np.asarray(end_s, dtype=float)
    seen = np.asarray(observed, dtype=bool)
    count = int(seen.sum())
    if x.ndim != 2 or y.ndim != 1 or seen.shape != y.shape or len(x) != len(y) or count == 0:
        return None
    x_scale = np.sqrt(np.mean(x**2, axis=0))
    y_scale = float(np.sqrt(np.mean(y**2)))
    if (not np.isfinite(x_scale).all() or not math.isfinite(y_scale)
            or np.any(x_scale == 0) or y_scale == 0):
        return None
    x, y = x / x_scale, y / y_scale
    transform = np.column_stack((x, -y))
    exact, censored = transform[seen], transform[~seen]
    beta = np.linalg.lstsq(x[seen], y[seen], rcond=None)[0]
    scatter = float(np.linalg.norm(y[seen] - x[seen] @ beta) / math.sqrt(count))
    initial_scale = scatter if scatter >= 1e-6 else 1.0
    point = np.append(beta, 1) / initial_scale

    def evaluate(at):
        eta = float(at[-1])
        errors = exact @ at
        gradient = exact.T @ errors
        information = exact.T @ exact
        loss = float(errors @ errors) / 2 - count * math.log(eta)
        gradient[-1] -= count / eta
        information[-1, -1] += count / eta**2
        for row, value in zip(censored, censored @ at, strict=True):
            log_cdf, slope, curvature = _cdf_terms(float(value))
            loss -= log_cdf
            gradient -= row * slope
            information += np.outer(row, row) * curvature
        return loss, gradient, information

    for _ in range(200):
        loss, gradient, information = evaluate(point)
        try:
            step = np.linalg.solve(information, gradient)
        except np.linalg.LinAlgError:
            break
        decrement = float(gradient @ step)
        if not math.isfinite(decrement) or decrement <= 1e-20:
            break
        # Compare with a small rounding allowance once the loss stops resolving
        # Newton improvements. The final point still has to pass B-5.
        for power in range(45):
            fraction = 2.0**-power
            candidate = point - fraction * step
            if candidate[-1] > 0 and np.isfinite(candidate).all():
                candidate_loss, _, _ = evaluate(candidate)
                if candidate_loss <= loss - 1e-4 * fraction * decrement + 2 * math.ulp(loss):
                    break
        else:
            break
        if np.array_equal(candidate, point):
            break
        point = candidate

    _, gradient, information = evaluate(point)
    if not np.isfinite(information).all() or not np.isfinite(gradient).all():
        return None
    spectrum = np.linalg.eigvalsh(information)
    if spectrum[0] <= 0 or spectrum[-1] > 1e10 * spectrum[0]:
        return None
    decrement = float(gradient @ np.linalg.solve(information, gradient))
    if not 0 <= decrement <= 1e-8:
        return None
    sigma = y_scale / float(point[-1])
    return OnsetFit(tuple(float(value) for value in sigma * point[:-1] / x_scale), sigma)


def fit_onset(rows, *, held_out_day=None, sensitivity=False):
    """Apply the main or leave-one-day-out onset gate (B-3 and B-4)."""
    training = [row for row in rows if row.day != held_out_day]
    observed = [row for row in training if row.observed]
    cells = Counter(row.cell for row in observed)
    if held_out_day is None and not sensitivity:
        enough = (len(observed) >= 12 and len({row.day for row in observed}) >= 3
                  and sum(count >= 4 for count in cells.values()) >= 2)
    else:
        enough = len(observed) >= 6 and sum(count >= 2 for count in cells.values()) >= 2
    if not enough:
        return None
    return censored_normal(
        [(1, *row.readings, row.prefill_s) for row in training],
        [row.end_s for row in training],
        [row.observed for row in training],
    )


def fit_channels(legs, rates, active_columns, responses, onset, *, exclude_day=None):
    """Fit both channels on the same full or held-out roster.

    Each response vector follows the sequence of decoded legs and each leg's
    prefill and decode segments. The caller supplies the corresponding onset
    fit. A marked-span diagnostic takes its own subset of legs and responses.
    """
    if not legs or responses.keys() != CHANNELS or any(len(y) != len(legs) for y in responses.values()):
        raise ValueError("channel roster mismatch")
    design = []
    selected = {channel: [] for channel in responses}
    for index, leg in enumerate(legs):
        if leg.day == exclude_day:
            continue
        columns, rows = design_rows(leg, rates, active_columns, onset)
        design.extend(rows)
        for channel, response in responses.items():
            if len(response[index]) != len(rows):
                raise ValueError("channel segment mismatch")
            selected[channel].extend(response[index])
    if not design:
        raise ValueError("no training legs")
    return {channel: fit_channel(columns, design, response) for channel, response in selected.items()}


def dc_segment(timestamps, samples, start, end):
    """RL-166 Q2, with endpoints interpolated and RL-173 E.1's hole bound."""
    if (len(timestamps) != len(samples) or len(timestamps) < 2
            or not all(map(math.isfinite, timestamps)) or not all(map(math.isfinite, samples))
            or any(a > b for a, b in zip(timestamps, timestamps[1:]))):
        raise ValueError("invalid DC-in samples or segment")
    return dc_trapezoids(timestamps, samples, start, end)


def dc_trapezoids(timestamps, samples, start, end):
    if not timestamps or not timestamps[0] <= start <= end <= timestamps[-1]:
        raise ValueError("DC-in samples do not bracket the segment")
    if start == end:
        return 0.0
    lo, hi = bisect_right(timestamps, start) - 1, bisect_left(timestamps, end)
    pieces = []
    for i in range(lo, hi):
        left_time, right_time = timestamps[i:i + 2]
        duration = right_time - left_time
        if duration > 2:
            raise ValueError("DC-in segment intersects a trace hole")
        if duration == 0:
            continue
        left, right = max(start, left_time), min(end, right_time)
        slope = (samples[i + 1] - samples[i]) / duration
        left_value = samples[i] + slope * (left - left_time)
        right_value = samples[i] + slope * (right - left_time)
        pieces.append((left_value + right_value) * (right - left) / 2)
    return math.fsum(pieces)


def trace_coverage(leg_fractions):
    """RL-173 E, for one channel's independently computed leg fractions."""
    values = tuple(leg_fractions)
    if not values or any(not 0 <= value <= 1 for value in values):
        raise ValueError("invalid leg coverage")
    return min(values), sum(value < 0.99 for value in values)


def interim_verdict(day_hot_totals):
    """RL-166 Q3, with one predicted/measured pair per leg with hot blocks."""
    errors = []
    for totals in day_hot_totals.values():
        if len(totals) >= 3:
            measured = math.fsum(value for _, value in totals)
            predicted = math.fsum(value for value, _ in totals)
            if measured <= 0:
                raise ValueError("nonpositive measured hot total")
            errors.append(abs(predicted - measured) / measured)
    if len(errors) < 3:
        return "not_evaluable"
    return "passes" if max(errors) <= 0.02 else "fails"


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("invalid child arguments")


def child_arguments(argv):
    parser = _ArgumentParser(add_help=False, allow_abbrev=False)
    for role in ("manifest", "stage1", "custody", "coefficients", "fit", "step3"):
        parser.add_argument(f"--{role}", type=Path, required=True)
    for role in ("manifest", "stage1", "coefficients"):
        parser.add_argument(f"--{role}-sha256", required=True)
    parser.add_argument("--ledger-commit", required=True)
    parser.add_argument("--span-dir", action="append", default=[])
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{40}", args.ledger_commit):
        raise ValueError("invalid ledger commit identity")
    return args


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate input field")
        result[key] = value
    return result


def finite(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite input")
    return number


def decode_json(data):
    return json.loads(data, object_pairs_hook=unique_object, parse_float=finite, parse_constant=finite)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_bound(path, sha256):
    data = path.read_bytes()
    if digest(data) != sha256:
        raise ValueError("input digest mismatch")
    return data


def child_path(directory, relative):
    if Path(relative).is_absolute():
        raise ValueError("absolute child path")
    resolved = (directory / relative).resolve(strict=True)
    if not resolved.is_relative_to(directory):
        raise ValueError("input escapes its declared directory")
    return resolved


def verify_pins(manifest, code_path):
    repository = code_path.parents[1]
    fit = manifest["fit"]
    pins = [fit["twin"], *fit["code"], *fit["dependencies"], fit["step3"]["code"],
            fit["step3"]["adapter"], manifest["stages"]["stage1"]["schema"],
            manifest["freeze2"]["schema"], manifest["outputs"]["schema"]]
    if child_path(repository, fit["twin"]["path"]) != code_path:
        raise ValueError("manifest names another twin")
    if not {DECODER_PATH, DECODER_PACKAGE_PATH} <= {pin["path"] for pin in fit["dependencies"]}:
        raise ValueError("meter decoder pins absent")
    decoder = None
    for pin in pins:
        path = child_path(repository, pin["path"])
        data = read_bound(path, pin["sha256"])
        if pin["path"] == DECODER_PATH:
            decoder = (path, data)
    return decoder


def meter_decoder(verified):
    path, data = verified
    module = ModuleType("_cadence_twin_km003c")
    module.__file__ = str(path)
    def import_decoder_dependency(name, globals=None, locals=None, fromlist=(), level=0):
        if level or name.partition(".")[0] not in sys.stdlib_module_names:
            raise ImportError("meter decoder dependency is outside the allowed standard library")
        return builtins.__import__(name, globals, locals, fromlist)

    module.__dict__["__builtins__"] = {**vars(builtins), "__import__": import_decoder_dependency}
    sys.modules[module.__name__] = module
    exec(compile(data, str(path), "exec", dont_inherit=True), module.__dict__)
    return module.parse


def select_paths(view, prefix, fields):
    result = {}
    for field in fields:
        value = view
        for key in field.split("/"):
            value = value[key]
        result[f"{prefix}/{field}"] = value
    return result


def channel_projections(c, f, channel):
    x, z = f"F#/channels/{channel}", f"C#/channels/{channel}"
    vectors = ("columns", "coefficients", "fold_coefficients")
    fit_fields = (*vectors, "fold_coefficients_no_heat")
    verdict_fields = ("lodo/hot/verdict", "lodo/no_heat/hot/verdict", "lodo/folds_delta_dropped")
    coefficients = select_paths(c, z, vectors) | select_paths(f, x, fit_fields)
    coefficients.update(select_paths(f, x, ("marked_sensitivity/coefficients_without",)))
    verdicts = select_paths(f, x, ("qualified", *verdict_fields))
    coverage = select_paths(f, x, ("trace_coverage",))
    marked = f["marked_sensitivity"]["fit_without"]
    if marked is not None:
        y = f"{x}/marked_sensitivity/fit_without"
        coefficients.update(select_paths(marked, y, fit_fields))
        verdicts.update(select_paths(marked, y, verdict_fields))
        coverage.update(select_paths(marked, y, ("trace_coverage",)))
    return coefficients, verdicts, coverage


def projections(stage1, c, f, step3):
    coefficients, coverage = {}, {}
    verdicts = select_paths(c, "C#", ("delta_column", "qualified_interim_half/verdict"))
    verdicts.update(select_paths(f, "F#", ("qualified_interim_half/verdict",)))
    verdicts.update(select_paths(step3, "D#", ("tripwire/decision", "tripwire/trips")))
    verdicts.update(select_paths(stage1, "S1#", (f"tripwires/{key}/trips" for key in TRIPWIRES)))
    for channel in sorted(CHANNELS):
        coefficients[channel], words, coverage[channel] = channel_projections(
            c["channels"][channel], f["channels"][channel], channel,
        )
        verdicts.update(words)
    cells = {}
    for cell in step3["cells"]:
        key = str(cell["prompt_tokens"])
        if key in cells:
            raise ValueError("duplicate Step 3 cell")
        cells[key] = {field: cell[field] for field in ("status", "gamma_estimable")}
    verdicts["D#/cells"] = cells
    return {
        "coefficients": coefficients,
        "censored_fit": {"C#/onset": c["onset"]},
        "verdicts": verdicts,
        "trace_coverage": coverage,
        "soak_retries": {"F#/soak_retries": f["soak_retries"], "S1#/soak_retries": stage1["soak_retries"]},
    }


def relative_differences(left, right):
    if type(left) is dict and type(right) is dict:
        for key in left.keys() & right.keys():
            yield from relative_differences(left[key], right[key])
    elif type(left) is list and type(right) is list:
        for a, b in zip(left, right):
            yield from relative_differences(a, b)
    elif type(left) in (int, float) and type(right) in (int, float):
        scale = max(abs(left), abs(right))
        difference = abs(left - right)
        if not scale:
            yield 0.0
        elif math.isfinite(difference):
            yield difference / scale
        else:
            yield abs(left / scale - right / scale)


def comparison_frame(primary, twin):
    def pair(primary_values, twin_values):
        return {"primary": primary_values, "twin": twin_values}

    frame = {"schema": COMPARISON_SCHEMA}
    for field in ("coefficients", "trace_coverage"):
        frame[field] = {c: pair(primary[field][c], twin[field][c]) for c in sorted(CHANNELS)}
    for field in ("censored_fit", "verdicts", "soak_retries"):
        frame[field] = pair(primary[field], twin[field])
    numeric = frame["coefficients"] | {"censored_fit": frame["censored_fit"]}
    frame["max_relative_difference"] = {
        field: max(relative_differences(values["primary"], values["twin"]), default=None)
        for field, values in numeric.items()
    }
    return frame


def failure_name(error):
    cls = type(error)
    if cls is json.JSONDecodeError:
        return "JSONDecodeError"
    linear_algebra = sys.modules.get("numpy.linalg")
    if cls is getattr(linear_algebra, "LinAlgError", None):
        return "LinAlgError"
    return BUILTIN_ERRORS.get(cls, "OtherError")


def run_child(evaluate):
    """Suppress incidental writes and send one protocol frame to the parent."""
    sys.dont_write_bytecode = True
    output, error = os.dup(1), os.dup(2)
    with open(os.devnull, "wb") as discard:
        os.dup2(discard.fileno(), 1)
        os.dup2(discard.fileno(), 2)
    try:
        if not sys.flags.isolated:
            raise ValueError("isolated interpreter required")
        frame = json.dumps(evaluate(), allow_nan=False, sort_keys=True, separators=(",", ":"))
        with os.fdopen(output, "wb") as stream:
            stream.write(frame.encode("utf-8") + b"\n")
    except BaseException as exc:
        os.write(error, f"stage2_error\n{failure_name(exc)}\n".encode("ascii"))
        os._exit(1)
    os._exit(0)


def fit_leg(record, active, centring):
    start = record["start"]
    segments = record["segments"]
    return FitLeg(
        record["day"], record["prefill_tokens"],
        tuple(start[name] - centring[name] for name in active),
        segments[0]["wall_start_s"], segments[0]["wall_end_s"], record["decode_tokens"],
        segments[-1]["wall_end_s"], start["state"] == "start_out_of_state",
    )


def onset_roster(records, legs, rates):
    rows = []
    for record, leg in zip(records, legs, strict=True):
        state = record["state"]
        use = state["onset_use"]
        if use in ("uncensored", "censored"):
            observed = use == "uncensored"
            rows.append(OnsetRow(leg.day, record["cell_prompt_tokens"], leg.readings,
                                 leg.prompt_tokens / rates[0],
                                 state["first_off_s" if observed else "censored_at_s"], observed))
    return rows


def onset_projection(rows, days, active, model, folds):
    predictors = ["intercept", *active, "t_p_s"]

    def serialize(value):
        if value is None:
            return None
        return {"coefficients": dict(zip(predictors, value.coefficients, strict=True)), "sigma_s": value.sigma_s}

    errors = []
    if model is not None:
        for row in rows:
            estimate = folds[row.day]
            if row.observed and estimate is not None:
                tau = max(0.0, estimate.mean(row.readings, row.prefill_s))
                errors.append((tau - row.end_s)**2)
    rms = math.sqrt(math.fsum(errors) / len(errors)) if errors else None
    cut = ({"form": "fixed_116_s", "fixed_s": 116.0, "offset_s": None} if rms is None else
           {"form": "tau_hat_minus_2rms", "fixed_s": None, "offset_s": 2 * rms})
    return {
        "status": "estimable" if model is not None else "not_estimable",
        "predictors": predictors,
        **(serialize(model) or {"coefficients": None, "sigma_s": None}),
        "folds": {day: serialize(folds[day]) for day in days},
        "lodo_rms_s": rms,
        "count_only_cut": cut,
    }


def hot_totals(predictions, response, segments):
    selected = [(prediction, measured) for prediction, measured, segment in
                zip(predictions, response, segments, strict=True) if segment["hot"]]
    if not selected:
        return None
    return tuple(math.fsum(values) for values in zip(*selected, strict=True))


def fit_projection(records, readings, centring, rates, days, response_records, *, sensitivity=False):
    legs = [fit_leg(record, readings, centring) for record in records]
    active = tuple(READINGS[reading] for reading in readings)
    onset_rows = onset_roster(records, legs, rates)
    main = fit_onset(onset_rows, sensitivity=sensitivity)
    onsets = {day: fit_onset(onset_rows, held_out_day=day) for day in days}
    responses = {channel: [data[channel]["segments"] for data in response_records] for channel in sorted(CHANNELS)}
    full = fit_channels(legs, rates, active, responses, main)
    base_legs = [replace(leg, readings=()) for leg in legs]
    folds, base = {}, {}
    with_heat, no_heat = {c: {} for c in CHANNELS}, {c: {} for c in CHANNELS}
    for day in days:
        folds[day] = fit_channels(legs, rates, active, responses, onsets[day], exclude_day=day)
        base[day] = fit_channels(base_legs, rates, (), responses, None, exclude_day=day)
        for channel in CHANNELS:
            hot, baseline = [], []
            for index, leg in enumerate(legs):
                if leg.day != day:
                    continue
                segments = records[index]["segments"]
                response = responses[channel][index]
                prediction = predict(leg, rates, active, folds[day][channel], onsets[day])[1]
                base_prediction = predict(base_legs[index], rates, (), base[day][channel])[1]
                total = hot_totals(prediction, response, segments)
                if total is not None:
                    hot.append(total)
                    baseline.append(hot_totals(base_prediction, response, segments))
            with_heat[channel][day], no_heat[channel][day] = hot, baseline

    channels = {}
    for channel in CHANNELS:
        low, count = trace_coverage(data[channel]["coverage_min"] for data in response_records)
        channels[channel] = {
            "columns": list(full[channel]), "coefficients": full[channel],
            "fold_coefficients": {day: folds[day][channel] for day in days},
            "fold_coefficients_no_heat": {day: base[day][channel] for day in days},
            "qualified": "not_run",
            "lodo": {
                "hot": {"verdict": interim_verdict(with_heat[channel])},
                "no_heat": {"hot": {"verdict": interim_verdict(no_heat[channel])}},
                "folds_delta_dropped": [day for day in days if onsets[day] is None],
            },
            "trace_coverage": {"min": low, "n_legs_under_0_99": count},
        }
    return {
        "channels": channels,
        "onset": onset_projection(onset_rows, days, readings, main, onsets),
        "delta_column": "kept" if main is not None else "dropped_onset_not_estimable",
        "qualified_interim_half": channels["gpu_rail"]["lodo"]["hot"],
    }


def recompute_fit(stage1, fit_records, response_records, marked_spans):
    active = tuple(name for name in READINGS if stage1["active_readings"][name]["active"])
    rates = stage1["rates"]["r_p"], stage1["rates"]["r_d"]
    centring = stage1["centring"]
    fit = fit_projection(fit_records, active, centring, rates, stage1["roster"]["fit_days"], response_records)
    unmarked = [(record, response) for record, response in zip(fit_records, response_records, strict=True)
                if record["span_id"] not in marked_spans]
    without = None
    if 0 < len(unmarked) < len(fit_records):
        kept_records, responses = zip(*unmarked, strict=True)
        days = [day for day in stage1["roster"]["fit_days"] if any(r["day"] == day for r in kept_records)]
        if len(days) > 1:
            try:
                without = fit_projection(kept_records, active, centring, rates, days, responses, sensitivity=True)
            except RankDeficient:
                pass
    for channel in CHANNELS:
        variant = without["channels"][channel] if without is not None else None
        fit["channels"][channel]["marked_sensitivity"] = {
            "coefficients_without": variant["coefficients"] if variant is not None else None,
            "fit_without": variant,
        }
    return fit


def span_dirs(root, overrides, spans):
    root = root.resolve(strict=True)
    requested = {}
    for raw in overrides:
        key, has_equal, value = raw.partition("=")
        if not has_equal or not value or key in requested or key not in spans:
            raise ValueError("invalid span override")
        requested[key] = Path(value).resolve(strict=True)
    return {span: requested[span] if span in requested else child_path(root, span) for span in spans}


def json_lines(data):
    return [decode_json(line) for line in data.splitlines() if line.strip()]


def gpu_fields(data):
    rows = csv.DictReader(io.StringIO(data.decode("utf-8")))
    return (row for row in rows if row["source"] == "powermetrics" and row["rail"] == "gpu_power")


def gpu_time_digest(data):
    pairs = []
    for row in gpu_fields(data):
        left, right, _ = (finite(row[k]) for k in ("interval_start_s", "interval_end_s", "timestamp_s"))
        pairs.append([left, right])
    return digest(json.dumps(sorted(pairs)).encode("utf-8"))


def gpu_rows(data):
    rows = []
    for row in gpu_fields(data):
        left, right, stamp, power = (finite(row[k]) for k in
                                    ("interval_start_s", "interval_end_s", "timestamp_s", "power_w"))
        if left >= right:
            raise ValueError("invalid GPU support interval")
        rows.append((left, right, stamp, power))
    if not rows:
        raise ValueError("GPU trace is empty")
    return sorted(rows)


def power_intervals(rows, start, end):
    """Cut recorded GPU intervals at the segment's wall-clock bounds."""
    if start > end:
        raise ValueError("invalid wall-clock segment")
    if start == end:
        return 0.0, None
    pieces = []
    width, rightmost = 0.0, start
    for left, right, _, power in rows:
        if right <= start:
            continue
        if left >= end:
            break
        left, right = max(left, start), min(right, end)
        if left - rightmost > 2:
            raise ValueError("GPU trace hole")
        # Intersect with the uncovered support, so no sample interval is counted twice.
        overlap = right - max(left, rightmost)
        if overlap > 0:
            pieces.append(power * overlap)
            width += overlap
            rightmost = right
    if end - rightmost > 2 or not pieces:
        raise ValueError("GPU trace does not support the segment")
    return math.fsum(pieces), min(1.0, width / (end - start))


METER_HEADER_KEYS = frozenset("k schema status reason rate_idx sps poll_s start_raw_ns start_real_ns start_mono_ns".split())
METER_TRAILER_KEYS = frozenset("k polls empties bad usb_errors elapsed_s end_raw_ns end_mono_ns stop_reason".split())


def meter_stream_paths(span):
    directory = span / "hazards" / "meter"
    if any(directory.glob("stream-*.jsonl.zst")):
        raise ValueError("compressed meter input")
    streams = sorted(directory.glob("stream-*.jsonl"))
    for path in streams:
        child_path(span, path.relative_to(span))
    return streams


def meter_time_digest(streams):
    """Stage-1 time identity. Project raw counters without decoding watts or clocks."""
    combined = hashlib.sha256()
    for name, data in streams:
        header = trailer = None
        polls, errors = [], 0
        lines = data.decode("utf-8").split("\n")
        for index, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("meter row is not an object")
            except ValueError:
                errors += index < len(lines) - 1
                continue
            kind = row.get("k")
            if kind == "h":
                header = {key: row[key] for key in row.keys() & METER_HEADER_KEYS}
            elif kind == "t":
                trailer = {key: row[key] for key in row.keys() & METER_TRAILER_KEYS}
            elif kind == "e":
                errors += 1
            elif kind == "b":
                try:
                    payload = bytes.fromhex(row.get("p") or "")
                except (TypeError, ValueError):
                    payload = b""
                counters = [int.from_bytes(payload[i:i + 2], "little") for i in range(0, len(payload) - 19, 20)]
                polls.append([row.get(key) for key in ("tx", "rx", "rt", "n")] + [counters])
        combined.update(json.dumps([name, header, trailer, errors], sort_keys=True).encode("utf-8"))
        for poll in polls:
            combined.update(json.dumps(poll).encode("utf-8"))
    return combined.hexdigest()


def native_time_digest(rich, native):
    rich_fields = (rb'"timestamp_s":\s*(-?[0-9][0-9.eE+-]*)', rb'"elapsed_ns":\s*([0-9]+)')
    native_fields = (rb'<key>elapsed_ns</key>\s*<integer>([0-9]+)</integer>',
                     rb'<key>thermal_pressure</key>\s*<string>([^<]*)</string>')

    def capture(pattern, content, convert):
        found = re.search(pattern, content)
        return convert(found[1]) if found else None

    rows = [[capture(pattern, line, bytes.decode) for pattern in rich_fields]
            for line in rich.split(b"\n") if line.strip()]
    frames = [frame for frame in native.split(b"\0") if frame.strip()]
    states = [[capture(native_fields[0], frame, bytes.decode), capture(native_fields[1], frame, bytes.hex)]
              for frame in frames[:len(rows)]]
    return digest(json.dumps([rows, states, len(frames)], sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8"))


def coverage_intervals(intervals, start, end):
    if end <= start:
        return None
    rightmost, covered = start, 0.0
    for left, right in intervals:
        if left >= end:
            break
        edge = min(right, end)
        length = edge - max(left, rightmost)
        if length > 0:
            covered += length
            rightmost = edge
    return covered / (end - start)


def sample_coverage(timestamps, period, start, end):
    half = period / 2
    first = bisect_left(timestamps, start - half)
    support = ((timestamps[i] - half, timestamps[i] + half) for i in range(first, len(timestamps)))
    return coverage_intervals(support, start, end)


def pooled_meter(streams, parse):
    samples, period = [], 0.0
    for path in streams:
        stream = parse(path)
        if not stream.present or not stream.aligned:
            continue
        header = stream.header
        if type(header["start_real_ns"]) is not int or type(header["start_raw_ns"]) is not int:
            raise ValueError("meter epoch anchor is invalid")
        offset = header["start_real_ns"] - header["start_raw_ns"]
        period = max(period, METER_PERIODS[header["rate_idx"]])
        samples.extend(((raw + offset) / 1e9, finite(watts)) for raw, watts in
                       zip(stream.host_ns, stream.watts, strict=True))
    samples.sort(key=lambda row: row[0])
    times, watts = map(tuple, zip(*samples, strict=True)) if samples else ((), ())

    def measure(start, end):
        return dc_trapezoids(times, watts, start, end), sample_coverage(times, period, start, end)

    return measure


def responses_for_leg(record, gpu, dc_segment_reader):
    output = {}
    for channel, measure in (("gpu_rail", lambda u, v: power_intervals(gpu, u, v)),
                             ("dc_in", dc_segment_reader)):
        samples = [measure(segment["wall_start_s"], segment["wall_end_s"]) for segment in record["segments"]]
        tails = {str(tail["prefix_len"]): measure(tail["wall_start_s"], tail["wall_end_s"])[0]
                 for tail in record["prefix_tails"]}
        output[channel] = {"segments": [energy for energy, _ in samples], "prefix_tails": tails,
                           "coverage_min": min((value for _, value in samples if value is not None), default=1.0)}
    return output


SOAK_KINDS = ("slope", "load", "kind not recorded")


def span_soak(receipt):
    if "soak_attempts" not in receipt:
        return {"attempts": 1, "field_present": False, "accepted": True, "retried": []}
    attempts = receipt["soak_attempts"]
    if not attempts or [row["attempt"] for row in attempts] != list(range(1, len(attempts) + 1)):
        raise ValueError("invalid soak attempts")
    distinct = {}
    for row in receipt.get("soak_refusals", []):
        number, kind = row["attempt"], row["kind"]
        if number in distinct or kind not in SOAK_KINDS[:2] or not 1 <= number <= len(attempts):
            raise ValueError("invalid soak refusal")
        distinct[number] = kind
    retried = []
    for row in attempts[:-1]:
        number = row["attempt"]
        if number in distinct:
            kind, source = distinct[number], "receipt soak_refusals[].kind"
        elif row.get("refusal_kind") is not None:
            kind, source = row["refusal_kind"], "receipt soak_attempts[].refusal_kind"
        else:
            kind, source = "kind not recorded", None
        if kind not in SOAK_KINDS:
            raise ValueError("unknown soak refusal kind")
        retried.append({"attempt": number, "kind": kind, "read_from": source})
    final = attempts[-1]
    name = "soak" if len(attempts) == 1 else f"soak.a{len(attempts)}"
    steps = [step for step in receipt["steps"] if step["name"] == name]
    if len(steps) != 1:
        raise ValueError("missing or repeated final soak step")
    accepted = final["refused"] is None and steps[0]["rc"] == 0
    return {"attempts": len(attempts), "field_present": True, "accepted": accepted, "retried": retried}


def soak_summary(receipts):
    spans = {key: span_soak(value) for key, value in receipts.items()}
    counts = Counter(row["kind"] for span in spans.values() for row in span["retried"])
    return {
        "spans": spans,
        "spans_with_retry": sum(bool(span["retried"]) for span in spans.values()),
        "retried_by_kind": {kind: counts[kind] for kind in SOAK_KINDS},
        "accepted_after_retry": sum(bool(span["retried"]) and span["accepted"] for span in spans.values()),
        "stopped_by_soak": sum(not span["accepted"] for span in spans.values()),
    }


def matched_step3_blocks(legs):
    by_block = {}
    for leg in legs:
        for block, temperature, joules in leg:
            by_block.setdefault(block, []).append((temperature, math.log(joules)))
    return [rows for rows in by_block.values() if len(rows) > 1]


def mean_centered_slope(legs):
    """Step 3(ii), eliminate the block-index fixed effects before fitting gamma."""
    numerators, denominators = [], []
    for rows in matched_step3_blocks(legs):
        mean_temp, mean_log = (math.fsum(values) / len(rows) for values in zip(*rows, strict=True))
        for temp, log_joules in rows:
            numerators.append((temp - mean_temp) * (log_joules - mean_log))
            denominators.append((temp - mean_temp)**2)
    denominator = math.fsum(denominators)
    return math.fsum(numerators) / denominator if denominator > 0 else None


def step3_drift(legs):
    """Largest absolute eligible gamma times the median Automatic TV0h rise."""
    from statistics import median

    all_rows = [rows for _, _, rows in legs]
    matched = matched_step3_blocks(all_rows)
    if not any(round(max(t for t, _ in rows) - min(t for t, _ in rows), 3) >= 2 for rows in matched):
        return False, None
    automatic = [(rise, rows) for high_power, rise, rows in legs if not high_power]
    rises = [rise for rise, _ in automatic if rise is not None]
    if not rises:
        return True, None
    slopes = [mean_centered_slope(all_rows), mean_centered_slope([rows for _, rows in automatic])]
    for i in range(len(legs)):
        slopes.append(mean_centered_slope([rows for _, _, rows in (*legs[:i], *legs[i + 1:])]))
    return True, round(max(abs(value) for value in slopes if value is not None) * median(rises), 8)


def step3_projection(cells, threshold):
    rows, drifts = [], []
    for cell, measurements in sorted(cells.items(), key=lambda item: (item[0] != 10000, item[0])):
        failures, legs = measurements
        if not failures and not legs:
            continue
        if failures > 2 or not legs:
            rows.append({"prompt_tokens": cell, "status": "not_run", "gamma_estimable": None})
            continue
        estimable, drift = step3_drift(legs)
        rows.append({"prompt_tokens": cell, "status": "ok", "gamma_estimable": estimable})
        if drift is not None and estimable:
            drifts.append(drift)
    trips = max(drifts) > threshold if drifts else None
    decision = "not_evaluable" if trips is None else "to the research lead" if trips else "within"
    return {"cells": rows, "tripwire": {"decision": decision, "trips": trips}}


def primary_identity(c, args, stage1):
    if c.keys() != COEFFICIENT_KEYS or c["channels"].keys() != CHANNELS:
        raise ValueError("coefficient object differs from its registered fields")
    if (c["look_id"], c["manifest_sha256"], c["stage1_sha256"], c["numpy_version"], c["synthetic"]) != (
        stage1["look_id"], args.manifest_sha256, args.stage1_sha256, stage1["numpy_version"], stage1["synthetic"],
    ):
        raise ValueError("coefficient object belongs to another look")
    expected_onset = stage1["onset"]
    for key in ("status", "predictors", "coefficients", "sigma_s", "count_only_cut"):
        if c["onset"][key] != expected_onset[key]:
            raise ValueError("coefficient onset does not match committed stage 1")
    lodo = expected_onset["lodo"]
    if c["onset"]["lodo_rms_s"] != (lodo["rms_s"] if lodo is not None else None):
        raise ValueError("coefficient onset error does not match committed stage 1")


def child_frame(args):
    import numpy as np

    manifest = decode_json(read_bound(args.manifest, args.manifest_sha256))
    stage1 = decode_json(read_bound(args.stage1, args.stage1_sha256))
    decoder_pin = verify_pins(manifest, Path(__file__).resolve())
    if manifest["look_id"] != "lm-interim-01" or stage1["look_id"] != manifest["look_id"]:
        raise ValueError("wrong look identity")
    if stage1["manifest_sha256"] != args.manifest_sha256 or stage1["numpy_version"] != np.__version__:
        raise ValueError("stage-1 inputs or interpreter differ from the committed look")
    coefficient_bytes = read_bound(args.coefficients, args.coefficients_sha256)
    fit = decode_json(args.fit.read_bytes())
    step3 = decode_json(args.step3.read_bytes())
    threshold, = (row["threshold"] for row in manifest["decisions"] if row["id"] == "drift_tripwire")
    if step3["tripwire"]["threshold_applied"] != threshold:
        raise ValueError("primary Step 3 threshold differs from the manifest")
    own_fit, own_step3 = recompute_bundle(args, stage1, fit["custody"], step3["custody"], decoder_pin, threshold)
    coefficients = decode_json(coefficient_bytes)
    primary_identity(coefficients, args, stage1)
    primary_projection = projections(stage1, coefficients, fit, step3)
    own_stage1 = {**stage1, "soak_retries": own_fit["soak_retries"]}
    twin_projection = projections(own_stage1, own_fit, own_fit, own_step3)
    return comparison_frame(primary_projection, twin_projection)


def step3_records(events_data, turns_data, journal_data, rich_data, native_data):
    """Decode the independent Step 3 inputs without retaining synthetic token IDs."""
    (turn,) = json_lines(turns_data)
    start, end = turn["start_stamp"]["epoch_s"], turn["end_stamp"]["epoch_s"]
    count = len(turn["generation"]["output_token_ids"])
    tokens = {}
    for row in json_lines(events_data):
        metadata = row.get("metadata", {})
        if "index" not in metadata or "align_turn_index" not in metadata:
            continue
        index = metadata["index"]
        if type(index) is not int or not 0 <= index < count or index in tokens:
            raise ValueError("invalid Step 3 token index")
        tokens[index] = row["timestamp_s"]
    token_times = [tokens[i] for i in range(count)]
    if not token_times or not start <= token_times[0] <= token_times[-1] <= end or any(
        a >= b for a, b in zip(token_times, token_times[1:])
    ):
        raise ValueError("invalid Step 3 token times")

    journal = []
    for row in json_lines(journal_data):
        if row.get("kind") != "reading" or row.get("error") or not row.get("values"):
            continue
        journal.append((row["finished"]["wall_ns"] / 1e9, row["started"]["monotonic_ns"],
                        row["values"]["sensors"].get("TV0h"), row["values"]["status"]))
    native = (frame for frame in native_data.split(b"\0") if frame.strip())
    power_state = []
    for frame, raw_bytes in zip(json_lines(rich_data), native):
        raw = plistlib.loads(raw_bytes)
        if frame["elapsed_ns"] != raw["elapsed_ns"]:
            raise ValueError("Step 3 telemetry intervals disagree")
        states = [(state["freq"], state["used_ns"]) for state in frame["gpu"]["dvfm_states"]]
        power_state.append((frame["timestamp_s"], frame["elapsed_ns"], raw["thermal_pressure"], states))
    if not journal or not power_state:
        raise ValueError("Step 3 telemetry is empty")
    return start, end, token_times, sorted(journal, key=lambda row: row[0]), power_state


def step3_cut(start, token_times, journal, power_state):
    """RL-150 §1.3 guarded wall time before applying the token-index cut."""
    end = token_times[-1]

    def fresh(row):
        _, started, _, status = row
        observed = status["pm_observed_ns"]
        return (type(status["os_level"]) is int and status["pm_state"] not in (None, "Unknown")
                and type(observed) is int and 0 <= started - observed <= 2_000_000_000)

    def off(status):
        return (type(status["os_level"]) is int and status["os_level"] > 0
                or status["pm_state"] not in (None, "Nominal", "Unknown"))

    carry = next((row for row in reversed(journal) if row[0] <= start), None)
    if carry is None or start - carry[0] > 2 or not fresh(carry) or off(carry[3]):
        return None
    anchors = [carry[0], *(row[0] for row in journal if start < row[0] <= end and fresh(row)), end]
    cuts = [end]
    gap = next((a for a, b in zip(anchors, anchors[1:]) if b - a > 2), None)
    if gap is not None:
        cuts.append(gap)
    off_time = min((*(row[0] for row in journal if start < row[0] <= end and off(row[3])),
                    *(row[0] for row in power_state if start < row[0] <= end
                      and row[2] not in (None, "Nominal", "Unknown"))), default=None)
    if off_time is not None:
        last_nominal = max((row[0] for row in journal if row[0] < off_time and fresh(row) and not off(row[3])),
                           default=start)
        cuts.append(min(last_nominal, off_time - 2))

    # Apply the e20 rule only to windows beginning at least 10 s into decode.
    # Scale active time by each row's overlap with the window.
    reference = max((freq for _, _, _, states in power_state for freq, used in states if used > 0), default=0)
    intervals = []
    for right, elapsed, _, states in sorted(power_state, key=lambda row: row[0]):
        if elapsed <= 0:
            raise ValueError("invalid Step 3 sampling period")
        left = right - elapsed / 1e9
        intervals.append((left, right, math.fsum(used for _, used in states),
                          math.fsum(freq * used for freq, used in states)))
        begin = right - 10
        if not token_times[0] + 10 <= begin < right <= end:
            continue
        weights, numerators = [], []
        for lo, hi, used, frequency_time in reversed(intervals):
            if hi <= begin:
                break
            scale = (hi - max(lo, begin)) / (hi - lo)
            weights.append(scale * used)
            numerators.append(scale * frequency_time)
        total = math.fsum(weights)
        if total and math.fsum(numerators) < 0.97 * reference * total:
            cuts.append(begin)
            break
    return min(cuts)


def step3_temperature(journal, time):
    return next((temperature for stamp, _, temperature, _ in reversed(journal)
                 if stamp <= time and temperature is not None), None)


def step3_observations(start, tokens, journal, power, gpu):
    cut = step3_cut(start, tokens, journal, power)
    if cut is None:
        return False, None, []
    prefix = bisect_right(tokens, cut)
    first, last = step3_temperature(journal, tokens[0]), step3_temperature(journal, cut)
    rise = last - first if first is not None and last is not None else None
    observations = []
    for block in range(1, prefix // 256):
        left, right = tokens[256 * block - 1], tokens[256 * block + 255]
        readings = [temperature for stamp, _, temperature, _ in journal
                    if left < stamp <= right and temperature is not None]
        temperature = math.fsum(readings) / len(readings) if readings else step3_temperature(journal, (left + right) / 2)
        if temperature is not None:
            joules, _ = power_intervals(gpu, left, right)
            if joules <= 0:
                raise ValueError("nonpositive Step 3 block response")
            observations.append((block, temperature, joules))
    # All admitted development legs in the interim adapter are Automatic.
    return False, rise, observations


def step3_measurements(bundle):
    sources = ("events.jsonl", "outputs/align_turns.jsonl", "outputs/align_thermal.jsonl",
               "rich_telemetry.jsonl", "raw/powermetrics.plist")
    start, _, tokens, journal, power = step3_records(*(child_path(bundle, name).read_bytes() for name in sources))
    gpu = gpu_rows(child_path(bundle, "power_trace.csv").read_bytes())
    return step3_observations(start, tokens, journal, power, gpu)



OPERATIONAL_BUNDLE_FILES = (
    "events.jsonl", "outputs/align_turns.jsonl", "outputs/align_thermal.jsonl", "config.json",
    "outputs/align_runtime_events.jsonl", "align_runtime_events.jsonl",
)


def present_file(span, name):
    path = span / name
    if path.with_name(path.name + ".zst").is_file():
        raise ValueError("compressed custody input")
    if path.is_file():
        return child_path(span, name)
    return None


def span_identities(span):
    receipt_path = child_path(span, "runner_receipt.json")
    receipt = decode_json(receipt_path.read_bytes())
    roster = receipt["roster"]
    if not isinstance(roster, list) or len(set(roster)) != len(roster):
        raise ValueError("invalid runner receipt roster")
    names = {"runner_receipt.json", "soak/soak_reference.json"}
    bundles = {}
    for leg in roster:
        if not leg or Path(leg).name != leg or leg in (".", ".."):
            raise ValueError("invalid receipt leg ID")
        prefix = f"legs/{leg}"
        record_name = f"{prefix}/leg_record.json"
        names.update((record_name, f"{prefix}/leg_summary.json"))
        record_path = present_file(span, record_name)
        if record_path is None:
            continue
        record = decode_json(record_path.read_bytes())
        bundle = (record.get("result") or {}).get("bundle")
        if not bundle or record.get("spec", {}).get("leg_type") == "T":
            continue
        if Path(bundle).name != bundle or bundle in (".", ".."):
            raise ValueError("invalid runtime bundle name")
        relative = f"{prefix}/runtime/{bundle}"
        bundles[leg] = relative
        names.update(f"{relative}/{suffix}" for suffix in OPERATIONAL_BUNDLE_FILES)

    raw_files = {}
    for name in sorted(names):
        path = present_file(span, name)
        if path is not None:
            raw_files[name] = file_digest(path)
    native_time = {}
    for relative in bundles.values():
        rich = present_file(span, f"{relative}/rich_telemetry.jsonl")
        native = present_file(span, f"{relative}/raw/powermetrics.plist")
        if rich is not None and native is not None:
            native_time[relative] = native_time_digest(rich.read_bytes(), native.read_bytes())
    return receipt, bundles, raw_files, native_time


def verified_span_inputs(span, identity):
    receipt, bundles, operational, native = span_identities(span)
    if identity["files_sha256"] != operational or identity["native_pm_sha256"] != native:
        raise ValueError("stage-1 span identities differ from custody")
    streams = meter_stream_paths(span)
    expected = identity["meter_time_sha256"]
    if expected is not None and expected != meter_time_digest((path.name, path.read_bytes()) for path in streams):
        raise ValueError("stage-1 meter time identity differs from custody")
    return receipt, bundles, streams


def check_custody_inventory(root, spans, *inventories):
    seen = {}
    for inventory in inventories:
        for file in inventory["files"]:
            path = Path(file["path"])
            resolved = (root / path).resolve(strict=True)
            if not any(resolved.is_relative_to(span) for span in spans):
                raise ValueError("comparison input outside named spans")
            if resolved.suffix == ".zst" or resolved.with_name(resolved.name + ".zst").is_file():
                raise ValueError("compressed comparison input")
            sha256 = file["sha256"]
            if resolved in seen and seen[resolved] != sha256:
                raise ValueError("inconsistent comparison input identities")
            if resolved not in seen:
                if file_digest(resolved) != sha256:
                    raise ValueError("comparison input digest mismatch")
                seen[resolved] = sha256


def gpu_input(span, bundle):
    name = f"{bundle}/power_trace.csv"
    path = present_file(span, name)
    if path is None:
        raise FileNotFoundError("missing GPU trace")
    return path


def recompute_bundle(args, stage1, fit_identity, step3_identity, decoder_pin, threshold):
    roster = stage1["roster"]["spans"]
    span_records = {row["span_id"]: row for row in roster}
    if len(span_records) != len(roster):
        raise ValueError("duplicate span ID")
    directories = span_dirs(args.custody, args.span_dir, span_records)
    parse = meter_decoder(decoder_pin)
    check_custody_inventory(args.custody.resolve(), directories.values(), fit_identity, step3_identity)
    receipts, bundle_paths, streams = {}, {}, {}
    for key, row in span_records.items():
        receipts[key], bundle_paths[key], streams[key] = verified_span_inputs(directories[key], row["custody"])
    fit_legs = [row for row in stage1["legs"] if row["in_energy_fit"]]
    step3_legs = [row for row in stage1["legs"] if row["included"] and row["role"] == "fit" and row["leg_type"] == "A"]
    known_bundles = {}
    for row in stage1["legs"]:
        if row["leg_type"] == "T":
            if row["in_energy_fit"]:
                raise ValueError("type-T leg in response roster")
            continue
        key, slash, tag = row["leg_key"].partition("/")
        if not slash or key != row["span_id"] or row["leg_key"] in known_bundles:
            raise ValueError("invalid stage-1 leg identity")
        relative = bundle_paths[key].get(tag)
        known_bundles[row["leg_key"]] = relative
        gpu_identity = (row.get("trace_holes") or {}).get("gpu_rail", {}).get("rows_sha256")
        if gpu_identity is not None:
            if relative is None or gpu_identity != gpu_time_digest(gpu_input(directories[key], relative).read_bytes()):
                raise ValueError("stage-1 GPU time identity differs from custody")
        elif row["in_energy_fit"]:
            raise ValueError("GPU time identity required for fit")

    dc_readers = {}
    responses = []
    for row in fit_legs:
        key = row["span_id"]
        if span_records[key]["custody"]["meter_time_sha256"] is None:
            raise ValueError("meter time identity required for fit")
        if key not in dc_readers:
            dc_readers[key] = pooled_meter(streams[key], parse)
        bundle = known_bundles[row["leg_key"]]
        gpu = gpu_rows(gpu_input(directories[key], bundle).read_bytes())
        responses.append(responses_for_leg(row, gpu, dc_readers[key]))
    marked = {key for key, row in span_records.items() if row["marks"]}
    fit = recompute_fit(stage1, fit_legs, responses, marked)
    fit["soak_retries"] = soak_summary(receipts)
    cells = {}
    for row in step3_legs:
        size = row["cell_prompt_tokens"]
        failures, legs = cells.setdefault(size, (0, []))
        try:
            relative = known_bundles[row["leg_key"]]
            if relative is None:
                raise ValueError("no accepted Step 3 bundle")
            span = directories[row["span_id"]]
            bundle = child_path(span, relative)
            legs.append(step3_measurements(bundle))
        except (OSError, KeyError, TypeError, IndexError, ValueError, plistlib.InvalidFileException):
            cells[size] = (failures + 1, legs)
    return fit, step3_projection(cells, threshold)


if __name__ == "__main__":
    run_child(lambda: child_frame(child_arguments(sys.argv[1:])))
