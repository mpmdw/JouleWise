# Magistrate brief for measurement block 5

Written 2026-10-07 for the hand-off of measurement block 5 to the magistrate, from the pre-mortem of the
first window, the orchestrator's decisions on its questions, the seal gate's rulings and the sealed
registration. This file is `docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` on main, and the top block of
`RUN_STATE.md` points at it. A bracketed id such as `[HN-1]` names the pre-mortem finding that a sentence
cures (the findings are in `docs/process_traces/2026-10-07-block5-seal/premortem/PREMORTEM.md`); you do not need to read them to follow
this brief.

You are the **magistrate**: the headless Opus 5.5 session that the watchdog starts on this Mac. The
**watchdog** is a launchd job (`com.joulewise.magistrate`, one run every 300 s) that starts a session only when
no measurement window is in progress, and that asks, then forces, a session to exit before a window starts.
Each session it starts is one **activation**. This brief is your whole step list for block 5, and it stands
alone: nothing in it needs a person at the keyboard, and no step waits for an interactive session. Where it and
an older document differ, this brief wins, with two exceptions that always win over it: the sealed
registration, and Ed's word. (Ed is the owner. He reads email; he is not at the Mac.)

## 1. What block 5 is, in the words this brief uses

- A **member** is one measured model run. A **pack** is a fixed, committed set of experiment inputs. Block 5
  has three packs, run in this order: ALPHA (`d117_floor_qwen3-1p7b_v5`, 119 members), BETA
  (`d117_floor_qwen3-8b_v5`, 119 members), GAMMA (`d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`, 101 members).
- A **window** is one unattended measurement run of one pack, started by launchd at a planned time **t0**; its
  collection is expected to take 5 to 9 hours. An **attempt** is one window of a pack: ALPHA-1 is ALPHA's
  first attempt. A pack is attempted again, with the next attempt number, until one attempt is claim-usable
  (defined below); then the next pack starts. Block 5 needs one claim-usable attempt of each pack.
- A **plan** is the file `night_plan.json` that fixes one attempt: its t0, its directories, its thresholds.
  The directory that holds it is the attempt's **custody root**, `/Users/edr/night-custody/<plan id>/`. The
  watchdog finds plans only there. A plan's two **runs roots** are the directories where the members' measured
  data is written (the plan names them in `hazard_window.runs_roots`).
- The **measurement clone** is the one checkout every window of this block runs from:
  `/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5`. It is checked out at the **seal commit** `ab7b21e576a2d74f0b25d9a26b463d6934588368`, whose only parent is
  **H_claim** `a64000884ef5bb4b76415835f02f39803f6eb620`. H_claim is the last commit that changed a **window input**: a tracked file a
  window can read, which is every file under `joulewise/`, `scripts/` and `configs/`, and the one document
  `docs/phase_2/window_runbook.md`. The seal commit changes only the three **seal documents**
  (`sealed_inventory.json`, `registration_block5.md` and `analysis_plan_block5.md` in
  `configs/campaigns/v5_claim_25g83/`). The clone's interpreter is `/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5/.venv/bin/python`.
- The **desk root** is a second, separate clone, `/Users/edr/night-custody/desk/b5-harvest`, from which the
  harvest program runs (the harvest is the program that checks a finished window; it has its own entry
  below). It is never the measurement clone and never the **canonical root** `/Users/edr/code/JouleWise`,
  which is the checkout the watchdog and you run from.
- At t0 the **driver** (`scripts/run_night.py` in the clone, started by the launchd job `com.joulewise.night`)
  takes the **agent census** (it lists Claude and Codex processes and refuses the window if one is alive), then
  runs the **arm** (it measures six physical hazards directly: the clock, the battery, thermal pressure, a
  competing process, free disk, the power sampler; this takes 4 to 47 minutes), then starts the **chain** (the
  shell program that runs the members between two calibration captures). While the chain runs the driver
  repeats the census every 30 seconds and stops the chain if an agent process appears. A second launchd job,
  `com.joulewise.night.deadman`, is the fallback that stops what a dead driver left running.
- The **calibration ledger** is the append-only file `runs/calibration_observation_ledger.jsonl` in the clone.
  The **pin** is the committed file `configs/calibration/calibration_ledger_head.json`, which names the
  ledger's last row. Each window opens one **bracket session** in the ledger (its calibration before the
  members and its calibration after them). A finished window has moved the ledger past the pin, and no new
  plan can be written until the pin is advanced.
- The **harvest** is the desk program (`scripts/harvest_b5_window.py`, run from the desk root) that copies a
  finished window into an **archive root** (`/Users/edr/night-archive/harvest-<plan id>`), checks the window's
  bytes, and writes one **verdict** and one yes-or-no value, **claim_usable**. A window is **claim-usable**
  when no finding removes the whole window and every reported quantity keeps at least 5 of its 10 planned
  units of each kind (registration sections 0.16 and 6.6). The harvest also writes the **window reasons**
  (`exclude_window_reasons` in `harvest.json`): the reason codes that remove the whole window.
- The **seal record** is the file on main that lists the SHA-256 of every sealed file,
  `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`. A **harvest addendum** is a section appended to it that names the commit
  the desk root is checked out at and the SHA-256 of each harvest program file. The harvest program is
  **pinned** when such an addendum is in the canonical root's copy of the seal record, and you harvest only
  with a pinned program (section 4.5 has the test).
- The **courier** is a short `claude -p` session the driver starts when a window ends. It emails Ed the
  window's structural result and writes `night/courier.sent`. The watchdog starts you again once it sees the
  window's result record, `night/courier.sent`, and no agent or driver process. If `courier.sent` is absent
  because the courier could not send, the watchdog holds the machine until t0 + `window_max_s` + 4,800 s,
  about a day after the chain ended, and you learn of the window only then. `[M2]`
- **The login.** You and the courier both run under whichever Claude account is logged in on this Mac, and
  both send mail through that account's Gmail connector. Which account that is is Ed's business alone (Ed,
  2026-10-07: "dont trip about which account leave that to me"): no step of this brief waits on it, and you
  never ask him about it. What it means for you is the sentence above and nothing more: a courier that
  cannot send holds a finished window about a day, and the window's measured bytes do not depend on it.
  `[M1]`
- **Blinding.** From ALPHA-1's arm until the **release event** (the recorded step, after the block has closed,
  at which the measured values are first opened to the analysis), nobody reads or writes an energy, a power, a
  phase duration or anything derived from one. You work from **structure** only: verdict words,
  `claim_usable`, window reasons, member counts, paths, hashes, hazard measurements. A file that holds, or can
  quote, a measured value is **restricted**: until the release event only programs read it. Section 6 lists
  exactly what you may open.

## 2. Fixed values, and the one rule about shell variables

**Every Bash tool call starts a new shell.** A variable set in one call is empty in the next, and `cd ""`
returns 0 and stays in the canonical root, so a command block that relied on an earlier `export` would run in
the wrong directory with empty names. `[M5]` Therefore the block's fixed values are in a file, and every
command block in this brief begins by sourcing it:

```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh
```

The orchestrator wrote that file at the hand-off. It exports:

```zsh
MEASUREMENT_ROOT='/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5'
PY="$MEASUREMENT_ROOT/.venv/bin/python"
H_CLAIM='a64000884ef5bb4b76415835f02f39803f6eb620'                           # the commit every window is compared with
SEAL_HEAD='ab7b21e576a2d74f0b25d9a26b463d6934588368'                       # the clone's head before any pin advance
REG_SHA256='4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841'                     # SHA-256 of the sealed registration_block5.md
BENCH=/Users/edr/night-plan-staging/b5-bench      # the helpers named below
DESK_ROOT=/Users/edr/night-custody/desk/b5-harvest                            # the clone the harvest program runs from
HARVEST_ADDENDUM='/Users/edr/code/JouleWise/docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md'  # the file that holds the harvest addendum (4.5)
RECORDS_BRANCH=records/2026-10-block5             # your records
RECORDS_WT=/Users/edr/code/JouleWise-wt-b5-records                            # a linked worktree on that branch
ANSWERS="$BENCH/owner-answers.txt"                # Ed's answers (below)
NOTICE_TO='<not printed in this copy>'            # the owner's notice address (held in the local file b5-fixed-env.zsh, not in the repository);
                                                  # used only as the recipient of a Gmail message and in the search for his replies
```

The repository's copy of this brief does not print Ed's address. Wherever a step needs it, it is the value of
`NOTICE_TO` in that file: `source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; echo "$NOTICE_TO"` prints it.

**Ed's answers are a file, not sentences of this brief.** Five questions were put to Ed at the hand-off.
His answers are in `$ANSWERS`, one `name=value` line each, and each has a default that is in force until he
answers. The orchestrator wrote the file at the hand-off with what was known then. When an activation reads
a newer answer in Ed's mail, it rewrites that one line, says so in its record, and follows it from then on.
Read a value with `sed -n 's/^E-2a=//p' "$ANSWERS"`; a missing line or file means the default.

| Name | The question | Values | Default |
|---|---|---|---|
| `E-2a` | May you quit a desktop application you find open on this Mac (Claude, ChatGPT, T3 Code, Chrome, Firefox)? | `YES`, `NO` | `NO` |
| `E-2b` | May you end an interactive `claude` or `codex` session you did not start, after one email about it has gone unanswered for 30 minutes? | `YES`, `NO` | `NO` |
| `E-3` | Does a GitHub issue opened from this Mac reach him as a notification? | `YES`, `NO` | `NO` |
| `E-4` | The lead between the arm notice and t0, in seconds | a number of at least 1200 | `1800` |
| `E-6` | Should the arm notice offer him a command that releases the Mac by hand when no result email arrives? | `YES`, `NO` | `NO` |

A window's own values (its plan id, t0, directories) are written by section 5.2 into
`/Users/edr/night-plan-staging/<plan id>/arm-env.zsh`. The fixed-values file sources that file too when the
variable `P` holds a plan id, so a block that works on one window begins:

