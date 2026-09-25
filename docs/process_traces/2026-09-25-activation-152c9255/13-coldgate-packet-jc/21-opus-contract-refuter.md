# Refuter report: Opus 5.5 contract and statistics lens on JCORRECT-FLOOR-01 (ex-30 §P)

Packet `00-charge.md` sha256 64c97214…dc0f was verified. I did not see the judge's ruling. My simulation code is in `/tmp/jc-ref/sim2.py` and `/tmp/jc-ref/sim3.py` (pure Python, fixed seeds). **Assumed** inputs: p per cell from 0.35 to 0.75 (a "mid" level) and 0.05 to 0.35 (a "hard" level); n_acc = 128; energy subsample of 40 problems per cell, spread over k = 5 envelope pairs; 0.7 % instrument scatter per envelope; per-attempt log-energy SD across problems of 0.2, plus a difficulty slope. I report the rate for one level at the strictest Holm step (α/5 = 0.01, two-sided). The floor is fixed at F = 0.0124.

## 1. P-0: the CG-1 accuracy-term BLOCKER

**Affirmed: the BLOCKER is real.** In `estimators.py:398-399`, each observation's variance terms are summed and divided by n². So a term shared by all k envelopes enters as V/k. The WIP helper (`origin/feat/2026-09-24-claimgate-v2:estimators.py` ≈`:490-494`) refuses every scope except `independent_run`, and WR-3 (CGW:69) does the same (`test_shared_scope_refused`). As ruled, p̂ therefore enters either not at all or divided by k.

| Scenario (Δ_L = 0) | Ruled CG-1 (accuracy omitted) | Shared term ÷ k | P-0, df = min(k−1, ·) | P-0, Welch df |
|---|---|---|---|---|
| Energy scatter from the instrument only (synthesis premise) | **0.84** | — | 0.000 | **0.0095** |
| Mid level, problems vary in energy | 0.14–0.15 | 0.012–0.016 | 0.000 | 0.009–0.010 |
| Hard level (p = 0.05 to 0.35) | **0.56–0.58** | 0.022–0.024 | 0.000 | 0.0035 |

- The synthesis's 0.81 is reproduced (0.84).
- Across five levels, the family false-admission rate is about 1 − 0.16⁵ ≈ 1.0 under the ruled text.
- P-0's structure (SE² = V_env/k + V_acc) calibrates: across my generators, the mean SE matches the empirical SD of Δ̂ to within 2 % (0.1587 vs 0.1613; 0.145 vs 0.144; 0.1607 vs 0.1607).
- The P-0 text still has five defects, listed below.

**P0-a — MATERIAL. The df rule makes the gate nearly powerless.** "The smaller of k−1 and the bootstrap's effective n" always equals k−1 = 4, because n_eff is about 128. V_acc dominates the variance: √V_acc ≈ 0.145 against √V_env ≈ 0.006–0.09. With 4 df, the Holm critical value is t_{4,0.995} = 4.60 instead of about 2.6.

- Simulated per-level admission at the mid level: 0.000 at Δ = 0, **0.002 at Δ_L = 0.3**, 0.09 at 0.5.
- With Welch df: 0.009 at Δ = 0, 0.23–0.25 at 0.3, 0.70 at 0.5.

A floor that is too large hides real effects, which is the error the charge warns against. The correct rule is Welch–Satterthwaite (text below). It gave a false-admission rate within 0.0105 of the 0.01 target on every generator.

**P0-b — MATERIAL. The text allows V_env to be counted twice.** P-0 says the draft's bootstrap (AP:61) "supplies" V_acc. AP:61 resamples the energy clusters as well as the accuracy problems, and recomputes the whole contrast. Its variance is therefore about V_acc + V_env, and the formula adds V_env/k on top.

- Simulated effect: conservative, false admission 0.003–0.006.
- Cost: power at Δ_L = 0.3 falls from 0.33 to 0.22 at n = 200, and from 0.53 to 0.32 at n = 400.
- Fix: V_acc must come from an accuracy-only replicate, with energy held at its point estimate.
- The omitted covariance between e and p is **empirically negligible**. It is of order σ_ep/n, because the energy subsample is drawn from inside the accuracy set. I checked this with budget-dependent and model-dependent difficulty slopes; calibration held (0.0095–0.0105). No Cauchy–Schwarz bound is needed; it would cost power (0.24 → 0.08 at Δ_L = 0.3).

