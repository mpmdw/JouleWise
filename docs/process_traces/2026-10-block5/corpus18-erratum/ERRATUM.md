# Prospective cold erratum to registration V5-CLAIM-25G83-B5: an 18-member NEG-8 corpus

**Status: DRAFT for the cold judge and the refuter. It binds nothing until it is ruled on.**
Written 2026-10-09 by an Opus 5.5 drafting seat for the magistrate of block 5. The seat wrote this one file
and nothing else, changed no code and no configuration, started no other agent and made no network request.
Structure only: this file holds no energy, power or duration measured in a claim window, no identity of a
member that failed, and no error text. Every energy printed below is synthetic and is labelled so.

Three things in this draft differ from the cold ruling that ordered it, and the judge should read them first:

1. **The bound gets wider with 18 members, not tighter** (section 2.5). The ruling says the screen "gets
   slightly stricter, never looser". That holds for one of the bound's two terms. The other term, which is the
   larger one in practice, grows by about 20% between 12 and 18 members.
2. **The core reader is tied to the old 12-member file by path** (section 4.2, finding F2). With an 18-member
   corpus every window, even one that loses nothing, is judged by the harvest's second route. No code that a
   window executes needs to change for that, but the registration must say it.
3. **The pack generators fix the number 12 as literals** (section 4.2, finding F1), and one of those literals
   feeds a digest that is stamped into all 280 science configurations (finding F3).

Section 8 turns each into a question that a one-line ruling answers.

## Which text is "the sealed registration" in this file

The brief pointed this seat at the worktree `/Users/edr/code/JouleWise-wt-harvest` (commit
`7e6158d669cbb6fb35761aee18abf363f07c5d36`). That commit descends from H_claim but not from the seal commit, so
its copy of `registration_block5.md` (3,492 lines) is a draft from before the seal: for example it still says a
reported quantity needs 8 of its 10 units, where the sealed text says 5. The sealed text is the one at the
seal commit `ab7b21e576a2d74f0b25d9a26b463d6934588368`, 6,173 lines, SHA-256
`4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841`; the checkout `/Users/edr/code/JouleWise`
(main, `3f564499e`) holds the same bytes (compared by this seat with `git show` and `shasum`). **Every
registration line number below is a line of the sealed text.** The cold ruling's line numbers
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
- **NEG-8 corpus.** The 12 reference members that every window runs first (line 976). "NEG-8" is an inherited
  label, not an abbreviation. After the corpus come three reference members (the **start triplet**), the
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
- **Seal, H_claim, sealed inventory, measurement clone.** **H_claim** is the commit whose files every window
  reads. The **sealed inventory** lists the SHA-256 of each code and pack file at H_claim. The **seal** is the
  record that pins those digests after a cold gate judged the files. The **measurement clone** is the one
  checkout the windows run from; it is never updated.
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

1. **The committed corpus has 18 members.** The existing twelve keep their run ids (`neg8-refcorpus-r01` to
   `-r12`). Six are added (`neg8-refcorpus-r13` to `-r18`). Each new configuration is a byte copy of an
   existing one except for the `run_id` line, as the existing twelve already are of each other (checked:
   `diff` of r01 against r02 and against r12 prints the `run_id` line only). The mint computes a member's
   scientific identity as the SHA-256 of its configuration with the run id removed
   (`joulewise/whole_window.py` lines 4849 to 4853 at the harvest pin), so all 18 share one identity, which
   the mint requires.
2. **Every member runs in every window, in the committed order** r01 to r18. No program decides at run time
   whether the last six run.
3. **The bound is derived from every member that succeeded and that the mint and the physics drop keep.**
   The mint's five reasons and the harvest's six physics codes are unchanged. The number of members the bound
   rests on, n, is from 10 to 18.
4. **The minimum stays 10** (`whole_window.NEG8_DRIFT_MINIMUM_N`, line 136; `chain.NEG8_RETRY_MINIMUM`,
   line 235; `driver.CORPUS_MIN_VALID`, line 152). With fewer than 10 kept, `neg8.bound_not_derived` removes
   the window, as now.
