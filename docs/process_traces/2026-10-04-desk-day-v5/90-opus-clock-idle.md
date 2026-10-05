# Consult: the `s1` clock and idle-admission budget (Opus 5.5 seat, blind)

## What each guard actually keeps out

- **The member bound protects the joules.** Its value is H (half the anchor interval) plus the wall-minus-monotonic span, plus resolution and padding (`joulewise/uncertainty_evidence.py:1335-1345`).
  - Drift is charged in full because the trace is mapped forward at rate 1 (`:910-925`).
  - If an edge is misplaced by ε at power P, the window's energy is off by P·ε: at 40 W and 5 ms that is 0.2 J per edge, below the roughly 1 J attribution limit.
  - A step inside a stream is caught separately, because the fit refuses any departure over 250 µs (`:895-905`).
- **The T-0 check protects provenance, not joules** (`arm_readiness_evidence_t0.py:1180-1185`). It shows that nothing set the clock between R0 and authoring. A step between streams moves no energy, since each stream fits its own anchor. So the T-0 check may allow for drift, but it must still detect a resync step.

## 1. The combination I recommend

- **(c) idle 75 s, not 55 s.**
  - Block-3 streams at idle 75 ran 112–222 s, and all 50 were bounded.
  - Record 44 already sizes block-3 attempts ("two 110 s attempts", `44-block4-sizing.md:46`), so 75 s leaves its arithmetic true.
  - At 55 s, streams land near 85–90 s, where the replay put 1 in 36 over 5 ms. Over 23 gated members that is 1 − (35/36)^23 ≈ 0.48 of at least one unbounded member: a second coin flip on END STATE.
- **(b) as the primary clock guard, with F_max = 5 ppm.** Read `ntp_adjtime(modes=0)` after G10's OFF and at every R0. Arm only if |f| ≤ 5 ppm.
  - The worst stream at zero backoff is a retried member: two idle slices of about 97 s, plus guards and about 30 s of run, so T ≈ 250 s.
  - Budget: H_max 3.60 ms (record 44 `:69`) + 0.1 ms + f·250 s ≤ 5 ms, so f ≤ 5.2 ppm.
  - Today's −3.17 ppm passes.
  - If the draw fails, allow one reviewed ON/OFF redraw before `a1` (a §5 erratum). A second failure goes to the lead and is not armed.
  - If many archived draws exceed 5 ppm, use 8 ppm: first attempts still fit (3.7 + 1.1 = 4.8 ms), and you accept the risk on retried members.
- **(a) only in the measured form**, under Q2.
- **(e) zero backoff plus the re-arm clause**, under Q3.

## 2. Drift-aware T-0 bound

The fixed form, 5 ms + RATE_CAP·span, is unsound in exactly the period block 4 occupies.

- A resync step is not "above 0.5 s" by nature. It equals the offset accrued since the last sync.
- G10 resyncs just before `a1`. Two hours later, at −3.17 ppm, the accrued offset is only 23 ms.
- With 12 ppm × 3600 s, the hole is 48 ms. A stray network-time ON during `a1`, `a2` or `s1`'s T-0 would pass unseen.
- `timed` may also slew a small offset rather than step it.

The bound I would register has three parts:

1. |Δ − f_R0·span| ≤ 5 ms, where f_R0 is the kernel frequency read with R0.
2. The frequency word at authoring equals f_R0.
3. |f_R0| ≤ F_max.

Any intervention by `timed` rewrites the frequency word, so part 2 catches steps and slews at any accrued offset. The prediction is exact: the memo's fit (−3.1681 ppm) and the kernel word (−3.16759 ppm) differ by 2 µs over 3600 s. G10's helper (`capture_t0_anchor_positive_control.py:125` and its post-ON checks) needs the same form. It still discharges, since the offset accrued since 10-01 is hundreds of ms.

The fallback, if reading the kernel word is too large a change before seal: 5 ms + 5 ppm·span, not 12 ppm. That leaves a 23 ms hole at 3600 s, which must be disclosed as a G4 limitation.

## 3. (d) or (e)?

**Choose (e) for this one night.**

- (d) rewires the sampler lifecycle under seal (`controller.py:1096-1140`, attempt promotion), along with custody and harvest replay. New surface on a qualification night.
- Its payoff is a 300 s backoff that has never fired live (memo §1.14).
- A guard-attested abort is the instrument refusing bad conditions, with no contaminated number produced. Calling it physics END STATE is a category error.
- Clause (e) as I would write it:
  - one such abort per block;
  - the guard observation must be authenticated;
  - no other RECOVER cause may be present;
  - the earlier attempt's bytes are kept and never pooled;
  - a second abort follows §7's same-refusal-twice consult.
- For block 5: an immediate retry inside a minutes-long burst re-measures the same burst. A long backoff needs either (d) or the v3.1 identity, which caps placement at 5 ms and drift at 25 ppm / 15 ms (`uncertainty_evidence.py:65-83`). v3.1 removes the conflict at its source.

## 4. Pre-mortem errors

1. **"A real resync step … is still caught" under (a)** is false right after G10 (Q2). This matters most.
2. **(a) without (b) moves the failure later and makes it costlier.** A 12 ppm draw arms, and 12 ppm × 140 s = 1.7 ms on top of H 3.6 ms gives `unknown`, then END STATE instead of a cheap NULL at arm. (b) is not optional.
3. **"A 300 s backoff exceeds 5 ms even at −3.17 ppm with h = 3.6 ms"** pairs a short-stream half-width with a 560 s stream. The anchor is a set-membership intersection, so more records only narrow it or refuse. The case is marginal (at worst 5.4 ms), not proven.
4. **0.46 rests on n = 2 retries.** An immediate retry inside a burst should nearly always fail, so 0.46 may be low; that favours (e).
5. **"About 440 s of stream at −3.17 ppm"** (C2) holds only for that draw; the frequency gate is what makes it hold on a given night.

**Bottom line:** idle 75 s; F_max 5 ppm with one redraw; the residual and frequency-equality T-0 check; clause (e); (d) or v3.1 in block 5.
