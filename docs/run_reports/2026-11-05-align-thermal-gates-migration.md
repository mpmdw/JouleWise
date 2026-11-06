# PR #666 migration onto fixed #658 — 2026-11-05

Branch: `lane/2026-11-05-align-thermal-gates` (the branch requested in the brief).
Starting head: `1bb8cd865`. Merge input: existing local origin ref
`lane/2026-11-05-align-smc-thermal`, `58525031ac7beda3dd0075cb8255716ccbbff1fb`.
All commits are local; no fetch, network, push or PR edit.

## Authority and boundaries

Read both requested run reports first, including #658's fix-round version
through `git show`. Read root AGENTS/CLAUDE, Mission M0, the stop-card,
status/workspace/queue pointers, authority map, orchestration and targeted
D-003/D-009/D-050/D-090 entries. No active stop card. Selected this explicit
bounded [AGENT] brief; did not register a task or edit RUN_STATE, TASK_QUEUE,
the state kernel or test_gen_state. The worktree began clean.

Read the binding council design from the authorized Git object store at
`6eb1ff5be31bec330ae5af262c2b4c7601e7755e`, including V8 and thermal/hold
requirements. Applied the explicit user instruction to adopt #658's fixed API.
No new scientific constants, roster, model pin, reference or registration.
The reports' unresolved Amendment-1 provenance remains lead work; no claim
that its complete text was verified here.

No real restricted directory, measurement data, external /Users/edr path,
analysis pipeline, native SMC read, MLX execution, model load, quiet capture,
external integration or agent delegation was used. Absolute references in
repo text were not followed. Synthetic tests used clone-local files and
allowed temporary directories. Git's shared code-object store was used only
through Git. No full test discovery or pytest; targeted unittest invocations
ran one module at a time under the standing machine-load restriction.

## Changes and commit structure

- `5e257e63e` — merge resolution. Adopted fixed ALIGN-local reader, Sidecar,
  coverage, R0/R1 selection, CLI and upstream compatibility tests. Resolved
  eight conflicts: the seven in the brief plus `test_pilot3_cache.py`, where
  #666's explicit legacy byte oracle was retained. Restored driver, harvest
  and schemas exactly to the input branch/pilot-9 bytes.
- `1facf91ff` — gate/hold runtime integration. `ThermalSession` wraps one
  fixed Sidecar and reads locked snapshots. It owns no second reader, thread
  or journal. Both sensor-only and nested gate `EpisodeSpec.thermal` slots
  work; gate validation is `thermal_gates.validate_gate_policy`, while sensor
  validation remains `validate_policy`. G0/G1, fixed-token holds, lookahead/stream draining,
  shared G0-entry deadman, partial tokens, phase markers and capability
  scoring remain in ALIGN. Context-free identity readiness opens no collector
  and cannot execute a member. Failed prepare closes collection; cleanup
  closes it after native teardown, including teardown failure.
- `6018b56ec` — sampling-grid coverage,
  Sidecar journal consumption in the desk, obsolete reader/monitor removal,
  expanded pilot-9 pin regression and migration tests/documentation. Gate/
  stream/registry helpers live in `align/apple/thermal_gates.py`; the fixed
  `thermal.py` collector stays independent of runtime/deadman imports.

The collector writes only `outputs/align_thermal.jsonl` with the fixed
`joulewise.align_thermal.v1` three-clock rows. OS/PM status is inside reading
values, outside the SMC bracket. Gate/hold begin/end rows use `Sidecar.event`;
final hold ends retain dispatch-time custody. Existing endpoint and attribution
logic splits holds out of owned decode and preserves gross energy/I3 tiling.
The desk retains U1–U6 and its separate hardware/monitoring verdicts, verifies
release samples against this member's journal, and uses the collector grid,
partial-edge policy and actual `max_interval_ns` for the 2 s bar.

Removed the obsolete #666 `align/apple/smc.py`, `temperature_monitor.py`
and `scripts/align_temperature_monitor.py`. The fixed `smc_reader.py` owns
extra decoders; CampaignPolicy and the driver have no thermal hooks.

