FINAL PASS: PASS

Third cold final pass, delta-limited, on PR #475 (queue row A6). Reviewer: Fable 5.1, no
prior context. Scope: `git diff aba27481 8f4fbb71` only (five files, 78 lines added).
Checkout: detached `baa9bb7b`; the six files this change and its tests depend on are
byte-identical between `8f4fbb71` and `baa9bb7b`. Session 22:23 to 22:40 PDT 2026-10-04.

The three findings of the second pass are cured in the product code, the cures are
guarded by tests that fail when the cure is removed, and the delta introduces no blocker.
I pass it with two things the lead must know before merging, neither of which is a
defect in the product logic of this delta:

- **H1**: the driver-death test still errors in about 1 run in 9 on this Mac, from a
  cleanup line this delta did not touch. Its assertions passed in every run. A two-line
  test-only fix is given below and was tried 30 times clean.
- **H2**: the time-zone pin changes the bytes of every recorded start time, so code from
  before this change and code from after it disagree about one live process and read it
  as "gone". Nothing is alive on this host now, so landing is safe now; the landing
  condition is stated under H2.

Terms. "Driver" = `scripts/run_night.py`. "Launcher" = `scripts/launch_window.py`, started
by the driver as the leader of its own process group. "Pending record" =
`night/launch.pending`, which the driver writes with the launcher's process id (pid),
process-group id (pgid) and start time. "Closure" = a later file proving that launch
attempt is over: `night/chain.exited` or `night/launch.resolved`. "Dead-man" = the
scheduled fallback that sends the night's report when the driver did not. "Census" =
`joulewise/measurement_liveness.py`, which asks "is any measurement still alive?" before
a harvest. "Identity probe" = `observe_identity`, which runs `ps -p <pid> -o lstart= -o
stat=` and returns the process's start time as text, for example `Sun Oct 4 22:27:28
2026`. A reader calls a pid "reused" when the pid is alive but that text differs from
the text in the record. "Group probe" = `os.killpg(pgid, 0)`, which asks the kernel
whether any process is in that group: "no such process" means the group is empty,
"permission denied" means something is there that cannot be signalled.

## 1. G1 (driver-death custody test): CURED, with a separate flake (H1)

What the fix does (`tests/test_launch_window_realization_recheck.py:483-490`). The shared
fixture replaces the identity probe with a constant date. The real driver had written the
launcher's real start time, so the dead-man saw "different text, pid reused, launcher
gone" and sent the report. The test now hands the dead-man an identity whose start time
is read back from the pending record itself (`None` when the writer's probe failed), so
the reuse check sees equal text and falls through to the real group probe on the real,
living launcher.

Runs of that one test in the real checkout (foreground, load average about 15):

| condition | runs | assertions passed | whole-test result |
|---|---|---|---|
| real `/bin/ps` | 27 | 27 | 24 OK, 3 ERROR at `:517` (H1) |
| `JOULEWISE_IDENTITY_PROBE=/usr/bin/false` (probe unavailable) | 11 | 11 | 10 OK, 1 ERROR at `:517` (H1) |

The whole file (20 tests) ran OK once each way (25 s, 24 s).

Does it still test the custody property? Yes. Mutations in a scratch copy
(`/tmp/dd5-fable-a6c/tree`, never the checkout):

| mutation of `scripts/run_night.py` | real `ps` | probe unavailable |
|---|---|---|
| none (baseline) | OK | OK |
| M1: guard returns "no refusal" when the group probe finds the group alive (dead-man ignores a live pending launcher) | FAILED `0 != 3` | FAILED `0 != 3` |
| M2: reuse check drops the "start times differ" clause (any live pid counts as reused) | FAILED `0 != 3` | OK (expected: with no recorded start time that branch cannot run) |

`0 != 3` is "dead-man returned GO, expected REFUSED". M2 shows the real-`ps` run now
exercises the start-time comparison that round 5 added, which the old green-only-without-
`ps` run never did.

Faithful variant (my edit in scratch): the dead-man given the REAL identity probe instead
of the stub, with the driver subprocess under `TZ=Asia/Tokyo` and the dead-man under
`TZ=America/Los_Angeles`. With this change's census module: OK, 3 of 3 (one earlier run
errored at `:517` only, H1). With the pre-fix module swapped in: FAILED `0 != 3`. So the
product refuses correctly with a real probe, and the G2 pin is what makes it hold across
zones.

## 2. G2 (time-zone pin): CURED going forward; it changes recorded bytes (H2)

`joulewise/measurement_liveness.py:56` adds `"TZ": "UTC"` to the probe's environment.
Measured on one live pid, system zone PDT:

| reader's `TZ` | before the change | after the change |
|---|---|---|
| unset (system PDT) | `Sun Oct 4 22:27:28 2026` | `Mon Oct 5 05:27:28 2026` |
| `Asia/Tokyo` | `Mon Oct 5 14:27:28 2026` | `Mon Oct 5 05:27:28 2026` |
| `America/Los_Angeles` | `Sun Oct 4 22:27:28 2026` | `Mon Oct 5 05:27:28 2026` |

After the change the text no longer depends on the caller's zone, which is the cure.
The new test `tests/test_measurement_liveness.py:390` fails without the pin (3 failures;
checked by swapping the old module in).

Bytes that change: the `start_time` text in `night/chain.started`, `night/launch.pending`,
the `start_time=` field of `campaign.lock` (`scripts/run_campaign.py:3298-3302`) and each
`active-campaigns/*.json` registry entry. All four are written and compared only through
this one function. The magistrate watchdog keeps its own lock with its own `ps` reading
(`scripts/magistrate_watchdog.py:228`, `:1005`) and never compares against these records,
so it is unaffected. No other reader of these fields exists (grep of `scripts/`,
`joulewise/`). See H2 for the comparison with records written before the change.

## 3. G3 (closure written by a reader): CURED and safe

`scripts/run_night.py:3996` writes `launch.resolved` at exactly one point: after the
group probe on the recorded pgid answered "no such process". Three callers reach it
(`:1722`, `:1747` in the driver's own courier, `:4042` in the dead-man); each passes
`<this plan's custody_root>/night`, so the write lands only in the window that caller
belongs to. The census, which is the only reader that walks OTHER windows, still writes
nothing.

Probe with real processes and the real identity probe (`/tmp/dd5-fable-a6c/probe_g3.py`):

| state of the recorded group | guard result | `launch.resolved` written | census |
|---|---|---|---|
| leader and a member alive | REFUSE | no | refuses |
| leader exited and reaped, a member survives | REFUSE | no | refuses |
| same, record's start time null | REFUSE | no | refuses |
| only an unreaped zombie leader remains (macOS answers "permission denied") | REFUSE | no | refuses |
| whole group gone | passes | yes, `basis: group_absent`, correct pgid | clear |
| second call after that | passes via the closure, file not rewritten | unchanged | clear |
| no pending record at all | n/a | no | n/a |

So a closure is never written while any process, even a zombie, is still in the group.
The driver refuses a second fire into a night directory that already holds
`launch.pending` (`_WRITE_ONCE_RECORDS`, `run_night.py:142`), so a closure cannot be left
behind to close a later launch attempt in the same directory. No harvest script reads
`launch.resolved`; it changes only "is this pending record still open?".

Mutation M3 (write the closure on "permission denied" instead of on "no such process"):
4 of the 18 dead-man tests fail, including the new
`tests/test_run_night.py:2298`. The second pass's two refusing rows (leaderless group,
null start time) are the two sub-cases of that new test.

## Findings

### H1 — MINOR, fix now (test only) — cleanup probe in the driver-death test errors on a zombie

`tests/test_launch_window_realization_recheck.py:514-519`, raise at `:517`. Not in this
delta (the delta touches `:483-490` only); the second pass's deterministic failure at
`:486` sat in front of it.

Mechanism. After its assertions the test kills the launcher's group, then polls the group
probe every 20 ms until it answers "no such process". The launcher's parent (the driver)
is already dead, so the killed launcher stays a zombie until `launchd` reaps it. On macOS
the group probe answers "permission denied" for a zombie-only group (measured: zombie →
`PermissionError`, after reap → `ProcessLookupError`). The loop catches only
`ProcessLookupError`, so a poll that lands in the zombie interval raises and the test is
recorded as ERROR although every assertion passed.

Evidence: 4 ERROR in 38 runs at this head (table in section 1), every one
`PermissionError: [Errno 1] Operation not permitted` at `:517`, zero assertion failures.

Why I do not fail the pass on it: the custody property is verified in every run and the
mutations are killed in both modes, which was not true at the second pass. The cost is a
test that reads red about one run in nine on the measurement host. Fix, tried 30 runs
with real `ps` in scratch, 30 OK:

```python
                            try:
                                os.killpg(child_pid, 0)
                            except ProcessLookupError:
                                break
                            except PermissionError:
                                pass  # macOS: only an unreaped zombie is left; keep waiting
                            time.sleep(.02)
```

Fold it into this PR or land it straight after; it needs no product review.

### H2 — MINOR, with a landing condition — old-format and new-format start times never match

`joulewise/measurement_liveness.py:56`, read at `:175-181` and `:226-229`.

A record written by code from before this change holds local-zone text; code from after
it observes UTC text. On any host whose zone is not UTC the two always differ, and the
census reads a difference as "pid reused, owner is stale". Probe
(`/tmp/dd5-fable-a6c/probe_g2.py`): one live `sleep` process, a record naming it:

| record written by | read by | `chain.started` | registry entry | `launch.pending` |
|---|---|---|---|---|
| old code | old code | refuses (live owner) | refuses | refuses |
| old code | new code | CLEAR, "stale reused PID" | CLEAR | CLEAR |
| new code | old code | CLEAR, "stale reused PID" | CLEAR | CLEAR |
| new code | new code | refuses (live owner) | refuses | refuses |

The two mixed rows are wrong in the unsafe direction: a living measurement is reported
gone. They need a process that is alive across the version boundary: a chain or campaign
running while the reading checkout is updated, or a writer in a checkout older than this
commit (for example a hand-run campaign from a stale measurement checkout) with a reader
at or after it. A driver-managed chain stays covered when the driver and the reader are
the same version, because the driver writes `chain.started` itself.

State now: I ran both census versions read-only against `~/night-custody` at 22:27 PDT.
Both answer clear, no open chain, no pending record, 11 registry entries all with dead
owners. So no live owner straddles the boundary at this moment.

Landing condition: merge and update checkouts only while the census is clear, and bring
the measurement checkout to this commit or later before the next launch. If a
no-conditions landing is wanted later, the readers can treat a mismatch as "reused" only
after the unpinned rendering also fails to match.

### H3 — NIT — two provers at the same instant make the second one raise

`scripts/run_night.py:623-631`, `:203-204`. `_resolve_launch_pending` creates the file
exclusively and does not tolerate "already exists". If the driver's courier and the
dead-man both pass the closure check and both find the group gone before either writes,
the loser raises `FileExistsError` out of `dead_man` or `run_courier` (reproduced by
forcing the interleaving). The window is microseconds and needs an unresolved record
whose group vanished just then. Hardening: `except FileExistsError: pass` inside
`_resolve_launch_pending`.

### H4 — NIT — the "pid reused" exit still leaves the record open

`scripts/run_night.py:3991-3992`. When the guard clears a record because the pid is
alive with a different start time, it returns without writing a closure (probe row:
passes, no `launch.resolved`, census clear). The record stays open, so the residue the
second pass described under G3 survives for this one branch; it needs a second number
collision later to matter and fails toward "refuse".

### H5 — NIT — the test's stub bypasses the real probe in the dead-man

`tests/test_launch_window_realization_recheck.py:488-490`. The dead-man's identity is a
stub built from the record, so the real probe-then-compare path in the dead-man is not
run by any test against a real launcher. My faithful variant shows it holds today.

### H6 — NIT — the recorded text carries no zone

`start_time` is now UTC text with no zone marker, next to an `epoch_s` field. A person
reading `chain.started` on this host will see a time seven hours ahead of the local
clock. Nothing computes with it.

## What I ran

- Real checkout: the driver-death test 38 times (two modes), the whole recheck file once
  per mode (20 tests OK each), `tests.test_measurement_liveness` (30 OK),
  `tests.test_run_night -k dead_man` (18 OK).
- Scratch copy (`git archive HEAD` into `/tmp/dd5-fable-a6c/tree`): mutations M1, M2, M3,
  the pre-fix census module against the new tests, the faithful variant, the H1 fix (30
  runs). Each mutated file was restored and compared byte-for-byte afterwards.
- Probes in `/tmp/dd5-fable-a6c/`: `probe_g2.py`, `probe_g3.py`, and one read-only census
  of `~/night-custody` with both module versions.

## What I did not verify

- The rest of `tests/test_run_night.py` and `tests/test_launch_window.py` (not in the
  delta's behaviour; the second pass covers them at the previous head).
- Hosted CI for this head, and whether its runners are macOS (H1 needs macOS's zombie
  answer; I did not check Linux).
- The launchd environments of the driver and dead-man (no longer matters for the start
  time after the pin).
- Which commit the measurement checkout is on (H2's condition).

No file in the checkout was edited (`git status` clean at the end), no writing git
command, no subagent, nothing in the background.
