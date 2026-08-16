```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Coverage VERIFIED: independently enumerated 251/251 tests; current-head execution accounted for 247/251, with four crash-matrix cases explicitly unexecuted.",
  "workspace": {
    "base_requested": "fac87d1",
    "base_mode": "exact",
    "head_start": "fac87d1f8350ab5277d45f422fbfa6098630efe4",
    "head_end": "fac87d1f8350ab5277d45f422fbfa6098630efe4",
    "upstream_end": "fac87d1f8350ab5277d45f422fbfa6098630efe4",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "coverage": "VERIFIED",
    "enumeration": {
      "numerator": 251,
      "denominator": 251
    },
    "current_head_execution": {
      "numerator": 247,
      "denominator": 251,
      "passed_test_bodies": 242,
      "skipped": 5,
      "unexecuted": 4
    },
    "non_test_evidence": {
      "enumerated": 26,
      "present_in_checkout": 25,
      "external_runtime_artifacts_absent": 1
    },
    "machine_readiness": "not regraded; the council NOT-READY verdict remains separate",
    "findings": [
      {
        "id": "L2R-1",
        "severity": "blocker",
        "title": "Current-head projection remains unbudgeted and prevents four writer-dependent crash cases completing locally",
        "disposition": "registered-limitation: WO-DETECT-PULSES-BUDGET plus WO-CRASHMATRIX-RELIABILITY; branch evidence was not counted as current-head execution"
      },
      {
        "id": "L2R-2",
        "severity": "should_fix",
        "title": "Recovery readiness with a missing ledger parent still emits an uncaught FileNotFoundError and has no exact-route test",
        "disposition": "registered-limitation: council L2-2 should-fix batch"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -c \"import unittest; ms=('tests.test_authentication_io','tests.test_calibration_bracketing','tests.test_calibration_custody_store','tests.test_calibration_exits','tests.test_calibration_ledger','tests.test_calibration_live_three_window','tests.test_powermetrics_fiducial','tests.test_calibration_writer_crash_matrix'); print([(m,unittest.defaultTestLoader.loadTestsFromName(m).countTestCases()) for m in ms])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "18 + 42 + 7 + 30 + 72 + 23 + 46 + 13 = 251; loader errors=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*251.*"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 18 tests in 0.573s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 18 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing tests.test_calibration_custody_store",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 42 tests in 0.062s — OK (skipped=1)", "Ran 7 tests in 0.287s — OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 42 tests.*Ran 7 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_ledger tests.test_calibration_live_three_window tests.test_powermetrics_fiducial",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 72 tests in 3.218s — OK (skipped=1)", "Ran 23 tests in 1.708s — OK (skipped=3)", "Ran 46 tests in 31.528s — OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 72 tests.*Ran 23 tests.*Ran 46 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 30 tests in 316.710s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 30 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_ambient_writer_crash_stage_is_inert_without_capability tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_invalid_crash_authorization_is_preserved_and_valid_one_is_consumed tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_owned_runner_bounds_inherited_pipe_wait_and_reaps_group tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_survivor_guard_detects_spinning_descendant tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_swapped_capability_pathname_fails_link_count_check_closed tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_teardown_propagates_persistent_eperm_after_sigkill tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_teardown_propagates_persistent_eperm_for_existing_group tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_teardown_raises_when_group_survives_successful_sigkill tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_teardown_reaps_zombie_only_group_after_term_eperm",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 9 tests in 15.700s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests.*OK"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "JW_PROBE=$(mktemp -d \"$TMPDIR/jw-l2-parent.XXXXXX\"); env PYTHONDONTWRITEBYTECODE=1 python3 scripts/recover_calibration_ledger.py --ledger \"$JW_PROBE/absent/ledger.jsonl\" --head-pin configs/calibration/calibration_ledger_head.json readiness --phase terminal",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: [Errno 2] No such file or directory: '$TMPDIR/jw-l2-parent.*/absent'"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FileNotFoundError"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d078_reason_registry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 0.054s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests.*OK"
      }
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git diff --exit-code && git diff --cached --exit-code && git status --short --branch && git rev-parse HEAD && git rev-parse origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "fac87d1f8350ab5277d45f422fbfa6098630efe4", "fac87d1f8350ab5277d45f422fbfa6098630efe4"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fac87d1f8350ab5277d45f422fbfa6098630efe4"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Four of thirteen crash-matrix IDs were not executed on current HEAD because writer-dependent cases enter the known degenerate projection path.",
      "needs": "Do not count the branch result as current-head coverage; retain the registered work orders."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Five tests were declared skipped and the untracked production ledger was absent from this audit worktree.",
      "needs": "Lead/Ed retains the real-input and live-production qualification gates."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The 14-OK/99s evidence belongs to ceda7a6 on impl/wo-detect-pulses-budget, not fac87d1; remediation was not graded.",
      "needs": ""
    }
  ]
}
```

