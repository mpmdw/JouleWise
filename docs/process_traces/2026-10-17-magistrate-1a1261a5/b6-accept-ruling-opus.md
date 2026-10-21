claude-opus-5-5

# Cold-gate ruling: block 6 registration, the quiet-machine values (2026-10-17)

Judge: Opus 5.5, cold, single session. Inputs: the registration draft at `df8373292` (fill = `git diff 63c388776
df8373292`), the acceptance commit `5ffbe15c4`, both derivations, the kit's raw data under
`/Users/edr/night-archive/threshold-validation/`, and the non-claim rehearsals under
`/Users/edr/night-archive/gate-prune/rehearsal-real/`. Nothing restricted by the block-5 brief §6 was opened.
Every script I ran is under `/private/tmp/opus-gate/` (listed at the end).

## Verdicts per slot

| Slot | Verdict | Value that governs |
|---|---|---|
| S-4 (fresh acceptance) | **REGISTER** | `configs/b6/registration/acceptance.json` at `5ffbe15c4`, SHA-256 `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8`; alignment reference 0.037054941476587 s; s_bracket 0.010818 s; drift budget 0.01550217418713139 s; corpus n = 13 |
| S-6 (M2's d) | **REGISTER-WITH-CHANGE** | d = +0.180 J (prefill), disclose-only. Change to the text only: describe the arms as measured (see ruling c) |
| S-7 r (M3) | **REGISTER** | r = −4.670 × 10⁻⁷ ppm (SE 5.19 × 10⁻⁷) |
| S-7 T_stream_max | **REGISTER** (interim, as the draft words it) | 335 s, carried from block 5, labelled not measured; replaced before round 1 by the machine test's longest run-level stamp span if that span is longer. Hold 14.675 ppm |
| S-8 w (M4) | **REGISTER-WITH-CHANGE** | w = 5.432 J per CPU-s is registered as the measured worst-case conversion. `contention.request_overlap` **stays a recorded flag and governs**. The registered exclusion is printed beside every cell as a labelled sensitivity (ruling a) |
| c_q | **REGISTER-WITH-CHANGE** | **c_q = 0.54 CPU-s per interval**, replacing 0.73 (ruling b) |
| S-12 (M14 cross-check) | **REGISTER** | printed as the draft has it; it excludes nothing. I did not re-derive M14 (NOT EXECUTED here). Sol reproduced it from raw data |
| S-5, S-9, S-11 | **HOLD** | each pack's non-claim smoke (target-phase lengths, 2,048-token prefill) is missing; both seats agree |
| S-10 (F_min) | not before me | every line below is computed at the proposed 1.9 J (F_min/4 = 0.475 J) |

Two actions are due before round 1. Neither is a hold on any slot.
1. Kill the orphaned `hazard_monitor.py`, pid 43816. At 2026-10-17 it was still alive (`ps`: parent 1, started
   Thu Oct 15 09:41:21, 11:20.66 of CPU, running from `JouleWise-wt-b6-s3cold-fix`). Confirm that the pre-session
   census would catch a leaked test process like this one.
2. The machine test on the pin reports the longest run-level stamp span (S-7).

## Rulings on the questions

**a. S-8: flag only, with the registered exclusion printed beside it.** The registered line sits at 0.0874 CPU-s
of excess, about a fifth of the bottom decile (0.41 CPU-s) of the quiet machine's own 10 s outside totals (10th to
90th percentile 0.41 to 1.60 CPU-s). It therefore fires on the noise of C, not on contamination. Replayed, it
removes 12 of 53 quiet 10-09 runs (36 of 77 rehearsal runs). The same 25 reference runs show no measurable energy
per outside CPU-second: the slope is +0.0057 ± 0.0083 J per CPU-s on decode and −0.0006 ± 0.014 on prefill. §8.7
item 1 then requires a resize or a flag, and no measured conversion exists to resize it with. The background-priority
w (0.0862) is rejected for two reasons. It is not an upper bound for interactive outside work, which costs 63 times
more (5.43 against 0.086 J per CPU-s). It also still removes the 2 known-good 10-09 references at about 20 CPU-s,
whose energies sit within one standard deviation of the other 23. So the alternative fails §8.7 item 1 too.

