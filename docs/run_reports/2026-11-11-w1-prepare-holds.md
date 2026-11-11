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

## Round 2

Seat `w1-prepare-holds`, branch `ops/2026-11-11-w1-prepare-holds-r2`,
base `bcc051881`. Clean starting tree. The explicit brief owns task intake;
coordination state remains lead-owned and unchanged. Read RL-79 verbatim
from the local audit ref (only its section), RL-53, RL-35 item 4, RL-37,
the four requested state-machine audit sections, M0, repository conventions,
and the local-ref speed toolbox. RL-79 withdraws RL-73 item 4, so the round-1
request for an additional desk-runtime hold signal is superseded. The three
harvest reason codes remain unchanged.

The sole bound edit remains `scripts/align_v4_session.py`. The held check
rebuilds and SHA-256-checks every record in the rebuilt packet's chronological
`window_chain`, checks link/tail identities, and applies `bind_final` between
immediate successors, matching packet lines 924-954. Its existing authenticated
ledger/successor binding for the last record is retained. R1/W1 and development
records are skipped: packet lines 1010-1012 omit R1/W1 from series history,
and 956-959 restrict calibration contributions. Every other final harvest's
exclusions are read through `WindowRecord.source`; nonfinal records are listed
as deferred. The arm's `held_window_check.windows` carries each window's
`final`, `held_reasons`, `released_by` (ruling ID or null), and status.

`--held-window-ruling` is repeatable. Each file is authenticated with the same
`GitEvidence`, at `series_commit`, or, if absent there, the latest regular blob
found in that commit's ancestor history. A current committed nonregular file
is refused; a historical version cannot override a differing current blob.
Repository-relative paths and absolute paths inside the measurement repository
are supported. Symlink working paths are refused. Working bytes must equal
the committed blob. The signed ledger row shape/reset/signature and text-source
digest checks remain. Each arm-carried ruling records repository path, commit,
file SHA-256, original row fields, full `text_sha256`, decoded `text_content`
(up to 16 KiB, preserving UTF-8 boundaries), and `truncated`. A wrong-window
ruling releases nothing for the held window.

Refusals retain the existing prefixes: one
`held_window: <window>: <reasons>: no signed ruling` per unreleased held window;
authentication, path, modified/uncommitted file, malformed row/signature or text
errors add `held_window: unreadable: <exception>: <detail>`. These are persisted
inside the arm's held-check evidence and copied to its refusal reasons before
meter/dwell. No earlier window record, measured byte, flag, verdict or receipt
check is changed. `align_v4_next_arm_packet.py` is unchanged. The unbound
PREQUAL case now uses final C1 supplied by provisional C2 while arming C3.

### Round 2 failing-first evidence

Test-only commit `081f7f457` precedes implementation. Local diagnostic logs and
runner scripts are under `/private/tmp/w1-prepare-holds-r2-checks/`, not custody.
The initial broad red invocation was interrupted (no completed result claimed).
The completed `red-focused` base run reported `Ran 5 tests in 43.785s; FAILED
(failures=3, errors=2)`, including:

```text
AssertionError: True is not false                 # uncommitted ruling accepted
KeyError: 'rulings'                               # no carried ruling text list
KeyError: 'windows'                               # no per-window evidence
AssertionError: PosixPath('second.json') != [PosixPath('ruling.json'), PosixPath('second.json')]
```

Its first required-chain failure was a fixture error (`None != 'C3'`): the
fixture supplied a fabricated current artifact digest, making the independent
full-desk gate reject provisional C2. The fixture now uses `Scenario.build()`'s
actual synthetic artifact digest. A second base replay extracts only the
unaltered `held_window_check` function from commit `081f7f457`, compiles its AST
into the imported session module, and runs the corrected tests. No source file
is swapped. `red-history`: `Ran 3 tests in 35.950s; FAILED (failures=3)`:

```text
AssertionError: True is not false : {'ok': True, 'window': 'C2', 'held_reasons': [], 'reasons': [], 'ruling': None, 'final': False, 'status': 'previous window not final: hold check deferred to its finality', 'finality_reason': 'no final sources'}
# Repeated for a wrong-window ruling: C1's hold was still missed.
# Two-window test: base reports only C2, omitting C1's refusal.
```

The first green attempt had loaded the old fixture before its correction and
is superseded below. Interrupting its runner left its detached child alive;
the base-history replay briefly overlapped that test child. An attempted signal
to that exact test process was denied by the sandbox; no escalation or bypass
was attempted. Subsequent invocations wait for completion and remain serial.
This was a test-control mistake, not evidence of a pass. No measurement job
was signalled, inspected or otherwise touched.

