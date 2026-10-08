# The whole test suite at `9395cecfb` (run 8, 2026-10-07)

## What this record is

The **whole suite** is every test module of the repository, run on one commit. The merge rules of this project
require it for code that bears on a measurement. This record is the run at commit
`9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`, the merge of the seal-landing lane into the
integration branch `integrate/2026-10-07-int5`. That commit is not the head the block was sealed at: the sealed
head, **H_claim** (`a64000884ef5bb4b76415835f02f39803f6eb620`, the last commit that changes anything a measurement
window reads), came later, and since this commit it changed no file under `joulewise/` or `scripts/` and, under
`configs/`, only the flag catalog and the refusal allowlist. The run at the seal commit is `20-whole-suite.md`
beside this file.

The seat that ran the suite was stopped before it wrote its record, so this record was written on 2026-10-08, by
the seat that assembled the seal's record commit, from the logs in
`/Users/edr/night-archive/gate-prune/frozen-suite-int5-8/` and the run's notes
(`/Users/edr/night-archive/gate-prune/wave-1007b/suite8/NOTES.md`). Every quoted line below was copied from a log
by a script, not typed.

## How it was run

In a detached worktree at that commit, with the interpreter `/opt/homebrew/bin/python3.13 -B` and
`TMPDIR=/private/tmp/int5suite8`. The method is the one CI's "Unit tests" job uses, split six ways: a **shard** is
one of six parts into which the ordinary test modules are divided so that the parts take about equal time. The six
shards ran at the same time, each as one Python process whose program text (`shard_runner.py`) was fed to it on
standard input. Two modules that must not run beside anything else (`tests.test_calibration_exits` and
`tests.test_calibration_writer_crash_matrix`, the **exclusive** modules) ran afterwards, one at a time. The run
ended at 22:41 PDT (`run.out` holds the line `ALLDONE`).

## Result

**9,842 tests: 9,774 in the six shards and 68 in the two exclusive modules. Shards 2, 5 and 6 and both exclusive
modules passed. Shards 1, 3 and 4 reported five failures between them, in three modules. All five pass when
their module is run alone.**

The last line of each shard's log:

```
SHARD SUMMARY index=1/6 modules=65 tests=1414 failures=3 errors=0 skipped=4 result=FAIL
SHARD SUMMARY index=2/6 modules=65 tests=1472 failures=0 errors=0 skipped=21 result=PASS
SHARD SUMMARY index=3/6 modules=64 tests=1717 failures=1 errors=0 skipped=6 result=FAIL
SHARD SUMMARY index=4/6 modules=65 tests=1834 failures=0 errors=1 skipped=11 result=FAIL
SHARD SUMMARY index=5/6 modules=64 tests=1711 failures=0 errors=0 skipped=12 result=PASS
SHARD SUMMARY index=6/6 modules=64 tests=1626 failures=0 errors=0 skipped=7 result=PASS
```

The last four lines of each exclusive module's log:

```
excl_exits.log:
----------------------------------------------------------------------
Ran 48 tests in 478.878s

OK

excl_crash.log:
----------------------------------------------------------------------
Ran 20 tests in 234.167s

OK
```

The failing tests, as the shard logs name them:

```
shard1.log: FAIL: test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child (test_sample_quiet_predicate_evidence.LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child) (exit_delay=1)
shard1.log: FAIL: test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child (test_sample_quiet_predicate_evidence.LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child) (exit_delay=60)
shard1.log: FAIL: test_real_load_tracks_point_one_core_and_guards_worker_budget (test_sample_quiet_predicate_evidence.LoadTests.test_real_load_tracks_point_one_core_and_guards_worker_budget)
shard1.log: MODULE FAIL tests.test_sample_quiet_predicate_evidence tests=96 failures=3 errors=0 skipped=0 seconds=26.804
shard3.log: FAIL: test_delivered_courier_journal_assembles_with_observed_exit_and_timeout (test_v5_s1_qualification.QualificationSubsetTests.test_delivered_courier_journal_assembles_with_observed_exit_and_timeout) (still_running=True)
shard3.log: MODULE FAIL tests.test_v5_s1_qualification tests=23 failures=1 errors=0 skipped=0 seconds=47.935
shard4.log: ERROR: test_worker_pool_matches_serial_assessment (test_harvest_b5_window.WorkerPoolTests.test_worker_pool_matches_serial_assessment)
shard4.log: MODULE FAIL tests.test_harvest_b5_window tests=182 failures=0 errors=1 skipped=0 seconds=518.545
```

