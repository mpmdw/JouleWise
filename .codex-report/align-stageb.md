# align-stageb lane report

## SUMMARY

Continued the pushed lane at 0e5f1733553a3e4f7d8571e685ba39b4a0c9bafb; the shared contracts and inherited registry file are unchanged.
F1/F2 use training-only condition fixed effects and Episode.condition; opaque hash IDs preserve the increment bit for bit.
The former affirmative counterfactual no-upload-stall INA result changes from 0.893842 to 0.735609 [0.625652, 0.816906], inconclusive.
The base stalled E2E INA result is 0.048994 [-0.156278, 0.250209], a nominal scenario no; independent episode timing spread can change it to yes.
The stalled episode-factor grid changes from no at 0.368832 ms/token SD to inconclusive at 0.868869 and yes at 1.575544; this is a sensitivity result, not a physical threshold.
F8 uses continuous Gaussian Fourier rounding and covariance bounds; current-world recovery values and upstream slot-guard arithmetic remain intact.
F4/F5/F6 explicitly retain the permitted marginal-effect, simulator-baseline and uncalibrated-null limitations; F7 is deferred to the lead.
CI 39739338982 passed all 41 Stage B tests plus 4 shared-record tests, with zero lane failures, errors or skips; no extras, network tests or hardware were used.
The report/runbook are complete; final-head CI is blocked by the lead's spine registry conflict in tests/test_shard_tests.py, preserved under F7. PR #526 remains draft and unmerged.

## FILES

- joulewise/align/moe_stage_b/__init__.py: package exports.
- joulewise/align/moe_stage_b/traffic.py: expert byte sizing, residency/SLRU traffic, transfer pulses and blocking-stall timing; pinned small-batch/slot guard remains.
- joulewise/align/moe_stage_b/simulation.py: exact acquisition overlaps, disjoint INA shunt slices, independent sensor-noise seed, shared PowerTrace outputs.
- joulewise/align/moe_stage_b/analysis.py: trace features, scalar recovery, condition-fixed-effect increment, nominal uncertainty and continuous rounding/covariance bounds.
- joulewise/align/moe_stage_b/reference.py: separately formulated numerical oracles, including within-condition pair-difference increment.
- joulewise/align/moe_stage_b/experiment.py: production-shaped world orchestration, Episode.condition adapter, episode timing factor, sensitivity sweep and fallback provenance.
- tests/align/test_moe_stage_b.py: 34 existing lane tests, including end-to-end/CLI paths and the corrected continuous-rounding oracle test.
- tests/align/test_moe_stage_b_review.py: four round-1 reviewer tests, retained blind/coverage/cache regressions and explicit condition in its oracle capture.
- tests/align/test_moe_stage_b_round2.py: three tests porting every round-2 repro pass condition, the timing sweep and the continuous-rounding/covariance bound.
- docs/align/moe_stage_b.md: fixed decision/outcome tables, both timing-spread sweeps, F4/F5/F6 limitations and existing pinned hardware procedure.
- .codex-report/align-stageb.md: this report, full CI-printed before/final evidence and ordered FIX LOG.
- tests/test_shard_tests.py: inherited registry normalization, not edited in round 2 or this continuation; F7 belongs to the lead.

Only the eight files in the round-2 diff from 932719cfc are changed this round.
This continuation changes only the report and runbook. No .review2 directory,
probe file, local checkout, shared contract, main branch or other lane was written.
The public GitHub connector was used with force=false and expected-head checks.
Blob identity against 932719cfc was verified for PIPELINE.md (829c944b),
records.py (ca3523d5), interfaces.py (b0468f41), and the inherited registry
file (6f19d939). No protected source or registry change is present.

## PUBLIC API

- `OffloadConfig(expert_bytes: Mapping[int, int], resident: frozenset[tuple[int, int]], cache_capacity_bytes: int, cache_policy: str, bandwidth_bytes_s: float, joules_per_byte: float, path: str, bandwidth_source: str, energy_source: str, prefill_mode: str = "bypass", prefill_batch_tokens: int = 1, flags: tuple[str, ...] = (), decode_miss_stalls: bool = False, running_power_w: float = 0.0)`
- `TokenWindow(token_index: int, start_ns: int, end_ns: int)`; `PowerPulse(start_ns: int, end_ns: int, watts: float)`.
- `SensorModel(name: str, source: str, channel: str, interval_ns: int, averaging_window_ns: int, quantum_w: float, noise_std_w: float, phase_ns: int = 0, notes: str = "", acquisition_slices_ns: tuple[tuple[int, int], ...] = ())`.
- `RoutingObservation(episode_id: str, group: str, routing_statistic: float, features: PowerFeatures, condition: str | None = None)`.
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

- `rounding_uncertainty(quantum_w: float, noise_std_w: float) -> tuple[float, float]`: continuous bias-W and rounding-plus-covariance W² bounds.
- `WorldConfig` adds `decode_episode_factor_half_width: float = 0.0`; all prior fields/defaults remain.
- `timing_spread_sweep(config: WorldConfig, sensor: SensorModel, *, jitter_points_ns: tuple[int, ...] = (2_000_000, 10_000_000, 25_000_000), episode_factor_half_widths: tuple[float, ...] = (0.0, 0.025, 0.05, 0.10, 0.20), stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int) -> list[dict[str, Any]]`.
- New `run_world` keys: `timing_scenario`, `within_condition_sd_episode_mean_decode_ms`, `mean_decode_ms_per_token`, `requirement_effect_provenance`, `energy_baseline_provenance`, `increment_null_calibration`. Existing reviewer patch seams and output keys remain.

## TESTS RUN

The managed environment remained pending and supplied no usable shell. The
initial exec attempt returned "No usable execution environment is available".
The explicitly authorized no-shell CI fallback is used: the literal local
discovery and isolated .review2 commands are UNRUN. No local fetch, checkout,
git status or probe-file creation is claimed. All their pass-condition worlds
were already ported to the in-scope round-2 test by the prior seat, and their
executed CI evidence was read and checked in this continuation.

Requested local discovery (UNRUN; no executor):

```sh
JW_B5_SYNTHETIC_ONLY=1 python3 -m unittest discover -s tests/align -t .
```

