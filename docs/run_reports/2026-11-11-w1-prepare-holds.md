# W1 prepare stack and held-window arm checks

Seat: `w1-prepare-holds`. Branch: `ops/2026-11-11-w1-prepare-holds`.
Base: `e66fdc3d51ce2497afdd4d54597f9dddc483759a`.
The starting worktree was clean. This explicit bounded AGENT brief overrides
queue selection, coordination writes and the full-suite instruction. No active
stop card. No network, model download, measurement, analysis pipeline, host
setter, real custody access, push, or subagent/consult. All new evidence is
synthetic; native behavior remains PROVISIONAL.

Read the armcheck/weight reports and session code, M0 and applicable repository
conventions, RL-73, RL-71, RL-65's hold rule, RL-53 through W-3, RL-35 item 4,
RL-37, and audit sections 0, 4.3, 4.5 and 8.1 from the local audit ref. Read the
speed toolbox from `origin/main`. No throughput optimization, batching or
decision cache is introduced. A broader RL-53 extraction emitted later policy
sections too; no sealed study files or outcomes were consulted.

## Changes and refusal records

Only `scripts/align_v4_session.py` changes among bound files.

- RL-73: `runtime_stack_preflight(python, identity_pins, runner=..., reader=...)`
  calls the existing `joulewise.flags.collect.runtime_versions` by default.
  Its argument is `<state.measurement_root>/.venv/bin/python` (the staged
  measurement view), matching the night /
  harvest interpreter convention (`align_pilot_session.py:329` and
  `flags/collect.py:1148`). The collector uses importlib.metadata and
  platform.python_version, never imports MLX or loads a model. It returns
  `{python, packages}`; missing installed distributions have null versions.
  Prepare reads the selected registered `identity_pins.json.runtime_versions`,
  compares Python and the union of package keys, and records registered,
  observed, ok, reasons and elapsed_s in `runtime_stack_preflight`. Differences
  name each package: `runtime_stack_preflight: differs: <name>: registered <a>
  installed <b>`. Missing keys use `<missing>`; null, empty, malformed or
  unreadable versions also produce `runtime_stack_preflight: unreadable: ...`.
  Work completes before the frequency preflight and any arm/dwell.
- The arm carries this block verbatim as `runtime_stack`, or validates
  `--runtime-stack-attested` JSON with a named operator, registered and observed
  `{python, packages}` blocks, or records `source: not_recorded_by_prepare`.
  Attested registered versions must match the actual pins. An attested
  difference/unreadable block refuses before the installer. There is no
  arm-time probe or library import. Existing weight evidence/refusals remain.
- The weight function now takes explicit `(registration_dir, members,
  identity_fn=..., reader=...)` inputs. `_prepare_weight_digests` is the small
  state adapter; the existing comparison logic, grouping, digest and per-file
  checks are retained. R1 can call either plain preflight unchanged.
- RL-62/71/73: a prepare mismatch records `holds_previous_window` in this
  prepare's session.json and appends the same statement to the exception text,
  held until the files/stack change time is established. The id is taken from
  the source checkout's authenticated HEAD `series/state.json` previous-record link; unavailable
  identity is null. This never writes the previous record. Unreadability alone
  does not assert a known mismatch.
- RL-65/71: `HELD_WINDOW_REASONS` contains the three unambiguous harvest codes:
  `records.source_changed_during_harvest`, `roster.no_science_bundles`, and
  `precheck.certain_exclusion`. `held_window_check` uses the arm's rebuilt
  packet identities, `GitEvidence`, `WindowRecord.final_evidence` and
  `WindowRecord.source('exclusions')`. Record digest and window must agree with
  the rebuilt packet. The ledger's authenticated last_passed_record.final_record also binds a
  successor's previous_final exactly as the packet's last_desk_state does.
  No custody locator is followed. The arm records
  `held_window_check` before the meter probe and dwell stamp. A held final
  harvest refuses with `held_window: <window>: <reason>[, ...]: no signed
  ruling`. Unreadable authentication/reasons refuse as `held_window:
  unreadable: ...`. A non-final previous window says exactly `previous window
  not final: hold check deferred to its finality`; existing finality/k+2 gates
  remain. A no-capture record final without harvest has no harvest hold.
