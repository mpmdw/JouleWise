"""Decode power features, grouped routing recovery and conditional Stage B power.

All decisions remain diagnostics with flags. Statistical design inputs are
parameters; synthetic results never establish a sensor's real detectability.
"""

from __future__ import annotations

import math
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
    mx, my = statistics.fmean(x), statistics.fmean(y)
    xx = math.fsum((v-mx)**2 for v in x)
    yy = math.fsum((v-my)**2 for v in y)
    if xx == 0.0 or yy == 0.0:
        return None
    value = math.fsum((a-mx)*(b-my) for a, b in zip(x, y))/math.sqrt(xx*yy)
    # Cauchy-Schwarz bounds the mathematical value; rounding can stray outside.
    return max(-1.0, min(1.0, value))


def extract_features(
    episode: Episode, trace: PowerTrace, *, baseline_w: float,
    noise_std_w: float, noise_multiplier: float, attribution_floor_j: float,
    windows: Sequence[TokenWindow] | None = None,
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
    # Independent overlap integration preserves phase/tool gaps without interpolating them.
    for token in decode:
        terms = []
        for i, (left, right, watts) in enumerate(cells):
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
        # Shifting each turn boundary by u changes at most 2*u*max|P-baseline| energy.
        clock_bound = (2*len(episode.turns)*uncertainty/NS_PER_SECOND
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
                         math.fsum(token_energies)/count,
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
                           tuple(predictions), tuple(dict.fromkeys(flags)))


def required_correlation(
    *, stage_a_effect_sd: float, n_per_condition: int, alpha: float,
    power: float, comparisons: int,
) -> CorrelationRequirement:
    """Normal-design requirement under d_power = |r| * |d_stageA|.

    Independent equal-sized groups, equal within-group variance, two-sided
    Bonferroni alpha and known-variance normal approximation. Repeated episodes
    of the same task are not independent units; n is independent task groups.
    """
    if (not math.isfinite(stage_a_effect_sd) or not 0 < alpha < 1
            or not 0.5 < power < 1 or n_per_condition <= 0 or comparisons <= 0):
        return CorrelationRequirement(None, False, ("invalid_detection_design",))
    if stage_a_effect_sd == 0:
        return CorrelationRequirement(None, False, ("stage_a_has_no_effect",))
    normal = statistics.NormalDist()
    minimum = ((-normal.inv_cdf(alpha/(2*comparisons)) + normal.inv_cdf(power))
               * math.sqrt(2/n_per_condition)/abs(stage_a_effect_sd))
    return CorrelationRequirement(minimum, minimum <= 1.0,
                                  () if minimum <= 1.0 else ("required_correlation_exceeds_one",))


def plan_detectability(
    sensor: SensorModel, *, stage_a_effect_sd: float, n_per_condition: int,
    alpha: float, power: float, comparisons: int, routing_stat_sd: float,
    traffic_energy_slope_j_per_token: float, decode_tokens: int,
    decode_duration_s: float, phase_bias_std_j: float,
    systematic_contrast_half_width_j: float,
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
    numeric = (routing_stat_sd, traffic_energy_slope_j_per_token, decode_duration_s,
               phase_bias_std_j, systematic_contrast_half_width_j,
               sensor.noise_std_w, sensor.quantum_w)
    if (not all(math.isfinite(v) for v in numeric) or decode_tokens <= 0
            or decode_duration_s <= 0 or sensor.interval_ns <= 0
            or sensor.averaging_window_ns <= 0
            or min(routing_stat_sd, phase_bias_std_j, systematic_contrast_half_width_j,
                   sensor.noise_std_w, sensor.quantum_w) < 0):
        return DetectionPlan(requirement.minimum_absolute_correlation, None, None, None,
                             False, tuple(dict.fromkeys(flags + ["invalid_sensor_forecast"])))
    sample_s = max(sensor.interval_ns, sensor.averaging_window_ns)/NS_PER_SECOND
    # Variance of the integral of independent averaged readings: sigma_W^2 * T * dt.
    white_noise_j = sensor.noise_std_w*math.sqrt(decode_duration_s*sample_s)
    signal_sd = abs(traffic_energy_slope_j_per_token)*routing_stat_sd
    noise_sd = math.hypot(white_noise_j, phase_bias_std_j)/decode_tokens
    correlation = (signal_sd/math.hypot(signal_sd, noise_sd)
                   if signal_sd or noise_sd else None)
    contrast = abs(stage_a_effect_sd)*signal_sd*decode_tokens
    # Two condition means can each carry q/2*T rounding bias of opposite sign.
    bound = systematic_contrast_half_width_j + sensor.quantum_w*decode_duration_s
    if sensor.averaging_window_ns < sensor.interval_ns:
        flags.append("requires_measured_random_phase_bias")
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
