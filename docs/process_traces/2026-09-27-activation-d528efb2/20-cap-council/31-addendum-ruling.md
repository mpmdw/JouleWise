ADDENDUM: CAP-COUNCIL-25G83-01-A1 ISSUED

# Cold addendum CAP-COUNCIL-25G83-01-A1 — ruling on the paired refuter's dissent

Judge: cold Fable 5.1 seat, one foreground session, 2026-09-27 18:29–18:42 PDT (13 of the 45 budgeted minutes).
Verification tree: `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2`, commit `c772b019`; main `e7c8bcc6` is an ancestor (checked). Digests recomputed by me: `powermetrics_fiducial.py` `386e8254…`, `uncertainty_evidence.py` `b583f35a…`, registration `81b65f08…`.
Inputs, sha256 first 16 characters, recomputed by me: ruling under review `a90b6e768a2137f1`; refuter `8da410811e07e501`; this addendum's charge `6f92e20d944779e1`; consult charge `286ed10291939caa`; cold-gate charge `b0195359a7f2284d`; seats `ccefaad5baa7f926`, `f059a50a5b4eebb4`, `6f3bf12c760f5971`, `8f13b894ab391a3d`.

**Result in one paragraph.** The dissent is upheld on all four blockers. B1, B3 and B4 are adopted; B2 is adopted with one part decided against the refuter's implied alternative (the factor of ten stays, and the August ruling is overruled for this epoch, with reasons). All nine should-fix items are adopted, three of them modified. Route R, the constant cap, the factor of ten, the tripwire, the membership ruling and the 5 ms clock limit stand. §4.3, §6, the closing conditions C1–C7, K2–K3 and §8 of the ruling are replaced by the texts below.

## 0. Contamination disclosure

