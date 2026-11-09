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
N = 22 after the prospective R25 expansion (W1: 4×30B + 1×D; C1-C14 and
T1-T3: one D pair each), formerly N = 16. The production roster is
`scripts/align_v4_u3_export.py` on `origin/align/2026-11-08-v4-r11` @
`33932b391`; authority is RUN_STATE 239 R25 on `origin/main`.
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

| Property | Source: 30B pilots 4-10 (pair at ordinals 1↔9) | Target: D in W1 (5↔17), C1-C14 and T1-T3 (early↔late sentinel) | Effect on relative replay noise |
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
f = 1.5, a D drift of 2 pilot SDs fails only about 1.1% of D pairs at N = 22
(§4). This is a judgement made without any D replay data. The paper discloses it as
"transfer-limited" (agreement L6).

## 4. Exact-model calibration and synthetic OC: N = 16 beside N = 22

R25 changes only the prospective roster: C9-C14 add six D comparisons, so
N = 5 + 14 + 3 = 22 (4×30B + 18×D), formerly 16 (4×30B + 12×D).
All other inputs remain fixed: one prespecified pair per session, n = 5, 6 or 7,
zero-centred RMS with df = n, f = 1.5, β = .05, the leave-one-out heavy-tail
rule, seed 20261108, 20,000 replicates and every existing OC scenario.
The q and OC calculations here use no pilot values.

The R14 equation and `v4_u3` implementation specify N unambiguously:

```
s₀ = sqrt(sum(r_i²)/n)
s_{−i} = sqrt(sum_{j≠i}(r_j²)/(n−1))
β = .025 if any |r_i| > 3 s_{−i}, otherwise .05
U² ~ χ²_n/n; p(U; q) = P(|Z| > qU)
q solves E_U[1 − (1 − p(U; q))^N] = β
a = E_U[p(U; q)] = P(|T_n| > q)
```

Here **a is the marginal per-comparison level** for 30B and for D when its
true SD is f = 1.5 times 30B's. β/N is shown only as an allocation reference;
it is not a substituted Bonferroni level. Nor is a = 1−(1−β)^(1/N): future
comparisons share the estimated scale U. When D's true scale is ×1, its wider
bar makes its own false-fail and the mixed-population familywise rate smaller.
N counts all possible comparisons before signing, including reserves even if
some windows are never run. It does not count the adjacent R1 screen, which
is qualification only. No bar is refitted from judged windows.

The numbers below use the unchanged 2,000-step `v4_u3` quadrature. The series
law is exact under the model; displayed values are numerical approximations.
At n = 7:

| Quantity | N = 16, β = .05 | N = 22, β = .05 | N = 16, β = .025 | N = 22, β = .025 |
|---|---:|---:|---:|---:|
| 30B / D comparisons | 4 / 12 | 4 / 18 | 4 / 12 | 4 / 18 |
| β/N (reference only) | 0.00312500 | 0.00227273 | 0.00156250 | 0.00113636 |
| q = 30B bar / s₀ | 4.0898 | 4.2793 | 4.6928 | 4.9011 |
| f q = D bar / s₀ | 6.1347 | 6.4190 | 7.0391 | 7.3516 |
| a: per-comparison false-fail at assumed scale | 0.00463218 | 0.00365846 | 0.00222729 | 0.00175102 |
| Familywise false-fail at assumed scale | 0.05000 | 0.05000 | 0.02500 | 0.02500 |
| D per-comparison false-fail at true scale ×1 | 0.00047461 | 0.00036072 | 0.00020434 | 0.00015572 |
| Mixed familywise false-fail at D true scale ×1 | 0.01920788 | 0.01600787 | 0.00923840 | 0.00763900 |

**Operating characteristics and power at the existing alternatives.** These
are the unchanged `v4_u3.operating_characteristics` scenarios. Series columns
report any failure over the whole roster; D pair columns report a single D
comparison's failure probability, which is power under a specified D
alternative. All rates are Monte Carlo estimates. Each series estimate has
SE at most 0.00354; D comparisons within a replicate share U and are dependent.
The same seed is retained, but differing roster lengths change subsequent RNG
positions, so these are not paired Monte Carlo draws across N.

