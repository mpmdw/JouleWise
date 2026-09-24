VERDICT: MERGE

Cold Fable 5.1 final pass, PR #396 (mpmdw/JouleWise), head 1fd2c79a753fe6fa75fb5ae36615697fee115341, base 313efcca. Judged from a detached worktree at that head (git status clean, nothing edited). Wall time about 20 min. No background work, no subagents.

## Summary

The change is tests-only, makes the test independent of trap-install timing, and does not weaken what the test proves: a driver with no SIGKILL escalation still fails it. The post-lens reap commit is safe. One reservation on the diagnosis: the real CI failure shows 26 TERMs in every red job, while a pure trap race produces exactly 2 TERMs on my bench. The fix still cures the most plausible reconciling mechanism (see Q3), and it cannot make CI worse, so it should merge. If the PR's own shard-1 job (pending at ruling time) still fails with 26 TERMs, the diagnosis is wrong and the next probe must run on Ubuntu, not on a Mac.

## Q1. Deterministic without weakening the proof: YES

Executed at HEAD (this worktree):

    python3 -B -m unittest tests.test_run_night.WindowDeadlineTests
    Ran 6 tests in 19.174s
    OK

Counterfactuals, each in a `git archive` copy under /tmp (never the worktree):

CF-A, HEAD test with the trap delayed 4 s (`/bin/sleep 4; trap "" TERM; : > ready; exec /bin/sleep 25`): PASS.

    Ran 1 test in 11.463s
    OK

The 11.5 s = 4 s hold + 2 s deadline + 5 s TERM census + KILL, so the whole TERM-then-KILL sequence ran.

CF-B, BASE test (313efcca) with the same 4 s delay: FAILS with the CI failure shape.

    AssertionError: <Signals.SIGKILL: 9> not found in [<Signals.SIGTERM: 15>, <Signals.SIGTERM: 15>] : a TERM-ignoring member must force the escalation
    Ran 1 test in 2.329s
    FAILED (failures=1)

CF-C, HEAD test against a driver copy with SIGKILL escalation removed (both `_signal_group(process_group, signal.SIGKILL)` and `observe(signal.SIGKILL)` changed to SIGTERM in `_terminate_process_group`): FAILS.

    AssertionError: 4 != 6      (EXIT_ABORTED expected; got the unproven-termination / courier-failed exit)
    Ran 1 test in 12.631s
    FAILED (failures=1)

So the fixed test still kills the escalation defect. It fails on the exit code before reaching the SIGKILL assertion, which is fine: without escalation the group is never proven gone.

Why the wait cannot move the deadline: `_run_chain_once` (scripts/run_night.py ~855-889) computes `deadline_monotonic` from `time.monotonic()` AFTER `_complete_chain_start` returns, and the fixture clock `now_epoch_s` is a constant, so the deadline is always 2 s after the wrapper returns. The `shutdown_monotonic` pre-computed path (~3200) applies only when `plan.quiet_admission` is set, which this fixture does not set. Verified by reading both sites.

## Q2. The reap commit 1fd2c79a: correct and safe: YES

- `pgid` comes from the real `_complete_chain_start`, which returns `process.pid`; the chain is launched with `start_new_session=True` (scripts/run_night.py:855, read this session), so the pgid is a fresh session/group id, never the test runner's own group.
- `ProcessLookupError` is swallowed, so on the success path (group already proven absent) the cleanup is a no-op. HEAD passing 6/6 exercises this path.
- Executed CF-D, HEAD test with `: > {ready}` removed (marker never appears):

      AssertionError: /tmp/tmp2takegl0/grandchild.ready never appeared within 10 s
      Ran 1 test in 10.461s
      FAILED (failures=1)
      after: no sleep 20/25 survivors      (pgrep -fl "/bin/sleep 2[05]" immediately after the run)

  No hang, clear message, and the chain group (sleep 20 and the TERM-ignoring sleep 25) was reaped by the cleanup. This is the leak Opus nit N1 described, now closed.
