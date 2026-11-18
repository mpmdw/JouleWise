#!/usr/bin/env python3
"""Independent lm-interim-01 arithmetic and isolated child output boundary.

The functions below take decoded values. The parent-to-child argument and
record layout needs a published synthetic spec before the direct entry point
can evaluate a bundle. See the run report for the missing interface clauses.
"""

from __future__ import annotations

from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import sys


CHANNELS = {"gpu_rail", "dc_in"}
BASE_COLUMNS = ("p1", "p2", "a0", "a1", "a2")
COMPARISONS = {
    "coefficients": 1e-8,
    "censored_fit": 1e-6,
    "verdicts": 0,
    "trace_coverage": 0,
    "soak_retries": 0,
}
WORDS = {word: (word + "\n").encode("ascii") for word in ("yes", "no", "not_evaluable")}
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
    if matrix.shape[0] < matrix.shape[1] or not np.isfinite(matrix).all() or not np.isfinite(response).all():
        raise ValueError("insufficient or invalid energy rows")
    scales = np.sqrt(np.mean(matrix**2, axis=0))
    if np.any(scales == 0):
        raise ValueError("empty energy column")
    left, singular, right = np.linalg.svd(matrix / scales, full_matrices=False)
    if singular[-1] < 1e-10 * singular[0]:
        raise ValueError("rank-deficient energy design")
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


def fit_onset(rows, *, held_out_day=None):
    """Apply the main or leave-one-day-out onset gate (B-3 and B-4)."""
    training = [row for row in rows if row.day != held_out_day]
    observed = [row for row in training if row.observed]
    cells = Counter(row.cell for row in observed)
    if held_out_day is None:
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
            or not timestamps[0] <= start < end <= timestamps[-1]
            or any(a >= b for a, b in zip(timestamps, timestamps[1:]))):
        raise ValueError("invalid DC-in samples or segment")
    pieces = []
    for i in range(bisect_right(timestamps, start) - 1, len(timestamps) - 1):
        left_time, right_time = timestamps[i:i + 2]
        if left_time >= end:
            break
        duration = right_time - left_time
        if duration > 2:
            raise ValueError("DC-in segment intersects a trace hole")
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


def _equal(left, right, tolerance):
    if type(left) is dict and type(right) is dict:
        return left.keys() == right.keys() and all(_equal(left[k], right[k], tolerance) for k in left)
    if type(left) is list and type(right) is list:
        return len(left) == len(right) and all(_equal(a, b, tolerance) for a, b in zip(left, right))
    if type(left) in (int, float) and type(right) in (int, float):
        return math.isclose(left, right, rel_tol=tolerance, abs_tol=0) if tolerance else left == right
    return type(left) is type(right) and left == right


def compare(twin, primary):
    """Compare normalized values under RL-180 amendment 2."""
    try:
        def normalize(record):
            for field in ("coefficients", "trace_coverage", "verdicts"):
                if not CHANNELS <= record[field].keys():
                    raise ValueError("missing channel")
            # Reject non-finite numbers and use the same representation for
            # arrays read from JSON and tuples returned by the calculations.
            return json.loads(json.dumps({field: record[field] for field in COMPARISONS}, allow_nan=False))

        left, right = normalize(twin), normalize(primary)
        matches = all(_equal(left[field], right[field], tolerance)
                      for field, tolerance in COMPARISONS.items())
    except (AttributeError, KeyError, OverflowError, TypeError, ValueError):
        return "not_evaluable"
    return "yes" if matches else "no"


def _write_result(restricted, twin, word):
    payload = (json.dumps({"agreement": word, "twin": twin}, allow_nan=False,
                          sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    directory = os.open(restricted, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fd = os.open("twin.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
    finally:
        os.close(directory)


def run_child(restricted: Path, evaluate):
    """Run a child evaluator behind a file-descriptor boundary and exit."""
    output = os.dup(1)
    discard = os.open(os.devnull, os.O_WRONLY)
    os.dup2(discard, 1)
    os.dup2(discard, 2)
    os.close(discard)
    word = "not_evaluable"
    try:
        if sys.flags.isolated:
            twin, primary = evaluate()
            word = compare(twin, primary)
            if word != "not_evaluable":
                _write_result(restricted, twin, word)
    except BaseException:
        word = "not_evaluable"
    try:
        os.write(output, WORDS[word])
    finally:
        # Standard descriptors stay muted through interpreter shutdown.
        os._exit(0)


if __name__ == "__main__":
    os.write(1, WORDS["not_evaluable"])