1. **Preloaded context I did not choose.** Before my first action the session harness injected the owner's global instruction file, the project instruction file of this worktree, the one-line index of the owner's memory store, and the five most recent commit subjects. I opened none of those files, and none of `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, memory files or skill files. The index carries one-line summaries of directives #416 and #421, a status line saying the candidate was cleared and a claim-window hold exists, and owner preferences on gates and writing. One commit subject says "cap refuter DISSENT (4 blockers)", which the charge also states. For #416 I rely only on the issue body I fetched myself (§2). The index holds no B value.
2. **Same model family.** I am Fable 5.1, as were the judge under review, the Fable seat, and the judges of the two rulings cited in the charge. The refuter is Opus 5.5. I sat on no earlier step.
3. **Values I have seen.** "B" is the one timing-uncertainty number a capture yields (§1). I saw: the historical B of one August probe (67.2 ms, printed in the August notes and in the refuter's text); about ten of the eleven 2026-09-19 B values, which appeared in a registration line I printed while looking for something else; the candidate's two statistics as the consult charge prints them. My own replays print cell counts, frame lengths, times and one true/false flag; they print no B.
4. **Other sessions' scratch I read.** `/tmp/cg-cap-d528efb2/mytiming2.py` and `cells_all.py` (the judge's harness), and `/tmp/cg-cap-d528efb2/opus-refuter/replay-results.txt` (the refuter's results).
5. **Other rulings I read.** Of the network-time addendum (SCI-25G83-CANDIDATE-01-A2): its head, its §7 and §8 in full, and the remaining lines only as returned by a text search. Of the D-138 design ruling: lines returned by a text search only, including its §7.3–§7.4 on the hold. I did not read the four seats again in full; the refuter confirms the ruling's table of their positions and nothing in dispute turns on them.
6. **What I executed.** One read-only replay of two stored captures (§2); read-only `git`, `grep`, `sed`, `shasum`; `gh issue view 416`; `sudo -n -l`, which lists permissions and runs nothing. No capture, no powermetrics, no background task, no subagent, no system setting changed. Scratch: `/tmp/cg-capa1-d528efb2/` (`replay.py`, a byte-identical copy of the judge's harness, `f4f8e4241170935d`; `replay-mine.txt`).
7. **Files.** I changed no existing file anywhere. This addendum is one new file. The verification tree's status is the same before and after (one untracked directory that was already there).

## 1. Words used

Terms defined in the ruling's §1 keep their meaning. Repeated here so this file can be read alone:

- **Capture**: one 197-second recording of the power sampler while the machine runs 59 commanded one-second load pulses. **Frame**: one power sample. **Median frame**: the middle value of a capture's frame lengths.
- **Estimator**: the code, in four files, that turns a capture's raw bytes into **B**, the capture's timing-uncertainty number in seconds. **Digest**: the sha256 of a file's bytes. **Pinned file**: one of those four files; the calibration records their digests.
- **Cell**: one rectangle of candidate pulse-edge timings that the estimator tests. **Need**: the number of cells a capture uses when nothing stops it. **The cap**: the most cells one capture may use, 165,000 today (`joulewise/powermetrics_fiducial.py:88`).
- **Wall deadline**: a second stop in the same file, 120 seconds of elapsed time per capture (`:92`). The code comment calls the cell count "the primary reproducible mechanism" and the deadline a catch for "host pathologies" (`:89–91`). A stop on the cap leaves the same record on every machine; a stop on the deadline depends on how busy the machine was, and the record marks it `reproducible: false` (`:1536–1539`).
- **Load average**: the operating system's count of programs wanting the processor at once. About 1–2 on an idle machine; 15–20 on this machine today while several agent sessions ran.
- **Member**: a capture whose B enters a calibration. **Calibration**: the issued file of limits computed from the members. **Registration**: the plan written and sealed before captures are taken.
- **Window**: a scheduled run of captures on a quiet machine. **Claim-bearing window**: one whose numbers will be reported as results. **The HOLD (H1)**: no claim-bearing window at this operating-system build until a written ruling closes the cap question.
- **D-138**: the decision that a change to a pinned file may land on main only inside one reviewed transaction that also re-issues the calibration (`docs/decision_log.md:10361–10383`). **Review gauntlet** (the decision log's "C-028 gauntlet"): the project's standard sequence of independent reviews a code change must pass before it may merge.
- **Directive #416**: the owner's instruction that three model families audit the whole measurement system before any claim-bearing run. Its text is quoted in §2.
- **Network time**: the macOS setting that lets the time daemon `timed` correct the clock from the internet. **H5, H6, H7**: the conditions set by addendum A2 (network time OFF for every window; a per-capture check of the `timed` log; a first comparison of the two states).
- **Launch context**: how the operating system was told to schedule the capture process. The registered context is "Interactive"; the 2026-09-19 captures ran in the default context.

## 2. What I verified by running or reading it

**B1: the stop-time check changes its verdict with machine load. Confirmed by my own replay.** At 18:30 PDT, load average 20.2, cap lifted to 5,000,000, same harness as the judge:

| Capture | Cells | Median frame | Seconds total | Seconds outside the cell loop | µs per cell | Stored B reproduced |
|---|---:|---:|---:|---:|---:|---|
| w1-d03 | 170,965 | 129.645 ms | 49.47 | 43.70 | 33.73 | not applicable (no stored B) |
| w1-d06 | 163,849 | 129.758 ms | 44.50 | 39.16 | 32.60 | true |

The cell counts equal the judge's and the refuter's to the last cell. The times do not:

| Who | Load average | T (s outside loop) | t (µs per cell) | R5: T + 1,710,000 × t | Verdict of R5 (limit 60 s) |
|---|---:|---:|---:|---:|---|
| Judge, ≈18:00 | not recorded | 12.56 | 11.11 | 31.6 s | pass |
| Refuter, ≈18:15 | 15.1 | 33.23 | 27.32 | 79.9 s | refuse |
| This addendum, 18:30 | 20.2 | 43.70 | 33.73 | 101.4 s | refuse |

Same bytes, three verdicts. A rule meant to fix a value cannot contain a check like that.

**A second fact follows from the same replay, and no one reported it.** A healthy capture under *today's* cap already uses 44.5 of the 120 seconds at load average 20, because the deadline clock starts before the 40 seconds of fitting that precede the first cell (`powermetrics_fiducial.py:976–979`). The decision log's statement that the deadline sits "about 440x" above the work was computed as 100,000 cells × 2.7 µs = 0.27 s (`docs/decision_log.md:10162–10174`). It left out the time outside the cell loop. For real captures the margin was never 440; it is about 8 on the judge's figures (120 ÷ 14.4) and 2.4 at load average 20 (120 ÷ 49.5).

**B2: both records exist as the refuter says.**
- The August ruling: "OPTION B — 165,000 UNCHANGED … budget exists to admit corpus-grade captures; the family screen refuses probe-6-class captures regardless; Option A's 1.55M makes the 120 s wall the binding guard → host-dependent failures" (`docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:405–411`).
- The capture: probe `20260818T182149-a7e8b412` "demands 1,282,827 cells (9.21x the next highest)" (`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, field `budget_probe_status`, line 526; the August maximum of 137,535 is in the field `budget_ruling`, line 525, and at lines 531–532).
- The ruling's roster (R2) names the August sweep record. That record does not contain the string `a7e8b412` (search count 0). The probe is therefore outside the roster by the accident of which file was named, and the ruling gives no reason.
- The "family screen" that Option B relied on is not a veto at this epoch: "The predecessor screen challenge is recorded as a diagnostic, not an issuance veto for this epoch" (registration line 632).
- NOT EXECUTED: a replay of the probe. I did not find its raw bytes in the time I had. NOT ESTABLISHED: how the August "knife-edge" validation captures were taken.