```zsh
P='<the plan id, typed out>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}" "${MEASUREMENT_ROOT:?}"
```

The last command stops the block if either value is empty. In the blocks below, `$C` means `$CUSTODY`, the
window's custody root, and `$STAGE` is the window's staging directory
`/Users/edr/night-plan-staging/<plan id>/`, which holds your working files for that window and is outside
every directory a window or a harvest reads.

Helper digests (check before first use, `cd "$BENCH" && shasum -a 256 *.py *.sh`): `b5_plan_inputs.py`
`f77f60c16e2122e1aa0cfe1ef2eb47fb88808e969cc8f5c7319766d664420f3b`, `b5_desk_identity.py`
`6c46fab80ed8f6d9b1d57949211a8197f70dd510e4559eeeb6415ab44dea48cf`, `b5_desk_seal_check.sh`
`c609714cb3eb745e474870295fe47b93f040e2a46d7bfd5f126e5d32fac5b381`, `b5_agent_check.py`
`5d6fac1279430998cc3219a73d4a02914479443a342ebe594ad01c364d14080d`. (These are the digests of the four
files as the pre-mortem left them on 2026-10-07; the orchestrator's runbook compared the installed copies
with them.) A helper whose digest differs is not used: restore it from `docs/process_traces/2026-10-07-block5-seal/bench/` in the
canonical root, which holds the same four files. Sealed registration:
`configs/campaigns/v5_claim_25g83/registration_block5.md` in the clone.

## 3. Every activation: find the state, then do the first thing that applies

Read the state from the disk, not from memory or from an earlier record:

```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh
ls /Users/edr/night-custody/magistrate/standdown.request 2>/dev/null                  # the watchdog wants this session gone
ls -1 /Users/edr/night-custody | grep '^v5-b5-' | sort -t- -k5                         # every attempt of this block, oldest t0 first
launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}'                     # jobs of an armed or unharvested window
pgrep -lf '[r]un_night\.py'                                                          # a driver that is still running
find /Users/edr/night-archive -maxdepth 2 -path '*/harvest-v5-b5-*/harvest.json'      # harvests that finished
find /Users/edr/night-plan-staging -maxdepth 2 -name harvest-deferred                 # refused windows whose harvest waits (4.5, variant B)
grep -m1 '^B5-ARM-RELEASED:' /Users/edr/code/JouleWise/RUN_STATE.md                   # the packs you may arm
cat "$ANSWERS" 2>/dev/null                                                           # Ed's answers (section 2); absent lines mean the defaults
```

The third line of the block orders the attempts by the start time at the end of each plan id, so its last line is the
newest attempt. (Plain `sort` orders by pack name first, and would call a GAMMA attempt newer than an ALPHA
attempt armed after it.) `[HN-5]`

If `standdown.request` exists, exit at once. Otherwise, for the newest plan id `P` with custody
`C=/Users/edr/night-custody/$P`:

1. **A window is armed or running:** `C/night/chain.started` exists and `C/night/chain.exited` does not, or a
   driver process is alive, or t0 is still ahead and the two jobs are loaded. Write nothing. If t0 is still
   ahead, search Gmail once for unread mail from Ed: the query is `from:<address> is:unread`, where `<address>` is
   the owner's notice address (held in the local file b5-fixed-env.zsh, not in the repository), the
   value of `NOTICE_TO` (section 2). A NO to this plan's notice is
   section 5.6, which this brief authorizes any activation to do, whichever activation wrote the plan.
   Otherwise exit within one minute, with no email and no record. `[C5, M7]` (Between an arm and t0 − 180 s
   the watchdog starts a new activation about every ten minutes. Each one lands here.)
2. **A window has ended and is not harvested:** `C/night/result.json` exists, the `find` line shows no
   `harvest-$P*/harvest.json`, and there is no file `/Users/edr/night-plan-staging/$P/harvest-deferred`. Do
   section 4, in order. A directory `harvest-$P…` without a `harvest.json` is a harvest that was cut short:
   leave it as it is; it does not count as a harvest. `[M8]`
3. **A plan was written and its window never started.** Two shapes, same cure. `[PD-3]` (a) t0 is ahead and
   the two jobs are not loaded: an arm was given up between the plan and the install. (b) t0 + 20 minutes has
   passed, no `run_night.py` process is alive, and `C/night` holds neither `result.json` nor `censuses.jsonl`:
   launchd never started the driver, or it died before its first record. Withdraw the plan by section 5.6
   (uninstall first, then move the custody), record it, and go on to case 4 with the same pack and
   `ATTEMPT` + 1. Do (b) promptly: the watchdog released this plan only because `C/night` was empty, and the
   dead-man job's next daily start writes two log files there, after which the watchdog fences the machine
   again for more than a day.
4. **No attempt is armed or unharvested, and the block is not closed:** arm the next attempt (section 5).
   Which one: section 6. Two conditions hold the arm, and both are read from the disk:
   - the pack must be named on the `B5-ARM-RELEASED:` line of the canonical root's `RUN_STATE.md`. If it is
     not, the pack is held until the harvest program is pinned: do what section 4.5, variant B, says. That
     variant ends by rewriting the line, so the hold never needs a person. `[M14]`
   - **never arm past a window that lacks its verdict.** The previous attempt that started a chain must have
     its verdict file, `<its claim runs root>/whole-window-verdict.json` (the claim runs root is
     `hazard_window.runs_roots.claim` in its plan; test that the file exists, do not open it). The one
     exception is an attempt that can have no verdict: its harvest verdict is NULL or NO_COLLECTION, or its
     bracket session was aborted in 4.2. Section 4.5 says why. `[HN-1]`
5. **GAMMA has a claim-usable attempt, or the block reached END STATE:** the block is closed. Section 7.

If the two launchd jobs are loaded and none of the above explains them, treat it as case 2 for the plan the
job names (`plutil -p ~/Library/LaunchAgents/com.joulewise.night.plist`).

## 4. After a window: close it, then harvest, then everything else

The order is fixed, and the next attempt is armed only after the harvest of 4.5 has finished. There are two
reasons. *The arm:* the harvest uses about 14 processes for 25 minutes, and the next arm measures competing
processes for at least 180 s after its t0; a harvest still running at that t0 is a competing process, and the
arm refuses. *The ledger:* the next window's reservation appends a new bracket session to the ledger, and
once a later session follows a window's session no command in this brief can write that window's verdict any
more (4.5).

Each block below starts with
`P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"`.

**4.1 Confirm the window is over.** `test -f "$C/night/result.json"`; `pgrep -lf '[r]un_night\.py'` prints
nothing; `pgrep -fl "$C"` prints nothing (a line that is only the shell running this very command does not
count). Read `verdict`, `stage_reached`, `refusal`, `yield` and `faults` from `$C/night/hazard_result.json`
(structure only). Do not open the chain's logs, `night.log`, `night/transcript/`, `operator-logs/`, the runs
roots or anything under `hazards/` or `flags/`, with one exception: the arm record `hazards/arm.json`, which
section 6 lists among what you may open. The registration's custody map (its section 8) restricts the
logs, the runs roots and the battery and meter records under `hazards/`; the orchestrator's decision O-7
(section 6 of this brief) is narrower than the map and keeps you out of the rest as well.

- The driver's yield and the courier's email count *planned* members by their final status. A `LOW` on a
  reference stage may have been made good by spare members, which the driver does not count, and `FULL` says
  nothing about members that ran and will be excluded at the harvest. Decide only from the harvest. `[WR-4]`
- **The dead-man job fires once inside every window, and that is not a fault.** Its launchd calendar has an
  hour and a minute and no date, so launchd starts it once a day, and for a window this long the first start
  falls inside the chain, at about t0 + 5 h 28 min for ALPHA, 6 h 08 min for BETA and 2 h 22 min for GAMMA.
  The job sees that the window is not over and exits after about 0.15 s. Record the job's hour and minute in
  the window record, so the analysis can name the member it fell in: read them before the uninstall of 4.4
  with `plutil -p ~/Library/LaunchAgents/com.joulewise.night.deadman.plist | grep -A3 StartCalendarInterval`.
  (The line the job writes is in `night.log`, which you do not open.) `[PD-1]`

**4.2 Close an open bracket session, if there is one.** A chain that stopped before its closing calibration
leaves its session open, and then neither the pin advance nor the next plan can proceed.

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"; cd "$MEASUREMENT_ROOT" || exit 3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c 'import json; from pathlib import Path; from joulewise.b5 import plan; print(json.dumps(plan.ledger_head_status(Path(".").resolve()), indent=1, sort_keys=True))'
grep '^FROZEN_PLAN=' "$C/window.env"
```

If `open_sessions` names `$P-calibration`, take the pack's frozen calibration plan from the `FROZEN_PLAN=` line
(it is `<pack root>/calibration_plan.json`, the file the chain's reservation opened the session with). Then,
when `open_session_next_slots` shows `custody_state` `complete`, run
`"$PY" -B scripts/recover_calibration_ledger.py resume-finalize --session-id "$P-calibration" --slot <that slot> --plan <FROZEN_PLAN>`;
otherwise run
`"$PY" -B scripts/recover_calibration_ledger.py abort-session --session-id "$P-calibration" --plan <FROZEN_PLAN> --reason "block 5: chain stopped before the post calibration"`.
A window whose arm refused opened no session; skip this step.

**4.3 Advance the pin.** This is the only kind of commit the clone ever receives.

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"; cd "$MEASUREMENT_ROOT" || exit 3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/advance_b5_ledger_pin.py --plan "$PLAN" --operator-identity "magistrate-$(date -u +%Y%m%dT%H%MZ)"
git diff --name-only "$SEAL_HEAD" HEAD        # must print only configs/calibration/calibration_ledger_head.json, or nothing
```

Exit 0 with `"status": "ADVANCED"` or `"NOT_NEEDED"`. Exit 2 `REFUSED`: read `detail`; an open session is 4.2.

