```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S1 cures the boundary failure and CG-1 passes the requested simulations; four material implementation ambiguities and one numerical nit remain.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "4b7f5a0498b8ab324f6674e1274192ee691f7dfd",
    "head_end": "4b7f5a0498b8ab324f6674e1274192ee691f7dfd",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"R1","severity":"should_fix","summary":"CG-4 omits upstream effective-margin testing and sign-flip admission wiring."},
      {"id":"R2","severity":"should_fix","summary":"Shared stochastic terms need explicit homogeneity and cross-envelope dependence rules."},
      {"id":"R3","severity":"should_fix","summary":"Retained-envelope eligibility is not reconciled with existing fixed-n refusal."},
      {"id":"R4","severity":"should_fix","summary":"The dimensionless alternative contradicts the permitted floor-unit enum."},
      {"id":"R5","severity":"nit","summary":"CG-3's printed r7 constants differ slightly from the actual corpus calculation."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"build",
      "cmd":"clang -O3 -shared -fPIC -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX15.4.sdk /tmp/278ebc9e/cgv2ref/perm.c -o /tmp/278ebc9e/cgv2ref/perm.dylib && PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgv2ref/run.py validate",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["permutation_validation 1 0.8781 0.878","permutation_validation 4 0.0646 0.0654","permutation_validation 16 0.0002 0.0008"]},
      "expected":{"exit_code":0,"tail_regex":"permutation_validation 16"}
    },
    {
      "id":"V2",
      "kind":"other",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgv2ref/run.py claims 5000 > /tmp/278ebc9e/cgv2ref/claims.jsonl",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":".*"}
    },
    {
      "id":"V3",
      "kind":"other",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgv2ref/run.py nights 10000 > /tmp/278ebc9e/cgv2ref/nights.jsonl",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":".*"}
    },
    {
      "id":"V4",
      "kind":"other",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgv2ref/literal.py nights 10000 > /tmp/278ebc9e/cgv2ref/literal.jsonl",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":".*"}
    },
    {
      "id":"V5",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgv2ref/code_probes.py > /tmp/278ebc9e/cgv2ref/code_probes.out",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":".*"}
    },
    {
      "id":"V6",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgv2ref/summarize.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["CG1 cells=24 N=5000 max_false_admission=0.0002","CG3 fixed_r7 cells=48 null_boundary_N=10000 permutations=2000","CG3 no_change_false_FAIL_range=0.0309..0.0459","CG3 margin_false_PASS_range=0.0005..0.0016","CG3 simulated_old cells=48 N=2000 sensitivity_only","SIMULATION_CHECKS_PASS"]},
      "expected":{"exit_code":0,"tail_regex":"SIMULATION_CHECKS_PASS"}
    },
    {
      "id":"V7",
      "kind":"inspection",
      "cmd":"git status --short --branch && git rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","4b7f5a0498b8ab324f6674e1274192ee691f7dfd"]},
      "expected":{"exit_code":0,"tail_regex":"4b7f5a0498b8ab324f6674e1274192ee691f7dfd"}
    }
  ],
  "flags": []
}
```

## Findings

No surviving numerical BLOCKER in the requested simulations. The following proposed replacements require lead adjudication before implementation.