**B3: confirmed.** Differences against the common ancestor with main `e7c8bcc6`, pinned files only:

| Commit | Its own subject line says | Pinned files it changes |
|---|---|---|
| `bda7ffe0` | "unreviewed; refuter pending" | `powermetrics_fiducial.py` (+62 −4) |
| `ea10e3c8` | "Acceptance v4 + rev 4 fix round 1"; the registration calls Revision 4 "drafted, never sealed … held at fallback tag" (line 602) | `powermetrics_fiducial.py`, `reduce.py` |
| `aeea07b6` | "UNREVIEWED, magistrate review before any me[rge]" | `reduce.py` (+82) |
| `5135c1d2` | "WIP [RED context] … uncorroborated", dated 2026-07-11 | all four; far behind main |

D-138 consequence (1) reads: "such branches complete their C-028 gauntlet normally but are MERGE-STAGED" (`docs/decision_log.md:10371–10372`). None of the four is ready by its own words.

**B4: confirmed from the owner's text, fetched by me.** Issue #416, binding text as amended 2026-09-25: the audit runs "after W1/W2 pass and before any claim-bearing run"; it is "the #416 audit at the frozen head that will produce paper numbers. Its evidence includes the real W1/W2 bundles, from which the auditors independently re-derive the calibration from raw data"; "If the audit finds a defect in the calibration derivation path, W1/W2 are re-run before any headline run"; the trigger is "CLAIM-RUN WORK COMPLETE (W1/W2 issued plus the headline pipeline frozen), carrying the sha and scope". Seats and method from the original text: Astra 6 at xhigh, Fable 5.1, Opus 5.5 at xhigh, "independently and blind to one another", blockers refuted by a different family, and the window arms "only after every verified BLOCKER is fixed … or ruled not load-bearing by a cold gate".

**S1: confirmed.** `/etc/sudoers.d/joulewise-network-time` exists (296 bytes, 2026-08-17), the same size as `scripts/joulewise-network-time.sudoers`. `sudo -n -l` lists `(root) NOPASSWD: /usr/sbin/systemsetup -setusingnetworktime off, … on`. The functions exist: `joulewise/quiet_predicate_campaign.py:357, 394, 695`. The derivation chain script contains no mention of network time (search returned nothing). Addendum A2 found the same.

**S3: confirmed.** Healthy evidence stores no cell count: the block that would hold it is written "only on governed invalid-evidence paths. Healthy serialized evidence remains byte-identical" (`powermetrics_fiducial.py:1525–1528`). The replay entry point takes no budget argument (`:1095–1103`). The function does return the count in memory: my replay of w1-d06 read 163,849 from the returned object although no stop occurred.

**S4: confirmed.** The registration says "Launch context sets the sampler cadence; this condition is part of the registered experiment" (line 608) and lists the 2026-09-19 night as context "D" (line 628). The issuer sets those captures aside for that reason (`scripts/issue_calibration_acceptance_generation.py:517–520`).

**S5: confirmed.** The issuer collects every valid capture of the same epoch whose session is outside the registration and which has no recorded disposition (`:1430–1443`), and refuses to issue if any exists (`:1558–1562`). The only sessions it exempts are the registration's own and its non-passing windows (`:1482`). The 12 valid W1/W2 rows are such captures for any successor.

**The slot leaves no room for a much longer deadline.** The chain gives each capture 480 seconds to finish (`scripts/night_chains/calibration_derivation_only.zsh:88–90`), of which the recording takes 197. This bounds any answer to B1 that would lengthen the deadline.

## 3. Rulings on the four blockers

### B1 — ADOPTED, modified

The measured stop-time check (R5) is deleted. The replacement rule in §4 contains no measured time. In its place:

1. **Arithmetic on two constants written down now** (R5 below): 45 seconds outside the loop and 35 µs per cell. They are the slowest figures anyone has measured on this machine (mine, load average 20.2, rounded up). The check is a multiplication; anyone gets the same answer on any day.
2. **A synthetic stop test at the production value** (R6 below), as the Opus seat and the refuter asked.
3. **An operating rule for deadline stops** (R8 below), so that a stop caused by a busy machine can never quietly remove one bracket from a claim.

