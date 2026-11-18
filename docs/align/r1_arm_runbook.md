# Arm ALIGN v4 R1

This is a magistrate procedure on the measurement Mac, after R0 passed. Build
seats run synthetic tests only. The route is one `HAZARD_PACK` LaunchAgent
window, containing diagnostic calibration bookends and the existing R1 chain.
It does not run the W1 roster. No R1 measurement code or kit numbers change.

**R1 follow-up night (2026-11-12 port).** This route was pinned at
`20e9edbc4` for the first R1 night. It now lives on the presign line beside the
follow-up driver (RL-59/RL-64/RL-72), with two changes and nothing else:
the window is sized to RL-72 E2 (section 2), and the plan carries no
`ac_powermode` key. Absent means 0 (`night_gate.NightPlan.ac_powermode`), the
same Automatic admission as before; the R1 driver still owns every A–B–A and
series power transition and its restore. Without the key, the magistrate
watchdog on `main` can parse the installed plan (items 249 and 262: it held
`HOLD_UNSAFE` on `extra ['ac_powermode']`). The arm item in RUN_STATE, not
this runbook, names the commit, the D-7 prepare-packet step and the RL-89
checks; step 1's fetch line below is the first night's and is superseded by it.

## 1. Advance the existing measurement checkout

Use the checkout with the already pinned environment, rather than rebuilding
its dependencies. Against `9c40e4e5d`, this branch changes **no dependency file**:
`pyproject.toml`, `env/mac-measurement-lock.txt`, and `env/analysis-lock.txt`
are identical. The checkout below starts at `9c40e4e5d`; the move to the R1
branch is deliberately a non-fast-forward checkout, preserving its `.venv`.
Preserve local changes if status reports any; do not force checkout over them.

```zsh
export M=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2
git -C "$M" status --short --branch
git -C "$M" fetch origin refs/heads/lane/2026-11-08-r1-arm
git -C "$M" switch --detach FETCH_HEAD
git -C "$M" rev-parse HEAD
git -C "$M" status --short --branch
export PY="$M/.venv/bin/python"
"$PY" -B -c 'import mlx.core,mlx_lm,transformers; from importlib.metadata import version; print(*(version(x) for x in ("mlx","mlx_lm","transformers")))'
```

The versions must still be `0.31.2 0.31.3 5.12.1`. No package installation is
part of this route. Use the existing R0 host preparation: Mac15,9 on AC and
not charging, no external volume mounted, narrow sudo permission for the two
`pmset -c powermode 0/2` commands, network-time OFF/ON permission and working
powermetrics. The driver's unchanged volume and power guards remain in force.
The established keep-awake job stays loaded (RUN_STATE item 19).

```zsh
pmset -g custom
pmset -g assertions
sudo -n -l
unset JOULEWISE_HOST_STATE_DIR ALIGN_R1_RUNTIME ALIGN_R1_INPUTS ALIGN_R1_REGISTRATION
unset EVIDENCE_POWER_RECORDER_REPLAY NIGHT_VERIFY_ONLY NIGHT_RESERVATION_ARGV_ONLY
```

