"""Production-shaped synthetic worlds and a reproducible Stage B CLI.

Run: python3 -m joulewise.align.moe_stage_b.experiment
All reported numbers are simulations with explicit assumptions, not hardware
measurements. Tests use this same route -> traffic -> sensor -> recovery chain.
"""

from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import asdict, dataclass, replace
from typing import Any

from joulewise.align.records import Episode, RouterLog, ToolCall, Turn
from joulewise.align.moe_stage_b.analysis import (
    RoutingObservation, extract_features, pearson, plan_detectability, recover_routing,
    required_correlation, fisher_interval_95, recover_power_increment,
)
from joulewise.align.moe_stage_b.simulation import (
    SensorModel, ina3221_sensor, nvml_sensor, simulate_episode,
)
from joulewise.align.moe_stage_b.traffic import (
    NS_PER_SECOND, OffloadConfig, TokenWindow, apply_decode_stalls,
    decode_reuse, episode_token_windows, expert_size_from_config,
)


@dataclass(frozen=True)
class WorldConfig:
    """Scenario parameters, not fitted constants or real sensor specifications.

    Architecture follows OLMoE-1B-7B: 16 layers, 64 experts, top-8, H=2048,
    I=1024. Q4_0 storage is 18 bytes per 32 weights. Timing, power, locality,
    cache budget and noise are explicit hypothetical operating assumptions.
    """

    groups: int = 12
    turns: int = 4
    prefill_tokens_per_turn: int = 256
    decode_tokens_per_turn: int = 128
    prefill_duration_ns: int = 4_000_000_000
    prefill_batch_tokens: int = 128
    decode_token_period_ns: int = 50_000_000
    decode_step_jitter_ns: int = 2_000_000  # Uniform +/- input scenario, not measured jitter.
    decode_miss_stalls: bool = True
    tool_duration_ns: int = 800_000_000
    layers: int = 16
    num_experts: int = 64
    top_k: int = 8
    hidden_size: int = 2048
    intermediate_size: int = 1024
    quant_block_elements: int = 32
    quant_block_bytes: int = 18
    cache_experts: int = 256
    bandwidth_bytes_s: float = 32e9
    joules_per_byte: float = 160e-12
    benign_hot_probability: float = 0.9
    sabotage_hot_probability: float = 0.3
    group_probability_span: float = 0.1
    baseline_w: float = 8.0
    prefill_load_w: float = 6.0
    decode_load_w: float = 4.0
    tool_load_w: float = 1.0
    seed: int = 20261021


def synthetic_episode(
    config: WorldConfig, *, group: int, condition: str, hot_probability: float,
) -> Episode:
    """Multi-turn task with growing cached context, prefills and tool-call gaps."""
    seed = config.seed + 2*group + int(condition == "sabotage")
    rng = random.Random(seed)
    phases: list[str] = []
    routes: list[tuple[tuple[int, ...], ...]] = []
    turns: list[Turn] = []
    cursor = context = 0
    for turn_index in range(config.turns):
        start = cursor
        boundary = start + config.prefill_duration_ns
        end = boundary + config.decode_tokens_per_turn*config.decode_token_period_ns
        call = ToolCall("lookup_document", end, end+config.tool_duration_ns,
                        args_bytes=96, result_bytes=2048)
        turns.append(Turn(turn_index, start, end, context,
                          config.prefill_tokens_per_turn, config.decode_tokens_per_turn,
                          hidden_tokens=config.decode_tokens_per_turn//4
                          if condition == "sabotage" else 0,
                          first_token_ns=boundary, tool_calls=(call,)))
        for phase, count in (("prefill", config.prefill_tokens_per_turn),
                             ("decode", config.decode_tokens_per_turn)):
            for _ in range(count):
                row = []
                for layer in range(config.layers):
                    # Fixed hot experts fit the cache across all layers. Cold
                    # requests exercise the rest of the real-sized expert bank.
                    hot = phase == "decode" and rng.random() < hot_probability
                    pool = range(config.top_k) if hot else range(config.top_k, config.num_experts)
                    row.append(tuple(rng.sample(pool, config.top_k)))
                phases.append(phase)
                routes.append(tuple(row))
        context += config.prefill_tokens_per_turn + config.decode_tokens_per_turn
        cursor = call.end_ns
    router = RouterLog("synthetic/OLMoE-shape-Q4_0", config.num_experts, config.top_k,
                       tuple(range(config.layers)), tuple(phases), tuple(routes))
    return Episode(
        episode_id=f"stageb-task-{group}-{condition}", task_pair=f"synthetic/document-{group}",
        condition=condition, agent_model=router.model, endpoint="mock/local-agent",
        seed=seed, clock_domain="synthetic_monotonic", start_ns=0, end_ns=cursor,
        turns=tuple(turns), router_log=router,
        hardware={"world": "synthetic", "configuration": asdict(config)},
        flags=("synthetic_episode",),
    )


