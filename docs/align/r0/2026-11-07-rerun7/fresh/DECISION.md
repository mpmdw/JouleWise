# SMC sensor selection for ALIGN R0/R1 on Mac15,9: reconciled decision (proposed)

Magistrate activation a9031916, 2026-11-07 about 02:40 PST, on Ed's 01:34 instruction ("of course
continue work on getting this right ... sol xhigh claude 5.5 and fable 5.1 should be doing fresh
designs").

Inputs:
- Three blind fresh designs: `sol-DESIGN.md` (Sol 6.1 xhigh), `opus-DESIGN.md` (Opus 5.5) and
  `fable-DESIGN.md` (Fable 5.1).
- Two earlier amendment-framed seats in `../consult/`.

All five seats executed on the re-run 7 journal (sha256 `16aa5307…4984`). Status: the lead's
reconciliation. It changes which sensors count, so Ed sees it before the build starts.

## Why the current rule fails on this Mac (all five seats, verified by the lead on raw data)

- **The "die" class has no real member.** No key that reads continuously at idle heats to 63% within
  5 s. Only the 32 power-gated `Tg*` GPU keys are that fast, and they read a fixed placeholder (0.0,
  -0.5, -2.75, -8.75 or -9.0 degC) on about 95% of idle and recovery samples.
- **The placeholder defeats the gates.** G0, G1 and H all evaluate while the GPU idles, so a
  placeholder always passes the band test and the fast band controls nothing.
- **The idle baseline was not settled.** Idle followed R0's 12-minute model load, and the machine was
  still cooling at 0.5-1.0 degC/min. The whole-idle median overstated baselines by 1-2 degC, and the
  "noise" was the cooling trend (TaRT 1.14 against a settled 0.042 degC).

## Decided by agreement (the build implements these)

**D1. Placeholder and non-temperature rejection.** A key is not selectable if either holds:
- (a) Any reading in idle or recovery is below 10 degC.
  - Derivation: Apple's operating minimum ambient for this MacBook Pro is 10 degC (Opus seat, from
    Apple's specification page). A powered component cannot read below ambient.
  - This catches the zero-valued placeholders that a "below 0" rule misses.
- (b) Its largest one-second change exceeds half its step rise.
  - Derivation: a first-order response does that only with tau < 1/ln 2 = 1.44 s, which a 1 Hz
    sampler cannot resolve (Fable).
  - This catches a placeholder whose value happens to be positive on another machine.
- Replay: (a) removes all 32 `Tg*` keys plus about 40 constant or virtual keys. (b) removes TCMz, the
  flickering `Tp*` keys and the clamp jumpers. Neither removes a key with a real positive response.
- A pinned floor or ceiling clamp is flagged and excluded from the picks only (Fable P3).

**D2. Baseline and noise.**
- Baseline: median of the last 60 s of idle, the same window as the window reference R
  (`capture_reference`).
- Noise: SD of the OLS residual over that window.
- The stale rule (at least 3 distinct idle values over the whole idle) is unchanged.

**D3. Settled idle.** The R0 SMC step runs first, before the weights hash and any model load.
- Idle lasts at least 300 s. It continues until every key that passes D1(a) and the stale rule on idle
  data has |OLS slope over the last 60 s| <= 0.2 degC/min for 10 consecutive 1 s evaluations. Those
  are G0's bar, window and count.
- Cap: 1,200 s, from the Opus seat's measured settle times on this capture (median about 930 s, max
  1,038 s after the GPU step).
- At the cap the step proceeds, and each unsettled key carries `baseline_unsettled` with its slope.
  This is a flag, not a refusal: R0 picks are provisional and R1 re-selects.
- Load (900 s) and recovery (600 s) are unchanged.
- Cost: 0 to +900 s of R0 time. The next run measures it.

**D4. Fast role.** Selectable keys (D1), resolving (rise >= 3.0 degC = 3 x the 1 degC band floor, and
rise and rise60 > 3 x noise floor), with cooling tau <= 60 s and settled noise <= 1/3 degC (3 SD within
the 1 degC band floor).
- Pick: the largest rise, lexical ties.
- On this capture: Tf18 (rise 45.7 degC, tau 24.7 s, noise 0.06 degC).
- The pick does not move for any boundary between 30 and 75 s (Fable) or at 47 s (Opus).
- Sol's tracking rule picks TCMb, a die-path key of the same kind (0.054 degC RMS from the active
  GPU maximum). TCMb is printed as a diagnostic beside the pick.

**D5. Slow role.** Selectable, resolving as in D4, 60 s < cooling tau <= 300 s, settled noise <=
0.15 degC.
- Noise derivation: the G0 slope test uses OLS over 60 one-second samples, so SD(slope) = 0.447 x
  noise degC/min. Making 3 sigma <= 0.2 needs noise <= 0.15.
- The default pick, provisional, is the longest band hold time tau x ln(rise / 1 degC) that is still
  <= 300 s (Fable). It ties the pick to G1/H's 300 s cap. TaLP on this capture.
- The build also prints, beside it:
  - the design-literal pick (longest tau);
  - Opus's pick (most stored heat in band units at 5 x tau of the fast pick): TSXR;
  - Sol's pick (longest resolved cooling after the fast key's bracket): TVS0.
- **The slow rule is chosen on the first settled R0 capture.** All five seats agree this capture cannot
  decide it.

**D6. Receipt.**
- `r0_host` reads each pick's classifier row: per-phase coverage >= 0.99 at the one-cell (NS // 2)
  tolerance, read errors < 1%, total phase time >= 600 s, longest interval between valid readings
  <= 2 s (U1(c)).
- The capture-wide 100 ms block becomes a diagnostic. summary.md prints the quantity the receipt reads.
- PR #692's coverage change and its nits are included.

## Not built here: findings for the R1 lane (laptop lead)

- After the 900 s full load, no physical key reaches G0's 0.2 degC/min until 840-1,040 s after load
  end, but G0's cap is 600 s (Opus). R1 should measure G0 waits in the real member cycle.
- The replayed G1 release came at 279 s, near the 300 s cap (Opus).
- R1's planned 10-minute cooldowns are shorter than D3's settle times (Opus).
- Once the fans stop (180 s after the load), every key cools on one shared slow mode, tau about
  430-510 s (Opus).
- Sol: TCMb and TVD0 are identical in all 1,800 rows. Tf24/Tf2D/Tf2E are one sensor under three keys
  (Fable). Aliased keys must never count as independent thermometers.

## Plan

1. Build D1-D6 onto #692: Sol 6.1 xhigh builder, with the real journal replayed through `rank` and
   the receipt.
2. Gates: Fable and Opus blind executing cold passes, then CI.
3. Merge into `lane/2026-11-05-align-pilot10-benign` and fast-forward the measurement checkout.
4. Run one R0 in a clean gap. The slow-rule choice uses that settled capture.
