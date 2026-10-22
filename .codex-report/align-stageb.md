# align-stageb lane report

## SUMMARY
Implemented a stdlib-only, parameterized MoE traffic model with pinned residency, LRU/SLRU and explicit prefill batch unions.
Added analytic power acquisition simulation for configurable INA3221 rails and the requested 100 ms / 25 ms NVML sensitivity case.
Added decode energy, variance and spectral features, grouped held-out routing recovery and conditional detectability planning.
Added multi-turn, tool-using synthetic worlds with all-resident controls and randomized acquisition phases.
Verified current llama.cpp offload/cache flags and routing callback seams at a pinned public source revision.
Documented memory budgets and operator procedures for Jetson Orin Nano Super and the RTX 3080 Ti box.
An independently authored numerical oracle checks traffic, acquisition, features, regression and planning.
Synthetic held-out recovery clears the fixed r=0.647120 requirement only for the contiguous INA control (r=0.725190); default acquisition worlds are negative.
The CI suite passed: 9,903 tests reported, 145 existing skips; all 29 Stage B tests passed without skips. No hardware result is claimed.

## FILES
- `joulewise/align/moe_stage_b/__init__.py`: public stdlib API exports.
- `joulewise/align/moe_stage_b/traffic.py`: expert block storage, timing adapter, cache simulation, traffic profiles, adjacent decode reuse.
- `joulewise/align/moe_stage_b/simulation.py`: sensor configuration, analytic acquisition and shared Episode/PowerTrace simulation.
- `joulewise/align/moe_stage_b/analysis.py`: features, grouped scalar recovery, normal-design correlation requirement and sensor forecast.
- `joulewise/align/moe_stage_b/experiment.py`: production-shaped worlds and JSON CLI.
- `joulewise/align/moe_stage_b/reference.py`: separately authored numerical oracle, using ordered lists, direct overlap integrals and pairwise statistics.
- `tests/align/test_moe_stage_b.py`: 29 focused tests, including real end-to-end production paths and oracle comparisons.
- `docs/align/moe_stage_b.md`: physical limits, sources, formulas, model fit and verified llama.cpp configuration/logging procedure.
- `.codex-report/align-stageb.md`: this handoff.
- `tests/test_shard_tests.py`: one-line discovery-inventory namespace normalization for newly discovered `align.*` modules. This is the only registry exception; it was necessary after the first repository CI run failed the inventory test. No timing weights or test coverage were changed.
- The three shared governing files were not modified. All other changed files are inside the lane's exhaustive WRITE_SCOPE.

## PUBLIC API
- `OffloadConfig(expert_bytes: Mapping[int, int], resident: frozenset[tuple[int, int]], cache_capacity_bytes: int, cache_policy: str, bandwidth_bytes_s: float, joules_per_byte: float, path: str, bandwidth_source: str, energy_source: str, prefill_mode: str = "bypass", prefill_batch_tokens: int = 1, flags: tuple[str, ...] = ())`
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
- `extract_features(episode: Episode, trace: PowerTrace, *, baseline_w: float, noise_std_w: float, noise_multiplier: float, attribution_floor_j: float, windows: Sequence[TokenWindow] | None = None) -> PowerFeatures`
- `pearson(x: Sequence[float], y: Sequence[float]) -> float | None`
- `recover_routing(observations: Sequence[RoutingObservation], *, feature_name: str) -> RoutingRecovery`
- `required_correlation(*, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int) -> CorrelationRequirement`
- `plan_detectability(sensor: SensorModel, *, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int, routing_stat_sd: float, traffic_energy_slope_j_per_token: float, decode_tokens: int, decode_duration_s: float, phase_bias_std_j: float, systematic_contrast_half_width_j: float) -> DetectionPlan`
- Experiment helpers: `synthetic_episode(config: WorldConfig, *, group: int, condition: str, hot_probability: float) -> Episode`; `world_offload(config: WorldConfig, *, all_resident: bool = False) -> OffloadConfig`; `default_sensors() -> tuple[SensorModel, ...]`; `run_world(config: WorldConfig, sensor: SensorModel, *, all_resident: bool, stage_a_effect_sd: float, n_per_condition: int, alpha: float, power: float, comparisons: int) -> dict[str, Any]`; `main() -> None`.
- Immutable output/config dataclasses are defined in the relevant modules. Reference helpers are test oracles; their strict input validation is not the production flags API.

