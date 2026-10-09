# Consult: block 5, ALPHA attempt 3 was collected and is again not usable for claims, this time through the NEG-8 corpus alone. What should the next arm be?

You are one of two blind seats. The other seat has the same brief and you do not see its answer. You are
asked for your own design judgment and you have explicit license to disagree with anything this brief
suggests. The magistrate (the lead session) decides after reading both answers.

## Hard rules for this seat

- Read-only. Write no file in any repository, custody root, runs root or archive. Run no git command that
  changes anything. Do not run the repository-wide test suite (`unittest discover`, `shard_tests.py`); you
  need no test run at all.
- No Homebrew command of any kind (`brew install`, `upgrade`, `reinstall`, `uninstall`, `cleanup`).
- No measurement work and no command that loads the machine for more than a few seconds.
- Do not start another agent, and do not call Claude or Codex by any route.
- The owner's address and name go into no network request made by you: not into a URL, a header or a
  payload of `curl`, `wget`, a Python HTTP call or a web tool, not into a `gh` call, and not into a
  `git config` line. A service that asks for a contact address gets none. They are also written into no
  file. You need no network access for this task.
- Blinding. The block is blinded until its release event: nobody may learn a measured energy, power or
  duration of a claim window. Your answer carries structure only: no energy, power or duration of a
  member, no member's name, no error text quoted from a restricted file. The passage below says exactly
  which files of the window you may open. It is binding on you, word for word.

### The passage (from the magistrate brief, section 6; "you" is the magistrate, and it binds the seat the same way)

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

For this consult you are a consult seat in the sense of that passage, so you may also read the monitor's
contention journal. You may not run a program over any restricted file, even one that prints only
integers. If a structural count from a restricted file would settle your answer, do not compute it: write
the exact program (it must print integers and code names only) in your answer under "Counts I would want",
and the magistrate will decide whether to run it.

## What happened

