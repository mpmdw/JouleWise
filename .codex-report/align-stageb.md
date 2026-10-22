# align-stageb lane report

## SUMMARY
Continued the existing Stage B lane from the lead-pinned r0 head; shared contracts remain unchanged.
Default worlds now use explicit per-token step variation and blocking decode cache-upload stalls.
The exactly commensurate, jitter-free schedule remains a labelled synchronized-bursts worst case.
Pinned llama.cpp source establishes same-stream upload dependencies; stall energy adds platform running power once.
Raw and centered held-out correlations now carry approximate 95% Fisher intervals and episode/effective counts.
An interval containing the required r=0.6471202067 yields "inconclusive at this cohort size" with the required flag.
The analytic forecast now includes within-condition routing-to-energy residual variation.
Independent oracle checks and a fresh source/test audit cover intervals, timing, energy, sparse coverage and nanosecond rounding.
CI passed 9,908 tests with 145 existing skips; all 34 Stage B tests passed in 115.018 s; stalled INA clears both bars at r=.823237 [.744863,.879203] (N=96).
No hardware, inference service or paid API was used; PR #526 remains draft and unmerged.

## FILES
- `joulewise/align/moe_stage_b/__init__.py`: public stdlib API exports.
- `joulewise/align/moe_stage_b/traffic.py`: expert block storage, timing adapter, cache simulation, traffic profiles, blocking decode timing adapter, separate transfer/stall energy, exact-ns rounding, adjacent decode reuse.
- `joulewise/align/moe_stage_b/simulation.py`: sensor configuration, analytic acquisition and shared Episode/PowerTrace simulation.
- `joulewise/align/moe_stage_b/analysis.py`: features, grouped scalar recovery, normal-design correlation requirement and sensor forecast.
- `joulewise/align/moe_stage_b/experiment.py`: production-shaped variable-timing/stalled worlds and tri-state JSON CLI.
- `joulewise/align/moe_stage_b/reference.py`: separately authored numerical oracle, using ordered lists, direct overlap integrals and pairwise statistics.
- `tests/align/test_moe_stage_b.py`: 34 focused tests, including enlarged interval-separated worlds, synchronized bursts, real end-to-end paths and independent oracles.
- `docs/align/moe_stage_b.md`: physical limits, sources, formulas, model fit and verified llama.cpp configuration/logging procedure.
- `.codex-report/align-stageb.md`: this handoff.
- `tests/test_shard_tests.py`: one-line discovery-inventory namespace normalization for newly discovered `align.*` modules. This r0 change is the only registry exception; no registry file was changed during r0c. It was necessary after the first repository CI run failed the inventory test. No timing weights or test coverage were changed.
- The three shared governing files were not modified. All other changed files are inside the lane's exhaustive WRITE_SCOPE.

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
- `StallTiming(episode, windows, reference_decode_duration_ns, flags=())`; `SimulatedEpisode` additionally exposes actual `windows` and optional `reference_decode_duration_ns`.
- `TokenTraffic` additionally exposes `stall_energy_j`, integer `transfer_duration_ns`, and `incremental_energy_j`; `TrafficResult.total_incremental_energy_j` sums memory plus running-stall energy. Existing `energy_j` / `total_energy_j` remain transfer-only.
- `RoutingRecovery` additionally exposes `held_out_interval_95`, `held_out_episodes` and `held_out_effective_n`; centered counterparts and tri-state verdicts are serialized by `run_world`.
- Immutable output/config dataclasses are defined in the relevant modules. Reference helpers are test oracles; their strict input validation is not the production flags API.

