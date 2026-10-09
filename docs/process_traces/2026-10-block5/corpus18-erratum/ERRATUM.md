# Prospective cold erratum to registration V5-CLAIM-25G83-B5: an 18-member NEG-8 corpus, with the deciding bound built at the desk from at most 12 of them

**Status: ADMITTED WITH CORRECTIONS on 2026-10-09 by the cold ruling `RULING.md` in this directory. This text
is the corrected text that the builder builds from, without another judge. Where this text and the ruling
differ, the ruling governs.**

Written 2026-10-09 by an Opus 5.5 drafting seat for the magistrate of block 5, refuted by an Opus 5.5 seat
(`REFUTATION.md`) and ruled on by a cold Fable 5.1 judge (`RULING.md`). The ruling's section E lists 14 numbered
corrections; an Opus 5.5 seat applied all of them to this file on 2026-10-09 and wrote
`CORRECTIONS-APPLIED.md`, which says where each one landed. Neither seat changed code or configuration,
started another agent or made a network request. Structure only: this file holds no energy, power or duration
measured in a claim window, no identity of a member that failed, and no error text. Every energy printed
below is synthetic and is labelled so.

**Two rulings are cited, and they are different files.** The **consult ruling** is
`alpha-a3-consult/RULING.md`, the ruling of 2026-10-09 on ALPHA attempt 3 that ordered this erratum. The
**cold ruling** is `RULING.md` in this directory, the ruling on this erratum. In item 1 of the list below, in section 0 and in
sections 1, 3 and 6 the words "the ruling" with no adjective mean the consult ruling, as they did in the draft. The cold ruling is always
called by its full name. In the same way "this seat" means the drafting seat, and the seat that applied the
corrections is called "the corrections seat".

Three things in the draft differed from the consult ruling. The cold ruling confirmed all three:

1. **The bound gets wider with 18 members, not tighter** (section 2.5). The ruling's reason for (a) was wrong;
   this erratum's rule is (d), ruled 2026-10-09. The **bound** is a number of joules computed from
   the corpus, a group of identical reference runs at the start of each window: it is the largest change of
   the instrument's reading between the window's start and its end that plain repeatability could produce,
   and a window that shows a larger change is removed (section 0 builds these terms). "(a)" is the rule the
   consult ruling ordered: derive the bound from every corpus member that is kept, 10 to 18 of them. "(d)" is the rule of section 2.1: all 18
   members run in the window, and afterwards, at the desk, the bound that decides the window is computed from
   at most 12 of them, the first 12 in committed order that were not lost or disturbed.
2. **The core reader is tied to the old 12-member file by path** (section 4.2, finding F2). With an 18-member
   corpus every window, even one that loses nothing, is judged by the harvest's second route. No code that a
   window executes needs to change for that, but the registration must say it.
3. **The pack generators fix the number 12 as literals** (section 4.2, finding F1), and one of those literals
   feeds a digest that is stamped into all 280 science configurations (finding F3).

Section 8 records the question each one raised and the cold ruling's answer.

## Which text is "the sealed registration" in this file

The brief pointed this seat at the worktree `/Users/edr/code/JouleWise-wt-harvest` (commit
`7e6158d669cbb6fb35761aee18abf363f07c5d36`). That commit descends from H_claim but not from the seal commit, so
its copy of `registration_block5.md` (3,492 lines) is a draft from before the seal: for example it still says a
reported quantity needs 8 of its 10 units, where the sealed text says 5. The sealed text is the one at the
seal commit `ab7b21e576a2d74f0b25d9a26b463d6934588368`, 6,173 lines, SHA-256
`4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841`; the checkout `/Users/edr/code/JouleWise`
(main, `3f564499e`) holds the same bytes (compared by this seat with `git show` and `shasum`). **Every
registration line number below is a line of the sealed text.** The consult ruling's line numbers
(`alpha-a3-consult/RULING.md`) are lines of the unsealed draft; the sentences it relies on are present in the
sealed text with the same meaning, at the lines given here.

Code line numbers are of H_claim (`a64000884ef5bb4b76415835f02f39803f6eb620`), which main also holds for every
file under `joulewise/`, `scripts/` and `configs/` except the three seal documents. Two files differ in the
harvest worktree, `joulewise/b5/harvest.py` and `joulewise/whole_window.py`; where a line is cited from that
worktree the citation says "harvest pin".

## 0. Terms, in the order they are used

- **Window.** One unattended measurement run on the Mac, a few hours long. **Block 5** is three windows, one
  for each **pack** (a committed set of experiment inputs): ALPHA, BETA, GAMMA, in that order.
- **Attempt.** One try at a pack's window. A pack is attempted until one attempt is **claim-usable**: the
  program that checks the finished window found nothing that removes the whole window, and every reported
  quantity keeps at least 5 of its 10 planned units (registration section 6.6, line 3996).
- **Member.** One measured request to a model: the machine sits idle, the request runs, the power sampler's
  records are reduced to an energy. A member's output directory is its **bundle**. A bundle holds a summary
  whose status is `succeeded` or not. A **runs root** is the directory that holds a window's bundles.
- **Idle admission.** Before its request, a member records the idle machine for about 75 s. The request is
  measured only if the machine was quiet in that record: the 95th percentile of the busiest CPU core's busy
  share is at most 0.5, and the 95th percentile of processor power is at most 1.0 W
  (`configs/campaign_policies/quiet_mac_p2_b5.json`, as the ruling's Q3 item 3 verified). A member gets two
  attempts, back to back. If both fail, the member **aborts**: it writes a complete bundle with a status that
  is not `succeeded`, and it measures no request.
- **Contention journal.** A monitor outside the measurement writes, every 10 s, which outside processes used
  more than 0.05 CPU-seconds per second. An interval with such a process is called **dirty** here.
- **Reference member.** A member of one fixed small workload (registration section 0.12, line 975). Its energy
  should be the same every time, so a change in it measures the instrument, not a model.
- **NEG-8 corpus.** The reference members that every window runs first: 12 under the first seal (line 976),
  18 under this erratum. "NEG-8" is an inherited label, not an abbreviation. After the corpus come three reference members (the **start triplet**), the
  science members with one **midpoint reference** among them, and three more (the **end triplet**).
- **Bound.** A number of joules computed from the corpus members' energies: the largest difference between a
  start-triplet mean and an end-triplet mean that plain repeatability could produce (formula in section 2.4).
- **Screen.** The test "|end-triplet mean − start-triplet mean| ≤ bound" (line 1019). A window that fails it
  is removed, because its instrument drifted by more than repeatability explains.
- **Drift allowance.** The larger of the bound and the spread of the start mean, the midpoint and the end
  mean. It is added to the uncertainty of the window's claims (line 1019 onward).
- **Cell.** One reported quantity of a pack, measured in 10 planned units of each of two kinds (each kind is a
  **stratum**). The corpus is not a cell.
- **Arm.** The checks run just before a window starts (battery, heat, clock, outside CPU load, free disk, the
  sampler). An arm that finds a physical hazard refuses, and no chain starts. Part of it is the **dwell**: a
  wait for 180 s in a row with no outside process above the contention limit.
- **Chain.** The shell script that runs a window's stages in order. A **stage** is one command of the chain;
  a collection stage runs a list of members. The **runner** (`scripts/run_campaign.py`) is the program a
  collection stage calls to run its members one after another. The **driver** (`scripts/run_night.py` with
  `joulewise/b5/driver.py`) starts the chain, watches it, and writes the window's **terminal record**
  `night/hazard_result.json`, which holds counts and return codes and no energy.
- **Plan tree.** A pack's file `plan_tree.json`: its stages in order, with each stage's inputs, command line,
  expected number of members, and the SHA-256 of every input file. The chain is rendered from it.
- **Custody root.** The directory that holds one attempt's records other than its bundles.
- **Release event.** The recorded moment, after the block has closed, at which the measured values may be
  opened. Until then every record, email and summary carries structure only.
- **Mint.** The function that builds the bound from the corpus bundles, run by the chain right after the
  corpus stage (`whole_window._mint_hazard_neg8_drift_bound`). It may leave a succeeded member out only for
  one of five registered validity reasons (registration section 5.3, lines 2848 to 2880).
- **Harvest.** The program run at the desk after the window. It checks the window's bytes, applies the screen
  and writes whether the attempt is claim-usable.
- **Physics drop.** The harvest alone can see the monitor's journals. A corpus member whose request overlapped
  an outside process, a battery event, thermal pressure or a clock step measured the disturbance, so the
  harvest leaves it out and builds the bound again from the rest (section 5.3, lines 2882 to 2911).
- **Corpus retry.** One extra run of the corpus stage, made when fewer than 10 members succeeded (section 5.1,
  line 2703).
- **Collection code, desk code.** Collection code is code that a window executes (the chain, the runner, the
  driver, the mint). Desk code runs after the window, at the desk (the harvest, the analysis). The registration
  treats a defect in each differently (section 7.5, lines 4600 to 4636): a desk defect is fixed and the
  harvest is run again on the same bytes, and no window is lost; a change to collection code or to a
  collection input that a completed window executed supersedes the block (the last term of this list).
- **Committed order.** The order of the corpus members in the committed file
  `configs/campaigns/neg8_reference_corpus_v5/order_manifest.json`: r01 first, r18 last. A member's
  **committed position** is its place in that order.
- **Collected manifest, prune.** After the corpus stage the chain writes a copy of the corpus manifest that
  lists only the members that succeeded and that the mint does not drop. The copy is the **collected
  manifest**, and the chain helper that writes it is the **prune** (`chain.py` lines 567 to 628).
- **In-window bound.** The bound the mint builds in the window, from the members of the collected manifest.
- **Core, core reader, core builder.** The **core** is the module `joulewise/whole_window.py`, which builds,
  reads and screens bounds. Its **reader** is `load_neg8_drift_bound_artifact`; its **builder** is
  `build_neg8_drift_bound_artifact`.
- **Route 1, route 2.** The two ways the harvest can accept an in-window bound (registration 5.3, lines 2773
  to 2781; built in finding F2 of section 4.2). Route 1: the core reader accepts it against one fixed file.
  Route 2: the harvest validates it against the window's own collected manifest and runs the screen again
  itself (the **re-screen**).
- **Monitor join.** The harvest step that matches the monitor's journal intervals to each member's time span,
  and so decides on which members a physics code fired.
- **Clean bound, cap.** The **clean bound** is the bound the harvest builds at the desk by applying the bound
  formula again to a subset of the in-window bound's recorded member energies. It needs no new measurement.
  Under the first seal the subset was "the members no physics code fired on", and the harvest built it only
  when a code had fired (`joulewise/b5/harvest.py` harvest pin lines 5339 to 5436, method
  `neg8_corpus_physics`). Under this erratum it is built on every window, and the subset is cut to its first
  12 members in committed order. That cut is the **cap** (section 2.1).
- **Seal, H_claim, sealed inventory, measurement clone.** **H_claim** is the commit whose files every window
  reads. The **sealed inventory** lists the SHA-256 of each code and pack file at H_claim. The **seal** is the
  record that pins those digests after a cold gate judged the files. The **measurement clone** is the one
  checkout the windows run from; it is never updated.
- **Seal documents, seal commit.** The seal documents are three files of
  `configs/campaigns/v5_claim_25g83/`: `sealed_inventory.json`, `registration_block5.md` and
  `analysis_plan_block5.md`. Their final bytes cannot exist at H_claim, because all three print H_claim's
  hash or digests computed at H_claim, and a commit cannot contain its own hash. The **seal commit** is the
  one commit whose only parent is H_claim and which changes only seal documents (registration section 11,
  lines 5051 to 5055). The first seal's is `ab7b21e57`.
- **Harvest lane, harvest pin.** The harvest program that judges block-5 windows is developed on its own
  branch, the **harvest lane**, checked out at `/Users/edr/code/JouleWise-wt-harvest`. The **harvest pin** is
  the commit of that lane which a section appended to the seal record (an **addendum**, marked
  `B5-HARVEST-PIN`) names as the program that judges the windows. Today it is `7e6158d66`.
- **Supersede.** To replace the block's sealed rules with new ones: the windows already run are kept and
  disclosed, their energies are never analysed, and the block starts again at ALPHA (section 7.5, line 4628).

## 1. The forcing problem

### 1.1 What the registration assumed and what happened

The registration sized the corpus rule on one loss rate: 1 member in 37 aborted by idle admission, the record
of blocks 2 and 3 (section 5.3, line 2759; section 6.6, line 4011). At that rate a 12-member corpus loses three
or more members in 0.4% of windows (section 2.3 computes it).

The two ALPHA chains that ran (attempts 1 and 3; attempt 2 was refused at its arm and started no chain) show
this instead. The counts are from `night/hazard_result.json` of each attempt, an open file; this seat printed
its per-stage rows (planned, present, succeeded, logged, failed, return code) and nothing else.

| Stage kind | Attempt 1 | Attempt 3 | Both | Rate |
|---|---|---|---|---|
| NEG-8 corpus (12 planned) | 2 not succeeded | 3 not succeeded | 5 of 24 | 0.21 |
| Science stages (100 planned) | 3 not succeeded | 0 not succeeded | 3 of 200 | 0.015 |
| Registered planning figure | | | 1 of 37 | 0.027 |

The science stages lose members at about the planned rate. The corpus loses them at about eight times that
rate. The members are the same kind of thing in both; what differs is where they sit in the window.

### 1.2 Why the corpus is exposed: it runs in the dirty first hour

```
 chain start                                                                        chain end
 |                                                                                          |
 | pre   | NEG-8 corpus  | bound | start   | science stages, with the     | end     | post |
 | calib | 12 members    | built | triplet | midpoint reference inside    | triplet | calib|
 |-------|---------------|-------|---------|------------------------------|---------|------|
 |<------ first hour: 360 intervals ------>|<------- the rest: about 1,550 intervals ------>|
          22% dirty (attempt 3)                       6% dirty (attempt 3)
          14% dirty (attempt 1)                       8% dirty (attempt 1)
```

Each box is one part of the chain, drawn left to right in the order it runs; widths are not to scale. "pre
calib" and "post calib" are the two timing calibrations that bracket the window. The bottom bar splits the
monitor's 10 s intervals into the first 360 (one hour) and the rest. The percentages are the share of dirty
intervals in each part, from the judge's recount of the two journals (ruling, "Journal recount" and Q2 reason
1): attempt 3, 81 of 360 against 92 of 1,553; attempt 1, 49 of 360 against 134 of 1,615. In attempt 3 every
run of four or more consecutive dirty intervals ends by interval 326.

So the corpus is the first collection stage, and the first hour is the hour in which sustained outside load
occurs. A sustained load defeats both admission attempts of a member, because the second attempt follows the
first with no wait.

### 1.3 Why 12-needs-10 has no margin

Two mechanisms stand between a lost corpus member and a lost window, and neither helps here.

**The retry cannot re-measure a member whose bundle exists.** The retry runs the same stage into the same
runs root. For each member the runner looks at the bundle directory (`scripts/run_campaign.py` lines 3024 to
3039): a readable summary gives the action `skip complete` whatever its status; a directory without a readable
summary gives `incomplete existing`; only a missing directory gives `would run`. A `skip complete` member with
a failed status is counted as a failure and nothing is launched (lines 10731 to 10759). An aborted member has
a complete bundle, so the retry skips it. The registration says the same in words (section 5.1, lines 2706 to
2709). Attempt 3 shows it in integers: the driver saw 131 attempts, which is 119 planned members plus 12 rows
that the retry logged, and after the retry the corpus still had 12 bundles present and 9 succeeded (ruling,
"Open-file facts"). The retry measured nothing.

**The physics drop needs zero further losses at 10.** At exactly 10 succeeded the retry does not run
(`joulewise/b5/chain.py` line 235, `NEG8_RETRY_MINIMUM = 10`; the decision at line 835 is "retry" only below
the minimum). The chain builds a bound from the 10. The harvest then drops any of those 10 on which a physics
code fires, and 9 is below the minimum (`joulewise/b5/harvest.py` harvest pin line 5405). Attempt 1 went this
way: 10 of 12 succeeded, the chain derived a bound, and the harvest reported `neg8.bound_not_derived`.

The whole margin of the rule is therefore two members, shared between run-time aborts and harvest drops, in
the hour when both are most likely.

### 1.4 The cause statement

The ruling permitted one structure-only count over the members of attempt 3 (its Q1), to be run once and
copied verbatim. Its output for the corpus runs root (label `bound`), from `alpha-a3-consult.md`:

```
bound.admission.attempt1.cpu_busy_ratio_p95_exceeded 3
bound.admission.attempt1.processor_combined_power_w_p95_exceeded 1
bound.admission.attempt2.cpu_busy_ratio_p95_exceeded 3
bound.admission.attempt2.processor_combined_power_w_p95_exceeded 1
bound.admission.attempts.2 3
bound.admission.decision.abort 3
bound.bundles 12
bound.failure_phase.idle_baseline 3
bound.failure_reason.unknown_error 3
bound.join.clock_check.ok 1
bound.join.not_succeeded.baseline_overlaps_over_limit 3
bound.join.offenders_in_not_succeeded_baselines.corespotlightd 2
bound.join.offenders_in_not_succeeded_baselines.find 1
bound.join.offenders_in_not_succeeded_baselines.fseventsd 1
bound.join.offenders_in_not_succeeded_baselines.mds 1
bound.join.offenders_in_not_succeeded_baselines.mds_stores 1
bound.join.offenders_in_not_succeeded_baselines.signpost_reporte 2
bound.join.offenders_in_not_succeeded_baselines.spindump 1
bound.join.succeeded.baseline_clean 7
bound.join.succeeded.baseline_overlaps_over_limit 2
bound.status.failed 3
bound.status.succeeded 9
```

Read line by line. Three corpus members did not succeed (`status.failed 3`). All three failed in the idle
record before the request (`failure_phase.idle_baseline 3`), by an admission abort (`decision.abort 3`) after
two attempts (`attempts.2 3`). On both attempts all three exceeded the busy-core limit, and one also exceeded
the power limit. All three idle records overlapped a dirty interval of the journal
(`not_succeeded.baseline_overlaps_over_limit 3`), and the processes in those intervals are operating-system
background services. No line shows a failure of the runner, the model runtime or the sampler.

**Cause, as this erratum states it:** in ALPHA attempt 3 the NEG-8 corpus lost three members to physical
idle-admission aborts under sustained outside CPU load in the first hour of the window. The admission rule
did what it is registered to do. The corpus rule had too few members to absorb what the admission rule
correctly refused.

## 2. The new rule

### 2.1 Statement

**The forcing problem of the rule, in three sentences.** Section 1 shows that 12 members are too few to
absorb the first hour's losses, so six are added. Section 2.5 shows that a bound computed from more members
is a larger bound, so a screen that used all 18 would be easier to pass than the screen the registration
sealed. The rule therefore lets the six extra members replace lost ones and do nothing else: all 18 run, and
the bound that decides the window is computed from at most 12.

