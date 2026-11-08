# Arm ALIGN v4 R1

This is a magistrate procedure on the measurement Mac, after R0 passed. Build
seats run synthetic tests only. The route is one `HAZARD_PACK` LaunchAgent
window, containing diagnostic calibration bookends and the existing R1 chain.
It does not run the W1 roster. No R1 measurement code or kit numbers change.

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
`pmset -c powermode 0/2` commands, network-time OFF permission and working
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
Automatic (`ac_powermode: 0`) and owns its A–B–A power transitions and restore.
Do not delete a persistent High Power marker by hand. A leftover marker is an
owed restore; the existing admission/driver handles it with the host lock.

## 2. Select t0, prepare and review

Prefer starting just after a known maintenance episode has ended, with the
opening soak quiet. Quiet segments already avoid the programmed 11:45–13:15
Pacific batch interval. A roughly 29-hour ceiling cannot avoid every scan.
See the scheduling answer below: repeated contamination can refuse the night.
If quiet segments cannot avoid the listed jobs, notify the lead **before
arming**, as RUN_STATE item 202(4) requires. This is a scheduling notification,
not authority to change a threshold or a segment.

Set t0 only when the review/notice is ready. This example leaves the existing
180-second installer budget (`bytes_h_session.install`) before the exclusive
installation cutoff. The cutoff itself is t0 minus the watchdog's 180-second
plan lead minus the driver's 120-second install-close margin. Rounding is to a
whole minute because the shared calendar requires it. An explicit later
whole-minute Unix epoch can replace this selection.

```zsh
export S="/Users/edr/night-align/r1-$(date -u +%Y%m%dT%H%M%SZ)"
export T0="$("$PY" -B -c 'import math,os,sys,time; sys.path.insert(0,os.environ["M"]); from scripts import run_night,magistrate_watchdog; print(60*math.ceil((time.time()+magistrate_watchdog.PLAN_LEAD_S+run_night.INSTALL_CLOSE_MARGIN_S+180)/60))')"
"$PY" -B "$M/scripts/arm_align_r1.py" prepare --measurement-root "$M" --custody-root "$S" --t0 "$T0"
cat "$S/arm.json"
"$PY" -B "$M/scripts/arm_align_r1.py" render --custody-root "$S" --output "$S/rendered"
plutil -p "$S/rendered/com.joulewise.night.plist"
plutil -p "$S/rendered/com.joulewise.night.deadman.plist"
```

`window_max_s = 105127` (29 h 12 min 7 s) is a ceiling, not a reservation:

| Term | Seconds | Source |
|---|---:|---|
| R1 with retries and corrected batch encounter | 96,427 | origin/main RUN_STATE items 215–216; replaces the stale runtime display |
| Hazard admission, inside the t0 deadline | 3,300 | `b5.plan.T0_STAGE_CAP_S` |
| Two diagnostic bookends | 3,600 | twice `b5.chain.STAGE_WALL_BUDGET_S.pre_calibration_capture` (1,800 each) |
| Bookend teardown/close allowances | 1,200 | twice the existing 600-second session-status budget; covers the budget helper's 30-second TERM grace and bounded process censuses/reap |
| Final R1 harvest/result writes | 600 | one existing session-status wall allowance |

Extra sustained-load redos can still reach this ceiling; it is not a promise
that every possible sequence of two redos per quiet segment will fit. The
outer driver also has its existing 300-second shutdown grace. Nothing changes
`night_worst_case_s` or its display test.

The two bookends are ordinary diagnostic D-109 fiducial observations. They
are **not a claim-eligible reserved W1 bracket**: R1 may exceed the existing
24-hour claim-bracket horizon. Failures/timeouts are recorded in
`bookends/{pre,post}.json` and do not veto the R1 chain. No W1 harvest runs.
The shared KM003C monitor also starts; it is a diagnostic and meter absence
does not veto R1. R1's v4 residual is GPU energy (item 212 R11-3).

The R1 sampler-span allowance is 5,764 seconds, the ceiling of the existing
`segment_bounds` maximum at the committed G0 timeout and step deadman. Clock
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
> Ceiling: 105,127 s after t0, plus the existing 300 s shutdown grace; it
> normally ends as soon as R1 completes. No agent session will remain at t0.
> Please keep the Mac on AC, not charging, with the external SSD unplugged;
> do not start agents or other work during collection. Security Responses
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
```

Exit the magistrate and every other agent session now. Do not run the driver
or `--dry-arm` from an agent tree as a live probe. LaunchAgent is the wake
source; the installed plists name the absolute `night_plan.json`, so the
watchdog's existing installed-plan fence sees this custody even outside its
usual scan directory. It suppresses relaunch during the plan span and while
an opened chain lacks `chain.exited`. An early daily dead-man fire on a
multi-day window returns before the completion epoch; the later fire handles
recovery. The supplied courier is the existing file-only `b6_courier.sh`,
which starts no agent and sends no email.

## 4. On return, preserve the result and uninstall

```zsh
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

## Scheduled jobs during R1 (item 202(4))

The scheduler's job name/time is not a trigger. Software Update (about
23:09/05:09/11:09/17:09), the midnight `/tmp` cleanup, trustkit's four-hourly
xx:31 task, XProtect around 05:40 and the 12:53 maintenance all have the same
load handling. Outside the explicit 11:45–13:15 start exclusion, R1 does not
pause a running quiet segment and wait for those jobs. It finishes that
attempt, then redoes it if background load exceeded 0.5 core for 60 consecutive
1 Hz samples. Heavy redos first release against the soak. Two redos are allowed;
contamination of all three attempts **refuses R1**. Missing/gappy load evidence
can also refuse; ordinary short contamination is recorded. A pure G0 timeout
has its separate INCONCLUSIVE/retry rule. The outer 5% contention monitor
journals the event; it does not turn a scheduled task into an immediate night
refusal. See `align_r1_rehearsal.py:869`, `:879`, `:980`, `:1050`, `:1273`
and `hazards/monitor.py:581`.
