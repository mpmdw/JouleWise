# Receipts-fix handoff — 2026-11-08

Task: apply the Opus cold review of timing receipts at `5fc873136`, merge the
latest local v4 r11 branch, and prove preservation using synthetic inputs.
Branch: `receipts-fix`. No push, network operation, model download, real
measurement/data read, production harvest, or quiet-machine campaign was run.
The active stop card was NONE. Mission M0 intake, repo authority, D-013/D-025,
and the speed toolbox were read. This explicit task was selected over the
ordinary queue. The user's sealed-study and no-full-suite rules override
normal coordination/full-suite instructions; no kernel task was registered.

## Findings and changes

- HIGH-1: moved member markers into the controller's RuntimeEvent list and
  stable event sort. Preserved the injected clock's original float timestamp
  to avoid nanosecond-round-trip inversions. Closed the finalization span
  before `run_finalized`, restored the ordinary bundle writer and removed its
  extra held stream/destructor. The imported Opus witnesses are unchanged.
- HIGH-2: the driver opens only its existing `night.log` (O_APPEND,
  without O_CREAT). A missing log leaves observations buffered. It never opens or
  writes the child's stage journal. Structure and harvest consumers were not
  edited. Cross-tree happy/refusal fixtures compare actual yield JSON,
  collection-presence/flags and the complete structure record byte for byte.
- HIGH-3: added `timing_receipts.py` to EXECUTED_CLOSURE, the pending template
  artifact map, and an actual single-module dynamic delta trace. Fixed the
  two reason-code-lint call sites. Template remains pending with null hashes.
- MED: replaced same-tree receipt disabling with separate base/current
  subprocesses at the same synthetic output path. The pinned base is
  `1a2574b49`. Shared seams supply tiny synthetic battery bytes, source
  provenance; traceback formatting removes source-location provenance while
  retaining actual exception types and messages. Only RSS/source paths are
  normalized after capture; only added marker lines are stripped. All other
  file bytes must match. Structural validation covers 18 W1 members and both
  pilot references, all 20 on each tree.
- MED: instrumented v4 arm checks, packet rebuild, meter probe, disk gate and
  install handoff. Install buffers markers and writes them to its already-open
  CLI stdout only when the operation exits. Chain settles use a single Python
  sleep process in place of the existing sleep process, write the existing
  chain log, and retain the requested wait even if receipt logging fails.
  Launch-barrier markers end before sending the collection release byte.
- MED: imported the offline reader and its synthetic/oracle tests from local
  object `dc684b308`. Member/native-log receipts refine broad envelopes;
  native G0/G1/H can precede episode start while staying inside the member.
  Gate intervals outside the member remain rejected. Existing sampler and
  zero-generation-observation boundaries explain the remaining synthetic
  gaps. The full producer test requires <=1 ms total unknown in-member time.
- LOW-1: moved the hazard dwell marker above the dwell start, boot read and
  first clock sample. No marker append occurs during the dwell itself.

Full implementation notes: [TIMING-RECEIPTS-IMPL.md](../perf/TIMING-RECEIPTS-IMPL.md).
The imported cold review is preserved at
[timing-receipts-opus-review.md](../perf/timing-receipts-opus-review.md).

## Commits

- `a25c77966` — merge latest local `origin/align/2026-11-08-v4-r11`
  (`a67de02f27328d77f7f40fac931f4b95f6c39dee`) into receipts-fix, without rebase.
- `ed9fd3ca16fa7c634657be03dc4f0a5c4cf22fc6` — fix receipt order/journal ownership, complete turnaround
  instrumentation, reader attribution, closure/template inventories and tests.
- A following documentation commit records this handoff; its hash is supplied
  in the final response (self-reference is intentionally avoided).

## Verification

All test processes used Python 3.13, `-B`, `JW_WP22_FULL=1`, a realpath’d
`TMPDIR=/private/tmp/receipts-fix-tests`, and disabled global/system Git
config and lazy fetching. Each process loaded only one unittest module.
No full suite or block-5 analysis pipeline was run. The commands below
share the prefix `python3.13 -B -m unittest MODULE` under that environment.

