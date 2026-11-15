# W1 estimator restore — RL-58
MEMO: OUTSIDE (joulewise/b5/harvest.py)

## Scope and authority

Seat `w1-est-restore`, branch `ops/2026-11-11-w1-est-restore`, starting at
`7913b3677431d25d7beee5e2072c139b21da6632`. The seat branch already existed
and was clean at intake. RL-58 was read verbatim first, stopping before
`### R1`; RL-53 W-0–W-3, RL-35, RL-37 and the specified state-machine audit
sections were consulted. The task's synthetic-only/no-network instructions
override the normal full-suite and coordination-state updates. No coordination
file, registration, closure trace, receipt, pin registry or repin tool was edited.
No measurement pipeline, real custody, host-state command or model download ran.

## Changes and estimator identity

1. **First commit `ebe3d56a7`**, `Restore accepted powermetrics estimator bytes
   (RL-58)`: exactly `git checkout origin/main -- joulewise/adapters/powermetrics.py`,
   plus the all-estimator-pins regression in the existing measurement-boundary
   test module. The estimator delta is **+0/−40 lines**. No subsequent estimator
   edit was made. Its restored bytes equal `origin/main` exactly.
2. **Second commit `2127e00bd`**, `Scope the powermetrics parse memo inside
   harvest (RL-58)`. The harvest delta is **+46/−1 lines**: four stdlib imports, its own scoped
   document memo, and removal of the estimator-side memo import. The member
   assessment's scope remains in the same location. No flags, verdicts, window
   fields, arithmetic, receipt checks or refusal codes were added or changed.
3. The three harvest-off test modules now invoke/disable the harvest memo and
   instrument the restored `_powermetrics_documents` parser. Existing member,
   damaged-member and whole-archive byte-equality assertions remain. The
   measurement-boundary test retains its other core digests; its post-window
   harvest checksum acknowledges the RL-58 edit. No new test module was added,
   so `scripts/test_timings.json` was not edited.

Estimator SHA-256, both restored file and issued acceptance pin:

```text
70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4
```

A separate `git show HEAD:<path>` check at `2127e00bd` also confirmed all four
committed estimator blobs equal the acceptance pins.

The pin regression obtains the issued acceptance through
`load_calibration_acceptance_bound()`, checks the pin key set against
`ESTIMATOR_CODE_PATHS`, and hashes **every** listed estimator file.

## Parser paths, lifetime and concurrency

The accepted estimator exposes `_powermetrics_documents` at line 2056. All
three internal document-parser calls resolve that module-level name:
`_parse_powermetrics_records` (line 1762), `decode_rich_telemetry`
(line 1872), and `_complete_powermetrics_frames` (line 2086). The public
record/sample and rich-telemetry paths reach these functions. There is no
second document parser to edit. The `b9fedca2a` patch was inspected; its separate
`_parse_powermetrics_documents` name disappears with the exact restore.

Harvest temporarily rebinds only `_powermetrics_documents`, restoring the
original object in `finally`. Its context variable is reset in the same cleanup.
Each member gets a new dictionary, indexed by SHA-256 of the exact bytes. Only
successfully parsed and serialized results enter it. Hits unpickle fresh
objects; first-call mutations cannot alter the stored snapshot. Nested scopes
get independent dictionaries and restore the enclosing context.

`assess_members` uses `ProcessPoolExecutor`: each worker's rebind and cache are
process-local. The serial path assesses members sequentially in its caller's
process. Inventory threads hash files, and the desk supervision thread observes
a child process; neither parses member plists. For other parser callers in the
same process, the wrapper calls the original parser whenever their context has
no member memo. An `RLock` serializes thread-owned memo scopes while allowing
nested scopes. No worker pool is created inside a memo scope. The thread witness
checks that an unrelated thread parses twice while the member still gets a hit.
Tests compare every estimator module attribute by identity after normal exit
and after an exception raised through `assess_member`.

## Failing-first evidence

Before the restore:

```text
python3.13 -B -m unittest tests.align.test_measurement_core_boundary.MeasurementCoreBoundaryTests.test_every_estimator_file_matches_issued_acceptance
AssertionError: '7a6e59268c8b83331f9b2ef3618b0e9331a4552ffd6486309869a700bbd322f2' != '70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4'
Ran 1 test in 11.562s
FAILED (failures=1)
```

After the exact restore, before its first commit:

```text
Ran 1 test in 11.985s
OK
```

Before adding the harvest memo, the relocated and new parser witnesses ran
against the restored estimator and unchanged harvest:

```text
JW_B5_SYNTHETIC_ONLY=1 JOULEWISE_BACKUP_ROOTS='' python3.13 -B -m unittest tests.align.test_harvest_off.DocumentMemoTests
AttributeError: module 'joulewise.b5.harvest' has no attribute 'document_memo'
Ran 8 tests in 47.744s
FAILED (errors=7)
```

Those seven errors cover successful/dropped-frame hits and mutation isolation,
exact-byte keys, repeated failures, failure-then-success, attribute restoration
on success/error, and unrelated-thread isolation. The off-by-default witness
already passed. An initial post-fix run used the large seed fixture and its
new thread witness exceeded a 10-second future timeout:

```text
TimeoutError
Ran 8 tests in 117.131s
FAILED (errors=1)
```

That parser-only fixture was replaced with three tiny synthetic XML plists,
each containing a 1 KiB payload. This preserves both malformed-middle-frame
refusal and truncated-final-frame diagnostics. Bundle/archive equality fixtures
were not reduced or changed. Final results are recorded below.

## Synthetic profile

No production throughput claim. A `cProfile` run used 20 generated plist
documents and 18 repeated calls; no measurement bytes were read. Each document
was `plistlib.dumps({'cpu': {'power': 1000}, 'values': list(range(100))})`,
joined with NUL bytes. Before the
implementation, plist loading took 4.464 of 4.548 seconds. A paired post-change
run on the loaded host measured:

| Mode | Seconds | Document-parser calls | `plistlib.loads` calls |
|---|---:|---:|---:|
| Plain | 2.908215 | 18 | 360 |
| Memo | 0.246893 | 1 | 20 |

The serialized list of all 18 outputs had the same SHA-256 in both modes:
`11f19939e7811275f774a60966334f8832353d4ff3e075e41d01abb333a505a1`.
Timing variation reflects synthetic profiling on a busy machine; native desk
time remains the lead's check. No decisions or refusals are cached.

## Cold review and process evidence

The repository orchestration instructions and RL-58 require a fresh reviewer.
Native sub-agent `/root/cold_memo_review` received a read-only brief with an
empty write scope, the exact diff baseline `ebe3d56a7`, all memo conditions,
and the no-network/no-custody/no-test rules. It returned **no correctness
findings**, verified the estimator digest and parser paths, and identified
two coverage limits: no explicit nested-error/outer-cache-continuation witness
and no overlapping thread-owned-scope witness. Existing nested-scope and
error cleanup tests plus the unrelated-thread test remain; the lead owns final
verification. A separate read-only follow-up audited only the tiny parser
fixture change and found no loss of coverage. The reviewer made no writes and
ran no tests. This was not a cross-model bridge call.

## Pin checks

`python3.13 -B scripts/repin.py --check` exited **0**. Its exact final tail:

```text
  scripts/validate_powermetrics_fiducial.py
  scripts/write_b5_identity_pins.py
PASS 16 pin families current
```

It emitted the existing sealed-inventory drift warning listing the W1 code
surface, including harvest; **no `stale` line**. The check began after the
estimator restore and completed on the memo diff. No stale pin was repinned.

`python3.13 -B scripts/repin.py --check g2_phase_d` exited **0**, exact tail:

```text
PASS 1 pin families current
```

## Verification results

`PYTHONPYCACHEPREFIX=/private/tmp/w1-est-restore-checks/pycache python3.13 -m compileall -q joulewise tests` exited **0**, with no output. Compilation artifacts were kept outside the repository. `git diff --check` passed. `git diff --exit-code origin/main -- joulewise/adapters/powermetrics.py` exited **0**.

All test commands ran one at a time. Full modules used `python3.13 -B -m unittest <module>`; focused and final short selections added `-v`. The test environment used `JW_B5_SYNTHETIC_ONLY=1`, absent external custody locators, no global Git config, and a temporary guard refusing external-home filesystem access and networking, including fresh child interpreters. Only these runners' own test process groups were terminated on timeout.

The main sequential runner took **872.873 seconds**; the focused memo checks took **15.478 seconds**, and the final short-module attempts took **30.108 seconds**. Earlier red/restore checks reported **188.422 seconds** of unittest time (their initial interpreter startup time was not separately recorded). Work stopped within the approximately 20-minute test allocation. No full suite was run. The three calibration skips are existing `U2 successor engine pending` skips.

