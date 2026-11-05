# ALIGN SMC thermal journal and R0 tool — 2026-11-05

Branch: `lane/2026-11-05-align-smc-thermal`.
Base: `origin/lane/2026-11-05-align-pilot9-benign`,
`c9a0a39437614176bf4e14ff1565a6e4537328fb` (verified before branch creation).
Implementation commit: `274fec2cb` —
`feat(align): add pinned SMC temperature journal and R0 desk tool`.
This report is a separate local documentation commit. Nothing was pushed.

## Intake and boundaries

Selected the user's bounded implementation brief as explicit [AGENT] desk
work, ahead of ordinary queue selection. Read AGENTS/CLAUDE conventions,
Mission M0, the stop-card/status/workspace/next-work pointers, current queue
and do-not-do list, authority map, D-003 clock policy, relevant ALIGN and
measurement docs, and orchestration conventions. No active stop card was
present; the checkout began clean and detached at the requested base.

The user's standing rules override normal coordination-state edits and the
canonical full-suite requirement. **No changes** to `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json` or `tests/test_gen_state.py`;
no task registration. No network, external consult, delegation, installation,
push, heavy GPU work, MLX import/model load, live SMC read, measurement
campaign or block-5 analysis pipeline was performed. Reads were confined to
this checkout, temporary test fixtures, and Git's authorized object store.
Some existing tests use stored hazard fixtures; none was treated as live
hardware evidence.

## Built

- Extended the existing `smc.Reader` with command-8 index enumeration through
  `#KEY`, readable T*** temperature/F?Ac fan discovery, retained enumeration
  errors and legacy `sp78` / `fpe2` decoding. Existing battery/power defaults
  remain the same.
- Added `scripts/align_smc_enumerate.py` and stdlib R0 capture/ranking helpers.
  The tool records 1 Hz three-clock samples, key metadata and failures,
  JSON and Markdown. The opt-in fixed MLX GPU matmul step uses an isolated,
  ready-signaling, time-bounded child; tests replace that load completely.
  It guards startup and periodically supervises agent and measurement-owner
  censuses, plus direct collector processes, and refuses uncertainty.
- Fits amplitude and first-order heating/recovery time constant, with idle
  noise and coverage checks. Proposes the largest amplitude/noise temperature
  in tau <30 s and >120 s classes, with strict boundaries and lexical ties.
  Fan fits are reported in RPM and excluded from temperature selection.
  A missing or unresolved class yields null, not an invented sensor identity.
- Added an optional `temperature.jsonl` journal to the existing hazard
  monitor, using its fast thread, locked SMC backend, append/fsync custody,
  session headers, supervisor lifecycle and three clock domains. Therefore
  it starts before and stops after the episode chain through the existing
  driver rather than adding an independent collector lifecycle.
- Added per-key/all-key successful-slot fractions and explicit merged gap
  intervals. Session ends report coverage; a desk helper recomputes over any
  episode span, including restart gaps. Late multi-slot reads, duplicate
  samples, invalid values and unreadable sensors do not repair missing slots.
- Added the optional `CampaignPolicy.smc_temperature` extension: fast/slow
  key names, fan list, and R0 JSON hash. The driver resolves the campaign
  policy's pinned pack descriptor, checks its byte hash and validates it;
  existing different monitor configs cannot be reused. Omitted extensions
  preserve old monitor probes/journals and policy serialization. No existing
  campaign policy or collected pack was changed or supplied with guessed keys.
- Added optional-journal loading and the temperature module's observation
  kind to the existing desk parser. No scientific eligibility, thermal
  admission threshold, historical interpretation, or desk-table column was
  installed by this diagnostic work.

## Files touched

- `joulewise/hazards/smc.py`, `temperature.py`, `smc_enumeration.py`, `monitor.py`.
- `joulewise/schemas.py`, `joulewise/b5/driver.py`, `joulewise/b5/harvest.py`.
- `scripts/align_smc_enumerate.py`.
- `tests/hazards/test_smc.py`, `test_temperature.py`, `test_smc_enumeration.py`.
- `tests/test_b5_driver.py`, `tests/fixtures/b5_plan/fake_window.py`.
- `docs/align/smc_temperature.md` and this report.

The existing SMC tests' unsupported-type sentinel changed from `sp78` to
`zzzz` because `sp78` is now supported. The fake measurement checkout now
includes actual static policy config bytes for the new pin check, and the
argv-only monitor seam test explicitly stubs the new policy resolver; the
new tests exercise that resolver with real temporary config files separately.

## Verification

All unittest commands below used `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest`.
Modules/cases were run sequentially; cumulative targeted test time was well
below 20 minutes. The full suite and `scripts/run_b5_analysis.py` were not run.