What governs: `contention.request_overlap` stays DISCLOSE, as the catalog already has it. Beside every cell the
analysis prints a labelled "registered outside-processor rule (w = 5.432, c_q = 0.54)" result with its exclusion
count; that is 38 of 77 rehearsal runs and 14 of 53 quiet ones at these values. The analysis does this from the
monitor's contention journal (per run: C, k, C − k × c_q and E_add at w = 5.432). Nothing computes E_add today, so
this code is owed before the analysis release (S-14), not before round 1: the journals are collected whatever the
disposition. An exclusion may come back only before round 1, and only with a conversion measured for the work that
actually runs (for example an in-situ fit on quiet-machine reference runs) that removes 0 known-good runs on replay.

**b. c_q = 0.54, without Spotify and the orphan.** c_q is the machine's own background. A user program running in a
window is outside work that the flag exists to show; folding it into c_q would hide it. The orphan is a defect, to be
killed (action 1). The kit's quiet machine without them gives 0.54, and the 10-09 rehearsal, whose journals list
Spotify in 0 of 852 intervals, gave 0.52. These two agree, and that agreement is the check that 0.54 is the quiet
machine. Joule size: the 0.18 CPU-s difference from 0.72 is 0.98 J per interval at w = 5.432 and 0.016 J at 0.0862.
Under the governing flag it moves no run; it moves the printed sensitivity from 36 to 38 of 77.

**c. M2 qualifies S-6. The proportional carry is not the rule's reading.** The two arms were measured by the same
path in alternated N L L N quads. Both the fallback timeline and the capped waits therefore act on both arms, and
the paired quad differences carry whatever random placement error the fallback adds (SE 0.068 J). Block-6 waited runs
are runs delayed by disturbances, up to a 1,500 s cap. The L arm (2,700 s with intermittent outside work) is the
nearest measured analogue of such a run, so the capped waits do not disqualify it; they are disclosed. The
registered rule reads d in joules on the reference workload. A proportional carry assumes a transfer mechanism that
nobody has measured, and its own interval includes zero: 26.1 J × (−0.10% to +4.81%) = −0.03 to +1.25 J, point
0.61 J. No physical hazard of 0.475 J on the 1.7B prefill is shown. `idle.waited` stays disclosed, and the with- and
without-waited-runs cells (§9.5 item 8) are the guard. No re-measurement is required before round 1.

**d. Keep T_stream_max = 335 s until the machine test reports run-level spans.** At the measured r the hold stays
far from triggering for any T below 5 ms / 0.25 ppm = 20,000 s. A run's numbers are protected by its own 5 ms clock
bound (§8.3), not by the hold, which only spares a doomed session. Sol is right that 2,292.6 s is the M10 sampler's
stream and the wrong quantity. Sol is also right that the value matters if r returns to block 5's 2.72 ppm: the hold
would then be 1.93 ppm at 2,292.6 s. That is why the machine-test span must replace 335 s if it is longer. It does not
justify a HOLD now, because the pre-check measures r at every session.

**e. The S-4 corpus is adequate.** The number that enters b_op is s_bracket, and it is set by the D-125 floor
(10.818 ms), not by this corpus (range 9.675 ms). The alignment reference and the drift budget only flag. Sized:
- A 24-capture corpus with this standard deviation (2.808 ms) would have an expected range of 3.895 × 2.808 =
  10.94 ms, 0.12 ms above the floor: 0.006 J at 0.047 J/ms.
- If day-to-day variation raised the standard deviation to block 5's 3.80 ms, a 13-capture range would be about
  3.336 × 3.80 = 12.7 ms: 1.9 ms, or 0.09 J of floor.
Both effects are well inside the ~1 J attribution limit, and n = 13 meets block 5's issuance minimum of 12.
Disclose that the corpus came from one job. The corpus-doubling and range-expansion flags cover later drift.

**Writer's Q4** is answered under c. **Sol's question on M4's literal maximum** is answered under "Where the seats
disagree" below.

## Re-derived numbers (from raw data, with the command)

Python: `/opt/homebrew/bin/python3.13 -B -I` (or `-B` with `TMPDIR=$(mktemp -d /private/tmp/accept.XXXX)
JW_B5_SYNTHETIC_ONLY=1` where repository code was imported).

