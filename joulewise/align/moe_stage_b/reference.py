"""Independent stdlib numerical oracle for synthetic MoE Stage B checks.

Implementation provenance:
- Written without viewing production Stage B code.
- Shared input contract: joulewise.align.records.RouterLog.
- Each token/layer selection is one atomic request, in log.layers order.
- Over-capacity requests stream every selected nonresident expert and leave
  cache contents and recency unchanged.
- Review-round updates follow the pinned max_batch=32 source rule: small
  prefill batches mutate cache, large batches bypass updates. Revised by this
  fix seat; these revisions are not a new independent-model derivation.
- Synthetic calculations only; these functions are not hardware measurements.
"""

from __future__ import annotations

from cmath import exp
from dataclasses import dataclass
from math import fsum, hypot, inf, isfinite, pi, sqrt
from statistics import NormalDist
from typing import Literal, Mapping, Protocol, Sequence

from joulewise.align.records import PowerTrace, RouterLog

ExpertKey = tuple[int, int]
TransferRectangle = tuple[int, int, float]  # start_ns, end_ns, energy_j
LoadRectangle = tuple[int, int, float]  # start_ns, end_ns, watts


class ReferenceConfig(Protocol):
    expert_bytes: Mapping[int, int]
    resident: frozenset[ExpertKey]
    cache_capacity_bytes: int
    cache_policy: Literal["none", "lru", "slru"]
    prefill_mode: Literal["bypass", "serial"]
    prefill_batch_tokens: int
    joules_per_byte: float
    bandwidth_bytes_s: float


@dataclass(frozen=True)
class ReferenceTransfer:
    moved_bytes: int
    energy_j: float


@dataclass(frozen=True)
class ReferenceCorrelationRequirement:
    minimum_correlation: float
    possible: bool


def _integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def reference_transfers(
    log: RouterLog, config: ReferenceConfig
) -> tuple[ReferenceTransfer, ...]:
    """Compute bytes and joules per token using explicit ordered cache lists.

    Resident weights occupy no space in this offload cache. An expert selected
    more than once within one request is fetched once. Bandwidth is validated
    for config compatibility; this function returns no timing prediction.

    In bypass mode, contiguous prefill rows are partitioned into batches of
    config.prefill_batch_tokens (default one). Their expert union is streamed
    once per batch, assigned to each expert's first token occurrence. A phase
    change starts a fresh batch. Only batches larger than max_batch=32 preserve
    cache state; smaller ones plan their layer union before charging first uses.
    """
    capacity = _integer(config.cache_capacity_bytes, "cache_capacity_bytes")
    if capacity < 0:
        raise ValueError("cache_capacity_bytes must be nonnegative")
    if config.cache_policy not in ("none", "lru", "slru"):
        raise ValueError("unknown cache_policy")
    if config.prefill_mode not in ("bypass", "serial"):
        raise ValueError("unknown prefill_mode")
    batch_tokens = _integer(
        getattr(config, "prefill_batch_tokens", 1), "prefill_batch_tokens"
    )
    if batch_tokens <= 0:
        raise ValueError("prefill_batch_tokens must be positive")
    energy_rate = _finite(config.joules_per_byte, "joules_per_byte")
    bandwidth = _finite(config.bandwidth_bytes_s, "bandwidth_bytes_s")
    if energy_rate < 0 or bandwidth <= 0:
        raise ValueError("energy rate must be nonnegative and bandwidth positive")
    if len(set(log.layers)) != len(log.layers):
        raise ValueError("RouterLog layers must be distinct")

    sizes: dict[int, int] = {}
    for layer in log.layers:
        size = _integer(config.expert_bytes[layer], "expert_bytes")
        if size <= 0:
            raise ValueError("expert_bytes must be positive")
        sizes[layer] = size

    # Lists run from oldest to newest. LRU uses only probation.
    probation: list[ExpertKey] = []
    protected: list[ExpertKey] = []
    moved_by_token = [0]*len(log.phase)

    def size_of(keys: Sequence[ExpertKey]) -> int:
        return sum(sizes[key[0]] for key in keys)

    def request(wanted_order, update):
        wanted = set(wanted_order)
        request_bytes = size_of(wanted_order)
        if not update or config.cache_policy == "none" or request_bytes > capacity:
            return wanted
        before = set(probation) | set(protected)
        hits = [key for key in wanted_order if key in before]
        misses = sorted(wanted-before)
        for key in hits:
            if key in probation:
                probation.remove(key)
            else:
                protected.remove(key)
            if config.cache_policy == "lru":
                probation.append(key)
            else:
                protected.append(key)
                while size_of(protected) > capacity//2:
                    probation.append(protected.pop(0))
        for key in misses:
            while size_of(probation)+size_of(protected)+sizes[key[0]] > capacity:
                victim = next(key for key in probation+protected if key not in wanted)
                if victim in probation:
                    probation.remove(victim)
                else:
                    protected.remove(victim)
            probation.append(key)
        return set(misses)

    position = 0
    while position < len(log.phase):
        phase = log.phase[position]
        if phase not in ("prefill", "decode"):
            raise ValueError("unknown RouterLog phase")
        end = position+1
        if phase == "prefill" and config.prefill_mode == "bypass":
            while end < len(log.phase) and end-position < batch_tokens and log.phase[end] == phase:
                end += 1
        # Pinned llama-moe-cache.cpp:503: max_batch=32, larger batches
        # preserve cache state. Small prefill unions use the same plan as decode.
        update = phase == "decode" or config.prefill_mode == "serial" or end-position <= 32
        for column, layer in enumerate(log.layers):
            ordered = list(dict.fromkeys(
                (layer, expert) for row in log.experts[position:end] for expert in row[column]
                if (layer, expert) not in config.resident))
            layer_updates = update
            if phase == "prefill" and config.prefill_mode == "bypass":
                layer_updates = layer_updates and (
                    min((end-position)*log.top_k, log.num_experts)*sizes[layer] <= capacity)
            missing = request(ordered, layer_updates)
            seen = set()
            for token in range(position, end):
                selected = {(layer, expert) for expert in log.experts[token][column]}
                fresh = (selected & missing)-seen
                moved_by_token[token] += size_of(tuple(fresh))
                seen.update(selected)
        position = end
    return tuple(ReferenceTransfer(moved, moved*energy_rate) for moved in moved_by_token)


