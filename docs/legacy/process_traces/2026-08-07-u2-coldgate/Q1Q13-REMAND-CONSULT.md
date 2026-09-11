# Q1+Q13 joint remand — design consult response of record (2026-08-08)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge. Chartered by
SYNTHESIS-V2.md (the second convening's joint remand). The consult
independently REPRODUCED the refuter's crossing (400,000-corpus Monte
Carlo: P(range>ceiling) = 0.2005 / 0.6718 / 0.8549 at n = 19/30/38)
and verified the actual D-116 30-member draw is coherent only narrowly.

**MAGISTRATE ADOPTION (Fable, 2026-08-08), with terms:** the design is
ADOPTED for the U2 rework —
1. **Lineage-monotone prediction-family envelopes:** S_g =
   max(S_{g-1}, t(0.975,n-1)·s·sqrt(2)), C_g = max(C_{g-1},
   t(0.995,n-1)·s·sqrt(2)); same-family ordering makes screen<ceiling
   structural; the genesis screen 0.010818 is the inherited lower
   bound, so successor allowances can only STRENGTHEN (grow) under
   degradation and never shrink below the ratified literal.
2. **Two-universe rule:** the R2.8 TRIGGER universe (full valid
   same-epoch; 30 today) is distinct from the DERIVATION BASIS
   (parent basis + parent-judged post-cutoff additions; Window-B
   excluded per D-116) — resolving Q1 and the refuter's finding
   jointly, with D-109 R2.2 + D-116 as the textual proof the universes
   were always distinct.
3. **Clamp removed:** invalid arithmetic refuses issuance
   (`invalid_acceptance_arithmetic`); runtime classification precedence
   and coherent excess/headroom record fields per memo §6; the interim
   issuance refusal stays as backstop.
