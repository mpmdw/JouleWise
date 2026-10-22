# align-stageb lane report

## SUMMARY
Continued the Stage B lane from ebba5483358d088d4cae81cbdfc944fae0503027.
Stage B now measures group-held-out power recovery beyond decode timing; raw energy, timing and mean power remain visible.
Removed the simulator compute-duration reference; all energy features integrate observed trace coverage.
Dithered rounding contributes q²/12 per reading; same-sign q*T is a labelled alternative only.
INA current acquisition defaults to each channel's shunt slices; the contiguous frame is a labelled sensitivity case.
Dropped samples retain finite features, coverage flags and the complete episode cohort.
Small prefill batches follow the pinned cache limit; noise has its own seed stream; hardware procedures cover supply/throttle hazards.
Validation and synthetic before/after numbers are recorded below; no hardware or external inference service was used.
PR #526 remains draft and unmerged; shared contracts and the registry file are unchanged this round.

## FILES
- joulewise/align/moe_stage_b/__init__.py: exports the added increment recovery API.
- joulewise/align/moe_stage_b/analysis.py: observed-coverage features, timing/mean power, grouped timing control, random rounding and labelled alternative bound.
- joulewise/align/moe_stage_b/experiment.py: real-world orchestration, compatible output keys, episode flags, candidate recoveries and provenance.
- joulewise/align/moe_stage_b/simulation.py: disjoint INA shunt acquisition and independently derived sensor-noise seed.
- joulewise/align/moe_stage_b/traffic.py: <=32 prefill cache updates, upstream slot guard and unavailable legacy reference alias.
- joulewise/align/moe_stage_b/reference.py: list/pairwise oracle maintenance for cache and rounding, plus timing-projection oracle.
- tests/align/test_moe_stage_b.py: existing 34 tests updated for the corrected feature, sensor, bounds and zero/control assertions.
- tests/align/test_moe_stage_b_review.py: CI fallback port of every reviewer pass condition, shunt averaging/cache regressions and noise-seed ablation.
- docs/align/moe_stage_b.md: revised criterion, uncertainty, interpretation, sensor alternatives and hardware hazard procedure.
- .codex-report/align-stageb.md: this report and complete evidence.
- No new registry edit. tests/test_shard_tests.py retains the inherited r0 line exactly as instructed by F7.

