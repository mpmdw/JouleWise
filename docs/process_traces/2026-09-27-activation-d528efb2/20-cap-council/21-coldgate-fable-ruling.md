RULING: CAP-COUNCIL-25G83-01 ISSUED

# Cold gate CAP-COUNCIL-25G83-01 — the 165,000-cell work cap at epoch 25G83

Judge: cold Fable 5.1 seat, one foreground session, 2026-09-27 ≈17:54–18:20 PDT (inside the 45-minute budget).
Verification tree: `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2`, commit `c772b019`, of which main `e7c8bcc6` is an ancestor. The four estimator files there have the digests the candidate pins (`386e8254…`, `b583f35a…`, `70f47086…`, `7b9c0d28…`), recomputed by me.

Inputs as I read them (sha256, first 16 characters): charge `286ed10291939caa`; Sol `ccefaad5baa7f926`; Astra `f059a50a5b4eebb4`; Opus `6f3bf12c760f5971`; Fable seat `8f13b894ab391a3d`; cold-gate charge `b0195359a7f2284d`; registration `81b65f08b19127a1`.

## 0. Contamination disclosure

1. **Preloaded context I did not choose.** Before my first action the session harness injected the owner's global instruction file, the project instruction file of the judge worktree, and the one-line index of the memory store. I opened none of those files, and none of `RUN_STATE.md`, `AGENTS.md`, memory files or skill files. The index carries owner directives and status lines, including one-line summaries of the two directives the charge cites (#416 and #421) and a status line saying the candidate was cleared and a claim-window hold exists. I use both directives only as the charge states them. The index holds no B value.
2. **`TASK_QUEUE.md`.** Read by a search for the strings `A331` and `A332` only; four rows returned (each lane appears twice).
3. **Same model family.** I am Fable 5.1, as were the Fable seat and the two earlier judges whose rulings I read. I sat on no earlier step.
4. **Values I have seen.** The 20 B values printed in the science-gate ruling's table, and the eleven 2026-09-19 values printed in the registration. Every rule below is therefore written with those values known. My own scripts print cell counts, frame lengths, compute times and one true/false flag ("the replay equals the stored B"); they print no B.
5. **Seat scratch I read.** `/tmp/cap-council-d528efb2/fable/evidence.md` and `timing.py`; `/tmp/cap-council-d528efb2/opus/applies.txt` and `prune_probe.py`. The `/tmp` copy of the Opus answer differs in size from the repository copy; I read the repository copy, whose digest matches the charge.
6. **What I executed.** Read-only replays of six stored captures; one query of the system log for the time daemon; one refused call to `systemsetup` (it needs administrator rights). No capture, no powermetrics, no background task, no subagent. Scratch: `/tmp/cg-cap-d528efb2/` (`mytiming.py` `8f5dba0a807ed735`, `mytiming2.py` `f4f8e4241170935d`, `cells_all.py` `8c0bbbf505a1dd5a`, `timed-mine.txt` `0ebcefc6cdcbb9e0`).
7. **Files.** I changed no existing file anywhere. This ruling is one new file. The verification tree's status is the same before and after (one untracked directory that was already there). The bookkeeping worktree holds other sessions' uncommitted files under `30-s1-repair/`; I did not open or touch them.
8. **Seen after the ruling was written.** My closing check for leftover processes listed the command line of another running session (process 77895, not mine, left untouched). It shows that a separate cold addendum, SCI-25G83-CANDIDATE-01-A2, has been charged with the network-time question as it bears on the `dbad7cc7` issuance. I read no output of that session. It changed nothing above; it is the gate to which §6 step 1 refers the matter, and its ruling governs that question.

## 1. Words used

