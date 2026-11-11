# The slow role: design round (RL-75, with RL-76)

Date: 2026-11-11 (PST). This is the round ordered by research-lead ruling RL-75, with RL-76's additions. It had two
seats:

- **Opus seat:** this file, on `design/2026-11-11-slow-sensor-rule`.
- **Sol seat:** `docs/run_reports/2026-11-11-slow-sensor-rule-design-sol.md`, on
  `design/2026-11-11-slow-sensor-rule-sol`.

This file is the one plan. Section D lists the disagreements with both positions, and section E the questions for the
research lead. The Opus analysis in sections 0 to 6 was committed (`c0477f3d9`) before the Sol plan (`6a4d9c79e`) was
read. Section 7 records what was taken from Sol afterwards.

**Inputs.**

- RL-72, RL-74, RL-75 and RL-76.
- The E1 thermometry print, `r1-thermometry-e1.md`. This includes its RL-74 section, the step-30b G0 replay on the
  candidate keys, which is a diagnostic because the coverage bar is waived at 0.797.
- WP14(a) only (`docs/align/pilot_protocol_v4.md:223-254` on the W1 line).
- R1's gate journals (TV0h and Tf08 at 1 Hz), read through `scripts/align_r1_thermal_replay.py`. It is extended here
  with `--key-roles`: two tests added, 21 in the module, all passing.
- Code on the W1 line @ `b4a6c217f`.

**Blinding.** Only temperatures, times and counts are used. There are no energy, power, token or decode-duration
values, and no v4 outputs.

---

## 0. What the data say

**Every key's last degree follows the slow mass. The keys differ in when their own fast part stops deciding.**

Table 1 gives the 30B step, from the E1 RL-74 replay. The fast key is TV0h at 1.0 °C. Each reference is the key's own
pre-warmup median.

| slow key | δ_slow | release s | decided by | slope alone / bands alone s | s per 0.01 °C of reference | equivalent Tf08 band ‡ |
|---|---|---|---|---|---|---|
| Tf08 | 1.0 | 1,007 (censored at −0.026 °C) | band | 540 / 1,007 | ~7 model †; release lost at −0.026 °C | 1.0 |
| Tf08 | 1.5 | 715 (739 at −0.026 °C) | band | 540 / 715 | 9.2 measured (−0.026 °C) · 2.4 (±0.05 °C, symmetric) · 4.8 model † | 1.5 |
| TV0s = TV1s | 1.0 | 672 | band | 478 / 672 | ~6.0 model † | ≈ 1.7 |
| TV0s = TV1s | 1.5 | 478 | slope (band 51 s earlier) | 478 / 427 | 0 within ±0.13 °C | ≈ 2.6 |
| TV0m | 1.0 | 430 | band | 343 / 430 | ~3.8 model † | ≈ 2.6 |
| TV0m | 1.5 | 343 | slope (band 69 s earlier) | 343 / 274 | 0 within ±0.27 °C | ≈ 3.9 |
| TV0h = TV1h (proxy only; an alias cannot fill both roles) | 1.0 / 1.5 | 183 | slope | 183 / 84 | 0 | ≈ 10 |

† **Model.** The local tail time constant comes from the two band-alone times:
τ_tail = Δt / ln(1.5/1.0). It is 720 s for Tf08, 604 s for TV0s and 385 s for TV0m. The sensitivity follows as
τ_tail × 0.01 / δ. The measured Tf08 values bracket the model, because the release needs 10 consecutive samples and
so moves in steps.

‡ **Equivalent Tf08 band.** δ divided by the key's excess relative to Tf08's at 600 s of recovery. Those ratios are
0.578 for TV0s, 0.383 for TV0m and 0.096 for TV0h (E1 "rec. excess at last read"). The column gives the depth of the
slow mass the key's band actually holds.

Table 2 gives the nine D members' post-warmup cooldowns, from R1's journals. They are passive, with no heater. Each
reference is the member's own capture.

| pair | δ_slow | release s | decided by | s per 0.01 °C (±0.05 °C) |
|---|---|---|---|---|
| TV0h / Tf08 | 1.0 | 873–1,049 | band (A2: joint) | 0.0–4.9 |
| TV0h / Tf08 | 1.5 | 728–878 | joint (slope alone 578–723, bands alone 702–801) | 0.0–5.2 |
| TV0h / TV0h (proxy) | either | 201–208 | slope | 0 |

