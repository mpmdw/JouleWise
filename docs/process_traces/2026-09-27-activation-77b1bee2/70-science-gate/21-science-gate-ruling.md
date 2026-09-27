VERDICT: PROCEED TO ISSUANCE

# Cold science gate SCI-25G83-CANDIDATE-01 — ruling

Judge: cold Fable 5.1 seat, one foreground session, 2026-09-27 16:34–16:53 PDT (19 of the 45 budgeted minutes).
Candidate: `candidate_acceptance_25g83.json`, sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2` (verified on both copies).
Scope of the verdict: the candidate may go to the D-138 issuing transaction, which has its own gate. The verdict is conditional on nothing, but it carries six mandatory disclosures (§7). Two facts in this ruling were in neither the packet nor the re-derivation report: the true causes of the 12 exclusions (§2).

## 0. Contamination disclosure

1. **Preloaded context I did not choose.** The session harness injected, before my first action, the owner's global instruction file, the project instruction file of the judge worktree, and the one-line index of the memory store. I opened none of those files and none of `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, memory files or skill files. The injected index contains owner directives and one status line ("W2 admitted; issuance blocked on custody repair; refuter running"). It contains no B value, statistic, screen or comparison. I treated it as background and took no instruction from it.
2. **Same model family as the lead.** I am Fable 5.1. The lead's final pass is also Fable. I did not sit on the capture, the harvest, the custody repair or the prepare run.
3. **Values I read.** The 12 member B values (in the candidate). The eleven 2026-09-19 diagnostic values (printed in the sealed registration). And eight B values that no one had computed before: see item 4.
4. **Diagnostic values I created.** To test whether an exclusion selected on outcome, I re-ran the pinned estimator in scratch on the raw bytes of all 24 captures with the compute cap lifted. That produced B values for the 8 captures the cap had excluded. They are diagnostics. They are never members, and from now on they are *disclosed design inputs* for any successor registration. They are listed in §2.3.
5. **No file modified.** Every command ran in the foreground with `/opt/homebrew/bin/python3 -B`. The run checkout is clean after my session (`git status` empty, no new `__pycache__`). Scratch is `/tmp/cg-sci-77b1bee2/` (`rederive.py` sha256 `0c8f837b…`, `w1.jsonl` `a62f7d18…`, `w2.jsonl` `336a820e…`).

## 1. Words used

- **Capture**: one 197 s recording of the power sampler while the machine runs 59 commanded one-second GPU load pulses.
- **B** (`b_fiducial_s`): for one capture, the largest timing uncertainty of any pulse edge plus the uncertainty of the capture's clock alignment, in seconds. It is the one number a capture contributes.
- **Frame**: one power sample. The sampler is asked for 100 ms frames and delivers longer ones; the delivered length is the *cadence*.
- **Clock alignment (anchor)**: the step that places the sampler's frames on the wall clock, using five paired wall/monotonic clock readings taken around the capture.
- **Valid**: the ledger's word for a capture in which the alignment resolved, all 59 pulses were fitted, and no protocol check failed. The capture writer decides this at capture time.
- **Member**: a valid capture of W1 or W2. **Level screen** = largest member B. **S** (bracket screen) = range of member B, floored at 0.010818 s. **C** (budget ceiling) = largest of the predecessor's C, the new Q99, and S. **Q99** = t(0.995, n−1) × sample SD × √2.
- **Cell**: one rectangle of candidate edge positions that the estimator evaluates when it maps out which pulse-edge timings are consistent with the data. **Cell budget**: the cap on cells per capture, 165,000, frozen in `joulewise/powermetrics_fiducial.py:88`. A capture that needs more is recorded invalid with reason `detection_nonconvergent` and every partial fit is discarded.

## 2. Question 1 — membership and exclusions

### 2.1 Membership: correct

