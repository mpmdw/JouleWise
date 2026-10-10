# Consult: block 5, BETA attempt 1 was collected and is not usable for claims; the one window-removing code is `neg8.screen_failed`, with the bound derived. What should the next arm be?

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
reported quantity keeps at least 5 of its 10 planned units of each kind.

**History.** Under the first seal ALPHA had three attempts, none claim-usable; two chains lost the NEG-8
corpus (12 reference runs at the start of a window, from whose spread the drift bound is computed; the bound
needs 10) to idle-admission aborts. A cold erratum enlarged the corpus to 18 members (bound from the first
12 clean ones in committed order, minimum 10 unchanged), under a second seal and a new measurement clone.
Under the second seal, **ALPHA attempt 1** (`v5-b5-alpha-a1-20261009T2312Z`, t0 16:12 PDT, chain 5 h 50 min)
was claim-usable: 125 planned, 123 succeeded, no window reason, corpus 18 collected, 12 kept, none dropped;
contention journal 165 of 2,081 intervals over the limit.

**BETA attempt 1** (`v5-b5-beta-a1-20261010T0742Z`, pack `d117_floor_qwen3-8b_v5`), the subject of this
consult. It ran from the same sealed clone as ALPHA attempt 1; no file a window reads has changed.

- t0 2026-10-10 00:42 PDT; the arm decided `GO` with no reason; the chain exited 0 at 06:45 PDT (6 h 03 min);
  the closing calibration ran and the bracket session is finalized (ledger pin advanced, sequence 432 to
  442).
- Driver yield `LOW`, fault reason `yield_low` only (`bound_derivation_failed` false, `post_bracket_failed`
  false), driver flag codes `network_time.off_output` and `yield.stage_low`. 125 members planned, 125
  bundles present, 117 succeeded. By stage (succeeded of planned, `min_valid`, local time the stage ended):
  bound collection (the NEG-8 corpus) 18/18 (10) 01:38; reference start 3/3 (2) 01:59; decode absolute
  10/10 02:24; decode ABBA 01-05 19/20 03:16; decode ABBA 06-10 19/20 04:06; reference midpoint 1/1 04:09;
  prefill p2048 absolute 10/10 04:35; prefill p2048 ABBA 01-05 20/20 05:28; **prefill p2048 ABBA 06-10
  15/20 (16) 06:31, status `LOW`**; **reference end 2/3 (2) 06:45**.
- The chain's stage list (23 entries) has rc 1 on five: the three science stages that lost members,
  `beta-reference-end`, and `beta-reference-end.spares` (after the end reference lost a member the spares
  decision returned 0 and the spare stage ran and returned 1). Everything else returned 0, including both
  calibration captures, the corpus stage and `beta-bound-derivation`. `neg8_corpus` in
  `night/hazard_result.json`: 18 listed, 18 kept. `yield_tripwire`: 125 attempts seen, no pre-bundle
  refusal flagged; the driver's shared-cause code `stage.members_refused_pre_bundle_identical` is absent.
- Harvest, from the pinned harvest program at commit `224a264c5faaae90cdf56118df37e773a932700b`, exit 0:
  verdict `COLLECTED`, `claim_usable` false, **one window reason, `neg8.screen_failed`**, `faults` empty.
  `cell.below_minimum` and `neg8.bound_not_derived` are absent. Harvest yield: planned 125, present 125,
  raw-valid 125, succeeded 117; roster stages `02_…decode_abba_blocks_01_05` 19/20, `03_…06_10` 19/20,
  `06_phase_prefill_p2048_abba_blocks_06_10` 15/20, `end_reference` 2/3 (3 present, 3 raw-valid),
  `start_reference` 3/3, `midpoint_reference` 1/1, `neg8_bound` 18/18, the rest full.
- The corpus under the cap rule (`derived/neg8-corpus-physics.json`, read by the magistrate with a program
  that prints counts only): 18 collected, 18 bound, 1 dropped at the harvest, 12 kept, 5 beyond the cap,
  minimum 10, `bound_derived_from` `collected_subset`, `clean_bound_validated` true, no problem listed. So
  the bound exists; unlike the first seal's attempt 3, the screen failure does not follow from a missing
  bound.
