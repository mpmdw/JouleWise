# Opus 5.5 cross-review: Sol reviewer-2 seats 1 and 2

2026-11-07. Reviewer: Opus 5.5. Inputs:
`align/2026-11-07-sol-reviewer2-seat1@b9535bbfc` (R1s) and `-seat2@d337f4633` (R2s).
Each seat role-plays three hostile reviewers: AI control/ML, security, and
statistics. Checked against protocol and code at `e901eb2a4`, the public
explainer and AGENDA on main `6f0bfd2d6`, the decision log and the imported
calibration script `7fbd95e31`. I recomputed every planning bound with my own
arithmetic. Marks: **AGREE**, **DISAGREE** or **UNVERIFIABLE**, each with a
one-line reason.

## Verdict

The two seats converge closely, at roughly 90 % overlap. Both say a favorable
v4 plus red team supports a **bounded, local, joint-audit** paper, not a
universal squeeze. Both name the same fatal sentence: "evading one channel
forces exposure to the other". Both also name the same three cheap fixes
before collection:
- the threat game and trust boundary;
- a successful-joint-evasion endpoint over all assigned attempts;
- one frozen joint-FPR construction on a clean split.

Their objections are well grounded in the repo. Two things are weak:
- **Proportionality.** Both recommend a third task pair, a second model and a
  second-unit replication as P1. That is months of Mac time and should be
  deferred behind the core.