- The packet accepts only `zero_capture_escalation` and
  `u1_u3_fail_escalation` resets (`align_v4_next_arm_packet.py:982-983`). It is
  outside scope and unchanged. The authorized fallback `--held-window-ruling`
  reads the same row shape with `resets: held_window_release`, the held
  `after_window`, nonempty ruling_id, and `kit.valid_lead_signature`. Its text
  is a `{path, sha256}` source authenticated at the rebuilt packet's
  series_commit and must be nonempty. The arm records the validated row,
  source `arm_cli` and text digest. Invalid signatures, wrong windows/reset
  words and bad text digests refuse. The lead still owes packet support for
  this reset word if ledger-based releases are desired.
- PREQUAL has named `runtime-stack-preflight` and `held-window` cases, each
  with a passing synthetic control and a tripped refusal. Existing PREQUAL
  and prepare fixtures supply explicit synthetic stack probes. The owed
  deadman_epoch parser test raises from a synthetic installed module and
  expects `parse: malformed`; the existing parser already passes this test.

## Stopped sub-item: RL-73's desk mismatch signal

NEEDS_RULING; no generic `model.identity_mismatch` hold was added.

On this supplied base `docs/align/v4/DEVIATIONS.md` contains no
`IDENTITY-FLAGS` row. `joulewise/b5/harvest.py:6026-6033` loads the registered
units; `6088-6092` emits member-level `model.identity_mismatch` if either the
model artifact or runtime identity digest differs. The v4 pins' units have
`stack_identity: {}` and `runtime_stack_unobserved`, with no
`runtime_identity_sha256`. Therefore that member code does not establish a
readable runtime-stack-versus-registration difference on this base.
The arm collector also emits `model.identity_mismatch` for several distinct
checks (`flags/collect.py:1049,1073,1087,1114,1133,1180,1205`).
`flags/exclusions.py:225-227,398-399` collapses EXCLUDE_WINDOW flags to reason
codes without preserving member scope or observed.check. Its final
`model.identity_mismatch` reason cannot distinguish these paths.
`model.stack_differs_from_registered` has no producer in the inspected harvest
or collector. Inferring a hold from the generic code would guess exactly where
the brief requires this sub-item to stop.

Question: which authenticated final source/signal should distinguish a real
member runtime-versus-pins difference on this branch?
Options: integrate the missing identity/deviation work with an explicit
harvest signal, or expand packet/source work to retain authenticated detailed
flags and define the exact discriminator. Recommendation: the former, then
add only the agreed signal to the hold constant with failing-first tests.
Blocked work: RL-73 item 4's desk-runtime hold only; the three RL-71 holds and
prepare runtime check are independently implemented.

## Failing-first evidence

Test-only commit `73eff70c1` precedes implementation. Commands/logs under
`/private/tmp/w1-prepare-holds-checks/` are local diagnostics, not custody.

Initial focused red command used `python3.13 -B -m unittest` with
RuntimeStackTests, HeldWindowTests, PreInstallTests, the two new arm
integration methods and the new deadman parser method. Result:

```text
AttributeError: module 'scripts.align_v4_session' has no attribute 'runtime_stack_preflight'
TypeError: weight_digest_preflight() got an unexpected keyword argument 'reader'
AttributeError: module 'scripts.align_v4_session' has no attribute 'held_window_check'
error: unrecognized arguments: --runtime-stack-attested stack.json --held-window-ruling ruling.json
AssertionError: ValueError not raised
- ['watchdog', 'meter', 'write', 'stamp']
+ ['held', 'watchdog', 'meter', 'write', 'stamp']
Ran 13 tests in 11.460s
FAILED (failures=3, errors=17)
```

