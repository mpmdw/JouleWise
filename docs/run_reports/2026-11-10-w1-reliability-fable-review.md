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

---

# Delta review (Fable 5.2), 2026-11-10 19:37 PST

Scope: the fixes Sol applied to the findings above. Same binding rules. This section is uncommitted.

| Branch | Head | Final verdict |
|---|---|---|
| `ops/2026-11-10-w1-reliability` | `ec0465fd1` (merges `bb1ec59fc`; fixes in `454d78142`) | **ADMIT.** All 14 findings are closed in code. Six small follow-ups (D-01 to D-06), none blocking; D-01 needs the lead's ratification before registration. Native checks and STRICT re-registration still gate the arm. |
| `ops/2026-11-10-watchdog-unknown-keys` | `343c424e8` (merges `b75feb66f`) | **ADMIT-WITH-FIXES.** W-B and W-C are closed. W-A is built, but it pushes to the remote during an armed span (W-F) and makes magistrate launch depend on the push (W-H). Fix or rule on W-F before this watchdog runs under any armed window, including an R1 re-arm. W-01/W-02 stay open until the native checks pass, as Sol says. |

## D1. What I ran

Branch 1, one module at a time, all passing:

| Module | Result |
|---|---|
| `tests.test_w1_reliability` | 11 |
| `tests.test_w1_reliability_r2` | 18 |
| `tests.test_w1_reliability_r3` | 14 |
| `tests.test_w1_reliability_r4` (new) | 42 |
| `tests.align.test_v4_executed_closure` | 4 |
| `tests.align.test_v4_dynamic_closure` (new to my run) | 10 |
| `tests.align.test_w1_smoke` | 28 |
| `tests.align.test_v4_series.ProductionPathTests` | 1 (42 s) |
| `tests.align.test_v4_next_arm_packet` | 46 (135 s) |
| `tests.align.test_km003c.NightChainTests` | 2 |
| `tests.test_b5_driver_p3.MeterWindowTests` | 7 |
| `tests.external.test_km003c_monitor` | 12, 1 live-device test skipped |
| five `tests.test_run_night` dead-man tests plus `CourierReapingTests` | 9 |

Branch 2 (temporary worktree, removed): `tests.test_watchdog_reliability` 31, `tests.test_magistrate_watchdog_v5` 4,
`tests.test_magistrate_watchdog` 155, all passing. Total test time about 5 minutes.

Probes (scratchpad only, synthetic hosts):

1. **F-01 on a plan from the real writer, preflight not patched.** `tests/align/test_v4_series.py` no longer
   replaces `frequency_word_preflight`; `prepare` in the W1 replay returned `ok: true, action: no_op` with network
   time verified OFF. I then called the real preflight on that same plan four ways:

   | Host condition | Result | Commands issued |
   |---|---|---|
   | word 0, network time OFF | `no_op` | launchd census, query |
   | word 0, network time ON | `no_op` | census, query, OFF, query |
   | word -648908 (item 251), helper works | `zeroed`; bound before 18.27 ms at the plan's 1,800 s span | census, OFF, query, helper |
   | word -648908, helper unavailable | refused, `clock.frequency_word_nonzero` | same, helper fails |

2. **F-04:** hazard night with unproven chain termination now leaves mode 2, network time OFF and the marker, and
   records the deferral. No restore command is issued.
3. **F-02:** two dead-man fires after a completed, delivered night: `result.json` sha unchanged, `courier.sent`
   kept, no courier re-run, no new record.
4. **W-F (new):** installed plan in an active span with an open chain, 25 ticks (about 2 h). Decision `FENCED`
   throughout, remote stop probe `NOT_PROBED` throughout, and 3 status pushes.

## D2. Branch 1: each finding