Executed. The set of captures whose custody evidence says `valid` equals the candidate's 12 members exactly. All 24 ledger finalization rows carry epoch `25G83`; 12 are `valid`, 12 `ordinary-invalid`. All 120 artifact digests in those rows match the custody bytes. Each member's stored B text equals the ledger's `exact_bound_lexeme_s` and the candidate's value, character for character. `excluded_members` is empty and `battery_confounded_sessions` is empty.

Stronger than read-back: my full re-run of the estimator from raw bytes reproduces all 12 member B values to the last digit, reproduces "alignment unresolved" for the 4 alignment failures, and shows each of the 8 capped captures needing more than 165,000 cells. The dispositions are deterministic functions of bytes whose digests were written to the ledger at capture time. Nobody chose them.

### 2.2 The exclusions: what actually happened

The packet says each non-valid capture is `clock_anchor_unresolved` or `detection_nonconvergent`. That is true of the top-level reason and hides the cause. The causes, read from each capture's `instrument_evidence.json`:

| Cause | Count | Captures | What it is physically |
|---|---:|---|---|
| Cell budget exhausted | 8 | W1 d02 d03 d09; W2 d02 d06 d08 d11 d12 | The estimator stopped at cell 165,000. Nothing was wrong with the capture. |
| Wall clock stepped mid-capture (`wall_minus_monotonic_span_exceeded`) | 3 | W1 d08, W1 d11, W2 d07 | The wall clock moved against the monotonic clock by 52.0 ms, 5.8 ms and 35.9 ms between the start and end readings. The cap is 5 ms. |
| No feasible clock fit (`affine_clock_fit_empty`) | 1 | W1 d01 | The registered r6 exclusion class. |

**Finding F1 (budget).** The 165,000 cap was sized on 2026-08-18 from the predecessor corpus, whose captures needed 112,205–137,189 cells at ≈120 ms frames. In this epoch the frames are 128–130 ms and the same estimator needs 144,037–170,965 cells. The cap now sits inside the workload distribution. Members used 87–99 % of it (w1-d06: 163,849). The 8 excluded captures needed 165,311–170,965, that is 0.2–3.6 % more than allowed. With the cap lifted all 8 fit 59 of 59 pulses with no spurious plateau.

**Finding F2 (clock steps).** Three captures were excluded for a reason that is not `affine_clock_fit_empty`. The packet's item 4 assertion was checked only against ledger-valid rows and did not surface this.

### 2.3 Could an exclusion have selected on outcome?

Procedurally no: every disposition was written by the pinned writer at capture time, before any B existed, and I reproduced each one from bytes. The remaining question is statistical: is the thing that triggers the exclusion correlated with B?

*Clock-step and fit-empty exclusions (4).* Decided from five clock readings. No power sample is read. They cannot depend on B. Their B is not computable under the registered estimator and I did not compute one.

*Budget exclusions (8).* The cell count is computed from the same trace as B, so correlation is possible and had to be measured. Executed on the 20 captures whose alignment resolved:

| Capture | Status | Cells needed | Median frame (ms) | B (s) |
|---|---|---:|---:|---:|
| w2-d05 | member | 144,037 | 127.86 | 0.028015 |
| w2-d09 | member | 147,365 | 127.84 | 0.029525 |
| w2-d01 | member | 148,923 | 127.72 | 0.032031 |
| w2-d04 | member | 149,173 | 127.93 | 0.032459 |
| w1-d05 | member | 150,187 | 127.58 | 0.024730 |
| w1-d10 | member | 151,427 | 127.79 | 0.024377 |
| w1-d04 | member | 156,205 | 127.98 | 0.036109 |
| w1-d12 | member | 158,019 | 127.99 | 0.026493 |
| w1-d07 | member | 159,063 | 127.99 | 0.029309 |
| w2-d03 | member | 162,911 | 129.68 | 0.027706 |
| w2-d10 | member | 163,405 | 130.16 | 0.038079 |
| w1-d06 | member | 163,849 | 129.76 | 0.026267 |
| w2-d02 | capped | 165,311 | 127.91 | 0.029164 (diagnostic) |
| w2-d08 | capped | 165,725 | 128.94 | 0.023351 (diagnostic) |
| w1-d02 | capped | 166,001 | 129.65 | 0.027679 (diagnostic) |
| w2-d12 | capped | 167,853 | 129.71 | 0.027362 (diagnostic) |
| w1-d09 | capped | 169,315 | 129.80 | 0.036909 (diagnostic) |
| w2-d06 | capped | 169,685 | 129.66 | 0.026508 (diagnostic) |
| w2-d11 | capped | 170,187 | 129.76 | 0.029430 (diagnostic) |
| w1-d03 | capped | 170,965 | 129.64 | 0.024069 (diagnostic) |