| Full module | Result | Exact unittest summary | Wall seconds |
|---|---|---|---:|
| `tests.test_calibration_live_three_window` | PASS | Ran 23 tests in 45.886s; OK (skipped=3) | 58.314 |
| `tests.test_repin` | TIMEOUT | Incomplete; no final unittest result | 175.025 |
| `tests.align.test_measurement_core_boundary` | FAIL | Ran 6 tests in 8.803s; FAILED (failures=1) | 17.440 |
| `tests.test_adapters_powermetrics` | PASS | Ran 3 tests in 31.112s; OK | 34.527 |
| `tests.align.test_v4_executed_closure` | PASS | Ran 4 tests in 57.275s; OK | 58.245 |
| `tests.align.test_v4_dynamic_closure` | PASS | Ran 10 tests in 88.842s; OK | 89.798 |
| `tests.align.test_v4_registration` | PASS | Ran 22 tests in 84.256s; OK | 89.162 |
| `tests.align.test_harvest_off` | TIMEOUT | Incomplete; no final unittest result | 175.198 |
| `tests.align.test_harvest_off_review_sol1` | TIMEOUT | Incomplete; no final unittest result | 175.143 |
| `tests.flags.test_flags_exclusions` | PASS | Ran 34 tests in 2.882s; OK | 3.638 |
| `tests.hazards.test_contention` | TIMEOUT | Incomplete; no final unittest result | 15.080 |
| `tests.test_b5_plan` | TIMEOUT | Incomplete; no final unittest result | 11.390 |

**All 12 focused memo witnesses passed:**

| Selection after `python3.13 -B -m unittest -v` | Result | Wall seconds |
|---|---|---:|
| `tests.align.test_harvest_off.DocumentMemoTests` | Ran 8 tests in 0.009s; OK | 4.814 |
| `tests.align.test_harvest_off_review_sol1.MemoAndSizingWitnesses.test_memo_content_changes_nested_members_and_refusals_are_isolated` | Ran 1 test in 0.009s; OK | 5.140 |
| `tests.align.test_harvest_off_review_sol2.MemoTests` | Ran 3 tests in 0.113s; OK | 5.524 |

The focused eight-test parser class now runs in 0.009 seconds of unittest time with its tiny synthetic fixture. All three harvest-off equality suites are preserved. Two full modules were attempted and **not completed** within the caps; the third full module was deferred. Full member/archive byte identity remains a lead verification item; this report does not infer a full-suite equality result from partial progress. The separate synthetic parser serialization equality/profile is complete.

### Exact full-module tails

The tails below preserve the captured log text; trailing spaces on interrupted progress lines were stripped. A timeout has no exit-0 result. `tests.align.test_harvest_off_review_sol2` was not run as a full module because the main budget was exhausted; its complete `MemoTests` class was subsequently run and passed.

`python3.13 -B -m unittest tests.test_calibration_live_three_window` — PASS; exit 0

```text
{"event": "calibration_custody_complete", "elapsed_s": 1.3819633750244975, "observations": 1}
...s.........s........s
----------------------------------------------------------------------
Ran 23 tests in 45.886s

OK (skipped=3)
```

`python3.13 -B -m unittest tests.test_repin` — TIMEOUT; terminated at the time cap

```text
..........................
```

`python3.13 -B -m unittest tests.align.test_measurement_core_boundary` — FAIL; exit 1

```text


----------------------------------------------------------------------
Ran 6 tests in 8.803s

FAILED (failures=1)
```

`python3.13 -B -m unittest tests.test_adapters_powermetrics` — PASS; exit 0

```text
...
----------------------------------------------------------------------
Ran 3 tests in 31.112s

OK
```

`python3.13 -B -m unittest tests.align.test_v4_executed_closure` — PASS; exit 0

```text
....
----------------------------------------------------------------------
Ran 4 tests in 57.275s

OK
```

`python3.13 -B -m unittest tests.align.test_v4_dynamic_closure` — PASS; exit 0

```text
..........
----------------------------------------------------------------------
Ran 10 tests in 88.842s

OK
```

`python3.13 -B -m unittest tests.align.test_v4_registration` — PASS; exit 0