The named PREQUAL witness failed before either check was registered:
`Ran 1 test in 2.335s; FAILED (failures=2)`.
The initial deadman stub omitted Storage.dry_run/would_write; that fixture was
completed before the final witness. No production parser change was needed.

A first implementation sweep ran 24 focused tests in 46.284s with one failure:
the prior id was null because GitEvidence.commit requires a full object id,
not HEAD. Resolve HEAD first, then authenticate the ledger/link. The same test
also needed its mock moved to the new prepare state adapter.
A late-final witness first failed (1 test in 9.857s): the previous record was
incorrectly deferred although its authenticated successor supplied final
exclusions. The ledger final_record binding now applies before finality.
The final HeldWindowTests repeat passed 5 tests in 54.749s.

Source review then aligned the probe with the staged state.measurement_root
interpreter actually used by install/desk (rather than the incoming source
root), and the previous-window lookup with source_measurement_root. The
prepare witness distinguishes those paths.

Two additional edge witnesses were run red before their fixes:
`Ran 2 tests in 0.020s; FAILED (failures=2)`: empty installed package maps did
not enumerate every missing package; Python missing on both sides was accepted.
The final comparison handles both explicitly.

## Verification and handoff

Final commands/results, exact diff counts and commit ids follow below.
No full suite or pytest. The serial regression tranche runs with synthetic HOME,
host-state path, no system/global Git config, no lazy fetch, offline model
settings and unset JW_* opt-ins. Timeouts are incomplete results, never passes.

Native checks owed to the lead, remotely after integration/registration and
outside a quiet campaign:

1. Use a disposable qualification prepare on the installed measurement
   checkout. Verify the exact measurement interpreter, all seven package
   versions and Python against the final registered pins, elapsed evidence,
   and completion before any dwell. No Metal/model execution is needed for
   this metadata probe. Actual installed versions were not checked here.
2. With synthetic pins/metadata, trip one version difference, a missing/null
   package and an unavailable interpreter; inspect the persisted refusal and
   previous-window statement. Exercise a synthetic weight mismatch too; prove
   previous record bytes stay unchanged.
3. Exercise prepare-carried, named-attested and legacy evidence; a mismatching
   attestation must refuse, never call the installer, and never probe at arm.
4. Arm on a synthetic authenticated final record for each of the three held
   reasons, the inert cell reason, and a non-final record. Inspect arm evidence
   and ordering before meter/dwell; release a held qualification record only
   with a valid signed ruling/text source. Exercise invalid signature/window/
   text digest refusals.
5. Cold review, the lead's deviation row, trace regeneration, STRICT receipt,
   PREQUAL and smoke run on the final integrated bytes. Add RL-73's agreed
   desk-runtime signal before treating that sub-item as complete. This seat
   does not admit the batch or satisfy any live gate.

No MLX code changed and no Metal availability is claimed. The report's fixture
passes cannot qualify actual host installation, stack or model identity.

## Final serial results

Text search found 54 importer modules; 54 were attempted as full modules,
one per invocation except the explicitly requested closure trio. Full importer
inventory and exact logs are in `/private/tmp/w1-prepare-holds-checks/`. The larger importer modules
received 8-second caps; selected smaller modules received 15 seconds. Those
short caps satisfy the bounded serial attempt inventory, not complete
regression coverage. The new named PREQUAL cases ran separately to completion.

Every row below uses `python3.13 -B -m unittest` followed by the listed
arguments. TIMEOUT means no completed result/count is claimed. The mutant
row uses the isolated local `mutant.py` script instead, with an expected
assertion failure proving rejection.