**The rule is the cold ruling's rule (d).** The six items below are the cold ruling's section B, items 1 to 6,
copied word for word. Four references inside them need a gloss: "J8" is question J8 of section 8 (the new
names); "finding F2" is in section 4.2; "harvest pin" marks a line number of the harvest lane's files
(section 0); `NEG8_RETRY_MINIMUM` is the constant 10 at `joulewise/b5/chain.py` line 235.

> 1. The committed corpus has 18 members, `neg8-refcorpus-r01` to `-r18`, in
>    `configs/campaigns/neg8_reference_corpus_v5/`, under the new `corpus_id` and manifest id of J8. Every
>    member runs in every window in the committed order of `order_manifest.json`. No program decides at run
>    time whether a member runs.
> 2. **In the window** nothing changes but the count: the chain's one retry fires when fewer than 10 succeeded
>    (`NEG8_RETRY_MINIMUM`), the prune keeps the succeeded members the mint does not drop, the mint derives
>    the in-window bound from all of them (n from 10 to 18) and the derivation stage fails below 10 or on any
>    refused or indeterminate member, as now. The in-window bound is a diagnostic: no screen or allowance of
>    block 5 is decided by it (finding F2: the core reader authenticates only the historical 12-member file,
>    whole_window.py 150-157 and 1710-1713, so every block-5 window is judged by the harvest's route 2).
> 3. **At the desk** the harvest always builds the deciding bound, the **clean bound**, in
>    `neg8_corpus_physics` after the monitor join, whether or not a physics code fired: (i) take the members
>    of the validated in-window bound; (ii) order them by their position in the committed
>    `order_manifest.json` (not by the artifact's own order); (iii) remove every member on which one of the
>    six physics codes fired (`NEG8_PHYSICS_LOSS_CODES`, harvest pin 91-93); (iv) of the remainder keep the
>    first 12 in that order, or all of them if fewer than 12 remain; (v) if fewer than 10 remain,
>    `neg8.bound_not_derived` with `observed.source` `corpus_physics`, as now; (vi) build the clean bound
>    from the kept members' recorded points with the core builder, validate it against the clean manifest
>    bytes (the bound's manifest less the removed and the capped members), write
>    `derived/neg8-clean-corpus.json`, `withheld/neg8-clean-bound.json` and
>    `derived/neg8-corpus-physics.json` as now, with one new key in the last, `beyond_cap`, listing the bundle
>    ids left out by step (iv), and `members_kept` the count after (iv). The screen re-runs against the clean
>    bound and the allowance comes from it (`corpus_physics_clean`), as the sealed path already does for a
>    physics drop.
> 4. **n is therefore 10, 11 or 12**, and the registration's sentence at 1004 ("n their count (10, 11 or 12;
>    §5.3)") stays as sealed. The t multipliers are 2.262, 2.201, 2.201 at n = 10, 11, 12 (unchanged).
> 5. Members left out by step (iv) are not dropped for cause: no `neg8.corpus_member_dropped` flag is emitted
>    for them, no catalog code is added, and their energies are used by nothing. They are disclosed after the
>    release event with the window's corpus size (analysis plan line 597).
> 6. The registration's 5.3 names this cap as the one accepted omission of the desk step, beside the mint's
>    five reasons and the six physics codes; the chain's collected-manifest test (harvest pin 4703-4737) is
>    unchanged, because the chain's manifest still lists every succeeded member.

One figure in item 4 does not agree with the code's table, and the table governs. The multiplier is
t(0.975, n − 1). The table `joulewise/aggregate.py` lines 41 to 59 gives 2.262 at 9 degrees of freedom
(n = 10), **2.228 at 10 degrees of freedom (n = 11)** and 2.201 at 11 (n = 12). Item 4 prints 2.201 for
n = 11. The words "(unchanged)" settle what is meant: the multipliers are the ones the sealed code already
uses, and no multiplier is edited. `CORRECTIONS-APPLIED.md` reports this to the magistrate.

*Worked example* (the cold ruling's, word for word; "the draft's six" are the six synthetic energies of
section 2.5):

> *Worked example (synthetic, the registration's own twelve energies plus the draft's six).* Members 2, 3 and
> 5 abort at admission and member 9 overlaps a contender at harvest. Kept after (iii), in committed order: 1,
> 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18. Step (iv) keeps 1, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16
> and records 17 and 18 under `beyond_cap`. The clean bound is computed from those twelve energies with
> t = 2.201. Had eight members been lost instead of four, the ten remaining would all be kept and t = 2.262,
> exactly as the sealed rule treats ten of twelve.

*The same example in numbers* (synthetic; computed by the corrections seat with the formula of section 2.4).
Give the members the energies of section 2.5 by committed position: positions 1 to 12 are 99.62, 99.71,
99.80, 99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31, 100.38 J and positions 13 to 18 are
99.76, 99.85, 99.95, 100.01, 100.12, 100.27 J. The section 2.4 formula at the planned shape is: bound = the
larger of (mean of the three largest energies − mean of the three smallest) and t × s × √(2/3), with s the
sample standard deviation.

| Which bound | Members it rests on (committed positions) | n | t | s | three largest − three smallest | t × s × √(2/3) | Bound |
|---|---|---|---|---|---|---|---|
| In-window bound (decides nothing) | the 15 that succeeded: 1, 4, 6 to 18 | 15 | 2.145 | 0.2113 J | 100.3200 − 99.7433 = 0.5767 J | 0.3701 J | 0.5767 J |
| After the physics drop, with no cap (what rule (a) would use) | 1, 4, 6, 7, 8, 10 to 18 | 14 | 2.160 | 0.2171 J | 100.3200 − 99.7433 = 0.5767 J | 0.3828 J | 0.5767 J |
| Clean bound (decides the screen) | the first 12 of those: 1, 4, 6, 7, 8, 10 to 16 | 12 | 2.201 | 0.2217 J | 100.3033 − 99.7433 = 0.5600 J | 0.3983 J | **0.5600 J** |

√(2/3) is 0.8165. Member 9 succeeded in the window, so the in-window bound holds it; the desk removes it
because a physics code fired on it. The cap then leaves out positions 17 and 18 (100.12 and 100.27 J), and
the bound falls from 0.5767 to 0.5600 J. Nobody read those two energies to choose them. They are left out
because, of the 14 clean members, they are the thirteenth and fourteenth in committed order.

**What the rule leaves standing from the draft, and one sentence the cold ruling added.**

- *The six new files.* The existing twelve keep their run ids (`neg8-refcorpus-r01` to `-r12`). Six are added
  (`neg8-refcorpus-r13` to `-r18`). Each new configuration is a byte copy of an existing one except for the
  `run_id` line, as the existing twelve already are of each other (checked: `diff` of r01 against r02 and
  against r12 prints the `run_id` line only). The mint computes a member's scientific identity as the SHA-256
  of its configuration with the run id removed (`joulewise/whole_window.py` lines 4849 to 4853 at the harvest
  pin), so all 18 share one identity, which the mint requires.
- *The margin, and its limit.* The corpus may lose up to eight members to status, validity or physics; one
  refused or indeterminate member still gives `neg8.bound_not_derived`. The three kinds of loss the eight
  absorb are: a member whose status is not `succeeded`; a member the mint omits for one of its five validity
  reasons; a member a physics code fires on. A **refused** member is one the mint will not judge at all (an
  unauthenticated launch lineage, a configuration that is not the reference workload, no recorded calibration
  identity, a file inventory that cannot be sealed: `whole_window.py` lines 4500 to 4541). An
  **indeterminate** member is one whose evidence the mint could not classify (line 4669 to 4674). Either one
  makes the mint raise, the chain's prune then falls back to the status-only rule (`chain.py` 603 to 612),
  and the derivation stage fails. With 18 members there are half again as many chances of one such member as
  with 12. Neither chain so far showed one.
- *The minimum stays 10* (`whole_window.NEG8_DRIFT_MINIMUM_N`, line 136; `chain.NEG8_RETRY_MINIMUM`, line 235;
  `driver.CORPUS_MIN_VALID`, line 152). With fewer than 10 kept, `neg8.bound_not_derived` removes the window,
  as now. The number of members a bound rests on, n, is 10, 11 or 12 at the desk; the in-window bound, which
  decides nothing, rests on 10 to 18.
- *The one corpus retry stays, unchanged.* It runs when fewer than 10 of the 18 succeeded. It can measure a
  member that has no bundle directory (one refused before its bundle existed). It cannot measure a member
  that aborted, because that member has a bundle. For the loss this erratum is about, the retry does nothing,
  and the registration will say so in those words.
- *The corpus has a new identity.* `derivation/settled_corpus.json` gets the `corpus_id`
  `neg8-reference-corpus-m3max-qwen25-1p5b-v2-n18`, because the old id names a 12-member set and every bound
  records the id and the SHA-256 of the manifest it was built from (accepted, J8).

### 2.2 How a reader would rebuild it

*In the window.* Take the list of 18 run ids in committed order. Run each as a member. For each, read the
status in its summary. Keep the members whose status is `succeeded`. From those, remove any member the mint
omits for one of its five validity reasons. If fewer than 10 remain, or any member is refused or
indeterminate, there is no in-window bound and the window is removed. Otherwise compute the in-window bound
of section 2.4 from the remaining energies and record, beside it, each member's id and energy.

*At the desk, on every window.* Take the members the in-window bound recorded. Sort them by committed
position. Remove every member on which one of the six physics codes fired. Count what is left. If it is fewer
than 10, the window is removed. If it is 10, 11 or 12, keep all. If it is more than 12, keep the first 12 and
write the ids of the others under `beyond_cap`. Compute the bound of section 2.4 from the kept energies: this
is the clean bound. Run the screen against it, and take the drift allowance from it.

Membership is decided by status, by the mint's five validity reasons, one of which (`precheck_ineligible`)
can turn on the ratio of a member's timing envelope to its own energy (`reduce.py`
`anchor_energy_envelope_exceeds_quarter_metric`), and by the six physics codes, and at the desk by committed
position (the cap). No step reads the size of an energy for any other purpose.

The one energy-dependent reason, built from the code. A member's **timing envelope** is the amount by which
its energy could be wrong because the sampler's clock and the request's clock are aligned only to within a
known uncertainty. The reducer marks a member's energy gate "not eligible" when (envelope deviation + joint
bound) ÷ |energy| exceeds 0.25 (`joulewise/reduce.py` lines 2330 to 2361; the constant
`ANCHOR_ENVELOPE_METRIC_RATIO_MAX` at line 119; merged into the gross and idle-subtracted gates at lines 2469
to 2481). The mint reads those gates (`whole_window.py` lines 4093 to 4099) and omits a member whose gate is
not eligible, with the reason `precheck_ineligible` (lines 4124, 4125 and 4397 to 4405; registration lines
2858 to 2860). A member with a smaller energy has a larger ratio, so this reason can remove low-energy
members a little more often than others, which would trim the low end of the corpus and shrink the bound.
The size of that effect here: the corpus members are one workload under one condition, and their energies
differ by well under one percent of each other (the registration's synthetic example at line 1233 spans
99.62 to 100.38 J), so the ratio moves by the same fraction. The cold ruling found the direction real and
the size negligible on this corpus, and ordered a disclosure, not a new threshold: the analysis plan prints,
for each window, how many corpus members each reason left out (section 4.5, edit P2). The exposure is the
same under every rule that was considered.

### 2.3 Worked example: how often 10 are kept

If each member is lost independently with probability p, the chance that at most k of n are lost is
the sum over j = 0..k of C(n, j) × p^j × (1 − p)^(n−j). The corpus of 12 survives when at most 2 are lost; the
corpus of 18 when at most 8 are lost.

At the observed corpus rate p = 5/24 = 0.208:

- 12 members, terms for j = 0, 1, 2: 0.0606 + 0.1914 + 0.2770 = **0.529**.
- 18 members, terms for j = 0..8: 0.0149 + 0.0707 + 0.1581 + 0.2219 + 0.2190 + 0.1613 + 0.0920 + 0.0415 +
  0.0150 = **0.994**.

| Loss rate per member | 12 members, at most 2 lost | 12, at most 1 lost | 18 members, at most 8 lost | 18, at most 7 lost |
|---|---|---|---|---|
| 1/37 = 0.027 (registered figure) | 0.996 | 0.960 | 1.000 | 1.000 |
| 0.10 | 0.889 | 0.659 | 1.000 | 1.000 |
| 5/24 = 0.208 (observed, corpus) | 0.529 | 0.252 | 0.994 | 0.979 |
| 0.25 | 0.391 | 0.158 | 0.981 | 0.943 |
| 0.35 | 0.151 | 0.042 | 0.861 | 0.728 |

The "one fewer lost" columns show the chance that one member is still spare for the harvest's physics drop.
(Computed by this seat with exact binomial sums; a reader can redo any cell with the formula above.)

**These figures are a guide, not a guarantee.** Losses are not independent. One sustained burst of outside
load takes consecutive members: a member's two admission attempts span about 170 s, so a five-minute burst
takes about two members. In those terms a 12-member corpus survives one burst and an 18-member corpus about
four. Both chains so far had at least one burst on the corpus. Nothing here promises that a fifth burst
cannot happen; the rule for that case is unchanged (the window is removed and the pack is attempted again).

### 2.4 The bound formula, as the registration states it

From the registration, section 0.12, lines 1001 to 1009. Let the kept corpus members' energies be given, with
n their count, s their sample standard deviation, and t = t(0.975, n − 1) the two-sided 95% Student
multiplier. Let U_j be the mean of the j largest energies and L_j the mean of the j smallest. For n_s start
references and n_e end references:

    bound(n_s, n_e) = max( max(U_ns − L_ne, U_ne − L_ns),  t × s × √(1/n_s + 1/n_e) )

The first term is the **envelope**: the widest gap between a start mean and an end mean if both were drawn
from the corpus itself. The second is the **repeatability term**: the 95% bound for the difference of two
means when nothing drifts. The same computation is done for the gross and for the idle-subtracted energies.

The multiplier t, from the code's table (`joulewise/aggregate.py` lines 41 to 59):

| n kept | degrees of freedom | t | t × √(2/3), the repeatability term in units of s at the planned shape (3, 3) |
|---|---|---|---|
| 10 | 9 | 2.262 | 1.847 |
| 11 | 10 | 2.228 | 1.819 |
| 12 | 11 | 2.201 | 1.797 |
| 18 (the in-window bound only) | 17 | 2.110 | 1.723 |

### 2.5 What the bound does when n grows: the reason the rule is (d)

This section corrects the consult ruling, and the cold ruling upheld the correction (its finding A.4). It
compares two rules: **(a)**, the bound from every kept member, n from 10 to 18, which the consult ruling
ordered; and **(d)**, the rule of section 2.1, n at most 12.

The consult ruling's Q2 (iii) says that with more members "the t multiplier falls ... on a normal window the screen
gets slightly stricter, never looser". The multiplier does fall. But the bound is the larger of two terms, and
the envelope is the larger one. The envelope is the mean of the three largest energies minus the mean of the
three smallest. The more members are drawn, the further out the three largest and the three smallest lie, so
the envelope grows with n even when the spread s does not.

*Synthetic example.* The registration's own twelve synthetic energies (line 1233): 99.62, 99.71, 99.80,
99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31, 100.38 J. s = 0.2353; envelope U_3 − L_3 =
100.3033 − 99.7100 = 0.5933; repeatability term 2.201 × 0.2353 × √(2/3) = 0.4228; **bound 0.5933 J**. Add six
more synthetic members that lie inside the same range: 99.76, 99.85, 99.95, 100.01, 100.12, 100.27 J. Now
n = 18 and s = 0.2141, smaller than before. U_3 = (100.38 + 100.31 + 100.27)/3 = 100.3200; L_3 = (99.62 +
99.71 + 99.76)/3 = 99.6967; envelope 0.6233; repeatability term 2.110 × 0.2141 × √(2/3) = 0.3689; **bound
0.6233 J**. The spread fell by 9% and the bound rose by 5%. If eight of the 18 are then lost (positions 2, 3,
4, 5, 9, 10, 14, 15 in committed order), the ten kept give s = 0.2376, envelope 100.3200 − 99.7833 = 0.5367,
repeatability term 2.262 × 0.2376 × √(2/3) = 0.4388, **bound 0.5367 J**.

*In general.* For members drawn independently from one normal distribution with standard deviation σ, this
seat simulated 200,000 corpora at each size (Python `random.gauss`, seed 20261009; the script is seven lines
and a reader can rerun it):

| n kept | mean envelope | mean repeatability term | mean bound | share of corpora where the envelope is the larger term | bound ÷ standard deviation of the screen statistic | chance a window with no drift fails the screen |
|---|---|---|---|---|---|---|
| 10 | 2.13 σ | 1.80 σ | 2.13 σ | 99.1% | 2.61 | 2.6% |
| 11 | 2.25 σ | 1.78 σ | 2.25 σ | 99.9% | 2.76 | 1.8% |
| 12 | 2.36 σ | 1.76 σ | 2.36 σ | 100.0% | 2.89 | 1.4% |
| 14 | 2.54 σ | 1.73 σ | 2.54 σ | 100.0% | 3.11 | 0.7% |
| 16 | 2.70 σ | 1.71 σ | 2.70 σ | 100.0% | 3.30 | 0.4% |
| 18 | 2.82 σ | 1.70 σ | 2.82 σ | 100.0% | 3.46 | 0.3% |

The screen statistic is the difference of two three-member means; its standard deviation is σ × √(2/3).

*The screen's power.* The table above says how often a window with no drift fails. The other half of a
screen is how often a window that did drift fails, which is the screen's **power**. A **true shift of δ**
means that the instrument's reading of the same workload moved by δ between the start triplet and the end
triplet. The cold judge simulated it (100,000 normal corpora for each size, seed 20261009, the screen
statistic drawn independently of the corpus; the cold ruling's finding A.4, its table copied here):

| n kept | mean envelope | mean repeatability term | mean bound | envelope larger | no-drift window fails | fails at a true 2 σ shift | at 3 σ |
|---|---|---|---|---|---|---|---|
| 10 | 2.13 σ | 1.80 σ | 2.13 σ | 99.2% | 2.5% | 45% | 81% |
| 12 | 2.36 σ | 1.76 σ | 2.36 σ | 100% | 1.4% | 36% | 75% |
| 15 | 2.62 σ | 1.72 σ | 2.62 σ | 100% | 0.6% | 26% | 66% |
| 18 | 2.83 σ | 1.70 σ | 2.83 σ | 100% | 0.3% | 20% | 58% |

Its last decimal differs from the drafting seat's table in two cells (2.83 σ against 2.82 σ, 2.5% against
2.6%); the two tables come from different random draws. Reading one row: a shift of three standard
deviations of one member fails a 12-member screen three times in four, and an 18-member screen 58 times in
a hundred.