- Cells against B: Pearson r = −0.05, Spearman −0.23. No association.
- Cells against median frame length: r = +0.82. The cap selects on cadence, not on B. Captures fall in two cadence groups, near 127.8 ms and near 129.7 ms; 6 of the 9 in the longer group were capped, against 2 of 11 in the shorter.
- B against median frame length inside this epoch: r = +0.09.
- Capped mean B 0.02806 s against member mean 0.02959 s; difference −0.0015 s; permutation p = 0.44 (100,000 shuffles).

**Ruling.** No exclusion selected on B, in procedure or in effect, on the evidence of all 20 computable captures. The cap did thin the longer-cadence group, so the corpus is 25 % longer-cadence against 45 % in the full resolved set. That is a disclosure (§7 D2), not a defect in the numbers.

*What the capped captures would have changed, as a diagnostic only:* with all 20, the maximum is unchanged (0.038079 s), the minimum falls to 0.023351 s, the range becomes 0.014727 s against S = 0.013701 s, and Q99 becomes 0.017118 s against C = 0.019021 s. The candidate's level screen is unaffected, its S is 1.0 ms stricter and its C 1.9 ms looser than the 20-capture figures. These are sampling differences of the expected size. None is operative and none may be substituted.

### 2.4 Is each exclusion a registered mechanism, correctly applied?

The registration (lines 165–171) allows three routes: (a) at the read-back step, `affine_clock_fit_empty`, "the ONLY exclusion mechanism registered at this step: an unresolved anchor carrying any other reason refuses issuance instead of quietly excluding the member"; (b) "a protocol gate fails (plateau, SNR, 59-pulse detection, spurious plateau, edge coverage), which the writer records as ordinary-invalid"; (c) a recorded operator or system event.

- **Budget (8):** route (b). The reason `detection_nonconvergent` was registered on 2026-08-15 (decision log, D-078 registry amendment), before the registration was written on 2026-09-10, as a completed `ordinary-invalid` observation. The cap value was frozen on 2026-08-18. Correctly applied.
- **Fit-empty (1):** the registered class, recorded by the writer as `ordinary-invalid`. Correctly applied.
- **Clock step (3):** this needs a reading of clause (a), and I rule on it.
  - *Strict reading:* three unresolved anchors carry "any other reason", so issuance refuses.
  - *Structural reading:* clause (a) governs "this step", the issuer's read-back over ledger-valid rows, and "the member" is a would-be member. A capture the writer already recorded `ordinary-invalid` never reaches that step; it is excluded under (b).
  - **I adopt the structural reading**, for five reasons. (1) The Membership paragraph's companion sentence is about "Valid registered observations whose stored outcome does not resolve". (2) The runbook defines a retained value as one that "BOTH carries ledger disposition `valid` AND resolves". (3) Statement REV5-REFUSAL-BRANCH-01 item 4(iii), fixed and cold-gate ratified before the run and sent to the owner, makes the refusal apply to "a valid capture's stored clock alignment". (4) The 2026-08-15 amendment already made an unresolved alignment an invalidating condition at the writer. (5) The clause exists to stop an exclusion being chosen after values are seen, and a test on five clock readings cannot do that.
  - **But the word "quietly" binds.** These three exclusions were silent in the candidate, the packet and the re-derivation report. They must be named wherever the calibration's provenance is reported (§7 D3). The owner may overrule this reading in writing under statement item 10; such a ruling is recorded as made after the outcome was known.