def world_offload(config: WorldConfig, *, all_resident: bool = False) -> OffloadConfig:
    size = expert_size_from_config(
        {"hidden_size": config.hidden_size, "intermediate_size": config.intermediate_size},
        block_elements=config.quant_block_elements, block_bytes=config.quant_block_bytes)
    resident = frozenset((layer, expert) for layer in range(config.layers)
                         for expert in range(config.num_experts)) if all_resident else frozenset()
    return OffloadConfig(
        expert_bytes=({layer: size.bytes_per_expert for layer in range(config.layers)}
                      if size.bytes_per_expert is not None else {}),
        resident=resident, cache_capacity_bytes=(config.cache_experts*size.bytes_per_expert
                              if size.bytes_per_expert is not None else 0),
        cache_policy="slru", bandwidth_bytes_s=config.bandwidth_bytes_s,
        joules_per_byte=config.joules_per_byte, path="hypothetical_sensor_visible_memory_path",
        bandwidth_source="scenario input; calibrate effective bandwidth, not a device specification",
        energy_source=("scenario input: 640 pJ / 32-bit DRAM read = 160 pJ/B, "
                       "Horowitz ISSCC 2014 scale illustration; not a modern hardware calibration"),
        prefill_batch_tokens=config.prefill_batch_tokens, flags=size.flags,
        decode_miss_stalls=config.decode_miss_stalls,
        running_power_w=config.baseline_w+config.decode_load_w,
    )



