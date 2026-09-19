# Record 48 — magistrate diff gate + bench proof (gate-ledger rows 3/7/8/9/11), fix-forward `fix/2026-09-19-rendezvous-real-spawn-darwin-only` at `b3a95dc89b08b82e8297f9699faf12b1bebe1941` (lead, 2026-09-19 12:3x PDT)

## The defect on main `0c529f99`

Hosted CI shard `test (3.13, 3)` (Linux) failed `test_sample_quiet_predicate_evidence.LoadTests.test_load_worker_runs_its_window_after_the_rendezvous` in its two real-spawn subtests (`exit_delay=1`: exit 1 ≠ 0; `exit_delay=60`: exit 1 ≠ −15) with the worker dying on `FileNotFoundError: '<stdin>'`: the hosted shard runner feeds the test script to Python on stdin, and multiprocessing's spawn start method re-imports `__main__`, which does not exist as a file. The worker also calls native QoS, macOS-only — the same reason the real-load test has carried `@unittest.skipUnless(sys.platform == "darwin")` since seat 13. The subtests were added in fix round 4 (S1/S2) inside the fake-clock rendezvous test, and every local run was `-m unittest` on macOS, so neither the seats nor the bench replays saw the hosted shape. Lesson (queue data): a real-spawn subtest inside a cross-platform test needs the same guard as the real-load test; the delta re-audits checked mutations, not platform shape.

## The change (lead, one file, +7/−3 by moving a block)

The real-spawn ladder block moves verbatim into its own test `test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` decorated `@unittest.skipUnless(sys.platform == "darwin", …)`; the fake-clock rendezvous test keeps every assertion it had. No production change.

## Bench proof (lead, this session, in the fix worktree)

- `python -B -m unittest tests.test_sample_quiet_predicate_evidence`: 46 tests OK (7.0 s).
- Hosted shape reproduced: runner script on stdin, `sys.platform` forced to `"linux"` before import → **46 run, 3 skipped, 0 failures, 0 errors** (the three skips are the real-load test, the moved ladder test, and the QoS readback test — all darwin-only).
- Same stdin runner on the real platform (macOS): the only failures are the moved ladder test's two subtests and the real-load test — the darwin-only spawn tests that hosted Linux never runs; this is the stdin/spawn incompatibility, not a code defect, and it does not occur under `-m unittest`.

## Rows

- 3: this record is the dictated closure (one move + one decorator); no seat.
- 7/8: the magistrate authored and read the whole diff; nothing else changes; no prune needed.
- 9: the full replay of this module's neighbourhood is the two replays already on record for the identical production code (records 21 at the lane head, 34 on the integration tree); the change is a test-file move with the bench proof above; hosted CI on the PR head is the Linux proof.
- 11: hosted CI on the PR head (recorded in the addendum before merge); post-merge cross-unit review folded into the next activation's first slice.

## Verdict

MERGE-READY subject to refuter 47 (execution + contract, detached worktree) and hosted CI green on the PR head.

## Addendum — refuter 47 (Astra high, execution + contract, detached worktree)

CLEAN on the change: the diff is exactly the four added lines (removing them reproduces the base byte-for-byte); under a stdin runner with the platform forced to Linux all three darwin tests skip and nothing fails; on the native platform via stdin only the two spawn-based methods fail (the QoS readback test passes — its `python -c` subprocess is not multiprocessing); `-m unittest`: 45 OK (the live-collection integration test excluded in its run); mutants `cleanup-silent` (killed by the moved ladder test) and `window-skip` (killed by the fake-clock rendezvous test) both die. R4: the guard costs hosted Linux the ladder and N3 pipe-cleanup coverage; the honest improvement is a file-based (importable) CI shard runner so spawn can re-import `__main__` — QUEUE DATA (lane candidate CI-SHARD-RUNNER-FILE-BASED-01), not this four-line fix-forward.

## Addendum 2 — a second hosted-only failure in the same module (main `42d3849e`, shard `test (3.13, 1)`)

`test_real_collect_no_power_reaps_all_recorded_workers` (real `collect --no-power` subprocess) returned rc 1 on hosted Linux. Cause: the harness's census and power-policy probes are macOS commands (`pmset`, `sysctl`, the census `pgrep` dialect); on Linux every round errors, and fix round 4's S3 rule (an all-error session sets `session["error"]` and exits 1) turned what used to be a silent exit 0 into the honest exit 1 — so this test was passing on Linux only because the harness was hiding the error before round 4. It is a macOS bench test like the real-load test; guarded darwin-only with the reason stated (`23c4bc4c6a9b4cd70f4e9fc95a3b476844c97ec4`). Bench: module 46 OK; the hosted shape with the platform forced to Linux: 0 failures (4 skips now). Not seen earlier because the first red run's other shards were cancelled fail-fast. Queue data with the file-based-runner lane: a Linux-neutral collect smoke (fake probes) would keep the reaping proof cross-platform.