def _rectangles(
    rectangles: Sequence[tuple[int, int, float]],
    name: str,
) -> tuple[tuple[int, int, float], ...]:
    checked = []
    for start, end, amount in rectangles:
        _integer(start, f"{name}.start_ns")
        _integer(end, f"{name}.end_ns")
        amount = _finite(amount, name)
        if end <= start:
            raise ValueError(f"{name} requires positive duration")
        if amount < 0:
            raise ValueError(f"{name} requires a nonnegative amount")
        checked.append((start, end, amount))
    return tuple(checked)


def reference_window_samples(
    times_ns: Sequence[int],
    window_ns: int,
    *,
    transfers: Sequence[TransferRectangle] = (),
    loads: Sequence[LoadRectangle] = (),
    baseline_watts: float = 0.0,
) -> tuple[float, ...]:
    """Average power over [timestamp - window_ns, timestamp].

    Transfers distribute energy uniformly across their positive duration.
    Loads contribute constant watts within their interval. Baseline applies
    at every time, including windows before or after all rectangles.
    """
    _integer(window_ns, "window_ns")
    if window_ns <= 0:
        raise ValueError("window_ns must be positive")
    baseline = _finite(baseline_watts, "baseline_watts")
    if baseline < 0:
        raise ValueError("baseline_watts must be nonnegative")
    pulses = _rectangles(transfers, "transfer")
    extras = _rectangles(loads, "load")
    result = []
    for timestamp in times_ns:
        _integer(timestamp, "timestamp")
        left = timestamp - window_ns
        contributions = [baseline]
        for start, end, energy in pulses:
            overlap = max(0, min(timestamp, end) - max(left, start))
            # Energy in the overlap, divided by window duration in seconds.
            contributions.append(
                energy * (overlap / (end - start)) * (1_000_000_000 / window_ns)
            )
        for start, end, watts in extras:
            overlap = max(0, min(timestamp, end) - max(left, start))
            contributions.append(watts * (overlap / window_ns))
        result.append(fsum(contributions))
    return tuple(result)


