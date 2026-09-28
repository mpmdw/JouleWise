SEAT: Opus 5.5 — CAP-COUNCIL-25G83-01

Read-only in `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2`; scratch `/tmp/cap-council-d528efb2/opus/`. **Disclosures:** I read B values only as printed in the gate ruling. My one estimator probe prints cell counts and a yes/no "B identical" flag, never a B. I have not computed a new cap value; the rule in §3 fixes it.

A **cell** is one rectangle of candidate (onset shift, offset shift) pairs that the estimator tests. The **cap** is the maximum number of cells per capture (`powermetrics_fiducial.py:88`).

## 1. What the cap is for

- **It guards against runaway input.** It is not a memory limit or an accuracy knob. Finding L2-1 (`2026-08-15-readiness-council/seat-reports/L2-CALIBRATION-ACQUISITION-report.md:49`) found the problem. When a pulse's loss surface is flat, the branch-and-bound search splits a 1.5 s × 1.5 s square down to 0.1 ms cells: about 2.25×10⁸ cells per pulse. The window writer then grinds for hours while holding its lease. Cells were chosen over seconds so the stop is reproducible (`:78–92, :533–550`).
- **Normal work is about 5 orders of magnitude below that:** about 2,400–2,900 cells per pulse. D-143 sized the guard as "largest need seen + 20.3 %". That is how you size a workload envelope, not a guard, and a guard 20 % above the workload becomes a filter on data. **This is the root error.**
- **Runtime does not constrain the cap (executed, w1-d06).** 163,849 cells cost about 1.8 s of a 14 s re-derivation, about 13 µs per cell. The 120 s wall deadline (`:92`) is about 8 million cells away.
- **Why work grows with frame length (executed, 4 captures).** The search visits every cell *inside* the accepted region, so work grows with the region's **area**. B needs only the region's **extent**, since the search returns its min and max (`:699–704`). I tested an exact pruning: skip any rectangle already inside the bounding box found so far.
  - B and all 59 per-pulse bounds come out bit-identical on w1-d06, w2-d05, w2-d02 and w1-d03.
  - Work falls from 144,037–170,965 cells to 26,807–28,603.
  - The gap between the two cadence groups falls from +18.7 % to +6.7 %.
  - So the cap problem is largely an artifact of the algorithm.
- **Could the bound scale with frame length instead?** Possible, not needed. A per-pulse limit scaled by (frame/120 ms)^k works only if k is stable, and it isn't (§7.2). A constant an order of magnitude above normal work never needs per-epoch re-sizing.
- **Cost under D-138.** Any byte change stales the calibration and needs one re-freeze transaction: re-issue, re-pin packs, arm sources, exact-pin regressions (`2026-08-18-shakedown-first-light/03-budget-calibration-sweep.md`). A constant, a formula or the pruning each cost that one transaction. The constant needs the least review.

## 2. Route

**Recommend route R**, with the ≥ 24 non-claim captures registered as a **successor derivation corpus** (§4).

- **Route R cost:** 2 windows of 12 slots (about 2 h 10 min each, ≥ 6 h apart), about 1 calendar day, plus about 0.5 day before and 0.5–1 day after. **About 2–3 days** to lift H1.
- **Route M:** no windows, but about 1/3 of calibration captures stop and about 44 % of brackets complete (A1 N-3). Every claim then rests on a low-power comparison. Reject.

## 3. Sizing rule (fixed before any value is computed)

> **CAP-RULE-1.**
> (a) **Inputs:** per-capture evaluated-cell counts and per-capture median native frame lengths only. They come from every retained raw capture that resolved its clock alignment and fitted 59/59 with the cap lifted, under the code that will ship: the August protocol-v3 corpus (n = 34), the 20 resolved 25G83 captures, and the 2026-08-18 shakedown. No B value, statistic or screen is used.
> (b) N_max = the largest cell count. T_obs = the largest median frame length.
> (c) k = the largest of two cadence exponents, each ln(mean cells ratio) / ln(mean frame ratio): August against 25G83, and between the two 25G83 cadence groups (split at 128.5 ms).
> (d) **Covered range:** median frame ≤ 150 ms, the registration's own stop (`preregistration_d079_epoch_25g83_rev1.md:612`).
> (e) **Cap = 10 × N_max**, rounded up to the next 10,000. The factor 10 is an order of magnitude above normal work, set by the guard's purpose, not fitted.
> (f) **Coverage check:** require Cap ≥ 2 × N_max × (150 / T_obs)^k. If this fails, the rule refuses and council reconvenes; there is no automatic bump.
> (g) **Guard check:** on the reference host, a synthetic flat-surface input must stop on the cell trigger within 60 s. If not, the rule refuses.
> (h) **Outside the range:** median frame > 150 ms is already a registration stop. A cap stop there is tagged `frame_out_of_covered_range` in the harvest report and is excluded from the zero-stop test.
> (i) **Inside the range:** any cap stop among the ≥ 24 validation captures is a failure of the rule. It returns to council, never to an in-loop re-size.
> (j) **Evidence roles:** the ≥ 24 new captures only validate the rule; they never fit it. The launch-context table has no cell counts and only justifies (d).

**How (f) avoids A1's trap.** No fitted line is carried past its data. The rule takes the steepest slope observed, doubles it, and carries it to the registration's hard frame limit.