The superseded first green child eventually completed: `Ran 12 tests in
200.602s; FAILED (failures=3)`. All three failures used the old fabricated
artifact-digest fixture (missing chain or C3 identity), rather than the final
fixture that the corrected base replay exercises. Subsequent final results
are recorded below.

### Round 2 native handoff and limits

The lead must exercise, remotely on the measurement Mac after integration and
registration, a disposable synthetic qualification series: C1 finalized by
C2's `previous_final`, C2 still provisional, C3 arm refused specifically for
C1; a valid committed C1 ruling admitting that hold; wrong-window, modified,
uncommitted and bad-signature rulings refusing; two held windows requiring
two repeated ruling options. Inspect the staged arm JSON for each window's
finality/deferred state, release IDs, committed ruling path/digest/row and text,
and text truncation/full digest. Prove the check finishes before meter/dwell,
no earlier record changes, and host installation remains refused when a hold
is unanswered. Exercise the ancestor-file case and PREQUAL's named held-window
case on the final installed bytes. None of these fixture results qualifies a
live host or satisfies the native gate. No MLX code changed or native Metal
execution was attempted. The lane still owns cold review, deviation row,
trace/STRICT receipt regeneration, PREQUAL and smoke. No integration, batch
admission, push or live/hardware validation is claimed.

There is no remaining contract question for this seat: RL-79 supplies the
round-1 ruling. Historical-file authentication is explicitly limited to the
packet series commit's ancestry; unrelated refs/working HEAD cannot authorize
a ruling. Verification limitations and any incomplete importer modules follow
in the final result table. No new test module was added, so test timings are
unchanged. The only repository writes are the five paths in the final diff.

### Round 2 final diff and completed focused checks

Against `bcc051881`:

| Path | Added / removed | Change |
|---|---:|---|
| `scripts/align_v4_session.py` (only bound file) | 102 / 47 | Full-chain hold check, authenticated repeated ruling files and carried text |
| `joulewise/align/w1_prequal.py` | 12 / 5 | C1-final/C2-provisional/C3-arm synthetic hold witness |
| `tests/align/test_v4_arm_watchdog_check.py` | 152 / 15 | Required history/release/file/text witnesses and compatible committed fixtures |
| `tests/align/test_r1_round6_power.py` | 1 / 0 | Isolate the unrelated held check in the lock-only fixture |
| This run report | append only | Round 2 evidence and handoff |

Local commits: `081f7f457` (test-only red), `7d472758a` (implementation,
corrected fixtures and PREQUAL). The final report commit is returned in the
handoff. Nothing was pushed.

Commands use `python3.13 -B -m unittest` with the arguments below. Timings in
the serial ledger include interpreter startup; unittest's own timings are:

- `tests.align.test_v4_arm_watchdog_check`: **76 passed**, 250.508 s.
- `tests.align.test_w1_prequal.ArmCliTests.test_named_runtime_stack_and_held_window_cases`:
  **1 passed** (two named PREQUAL subcases), 60.052 s.
- Final working-file guard check: **3 passed**, 49.262 s, using these arguments:

```text
tests.align.test_v4_arm_watchdog_check.HeldWindowTests.test_uncommitted_modified_and_outside_repository_rulings_refuse
tests.align.test_v4_arm_watchdog_check.HeldWindowTests.test_ruling_from_series_ancestor_is_authenticated_and_carried
tests.align.test_v4_arm_watchdog_check.HeldWindowTests.test_valid_signed_ruling_answers_hold_and_is_recorded_invalid_refuses
```

The full arm run had imported the function just before the final regular-file
working-path guard was added; these last three tests exercise the final bytes.
Changed Python files also compile in memory, and `git diff --check` passes.
No full suite, pytest, native host commands, measurement, model download,
real custody access, network operation, external integration or delegation was
performed. All completed fixture results remain synthetic.

Required canonical group (exact arguments):

```text
tests.align.test_v4_executed_closure tests.align.test_v4_dynamic_closure tests.align.test_v4_registration
```

**36 passed**, 203.662 s (209.088 s process wall). No stale trace/receipt
digest failure was emitted, so there is no EXPECTED failure message to quote.

### Round 2 serial importer ledger

