# SHARD2 unittest results

- Started: `2026-11-06T18:57:49Z` UTC
- Python: `/root/.pyenv/versions/3.13.13/bin/python3.13` (`Python 3.13.13`)
- Data policy: TEST/SYNTHETIC DATA ONLY; `JW_B5_S10_REAL_PROGRAMS` was not set.

## Module results

tests.b5_analysis.test_analysis_work_counts: <Ran 1 test in 82.771s> <OK>

tests.b5_analysis.test_auth_recorder_and_verdict_memo: <Ran 34 tests in 0.472s> <FAILED (failures=5)>

### Failure details: `tests.b5_analysis.test_auth_recorder_and_verdict_memo`

- FAIL: `test_missing_directory_and_unreadable_inputs_raise_identically`
- FAIL: `test_missing_directory_and_unreadable_inputs_raise_identically`
- FAIL: `test_missing_directory_and_unreadable_inputs_raise_identically`
- FAIL: `test_missing_directory_and_unreadable_inputs_raise_identically`
- FAIL: `test_missing_directory_and_unreadable_inputs_raise_identically`

**Likely cause:** Environment. The process is running as a privileged user, so the `chmod(0)` fixture remains readable; all five failures are the unreadable-file subcases (indexes 10–14), rather than evidence of a code-under-test regression.

```text
..........................FFF/workspace/JouleWise/tests/b5_analysis/test_auth_recorder_and_verdict_memo.py:626: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/jws/authio-ajum7ewt/locked.json' mode='r' encoding='UTF-8'>
  plain, recorded = self._both(call)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
F/workspace/JouleWise/tests/b5_analysis/test_auth_recorder_and_verdict_memo.py:626: ResourceWarning: unclosed file <_io.BufferedReader name='/tmp/jws/authio-ajum7ewt/locked.json'>
  plain, recorded = self._both(call)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
F.......
======================================================================
FAIL: test_missing_directory_and_unreadable_inputs_raise_identically (tests.b5_analysis.test_auth_recorder_and_verdict_memo.RecorderSessionlessSemantics.test_missing_directory_and_unreadable_inputs_raise_identically) (index=10)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_auth_recorder_and_verdict_memo.py", line 627, in test_missing_directory_and_unreadable_inputs_raise_identically
    self.assertEqual(plain[0], "raise")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
AssertionError: 'ok' != 'raise'
- ok
+ raise


======================================================================
FAIL: test_missing_directory_and_unreadable_inputs_raise_identically (tests.b5_analysis.test_auth_recorder_and_verdict_memo.RecorderSessionlessSemantics.test_missing_directory_and_unreadable_inputs_raise_identically) (index=11)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_auth_recorder_and_verdict_memo.py", line 627, in test_missing_directory_and_unreadable_inputs_raise_identically
    self.assertEqual(plain[0], "raise")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
AssertionError: 'ok' != 'raise'
- ok
+ raise


======================================================================
FAIL: test_missing_directory_and_unreadable_inputs_raise_identically (tests.b5_analysis.test_auth_recorder_and_verdict_memo.RecorderSessionlessSemantics.test_missing_directory_and_unreadable_inputs_raise_identically) (index=12)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_auth_recorder_and_verdict_memo.py", line 627, in test_missing_directory_and_unreadable_inputs_raise_identically
    self.assertEqual(plain[0], "raise")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
AssertionError: 'ok' != 'raise'
- ok
+ raise


======================================================================
FAIL: test_missing_directory_and_unreadable_inputs_raise_identically (tests.b5_analysis.test_auth_recorder_and_verdict_memo.RecorderSessionlessSemantics.test_missing_directory_and_unreadable_inputs_raise_identically) (index=13)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_auth_recorder_and_verdict_memo.py", line 627, in test_missing_directory_and_unreadable_inputs_raise_identically
    self.assertEqual(plain[0], "raise")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
AssertionError: 'ok' != 'raise'
- ok
+ raise


======================================================================
FAIL: test_missing_directory_and_unreadable_inputs_raise_identically (tests.b5_analysis.test_auth_recorder_and_verdict_memo.RecorderSessionlessSemantics.test_missing_directory_and_unreadable_inputs_raise_identically) (index=14)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_auth_recorder_and_verdict_memo.py", line 627, in test_missing_directory_and_unreadable_inputs_raise_identically
    self.assertEqual(plain[0], "raise")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
AssertionError: 'ok' != 'raise'
- ok
+ raise


----------------------------------------------------------------------
Ran 34 tests in 0.472s

FAILED (failures=5)

```

tests.b5_analysis.test_claim_gate_kept_quads: <Ran 31 tests in 3.938s> <OK>

tests.b5_analysis.test_deadline_tripwire: <Ran 7 tests in 199.610s> <OK>

tests.b5_analysis.test_fill_adapter: <Ran 11 tests in 1.179s> <OK>

tests.b5_analysis.test_frozen_files: <Ran 3 tests in 1.162s> <OK>

