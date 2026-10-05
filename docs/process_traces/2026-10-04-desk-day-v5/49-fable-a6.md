FINAL PASS: FAIL

Cold final pass on `14324c52` (PR #475, queue row A6 V5-LAUNCH-REALIZATION-RECHECK-01).
Reviewer: Fable 5.1, no prior context. Scope: `scripts/`, `joulewise/`, `tests/` in
`git diff cfdb90d6..14324c52`.

The ruled property itself is met (drift refuses before any bundle, with no
`chain.started`). The FAIL is for two verified defects in the custody machinery
added around it: F1 lets old records block later harvests, F2 lets a collection run
with no claimed start. Both fail toward "refuse", not toward a wrong number, and both
have small fixes.

## Answers to the five questions

1. **Ruled property: MET.** `scripts/launch_window.py:327` runs the recheck directly
   after `verify_consumed_launch` (`:319`) and before `execve` (`:343`). On a mismatch
   the launcher prints `readiness_identity_environment_dirty` and exits 2; the driver
   never calls `_claim_chain_start`. A clean launch claims exactly once
   (`scripts/run_night.py:1039-1043`), through the same `_claim_chain_start` /
   `_complete_chain_start` as main, so the record has main's four fields
   (`pid`, `pgid`, `epoch_s`, `start_time`).
2. **Collection without a claimed start: YES, in one configuration (F2). Claim without
   a recheck PASS: no. Stale record blocking later work: YES (F1).** No deadlock found:
   every wait on the launcher side ends on driver death (end-of-file on the socket),
   and every wait on the driver side is covered by the window deadline thread.
3. **Non-pack paths: behaviourally identical to main.** For DIAGNOSTIC_NO_PACK and
   REHEARSAL_STUB the driver still claims before launch (`run_night.py:3720`), no socket
   is created, `Popen` gets no extra arguments, and every new branch is gated on
   `claim_descriptor is None` or on `launch.pending` existing. The only new work is two
   `stat` calls on an absent `launch.pending`; `_artifact_entry` returns `None` for it
   (`:1159-1164`), so `result.json` is unchanged.
4. **Same derivation: YES.** `_recheck_identity_projection`
   (`launch_window.py:265-289`) calls the existing `identity_pins` helpers with the same
   four-clause comparison as `joulewise/arm_readiness_evidence_t0.py:1773-1786`, the
   site the ruling names. No new derivation code.
5. **Tests: they kill the claimed regressions, with two gaps** (see F1 and F2): one test
   pins F1 as desired behaviour, and nothing covers a launcher that never speaks.

## Findings

### F1 — BLOCKER — a finished window's `launch.pending` can refuse every later harvest

`joulewise/measurement_liveness.py:190-209`, `:232-238`; pinned by
`tests/test_measurement_liveness.py:125` and `:74`; same rule in
`scripts/run_night.py:3879-3901` (used at `:1641`, `:1666`, `:3941`), pinned by
`tests/test_run_night.py:2255`.

What happens. Every pack window now leaves a write-once `launch.pending` holding the
launcher's process-group id (pgid). Nothing ever closes it: not `chain.exited`, not
`result.json`, not `courier.sent`. The measurement-owner census decides "is this
launcher still alive?" with a bare `os.killpg(pgid, 0)`, which only asks "does any
process group with this number exist right now". The operating system reuses process
ids, so months-old numbers come to name unrelated programs. When that happens the
census refuses, even though it has just observed that the leader's start time differs
(it logs `stale reused PID` and then refuses anyway). If the unrelated group belongs to
another user, `killpg` raises `PermissionError`, and the census reports
`census indeterminate` and stops scanning.

Who is blocked. `scripts/harvest_window.py:323` and `:544` run the census over the
whole custody parent, so one old record in any sibling window refuses the harvest of
the current window ("measurement ownership is not clear"). `scripts/window_status.sh:44`
refuses to publish status the same way. I did not find the census on the arm or install
path, so arming itself is not blocked; I did not verify whether the next window's
install depends on the previous harvest's uninstall step.

Evidence (real `killpg`, real `ps`, scratch directory;
`/tmp/dd5-fable-a6/stale_pending_demo.py`). A window directory with `launch.pending`,
`chain.started`, a valid `chain.exited` and `courier.sent`, whose recorded pgid is:

| recorded pgid now names | census result | same directory without `launch.pending` |
|---|---|---|
| an unrelated group of the same user | `clear=False`, "live measurement owner process group", plus warning "stale reused PID" | `clear=True` |
| an unrelated root-owned group | `clear=False`, "census indeterminate: [Errno 1] Operation not permitted" | `clear=True` |

How often. Measured on this host during the review: 678 live process groups (283 not
owned by the user), process ids drawn from about 99,900 values, and the id counter
wrapped at least 8 times in the last 72 hours. So once the counter has wrapped, each
old record has about 678 / 99,900 = 0.68% chance of naming a live group at any instant.
With N records under one custody parent the chance that at least one collides is
1 − (1 − 0.0068)^N: 15% at N = 24, 29% at N = 50, 49% at N = 100. A collision lasts as
long as the unrelated process lives, which for a system daemon is days. These rates are
from one loaded host and are an estimate, not a bound.

Why it blocks merge. There is no sanctioned release: the record is immutable custody
evidence, so the only cures are deleting it, killing an unrelated process, or
rebooting. Main does not have this problem, because a closed chain is skipped and an
open one is cleared by the start-time token.

Fix direction. The driver already proves the group absent on every path where it
survives (`_terminate_process_group`). Have it write a resolution the readers honour
(a new write-once marker, or `chain.exited` when one exists), and fall back to the bare
group probe only for an unresolved record, which means the driver died. Replace the
test at `test_measurement_liveness.py:125` with one that requires a resolved record
plus a reused pgid to be clear. Because the fix is on the reader side, records already
written stay valid.

Related, MINOR: `_write_launch_pending` (`run_night.py:603-609`) fsyncs the directory
but not the file, while `launch_window.py:296` says the driver "has fsynced the separate
launcher identity". After a power loss the name can survive with no bytes; both readers
then refuse permanently ("cannot be read" / "census indeterminate"), the same blocking
class as above.

### F2 — MAJOR — a launcher that does not speak the barrier collects with no `chain.started`

`scripts/run_night.py:1021-1057`, `:1133-1154`, `:2276-2278`, `:904-905`;
`joulewise/night_gate.py:1319`.

What happens. The driver reads the barrier's environment-variable name from its own
checkout (`:904`) but starts the launcher from the plan's measurement checkout
(`:2277-2278`). The plan pins the two checkouts with separate fields (`repo_head`,
`measurement_head`); the gate checks each against its own checkout and nothing requires
the measurement checkout to contain this change. A launcher from before this change
ignores the variable and `execve`s the chain immediately. The driver has not claimed,
never receives a byte, and keeps waiting while the collection runs. When the chain
exits, the driver records REFUSED with "launcher exited before passing its launch
recheck". No recheck ran, and neither `chain.started` nor `chain.exited` exists for a
window that collected to completion.

Evidence (`/tmp/dd5-fable-a6/skew_probe.py`: real `_run_chain_once`, pack mode, command
is a stand-in that ignores the barrier and writes a marker file):

```
refusal: night_chain_launch_failed / "launcher exited before passing its launch recheck"
termination_proven: True
collection ran: True
chain.started exists: False      chain.exited exists: False
```

Consequence. A harvest reads this window as never started while bundles exist under the
runs root, and the one-use arm is spent. On main the same pairing was safe, because the
driver claimed first. I did not check how the staging procedure chooses
`measurement_head`; if it always equals the driver's head the case cannot arise, but no
code enforces that.

Fix direction. Fail closed in the driver: refuse before `Popen` unless the measurement
checkout's launcher carries the barrier, or bound the wait for the first byte and, on
timeout, terminate the group and record the start conservatively. Add the probe above
as a test.

### F3 — MINOR — report delivery now waits for the whole process group

`run_night.py:1641`, `:1666`, `:3941`. After a normal chain exit main delivered the
report as soon as the leader was reaped. Now the courier (the step that sends the
night's report) and the dead-man (the scheduled fallback that sends it if the driver
did not) both refuse while any member of the launcher's group is alive, even with
`chain.exited` present. I found no background jobs in `scripts/night_chains/*.zsh`, so I
expect no effect today; a chain that ever leaves a child behind would turn a delivered
report into `courier.sent` missing, which harvest requires. Folding this into the F1
resolution marker would remove it.

### F4 — NIT — a malformed barrier variable escapes the refusal handler

`launch_window.py:293-295`. `int(start_fd)` raises `ValueError`, which `main()` does not
catch, so the launcher exits with a traceback instead of a REFUSE document. The driver
still refuses with the generic detail; nothing starts.

### F5 — NIT — the driver's reason code is its own, not the ruled one

A recheck refusal reaches `refusal.json` as `night_chain_launch_failed` with
`readiness_identity_environment_dirty` in the detail and in
`evidence.launcher_refusal`. The launcher emits the ruled code verbatim, which is what
the ruling asks; noted so a reader grepping `result.json` for the ruled code knows where
it is.

## What I ran

- `tests/test_launch_window_realization_recheck.py`: 17 passed (45 s).
- `tests/test_measurement_liveness.py`: 27 passed, 36 subtests.
- `tests/test_run_night.py -k "pending or launcher_recheck or write_once or go_receipt_is_published"`: 9 passed.
- `tests/test_launch_window.py -k "PackNightLaunchBoundary or LaunchWindowEntrypoint"`: 18 passed.
- Two scratch probes named above, both against the checkout's real code.

## What I did not verify

- The other 20 tests in `tests/test_launch_window.py` and the other 254 in
  `tests/test_run_night.py`. My first combined run did not finish in 10 minutes
  (host load about 26) and I did not identify which test was slow.
- Protocol deviation: that run was moved to the background by the harness when it hit
  the 10-minute limit. I stopped it at once, confirmed no process remained, and ran
  everything afterwards in the foreground under a hard kill timer.
- The cost of the recheck on a real pack (it hashes model files and runs the runtime
  probe in the launcher just before the chain starts). No real pack was touched.
- Whether window staging always sets `measurement_head` equal to the driver's head (F2),
  and whether the next install depends on the previous harvest (F1).

No file in the checkout was edited and no git command that writes was run. Scratch is
under `/tmp/dd5-fable-a6/`.
