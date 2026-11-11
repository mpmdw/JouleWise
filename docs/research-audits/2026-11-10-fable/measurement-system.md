# Measurement-system audit, 2026-11-10 (Fable 5.2, independent seat)

Scope: the measurement system end to end as it runs on the MBP for the armed ALIGN v4 R1
(arm, schedule, chain, driver, runtime, instruments, courier, dead-man, watchdog, post-window
restore, hostlink, offload). Audit only; no code was changed.

**How to read the evidence.** Paths are prefixed with the tree they were read in:

| Prefix | Commit | What it is |
|---|---|---|
| `armed:` | `20e9edbc4` (`lane/2026-11-08-r1-arm-fixes`) | the code R1 is armed on (RUN_STATE 225, 249) |
| `main:` | `bfe0f4c78` | this worktree |
| `wdv5:` | `df5311456` (`ops/2026-11-10-watchdog-v5-installed`) | the watchdog fix, not installed yet |
| `hostlink:` | `f3d2d7882` (`ops/2026-11-10-hostlink`) | Air-to-MBP link scripts |
| `offload:` | `b5af05e12` (`ops/2026-11-08-air-offload-merged`) | Air offload tool |

**Method note (please read).** `main` does not contain the R1 route at all (no `joulewise/align/`,
no `scripts/arm_align_r1.py`, no `scripts/hostlink/`, no `post_window_unstrand.sh`). To audit what
is actually armed I read the lane commits with `git show` / `git archive` into the session
scratchpad. That reads the repository's shared object store, which sits outside the worktree
directory. I read code, configs and runbooks only: no `records/*` branch, no custody or data
path, nothing under the pruned directories. If that reading of the rule is narrower than
intended, the affected findings are every one marked `armed:`, `wdv5:`, `hostlink:` or `offload:`.

"VERIFIED" means I (or a forked seat of this audit, then spot-checked by me where marked)
read the code path. "INFERENCE" means it follows from the code but depends on host behaviour
I could not observe.

---

## 1. Verdict

The measuring core is careful: process-group termination is proven rather than assumed, the
High Power marker is written before the mode change, G0 and segment redos are bounded, and
disk, external-volume and monitor-outage checks are live. The weakness is everything around
the measurement that tells a human what happened. As armed today, R1 can still fail in the
same way it failed on 11-08 and be just as quiet about it: the night's `result.json` says
`GO` for any chain exit code (A-01), the courier for this route writes a file and marks
`courier.sent` without sending mail (A-02), the installed watchdog is known to hold on these
plists (W-01), and the no-SSH rule means nobody can see an early refusal until the 29-hour
ceiling passes. Separately, the KM003C DC-in meter is non-gating and has no liveness check, so
a missing or unplugged meter loses the channel for the whole window with `fault: false`
(I-01), which is against Ed's rule that every measurement captures it. None of this corrupts
a number that R1 does produce; the cost is lost windows, days of idle Mac, and a host left
with network time off or in High Power. Before the next arm (W1), fix the reporting path,
the meter gating and the watchdog/plan version skew; all three are small.

---

## 2. System map

```
magistrate (headless Claude, launched by the watchdog)        Air (lead)
  | arm_align_r1.py prepare/render/install                      | hostlink: jwssh, mbp_link_monitor.sh
  v                                                             | (no SSH during armed spans)
install_night_agent.sh -> joulewise.night_agent_install
  writes ~/Library/LaunchAgents/com.joulewise.night.plist          (calendar: Month/Day/Hour/Minute = t0)
         ~/Library/LaunchAgents/com.joulewise.night.deadman.plist  (calendar: Hour/Minute only, daily)
  env in plist: PATH only

launchd (gui domain) at t0
  v
scripts/run_night.py run --plan $S/night_plan.json --courier-bin $M/scripts/b6_courier.sh
  | agent census -> AC powermode admission (plan ac_powermode 0; reads markers, takes no lock)
  v
joulewise/b5/driver.py run_hazard_night   (receipt_class HAZARD_PACK)
  | caffeinate keep-awake
  | hazard arm (joulewise/hazards/arm.py): clock, battery, thermal, contention, disk,
  |   instrument; turns network time OFF (sudo -n systemsetup)
  | hazard monitor  (scripts/hazard_monitor.py, taskpolicy -b)  -> $S/hazards/monitor/
  | KM003C monitor  (scripts/km003c_monitor.py, plain QoS)      -> $S/hazards/meter/stream-NNN.jsonl
  | in-window agent census every 30 s (PausingCensus), disk floor, monitor liveness
  | window deadline thread: t0 + window_max_s + 300 s -> TERM, 30 s, KILL
  v
$S/chain.zsh  (generated wrapper, new session / process group)
  | sha256 pin of the chain source -> exit 65 on mismatch
  | arm_align_r1.py _display-dwell   (pmset displaysleepnow, 300 s)
  | arm_align_r1.py _bookend pre     (validate_powermetrics_fiducial.py, 1,800 s budget, never a veto)
  | scripts/night_chains/align_r1_rehearsal.zsh
  |     sudo -n -l rule check, restore Automatic, EXIT/TERM traps restore Automatic
  |     scripts/align_r1_rehearsal.py  (R1 driver: HostLock, PowerModeGuard, phase plan,
  |        11:45-13:15 batch wait, redo/retry, renames to .rejectedN / g0-timeout)
  |         per segment: scripts/align_r1_runtime.py -> joulewise/align/apple/r1_runtime.py
  |            (WP15 seam: sudo -n powermetrics, SMC thermal sidecar, CPU journal,
  |             battery journal; writes runtime_result.json + runtime_custody.json)
  |     -> $S/night/align-r1/r1_result.json (status), r1_slots.json (only if complete)
  | arm_align_r1.py _bookend post
  v
back in run_night: hazard_result.json, result.json (verdict), courier (b6_courier.sh: file drop
  into <custody parent>/courier-program/, touches night/courier.heartbeat and night/courier.sent)

dead-man (daily HH:MM of t0 + window_max_s + 300 + 3600): skips if courier.sent exists; stands
  down before the completion epoch; else proves the chain gone, reaps monitors, courier.

watchdog (com.joulewise.magistrate, StartInterval 300 s, RunAtLoad, no KeepAlive): one tick of
  scripts/magistrate_watchdog.py per run, FROM THE CANONICAL CHECKOUT, not from $M. Reads
  ~/night-custody/*/night_plan.json plus the plans named by installed night plists (the only
  route to an R1 custody under ~/night-align/). Fences the span; when clear, forks a resident
  supervisor that runs `claude -p <prompt> --model opus --permission-mode auto`.
  State (paths as text from the code): ~/night-custody/magistrate/{state.json, events.jsonl,
  magistrate.lock, watchdog.lock, standdown.request, notice.ack, heartbeat, STOP, attempts/}.
  Self-clearing states: BACKOFF*, CLOCK_UNCERTAIN, NETWORK_UNCERTAIN, HOLD_CENSUS, bounded FENCED.
  Human-only exits: STOPPED, HOLD_UNSAFE, FENCED with chain.started and no chain.exited.

post-window (manual, docs/align/r1_arm_runbook.md section 4, on the lane only): network time ON,
  read r1_result.json, pmset -g custom, uninstall plists, check stray monitors.
```