**The refuter asked me either to keep a tenfold margin under load or to justify giving it up. I give it up, and this is the justification.** (a) The margin the decision log describes never existed for real captures (§2). (b) It cannot be restored by lengthening the deadline: a tenfold margin over 30 seconds of quiet-machine work is 300 seconds, which with a 197-second recording exceeds the 480-second slot. (c) It cannot be restored by lowering the cap without putting the cap back next to the work: holding the deadline at 120 seconds and asking for a twofold margin at load average 20 allows at most (60 − 45) ÷ 35 µs ≈ 428,000 cells, 2.5 times the largest need, with the tripwire at 1.25 times. That is the August design again, and it stopped 8 of 24 captures. (d) What the margin protected is kept by other means: a deadline stop makes the capture invalid exactly as a cap stop does, so no wrong number is accepted either way; and under R8 any stop holds the whole window, so no claim is computed from the survivors of a filter. What is lost is only that the diagnostic record of a runaway capture on a very busy machine may differ between machines. Windows run on a quiet machine with no agent session, where the same arithmetic gives about 12.6 + 1,710,000 × 11.1 µs ≈ 31.6 s, a margin near four. *The 12.6 s and 11.1 µs are the judge's figures; the load at that time was not recorded, so "quiet" here is an upper estimate, not a measurement.*

### B2 — ADOPTED; the August ruling is overruled for this epoch, with reasons

The ruling's §4.1 sentence "The cap exists for one reason" is wrong as history and is replaced (§4.1 below). The record gives two purposes: stopping a runaway search, and, per the August ruling, admitting only "corpus-grade" captures. I overrule the second purpose for epoch 25G83, for three reasons.

1. **It rested on a screen that no longer decides.** Option B reasoned that captures like the probe would be refused by the family screen anyway. At this epoch that screen is a diagnostic, not a veto (registration line 632).
2. **Its design is the one that failed.** A cap placed 20 % above the work seen became a filter when the work moved by 25 %. All four seats and the refuter reject that.
3. **Its fear is real and is answered by structure.** Option B feared "host-dependent failures". §2 shows the fear was justified and applies even at today's cap. The answer is R5 (arithmetic, not measurement) and R8 (any stop holds the whole window).

**The probe.** It enters the rule's record under a principle written before replay (R2): the cap is sized from captures that registered chains produced, because those are the captures the cap must admit; captures taken to test the method at its edge are replayed and listed but do not size it. I state the consequence of the other choice so the reader can judge: with the probe in the sizing set the largest need is 1,282,827, the cap would be 12,830,000, and R5 would refuse (45 + 449 s). So the boundary decides the outcome, as the refuter says; it is drawn here on purpose and in the open, with the counts known.

**What the new cap does with a capture like the probe.** It completes (0.75 of the illustrative cap), it trips the tripwire at 0.5, claim-bearing windows halt, and the council looks. In a calibration campaign it fails the acceptance test (R9) and the campaign is void under the ruling's §5 item 4. It is never dropped silently and never accepted silently.

### B3 — ADOPTED

§6 is replaced in full by §5 below. The branch set is named first and frozen first; the value is computed on the bytes that ship; the B-identity test is kept as an extra check and is not an admission test. As the record stands today, no waiting branch is eligible, so the cap change rides alone unless the council shows otherwise by commit and review record.

### B4 — ADOPTED

Step 9's limited pass does not meet the directive. The audit text is §6 below. The ruling's §8 item 4 (a question to the owner) is deleted: the directive answers it.

## 4. Replacement for §4.1 (first paragraph) and §4.3

### 4.1 What the cap is for (replaces the first paragraph of §4.1)

> The record gives the cap two purposes. **First,** a guard: if a pulse's data rule no timing out, the search must test about 5.4 × 10^8 cells; the cap stops that after a fixed, repeatable amount of work (`powermetrics_fiducial.py:77–87`). **Second,** by the magistrate ruling of 2026-08-18, an admission bound sized 20 % above the largest need of claim-bearing captures, which rejected a cap of 1,550,000. This ruling keeps the first purpose and overrules the second for epoch 25G83 (addendum A1 §3, B2).

The scale, redrawn. Cells per capture; each tick is ten times the last; every letter is named below.

```
 10^4          10^5          10^6          10^7          10^8          10^9
  |-------------|-------------|-------------|-------------|-------------|
           S     A E        T  P N L                                F
                   ^O
```

- **S**: need in the default launch context, frames near 250 ms: 44,959–56,289 (measured by the judge and the refuter).
- **A**: need in August, frames near 120 ms: 112,205–137,535.
- **E**: need at this epoch, Interactive context, frames 128–130 ms: 144,037–170,965.
- **O**: the old cap, 165,000. It sits inside E.
- **T**: the tripwire, half the new cap (illustration: 855,000).
- **P**: the August probe, 1,282,827. The one capture on record between healthy work and a runaway.
- **N**: the new cap, ten times the largest need in the sizing set (illustration: 1,710,000).
- **L**: 2,142,857, the largest cap that R5's arithmetic allows.
- **F**: one pulse with nothing ruled out, about 5.4 × 10^8.

### 4.3 The rule (replaces CAP-RULE-25G83-1 entirely)

