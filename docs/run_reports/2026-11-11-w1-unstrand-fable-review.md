# Fable cold review: `w1-unstrand` (RL-53 W-3; audit Q6)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 03:50 PST. Reviewed head `0fd8ae91c`
(`ops/2026-11-11-w1-unstrand`, base the W1 line `b4a6c217f`). Builder: Sol xhigh.

**Verdict: ADMIT-WITH-FIXES.** U-1 blocks: the new restore path can strand itself. Round 2 goes back to Sol.

## What I did

- Read the whole diff of `scripts/post_window_unstrand.sh` (+161/-10) against RL-53 W-3, line by line.
- Ran `tests.test_post_window_unstrand` on the Air on the branch (50 tests) and on the base (24 tests). Both
  have the same four failures, by name: three native `ps` tests and one follower timing test. They refuse with
  "a chain, driver or window process is still present" on this machine, on the base as well, so they are this
  host's process table and not this change. The 26 new tests pass.
- Ran `tests.align.test_v4_executed_closure` and `tests.align.test_v4_dynamic_closure`: 14 tests, OK.
- Confirmed only the bound file named in the brief and its test module changed.

## Against the ruling

| RL-53 W-3 condition | Met? | Where |
|---|---|---|
| Result for this plan with verdict REFUSED | Yes | `plan_id` equality, `verdict == "REFUSED"`, null `chain_exit_code` |
| Delivered | Yes | `courier.sent` exists and (`courier.json` `sent` is true, or a git-push receipt naming this plan, its ref and the result's SHA-256). Same evidence as the next-arm packet's terminal release check. |
| No `chain.started` | Yes | The new path is chosen only when neither chain marker exists; with `chain.started` present the old requirements apply unchanged |
| No night process alive; existing live-chain refusal stays | Yes | The existing process and installed-plan checks run for both paths, unedited |
| Host restore is a separate flag, off by default | Yes | `--restore-host`, refused without `--go`; otherwise the command is printed and nothing is restored |
| Through `powermode.restore_owed`, host lock, defers to a measuring night; no bare `pmset` | Yes | `HostLock.acquire`, `restore_owed(..., lock=lock)`; network time through `run_night._restore_network_time` only when this night turned it off |
| Records what it found and what it restored | Yes | `night/unstrand.restore.json` |

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| U-1 | **Blocking** | The restore record is opened write-once before anything else, and an existing record refuses every later attempt. A restore that was deferred to a measuring night, or failed, leaves a record. From then on the tool says "record already exists; no host restore attempted", and the host stays unrestored with no tool that will restore it. This is the stuck state the lane exists to remove. | One write-once record per attempt (`night/unstrand.restore.<n>.json`, n from 1). A new attempt is refused only when an earlier record has `ok: true`. Test: deferred, then retried and restored; failed, then retried; succeeded, then refused. |
| U-2 | Medium | After a first `--go`, the jobs are gone. The retry in U-1 needs `--go --restore-host` to pass the uninstall step a second time. Not tested. | Test the second run end to end with the jobs already absent. If the uninstall route refuses "nothing installed", treat already-absent as success for this plan only, with the absence verified by the existing probe. |
| U-3 | Low | `ok` requires `network.get("ok") is True`. The driver's own terminal restore also accepts `verified is True` (`scripts/run_night.py:4593-4594`). | Use the same rule as the driver. |
| U-4 | Low | When a W1 marker belongs to another session the action is `not_owner` and the tool exits 1 with "host restore failed". That reads as a fault; it is a correct refusal. | Distinct message: another armed session owns the host state; nothing was changed. |

## Native checks owed after install (remote, never physical)

1. On a synthetic refused plan in a scratch custody root: inspect, `--go`, then `--go --restore-host`; confirm
   the record and that `pmset -g custom` and network time read as before the arm.
2. With a night lock held by a second process: confirm `deferred`, exit nonzero, and a successful retry after
   the lock is released.

## Round 2 delta review (2026-11-11 04:13 PST)

Reviewed `556ce3e5e` (Sol's round 2, pushed as the side branch `ops/2026-11-11-w1-unstrand-r2` and merged here
into `ops/2026-11-11-w1-unstrand`).

**Verdict: ADMIT.**

| Finding | Disposition |
|---|---|
| U-1 | Fixed. One write-once record per attempt, `night/unstrand.restore.<n>.json`, n from 1 to 20. A new attempt is refused only when an earlier record has `ok: true`; an unreadable earlier record is warned about and does not count as success. Each record carries `attempt` and the earlier attempts' action words. |
| U-2 | Fixed. A second `--go --restore-host` with the jobs already absent reaches the restore; tested end to end with the fakes. |
| U-3 | Fixed. `ok` accepts `verified is True` as the driver's terminal restore does (`scripts/run_night.py:4593-4594`). |
| U-4 | Fixed. `not_owner` is recorded as `refused: other_session_owns_host_state` with its own message, and network time is not touched in that case. |

Checks on the merged head:

- `tests.test_post_window_unstrand`: 57 tests; the same four host-process failures as on the base, and no other.
- Eight mutants of the new path, each killed (five or more failures against the baseline four): an earlier
  successful restore no longer refuses; any verdict accepted; `courier.sent` not required; unproven delivery
  accepted; the host lock not honoured; `chain.started` without `chain.exited` routed to the new path; another
  plan's result accepted; a non-null chain exit code accepted.
- Only `scripts/post_window_unstrand.sh` and its test module differ from the W1 line, plus reports.

The two native checks listed above remain owed after install, both remote.