## 4. Membership

- **Re-issue with the cap change: the same 12 members, exactly.**
  - Ledger dispositions are immutable.
  - The 8 capped captures' B values are already known (D4). Admitting them would move S by +1.0 ms and C by −1.9 ms (ruling §2.3), so admitting them would be choosing numbers.
  - A cap change cannot move a B that finished (A1 §2), so the 12 re-derive bit-identically. Record both digests and the replay.
  - The registration voids only on a code rotation *mid-campaign* (`:136–137`), and the campaign ends at issuance.
- **The 8 stay diagnostics permanently.**
- **Fresh corpus.** Register the ≥ 24 route-R captures as derivation windows under a sealed successor revision, with the 12 + 8 as disclosed design inputs and B blind until the terminal session.
  - Why: a raised cap lets measurements sample long-frame states, and the 12 under-represent those (25 % against 45 %, D2).
  - The diagnostic "no difference in B" (p = 0.44, n = 20) is weak evidence.
  - Result: n ≈ 20 from the unfiltered population, instead of 12 at the floor.
  - Cheapest acceptable alternative: a pre-registered validation look on those 24.

## 5. Sequencing

1. `dbad7cc7` issuance under A1 B1–B3 (unchanged).
2. Written council ruling on CAP-RULE-1 and membership, then a cold gate.
3. **Network time OFF for windows (§6).** This is an admin/`systemsetup` action and may need Ed or sudo.
4. Offline replay, no capture. Zero cap stops at the new value on every retained capture, and all 12 members bit-identical.
5. One D-138 transaction: the cap change plus the same-12 re-issue.
   - **(b)** A staged estimator branch joins only if its replay leaves all 12 member B values bit-identical. Otherwise it waits for a later derivation transaction.
   - I did not review those branches.
6. **(c)** The #416 audit on the step-5 tree, **before** the captures, so a forced estimator change cannot waste them. Close agent sessions before the quiet windows.
7. **(d)** The ≥ 24 non-claim derivation captures, with network time OFF attested for each capture.
8. Successor gate and issuance.
9. A ruling closes H1 and H4, then claim-bearing windows.

## 6. Clock steps: cause found (executed, read-only)

`/usr/bin/log show` for `timed` (`/tmp/cap-council-d528efb2/opus/timed.txt`, `applies.txt`) matches all three steps:

| Capture | Window (PDT) | `timed` action | Span on record |
|---|---|---|---|
| W1-d08 | 01:50:11–01:53:28 | 01:53:09 `settimeofday` +53.2 ms | 52.0 ms |
| W1-d11 | 02:20:11–02:23:28 | 02:20:42 adjtime +4.39 ms | 5.8 ms |
| W2-d07 | 10:10:13–10:13:30 | 10:11:29 adjtime −35.9 ms | 35.9 ms |

- **What happened.** Network time was **ON** in both windows. `timed` re-synced about every 27 min, applying corrections of 12.6, 53.2, 4.4, 44.2, 35.9 and 38.8 ms. Every correction ≥ 1 ms that landed inside a capture excluded that capture. Member W1-d12 contained only µs-scale adjustments.
- **Is 5 ms the right physics? Yes.**
  - With network time off, the clock drifts freely at about 8 ppm, about 1.6 ms per 197 s capture. That leaves a 3× margin under 5 ms.
  - A step of any size breaks the anchor's affine model (`uncertainty_evidence.py:891–894`). The cure is to remove the steps, not to loosen the limit.
- **Cheapest check: the query above.** It takes seconds and needs no capture.
  - The method already requires network-time-OFF attestation from this log for claim-bearing captures (`uncertainty_evidence.py:903–909, 952–956`).
  - Confirm that the 25G83 claim-window arm path enforces it. A 09-22 record found the probe did not govern evidence nights (`2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md:185–197`).

## 7. What I judge wrong

1. **D-143 treated a guard as an envelope** (§1).
2. **A1 §5.1's "≈7,500 cells per ms" compares two clusters; it is not a slope.**
   - Inside each group the correlation flips: −0.42 in the long group, +0.48 in the short.
   - The exponent is about 6.0 inside 25G83 and about 4.4 between August and 25G83.
   - The shakedown needed 124,029 cells at 113 ms, above the 120 ms median.
   - My inference: frame length marks a machine state rather than setting the work. A1's extrapolation can err in either direction.
3. **A1 names only selection on machine state.** Cells track the region's area and B tracks its extent, so in other states a tight cap could also select on B. Inside 25G83 the correlation between cells and B is r = −0.05, but that is not a guarantee. The cap belongs far above the workload, leaving the registered B screens to judge.
4. **A1 H4 calls the steps unexplained.** They are network-time corrections, which means W1/W2 did not meet the method's network-time-OFF precondition. For the members this is already priced, since µs-scale slews fall under the span term. It should be disclosed as a known condition at the issuance gate; it is not a void.

**Summary:** Route R, with the cap raised about tenfold by CAP-RULE-1 and the coverage check carried to 150 ms. The re-issue keeps the same 12 members. The ≥ 24 validation captures become a successor derivation. Network time goes OFF before any window. Exact bounding-box pruning (about 6× less work, bit-identical B) is optional hardening.