**Three further observations.**

1. **The classifier's τ depends on the pulse.** After the D warmup's short pulse (about 40 °C on Tf08), Tf08's 1/e
   crossing comes at 43–46 s, which would class it `die`. After the 30B step it comes at 140 s. Its return to within
   1.0 °C still takes 773–930 s on D.

   The registered test τ·ln(rise/1 °C) assumes a single exponential. On D it predicts 44 × ln 39.7 = 162 s against
   the 773–930 s observed.

   On the 30B step it also fails to describe the keys it admits. At 600 s of recovery, TV0m is still 1.46 °C above
   baseline and TV0s 2.20 °C, although the test says each returns within 1 °C in under 300 s. Only the TV0h family
   (0.36 °C) is actually back. The test is an extrapolation, and the slow class it defines, 60 < τ ≤ 300/ln(rise), is
   a window of about 15 s at a 56 °C rise. Keys sit on both sides of it, depending on the sampler (TV0m 60.2 or
   58.0 s, TV0s 78.3 or 66.6 s).
2. **The duty bar caps G0 below 617 s.** The bar is gate_hold = G0 + G1 + H ≤ 0.40 × duty T_dead, with
   T_dead ≤ (1,750 − I_D)/1.13544 < 1,541 s (`align_r1_rehearsal.py:771-777`, `:1512-1535`). So a gated run whose
   G0 alone exceeds 616.5 s fails the bar whatever else happens. In W1 every D member's G0 is a cooldown from its own
   warmup, like the ones in Table 2.
3. **A G1 that does not release ends the episode.** `workload.py:539-542` breaks out of the turn loop when the outcome
   is not `released` or `unobserved`. The G1 and H turn cap is 300 s, and their reference is the G0 release
   temperature plus δ. Tf08 heats fast (t63 23 s on the 30B step) and needs 655–805 s to come within 1.5 °C after a
   warmup-sized pulse, so a turn of that size makes a Tf08 G1 time out and ends the member.

**The framing (RL-76), answered.** There are three properties a slow-role gate can have:

- it sees the slow mass: it is band-decided in the slow tail;
- it is stable: low reference sensitivity, and a pick away from the class boundaries;
- it is feasible: G0 at or below about 616 s, and G1/H inside 300 s.

On this machine, at this step size, **no key has all three**. Every gate that holds the slow mass to an equivalent
Tf08 band of about 1.7 °C or tighter costs at least about 670 s of G0, which breaks the duty bar. Every gate that
fits the duty bar is decided by the slope, or holds the slow mass only loosely (an equivalent Tf08 band of about
2.6 °C or wider). The choice is therefore which property to give up, and it should be made on purpose.

---

## 1. Option 1: the registered rule as it stands, slow pick from the fast family

**Pick.** On D the slow pick is whatever the D step yields among TV0m, TV0s and TV1s, or nothing. The pick is
unstable, because both candidates sit on a class boundary. The band starts at max(1.0 °C, 3 × soak SD), so 1.0 °C,
and S6's Tf08 receipt does not carry over (RL-74).

**Waits, from the 30B record.**

| slow key | δ | G0 release | decided by | duty bar |
|---|---|---|---|---|
| TV0s | 1.0 °C | 672 s | band; ≈ Tf08 at 1.7 °C; about 6 s per 0.01 °C | fails (> 616 s) |
| TV0m | 1.0 °C | 430 s | band; ≈ Tf08 at 2.6 °C; about 4 s per 0.01 °C | passes |
| either | 1.5 °C | 343–478 s | slope; insensitive to the reference | passes |

- **G1/H.** These fit 300 s on TV0h. On the V-s keys they are uncertain after a large turn, because TV0s is still
  2.2 °C up at 600 s on the 30B step.
- **Cap.** G0_cap_W1 is about 840 s for TV0s at 1.0 °C, and the 600 s floor otherwise.

**What W1's control means.** It holds the die and near-die state. At 1.0 °C with TV0s it holds the slow mass to about
Tf08 + 1.7 °C, and does not otherwise.

