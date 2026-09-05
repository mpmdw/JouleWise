```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The refreshed merge-base mission delta is scope-clean, its focused module passes, and both added guards fail under discriminating counterfactual mutations.",
  "workspace": {"base_requested":"65d0a821113f597bcbdd1309a4f4c24e0cdf2d66","base_mode":"exact","head_start":"65d0a821113f597bcbdd1309a4f4c24e0cdf2d66","head_end":"65d0a821113f597bcbdd1309a4f4c24e0cdf2d66","upstream_end":"65d0a821113f597bcbdd1309a4f4c24e0cdf2d66","branch":"feat/2026-09-04-fan-CALEXITS-HYGIENE-FIXES-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/CALEXITS-HYGIENE-FIXES-01/02-refuter-merge-base.md"],
  "unowned_dirty": [],
  "verdict": {"gauntlet":"LANDABLE","findings":[]},
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"base=$(git merge-base origin/main HEAD); git diff --name-status \"$base\"..HEAD; git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["A\tdocs/process_traces/2026-09-04-fanout/CALEXITS-HYGIENE-FIXES-01/01-sol-report.md","M\ttests/test_calibration_exits.py"]},"expected":{"exit_code":0,"tail_regex":"01-sol-report\\.md\\nM\\s+tests/test_calibration_exits\\.py$"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest -v tests.test_calibration_exits","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 47 tests in 634.434s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 47 tests in [0-9.]+s\\n\\nOK"}},
    {"id":"V3","kind":"test","cmd":"python3 -c 'import sys,unittest; import tests.test_calibration_exits as m; original=m.PublicGovernedExitWitnessTests._writer_env; m.PublicGovernedExitWitnessTests._writer_env=lambda self,state,*,mode:{**original(self,state,mode=mode),\"JW_FAKE_TIME_ORIGIN\":str(m.time.time())}; result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(\"tests.test_calibration_exits.RefusalInventoryTests.test_default_writer_origin_never_reads_the_ambient_wall_clock\")); sys.exit(0 if result.wasSuccessful() else 1)'","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Ran 1 test in 0.001s","","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"AssertionError: logical writer read ambient wall time[\\s\\S]*FAILED \\(failures=1\\)"}},
    {"id":"V4","kind":"test","cmd":"python3 -c 'import errno,sys,unittest; import tests.test_calibration_exits as m; m._CLEANUP_RACE_ERRNOS=frozenset({errno.ENOTEMPTY,errno.ENOENT,errno.EACCES}); result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(\"tests.test_calibration_exits.CalibrationExitReliabilityTests.test_absent_pack_child_never_masks_a_raised_cleanup_errno\")); sys.exit(0 if result.wasSuccessful() else 1)'","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Items in the first set but not the second:","13","","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"Items in the first set but not the second:[\\s\\S]*13[\\s\\S]*FAILED \\(failures=1\\)"}},
    {"id":"V5","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V6","kind":"inspection","cmd":"git diff --name-only e6f500ca^..0202ce9a","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["tests/test_calibration_exits.py"]},"expected":{"exit_code":0,"tail_regex":"^tests/test_calibration_exits\\.py$"}}
  ],
  "flags": []
}
```

## Findings

None.

## Evidence

HEAD was exactly `65d0a821113f597bcbdd1309a4f4c24e0cdf2d66`. The review range was `b0ed6991c11f3a515ad293760c6dfc031adda8e1..HEAD`, where the left endpoint was computed with `git merge-base origin/main HEAD`. Its only paths were the declared-scope test module and seat report. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` had no delta.

The touched module passed all 47 tests. The H1 counterfactual is a writer environment whose default origin calls ambient `time.time()`; the new test failed on that process-local mutation with `logical writer read ambient wall time`. The E-4 counterfactual is an errno allowlist widened with `EACCES`; the new exact-set assertion failed on member `13`. Both mutations vanished when their Python processes exited, and the repository was never edited for mutation testing.

The seat's two other claims reproduced: `git diff --check` passed, and the historical seven-commit implementation range changed only `tests/test_calibration_exits.py`; all seven commits were also confirmed as ancestors of the seat's requested base. No previous refuter verdict exists in this directory or its Git history, so there was no previous-round non-staleness blocker to re-test.

## Residual risk

None within the mission delta. This review intentionally did not re-review implementation already below the computed merge base and did not run the whole suite.