| Arguments after command prefix | Result | Process wall (s) |
|---|---|---:|
| `tests.align.test_v4_arm_watchdog_check` | FAIL; 68 tests; errors=2 | 89.300 |
| `tests.align.test_w1_prequal.ArmCliTests.test_named_runtime_stack_and_held_window_cases` | FAIL; 1 tests; failures=1 | 27.604 |
| `tests.align.test_v4_arm_watchdog_check` | PASS; 68 tests | 83.766 |
| `tests.align.test_v4_arm_watchdog_check.HeldWindowTests.test_previous_final_sources_can_ride_in_authenticated_successor` | FAIL; 1 tests; failures=1 | 14.659 |
| `tests.align.test_v4_arm_watchdog_check.HeldWindowTests` | PASS; 5 tests | 58.204 |
| `tests.align.test_w1_prequal.ArmCliTests.test_named_runtime_stack_and_held_window_cases tests.align.test_w1_prequal.ArmCliTests.test_named_weight_digest_check_passes_matching_and_trips_mismatch` | PASS; 2 tests | 58.306 |
| `tests.align.test_v4_executed_closure tests.align.test_v4_dynamic_closure tests.align.test_v4_registration` | FAIL; 36 tests; failures=2 | 202.872 |
| `tests.align.test_harvest_off` | TIMEOUT; incomplete | 8.030 |
| `tests.align.test_harvest_off_review_sol1` | TIMEOUT; incomplete | 8.045 |
| `tests.align.test_harvest_off_review_sol2` | TIMEOUT; incomplete | 8.011 |
| `tests.align.test_km003c` | PASS; 25 tests | 10.598 |
| `tests.align.test_merge_c84_sol` | TIMEOUT; incomplete | 8.014 |
| `tests.align.test_r0_host` | TIMEOUT; incomplete | 8.019 |
| `tests.align.test_r11_delta3_sol1` | TIMEOUT; incomplete | 8.015 |
| `tests.align.test_r11_delta3_sol2` | TIMEOUT; incomplete | 8.288 |
| `tests.align.test_r11_delta4_sol1` | TIMEOUT; incomplete | 8.012 |
| `tests.align.test_r11_delta4_sol2` | TIMEOUT; incomplete | 8.011 |
| `tests.align.test_r11_delta5_sol1` | TIMEOUT; incomplete | 8.008 |
| `tests.align.test_r11_delta5_sol2` | TIMEOUT; incomplete | 8.006 |
| `tests.align.test_r11_delta6_sol1` | TIMEOUT; incomplete | 8.130 |
| `tests.align.test_r11_delta6_sol2` | TIMEOUT; incomplete | 8.085 |
| `tests.align.test_r11_delta_sol1` | FAIL; 8 tests; failures=1 | 6.929 |
| `tests.align.test_r11_delta_sol2` | PASS; 6 tests | 8.896 |
| `tests.align.test_r1_round6_exec_review` | FAIL; 9 tests; failures=1 | 5.817 |
| `tests.align.test_r1_round6_power` | FAIL; 25 tests; failures=1, errors=6 | 6.744 |
| `tests.align.test_r1_round7_install` | TIMEOUT; incomplete | 8.012 |
| `tests.align.test_r1_round7_power` | TIMEOUT; incomplete | 8.015 |
| `tests.align.test_r1_round8` | TIMEOUT; incomplete | 8.014 |
| `tests.align.test_smoke_delta4_sol1` | TIMEOUT; incomplete | 8.012 |
| `tests.align.test_smoke_delta4_sol2` | TIMEOUT; incomplete | 8.013 |
| `tests.align.test_smoke_delta_sol1` | TIMEOUT; incomplete | 8.017 |
| `tests.align.test_smoke_delta_sol2` | TIMEOUT; incomplete | 8.006 |
| `tests.align.test_smoke_review_sol1` | TIMEOUT; incomplete | 8.022 |
| `tests.align.test_smoke_review_sol2` | TIMEOUT; incomplete | 8.018 |
| `tests.align.test_timing_receipts` | TIMEOUT; incomplete | 8.083 |
| `tests.align.test_v4_dc_sealing` | PASS; 2 tests | 3.265 |
| `tests.align.test_v4_disclosure_only_desk` | TIMEOUT; incomplete | 8.012 |
| `tests.align.test_v4_kit` | TIMEOUT; incomplete | 8.070 |
| `tests.align.test_v4_next_arm_packet` | TIMEOUT; incomplete | 8.007 |
| `tests.align.test_v4_next_arm_packet_opus_witnesses` | TIMEOUT; incomplete | 8.013 |
| `tests.align.test_v4_powermode_record` | PASS; 9 tests | 4.303 |
| `tests.align.test_v4_r11` | PASS; 27 tests | 5.666 |
| `tests.align.test_v4_record_binding` | TIMEOUT; incomplete | 8.112 |
| `tests.align.test_v4_series` | TIMEOUT; incomplete | 8.019 |
| `tests.align.test_v4_series_e2e` | TIMEOUT; incomplete | 8.016 |
| `tests.align.test_v4_series_r20` | TIMEOUT; incomplete | 8.017 |
| `tests.align.test_v4_w1_blockers` | TIMEOUT; incomplete | 8.033 |
| `tests.align.test_v4_w1_synthetic` | TIMEOUT; incomplete | 8.016 |
| `tests.align.test_w1_kit_r10` | TIMEOUT; incomplete | 8.012 |
| `tests.align.test_w1_prequal` | TIMEOUT; incomplete | 8.099 |
| `tests.align.test_w1_smoke` | TIMEOUT; incomplete | 8.012 |
| `tests.align.test_w1bm_sol1` | TIMEOUT; incomplete | 8.087 |
| `tests.align.test_w1bm_sol2` | TIMEOUT; incomplete | 8.038 |
| `tests.test_w1_reliability_r2` | TIMEOUT; incomplete | 8.007 |
| `tests.test_w1_reliability_r3` | FAIL; 14 tests; errors=2 | 5.397 |
| `tests.test_w1_reliability_r4` | TIMEOUT; incomplete | 8.020 |
| `tests.test_w1_reliability_r5` | PASS; 7 tests | 7.219 |
| `tests.test_w1_reliability_r7` | PASS; 10 tests | 4.429 |
| `tests.align.test_v4_kit.W1DiskGateTests.test_cli_install_requires_and_forwards_the_disk_config` | PASS; 1 tests | 4.206 |
| `tests.align.test_v4_arm_watchdog_check.RuntimeStackTests tests.align.test_v4_arm_watchdog_check.PreInstallTests tests.align.test_v4_arm_watchdog_check.RemoteProbeTests.test_direct_parser_rejects_installed_deadman_epoch_error tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests.test_runtime_stack_prepare_legacy_and_attestation_sources` | PASS; 10 tests | 5.425 |
| `tests.align.test_v4_registration.RegistrationTests.test_arm_derives_float_across_a_window_from_its_own_smc_journal tests.align.test_v4_registration.RegistrationTests.test_arm_records_battery_and_refuses_missing_attestation` | PASS; 2 tests | 10.122 |
| `tests.align.test_r11_delta_sol1` | PASS; 8 tests | 6.286 |
| `tests.align.test_r1_round6_power` | FAIL; 25 tests; errors=6 | 5.064 |
| `tests.test_w1_reliability_r3` | PASS; 14 tests | 5.868 |
| `tests.align.test_v4_registration` | PASS; 22 tests | 66.645 |
| `/private/tmp/w1-prepare-holds-checks/mutant.py` | EXPECTED mutant rejection; 1 assertion failure | 3.395 |

