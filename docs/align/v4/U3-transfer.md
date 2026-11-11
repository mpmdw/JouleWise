# U3 transfer note: why the D bar is f = 1.5 times the 30B bar

Status: draft for the lead to adopt. Adoption happens by digest: put this file's
sha256 in `u3_sources/policy.json` as `transfer_justification_sha256`
(W1-BLOCKERS-merged §4, step 2). Any edit to this file changes the digest, so the
signature lives in the policy and the bar, not here.

**Basis.** This note uses physics, design documents and the U3 model simulation
only. It uses no pilot 4-10 energy, residual, score or outcome value, and no R1
value. The only measured numbers below are design and sizing constants already
committed in the cited documents: decode rates, D's planning cost per token, and
the window ceilings.

## 1. What f does

U3 compares the two members of an identical-work replay pair in relative terms:
r = ΔE/Ē. The bar is fitted on 30B: s₀ is the RMS about zero of one prespecified
30B pilot pair per session, and q is the exact series quantile at β = .05 with
N = 24 under RL-16 and the prospective R25 rule (W1: 4×30B + 1×D; C1-C14 and
T1-T5: one D pair each), formerly N = 16 and then N = 22. The production roster is
`scripts/align_v4_u3_export.py`; authority is RL-16, applying RUN_STATE 239 R25 to both test reserves.
A 30B pair fails if |r| > q·s₀. A D pair fails if |r| > f·q·s₀
(`pilot_protocol_v4.md:644-664`; RUN_STATE 226 R14). So f is the largest ratio
of D's true relative replay SD to 30B's at which the series false-fail is still
at most β. The OC in §4 confirms that at a true D/30B ratio of exactly 1.5, the
series rate is the nominal 5%.

The ruled value is f = 1.5. Two documents set it: the W1-BLOCKERS agreement, D4
and L6 (`docs/align/v4/W1-BLOCKERS-AGREEMENT.md:39,94` on
`align/2026-11-08-w1-blockers-opus` @ `2cfe51f8c`), and RUN_STATE 226 R14. This
note is the written justification L6 requires.

## 2. How the source and the target differ

| Property | Source: 30B pilots 4-10 (pair at ordinals 1↔9) | Target: D in W1 (5↔17), C1-C14 and T1-T5 (early↔late sentinel) | Effect on relative replay noise |
|---|---|---|---|
| Model | Qwen3-30B-A3B, MoE, about 3.3 B active parameters, MLX 4-bit: about 1.9 GB of weights read per decode token | Qwen3.8-27B dense, 8-bit (`pilot_protocol_v4.md:70-80`): about 28 GB per token, roughly 15× more | Each D token costs more energy, so the member total Ē is much larger (rows below) |
| Cost per token, decode rate | Physics only: of order a few tenths of a J/token, scaled from D by bytes moved. Decode at least 41.95 tok/s (v3 sizing constant, a timing value) | e_D ≈ 3.5-3.6 J/token (range 3.0-4.5), about 90 ms per step, about 11 tok/s (`council-2026-11-06-v4-review/CHAIR.md:275`) | Neither enters r directly; both set Ē and the duration |
| Decode length and member energy | 120 s episode guard plus one admitted turn (planning 234 s; `pilot_protocol_v3.md:76-90`): a few thousand decode tokens per member | B_D ≥ 6,144 decode tokens, member ≤ 1,800 s, no time guard (`pilot_protocol_v4.md:189-201`). E_D ≈ 25-35 kJ (`CHAIR.md:276`) | A D member is about an order of magnitude or more larger in Ē and about 5-10× longer |
| Sampler | 0.6 / 0.95 / 20 / 0 | 1.0 / 0.95 / 20 / 0 | None. U3 admits only exact token-identical pairs (X5 otherwise), so both replays do the same work |
| Thermal control | 300 s idle only, no G0, G1 or holds | G0 to R+δ with a slope criterion, G1 before every turn, and holds, because D is heavy class (`pilot_protocol_v4.md:352-433`). U2 caps the G0 slow-key range at 3 °C. U5 requires \|β_T\|·δ_slow ≤ σ_pair (`:450-458`) | The start state is re-anchored before every D member and turn. The 30B source had no such anchoring |
| Separation of the pair | 8 ordinals, about 1.4 h (v3 member law: 516.6 s + 1.135 × episode) | W1: 12 ordinals (3 D and 8 contrast members between), about 3-4 h at planning bounds. C and T: early and late sentinels spread over a window of up to 59,520 s, about 10× the source separation (`pilot_protocol_v4.md:149-158`) | Larger. This is the main reason f > 1 (§3) |
| Predecessor of each member | Ordinal 1 follows the scaffold, ordinal 9 follows a 30B member | W1 5 and 17 both follow 30B. In C and T, the early sentinel follows a 30B anchor and the late one follows D (`pilot_protocol_v4.md:690-694`) | Heat from the predecessor differs. G0 re-anchors the fast and slow keys, but not chassis heat that G0 does not observe |
| G0 cap | none | R1's D_spam a/b screen: 1,200 s (`r1_runtime_contract.md:93`). W1 D: G0_cap_W1 = clamp(⌈1.25 × max gated wait⌉, 600, 1,200), or G0* under a signed R10-2(a) receipt (`pilot_protocol_v4.md:362-394`) | Changes which members are admitted, not the start state of an admitted member (§3e) |
| Clock, power mode, battery | Active-clock difference ≤ 0.5%, exact tokens | Same clock and token gates; series power mode pinned from R1; B bar requires zero charging members (R14) | Same cap in relative terms |