- Cleanup order: `addCleanup(reap)` is registered inside the test body, so it runs before setUp's patch stops and before the tempdir is removed (LIFO). The killpg spy is already out of scope by then, and even if active it forwards to the real `os.killpg`.
- Theoretical only: a pid reused as a new process-group id between test end and cleanup could receive the SIGKILL (or raise PermissionError if owned by another user). The window is milliseconds and the id must be re-issued as a group leader; not a merge concern.

## Q3. Is the diagnosis wrong in a way that leaves CI red: PARTLY UNRESOLVED, low risk

Executed: fetched both red main runs.

    gh run view 35923570037 --log-failed | grep "SIGKILL: 9> not found"   -> test (3.11, 1) TERM_count=26
    gh run view 35921839514 --log-failed | grep "SIGKILL: 9> not found"   -> test (3.13, 1) TERM_count=26

Exactly 26 TERMs in both jobs, both Python versions: one from `_terminate_process_group` plus 25 census iterations at GROUP_CENSUS_INTERVAL_S = 0.2 s, i.e. the full GROUP_CENSUS_WINDOW_S = 5 s window with a group member visible on every census except the last, which reported absent (a timeout or failed census returns not-absent by construction, `_group_census` ~3435, read this session; that would have escalated to SIGKILL).

A pure trap race does not produce that: CF-B above shows it empties the group at the FIRST census, giving exactly 2 TERMs. So the root-cause report's V3 reproduction (mock census absent on the 20th call) reproduces the count, not the mechanism. The report itself rates the cause "probable" and flags F1 (no Ubuntu observation).

The reconciling mechanism I find most plausible: on the Ubuntu runner the TERM-killed grandchild (no trap yet) lingers as a zombie in the chain's group until PID 1 reaps the orphan; Linux pgrep lists zombies; the census sees a member for the window and then absence. If that is the story, this PR cures it: the fixed test guarantees a LIVE trap-installed sleep is in the group (asserted via getpgid) before the deadline exists, and a live TERM-ignoring process cannot leave pgrep's census within 5 s, so SIGKILL must follow. The identical 26 count on 3 of 3 runs is more consistent with a deterministic shard-1 ordering effect than with a >2 s scheduling stall, but I could name no state that a preceding shard-1 module would leak into a freshly loaded driver and a fresh zsh; a Mac cannot probe Linux zombie/pgrep behaviour, so this is NOT EXECUTED.

Merge-risk framing: the PR cannot make any run redder (tests-only, base test was already failing, all six deadline tests pass at HEAD on this Mac). The only world in which CI stays red is one where a live TERM-ignoring sleep disappears from a Linux pgrep census within 5 s, for which I can name no mechanism. Decisive evidence is the PR's own run:

    run 35929745827 (head 1fd2c79a), created 2026-09-23T22:41:41Z; test (3.13, 1) still pending at 22:50Z.
    (The earlier run at 13e802d7 was cancelled by the second push; the previous red runs needed ~40 min to reach this test.)

NOT EXECUTED: waiting for that job (outside the 25 min budget). If shard 1 goes green the diagnosis is confirmed in effect; if it fails with 26 TERMs again, the next step is an Ubuntu-side probe that logs the census lines (zombie vs live member), not another Mac counterfactual.

Other CI-red checks, by reading: no new imports; `os.getpgid`, `signal`, `mock.patch.object(..., side_effect=...)` are 3.11-safe; `/bin/zsh` is installed by the CI job; the 10 s readiness timeout is generous for a zsh start.

## Q4. Should it merge: YES

Tests-only, strictly improves determinism, keeps the SIGKILL proof (CF-C), closes the leak (CF-D), and is safe. Merge; treat the pending shard-1 job as the confirmation of the diagnosis rather than of the change's safety. Opus nit N2 (a pid file read between create and write) remains theoretical and is not a blocker.

## Housekeeping

/tmp copies (pr396-head, pr396-base, pr396-cfA, pr396-cfC, pr396-cfD) removed after use. No repository file edited; no launchctl, sudo, or night-custody access.
