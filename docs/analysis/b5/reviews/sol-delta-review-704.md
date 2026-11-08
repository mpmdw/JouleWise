# Sol delta review of PR #704

Date: 2026-11-07 PST. Branch: `b5rel/2026-11-08-sol-delta-704`.
Reviewed range: `337e74b59..bea480f296e5c7bc77ad1684936f2b257801f597`
(`e9b24ce74` and `bea480f29` only). Repository code outside the delta was
read only to establish the producers' rules and test the changes.

## Verdict: ADMIT_WITH_FIXES

The original three refusal witnesses now pass legitimately, and the mapped
numeric/diagnostic-word copies work in both supported shapes. This head is
**not admitted** until the remaining copy gap and conditional-presence mismatch
below are dispositioned and fixed. The lead must also resolve the exact-threshold
policy question: the new implementation accepts an incorrect label at equality,
as its new DLE-5 prose allows, without the existing RC-CMP-11 qualification.

No production code was changed by this review. New tests preserve the remaining
counterexamples as explicit expected failures; those markers are not evidence
that the desired refusals succeed.

## Findings

### P2 — R704-D1: R704-2 still permits divergent exempt metadata copies

Locations: `scripts/compare_b5_recompute.py:4097`, `:3759`, `:3762`.

The new `COPIED_LISTS` entry requires rows only for the five diagnostic fields
and the claim evaluation's class, source and published-floor fields. There are
no comparison rows for the discipline object's leaves or the floor/resolution
class/source words. Their coverage exemptions consequently still allow the
fill to omit, alter or add those values independently of the verdict.

Four separate synthetic CLI probes each returned **exit 0, no failed family,
zero unmapped leaves**:

- Delete the fill's whole `claim_evaluation.floor_limit.single_count_discipline`.
- Change only the fill's `floor.floor_limit_class` to `wrong_class`.
- Delete only the fill's first resolution's `floor_source`.
- Change only the fill's claim discipline's `gating` flag from false to true.

The reverse direction also passes: delete `floor.floor_limit_class` from the
verdict while retaining it in the fill. Three committed witnesses cover omission,
changed value and the reverse direction (`DeltaCopyTests`, expected failures).

The existing exemption from **independent derivation** need not change. It does
not establish equality between two copies. Require type-preserving equality of
the complete copied metadata, including these exempt words/flags, in both
directions. This finishes the original review's requested descendant-copy
guarantee without inventing new scientific semantics.

### P2 — R704-D2: a refused combination can require nonexistent combined metadata

Locations: `scripts/compare_b5_recompute.py:2229`, `:2230`, `:2235`, `:2240`;
producer: `joulewise/analysis_engine/__init__.py:314`.

The engine publishes aggregate attribution metadata only when **all resolutions
are usable** and at least one is limited. A usable limited arm retains its own
resolution diagnostic when its partner refuses, but the combined floor is
`refused`, its active floor is null, and it has no aggregate point diagnostics
or claim `floor_limit`. `claims.evaluate_claim` cannot copy absent combined
metadata into a claim.

The delta instead derives aggregate presence from any limited registered source
cell, without the all-usable condition. A synthetic witness calls the actual
`_combined_floor` with A resolved/limited and B refused/below minimum, and uses
the actual independent `floor_estimate` outputs. On that correct producer output,
`compare_floor_limit` produces **15 failed rows**: 4 routing, 6 floor-number and
5 outcome-word rows. The same function at `337e74b59` produces no failed rows.
Witness: `DeltaRuleTests.test_unresolved_combination_must_not_require_combined_metadata`.

This is a function-level delta witness, **not** a demonstration that a complete
release otherwise passes with a refused contrast. Other existing null-floor
checks can already hold such a run. Nevertheless, these new rows misclassify
correct metadata absence as disagreement and do not faithfully follow the
engine's conditional publication rule.

Apply the producer's usability/publication condition to the aggregate floor and
evaluation, while retaining diagnostics on a usable limited resolution. Also
audit a refused resolution whose source still has computed terms: the new
resolution check currently requires diagnostics irrespective of refusal status.
Derive usability from the independent state where possible; do not simply trust
an arbitrary printed status to suppress checks.

### P2 / ruling needed — R704-D3: exact equality can silently accept a wrong label

Location: `scripts/compare_b5_recompute.py:2204`.

The numerical condition outside the bar is correct. Inside the bar, the code
unconditionally sets the form to `None`, accepts either diagnostic/presence
choice, and may omit the presence row entirely. It does not use
`Comparison.atom`/`word`, check L9's decision operands, apply RC-CMP-11's
bit-identical exception, or record a `within_bar_undetermined` row.

Concrete synthetic producer witness: five comparative values all 1 J, half-widths
all 0.5 J. The independent and engine terms give point floor 1 J, guard 1.5,
and linear bound 1.5 J. The engine's strict `>` rule returns **false**. Printing
the limited diagnostic and claim metadata anyway yields **zero failed rows and
zero undetermined rows** from `compare_floor_limit`. All printed diagnostic
operands are the actual producer values; no rounding perturbation is introduced.
Witness: `DeltaRuleTests.test_strict_equality_does_not_accept_an_incorrect_limit_label`.

DLE-5 explicitly discloses the broader inside-bar permission, so this is not an
undocumented coding accident. It conflicts with a blanket assurance that wrong
labels cannot pass and is broader than the existing comparator header's
RC-CMP-11 rule. The lead should either require the existing two-sided FS3/F1
treatment (including exact strict equality), or explicitly rule that this new
classification has a broader exemption and describe its limits. This review
does not install that policy decision. No claim is made about proximity of any
real value to this threshold.

## Answers to the requested checks