`rg -l align_v4_session tests` found 54 modules. The full arm module and the
executed-closure/registration modules are covered above. The other 51 modules
were attempted individually with the same unittest prefix, isolated synthetic
HOME/host-state, no global/system Git config, lazy fetch disabled and offline
model settings. Test opt-ins (`JW_*` and `JOULEWISE_*`) were cleared before
setting the synthetic host-state path. Initial red did not use that wrapper;
its tests use only their private synthetic Git repository.

The remaining budget cannot complete all 51 full modules. Known smaller
modules receive up to 10 s; other modules receive up to 4 s, reduced as needed
to reserve a serial attempt for every importer while keeping total test
process wall below 20 minutes. A TIMEOUT is incomplete coverage and never a
pass. The lead must finish those modules under a fresh authorized test budget.
These bounded attempts do not satisfy a complete importer regression gate.

| Module (arguments after unittest prefix) | Result | Cap (s) | Wall (s) |
|---|---|---:|---:|
| `tests.align.test_km003c` | TIMEOUT; incomplete | 10.000 | 10.018 |
| `tests.align.test_r11_delta_sol1` | PASS; 8 tests | 10.000 | 8.174 |
| `tests.align.test_r11_delta_sol2` | TIMEOUT; incomplete | 10.000 | 10.014 |
| `tests.align.test_r1_round6_exec_review` | FAIL; 9 tests; failures=1 | 10.000 | 6.942 |
| `tests.align.test_r1_round6_power` | FAIL; 25 tests; errors=6 | 10.000 | 6.421 |
| `tests.align.test_v4_dc_sealing` | PASS; 2 tests | 10.000 | 4.181 |
| `tests.align.test_v4_powermode_record` | PASS; 9 tests | 10.000 | 6.694 |
| `tests.align.test_v4_r11` | PASS; 27 tests | 10.000 | 8.050 |
| `tests.test_w1_reliability_r3` | PASS; 14 tests | 10.000 | 7.150 |
| `tests.test_w1_reliability_r5` | TIMEOUT; incomplete | 10.000 | 10.009 |
| `tests.test_w1_reliability_r7` | PASS; 10 tests | 10.000 | 8.564 |
| `tests.align.test_harvest_off` | TIMEOUT; incomplete | 4.000 | 4.025 |
| `tests.align.test_harvest_off_review_sol1` | TIMEOUT; incomplete | 4.000 | 4.097 |
| `tests.align.test_harvest_off_review_sol2` | TIMEOUT; incomplete | 4.000 | 4.024 |
| `tests.align.test_merge_c84_sol` | TIMEOUT; incomplete | 4.000 | 4.014 |
| `tests.align.test_r0_host` | TIMEOUT; incomplete | 4.000 | 4.035 |
| `tests.align.test_r11_delta3_sol1` | TIMEOUT; incomplete | 4.000 | 4.032 |
| `tests.align.test_r11_delta3_sol2` | TIMEOUT; incomplete | 4.000 | 4.025 |
| `tests.align.test_r11_delta4_sol1` | TIMEOUT; incomplete | 4.000 | 4.013 |
| `tests.align.test_r11_delta4_sol2` | TIMEOUT; incomplete | 4.000 | 4.015 |
| `tests.align.test_r11_delta5_sol1` | TIMEOUT; incomplete | 4.000 | 4.034 |
| `tests.align.test_r11_delta5_sol2` | TIMEOUT; incomplete | 4.000 | 4.118 |
| `tests.align.test_r11_delta6_sol1` | TIMEOUT; incomplete | 4.000 | 4.019 |
| `tests.align.test_r11_delta6_sol2` | TIMEOUT; incomplete | 4.000 | 4.018 |
| `tests.align.test_r1_round7_install` | TIMEOUT; incomplete | 4.000 | 4.035 |
| `tests.align.test_r1_round7_power` | TIMEOUT; incomplete | 4.000 | 4.153 |
| `tests.align.test_r1_round8` | TIMEOUT; incomplete | 4.000 | 4.021 |
| `tests.align.test_smoke_delta4_sol1` | TIMEOUT; incomplete | 4.000 | 4.020 |
| `tests.align.test_smoke_delta4_sol2` | TIMEOUT; incomplete | 4.000 | 4.014 |
| `tests.align.test_smoke_delta_sol1` | TIMEOUT; incomplete | 4.000 | 4.137 |
| `tests.align.test_smoke_delta_sol2` | TIMEOUT; incomplete | 4.000 | 4.011 |
| `tests.align.test_smoke_review_sol1` | TIMEOUT; incomplete | 4.000 | 4.008 |
| `tests.align.test_smoke_review_sol2` | TIMEOUT; incomplete | 4.000 | 4.022 |
| `tests.align.test_timing_receipts` | TIMEOUT; incomplete | 4.000 | 4.038 |
| `tests.align.test_v4_disclosure_only_desk` | TIMEOUT; incomplete | 4.000 | 4.134 |
| `tests.align.test_v4_kit` | TIMEOUT; incomplete | 4.000 | 4.017 |
| `tests.align.test_v4_next_arm_packet` | TIMEOUT; incomplete | 4.000 | 4.095 |
| `tests.align.test_v4_next_arm_packet_opus_witnesses` | TIMEOUT; incomplete | 4.000 | 4.032 |
| `tests.align.test_v4_record_binding` | TIMEOUT; incomplete | 4.000 | 4.018 |
| `tests.align.test_v4_series` | TIMEOUT; incomplete | 3.669 | 3.683 |
| `tests.align.test_v4_series_e2e` | TIMEOUT; incomplete | 1.986 | 1.996 |
| `tests.align.test_v4_series_r20` | TIMEOUT; incomplete | 1.990 | 2.256 |
| `tests.align.test_v4_w1_blockers` | TIMEOUT; incomplete | 1.734 | 1.773 |
| `tests.align.test_v4_w1_synthetic` | TIMEOUT; incomplete | 1.961 | 1.989 |
| `tests.align.test_w1_kit_r10` | TIMEOUT; incomplete | 1.972 | 1.988 |
| `tests.align.test_w1_prequal` | TIMEOUT; incomplete | 1.984 | 2.002 |
| `tests.align.test_w1_smoke` | TIMEOUT; incomplete | 1.982 | 1.994 |
| `tests.align.test_w1bm_sol1` | TIMEOUT; incomplete | 1.988 | 2.003 |
| `tests.align.test_w1bm_sol2` | TIMEOUT; incomplete | 1.985 | 2.019 |
| `tests.test_w1_reliability_r2` | TIMEOUT; incomplete | 1.966 | 1.978 |
| `tests.test_w1_reliability_r4` | TIMEOUT; incomplete | 1.988 | 2.023 |

