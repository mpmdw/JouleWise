# Replay: full sharded suite at integration head 51565cee

## Command (exact)

```
cd /Users/edr/code/JouleWise-wt-replay-51565cee && PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4 --split > /tmp/magistrate-96bfeca7/replay-51565cee.log 2>&1; echo "REPLAY_RC=$?" >> /tmp/magistrate-96bfeca7/replay-51565cee.log
```

`--split` was accepted (declared in `scripts/shard_tests.py:877`); no rerun was needed.
Single replay only. Worktree `/Users/edr/code/JouleWise-wt-replay-51565cee`, HEAD
`51565ceece0f3893beb0914ccdb060cd1286c769`, `git status --porcelain` empty before and no
files edited, no git state changed. No `[QUIET-MAC]`, no sudo, no live powermetrics.

## Wall clock

- START 2026-09-10 13:02:49 PDT
- END   2026-09-10 13:46:13 PDT
- Elapsed 43m24s

## Result

**`REPLAY_RC=1`** (log line 8687). Log kept at `/tmp/magistrate-96bfeca7/replay-51565cee.log` (8687 lines).

```
WORKERS SUMMARY shards=4 modules=227 tests=5773 failures=5 errors=9 skipped=109 failed_shards=1,2,3,4 result=FAIL
```

### Per-shard

| shard | modules | tests | failures | errors | skipped | result |
|---|---|---|---|---|---|---|
| 1/4 | 49 | 1173 | 0 | 1 | 16 | FAIL |
| 2/4 | 59 | 1528 | 1 | 0 | 7  | FAIL |
| 3/4 | 59 | 1254 | 4 | 0 | 50 | FAIL |
| 4/4 | 60 | 1818 | 0 | 8 | 36 | FAIL |

Only five modules failed; every other module reported `MODULE PASS`.

```
198:  MODULE FAIL tests.test_arm_readiness_dry_run          tests=10 failures=0 errors=1 seconds=37.387
2297: MODULE FAIL tests.test_arm_readiness_evidence_author  tests=24 failures=1 errors=0 seconds=81.477
4437: MODULE FAIL tests.test_authentication_io              tests=22 failures=1 errors=0 seconds=1.027
4947: MODULE FAIL tests.test_custody_mode_inventory         tests=7  failures=3 errors=0 seconds=45.667
7199: MODULE FAIL tests.test_launch_window                  tests=38 failures=0 errors=8 seconds=243.460
```

## Pre-existing vs new

**The known local-only, row-9-waived failure did NOT occur.**
`tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
appears once in the log (line 4848) and its status is `... ok`. Record-35's waived row is therefore
not among today's 14 failing results.

**All 14 failing results are NEW at this integration head**, and all three clusters map onto files the
integration branch changed relative to `origin/main` (`git diff --stat origin/main...HEAD`:
`joulewise/calibration_ledger.py` +334, new `scripts/issue_calibration_acceptance_generation.py` +150,
`tests/test_calibration_ledger.py` +1028).

---

## Cluster A — nested focused suite `tests.test_calibration_ledger` refuses during evidence authoring (10 of 14)

Root failure is identical in all ten: `author_arm_readiness_evidence` runs a focused subprocess
suite over `tests.test_calibration_ledger` and that nested run reports `errors=1`.

```
joulewise.arm_readiness_evidence.EvidenceAuthoringError: focused suite refused: failures=0, errors=1, unexpected_successes=0
```

Common traceback tail (log 179-195, 7023-7196):

```
  File ".../tests/test_arm_readiness_dry_run.py", line 516, in test_production_minted_dry_run_survives_repository_relocation
    authored = evidence.author_arm_readiness_evidence(pack)
  File ".../joulewise/arm_readiness_evidence.py", line 3380, in author_arm_readiness_evidence
    item = _DERIVERS[kind](context)
  File ".../joulewise/arm_readiness_evidence.py", line 2427, in _derive_recovery_ledger_test
    result = _run_suite(context, kind, ("tests.test_calibration_ledger",))
  File ".../joulewise/arm_readiness_evidence.py", line 781, in _run_suite
    raise _underivable(...)