All 29 pre-migration gate/hold tests remain; two added cases cover a gate
crossing caller-slot boundaries and X4 hold completion. All 18 thermal desk
cases remain, with journal/coverage fixtures adapted to the fixed API.
The original driver-policy/journal/fast-loop temperature checks are adapted
to the EpisodeSpec identity, one-Hz Sidecar, three-clock custody and rejection
of path fields. The fixed #658 enumeration/ranking tests supersede the
rejected little-endian/#KEY and amplitude/noise selection expectations.

### Catches during migration

The initial gate run caught context-free readiness accidentally constructing
a collector, and a fake-clock sampling-grid shift after costly status parsing.
Grid-aware follow-ups caught duplicate fake ticks resetting the consecutive
sample count. The final test seam ticks the same collector on absolute
deadlines and does not tick twice when an injected clock already sampled.
A final static import-graph check caught gates pulling runtime dependencies
through the `hazards.temperature` compatibility alias. Separating the gate
controller into `thermal_gates.py` restored the diagnostic/core boundary;
all five static graph cases passed after the move. Endpoint/workload and
#666 tests use the new gate module directly.
The desk boundary test now requires an explicit maximum interval, including
the exact 2 s pass and 2 s + 1 ns failure.

An added end-to-end regression was observed failing before its one-line fix:
X4/unobserved H resumed decoding but `workload.py` treated any non-released H
as a cancellation and suppressed the completed tools. It now suppresses tools
only for actual timeout/deadman outcomes, matching the existing F10 ruling.
X4 retains completed IDs/tools and capability, while remaining excluded.

## Verification

Every module row below is a separate serial invocation of
`JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest <module>`.
The final set has 24 module targets plus the focused cases listed afterward;
all returned 0. Native skips are not native passes. Final module wall time was
about 160 seconds; all repetitions and failed reproductions stayed well below
the approximately 20-minute test budget. Python 3.11 was not exercised.

| Module | Final result |
|---|---|
| `tests.hazards.test_smc_enumeration` | 15 reported; PASS |
| `tests.hazards.test_temperature` | 13 reported; PASS |
| `tests.align.test_smc_selection` | 9 reported; PASS |
| `tests.align.test_smc_quiet` | 5 reported; PASS |
| `tests.align.test_smc_gpu` | 4 reported; PASS |
| `tests.align.test_decode_budget` | 15 reported; PASS |
| `tests.align.test_attribution` | 36 reported; PASS |
| `tests.align.test_thermal_legacy` | 1 reported; PASS |
| `tests.align.test_pilot3_cache` | 12 reported; PASS |
| `tests.align.test_pilot4` | 18 reported; OK, 1 skips |
| `tests.align.test_energy_residual` | 13 reported; OK, 1 skips |
| `tests.align.test_apple_endpoint` | 9 reported; PASS |
| `tests.align.test_apple_campaign` | 12 reported; PASS |
| `tests.hazards.test_monitor` | 36 reported; OK, 1 skips |
| `tests.hazards.test_monitor_p2` | 6 reported; PASS |
| `tests.test_schemas` | 43 reported; OK, 1 skips |
| `tests.align.test_thermal_mlx` | 2 reported; OK, 2 skips |
| `tests.align.test_smc_native` | 1 reported; OK, 2 skips |
| `tests.align.test_thermal_gate` | 31 reported; PASS |
| `tests.align.test_thermal_sidecar` | 9 reported; PASS |
| `tests.align.test_thermal_desk` | 18 reported; PASS |
| `tests.align.test_thermal_coverage` | 3 reported; PASS |
| `tests.align.test_measurement_core_boundary` | 1 reported; PASS |
| `tests.align.test_attribution_holds` | 5 reported; PASS |

`test_smc_native` reports one test run and two skips because the SMC class is
skipped in setUpClass and the GPU case separately skips. Neither native case
executed. `test_thermal_mlx`'s two array/stream tests also skipped.

Focused commands with the same synthetic/Python prefix:

- `tests.hazards.test_smc.EncodingTests tests.hazards.test_smc.ReaderTests`:
  12 reported, OK, one skip; no live class selected.
- `tests.test_b5_driver.UnitTests.test_production_seams_follow_the_other_lanes_command_lines`:
  one PASS.