5. **The one corpus retry stays, unchanged.** It runs when fewer than 10 of the 18 succeeded. It can measure
   a member that has no bundle directory (one refused before its bundle existed). It cannot measure a member
   that aborted, because that member has a bundle. For the loss this erratum is about, the retry does
   nothing, and the registration will say so in those words.
6. **The corpus has a new identity.** `derivation/settled_corpus.json` gets a new `corpus_id`, because the old
   one names a 12-member set and every bound records the id and the SHA-256 of the manifest it was built
   from. Proposed: `neg8-reference-corpus-m3max-qwen25-1p5b-v2-n18`.

### 2.2 How a reader would rebuild it

Take the list of 18 run ids in order. Run each as a member. For each, read the status in its summary. Keep
the members whose status is `succeeded`. From those, remove any member the mint rejects for one of its five
validity reasons. If fewer than 10 remain, there is no bound and the window is removed. Otherwise compute the
bound of section 2.4 from the remaining energies. At the desk, remove from that set every member on which one
of the six physics codes fired; if any was removed, compute the bound again from the rest, and if fewer than
10 remain the window is removed. No step looks at a member's energy to decide whether it stays.

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
| 12 | 11 | 2.201 | 1.797 |
| 18 | 17 | 2.110 | 1.723 |

### 2.5 What the bound does when n grows (this corrects the ruling)

The ruling's Q2 (iii) says that with more members "the t multiplier falls ... on a normal window the screen
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

What this means, stated plainly:

- On a window that keeps all 18, the bound is about **20% larger** than on a window that keeps 12 (2.82 σ
  against 2.36 σ), and about 33% larger than on one that keeps 10.
- A larger bound makes the screen **easier to pass**: a drift has to be about 3.5 standard deviations of the
  screen statistic to remove an 18-member window, against about 2.9 for a 12-member one.
- A larger bound also makes the **drift allowance larger**, and the allowance is added to every claim's
  uncertainty. So a drift that the wider screen lets through is still covered by the allowance the claims
  carry. The claims stay honest; they get less sharp. GAMMA's two contrasts carry this allowance.
- The bound now depends more on how many members were lost. Under the present rule n is 10 to 12 and the
  mean bound ranges over 2.13 σ to 2.36 σ. Under the new rule n is 10 to 18 and it ranges over 2.13 σ to
  2.82 σ. A window that lost more corpus members gets a smaller bound.

This does not make the rule wrong. The envelope is defined as the widest gap the corpus itself could show, and
a larger corpus shows a wider one. But the registration must state the range and its direction, and the judge
should rule on it knowingly (section 8, question J1, with an alternative that keeps n at 10 to 12).

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
| The physics drop | six codes | registration 5.3 lines 2887 to 2890 | Unchanged. |

**The protections against selecting on an outcome, one by one.**

- *No step decides anything from a corpus energy.* The chain's retry decision counts summary statuses
  (`chain.py` lines 822 to 835). The chain's prune asks the mint which members it drops, and the mint's five
  reasons are validity tests that would also remove a science member. The harvest's physics drop reads the
  monitor's journals. None of these reads the size of a member's energy. With 18 members the same code runs
  on a longer list.
- *All 18 always run.* There is no rule of the form "run more members if the first ones look bad". This is
  why the ruling preferred 18 unconditional members to a spare stage triggered at run time: a rule with no
  run-time decision cannot be steered.