| Scenario (n = 7) | β | N = 16 series | N = 22 series | N = 16 D pair | N = 22 D pair |
|---|---:|---:|---:|---:|---:|
| Normal iid (D true scale ×1) | 0.05 | 0.01840 | 0.01630 | 0.000496 | 0.000369 |
| Within-window correlation 0.5 | 0.05 | 0.01725 | 0.01470 | 0.000508 | 0.000342 |
| Whole-series correlation 0.9 | 0.05 | 0.00840 | 0.00560 | 0.000475 | 0.000256 |
| Training correlation 0.5 | 0.05 | 0.04125 | 0.03895 | 0.001304 | 0.001122 |
| Student t₃, unit variance | 0.05 | 0.15255 | 0.16595 | 0.008412 | 0.007414 |
| Centred exponential | 0.05 | 0.11445 | 0.12260 | 0.005012 | 0.004358 |
| D true scale ×1 | 0.05 | 0.01840 | 0.01630 | 0.000496 | 0.000369 |
| D true scale ×1.5 | 0.05 | 0.04895 | 0.05020 | 0.004733 | 0.003561 |
| D true scale ×2 | 0.05 | 0.14705 | 0.15930 | 0.018100 | 0.014681 |
| D true scale ×3 | 0.05 | 0.49130 | 0.53650 | 0.080350 | 0.069847 |
| D drift +2 pilot SD | 0.05 | 0.08675 | 0.08755 | 0.014317 | 0.011003 |
| D drift +8 pilot SD | 0.05 | 0.98035 | 0.97580 | 0.863662 | 0.823986 |
| Normal iid (D true scale ×1) | 0.025 | 0.00975 | 0.00800 | 0.000188 | 0.000194 |
| Within-window correlation 0.5 | 0.025 | 0.00875 | 0.00710 | 0.000192 | 0.000153 |
| Whole-series correlation 0.9 | 0.025 | 0.00335 | 0.00290 | 0.000258 | 0.000061 |
| Training correlation 0.5 | 0.025 | 0.02105 | 0.01930 | 0.000546 | 0.000472 |
| Student t₃, unit variance | 0.025 | 0.11235 | 0.12180 | 0.005738 | 0.005081 |
| Centred exponential | 0.025 | 0.07775 | 0.08095 | 0.003025 | 0.002611 |
| D true scale ×1 | 0.025 | 0.00975 | 0.00800 | 0.000188 | 0.000194 |
| D true scale ×1.5 | 0.025 | 0.02510 | 0.02370 | 0.002250 | 0.001692 |
| D true scale ×2 | 0.025 | 0.08260 | 0.09015 | 0.009696 | 0.007697 |
| D true scale ×3 | 0.025 | 0.35245 | 0.38440 | 0.051433 | 0.043503 |
| D drift +2 pilot SD | 0.025 | 0.04440 | 0.04310 | 0.006771 | 0.004992 |
| D drift +8 pilot SD | 0.025 | 0.92375 | 0.90860 | 0.726642 | 0.671892 |

The same rule at β = .05 if fewer sessions are available. Scale rows are
Monte Carlo **series** failure rates; at true D scale ×1.5 the exact-model
familywise rate is .05 for every n and N.

| n | Quantity | N = 16 | N = 22 |
|---:|---|---:|---:|
| 5 | q | 4.6575 | 4.8866 |
| 5 | Per-comparison false-fail at assumed scale | 0.00554549 | 0.00452769 |
| 5 | Series, D true scale ×1 | 0.02190 | 0.01885 |
| 5 | Series, D true scale ×1.5 | 0.05045 | 0.05245 |
| 5 | Series, D true scale ×2 | 0.12385 | 0.13325 |
| 5 | Series, D true scale ×3 | 0.38525 | 0.42435 |
| 6 | q | 4.3172 | 4.5229 |
| 6 | Per-comparison false-fail at assumed scale | 0.00499777 | 0.00400530 |
| 6 | Series, D true scale ×1 | 0.02170 | 0.01760 |
| 6 | Series, D true scale ×1.5 | 0.05115 | 0.05195 |
| 6 | Series, D true scale ×2 | 0.13935 | 0.14670 |
| 6 | Series, D true scale ×3 | 0.44925 | 0.48535 |

