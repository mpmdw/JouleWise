# Consult CAP-COUNCIL-25G83-01: the 165,000-cell estimator work cap at epoch 25G83

You are ONE of four blind, independent seats (Sol 6.0, Astra 6, Opus 5.5, Fable 5.1). You will not see the other seats' answers before writing yours. Disagreement is useful; say plainly where the rulings below are wrong. You advise; you do not decide.

## Facts (verify what you rely on; cite file:line)

Repository: any clean checkout of main `e7c8bcc6` plus the 2026-09-27 records, e.g. `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2` (read-only).

- **The cap.** `joulewise/powermetrics_fiducial.py:88` freezes a per-capture cell budget of 165,000 (decision log D-143, 2026-08-18: sized as "max observed need 137,189 + 20.3 %" from a corpus at ≈120 ms sampler frames). A capture that needs more is recorded invalid, `detection_nonconvergent`, and its partial fit is discarded. The file is one of the four D-138-pinned estimator inputs, so changing the cap stales the issued calibration and forces a re-issue (decision log D-138).
- **What the 25G83 corpus showed** (cold science gate SCI-25G83-CANDIDATE-01, `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md` §§2, 7, 8): 24 captures, 12 valid members. Of the 12 others, 8 were stopped by the cap (need 165,311–170,965 cells), 3 by wall-clock steps of 52.0 / 5.8 / 35.9 ms (cap 5 ms), 1 by an infeasible clock fit. Frames at this epoch are 127.6–130.2 ms; need ≈ +7,500 cells per ms of frame length, r = +0.82. Members used 87–99 % of the cap. With the cap lifted, the 8 fit 59/59 pulses; their diagnostic B values were computed by the gate (§2.3) and are now disclosed design inputs (D4) — never members.
- **Addendum A1** (`…/70-science-gate/31-addendum-ruling.md` §§4, 5, 7): B1–B4 — the issuing transaction for candidate `dbad7cc7` keeps all four estimator digests and folds in no estimator change; the cap is re-sized, if at all, in a LATER D-138 transaction after the council rules on re-issue membership. §5 H1–H4: a HOLD on 25G83 claim-bearing windows until a written ruling closes the cap-and-cadence question by **route R** (re-size under a rule written before the value is computed, stating its frame-length range, cells and frame lengths only; then ≥ 24 non-claim captures under the new cap with zero cap stops) or **route M** (keep the cap and measure the filter under a registered plan). §5 also gives an extrapolation showing a naive "max + 20.3 %" re-size (≈205,600) could again sit inside the workload at the registration's recorded launch-context frames (median 131.6 ms, p95 134.8 ms).
- **Mechanism of harm** (A1 §5.1): in a measurement window an invalid calibration capture abandons its bracket, so surviving measurements come preferentially from short-frame machine states; if frame length correlates with workload energy, reported energy is a filtered sample. Unmeasured.
- Lanes: `TASK_QUEUE.md` rows A331 (ESTIMATOR-CELL-CAP-RESIZE-01) and A332 (WALLCLOCK-STEP-SOURCE-01). Registration: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. Owner principle (directive #421): anything that can change whether a number is true is mandatory.
- The D-138 issuing transaction for the current candidate (`dbad7cc7`, S = 0.013701 s, C = 0.019021 s) is being prepared now, separately; it is not in question here.

## Questions

1. **What is the cap for?** Find its purpose in code and history (runtime bound? memory? pathological-input guard?). Does that purpose need a fixed cell count at all, or could the bound be expressed in terms the physics supplies (frames, pulses, capture duration) so it scales with cadence instead of being re-sized per epoch? What would that change cost under D-138?
2. **Route R, M, or another route?** Recommend one, with its cost in windows and days.
3. **The sizing rule** (if the cap stays a number or becomes a formula): write it in full, BEFORE any value is computed. It must use cell counts and frame lengths only (no B values), state the frame-length range it covers and what happens outside that range (refuse? flag?), and say how it avoids the extrapolation trap A1 §5 describes. Say what evidence the rule may be fitted to (the 24 25G83 captures' cell counts? the August corpus? the launch-context table?).
4. **Membership of the re-issue** after a cap change: the same 12 members (ledger rows are immutable), the 12 plus captures re-evaluated under the new cap, or a fresh corpus? Weigh selection bias, the immutability of ledger dispositions, and the fact that 8 diagnostic B values are already known to the project.
5. **Sequencing:** relative to (a) the `dbad7cc7` issuance, (b) the other estimator-file branches that are merge-staged under D-138, (c) the three-family full-system audit Ed requires before any claim-bearing run (directive #416), and (d) the ≥ 24 non-claim captures. Give an ordered list.
6. **The clock steps (H4):** is a 5 ms span limit the right physics, and what is the cheapest way to find what steps the wall clock (NTP/timed slews, sleep/wake, etc.) without running a quiet-machine capture from an agent session?
7. Anything in A1 §5 or D-143 you judge wrong.

## Output

Write your answer (≤ 1,500 words, plain language, every claim cited or marked as inference) with a first line `SEAT: <model> — CAP-COUNCIL-25G83-01`. Run read-only commands to check facts; modify no file in any repository; run no capture or powermetrics; do not call other models.
