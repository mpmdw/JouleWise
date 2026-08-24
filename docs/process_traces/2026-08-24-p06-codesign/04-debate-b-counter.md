## 1. T1 — Attribution: ACCEPT

A is right: prose-only treatment leaves the paper’s central timing-attribution claim untested. The draft itself foregrounds the retained diagnostic timing range and attribution limit, so a fresh schema must criterion that property. [draft-v1.md:7](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:7) [draft-v1.md:267](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:267)

Exact schema change: retain six public rows, but make these conjunctive C4 internal subtests:

- `C4.3 attribution_term_decomposition`: report `b_fiducial_s` separately from per-bundle local/edge terms.
- `C4.4 bracket_bound_within_issued_band`: both bracket captures lie within the bound of the frozen acceptance edition.
- `C4.5 quarter_window_eligibility`: zero claim-bearing members carry `clock_bound_exceeds_quarter_window`.
- `C4.6 cadence_and_sample_fidelity`: zero claim-bearing members carry `cadence_ratio_below_threshold` or `insufficient_in_window_samples`.
- `C4.7 attribution_dominance_realized`: evaluate the existing dominance predicate, which compares anchor-envelope uncertainty with the guarded point-only floor. [reduce.py:970-998](/Users/edr/code/JouleWise/joulewise/reduce.py:970) [detection_floor.py:806-841](/Users/edr/code/JouleWise/joulewise/detection_floor.py:806)

C4’s one existing rendered outcome is the printed, criterioned attribution outcome; no public row or token amendment is needed. A C4.7 contradiction precommits that the fresh window’s floors do not receive the attribution-limited label; historical material may remain explicitly diagnostic only.

## 2. T3 — Vocabulary: ACCEPT

`READY/NOT_READY/UNVERIFIED` belongs to the pre-window readiness council, whose verdict procedure and decider are different. [instrument-readiness-audit-charter.md:79-91](/Users/edr/code/JouleWise/docs/process/instrument-readiness-audit-charter.md:79) A’s renderer-aligned vocabulary closes the real gap: the template has exactly four permissible phrases, including the C6-only fewer-than-three-sessions phrase. [DRAFT-RESULTS_PROSE.md:259-263](/Users/edr/code/JouleWise/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:259)

Exact schema change:

- `row_outcome ∈ {supported, indeterminate, contradicted, pending_eligibility}`; the last is C6-only.
- Total render map: `supported`, `indeterminate`, `contradicted`, and `pending_eligibility` map respectively to the template’s four phrases.
- Preserve B’s adopted `publication_class` and closed `failure_class` as separate layers: supported→`RESULT`; contradicted→`PUBLISHABLE_REFUSAL`; indeterminate/pending→`DIAGNOSTIC_ONLY`.
- `protocol_incomplete` is not an issued row outcome after freeze; the writer refuses issuance instead.
- Add closed `characterization_*` `reason_code`s, disjoint from readiness codes, following the house’s domain-specific closed-vocabulary pattern. [receipt_histsem_verifier.md:103-129](/Users/edr/code/JouleWise/docs/contracts/receipt_histsem_verifier.md:103)

## 3. T4 — C2 split: ACCEPT

The unconditional ten-block split is good insurance but not the primary design when a matching issued floor exists. The null ladder already plans five same-condition ABBA blocks per magnitude. [null_ladder/README.md:10-11](/Users/edr/code/JouleWise/configs/campaigns/metrology_v1/null_ladder/README.md:10)

Exact schema change: freeze `c2_floor_mode` prospectively:

- `issued_floor_comparator` iff a same-cell, earlier-issued `F_operative` exists and its evidence-bundle hash set is disjoint from the null-ladder hash set.
- Otherwise `heldout_train_test`, requiring ten blocks per magnitude: five `floor_train`, five `null_test`; only train blocks derive `F_train`.

This is not merely cheaper. The verified guard rule gives \(g(5)=\sqrt{9/4}=1.5\), while \(g(10)=1\); an unconditional split would impose that weaker n=5 comparator even where an issued n=10 floor is available. [detection_floor.py:104-109](/Users/edr/code/JouleWise/joulewise/detection_floor.py:104) [detection_floor.py:664-672](/Users/edr/code/JouleWise/joulewise/detection_floor.py:664) The branch preserves non-circularity because comparative floors are constructed from ABBA deltas. [draft-v1.md:180-195](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:180)