*A drift inside the corpus widens the bound, and faster for a longer corpus.* If the instrument drifts while
the corpus itself is being measured, the members spread out and the envelope grows. With a linear drift of
0.1 σ per member inside the corpus the mean bound is 2.51 σ at 12 and 3.20 σ at 18 (the cold ruling, A.4). A
drifting instrument relaxes its own screen, and with 18 members it relaxes it faster.

What this means, stated plainly:

- A bound from 18 members is about **20% larger** than a bound from 12 (2.82 σ against 2.36 σ), and about
  33% larger than a bound from 10.
- A larger bound makes the screen **easier to pass**: a drift has to be about 3.5 standard deviations of the
  screen statistic to remove a window screened on 18 members, against about 2.9 for one screened on 12.
- A larger bound also makes the **drift allowance larger**, and the allowance is added to every claim's
  uncertainty. So a drift that a wider screen lets through is still covered by the allowance the claims
  carry (registration lines 1019 to 1025: the allowance is at least the bound, and a window passes only when
  the screen statistic is at most the bound). The allowance compensates for validity, not for sharpness or
  comparability: under (a) every claim would carry a floor about 20% higher, GAMMA's direction decision
  would be harder to reach, and the screen's level would differ between windows with different losses.
  (GAMMA's direction decision is the decision whether the sign of a contrast can be claimed; it rests on a
  quantity that contains the allowance, analysis plan lines 132 and 133.)
- Under (a) the bound would depend on how many members each window lost: n from 10 to 18, a mean bound from
  2.13 σ to 2.82 σ, three windows of one block screened at three levels. Under (d) n is 12 whenever at most
  six of the 18 are lost to status, mint reasons and physics together, 11 at seven lost, 10 at eight, and
  the window is removed at nine or more. That is the sealed dependence, shifted by six losses that the extra
  members absorb.

**Why (d) and not the others**, from the cold ruling's section B. The registration sets the screen's
operating point by sealing a 12-member corpus, and it calls a widened envelope "a bias toward passing" (lines
2883 to 2885). Rule (a) would move that operating point from 2.36 σ to 2.83 σ as a side effect of a fix for
lost members. Rule (d) keeps the sealed level whenever 12 clean members exist and falls back to the sealed
10-or-11 behaviour below that. Neither (a) nor (d) changes collection code. Rule (d) adds a change inside
one desk method that already exists; a defect in it is a desk defect, cured by a re-harvest on identical
bytes, and loses no window. Building the same 12-member bound in the chain (the draft's option (b)) would
change collection code and is refused for that reason alone. A corpus of 15 (option (c)) pays part of both
prices: a mean bound of 2.62 σ, and room for about two bursts of outside load where 18 has four. Dropping
the envelope and screening on the repeatability term alone would change the registered formula in the core
and is refused.

## 3. What does not change

| Item | Value | Where | Why it still holds with 18 |
|---|---|---|---|
| Corpus minimum | 10 kept members | registration 5.3 line 2755; `whole_window.py` 136 | The constant is not edited. |
| Idle-admission limits | busy share p95 ≤ 0.5; processor power p95 ≤ 1.0 W; two attempts | `quiet_mac_p2_b5.json` | The policy file is not edited. The count of section 1.4 gives no evidence that the limits are wrong. |
| Contention limit | 0.05 CPU-s/s for any outside process | registration 4.2, 4.3 | Not edited. Registration section 14 Q3 (line 5778) stays open as written. |
| Cell minimum | 5 of 10 units in each stratum | registration 6.6 line 3996 | Not touched; the corpus is not a reported cell. |
| Reference minimum | 2 surviving references at each end | registration 0.12 | Not touched. |
| Catalog effects | `neg8.bound_not_derived` and `neg8.screen_failed` remove the window; `neg8.corpus_member_dropped`, `member.retried`, `whole_window.not_passed`, `yield.stage_low` are disclosed | `flag_catalog.json` (read by this seat: family, effect and blinding of each) | The catalog file is not edited. No code is added or removed. |
| Blinding | structure only until the release event | registration 8, line 4654 | Six more bundles land in the bound runs root, which is already restricted as a whole. |
| The mint's closed list | five validity reasons | registration 5.3 lines 2855 to 2861 | Imported by the harvest from the mint, not copied. |
| The physics drop | six codes | registration 5.3 lines 2887 to 2890 | The six codes are unchanged. What changes is that the desk method which applies them now builds the clean bound on every window and caps it at 12 (section 2.1). |
| The bound formula and the multipliers | the larger of the envelope and t × s × √(1/n_s + 1/n_e) (section 2.4) | registration 0.12 lines 1001 to 1008; `aggregate.py` 41 to 59 | Not edited. The deciding bound rests on 10, 11 or 12 members, as the sealed sentence at line 1004 says. |
| The chain, the driver, the runner, the core at the new H_claim | byte-identical to the first seal's H_claim | section 4.3, "What must not change" | The count the chain reads comes from the plan tree, which is regenerated. |

**The protections against selecting on an outcome, one by one.**

- *What decides membership.* Membership is decided by status, by the mint's five validity reasons, one of
  which (`precheck_ineligible`) can turn on the ratio of a member's timing envelope to its own energy
  (`reduce.py` `anchor_energy_envelope_exceeds_quarter_metric`), and by the six physics codes, and at the
  desk by committed position (the cap). No step reads the size of an energy for any other purpose. In the
  code: the chain's retry decision counts summary statuses (`chain.py` lines 822 to 835); the chain's prune
  asks the mint which members it drops, and the mint's five reasons are validity tests that would also remove
  a science member; the harvest's physics drop reads the monitor's journals; the cap reads the committed
  order file. Section 2.2 builds the one energy-dependent reason and says why its effect on this corpus is
  negligible and how it is disclosed. The cap is applied after the physics drop, so no step chooses which
  twelve by looking at energies.
- *All 18 always run.* There is no rule of the form "run more members if the first ones look bad". This is
  why the ruling preferred 18 unconditional members to a spare stage triggered at run time: a rule with no
  run-time decision cannot be steered.
- *A succeeded member left out for any other reason still removes the window.* The harvest accepts a
  collected manifest only if its members are committed members, each once, in committed order, at least 10,
  and every member left out either did not succeed or was dropped by the mint for one of the five reasons;
  any other succeeded member left out is a selected corpus and gives `neg8.bound_not_derived`
  (`harvest.py` harvest pin lines 4703 to 4737; registration lines 2775 to 2781 and 2873 to 2875). That test
  compares the collected list with whatever the committed manifest lists, so it applies to 18 as it does
  to 12. The cap does not weaken it: the cap is applied at the desk to the clean bound, and the chain's
  collected manifest still lists every succeeded member the mint kept, so the test is unchanged (rule item 6).
- *The cap is the one new accepted omission, and it is by position.* A member beyond the cap is not dropped
  for cause: it gets no `neg8.corpus_member_dropped` flag, the catalog gains no code, and nothing uses its
  energy (rule item 5).
- *The order is fixed in a committed file* whose SHA-256 each pack's plan tree pins.
- *Re-arming reads no energy.* Registration section 7.6 (line 4637) is unchanged.

## 4. Exact change list

### 4.1 Does any code fix the number 12? What this seat found by reading

Search: the literal `12`, `twelve` and `range(1, 13)` in `joulewise/b5/*.py`, `joulewise/whole_window.py`,
`joulewise/hazards/*.py`, `joulewise/flags/*.py`, `joulewise/window_lineage.py`, `scripts/run_campaign.py`,
`scripts/run_night.py`, `scripts/size_b5_window.py`, `scripts/write_b5_window_plan.py`,
`scripts/write_b5_identity_pins.py`, `scripts/hazard_monitor.py`, `scripts/magistrate_watchdog.py`, the three
packs' generators, and the tests; then the names that carry the corpus size (`expected_count`,
`planned_n_bundles`, `bound_count`, `planned_bound_bundles`, `NEG8_DRIFT_MINIMUM_N`, `NEG8_RETRY_MINIMUM`,
`CORPUS_MIN_VALID`, `REGISTERED_NEG8_REFERENCE_CORPUS_*`). Nothing was executed; this is a reading.

**Code a window executes: no live logic holds the number 12.**

| File and line | What is there | Kind |
|---|---|---|
| `joulewise/b5/chain.py` 1126, 1132 | members per stage and the stage's time allowance come from the plan tree's `expected_count` | live logic, reads the count |
| `chain.py` 514, 516 | `--max-failures` is set to the stage's `expected_count` | live logic, reads the count |
| `chain.py` 822 to 835 (retry helper) | counts the members the manifest lists; compares with the minimum 10 | live logic, reads the list |
| `chain.py` 567 to 628 (prune helper) | iterates the manifest's members | live logic, reads the list |
| `chain.py` 184, 185 | wall budgets of the prune and of the derivation: 1,800 s each | live logic; not a count. Registration 5.5 puts 12 bundles at about 270 to 320 s, so 18 fit |
| `chain.py` 64, 68 | module docstring: "all 12 kept", "committed 12-member bytes" | comment |
| `chain.py` 268, 271 | the same words inside the `DEVIATIONS` tuple | **text that is written out**: every chain script prints the tuple as shell comments (line 1075) and every window plan stores it as `chain_deviations` (`joulewise/b5/plan.py` 910, 958). No logic reads it. Left as it is and registered as deviation 9 (J5, section 8) |
| `chain.py` 1198 | "A pruned copy (10 or 11 of 12) derives" | a shell comment rendered into the chain script |
| `chain.py` 23, 117, 1070; `driver.py` 2585, 2607 | 12 as the chain's exit code for a failed pre-calibration screen | unrelated number |
| `joulewise/b5/driver.py` 1402 to 1414, 1432 to 1477 | the yield plan counts the run ids in the stage's order manifest | live logic, reads the list |
| `driver.py` 152, 1392 to 1394 | `CORPUS_MIN_VALID = 10`; the stage's minimum is min(10, planned) | live logic; no 12 |
| `joulewise/b5/plan.py` 767 to 777 | planned bytes = bytes per member × (sum of `expected_count` + spares) | live logic, reads the count |
| `plan.py` 881 | `window_max_s` = 60 × ceil((programmed span + 3,300) / 60) | live logic; no count |
| `scripts/run_campaign.py` | no literal 12 except a digest prefix length and a tolerance | none |
| `joulewise/whole_window.py` | no literal 12 except tolerances of 1e-12; minimum 10 at 136 | none. **But see F2 below** |

**Desk code.**

| File and line | What is there | Kind |
|---|---|---|
| `joulewise/b5/harvest.py` (harvest pin) 4699 to 4721 | the collected members must be a subset of the committed list, in order, at least 10 | live logic, reads the list |
| `harvest.py` 4514, 4516, 4859 | "committed 12-member corpus", "10 of the 12" | comments |
| `harvest.py` (harvest pin) 5339 to 5436 | `neg8_corpus_physics`: builds the clean bound; returns at 5373, 5374 when no physics code fired; has no cap | live logic, no literal 12. **This is the one method the desk rule of section 2.1 changes** (section 4.3, table F) |
| `scripts/size_b5_window.py` 396 | each stage's order manifest must list `expected_count` members | live logic, reads the count |
| `size_b5_window.py` 585 to 598 | the corpus stage is found from the stage rows; the retry is charged from its member count | live logic, reads the count |
| `size_b5_window.py` 112, 113 | `B5_BOUND_DERIVATION_S = 320`, `B5_CORPUS_PRUNE_S = 320` | **live sizing constants chosen for 12 bundles**. See F4 |
| `size_b5_window.py` 108 | comment | comment |
| `size_b5_window.py` 680, 684 | "re-reduces 12 bundles", "the same 12 bundles" | **text written into `sizing_b5.json`** (`terms.bound_derivation.source`, `terms.corpus_prune.source`). No logic reads it. Left as it is and covered by deviation 9 |
| `scripts/rehearse_b5_real.py` 98 | the real-model rehearsal keeps 1 corpus member by default | rehearsal setting; see section 6 and 7 |

### 4.2 Four findings that change what the build is

**F1. The pack generators fix 12 as literals. This is live generator logic.** The generators run at the desk,
never in a window, but each sits in a pack directory and so is listed in the sealed inventory.

| File | Line | Literal | New value |
|---|---|---|---|
| `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py` | 241 | SHA-256 of the corpus order manifest, `0ec9d68a…` | the new file's digest |
| same | 246 to 248 | SHA-256 of `settled_corpus.json`, `74ccdaec…` | the new file's digest |
| same | 727 | `"bound_count": 12` (plan tree, `runtime_budget`) | 18 |
| same | 1818 | `"expected_count": 12` (stage `alpha-bound-collection`) | 18 |
| same | 2851 | `"planned_bound_bundles": 12` (calibration plan) | see F3 |
| `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py` | 241, 246 to 248, 727, 1818, 2851 | the same five | the same |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py` | 2365 | `12`, the expected count of stage `gamma-bound-collection` | 18 |
| same | 2056 | `"planned_bound_bundles": 12` (calibration plan) | see F3 |
| `configs/campaigns/d117_contrast_v5/generate_configs.py` | 2056, 2365 | a twin of the file above (they differ at line 21 only); two tests load this copy | the same edits |

The contrast generator computes the two corpus digests from the files (lines 2177, 3387) and reads the
external manifest's own count for its pin record (line 2180), so it has no digest literal to edit.

So the build is not configuration alone: it edits generator source in four files. At the new H_claim it edits
no file among the driver, the chain, the runner, the controller, the hazard modules, the harvest or the core.
The harvest's one desk method changes afterwards, on the harvest lane (section 4.3, table F).

**F2. The core reader authenticates a bound against the old corpus file, by path.** A bound records the
SHA-256 of the manifest it was built from. The core reader `whole_window.load_neg8_drift_bound_artifact`
accepts a bound only if that digest is the digest of one fixed file (`whole_window.py` lines 150 to 157 and
1703 to 1720): `configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json`. That is the
*historical* corpus directory, not `neg8_reference_corpus_v5`. Today the two directories hold byte-identical
manifests (both SHA-256 `74ccdaec74497c3aa7c074ef1129ec2bf2cc01d8ac14d3d07be77ab468599688`, computed by this
seat), which is the only reason a full 12-member block-5 bound passes the core reader. The ruling cites line
157 for this and missed that the directory at lines 150 to 156 is the historical one.

Once the `_v5` manifest lists 18 members under a new id, its bytes differ from the historical file, and **the
core reader will accept no block-5 bound at all**, however many members were kept. What follows is already
registered for a 10- or 11-member bound (section 5.3, lines 2769 to 2781, and lines 2810 to 2846):

```
 the chain's bound  -->  core reader: digest equals the historical 12-member file?
                              |
                              +-- yes (today, when all 12 kept): "route 1", the stored screen stands
                              |
                              +-- no (today with 10 or 11 kept; with 18 committed: ALWAYS)
                                     |
                                     v
                         the verdict writer treats the bound as absent; the stored screen
                         fails with exactly the two "bound underived" conditions
                                     |
                                     v
                         harvest "route 2": validates the bound against the window's own
                         collected manifest and checks every member against its bundle
                                     |
                                     v
                         harvest, after the monitor join: builds the clean bound from the
                         first 12 clean members in committed order (section 2.1)
                                     |
                                     v
                         harvest re-screen against the clean bound; that re-screen decides,
                         and the drift allowance comes from the clean bound