**S-4.** `s4.py` reads each capture's `b_fiducial_s` from `instrument_evidence.json`, selects `condition == quiet`
from M1's and M13's `collection.json`, and imports block 5's issuer
(`scripts/issue_calibration_acceptance_generation.py`: `student_t_quantile`, `two_draw_prediction_lexeme`):
```
n 13  max 0.037054941476587284  min 0.027380174613889405  align 0.037054941476587  range_q 0.009675  S 0.010818
mean 0.030721483979622774  sd 0.002808268859283743  sw 0.002917865816168467  (K = 2: M1, M13)
Q99 0.012131079260684415  Q99w 0.01281606527393005  budget 0.01550217418713139  own-only 0.01281606527393005
```
`refit.py` runs `joulewise.b6.calibration.read_own_capture` (from `/Users/edr/code/JouleWise-wt-b6-accept`) on all
21 captures. All 13 quiet captures are `valid`, with refit equal to the stored lexeme, clock anchor `bounded` and
59/59 pulses. Utility captures 008 and 016 are `refit_failed`. The acceptance file is exact:
`git -C /Users/edr/code/JouleWise show 5ffbe15c4:configs/b6/registration/acceptance.json | shasum -a 256` →
`ea130c87…539ce2a8`, and its corpus equals the 13 lexemes above. These are exact equalities from identical code on
identical inputs.

**S-6.** `m2d.py` reads `summary_metrics.json` `phase_energy_j` of each of the 20 M2 bundles, with arm and quad
taken from `run_table`:
```
prefill  meanL 7.845990 meanN 7.665669  d +0.18032104414320038  quad diffs [0.1159, 0.2147, 0.1198, 0.4241, 0.0271]
         se 0.067779  95% CI -0.0079 .. +0.3685 (t(0.975,4) = 2.7764)  +2.352%
decode   d +0.008900552142616647  CI -0.1561 .. +0.1739
request (energy_request_j)  d +0.19506  CI -0.1043 .. +0.4945
```
All 20 bundles have `clock_anchor.status = unknown` and `detail = clock_fit_span_insufficient`. The N arm's delivered
idle baselines were 74.94 to 75.16 s.

**S-7 r.** `m3.py` fits (REALTIME − MONOTONIC_RAW) against MONOTONIC_RAW by exact-fraction OLS over `clock-end.jsonl`:
```
n 5147  span 51513.958735646 s  one boot ea2d3ec8-…  kernel frequency correction 0.0 ppm
rate -4.670018146614963e-07 ppm  se 5.185665516238618e-07 ppm  max |resid| 0.028142580959178938 ms
```
Exact match to `result.json` (identical inputs, exact arithmetic).

**S-8 w.** `m4.py` parses `rails/powermetrics.plist` (9,642 samples; time = the anchor's
`first_sample_end_point_epoch_s` plus the cumulative `elapsed_ns`; power = cpu + gpu + ane) and uses the segment
times and load reports in `collection.json`.
- Steady arms: w = (load-segment mean − mean of the two bracketing idle means) / `true_cpu_s_per_s`.
- Bursts: excess energy over [on − 0.5 s, off + 1.0 s] above the bracketing idle level, divided by the load's
  `cpu_seconds`.

```
arms: bg 5% 0.951 | bg 20% 1.722 | bg 100% 0.0852 | int 5% 18.33 | int 20% 1.464 | int 100% 4.960   (J per CPU-s)
kit:  1.287±2.303 | 2.025±1.469  | 0.0862±0.0106  | 19.33±3.66  | 1.504±0.292 | 4.969±0.015      (all within 1 SE)
int 5% arm: load 0.0052 CPU-s/s, step 0.095 W; the kit records outside CPU +0.154 CPU-s/s (mediaanalysisd)
bursts clipped to the segment: 4.32 .. 5.46; largest s033 3.5935 J / 0.658697 CPU-s = 5.4555 (kit 5.4320, 0.4%)
bursts with the full window: 4.32 .. 6.37 (placement-0 bursts s013, s023, s033, s043 gain 0.47 to 0.79 J)
```
The kit integrates only samples inside segments (`analysis.py` lines 160 to 175). For a placement-0 burst the window
reaches about 0.37 s back into the inter-segment gap, where the kit takes its boundary `ps` snapshot. That gap holds
the extra 0.47 to 0.79 J. The kit's segment-only value is the right one to register as "largest burst", 5.432.
Under the governing flag the choice changes no run: replays at w = 4.96, 5.432 and 19.33 all give 36/77.