## 3. Question 2 — arithmetic and proofs

Executed independently in 60-digit Decimal, with my own Student-t quantile (Simpson integration of the density, bisection) sharing no code with the issuer.

| Quantity | Candidate | Mine | Agree |
|---|---:|---:|---|
| Minimum (s) | 0.024377093921897318 | same | yes |
| Maximum (s) | 0.03807857930294817 | same | yes |
| Range (s) | 0.013701485381050852 | same | yes |
| Mean, 1e-18 presentation | 0.029591582579198539 | same | yes |
| Sample SD, 1e-18 presentation | 0.004330477884879059 | same | yes |
| Range quantized to 1e-6, half-even | 0.013701 | same | yes |
| S = max(0.013701, 0.010818) | 0.013701, floor not binding | same | yes |
| Level screen, maximum quantized to 1e-15 | 0.038078579302948 | same | yes |
| t(0.975, 11) | 2.20098516009163986788 | 2.200985160091638 | to 13 digits |
| t(0.995, 11) | 3.10580651553928100710 | 3.1058065155392685 | to 13 digits |
| 95 % two-draw prediction, binary64 | 0.013479318561660503 | same | yes |
| Q99, binary64 | 0.01902064410651988 | same | yes |
| C = max(0.010164834757777545, Q99, S) | 0.01902064410651988 | same | yes |
| C − S | 0.00531964410651988 | same | yes |

Worked line for Q99: 3.1058065155… × 0.004330477884879059 × 1.4142135623… = 0.0190206441… s.

Registered limits: members above 0.075 s: 0, so no `excursion_limited`. Members above 0.25 s: 0, so no plateau-inset refusal. Retained n = 12, the floor exactly. C > S, so `positive_headroom`.

Quantile proof: the block's declared bounds (residual ≤ 1e-30, agreement ≥ 30 digits) are met by the recorded values (4e-81 and 2e-81; 57 and 57 digits). I confirmed the quantiles to 13 digits only. The 80-digit proof itself is **NOT EXECUTED** by me; the cross-family re-derivation reports reproducing the block exactly and I give that weight because its membership, digest and statistics claims all matched what I measured myself. Where its report is silent (causes of exclusion, the cap, the clock steps) it was not wrong, it did not look.

**Ruling.** S, C, the level screen and headroom are correct and inside their declared bounds.

## 4. Question 3 — the screen challenge

Two members exceed the predecessor's level screen 0.032898493715362 s: w1-d04 (0.03610911339816257) and w2-d10 (0.03807857930294817). Revision 1 would refuse issuance on two.

**The sealed Revision 5 text removes that veto, in three places.** I compared the packet's quotation byte for byte with lines 600–664 of the registration at sha256 `81b65f08…ddf1`; they are identical.

> "This revision amends Revision 2's `## What replaces it`, `## On PASS`, and `## On FAIL` sections, Revision 1's “Stopping.” and dry-run outputs under “Blindness.”, and drops Revision 1's “Screen challenge.” as an issuance veto for this epoch."

> "The predecessor screen challenge is recorded as a diagnostic, not an issuance veto for this epoch: on an identical instrument it would falsely refuse 16.3 % of the time."

> "Calendar-day spacing, n ≥ 19, the predecessor screen challenge, and strict S < C are not physical barriers for this epoch."

The decision log's D-126 addendum of 2026-09-25 says the same. The text was sealed on 2026-09-25 (last commit to the file 2026-09-25 17:21 PDT); W1 opened on 2026-09-27 07:30 UTC. The registration digest appears in both arm notice bodies. The rule was fixed before the data.

I checked the 16.3 %. If 12 new draws and the 17 old ones come from one population, the chance that none of the 12 exceeds the old maximum is 17/29 = 0.5862, and that exactly one does is (12 × 17)/(29 × 28) = 0.2512. So two or more exceed with probability 1 − 0.5862 − 0.2512 = 0.1626. The figure is right, and two exceedances in 12 are unremarkable.