**4.4 Remove the window's two launchd jobs.** Before the harvest, not after it. `[HN-2]`

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"
pgrep -fl "$C"                                                        # must print nothing
plutil -p ~/Library/LaunchAgents/com.joulewise.night.deadman.plist 2>/dev/null | grep -A3 StartCalendarInterval   # 4.1: record the hour and minute
if [ -n "$(ls ~/Library/LaunchAgents | grep com.joulewise.night)" ]; then "$MEASUREMENT_ROOT/scripts/install_night_agent.sh" --uninstall --plan "$PLAN"; echo "uninstall rc=$?"; fi
launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}'     # must print nothing
ls ~/Library/LaunchAgents | grep com.joulewise.night                 # must print nothing
```

*Why before the harvest:* each daily firing of the dead-man job appends a line to `$C/night.log`. The harvest
hashes the whole custody root when it archives it and again at its end, and a file that changed in between is
the code `records.source_changed_during_harvest`, which removes the window from the claims until a second
harvest (about 45 more minutes). *Why it cannot be skipped:* the installer refuses the next plan while either
label is loaded. The uninstall checks no plan head, so it works after the pin advance. If an uninstall does
not exit 0 and a job file remains, retry once and then send the fault email (section 5.6 says why nobody else
would).

**4.5 Harvest.** The registration (section 11 item 4) lets a harvest run only after the harvest program has
been pinned by a harvest addendum to the seal record (section 1 defines the three terms). An addendum
carries one line that a program can find: it starts in the first column and reads `B5-HARVEST-PIN: `
followed by the 40-character name of the commit the desk root is checked out at. The harvest program is
pinned when that line is in the canonical root's copy of the seal record. One test on the disk says whether
that is so, and it chooses between the two variants below. Run it before every harvest. `[M14, SC-2]`

```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh
DESK_HEAD="$(git -C "$DESK_ROOT" rev-parse HEAD 2>/dev/null)"
if test -n "$DESK_HEAD" && test -f "$HARVEST_ADDENDUM" && grep -q "^B5-HARVEST-PIN: $DESK_HEAD\$" "$HARVEST_ADDENDUM" \
   && git -C "$DESK_ROOT" merge-base --is-ancestor "$H_CLAIM" HEAD \
   && test -z "$(git -C "$DESK_ROOT" status --porcelain=v1 --untracked-files=all)"; then echo HARVEST_PINNED; else echo HARVEST_HELD; fi
echo "desk root at: ${DESK_HEAD:-there is no desk root}"
```

It prints `HARVEST_PINNED` when the file that holds the addendum exists in the canonical root and its pin
line names the commit the desk root is checked out at. The two further conditions guard the desk root
itself: its commit descends from H_claim, and it has no uncommitted file. *Why the commit matters:* a
harvest program older than the seal-landing change reports a correct window as
`code.executed_differs_from_sealed`, and before the pinned program nothing in a harvest's outputs recorded
which program produced them.

---

**Variant A, harvest at once (`HARVEST_PINNED`). This is the default**, and the state the hand-off leaves
when the addendum was on main before ALPHA-1's arm (the `B5-ARM-RELEASED:` line then reads
`alpha beta gamma`): every window is harvested as soon as steps 4.1 to 4.4 are done.

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"
pgrep -fl 'run_campaign.py --whole-window-verdict'       # must print nothing; see below
ARCH="/Users/edr/night-archive/harvest-$P"               # a re-harvest, or a retry after a cut-short one: harvest-$P-r2, then -r3
test ! -e "$ARCH" && PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$DESK_ROOT/scripts/harvest_b5_window.py" --plan "$PLAN" --archive-root "$ARCH" --prepare-desk > "$STAGE/harvest.stdout" 2> "$STAGE/harvest.stderr"; echo "harvest rc=$?" >> "$STAGE/harvest.stdout"
```

Then read the result, with this block and no other:

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"
ARCH="$(find /Users/edr/night-archive -maxdepth 1 -name "harvest-$P*" | sort | tail -1)"; echo "archive: $ARCH"
tail -1 "$STAGE/harvest.stdout"                                                                # the line "harvest rc=<n>"
sed -E -n '1s/^(verdict=[A-Z_]+)( reason=[A-Za-z_.]+)?.*/\1\2/p' "$STAGE/harvest.stdout"       # the verdict word, and an error's type
if test -f "$ARCH/harvest.json"; then
  python3 -c 'import json, sys
h = json.load(open(sys.argv[1]))
keys = ("plan_id", "attempt", "pack_id", "verdict", "claim_usable", "exclude_window_reasons", "yield", "faults", "harvest_checkout")
print(json.dumps({k: h.get(k) for k in keys}, indent=1, sort_keys=True))' "$ARCH/harvest.json"
  shasum -a 256 "$ARCH/harvest.json"
else
  echo "no harvest.json in the newest archive directory: the harvest wrote no record"
fi
git -C "$DESK_ROOT" rev-parse HEAD                                                              # must equal harvest_checkout.head
```

- **Run the harvest as a background task and wait for it.** Start the harvest block with the Bash tool's
  background option and do not end your turn until it has exited. A foreground command is ended by the tool
  after at most ten minutes, and a harvest of ALPHA or BETA takes about 40 to 45 minutes on a quiet machine:
  about 14 processes for the first 25 minutes, mostly one core after; the verdict writer's own limit is 2.7
  hours. `[M8, HN-4]`
- **A harvest that was killed leaves its verdict writer running.** The harvest starts the writer
  (`run_campaign.py --whole-window-verdict`, the clone's own program) in a session of its own, so whatever
  ends the harvest does not reach it; it runs on for up to about 20 minutes, holds a lock in the claim runs
  root, and then writes the verdict. A second harvest started meanwhile collides with it and records the
  window as excluded. So the `pgrep` line must print nothing before any harvest, first or repeated. If it
  lists a process, wait for it to exit. Do not signal it: it is writing the window's one verdict. `[HN-3]`
- **Read nothing else of the harvest's output.** Do not print the rest of `harvest.stdout` and do not open
  `harvest.stderr`: when the verdict is HARVEST_FAULT they quote an error text, which can quote a data value,
  and the custody map restricts it. The `sed` line keeps only the verdict word and the error's type.
- Exit codes: 0 a verdict; 2 a harvest fault recorded in `harvest.json`; 3 the harvest stopped on an error
  before a record, or its inputs could not be resolved, or the archive root exists; 4 not ready (the chain's
  processes are alive or the result record is absent: go back to 4.1); 6 members were planned and none is
  present. Never pass an existing directory as `--archive-root`.
- `harvest_checkout.head` must equal the desk root's commit, and `harvest_checkout.status_clean` must be
  `true`. If either differs, the harvest ran from a program the addendum does not pin: do not decide from it;
  put the desk root right (section 9) and harvest again into `-r2`.
- The window reason list never contains `whole_window.verdict_unauthenticated`: that code is recorded on every
  harvest, is disclosed only, and is not a reason for anything. `[HN-4]`
- **A window whose session is no longer the newest in the ledger must not be harvested from the live
  ledger.** `[HN-1]` The function that finds a session's last ledger row refuses as soon as any row of a later
  session follows it, and the next window's reservation is such a row. A harvest of the earlier window then
  records `calibration.no_bracket` (it removes the window) and starts no verdict writer, and the pin advance
  cannot name the earlier session either. Two rules follow. (1) Never arm the next window before this one has
  its verdict file (section 3 case 4). (2) A re-harvest of a window that is not the newest in the ledger adds
  `--ledger-path "<its first archive>/sources/ledger/calibration_observation_ledger.jsonl" --head-pin-path "<its first archive>/sources/ledger/calibration_ledger_head.json"`,
  the copies the first harvest took (pass the paths; do not open the files). And a re-harvest of a window that
  ran before a re-issued seal (section 9) adds
  `--sealed-inventory-path "<its first archive>/sources/inputs/sealed_inventory.json"`.

---

**Variant B, hold for the desk session (`HARVEST_HELD`). The fallback.** It applies only when the hand-off
released ALPHA before the harvest program was pinned (the orchestrator's decision O-4: the arm does not wait
for the harvest lane); the `B5-ARM-RELEASED:` line then reads `alpha`. Steps 4.1 to 4.4 are done. **Do not
harvest with a program that is not pinned.** The **desk session** is the piece of work that pins it: it
finishes the gates of the **harvest lane** (the branch `lane/2026-10-07-harvest-lane`, which carries the
harvest changes the seal gate required; its work-list and notes are in
`/Users/edr/night-archive/gate-prune/wave-1007b/harvest-lane/`, and the RUN_STATE top block says which of
its gates had passed at the hand-off), checks the desk root out at the lane's head, and puts the addendum on
main. It is a piece of work, not a person's turn: if nobody else is doing it, you do. What you do depends on
two facts on the disk.

- **The window never started a chain** (no `$C/night/chain.started`: the census or the arm refused). It
  collected nothing and opened no bracket session, so the ledger rule of this section does not bind it, and
  waiting would cost a day for nothing. Mark it and go on:
  `P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"; date -u +%Y%m%dT%H%MZ > "$STAGE/harvest-deferred"`.
  Treat the window as the `verdict=NULL` row of section 6, reading the refusing hazard from
  `night/hazard_result.json`, and arm the same pack again. The marker file is in the staging directory, never
  in the custody root, which the harvest will hash.