**c_q.**
- `cq2raw.py` rebuilds CPU-seconds per interval from consecutive raw `ps/boundary-*.json` snapshot pairs 9 to 11 s
  apart. It counts every process except the kit's tree (descendants of root 86445), pid 0 and `kernel_task` (no
  snapshot lists one); processes are matched by pid and start identity.
- `cq3raw.py` reads M2's `long-wait.jsonl` interval records (`outside_total_cpu_s_per_s × elapsed_s`, 9 to 11 s).

```
M4 0.775 (n 122) | M5 0.72 (98) | M10 0.555 (228) | M14 0.765 (126) | M2 long waits 0.72 (2,391)
pooled n 2,965: median 0.72 CPU-s per interval;  without Spotify, Spotify Helper, pid 43816: 0.54
(per 10 s normalised instead of per interval: M2 0.709; the registered C is per interval, so 0.72)
```

**Replay.** `replay.py` takes the request times [ss, se] from the 10-15 council table
`/private/tmp/claude-501/silly-council-opus/runs.json` and the monitor `contention.jsonl` interval records. Per run,
C = Σ over the overlapping intervals of `outside_total × elapsed`, minus the listed agent processes; k is the
number of those intervals.
```
w 5.432 c_q 0.73: 10-09 12/53, alpha-1 13/13, gamma-2 11/11, all 36/77
w 5.432 c_q 0.72: 12/53, 36/77       w 5.432 c_q 0.54: 14/53, 38/77     w 4.96 c_q 0.72: 36/77
w 0.0862 c_q 0.72 or 0.54: 2/53, 4/13, 8/11, 14/77                     w 19.333: 36/77     w 0.172: 20/77
largest 10-09 C: refcorpus r01 20.23 (k 2), r03 20.18 (k 1), prefill b08-b2 4.07, decode b01-b1 2.60
```
**In-situ effect.** On the 25 10-09 references, r01 and r03 against the other 23:
- prefill 11.109 and 11.440 J against 11.262 ± 0.382 J;
- decode 25.704 and 25.576 J against 25.497 ± 0.224 J;
- OLS slope of phase energy on C: prefill −0.0006 ± 0.0141, decode +0.0057 ± 0.0083 J per outside CPU-s.

**S-5 stop line.** Unchanged at 139 ms. With the new s_bracket the opening-capture stop is at b_pre > 128.182 ms.
Writer's replay: 0 of 4 rehearsal sessions stopped. I did not re-run the rehearsal b_op table (NOT EXECUTED); the
arithmetic 0.25 × 26.1 / 0.047 = 138.83 ms is the draft's.

## Where the seats disagree

- **c_q 0.73 against 0.72: Sol is right on the population. Both are superseded by ruling b (0.54).** The writer
  pooled only the intervals stored in result files (M2's 2,391 and M4's 86, median 0.765). That omits M5, M10 and
  M14 and over-weights M4's load-time intervals. The registered definition is the median over the quiet-machine
  measurement sessions. M2's idle waits alone give 0.72, and the full pool (2,965 intervals) gives 0.72. The 0.01
  difference is 0.054 J per interval at w = 5.432 and moves 0 runs in the replay.
- **T_stream_max: the writer's disposition is right; Sol's diagnosis is right.** 335 s is not measured and must be
  labelled so (the draft does this). But no decision at the measured r depends on it below 20,000 s, so "undetermined"
  does not warrant a HOLD (ruling d).
- **19.33 against 5.432: 5.432 is right.** The registered conversion is "the largest over M4's burst placements and
  priorities", and s007 is a steady arm, not a burst. Physics also refuses 19.33 as a conversion. In that arm the
  outside CPU rose by 0.154 CPU-s/s, 30 times the load's 0.0052 CPU-s/s, so the power step belongs to
  `mediaanalysisd`, not to the load; charged to all the CPU present, it is 0.63. M14 confirms the scale
  independently: one full core reads 5.21 to 5.42 W on the rails, against 4.96 to 5.43 predicted by the clean burst
  values and 19.3 W by s007. The dispute changes no count (36/77 either way).

