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
N = 16. A 30B pair fails if |r| > q·s₀. A D pair fails if |r| > f·q·s₀
(`pilot_protocol_v4.md:644-664`; RUN_STATE 226 R14). So f is the largest ratio
of D's true relative replay SD to 30B's at which the series false-fail is still
at most β. The OC in §4 confirms that at a true D/30B ratio of exactly 1.5, the
series rate is the nominal 5%.

The ruled value is f = 1.5. Two documents set it: the W1-BLOCKERS agreement, D4
and L6 (`docs/align/v4/W1-BLOCKERS-AGREEMENT.md:39,94` on
`align/2026-11-08-w1-blockers-opus` @ `2cfe51f8c`), and RUN_STATE 226 R14. This
note is the written justification L6 requires.

## 2. How the source and the target differ

| Property | Source: 30B pilots 4-10 (pair at ordinals 1↔9) | Target: D in W1 (5↔17), C1-C8 and T1-T3 (early↔late sentinel) | Effect on relative replay noise |
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

Larger values cost sensitivity. f = 2 makes the D bar about 2.7× the f = 1 bar
of the Opus build, and U3 for D becomes nearly vacuous (agreement D4). Even at
f = 1.5, a D drift of 2 pilot SDs fails only about 1.4% of D pairs (§4). This is
a judgement made without any D replay data. The paper discloses it as
"transfer-limited" (agreement L6).

## 4. Simulation: OC from the bar build

`v4_u3.operating_characteristics` was run with the policy template: seed
20261108, 20,000 replicates, the roster of RUN_STATE 226 R15 with N = 16, and
f = 1.5. The OC depends only on n and q, never on pilot values. The derivation
will therefore print these exact rows for the realized n and β.

At n = 7, q = 4.0898 at β = .05: the 30B bar is 4.09·s₀ and the D bar is 6.13·s₀.
If the heavy-tail rule halves β, q = 4.6928 at β = .025. Monte Carlo SE is
about 0.001-0.0035.

| Scenario (n = 7) | Series rate, β = .05 | D pair rate | Series rate, β = .025 | D pair rate |
|---|---:|---:|---:|---:|
| D true scale ×1 (normal, iid) | 0.0184 | 0.0005 | 0.0097 | 0.0002 |
| D true scale ×1.5 | **0.0490** | 0.0047 | **0.0251** | 0.0022 |
| D true scale ×2 | 0.1470 | 0.0181 | 0.0826 | 0.0097 |
| D true scale ×3 | 0.4913 | 0.0804 | 0.3524 | 0.0514 |
| D drift +2 pilot SD | 0.0867 | 0.0143 | 0.0444 | 0.0068 |
| Student t₃, unit variance | 0.1525 | 0.0084 | 0.1124 | 0.0057 |
| Centred exponential | 0.1144 | 0.0050 | 0.0777 | 0.0030 |
| Training correlation 0.5 | 0.0413 | 0.0013 | 0.0210 | 0.0006 |

The same rule at β = .05 if fewer sessions are available. Each cell is the
series false-fail rate at that true D scale:

| n | q | ×1 | ×1.5 | ×2 | ×3 |
|---:|---:|---:|---:|---:|---:|
| 5 | 4.6575 | 0.0219 | 0.0505 | 0.1239 | 0.3852 |
| 6 | 4.3172 | 0.0217 | 0.0512 | 0.1394 | 0.4492 |

**Power of the R1 screen.** The screen is one adjacent D_spam a/b pair tested
against f·q·s₀. Under the model, at n = 7 and β = .05, the chance it refutes is
0.0005, 0.0046, 0.018 and 0.080 at true scales ×1, ×1.5, ×2 and ×3. Because the
pair is adjacent, it also leaves out most of component (f). The screen catches
only gross violations. W1's D 5↔17 pair is the first separated test.

## 5. Residual risk

- **D noisier than assumed.** If D's true relative replay SD is ×2 the 30B
  value, the series false-fail rises to about 15% (×3: about 49%), and almost
  all of the excess lands on D pairs. A failed D pair fails that window's U3: W1
  then fails at the desk and the lead disposes, and a C or T window is barred
  from the pool but still counts toward the 8 (R15). The R1 screen will
  usually not warn in advance.
- **D quieter than assumed.** If D is as quiet as 30B or quieter, D's false-fail
  is negligible, but U3 rarely detects a real D state shift of 2 pilot SDs.
  U3 is then a weak control for D. U4 and U5 carry the state-control burden.
- **Model assumptions.** The bar assumes normal, independent pilot sessions.
  Heavy tails (t₃) raise the series rate to about 15%. The OC is a model
  sensitivity analysis, not hardware validation.
- **Scope of this note.** It covers the 30B→D transfer and the R1→W1 G0 cap
  difference. It does **not** cover these changes:
  - any change to δ_slow, G_turn, N_chunk, power mode, quantization, B_D or
    T_dead between R1 and the W1 D configuration (D-17a,
    `pilot_protocol_v4.md:695-702`);
  - any escalation-ladder change in a later window (`:501-509`).

  Any of them changes `d_configuration_sha256`. It then needs an amended note,
  with a new digest, before step 6, or that window's D pairs are inconclusive.
