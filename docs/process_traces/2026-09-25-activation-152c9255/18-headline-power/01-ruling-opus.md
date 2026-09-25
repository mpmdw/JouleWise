# HEADLINE-POWER-01: blind ruling from the Opus 5.5 seat

Checkout `6d0ae9b0`. Stdlib-only desk simulation (no numpy on this machine). The scripts are in `/tmp/152c9255/pw-opus/`: `sim.py` (sha256 `e36cc8fd…307b5`), `df_check.py` and `boot_check.py`. All runs used 2,000 families with `PYTHONHASHSEED=0`, so the Monte Carlo SE of a family rate near 0.05 is about 0.005. **Every generator input is assumed.** The sourced numbers carry a path:line.

## 0. Facts that change the premise

1. **The pool is not about 800 per level.** Eligible counts for levels 1–5 are **381 / 733 / 924 / 967 / 1,035** (`tests/test_benchmark_import_math.py:291`). AP:21 gives only the total, 4,040. Subtracting the pilot (about 3 per level) and the 10-problem calibration draw (`21-coldgate…ruling.md:85`) leaves a census of about **368 / 720 / 911 / 953 / 1,022**.
2. **There is no Qwen3 throughput measurement in the repo.**
   - The 49 tok/s (8B) and 231 tok/s (1.7B) figures are "planning rates … not measurements" (`docs/process_traces/2026-08-28-workload-consult/01-sol-seat.md:287`).
   - They are also "older 1.5B/7B stand-ins … not a valid 25G83 rate pin" (`…278ebc9e/50-calnight-registration-draft/01-registration-draft.md:19`).
   - The only Qwen3 timing attempt exited at preflight without MLX and recorded no timings (`…278ebc9e/57-calnight-desk-smoke/README.md:11,19-30`).
   - All time figures below are therefore **assumed**. I applied a long-context slowdown of 7% (8B) and 20% (1.7B), anchored on the KV-read growth of +14% and +50% at 4k (`…278ebc9e/10-council-407-seat-fable.md:9`).
3. **The quiet-window bill is about 70, not 20.**
   - The ruling counts 20 null windows (`21-…ruling.md:88`).
   - Claim envelopes add 5 levels × 2 models × k pairs, with k ≥ 5 (`21-…ruling.md:65`). At k = 5 that is 50 more.
   - This bill does not depend on n_acc.

**Generator (all assumed).**
- Accuracy cells, per level, as (8B,hi / 8B,lo / 1.7B,hi / 1.7B,lo):
  - L1: .97 / .90 / .93 / .80
  - L2: .94 / .82 / .87 / .68
  - L3: .90 / .72 / .80 / .55
  - L4: .82 / .58 / .68 / .40
  - L5: .65 / .38 / .48 / .22
  - "hard5" variant: L5 = .30 / .20 / .15 / .05, which is the judge's G4.
- Outcome correlation: a latent-difficulty probit. Within a model, across budgets, ρ = 0.8 (nesting shares the prefix). Across models, ρ = 0.5. The "indep" rows set both to 0.
- Budgets: b_lo = 1k, b_hi = 4k.
- Energy per attempt is proportional to tokens: thinking tokens are min(ℓ, b), plus 250 answer and prefill tokens.
  - ℓ is lognormal with σ = 0.6. The 8B median runs 900 → 4,000 tokens from L1 to L5, and the 1.7B median is 1.3× that. Cross-model length correlation is 0.6.
  - Each block holds one problem, so an envelope holds 10 problems. σ_env = 0.007.
- Assumed F_Δ = 0.03 and B_ln = 0.005.
- The estimator is exactly A-JC-1 v1.1 §A(iii)–(vi) (`21-…ruling.md:67-73`), except that V_acc uses the delta method.
- **Check of that exception:** the delta-method V_acc against the §A(iv) stratified joint bootstrap (R = 1,500) gave √ratios of 0.99–1.02 on the plausible cells and 1.08 on hard5. So the delta method is slightly anti-conservative only for the p = 0.05 cell.

## Power table