**Executed production/test code: 0e5f1733553a3e4f7d8571e685ba39b4a0c9bafb,
[CI 39739338982](https://github.com/mpmdw/JouleWise/actions/runs/39739338982):
completed success.** Build, fences, quick, installed-wheel, all twelve ordinary
shards and all three exclusive jobs succeeded. This is CI execution, not a local
whole-repository run; no whole repository suite was launched by this seat.
The separate gate-ledger run 39739338897 failed for unfilled lead gates.

| Actual CI module / job | Tests | Failures | Errors | Skips | Module seconds |
|---|---:|---:|---:|---:|---:|
| tests.align.test_moe_stage_b / 119694267510 (shard 9) | 34 | 0 | 0 | 0 | 88.874 |
| tests.align.test_moe_stage_b_review / 119694267283 (shard 8) | 4 | 0 | 0 | 0 | 284.661 |
| tests.align.test_moe_stage_b_round2 / 119694267390 (shard 5) | 3 | 0 | 0 | 0 | 1085.650 |
| tests.align.test_records / 119694267305 (shard 4) | 4 | 0 | 0 | 0 | 0.005 |
| Stage B subtotal | 41 | 0 | 0 | 0 | 1459.185 |
| Alignment total including shared records | 45 | 0 | 0 | 0 | 1459.190 |

The module times are summed, not wall time. Relative to the reviewed 42-test
alignment total, the round-2 module adds three tests; no earlier test is removed.
Each reviewer module scopes JW_B5_SYNTHETIC_ONLY=1 with patch.dict and restores
it. No lane test imports an optional dependency or uses network/hardware.
Extras installed: none. Extra-dependent tests: none; no skip reasons or extra
run apply.

Baseline production code is exactly 932719cfc: checkpoint
e229ff9b9eb405c7dd705b7f2835c8132f7b4bae changes only the evidence test.
[Baseline CI 39732398546](https://github.com/mpmdw/JouleWise/actions/runs/39732398546)
completed success. Its round-2 evidence collector ran one test, zero
failures/errors/skips, 635.709s (job 119671578296, shard 5); it deliberately
printed the existing failures rather than asserting the new pass conditions.
The final test enables those assertions. The baseline reproduces the hash-ID
StatisticsError, condition-only yes and two random-covariate FAILs.

CI actually invokes unittest through the repository sharder. The exact heredoc
below is from the unchanged workflow; SHARD_COUNT=12 and SHARD_INDEX=4,5,8,9
select the listed module jobs. It is not the unrun discovery command.

```sh
python - <<'PY'
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, "scripts")
import shard_tests

overlay = json.loads(Path("scripts/test_timings.json").read_text())
exclusive = frozenset(overlay["exclusive_modules"])
discovered = shard_tests.discover_test_modules()
assert exclusive <= set(discovered), (exclusive, discovered)
timings = shard_tests.load_timing_map()
ordinary = tuple(module for module in discovered if module not in exclusive)

# UNIT-atomic, not module-atomic. Modules in split_modules (today
# test_reduce and test_controller_g2b_attachment, each audited for
# per-test independence) are spread across shards at test
# granularity, so no single module floors the shard time. This edits no test file and
# skips nothing: expand_units emits one unit per declared heavy
# test plus ONE remainder unit holding every other test in that
# module, and verify_split_declaration fails the build closed if
# a declared id no longer exists.
splits = {
    module: declaration
    for module, declaration in shard_tests.load_split_declarations().items()
    if module in set(ordinary)
}
unknown = shard_tests.conservative_unknown_weight()
units, weights = shard_tests.expand_units(
    ordinary, timings, splits, unknown_weight=unknown
)
count = int(os.environ["SHARD_COUNT"])
partitions = shard_tests.partition_modules(
    units, weights, count, unknown_weight=unknown
)
totals = shard_tests.partition_totals(
    partitions, weights, unknown_weight=unknown
)
print("ORDINARY SHARD ESTIMATES", ",".join(f"{value:.3f}" for value in totals))
index = int(os.environ["SHARD_INDEX"])
raise SystemExit(shard_tests.run_units(partitions[index - 1], count, index))
PY
```

The existing CLI test actually invokes:

```text
/opt/hostedtoolcache/Python/3.13.16/x64/bin/python -m joulewise.align.moe_stage_b.experiment
```

**Final-head CI is BLOCKED, not green.** The lead moved the spine from
4d47c4362352ccd8d4d904134a79f0d8260b21b5 to
6bca315c2e04d5a254ab1a4aedd366deb4e59ddf while this continuation was
finishing. That commit changes only tests/test_shard_tests.py, including the
same normalization line this lane inherited. GitHub reports mergeable=false,
mergeable_state=dirty; the final report head has zero workflow runs/checks.
Compare confirms exactly one behind-spine commit, and the only overlapping
path is tests/test_shard_tests.py. Thus GitHub cannot build a PR merge tree
or start final-head CI. The earlier runbook-only candidate ca1fc4489 did
schedule CI 39746060999 against the old spine; it is not final-head evidence.

F7 says: "leave tests/test_shard_tests.py exactly as it is on the branch";
the lead "lands the registry line on the spine and drops it from this lane
before merge". Its blob remains 6f19d939162b5ea9b5a727173f5bae541a66103a.
This seat did not change it or merge the spine. The concrete remaining action
is for the lead to resolve that one file against its new spine version, or
explicitly authorize that exact scope expansion. A single close/reopen of
PR #526 attempted a CI refresh before the new spine conflict was diagnosed;
the PR stayed draft, unmerged, and is open. No ready transition occurred.

This operational block is separate from the successful 45-test code-head CI
above. No final-head success is claimed. The report and PR are otherwise
complete; independent review/merge/cold gates remain lead-owned.

## END-TO-END

The real chain is synthetic_episode -> synthetic_token_schedule ->
apply_decode_stalls -> model_traffic -> simulate_episode -> shared
Episode/PowerTrace -> extract_features(actual windows) ->
group-held-out scalar/fixed-effect increment -> nominal Fisher interval and
the fixed scenario requirement. experiment's four patched globals remain the
entry points. The review tests capture the actual RoutingObservations.

Default worlds: 12 matched task groups per condition, four turns, 1024 prefill
and 512 decode tokens, four tool calls per episode, N=24. E2E worlds: 48
matched groups per condition, three turns, 768 prefill and 384 decode tokens,
three tool calls, N=96. The default per-token compute step is 50 ms plus
uniform ±2 ms. Upload stalls, sensor phase, quantization, white noise and tool
gaps run through the production functions. INA is 1.1 ms shunt acquisition
per 10 ms poll, q=0.036032 W, scenario noise SD=0.04 W; NVML is 25 ms per
100 ms, q=0.001 W, scenario noise SD=1 W. These are synthetic scenarios,
not device calibrations. Every no-stall case, including raw e2e_nostall,
nostall, p2/p3, variable-timing and no-stalls tags below, is a
**counterfactual** because the pinned llama.cpp blocks dependent uploads.

The supplied planning design d_A=1, n=50, alpha=.05, power=.8 and comparisons=3
still gives required r=0.6471202066782847. F4 means this is a marginal-effect
scenario comparison, not proven conditional design power. F5 means the energy
column and fitted forecast use simulator running-level truth. F6 means no
nominal Fisher no is a measured absence of signal.

### Fixed outcome table

| World / sensor | Energy r [95% CI], simulator running level (F5) | Timing r [95% CI] | Mean power r [95% CI] | Increment r [95% CI] | Stage B scenario comparison |
|---|---|---|---|---|---|
| Default stalled INA | 0.774001 [0.523083, 0.901446] | 0.843815 [0.655352, 0.933370] | 0.847834 [0.663334, 0.935165] | 0.156939 [-0.294722, 0.551283] | no |
| Default stalled NVML | 0.634586 [0.290765, 0.833261] | 0.843815 [0.655352, 0.933370] | 0.673615 [0.351958, 0.852979] | -0.532326 [-0.783882, -0.130658] | no |
| E2E stalled INA | 0.784768 [0.692217, 0.851924] | 0.821391 [0.742314, 0.877902] | 0.844028 [0.773729, 0.893794] | 0.048994 [-0.156278, 0.250209] | no |
| E2E stalled NVML | 0.274987 [0.076636, 0.452400] | 0.821391 [0.742314, 0.877902] | 0.279720 [0.081732, 0.456469] | 0.133760 [-0.071911, 0.328520] | no |
| E2E counterfactual no-stall INA | 0.724566 [0.611759, 0.808490] | -0.010303 [-0.212480, 0.192720] | 0.723570 [0.610448, 0.807764] | 0.735609 [0.625652, 0.816906] | inconclusive |
| E2E counterfactual no-stall NVML | 0.120411 [-0.084265, 0.315338] | -0.010303 [-0.212480, 0.192720] | 0.120470 [-0.084206, 0.315392] | 0.097389 [-0.108475, 0.295243] | no |
| E2E counterfactual no-stall INA, contiguous 6.6 ms alternative | 0.810716 [0.727619, 0.870364] | -0.010303 [-0.212480, 0.192720] | 0.808374 [0.724406, 0.868706] | 0.821912 [0.742523, 0.878529] | yes |


### Which printed values moved

| Case | Before r | Fixed r | Fixed minus before | Fixed verdict |
|---|---:|---:|---:|---|
| Default stalled INA | 0.173430480 | 0.156938561 | -0.016491919 | no |
| Default stalled NVML | -0.588600491 | -0.532326097 | 0.056274394 | no |
| E2E counterfactual no-stall INA | 0.893842314 | 0.735608748 | -0.158233566 | inconclusive at this cohort size |
| E2E counterfactual no-stall NVML | 0.201304006 | 0.097389003 | -0.103915003 | no |
| E2E stalled INA | 0.038780948 | 0.048993963 | 0.010213015 | no |
| Stalled INA ±10 ms token jitter | 0.603187623 | 0.543588417 | -0.059599206 | inconclusive at this cohort size |
| Stalled INA ±25 ms token jitter | 0.917115563 | 0.757955289 | -0.159160274 | yes |
| Counterfactual condition-only sensor +0.3 W | 0.753929524 | -0.268944258 | -1.022873782 | no |


Stalled E2E NVML moves from 0.13023441275020084 to 0.13375996013901492
(+0.0035255473888140814), remaining no. Timing, energy-only and mean-power
point estimates are unchanged for the same unmodified worlds: F1 changes the
increment fit, F2 changes label provenance, and the zero episode-factor
default preserves simulation values. The 6.6 ms contiguous counterfactual
alternative moves from increment 0.9270878135830587 to 0.8219116242960651
(-0.10517618928699357), still yes; it is not the default INA acquisition.

F8 does not change any trace or recovery point estimate. In the counterfactual
E2E INA forecast, the contrast bound changes from 0.0009114822446086623 J to
0.0009114822573562025 J (+1.2747540111164579e-11 J). This is far below 1% of
the smaller printed bound (9.114822446086624e-6 J), the rule-3 agreement
scale; no scenario verdict changes from this bound. Strong dithering has
sigma/q=1.1101 for INA and 1000 for NVML; covariance/Fourier corrections are
tiny there. At sigma=0 the bound is q²/4, so the zero-noise forecast oracle
now includes quantization rather than assuming zero white contribution.

### Timing-spread sweep (F3)

One independent uniform episode factor multiplies every compute-only decode
duration before blocking transfers are added. Running watts remain constant;
compute background energy scales with duration, transfer bytes/J are fixed,
and acquisition alignment changes. The default factor half-width is zero and
uses no extra route/timing RNG draws. Context length/DVFS are motivating
episode-level causes, not additional simulated physical models.

The scenario grid is token jitter ±2/10/25 ms, then episode-factor half-widths
0/2.5/5/10/20% with ±2 ms token jitter. Grid points are scenario inputs, not
bars. The sweep axis is the mean of the two condition population SDs of
episode-mean decode time per token.

#### Blocking-upload INA

| Scenario input (grid point) | Within-condition SD of episode-mean decode time (ms/token) | Increment r [nominal 95% CI] | Scenario verdict |
|---|---:|---|---|
| Token jitter ±2 ms | 0.368832 | 0.048994 [-0.156278, 0.250209] | no |
| Token jitter ±10 ms | 0.447588 | 0.543588 [0.382200, 0.672798] | inconclusive |
| Token jitter ±25 ms | 0.816151 | 0.757955 [0.655447, 0.833042] | yes |
| Episode factor ±0% (token jitter ±2 ms) | 0.368832 | 0.048994 [-0.156278, 0.250209] | no |
| Episode factor ±2.5% (token jitter ±2 ms) | 0.868869 | 0.686035 [0.560681, 0.780649] | inconclusive |
| Episode factor ±5% (token jitter ±2 ms) | 1.575544 | 0.761929 [0.660779, 0.835898] | yes |
| Episode factor ±10% (token jitter ±2 ms) | 3.043434 | 0.796699 [0.707873, 0.860719] | yes |
| Episode factor ±20% (token jitter ±2 ms) | 6.010339 | 0.772448 [0.674944, 0.843439] | yes |

#### Counterfactual no-upload-stall INA

| Scenario input (grid point) | Within-condition SD of episode-mean decode time (ms/token) | Increment r [nominal 95% CI] | Scenario verdict |
|---|---:|---|---|
| Token jitter ±2 ms | 0.071625 | 0.735609 [0.625652, 0.816906] | inconclusive |
| Token jitter ±10 ms | 0.292804 | 0.755908 [0.652705, 0.831569] | yes |
| Token jitter ±25 ms | 0.779390 | 0.788357 [0.696502, 0.854791] | yes |
| Episode factor ±0% (token jitter ±2 ms) | 0.071625 | 0.735609 [0.625652, 0.816906] | inconclusive |
| Episode factor ±2.5% (token jitter ±2 ms) | 0.757150 | 0.764849 [0.664703, 0.837994] | yes |
| Episode factor ±5% (token jitter ±2 ms) | 1.499974 | 0.781413 [0.687071, 0.849844] | yes |
| Episode factor ±10% (token jitter ±2 ms) | 2.988072 | 0.774920 [0.678282, 0.845207] | yes |
| Episode factor ±20% (token jitter ±2 ms) | 5.965506 | 0.787803 [0.695748, 0.854397] | yes |


The stalled episode-factor verdict changes no -> inconclusive -> yes between
the printed 0, 2.5% and 5% points, i.e. SD 0.368832 -> 0.868869 -> 1.575544
ms/token. No exact transition is inferred between grid points. The final
stalled point reaches 6.010339/54.403347=11.05% of mean decode time; the
counterfactual final point reaches 5.965506/48.915798=12.20%. Both exceed the
lead's 5% reach criterion. Per-token jitter alone gives stalled SD
0.368832/0.447588/0.816151 ms/token, showing why averaged token jitter
cannot represent general between-episode timing causes.

### Pass-condition audit

- F1: all five q6 fixed shipped values equal the reviewer's within-condition sketch bit for bit in these CI runs; each pair is printed below. The separate pair-difference oracle differs by at most binary64 rounding (largest observed difference 1.1102230246251565e-16), below 1% of each printed 95% half-width. No design difference needs accounting.
- All five q7 variants give no or inconclusive. The counterfactual +0.3 W condition-only sensor changes from 0.7539295242538844 / yes to -0.26894425758502544 / no; q8 prints the same sketch value. The stalled +0.3 W case is 0.7245091211015002 [0.610971134479966, 0.8088429772481662], inconclusive. This is nominal uncalibrated output, not a validated null distribution.
- l1 counterfactual INA, counterfactual NVML and stalled INA all print PASS. Their largest random-covariate deviations from constant timing are 0.008362403145948716, 0.04677865335404372 and 0.014352092360890967, below respective printed constant-result half-widths 0.09681743656959485, 0.20169205205071722 and 0.07752558485831718. These bars are supplied by the lead: a change below the 95% half-width is not a measured difference.
- q5 completes for both sensors and flags constant within-condition timing. Counterfactual INA real/constant increment is 0.7356087476296433/0.7316358556654516; NVML is 0.09738900253260493/0.10168638294763703.
- q2 const_off is inconclusive with constant-increment flags; noise_only is no at -0.20539816781350065. The four round-1 sensors stuck at their true running level remain inconclusive and keep their full N=96/24 cohorts.
- q2 b_plus1 preserves the increment and mean-power verdict/point estimates within the mandated 1%-of-half-width bar: increment 0.04899396302686891 -> 0.048993963026867746 and mean-power 0.844028133904538 -> 0.8440281339045353. F5's energy-only offset sensitivity is disclosed: const_off energy-only remains 0.8213906829904345 / yes because the allowed fallback is used.
- F2: all four q1 hash worlds complete with the same verdict and bit-identical increment r/interval as suffix worlds. All four q1b captured-observation replacements also preserve bit identity. Missing/unknown conditions have unavailable predictions, a missing_or_unknown_condition flag and 95 of 96 observations in within-condition statistics. The synthetic ID constructor may retain suffixes; production condition readers do not parse them.
- q4 counterfactual INA seeds 1..6 span r=0.722259776923693 to 0.7833267733949544: three yes and three inconclusive, rather than the old uniformly affirmative 0.907..0.921 range. NVML seeds 1..3 are 0.05417111919095635, -0.22654561383560248 and 0.048887136883611744, all no.
- F8: test_continuous_rounding_bound checks both sides of sigma=q/2, the zero-noise/zero-quantum limits and an analytic Gaussian-bin variance example with nonzero rounding covariance. The test's q/2 agreement bar is 1% of the printed uncertainty; its analytic variance comparison uses rule 3's 1e-6 relative bar. No sigma=q/2 branch remains.
- Prior-round prefill slot guard and documentation byte/time/energy/device-fit arithmetic are unchanged. All 34 original tests and four prior reviewer tests pass.

### Exact CI-printed before and final evidence

These are the authorized no-shell ports, not fabricated isolated-script logs.
Baseline source: e229ff9b9 on unchanged 932719cfc production, job 119671578296,
test_all_reviewer_worlds. Final source: 0e5f17335, job 119694267390.
The final test_all_reviewer_worlds prints q1, q1b, q2, q3, q4, q5, q6, q7,
q8 and l1 plus reference/unknown-condition/check arrays.
test_between_episode_timing_sweep prints both sweep arrays.
test_continuous_rounding_bound passes without an evidence line.
Sensor index 0=INA, 1=NVML; e2e=stalled, e2e_nostall/nostall=counterfactual.
Repeated identical worlds are consolidated by the CI port's cache. Every
world parameter and patched experiment global in the lead probes is retained.
q5 emits its three recovery comparisons; its extra in-sample descriptive
correlations are not printed by the port. q6 emits the shipped/sketch/SD
comparison; random-covariate draws for the shared worlds are printed by l1.
No attribute/key adaptation was required, and no .review2 script was edited.

Before (all 41 STAGEB_R2 evidence lines):

```text
STAGEB_R2 q1_ids default 0 {"hash_ids": {"error": "StatisticsError", "message": "fmean requires at least one data point"}, "suffix_ids": {"ci": [-0.2791638835042857, 0.5629748878035307], "decode_s": [25.856373476, 30.914227554], "episodes": 24, "flags": [], "r": 0.1734304799794651, "recovery": {"decode_seconds_per_token": [0.8438154771382044, [0.6553517606446033, 0.9333699301483963], "yes"], "energy_per_decode_token_j": [0.7740006547148806, [0.5230834994984437, 0.9014464496892164], "inconclusive at this cohort size"], "mean_decode_power_w": [0.8478338120759732, [0.6633335569803914, 0.9351652157432788], "yes"], "token_energy_variance_j2": [0.8075488647977788, [0.585168978991736, 0.9169616657713987], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.0478756886311657, [-0.38143894286501157, 0.46020170271264166], "no"]}, "required": 0.6471202066782847, "verdict": "no"}}
STAGEB_R2 q1_ids default 1 {"hash_ids": {"error": "StatisticsError", "message": "fmean requires at least one data point"}, "suffix_ids": {"ci": [-0.8135700110924684, -0.21035765763800887], "decode_s": [25.856373476, 30.914227554], "episodes": 24, "flags": [], "r": -0.5886004907339206, "recovery": {"decode_seconds_per_token": [0.8438154771382044, [0.6553517606446033, 0.9333699301483963], "yes"], "energy_per_decode_token_j": [0.6345858161086284, [0.29076507775888405, 0.8332611577713871], "inconclusive at this cohort size"], "mean_decode_power_w": [0.6736148880248951, [0.35195791312058256, 0.8529787790146469], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.2858705700385963, [-0.15434780908481388, 0.6313864502855886], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}}
STAGEB_R2 q1_ids e2e_nostall 0 {"hash_ids": {"error": "StatisticsError", "message": "fmean requires at least one data point"}, "suffix_ids": {"ci": [0.8437692437918409, 0.9284890626614218], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": [], "r": 0.8938423135247563, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.7245660029010135, [0.611758967778493, 0.8084904919807115], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7235703428110349, [0.6104476360084228, 0.8077643915236326], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.6325631403793299, [0.4931497081242412, 0.7402993283247059], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.16429493178438637, [-0.03964543115308715, 0.3550945831277374], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}}
STAGEB_R2 q1_ids e2e_nostall 1 {"hash_ids": {"error": "StatisticsError", "message": "fmean requires at least one data point"}, "suffix_ids": {"ci": [-0.002510872103624055, 0.38906128288021297], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": [], "r": 0.20130400551357638, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.1204111321940513, [-0.08426533948028601, 0.3153381677919225], "no"], "mean_decode_power_w": [0.12046980734966435, [-0.08420622312773121, 0.31539178517467187], "no"], "token_energy_variance_j2": [0.07548130253882322, [-0.12911395980406556, 0.2739126494513399], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}}
STAGEB_R2 q1b_increment_ids e2e_nostall 0 {"flags": [], "hash_ids": [0.9966216618198721, [0.9948975321730986, 0.9977638591474751]], "suffix_ids": [0.8938423135247563, [0.8437692437918409, 0.9284890626614218]]}
STAGEB_R2 q1b_increment_ids e2e 0 {"flags": [], "hash_ids": [0.038659643150421454, [-0.16636244431743252, 0.24047768969798505]], "suffix_ids": [0.03878094817615853, [-0.16624431709872659, 0.24059214797596737]]}
STAGEB_R2 q1b_increment_ids default 1 {"flags": [], "hash_ids": [-0.5859372347082612, [-0.812190951972158, -0.20646891039257317]], "suffix_ids": [-0.5886004907339206, [-0.8135700110924684, -0.21035765763800887]]}
STAGEB_R2 q1b_increment_ids e2e_nostall 1 {"flags": [], "hash_ids": [0.7840143022656317, [0.690600267155911, 0.8516987991115142]], "suffix_ids": [0.20130400551357638, [-0.002510872103624055, 0.38906128288021297]]}
STAGEB_R2 q2_blind real {"ci": [-0.16624431709872659, 0.24059214797596737], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": [], "r": 0.03878094817615853, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.7847682385203254, [0.6922172578618175, 0.8519241883004665], "yes"], "mean_decode_power_w": [0.844028133904538, [0.7737286721887902, 0.8937942788319294], "yes"], "token_energy_variance_j2": [0.8381683660231627, [0.7655635678094398, 0.8896923523279705], "yes"], "token_rate_amplitude_w": [0.07137319129642268, [-0.13317330306237754, 0.2700878527620881], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q2_blind const_off {"ci": null, "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": ["constant_power_increment_feature", "undefined_power_increment_correlation"], "r": null, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.8213906829904345, [0.7423138889988471, 0.8779015354109607], "yes"], "mean_decode_power_w": [null, null, "inconclusive at this cohort size"], "token_energy_variance_j2": [0.4414712166485143, [0.2623150128656091, 0.5912075984022859], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q2_blind noise_only {"ci": [-0.3883582249975427, 0.0033390591349903463], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": [], "r": -0.20050924019146646, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [-0.08439446277323642, [-0.2821895901071562, 0.12028296760037162], "no"], "mean_decode_power_w": [-0.09448574784196434, [-0.2915251544181646, 0.11024545971170721], "no"], "token_energy_variance_j2": [0.10143301539051935, [-0.1033108573842711, 0.2979304103482086], "no"], "token_rate_amplitude_w": [0.061147925419471554, [-0.1432474711313166, 0.26054045880124954], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q2_blind b_plus1 {"ci": [-0.1662443170987273, 0.24059214797596667], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": [], "r": 0.038780948176157785, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.760866939930668, [0.6599961882575257, 0.8347901739898798], "yes"], "mean_decode_power_w": [0.8440281339045353, [0.7737286721887865, 0.8937942788319275], "yes"], "token_energy_variance_j2": [0.8273292843611642, [0.750521593907891, 0.8820828436939568], "yes"], "token_rate_amplitude_w": [0.07137319129642268, [-0.13317330306237754, 0.2700878527620881], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q3_jitter 2000000 {"ci": [-0.16624431709872659, 0.24059214797596737], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": [], "r": 0.03878094817615853, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.7847682385203254, [0.6922172578618175, 0.8519241883004665], "yes"], "mean_decode_power_w": [0.844028133904538, [0.7737286721887902, 0.8937942788319294], "yes"], "token_energy_variance_j2": [0.8381683660231627, [0.7655635678094398, 0.8896923523279705], "yes"], "token_rate_amplitude_w": [0.07137319129642268, [-0.13317330306237754, 0.2700878527620881], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q3_jitter 10000000 {"ci": [0.45543838785555724, 0.7186004264964722], "decode_s": [19.343161443, 23.329624284], "episodes": 96, "flags": [], "r": 0.6031876227914476, "recovery": {"decode_seconds_per_token": [0.6225176900943571, [0.4805056345873075, 0.7327170804703199], "inconclusive at this cohort size"], "energy_per_decode_token_j": [0.7264095395603055, [0.6141886312454425, 0.8098342452953273], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7820990654664629, [0.688600580828382, 0.8500178561535348], "yes"], "token_energy_variance_j2": [0.6669244285863579, [0.5368497566270211, 0.7660294487870302], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.10058636269437991, [-0.10415703297145576, 0.29715075739843305], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q3_jitter 25000000 {"ci": [0.8773089747932467, 0.9443896458835185], "decode_s": [19.025162695, 23.675648954], "episodes": 96, "flags": [], "r": 0.9171155628350061, "recovery": {"decode_seconds_per_token": [0.2859490702192582, [0.08845340175038621, 0.4618126164680928], "no"], "energy_per_decode_token_j": [0.7662433679640117, [0.6672118847040501, 0.8386568718179834], "yes"], "mean_decode_power_w": [0.7971912255617452, [0.7091115522216582, 0.860773367424369], "yes"], "token_energy_variance_j2": [0.8051881665486867, [0.7200405372012578, 0.8664495092420316], "yes"], "token_rate_amplitude_w": [0.1442228433755383, [-0.060155640816427325, 0.33699556961298033], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 1 nostall 0 {"ci": [0.8748034191200041, 0.943212550944873], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.9153862845386987, "recovery": {"decode_seconds_per_token": [-0.1734213042388982, [-0.36327680504652665, 0.030262672483032518], "no"], "energy_per_decode_token_j": [0.7774302906770401, [0.6822856471615543, 0.8466791188403034], "yes"], "mean_decode_power_w": [0.776883978880419, [0.6815476385009901, 0.8462880833088657], "yes"], "token_energy_variance_j2": [0.6369981023518875, [0.4987507409182385, 0.7436381131427936], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.205034538075162, [0.0025185857901886427, 0.39139492685545024], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 2 nostall 0 {"ci": [0.8633049220107933, 0.9377885042940577], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.9074310261715518, "recovery": {"decode_seconds_per_token": [-0.056861874647458115, [-0.2565269139370425, 0.14745762659407177], "no"], "energy_per_decode_token_j": [0.7087154761500463, [0.5909564393779485, 0.7969008278244267], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7094594134758346, [0.5919293064006004, 0.7974462392194557], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.6223490728820592, [0.48029390098456276, 0.7325895752695265], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17738062394290716, [-0.02618092888868043, 0.3668174359891461], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 3 nostall 0 {"ci": [0.8728085576148743, 0.9422741470840753], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.9140084042025864, "recovery": {"decode_seconds_per_token": [-0.11977129945425358, [-0.3147534075654113, 0.08490988981658565], "no"], "energy_per_decode_token_j": [0.7690089886764835, [0.6709308740129158, 0.8406430521953545], "yes"], "mean_decode_power_w": [0.768035140159154, [0.6696207560314941, 0.8399438850442931], "yes"], "token_energy_variance_j2": [0.6579603699438198, [0.5253817429396007, 0.7593475391516569], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.1933671394540508, [-0.009630781079792051, 0.381057817065991], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 4 nostall 0 {"ci": [0.8726575017799989, 0.9422030443587197], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.9139040289778375, "recovery": {"decode_seconds_per_token": [-0.07203581912200638, [-0.2707052071743779, 0.13251900526454705], "no"], "energy_per_decode_token_j": [0.7331632776876585, [0.6231078370228275, 0.8147495766865345], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7341578785931354, [0.6244237617876964, 0.8154724521637098], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.6285609813194366, [0.4881051755919032, 0.7372818028680461], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17896739933980382, [-0.024543182257106094, 0.36823487483348327], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 5 nostall 0 {"ci": [0.88320110115919, 0.9471509729132014], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.9211762802330011, "recovery": {"decode_seconds_per_token": [-0.07903806123652074, [-0.2772190555986949, 0.125593876782121], "no"], "energy_per_decode_token_j": [0.7669820969472144, [0.6682047863231438, 0.8391875919339726], "yes"], "mean_decode_power_w": [0.7658670242592706, [0.6667061886393493, 0.8383864448493503], "yes"], "token_energy_variance_j2": [0.6971338479802602, [0.5758548766192376, 0.7883912736599059], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17737442810851145, [-0.02618732160792211, 0.36681189963368804], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 6 nostall 0 {"ci": [0.8685714194836089, 0.9402773258097541], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.9110785933432388, "recovery": {"decode_seconds_per_token": [-0.1326868504663593, [-0.32652868328607904, 0.07186585425846996], "no"], "energy_per_decode_token_j": [0.7150178906016696, [0.5992091328607609, 0.8015168445531617], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7151801313522064, [0.599421904367454, 0.8016355370342293], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.591162198426132, [0.4414150248463187, 0.7088728389547391], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17320505397851166, [-0.030485413818306873, 0.3630832646783135], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 1 nostall 1 {"ci": [-0.0018639874559796548, 0.3896101138915353], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.2019245983495024, "recovery": {"decode_seconds_per_token": [-0.1734213042388982, [-0.36327680504652665, 0.030262672483032518], "no"], "energy_per_decode_token_j": [0.07281622897394084, [-0.13174817741300668, 0.27143208676661595], "no"], "mean_decode_power_w": [0.07279156049065869, [-0.1317725467995254, 0.27140911382338734], "no"], "token_energy_variance_j2": [0.11782763832017552, [-0.08686683188082994, 0.3129761355638427], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q4_seeds 2 nostall 1 {"ci": [-0.07973666853308871, 0.3214810364644569], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.12602226174224798, "recovery": {"decode_seconds_per_token": [-0.056861874647458115, [-0.2565269139370425, 0.14745762659407177], "no"], "energy_per_decode_token_j": [-0.00414258556378954, [-0.20658976463271522, 0.19864473644866554], "no"], "mean_decode_power_w": [-0.0041483492457129985, [-0.20659528241280326, 0.19863920009860186], "no"], "token_energy_variance_j2": [0.16256098975569117, [-0.04142402825134878, 0.3535367108265941], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q4_seeds 3 nostall 1 {"ci": [-0.006070555120189861, 0.386036188721665], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": [], "r": 0.19788607129369648, "recovery": {"decode_seconds_per_token": [-0.11977129945425358, [-0.3147534075654113, 0.08490988981658565], "no"], "energy_per_decode_token_j": [0.06322440122788221, [-0.14120510088016233, 0.26248243781689423], "no"], "mean_decode_power_w": [0.06320599562883387, [-0.14122321181933367, 0.26246523146648193], "no"], "token_energy_variance_j2": [0.13557089408869877, [-0.06894353204627356, 0.3291499107628256], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 l1_random_covariate e2e_nostall 0 {"bar_half_width": 0.0963503716416596, "const": [0.733196937462531, [0.6224555827995162, 0.8151563260828354], []], "random_covariate": [0.7631290641895777, 0.7336908867925656, 0.7838751843513776, 0.8613686056719941, 0.7302761191359117, 0.8727129980715291, 0.7492413689506917, 0.7619985731742132, 0.9475886565330001, 0.7780211657515587], "real": [0.8938423135247563, [0.8437692437918409, 0.9284890626614218]], "result": "FAIL", "worst_abs_change": 0.21439171907046906}
STAGEB_R2 q5_procedure 0 {"a_increment": 0.8938423135247563, "b_increment_no_timing": 0.733196937462531, "c_energy_only_within": 0.7245660029010135}
STAGEB_R2 l1_random_covariate e2e_nostall 1 {"bar_half_width": 0.20062831298994882, "const": [0.12562673254529513, [-0.08013599238807052, 0.32112063359182713], []], "random_covariate": [0.12532544167568951, 0.10951654646997767, 0.09647240493257737, 0.18974462056736574, 0.11903957348424346, 0.1928325544815843, 0.17625188889053722, 0.13019199403634898, 0.29898651898698403, 0.1448654408096689], "real": [0.20130400551357638, [-0.002510872103624055, 0.38906128288021297]], "result": "PASS", "worst_abs_change": 0.1733597864416889}
STAGEB_R2 q5_procedure 1 {"a_increment": 0.20130400551357638, "b_increment_no_timing": 0.12562673254529513, "c_energy_only_within": 0.1204111321940513}
STAGEB_R2 l1_random_covariate e2e 0 {"bar_half_width": 0.07803421009142092, "const": [0.7917726830598384, [0.7011520600031974, 0.8572204801860392], []], "random_covariate": [0.8168948977173967, 0.7949776685281287, 0.8398346712831682, 0.8948259772662789, 0.7892186058174446, 0.9038547917335561, 0.8035114112913352, 0.8108497012718527, 0.96025572351735, 0.8258592221676905], "real": [0.03878094817615853, [-0.16624431709872659, 0.24059214797596737]], "result": "FAIL", "worst_abs_change": 0.1684830404575116}
STAGEB_R2 q6_leak e2e_nostall 0 2000000 {"shipped": [0.8938423135247563, [0.8437692437918409, 0.9284890626614218], "yes"], "within_condition_nuisance_fit": [0.7356087476296433, [0.6256522408405558, 0.8169055178178175]], "within_sd_timing_ms": 0.07162480821319159}
STAGEB_R2 q6_leak e2e_nostall 1 2000000 {"shipped": [0.20130400551357638, [-0.002510872103624055, 0.38906128288021297], "no"], "within_condition_nuisance_fit": [0.09738900253260493, [-0.10847497677598433, 0.2952434901072392]], "within_sd_timing_ms": 0.07162480821319159}
STAGEB_R2 q6_leak e2e 0 2000000 {"shipped": [0.03878094817615853, [-0.16624431709872659, 0.24059214797596737], "no"], "within_condition_nuisance_fit": [0.04899396302686891, [-0.15627770234212882, 0.2502086290193932]], "within_sd_timing_ms": 0.3688315632613681}
STAGEB_R2 q6_leak e2e 0 10000000 {"shipped": [0.6031876227914476, [0.45543838785555724, 0.7186004264964722], "inconclusive at this cohort size"], "within_condition_nuisance_fit": [0.5435884172451112, [0.3821995378666403, 0.6727977743083902]], "within_sd_timing_ms": 0.44758826828606724}
STAGEB_R2 q6_leak e2e 0 25000000 {"shipped": [0.9171155628350061, [0.8773089747932467, 0.9443896458835185], "yes"], "within_condition_nuisance_fit": [0.7579552887635139, [0.655447422233347, 0.8330417830958603]], "within_sd_timing_ms": 0.8161511237517547}
STAGEB_R2 q7_condition_sensor e2e_nostall 0.0 {"ci": [-0.20248551718228558, 0.20493766726548754], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": [], "r": 0.0012791581581449239, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.005258572032977311, [-0.19757252545565196, 0.20765789855472713], "no"], "mean_decode_power_w": [0.005320448181600522, [-0.19751306224587817, 0.20771710738803323], "no"], "token_energy_variance_j2": [-0.03232339278983169, [-0.23341525146250872, 0.17141988696677804], "no"], "token_rate_amplitude_w": [-0.06522211814070869, [-0.26434923707022345, 0.13923855214862202], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q7_condition_sensor e2e_nostall 0.1 {"ci": [0.6443634494043755, 0.8270740953324667], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": [], "r": 0.7496702614943103, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [-0.12054370338844832, [-0.3154593096364715, 0.08413176939143467], "no"], "mean_decode_power_w": [-0.11932708838864414, [-0.31434734414326115, 0.08535727540101107], "no"], "token_energy_variance_j2": [-0.1394069182865722, [-0.3326317502207593, 0.06505114766548425], "no"], "token_rate_amplitude_w": [-0.07336935498451479, [-0.2719471353184851, 0.13120169292619924], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q7_condition_sensor e2e_nostall 0.3 {"ci": [0.650056105517618, 0.8301442143957536], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": [], "r": 0.7539295242538844, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [-0.3152958261098426, [-0.48681596630306806, -0.1203647973478505], "no"], "mean_decode_power_w": [-0.3292735132938631, [-0.49862691147762717, -0.1357069706116846], "no"], "token_energy_variance_j2": [-0.056094961663672505, [-0.25580803405948355, 0.1482101792991354], "no"], "token_rate_amplitude_w": [-0.08155440856839881, [-0.279555450974594, 0.12310036085941158], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q8_fixcheck {"shipped": 0.7539295242538844, "within_condition_fit": [-0.26894425758502544, [-0.44810573375996904, -0.0690133929008036]]}
STAGEB_R2 q7_condition_sensor e2e_nostall 1.0 {"ci": [0.6493085157493267, 0.829741652054187], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": [], "r": 0.7533706729430419, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [-0.6853923950889547, [-0.7797284914392767, -0.5606289335140712], "no"], "mean_decode_power_w": [-0.823235888079771, [-0.8792016488894461, -0.7448615971039794], "no"], "token_energy_variance_j2": [-0.03249199524255191, [-0.2335748293186135, 0.1712560620674549], "no"], "token_rate_amplitude_w": [-0.07110964516799272, [-0.2698422677472176, 0.1334334865496318], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q7_condition_sensor e2e 0.3 {"ci": [0.002564217247430469, 0.3933596477605623], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": [], "r": 0.20616843448885078, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [-0.06998215027366496, [-0.2687913215430803, 0.13454627725011767], "no"], "mean_decode_power_w": [-0.4179198947602215, [-0.5720958739302694, -0.23521731787918765], "no"], "token_energy_variance_j2": [0.05635192984113401, [-0.14795804914994826, 0.25604893247636484], "no"], "token_rate_amplitude_w": [0.0653197600201441, [-0.1391423923124313, 0.26444044188955873], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 checks [["opaque IDs complete and preserve verdict", false], ["opaque IDs complete and preserve verdict", false], ["opaque IDs complete and preserve verdict", false], ["opaque IDs complete and preserve verdict", false], ["ID-only replacement is bit-identical", false], ["ID-only replacement is bit-identical", false], ["ID-only replacement is bit-identical", false], ["ID-only replacement is bit-identical", false], ["blind sensor gives no yes", true], ["blind sensor gives no yes", true], ["noise-only verdict", true], ["baseline shift preserves verdict", true], ["baseline shift preserves increment", true], ["baseline shift preserves mean_decode_power_w", true], ["independent random covariate stays below printed uncertainty", false], ["constant timing is flagged", false], ["independent random covariate stays below printed uncertainty", true], ["constant timing is flagged", false], ["independent random covariate stays below printed uncertainty", false], ["constant timing is flagged", false], ["within-condition sketch agrees", false], ["within-condition sketch agrees", false], ["within-condition sketch agrees", false], ["within-condition sketch agrees", false], ["within-condition sketch agrees", false], ["condition-offset sensor gives no yes", true], ["condition-offset sensor gives no yes", true], ["condition-offset sensor gives no yes", false], ["condition-offset sensor gives no yes", false], ["condition-offset sensor gives no yes", true]]
```

Final (all printed STAGEB_R2 lines, including both sweep arrays):

```text
STAGEB_R2 q1_ids default 0 {"hash_ids": {"ci": [-0.294722386403027, 0.5512831521892628], "decode_s": [25.856373476, 30.914227554], "episodes": 24, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.15693856071329085, "recovery": {"decode_seconds_per_token": [0.8438154771382044, [0.6553517606446033, 0.9333699301483963], "yes"], "energy_per_decode_token_j": [0.7740006547148806, [0.5230834994984437, 0.9014464496892164], "inconclusive at this cohort size"], "mean_decode_power_w": [0.8478338120759732, [0.6633335569803914, 0.9351652157432788], "yes"], "token_energy_variance_j2": [0.8075488647977788, [0.585168978991736, 0.9169616657713987], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.0478756886311657, [-0.38143894286501157, 0.46020170271264166], "no"]}, "required": 0.6471202066782847, "verdict": "no"}, "suffix_ids": {"ci": [-0.294722386403027, 0.5512831521892628], "decode_s": [25.856373476, 30.914227554], "episodes": 24, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.15693856071329085, "recovery": {"decode_seconds_per_token": [0.8438154771382044, [0.6553517606446033, 0.9333699301483963], "yes"], "energy_per_decode_token_j": [0.7740006547148806, [0.5230834994984437, 0.9014464496892164], "inconclusive at this cohort size"], "mean_decode_power_w": [0.8478338120759732, [0.6633335569803914, 0.9351652157432788], "yes"], "token_energy_variance_j2": [0.8075488647977788, [0.585168978991736, 0.9169616657713987], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.0478756886311657, [-0.38143894286501157, 0.46020170271264166], "no"]}, "required": 0.6471202066782847, "verdict": "no"}}
STAGEB_R2 q1_ids default 1 {"hash_ids": {"ci": [-0.7838822249695361, -0.13065781262560253], "decode_s": [25.856373476, 30.914227554], "episodes": 24, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.5323260965864958, "recovery": {"decode_seconds_per_token": [0.8438154771382044, [0.6553517606446033, 0.9333699301483963], "yes"], "energy_per_decode_token_j": [0.6345858161086284, [0.29076507775888405, 0.8332611577713871], "inconclusive at this cohort size"], "mean_decode_power_w": [0.6736148880248951, [0.35195791312058256, 0.8529787790146469], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.2858705700385963, [-0.15434780908481388, 0.6313864502855886], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}, "suffix_ids": {"ci": [-0.7838822249695361, -0.13065781262560253], "decode_s": [25.856373476, 30.914227554], "episodes": 24, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.5323260965864958, "recovery": {"decode_seconds_per_token": [0.8438154771382044, [0.6553517606446033, 0.9333699301483963], "yes"], "energy_per_decode_token_j": [0.6345858161086284, [0.29076507775888405, 0.8332611577713871], "inconclusive at this cohort size"], "mean_decode_power_w": [0.6736148880248951, [0.35195791312058256, 0.8529787790146469], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.2858705700385963, [-0.15434780908481388, 0.6313864502855886], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}}
STAGEB_R2 q1_ids e2e_nostall 0 {"hash_ids": {"ci": [0.6256522408405558, 0.8169055178178175], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7356087476296433, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.7245660029010135, [0.611758967778493, 0.8084904919807115], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7235703428110349, [0.6104476360084228, 0.8077643915236326], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.6325631403793299, [0.4931497081242412, 0.7402993283247059], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.16429493178438637, [-0.03964543115308715, 0.3550945831277374], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}, "suffix_ids": {"ci": [0.6256522408405558, 0.8169055178178175], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7356087476296433, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.7245660029010135, [0.611758967778493, 0.8084904919807115], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7235703428110349, [0.6104476360084228, 0.8077643915236326], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.6325631403793299, [0.4931497081242412, 0.7402993283247059], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.16429493178438637, [-0.03964543115308715, 0.3550945831277374], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}}
STAGEB_R2 q1_ids e2e_nostall 1 {"hash_ids": {"ci": [-0.10847497677598433, 0.2952434901072392], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.09738900253260493, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.1204111321940513, [-0.08426533948028601, 0.3153381677919225], "no"], "mean_decode_power_w": [0.12046980734966435, [-0.08420622312773121, 0.31539178517467187], "no"], "token_energy_variance_j2": [0.07548130253882322, [-0.12911395980406556, 0.2739126494513399], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}, "suffix_ids": {"ci": [-0.10847497677598433, 0.2952434901072392], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.09738900253260493, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.1204111321940513, [-0.08426533948028601, 0.3153381677919225], "no"], "mean_decode_power_w": [0.12046980734966435, [-0.08420622312773121, 0.31539178517467187], "no"], "token_energy_variance_j2": [0.07548130253882322, [-0.12911395980406556, 0.2739126494513399], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}}
STAGEB_R2 q1b_increment_ids e2e_nostall 0 {"flags": ["nominal_fisher_interval_not_null_calibrated"], "hash_ids": [0.7356087476296433, [0.6256522408405558, 0.8169055178178175]], "suffix_ids": [0.7356087476296433, [0.6256522408405558, 0.8169055178178175]]}
STAGEB_R2 q1b_increment_ids e2e 0 {"flags": ["nominal_fisher_interval_not_null_calibrated"], "hash_ids": [0.04899396302686891, [-0.15627770234212882, 0.2502086290193932]], "suffix_ids": [0.04899396302686891, [-0.15627770234212882, 0.2502086290193932]]}
STAGEB_R2 q1b_increment_ids default 1 {"flags": ["nominal_fisher_interval_not_null_calibrated"], "hash_ids": [-0.5323260965864958, [-0.7838822249695361, -0.13065781262560253]], "suffix_ids": [-0.5323260965864958, [-0.7838822249695361, -0.13065781262560253]]}
STAGEB_R2 q1b_increment_ids e2e_nostall 1 {"flags": ["nominal_fisher_interval_not_null_calibrated"], "hash_ids": [0.09738900253260493, [-0.10847497677598433, 0.2952434901072392]], "suffix_ids": [0.09738900253260493, [-0.10847497677598433, 0.2952434901072392]]}
STAGEB_R2 q2_blind real {"ci": [-0.15627770234212882, 0.2502086290193932], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.04899396302686891, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.7847682385203254, [0.6922172578618175, 0.8519241883004665], "yes"], "mean_decode_power_w": [0.844028133904538, [0.7737286721887902, 0.8937942788319294], "yes"], "token_energy_variance_j2": [0.8381683660231627, [0.7655635678094398, 0.8896923523279705], "yes"], "token_rate_amplitude_w": [0.07137319129642268, [-0.13317330306237754, 0.2700878527620881], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q2_blind const_off {"ci": null, "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": ["constant_power_increment_feature", "undefined_power_increment_correlation", "nominal_fisher_interval_not_null_calibrated"], "r": null, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.8213906829904345, [0.7423138889988471, 0.8779015354109607], "yes"], "mean_decode_power_w": [null, null, "inconclusive at this cohort size"], "token_energy_variance_j2": [0.4414712166485143, [0.2623150128656091, 0.5912075984022859], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q2_blind noise_only {"ci": [-0.39267956038217, -0.001759893663998019], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.20539816781350065, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [-0.08439446277323642, [-0.2821895901071562, 0.12028296760037162], "no"], "mean_decode_power_w": [-0.09448574784196434, [-0.2915251544181646, 0.11024545971170721], "no"], "token_energy_variance_j2": [0.10143301539051935, [-0.1033108573842711, 0.2979304103482086], "no"], "token_rate_amplitude_w": [0.061147925419471554, [-0.1432474711313166, 0.26054045880124954], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q2_blind b_plus1 {"ci": [-0.15627770234212998, 0.2502086290193921], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.048993963026867746, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.760866939930668, [0.6599961882575257, 0.8347901739898798], "yes"], "mean_decode_power_w": [0.8440281339045353, [0.7737286721887865, 0.8937942788319275], "yes"], "token_energy_variance_j2": [0.8273292843611642, [0.750521593907891, 0.8820828436939568], "yes"], "token_rate_amplitude_w": [0.07137319129642268, [-0.13317330306237754, 0.2700878527620881], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q3_jitter 2000000 {"ci": [-0.15627770234212882, 0.2502086290193932], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.04899396302686891, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [0.7847682385203254, [0.6922172578618175, 0.8519241883004665], "yes"], "mean_decode_power_w": [0.844028133904538, [0.7737286721887902, 0.8937942788319294], "yes"], "token_energy_variance_j2": [0.8381683660231627, [0.7655635678094398, 0.8896923523279705], "yes"], "token_rate_amplitude_w": [0.07137319129642268, [-0.13317330306237754, 0.2700878527620881], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q3_jitter 10000000 {"ci": [0.3821995378666403, 0.6727977743083902], "decode_s": [19.343161443, 23.329624284], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.5435884172451112, "recovery": {"decode_seconds_per_token": [0.6225176900943571, [0.4805056345873075, 0.7327170804703199], "inconclusive at this cohort size"], "energy_per_decode_token_j": [0.7264095395603055, [0.6141886312454425, 0.8098342452953273], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7820990654664629, [0.688600580828382, 0.8500178561535348], "yes"], "token_energy_variance_j2": [0.6669244285863579, [0.5368497566270211, 0.7660294487870302], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.10058636269437991, [-0.10415703297145576, 0.29715075739843305], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q3_jitter 25000000 {"ci": [0.655447422233347, 0.8330417830958603], "decode_s": [19.025162695, 23.675648954], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7579552887635139, "recovery": {"decode_seconds_per_token": [0.2859490702192582, [0.08845340175038621, 0.4618126164680928], "no"], "energy_per_decode_token_j": [0.7662433679640117, [0.6672118847040501, 0.8386568718179834], "yes"], "mean_decode_power_w": [0.7971912255617452, [0.7091115522216582, 0.860773367424369], "yes"], "token_energy_variance_j2": [0.8051881665486867, [0.7200405372012578, 0.8664495092420316], "yes"], "token_rate_amplitude_w": [0.1442228433755383, [-0.060155640816427325, 0.33699556961298033], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 1 nostall 0 {"ci": [0.6896671071861853, 0.8512087551075963], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7833267733949544, "recovery": {"decode_seconds_per_token": [-0.1734213042388982, [-0.36327680504652665, 0.030262672483032518], "no"], "energy_per_decode_token_j": [0.7774302906770401, [0.6822856471615543, 0.8466791188403034], "yes"], "mean_decode_power_w": [0.776883978880419, [0.6815476385009901, 0.8462880833088657], "yes"], "token_energy_variance_j2": [0.6369981023518875, [0.4987507409182385, 0.7436381131427936], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.205034538075162, [0.0025185857901886427, 0.39139492685545024], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 2 nostall 0 {"ci": [0.6080054879778116, 0.8072052266701767], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.722259776923693, "recovery": {"decode_seconds_per_token": [-0.056861874647458115, [-0.2565269139370425, 0.14745762659407177], "no"], "energy_per_decode_token_j": [0.7087154761500463, [0.5909564393779485, 0.7969008278244267], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7094594134758346, [0.5919293064006004, 0.7974462392194557], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.6223490728820592, [0.48029390098456276, 0.7325895752695265], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17738062394290716, [-0.02618092888868043, 0.3668174359891461], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q4_seeds 3 nostall 0 {"ci": [0.6849675002567868, 0.8487364925675429], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.779860734196797, "recovery": {"decode_seconds_per_token": [-0.11977129945425358, [-0.3147534075654113, 0.08490988981658565], "no"], "energy_per_decode_token_j": [0.7690089886764835, [0.6709308740129158, 0.8406430521953545], "yes"], "mean_decode_power_w": [0.768035140159154, [0.6696207560314941, 0.8399438850442931], "yes"], "token_energy_variance_j2": [0.6579603699438198, [0.5253817429396007, 0.7593475391516569], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.1933671394540508, [-0.009630781079792051, 0.381057817065991], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 4 nostall 0 {"ci": [0.6411533714902434, 0.8253380407471964], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7472646186855327, "recovery": {"decode_seconds_per_token": [-0.07203581912200638, [-0.2707052071743779, 0.13251900526454705], "no"], "energy_per_decode_token_j": [0.7331632776876585, [0.6231078370228275, 0.8147495766865345], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7341578785931354, [0.6244237617876964, 0.8154724521637098], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.6285609813194366, [0.4881051755919032, 0.7372818028680461], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17896739933980382, [-0.024543182257106094, 0.36823487483348327], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q4_seeds 5 nostall 0 {"ci": [0.6823778214804334, 0.8473711069710954], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7779483125592, "recovery": {"decode_seconds_per_token": [-0.07903806123652074, [-0.2772190555986949, 0.125593876782121], "no"], "energy_per_decode_token_j": [0.7669820969472144, [0.6682047863231438, 0.8391875919339726], "yes"], "mean_decode_power_w": [0.7658670242592706, [0.6667061886393493, 0.8383864448493503], "yes"], "token_energy_variance_j2": [0.6971338479802602, [0.5758548766192376, 0.7883912736599059], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17737442810851145, [-0.02618732160792211, 0.36681189963368804], "no"]}, "required": 0.6471202066782847, "verdict": "yes"}
STAGEB_R2 q4_seeds 6 nostall 0 {"ci": [0.6150890088219804, 0.811111955623506], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7276283867137295, "recovery": {"decode_seconds_per_token": [-0.1326868504663593, [-0.32652868328607904, 0.07186585425846996], "no"], "energy_per_decode_token_j": [0.7150178906016696, [0.5992091328607609, 0.8015168445531617], "inconclusive at this cohort size"], "mean_decode_power_w": [0.7151801313522064, [0.599421904367454, 0.8016355370342293], "inconclusive at this cohort size"], "token_energy_variance_j2": [0.591162198426132, [0.4414150248463187, 0.7088728389547391], "inconclusive at this cohort size"], "token_rate_amplitude_w": [0.17320505397851166, [-0.030485413818306873, 0.3630832646783135], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 q4_seeds 1 nostall 1 {"ci": [-0.15120943433420556, 0.2550682753918178], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.05417111919095635, "recovery": {"decode_seconds_per_token": [-0.1734213042388982, [-0.36327680504652665, 0.030262672483032518], "no"], "energy_per_decode_token_j": [0.07281622897394084, [-0.13174817741300668, 0.27143208676661595], "no"], "mean_decode_power_w": [0.07279156049065869, [-0.1317725467995254, 0.27140911382338734], "no"], "token_energy_variance_j2": [0.11782763832017552, [-0.08686683188082994, 0.3129761355638427], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q4_seeds 2 nostall 1 {"ci": [-0.41127707218258597, -0.02393846315558513], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.22654561383560248, "recovery": {"decode_seconds_per_token": [-0.056861874647458115, [-0.2565269139370425, 0.14745762659407177], "no"], "energy_per_decode_token_j": [-0.00414258556378954, [-0.20658976463271522, 0.19864473644866554], "no"], "mean_decode_power_w": [-0.0041483492457129985, [-0.20659528241280326, 0.19863920009860186], "no"], "token_energy_variance_j2": [0.16256098975569117, [-0.04142402825134878, 0.3535367108265941], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q4_seeds 3 nostall 1 {"ci": [-0.1563821679697834, 0.2501082475440196], "decode_s": [19.129320208, 19.254973083], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.048887136883611744, "recovery": {"decode_seconds_per_token": [-0.11977129945425358, [-0.3147534075654113, 0.08490988981658565], "no"], "energy_per_decode_token_j": [0.06322440122788221, [-0.14120510088016233, 0.26248243781689423], "no"], "mean_decode_power_w": [0.06320599562883387, [-0.14122321181933367, 0.26246523146648193], "no"], "token_energy_variance_j2": [0.13557089408869877, [-0.06894353204627356, 0.3291499107628256], "no"], "token_rate_amplitude_w": [null, null, "inconclusive at this cohort size"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 l1_random_covariate e2e_nostall 0 {"bar_half_width": 0.09681743656959485, "const": [0.7316358556654516, [0.6203884638189294, 0.8140233369581191], ["constant_within_condition_training_timing", "nominal_fisher_interval_not_null_calibrated"]], "random_covariate": [0.7283444879972638, 0.7293210138485989, 0.7399982588114004, 0.7319168084417005, 0.7298210346335631, 0.7271541946040583, 0.7286368619975135, 0.733157836494763, 0.7294448552394854, 0.7359791265387123], "real": [0.7356087476296433, [0.6256522408405558, 0.8169055178178175]], "result": "PASS", "worst_abs_change": 0.008362403145948716}
STAGEB_R2 q5_procedure 0 {"a_increment": 0.7356087476296433, "b_increment_no_timing": 0.7316358556654516, "c_energy_only_within": 0.7245660029010135}
STAGEB_R2 l1_random_covariate e2e_nostall 1 {"bar_half_width": 0.20169205205071722, "const": [0.10168638294763703, [-0.10418366499328183, 0.29920043910815264], ["constant_within_condition_training_timing", "nominal_fisher_interval_not_null_calibrated"]], "random_covariate": [0.09561171021961921, 0.10051261805126235, 0.05490772959359331, 0.1017286670891391, 0.10497642702380444, 0.09944068897912295, 0.10083954441266163, 0.09479306370646332, 0.09612464631394875, 0.09608677851587658], "real": [0.09738900253260493, [-0.10847497677598433, 0.2952434901072392]], "result": "PASS", "worst_abs_change": 0.04677865335404372}
STAGEB_R2 q5_procedure 1 {"a_increment": 0.09738900253260493, "b_increment_no_timing": 0.10168638294763703, "c_energy_only_within": 0.1204111321940513}
STAGEB_R2 l1_random_covariate e2e 0 {"bar_half_width": 0.07752558485831718, "const": [0.7933314786596826, [0.7032769009140677, 0.858328070630702], ["constant_within_condition_training_timing", "nominal_fisher_interval_not_null_calibrated"]], "random_covariate": [0.7901126002810928, 0.795126441289289, 0.8076835710205735, 0.7958452332789305, 0.793334802924029, 0.7942573681228108, 0.7911826305838826, 0.7912961304333402, 0.7932982473252719, 0.794805226852127], "real": [0.04899396302686891, [-0.15627770234212882, 0.2502086290193932]], "result": "PASS", "worst_abs_change": 0.014352092360890967}
STAGEB_R2 q6_leak e2e_nostall 0 2000000 {"shipped": [0.7356087476296433, [0.6256522408405558, 0.8169055178178175], "inconclusive at this cohort size"], "within_condition_nuisance_fit": [0.7356087476296433, [0.6256522408405558, 0.8169055178178175]], "within_sd_timing_ms": 0.07162480821319159}
STAGEB_R2 reference e2e_nostall 0 2000000 {"count": 96, "r": 0.7356087476296433}
STAGEB_R2 q6_leak e2e_nostall 1 2000000 {"shipped": [0.09738900253260493, [-0.10847497677598433, 0.2952434901072392], "no"], "within_condition_nuisance_fit": [0.09738900253260493, [-0.10847497677598433, 0.2952434901072392]], "within_sd_timing_ms": 0.07162480821319159}
STAGEB_R2 reference e2e_nostall 1 2000000 {"count": 96, "r": 0.09738900253260492}
STAGEB_R2 q6_leak e2e 0 2000000 {"shipped": [0.04899396302686891, [-0.15627770234212882, 0.2502086290193932], "no"], "within_condition_nuisance_fit": [0.04899396302686891, [-0.15627770234212882, 0.2502086290193932]], "within_sd_timing_ms": 0.3688315632613681}
STAGEB_R2 reference e2e 0 2000000 {"count": 96, "r": 0.04899396302686888}
STAGEB_R2 q6_leak e2e 0 10000000 {"shipped": [0.5435884172451112, [0.3821995378666403, 0.6727977743083902], "inconclusive at this cohort size"], "within_condition_nuisance_fit": [0.5435884172451112, [0.3821995378666403, 0.6727977743083902]], "within_sd_timing_ms": 0.44758826828606724}
STAGEB_R2 reference e2e 0 10000000 {"count": 96, "r": 0.5435884172451113}
STAGEB_R2 q6_leak e2e 0 25000000 {"shipped": [0.7579552887635139, [0.655447422233347, 0.8330417830958603], "yes"], "within_condition_nuisance_fit": [0.7579552887635139, [0.655447422233347, 0.8330417830958603]], "within_sd_timing_ms": 0.8161511237517547}
STAGEB_R2 reference e2e 0 25000000 {"count": 96, "r": 0.757955288763514}
STAGEB_R2 q7_condition_sensor e2e_nostall 0.0 {"ci": [-0.40433453752383347, -0.015614262883346408], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.21863075142373237, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [0.005258572032977311, [-0.19757252545565196, 0.20765789855472713], "no"], "mean_decode_power_w": [0.005320448181600522, [-0.19751306224587817, 0.20771710738803323], "no"], "token_energy_variance_j2": [-0.03232339278983169, [-0.23341525146250872, 0.17141988696677804], "no"], "token_rate_amplitude_w": [-0.06522211814070869, [-0.26434923707022345, 0.13923855214862202], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q7_condition_sensor e2e_nostall 0.1 {"ci": [-0.653134405604882, -0.35183918816532955], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.51839569320646, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [-0.12054370338844832, [-0.3154593096364715, 0.08413176939143467], "no"], "mean_decode_power_w": [-0.11932708838864414, [-0.31434734414326115, 0.08535727540101107], "no"], "token_energy_variance_j2": [-0.1394069182865722, [-0.3326317502207593, 0.06505114766548425], "no"], "token_rate_amplitude_w": [-0.07336935498451479, [-0.2719471353184851, 0.13120169292619924], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q7_condition_sensor e2e_nostall 0.3 {"ci": [-0.44810573375996904, -0.0690133929008036], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.26894425758502544, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [-0.3152958261098426, [-0.48681596630306806, -0.1203647973478505], "no"], "mean_decode_power_w": [-0.3292735132938631, [-0.49862691147762717, -0.1357069706116846], "no"], "token_energy_variance_j2": [-0.056094961663672505, [-0.25580803405948355, 0.1482101792991354], "no"], "token_rate_amplitude_w": [-0.08155440856839881, [-0.279555450974594, 0.12310036085941158], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q8_fixcheck {"shipped": -0.26894425758502544, "within_condition_fit": [-0.26894425758502544, [-0.44810573375996904, -0.0690133929008036]]}
STAGEB_R2 q7_condition_sensor e2e_nostall 1.0 {"ci": [-0.5186089792273828, -0.15984809827284843], "decode_s": [19.121838945, 19.261471238], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": -0.3520947617513574, "recovery": {"decode_seconds_per_token": [-0.010303124188217116, [-0.21248013030776805, 0.19271978742984244], "no"], "energy_per_decode_token_j": [-0.6853923950889547, [-0.7797284914392767, -0.5606289335140712], "no"], "mean_decode_power_w": [-0.823235888079771, [-0.8792016488894461, -0.7448615971039794], "no"], "token_energy_variance_j2": [-0.03249199524255191, [-0.2335748293186135, 0.1712560620674549], "no"], "token_rate_amplitude_w": [-0.07110964516799272, [-0.2698422677472176, 0.1334334865496318], "no"]}, "required": 0.6471202066782847, "verdict": "no"}
STAGEB_R2 q7_condition_sensor e2e 0.3 {"ci": [0.610971134479966, 0.8088429772481662], "decode_s": [19.382917268, 23.189452019], "episodes": 96, "flags": ["nominal_fisher_interval_not_null_calibrated"], "r": 0.7245091211015002, "recovery": {"decode_seconds_per_token": [0.8213906829904342, [0.7423138889988465, 0.8779015354109604], "yes"], "energy_per_decode_token_j": [-0.06998215027366496, [-0.2687913215430803, 0.13454627725011767], "no"], "mean_decode_power_w": [-0.4179198947602215, [-0.5720958739302694, -0.23521731787918765], "no"], "token_energy_variance_j2": [0.05635192984113401, [-0.14795804914994826, 0.25604893247636484], "no"], "token_rate_amplitude_w": [0.0653197600201441, [-0.1391423923124313, 0.26444044188955873], "no"]}, "required": 0.6471202066782847, "verdict": "inconclusive at this cohort size"}
STAGEB_R2 unknown_condition None {"episodes": 95, "flags": ["missing_or_unknown_condition", "insufficient_grouped_training_data", "nominal_fisher_interval_not_null_calibrated"]}
STAGEB_R2 unknown_condition unknown {"episodes": 95, "flags": ["missing_or_unknown_condition", "insufficient_grouped_training_data", "nominal_fisher_interval_not_null_calibrated"]}
STAGEB_R2 checks [["opaque IDs complete and preserve verdict", true], ["opaque IDs preserve increment", true], ["opaque IDs complete and preserve verdict", true], ["opaque IDs preserve increment", true], ["opaque IDs complete and preserve verdict", true], ["opaque IDs preserve increment", true], ["opaque IDs complete and preserve verdict", true], ["opaque IDs preserve increment", true], ["ID-only replacement is bit-identical", true], ["ID-only replacement is bit-identical", true], ["ID-only replacement is bit-identical", true], ["ID-only replacement is bit-identical", true], ["blind sensor gives no yes", true], ["blind sensor gives no yes", true], ["noise-only verdict", true], ["baseline shift preserves verdict", true], ["baseline shift preserves increment", true], ["baseline shift preserves mean_decode_power_w", true], ["independent random covariate stays below printed uncertainty", true], ["constant timing is flagged", true], ["independent random covariate stays below printed uncertainty", true], ["constant timing is flagged", true], ["independent random covariate stays below printed uncertainty", true], ["constant timing is flagged", true], ["independent pairwise reference agrees", true], ["within-condition sketch agrees", true], ["independent pairwise reference agrees", true], ["within-condition sketch agrees", true], ["independent pairwise reference agrees", true], ["within-condition sketch agrees", true], ["independent pairwise reference agrees", true], ["within-condition sketch agrees", true], ["independent pairwise reference agrees", true], ["within-condition sketch agrees", true], ["condition-offset sensor gives no yes", true], ["condition-offset sensor gives no yes", true], ["condition-offset sensor gives no yes", true], ["condition-offset sensor gives no yes", true], ["condition-offset sensor gives no yes", true], ["unknown condition records a flag", true], ["unknown condition retains an unavailable prediction", true], ["unknown condition omitted from within stats", true], ["unknown condition records a flag", true], ["unknown condition retains an unavailable prediction", true], ["unknown condition omitted from within stats", true]]
STAGEB_R2 timing_spread_sweep stalled [{"episode_factor_half_width": 0.0, "increment_r": 0.04899396302686891, "interval_95": [-0.15627770234212882, 0.2502086290193932], "jitter_ns": 2000000, "mean_decode_ms_per_token": 55.480608874159074, "scenario_axis": "per_token_jitter", "timing_scenario": "blocking_uploads", "verdict": "no", "within_condition_sd_episode_mean_decode_ms": 0.3688315632613681}, {"episode_factor_half_width": 0.0, "increment_r": 0.5435884172451112, "interval_95": [0.3821995378666403, 0.6727977743083902], "jitter_ns": 10000000, "mean_decode_ms_per_token": 55.47849509122721, "scenario_axis": "per_token_jitter", "timing_scenario": "blocking_uploads", "verdict": "inconclusive at this cohort size", "within_condition_sd_episode_mean_decode_ms": 0.44758826828606724}, {"episode_factor_half_width": 0.0, "increment_r": 0.7579552887635139, "interval_95": [0.655447422233347, 0.8330417830958603], "jitter_ns": 25000000, "mean_decode_ms_per_token": 55.490341776828345, "scenario_axis": "per_token_jitter", "timing_scenario": "blocking_uploads", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 0.8161511237517547}, {"episode_factor_half_width": 0.0, "increment_r": 0.04899396302686891, "interval_95": [-0.15627770234212882, 0.2502086290193932], "jitter_ns": 2000000, "mean_decode_ms_per_token": 55.480608874159074, "scenario_axis": "episode_factor", "timing_scenario": "blocking_uploads", "verdict": "no", "within_condition_sd_episode_mean_decode_ms": 0.3688315632613681}, {"episode_factor_half_width": 0.025, "increment_r": 0.686035327557215, "interval_95": [0.5606805189143128, 0.7806487860091953], "jitter_ns": 2000000, "mean_decode_ms_per_token": 55.34595117629666, "scenario_axis": "episode_factor", "timing_scenario": "blocking_uploads", "verdict": "inconclusive at this cohort size", "within_condition_sd_episode_mean_decode_ms": 0.8688691178706056}, {"episode_factor_half_width": 0.05, "increment_r": 0.7619290435616316, "interval_95": [0.6607793529019045, 0.8358978828515917], "jitter_ns": 2000000, "mean_decode_ms_per_token": 55.21129348255751, "scenario_axis": "episode_factor", "timing_scenario": "blocking_uploads", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 1.5755438019786991}, {"episode_factor_half_width": 0.1, "increment_r": 0.7966994781193362, "interval_95": [0.7078734222005973, 0.860719110764389], "jitter_ns": 2000000, "mean_decode_ms_per_token": 54.94197809209527, "scenario_axis": "episode_factor", "timing_scenario": "blocking_uploads", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 3.04343443276818}, {"episode_factor_half_width": 0.2, "increment_r": 0.7724484684654346, "interval_95": [0.6749436307508296, 0.8434393353124494], "jitter_ns": 2000000, "mean_decode_ms_per_token": 54.40334730919053, "scenario_axis": "episode_factor", "timing_scenario": "blocking_uploads", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 6.010339323851212}]
STAGEB_R2 timing_spread_sweep counterfactual_no_stall [{"episode_factor_half_width": 0.0, "increment_r": 0.7356087476296433, "interval_95": [0.6256522408405558, 0.8169055178178175], "jitter_ns": 2000000, "mean_decode_ms_per_token": 49.993059874159066, "scenario_axis": "per_token_jitter", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "inconclusive at this cohort size", "within_condition_sd_episode_mean_decode_ms": 0.07162480821319159}, {"episode_factor_half_width": 0.0, "increment_r": 0.7559081407867783, "interval_95": [0.6527045689491857, 0.8315688504317809], "jitter_ns": 10000000, "mean_decode_ms_per_token": 49.99094609122721, "scenario_axis": "per_token_jitter", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 0.29280442094163983}, {"episode_factor_half_width": 0.0, "increment_r": 0.7883569959239218, "interval_95": [0.6965016556413341, 0.8547913703832256], "jitter_ns": 25000000, "mean_decode_ms_per_token": 50.00279277682834, "scenario_axis": "per_token_jitter", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 0.7793901184962744}, {"episode_factor_half_width": 0.0, "increment_r": 0.7356087476296433, "interval_95": [0.6256522408405558, 0.8169055178178175], "jitter_ns": 2000000, "mean_decode_ms_per_token": 49.993059874159066, "scenario_axis": "episode_factor", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "inconclusive at this cohort size", "within_condition_sd_episode_mean_decode_ms": 0.07162480821319159}, {"episode_factor_half_width": 0.025, "increment_r": 0.7648486353025981, "interval_95": [0.6647033382309879, 0.8379937630944094], "jitter_ns": 2000000, "mean_decode_ms_per_token": 49.858402176296664, "scenario_axis": "episode_factor", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 0.7571497079850513}, {"episode_factor_half_width": 0.05, "increment_r": 0.7814125835657253, "interval_95": [0.687070678939731, 0.8498437707744042], "jitter_ns": 2000000, "mean_decode_ms_per_token": 49.72374448255751, "scenario_axis": "episode_factor", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 1.4999744697804493}, {"episode_factor_half_width": 0.1, "increment_r": 0.7749197465052431, "interval_95": [0.6782816331764044, 0.8452069632920194], "jitter_ns": 2000000, "mean_decode_ms_per_token": 49.45442909209527, "scenario_axis": "episode_factor", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 2.9880719983742057}, {"episode_factor_half_width": 0.2, "increment_r": 0.7878029811651506, "interval_95": [0.6957480998268136, 0.8543971011153042], "jitter_ns": 2000000, "mean_decode_ms_per_token": 48.915798309190535, "scenario_axis": "episode_factor", "timing_scenario": "counterfactual_no_upload_stalls", "verdict": "yes", "within_condition_sd_episode_mean_decode_ms": 5.965505972909796}]
```

Additional unchanged-path evidence from round-1 review/CLI at the fixed head:

```text
STAGEB_REVIEW e2e nvml_100ms_25ms {"apparent": [-0.0020557139120364475, 0.05875739027365367], "bound": 8.42705045427661e-05, "ci": [0.07663600667060576, 0.45240035809789975], "contrast": 0.5982422458787154, "episodes": 96, "forecast_r": 0.34931967851221857, "increment": {"flags": ["nominal_fisher_interval_not_null_calibrated"], "held_out_effective_n": 93, "held_out_episodes": 96, "verdict": "no", "within_condition_held_out_correlation": 0.13375996013901492, "within_condition_held_out_interval_95": [-0.0719114299727998, 0.32852019036886765]}, "mean_power": {"flags": [], "held_out_effective_n": 96, "held_out_episodes": 96, "verdict": "no", "within_condition_held_out_correlation": 0.2797199163562553, "within_condition_held_out_interval_95": [0.08173163642031049, 0.45646919101002054]}, "phase_err_sd_J": 1.5550265470318823, "recovery_meets": false, "required_r": 0.6471202066782847, "status": "ok", "timing": {"flags": [], "held_out_effective_n": 96, "held_out_episodes": 96, "verdict": "yes", "within_condition_held_out_correlation": 0.8213906829904342, "within_condition_held_out_interval_95": [0.7423138889988465, 0.8779015354109604]}, "true": [0.00940750848, 0.17660279808], "verdict": "no", "within_r": 0.274986590911851, "worst_case_bound_j": 0.021304553807677085}
STAGEB_REVIEW e2e_blind ina3221 {"apparent": [0.0, 0.0], "bound": 0.0009602050137892887, "ci": null, "contrast": 0.5982422458787154, "episodes": 96, "forecast_r": 0.07136020806232629, "increment": {"flags": ["constant_power_increment_feature", "undefined_power_increment_correlation", "nominal_fisher_interval_not_null_calibrated"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "mean_power": {"flags": ["constant_training_power_feature", "undefined_observed_correlation", "held_out_recovery_inconclusive_at_cohort_size"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "phase_err_sd_J": 8.352651279661636, "recovery_meets": null, "required_r": 0.6471202066782847, "status": "ok", "timing": {"flags": [], "held_out_effective_n": 96, "held_out_episodes": 96, "verdict": "yes", "within_condition_held_out_correlation": 0.8213906829904342, "within_condition_held_out_interval_95": [0.7423138889988465, 0.8779015354109604]}, "true": [0.00940750848, 0.17660279808], "verdict": "inconclusive at this cohort size", "within_r": null, "worst_case_bound_j": 0.7676456827982208}
STAGEB_REVIEW e2e_blind nvml_100ms_25ms {"apparent": [0.0, 0.0], "bound": 8.42705045427661e-05, "ci": null, "contrast": 0.5982422458787154, "episodes": 96, "forecast_r": 0.07136020806232628, "increment": {"flags": ["constant_power_increment_feature", "undefined_power_increment_correlation", "nominal_fisher_interval_not_null_calibrated"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "mean_power": {"flags": ["constant_training_power_feature", "undefined_observed_correlation", "held_out_recovery_inconclusive_at_cohort_size"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "phase_err_sd_J": 8.352651279661636, "recovery_meets": null, "required_r": 0.6471202066782847, "status": "ok", "timing": {"flags": [], "held_out_effective_n": 96, "held_out_episodes": 96, "verdict": "yes", "within_condition_held_out_correlation": 0.8213906829904342, "within_condition_held_out_interval_95": [0.7423138889988465, 0.8779015354109604]}, "true": [0.00940750848, 0.17660279808], "verdict": "inconclusive at this cohort size", "within_r": null, "worst_case_bound_j": 0.021304553807677085}
STAGEB_REVIEW default_blind ina3221 {"apparent": [0.0, 0.0], "bound": 0.0011086205353178814, "ci": null, "contrast": 0.8631576590651903, "episodes": 24, "forecast_r": 0.0770312679988224, "increment": {"flags": ["constant_power_increment_feature", "undefined_power_increment_correlation", "nominal_fisher_interval_not_null_calibrated"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "mean_power": {"flags": ["constant_training_power_feature", "undefined_observed_correlation", "held_out_recovery_inconclusive_at_cohort_size"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "phase_err_sd_J": 11.158883730059388, "recovery_meets": null, "required_r": 0.6471202066782847, "status": "ok", "timing": {"flags": [], "held_out_effective_n": 24, "held_out_episodes": 24, "verdict": "yes", "within_condition_held_out_correlation": 0.8438154771382044, "within_condition_held_out_interval_95": [0.6553517606446033, 0.9333699301483963]}, "true": [0.01017297792, 0.17649062784], "verdict": "inconclusive at this cohort size", "within_r": null, "worst_case_bound_j": 1.0232899505603228}
STAGEB_REVIEW default_blind nvml_100ms_25ms {"apparent": [0.0, 0.0], "bound": 9.729590068353058e-05, "ci": null, "contrast": 0.8631576590651903, "episodes": 24, "forecast_r": 0.0770312679988224, "increment": {"flags": ["constant_power_increment_feature", "undefined_power_increment_correlation", "nominal_fisher_interval_not_null_calibrated"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "mean_power": {"flags": ["constant_training_power_feature", "undefined_observed_correlation", "held_out_recovery_inconclusive_at_cohort_size"], "held_out_effective_n": 0, "held_out_episodes": 0, "verdict": "inconclusive at this cohort size", "within_condition_held_out_correlation": null, "within_condition_held_out_interval_95": null}, "phase_err_sd_J": 11.158883730059388, "recovery_meets": null, "required_r": 0.6471202066782847, "status": "ok", "timing": {"flags": [], "held_out_effective_n": 24, "held_out_episodes": 24, "verdict": "yes", "within_condition_held_out_correlation": 0.8438154771382044, "within_condition_held_out_interval_95": [0.6553517606446033, 0.9333699301483963]}, "true": [0.01017297792, 0.17649062784], "verdict": "inconclusive at this cohort size", "within_r": null, "worst_case_bound_j": 0.02839947686945834}
STAGEB_REVIEW p3 contiguous_6.6ms {"apparent": [0.0024222549777566885, 0.05298272846853936], "bound": 0.0009114822573562025, "ci": [0.7276193778957244, 0.8703636017948386], "contrast": 0.5982422458787154, "episodes": 96, "forecast_r": 0.8109358181564447, "increment": {"flags": ["nominal_fisher_interval_not_null_calibrated"], "held_out_effective_n": 93, "held_out_episodes": 96, "verdict": "yes", "within_condition_held_out_correlation": 0.8219116242960651, "within_condition_held_out_interval_95": [0.7425226466559279, 0.8785286784177099]}, "mean_power": {"flags": [], "held_out_effective_n": 96, "held_out_episodes": 96, "verdict": "yes", "within_condition_held_out_correlation": 0.8083738802855257, "within_condition_held_out_interval_95": [0.7244060763277498, 0.8687062918438864]}, "phase_err_sd_J": 0.1713564423832338, "recovery_meets": true, "required_r": 0.6471202066782847, "status": "ok", "timing": {"flags": [], "held_out_effective_n": 96, "held_out_episodes": 96, "verdict": "no", "within_condition_held_out_correlation": -0.010303124188217116, "within_condition_held_out_interval_95": [-0.21248013030776805, 0.19271978742984244]}, "true": [0.00281346048, 0.05281579008], "verdict": "yes", "within_r": 0.8107156206127827, "worst_case_bound_j": 0.6917183744201088}
STAGEB_REVIEW p5 default_drop_change {"change_j_per_token": 2.6250000000060947e-08, "dropped_j_per_token": 0.009750032454274273, "full_j_per_token": 0.009750006204274273}
```

## DECISIONS I MADE

- Continue the pushed head; do not redo any already-pushed code. Use the available GitHub connector because the managed workspace has no usable executor. Every ref update is a fast-forward, expected-head-checked and force=false, only on lane/2026-10-21-align-stageb.
- The governing round-2 brief determines the primary conditional increment. Every nuisance fit, residual slope and target condition mean is training-only and within condition. The final score additionally centres held-out truth/prediction within condition, matching the reviewer sketch. No pooled-mean term enters both target and prediction. q6 shows no design difference.
- Carry condition explicitly in the lane-local RoutingObservation, sourced from Episode.condition. Keep condition=None as a compatible construction default; it records a flag and unavailable prediction rather than guessing from opaque IDs. Scalar unconditional candidates remain descriptive; their within-condition evaluation reads the field.
- Constant timing uses zero timing slopes and a flag. Its arithmetic threshold is derived from O(N) ulps of centering, not a measured-effect bar. Missing labels are omitted only from within-condition statistics, never silently relabelled or removed from the episode ledger.
- Episode timing factors are independent of routes and token jitter, multiply compute-only durations, and leave running W fixed. Added duration changes background J and phase alignment; transfer bytes/J and stall construction are unchanged. The zero default preserves all original synthetic traces.
- Expand the scenario factor grid to ±20% so it reaches beyond the lead's 5%-of-mean-time criterion even with blocking uploads; the grid points themselves are scenario inputs, not physical thresholds. Keep and print the full non-monotonic sweep, including the duplicate zero-factor anchor.
- F4 fallback is explicit: marginal d_A and required r remain the supplied design, with provenance/flags. It cannot be read as timing-conditional design power. No new condition effect is inferred from these simulations.
- F5 fallback is explicit: energy-only/forecast retain the true supplied running level, labelled unavailable on hardware. The strict increment and mean power retain baseline-offset invariance; no hardware analyst-baseline claim is made.
- F6 fallback is explicit: no permutation/null calibration is added. Nominal negative-null Fisher intervals are disclosed next to the decision. A no is a scenario comparison, not measured absence; yes is not validated design power.
- F8 bounds the complete Gaussian Fourier series by its geometric majorant and trivial q/2 cap continuously; the noise/rounding covariance uses Gaussian integration by parts plus an integral bound. Current strongly dithered worlds move only far below the rule-3 bound. The separate same-sign q*T alternative stays labelled.
- Existing observed-coverage integration, 1.1 ms INA shunt slices, independent noise RNG, physical upload-stall truth, prefill cache guard and supply/throttle procedures remain. Dropped samples keep numeric features/flags; no new real-data eligibility rule is introduced.
- The 34-test module changes a flag expectation and the residual-forecast oracle to the continuous bound; its .8 ideal test now sets both noise and quantum to zero. The four-test review module supplies Episode.condition to its capture. The round-2 baseline collector becomes asserted regressions and adds sweep/continuous-bound checks. These update changed criteria/worlds; no prior pass condition or numerical agreement bar was weakened.
- Report/doc tables are generated from the exact CI-printed values, with decimal rounding for readability. Raw lines retain full precision. All named fix commits remain in the fast-forward ancestry (GitHub compare reports ahead for each named round-1 base; round-2 history is a straight fast-forward from 932719cfc). The inherited registry line is untouched and deferred as directed.
- Original different-model oracle provenance is historical. The new pair-difference derivation is mathematically separate from production, and the external reviewer's independent sketch agrees; this seat does not claim that it constitutes the pipeline's future different-model/cold executing gate.
- No subagents, optional packages, hardware operations, inference services, paid services, out-of-scope repository changes, merge or ready transition were used.

## CONTRACT-CHANGE

No shared file was modified. The existing shared RouterLog has no token/turn/
microbatch timestamps. Desired future companion timing record: token ordinal,
turn/phase, start/end brackets, microbatch identity and clock domain. The lane
uses explicit TokenWindow inputs and flags as its local adapter. Explicit
RoutingObservation.condition is lane-local and requires no shared schema change.

## OPEN ISSUES

- Hardware Stage A effects, timing-conditional effect, memory bandwidth/J-per-byte, deployed shunts/acquisition/cadence/phase, baseline estimator, noise/systematic uncertainty and logger perturbation need independent calibration before any physical interpretation.
- Nominal cross-validated Fisher intervals need null/dependence calibration before a measured absence or design-power claim. The condition-offset stalled probe remains high but inconclusive; the F6 fallback applies to it too.
- Conditional increment and descriptive mean-power recovery answer different scientific questions. This brief chooses the former; no alternative is selected after seeing the result.
- Every no-stall world is counterfactual relative to the pinned blocking-upload backend. The stalled verdict depends on realistic between-episode timing spread; no universal sensor detectability conclusion follows.
- Exact upstream replay still needs group/slot/reset and actual microbatch/token timing inventory; large-batch read-only cache reuse remains flagged as unmodelled.
- The numerical reference and independent reviewer sketch agree, but lead-owned independent executing review, merged-tree verification and cold final gate remain unfilled. Gate-ledger failure is expected and is not waived.
- F7 is deferred: the lead has now landed 6bca315c2 on the spine and must resolve/drop this lane's inherited line in tests/test_shard_tests.py. Its overlapping change blocks GitHub's final PR merge tree and CI. The exact path is preserved under the explicit F7 instruction; taking the spine version requires new authority for this seat.
- No usable executor existed for literal local discovery, git checkout or isolated-script execution. CI fallback evidence is identified explicitly.

## NEEDS_RULING

none for the scientific implementation. The brief fixes the primary estimand
and explicitly permits F4/F5/F6 fallbacks. Calibration, registration and
measured-result interpretation remain prospective lead work. The operational
F7 scope block is recorded in TESTS RUN / OPEN ISSUES: the lead must resolve
tests/test_shard_tests.py, or authorize this seat to take the spine version,
before final-head CI can run. This is not a change of scientific criterion.

## FIX ROUND 2

Implemented/verified training-only condition fixed effects, explicit condition
provenance, independent episode timing sensitivity and continuous rounding with
covariance. Replaced the withdrawn affirmative default counterfactual decision
with the executed inconclusive result. Printed both timing grids and the
stalled-world transition, retained the permitted F4/F5/F6 fallbacks, and deferred
F7. This continuation changes documentation/evidence only after reading the
successful code-head CI; it does not redo the pushed implementation. The lead's
new spine registry commit creates an F7 overlap, so final-head CI remains
blocked rather than silently expanding this seat's write scope.

The baseline evidence commit e229ff9b9 retains the failures. The implementation
commit is 49d2232f4; ac07bbbde extends the factor grid and a01f24374 asserts
the lead's 5% reach. cc46dff46 completes the continuous covariance bound.
0e5f17335 corrects the zero-noise forecast test's quantization allowance.
The existing tests' changes are described under DECISIONS I MADE.

## HISTORY

Round 1's complete evidence remains at 932719cfc5f73c7029048f38696d17d08ec2833b.
It removed simulator compute-reference leakage, fixed observed coverage and
INA acquisition, separated the noise stream and preserved the upstream cache
guard/hazard procedure. Its 42-test result is historical; the current 45-test
alignment result supersedes it. Earlier affirmative counterfactual conclusions
are superseded by the within-condition fit and the sensitivity sweep.

## FIX LOG

### Round 1

- F1 — fixed 43d19f6fd3b9b1f89e88627a44db7d504618bc2c: timing-controlled held-out power increment, timing/mean-power alternatives, blind-sensor regression and unavailable reference aliases.
- F2 — fixed c8cc1cd01f85c01e08a0bb7a667e8b962dd59b15: q²/12 random rounding propagated to condition means; q*T is a labelled alternative.
- F3 — fixed 5da157ca79e586045925db30dd1d7ec7820b9b9b: integrate existing coverage, retain every episode, flag gaps and print the default dropped-feature delta.
- F4 — fixed e535c1d2e7d79e6415be4df66b7a5d7edd6aba81: default shunt-slice acquisition, disjoint averages and separate span/duty; the CI port explicitly retains the original 6.6 ms and 1.1 ms worlds.
- F5 — fixed c8cc1cd01f85c01e08a0bb7a667e8b962dd59b15: forecast phase bias is labelled as fitted on the same evaluated episodes.
- F6 — fixed c8cc1cd01f85c01e08a0bb7a667e8b962dd59b15: INA 0.04 W noise is explicitly a scenario parameter.
- F7 — rejected: lead lands it on the spine; the inherited tests/test_shard_tests.py line is unchanged this round, as the brief directs.
- F8 — fixed 7a05e30eab947478c563c6649c81654d5f12522a: short prefill batches update cache under the pinned size/slot guard; 32/33-token regressions check warming, eviction and preservation.
- F9 — fixed c8cc1cd01f85c01e08a0bb7a667e8b962dd59b15: algebraic zero uses float noise; apparent resident energy has a separate sensor-derived bound.
- F10 — fixed c8cc1cd01f85c01e08a0bb7a667e8b962dd59b15: noise uses its own derived seed; a legacy-noise-seed ablation prints the numerical change.
- STAGEB-S — fixed c8cc1cd01f85c01e08a0bb7a667e8b962dd59b15: per-episode supply/throttle flags, inclusive and labelled unflagged results, and electrical-hazard handling are in both hardware procedures.

### Round 2

- F1 — fixed 49d2232f41a7178da4c4b5d4cabff2424bf5798e: all nuisance/residual slopes and target centering use training-only condition fixed effects; constant timing flags, condition-only/random-covariate regressions and separate pair-difference reference pass.
- F2 — fixed 49d2232f41a7178da4c4b5d4cabff2424bf5798e: RoutingObservation.condition is copied from Episode.condition; all condition reads use it, unknown labels flag, hash-ID results are bit-identical.
- F3 — fixed 49d2232f41a7178da4c4b5d4cabff2424bf5798e, ac07bbbde0491db6278f706d4db574f02faf2644 and a01f2437442c34d322d0b728b6dc78a1e6c4f2c9; executed decision/tables ca1fc44890a777dcc54223a1c7fdd62dd740f821: independent episode compute factors, both sweeps reaching beyond 5% mean decode time, and counterfactual labels.
- F4 — fallback 49d2232f41a7178da4c4b5d4cabff2424bf5798e: the marginal Stage A requirement is labelled beside the formula and in Decision; it cannot establish timing-conditional design power.
- F5 — fallback 49d2232f41a7178da4c4b5d4cabff2424bf5798e: energy-only and forecast use simulator running truth, unavailable on hardware; labelled in provenance, Decision and outcome-column heading. const_off energy-only yes is disclosed.
- F6 — fallback 49d2232f41a7178da4c4b5d4cabff2424bf5798e: no null calibration is shipped; Decision quotes the reviewer's negative-null examples and states that no is not a measured absence.
- F7 — deferred: the lead lands the registry line on the spine and drops it from this lane before merge; tests/test_shard_tests.py is exactly unchanged from the round-2 starting branch.
- F8 — fixed cc46dff463dde193cb675486395dd735fc9e8c41; oracle-test adjustment 0e5f1733553a3e4f7d8571e685ba39b4a0c9bafb: continuous Fourier rounding bias/second-moment plus Gaussian covariance bound, no sigma=q/2 switch; current-world changes stay below the rule-3 bar.
