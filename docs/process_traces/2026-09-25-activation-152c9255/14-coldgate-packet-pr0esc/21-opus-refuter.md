# Opus 5.5 contract/execution refuter: the PR-0 escalation proposal (packet 14)

The packet is verified: `00-charge.md` sha256 `fd67f554…985ec` matches. Probes ran in `/tmp/152c9255/pr0esc-ref` at `7929a7ec` (`test/2026-09-25-claimgate-pr0-golden`); `capture()` reproduces the golden byte-for-byte. coverage.py is not installed in any interpreter on this machine, so I installed 7.16.1 into `/tmp/152c9255/covlib` and ran `capture()` under branch mode. Nothing in the worktree or the canonical root was touched, and I ran no discovery suite.

**Verdict: 2 BLOCKERs and 7 MATERIALs.** The proposal's structural cure S is the right *shape*, but as written it cannot be met:
- One part of it contradicts D-1.
- Its mutation operators do not generate 3 of the 7 mutants that survived the delta audit.
- Four verified equivalent mutants (changes that alter no output) make "zero survivors" impossible.

## Q1: current branch coverage from the golden's inputs (`capture()`, coverage.py branch mode)

| Function | Uncovered arcs | Can golden inputs reach them without `joulewise/` changes? |
|---|---|---|
| `claims.py::_inside_equivalence`, `multiplicity.py::holm_adjust`, `epoch_equivalence_check.py::evaluate_session` | none | already 100 % |
| `claims.py::_interval` | 249→250 | yes (an interval with lower > upper) |
| `claims.py::evaluate_claim` | 349→350, 356→357, 369→373, 373→374, 373→377; the `except` lines 294–295 never run | yes: margin 0 or a wrong method; `base_reason_codes=("multiplicity_not_rejected",)`; the two interval-straddle rows |
| `__init__.py::_resolve_contrast_floor` | 390→395, 402→403/406, 407→456, 417→418, 432→436, 457→461/474 | probably. 390→395 needs `request_factory=None` with a real floor binding; not verified |
| `artifact.py::validate_claim_verdicts` | **432 arcs / 410 lines** | mostly by crafted invalid artifacts. It is one 2,502-line function (`artifact.py:981-3482`) with no nested defs |
| `paper_custody.py::_claim_issuance_gate` | 620→621, 626→627, 632→633, 649→629 now; **after D-1: 620→621, 626→627, 629→651, 632→633, 632→634, 649→629, 649→650** | **no** for the post-D-1 set (B-1) |

Two further facts:
- `holm_adjust` is at 100 % branch coverage, yet the delta audit's mutant N2 survived there. Branch coverage alone does not imply a kill.
- `evaluate_session` is at 100 % only because `_slot_outcomes` is mocked (`capture_claim_replay_golden.py:222`).

## BLOCKER

**B-1. S(ii)/(iii) and D-1 cannot both be met for `_claim_issuance_gate`.**
- `validate_claim_verdicts` enforces exact top-level keys (`artifact.py:49-58`, `:989-995`), so no artifact that passes it carries a top-level `evidence_class`.
- The gate therefore stops at `paper_custody.py:632`, the line that reads `artifact["evidence_class"]`.
- I applied D-1 (no key injected, no verdict-validator mock). The real validator on `am-5e97…` returns `[]`, and the direct gate call raises `KeyError 'evidence_class'`. Lines 633–636 and 648–652 never execute.
- So 100 % coverage is unreachable, and every mutant in 633–652 survives. Example: deleting the L2-grant guard at `:649`.
- The only way to reach that code is the mock that D-1 removes.
- **Corrected S(ii) text:** "…fails listing any uncovered arc **not in `unreachable_arcs`**. The golden carries `unreachable_arcs`: `{"paper_custody.py::_claim_issuance_gate": [[629,651],[632,633],[632,634],[649,629],[649,650]], "reason": "D-1: validate_claim_verdicts forbids top-level evidence_class; gate raises at :632"}`. The test asserts the uncovered set **equals** this list exactly, not merely that it is contained in it. Lane V1-ISSUANCE-GATE-EVIDENCE-CLASS-01 empties the list by reviewed PR." S(iii) gets the same exemption for mutants on those lines.

**B-2. The sweep's operators do not generate N4, N6 or N9, so "SF-A to SF-C subsumed by S" is false.**
- The operator list in S(iii) is: comparisons flipped strict/non-strict, `max`/`min` collapsed, guards deleted.
- N4 (drop `or not adjusted_rejected`, `claims.py:363-367`), N6 (drop the decision-interval disjunct, `:371`) and N9 (drop the `window_class !=` disjunct, `__init__.py:409`) each delete one operand of an `and`/`or`.
- Line-level branch coverage does not demand them either. One `metric` mismatch row satisfies both arcs of the multi-line `if` at `:407`.
- **Corrected S(iii) operator text:**
  - every `<`, `<=`, `>`, `>=` flipped strict/non-strict;
  - every `==`/`!=`, `in`/`not in`, `is`/`is not` negated;
  - every operand of every `and`/`or` deleted (replaced by `True` in an `and`, `False` in an `or`);
  - every `if`/`elif` condition replaced by `True` and by `False`;
  - every `max`/`min` with two or more arguments collapsed to each argument;
  - every `return`/outcome string literal in a named function replaced by a sibling outcome.