State that outlives a window and needs someone to clear it:

| State | Where | Cleared by |
|---|---|---|
| Night and dead-man plists | `~/Library/LaunchAgents` | magistrate `uninstall`, or `wdv5: scripts/post_window_unstrand.sh --go` |
| Network time OFF | system setting | magistrate, by hand (`sudo -n systemsetup -setusingnetworktime on`) |
| AC powermode 2 + markers | `/Users/Shared/JouleWise/host-power/high-power.marker`, `$M/.align-r1-high-power` | driver guard, chain trap, next admission, next R1 start, or by hand |
| Host night lock | `/Users/Shared/JouleWise/host-power/night.lock` (flock) | kernel, on process death |
| Hazard and meter monitors | process groups in `night/monitor_supervision.jsonl`, `meter_supervision.jsonl` | driver, or dead-man reap |
| Courier drop | `<custody parent>/courier-program/*.json` | nothing reads it |

---

## 3. Findings

Severity: BLOCKER = do not arm the next window until fixed; HIGH = can lose a window or a
channel silently; MED = can strand the host or weaken a result under a plausible trigger;
LOW = hygiene. "R1" in the last column means the currently armed window is exposed.

| ID | Sev | Finding | Affects | Conf. |
|---|---|---|---|---|
| A-01 | HIGH | `night/result.json` says `GO` for any chain exit; no fault is raised for R1 | R1 + future | high |
| A-02 | BLOCKER | R1's courier sends nothing and still marks `courier.sent`; an early refusal is invisible for up to 29 h | R1 + future | high |
| A-03 | HIGH | The armed system is not on `main`; four or more divergent lines; live path imports modules on the prune list | future | high |
| W-01 | BLOCKER | Watchdog holds indefinitely, with no alarm, on any plan it cannot parse (version skew); the pending fix covers one key | R1 + future | high |
| W-02 | HIGH | No liveness signal leaves the MBP; magistrate or watchdog silence is undetectable | R1 + future | high |
| I-01 | HIGH | KM003C DC-in is non-gating, unmonitored, and absent from R1's records | R1 + future | high |
| A-04 | MED | High Power is not restored after a kill of the R1 driver until the next arm or a human | R1 | high |
| A-05 | MED | Network time is left OFF with no automated restore | R1 + future | high |
| A-06 | MED | R1 driver runs each runtime segment with no wall timeout | R1 | med |
| A-07 | MED | Dead-man never kills; a root-owned survivor makes the chain unprovable forever | R1 + future | med |
| A-08 | MED | An agent appearing mid-window neither stops nor pauses R1 | R1 | high |
| A-09 | MED | No pre-arm check of production-only paths; tests always use the seam | future | high |
| A-10 | MED | `r1_result.json` can be absent or truncated on several exits | R1 | high |
| A-11 | MED | All LaunchAgents are gui-domain: a reboot or logout stops everything | R1 + future | med (inference) |
| I-02 | MED | AC loss mid-window is silent for R1 and would mislabel A-B-A legs | R1 | high |
| I-03 | MED | Display state is set once and never observed again | R1 | med |
| I-04 | MED | One gap over 5 s in the CPU journal refuses the whole night | R1 | med |
| I-05 | MED | The chain's zsh restores Automatic outside the lock discipline | future (W1) | high |
| W-03 | MED | The Air's link monitor can SSH into an armed span and register as an agent | R1 if `armed_until` is unset | med |
| W-04 | MED | Watchdog releases a window on `result.json`'s verdict alone; an R1 refusal reads as collected | R1 (after the fix is installed) | high |
| W-05 | MED | `post_window_unstrand.sh` only uninstalls; the rest of the post-window steps are unchecked prose | R1 | high |
| W-06 | MED | Hostlink setup changes the measurement host (pmset, `NOPASSWD: ALL`) | applied config (inferred) | med |
| A-12 | LOW | Window deadline runs on a clock that stops during sleep | R1 | high |
| A-13 | LOW | Bookend and display-dwell failures surface nowhere | R1 | high |
| A-14 | LOW | Stale night plists block the offload until a manual uninstall | future | high |
| I-06 | LOW | Battery read failures are silent | R1 | high |
| W-07 | LOW | An unparseable plan also removes the t0-relative stand-down | future | high |
| W-08 | LOW | Other silent no-magistrate states (CLI flags, GitHub reachability, stop branches, clock step) | future | med |
| W-09 | LOW | Watchdog logs and event journal grow without bound | future | high |
| W-10 | LOW | R1 custody is outside the watchdog's scan path; the plists are the only link | R1 + future | high |


