# Round 2 execution checkpoint

Continued from 932719cfc5f73c7029048f38696d17d08ec2833b.
The test-only baseline checkpoint is e229ff9b9eb405c7dd705b7f2835c8132f7b4bae.
The managed environment has not supplied a shell. The explicit no-shell CI
fallback ports all listed worlds/pass conditions into test_moe_stage_b_round2.
F1/F2 implement condition fixed effects and explicit Episode.condition.
F3 adds an independent per-episode compute-duration factor and a sweep.
F8 replaces the dither switch by continuous Gaussian Fourier bounds.
F4/F5/F6 use the brief's permitted limitations; F7 is deferred to the lead.
Execution and a final evidence-based decision are pending; the prior report
below is historical and its affirmative counterfactual no-stall conclusion
is withdrawn pending the fixed run.

---

# align-stageb lane report

## SUMMARY

Continued lane/2026-10-21-align-stageb from ebba5483358d088d4cae81cbdfc944fae0503027; shared contracts are unchanged.
Stage B now uses group-held-out power recovery after timing control, with timing-only, energy and mean-power alternatives printed beside it.
Removed the simulator compute reference; observed coverage supplies every energy feature, and blind sensors no longer produce yes.
Dithered rounding uses q²/12; same-sign q*T remains a labelled alternative, never the verdict.
INA defaults to shunt-slice acquisition; small prefill batches update cache, and sensor noise has its own seed stream.
Dropped samples retain numeric features, coverage flags and all 24 episodes; hardware procedures now cover supply and throttling hazards.
All 42 alignment tests executed successfully in CI, with zero failures/errors/skips; summed module time was 448.824s.
Stalled worlds fail the chosen increment criterion; no-stall INA clears it. Mean-power alternatives differ and are recorded under NEEDS_RULING.
PR #526 remains draft and unmerged; final-head CI continues independently, with no hardware or external inference service used.

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
- `SensorModel(name: str, source: str, channel: str, interval_ns: int, averaging_window_ns: int, quantum_w: float, noise_std_w: float, phase_ns: int = 0, notes: str = "", acquisition_slices_ns: tuple[tuple[int, int], ...] = ())`.
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

The managed environment failed to provision: snapshot_materialization_failed /
gateway_unavailable. No shell, local git checkout, .review1 file creation or
literal local command ran. The brief's explicit CI fallback was used. Each
review test scopes JW_B5_SYNTHETIC_ONLY=1 using patch.dict; it restores the
environment afterward. Tests make no network or hardware calls.