| ID | Severity | Finding and exact replacement text |
|---|---|---|
| R1 | **MATERIAL** | **The implementation list misses two decision paths.** [`_claim_raw_p`](/Users/edr/code/wt-278ebc9e-cg-astra/joulewise/analysis_engine/__init__.py:1305) computes TOST using registered Δ before the evaluator runs. With Δ=2, F=0.8, B=0.1, SE=0.5 and df=7, the interval fits inside Δ_eff, but Holm is **0.012975 using Δ versus 0.118665 using Δ_eff**: an erroneous equivalence admission. Separately, [`randomization_check`](/Users/edr/code/wt-278ebc9e-cg-astra/joulewise/analysis_engine/sensitivity.py:115) and claim/artifact sensitivity handling suppress five-envelope admission. Replace the relevant CG-4(c) wording with: **“Resolve Δ_eff through one shared v2 helper before `_family_adjustments`; use that identical value for raw TOST, Holm adjustment, evaluator containment, and artifact replay. Version `_claim_raw_p`, `_randomization_for_prepared`, `_analysis_reasons`, `_evaluation`, and sensitivity validation together. Sign-flip is diagnostic only at every k, records its minimum attainable p, and supplies no admission refusal or sensitivity demotion.”** The final sentence also settles the current ambiguity at k≥8. |
| R2 | **MATERIAL** | **“Carry once, undivided” does not identify a value when shared terms have different block-level variances.** Two perfectly correlated contributions Z and 3Z have block variances 1 and 9, but their mean has variance **4**. Neither block value can simply be carried. Also, the existing estimator divides propagated envelope variances by k² and cannot represent covariance between envelopes. Replace the shared-term clause with: **“The undivided shared-term shortcut applies only to one identical random contribution in every block of an envelope, with identical variance/covariance fields and independently drawn contributions across envelopes. Reject unequal fields, cross-envelope sharing, or unspecified dependence as `not_estimable: envelope_term_scope_unknown`; a more general covariance model requires a separately registered estimator.”** |
| R3 | **MATERIAL** | **Excluding incomplete envelopes leaves confirmatory eligibility unresolved.** CG-1 counts retained k, while [`__init__.py:725`](/Users/edr/code/wt-278ebc9e-cg-astra/joulewise/analysis_engine/__init__.py:725) and its second preparation path enforce `fixed_n_plan_incomplete`; `_claim_raw_p` then returns `None`. An implementer must decide whether to preserve or waive this gate. Recommended replacement: **“Register the planned envelope count K and exactly n_reg blocks per envelope. Incomplete envelopes are excluded and disclosed. Fewer than five complete envelopes gives `not_estimable`; five or more supports descriptive estimation, but an unfilled planned envelope gives `not_resolvable: fixed_n_plan_incomplete` and a missing confirmatory p-value. Only prospectively registered technical replacements can complete K; excess blocks or envelopes cannot be selected after outcomes.”** |
| R4 | **MATERIAL** | **CG-4(f)’s dimensionless alternative conflicts with CG-1’s units and CG-4(c)’s `floor_unit ∈ {J, J/correct}`.** Recommended replacement for CG-4(f)’s opening: **“AP-5M v5 registers an additive J/correct contrast as the primary estimand. Dimensionless contrasts are outside this v2 rule and require a separately ruled estimator, matched floor derivation, and unit schema.”** |
| R5 | **NIT** | **The illustrative r7 constants are slightly inaccurate.** Replace the numerical parenthetical in CG-3 with: **“For the checked-in r7 corpus: w̄=27.051261 ms, s_w=2.709555 ms, s_old=2.460856 ms, prediction half-width=5.209350 ms, and Δ_loc=8.612997 ms; therefore PASS requires \|ȳ−27.051261 ms\|<3.403647 ms. Compute from authenticated operands without rounding.”** Both literal and recomputed versions passed the simulations. |

**D1 — disposition of 88b F1–F7**

| Prior finding | Cured? |
|---|---|
| F1 | **Yes:** full S1 verdict has boundary false PASS ≤0.16% across the tested fixed-r7 cells. |
| F2 | **Yes at the evaluator-rule level:** strict Δ and Δ_eff resolve the original conflict; upstream wiring remains R1. |
| F3 | **Yes:** a new confirmatory shape requires prospective registration and subsequently collected observations. |
| F4 | **Yes:** the median gate and S1 reject the original all-above-screen exhibit. |
| F5 | **Arithmetic cured; specification incomplete:** variance scaling is correct, but shared-term semantics require R2. |
| F6 | **Yes:** the stated estimand now matches equally weighted envelope means. |
| F7 | **Partially:** named schema paths were added; decision wiring and unit consistency remain R1/R4. |

**Simulation tables**

All rates below are percentages. Scripts and complete results are in [authorized scratch](/tmp/278ebc9e/cgv2ref/run.py).

CG-1 used the four trace-19 generator forms through the ex-88 envelope adaptation: six blocks per envelope, independent envelope shocks, k_cal=k, registered positive direction, production estimator/Student-t/Holm helpers, and a frozen family of five with four missing members. Each cell has **5,000 trials**. Three deterministic-bound settings were tested: B/σ=0.5, 1, 2.

| Generator | k | Maximum δ=0 admission across B settings | 2σ power, B/σ=0.5 / 1 / 2 | 5σ power range |
|---|---:|---:|---:|---:|
| Gaussian | 5 | 0.00 | 75.78 / 64.08 / 2.34 | 100.00 |
| Gaussian | 8 | 0.02 | 99.92 / 96.10 / 2.46 | 100.00 |
| Heavy t3 | 5 | 0.00 | 77.30 / 66.24 / 2.16 | 99.76–99.96 |
| Heavy t3 | 8 | 0.00 | 99.34 / 96.00 / 2.14 | 99.96–100.00 |
| Linear drift | 5 | 0.00 | 77.68 / 63.90 / 2.42 | 100.00 |
| Linear drift | 8 | 0.00 | 100.00 / 96.02 / 2.14 | 100.00 |
| Shared plus local | 5 | 0.02 | 53.30 / 36.16 / 2.02 | 99.76–100.00 |
| Shared plus local | 8 | 0.00 | 99.34 / 81.54 / 2.78 | 100.00 |