## TESTS RUN
**PASS: [r0c CI run 39716151868](https://github.com/mpmdw/JouleWise/actions/runs/39716151868), all 20 jobs, tested code SHA `909ebae8c90e20a0d92a4b20106ea2219c58becb`.**
The discovered suite reported **9,908 tests, zero failures/errors and 145 existing skips**:
9,840 ordinary tests + 48 calibration-exit tests + 20 crash-matrix tests. Quick/fence
checks overlap this suite and are not added again.

| Ordinary shard | Tests | Skips | Failures / errors |
|---:|---:|---:|---:|
| 1 | 600 | 12 | 0 / 0 |
| 2 | 506 | 4 | 0 / 0 |
| 3 | 809 | 6 | 0 / 0 |
| 4 | 878 | 16 | 0 / 0 |
| 5 | 556 | 5 | 0 / 0 |
| 6 | 768 | 9 | 0 / 0 |
| 7 | 695 | 11 | 0 / 0 |
| 8 | 987 | 13 | 0 / 0 |
| 9 | 964 | 27 | 0 / 0 |
| 10 | 1136 | 25 | 0 / 0 |
| 11 | 1073 | 12 | 0 / 0 |
| 12 | 868 | 5 | 0 / 0 |
| Total | 9840 | 145 | 0 / 0 |

- `tests.align.test_moe_stage_b`: **34 tests, zero failures/errors/skips, 115.018 s**, shard 9.
- `tests.align.test_records`: **4 tests, zero failures/errors/skips, 0.009 s**, shard 8.
- Thus all **38 alignment tests** passed. Their summed module elapsed time is
  115.027 s, including the standalone CLI and 576 main synthetic episodes; it is
  not the wall time of the unrun local discovery command. The enlarged cohorts
  are sized by the requested Fisher-z margin, with no extra dependencies.
- Actual standalone command:
  `/opt/hostedtoolcache/Python/3.13.16/x64/bin/python -m joulewise.align.moe_stage_b.experiment`.
  Finite SYNTHETIC_ONLY JSON covered all four default cases; the test invoked
  this command through the real subprocess/module entry.
- `python3 scripts/quick_suite.py --tier quick --workers 4`: 212 modules selected,
  176 excluded by existing policy, zero failed modules, 131.874 s.
- The unchanged ordinary/crash-matrix command blocks reproduced below also ran
  in this current CI run, with the same SHARD_COUNT/SHARD_INDEX settings.
  The exact remaining workflow commands below (compileall, calibration exits,
  fences, strict mock chain, build and installed-wheel smokes) also passed.
  Workflow source: [current tested revision](https://github.com/mpmdw/JouleWise/blob/909ebae8c90e20a0d92a4b20106ea2219c58becb/.github/workflows/ci.yml).
- The managed environment never supplied a shell: two pwd attempts failed and
  the readiness wait remained pending. Local fetch/checkout, literal
  `python3 -m unittest discover -s tests/align -t .`, canonical local discovery,
  touched-tier and census commands were not run. The user-authorized PR CI
  fallback executed both actual alignment modules and the whole discovered
  suite; it is distinguished from those unrun local commands.
- Extras: none installed, imported or required by this lane. CI's build frontend
  is packaging tooling, not a project extra; installed-wheel smoke uses --no-deps.
- Independent blind oracle derivation and fresh source/test audit used only
  requested gpt-6.1-sol helpers. All findings were dispositioned and the numerical
  oracles executed in CI. Their source reviews are **not independent execution**.
- [Current gate-ledger run 39716151861](https://github.com/mpmdw/JouleWise/actions/runs/39716151861)
  remains red because rows 1–4 are honestly NOT-RUN: independent executing review,
  merged-tree gate, final-head CI and cold final pass. PR #526 remains draft.
  The final handoff changes only this report/runbook relative to tested code.

Current skip reasons, counted from all 12 ordinary logs (sum 145; zero lane skips).
Existing fixture rulings/authority blockers below are not new lane rulings.

| Count | Exact unittest reason |
|---:|---|
| 18 | requires Darwin fchflags/st_flags |
| 13 | full scored corpus (set JOULEWISE_FULL_CORPUS=1) |
| 10 | block-3 b3w1 archive is local to the measurement Mac |
| 9 | matplotlib ([analysis] extra) not installed |
| 6 | FLAG joulewise/arm_readiness.py:7621: committed GAMMA lacks freeze authority; writer/ARM cannot continue. No nonphysical semantic shortcut is allowed. |
| 3 | the 2026-09-22 harvest archives are not on this machine |
| 3 | U2 successor engine pending |
| 3 | local model mirrors absent (CI environment): ['qwen25_0p5b', 'qwen25_1p5b', 'qwen25_7b'] |
| 2 | jsonschema not installed |
| 2 | lead-reviewed D-079 import inputs are unavailable |
| 2 | local Qwen3 tokenizer mirrors are absent |
| 2 | lsof is not installed |
| 2 | markdown-it-py not installed; the build cannot run here |
| 2 | native QoS requires macOS |
| 2 | optional jsonschema dependency is absent |
| 2 | reads the real gauge (macOS) |
| 2 | reads the real notify bus (macOS) |
| 2 | reads the real process table (macOS) |
| 2 | reads the real SMC (macOS) |
| 2 | real runs corpus unavailable |
| 2 | source corpus unavailable: /Users/edr/code/JouleWise/runs_window_a5_20260723 |
| 2 | requires Darwin's real pgrep command semantics |
| 1 | a desk run of the real read-only probes (macOS) |
| 1 | ACCEPTANCE GATE SKIP: determinism gate requires the retained runs/ corpus |
| 1 | ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus |
| 1 | clonefile(2) is an APFS call |
| 1 | CommonCrypto is macOS only |
| 1 | controlled runs corpus unavailable |
| 1 | Darwin pgrep ancestor exclusion; Linux pgrep has no such rule |
| 1 | design/2026-10-05-v5-claim-block-draft is not in this clone |
| 1 | full-fixture proof runs in d117-production-proof |
| 1 | gate-prune inventory is not on this machine |
| 1 | jsonschema not installed (optional) |
| 1 | kern.bootsessionuuid is a Darwin kernel value |
| 1 | kern.bootsessionuuid is Darwin-only |
| 1 | lead-reviewed D-079 import custody inputs are unavailable |
| 1 | live identity probes need macOS sysctl |
| 1 | measurement ledger not on this machine |
| 1 | pinned MATH source absent |
| 1 | POWER-Z KM003C not on the USB bus |
| 1 | reads the macOS kernel clock |
| 1 | reads the real host CPU ticks (macOS) |
| 1 | reads the real kernel clock (macOS) |
| 1 | real campaign-log corpus is unavailable |
| 1 | real collect subprocess runs the macOS census and power-policy probes (pmset, sysctl); on Linux every round errors and, since fix round 4, an all-error session exits 1 by design |
| 1 | real launchctl required |
| 1 | real Qwen3 tokenizer test requires the optional tokenizers library and local tokenizer.json |
| 1 | real spawned worker uses native QoS; hosted Linux shards feed the runner via stdin, which spawn cannot re-import |
| 1 | requires Darwin and explicit QG_LIVE_DARWIN=1 real-acquisition opt-in |
| 1 | retained capture 20260722T145535-e941c821 is not on this machine; run scripts/check_paper_replay_fence.py where the corpus lives |
| 1 | retained runs corpus is absent |
| 1 | retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live |
| 1 | runs_window corpus absent (clean checkout without bundles) |
| 1 | runs/ corpus absent (clean checkout without bundles) |
| 1 | split production proof requires a registered JOULEWISE_D117_PROOF_PARTITION |
| 1 | stopped-after-exec probe requires Darwin POSIX_SPAWN_START_SUSPENDED |
| 1 | STRUCTURAL-BLOCKED: generator targets uninstalled _v2 family while the registry installs _v5 |
| 1 | STRUCTURAL-BLOCKED: synthetic _v5 fixture omits the family-publication marker required before self-predecessor validation |
| 1 | successor member not minted yet; shape check is vacuous |
| 1 | temporary filesystem is case-sensitive |
| 1 | the block-5 design branch is not in this clone |
| 1 | the gate-prune inventory is not on this machine |
| 1 | the real kern.bootsessionuuid exists only on macOS |
| 1 | the two pilot-night archives are not on this machine |
| 1 | this file system gave the replacement lock the inode number of the lock just unlinked (4522143); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers) |
| 1 | window-B quarantine custody path is absent |
| 1 | local model mirrors absent (CI environment): ['qwen3-1p7b', 'qwen3-8b'] |
| 1 | NEEDS-RULING: config-authenticated mock telemetry is excluded by the production claim loader, so the existing canned fixture cannot satisfy D-158's DATA-only predicate without loosening a production gate or building a new corpus fixture |
| 1 | requires Darwin's POSIX extended regular expressions |
| 1 | requires Darwin's real boot-session sysctl command |
| 1 | requires Darwin's real caffeinate process |
| 1 | requires Darwin's real sysctl command |
| 1 | successor mirrors are still absent/incomplete: ['qwen3-1p7b', 'qwen3-8b'] |
| 1 | the block-3 reference archive and the measurement interpreter are on Ed's Mac only |


### Historical r0 execution (retained provenance, not current-head validation)
**PASS: [CI run 39708988879](https://github.com/mpmdw/JouleWise/actions/runs/39708988879), all 20 jobs, tested code SHA `1110fff802b0c0c4c9400f984a4f168d8c319ac1`.** The r0 final handoff commit changed only its report and runbook. The historical whole discovered suite reported 9,903 tests, zero failures/errors and 145 existing skips: 9,835 ordinary tests plus 48 calibration-exit tests and 20 crash-matrix tests. Quick-tier/fence tests overlap that suite and are not added again.

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
- R0c run `39714649345`, code `de8473a7a8d6b6e8928f4f00d3cdec511478bdfc`: the Stage B module executed 34 tests in 139.381 s, two failed assertions, zero errors/skips. Both INA recovery intervals cleared the unchanged required r, but the tests incorrectly also expected the separate physical contrast bound to clear. The correct failed no-stall physical verdict is retained. The positive configuration now enables source-backed blocking stalls; neither the statistical bar nor q*T bound was weakened. Later guard/test revisions superseded this unfinished whole-suite run. Other superseded continuation CI runs were cancelled automatically by the unchanged PR concurrency policy; none is claimed as a passing full suite.
- CI run `39705799481`: repository discovery inventory failed because unittest named the new subpackage modules `align.*` while the shard inventory used `tests.align.*`. Fixed only the existing namespace-normalization condition in `tests/test_shard_tests.py`; preserved exact inventory equality.
- CI run `39706737827`, code `9eaf7683f31befbe4633f796326e532de5656d13`: 28 Stage B tests ran, one failed, zero errors/skips. The failed assertion expected gapped INA acquisition to clear the fixed recovery bar. The synchronized 50 ms schedule failed the point comparison; the continuation replaces that invalid default verdict and evaluates it only as a labelled worst case with an interval. Retained that world as a negative test, corrected the final verdict to require empirical recovery, and added a contiguous-acquisition positive control. No routing coefficients or comparison bar were weakened. Unfinished ordinary shards were cancelled; this was not a passing whole-suite run.

Independent numerical/source review: requested model `gpt-6-astra`, task `/root/independent_numeric_reference`; the runtime did not separately expose model identity. The reviewer authored the oracle before seeing the production implementation. It uses ordered lists, direct overlap integrals and pairwise statistics, independently checking traffic policies, batched prefill, acquisition, feature energy/variance/spectrum, OLS, correlations and the design forecast. Source findings fixed: preserve hit order, clock bounds over disjoint intervals, scaled Pearson, finite/count/tail validation, within-condition SD and held-out attenuation, white-noise double counting, and optimistic forecast substitution. Final source-only review of `1110fff802b0c0c4c9400f984a4f168d8c319ac1` found no blocking scientific defect. Its nonblocking naming observation was resolved in documentation: `forecast_empirical_disagreement` specifically reports an optimistic forecast that fails empirical recovery, not the reverse direction. The independent agent had no shell; this is source/oracle review, not an independently executing review.

## END-TO-END
The real chain is `synthetic_episode -> synthetic_token_schedule -> apply_decode_stalls -> model_traffic -> simulate_episode -> PowerTrace -> extract_features(actual windows, nominal reference) -> grouped recover_routing -> Fisher interval/design comparison`.
Architecture, 864 MiB synthetic SLRU budget, 128-token prefill batches, 32 GB/s and 160 pJ/B inputs remain the r0 scenarios. Both sensors see the same Jetson-like 8 W baseline + 4 W decode power world; NVML here is an acquisition sensitivity case, not an RTX power calibration.
INA inputs remain 6.6 ms acquisition / 10 ms polling, 0.036032 W quantum and 0.04 W independent noise. NVML remains 25 ms / 100 ms, 0.001 W quantum and 1 W noise.
Timing variation is uniform +/-2 ms about 50 ms compute steps, a declared uncalibrated parameter with its own seeded RNG. Default worlds also add blocking upload time; the synchronized-bursts world has zero variation and stalls disabled.
The supplied external Stage A d=1, 50 independent groups/condition, alpha=.05, power=.8 and three comparisons still require r=0.6471202066782847. No synthetic condition separation substitutes for Stage A.

The enlarged E2E worlds have 48 groups/condition, three turns, 768 prefill and
384 decode tokens, and three tool calls per episode. Each has 96 held-out
episodes, n_eff=94. The jitter-only rows retain transfer-only energy; the stalled
INA row enables the source-backed running-energy term. Both comparison bars
remain fixed.

| Configuration | Window / cadence ms | Samples | Held-out energy r [95% Fisher CI] | Forecast r | Contrast / bound J | Overall verdict |
|---|---:|---:|---|---:|---:|---|
| INA, variable timing + stalls | 6.6 / 10 | 342862 | 0.823237 [0.744863, 0.879203] | 0.833440 | 2.000373 / 0.767646 | yes |
| INA, variable timing, no stalls | 6.6 / 10 | 322624 | 0.809315 [0.725697, 0.869372] | 0.811230 | 0.598242 / 0.691718 | no |
| INA, resident | 6.6 / 10 | 322624 | -0.196926 [-0.384216, 0.005931] | 0.000000 | 0.000000 / 0.691718 | no |
| NVML, variable timing, no stalls | 25 / 100 | 32342 | 0.164749 [-0.039179, 0.355502] | 0.097968 | 0.598242 / 0.019197 | no |
| INA, synchronized bursts, no stalls | 6.6 / 10 | 322656 | 0.300520 [0.104247, 0.474262] | 0.439009 | 0.598242 / 0.691814 | no |

All five E2E analytic correlations lie inside the corresponding empirical
intervals. The no-stall variable INA row clears recovery but fails the separate
quantization contrast bound (0.598242 J < 0.691718 J); that negative physical
result is retained. Blocking stalls lift the contrast to 2.000373 J above
0.767646 J without changing the required r. Synchronized bursts retain failed
recovery. This supports timing-dependent INA visibility, not a sensor-wide
negative conclusion.

Default CLI: 12 groups/condition, four turns, 1024 prefill and 512 decode tokens,
four tool calls; N=24 and n_eff=22. Offloaded rows include blocking stalls.

| Configuration | Samples | Held-out energy r [95% Fisher CI] | Forecast r | Contrast / bound J | Overall verdict |
|---|---:|---|---:|---:|---|
| INA, offloaded + stalls | 114259 | 0.807376 [0.584842, 0.916882] | 0.847007 | 2.886183 / 1.023290 | inconclusive at this cohort size |
| INA, resident | 107546 | 0.116207 [-0.321143, 0.512702] | 0.000000 | 0.000000 / 0.922481 | no |
| NVML, offloaded + stalls | 11446 | 0.665356 [0.338775, 0.848848] | 0.759429 | 2.886183 / 0.028399 | inconclusive at this cohort size |
| NVML, resident | 10771 | 0.427928 [0.007702, 0.719695] | 0.000000 | 0.000000 / 0.025602 | inconclusive at this cohort size |

The offloaded default INA and NVML forecasts lie inside their empirical
intervals; both intervals contain required r, so neither point estimate decides
the pilot. The resident NVML nominal interval happens to exclude the forecast's
zero correlation while still containing the required r: finite-cohort noise is
retained, not evidence of modeled coupling (its bytes and true energy are zero).
Paired episodes/shared CV fits further limit nominal interval coverage.

Default transfer-only extra energy is [0.00304238592, 0.05278224384] J/decode token;
with running stalls it is [0.01017297792, 0.17649062784] J/token. Decode duration
grows from [25.548059603, 25.654410814] s compute-only to
[25.856373476, 30.914227554] s offloaded, preserving prefill/tool gaps.
INA apparent extra is [0.010193455699749773, 0.17654024210091254] J/token;
NVML is [0.01174969970150001, 0.17697168368906446] J/token.
Default acquisition-error SD is 0.0866584442041829 J for INA and
1.4877634899422347 J for NVML; resident values are 0.024937692923639846 J
and 1.5612500592270946 J. In the E2E phase comparison INA error SD is
0.17020184370230057 J with jitter versus 1.15849743485807 J synchronized.

The CLI ran 96 episodes; the five enlarged E2E cases ran another 480.
All raw and centered feature correlations/intervals, including variance and
spectral diagnostics, are retained in the CI evidence JSON.


The independent unequal-traffic fixture runs actual model traffic, timing, sensor simulation and extraction: 10/0/20 bytes at 1000 B/s add 10/0/20 ms to 2/5/3 ms compute windows. Actual decode is 40 ms, tool gap stays 5 ms; memory energy is .03 J. Running power 12 W adds .36 J, for .39 J incremental (.13 J/token); a 6 W stalled platform gives .21 J incremental. Both explicit and implicit timing paths are checked. Sparse coverage cannot receive inferred stall energy.
For a production-shaped all-miss token, 128*3,538,944 = 452,984,832 B at 32 GB/s takes 14.155776 ms: memory .07247757312 J, running .169869312 J at 12 W, total .24234688512 J. Default per-token with/without-stall ranges appear above; values are illustrative inputs, never calibration.
A real-sized exact-time regression checks 37*3,538,944 B / 32 GB/s = 4,091,904 ns; this catches the prior float-ceil one-nanosecond excess.

No synthetic result establishes real detectability, calibrated channel J/B, confidence-interval coverage under dependent folds, or registered design power.

## DECISIONS I MADE
- User-directed lane work overrides unrelated historical queue ranking; Mission M0/read-only intake found no active stop card in the fetched spine. No out-of-scope bookkeeping was written.
- At r0 intake the lane branch did not exist. It was created from spine SHA `4d47c4362352ccd8d4d904134a79f0d8260b21b5`. While the VM was unavailable, authorized branch-only commits were checkpointed using connected GitHub tools.
- No sensor simulator exists on the spine; the lane therefore owns a local analytic simulator.
- Keep all core functionality stdlib-only, with no optional-dependency requirement or network in tests.
- Model incremental bytes/energy on a named sensor-visible memory path, not total inference energy. Cache-disabled CPU offload is not a PCIe expert-upload model; Jetson shares DRAM.
- The upstream source is pinned at llama.cpp `a37cc46104eb50900d5ab4a9ba02a0abdac039db`; `--n-cpu-moe`, `-ot`, `--moe-cache-mib`, `--fit off` and `--n-gpu-layers all` were checked in its parser.
- Model request-atomic hit-first LRU/SLRU, pinned residency and explicit prefill batch unions. Upstream multi-group caches and read-only large-batch cache reuse are documented limitations with flags.
- Preserve all flags and missing predictions rather than excluding episodes. No new data-eligibility rule is introduced.
- Use explicit actual token windows throughout the continuation world. The uniform adapter remains flagged interpolation; it is never observed timing. Never apply the compute-only stall adapter twice to measured timestamps.
- Treat NVML duty-cycle gaps and acquisition spectra explicitly; do not multiply apparent energy by inverse duty fraction.
- Predeclare three scalar features and hold out complete task groups. Center held-out results within condition for the Stage A attenuation comparison; report raw correlation separately.
- Keep Stage A effect, sensor noise, memory energy, step jitter, running power, systematic bounds and design choices as parameters. +/-2 ms is a timing scenario input, not a sourced hardware estimate. Route and timing RNGs are separate so timing changes preserve route identity.
- OLMoE Q4_0 is the small physical pilot candidate. Re-estimate Stage A on that model; a Qwen effect cannot be transplanted. A Qwen3-30B-A3B resident bank does not fit Jetson shared memory, while RTX CPU-offload feasibility also depends on unspecified host RAM.
- Use the separately authored numerical oracle and source review required by PIPELINE/AGENTS. CI provides execution while the managed VM is offline; distinguish it from independent executing review and the literal unrun local commands.
- Predeclare energy as the empirical decision. Require the complete approximate 95% Fisher interval to clear the unchanged design bar; center within condition and reduce effective n by two fitted means. Raw r uses the full held-out episode count. Negative signed recovery is not made positive. Inconclusive intervals and missing features remain flags/nullable results, never exclusions.
- Source establishes blocking upload dependencies, so the default includes decode stalls plus sensor-visible running energy. Prefill stalls, execution overlap, cache groups and nonconstant running power remain separate calibration questions. Transfer-only J/B excludes the running term to avoid double counting.
- Fit the analytic slope within condition and retain true mapping residual variance; report whether forecast r lies in the held-out interval. Correlated aliasing/DVFS errors can still violate its independent-error assumptions.
- Enlarge E2E scenarios to 48 groups (96 held-out episodes, n_eff=94). Its Fisher-z margin is 1.96/sqrt91=0.2055; a positive point near .8 (z=1.099) separates from required z=0.770. The positive configuration enables the source-backed blocking stalls; the jitter-only comparison retains its failed physical contrast bound. Default CLI retains 12 groups and may be inconclusive.
- Only gpt-6.1-sol helpers were started in r0c: one blind oracle/source derivation and one fresh source/test audit. The PIPELINE request for a different-model oracle conflicts with the continuation's exclusive model rule; existing r0 cross-model oracle is retained and this new independent same-model provenance is explicit. No other model was started in this continuation.
- Keep the PR to the spine as a draft for existing CI; no workflow changes, merge, force-push or main push. Report all evidence against its tested code SHA; the final report/documentation commit changes no Python source.

## CONTRACT-CHANGE
No shared contract file was modified. A future optional companion routing-timing record would avoid reconstructing token/turn/microbatch timing: token ordinal, turn index, actual executed phase, start/end brackets, microbatch identity and clock domain. The current lane works around the absence with explicit `TokenWindow` inputs and flags. This proposal is not installed and changes no data eligibility.

## OPEN ISSUES
- The managed environment never supplied a shell. Exact local discovery/touched-tier/census commands remain unrun; existing CI executed the discovered modules instead.
- The primary mean-energy correction uses a nominal compute-time reference. Hardware must estimate it independently from controls and propagate its uncertainty; per-token variance remains explicitly flagged as excluding that running-stall correction.
- Hardware J/B, effective bandwidth, INA rail configuration, RTX sensor cadence, logger perturbation and Stage A effect sizes require calibration. No hardware, model server or external inference service was accessed.
- Exact batched-prefill replay needs backend cache-group/slot/batch state; read-only cached-weight reuse is flagged as unmodelled. The timing adapter is flagged interpolation, not measured token timing.
- Mapping residuals are now included in the forecast. Correlated sensor errors and dependence from paired episodes/shared cross-validation fits remain limitations; the nominal Fisher interval is not demonstrated frequentist coverage or hardware design power. Hardware must measure token/sensor phase locking.
- Draft PR #526 remains a CI/review vehicle. Its separate gate-ledger fails the honestly uncompleted review/merge/final-head/cold-pass rows; no independent executing review, cold Fable pass, all-checks-green or merge-ready claim is made. No merge was requested or performed.
- No network access, credentials, keys or personal email addresses were added to tests.

## NEEDS_RULING
none

## CONTINUATION r0c
Variable INA without stalls: r=.809315 [.725697,.869372], recovery yes but physical contrast no; synchronized bursts: r=.300520 [.104247,.474262], recovery no. Stalled INA: r=.823237 [.744863,.879203], contrast 2.000373 J > bound 0.767646 J, yes. Default stalled INA r=.807376 [.584842,.916882] and NVML r=.665356 [.338775,.848848] are inconclusive at N=24. Forecast r is inside all five E2E intervals. Stage B module: 34 tests, 115.018 s, zero skips; final whole-suite status recorded above.

Work resumed from `0fc746f6d36aecb61716e821ce6318f40ab02c1a` under the lead’s three findings. Added explicit variable token windows, blocking decode stalls and platform running energy, conservative interval-based verdicts, forecast mapping residuals and enlarged synchronized/variable timing worlds. Source/test audit fixed configured-power agreement, incomplete-coverage correction and exact-ns rounding. Invalid schedule inputs are flagged before arithmetic; synchronized_bursts requires both zero jitter and stalls disabled. The first executed no-stall recovery succeeded but failed the separate quantization contrast bound; that result is preserved. Historical r0 commands/results remain labelled above.