### 3.1 Arming, scheduling, chain and reporting

**A-01 HIGH. `night/result.json` says `GO` for any chain exit.** VERIFIED.
- Evidence: `armed: joulewise/b5/driver.py:2754-2759`: with no abort and no `chain.stop`,
  `verdict = "GO"  # it describes the arm`; a non-zero exit changes only the process exit
  code. `:2767-2784`: `fault_reasons` has no entry for a non-zero chain exit. `:1766-1767`:
  R1 plans zero members, so the yield is `UNKNOWN`, never `EMPTY`.
  `armed: scripts/run_night.py:2121-2126` writes that verdict beside `chain_exit_code`.
  Same logic on `main: joulewise/b5/driver.py:2614` and on the W1 line (`9abe6095f`, line 2756).
- Scenario: the R1 driver refuses (exit 3) or aborts (exit 4), or the wrapper exits 65. The
  record reads `verdict: GO`, `fault: false`, `chain_exit_code: 3`. This is the 11-08 loss,
  unchanged in the armed commit.
- Consumers that key on it: the dead-man (`run_night.py:5040-5043`), the offload's terminal
  check (`offload: scripts/offload_window.py:710`), the unstrand script's markers.
- Fix: a non-zero chain exit is `CHAIN_FAILED` with `fault_reasons: ["chain_exit:<rc>"]`.
  For a single-chain plan, copy the inner status (`r1_result.status`, or "absent") into
  `result.json` and the report facts as `measurement_outcome`.
- R1: exposed. RUN_STATE 249 already tells the next activation to read `r1_result.json` first.

**A-02 BLOCKER. The courier for this route sends nothing, and still marks `courier.sent`.** VERIFIED.
- Evidence: `armed: joulewise/align/r1_arm.py:271` passes `--courier-bin scripts/b6_courier.sh`.
  `armed: scripts/b6_courier.sh:15-26` writes the prompt to `<custody parent>/courier-program/`
  with `"transport": "file", "mail_sent": False`, then touches `night/courier.heartbeat` and
  `night/courier.sent`. Nothing in the tree reads `courier-program/` (grep). The runbook says so:
  `armed: docs/align/r1_arm_runbook.md:174-175`, "starts no agent and sends no email".
- So the only report of an R1 outcome is the next magistrate activation, which the watchdog
  must launch, and the installed watchdog holds on these plists (W-01; RUN_STATE 249 item 2).
  The lead may not SSH during the armed span, so it cannot see `chain.exited` either.
- Scenario: R1 refuses at about t0 + 35 min for any new reason. The MBP sits idle until
  Wed 11-11 19:03 PST, then until someone runs the post-window steps. `courier.sent` exists,
  so the dead-man skips, and RUN_STATE 249's "the courier sent normally" was true only of the marker.
- Fix: (1) a program mailer or push on the terminal record (block 6 already has
  `joulewise/b6/mailer.py`); (2) `courier.sent` only when a transport delivered, otherwise
  `courier.filed`; (3) a "chain exited" signal the Air can read without a shell on the MBP.
- R1: exposed, and not fixable while armed. See recommendation 1 for the one decision Ed can make now.

**A-03 HIGH. The armed system is not on `main`, and the lines have diverged.** VERIFIED.
- Evidence: `git merge-base --is-ancestor 20e9edbc4 bfe0f4c78` is false; the merge base is
  `d842f697f`; `git diff --stat main 20e9edbc4 -- scripts joulewise` is 309 files. There are at
  least four live variants of the night driver and plan parser: `main`, the armed lane, the W1
  line (`align/2026-11-08-v4-r11` @ `9abe6095f`), and the watchdog fix (`df5311456`, based on
  `main`). `main: joulewise/night_gate.py` has no `ac_powermode` field at all; the armed lane
  writes it into every plan (`armed: joulewise/align/r1_arm.py:167`).
- `main: CANONICAL.md` does not name `lane/2026-11-08-r1-arm-fixes` or `20e9edbc4`; it still
  says the R1 driver is on `lane/2026-11-06-v4-r1-integrated` and "not yet on the measurement lane".