**Ruling.** The issuer's skip at lines 1923–1935 implements the sealed text. The count of 2 is recorded as a diagnostic. The second diagnostic is false: 0.038079 does not exceed 0.042622. The second limb of the question does not arise.

## 5. Question 4 — physics and science sanity

**Level screen and C above the predecessor's.** The level screen is the corpus maximum, so it rises with the data. Against the predecessor (n = 17): mean 26.85 → 29.59 ms (+10 %), SD 2.46 → 4.33 ms (+76 %). Welch t ≈ 1.98 on the means (p ≈ 0.07); variance ratio 3.1. The frames are 7 % longer (≈120 → 128–130 ms) and the registration states in advance that B grows with frame length. C rose by 1.871×, and that factors exactly: 1.760 from the SD times 1.063 from the smaller sample (t(0.995, 11) = 3.106 against t(0.995, 16) = 2.921). A wider distribution in a new operating condition is why a derivation was run and not a continuation. A larger C widens the uncertainty later measurements must carry; it cannot make a claim look better.

**W2 higher than W1.** Among members the means are 0.02788 and 0.03130 s, difference 3.4 ms, permutation p = 0.19. With the 8 capped diagnostics included the difference is 1.0 ms, p = 0.62. There is no session effect to explain.

**Yield 50 % against ≈79 %.** Explained in full by §2.2: 8 cap, 3 clock step, 1 fit-empty. The ≈79 % came from the predecessor epoch, where no capture came near the cap. Without the cap this epoch's yield is 20 of 24, 83 %.

**Display state.** Both windows' gate receipts record `displaysleep` = "0" and screensaver idle 0. The panel's actual state is recorded nowhere: **NOT EXECUTED**, and not executable from the evidence. What I can say is that all 24 captures sit in one cadence regime: per-capture medians 127.6–130.2 ms, longest single frame 141.6 ms, no frame above 183 ms. The registered slow regime has medians of 243–248 ms. Both probe receipts record `ProcessType` = `Interactive` on all three launchd labels and probe cadence medians of 131.8 and 131.1 ms.

**Battery gauge.** All 48 raw observations authenticate against their recorded digests and pass the registered predicate on my own parse. Beyond the step the charge names, I found two more: W1 stepped +9 mAh *inside* slot d11 (7575 → 7584), and the gauge read 12 mAh lower at W2's start (7572) than at W1's end. In every one of the 48 readings the current capacity equals the maximum capacity, at 100 % and fully charged; the two move together. That is the gauge revising its estimate of full capacity, not charge flowing. Voltage falls slowly and monotonically through each window (12896 → 12890 mV, 12894 → 12888 mV); charging would raise it. Instantaneous current is 0 mA in 47 readings and −11 mA in one. The `pmset` log check is the lead's; **NOT EXECUTED** by me.

**Estimator identity.** The four estimator files and the chain source are byte-identical between the W1 and W2 checkouts and match the digests the candidate pins.

**Sign of an artifact?** One, and it is in the estimator's work cap, not in the members: F1. One machine-state observation: F2, wall-clock steps in 3 of 24 captures. Neither touches a retained value. Every member's alignment passed with a wall-against-monotonic span of 0.74–1.54 ms over the 197 s capture, which is a smooth rate offset of at most 7.7 parts per million, and an alignment bound of 1.5–2.9 ms (executed over all 12).

**The prepare run.** The record shows one run, at 16:26:39 PDT, exit code 0, from the run checkout at `e7c8bcc6`, tool sha256 `21b2eea8…`, which are the commit and digest I found there. The command adds `--corpus-root` and `--predecessor-acceptance` to the statement's item 2(a) command. The first is the custody repair's argument; the second is permitted by amendment ruling `11-predecessor-path-ruling.md` (option (b)). No refused run is recorded.

