# SHARD4 unittest results

- Date: 2026-11-06
- Data: test/synthetic only
- Python: `Python 3.13.13`

tests.b5_analysis.test_attempt_record: Ran 33 tests in 5.551s OK
tests.b5_analysis.test_census_path_token: Ran 6 tests in 61.234s OK
tests.b5_analysis.test_context: Ran 43 tests in 127.372s FAILED (errors=1)

## tests.b5_analysis.test_context — environment (governing Git pin lacks the required path)

The test's governing commit `224a264c5faaae90cdf56118df37e773a932700b` is present, but its tree does not contain the required `joulewise/b5/harvest.py` path. This is a missing/incompatible Git-history input rather than a failure in the exercised code path.

```text
....fatal: path 'joulewise/b5/harvest.py' exists on disk, but not in '224a264c5faaae90cdf56118df37e773a932700b'
E......................................
======================================================================
ERROR: test_build_roster_and_projection_helpers_are_source_equal_at_governing_pins (tests.b5_analysis.test_context.ContextTests.test_build_roster_and_projection_helpers_are_source_equal_at_governing_pins)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_context.py", line 459, in test_build_roster_and_projection_helpers_are_source_equal_at_governing_pins
    source = subprocess.check_output(["git", "show", fx.PINS.pins[shape]["head"] + ":joulewise/b5/harvest.py"],
             ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        cwd=fx.ROOT).decode()
        ^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 472, in check_output
    return run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
               **kwargs).stdout
               ^^^^^^^^^
  File "/root/.pyenv/versions/3.13.13/lib/python3.13/subprocess.py", line 577, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', 'show', '224a264c5faaae90cdf56118df37e773a932700b:joulewise/b5/harvest.py']' returned non-zero exit status 128.

----------------------------------------------------------------------
Ran 43 tests in 127.372s

FAILED (errors=1)

```

tests.b5_analysis.test_dry_run: Ran 66 tests in 458.881s FAILED (errors=1, skipped=3)

## tests.b5_analysis.test_dry_run — code under test

The failure was produced by the test/code path rather than an identified missing tag, branch, tool, network dependency, or timeout.

```text
....................................................s....E.ss.......
======================================================================
ERROR: test_only_git_seams_replay_registered_history_and_tracked_index (tests.b5_analysis.test_dry_run.JoinedHarnessMockTests.test_only_git_seams_replay_registered_history_and_tracked_index)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/JouleWise/tests/b5_analysis/test_dry_run.py", line 1152, in test_only_git_seams_replay_registered_history_and_tracked_index
    energy._verify_gate_ordering(self.harness.repo)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/workspace/JouleWise/joulewise/paper_reported_energy.py", line 93, in checked
    return fn(*args, **kwargs)
  File "/workspace/JouleWise/joulewise/paper_reported_energy.py", line 266, in _verify_gate_ordering
    proof = verify_registration_ordering(repository, model)
  File "/workspace/JouleWise/tests/b5_analysis/joined_s10.py", line 224, in registered_history
    return ordering(d.ROOT, model)
  File "/workspace/JouleWise/joulewise/paper_reported_energy.py", line 227, in verify_registration_ordering
    raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid")
joulewise.paper_reported_energy.PaperReportedEnergyRefusal: paper_reported_energy_ordering_history_invalid

----------------------------------------------------------------------
Ran 66 tests in 458.881s

FAILED (errors=1, skipped=3)

```

tests.b5_analysis.test_fixture_shapes: Ran 23 tests in 320.793s OK
tests.b5_analysis.test_issuer: Ran 31 tests in 222.491s OK
tests.b5_analysis.test_leaf_bracket: Ran 20 tests in 352.776s OK
tests.b5_analysis.test_mint_kept_units: Ran 87 tests in 196.339s OK (skipped=2)
tests.b5_analysis.test_phase_timing: Ran 34 tests in 3.028s OK (skipped=1)
tests.b5_analysis.test_run_caches: Ran 15 tests in 132.911s OK
tests.b5_analysis.test_sensitivity: Ran 36 tests in 303.834s OK
tests.b5_analysis.test_sources_replay: Ran unknown tests in 1200 s TIMEOUT

## tests.b5_analysis.test_sources_replay — environment (timeout)

```text
......................
```


## Not run (48-minute start cutoff)

- `tests.b5_analysis.test_step4_reason_table`
- `tests.b5_analysis.test_vdl_kernel_resolution`
- `tests.b5_analysis.test_vdl_sol_hunt2`