- Prune dependency (the brief asked for this): the live path imports modules on the prune
  list at import time. `main: scripts/run_night.py:49-51` (`arm_readiness`,
  `arm_readiness_evidence_t0`, `night_gate`, `t0_rehearsal`, `network_time_off`) and `:1053`
  (`t0_rehearsal.observed_popen` launches every chain); `main: scripts/magistrate_watchdog.py:41,49`
  (`night_gate`, `arm_retry`); `armed: joulewise/align/r1_arm.py:19`,
  `armed: joulewise/b5/driver.py:62`, `armed: joulewise/night_agent_install.py:1214` (`night_gate`).
- Scenario: the prune deletes `night_gate.py` or `t0_rehearsal.py` from `main`; the next lane
  merged onto `main` cannot import `run_night`, or a watchdog installed from `main` cannot start.
  Or, as already happened, a watchdog from one line cannot parse a plan from another.
- Fix: land the armed route on `main` before pruning; move `NightPlan`, `agent_census` and
  `observed_popen` out of the CA-42 modules first; name the armed commit in `CANONICAL.md`.

**A-04 MED. High Power is not restored after a kill of the R1 driver.** VERIFIED.
- Evidence: the outer driver registers its close-time restore only for plan mode 2
  (`armed: scripts/run_night.py:4517-4521`); R1 plans mode 0 and sets High Power itself. The
  dead-man returns before any restore when `courier.sent` exists (`:5040-5043`), which for this
  courier is always. When it does run, it passes an owner (`:4124-4129`), and
  `armed: joulewise/align/apple/powermode.py:181-182` makes `owned_by` false for any marker
  that is not a W1 marker; R1 writes `R1_MARKER_TEXT` (`armed: scripts/align_r1_rehearsal.py:476-478`).
  The driver's own comment says the markers are "left for the dead-man" (`:1857-1858`).
- Scenario: the deadline or a supervision stop sends TERM, the driver's teardown overruns the
  35 s group budget (its own child grace is 20 s plus a 30 s reap, `:185,196`), KILL follows.
  After an adopted A-B-A the rest of the D series runs in mode 2, so the exposure is hours, not
  one leg. The host stays in High Power until the next admission, the next R1 start, or a human.
- Fix: once the chain is proven gone and the lock is free, the close and the dead-man restore
  any marker (the "session start" rule, `owner=None`). Do not skip that on `courier.sent`.

**A-05 MED. Network time is left OFF.** VERIFIED.
- Evidence: the arm turns it off (`armed: joulewise/b5/driver.py:100`); R1 disables G10
  (`armed: joulewise/align/r1_arm.py:154`), the only code that turns it on. The runbook:
  "the night leaves it OFF" (`r1_arm_runbook.md:179`). `wdv5: scripts/post_window_unstrand.sh:2`
  is "no-sudo" and does not restore it.
- Scenario: 11-08 to 11-10, the clock free-ran for about 2.5 days. Any strand repeats it.
- Fix: the close (or dead-man) turns it back on when `network_time_off.action.json` shows this
  night turned it off, using the existing narrow sudo rule.

**A-06 MED. No wall timeout on a runtime segment.** VERIFIED for the code; the hang is INFERENCE.
- Evidence: `armed: scripts/align_r1_rehearsal.py:340-357`: `_run` calls `process.communicate()`
  with no timeout, for every segment and for `sudo`/`pmset` (`:541-556`). `segment_bounds`
  (`:138-156`) is used only for the batch-window wait.
- Scenario: a segment blocks (a stuck SMC read, powermetrics that never returns a frame, an
  `idle` whose loop does not end). The driver waits until the outer deadline, 29 h later, is
  then killed, and `r1_slots.json` is never committed.
- Fix: timeout = that segment's bound times a margin, then `Refusal` and exit.

**A-07 MED. The dead-man never kills, and a root-owned survivor cannot be disproved.** VERIFIED for the code; the trigger is INFERENCE.
- Evidence: `armed: scripts/run_night.py:5098-5114`: if the chain's group is alive at the
  dead-man, it writes a refusal and returns; `PermissionError` counts as alive (`:5102-5103`).
  `_signal_group` swallows `PermissionError` (`:505`). The runtime starts `sudo -n powermetrics`
  inside the chain's group.
- Scenario: `run_night` dies (SIGKILL, crash) with the chain running, or `sudo` is killed before
  it relays TERM and root `powermetrics` is orphaned in the group. Every later dead-man fire
  says "chain alive"; the watchdog fences for want of `chain.exited`. Only a human with sudo ends it.
- Fix: past completion plus grace the dead-man terminates the group; add a narrow sudo rule to
  kill a `powermetrics` whose parent is gone, or classify root-only survivors separately.

**A-08 MED. An agent appearing mid-window neither stops nor pauses R1.** VERIFIED.
- Evidence: `armed: joulewise/b6/agent_pause.py:60-88,97-106`: a positive census returns no
  refusal until 7,200 s cumulative (`PAUSE_LIMIT_S`); it writes `collection/pause.json`, and an
  episode ends only after 600 s with no sighting (`PAUSE_RESUME_S`). Neither
  `align_r1_rehearsal.py` nor `r1_runtime.py` reads that marker (no `pause` in either).
