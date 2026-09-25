# Cold Fable gate ruling — CLAIMGATE-01 (packet 66)

Judge: Claude Fable 5.1, cold session, 2026-09-24 17:05–17:20 PDT. Worktree HEAD `9196e8b7`. Read-only except this file. No subagents, no background tasks, no sudo/launchctl/powermetrics/systemsetup, no canonical root, no custody dirs, no discovery suite.

## 0. Disclosure and trust anchors

Auto-loaded before any action: global `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and the memory index `MEMORY.md` (truncated). None was requested; none is used here. Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory files, any `docs/process_traces` file outside packet 66 (including `19-desk-simulations/sim.py`, the AP-5M v5 draft, and the O-21 harvest file).

Validator (`scripts/validate_gate_packet.py`, receipt schema `coldgate-validator-receipt/v2`):
- Run 1, expected charter sha `…95d82` (deliberate typo): observed `…95d81`, result **REFUSE**, reason `charter_trusted_observed_mismatch`, rc=2.
- Run 2, expected charter `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`, expected packet `630d4978a3bf9baa50d0f71faf078388d413a7ae86ccb069f022a84522f844c9`: observed both equal, all 14 exhibits `expected_sha256 == observed_sha256`, manifest sha `296c2bc2…1e1c7c`, result **PASS**, rc=0.
- Independent method: `shasum -a 256` on both files reproduced both digests.

Charter §9 satisfied; merits follow.

## 1. Packet hygiene (charter §6)

- **H1 (MATERIAL).** O-21 (Ed's floor decision) and the AP-5M v5 draft are cited as controlling authority in ex-55-03 and ex-55-00 but only by path into process_traces files outside the packet; the packet offers paraphrase, not the bounded verbatim excerpt §4 requires. I rule on the paraphrase "a claimed J/correct difference must also clear an applicable instrument floor `|estimate|>F`" because every seat and the synthesis accept it; the cure is in CG-4 (Ed is told which F now satisfies it).
- **H2 (NIT).** The charge's summary ("misses 84 % of 5σ effects", "covers about 56 %", "false-alarms 58 %", "blind to ×4") matches ex-19 README lines 44–46 and 57–59; no cherry-picking found.
- **H3 (MATERIAL).** The synthesis (ex-65) omits three seat findings that bear on its own rulings: Fable §(e) "contradicts the numerical shape Ed fixed in issue 316 … needs Ed's notice"; Sol F3 and Astra F3 (AP-5M's log-ratio contrast has no conversion to the J/correct difference O-21 gates); Astra "directional and equivalence claims must not become two independently searched families". Effects ruled under M3, M4, M5.

## 2. Verified facts the ruling rests on

- `claims.py:343-344` strict point test `abs(estimate) <= floor → effect_not_above_floor`; `:369-382` both intervals must exclude zero, else `unresolved`/`not_resolvable`; `:346-368` equivalence requires margin > floor and BOTH supplied intervals inside ±margin.
- `estimators.py:465-486` df = n−1 over blocks, SE from block scatter, 95 % fixed (`_ci_t_critical` = `student_t_quantile(0.975, df)`, line 228); deterministic total = mean of per-observation bounds (`_deterministic_bound_totals`).
- `detection_floor.py:871-881` prediction term `t·s·sqrt(1+1/n)` plus `max_abs`; guard `sqrt(9/(n−1))` for 5 ≤ n < 10 (`:850-854`); `comparative_false_effect_floor` never re-centres (`:1132-1152`).
- `multiplicity.py:49-77` Holm keeps `None` members in m.
- `epoch_equivalence_check.py:127` `MINIMUM_RETAINED_M = 6` ("Issue 316"); `:480-536` max ≤ level screen AND range ≤ bracket screen. Docstring lines 1–10: shape fixed by Ed's directive issue 316 before capture.
- `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`: 17 members over **10 windows** (a, a2–a10; 1/1/1/1/3/1/2/2/3/2 members) and 4 dates; total SD 2.461 ms; pooled within-window SD 1.98 ms (df 7); window-mean SD 2.71 ms. Opus's re-basing claim is correct; the desk model's single-night old corpus is wrong.
- D-083 addendum (`decision_log.md:11291-11303`): checks stay separate; conjunction `|estimate|>max(F, h+B)`; "preserve its rejection of an additive acceptance gate". D-078 addendum (`:11268-11283`): F+B non-gating.
- `distributions.py:174` has `exact_sign_flip_p_value` already; with k = 5 envelopes the smallest attainable two-sided p is 2/2⁵ = 0.0625.
- Existing consumers of `direction_supported`: `docs/paper/fill-rehearsal/*gamma-claim-verdicts.json` are marked SYNTHETIC-REHEARSAL; `docs/paper/round7/dependence-sensitivity.md:14` "never issues it"; `configs/analysis_registry/ap_spec_*.v2.json` are `pending_p2_015` and inherit the contract row `docs/contracts/analysis_plans.md:29` ("Floor gate: `max(floor_abs_j, floor_cmp_j)`").

## 3. Probe (own harness, production `student_t_quantile`, `student_t_cdf`, `holm_adjust`, `small_sample_guard_factor`)

`python3 /tmp/278ebc9e/cg-judge/sim_judge.py 200` (24 s; script and output under `/tmp/278ebc9e/cg-judge/`). Four generators as ex-19 describes them (gaussian, t3, centred drift, shared-plus-local timing), k = 5 envelopes × 6 blocks, between-envelope shock τ ∈ {0, 0.5σ}, n_cal = 8, Holm m = 5 with one tested contrast (worst rank). Two magnitude forms, both with Holm p < 0.05 and decision interval excluding 0:
- **SUM** = synthesis CG-1 cond. 3, near endpoint > F_est (equivalently |θ̂| > F_est + h + B);
- **MAX** = D-083 form, strict point test |θ̂| > F_est.

| state (τ = 0.5σ, mean over 4 models) | SUM | MAX |
|---|---:|---:|
| δ = 0, no offset (24 cells, both τ) | 0.000 | 0.000 |
| δ = 0, instrument null offset 1σ | 0.000 | ≤ 0.035 |
| δ = 0, null offset 2σ (worst cell: t3, w = 0.5σ) | ≤ 0.005 | 0.065 |
| δ = 2σ, w = 0.5 / 1 / 2σ | 0.11 / 0.01 / 0.00 | 0.78 / 0.55 / 0.03 |
| δ = 3σ, w = 0.5 / 1 / 2σ | 0.69 / 0.32 / 0.00 | 0.99 / 0.98 / 0.51 |
| δ = 5σ, all w | 0.85 (0.51–1.00) | 0.998 |

Equivalence night, re-based on the r7 layout (old = 17 values over 10 windows, within 1.98 ms, between 2.1 ms; new night m = 12 with its own shock), location TOST df = 11, PASS rates:

| Δ_loc | no change | +3σ (7.4 ms) | +5σ | ×4 var |
|---|---:|---:|---:|---:|
| ±3 ms (synthesis) | **0.480** | 0.000 | 0.000 | 0.13 |
| ±5 ms | 0.815 | 0.035 | 0.000 | 0.49 |
| ±8.61 ms (3.5·s_old) | 0.990 | 0.385 | 0.015 | 0.82 |

Spread, one-sided permutation test of log(var_new/var_old) on the 29 pooled values, FAIL if p < 0.05: ×1 0.000, ×4 0.31, ×16 0.98.

## 4. Rulings

### M1 (CG-1, directional) — AFFIRM replicate, F_est scale, Holm, interval; REJECT condition 3 and the k = 5 sign-flip sensitivity; write different text.

- **Replicate = envelope mean, k ≥ 5, df = k−1: AFFIRM.** Deciding evidence: `estimators.py:465-467` uses block scatter; ex-19 README line 44 coverage 0.565 is the consequence; my probe's decision-interval false admission is 0 at τ = 0.5σ under the envelope interval.
- **F_est on the mean scale: AFFIRM the scale, AMEND the formula (MATERIAL).** The synthesis's `s_cal/√n_cal` over calibration *blocks* treats them as independent, reintroducing at the floor exactly the between-envelope defect the council removed from the claim interval (r7 itself spans 10 windows with a between-window SD ≈ within SD). F_est must use calibration envelope means.
- **Condition 3 (near endpoint > F_est): REJECT (MATERIAL).** It is an additive gate F_est + h + B, contrary to the ratified D-083 addendum (`decision_log.md:11294-11299`), which the synthesis neither cites nor supersedes; its only stated reason is "the most conservative … that still admits real effects", which is strictness without a stated science reason (Ed's standard, charge §Background). Probe: it buys ≤ 0.06 of false-admission protection in one adverse cell (2σ instrument offset with heavy tails and n_cal = 8) at the price of 2σ power 0.78 → 0.11 and 3σ power 0.99 → 0.69. The ratified point form with F = F_est already holds false admission at 0.000 with no offset and ≤ 0.035 at a 1σ offset. Magnitude claims ("by more than τ") get their own registered shape (Opus, Sol, Astra concur), below.
- **Sign-flip sensitivity: REJECT at k < 8 (MATERIAL).** With k = 5 its minimum two-sided p is 0.0625; under Holm m = 5 the first-rank threshold is 0.01, needing 2^k ≥ 200, k ≥ 8. A registered sensitivity that can never reject is not a sensitivity.
- **Scope ≥ 3 distinct nights: AFFIRM**, with "night" defined.
- Operating characteristics of the ruled rule (probe, τ = 0.5σ): false admission 0.000 (0 offset), ≤ 0.065 worst adverse cell; power 2σ 0.78 / 0.55 / 0.03 at w = 0.5 / 1 / 2σ; 5σ ≥ 0.985 everywhere. A 2σ effect at w = 2σ is unresolvable by physics (all seats agree); report it as an instrument limit.

### M2 (CG-2, equivalence claim) — AFFIRM margin logic; write different text (MATERIAL ×3).

(i) The TOST p-value must be computed against the same effective margin Δ − F_est as the interval, or the two conditions test different hypotheses; the synthesis leaves the p's margin unstated. (ii) "90 % decision interval" does not exist in production: `_ci_t_critical` is fixed at 0.975 and `claims.py:361-363` tests the supplied 95 % intervals; CG-4 lists no such change. The estimator needs a `confidence` parameter and the artifact a recorded level. (iii) Astra's dropped rule: one contrast registers ONE claim shape (direction OR equivalence OR magnitude) before data.

### M3 (CG-3, equivalence night) — AFFIRM m ≥ 8, TOST location, re-based precondition; REJECT ±3 ms and the night-mean variance ratio; write different text.

- **±3 ms: REJECT (BLOCKER).** It is Astra's constant from a 64-nights-per-era design (ex-60 lines 154–158) transplanted to a one-night test. Re-based probe: no-change PASS 0.480, i.e. a 52 % false FAIL, no better than the 58 % of the rule it replaces. At 3.5·s_old = 8.61 ms (the desk/Fable value) false FAIL is 1 % with +5σ detection 98.5 %; +3σ is missed 38 % (Fable §(f)3 explains why that is tolerable: the level screen refuses such captures pre-flight).
- **Night-mean variance ratio: REJECT (BLOCKER).** One new night has one night mean; its between-night variance is unidentifiable (Astra ex-60 line 182 says so explicitly). The magistrate cannot execute the text.
- **Spread test: write** the one-sided permutation test (Fable seat; probe: false FAIL 0.000, ×4 detection 0.31, ×16 0.98 under the re-based model). Weak ×4 power is a design fact of one night (Opus ex-61 line 52); the ×4 target is reported, not gated.
- **Supersedes Ed's issue-316 shape (MATERIAL, dropped by synthesis):** prospective only; Ed informed before the first night uses it; historical verdicts keep their bytes (charter §9).

### M4 (CG-4, implementation) — AFFIRM one PR, rules before data, D-numbered constants, simulation before use; write different text (MATERIAL ×3).

(i) "Block floor stays for window admission" is a category error: F_block is a *contrast* floor; window admission is the reducer reason set (`claims.py:40-73`). F_block stays as the published single-block instrument characteristic. (ii) The contract row `docs/contracts/analysis_plans.md:29` is the controlling text every pending registration inherits; it needs a versioned second entry, and the D-083 addendum needs a dated second addendum for the estimate-scale floor. (iii) AP-5M estimand (Sol F3, Astra F3, open fact 10, dropped): F_est is in joules; it cannot gate a log ratio-of-ratios; AP-5M must register an additive J/correct contrast (or a registered dimensionless margin with a matched, derived floor) before data. **Affected registrations:** no issued claim (fill-rehearsal files are synthetic; round7 sheet never issues); `ap_spec_draft_front.v2` and `ap_spec_native_mtp_front.v2` are `pending_p2_015` and keep the block-floor row until re-registered under the new version; O-21 is satisfied with F = F_est but Ed must be told that is the reading.

### M5 (dropped/merged) — see H3 and the items above; additionally (NIT): Opus's calibration-size lever (k_cal 5→16 raises 2σ power 0.08→0.38) belongs in the registration's sizing row; Opus's A/A floor-transfer spot-check is unsimulated and stays a proposal.

## 5. Claim-gate rulings (final texts)

**CG-1 (directional claim).** Estimand θ = E[B−A] in joules (or J/correct) over the registered block population on one frozen instrument epoch, registered sign. Replicate = envelope mean: for each quiet-window envelope e with n_e blocks, value_a = mean of block A values, value_b = mean of block B values, each stochastic metrology term = the block term divided by √n_e, each deterministic term = mean of the per-block bounds; feed the k envelope observations to `estimate_paired_blocks` (df = k−1). Register k ≥ 5; k < 5 → `not_estimable`. F_est = g(k_cal)·(|mean_cal| + t_{0.975,k_cal−1}·s_cal/√k_cal) where mean_cal and s_cal are the mean and SD of the k_cal envelope-mean null (same-model ABBA) contrasts of the same-epoch accepted calibration, g = `small_sample_guard_factor`; k_cal < 5 → `not_resolvable`. F_est contains no timing term; B enters once, on the claim side. Admit `direction_supported` iff all hold: (1) Holm-adjusted two-sided p < 0.05 at frozen m (AP-5M: 5, missing kept); (2) metrology interval and decision interval θ̂ ± (h+B) both exclude 0 on the registered side; (3) |θ̂| > F_est strictly (O-21 with F = F_est). Optional registered **magnitude claim** "by more than τ": register τ ≥ F_est in joules before data; additionally require decision-interval near endpoint > τ and Holm on the shifted null p = P(T > (|θ̂|−τ)/SE). Claim wording is scoped to the measured nights unless blocks span ≥ 3 distinct calendar-date sessions. Sign-flip (`exact_sign_flip_p_value`) is reported as a diagnostic only, with its minimum attainable p printed; it bears on no decision when k < 8. F_block remains the published single-block instrument characteristic and never gates a mean.

**CG-2 (equivalence claim).** Register Δ in the estimand's joules, Δ ≥ F_est + B, before data. Effective margin Δ_eff = Δ − F_est. Admit `equivalent` iff the clustered (CG-1 replicate) 1−2α = 90 % metrology interval, widened by B, lies strictly inside ±Δ_eff AND the Holm-adjusted `tost_p_value(θ̂, SE, k−1, Δ_eff)` < 0.05. Implementation: `estimate_paired_blocks` gains `confidence` (default 0.95; equivalence path passes 0.90) recorded in the artifact; `claims.py:361-363` tests the 90 % intervals for this path. Each registered contrast names exactly one claim shape (direction, magnitude, or equivalence); a second shape on the same contrast is a new registration after the first is issued.

**CG-3 (equivalence night, prospective, supersedes the issue-316 numerical shape; Ed informed before first use).** INCONCLUSIVE if retained m < 8. Location: TOST of new mean vs old-corpus mean, margin Δ_loc = 3.5·s_old (r7: 8.61 ms), 90 % interval with SE = sqrt(s_old²/n_old + s_new²/m), df = min(n_old−1, m−1); PASS iff the interval is strictly inside ±Δ_loc. Spread: one-sided permutation test of log(s_new²/s_old²) over the pooled n_old+m values, ≥ 2000 permutations, FAIL iff p < 0.05 (increase only). Verdict PASS iff both pass; else FAIL. Diagnostics printed, non-gating: count of new values above the level screen; new range vs bracket screen. Precondition to registration: re-run the desk simulation with the old corpus laid out as r7's 10 windows (within-window and between-window components estimated from the JSON) and report no-change false FAIL (must be ≤ 5 % on every generator), +3σ, +5σ, ×4 and ×16 detection; commit results before the first night.

**CG-4 (implementation).** One PR, full tier, rules before data, in this order: (a) D-083 dated second addendum: for mean-scale claims the floor role is F_est (CG-1) and the conjunction stays `|θ̂| > max(F_est, h+B)` with separate checks; no additive gate. (b) `docs/contracts/analysis_plans.md:29` Floor-gate row gains a versioned entry "estimate-scale floor F_est (rule v2) for mean/envelope claims; block floor v1 for single-block claims"; `pending_p2_015` specs keep v1 until re-registered. (c) Code: envelope aggregation helper + `confidence` parameter in `estimators.py`; `floor_est_j` producer beside `floor_gate_j` with `floor_class` metadata so F_block can never be passed for a mean; new reason code `floor_class_mismatch`; `epoch_equivalence_check.py:127,480-536` replaced per CG-3 with the old rule kept behind a version flag for historical replay. (d) Every constant (k ≥ 5, k_cal ≥ 5, m ≥ 8, 3.5·s_old, 0.90, 2000 permutations) gets a D-numbered addendum. (e) Desk simulation re-run on CG-1/CG-2/CG-3 exactly as ruled and committed before any claim-bearing use. (f) AP-5M v5 registers an additive J/correct contrast as the primary estimand (or a registered dimensionless margin with a derived, matched floor), cites CG-1/CG-2 by id, and rewrites its "block window must clear floor_gate_j" sentence to name the window-admission reason codes. (g) Ed is informed, per D-184's after-the-fact rule, that O-21's F is implemented as F_est and that issue 316's night shape is superseded prospectively.

## 6. Severity ledger

BLOCKER: CG-3 ±3 ms (52 % false FAIL); CG-3 night-mean variance ratio (non-executable). MATERIAL: CG-1 cond. 3 overrides D-083 silently and costs most 2σ–3σ power; F_est built on independent calibration blocks; sign-flip sensitivity vacuous at k = 5; CG-2 unstated TOST margin and nonexistent 90 % interval; single-claim-shape rule dropped; CG-4 window-admission category error; contract row and D-083 addendum not named; AP-5M estimand mapping dropped; issue-316 supersession and O-21 reading not surfaced to Ed; H1 paraphrased authority. NIT: H2; calibration-size lever; A/A spot-check.

## 7. Plain-language summary for Ed

1. The council is right that the gate compares a mean with a one-block floor and that nights, not blocks, are the replicate. I keep both fixes.
2. I removed the extra "whole interval must clear the floor" test: it contradicts your D-083 ruling, was justified only as "most conservative", and cuts power at 2–3σ effects by two thirds for almost no protection.
3. Sign claims use the strict point test against the new mean-scale floor; "bigger than τ" claims register τ first.
4. The equivalence-night ±3 ms tolerance would fail half of unchanged nights, as bad as today's rule; I set 8.6 ms, which fails 1 %.
5. The "night-mean variance" test cannot be computed from one night; a one-sided spread test replaces it. It catches a ×16 spread change nearly always and a ×4 change about a third of the time; one night cannot do better.
6. Nothing already published is affected; two pending analysis specs keep the old floor until re-registered.
7. AP-5M must state its headline as a J/correct difference before data; a log ratio cannot be gated by a floor in joules.
8. Two things need your notice, not your work: the night rule replaces the shape you fixed in issue 316, and O-21's floor is now the mean-scale floor.
