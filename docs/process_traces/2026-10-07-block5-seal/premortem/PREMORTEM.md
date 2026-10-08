# Pre-mortem of the first block-5 window (ALPHA-1): synthesis

Written 2026-10-07, 22:14 to 22:50 PDT, by the synthesizer (Opus 5.5) of the pre-mortem workflow, for the
orchestrator. Sources: the eight lens files in this directory, the verifiers' verdicts on every finding whose
stated effect stops, nulls or excludes, and the synthesizer's own read-only checks of the rest. Code citations
are to the integration head `9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a` (branch `integrate/2026-10-07-int5`,
worktree `/Users/edr/code/JouleWise-wt-int5`), which every lens's second pass used.

The question each lens was given: assume ALPHA-1 was armed from the runbook and failed to give a claim-usable
window; find the cause before it happens.

## 1. The answer in one page

**Nothing found in the code path is likely to lose ALPHA-1.** A clone built by the runbook at a correctly
landed seal passes every identity check at the arm and at the harvest for all three packs, the plans are
accepted by the plan writer, the chain check, the installer and the driver, and the registered order after a
window (pin advance, then harvest, then the next plan) ran end to end with the real programs, on scratch copies
of real rehearsal bundles, for the first time in this pre-mortem.

**What would have lost it is the hand-off around the code.** Fifty-five findings; none was refuted. Three groups
would have cost ALPHA-1 itself, or a full day, with certainty or near it, and all three are now runbook steps
or brief sentences:

1. The orchestrator's own session is an agent process. Nothing ended it, and the window refuses while it lives
   (C1). After such a refusal the watchdog starts nothing for up to 28 h 28 min while the process stays alive
   (C2), not "about a minute" as three draft sentences said. Deleting the stop ref starts an arm about 35
   minutes later without looking at who else is on the machine (M4).
2. The brief harvested ALPHA-1 at once and armed BETA-1, although the registration and the seal gate's stage-1
   ruling make ALPHA-1's harvest wait for an addendum that pins the harvest program (M14), and the brief named
   no fixed checkout for that program (SC-2). The brief also allowed "arm first, harvest both later", after
   which the earlier window's verdict can never be written (HN-1).
3. The magistrate's commands were written with shell variables that do not survive from one command to the
   next (M5), and its relaunch prompt forbids what the brief orders (M3).

**Before the code head is frozen** one thing is open and it is not a finding's cure but missing knowledge: the
twelve Linux test shards have never completed on this tree (SC-5). At 22:15 PDT one had failed and ten had been
cancelled behind it. A failure whose cure lies under `joulewise/`, `scripts/` or `configs/` cannot land after
H_claim without re-issuing the seal. No other code change is required before the seal. Two are offered for the
orchestrator's decision (section 5).

**What needs Ed:** which Claude account lasts the block and a test of the headless mail path on it (M1); whether
the magistrate may end a session or quit an application it did not start (C2); whether a GitHub issue reaches
him when Gmail is down (M9). Section 8 has the full list.

## 2. Words used here

- **Pack:** a fixed set of experiment inputs. Block 5 has three: ALPHA, BETA, GAMMA. **Window:** one unattended
  measurement run of one pack, started by launchd at a planned time **t0** from a **plan** file
  (`night_plan.json`) in the window's **custody root**. **ALPHA-1** is the first attempt of the first pack. A
  window's deadline is t0 + `window_max_s` (28.4 h for ALPHA); its expected collection is 5 to 9 hours.
- **Member:** one measured model run. A **cell** is the set of members that share one experimental condition; a
  cell is built from **units** (single repeats, or groups of four members called quads). The catalog removes a
  window when a target cell keeps fewer than `rules.cell_unit_minimum` units of either kind. **Reference**
  members (in ALPHA and BETA seven per window: three at the start, one in the middle, three at the end) and
  twelve **corpus** members measure a small fixed workload against which drift is screened; a **spare** is a
  reference the chain runs again when one did not succeed.
- **Ledger and pin:** the calibration ledger is the append-only file of calibration captures in the clone; the
  pin is the committed file that names its last row. Each window opens one **session** in the ledger; after a
  window the **pin advance** commits the new last row.
- **Stop ref:** the remote branch `ops/stop-pause`; while it exists the watchdog starts nothing. **Span** and
  **fence:** from t0 − 180 s until a window is released the watchdog starts no magistrate; that interval is
  the plan's span, and the machine is said to be fenced. **Dead-man job:** the second launchd job of a window,
  the fallback that stops what a dead driver left; it carries only an hour and a minute, so it fires daily.
- **Arm:** the driver's measurement of the physical hazards at t0. **Census:** the driver's listing of Claude and
  Codex processes (`/usr/bin/pgrep -a -lf '[c]odex|[c]laude'`, decided by `joulewise/agent_identity.py`), taken
  first at t0 and then every 30 seconds while the chain runs. **Chain:** the shell program that runs the members
  between two calibrations.
- **Magistrate:** the headless `claude -p` session that arms and harvests. **Watchdog:** the launchd job that
  starts a magistrate every 300 s when no window is in progress. **Courier:** the short `claude -p` session the
  driver starts at a window's end to email the result; it writes `night/courier.sent`.
- **Harvest:** the desk program that turns a finished window's bytes into numbers and flags and prints
  `claim_usable`. **Claim-usable:** no flag whose catalog effect is EXCLUDE_WINDOW stands against the window.
- **Window input:** a tracked file a window can read: everything under `joulewise/`, `scripts/` and `configs/`,
  and `docs/phase_2/window_runbook.md`. **H_claim:** the last commit that changes a window input. **Seal
  commit:** its only child, which changes only the sealed inventory, the registration and the analysis plan.
  The **measurement clone** is checked out at the seal commit. The **desk root** is the separate checkout the
  harvest runs from. The **canonical root** is `/Users/edr/code/JouleWise`, where the watchdog and the
  magistrate run.
- **Effect words:** a finding **stops collection** (a running chain ends early), **refuses the arm** (no chain
  starts; nothing was collected), **excludes** a member or the window at the harvest (the bytes exist and are
  removed from the claims), **delays** the next arm, or only **flags**.

## 3. What changed after the lenses ran (checked by the synthesizer, 22:14 to 22:30 PDT)