- **The window started a chain** (`$C/night/chain.started` exists). Do not arm. Run the agent check of 5.1.
  - *If `foreign_agents` lists an interactive session* (a `claude` or `codex` process with a terminal): a
    desk session is at work on this Mac and the pin is its job. Exit quietly (no email: the courier has
    already reported the window; no record; no commit). The watchdog starts another activation every five
    to ten minutes, and each repeats this test.
  - *Otherwise the desk session is yours, now.* No window is running and none can be armed, so the machine
    is free for desk work. In order:
    1. Finish the lane's missing gates by section 9's route for code that does not run during a window: an
       independent executing review, a cold Fable 5.1 pass (the harvest is on the path to a claim), every
       finding dispositioned, the lane's tests. The lane's head must descend from H_claim, and
       `git diff --name-only "$H_CLAIM" <lane head>` must list only `joulewise/b5/harvest.py`,
       `joulewise/whole_window.py`, `scripts/harvest_b5_window.py` and paths under `tests/` (registration
       section 11 item 4 permits nothing else).
    2. Check the desk root out at that head. If `$DESK_ROOT` does not exist:
       `git clone -q --no-hardlinks https://github.com/mpmdw/JouleWise "$DESK_ROOT"`. Then
       `git -C "$DESK_ROOT" fetch -q origin && git -C "$DESK_ROOT" checkout -q --detach <lane head>`.
    3. In the records worktree, append the addendum to the seal record: the line
       `B5-HARVEST-PIN: <lane head>`, the SHA-256 of each of the three harvest program files at that head,
       and the paths of the review and of the cold pass. In the same commit change the RUN_STATE line to
       `B5-ARM-RELEASED: alpha beta gamma`. The commit changes documents only; push it to main
       (`git push origin HEAD:main`, after `git fetch origin main` and a rebase onto it). If GitHub refuses
       a direct push, open a light-tier pull request for it and merge it with `gh pr merge --merge`. Then
       run `git -C /Users/edr/code/JouleWise pull --ff-only` (allowed here: no night job is loaded after
       4.4 and no plan is armed).
    4. Run the test again. It prints `HARVEST_PINNED`; harvest by variant A.
    Every seat you brief for this carries the blinding paragraph of section 6, and none of them, and not
    you, has read a claim-window energy: the registration requires that of whoever writes an addendum. If
    an activation ends before the four steps are done, leave the note that section 10's last rule asks for.
- **Catching up.** At the first activation where the test prints `HARVEST_PINNED`, harvest every attempt that
  has a `harvest-deferred` marker and no `harvest.json`, oldest first, by variant A, before anything else, and
  delete each marker when its `harvest.json` exists. Each is a window with no members and takes minutes.

Never move the desk root to a commit that has not passed those gates, and never harvest from another
checkout.

---

**4.6 Record.** In the records worktree `$RECORDS_WT` (never the canonical root, never the clone, never the
desk root): the plan id, the fields the reading block printed, `harvest.json`'s SHA-256, the pin commit's sha,
the uninstall's return code, the desk root's commit, and the dead-man job's hour and minute from 4.1. Paths,
hashes, codes and counts only. Commit and push `$RECORDS_BRANCH`. Do not wait for a merge.

**4.7 Decide** by section 6, then arm (section 5) or close (section 7).

## 5. Arming one attempt

Do the steps in order. A check that fails stops this arm; a cause you can fix is fixed and the arm is
repeated with a new t0. Nothing here is ever a reason to stop and wait for a person, with the one exception of
5.1's first check.

**5.1 Before writing anything.**

```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
/usr/bin/pgrep -a -lf '[c]odex|[c]laude' | PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_agent_check.py"; echo "agent check rc=$?"
ps -axo pid=,comm= | grep -iE '/(Claude|ChatGPT|T3 Code[^/]*|Google Chrome)\.app/'      # must print nothing
pgrep -lx firefox                                                                      # a browser: see below
test -z "$(git status --porcelain=v1 --untracked-files=all)" && echo "clone clean"
git diff --name-only --no-renames "$H_CLAIM" HEAD      # the three seal documents; after the first window also the ledger pin; nothing else
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c 'from pathlib import Path; from joulewise.b5 import plan; s=plan.ledger_head_status(Path(".").resolve()); print(s["blocking"], s["open_sessions"]); assert not s["blocking"]'
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c 'import json; from joulewise.hazards import clock; f=clock.read_frequency(); print(json.dumps(clock.frequency_bound(f["raw_word"], clock.DEFAULT_THRESHOLDS)))'
df -g /Users/edr | tail -1
test "$(sw_vers -buildVersion)" = 25G83 && echo "build 25G83"
```

- **The agent check** lists what the window's census would count after you are gone. `own_session_pid` is
  you; you and your MCP servers end when you exit. `foreign_agents` are agent processes outside your session:
  another Claude or Codex session, an application's helper, a seat that was started in its own session.
  `own_seats_still_running` are seats you started that are still alive. **Write no plan while
  `foreign_agents` is not empty.** `[C1, C2, M4]` *Why this is the one check that may hold an arm:* a window
  whose first census finds such a process refuses with no chain, and afterwards the watchdog starts no
  activation while that process lives, for up to t0 + `window_max_s` + 300 s (28 h 28 min for ALPHA). A plan
  that is never written costs nothing. What to do with a listed process, by its kind:
  - *A seat an activation of yours started* (a `codex` or `claude -p` process with no terminal): end it
    (SIGTERM, then SIGKILL after 20 s), record its pid, executable and start time, and run the check again.
  - *A desktop application* (the second line of the block names it, or the agent check shows a helper under
    `/Applications/…` or `~/Library/Application Support/Claude/`). Read Ed's answer `E-2a` (section 2).
    If it is `YES`: quit the application by its main process (`pkill -x Claude`, `pkill -x ChatGPT`,
    `pkill -x "Google Chrome"`), record it, and check again; the census cannot see an application's main
    process, only the helpers it starts, so quit the application, not the helper. `[C3]`
    If it is `NO`, or there is no answer: treat it as the next kind.
  - *An interactive session in a terminal* (a `claude` or `codex` process with a terminal), or an
    application you may not quit. It is not yours to signal. Write no plan. On first seeing it, append one
    line (the time and the pids) to `$BENCH/foreign-agents.log` and exit quietly. The next activation, about
    ten minutes later, repeats the check. The third consecutive activation that finds the same pid sends Ed
    one email (subject `ACTION NEEDED: a session is open on the measurement Mac`, the pid, what it is, how
    long it has been seen, and the one thing to do: close it) and notes in the log that it did; no later
    activation emails again for that pid. Then read Ed's answer `E-2b`. If it is `YES`: the first
    activation that finds the log's email note at least 30 minutes old, with no reply from Ed and the pid
    still alive, ends the session (SIGTERM to its pid), records it, and checks again. If it is `NO`, or
    there is no answer: keep exiting quietly until the process is gone. This is the one place where the
    block waits for a person, and it waits because the process is his.
- **The application line** must print nothing: opened, each of those four applications starts an agent
  process of its own.
- **The browser line** never holds an arm. Firefox is not an agent, and the window does not refuse on it;
  but a browser in use exceeds the window's contention limit and removes the members it overlaps. If the line
  prints a process and Ed's answer `E-2a` is `YES`, quit it (`pkill -x firefox`) and record it; otherwise
  arm, and say in the arm notice that a browser is open. `[AH-3]`
- **The clone lines.** `clone clean` must print, and the `diff` must list nothing beyond the three seal
  documents and, after the first window, the ledger pin. Any other path is a change to something a window
  reads: do not arm; section 9. `[PD-6, SC-3]`
- The ledger line must print `[] []`. Otherwise section 4.2 or 4.3 is unfinished.
- The clock line prints `"passes": true` or `false`. If false, the arm would refuse: do the **frequency
  redraw** of registration section 3 first (`sudo -n /usr/sbin/systemsetup -setusingnetworktime on`; read the
  line above once a minute; `… -setusingnetworktime off` at the first reading, at least 60 s after ON, that
  passes, or after 15 minutes; read again 10 minutes later; at most three cycles, then a consult).
- **Free disk** (the fourth column of `df -g`, in GiB) must be at least 88 for ALPHA and BETA and 78 for
  GAMMA. The arm's rule is three copies of the window's planned bytes plus 20 GiB on this volume, and each
  collected window keeps about 22 GiB, so the number falls by about 22 with every window: from a free space F
  before ALPHA, BETA arms only if F ≥ 110 and GAMMA only if F ≥ 122, and each repeated attempt needs 22 more.
  `[CE-4, AH-5, PD-4]` **Make no backup copy of a window during the block** (`scripts/backup_runs.sh` is not
  run): the backup folder is on the same volume and two copies per window do not fit. If the number is too
  low:
  1. First delete data that can be made again: scratch directories under `/private/tmp` (nothing the block
     reads is there) and the worktrees of merged lanes (`git worktree remove <path>`, run from the canonical
     root). A deletion returns space at once; read `df` again.
  2. Only then move data to iCloud by the 2026-10-05 offload method
     (`/Users/edr/night-archive/icloud-offload-2026-10-05/`). The folder is on the same volume, so an offload
     returns space only after iCloud has uploaded and evicted the files: on 2026-10-05 the first space came
     back after about 50 minutes and the last after about 2.5 hours.
  3. **Never delete, move or offload** `[CE-5, SC-6, SC-8]`: any block-5 custody root, runs root
     (`/Users/edr/night-b5/`) or harvest archive; the measurement clone; the desk root; the two archives the
     identity pins were derived from (`/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2`,
     `/Users/edr/night-archive/gate-prune/rehearsal-real`); the places the ledger's older captures live, which
     every harvest re-reads (the six custody roots
     `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919`, `-n2-20260919`, `-w1-20260927`,
     `-w2-20260927`, `d079-epoch-25g83-r6-derivation-c1-20261001T0617Z`, `-c2-20261001T2252Z`;
     `/Users/edr/night-g2a/`; the iCloud Drive folder `JouleWise-backup`); and the three model directories
     the block loads, under `/Users/edr/jw_models/mlx-community/`: `Qwen3-1.7B-4bit`, `Qwen3-8B-4bit`,
     `Qwen2.5-1.5B-Instruct-4bit`.

Then the one check of the reference model. `[CE-2, SC-6]` The model `Qwen2.5-1.5B-Instruct-4bit` is loaded in
every window, and no check at the arm hashes it (the arm's collectors hash only the pack's own models):