## The five failures, each run again alone

Each module was run again by itself with `/opt/homebrew/bin/python3.13 -B -m unittest <module>`, same worktree and
`TMPDIR`. The last lines of each log:

```
rerun_tests.test_sample_quiet_predicate_evidence.log:
----------------------------------------------------------------------
Ran 96 tests in 29.488s

OK

rerun_tests.test_v5_s1_qualification.log:
----------------------------------------------------------------------
Ran 23 tests in 14.256s

OK

rerun_tests.test_harvest_b5_window_plus_seal_landing_flags.log
(tests.test_harvest_b5_window, tests.test_b5_seal_landing and tests.flags.test_flags_collect together):
----------------------------------------------------------------------
Ran 249 tests in 538.026s

OK
```

## Why four of the five fail inside the shard run: the runner was fed on standard input

Four of the five failures are not caused by machine load and say nothing about the code under test. They are the
three failures in `tests.test_sample_quiet_predicate_evidence` (class `LoadTests`) and the one error in
`tests.test_harvest_b5_window` (class `WorkerPoolTests`). Each of those tests starts worker processes with
Python's `multiprocessing`, and a worker process begins by running the parent's main program file again. When the
parent's program was fed on standard input, its main file is recorded as `<stdin>`, which is not a file; the
worker fails to open it and dies, and the test fails. The seat that ran the suite showed this by running the same
tests twice more, alone: with the runner's text on standard input they fail every time, and with the same text
saved as a file they pass.

```
probe_stdin_loadtests.log (runner text on standard input):
----------------------------------------------------------------------
Ran 11 tests in 0.238s

FAILED (failures=3)

probe_stdin_WorkerPoolTests.log (runner text on standard input):
----------------------------------------------------------------------
Ran 1 test in 3.872s

FAILED (errors=1)

probe_file_LoadTests.log (the same runner as a file):
----------------------------------------------------------------------
Ran 11 tests in 5.103s

OK

probe_file_WorkerPoolTests.log (the same runner as a file):
----------------------------------------------------------------------
Ran 1 test in 6.703s

OK
```

The fifth failure, `tests.test_v5_s1_qualification`
`test_delivered_courier_journal_assembles_with_observed_exit_and_timeout`, is a timing test: inside shard 3 a
child process it had signalled was still running after 30.2 s against a limit of 5 s. It passes alone, and it
also passes alone when the runner is fed on standard input
(`probe_stdin_test_delivered_courier_journal_assembles_with_observed_exit_and_timeout.log`: 1 test, OK), so its
cause is not the one above. The seat started a probe to find why the child outlives its signal inside the shard
(`probe_shard3_order.py`); the session was stopped before a conclusion was recorded. It is classed with the known
load-sensitive tests of this suite (courier timing).

The same five tests also failed in the earlier suite run that `21-frozen-head-4.md` records (suite head
`63d2b9bad`, for the frozen head `fe28e5a0c`). That record classed all five as load failures; the finding that
four of them come from the way the runner is fed was made in this run.

## The checks run beside the suite

At the same commit, before the suite (`checks.log`, `refusal_census_main.log`, `refusal_census_test.log`): nine
generator and pin checks, every return code 0 and every digest equal to the table of `21-frozen-head-4.md`; the
refusal census (the listing of every place where code stops collection or removes data, compared with the allowed
list `configs/gates/hazard_refusals.json`) returned 0 with all five of its lists empty, and
`tests.hazards.test_refusal_allowlist` ran 23 tests, OK. The last lines of `checks.log`:

```
PARITY_DIFF_EMPTY generator=GAMMA files=117
PARITY_OK generators=3 files=357 excluded=['generate_configs.py', 'plan_tree.json', 'plan_tree.sha256'] baseline=2011ec285
rc=0
== repin --check
PASS 16 pin families current
rc=0
== gen_derivation_night --check
PASS generated derivation-night wrapper region matches
rc=0
== file hashes
89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa  configs/campaigns/v5_claim_25g83/sizing_b5.json
a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9  configs/campaigns/v5_claim_25g83/identity_pins.json
d0a54d5a63eeafd69c4c5b15b7b152134b93228e3a631f39ba8511dd53c7142d  configs/gates/hazard_refusals.json
a4a2be94912c4a3c33b1fb04e0f91e9e691290e2a7b7ee98898783ff307033b2  configs/pins/registry.json
```