- *A succeeded member left out for any other reason still removes the window.* The harvest accepts a
  collected manifest only if its members are committed members, each once, in committed order, at least 10,
  and every member left out either did not succeed or was dropped by the mint for one of the five reasons;
  any other succeeded member left out is a selected corpus and gives `neg8.bound_not_derived`
  (`harvest.py` harvest pin lines 4703 to 4737; registration lines 2775 to 2781 and 2873 to 2875). That test
  compares the collected list with whatever the committed manifest lists, so it applies to 18 as it does
  to 12.
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
| `chain.py` 268, 271 | the same words inside the `DEVIATIONS` tuple | **text that is written out**: every chain script prints the tuple as shell comments (line 1075) and every window plan stores it as `chain_deviations` (`joulewise/b5/plan.py` 910, 958). No logic reads it. See question J5 |
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
| `scripts/size_b5_window.py` 396 | each stage's order manifest must list `expected_count` members | live logic, reads the count |
| `size_b5_window.py` 585 to 598 | the corpus stage is found from the stage rows; the retry is charged from its member count | live logic, reads the count |
| `size_b5_window.py` 112, 113 | `B5_BOUND_DERIVATION_S = 320`, `B5_CORPUS_PRUNE_S = 320` | **live sizing constants chosen for 12 bundles**. See F4 |
| `size_b5_window.py` 108 | comment | comment |
| `size_b5_window.py` 680, 684 | "re-reduces 12 bundles", "the same 12 bundles" | **text written into `sizing_b5.json`** (`terms.bound_derivation.source`, `terms.corpus_prune.source`). No logic reads it |
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

So the build is not configuration alone: it edits generator source in four files. It edits no file among the
driver, the chain's logic, the runner, the controller, the hazard modules, the harvest's logic or the core.

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
                         collected manifest, checks every member against its bundle,
                         and runs the screen again itself; that re-screen decides