**P0-c — MATERIAL. The claim's population is never stated, and the draft contradicts itself.** P-0's V_acc assumes the claim generalizes to the level's population of problems. AP:19 and AP:57 describe C and R "for this frozen set". Under seeded decoding, p on a frozen set is a complete count with zero sampling variance. On that reading V_acc = 0 and the BLOCKER vanishes, but so does any meaning beyond these 128 problems. The amendment has to name the population; the text below does.

A related point: the draw is subject-balanced round-robin (AP:21), so the bootstrap should resample within subject strata. There is also no finite-population correction (128 of about 800 eligible problems per level), which overstates V_acc by about 19 %; this errs conservative and is acceptable if stated.

**P0-d — MATERIAL. The estimand has no envelope form.** CG-1 defines θ as the mean over envelopes of an in-envelope B−A difference. WR-5 (CGW:73) feeds one envelope per observation into `estimate_paired_blocks`. Δ_L cannot be computed inside one envelope, because inv_14 allows one model per envelope (`scored_packer.py:218`) and log p lies outside every envelope.

P-0 amends only the SE. It leaves undefined what k counts, how the 8B and 1.7B envelopes are paired, and the estimator (mean of per-envelope logs, or log of the pooled mean). The text below defines all three.

**P0-e — MATERIAL. Two CG-1 clauses cannot be evaluated in ln units.**
- The anchor bound B is in joules, and P-J1's `ln_ratio` unit gives no conversion.
- CG-1 lets the sign-flip diagnostic bear on decisions once k ≥ 8. That diagnostic sees only envelope scatter, so it must never gate an estimand with a shared accuracy term.

**Power at the draft's planned n_acc (not flagged by any seat).** Assumed mid-level p, Welch df, per-level admission at Δ_L = 0.3:

| n_acc | Per-level power at Δ_L = 0.3 |
|---|---|
| 128 | 0.24 |
| 200 (the AP:31 cap) | 0.33 |
| 400 | 0.53 |

- At the hard level, power is about 0: SE ≈ 0.48, and ln p̂ has a bias of +0.067.
- At n = 400, V_env (√ ≈ 0.067 at n_sub = 40) is comparable to V_acc, so power depends on n_sub as well as n_acc. The synthesis's claim at line 33 ("power is set by n_acc") is only half right.
- The effect size "0.2–0.3" at lines 31 and 84 has no source.
- Accuracy runs take no quiet windows, but they are not cheap. For the 8B at b_high, 400 problems × ≈ 90 s ≈ 10 h per level (assumed).