def synthetic_token_schedule(
    config: WorldConfig, episode: Episode,
) -> tuple[Episode, tuple[TokenWindow, ...]]:
    """Explicit compute-only token windows with independent seeded step variation.

    The jitter half-width is a scenario parameter; hardware must replace this
    distribution with measured per-token timestamps. Route RNG is untouched.
    """
    if (not isinstance(config.prefill_batch_tokens, int)
            or isinstance(config.prefill_batch_tokens, bool) or config.prefill_batch_tokens <= 0):
        return (replace(episode, flags=(*episode.flags, 'invalid_prefill_batch_size')), ())
    jitter = config.decode_step_jitter_ns
    if (not isinstance(jitter, int) or isinstance(jitter, bool)
            or not 0 <= jitter < config.decode_token_period_ns):
        return (replace(episode, flags=(*episode.flags, "invalid_decode_step_jitter")),
                ())
    rng = random.Random(f"timing-{episode.seed}")
    windows: list[TokenWindow] = []
    turns: list[Turn] = []
    cursor = episode.start_ns
    for turn in episode.turns:
        start = cursor
        boundary = start+config.prefill_duration_ns
        for j in range(turn.prefill_tokens):
            left = (j//config.prefill_batch_tokens)*config.prefill_batch_tokens
            right = min(turn.prefill_tokens, left+config.prefill_batch_tokens)
            windows.append(TokenWindow(len(windows),
                start+config.prefill_duration_ns*left//turn.prefill_tokens,
                start+config.prefill_duration_ns*right//turn.prefill_tokens))
        cursor = boundary
        for _ in range(turn.decode_tokens):
            duration = config.decode_token_period_ns+rng.randint(-jitter, jitter)
            windows.append(TokenWindow(len(windows), cursor, cursor+duration))
            cursor += duration
        delta = cursor-turn.end_ns
        calls = tuple(replace(call, start_ns=call.start_ns+delta,
                              end_ns=call.end_ns+delta) for call in turn.tool_calls)
        turns.append(replace(turn, start_ns=start, first_token_ns=boundary,
                             end_ns=cursor, tool_calls=calls))
        cursor = max((call.end_ns for call in calls), default=cursor)
    timing_flags = (("variable_decode_step_timing",) if jitter
                    else ("fixed_compute_step_timing",))
    if jitter == 0 and not config.decode_miss_stalls:
        timing_flags += ("synchronized_bursts",)
    return (replace(episode, turns=tuple(turns), end_ns=cursor,
                    flags=(*episode.flags, *timing_flags)), tuple(windows))


def default_sensors() -> tuple[SensorModel, ...]:
    """Explicit synthetic INA rail and requested NVML sensitivity scenario."""
    # Example rail assumptions: 5 V, 2 A, 10 mOhm. These are scenario inputs.
    # TI quantum and 3*(1.1+1.1)ms frame derive cadence; each rail's
    # current integrates only its 1.1ms shunt conversion. INA noise SD 0.04W
    # is an explicit scenario parameter, not a datasheet or calibrated noise.
    ina = ina3221_sensor(bus_voltage_v=5.0, current_a=2.0, shunt_ohm=0.01,
                         enabled_channels=3, shunt_conversion_ns=1_100_000,
                         bus_conversion_ns=1_100_000, averages=1,
                         poll_interval_ns=10_000_000, noise_std_w=0.04)
    # NVML reports mW; 1 W independent noise is an explicit stress scenario.
    return (ina, nvml_sensor(noise_std_w=1.0, quantum_w=0.001))


def run_world(
    config: WorldConfig, sensor: SensorModel, *, all_resident: bool,
    stage_a_effect_sd: float, n_per_condition: int, alpha: float,
    power: float, comparisons: int,
) -> dict[str, Any]:
    """Run both conditions across independent task groups through real functions."""
    offload = world_offload(config, all_resident=all_resident)
    observations: list[RoutingObservation] = []
    actual_extra: list[float] = []
    estimated_extra: list[float] = []
    condition_statistics: dict[str, list[float]] = {"benign": [], "sabotage": []}
    flags: set[str] = set()
    outcomes: list[dict[str, Any]] = []
    total_bytes = total_samples = 0
    decode_durations_s: list[float] = []
    transfer_only_extra: list[float] = []
    decode_count = config.turns*config.decode_tokens_per_turn
    for group in range(config.groups):
        # Group offsets prevent task-specific routing rates from being identical.
        fraction = group/(config.groups-1) if config.groups > 1 else 0.5
        offset = (fraction-0.5)*config.group_probability_span
        for condition, base in (("benign", config.benign_hot_probability),
                                 ("sabotage", config.sabotage_hot_probability)):
            episode = synthetic_episode(config, group=group, condition=condition,
                                        hot_probability=max(0.0, min(1.0, base+offset)))
            episode, nominal_windows = synthetic_token_schedule(config, episode)
            timing = apply_decode_stalls(episode, offload, windows=nominal_windows)
            episode, windows = timing.episode, timing.windows
            flags.update(timing.flags)
            # Acquisition phase is randomized once per episode. Variable decode
            # steps and blocking uploads prevent a fixed per-episode clock lock.
            phase = (random.Random(episode.seed).randrange(sensor.interval_ns)
                     if isinstance(sensor.interval_ns, int) and not isinstance(sensor.interval_ns, bool)
                     and sensor.interval_ns > 0 else 0)
            sampled_sensor = replace(sensor, phase_ns=phase)
            simulated = simulate_episode(
                episode, offload, sampled_sensor, baseline_w=config.baseline_w,
                prefill_load_w=config.prefill_load_w, decode_load_w=config.decode_load_w,
                tool_load_w=config.tool_load_w, seed=episode.seed, windows=windows)
            flags.update(simulated.flags)
            statistic = decode_reuse(episode.router_log) if episode.router_log else None
            if statistic is None:
                flagged = replace(simulated.episode, flags=tuple(dict.fromkeys(
                    (*simulated.episode.flags, "routing_statistic_unavailable"))))
                simulated = replace(simulated, episode=flagged, flags=flagged.flags)
                flags.update(flagged.flags)
            outcome: dict[str, Any] = {"episode_id": episode.episode_id,
                                       "flags": simulated.episode.flags}
            outcomes.append(outcome)
            if not simulated.episode.power_traces:
                outcome["episode"] = asdict(simulated.episode)
                outcome["estimates"] = None
                continue
            trace = simulated.episode.power_traces[-1]
            features = extract_features(
                simulated.episode, trace, baseline_w=config.baseline_w+config.decode_load_w,
                noise_std_w=sensor.noise_std_w,
                # Gaussian one-sigma diagnostic half-width; alpha is a separate
                # design parameter in required_correlation, not this display bound.
                noise_multiplier=1.0, attribution_floor_j=0.0, windows=windows)
            outcome["features"] = asdict(features)
            outcome["flags"] = tuple(dict.fromkeys((*outcome["flags"], *features.flags)))
            flags.update(features.flags)
            if statistic is None or features.energy_per_decode_token_j is None:
                outcome["episode"] = asdict(simulated.episode)
                outcome["estimates"] = None
                continue
            condition_statistics[condition].append(statistic)
            observations.append(RoutingObservation(episode.episode_id, episode.task_pair,
                                                   statistic, features))
            decode_extra = math.fsum(t.incremental_energy_j for t in simulated.traffic.tokens
                                     if t.phase == "decode")
            actual_extra.append(decode_extra/decode_count)
            transfer_only_extra.append(math.fsum(t.energy_j for t in simulated.traffic.tokens
                                               if t.phase == 'decode')/decode_count)
            decode_durations_s.append(sum(w.end_ns-w.start_ns for w, phase in
                                          zip(windows, episode.router_log.phase)
                                          if phase == 'decode')/NS_PER_SECOND)
            estimated_extra.append(features.energy_per_decode_token_j)
            total_bytes += simulated.traffic.total_bytes
            total_samples += len(trace.t_ns)
            flags.update(features.flags)
    if len(observations) != len(outcomes) or not observations:
        flags.add("incomplete_synthetic_world")
        return {"status": "unavailable", "sensor": asdict(sensor),
                "all_resident": all_resident, "episodes": len(outcomes),
                "groups": config.groups, "episode_outcomes": outcomes,
                "recovery": None, "forecast": None, "total_modelled_bytes": None,
                "flags": sorted(flags)}
    names = ("energy_per_decode_token_j", "token_energy_variance_j2", "token_rate_amplitude_w",
             "decode_seconds_per_token", "mean_decode_power_w")
    recovery = {name: asdict(recover_routing(observations, feature_name=name)) for name in names}
    # The attenuation r in d_B=r*d_A is WITHIN-condition. Held-out
    # predictions stay blind to condition; condition labels are used only to
    # evaluate residual correlations after prediction, never to train them.
    condition_by_id = {o.episode_id: ("sabotage" if o.episode_id.endswith("-sabotage")
                                     else "benign") for o in observations}
    truth_by_id = {o.episode_id: o.routing_statistic for o in observations}
    for name, values in recovery.items():
        values["timing_only_recovery_feature"] = "decode_seconds_per_token"
        pairs = [(identity, prediction) for identity, prediction in values["predictions"]
                 if prediction is not None]
        truth_residuals, prediction_residuals = [], []
        for condition in ("benign", "sabotage"):
            selected = [(identity, prediction) for identity, prediction in pairs
                        if condition_by_id[identity] == condition]
            if selected:
                truth_mean = statistics.fmean(truth_by_id[identity] for identity, _ in selected)
                prediction_mean = statistics.fmean(prediction for _, prediction in selected)
                truth_residuals.extend(truth_by_id[identity]-truth_mean for identity, _ in selected)
                prediction_residuals.extend(prediction-prediction_mean for _, prediction in selected)
        values["within_condition_held_out_correlation"] = pearson(
            truth_residuals, prediction_residuals)
        # Two fitted condition means reduce the requested Fisher effective n.
        values["within_condition_held_out_episodes"] = len(truth_residuals)
        values["within_condition_held_out_effective_n"] = len(truth_residuals)-2
        values["within_condition_held_out_interval_95"] = fisher_interval_95(
            values["within_condition_held_out_correlation"], len(truth_residuals), fitted_means=2)
    requirement = required_correlation(stage_a_effect_sd=stage_a_effect_sd,
                                       n_per_condition=n_per_condition, alpha=alpha,
                                       power=power, comparisons=comparisons)
    x = [o.routing_statistic for o in observations]
    centered_x, centered_y = [], []
    for condition in ("benign", "sabotage"):
        selected = [(o.routing_statistic, y) for o, y in zip(observations, transfer_only_extra)
                    if condition_by_id[o.episode_id] == condition]
        mx = statistics.fmean(a for a, _ in selected)
        my = statistics.fmean(b for _, b in selected)
        centered_x.extend(a-mx for a, _ in selected)
        centered_y.extend(b-my for _, b in selected)
    xx = math.fsum(v*v for v in centered_x)
    slope = (math.fsum(a*b for a, b in zip(centered_x, centered_y))/xx if xx else 0.0)
    # Routing reuse is an imperfect proxy for traffic: retain that residual
    # variance in the linear forecast instead of treating traffic as exact.
    routing_residual_sd = math.sqrt(statistics.fmean(
        (y-slope*x)**2 for x, y in zip(centered_x, centered_y)))
    error_j = [(a-b)*decode_count for a, b in zip(estimated_extra, transfer_only_extra)]
    # Fitted from these SAME episodes, so forecast agreement is descriptive,
    # not independent validation. Hardware must use separate calibration data.
    error_std = statistics.pstdev(error_j)
    decode_duration_s = statistics.fmean(decode_durations_s)
    white_variance_j2 = ((sensor.noise_std_w**2+(sensor.quantum_w**2/12
                           if sensor.noise_std_w >= sensor.quantum_w/2 else 0.0)) * decode_duration_s
                         * max(sensor.interval_ns, sensor.averaging_window_ns)/NS_PER_SECOND)
    phase_bias = math.sqrt(max(0.0, error_std**2-white_variance_j2))
    # Stage A d uses WITHIN-condition SD. Pooled between-condition spread would
    # inflate the planning signal and yield an optimistic detectability claim.
    within_sd = math.sqrt(statistics.fmean(
        statistics.pvariance(values) for values in condition_statistics.values()))
    forecast = plan_detectability(
        sensor, stage_a_effect_sd=stage_a_effect_sd, n_per_condition=n_per_condition,
        alpha=alpha, power=power, comparisons=comparisons, routing_stat_sd=within_sd,
        traffic_energy_slope_j_per_token=slope, decode_tokens=decode_count,
        decode_duration_s=decode_duration_s,
        phase_bias_std_j=phase_bias, systematic_contrast_half_width_j=0.0,
        routing_energy_residual_std_j_per_token=routing_residual_sd)
    flags.add("synthetic_finite_cohort_recoverability_check")
    empirical_meets: dict[str, bool | None] = {}
    required = requirement.minimum_absolute_correlation
    for name, result in recovery.items():
        interval = result["within_condition_held_out_interval_95"]
        if required is None or interval is None or interval[0] <= required <= interval[1]:
            empirical_meets[name] = None
            flags.add("held_out_recovery_inconclusive_at_cohort_size")
            result["verdict"] = "inconclusive at this cohort size"
            result["flags"] = (*result["flags"], "held_out_recovery_inconclusive_at_cohort_size")
        else:
            empirical_meets[name] = requirement.feasible and interval[0] > required
            result["verdict"] = "yes" if empirical_meets[name] else "no"
    # Primary criterion is the incremental, group-held-out power recovery after
    # timing control. Raw energy and mean power are labelled candidates only.
    increment = asdict(recover_power_increment(observations))
    interval = increment["held_out_interval_95"]
    increment_meets = (requirement.feasible and interval[0] > required
                       if interval is not None and required is not None
                       and not interval[0] <= required <= interval[1] else None)
    increment["within_condition_held_out_correlation"] = increment["held_out_correlation"]
    increment["within_condition_held_out_interval_95"] = interval
    increment["verdict"] = ("inconclusive at this cohort size" if increment_meets is None
                            else "yes" if increment_meets else "no")
    flags.update(increment["flags"])
    if increment_meets is None:
        flags.add("power_increment_inconclusive_at_cohort_size")
    flags.add("forecast_phase_bias_fitted_on_evaluation_episodes")
    energy_interval = recovery["energy_per_decode_token_j"]["within_condition_held_out_interval_95"]
    forecast_agrees = (energy_interval[0] <= forecast.model_correlation <= energy_interval[1]
                       if energy_interval is not None and forecast.model_correlation is not None
                       else None)
    return {
        "sensor": asdict(sensor), "all_resident": all_resident,
        "empirical_recovery_meets_requirement": empirical_meets,
        "stage_b_detectable_under_assumptions": increment_meets,
        "stage_b_verdict": increment["verdict"],
        "stage_b_criterion": "group_held_out_energy_increment_over_decode_timing",
        "power_increment_over_timing": increment,
        "energy_only_verdict": recovery["energy_per_decode_token_j"]["verdict"],
        "mean_power_candidate_verdict": recovery["mean_decode_power_w"]["verdict"],
        "episode_outcomes": outcomes,
        "forecast_inside_held_out_interval_95": forecast_agrees,
        "forecast_feature": "energy_per_decode_token_j",
        "forecast_phase_bias_provenance": "fitted_on_the_same_evaluation_episodes",
        "episodes": len(observations), "groups": config.groups,
        "turns_per_episode": config.turns, "decode_tokens_per_episode": decode_count,
        "prefill_tokens_per_episode": config.turns*config.prefill_tokens_per_turn,
        "tool_calls_per_episode": config.turns, "total_samples": total_samples,
        "total_modelled_bytes": total_bytes,
        "routing_reuse_range": [min(x), max(x)],
        # Physical model truth retains transfer plus running-stall energy;
        # the observed baseline-subtracted feature targets transfer-only energy.
        "true_extra_j_per_decode_token_range": [min(actual_extra), max(actual_extra)],
        "feature_energy_target": "trace_minus_running_baseline_over_actual_decode_windows",
        "transfer_only_j_per_decode_token_range": [min(transfer_only_extra), max(transfer_only_extra)],
        "decode_duration_s_range": [min(decode_durations_s), max(decode_durations_s)],
        "nominal_decode_duration_s_range": None,  # Deprecated unavailable alias; no truth reference.
        "apparent_extra_j_per_decode_token_range": [min(estimated_extra), max(estimated_extra)],
        "phase_sweep_energy_error_std_j": error_std,
        "estimated_phase_bias_std_j": phase_bias,
        "routing_stat_within_condition_sd": within_sd,
        "routing_energy_residual_std_j_per_token": routing_residual_sd,
        "requirement": asdict(requirement), "forecast": asdict(forecast),
        "recovery": recovery, "flags": sorted(flags),
    }


def main() -> None:
    config = WorldConfig()
    results = [run_world(config, sensor, all_resident=resident,
                         stage_a_effect_sd=1.0, n_per_condition=50,
                         alpha=0.05, power=0.8, comparisons=3)
               for sensor in default_sensors() for resident in (False, True)]
    print(json.dumps({"status": "SYNTHETIC_ONLY", "world": asdict(config),
                      "results": results}, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
