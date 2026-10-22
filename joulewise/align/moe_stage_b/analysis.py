"""Decode power features, grouped routing recovery and conditional Stage B power.

All decisions remain diagnostics with flags. Statistical design inputs are
parameters; synthetic results never establish a sensor's real detectability.
"""

from __future__ import annotations

import math
import bisect
import statistics
from dataclasses import dataclass
from typing import Sequence

from joulewise.align.records import Episode, PowerTrace
from joulewise.align.moe_stage_b.simulation import SensorModel
from joulewise.align.moe_stage_b.traffic import NS_PER_SECOND, TokenWindow, episode_token_windows


@dataclass(frozen=True)
class PowerFeatures:
    episode_id: str
    decode_tokens: int
    energy_per_decode_token_j: float | None
    token_energy_variance_j2: float | None
    token_rate_hz: float | None
    token_rate_amplitude_w: float | None
    energy_half_width_per_token_j: float | None
    coverage_fraction: float
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class RoutingObservation:
    episode_id: str
    group: str
    routing_statistic: float
    features: PowerFeatures


@dataclass(frozen=True)
class RoutingRecovery:
    feature_name: str
    observed_correlation: float | None
    held_out_correlation: float | None
    held_out_rmse: float | None
    predictions: tuple[tuple[str, float | None], ...]
    flags: tuple[str, ...] = ()
    held_out_interval_95: tuple[float, float] | None = None
    held_out_episodes: int = 0
    held_out_effective_n: int = 0


def fisher_interval_95(
    correlation: float | None, episodes: int, *, fitted_means: int = 0,
) -> tuple[float, float] | None:
    """Requested 95% Fisher-z interval, with explicit centering degrees of freedom.

    This is an approximate episode-level interval, not a grouped bootstrap or
    proof of design power. Overlapping cross-validation fits can add dependence.
    """
    if (not isinstance(episodes, int) or isinstance(episodes, bool)
            or not isinstance(fitted_means, int) or isinstance(fitted_means, bool)
            or fitted_means < 0):
        return None
    effective_n = episodes-fitted_means
    if (correlation is None or not math.isfinite(correlation)
            or abs(correlation) > 1 or effective_n <= 3):
        return None
    if abs(correlation) == 1:
        return (correlation, correlation)  # Limits of tanh(z +/- width) at infinity.
    # The lead specifies 1.96 for the two-sided normal 95% interval.
    width = 1.96/math.sqrt(effective_n-3)
    center = math.atanh(correlation)
    return (math.tanh(center-width), math.tanh(center+width))


@dataclass(frozen=True)
class CorrelationRequirement:
    minimum_absolute_correlation: float | None
    feasible: bool
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class DetectionPlan:
    required_correlation: float | None
    model_correlation: float | None
    contrast_energy_j: float | None
    contrast_half_width_j: float | None
    detectable_under_assumptions: bool
    flags: tuple[str, ...] = ()


def pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    """Centered two-pass Pearson correlation; constant series stay undefined."""
    if len(x) != len(y) or len(x) < 2 or any(not math.isfinite(v) for v in (*x, *y)):
        return None
    scale_x, scale_y = max(map(abs, x)), max(map(abs, y))
    if scale_x == 0.0 or scale_y == 0.0:
        return None
    normalized_x, normalized_y = [v/scale_x for v in x], [v/scale_y for v in y]
    mx, my = statistics.fmean(normalized_x), statistics.fmean(normalized_y)
    centered_x = [v-mx for v in normalized_x]
    centered_y = [v-my for v in normalized_y]
    xx = math.fsum(v*v for v in centered_x)
    yy = math.fsum(v*v for v in centered_y)
    if xx == 0.0 or yy == 0.0:
        return None
    value = (math.fsum(a*b for a, b in zip(centered_x, centered_y))
             / math.sqrt(xx) / math.sqrt(yy))
    # Cauchy-Schwarz bounds the mathematical value; rounding can stray outside.
    return max(-1.0, min(1.0, value))


