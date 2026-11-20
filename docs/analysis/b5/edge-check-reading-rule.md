# Block 5 cross-instrument edge check: reading rule

Research lead (Fable 5.2), 2026-11-12. Written and committed before any edge time is computed; the commit time is the record.
Status: **exploratory diagnostic** on released Block 5 data. It is not registered, mints no claim, and changes no registered number or sentence.
What was seen beforehand: only the feasibility probe (one ALPHA member and one calibration pulse, levels and sample layout; no edge-time difference was computed).

## 1. Question and reading

Paper 1 derives its timing bound from commanded GPU pulses and applies it to inference edges untested (§4.2, §9).
The question: **does the sampler place inference edges, relative to an independent 50 Hz meter, the same way it places pulse edges?**

For each edge, Δ = (sampler edge time) − (KM003C edge time) on one clock. The statistic is the transfer difference
T = median Δ over inference edges − median Δ over pulse edges, like with like (rise with rise, fall with fall).
The reference line is each session's operative timing bound b, as already printed in `RESULTS.md`. It is a reference, not a test: the check is **descriptive**.

| Result | Wording |
|---|---|
| 95% interval of T lies inside ±b | "An exploratory cross-instrument check on released data found no pulse-to-inference difference in edge placement larger than the timing bound (T = …)." |
| Interval lies wholly outside ±b | "An exploratory check found that the sampler places inference edges … ms differently from pulse edges, more than the timing bound; the pulse-derived bound may be too narrow for inference edges." Printed with the same prominence. |
| Anything else | "The check did not resolve a difference at the scale of the timing bound (T = …)." |

In every case: §9 keeps the limitation, with "untested" becoming "not tested by a registered experiment"; the registered fixed sentences stay; no floor, interval or outcome word moves.
The first row does not validate the bound: b limits each edge, T compares typical placement.
Standing caveat, printed with the number: the meter reads whole-machine DC input, whose lag behind rail power may depend on step size and shape, so T mixes sampler placement with that path difference. The meter is not ground truth.

## 2. Edges, sessions, inclusion

- **Sessions:** the three claim-usable sessions only (ALPHA a1, BETA a6, GAMMA a1). **Runs:** the runs Paper 1's Block 5 cells keep, plus each one's calibration capture. No other data.
- **Pulse edges:** command ON (rise) and OFF (fall) of the 56 non-warmup pulses per capture.
- **Inference edges, primary:** decode end (fall), in every kept run; request start (rise) in 2,048-token-prefill runs.
- **Inference edges, secondary (reported, not in T):** request start in short-prefill runs (the 76 ms prefill blurs it); the prefill-to-decode transition in 2,048-token runs.
- **Exclusions, fixed:** another stamped edge inside the edge's window (−700 to +800 ms), except the transition itself for the secondary edges; a meter dropout or a missing sampler record in the window; a step smaller than 5 times the larger standard deviation of the two level windows, on either instrument. Counts of excluded edges are printed by reason. Nothing else is removed, and no outlier trimming.

## 3. Estimator and clock

- **One estimator for both instruments,** the energy-equivalent step time: t = B − ∫ₐᴮ (P − L_pre) dt ÷ (L_post − L_pre).
  L_pre and L_post are median power over −700 to −250 ms and +350 to +800 ms from the stamped edge. A to B is −250 to +350 ms for the meter; for the sampler, the whole records that cover that span.
- **Meter:** P = V × I per 20 ms sample from `stream-001.jsonl`; device time mapped to CLOCK_MONOTONIC_RAW by the shipped `km003c_parse.clock_fit`, not refitted.
- **Sampler:** summed rail power (CPU + GPU + ANE) over `power_trace.csv` records at their `interval_start_s` and `interval_end_s`, the placement the reduction reads.
- **Clock:** everything in REALTIME (sampler records, phase events, pulse `epoch_s`) goes to the meter's RAW axis through a straight-line fit of the meter polls' `rx` on `rt` within ±30 s of the edge. The same route in all three sessions; no constant monotonic-to-RAW offset is used anywhere. Stamps only place the windows; Δ does not depend on them.

## 4. Statistic and interval

- Per session and direction: n, median and interquartile range of Δ for pulse and for inference edges, and T.
- Interval on T: 95% percentile bootstrap, 2,000 resamples, resampling whole runs (each run brings its own calibration capture). A pooled T over the three sessions, resampling runs within session, is printed beside them.
- No threshold, no p-value, no pass or fail. The ±b line and the three wordings of §1 are the whole reading.

## 5. What is printed, and where

- One short paragraph in §4.2 after the transfer sentence and a matching change in §9, both headed *Exploratory, derived after release*.
- One appendix table (Appendix B): per session and direction, the §4 numbers, exclusion counts and the secondary edges.
- The script, its output and this rule are cited by commit. §6.4 and the abstract are not touched.

## 6. What will not be done

- No change to windows, estimator, edge classes, exclusions or sessions after any Δ is seen. A bug fix is allowed; it is logged in `DEVIATION-LOG.md` and both results are printed.
- No second estimator "to check", no per-model or per-phase slicing beyond §4, no selective reporting: all three rows of §1 are equally printable.
- No use of the result to alter b, any floor, any registered sentence, or Block 6 handling.
- No opening of Block 6, ALIGN or BYTES held-out data.
- No further guards, gates or reviews beyond one independent re-run of the script.