**Left unchecked, stated plainly.**
- NOT EXECUTED: the ledger's 276-receipt hash chain (I checked artifact digests, not receipt links; the re-derivation report covers it).
- NOT EXECUTED: the 80-digit quantile proof.
- NOT EXECUTED: `pmset` log, quiet-machine census contents, rendered launchd plist digests against the templates.
- NOT ESTABLISHABLE from artifacts: that no person or agent read a B value before W2 was terminal. The harvest outputs I read contain none.
- NOT EXECUTED: an audit of the custody-repair rulings and the predecessor-path ruling. I read their verdict lines only (`MERGE` / `TOOL REPAIR` with four conditions; option (b) with six conditions). Whether each condition was discharged before the run is for the D-138 gate.
- NOT EXECUTED: a second seat's replication of §2.3. The script and outputs are in scratch with digests in §0; the computation is deterministic.

## 6. Question 5 — verdict

**PROCEED TO ISSUANCE.** The candidate is what the sealed registration prescribes. Membership is exact, the arithmetic reproduces, the screen-challenge veto was removed before capture, and the one mechanism that could have biased the corpus was measured and did not.

**Marks the calibration carries.** No registered mark: not `excursion_limited`, not `zero_headroom`. Status `positive_headroom`, C − S = 0.005320 s. Retained n = 12, at the floor with zero margin. Screen-challenge count 2, diagnostic.

## 7. Mandatory disclosures

These travel with the issuing transaction's record and with any text that reports this calibration. None changes a member, a statistic or an operative number.

- **D1. Yield and causes.** 12 of 24 captures are members. The 12 others: 8 stopped by the 165,000-cell work cap, 3 by a wall-clock step above 5 ms during capture, 1 by an infeasible clock fit.
- **D2. The cap is mis-sized for this epoch.** It was sized at ≈120 ms frames; this epoch runs at 128–130 ms and needs 144,037–170,965 cells. The cap excluded on cadence (r = +0.82), not on B (r = −0.05; p = 0.44). The corpus under-represents the longer-cadence group, 25 % against 45 %.
- **D3. Three exclusions carry an alignment reason other than the registered class.** `wall_minus_monotonic_span_exceeded`, spans 52.0, 5.8 and 35.9 ms. They were excluded by the writer as `ordinary-invalid`, under the structural reading ruled in §2.4.
- **D4. Eight diagnostic B values exist for excluded captures** (§2.3 table), computed by this gate with the cap lifted. Never members; disclosed design inputs for any successor.
- **D5. Tool repair.** The issuing tool was repaired after capture and before any B was read (statement item 6(d) R9).
- **D6. Known conditions.** Display state unconstrained and unrecorded; battery gauge steps in both windows with no current flow; n = 12; predecessor-screen count 2.

## 8. Recommendations, outside this gate

- **The cap will refuse about a third of future calibration captures.** A measurement bracket needs a valid capture before and after, so roughly one bracket in four will complete. Re-sizing the cap changes a pinned estimator file, which makes the issued calibration stale and forces a re-issue. The council should rule *before* that change on which captures a re-issue may contain. My view: the same 12, because the ledger rows are immutable and the 8 diagnostic values are now known.
- **Find what steps the wall clock.** Three steps of 6–52 ms in 24 three-minute captures is frequent enough to matter to measurement windows too.
- **Packet erratum.** Item 04 should name the per-capture cause codes; its assertion about the only registered exclusion class is true of ledger-valid rows only.

## Summary for the owner

1. The candidate is correct and may go to the issuing transaction: the 12 members are exactly the registered set, every number reproduces, and Revision 5 removed the screen-challenge veto before any capture.
2. The 50 % yield has a cause nobody had reported: 8 good captures were discarded by the estimator's 165,000-cell work cap, sized for the old 120 ms cadence, and 3 by wall-clock jumps; I measured that the cap did not select on B (r = −0.05), so the numbers are unbiased, but this must be disclosed.
3. Before measurement windows run at scale, the cap needs re-sizing and the clock jumps need explaining; the three clock-jump exclusions rest on my reading of the registration, which you may overrule in writing.
