# W1 phase-table move — 2026-11-11

Seat: w1-phase-table. Branch: `ops/2026-11-11-w1-phase-table`.
Base: `ff6f349d6` (W1 line plus unbound CI fixes); the requested seat branch
was already checked out and clean at intake.

RL-61 option (a) is implemented as a pure move. The W1 PREQUAL sizing check
passes without changing `joulewise/align/w1_prequal.py`. No measured bytes,
flags, verdicts, window records, receipt validation rules, or host state changed.
No new refusal codes or staging/record fields were added.

Authority: read RL-61 first, verbatim, then RL-53 through W-3, RL-35 item 4,
RL-37, RL-29, and implicit-state-machines sections 0, 4.3, 4.5, 8.1 from
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/`.
The seat-specific RL-61 brief explicitly permits the new module and the
run_night/registration edits despite the common W1 batch restrictions.
Mission M0 found no active stop card. The explicit seat brief selects this
bounded AGENT task; coordination state stays lead-owned and untouched.

## Changes and local commits

1. `2f4c1730d` — `test(align): pin R1 phase tables before RL-61 move`.
   Only `tests/align/test_r1_rehearsal.py` changed: full literal tuples for
   both include_4bit values at the default cap and `777.0`. The test passed
   on the base before any production edit.
2. `aeda76a96` — `fix(align): move R1 phase table outside W1 wait closure`.
   The move, re-exports, night-runner import, additive strict binding, and
   red-then-green re-export/binding tests.
3. This run report is committed separately after verification.

Diff against the base (additions/deletions):

| File | + / - | Change |
| --- | ---: | --- |
| `joulewise/align/apple/r1_phase_table.py` | 87 / 0 | New import-free table module; original definitions and comments |
| `scripts/align_r1_rehearsal.py` | 4 / 81 | Import/re-export the moved names; remove their original definitions only |
| `scripts/run_night.py` | 1 / 1 | One lazy import changes to the new module |
| `joulewise/align/apple/v4_registration.py` | 1 / 0 | Add the new module to `_NAMED_ARTIFACTS`; strict by default |
| `tests/align/test_r1_rehearsal.py` | 107 / 0 | Four complete literal plans plus re-export identity check |
| `tests/align/test_v4_executed_closure.py` | 5 / 0 | Require the named strict binding |

Exactly seven names moved: `phase_plan`, `COOLDOWN_AFTER_D_MAX_S`,
`GATED_D_RUNS`, `HIGH_POWER_LEGS`, `PLANNING_RUN_ORDER_C`, `PRECOOL_SUFFIX`,
and `STEP_D_NAME`. No helper or other constant moved. The driver imports
and re-exports all seven; constants have one definition. The module imports
nothing, and contains only these constants and the unchanged function.

## Failing-first and identity evidence

Before the production edits:

- `python3.13 -B -m unittest tests.align.test_r1_rehearsal.PhaseTableIdentityTests`
  passed the original literal-table test (1 test, four subcases).
- After adding the re-export test, the same command ran 2 tests and failed:
  `ImportError: cannot import name 'r1_phase_table' from 'joulewise.align.apple'`.
- `python3.13 -B -m unittest tests.align.test_w1_prequal.SizingTests`
  ran 2 tests in 26.374 s, with one failure:
  `W1-executed code waits outside the programmed span: ['scripts/align_r1_rehearsal.py']`.
- `python3.13 -B -m unittest tests.align.test_v4_executed_closure.ExecutedClosureBindingTests.test_r1_phase_table_is_named_and_strict`
  failed: `AssertionError: 'joulewise/align/apple/r1_phase_table.py' not found in (...)`.

After the move, the pinned/re-export class passed (2 tests), and SizingTests
passed (2 tests in 56.446 s). The named-strict-binding test also passes in
the closure module; its separate expected receipt failure is detailed below.

The function text (including signature, docstring, comments, body, and final
newline) is byte-identical: 2,498 bytes, SHA-256
`3bb645f577b04b4635ead71a8e088f6687bde04725243889b0543f07e3f1bda4`.
Its location changes from base driver line 495 to new module line 44.
The comparison extracted the AST function's original source lines from
`git show ff6f349d6:scripts/align_r1_rehearsal.py` and the new file, then ran
`difflib.unified_diff` on those source strings:

```text
phase_plan unified diff:
```

There were zero diff lines. An additional AST-source comparison confirmed
all six moved constant definitions are byte-identical and every remaining
driver function/assignment is unchanged. Comments were moved with their
original source blocks, without rewriting.

Compact JSON serialization of each base/new plan was also byte-identical:

| include_4bit | precool_cap_s | bytes | SHA-256 |
| --- | --- | ---: | --- |
| False | default | 1103 | `6866892cc955f6532759affe6583eab68e9765ad69248d0c555b342f0ee28e2e` |
| False | 777.0 | 1106 | `aaa3f550f2020cc7ae6d2879ab3b7ae94f8f3f338009d943f6434759166afbf8` |
| True | default | 1145 | `9ab4d4478225cf684ab091d8a9beb050dc561fef5010271a22579254038ae6d7` |
| True | 777.0 | 1148 | `65c1f76c886b10885426bd7c2bb3b30a8e6ae9b5332c5df2b83221dab0b18f87` |

The base plans were evaluated from only their AST-extracted constants and
function in memory; no real measurement input was read.

## Import closure and registration handoff

The exact requested command:

```sh
python3.13 -B -c "from joulewise.align import w1_prequal as w; from pathlib import Path; print(sorted(p for p in w.executed_closure(Path('.')) if 'r1_rehearsal' in p or 'r1_phase' in p))"
```

returns:

```text
['joulewise/align/apple/r1_phase_table.py']
```

`w1_prequal.CLOSURE_ENTRIES` is endpoint, run_night, and align_v4_session.
`executed_closure(Path('.'))` excludes `scripts/align_w1_budget_procedure.py`.
Its line 228 lazy import of `x_g_evidence` remains unchanged. The broader
registration closure intentionally includes the R1 entry points and budget
procedure; it is distinct from the W1 PREQUAL import closure.

The import census used `rg` and AST import nodes. Outside the moved driver,
the production phase_plan caller was run_night, which now uses the small
module. Existing driver-importing tests also use non-moved driver APIs, so
none can discard the driver import just by changing their table access.
No other caller was changed.

RL-29's existing watchdog addition at `928976f8c` established the pattern:
add the path to `_NAMED_ARTIFACTS`; `ARTIFACTS` includes it and `is_strict`
returns True. No receipt-check logic changes. There is no separately derived
receipt template in this code: test_v4_executed_closure calls the committed
`configs/campaigns/align_v4/registration/registration_receipt.json` its
"template". That file is expressly forbidden to this seat and stays untouched.
The dynamic trace and DEVIATIONS also stay untouched for the lane lead.
The dynamic-closure tests pass, but their committed synthetic trace still
lacks the new module: the tested minimal W1 live scenario does not exercise
the R1 refusal-summary import. The lead must regenerate the complete trace.

## Verification results

The closure/registration trio was run **one module at a time** per the
standing rule, using `python3.13 -B -m unittest <module>`:

- `tests.align.test_v4_executed_closure`: 5 tests; 1 EXPECTED failure only
  because the untouched receipt/template lacks the new bound path:

  ```text
  FAIL: test_artifact_set_has_no_duplicates_or_missing_files_and_matches_template
  AssertionError: Items in the second set but not the first:
  'joulewise/align/apple/r1_phase_table.py'
  ```

- `tests.align.test_v4_dynamic_closure`: 10 tests, PASS. No stale-trace
  assertion failed; this does not establish that the full trace is current.
- `tests.align.test_v4_registration`: 22 tests, PASS. No digest failures.

The table below records exact serial commands: each module row was run as
`python3.13 -B -m unittest <module>`. Elapsed time includes interpreter and
fixture overhead. Test runners were bounded to 1,095.18 s combined, plus
the earlier targeted/baseline checks, keeping total testing at about
20 minutes. No full-suite discovery or concurrent test modules were run.

| Module | Tests | Result | Elapsed s |
| --- | ---: | --- | ---: |
| `tests.align.test_v4_executed_closure` | 5 | FAILED (failures=1) | 26.982 |
| `tests.align.test_v4_dynamic_closure` | 10 | OK | 92.151 |
| `tests.align.test_v4_registration` | 22 | OK | 136.085 |
| `tests.test_w1_reliability` | 11 | OK | 24.191 |
| `tests.test_w1_reliability_r5` | 7 | OK | 10.541 |
| `tests.test_w1_reliability_r6` | 3 | OK | 12.065 |
| `tests.align.test_r1_rehearsal` | 76 | OK | 17.681 |
| `tests.align.test_r1_round5_exec_review` | 7 | OK | 15.786 |
| `tests.align.test_r1_round6_exec_review` | 9 | FAILED (failures=1) | 7.094 |
| `tests.align.test_r1_round6_lows` | 18 | OK | 13.322 |
| `tests.align.test_r1_round6_power` | 25 | OK | 8.196 |
| `tests.align.test_r1_round7_exec_review` | 6 | OK | 6.761 |
| `tests.align.test_r1_round7_power` | 29 | OK | 28.541 |
| `tests.align.test_r1_round7_science` | 18 | OK | 2.598 |
| `tests.align.test_r1_round8` | 21 | FAILED (failures=5) | 63.508 |
| `tests.align.test_r1_round8_exec_review` | 7 | FAILED (failures=4) | 53.484 |
| `tests.align.test_r1_runtime` | 33 | OK | 167.478 |
| `tests.align.test_r1_runtime_contract` | 11 | OK | 0.623 |
| `tests.align.test_r1_runtime_e2e` | 2 | OK | 224.678 |
| `tests.align.test_r1_turn_counts_export` | 13 | OK | 8.428 |
| `tests.align.test_r11_delta2_sol1` | 11 | OK | 11.772 |
| `tests.align.test_r11_delta2_sol2` | 10 | OK | 16.256 |
| `tests.align.test_r11_delta3_sol1` | 18 | OK | 36.898 |
| `tests.align.test_r11_delta3_sol2` | 13 | OK | 15.676 |
| `tests.align.test_r11_delta4_sol1` | incomplete | BUDGET STOP (no terminal unittest result) | 49.186 |
| `tests.align.test_w1_kit_r10` | incomplete | BUDGET STOP (no terminal unittest result) | 45.150 |

Completed module runs reported 385 tests in total (excluding incomplete
budget-stopped runs and the separate focused/baseline checks).

### Other failures: not attributed to this move

The two stale log assertions also failed with the **original base
`ff6f349d6:scripts/run_night.py` source** compiled in memory with its original
filename, through the existing `tests.test_run_night._load_driver` seam.
Other test helpers/dependencies remained at this checkout; this was a focused
base-runner replay, not a full baseline checkout test.

- `tests.align.test_r1_round6_exec_review.DeadManHighPowerTests.test_a_never_launched_w1_night_is_restored_by_its_dead_man`
  expects `ac powermode exit restore (dead_man)`; the log says
  `ac powermode close: restore Automatic; network time unchanged:`.
  Base replay: 1 test, 0.731 s, FAILED (failures=1).
- `tests.align.test_r1_round8_exec_review.NightUnprovenNonInterruptCloseTests.test_an_exception_escaping_the_chain_wait_restores_nothing`
  expects `exception escaping the chain wait (RuntimeError: chain wait broke)`;
  the log instead records `chain_termination` with `path: exception`,
  `error: RuntimeError: chain wait broke`, `proven: false`, and restore deferred.
  Base replay: 1 test, 1.203 s, FAILED (failures=1).

Base replay commands were `python3.13 -B
/private/tmp/w1-phase-table-baseline-log-test.py <full-test-id>` for each
of these IDs separately. That temporary harness compiled `git show
ff6f349d6:scripts/run_night.py` into a module whose `__file__` was the real
checkout driver path, replaced only the test helper loader, and retained its
normal clean-dwell mocks. Production files were never swapped or reverted.

The following eight process/signal assertions remain unqualified in this
sandbox. Relevant logs report:

```text
census_exit_3: sysmon request failed with error: sysmond service not found
pgrep: Cannot get process list
```

The chain therefore reports `proven: false` and defers restoration. The
R1 descendant assertions also lack a usable process census. These failures
need native rerun; I did not reproduce each against the base. The affected
termination/close functions are byte-identical to the base, and no process
or restore code was changed in this seat.

| Test (module-relative) | Assertion |
| --- | --- |
| `test_r1_round8.NightInterruptTests.test_sighup_while_the_chain_runs_stops_it_and_restores` | `"proven": true` absent |
| `test_r1_round8.NightInterruptTests.test_sigint_on_a_chain_that_ignores_term_is_killed_and_restored` | `"proven": true` absent |
| `test_r1_round8.NightInterruptTests.test_sigterm_while_the_chain_runs_stops_it_and_restores` | `"proven": true` absent |
| `test_r1_round8.R1InterruptTests.test_the_runtime_and_its_descendants_are_proven_gone_before_the_restore` | `AssertionError: [] is not true` |
| `test_r1_round8.TerminateTreeTests.test_an_orphan_holding_the_pipe_neither_hangs_nor_survives` | `AssertionError: False is not true` |
| `test_r1_round8_exec_review.NightRepeatedSignalTests.test_signals_during_the_termination_do_not_cut_it_short` | `"proven": true` absent |
| `test_r1_round8_exec_review.NightLockHoldingEscapeeTests.test_an_escapee_that_holds_the_lock_sees_no_restore` | `could not be retaken` absent; earlier group proof already failed |
| `test_r1_round8_exec_review.R1RepeatedSignalTests.test_signals_during_the_runtime_kill_do_not_cut_the_close_short` | `AssertionError: False is not true` (termination proof) |

### Budget-stopped and unrun checks

`tests.align.test_r11_delta4_sol1` was stopped after 49.186 s when the main
1,050 s runner budget expired. `tests.align.test_w1_kit_r10` was stopped
after 45.150 s in the final reserved window. Neither produced a terminal
unittest result; they are **incomplete**, not passing tests or proven
regressions. No tests were run after the final reserved window closed.

The AST census found 75 direct test-module importers of the three edited
existing production modules. All phase-plan/moved-constant consumers were
run; the broader requirement to complete every importing module remains
incomplete. The following 52 direct-import modules were not run in
full; `test_w1_prequal.SizingTests` was separately run and passed as above.
Each outstanding full-module command is `python3.13 -B -m unittest <module>`:

```text
tests.align.test_r11_delta4_sol2
tests.align.test_r11_delta5_sol1
tests.align.test_r11_delta_sol1
tests.align.test_r11_delta_sol2
tests.align.test_r11_review_sol1_witnesses
tests.align.test_r11_review_sol2
tests.align.test_smoke_delta_sol1
tests.align.test_smoke_delta_sol2
tests.align.test_smoke_review_sol1
tests.align.test_smoke_review_sol2
tests.align.test_thermal_desk
tests.align.test_timing_receipts
tests.align.test_timing_receipts_opus_witnesses
tests.align.test_v4_next_arm_packet
tests.align.test_v4_r11
tests.align.test_v4_receipt_tiers
tests.align.test_v4_series
tests.align.test_v4_series_e2e
tests.align.test_v4_w1_blockers
tests.align.test_v4_w1_synthetic
tests.align.test_w1_prequal
tests.align.test_w1_smoke
tests.align.test_w1bm_sol1
tests.align.test_w1bm_sol2
tests.b6.test_round2_review_fixes
tests.test_arm_retry
tests.test_b6_machine_test
tests.test_evidence_arm_sequence
tests.test_gen_derivation_night
tests.test_gen_evidence_night
tests.test_gen_g2a_window
tests.test_install_night_agent
tests.test_magistrate_watchdog_v5
tests.test_network_time_off
tests.test_night_gate
tests.test_quiet_predicate_campaign
tests.test_run_night
tests.test_run_night_probe_cadence
tests.test_run_night_probe_worker_cadence
tests.test_sample_quiet_predicate_evidence
tests.test_v5_block4_replay
tests.test_v5_block4_x1
tests.test_v5_block4_x10
tests.test_v5_block4_x12b
tests.test_v5_block4_x16
tests.test_v5_block4_x2
tests.test_v5_block4_x4
tests.test_v5_block4_x7
tests.test_v5_qualification_plan
tests.test_w1_reliability_r3
tests.test_w1_reliability_r4
tests.test_w1_reliability_r7
```

The original reliability module and refusal-summary modules r5/r6 passed.
The other direct reliability importers r3/r4/r7 are in the unrun list.
The dynamically loaded driver module `tests.test_b5_driver` was also queued
but not reached. Raw transient logs and serial command results are at
`/private/tmp/w1-phase-table-logs/`; the persistent findings and counts are
recorded here. `git diff --check` passed.


## Limits, review, and next exact step

Only synthetic tests and repository code/plan structure were used. No
external network command, model download, real host-state setter, or
measurement pipeline was run. No tool was directed to real custody,
restricted data, or forbidden home-directory paths; absolute data paths in
repository text were not followed.
No full-suite discovery was run. No new test module was added, so
`scripts/test_timings.json` did not change. RUN_STATE, TASK_QUEUE, the state
kernel, test_gen_state, thermal_gates, r1_runtime and its configuration,
real receipt, dynamic trace, and DEVIATIONS are unchanged.

The full direct-import census could not be completed within the requested
test-time budget; the exact unrun commands are listed above.
This seat did not perform independent cold review or native hardware
validation. The lane lead must cold-review the final diff, integrate the
matching R1 driver/runtime/thermal-gate/config/table bytes, add the required
deviation row, regenerate the trace and receipt at integration, and rerun
the closure/registration gates. RL-61 condition 13 requires identity with
the files at the commit that produced the entered R1 slots, with that commit
named by the slots. This seat does not sign the receipt. Implementation and
verification of the signing-time condition-13 comparison are outside this
seat's additive-binding-only registration edit; the lane lead must ensure
that comparison exists and passes.
Rerun the process-census/signal test modules listed above outside this
sandbox, whose `pgrep` cannot obtain the process list. These are native
process checks with synthetic workloads, not live measurement evidence.
Then run PREQUAL plus the W1 smoke at the registered integrated head,
remotely on the measurement Mac under a lead-controlled quiet session.
Confirm the new module is installed and R1 outcome/refusal vocabulary is
unchanged. This pure stdlib move introduces no MLX code or native MLX test;
no Metal/device validation is claimed here.

Open scope question: none. Integration gates above remain lead-owned;
this local branch alone is not evidence that W1 is registered or armable.
