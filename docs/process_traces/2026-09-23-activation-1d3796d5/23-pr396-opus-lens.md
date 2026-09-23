**Verdict: MERGEABLE.** No blockers and no should-fix findings. Two nits.

I reviewed PR #396 at head 13e802d7 against base 313efcca. The diff changes 20 lines in `tests/test_run_night.py` and nothing in production code. On this Mac the full `WindowDeadlineTests` class passes 6/6 at head in 18.7 s, since `pgrep` works here.

**(1) The diagnosis is right, and the wait does not weaken what the test proves.**
- In `_run_chain_once` (`scripts/run_night.py` ~871), the chain is started by `Popen(start_new_session=True)` and then `_complete_chain_start` runs. The wrapper blocks inside that call. So the chain process group already exists, and the grandchild has been forked (the ready marker is written after `trap "" TERM`).
- The deadline is built after the wrapper returns. `deadline_monotonic` is `time.monotonic() + (deadline_epoch_s - probes.now_epoch_s())`, computed at ~887. The fixture's `ProbeSource.now_epoch_s` is a constant (t0+1), so the deadline always lands 2 s after the wrapper returns, however long the wait took. Only then does `_WindowDeadline.start()` launch the watchdog thread.
- The one path that fixes the deadline before chain start is `shutdown_monotonic` at ~3200. It is only used when `plan.quiet_admission` is set, and this fixture's plan does not set it. So the wait cannot push the deadline into the past.
- Executed: I delayed the trap by 8 s. The fixed test passed in 15.75 s (8 s wait + 2 s deadline + 5 s TERM census window + KILL), so the full TERM-then-KILL sequence ran. The base test with the same 8 s delay failed with `SIGKILL not found in [SIGTERM, SIGTERM]`, which is the CI failure shape.
- The added assertion `pgid == os.getpgid(grandchild)` also pins the premise that the grandchild is in the group being killed.

**(2) The test still kills the defect it was written for.**
- I made a /tmp copy of the tree and removed every SIGKILL from `_terminate_process_group`: the explicit `_signal_group(..., SIGKILL)` and also `observe(signal.SIGKILL)`, which re-sends SIGKILL on every census retry.
- The fixed test FAILED: `AssertionError: 4 != 6` on `EXIT_ABORTED`. That means the run ended with termination unproven (courier suppressed). It failed at the first assertion, before reaching the SIGKILL check.
- Why both SIGKILLs had to go: removing only the explicit call is an equivalent mutant, because the census loop in `_prove_group_absent` still sends SIGKILL as its first act. That is not a gap in the test.

**(3) No hang if the ready marker never appears; a leak, but it ends by itself.**
- Executed: I removed `: > {ready}` from the recipe. The test failed in 10.46 s with the clear message `grandchild.ready never appeared within 10 s`. No hang.
- **Nit N1:** that failure leaks the chain's process group. `/bin/sleep 20` and the TERM-ignoring `/bin/sleep 25` were still alive after the test (I saw them with `pgrep`). The AssertionError is raised inside the patched `_complete_chain_start`, before any deadline or termination exists. The processes end on their own within about 25 s and use their own group id, so I found no effect on neighbouring tests. An optional hardening: in the wrapper, `self.addCleanup(lambda: _kill_quietly(pgid))` straight after `complete_start` returns.

**(4) Other flakes of the same kind.**
- **Nit N2:** the wrapper waits for the pid file to exist, then reads it with `int(grandchild.read_text().strip())`. zsh's `echo $! > file` creates the file before it writes the number, so a read in between would raise `ValueError: ''`. The window is microseconds, and the ready marker, awaited first, is written only after the grandchild has started a new zsh and installed its trap. So this is theoretical. A fix would be to write to a temporary name and rename it, or to retry the read until it parses.
- The other tests in `WindowDeadlineTests` have no dependence on when a trap is installed. The sibling grandchild test uses plain `sleep 25` and only needs TERM. The abort-budget test already carries an 8 s margin from an earlier fix.
- Across the other SIGTERM-ignoring fixtures in `tests/` (`test_node_worker`, `test_sampler_teardown`, the `test_calibration_exits` stubborn-child test), readiness is signalled after `SIG_IGN` is installed. One exception is the ownership-cycle test at ~2872: the parent writes ready without waiting for the child's `SIG_IGN`. That test only asserts that no processes survive, and a TERM that arrives early makes that easier to satisfy, so it is not this failure mode.

**Not verified:** the Ubuntu shard-1 replay that the root-cause report asks for (its flag F1). The cause is still rated *probable* until hosted CI passes on 3.11 and 3.13. The counterfactuals above show the fix holds against any trap delay up to at least 8 s.

I left no files behind: the /tmp copy was deleted after use, and nothing in either worktree was edited.