`arm-final` (68 tests) preceded the successor-final binding and staged-view
argument correction. Those final deltas are covered by `late-final` (5 tests)
and `final-main` (10 tests); a second full arm-module run was not made. The
PREQUAL controls use equal source/view paths; final-main distinguishes them.

The initial closure trio ran all 36 tests: executed closure/dynamic closure
passed, and two battery-only registration fixtures failed because their fake
packet identities are not Git evidence. These are **not EXPECTED digest
failures**. Both fixtures now explicitly mock the unrelated held check, and
the final registration run below supersedes those failures. No stale trace or
receipt digest message was emitted; there is no EXPECTED digest text to quote.

The same explicit synthetic hold seam repairs the existing history witness
and the round-6 no-install restore witness. Series replay fixtures already
replace packet authentication and now also isolate the held check. The
frequency-prepare fixture supplies its staged measurement_root. Original
battery, history, restore and frequency assertions remain. Their completed
final repeats are listed above; series full modules remain timed out.

Remaining completed failures are the prior lane failures, not relabelled
EXPECTED: `test_r1_round6_exec_review` has the deadman log wording assertion
(`ac powermode exit restore (dead_man)` versus `ac powermode close: restore
Automatic; network time unchanged`); the final `test_r1_round6_power` has six
errors, three `FakeArmHost.__call__() got an unexpected keyword argument
'check'` and three `KeyError: 'plan_path'`. The preceding weight-digest
report independently reproduced these classes against its base. This seat
observed matching diagnostics but did not independently re-run that base
witness; baseline attribution relies on that earlier recorded evidence.
The newly introduced no-install held-check failure is fixed; its final
module repeat retains only those six errors.

