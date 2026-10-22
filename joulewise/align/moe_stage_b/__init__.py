"""MoE Stage B traffic, power simulation and routing-visibility diagnostics.

No hardware is accessed and no optional packages are imported by this package.
The reference module is an independent test oracle, not a production estimator.
"""

from joulewise.align.moe_stage_b.analysis import (
    CorrelationRequirement, DetectionPlan, PowerFeatures, RoutingObservation,
    RoutingRecovery, extract_features, pearson, plan_detectability,
    recover_routing, required_correlation, fisher_interval_95, recover_power_increment,
)
from joulewise.align.moe_stage_b.simulation import (
    PowerPulse, SensorModel, SimulatedEpisode, SimulatedTrace, ina3221_sensor,
    nvml_sensor, simulate_episode, simulate_trace,
)
from joulewise.align.moe_stage_b.traffic import (
    ExpertSize, OffloadConfig, TimingResult, TokenTraffic, TokenWindow,
    TrafficResult, TransferPulse, decode_reuse, episode_token_windows,
    expert_size_from_config, model_traffic, apply_decode_stalls, StallTiming,
)

__all__ = [
    "fisher_interval_95", "apply_decode_stalls", "StallTiming", "recover_power_increment",
    "CorrelationRequirement", "DetectionPlan", "PowerFeatures", "RoutingObservation",
    "RoutingRecovery", "extract_features", "pearson", "plan_detectability",
    "recover_routing", "required_correlation", "PowerPulse", "SensorModel",
    "SimulatedEpisode", "SimulatedTrace", "ina3221_sensor", "nvml_sensor",
    "simulate_episode", "simulate_trace", "ExpertSize", "OffloadConfig",
    "TimingResult", "TokenTraffic", "TokenWindow", "TrafficResult", "TransferPulse",
    "decode_reuse", "episode_token_windows", "expert_size_from_config", "model_traffic",
]
