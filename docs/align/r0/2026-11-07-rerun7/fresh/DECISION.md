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

## Erratum 1 (02:59 PST, lead ruling on the build seat's NEEDS_RULING F1)

**D1 (c).** A key is not selectable if any valid reading over the whole capture is above 125 degC.
- Derivation: 125 degC is the standard absolute-maximum junction rating for silicon. A reading above it
  is not a component temperature on a running machine. The composite max-die key TCMb peaked at
  85.5 degC, and the hottest plausible real key (TCMz) at 112 degC.
- Fable's fresh design (P3) proposed this ceiling; the reconciliation left it out by omission.
- Under literal D1-D6 the build seat found TVH3 winning the fast pick: rise 64.1 degC, max reading
  137 degC. Fable measured TVH3 = 1.72 x TCMb - 38 (R^2 0.98), a firmware-derived value, not a
  thermometer.
- With D1 (c), the replay gives Tf18 / TaLP, with alternatives TaRT / TSXR / TVS0, as DECISION.md
  expected.

## Erratum 2 (03:35 PST, lead dispositions of the two cold passes on c0c460fd9)

Both cold passes returned ADMIT_WITH_FIXES (Fable 5.1 and Opus 5.5, blind and executing). Reviews:
`cold2-fable-REVIEW.md` and `cold2-opus-REVIEW.md`.