## What either seat got wrong

Writer (registration seat):
1. c_q = 0.73 used the wrong interval population (above). The "without user programs" figure 0.55 is close to the
   pooled 0.54 but came from M2 and M4 only.
2. It offered the background-priority w as the alternative without saying that it too removes 2 known-good quiet runs
   and so fails §8.7 item 1. It is also not an upper bound for interactive outside work.
3. The S-6 text calls the N arm "the ordinary 85 s". The N arm's delivered idle baselines were 74.94 to 75.16 s, and
   the L arm was 2,700 s with 8 of 10 waits lacking 20 continuous quiet minutes. The change for S-6: state the arms
   as measured, in §8.5 and §14.
4. "+0.193 J over the whole request" is the difference of the sums of phase means. The bundles' `energy_request_j`
   gives +0.195 J. Label which quantity is printed.

Sol (blind seat):
1. It called s007's 19.33 the "literal maximum" of the registered rule. s007 is not a burst placement, and the arm is
   contaminated (above).
2. It recommended repeating M2 and leaving T_stream_max open. Neither is needed to register: d's use is guarded by
   the with/without printing, and T_stream_max changes no decision at the measured r (rulings c and d).
3. Daemon-fit replay at w = 0.172: Sol 21/77, mine 20/77. The difference is in agent-process removal. It is not
   material, since that w is a diagnostic only.

Both seats derived S-4, d, r and the M4 burst values correctly. My raw re-derivations agree with both: exactly where
the code and inputs are identical (S-4, r, d), and within the kit's own standard errors for M4's arms. Sol's read of
block 5's `hazards/arm.json` is permitted by the brief §6 (named on its list).

## Required text changes (registration draft)

- §8.3 item 3, §8.5 table and derivation, §8.6 S-8 row, §14 S-8 row, D27:
  - c_q = 0.54 CPU-s per interval (pooled kit median without Spotify, Spotify Helper and the orphan; the 10-09
    value was 0.52);
  - `contention.request_overlap` governs as a recorded flag;
  - the registered rule (w = 5.432, line 0.0874 CPU-s) is printed beside each cell as a labelled sensitivity,
    replay 14/53 and 38/77;
  - reason: the line lies inside the quiet machine's own scatter of C, and §8.7 item 1 applies;
  - the analysis computes E_add from the journals before the release.
- §8.5 waiting row and the S-6 rows: the arms as measured (writer error 3). The registered reading of d is in joules;
  the proportional carry is not adopted.
- D25: add the sizing of e (0.006 J from sample size; 0.09 J if the spread grows to block 5's).
- Pre-round-1 list: kill pid 43816; machine-test spans for S-7.

## What I ran

All foreground, in this session. Scripts are under `/private/tmp/opus-gate/`.
- `git diff 63c388776 df8373292`; read both derivations, TASK.md, the draft's §8.1 to §8.7, and the block-5 brief §6.
- `s4.py` (S-4 arithmetic through block 5's issuer functions); `refit.py` (`read_own_capture` on 21 captures).
- `git show 5ffbe15c4:…acceptance.json | shasum -a 256`.
- `m2d.py` (d from the 20 bundles' summary metrics, plus anchor status).
- `m3.py` (exact OLS on 5,147 clock readings).
- `m4.py` (arms and bursts from the raw rail plist, full and segment-clipped windows); read the kit's
  `joulewise/quiet_kit/analysis.py` M4 code at `1c1bc3204`.
- `cq2raw.py`, `cq3raw.py` and a pooled run (c_q from raw ps pairs and M2's interval records).
- `replay.py` (outside-processor rule over 77 rehearsal runs at nine (w, c_q) pairs); in-situ slope on 25 references.
- `ps -p 43816`; a Spotify count in the 10-09 journal.

NOT EXECUTED:
- M14, M5, M9, M10, M13 and M15 re-derivations;
- the rehearsal b_op table through `calibration.evaluate`;
- the unit-test suites;
- any block-5 replay (S-16, blinded).