**Deviation.** None to the classifier. RL-75 requires the pick to come to the lead, because it is an R0-fast key.

## 2. Option 2: an amended return-time test that admits a truly slow key

- **2a. Return to the gate's band:** τ·ln(rise/δ) ≤ 300 s. Tf08 gives 140 × ln(55.8/1.5) = 506 s, so it still
  fails. A slow key passes only if its rise is at most δ·e^(300/τ), which is 12.8 °C for Tf08. This does not do what
  it is meant to.
- **2b. Return against the G0 cap:** τ·ln(rise/δ) ≤ 1,200 s. This admits Tf08 (565 s at δ = 1.0, 508 s at δ = 1.5),
  but the registered slow tie ("longest band hold") then picks the deepest admissible key, not Tf08: TVFm (817 s)
  at 1.0 °C, or TVS2 (1,031 s; rise 9.2 °C, τ 570 s) at 1.5 °C. Landing on Tf08 needs a further criterion, such as
  largest rise among slow keys. Every such criterion is a choice of key. It must be made blind and stated as one.
- **2c. Measure the return instead of extrapolating it:** the observed time to within δ of baseline in the 600 s
  recovery. At 1 °C only the TV0h family qualifies on the 30B step, so the slow role is null, and the IOHID/X4 ruling
  applies. This is the honest form of the registered test, and it shows the slow role cannot exist at this step size.

**Consequences if Tf08 gates (2b with a Tf08-selecting tie).**

- **G0:** 728–878 s at 1.5 °C and 873–1,055 s at 1.0 °C on D. These are band-decided or joint, with 0–9 s per
  0.01 °C.
- **Cap:** G0_cap_W1 is about 1,098 s at 1.5 °C, and saturates at 1,200 s at 1.0 °C.
- **Duty bar:** it fails on G0 alone for every gated run.
- **G1:** after a heavy turn it cannot return within 300 s, so the episode ends after its first turn.
- **What follows:** the registered fallback order starts at once. Even at δ = 2.0 °C, the G0 cannot release before the
  slope bar, which takes 578–723 s on D. That is above the 616 s limit for four of the five passive members. That leaves
  in practice only the later rungs: idle 450 s, then 4-bit, then screen-only.
- **What W1's control means:** tight control of the slow mass, and heavy cells that cannot run. These are the long
  waits of the last two nights, made permanent.

## 3. Option 3: one family gates, the other is recorded for every member

- **3a. The fast family gates; Tf08 is recorded.** This is Option 1's gate, so it has Option 1's waits, duty bar and
  cap. Each member also records Tf08's start excess over the window reference, so the analysis can test balance
  between conditions and disclose it.
- **3b. Tf08 gates; the V key is recorded.** This has Option 2's consequences, plus a hand substitution that WP14(a)
  forbids ("no manual sensor substitution"), so it needs a deviation.

**Expressible by policy data alone? No, for either.** `thermal.validate_policy` (`joulewise/align/apple/thermal.py:22-37`)
accepts exactly `{s_fast, s_slow, fan_keys, r0_sha256}`, and `fan_keys` must match `F?Ac`. No third temperature key
can be journalled through policy. Recording one needs an additive bound edit to `thermal.py`: an optional
`record_keys` list of `T???` keys that `keys()` journals and the gates never read. `thermal_gates.py` stays
byte-identical.

RL-74(c) says that such an edit "is not done, and the builder says so" if it is in the gate module. `thermal.py` is
the sidecar module, not `thermal_gates.py`. Whether this edit counts is the lead's call (E3). In R1 itself, the
fixed full-inventory journal already records every key around the step members, but only those.

## 4. Recommendation (Opus)

**Option 3a with Option 1's registered pick, armed at the registered default band, and an honest name for the slow
role.**

1. **The gate pair is the registered classifier's D picks**, by RL-74 outcome 2 or 3, ruled per RL-75. The slow role is
   described in the methods as **"the near-die settling check"**: it guarantees that a member starts with the
   fast-responding masses settled. It does not guarantee the heatsink's state. Arm δ_slow at the registered default.
   If the gated G0 breaks the duty bar, the registered fallback, step 1 (S6 tuning, capped at 2.0 °C), takes it to
   1.5 °C. The night's desk replays both bands from the journals, so nothing more is measured to decide.