| Fact | Consequence for the findings |
|---|---|
| The seal-landing lane is merged (int5 `9395cecfb`) and its procedure accepted (`../seal-land/ORCHESTRATOR_RULING.md`). | SC-1 is cured. The runbook's seal-landing fills are written from `../seal-land/SEAL_LANDING.md`: H_claim and the seal commit are two commits; the clone is at the seal commit; `identity_pins.json` and `sizing_b5.json` keep their draft labels (ruling F7). |
| The seal gate's stage-1 ruling is in `/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE1.md`. It sets the cell minimum to 5 (change C-1; pushed on `lane/2026-10-07-seal-rulings` at `059fafc55`, not yet in int5, where the catalog still says 8). | AH-1, AH-2 and WR-2 were computed at a minimum of 8 of 10. At 5 a cell must lose six units, not three, before the window goes. Section 4 gives both numbers. |
| The same ruling keeps window-time code unchanged before the freeze and puts the cures for a reference with unreadable energy into harvest code (K-4 to K-7), landing after the seal in a desk checkout; "ALPHA-1's harvest does not run until the addendum exists". A harvest lane is running (`../harvest-lane/NOTES.md`: K-4 in flight at 22:13). | WR-1's proposed change to `joulewise/b5/chain.py` is not taken. M14's hold is a ruling, not only a proposal. The orchestrator's 21:45 note calls the harvest-then-arm sequence pending before the judge, so the brief marks it PENDING THE JUDGE and writes both variants; one test on the disk selects between them, so the text is right either way. |
| The same ruling (SG-12, change T-32) restricts `derived/flags.jsonl`, `derived/exclusions.json` and `derived/window_flags.json` until the release event. | The brief's draft read `derived/window_flags.json`, and two lens cures sent the magistrate to `derived/flags.jsonl`. The brief no longer opens any of the three. Which other harvest outputs the magistrate and a consult seat may open is a question for the orchestrator (section 8, item O-7). |
| CI: draft #489 at `9395cecfb` has `quick` failed and the test matrix skipped. The CI lane's draft #490 at `eb0a1fb37` (two test-only fixes) has `quick` passed; shard 5 failed, shard 3 passed, ten shards cancelled by fail-fast; one exclusive job still running. | SC-5 stands and is the one open item before the freeze. |
| Free disk: 123 GiB at 22:14 PDT (146 GiB at 15:50). | CE-4, AH-5 and PD-4 stand; the third window's arm is at the refusal line with no margin. |
| Gmail: the search the magistrate runs at launch returns two unread messages from Ed's alias, dated 2026-10-05. `gh`: six open issues labelled `directive`; no label `directive-notice`. | M12, M13 and M9 stand as reported. |
| Machine at 22:17 PDT: `displaysleep 0`; on AC at 80 %, not charging; foreground applications Finder, Terminal, firefox; `mediaanalysisd` running although marked disabled; Homebrew `python@3.13` at 3.13.1 and not pinned; lid open; watchdog `STOPPED` on `ops/stop-pause`; only `com.joulewise.magistrate` loaded. | WR-2, AH-3, AH-2, CE-3 and WR-3 describe the machine as it is now. |

## 4. Confirmed findings, each with its cure in its place

"Verified" names who reproduced the finding: **V** a verifier (verdict CONFIRMED, with the corrections folded
into the wording here), **S** the synthesizer, **L** the lens only. Findings with the same cause are merged and
both ids are given. Steps (A0 to A11, B1 to B-after) are in `POST_SEAL_RUNBOOK.md`; sections (1 to 10) are in
`MAGISTRATE_BRIEF_DRAFT.md`.

### 4.1 Cured by a runbook step