Read-only `pmset` is shown here. Do not manually select High Power: R1 admits
Automatic (the plan's `ac_powermode` is absent, meaning 0) and owns its A–B–A power transitions and restore.
Do not delete a persistent High Power marker by hand. A leftover marker is an
owed restore; the existing admission/driver handles it with the host lock.

## 2. Select t0, prepare and review

Prefer starting just after a known maintenance episode has ended, with the
opening soak quiet. Quiet segments already avoid the programmed 02:00–02:35
Pacific batch interval (RL-149 §2.9 item 4; it was 11:45–13:15 under RL-72 E2).
A roughly 29-hour ceiling cannot avoid every scan.
See the scheduling answer below: repeated contamination can refuse the night.
If quiet segments cannot avoid the listed jobs, notify the lead **before
arming**, as RUN_STATE item 202(4) requires. This is a scheduling notification,
not authority to change a threshold or a segment.

Set t0 only when the review/notice is ready, **at least 15 minutes from now**
(R1-ARM-FIX-1 arm notice). Preparation enforces this interval. The existing
installation cutoff is t0 minus the watchdog's 180-second plan lead minus the
driver's 120-second install-close margin. Allow the existing 180-second
installer budget (`bytes_h_session.install`) before that cutoff, and choose a
later t0 if review/notice/install needs more time. Rounding is to a whole minute
because the shared calendar requires it.

```zsh
export S="/Users/edr/night-align/r1-$(date -u +%Y%m%dT%H%M%SZ)"
export T0="$("$PY" -B -c 'import math,os,sys,time; sys.path.insert(0,os.environ["M"]); from joulewise.align.r1_arm import ARM_NOTICE_S; print(60*math.ceil((time.time()+ARM_NOTICE_S)/60))')"
"$PY" -B "$M/scripts/arm_align_r1.py" size --t0 "$T0"
"$PY" -B "$M/scripts/arm_align_r1.py" prepare --measurement-root "$M" --custody-root "$S" --t0 "$T0"
df -g /Users/edr | tee "$S/df-arm.txt"
cat "$S/arm.json"
"$PY" -B "$M/scripts/arm_align_r1.py" render --custody-root "$S" --output "$S/rendered"
plutil -p "$S/rendered/com.joulewise.night.plist"
plutil -p "$S/rendered/com.joulewise.night.deadman.plist"
```

`window_max_s` is 119,880 s for every t0 (RL-72 E2's construction at the RL-149
blackout; it was 126,480 s). `size` prints the terms, the local 02:00 crossings
(disclosed) and the final seconds; `arm.json` keeps the same derivation. It is a
ceiling, not a reservation.

**What is inside the driver's span, and what is outside it (from the code).**

- The driver's span is `align_r1_rehearsal.night_worst_case_s()["programmed_span_s"]`
  = 102,168 s: the no-redo phase subtotal (58,711.9616 s), two whole-unit load
  redos and two batch encounters (largest unit 7,563.9952 s + 2,100 s blackout,
  RL-149 §2.9 item 4; RL-72 E2 had 5,400 s and 108,768 s), rounded up to
  93,168 s, plus 9,000 s overhead. That overhead is the driver's
  OWN segments: `pre_calibration_bracket` and `post_calibration_bracket`
  (`r1_phase_table.py`, kinds `calibration-pre`/`-post`, 1,800 s each in
  `phase_bound` and `_run`), close 900 and harvest 4,500.
- The driver's work deadline is its own start + 102,168 − 900 s
  (`_R1_WORK_DEADLINE`), and every runtime child's cap is clipped to it.
- This route's wrapper (`r1_arm.wrapper_bytes`) runs OUTSIDE the driver, before
  and after the chain: the hazard arm (inside run_night's t0 deadline), the 300 s
  display dwell, and two D-109 fiducial bookends (`validate_powermetrics_fiducial.py`
  under the stage budget helper), which are not the driver's calibration brackets.
  The 11-10 R1 night ran both: `bookends/{pre,post}.json` and the driver's
  `pre_calibration_bracket` phase.

| Term | Seconds | Source |
|---|---:|---|
| R1 follow-up driver span | 102,168 | RL-72 E2 at the RL-149 blackout; `night_worst_case_s` on the measurement checkout (refuses any other value) |
| Hazard admission, inside the t0 deadline | 3,300 | `b5.plan.T0_STAGE_CAP_S` |
| Two diagnostic bookends | 3,600 | twice `b5.chain.STAGE_WALL_BUDGET_S.pre_calibration_capture` (1,800 each) |
| Bookend teardown/close allowances | 1,200 | twice the existing 600-second session-status budget; covers the budget helper's 30-second TERM grace |
| Final R1 harvest/result writes | 600 | one existing session-status wall allowance |
| Display sleep dwell before the pre bookend | 300 | R0-L3 / RUN_STATE items 206, 209 |
| **Route base** | **111,168** | sum |
| **`window_max_s`** | **119,880** | max(plan writer `b6.plan_inputs.window_max_s(102,168)` = 119,880, `r1_arm.R1_FOLLOWUP_WINDOW_S` 119,880, base) |

No batch allowance is added on top: the driver's span already holds two
encounters, and the driver refuses a third. A 119,880 s window holds at most two
local 02:00 starts; `size` refuses more. The latest driver end after t0 is
3,300 + 300 + 1,830 + 102,168 = 107,598 s; with the post bookend (1,830) and the
final writes (600) that is 110,028 s, inside 119,880 s. The outer driver keeps
its existing 300-second shutdown grace after `window_max_s`.

**D-7 at arm time.** `prepare` records in `arm.json` the path and SHA-256 of
`$M/.align-r1-prepare.json`, the packet the chain hands the driver (a missing
packet is flagged `r1.prepare_packet_absent_at_arm`; the chain refuses without
it). Compare that SHA-256 with the one `align_r1_followup_kit.py prepare`
printed, before install. The driver's `r1_result.json` `prepare_packet.sha256`
gives the same comparison after the night.

The two bookends are ordinary diagnostic D-109 fiducial observations. They
are **not a claim-eligible reserved W1 bracket**: R1 may exceed the existing
24-hour claim-bracket horizon. Failures/timeouts are recorded in
`bookends/{pre,post}.json` and do not veto the R1 chain. No W1 harvest runs.
The shared KM003C monitor also starts; it is a diagnostic and meter absence
does not veto R1. R1's v4 residual is GPU energy (item 212 R11-3).

Before either bookend, the generated wrapper checks the SHA-256 of
`scripts/night_chains/align_r1_rehearsal.zsh` against a literal captured from
the measurement checkout at preparation. A mismatch or unreadable source
exits 65 before display preparation, bookends or the chain. This is the same
chain-source pin as agreement D5 / the Opus wrapper; it does not authenticate
every transitive Python import. The installer checks checkout heads at install.
Preserve those bytes: **no git operation in the measurement checkout between
install and t0**, including status/fetch/checkout. The wrapper then calls
`pmset displaysleepnow` and dwells 300 s before the pre bookend; sleep-command
failure is a flag, never a veto. `night/r1_wrapper.jsonl` records the sleep
outcome and dwell start/end.

The R1 sampler-span allowance is 5,764 seconds, the ceiling of the revised
`segment_bounds` maximum (5,763.9952 s, shared by step-30b, step-d and the designed states) at the committed G0 timeout and step deadman. Clock
admission uses the **existing ALIGN pilot S-7 hold** from `b6.plan_inputs`:
5 ms / span minus 0.25 ppm, with placement judged by each run's own fit. Do
not substitute Block 5's old 3.7 ms placement hold: even zero rate would give
3.7 + 0.25 × 5764 / 1000 = 5.141 ms and always refuse.

The default allocation is explicitly **unsized**, flagged in `arm.json`;
the shared 20 GiB arm headroom and 10 GiB live disk floor stay. If a sourced
R1 footprint estimate exists, pass its bytes with `prepare --planned-bytes`.
Do not substitute Block 5's unrelated 182 MiB-per-member estimate. The plan
author creates no model copies or backups.

## 3. Notice, install, then exit

Send Ed the following content through the magistrate's ordinary notice route,
filling times/head from `arm.json` and `git rev-parse HEAD`. This command does
not send mail. There is no new notice approval protocol.

> ALIGN v4 R1 hardware rehearsal is arming on Mac15,9, after R0 passed.
> Measurement checkout/head: …; custody: … . t0: … Pacific / … UTC.
> Ceiling: … s after t0 (the final `arm.json` value), plus the existing 300 s shutdown grace; it
> normally ends as soon as R1 completes. No agent session will remain at t0.
> Please keep the Mac on AC, not charging, with the external SSD unplugged;
> the display stays asleep; do not wake/touch the Mac or start agents or other
> work until the latest end time … . Security Responses
> remain automatic. Scheduled-job contamination may redo a segment and can
> refuse R1 after its retry cap; the lead has been notified if those times
> cannot be avoided. R1 owns High Power and restores Automatic. KM003C runs
> as a diagnostic; R1's own outputs use GPU energy. The allocation estimate
> is unsized unless a sourced estimate was supplied. I will report the R1
> terminal record and power restore afterwards.

```zsh
"$PY" -B "$M/scripts/arm_align_r1.py" install --custody-root "$S"
launchctl print "gui/$(id -u)/com.joulewise.night"
launchctl print "gui/$(id -u)/com.joulewise.night.deadman"
pmset displaysleepnow
```

The magistrate sleeps the display before exiting. No git operation in `$M`
is allowed between install and t0. Exit the magistrate and every other agent
session now. Do not run the driver
or `--dry-arm` from an agent tree as a live probe. LaunchAgent is the wake
source; the installed plists name the absolute `night_plan.json`, so the
watchdog's existing installed-plan fence sees this custody even outside its
usual scan directory. It suppresses relaunch during the plan span and while
an opened chain lacks `chain.exited`. An early daily dead-man fire on a
multi-day window returns before the completion epoch; the later fire handles
recovery. The supplied courier is the existing file-only `b6_courier.sh`,
which starts no agent and sends no email.

## 4. On return, preserve the result and uninstall

At the next activation after R1, read `$S/night/align-r1/r1_result.json` and
the chain's exit code first. Do not rely on `result.json`'s `verdict`: it can
read GO for a refused chain (audit A-01).

Network time: restoring it ON re-creates the kernel frequency-word hazard for
the next arm (RUN_STATE item 251). Before the next arm, set network time OFF
and run the zero step.

**R_op after a redo (cold pass F1, 2026-11-10).** If the accepted `step_30b`
attempt index is above 0, R_op was captured after a full 30B turn rather than
after the soak. It may then be high by an unmeasured amount. Read
`operating_minus_soak_c` (about +1.06 C on 11-10). Send such a night to the
ruling seat before any R_op-gated number is used. This rule is a flag. The
night is not refused.

Also read first the G0 outcomes of the three sensors-only releases between
the A-B-A legs (cold pass observation 1). They keep a 600 s cap.

```zsh
sudo -n systemsetup -setusingnetworktime on
cat "$S/night/align-r1/r1_result.json"
cat "$S/night/align-r1/r1_slots.json"
cat "$S/night/result.json"
pmset -g custom
"$PY" -B "$M/scripts/arm_align_r1.py" uninstall --custody-root "$S"
```

For an interrupted run, slots may be absent; the terminal result and custody
are retained. `r1_result.json` is the R1 outcome, not the shared launcher's
zero-W1-member yield summary. Check the observed Automatic restore before
recording completion. If termination was unproven, retain markers for existing
dead-man/session-start recovery. Preserve the complete custody directory,
including rejected attempts and bookends. The unchanged shared hazard branch
can leave its diagnostic monitor/meter until dead-man recovery on an interrupt
(integration report R8 residual); do not describe a power restore as proof that
those diagnostic processes ended. The lead owns live verification and the
post-R1 record/kit fill.
At this activation also check for stray `km003c_monitor.py` and
`hazard_monitor.py` processes (agreement D7).

## Scheduled jobs during R1 (item 202(4))

The scheduler's job name/time is not a trigger. Software Update (about
23:09/05:09/11:09/17:09), the midnight `/tmp` cleanup, trustkit's four-hourly
xx:31 task, XProtect around 05:40 and the 12:53 maintenance all have the same
load handling. Outside the explicit 02:00–02:35 start exclusion (RL-149), R1 does not
pause a running quiet segment and wait for those jobs. It finishes that
attempt, then redoes it if background load exceeded 0.5 core for 60 consecutive
1 Hz samples. Heavy redos first release against the soak. Two redos are allowed;
contamination of all three attempts **refuses R1**. Missing/gappy load evidence
can also refuse; ordinary short contamination is recorded. A pure G0 timeout
has its separate INCONCLUSIVE/retry rule. The outer 5% contention monitor
journals the event; it does not turn a scheduled task into an immediate night
refusal. See `align_r1_rehearsal.py:869`, `:879`, `:980`, `:1050`, `:1273`
and `hazards/monitor.py:581`.
