VERDICT: MERGE

# Cold Fable 5.1 delta pass, PR #396 at head 10b909a2 (2026-09-23)

Judged from: `git diff 1fd2c79a..10b909a2`, `git log -3`, `gh pr view/checks 396`,
the diagnostic Linux trail in run 35931353907, the driver's termination code
(`scripts/run_night.py` lines 76-90, 437-527, 3435-3457, 676-760, 870-1010) and
the executions below. No repository file edited; nothing under night-custody
touched; no launchctl/sudo. Detached worktree /Users/edr/code/wt-1d3796d5-fable396.

Precondition before the merge click (no new commit needed): the hosted
`gate-ledger` check is RED at 10b909a2 only because every ledger row still
cites `RUN 1fd2c79a...` ("item 12: sha is not the PR head"). Re-point the
twelve rows to 10b909a2998e008c5fe86d936e883a82183b3a30 and rerun the check.
All test jobs at 10b909a2 are green (build, quick, fences, installed-wheel,
calibration-exits, crash-matrix 1+2, test 3.13 shards 1-6; shard 5 finished
green while this pass ran). Shard 1, the failing shard since c741678b, passed.

## Q1. Cause established? Cure without weakening the test?

**Cause: established, by the trail plus the driver's code, not by inference.**

The driver's TERM phase is `killpg(TERM) -> wait(30) -> _prove_group_absent(TERM)`,
and `_prove_group_absent` RE-SENDS the signal every ~0.2 s for
GROUP_CENSUS_WINDOW_S = 5 s, returning `absent=True` the moment a census is empty
(lines 444-467). So a TERM-ignoring member that exits ON ITS OWN inside those
5 s makes the group "proven absent" under TERM alone, and SIGKILL never fires.
That is exactly the diagnostic trail (run 35931353907, shard 1):

    1049.93 absent=False ps=['11914 11913 1 SN 20 /bin/sleep 25']   # first census, etimes 20
    ...
    1054.75 absent=False ps=['11914 11913 1 SN 24 /bin/sleep 25']   # etimes 24
    1054.92 absent=True  lines=[] ps=[]                              # sleep 25 ended by itself

The 5 s phase covered grandchild elapsed 20-25 s; `sleep 25` ended at 25 s inside
the phase; the census emptied; `proven=True` with ~26 TERMs and zero KILLs. This
also reconciles the earlier pass's reservation: 26 TERMs is the re-signalling
census loop (5 s / 0.2 s), not a trap race; the pre-fix "2 TERMs on a Mac" was
the group dying at the first TERM. On this Mac at HEAD the same loop issued
15 census TERMs before KILL (trail below).

**Cure: sufficient and not a weakening.** With `sleep 300` the member cannot
self-exit inside any 5 s TERM phase that starts before elapsed 295 s, so the
only way the census empties is SIGKILL. The three assertions that carry the
test are unchanged (`proven` True, SIGKILL in the sent list, member dead
afterwards), and the N1 `addCleanup(reap)` SIGKILLs the group at teardown, so a
failing run cannot leak a 300 s sleeper.

Executed evidence (Mac, Python 3.13, unittest as CI runs it):

1. Whole class at HEAD:
       python3.13 -m unittest -v tests.test_run_night.WindowDeadlineTests
       Ran 6 tests in 17.514s  OK
2. Fixed test at HEAD with a printed census trail (my own wrapper around
   `_group_census`, driver untouched): first census at grandchild etime 00:03,
   15 TERM-phase censuses over 5.0 s all `absent=False` on `/bin/sleep 300`,
   the last census `census_failed: TimeoutExpired ... 0.0136 s` (the clipped
   end-of-phase timeout, reported as not-absent as designed), then SIGKILL and
   `absent=True lines=[] ps=[]` at +5.06 s. `ok`, 7.27 s.
3. Counterfactual: driver copy at /tmp/cf396/scripts/run_night.py with the
   SIGKILL escalation removed (line 516 `_signal_group(process_group,
   signal.SIGKILL)` -> `pass`; line 522 `observe(signal.SIGKILL)` ->
   `observe(signal.SIGTERM)`; the repo tree symlinked around it so imports
   resolve; `diff` shows exactly those two lines). Result:
       FAIL: AssertionError: 4 != 6   (EXIT_ABORTED expected, unproven-termination exit returned)
       Ran 1 test in 12.421s  FAILED (failures=1)
   `pgrep -lf "sleep 300"` afterwards: no leaked sleeper (the reap cleanup
   worked; the two `sleep 3000` on the machine are unrelated, pids 19517/60219).
   Run script: /tmp/cf396/runner.py (`head` | `nokill <driver>`).

Not executed: the base-head (pre-PR) test with an artificially late deadline;
the CI trail already shows that mechanism directly, so I did not spend budget
reproducing it.

## Q2. Diagnostic trail kept in the assertion message: acceptable?

Yes. Cost is one `ps -eo` per census, ~15-25 calls per run, tens of
milliseconds each, outside the clipped pgrep timeout; the 5 s phase is bounded
on monotonic time, so the extra call cannot extend the driver's stated 70 s
bound. The text renders only on failure. The wrapper passes the driver's
positional `(pgid, timeout_s)` call through unchanged and returns the real
census answer, so it observes and never alters the decision. Two nits, neither
blocking: the commit subject still says "DIAGNOSTIC (not for merge as-is)"
while the code is now permanent, so the squash/merge message should not carry
that phrase; and `trail[:3] + ["..."] + trail[-4:]` repeats entries when the
trail is shorter than seven, harmless.

## Q3. The ~18 s before the first census: production concern or CI matter?

CI/follow-up matter, not a merge blocker, and I state plainly that the cause
is NOT established. Facts: on this Mac the first census comes at grandchild
elapsed 3 s (2 s scaled deadline + ~1 s), i.e. on time. On the Linux runner the
first census came at elapsed 20 s, with the grandchild's ppid already 1 and no
other group member listed, and 20 s is exactly the chain's own `/bin/sleep 20`.
Two readings fit: the deadline fired on time but `process.wait(30)` only
returned when the chain shell reached its own end (a Linux/zsh signal-delivery
question for the fixture), or both enforcers fired ~18 s late (which WOULD be a
driver concern). The code after the main loop only `cancel()`s, never fires, so
a chain that ended before the deadline could not have produced
`night_window_exceeded`; the fire happened while the chain was still owed a
wait. Production runs the night driver on macOS under launchd, where the bench
shows on-time firing and `test_the_watchdog_fires_while_the_main_loop_is_blocked_on_the_volume`
passes. Follow-up lane, cheap: have the trail also print
`deadline_monotonic`, the `fire()` entry time and the `process.wait` return
time, so a late fire is distinguishable from a slow wait on the next Linux run.
If that shows a late fire, it becomes a driver lane.

## Q4. Verdict

MERGE at 10b909a2, tests-only, once the gate-ledger rows cite the head sha and
the check is green. Cause shown by executed trail, cure verified by execution,
counterfactual fails as required, nothing leaked, hosted test matrix green.