def extract_features(
    episode: Episode, trace: PowerTrace, *, baseline_w: float,
    noise_std_w: float, noise_multiplier: float, attribution_floor_j: float,
    windows: Sequence[TokenWindow] | None = None,
    reference_decode_duration_ns: int | None = None,
) -> PowerFeatures:
    """Reconstruct interval energy and per-token/spectral power features.

    Each reading represents a nominal cell ENDING at its timestamp. Missing
    cells are not filled. For duty-cycled sensors this is an apparent energy,
    requiring randomized sampling phases/repetitions before an unbiased claim.
    Quantization is bounded by q/2 per sample; it is not assumed to dither.
    """
    flags = list(episode.flags)
    count = sum(t.decode_tokens for t in episode.turns)
    def missing(reason: str) -> PowerFeatures:
        return PowerFeatures(episode.episode_id, count, None, None, None, None,
                             None, 0.0, tuple(dict.fromkeys(flags + [reason])))
    if (not all(math.isfinite(v) for v in (baseline_w, noise_std_w, noise_multiplier,
                                           attribution_floor_j))
            or min(noise_std_w, noise_multiplier, attribution_floor_j) < 0):
        return missing("invalid_feature_parameters")
    if trace.unit != "W" or trace.nominal_interval_ns <= 0:
        return missing("unsupported_trace_unit_or_cadence")
    if not trace.t_ns or any(not math.isfinite(v) for v in trace.values):
        return missing("missing_or_nonfinite_power_samples")
    offset = uncertainty = 0
    if trace.clock_domain != episode.clock_domain:
        mappings = [m for m in episode.clock_mappings
                    if m.trace_domain == trace.clock_domain
                    and m.episode_domain == episode.clock_domain]
        if len(mappings) != 1:
            return missing("missing_or_ambiguous_clock_mapping")
        offset, uncertainty = mappings[0].offset_ns, mappings[0].uncertainty_ns
        if uncertainty < 0:
            return missing("invalid_clock_uncertainty")
        if uncertainty:
            flags.append("clock_mapping_uncertainty")
    if windows is None:
        timing = episode_token_windows(episode)
        flags.extend(timing.flags)
        windows = timing.windows
    router = episode.router_log
    if router is None or len(windows) != len(router.phase):
        return missing("missing_decode_token_timing")
    if any(w.token_index != i or w.end_ns <= w.start_ns
           for i, w in enumerate(windows)):
        return missing("invalid_decode_token_timing")
    decode = [w for w, phase in zip(windows, router.phase) if phase == "decode"]
    if len(decode) != count or not decode:
        return missing("decode_count_mismatch_or_empty")
    if any(b.start_ns < a.end_ns for a, b in zip(decode, decode[1:])):
        return missing("overlapping_decode_token_windows")
    interval = trace.nominal_interval_ns
    times = [t+offset for t in trace.t_ns]
    cells = [(max(t-interval, times[i-1] if i else t-interval), t, value-baseline_w)
             for i, (t, value) in enumerate(zip(times, trace.values))]
    if any(b-a != interval for a, b in zip(times, times[1:])):
        flags.append("irregular_sample_cadence")
    if trace.duty_fraction is not None and trace.duty_fraction < 1.0:
        flags.append("duty_cycled_apparent_energy")
    token_energies: list[float] = []
    cell_weights_s = [0.0]*len(cells)
    coverage_ns = 0
    cell_starts = [cell[0] for cell in cells]
    # Independent overlap integration preserves phase/tool gaps without interpolating them.
    for token in decode:
        terms = []
        first = bisect.bisect_right(times, token.start_ns)
        last = bisect.bisect_left(cell_starts, token.end_ns)
        for i in range(first, last):
            left, right, watts = cells[i]
            overlap = max(0, min(right, token.end_ns)-max(left, token.start_ns))
            if overlap:
                seconds = overlap/NS_PER_SECOND
                terms.append(watts*seconds)
                cell_weights_s[i] += seconds
                coverage_ns += overlap
        token_energies.append(math.fsum(terms))
    duration_ns = sum(w.end_ns-w.start_ns for w in decode)
    coverage = coverage_ns/duration_ns
    if coverage_ns < duration_ns:
        flags.append("incomplete_decode_coverage")
    duration_s = duration_ns/NS_PER_SECOND
    if (reference_decode_duration_ns is not None
            and (not isinstance(reference_decode_duration_ns, int)
                 or isinstance(reference_decode_duration_ns, bool)
                 or not 0 <= reference_decode_duration_ns <= duration_ns)):
        return missing("invalid_reference_decode_duration")
    # Subtract nominal compute energy, preserving platform power during added
    # blocking time. The trace already contains that power: do not add a pulse.
    stall_energy = (baseline_w*(duration_ns-reference_decode_duration_ns)/NS_PER_SECOND
                    if reference_decode_duration_ns is not None else 0.0)
    if stall_energy and coverage_ns < duration_ns:
        # A total nominal duration cannot locate missing stall energy. Keep it
        # missing rather than filling unsampled cells with the model reference.
        return missing("stall_energy_reference_requires_complete_decode_coverage")
    if stall_energy:
        flags.append("nominal_compute_energy_reference")
        flags.append("variance_excludes_running_stall_energy")
    if coverage_ns == 0:
        return missing("no_decode_sample_coverage")
    quantum = trace.resolution
    if quantum is None or not math.isfinite(quantum) or quantum < 0:
        flags.append("unknown_power_resolution")
        half_width = None
    else:
        # q/2 * observed duration is a deterministic rounding bound.
        quantization_bound = quantum/2 * sum(cell_weights_s)
        independent_noise = noise_multiplier*noise_std_w*math.sqrt(
            math.fsum(w*w for w in cell_weights_s))
        # A clock shift moves both boundaries of each disjoint observed decode
        # interval. Explicit token timing may contain multiple intervals per turn.
        intervals: list[tuple[int, int]] = []
        for window in decode:
            if intervals and window.start_ns == intervals[-1][1]:
                intervals[-1] = (intervals[-1][0], window.end_ns)
            else:
                intervals.append((window.start_ns, window.end_ns))
        clock_bound = (2*len(intervals)*uncertainty/NS_PER_SECOND
                       * max(abs(v-baseline_w) for v in trace.values))
        half_width = (quantization_bound+independent_noise+attribution_floor_j+clock_bound)/count
    rate = count/duration_s
    amplitude = None
    # The Nyquist limit derives from the sensor cadence, irrespective of polling rate.
    if rate >= NS_PER_SECOND/(2*interval):
        flags.append("token_rate_at_or_above_nyquist")
    else:
        selected = [(right, watts, weight) for (left, right, watts), weight
                    in zip(cells, cell_weights_s) if weight > 0]
        weight_sum = math.fsum(w for _, _, w in selected)
        mean_power = math.fsum(v*w for _, v, w in selected)/weight_sum
        origin = episode.start_ns
        real = math.fsum((v-mean_power)*w*math.cos(
            2*math.pi*rate*(t-origin)/NS_PER_SECOND) for t, v, w in selected)
        imag = math.fsum((v-mean_power)*w*math.sin(
            2*math.pi*rate*(t-origin)/NS_PER_SECOND) for t, v, w in selected)
        amplitude = 2*math.hypot(real, imag)/weight_sum
        flags.append("spectrum_includes_acquisition_transfer_function")
    if any(w.end_ns-w.start_ns < interval for w in decode):
        flags.append("per_token_energy_underresolved")
    if trace.averaging_window_ns and trace.averaging_window_ns > interval:
        flags.append("noise_independence_requires_calibration")
    return PowerFeatures(episode.episode_id, count,
                         (math.fsum(token_energies)+stall_energy)/count,
                         statistics.pvariance(token_energies) if len(token_energies) > 1 else 0.0,
                         rate, amplitude, half_width, coverage,
                         tuple(dict.fromkeys(flags)))