```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
SCRATCH="/private/tmp/b5-pins-check-$(date +%s)"; mkdir -p "$SCRATCH"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/write_b5_identity_pins.py --repo "$MEASUREMENT_ROOT" --runtime-python "$PY" --hash-local-models --out "$SCRATCH/identity_pins.regenerated.json" > /dev/null; echo "generator rc=$?"
python3 -c 'import json, sys
new, sealed = (json.load(open(p)) for p in sys.argv[1:3])
for doc in (new, sealed):
    doc["sources"]["runtime_probe"].pop("python")     # the probed interpreter path: differs for every clone
for key in ("units", "runtime_versions", "runtime_versions_sha256", "sources"):
    assert new[key] == sealed[key], key + " differs from the sealed pins"
print("equal to the sealed pins:", sorted(new["units"]))' "$SCRATCH/identity_pins.regenerated.json" configs/campaigns/v5_claim_25g83/identity_pins.json
```

It takes about 3 s and must print `generator rc=0` and `equal to the sealed pins:` with nine names. A failure
means a model directory or the interpreter is no longer the sealed one: do not arm; section 9. Never cure it
by writing a new `identity_pins.json` into the clone.

**5.2 Names and t0.** This block chooses the window's values and writes them, as literals, into the file
that later blocks source.

```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh
PACK=alpha; ATTEMPT=1                # PACK is alpha, beta or gamma; ATTEMPT is this pack's attempt number (section 6)
LEAD_S="$(sed -n 's/^E-4=//p' "$ANSWERS" 2>/dev/null | tail -1)"       # Ed's answer E-4 (section 2)
case "$LEAD_S" in ''|*[!0-9]*) LEAD_S=1800;; esac; [ "$LEAD_S" -ge 1200 ] || LEAD_S=1800   # the default is 1800 s; never below 1200
T0_EPOCH_S=$(( ( ( $(date +%s) + LEAD_S ) / 60 + 1 ) * 60 ))
T0_UTC="$(TZ=UTC date -r "$T0_EPOCH_S" +%Y%m%dT%H%MZ)"
PLAN_ID="v5-b5-$PACK-a$ATTEMPT-$T0_UTC"
CUSTODY="/Users/edr/night-custody/$PLAN_ID"; RUNS_PARENT="/Users/edr/night-b5/$PLAN_ID"; STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
BACKUP="/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/$PLAN_ID"
for p in "$CUSTODY" "$RUNS_PARENT" "$STAGE"; do [ ! -e "$p" ] || { echo "already exists: $p"; exit 3; }; done
G10=$( [ -z "$(find /Users/edr/night-custody -maxdepth 3 -path '*/v5-b5-*/night/g10.json' -print -quit)" ] && echo true || echo false )
mkdir -p "$RUNS_PARENT" "$STAGE"
cat > "$STAGE/arm-env.zsh" <<EOF
export PACK='$PACK' ATTEMPT='$ATTEMPT' G10='$G10' T0_EPOCH_S='$T0_EPOCH_S' T0_UTC='$T0_UTC'
export PLAN_ID='$PLAN_ID' CUSTODY='$CUSTODY' C='$CUSTODY' RUNS_PARENT='$RUNS_PARENT' STAGE='$STAGE'
export BACKUP='$BACKUP' PLAN='$CUSTODY/night_plan.json'
EOF
cat "$STAGE/arm-env.zsh"; echo "PLAN ID: $PLAN_ID"
```

Note the plan id it prints: every later block of this arm, and section 4 after the window, begins with
`P='<that plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh`. Do not run this block a
second time for the same arm: it would compute a new t0 and a new plan id. `G10` asks the driver to run the
clock control at the window's tail; it is `true` until one window of this block has left a `night/g10.json`.
`BACKUP` is only a pair of paths the plan must name; nothing is copied there during the block. Every attempt
gets a new plan id, a new custody root and new runs roots; nothing of an earlier attempt is reused.

**5.3 Desk files, plan inputs, plan, checks.**

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"; cd "$MEASUREMENT_ROOT" || exit 3
find configs/campaigns \( -name .DS_Store -o -name __pycache__ \) -print -prune -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_desk_identity.py" --measurement-root "$MEASUREMENT_ROOT" --stage-dir "$STAGE"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_plan_inputs.py" --measurement-root "$MEASUREMENT_ROOT" --pack "$PACK" \
  --plan-id "$PLAN_ID" --attempt "$ATTEMPT" --t0-epoch-s "$T0_EPOCH_S" --g10 "$G10" --stage-dir "$STAGE" \
  --custody-root "$CUSTODY" --runs-parent "$RUNS_PARENT" --claim-backup "$BACKUP/claim" --bound-backup "$BACKUP/bound" \
  --registration-sha256 "$REG_SHA256" | tee "$STAGE/inputs-summary.json"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/write_b5_window_plan.py --inputs "$STAGE/plan-inputs.json" | tee "$STAGE/plan-record.json"
python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); a=r["thresholds_audit"]; assert r["status"]=="STAGED" and not a["differences_from_defaults"] and not r["pack_digest_error"], r' "$STAGE/plan-record.json"
/bin/zsh -n "$CUSTODY/chain.zsh" && ( cd "$CUSTODY" && shasum -a 256 -c chain.zsh.sha256 )
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_b5_chain.py --plan "$PLAN" > "$STAGE/chain-check.json"; echo "rc=$?"     # 0
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/run_night.py preflight --plan "$PLAN"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/run_night.py schedule --plan "$PLAN" | tee "$STAGE/schedule.json"
/bin/zsh "$BENCH/b5_desk_seal_check.sh" "$MEASUREMENT_ROOT" "$H_CLAIM" "$PLAN" "$STAGE/desk-seal-check"; echo "desk seal check rc=$?"
```

- The `find` line removes two kinds of stray entry from the pack directories: `.DS_Store` (the Finder writes
  it when a folder is opened) and `__pycache__`. Git ignores both, so the clean-tree test of 5.1 cannot see
  them, but the arm's pack check walks the directory on disk and records any entry git does not track as
  `pack.identity_mismatch`, which removes the window. `[SC-7]` If the session's permission check refuses the
  command, skip it: the desk seal check below reports such an entry, and it is then removed by name.
- `b5_desk_identity.py` printing `"status": "REFUSED"` means this machine's identity (operating-system build,
  powermetrics binary, MLX version, power policy) is no longer the one the calibration acceptance was derived
  on. Do not arm. That is a fault email to Ed (section 8): an operating-system change supersedes the block
  (registration section 7.5).
- The plan writer printing `{"status": "REFUSED", …}` (exit 2) wrote nothing; `detail` names the cure.
- **The desk seal check** must print `no flag: …` and `desk seal check rc=0`. `[SC-3, CE-2, PD-6, SC-6]`
  *What it is for:* at the arm the driver compares the clone with the plan's own head, which is the clone's
  head, so the arm compares the clone with itself; and the arm records an identity defect and goes on. The
  first program to compare a window with H_claim is the harvest, after the window has run its whole span.
  This check makes the same comparison now, in about ten seconds: it runs the arm's four identity collectors
  with H_claim as the reference, into `$STAGE/desk-seal-check` (never into the custody root). Every code it
  can print removes a window. On `rc=1` do not install: withdraw the plan (5.6), cure the cause it names (a
  stray pack entry: remove it; anything else: section 9), and start again at 5.2. The output directory must
  not exist beforehand, so a repeated check takes a new directory name.
- Do not run the driver's `--dry-arm` on this plan.

**5.4 The arm notice.** Send one email with the Gmail tool to `$NOTICE_TO`. It is this activation's one
email, so it also carries the previous window's outcome. Structure only.

```
Subject: ARM NOTICE: <PLAN_ID> (block 5, <PACK> attempt <n>)

Ed,

No action is needed. Reply NO to stop this window. A NO that arrives by <local time of t0 − 15 min> is acted
on; after that nothing reads mail until the window ends.

Until the result email for this window arrives, please do not open the Claude app, the ChatGPT app, T3 Code,
Chrome, Firefox, or a `claude` or `codex` command on the measurement Mac: the window checks every 30 seconds
and stops itself when it sees an agent. Leave the lid open and the charger connected, and do not touch the
keyboard, trackpad or lid.

What this is: window <PACK> attempt <n> of measurement block 5, under the sealed registration
configs/campaigns/v5_claim_25g83/registration_block5.md (sha256 <REG_SHA256>).
Previous window (omit for ALPHA-1): <plan id>: verdict <V>, claim-usable <yes|no>, members <raw-valid>/<planned>,
window-removing codes <codes or none>.

Times: t0 <local time> (epoch <T0_EPOCH_S>). The chain starts 4 to 47 minutes after t0 and is expected to run
5 to 9 hours. The deadline is t0 + <window_max_s> s. The result email should reach you by <local time of
t0 + 10 h>. If it has not, the email failed, not necessarily the window.
[These three lines only when Ed's answer E-6 is YES:
In that case the Mac would otherwise sit idle for about a day. From the Terminal application, not from a
Claude session, you can release it with:
N="<CUSTODY>/night"; test -f "$N/courier.json" && test ! -e "$N/courier.sent" && echo owner-release > "$N/courier.sent"]
Identifiers: plan <PLAN_ID>, plan sha256 <…>, clone head <…>, custody <CUSTODY>.
```

The two requests in the second paragraph are there because nothing else tells Ed. `[C3, WR-3]` Opening the
Claude application is enough to stop a chain: it starts its own `claude` program within seconds, with no
session. The Mac's only display is the built-in one, so a closed lid puts it to sleep, and on battery it
sleeps after one idle minute; the window holds nothing that keeps it awake. A chain stopped either way has no
closing calibration, so the window cannot carry claims. The "by t0 + 10 h" sentence makes silence a signal.
`[M9]` The previous window's line is taken from the reading block of 4.5 and from nothing else. The
bracketed release command is an owner action, offered only when Ed asked for it (answer `E-6`): no agent can
run while the machine is fenced, so nobody but him could use it. `[M2]` The notice's times follow the lead
(answer `E-4`): with the default of 1,800 s Ed has about ten minutes between the notice and t0 − 15 min.

Then search Gmail for unread mail from Ed (the query of section 3 case 1: `from:<address> is:unread`, with the
value of `NOTICE_TO` as the address) across all threads. A NO stops this
arm: do not install; withdraw the plan (5.6); answer Ed in one line; record it; exit. The session that arms
does not stay to read mail; the activations the watchdog starts between your exit and t0 − 180 s each search
once (section 3 case 1), about every ten minutes, which is why the notice promises t0 − 15 min and not later.
`[M7]` If the notice cannot be delivered, section 8 says what to do; an arm notice that reached nobody is not
a notice.

**5.5 Install, strictly before t0 − 300 s, then verify.** First run the agent check of 5.1 again: both lists
must be empty. `[C2, C4]`

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"; cd "$MEASUREMENT_ROOT" || exit 3
/usr/bin/pgrep -a -lf '[c]odex|[c]laude' | PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_agent_check.py" || { echo "an agent is alive: do not install"; exit 3; }
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" 2>&1 | tee "$STAGE/install.out"
launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}' | sort      # exactly: com.joulewise.night, com.joulewise.night.deadman
plutil -p ~/Library/LaunchAgents/com.joulewise.night.plist | grep -A6 ProgramArguments   # …/run_night.py run --plan $PLAN
```