```

Affected test ids:

1. `tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_production_minted_dry_run_survives_repository_relocation` — ERROR (shard 1, log 179)
2. `tests.test_launch_window.ProductionArmRelocationLaunchTests.test_mint_keeps_raw_anchors_separate_from_sequence_clock` — ERROR x4 subtests (log 7023, 7042, 7061, 7080), params
   `(raw_now=10000000000000, ordinary_minus_raw_ns=-7200000000000)`, `(…, 0)`, `(…, 7200000000000)`,
   `(raw_now=60000000000, ordinary_minus_raw_ns=-7200000000000)`; fails at `tests/test_launch_window.py:530` -> `_mint_v4_arm` (`:724`)
3. `tests.test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_go_binds_root_and_refuses_content_change` — ERROR (log 7099), `tests/test_launch_window.py:999` -> `_mint_v4_arm`
4. `tests.test_launch_window.ProductionArmRelocationLaunchTests.test_subprocess_clock_observations_keep_refusal_predicates_real` — ERROR x3 subtests (log 7118, 7144, 7170), params
   `(skew_ns=1000000, drift_ns=5000000)`, `(skew_ns=1000001, drift_ns=0)`, `(skew_ns=1000, drift_ns=5000001)`; `tests/test_launch_window.py:893` -> `_mint_v4_arm`
5. `tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_authored_evidence_makes_synthetic_pack_freeze_pass` — FAIL (shard 2, log 2285)

```
  File ".../tests/test_arm_readiness_evidence_author.py", line 1278, in test_authored_evidence_makes_synthetic_pack_freeze_pass
    self.assertEqual(author_return_code, 0)
AssertionError: 2 != 0
```

**Diagnostic note (important for the fix round):** `tests.test_calibration_ledger` PASSES as its own
module in this same replay — log 2838, `MODULE PASS tests.test_calibration_ledger tests=92 failures=0
errors=0 skipped=1 seconds=8.085`. It refuses only under the nested authoring path, whose call sites
are all repository-RELOCATION tests (`_mint_v4_arm`, `survives_repository_relocation`). So the likely
shape is a test added in this branch's +1028 lines of `tests/test_calibration_ledger.py` that assumes
the canonical repo root / an in-place path and errors when executed from the relocated copy.
The failing test id inside the nested suite is NOT recoverable from this log:
`_run_suite` -> `_execute_unittest_suite_subprocess` parses only counts from the subprocess and
discards its output (`joulewise/arm_readiness_evidence.py:746-786`). Getting that id needs a targeted
run of the authoring path with the subprocess output retained.

## Cluster B — authentication-surface guard, 8 new direct-IO call sites (1 of 14)

`tests.test_authentication_io.AuthenticationSurfaceGuardTests.test_marked_v2_surface_has_no_direct_readable_io` — FAIL (shard 3, log 4411)

```
  File ".../tests/test_authentication_io.py", line 426, in test_marked_v2_surface_has_no_direct_readable_io
    self.assertEqual(violations, [])
AssertionError: Lists differ: ['joulewise/calibration_ledger.py:_filesys[544 chars]pen'] != []
First list contains 8 additional elements.
- ['joulewise/calibration_ledger.py:_filesystem_type:2983:read_text',
-  'joulewise/calibration_ledger.py:_open_slot_sidecar:3087:os.open',
-  'joulewise/calibration_ledger.py:abandon_calibration_ledger_tail:4106:os.fdopen',
-  'joulewise/calibration_ledger.py:open_append_descriptor:3418:os.open',
-  'joulewise/calibration_ledger.py:publish_genesis_payload:3363:os.open',
-  'joulewise/calibration_ledger.py:repair_calibration_ledger:4049:os.fdopen',
-  'joulewise/calibration_ledger.py:resolve_ledger_lease_identity:3035:os.open',
-  'joulewise/calibration_ledger.py:resolve_ledger_lease_identity:3049:os.open']
```

All eight are in `joulewise/calibration_ledger.py`, the file this integration head grew by +334 lines.

## Cluster C — custody-mode inventory allowlist misses the new script (3 of 14)

All three failures in `tests.test_custody_mode_inventory.CustodyModeInventoryTests` report the same
single uncensused row for the branch's new script (shard 3, log 4914-4934):

```
('scripts/issue_calibration_acceptance_generation.py', 'check', 1)
```

- `test_line_shift_does_not_require_allowlist_edit` — FAIL, `tests/test_custody_mode_inventory.py:335`, `self.assertEqual(actual, allowed_replay())` -> `AssertionError: Items in the first set but not the second: ('scripts/issue_calibration_acceptance_generation.py', 'check', 1)`
- `test_read_replay_inventory` — FAIL, `tests/test_custody_mode_inventory.py:246`, same assertion and same extra item
- `test_second_call_requires_its_own_allowlist_row` — FAIL, `tests/test_custody_mode_inventory.py:348`, `self.assertEqual(actual - allowed_replay(), {(path, "analyze_claims", 2)})` -> same extra item

This is a missing allowlist row for the new `scripts/issue_calibration_acceptance_generation.py`
`check` call site, not a behavioural defect in the script.

## Bottom line

Integration head 51565cee is RED: `REPLAY_RC=1`, 5773 tests, 5 failures + 9 errors across 5 modules,
109 skipped. The row-9-waived `test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
passed, so none of the 14 are the known pre-existing local failure — all 14 are new and all three
clusters trace to this branch's calibration-ledger work. Clusters B and C look mechanical
(surface-guard allowlist / custody census rows). Cluster A is the substantive one and needs the
nested suite's failing test id, which this log cannot supply.
