```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"D1 is reachable; use an atomically locked launch-state transaction, and add a post-t0 dead-man eligibility guard.","workspace":{"base_requested":"f07c85d51b386c9c00fb41cb529c8f113c8fe28e","base_mode":"exact","head_start":"f07c85d51b386c9c00fb41cb529c8f113c8fe28e","head_end":"f07c85d51b386c9c00fb41cb529c8f113c8fe28e","upstream_end":"f07c85d51b386c9c00fb41cb529c8f113c8fe28e","branch":"feat/2026-09-01-night-driver"},"pathspec":[],"unowned_dirty":[],"verdict":{"ruling":"D1 reachable; choose (d), a Darwin O_EXLOCK-serialized transaction on chain.started, over the listed candidates.","findings":[{"id":"F1","severity":"blocker","title":"Dead-man can convert an in-progress launch into launch_failed and courier concurrently with a live chain."},{"id":"F2","severity":"blocker","title":"Same-day dead-man before the plan's post-t0 07:00 occurrence can courier early and preempt the later run."}]},"verification":[{"id":"V1","kind":"inspection","cmd":"git rev-parse HEAD && git rev-parse --abbrev-ref HEAD && git rev-parse '@{upstream}' && git status --porcelain=v1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["f07c85d51b386c9c00fb41cb529c8f113c8fe28e","feat/2026-09-01-night-driver","f07c85d51b386c9c00fb41cb529c8f113c8fe28e"]},"expected":{"exit_code":0,"tail_regex":"f07c85d51b386c9c00fb41cb529c8f113c8fe28e\\nfeat/2026-09-01-night-driver\\nf07c85d51b386c9c00fb41cb529c8f113c8fe28e$"}}],"flags":[{"id":"FL1","kind":"lead_ruling","level":"blocking","text":"NIGHT-DRIVER-01 is not merge-safe until F1 and F2 are cured.","needs":"Adjudicate and implement the launch-state transaction plus dead-man eligibility guard."},{"id":"FL2","kind":"verification_gap","level":"nonblocking","text":"No tests were run because the seat was ordered to write nothing anywhere.","needs":""}]}
```

# RULING

## Q1 — D1 reachability

| Schedule | Verdict | Controlling evidence |
|---|---|---|
| Run and dead-man both scheduled at 07:00, `t0=07:00` | **REACHABLE.** Either job may run first; no dependency exists between the independently rendered jobs (`install_night_agent.sh:124-125`). `_next_deadman_epoch` chooses tomorrow because dead-man time is `<= t0` (`run_night.py:858-868`), so the overrun check does not prevent launch (`:1038-1062`). |
| Run normally starts before 07:00 and completes `Popen` promptly | **NOT REACHABLE under that schedule.** The marker is completed at `:432` before the later dead-man invocation. |
| Earlier run is descheduled or `Popen` remains incomplete until 07:00 | **REACHABLE.** Nothing bounds or serializes the interval from O_EXCL creation (`:349-355`) through `Popen` (`:410-418`) to completion (`:432`). The overrun predicate constrains planned epochs, not actual launch progress. |
| `t0>07:00`, ordinary awake machine | **NOT concurrently reachable, but defective.** Same-day dead-man runs first; Q4 applies. The next-day selection at `:858-868` permits the plan rather than preventing it. |
| Sleep misses both jobs; `t0<07:00`; wake is after 07:00 and run had not begun | **NOT REACHABLE.** launchd coalesces missed calendar firings on wake (`/usr/share/man/man5/launchd.plist.5:456-459`), but either the overrun check refuses (`run_night.py:1038-1062`) or the missed-window gate refuses before the claim (`night_gate.py:546-566`, `run_night.py:1064-1105`). |
| Sleep misses both jobs; `t0>=07:00`; wake remains inside the plan window | **REACHABLE.** The missed events may be coalesced, the gate admits the delayed run, and `_next_deadman_epoch` points to the following day; either process can enter the critical interval first. |
| Manual `run` at 07:00 with `t0=07:00`, alongside scheduled dead-man | **REACHABLE.** Manual invocation has no mutual exclusion with dead-man. For `t0<07:00`, overrun/window admission prevents the claim; for `t0>07:00`, the window has not opened (`night_gate.py:556-566`). |
| Manual dead-man concurrent with any admitted run | **REACHABLE.** `dead_man()` contains no temporal eligibility check before reading the markers (`run_night.py:1253-1281`). |

