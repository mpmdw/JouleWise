"""Synthetic, fixed-work power contrasts. No collectors or data-file readers.

All estimates are B minus A in watts. For equal-duration fixed-work arms this
is also the energy contrast divided by arm duration. The reference is -1 for A
and +1 for B; injected power is ``baseline + contrast * reference / 2``.

NumPy is imported on use. CIs are exploratory asymptotic intervals, not the
repo's registered claim intervals or deterministic instrument error bounds.
HAC and bootstrap operate on chronological FOUR-CHIP blocks, never on nominally
independent meter samples. They assume dependence decays between blocks;
unmodelled schedule-correlated drift/transients can still bias both methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from statistics import NormalDist
from typing import Any

from ._common import require_numpy as _numpy


def _finite(name: str, value: float, *, positive: bool = False,
            nonnegative: bool = False) -> None:
    if not math.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0):
        raise ValueError(f"invalid {name}: {value!r}")


def _integer(name: str, value: int, minimum: int = 1) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


@dataclass(frozen=True)
class Schedule:
    """Equal-duration chips, grouped into complete four-chip inference blocks."""

    chips: tuple[int, ...]
    chip_seconds: float
    kind: str = "custom"

    def __post_init__(self):
        _finite("chip_seconds", self.chip_seconds, positive=True)
        if not self.chips or len(self.chips) % 4 or any(c not in (-1, 1) for c in self.chips):
            raise ValueError("chips must be +/-1 in complete four-chip blocks")

    @property
    def duration_seconds(self) -> float:
        return len(self.chips) * self.chip_seconds

    @property
    def n_blocks(self) -> int:
        return len(self.chips) // 4

    def window_reference(self, starts: Any, ends: Any):
        """Exact average of the chip signs over each [start, end) window."""
        np = _numpy()
        starts, ends = np.asarray(starts, dtype=float), np.asarray(ends, dtype=float)
        if (starts.shape != ends.shape or starts.ndim != 1 or
                not np.all(np.isfinite(starts)) or not np.all(np.isfinite(ends)) or
                np.any(starts < 0) or np.any(ends > self.duration_seconds) or
                np.any(ends <= starts)):
            raise ValueError("invalid sampling windows")
        chips = np.asarray(self.chips, dtype=float)
        prefix = np.multiply(np.concatenate(([0.0], np.cumsum(chips))), self.chip_seconds)

        def integral(t):
            index = np.minimum(np.divide(t, self.chip_seconds).astype(int), len(chips) - 1)
            return np.add(prefix[index], np.multiply(chips[index],
                          np.subtract(t, np.multiply(index, self.chip_seconds))))

        return np.divide(np.subtract(integral(ends), integral(starts)), np.subtract(ends, starts))


def make_schedule(n_blocks: int, chip_seconds: float = 2.0, *,
                  kind: str = "randomized_abba", seed: int = 0) -> Schedule:
    """Square chop, ABBA, randomized ABBA/BAAB, or balanced random bi-phase.

    ``manchester`` is random bi-phase coding, not a maximal-length m-sequence.
    Its pairs have zero DC. Schedule and noise RNGs are independent.
    """
    _integer("n_blocks", n_blocks)
    _finite("chip_seconds", chip_seconds, positive=True)
    np = _numpy()
    rng = np.random.default_rng(seed)
    if kind == "square":
        chips = np.tile([-1, 1, -1, 1], n_blocks)
    elif kind in ("abba", "randomized_abba"):
        orientations = (rng.choice([-1, 1], n_blocks) if kind == "randomized_abba"
                        else np.ones(n_blocks, dtype=int))
        chips = (orientations[:, None] * np.array([-1, 1, 1, -1])).ravel()
    elif kind == "manchester":
        signs = rng.choice([-1, 1], 2 * n_blocks)
        chips = np.column_stack((signs, np.negative(signs))).ravel()
    else:
        raise ValueError(f"unknown schedule kind: {kind}")
    return Schedule(tuple(int(x) for x in chips), chip_seconds, kind)


@dataclass(frozen=True)
class NoiseModel:
    """Synthetic noise parameters, in watts and seconds.

    White SD is PER REPORTED WINDOW, not a sensor noise density. Changing Hz
    with the same SD does not model the same physical instrument. Pink noise
    has 1/f power spectrum between 1/trace_duration and Nyquist, normalized to
    the requested realization RMS. It is a finite-trace model, not a license
    to extrapolate one long 1/f trace as independent replays.

    Thermal drift is an exponential warm-up. Steps are (time, signed watts).
    Contention is positive rectangular Poisson bursts with exponential lengths;
    overlapping bursts add. No clipping, censoring or outlier removal occurs.
    """

    white_sd_w: float = 0.03
    pink_sd_w: float = 0.0
    thermal_amplitude_w: float = 0.0
    thermal_tau_seconds: float = 300.0
    steps: tuple[tuple[float, float], ...] = ()
    burst_rate_hz: float = 0.0
    burst_mean_seconds: float = 1.0
    burst_amplitude_w: float = 0.0

    def __post_init__(self):
        for name in ("white_sd_w", "pink_sd_w", "burst_rate_hz", "burst_amplitude_w"):
            _finite(name, getattr(self, name), nonnegative=True)
        _finite("thermal_amplitude_w", self.thermal_amplitude_w)
        _finite("thermal_tau_seconds", self.thermal_tau_seconds, positive=True)
        _finite("burst_mean_seconds", self.burst_mean_seconds, positive=True)
        for time, watts in self.steps:
            _finite("step time", time, nonnegative=True)
            _finite("step watts", watts)


@dataclass(frozen=True)
class SyntheticTrace:
    schedule: Schedule
    starts_seconds: Any
    ends_seconds: Any
    reference: Any
    power_w: Any
    baseline_w: float
    effect_fraction: float
    components_w: dict[str, Any] = field(repr=False)

    @property
    def contrast_w(self) -> float:
        return self.baseline_w * self.effect_fraction


def simulate_trace(schedule: Schedule, *, sample_rate_hz: float = 8.0,
                   baseline_w: float = 27.0, effect_fraction: float = 1e-5,
                   noise: NoiseModel | None = None, seed: int = 0) -> SyntheticTrace:
    """Generate interval-average power at rail or meter-window sample rates.

    The commanded signal, thermal drift, steps and bursts are window averaged.
    White/pink components are generated at the reported cadence. A last partial
    window is retained. Effects may be signed; A/A' is ``effect_fraction=0``.
    This is NOT an acquisition tool or a calibrated Apple/KM003C noise model.
    """
    np = _numpy()
    _finite("sample_rate_hz", sample_rate_hz, positive=True)
    _finite("baseline_w", baseline_w, positive=True)
    _finite("effect_fraction", effect_fraction)
    noise = noise or NoiseModel()
    duration = schedule.duration_seconds
    n = math.ceil(duration * sample_rate_hz)
    starts = np.divide(np.arange(n, dtype=float), sample_rate_hz)
    ends = np.minimum(np.add(starts, 1 / sample_rate_hz), duration)
    widths = np.subtract(ends, starts)
    reference = schedule.window_reference(starts, ends)
    rng = np.random.default_rng(seed)
    white = rng.normal(0, noise.white_sd_w, n)
    pink = np.zeros(n)
    if noise.pink_sd_w and n > 2:
        freqs = np.fft.rfftfreq(n)
        spectrum = rng.normal(size=len(freqs)) + 1j * rng.normal(size=len(freqs))
        spectrum[0] = 0
        spectrum[1:] /= np.sqrt(freqs[1:])
        pink = np.fft.irfft(spectrum, n=n)
        pink *= noise.pink_sd_w / np.std(pink)
    tau = noise.thermal_tau_seconds
    decay = np.exp(np.divide(np.negative(starts), tau))
    window_decay = np.negative(np.expm1(np.divide(np.negative(widths), tau)))
    thermal = np.multiply(noise.thermal_amplitude_w,
                          np.subtract(1, np.divide(np.multiply(tau, np.multiply(decay, window_decay)), widths)))
    steps = np.zeros(n)
    for time, watts in noise.steps:
        steps += np.divide(np.multiply(watts, np.clip(
            np.subtract(ends, np.maximum(starts, time)), 0, widths)), widths)
    bursts = np.zeros(n)
    count = rng.poisson(noise.burst_rate_hz * duration)
    for start, length in zip(rng.uniform(0, duration, count),
                             rng.exponential(noise.burst_mean_seconds, count)):
        overlap = np.clip(np.subtract(np.minimum(ends, start + length), np.maximum(starts, start)),
                          0, widths)
        bursts += np.divide(np.multiply(noise.burst_amplitude_w, overlap), widths)
    components = {"signal": np.multiply(baseline_w * effect_fraction / 2, reference),
                  "white": white, "pink": pink, "thermal": thermal,
                  "steps": steps, "bursts": bursts}
    power = np.add(baseline_w, np.sum(list(components.values()), axis=0))
    return SyntheticTrace(schedule, starts, ends, reference, power,
                          baseline_w, effect_fraction, components)


@dataclass(frozen=True)
class Estimate:
    contrast_w: float
    standard_error_w: float
    ci_low_w: float
    ci_high_w: float
    confidence: float
    estimator: str
    ci_method: str
    n_blocks: int
    dependence_blocks: int
    retained_fraction: float
    warnings: tuple[str, ...]


def _interval(estimate: float, block_scores: Any, *, confidence: float,
              ci_method: str, hac_lags: int | None, bootstrap_block_length: int | None,
              bootstrap_replicates: int, seed: int, estimator: str,
              retained_fraction: float) -> Estimate:
    """HAC or circular moving-block bootstrap of centered block influence scores."""
    np = _numpy()
    if not 0 < confidence < 1:
        raise ValueError("confidence must lie strictly between 0 and 1")
    scores = np.asarray(block_scores, dtype=float)
    n = len(scores)
    if n < 8:
        raise ValueError("at least eight complete four-chip blocks are required")
    scores = scores - np.mean(scores)
    warnings = ("asymptotic CI; fewer than 30 blocks",) if n < 30 else ()
    if ci_method == "hac":
        lags = int(4 * (n / 100) ** (2 / 9)) if hac_lags is None else hac_lags
        _integer("hac_lags", lags, 0)
        if lags >= n:
            raise ValueError("hac_lags must be smaller than n_blocks")
        meat = float(np.sum(np.square(scores)))
        for lag in range(1, lags + 1):
            meat += 2 * (1 - lag / (lags + 1)) * float(np.sum(np.multiply(scores[lag:], scores[:-lag])))
        se = math.sqrt(max(0.0, meat) / (n * (n - 1)))
        half = NormalDist().inv_cdf((1 + confidence) / 2) * se
        low, high = estimate - half, estimate + half
        dependence = lags
    elif ci_method == "block_bootstrap":
        length = (max(1, round(n ** (1 / 3))) if bootstrap_block_length is None
                  else bootstrap_block_length)
        _integer("bootstrap_block_length", length)
        _integer("bootstrap_replicates", bootstrap_replicates, 100)
        if length >= n:
            raise ValueError("bootstrap_block_length must be smaller than n_blocks")
        rng = np.random.default_rng(seed)
        # Bounded memory: bootstrap block scores, not kHz raw sample arrays.
        draws = np.empty(bootstrap_replicates)
        offsets = np.arange(length)
        for i in range(bootstrap_replicates):
            starts = rng.integers(n, size=math.ceil(n / length))
            index = ((starts[:, None] + offsets) % n).ravel()[:n]
            draws[i] = np.mean(scores[index])
        se = float(np.std(draws, ddof=1))
        tail = (1 - confidence) / 2
        q_low, q_high = np.quantile(draws, [tail, 1 - tail])
        low, high = estimate - float(q_high), estimate - float(q_low)
        dependence = length
    else:
        raise ValueError("ci_method must be hac or block_bootstrap")
    return Estimate(float(estimate), se, low, high, confidence, estimator,
                    ci_method, n, dependence, retained_fraction, warnings)


def _trace_arrays(trace: SyntheticTrace):
    np = _numpy()
    arrays = [np.asarray(x, dtype=float) for x in
              (trace.starts_seconds, trace.ends_seconds, trace.reference, trace.power_w)]
    start, end, ref, power = arrays
    if (any(x.ndim != 1 or x.shape != power.shape or not np.all(np.isfinite(x))
            for x in arrays) or len(power) < 2 or np.any(start < 0) or
            np.any(end <= start) or np.any(start[1:] < end[:-1] - 1e-10) or
            np.any(end > trace.schedule.duration_seconds) or np.any(np.abs(ref) > 1 + 1e-10)):
        raise ValueError("invalid trace arrays")
    return start, end, ref, power


def demodulate(trace: SyntheticTrace, *, fundamental: bool = False,
               detrend: bool = True, edge_guard_seconds: float = 0.0,
               ci_method: str = "hac", confidence: float = 0.95,
               hac_lags: int | None = None, bootstrap_block_length: int | None = None,
               bootstrap_replicates: int = 999, seed: int = 0) -> Estimate:
    """Synchronous demodulation against the known, window-averaged reference.

    Default: matched square/coded reference (including harmonics). For square
    schedules, ``fundamental=True`` uses the known-phase sinusoid at
    1/(2*chip_seconds), calibrated against the actual averaged square reference.
    This estimates a signed B-A contrast, not a positively biased FFT magnitude.
    Intercept and optional linear trend are projected out of the reference.
    Edge guards discard whole windows near chip edges, never individual values.
    CIs use four-chip sums of regression influence scores; lags/lengths are in
    those blocks. These are score-bootstrap (basic) intervals, not iid resampling.
    """
    np = _numpy()
    start, end, reference, power = _trace_arrays(trace)
    _finite("edge_guard_seconds", edge_guard_seconds, nonnegative=True)
    chip = trace.schedule.chip_seconds
    if 2 * edge_guard_seconds >= chip:
        raise ValueError("edge guard leaves no chip interior")
    keep = np.ones(len(power), dtype=bool)
    if edge_guard_seconds:
        index = np.floor(np.divide(np.add(start, 1e-10), chip))
        left = np.add(np.multiply(index, chip), edge_guard_seconds - 1e-10)
        right = np.add(np.multiply(np.add(index, 1), chip), -edge_guard_seconds + 1e-10)
        keep = (start >= left) & (end <= right)
    retained = float(np.mean(keep))
    start, end, reference, power = (x[keep] for x in (start, end, reference, power))
    if not len(power):
        raise ValueError("no retained sampling windows")
    time = np.divide(np.add(start, end), 2)
    x = np.divide(reference, 2)
    centered_time = np.subtract(time, np.mean(time))

    def residualize(values):
        # The centered time column is orthogonal to the intercept, so the
        # nuisance projection needs no matrix factorization or BLAS threads.
        centered = np.subtract(values, np.mean(values))
        if detrend:
            time_ss = float(np.sum(np.square(centered_time)))
            if time_ss == 0:
                raise ValueError("sampling times do not identify a trend")
            slope = float(np.sum(np.multiply(centered_time, centered))) / time_ss
            centered = np.subtract(centered, np.multiply(centered_time, slope))
        return centered

    if fundamental:
        expected = (-1, 1, -1, 1) * trace.schedule.n_blocks
        if trace.schedule.chips not in (expected, tuple(-x for x in expected)):
            raise ValueError("fundamental demodulation requires the A/B square schedule")
        frequency = 1 / (2 * chip)
        instrument = np.multiply(-np.sin(np.multiply(2 * np.pi * frequency, time)),
                                 np.sinc(np.multiply(frequency, np.subtract(end, start))))
    else:
        instrument = x.copy()
    r = residualize(instrument)
    denominator = float(np.sum(np.multiply(r, x)))
    scale = math.sqrt(float(np.sum(np.square(r))) * float(np.sum(np.square(x))))
    if abs(denominator) <= 1e-12 * max(1.0, scale):
        raise ValueError("reference is unidentifiable at this cadence/guard")
    estimate = float(np.sum(np.multiply(r, power))) / denominator
    residual = residualize(np.subtract(power, np.multiply(estimate, x)))
    block_index = np.minimum(np.divide(time, 4 * chip).astype(int), trace.schedule.n_blocks - 1)
    if len(np.unique(block_index)) != trace.schedule.n_blocks:
        raise ValueError("sampling must cover every schedule block")
    scores = np.multiply(np.bincount(block_index,
                         weights=np.divide(np.multiply(r, residual), denominator),
                         minlength=trace.schedule.n_blocks), trace.schedule.n_blocks)
    return _interval(estimate, scores, confidence=confidence, ci_method=ci_method,
                     hac_lags=hac_lags, bootstrap_block_length=bootstrap_block_length,
                     bootstrap_replicates=bootstrap_replicates, seed=seed,
                     estimator="fundamental" if fundamental else "matched_reference",
                     retained_fraction=retained)


def abba_differences(trace: SyntheticTrace):
    """One B-A contrast per ABBA/BAAB block, cancelling a local linear drift.

    Chip means use only windows wholly inside a chip, weighted by duration.
    Each chip must have the SAME observed duration and mean sample time relative
    to chip start. Refuse unequal coverage rather than inventing a missing arm.
    Crossing windows cannot be unmixed into observed A and B powers.
    """
    np = _numpy()
    start, end, _, power = _trace_arrays(trace)
    chip = trace.schedule.chip_seconds
    signs = np.asarray(trace.schedule.chips).reshape(-1, 4)
    if not np.all(np.abs(np.sum(np.multiply(signs, [-1, 1, 1, -1]), axis=1)) == 4):
        raise ValueError("paired differences require ABBA or BAAB in every block")
    indices = np.floor(np.divide(np.add(start, 1e-10), chip)).astype(int)
    keep = end <= np.add(np.multiply(np.add(indices, 1), chip), 1e-10)
    indices, widths = indices[keep], np.subtract(end, start)[keep]
    size = len(trace.schedule.chips)
    weights = np.bincount(indices, weights=widths, minlength=size)
    if np.any(weights == 0) or not np.allclose(weights, weights[0], rtol=1e-9, atol=1e-10):
        raise ValueError("ABBA requires equal nonempty chip coverage")
    time_in_chip = np.subtract(np.divide(np.add(start[keep], end[keep]), 2), np.multiply(indices, chip))
    centroids = np.divide(np.bincount(indices, weights=np.multiply(widths, time_in_chip), minlength=size), weights)
    if not np.allclose(centroids, centroids[0], rtol=1e-9, atol=1e-10):
        raise ValueError("ABBA requires equal within-chip sampling centroids")
    means = np.divide(np.bincount(indices, weights=np.multiply(widths, power[keep]), minlength=size), weights)
    return np.divide(np.sum(np.multiply(means.reshape(-1, 4), signs), axis=1), 2)


def estimate_abba(trace: SyntheticTrace, *, ci_method: str = "hac",
                  confidence: float = 0.95, hac_lags: int | None = None,
                  bootstrap_block_length: int | None = None,
                  bootstrap_replicates: int = 999, seed: int = 0) -> Estimate:
    """Mean of signed ABBA differences, with HAC or block-bootstrap uncertainty."""
    np = _numpy()
    contrasts = abba_differences(trace)
    start, end, _, _ = _trace_arrays(trace)
    chip = trace.schedule.chip_seconds
    retained = float(np.mean(end <= (np.floor((start + 1e-10) / chip) + 1) * chip + 1e-10))
    return _interval(float(np.mean(contrasts)), contrasts, confidence=confidence,
                     ci_method=ci_method, hac_lags=hac_lags,
                     bootstrap_block_length=bootstrap_block_length,
                     bootstrap_replicates=bootstrap_replicates, seed=seed,
                     estimator="paired_abba", retained_fraction=retained)