- Scenario: a Claude session or Claude.app starts on the MBP at hour 6. R1 measures through
  it for up to two hours. The night gets an `agent.presence` flag; `r1_result.json` gets
  nothing unless the 0.5-core / 60 s rule happens to fire.
- Fix: the R1 driver checks the marker between segments and redoes an overlapped one; copy the
  presence intervals into `r1_result.json`.

**A-09 MED. Production-only paths are first exercised inside the window.** VERIFIED.
- Evidence: `armed: joulewise/align/r1_arm.py:87-88`, `prepare` "without executing a probe".
  The first `mkdir`/`open` under `/Users/Shared/JouleWise/host-power` is at
  `align_r1_rehearsal.py:1622-1625`, after the 300 s dwell and the pre bookend.
  `armed: tests/align/__init__.py` sets `JOULEWISE_HOST_STATE_DIR` for every ALIGN test, and
  `tests/align/test_r1_arm.py:366-367` stubs the courier to "sent". The runbook's `unset` lines
  (`r1_arm_runbook.md:39-40`) act on the magistrate's shell, not on launchd's environment.
- Still unprobed before t0: a `pmset -c powermode 2` round trip, KM003C and libusb,
  powermetrics under launchd, and whether the installed watchdog can parse this plan.
- Fix: `arm_align_r1.py preflight`, run by `prepare` under `mark_production_entry`: HostLock
  acquire and release, the four sudo rules, a meter init, and the installed watchdog's own
  parser on the rendered plan. The last one would have caught the 2.5-day hold.

**A-10 MED. `r1_result.json` can be absent or truncated.** VERIFIED.
- Evidence: `armed: scripts/align_r1_rehearsal.py:1924-1934` returns 3 with no record (bad
  inputs, refused override); `:1592-1594` can raise before the `try`; the wrapper can exit 65
  or fail in `_display-dwell` before the driver runs (`r1_arm.py:212-216`); a KILL writes
  nothing, since `status: running` is never persisted; `:1896` is a plain `write_text`.
- Scenario: the post-window reader is told to "read status first" and finds no file. Combined
  with A-01 the night still says `GO`.
- Fix: write `status: running` atomically at start, replace atomically at the end; readers
  treat "absent" as "not measured".

**A-11 MED. Everything is a gui-domain LaunchAgent.** INFERENCE from the plist and install code.
- Evidence: `armed: configs/launchd/com.joulewise.night.plist.template` (`RunAtLoad false`,
  calendar only); `r1_arm_runbook.md:160-161` prints `gui/$(id -u)/...`.
- Scenario: a panic, power loss or automatic security update reboots the MBP. Without
  auto-login (FileVault) no agent loads: no night, no dead-man, no watchdog. A t0 that passes
  while the Mac is off is not replayed.
- Fix: decide and document auto-login and `pmset autorestart`; have the Air alarm on a missed
  heartbeat rather than on a message.

**A-12 LOW.** The deadline is tracked on `time.monotonic()` (`run_night.py:1157-1167`), which
stops during sleep on macOS (RUN_STATE item 20). A sleep moves the "latest end" later by its
length; the wall-clock dead-man then meets a live chain. Keep-awake makes this unlikely.

**A-13 LOW.** The pre bookend's exit code is ignored and both bookends record failures only in
`bookends/*.json` (`r1_arm.py:217,241-262`); a failed `displaysleepnow` is a line in
`night/r1_wrapper.jsonl`. Neither reaches `result.json` or `r1_result.json`.

**A-14 LOW.** The offload treats any `com.joulewise.night*.plist` as armed
(`offload: scripts/offload_window.py:104,1632-1634`). The plists stay until someone uninstalls
them, so a strand also blocks the offload, and then disk.

### 3.2 Instruments

**I-01 HIGH. KM003C DC-in is non-gating, unmonitored and absent from R1's records.** VERIFIED (I re-read `km003c_monitor.py` myself).
- Evidence: `armed: scripts/km003c_monitor.py:4-5`, "never a refusal, never a claim number";
  `:166-167`, an absent meter writes a header and exits 0. `armed: joulewise/b5/driver.py:2462`,
  `restart_on_clean_exit=False`, so one failed init (four attempts, about 4 s) is final for the
  window. `km003c_monitor.py:186-189`: a `UsbError` on a poll writes an `e` line and loops
  forever; it never re-inits and never exits, so the supervisor sees a healthy process. The
  driver flags only start, crash-loop, record and stop faults (`driver.py:2448-2500`); there is
  no liveness check on meter samples (the liveness check covers the hazard monitor's journals
  only). `align_r1_rehearsal.py`, `r1_runtime.py` and `align_v4_kit.py` never mention the meter;
  libusb is looked up only under Homebrew paths (`armed: joulewise/external/km003c_usb.py:59`).
- Scenario: the meter re-enumerates at hour 2, or was never attached. Result: `verdict GO`,
  `fault: false`, `r1_result.status: complete`, and no DC-in for 27 hours.
- This is against Ed's rule (every measurement captures the KM003C, every analysis uses the
  DC-in channel). The runbook states the opposite position openly: "a diagnostic and meter
  absence does not veto R1" (`r1_arm_runbook.md:110-111`). The W1 line appears to add a
  "meter reader live" triage (`9abe6095f: joulewise/align/w1_prequal.py:396`); I did not verify it.