## MATERIAL

**M-1. Equivalent mutants make "zero survivors" unreachable.** Each candidate was checked against the unmutated `evaluate_claim` over 60,000 random inputs that included the edge values 0, −0 and NaN. A control mutant differed on 10,842 of them.

| ID | Mutant | Differing cases | Why nothing changes |
|---|---|---|---|
| E1 | `numeric_estimate > 0.0` → `>= 0.0` (direction line) | 0 | An estimate of 0 with a finite floor ≥ 0 always adds `effect_not_above_floor`, which is in `_NOT_RESOLVABLE`, so the outcome is never `direction_supported` |
| E2 | delete `and numeric_estimate is not None` (same line) | 0 | redundant after the not-estimable screen |
| E3 | delete the three `assert`s (`claims.py:~333-335`) | 0 | they can never fire |
| E4 | delete `floor is None or` (`if floor is None or reasons & _NOT_RESOLVABLE`) | 0 | a missing floor adds `floor_abs_missing`, which is already in `_NOT_RESOLVABLE` |

- More exist in `validate_claim_verdicts` and `_resolve_contrast_floor`; I did not enumerate them within budget.
- **Ruled exception, corrected text:** "0 survivors outside `equivalent_mutants`. A pinned list in the sweep script gives, per entry: file:line, the operator, and a one-line proof. A justification that the proof is 'unreachable input' must cite the refusing line. The sweep asserts survivors == list exactly. Adding an entry requires reviewed-PR review of its proof."

**M-2. "The decision branches of `validate_claim_verdicts`" is not a mechanical target.**
- The function is a single 2,502-line body with 432 uncovered arcs. Pinning it arc by arc is the hand-enumeration anti-pattern at roughly 50 times the scale.
- The validator's claim recompute is not even in it. It lives in `_validate_cross_field_claim_semantics` (`artifact.py:639-882`, recompute at `:758`).
- **Fix:**
  - Name exact line ranges: `artifact.py:2085-2100` (t-critical, N10) and `:2285-2305` (the WIP v2 site), plus all of `_validate_cross_field_claim_semantics`.
  - Add a **diff-coverage gate** to the CG-4 PR: every pre-image line that PR's `joulewise/` diff modifies (`git diff -U0 <PR-0 merge>..HEAD`) must have been executed by `capture()` at the base. This makes the named list self-completing.

**M-3. The named list is incomplete for WR-0 to WR-10.** These are edited or pinned by the rulings but not named:
- `analyze_claims` (`__init__.py:1653`): the WR-6 closure check and WR-5's `envelope_member_only`.
- `_evaluation` (`:1243-1302`): WR-0(ii), the call at `:1278`.
- `_prepare_contrast_v3` (`:514-785`): v1 admission at `:724-747`; the WIP `(5 if v2 else 2)`.
- `estimators.py::estimate_paired_blocks` and `_ci_t_critical` (`:224-228`, the N3 site): WR-0 lets the helper and its `confidence` parameter stand.
- `multiplicity.py::adjust_p_values` (10 uncovered arcs; `adjusted_p <= threshold` is the alpha boundary).
- `claim_side_bound.py::_project` (`:89-155`), `claim_side_bound_diagnostics` (`:207-222`) and `validate_claim_side_bound`: WR-5 versions them, and the golden **mocks** them (`capture:331`).
- The v3 manifest validators (WR-4): also mocked in the issuance scenario (`:332`).
- `_resolve_contrast_floor` as a whole rather than `:400-415` (WR-5 adds the `floor_class` refusal), plus `_floor_request_or_refusal`.
- For the epoch check, the functions CG-3 edits, and `_slot_outcomes` unmocked or explicitly exempted.

The diff-coverage gate from M-2 closes this class for good.

**M-4. The coverage tool needs pinning.**
- The core package is stdlib-only (`pyproject.toml:10-15`, D-009), and coverage.py is not installed anywhere here. S(ii) would therefore always run the `sys.settrace` fallback.
- `sys.settrace` sees only executed arcs; the set of *possible* arcs needs coverage.py's static analysis. A hand-rolled fallback is a second, unreviewed arc model, not a mechanical check.
- **Corrected text:** "Pin coverage.py 7.16.1 as a test-only extra. If it is absent, the coverage test **fails** (it does not skip), and there is no settrace fallback."