2. **Tf08 is recorded in every W1 member**, through the `thermal.py` `record_keys` edit (E3). The desk prints each
   member's Tf08 start excess over the window reference. A pre-declared disclosure compares it between conditions
   within each window. If the edit is refused, the methods say the slow mass's start state is unrecorded in W1 and
   recorded only in R1.
3. **Not Option 2.** It buys slow-mass control at the cost of every heavy cell, through the duty bar.
4. **Why not Tf08 at a looser band?** At 2.0 °C its G0 still cannot release before the slope bar, 578–723 s on D. That
   is above the duty limit for four of five members. Loosening the band on Tf08 does not buy feasibility.

**Deviation row text** (blind, against WP14(a), before signing):

> **WP14(a)-R1-SLOW.** On Mac15,9 at the registered R1 step (10k-fed prefill + 4,096 decode), R0's slow pick Tf08 fails
> the registered return-time rule (τ 140 s; τ·ln(rise/1 °C) = 565 s > 300 s; E1 print, RL-74). R1's selection is the
> registered classifier's, unchanged, on the D step of the pre-night smoke. Its slow pick is a key R0 classed fast. It
> is entered as the slow role, under the name "near-die settling check": with the fast pick it controls the
> fast-responding masses at G0, G1 and H. It does not control the heatsink mass. The heatsink key Tf08 is journalled
> record-only in every member (`thermal.record_keys`, an additive sidecar edit; the gate module is unchanged), and its
> start excess over the window reference is printed and compared between conditions as a disclosure. No key is
> substituted by hand. Aliases do not fill both roles. Decided before any v4 window, blind to all v4 data (RL-75).

**Alternative row, if the lead chooses Option 2** (shown for completeness, not recommended):

> **WP14(a)-RETURN.** The D4/D5 return-time term becomes τ·ln(rise/δ_role) ≤ the armed G0 cap, and the slow role is
> chosen by largest rise among admissible slow keys [or: R0's slow pick if admissible]. Per-turn gates and the duty
> bar are then infeasible for heavy cells, and the registered fallback order applies before W1.

## 5. What smoke Part B's D table must show to decide

Part B is step-D natively, with the fixed sampler, and the full inventory, classified by the unchanged rule. The table
must show the following.

**0. Sampler bar.** Every phase meets the bar: the pre-warmup idle (RL-76), quiet, load and recovery. That is ≥ 99 %
of one-second cells, < 1 % read errors and no two empty cells in a row. The pre-warmup capture coverage is ≥ 0.9, so
every key's reference is a registered capture. If this fails, nothing below counts.

**For each key** (TV0h, TV1h, TV0m, TV0s, TV1s, Tf08, and whatever the classifier picks), it reports:

- **Classification:** class, τ (1/e), rise, t_band, and the τ margin to the 60 s boundary and to 300/ln(rise).
- **Settling:** the excess at 600 s of recovery, and its ratio to Tf08's.
- **The three RL-76 terms, from a G0 replay on the smoke's own journal** (TV0h fast, each candidate as slow, own
  capture, at δ 1.0 and 1.5 °C): the release time; which condition decides (band, slope or joint); and the release
  shift per 0.01 °C of reference, by ±0.05 °C replays.

**Then, pre-declared:**

| D table shows | outcome |
|---|---|
| The slow pick is Tf08: its t_band on the D step ≤ 300 s | RL-74 outcome 1. R0's picks; arm as planned |
| The slow pick is a V key, with a τ margin ≥ 5 s at both boundaries, unaliased with the fast pick, and a G0 at the armed δ ≤ 616 s (gated-run duty limit) | Option 3a as recommended. Gate on it; record Tf08 |
| The slow pick is a V key, but its G0 at δ = 1.0 exceeds 616 s, while at 1.5 it is slope-decided and ≤ 616 s | Option 3a, armed at δ_slow 1.5 under fallback step 1 (S6 tuning), with a receipt citing this table |
| The slow pick is null, or within 5 s of a boundary, or differs from the 30B diagnostic's TV0m/TV0s | **Lead.** The rule cannot fill the slow role stably. Choose Option 3a with a pre-declared deterministic slow key (largest τ among R0-classified, unaliased keys with τ·ln(rise) ≤ 300 s on the D step), or Option 2. No night arms first |