- Fix: a pre-arm meter probe that refuses or records an explicit waiver; the monitor exits
  non-zero after N consecutive USB errors and retries "absent" with backoff; a driver liveness
  check on the last `b` line with `n > 0`, feeding `fault_reasons`; stream digests and coverage
  in `r1_result.json`.

**I-02 MED. AC loss mid-window is silent for R1.** VERIFIED (spot-checked).
- Evidence: `_check_member_powermode` (`align_r1_rehearsal.py:1538-1545`) compares the value
  from `parse_ac_powermode` (`powermode.py:20-31`), which reads the "AC Power" profile setting
  whatever the active source. The runtime's battery journal records `ac`; nothing reads it.
- Scenario: the charger drops (it did on 10-10, RUN_STATE item 19). caffeinate keeps the Mac
  awake, R1 measures on the battery profile, and leg B is recorded as mode 2.
- Fix: refuse or redo a segment whose battery rows show AC absent or discharging.

**I-03 MED. Display state is unobserved after t0.** VERIFIED for the code; the energy effect is INFERENCE.
One `pmset displaysleepnow` (`r1_arm.py:231`), then nothing reads display state for 29 h. A
wake adds WindowServer GPU work to R1's GPU-energy outputs. Fix: journal display power state
per segment and redo on a wake.

**I-04 MED. One gap over 5 s in the CPU journal refuses the whole night.** VERIFIED (spot-checked); the probability is INFERENCE.
`align_r1_rehearsal.py:900-901` raises `Refusal`, not a redo. The same ticker thread also runs
`pmset -g batt` every 30 ticks (`r1_runtime.py:1319-1326`), each call with its own timeout. One
slow `ps` or `pmset` at hour 20 ends R1 with no slots. Fix: make a gap a segment redo, and move
the battery poll off that thread.

**I-05 MED (W1 only). The chain's zsh restores Automatic outside the lock discipline.** VERIFIED.
`armed: scripts/night_chains/align_r1_rehearsal.zsh:17,25` runs `sudo -n pmset -c powermode 0`
unconditionally at start and on EXIT, while the Python driver refuses to restore without the
host lock (`align_r1_rehearsal.py:1859-1863`). A late R1 fire under a measuring W1 High Power
night would set mode 0 beneath it. Fix: route both through `powermode.restore_owed`.

**I-06 LOW.** A failed battery read is journaled and a null drain is accepted
(`r1_runtime.py:646-647`; `align_r1_rehearsal.py:676-678`).

Instrument summary:

| Instrument | Started by | If missing or dead mid-window |
|---|---|---|
| KM003C DC-in | hazard driver (`driver.py:2457-2464`) | silent (I-01) |
| SMC power keys (second DC-in view) | hazard monitor, 1 Hz | 600 s of silence stops the chain (`driver.py:2577-2588`) |
| powermetrics | R1 runtime, `sudo -n` | member fails; segment refusal |
| SMC thermal sidecar, G0/G1 | R1 runtime | fault; G0 timeout is retried once, then INCONCLUSIVE |
| CPU journal and census | R1 runtime ticker | gap refuses the night (I-04) |
| Battery / AC | runtime every 30 s; hazard journal | recorded, never judged in R1 (I-02) |
| Agent census | hazard driver, 30 s | flag only, up to 2 h (A-08) |
| Keep-awake | hazard driver, caffeinate | flags only |
| Display | wrapper, once | never observed again (I-03) |
| High Power + HostLock | R1 driver | refusal (exit 3) |
| Disk floor, external volume | hazard driver; R1 driver | stop / refusal |

Checked and sound: G0 is bounded (config cap, one precool and retry); segment redos are capped
at two; the host lock is a `flock`, so no stale lock or pid reuse; markers are written and
fsynced before the mode change; the meter stream flushes each second and stamps RAW, monotonic
and wall clocks at both ends; the replay-recorder environment variable refuses rather than
being silently dropped (`run_night.py:714-719`).

### 3.3 Watchdog, magistrate, unstrand, hostlink

One caveat on every watchdog citation: the watchdog runs from the canonical checkout, not
from `$M`. I audited `main`'s `scripts/magistrate_watchdog.py` as the installed one; which
commit that checkout is on needs the MBP.

**W-01 BLOCKER. The watchdog holds indefinitely and silently on any plan it cannot parse.** VERIFIED (spot-checked; a forked seat reproduced the parse error with a synthetic plan).
- Evidence: `main: joulewise/night_gate.py:466`, `if keys != expected_keys`: the plan parser
  demands an exact key set, and `main` does not know `ac_powermode`, which the armed lane
  writes into every plan (`armed: joulewise/align/r1_arm.py:167`).
  `main: scripts/magistrate_watchdog.py:2050-2051`: any snapshot error returns `HOLD_UNSAFE`.
  `:3079-3084`: a notice is queued only for `CLOCK_UNCERTAIN`, `NETWORK_UNCERTAIN`,
  `HOLD_CENSUS`, plan conflicts and corrupt locks, and the only delivery of a notice is the
  next magistrate's prompt, which the hold prevents. `main: docs/process/MAGISTRATE_WATCHDOG.md:30`
  documents the hold as intended.
- That is the 2.5-day hold of 11-08, in code. It will recur for the armed R1 (RUN_STATE 249,
  next-activation item 2).