```

Each arrow is "then"; the two branches are the reader's two outcomes. The last two boxes are the desk rule
of section 2.1; under the first seal the clean-bound box ran only when a physics code had fired. Route 2
itself needs no code change: the chain
always writes the collected manifest and the driver always records it (`chain.py` 629 to 635 and 1336 onward),
and when nothing was dropped the collected manifest is the committed 18-member file byte for byte (`chain.py`
627, 628: the bytes are re-rendered only if a member was dropped). But three things become true of **every**
window, not only of a window that lost members:

- the stored verdict reads "failed" and the window carries `whole_window.not_passed` (disclosed only);
- the harvest's re-screen against the clean bound, not the stored verdict, decides the screen;
- every contrast needs part (c) of lane L9-NEG8 (a planned repair of claim-time code, which never runs in a
  window; analysis plan section 11, line 729) before it can be claimed, because the claim validator
  rejects a row whose stored screen failed before it reads the harvest's record (registration 0.12, "Which
  bracket carries the allowance", line 1205 onward). That lane was already required before any claim; it was
  needed for every floor and for some contrasts, and is now needed for every contrast.

Two more facts about route 2 hold for every window now, and the registration's 5.3 will state all three
(section 4.5, edit R17; the cold ruling's correction 9):

- *The stored bracket's other conditions.* The **stored bracket** is the NEG-8 part of the verdict row that
  the verdict writer stored. With no bound it carries two conditions, `neg8_drift_bound_underived` and its
  idle-subtracted twin (the two "underived" conditions). On the collected-subset route the stored bracket
  must carry no NEG-8 condition other than those two for the re-screen to be evaluated: the harvest records
  the problem `conditions_beyond_bound_underived` and evaluates nothing (`harvest.py` harvest pin lines 5233,
  5234). That guard applies only when the screen step's `survivors` value is false, and the value is true
  whenever a clean bound exists or a reference was lost at the desk (line 4915:
  `survivors = bool(new_losses) or clean_bound is not None`). The always-on clean bound therefore makes it
  true on every window, and the guard no longer runs. So the harvest's always-on clean bound must handle a stored
  bracket that carries another condition, and harvest-lane test (c) of section 4.7 fixes that it still fails
  or re-derives correctly.
- *What the allowance consumer checks.* The **allowance consumer** is the core function that reads the
  window's drift allowance for a claim. It checks a clean bound's arithmetic and digest against the
  harvest's record, not its corpus identity (`whole_window.py` harvest pin lines 7322 to 7340). That is the
  sealed behaviour, now applied to every window.

The alternatives are a change to the core (point the reader at the `_v5` file, or let it accept either), which
is collection code and would stop historical 12-member bounds from authenticating, or overwriting the
historical file, which rewrites history. Ruled (J2, section 8): route 2 for every window and no core change.

**F3. One literal feeds a digest that is stamped into all 280 science configurations.** Each pack's
`calibration_plan.json` carries `"planned_bound_bundles": 12` (line 1653 in the two floor packs, 1150 in
GAMMA's). The SHA-256 of that file is written into every science configuration of the pack as the tag
`calibration-plan-sha256=<digest>` and into every science stage's order manifest (counted by this seat: 100,
100 and 80 configurations carry their pack's digest). No program under `joulewise/` or `scripts/` reads
`planned_bound_bundles` or `bound_count` (searched; `bound_count` is a second descriptive field, in each plan
tree's `runtime_budget`). Two ways to build:

- *Leave `planned_bound_bundles` at 12.* The calibration plans and all 280 science configurations keep their
  bytes, so the science members of the new block are byte for byte the ones the three ALPHA attempts ran. The
  field is then a stale descriptive value. The registration has a precedent: the plan trees' `attempt_policy`
  is "superseded by the flag catalog and disclosed, not regenerated" (section 5.2; deviation 2, section 10).
- *Change it to 18.* Truthful files, but three new calibration-plan digests, 280 changed science
  configurations, 12 changed science order manifests, and every pin on them.

Ruled (J3, section 8): the first, registered as deviation 8. The two descriptive fields are treated
differently, and the registration says why: `planned_bound_bundles` stays 12, because changing it would
change 280 science configurations; `bound_count` becomes 18, because the plan tree that holds it is
regenerated in any case. The planning estimate that the plan tree prints beside `bound_count` was computed
for 12 and is stale (deviation 8's last sentence, section 4.5).

**F4. Two sizing charges were chosen for 12 bundles.** The sizer charges the bound derivation and the corpus
prune 320 s each, from an estimate of 270 to 320 s for re-reducing 12 bundles that the registration calls
"never measured live" (section 5.5, line 3018). Scaled to 18 bundles that estimate is 405 to 480 s each, up to
160 s over the charge, 320 s for both. The chain's wall budget for each is 1,800 s (`chain.py` 184, 185), so
neither stage is cut. The programmed span exceeds the expected chain by more than 70,000 s (section 4.6), so
the window deadline is not at risk. Ruled (J4, section 8): the two constants stay at 320 s and the
registration's 5.5 states the under-charge. The rehearsal of section 7 (gate 7) records both wall times; a
measured time above 1,200 s for either goes to a consult before the arm.

### 4.3 Files that change

Old and new values. "Generator" names the program that writes the file; "hand" means no generator exists.

**A. The corpus directory `configs/campaigns/neg8_reference_corpus_v5/` (hand; commit `cfd51a963` created it
as copies and no script names it).**

| # | File | Old | New |
|---|---|---|---|
| 1 to 6 | `neg8-refcorpus-r13.json` … `-r18.json` | absent | byte copy of `neg8-refcorpus-r01.json` with `"run_id"` set to the file's own id; 1,319 bytes each |
| 7 | `order_manifest.json` | `planned_n_bundles` 12; 12 rows; `manifest_id` `neg8-reference-corpus-order-v1`; `plan_id` `neg8-reference-corpus-m3max-qwen25-1p5b-v1` | `planned_n_bundles` 18; rows 13 to 18 appended in the pattern of row 12 (`index`, `rep`, `block_index` = 13..18, `position_in_block` 1, same `model_tag`, `workload`, `role`); `manifest_id` `neg8-reference-corpus-order-v2`; `plan_id` = the new corpus id |
| 8 | `derivation/settled_corpus.json` | `corpus_id` `neg8-reference-corpus-m3max-qwen25-1p5b-v1`; 12 members | `corpus_id` `neg8-reference-corpus-m3max-qwen25-1p5b-v2-n18`; 18 members, rows 13 to 18 appended; every other key unchanged |
| 9 | `README.md` | "collects 12 sequential, same-condition copies" | 18, and one sentence naming this erratum |

The historical directory `configs/campaigns/neg8_reference_corpus/` is not touched.

**B. Generator source (hand edits of literals, F1).**

| # | File | Change |
|---|---|---|
| 10, 11 | the two floor generators | line 241: `<ORDER_MANIFEST_SHA256>`; lines 246 to 248: `<SETTLED_CORPUS_SHA256>` (the two placeholders are filled by step 2 of section 4.4); 727: 18; 1818: 18; 2851: unchanged at 12 (deviation 8) |
| 12, 13 | the contrast generator and its twin | line 2365: 18; 2056: unchanged at 12 (deviation 8) |

**C. Generated pack files.**

| # | File | Generator | What changes |
|---|---|---|---|
| 14, 15 | `d117_floor_qwen3-1p7b_v5/plan_tree.json`, `plan_tree.sha256` | that pack's `generate_configs.py` | corpus stage `expected_count` 12 → 18; `external_inputs.manifests[0]`: `expected_count` 18, six more member pins, new manifest digest; the settled-corpus digest in the derivation stage and in `external_inputs.artifacts[0]`; `runtime_budget.bound_count` 18 |
| 16, 17 | the same two files of `d117_floor_qwen3-8b_v5` | its generator | the same |
| 18, 19 | the same two files of `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` | its generator | stage `gamma-bound-collection` `expected_count` 18; `external_inputs[0]` with 18 pins and the new manifest digest; `external_inputs[1]` the new settled-corpus digest |

Two descriptive fields are treated differently (finding F3): the plan tree's `runtime_budget.bound_count`
changes to 18, and each calibration plan's `planned_bound_bundles` does not change and stays 12 (deviation 8).
The three `calibration_plan.json` files are therefore not in this table.

If the generators rewrite any other file of a pack, that is a defect of the build: a `git diff --stat` of
each pack directory must show the generator, `plan_tree.json`, `plan_tree.sha256` and (only if it embeds a
plan-tree digest) the pack's `README.md`, and nothing else.

**D. Block-level generated files in `configs/campaigns/v5_claim_25g83/`, committed at the new H_claim.**

| # | File | Generator | What changes |
|---|---|---|---|
| 20 | `sizing_b5.json` | `scripts/size_b5_window.py` | the three plan-tree digests, the corpus manifest digest, members, spans and deadlines (section 4.6). Its two `source` strings still say 12 (deviation 9) |
| 21 | `identity_pins.json` | `scripts/write_b5_identity_pins.py` | it records the three plan-tree digests; no model or runtime pin changes |

**E. Other tracked files at the new H_claim.**

| # | File | Generator | What changes |
|---|---|---|---|
| 22 | `configs/pins/registry.json` | `scripts/digest_pin_census.py --write` | six new corpus files and the changed digests |
| (tests) | the files of section 4.7, window side | hand | assertions of 12, 119, 101, 126 and the sizing numbers; the two new window-side tests |

**The seal commit: three files, one parent.** The seal commit's only parent is the new H_claim, and it
changes exactly the three seal documents, as registration section 11 states (lines 5051 to 5055) and as the
first seal did (`git show --stat ab7b21e57`: one parent `a64000884`, three files).

| # | File | Generator | What changes |
|---|---|---|---|
| 23 | `sealed_inventory.json` | `docs/process_traces/2026-10-07-block5-seal/bench/make_sealed_inventory.py` | regenerated from a clean checkout of the new H_claim |
| 24 | `registration_block5.md` | hand | every edit of section 4.5, table R |
| 25 | `analysis_plan_block5.md` | hand | every edit of section 4.5, table P |

*Why three files and not one.* The sealed registration prints H_claim's hash (lines 1650 and 5542), the
three plan-tree digests (750 to 756), the identity-pins digest (2523, 2524 and 5690) and the sizing digest
(3026, 3027). None of those values exists before the merge that makes the new H_claim, and a file cannot
name the commit that contains it. So the two documents must be edited after the new H_claim exists, and the
only commit that may then change them is the seal commit. The landing test agrees: it forbids only paths
outside the three seal documents (`tests/test_b5_seal_landing.py` lines 97 to 110; `SEAL_DOCUMENT_PATHS`,
`harvest.py` lines 166, 167). **This departs from magistrate brief 40, section 9, step 2**, which says to
commit "that one file" (the inventory). That step was written for a cure that leaves the registration's text
alone. It is wrong against registration section 11, and the registration governs (the cold ruling, A.2).

*What the inventory lists.* The inventory's roots are `joulewise`, `scripts`, the three pack directories and
the flag catalog (`scripts/rehearse_b5_real.py` lines 286 to 290). The corpus directory is not a root. The
six new corpus files and the two changed manifests enter the inventory only through each plan tree's
`external_inputs`, which pins each member file and the settled-corpus digest, and the plan trees are in the
inventory. Nobody should expect to find `neg8-refcorpus-r13.json` listed in `sealed_inventory.json`.

**F. Desk side, on the harvest lane, after the seal commit.** These files are not at the new H_claim and no
window reads them.

| # | File | What changes |
|---|---|---|
| F1 | `joulewise/b5/harvest.py`, method `neg8_corpus_physics` (harvest pin lines 5339 to 5436) | the desk rule of section 2.1 item 3: the method runs on every window (today it returns at line 5373 when no physics code fired); it orders the members by the committed `order_manifest.json`; it keeps the first 12 clean members; the clean manifest it writes leaves out the removed and the capped members; `derived/neg8-corpus-physics.json` gains the key `beyond_cap` and `members_kept` is the count after the cap. No flag code is added |
| F2 | the harvest lane's tests | tests (a) to (d) of section 4.7 |
| F3 | `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` | a new `B5-HARVEST-PIN` addendum naming the harvest-lane commit that holds F1 and F2, built on the new seal commit, written and pushed before the first arm. (The same file also gains, at gate 4 of section 7, the section that pins the new digests.) |

**What must not change** (the cold ruling, section D): `joulewise/b5/chain.py`, `driver.py`, `plan.py`,
`scripts/run_campaign.py`, `scripts/run_night.py`, the controller, `joulewise/hazards/`,
`scripts/hazard_monitor.py`, `joulewise/whole_window.py` at the new H_claim, `flag_catalog.json`,
`quiet_mac_p2_b5.json`, the three `calibration_plan.json`, the 280 science configurations and the 12 science
order manifests, the reference and spare directories, `configs/campaigns/neg8_reference_corpus/`
(historical), the four pinned estimator files and `scripts/prewindow_check.sh`, `scripts/size_b5_window.py`
(source), the old measurement clone. At the new H_claim `joulewise/b5/harvest.py` also keeps the first
seal's bytes (J6).

**Count.** At the new H_claim, 22 files change (9 in the corpus directory, 4 generators, 6 generated pack
files, `sizing_b5.json`, `identity_pins.json`, the pin registry), plus tests, plus a pack's `README.md` only
if it embeds a plan-tree digest. The seal commit changes 3 files. That is the draft's 25; `chain.py` is not
among them and is not conditional any more. On the harvest lane, one code file, its tests and the seal
record change.

### 4.4 Regeneration commands, in order

Run from a linked worktree on a branch from main. The interpreter is the one the seal used,
`/opt/homebrew/bin/python3.13` (not the project environment).

```sh
# 1. The six member configurations (no generator exists).
cd configs/campaigns/neg8_reference_corpus_v5
for i in 13 14 15 16 17 18; do
  sed 's/"run_id": "neg8-refcorpus-r01"/"run_id": "neg8-refcorpus-r'"$i"'"/' \
      neg8-refcorpus-r01.json > "neg8-refcorpus-r$i.json"
done
# check: each new file differs from r01 in line 3 only and is 1,319 bytes
for i in 13 14 15 16 17 18; do diff neg8-refcorpus-r01.json "neg8-refcorpus-r$i.json" | grep -c '^[<>]'; done  # 2 each
cd -

# 2. By hand: order_manifest.json, derivation/settled_corpus.json, README.md (table A, rows 7 to 9).
shasum -a 256 configs/campaigns/neg8_reference_corpus_v5/order_manifest.json \
              configs/campaigns/neg8_reference_corpus_v5/derivation/settled_corpus.json

# 3. By hand: the generator literals (table B), using the two digests step 2 printed.

# 4. The three packs. The floor generators find the prefill pin inside the pack.
python3.13 configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py
python3.13 configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --check
python3.13 configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py
python3.13 configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py --check
python3.13 configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --no-preserve-current-frozen-bytes
python3.13 configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --no-preserve-current-frozen-bytes --check
python3.13 -m joulewise.b5.reference_spares --check     # the spare pins in the plan trees are intact

# 5. The block-level files.
python3.13 scripts/size_b5_window.py && python3.13 scripts/size_b5_window.py --check
python3.13 scripts/write_b5_identity_pins.py --check    # expected to FAIL first: it pins the old plan trees
#    then rewrite it with the arguments the sealed registration records for it (section 4.6 item 3,
#    lines 2505 to 2525) and run --check again
python3.13 scripts/digest_pin_census.py --write

# 6. The per-pack diff check of table C, before the merge.
for p in d117_floor_qwen3-1p7b_v5 d117_floor_qwen3-8b_v5 d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5; do
  git diff --stat main -- "configs/campaigns/$p"
done

# 7. After the merge (gate 3 of section 7): the values that fill the placeholders of section 4.5.
git rev-parse HEAD                                           # on main at the merge commit: <NEW_H_CLAIM>
shasum -a 256 configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json                    # <PT_ALPHA_SHA256>
shasum -a 256 configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json                      # <PT_BETA_SHA256>
shasum -a 256 configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json     # <PT_GAMMA_SHA256>
shasum -a 256 configs/campaigns/v5_claim_25g83/sizing_b5.json                              # <SIZING_SHA256>
shasum -a 256 configs/campaigns/v5_claim_25g83/identity_pins.json                          # <PINS_SHA256>
shasum -a 256 configs/pins/registry.json                                                   # <REGISTRY_SHA256>

