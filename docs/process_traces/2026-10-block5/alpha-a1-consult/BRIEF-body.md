# Consult: block 5, ALPHA attempt 1 was collected and is not usable for claims. What should the next arm be?

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

ALPHA attempt 1, plan id `v5-b5-alpha-a1-20261008T2201Z`:

- t0 2026-10-08 15:01 PDT; chain started about 15:04 and exited about 20:33 PDT. Driver verdict `GO`,
  no refusal, no fault reason, closing calibration done, the G10 clock control `DISCHARGED`.
- Driver yield `PARTIAL`: 119 members planned, 119 present, 114 succeeded; every stage at or above its
  `min_valid`. By stage (succeeded of planned): bound collection (the NEG-8 corpus) 10/12; reference start
  3/3; decode absolute 10/10; decode ABBA blocks 01-05 19/20; decode ABBA blocks 06-10 20/20; reference
  midpoint 1/1; prefill p2048 absolute 9/10; prefill p2048 ABBA blocks 01-05 19/20; prefill p2048 ABBA
  blocks 06-10 20/20; reference end 3/3.
- Harvest, from the pinned harvest program at commit `7e6158d669cbb6fb35761aee18abf363f07c5d36`, exit 0:
  verdict `COLLECTED`, `claim_usable` false, window reasons **`cell.below_minimum`** and
  **`neg8.bound_not_derived`**, `faults` empty. Harvest yield: planned 119, present 119, raw-valid 119,
  succeeded 114, `strict_deferred` 119.
- `derived/code-identity.json`: the window ran the sealed code; no changed window input.
- The clock-instrument count the registration's END STATE rule uses: 116 recorded statuses, 1 not bounded.

The sealed procedure's row for these two reason codes reads:

> Do not arm the same pack again unchanged. Each of these can come from a cause the next window would meet
> again, and the rate of that cause on this Mac with no agent alive was never measured before ALPHA-1.
> `cell.below_minimum`: one reported quantity kept fewer than 5 of its 10 units of one kind, most plausibly
> because a system process kept exceeding the contention limit (0.05 CPU-seconds per second in a 10-second
> interval that overlaps a member's request). The two `neg8` codes: reference or corpus members (the small
> fixed workload against which drift is screened) could not be used; the chain runs a spare only for a
> member that did not succeed, and the corpus has no spare at all. Convene the consult at once, on the
> first occurrence. Its evidence is structural: the window reasons, the member counts, and the monitor's
> contention journal.

That row's "most plausibly" is a guess written before any window ran. Treat it as a hypothesis to test,
not as the finding.

## Where things are (absolute paths)

Evidence you may open:
- `/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261008T2201Z/harvest.json`: only the keys `verdict`,
  `claim_usable`, `exclude_window_reasons`, `yield`, `faults`, `harvest_checkout`. Read them with a program
  that prints those keys and no others; do not print the file.
- `/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261008T2201Z/derived/code-identity.json`
- `/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z/night/hazard_result.json`
- `/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z/hazards/arm.json`
- `/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z/hazards/monitor/contention.jsonl` (1,978 lines:
  process names and CPU shares)
- Plan-time files, which are not restricted: `/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z/night_plan.json`,
  `window.env` beside it, and `/Users/edr/night-plan-staging/v5-b5-alpha-a1-20261008T2201Z/`.

Code and the sealed documents, in your working directory (a detached worktree at the harvest program's
commit, which contains the sealed tree):
- `configs/campaigns/v5_claim_25g83/registration_block5.md` (sealed registration; sections 0.8, 0.9, 0.12,
  4.2, 4.3, 5.2, 5.3, 6.3 to 6.6, 6.9, 7.2 to 7.6, 10)
- `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`, `flag_catalog.json`
- `joulewise/b5/harvest.py` (where both codes are emitted), `joulewise/b5/chain.py`,
  `joulewise/hazards/` (the contention module and its thresholds), `scripts/hazard_monitor.py`
- The procedure: `/Users/edr/code/JouleWise/docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`,
  sections 6 and 9.

Everything else under the custody root, the runs roots `/Users/edr/night-b5/`, and the archive's `derived/`
(other than `code-identity.json`), `sources/` and `withheld/` is closed to you.

## The questions

1. **Cause.** From the code, state exactly which conditions make the harvest emit each of the two codes,
   and which upstream conditions (member exclusion codes by family, not by member) can produce them in a
   window whose counts are the ones above: 114 of 119 succeeded, the corpus at 10 of 12, no harvest fault.
   Then use the contention journal to say how far contention explains it: what share of the window's
   intervals exceed the registered limit, which processes are responsible, whether the excess is steady
   across the window or clustered, and whether those processes are ours to remove (a daemon that can be
   restarted or disabled, a leftover of our own tooling) or part of the operating system at rest. Say what
   the evidence cannot distinguish.
2. **Would the next unchanged window meet it again?** Give your estimate and what it rests on.
3. **Recommendation.** Choose one and defend it:
   (a) arm ALPHA attempt 2 unchanged;
   (b) arm ALPHA attempt 2 after a cure that changes nothing a window reads (a machine-state action before
       the arm: name the exact commands and the check that shows the cure took);
   (c) a change to something a window reads or to a registered threshold, catalog effect or minimum. This
       route is expensive: a threshold or catalog change needs a prospective cold erratum before the next
       arm (registration section 10), and a change to code a window executes supersedes the block, because
       ALPHA-1 executed it (registration section 7.5). Recommend it only if the physics requires it, and
       then say what the new rule should be and why it is better science, not only what is cheaper;
   (d) the harvest program is at fault (it removed a window the registration would keep): name the defect,
       the file and the lines. A harvest fix does not touch the window code and reaches the harvest
       through the desk root and an addendum;
   (e) END STATE.
4. **What you are least sure of**, and the one additional structural fact that would change your answer.

Rule carried in every brief on this path: only a directly measured physical hazard or a number-integrity
condition may stop collection or exclude data. A rule that is only about how something is recorded is a
flag, not a refusal. Old rules do not bind the science: if the evidence shows a registered limit is wrong
for this machine, say so and say what the right one is; the gate for changing it is a cold erratum, and
"the existing rule says" is never the reason a worse rule stays.

## What to return

Plain findings, not prose for a reader outside the project. Sections: Cause; Recurrence; Recommendation
(one letter, then the steps); Least sure; Counts I would want (optional). Cite file paths and line numbers
for every claim about code, and journal line counts or integer tallies for every claim about contention.
