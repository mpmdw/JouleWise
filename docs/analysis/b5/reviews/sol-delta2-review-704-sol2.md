# Second Sol delta review of PR #704 — seat sol2

Date: 2026-11-07 PST (2026-11-08 UTC). Branch:
`b5rel/2026-11-08-sol-delta2-704-sol2`.
Reviewed range: `bea480f29..131369801` (`0f2489d90`, `131369801`).
The tree started clean at the requested head. This review changes tests and
reports only; the lead owns dispositions and final verification.

## Verdict: ADMIT_WITH_FIXES

R704-D1, D2's below-minimum/drift cases, and D3's strict-equality and automatic
hold cases now pass their witnesses. All 97 tests in the four touched
`tests/independent_recompute/` modules pass without skips or expected failures.
No new false agreement was demonstrated in the reviewed metadata paths.

One small new exit-classification defect remains: a comparator exit 2 can
become release exit 1 if its written output contains undetermined rows. This
never releases a result, but contradicts the explicit 0/1/2 contract. Fix
R704-S2-2 before admitting that contract as coherent.

There are also two qualifications: the finite-gate usability proxy does not
model a general transport refusal (an inherited limitation, R704-S2-1), and a
correct producer output can hold forever inside the bar. The latter is the
lead's stated conservative policy, not a request to weaken the gate. It must
be disclosed with its structural-equality qualification below. This verdict
provides no unseal, publication, merge, or real-data release authority.

## Findings and limits

### P3 — R704-S2-2: comparator refusal can be reported as semantic hold

Location: `scripts/release_b5.py:408` (new), with exit mapping at `:460`.
Witness: `ReleaseExitTests.test_exit_two_with_undetermined_rows_stays_a_refusal`
in `tests/independent_recompute/test_sol_delta2_review_704_sol2.py`.

Stage (c) receives an actual process status separately from the output file.
With valid positive comparison counts, empty coverage defects, a valid
`limit_undetermined` key, and process exit **2**, the new branch returns
`("within_bar_undetermined", True)` instead of
`("comparator_refused", False)`. `_release` maps that tuple to exit **1**.
The same payload without an undetermined row correctly preserves refusal.

This is a process/output inconsistency probe, not evidence that the current
comparator normally produces such a pair. Its ordinary explicit refusal
payload (`refused`) still takes the earlier refusal branch. Nonetheless,
a process that failed after writing a summary must not be reclassified by
that summary. Require an accepted comparator process status before the new
hold branch; make exit 2/other failing process statuses take refusal
precedence. The older disagreement branch has analogous precedence behavior;
fixing the common precedence is preferable to special-casing this witness.
Neither case can turn a hold/refusal into agreement.

### R704-S2-1 — inherited limit: a finite source floor does not prove transport usability

Location: `scripts/compare_b5_recompute.py:2275` and `:2298`;
producer: `joulewise/analysis_engine/inputs.py:5271`, `:5307`;
conditional aggregation: `joulewise/analysis_engine/__init__.py:260`, `:314`.
Witness: `TransportProxyTests.test_transport_refusal_must_not_require_aggregate_limit_metadata`.

A synthetic pure-API request first resolves as transported. Raising only the
consumer's maximum power makes the real `resolve_floor` refuse with
`power_outside_calibrated_envelope`, while its calibration source retains a
finite floor gate. The real `_combined_floor`, paired with a usable limited
arm, correctly publishes no aggregate point diagnostics or claim limit.
The comparator's `usable_arms` still returns `[True, True]` and
`compare_floor_limit` produces **15 failed rows** against that correct
metadata absence. The ordinary precondition test separately proves the real
resolver reaches both statuses; the expected failure is at the final desired
metadata-agreement assertion, not fixture setup.