Two further rules:

- **Stability check.** A V-key pick also needs its band-decided sensitivity ≤ 6 s per 0.01 °C at the armed band.
  Otherwise the reference noise of a 60 s median (about 0.01 °C) moves the release by more than a sample window.
- **Smoke vs night.** If the night's step-D classification differs from the smoke's, the registered pick-change rule
  applies and the case goes to the lead (RL-74 outcome 2).

## 6. Build-side note (RL-76): the sampler

The stall happens before warmup as well as in recovery (E1 RL-74 section: sweeps of 2.0–3.4 s at −12 to −2 s). So
moving the bundle read-back is not enough.

- **Plan:** the inventory ticker runs in its own process. A child process owns the SMC reader and writes the journal;
  the runtime only starts it, stops it and reads the file.
- **Test:** a synthetic busy main thread does not change the child's cadence.
- **Native check:** smoke Part B checks the bar in all five phases.

The gate sidecar is W1's and is not touched.

---

## 7. Reconciliation: what the plan takes from the Sol seat

**Agreed independently.** Both seats found the following:

- 2a fails: Sol's arithmetic matches this plan's. A band of at least 6.59 °C would be needed for Tf08 to return
  within 300 s.
- Every D warmup-cooldown G0 on Tf08 exceeds the 616.50 s duty limit. The bar is in conditional breach if those
  waits recur.
- No option is expressible by policy data alone where it records a third key. Gating different pairs by gate kind is
  not expressible either. Moving Tf08 into the fast slot changes the band but does not make Tf08 record-only.
- `thermal_gates.py` stays byte-identical under every option.
- The cooldowns are two-timescale. Sol's piecewise log fits on D give TV0h τ ≈ 18 / 212 / 320–385 s and Tf08
  τ ≈ 52 / 260 / 330–410 s over 0–60, 60–300 and 300–600 s. At 600 s Tf08 is still 1.9–2.4 °C above its own
  reference, against 0.17–0.23 °C for TV0h.
- The replays agree to the 0.01 s on every shared row.

**Adopted from Sol.**

1. **Part B alone cannot decide on duty.** Part B is one D step, not three admitted turns with holds after a D
   predecessor. The plan's third outcome row ("arm at 1.5 °C under fallback step 1") is therefore withdrawn as a
   *decision*. It becomes a *prediction* printed with the table. S6, S7, duty and cap receipts are earned on the
   follow-up's gated block for the keys actually picked, as Sol says. (The point that remains in dispute is D5.)
2. **A second stability test.** A stable pick must also be the same key, or the same alias representative, with the
   same class and heat-order reference, under both treatments of the borderline reads. The plan's numeric margins
   (τ ≥ 5 s from each boundary; ≤ 6 s per 0.01 °C) stay beside it (D3).
3. **The duty bar's other terms.** For the V candidates, Sol's G1/H allowance under the 616.50 s bound is: at 1.0 °C,
   at most 186.7 s for TV0m and −55.3 s for TV0s; at 1.5 °C, 273.7 s and 138.7 s. Nothing shows that three turns fit.
4. **Sol's deviation drafts** SS-1 (unchanged classifier, R0-fast slow pick), SS-2 (slow return ceiling 1,200 s) and
   SS-3A (record-only lag key) are the alternatives to this plan's WP14(a)-R1-SLOW row, which combines SS-1 and
   SS-3A. If Option 2 is chosen, SS-2's text is used, and not this plan's WP14(a)-RETURN.

**One new finding, against SS-2 as written.** SS-2 keeps 60 < τ ≤ 300 s, noise ≤ 0.15 °C and the "longest t1" ranking,
and changes the ceiling to t1 ≤ 1,200 s. On the 30B diagnostic (E1, gates removed, variant a), that rule selects
**TVFm**, not Tf08:

- TVFm: τ 208.9 s, rise 50.0 °C, t1 = 817 s, noise 0.0002 °C, rise below the D1(d) limit, unclamped.

It ranks ahead of all the other admissible slow keys:

| key | t1 (s) |
|---|---|
| TVFm | 817 |
| TVFh | 814 |
| TCHP | 661 |
| Tf04 / Tf09 / Tf0A / Tf0B | 620–630 |
| Tf08 | 565 |

(TVS1 and TVS2, at τ ≈ 566–570 s, are outside τ ≤ 300 s.) Nobody has replayed TVFm as a gate. Its excess at 600 s,
1.36 °C, is about a third of Tf08's. So "admit a truly slow key" by a ranking rule chooses a key whose waits are
unknown. Landing on Tf08 would take a further criterion, and that criterion would be the choice. The plan's position
stays: Option 2 is not recommended. If the lead prefers it, the D table must replay the amended winner as a gate
before any night arms.

## D. Disagreements between the seats

| # | topic | Opus | Sol | plan |
|---|---|---|---|---|
| D1 | recommendation | **3a.** The registered classifier's fast-family pair gates, named for what it controls (a near-die settling check), and Tf08 is recorded in every member. Option 2 buys slow-mass control at the price of every heavy cell, through the duty bar | **Option 2 (SS-2) is preferred scientifically.** The slow role should represent the long tail; amend only the slow return ceiling to 1,200 s, keeping G1/H at 300 s and the duty bar. Sol warns it is likely infeasible on duty, and offers 3A as the coherent alternative | 3a; Option 2 kept as the lead's alternative (E1) |
| D2 | which key Option 2 selects | computed: TVFm on the 30B diagnostic (section 7), which has never been replayed as a gate | "may be another key, not Tf08"; winner not computed | the TVFm finding stands; Option 2 needs a gate replay of its winner in Part B |
| D3 | pre-declared numeric criteria for the D table | τ margin ≥ 5 s at both class edges; ≤ 6 s per 0.01 °C at the armed band; G0 ≤ 616.5 s | no new numeric thresholds from a design seat; stability = the same pick across borderline-read views; the lead judges | both tests printed; the lead rules on whether the numbers bind (E4) |
| D4 | recording mechanism for the third key | an additive `record_keys` field in `thermal.py` (the sidecar), with gates that never read it | a separately bound collector outside `thermal_gates.py`, with its own schema and accounting; a further approval, not a knob | either; the lead chooses (E3). If refused, the methods say the slow mass is unrecorded in W1 |
| D5 | arming band for a V-key pick | at the registered default, with a prediction from Part B of whether 1.0 °C breaks the duty bar | receipts earned only on the night's gated block, never from Part B | Sol's rule is adopted: arm at the default. The cost is a possible second night if the default breaks the duty bar; the lead may waive (E5) |
| D6 | which A-family keys count as distinct | TV0s and TV1s treated as identical in E1 (same values), though not in E1's alias list | treated as aliases on that record | one candidate on the 30B record; the D record's alias groups decide |

## E. Questions for the research lead

- **E1.** Which slow role: Option 3a (recommended; deviation row WP14(a)-R1-SLOW, or SS-1 + SS-3A), or Option 2 (SS-2).
  If Option 2: note that it picks TVFm on the 30B diagnostic, and whether a further criterion is to be added to reach
  Tf08.
- **E2.** If the D table gives a null or unstable slow pick: is a pre-declared deterministic slow key acceptable,
  namely the largest τ among R0-classified, unaliased keys with τ·ln(rise) ≤ 300 s on the D step? Or does it go to the
  IOHID/X4 ruling?
- **E3.** The record-only channel for the unused slow key: approve a `thermal.py` `record_keys` edit, or a separate
  bound collector (D4), or neither.
- **E4.** Whether this plan's numeric D-table criteria bind (D3).
- **E5.** D5: accept the risk of a second night, or allow the arm band to follow Part B's prediction.
- **E6. Sol-seat exposure, for the lead's ruling.** The Sol seat reports that its first audit command printed the
  whole decision document. It returned unrelated Block 5 policy and outcome prose, including aggregate ledger and
  check counts. A later RL-59 range also ran into the next decision request. Sol states that no Block 5 result file
  was opened and that its thermal calculations use only thermal inputs. It asks whether its seat remains acceptable
  for adoption. This plan's recommendation does not depend on Sol's: section 0 was committed first.