The largest observed null-admission rate, 1/5,000, has a 95% Wilson upper bound of **0.1132%**.

CG-3 used the fixed 17-member, ten-window r7 corpus and the ex-88 night generators. Every verdict included **location, median level, and spread**, with **2,000 permutations**. Null and boundary cells have **10,000 trials**; detection cells have **2,000**.

The first two rate columns use CG-3’s **literal printed constants**; detection columns use the formula recomputed from r7.

| Generator | m | No-change false FAIL | Margin false PASS | +3σ detection | +5σ | ×4 variance | ×16 variance |
|---|---:|---:|---:|---:|---:|---:|---:|
| Gaussian | 8 | 4.22 | 0.14 | 98.45 | 100.00 | 51.70 | 97.00 |
| Heavy t3 | 8 | 4.38 | 0.12 | 98.45 | 100.00 | 37.70 | 88.85 |
| Linear drift | 8 | 4.60 | 0.16 | 98.75 | 100.00 | 64.50 | 98.85 |
| Shared plus local | 8 | 3.54 | 0.07 | 99.30 | 100.00 | 31.15 | 90.15 |
| Gaussian | 12 | 3.80 | 0.08 | 99.20 | 100.00 | 57.80 | 99.30 |
| Heavy t3 | 12 | 3.71 | 0.08 | 98.80 | 100.00 | 37.65 | 92.60 |
| Linear drift | 12 | 3.97 | 0.05 | 99.00 | 100.00 | 70.95 | 99.85 |
| Shared plus local | 12 | 3.10 | 0.06 | 98.90 | 100.00 | 28.80 | 94.00 |

With recomputed constants, no-change false FAIL is **3.09–4.59%** and boundary false PASS remains **0.05–0.16%**. The largest boundary rate has a 95% Wilson upper bound of **0.2598%**.

The simulated-old-corpus sensitivity used **2,000 trials per cell**, recomputing S1 and its margin for each old corpus:

| Generator | No-change false FAIL, m=8 / 12 | Boundary false PASS, m=8 / 12 |
|---|---:|---:|
| Gaussian | 4.85 / 4.65 | 2.10 / 1.75 |
| Heavy t3 | 7.00 / 5.40 | 1.85 / 1.60 |
| Linear drift | 1.80 / 2.25 | 1.40 / 1.50 |
| Shared plus local | 7.20 / 6.05 | 2.55 / 3.00 |

These sensitivity failures do **not** violate the expressly fixed-r7 precondition; they limit transfer to other calibration corpora.

**Probe tails**

```text
SIGNFLIP k=5 p_min=0.0625 status=not_run ready=False reasons=randomization_check_insufficient_blocks
TOST Delta=2 F=0.8 B=0.1 SE=0.5 decision_halfwidth=1.047289 wrong_Holm=0.012975 correct_Holm=0.118665 outcomes=equivalent/unresolved
MISSING_ENVELOPE complete_k=8 raw_p_with_fixed_n_plan_incomplete=None
SHARED_TERM block_variances=1,9 true_envelope_variance=4 carry_first=1 carry_last=9
CODE_PROBES_PASS
CG1 cells=24 N=5000 max_false_admission=0.0002
CG3 fixed_r7 cells=48 null_boundary_N=10000 permutations=2000
CG3 no_change_false_FAIL_range=0.0309..0.0459
CG3 margin_false_PASS_range=0.0005..0.0016
CG3 simulated_old cells=48 N=2000 sensitivity_only
SIMULATION_CHECKS_PASS
```

Next exact step: adjudicate R1–R4 and incorporate the chosen wording before implementing v2. Repository HEAD and cleanliness are unchanged.

## Residual risk

These are CPU-only simulations of the proposed rules, not end-to-end v2 implementation or live hardware validation. Monte Carlo rates are conditional on the specified generators; the highest no-change rate’s 95% interval slightly crosses 5%. CG-1 simulations assume independent envelope shocks.

No repository code changed, so the canonical suite was not run. Only the authorized scratch directory was written.