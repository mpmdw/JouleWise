<!-- Record 05 — execution-lens refuter (Opus subagent, read-only, worktree JouleWise-wt-ref-exec-28ff4b28 at e32ea56c). Report captured verbatim from the subagent hand-back by activation 28ff4b28. -->

# Execution-lens refutation — TEST-LARGE-FRAME-ARGV-PORTABILITY-01 (`6ec5b460..e32ea56c`, tests-only)

Worktree `/Users/edr/code/JouleWise-wt-ref-exec-28ff4b28` @ `e32ea56c`; scratch `/tmp/mag-28ff4b28/exec-refuter/`. Worktree left clean (`git status --short` empty). No writes outside /tmp.

## Findings

**1. should_fix — the new assertion can go green while blind (no positive-evidence floor).**
`max_arg_bytes` defaults to `0` in the row and is only ever set inside `argv_for`. The test asserts `assertLess(..., 131072)` with no lower bound, so if the recording ever stops running (refactor of `_BindTask` to a precomputed argv, a scenario where `argv_for` is not invoked), the test passes on all-zeros while the defect is present.
Demonstrated: mutant tree with the **pre-fix parent-side 200 000-char payload restored AND the one recording line deleted** (`/tmp/mag-28ff4b28/exec-refuter/mut2-tree`):
```
$ python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_large_frame_keeps_each_worker_argument_below_linux_limit
. Ran 1 test in 0.877s  OK
```
Green with a 200 885-byte argv string present. One extra line (`self.assertGreater(task['max_arg_bytes'], 0)`, or asserting the sample task exceeds some small floor) makes the instrumentation self-proving. Cheap; nothing else in the suite covers it.

**2. nit — the guard is MAX_ARG_STRLEN only, not total ARG_MAX.** Per-string was the observed CI failure, so this matches the defect; a future growth of the *number* of argv strings or the environment would not be caught. Largest observed total across all kinds is ~2.6 KB, so there is no present exposure.

## Confirmations (no finding)

**E1 — full class passes.** `python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests -v`
```
test_large_frame_is_incremental_and_still_bounded ... ok
test_large_frame_keeps_each_worker_argument_below_linux_limit ... ok
Ran 22 tests in 37.649s   OK
```
Wall time 37.9 s. Note `test_large_frame_is_incremental_and_still_bounded` still asserts `max_buffer > 200000` and passes — the 200 KB frame really does still reach the parent, so moving the expansion into the worker did not hollow out the pre-existing coverage.

**E2 — emulated Linux cap, fix head: verdict GO.** Driver `/tmp/mag-28ff4b28/exec-refuter/drive.py` patches `subprocess.Popen._execute_child` to raise `OSError(errno.E2BIG)` when any argv string (incl. NUL) exceeds 131 072 B, then runs `Bench('large_frame', tmpdir).run()` with a finally-block that SIGKILLs the process group of every launched task, closes both sockets and sweeps the fixture's `workers` registry.
```
fixture module: .../JouleWise-wt-ref-exec-28ff4b28/tests/night_gate_fixtures/bind_supervision.py
largest argv string seen at exec (bytes, incl NUL): 2643
verdict: GO      refusal: null
  census-1  kind=census  max_arg_bytes=247
  static-2  kind=static  max_arg_bytes=1908
  hard-3    kind=hard    max_arg_bytes=2623
  sample-4  kind=sample  max_arg_bytes=912
  census-5  kind=census  max_arg_bytes=247
  hard-6/7  kind=hard    max_arg_bytes=2643
```
Per kind: sample 912 B, census 247 B, static 1908 B, hard 2643 B — all ≥50× under the cap. Values are non-zero, so the new assertion is *not* vacuous at this head (contrast finding 1, which is about future blindness).

**E3 — counterfactual, base fixture refuses.** Same driver, `tests/` tree copied to `/tmp/.../base-tree` with only `bind_supervision.py` replaced by `git show 6ec5b460:...` (byte-identical, verified by `diff`); worktree `scripts`/`joulewise` supplied via PYTHONPATH.
```
fixture module: /tmp/mag-28ff4b28/exec-refuter/base-tree/tests/night_gate_fixtures/bind_supervision.py
largest argv string seen at exec (bytes, incl NUL): 200880
verdict: REFUSED
refusal: {"detail": "binding observation failed: ProbeError: OSError: [Errno 7] Argument list too long",
          "reason": "night_probe_error", "evidence": []}
```
Exactly the hosted-CI signature.

**Mutation kill (extra).** Fix-head tree with only the payload move reverted to parent-side (`/tmp/.../mut-tree`) — the new regression fails for the right reason, no emulation needed:
```
FAIL ... (job_id='sample-4', kind='sample')
AssertionError: 200885 not less than 131072
```
So the regression does kill a reintroduction of the defect shape, and 200 885 matches the brief's figure.

**E4 — reaping.** `pgrep -fl bind_supervision` is **non-empty, but contains zero fixture workers**: the 8 matches are concurrent sibling Codex seats (pids 38531/38648/38687/38692/38962/39104/39143/39149) whose *prompt text*, passed as an argv argument, contains the string `bind_supervision`. The precise check is clean:
```
$ ps -eo pid,args | grep -E 'python[^ ]*.* [^ ]*bind_supervision\.py' | grep -v grep
(no output)
```
Two transient python pids (40753, 40763) were seen mid-check and had already exited when inspected 2 s later; nothing persists. No orphaned workers, no zombies.

**E5 — flake.** New test alone, 5 consecutive runs: `OK` every time, 0.860/0.872/0.877/0.878/0.879 s (`real` 1.06–1.08 s). No flake, no variance of interest.

same-signature: none found