```text
5 SECONDARY / not yet registered: {"flags": ["meter.custody_unavailable"], "sealed": true, "sealed_sha256": "43fab528e630ddeaffb66703d20b294b4f1763b3ad46a69f88518b7fc1bb64bf", "status": "missing"}
17 SECONDARY / not yet registered: {"flags": ["meter.custody_unavailable"], "sealed": true, "sealed_sha256": "43fab528e630ddeaffb66703d20b294b4f1763b3ad46a69f88518b7fc1bb64bf", "status": "missing"}
balance benign: members=0 exposure_s=0 events=0 expected=None
balance sabotage: members=0 exposure_s=0 events=0 expected=None
balance benign-vs-sabotage: {'exact_binomial_p': None, 'rate_ratio_sabotage_over_benign': None} (print only)
synthetic/W1 battery: {"B_count": 0, "assist_count": 0, "bar_pass": true, "consequence": "retain GPU members; disclose assist; print no-assist sensitivity; DC-in remains secondary", "unobserved_count": 0}
```

`python3.13 -B -m unittest tests.align.test_harvest_off` — TIMEOUT; terminated at the time cap

```text
............................
```

`python3.13 -B -m unittest tests.align.test_harvest_off_review_sol1` — TIMEOUT; terminated at the time cap

```text
..
```

`python3.13 -B -m unittest -v tests.flags.test_flags_exclusions` — PASS; exit 0

```text
test_three_lost_quads_no_longer_remove_the_window (tests.flags.test_flags_exclusions.SealedCellMinimumTests.test_three_lost_quads_no_longer_remove_the_window) ... ok

----------------------------------------------------------------------
Ran 34 tests in 2.882s

OK
```

`python3.13 -B -m unittest -v tests.hazards.test_contention` — TIMEOUT; terminated at the time cap

```text
test_quiet_regressed_counter_is_unmeasured_with_residual_disclosure (tests.hazards.test_contention.RegressedCounterTests.test_quiet_regressed_counter_is_unmeasured_with_residual_disclosure) ... ok
test_quiet_zombie_every_150_s_through_the_dwell_passes (tests.hazards.test_contention.RegressedCounterTests.test_quiet_zombie_every_150_s_through_the_dwell_passes) ... ok
test_refusal_names_last_measured_contention_before_missing_intervals (tests.hazards.test_contention.RegressedCounterTests.test_refusal_names_last_measured_contention_before_missing_intervals) ... ok
test_regression_neither_extends_nor_breaks_the_clean_run (tests.hazards.test_contention.RegressedCounterTests.test_regression_neither_extends_nor_breaks_the_clean_run) ... ok
test_unread_host_regression_discloses_missing_residual (tests.hazards.test_contention.RegressedCounterTests.test_unread_host_regression_discloses_missing_residual) ... ok
test_zombie_dwell_with_a_measured_contender_refuses (tests.hazards.test_contention.RegressedCounterTests.test_zombie_dwell_with_a_measured_contender_refuses) ...
```

`python3.13 -B -m unittest -v tests.test_b5_plan` — TIMEOUT; terminated at the time cap

```text
test_structural_defects_are_refused (tests.test_b5_plan.HazardWindowValidationTests.test_structural_defects_are_refused) ... ok
test_valid_window_round_trips (tests.test_b5_plan.HazardWindowValidationTests.test_valid_window_round_trips) ... ok
test_a_chain_stopped_before_its_post_calibration_is_cured_by_abort_then_advance (tests.test_b5_plan.LedgerHeadTests.test_a_chain_stopped_before_its_post_calibration_is_cured_by_abort_then_advance)
Rehearsal round 2, R2-5: the chain never aborts an open session, and its harvest has no terminal pin. ... ok
test_a_ledger_ahead_of_its_committed_pin_is_refused_at_the_desk_and_cured_by_the_pin_advance (tests.test_b5_plan.LedgerHeadTests.test_a_ledger_ahead_of_its_committed_pin_is_refused_at_the_desk_and_cured_by_the_pin_advance) ... ok
test_an_uncommitted_pin_and_an_open_session_are_refused_at_the_desk (tests.test_b5_plan.LedgerHeadTests.test_an_uncommitted_pin_and_an_open_session_are_refused_at_the_desk) ...
```

### Remaining importer modules for the lane lead

The census used `rg` followed by AST inspection of direct imports, including function-local imports. Comments/string-only references and the non-test `timing_receipts_capture.py` helper were excluded. The modules below were not run; except for the explicit recorded long module, they are deferred because the total time budget was exhausted, rather than assumed to be slow or green.

