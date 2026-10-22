"""Independent stdlib numerical oracle for synthetic MoE Stage B checks.

Implementation provenance:
- Written without viewing production Stage B code.
- Shared input contract: joulewise.align.records.RouterLog.
- Each token/layer selection is one atomic request, in log.layers order.
- Over-capacity requests stream every selected nonresident expert and leave
  cache contents and recency unchanged. Prefill bypass has the same behavior.
- Synthetic calculations only; these functions are not hardware measurements.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import fsum, inf, isfinite, sqrt
from statistics import NormalDist
from typing import Literal, Mapping, Protocol, Sequence

from joulewise.align.records import RouterLog

ExpertKey = tuple[int, int]
TransferRectangle = tuple[int, int, float]  # start_ns, end_ns, energy_j
LoadRectangle = tuple[int, int, float]  # start_ns, end_ns, watts


class ReferenceConfig(Protocol):
    expert_bytes: Mapping[int, int]
    resident: frozenset[ExpertKey]
    cache_capacity_bytes: int
    cache_policy: Literal["none", "lru", "slru"]
    prefill_mode: Literal["bypass", "serial"]
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
    """
    capacity = _integer(config.cache_capacity_bytes, "cache_capacity_bytes")
    if capacity < 0:
        raise ValueError("cache_capacity_bytes must be nonnegative")
    if config.cache_policy not in ("none", "lru", "slru"):
        raise ValueError("unknown cache_policy")
    if config.prefill_mode not in ("bypass", "serial"):
        raise ValueError("unknown prefill_mode")
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

    def size_of(keys: Sequence[ExpertKey]) -> int:
        return sum(sizes[key[0]] for key in keys)

    for phase, token in zip(log.phase, log.experts):
        if phase not in ("prefill", "decode"):
            raise ValueError("unknown RouterLog phase")
        moved = 0
        for layer, experts in zip(log.layers, token):
            wanted = {
                (layer, expert)
                for expert in experts
                if (layer, expert) not in config.resident
            }
            request_bytes = size_of(tuple(wanted))
            bypass = phase == "prefill" and config.prefill_mode == "bypass"
            if (
                bypass
                or config.cache_policy == "none"
                or request_bytes > capacity
            ):
                moved += request_bytes
                continue

            before = set(probation) | set(protected)
            hits = sorted(wanted & before)
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
                    # Compare integers: protected budget is capacity / 2 bytes.
                    while 2 * size_of(protected) > capacity:
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