## 3. Components of replay noise and their expected D/30B ratio

These are the replay-noise components that the protocol and the council name.
For each, here is how its contribution to r scales from source to target.

a. **Additive attribution and instrument error.** This is a fixed number of
   joules per attribution boundary. In r it scales as 1/Ē, and Ē is ≥10× larger
   for D. Holds add boundaries inside each D turn, but even √(several tens of
   boundaries) gives a relative contribution well below the 30B one.
   **Expected D/30B ratio < 1.**
b. **Background OS activity**, modelled as a Poisson stream of small energy
   events. Its relative SD scales as 1/(P·√T). D has higher sustained power P
   and a longer duration T. **Ratio < 1.**
c. **Clock and DVFS.** Both populations are capped at the same 0.5% active-clock
   difference, and the power mode is pinned. **Ratio about 1.**
d. **Between-session moment** (σ_w, `pilot_protocol_v4.md:466-471`). It is
   common to both members of a within-session pair, so it cancels in r for the
   source and the target alike. **No contribution.**
e. **Thermal start state.** Leakage power rises with die temperature. D's heavy
   sustained load runs the die hotter, so a given temperature offset moves a
   larger fraction of D's power: per °C, D's relative sensitivity is higher.
   Against this, D's start state is gated to R+δ at G0 and at every G1/hold.
   The 30B pilots were ungated. U5 bounds the gated contribution by D's own
   pair SD, |β_T|·δ_slow ≤ σ_pair.
   The G0 cap does not change this release criterion. A shorter cap converts
   slow-cooling starts into X2 exclusions; it does not admit warmer starts. So
   the source→target G0 cap difference (1,200 s in R1 against G0_cap_W1 or G0*
   in W1) does not widen the admitted start-state distribution.
   **Ratio about 1, with the sign uncertain.**
f. **Slow drift between the two ordinals** (ambient temperature, chassis heat,
   OS and SSD state). Ungated, drift behaves like a random walk: its variance
   grows with the separation Δt. At 3-10× the source separation, that alone
   would give an SD ratio of about 1.7-3.2. G0 re-anchors the observed
   temperatures at every member, which stops their drift from accumulating. What
   remains is drift that G0 does not see: ambient temperature (unobserved,
   `CHAIR.md:203-205`), chassis heat from an unlike predecessor, and OS state.
   **Ratio > 1, bounded but not quantified.**