| ID | Closed? | Note |
|---|---|---|
| F-01 | Yes | Reads `hazard_window.thresholds.clock` with the span from `hazard_window.T_stream_max_s`. A missing budget has its own cause, `clock.frequency_plan_invalid`. Probe 1. |
| F-01t | Yes | The real-writer replay runs the real preflight with injected reader and runner. The kit and cadence unit fixtures still stub it; they write no real plan. |
| F-02 | Yes | No rewrite of `result.json`, no unlink of `courier.sent`. A restored, delivered night is a no-op. Recovery records are create-once and published. Probe 3 and the three-fire test. |
| F-03 | Yes | Stand-down writes the custody log only. Both original assertions are restored. See D-03 for a side effect. |
| F-04 | Yes | `_set_chain_termination_unproven` is called on the hazard path and on an interrupt. Probe 2. |
| F-05 | Yes | A passing word also needs an authenticated OFF. See D-04. |
| F-06 | Yes (code) | Monitor exits 1 after 5 consecutive USB errors; the supervisor restarts it, including after an "absent" exit, with its existing backoff; the chain waits up to 20 s for a first valid batch. Real re-enumeration is native check 7. |
| F-07 | Yes | Unreadable secondary artifacts are omitted and named in `delivery_omissions.json`, the receipt and the log. |
| F-08 | Yes | The fallback result is published at once. |
| F-09 | Consumer side yes | The release check accepts a `courier_delivery` receipt bound to the result digest. No exporter on this line writes that source; whoever builds the window record must add it. |
| F-10 | Yes | Helper digest recorded; C source bound. See D-01. |
| F-11 | Yes | ON only when this night turned it OFF, or the dead-man proves no night job. Signals resume before the courier. See D-02. |
| F-12 | Yes | Stderr tail kept, `courier.filed` removed on success, early return on a failed courier process. |
| F-13 | Yes | Only the last complete batch is decoded; sleep handled with paired clocks; probe child goes through the observed boundary; trace regenerated. See D-06. |

## D3. Branch 1: remaining findings