Completed importer attempts: **6 pass, 2 fail, 43 timeout** (plus the three
importer modules already covered by the passing arm/canonical group). All 54
importers received a full-module invocation; 43 did not complete. A separate
final invocation after the lock-only fixture adaptation was:

`python3.13 -B -m unittest tests.align.test_r1_round6_power`:
**FAIL**, 25 tests, 6 errors, 3.419 s unittest / 9.972 s process wall.

Completed failures, not labelled EXPECTED:

- `tests.align.test_r1_round6_exec_review`, 9 tests, one failure: expected
  `ac powermode exit restore (dead_man)` but the synthetic dead-man log says
  `ac powermode close: restore Automatic; network time unchanged`.
- The first `tests.align.test_r1_round6_power` attempt had one newly exposed
  fixture error: `ValueError: v4 arm refused: held_window: unreadable: KeyError: 'window_chain'`
  in `test_install_holds_the_lock_until_it_returns`. That test supplies a
  synthetic pointer without packet-chain authentication and tests the host
  lock. Its context now explicitly isolates `held_window_check`, exactly as
  the nearby install helper already does; the lock assertions are unchanged.
  This red log preceded the one-line fixture fix. On the final module repeat,
  the held refusal is gone. The remaining six errors are three
  `TypeError: FakeArmHost.__call__() got an unexpected keyword argument 'check'`
  and three `KeyError: 'plan_path'`. These match the classes documented in the
  round-1 report. Round 2 did not independently replay those unrelated errors
  against its base, so historical attribution is recorded rather than claimed
  as a fresh baseline proof. No unrelated host/restore fix was attempted.

Conservative total test process wall: **1190.007 s** (**19.833 min**), including the interrupted initial red, the superseded green child, interpreter startup and all timed-out attempts. This sums overlapping test processes separately. No further tests were started after this ledger.


Final in-memory compilation of all four changed Python files and final diff
whitespace checks pass. Coordination state, protocol, deviations, receipt,
registration, dynamic trace, next-arm packet builder, watchdog, night driver
and B5 driver remain unchanged. No raw evidence was edited. The handoff is
not a green full regression claim: the two failed modules and 43 incomplete
modules remain for the lead, along with all native gates above.