```

Each arrow is "then"; the two branches are the reader's two outcomes. Route 2 needs no code change: the chain
always writes the collected manifest and the driver always records it (`chain.py` 629 to 635 and 1336 onward),
and when nothing was dropped the collected manifest is the committed 18-member file byte for byte (`chain.py`
627, 628: the bytes are re-rendered only if a member was dropped). But three things become true of **every**
window, not only of a window that lost members:

- the stored verdict reads "failed" and the window carries `whole_window.not_passed` (disclosed only);
- the harvest's re-screen, not the stored verdict, decides the screen;
- every contrast needs part (c) of lane L9-NEG8 (a planned repair of claim-time code, which never runs in a
  window; analysis plan section 11, line 729) before it can be claimed, because the claim validator
  rejects a row whose stored screen failed before it reads the harvest's record (registration 0.12, "Which
  bracket carries the allowance", line 1205 onward). That lane was already required before any claim; it was
  needed for every floor and for some contrasts, and is now needed for every contrast.

The alternatives are a change to the core (point the reader at the `_v5` file, or let it accept either), which
is collection code and would stop historical 12-member bounds from authenticating, or overwriting the
historical file, which rewrites history. This draft assumes route 2 for every window and no core change
(question J2).

**F3. One literal feeds a digest that is stamped into all 280 science configurations.** Each pack's
`calibration_plan.json` carries `"planned_bound_bundles": 12` (line 1653 in the two floor packs, 1150 in
GAMMA's). The SHA-256 of that file is written into every science configuration of the pack as the tag
`calibration-plan-sha256=<digest>` and into every science stage's order manifest (counted by this seat: 100,
100 and 80 configurations carry their pack's digest). No program under `joulewise/` or `scripts/` reads
`planned_bound_bundles` or `bound_count` (searched). Two ways to build:

- *Leave `planned_bound_bundles` at 12.* The calibration plans and all 280 science configurations keep their
  bytes, so the science members of the new block are byte for byte the ones the three ALPHA attempts ran. The
  field is then a stale descriptive value. The registration has a precedent: the plan trees' `attempt_policy`
  is "superseded by the flag catalog and disclosed, not regenerated" (section 5.2; deviation 2, section 10).
- *Change it to 18.* Truthful files, but three new calibration-plan digests, 280 changed science
  configurations, 12 changed science order manifests, and every pin on them.

This draft assumes the first, registered as a new deviation (question J3).

**F4. Two sizing charges were chosen for 12 bundles.** The sizer charges the bound derivation and the corpus
prune 320 s each, from an estimate of 270 to 320 s for re-reducing 12 bundles that the registration calls
"never measured live" (section 5.5, line 3018). Scaled to 18 bundles that estimate is 405 to 480 s each, up to
160 s over the charge, 320 s for both. The chain's wall budget for each is 1,800 s (`chain.py` 184, 185), so
neither stage is cut. The programmed span exceeds the expected chain by more than 70,000 s (section 4.6), so
the window deadline is not at risk. This draft leaves the two constants alone and states the under-charge in
section 5.5 (question J4).

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
| 10, 11 | the two floor generators | lines 241 and 246 to 248: the two new digests; 727: 18; 1818: 18; 2851: unchanged at 12 if J3 is ruled as assumed |
| 12, 13 | the contrast generator and its twin | line 2365: 18; 2056: unchanged at 12 if J3 is ruled as assumed |

**C. Generated pack files.**

| # | File | Generator | What changes |
|---|---|---|---|
| 14, 15 | `d117_floor_qwen3-1p7b_v5/plan_tree.json`, `plan_tree.sha256` | that pack's `generate_configs.py` | corpus stage `expected_count` 12 → 18; `external_inputs.manifests[0]`: `expected_count` 18, six more member pins, new manifest digest; the settled-corpus digest in the derivation stage and in `external_inputs.artifacts[0]`; `runtime_budget.bound_count` 18 |
| 16, 17 | the same two files of `d117_floor_qwen3-8b_v5` | its generator | the same |
| 18, 19 | the same two files of `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` | its generator | stage `gamma-bound-collection` `expected_count` 18; `external_inputs[0]` with 18 pins and the new manifest digest; `external_inputs[1]` the new settled-corpus digest |

If the generators rewrite any other file of a pack, that is a defect of the build: with J3 as assumed, a
`git diff --stat` of each pack directory must show the generator, `plan_tree.json`, `plan_tree.sha256` and
(only if they embed a plan-tree digest) the pack's `README.md`, and nothing else.

**D. Block-level generated files in `configs/campaigns/v5_claim_25g83/`.**

| # | File | Generator | What changes |
|---|---|---|---|
| 20 | `sizing_b5.json` | `scripts/size_b5_window.py` | the three plan-tree digests, the corpus manifest digest, members, spans and deadlines (section 4.6) |
| 21 | `identity_pins.json` | `scripts/write_b5_identity_pins.py` | it records the three plan-tree digests; no model or runtime pin changes |
| 22 | `sealed_inventory.json` | `docs/process_traces/2026-10-07-block5-seal/bench/make_sealed_inventory.py` | regenerated from the new H_claim and committed alone as the new seal commit |
| 23 | `registration_block5.md` | hand | section 4.5 |
| 24 | `analysis_plan_block5.md` | hand | section 4.5 |

**E. Other tracked files.**

| # | File | Generator | What changes |
|---|---|---|---|
| 25 | `configs/pins/registry.json` | `scripts/digest_pin_census.py --write` | six new corpus files and the changed digests |
| 26 | `joulewise/b5/chain.py` | hand | only if J5 is ruled "edit": the words at 64 to 68, 268 to 271 and 1198 |
| 27 | tests (section 4.7) | hand | assertions of 12, 119, 101, 126 and the sizing numbers |

`flag_catalog.json`, the campaign policy, the reference and spare directories, the runner, the controller, the
driver, the harvest and `whole_window.py` do not change.

**Count: 25 files change for certain** (9 in the corpus directory, 4 generators, 6 generated pack files, 5
block-level files, the pin registry), plus `chain.py` if J5 says so, plus tests.

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

# 6. After the merge: the new H_claim, the inventory, the seal commit (magistrate brief section 9, steps 1 to 4).
python3.13 -B docs/process_traces/2026-10-07-block5-seal/bench/make_sealed_inventory.py <clean checkout at new H_claim> <out.json>
python3.13 -m unittest tests.test_b5_seal_landing
```

The commands of steps 4 and 5 are the ones the pack READMEs and the registration name; this seat did not run
them, because every one of them writes or was built to be run in a build worktree. The builder records the
exit code of each `--check`.

### 4.5 Text edits to the registration and the analysis plan

Line numbers are of the sealed text. "→" separates the old wording from the new.

