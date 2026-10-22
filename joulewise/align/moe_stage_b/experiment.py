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
    RoutingObservation, extract_features, plan_detectability, recover_routing,
    required_correlation,
)
from joulewise.align.moe_stage_b.simulation import (
    SensorModel, ina3221_sensor, nvml_sensor, simulate_episode,
)
from joulewise.align.moe_stage_b.traffic import (
    NS_PER_SECOND, OffloadConfig, decode_reuse, expert_size_from_config,
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
    if size.bytes_per_expert is None:
        raise ValueError("synthetic world has invalid expert storage dimensions")
    resident = frozenset((layer, expert) for layer in range(config.layers)
                         for expert in range(config.num_experts)) if all_resident else frozenset()
    return OffloadConfig(
        expert_bytes={layer: size.bytes_per_expert for layer in range(config.layers)},
        resident=resident, cache_capacity_bytes=config.cache_experts*size.bytes_per_expert,
        cache_policy="slru", bandwidth_bytes_s=config.bandwidth_bytes_s,
        joules_per_byte=config.joules_per_byte, path="hypothetical_sensor_visible_memory_path",
        bandwidth_source="scenario input; calibrate effective bandwidth, not a device specification",
        energy_source=("scenario input: 640 pJ / 32-bit DRAM read = 160 pJ/B, "
                       "Horowitz ISSCC 2014 scale illustration; not a modern hardware calibration"),
        prefill_batch_tokens=config.prefill_batch_tokens,
    )


def default_sensors() -> tuple[SensorModel, ...]:
    """Explicit synthetic INA rail and requested NVML sensitivity scenario."""
    # Example rail assumptions: 5 V, 2 A, 10 mOhm. These are scenario inputs.
    # The TI quantum and 3*(1.1+1.1)ms conversion frame derive the sensor shape.
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
    total_bytes = total_samples = 0
    decode_count = config.turns*config.decode_tokens_per_turn
    for group in range(config.groups):
        # Group offsets prevent task-specific routing rates from being identical.
        fraction = group/(config.groups-1) if config.groups > 1 else 0.5
        offset = (fraction-0.5)*config.group_probability_span
        for condition, base in (("benign", config.benign_hot_probability),
                                 ("sabotage", config.sabotage_hot_probability)):
            episode = synthetic_episode(config, group=group, condition=condition,
                                        hot_probability=max(0.0, min(1.0, base+offset)))
            # A deterministic, seeded acquisition-phase sweep avoids a synchronized
            # 20 Hz token stream always falling in the same NVML blind interval.
            phase = random.Random(episode.seed).randrange(sensor.interval_ns)
            sampled_sensor = replace(sensor, phase_ns=phase)
            simulated = simulate_episode(
                episode, offload, sampled_sensor, baseline_w=config.baseline_w,
                prefill_load_w=config.prefill_load_w, decode_load_w=config.decode_load_w,
                tool_load_w=config.tool_load_w, seed=episode.seed)
            flags.update(simulated.flags)
            trace = simulated.episode.power_traces[-1]
            features = extract_features(
                simulated.episode, trace, baseline_w=config.baseline_w+config.decode_load_w,
                noise_std_w=sensor.noise_std_w,
                # Gaussian one-sigma diagnostic half-width; alpha is a separate
                # design parameter in required_correlation, not this display bound.
                noise_multiplier=1.0, attribution_floor_j=0.0)
            statistic = decode_reuse(episode.router_log)
            if statistic is None:
                raise ValueError("world needs adjacent decode tokens")
            condition_statistics[condition].append(statistic)
            observations.append(RoutingObservation(episode.episode_id, episode.task_pair,
                                                   statistic, features))
            decode_extra = math.fsum(t.energy_j for t in simulated.traffic.tokens
                                     if t.phase == "decode")
            actual_extra.append(decode_extra/decode_count)
            estimated_extra.append(features.energy_per_decode_token_j)
            total_bytes += simulated.traffic.total_bytes
            total_samples += len(trace.t_ns)
            flags.update(features.flags)
    names = ("energy_per_decode_token_j", "token_energy_variance_j2", "token_rate_amplitude_w")
    recovery = {name: asdict(recover_routing(observations, feature_name=name)) for name in names}
    requirement = required_correlation(stage_a_effect_sd=stage_a_effect_sd,
                                       n_per_condition=n_per_condition, alpha=alpha,
                                       power=power, comparisons=comparisons)
    x = [o.routing_statistic for o in observations]
    x_mean, y_mean = statistics.fmean(x), statistics.fmean(actual_extra)
    xx = math.fsum((v-x_mean)**2 for v in x)
    slope = math.fsum((a-x_mean)*(b-y_mean) for a, b in zip(x, actual_extra))/xx if xx else 0.0
    error_j = [(a-b)*decode_count for a, b in zip(estimated_extra, actual_extra)]
    # Phase/noise error is measured from this synthetic sweep only. A real forecast
    # must replace it with phase-swept hardware repetitions on the same channel.
    error_std = statistics.pstdev(error_j)
    decode_duration_s = decode_count*config.decode_token_period_ns/NS_PER_SECOND
    white_variance_j2 = (sensor.noise_std_w**2 * decode_duration_s
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
        decode_duration_s=decode_count*config.decode_token_period_ns/NS_PER_SECOND,
        phase_bias_std_j=phase_bias, systematic_contrast_half_width_j=0.0)
    return {
        "sensor": asdict(sensor), "all_resident": all_resident,
        "episodes": len(observations), "groups": config.groups,
        "turns_per_episode": config.turns, "decode_tokens_per_episode": decode_count,
        "prefill_tokens_per_episode": config.turns*config.prefill_tokens_per_turn,
        "tool_calls_per_episode": config.turns, "total_samples": total_samples,
        "total_modelled_bytes": total_bytes,
        "routing_reuse_range": [min(x), max(x)],
        "true_extra_j_per_decode_token_range": [min(actual_extra), max(actual_extra)],
        "apparent_extra_j_per_decode_token_range": [min(estimated_extra), max(estimated_extra)],
        "phase_sweep_energy_error_std_j": error_std,
        "estimated_phase_bias_std_j": phase_bias,
        "routing_stat_within_condition_sd": within_sd,
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
