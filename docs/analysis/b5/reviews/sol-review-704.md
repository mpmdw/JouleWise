# Independent executing review of PR #704

Date: 2026-11-07 PST. Branch: `b5rel/2026-11-08-sol-review-704`.
Reviewed head: `337e74b59f6dd0c25496d69727e392e09980b84a`.
Reference analysis: `b5/analysis-r4`, `ab1e0098dbd0ab839c8f278088221aa8aa4de8d2`.

## Verdict: ADMIT_WITH_FIXES

The arithmetic mapping is sound for the supported printed leaves, but the current
head is **not admitted for merge/release** until R704-1 and R704-2 are fixed and
independently checked. Synthetic mutations demonstrate comparator exit 0 despite
incorrect diagnostic ownership or disagreement between verdict and fill. Neither
finding demonstrates an incorrect claim gate or outcome being accepted; both
break the requested routing/copy guarantees on the newly admitted metadata.

This review changes tests and reports only. It does not implement the fixes.

## Findings by severity

### P2 — R704-1: transported diagnostics can belong to the other resolution

Location: `scripts/compare_b5_recompute.py:2174`, `:2203`, `:2225`.

`compare_arms` passes the entire contrast to `compare_point_diagnostics`.
`diagnostic_cells` consequently accepts either of that contrast's registered
floor cells, regardless of the resolution's own registered arm/source. The
separate `source_cell_ids` routing rows validate the printed source list, but
never join that list to the diagnostic dictionary's cell keys.

Reproduction: create the existing synthetic transported fixture, then swap the
two resolutions' complete diagnostic dictionaries in both verdict and fill.
Keep `source_cell_ids`, transport groups and all numbers unchanged. The
diagnostic cell ownership is now B under resolution A and A under resolution B;
the aggregate diagnostic union is preserved. The comparator still exits 0, with
no failed family and no unmapped leaf. Equal synthetic point values expose the
missing ownership check without requiring a numeric discrepancy.

Witness: `SolReview704Tests.test_transported_diagnostic_must_belong_to_its_resolution`
in `tests/independent_recompute/test_sol_review_704.py`.

Required fix: constrain resolution diagnostic cells to that resolution position's
registered sources, retaining literal registry lookup and per-key routing rows.
The floor and evaluation's aggregate dictionaries may continue to use the
contrast-wide source set. A valid cell of the other arm must produce a failed
routing row even when its numeric values happen to coincide.

### P2 — R704-2: a fill can silently omit verdict floor-limit numbers

Location: `scripts/compare_b5_recompute.py:1140`, `:2178`, `:4055`, `:4099`.

Comparison rows come from the verdict; coverage walks only leaves actually
present in the fill. The expected-check table does not require the conditional
`floor_limit` group or its diagnostic descendants. The existing shortened-copy
check covers specific lists, not these dictionaries. Thus deleting a fill leaf
does not create an absent-side comparison or an uncovered leaf.

Two independent witnesses both retain the complete verdict and return exit 0,
with no failed family or unmapped leaf:

- Delete `claim_evaluation.floor_limit.point_floor_diagnostics[CELL_A].absolute`
  only from the fill. Its three numeric leaves and two words disappear.
- Delete the entire `claim_evaluation.floor_limit` only from the fill, including
  its `published_floor_j` number.

Witnesses: `test_fill_cannot_omit_a_verdict_diagnostic` and
`test_fill_cannot_omit_the_whole_floor_limit` in the same review test module.
The PR's changed-value copy test succeeds, but does not exercise missing copies.

Required fix: when verdict metadata is present, require its corresponding fill
group and all copied descendant keys/values, with type-preserving equality.
Check both directions. This is a copy-preservation requirement, not a new
derivation of which forms should be attribution-limited. Audit the analogous
floor and resolution diagnostic copies for the same omission pattern.

## Requested checks and supporting evidence

1. **Bars and claims.** The commit changes no bar configuration, numeric bar
   implementation, L9 producer, or recompute. New point/guard/product rows use
   the existing `floor_j` family; `published_floor_j` uses `floor_gate_j`.
   Both bars remain `max(1e-6, 1e-6 * abs(L9))`. The flat diagnostic numeric
   exemption is removed. The new discipline rule accepts words/booleans only;
   it adds no numeric exemption. The operative widened/drift-adjusted floor
   remains distinct from the diagnostic point floor, as registered in §5.
   `claims.evaluate_claim` gates on its `floor_gate_j` argument and copies the
   point diagnostics as metadata. Existing non-derived class/source and
   discipline-word exemptions are retained as disclosed in DLE-5.