| Target/command suffix | Final result |
|---|---|
| `tests.hazards.test_smc_enumeration` | 18 tests, PASS (~1.5 s); fake IOKit, sensors, clocks, process censuses and GPU worker |
| `tests.hazards.test_temperature` | 12 tests, PASS (~0.6 s); policy pin/config reuse, three-clock journals, real desk parser, gaps/coverage |
| `tests.hazards.test_smc` | 12 tests, PASS, 2 live-hardware skips |
| `tests.hazards.test_monitor` | 36 tests, PASS, 1 live-hardware skip (~18.4 s) |
| `tests.hazards.test_monitor_p2` | 6 tests, PASS |
| `tests.test_schemas` | 43 tests, PASS, 1 skip |
| `tests.test_b5_driver.UnitTests.test_production_seams_follow_the_other_lanes_command_lines` | PASS |
| `tests.test_b5_driver_p2.SupervisionTests.test_the_production_monitor_config_names_the_chain_start_record_as_a_tree_root` | PASS |
| Five static cases of `tests.hazards.test_import_graph.ImportGraphTests` listed below | 5 tests, PASS |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_smc_enumerate.py` | PASS |
| `python3.13 -B scripts/align_smc_enumerate.py --help` | PASS; no backend opened |
| `git diff --check` / staged equivalent | PASS |
| Protected-path diff check | PASS; all four prohibited files unchanged |

Static import-graph cases:

```text
test_hazard_modules_reach_no_retired_module
test_the_analyzer_sees_the_measurement_core_reach_arm_readiness
test_hazard_modules_import_no_flag_code
test_flags_package_reaches_no_retired_module
test_the_adapter_import_is_confined_to_the_capture_child
```

Initial targeted failures were corrected: the old unsupported-type sentinel,
the optional task being included in the default task-list invariant, and
missing fields/config bytes in synthetic driver fixtures. The corresponding
checks above passed after those corrections.

Two broader targeted runs are **not green** and must not be represented as
fully verified:

1. `tests.test_b5_driver.UnitTests`: 12 tests; 3 failures and 1 error in the
   initial run (~22.4 s). The error was the policy/fixture seam issue, now
   corrected and rerun successfully as the exact case above. The three
   process-management failures were
   `test_arm_run_off_and_collectors_are_recorded_once_not_rerun`,
   `test_dead_man_stops_an_orphaned_monitor_group_and_never_a_reused_pid`, and
   `test_the_monitor_disk_low_marker_stops_the_chain`. This sandbox denies
   `ps` and process-group signaling; these cases depend on those operations.
   Their complete behavior was not verified here. Two test-created sleeping
   monitor processes (PIDs 7013 and 7147) emitted ResourceWarnings. Cleanup
   attempts using only those known test process groups were also denied.
   Their source has a fixed 600 s sleep and then exits; their final exit
   could not be observed through the denied process census. No analysis-job
   process was targeted, and no sandbox override was attempted.
2. `tests.hazards.test_import_graph`: 6 tests; 5 passed, but
   `test_a_complete_arm_and_monitor_run_load_no_retired_module` returned
   synthetic arm decision `NULL` rather than `GO`. This case starts the
   fake cadence collector as a real subprocess. The exact cause was not
   isolated and no clean baseline reproduction was made; sandbox process
   restrictions are a possible cause, not a proven diagnosis. The five
   static graph cases were rerun successfully by exact names. Do not claim
   the complete arm/monitor integration passed.

Python 3.11 was not exercised as part of this run; local checks used
Python 3.13. No performance, actual sensor cadence or real GPU claims are
supported by this test evidence.

## Measurement-Mac handoff and open questions

Full procedure and assumptions: [`docs/align/smc_temperature.md`](../align/smc_temperature.md).
After all agent sessions and measurement chains have ended, use the existing
measurement environment and its correct custody-parent environment variables:

```sh
python3.13 -B scripts/align_smc_enumerate.py \
  --output desk-custody/align-r0-step-UNIQUE --gpu-step \
  --idle-seconds 300 --load-seconds 600 --recovery-seconds 600
```

Use the interpreter with the existing MLX install, such as `.venv/bin/python`,
if appropriate. No installation or download is part of the tool. A 60 s
inventory-only command without `--gpu-step` is documented too. Outputs must
stay in separate diagnostic custody; a completed report does not authorize
a measurement window.

**Next exact step:** lead reviews this branch and the sandbox-limited checks,
then runs R0 in a clean Mac15,9 desk session. Check reported hardware identity,
enumeration/index/byte-order behavior, readable keys, response traces,
coverage and fit quality. Anatomical die/GPU-cluster vs heatsink/skin identity
is still unverified; first-order tau is an operational proposal, not an
anatomical proof. If either class is missing, do not invent a pin. R0's
quality-filter constants are documented diagnostic choices; the lead must
review any future measurement admission/eligibility rule separately.

After accepting real M3 Max proposals, pin the emitted extension and R0 JSON
hash in a new/reviewed campaign policy and regenerate the pack's policy
descriptor through the normal lead-owned workflow. Then verify journal
coverage, fan readings, overhead and alignment to actual episode/meter spans
on that Mac. The R0 hash is retained provenance; acquisition does not
dereference an R0 data path. All real sensor, physical-location, worker,
signal-cleanup and cadence validation remains **PROVISIONAL**. This work
cannot retroactively explain pilot 7's alarms or the pilot 5-to-6 level step.