Measurement block 5 is three unattended windows on one Mac (packs ALPHA, BETA, GAMMA, in that order), run
under a sealed registration. A pack is attempted until one attempt is *claim-usable*: the harvest (the desk
program that checks a finished window's bytes) found nothing that removes the whole window, and every
reported quantity keeps at least 5 of its 10 planned units of each kind. ALPHA has now had three attempts
and none is claim-usable. All three ran from the same sealed clone; no file a window reads has changed.

**Attempt 1** (`v5-b5-alpha-a1-20261008T2201Z`): chain ran its whole span. Harvest `COLLECTED`, not
claim-usable, window reasons `cell.below_minimum` and `neg8.bound_not_derived`. The NEG-8 corpus stage
(12 members; the bound needs 10 clean ones) had 10 of 12 succeed at run time, so the chain ran no retry,
and the harvest then dropped at least one of the 10 for a physics-in-span code. Contention journal: 183 of
1,975 ten-second intervals had an outside process above the registered limit of 0.05 CPU-seconds per
second; `mediaanalysisd` in 77 (alone in 72), `corespotlightd` in 51 (alone in 43), `fseventsd` in 14.
A two-seat consult and a cold ruling followed: `alpha-a1-consult/RULING.md` (path below). Its cure, a
`launchctl bootout` of the two photo-analysis agents that are listed as disabled but still running, was
refused by the operating system (rc=150, System Integrity Protection). Attempt 2 was armed unchanged.

**Attempt 2** (`v5-b5-alpha-a2-20261009T0515Z`): the arm refused before any chain (`NULL`): its contention
dwell never found 180 clean seconds because `fseventsd` was looping at a full core. Cured by restarting
that daemon and toggling Wi-Fi once.

**Attempt 3** (`v5-b5-alpha-a3-20261009T0644Z`), the subject of this consult:

- t0 2026-10-08 23:44 PDT; the arm passed all six hazards (decision `GO`, no reason, nothing unmeasured);
  the chain exited 0 at about 05:06 PDT on 2026-10-09; closing calibration done.
- Driver yield `LOW`, fault reasons `yield_low` and `bound_derivation_failed`, driver flag codes
  `network_time.off_output` and `yield.stage_low`. 119 members planned, 119 bundles present, 115
  succeeded. By stage (succeeded of planned, `min_valid`): bound collection (the NEG-8 corpus) **9/12
  (10)**; reference start 2/3 (2); decode absolute 10/10; decode ABBA 01-05 20/20; decode ABBA 06-10
  20/20; reference midpoint 1/1; prefill p2048 absolute 10/10; prefill p2048 ABBA 01-05 20/20; prefill
  p2048 ABBA 06-10 20/20; reference end 3/3.
- The chain's stage list in `night/hazard_result.json` shows, in order: `alpha-bound-collection` rc 1;
  `alpha-bound-collection.retry-decision` rc 0; `alpha-bound-collection.retry` rc 1;
  `alpha-bound-derivation.corpus` rc 0; `alpha-bound-derivation` rc 2; `alpha-reference-start` rc 1;
  `alpha-reference-start.spares-decision` rc 0; `alpha-reference-start.spares` rc 1; every science stage
  rc 0 except `alpha-science-prefill-p2048-abba-06-10` rc 1 (20 of 20 succeeded all the same). So the
  corpus was short after its first pass, its one retry ran, and it was still at 9. `neg8_corpus` in the
  same file: 12 listed, 9 kept, pruned. `yield_tripwire`: 131 attempts seen, no pre-bundle refusal
  flagged.
- Harvest, from the pinned harvest program at commit `7e6158d669cbb6fb35761aee18abf363f07c5d36`, exit 0:
  verdict `COLLECTED`, `claim_usable` false, window reasons **`neg8.bound_not_derived`** and
  **`neg8.screen_failed`**, `faults` empty. `cell.below_minimum` is absent this time: every reported
  quantity kept its units. Harvest yield: planned 119, present 119, raw-valid 119, succeeded 115; roster
  stage `neg8_bound` 9/12, `start_reference` 2/3, every other stage full.
- `derived/code-identity.json`: the window ran the sealed code; no changed window input.
- Contention journal of attempt 3 (the magistrate's tally, by the same program that reproduces the cold
  judge's attempt-1 figures): 1,913 intervals, 173 with an outside process over the limit;
  `mediaanalysisd` in 73 (alone in 72), `find` in 31 (alone in 18), `signpost_reporte` in 17 (alone in
  14), `fseventsd` in 13, `mobileassetd` in 12, `PerfPowerService` in 10, `runningboardd` in 9, `mds` in
  8, `corespotlightd` in 8 (alone in 3), `airportd` in 7, `mds_stores` in 7, `deleted` in 7.
- The clock-instrument count the registration's END STATE rule uses, over attempts 1 and 3: 233 recorded
  statuses, 2 not bounded. Not END STATE.

What is not known and what you are asked to find out from the code: **why three corpus members did not
succeed at run time, twice in a row within one window** (first pass and retry). The magistrate has not
established which run-time condition marks a corpus member as not succeeded (an idle-admission gate that
gives up, a per-member contention or thermal check, a model or runner error, something else), nor whether
that condition is a physical one or a deterministic one that the next window would meet again whatever
the machine state.

## The machine, and what the owner has answered

- `com.apple.mediaanalysisd` (pid 98055) and `com.apple.photoanalysisd` (pid 81746) are still running,
  listed as disabled for the login session; the disable takes effect only at the next login.
- The owner was asked whether the Mac may be restarted between windows and whether
  `com.apple.corespotlightd` may be disabled. He answered yes to both, the restart on the condition that
  work keeps going afterwards.
- A restart cannot be done unattended on this Mac: FileVault is on and there is no automatic login, so
  after a restart the machine waits at the unlock screen for the owner's password, and the watchdog (a
  launchd job in the user's session, `RunAtLoad` true, every 300 s) starts again only after he logs in.
  The magistrate has no passwordless `shutdown`, `reboot` or `fdesetup authrestart`. So a restart is the
  owner's act at the keyboard, at a time nobody can schedule; he reads email.
- The magistrate session's permission check refused `launchctl disable gui/501/com.apple.corespotlightd`
  when it tried; the owner can run it himself.
- Uptime is 20 days. Network time is OFF by design (the clock check measures drift directly). The Mac is
  dedicated to this work; windows run back to back at any hour.

## Where things are (absolute paths)

Evidence you may open:
- `/Users/edr/night-archive/harvest-v5-b5-alpha-a3-20261009T0644Z/harvest.json`: only the keys `verdict`,
  `claim_usable`, `exclude_window_reasons`, `yield`, `faults`, `harvest_checkout`. Read them with a program
  that prints those keys and no others; do not print the file.
- `/Users/edr/night-archive/harvest-v5-b5-alpha-a3-20261009T0644Z/derived/code-identity.json`
- `/Users/edr/night-custody/v5-b5-alpha-a3-20261009T0644Z/night/hazard_result.json`
- `/Users/edr/night-custody/v5-b5-alpha-a3-20261009T0644Z/hazards/arm.json`
- `/Users/edr/night-custody/v5-b5-alpha-a3-20261009T0644Z/hazards/monitor/contention.jsonl` (process names
  and CPU shares; each `interval` record's `values.outside_over_limit` lists the offenders, and
  `values.interval` and `started`/`finished` give its time)
- The same five files of attempt 1, under `/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261008T2201Z/`
  and `/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z/`, and attempt 2's `night/hazard_result.json`
  and `hazards/arm.json` under `/Users/edr/night-custody/v5-b5-alpha-a2-20261009T0515Z/`.
- Plan-time files, which are not restricted: each custody root's `night_plan.json`, `window.env`,
  `chain.zsh`, and `/Users/edr/night-plan-staging/<plan id>/`.
- The attempt-1 consult papers: `/Users/edr/night-archive/b5-consults/alpha-a1/` (`RULING.md`,
  `sol-consult.md`, `opus-consult.md`).

Code and the sealed documents, in your working directory (a worktree at the harvest program's commit,
which contains the sealed tree; treat it as read-only):
- `configs/campaigns/v5_claim_25g83/registration_block5.md` (sealed registration; sections 0.8, 0.9, 0.12,
  4.2, 4.3, 5.2, 5.3, 5.7, 6.3 to 6.6, 6.9, 7.2 to 7.6, 10, 14)
- `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`, `flag_catalog.json`
- `joulewise/b5/harvest.py` (where both codes are emitted), `joulewise/b5/chain.py` (the corpus retry,
  `NEG8_RETRY_MINIMUM`, the bound derivation stage), `joulewise/whole_window.py`, the campaign runner and
  controller that decide whether a member succeeded, `joulewise/hazards/`, `scripts/hazard_monitor.py`
- The procedure: `/Users/edr/code/JouleWise/docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`,
  sections 6 and 9.

Everything else under the custody roots, the runs roots `/Users/edr/night-b5/`, and the archives'
`derived/` (other than `code-identity.json`), `sources/` and `withheld/` is closed to you. That includes
the corpus members' own run records and logs: if a member's recorded failure reason is the one fact that
would settle the cause, do not read it; write, under "Counts I would want", the exact program that would
print reason-code names and integers only (no member name, no error text, no measured value), and the
magistrate will decide whether it may run.

## The questions

1. **Cause.** From the code, state exactly (a) which run-time conditions make a NEG-8 corpus member end
   as not succeeded, and which of them the single stage retry can and cannot repair; (b) which conditions
   make the harvest emit `neg8.bound_not_derived` and `neg8.screen_failed`, and whether in attempt 3 both
   follow from the corpus being at 9 or the second has a cause of its own (the start reference was 2 of 3
   after its spares ran). Then use the contention journal: do the over-limit intervals cluster at the
   start of the window where the corpus stage runs; which processes are in them; is `find` a leftover of
   ours or an operating-system job (name what starts it if you can tell without loading the machine).
   Say what the permitted evidence cannot distinguish.
2. **Would the next unchanged window meet it again?** Three attempts, two chains, both lost through the
   corpus (10 kept with zero margin, then 9). Give your estimate of the chance that an unchanged attempt 4
   is claim-usable, and what it rests on.
3. **Recommendation.** Choose one and defend it:
   (a) arm ALPHA attempt 4 unchanged, now;
   (b) arm attempt 4 after a cure that changes nothing a window reads. Two candidate cures are on the
       table and you may propose others: the owner's restart (which makes the two existing disables
       effective, and the Spotlight disable if he runs it), which costs an unknown wait for a person; and
       anything the magistrate can do alone now. Say whether to hold the arm for the restart, or to arm
       unchanged meanwhile and let the owner restart between windows whenever he can (a restart during a
       window ends that window). Name the exact commands and the check that shows the cure took;
   (c) a change to something a window reads or to a registered threshold, catalog effect or minimum: for
       instance a larger corpus, more than one corpus retry, a retry that waits for a clean interval, or a
       different minimum for the bound. This route is expensive: a threshold or catalog change needs a
       prospective cold erratum before the next arm (registration section 10), and a change to code a
       window executes supersedes the block, because completed windows executed it (registration section
       7.5): a new sealed clone, and the block restarts at ALPHA, which in practice costs nothing in data
       here because no ALPHA attempt is claim-usable. Recommend it if the physics or the arithmetic of a
       12-member corpus that needs 10 requires it, and then say what the new rule should be and why it is
       better science, not only what is cheaper. If you recommend it, say whether (b) should run in
       parallel while the change is built and gated;
   (d) the harvest program or the chain's bound derivation is at fault (it removed a window the
       registration would keep): name the defect, the file and the lines;
   (e) END STATE.
4. **What you are least sure of**, and the one additional structural fact that would change your answer.

Rule carried in every brief on this path: only a directly measured physical hazard or a number-integrity
condition may stop collection or exclude data. A rule that is only about how something is recorded is a
flag, not a refusal. Old rules do not bind the science: if the evidence shows a registered limit or a
registered design choice is wrong for this machine, say so and say what the right one is; the gate for
changing it is a cold erratum, and "the existing rule says" is never the reason a worse rule stays.

## What to return

Plain findings, not prose for a reader outside the project. Sections: Cause; Recurrence; Recommendation
(one letter, then the steps); Least sure; Counts I would want (optional). Cite file paths and line numbers
for every claim about code, and journal line counts or integer tallies for every claim about contention.