| Section | Line | Edit |
|---|---|---|
| Change summary | 87 | "each window starts with 12 reference runs" → 18; add that a window may keep 10 to 18 |
| 0.12, Reference member | 976 | "Each window runs 12 at its start" → 18 |
| 0.12, NEG-8 bound | 1004 | "n their count (10, 11 or 12; §5.3)" → "(10 to 18; §5.3)". Add after the formula: the multiplier table of section 2.4 of this erratum, and the paragraph and table of section 2.5 (the envelope grows with n; the mean bound ranges from 2.13 σ at 10 to 2.82 σ at 18 for normal draws) |
| 0.12, worked example | 1233 | keep the twelve-member example and label it "a window that kept 12 of its 18"; add the 18-member example of section 2.5 |
| 0.17, window plan | 406, 1411 | "the 12 NEG-8 corpus members" → 18 |
| 2, dry render record | 1772 to 1774 | leave as the record of 2026-10-07; add the new dry render's record beside it (section 7) |
| 4.2, disk | 2240 to 2247 | 126 → 132 members and 22.4 → 23.5 GiB for ALPHA and BETA; 108 → 114 and 19.2 → 20.3 GiB for GAMMA; 87.2 → 90.4 GiB and 77.6 → 80.8 GiB required |
| 4.3, thresholds | 2261, 2262 | `planned_bytes` = 126 × 182 MiB = 24,045,944,832 → 132 × 182 MiB = 25,190,989,824 |
| 5.1, corpus retry | 2705 | "fewer than 10 of the 12" → "of the 18". Add: "An idle-admission abort leaves a complete failed bundle, so the retry never repairs it. In block 5's first two chains every corpus loss was of this kind and the retry measured nothing. The retry is kept for the member refused before its bundle exists." Rework the worked example (2710 to 2714) on 18 |
| 5.3, title | 2752 | "may lose up to two members" → "may lose up to eight members" |
| 5.3, rule | 2755 | "at least 10 of the 12" → "at least 10 of the 18" |
| 5.3, why it matters | 2759, 2760 | replace with the table of section 1.1 and the table of section 2.3 of this erratum, with the sentence that losses cluster |
| 5.3, item 2 | 2770 to 2772 | "That reader authenticates a bound only against the committed 12-member manifest. It therefore treats a 10- or 11-member bound as absent" → "That reader authenticates a bound only against the historical 12-member manifest `configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json`. The block-5 corpus has 18 members under its own id, so the reader treats every block-5 bound as absent" (if J2 is ruled as assumed) |
| 5.3, item 3 | 2775 | add: "Route 1 cannot occur in block 5; route 2 judges every window." |
| 5.3, closed list | 2848, 2849 | "may rest on 10 or 11 members" → "on 10 to 17 members when some are left out" |
| 5.3, physics example | 2908 to 2911 | rework on 18: a third flagged member leaves 15, not 9 |
| 5.5, corpus retry charge | 3012, 3013 | "12 × (595 + 45 + 32) s = 8,304 s" → "18 × (595 + 45 + 32) s = 12,336 s" |
| 5.5, derivation and prune | 3018 to 3020 | "re-reduces 12 bundles, about 270–320 s" → "re-reduces up to 18 bundles; the estimate for 12 was 270–320 s, so 405–480 s for 18; the charge stays 320 s and the difference, at most 160 s for each, is inside the span's margin; the wall budget is 1,800 s" (if J4 is ruled as assumed) |
| 5.5, sizing output | 3028 onward | the new SHA-256 of `sizing_b5.json` at the new H_claim |
| 5.5, table | 3056 to 3058 | section 4.6 of this erratum |
| 5.5, decomposition | 3068 to 3072 | "119 members × 595 s = 70,805 s" → "125 × 595 = 74,375 s"; custody "119 × 77 = 9,163" → "125 × 77 = 9,625"; retry 8,304 → 12,336; the other 5,130 s unchanged; span 106,890 s |
| 5.5, expected chain | 3094 onward | section 4.6 |
| 5.7, yield plan | 3190 | "(… a minimum of 12 would raise a false alarm in about 28% of windows)" → "(the bound's minimum, §5.3; 10 of 18)" |
| 5.7, worked example | 3286 to 3288 | "corpus 12/12" → "18/18"; "99 of 119" → "105 of 125" |
| 8, worked example | 4743 to 4745 | "GAMMA plans 101 members … the 12 NEG-8 corpus members" → 107 and 18 |
| 10, deviation 3 | 4991 | "may be derived from 10 or 11 corpus members" → "from 10 to 17 of the 18" |
| 10, new deviation 8 | after deviation 7 (line 5011) | "Each pack's `calibration_plan.json` still reads `planned_bound_bundles` 12; the plan tree's stage graph, which the chain reads, says 18. No program reads the field. It is left so that the science configurations keep the bytes of the superseded attempts." (if J3 is ruled as assumed) |
| 13, binding register | 5753 | "12 corpus members … 101 in all" → "18 … 107 in all" |
| 14 | new entry | this erratum, its ruling, and that the three superseded ALPHA attempts are listed in the attempt history |