Next exact step: cold-review `081f7f457..7d472758a` and the final one-line
lock-fixture/report commit; finish the TIMEOUT modules in a fresh authorized
budget and disposition the two observed regression failures. Then the lead
integrates, adds its deviation row, regenerates trace/STRICT receipt, and
runs remote synthetic native qualification, PREQUAL and smoke on the final
registered bytes. Any measured smoke requires agents to stand down and a
clean lead-controlled quiet session. No research ruling question remains;
RL-79 supersedes the round-1 identity-hold question.

## Round 3 — PH-1: W1 final harvests participate in holds

Base: arm-check `bb64d1e70` (rounds 1 and 2 merged). Local branch:
`ops/2026-11-11-w1-prepare-holds-r3`. Read RL-53 W-0 through W-3,
RL-35 item 4, RL-37, RL-65, RL-71 and RL-79 at the requested audit ref,
the requested state-machine audit sections, M0 and repository conventions.
The explicit seat brief selects this work and prohibits coordination-state
writes and a full suite; no kernel task was registered. No agent was delegated.

The only bound edit is in `scripts/align_v4_session.py`: replace the
R1/W1/development skip with `window.window == 'R1'` and correct its comment.
W1 and other development records now use the existing finality, no-capture
and authenticated-final-exclusions branches. R1 remains skipped. The packet's
calibration-count omission does not exempt W1 from RL-65/RL-71/RL-79 holds.
No measured byte, flag, verdict, window-record content or receipt check changes.

No new refusal code is introduced. The existing
`held_window: W1: roster.no_science_bundles: no signed ruling` now refuses
the arm of C1 when W1's final harvest carries that reason. Its evidence is
recorded in the arm's `held_window_check.windows` (and latest-window summary),
and the refusal is copied to the arm's `reasons`, persisted by the existing
`staging/v4-arm-NNN.json` writer before quiet dwell. The hold check itself
finishes before the meter probe. The existing unreadable
refusal and committed, authenticated ruling requirements are unchanged.

### Round 3 failing-first evidence

Test-only commit `01cf4094e` precedes the production edit. Six selected
arm-module tests ran against unchanged production code: **6 tests, 5 failures**,
63.310 s unittest / 70.376 s process wall. Red output excerpts:

```text
FAIL: test_w1_not_final_defers_without_refusing
AssertionError: Lists differ: [] != ['W1']
FAIL: test_w1_final_without_capture_needs_no_harvest
AssertionError: 'skipped' != 'no final harvest: no capture'
FAIL: test_other_development_record_checks_final_exclusions
AssertionError: True is not false
FAIL: test_r1_is_skipped_and_each_chain_digest_is_verified
AssertionError: Lists differ: ['skipped', 'skipped'] != ['skipped', 'no held reasons']
```

That first run's new C1-arm fixture also exposed my stale synthetic battery
timestamp: its only arm refusal was `battery top-up incomplete/unobserved`,
so its failed reason assertion was not used as the decisive PH-1 arm witness.
I corrected the fixture to timestamp its fake battery and quiet records at
the current test time, then reran only the W1/C1 test against the same unchanged
production code: **1 test, 1 failure**, 10.250 s unittest / 17.459 s process wall:

```text
FAIL: test_w1_final_hold_refuses_c1_arm_until_committed_ruling
    self.assertFalse(row['admitted'], row)
AssertionError: True is not false
```

The captured arm had `admitted: True`, no refusal reasons and W1 status
`skipped`, despite the authenticated final `roster.no_science_bundles` reason.
The first six-test run also passed the unchanged round-2 test
`test_k_final_with_held_reason_and_k_plus_1_not_final_refuses_the_arm_of_k_plus_2`.
The first full post-fix run completed **80 tests, 1 failure**, 338.717 s
unittest / 345.564 s process wall. The new release fixture reused a packet
after changing its series commit to commit the ruling; the production arm
correctly refused that stale packet with:

```text
next_arm_triage: packet does not match its committed sources (the supplied packet differs from the arm's own build)
```

Its held check was already successful and carried W1's release ID. I corrected
the fixture to rebuild the packet at the new commit. Static review also
corrected its not-yet-reached release assertion: release IDs live in
`windows[].released_by`, while the existing latest-window summary is not
refreshed for that field. No production change was made for either test
mistake; completed verification is recorded below.

### Round 3 fixture and native handoff

The shared synthetic `Scenario` already writes W1's final `pilot`, `desk`
and readable `exclusions` sources. PREQUAL's held-window case uses that same
fixture. No missing-W1-exclusions fixture repair or PREQUAL harness change
was needed; the check was not weakened. Fixture corrections were limited to
the new arm test's synthetic timestamps, packet rebuild after the ruling
commit, and per-window release assertion described above.