Entries are `direction_supported` rates with the correct sign under the full five-level Holm gate. The "Power at 0.223" and "Power at 0.3" columns assume all five levels have the stated Δ.

| Design | FWER at Δ=0 (CP 95% upper) | Power at 0.223, L1–L5 | Power at 0.223, L1–L5, one true level | Power at 0.3, L1–L5 | √V_acc, L1–L5 | SE_energy, L1–L5 |
|---|---|---|---|---|---|---|
| n=128, k=5 | .044 (.053) | .75 .55 .40 .28 .12 | .71 .51 .34 .22 .08 | .96 .86 .74 .55 .29 | .046 … .170 | .040–.051 |
| n=200, k=5 | .053 (.062) | .83 .67 .54 .44 .23 | .78 .59 .45 .34 .14 | .97 .92 .86 .78 .49 | .037 … .136 | same |
| n=368, k=5 | **.061 (.071)** | .86 .74 .67 .63 .43 | .78 .62 .55 .51 .30 | .99 .96 .93 .90 .76 | .027 … .100 | same |
| census, k=5, Welch ν̂ | **.067 (.077)** | .89 .78 .76 .78 .76 | .78 .62 .58 .65 .63 | .99 .97 .97 .97 .97 | .027 .026 .030 .040 .060 | same |
| **census, k=5, ν = projected** | **.031** | .91 .80 .76 .81 .80 | — | — | same | same |
| census, k=5, σ_env=0.03 | .073 (.084) | .89 .77 .74 .79 .77 | — | .99 .97 .95 .97 .97 | same | same |
| census, indep outcomes | .068 (.077) | .87 .77 .72 .69 .56 | — | .99 .96 .95 .94 .87 | .036 … .082 | same |
| census, hard5 | .074 (.084) | .86 .74 .70 .75 **.25** | — | .98 .96 .94 .96 **.51** | L5 .135 | same |
| census, k=10 | .058 (.067) | 1.0 .99 .98 .98 .91 | .99 .97 .94 .93 .78 | ≈1.0 | same | .028–.038 |

**What the table shows:**
- **The judge's power figures do not survive under Qwen3-like accuracies.**
  - At n = 128 I get 0.29–0.96 at Δ = 0.3, not 0.20–0.37. The judge's generator used mid cells near 0.5 and a smaller within-model correlation.
  - "≈ 0 at any feasible n" for a p = 0.05 cell is **false at census**: power is 0.51 at Δ = 0.3 (SD(ln p̂) = √(0.95/(0.05·1022)) = 0.136).
- **Raising n shifts the SE onto the k = 5 energy term.**
  - The energy term has 4 degrees of freedom and a floor of about 0.04–0.05 SE here (assumed heterogeneity).
  - Welch–Satterthwaite then runs hot, because ν̂ and ŝ_d are correlated. Family false admission is 0.061 at n = 368 and 0.067 at census. **Both fail §A(vii)(a) as ruled** (point ≤ 0.06, CP upper ≤ 0.075; `21-…ruling.md:75`).
  - A ν registered from projected variance components fixes this with no power loss. Across 4 designs: census 0.066 → 0.031, n = 368 0.072 → 0.041, n = 200 0.056 → 0.041, census k = 10 0.055 → 0.051.
- **MDE at 80% power (census, k = 5):** about 0.20 at L1 and 0.23–0.24 at L2–L5. At n = 128 it is about 0.30 at L2 and above 0.3 at L4–L5.

## P1. What n_acc per level

**Recommendation: a census of every eligible level-L problem not used in the pilot or calibration draw.** Keep all five levels, Δ_L as the primary, and k = 5. Replace the df rule with ν = min(ν̂_Welch, ν_proj,L).

Why the alternatives lose:
- **Fewer or pooled levels, or dropping or merging the hardest level.** Each breaks the binding "one hypothesis per level, Holm m = 5" (AP:10 item 7) and v5 §6's merge prohibition (AP:69). The table also shows no need: at census, even the hard5 level keeps power 0.51 at Δ = 0.3.
- **A different primary (per-model C trends).** R-Q3(7) fixes the primary on log R_L. Per-model trends stay descriptive.
- **n = 128 or 200.** They leave L4–L5 below 0.5 power at the smallest effect of interest, for about 100 accuracy hours saved. Those hours are off the quiet-window critical path (P2).