| MODULE | Tests | Latest result | Seconds |
|---|---:|---|---:|
| `tests.align.test_timing_receipts` | 21 | OK | 24.540 |
| `tests.align.test_timing_receipts_opus_witnesses` | 3 | OK | 6.753 |
| `tests.align.test_window_timing` | 28 | OK | 2.273 |
| `tests.align.test_v4_w1_synthetic` | 22 | OK (1 expected failure) | 94.054 |
| `tests.align.test_v4_executed_closure` | 4 | OK | 2.583 |
| `tests.align.test_v4_dynamic_closure` | 10 | OK | 10.557 |
| `tests.align.test_v4_registration` | 22 | OK | 23.548 |
| `tests.align.test_v4_next_arm_packet` | 28 | OK | 87.295 |
| `tests.align.test_v4_kit` | 116 | OK | 6.744 |
| `tests.test_bundle` | 74 | OK | 8.763 |
| `tests.test_bundle_read` | 82 | OK | 20.570 |
| `tests.test_controller` | 74 | OK | 48.537 |
| `tests.align.test_thermal_gate` | 44 | OK | 10.167 |
| `tests.test_b5_chain` | 25 | OK | 16.276 |
| `tests.test_run_night` | 318 | 2 failures, 1 error, 9 skips; identical failures on pinned base | 131.761 |
| `tests.test_session_structure` | 21 | OK | 0.343 |

The initial executed-closure check caught the missing pending-template
artifact entry; it passed after that entry was added. The final receipt
rerun includes the exception-type/message-preserving provenance seam and
the settle logging-failure path.

The three night-driver failures reproduce on untouched `1a2574b49`, in
one baseline process (3 tests, 32.495 s):

- `tests.test_run_night.HazardPackPrimitiveTests.test_dead_man_stops_the_hazard_monitor_a_dead_driver_left_running`
- `tests.test_run_night.HazardPackPrimitiveTests.test_natural_exit_census_proves_survivors_gone_before_recording_the_exit`
- `tests.test_run_night.HazardPackPrimitiveTests.test_supervision_stop_terminates_the_group_and_returns_its_refusal`

The baseline and current tree both report the same monitor-termination
timeout and two unproven process-group/census assertions. This establishes
that they predate this fix; sandbox process visibility is the likely
cause, but its root cause was not independently established here.

Additional checks:

- `python3.13 -B -m compileall -q joulewise tests scripts` — OK.
- `git diff --check` — OK.
- Fresh single-module dynamic trace: `tests.align.test_v4_w1_synthetic.MinimalDryRunTests`
  — 3 tests OK; no unbound/non-STRICT executed paths.
- Final read of producer, reader, test and inventory diffs completed.
- Final unique-module matrix: 892 test executions across 16 modules;
  additional focused retries/baseline checks are disclosed above. Total
  test wall time including intermediate attempts remained below 20 minutes.
- The final cross-tree assertions cover all 20 structurally valid bundles,
  identical normalized capture files, identical structure/yield outputs on
  both desk paths, and <=1 ms summed unattributed in-member time.

Raw command logs were kept only in this task’s scratch directory under
`/private/tmp/receipts-fix-tests`; no study inputs were copied there.

## Files touched

Correction round, relative to the merge commit (including new files):

- `configs/campaigns/align_v4/registration/registration_receipt.json`
- `docs/align/v4/dynamic_closure_trace.json`
- `docs/perf/TIMING-RECEIPTS-IMPL.md`
- `docs/perf/timing-receipts-opus-review.md`
- `docs/run_reports/2026-11-08-receipts-fix.md`
- `joulewise/align/apple/v4_registration.py`
- `joulewise/align/window_timing.py`
- `joulewise/b5/chain.py`
- `joulewise/bundle.py`
- `joulewise/controller.py`
- `joulewise/hazards/arm.py`
- `joulewise/timing_receipts.py`
- `scripts/align_v4_session.py`
- `scripts/run_night.py`
- `tests/align/benchmark_window_timing.py`
- `tests/align/test_timing_receipts.py`
- `tests/align/test_timing_receipts_opus_witnesses.py`
- `tests/align/test_window_timing.py`
- `tests/align/timing_receipts_capture.py`
- `tests/align/window_timing_synthetic.py`
- `tests/fixtures/b5_plan/fake_window.py`

Every receipt-bound path changed by this correction round (`ARTIFACTS`;
new strict module and the source/trace inventories are included):