> **CAP-RULE-25G83-2**
>
> R0. *Words and tool.* A capture's **need** is the number of cells evaluated when the replay harness replays it from its stored raw bytes with the cell limit set to 5,000,000 and the wall deadline set to 3,600 s, its clock alignment resolves, and all 59 pulses fit. Its **median frame** is the median of its native frame lengths in milliseconds. The **replay harness** is one committed script, cited by digest. In sizing mode it changes the two limits just named and nothing else. In report mode it calls the unmodified production function and reads the cell count from the object that function returns. In both modes it prints cells, frame lengths, dispositions, stop triggers, elapsed seconds and a true/false flag "stored B reproduced". It prints no B.
>
> R1. *Code first.* The council names, by commit, every change to a pinned file that will ship with the cap. A change is eligible only if its review gauntlet is complete on the record and it is meant to ship. The four pinned files are then frozen and their digests recorded. Three things stay open: the integer on the cap line, the comment above it, and the two pinned numbers in the cap's unit test. When the value is set, the record shows the difference between the frozen file and the shipped file, and that difference is the cap line and its comment only.
>
> R2. *Roster, written and committed before any replay.*
> (a) **Sizing set:** every retained capture taken on this machine under pulse protocol v3 by a registered derivation chain or window chain, in any launch context. Today that is every capture of W1 and W2 (2026-09-27), every capture of the n1 and n2 sessions (2026-09-19), and every unique protocol-v3 bundle named in `docs/process_traces/2026-08-18-shakedown-first-light/03-budget-calibration-sweep.md`, the shakedown included.
> (b) **Check set:** every retained validation-only capture under protocol v3, among them the eight captures of 2026-08-18 that the August notes call knife-edge bundles, and probe `20260818T182149-a7e8b412`. They are replayed and listed with their need. They do not set the cap.
> (c) Captures whose median frame lies outside R4's range stay in the sizing set. They can raise the cap and cannot lower it.
> (d) A capture with no need (alignment unresolved, or fewer than 59 pulses fitted) is listed with its reason and contributes nothing; it is never counted as zero. A capture whose raw bytes are not retained is listed as such, with any need on record and its source.
> (e) If any replay reaches 5,000,000 cells or 3,600 s, the rule refuses and returns to council.
>
> R3. *Value.* N_max is the largest need in the sizing set. **Cap = 10 × N_max, rounded up to the next multiple of 10,000.** It is written into the code as one integer. It is not a function of frame length or of anything a capture supplies. The wall deadline stays 120 s.
>
> R4. *Covered range.* Per-capture median frame from 100 ms to 150 ms inclusive, in the registered launch context. Need has been measured only in the bands the roster record shows (expected: near 113–121 ms and 127.6–130.2 ms). The rest of the range is covered by the factor of ten and watched by R8, not by measurement. The record says so in those words.
>
> R5. *Deadline arithmetic (can only refuse; uses no measurement).* Two design constants are fixed by this text: T* = 45 s and t* = 35 µs per cell. Require **T* + Cap × t* ≤ 120 s**. If it fails, the rule refuses and returns to council; the value is not lowered automatically. Meaning: on a machine no slower than this one at load average 20, every capture that fits under the cap finishes before the deadline, so whether a capture is valid does not depend on how busy the machine was. Elapsed seconds are recorded by the harness for every replay and every window capture, for information. No recorded time can change the value or the verdict of this rule.
>
> R6. *Guard tests.* (i) The test that the production default stops exactly at the cap (`tests/test_powermetrics_fiducial.py:606–639`) is kept and its pinned numbers (`:579`, `:581`) are set to the new cap and to N_max. (ii) The flat-surface test with an injected limit of 31 cells (`:641–660`) is kept unchanged. (iii) New: a synthetic flat surface run under the production cap and the production deadline stops with trigger `evaluated_cell_budget`, count equal to the cap, no B and no fits. Its elapsed seconds are printed and not asserted.
>
> R7. *Outside the range.* The estimator runs as usual and the cap applies as usual. A capture whose median frame is below 100 ms or above 150 ms is flagged `frame_out_of_covered_range` in the window report. It is not a member. No bracket is dropped for frame length alone: a window containing such a capture has its claim status held, whole, for a council ruling. Extending the range requires need measured at those frame lengths in the registered launch context.
>
> R8. *Tripwire and stops, every window.* At harvest the harness, in report mode, states for every capture its cells, its median frame, cells ÷ Cap, its disposition and any stop trigger. The first capture seen in a 5 ms band of median frame that holds no earlier capture is marked as such.
> (a) If any capture inside the range exceeds 0.5, no further claim-bearing window is armed until council has reviewed the sizing.
> (b) If any capture stops on the cap or on the wall deadline, inside the range or not, the claim status of **that window** is held whole for a council ruling, and no further claim-bearing window is armed until it rules.
> (c) In a replay, a stop on the wall deadline is a failed replay. It is repeated. It is never recorded as a finding about the capture.
>
> R9. *Acceptance test.* Under the shipped bytes, in windows that carry no claim, registered before they run, in the registered launch context, with H5 and H6 met: at least 24 captures in which the cell search ran and whose median frame is inside the range. A capture refused at clock alignment uses zero cells and does not count. A capture outside the range does not count toward the 24, but a stop on it still fails the test. All of: zero stops on the cell count; zero stops on the wall deadline; every cells ÷ Cap at or below 0.5; every median frame reported. The windows are two of 12 declared slots; a third is permitted only if fewer than 24 captures counted, and that condition is written in the registration beforehand. If fewer than 24 count after the third window, the test has not passed and the matter returns to council. The test reads cells, frame lengths and dispositions only. Its record is committed before any B of those windows is read, and that commit is an ancestor of every commit that carries such a B.
>
> R10. *Failure.* A failure of R9 sends the rule back to council. The value is never adjusted between captures or between windows.
>
> R11. *Excluded inputs.* No B value, no statistic or screen computed from B, no energy value and no measured time is read in deciding R1–R10.
>
> R12. *Restart.* Any later change to a pinned file that changes how many cells a capture needs restarts this rule from R1.