**M-5 (D-1). The KeyError is conditional, and it is a crash only at a private seam.**
- It fires only after four things succeed: the finalized-manifest validator, the verdict validator, the side-bound validator and the floor anchor (`:611-624`); `_validate_floor_acceptance` (`:625`); and a non-empty subject list whose ids all resolve (`:627`).
- At the production seam, `_replay_family` (`paper_custody.py:1339-1348`) catches it. I ran it with gate id `claim-evidence.v1`: it returns `authentic=False, admitted=False, grants=(), validator_codes=("KeyError",)`.
- `open_paper_input` would turn anything else into `paper_custody_request_invalid`.
- So production refuses without admitting. The refusal code is an exception class name rather than a reason code, but it does not crash.
- Side note: the test context the golden builds carries `issuance_gate_id="d165-closeout.v1"`, so the direct call bypasses dispatch.
- **Corrected D-1 text:** "Record both outcomes:
  - direct: `{"raised":"KeyError","key":"evidence_class"}`;
  - production seam (`_replay_family`, gate id `claim-evidence.v1`): `{"authentic":false,"admitted":false,"grants":[],"validator_codes":["KeyError"]}`.

  The lane's defect statement: the gate refuses with an untyped exception-class code instead of a reason code, and no v1 admit is reachable. This fails closed with an untyped refusal code; it does not fail closed by crash."

**M-6 (D-2). The transition rule differs from WR-6 and is undefined for part of its scope.**
- **(a) The id is misnamed.** WR-6 says the finalized manifest's `collection_manifest_id` ∈ `V1_FRONT_PLANNED_MANIFEST_IDS`, meaning the front registries' `planned_manifest_id` values. The registries carry no `collection_manifest_id`; that field is on the finalized v3 manifest (`analysis_manifest_v3.py:1155`, `:3967`). The proposal's "a front-registry `collection_manifest_id`" is wrong.
- **(b) "Nothing else changes" breaks an invariant.** `claim_level_ceiling = "L2" if claim_ready else "L1"` (`claims.py:409`). Setting ready to false while keeping ceiling L2 produces a state `evaluate_claim` never emits. WR-6 is silent on this, so the rule must say what happens.
- **(c) Issuance outcomes have no `claim_ready_for_l2_l3` field.** After D-1 the pre-outcome is a KeyError, and the post-outcome depends on where the WR-6 check sits relative to `:632`.
- **(d) `minimal_v1_artifact` is hand-built** (`tests/test_analysis_claims.py:297`), not produced by `analyze_claims`, so WR-6 cannot change it.
- **Corrected rule:** "For `window_engine.v3_window_clean` and `v3_window_supersession_diverged`, and only for them: each contrast without the v2 group whose finalized `manifest_id` ∉ `v1_golden_manifest_ids`, and whose manifest `collection_manifest_id` (absent counts as non-member) ∉ `V1_FRONT_PLANNED_MANIFEST_IDS`, changes as follows:
  - `reason_codes` becomes `ordered_reason_codes(pre ∪ {"claim_rule_version_v1_closed"})`;
  - `claim_ready_for_l2_l3` becomes `false`;
  - `claim_level_ceiling` becomes `"L1"`;
  - `outcome` and `direction` stay unchanged.

  The WR-6 check in `_claim_issuance_gate` runs **before** `:629`, as a validator code. The post-outcome of the issuance scenario is then `{"authentic":false,"admitted":false,"grants":[],"validator_codes":["claim_rule_version_v1_closed"]}`. All other scenarios are invariant."

**M-7 (D-2, Q4b). `post = transform(pre)` masks some v1 changes in closed contrasts.**
- Because the transform overwrites ready and the ceiling, a CG-4 change in `analyze_claims` that alters only those fields is invisible. Example: `confirmatory_status` or `evidence_class` wiring, since demotion adds no reason code (`claims.py:395`).
- The `window_engine` section records only `claim_evaluation` (`capture:283-287`). Estimates, confidence intervals and floors are unpinned.
- The window builder also mocks `_resolve_contrast_floor` and five other functions (`tests/test_analysis_integration.py:596-626`), so the floor-selector accept arc 407→456 never runs.
- **Fix:**
  - The golden records, per contrast, `estimator`, `deterministic_bounds`, `floor` and `multiplicity`.
  - The CG-4 test also re-runs `evaluate_claim` on the post artifact's contrast inputs with the closure code removed, and asserts the result equals `pre` byte-for-byte, readiness and ceiling included.

## NIT

- **N-1.** The proposal's "window floor selector at ≈:400-415": the real decision is the multi-line `if` at `:407-417` inside `_resolve_contrast_floor` (`:372-481`). Name the function, not an approximate line range.

## Direct answers

1. **Q1:** 100 % coverage from golden inputs is achievable for `evaluate_claim`, `_interval`, `_inside_equivalence`, `holm_adjust` and `evaluate_session`, and probably for `_resolve_contrast_floor`. It is **not** achievable for `_claim_issuance_gate` once D-1 is applied (B-1). For `validate_claim_verdicts` the target is undefined (M-2).
2. **Q2:** Yes, equivalent mutants exist: E1–E4, each verified with 0 differing cases out of 60,000. The ruled exception is in M-1.
3. **Q3:** The list is incomplete (M-3). The durable fix is the diff-coverage gate (M-2).
4. **Q4:** No, the declared rule is not exactly WR-6's (M-6). The CG-4 test catches v1 changes to outcome, direction and reason codes, but misses changes that alter only readiness or the ceiling, and any numeric change (M-7).
5. **Q5:** The KeyError is unconditional for every artifact that passes the validator *and* reaches the loop. At the production seam it becomes a typed-by-class-name refusal, not a crash (M-5).