**Corrected P-0 text (labelled cold-gate amendment A-1 to CG-1; it also applies to CG-2's SE and TOST df):**

> **A-1.** Scope: an estimand containing a correctness fraction measured outside the envelopes (J/correct, `ln_ratio` Δ_L).
>
> (i) Population: the level-L problems of the AP-5M eligible pool (AP §1). The n_acc test problems are its registered subject-balanced draw. Claims are worded "at the registered seed and stack".
>
> (ii) Envelope pairs: pair j = the j-th retained 8B envelope with the j-th retained 1.7B envelope for level L, in capture order. Each envelope holds both registered budgets. k = number of complete pairs; k < 5 → `not_estimable`.
>
> (iii) Estimator: d_j = Σ_c a_c·ln ē_{c,j}, with a = (+,−,−,+) over (8B,hi), (8B,lo), (1.7B,hi), (1.7B,lo). θ̂ = mean_j d_j − Σ_c a_c·ln p̂_c.
>
> (iv) SE² = s_d²/k + V_acc. V_acc is the variance, over 20,000 replicates, of −Σ_c a_c·ln p̂*_c. Each replicate resamples the n_acc problem ids with replacement within subject strata, jointly for the four cells, with energy held fixed. No energy resampling enters V_acc. If more than 1 % of replicates have any p̂*_c = 0 → `not_estimable`, reason `accuracy_denominator_unstable`.
>
> (v) df ν = SE⁴ / [(s_d²/k)²/(k−1) + V_acc²/(n_acc−1)] (Welch–Satterthwaite). Holm p = 2·P(T_ν > |θ̂|/SE). Intervals θ̂ ± t_{ν}·SE. The decision interval is widened by B_ln = Σ_c −ln(1 − B_c/ē_c); B_c ≥ ē_c → `not_estimable`.
>
> (vi) The sign-flip diagnostic bears on no decision for these estimands.
>
> (vii) WR-3 gains `accuracy_artifact{sha256 of the four per-problem correctness vectors, n_acc, scorer_id}`. Until A-1 is installed, a J/correct or `ln_ratio` metric → `claim_shared_accuracy_term_unruled`. After installation, a missing artifact → `accuracy_artifact_unbound`. Both codes go into `reason_kinds.py`.
>
> (viii) CG-4(e) acceptance: 20,000 five-level families per generator:
> - G1: instrument-only energy at 0.7 %;
> - G2: problem-heterogeneous energy with a budget-dependent difficulty slope;
> - G3: the pilot's measured p's;
> - G4: a level with min p ≤ 0.05.
>
> Pass iff, on every generator, the family false-admission rate at Δ = 0 is ≤ 0.05 point estimate with a one-sided 95 % Clopper–Pearson upper bound ≤ 0.06, **and** mean SE / empirical SD(θ̂) is in [0.9, 1.15]. Report per-level power at Δ_L ∈ {0.1, 0.2, 0.3, 0.5}. n_acc and n_sub are set from that table before freeze. Raising n_acc above 200 is an AP:31 amendment.

## 2. Do the proposals contradict ruled text or code?

**C-1 — MATERIAL. P-J3 and P-J1 contradict WR-1; the synthesis presents this as an enum change only.** WR-1 (CGW:65) mints `unit ("J")` under `derivation_rule_id "cg1_f_est.v1"`. It re-derives `block_deltas_j` through `abba_delta` in joules (`detection_floor.py:1449-1453`), binds evidence "with zero problems", and refuses `estimate_floor_model_mismatch` unless every envelope has the same `model_artifact_sha256`. A two-model composite floor in ln units violates each of these. Corrected text:

> P-J1/P-J3 require a labelled WR-1 amendment: new schema `joulewise.estimate_floor_artifact.v2`, `derivation_rule_id "cg1_f_est_ln_ratio.v1"`, unit `ln_ratio`, and `components[{model_artifact_sha256, budget, envelopes[]}]`. The model-mismatch check becomes per component. The per-block value is (ln B1 + ln B2 − ln A1 − ln A2)/2 from member joules. A new scored-null producer (not P2-015's comparative component) binds the problem ids and trace hashes. `estimate_floor.v1` stays unchanged for J.

**C-2 — MATERIAL. The S4 ceiling of 10 % contradicts WR-1's rule that envelopes with n_blocks ≠ n_cal are excluded.** A refused block leaves the envelope with 9 blocks, so the envelope is excluded. At a 10 % block refusal rate, P(envelope intact) = 0.9¹⁰ = 0.35, so k_cal < 5 and the mint returns `not_resolvable` well before the ceiling is reached. Replacement blocks would add selection. The 10 % figure has no derivation. Corrected text:

> A null block whose four members are not byte-identical is refused. Its envelope is excluded and listed under WR-1; no replacement block is run. If any envelope is excluded for byte mismatch, the mint refuses with `estimate_floor_replay_nondeterministic` and A283's determinism gate reopens. Reason: the same defect would breach the AP:47 byte-match of claim reruns.

**C-3 — NIT.** WR-3 already refuses non-independent scopes (`envelope_term_scope_unknown`). But the accuracy term is not a per-block term, so nothing refuses a J/correct metric today. The new code has to be keyed on the metric (A-1 (vii)).

**C-4 — NIT.** The k_cal trigger ("a third of the expected Holm threshold") is undefined. Define it as threshold_L = t_{1−0.005,ν}·SE_L, projected from the pilot's p̂ and the registered n_acc and n_sub. On my numbers F ≈ 0.012–0.04 against a threshold of about 0.38, so the trigger never fires.

**Checks with no contradiction found:** S6/inv_14 (`scored_packer.py:218`), the cap-hit exclusion (`floor_extraction.py:2699-2702`), greedy decoding at HEAD (`mlx_runtime.py:984-988`), and g(k) (`detection_floor.py:846-855`) all match the synthesis.

## 3. S2: one b_lo floor plus a b_high verification pair is not shown to be conservative

**MATERIAL.**

1. **The monotonicity evidence stops short of b_high.** Opus's data (seat `:24-29`) reach 193 J of short fixed-token work, where absolute SD grows like √E. An assumed 8B attempt at b_high is 1–4 kJ at ≈ 90 s, 5–20× past the data. Relative *scatter* probably does fall with energy. Systematic *bias* is a different quantity.
2. **Thermal curvature is invisible to a short-block null.** In an ABBA block of runs of duration D, a concave warming curve gives a bias of (f(1.5D) + f(2.5D) − f(0.5D) − f(3.5D))/2, which is not zero.
   - For a thermal time constant τ of 60–300 s: 0.0003–0.006·c at D = 5 s, against 0.05–0.17·c at D = 90 s, where c is the power rise from cold to hot at fixed work. That is **30–170× larger at b_high**.
   - The bias has the same sign in every block that starts off steady state. A b_lo mint cannot see it.
3. **The verification pair cannot detect a change.** Two envelopes per model give a spread estimate with df = 1, compared against s_cal with df = 4. P(F_{1,4} > 1/r²):

   | True SD ratio r | P(any of 2 models triggers a re-mint) |
   |---|---|
   | 1 (no change) | 0.61 (spurious) |
   | 2 | 0.87 |

   The test is close to a coin flip in both directions. It also tests scatter only, not |mean|. Its comparator, the "per-model component" of a floor defined on ν = x_8B − x_1.7B, is not defined anywhere in CG-1.
4. **No same-config null can see the claim's own carry-over.** In a claim envelope ABBA = lo, hi, hi, lo, the short A2 run follows two long hot runs. The resulting bias differs between models (4.3 GB vs 0.94 GB weights), so it does not cancel in Δ_L. A null at b_lo misses it, and so does a null at b_high.

Corrected text:

> S2: mint per model at both (b_lo, lowest-energy level) and (b_high, highest-energy level), k_cal = 5 each. F = max(F_lo, F_hi), where each is CG-1's formula on ν. This adds about 6 one-hour envelopes over the synthesis's 10 + 4.
>
> Claim envelopes alternate ABBA and BAAB (C407:36) under a registered fixed pre-run idle (or a thermal-pressure threshold). Carry-over check: if |mean d(ABBA) − mean d(BAAB)| > 2·SE_env, then `carryover_detected` and the level is not resolved.
>
> Disclosure: at the planned n_acc, F (≈ 0.01–0.04) is below SE/3, so the transfer risk affects the floor check rather than the Holm or interval checks.

## 4. S5: pilot-set null vs outcome-blind freeze

**Affirm the pilot set over test problems.** Opus's order conflicts with AP:27 twice over: running test problems inside a null *creates* test outcomes before the registration hash, whether or not anyone scores them.

- **NIT, better option:** the pilot has 16 problems across five levels, about 3 per level. A third disjoint draw from the eligible pool would give ≥ 10 problems at each used level, one per null block, so no single problem dominates. It uses the same round-robin with its own domain string. It is outcome-blind at no quiet-window cost. It needs a one-line amendment to AP §1.
- **NIT, ordering:** the nulls must also come *after* the pilot fixes (b_low, b_high) and after A283 freezes the stack. P-J4 states neither. Suggested text: "null windows follow pilot pair selection and the A283 stack freeze; any stack change after the mint voids the floor."

## 5. Missed by all seats and the synthesis (F3)

1. **MATERIAL:** the claim's population (P0-c).
2. **MATERIAL:** power at n_acc = 128 is about 0.24 per level at Δ_L = 0.3, and about 0 at hard levels (§1).
3. **MATERIAL:** the anchor bound B has no conversion to ln units (P0-e).
4. **NIT:** AP:47 draws energy subsamples per (model, level, budget). Using the same ids across both budgets would keep problem-level pairing inside d_j; the nested design makes this free.

## Tier summary

| Tier | Findings |
|---|---|
| BLOCKER (affirmed) | P-0 as a defect: the ruled CG-1 gives 0.84 false admission per level on the instrument-only premise |
| MATERIAL | P0-a (df rule), P0-b (V_env counted twice), P0-c (population), P0-d (no envelope form), P0-e (B conversion and sign-flip), C-1 (WR-1 contradiction), C-2 (10 % ceiling vs WR-1 exclusion), S2 (floor transfer not shown conservative), power at planned n_acc |
| NIT | C-3, C-4, S5 calibration draw and ordering, same subsample ids across budgets |