# 8. The seal commit (gate 4 of section 7): the inventory, then the two documents edited by section 4.5,
#    then one commit of exactly those three files whose only parent is the new H_claim.
python3.13 -B docs/process_traces/2026-10-07-block5-seal/bench/make_sealed_inventory.py <clean checkout at new H_claim> <out.json>
python3.13 -m unittest tests.test_b5_seal_landing
```

The commands of steps 4 and 5 are the ones the pack READMEs and the registration name; the drafting seat did
not run them, because every one of them writes or was built to be run in a build worktree. The builder
records the exit code of each `--check`. Step 2's two digests are `<ORDER_MANIFEST_SHA256>` (the first file)
and `<SETTLED_CORPUS_SHA256>` (the second).

### 4.5 Text edits to the registration and the analysis plan

This section is the whole instruction for the two hand-edited seal documents. The writer makes these edits
after the new H_claim exists, and they go into the seal commit with the regenerated inventory (section 4.3).

**How to read an edit.** Each edit has a number (R for the registration, P for the analysis plan), the line
or lines of the sealed text it changes, the old wording and the new wording. "→" separates old from new.
"Insert after" adds words and removes none. Words of a line that an edit does not quote stay as they are.

**Rules for the writer.**

1. *Line numbers are of the sealed text before any edit*: `registration_block5.md`, 6,173 lines, SHA-256
   `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841`; `analysis_plan_block5.md`, 999 lines,
   SHA-256 `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a` (both computed with
   `shasum -a 256` on main `3f564499e`). Several edits add lines, so make the edits from the bottom of each
   file upward, or find each place by its quoted old wording. A quoted old wording may run over a line break
   of the file; the break is not part of the quote.
2. *In the analysis plan, line 354 must stay line 354.* A test data file names that line
   (`tests/fixtures/d165_rationale_allowlist.json` lines 279 to 293). Edit P1 changes line 3 inside the line
   and adds no line break. Edits P2 to P4 are below line 354.
3. *Placeholders.* A value that exists only after the build is written here as a name in angle brackets. The
   writer replaces every occurrence of a name with the same value. No angle-bracket name may remain in either
   document; the text gate (section 7, gate 4(c)) searches for `<` followed by a capital letter.
4. *Predicted numbers.* The members, spans, deadlines, chain lengths and disk figures below are the drafting
   seat's arithmetic from the registered rules (section 4.6). Before writing each one, the writer reads it
   from the regenerated `sizing_b5.json` or recomputes it. If a value differs from the one printed here, the
   writer stops and reports the difference as a finding; the writer does not silently write a different
   number.

**The placeholders, and the command whose output fills each.** Twelve names. The commands are steps 2 and 7
of section 4.4 unless a row says otherwise.

| Placeholder | What it is | Command | Used in |
|---|---|---|---|
| `<NEW_H_CLAIM>` | the 40-character hash of the merge commit that is the new H_claim | `git rev-parse HEAD` on main at the merge commit | R7, R34, R38 |
| `<PT_ALPHA_SHA256>` | SHA-256 of ALPHA's plan tree at the new H_claim | `shasum -a 256 configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json` | R4, R35 |
| `<PT_BETA_SHA256>` | SHA-256 of BETA's plan tree | `shasum -a 256 configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json` | R4, R35 |
| `<PT_GAMMA_SHA256>` | SHA-256 of GAMMA's plan tree | `shasum -a 256 configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json` | R4, R35 |
| `<SIZING_SHA256>` | SHA-256 of the regenerated sizing output | `shasum -a 256 configs/campaigns/v5_claim_25g83/sizing_b5.json` | R24, R35 |
| `<PINS_SHA256>` | SHA-256 of the regenerated identity pins | `shasum -a 256 configs/campaigns/v5_claim_25g83/identity_pins.json` | R12, R35 |
| `<REGISTRY_SHA256>` | SHA-256 of the regenerated pin registry | `shasum -a 256 configs/pins/registry.json` | R35 |
| `<ORDER_MANIFEST_SHA256>` | SHA-256 of the 18-row corpus order manifest | `shasum -a 256 configs/campaigns/neg8_reference_corpus_v5/order_manifest.json` (step 2) | section 4.3 table B only; neither document prints it |
| `<SETTLED_CORPUS_SHA256>` | SHA-256 of the 18-member settled-corpus manifest | `shasum -a 256 configs/campaigns/neg8_reference_corpus_v5/derivation/settled_corpus.json` (step 2) | section 4.3 table B only; neither document prints it |
| `<DRY_RENDER_RECORD_PATH>` | the path of the new dry-render record (section 7, gate 2) | chosen by the builder when the record is written; a file beside `/Users/edr/night-archive/gate-prune/dry-records-2/DRY_RECORDS.md` | R8 |
| `<DRY_RENDER_RECORD_SHA256>` | SHA-256 of that record | `shasum -a 256 <DRY_RENDER_RECORD_PATH>` | R8 |
| `<SEAL_DATE>` | the UTC date on which the seal commit is made | `date -u +%F` when the writer makes the commit | R1, R34, P1, P4 |

#### Table R: the registration, in line order

**R1. Line 3, the status line.** (Added by the corrections seat so that the file says it was amended; the
cold ruling did not order it and the magistrate may strike it.)
"Status: **Revision 12, 2026-10-07.** This is the text" → "Status: **Revision 12, 2026-10-07, amended on
`<SEAL_DATE>` by the prospective cold erratum of 2026-10-09 (§14 Q16: an 18-member NEG-8 corpus, superseding
the first seal).** This is the text"

**R2. Lines 87 and 88, the change summary of revision 4, item 1.**
"each window starts with 12 reference runs, the NEG-8 corpus, from which a drift bound is derived (§0.12). A
window in which only 10 or 11 of them succeeded no longer loses that bound: the harvest validates the bound
against the members actually collected and re-screens the window against it (§14 Q1 closed)." →
"each window starts with 18 reference runs, the NEG-8 corpus, from which a drift bound is derived (§0.12);
revision 4 wrote 12, and the erratum of 2026-10-09 made it 18 (§14 Q16). A window in which as few as 10 of
them succeeded no longer loses that bound: the harvest validates the bound against the members actually
collected, builds the deciding bound from at most 12 of them (§5.3, "the desk cap") and re-screens the window
against it (§14 Q1 closed)."

**R3. Line 406.** "the 12 NEG-8 corpus members" → "the 18 NEG-8 corpus members"

**R4. Lines 754 to 756, the plan-tree digests.** Lines 747 to 753 stay: they are a dated record of the int5
head `fe28e5a0c`, and the three old digests in lines 750 to 752 stay in them as history.
"and recorded in the sizing
output (§5.5); this author computed the same three values again at the int5 head `9395cecfb`. At H_claim the three
files hash to ALPHA `1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a`, BETA `0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670` and GAMMA `8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf`." →
"and recorded in the sizing output of that head (§5.5); this author computed the same three values again at
the int5 head `9395cecfb`, and the three files had the same values at the first seal's H_claim,
`a64000884ef5bb4b76415835f02f39803f6eb620`. The erratum of 2026-10-09 gave the NEG-8 corpus 18 members (§14
Q16), which changed each plan tree's corpus stage and its pins of the corpus files. At H_claim (§2, "Before
ALPHA-1 arms", item 1) the three files hash to ALPHA `<PT_ALPHA_SHA256>`, BETA `<PT_BETA_SHA256>` and GAMMA
`<PT_GAMMA_SHA256>`, computed with `shasum -a 256` at H_claim, equal to each pack's committed
`plan_tree.sha256` there, with each pack's `generate_configs.py --check` exiting 0, and recorded in the
sizing output (§5.5)."

**R5. Line 976.** "Each window runs 12 at its start" → "Each window runs 18 at its start"

**R6. Line 1411.** "the 12 NEG-8 corpus
members" → "the 18 NEG-8 corpus members"

**R7. Lines 1650 and 1651, H_claim.**
"**H_claim is `a64000884ef5bb4b76415835f02f39803f6eb620`**, on
branch `integrate/2026-10-07-int5`. It carries PR #483" →
"**H_claim is `<NEW_H_CLAIM>`**: the merge into main of the build that the erratum of 2026-10-09 ordered (§14
Q16; the 18-member corpus files, four generator literals, the three regenerated plan trees, the sizing
output, the identity pins and the pin registry). It contains the first seal's H_claim,
`a64000884ef5bb4b76415835f02f39803f6eb620`, and changes no file under `joulewise/` or `scripts/`. The first
seal's H_claim, on branch `integrate/2026-10-07-int5`, carries PR #483"

**R8. Lines 1788 and 1789, the dry render record: insert, change nothing.** The record of 2026-10-07 (lines
1769 to 1789, with "NEG-8 corpus 12 listed and 12 kept" and bound bundles 12/12/12) stays as the record of
the first seal's render. Insert after the sentence that ends "(`dry-records/DRY_RECORDS.md`) number for
number.":
"After the erratum of 2026-10-09 gave the corpus 18 members (§14 Q16), the six renders were repeated on the
build branch whose merge is H_claim, with the pack bytes of H_claim: `<DRY_RENDER_RECORD_PATH>`, SHA-256
`<DRY_RENDER_RECORD_SHA256>`. Every count equals the table's except the bound bundles, which are 18/18/18 in
all six rows, and the NEG-8 corpus, 18 listed and 18 kept; the corpus stage's rendered command carries
`--max-failures 18`. The rendered comments still say 12 (§10, deviation 9)."
If the new record does not show exactly that, the sentence is not written and the difference is a finding
(section 7, gate 2).

**R9. Lines 2240 and 2241, planned bytes.**
"22.4 GiB for ALPHA and BETA (119 + 7 = 126 members), 19.2 GiB for GAMMA
(101 + 7 = 108)." → "23.5 GiB for ALPHA and BETA (125 + 7 = 132 members), 20.3 GiB for GAMMA (107 + 7 =
114)."

**R10. Lines 2246 and 2247, required free disk.**
"3 × 22.39 + 20 = 87.2 GiB required for ALPHA and BETA, and 3 × 19.20 + 20 = 77.6 GiB for
GAMMA, against 264 GiB free on 2026-10-05 (revision 6, before the spares: 83.5 and 73.9 GiB)." →
"3 × 23.46 + 20 = 90.4 GiB required for ALPHA and BETA, and 3 × 20.26 + 20 = 80.8 GiB for GAMMA, against
216 GiB free on 2026-10-09 (`df -g`; with the first seal's 12-member corpus: 87.2 and 77.6 GiB; revision 6,
before the spares: 83.5 and 73.9 GiB)."

**R11. Lines 2261 and 2262, and line 2272, ALPHA's `planned_bytes`.**
Lines 2261, 2262: "(`planned_bytes` = 126 × 182 MiB = 24,045,944,832
bytes, the window's 119 members plus its 7 spares, computed by this author; revision 6 showed 119 × 182 MiB)" →
"(`planned_bytes` = 132 × 182 MiB = 25,190,989,824 bytes, the window's 125 members plus its 7 spares; the
first seal, with a 12-member corpus, showed 126 × 182 MiB, and revision 6 showed 119 × 182 MiB)"
Line 2272, inside the thresholds block: `"planned_bytes": 24045944832` → `"planned_bytes": 25190989824`
(The cold ruling's search list has the number with commas; the corrections seat found this second
occurrence, without commas.)

**R12. Lines 2523 and 2524, the identity-pins digest.**
"The file's SHA-256 at H_claim is `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9`. At the int5 head `fe28e5a0c` it was" →
"The file's SHA-256 at H_claim is `<PINS_SHA256>` (`shasum -a 256`; `scripts/write_b5_identity_pins.py
--check` reproduces the file there, exit 0). The file records the three plan-tree digests, which the erratum
of 2026-10-09 changed (§14 Q16); no model or runtime pin in it changed. At the first seal's H_claim and at
the int5 head `fe28e5a0c` it was"
The digest that follows on line 2524 stays: it is now the dated earlier value.

**R13. Lines 2705 to 2714, the corpus retry.**
(a) Line 2705: "when fewer than 10 of the 12 corpus members succeeded" → "when fewer than 10 of the 18 corpus
members succeeded"
(b) Line 2709, insert after the sentence that ends "never a member that was measured and failed.":
"An idle-admission abort leaves a complete failed bundle, so the retry never repairs it. In the two chains
that ran under the first seal every corpus loss was of this kind and the retry measured nothing (§14 Q16).
The retry is kept for the member refused before its bundle exists."
(c) Lines 2711 to 2714, the worked example:
"*Worked example:*
members 4, 5 and 6 are refused before their bundles exist and member 9 is aborted by idle admission (a failed
bundle), so 8 of 12 succeeded. The retry measures 4, 5 and 6, each flagged `member.retried`, and leaves 9 alone. If
all three succeed, 11 have succeeded and the bound is derived from those 11 (§5.3)." →
"*Worked example:* members 4 to 9 are refused before their bundles exist and members 11, 12 and 13 are aborted
by idle admission (failed bundles), so 9 of 18 succeeded. The retry measures 4 to 9, each flagged
`member.retried`, and leaves 11, 12 and 13 alone. If all six succeed, 15 have succeeded: the chain derives
its bound from those 15, and the harvest builds the deciding bound from the first 12 of them, in committed
order, on which no physics code fired (§5.3)."

**R14. Line 2752, the title of 5.3.**
"### 5.3 The NEG-8 corpus may lose up to two members, for validity or for physics" →
"### 5.3 The NEG-8 corpus may lose up to eight members to status, validity or physics; one refused or
indeterminate member still gives `neg8.bound_not_derived`"
(The new title is one line in the file.)

**R15. Lines 2754 to 2757, the registered rule.**
"**Registered rule:** the bound is derived
from the corpus members that were collected and succeeded, provided there are at least 10 of the 12
(`whole_window.NEG8_DRIFT_MINIMUM_N` = 10); t uses n − 1 degrees of freedom. With fewer than 10,
`neg8.bound_not_derived` removes the window." →
"**Registered rule** (as amended by the erratum of 2026-10-09, §14 Q16): the committed corpus has 18 members,
`neg8-refcorpus-r01` to `-r18`, and every one of them runs in every window, in the committed order of the
corpus's `order_manifest.json`; no program decides at run time whether a member runs. *In the window,* the
chain derives a bound from the corpus members that were collected and succeeded, provided there are at least
10 of the 18 (`whole_window.NEG8_DRIFT_MINIMUM_N` = 10). That **in-window bound** rests on 10 to 18 members
and decides nothing. *At the desk,* the harvest builds the bound that decides the screen and the allowance,
the **clean bound**, from at most 12 of those members ("the desk cap", below). So the n of §0.12 is 10, 11 or
12, and t uses n − 1 degrees of freedom. With fewer than 10, in the window or at the desk,
`neg8.bound_not_derived` removes the window. The eight members that the corpus can lose are members that did
not succeed, members the mint omits for one of its five reasons, and members dropped for physics. A member
that the mint refuses or cannot classify (below) is not among them: one such member leaves the window with no
bound."

**R16. Lines 2759 and 2760, "Why it matters".**
"*Why it matters.* At 1 abort in 37 members (the block 2 and 3 record), the chance that all 12 corpus members succeed
is (36/37)¹² ≈ 0.72. A rule that needed all 12 would lose about 28% of windows to the corpus alone." →
"*Why it matters.* The rule was first sized, for a corpus of 12, on 1 abort in 37 members (the block 2 and 3
record). At that rate all 12 succeed with chance (36/37)¹² ≈ 0.72, so a rule that needed all 12 would have
lost about 28% of windows to the corpus alone, and the rule "10 of 12" about 0.4%. The two ALPHA chains that
ran under the first seal showed a different rate for the corpus, which is the first collection stage of the
window and runs in its first hour:"
then the table of section 1.1 of this erratum, unchanged (three rows: NEG-8 corpus, science stages,
registered planning figure), then:
"If each member is lost independently with probability p, the chance that at most k of n are lost is the sum
over j = 0..k of C(n, j) × p^j × (1 − p)^(n−j). A corpus of 12 keeps 10 when at most 2 are lost, a corpus of
18 when at most 8 are lost:"
then the five-row table of section 2.3 of this erratum, unchanged, then:
"These figures are a guide, not a guarantee, because losses are not independent: one sustained burst of
outside load takes consecutive members (a member's two admission attempts span about 170 s, so a five-minute
burst takes about two). In those terms a 12-member corpus survives one burst and an 18-member corpus about
four (§14 Q16)."

**R17. Lines 2770 to 2772 (item 2), line 2775 (item 3) and an insertion after line 2846: every window takes
route 2.**
(a) Lines 2770 to 2772: "That reader authenticates a bound only
against the committed 12-member manifest. It therefore treats a 10- or 11-member bound as absent, and the stored" →
"That reader authenticates a bound only against the historical 12-member manifest,
`configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json`. The block-5 corpus
(`configs/campaigns/neg8_reference_corpus_v5/`) has 18 members under its own id since the erratum of
2026-10-09, so its manifest's bytes differ from that file's. The reader therefore treats every block-5 bound
as absent, whether the window lost a member or not, and the stored"
(b) Line 2775, insert after "*Route 1:* the core reader accepts the bound.":
"(Route 1 cannot occur in block 5 since the erratum of 2026-10-09: item 2. Route 2 judges every window.)"
(c) Line 2814, case (c) of the re-screen: "(c) a
corpus member was dropped for physics and the bound re-derived (below)." → "(c) the harvest built the clean
bound (below), which since the erratum of 2026-10-09 it does on every window whose bound was derived."
(d) Line 2819: "(the physics-clean bound if there is one, else the" → "(the clean bound if there is one,
else the"
(e) Insert after line 2846, as a new paragraph:
"**Since the erratum of 2026-10-09 every block-5 window is judged this way** (§14 Q16), also a window that
lost no corpus member: its stored verdict reads "failed", it carries `whole_window.not_passed` (disclosed
only), and the harvest's re-screen against the clean bound decides its screen. Three things follow, and each
was the registered behaviour for a 10- or 11-member bound before. First, on the collected-subset route the
stored bracket must carry no NEG-8 condition other than the two bound-underived ones for the re-screen to be
evaluated, or the harvest's always-on clean bound must handle it: the harvest program pinned for these
windows (§11 item 4) is tested on a stored bracket that carries another NEG-8 condition, and such a window
must still fail or be re-derived correctly. Second, the allowance consumer checks a clean bound's arithmetic
and digest against the harvest's record, not its corpus identity, which is the sealed behaviour now applied
to every window. Third, lane L9-NEG8 part (c) (analysis plan §11) is a condition of every contrast, as it
already was of every floor."

**R18. Lines 2848 and 2849, and line 2878, the closed list.**
(a) "*Forcing problem:* the bound may rest on
10 or 11 members, so something must decide" → "*Forcing problem:* the in-window bound may rest on fewer
members than ran (10 to 17 of the 18), so something must decide"
(b) Line 2878: "it is omitted, the bound uses the other 11, and the harvest records" → "it is omitted, the
in-window bound uses the other 17, and the harvest records"

**R19. Lines 2887 to 2897, the physics drop's mechanism.**
(a) Line 2887: "(`harvest.neg8_corpus_physics`, after the monitor joins):" →
"(`harvest.neg8_corpus_physics`, after the monitor joins; since the erratum of 2026-10-09 the step builds
the clean bound on every window, whether or not a code fired):"
(b) Lines 2892 to 2894: "writes the bound's own
manifest less those members to `derived/neg8-clean-corpus.json`, builds the bound from the clean members' recorded
points with the core's own builder," → "writes the bound's own manifest less those members and less the
members beyond the desk cap (next paragraph) to `derived/neg8-clean-corpus.json`, builds the bound from the
kept members' recorded points with the core's own builder,"

**R20. Lines 2908 to 2911, the physics worked example.**
"*Worked example (synthetic):* of 12 succeeded corpus members, member 3's request overlapped a
process at 0.09 CPU-s/s (`contention.request_overlap`): the bound is re-derived from the other 11 with t(0.975, 10),
and the screen is re-run against it. Had a second member also been flagged, the bound would rest on 10; had a third,
on 9, and the window would carry `neg8.bound_not_derived`." →
"*Worked example (synthetic):* all 18 corpus members succeeded, and member 3's request overlapped a process
at 0.09 CPU-s/s (`contention.request_overlap`): member 3 is omitted, 17 remain, and the clean bound is built
from the first 12 of them in committed order (members 1, 2 and 4 to 13) with t(0.975, 11); the screen is
re-run against it. Had eight members been lost in all, to status, the mint's reasons and physics together,
the clean bound would rest on the 10 that remain, with t(0.975, 9); had nine been lost, 9 would remain and
the window would carry `neg8.bound_not_derived`."

**R21. Insert after line 2911, as new paragraphs: the desk cap.** This is the new 5.3 text for the desk
rule. The numbered steps (i) to (vi) and the two passages that begin at a † are the cold ruling's words.
The † marks are for the writer and are not copied into the registration; the outer quotation marks are
not copied either.

"**A fifth source of omission, and the only one by position: the desk cap** (erratum of 2026-10-09, §14 Q16;
cold ruling `docs/process_traces/2026-10-block5/corpus18-erratum/RULING.md`, section B). *Forcing problem:*
the corpus has 18 members so that a window can lose eight of them and still have 10. But the bound's first
term, the envelope (§0.12), is the mean of the three largest corpus energies minus the mean of the three
smallest, and the extremes of a sample lie further out the larger the sample is. So a bound computed from all
18 would be larger than the bound this registration sealed with a 12-member corpus, the screen would be
easier to pass, and by how much would depend on how many members each window happened to lose. For members
drawn independently from one normal distribution with standard deviation σ (the cold judge's simulation,
100,000 corpora for each size; a "true shift" is a change of the instrument's reading between the start and
the end triplet):

| n kept | mean envelope | mean repeatability term | mean bound | a window with no drift fails the screen | a true shift of 2 σ fails | a true shift of 3 σ fails |
|---|---|---|---|---|---|---|
| 10 | 2.13 σ | 1.80 σ | 2.13 σ | 2.5% | 45% | 81% |
| 12 | 2.36 σ | 1.76 σ | 2.36 σ | 1.4% | 36% | 75% |
| 15 | 2.62 σ | 1.72 σ | 2.62 σ | 0.6% | 26% | 66% |
| 18 | 2.83 σ | 1.70 σ | 2.83 σ | 0.3% | 20% | 58% |

A drift inside the corpus itself widens the envelope further, and faster for a longer corpus: with a linear
drift of 0.1 σ per member the mean bound is 2.51 σ at 12 and 3.20 σ at 18. The allowance would compensate
for validity, not for sharpness or comparability: with a bound from all 18 every claim would carry a floor
about 20% higher, GAMMA's direction decision would be harder to reach, and the screen's level would differ
between windows with different losses. The six extra members exist to absorb losses, not to change the
bound.

*Mechanism.* At the desk the harvest always builds the deciding bound, the **clean bound**, in
`neg8_corpus_physics` after the monitor join, whether or not a physics code fired: (i) take the members of
the validated in-window bound; (ii) order them by their position in the committed `order_manifest.json` (not
by the artifact's own order); (iii) remove every member on which one of the six physics codes fired
(`NEG8_PHYSICS_LOSS_CODES`); (iv) of the remainder keep the first 12 in that order, or all of them if fewer
than 12 remain; (v) if fewer than 10 remain, `neg8.bound_not_derived` with `observed.source`
`corpus_physics`, as now; (vi) build the clean bound from the kept members' recorded points with the core
builder, validate it against the clean manifest bytes (the bound's manifest less the removed and the capped
members), write `derived/neg8-clean-corpus.json`, `withheld/neg8-clean-bound.json` and
`derived/neg8-corpus-physics.json` as now, with one new key in the last, `beyond_cap`, listing the bundle ids
left out by step (iv), and `members_kept` the count after (iv). The screen re-runs against the clean bound
and the allowance comes from it (`corpus_physics_clean`), as the sealed path already does for a physics drop.

*What the cap is, and what it is not.* The cap at the first 12 clean members in committed order is the one
accepted omission of the desk step, beside the mint's five reasons and the six physics codes. † Members left
out by step (iv) are not dropped for cause: no `neg8.corpus_member_dropped` flag is emitted for them, no
catalog code is added, and their energies are used by nothing. They are disclosed after the release event
with the window's corpus size (analysis plan §8.1). The chain's collected-manifest test (item 3 above) is
unchanged, because the chain's manifest still lists every succeeded member. n is therefore 10, 11 or 12, as
§0.12 says: 12 whenever at most six of the 18 are lost to status, the mint's reasons and physics together,
11 at seven lost, 10 at eight, and no bound at nine or more.

*What decides membership.* † Membership is decided by status, by the mint's five validity reasons, one of
which (`precheck_ineligible`) can turn on the ratio of a member's timing envelope to its own energy
(`reduce.py` `anchor_energy_envelope_exceeds_quarter_metric`), and by the six physics codes, and at the desk
by committed position (the cap). No step reads the size of an energy for any other purpose. The cap is
applied after the physics drop, so no step chooses which twelve by looking at energies. On a corpus of one
workload under one condition the members' energies differ by well under one percent of each other, so the
ratio that `precheck_ineligible` can turn on moves by the same fraction; the number of members each reason
left out is disclosed for every window (analysis plan §8.1).

*The in-window bound.* The chain's retry, prune and mint are unchanged but for the count: the retry fires
when fewer than 10 succeeded, the prune keeps the succeeded members the mint does not drop, and the mint
derives the in-window bound from all of them (n from 10 to 18). That bound is a diagnostic. No screen or
allowance of block 5 is decided by it, because the core reader authenticates only the historical 12-member
file (item 2) and every window is therefore judged by route 2 and the clean bound.

*Worked example (synthetic, the twelve energies of §0.12's worked example for members 1 to 12, and 99.76,
99.85, 99.95, 100.01, 100.12, 100.27 J for members 13 to 18).* Members 2, 3 and 5 abort at admission and
member 9 overlaps a contender at harvest. Kept after (iii), in committed order: 1, 4, 6, 7, 8, 10, 11, 12,
13, 14, 15, 16, 17, 18. Step (iv) keeps 1, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16 and records 17 and 18
under `beyond_cap`. The clean bound is computed from those twelve energies with t = 2.201: s = 0.2217 J,
U_3 = 100.3033 J, L_3 = 99.7433 J, so bound(3, 3) = max(0.5600, 2.201 × 0.2217 × √(2/3) = 0.3983) = 0.5600 J.
(From all 14 clean members it would have been 0.5767 J.) Had eight members been lost instead of four, the
ten remaining would all be kept and t = 2.262, exactly as the first seal's rule treated ten of twelve."

**R22. Lines 3012 and 3013, the corpus retry's charge.**
"60 s settle + 180 s overhead + 12 × (595 + 45 +
32) s = 8,304 s" → "60 s settle + 180 s overhead + 18 × (595 + 45 + 32) s = 12,336 s"

**R23. Lines 3018 to 3020, the derivation and the prune.**
"a real derivation re-reduces 12 bundles,
about 270–320 s (PLAN2 §1.4 item 6; never measured live). The **corpus prune**, which asks the NEG-8 mint which
corpus members it would drop (§5.3), reads the same 12 bundles and is charged the same." →
"a real derivation re-reduces up to 18 bundles. The estimate for 12 bundles was about 270–320 s (PLAN2 §1.4
item 6; never measured live), which scales to about 405–480 s for 18. The charge stays 320 s: the
difference, at most 160 s, is inside the span's margin of more than 70,000 s over the expected chain, and the
chain's wall budget for the stage is 1,800 s. The **corpus prune**, which asks the NEG-8 mint which corpus
members it would drop (§5.3), reads the same 18 bundles and is charged the same, with the same under-charge.
A real-model rehearsal before the first arm records both wall times, and a measured time above 1,200 s for
either goes to a consult before the arm (§14 Q16)."

**R24. Lines 3026 and 3027, the sizing digest.**
"SHA-256 at H_claim: `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa`. At the int5 heads `fe28e5a0c` and
`9395cecfb` it was" →
"SHA-256 at H_claim: `<SIZING_SHA256>` (`shasum -a 256`, with `scripts/size_b5_window.py --check`
reproducing the file byte for byte, exit 0, at H_claim; the erratum of 2026-10-09 changed the file's members,
spans and plan-tree digests, §14 Q16). At the first seal's H_claim and at the int5 heads `fe28e5a0c` and
`9395cecfb` it was"
The digest that follows on line 3027 stays as the dated earlier value.

**R25. Lines 3056 to 3058, the sizing table's three rows.**
"| ALPHA | 119 / 0 | 98,826 s (27.5 h) | 102,180 s (28.4 h) | 31,584 s (8.8 h) | 19,460 s (5.4 h) |" →
"| ALPHA | 125 / 0 | 106,890 s (29.7 h) | 110,220 s (30.6 h) | 33,003 s (9.2 h) | 20,278 s (5.6 h) |"
"| BETA | 19 / 100 | 101,226 s (28.1 h) | 104,580 s (29.05 h) | 32,634 s (9.1 h) | 20,510 s (5.7 h) |" →
"| BETA | 25 / 100 | 109,290 s (30.4 h) | 112,620 s (31.3 h) | 34,053 s (9.5 h) | 21,328 s (5.9 h) |"
"| GAMMA | 61 / 40 | 87,690 s (24.4 h) | 91,020 s (25.3 h) | 27,747 s (7.7 h) | 17,426 s (4.8 h) |" →
"| GAMMA | 67 / 40 | 95,754 s (26.6 h) | 99,060 s (27.5 h) | 29,166 s (8.1 h) | 18,244 s (5.1 h) |"

**R26. Lines 3068 to 3072, the worked decomposition for ALPHA.**
"119 members × 595 s = 70,805 s, of which
35,700 s is every member's cooldown at its 300 s cap and 32,725 s is every member's two admission attempts.
Per-member custody adds 119 × 77 = 9,163 s; the corpus retry 8,304 s; the spare retries 5,424 s; settles,
calibration, derivation, prune, the window calibration verdict, stage custody and shutdown the other 5,130 s; span
98,826 s." →
"125 members × 595 s = 74,375 s, of which 37,500 s is every member's cooldown at its 300 s cap and 34,375 s
is every member's two admission attempts. Per-member custody adds 125 × 77 = 9,625 s; the corpus retry
12,336 s; the spare retries 5,424 s; settles, calibration, derivation, prune, the window calibration verdict,
stage custody and shutdown the other 5,130 s; span 106,890 s."
(The cooldown and admission figures are 125 × 300 and 125 × 275; the draft's list did not have them.)

**R27. Lines 3094 to 3096, the expected chain on the block-3 basis.**
"- ALPHA: 1,830 + 10 × 161 + 119 × 236.5 = 31,584 s ≈ 8.8 h." → "- ALPHA: 1,830 + 10 × 161 + 125 × 236.5 =
33,003 s ≈ 9.2 h."
"- BETA: 1,830 + 1,610 + 19 × 236.5 + 100 × 247.0 = 32,634 s ≈ 9.1 h." → "- BETA: 1,830 + 1,610 + 25 × 236.5
+ 100 × 247.0 = 34,053 s ≈ 9.5 h."
"- GAMMA: 1,830 + 1,610 + 61 × 236.5 + 40 × 247.0 = 27,747 s ≈ 7.7 h." → "- GAMMA: 1,830 + 1,610 + 67 ×
236.5 + 40 × 247.0 = 29,166 s ≈ 8.1 h."
(Each new line is one line in the file. The cold ruling names line 3094; lines 3095 and 3096 carry the same
sum for the other two packs.)

**R28. Lines 3110 to 3112, the expected chain, projected.**
"- ALPHA: 1,830 + 10 × 141 + 119 × 136.3 = 19,460 s ≈ 5.4 h." → "- ALPHA: 1,830 + 10 × 141 + 125 × 136.3 =
20,278 s ≈ 5.6 h."
"- BETA: 1,830 + 1,410 + 19 × 136.3 + 100 × 146.8 = 20,510 s ≈ 5.7 h." → "- BETA: 1,830 + 1,410 + 25 × 136.3
+ 100 × 146.8 = 21,328 s ≈ 5.9 h."
"- GAMMA: 1,830 + 1,410 + 61 × 136.3 + 40 × 146.8 = 17,426 s ≈ 4.8 h." → "- GAMMA: 1,830 + 1,410 + 67 ×
136.3 + 40 × 146.8 = 18,244 s ≈ 5.1 h."
(The cold ruling names line 3110; lines 3111 and 3112 carry the same sum for the other two packs.)

**R29. Lines 3190 and 3191, the yield plan's minimum.**
"10 (the bound's minimum, §5.3; a minimum of 12 would raise a false alarm in about 28% of
windows);" → "10 of the 18 (the bound's minimum, §5.3);"

**R30. Lines 3286 to 3288, the yield worked example.**
"stage rows corpus 12/12" → "stage rows corpus 18/18"; "collected 99 of 119 planned members" → "collected
105 of 125 planned members"

**R31. Line 4498.** "the 101 run ids read through them" → "the 107 run ids read through them"

**R32. Lines 4743 to 4745, the custody worked example.**
"GAMMA plans 101 members (§4.2)" → "GAMMA plans 107 members (§4.2)"; "and the 12 NEG-8 corpus
members" → "and the 18 NEG-8 corpus members"

**R33. Line 4991 (deviation 3), and an insertion after line 5017 (deviations 8 and 9).**
(a) "3. The NEG-8 bound may be derived from 10 or 11 corpus members (§5.3)." → "3. The NEG-8 bound may be
derived from fewer corpus members than the 18 committed: the in-window bound from 10 to 18, the deciding
bound from 10, 11 or 12 (§5.3)."
(b) Insert after line 5017, the last line of deviation 7, as two new list items:
"8. Each pack's `calibration_plan.json` still reads `planned_bound_bundles` 12; the plan tree's stage graph,
   which the chain reads, says 18 (erratum of 2026-10-09, §14 Q16). No program reads the field. It is left
   so that the 280 science configurations and the 12 science order manifests, each of which carries the
   SHA-256 of its pack's calibration plan, keep the bytes they had in the superseded attempts. The plan
   tree's `runtime_budget.bound_count` reads 18, because the plan tree was regenerated in any case; the
   planning estimate printed beside it was computed for 12 members and is stale. No program reads either.
9. The chain script's comments, the plan's `chain_deviations` and the sizing output's two `source` strings
   still say 12, 10 and 11; the stage graph the chain reads says 18, and the desk rule of §5.3 caps the
   deciding corpus at 12."
(Deviation 9's sentence is the cold ruling's, word for word. `joulewise/b5/chain.py` and
`scripts/size_b5_window.py` are byte-identical to the first seal's H_claim.)

**R34. Line 5542, the name `H-CLAIM`.**
"`H-CLAIM` is the commit `a64000884ef5bb4b76415835f02f39803f6eb620`: the last commit of the integration branch
that changes a window input (§9.1, §11). It carries `fe28e5a0c`," →
"`H-CLAIM` is the commit `<NEW_H_CLAIM>`, filled again on `<SEAL_DATE>` at the seal of the erratum of
2026-10-09 (§14 Q16): the last commit that changes a window input (§9.1, §11). Under the first seal it was
`a64000884ef5bb4b76415835f02f39803f6eb620`, the last commit of the integration branch that changed a window
input. The new H_claim contains that commit and so carries `fe28e5a0c`,"

**R35. Line 5690, the register row "sizing, pins, plan trees".** The row's second cell:
"the three `plan_tree.json` and `sizing_b5.json` unchanged; `identity_pins.json` `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` (was `f78a27f8…`); `configs/pins/registry.json` `a4a2be94912c4a3c33b1fb04e0f91e9e691290e2a7b7ee98898783ff307033b2`, unchanged" →
"at H_claim, after the erratum of 2026-10-09 (§14 Q16): the three `plan_tree.json` `<PT_ALPHA_SHA256>`,
`<PT_BETA_SHA256>` and `<PT_GAMMA_SHA256>`; `sizing_b5.json` `<SIZING_SHA256>`; `identity_pins.json`
`<PINS_SHA256>`; `configs/pins/registry.json` `<REGISTRY_SHA256>`. At the first seal's H_claim: the three
`plan_tree.json` and `sizing_b5.json` unchanged from `fe28e5a0c`; `identity_pins.json`
`a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` (was `f78a27f8…`);
`configs/pins/registry.json` `a4a2be94912c4a3c33b1fb04e0f91e9e691290e2a7b7ee98898783ff307033b2`, unchanged"
(The row is one line in the file. Its other cells stay.)

**R36. Line 5753, the register row "GAMMA's planned members".**
"12 corpus members, reference stages of 3, 1 and 3, two diagnostic stages of 1, and four science stages of
20, 101 in all" → "18 corpus members, reference stages of 3, 1 and 3, two diagnostic stages of 1, and four
science stages of 20, 107 in all"

**R37. Line 5773, question Q1.**
"- **Q1. NEG-8 corpus of 10 or 11. Closed in revision 4.** It was settled" →
"- **Q1. A NEG-8 corpus with fewer members than were committed (10 or 11 of 12 when the question was closed;
since the erratum of 2026-10-09, 10 to 17 of 18, Q16). Closed in revision 4.** It was settled"

**R38. Insert after line 5918, the last line of Q15, as a new entry: question Q16.**
"- **Q16. An 18-member NEG-8 corpus, with the deciding bound capped at 12. Closed by the prospective cold
  erratum of 2026-10-09 (§10: one judge, one refuter, settled in one erratum).** The erratum, its refutation
  and the cold ruling that admitted it with corrections are
  `docs/process_traces/2026-10-block5/corpus18-erratum/ERRATUM.md`, `REFUTATION.md` and `RULING.md`. *Forcing
  problem:* the two ALPHA chains that ran under the first seal lost 2 and 3 of their 12 corpus members to
  idle-admission aborts under outside CPU load in the window's first hour, 5 of 24 where the rule had been
  sized on 1 in 37; the corpus retry of §5.1 cannot re-measure an aborted member; and "10 of 12" leaves a
  margin of two members for run-time aborts and harvest drops together. *Ruling:* the corpus has 18 members,
  all of which always run, and the harvest builds the deciding bound from the first 12 clean members in
  committed order (§5.3). Every block-5 window is judged by the harvest's route 2 (§5.3). Deviations 8 and 9
  are registered (§10). The two 320 s sizing charges stay (§5.5). *Supersession:* the corpus manifest and
  the plan trees are collection inputs that both chains executed, so §7.5 applies. The first seal (H_claim
  `a64000884ef5bb4b76415835f02f39803f6eb620`, seal commit `ab7b21e576a2d74f0b25d9a26b463d6934588368`) is
  superseded by the seal whose H_claim is `<NEW_H_CLAIM>`, and the block restarts at ALPHA attempt 1. The
  first seal's three ALPHA attempts are retained, disclosed structurally and never analysed (analysis plan
  §2.1 and §8.1): `v5-b5-alpha-a1-20261008T2201Z` (chain ran; COLLECTED, not claim-usable),
  `v5-b5-alpha-a2-20261009T0515Z` (refused at the arm; no chain) and `v5-b5-alpha-a3-20261009T0644Z` (chain
  ran; COLLECTED, not claim-usable). They do not count when the causes of two attempts of a pack are compared
  for the re-arm rule (§7.3), and all three are printed in the attempt history. *What stays as history in
  this file:* the dry render record of 2026-10-07 in §2 (bound bundles 12/12/12), the dated earlier digests
  in §0, §4.6 and §5.5, the row of §13 that records the hashes "as at `fe28e5a0c`", and the counts of 119 and
  101 run ids in §16 are records of checks made for the first seal and were not rewritten."

**R39. Line 6124, the record of the first seal's checks: insert, change nothing.** Lines 6123 and 6153 keep
"119 run ids" and "101". Insert after the sentence that ends "the same 101 run ids either way.":
"(These counts, and GAMMA's 101 planned members later in this section, are the record of checks made for the
first seal, whose corpus had 12 members; under the erratum of 2026-10-09 the plan trees list 125, 125 and
107 run ids, §14 Q16.)"

#### Lines of the registration that hold a first-seal value and stay

The text gate (section 7, gate 4(c)) will find these when it searches for the old numbers and digests. Each
stays, for the reason given.

| Lines | What stays | Why |
|---|---|---|
| 750 to 752 | the three old plan-tree digests | a dated record of the int5 head `fe28e5a0c`; R4 adds the new values after it |
| 1004 | "n their count (10, 11 or 12; §5.3)" | true of the deciding bound under the rule; the cold ruling, section B item 4, says it stays as sealed |
| 1233 to 1236 | the twelve-member worked example of 0.12 | a corpus of 12 kept members is the normal case under the cap |
| 1772 to 1784 | "12 listed and 12 kept", bound bundles 12/12/12 | the record of the first seal's dry render; R8 adds the new record beside it |
| 2034, 3524 to 3533 | "a precheck can turn on an energy test"; "whether a precheck is eligible can turn on the energy envelope" | these two sentences are right and describe the path that `precheck_ineligible` takes (the cold ruling, A.3); it was the draft's sentences that were corrected |
| 2247, 2262 (parts) | "revision 6 ... 83.5 and 73.9 GiB"; "revision 6 showed 119 × 182 MiB" | dated history, kept inside R10 and R11 |
| 2524, 3027 | the old identity-pins and sizing digests | kept by R12 and R24 as the dated earlier values |
| 3104 to 3106 | "over 119 members" (three times) | the per-member savings were measured over the 119 members of an earlier window plan; the per-member figures 22.9, 41.0 and 56.9 s do not change |
| 3178 | "0 of 119 bundles" | the record of a window of revision 4 |
| 5721 | abbreviated old digests `1d87a309…`, `0cdb3383…`, `8b1d1d71…`, `89e7ea70…`, `a0865895…` | the row records a check "as at `fe28e5a0c`" |
| 6123, 6153 | "119 run ids", "101 run ids", "GAMMA's 101 planned members" | the record of the first seal's checks; R39 adds the sentence saying so (the cold ruling, minor finding 12) |

#### Table P: the analysis plan, in line order

**P1. Line 3, the status line.** (Added by the corrections seat, like R1; the magistrate may strike it. The
edit is inside the line and adds no line break.)
"Status: **Revision 12, 2026-10-07.** This file has its sealed bytes" → "Status: **Revision 12, 2026-10-07,
amended on `<SEAL_DATE>` by the prospective cold erratum of 2026-10-09 (registration §14 Q16).** This file
has its sealed bytes"

**P2. Lines 597 to 599, the reference-drift disclosure.**
"- **Reference drift:** each window's NEG-8 screen result, allowance and corpus size (10, 11 or 12). For a corpus of 10
  or 11, also disclose that the bound was validated against the collected members and that the harvest's re-screen,
  not the stored verdict, decided the screen (registration §5.3; `derived/neg8-bound.json`, `derived/neg8-screen.json`)." →
"- **Reference drift:** each window's NEG-8 screen result, allowance and corpus size (10, 11 or 12: the
  number of corpus members the deciding bound was built from, registration §5.3), printed beside the
  window's allowance, with the number of corpus members that ran (18), the number the in-window bound rested
  on (10 to 18) and the members left out by the desk cap, and, for each window, the number of corpus members
  left out by each reason (status, each mint reason, each physics code, the cap). For every block-5 window,
  also disclose that the bound was validated against the collected members and that the harvest's re-screen
  against the clean bound, not the stored verdict, decided the screen (registration §5.3;
  `derived/neg8-bound.json`, `derived/neg8-screen.json`, `derived/neg8-corpus-physics.json`)."
(The words "and, for each window, the number of corpus members left out by each reason (status, each mint
reason, each physics code, the cap)" are the cold ruling's, correction 3.)

**P3. Line 508, the attempt history: insert, change nothing.** Insert after the fixed sentence that ends
"the kept units of each cell are printed beside it."" and before "*A hazard not read at the arm.*":
"The windows of a block superseded under registration §7.5 are listed in the same history, separately from
the attempts of the block that replaced it, each with its verdict and cause. For block 5 these are the three
ALPHA attempts of the first seal, `v5-b5-alpha-a1-20261008T2201Z`, `v5-b5-alpha-a2-20261009T0515Z` and
`v5-b5-alpha-a3-20261009T0644Z` (registration §14 Q16). They are inputs to no number (§2.1)."

**P4. After line 999, the last line of the file: a new entry in §14.** Insert one empty line and then:
"**Amendment of `<SEAL_DATE>` (the prospective cold erratum of 2026-10-09; registration §14 Q16).** The NEG-8
corpus has 18 members and the harvest builds the deciding bound from at most 12 of them (registration §5.3).

- §8.1, reference drift: the corpus size printed is that of the deciding bound; the disclosure now applies to
  every window, and it adds the members that ran, the members beyond the cap and the count of members left
  out by each reason.
- §8.1, attempt history: the three ALPHA attempts of the superseded first seal are listed separately.
- No line above §6's sentence on R_cm changed its line number: the status line was changed inside the line,
  and the other edits are below that sentence."

### 4.6 Window duration, the sizing file and free disk

The sizer charges each reference-class member 595 s of allowance plus 77 s of custody, 672 s (registration
5.5, lines 3003 to 3011). Six more corpus members add 6 × 672 = 4,032 s to the corpus stage and another 4,032 s
to the one corpus retry that the span always charges: **+8,064 s per pack**. `WINDOW_MAX_S` = 60 × ceil((span +
3,300) / 60).

| Pack | Members, small-class / 8B (old → new) | Programmed span (old → new) | `WINDOW_MAX_S` (old → new) | Expected chain, block-3 basis | Expected chain, projected |
|---|---|---|---|---|---|
| ALPHA | 119 / 0 → 125 / 0 | 98,826 → 106,890 s (29.7 h) | 102,180 → 110,220 s (30.6 h) | 31,584 → 33,003 s (9.2 h) | 19,460 → 20,278 s (5.6 h) |
| BETA | 19 / 100 → 25 / 100 | 101,226 → 109,290 s (30.4 h) | 104,580 → 112,620 s (31.3 h) | 32,634 → 34,053 s (9.5 h) | 20,510 → 21,328 s (5.9 h) |
| GAMMA | 61 / 40 → 67 / 40 | 87,690 → 95,754 s (26.6 h) | 91,020 → 99,060 s (27.5 h) | 27,747 → 29,166 s (8.1 h) | 17,426 → 18,244 s (5.1 h) |

Arithmetic for ALPHA: 98,826 + 8,064 = 106,890; (106,890 + 3,300) / 60 = 1,836.5, rounded up to 1,837;
1,837 × 60 = 110,220. The expected chain grows by 6 × 236.5 = 1,419 s on the block-3 basis and by 6 × 136.3 =
818 s on the projected basis (the per-member figures of registration 5.5), so **a normal window is 14 to 24
minutes longer**, plus up to about 5 minutes for the prune and the derivation reading 18 bundles instead of 12
(F4). These are this seat's computations from the registered rule; the sizer's output is the authority, and
the builder checks that it prints these spans. If it does not, the difference is a finding.

The corpus stage's launch allowance under the collection deadline becomes 60 + 180 + 18 × 620 = 11,400 s
(`chain.py` 1132; it was 7,680 s). The corpus is the first collection stage, so this never refuses it.

Free disk at the arm: planned bytes are 182 MiB × (members + 7 spares) (`plan.py` 767 to 777). ALPHA and
BETA: 132 × 182 MiB = 23.46 GiB, three copies on the runs volume plus 20 GiB of headroom = **90.4 GiB**
(was 87.2). GAMMA: 114 × 182 MiB = 20.26 GiB, **80.8 GiB** (was 77.6). The volume had 216 GiB free when this
was written (`df -g`). The arm measures it again each time.

### 4.7 Tests that fix the old numbers

These lines assert 12, or a number derived from it, against the committed packs. Tests are not window inputs.
The list is what the search of section 4.1 found; the whole suite on the merged tree is the authority.

| File | Lines | What it asserts |
|---|---|---|
| `tests/test_b5_chain.py` | 34, 234, 239, 284 | 119 and 101 members; corpus listed 12, kept 11 or 12 |
| `tests/test_b5_chain_prune2.py` | 322, 334, 436, 657, 798, 845 | 119; run ids r01 to r12; derivation over 12 |
| `tests/test_b5_driver.py` | 803, 811, 831 | corpus (12, 12) and (12, 11) |
| `tests/test_b5_driver_p2.py` | 521, 529, 537, 596, 661, 671 | ("corpus", 12, 10); "of 119 planned members" |
| `tests/test_b5_plan.py` | 54 | 119, 119, 101 |
| `tests/test_size_b5_window.py` | 61, 82, 95 to 110 | 12 corpus members in the retry; spans 98826, 101226, 87690; deadlines; `corpus_retry_s` 8304 |
| `tests/test_harvest_b5_window.py` | 530, 1575 to 1599, 1988, 3162, 5040 | the 12-member committed corpus; 126 bundles |
| `tests/test_hazard_neg8_mint_verdicts.py` | 46, 66 | fixtures of 12 corpus bundles (a fixture of 12 may stay: 12 kept of 18 is a legal corpus) |
| `tests/test_hazard_whole_window_verdict.py` | 114, 287, 312, 478, 561 | the same kind of fixture |
| `tests/test_run_campaign.py` | 9331 | run ids r01 to r12 |
| `tests/test_v5_pack_regen.py`, `tests/test_d117_floor_qwen3_v5_generate.py`, `tests/test_d117_contrast_v5_pack.py` | whole files | regenerate the packs and compare bytes; they pass once the generators and the files agree |
| `tests/fixtures/b5_plan/fake_window.py` | 41, 61 | reads the corpus directory; a fixed `planned_bytes` |

The table above is the **window side**: these tests are edited on the build branch, so that the whole suite
passes on the merged tree that becomes the new H_claim. Main holds the first seal's `harvest.py`, so on main
`tests/test_harvest_b5_window.py` gets only the changes of fixed numbers that the 18-member corpus forces.
The harvest lane's copy of that file is 644 lines longer (refutation, finding 6); when the lane merges the
new seal commit the two copies will conflict, and the lane's copy, with the same numbers changed, is the one
that tests the program which judges the windows.

**Tests to add on the window side** (at the new H_claim):

- (i) a chain render of each pack shows the corpus stage with 18 members and `--max-failures 18`;
- (ii) the sizer prints the members, spans and deadlines of section 4.6.

**Tests to add on the harvest lane** (after it has merged the new seal commit; the cold ruling's section D,
its tests (a) to (d)). A defect these tests miss is a desk defect: it is fixed and the harvest is run again
on the same bytes.

- (a) the harvest accepts a collected manifest of 18, of 10, and of 13 with a gap, and refuses 9 and refuses
  a succeeded member left out;
- (b) the core reader returns nothing for an 18-member bound and the harvest takes route 2;
- (c) the clean bound under the rule of section 2.1: 18 kept → 12 used and 6 under `beyond_cap`; 14 kept
  with two physics drops → 12 used; 11 kept → 11 used; 9 kept → `neg8.bound_not_derived`; a stored bracket
  carrying a NEG-8 condition other than the two "underived" ones still fails or re-derives correctly with
  the always-on clean bound; the allowance consumer authenticates the clean bound and refuses a tampered
  clean manifest;
- (d) the bound builder at n = 12 uses t = 2.201 and at n = 10 uses 2.262.

The draft's test "the bound builder at n = 18 uses t = 2.110" is dropped: no deciding bound rests on 18
members.

## 5. Supersession, and the three ALPHA attempts

The corpus stage's inputs are files that completed windows read: both chains that ran executed the corpus
stage from the 12-member manifest. Registration section 7.5 (line 4628) therefore applies: a cure that
touches collection inputs a completed window executed **supersedes the whole block**. Completed windows are
kept and disclosed structurally, their energies are never analysed, a cold erratum is written (this file),
and the block restarts at ALPHA. Section 10 (line 4971) requires a prospective cold erratum for a roster
change, with one judge and one refuter, settled in one erratum.

What happens to each attempt:

| Attempt | Plan id | What it was | Under the new seal |
|---|---|---|---|
| ALPHA 1 | `v5-b5-alpha-a1-20261008T2201Z` | chain ran; harvest COLLECTED, not claim-usable (`cell.below_minimum`, `neg8.bound_not_derived`) | kept, disclosed, never analysed |
| ALPHA 2 | `v5-b5-alpha-a2-20261009T0515Z` | refused at the arm (contention dwell); no chain | kept, disclosed |
| ALPHA 3 | `v5-b5-alpha-a3-20261009T0644Z` | chain ran; harvest COLLECTED, not claim-usable (`neg8.bound_not_derived`, `neg8.screen_failed`) | kept, disclosed, never analysed |

None of the three was claim-usable, so the supersession discards no analysable window. Their custody roots,
runs roots and harvest archives stay where they are and stay restricted until the release event. The old
measurement clone is not edited or deleted (magistrate brief section 9): a re-harvest of an old attempt reads
that clone and the sealed inventory in force when the attempt was armed (registration 7.5, lines 4624 to
4627). No window is armed from the old clone again.

The new block starts at **ALPHA attempt 1 under the new seal** (J10, section 8). Attempt numbers restart;
plan ids must not collide with the three above, and they do not, because each carries its own time stamp. No
block marker is added to plan ids unless a search shows that no program parses the id.
The paper's attempt history lists the three superseded attempts separately, with their verdicts and causes,
beside the new block's attempts (analysis plan sections 2.1 and 8; section 4.5, edit P3). Every reported
number stays conditional on its window having passed the quiet, timing and drift tests (registration 7.6),
and the reader sees every attempt that was made, the superseded ones included.

**The superseded attempts and the re-arm rule.** Rule 1 of the magistrate brief compares the **cause keys**
of two attempts of a pack (a cause key names why an attempt failed: the hazard modules that refused, or the
families of the codes that removed the window; registration 7.3). The three superseded attempts do not count
toward that rule: the new block's ALPHA
attempt 1 is compared with no earlier attempt. All three are printed in the attempt history (the cold
ruling, minor finding 19).

## 6. The open defect to explain in the same lane

**What was seen.** In both chains the stage `alpha-science-prefill-p2048-abba-06-10` returned code 1 while all
20 of its members succeeded. The driver's terminal record (an open file) adds one fact that the ruling did not
have. Its per-stage row for that stage reads, in both attempts: planned 20, present 20, succeeded 20,
**logged 20, failed 1**. "Succeeded" is the driver's own count of bundle summaries with status `succeeded`.
"Failed" is its count of rows in the runner's campaign log whose status is `failed` (`driver.py` 1752 to
1757). So in both chains the runner logged one member of that stage as failed although that member's bundle
says it succeeded. The window totals agree: attempt 3 has 115 succeeded and 5 logged failed out of 119, one
more than fits. Twice in two chains, in the same stage, with one member: this looks deterministic.

**The code path.** After a member's child process returns, the runner sets the member's log status
(`scripts/run_campaign.py` lines 11226 to 11236): `ok` only if the child's exit code is 0, and none of the
member's evaluations is failed, and no bundle is missing; otherwise `failed`. A `failed` status adds one to
the stage's failure count (line 11262), and a nonzero failure count makes the stage return 1 (lines 11398 to
11404 on the block-5 path). So one of three things happened to one member:

1. its child process exited nonzero after it had written a succeeded summary (something after the reduction,
   such as cleanup or the sampler's wind-down);
2. the runner's own check of the finished bundle called it not usable (`evaluation.failed`, line 500: not
   usable and not waived). In block 5 that check is structural: files present and hashed, the configuration
   binding, the prompt hash, the custody identity (registration 5.2; `run_campaign.py` 2876 to 2934);
3. the bundle directory did not exist when the runner looked (`missing_after_run`, lines 11220 to 11225),
   which would also make the stage's provisional verdict `blocked` (lines 6363 to 6387).

The ruling's Q3 item 4 named the stage-level conditions (`counts["drained"]`, a `blocked` or `invalid`
verdict, the verdict row's append failing). The "failed 1" count narrows it to the member level: a drain or a
failed append would not write a `failed` member row. An `invalid` verdict is the stage-level echo of case 2.
The ruling excluded an earlier stage's bundle being re-evaluated; that stands.

It removed nothing from either window: the harvest validates every bundle itself and kept every unit. It is
still worth one explanation, because a runner that calls a good member failed is a wrong record, and if the
cause is case 1 a child process is ending badly once per window.

**How to reproduce it.** The real-model rehearsal rig (`scripts/rehearse_b5_real.py`) runs the block-5 path
on real hardware under ids prefixed `REH-`; it is a rehearsal, not a claim window, so its stage logs may be
read. Its archive `/Users/edr/night-archive/gate-prune/rehearsal-real/alpha-1/` does **not** show the defect:
there the stage returned 0 (read by this seat from that archive's `custody/night/hazard_result.json`, stage
ids and return codes only). The rig keeps one member per stage unless told otherwise (line 97, `KEEP_DEFAULT`),
so that rehearsal ran 1 of the stage's 20 members. The reproduction is bounded to one run: the rehearsal of
section 7, gate 7, which is required in any case, with this stage kept whole. The builder therefore:

1. runs the rig for ALPHA once, with this stage kept whole and with the corpus and the references that gate
   7 requires:
   `scripts/rehearse_b5_real.py all --pack <alpha> --base <new directory under rehearsal-real/>
   --keep '{"06_phase_prefill_p2048_abba_blocks_06_10": 20, "neg8_reference_corpus_v5": 18, ...}'` (the pack
   name as the rig's `--pack` choices spell it; "..." stands for the keys that keep the full start triplet,
   the midpoint and the full end triplet; a `--keep` key is the basename of a stage's configuration
   directory and a stage with no key keeps 1 member, `scripts/rehearse_b5_real.py` lines 96 to 101, so the
   builder reads the three reference stages' directory names from ALPHA's plan tree and gives the two
   triplets 3 each), with no agent session doing other heavy work;
2. reads `custody/operator-logs/12-alpha-science-prefill-p2048-abba-06-10.log` of that rehearsal. The runner
   prints one line per member, `<status> <run id>: exit=<code> ...` (line 11340), then `Summary:` with a count
   per status, then `COLLECTION VERDICT (provisional):` with the verdict, each reason and the four category
   counts (lines 11361 to 11377). The member line with status `failed` names the member and gives its exit
   code: nonzero means case 1; zero with the member under `failed` in the verdict means case 2; a
   `missing member bundle(s)` reason means case 3;
3. states the cause as far as that one run shows it. (The draft's step 3, two more full stages if 20 members
   reproduced nothing, is struck by the cold ruling: the search has no further round.)
4. applies this bound, which is the cold ruling's (A.10): the runner is changed in this seal only if the
   cause is shown to alter a byte or a status that the harvest reads; otherwise the wrong log row is recorded
   as a known wrong record with its explanation, and the arm does not wait. The runner is collection code
   that both completed chains executed, the defect removed nothing from either window, and a fix of unknown
   size must not ride into a seal on the strength of a wrong label.

**A second, smaller defect seen in the same record.** The driver's `ok` count is 0 for every stage of both
attempts, including stages with 20 of 20 succeeded and return code 0. The driver counts log rows whose status
equals `succeeded` (`driver.py` 1754), but the runner's word for a good member is `ok` (`run_campaign.py`
214 to 225 and 11228 to 11232). The count is a label in a record; nothing reads it for a decision. Under the
doctrine that a finding about representation is a flag and not a fix round, this is recorded here. Ruled
(J7, section 8): `driver.py` line 1754 is left alone and the label mismatch is recorded as a flag; it touches
no number. The cold judge verified this reading: the driver counts log rows with status `succeeded`, the
runner's word is `ok`, and the "failed 1" row therefore comes from `run_campaign.py` lines 11233, 11234 (a
nonzero exit, a failed evaluation or a missing bundle).

## 7. Gates

**Before the build: this erratum, ruled cold. Done.** One Fable 5.1 judge and one Opus 5.5 refuter
(registration section 10, line 4971; magistrate brief section 9) ruled on the rule of section 2, the bound's
behaviour as n grows (section 2.5), the files (section 4.3), the cause statement (section 1.4, which stands
as written) and the questions of section 8. The cold ruling settled the science and returned nothing for
redrafting. The builder builds from this corrected text without another judge.

**What the build is built on.** A branch from main at `3f564499e`, which contains the first seal's H_claim
`a64000884` and its seal commit `ab7b21e57`. The branch's merge into main is the new H_claim. The new
H_claim's only child is the new seal commit.

**Gates before the first arm, in order.** These are the cold ruling's section D, gates 1 to 8. Each gate
names what is run and what must be seen.

1. **Generation and checks, each exit code recorded** (section 4.4, steps 1 to 6): the six member files and
   the two manifests; the generator literals; each pack's `generate_configs.py` and then the same with
   `--check` (the contrast generator with `--no-preserve-current-frozen-bytes`);
   `python3.13 -m joulewise.b5.reference_spares --check`; the sizer and then `--check`; the identity pins
   rewritten with the registration's recorded arguments and then `--check`;
   `scripts/digest_pin_census.py --write`; the per-pack `git diff --stat` of section 4.3, table C, which must
   show the generator, `plan_tree.json`, `plan_tree.sha256` and at most the pack's `README.md`.
2. **Dry render of each pack's chain.** The corpus stage shows `expected_count` 18 and `--max-failures 18`
   (`chain.py` lines 509 to 516). The rendered comments still say 12, and that is expected (deviation 9).
   The result is recorded as the new dry-render record beside the one of 2026-10-07; its path and digest
   fill `<DRY_RENDER_RECORD_PATH>` and `<DRY_RENDER_RECORD_SHA256>` (section 4.5, edit R8).
3. **The merge gates for code and inputs that a window reads** (magistrate brief section 9): an independent
   executing review by a non-author; the whole test suite on the merged tree; continuous integration green
   on the final head; a cold Fable 5.1 pass, because the change touches measurement; every finding
   dispositioned (fixed, deferred to a named lane, or rejected with a reason); the Impact statement (the
   pull request's paragraph saying which numbers the change can move); and the re-audit that directive #416
   requires after a change to frozen code (a blind audit of the system before arming; registration 7.5, line
   4621), scoped here to the diff. The review and the re-audit have the same object, generated plan trees
   and generator source, so one brief serves both. Then the merge. The merge commit is the new H_claim.
4. **The seal.**
   (a) The inventory, generated from a clean checkout of the new H_claim with `make_sealed_inventory.py`
   (section 4.4, step 8).
   (b) The three-file seal commit: the inventory and the two documents edited by section 4.5, one parent.
   `python3.13 -m unittest tests.test_b5_seal_landing` passes.
   (c) **The text gate.** *Forcing problem:* section 4.5 lists 39 numbered hand edits to a 6,173-line
   registration, several of them in parts, and four to the analysis plan, and what binds the windows is the edited registration, not
   this erratum; the gates above check code and inputs, and none of them reads the text. *The gate:* one
   reader, one pass, over the seal commit's diff of the two documents, edit by edit against the cold
   ruling's corrections and against section 4.5 of this erratum. The reader is the cold Fable pass of gate
   3; no new seat is needed. The reader also searches both documents for every remaining `12`, `119`, `101`,
   `126`, `108`, `24,045,944,832`, `98,826`, `101,226`, `87,690` and the old digests `0ec9d68a…`,
   `74ccdaec…`, `1d87a309…`, `0cdb3383…`, `8b1d1d71…`, `a0865895…`, `89e7ea70…` (the cold ruling's list, A.7).
   Every hit is either changed by an edit of section 4.5 or is in that section's table "Lines of the
   registration that hold a first-seal value and stay"; any other hit is a finding. The corrections seat
   adds three searches that follow from section 4.5: the number without commas, `24045944832` (edit R11);
   the old H_claim `a64000884`, which may remain only where an edit calls it the first seal's; and `<`
   followed by a capital letter, which must find nothing (an unfilled placeholder).
   (d) The seal record gains a section that pins the new digests: the three seal documents, the three plan
   trees, `sizing_b5.json`, `identity_pins.json`.
5. **The harvest lane.** *Forcing problem:* the new H_claim keeps the first seal's `harvest.py` (J6), and the
   harvest pin `7e6158d66` is not an ancestor of main: main and the pin differ by 535 lines of `harvest.py`,
   80 lines of `whole_window.py` and 7 lines of `scripts/harvest_b5_window.py`. Harvest tests run on main
   would test a harvest that never judges a block-5 window. *The gate:* the harvest lane merges the new seal
   commit; the desk rule of section 2.1 is implemented in `neg8_corpus_physics` with tests (a) to (d) of
   section 4.7; the whole suite passes on that tree; a cold Fable pass reads the change, because desk code
   that decides the screen is number-integrity code; the `B5-HARVEST-PIN` addendum is written and pushed;
   the desk root is moved to that commit. **The pin addendum is written before the first arm**, not merely
   before the first harvest, so that the rehearsal of gate 7 is harvested by the pinned program.
6. **The new measurement clone**, at the new seal commit, by the hand-off runbook's steps 3 to 6, with the
   calibration ledger and its pin carried over. One consult seat checks the carry-over commands before they
   run; they have not been rehearsed (brief section 9, step 3). A new fixed-values file names the new
   `MEASUREMENT_ROOT`, `H_CLAIM` and `SEAL_HEAD`. In the clone: `tests.test_b5_seal_landing` passes; every
   digest in the inventory is recomputed from the working tree (not from git objects) and compared; the
   interpreter gives the pinned `runtime_versions_sha256`. Then the desk seal check with the new H_claim.
7. **The rehearsal** (J9, required). *Forcing problem:* the path that will judge every window has never run
   to a pass on real bundles. Both archived real-model rehearsals kept one corpus member (`KEEP_DEFAULT`,
   `scripts/rehearse_b5_real.py` lines 97 to 101), and in both the derivation stage returned 2; so the
   prune, the mint and route 2 have never run on ten or more real bundles, the re-screen has never been
   evaluated on real data, and the two 320 s charges of F4 rest on an estimate never measured live. *The
   gate:* one real-model rehearsal under `REH-` ids (a rehearsal, not a claim window) with all 18 corpus
   members, the full start triplet, the midpoint and the full end triplet, and the stage
   `alpha-science-prefill-p2048-abba-06-10` of section 6 kept whole (the command is in section 6, step 1).
   It is run from the new clone only if the clone's working tree is clean afterwards (`git status
   --porcelain` prints nothing); otherwise from a desk checkout at the seal commit. It is harvested by the
   pinned harvest program. Its record must show: the re-screen evaluated; the clean bound built from 12
   members with 6 under `beyond_cap`; the wall times of the prune and of the derivation. A wall time above
   1,200 s for either goes to a consult before the arm. For section 6: the runner's log line is read, the
   cause is stated, and the bound of section 6, step 4, applies.
8. **Pre-arm**, from the records note:
   - the two `/private/tmp` numbers of procedure (a) below;
   - the 60-minute settle of procedure (b) below, after any daemon restart, Wi-Fi toggle or owner login;
   - if the owner restarted the Mac: `launchctl print-disabled gui/501` lists `com.apple.mediaanalysisd`,
     `com.apple.photoanalysisd` and `com.apple.corespotlightd` as disabled; `pgrep -x` for each of the three
     prints nothing, twice, ten minutes apart; `sysctl -n kern.boottime` has changed; the watchdog is loaded
     again (the consult ruling's Q2 (ii)); and `sw_vers -buildVersion` is unchanged, because registration 7.5
     requires one macOS build for all three windows;
   - no agent session alive.

   Then ALPHA attempt 1.

**The cheapest desk checks that must pass before a window is spent** (the cold ruling, section D): the
`--check` exit codes of gate 1 (minutes, no load); the dry-render search of gate 2; the seal landing test and
the recomputed inventory digests of gate 6; the synthetic harvest tests (c) of section 4.7; and the
rehearsal harvest of gate 7, which is the only check that exercises the 18-member path through the corpus
prune, the mint, route 2 and the clean bound on real bundles.

**One desk check before GAMMA: the dead-man job's firing time.** The **dead-man** is the scheduled job that
stops a window which overran. Its schedule keeps only the hour and the minute of t0 + `WINDOW_MAX_S` +
3,900 s (`scripts/run_night.py` lines 2105 to 2111 and 2206, 2207), so it fires every day at that clock
time, and a firing that comes before the deadline stands down (lines 4500 to 4506). The first firing after
t0 is therefore (`WINDOW_MAX_S` + 3,900) less 86,400 s. Worked for GAMMA: 99,060 + 3,900 = 102,960;
102,960 − 86,400 = **16,560 s** after t0 (under the first seal: 91,020 + 3,900 − 86,400 = 8,520 s). For
ALPHA it moves from 19,680 s to 27,720 s and for BETA from 22,080 s to 30,120 s, both after the projected
end of the chain (20,278 s and 21,328 s, section 4.6). For GAMMA it stays inside the projected chain
(18,244 s) and moves toward its end. The concern is a scheduled job firing while a reference member is
being measured. Before GAMMA
is armed, the magistrate compares 16,560 s with the rendered stage order and confirms that it does not fall
in the end triplet; if it does, t0 is shifted by a few minutes (the cold ruling, minor finding 15: required
as written).

**Two procedure items, in force now.** They are not registered rules and need no erratum, because they change
no file a window reads, no threshold, no catalog effect, no roster and no blinding rule.

- *(a) `/private/tmp` is small before every arm.* Reason: the operating system runs a cleaner at 00:00 local
  time every day that walks `/tmp` with two `find` passes. Their length is the size of the tree. In attempt 3
  the tree held about 149 GiB of agent-session scratch, the walk took about five minutes, and it fell inside
  the corpus stage (31 consecutive dirty intervals). **The check, in two exact numbers:** fewer than 1,000
  entries under `/private/tmp` (`find /private/tmp -mindepth 1 | wc -l`) and under 1 GiB
  (`du -sk /private/tmp` prints less than 1,048,576). Why these numbers: the cleaner's cost is one file
  lookup (a `stat` call) per entry per pass, and a thousand lookups take far less than one 10 s monitor
  interval. **The arm rule: until both numbers hold, no window is armed whose span contains 00:00 local
  time.** That rule is in force now. The magistrate's attempt to move the scratch was refused by its
  permission check; a restart of the Mac empties the directory.
- *(b) A settling wait of 60 minutes, display asleep (`pmset displaysleepnow`), between any daemon restart,
  Wi-Fi toggle or owner login and the arm.* Reason: attempt 3 was armed 38 minutes after a daemon restart and
  just after a Wi-Fi toggle, and its first hour shows the aftermath of both; the arm's own 180 s of clean
  dwell passed at once and did not see what followed. No general wait is added after an ordinary agent
  session, for which the evidence is mixed.

The owner has been asked to disable the Spotlight agent and restart the Mac during the build, between
windows only. The arm does not wait for it: the restart helps the cells, not the corpus. If the restart has
happened, the post-restart checks of gate 8 apply.

## 8. The questions, and the cold ruling's answers

The draft put ten questions to the judge. This section is the record: each question as it was asked, in
short, and then the answer of the cold ruling (`RULING.md`, sections B and C). Where an answer changed this
text, the place is named.

**J1. The bound grows with n (section 2.5). Which rule?** The draft offered (a) the bound from every kept
member, n from 10 to 18, and assumed it; (b) the bound from the first 12 kept members, built in the chain's
prune, which is collection code; (c) fewer members, for example 15. The refuter added (d): all 18 run, the
chain is unchanged, and the first 12 clean members are chosen at the desk.
**Answer: rule (d), stated in full in section 2.1. Not (a), (b) or (c).** The consult ruling's reason for
(a), "it tightens rather than loosens", is withdrawn: the multiplier t falls, but the bound is the envelope
in every realistic case, and the envelope is an extreme of the sample, which grows with n. The allowance
compensates for validity, not for sharpness or comparability: under (a) every claim would carry a floor
about 20% higher, GAMMA's direction decision would be harder to reach, and the screen's level would differ
between windows with different losses. (b) is the same estimator with a collection-code change and is
refused for that reason alone. (c) pays part of both prices. Screening on the repeatability term alone would
change the registered formula in the core and is refused. Changed here: sections 2.1, 2.2, 2.5, 3, 4.3
table F, 4.5 (edits R15, R19 to R21, P2) and 4.7.

**J2. The core reader (F2).** Is it accepted that every block-5 window is judged by the harvest's route 2,
carries `whole_window.not_passed`, and needs lane L9-NEG8 part (c) for every contrast, with no change to
`whole_window.py`?
**Answer: yes.** Route 2 for every window; no change to `whole_window.py`. A core change would alter a file
that both completed chains executed, for no gain in what is measured. The registration's 5.3 says that route
1 cannot occur in block 5 and carries the three additions of section 4.2 (edit R17).

**J3. `planned_bound_bundles` (F3).** Leave it at 12 in the three calibration plans, as a registered
deviation, so that all 280 science configurations keep their bytes?
**Answer: yes, as deviation 8.** The 280 science configurations and the 12 science order manifests keep the
bytes the three ALPHA attempts ran. No program under `joulewise/` or `scripts/` reads the field.
`bound_count` becomes 18 with the regenerated plan tree (edit R33).

**J4. The 320 s charges (F4).** Leave both sizer constants at 320 s and state the under-charge in the
registration's 5.5?
**Answer: yes.** Both constants stay 320 s (`size_b5_window.py` lines 112, 113); the wall budgets are 1,800 s
each (`chain.py` lines 184, 185). The rehearsal records both wall times; a measured time above 1,200 s for
either goes to a consult before the arm (edit R23; gate 7).

**J5. Stale words that are written into every plan and chain script** (`chain.py` 268, 271, 1198, and the
docstring at 64, 68; `size_b5_window.py` 680, 684). Edit the strings, or leave them and disclose? The draft
recommended editing them.
**Answer: leave `chain.py` byte-identical. The opposite of the draft's recommendation.** `DEVIATIONS` is a
tuple of adjacent string literals (`chain.py` lines 245 to 275), in which a dropped comma merges two entries
with no error, and lines 1197 to 1199 are text rendered into the shell script that runs the window; no logic
reads either. Leaving the file alone keeps the collection-code diff to generated plan trees, corpus files
and generator source that no window runs. The sizer's two `source` strings are left too, so `scripts/` has
no hand edit at all. The stale strings are registered as deviation 9: "The chain script's comments, the
plan's `chain_deviations` and the sizing output's two `source` strings still say 12, 10 and 11; the stage
graph the chain reads says 18, and the desk rule of §5.3 caps the deciding corpus at 12." (edit R33).

**J6. Which commit is the new H_claim built on?** Either the build merges the harvest lane, so that one
commit holds the window's code and the harvest's code, or the new H_claim keeps the first seal's
`harvest.py` and `whole_window.py` and the desk gets a new harvest pin. The draft recommended the second.
**Answer: the second.** The new H_claim keeps H_claim's `harvest.py` and `whole_window.py`, so the code a
window executes stays byte-identical to what ran in two full chains, except the generated plan trees. The
harvest lane then merges the new seal commit, implements the desk rule and the 18-member tests, and the desk
gets a new `B5-HARVEST-PIN` addendum built on the new seal, before the first arm (gate 5).

**J7. The driver's `ok` count (section 6).** Fix the one word in `driver.py` 1754 in this seal, or record it
as a flag and leave the file alone?
**Answer: leave `driver.py` line 1754 alone and record the label mismatch as a flag; it touches no number.**
The larger defect of section 6 is bounded: the runner is changed in this seal only if the cause is shown to
alter a byte or a status that the harvest reads; otherwise the wrong log row is recorded as a known wrong
record with its explanation, and the arm does not wait (section 6, steps 3 and 4).

**J8. The names.** `corpus_id` `neg8-reference-corpus-m3max-qwen25-1p5b-v2-n18`; order manifest
`manifest_id` `neg8-reference-corpus-order-v2` and `plan_id` equal to the corpus id; the directory name
`neg8_reference_corpus_v5` unchanged. Accept, or name others?
**Answer: accepted, all three.** The refuter searched for a program that compares one of these ids with a
fixed string and found none. The dry render (gate 2) and each generator's `--check` (gate 1) are the
executing check.

**J9. The rehearsal** (at least 10 real corpus members through the prune and the mint before the first arm):
required, or struck?
**Answer: required, and widened.** All 18 corpus members, the full start triplet, the midpoint and the end
triplet, and the stage `alpha-science-prefill-p2048-abba-06-10` kept whole, harvested by the pinned harvest
program until its record shows the re-screen evaluated and the clean bound built under the rule of section
2.1; the wall times of the prune and the derivation recorded (gate 7).

**J10. Attempt numbering.** Does the new block's first ALPHA arm carry attempt number 1, with the three
superseded attempts listed separately in the attempt history?
**Answer: yes.** The three superseded attempts are listed separately in the attempt history with their
verdicts and causes, and do not count toward the brief's rule 1. No block marker is added to plan ids unless
a search shows that no program parses the id (section 5).

No question here needed the owner. The consult ruling's Q4 already found that the corpus change, the erratum
and the new seal are agent work under registration sections 7.5 and 10. The cold ruling returned nothing for
redrafting.


## 9. What the seats read, ran and did not run

### 9.1 The drafting seat

**Read.** `BRIEF-body.md` (rules and the file-access passage); `RULING.md`; `alpha-a3-consult.md`;
`opus-consult.md`; `sol-consult.md`; the sealed registration, sections 0.12, 0.17, 4.2, 4.3, 5.1, 5.3, 5.5,
5.7, 6.6, 7.2, 7.3, 7.5, 7.6, 8, 10, 11, 12 and 14 in the parts cited; the analysis plan, sections 2.1 and
8.1; the seal record, sections 1 to 3 and Addendum 1; magistrate brief section 9; the corpus directory whole;
the three plan trees (every entry naming the corpus or the count); `sizing_b5.json` (pack summaries);
`flag_catalog.json` (the corpus codes); `chain.py`, `driver.py`, `plan.py`, `harvest.py`, `whole_window.py`,
`aggregate.py`, `size_b5_window.py`, `run_campaign.py` and `rehearse_b5_real.py` at the lines cited; the three
pack generators and the twin at the lines cited.

**Window files opened** (open files only): `night/hazard_result.json` of attempts 1 and 3, by a program
that printed stage ids, return codes and per-stage counts. No file under a runs root, `flags/`,
`operator-logs/`, `night/transcript/`, `derived/`, `sources/` or `withheld/` of a claim window was opened, and
no program was run over one. The contention journal was not read; its figures here are the judge's recount.

**Rehearsal files opened** (not claim windows): `custody/night/hazard_result.json` of the three real-model
rehearsals, stage ids and return codes only; a directory listing of `alpha-1`.

**Computed by this seat:** the binomial tables of section 2.3; the synthetic bounds and the simulation of
section 2.5; the spans, deadlines and disk figures of section 4.6; SHA-256 of the two settled-corpus
manifests, the two order manifests and the six seal-directory files.

**Not executed:** the test suite or any test; any generator, with or without `--check`; the sizer; a chain
render; anything that writes outside this file; any command on launchd or system settings. The sizing numbers
of section 4.6 are therefore predictions of the sizer's output, to be confirmed by the builder. The test list
of section 4.7 comes from a text search and may be incomplete.

### 9.2 The corrections seat (2026-10-09)

**Read.** `BRIEF-body.md` from its top through "The passage"; the draft of this file, `REFUTATION.md` and
`RULING.md`, whole; the sealed registration (main `3f564499e`) at every line that section 4.5 quotes, and by
pattern search for the old counts, spans and digests; the sealed analysis plan at lines 1 to 6, 70 to 74,
130 to 134, 504 to 513, 594 to 600, 726 to 731, 784 to 808 and 938 to 999; `joulewise/aggregate.py` lines 38
to 62; `joulewise/b5/harvest.py` at the harvest pin, lines 88 to 99, 5225 to 5240 and 5338 to 5436, and a
search for the name `survivors`; `scripts/rehearse_b5_real.py` lines 78 to 104;
`tests/fixtures/d165_rationale_allowlist.json` lines 274 to 296; the consult ruling at its Q2 (ii) only.

**Computed.** SHA-256 of the two sealed documents; the synthetic bounds of the worked example in section 2.1
(Python, on the eighteen synthetic energies of section 2.5; no file read or written); the dead-man offsets
of section 7 and the two figures 37,500 s and 34,375 s of edit R26, by hand.

**Window files opened: none.** No file under a custody root, a runs root or a harvest archive was opened,
and no program was run over one.

**Not executed:** any test, generator, sizer or chain render, and any git command that changes anything. No
agent was started and no network request was made. The seat changed this file, wrote
`CORRECTIONS-APPLIED.md`, and wrote nothing else.