## PUBLIC API
- `OffloadConfig(expert_bytes: Mapping[int, int], resident: frozenset[tuple[int, int]], cache_capacity_bytes: int, cache_policy: str, bandwidth_bytes_s: float, joules_per_byte: float, path: str, bandwidth_source: str, energy_source: str, prefill_mode: str = "bypass", prefill_batch_tokens: int = 1, flags: tuple[str, ...] = (), decode_miss_stalls: bool = False, running_power_w: float = 0.0)`
- `TokenWindow(token_index: int, start_ns: int, end_ns: int)`; `PowerPulse(start_ns: int, end_ns: int, watts: float)`.
- `SensorModel(name: str, source: str, channel: str, interval_ns: int, averaging_window_ns: int, quantum_w: float, noise_std_w: float, phase_ns: int = 0, notes: str = "")`.
- `RoutingObservation(episode_id: str, group: str, routing_statistic: float, features: PowerFeatures)`.
- `expert_size_from_config(config: Mapping[str, Any], *, block_elements: int, block_bytes: int) -> ExpertSize`
- `episode_token_windows(episode: Episode, *, prefill_batch_tokens: int = 1) -> TimingResult`
- `model_traffic(router: RouterLog, config: OffloadConfig, *, windows: Sequence[TokenWindow] | None = None) -> TrafficResult`
- `decode_reuse(router: RouterLog) -> float | None`
- `nvml_sensor(*, noise_std_w: float, quantum_w: float, phase_ns: int = 0) -> SensorModel`
- `ina3221_sensor(*, bus_voltage_v: float, current_a: float, shunt_ohm: float, enabled_channels: int, shunt_conversion_ns: int, bus_conversion_ns: int, averages: int, poll_interval_ns: int, noise_std_w: float, phase_ns: int = 0) -> SensorModel`
- `simulate_trace(traffic: TrafficResult, sensor: SensorModel, *, start_ns: int, end_ns: int, clock_domain: str, baseline_w: float, loads: Sequence[PowerPulse] = (), seed: int = 0, episode_bias_w: float = 0.0) -> SimulatedTrace`
- `simulate_episode(episode: Episode, config: OffloadConfig, sensor: SensorModel, *, baseline_w: float, prefill_load_w: float, decode_load_w: float, tool_load_w: float, seed: int = 0, episode_bias_w: float = 0.0, windows: Sequence[TokenWindow] | None = None) -> SimulatedEpisode`
- `extract_features(episode: Episode, trace: PowerTrace, *, baseline_w: float, noise_std_w: float, noise_multiplier: float, attribution_floor_j: float, windows: Sequence[TokenWindow] | None = None, reference_decode_duration_ns: int | None = None) -> PowerFeatures`
- `pearson(x: Sequence[float], y: Sequence[float]) -> float | None`
- `recover_routing(observations: Sequence[RoutingObservation], *, feature_name: str) -> RoutingRecovery`
- `required_correlation(*, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int) -> CorrelationRequirement`
- `plan_detectability(sensor: SensorModel, *, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int, routing_stat_sd: float, traffic_energy_slope_j_per_token: float, decode_tokens: int, decode_duration_s: float, phase_bias_std_j: float, systematic_contrast_half_width_j: float, routing_energy_residual_std_j_per_token: float = 0.0) -> DetectionPlan`
- Experiment helpers: `synthetic_episode(config: WorldConfig, *, group: int, condition: str, hot_probability: float) -> Episode`; `world_offload(config: WorldConfig, *, all_resident: bool = False) -> OffloadConfig`; `default_sensors() -> tuple[SensorModel, ...]`; `run_world(config: WorldConfig, sensor: SensorModel, *, all_resident: bool, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int) -> dict[str, Any]`; `main() -> None`.
- `fisher_interval_95(correlation: float | None, episodes: int, *, fitted_means: int = 0) -> tuple[float, float] | None`
- `apply_decode_stalls(episode: Episode, config: OffloadConfig, *, windows: Sequence[TokenWindow]) -> StallTiming`
- `synthetic_token_schedule(config: WorldConfig, episode: Episode) -> tuple[Episode, tuple[TokenWindow, ...]]`
- `StallTiming(episode, windows, reference_decode_duration_ns: int | None, flags=())`; `SimulatedEpisode` additionally exposes actual `windows` and unavailable `reference_decode_duration_ns=None` compatibility alias.
- `TokenTraffic` additionally exposes `stall_energy_j`, integer `transfer_duration_ns`, and `incremental_energy_j`; `TrafficResult.total_incremental_energy_j` sums memory plus running-stall energy. Existing `energy_j` / `total_energy_j` remain transfer-only.
- `RoutingRecovery` additionally exposes `held_out_interval_95`, `held_out_episodes` and `held_out_effective_n`; centered counterparts and tri-state verdicts are serialized by `run_world`.
- Immutable output/config dataclasses are defined in the relevant modules. Reference helpers are test oracles; their strict input validation is not the production flags API.

- Added PowerFeatures.decode_seconds_per_token and PowerFeatures.mean_decode_power_w (optional floats).
- Added SensorModel.acquisition_slices_ns: tuple[tuple[int, int], ...] = (), offsets before each reading.
- Added DetectionPlan.worst_case_same_sign_quantization_bound_j and rounding_contrast_std_j.
- recover_power_increment(observations: Sequence[RoutingObservation]) -> RoutingRecovery.
- reference_detection_forecast(..., *, n_per_condition: int) -> ReferenceDetectionForecast; reference_power_increment(observations) -> tuple[float | None, int] (test oracles).
- run_world additionally returns power_increment_over_timing, timing and mean-power recovery, candidate verdicts, episode_outcomes, forecast provenance and a labelled quantization alternative. The nominal_decode_duration_s_range alias is None. true_extra retains physical transfer + running-stall truth; transfer_only is the target for the observed baseline-subtracted energy feature.

## TESTS RUN
The environment failed provisioning (snapshot_materialization_failed / gateway_unavailable). No shell, checkout, local discovery or .review1 command ran. The brief's CI fallback is in use.
Baseline CI 39722816945 at f0c25415485c3e866bfdb8cc669d5231de9f5c2f retains unchanged ebba54833 production code. The original 34 Stage B tests passed in 134.801s; records: four tests in 0.004s; reviewer port: one evidence-capture test in 246.748s. Zero lane skips/failures/errors. Sum of alignment module elapsed times: 381.553s, not local discovery wall time. Final-code validation is pending this checkpoint.

## END-TO-END
Baseline p1--p5 evidence is retained from CI; current before/after tables will be installed after the fixed code executes. No before measurement is substituted for final-head execution.