## 4. T2 — Hybrid limit: ACCEPT

H alone is a resolution statement, not an instrument-quality gate: a degraded interval can enlarge its own allowed residual. Keep it, but require an independently issued, claim-anchored limb as well.

Exact schema change:

- C1 has `resolution_limb: R_max ≤ H` and `claim_limb: R_max ≤ F_operative`, both computed from the same fixed fit.
- Apply the analogous dual limb to C4 prompt invariance: \(L_H=\max(h_{\rm prefill})/\Delta T\) and \(L_F=F_{\rm operative}/\Delta T\).
- A missing operative-floor limb yields `row_outcome=indeterminate`, `publication_class=DIAGNOSTIC_ONLY`, and `reason_code=characterization_operative_floor_unavailable`; it is never silently omitted.
- C1 carries `claim_ceiling=resolution-qualified tested-range behavior` and forbids universal physical-linearity wording.

This uses the cell-specific operative floor, not a universal historical joule constant. [draft-v1.md:257-275](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:257) The registry already requires a preregistered residual criterion rather than an outcome-selected one. [results-fill-registry.md:253-261](/Users/edr/code/JouleWise/docs/paper/results-fill-registry.md:253)

## 5. New defects: ACCEPT-WITH-MODIFICATION

- C3 gains `predicted_delta_j`, `realized_delta_j`, and a frozen `sizing_tolerance_ratio`. A breach yields `indeterminate` with `characterization_effect_sizing_missed`, never `contradicted`. I do not invent the ratio: it is `ed_input_required` and blocks C3 freeze until ratified. The present micro-delta plan is expressly draft-pending-slope. [micro_delta/calibration_plan.json:5-8](/Users/edr/code/JouleWise/configs/campaigns/metrology_v1/micro_delta/calibration_plan.json:5)

- C4 closure becomes two criteria: `max(D_i) ≤ τ_float` for overcount, and `|D_i| ≤ gap_duration_i × max_gap_power_i` for legitimate unphased-gap accounting. The template explicitly presupposes a registered gap treatment. [DRAFT-RESULTS_PROSE.md:2456-2460](/Users/edr/code/JouleWise/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:2456) I do not freeze A’s proposed `1e-9 J` without a source: the current evidence establishes a 0.0-J reintegration discrepancy, not that literal tolerance. [draft-v1.md:423-425](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:423) Thus `τ_float` must be a pinned code-defined value or `ed_input_required`.

- Register the characterization family as exploratory with explicit no-confirmatory-inference wording, and apply Holm with `m=2` to the null-containment and prompt-invariance inferential subfamily. Add the anti-selection rule: a successor window names its predecessor and both reports publish; a contradicted row in a passed window cannot trigger recollection to reverse it. The analysis-plan contract requires a named multiplicity rule and frozen family membership. [analysis_plans.md:20-35](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:20) [analysis_plans.md:46-67](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:46)

## 6. R2 / 1.25×: ACCEPT

The symmetric \(\max(F)/\min(F)\le1.25\) corridor is a useful new C6 criterion, but it is not already ruled. The existing rule is directional: a Window-B revalidation floor must be no more than \(1.25\times\) the Window-A floor, with stated change checks; it expressly is not a statistical overlap test. [detection_floor.md:389-408](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:389)

Exact schema change: retain the symmetric three-session corridor, but label it `limit_basis=derived`, with `derivation=symmetric_generalization_of_directional_stale_floor_sentinel` and the existing narrow claim ceiling. It must never be described as a ruled statistical-stability test.

## SEAT B FINAL POSITION

1. T1 — ACCEPT: fold five attribution-realization subtests into conjunctive C4.
2. T3 — ACCEPT: use four-layer, renderer-complete outcome architecture.
3. T4 — ACCEPT: issued-floor primary; ten-block split only as a frozen conditional branch.
4. T2 — ACCEPT: require both resolution and claim-anchored limits; name unavailable limbs.
5. Defects — ACCEPT-WITH-MODIFICATION: add sizing and signed-gap repairs; block unruled numeric literals; add multiplicity and anti-selection.
6. R2 — ACCEPT: retain symmetric corridor only as derived-not-ruled.