Recorded regression process wall: 1032.461 seconds.
The initial red/focused invocations outside this ledger add about 65-75
seconds (including interpreter starts); total test execution remains below
the approximately 20-minute cap. The initial red PREQUAL command was started before the preceding red
process had been polled to completion. Both finished quickly; whether they
briefly overlapped is not established. All subsequent commands used the
explicit serial runner. No full suite, pytest, native Metal, real meter or
real custody test was run.

## Final diff and local commits

| File | + / - versus base | Purpose |
|---|---:|---|
| `joulewise/align/w1_prequal.py` | 58 / 1 | Unbound synthetic PREQUAL cases and inputs |
| `scripts/align_v4_session.py` | 226 / 18 | Only bound edit: prepare runtime/hold evidence, reusable weight inputs, arm hold/ruling |
| `tests/align/test_r11_delta_sol1.py` | 2 / 1 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_r1_round6_power.py` | 1 / 0 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_v4_arm_watchdog_check.py` | 259 / 8 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_v4_kit.py` | 2 / 1 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_v4_next_arm_packet.py` | 1 / 1 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_v4_registration.py` | 4 / 2 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_v4_series.py` | 5 / 1 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_v4_series_e2e.py` | 5 / 1 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/align/test_w1_prequal.py` | 9 / 0 | Synthetic witnesses, API adaptation or explicit isolation |
| `tests/test_w1_reliability_r3.py` | 3 / 2 | Synthetic witnesses, API adaptation or explicit isolation |
| This report | new | Authority, red/green evidence, complete attempt inventory and handoff |

Commits: `73eff70c1` (test-only initial red), `3962cb34e` (implementation
and primary fixture updates), followed by the local report/fixture-isolation
commit whose id is returned in the final handoff. No push.

Final in-memory compilation of all changed Python files and `git diff
--check` pass. No new test module, so `scripts/test_timings.json` is unchanged.
Protected coordination, protocol, registration, receipt, trace, watchdog,
night-driver and B5-driver paths are unchanged. No raw evidence was edited.

Next exact step: the lead supplies/integrates the authoritative RL-73
desk-runtime signal (NEEDS_RULING above), finishes TIMEOUT modules under a
fresh authorized budget and dispositions the two prior failing modules.
Then cold-review/integrate, add the deviation row, regenerate trace/receipt,
and run remote native qualification/PREQUAL/smoke at the final registered
head, with any measured smoke in a clean lead-controlled quiet session
after agents stand down. The signed-file release route is implemented; ledger
reset support is a separate lead-owned packet follow-up. No batch admission or live gate is
claimed here.