- **D1 (d), heat ordering** (Fable F1; the rule is from the Opus fresh design).
  - The rule: among keys that pass D1 (a)-(c) and resolve, take the one with the shortest cooling tau
    (lexical ties). Exclude from the picks any key whose rise exceeds that key's rise by more than
    3 x that key's noise floor.
  - Derivation: the fastest-responding key is the one closest to the heat source. Under one step, no
    key farther along the conduction path can rise more than the source does. The 3-floor margin is
    the resolution bar D4 already uses.
  - On this capture it removes only TVH3 (rise 64.1 against Tf18's 45.7). D1 (c) stays as a backstop.
  - Without this rule, a step 15% lighter than the matmul makes TVH3 the fast pick (Fable, executed).
- **D3, the settle set** (Fable F2, Opus F1).
  - Fault: waiting on every key that passes D1 (a) and the stale rule includes flicker keys (residual SD
    3-8 degC) that D1 (b) only removes later. Their 60 s slopes never pass, so idle always hits the
    1,200 s cap and records settled False.
  - The new set: keys that pass D1 (a), the stale rule and D1 (b) on the idle data so far, with trailing
    60 s residual SD <= 0.15 degC. That is the noise at which the 0.2 degC/min slope test is decidable
    at 3 sigma, the D5 derivation.
  - If no key qualifies, the phase records `settle_keys: 0` and settled is null (indeterminate), not
    True (Opus F6).
- **D6, readings with holes** (Fable F3, Opus F2).
  - The bar is restated in grid cells: a pick may not have two consecutive empty 1 s cells within a
    phase. It is checked per phase, so the idle-to-load handshake is not a hole.
  - It moves into `rank` eligibility, so a key with such a hole loses its role and the next key is
    picked. The receipt re-checks the same per-phase quantity.
  - Derivation: the coverage bar is defined on 1 s cells. One missed read leaves one empty cell, which
    the 99% bar already admits. Two consecutive empty cells mean the reader lost at least 2 s, the U1 (c)
    window bar.
  - The seconds bar goes.
- **Phase-duration check** (Fable F4, Opus F5): a phase that differs from its configured length by more
  than 1 s is a recorded flag, not a refusal.
- **An SMC inconclusive does not stop R0** (Opus F3). With SMC first, `inconclusive` from smc is recorded
  and the host, disk and model checks still run: they do not depend on the selection. `fail` from smc is
  unchanged.
- **Labels and numbers** (Fable F5-F7, Opus F4 and the number list):
  - `design_literal` says it applies the band-hold cap.
  - The D1 (b) reason is stamped only on keys with a positive rise.
  - `CLAMP_DISTINCT = 10` gets its derivation (Fable fresh P2: with 10 or more distinct values,
    quantum << noise, so one value holding 40% is a clamp) or goes.
  - The vacuous `>= 600 s` check is removed or justified.
  - The SMC journal estimate is corrected to the measured size per sample (about 53 KB, not 16 KiB),
    so the disk budget is right.
- **Deferred to the R1 lane:** aliased and virtual keys (TCMb = TVD0, Tf24 = Tf2D = Tf2E, TVV0). D1 (d)
  does not remove an exact copy. The R0 picks print their aliases, and R1 must not count aliases as
  independent thermometers.

## Erratum 3 (03:40 PST, lead ruling on the fix seat's NEEDS_RULING)

**D1 (d), the reference key.** The reference is the key with the shortest cooling tau among keys that qualify
for the fast role under D4: selectable under D1 (a)-(c), resolving, tau <= 60 s, noise <= 1/3 degC, and not
clamp-flagged. Lexical ties.

Derivation: the ordering argument needs the reference to be a real thermometer near the source. A key too noisy
for the fast role, such as the flicker key Tp0M, cannot anchor it. With every resolving key allowed as the
reference, Tp0M became the reference and the fast pick moved to Tf48. With role-qualified references the replay
keeps Tf18 / TaLP.

## Erratum 4 (about 04:10 PST, lead dispositions of the two delta reviews on eb6e8e493)

Both delta reviews (Fable 5.1 and Opus 5.5, blind and executing) returned ADMIT_WITH_FIXES. Every Erratum 2/3
fault is reproduced on the parent and gone at the head. The real capture gives Tf18 / TaLP, and the receipt
passes. Reviews: `cold3-fable-REVIEW.md` and `cold3-opus-REVIEW.md`.

- **D1 (d) rebuilt** (Fable H1, Opus M1 and N1).
  - Fault, executed by both: the reference was the argmin of a cooling tau measured from the first recovery
    read. Eight Tf keys lie within 1.1 s of each other. The fast keys drop about 6 degC in the first
    second, and the margin was 0.16 degC. As a result:
    - a first recovery read one cell late, or a +1.3 s load overrun, moves the reference to Ts0h or TV0m
      and excludes the whole Tf family (Fable);
    - one admitted missed read of Tf2B excludes Tf18 and Tf2B (Opus).
    - In each case the receipt still prints pass.
  - New rule, in three parts:
    1. **Reference cooling time** (stable threshold): the first crossing of baseline + rise/e, where rise is
       the load-tail median already computed, timed from the load phase's actual end. Neither the threshold
       nor the origin depends on when the first recovery read lands (Fable).
    2. **Reference rise:** the largest rise among D4-qualified keys (Erratum 3) whose stable cooling time is
       within 1 s of the shortest. 1 s is the crossing resolution at 1 Hz (Opus).
    3. **Margin:** 1.0 degC, the band floor, the smallest temperature difference the gates resolve. The 3
       noise floors measured one sensor's noise. The question here is the gain and offset spread between
       sensors (Opus N1), which is 0.46 degC across the co-located Tf keys.
  - A key whose rise exceeds the reference rise + 1.0 degC is excluded. On this capture that is TVH3 only
    (64.1 against 45.68; 54.5 at a 0.85 step).
  - The class tau (D4/D5) is unchanged. The stable cooling time is printed beside it.
- **The receipt and summary print the D1 (d) reference, its rise and the excluded keys** (Fable L2).
- **Settle set:** the idle D1 (b) half-range term is dropped (Opus M2).
  - For stationary noise the largest one-second jump (about 4.9 sigma) always exceeds half the range (about
    2.75 sigma). The term therefore emptied the set on a settled machine and blinded the D3 cost
    measurement.
  - The 0.15 degC noise bar alone removes the flicker keys (3-8 degC).
- **An empty settle set** (Fable L1) ends idle only after 10 consecutive evaluations with no settle key (G0's
  confirmation count). settled stays null.
- **complete_r0 needs smc pass** (Opus L1). smc `inconclusive` still lets the other checks run, but the report
  records `smc_selection_missing` and complete_r0 is False.
- **Cells end at the phase deadline** (Opus L2 and N3).
  - Coverage and empty-cell counts stop at the configured deadline (for adaptive idle, the evaluation that
    ended it). Exit overrun lies outside the reader's grid, like the handshake.
  - The phase-length flag stays at 1 s.
- **Documented, not changed** (Fable M1, Opus L3): fast-role keys with noise in (0.15, 1/3] degC are not waited
  on, because the 0.2 degC/min test is undecidable for them at 3 sigma. rank still flags their
  `baseline_unsettled`. Opus L3's decidable-drift option is deferred to the R1 lane.
- **Docs and wording:**
  - `r0_desk_runbook.md:153` gets Erratum 3's reference (Opus L5).
  - The CLAMP_DISTINCT comment: 10 or more distinct values in about 300 reads means sigma >= about 1.8q, so the
    non-clamp mode fraction is <= 0.22, under the 0.40 bar (Fable L3, Opus N2).
- **Required replays, written beside the rule** (acceptance-rule requirements): the real capture;
  recovery_delay 0.3 and 1.0 s; overrun_load 1.3 and 1.6 s; scale 0.6, 0.85 and 1.2; a missed read of
  Tf2B at recovery 0 and at load 236-237. Record the D1 (d) exclusions for each. Expected: TVH3 only, with
  Tf18 the fast pick or a Tf sibling where a D6 hole removes Tf18.
