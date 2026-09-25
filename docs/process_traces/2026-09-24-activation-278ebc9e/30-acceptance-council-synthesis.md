# 30 — Synthesis of the D-184 council on instrument acceptance on macOS 25G83 (magistrate, Opus 5.5)

Four blind seats answered brief 23 on packet 22: Sol 6.0 (24), Astra 6 (25), Opus 5.5 (26) and Fable 5.1 (27). This synthesis binds nothing until the cold Fable judge rules on packet 31.

Terms, built before use:
- **Acceptance:** the D-079 calibration acceptance artifact. Every claim-bearing window needs valid calibration brackets (a pre- and post-window timing calibration capture) bound to the live operating-system "epoch". The active artifact r7 is bound to build 25F84; the machine runs 25G83.
- **Capture:** one calibration run. The GPU is switched on and off in 59 timed pulses while `powermetrics` samples power. The **fiducial detector** needs at least one whole sample interval inside each pulse's interior, which is the pulse minus 0.25 s at each end. One missed pulse invalidates the capture.
- **B:** a capture's timing bound, meaning the worst residual endpoint error plus the clock-anchor bound.
- **Corpus:** the set of retained captures from which the acceptance's bounds are derived. Its pre-registration (rev 1) asks for three 12-slot windows on distinct calendar days and retained n ≥ 19.

## What all four seats agree on

1. **The cadence change is mainly a YIELD problem, not a claim-accuracy problem.**
   - With 1.0 s pulses and a 0.25 s inset, the interior is 0.5 s. A delivered interval of about 0.245 s (p95 0.274 s, max 0.419 s) often straddles it, and one miss voids the capture. That explains the 11/24 valid rate on 09-19.
   - Energy over complete intervals is allocated by overlap, so coarser intervals do not by themselves bias window energy. The vulnerabilities are cut cells at window edges, timing reconstruction, and pulse identification. Fable puts the cut-cell effect at about +0.4 J.
   - The nine retained 25G83 B values (0.028–0.043 s) sit only slightly above r6's (0.023–0.033 s).
2. **The protocol fix is a longer calibration pulse**, which gives a new protocol identity (v4) and a new registration revision:
   - Opus: 1.5 s, which gives a 1.0 s interior, at least 2× the largest observed interval.
   - Sol and Fable: 2.0 s, which gives a 1.5 s interior and guarantees a whole interval for any h ≤ 0.75 s.
   - Astra: a deliberate re-characterisation at the observed cadence.
3. **Cause attribution (lane A243, "why did macOS change the cadence") is NOT a prerequisite for acceptance.** It runs in parallel as a diagnostic that affects disclosure. Only Sol puts an A-type matched diagnostic window first, and only to test whether some production-compatible setting restores 0.120 s.
4. **Keep the physical gates:** pulse interiors, SNR, complete detection, edge support, a feasible clock fit, and the valid pre and post brackets for every claim-bearing window.
5. **Drop or relax the barriers that are calendar or yield arithmetic, not physics.** All four say the three-distinct-calendar-days rule is not physical: midnight resets nothing, while elapsed hours and thermal state matter. The pre-registration's own arithmetic shows n ≥ 19 was sized from historical yield, not from an error bound.
6. **Rules before data.** The already-seen n1/n2 B values are disclosed as design inputs and are not admitted to the corpus. The new corpus is captured blind to B, with stops on counts only.
7. **Opus adds two points:** (a) a futility stop on counts; (b) Ed should switch off automatic macOS updates until the end of November, because another build bump restarts this whole process.

## Where they differ

| Item | Sol | Astra | Opus | Fable |
|---|---|---|---|---|
| Pulse | 2 s (after a matched diagnostic) | re-characterise at observed cadence | 1.5 s (v4) | 2.0 s (v4; window 1.8–2.2 s) |
| Windows | 1 × 12 slots with ≥ 10 valid, if simulation shows it admits no false claim; else 2 days | 3 separately started blocks × 12, calendar dropped | 3 windows ≥ 4 h apart, first to last ≥ 24 h | ≥ 2 windows ≥ 6 h apart, any dates; third only on n < 12 |
| Retained n | ≥ 10 (operating minimum, simulation-checked) | keep 19 as a target | 19 unchanged (implied) | ≥ 12 |
| Futility stop | — | — | after W1 if < 8/12 valid | third window only on count |
| Ed's written acknowledgement | — | — | required by prereg `:11-13` (night count, slots, n) and for dropping the r6 screen challenge | none on the critical path |
| Earliest G2-a | 09-26 (conditional) | see seat | see seat (e) | see seat (e) |

## Proposed ruling (the magistrate's; the judge may amend any part)

- **R-ACC-1 (protocol).** Adopt fiducial protocol v4 with a 2.0 s pulse, authenticated window 1.8–2.2 s and the 0.25 s inset unchanged. It lands as a full-tier PR merge-staged into the D-138 successor transaction. Before it lands, a desk replay must show the miss mechanism: the 24 archived n1/n2 captures under the interior rule, and Opus's jittered resampling of r6 frames onto 25G83 frame-length sequences, which must reproduce the observed miss rate. If the replay does not reproduce the miss rate, the mechanism is wrong and the path stops.
  - Why 2.0 s over 1.5 s: margin against the heavy tail (max 0.419 s), for about +30 s per capture. That still fits the 480 s slot.
- **R-ACC-2 (registration rev 2 for 25G83).** Sealed before the first v4 capture:
  - Two 12-slot derivation windows, at least 6 h apart, any dates.
  - Issue the acceptance on retained n ≥ 12.
  - A third window is pre-authorised only if n < 12 after two windows (a count-only stop).
  - Futility: if window 1 has fewer than 8/12 valid, stop and go to the A243 diagnostic.
  - Blind to B during capture.
  - The already-seen 25G83 B values and the r6 decimation are disclosed as design inputs, never admitted.
  - All physical gates are kept.
  - The desk simulation of R-Q4(a) is extended to show that n ≥ 12 with the v4 protocol does not admit a false claim through the actual bracket, floor and decision-interval gates. If it does not show this, the registration reverts to n ≥ 19.
- **R-ACC-3 (A243).** The attribution runs as a parallel diagnostic window: the 35-min matched matrix, using the existing `sudo -n` powermetrics rule if one exists, with no new sudo. Its result goes to disclosure. It is not a gate unless native intervals exceed 0.75 s under load.
- **R-ACC-4 (authority).** Under D-184's addendum (the council decides experiment design; Ed is owner-only for hardware, sudo, notice NO and claim publication), this council plus the cold gate decides the registration revision. Ed is informed after, with a veto. The judge rules whether prereg rev 1 `:11-13` requires Ed's written acknowledgement anyway.
- **R-ACC-5 (Ed hardware/settings, asked in the after-the-fact email as an action item, not a question):** disable automatic macOS updates until the end of November.
- **R-ACC-6 (order).** Protocol v4 and registration rev 2 (desk) → cold gate → derivation windows W1, W2 (and W3 only if needed) → derivation, cold science gate, and the D-138 successor transaction → G2-a bindings regenerated → G2-a arm → calibration night, as ruled in COUNCIL-407-01.
