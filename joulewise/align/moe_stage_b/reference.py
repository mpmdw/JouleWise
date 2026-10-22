"""Independent stdlib numerical oracle for synthetic MoE Stage B checks.

Implementation provenance:
- Written without viewing production Stage B code.
- Shared input contract: joulewise.align.records.RouterLog.
- Each token/layer selection is one atomic request, in log.layers order.
- Over-capacity requests stream every selected nonresident expert and leave
  cache contents and recency unchanged.
- Prefill bypass streams each nonresident expert once per explicit batch,
  charging its first occurrence without changing the dynamic cache. This
  batch-union approximation does not model read-only cache reuse for large
  upstream batches.
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
    change starts a fresh batch. Dynamic cache state is preserved throughout.
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
    output: list[ReferenceTransfer] = []
    prefill_position = 0
    batch_seen: set[ExpertKey] = set()

    def size_of(keys: Sequence[ExpertKey]) -> int:
        return sum(sizes[key[0]] for key in keys)

    for phase, token in zip(log.phase, log.experts):
        if phase not in ("prefill", "decode"):
            raise ValueError("unknown RouterLog phase")
        if phase == "decode":
            prefill_position = 0
            batch_seen.clear()
        else:
            if prefill_position % batch_tokens == 0:
                batch_seen.clear()
            prefill_position += 1
        moved = 0
        for layer, experts in zip(log.layers, token):
            wanted_order = list(dict.fromkeys(
                (layer, expert) for expert in experts
                if (layer, expert) not in config.resident
            ))
            wanted = set(wanted_order)
            request_bytes = size_of(tuple(wanted))
            bypass = phase == "prefill" and config.prefill_mode == "bypass"
            if bypass:
                moved += size_of(tuple(wanted - batch_seen))
                batch_seen.update(wanted)
                continue
            if config.cache_policy == "none" or request_bytes > capacity:
                moved += request_bytes
                continue

            before = set(probation) | set(protected)
            hits = [key for key in wanted_order if key in before]
            misses = sorted(wanted - before)
            moved += size_of(misses)

            # Complete all hit touches before admitting any miss.
            for key in hits:
                if key in probation:
                    probation.remove(key)
                else:
                    protected.remove(key)
                if config.cache_policy == "lru":
                    probation.append(key)
                else:
                    protected.append(key)
                    # Protected byte budget is floor(capacity / 2).
                    while size_of(protected) > capacity // 2:
                        probation.append(protected.pop(0))

            for key in misses:
                needed = sizes[key[0]]
                while size_of(probation) + size_of(protected) + needed > capacity:
                    # Selected keys cannot be evicted during their request.
                    victim = next(
                        (
                            candidate
                            for candidate in probation + protected
                            if candidate not in wanted
                        ),
                        None,
                    )
                    if victim is None:
                        raise AssertionError("atomic request capacity invariant")
                    if victim in probation:
                        probation.remove(victim)
                    else:
                        protected.remove(victim)
                probation.append(key)

        output.append(ReferenceTransfer(moved, moved * energy_rate))
    return tuple(output)


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
) -> ReferenceDetectionForecast:
    """Return diagnostic correlation, group contrast, and systematic bound.

    White sensor noise uses max(sample interval, averaging window) as its
    effective correlation time. Independent phase-bias variance adds in
    quadrature. The contrast assumes standardized linear attenuation. The
    systematic half-width adds the supplied contrast bound and quantum*T.
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
    if decode_tokens <= 0 or duration <= 0:
        raise ValueError("decode token count and duration must be positive")
    signal = abs(slope) * routing
    white_sigma_j = sensor_sigma * sqrt(
        duration * (max(interval_ns, window_ns) / 1_000_000_000)
    )
    noise = hypot(white_sigma_j, phase_sigma) / decode_tokens
    denominator = hypot(signal, noise)
    correlation = signal / denominator if denominator else None
    contrast = abs(effect) * signal * decode_tokens
    bound = systematic + quantum * duration
    return ReferenceDetectionForecast(correlation, contrast, bound)


# Continuation oracle independently authored by gpt-6.1-sol without production code.
def reference_within_condition_fisher_interval(r, heldout_episodes):
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


def reference_decode_stall_schedule(windows, phases, moved_bytes,
                                    bandwidth_bytes_s, boundaries):
    from fractions import Fraction
    rate = Fraction(str(bandwidth_bytes_s))
    insertions = []
    for (_, _, end), phase, count in zip(windows, phases, moved_bytes):
        if phase == "decode" and count:
            exact_ns = Fraction(count * 1_000_000_000, 1) / rate
            dt = (exact_ns.numerator + exact_ns.denominator - 1) // exact_ns.denominator
            insertions.append((end, dt))
    def mapped(t):
        return None if t is None else t + sum(dt for end, dt in insertions if end <= t)
    adjusted = tuple((index, mapped(start), mapped(end)) for index, start, end in windows)
    adjusted_bounds = {name: mapped(t) for name, t in boundaries.items()}
    return adjusted, adjusted_bounds, sum(dt for _, dt in insertions)


def reference_residual_adjusted_correlation(signal_sd, residual_sd,
                                            white_j, phase_j, decode_tokens):
    """Independent episode-scale sum of signal, mapping and sensor variances."""
    import math
    signal_j = signal_sd * decode_tokens
    residual_j = residual_sd * decode_tokens
    total_sd_j = math.sqrt(math.fsum(value*value for value in
        (signal_j, residual_j, white_j, phase_j)))
    return signal_j / total_sd_j if total_sd_j else None