- **Capture**: one 197-second recording of the power sampler while the machine runs 59 commanded one-second GPU load pulses.
- **Frame**: one power sample. The sampler is asked for 100 ms frames and delivers longer ones. **Median frame** of a capture: the middle value of its frame lengths.
- **Estimator**: the code that turns a capture's raw bytes into **B**, the one timing-uncertainty number a capture yields, in seconds. It lives in four files. **Digest**: the sha256 of a file's bytes.
- **Cell**: the estimator decides which pulse-edge timings fit the data by testing rectangles of candidate (start shift, end shift) pairs. It starts from one square 1.5 s on a side, discards a rectangle when the data rule it out, and otherwise halves it, down to 0.1 ms (`joulewise/powermetrics_fiducial.py:657–696`). Each rectangle tested is one cell.
- **Need**: the number of cells a capture uses when nothing stops it.
- **The cap**: the most cells one capture may use, 165,000 today (`powermetrics_fiducial.py:88`). A capture that reaches it is recorded invalid and all its partial work is thrown away (`:992–1010`).
- **Member**: a capture whose B is one of the values a calibration is computed from. **Calibration**: the issued file of limits computed from the members. **Corpus**: the set of members.
- **Pinned file**: one of the four estimator files, whose digest the calibration records. **D-138**: the decision that any change to a pinned file may land only inside one reviewed transaction that also re-issues the calibration (`docs/decision_log.md:10361–10383`).
- **Bracket**: in a measurement window, one workload measurement with a calibration capture before and after it. **Claim-bearing window**: a window whose numbers will be reported as results.
- **The HOLD (H1)**: addendum A1's rule that no claim-bearing window is armed at this epoch until a written ruling closes the cap question.
- **Wall clock / monotonic clock**: the clock that tells the time of day, which the system may correct, and the clock that only counts elapsed time and is never corrected. **Span**: how far the difference between the two moves during one capture.
- **Network time**: the macOS setting that lets the time daemon `timed` correct the wall clock from the internet.

## 2. What I verified by running it

**The cap changes no number.** `consume_cell` counts and may stop; it returns nothing (`powermetrics_fiducial.py:533–550`). Replayed by me:

| Capture | On record | Cap given | Result | Cells | Median frame | Seconds total | µs per cell |
|---|---|---:|---|---:|---:|---:|---:|
| w1-d03 | invalid (cap) | 165,000 | stopped on the cell count | 165,000 | 129.65 ms | 14.4 | 11.11 |
| w1-d03 | invalid (cap) | 5,000,000 | fitted 59 of 59 | 170,965 | 129.65 ms | 14.2 | 10.61 |
| w1-d06 | member | 5,000,000 | fitted 59 of 59, stored B reproduced | 163,849 | 129.76 ms | 13.8 | 10.66 |

About 12.1–12.6 s of each run is spent outside the cell loop. The 120-second deadline clock starts before that fitting (`:976–979`), as the Fable seat said.

**Need does not rise steadily with frame length. This is new; no seat reported it.** The 2026-09-19 captures of this same epoch ran at frames near 245–254 ms. Replayed with the cap lifted:

| Capture | On record | Median frame | Cells |
|---|---|---:|---:|
| n1-d01 | valid | 244.29 ms | 47,383 |
| n1-d02 | invalid | 248.81 ms | 52,897 |
| n2-d12 | valid | 251.63 ms | 44,959 |
| n2-d10 | invalid | 254.26 ms | 48,619 |

So need is about 112,000–137,000 cells near 120 ms (August, from the sweep record), 144,000–171,000 near 128–130 ms, and about 45,000–53,000 near 250 ms. The steepest growth law any seat fitted (need ∝ frame length to the power 7.55) predicts about 20,900,000 cells at 245 ms. The measured value is 47,383. The law is wrong there by a factor of about 440. Frame length is a marker of the machine's state, as the Opus seat inferred; it does not set the work. Why need is lower at 250 ms I did not establish.

**The launch-context table is a table of single frames.** Its columns are "Files", "Intervals", then median, p95 and maximum over 6,155 and 3,510 intervals (registration lines 620–628). The 134.8 ms figure is the 95th percentile of individual frames, not of per-capture medians. Astra is right, and A1 §5.3's example put a single-frame percentile into a line fitted to capture medians.