| Module | Reason |
|---|---|
| `tests.align.test_harvest_off_review_sol2` | Total test-time budget exhausted |
| `tests.align.test_hoff_delta2_sol1` | Total test-time budget exhausted |
| `tests.align.test_v4_w1_blockers` | Total test-time budget exhausted |
| `tests.b6.test_audit_record_fixes` | Total test-time budget exhausted |
| `tests.b6.test_bytes_p2_thermal_window` | Total test-time budget exhausted |
| `tests.b6.test_bytes_packs` | Total test-time budget exhausted |
| `tests.b6.test_cold_pass_fixes` | Recorded scheduling hint 1800 seconds (over the three-minute limit) |
| `tests.b6.test_fix416_gates` | Total test-time budget exhausted |
| `tests.b6.test_precheck` | Total test-time budget exhausted |
| `tests.b6.test_smoke` | Total test-time budget exhausted |
| `tests.b6.test_tolerance_sizing` | Total test-time budget exhausted |
| `tests.flags.test_b6_emitters` | Total test-time budget exhausted |
| `tests.flags.test_flags_collect` | Total test-time budget exhausted |
| `tests.flags.test_flags_core` | Total test-time budget exhausted |
| `tests.flags.test_flags_fx_regressions` | Total test-time budget exhausted |
| `tests.hazards.test_monitor` | Total test-time budget exhausted |
| `tests.test_align_pilot_session` | Total test-time budget exhausted |
| `tests.test_b5_seal_landing` | Total test-time budget exhausted |
| `tests.test_bytes_h_session` | Total test-time budget exhausted |
| `tests.test_bytes_manifest` | Total test-time budget exhausted |
| `tests.test_desk_compress` | Total test-time budget exhausted |
| `tests.test_desk_compressed_readers` | Total test-time budget exhausted |
| `tests.test_fix573f_restore` | Total test-time budget exhausted |
| `tests.test_fix573g_restore` | Total test-time budget exhausted |
| `tests.test_harvest_b5_p2harv` | Total test-time budget exhausted |
| `tests.test_harvest_b5_p3harv` | Total test-time budget exhausted |
| `tests.test_harvest_b5_window` | Total test-time budget exhausted |
| `tests.test_harvest_off_io` | Total test-time budget exhausted |
| `tests.test_hazard_neg8_mint_verdicts` | Total test-time budget exhausted |
| `tests.test_neg8_survivors` | Total test-time budget exhausted |
| `tests.test_write_b5_identity_pins` | Total test-time budget exhausted |

Also incomplete: `tests.test_repin`, `tests.align.test_harvest_off`, and `tests.align.test_harvest_off_review_sol1` at 175 seconds each; the final short attempts `tests.hazards.test_contention` (15 seconds) and `tests.test_b5_plan` (11.3 seconds remaining in that small reserve). Their logs contain no failure verdict before termination. The only completed red module is the **different-cause driver checksum** failure described below. All three closure/registration modules passed, so there is no stale-trace/receipt failure to classify as EXPECTED.

## Native handoff and uncertainty

No native measurement or MLX execution was attempted; this edit adds no MLX
code. The next exact step is for the lane lead to complete `python3.13 -B -m unittest tests.align.test_harvest_off`, then the two harvest-off review modules and `tests.test_repin` without this seat's caps, and disposition the existing driver checksum mismatch. The lane lead must also run the remaining importer modules listed above, the integration
fences, and the registered-head checks after the one batch deviation row and
closure-trace/receipt regeneration. On the measurement Mac after install,
exercise a synthetic member/whole-archive harvest with one and several worker
processes and confirm byte identity, parser cleanup after an injected member
exception, and accepted estimator digests. The lead performs native checks
remotely, outside an active quiet measurement window. Live hardware gates
remain unsatisfied by this report's fixture evidence.

The full measurement-boundary module exposed a **different cause**, already
present at the starting commit: its driver checksum expects
`d8780edb8e5806535291b32ace77cdf9a7acd7c8546a36fffebd119c311c0d5e`,
but both the starting Git blob and this tree contain
`88068b64d09d3e335810e3b4718246cb3164223b87f96b56c5a098349882f90b`.
The driver and its checksum were left unchanged.

```text
FAIL: test_pilot9_measurement_core_is_unchanged (tests.align.test_measurement_core_boundary.MeasurementCoreBoundaryTests.test_pilot9_measurement_core_is_unchanged) (name='joulewise/b5/driver.py')
AssertionError: '88068b64d09d3e335810e3b4718246cb3164223b87f96b56c5a098349882f90b' != 'd8780edb8e5806535291b32ace77cdf9a7acd7c8546a36fffebd119c311c0d5e'
```

Open review limitations are the two additional concurrency/nesting witnesses
above; no production defect was found. No new refusal code or staging-record
field exists. The completed different-cause failure and every incomplete check
are recorded above for the lane lead. No authority question requires a ruling.