**Conclusion.** Components (a) and (b) favour D. Components (c) and (d) are
neutral. (e) is gated. (f) is the one that plausibly makes D noisier. f = 1 would
assume that the gates fully offset (f) despite the longer, heavier D windows,
and nothing supports that before W1. f = 1.5 allows D's relative replay variance
to reach 2.25× 30B's. That is enough for the unobserved part of (f) to double the
total variance even if (a) and (b) contributed nothing.

Larger values cost sensitivity. Under the adopted R14 arithmetic, f = 2 makes
the D bar exactly twice the f = 1 bar at the same n, N and β. Even at
f = 1.5, a D drift of 2 pilot SDs is detected rarely (§4). This judgement uses no D replay data;
the paper discloses it as "transfer-limited" (agreement L6).

## 4. Exact-model calibration and synthetic OC: N = 24

RL-16 applies R25's rule to every window that can run: W1 30B 4 + D 1,
C1-C14 and T1-T5 D 1 each, N = 24 (4×30B + 20×D). At n = 7, β = .05,
q = 4.3305 and f q = 6.4958, replacing 4.2793 and 6.4190 at N = 22.
The bar is unsigned. The transfer factor remains 1.5 and the familywise budget .05;
the leave-one-out heavy-tail trigger still halves β. No other gate changes.

The unchanged 2,000-panel quadrature solves
`E_U[1 − (1 − P(|Z| > q U))^N] = β`, `U² ~ χ²_n/n`.
The scale is zero-centred RMS with n degrees of freedom; no pilot values enter
this evidence. β/N is a reference allocation, not a substituted Bonferroni rule.

| n | β | q | D multiplier | Per-comparison rate at assumed scale | Familywise rate |
|---:|---:|---:|---:|---:|---:|
| 7 | 0.05 | 4.3305 | 6.4958 | 0.00343554 | 0.05000 |
| 7 | 0.025 | 4.9575 | 7.4362 | 0.00164226 | 0.02500 |
| 5 | 0.05 | 4.9484 | 7.4226 | 0.00429159 | 0.05000 |
| 6 | 0.05 | 4.5784 | 6.8677 | 0.00377679 | 0.05000 |

All existing OC scenarios are regenerated with seed 20261108 and 20,000 replicates,
independent of any measurements. The scale is regenerated once per replicate and
shared over all future comparisons. Series rates count any failure; D pair rates
are the marginal failure probability (power under the specified alternative).

| Scenario (n = 7) | β | Series rate | D pair rate | Monte Carlo SE of series rate |
|---|---:|---:|---:|---:|
| normal_iid | 0.05 | 0.01825 | 0.000407 | 0.00095 |
| normal_window_rho_0.5 | 0.05 | 0.01465 | 0.000387 | 0.00085 |
| normal_series_rho_0.9 | 0.05 | 0.00565 | 0.000307 | 0.00053 |
| normal_correlated_training_rho_0.5 | 0.05 | 0.03515 | 0.001012 | 0.00130 |
| student_t3_unit_variance | 0.05 | 0.16240 | 0.006835 | 0.00261 |
| centered_exponential | 0.05 | 0.12805 | 0.004230 | 0.00236 |
| D_true_scale_1.0 | 0.05 | 0.01825 | 0.000407 | 0.00095 |
| D_true_scale_1.5 | 0.05 | 0.05115 | 0.003602 | 0.00156 |
| D_true_scale_2.0 | 0.05 | 0.16310 | 0.014557 | 0.00261 |
| D_true_scale_3.0 | 0.05 | 0.54295 | 0.067193 | 0.00352 |
| D_drift_two_pilot_sd | 0.05 | 0.08660 | 0.010913 | 0.00199 |
| D_drift_eight_pilot_sd | 0.05 | 0.97215 | 0.809998 | 0.00116 |
| normal_iid | 0.025 | 0.00955 | 0.000178 | 0.00069 |
| normal_window_rho_0.5 | 0.025 | 0.00755 | 0.000158 | 0.00061 |
| normal_series_rho_0.9 | 0.025 | 0.00310 | 0.000120 | 0.00039 |
| normal_correlated_training_rho_0.5 | 0.025 | 0.01805 | 0.000472 | 0.00094 |
| student_t3_unit_variance | 0.025 | 0.12200 | 0.004875 | 0.00231 |
| centered_exponential | 0.025 | 0.08425 | 0.002502 | 0.00196 |
| D_true_scale_1.0 | 0.025 | 0.00955 | 0.000178 | 0.00069 |
| D_true_scale_1.5 | 0.025 | 0.02715 | 0.001783 | 0.00115 |
| D_true_scale_2.0 | 0.025 | 0.09375 | 0.007865 | 0.00206 |
| D_true_scale_3.0 | 0.025 | 0.39495 | 0.042555 | 0.00346 |
| D_drift_two_pilot_sd | 0.025 | 0.04600 | 0.005343 | 0.00148 |
| D_drift_eight_pilot_sd | 0.025 | 0.90290 | 0.656920 | 0.00209 |