tests.b5_analysis.test_kept_units: <Ran 47 tests in 15.826s> <OK>

tests.b5_analysis.test_leaf_whole_window: <Ran 22 tests in 101.422s> <OK>

tests.b5_analysis.test_neg8_predicate: <Ran 6 tests in 2.100s> <OK>

tests.b5_analysis.test_reported_cell: <Ran 16 tests in 0.158s> <OK>

tests.b5_analysis.test_s10_chain_defects: <Ran 34 tests in 13.467s> <OK>

tests.b5_analysis.test_sibling_pinset: <Ran 24 tests in 4.827s> <OK>

tests.b5_analysis.test_step4_exit_classes: <Ran 26 tests in 0.019s> <OK>

tests.b5_analysis.test_validator_context: <Ran 47 tests in 359.520s> <FAILED (errors=3)>

### Failure details: `tests.b5_analysis.test_validator_context`

- ERROR: `test_adapter_no_context_three_cases_match_pinned_base`
- ERROR: `test_no_context_blocks_1_to_3_byte_identical_to_pinned_base`
- ERROR: `test_non_archive_session_attribute_matches_pinned_base_on_stored_failure`

**Likely cause:** Environment (missing git tag/branch, missing tool/file, network issue, or timeout indicated by the retained output).

```text
....fatal: path 'joulewise/whole_window.py' exists on disk, but not in 'b039c0257d1b1d407ee9598222db3f78f6ad7beb'
E................fatal: path 'joulewise/whole_window.py' exists on disk, but not in 'b039c0257d1b1d407ee9598222db3f78f6ad7beb'
E..fatal: path 'joulewise/whole_window.py' exists on disk, but not in 'b039c0257d1b1d407ee9598222db3f78f6ad7beb'
E......................
======================================================================
ERROR: test_adapter_no_context_three_cases_match_pinned_base (tests.b5_analysis.test_validator_context.ValidatorContextTests.test_adapter_no_context_three_cases_match_pinned_base)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_validator_context.py", line 564, in test_adapter_no_context_three_cases_match_pinned_base
    base = manager.__enter__()
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/contextlib.py", line 141, in __enter__
    return next(self.gen)
  File "/workspace/JouleWise/tests/b5_analysis/test_validator_context.py", line 23, in pinned_base
    raw = subprocess.check_output(["git", "show", head + ":joulewise/whole_window.py"], cwd=fx.ROOT)
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 472, in check_output
    return run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
               **kwargs).stdout
               ^^^^^^^^^
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 577, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', 'show', 'b039c0257d1b1d407ee9598222db3f78f6ad7beb:joulewise/whole_window.py']' returned non-zero exit status 128.

======================================================================
ERROR: test_no_context_blocks_1_to_3_byte_identical_to_pinned_base (tests.b5_analysis.test_validator_context.ValidatorContextTests.test_no_context_blocks_1_to_3_byte_identical_to_pinned_base)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_validator_context.py", line 742, in test_no_context_blocks_1_to_3_byte_identical_to_pinned_base
    base = manager.__enter__()
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/contextlib.py", line 141, in __enter__
    return next(self.gen)
  File "/workspace/JouleWise/tests/b5_analysis/test_validator_context.py", line 23, in pinned_base
    raw = subprocess.check_output(["git", "show", head + ":joulewise/whole_window.py"], cwd=fx.ROOT)
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 472, in check_output
    return run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
               **kwargs).stdout
               ^^^^^^^^^
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 577, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', 'show', 'b039c0257d1b1d407ee9598222db3f78f6ad7beb:joulewise/whole_window.py']' returned non-zero exit status 128.

======================================================================
ERROR: test_non_archive_session_attribute_matches_pinned_base_on_stored_failure (tests.b5_analysis.test_validator_context.ValidatorContextTests.test_non_archive_session_attribute_matches_pinned_base_on_stored_failure)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_validator_context.py", line 101, in test_non_archive_session_attribute_matches_pinned_base_on_stored_failure
    with pinned_base(self, "s3_invalid_context_base") as base, fx.adapter_projection(case):
         ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/contextlib.py", line 141, in __enter__
    return next(self.gen)
  File "/workspace/JouleWise/tests/b5_analysis/test_validator_context.py", line 23, in pinned_base
    raw = subprocess.check_output(["git", "show", head + ":joulewise/whole_window.py"], cwd=fx.ROOT)
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 472, in check_output
    return run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
               **kwargs).stdout
               ^^^^^^^^^
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 577, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', 'show', 'b039c0257d1b1d407ee9598222db3f78f6ad7beb:joulewise/whole_window.py']' returned non-zero exit status 128.

----------------------------------------------------------------------
Ran 47 tests in 359.520s

FAILED (errors=3)

```

tests.b5_analysis.test_vdl_shipping: <Ran 32 tests in 20.698s> <OK>

tests.b5_analysis.test_vdl_sol_w2: <Ran 20 tests in 33.153s> <OK>

- Finished: `2026-11-06T19:12:17Z` UTC
- Total elapsed: `868` seconds