- `derived/code-identity.json`: the window ran the sealed code; no changed window input.
- The whole-window verdict file exists in the claim runs root (not opened).
- Contention journal (the magistrate's tally; names and integers only): 2,152 ten-second intervals, 228
  with an outside process above the registered limit of 0.05 CPU-seconds per second. Intervals containing
  each process (alone in): `XProtectRemediat` 77 (61), `mediaanalysisd` 76 (72), `mobileassetd` 13 (2),
  `PerfPowerService` 12 (0), `runningboardd` 12 (0), `corespotlightd` 11 (9), `cloudd` 11 (2), `mds` 11 (0),
  `trustd` 10 (0), `deleted` 8 (0), `duetexpertd` 8 (2), `syspolicyd` 8 (6), `triald` 7 (3), `mds_stores` 6
  (4), `loginwindow` 5 (5). By the stage each interval ended in (over-limit of all): bound collection 33
  of 315; reference start 7 of 124; decode absolute 5 of 149; decode ABBA 01-05 9 of 310; decode ABBA 06-10
  9 of 302; reference midpoint 1 of 19; prefill absolute 12 of 156; prefill ABBA 01-05 25 of 316; prefill
  ABBA 06-10 **114 of 379**; reference end 13 of 82 (most frequent there: `syspolicyd`, 7). All 77
  `XProtectRemediat` intervals lie between 05:40 and 06:00 PDT. `XProtectRemediat` did not appear in the
  ALPHA attempt 1 journal (that window ran 16:12 to 22:02 PDT).
- The clock-instrument count of the registration's END STATE rule, over the four attempts that started a
  chain: 477 recorded statuses, 2 not bounded. Not END STATE.

What is not known, and what you are asked to find out from the code and the permitted evidence: **which
branch of the harvest emitted `neg8.screen_failed` here.** The candidates the magistrate can see from the
registration (sections 6.5 and 0.12, and the text near lines 1172, 2915 and 4107 of the sealed
registration) are: (i) too few usable references at an endpoint (the screen needs at least 2 at the start
and 2 at the end; the end stage had 2 succeed at run time, so one more loss at the harvest, for instance a
physics-in-span drop of one of the two, would leave 1); (ii) the screen ran and the start-to-end drift of
the reference workload exceeded the bound, which is the screen doing its job on a machine that really
drifted; (iii) the stored verdict's bracket was absent, not passed or carried conditions and the survivor
re-screen did not run or did not pass for a reason of its own; (iv) a harvest or verdict-writer defect.
(i) and (ii) are physical outcomes of this window; they differ in what the next window should expect.

## The machine, and what the owner has answered

- `com.apple.mediaanalysisd`, `com.apple.photoanalysisd` and `com.apple.corespotlightd` are still running.
  The first two are listed as disabled for the login session; the disable takes effect only at the next
  login. The owner was asked on 2026-10-09 to run `launchctl disable gui/501/com.apple.corespotlightd` and
  to restart the Mac when convenient; the Mac has not been restarted (boot time 2026-09-18). No step waits
  for him.
- A restart cannot be done unattended on this Mac: FileVault is on and there is no automatic login. The
  magistrate has no passwordless `shutdown` or `reboot`. Its passwordless `sudo` covers only a restart of
  `fseventsd`, the two network-time commands and `powermetrics`. The session's permission check refuses
  `launchctl disable` of an Apple agent; `launchctl bootout` of the photo-analysis agents is refused by
  System Integrity Protection (rc=150).
- A macOS job walks `/tmp` at 00:00 local every day; `/private/tmp` still holds about 5.2 million entries
  of agent scratch (the session's permission check refused the bulk move), so no window is armed whose
  chain is expected to be running at 00:00 local: t0 lies between 00:10 and 17:15 local.
- An arm waits 60 minutes, display asleep, after any daemon restart, Wi-Fi toggle or owner login.
- Network time is OFF by design (the clock check measures drift directly). The Mac is dedicated to this
  work; windows run back to back at any hour. Firefox was open, idle, through this window (the owner's;
  the magistrate may not quit it); it does not appear in the journal's over-limit tally.

## Where things are (absolute paths)

Evidence you may open:
- `/Users/edr/night-archive/harvest-v5-b5-beta-a1-20261010T0742Z/harvest.json`: only the keys `verdict`,
  `claim_usable`, `exclude_window_reasons`, `yield`, `faults`, `harvest_checkout`. Read them with a program
  that prints those keys and no others; do not print the file.
- `/Users/edr/night-archive/harvest-v5-b5-beta-a1-20261010T0742Z/derived/code-identity.json`
- `/Users/edr/night-custody/v5-b5-beta-a1-20261010T0742Z/night/hazard_result.json`
- `/Users/edr/night-custody/v5-b5-beta-a1-20261010T0742Z/hazards/arm.json`
- `/Users/edr/night-custody/v5-b5-beta-a1-20261010T0742Z/hazards/monitor/contention.jsonl` (process names
  and CPU shares; each `interval` record's `values.outside_over_limit` lists the offenders, and
  `started`/`finished` give its time)
- The same five files of the second seal's ALPHA attempt 1, under
  `/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261009T2312Z/` and
  `/Users/edr/night-custody/v5-b5-alpha-a1-20261009T2312Z/`, for comparison.
- Plan-time files, which are not restricted: each custody root's `night_plan.json`, `window.env`,
  `chain.zsh`, and `/Users/edr/night-plan-staging/<plan id>/` (but not `harvest.stdout` or `harvest.stderr`
  there, which can quote a data value).
- Earlier consult papers: `/Users/edr/night-archive/b5-consults/alpha-a3/` (`RULING.md`, `sol-consult.md`,
  `opus-consult.md`) and the erratum's ruling
  `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/corpus18-erratum/RULING.md`.
- The window records:
  `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/seal2-beta-a1-window.md` and
  `seal2-alpha-a1-window.md`.

Code and the sealed documents, in your working directory `/Users/edr/code/JouleWise-wt-harvest-cap` (a
worktree at the pinned harvest program's commit, which contains the sealed tree; treat it as read-only):
- `configs/campaigns/v5_claim_25g83/registration_block5.md` (sealed registration; sections 0.8, 0.9, 0.12,
  4.2, 4.3, 5.2, 5.3, 5.7, 6.3 to 6.6, 6.9, 7.2 to 7.6, 10, 14)
- `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`, `flag_catalog.json`
- `joulewise/b5/harvest.py` (`neg8.screen_failed` is emitted near lines 4776 and 4847 to 4966),
  `joulewise/whole_window.py` (`evaluate_neg8_point_drift`, `neg8_count_adjusted_bound`,
  `neg8_family_endpoint_bound`), `joulewise/b5/chain.py` (the reference spares, the spares decision), the
  campaign runner and controller that decide whether a member succeeded, `joulewise/hazards/`,
  `scripts/hazard_monitor.py`
- The procedure: `/Users/edr/code/JouleWise/docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`,
  sections 6 and 9.

Everything else under the custody roots, the runs roots `/Users/edr/night-b5/`, and the archives'
`derived/` (other than `code-identity.json`), `sources/` and `withheld/` is closed to you. That includes
`derived/neg8-screen.json` (the registration says it records the counts, the formula used and which bound
was used, and it is in restricted custody because it sits beside reference energies), the whole-window
verdict and the reference members' own run records. If a count or a status word from one of those files
is the one fact that would settle the cause, do not read it; write, under "Counts I would want", the exact
program that would print it. The program must print only fixed labels, code names and status words from
closed lists in the code, and integers that are counts: no member name, no error text, and no measured
value, ratio, bound or threshold comparison's operands. Say for each printed field why it cannot carry an
energy. The magistrate will decide whether it may run.

## The questions

1. **Cause.** From the code, state exactly (a) every condition under which the harvest emits
   `neg8.screen_failed` when the bound was derived and validated, in the order the code tests them;
   (b) which of them is consistent with this window's permitted evidence (end reference 2 of 3 succeeded,
   3 raw-valid; a spare stage that ran and returned 1; start 3 of 3; midpoint 1 of 1; one corpus member
   dropped at the harvest); (c) what a reference spare is, when the chain runs one, whether the spare that
   ran here could have counted toward the end endpoint, and what its rc 1 means; (d) which run-time
   condition made 5 of 20 members of the last science stage and 1 of 3 end references end as not
   succeeded, as far as the code and the journal can say (the `XProtectRemediat` burst from 05:40 to 06:00
   PDT, `syspolicyd` in the end stage). Say what the permitted evidence cannot distinguish.
2. **Would the next unchanged window meet it again?** Say what starts `XProtectRemediator` on macOS and on
   what schedule if you can tell without loading the machine (launchd plists may be read; do not start or
   stop anything), and whether a t0 can be chosen so that its run falls outside a chain or at least
   outside the end references. Give your estimate of the chance that an unchanged BETA attempt 2 is
   claim-usable, and what it rests on. One of four chains that kept its corpus has now lost the screen.
3. **Recommendation.** Choose one and defend it:
   (a) arm BETA attempt 2 unchanged, at the next permitted t0;
   (b) arm attempt 2 after a cure or a scheduling rule that changes nothing a window reads (a t0 chosen
       against a known schedule, a wait, something the magistrate can do alone now); name the exact
       commands and the check that shows the cure took;
   (c) a change to something a window reads or to a registered threshold, catalog effect or minimum (for
       instance more end references, spares that can replace a physics-dropped reference, a different
       endpoint minimum). This route is expensive: a prospective cold erratum before the next arm
       (registration section 10), and a change to code a window executes supersedes the block, because
       completed windows executed it (registration section 7.5): a new seal, a new clone, and the block
       restarts at ALPHA, which this time would cost the claim-usable ALPHA window (its bytes are kept
       and disclosed, its energies never analysed). Recommend it only if the physics or the arithmetic
       requires it, and then say what the new rule should be and why it is better science;
   (d) the harvest program or the verdict writer is at fault (it removed a window the registration would
       keep): name the defect, the file and the lines. A harvest fix does not touch the clone and does
       not supersede anything;
   (e) END STATE.
   Also say whether GAMMA attempt 1 may be armed before BETA has a claim-usable attempt. The brief's order
   is ALPHA, BETA, GAMMA; say whether the registration fixes that order or only the magistrate brief
   does, and whether running GAMMA now would be sound.
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
