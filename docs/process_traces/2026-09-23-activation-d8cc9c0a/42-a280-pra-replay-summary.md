# 42 — A280 PR A full local replay (magistrate, executed)

Head 50dc2272 in the detached worktree /Users/edr/code/wt-d8cc9c0a-a280a-review. Command: `/Users/edr/code/JouleWise/.venv/bin/python scripts/shard_tests.py --workers 8 --split`. Log: /tmp/d8cc9c0a-replay-50dc2272.log.

`WORKERS SUMMARY shards=8 modules=254 tests=7029 failures=1 errors=0 skipped=103 result=FAIL`

The single failure: `tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper` failed with `AssertionError: {'test_night_kinds.py': (63,)} != {}`. PR A's new test module initialised its base-archive git repository with a direct `git init` instead of the repository's shared helper `tests.git_fixture.init_git_fixture`, which disables detached auto-maintenance so a fixture's cleanup cannot race a detached git writer. This is a real defect in PR A's test, and it is new: it is not the class of the lens findings.

Bench fix (magistrate), commit **bedcc0ae** on `feat/2026-09-23-a280-kind-table`: line 65 now calls `init_git_fixture(BASE_SOURCE, "-q")`, imported at line 37. The only change is `tests/test_night_kinds.py`: 3 insertions, 1 deletion. After the fix, `python3 -B -m unittest tests.test_night_kinds tests.test_git_fixture_maintenance` ran 18 tests, OK.

Earlier bench runs: at 702afd8d, the 19-module acceptance ran 1,101 tests with 1 failure and 3 errors, all load flakes (the census `process.wait(timeout=5)` and the SIGTERM-timing test) that passed in isolation (Ran 2, OK). At 50dc2272, the 6 gate modules plus the two process-list tests ran 455 tests, OK.
