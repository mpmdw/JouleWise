FINAL PASS: FAIL

Second cold final pass on `aba27481` (PR #475, queue row A6 V5-LAUNCH-REALIZATION-RECHECK-01).
Reviewer: Fable 5.1, no prior context. Scope: `scripts/`, `joulewise/`, `tests/` in
`git diff 784d12f1..aba27481` (784d12f1 is the merge base with main).

The product code is sound on every question asked, and both findings of the first pass
(F1, F2) are cured. The FAIL is for one thing only: the regression test that guards the
earlier blocker ("driver dies during the recheck, the launcher must stay in custody") is
RED at this head on any machine where `/bin/ps` works, and green only where `ps` cannot
run. The fix is a few lines in the test; no product change is needed for it (G1).

Terms used below. "Driver" = `scripts/run_night.py`. "Launcher" = `scripts/launch_window.py`.
"Recheck" = the launcher re-deriving the identity projection and comparing it with the
frozen one. "Pending record" = `night/launch.pending`, written by the driver with the
launcher's process id (pid), process-group id (pgid) and start time. "Closure" = a later
record proving that launch attempt is over: `chain.exited` or the new `launch.resolved`.
"Dead-man" = the scheduled fallback that sends the night's report if the driver did not.
"Census" = `joulewise/measurement_liveness.py`, which a harvest runs to ask "is any
measurement still alive under this custody parent?".

## Answers to the five questions

1. **Ruled property: MET.** `launch_window.py:343` runs the recheck directly after
   `verify_consumed_launch` and before `execve` (`:359`). A mismatch prints
   `readiness_identity_environment_dirty`, exits 2, and the driver never calls
   `_claim_chain_start` (`run_night.py:1212-1234`). A clean launch claims exactly once
   (`run_night.py:1117-1123`) through main's own `_claim_chain_start` /
   `_complete_chain_start`, so `chain.started` has main's four fields (`pid`, `pgid`,
   `epoch_s`, `start_time`). Tests with a real launcher child confirm both directions.
2. **Collection without a claimed start: no, for the real launcher.** The launcher
   `execve`s only after the driver answers `G`, and the driver sends `G` only after
   writing `chain.started`. **Claim without a recheck PASS: only the deliberate
   conservative one** (first-byte timeout, `run_night.py:1076-1090`), which exists so a
   harvest reads RECOVER rather than NULL. **Deadlock: none found.** Every launcher wait
   ends on driver death (end-of-file on the socket); the driver's first wait is bounded
   at 30 s and the rest by the window-deadline thread. **Stale record blocking later
   windows: cured for every path where the driver survives** (see F1 below); a small
   residual remains when the driver itself dies (G3).
3. **Non-pack paths: behaviourally identical to main.** DIAGNOSTIC_NO_PACK and
   REHEARSAL_STUB still claim before launch (`run_night.py:3801`), get no socket and no
   extra `Popen` argument, and every new branch is gated on `claim_descriptor is None`
   or on `launch.pending` existing. The only added work is `stat` calls on an absent file.
4. **Same derivation: YES.** `_recheck_identity_projection` (`launch_window.py:272-296`)
   calls the existing `identity_pins` helpers with the same four-clause comparison as
   `joulewise/arm_readiness_evidence_t0.py:1773-1786`, the site the ruling names. The
   compared `model_runtime_config` includes `runtime_identity_sha256`, a hash of the
   whole realized stack, so stack drift is covered. No second implementation.
5. **Tests: they kill the claimed regressions, except that one of them is red here (G1).**

## Were the first pass's findings cured?