Analysis plan: line 597, "corpus size (10, 11 or 12). For a corpus of 10 or 11, also disclose that the bound
was validated against the collected members and that the harvest's re-screen, not the stored verdict, decided
the screen" → "corpus size (10 to 18), printed beside every window's allowance. For every block-5 window,
disclose that the bound was validated against the collected members and that the harvest's re-screen decided
the screen (registration §5.3)." Section 2.1 (line 72) already says that the windows of a superseded block are
disclosed and never analysed; add the three ALPHA attempts by plan id to the attempt history of section 8.

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

Tests to add: (i) a chain render of each pack shows the corpus stage with 18 members and `--max-failures 18`;
(ii) the harvest accepts a collected manifest of 18, of 10 and of 13 with a gap in the middle, and refuses 9
and refuses a succeeded member left out; (iii) the core reader returns nothing for an 18-member bound and the
harvest then takes route 2 with all 18 (F2); (iv) the bound builder at n = 18 uses t = 2.110.

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

The new block starts at **ALPHA attempt 1 under the new seal**. Attempt numbers restart; plan ids must not
collide with the three above (they carry their own time stamps, and the magistrate may add a block marker).
The paper's attempt history lists the three superseded attempts with their verdicts and causes beside the new
block's attempts (analysis plan sections 2.1 and 8). Every reported number stays conditional on its window
having passed the quiet, timing and drift tests (registration 7.6), and the count of attempts the reader sees
includes the superseded ones.

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
so that rehearsal ran 1 of the stage's 20 members. The builder therefore:

1. runs the rig for ALPHA with the whole stage kept:
   `scripts/rehearse_b5_real.py all --pack <alpha> --base <new directory under rehearsal-real/>
   --keep '{"06_phase_prefill_p2048_abba_blocks_06_10": 20}'` (the pack name as the rig's `--pack` choices
   spell it), with no agent session doing other heavy work;
2. reads `custody/operator-logs/12-alpha-science-prefill-p2048-abba-06-10.log` of that rehearsal. The runner
   prints one line per member, `<status> <run id>: exit=<code> ...` (line 11340), then `Summary:` with a count
   per status, then `COLLECTION VERDICT (provisional):` with the verdict, each reason and the four category
   counts (lines 11361 to 11377). The member line with status `failed` names the member and gives its exit
   code: nonzero means case 1; zero with the member under `failed` in the verdict means case 2; a
   `missing member bundle(s)` reason means case 3;
3. if 20 members reproduce nothing, repeats with the two preceding prefill stages also at full size, since a
   position in the window may matter;
4. states the cause, and fixes it only if the fix is in code that this build already changes or in desk code.
   A fix in the runner is collection code; it rides in this same seal if it is needed, and it is otherwise
   recorded as a known wrong record with its explanation.

**A second, smaller defect seen in the same record.** The driver's `ok` count is 0 for every stage of both
attempts, including stages with 20 of 20 succeeded and return code 0. The driver counts log rows whose status
equals `succeeded` (`driver.py` 1754), but the runner's word for a good member is `ok` (`run_campaign.py`
214 to 225 and 11228 to 11232). The count is a label in a record; nothing reads it for a decision. Under the
doctrine that a finding about representation is a flag and not a fix round, this is recorded here and goes to
the judge as question J7.

## 7. Gates