## Q2 — ranked cure

| Rank | Choice | D1 | F3 | New durable/schema state | Test cost |
|---|---|---|---|---|---|
| 1 | **(d) Atomically locked single-marker transaction** | Fully closes | Preserves cure | None; transient lock semantics only | Medium |
| 2 | **(a) `chain.claim` plus atomic `chain.started`** | Only if dead-man also consumes/serializes `chain.claim` | Preserves | New driver artifact, though neither courier prompt nor night-gate receipt schema needs it | Medium-high |
| 3 | **(c) Refuse on empty marker** | Prevents unsafe courier | Reopens F3 under overlap: dead-man and run can collide writing `refusal.json`, while failure reporting may be lost (`run_night.py:1185-1193`) | None | Apparently low, actually medium |
| 4 | **(b) mtime grace** | Does not fully close: no finite grace proves `Popen` has finished | Usually preserves | New timing state | Medium and timing-sensitive |

Chosen mechanism: create `chain.started` with Darwin’s atomic `O_EXLOCK` alongside O_EXCL; hold the lock through launch publication. Dead-man must acquire the same lock before checking `chain.exited` or parsing the marker. Success publishes the complete positive-pgid document before unlock; failure publishes the complete null-pgid document and all terminal records before unlock. An empty document observed only after acquiring an abandoned lock then unambiguously means launcher death, not launch-in-progress.

Rejected reasons: (a) merely moves the ambiguity unless `chain.claim` participates in the protocol; (b) substitutes a guess for synchronization; (c) is safe for a successful launch but makes concurrent Popen failure non-idempotent.

## Q3 — R-7 preservation

| Property | Finding |
|---|---|
| Exactly one courier | **YES in R-7’s ownership sense:** `courier.lock` is O_EXCL (`run_night.py:679-690`) and held through the attempt sequence (`:708-785`); `courier.sent` makes later dead-man runs skip (`:1261-1265`). This is not literally one process: R-7 intentionally permits retries (`:720-776`). |
| Dead-man never couriers while chain alive | **YES**, once marker inspection is lock-serialized; a positive live pgid refuses before courier (`:1295-1312`). |
| Never `killpg` a null pgid | **YES.** Invalid/null pgid returns `None` (`:1242-1250`); only the positive-pgid branch calls `killpg` (`:1294-1297`). |
| Durable record before courier | **YES.** Run path publishes at `:914` before `:916`; dead-man publishes at `:1329` before `:1338`. |

## Q4 — pre-t0 dead-man

**F2 is a defect under R-7.** With no `chain.started`, the condition at `run_night.py:1281` is false. Dead-man performs the census (`:1316-1318`), may write a refusal (`:1319-1327`), durably records (`:1329`), and starts the courier (`:1330-1338`). It then creates `courier.json` (`:1339-1340`), which the later run treats as an existing write-once record and refuses (`:60-67`, `:1009-1012`).

Correct behavior is to stand down without courier or write-once records until `now >= _next_deadman_epoch(plan.t0_epoch_s)`. Checking only `now < t0` is insufficient when `t0=07:00`; the eligible dead-man is the following civil day.

## Findings

- **F1 — blocker:** Partial `chain.started` publication is observable as a false launch failure.
- **F2 — blocker:** Dead-man lacks a post-t0 occurrence guard and can consume the night before launch.

## Dissent

R-7 should specify the dead-man’s eligible civil occurrence, not merely “07:00.” I would also phrase courier semantics as “one active courier owner, bounded retries, stop after `courier.sent`”; external email followed by a local marker cannot provide literal exactly-once delivery (`NIGHT_COURIER_PROMPT.md:14-17`).

## Residual risk

The lock design is safety-first: a permanently stuck `Popen` can delay dead-man reporting rather than permit an unsafe courier. Deterministic Darwin tests should cover success, OSError, launcher death, coalesced wake, and `t0=07:00`; none were run in this read-only seat.