4. **Transcription term (the consult's own condition):** D-117 cl.1's
   "every mint" literal is amended for SUCCESSORS to "genesis lower
   bound + lineage-envelope rule" ONLY via an explicit decision-log
   entry; that entry is transcribed flagged ED-REVERSIBLE (morning
   review) and notes the amendment can only ever raise the allowance
   floor. Until transcription + Ed's morning pass, option (e)
   (freeze-until-ruled) controls — which is fail-closed and costless
   for the three D-117 nights (the ISSUED artifact governs them;
   successors matter only if a mid-campaign trigger fires).

---

## Positions

### 1. Quantitative finding reproduced

Using 400,000 standard-Gaussian corpora per size, the production non-pinned t kernel, and seed `20260807+n`:

| n | P(range > 99% ceiling) | Monte Carlo 95% interval |
|---:|---:|---:|
| 19 | 0.200453 | [0.199212, 0.201693] |
| 30 | 0.671793 | [0.670337, 0.673248] |
| 38 | 0.854905 | [0.853814, 0.855996] |

The refuter’s result is correct. The issued n=19 artifact has:

- range: `0.010817749309353528`
- sample SD: `0.002970761365307205`
- screen: `0.010818`
- 95% two-draw prediction: `0.008826584887500717`
- 99% ceiling: `0.012093166090593858`
- cap: `0.001275166090593858`
- ceiling/screen: `1.1178744769`

Reconstructing all 30 D-116-valid observations gives:

- the same extrema and range
- sample SD: `0.002947531588352414`
- 95% prediction: `0.008525415306447831`
- 99% ceiling: `0.011489826907224958`
- range-screen cap: `0.000671826907224958`

Thus the actual 30-member draw remains coherent, but only narrowly; it does not invalidate the approximately 67% repeated-sampling failure probability.

### 2. Binding arithmetic design: choose (b), with lineage envelopes

Choose the existing 95% and 99% two-draw prediction family, but make both operatives lineage-monotone:

\[
Q_{95,g}=t_{0.975,n_g-1}s_g\sqrt2,\qquad
Q_{99,g}=t_{0.995,n_g-1}s_g\sqrt2
\]

\[
S_g=\max(S_{g-1},Q_{95,g}),\qquad
C_g=\max(C_{g-1},Q_{99,g})
\]

\[
\text{cap}_g=C_g-S_g,\qquad
A_g=\max(\text{observed drift},S_g)
\]

Genesis remains:

- `S₀ = 0.010818`
- `C₀ = 0.012093166090593858`

The 95% and 99% candidates should use the same `1e-18`, `ROUND_HALF_EVEN` comparator quantum; presentation rounding remains separate.

This is not raw option (b): the D-117 literal remains the genesis lower bound, and neither screen nor ceiling may fall as more observations arrive. It is also not option (e): sufficiently increased drift dispersion automatically raises both quantities.

The ordering is algebraic. For every nondegenerate corpus, `Q95 < Q99`; by induction, if `S(g−1) < C(g−1)`, then:

\[
\max(S_{g-1},Q_{95,g}) < \max(C_{g-1},Q_{99,g})
\]

A zero-SD corpus is still safe because the strictly ordered inherited pair dominates. Consequently, `P(screen >= ceiling)=0` for valid derivations, apart from implementation defects caught by the issuance backstop.

Using the same 99% statistic for both screen and ceiling is rejected: once that candidate dominates, screen equals ceiling, cap becomes zero, the budgeted-drift lane disappears, and issuance must refuse. The never-zero allowance would cease to be a floor and become the maximum admissible drift itself.

The allowance’s new meaning is precise: it is the larger of the observed drift and a nondecreasing, genesis-anchored 95% two-draw prediction floor. It never authorizes a drift above the independently maintained 99% ceiling.

### 3. Corpus universe: parent basis plus post-cutoff additions

Use two explicitly different universes:

- **R2.8 trigger universe:** every authenticated, content-distinct, valid same-epoch observation. It currently counts 30, including the two valid Window-B fiducials.
- **Derivation basis:** the parent derivation corpus plus valid same-epoch content first appearing after the parent cutoff and judged under the parent artifact before absorption.

Therefore the eleven valid observations already known at the D-116 cutoff but absent from the n=19 basis remain bound-inert, including both Window-B fiducials. They remain in `prior_observation_set` and trigger counting.

This separation is directly supported by D-109:

- R2.2 says the derivation corpus remains the exact n=19 threshold-producing set.
- R2.8 calls its full-valid universe the “Counting rule for the … trigger,” not the derivation basis.
- R2.5/R2.6 and the ratified Q11 disposition permit genuinely new, parent-judged observations to be absorbed prospectively.
- D-116 demonstrates the separation in practice: 30 observations count, while the bound remains n=19 and Window-B is explicitly bound-inert.

At the 38-count trigger, if eight post-cutoff valid observations were added, the trigger count would be 38 while the derivation basis would be 27. The next trigger boundary would be 76, derived from the trigger count—not 54 from the derivation basis.

Window-A-lineage-only is rejected because a historical directory/window label is not a durable metrology rule. The full-valid basis is rejected because it contradicts D-116’s explicit bound-inertness statement.

### 4. Option ranking

1. **(b), lineage-monotone 95%/99% envelope — selected.** Stable as n grows, structurally ordered, never-zero, and responsive to increased dispersion. D-102 already authenticates both statistics. This remand must explicitly amend D-117 clause 1 from permanent equality to a genesis lower bound.
2. **(e), freeze until ruled.** Strongest pre-remand authority reading and the mandatory fallback if the amendment is not transcribed. It is safe but turns degradation-triggered issuance into a desk ruling and supplies no automatic growth.
3. **(d), capped range.** Coherence would require `k < 2.575829…√2 ≈ 3.642773`; `k=3.5` would work algebraically but is unratified and suppresses isolated degradation as approximately `kD/√n`. Choosing `k≈3.641406` merely reverse-engineers the favorable genesis draw and leaves negligible margin.
4. **(c), rolling fixed-size subset.** “Most recent 19” has no authoritative selector and merely freezes the failure probability near 20% per issuance. The exact original 19 is option (e), not a rolling-subset design.
5. **(a), full-corpus range.** Its crossing probability tends to one. It is licensed only as the ratified genesis derivation, not as an unbounded successor rule.

A pure level shift need not enlarge the drift-dispersion statistic; Q2’s preflight observed-maximum comparator handles that failure class. A mixed old/new degraded regime or increased variability raises the two-draw predictions. A systematic-invalid observation remains a persistent refusal rather than being fitted away.

### 5. Issuance-time refusal

Retain the ordered backstop permanently:

- Compare the stored, post-quantization Decimal operatives.
- Refuse exactly when `screen >= ceiling`.
- Margin: zero; strict positive headroom is required, but no invented epsilon is added.
- Refusal: `successor_screen_exceeds_budget_ceiling`.
- Compute cap as `ceiling - screen`; never use `max(0, …)`.

The validator must also require `cap == ceiling - screen` and `cap > 0`. The selected design makes the refusal unreachable for correctly derived artifacts, but it remains necessary against rule drift, malformed artifacts, and numerical/rounding defects.

### 6. Runtime ordering and record

After validating `screen < ceiling`, classify in this order:

1. `drift > ceiling` → `budget_exceeded`, refuse `instrument_calibration_mismatch`.
2. Else `drift > screen` → `passed_budgeted`.
3. Else → `passed_screen`.
4. Mint allowance only after a passing classification.

The record should contain:

- `excess_over_screen_s = max(drift-screen, 0)`
- `excess_over_budget_ceiling_s = max(drift-ceiling, 0)`
- `budget_headroom_s = ceiling-screen`

A `budget_exceeded` record must therefore always have positive values for both excesses. If the arithmetic invariant somehow fails at runtime, emit `status=invalid_acceptance_arithmetic` and refuse before classifying the observed drift.

### 7. Worked examples

**Issued n=19.** `Q95=0.008826584887500717`, so the inherited genesis screen wins: `S=0.010818`. `C=0.012093166090593858`; cap is `0.001275166090593858`.

A drift of `0.011581436` is above the screen but below the ceiling:

- status: `passed_budgeted`
- allowance: `0.011581436`
- excess over screen: `0.000763436`
- budget excess: `0`

**Current n=30 trigger inventory.** Under the selected universe, these 30 do not become the derivation basis: the basis remains the ratified 19 because the additional eleven were already known at the parent cutoff. Screen, ceiling, and cap therefore remain the n=19 values.

As an arithmetic stress check, even feeding the actual 30 statistics produces `Q95=0.008525415306447831` and `Q99=0.011489826907224958`; both are below their inherited operatives, so the envelope still yields:

- screen: `0.010818`
- ceiling: `0.012093166090593858`
- cap: `0.001275166090593858`

A drift of `0.010000` passes the screen and mints allowance `0.010818`. A drift of `0.012200` refuses as `budget_exceeded`, with screen excess `0.001382` and budget excess `0.000106833909406142`.

For a degraded hypothetical n=30 basis with SD `0.004`, the candidates become approximately `Q95=0.011569565992286168` and `Q99=0.015592473312419959`; both operatives grow, retain strict ordering, and produce a positive cap.

## Disagreements

- R2.8 does not require trigger-universe membership to imply derivation-basis membership; D-109 R2.2 and D-116 prove the opposite.
- The D-117 literal cannot be silently generalized. The remand’s adopted decision must explicitly supersede “every mint” into “genesis lower bound plus the lineage-envelope rule.” Without that transcription, option (e) controls.
- The current `max(0, cap)` is not a conservative recovery; it creates an invalid acceptance artifact and must be removed.

## Open questions

None in the arithmetic design. The lead must assign and transcribe the new decision ID before replacing `COLD-GATE-U2-PENDING`; that is an administrative authority step, not an unresolved design choice.

## Recommendation

Implement the rework as follows:

- `docs/decision_log.md`: add the remand decision, explicitly amending D-117 clause 1 for successors and recording the two-universe rule; preserve historical text.
- `joulewise/calibration_bracketing.py`: add separate trigger/basis rule constants; implement the lineage 95%/99% envelopes; remove the cap clamp; enforce strict arithmetic validation; decouple trigger count from derivation `n`; fix runtime classification and record fields.
- `scripts/build_calibration_acceptance_successor.py`: retain the full prior/trigger inventory, but select only parent-basis plus parent-judged post-cutoff additions; compute count boundaries from full-valid trigger count; pass parent operatives into derivation; emit the ordered issuance refusal.
- `tests/test_calibration_acceptance_successor.py`: cover the actual 30-trigger/n19-basis split, 38-trigger/n27-basis progression, Window-B exclusion, n=19/n=30 arithmetic, zero variance, degradation growth, and no-clamp refusal.
- `tests/test_calibration_bracketing.py`: cover exact screen/ceiling boundaries, coherent excess fields, invalid-arithmetic rejection, and allowance behavior.
- `configs/calibration/calibration_acceptance_d079_v2.json`: unchanged and immutable.
- The existing writer copied-scalar removal remains a separate mandatory pre-issuance unit under the synthesis.

No files were written, staged, or committed.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Designed a lineage-monotone 95%/99% successor arithmetic with separate R2.8 trigger and derivation universes; independently reproduced the Gaussian crossover and verified the issued n=19 and ratified n=30 arithmetic.","pathspec":[],"verification":["git show ad5f3f7 authority/code/artifact inspection: complete","D-116 30-valid inventory reconstructed from committed issuance evidence: complete","400000-trial Gaussian simulations at n=19/30/38: 0.200453/0.671793/0.854905","production Decimal kernel replay for n=19 and actual n=30 statistics: complete","git status --short --branch: clean"],"flags":["no_edits","read_only_design","remand_decision_requires_transcription"]}