**The 150 ms figure** is the registration's own stop: "if the median of the per-capture median native frame lengths is above 150 ms, stop" (line 612). It is a stop on a whole window, not on one capture.

**The clock steps are network-time corrections.** My own query of the system log (`/usr/bin/log show`, process `timed`, 00:00–11:30 PDT) returned 70 applied corrections, 18 of them 1 ms or larger, roughly one every 27 minutes. Three fall inside captures:

| Capture | Capture interval (PDT) | Correction in the log | Span on record |
|---|---|---|---:|
| W1-d08 | 01:50:09–01:53:26 | 01:53:09, clock set, +53.198 ms | 52.0 ms |
| W1-d11 | 02:20:09–02:23:26 | 02:20:42, +4.386 ms | 5.8 ms |
| W2-d07 | 10:10:11–10:13:28 | 10:11:29, −35.939 ms | 35.9 ms |

This confirms the Opus and Fable seats and answers the forensic question Sol and Astra posed. *Inference, not established:* the fourth clock exclusion, W1-d01 (no feasible clock fit), started at 00:40:08, sixteen seconds after a −1.262 ms correction at 00:39:52, and the Fable seat's table shows its clock difference moving by −1.26 ms during the capture. A correction being applied gradually during the capture would bend the clock relation and produce exactly that refusal.

**Network time was ON for both windows and nothing checked it.** The W1 chain script contains no mention of network time, `systemsetup` or `timed` (search returned nothing), and neither does the registration. The clock method's own text says the opposite is required: a capture "with network time ON or unknown is validation-only material" (`joulewise/uncertainty_evidence.py:903–909`). A tool to switch it off already exists and needs administrator rights (`scripts/quiet_window_clock.sh:1–27`).

## 3. Ruling 1 — route R, and how the HOLD closes

**Route R.** Route M keeps a cap that stops a third of captures and rests every claim on a comparison with discarded brackets. All four seats reject it and so do I.

**The HOLD (H1) is closed when, and only when, a closing ruling cites each of the following by file path and digest:**

- C1. The sizing rule of §4, committed to the repository with its digest recorded, at a commit earlier than the roster replay of R2.
- C2. The roster replay record and the value it gives; the merged D-138 transaction whose change to `powermetrics_fiducial.py` is that value (and whatever else §6 step 4 admits).
- C3. The acceptance record of R9: at least 24 captures listed with cells, median frame, need ÷ cap and disposition; zero stops; every need ÷ cap at or below 0.5.
- C4. The successor calibration, derived from the fresh corpus of §5, issued and in force.
- C5. The clock record of §7 filed, network time OFF attested for every capture of C3, and zero span refusals among them.
- C6. The record of the three-family audit of §6 steps 5 and 9.
- C7. A rule in the window report that every bracket attempted is listed, abandoned ones included, with its cause.

If any of the seven is missing, the HOLD stands. Windows that carry no claim may run throughout.

## 4. Ruling 2 — the sizing rule

### 4.1 The forcing problem, with numbers

The cap exists for one reason: if a pulse's data cannot rule any timing out, the search never discards anything and must test 2^28 = 268,435,456 smallest rectangles, about 537 million cells counting the intermediate ones. At the measured 10.6 µs per cell that is about 1.6 hours for one pulse of 59. The cap stops that after a fixed, repeatable amount of work (`powermetrics_fiducial.py:77–87`; `tests/test_powermetrics_fiducial.py:641–660`; `docs/decision_log.md:10149–10180`).

August sized the cap upward from the work it had seen: largest need 137,189, plus 20.3 %. A guard placed 20 % above the work becomes a filter on the data the moment the work shifts, and it did.

Every quantity on one scale (cells per capture, each tick ten times the last):