Refusals: exit 2 `install_span_closed` (too late: 5.6, then 5.2 again); exit 3 `plan … does not match …
checkout HEAD` (the clone's head moved after the inputs were written: 5.6, then 5.2 again); exit 3
`night_agent_already_loaded` or `retained prior plist` (section 4.4 was not done for the previous window: do
it, then install). If the agent check stops the block because a foreign agent appeared after 5.1, withdraw
the plan (5.6) and go back to 5.1's rule.

**5.6 Withdrawing a plan that will not be armed.** A plan left under `/Users/edr/night-custody/` fences the
machine around its t0 whether or not it was installed. Move it out, in this order and no other: `[M6]`

```zsh
P='<plan id>'; source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; : "${PLAN:?}"
if [ -n "$(ls ~/Library/LaunchAgents | grep com.joulewise.night)" ]; then "$MEASUREMENT_ROOT/scripts/install_night_agent.sh" --uninstall --plan "$PLAN"; echo "uninstall rc=$?"; fi
test -z "$(ls ~/Library/LaunchAgents | grep com.joulewise.night)" && mv "$CUSTODY" "/Users/edr/night-custody-archive/$PLAN_ID-withdrawn" && echo WITHDRAWN
```

It must print `WITHDRAWN`. If it does not, a job file is still installed: **leave the custody directory where
it is**, run the block once more, and if it still fails send the fault email yourself and record it. *Why:*
the uninstaller can keep the job files (exit 4 when a label is still loaded, exit 1 on an error). If the
custody were moved then, the installed job file would name a plan path that no longer exists; the watchdog
cannot read such a job and from then on starts no activation at all, and it queues no notice about it, so
nobody would be told. The repair, should it ever have happened: run the uninstall with `--plan` pointing at
the moved `night_plan.json`.

**5.7 Record and exit.** Commit and push the arm record (plan id, plan and inputs SHA-256, clone head, t0,
the notice's message id, the files under `$STAGE`). Search for a NO once more; a NO now is 5.6. Stop every
child process you started, then run the agent check of 5.1 one last time: `foreign_agents` and
`own_seats_still_running` must both be empty. `[C4]` *Why the check and not only the instruction:* the
watchdog can end only processes it reaches by parent links from your pid, and only while you are alive. A
seat whose launching shell has exited is never reached, and after you have exited by yourself nothing you
left running is ever signalled; it would still be alive at t0 and the window would refuse. Then exit at once:
do not wait for the watchdog's request at t0 − 180 s. Arming a window is the last act of an activation.

## 6. What each outcome means for the next arm

**No program schedules the block.** The rules below are registration sections 7.2, 7.3, 7.4 and 7.6. No code
computes them: the harvest writes each attempt's verdict, `claim_usable` and window reasons, and you apply
the rules to those records. Section 7.6 is the limit on all of them: the decision to arm again reads only
verdict words, `claim_usable`, reason codes, counts and status words, and never an energy, so re-arming
cannot select on the science outcome.

**What you may open before the release event** (the orchestrator's decision O-7 of 2026-10-07). The
registration's custody map (its section 8) lists the paths nobody may open before the release event and
calls the rest releasable. Decision O-7 gives you less than the map releases, on purpose: every file you do
not open is one that cannot leak a value into a record, an email or a repair. Where the two differ, follow
this list. Of everything a window and its harvest produce, you open only:

- `harvest.json` in a harvest's archive root: `verdict`, `claim_usable` and `exclude_window_reasons`, and
  also its member counts (`yield`), its list of failed collectors by name (`faults`) and `harvest_checkout`.
  You read them through the reading block of 4.5.
- `derived/code-identity.json` in the archive root (which paths differ between H_claim and the commit the
  window ran from).
- `night/hazard_result.json` in the window's custody root (the driver's verdict, the arm's verdict for each
  hazard, the yield counts for each stage, the reason codes the driver raised, the fault reasons), and the
  one word `result` of `night/g10.json`.
- `hazards/arm.json` in the window's custody root, the **arm record**: what the arm measured for each of the
  six hazards, its verdict for each, and so which hazard modules refused. Registration section 7.3 builds the
  **cause key** of an attempt that started no chain from this file (the cause key is what rule 1 below
  compares between two attempts of a pack: the hazard modules that refused, or the families of the
  window-removing codes), and the registration's custody map lists the file as a hazard measurement that may
  be read during the block (the orchestrator's decision of 2026-10-07 23:55 adds it to this list).

A consult seat that you convene may also read the monitor's contention journal,
`<custody root>/hazards/monitor/contention.jsonl` (process names and CPU shares). **Nobody opens
`derived/flags.jsonl`, `derived/exclusions.json` or `derived/window_flags.json`** (seal gate ruling SG-12):
they name, member by member, a reason code whose presence says something about a measured energy. The
harvest program reads them to compute `claim_usable`; you read `claim_usable` from `harvest.json`. Nobody
opens anything else under a custody root's `hazards/`, `flags/`, `operator-logs/` or `night/transcript/`, its
`night.log` or chain logs, a runs root, or an archive's `sources/` or `withheld/`, except a program that
prints structure only (the END STATE count below is one). Plan-time files written at the desk before t0 (the
plan, `window.env`, the staging directory) are not restricted. Testing that a file exists is not opening it.
Every brief you write for a seat carries this passage whole, from "What you may open" to here.

| Outcome | What you do next |
|---|---|
| `verdict=COLLECTED claim_usable=true` | The pack is done and is never armed again. Arm the next pack's attempt 1 (ALPHA, then BETA, then GAMMA), if the `B5-ARM-RELEASED:` line names it (section 3 case 4). After GAMMA: the block is closed (section 7). The pack's analysed window is its first claim-usable attempt in arm order; attempts are never mixed (registration 7.2). |
| `verdict=COLLECTED claim_usable=false`, and every window reason is one of `*.identity_unmeasured`, `model.identity_unpinned`, `whole_window.verdict_absent`, `records.source_changed_during_harvest` | The harvest is the problem, not the window (registration 7.2, "harvest problems first"): a check did not run, had no pin to compare against, or ran on moving bytes. `whole_window.verdict_absent` with a pin that was not advanced: redo 4.3, then harvest again into `harvest-$P-r2`. `records.source_changed_during_harvest`: something wrote into the custody or a runs root while the harvest ran (a dead-man firing if 4.4 was skipped, or an orphaned verdict writer, 4.5); make sure neither is alive and harvest again. Otherwise fix the harvest (section 9) and harvest the same bytes again. Decide only from the re-harvest. |
| A window reason is `code.executed_differs_from_sealed`, `pack.identity_mismatch` or `model.identity_mismatch` | Before anything else open `derived/code-identity.json`. If the file is absent, or its `window_input` list is empty while the only difference is the head (`check: head`), the harvest *program* is at fault, not the window: the desk root is at a commit that does not know the seal landing. Do not re-arm. Run the test of 4.5; when it prints `HARVEST_PINNED`, harvest again into `-r2`. `[SC-2]` If the file lists a changed window input, or a model or pack mismatch stands, the window is lost and the same defect would lose the next one: section 9 before any arm. |
| A window reason is `cell.below_minimum`, `neg8.bound_not_derived` or `neg8.screen_failed` | Do not arm the same pack again unchanged. Each of these can come from a cause the next window would meet again, and the rate of that cause on this Mac with no agent alive was never measured before ALPHA-1. `cell.below_minimum`: one reported quantity kept fewer than 5 of its 10 units of one kind, most plausibly because a system process kept exceeding the contention limit (0.05 CPU-seconds per second in a 10-second interval that overlaps a member's request). The two `neg8` codes: reference or corpus members (the small fixed workload against which drift is screened) could not be used; the chain runs a spare only for a member that did not succeed, and the corpus has no spare at all. Convene the consult of rule 1 below at once, on the first occurrence. Its evidence is structural: the window reasons, the member counts, and the monitor's contention journal. `[AH-1, WR-1]` |
| `verdict=COLLECTED claim_usable=false`, any other window reason | Arm the same pack again with `ATTEMPT` + 1. First apply the rules under the table. |
| On GAMMA, the window reason `neg8.midpoint_lost_primary` | The same: GAMMA is armed again (registration 7.2; seal gate ruling SG-5). On ALPHA and BETA the lost midpoint is disclosed only and removes nothing. |
| `verdict=NULL` (no chain started: the census or the arm refused, or the driver failed before the chain) | Read the refusing hazard from `night/hazard_result.json` and, for which hazard modules refused and what each measured, from the arm record `hazards/arm.json`. Remove it, then arm the same pack again with `ATTEMPT` + 1 (registration 7.2). **An agent process:** this is not "nothing to fix". Section 5.1's agent check must print two empty lists before any plan is written; until it does, no arm. `[C2]` **A competing process:** name it from the arm record. A leftover of ours (a test worker, a stub): kill it. `fseventsd` (the file-events daemon, which has looped on this Mac before): run `sudo -n /usr/local/sbin/joulewise-restart-fseventsd`, wait 3 minutes; if `/usr/bin/log show --last 10m --predicate 'process=="launchd" AND eventMessage CONTAINS "spawned corecaptured"'` shows more than two lines, switch Wi-Fi off and on once (`networksetup -setairportpower en0 off`, 8 s, `on`); then arm. `[AH-6]` **The battery** charging or discharging: wait until the adapter is connected, the battery is not charging and its current is at most 200 mA in either direction, then arm. **The frequency gate:** the redraw of 5.1. **Disk:** 5.1. **An operating-system build the acceptance never judged:** fault email; no arm. |
| `verdict=NO_COLLECTION` (the chain started and no collection stage ran to its end) | 4.2 closes the session and 4.3 advances the pin, as always. Then as the row above, by the stop's reason. |
| exit 2 or 3, `verdict=HARVEST_FAULT` | Never a science outcome. Fix the harvest program (section 9), then harvest the same archive bytes again into a new directory. Do not arm the next window until a harvest has given this window a verdict, however long the fix takes. `[HN-1]` The fix seat works from the error's type, the collector names in `harvest.json` `faults`, and a reproduction on the real-model rehearsal archive `/Users/edr/night-archive/gate-prune/rehearsal-real/` (a rehearsal, not a claim window). The error's text is restricted: if those three do not locate the defect, the question of who may read the text goes to a cold gate (a fresh Fable 5.1 judge), not to you and not to the fix seat. |
| exit 6, or the driver's yield status `EMPTY`, or `LOW` with one shared cause (the driver's reason code `stage.members_refused_pre_bundle_identical` in `flags_emitted` of `night/hazard_result.json`) | A deterministic loss: the same code would lose the next window the same way (registration 7.3). Do not arm on unchanged code. Find the cause from structure (codes, counts, exit codes), fix it (section 9), then arm. The yield rule below names the one `LOW` this row does not cover, and says what to do when the driver's code is absent. |
| The window's `night/g10.json` has a `result` other than `DISCHARGED` | One consult (two blind seats) before BETA is armed. It gates nothing in ALPHA. |
| A flag code the catalog does not classify | You will not see it: it is named only in the restricted files, and `claim_usable` already counts such an attempt as usable when no classified code removes it (registration 7.2). It is classified by a cold erratum before the release event. If that later makes an attempt not claim-usable, the last rule under the table applies. |

**The yield rule** (registration sections 5.7 and 7.3). The driver gives every window a yield status from
counts alone, and `EMPTY` or `LOW` sends Ed a fault email. A yield status stops nothing and removes nothing.

- *One `LOW` does not hold the next arm.* On GAMMA the two diagnostic interior references (stages
  `gamma-reference-decode-midpoint` and `gamma-reference-prefill-midpoint`, one member each) are counted as
  science stages, so one lost diagnostic member makes the whole window `LOW`. That happens by chance in about
  5.3 % of GAMMA windows, the diagnostic member enters no reported quantity and no contrast, and a single lost
  member is not a cause repeated across members. So when the only stage of `yield.per_stage` in
  `night/hazard_result.json` whose `succeeded` is below its `min_valid` is one of those two stages, the `LOW`
  does not hold the next arm: decide from the harvest as usual.
- *A wholly lost stage no longer removes a window by itself, and it is still reported.* A science stage of
  20 members is five of one quantity's ten quads. Since the seal gate set the minimum to 5 units of each kind
  (it was 8), a window that lost one whole stage and nothing else in that quantity keeps 5 and can be
  claim-usable; one more lost quad in the same quantity removes it (`cell.below_minimum`). The driver's own
  threshold stayed at 8 of 10, so such a window reads `LOW`, Ed gets the fault email, and you report the
  stage's counts in the next arm notice. Whether it holds the next arm is the table's `LOW` row: it does when
  the stage's members were lost to one shared cause. The driver's code
  `stage.members_refused_pre_bundle_identical` says so directly. The registration's second test for a shared
  cause, the harvest's grouping of the members' error lines, lives in a restricted file, so you cannot read
  it: when a stage was wholly lost and the driver's code is absent, convene the consult of rule 1 before
  arming the same pack again.

Rules before any re-arm of the same pack:

1. **Same cause twice goes to a consult, not a third arm** (registration 7.3). If this attempt and the
   previous attempt of the same pack were lost for the same family of cause (the same refusing hazard, or
   window reasons of the same family), convene two blind seats (Sol 6.1 at effort high through
   `codex-run-v3`, and an Opus 5.5 agent) with the structural evidence, then decide: another unchanged
   attempt, a change, or END STATE. A consult that cannot settle goes to a cold gate (a fresh Fable 5.1
   judge); a Fable refusal goes to Ed. None of this is a cap on attempts.
2. **A cure must not move the clone.** See section 9.
3. **END STATE is counted after every harvest of a window that started a chain** (registration 7.4). A
   member's metadata and each calibration capture record one status word for the clock check, `bounded` or
   another word. Across every started attempt of the block: if at least 5 members and captures together have
   a recorded status and more than half of those are not `bounded`, the clock instrument is failing, another
   window cannot cure it, and the block is in END STATE (section 7). No program adds the counts of several
   attempts, so run this one, which reads restricted files and prints integers only:

```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh
python3 - <<'PY'
import glob, json, os
recorded_total = not_bounded_total = 0
for custody in sorted(glob.glob("/Users/edr/night-custody/v5-b5-*")):
    plan_id = os.path.basename(custody)
    if not os.path.exists(custody + "/night/chain.started"):
        continue                                    # only attempts that started a chain are counted
    archives = sorted(a for a in glob.glob("/Users/edr/night-archive/harvest-" + plan_id + "*")
                      if os.path.exists(a + "/harvest.json"))
    if not archives:
        print(plan_id, "not harvested: not counted")
        continue
    archive = archives[-1]
    harvest = json.load(open(archive + "/harvest.json"))
    members = json.load(open(archive + "/withheld/member-assessments.json"))["members"]
    words = [m.get("anchor_recorded") or "not recorded" for m in members.values()]
    if "calibration.no_bracket" not in (harvest.get("exclude_window_reasons") or []):
        bindings = json.load(open(custody + "/night_plan.json"))["hazard_window"]["bindings"]
        for key in ("pre_calibration_dir", "post_calibration_dir"):
            try:
                evidence = json.load(open(bindings[key] + "/instrument_evidence.json"))
                words.append((evidence.get("clock_anchor") or {}).get("status") or "not recorded")
            except (OSError, ValueError, KeyError):
                pass                                # a capture that cannot be read is left out of the count
    recorded = [w for w in words if w != "not recorded"]
    not_bounded = sum(w != "bounded" for w in recorded)
    recorded_total += len(recorded)
    not_bounded_total += not_bounded
    print(plan_id, "recorded", len(recorded), "not_bounded", not_bounded)
end_state = recorded_total >= 5 and 2 * not_bounded_total > recorded_total
print("block total: recorded", recorded_total, "not_bounded", not_bounded_total, "END_STATE" if end_state else "continue")
PY
```

   Its reading of the two files was tested on 2026-10-07, by the seat that finished this brief, on the three
   real-model rehearsal windows (which are not claim windows), with their custody and archive paths passed
   in by hand because rehearsals do not live under the block's paths: 15, 1 and 13 recorded status words,
   none other than `bounded`, result `continue`. The harvest writes each member's word with the same
   three-way rule the program reads (`bounded` or another status word, `unbounded` for a word it does not
   know, `not recorded` for none).
   The program as printed here, with its two `glob` lines, has not run on a real block-5 custody root: none
   exists before ALPHA-1. Its rule for the two captures is an approximation of the registration's ("only for
   a window whose bracket session was finalized"): it counts them when the window reasons do not include
   `calibration.no_bracket`. So when it prints `END_STATE`, have one consult seat count the status words again
   from the ledger and the member records, by a program that prints integers only, before you act on it. A
   window whose own count meets the rule already carries the window reason `clock.systematic`.
4. **A re-harvest that changes `claim_usable`** (registration 7.2). A repaired harvest program, run on the
   same bytes, may change a completed attempt's `claim_usable`. A pack whose analysed attempt becomes not
   claim-usable is armed again after the packs already scheduled, and the changed order is recorded and told
   to Ed. An attempt that becomes claim-usable is the pack's analysed attempt only if it is that pack's first
   claim-usable attempt in arm order; a later attempt of the pack is then listed as not analysed.

## 7. Closing the block

- **All three packs have a claim-usable attempt.** Email Ed once: block 5 collection is complete, with each
  pack's analysed window (its first claim-usable attempt), every attempt's plan id, verdict and `harvest.json`
  SHA-256, and the count of attempts per pack with their causes. Remove any loaded night job (4.4). Arm
  nothing further. The next work is the analysis lanes named in the RUN_STATE block (lane L9 and lane
  L9-NEG8, written blind, before any release event); start them only as that block says.
- **END STATE.** Arm nothing further. Email Ed once with the structural evidence. Write the design record
  that names the cause; it goes to a consult and a cold gate. Claim-usable windows keep their bytes.

## 8. When you email Ed

One email per change of state, never a progress report:

- **An arm:** the notice of 5.4.
- **A stand-down** the watchdog requested while other work was in flight (the relaunch prompt's standing
  rule). A session that has just armed, or that has nothing in flight, sends nothing more.
- **The block is complete,** or reached END STATE (section 7).
- **A fault:** a window whose result record shows a chain stop, an empty or low yield, a monitor or
  instrument failure (the courier sends this one itself; add yours only if you learned something the courier
  could not say); a window whose `night/courier.sent` is absent (the courier could not send, so Ed has heard
  nothing: report the window's structural result yourself and say that the courier failed); a
  machine-identity change (5.3); an uninstall that would not remove the job files (5.6); the same failure
  twice with no cure from the consult; a Fable refusal.
- **A question only Ed can answer:** a hardware or operating-system setting, a permission setting (section
  10), a session on the Mac that you may not end (5.1), a choice the registration reserves to a cold gate
  that the gate sent to him. Ask so that one word answers it, and give the cost of each answer.

Everything else is yours to decide and record. Pending notices the watchdog hands you at launch (a yield
alert, a forced stand-down, a launch failure) go into the next email you send; acknowledge them only after
Gmail has accepted that email.

**If Gmail is unavailable.** `[M9]` Write the exact message under `/Users/edr/night-custody/magistrate/` and
say so in the record, in every case. Then read Ed's answer `E-3` (section 2), which says whether a GitHub
issue opened from this Mac reaches him.

*If it is `YES`* (the fallback Ed ruled in issue #349): open an issue with
`gh issue create --repo mpmdw/JouleWise --label directive-notice --title "<the email's subject>" --body-file <the message>`,
record its number as the notice's transport, and go on as if the email had been sent. The title and the body
are the email's subject and text and nothing more: no email address goes into an issue.

*If it is `NO`, or there is no answer, or the issue cannot be opened either:* for an **arm notice** do not
install: withdraw the plan (5.6), append the time to `$BENCH/notice-failures.log`, and exit. The arm notice
with Ed's NO is a gate this block keeps, and a notice nobody could receive is not one. An activation that
finds the log's last line less than an hour old exits quietly without writing a plan; the first one after
that hour arms again from 5.1. For every other email, do not hold the work for it: the next activation that
finds Gmail working sends it.

## 9. Fixing things: fixed, merged, re-armed

A failure you can fix is fixed. "Halt and email" is not an outcome of this brief, and no fix waits for an
interactive session. The route (called R3 in the records): a branch in a linked worktree; the fix with tests;
the merge gates (for code: an independent executing review, the whole suite on the merged tree, CI green on
the final head, a cold Fable 5.1 pass when the code touches measurement, calibration or claims, findings
dispositioned, the Impact statement; for documents and tests: the light tier); merge; then continue from where
the failure stopped you. Sol 6.1 at effort high is the default seat for the implementation and the review.

What a fix may touch decides what else it needs:

- **Code that does not run during a window** (the harvest, extraction, the floor mint, analysis, the
  watchdog, this brief, tests, documents): fix, gate, merge. A harvest fix reaches the harvest by moving the
  **desk root** to the merged commit
  (`git -C "$DESK_ROOT" fetch origin main && git -C "$DESK_ROOT" checkout --detach <commit>`, possible
  whenever no window is running), and by a new addendum: one more section appended to the seal record on
  main, with a new line `B5-HARVEST-PIN: <that commit>` and the SHA-256 of each harvest program file
  (`joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py`), written by a
  seat that has read no claim-window energy and pushed as step 3 of variant B in section 4.5 describes.
  Until the canonical root holds that line the test of 4.5 holds the harvest. A watchdog or brief fix takes
  effect by fast-forwarding the canonical root (section 10). **The measurement clone is not moved**: no `git pull`,
  `fetch`, `checkout` or `merge` in it, ever. Its only commits are pin advances. *Why:* every window's
  executed files are compared with the sealed inventory, all three windows must have run the same collection
  code, and the comparison cannot tell "does not run during collection" from "runs": any changed file under
  `joulewise/`, `scripts/` or `configs/` in the clone removes the window.
- **Code a window executes** (the driver, the chain, the campaign runner, the controller, the hazard
  modules, the monitor, the adapters, the packs), and any other file a window reads (everything under
  `configs/`, and `docs/phase_2/window_runbook.md`): this is registration section 7.5. If no completed window
  executed the changed file, the fix needs the merge gates plus a diff-scoped re-audit of the change. If a
  completed window did execute it, the fix supersedes the block: completed windows are kept and disclosed,
  their energies are never analysed, and the block restarts at ALPHA under a prospective cold erratum (one
  Fable 5.1 judge, one Opus 5.5 refuter). In both cases the changed code reaches a window only through a
  **new** measurement clone, and **the seal is issued again for it**. `[SC-8]` The steps, which the erratum's
  seal record lists:
  1. The cure's merged commit is the new H_claim. On a clean checkout of it, generate the inventory:
     `/opt/homebrew/bin/python3.13 -B docs/process_traces/2026-10-07-block5-seal/bench/make_sealed_inventory.py <checkout> <out.json>`.
  2. Commit that one file, `configs/campaigns/v5_claim_25g83/sealed_inventory.json`, as the new H_claim's
     only child: the new seal commit. Run `python -m unittest tests.test_b5_seal_landing`; it must pass.
  3. Build the new clone at the new seal commit by the hand-off runbook's clone, relock, ledger and bench
     steps (`docs/process_traces/2026-10-07-block5-seal/30-post-seal-runbook.md`, steps 3 to 6), carry the ledger file over, commit the
     pin there, and write a new fixed-values file with the new `MEASUREMENT_ROOT`, `H_CLAIM` and `SEAL_HEAD`.
  4. Run the desk seal check (5.3) with the new H_claim before the first arm from the new clone.
  *Why the inventory:* a clone at the cure's commit with the old inventory passes every check before the
  window; the window then runs its whole span and is excluded at its own arm record and again at its harvest,
  because the executed files no longer match the inventory. Have one consult seat check the commands of step
  3 before you run them; carrying the ledger and the pin into a new clone has not been rehearsed. **The old
  clone is never edited or deleted** before the release event: the windows that ran from it are harvested,
  and re-harvested, against its files. If it must be moved, every later harvest of those windows passes
  `--measurement-root <its new path>`. Never edit the four pinned estimator files (`joulewise/reduce.py`,
  `joulewise/uncertainty_evidence.py`, `joulewise/powermetrics_fiducial.py`,
  `joulewise/adapters/powermetrics.py`) or `scripts/prewindow_check.sh`.
- **A threshold, a catalog effect, the roster or a blinding rule:** a prospective cold erratum before the
  next arm (registration section 10). A review finding that is only about how something is recorded is
  dispositioned "flag, not refuse" and gets no fix round.

Every review brief you write carries `/Users/edr/night-archive/gate-prune/REVIEW_BRIEF_RULE.md` verbatim: only
a directly measured physical hazard or a number-integrity condition may stop collection or exclude data.

## 10. Rules that hold for the whole block

- **Never start or continue measurement work while an agent session is alive**, and never let agent work run
  into a window: every session, seat and background process you started is gone before you exit after an arm
  (5.7 proves it).
- **Blinding** (sections 1 and 6). Never open the body of a harvest or fix pull request. Your own
  pull-request bodies, records and emails carry structure only: no energy, power or duration, no member's
  name, no error text, and no count of flags by reason code.
- **No Homebrew.** No `brew install`, `brew upgrade`, `brew reinstall`, `brew uninstall` or `brew cleanup`
  during the block, by you or by any seat you brief. `[CE-3]` The clone's interpreter is a link into
  Homebrew's `python@3.13`, an upgrade is already pending there, and a `brew install` of anything that depends
  on Python can perform it. The interpreter of the existing environment would change in place, and every later
  window would run its whole span and be excluded for it. The formula is pinned; 5.1's last check and the desk
  seal check are the proof before each arm.
- **The canonical root** `/Users/edr/code/JouleWise` is moved only by `git pull --ff-only`, only when no night
  job is loaded and no plan is armed, and only when a merged fix to the watchdog or to this brief, a harvest
  addendum or a changed `B5-ARM-RELEASED:` line has to take effect. Records merges can wait for the block's
  end.
- **Instructions that predate the hand-off.** The relaunch prompt has you read Ed's unread mail and the open
  issues labelled `directive` at every launch. Whatever of either predates this hand-off is discharged as the
  RUN_STATE top block says, issue by issue. An instruction dated after the hand-off is new, and it binds.
  `[M12, M13]`
- **No STOP file and no `ops/stop-*` ref** to pause. A pause is pushed work and an idle machine.
- **Never message a running workflow agent**; route a correction through a file or a follow-on lane.
- **Only Opus 5.5 writes prose a person reads** (records, pull-request bodies, emails). Fable and Sol seats
  return findings, code and verdicts.
- **Usage.** If `claude` reports a usage limit, exit; the watchdog backs off and starts you again. No email
  about it.
- **Permissions.** The settings sentence that lets a headless session run the science pipeline was written
  on 2026-10-02 and names the block-1 programs; whether the session's permission check passes the block-5
  programs of this brief was not tested before the hand-off. If the check blocks one of this brief's
  commands, do not work around it and do not change any permission setting. Do every step that does not
  need the blocked command. Then look in `$BENCH/permission-blocks.log`: if the exact command is not there
  yet, append it with the time and send Ed one email that quotes it and asks him to allow it (a question
  only he can answer; one word, "allowed", answers it). If it is there, send nothing. In both cases exit;
  the next activation tries the command again.
- **Ed's address and name go into no network request** made by you or by a seat you brief: not into a URL,
  a header or a payload of `curl`, `wget`, a Python HTTP call or a web tool, not into a `gh` call to another
  repository, and not into a `git config` line. A service that asks for a contact address gets none. The
  one place the address goes is the Gmail tool: as the recipient of a message, and in the search for his
  replies. It is also written into no file that is committed: a record, a note or a pull-request body names it
  as the owner's notice address and never prints it. Every brief you write for a seat carries this paragraph.
- **End every activation with the next action durable.** Because section 3 reads the state from the disk, the
  next activation needs no hand-written pointer for the normal path. For anything in flight (a fix branch, a
  consult, a re-harvest), commit and push a short note on `$RECORDS_BRANCH` that says what is done, what is
  running and the next command. Never end with a step that only an interactive session could do.