- The pending fix closes one key, not the class: `wdv5: joulewise/night_gate.py:464-465` adds
  `ac_powermode` to the accepted set, and `wdv5: tests/test_magistrate_watchdog_v5.py:87-97`
  pins "unknown key or schema holds". The same exactness applies to the schema version
  (`main: night_gate.py:488`), the hazard-window key set (`:738`), and a plan authored "in the
  future" after a backward clock step (`magistrate_watchdog.py:774`). A malformed plan left under
  `~/night-custody/*/` also holds. The next new plan field from any lane repeats the outage.
- Fix: keep the fail-closed hold, but (1) every `HOLD_*` older than N minutes raises an alarm
  that does not need a magistrate (program mail, or a status word the Air polls); (2) the arm
  refuses unless the installed watchdog's own `load_plans` accepts the rendered plan; (3) the
  watchdog and the plan writer come from one pinned commit.

**W-02 HIGH. No liveness signal leaves the MBP.** VERIFIED.
- Evidence: the magistrate's prompt tells it to write a `heartbeat` file; nothing in
  `main: scripts/magistrate_watchdog.py` reads it. `ACTIVE` lasts as long as the pid lives, with
  no maximum duration. A quiet relaunch sends nothing, by design. Reports go through one
  channel, the Gmail connector of a headless model session. The Air's monitor reports only
  "label loaded" and a `pgrep -x claude` count (`hostlink: scripts/hostlink/mbp_link_monitor.sh:18`).
- Scenario: the watchdog is held, stopped, crash-looping at import, or not loaded after a
  reboot; or the magistrate hangs. From the Air all of these look like "no mail", which is also
  what a healthy quiet night looks like. This is failure (c), and it is structural.
- Fix: export the watchdog's state word, its transition time and the heartbeat mtime (none is
  outcome-bearing) to somewhere the Air reads, and alarm there on staleness.

**W-03 MED. The Air's link monitor can connect during an armed span and register as an agent.** Mechanism VERIFIED; how often it fires is INFERENCE.
- Evidence: `hostlink: scripts/hostlink/mbp_link_monitor.sh:19-27`: the only gate that prevents
  a connection is a local file `armed_until`, and nothing in the repository writes it (the
  comment says "the lead (or the arming procedure) writes"; the arming magistrate runs on the
  MBP and cannot). The remote guard (`:11-12,18`) runs after the SSH session exists. The probe
  string itself contains `claude`, and the census pattern is `[c]odex|[c]laude` over full
  command lines (`armed: joulewise/night_gate.py:220`), so the probe's own shell matches while
  it lives. `jwssh` has no armed guard at all.
- Effect on this R1 (HAZARD path): a hit is not an abort; it opens a presence episode that
  lasts until 600 s clean, flags `agent.presence`, and counts toward the 7,200 s stop (A-08).
  With a 300 s probe cadence and a 30 s census, a handful of hits across 29 h is plausible.
  On the older non-hazard path a hit terminates the chain (`armed: scripts/run_night.py:1338-1339`).
- Fix: default-deny on the Air (probe only when a fresh "idle" marker exists); write
  `armed_until` from the arm notice; call a neutrally named helper on the MBP; test the monitor.
- R1: check now, on the Air only, that `armed_until` holds this window's latest end, or unload
  the monitor until then. That needs no contact with the MBP.

**W-04 MED. The watchdog releases a window on `result.json`'s verdict alone.** VERIFIED.
`main: joulewise/arm_retry.py:296-300`: any terminal verdict with `chain.exited` is
`collected_window`; neither `chain_exit_code` nor the inner record is read. Once the fixed
watchdog is installed, an R1 that refused will be released as collected with no notice. This is
A-01 again, one layer up. Fix: a non-zero `chain_exit_code` queues a notice.

**W-05 MED. `post_window_unstrand.sh` only uninstalls.** VERIFIED.
- Evidence: `wdv5: scripts/post_window_unstrand.sh:2` ("no-sudo"); `:33-38` refuses unless
  `chain.exited`, `result.json` and `courier.sent` all exist, by existence only; `:70-105`
  refuses on a stray `hazard_monitor.py` or `km003c_monitor.py` and offers no way to stop one.
- So it does not cover a refusal before the chain, a courier failure, or A-07; it does not
  restore network time or the power mode; and an R1 refusal still passes its marker check.
  Its tests stub `launchctl`; a real `bootout gui/...` over SSH is unexercised. The script
  exists only on the unmerged fix branch. The other post-window steps
  (`armed: docs/align/r1_arm_runbook.md:179-201`) are prose with no check that they happened.
- It is otherwise careful: idempotent, `set -euo pipefail`, refuses against a live chain.
- Fix: one `post_window.py` that reads the inner status, restores network time and Automatic
  through the narrow rules, reaps recorded monitor groups, uninstalls, and writes a record; the
  next arm refuses if the previous window has no such record.

**W-06 MED. Hostlink setup changes the measurement host.** VERIFIED in the script; whether it was applied is INFERENCE.
`hostlink: scripts/hostlink/hostlink_setup.sh:187-193` sets `pmset -c sleep 0`, `womp 1`,
`tcpkeepalive 1`; `:222` installs `<user> ALL=(ALL) NOPASSWD: ALL`. The headless magistrate
runs as that user in auto-permission mode, so it now has unrestricted root, which widens the
"root-owned artifact in a user path" class behind the 11-08 refusal, and the chain's "narrow
rule only" premise no longer describes the host. A Tailscale daemon during windows is
unassessed. No secrets are in the repository and host-key checking is kept.
Fix: record these host changes in the R0 host-state record; keep sudo narrow for the
magistrate's user, or run the link under a separate account.