- **Schedule.** Neither checks venue timing against the collection budget (see
  "What both missed", #1).

## Claim checks

| # | Claim (seat) | Mark | Reason |
|---|---|---|---|
| 1 | Within-forward-pass blindness means ordinary-token sabotage is a shared blind spot; the squeeze is a hypothesis (R1s C1, R2s S3) | AGREE | `PIPELINE.md:20`; `energy_residual.md:388-400`. This is the paper's most attackable sentence |
| 2 | Detecting harness-injected work is not control; the primary endpoint is P(S ∧ U ∧ ¬M ∧ ¬E) over all assigned attempts, plus the S-conditional version (R1s C2, R2s M1) | AGREE | Same estimand as the design seats D1/D2 (see the squeeze-design review). The P1/P2 injected-workload primary fails this objection |
| 3 | Audit vs prevention: an episode-end alarm after a transfer is not prevention (R1s C2, R2s M1) | AGREE | Correct, and cheap to fix in wording. Claim "audit" unless a hold/rollback exists |
| 4 | Monitor renderer hides tool arguments in every view; `no_scratchpad` strips closed scratchpads (R2s S3) | AGREE | `monitor.py` `render_transcript`: "arguments remain hidden in every visibility" |
| 5 | Explainer says a USB-C DC meter is at the charger cable on every episode, while v4 analysis reads `powermetrics:gpu_power` and the setup is direct MagSafe (R1s S1, R2s S2) | AGREE | `energy-tripwire.html` step 03 vs `pilot_analysis.py` (`'powermetrics:gpu_power'`) and `pilot_protocol_v4.md:699`. A real public inconsistency; fix the explainer or the setup before registration |
| 6 | D-139 A1, "no in-process adversarial programs are assumed", conflicts with a red team on the measurement host (R2s S1) | AGREE (needs scope line) | `decision_log.md` D-139 A1 is **Ed's** ruling ("family-wide"). Only Ed can scope it out for ALIGN, not the lead. R1s missed it |
| 7 | v4 uses per-session LOTO for benign and a full fit for sabotage, so the conformal bound needs a clean split or a proof (R1s T1, R2s T1) | AGREE | `pilot_protocol_v4.md:488-505`; `pilot_analysis.py:228-235` asymmetric maps |
| 8 | Imported calibration uses k=ceil(.95(m+1)), rank 38 at m=39 (5 %), while the explainer says max (2.5 %) (R2s T2; R1s T1 same point) | AGREE | `align_pilot_calibration.py@7fbd95e31`: "ceil(19*(m+1)/20)"; explainer step 05 "largest residual ... 2.5 % at m ≥ 39" |
| 9 | Realized-tail bounds: 1−.1^(1/m) = 10.87 % at m=20, 5.73 % at m=39; 7.39 % at 95 % (both) | AGREE | Recomputed |
| 10 | 0/59 independent benign tests give a 4.95 % one-sided 95 % upper bound (both) | AGREE | 1−.05^(1/59) = .0495 |
| 11 | 3/3 detected gives a lower bound of only 36.8 %; 29/29 > 90 % (R1s T2) | AGREE | .05^(1/3) = .368; .05^(1/29) = .902 |
| 12 | 29 successful sabotages per pair need ≥29 default D windows at 1 sabotage/pair/window (R1s T2) | AGREE | `pilot_protocol_v4.md:141-143`. An attack-heavy roster must be a new addendum, as both say |
| 13 | Six families × 2 pairs × 59 = 708 zero-escape trials for per-family 5 % bounds (R2s cost discipline) | AGREE | Arithmetic is right. Its conclusion (mixture-average primary, families descriptive) matches the squeeze-design review's #14 |
| 14 | OR of two 5 % alarms can reach 10 %; use .025/.025 or a jointly calibrated statistic (both) | AGREE | Union bound. Matches all four design drafts |
| 15 | Two pairs, one production model and one laptop limit the claim; model size ≠ attacker competence (R1s C3/C4, R2s M2/M3) | AGREE | `pilot_protocol_v4.md:56-74`; CHAIR:315-317 already limits to capped episodes |
| 16 | Add a third task pair, a second model and a second-unit replication as P1 (R1s A10/A11, R2s M2/M3/S4) | DISAGREE (priority) | Each is several windows plus fresh calibration (R2s itself prices 39+12 members ≈ 25.5 member-hours for one pair). Under proportionate care, defer all three until the core joint result exists, and narrow the abstract instead. Both seats allow this as the fallback |
| 17 | Eligibility exclusions (X1-X8) may remove the best attacks; keep an all-assigned funnel (R1s S2, R2s T4) | AGREE | `pilot_protocol_v4.md:454-470`. Cheap and essential |
| 18 | Datacenter/batching is a different identification problem; claim a dedicated local host (R1s S3, R2s S4) | AGREE | v4:508-522 reference-state energy; CHAIR:315-316 |
| 19 | Trusted elapsed time must be a baseline; if time + monitor matches energy + monitor, energy's value is unproven (R1s S4/A9, R2s M1) | AGREE (important) | This is the sharpest novelty threat after #1. Time is free and attacker-visible, so it must be a registered primary comparator, not a P1 baseline |
| 20 | Novelty neighbors: CoIn/PALACE, Gargiulo & Kulp, Kimpson-Baker-Graham, energy regressions plus SHADE monitors (both) | UNVERIFIABLE | Taken from the literature audit `16e1db623`; neither seat (nor this review) checked primary sources. The positioning advice ("no 'first physical monitor'") is right regardless |
| 21 | Venue ranking: R1s puts ICML 2027 first; R2s puts USENIX Security / NeurIPS 2027 first; all dates unverified offline (both) | UNVERIFIABLE / see missed #1 | Both honestly mark the dates unverified. R1s's ICML-first is unrealistic given the budget |
| 22 | Close the existing W1 pre-arm findings at one pinned head, not a new council (R1s A8, R2s T5) | AGREE | Matches the v4-registration seats. Item 209 adds the #694 delta review |

## Where the two seats agree

#1-#5, #7-#11, #14-#15, #17-#22: same claim ceiling, same endpoint, same
trust-boundary demand, the same statistics corrections and the same novelty
discipline. Their unique contributions:
- **R2s:** D-139 (#6); the 708-trial cost of per-family claims (#13); a
  concrete 36-attempt screening design.
- **R1s:** fragmentation/low-and-slow across episodes, campaign vs episode
  detection; the 29-window arithmetic (#12).

Cross-family agreement: k=3 (R1s, R2s, Opus) on everything except #16 and #21.

## What both missed

1. **Schedule vs collection budget.** This review's unverified training
   knowledge suggests these approximate cycles; Ed or the lead must confirm
   them before planning:
   - already past or imminent: ICLR 2027, SaTML 2027 and the last S&P 2027 cycle;
   - about late January 2027: ICML 2027, CCS 2027 cycle A and USENIX Security
     '27 cycle 2;
   - about mid-May 2027: NeurIPS 2027.

   R0 has not yet passed (item 209: re-run 11 pending after ~10 refusals).
   R1, W1, D1-D6 and a 37-45-window squeeze cohort follow at one 16.5 h window
   per day at best. So January venues can carry at most v4 plus a limits or
   positive-control result, not the confirmatory squeeze. **NeurIPS 2027, or a
   spring security cycle, is the first realistic main-track target for the full
   claim.** This should drive which half of the design is collected first.
2. **Monitor strength as a reviewer objection.** R2s comes close ("compare
   with spending the same resources on a stronger transcript monitor"), but
   neither demands it. A 20-30B local monitor will be called a strawman, and
   energy's incremental gain over a weak monitor overstates its value. A
   frontier-monitor co-primary on the same frozen views is cheap (off-box,
   needs Ed's OK for API use) and removes the objection.
3. **Gating realism.** Both mention reference-state energy only in the
   datacenter context. A control reviewer will also ask whether the G0/G1/hold
   gating that makes the residual clean is acceptable in a local deployment
   (latency cost per turn). Report the measured gating latency overhead as part
   of the cost account, or run an ungated sensitivity arm.
4. **Who owns which fix.** Several "required changes" need Ed, not the lead:
   - D-139 (#6);
   - the KM003C/power path (#5);
   - API monitor use;
   - publishing the explainer correction.

   Route them to Ed as one batched packet rather than letting them surface one
   at a time.

## Recommended merge for the agreement job

- **Adopt now, before collection:** R1s A1-A9 and R2s P0 rows.
- **Add:** trusted-time + monitor as a registered primary comparator (#19), the
  frontier-monitor co-primary (missed #2), and the D-139 scope line from Ed (#6).
- **Defer:** third pair, second model and second-unit replication (#16).
- **Fix now:** the public explainer's DC-meter and max-rank statements (#5, #8),
  since they are already published claims.
- **Pick the venue from the schedule arithmetic** (missed #1): NeurIPS 2027 for
  the full squeeze, with a January-cycle submission only for a v4 + limits paper
  if one is ready.