## TESTS RUN
**PASS: [CI run 39708988879](https://github.com/mpmdw/JouleWise/actions/runs/39708988879), all 20 jobs, tested code SHA `1110fff802b0c0c4c9400f984a4f168d8c319ac1`.** The final handoff commit changes only this report and the runbook, not Python source. The whole discovered suite reported 9,903 tests, zero failures/errors and 145 existing skips: 9,835 ordinary tests plus 48 calibration-exit tests and 20 crash-matrix tests. Quick-tier/fence tests overlap that suite and are not added again.

| Ordinary shard | Tests reported | Skips | Failures / errors |
|---:|---:|---:|---:|
| 1 | 600 | 12 | 0 / 0 |
| 2 | 506 | 4 | 0 / 0 |
| 3 | 809 | 6 | 0 / 0 |
| 4 | 878 | 16 | 0 / 0 |
| 5 | 556 | 5 | 0 / 0 |
| 6 | 768 | 9 | 0 / 0 |
| 7 | 695 | 11 | 0 / 0 |
| 8 | 987 | 13 | 0 / 0 |
| 9 | 959 | 27 | 0 / 0 |
| 10 | 1136 | 25 | 0 / 0 |
| 11 | 1073 | 12 | 0 / 0 |
| 12 | 868 | 5 | 0 / 0 |
| Total | 9835 | 145 | 0 / 0 |

Focused results through CI's real unittest loader:
- `tests.align.test_moe_stage_b`: **29 tests, zero failures/errors/skips**, 29.591 s, ordinary shard 9.
- `tests.align.test_records`: **4 tests, zero failures/errors/skips**, ordinary shard 8.
- Thus both alignment modules' 33 tests executed cleanly; the literal alignment-discovery shell command remained unavailable locally.
- The independently implemented oracle actually executed in the 29-test module, not merely source inspection.

CI used the unchanged workflow at [the tested code revision](https://github.com/mpmdw/JouleWise/blob/1110fff802b0c0c4c9400f984a4f168d8c319ac1/.github/workflows/ci.yml).
Its exact ordinary-suite entry below ran with `SHARD_COUNT=12` and each `SHARD_INDEX=1..12` on Python 3.13; the two exclusive modules are deliberately absent from those partitions.

```bash
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

The exact crash-matrix entry below ran with `SHARD_INDEX=1` and `SHARD_INDEX=2`; it covers one declared heavy test and the 19-test remainder without skipping either.

```bash
python - <<'PY'
import os
import sys

sys.path.insert(0, "scripts")
import shard_tests

module = "tests.test_calibration_writer_crash_matrix"
timings = shard_tests.load_timing_map()
splits = shard_tests.load_split_declarations()
unknown = shard_tests.conservative_unknown_weight()
# expand_units runs verify_split_declaration, which fails closed if
# the declared heavy test id no longer exists. That is the case a
# computed remainder would otherwise absorb in silence, handing one
# shard ~20 minutes of unaccounted work while the weights disagree.
units, weights = shard_tests.expand_units(
    (module,), timings, {module: splits[module]}, unknown_weight=unknown
)
partitions = shard_tests.partition_modules(
    units, weights, 2, unknown_weight=unknown
)
totals = shard_tests.partition_totals(
    partitions, weights, unknown_weight=unknown
)
print("CRASH-MATRIX SHARD ESTIMATES", ",".join(f"{v:.3f}" for v in totals))
index = int(os.environ["SHARD_INDEX"])
raise SystemExit(shard_tests.run_units(partitions[index - 1], 2, index))
PY
```

Other executed commands:
- `python3 scripts/quick_suite.py --tier quick --workers 4`: 212 selected modules, 176 excluded by the existing quick-tier policy, zero failed modules. The two alignment modules were executed by ordinary shards, not this quick selection.
- `python -m unittest -v tests.test_calibration_exits`: 48 tests, zero failures/errors/skips.
- `python -m compileall -q joulewise tests`, and the exclusive-job variant adding `scripts/validate_powermetrics_fiducial.py`: passed.
- `python scripts/gen_state.py --check`; `python scripts/repin.py --check`; `python -m unittest -v tests.test_docs_freshness` (31 tests, zero skips); `python scripts/verify_receipt_histsem.py --repository-root . --require-published`: passed.
- `python -m joulewise validate-config configs/examples/mock_local.json`; `python -m joulewise validate-config configs/examples/mac_mlx_local.json`: passed.
- Strict mock chain: `python -m joulewise run configs/examples/mock_local.json --runs-dir ci-runs`, then `python -m joulewise validate-bundle --strict "$bundle"`, `python -m joulewise reduce "$bundle"`, and the same strict validation again; `bundle` was parsed from the run command's output by the unchanged CI workflow. Passed.
- `python -m build`: wheel and sdist built. Existing clean-venv `python -m pip install --no-deps "$wheel"` and outside-repo installed-wheel CLI/manifest smokes passed. These check the repository packaging, not a dedicated installed-layout Stage B experiment.
- The Stage B test executes the standalone CLI using `sys.executable -m joulewise.align.moe_stage_b.experiment`; the exact interpreter path and result count are recorded with the evidence below.

The 145 skips are pre-existing repository conditions, with zero lane skips. Counts below group the exact unittest reason strings from all ordinary-shard logs; they sum to the runner-reported 145. Full individual reasons remain in the linked CI job logs. Existing D-158/registration fixture blockers below are not new lane rulings.

| Existing skip reason (grouped) | Count |
|---|---:|
| macOS/Darwin/APFS facilities or live-acquisition opt-in unavailable on hosted Linux | 50 |
| Retained corpus/archive/ledger/inventory or custody path absent | 32 |
| Full scored corpus requires JOULEWISE_FULL_CORPUS opt-in | 13 |
| Optional matplotlib analysis extra absent | 9 |
| Local model/tokenizer mirrors absent or incomplete | 7 |
| Existing GAMMA registration lacks freeze authority | 6 |
| Optional jsonschema package absent | 5 |
| Lead-reviewed D-079 import/custody inputs unavailable | 3 |
| U2 successor engine pending | 3 |
| Existing family-publication/generator fixture is structurally blocked | 2 |
| Optional markdown-it-py documentation package absent | 2 |
| Required design branch absent from checkout | 2 |
| Production proof requires its dedicated branch/registered partition | 2 |
| lsof utility absent | 2 |
| POWER-Z USB instrument absent | 1 |
| Case-insensitive filesystem required | 1 |
| Pinned MATH source absent | 1 |
| Optional tokenizers package and local tokenizer fixture absent | 1 |
| Existing D-158 fixture cannot satisfy the production DATA-only gate | 1 |
| Successor member not minted | 1 |
| Known lock-reclaimer limitation when the temporary filesystem reuses an inode | 1 |
| Total | 145 |

The separate `gate-ledger` workflow is **not green**: [run 39708988953](https://github.com/mpmdw/JouleWise/actions/runs/39708988953) reports rows 1–4 still `NOT-RUN` (independent executing review, merged-tree gate, final-head CI evidence and cold final pass). The PR remains draft; passing `ci` is not a claim that all merge gates are satisfied.

Local execution limitation: the selected managed environment stayed `starting`, connectivity `offline`, with no usable shell. Two `pwd` calls failed before reaching Python. Consequently the literal local commands below were **not run**, and are not conflated with CI's module-equivalent execution:
- `python3 -m unittest discover -s tests/align -t .`
- `python3 -m unittest -v tests.align.test_moe_stage_b`
- `python3 -m unittest discover -s tests`
- `python3 scripts/quick_suite.py --tier touched --since 4d47c4362352ccd8d4d904134a79f0d8260b21b5`
- `python3 scripts/fixture_orphan_census.py --fail-on-orphans`

Extras: none imported, installed or required by this lane. CI installs the packaging frontend `build`, not project extras; it installs the wheel with `--no-deps`. No extra-dependent lane path exists, and all lane tests have zero skips.

Earlier failures and their disposition:
- CI run `39705799481`: repository discovery inventory failed because unittest named the new subpackage modules `align.*` while the shard inventory used `tests.align.*`. Fixed only the existing namespace-normalization condition in `tests/test_shard_tests.py`; preserved exact inventory equality.
- CI run `39706737827`, code `9eaf7683f31befbe4633f796326e532de5656d13`: 28 Stage B tests ran, one failed, zero errors/skips. The failed assertion expected gapped INA acquisition to clear the fixed recovery bar. Actual within-condition held-out r=-0.0053296434 was below 0.6471202067. Retained that world as a negative test, corrected the final verdict to require empirical recovery, and added a contiguous-acquisition positive control. No routing coefficients or comparison bar were weakened. Unfinished ordinary shards were cancelled; this was not a passing whole-suite run.

Independent numerical/source review: requested model `gpt-6-astra`, task `/root/independent_numeric_reference`; the runtime did not separately expose model identity. The reviewer authored the oracle before seeing the production implementation. It uses ordered lists, direct overlap integrals and pairwise statistics, independently checking traffic policies, batched prefill, acquisition, feature energy/variance/spectrum, OLS, correlations and the design forecast. Source findings fixed: preserve hit order, clock bounds over disjoint intervals, scaled Pearson, finite/count/tail validation, within-condition SD and held-out attenuation, white-noise double counting, and optimistic forecast substitution. Final source-only review of `1110fff802b0c0c4c9400f984a4f168d8c319ac1` found no blocking scientific defect. Its nonblocking naming observation was resolved in documentation: `forecast_empirical_disagreement` specifically reports an optimistic forecast that fails empirical recovery, not the reverse direction. The independent agent had no shell; this is source/oracle review, not an independently executing review.

## END-TO-END
The executed real-function chain is `synthetic_episode -> RouterLog -> model_traffic -> simulate_episode -> PowerTrace -> extract_features -> grouped recover_routing -> empirical/design comparison`.
The default CLI defines four cases (INA/NVML x offloaded/all-resident), each 12 task groups x 2 conditions = 24 episodes, four turns, 1024 prefill tokens, 512 decode tokens and four tool calls per episode. At 50 ms/token, decode lasts 25.6 s; 16 s prefill and 3.2 s tool gaps give 44.8 s per episode.
Architecture is OLMoE-shaped: 16 layers, 64 experts/layer, top-8, three 2048x1024 matrices/expert, Q4_0 blocks of 32 weights/18 bytes. One expert occupies exactly 3,538,944 bytes. The synthetic SLRU cache holds 256 experts (=864 MiB, by 256*3,538,944/2**20); prefill uses explicit 128-token microbatches. This is a scenario distinct from the operator's proposed 512 MiB trial, not a claim to duplicate its slot inventory.
The INA scenario derives a 6.6 ms conversion frame and 10 ms effective cadence with a 0.036032 W quantum from supplied 5 V / 2 A / 10 mOhm inputs. NVML uses 25 ms acquisition every 100 ms; the 20 Hz token-rate feature exceeds its 5 Hz Nyquist frequency. Both sensors sample the same Jetson-like power world to isolate acquisition response; this is not an 8 W RTX calibration.
The fixed statistical example supplies external Stage A d=1, 50 independent task groups/condition, alpha=.05, power=.8 and three comparisons. Its normal-design requirement is 0.6471202066782847. No synthetic condition effect is substituted for that external parameter. Actual cohorts have six or twelve task groups; their correlations are finite-cohort point estimates, not validation of 50-group design power.

The six-group/condition E2E cohort has three turns, 768 prefill and 384 decode tokens, three tool calls and 33.6 s per episode (19.2 s decode + 12 s prefill + 2.4 s tool gaps). All four cases use the same routes, transfer coefficients and design requirement. Only acquisition and residency change. The contiguous INA control passes; the original 10 ms polling case remains a negative result despite its optimistic forecast.

| Sensor | Placement | Window / cadence (ms) | Episodes | Samples | Within-condition held-out energy r | Analytic forecast | Empirical verdict |
|---|---|---:|---:|---:|---:|---|---|
| ina3221 | offloaded | 6.6 / 6.6 | 12 | 61104 | 0.725190209 | yes | yes |
| ina3221 | offloaded | 6.6 / 10 | 12 | 40332 | -0.005329643 | yes | no |
| ina3221 | resident | 6.6 / 10 | 12 | 40332 | -0.436755449 | no | no |
| nvml_100ms_25ms | offloaded | 25 / 100 | 12 | 4044 | 0.026436210 | no | no |

Default CLI, 12 groups/condition and four turns:

| Sensor | Placement | Window / cadence (ms) | Episodes | Samples | Within-condition held-out energy r | Analytic forecast | Empirical verdict |
|---|---|---:|---:|---:|---:|---|---|
| ina3221 | offloaded | 6.6 / 10 | 24 | 107544 | 0.503038807 | yes | no |
| ina3221 | resident | 6.6 / 10 | 24 | 107544 | -0.200977581 | no | no |
| nvml_100ms_25ms | offloaded | 25 / 100 | 24 | 10776 | 0.073315943 | no | no |
| nvml_100ms_25ms | resident | 25 / 100 | 24 | 10776 | 0.438995922 | no | no |

Observed default energy ranges and diagnostic correlations (full binary64 JSON values transcribed from the executed CLI; table correlations above are rounded to nine decimal places):

- ina3221, offloaded: true extra J/decode token [0.00304238592, 0.05278224384]; apparent extra [0.00006716147122602153, 0.054520428032297646]; phase/acquisition energy error SD 1.5562312138217516 J. Feature correlations: energy 0.5030388072288084; variance 0.026523649293922844; token-rate amplitude 0.4599657560309025.
- ina3221, resident: true extra J/decode token [0, 0]; apparent extra [-0.00016745262785222841, 0.00003070831907602196]; phase/acquisition energy error SD 0.024234793478783358 J. Feature correlations: energy -0.2009775806965525; variance 0.23580865421794833; token-rate amplitude 0.1465370115506436.
- nvml_100ms_25ms, offloaded: true extra J/decode token [0.00304238592, 0.05278224384]; apparent extra [-0.004901948977585925, 0.10123377333102346]; phase/acquisition energy error SD 15.163225432753432 J. Feature correlations: energy 0.07331594270722545; variance -0.02069141625382751; token-rate amplitude unavailable (Nyquist flag).
- nvml_100ms_25ms, resident: true extra J/decode token [0, 0]; apparent extra [-0.007815123451007797, 0.0037537432716132947]; phase/acquisition energy error SD 1.5230077229369028 J. Feature correlations: energy 0.4389959216840215; variance -0.04684527498374196; token-rate amplitude unavailable (Nyquist flag).

The contiguous INA E2E world's apparent extra J/token range was [0.003439042897198688, 0.05281341877279169], against true range [0.00346226688, 0.05281579008], with phase/acquisition energy error SD 0.011826540188551846 J. The same true traffic under gapped INA produced error SD 1.2027712942338027 J and under NVML 11.159842074822459 J. Resident controls have zero modelled bytes and zero true incremental traffic energy; noise/baseline reconstruction remains visible instead of being clipped to zero.

Standalone command actually executed: `/opt/hostedtoolcache/Python/3.13.16/x64/bin/python -m joulewise.align.moe_stage_b.experiment`. It returned finite `SYNTHETIC_ONLY` JSON for all four default cases, 96 episodes total. No network or model server was called.

Final Stage B verdict uses the predeclared energy feature's within-condition held-out r and the physical contrast bound. Variance/spectrum remain diagnostics. The separate linear/noise forecast omits routing-to-energy residual variation and can be optimistic; forecast optimism that fails empirical recovery remains a flag, never a reason to discard data. No synthetic number is a hardware result.

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
- Use the separately authored numerical oracle and source review required by PIPELINE/AGENTS. CI provides execution while the managed VM is offline; distinguish it from independent executing review and the literal unrun local commands.
- Predeclare energy as the final empirical recovery decision; retain variance and spectral diagnostics and the separate analytic forecast. Preserve negative gapped-acquisition results and use a physically changed acquisition setting for a positive control. Do not tune the statistical bar after observing a failure.
- Keep the PR to the spine as a draft for existing CI; no workflow changes, merge, force-push or main push. Report all evidence against its tested code SHA; the final report/documentation commit changes no Python source.

## CONTRACT-CHANGE
No shared contract file was modified. A future optional companion routing-timing record would avoid reconstructing token/turn/microbatch timing: token ordinal, turn index, actual executed phase, start/end brackets, microbatch identity and clock domain. The current lane works around the absence with explicit `TokenWindow` inputs and flags. This proposal is not installed and changes no data eligibility.

## OPEN ISSUES
- The managed environment never supplied a shell. Exact local discovery/touched-tier/census commands remain unrun; existing CI executed the discovered modules instead.
- Hardware J/B, effective bandwidth, INA rail configuration, RTX sensor cadence, logger perturbation and Stage A effect sizes require calibration. No hardware, model server or external inference service was accessed.
- Exact batched-prefill replay needs backend cache-group/slot/batch state; read-only cached-weight reuse is flagged as unmodelled. The timing adapter is flagged interpolation, not measured token timing.
- The linear forecast omits routing-to-energy residual variation. Empirical recovery governs the synthetic verdict; finite synthetic cohorts do not establish real detectability or registered design power.
- Draft PR #526 remains a CI/review vehicle. Its separate gate-ledger fails the honestly uncompleted review/merge/final-head/cold-pass rows; no independent executing review, cold Fable pass, all-checks-green or merge-ready claim is made. No merge was requested or performed.
- No network access, credentials, keys or personal email addresses were added to tests.

## NEEDS_RULING
none

## CONTINUATION r0c
Work resumed from `0fc746f6d36aecb61716e821ce6318f40ab02c1a` under the lead’s three findings. Initial checkpoint adds episode-counted 95% Fisher-z intervals to raw held-out recovery. Variable timing, stall physics, centered intervals, revised verdicts, new execution evidence and tables are in progress; the r0 numbers above are historical until replaced below.
