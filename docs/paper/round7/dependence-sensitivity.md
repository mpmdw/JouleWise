# Dependence sensitivity for the registered `_v5` direction screen

`_v5` is the fixed name of this campaign configuration. A **direction screen** is the registered rule that accepts a direction only when every endpoint of each required interval is strictly on the same side of zero. This pre-registered analysis fixes its calculation and report before the campaign produces contrast data. It tests how a possible relation between successive blocks changes only the uncertainty caused by block-to-block repeat variation. It does not change a metrology input or create a final two-contrast result.

One A/B/B/A block is ordered A, then B, then B, then A. For block \(i\), its signed energy difference is \(d_i=(B_{i1}+B_{i2}-A_{i1}-A_{i2})/2\). Positive means B used more energy than A. There are exactly ten complete blocks per contrast. This order counters a simple time trend, a gradual change over a run, but does not prove that one block is unrelated to the next.

## Terms and registered components

The **sample mean** \(\bar d\) is the ten deltas added and divided by ten. The **sample standard deviation** \(s\) is the square root of (the summed squared distances from \(\bar d\) divided by \(n-1\)). A **standard error** (SE) is the estimated spread of repeated sample means. A **critical value** is the Student-*t* distribution cutoff for the chosen coverage and degrees of freedom (a pure number, for example 2.262). A **half-width** is the critical value multiplied by an SE, so an interval is its centre minus and plus the half-width. A **Student-*t* statistic** is the mean divided by its total SE; its **raw two-sided p-value** is the chance, under a zero mean in that Student-*t* model, of a magnitude at least as large in either direction.

A **variance multiplier** \(V\) says how much dependence multiplies the repeat variance of the mean. An **effective sample size** \(n_{\mathrm{eff}}\) is the number of independent blocks that would have the same repeat SE. A **degree of freedom** \(\nu\) selects the small-sample Student-*t* reference; fewer degrees make its critical value larger. **Alpha** is the fixed chance of missing the stated two-sided interval coverage. It is \(\alpha=0.05\), frozen with a two-comparison family adjustment (\(m=2\)) in configs/campaigns/d117_contrast_v5/generate_configs.py: the generator field `"family_alpha": 0.05` is at line 1859, and the field `"multiplicity": {"method": "holm", "alpha": 0.05, …, "m": 2}` is at line 2578. The \(m=2\) adjustment applies to p-values only; every interval in this sheet is an unadjusted two-sided 95% interval (engine `joulewise/estimators.py:226`, script \(t_{0.975}\)).

**Stochastic metrology** is random measurement uncertainty carried by the registered engine as se_metrology; it is combined with repeat uncertainty by root-sum-of-squares, meaning square each SE, add them, then take the square root. A **metrology-aware interval** uses that combined SE. **Deterministic metrology** is a non-random allowed measurement amount carried by the engine as deterministic_bound_total; it widens the metrology-aware interval into the **decision interval** but is not variance. The **floor gate** is the strict check \(|\bar d|>F\), where \(F\) is the already-issued energy-resolution floor in joules. The **direction gate** is the strict common-sign check on both intervals: this screen's direction gate is the strict sign check only; the registered claim outcome additionally requires the floor check and the two-contrast Holm rejection (`joulewise/claims.py:362-375`), and this sheet never issues it. Equality with a floor or zero fails the relevant strict check.

An **independent unit** is the smallest observation treated as a separate draw: one complete A/B/B/A block, never a **member run** (one of its four measurements). A **sampler phase** is the short measurement phase reported by the meter. A **deterministic drift allowance** is a non-random amount reserved for possible measurement change over time. Session calibration, thermal path, background conditions, neighbouring sampler phases, local drift, and paired order can make block values move together.