- `tests.test_b5_driver_p2.SupervisionTests.test_the_production_monitor_config_names_the_chain_start_record_as_a_tree_root`:
  one PASS.
- The five static `tests.hazards.test_import_graph.ImportGraphTests` cases:
  `test_hazard_modules_reach_no_retired_module`,
  `test_the_analyzer_sees_the_measurement_core_reach_arm_readiness`,
  `test_hazard_modules_import_no_flag_code`,
  `test_flags_package_reaches_no_retired_module`, and
  `test_the_adapter_import_is_confined_to_the_capture_child`: five PASS.
  The first was initially red and led to the module-boundary fix above.

Additional checks:

- `python3.13 -B -m compileall -q joulewise tests scripts/align_smc_enumerate.py scripts/align_v4_thermal_desk.py`: PASS.
- Both CLI `--help` commands: PASS; no backend opened.
- `git diff --check` and staged check: PASS after removing a trailing blank
  line caught in the final report check.
- Direct full-byte comparisons of driver, harvest, schemas, hazard SMC and
  hazard monitor against **both** `c9a0a3943` and the fixed origin ref: PASS.
  The expanded regression freezes SHA-256 for these complete pilot-9 files.
  An AST inventory confirms all original gate (29), desk (18), attribution-
  hold (5) and native-MLX (2) test methods remain; gates now have 31 cases.
  The fixed #658 commit is verified as an ancestor of HEAD.
- Protected coordination-path diff against `1bb8cd865`: empty.
- Session-end `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`:
  exit **2**, `{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}`.
  Count/rows are unavailable; this is not an empty/clean census. No signal or
  sandbox bypass was attempted. Full driver/process integration was not run.

Temporary command logs/structured results are in
`/private/tmp/jwsol/migrate-666/tmp/{targeted,integration,boundary}-results.json`,
`final-module-results.json` and `focused-cases-results.json`. They contain
synthetic test output only; the committed table is the durable handoff.
No ephemeral invocation was delegated to another agent or model.

## Files and next exact step

Migration-authored runtime files: `align/apple/{thermal,thermal_gates,
thermal_desk,workload,endpoint}.py`; removed `align/apple/{smc,
temperature_monitor}.py` and `scripts/align_temperature_monitor.py`.
Tests: `tests/align/{test_measurement_core_boundary,test_thermal_gate,
test_thermal_desk,test_thermal_sidecar,test_thermal_mlx}.py` and
`tests/hazards/test_temperature.py`. Docs: `docs/align/{thermal_gates,
smc_temperature}.md` and this report. The merge also brings #658's fixed
SMC/selection/coverage/CLI files, compatibility imports, restored pinned files
and its own tests/reports; those changes are recorded in the merge commit.
A final docs-only commit records these results.

Next: lead review of the local merge and integration commits, then the native
checks below in a clean, lead-controlled Mac session after agents exit:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
JW_B5_SYNTHETIC_ONLY=0 JW_LIVE_HW=1 python3.13 -B -m unittest tests.align.test_smc_native
```

Use the locked interpreter with MLX importable; no CPU fallback. The first
module's two tests use real arrays in a small synthetic lookahead stream.
The second owes `NativeSmcTests.test_native_big_endian_count_and_index_inventory`
and `NativeGpuTests.test_native_worker_starts_from_other_directory_and_is_reaped`.
These are still not qualification of the actual pinned mlx-lm 0.31.3 generator.
R1 must establish held/unheld token identity, actual pending-work draining,
resume transients, sensor identity/refresh/coverage, sidecar overhead/cleanup,
member intercept/teardown slack and live meter exclusion custody. An
uninterruptible native/OS call is still bounded by the external runner.

No code migration blocker remains. Native behavior, the full process-capable
driver/dynamic import integration and Python 3.11 remain unverified here.
The v4 launcher must select `thermal_gates.ThermalRegistry`, persist the
window reference across fresh processes, bind registered sampler spans and
feed the full frozen v4 desk. The earlier reports' unresolved protocol U4–U6
conventions and Amendment-1 provenance remain lead-owned. No scientific
registration, control verdict or acceptance certificate is claimed.
All hardware evidence remains **PROVISIONAL**.
