# align-stageb lane report

## SUMMARY
Implemented a stdlib-only, parameterized MoE traffic model with pinned residency, LRU/SLRU and explicit prefill batch unions.
Added analytic power acquisition simulation for configurable INA3221 rails and the requested 100 ms / 25 ms NVML sensitivity case.
Added decode energy, variance and spectral features, grouped held-out routing recovery and conditional detectability planning.
Added multi-turn, tool-using synthetic worlds with all-resident controls and randomized acquisition phases.
Verified current llama.cpp offload/cache flags and routing callback seams at a pinned public source revision.
Documented memory budgets and operator procedures for Jetson Orin Nano Super and the RTX 3080 Ti box.
An independently authored numerical oracle and 25 focused test methods are committed; execution is pending.
The managed environment has remained pending/starting without a usable shell; no test or hardware result is claimed.

## FILES
- `joulewise/align/moe_stage_b/__init__.py`: public stdlib API exports.
- `joulewise/align/moe_stage_b/traffic.py`: expert block storage, timing adapter, cache simulation, traffic profiles, adjacent decode reuse.
- `joulewise/align/moe_stage_b/simulation.py`: sensor configuration, analytic acquisition and shared Episode/PowerTrace simulation.
- `joulewise/align/moe_stage_b/analysis.py`: features, grouped scalar recovery, normal-design correlation requirement and sensor forecast.
- `joulewise/align/moe_stage_b/experiment.py`: production-shaped worlds and JSON CLI.
- `joulewise/align/moe_stage_b/reference.py`: separately authored numerical oracle, using ordered lists, direct overlap integrals and pairwise statistics.
- `tests/align/test_moe_stage_b.py`: 25 focused tests, including real end-to-end production paths and oracle comparisons.
- `docs/align/moe_stage_b.md`: physical limits, sources, formulas, model fit and verified llama.cpp configuration/logging procedure.
- `.codex-report/align-stageb.md`: this handoff.
- Registry exceptions: none used so far. The three shared governing files were not modified.

## PUBLIC API
- `expert_size_from_config(config: Mapping[str, Any], *, block_elements: int, block_bytes: int) -> ExpertSize`
- `episode_token_windows(episode: Episode, *, prefill_batch_tokens: int = 1) -> TimingResult`
- `model_traffic(router: RouterLog, config: OffloadConfig, *, windows: Sequence[TokenWindow] | None = None) -> TrafficResult`
- `decode_reuse(router: RouterLog) -> float | None`
- `nvml_sensor(*, noise_std_w: float, quantum_w: float, phase_ns: int = 0) -> SensorModel`
- `ina3221_sensor(*, bus_voltage_v: float, current_a: float, shunt_ohm: float, enabled_channels: int, shunt_conversion_ns: int, bus_conversion_ns: int, averages: int, poll_interval_ns: int, noise_std_w: float, phase_ns: int = 0) -> SensorModel`
- `simulate_trace(traffic: TrafficResult, sensor: SensorModel, *, start_ns: int, end_ns: int, clock_domain: str, baseline_w: float, loads: Sequence[PowerPulse] = (), seed: int = 0, episode_bias_w: float = 0.0) -> SimulatedTrace`
- `simulate_episode(episode: Episode, config: OffloadConfig, sensor: SensorModel, *, baseline_w: float, prefill_load_w: float, decode_load_w: float, tool_load_w: float, seed: int = 0, episode_bias_w: float = 0.0, windows: Sequence[TokenWindow] | None = None) -> SimulatedEpisode`
- `extract_features(episode: Episode, trace: PowerTrace, *, baseline_w: float, noise_std_w: float, noise_multiplier: float, attribution_floor_j: float, windows: Sequence[TokenWindow] | None = None) -> PowerFeatures`
- `pearson(x: Sequence[float], y: Sequence[float]) -> float | None`
- `recover_routing(observations: Sequence[RoutingObservation], *, feature_name: str) -> RoutingRecovery`
- `required_correlation(*, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int) -> CorrelationRequirement`
- `plan_detectability(sensor: SensorModel, *, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int, routing_stat_sd: float, traffic_energy_slope_j_per_token: float, decode_tokens: int, decode_duration_s: float, phase_bias_std_j: float, systematic_contrast_half_width_j: float) -> DetectionPlan`
- Experiment helpers: `synthetic_episode(config: WorldConfig, *, group: int, condition: str, hot_probability: float) -> Episode`; `world_offload(config: WorldConfig, *, all_resident: bool = False) -> OffloadConfig`; `default_sensors() -> tuple[SensorModel, ...]`; `run_world(config: WorldConfig, sensor: SensorModel, *, all_resident: bool, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int) -> dict[str, Any]`; `main() -> None`.
- Immutable output/config dataclasses are defined in the relevant modules. Reference helpers are test oracles; their strict input validation is not the production flags API.

## TESTS RUN
**Execution pending; zero Python tests run, zero skips reported.** There is no usable execution environment yet.
- Two attempts to run `pwd` through `exec_command` failed with “No usable execution environment is available.” No Python interpreter was reached.
- `wait_for_environment` is still pending; runtime status repeatedly alternated `pending` and `starting`, connectivity offline, no failure detail.
- Commands to run when the environment becomes usable:
  - `python3 -m unittest discover -s tests/align -t .`
  - `python3 -m unittest -v tests.align.test_moe_stage_b`
  - `python3 -m joulewise.align.moe_stage_b.experiment`
  - `python3 -m unittest discover -s tests`
  - `python3 scripts/quick_suite.py --tier touched --since 4d47c4362352ccd8d4d904134a79f0d8260b21b5`
  - `python3 scripts/fixture_orphan_census.py --fail-on-orphans`