An in-memory replay with the **parent comparator at bea480f29 also produces
15 failed rows**. This is an incomplete generalization of D2's usability
claim, not a newly introduced disagreement. The synthetic fixture exercises
the pure resolver/metadata functions, with source arithmetic from the actual
independent estimator. It does not prove complete authenticated Block-5
custody can otherwise release in this state. Existing null-versus-finite
floor checks already hold a refused resolution.

The scope distinction matters: the registered Block-5 manifest specifies
`transport.mode == exact_stack_only` for both contrasts, and plan §5 specifies
same-model, phase/length, singleton-source transfer. The production request
builder uses `exact_stack_serving_cell` with empty consumer stress on that
successfully bound route; it does not apply the general stress-envelope
transport test (`inputs.py:4898`, `detection_floor.py:3085`). Thus this witness
is **not a demonstrated new false hold on the intended, successfully bound
Block-5 route**. A binding/provenance refusal also cannot be inferred solely
from a finite source gate. Do not describe the proxy as universally equivalent
to engine usability. The lead should explicitly retain the narrower scope,
or extend independent resolution derivation if general transported refusals
are meant to be covered; trusting a printed refusal to suppress checks would
reopen the safety problem.

### Disclosed consequence of D3: legitimate permanent holds are possible

Locations: `scripts/compare_b5_recompute.py:2249`, `:2255`;
`BoundaryEvidenceTests` in the new module.

A form with nonzero widths and
`abs(linear - guard * point) <= max(1e-6 J, 1e-6 * abs(guard * point))`
is inside the bar. If its correct strict-`>` result is false, the producer
prints no diagnostic. Consequently there are no printed operands to satisfy
the exception: the comparator records `within_bar_undetermined`, and release
holds, even when the independently recomputed equality is exact. Rechecking
the same immutable inputs repeats the hold; disclosure alone does not provide
a mechanical override. A lead ruling/code change or further independently
verifiable decision evidence would be needed, rather than repeated reruns.

The five-member equality witness uses the real producer and independent
estimator. An additional ten-member comparative example uses values
`[1, 0, ..., 0]` and widths `[0, .01, ..., .01]`. Both estimators give
`point = linear = 1`, `guard = 1`, and a false limited predicate. The real
combined-floor producer correctly prints no diagnostic; the comparator
records four undetermined aggregate rows. These are synthetic numbers only.

**Likelihood:** for nondegenerate continuous operands the one-part-per-million
relative band (or 1 microjoule absolute band) is narrow; closeness would
usually need a near-boundary coincidence. It is unsafe to equate that with a
probability or call the hold negligible. At n >= 10 the guard is exactly 1.
When the comparative point floor is set by max absolute delta and that
maximizing member has zero width, other members can have positive widths
without raising the linear maximum. Equality then persists over a range of
those widths. It is structural, not a measure-zero rounding event. All widths
zero are separately skipped and do not cause this hold. With positive width
on the maximizing member, that particular equality plateau disappears.
No real widths, values, outcomes, or empirical probability were inspected or
inferred. The design therefore permits permanent holds; it does not establish
how often this Block-5 run will encounter one.

## Requested checks

1. **R704-D1:** complete leaf/type/presence copy comparison now runs in both
   directions. Original omission, changed exempt word/flag, reverse omission,
   and exact/transported leaf sweeps pass. A new empty-extra-container CLI
   probe refuses with exit 2 and `floor_limit_copy/copy_extra`; empty containers
   no longer disappear merely because they print no scalar.
2. **R704-D2:** the real mixed resolved/refused producer witness now has no
   aggregate-metadata disagreements when the independent partner gate is null.
   The usable limited resolution retains its own required diagnostic. Computed
   records missing/malformed terms refuse `recompute_floor_terms_missing`;
   retained terms on `not_computed` records are ignored. General transport
   usability has the qualified inherited limitation above.
