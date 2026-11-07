# SMC classifier for R0/R1 on Mac15,9: two-seat consult and lead recommendation

Magistrate activation a9031916, 2026-11-07 about 03:30 PST. Inputs: two blind seats, Sol 6.1 xhigh
(`sol-PROPOSAL.md`) and Fable 5.1 (`fable-PROPOSAL.md`), from `BRIEF.md`. Both executed on the
re-run 7 journal (sha256 `16aa5307…4984`). Background: `../NOTE.md`; PR #692 and its two cold reviews
(`pr692-*-REVIEW.md`). This is a recommendation. The decision belongs to Ed or the laptop lead
(RUN_STATE item 185 (3)), because it changes which sensors the windows gate on.

## What the windows need from the two keys (both seats agree, from thermal_gates.py and FINAL-DESIGN 2.6)

- **s_fast:** sheds a load excess into a 1 degC band within G1's cap (S6 target: 90 s median wait).
- **s_slow:** carries the machine's slower state between members. It is the key in the G0 slope test
  (|OLS slope over 60 s| <= 0.2 degC/min) and in U2/U5.
- **Both:** must read a real temperature at idle, because the reference R is their idle-end median.

## Where the seats agree (recommend adopting as written)

1. **Placeholder series are not temperatures.** The 32 `Tg*` GPU keys sit on one exact code while the
   GPU is powered down and copy a CPU die reading when it is on. Each seat gives an observable,
   sign-independent rule:
   - Fable: refuse any reading <= 0 degC, and refuse a largest one-second change greater than half the
     step rise (a first-order response does that only with tau < 1.44 s).
   - Sol: refuse a majority modal code in idle and recovery with a one-step reset into it.

   Both remove all 32 `Tg*` keys and no key with a real positive response. **Recommendation:** Fable's
   pair (simpler, each with a one-line physical derivation). Sol's reset rule goes in as a test fixture
   it must also catch.
2. **Baseline from the end of idle, not the whole idle.**
   - The idle phase followed R0's 12-minute memory check, and the machine was still cooling. TCMb fell
     63.1 to 49.4 degC during idle, so the whole-idle "noise" was drift: TaRT 1.14 against a detrended
     0.042 degC.
   - Baseline = median of the last 60 s of idle; noise = OLS-residual SD over that window. This is the
     same window the sidecar uses for R.
3. **Settledness is checked with the G0 number:** |last-60 s idle slope| <= 0.2 degC/min. On this
   capture almost no class member passes (Fable: 42 of 45 fail; Sol: the candidate pair fails).
4. **Fast class: cooling tau <= 30 s.** Three time constants in the 90 s S6 target. Plus a resolved
   response (dT and dT60 > 3 x noise floor) and noise <= 1/3 degC (3 SD within the 1 degC band floor).
   This admits the real CPU-cluster keys. Both seats' fast candidate is `Tf18` (dT 45.7 degC, t63
   18.9 s, tau 24.7 s, noise 0.06 degC). Tf2B/Tf24 are the same kind; TCDX and TCMb are close behind.
5. **Slow keys need a noise gate.** TaRT's rise at 50-60 s is 0.06 degC, inside its noise. Fable
   derives a decidable G0 slope test: SD(slope over 60 one-second samples) = 0.447 x SD degC/min, so
   3 sigma <= 0.2 needs **SD <= 0.15 degC**.
6. **The receipt reads the classifier's own per-phase coverage** (the NS // 2 phase-grid numbers in each
   pick's row), plus the 600 s total from `phases`. The capture-wide 100 ms block becomes a diagnostic,
   and summary.md prints the same quantity the receipt reads. This is Fable F1 on #692.
7. **This capture cannot give a valid selection.** With the baseline fixed, the slow-class tau values
   are biased by the still-cooling machine, so the slow pick is undetermined. Both seats say: measure
   on a settled idle first.

## Where they differ, and the lead's recommendation

| Question | Sol | Fable | Recommendation |
|---|---|---|---|
| Slow class lower bound | 30 s < tau | 90 s < tau (keeps most state across one fast settling time, 3 x 30 s); 30-90 s recorded as intermediate | **90 s.** It is derived from what G1/G0 need; 30 s only reuses the old boundary. |
| Unsettled baseline | refuse the selection | flag `idle_unsettled`; picks prefer settled keys | **Flag, plus fix the cause** (next row). R0 picks are provisional and R1 re-selects. An unsettled pick prints as PROVISIONAL-UNSETTLED. |
| How to get a settled idle | extend idle; measure the dwell first | **run the SMC step first in R0, before any model load** (zero added time); else a 900 s dwell (3 x the 300 s class bound) | **Reorder.** This is a protocol change to Amendment 1 A5 step order, so it is part of the decision. |
| Slow pick rule | longest tau (design) | NEEDS_RULING: (a) design literal, longest tau with dT >= 3 (lands on the smallest, least certain keys); (b) longest tau with dT >= 6 degC (twice the U2 3 degC range); (c) largest dT in (90, 300] s, with clamp exclusion | **Decide after one settled R0.** Print the (a), (b) and (c) outcomes side by side; lean to (b), because U2 cannot fail on a key whose whole step rise is 3 degC. |
| Fast bound 30 vs 35 s | 30 | 30 (35 admits TVH3 with a 46% longer release) | **30 s.** |

## What gets built after the decision (one lane, onto #692 or a successor)

- `rank`: P1/P2 placeholder refusals; end-of-idle baseline and residual noise; the fast and slow class
  definitions above; the `idle_unsettled` flag; the floor-clamp flag (Fable P3) excluding a key from the
  picks only; a printed slow pick under each of (a), (b) and (c).
- `r0_host` receipt reading the classifier's per-phase rows; `align_smc_enumerate.py` printing the same
  quantity; the #692 nits.
- R0 step order: SMC before the weights hash and model load (Amendment 1 A5).
- Tests: production-shaped synthetic captures, including a placeholder key, a still-cooling idle and the
  403-key read jitter, through the real `rank` and the receipt. Replay on this journal: the fast pick
  should be Tf18 or its family, and the selection should be flagged unsettled.
- Gates: executing review, Fable and Opus blind cold passes, CI. Then one R0 re-run in a clean gap.