- Extras: none imported, installed or required. There is no extra-dependent test path to skip.
- Independent numerical/source review: requested model `gpt-6-astra`, agent task `/root/independent_numeric_reference`. The runtime did not independently expose its model identity. Source and review outputs were consumed into the committed oracle and fixes; no execution was claimed.
- Review findings fixed: preserve top-k hit order; count disjoint decode intervals in clock bounds; normalize Pearson inputs; validate integer counts and subnormal normal-tail inputs; prevent NaN effect propagation; use within-condition routing SD and within-condition held-out attenuation; avoid double-counting the modeled white-noise variance.
- Independent review did not read production Stage B implementation before authoring its numerical oracle. Root remains responsible for actual execution and final verification.

## END-TO-END
The committed real-function chain is `synthetic_episode -> RouterLog -> model_traffic -> simulate_episode -> PowerTrace -> extract_features -> grouped recover_routing -> plan_detectability`.
The default CLI defines four cases (INA/NVML x offloaded/all-resident), each 12 task groups x 2 conditions = 24 episodes, four turns, 1024 prefill tokens, 512 decode tokens and four tool calls per episode. At 50 ms/token, decode lasts 25.6 s; 16 s prefill and 3.2 s tool gaps give 44.8 s per episode.
Architecture is OLMoE-shaped: 16 layers, 64 experts/layer, top-8, three 2048x1024 matrices/expert, Q4_0 blocks of 32 weights/18 bytes. An expert occupies 3,538,944 bytes. The dynamic cache holds 256 such experts; explicit prefill microbatches have 128 tokens.
The INA scenario derives a 6.6 ms conversion frame and 10 ms effective cadence with a 0.036032 W quantum from the supplied 5 V / 2 A / 10 mOhm rail. NVML is the requested 25 ms acquisition every 100 ms; its token-rate spectrum at 20 Hz is flagged beyond Nyquist.
The fixed statistical example supplies Stage A d=1, 50 independent task groups/condition, alpha=.05, power=.8 and three comparisons. Actual recovered correlations, energy ranges and detection outputs are **not yet available** because no Python execution has occurred.
The end-to-end test cohort uses six task groups per condition and three turns; it calls the same production functions. Its comparison bar is the parameterized normal-design requirement, not a guessed correlation cutoff.

## DECISIONS I MADE
- User-directed lane work overrides unrelated historical queue ranking; Mission M0/read-only intake found no active stop card in the fetched spine. No out-of-scope bookkeeping was written.
- The lane branch did not exist at intake. It was created from spine SHA `4d47c4362352ccd8d4d904134a79f0d8260b21b5`. While the VM was unavailable, authorized branch-only commits were checkpointed using connected GitHub tools.
- No sensor simulator exists on the spine; the lane therefore owns a local analytic simulator.
- Keep all core functionality stdlib-only, with no optional-dependency requirement or network in tests.
- Model incremental bytes/energy on a named sensor-visible memory path, not total inference energy. Cache-disabled CPU offload is not a PCIe expert-upload model; Jetson shares DRAM.
- The upstream source is pinned at llama.cpp `a37cc46104eb50900d5ab4a9ba02a0abdac039db`; `--n-cpu-moe`, `-ot`, `--moe-cache-mib`, `--fit off` and `--n-gpu-layers all` were checked in its parser.
- Model request-atomic hit-first LRU/SLRU, pinned residency and explicit prefill batch unions. Upstream multi-group caches and read-only large-batch cache reuse are documented limitations with flags.
- Preserve all flags and missing predictions rather than excluding episodes. No new data-eligibility rule is introduced.
- Use supplied token timing or a flagged uniform adapter. Missing turn/phase information is not fabricated as observed timing.
- Treat NVML duty-cycle gaps and acquisition spectra explicitly; do not multiply apparent energy by inverse duty fraction.
- Predeclare three scalar features and hold out complete task groups. Center held-out results within condition for the Stage A attenuation comparison; report raw correlation separately.
- Keep Stage A effect, sensor noise, memory energy, systematic bounds and design choices as parameters. Synthetic world parameters are scenarios, not hardware estimates.
- OLMoE Q4_0 is the small physical pilot candidate. Re-estimate Stage A on that model; a Qwen effect cannot be transplanted. A Qwen3-30B-A3B resident bank does not fit Jetson shared memory, while RTX CPU-offload feasibility also depends on unspecified host RAM.
- Use an independently authored numerical oracle and source review per PIPELINE/AGENTS; root will run final checks when execution becomes available. A source review is not an executing review.

## CONTRACT-CHANGE
No shared contract file was modified. A future optional companion routing-timing record would avoid reconstructing token/turn/microbatch timing: token ordinal, turn index, actual executed phase, start/end brackets, microbatch identity and clock domain. The current lane works around the absence with explicit `TokenWindow` inputs and flags. This proposal is not installed and changes no data eligibility.

## OPEN ISSUES
- BLOCKED: the selected managed environment has not become usable; local checkout, Python execution, focused/alignment/repo-wide tests and actual synthetic result numbers remain unverified.
- Source-only independent review is complete; executing validation is pending. The branch is not represented as tested or merge-ready.
- Hardware J/B, effective bandwidth, INA rail configuration, RTX sensor cadence, logger perturbation and Stage A effect sizes require later real calibration. No hardware was accessed.
- Exact batched-prefill replay needs backend cache-group/slot/batch state; read-only cached-weight reuse is currently flagged as unmodelled.
- No credentials, keys, personal email addresses or external service calls are present in tests.

## NEEDS_RULING
none