**What is fitted:** nothing. The one data-dependent quantity is N_max.

**Worked example, as illustration only.** On counts already printed, N_max is 170,965, so Cap = 1,709,650 rounded up to 1,710,000. R5: 45 + 1,710,000 × 0.000035 = 45 + 59.85 = 104.85 s, under 120 s; it would fail for any N_max above 214,285. Tripwire: 855,000 cells, five times the largest need. The operative value is whatever the roster replay yields under the frozen bytes. The August bundles were swept under an older clock-alignment method, so their needs under today's bytes may differ from the figures above.

**Honest statement of how the rule was written** (replaces Summary item 1's phrase "written before the value is computed"): the rule reads no B, but its author and I knew the cell counts, so the value was foreseeable. The factor of ten and the constants 45 s and 35 µs were chosen with those counts known. With them the illustration passes R5 by 15 seconds. I took the constants from the slowest measurement on record; I did not choose them to pass.

**§4.2 reason 2 is reworded** (S4): "No growth-law check. The 2026-09-19 captures ran in a different launch context, so they show only that no law carries from one context to another; they say nothing about 130–150 ms in the registered context. The check is dropped for a different reason: the fit inside the registered context has 20 points spanning 2.6 ms of frame length, and 150 ms lies 20 ms beyond them. Its verdict would be set by the error of the exponent, not by the machine. The protection is R8, which measures need in every window and halts at half the cap." The §2 paragraph headed "Need does not rise steadily with frame length" is retitled "Need is much lower in the default launch context", and the words "of this same epoch" are replaced by "of this operating-system build, in the default launch context".

## 5. Replacement for §6 — the sequence

1. **Issue the current candidate `dbad7cc7`** under addendum A1's conditions and the D-138 design ruling. The HOLD stands and is enforced in code by that change. If this issuance does not complete, the cap transaction waits for it; no calibration of another epoch is re-pinned in its place (S6).
2. **Land the network-time enforcement** (H5, H6; K2 below) and **file the clock record** (K1). Engineering work and read-only work; no owner action. It must be in force before the next window of any kind.
3. **The council names the branch set** by commit (R1). On today's record none of the four waiting branches is eligible. Unless that changes, the cap rides alone, and each waiting branch later costs its own re-issue and an R12 restart.
4. **Build the staged branch and freeze** the four pinned files; record the digests.
5. **Commit the rule text, the roster and the replay harness;** record their three digests.
6. **Roster replay** under the frozen bytes; compute the value; run R5 and R6. The replay record embeds the three digests of step 5 and the four of step 4, in a commit that descends from both.
7. **B-identity check, as an extra check:** under the final bytes every one of the 12 members replays to its stored B to the last digit, and all 24 captures keep their recorded disposition except the 8 cap stops. A failure stops the transaction and returns to council.
8. **Review gauntlet** for the staged branch. *Recommended, at the lead's discretion, and not a closing condition:* an early multi-family check of the estimator and the derivation path here, because a defect found after step 10 voids the new captures. It does not discharge #416.
9. **Merge the cap transaction** with the interim re-issue (ruling §5 item 2). The interim file's identifier is entered in the code's hold list in the same change.
10. **Seal the successor registration** (owner approval). It names how the 12 W1/W2 rows are handled (§7, S5), pins the chain digest then in force, and declares both purposes of the windows. **Run two non-claim windows** of 12 slots, at least 6 hours apart, no agent session active.
11. **After each window,** before any B is read: the harness report (R8), the H6 log check per capture, then the R9 test.
12. **Derive the successor candidate; cold science gate; issue it.**
13. **Freeze the headline pipeline,** meaning the code that will produce the reported numbers. Send the directive's trigger, "CLAIM-RUN WORK COMPLETE", with the commit and the scope.
14. **The #416 audit** at that commit (§6).
15. **Fixes.** A fix that moves a pinned byte restarts at step 4 (R12). A fix in the calibration derivation path means the two windows are re-run (directive, item 3). After any fix, the audit record names the final commit.
16. **Closing ruling** citing C1–C9 (§8). Then the reviewed change that removes the hold entry from the code, citing that ruling. Then claim-bearing windows.

Cost if nothing fails: unchanged from the ruling's estimate of 2–4 days, plus the audit's hours at step 14. I give no date.

## 6. Replacement for C6 and for step 9's audit — the #416 text

> **The audit.** After the successor calibration is issued and the headline pipeline is frozen, and before any claim-bearing window, three seats audit the whole measurement system at the one commit that will produce the reported numbers: Astra 6 at its highest effort setting, Fable 5.1, and Opus 5.5 at its highest effort setting. Each works alone and sees no other seat's findings. Scope: instrument adapters, calibration and issuance, the window machinery (prepare, install, start-time checks, driver, harvest), reduction, analysis and claim code. Evidence: the raw bundles of the two successor windows and of W1 and W2. Each seat re-derives the successor calibration from the raw bundles independently and compares it with the issued file. Findings are cross-checked; every blocker is tested by a refuter from a different family.
>
> **Pass.** Every verified blocker is fixed under the gates for its kind of change, or ruled not load-bearing by a cold gate; and the commit the audit record names equals the commit from which claim-bearing windows will run.
>
> **Reading stated.** The directive speaks of "W1/W2". I read that as the windows from which the calibration in force for claims is derived, which after this ruling are the two successor windows. This is the stricter reading, so it needs no question to the owner.

## 7. Rulings on the should-fix items

| Item | Ruling | Replacement text or effect |
|---|---|---|
| S1 no owner action needed for network time | **Adopted.** | §8 item 1 of the ruling is deleted. K2 becomes: "H5 and H6 of addendum A2 govern. Before the next window of any kind, the arming path sets network time OFF with the installed passwordless command, saves the command's arguments, exit status, exact output and time, and refuses to arm unless the exit status is 0 and the output is exactly `setUsingNetworkTime: Off`. It restores ON after the last capture and saves that receipt. Whether this is done from the arming session or inside the chain is the implementing lane's choice; if the chain script changes, the successor registration pins the new digest." |
| S2 the 250 µs threshold | **Adopted, modified.** | K3 becomes: "In every capture of R9, the H6 count is zero: no correction of any size, to the clock's offset or to its rate, from 300 s before the capture to 1 s after it. A capture with a count above zero, or with no readable log, does not count toward the 24. One such capture while network time is attested OFF returns the clock question to council, because it would mean OFF does not silence the daemon." Modified because A2's H6 already fixes the query and the interval; I point to it and do not write a second definition. |
| S3 cell counts are not stored; harness not pinned | **Adopted.** | R0 and R8 above. I choose the harness over a change to the pinned file: it leaves healthy evidence byte-identical and adds no registry amendment. The judge's harness did not set the 3,600 s deadline; no replay came near 120 s, so no figure is affected. |
| S4 two launch contexts, not two frame lengths | **Adopted.** | Rewording at the end of §4; R2(c); R4 and R7 now say "in the registered launch context". The Opus seat's growth-law check stays out, for the reason given there. |
| S5 the issuer will refuse the successor | **Adopted.** | Added to the ruling's §5 as item 6: "The 12 valid W1/W2 rows are valid captures of the same epoch outside the successor registration, and the issuer refuses while such rows exist. Before sealing, a reviewed change gives the issuer a way to recognise them. The requirement is fixed here; the design is its own lane. The rows are named in the successor registration by content identifier as 'members of the predecessor, selected under the 165,000 cap'. They are not members of the successor and are not labelled diagnostics, which they are not." |
| S6 no branch if `dbad7cc7` is voided | **Adopted, modified.** | A2 ruled PROCEED, so the case the refuter feared did not arise. The remaining contingency is step 1 of §5. |
| S7 closing conditions not checkable | **Adopted.** | §8 below. |
| S8 a stop inside a claim window | **Adopted.** | R8(b). |
| S9 R9 has no end state | **Adopted.** | R9, the sentence beginning "If fewer than 24". |

Minor points: N1 adopted (the honest statement in §4). N2 adopted (R6). N3 adopted: the ruling's §5 item 2 now cites the writer's own check, which refuses a calibration whose recorded estimator digest differs from the running code (`scripts/validate_powermetrics_fiducial.py:397–402`). N4 adopted: the August maximum is 137,535 under the clock-alignment method then adopted; 137,189 is the earlier sweep.

## 8. Replacement for C1–C7 — when the HOLD closes

The HOLD is closed when, and only when, a closing ruling cites each of the following by file path, digest and commit:

- **C1.** The rule text, the roster and the harness, each by digest; and the replay record, which embeds those three digests and the four frozen estimator digests and sits in a commit that descends from the commits holding them.
- **C2.** The merged cap transaction. The difference between the frozen and the shipped `powermetrics_fiducial.py` is the cap line and its comment. The named branch set, with each branch's review record.
- **C3.** The acceptance record of R9: at least 24 counted captures, each with cells, median frame, cells ÷ Cap, disposition and trigger; zero stops on the cell count; zero stops on the wall deadline; every ratio at or below 0.5. Its commit is an ancestor of every commit that carries a B from those windows.
- **C4.** The successor calibration, derived from the fresh captures, issued and in force.
- **C5.** The clock record K1; for every capture of C3, the H5 receipts and an H6 count of zero.
- **C6.** The #416 audit record at a commit equal to the head from which claim-bearing windows will run, with every verified blocker shown fixed or ruled not load-bearing by a cold gate.
- **C7.** The window report contains a table named `brackets_attempted`, one row per bracket with its disposition and cause, and a test that fails if the number of rows differs from the number of brackets the window declared.
- **C8.** The per-capture report of R8 and the flag of R7 are implemented, each with a test that fails when the report or the flag is removed.
- **C9.** The arming refusal of K2 is implemented, with a test that fails when the refusal is removed.

If any of the nine is missing, the HOLD stands. Windows that carry no claim may run throughout, once step 2 of §5 is in force.

## 9. What of the ruling stands unchanged

- Route R; route M rejected.
- §2's replays and its reading of the `timed` log, except the wording changed by S4.
- §4.2's table and reasons 1, 3, 4, 5 and 6. The cap is one constant, ten times the largest need, with a tripwire at half.
- §5 membership: the eight capped captures and the eleven 2026-09-19 captures are never members; an interim re-issue of the same 12 values that carries no claim; then a fresh registered corpus; the acceptance captures may also be that corpus on the four stated conditions; the disclosed design inputs. Item 6 is added (S5).
- §7: the 5 ms limit on clock movement within a capture; K1 (the filed clock record); K4 (every abandoned bracket recorded by cause).
- §9's list of what was left unchecked, less "reading directive #416", which is now done.

## 10. What now needs Ed

1. **Approval of the successor registration** before it is sealed (unchanged). It now also names the handling of the 12 W1/W2 rows.
2. **Identity of two calibration files:** the interim re-issue and the successor (unchanged).
3. **Nothing else is required.** The administrator action and the question about the audit are both withdrawn.
4. **Optional.** Ed may overrule any of three choices made here with the numbers known: the factor of ten; the overruling of the August "Option B" ruling for this epoch; keeping the August probe out of the set that sizes the cap.

Nothing here publishes anything.

## 11. Left unchecked, stated plainly

- NOT EXECUTED: a replay of probe `a7e8b412` (raw bytes not located in the time available); a replay of the August corpus under today's bytes; any timing on a quiet machine. The machine was at load average 14–20 throughout my session.
- NOT EXECUTED: any review of what the four waiting branches change. I read their subject lines and which pinned files they touch.
- NOT EXECUTED: the issuer itself. S5 rests on reading its code.
- NOT ESTABLISHED: how the August knife-edge captures were taken, and so whether a capture like the probe can arise in an ordinary window. R8 and R9 are written to be safe either way.
- NOT ESTABLISHED: the time the chain spends inside a slot besides the recording and the estimator. My statement that a 300-second deadline does not fit a 480-second slot assumes only the 197-second recording.
- NOT READ in full: addendum A2 and the D-138 design ruling (§0 item 5). If either conflicts with a text above on network time or on the hold in code, that ruling governs its own subject.

## Summary for the owner

1. The refuter was right on all four blockers: I re-ran the timing myself and the old stop-time check gave 101 seconds against a 60-second limit on a busy machine, so the rule now uses cell counts and fixed arithmetic only, and any stop of any kind holds the whole window instead of quietly dropping one measurement.
2. The cap stays one constant at ten times the largest work measured (about 1.7 million cells); the August ruling against a cap that size is overruled for this epoch because the screen it relied on no longer decides, and the one 1.28-million-cell capture on record is shown, listed, and would trip the alarm, not pass unseen.
3. The order is fixed: name and freeze the code first, then compute the value, then new captures, then your full three-family audit at the final frozen commit; you are asked only to approve the successor registration and name the two calibration files, and no administrator action is needed.