## DECISIONS I MADE
- Continue the existing lane head, never recreate from the spine. GitHub fast-forward ref updates replace unavailable local checkout/push; only this lane branch is updated, with expected-head checks and force=false.
- The environment never supplied a shell. Follow the explicit CI fallback: port every reviewer pass condition into the in-scope review test, retaining production-shaped worlds, real traffic/sampling/extraction and monkeypatch seams.
- F1: predeclare grouped timing-residual energy recovery as the primary increment criterion. Timing->energy and timing->routing fits use other task groups; conditions center evaluation only. Print raw energy, timing and mean-power candidates beside the increment.
- Remove the nominal compute reference instead of estimating a hardware reference from simulator truth. Preserve deprecated None aliases and an ignored extraction argument. Thus no reference uncertainty enters features.
- Energy subtracts the supplied running baseline over actual covered decode time. Physical true_extra retains transfer plus running-stall truth; transfer_only targets this observed energy feature. Gross mean power comes from observed energy / covered time plus that baseline.
- Keep the lead's d=1, n=50, alpha=.05, power=.8 and comparisons=3 planning parameters. Extra printed candidates are diagnostics, not a search for a passing detector. The required r remains 0.6471202066782847.
- The primary nominal Fisher interval accounts for two condition means plus one timing covariate (N-3 effective observations). It shares the existing episode/CV-dependence limitation.
- F2: use uniform dithered rounding variance q²/12 propagated through independent readings and the two condition means. The supplied systematic half-width remains a measured/scenario parameter, zero in these uncalibrated worlds. q*T is printed as an alternative and never decides Stage B.
- F3: retain the one dropped-sample episode, integrate existing cells without filling, flag incomplete coverage, and retain the same 24 episodes. No eligibility rule is added.
- F4: adopt shunt slices as requested by the datasheet sequence; use 1.1ms acquisition / 10ms polling. Four averages use separated slices. Keep 6.6ms as the labelled alternative.
- F5/F6: label phase_bias_std_j as fitted on the same evaluated episodes and INA 0.04W noise as a scenario parameter. Neither is independent hardware validation.
- F8: use actual prefill microbatch size, including the last partial batch. Pinned max_batch=32 is at :230, with the size/slot guard at :503. Defaults have only full 128-token batches, so this change alone moves no default numbers.
- F9: algebraic zero gets a float-noise bar; apparent resident energy gets separate quantum, noise and boundary-mixing bars.
- F10: preserve route and phase RNGs; derive only sensor noise from f"noise-{seed}". Print an old-noise-seed ablation with every other final input fixed.
- Keep the inherited registry normalization untouched; the lead lands its shared spine fix.
- STAGEB-S: per the sampler lanes, record alarms, OC counters and power/throttle reasons per episode; report all-inclusive primary and labelled unflagged sensitivity counts, and stop physical work on electrical limiting events.
- Existing oracle provenance remains historical. This seat maintained the oracle and added the timing-projection comparison; that new work is not claimed as an independent different-model derivation. No helpers were started.
- No optional dependencies, network tests, hardware operations, inference service, merge, ready-for-review transition or out-of-scope write.

## CONTRACT-CHANGE
No shared contract changes. The existing lane-local TokenWindow adapter remains necessary because RouterLog has no token timestamps or microbatch identity. A future optional companion timing record remains a proposal, not an installed eligibility rule.

## OPEN ISSUES
Fixed-code execution and numeric evidence are pending this checkpoint. Hardware J/B, sensor phase/cadence, noise, supply, logger overhead, cache groups and Stage A effect need calibration. Nominal Fisher intervals do not establish dependent-fold coverage or registered design power. The new timing-projection oracle was maintained by this seat, not independently authored by a different model. PR #526 remains draft.

## NEEDS_RULING
The provisional primary is grouped timing-residual energy recovery. Mean decode power is printed as an alternative for the lead's prospective scientific criterion choice; results will be filled from execution. No data are excluded and no ruling blocks implementation.

## FIX ROUND 1
Removed timing-reference leakage and nonphysical missing-sample refusal; corrected dithered rounding, INA shunt acquisition, prefill cache policy and noise seeding. Updated the old feature/sensor/bound assertions and added the no-shell reviewer port. Full FIX LOG will cite the executed code after validation.

## HISTORY
r0 CI 39708988879 passed 29 Stage B tests. r0c CI 39716151868 passed 34 in 115.018s. The lead's ebba54833 review ran 38 alignment tests in 64.0s. These are history; the former stalled-world positive verdict is superseded by this fix round.