```
 10^4          10^5          10^6          10^7          10^8          10^9
  |-------------|-------------|-------------|-------------|-------------|
         [S]     [A][E]   [T] [N]                            [F]
                   ^O
```

- **S**: need at ≈250 ms frames, 45,000–53,000 (measured, §2).
- **A**: need in August at ≈120 ms frames, 112,205–137,189.
- **E**: need in this epoch at 128–130 ms frames, 144,037–170,965.
- **O**: the old cap, 165,000. It sits inside E.
- **N**: the new cap, ten times the largest need.
- **T**: the tripwire, half of N.
- **F**: one pulse with nothing ruled out, about 5 × 10^8.

The rule puts N where the purpose puts it: far above all healthy work, far below F.

### 4.2 Where the seats disagreed, and what I rule

| Question | Sol | Astra | Opus | Fable seat | Ruling |
|---|---|---|---|---|---|
| Size from | 1.25 × largest need | 2 × largest need | 10 × largest need | time ceiling, or 1 % of one flat pulse | **10 × largest need** |
| Covered range of median frame | 127.5–136 ms | 120–140 ms | up to 150 ms | 100–150 ms | **100–150 ms** |
| Evidence needed at the top of the range | measured counts, 3 per band, before any value | measured counts, 6 per 5 ms band | growth-law check to 150 ms | growth-law check to 150 ms | **neither; see below** |
| Outside the range | hold the whole claim window | refuse claim eligibility | tag, leave out of the test | flag, not a member or bracket | **flag, and hold the whole window** |
| Constant or formula | constant | constant | constant | constant | **constant** |

Reasons.

1. **Size from purpose, not from need plus a margin.** Sol's 1.25 and Astra's 2 repeat August's design with a larger margin. They keep the cap near the work, so they must then prove coverage at every frame length, and both rules wait for captures at frame lengths nobody can command: the sampler's cadence is set by the machine, and no capture on record has a median between 130.2 and 244 ms. Their rules may never complete. The sound part of their position is kept in R7 and R8: claims are limited to a stated range, and need is watched in every window.
2. **No growth-law check.** Opus's step (f) and the Fable seat's step 3 carry a fitted exponent to 150 ms. §2 shows such laws fail by a factor of hundreds outside their data. A1's warning against carrying a fit past its data applies to them as well. They are replaced by a measurement made in every window (R8).
3. **Compute time does not set the value.** The Fable seat's rule takes seconds-per-cell as an input. A1's binding B4 says the rule "uses cell counts and frame lengths only". I keep the value a function of cell counts alone and use time only in a check that can refuse (R5). I read B4's purpose as keeping outcomes out of the sizing; a check that can only say no does not breach it. The owner may overrule that reading.
4. **Constant.** Need is not a function of frame length (§2), so no formula in frame length is justified. A constant changes the fewest bytes.
5. **Factor ten.** It is an engineering reserve, not a statistic. Two checks bound it: the tripwire (low side) and the stop-time check (high side). On today's numbers any factor from about 5 to 25 passes both; ten is chosen here, before the value is computed, and is not to be tuned.
6. **The Opus seat's faster search** (skip rectangles already inside the region found; about one sixth of the work, same B on four captures) is not part of this transaction. It changes the search itself and needs its own review. If it is ever adopted, R12 applies.

### 4.3 The rule, as text to be pre-registered