The census does not change the 50 claim envelopes or the 20 null windows.

> **Registration text (P1).** `n_acc_rule: "census_v1"`: for each level L, the test draw is every problem of the AP §1 eligible pool at level L that is not in the pilot draw or `calibration_draw`, listed by the importer at registration: expected 368/720/911/953/1022 for L1–L5; exact counts and ID-list SHA-256 are registration fields; `subject_strata[]` are the pool's actual stratum sizes. All five levels remain in the Holm family (m = 5); no level is merged, dropped or pooled for confirmation. `k_planned_pairs: 5`. `df_rule: "welch_satterthwaite_min_projected_v1"`: ν_L = min(ν̂_L, ν_proj,L), where ν_proj,L is the Satterthwaite df computed before any test outcome from SE_proj components (s_d,proj² from pilot token-length heterogeneity at the registered s, b_lo and b_hi, as a design projection only; V_acc,proj from pilot p̂ per cell). Registered secondary, outside the Holm family: pooled Δ̄ = (1/5)Σ_L Δ̂_L, SE = √(Σ SE_L²)/5, two-sided α = 0.05, reported but never a level claim. This is an AP:31 amendment (n > 200) and an A-JC-1 v1.1 §A(v) amendment (df rule), both for the E2 council and cold gate.

## P2. Cost and feasibility

**Accuracy compute (assumed).** Per problem, across four rungs {0, 1k, 2k, 4k}:
- 8B: 56 s at L1 up to 106 s at L5.
- 1.7B: 27–39 s.

| n_acc per level | Accuracy compute | Machine-days at 16 h/day |
|---|---|---|
| 128 | 20 h | 1.3 |
| 200 | 32 h | 2.0 |
| 368 | 58 h | 3.6 |
| **census** | **133 h** | **8.3** |

**Quiet windows.** They are independent of n_acc: 20 null + 50 claim = **70**, at one envelope per window. That is 14.0 days at 5 windows/day and 15.6 days at 4.5/day.

**Is it feasible?**
- Accuracy runs follow the freeze and can interleave with the 50 claim windows. That gives about 11 days × roughly 17 non-window hours ≈ 190 h, against the 133 h needed. So the **census adds no calendar time.**
- The calendar is set by the windows, and it is borderline at 2 weeks under any n_acc.
- k = 10 would need 120 windows (24–30 days), so it is not feasible now.
- Run the energy-subsample problems first in the accuracy queue so that byte-match checks are never waiting.

