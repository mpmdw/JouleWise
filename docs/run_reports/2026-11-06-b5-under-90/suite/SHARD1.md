# SHARD1 unittest results

- Started: 2026-11-06T18:57:36Z UTC
- Python: `python3.13` (`Python 3.13.13`)
- Data: TEST/SYNTHETIC ONLY

tests.b5_analysis.test_analysed_windows_index: <Ran 5 tests in 15.917s> <OK>
tests.b5_analysis.test_auth_capability_bridge: <Ran 28 tests in 539.541s> <OK>
tests.b5_analysis.test_chain_fixture: <Ran 2 tests in 5.184s> <OK>
tests.b5_analysis.test_deadline_observer: <Ran 17 tests in 124.209s> <OK>
tests.b5_analysis.test_environment_admission_memo_first: <Ran 6 tests in 7.185s> <OK>
tests.b5_analysis.test_floor_kept_units: <Ran 53 tests in 65.582s> <OK>
tests.b5_analysis.test_joined_probes: <Ran 0 tests in 0.000s> <OK>
tests.b5_analysis.test_leaf_cli: <Ran 19 tests in 415.801s> <OK>
tests.b5_analysis.test_neg8_parity: <Ran 3 tests in 4.302s> <OK>
tests.b5_analysis.test_removed_member_preparation: <Ran 11 tests in 4.456s> <OK>
tests.b5_analysis.test_runtime_identity_cells: <Ran 12 tests in 5.437s> <OK>
tests.b5_analysis.test_shared_physics_cache: <Ran 10 tests in 350.919s> <OK>
tests.b5_analysis.test_step11_null_outcomes: <Ran 9 tests in 1.669s> <OK>
tests.b5_analysis.test_tripwires: <Ran 7 tests in 114.240s> <OK>
tests.b5_analysis.test_vdl_key_schema: <Ran 8 tests in 1.112s> <OK>
tests.b5_analysis.test_vdl_sol_hunt3: <Ran 15 tests in 93.414s> <OK>
tests.test_custody_mode_inventory: <Ran 7 tests in 220.863s> <FAILED (failures=2)>

## Failure: `tests.test_custody_mode_inventory`

- Assessment: **code under test (no clear missing-tool, missing-ref, network, or timeout signature)**.
- Failing test names and full traceback output from `/tmp/jws/tests.test_custody_mode_inventory.log`:

```text
..FF...
======================================================================
FAIL: test_line_shift_does_not_require_allowlist_edit (tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_line_shift_does_not_require_allowlist_edit)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/test_custody_mode_inventory.py", line 339, in test_line_shift_does_not_require_allowlist_edit
    self.assertEqual(actual, allowed_replay())
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Items in the second set but not the first:
('joulewise/b5_analysis/sensitivity.py', 'sensitivity_pass', 1)

======================================================================
FAIL: test_read_replay_inventory (tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_read_replay_inventory)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/test_custody_mode_inventory.py", line 250, in test_read_replay_inventory
    self.assertEqual(actual, allowed_replay())
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Items in the second set but not the first:
('joulewise/b5_analysis/sensitivity.py', 'sensitivity_pass', 1)

----------------------------------------------------------------------
Ran 7 tests in 220.863s

FAILED (failures=2)

```

tests.test_issue_calibration_acceptance_generation: <Ran 156 tests in 304.262s> <OK>
tests.test_reissue_calibration_acceptance: <Ran 6 tests in 0.328s> <OK>
tests.test_b5_seal_landing: <Ran 9 tests in 2.394s> <OK>

## Modules not run

None.

- Finished: 2026-11-06T19:36:01Z UTC
- Elapsed: 2305 seconds