def recover_routing(
    observations: Sequence[RoutingObservation], *, feature_name: str,
) -> RoutingRecovery:
    """Scalar inverse regression, separately for each named power feature.

    Every task group is predicted only from other groups. Missing observations
    remain in the prediction list with None and a flag; they are never silently
    converted to zeros. Features and routing statistics must be fixed before
    evaluating the held-out groups; selecting the best feature here is leakage.
    """
    allowed = ("energy_per_decode_token_j", "token_energy_variance_j2",
               "token_rate_amplitude_w")
    flags: list[str] = []
    if feature_name not in allowed:
        return RoutingRecovery(feature_name, None, None, None, (),
                               ("unknown_power_feature",))
    values = [(o, getattr(o.features, feature_name)) for o in observations]
    valid = [(o, x) for o, x in values if x is not None and math.isfinite(x)
             and math.isfinite(o.routing_statistic)]
    if len(valid) != len(values):
        flags.append("missing_observations")
    predictions: list[tuple[str, float | None]] = []
    paired_truth: list[float] = []
    paired_prediction: list[float] = []
    for observation, value in values:
        prediction = None
        training = [(o.routing_statistic, x) for o, x in valid if o.group != observation.group]
        if (value is not None and math.isfinite(value)
                and math.isfinite(observation.routing_statistic) and len(training) >= 2):
            mean_x = statistics.fmean(x for _, x in training)
            mean_y = statistics.fmean(y for y, _ in training)
            sxx = math.fsum((x-mean_x)**2 for _, x in training)
            if sxx:
                slope = math.fsum((x-mean_x)*(y-mean_y) for y, x in training)/sxx
                prediction = mean_y+slope*(value-mean_x)
            else:
                flags.append("constant_training_power_feature")
        else:
            flags.append("insufficient_grouped_training_data")
        predictions.append((observation.episode_id, prediction))
        if prediction is not None:
            paired_truth.append(observation.routing_statistic)
            paired_prediction.append(prediction)
    observed = pearson([o.routing_statistic for o, _ in valid], [x for _, x in valid])
    if observed is None:
        flags.append("undefined_observed_correlation")
    held_out = pearson(paired_truth, paired_prediction)
    rmse = (math.sqrt(statistics.fmean((a-b)**2 for a, b in zip(paired_truth, paired_prediction)))
            if paired_prediction else None)
    return RoutingRecovery(feature_name, observed, held_out, rmse,
                           tuple(predictions), tuple(dict.fromkeys(flags)),
                           fisher_interval_95(held_out, len(paired_truth)),
                           len(paired_truth), len(paired_truth))