> **Registration text (P2).** `accuracy_budget_h_projected: 133` (assumed rates 49/231 tok/s × long-context factors 1/1.07 and 1/1.2, to be replaced by the pilot's measured per-model s/token before freeze; if the pilot-projected total exceeds 260 h, fall back to `n_acc = 368` per level, decided on pilot timing only). `quiet_windows_planned: 70` (20 null + 5 levels × 2 models × 5 pairs). `accuracy_queue_order: "energy_subsample_ids_first, then level-interleaved by registration seed"`. Accuracy runs never overlap a quiet window.

## P3. Smallest effect of interest, and wording for a null level

**The smallest effect of interest is |Δ_L| = ln 1.25 = 0.2231: the budget change moves the 8B-to-1.7B J/correct ratio by 25%.**
- It is about 7× the assumed floor F_Δ ≈ 0.03 (`21-…ruling.md:45`).
- A smaller shift would not change which model an operator picks when R is within a factor of 2 of 1.
- It is chosen on meaning, not reverse-engineered from power. Power at this value is 0.76–0.89 per level at census, from my assumed generator.

**How a level that is not admitted is worded.** It is split by the CG-2 equivalence test (TOST, two one-sided tests) at ±0.2231:
- **Null-supported:** the 90% interval lies inside ±0.2231.
- **Underpowered:** the interval straddles a margin.

Analytic TOST power at Δ = 0 is about 0.55 at the Holm-first step and 0.9 or more unadjusted, from the census SEs of about 0.06–0.07. At n = 128 the L5 SE is about 0.18, so equivalence is impossible.

> **Registration text (P3).** `sesoi: {"delta_ln": 0.2231, "meaning": "25 % change in R_L between registered budgets"}`. `projected_power` records per-level power at Δ ∈ {0.1, 0.2, 0.2231, 0.3, 0.5} and `mde_80` from the §A(vii) re-run at the census n. For each level not `direction_supported`: if CG-2 TOST at ±0.2231 (Holm m = 5, α = 0.05, same SE and ν rule) rejects both one-sided nulls, report "`equivalent_within_sesoi`: the budget change moved R_L by less than 25 % (90 % interval [a, b])"; otherwise report "`not_resolved`: the data are compatible with changes from a to b; power at 25 % was P". The words "no effect" and "no difference" are never printed for a `not_resolved` level.

## P4. What would show this recommendation wrong

> **Registration text (P4), pre-declared revisit triggers, evaluated on pilot data only.**
> 1. The §A(vii) acceptance simulation, using the actual bootstrap and the ν-min rule, gives family false admission > 0.06 on any generator: then the census stands and k is raised, or n_acc = 200 is adopted.
> 2. The pilot-projected SE_energy > 0.08 at any level: n_acc beyond 368 buys under 0.05 power, so fall back to 368.
> 3. The pilot shows any cell with p̂ < 0.10 at b_lo: the hard5 row applies and the registration prints that level's power, about 0.25 at the smallest effect of interest.
> 4. Measured 8B decode below 25 tok/s: accuracy > 260 h, so fall back per P2.
> 5. A291 v5 packs ≥ 2 claim envelopes per window: re-cost with k = 10 before freeze, since k = 10 roughly doubles L5 power.

## Concerns

- **BLOCKER (for any n_acc above about 200).** The ruled Welch df fails the ruling's own acceptance criterion (0.061 at n = 368, 0.067 at census). The df amendment in P1 is a precondition.
- **MATERIAL.**
  - The quiet-window count of about 70 is not budgeted anywhere.
  - The per-level pool counts are 381–1,035, not about 800.
  - The judge's power numbers and "≈ 0 at any feasible n" fail under these generators.
  - At census, the no-FPC V_acc means the population is really "level-L MATH-style problems", with the pool as one draw of them. A-JC-1 (i) wording should say so (`21-…ruling.md:63`).
  - The estimand mismatch: Ê_L is a mean of per-problem log ratios, while C = e/p is a log of means. In my generator the gap is about 0.02 (−0.023 to +0.019), which is 9% of the smallest effect of interest (AP §5).
- **NIT.** The 16-problem pilot gives only about 3 problems per level for the s_d projection. That is why ν takes the minimum, not ν_proj alone.

## Where the other seat may disagree

- It may keep n_acc ∈ [128, 200] as the ruled bound, and read census as re-opening R-Q3(4).
- It may prefer df = k − 1 or a larger k over a projected ν.
- It may keep the pool (not superpopulation) population and apply an FPC.
- It may pick a smallest effect of interest of 0.3, or none.
- Its generator may use lower accuracies, like the judge's, and conclude L5 is hopeless.

## Plain summary for Ed

- Level 1 has only 381 usable problems, not about 800.
- Using every usable problem per level lifts per-level power to detect a 25% change in the models' relative efficiency to about 0.75–0.9, up from 0.1–0.75 at 128.
- It costs about 133 machine-hours (an estimate: no Qwen3 speed has been measured). That fits in the gaps between quiet windows.
- Quiet windows, not problem count, set the calendar: about 70 of them, or 14–16 days. That is a separate count nobody has budgeted.
- The gate's current degrees-of-freedom rule gets slightly too permissive at large n (false admission 6–7% instead of 5%). Fixing the degrees of freedom before seeing data cures it at no power cost.
- A level that comes out non-significant gets a pre-written verdict: either "changed by less than 25%" or "not resolved". It is never reported as "no effect".