**F1 (BLOCKER, a closed window's pending record refused later harvests): CURED.**
Readers now check closure before probing any process number
(`measurement_liveness.py:190-210`, `:213-218`; `run_night.py:3974-3985`). The driver
writes a closure on every path where it survives: `chain.exited` on a claimed exit, and
`launch.resolved` whenever `_terminate_process_group` proves the group gone
(`run_night.py:571-573`, `:623-631`). Re-run of the first pass's probe
(`stale_pending_demo.py`, real `ps` and `killpg`), same two cases that refused before:

| recorded pgid now names | first pass | now |
|---|---|---|
| unrelated same-user group (pgid 203) | `clear=False` | `clear=True`, no refusals |
| unrelated root group (pgid 337) | `clear=False` (indeterminate) | `clear=True`, no refusals |

**F2 (MAJOR, a launcher that does not speak the barrier collected with no
`chain.started`): CURED.** The first pass's `skew_probe.py` no longer exercises the path
(its stub plan has no `measurement_root`, so it refuses for the wrong reason), so I
rebuilt it (`/tmp/dd5-fable-a6b/skew2.py`, real `_run_chain_once`):

| case | result |
|---|---|
| measurement checkout holds main's `launch_window.py` (no barrier constants) | refused before `Popen`: "measurement launcher lacks the supported chain-start barrier"; collection did not run; night directory empty |
| constants present, process silent and still running at the timeout | "launcher first-byte timeout; collection start claimed conservatively"; `chain.started`, `chain.exited`, `launch.resolved` all written; group killed |

**F3 (MINOR, report delivery waited for the whole group): CURED** — a closed chain no
longer blocks the courier (closure is read first). **F1's fsync note: CURED**
(`run_night.py:619-620`). **F4 (NIT): CURED** — a malformed barrier variable now prints a
REFUSE document (`launch_window.py:302-312`, test passes). **F5 (NIT): unchanged and
now documented** in the launcher's module docstring.

## Findings

### G1 — MAJOR — the driver-death custody test is red wherever `ps` works

`tests/test_launch_window_realization_recheck.py:419-491` (assertion at `:486`);
fixture stub at `tests/test_run_night.py:397`; code path `scripts/run_night.py:3991`.

What happens. The test starts a real driver and a real launcher, kills the driver while
the launcher is inside the recheck, then calls the dead-man and expects it to refuse
(`night_chain_alive`). The pending record is written by the real driver, so it holds the
launcher's real start time. The dead-man is then run through the shared test fixture
`NightDriverTests`, whose `setUp` replaces `observe_identity` (the function that asks
`ps` for a pid's start time) with a constant "Tue Sep 8 01:02:03 2026". Round 5 added
`_record_pid_reused` to the dead-man's guard: "the pid is alive but its start time
differs from the record, so the number was reused by another process; the old launcher
is gone". Real start time versus the fixture's constant always differ, so the dead-man
concludes "reused", sends the report, and returns GO with the launcher still alive.

Evidence (this host, foreground, three runs):

| run | result |
|---|---|
| test as written, real `ps` (twice) | FAILED: `AssertionError: 0 != 3` at `:486` |
| same test with `JOULEWISE_IDENTITY_PROBE=/usr/bin/false` (identity probe unavailable) | passed |
| same test body, dead-man given the real `observe_identity` (`/tmp/dd5-fable-a6b/faithful.py`) | passed: the dead-man refuses |

So the product behaves correctly in this scenario; the test is wrong for round 5. The
first pass reported this file fully green at the previous head with real `ps`, so round 5
introduced the failure. It is green only where `ps` cannot run, and there the pending
record's `start_time` is null, which means the green run never exercises the start-time
comparison round 5 added.

Why it fails the pass. This is the only test that proves the earlier blocker (driver
death before PASS lost launcher custody) stays fixed, and it is deterministically red on
the measurement host. Merging puts a red test on main.

Fix direction (test only). Inside the `try` at `:481`, give `case.driver` the real
identity probe for the `dead_man` call (or a stub returning the start time recorded in
`launch.pending`). Keep the existing separate test for the "reused pid" branch.

### G2 — MINOR — the dead-man now believes a start-time text mismatch over the group probe

`scripts/run_night.py:3960-3972`, `:3991`, `:4067-4069`; `joulewise/measurement_liveness.py:56`.

On main the dead-man decided "is the chain alive?" only with `os.killpg(pgid, 0)`, which
asks the kernel whether any process in that group exists. Now, if the recorded start-time
text differs from the text `ps` prints today for the same pid, the dead-man skips the
kernel probe, treats the launcher as gone, and (when `chain.started` exists) writes
`chain.exited` itself. G1's red test is a live demonstration of that branch firing on a
launcher that is alive. In production the two texts differ for one live process only if
the time zone differs between the process that wrote the record and the one that reads
it: `ps -o lstart=` printed "Sun Oct 4 21:40:37 2026" and, under `TZ=UTC`,
"Mon Oct 5 04:40:37 2026" for the same pid. The driver and dead-man both run under
launchd, so I expect the same zone and no effect today; the census already had this
sensitivity on main for `chain.started`. Cheap hardening for a follow-up row: pin `TZ`
in `observe_identity`'s environment (it already pins `LC_ALL`), or compare an epoch
rather than text. I did not verify the launchd environments.

### G3 — MINOR — a pending record the driver never closed stays open for good

`scripts/run_night.py:4041-4047` (dead-man passes the guard but writes no closure);
`joulewise/measurement_liveness.py:213-239`.

If the driver dies between writing `launch.pending` and writing a closure, nothing ever
closes that record: the dead-man proves the group gone and moves on without writing
`launch.resolved`. Later censuses then probe that old pid/pgid every time. Probe
(`/tmp/dd5-fable-a6b/residual.py`, real `ps`/`killpg`, unclosed record):

| old pgid now names | census |
|---|---|
| a live group leader, record has a start time | clear ("stale reused PID") |
| nothing | clear ("stale dead pending process group") |
| a group whose leader exited but a member survives (classic daemon shape) | REFUSES: "live measurement owner process group" |
| a live pid, record's `start_time` is null (`ps` failed at write time) | REFUSES: "census indeterminate" |

Both refusing rows need a driver crash in the few seconds of the launch plus an
unlucky number collision, so this is far rarer than F1 was, and it fails toward
"refuse". Fix direction: let the dead-man write `launch.resolved` when its own
`killpg` probe says the group is absent.

### G4 — NIT — a launcher that carries the barrier constants but stays silent and exits within 30 s

`scripts/run_night.py:634-656`, `:1129-1131`, `:1212-1234`. Probe case (c) in
`skew2.py`: constants present, process writes its marker and exits 0 in 1 s. Result:
"launcher exited before passing its launch recheck", collection ran, no `chain.started`.
The constants and the handshake live in the same file, and a real collection outlasts
30 s, so I do not consider this reachable; noted because the capability check proves
the constants exist, not that the handshake is spoken.

### G5 — NIT — window deadline firing at the instant of the claim

`scripts/run_night.py:869-873` reads "does `chain.started` exist?" without a lock
shared with the claim at `:1118-1123`. If the window deadline (hours after launch) fires
in that instant, `chain.started` is left without `chain.exited`; `launch.resolved` is
still written and the dead-man later closes the chain. The harvest reads RECOVER, the
conservative side.

### G6 — NIT — only one exception type maps to the ruled code

`scripts/launch_window.py:275-285`. `IdentityPinProjectionError` and any mismatch print
`readiness_identity_environment_dirty`. A bare `OSError` from the helpers would print
`launch_consumption_invalid`, and any other exception a traceback. Nothing `execve`s in
either case and the T-0 author has the same shape, so the ruled safety property holds.

## What I ran (all on this checkout's code; host load average about 28)

- `tests/test_launch_window_realization_recheck.py`: 19 passed, 1 failed (G1), 31 s.
- `tests/test_measurement_liveness.py`: 29 passed, 39 subtests.
- `tests/test_run_night.py` (whole file): 255 passed, 11 failed, 289 s. Eight failures
  are installer tests listed in `base-failures-8fa002f7.txt` (lines 23-33, local
  environment). Three are `BindSupervisionProcessTests` ("external watchdog (8 s)"),
  which this change does not touch and which are not in that list. They are load
  timeouts: on a re-run of that class a different subset failed (2 failed, 20 passed),
  and the two failing scenarios run directly, outside the 8 s watchdog, completed
  correctly in 7.1 s (`startup_hang`) and 8.2 s (`blocked_journal`) at load about 22.
- Probes in `/tmp/dd5-fable-a6b/`: `stale_pending_demo.py`, `skew_probe.py` (both
  copied from the first pass), `skew2.py`, `residual.py`, `faithful.py`.

## What I did not verify

- `tests/test_launch_window.py`: a subset of the changed classes ran one test in 330 s
  under load and was stopped by my timer. Not verified.
- Protocol deviation: my first combined test run exceeded the tool's 400 s limit and
  was moved to the background by the harness. I stopped it and confirmed no process
  remained; every later run was in the foreground under a hard kill timer.
- The cost of the recheck on a real pack (it runs the runtime probe and file hashing in
  the launcher just before the chain starts). No pack, model or window was touched.
- Hosted CI status for this head, and the launchd environments (G2).

No file in the checkout was edited and no git command that writes was run.