| ID | Sev | Path:line | Finding | Fix |
|---|---|---|---|---|
| D-01 | LOW (process) | `joulewise/align/apple/v4_registration.py:24`; `configs/campaigns/align_v4/registration/registration_receipt.json` | Registration code and the receipt template were edited to bind the C helper. I recommended it, but the standing restriction was "no registration code", and no ruling for it is quoted in the r4 report. The change only adds a binding. | Lead ratifies it in the deviation log before re-registration. |
| D-02 | MED-LOW | `scripts/run_night.py:4469-4535` | F-05 and F-11 interact. The install preflight now turns network time OFF, but the close restores ON only if the night itself turned it OFF. A refusal before the hazard arm (agent census at t0, powermode admission, host lock, a night that never fires) leaves it OFF and records `network_time: not_owed`, `ok: true`. The dead-man does not restore either, because the night job is still loaded. This reopens part of A-05 for early refusals. It does not hurt the next arm (item 253's restore left it OFF on purpose). | Lead rules: either restore ON on this plan's own non-rerun terminal path whenever network time reads OFF, or keep it OFF and record `left_off` with the observed state instead of `not_owed`. |
| D-03 | MED-LOW | `scripts/run_night.py:5400, 5473-5476` | For a launch-abandoned night the dead-man now does nothing, including no power restore. At base it restored a W1 marker this plan owned. A W1 mode-2 install that never launched stays in High Power until a late night fire or the next session start. The new test pins `host.calls == []`. | Do the restore and log to custody only, as `_close_night_host` does (`:4581`); keep `night/` untouched. |
| D-04 | LOW | `scripts/align_v4_session.py:163` | `_require_night_job_absent` now runs on every preflight, so `prepare` refuses whenever any night job is loaded, with cause `clock.frequency_word_nonzero` and a launchd reason. `prepare` must now follow the previous window's uninstall. | Give it its own cause and state the ordering in the runbook. |
| D-05 | LOW (enhancement) | `scripts/run_night.py` `_chain_outcome` | The 19:05 R1 refusal would now read `fault: true`, `measurement_outcome: refused`, but the class (`step_30b`, `thermal.start_gate_timeout`) still needs a shell on the MBP: `r1_result.json` is not published. | Copy the refused phase name and the refusal code tokens (an allow-listed vocabulary, no values) into `result.json`. |
| D-06 | LOW | `joulewise/b5/driver.py` `MeterLiveness._read_stream` | Only the last batch per check is considered, and an empty poll (`n == 0`) as the last line gives no refresh for that check. At 50 samples/s and 200 ms polls empties are rare, so this is not a practical risk at the current rate. | Use the last non-empty batch; its own `rx` already dates it. |

Also note for native check 7: the monitor restarts after five errors, which is one to three seconds. Count restarts
over a clean hour; the expected number is zero.

## D4. Branch 2: each finding

| ID | Closed? | Note |
|---|---|---|
| W-A | Built, not closed | `scripts/watchdog_status.py` pushes `status.json` and a transition batch to `refs/heads/watchdog-status/<host>`, with a durable outbox, a 25 s budget, prompts disabled and an Air poller with a cursor and latched alarms. Structure only; no reasons, paths or outcomes leave the host. Not closed because of W-F and W-H, and because no Air scheduler or notifier exists yet. |
| W-B | Yes | Anchored prefixes; `desk_fence:` is tested first. |
| W-C | Yes | Growth of the supervisor's own `attempt-N.stream.jsonl` (same inode) is the primary signal; the model heartbeat is second. |
| W-D | Yes, with W-G | A CLI model rejection becomes `HOLD_MODEL_REJECTED`, latched and exported. |
| W-E | Open (by design) | Not ported. Sol's dry merge onto the W1 line shows one conflict in `transition()`. The new module `scripts/watchdog_status.py` must be added to `ARTIFACTS` at the port. |

## D5. Branch 2: remaining findings

| ID | Sev | Path:line | Finding | Fix |
|---|---|---|---|---|
| W-F | HIGH (needs ruling) | `scripts/magistrate_watchdog.py:3340`; `scripts/watchdog_status.py:204`; `docs/process/MAGISTRATE_WATCHDOG.md:93` | Every tick flushes the exporter, and the flush has no plan-span test. During an armed, measuring span the watchdog now pushes to GitHub on each transition and hourly: about ten git processes and three network connections each time. The base watchdog deliberately skips its remote probe in a span (`_remote_probe_allowed`). The doc says the traffic "also runs while fenced", so this was a choice, but it adds network and CPU activity on the measurement host inside windows and nobody ruled on it. Probe 4. My W-A wording ("slow keepalive") did not exclude spans; it should have. | Gate `flush` with `_remote_probe_allowed`. Before the span, push one status carrying the span's end epoch, and have the Air poller hold its staleness alarm until that epoch plus 75 minutes. The night's own terminal push covers the window. |
| W-H | MED (needs ruling) | `scripts/magistrate_watchdog.py:2423, 3098`; `scripts/watchdog_status.py:187` | A missing, failed or hour-old status delivery blocks a new magistrate with `HOLD_STATUS_EXPORT`. Push credentials under launchd become a single point of failure for the unattended system, and the block also removes the magistrate's own mail channel exactly when the export channel is down. Without a running Air poller this is a new quiet no-magistrate state. | Prefer: launch anyway and put a `status_export_failed` notice in the prompt so the two channels fail independently. If the block stays, do not install before the Air poller and its notifier are proven. |
| W-G | LOW | `scripts/magistrate_watchdog.py:2433, 2674` | The rejection check runs at every session end, not only at startup, and matches "model" plus words such as "not available". A transient capacity error can latch a hold that only an operator clears; before, it backed off. | Latch only when the session ended within a short startup window with no assistant output; otherwise back off. |
| W-I | LOW | `scripts/watchdog_status.py:143` | The ref name defaults to `socket.gethostname()`, which on macOS changes with the network. A changed name moves the ref and the Air poller, fixed on one name, alarms. | Set `MAGISTRATE_WATCHDOG_STATUS_HOST` in the watchdog plist and make the install check require it. |

Fail-safe direction on branch 2 is unchanged: every new hold has `launch=False`, plan and desk fences are re-read
immediately before spawn, and no unknown key is tolerated.

## D6. Regressions

None in the modules I ran. Behaviour changes to know about: D-02, D-03 and D-04 on branch 1; W-F and W-H on
branch 2. The first review's native checks 1 to 11 still apply, with these additions:

- Check 2: also prove a status push from the launchd context, then the Air poller exit code and notifier, before
  relying on the watchdog; set the status host name.
- Check 7: count meter restarts in a clean hour.
- Check 8: after a network-down close and a dead-man delivery, build the window record with the
  `courier_delivery` source and run the next-arm check (F-09).
- Check 9: include a launch-abandoned mode-2 case (D-03) and a pre-arm refusal (D-02).

STRICT-bound paths added by round 4: `joulewise/align/apple/v4_registration.py`,
`scripts/align_v4_dynamic_trace.py`, `scripts/align_v4_next_arm_packet.py`, `scripts/km003c_monitor.py`,
`docs/align/v4/dynamic_closure_trace.json`, and the newly bound `scripts/zero_ntp_frequency.c`.

## D7. The 19:05 R1 refusal (RUN_STATE 253)

- **Neither branch touches G0 or the start gate.** A search of both diffs for G0 and start-gate terms finds
  nothing. `joulewise/align/apple/r1_runtime.py` and `scripts/align_r1_rehearsal.py` are not in either diff.
- **Item 253 is A-01 observed live:** `verdict: GO` with `chain_exit_code 3`. R1 runs on `20e9edbc4`, which does
  not have the fix, so a re-arm there will show the same mask. Keep the Air ref watcher keyed on
  `chain_exit_code`, or backport `5bb152acc` (a bound-file change on the armed lane, so a lead decision).
- **Surfacing the class:** see D-05. With branch 1 the result would say `refused` and fault, but not
  `thermal.start_gate_timeout`.
- **Code facts for the diagnosis** (structure only; I read no thermal or custody data):
  - `step-30b` keeps a 600 s G0 cap (`scripts/align_r1_rehearsal.py:112-116`). Ruling R7-2 raised the cap to the
    config's 1,200 s for step-d, X-G, the gated D runs and the planning kinds, with the stated reason that after a
    full load no key reaches G0's slope bar until 840 to 1,040 s after load end
    (`joulewise/align/apple/r1_runtime.py:75-81`).
  - `step-30b` is the only G0-gated segment where a G0 timeout refuses the night. Step-d and the designed start
    states retry once and then record INCONCLUSIVE (`_calibration_segment`); A-B-A legs record INCONCLUSIVE;
    `k_step` raises for anything else (`r1_runtime.py:1681`).
  - Its output is labelled record-only (`30B_record_only`, `align_r1_rehearsal.py:1820`).
  - Not established: whether the 30B member's model load precedes its G0. If it does, 600 s may be structurally
    short and an unchanged re-arm could refuse the same way. That is worth checking before re-arming as
    "operational". Any change to the cap or a retry rule is a design change under item 253 (3), not part of
    these branches.

## D8. Limits

Same as section 9. In addition: the Air poller, the launchd push and the CLI's real rejection text are untested
natively; I did not re-read the whole watchdog file, only the r2 diff, the new status module and the functions
they touch.

---

# Round-5 check (Fable 5.2), 2026-11-10 19:58 PST

Scope: the round-5 fixes for the delta findings, under the lead rulings quoted in
`docs/run_reports/2026-11-10-reliability-r5.md`. Same binding rules. This section is uncommitted.

| Branch | Head | Final verdict |
|---|---|---|
| `ops/2026-11-10-w1-reliability` | `fe6912519` (fixes in `c6d25d963`) | **ADMIT-WITH-FIXES: one small fix, R5-1, before STRICT re-registration.** D-02 to D-06 are closed. D-01 still awaits the research lead's ratification. |
| `ops/2026-11-10-watchdog-unknown-keys` | `5e7c60596` | **ADMIT.** W-F, W-H, W-G and W-I are closed. Safe to install after R1 closes. Three low follow-ups (R5-3 to R5-5). W-01/W-02 stay open until the native launchd push and the Air alarm are proven; W-E (port to the W1 line) is still owed. |

## R1. What I ran

All passing, one module at a time, about 5 minutes.

- Branch 1: `tests.test_w1_reliability` 11, `_r2` 18, `_r3` 14, `_r4` 42, `_r5` 7 (new);
  `tests.align.test_v4_executed_closure` 4; `tests.align.test_v4_dynamic_closure` 10; `tests.align.test_w1_smoke` 28;
  `tests.align.test_v4_series.ProductionPathTests` 1; `tests.align.test_v4_next_arm_packet` 46;
  `tests.align.test_km003c.NightChainTests` 2; `tests.test_b5_driver_p3.MeterWindowTests` 7;
  `tests.external.test_km003c_monitor` 12 with 1 live-device skip; the nine selected `tests.test_run_night` tests.
- Branch 2 (temporary worktree, removed): `tests.test_watchdog_reliability` 39, `tests.test_magistrate_watchdog_v5` 4,
  `tests.test_magistrate_watchdog` 155, `tests.test_install_magistrate_watchdog` 12 (new).

Probes (scratchpad only, synthetic):

1. **D-05 on the item-253 error text.** `_r1_refusal_summary` returns phase `step_30b` and codes
   `['thermal.start_gate_timeout']`.
2. **D-05 failure mode.** With the summary helper made to raise, a refused R1 night ends with no `result.json`, no
   `hazard_result.json` and no courier. This is R5-1.
3. **W-F across a whole span.** A plan with a 2 h window, ticks every 300 s from 22 minutes before the span to
   after its end: one push 120 s before the span carrying the span end, **zero pushes inside the span**, and the
   next push on the first tick after the fence clears.
4. **W-H after a span.** With the earlier notice acknowledged and a new activation id, the first launch after
   the span carries a `status_export_failed` notice although no export failed. This is R5-3.

## R2. Branch 1: each item

| ID | Closed? | Note |
|---|---|---|
| D-01 | Left as ruled | Registration binding unchanged; ratification is the research lead's. |
| D-02 | Yes | Early refusals query network time and never set it. A verified OFF records `action: left_off` with `observed`, `verified` and the reason. A failed query leaves the close incomplete and faults. |
| D-03 | Yes | The dead-man restores power for an abandoned launch through the lock and ownership guards, leaves network time alone, logs to custody only and leaves `night/` byte-identical. A pending launcher or an open chain defers. |
| D-04 | Yes | Causes `prepare.night_job_loaded` and `prepare.night_job_state_unavailable`, raised before any setter or helper call. The runbook states uninstall-before-prepare. |
| D-05 | Yes, with R5-1 and R5-2 | `result.json` gains `chain_refused_phase` and `chain_refusal_codes` from a fixed vocabulary. Numbers, paths and prose are dropped. `chain_outcome` stays a string. |
| D-06 | Yes | An empty final poll no longer displaces the last non-empty batch; that batch's own `rx` dates it. A malformed non-empty final batch still fails closed. |

## R3. Branch 1: left over

| ID | Sev | Path:line | Finding | Fix |
|---|---|---|---|---|
| R5-1 | MED | `scripts/run_night.py:2298` (helper at `:2255`) | `_r1_refusal_summary` runs inside a `try` that catches only `FileNotFoundError`, `OSError` and `ValueError`. It imports `scripts.align_r1_rehearsal` and calls `phase_plan`. Any other exception (an import error, a changed signature, an unexpected type) escapes `_chain_outcome`, and the fallback result write calls the same function and fails again. Probe 2: no `result.json`, no hazard result, no courier. The path runs only for a refused or aborted R1, which is exactly when the record matters. Unlikely in practice, but a reporting-only enrichment must not be able to remove the terminal record. | Wrap the call in `except Exception` and fall back to the null summary (optionally with a `chain_refusal_summary_error` class name). Add a test that makes the helper raise and asserts `result.json` is still written. `run_night.py` is STRICT-bound, so do this before re-registration. |
| R5-2 | LOW | `scripts/run_night.py:2270` | The token pattern allows only letters and underscores, so `episode.g0_unreleased` (in the allow-list) is never extracted from error text. On the item-253 text only `thermal.start_gate_timeout` comes out. The decisive code does surface. | Allow digits inside a token segment (`[a-z_][a-z0-9_]*`). |

Registration note: round 5 touches only paths already bound (`scripts/run_night.py`, `scripts/align_v4_session.py`,
`joulewise/b5/driver.py`). The runbook is not bound. The dynamic closure trace was not regenerated this round;
regenerate it at the final head, since the night runner can now import the R1 rehearsal module.

## R4. Branch 2: each item

| ID | Closed? | Note |
|---|---|---|
| W-F | Yes | Tick, resident and final flushes all go through `_remote_probe_allowed`, and each git subprocess rechecks it. A 50 s guard keeps a push from running into a span. The last pre-span tick pushes `span_end_epoch_s`, and `next_status_expected_epoch_s` tells the Air when to expect the next status. Probe 3. |
| W-H | Yes, with R5-3 | A missing, failed or old export no longer blocks a launch; it adds a `status_export_failed` notice. Plan and desk fences keep priority. |
| W-G | Yes | The rejection latch applies only within 60 s of spawn and only with no assistant output; later errors use the existing backoff. |
| W-I | Yes | Host name comes only from `MAGISTRATE_WATCHDOG_STATUS_HOST`; the installer refuses without a valid value and writes it into the plist. A missing value at run time disables export and raises the notice. |

## R5. Branch 2: left over

| ID | Sev | Path:line | Finding | Fix |
|---|---|---|---|---|
| R5-3 | LOW-MED | `scripts/watchdog_status.py:195-209`; `scripts/magistrate_watchdog.py:2060, 2475` | `launch_hold` still calls a receipt older than 3,600 s stale. After W-F the export is silent for the whole span on purpose, so the first launch after any window longer than an hour gets a false `status_export_failed` notice (probe 4). The same happens on the first tick after install, before any push was tried. The prompt tells the magistrate every notice is something Ed must hear, so this is one false mail per window. | Judge freshness against the last delivered record's own `next_status_expected_epoch_s`, or flush once before deciding when the probe is allowed. Treat "nothing attempted yet" as not a failure. |
| R5-4 | LOW (by design) | `scripts/magistrate_watchdog.py:2032-2044` | An unparseable plan makes the span unknown, so export is deferred. The W-01 case therefore reaches the Air as `watchdog_status_stale` within 75 minutes, not as a named hold. That is the conservative choice and it does alarm. | Say so in the Air notifier text: "stale" can mean an unreadable armed plan. |
| R5-5 | LOW | `scripts/magistrate_watchdog.py:2046-2055` | The announced span end is the plan's completion epoch. If a night never releases, the fence runs to the dead-man tail, which is exactly 75 minutes later, so the Air alarm and the fence end coincide and a stale alarm can show for one tick. A desk fence has no announced end at all. Both cases are already abnormal or rare. | Add one tick of margin; announce a desk fence's end if it has one. |

Still open on branch 2, unchanged: W-01/W-02 until the launchd push and the Air poller plus notifier are proven
natively; W-E. At the port to the W1 line, bind the new `scripts/watchdog_status.py` and note that the bound
`configs/launchd/com.joulewise.magistrate.plist.template` changed. `scripts/install_magistrate_watchdog.sh` is not
bound.

## R6. Regressions

None in any module I ran. The native checks in sections 7 and D6 still apply. Two more for this round: confirm
on the MBP that no status push occurs between the pre-span status and chain exit during a real armed span, and
that the Air poller stays quiet through the span and alarms if the post-span status does not arrive.

---

# Rounds 6-7 check (Fable 5.2), 2026-11-10 20:48 PST

Scope: the round-6 fixes for R5-1 to R5-5 and the round-7 changes under research-lead ruling RL-26, plus a
merge and port preview against the W1 integration line at `7770d6a4f` (claim contract B). Same binding rules.
This section is uncommitted.

| Branch | Head | Final verdict |
|---|---|---|
| `ops/2026-11-10-w1-reliability` | `e2fca0096` | **ADMIT.** No code finding is left open. It merges cleanly with claim B. Native checks and STRICT re-registration at the integrated head still gate the arm. |
| `ops/2026-11-10-watchdog-unknown-keys` | `6e0647a61` | **ADMIT.** R5-3 to R5-5 are closed. W-01/W-02 stay open until the launchd push and the Air alarm are proven natively. The port to the W1 line is more than the one textual conflict (section S4). |

## S1. What I ran

All passing, one module at a time.

- **Branch 1 at `e2fca0096`** (about 6 minutes): `tests.test_w1_reliability` 11, `_r2` 18, `_r3` 14, `_r4` 42, `_r5` 7,
  `_r6` 3 (new), `_r7` 10 (new); `tests.align.test_v4_executed_closure` 4; `tests.align.test_v4_dynamic_closure` 10;
  `tests.align.test_w1_smoke` 28; `tests.align.test_v4_series.ProductionPathTests` 1; `tests.align.test_v4_series_e2e`;
  `tests.align.test_v4_kit` (`SessionParameterTests`, `W1HighPowerTests`, `W1DiskGateTests`);
  `tests.align.test_v4_next_arm_packet` 46; `tests.align.test_km003c.NightChainTests` 2;
  `tests.test_b5_driver_p3.MeterWindowTests` 7; `tests.external.test_km003c_monitor` 12 with 1 live-device skip; the
  nine selected `tests.test_run_night` tests.
- **Branch 2 at `6e0647a61`** (temporary worktree, removed): `tests.test_watchdog_reliability` 45,
  `tests.test_magistrate_watchdog_v5` 4, `tests.test_magistrate_watchdog` 155, `tests.test_install_magistrate_watchdog` 12.
- **Dry-run merge of branch 1 with `7770d6a4f`** (temporary worktree, `git merge --no-commit`, aborted and removed;
  about 11 minutes): `tests.align.test_v4_executed_closure` 4, `tests.align.test_v4_dynamic_closure` 10,
  `tests.align.test_v4_registration` 22, `tests.align.test_v4_claim_b_packet` 15, `tests.align.test_v4_series` 16,
  `tests.align.test_v4_test_reserves` 2, `tests.align.test_v4_replacement_windows` 20,
  `tests.align.test_v4_next_arm_packet` 46, `tests.test_w1_reliability_r3` 14, `_r4` 42, `_r7` 10.

Probes re-run at the new heads (scratchpad only, synthetic):

1. **R5-1:** with the summary helper made to raise, the refused R1 night now writes `result.json` and
   `hazard_result.json` and runs the courier.
2. **R5-2:** the item-253 text yields `step_30b` with both `episode.g0_unreleased` and
   `thermal.start_gate_timeout`.
3. **R5-3 and W-F together:** across a 2 h window, zero pushes inside the span; no `status_export_failed`
   notice on the first tick after install or on the first launch after the span (new activation id, earlier
   notices acknowledged).

## S2. Branch 1

| Item | Closed? | Note |
|---|---|---|
| R5-1 | Yes | `except Exception` around the summary; both the primary and the fallback result writes are tested with a raising helper. |
| R5-2 | Yes | Digits allowed inside a token segment; near-miss tokens are still rejected. |
| D-01 | Yes (RL-26) | Deviation row in `docs/align/v4/DEVIATIONS.md` with the ruling quoted verbatim and its source commit. |
| RL-26 condition (a) | Yes | Every preflight, including a no-op, records the installed helper's path and SHA-256 beside the receipt-bound source digest, and checks the source bytes against that digest. A needed helper that is missing or unreadable refuses as `clock.frequency_helper_unreadable` before the helper or the installer runs. An unbound or drifted source refuses as `clock.frequency_helper_source_unbound`. |
| RL-26 condition (b) | Yes | `clock_frequency_pre_t0` in the arm record: a read-only in-process kernel read after the arm checks and the disk gate, before the quiet-dwell stamp, with read start and finish times and the plan's t0. It adds no threshold; it refuses only if the read fails or t0 has passed. |

Notes, none of them findings:

- The source-binding check does not add an ordering constraint: `prepare` already requires a signed
  registration receipt (`require_w1_ready`), so the smoke and the arm both run after registration.
- The helper digest pair shows which binary ran, not that it was built from the bound source. Build
  provenance stays in the provisioning record (native check 4).
- "Last pre-t0 word" is the session's last read before the dwell, not a read at t0. The hazard arm at t0 still
  owns admission.
- The dynamic closure trace regenerated byte-identical in round 7. Regenerate it again after the claim B merge.

## S3. Branch 2

| Item | Closed? | Note |
|---|---|---|
| R5-3 | Yes | Freshness is judged against the delivered record's own `next_status_expected_epoch_s`; "nothing attempted yet" is not a failure; the launch boundary checkpoints and flushes (still gated by the span test) before classifying. Probe 3. |
| R5-4 | Yes | The Air poller prints `notifier_text` saying a stale status can mean an unreadable armed plan; the doc says the same. |
| R5-5 | Yes | The expectation now covers the fence end plus one 300 s tick; the record carries `span_fence_end_epoch_s`, `span_end_margin_s` and `desk_fence_end_announced: false`. |

Nothing new found. Still open by design: W-01/W-02 (native launchd push, Air scheduler and notifier), and W-E.

## S4. For the integration seat

### Branch 1 into `7770d6a4f`

- **Textual merge is clean.** Three files changed on both sides and all auto-merge:
  `scripts/align_v4_next_arm_packet.py`, `docs/align/v4/DEVIATIONS.md`, `tests/align/test_v4_series.py`.
- **`scripts/align_v4_next_arm_packet.py`: no overlap.** Branch 1 touches only `terminal_release_check`
  (the `courier_delivery` receipt, about line 172). Claim B touches `build_packet` (thermal rulings, lead-ruling
  rows, test-window bars) and adds a constant near line 42. The merged file passed the claim B packet tests and
  the next-arm packet tests.
- **`tests/align/test_v4_series.py`:** claim B edits `ManifestTests` and `PacketTests`; branch 1 edits
  `FakeWorld.replay`. The whole module passed on the merged tree, including the replay over the new manifest.
- **`docs/align/v4/DEVIATIONS.md`:** both sides add rows; no ID collision (`D-01` versus `B-*`, `V4-*`, `RL16-*`,
  `U5-closure`). It is a bound file.
- **After the merge, regenerate `docs/align/v4/dynamic_closure_trace.json`** and re-run both closure modules;
  claim B changes executed series and packet code. The receipt template needs no further edit from branch 1.
- **Still owed from F-09:** no exporter on either line writes the `courier_delivery` source into a window
  record.

### Branch 2 onto `7770d6a4f`

The W1 line did not change its watchdog in claim B, so the picture is the same as before, but it is larger than
"one conflict":

1. **`scripts/magistrate_watchdog.py`: one textual conflict, in `transition()`.** Keep the W1 line's
   `[*boundaries, event]` append and add the status checkpoint after it.
2. **Missing module.** The watchdog branch imports `scripts.launch_align_r0` (the desk fence: `FENCE_NAME`,
   `fence_lock`, `read_fence`). That file is not on the W1 line, and the W1 watchdog has no desk-fence code. A
   three-way merge carries the import through without a conflict, so the merged watchdog would fail at import:
   a crash-looping watchdog and no magistrate. Either port `scripts/launch_align_r0.py` (and
   `scripts/run_align_r0_launchagent.sh` if the fence is used) or strip the desk-fence paths. Decide which
   before merging.
3. **W1-only watchdog features that must survive:** the J4 High Power restore on a launch-abandoned release
   (`powermode.restore_owed` through `deps.power_runner`), the timing-receipt hold boundaries
   (`joulewise.timing_receipts`), and `mark_production_entry("magistrate_watchdog")` (R7-10). The watchdog branch
   has none of them. A three-way merge keeps them; a file copy would silently drop them.
4. **`joulewise/night_gate.py`: two conflict hunks** (both lines added `ac_powermode` differently). Take the
   W1 line's file; I checked earlier that the two parsers differ only in reason codes and comments, and that the
   watchdog branch's parser accepts a W1-line plan.
5. **New files to bring:** `scripts/watchdog_status.py`, `tests/test_watchdog_reliability.py`,
   `tests/test_magistrate_watchdog_v5.py`, and `scripts/post_window_unstrand.sh` if it is still wanted (branch 1's
   close and dead-man now cover most of it).
6. **Registration.** `scripts/watchdog_status.py` (and `scripts/launch_align_r0.py` if ported) are executed by a
   bound script and must be added to `v4_registration.ARTIFACTS`. That is another registration-code edit: get
   it ratified the way D-01 was. The bound `configs/launchd/com.joulewise.magistrate.plist.template` changes too.
7. **Run on the integrated tree before anything else:** the four watchdog modules, both closure modules, and a
   `--dry-run` tick. None of my watchdog results apply to the ported file.

## S5. Remaining gates

No code finding remains on either branch. What is left is outside these branches: the native checks in
sections 7, D6 and R6; STRICT re-registration at the integrated head; the Air poller and notifier; the
`courier_delivery` exporter; and the watchdog port above.