2. **Independent arithmetic and hash.** The recompute uses standard-library
   imports only; no `joulewise` import or dynamic repository import was found.
   Its bytes at the reviewed head and r4 have the identical SHA-256
   `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`.
   `point_floor` implements the two forms' deviations/prediction and maximum
   in plan §5; `floor_estimate` supplies the registered guard. Every supported
   printed diagnostic number maps to those independent values or their
   product. The published claim-floor copy maps to the independent contrast
   floor gate. Missing independent point values fail closed in my probe.

3. **Product and routing.** Actual producer diagnostics from tiny synthetic
   absolute and comparative samples agree with independent arithmetic for
   n=5, 9 and 10 (six subcases). A compensating point/guard error that preserves
   their product fails both operand comparisons. Distinct model/form values
   verify that lookup does not accidentally alias equal fixture values.
   Invented lookalike cell ids and changing an exact resolution's source to
   the other arm fail routing. Transported diagnostic ownership has R704-1.
   The product comparison uses the existing tolerance; it is not an additional
   exact algebraic-equality check on the three printed operands.

4. **Agreement despite producer disagreement.** The changed-value copy checks
   work, but the universal guarantee is false at this head: R704-1 and R704-2
   have successful CLI witnesses. Expected-failure tracebacks were inspected;
   all three failures are the final `assertNotEqual(0, 0)`, not fixture setup
   or another preliminary assertion.

5. **Leaf count.** `14 + 10C + 5R` correctly describes newly unmapped
   **normalized path names**, for the v2 discipline shape described in DLE-5.
   The 14 are two class/source words, one published-floor number and eleven
   discipline words. Each cell/form pair contributes five floor and five
   evaluation paths; each distinct resolution diagnostic path prefix
   contributes five. Floor/resolution class/source and discipline copies
   were already covered and are not part of this delta. Lists collapse to
   `*`, so R is not the count of diagnostic objects or comparison rows.
   A synthetic two-contrast fixture has C=6 and R=2 (exact resolutions):
   parent coverage reports exactly 84 unmapped paths and the PR coverage
   reports none. No real leaf census was opened or inferred. Other supported
   discipline versions have different field counts; 14 is not a universal
   count for every historical version.

## Verification

All modules ran separately, sequentially, using Python 3.13 and `nice -n 10`.
Each invocation printed `nice: setpriority: Operation not permitted`; Python
continued. Thus the requested wrapper ran, but priority adjustment could not
be verified/enforced in this sandbox. Aggregate test execution, including
repeated review probes and the census recheck, was under two minutes.

| Command | Result |
| --- | --- |
| `nice -n 10 python3.13 -B -m unittest tests.independent_recompute.test_floor_limit` | 15 passed, 2.905 s; no skips |
| `nice -n 10 python3.13 -B -m unittest tests.independent_recompute.test_input_gate` | 45 passed, 3.527 s |
| `nice -n 10 python3.13 -B -m unittest tests.test_single_count_discipline_census` | 6 passed; checked again after adding the review tests |
| `nice -n 10 python3.13 -B -m unittest tests.independent_recompute.test_comparator` | 28 passed, 4.362 s |
| `JW_B5_SYNTHETIC_ONLY=1 nice -n 10 python3.13 -B -m unittest -v tests.independent_recompute.test_sol_review_704` | 10 tests: 7 passed, 3 expected failures exposing the findings; six producer/guard subcases |
| Custom `unittest.TextTestRunner` over that review module, same environment/wrapper | Same result; confirmed all expected-failure traces end `AssertionError: 0 == 0` |
| `nice -n 10 python3.13 -B -m compileall -q joulewise tests scripts/compare_b5_recompute.py scripts/independent_recompute_b5.py` | Passed |
| `git diff --check` | Passed |

An initial producer probe used absolute-energy-sized comparative deltas; its
n=5 sample was not attribution-limited, so the fixture's classification
assertion failed. Replacing them with small synthetic comparative deltas made
that intended precondition hold. This was a review-fixture correction, not a
production arithmetic failure.

The added tests deliberately keep three `expectedFailure` annotations. They
are witnesses of unresolved defects, not evidence that refusal works. Remove
those annotations when the fixes make their refusal assertions pass.

## Blinding, limits and handoff

Only repository code/text and newly generated synthetic fixtures were used.
No network, measurement pipeline, real restricted directory, external custody,
model download, or running analysis job was accessed. The required census's
four source roots were checked for restricted directories and symlinks before
its recursive source scan; none were present. No coordination-state file was
edited and no kernel task was registered. The full suite was intentionally
not run under the brief's concurrent-job constraint.

No MLX/native code changed; this review requires no Metal test. Actual release
acceptance remains untested here. The lead should fix both findings, audit the
new tests, rerun the focused modules with the three witnesses converted to
ordinary tests, and obtain a delta review before any authorized blinded r4
release check. This report does not authorize a release or assert anything
about real Block-5 values/outcomes. The lead must decide the final disposition
of the findings; classification itself remains outside the independent
recompute's disclosed scope.