> **CAP-RULE-25G83-1**
>
> R0. *Words.* A capture's **need** is the number of cells evaluated when it is replayed from its stored raw bytes with the cell limit set to 5,000,000 and the wall deadline to 3,600 s, its clock alignment resolves, and all 59 pulses fit. Its **median frame** is the median of its native frame lengths in milliseconds.
>
> R1. *Code first.* The four estimator files are frozen at recorded digests before any replay under this rule. The frozen bytes are the bytes that will ship, with only the cap constant and its comment left to be set.
>
> R2. *Roster.* A list of captures is written and committed before any replay: all 24 captures of W1 and W2 (2026-09-27); all 24 of n1 and n2 (2026-09-19); every unique protocol-v3 bundle named in `docs/process_traces/2026-08-18-shakedown-first-light/03-budget-calibration-sweep.md`, the shakedown included. Each is replayed once under R0. A capture with no need (alignment unresolved, or fewer than 59 pulses fitted) is listed with its reason and contributes nothing; it is never counted as zero. If any replay reaches 5,000,000 cells or 3,600 s, the rule refuses and the matter returns to council.
>
> R3. *Value.* N_max is the largest need on the roster. **Cap = 10 × N_max, rounded up to the next multiple of 10,000.** It is written into the code as one integer. It is not a function of frame length or of anything else a capture supplies.
>
> R4. *Covered range.* Per-capture median frame from 100 ms to 150 ms inclusive. Within it, need has been measured only in the bands the roster record shows (expected: near 113–121 ms and 127.6–130.2 ms). The rest of the range is covered by the factor of ten and watched by R8, not by measurement. The record says so in those words.
>
> R5. *Stop-time check (can only refuse).* Let t be the largest seconds-per-cell and T the largest time spent outside the cell loop, over all roster replays on the measurement machine. Require T + Cap × t ≤ 60 s, half the wall deadline, so that a runaway stops on the repeatable cell count and not on the clock. If this fails, the rule refuses and returns to council. The value is not lowered automatically.
>
> R6. *Guard tests kept.* The existing test that a flat loss surface stops on the cell count with no B, no fits and reason `detection_nonconvergent` is kept and run at the new value.
>
> R7. *Outside the range.* The estimator runs as usual and the cap applies as usual. A capture whose median frame is below 100 ms or above 150 ms is flagged `frame_out_of_covered_range` in the window report. It is not a member. No bracket is dropped for frame length alone: a window containing such a capture has its claim status held, whole, for a council ruling. Extending the range requires need measured at those frame lengths.
>
> R8. *Tripwire, every window.* Each window report states, for every capture, its cells, its median frame and cells ÷ Cap. If any capture inside the range exceeds 0.5, no further claim-bearing window is armed until council has reviewed the sizing. If any capture inside the range stops on the cap or on the wall deadline, claim-bearing windows halt.
>
> R9. *Acceptance test.* Under the shipped bytes, in windows that carry no claim, registered before they run, in the registered launch context and with network time OFF attested: at least 24 captures in which the cell search ran (a capture refused at clock alignment uses zero cells and does not count). All of: zero stops on the cell count; zero stops on the wall deadline; every cells ÷ Cap at or below 0.5; every median frame reported. The windows are two of 12 declared slots; a third is permitted only if fewer than 24 captures ran the search, and that condition is written in the registration beforehand. The test reads cells, frame lengths and dispositions only, and is made before any B of those windows is read.
>
> R10. *Failure.* A failure of R9 sends the rule back to council. The value is never adjusted between captures or between windows.
>
> R11. *Excluded inputs.* No B value, no statistic or screen computed from B, and no energy value is read in R1–R10.
>
> R12. *Restart.* Any later change to a pinned file that changes how many cells a capture needs restarts this rule from R1.

**What the evidence may be fitted to:** nothing is fitted. The rule's single data-dependent quantity is N_max.

**Worked example, as illustration only.** On counts already printed in the gate ruling, N_max is 170,965, so the rule would give 1,709,650, rounded to 1,710,000. With my slowest measured figures, the stop-time check reads 12.56 s + 1,710,000 × 11.11 µs = 31.6 s, under 60 s. The tripwire would sit at 855,000 cells, five times the largest need on record. The operative value is whatever the roster replay yields under the frozen bytes; I state the illustration because I cannot un-know it.