After integration and registration, the lead must remotely exercise the
installed arm on a disposable synthetic W1 record whose authenticated final
exclusions carry `roster.no_science_bundles`: C1 refuses without its ruling,
then admits that hold with a valid committed W1 ruling. Inspect the staged
arm's W1 finality, reason, release ID and carried ruling, and confirm no
earlier record changes and completion before meter/dwell. Also exercise W1
provisional/deferred, W1 final zero-capture without harvest, R1 skipped, and
the final-k/provisional-k+1/arm-k+2 history case. All host commands in these
tests use existing fakes; no live host or measurement validation is claimed.
No MLX code changed and no Metal execution was attempted. Quiet measurements,
PREQUAL/smoke on registered bytes, deviation row, trace/STRICT receipt
regeneration and admission remain lead-owned gates.

### Round 3 final diff and verification

Against `bb64d1e70`:

| Path | Added / removed | Change |
|---|---:|---|
| `scripts/align_v4_session.py` (only bound file) | 2 / 3 | R1-only skip and corrected comment |
| `tests/align/test_v4_arm_watchdog_check.py` | 56 / 3 | Four new regression tests; update the combined R1/W1 expectation |
| This report | append only | Round 3 evidence and handoff |

No new test module was added, so `scripts/test_timings.json` is unchanged.
The round-2 k/k+1/k+2 method's source was also compared with the base in
memory and is unchanged. Both changed Python files compile in memory.

Final verification uses `python3.13 -B -m unittest` with the exact arguments
below. The separate corrected W1-arm test passed first: **1 test**, 25.268 s
unittest / 32.895 s process wall. The final complete arm module then passed:
**80 tests**, 373.715 s unittest / 383.389 s process wall.

```text
tests.align.test_v4_arm_watchdog_check
```

PREQUAL's held-window/runtime-stack case and production arm CLI control/fault
cases passed: **2 tests**, 231.835 s unittest / 233.143 s process wall.
The held-window case's clean W1 final exclusions remained readable; no new
`held_window: unreadable` refusal was observed.

```text
tests.align.test_w1_prequal.ArmCliTests.test_named_runtime_stack_and_held_window_cases
tests.align.test_w1_prequal.ArmCliTests.test_production_cli_admits_the_control_and_refuses_every_fault_before_the_installer
```

Importer discovery used `rg -l align_v4_session tests scripts` (excluding
real restricted directories). Per this round's explicit narrower test
instruction, no other importer modules were invoked independently. Every
test invocation was serial, with private synthetic HOME/host-state/temp
paths, system/global Git config disabled, hooks/templates disabled, lazy
fetch disabled and offline model settings. Test opt-ins were cleared.
Diagnostic logs and the process-wall ledger are in
`/private/tmp/w1-prepare-holds-r3-checks/`; they contain synthetic fixtures.

The required canonical group passed: **36 tests**, 335.703 s unittest /
343.225 s process wall, with these exact arguments:

```text
tests.align.test_v4_executed_closure tests.align.test_v4_dynamic_closure tests.align.test_v4_registration
```

No stale trace/receipt digest failure was emitted, so there is no EXPECTED
failure message to quote. Final requested checks: **118 tests passed**,
plus the separate passing corrected W1-arm test.

Total serial test process wall, including both red runs and the superseded
full-module fixture failure: **1426.051 s (23.768 min)**. This exceeded the
approximately 20-minute target by 3.768 min. The extra full-module run after
my new-fixture mistakes caused the overrun; no additional test process was
started after the canonical group. No full suite, pytest, network operation,
model download, real measurement-data access, real custody access or live
host command was performed.

Final diff/whitespace review passes and confirms only the three paths above
changed. Coordination state, protocol, deviations, trace, registration and
receipt, packet builder, watchdog, night driver and B5 driver are unchanged.
Local test-only commit: `01cf4094e`; the implementation/test-correction/report
commit is returned in the handoff. Nothing was pushed.

No open contract question remains. The test subset is green; it does not
claim a complete importer regression or native qualification. Next exact
step: the lead cold-reviews the round-3 commits, integrates the narrow fix,
adds its deviation row and regenerates the trace/STRICT receipt, then runs
the remote installed synthetic native checks above and PREQUAL/smoke on the
registered bytes. Any measurement requires agents to stand down first.
