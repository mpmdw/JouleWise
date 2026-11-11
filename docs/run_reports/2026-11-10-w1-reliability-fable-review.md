# Cold review (Fable 5.2): W1 reliability and watchdog branches

Written 2026-11-10 18:51 PST. Review only; nothing pushed, merged or installed. This file is uncommitted.

| Branch | Head | Base | Verdict |
|---|---|---|---|
| `ops/2026-11-10-w1-reliability` | `297629a0d` | `origin/align/2026-11-08-v4-r11` (`9abe6095f`) | **ADMIT-WITH-FIXES** (F-01 and F-02 before any arm) |
| `ops/2026-11-10-watchdog-unknown-keys` | `4d46d9c3e` | `origin/ops/2026-11-10-watchdog-v5-installed` (`df5311456`) | **ADMIT-WITH-FIXES** (safe to install after R1; W-01 and W-02 stay open as alarms) |

Source audit: `origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/measurement-system.md`.
Context read: RUN_STATE item 251 on `origin/main`; the three Sol run reports on branch 1.

## 1. What I ran

All synthetic, one module at a time, Python 3.13, no MLX, no full suite, no host command. About 40 s of test time.

| Where | Command | Result |
|---|---|---|
| branch 1 | `python3.13 -B -m unittest tests.test_w1_reliability` | 11 passed |
| branch 1 | `... tests.test_w1_reliability_r2` | 18 passed |
| branch 1 | `... tests.test_w1_reliability_r3` | 14 passed |
| branch 1 | `... tests.align.test_v4_executed_closure` | 4 passed |
| branch 1 | `... tests.align.test_w1_smoke` | 28 passed |
| branch 2 (temp worktree, removed) | `... tests.test_watchdog_reliability` | 9 passed |
| branch 2 | `... tests.test_magistrate_watchdog_v5` | 4 passed |
| branch 2 | `... tests.test_magistrate_watchdog` | 155 passed |

Three review probes, kept in the session scratchpad and not added to the tree. Each reuses the branch's own test
harness with a synthetic host:

1. **Real frequency preflight on a plan from the real plan writer** (`tests.align.test_v4_series.FakeWorld`, W1).
   Kernel word 0, t0 in the future. Result: `ok: false`, cause `clock.frequency_word_nonzero`, reason
   `KeyError: 'thresholds'`. This is F-01.
2. **Hazard night whose chain termination is not proven**, with an R1-tagged marker and mode 2. Result: Automatic
   restored, network time ON, `host_restoration.ok: true`, no deferral. This is F-04.
3. **Dead-man after a completed, delivered night** (`host_restoration.ok: true`, `courier.sent` present). Result:
   `result.json` sha256 changed, `courier.sent` removed, courier re-run; with a failing re-delivery `courier.sent`
   stays gone on every later fire. This is F-02.

I also loaded a W1-line plan (synthetic, from probe 1) with the watchdog branch's `NightPlan.from_mapping`: it is
accepted. The two lines' `joulewise/night_gate.py` differ by 18 diff lines (reason codes and comments only). An
added unknown key still refuses, as intended.

## 2. Do the fixes close the audit findings?