**Executed fixed code: dfe3436e10c07a57ed65f086b7228b213009ba35,
[CI 39726492085](https://github.com/mpmdw/JouleWise/actions/runs/39726492085).**

| Actual CI module / job | Tests | Failures | Errors | Skips | Module elapsed seconds |
|---|---:|---:|---:|---:|---:|
| tests.align.test_moe_stage_b / 119653179134 (shard 9) | 34 | 0 | 0 | 0 | 159.159 |
| tests.align.test_moe_stage_b_review / 119653178717 (shard 8) | 4 | 0 | 0 | 0 | 289.657 |
| tests.align.test_records / 119653178824 (shard 5) | 4 | 0 | 0 | 0 | 0.008 |
| Total | 42 | 0 | 0 | 0 | 448.824 |

The observed span across these parallel CI modules was 296.463s
(05:16:31.2318399 to 05:21:27.6947200 UTC). That span and the summed module
times are not the wall time of the unrun local discovery command.

The original 34-test module took 134.801s at the baseline checkpoint and
159.159s after the fix (+24.358s). The required reviewer port took 246.748s
before and 289.657s after (+42.909s), now also covering the 48-episode
noise-seed ablation, eight-episode oracle and two small source regressions.
It runs 874 episode simulations; the existing large E2E/CLI cases run another
576. This cost is the requested repro coverage, not a new parameter grid.

Before fixed-code publication, checkpoint f0c25415485c3e866bfdb8cc669d5231de9f5c2f
retained unchanged ebba54833 production code and ran the p1--p5 worlds:
[baseline CI 39722816945](https://github.com/mpmdw/JouleWise/actions/runs/39722816945).
All 34 original Stage B tests, four records tests and the one baseline evidence
test executed successfully: 39 tests, zero lane skips/failures/errors,
381.553s summed module time. The original table and all major failures match
the lead's repro values.

CI's **actual** unchanged entry is the heredoc below, with SHARD_COUNT=12 and
SHARD_INDEX=5,8,9 for the relevant module jobs. It uses unittest's loader and
TextTestRunner through shard_tests.run_units. It is not claimed as the literal
unrun discovery or isolated-script command.

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

The standalone CLI was actually invoked by the existing subprocess test:

```text
/opt/hostedtoolcache/Python/3.13.16/x64/bin/python -m joulewise.align.moe_stage_b.experiment
```

Build, fences, installed-wheel and quick tier passed in fixed-code CI before
the report-only checkpoint superseded it. The ordinary jobs were then cancelled
by the unchanged PR concurrency policy, **after all three alignment MODULE PASS
lines**. This is focused execution evidence, not a passing whole-repository
suite or final-head CI claim. No whole suite was launched locally.
The final report/runbook commit changes no Python source relative to the tested
head. Final-head CI is intentionally not awaited; PR #526 stays draft.

The literal commands requested below remain **UNRUN** because no executor
existed. Their worlds and pass conditions were ported into the review module;
the port keeps calling experiment.simulate_episode and experiment.extract_features
through the experiment globals. In p3, the final port explicitly spells out the
same original 6.6ms and 1.1ms alternatives after the default changes to shunt
acquisition. No routing, timing, cohort or noise parameter from a repro was tuned.

```sh
JW_B5_SYNTHETIC_ONLY=1 python3 -m unittest discover -s tests/align -t .
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p1_leak.py e2e
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p1_leak.py e2e_blind
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p1_leak.py default
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p1_leak.py default_blind
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p2_quant.py
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p3_ina_slice.py
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p4_flags.py
JW_B5_SYNTHETIC_ONLY=1 python3 -I /workspace/JouleWise/.review1/p5_drop_world.py
```

Extras: none installed, imported or required by the lane. There are no
extra-dependent lane tests and zero skip reasons to list. CI's packaging
frontend is not a project extra; no extra-dependency run was applicable.

## END-TO-END

Production chain: synthetic_episode -> synthetic_token_schedule ->
apply_decode_stalls -> model_traffic -> simulate_episode -> shared PowerTrace ->
extract_features(actual windows) -> grouped scalar recovery / timing-controlled
recovery -> nominal Fisher interval / fixed Stage A design comparison.

E2E: 48 task groups per condition, three turns, 768 prefill and 384 decode tokens,
three local tool calls per episode, N=96. Default: 12 groups per condition,
four turns, 1024 prefill and 512 decode tokens, four tool calls, N=24.
Compute jitter is the declared +/-2ms scenario around 50ms steps; blocking stalls
are explicit. Architecture/cache/bandwidth/J-per-byte parameters are unchanged.
Required r remains 0.6471202066782847 for d=1, n=50, alpha=.05, power=.8,
three supplied comparisons.

INA is now 1.1ms shunt acquisition / 10ms cadence with 0.036032W quantum and
0.04W scenario noise. The contiguous 6.6ms frame is an alternative. NVML remains
25ms / 100ms, 0.001W quantum and 1W stress-scenario noise. Both see the same
synthetic running loads; these are not RTX/Jetson calibrations.

### Current criterion and the other readings

| World / sensor | Energy r [95% CI] | Timing-only r [95% CI] | Mean-power r [95% CI] | Increment r [95% CI] | Stage B |
|---|---|---|---|---|---|
| e2e ina3221 | 0.7847682385203254 [0.6922172578618175, 0.8519241883004665] | 0.8213906829904342 [0.7423138889988465, 0.8779015354109604] | 0.844028133904538 [0.7737286721887902, 0.8937942788319294] | 0.03878094817615853 [-0.16624431709872659, 0.24059214797596737] | no |
| e2e nvml_100ms_25ms | 0.274986590911851 [0.07663600667060576, 0.45240035809789975] | 0.8213906829904342 [0.7423138889988465, 0.8779015354109604] | 0.2797199163562553 [0.08173163642031049, 0.45646919101002054] | 0.13023441275020084 [-0.07548000626420594, 0.32531560352046] | no |
| default ina3221 | 0.7740006547148806 [0.5230834994984437, 0.9014464496892164] | 0.8438154771382044 [0.6553517606446033, 0.9333699301483963] | 0.8478338120759732 [0.6633335569803914, 0.9351652157432788] | 0.1734304799794651 [-0.2791638835042857, 0.5629748878035307] | no |
| default nvml_100ms_25ms | 0.6345858161086284 [0.29076507775888405, 0.8332611577713871] | 0.8438154771382044 [0.6553517606446033, 0.9333699301483963] | 0.6736148880248951 [0.35195791312058256, 0.8529787790146469] | -0.5886004907339206 [-0.8135700110924684, -0.21035765763800887] | no |
| p3 shunt_slice_1.1ms | 0.7245660029010135 [0.611758967778493, 0.8084904919807115] | -0.010303124188217116 [-0.21248013030776805, 0.19271978742984244] | 0.7235703428110349 [0.6104476360084228, 0.8077643915236326] | 0.8938423135247563 [0.8437692437918409, 0.9284890626614218] | yes |
| p3 contiguous_6.6ms (alternative) | 0.8107156206127827 [0.7276193778957244, 0.8703636017948386] | -0.010303124188217116 [-0.21248013030776805, 0.19271978742984244] | 0.8083738802855257 [0.7244060763277498, 0.8687062918438864] | 0.9270878135830587 [0.891800255448484, 0.9511640036403203] | yes |

All four blind worlds complete with 96/24 episodes, zero observed extra energy,
constant-feature flags and inconclusive verdicts. Their timing-only r is still
0.8213906829904342 (E2E) / 0.8438154771382044 (default).
The stalled worlds therefore show timing recovery without a detected conditional
power increment. The no-stall shunt INA world clears the chosen increment bar,
while its energy-only / mean-power intervals are inconclusive. The difference
between these estimands is retained for a prospective lead ruling below; no
physical detectability or independent validation is claimed.

### Numbers moved from the reviewed head

| Probe | Before energy r / verdict | After energy r / verdict | Change in energy r |
|---|---|---|---|
| e2e ina3221 | 0.8232371412861 / yes | 0.7847682385203254 / no | -0.03846890276577464 |
| e2e nvml_100ms_25ms | 0.7470347806978304 / inconclusive at this cohort size | 0.274986590911851 / no | -0.47204818978597934 |
| default ina3221 | 0.80737563681128 / inconclusive at this cohort size | 0.7740006547148806 / no | -0.03337498209639944 |
| default nvml_100ms_25ms | 0.6653557102979055 / inconclusive at this cohort size | 0.6345858161086284 / no | -0.030769894189277114 |
| p2 q | 0.8093149327426429 / no | 0.7245660029010135 / yes | -0.0847489298416294 |
| p2 fine | 0.8093078674101826 / yes | 0.7245426207698503 / yes | -0.08476524664033225 |
| p3 shunt_slice_1.1ms | 0.7225503465515355 / inconclusive at this cohort size | 0.7245660029010135 / yes | 0.002015656349477979 |
| p3 contiguous_6.6ms | 0.8093149327426429 / no | 0.8107156206127827 / yes | 0.0014006878701398051 |
| p5 stalls | null / null | 0.7740014099210382 / no | new numeric result |
| p5 no-stalls | 0.7847843468528873 / inconclusive at this cohort size | 0.6919038002129244 / yes | -0.09288054663996292 |

These verdict changes include the deliberately changed primary criterion.
A new increment r is not numerically compared to the former energy r as if they
were the same statistic. Physical true_extra ranges, actual decode-duration
ranges and default traffic counts remain unchanged. Apparent extra is now the
trace integral above running baseline over actual covered windows; nominal
compute-duration output is the unavailable None alias.

F2: q/fine now both give yes for the chosen increment. At real q the random
rounding contrast SD is 0.0009114822446086623J versus the labelled same-sign
alternative 0.6917183744201088J; contrast stays 0.5982422458787154J.
Before, q alone flipped no -> yes when reduced. Measured rounding SD moves from
0.004727768884084749 to 0.004324237908642516J (delta
-0.0004035309754422331); its condition-mean
difference moves from 0.0005183719920603264 to 0.00097816833854091J
(delta 0.00045979634648058354).
The old negative-physical-result language is withdrawn.

F4, holding each final no-stall world fixed: the shunt energy r is
0.7245660029010135 versus 0.8107156206127827 for the labelled contiguous frame;
the chosen increments are 0.8938423135247563 and 0.9270878135830587.
Both criteria/readings and uncertainties are printed rather than silently
substituting the 6.6ms approximation for the INA result.

### Coverage and cohort retention

| Sensor | Before full J/token | Before dropped | After full J/token | After dropped J/token | Drop change J/token | Covered fraction |
|---|---:|---|---:|---:|---:|---:|
| p4 ina3221 | 0.16757110982072204 | None | 0.05066580741928828 | 0.050664452419288276 | -0.000001355000000001494 | 0.9993467110604671 |
| p4 nvml_100ms_25ms | 0.16819281044078907 | None | 0.04696391021256252 | 0.04671195708756252 | -0.0002519531250000026 | 0.9934671106046709 |

p5 stalled changes unavailable -> ok with all 24 episodes, numeric energy
recovery r=0.7740014099210382, and verdict no. The dropped episode carries
incomplete_decode_coverage in both its feature flags and outcome flags.
Its full feature is 0.009750006204274273J/token; after deletion it is
0.009750032454274273J/token, delta 2.6250000000060947e-8J/token.
No sensor cell is filled from truth. The no-stall dropped world likewise keeps
24 episodes and prints its full numeric recovery and verdict below.

### Small-prefill and seed effects

F8 alone changes default printed traffic/energy by exactly zero: all default
prefills contain two complete 128-token microbatches per turn, above max_batch.
The 32-token and 33-token cache tests prime 32 ten-byte slots and independently
probe warmth and eviction. Thirty-two updates/evicts, while 33 preserves the
old cache. Integer byte/count assertions test identity, not a measurement bar.

F10's paired comparison changes only the noise seed in the final world:

| Sensor (same final world) | Legacy-noise energy r → new r (delta) | Legacy increment r → new r (delta) | Energy-error SD J, legacy → new |
|---|---|---|---|
| ina3221 | 0.77844467529509 → 0.7740006547148806 (-0.004444020580209429) | 0.13403185926456668 → 0.1734304799794651 (0.039398620714898414) | 0.2813990239517388 → 0.28231468187151165 |
| nvml_100ms_25ms | 0.15004646401054125 → 0.6345858161086284 (0.4845393520980872) | -0.04329725523392728 → -0.5886004907339206 (-0.5453032354999934) | 1.4877634899422347 → 1.6344200800256645 |

INA apparent range changes from [0.0026808824290117726, 0.05281653112874765]
to [0.0027584071277335217, 0.05281015158707227]J/token
(endpoint deltas +0.00007752469872174912, -0.0000063795416753789636).
NVML changes from [0.0015384068183945433, 0.05326329968906447]
to [-0.001115443389494129, 0.05854830610006447]J/token
(deltas -0.0026538502078886726, +0.005285006411).
Both default increment verdicts remain no. Routing, timing, physical traffic
and bounds are identical in this ablation.

The unequal-traffic fixture now observes .03J above a 12W running baseline,
rather than adding .36J from a simulator-only compute reference. Physical
incremental traffic truth still includes .03J transfer + .36J running-stall
energy = .39J. The lower stalled-power fixture observes -.15J above the same
running baseline, with .21J physical incremental truth. Negative corrected
energy is retained, not clipped. Sparse traces remain numeric and flagged.

### Complete before output of the reviewer-world port

These are the actual baseline STAGEB_REVIEW records. The port's extra full raw
Episode dump for the unavailable p5 episode is reduced to its id, flags and
features: the supplied p5 script itself prints only recovery/status/counts.
All measured pass-condition values are retained; literal stdout and individual
elapsed_s of the unrun scripts are not claimed. No raw routing fixture is needed
in the handoff report.

```json
[
  {
    "label": "e2e ina3221",
    "data": {
      "apparent": [
        0.009469296710107855,
        0.17662586599104335
      ],
      "bound": 0.7676456827982208,
      "ci": [
        0.7448633282056377,
        0.879202531603253
      ],
      "contrast": 2.0003725096569545,
      "episodes": 96,
      "forecast_r": 0.833440396453997,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 0.0642570569198771,
      "status": "ok",
      "timing": null,
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "yes",
      "within_r": 0.8232371412861
    }
  },
  {
    "label": "e2e nvml_100ms_25ms",
    "data": {
      "apparent": [
        0.002850384235903659,
        0.17947287898939324
      ],
      "bound": 0.021304553807677085,
      "ci": [
        0.6415172066752958,
        0.8248085321163152
      ],
      "contrast": 2.0003725096569545,
      "episodes": 96,
      "forecast_r": 0.7098517319843417,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 1.4780627284508816,
      "status": "ok",
      "timing": null,
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": 0.7470347806978304
    }
  },
  {
    "label": "e2e_blind ina3221",
    "data": {
      "apparent": [
        0.006594048000000001,
        0.12378700799999999
      ],
      "bound": 0.7676456827982208,
      "ci": [
        0.7472798566036094,
        0.880433855878124
      ],
      "contrast": 2.0003725096569545,
      "episodes": 96,
      "forecast_r": 0.23018146032595468,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 8.352651279661636,
      "status": "ok",
      "timing": null,
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "yes",
      "within_r": 0.8249858080477791
    }
  },
  {
    "label": "e2e_blind nvml_100ms_25ms",
    "data": {
      "apparent": [
        0.006594048000000001,
        0.12378700799999999
      ],
      "bound": 0.021304553807677085,
      "ci": [
        0.7472798566036094,
        0.880433855878124
      ],
      "contrast": 2.0003725096569545,
      "episodes": 96,
      "forecast_r": 0.2301814603259547,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 8.352651279661636,
      "status": "ok",
      "timing": null,
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "yes",
      "within_r": 0.8249858080477791
    }
  },
  {
    "label": "default ina3221",
    "data": {
      "apparent": [
        0.010193455699749773,
        0.17654024210091254
      ],
      "bound": 1.0232899505603228,
      "ci": [
        0.5848415582162446,
        0.9168823931438648
      ],
      "contrast": 2.8861834224992293,
      "episodes": 24,
      "forecast_r": 0.8470073684678862,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 0.0866584442041829,
      "status": "ok",
      "timing": null,
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": 0.80737563681128
    }
  },
  {
    "label": "default nvml_100ms_25ms",
    "data": {
      "apparent": [
        0.01174969970150001,
        0.17697168368906446
      ],
      "bound": 0.02839947686945834,
      "ci": [
        0.33877503376500123,
        0.8488484865196229
      ],
      "contrast": 2.8861834224992293,
      "episodes": 24,
      "forecast_r": 0.7594288439245359,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 1.4877634899422347,
      "status": "ok",
      "timing": null,
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": 0.6653557102979055
    }
  },
  {
    "label": "default_blind ina3221",
    "data": {
      "apparent": [
        0.007130592,
        0.123708384
      ],
      "bound": 1.0232899505603228,
      "ci": [
        0.5893045511592465,
        0.917960688988899
      ],
      "contrast": 2.8861834224992293,
      "episodes": 24,
      "forecast_r": 0.24737518439024686,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 11.158883730059388,
      "status": "ok",
      "timing": null,
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": 0.8097335676240313
    }
  },
  {
    "label": "default_blind nvml_100ms_25ms",
    "data": {
      "apparent": [
        0.007130592,
        0.123708384
      ],
      "bound": 0.02839947686945834,
      "ci": [
        0.5893045511592465,
        0.917960688988899
      ],
      "contrast": 2.8861834224992293,
      "episodes": 24,
      "forecast_r": 0.2473751843902468,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 11.158883730059388,
      "status": "ok",
      "timing": null,
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": 0.8097335676240313
    }
  },
  {
    "label": "p2 q",
    "data": {
      "apparent": [
        0.002413391021682021,
        0.05295295995323052
      ],
      "bound": 0.6917183744201088,
      "ci": [
        0.7256969362755795,
        0.8693724612976198
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.811229791048336,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 0.17020184370230057,
      "status": "ok",
      "timing": null,
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "no",
      "within_r": 0.8093149327426429
    }
  },
  {
    "label": "p2 fine",
    "data": {
      "apparent": [
        0.0024181331680919985,
        0.052958985405741066
      ],
      "bound": 1.9197334991677085e-8,
      "ci": [
        0.7256872424278559,
        0.8693674605738089
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.8114431582001935,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 0.1693596921841463,
      "status": "ok",
      "timing": null,
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "yes",
      "within_r": 0.8093078674101826
    }
  },
  {
    "label": "p2 rounding",
    "data": {
      "condition_difference_j": 0.0005183719920603264,
      "max_abs_j": 0.0116563919086623,
      "sd_j": 0.004727768884084749
    }
  },
  {
    "label": "p3 contiguous_6.6ms",
    "data": {
      "apparent": [
        0.002413391021682021,
        0.05295295995323052
      ],
      "bound": 0.6917183744201088,
      "ci": [
        0.7256969362755795,
        0.8693724612976198
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.811229791048336,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 0.17020184370230057,
      "status": "ok",
      "timing": null,
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "no",
      "within_r": 0.8093149327426429
    }
  },
  {
    "label": "p3 shunt_slice_1.1ms",
    "data": {
      "apparent": [
        0.002275719966728688,
        0.05336706359221885
      ],
      "bound": 0.6917183744201088,
      "ci": [
        0.6091048951018189,
        0.80702027853956
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.7292501346950881,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 0.39763430027584623,
      "status": "ok",
      "timing": null,
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": 0.7225503465515355
    }
  },
  {
    "label": "p4 ina3221",
    "data": {
      "change_j_per_token": null,
      "dropped": {
        "coverage_fraction": 0,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": null,
        "energy_per_decode_token_j": null,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_cache_bypassed",
          "prefill_batch_union_profile_assumption",
          "prefill_readonly_cache_reuse_unmodelled",
          "serialized_token_start_transfer_profile",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "stall_energy_reference_requires_complete_decode_coverage"
        ],
        "token_energy_variance_j2": null,
        "token_rate_amplitude_w": null,
        "token_rate_hz": null
      },
      "full": {
        "coverage_fraction": 1,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.0011383579299676476,
        "energy_per_decode_token_j": 0.16757110982072204,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_cache_bypassed",
          "prefill_batch_union_profile_assumption",
          "prefill_readonly_cache_reuse_unmodelled",
          "serialized_token_start_transfer_profile",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "duty_cycled_apparent_energy",
          "nominal_compute_energy_reference",
          "variance_excludes_running_stall_energy",
          "spectrum_includes_acquisition_transfer_function"
        ],
        "token_energy_variance_j2": 0.00008098993205882508,
        "token_rate_amplitude_w": 0.7556738492549713,
        "token_rate_hz": 16.7241968520425
      },
      "samples": 2492,
      "without_reference": {
        "coverage_fraction": 0.9993467110604671,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.0011376342032777488,
        "energy_per_decode_token_j": 0.04986562732072203,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_cache_bypassed",
          "prefill_batch_union_profile_assumption",
          "prefill_readonly_cache_reuse_unmodelled",
          "serialized_token_start_transfer_profile",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "spectrum_includes_acquisition_transfer_function"
        ],
        "token_energy_variance_j2": 0.00008087669344351342,
        "token_rate_amplitude_w": 0.7566111548667901,
        "token_rate_hz": 16.7241968520425
      }
    }
  },
  {
    "label": "p4 reference",
    "data": {
      "flags": [
        "synthetic_episode",
        "variable_decode_step_timing",
        "blocking_decode_upload_stalls",
        "constant_running_power_during_stall",
        "compute_only_schedule_retimed",
        "prefill_batch_boundaries_unavailable",
        "prefill_cache_bypassed",
        "prefill_batch_union_profile_assumption",
        "prefill_readonly_cache_reuse_unmodelled",
        "serialized_token_start_transfer_profile",
        "sensor_duty_gaps",
        "synthetic_power_trace",
        "duty_cycled_apparent_energy",
        "invalid_reference_decode_duration"
      ]
    }
  },
  {
    "label": "p4 nvml_100ms_25ms",
    "data": {
      "change_j_per_token": null,
      "dropped": {
        "coverage_fraction": 0,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": null,
        "energy_per_decode_token_j": null,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_cache_bypassed",
          "prefill_batch_union_profile_assumption",
          "prefill_readonly_cache_reuse_unmodelled",
          "serialized_token_start_transfer_profile",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "stall_energy_reference_requires_complete_decode_coverage"
        ],
        "token_energy_variance_j2": null,
        "token_rate_amplitude_w": null,
        "token_rate_hz": null
      },
      "full": {
        "coverage_fraction": 1,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.004853970092240914,
        "energy_per_decode_token_j": 0.16819281044078907,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_cache_bypassed",
          "prefill_batch_union_profile_assumption",
          "prefill_readonly_cache_reuse_unmodelled",
          "serialized_token_start_transfer_profile",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "duty_cycled_apparent_energy",
          "nominal_compute_energy_reference",
          "variance_excludes_running_stall_energy",
          "token_rate_at_or_above_nyquist",
          "per_token_energy_underresolved"
        ],
        "token_energy_variance_j2": 0.004814170162236688,
        "token_rate_amplitude_w": null,
        "token_rate_hz": 16.7241968520425
      },
      "samples": 251,
      "without_reference": {
        "coverage_fraction": 0.9934671106046709,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.004837933515826764,
        "energy_per_decode_token_j": 0.05024829356578908,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_cache_bypassed",
          "prefill_batch_union_profile_assumption",
          "prefill_readonly_cache_reuse_unmodelled",
          "serialized_token_start_transfer_profile",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "token_rate_at_or_above_nyquist",
          "per_token_energy_underresolved"
        ],
        "token_energy_variance_j2": 0.004819416986754716,
        "token_rate_amplitude_w": null,
        "token_rate_hz": 16.7241968520425
      }
    }
  },
  {
    "label": "p4 reference",
    "data": {
      "flags": [
        "synthetic_episode",
        "variable_decode_step_timing",
        "blocking_decode_upload_stalls",
        "constant_running_power_during_stall",
        "compute_only_schedule_retimed",
        "prefill_batch_boundaries_unavailable",
        "prefill_cache_bypassed",
        "prefill_batch_union_profile_assumption",
        "prefill_readonly_cache_reuse_unmodelled",
        "serialized_token_start_transfer_profile",
        "sensor_duty_gaps",
        "synthetic_power_trace",
        "duty_cycled_apparent_energy",
        "invalid_reference_decode_duration"
      ]
    }
  },
  {
    "label": "p5 stalls",
    "data": {
      "apparent": null,
      "bound": null,
      "ci": null,
      "contrast": null,
      "episodes": 24,
      "forecast_r": null,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": null,
      "status": "unavailable",
      "timing": null,
      "true": null,
      "verdict": null,
      "within_r": null
    }
  },
  {
    "label": "p5 dropped_episode",
    "data": {
      "flags": [
        "synthetic_episode",
        "variable_decode_step_timing",
        "blocking_decode_upload_stalls",
        "constant_running_power_during_stall",
        "compute_only_schedule_retimed",
        "prefill_batch_boundaries_unavailable",
        "prefill_cache_bypassed",
        "prefill_batch_union_profile_assumption",
        "prefill_readonly_cache_reuse_unmodelled",
        "serialized_token_start_transfer_profile",
        "sensor_duty_gaps",
        "synthetic_power_trace"
      ],
      "features": {
        "coverage_fraction": 0,
        "decode_tokens": 512,
        "energy_half_width_per_token_j": null,
        "energy_per_decode_token_j": null,
        "episode_id": "stageb-task-0-benign",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_cache_bypassed",
          "prefill_batch_union_profile_assumption",
          "prefill_readonly_cache_reuse_unmodelled",
          "serialized_token_start_transfer_profile",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "stall_energy_reference_requires_complete_decode_coverage"
        ],
        "token_energy_variance_j2": null,
        "token_rate_amplitude_w": null,
        "token_rate_hz": null
      },
      "estimates": null,
      "episode_id": "stageb-task-0-benign"
    }
  },
  {
    "label": "p5 no-stalls",
    "data": {
      "apparent": [
        0.0026176096544841473,
        0.05228057185569165
      ],
      "bound": 0.9224808593080986,
      "ci": [
        0.5427539160736634,
        0.9064696062145731
      ],
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.8326439820417312,
      "increment": null,
      "mean_power": null,
      "phase_err_sd_J": 0.19185825239682444,
      "status": "ok",
      "timing": null,
      "true": [
        0.00304238592,
        0.05278224384
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": 0.7847843468528873
    }
  },
  {
    "label": "elapsed",
    "data": {
      "seconds": 246.74594485099996
    }
  }
]
```

### Complete final output of the reviewer-world port

Candidate held_out_effective_n is the raw scalar recovery's count; its
within-condition intervals use N-2. The increment uses N-3. The full default
CLI evidence below also prints the centered count and all scalar candidates.

```json
[
  {
    "label": "e2e ina3221",
    "data": {
      "apparent": [
        0.0018100693076293552,
        0.05323122222085053
      ],
      "bound": 0.0009602049996847113,
      "ci": [
        0.6922172578618175,
        0.8519241883004665
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.7868317148173697,
      "increment": {
        "flags": [],
        "held_out_effective_n": 93,
        "held_out_episodes": 96,
        "verdict": "no",
        "within_condition_held_out_correlation": 0.03878094817615853,
        "within_condition_held_out_interval_95": [
          -0.16624431709872659,
          0.24059214797596737
        ]
      },
      "mean_power": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.844028133904538,
        "within_condition_held_out_interval_95": [
          0.7737286721887902,
          0.8937942788319294
        ]
      },
      "phase_err_sd_J": 0.2514318404779241,
      "recovery_meets": true,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8213906829904342,
        "within_condition_held_out_interval_95": [
          0.7423138889988465,
          0.8779015354109604
        ]
      },
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "no",
      "within_r": 0.7847682385203254,
      "worst_case_bound_j": 0.7676456827982208
    }
  },
  {
    "label": "e2e nvml_100ms_25ms",
    "data": {
      "apparent": [
        -0.0020557139120364475,
        0.05875739027365367
      ],
      "bound": 0.0000842705045427661,
      "ci": [
        0.07663600667060576,
        0.45240035809789975
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.34931967851221857,
      "increment": {
        "flags": [],
        "held_out_effective_n": 93,
        "held_out_episodes": 96,
        "verdict": "no",
        "within_condition_held_out_correlation": 0.13023441275020084,
        "within_condition_held_out_interval_95": [
          -0.07548000626420594,
          0.32531560352046
        ]
      },
      "mean_power": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "no",
        "within_condition_held_out_correlation": 0.2797199163562553,
        "within_condition_held_out_interval_95": [
          0.08173163642031049,
          0.45646919101002054
        ]
      },
      "phase_err_sd_J": 1.5550265470318823,
      "recovery_meets": false,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8213906829904342,
        "within_condition_held_out_interval_95": [
          0.7423138889988465,
          0.8779015354109604
        ]
      },
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "no",
      "within_r": 0.274986590911851,
      "worst_case_bound_j": 0.021304553807677085
    }
  },
  {
    "label": "e2e_blind ina3221",
    "data": {
      "apparent": [
        0,
        0
      ],
      "bound": 0.0009602049996847113,
      "ci": null,
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.07136020806232629,
      "increment": {
        "flags": [
          "constant_power_increment_feature",
          "undefined_power_increment_correlation"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "mean_power": {
        "flags": [
          "constant_training_power_feature",
          "undefined_observed_correlation",
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "phase_err_sd_J": 8.352651279661636,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8213906829904342,
        "within_condition_held_out_interval_95": [
          0.7423138889988465,
          0.8779015354109604
        ]
      },
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": null,
      "worst_case_bound_j": 0.7676456827982208
    }
  },
  {
    "label": "e2e_blind nvml_100ms_25ms",
    "data": {
      "apparent": [
        0,
        0
      ],
      "bound": 0.0000842705045427661,
      "ci": null,
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.07136020806232628,
      "increment": {
        "flags": [
          "constant_power_increment_feature",
          "undefined_power_increment_correlation"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "mean_power": {
        "flags": [
          "constant_training_power_feature",
          "undefined_observed_correlation",
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "phase_err_sd_J": 8.352651279661636,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8213906829904342,
        "within_condition_held_out_interval_95": [
          0.7423138889988465,
          0.8779015354109604
        ]
      },
      "true": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": null,
      "worst_case_bound_j": 0.021304553807677085
    }
  },
  {
    "label": "default ina3221",
    "data": {
      "apparent": [
        0.0027584071277335217,
        0.05281015158707227
      ],
      "bound": 0.0011086205166570683,
      "ci": [
        0.5230834994984437,
        0.9014464496892164
      ],
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.8165087416167143,
      "increment": {
        "flags": [],
        "held_out_effective_n": 21,
        "held_out_episodes": 24,
        "verdict": "no",
        "within_condition_held_out_correlation": 0.1734304799794651,
        "within_condition_held_out_interval_95": [
          -0.2791638835042857,
          0.5629748878035307
        ]
      },
      "mean_power": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8478338120759732,
        "within_condition_held_out_interval_95": [
          0.6633335569803914,
          0.9351652157432788
        ]
      },
      "phase_err_sd_J": 0.28231468187151165,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8438154771382044,
        "within_condition_held_out_interval_95": [
          0.6553517606446033,
          0.9333699301483963
        ]
      },
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "no",
      "within_r": 0.7740006547148806,
      "worst_case_bound_j": 1.0232899505603228
    }
  },
  {
    "label": "default nvml_100ms_25ms",
    "data": {
      "apparent": [
        -0.001115443389494129,
        0.05854830610006447
      ],
      "bound": 0.00009729590068353058,
      "ci": [
        0.29076507775888405,
        0.8332611577713871
      ],
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.43832762070182724,
      "increment": {
        "flags": [],
        "held_out_effective_n": 21,
        "held_out_episodes": 24,
        "verdict": "no",
        "within_condition_held_out_correlation": -0.5886004907339206,
        "within_condition_held_out_interval_95": [
          -0.8135700110924684,
          -0.21035765763800887
        ]
      },
      "mean_power": {
        "flags": [
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": 0.6736148880248951,
        "within_condition_held_out_interval_95": [
          0.35195791312058256,
          0.8529787790146469
        ]
      },
      "phase_err_sd_J": 1.6344200800256645,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8438154771382044,
        "within_condition_held_out_interval_95": [
          0.6553517606446033,
          0.9333699301483963
        ]
      },
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "no",
      "within_r": 0.6345858161086284,
      "worst_case_bound_j": 0.02839947686945834
    }
  },
  {
    "label": "default_blind ina3221",
    "data": {
      "apparent": [
        0,
        0
      ],
      "bound": 0.0011086205166570683,
      "ci": null,
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.0770312679988224,
      "increment": {
        "flags": [
          "constant_power_increment_feature",
          "undefined_power_increment_correlation"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "mean_power": {
        "flags": [
          "constant_training_power_feature",
          "undefined_observed_correlation",
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "phase_err_sd_J": 11.158883730059388,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8438154771382044,
        "within_condition_held_out_interval_95": [
          0.6553517606446033,
          0.9333699301483963
        ]
      },
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": null,
      "worst_case_bound_j": 1.0232899505603228
    }
  },
  {
    "label": "default_blind nvml_100ms_25ms",
    "data": {
      "apparent": [
        0,
        0
      ],
      "bound": 0.00009729590068353058,
      "ci": null,
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.0770312679988224,
      "increment": {
        "flags": [
          "constant_power_increment_feature",
          "undefined_power_increment_correlation"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "mean_power": {
        "flags": [
          "constant_training_power_feature",
          "undefined_observed_correlation",
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 0,
        "held_out_episodes": 0,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": null,
        "within_condition_held_out_interval_95": null
      },
      "phase_err_sd_J": 11.158883730059388,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8438154771382044,
        "within_condition_held_out_interval_95": [
          0.6553517606446033,
          0.9333699301483963
        ]
      },
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "inconclusive at this cohort size",
      "within_r": null,
      "worst_case_bound_j": 0.02839947686945834
    }
  },
  {
    "label": "p2 q",
    "data": {
      "apparent": [
        0.002272316637171021,
        0.05334247548443969
      ],
      "bound": 0.0009114822446086623,
      "ci": [
        0.611758967778493,
        0.8084904919807115
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.7291350447390186,
      "increment": {
        "flags": [],
        "held_out_effective_n": 93,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8938423135247563,
        "within_condition_held_out_interval_95": [
          0.8437692437918409,
          0.9284890626614218
        ]
      },
      "mean_power": {
        "flags": [
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": 0.7235703428110349,
        "within_condition_held_out_interval_95": [
          0.6104476360084228,
          0.8077643915236326
        ]
      },
      "phase_err_sd_J": 0.3979013764714221,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "no",
        "within_condition_held_out_correlation": -0.010303124188217116,
        "within_condition_held_out_interval_95": [
          -0.21248013030776805,
          0.19271978742984244
        ]
      },
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "yes",
      "within_r": 0.7245660029010135,
      "worst_case_bound_j": 0.6917183744201088
    }
  },
  {
    "label": "p2 fine",
    "data": {
      "apparent": [
        0.002271042140340114,
        0.05334264081385203
      ],
      "bound": 2.529646549202549e-11,
      "ci": [
        0.6117281652871647,
        0.8084734431306272
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.7293773753792719,
      "increment": {
        "flags": [],
        "held_out_effective_n": 93,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8938542030020322,
        "within_condition_held_out_interval_95": [
          0.8437862787820146,
          0.928497218267882
        ]
      },
      "mean_power": {
        "flags": [
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": 0.7235435867348866,
        "within_condition_held_out_interval_95": [
          0.6104124055358314,
          0.8077448757175925
        ]
      },
      "phase_err_sd_J": 0.39733896561676096,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "no",
        "within_condition_held_out_correlation": -0.010303124188217116,
        "within_condition_held_out_interval_95": [
          -0.21248013030776805,
          0.19271978742984244
        ]
      },
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "yes",
      "within_r": 0.7245426207698503,
      "worst_case_bound_j": 1.9197334991677085e-8
    }
  },
  {
    "label": "p2 rounding",
    "data": {
      "condition_difference_j": 0.00097816833854091,
      "max_abs_j": 0.010848884880678922,
      "sd_j": 0.004324237908642516
    }
  },
  {
    "label": "p3 contiguous_6.6ms",
    "data": {
      "apparent": [
        0.0024222549777566885,
        0.05298272846853936
      ],
      "bound": 0.0009114822446086623,
      "ci": [
        0.7276193778957244,
        0.8703636017948386
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.8109358181564447,
      "increment": {
        "flags": [],
        "held_out_effective_n": 93,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.9270878135830587,
        "within_condition_held_out_interval_95": [
          0.891800255448484,
          0.9511640036403203
        ]
      },
      "mean_power": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8083738802855257,
        "within_condition_held_out_interval_95": [
          0.7244060763277498,
          0.8687062918438864
        ]
      },
      "phase_err_sd_J": 0.1713564423832338,
      "recovery_meets": true,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "no",
        "within_condition_held_out_correlation": -0.010303124188217116,
        "within_condition_held_out_interval_95": [
          -0.21248013030776805,
          0.19271978742984244
        ]
      },
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "yes",
      "within_r": 0.8107156206127827,
      "worst_case_bound_j": 0.6917183744201088
    }
  },
  {
    "label": "p3 shunt_slice_1.1ms",
    "data": {
      "apparent": [
        0.002272316637171021,
        0.05334247548443969
      ],
      "bound": 0.0009114822446086623,
      "ci": [
        0.611758967778493,
        0.8084904919807115
      ],
      "contrast": 0.5982422458787154,
      "episodes": 96,
      "forecast_r": 0.7291350447390186,
      "increment": {
        "flags": [],
        "held_out_effective_n": 93,
        "held_out_episodes": 96,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8938423135247563,
        "within_condition_held_out_interval_95": [
          0.8437692437918409,
          0.9284890626614218
        ]
      },
      "mean_power": {
        "flags": [
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": 0.7235703428110349,
        "within_condition_held_out_interval_95": [
          0.6104476360084228,
          0.8077643915236326
        ]
      },
      "phase_err_sd_J": 0.3979013764714221,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 96,
        "held_out_episodes": 96,
        "verdict": "no",
        "within_condition_held_out_correlation": -0.010303124188217116,
        "within_condition_held_out_interval_95": [
          -0.21248013030776805,
          0.19271978742984244
        ]
      },
      "true": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "yes",
      "within_r": 0.7245660029010135,
      "worst_case_bound_j": 0.6917183744201088
    }
  },
  {
    "label": "p4 ina3221",
    "data": {
      "change_j_per_token": -0.000001355000000001494,
      "dropped": {
        "coverage_fraction": 0.9993467110604671,
        "decode_seconds_per_token": 0.0597936037734375,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.00006312827100861793,
        "energy_per_decode_token_j": 0.050664452419288276,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "dithered_rounding_uncertainty",
          "spectrum_includes_acquisition_transfer_function"
        ],
        "mean_decode_power_w": 12.847876183794083,
        "token_energy_variance_j2": 0.00022266500212545843,
        "token_rate_amplitude_w": 0.8598610329956956,
        "token_rate_hz": 16.7241968520425
      },
      "full": {
        "coverage_fraction": 1,
        "decode_seconds_per_token": 0.0597936037734375,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.00006314891206353711,
        "energy_per_decode_token_j": 0.05066580741928828,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "duty_cycled_apparent_energy",
          "dithered_rounding_uncertainty",
          "spectrum_includes_acquisition_transfer_function"
        ],
        "mean_decode_power_w": 12.847344936947852,
        "token_energy_variance_j2": 0.00022273011818427197,
        "token_rate_amplitude_w": 0.8591568043131121,
        "token_rate_hz": 16.7241968520425
      },
      "samples": 2492,
      "without_reference": {
        "coverage_fraction": 0.9993467110604671,
        "decode_seconds_per_token": 0.0597936037734375,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.00006312827100861793,
        "energy_per_decode_token_j": 0.050664452419288276,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "dithered_rounding_uncertainty",
          "spectrum_includes_acquisition_transfer_function"
        ],
        "mean_decode_power_w": 12.847876183794083,
        "token_energy_variance_j2": 0.00022266500212545843,
        "token_rate_amplitude_w": 0.8598610329956956,
        "token_rate_hz": 16.7241968520425
      }
    }
  },
  {
    "label": "p4 reference",
    "data": {
      "flags": [
        "synthetic_episode",
        "variable_decode_step_timing",
        "blocking_decode_upload_stalls",
        "constant_running_power_during_stall",
        "compute_only_schedule_retimed",
        "prefill_batch_boundaries_unavailable",
        "prefill_upstream_batch_cache_policy",
        "prefill_batch_union_profile_assumption",
        "serialized_token_start_transfer_profile",
        "prefill_cache_bypassed",
        "prefill_readonly_cache_reuse_unmodelled",
        "sensor_duty_gaps",
        "synthetic_power_trace",
        "duty_cycled_apparent_energy",
        "reference_decode_duration_ignored",
        "dithered_rounding_uncertainty",
        "spectrum_includes_acquisition_transfer_function"
      ]
    }
  },
  {
    "label": "p4 nvml_100ms_25ms",
    "data": {
      "change_j_per_token": -0.0002519531250000026,
      "dropped": {
        "coverage_fraction": 0.9934671106046709,
        "decode_seconds_per_token": 0.0597936037734375,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.004808232226783042,
        "energy_per_decode_token_j": 0.04671195708756252,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "dithered_rounding_uncertainty",
          "token_rate_at_or_above_nyquist",
          "per_token_energy_underresolved"
        ],
        "mean_decode_power_w": 12.78635714996249,
        "token_energy_variance_j2": 0.00498414621561689,
        "token_rate_amplitude_w": null,
        "token_rate_hz": 16.7241968520425
      },
      "full": {
        "coverage_fraction": 1,
        "decode_seconds_per_token": 0.0597936037734375,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.004824073491357244,
        "energy_per_decode_token_j": 0.04696391021256252,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "duty_cycled_apparent_energy",
          "dithered_rounding_uncertainty",
          "token_rate_at_or_above_nyquist",
          "per_token_energy_underresolved"
        ],
        "mean_decode_power_w": 12.785433679336546,
        "token_energy_variance_j2": 0.004979605078914651,
        "token_rate_amplitude_w": null,
        "token_rate_hz": 16.7241968520425
      },
      "samples": 251,
      "without_reference": {
        "coverage_fraction": 0.9934671106046709,
        "decode_seconds_per_token": 0.0597936037734375,
        "decode_tokens": 256,
        "energy_half_width_per_token_j": 0.004808232226783042,
        "energy_per_decode_token_j": 0.04671195708756252,
        "episode_id": "stageb-task-0-sabotage",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "dithered_rounding_uncertainty",
          "token_rate_at_or_above_nyquist",
          "per_token_energy_underresolved"
        ],
        "mean_decode_power_w": 12.78635714996249,
        "token_energy_variance_j2": 0.00498414621561689,
        "token_rate_amplitude_w": null,
        "token_rate_hz": 16.7241968520425
      }
    }
  },
  {
    "label": "p4 reference",
    "data": {
      "flags": [
        "synthetic_episode",
        "variable_decode_step_timing",
        "blocking_decode_upload_stalls",
        "constant_running_power_during_stall",
        "compute_only_schedule_retimed",
        "prefill_batch_boundaries_unavailable",
        "prefill_upstream_batch_cache_policy",
        "prefill_batch_union_profile_assumption",
        "serialized_token_start_transfer_profile",
        "prefill_cache_bypassed",
        "prefill_readonly_cache_reuse_unmodelled",
        "sensor_duty_gaps",
        "synthetic_power_trace",
        "duty_cycled_apparent_energy",
        "reference_decode_duration_ignored",
        "dithered_rounding_uncertainty",
        "token_rate_at_or_above_nyquist",
        "per_token_energy_underresolved"
      ]
    }
  },
  {
    "label": "p4 flags",
    "data": {
      "bad_resident": [
        "invalid_resident_expert"
      ],
      "duplicate": [
        "transfer_only_time_axis",
        "serialized_token_start_transfer_profile",
        "duplicate_expert_ids"
      ]
    }
  },
  {
    "label": "p5 stalls",
    "data": {
      "apparent": [
        0.0027584071277335217,
        0.05281015158707227
      ],
      "bound": 0.0011086205166570683,
      "ci": [
        0.5230848677653802,
        0.901446802677942
      ],
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.8165087557801681,
      "increment": {
        "flags": [],
        "held_out_effective_n": 21,
        "held_out_episodes": 24,
        "verdict": "no",
        "within_condition_held_out_correlation": 0.17342777046824073,
        "within_condition_held_out_interval_95": [
          -0.2791664593294462,
          0.5629729796510822
        ]
      },
      "mean_power": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8479268386238027,
        "within_condition_held_out_interval_95": [
          0.6635188382529319,
          0.9352067244694103
        ]
      },
      "phase_err_sd_J": 0.2823146132068166,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8438154771382044,
        "within_condition_held_out_interval_95": [
          0.6553517606446033,
          0.9333699301483963
        ]
      },
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "no",
      "within_r": 0.7740014099210382,
      "worst_case_bound_j": 1.0232899505603228
    }
  },
  {
    "label": "p5 dropped_episode",
    "data": {
      "episode_id": "stageb-task-0-benign",
      "features": {
        "coverage_fraction": 0.9996243028128502,
        "decode_seconds_per_token": 0.0519866814765625,
        "decode_tokens": 512,
        "energy_half_width_per_token_j": 0.000041631571557083775,
        "energy_per_decode_token_j": 0.009750032454274273,
        "episode_id": "stageb-task-0-benign",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "blocking_decode_upload_stalls",
          "constant_running_power_during_stall",
          "compute_only_schedule_retimed",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "dithered_rounding_uncertainty",
          "spectrum_includes_acquisition_transfer_function"
        ],
        "mean_decode_power_w": 12.187619148091954,
        "token_energy_variance_j2": 0.00023975498485812123,
        "token_rate_amplitude_w": 0.17498982799784016,
        "token_rate_hz": 19.235695982072574
      },
      "flags": [
        "synthetic_episode",
        "variable_decode_step_timing",
        "blocking_decode_upload_stalls",
        "constant_running_power_during_stall",
        "compute_only_schedule_retimed",
        "prefill_batch_boundaries_unavailable",
        "prefill_upstream_batch_cache_policy",
        "prefill_batch_union_profile_assumption",
        "serialized_token_start_transfer_profile",
        "prefill_cache_bypassed",
        "prefill_readonly_cache_reuse_unmodelled",
        "sensor_duty_gaps",
        "synthetic_power_trace",
        "irregular_sample_cadence",
        "duty_cycled_apparent_energy",
        "incomplete_decode_coverage",
        "dithered_rounding_uncertainty",
        "spectrum_includes_acquisition_transfer_function"
      ]
    }
  },
  {
    "label": "p5 default_drop_change",
    "data": {
      "change_j_per_token": 2.6250000000060947e-8,
      "dropped_j_per_token": 0.009750032454274273,
      "full_j_per_token": 0.009750006204274273
    }
  },
  {
    "label": "p5 no-stalls",
    "data": {
      "apparent": [
        0.003045773153486021,
        0.053131074082086026
      ],
      "bound": 0.0010525972690221938,
      "ci": [
        0.3816110664807926,
        0.8620455405219152
      ],
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.7841676030012349,
      "increment": {
        "flags": [],
        "held_out_effective_n": 21,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.9596333732125151,
        "within_condition_held_out_interval_95": [
          0.9013326708991012,
          0.9837791605007762
        ]
      },
      "mean_power": {
        "flags": [
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": 0.6906719367623417,
        "within_condition_held_out_interval_95": [
          0.37959349128425857,
          0.8614382433473007
        ]
      },
      "phase_err_sd_J": 0.41687177928493097,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [
          "held_out_recovery_inconclusive_at_cohort_size"
        ],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "inconclusive at this cohort size",
        "within_condition_held_out_correlation": 0.47585170050420866,
        "within_condition_held_out_interval_95": [
          0.06784869432119592,
          0.747498967265982
        ]
      },
      "true": [
        0.00304238592,
        0.05278224384
      ],
      "verdict": "yes",
      "within_r": 0.6919038002129244,
      "worst_case_bound_j": 0.9224808593080986
    }
  },
  {
    "label": "p5 dropped_episode",
    "data": {
      "episode_id": "stageb-task-0-benign",
      "features": {
        "coverage_fraction": 0.9996097805899696,
        "decode_seconds_per_token": 0.0500519694765625,
        "decode_tokens": 512,
        "energy_half_width_per_token_j": 0.000040848372712468824,
        "energy_per_decode_token_j": 0.00867615008279152,
        "episode_id": "stageb-task-0-benign",
        "flags": [
          "synthetic_episode",
          "variable_decode_step_timing",
          "prefill_batch_boundaries_unavailable",
          "prefill_upstream_batch_cache_policy",
          "prefill_batch_union_profile_assumption",
          "serialized_token_start_transfer_profile",
          "prefill_cache_bypassed",
          "prefill_readonly_cache_reuse_unmodelled",
          "sensor_duty_gaps",
          "synthetic_power_trace",
          "irregular_sample_cadence",
          "duty_cycled_apparent_energy",
          "incomplete_decode_coverage",
          "dithered_rounding_uncertainty",
          "spectrum_includes_acquisition_transfer_function"
        ],
        "mean_decode_power_w": 12.173410499074684,
        "token_energy_variance_j2": 0.00022731527898793815,
        "token_rate_amplitude_w": 0.15274491691252376,
        "token_rate_hz": 19.979233793552584
      },
      "flags": [
        "synthetic_episode",
        "variable_decode_step_timing",
        "prefill_batch_boundaries_unavailable",
        "prefill_upstream_batch_cache_policy",
        "prefill_batch_union_profile_assumption",
        "serialized_token_start_transfer_profile",
        "prefill_cache_bypassed",
        "prefill_readonly_cache_reuse_unmodelled",
        "sensor_duty_gaps",
        "synthetic_power_trace",
        "irregular_sample_cadence",
        "duty_cycled_apparent_energy",
        "incomplete_decode_coverage",
        "dithered_rounding_uncertainty",
        "spectrum_includes_acquisition_transfer_function"
      ]
    }
  },
  {
    "label": "p10 legacy_noise_seed ina3221",
    "data": {
      "apparent": [
        0.0026808824290117726,
        0.05281653112874765
      ],
      "bound": 0.0011086205166570683,
      "ci": [
        0.5311575366964828,
        0.9035206867800984
      ],
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.8166973732785391,
      "increment": {
        "flags": [],
        "held_out_effective_n": 21,
        "held_out_episodes": 24,
        "verdict": "no",
        "within_condition_held_out_correlation": 0.13403185926456668,
        "within_condition_held_out_interval_95": [
          -0.315942482743387,
          0.5347826436338446
        ]
      },
      "mean_power": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8510559223219214,
        "within_condition_held_out_interval_95": [
          0.6697642486097328,
          0.9366015351799866
        ]
      },
      "phase_err_sd_J": 0.2813990239517388,
      "recovery_meets": null,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8438154771382044,
        "within_condition_held_out_interval_95": [
          0.6553517606446033,
          0.9333699301483963
        ]
      },
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "no",
      "within_r": 0.77844467529509,
      "worst_case_bound_j": 1.0232899505603228
    }
  },
  {
    "label": "p10 legacy_noise_seed nvml_100ms_25ms",
    "data": {
      "apparent": [
        0.0015384068183945433,
        0.05326329968906447
      ],
      "bound": 0.00009729590068353058,
      "ci": [
        -0.2899089614371101,
        0.5376490190826543
      ],
      "contrast": 0.8631576590651903,
      "episodes": 24,
      "forecast_r": 0.43832762070182724,
      "increment": {
        "flags": [],
        "held_out_effective_n": 21,
        "held_out_episodes": 24,
        "verdict": "no",
        "within_condition_held_out_correlation": -0.04329725523392728,
        "within_condition_held_out_interval_95": [
          -0.4662757116124196,
          0.395794282196503
        ]
      },
      "mean_power": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "no",
        "within_condition_held_out_correlation": 0.14666166455732987,
        "within_condition_held_out_interval_95": [
          -0.29307586132869246,
          0.5351839184135365
        ]
      },
      "phase_err_sd_J": 1.4877634899422347,
      "recovery_meets": false,
      "required_r": 0.6471202066782847,
      "status": "ok",
      "timing": {
        "flags": [],
        "held_out_effective_n": 24,
        "held_out_episodes": 24,
        "verdict": "yes",
        "within_condition_held_out_correlation": 0.8438154771382044,
        "within_condition_held_out_interval_95": [
          0.6553517606446033,
          0.9333699301483963
        ]
      },
      "true": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "no",
      "within_r": 0.15004646401054125,
      "worst_case_bound_j": 0.02839947686945834
    }
  },
  {
    "label": "elapsed",
    "data": {
      "seconds": 287.618557817
    }
  }
]
```

### Final enlarged E2E and default CLI evidence

The main E2E cases additionally cover resident and synchronized controls. The
CLI includes every energy/variance/spectrum/timing/mean-power recovery and
interval, with the chosen increment printed beside them. Forecast agreement
is fitted on these same episodes and is never an independent check.

```json
{
  "e2e": [
    {
      "apparent_extra_j_per_token": [
        0.0018100693076293552,
        0.05323122222085053
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.0009602049996847113,
      "contrast_j": 0.5982422458787154,
      "decode_tokens_per_episode": 384,
      "episodes": 96,
      "forecast_r": 0.7868317148173697,
      "increment_ci": [
        -0.16624431709872659,
        0.24059214797596737
      ],
      "increment_r": 0.03878094817615853,
      "interval_ns": 10000000,
      "model_forecast_detection": true,
      "n_eff": 94,
      "phase_sweep_error_std_j": 0.2514318404779241,
      "required_r": 0.6471202066782847,
      "resident": false,
      "samples": 342862,
      "sensor": "ina3221",
      "timing_r": 0.8213906829904342,
      "true_extra_j_per_token": [
        0.00940750848,
        0.17660279808
      ],
      "verdict": "no",
      "window_ns": 1100000,
      "within_condition_held_out_r": 0.7847682385203254,
      "within_condition_interval_95": [
        0.6922172578618175,
        0.8519241883004665
      ],
      "world": "variable timing + stalls"
    },
    {
      "apparent_extra_j_per_token": [
        0.002272316637171021,
        0.05334247548443969
      ],
      "conditional_detection": true,
      "contrast_bound_j": 0.0009114822446086623,
      "contrast_j": 0.5982422458787154,
      "decode_tokens_per_episode": 384,
      "episodes": 96,
      "forecast_r": 0.7291350447390186,
      "increment_ci": [
        0.8437692437918409,
        0.9284890626614218
      ],
      "increment_r": 0.8938423135247563,
      "interval_ns": 10000000,
      "model_forecast_detection": true,
      "n_eff": 94,
      "phase_sweep_error_std_j": 0.3979013764714221,
      "required_r": 0.6471202066782847,
      "resident": false,
      "samples": 322624,
      "sensor": "ina3221",
      "timing_r": -0.010303124188217116,
      "true_extra_j_per_token": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "yes",
      "window_ns": 1100000,
      "within_condition_held_out_r": 0.7245660029010135,
      "within_condition_interval_95": [
        0.611758967778493,
        0.8084904919807115
      ],
      "world": "variable timing"
    },
    {
      "apparent_extra_j_per_token": [
        -0.00024306621700481145,
        0.00004826684806935423
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.0009114822446086623,
      "contrast_j": 0,
      "decode_tokens_per_episode": 384,
      "episodes": 96,
      "forecast_r": 0,
      "increment_ci": [
        -0.2639854534893615,
        0.1418535543369694
      ],
      "increment_r": -0.06369908635704787,
      "interval_ns": 10000000,
      "model_forecast_detection": false,
      "n_eff": 94,
      "phase_sweep_error_std_j": 0.023420397160116152,
      "required_r": 0.6471202066782847,
      "resident": true,
      "samples": 322624,
      "sensor": "ina3221",
      "timing_r": -0.010303124188217116,
      "true_extra_j_per_token": [
        0,
        0
      ],
      "verdict": "no",
      "window_ns": 1100000,
      "within_condition_held_out_r": -0.12887496770191031,
      "within_condition_interval_95": [
        -0.32305958767407406,
        0.07572294954090107
      ],
      "world": "variable timing"
    },
    {
      "apparent_extra_j_per_token": [
        -0.006266718386585925,
        0.10127244643353649
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.0000799944477066525,
      "contrast_j": 0.5982422458787154,
      "decode_tokens_per_episode": 384,
      "episodes": 96,
      "forecast_r": 0.09225533631484562,
      "increment_ci": [
        -0.002510872103624055,
        0.38906128288021297
      ],
      "increment_r": 0.20130400551357638,
      "interval_ns": 100000000,
      "model_forecast_detection": false,
      "n_eff": 94,
      "phase_sweep_error_std_j": 6.444814550829642,
      "required_r": 0.6471202066782847,
      "resident": false,
      "samples": 32342,
      "sensor": "nvml_100ms_25ms",
      "timing_r": -0.010303124188217116,
      "true_extra_j_per_token": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "no",
      "window_ns": 25000000,
      "within_condition_held_out_r": 0.1204111321940513,
      "within_condition_interval_95": [
        -0.08426533948028601,
        0.3153381677919225
      ],
      "world": "variable timing"
    },
    {
      "apparent_extra_j_per_token": [
        -0.00010984461328331275,
        0.06908736215874102
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.0009115455092094964,
      "contrast_j": 0.5982422458787154,
      "decode_tokens_per_episode": 384,
      "episodes": 96,
      "forecast_r": 0.18717864223339423,
      "increment_ci": [
        -0.23539126894257953,
        0.17160014601796592
      ],
      "increment_r": -0.03327495820373523,
      "interval_ns": 10000000,
      "model_forecast_detection": false,
      "n_eff": 94,
      "phase_sweep_error_std_j": 3.114516000188875,
      "required_r": 0.6471202066782847,
      "resident": false,
      "samples": 322656,
      "sensor": "ina3221",
      "timing_r": null,
      "true_extra_j_per_token": [
        0.00281346048,
        0.05281579008
      ],
      "verdict": "no",
      "window_ns": 1100000,
      "within_condition_held_out_r": -0.04025951315215988,
      "within_condition_interval_95": [
        -0.24091485778265323,
        0.16369640990358336
      ],
      "world": "synchronized bursts"
    }
  ],
  "default_cli": [
    {
      "apparent_extra_j_per_token": [
        0.0027584071277335217,
        0.05281015158707227
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.0011086205166570683,
      "contrast_j": 0.8631576590651903,
      "decode_duration_s": [
        25.856373476,
        30.914227554
      ],
      "episodes": 24,
      "forecast_r": 0.8165087416167143,
      "increment_ci": [
        -0.2791638835042857,
        0.5629748878035307
      ],
      "increment_r": 0.1734304799794651,
      "interval_ns": 10000000,
      "model_forecast_detection": true,
      "n_eff": 22,
      "nominal_decode_duration_s": null,
      "phase_sweep_error_std_j": 0.28231468187151165,
      "raw_held_out": {
        "decode_seconds_per_token": {
          "interval_95": [
            0.9943819688263544,
            0.9989823896833857
          ],
          "r": 0.9976078720241663
        },
        "energy_per_decode_token_j": {
          "interval_95": [
            0.992414058661466,
            0.9986248252564206
          ],
          "r": 0.9967681151452294
        },
        "mean_decode_power_w": {
          "interval_95": [
            0.9945820455099386,
            0.9990187107664488
          ],
          "r": 0.9976931965003263
        },
        "token_energy_variance_j2": {
          "interval_95": [
            -0.1368954223044181,
            0.6154539120258312
          ],
          "r": 0.2820857914617048
        },
        "token_rate_amplitude_w": {
          "interval_95": [
            0.360275095250203,
            0.8433364877760778
          ],
          "r": 0.6667722654674202
        }
      },
      "required_r": 0.6471202066782847,
      "resident": false,
      "samples": 114259,
      "sensor": "ina3221",
      "transfer_only_j_per_token": [
        0.00304238592,
        0.05278224384
      ],
      "true_extra_j_per_token": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "no",
      "window_ns": 1100000,
      "within_condition_interval_95": {
        "decode_seconds_per_token": [
          0.6553517606446033,
          0.9333699301483963
        ],
        "energy_per_decode_token_j": [
          0.5230834994984437,
          0.9014464496892164
        ],
        "mean_decode_power_w": [
          0.6633335569803914,
          0.9351652157432788
        ],
        "token_energy_variance_j2": [
          0.585168978991736,
          0.9169616657713987
        ],
        "token_rate_amplitude_w": [
          -0.38143894286501157,
          0.46020170271264166
        ]
      },
      "within_condition_r": {
        "decode_seconds_per_token": 0.8438154771382044,
        "energy_per_decode_token_j": 0.7740006547148806,
        "mean_decode_power_w": 0.8478338120759732,
        "token_energy_variance_j2": 0.8075488647977788,
        "token_rate_amplitude_w": 0.0478756886311657
      }
    },
    {
      "apparent_extra_j_per_token": [
        -0.000246092073863229,
        5.645516951471672e-7
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.0010525972690221938,
      "contrast_j": 0,
      "decode_duration_s": [
        25.548059603,
        25.654410814
      ],
      "episodes": 24,
      "forecast_r": 0,
      "increment_ci": [
        -0.4266963011340857,
        0.4366647107691784
      ],
      "increment_r": 0.006125763882418828,
      "interval_ns": 10000000,
      "model_forecast_detection": false,
      "n_eff": 22,
      "nominal_decode_duration_s": null,
      "phase_sweep_error_std_j": 0.03093924476022808,
      "raw_held_out": {
        "decode_seconds_per_token": {
          "interval_95": [
            -0.2606562260453995,
            0.5288892556214323
          ],
          "r": 0.15952058653078854
        },
        "energy_per_decode_token_j": {
          "interval_95": [
            -0.28342830337144503,
            0.5109453044414076
          ],
          "r": 0.13546330717084304
        },
        "mean_decode_power_w": {
          "interval_95": [
            -0.28268796601877944,
            0.511539770336325
          ],
          "r": 0.13625327337151083
        },
        "token_energy_variance_j2": {
          "interval_95": [
            0.018576256895744478,
            0.703396954626719
          ],
          "r": 0.4188408694130792
        },
        "token_rate_amplitude_w": {
          "interval_95": [
            -0.22131619649011441,
            0.5583100053396628
          ],
          "r": 0.19993744501731298
        }
      },
      "required_r": 0.6471202066782847,
      "resident": true,
      "samples": 107546,
      "sensor": "ina3221",
      "transfer_only_j_per_token": [
        0,
        0
      ],
      "true_extra_j_per_token": [
        0,
        0
      ],
      "verdict": "no",
      "window_ns": 1100000,
      "within_condition_interval_95": {
        "decode_seconds_per_token": [
          0.06784869432119592,
          0.747498967265982
        ],
        "energy_per_decode_token_j": [
          -0.6399834855631528,
          0.1402336481125445
        ],
        "mean_decode_power_w": [
          -0.6396169834311675,
          0.14084189321320292
        ],
        "token_energy_variance_j2": [
          -0.5099376561133768,
          0.3244960526022412
        ],
        "token_rate_amplitude_w": [
          -0.4775131869009861,
          0.36231809184316377
        ]
      },
      "within_condition_r": {
        "decode_seconds_per_token": 0.47585170050420866,
        "energy_per_decode_token_j": -0.29906362256283436,
        "mean_decode_power_w": -0.2984985142042681,
        "token_energy_variance_j2": -0.1125122710454576,
        "token_rate_amplitude_w": -0.06998851199468009
      }
    },
    {
      "apparent_extra_j_per_token": [
        -0.001115443389494129,
        0.05854830610006447
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.00009729590068353058,
      "contrast_j": 0.8631576590651903,
      "decode_duration_s": [
        25.856373476,
        30.914227554
      ],
      "episodes": 24,
      "forecast_r": 0.43832762070182724,
      "increment_ci": [
        -0.8135700110924684,
        -0.21035765763800887
      ],
      "increment_r": -0.5886004907339206,
      "interval_ns": 100000000,
      "model_forecast_detection": false,
      "n_eff": 22,
      "nominal_decode_duration_s": null,
      "phase_sweep_error_std_j": 1.6344200800256645,
      "raw_held_out": {
        "decode_seconds_per_token": {
          "interval_95": [
            0.9943819688263544,
            0.9989823896833857
          ],
          "r": 0.9976078720241663
        },
        "energy_per_decode_token_j": {
          "interval_95": [
            0.9732868575981087,
            0.9951190955190516
          ],
          "r": 0.9885561808791966
        },
        "mean_decode_power_w": {
          "interval_95": [
            0.9716461389049296,
            0.9948157879280854
          ],
          "r": 0.9878475269019805
        },
        "token_energy_variance_j2": {
          "interval_95": [
            0.9356274817694415,
            0.9880517819715711
          ],
          "r": 0.9721188826407583
        },
        "token_rate_amplitude_w": {
          "interval_95": null,
          "r": null
        }
      },
      "required_r": 0.6471202066782847,
      "resident": false,
      "samples": 11446,
      "sensor": "nvml_100ms_25ms",
      "transfer_only_j_per_token": [
        0.00304238592,
        0.05278224384
      ],
      "true_extra_j_per_token": [
        0.01017297792,
        0.17649062784
      ],
      "verdict": "no",
      "window_ns": 25000000,
      "within_condition_interval_95": {
        "decode_seconds_per_token": [
          0.6553517606446033,
          0.9333699301483963
        ],
        "energy_per_decode_token_j": [
          0.29076507775888405,
          0.8332611577713871
        ],
        "mean_decode_power_w": [
          0.35195791312058256,
          0.8529787790146469
        ],
        "token_energy_variance_j2": [
          -0.15434780908481388,
          0.6313864502855886
        ],
        "token_rate_amplitude_w": null
      },
      "within_condition_r": {
        "decode_seconds_per_token": 0.8438154771382044,
        "energy_per_decode_token_j": 0.6345858161086284,
        "mean_decode_power_w": 0.6736148880248951,
        "token_energy_variance_j2": 0.2858705700385963,
        "token_rate_amplitude_w": null
      }
    },
    {
      "apparent_extra_j_per_token": [
        -0.005458077447687488,
        0.005693036182566417
      ],
      "conditional_detection": false,
      "contrast_bound_j": 0.00009237913046689412,
      "contrast_j": 0,
      "decode_duration_s": [
        25.548059603,
        25.654410814
      ],
      "episodes": 24,
      "forecast_r": 0,
      "increment_ci": [
        -0.36327314001347183,
        0.49548289114755223
      ],
      "increment_r": 0.08114609838360143,
      "interval_ns": 100000000,
      "model_forecast_detection": false,
      "n_eff": 22,
      "nominal_decode_duration_s": null,
      "phase_sweep_error_std_j": 1.4323521011358258,
      "raw_held_out": {
        "decode_seconds_per_token": {
          "interval_95": [
            -0.2606562260453995,
            0.5288892556214323
          ],
          "r": 0.15952058653078854
        },
        "energy_per_decode_token_j": {
          "interval_95": [
            -0.07910801541118548,
            0.6504858529444615
          ],
          "r": 0.3349854764266539
        },
        "mean_decode_power_w": {
          "interval_95": [
            -0.07859192725435775,
            0.6507853291496519
          ],
          "r": 0.33544643783291844
        },
        "token_energy_variance_j2": {
          "interval_95": [
            -0.3032002380491858,
            0.4947829314912479
          ],
          "r": 0.11416704907568495
        },
        "token_rate_amplitude_w": {
          "interval_95": null,
          "r": null
        }
      },
      "required_r": 0.6471202066782847,
      "resident": true,
      "samples": 10771,
      "sensor": "nvml_100ms_25ms",
      "transfer_only_j_per_token": [
        0,
        0
      ],
      "true_extra_j_per_token": [
        0,
        0
      ],
      "verdict": "no",
      "window_ns": 25000000,
      "within_condition_interval_95": {
        "decode_seconds_per_token": [
          0.06784869432119592,
          0.747498967265982
        ],
        "energy_per_decode_token_j": [
          -0.12919760929886176,
          0.6465722345801956
        ],
        "mean_decode_power_w": [
          -0.12908889268613838,
          0.6466365700615198
        ],
        "token_energy_variance_j2": [
          -0.2694754963767281,
          0.5532213385045905
        ],
        "token_rate_amplitude_w": null
      },
      "within_condition_r": {
        "decode_seconds_per_token": 0.47585170050420866,
        "energy_per_decode_token_j": 0.30926374761666786,
        "mean_decode_power_w": 0.30936373027737335,
        "token_energy_variance_j2": 0.1716406981346448,
        "token_rate_amplitude_w": null
      }
    }
  ]
}
```

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

No shared contract was modified. Desired future companion timing record: token ordinal, turn, phase, start/end brackets, microbatch identity and clock domain. The current lane works around the missing RouterLog timing with explicit TokenWindow inputs and flags. This proposal is not installed and changes no data eligibility.

## OPEN ISSUES

- Hardware bandwidth/J-per-byte, deployed shunts/cadence/phase, noise, voltage
  skew, logger perturbation, supply events and Stage A effect require calibration.
  No hardware, inference server or paid service was used.
- Residualized recovery and mean-power recovery answer different questions.
  The chosen nuisance fits can remove timing-correlated error as well as signal;
  shared folds/paired conditions and fitted nuisance targets limit nominal Fisher
  coverage. Positive synthetic residual recovery is not established hardware
  design power. Use independent groups/repetitions before a physical claim.
- The numerical oracle's original independent-model provenance is retained.
  This seat maintained it and added the new projection comparison; that new work
  is not claimed as an independent different-model derivation. No helpers were
  started under this seat's delegation constraints. Independent executing review
  and the cold final pass remain lead gates.
- Exact upstream replay still needs cache group/slot/reset and microbatch timing
  inventory; large-batch read-only cache reuse remains flagged as unmodelled.
- No executor was available for literal local discovery or script execution.
  The authorized CI fallback executed every pass condition and all 42 alignment
  tests; this limitation is not presented as local execution.
- Final-head CI is pending and is not awaited per the brief. Earlier CI was
  superseded after focused MODULE PASS lines; no whole-suite green or merge-ready
  claim is made. PR #526 remains draft and unmerged. Gate-ledger still reports
  the uncompleted independent/merged-tree/final-head/cold-pass gates.

## NEEDS_RULING

**F1 prospective criterion:** current code adopts grouped timing-residual power
recovery, measuring the conditional increment. The permitted alternative is mean
observed decode power, measuring power-level routing visibility. They change a
printed verdict:

| World | Adopted increment / verdict | Mean-power alternative / verdict |
|---|---|---|
| E2E stalled INA | 0.03878094817615853 [-0.16624431709872659, 0.24059214797596737] / no | 0.844028133904538 [0.7737286721887902, 0.8937942788319294] / yes |
| Default stalled INA | 0.1734304799794651 [-0.2791638835042857, 0.5629748878035307] / no | 0.8478338120759732 [0.6633335569803914, 0.9351652157432788] / yes |
| E2E no-stall shunt INA | 0.8938423135247563 [0.8437692437918409, 0.9284890626614218] / yes | 0.7235703428110349 [0.6104476360084228, 0.8077643915236326] / inconclusive |
| E2E no-stall frame alternative | 0.9270878135830587 [0.891800255448484, 0.9511640036403203] / yes | 0.8083738802855257 [0.7244060763277498, 0.8687062918438864] / yes |

Recommendation: retain the adopted increment for the strict additional-to-timing
question, and retain mean-power visibility as a separate descriptive result.
The lead must predeclare the scientific estimand and validate the conditional
Stage A attenuation / nuisance-fitting uncertainty before registration. This
prospective question does not block implementation or exclude any episode.

F2 is determined by the brief's dithered simulation: q²/12 contrast SD
0.0009114822446086623J versus labelled q*T 0.6917183744201088J at contrast
0.5982422458787154J. The latter would fail a physical contrast test; it is not
the adopted verdict. No ruling is needed to restore that rejected assumption.
F4 follows the shunt sequence rather than departing from it; both alternatives
are printed above. F3 admits the same 24 episodes with coverage flags, as
explicitly directed; no new exclusion/eligibility choice is installed.
No compute-duration estimate remains.

## FIX ROUND 1

Implemented F1--F6, F8--F10 and STAGEB-S; F7 is left for the lead exactly as
directed. The original 34 tests remain, with assertions changed where the
review changes their feature, bound or acquisition world:

- Sensor cadence now checks the 1.1ms shunt slice rather than the 6.6ms frame.
- The old stalled energy-positive test now checks the timing/increment ledger;
  the separate blind-sensor regression enforces the required no-yes result.
- The old no-stall q*T rejection is replaced by dithered-rounding and
  shunt-model assertions. The synchronized-world negative interval/bar remains.
- The stall fixture compares observed baseline-subtracted .03J rather than
  adding .36J from truth. Its modeled physical .39J remains checked. The cooler
  fixture uses -.15J above actual running baseline; sparse features are finite
  with coverage flags rather than None.
- Forecast/oracle agreement now passes the explicit n=50 condition-mean count.
- The resident true-zero assertion uses float noise, with a separate apparent
  sensor-bound assertion.
- The review module adds the real p1--p5 paths, constant-sensor regression,
  one-sample cohort retention, 32/33 cache readouts, disjoint INA averages,
  pairwise projection oracle and legacy-noise ablation. All four tests passed.

No test was weakened to hide a failure: these are the feature, bound and world
corrections the brief requires. All lead-specified categorical pass conditions
executed successfully. Numerical bars retain their physical/precision derivations.

## HISTORY

r0 CI 39708988879 passed 29 Stage B tests. r0c CI 39716151868 passed 34 in
115.018s. The lead's ebba54833 review ran 38 alignment tests in 64.0s.
Those are provenance, not current-head validation. The old stalled-world yes
and no-stall q*T negative result are superseded by this round.

## FIX LOG

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