**Power of the R1 screen.** The screen is one adjacent D_spam a/b pair tested
against f·q·s₀. The following normal-model probabilities integrate U directly
rather than estimating them from the OC D comparisons (n = 7, no drift):

| D true scale | N = 16, β = .05 | N = 22, β = .05 | N = 16, β = .025 | N = 22, β = .025 |
|---|---:|---:|---:|---:|
| ×1 | 0.000475 | 0.000361 | 0.000204 | 0.000156 |
| ×1.5 | 0.004632 | 0.003658 | 0.002227 | 0.001751 |
| ×2 | 0.018135 | 0.014869 | 0.009733 | 0.007904 |
| ×3 | 0.080132 | 0.069670 | 0.051360 | 0.044073 |

Because the pair is adjacent, it also leaves out most of component (f). The
screen catches only gross violations. W1's D 5↔17 pair is the first separated
test. At N = 22, β = .05, a +2 SD shift is detected in about 1.1% of D pairs
(OC above), although the longer series can still fail elsewhere.

Reproduction:

```bash
python3.13 -B scripts/align_v4_u3_scope_comparison.py --output <new-path>.json
```

[U3-scope-n22.json](U3-scope-n22.json) preserves both full synthetic policies,
all OC rows (including per-window rates and series failure counts), and the
normal-model power calculations. Only the six roster entries differ between
policies; the digest stand-ins bind no real source. All reported OC scenarios
hold β fixed and regenerate a calibration scale in every replicate, as the
existing procedure does; they do not reapply the leave-one-out trigger in each
replicate. Neither the .05 nor the .025 rows promise a rate conditional on the
realized scale or on selection of that heavy-tail branch. These are model
sensitivity results, not hardware validation or a signed U3 bar.

## 5. Residual risk

- **D noisier than assumed.** If D's true relative replay SD is ×2 the 30B
  value, the series false-fail at N = 22 rises to about 15.9% (×3: about 53.7%),
  and almost all of the excess lands on D pairs. A failed D pair fails that window's U3: W1
  then fails at the desk and the lead disposes. A C window with a failed U3 is a
  STRUCTURAL bar (R22-2): it enters no pool, contributes nothing to calibration
  (not even the members it captured), is not counted and is replaced by the next
  reserve window C9-C14 in order (R24), so calibration stays exactly 8 admitted
  windows; a T window has no replacement and its failure is disposed by the lead.
  (This supersedes R15's rule that such a window still counted toward the eight.)
  The R1 screen will usually not warn in advance.
- **D quieter than assumed.** If D is as quiet as 30B or quieter, D's false-fail
  is negligible, but U3 rarely detects a real D state shift of 2 pilot SDs.
  U3 is then a weak control for D. U4 and U5 carry the state-control burden.
- **Model assumptions.** The bar assumes normal, independent pilot sessions.
  Heavy tails (t₃) raise the N = 22 series rate to about 16.6%. The OC is a model
  sensitivity analysis, not hardware validation.
- **Scope of this note.** It covers the 30B→D transfer and the R1→W1 G0 cap
  difference. It does **not** cover these changes:
  - any change to δ_slow, G_turn, N_chunk, power mode, quantization, B_D or
    T_dead between R1 and the W1 D configuration (D-17a,
    `pilot_protocol_v4.md:695-702`);
  - any escalation-ladder change in a later window (`:501-509`).

  Any of them changes `d_configuration_sha256`. It then needs an amended note,
  with a new digest, before step 6, or that window's D pairs are inconclusive.