| Finding | Closed? | Basis |
|---|---|---|
| A-01 | **Yes** | `chain_outcome`, `measurement_outcome`, `fault`, `fault_reasons` in `result.json`, `hazard_result.json` and the courier facts. A non-zero chain exit and an R1 status other than `complete` (absent, unreadable, running, refused) fault even under verdict `GO`. Verdict and exit-code policy unchanged. |
| A-02 | **Mostly** | `courier.sent` now means a `git push` of the snapshot to `night-results/<plan>` was acknowledged, bound to the `result.json` digest; a failure writes `courier.filed` and returns non-zero. Pre-chain refusals publish at once. Gaps: F-07 (one unreadable artifact blocks every delivery), F-08 (an escaped exception writes a result but does not publish it), F-09 (a failed run-path delivery blocks the series). Push under launchd is unproven (native check 8). |
| I-01 | **Gate yes, recovery no** | Pre-chain probe refuses an absent reader; in-window liveness stops the chain after 600 s without a valid sample batch. "Never measure without the meter" now holds. The monitor still never re-initialises after a USB error, so a short re-enumeration becomes a certain window stop (F-06). |
| A-04 | **Yes, with F-02/F-03/F-04** | Every plan closes through one restore, including mode-0 R1 chains; the dead-man restores R1- and W1-tagged markers and no longer skips on `courier.sent`. |
| A-05 | **Yes, with F-05/F-11** | Network time ON with an authenticated read-back on every terminal path, recorded in the result. |
| Frequency word (item 251) | **No, as written** | The design is right (project the word through the plan's own clock budget; OFF, zero, read back; named refusal). The code reads the wrong key and refuses every real plan (F-01). |
| Host-state preflight (A-09 part) | **Yes** | `host_lock_preflight` creates, locks and releases the production path in `prepare` and in the smoke guards. The other A-09 items (watchdog parser on the rendered plan, pmset round trip) are not in the branch; see native checks 2 and 4. |
| W-01 | **No (improved)** | Holds are named and a notice is queued at once, with a `STRANDED` state after 900 s. The hold is still indefinite and the notice never leaves the MBP (W-A). Unknown keys still hold, by design. |
| W-02 | **No (improved)** | The heartbeat is read and a stale notice queued; `state.json` records it. Nothing is exported, so watchdog or magistrate silence is still invisible from the Air (W-A). |

New silent-failure paths: none found. Every new failure I found is fail-closed and recorded. The costs are lost or
blocked windows (F-01, F-05, F-06, F-09) and a changed terminal record (F-02).

## 3. Findings

Severity: BLOCKER = fix before the branch is used to arm; HIGH = can cost a window or change a custody record;
MED = fix before W1 arms unless the lead rules otherwise; LOW = hygiene. Paths are at the branch heads.

### Branch 1: `ops/2026-11-10-w1-reliability`

| ID | Sev | Path:line | Finding | Fix |
|---|---|---|---|---|
| F-01 | BLOCKER | `scripts/align_v4_session.py:156` | `limits = night_plan['thresholds']['clock']`. A night plan has no top-level `thresholds`; they are at `hazard_window.thresholds`, and `night_gate` demands the exact key set. Every real `prepare` raises `clock.frequency_word_nonzero: KeyError: 'thresholds'` and every `install` refuses. Fail-closed, but W1 cannot arm, and the named cause is wrong. Proven by probe 1. | Read `night_plan['hazard_window']['thresholds']['clock']` and set `t_stream_max_s` from `hazard_window['T_stream_max_s']`, as `driver._arm_thresholds` does (`joulewise/b5/driver.py:586`). Report a missing key under its own cause, not as a nonzero word. |
| F-01t | BLOCKER (test) | `tests/test_w1_reliability_r3.py:64`; `tests/align/test_v4_series.py:486`; `tests/align/test_v4_series_e2e.py:105`; `tests/align/test_v4_kit.py:40` | The only tests of the real preflight use a hand-built `{'thresholds': ...}` dict. Every test that builds a real plan patches the preflight out. | In `ProductionPathTests`, inject `frequency_reader`/`frequency_runner` instead of replacing the function, so the real preflight reads a plan from the real writer. |
| F-02 | HIGH | `scripts/run_night.py:5334-5348` (and the removed skip in `_dead_man`) | On every fire past completion the dead-man rewrites `result.json` (adds `dead_man_host_restoration`), deletes `courier.sent` and re-runs the courier. This includes a night that completed, restored and delivered. The dead-man is a daily job, so it repeats until the plists are uninstalled. `result.json` is a create-once record whose sha256 is the watchdog's release key (`scripts/magistrate_watchdog.py:893-899`) and the next-arm latch (`scripts/align_v4_next_arm_packet.py:181-190`); `courier.sent` is terminal evidence for the offload (`scripts/offload_window.py:717`) and the harvest. A failed re-delivery leaves a delivered window without `courier.sent`. Proven by probe 3. | Never rewrite `result.json` and never unlink `courier.sent`. Keep the create-once `deadman_host_restoration-*.json` and add it to `_artifact_list` so it is published. Make the dead-man a no-op for restore when `result.json` shows `host_restoration.ok` true and no power marker exists. |
| F-03 | MED | `scripts/run_night.py:5326-5332` | The dead-man now writes `night/deadman_host_restoration-<ns>.json` on a stand-down before the completion epoch (including before t0) and has no `launch_abandoned.json` guard, unlike `_close_night_host` (`:4517`). The watchdog's launch-liveness release needs `night/` empty (`_night_records(...) == []`), so a never-launched night stays fenced for its whole span. Two tests that pinned "stand-down leaves `night/` untouched" were relaxed (`tests/test_run_night.py`, `test_dead_man_stands_down_immediately_after_t0_on_empty_night`, `..._one_second_before_completion_epoch`). | On a stand-down write to the custody log only, as before. Honour `LAUNCH_ABANDONED_MARKER`. Restore the two assertions. |
| F-04 | MED | `joulewise/b5/driver.py:2718-2730, 2932`; `scripts/run_night.py:4444` | The close defers on `_CHAIN_TERMINATION_UNPROVEN`, which only the non-hazard path sets. R1 and W1 are HAZARD_PACK. With `proven == False` the close still restores Automatic, turns network time ON, removes the marker and records `ok: true`. Only the lock retake protects, and a mode-0 night holds no lock. Proven by probe 2. The docstring claims the opposite. | Before `rt._write_result`, when the chain started and is not proven gone, set the unproven record through a small runtime setter. Add a hazard-driver test that returns `proven=False` (the existing test sets the global by hand). |
| F-05 | MED | `scripts/align_v4_session.py:157-161` | A passing word is a no-op that never checks network time. With network time ON (which A-05 now leaves) and a word still near zero, the preflight passes, timed changes the word later, and the t0 arm refuses: the item-251 loss. Likely trigger: a back-to-back re-arm minutes after a close. | On the passing path also require an authenticated OFF read-back; if ON, turn OFF and re-read. The t0 arm turns it OFF anyway, so no measurement semantics change. |
| F-06 | MED | `scripts/km003c_monitor.py:186-189` (unchanged); `joulewise/b5/driver.py:2557, 2652-2661` | The liveness gate was added without the monitor recovery the audit paired with it. After a `UsbError` the monitor loops on the dead handle and never exits, and it is started with `restart_on_clean_exit=False`. Any KM003C re-enumeration now ends the window at 600 s. Also, the chain launches without waiting for a first valid batch, so a meter that goes absent between the probe and the start costs 10 minutes of chain before the stop. | Exit non-zero after N consecutive USB errors so the supervisor restarts into a new `stream-NNN` (the liveness reader already handles restarts). Wait for a first valid batch before the chain, inside the existing monitor-readiness budget. `km003c_monitor.py` is STRICT-bound: needs a lead ruling under I-01. Native check 7 decides the urgency. |
| F-07 | MED | `scripts/run_night.py:1672-1673` | `_publish_terminal_result` raises on any artifact with an `error`. The old publisher omitted and named it. One unreadable file (the 11-08 root-owned class) now blocks every delivery attempt, including the dead-man's. | Omit and name unreadable artifacts in the snapshot and in the diagnostic. Fail only if `result.json` itself cannot be read. |
| F-08 | MED | `scripts/run_night.py:4672-4682` | An exception that escapes `_run_night` gets a terminal result and a host restore, but no publish. The Air sees nothing until the dead-man, up to window length plus an hour later. | Call `_durable_record` (already bounded at 50 s for `align-` plans) after that `_write_result`. |
| F-09 | MED | `scripts/run_night.py:5517`; `scripts/align_v4_next_arm_packet.py:171` | `courier.json` is create-once. If all four run-path deliveries fail (network down at close), it stays `sent: false` even after the dead-man delivers, and `terminal_release_check` then refuses the next series arm with "courier delivery missing". The program courier could not fail before this branch. | Let the release check accept a `courier.delivery.json` receipt bound to the result digest, or append a delivery addendum on a later success. Lead ruling: the check is in bound code. |
| F-10 | LOW | `scripts/align_v4_session.py:110`; `scripts/zero_ntp_frequency.c` | The root helper's source is not in `v4_registration.ARTIFACTS`, and the preflight runs the installed binary without recording its digest. | Record the binary's sha256 in the preflight record. Bind the C source in the registration (registration code edit: lead ruling). |
| F-11 | LOW | `scripts/run_night.py:4356-4364, 4475, 4506` | Network time ON is unconditional, including rerun and launch-abandoned exits that measured nothing; the audit asked for it only when this night turned it OFF. A mode-0 night holds no host lock, so the lock does not guard this. Separately, the close latches signal handling from result-write time, so TERM is ignored through a courier phase that can now last about 34 minutes. | Restore ON only when this night's `network_time_off` action shows it turned it OFF, or when the dead-man proves no night is installed. |
| F-12 | LOW | `scripts/run_night.py:1691, 1711-1713` | A delivery failure records only the exception class, so an auth failure and a network failure look the same. `courier.filed` survives a later success. `_wait_for_courier` waits the full 300 s after the program courier has already exited 1. | Keep a bounded stderr tail (git output is not outcome-bearing). Remove `courier.filed` on success. Return early when the courier process has exited non-zero. |
| F-13 | LOW | `joulewise/b5/driver.py:1310-1345, 2321` | `MeterLiveness` parses the full 10 s backlog (every sample payload) inside the night driver during measurement: a few ms every 10 s. A sleep makes `seen > now`, so no batch refreshes liveness afterwards. The pre-chain probe imports `scripts.align_v4_session` into the hazard driver and spawns an unobserved 3 s child at t0. | Validate only the last complete `b` line per check. Note the new import and child in the dynamic closure trace. |

### Branch 2: `ops/2026-11-10-watchdog-unknown-keys`

| ID | Sev | Path:line | Finding | Fix |
|---|---|---|---|---|
| W-A | HIGH (closure) | `scripts/magistrate_watchdog.py:2274-2286, 2402` | `_queue_safety_notice` writes only `state.json` and `events.jsonl`. The one delivery route is the next magistrate's prompt, which the hold prevents. `STRANDED` renames the state and adds a second local notice. The branch's own report and doc say this. W-01 ("no alarm") and W-02 ("no liveness leaves the MBP") are not closed. | Export a small status record (state word, transition time, heartbeat age; none outcome-bearing) on transitions and on a slow keepalive, by the same route A-02 uses (a ref the Air watcher polls), and alarm on the Air on staleness or any `HOLD_*`/`STRANDED`. Until then keep W-01/W-02 open and rely on native check 2 before each arm. |
| W-B | LOW | `scripts/magistrate_watchdog.py:2267` | `"lock" in reason` also matches "clock" and "blocked", and it is tested before the `desk_fence:` prefix. A desk-fence or launch-fence error mentioning the clock is labelled `HOLD_LOCK`. Label only; every branch fails closed. | Match anchored prefixes (`corrupt_lock_`, `dead_lock_`, `magistrate.lock`) and move the `desk_fence:` test up. |
| W-C | LOW | `scripts/magistrate_watchdog.py:2289-2336`; `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:2` | Liveness depends on the model rewriting a file every minute with the lock PID. A long tool call gives a false stale notice, and the prompt tells the next magistrate that every notice is something Ed must hear. The changed expectation in `tests/test_magistrate_watchdog.py` (`["magistrate_heartbeat_stale", "forced_standdown"]`) shows it firing in an ordinary stand-down. Notice only, no kill. | Use growth of the supervisor's own `attempt-N.stream.jsonl` as the progress signal, with the model-written heartbeat as a second input. |
| W-D | LOW | `scripts/magistrate_watchdog.py:149` | `--model claude-fable-5-2` is a fixed flag against an auto-updating CLI. A rejected value is a silent no-magistrate state (audit W-08). | Native check 1. |
| W-E | INFO | whole file | `scripts/magistrate_watchdog.py` is a STRICT-bound path on the W1 line, but this branch is based on PR #707's line. The two copies differ by about 360 lines. Registration at the W1 head binds bytes that are not the installed watchdog (audit A-03). | Port PR #707 plus this branch onto the W1 line before re-registration, or record in the registration notes that the bound watchdog is not the installed one. |

## 4. Fail-safe direction

- **Never launch over a possibly armed plan: preserved.** `STRANDED` and every named hold keep `launch=False`
  and drain a resident session. No unknown key is ignored. The test proves two days of ticks with no fork, and
  that repairing the plan does not bypass an open chain fence.
- **Never measure without the meter: now enforced** (pre-chain refusal, 600 s in-window stop). F-06 is about
  yield, not direction.
- **Never restore under a possibly measuring chain: one gap**, F-04.
- **Dead-man early or with a live chain: preserved.** It defers and takes no result slot. F-03 is about where it
  writes.

## 5. Measurement semantics and STRICT-bound files

No change to analysis or engine code, thresholds, seeds, registration text or registration code. The frequency
preflight adds no threshold: it projects through the plan's existing clock budget. The behaviour changes are the
ones the lead ruled on (meter refusal and stop; restore on every terminal path; network time ON at close;
host-lock preflight; frequency preflight). Two things go a little past the letter of the rulings and should be
confirmed: the ruling says an in-window meter gap is "a recorded liveness fault", and the code also stops the chain
(it reuses the existing monitor-outage stop, which the ruling names, so I read it as covered); and the dead-man now
writes a `REFUSED` `result.json` when none exists.

Bound paths touched, all strict (`AMENDMENT_ALLOWLIST` is empty), checked against `v4_registration.ARTIFACTS`:

| Path | Branch | Note |
|---|---|---|
| `scripts/run_night.py` | 1 | in `STRICT_SCRIPTS` |
| `scripts/align_v4_session.py` | 1 | in `STRICT_SCRIPTS` |
| `scripts/b6_courier.sh` | 1 | in `STRICT_SCRIPTS` |
| `joulewise/b5/driver.py` | 1 | executed closure |
| `joulewise/align/apple/powermode.py` | 1 | executed closure |
| `scripts/magistrate_watchdog.py` | 2 | in `STRICT_SCRIPTS`; see W-E |

Re-registration must also cover:

- `docs/align/v4/dynamic_closure_trace.json` (bound): regenerate. The night runner now imports
  `scripts.align_v4_session` and runs a `km003c_monitor.py` probe child; the courier imports `scripts.run_night`.
- `scripts/km003c_monitor.py` (bound) if F-06 is fixed; `scripts/align_v4_next_arm_packet.py` if F-09 is fixed
  there.

Touched but not bound: `scripts/zero_ntp_frequency.c` (new; a root helper on the arm path, see F-10),
`joulewise/align/w1_smoke.py`, `scripts/align_v4_w1_smoke.py`, the two watchdog process docs, tests and run reports.

## 6. Are the tests meaningful?

Mostly yes. They would fail on the base code: the base has no `chain_outcome` or `fault` keys, marks
`courier.sent` on a file drop, never closes a mode-0 plan, skips the dead-man on `courier.sent`, has no meter
refusal and a single `HOLD_UNSAFE`. Delivery tests push to a real local bare repository and run the real shell
courier. The SIGKILL test uses a real flock holder.

Gaps, each tied to a finding:

- F-01t: the frequency preflight is never run on a real plan.
- F-04: the unproven-chain test sets the global by hand and calls `_close_ac_powermode` directly; the hazard
  driver's own unproven path is untested.
- F-02: `test_dead_man_restores_and_redelivers_when_courier_sent_exists` pins the mutation as intended behaviour.
  No test covers a completed and delivered night, or a second daily fire.
- F-03: two existing assertions were weakened to fit the new file.
- F-06: the in-window outage test mocks `MeterLiveness.check`; nothing drives the real monitor's USB-error loop.

## 7. Native checks on the MBP after R1 closes, in order

Batch the sudo and physical steps (4, 5, 7) while Ed is present.

1. **Close R1 on the armed commit first.** On `20e9edbc4`: read `r1_result.json` status, then `result.json`.
   Uninstall both night plists and confirm `launchctl print gui/$UID/com.joulewise.night` exits 113. Only then
   move `$M` or the canonical checkout. Record `pmset -g custom` and network time.
2. **Install the watchdog** (PR #707 plus branch 2). Run `magistrate_watchdog.py --dry-run`: expect no writes
   and a sane state word. Confirm the installed CLI accepts `--model claude-fable-5-2` with a one-line `-p`
   no-op. Let one activation run and check that `heartbeat` is `PID ACTIVATION EPOCH` with the
   `magistrate.lock` PID, and that `state.json` shows `magistrate_heartbeat.status: observed`.
3. **Real-process test outside the sandbox:**
   `python3.13 -B -m unittest tests.test_b5_driver.LaunchTests.test_chain_digest_mismatch_is_a_flag_and_the_chain_runs`.
4. **Provision the helper and sudo rules.** Build `zero_ntp_frequency.c` from the reviewed source, record
   source and binary sha256, install root:wheel 0755 without setuid. After `sudo -k`, confirm `sudo -n` works
   for the helper, `systemsetup -setusingnetworktime on|off`, `-getusingnetworktime`, and
   `pmset -c powermode 0|2`. Without the query rule every result will carry `host_restoration_incomplete`.
5. **Host-state directory.** `ls -ld /Users/Shared/JouleWise /Users/Shared/JouleWise/host-power`; run
   `prepare` with the override unset and confirm the lock is taken and released.
6. **Frequency preflight, live, after F-01 is fixed.** Network time ON until the word is nonzero, then
   `prepare`: expect OFF verified, helper success, before and after words, a passing bound. Repeat the 180 s
   wall-versus-raw rate measurement. Then ON and OFF again between `prepare` and `install`: `install` must
   re-zero. Then with the helper rule removed: named refusal and no launchd job.
7. **Meter.** Connected: probe live. Unplugged before arm: pre-chain refusal, no `chain.started`,
   `meter_not_sampling`, result pushed. Unplug for 30 s mid-smoke and replug: does the stream resume? (I expect
   not; that settles F-06.) Unplug for more than 600 s: chain stop and `meter_liveness_outage`.
8. **Delivery under launchd.** A smoke night started by launchd pushes `night-results/<plan>` within a
   minute of its terminal record, and the Air watcher sees it. Repeat with Wi-Fi off: `courier.filed`, no
   `courier.sent`, then dead-man re-delivery. Check what `courier.json` says afterwards (F-09).
9. **Terminal-path restores.** Normal end, pre-chain refusal, TERM, and SIGKILL of the outer driver followed by
   the dead-man. After each: `pmset -g custom` shows powermode 0, `-getusingnetworktime` shows On, and the
   result carries the restore record. After F-02 is fixed, confirm a second dead-man fire changes nothing.
10. **Watchdog against the rendered W1 plan.** After `prepare` at the final head and before `install`, run the
    canonical watchdog's `--dry-run`: no `HOLD_PLAN_*`. After `install`: `FENCED` for that plan. This is the
    A-09 check that would have caught the 2.5-day hold.
11. **PREQUAL and W1 smoke at the final integrated head, then STRICT re-registration, then arm.**

## 8. Effect on the armed R1 and the post-R1 install

- Neither branch runs on the MBP until `$M` or the canonical checkout moves. R1 is on `20e9edbc4` and is not
  affected, provided nothing is fetched or checked out there before `chain.exited` (RUN_STATE 251, item 1).
- **Uninstall R1's plists before putting branch 1's code at `$M`.** R1's dead-man plist runs
  `$M/scripts/run_night.py`. With the new code it would rewrite R1's `result.json`, delete its `courier.sent`,
  push again and turn network time ON (F-02).
- **Branch 1 cannot arm as written** (F-01). The first `prepare` after the post-R1 install will refuse.
- **After the first night on this line, every later arm needs the root helper.** The close leaves network
  time ON, so the word will be nonzero and an unprovisioned helper means a named refusal at every `prepare`.
- The watchdog branch's parser accepts W1-line plans (checked on a synthetic plan). No consumer of the literal
  `HOLD_UNSAFE` exists in `scripts/` or `joulewise/` on main, the W1 line or the hostlink branch. No consumer
  of `result.json` on either line demands an exact key set, so the new keys are safe.
- Branch 2 is safe to install after R1 closes. It does not make a hold audible; do native check 10 before
  every arm until W-A is fixed.

## 9. Limits of this review

No MBP contact and no native run: push authentication under launchd, sudo rules, USB behaviour, timed's
behaviour after ON, and the CLI's acceptance of the model flag are unverified. I did not read custody, night or
restricted paths. I did not run the full suite or the long series modules beyond the single W1 probe. I read the
watchdog diff and the functions it touches, not the whole 3,300-line file.