| Reported quantity | Independent unit | Shared components | Degrees of freedom | Missing-block rule |
|---|---|---|---|---|
| Block delta \(d_i\) | One complete A/B/B/A block | Session state, local drift, paired order, and the immediate state shared by its four member runs | None | If any member is absent, invalid, or not admitted, the contrast cannot enter the registered claim procedure. |
| Mean and repeat spread | Ten complete deltas | Shared components can make blocks move together; forty member runs are never forty independent observations. | Independent model: \(n-1=9\) | No shortened set, replacement, or outcome-driven top-up (adding blocks after seeing a result). |
| Fully composed result | Ten deltas plus issued se_metrology and deterministic_bound_total | Dependence changes only the repeat SE. Metrology inputs retain their issued values. | Model-specific \(\nu\) below | Do not calculate a registered result unless all ten blocks are present. |

## Fixed sensitivity procedure

For each contrast, retain all ten \(d_i\) values in collection order. The calculator refuses any count other than ten. It requires the issued floor \(F\), se_metrology in joules, and deterministic_bound_total in joules. It does not accept an alpha option: \(0.05\) is registered and fixed.

For every model, dependence changes only the repeat component:

\[
\mathrm{SE}_{\mathrm{repeat,model}}=s\sqrt{V}/\sqrt{n}=s/\sqrt{n_{\mathrm{eff}}},
\qquad
\mathrm{SE}_{\mathrm{total}}=\operatorname{hypot}(\mathrm{SE}_{\mathrm{repeat,model}},\mathrm{SE}_{\mathrm{metrology}}).
\]

With the registered three-decimal critical value \(t_{0.975,\nu}\), the calculator reports a repeat-only interval only as an intermediate arithmetic check, with no gate attached. It then forms the metrology-aware interval \(\bar d\mathbin{\pm}t_{0.975,\nu}\mathrm{SE}_{\mathrm{total}}\), and widens that to the decision interval by subtracting deterministic_bound_total from its lower endpoint and adding it to its upper endpoint. The direction gate passes only when both endpoints of the metrology-aware interval have one strict sign and both endpoints of the decision interval have that same strict sign. The raw p-value uses \(\mathrm{SE}_{\mathrm{total}}\), not repeat-only SE. This replicates estimate_paired_blocks in joulewise/analysis_engine/estimators.py and the interval check in joulewise/analysis_engine/claims.py.

Run all three models, even if the first direction gate passes.

1. **Registered composition with \(n_{\mathrm{eff}}=n\).** Set \(V=1\), \(n_{\mathrm{eff}}=10\), and \(\nu=9\). At \(\rho=0\), this exactly reproduces registered-engine arithmetic.

2. **AR(1) estimated-adjacency model.** AR(1), or first-order autoregression, lets each block be related to the immediately preceding block. Centre each delta (subtract the common mean), multiply each preceding/following pair, sum those products, and divide by preceding centred squares:

   \[
   \hat\rho=\frac{\sum_{i=2}^{n}(d_i-\bar d)(d_{i-1}-\bar d)}{\sum_{i=2}^{n}(d_{i-1}-\bar d)^2}.
   \]

   This uses nine adjacent pairs. It is not pulled toward zero or forced inside an allowed range: if its denominator is zero, it is not finite, or \(|\hat\rho|\ge1\), the calculation refuses. Use \(V=1+2\sum_{k=1}^{n-1}(1-k/n)\hat\rho^k\), \(n_{\mathrm{eff}}=n/V\), and \(\nu=\min(n-1,\lfloor n_{\mathrm{eff}}\rfloor-1)\), where \(\lfloor x\rfloor\) is \(x\) rounded down to a whole number. The finite sum counts each separation among ten observed positions. Refuse if fewer than two effective blocks remain. At \(\hat\rho=0\), \(V=1\).

3. **Fixed effective-n halving (a named pessimistic scenario, not a bound).** Set \(n_{\mathrm{eff}}=5\), \(V=2\), and \(\nu=4\). This is not a mathematical worst case: for \(n=10\) and \(\rho=0.5\), the finite formula gives \(V=2.600391\) and \(n_{\mathrm{eff}}=3.845576\), already more adverse than five; at \(\rho=0.9\), \(n_{\mathrm{eff}}=1.374341\).