**Before the build: this erratum, ruled cold.** One Fable 5.1 judge and one Opus 5.5 refuter (registration
section 10, line 4971; magistrate brief section 9). They rule on: the rule of section 2; the n range and the
bound's behaviour over it (section 2.5); the files (section 4.3); the cause statement (section 1.4); and the
questions of section 8. A disagreement is settled in this one erratum.

**Before the first arm**, as the ruling's Q2 (v) lists them:

1. the merge gates for code and inputs that a window executes: an independent executing review by a
   non-author; the whole test suite on the merged tree; continuous integration green on the final head; a
   cold Fable 5.1 pass, because the change touches measurement; every finding dispositioned (fixed, deferred
   to a named lane, or rejected with a reason); the Impact statement (the pull request's paragraph saying
   which numbers the change can move);
2. the re-audit that directive #416 requires after a change to frozen code (a blind audit of the system
   before arming), scoped here to the diff (registration 7.5, line 4621);
3. a dry render of each pack's chain showing the corpus stage with `expected_count` 18 and
   `--max-failures 18` (`chain.py` 509 to 516), recorded as the new dry-render record;
4. the new seal: the merged commit is the new H_claim; the sealed inventory is generated from a clean
   checkout of it and committed alone as the seal commit; `tests.test_b5_seal_landing` passes; the seal record
   gains a section that pins the new digests (the three documents, the three plan trees, `sizing_b5.json`,
   `identity_pins.json`);
5. a new measurement clone at the new seal commit, with the calibration ledger and its pin carried over, and
   a new fixed-values file naming the new `MEASUREMENT_ROOT`, `H_CLAIM` and `SEAL_HEAD`. One consult seat
   checks the carry-over commands before they run; they have not been rehearsed (brief section 9, step 3);
6. the desk seal check with the new H_claim;
7. the harvest program for the new block, pinned by an addendum before the new ALPHA attempt 1 is harvested
   (question J6 asks from which commit).

This draft adds one item for the judge to accept or strike: **a real-model rehearsal that keeps at least 10
corpus members**, so that the prune and the mint run once on a real 10-or-more-member corpus before a claim
window depends on them. Both archived real-model rehearsals kept one corpus member, and in both the
derivation stage returned 2 (read from their terminal records). The section 6 rehearsal can carry this by
adding `"neg8_reference_corpus_v5": 18` to its `--keep` argument, at a cost of about 18 member cycles.

**Two procedure items, in force now.** They are not registered rules and need no erratum, because they change
no file a window reads, no threshold, no catalog effect, no roster and no blinding rule.

- *(a) `/private/tmp` is small before every arm.* Reason: the operating system runs a cleaner at 00:00 local
  time every day that walks `/tmp` with two `find` passes. Their length is the size of the tree. In attempt 3
  the tree held about 149 GiB of agent-session scratch, the walk took about five minutes, and it fell inside
  the corpus stage (31 consecutive dirty intervals). A small tree makes the walk a matter of seconds. The
  check is the entry count and size of `/private/tmp`; below about 100 entries and 1 GiB it passes. Until it
  passes, the fallback holds: no window is armed whose span contains 00:00 local. (The magistrate's attempt
  to move the scratch was refused by its permission check; a restart of the Mac empties the directory.)
- *(b) A settling wait of 60 minutes, display asleep (`pmset displaysleepnow`), between any daemon restart,
  Wi-Fi toggle or owner login and the arm.* Reason: attempt 3 was armed 38 minutes after a daemon restart and
  just after a Wi-Fi toggle, and its first hour shows the aftermath of both; the arm's own 180 s of clean
  dwell passed at once and did not see what followed. No general wait is added after an ordinary agent
  session, for which the evidence is mixed.

The owner has been asked to disable the Spotlight agent and restart the Mac during the build, between
windows only. The arm does not wait for it: the restart helps the cells, not the corpus.

## 8. Questions for the judge

Each is written so that one line answers it. The draft's assumption is stated first.