| Id | What goes wrong, as verified | Effect | Cure, and where it now is | Verified |
|---|---|---|---|---|
| C1 | The interactive session (pid 99199 and its three Codex MCP servers) is the only agent on the machine and nothing ends it. Alive at t0, the driver's first census refuses: verdict REFUSED, reason `night_refused_agent_present`, no chain. Each attempt costs about a minute, and every re-arm refuses the same way until the session is gone. | refuses the arm, repeatedly | Ed types `/exit` on the orchestrator's email (decided). Runbook A10 fixes the order (stop the wave, email, delete the ref) and the email's content; A11 names the session's end as a step, with the documented hand-off reaper as the agent-run fallback. Proof is the magistrate's: brief 5.1 writes no plan while a foreign agent is alive. | V |
| M4 | Outside a plan's span the watchdog launches without reading the census, so deleting the stop ref starts an arm about 35 minutes later whether or not the machine can be free of agents. | refuses the arm, then C2's hold | Runbook A10: deleting the ref is the last act of the last agent session. Brief 5.1: the agent check comes first and no plan is written while it lists a foreign agent. | V |
| M1 | Magistrate and courier are both `claude -p` on the Mac's one login, which is the account being cancelled. A login that is over its limit, lapsed or logged out sends no result email, the finished window is then not released (M2), and nothing tells Ed. The login cannot be changed while a window runs: any `claude` command, `claude auth login` included, is an agent process. A headless send has not been tested. | delays the next arm by about a day per window; then stops the block | Runbook A9 reading 9 (needs Ed): the account that lasts the block; the watchdog's launch shape run once in the launchd environment (it must show Opus 5.5, auto mode and the Gmail connector connected); one real email in the courier's shape; Ed's reply found by the magistrate's search. | V |
| M3 | The relaunch prompt is the magistrate's instruction, and four of its lines contradict the brief: line 11 allows arming only through the `NIGHT_HANDBACK` procedure, line 13 only under a v2 plan, line 17 gives the old stand-down times, line 19 names the old plan writer and lets a session remove only a plan it authored. A test pins the stale phrases. Separately, the courier reads `NIGHT_HANDBACK.md` from the clone, and its three live sections still describe block 1. | delays the arm (a magistrate that obeys the prompt declines to arm); the courier's email misdescribes the window | Runbook A6 item 6: reword lines 11, 13, 17 and 19 inside their pinned phrases, keep 25 lines, run `tests.test_magistrate_watchdog`. Runbook A0 item 3: the handback rewrite must be in the commit the clone is checked out at, so it lands at or before H_claim (it is a document, not a window input). | S |
| M12 | Two unread messages from Ed (2026-10-05, the G10 ruling, ids `1a10b4bafef610b6` and `1a10b4cdfc77967b`) are in the mailbox. The prompt makes every unread message a pending instruction; this one is already applied another way. | delays the arm (wasted turns, a repeated email, at worst a deferred arm) | Runbook A6 item 8 and A9 reading 8: mark both read; the search must return nothing. RUN_STATE draft: a paragraph "Instructions that predate this hand-off". | S |
| M13 | Six directive issues are open (#405, #408, #416, #417, #421, #422) and the prompt makes each body an instruction. #416 demands a three-family audit before any claim-bearing run; #421 states the battery rule as a check by the session. | delays the arm | Runbook A6 item 8: close the four retired ones; close #416 and #421 with the evidence or keep the sentence the RUN_STATE draft carries for each. | S |
| M9 | When Gmail is down the brief saved the message to disk and armed anyway, so a window could start with no notice and no chance for Ed's NO. The ruled fallback (issue #349: a GitHub issue labelled `directive-notice`) cannot work: the label does not exist, and `gh` is Ed's own account. | none on the window; a kept gate is bypassed | Runbook A9 reading 10: create the label, open one test issue, ask Ed whether it reached him. Brief section 8 (PENDING ED): with a working fallback, use it; without one, an arm notice that cannot be delivered means no install. The notice now says by when the result email is due. | S (label absent; notification behaviour not checked) |
| CE-4, AH-5, PD-4 | The arm needs three copies of the window's planned bytes plus 20 GiB on the one volume (87.18 GiB for ALPHA and BETA, 77.59 for GAMMA), and each collected window keeps about 22.4 GiB. So from free space F before ALPHA: BETA needs F ≥ 109.6, GAMMA F ≥ 122.4, one repeat F ≥ 144.8, two repeats F ≥ 167.2. F is 123 GiB and was falling. The brief's cure, an iCloud offload, returns space only after an hour or more. | refuses a later arm (not ALPHA-1); nothing collected is lost | Runbook A9: delete the wave's scratch, four rehearsal rigs under `/private/tmp` (about 259 GiB by `du`) and merged-lane worktrees first, then require 170 GiB (145 the floor). Brief 5.1: the thresholds, deletion before offload, and what is never touched. RUN_STATE draft: the arithmetic. | V (PD-4), S (`df`) |
| CE-1, SC-4 | Runbook A3 check 3 compared `sources`, which holds the probed interpreter's path, so it failed on every correct clone. The likely wrong reaction, regenerating `identity_pins.json`, is SC-3. | delays the arm | Runbook A3: the comparison drops that one field. Run by the synthesizer on a scratch clone: as drafted it raises "sources differs", corrected it passes with nine units in 3.2 s. | S |
| CE-3, SC-6 | The clone's interpreter is a chain of links into Homebrew's `python@3.13`, unpinned, with 3.13.16 pending and nine formulae depending on it. An upgrade changes the existing environment in place; the sealed digest covers the string 3.13.1; every later window runs its whole span and is excluded (`model.identity_mismatch`). Nothing runs Homebrew unattended; the exposure is a person or a seat. | excludes every later window | Runbook A3: `brew pin python@3.13`. Brief section 10: no Homebrew during the block. Brief 5.1 and 5.3: the identity checks before every install. | V |
| SC-3, PD-6 | At the arm the clone is compared with the plan's own head, which the installer forces to equal the clone's head, so a window input changed after H_claim is invisible to the plan writer, the installer and the arm (`driver.py:712`, `night_agent_install.py:1234-1242`). The harvest is the first to compare with H_claim, after the whole span. `identity_pins.json` and `sizing_b5.json` still say `UNSEALED_DRAFT`, which invites the edit. The landing test catches the edit only inside the seal commit, not in a later commit. | excludes the window (and every later one from that clone) | Runbook A1: the seal commit's parent is H_claim, the diff is the three seal documents, the landing test passes; do not edit the two files. A2: `git diff H_claim HEAD` in the clone. A5 and brief 5.3: the desk seal check (`b5_desk_seal_check.sh`), which runs the arm's four identity collectors against H_claim in about ten seconds, before every install. A6: the record commit's check is worded by path class. | V (both) |
| PD-5 | The plan helper hashes the clone's own `sizing_b5.json`, so the plan writer's sizing check compares the file with itself. | none today | Runbook A2: one `shasum` line against the seal record's digest. A committed change is also caught by the desk seal check (the file is a window input). | S (helper line 83) |
| SC-9 | The harvest's nine thresholds have one source, a JSON block in the sealed registration, and the plan helper reads another block of the same text. If the final text's block does not parse, every harvest faults and only a harvest change cures it. All seven candidate texts parse; sections 11 and 12 were unwritten. | delays the verdict | Runbook A0 item 2: `reg_probe.py` on the final text before the seal commit is made. A5b: one harvest-side rehearsal per pack from the desk root. | S (code read; probe not re-run) |
| SC-2 | The harvest program's checkout was an unfilled value and nothing checks its commit. A desk root older than the seal-landing change reports a correct window as `code.executed_differs_from_sealed`, and the brief's table would then re-arm and set a good window aside. The canonical root cannot serve (no harvest script at its commit; it cannot move while a job is loaded). The harvest records nothing about its own program. | excludes a good window, falsely | Runbook A5b: the desk root is its own full clone at the commit the addendum names. Brief 4.5: the test before every harvest. Brief section 6: on an identity code, read `derived/code-identity.json` before any re-arm. Brief section 9: how a harvest fix reaches the desk root. | V |
| SC-1 | Resolved by the merge. | none | Runbook A1 keeps one line: `git merge-base --is-ancestor 2737ef88c "$H_CLAIM"`. | L |
| SC-5 | CI has never run the twelve Linux shards and the exclusive jobs to their end on this tree. Main requires all 18 checks, and the merge must precede the arm. | delays the arm; may force a change before the freeze | Runbook A0 item 1 and A7 (edit draft #489, do not create a second pull request). See section 5. | S |
| AH-3 | Firefox is open. A browser is not an agent, and the block-5 arm has no refusal by application name. In use, it exceeded the contention limit in 5 of 26 thirty-second intervals; idle, it is fifty times under it. | excludes members (the window only if one cell loses enough) | Runbook A9 reading 7 and the `/exit` email: quit everything but Finder and Terminal. | V |
| WR-3 | The Mac's only display is the built-in one and a closed lid sleeps it; on battery it sleeps after one idle minute; the window holds no keep-awake assertion. The instruction not to touch lid or charger exists in the older tracked runbook and was not carried into the block-5 drafts. | stops collection (needs Ed to close the lid or unplug) | Runbook A10 email item 4; brief 5.4, the arm notice. | V |
| WR-2 | Display sleep is asked for once per stage and `displaysleep` is 0, so a display that wakes mid-stage stays awake and every later member of the stage is removed. A 20-member stage is five units of one cell: at a minimum of 8 one early wake removes the window; at the ruled minimum of 5 it leaves that cell with no margin. No unattended wake is on record in 47.6 hours. | excludes members; the window at minimum 8 | Runbook A9 reading 11, optional, Ed's hands: `sudo pmset -c displaysleep 1`. No check reads the value. | V |
| AH-4, WR-5 | `sudo -n -l <command>` exits 0 for any command this user may run with a password, so the check could not fail. | none today | Runbook A9 reading 4: grep the plain listing for the two `NOPASSWD` rules; must print 2. | S |
| AH-1 | The share of 10-second intervals in which a system process exceeds 0.05 CPU-s/s on this Mac with no agent alive has never been measured. Each such interval that overlaps a member's request removes the member, and a removed quad member removes its quad. In the two quietest records 13 % and 14 % of intervals were dirty (19 % and 22 % counting display processes, which the harvest does count). | conditional: excludes the window if the quiet rate is high | Not cured by a step; ALPHA-1 is the measurement. Brief section 6: a window removed by `cell.below_minimum` goes to a consult at once and is not re-armed unchanged. See the numbers below the table, and item O-5. | V |
| AH-2 | `mediaanalysisd` and `photoanalysisd` are disabled on paper and still loaded. Their cost is batches of 435 text-processing requests, 3 to 4 minutes at about 1.7 CPU-s/s, four in 31 hours; a batch removes at most the one to three members it overlaps. | excludes one to three members per batch, not a window | No step. A logout and login by Ed would make the disable take effect; not required. `pkill` is not a cure (the service restarts on demand). | V |

**AH-1 in numbers.** If a fraction x of members is lost to this rule beyond the registered idle-admission loss of
1 in 37, the chance that both target cells keep their minimum is:

| x | 0 | 1 % | 2 % | 3 % | 5 % | 10 % | 15 % | 20 % |
|---|---|---|---|---|---|---|---|---|
| minimum 8 of 10 (int5 today) | 0.849 | 0.711 | 0.561 | 0.419 | 0.203 | 0.017 | 0.001 | 0.000 |
| minimum 5 of 10 (ruled, C-1) | 1.000 | 0.998 | 0.994 | 0.985 | 0.943 | 0.660 | 0.292 | 0.081 |

(Recomputed by the synthesizer: a member is kept with probability (36/37)(1 − x); a repeat unit is kept with
that probability and a quad with its fourth power; a cell has ten units of each kind and needs the minimum of
each; two cells; losses taken as independent.) At a loss rate of 5 % the window survives with probability 0.94
at the ruled minimum, against 0.20 at the old one. That is why the 30-minute quiet census the lens proposed is
listed as an option (item O-5) and not as a step.

### 4.2 Cured by a brief sentence

| Id | What goes wrong, as verified | Effect | Cure, and where it now is | Verified |
|---|---|---|---|---|
| C2 | After a census refusal the watchdog releases the refused window only on a tick where its own census is empty. While any agent outside the window lives it decides `HOLD_CENSUS` and starts nothing until t0 + `window_max_s` + 300 s (28 h 28 min for ALPHA), then launches a magistrate that is refused again. Three draft sentences said "about a minute". | delays the next arm by up to a day per cycle | Brief 5.1: the agent check (`b5_agent_check.py`) and the rule "write no plan while `foreign_agents` is not empty", with what to do by kind of process; repeated before the install (5.5). Brief section 6, the NULL row, and runbook A9 reading 6: the corrected cost. What the magistrate may end is PENDING ED. | S (code), V (M4's dry ticks) |
| C3 | The census pattern is lowercase and `pgrep` is case-sensitive, so the Claude, ChatGPT and T3 Code applications are seen only through a helper or a bundled binary. The Claude app starts its bundled `claude` within about six seconds of opening, with no session (observed 21:19 to 21:27 on 2026-10-07). Opened during a window, it stops the chain at the next census, and a stopped chain has no closing calibration. Nothing told Ed. | stops collection; the window is not claim-usable | Brief 5.4 and runbook A10: "do not open", with no qualifier. Brief 5.1 and runbook A9 reading 7: the check by application name; quit the application's main process, not the helper. | V |
| C4 | The watchdog signals only what it reaches by parent links from the magistrate, and only while the magistrate is alive. A seat whose launching shell exited is never reached; after the magistrate exits by itself, which the brief orders, nothing it left is signalled. | refuses the arm, then C2's hold | Brief 5.5 and 5.7: the agent check must print two empty lists before the install and before the exit. | V |
| C5, M7 | Between the arming session's exit and t0 − 180 s the watchdog starts a magistrate about every ten minutes (eight on 2026-10-04, each gone in 31 to 41 s). The notice promised that mail is read until t0 − 6 min, but the arming session has left, and prompt line 19 forbids another session to remove its plan. The forced stand-down has never run (zero signal events in 3,953). | none on the window; a late NO is not acted on | Brief section 3 case 1: each of those activations searches once for a NO and may withdraw the plan. Brief 5.4: the notice promises t0 − 15 min. Runbook A6 item 6 rewords line 19. "Exit at once" is kept: it is the shape block 3 ran. The lens's alternative (wait for the watchdog's request, then exit) is not adopted, because how a headless session waits 25 minutes is untested. | S (events of 10-04) |
| M5 | Every Bash tool call is a new shell. The brief exported t0, the plan id and the roots in one step and used them in later ones; with empty variables `cd "$MEASUREMENT_ROOT" && …` stays in the canonical root, and re-running the export step computes a new t0. | delays the arm, or runs commands against the canonical root | Runbook A5 writes `b5-fixed-env.zsh`; brief 5.2 writes `arm-env.zsh` with literal values; every block begins by sourcing, and guards on `${PLAN:?}`. Shape tested in scratch. | S |
| M14 | The brief harvested at once and then armed the next pack. The registration (lines 3077-3078) and the stage-1 ruling require the harvest pin first, and `WAVE.md` records a desk gap before BETA. No code holds the harvest. | a harvest before its registered pin (an erratum and a re-harvest); a BETA arm into a machine where desk sessions are working | Brief 4.5 (PENDING THE JUDGE): harvest only when the addendum exists in the canonical root and names the desk root's commit; otherwise exit quietly. Brief section 3 case 4: arm only a pack the RUN_STATE line `B5-ARM-RELEASED:` names. Both read from the disk. | V |
| HN-1 | The function that finds a session's last ledger row refuses once any row of a later session follows it. After the next window's reservation, a harvest of the earlier window from the live ledger records `calibration.no_bracket` and starts no verdict writer, and the pin advance cannot name the earlier session. Shown on real rehearsal ledgers: only the newest of nine sessions returns a pin. | excludes the earlier window; no command in the brief can then write its verdict | Brief section 3 case 4: never arm past a window that still lacks its verdict file. Brief 4.5: a re-harvest of a window that is not the newest passes the first archive's ledger and pin copies. Brief section 6: the "arm and harvest both afterwards" exception is deleted. | V |
| HN-2 | The dead-man job fires daily and appends a line to `night.log`; the harvest hashes the custody root at its archive step and at its end; a firing in the last 18 minutes gives `records.source_changed_during_harvest`. | one more harvest (about 45 minutes) | Brief 4.4: remove the two launchd jobs before the harvest. | S (code read; the lens ran it) |
| HN-3 | A killed harvest leaves its verdict writer running in a session of its own; a second harvest collides with it and records the window as excluded; a third is clean. | one more harvest | Brief 4.5: `pgrep` for the writer must print nothing before any harvest; wait, do not signal. | S (code read) |
| HN-4 | A 119-member harvest takes about 40 to 45 minutes on a quiet machine (the brief said 20 or more); about 15 of them replay a value the harvest already knows, and `whole_window.verdict_unauthenticated` appears on every harvest. | delays the next arm | Brief 4.5: the expected time and shape; the code is disclosed only. The replay's cost goes to the harvest lane. | unchecked (timing not re-run; the lens's step record exists) |
| HN-5 | The brief found "the newest plan" with a plain sort, which orders by pack name first. | confusion; the installer and the plan writer stop a wrong arm | Brief section 3: `ls -1 … | grep '^v5-b5-' | sort -t- -k5`. The synthesizer found that the lens's own fix fails on full paths (the directory name `night-custody` adds a hyphen field), so the brief sorts bare plan ids. | S |
| M6 | The brief's withdrawal ran the uninstall and then moved the custody unconditionally. If the uninstaller keeps the job files (exit 4 or 1) and the custody is moved, the watchdog cannot read the installed job, decides `HOLD_UNSAFE` on every tick and queues no notice. | stops every later launch, silently | Brief 5.6: move the custody only when both job files are gone; otherwise leave it, retry once, and send the fault email from the session. | V |
| M8 | The Bash tool ends a foreground command after at most ten minutes; a cut-short harvest leaves a directory the next harvest refuses (exit 3); the brief's "not harvested" test then never clears. | delays the next arm | Brief 4.5: run the harvest as a background task and wait. Brief section 3 case 2: harvested means some `harvest-<plan id>*/harvest.json` exists; a directory without one is kept and the next run takes the next suffix. | S (code read) |
| PD-3 | The watchdog releases a launch that never started only while `night/` is empty. launchd creates `launchd.night.out` and `.err` at spawn (all 15 earlier windows have them), and the dead-man job's first daily start adds two more files, after which the release lapses until t0 + 26.6 to 30.4 h. The brief had no case for it. | delays the next arm (needs a driver that never starts or dies at startup) | Brief section 3 case 3: withdraw promptly, uninstall first. Optional code after block 5 in section 6 below. | S (code read) |
| PD-1 | The dead-man job's calendar has no date, so for a window this long its first daily start falls inside the chain (t0 + 5 h 28 min ALPHA, 6 h 08 min BETA, 2 h 22 min GAMMA): about 0.15 CPU-seconds outside the driver's tree. | none | Brief 4.1: expect the line, record its timestamp. The dated calendar is code after block 5. | S (code and arithmetic) |
| CE-2 | No step between Part A and an install read the interpreter's package versions, the model weights or the executed files against the seal; the arm records such a defect and goes on. The reference model `Qwen2.5-1.5B-Instruct-4bit` is hashed before a window only by runbook A3. No defect is present today. | excludes the window if a drift occurs | Brief 5.3: the desk seal check. Brief 5.1: A3's check 3, corrected, before each arm (3 s). The lens's own script `b5_desk_precheck.zsh` is not used: one check, and the one that takes H_claim as an argument. | V |
| CE-5 | The ledger names 116 older capture directories (iCloud Drive, six custody roots, `/Users/edr/night-g2a`) that every harvest re-reads; the brief's never-offload list did not protect them, nor the three model directories. A missing capture is a disclosed flag. | flag only | Brief 5.1: the list. Runbook A4: the full custody reading is no longer UNKNOWN (refusals none, head 402, 5 s). | S (catalog effect only) |
| SC-7 | The arm's pack check walks the pack directory on disk; `.DS_Store` and `__pycache__/` are git-ignored, so `git status` is silent and the arm records `pack.identity_mismatch`, which the harvest does not supersede. (`._*` files are not git-ignored, so those are visible.) | excludes the window (needs someone to open the folder in Finder) | Brief 5.3: remove the two names before the plan is written; the desk seal check reports any that remain. | V |
| SC-8 | The brief sent a cure of window-read code through "a new clone at the head the erratum names" without re-issuing the inventory; the first window from such a clone passes every check before it runs and is excluded after. The inventory generator is not tracked. | excludes the first window after a cure | Brief section 9: the cure commit is a new H_claim; generate the inventory; commit it alone as the new seal commit; landing test; new clone; desk seal check; the old clone is never edited or deleted (if moved, `--measurement-root`). Runbook A6: commit the generator and the desk seal check with the helpers. | V |
| WR-1 | The chain decides spares and the corpus retry from summary status only. A reference or corpus member that succeeded with an energy reading the eligibility test cannot use is never replaced. 3 of the 8 real v5 reference-family bundles (loaded desk) are such. After harvest change K-4 a window is lost on the references only if two of three at one endpoint are unreadable; the corpus half is untouched: three or more ineligible among twelve gives `neg8.bound_not_derived`. | excludes the window if the quiet-machine rate is high (corpus keeps 10 of 12 with probability 0.98, 0.89, 0.56 at rates 5, 10, 20 %) | No code change: the stage-1 ruling keeps window-time code as it is. Brief section 6: a window removed by `neg8.bound_not_derived` or `neg8.screen_failed` goes to a consult at once and is not re-armed unchanged. ALPHA-1 is the first measurement of the rate. | V |
| WR-4 | The driver's yield line counts planned run ids by status: a reference stage rescued by spares reads LOW (and sends a fault email), and a window whose members will all be excluded reads FULL. | flag only | Brief 4.1: decide only from the harvest. | S (partly) |
| AH-6 | A looping `fseventsd` makes every dwell interval dirty and the arm refuses at 2,700 s; the installed passwordless cure was not in the brief. | delays the arm by two arms of up to 45 minutes | Brief section 6, the NULL row: the restart command and the follow-up. | S (the script and its sudo rule exist; the log predicate was not run) |

### 4.3 Flag, not refuse

| Id | What | Disposition |
|---|---|---|
| M11 | The watchdog classes the CLI's own limit and logged-out messages as `generic_error`, so its retry ladder is the shorter one and its notice is mislabelled. | Flag, not refuse: no fix round. Runbook A10's check names it. Read from the eight patterns, not run. |

## 5. Code changes before the seal: the orchestrator decides

**None is required by a confirmed finding.** The list below is everything in the pre-mortem that touches code
and could matter before the head is frozen, smallest change first. "Window input" says whether the file is one
(tracked under `joulewise/`, `scripts/` or `configs/`, or `docs/phase_2/window_runbook.md`); a window input
cannot change in the clone after H_claim.

| Item | The smallest change | File | Window input? | Recommendation |
|---|---|---|---|---|
| SC-5 | Unknown until the shards run. So far two test-only fixes (`cff799a96`, `eb0a1fb37` on `lane/2026-10-07-ci-linux-fixes`). | so far `tests/test_g10_clock_step_control.py`, `tests/fixture_signatures.json`, `tests/test_fixture_orphan_census.py` | No (tests). A later shard failure may point into `joulewise/` or `scripts/`: yes. | **Hold H_claim until all twelve Linux shards and both exclusive jobs have run to their end on the candidate tree.** This is the one item that can force a window-input change. `strategy.fail-fast: false` on the lane's branch would show every failing shard in one round (`.github/` is not a window input). |
| M2 | A finished window is released also when `night/courier.json` exists (the driver's four courier attempts are over), with a `courier_failed` notice queued for the magistrate. Today a failed courier fences the machine until t0 + `window_max_s` + 4,800 s: 29.7 h after t0 for ALPHA, 20 to 24 idle hours, and no email. (Checked by the synthesizer in the code: `arm_retry.py:285-286`, `magistrate_watchdog.py:1242-1262`; the arithmetic by M1's verifier.) | `scripts/magistrate_watchdog.py` (the reads at lines 848, 926, 1260, 1282, 1287), its tests, and one registration sentence (line 1792, "A failed courier keeps the old dead-man timing") | Yes by path. But the watchdog runs from the canonical root, never from the clone. | Optional. Before the freeze it is cleanest (one tree, the registration sentence changes in the same pass). After the freeze it can still land on main alone (class ii of registration section 11 item 1: permitted on main, forbidden in the clone), with the registration sentence corrected by an erratum. Not needed for ALPHA-1 if runbook A9 reading 9 passes. It is worth having before BETA: a real courier has never run on a block-5 window, the Gmail path was blocked earlier today, and one past courier used 296 of its 300 seconds. Until then the fallback is an owner action in the arm notice (brief 5.4, marked for the orchestrator to keep or delete). |
| PD-3 | `_night_records` ignores launchd's four log files, so a driver that died at startup is released at t0 + 900 s. | `scripts/magistrate_watchdog.py` (lines 930-942) | Yes by path; runs from the canonical root. | Optional, with M2 or after block 5. Low probability: preflight and the dry arm pass under launchd's environment. |
| WR-1 | In the chain's spare helper, count a reference as succeeded only when its stored eligibility flag is not false. | `joulewise/b5/chain.py` (lines 863-893) | Yes, and it executes during a window. | **Not taken.** The stage-1 ruling keeps window-time code unchanged before the freeze and cures the reference half in the harvest (K-4). The corpus half stays an accepted risk with a brief sentence. Listed so that the decision is explicit. |

Already ruled elsewhere and still to land before H_claim, as a reminder because each is a window input by path:
the catalog's cell minimum of 5 and the allowlist changes (`lane/2026-10-07-seal-rulings`, C-1, K-1 to K-3); the
catalog's status note rewritten to a sentence true before and after the seal (ruling F7). Not a window input but
needed in the clone's commit: the `NIGHT_HANDBACK.md` rewrite (M3, runbook A0 item 3).

## 6. Code after block 5

| Id | Change | File | Note |
|---|---|---|---|
| PD-1 | Give the dead-man calendar its month and day when its time is more than a day after the install. | `joulewise/night_agent_install.py` (lines 657-659) | Removes the in-window start and with it PD-2's only known trigger. |
| PD-2 | An in-window census line whose process has exited is probed once more and then flagged, not treated as an agent. Verified in a real race: the line is kept only when `pgrep` starts 4 to 16 ms before the process exits, about 0.05 % per dead-man start inside a chain. | `joulewise/agent_identity.py`, `joulewise/b5/driver.py` | Accepted for block 5. Effect if it happens: stops collection. |
| M10 | Catch and retry the supervisor's process listing and raise its limit from 1 s to 5 s. Verified: a timeout ends the supervisor; it matters only if the magistrate is still alive at t0 − 90 s; worst case one refused arm. | `scripts/magistrate_watchdog.py` (lines 250-257, 2480-2501) | The limit fired once (2026-10-05, during a session start). |
| C2 (optional) | Release a window that never started a chain on plan-scoped evidence alone (no driver, no process naming the custody root). | `scripts/magistrate_watchdog.py` | Removes the day-long hold after a census refusal. |
| SC-7 (optional) | The arm's pack check skips the OS metadata names the harvest already skips. | `joulewise/flags/collect.py` (lines 293-319) | "Flag, not refuse" for a stray `.DS_Store`. |
| HN-4 | Skip the verdict-row replay when no consumption session is given, or give it one. | `joulewise/b5/harvest.py` | Desk code; the harvest lane may take it at any time. Saves about 15 minutes per harvest. |

## 7. Verdicts: what the verifiers changed, and what was not refuted

**No finding was refuted.** Twenty-five of the fifty-five were sent to a verifier (every one whose stated effect
stops, nulls or excludes); all came back CONFIRMED. The verifiers corrected the statement of fourteen, mostly by
lowering or narrowing the effect, and the tables above use the corrected wording:

- **C1, M4, C4:** "nulls the window" is a zero-capture refusal of about a minute; the cost is the repetition
  and C2's hold. C4 is wider than stated: anything left running when the magistrate exits by itself escapes.
- **PD-4:** not a nulled window but an arm-time refusal for later windows; ALPHA-1 passes today.
- **AH-2:** member-level, not window-level. The "0.19 CPU-s/s for 33 minutes" was a mean across a gap between
  two snapshots; the real shape is a 3 to 4 minute batch.
- **AH-3:** member-level; and Terminal cannot be quit before the `/exit`.
- **M10:** one refused arm, and only if the magistrate ignored the cooperative request.
- **PD-2:** 0.05 % per dead-man start, not 0.1 %.
- **SC-3:** the window runs 24 to 28 hours of programmed span before the harvest sees the edit, not 5 to 9; the
  landing test does not catch an edit in a later commit; the desk seal check does.
- **SC-8:** a moved clone can still be harvested with `--measurement-root`; only an edited or deleted one cannot.
- **WR-1:** after harvest change K-4 one unreadable reference no longer removes the window; two at one endpoint
  do; the corpus half is unchanged.
- **WR-3:** the instruction exists in the older tracked runbook; a missed launchd calendar job runs once on wake.
- **C3:** worse than stated: the Claude app starts its `claude` binary on opening, with no session.
- **M1:** the hold comes first and the failing launches after it; a stripped environment without `USER` reports
  "Not logged in", so the smoke must run in the launchd job's real environment.

Resolved or dropped before the synthesis: SC-1 (cured by the merge); the clone-and-env lens's first-pass CE-6
(the registration's "fast-forwarded to H_claim" sentence; its correction is queued in
`../seal-land/REGISTRATION_FACTS.md` line 105).

The thirty findings that were not sent to a verifier (stated effect "delays the arm", "flag only" or "none")
are marked in the tables: **S** where the synthesizer checked the code or the machine, with what was and was
not run; **L** for SC-1, which the merge resolved; "unchecked" for HN-4. Of the nineteen whose stated effect was
"delays the arm", eighteen are checked (C2, AH-5, AH-6, CE-1, CE-4, PD-3, HN-2, HN-3, HN-5, M2, M3, M5, M8,
M12, M13, SC-4, SC-5, SC-9: by code read, by a command run on this machine, or both, as each row says; M2's row
is in section 5) and one is not (HN-4, a timing that was not re-run). Partly checked: CE-5 (only the catalog effect), WR-4 (only that the driver
never mentions spares), M7 (the relaunch record, not the stand-down ladder), M9 (the label, not GitHub's
notification rule), AH-6 (the script and its sudo rule, not the log predicate or the Wi-Fi step).

## 8. Questions only the orchestrator or Ed can answer

**For Ed**

- E-1 (blocks the release). Which Claude account runs the block, when does the present one stop, and will the
  Mac be logged in to the lasting one with its Gmail connector before the stop ref is deleted? (M1)
- E-2. May the magistrate quit a desktop application (Claude, ChatGPT, T3 Code, Chrome) it finds open on the
  measurement Mac? May it end an interactive `claude` or `codex` session it did not start, after one email has
  gone unanswered? Without the second, a forgotten session stops the block until a person closes it. (C2;
  brief 5.1, `FILL[MAY-END-FOREIGN]`)
- E-3. Does a GitHub issue opened by his own `gh` account reach him? If not, is "no deliverable notice, no
  install" the rule he wants for an arm? (M9; brief section 8)
- E-4. With a 30-minute lead he has about ten minutes to answer NO, and a NO is acted on only if it arrives by
  about t0 − 15 min. Is that what he wants, or a longer lead? (M7; runbook open question 5)
- E-5. Optional, at the keyboard: `sudo pmset -c displaysleep 1` before the block. (WR-2)
- E-6. Should the arm notice carry a one-line command with which he can release the Mac by hand when no result
  email arrives? It is an owner action, offered only because no agent can run while the machine is fenced. (M2)

**For the orchestrator**

- O-1. Hold H_claim until CI's twelve Linux shards and exclusive jobs have completed? (SC-5)
- O-2. The watchdog change of M2 (and PD-3): before the freeze, on main after it, or not for block 5?
- O-3. `NIGHT_HANDBACK.md`: rewritten at or before H_claim, or in the record commit with the clone checked out
  there? (M3)
- O-4. Is the harvest lane pinned before ALPHA-1's arm? That decides the harvest addendum, the desk root's
  commit and the RUN_STATE line `B5-ARM-RELEASED:` (`alpha beta gamma`, or `alpha`). If it is not, the magistrate
  relaunches quietly every five to ten minutes through the gap (about 0.6 USD of usage each); accept that, since
  the brief forbids a stop ref as a pause? (M14)
- O-5. A 30-minute quiet census before the arm (`b5_quiet_census.py`, sha256 `27bc8485…8e13`, tested for four
  intervals), or ALPHA-1 as the measurement? The synthesis assumes the second: at the ruled cell minimum the risk
  is small, and the census needs half an hour with no agent alive between Ed's `/exit` and the release, which
  only an unrehearsed detached script could arrange. (AH-1)
- O-6. The desk root's path (proposed `/Users/edr/night-custody/desk/JouleWise-desk-b5`) and who writes the
  harvest addendum. (SC-2)
- O-7. Which harvest outputs may the magistrate, and a consult seat it convenes, open to find the cause of a
  lost window, now that change T-32 restricts three `derived/` files? The brief reads the two stdout lines,
  three fields of `harvest.json`, `derived/code-identity.json`, `night/hazard_result.json` and, for a consult,
  the monitor's contention journal.
- O-8. Issues #416 and #421: close with the evidence, or keep the RUN_STATE sentences? (M13)
- O-9. The four rehearsal rigs under `/private/tmp` (`reh1`, `reh2`, `reh3`, `dd5-isreview`, about 259 GiB by `du`)
  are named by nothing the block reads. Delete them? (CE-4)
- O-10. Two things the lenses could not exercise and that have no cure after the freeze: GAMMA's verdict writer
  and its G3 recompute have never run on real bundles at any head, and the writer is the clone's own program
  (`run_campaign.py --whole-window-verdict`), so a defect in it is collection code. One short real-model GAMMA
  rehearsal with a valid closing calibration, harvested in the registered order, would exercise both. Worth the
  time before the seal?
- O-11. The auto-mode permission sentences that cover the science pipeline name the block-1 programs
  (`harvest_window.py`, `land_window_records.py`), not the block-5 ones. On 2026-10-05 the classifier twice
  blocked a headless magistrate. Whether it would pass `write_b5_window_plan.py`, the installer and the harvest
  is untested. A settings change is Ed's or the orchestrator's, not an agent's.

## 9. Suspicions the lenses could not test (not findings)

- A top-up charge at the battery's 80 % hold: raw capacity fell 94 mAh in 34 hours and the resume level is
  unknown; a charge inside a calibration capture removes the window. (arm-hazards)
- G10 has never run on the real clock; afterwards the frequency word may exceed the gate and BETA's arm would
  refuse until the brief's redraw. (window-run)
- Spotlight indexes the data volume, so the new runs parent `/Users/edr/night-b5` and a clone made minutes before
  an arm may draw `mds` activity; a parent whose name ends in `.noindex` would be skipped (not proven).
  (arm-hazards, window-run, plans-and-driver)
- The pin advance reads every ledger-named capture with no time limit; an iCloud-evicted capture is downloaded
  on read and could hang with the network down. Storage optimisation is on. (clone-and-env)
- `charset-normalizer 3.4.8` is yanked on PyPI; a later relock depends on PyPI still serving it. (clone-and-env)
- A real `launchctl bootstrap`, a real launchd start of the driver and of the dead-man job, network time
  switched off for real, and the courier on a block-5 window stay unexercised until ALPHA-1. (several)
- The second account's tier, model alias, auto mode and connector; what `claude -p` returns after a lapse.
  (magistrate)
- After the block closes the watchdog keeps starting a quiet relaunch every five to ten minutes. (magistrate)
- Every member of the smoke window carried `calibration.refit_cache_miss` with reason `verdict_schema_mismatch`
  (disclosed only). (harvest-and-next-arm)
- The hand-off reaper (runbook A11's fallback) was read from code and last run on 2026-09-06.
- Whether the interactive session's background shells end with it. (census)

## 10. What the synthesis changed, and what it did not do

**Files written** (all in this directory):

- `PREMORTEM.md` (this file).
- `POST_SEAL_RUNBOOK.md`: revised in place. New steps A0 (before the freeze: CI, the registration probe, the
  handback), A5b (the desk root and a harvest-side rehearsal) and A11 (the session ends). Changed: A1 (seal-landing
  checks), A2 (the clone against H_claim, the sizing digest, the inventory's head), A3 (the Homebrew pin, the
  corrected check 3), A4 (the custody reading's expected result), A5 (four helpers, the fixed-values file, the
  desk seal check on each scratch plan), A6 (the bench files, the prompt's four lines, the harvest addendum, mail
  and issues, the check by path class), A7 (edit #489, merge commit), A8 (three more checks), A9 (disk first;
  eleven readings), A10 (email, then release), B1 to B4 and B-after (the commands that changed). Every seal-landing
  fill is resolved. Every zsh block passes `zsh -n`.
- `MAGISTRATE_BRIEF_DRAFT.md`: rewritten in place with every brief cure. Section 4.5 is marked PENDING THE JUDGE
  with both variants; sections 5.1 and 8 carry the two PENDING ED decisions.
- `RUN_STATE_BLOCK_DRAFT.md`: rewritten in place (H_claim and the seal commit, the desk root and the addendum,
  the line `B5-ARM-RELEASED:`, the order after a window, the paragraph on instructions that predate the
  hand-off).
- `b5_agent_check.py` (new, sha256 `5d6fac1279430998cc3219a73d4a02914479443a342ebe594ad01c364d14080d`): the agent
  check used in runbook A9 and brief 5.1, 5.5 and 5.7. It replaces the census lens's inline one-liner, finds the
  session it runs inside by itself, and also lists the session's own seats. Tested with stand-in processes.

**Commands the synthesizer ran:** read-only git, `gh` listings, one read-only Gmail search (metadata only),
`df`, `pmset -g`, `launchctl print`, `sudo -n -l` listings, `osascript` for the foreground list; the corrected
identity-pin comparison on the clone-and-env lens's scratch clone; short stand-in processes named
`codex-standin-*` (each under 15 s, none left). Scratch: `/private/tmp/w1007-premortem-synth` (small; deletable).

**Not done:** nothing armed, installed, loaded or unloaded; no email sent; no message marked read; no issue or
label changed; no git write in any repository; no machine setting changed (`brew pin` and `pmset` are written
as steps, not run); no claim-window data opened. The registration's text was not edited; one sentence of it
(line 1792) changes only if O-2 is answered "before the freeze".