**W-07 LOW.** With an unparseable plan the resident magistrate gets only the 9 + 1 minute error
drain, not the t0-relative ladder (`main: scripts/magistrate_watchdog.py:2622`); arming inside
about 11 minutes of t0 with a magistrate still alive gives a census refusal at t0.

**W-08 LOW.** Other states that end in "no magistrate, no message": fixed CLI flags against an
auto-updating `claude` binary; the stop probe needs an unauthenticated `git ls-remote` to
GitHub; any branch matching `ops/stop*` stops it; a wake or a clock step over 60 s kills the
resident session. Each is deliberate; none alarms off the box.

**W-09 LOW.** `launchd.out|err`, `events.jsonl` and `attempts/*/` are never rotated, and
`events.jsonl` is re-read on every tick.

**W-10 LOW.** R1's custody is under `~/night-align/`, outside the watchdog's scan directory, so
the installed plists are the watchdog's only knowledge of the window: plists removed while a
chain is alive means no fence. For the same reason the courier's watchdog-liveness line looks
in the wrong place for R1 (`armed: scripts/run_night.py:1669`, `<custody parent>/magistrate/state.json`)
and would report the watchdog dead.

Folded into earlier findings: the dead-man's early return on `courier.sent` (A-04), the
permanent fence behind an orphaned chain (A-07), and the watchdog's imports of prune-list
modules, including a test fixture read at import (`main: scripts/magistrate_watchdog.py:41-65,77`) (A-03).

---

## 4. What I could not verify (needs the MBP)

- Whether R1 is measuring right now, and whether `hazards/meter/stream-001.jsonl` has status
  `streaming` or `absent`.
- Which commit the canonical checkout (and so the installed watchdog) is on, and its state file.
- Whether `com.joulewise.hostlink.monitor` is loaded on the Air and whether `armed_until` was
  written for this R1 (an Air-side check; I did not look outside the worktree).
- What `launchctl list` returns over SSH for gui-domain agents, and the process name of the
  `claude` binary, which decide whether the link monitor's remote guard works at all.
- Whether the hostlink `pmset` changes, `NOPASSWD: ALL` and Tailscale are in effect on the MBP.
- Ownership of `/Users/Shared/JouleWise` itself (the 11-10 fix created only the leaf) and of
  the files inside `host-power`.
- The sudoers content; that `pmset -c powermode 2` and `systemsetup` succeed unattended; that
  libusb resolves under launchd's PATH-only environment.
- Auto-login, FileVault, `pmset autorestart`, and whether `local.jwbench.keepawake` is loaded.
- Whether root `powermetrics` survives when its `sudo` parent is killed.
- The Mac's system time zone (the batch-window code assumes America/Los_Angeles,
  `align_r1_rehearsal.py:95`).
- Display state and AC state through the window.
- Anything about the content of the custody directories; I did not open them.

No test modules were run: the armed code's tests are not in this worktree, and running `main`'s
would not have exercised the armed route. A forked seat ran two small read-only Python probes on
synthetic input (the `main` plan parser on a plan with `ac_powermode`, and the census filter).

---

## 5. Top five recommendations, in priority order

1. **Today, for the armed R1, without touching the MBP.** Nothing will announce an early
   end (A-02, W-01, W-02). Three things can be done from the Air: confirm the link monitor's
   `armed_until` holds this window's latest end or unload it (W-03); set the alarm for
   Wed 11-11 19:03 PST plus grace and run the post-window steps then, reading
   `r1_result.json` status before `result.json` and treating "absent" as "not measured"
   (A-01, A-10); and have Ed rule whether one neutral existence check of `night/chain.exited`
   is allowed earlier, since a repeat of the 11-08 refusal would otherwise cost another day.
   At that visit also check the meter stream's header status (I-01), network time (A-05) and
   `pmset -g custom` (A-04).
2. **Make the outcome impossible to misread and impossible to miss** (A-01, A-02, W-01, W-04).
   A non-zero chain exit is not `GO`; the inner status is copied into `result.json`; a program
   mailer delivers the terminal record; `courier.sent` means delivered; every `HOLD_*` and
   every non-zero exit raises an alarm that needs no magistrate. Before the next arm.
3. **Gate the KM003C and the power source** (I-01, I-02). Pre-arm meter probe, in-window sample
   liveness, re-init on USB loss, AC-present check per segment, and the stream's coverage in the
   window's own result. Ed's rule is not met by the code as armed.
4. **Give the close ownership of everything the window changed** (A-04, A-05, A-07, W-05).
   Network time, Automatic power, monitor groups and the plists are restored by the close or the
   dead-man, with a record, and the dead-man gets a bounded kill ladder. The next arm refuses
   without that record.
5. **One line of code, pinned, with a production preflight** (A-03, A-09, W-01). Land the armed
   route on `main` before the prune removes `night_gate`, `t0_rehearsal` and friends; install the
   watchdog from the same commit that writes the plans; add `arm_align_r1.py preflight` that
   exercises the real host-state directory, the sudo rules, the meter and the installed
   watchdog's parser; and update `CANONICAL.md` to name what is armed.