**J1. The bound grows with n (section 2.5). Which rule?**
(a) As the ruling has it: the bound from every kept member, n from 10 to 18, with the registration stating
that the mean bound and the drift allowance are about 20% larger at 18 than at 12 and that n is printed
beside every window. No code. *The draft assumes (a).*
(b) The bound from the first 12 kept members in committed order, the rest run and recorded but not used. n
stays 10 to 12 and the bound keeps today's size. Membership is still by committed position and status only.
This needs code in the chain's prune helper (collection code) and in the harvest's subset test and physics
drop, which must learn a sixth accepted omission and must pull the next member in when a physics code drops
one of the twelve.
(c) Fewer members, for example 15 (mean bound 2.62 σ; at the observed loss rate the chance of keeping 10 is
0.93 by the formula of section 2.3).
This seat's view: (a) is acceptable science, because the wider bound is carried by every claim as allowance,
so the error is on the cautious side; its cost is sharpness, most of all for GAMMA's two contrasts. (b) is the
better estimator and the slower build. The judge should choose knowing that the ruling's reason for (a), "it
tightens rather than loosens", is not correct.

**J2. The core reader (F2).** Is it accepted that every block-5 window is judged by the harvest's route 2,
carries `whole_window.not_passed`, and needs lane L9-NEG8 part (c) for every contrast, with no change to
`whole_window.py`? *The draft assumes yes.* The alternative is a core change so that a full 18-member bound
authenticates directly.

**J3. `planned_bound_bundles` (F3).** Leave it at 12 in the three calibration plans, as a registered
deviation, so that all 280 science configurations keep their bytes? *The draft assumes yes.* The alternative
changes 280 configurations and three calibration-plan digests for a field no program reads.

**J4. The 320 s charges (F4).** Leave both sizer constants at 320 s and state the under-charge in section
5.5? *The draft assumes yes.* The alternative is an edit to `scripts/size_b5_window.py`.

**J5. Stale words that are written into every plan and chain script** (`chain.py` 268, 271, 1198, and the
docstring at 64, 68; `size_b5_window.py` 680, 684). Edit the strings, or leave them and disclose? This seat
recommends editing them: a window plan that says "byte-identical when all 12 are kept" of an 18-member corpus
is a false sentence in a custody record, the edit changes no logic, and this build is audited as collection
code in any case. *The change list counts `chain.py` as conditional on this answer.*

**J6. Which commit is the new H_claim built on?** Main holds H_claim's `harvest.py` and `whole_window.py`.
The harvest lane's versions (items K-4 to K-7, pinned as `B5-HARVEST-PIN: 7e6158d66…`) are not merged into
main (checked with `git merge-base --is-ancestor`). Either the build merges that lane, so that one commit
holds the window's code and the harvest's code and the in-window `whole_window.py` changes by that lane's 80
lines, or the new H_claim keeps H_claim's two files and the desk root gets a new harvest pin built on it. The
first is one head and a larger audited diff; the second keeps the window's code byte-identical to what ran.
This seat recommends the second, because it keeps the collection-code diff to the generators, the plan trees
and (by J5) three strings.

**J7. The driver's `ok` count (section 6).** Fix the one word in `driver.py` 1754 in this seal, or record it
as a flag and leave the file alone? This seat recommends leaving it: it touches no number, and `driver.py` is
otherwise unchanged by this build.

**J8. The names.** `corpus_id` `neg8-reference-corpus-m3max-qwen25-1p5b-v2-n18`; order manifest
`manifest_id` `neg8-reference-corpus-order-v2` and `plan_id` equal to the corpus id; the directory name
`neg8_reference_corpus_v5` unchanged. Accept, or name others? (Not verified by this seat: that no program
compares the order manifest's `plan_id` with a fixed string. The dry render and the generators' `--check`
would show it.)

**J9. The rehearsal of section 7** (at least 10 real corpus members through the prune and the mint before
the first arm): required, or struck?

**J10. Attempt numbering.** Does the new block's first ALPHA arm carry attempt number 1, as the ruling says,
with the three superseded attempts listed separately in the attempt history? *The draft assumes yes.*

No question here needs the owner. The ruling's Q4 already found that the corpus change, the erratum and the
new seal are agent work under registration sections 7.5 and 10.

## 9. What this seat read, ran and did not run

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