1. **D-078 arithmetic.** The `not any(widths)` gate is preserved for valid
   recompute records. The threshold is guard times the **point** floor, not the
   widened/drift-adjusted published floor. The recompute's absolute linear
   residual bound and comparative `max(abs(delta) + width)` match
   `admissible_set_uncertainty_dominates_point_floor` and registered plan §5.
   Strict `>` is used outside the bar. Eighteen synthetic producer/recompute
   samples (n=5, 9, 10; both forms; widths 0, .001, 2 J) agree wherever the
   comparator decides the classification. The unresolved-publication and
   boundary qualifications above prevent an unconditional correctness verdict.

2. **Copy check.** All **63 mapped scalar leaves** of one synthetic two-arm,
   two-form contrast work in each exact and transported shape: every fill
   omission produces `copy_shortened`, every changed type produces
   `value_differs`, and every verdict omission with a retained fill leaf fails
   comparison or coverage. That is 378 scalar mutations. Both unchanged shapes
   exit 0. The routing-row exclusions prevent synthetic `cells/` and `forms/`
   row keys from creating false copy obligations. The exempt leaves still have
   R704-D1. No false refusal was found on supported, resolved shapes.

3. **Adjusted witnesses.** The three original expected failures were correctly
   converted into ordinary passing tests. The other three test adjustments are
   legitimate: accepting structural duplicate-row refusal for a wrong exact
   source still requires nonzero exit; setting both contrasts' domination terms
   preserves the 84-path historical census; subtracting the new
   `copy_shortened` pattern from that historical census keeps it a leaf-path
   census. Adding widths/linear terms to the distinct-value lookup witness
   satisfies the new independent precondition while retaining its three numeric
   disagreement assertions. These edits do not explain away the original bugs.

4. **Hash independence.** AST/import and source inspection found only stdlib
   imports in both production scripts, no `joulewise` import and no dynamic
   `exec`, `eval` or `__import__` call. The recompute is byte-identical at both
   range endpoints and `b5/analysis-r4`. Its SHA-256 remains
   `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`.

5. **Actual recompute schema and noncomputed states.**
   `scripts/independent_recompute_b5.py:1414` always retains `widths_j` and
   populates `linear_deviation_bound_j`, `guard` and
   `point_unguarded_floor_j` before returning `status="computed"`. The normal
   output assembly stores the complete record, not a projection. Thus this
   delta does not require a missing computed-field producer change.
   Below-minimum records have null guard/point and no linear term; unavailable
   widths/corner-cap records have null guard and no linear term. `limited_forms`
   skips those. `make_floors` also resets both forms when the reported cell is
   below minimum. A missing drift allowance is different: `make_floors` can
   change status to `not_computed` **after** retaining all four valid terms;
   `limited_forms` ignores that status and can still classify it as limited.
   This reinforces the need to distinguish a source's arithmetic classification
   from whether a resolution/combined floor can publish metadata.

Missing/malformed required terms on a purported computed record are silently
treated as no derived limit, rather than a distinct structure refusal. Printed
diagnostics then fail, but absent diagnostics need not. The unchanged real
recompute supplies these terms; I found no normal computed path omitting them.
This remains a robustness limit, not evidence of a current real-data failure.

## Verification

All named modules ran separately and sequentially with
`JW_B5_SYNTHETIC_ONLY=1 nice -n 10 python3.13 -B -m unittest tests.independent_recompute.<module>`.
All **336 requested tests passed**, with no skips or expected failures:

| Module | Tests | Time (s) |
| --- | ---: | ---: |
| `test_floor_limit` | 35 | 5.143 |
| `test_sol_review_704` | 10 | 1.379 |
| `test_input_gate` | 45 | 3.532 |
| `test_comparator` | 28 | 4.396 |
| `test_structural_rules` | 29 | 2.990 |
| `test_rc_cmp7` | 21 | 56.296 |
| `test_rc_cmp8` | 27 | 12.970 |
| `test_rc_cmp9` | 32 | 97.583 |
| `test_rc_cmp10` | 31 | 11.253 |
| `test_rc_cmp11` | 13 | 6.787 |
| `test_release_b5` | 27 | 3.470 |
| `test_review_fixes` | 38 | 4.708 |

The new `test_sol_delta_review_704` module, with the same environment/wrapper and
`-v`, ran 8 tests in 31.712 s: 3 pass and 5 expected failures for the findings above.
Expected-failure traces were checked at their final desired-behavior assertions,
not accepted on setup errors. The boundary witness's preconditions independently
assert that the actual engine returns false and the two independent threshold
operands are exactly equal. The mapped-leaf sweep passes all 378 mutations.
Aggregate test execution, including review iterations, stayed below 10 minutes.

`nice` printed `setpriority: Operation not permitted` on every invocation;
Python continued. The wrapper was used, but the priority change could not be
enforced/verified in this sandbox. `nice -n 10 python3.13 -B -m compileall -q
joulewise tests scripts/compare_b5_recompute.py scripts/independent_recompute_b5.py`
and `git diff --check` passed.

## Limits and handoff

Only repository text/code/Git objects and synthetic fixtures were accessed.
No network, real custody, real measurement data, sealed directories, model
weights, measurement pipeline, or running analysis job was accessed. The full
suite was not run under the explicit concurrent-job constraint. No coordination
state file was edited or kernel task registered. No MLX/native code changed;
there is no new Metal test for the lead to run.

Changed files are this report, the dated run-report pointer, and
`tests/independent_recompute/test_sol_delta_review_704.py`. Next exact step:
the lead dispositions D1/D2, rules on D3, implements the authorized fixes, audits
the new tests, converts resolved witnesses to ordinary tests, and requests a
delta review of production changes. A real blinded release check remains
lead-owned and unexecuted here. This report authorizes no release or merge and
infers no Block-5 outcome.