## Findings

### L2R-1 — blocker

The current-head detector has no finite projection budget, and the crash matrix is not fully executable locally.

Nine non-writer-dependent crash tests passed. A broader attempt reached `test_torn_and_fsynced_append_boundaries_resume_from_fresh_processes`, stopped making progress after the preceding nine tests, and required interruption. Four writer-dependent IDs remain unexecuted:

- `test_every_exact_stage_pre_and_post_sigkill_reaches_fresh_governed_exit`
- `test_torn_and_fsynced_append_boundaries_resume_from_fresh_processes`
- `test_two_presenters_racing_one_capability_authorize_exactly_one`
- `test_two_process_lease_contention_then_fresh_resume`

The interrupted writer briefly survived its unittest parent, then exited; final inspection found no remaining process or open fixture.

Disposition: existing `WO-DETECT-PULSES-BUDGET`, `WO-CRASHMATRIX-RELIABILITY`, and the test-harness clause of `WO-SAMPLER-SUPERVISOR`. Commit `ceda7a6` independently contains 14 test methods and records 14 OK in 99 seconds, but that evidence is from the remediation branch and is excluded from the current-head numerator. The later branch head contains 15 methods and was not graded.

### L2R-2 — should_fix

The exact missing-parent route is uncovered and still fails outside the refusal registry:

```text
recover_calibration_ledger.py ... readiness --phase terminal
→ FileNotFoundError at resolve_ledger_lease_identity(...).parent.resolve(strict=True)
→ exit 1, no registered refusal envelope
```

No enumerated test constructs this exact absent-parent diagnostic route. The generic `calibration_physical_ledger_unreadable` public witness does not cover it.

Disposition: the council’s existing L2-2 should-fix batch. This is not a new work order.

## Independent enumeration

Procedure:

1. Start only from the charter’s L2 nouns: fiducial writer, authenticated acceptance, bracket reservation, ledger, recovery, and writer lifecycle.
2. Trace the three operational entry points and their direct imports/default evidence paths.
3. Include an entire test module when its primary contract is one of those L2 surfaces. Do not select favorable individual methods.
4. Include authentication, custody-store, refusal-registry, three-window, and crash-lifecycle modules because they directly govern L2 acquisition.
5. Exclude downstream consumption modules such as `test_reduce`, `test_run_campaign`, whole-window, floor-mint, and arm-readiness tests. Their primary contracts belong to other seats; string matches do not enlarge this denominator.
6. Load every included module with `unittest.TestLoader`, require zero loader errors, and sum `countTestCases()`.

| Module | Measured count | Current-head outcome |
|---|---:|---|
| `tests.test_authentication_io` | 18 | 18 pass |
| `tests.test_calibration_bracketing` | 42 | 41 pass, 1 skip |
| `tests.test_calibration_custody_store` | 7 | 7 pass |
| `tests.test_calibration_exits` | 30 | 30 pass |
| `tests.test_calibration_ledger` | 72 | 71 pass, 1 skip |
| `tests.test_calibration_live_three_window` | 23 | 20 pass, 3 skips |
| `tests.test_powermetrics_fiducial` | 46 | 46 pass |
| `tests.test_calibration_writer_crash_matrix` | 13 | 9 pass, 4 unexecuted |
| **Total** | **251** | **242 pass, 5 skip, 4 unexecuted** |

The non-test universe independently traced from those entry points contains 26 paths/classes:

- 10 implementation paths: five operational/issuance scripts and five core modules.
- 11 committed inputs: acceptance artifact, head pin, three protocol files, and the three current D117 `calibration_plan.json`/sidecar pairs.
- 4 governing documents: ledger contract, generated append/refusal contract, fiducial contract, and window runbook.
- 1 external runtime artifact: `runs/calibration_observation_ledger.jsonl`.

All 25 committed paths were present. The three D117 plan sidecars matched their plan bytes. The acceptance artifact loaded as issued and claim-eligible at sequence 76. The physical production ledger was absent because it is untracked and external to this worktree; it was not silently treated as examined.

## Coverage accounting

Two separate ratios prevent the branch and skip caveats from being laundered:

- Universe/accounting coverage: **251/251 test IDs explicitly enumerated and dispositioned**.
- Current-head execution coverage: **247/251 runner-accounted**, comprising 242 passing test bodies and 5 declared skips. Four crash-matrix IDs were not run.

The five skips were:

- Two tests requiring unavailable lead-reviewed D-079 import inputs.
- Three successor-engine tests explicitly marked `U2 successor engine pending`.

The cross-project D-078 registry module is outside the direct L2 denominator but was run as corroborating contract coverage: 13/13 OK.

### Denominator-sensitivity probes

Each probe copied `tests/` beneath `$TMPDIR`, renamed one method from `test_*` to `removed_*`, and loaded that copied module directly with `importlib.util.spec_from_file_location`:

| Probe | Renamed test | Result |
|---|---|---:|
| P1 | `test_range_expanding_live_observation_requires_successor` | 23→22; total **251→250** |
| P2 | `test_every_exact_stage_pre_and_post_sigkill_reaches_fresh_governed_exit` | 13→12; total **251→250** |
| P3 | `test_generated_contract_projection_and_runbook_anchors_are_fresh` | 30→29; total **251→250** |

Thus the procedure responds to removed membership rather than reproducing a memorized total.

## Adversarial coverage attack

| Failure class | Attack result | Covering test or disposition |
|---|---|---|
| Non-termination/work budget | **Explicit gap.** No current-head budget/exhaustion test or implemented projection budget; writer-dependent crash execution stalled. | Registered limitation: `WO-DETECT-PULSES-BUDGET`. |
| Crash-matrix writer kills | Exact-stage/torn-append tests exist, but four writer-dependent IDs were not executable on this head. Nine process/capability/teardown tests passed. | Registered execution limitation: `WO-DETECT-PULSES-BUDGET` + `WO-CRASHMATRIX-RELIABILITY`; branch evidence excluded. |
| Staleness/freshness | Covered for stale derivation, estimator-byte drift, identity epoch, causal/T1/protocol mismatch, and range expansion. | `test_estimator_byte_drift_refuses_acceptance_as_stale`, `test_identity_epoch_violation_refuses_stale_acceptance_bound`, `test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint`; successor-specific cases remain declared skips. |
| Custody/lease | Covered for missing/changed custody, symlink and hard-link aliasing, slot replacement, concurrent double-arm, and stable-claim repair. | `test_store_refuses_missing_symlink_nonregular_and_hash_mismatch`, `test_symlink_alias_cannot_acquire_a_second_writer_lease`, `test_hard_link_alias_cannot_acquire_a_second_writer_lease`, `test_concurrent_double_arm_accepts_exactly_one_and_loser_cannot_abort_winner`. |
| Novel: authenticated-input TOCTOU/forgery | Covered. | `test_repeated_read_detects_toctou_mutation`, `test_rekeyed_self_consistent_artifact_is_not_authenticated`, `test_hash_rekeyed_candidate_cannot_bypass_binding_authentication`. |
| Novel: session/plan substitution | Covered for neighboring endpoint borrowing, reordered/conflicting receipts, cross-window swaps, and session forks. | `test_exact_session_binding_selects_reserved_pair_not_neighbors`, `test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding`, `test_conflicting_session_identity_and_session_fork_refuse`. |
| Novel: durability/power-loss publication | Covered in the ledger module; crash-writer variants retain the execution caveat above. | `test_historical_import_fsync_failure_keeps_visible_ledger_empty`, `test_post_replace_dir_fsync_fault_is_committed_and_retry_confirms`, `test_sigkill_at_all_six_append_points_converges_without_deletion`. |
| Novel: advisory backfill corruption | No direct test imports `calibration_ledger_backfill.py`. | **Covered elsewhere:** output is explicitly `authoritative:false` and `production_issuance_blocked:true`, cannot append the ledger, and requires lead-owned raw-physics/hash review before the independently authenticated bootstrap route. |
| Missing ledger parent on diagnostic route | **Explicit gap reproduced.** Raw traceback, no refusal envelope. | Registered limitation: council L2-2 should-fix batch. |

## Verdict

**Coverage VERIFIED: 251/251 independently enumerated and dispositioned.**

This closes the distinct uncertainty about L2’s coverage denominator. It does not claim 251/251 current-head execution, does not certify the remediation branch, and does not alter the council’s separate **NOT-READY** machine verdict.

## Residual risk

The production physical ledger and lead-owned D-079/live qualification inputs were unavailable in this worktree. Consequently, this report verifies the coverage universe and its accounting—not production-ledger parity, real hardware behavior, or ED-QUALIFICATION closure.