The raw p-values are audit values, not a final result. **Holm** is the fixed two-comparison procedure: order the two raw p-values, reject when \(p_{(1)}\le0.025\), then reject the second when \(p_{(2)}\le0.05\); equality passes. The single-contrast calculator emits no Holm or final claim verdict, because the other contrast is required.

## Pre-registered disagreement sentence

The paper lists all three metrology-aware and decision intervals, the floor gate, and the direction gate. If the three direction-gate outcomes disagree, it prints this sentence, replacing the bracketed word mechanically with the registered direction-gate outcome supplied by DS-31 for decode or PG-07 for prefill:

> “The registered independent-block direction gate [passed/failed], but the pre-registered dependence-sensitivity analyses did not agree; we therefore report the signed estimate and all three intervals and do not state that this session establishes the registered direction.”

Agreement does not prove independence. It says only that these calculations did not change this screen; the other contrast's inclusive Holm calculation remains required before any final claim result.

## Calibration-bound wording if pulse independence is not defended

Here **onset** means a pulse start and **offset** means its end. A **population-coverage bound** claims to cover a stated fraction of possible future values with stated confidence; a **deterministic out-of-sample guarantee** would cover future values without probability. Reuse this ratified H30 replacement verbatim; it replaces any competing calibration sentence ([retensing-plan.md, H30](retensing-plan.md#h30--appendix-a36--draft-line-652--added-r7-item-6-9595-label)).

> The pulse portion of the calibration bound is the largest of 118 observed onset and offset excursions from 59 commanded pulses in one capture; the clock-anchor allowance is then added. Because those pulses share one capture and the paper has not shown independence across pulse order or between onset and offset errors, this value is reported as the observed sample maximum, not as a “95/95” population-coverage bound. It is not a deterministic out-of-sample guarantee.

## Worked pre-collection example

These invented values are an arithmetic check, not measurement data or a campaign-floor setting. Let \(F=3.500000\) J, se_metrology \(=0.200000\) J, and deterministic_bound_total \(=4.000000\) J. Use these ten ordered deltas in joules:

| Input | Value |
|---|---|
| Ordered block deltas (J) | `[5.0, 7.6, 5.5, 4.2, 4.7, 6.8, 5.5, 3.6, 3.9, 3.2]` |

The deltas are written to one decimal place so a reader can redo the arithmetic by hand, and the script prints the same values.

Their sum is \(50.000000\) J, so \(\bar d=5.000000\) J. The squared deviations sum to \(17.640000\) J\(^2\), hence \(s=1.400000\) J. The centred adjacent-product numerator is \(4.320000\) J\(^2\), the preceding centred-squares denominator is \(14.400000\) J\(^2\), and \(\hat\rho=0.300000\). The nine AR(1) terms, in lag order one through nine, are \(0.270000, 0.072000, 0.018900, 0.004860, 0.001215, 0.000292, 0.000066, 0.000013, 0.000002\).

For registered composition with \(n_{\mathrm{eff}}=n\), \(V=1.000000\), \(n_{\mathrm{eff}}=10.000000\), and \(\nu=9\). Its repeat SE is \(0.442719\) J; the repeat-only intermediate interval is \([3.998570, 6.001430]\) J. Its total SE is \(0.485798\) J, critical value \(2.262000\), and half-width \(1.098876\) J. The metrology-aware interval is \([3.901124, 6.098876]\) J; the decision interval is \([-0.098876, 10.098876]\) J. The *t* statistic is \(10.292337\), and raw two-sided p-value \(0.000002814\). The floor gate passes, but the direction gate fails because the decision interval contains zero.

For AR(1), the terms sum to \(0.367347\), so \(V=1.734695\), \(n_{\mathrm{eff}}=5.764703\), and \(\nu=4\). Its repeat SE is \(0.583095\) J; the repeat-only intermediate interval is \([3.381327, 6.618673]\) J. Its total SE is \(0.616442\) J, critical value \(2.776000\), and half-width \(1.711242\) J. The metrology-aware interval is \([3.288758, 6.711242]\) J; the decision interval is \([-0.711242, 10.711242]\) J. The *t* statistic is \(8.111070\), and raw two-sided p-value \(0.001256214\). The floor gate passes and the direction gate fails.

For fixed effective-n halving, \(V=2.000000\), \(n_{\mathrm{eff}}=5.000000\), and \(\nu=4\). Its repeat SE is \(0.626099\) J; the repeat-only intermediate interval is \([3.261949, 6.738051]\) J. Its total SE is \(0.657267\) J, critical value \(2.776000\), and half-width \(1.824573\) J. The metrology-aware interval is \([3.175427, 6.824573]\) J; the decision interval is \([-0.824573, 10.824573]\) J. The *t* statistic is \(7.607258\), and raw two-sided p-value \(0.001602484\). The floor gate passes and the direction gate fails.

| Model | \(n_{\mathrm{eff}}\) | \(\nu\) | Repeat-only intermediate (J) | Metrology-aware interval (J) | Decision interval (J) | Floor gate | Direction gate |
|---|---:|---:|---|---|---|---|---|
| Registered composition with \(n_{\mathrm{eff}}=n\) | 10.000000 | 9 | [3.998570, 6.001430] | [3.901124, 6.098876] | [-0.098876, 10.098876] | pass | fail |
| AR(1), \(\hat\rho=0.300000\) | 5.764703 | 4 | [3.381327, 6.618673] | [3.288758, 6.711242] | [-0.711242, 10.711242] | pass | fail |
| Fixed effective-n halving | 5.000000 | 4 | [3.261949, 6.738051] | [3.175427, 6.824573] | [-0.824573, 10.824573] | pass | fail |

The gates agree in this invented example. Reproduce it exactly with:

    python3 scripts/dependence_sensitivity.py --example

To exercise the disagreement sentence with the same ten deltas, change only deterministic_bound_total to \(3.500000\) J. The command extracts the one list in the table above:

    python3 scripts/dependence_sensitivity.py --block-deltas "$(grep '^| Ordered block deltas' docs/paper/round7/dependence-sensitivity.md | cut -d'|' -f3 | tr -d ' \t' | tr -d '\\140')" --floor 3.5 --se-metrology 0.2 --deterministic-bound-total 3.5

That output has the registered-composition direction screen passing while the AR(1) and halving screens fail, and renders `"direction_gate_outcomes_agree": false`.

For future data, pass the authenticated block-delta JSON list, meaning a structured text list whose recorded SHA-256 fingerprint is checked, together with the issued floor and two metrology values. The `--block-deltas` value must be the exact canonical JSON text whose digest is recorded.

The output artifact has schema joulewise.dependence_sensitivity.v1, where a schema is the expected named-field layout. It carries a SHA-256 digest, a fixed 64-character fingerprint, of canonical UTF-8 block-delta JSON and a second digest plus values for the metrology inputs. A reviewer rebuilds the JSON texts using the displayed canonical_json rule and compares both digests.

## Placements to register

A **fill registry** is the table that says which authenticated result supplies each paper location. A **placement** is one such paper location. A **source artifact** is the calculator's saved JSON result. A **STOP_FILL rule** instructs the paper writer to omit a placement when its stated evidence is absent or invalid. These are proposed new placements; no registry or paper-rendering file changes here. The sensitivity tables use `joulewise.dependence_sensitivity.v1`; each disagreement row also uses its registered DS-31 or PG-07 direction-gate supplier for the bracketed word.

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| DS-SENS-01 — decode sensitivity table; insertion before `docs/paper/draft-v1.md` line 285 | `Table 3. Prospective contrast decisions.` (the sentence it precedes) | `joulewise.dependence_sensitivity.v1`: `input_authentication.block_deltas_json_sha256`, `input_authentication.metrology_inputs`, `input_authentication.metrology_inputs_json_sha256`, `input.registered_alpha`, `input.registered_floor_j`, `summary.mean_j`, `ar1_rho_estimator.rho_hat`, `ar1_variance_terms`, and, for every `models.*`, `description`, `effective_n`, `degrees_of_freedom`, `variance_inflation_factor`, `se_repeat_j`, `repeat_only_interval_j`, `se_total_j`, `t_critical_95`, `half_width_j`, `metrology_aware_interval_j`, `deterministic_bound_total_j`, `decision_interval_j`, `raw_two_sided_p`, `floor_gate`, and `direction_gate` | gamma / decode sensitivity | DERIVE — render both the table values and labels from the authenticated fields and fixed formulas; reject an independently supplied value. | KEY_FROZEN / VALUE_UNISSUED; PROPOSAL ONLY UNTIL REGISTRY ADOPTS; STOP_FILL if the artifact is missing or schema-wrong, either digest cannot be rebuilt, or inputs differ from authorized decode inputs. | DRAFT, `scripts/dependence_sensitivity.py`, AUTH |
| DS-SENS-02 — decode disagreement sentence; insertion before `docs/paper/draft-v1.md` line 292 | `**Limitation 1 is an untested load-regime transfer.**` at draft line 294 (the sentence it precedes) | For the sensitivity outcome, artifact field only: `comparison.direction_gate_outcomes_agree`; `input_authentication.block_deltas_json_sha256` and `input_authentication.metrology_inputs_json_sha256` authenticate it; the bracketed word is supplied by the registered DS-31 direction-gate outcome. | gamma / decode sensitivity | DERIVE — derive whether the fixed sentence is inserted from the authenticated comparison flag, while taking the bracketed word only from DS-31; no sensitivity model outcome supplies that word. | KEY_FROZEN / VALUE_UNISSUED; PROPOSAL ONLY UNTIL REGISTRY ADOPTS; STOP_FILL on missing or unauthenticated inputs, or with reason `SENSITIVITY_MODEL_1_OUTCOME_DISAGREES_WITH_REGISTERED_DS31` if the artifact's model-1 outcome disagrees with DS-31. | DRAFT, `scripts/dependence_sensitivity.py`, DS-31, AUTH |
| PG-SENS-01 — prefill sensitivity table; insertion before `docs/paper/draft-v1.md` line 285 | `Table 3. Prospective contrast decisions.` (the sentence it precedes; place after DS-SENS-01) | The same authenticated `joulewise.dependence_sensitivity.v1` fields as DS-SENS-01, from the selected prefill artifact. | gamma / prefill sensitivity | DERIVE — render both the table values and labels from the authenticated fields and fixed formulas; reject an independently supplied value. | KEY_FROZEN / VALUE_UNISSUED; PROPOSAL ONLY UNTIL REGISTRY ADOPTS; STOP_FILL if the artifact is missing or schema-wrong, either digest cannot be rebuilt, or inputs differ from authorized prefill inputs. | DRAFT, `scripts/dependence_sensitivity.py`, AUTH |
| PG-SENS-02 — prefill disagreement sentence; insertion before `docs/paper/draft-v1.md` line 292 | `**Limitation 1 is an untested load-regime transfer.**` at draft line 294 (the sentence it precedes; place after DS-SENS-02) | For the sensitivity outcome, artifact field only: `comparison.direction_gate_outcomes_agree`; `input_authentication.block_deltas_json_sha256` and `input_authentication.metrology_inputs_json_sha256` authenticate it; the bracketed word is supplied by the registered PG-07 direction-gate outcome. | gamma / prefill sensitivity | DERIVE — derive whether the fixed sentence is inserted from the authenticated comparison flag, while taking the bracketed word only from PG-07; no sensitivity model outcome supplies that word. | KEY_FROZEN / VALUE_UNISSUED; PROPOSAL ONLY UNTIL REGISTRY ADOPTS; STOP_FILL on missing or unauthenticated inputs, or with reason `SENSITIVITY_MODEL_1_OUTCOME_DISAGREES_WITH_REGISTERED_PG07` if the artifact's model-1 outcome disagrees with PG-07. | DRAFT, `scripts/dependence_sensitivity.py`, PG-07, AUTH |

The existing DS-26, DS-31, PG-02, and PG-07 rows keep their suppliers and meanings. These proposed placements add sensitivity reporting only; they do not replace primary endpoints, direction results, or existing STOP_FILL rules.