**What the acceptance test does and does not show** (Astra's point, adopted). Zero stops in 24 captures still allows a true stop rate up to about 12 % at 95 % confidence. The count is a commissioning minimum. The protection that lasts is the margin and the tripwire.

## 5. Ruling 3 — membership

1. **The eight capped captures are never members,** of anything. Their ledger rows are immutable and their diagnostic B values are known. The same holds for the eleven 2026-09-19 values.
2. **Interim re-issue: the same 12, values unchanged.** Inside the cap transaction the calibration is re-issued with the new digests and the identical 12 member values. Reason: D-138 requires the change and a re-issue to land together, and the registration says each derivation capture "is written derivation-only under the active artifact (… estimator-code digest)" (lines 149–150), so new windows need a calibration in force whose pins name the code that runs. *I read that from the text; I did not execute the writer.* Conditions: (a) a replay of all 12 members under the new bytes gives each stored B to the last digit, and a replay of all 24 gives the recorded disposition for every capture except the 8 cap stops; (b) the artifact states that its member list was fixed by dispositions written under the 165,000 cap, which the pinned code would not reproduce for those 8; (c) **it is not claim-eligible**: the HOLD stands under it.
3. **Final: a fresh registered corpus.** Sol and Astra wanted only this; Opus and the Fable seat wanted the interim plus this. All four agree on the reason and so do I: once the cap lifts, brackets come from every machine state, and the 12 are 25 % long-frame against 45 % in the unfiltered set. "No difference in B" (p = 0.44, n = 20) is weak evidence of sameness.
4. **The acceptance captures may also be the successor's corpus,** on four conditions fixed in the successor registration before the first capture: both purposes are declared; the cell-count look of R9 is made before any B is read; every valid resolved capture is retained with no B-based exclusion or top-up; and if R9 fails, the campaign is void and its captures are diagnostics, never members under a different cap. The cap test cannot select on B, because passing it means no capture was removed.
5. The successor registration lists as disclosed design inputs the 12 member values, the 8 diagnostic values, and the three seats that computed them (A1 §6 N-4), plus this ruling's replays, which read no new B.

## 6. Ruling 4 — sequence

1. **Issue `dbad7cc7`** under A1's B1–B4, unchanged. The HOLD stands. One item is referred to that transaction's gate, which I do not rule on: network time was ON during W1 and W2 (§2), and the clock method's text calls such captures validation-only material (`uncertainty_evidence.py:903–909`). Every member passed the clock checks with spans of 0.74–1.54 ms, and what remains unguarded is bounded by the method at 250 µs against B values of 24–38 ms. It bears on whether a number is true, so it must be disclosed and decided there.
2. **File the clock record** (§7) and have network time switched OFF for windows. Read-only work plus one owner action; runs alongside steps 3–5.
3. **Pre-register CAP-RULE-25G83-1** (commit, digest). Only then run the roster replay and compute the value, R5 and R6.
4. **Build one staged branch** under D-138: the cap, plus each waiting estimator branch that passes this test: replay leaves all 12 member B values identical to the last digit and all 24 dispositions unchanged apart from the 8 cap stops. A branch that fails the test changes B; it does not ride, and the council decides before step 7 whether it waits until after the claim windows. I did not review what the four waiting branches change.
5. **Three-family full-system audit** on the frozen staged tree, before any fresh capture, so that a finding cannot make the new corpus stale. Fix, re-freeze, and repeat step 3's replay if a pinned byte moved.
6. **Merge the cap transaction** with the interim re-issue (§5 item 2).
7. **Seal the successor registration;** run two non-claim windows of 12 slots, at least 6 hours apart, network time OFF and attested, no agent session active.
8. **After each window,** the cadence and cell report, then the R9 test, before any B is read.
9. **Terminal session:** derive the successor candidate; cold science gate; issue it (no estimator change, so no new staleness). Then an audit pass limited to what changed since step 5: the new artifact and its pins.
10. **Closing ruling** citing C1–C7. Then claim-bearing windows.

Sol placed the audit after the final issuance; the other three placed it before the captures. Step 5 plus the limited pass in step 9 gives both protections. Cost if nothing fails: two windows on one day, about 2–4 days in all. A failed R9, a failed audit or a missing owner action adds to that; I give no date.

## 7. Ruling 5 — clock steps (H4)

**The 5 ms span limit stands** (`uncertainty_evidence.py:40`, applied at `:1110–1126`). The method assumes one clock rate and no step within a capture (`:891–894`). Left alone the clock drifts 4–8 parts per million, which is 0.7–1.5 ms over 197 s, so 5 ms leaves a threefold margin for a healthy clock and refuses every correction large enough to matter. The three refused captures were refused correctly. The looser limit in the code (15 ms, `:74–81`) belongs to a different method for a different consumer and is not adopted.

**Required before claim-bearing windows:**

- K1. A filed record with the log extract for 2026-09-27 00:00–11:30, its digest, the table of §2, and the W1-d01 question answered from the capture's stored clock readings. System logs expire; my extract is at `/tmp/cg-cap-d528efb2/timed-mine.txt` and should be copied into the record promptly.
- K2. Network time OFF for the whole of every window, switched before the settle period and restored afterwards, and attested per capture from the `timed` log. The arm path must refuse to arm without it.
- K3. In the captures of R9: zero span refusals, and no applied correction of 250 µs or more inside any capture interval. One failure returns H4 to council.
- K4. Every abandoned bracket recorded by cause.

The Fable seat's point that these losses follow a timer and not machine load is a reasonable inference and lowers the concern; K2 removes the cause either way.

## 8. Ruling 6 — what this needs from Ed

1. **An administrator action.** Network time OFF for windows: either run `scripts/quiet_window_clock.sh disable` before each window and `enable` after, or install a passwordless helper so the chain can. Nothing in step 7 can run without it.
2. **Approval of the successor registration** before it is sealed: the dual-purpose windows, the network-time condition, the disclosed design inputs. The sealed Revision 5 text itself is not edited by anything here.
3. **Identity of two acceptance artifacts:** the interim same-12 re-issue, and the successor.
4. **A word on the audit:** whether the full audit at step 5 plus the limited pass at step 9 meets directive #416. I have not read the directive.
5. **Optional.** Ed may overrule my reading of B4 (§4.2 item 3), the factor of ten, or the interim re-issue.

Nothing here publishes anything.

## 9. Left unchecked, stated plainly

- NOT EXECUTED: replay of the August corpus and the shakedown; their frame lengths; the Opus seat's figure of 124,029 cells at 113 ms.
- NOT EXECUTED: replay of the other 20 captures of 2026-09-19. I ran 4 of 24.
- NOT EXECUTED: the Opus seat's faster-search probe.
- NOT EXECUTED: any review of the four waiting estimator branches.
- NOT EXECUTED: the capture writer's check of the estimator digest against the artifact in force (§5 item 2 rests on the registration's words).
- NOT EXECUTED: reading directive #416.
- NOT ESTABLISHED: why need is lower at 250 ms frames; whether W1-d01's refusal was a network-time correction; the current network-time setting (the query needs administrator rights).
- NOT ESTABLISHABLE from stored captures: whether workload energy depends on frame length. Route R removes the filter; it does not measure that.

## Summary for the owner

1. Route R: the cap becomes one constant, ten times the largest work ever measured, fixed by a rule written before the value is computed; I measured that work does not rise steadily with frame length (it falls to a third at 250 ms), so no formula and no extrapolation is used, and every window reports how close it came.
2. The calibration is re-issued twice: first the same 12 values under the new code, not usable for claims, then a fresh corpus from two new non-claim windows that also prove the cap stops nothing; the hold lifts only when all seven listed conditions are cited in a closing ruling.
3. The three clock-step losses are macOS network-time corrections, which arrive about every 27 minutes (a fourth loss probably is too, unproven); the 5 ms limit stays, and I need you to switch network time off for windows (administrator rights), approve the successor registration, and name the two artifacts.