def required_correlation(
    *, stage_a_effect_sd: float, n_per_condition: int, alpha: float,
    power: float, comparisons: int,
) -> CorrelationRequirement:
    """Normal-design requirement under d_power = |r| * |d_stageA|.

    Independent equal-sized groups, equal within-group variance, two-sided
    Bonferroni alpha and known-variance normal approximation. Repeated episodes
    of the same task are not independent units; n is independent task groups.
    """
    if (not all(math.isfinite(v) for v in (stage_a_effect_sd, alpha, power))
            or not 0 < alpha < 1 or not 0.5 <= power < 1
            or not isinstance(n_per_condition, int) or isinstance(n_per_condition, bool)
            or not isinstance(comparisons, int) or isinstance(comparisons, bool)
            or n_per_condition <= 0 or comparisons <= 0):
        return CorrelationRequirement(None, False, ("invalid_detection_design",))
    if stage_a_effect_sd == 0:
        return CorrelationRequirement(None, False, ("stage_a_has_no_effect",))
    normal = statistics.NormalDist()
    try:
        tail = alpha/(2*comparisons)
        if tail == 0.0:
            return CorrelationRequirement(None, False, ("design_tail_below_float_range",))
        minimum = ((-normal.inv_cdf(tail) + normal.inv_cdf(power))
                   * math.sqrt(2/n_per_condition)/abs(stage_a_effect_sd))
    except (ArithmeticError, statistics.StatisticsError):
        return CorrelationRequirement(None, False, ("detection_design_outside_float_range",))
    if not math.isfinite(minimum):
        return CorrelationRequirement(None, False, ("required_correlation_exceeds_float_range",))
    return CorrelationRequirement(minimum, minimum <= 1.0,
                                  () if minimum <= 1.0 else ("required_correlation_exceeds_one",))