The adjacent R1 screen is qualification only and is not in N. Its normal-model
power is the `D_pair_failure_probability` in each case's `normal_model` rows.
It omits most long-separation drift and detects only gross transfer violations.
W1's separated D pair remains the first long-separation check.

Reproduce (new output path; never overwrite evidence):

```bash
python3.13 -B scripts/align_v4_u3_scope_comparison.py --output <new-path>.json
```

[U3-scope-n24.json](U3-scope-n24.json) holds the full synthetic policy, all per-window
OC rates and counts, the n = 5/6 cases, both fixed-β branches at n = 7, and normal-model
power. Digest stand-ins bind no real artifacts. The OC does not reapply the heavy-tail
trigger per replicate; neither branch promises a rate conditional on the realized
scale or trigger. Historical N = 16/22 evidence stays in `U3-scope-n22.json`.
These are model sensitivities, not hardware validation, adoption, or a signed bar.

## 5. Residual risk

- **D noisier than assumed.** If D's true relative replay SD is ×2 the 30B
  value, the series false-fail at N = 24 rises to about 16.3% (×3: about 54.3%),
  and almost all of the excess lands on D pairs. A failed D pair fails that window's U3: W1
  then fails at the desk and the lead disposes. A C window with a failed U3 is a
  STRUCTURAL bar (R22-2): it enters no pool, contributes nothing to calibration
  (not even the members it captured), is not counted and is replaced by the next
  reserve window C9-C14 in order (R24), so calibration stays exactly 8 admitted
  windows; a barred T window uses T4 then T5 under B6 and RL-15. RL-20 freezes the series policy.
  (This supersedes R15's rule that such a window still counted toward the eight.)
  The R1 screen will usually not warn in advance.
- **D quieter than assumed.** If D is as quiet as 30B or quieter, D's false-fail
  is negligible, but U3 rarely detects a real D state shift of 2 pilot SDs.
  U3 is then a weak control for D. U4 and U5 carry the state-control burden.
- **Model assumptions.** The bar assumes normal, independent pilot sessions.
  Heavy tails (t₃) raise the N = 24 series rate to about 16.2%. The OC is a model
  sensitivity analysis, not hardware validation.
- **Scope of this note.** It covers the 30B→D transfer and the R1→W1 G0 cap
  difference. It does **not** cover these changes:
  - any change to δ_slow, G_turn, N_chunk, power mode, quantization, B_D or
    T_dead between R1 and the W1 D configuration (D-17a,
    `pilot_protocol_v4.md:695-702`);
  - any escalation-ladder change in a later window (`:501-509`).

  Any of them changes `d_configuration_sha256`. It then needs an amended note,
  with a new digest, before step 6, or that window's D pairs are inconclusive.