3. **R704-D3:** an incorrect limited label at exact equality fails; just-above
   and just-below cases decide strictly only with identical printed point,
   guard and product operands. Missing/slightly different operands create
   listed undetermined rows; numerical agreement does not release them.
   The comparator and release tests prove exit 1 with keys/count only and
   reason `within_bar_undetermined`. A disagreement alongside such rows still
   holds, possibly under the ordinary disagreement/refusal reason.
4. **Independence:** `scripts/independent_recompute_b5.py` is unchanged across
   the reviewed range. SHA-256 is
   `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`.
   AST/import inspection finds only stdlib imports, no `joulewise` import,
   and no direct `exec`, `eval`, or `__import__` call. The comparator delta
   adds no repository estimator import. L9 does not print the linear bound;
   D3 explicitly substitutes the recompute's bound on that side. This is the
   stated policy, not independent observation of an unprinted L9 operand.
5. **False agreement / exit contract:** the reviewed wrong ownership,
   missing/extra/divergent copy, wrong exact-threshold label and malformed
   computed-term probes do not exit 0. Normal release agreement is 0,
   disagreement/undetermined is 1, ordinary refusal is 2. R704-S2-2 is the
   remaining exit/payload consistency exception. The existing named coverage
   exemptions remain exemptions; this review does not certify independently
   derived correctness of exempt discipline/class/source words merely because
   two copies agree, or close the broader LEAN-COVERAGE-AUDIT gaps.

## Verification

Each module below ran in its own process, sequentially:
`JW_B5_SYNTHETIC_ONLY=1 nice -n 10 python3.13 -B -m unittest <module>`.
The new review module also used `-v`.

| Module | Tests | Result | Seconds |
| --- | ---: | --- | ---: |
| `tests.independent_recompute.test_floor_limit` | 37 | pass | 12.001 |
| `tests.independent_recompute.test_sol_delta_review_704` | 21 | pass | 198.659 |
| `tests.independent_recompute.test_sol_review_704` | 10 | pass | 1.757 |
| `tests.independent_recompute.test_release_b5` | 29 | pass | 10.437 |
| `tests.test_single_count_discipline_census` | 6 | pass | 27.381 |
| `tests.independent_recompute.test_sol_delta2_review_704_sol2` | 9 | 7 pass, 2 expected failures | 0.905 |

The two new expected-failure markers were temporarily disabled **in memory**
and run with `unittest.TextTestRunner`: exactly two assertion failures,
no setup errors (0.007 s). The first shows the 15 unexpected metadata rows;
the second shows `('within_bar_undetermined', True)` instead of
`('comparator_refused', False)`. Expected-failure markers remain in the
committed witnesses and are not claimed as resolved bugs. Parent/candidate
transport comparisons also ran in that bounded synthetic audit.

The final module set contains 112 tests: 110 pass and 2 expected failures.
Total test time including review iterations stayed below five minutes.
`nice` printed `setpriority: Operation not permitted`; Python continued, so
requested priority could not be enforced in this sandbox.

`python3.13 -B -m compileall -q` on the two changed scripts, unchanged recompute,
four touched independent-recompute test modules, new review module and census
passed. `git diff --check` passed. No full suite was run, per the explicit
concurrent-job constraint. No MLX/native code changed; there is no additional
Metal test for this delta. Real custody/hardware/release validation remains
lead-owned and was not run here.

## Handoff

Changed files: this report, its dated pointer under `docs/run_reports/`, and
`tests/independent_recompute/test_sol_delta2_review_704_sol2.py`. No production
code, coordination state, or kernel tasks were changed. No network, real
measurement data, real restricted directory, model weights, measurement
pipeline, or running analysis job was accessed. Referenced
external paths remained text. All test custody was synthetic under temporary
directories.

Next exact step: the lead dispositions R704-S2-2, fixes comparator-process exit
precedence, independently audits the witnesses, and reruns the release and
second-review modules. Record the narrower D2 usability scope and explicitly
disclose that D3 can hold correct immutable outputs indefinitely. Preserve
Ed's unseal gate; this review makes no statement about sealed outcomes.