def plan_detectability(
    sensor: SensorModel, *, stage_a_effect_sd: float, n_per_condition: int,
    alpha: float, power: float, comparisons: int, routing_stat_sd: float,
    traffic_energy_slope_j_per_token: float, decode_tokens: int,
    decode_duration_s: float, phase_bias_std_j: float,
    systematic_contrast_half_width_j: float,
    routing_energy_residual_std_j_per_token: float = 0.0,
) -> DetectionPlan:
    """Conditional linear/noise forecast for a sensor and a Stage A effect.

    phase_bias_std_j MUST come from phase-swept repetitions or calibration;
    a duty fraction alone cannot identify energy missed between acquisitions.
    White measurement noise averages down; quantization and systematic bounds
    do not. The transfer slope must describe energy visible on this sensor's
    channel, not unmeasured host DRAM energy on a GPU-only NVML channel.
    """
    requirement = required_correlation(stage_a_effect_sd=stage_a_effect_sd,
                                       n_per_condition=n_per_condition,
                                       alpha=alpha, power=power, comparisons=comparisons)
    flags = list(requirement.flags)
    numeric = (stage_a_effect_sd, routing_stat_sd, traffic_energy_slope_j_per_token, decode_duration_s,
               phase_bias_std_j, systematic_contrast_half_width_j,
               sensor.noise_std_w, sensor.quantum_w, routing_energy_residual_std_j_per_token)
    if (not all(math.isfinite(v) for v in numeric) or not isinstance(decode_tokens, int) or isinstance(decode_tokens, bool)
            or decode_tokens <= 0 or decode_duration_s <= 0
            or not isinstance(sensor.interval_ns, int) or isinstance(sensor.interval_ns, bool)
            or not isinstance(sensor.averaging_window_ns, int)
            or isinstance(sensor.averaging_window_ns, bool)
            or sensor.interval_ns <= 0 or sensor.averaging_window_ns <= 0
            or min(routing_stat_sd, phase_bias_std_j, systematic_contrast_half_width_j,
                   sensor.noise_std_w, sensor.quantum_w,
                   routing_energy_residual_std_j_per_token) < 0):
        return DetectionPlan(requirement.minimum_absolute_correlation, None, None, None,
                             False, tuple(dict.fromkeys(flags + ["invalid_sensor_forecast"])))
    sample_s = max(sensor.interval_ns, sensor.averaging_window_ns)/NS_PER_SECOND
    # Variance of the integral of independent averaged readings: sigma_W^2 * T * dt.
    white_noise_j = sensor.noise_std_w*math.sqrt(decode_duration_s*sample_s)
    signal_sd = abs(traffic_energy_slope_j_per_token)*routing_stat_sd
    noise_sd = math.hypot(white_noise_j/decode_tokens, phase_bias_std_j/decode_tokens,
                         routing_energy_residual_std_j_per_token)
    correlation = (signal_sd/math.hypot(signal_sd, noise_sd)
                   if signal_sd or noise_sd else None)
    contrast = abs(stage_a_effect_sd)*signal_sd*decode_tokens
    # Two condition means can each carry q/2*T rounding bias of opposite sign.
    bound = systematic_contrast_half_width_j + sensor.quantum_w*decode_duration_s
    if sensor.averaging_window_ns < sensor.interval_ns:
        flags.append("requires_measured_random_phase_bias")
    if routing_energy_residual_std_j_per_token:
        flags.append("routing_to_energy_residual_in_forecast")
    if signal_sd == 0:
        flags.append("no_routing_energy_coupling")
    if contrast <= bound:
        flags.append("contrast_below_systematic_bound")
    detectable = (requirement.feasible and correlation is not None
                  and requirement.minimum_absolute_correlation is not None
                  and correlation >= requirement.minimum_absolute_correlation and contrast > bound)
    flags.append("conditional_forecast_not_hardware_validation")
    return DetectionPlan(requirement.minimum_absolute_correlation, correlation,
                         contrast, bound, detectable, tuple(dict.fromkeys(flags)))