- `docs/align/v4/dynamic_closure_trace.json`
- `joulewise/align/apple/v4_registration.py`
- `joulewise/b5/chain.py`
- `joulewise/bundle.py`
- `joulewise/controller.py`
- `joulewise/hazards/arm.py`
- `joulewise/timing_receipts.py`
- `scripts/align_v4_session.py`
- `scripts/run_night.py`

The registration template `configs/campaigns/align_v4/registration/registration_receipt.json`
was also changed; it inventories the new strict module but remains pending.
The offline reader and test files are not runtime receipt-bound.

Every additional receipt-bound path imported by the v4 merge, relative to
the task's starting `5fc873136` (overlaps with the correction list are retained):

- `configs/align/v4/r1_runtime.json`
- `configs/campaigns/align_v4/collection_plan.json`
- `configs/campaigns/align_v4/plan_tree.json`
- `configs/campaigns/align_v4/registration/battery_window_policy.json`
- `configs/campaigns/align_v4/registration/identity_pins.json`
- `configs/campaigns/align_v4/registration/inputs.json`
- `docs/align/pilot_protocol_v4.md`
- `docs/align/v4/W1-BLOCKERS-sol.md`
- `docs/align/v4/dynamic_closure_trace.json`
- `joulewise/align/apple/km003c.py`
- `joulewise/align/apple/smc_enumeration.py`
- `joulewise/align/apple/thermal_desk.py`
- `joulewise/align/apple/v4_battery.py`
- `joulewise/align/apple/v4_cadence.py`
- `joulewise/align/apple/v4_registration.py`
- `joulewise/align/apple/v4_topup.py`
- `joulewise/align/apple/v4_u3.py`
- `joulewise/align/apple/workload.py`
- `joulewise/align/r0.py`
- `joulewise/align/r0_host.py`
- `joulewise/align/r0_runner.py`
- `scripts/align_smc_enumerate.py`
- `scripts/align_v4_dynamic_trace.py`
- `scripts/align_v4_kit.py`
- `scripts/align_v4_next_arm_packet.py`
- `scripts/align_v4_session.py`
- `scripts/align_v4_thermal_desk.py`
- `scripts/align_v4_u3_bar.py`
- `scripts/align_v4_u3_export.py`
- `scripts/align_v4_w1_synthetic.py`

For the integration review, every net receipt-bound difference from the
merged v4 target (including the receipts inherited from `5fc873136`):

- `docs/align/v4/dynamic_closure_trace.json`
- `joulewise/align/apple/thermal_gates.py`
- `joulewise/align/apple/v4_registration.py`
- `joulewise/b5/chain.py`
- `joulewise/b5/driver.py`
- `joulewise/bundle.py`
- `joulewise/controller.py`
- `joulewise/hazards/arm.py`
- `joulewise/timing_receipts.py`
- `scripts/align_v4_session.py`
- `scripts/align_v4_w1_synthetic.py`
- `scripts/magistrate_watchdog.py`
- `scripts/run_night.py`

## Limits, uncertainty and exact next step

- This is synthetic software evidence. Structural `validate_bundle == []`
  does not establish strict physics/uncertainty eligibility; no native or
  production claim is made. No throughput improvement is claimed.
- The desk preservation fixture uses an empty synthetic roster and the real
  stage/yield/check methods, rather than launching a full production harvest.
- Arm-only timing without an existing driver log remains in memory; a crash
  can also lose member or v4-install buffered markers. No substitute timing
  sidecar is created. Retain the existing v4 CLI transcript to keep those
  post-operation receipts.
- The dynamic trace unions an actual 3-test minimal W1 delta with its prior
  committed evidence. Historical multi-module scenarios were not rerun as a
  combined trace, respecting one-module-per-process execution.
- A fresh delta review and STRICT re-registration/full-desk gate remain the
  lead's next step before capture. No signer, artifact digest, or native
  admission has been invented. R16 condition-wait integration and downstream
  off-machine harvest/backup/push are separate lead-owned work.
- No unresolved implementation question is being escalated.
- Native MLX cannot run here. The lead should run, outside this sandbox and
  with sealed-data fences intact, the relevant optional native runtime checks
  (`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx` and
  `python3.13 -B -m unittest tests.hazards.test_arm`, one module per process).
  These commands are software/native gate follow-ups, not authorization for
  a quiet-machine campaign while any agent is active. No MLX source changed.
- `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
  `tests/test_gen_state.py` are untouched; the lead owns coordination.