def _paired(
    x: Sequence[float], y: Sequence[float]
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("paired samples require equal lengths of at least two")
    return (
        tuple(_finite(value, "x") for value in x),
        tuple(_finite(value, "y") for value in y),
    )


def _pairwise_sums(
    x: Sequence[float], y: Sequence[float]
) -> tuple[float, float, float]:
    """Quadratic reference calculation, independent of mean-centering code.

    Sum_{i<j}(x_i-x_j)(y_i-y_j)
      = n * Sum_i((x_i-mean(x)) * (y_i-mean(y))).
    """
    n = len(x)
    xx = fsum((x[i] - x[j]) ** 2 for i in range(n) for j in range(i))
    yy = fsum((y[i] - y[j]) ** 2 for i in range(n) for j in range(i))
    xy = fsum(
        (x[i] - x[j]) * (y[i] - y[j])
        for i in range(n)
        for j in range(i)
    )
    return xx, yy, xy


def reference_pearson(x: Sequence[float], y: Sequence[float]) -> float:
    """Pearson correlation; constant inputs have undefined correlation."""
    xs, ys = _paired(x, y)
    xx, yy, xy = _pairwise_sums(xs, ys)
    if xx == 0 or yy == 0:
        raise ValueError("Pearson correlation is undefined for constant inputs")
    value = (xy / sqrt(xx)) / sqrt(yy)
    return min(1.0, max(-1.0, value))


def reference_linear_prediction(
    train_x: Sequence[float],
    train_y: Sequence[float],
    test_x: Sequence[float],
) -> tuple[float, ...]:
    """Scalar ordinary least squares with an intercept.

    A constant training predictor yields the training response mean.
    Predictions use only the supplied training observations.
    """
    xs, ys = _paired(train_x, train_y)
    xx, _, xy = _pairwise_sums(xs, ys)
    mean_x = fsum(xs) / len(xs)
    mean_y = fsum(ys) / len(ys)
    slope = xy / xx if xx else 0.0
    return tuple(
        mean_y + slope * (_finite(value, "test_x") - mean_x)
        for value in test_x
    )


def reference_required_correlation(
    stage_a_standardized_effect: float,
    n_per_group: int,
    *,
    alpha: float,
    power: float,
    comparisons: int,
) -> ReferenceCorrelationRequirement:
    """Gaussian equal-variance two-group normal approximation.

    Assumes d_power = r * d_stageA, equal group sizes, two-sided testing,
    and Bonferroni alpha / comparisons. For requested power >= 0.5:

        r_min = (z_(1-alpha/(2*comparisons)) + z_power)
                * sqrt(2 / n_per_group) / abs(d_stageA).

    A result above one is impossible under the stated attenuation model.
    This is not an empirical power estimate or a finite-sample t-test.
    """
    effect = abs(_finite(stage_a_standardized_effect, "stage_a_effect"))
    _integer(n_per_group, "n_per_group")
    _integer(comparisons, "comparisons")
    alpha = _finite(alpha, "alpha")
    power = _finite(power, "power")
    if n_per_group <= 0 or comparisons <= 0:
        raise ValueError("group size and comparisons must be positive")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    if not 0.5 <= power < 1:
        raise ValueError("this approximation requires power in [0.5, 1)")
    tail_probability = alpha / (2 * comparisons)
    if effect == 0 or tail_probability == 0:
        return ReferenceCorrelationRequirement(inf, False)
    normal = NormalDist()
    # Symmetry avoids subtracting a tiny tail probability from one.
    critical = -normal.inv_cdf(tail_probability)
    minimum = (
        (critical + normal.inv_cdf(power))
        * sqrt(2 / n_per_group)
        / effect
    )
    return ReferenceCorrelationRequirement(minimum, minimum <= 1.0)



def reference_interval_energies(
    trace: PowerTrace,
    windows: Sequence[tuple[int, int]],
    baseline_w: float,
) -> tuple[float, ...]:
    """Integrate baseline-subtracted watts over sampled cells, in joules.

    A cell ends at its sample time. Its start is the later of the preceding
    sample time and one nominal interval before its end. The first cell uses
    one nominal interval. Gaps longer than this interval remain uncovered;
    sensor averaging windows do not extend these integration cells.
    """
    if trace.unit != "W":
        raise ValueError("interval energies require a watts trace")
    interval = _integer(trace.nominal_interval_ns, "nominal_interval_ns")
    if interval <= 0:
        raise ValueError("nominal_interval_ns must be positive")
    baseline = _finite(baseline_w, "baseline_w")
    if len(trace.t_ns) != len(trace.values):
        raise ValueError("trace times and values must have equal lengths")
    cells: list[tuple[int, int, float]] = []
    previous: int | None = None
    for timestamp, value in zip(trace.t_ns, trace.values):
        _integer(timestamp, "trace timestamp")
        watts = _finite(value, "trace watts")
        if previous is not None and timestamp <= previous:
            raise ValueError("trace timestamps must be strictly increasing")
        start = timestamp - interval
        if previous is not None:
            start = max(start, previous)
        cells.append((start, timestamp, watts - baseline))
        previous = timestamp

    results = []
    for left, right in windows:
        _integer(left, "window start")
        _integer(right, "window end")
        if right < left:
            raise ValueError("window ends before its start")
        results.append(fsum(
            max(0, min(right, end) - max(left, start)) * watts / 1_000_000_000
            for start, end, watts in cells
        ))
    return tuple(results)


def reference_spectrum_amplitude(
    times: Sequence[int],
    values: Sequence[float],
    weights: Sequence[float],
    frequency_hz: float,
    origin_ns: int,
) -> float:
    """Weighted, mean-centered Fourier amplitude at one supplied frequency.

    Time-origin subtraction precedes conversion to seconds. Weights may be
    zero but must be nonnegative with a positive total. This direct complex
    sum imposes no evenly spaced sampling assumption.
    """
    if len(times) != len(values) or len(times) != len(weights) or not times:
        raise ValueError("times, values, and weights require equal nonzero lengths")
    frequency = _finite(frequency_hz, "frequency_hz")
    _integer(origin_ns, "origin_ns")
    for timestamp in times:
        _integer(timestamp, "spectrum timestamp")
    ys = tuple(_finite(value, "spectrum value") for value in values)
    ws = tuple(_finite(weight, "spectrum weight") for weight in weights)
    if any(weight < 0 for weight in ws):
        raise ValueError("spectrum weights must be nonnegative")
    total_weight = fsum(ws)
    if total_weight <= 0:
        raise ValueError("spectrum total weight must be positive")
    mean = fsum(value * weight for value, weight in zip(ys, ws)) / total_weight
    terms = [
        (value - mean) * weight
        * exp(2j * pi * frequency * ((timestamp - origin_ns) / 1_000_000_000))
        for timestamp, value, weight in zip(times, ys, ws)
    ]
    coefficient = complex(
        fsum(term.real for term in terms),
        fsum(term.imag for term in terms),
    )
    return 2 * abs(coefficient) / total_weight


@dataclass(frozen=True)
class ReferenceDetectionForecast:
    model_correlation: float | None
    contrast_j: float
    contrast_half_width_j: float


def reference_detection_forecast(
    sensor_noise_std_w: float,
    interval_ns: int,
    window_ns: int,
    quantum_w: float,
    routing_sd: float,
    slope_j_per_token: float,
    decode_tokens: int,
    decode_duration_s: float,
    phase_bias_std_j: float,
    stage_a_effect_sd: float,
    systematic_contrast_half_width_j: float,
    *, n_per_condition: int,
) -> ReferenceDetectionForecast:
    """Return diagnostic correlation, group contrast, and systematic bound.

    White sensor noise uses max(sample interval, averaging window) as its
    effective correlation time. Independent phase-bias variance adds in
    quadrature. The contrast assumes standardized linear attenuation. The
    systematic half-width is supplied. In the dither scenario, independent
    rounding variance q^2/12 is propagated to two n-episode condition means.
    The prior same-sign q*T alternative is not a decision bound.
    Zero signal and zero noise produce undefined correlation (None).
    """
    sensor_sigma = _finite(sensor_noise_std_w, "sensor_noise_std_w")
    _integer(interval_ns, "interval_ns")
    _integer(window_ns, "window_ns")
    quantum = _finite(quantum_w, "quantum_w")
    routing = _finite(routing_sd, "routing_sd")
    slope = _finite(slope_j_per_token, "slope_j_per_token")
    _integer(decode_tokens, "decode_tokens")
    duration = _finite(decode_duration_s, "decode_duration_s")
    phase_sigma = _finite(phase_bias_std_j, "phase_bias_std_j")
    effect = _finite(stage_a_effect_sd, "stage_a_effect_sd")
    systematic = _finite(
        systematic_contrast_half_width_j, "systematic_contrast_half_width_j"
    )
    if min(sensor_sigma, quantum, routing, phase_sigma, systematic) < 0:
        raise ValueError("standard deviations, quantum, and bounds must be nonnegative")
    if interval_ns <= 0 or window_ns < 0:
        raise ValueError("interval must be positive and window nonnegative")
    _integer(n_per_condition, "n_per_condition")
    if decode_tokens <= 0 or duration <= 0 or n_per_condition <= 0:
        raise ValueError("decode token count, duration and condition count must be positive")
    signal = abs(slope) * routing
    dt = max(interval_ns, window_ns)/1_000_000_000
    # Integral is dt*sum(readings), so rounding Var=q^2/12*T*dt.
    rounding_j2 = quantum**2/12*duration*dt if sensor_sigma >= quantum/2 else 0.0
    white_sigma_j = sqrt(sensor_sigma**2*duration*dt+rounding_j2)
    noise = hypot(white_sigma_j, phase_sigma) / decode_tokens
    denominator = hypot(signal, noise)
    correlation = signal / denominator if denominator else None
    contrast = abs(effect) * signal * decode_tokens
    # Independent means of n readings of episode energy: Var(diff)=2*Var/n.
    bound = systematic + sqrt(2*rounding_j2/n_per_condition)
    return ReferenceDetectionForecast(correlation, contrast, bound)


# Continuation oracle independently authored by gpt-6.1-sol without production code.
def reference_within_condition_fisher_interval(
    r: float | None, heldout_episodes: int,
) -> tuple[float, float] | None:
    import math
    if (not isinstance(heldout_episodes, int)
            or isinstance(heldout_episodes, bool) or heldout_episodes <= 5
            or r is None or not math.isfinite(r) or not -1.0 <= r <= 1.0):
        return None
    # N minus two fitted means, then Fisher's -3. 3.92 = 2*1.96.
    spread = math.exp(3.92 / math.sqrt(heldout_episodes - 5))
    plus, minus = 1.0 + r, 1.0 - r
    return ((plus - spread*minus)/(plus + spread*minus),
            (spread*plus - minus)/(spread*plus + minus))


def reference_decode_stall_schedule(
    windows: Sequence[tuple[int, int, int]], phases: Sequence[str], moved_bytes: Sequence[int],
    bandwidth_bytes_s: float, boundaries: Mapping[str, int | None],
) -> tuple[tuple[tuple[int, int, int], ...], dict[str, int | None], int]:
    from fractions import Fraction
    rate = Fraction(str(bandwidth_bytes_s))
    insertions = []
    for (_, _, end), phase, count in zip(windows, phases, moved_bytes):
        if phase == "decode" and count:
            exact_ns = Fraction(count * 1_000_000_000, 1) / rate
            dt = (exact_ns.numerator + exact_ns.denominator - 1) // exact_ns.denominator
            insertions.append((end, dt))
    def mapped(t: int | None) -> int | None:
        return None if t is None else t + sum(dt for end, dt in insertions if end <= t)
    adjusted = tuple((index, mapped(start), mapped(end)) for index, start, end in windows)
    adjusted_bounds = {name: mapped(t) for name, t in boundaries.items()}
    return adjusted, adjusted_bounds, sum(dt for _, dt in insertions)


def reference_residual_adjusted_correlation(
    signal_sd: float, residual_sd: float, white_j: float, phase_j: float, decode_tokens: int,
) -> float | None:
    """Independent episode-scale sum of signal, mapping and sensor variances."""
    import math
    signal_j = signal_sd * decode_tokens
    residual_j = residual_sd * decode_tokens
    total_sd_j = math.sqrt(math.fsum(value*value for value in
        (signal_j, residual_j, white_j, phase_j)))
    return signal_j / total_sd_j if total_sd_j else None


def reference_power_increment(observations) -> tuple[float | None, int]:
    """Review-round oracle using pairwise OLS and explicit projection vectors.

    Revised in this fix seat, not a new independent-model implementation.
    Groups are held out together; conditions center evaluation, never training.
    """
    residuals = []
    for target in observations:
        training = [item for item in observations if item.group != target.group]
        if len(training) < 2:
            continue
        z = [item.features.decode_seconds_per_token for item in training]
        x = [item.features.energy_per_decode_token_j for item in training]
        y = [item.routing_statistic for item in training]
        tz = [target.features.decode_seconds_per_token]
        all_z = z+tz
        fitted_x = reference_linear_prediction(z, x, all_z)
        fitted_y = reference_linear_prediction(z, y, all_z)
        rx = [value-fit for value, fit in zip(x, fitted_x)]
        ry = [value-fit for value, fit in zip(y, fitted_y)]
        xx, _, _ = _pairwise_sums(rx, ry)
        if not xx:
            continue
        tx = target.features.energy_per_decode_token_j-fitted_x[-1]
        predicted = reference_linear_prediction(rx, ry, [tx])[0]
        residuals.append((target.episode_id.endswith("-sabotage"),
                          target.routing_statistic-fitted_y[-1], predicted))
    truth, prediction = [], []
    for label in (False, True):
        selected = [(a, b) for tag, a, b in residuals if tag == label]
        if selected:
            ma, mb = fsum(a for a, _ in selected)/len(selected), fsum(b for _, b in selected)/len(selected)
            truth.extend(a-ma for a, _ in selected)
            prediction.extend(b-mb for _, b in selected)
    try:
        correlation = reference_pearson(truth, prediction)
    except ValueError:
        correlation = None
    return correlation, len(truth)
