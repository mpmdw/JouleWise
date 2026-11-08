# Sol delta-2 review of PR #704 — seat sol1

Date: 2026-11-07 PST. Branch: `b5rel/2026-11-08-sol-delta2-704-sol1`.
Reviewed: `bea480f29..1313698017e8277e4791b368eb8fde0d94748b1e`
(`0f2489d90`, `131369801`). The previous review was read from
`origin/b5rel/2026-11-08-sol-delta-704:docs/analysis/b5/reviews/sol-delta-review-704.md`.
The lead's dispositions in the task brief were the authority for this review;
no network or PR lookup was used.

## Verdict: ADMIT_WITH_FIXES

The original probes now pass, including a mechanical comparator/release HOLD
for undetermined limit forms. D1's complete, type-preserving copy check works.
Two gaps remain in the intended D2/D3 guarantees: the unprinted linear bound is
assumed identical when it can differ across the implementations, and finite
source-floor gates do not establish transport usability. Disposition these
before admitting the comparator delta. Neither finding is evidence about a
Block-5 outcome, and this review authorizes no unsealing.

Production code is unchanged. The new witness module has five passing tests
and three **expected failures** for the two open findings. Those markers are
not successful refusals. Each expected-failure traceback was checked: all
preconditions complete, and failure is at the final desired-behavior assertion.

## Findings

### P2 — R704-DELTA2-S1: the bit-identity exception assumes an unprinted operand

Locations: `scripts/compare_b5_recompute.py:2251`, `:2253`;
`scripts/independent_recompute_b5.py:1431`;
`joulewise/detection_floor.py:1008`.

The new check establishes equality of the printed point floor, guard and
guarded point floor, then calls `Comparison.atom` with `linear` on **both**
sides. The producer's linear bound is not printed, so the check has not
established its equality. The two absolute-floor implementations use different
floating-point expressions:

- Recompute: `abs(v - mean) + w * (1 - 1/n) + sum(other_widths) / n`.
- Producer: `abs(residual) + w * (n - 1) / n + (fsum(widths) - w) / n`.

A tiny actual-producer witness uses absolute values `[9, 9, 10, 11, 11]` J and
half-widths `[2.6242141276127544, 0.3280267659515943, 2.7647970273062943,
0.46860966564513473, 2.905379926999835]` J. **All numbers in this paragraph are
synthetic.** The actual producer and recompute have identical point floor
`3.040955639268682`, guard `1.5`, and guarded point `4.561433458903023`.
The producer's linear bound is exactly that threshold, and its actual strict
`>` classifier returns false. The recompute's bound is
`4.561433458903024`, one ulp above it. Printing the incorrect limited metadata
with the actual producer diagnostic yields **no failed rows and no
undetermined rows** from `compare_floor_limit`.

Witness:
`Delta2RuleTests.test_rounding_of_unprinted_absolute_bound_must_not_accept_wrong_limit_label`.
It independently asserts the producer's false decision, exact equality of its
bound to the threshold, the recompute's one-ulp excess, and identity of all three
printed diagnostic operands before its final refusal-or-HOLD assertion fails.
This is a function-level false-agreement witness for the changed metadata
check, not a demonstration that an entire synthesized release agrees.

Recommendation: use the strict bit-identity exception only when the **full**
decision operands are established on both sides. If the unprinted producer
bound cannot be independently reconstructed and compared, leave the form
undetermined and HOLD. The disclosed substitution of the recompute's bound
does not support the assurance that an incorrect label cannot pass. No change
to the pinned independent recompute is needed merely to take the conservative
HOLD path.

### P2 — R704-DELTA2-S2: source arithmetic availability is not transport usability

Locations: `scripts/compare_b5_recompute.py:2158`, `:2275`, `:2303`;
producer: `joulewise/analysis_engine/inputs.py:5308`,
`joulewise/analysis_engine/__init__.py:256`, `:314`.

`usable_arms` returns true whenever a source cell's independent floor gate is
finite. A source can have perfectly valid, finite, attribution-limited floors
while its consumer is correctly refused for transport outside the calibrated
power, duration, cadence or other envelope. The recompute has no transport
model; its finite source gate cannot decide that consumer predicate.

The new fixture calls real `resolve_floor` and `_combined_floor`, without
mocking either. Arm A resolves exactly. Arm B has a finite limited source but
its consumer power exceeds the calibrated envelope, so the producer returns
`status="refused"`, reason `power_outside_calibrated_envelope`. It correctly
publishes neither aggregate diagnostics nor B's resolution diagnostics.
`usable_arms` nevertheless returns `[True, True]`, and the metadata checks
produce **29 failed aggregate rows and 7 failed B-resolution rows**. With B's
consumer inside the envelope, the actual transported producer metadata passes
both aggregate and resolution diagnostic checks.

Witnesses:

- `test_transport_refusal_with_finite_source_gate_requires_no_aggregate_metadata`.
- `test_transport_refusal_with_finite_source_gate_requires_no_resolution_metadata`.

Both are expected failures in `Delta2RuleTests`; the in-envelope control is an
ordinary passing test. The fixture uses registered cell ids for these metadata
checks but is not a complete registered Block-5 release fixture.

This is a remaining conditional-publication gap, not a newly demonstrated
release deadlock: the earlier implementation already required this metadata,
and existing floor-number comparisons also hold a refused consumer against a
positive recompute source gate. The delta fixes the below-minimum D2 example
but does not implement the engine's full usability predicate for transport.
Do not describe these extra metadata failures as evidence of wrong producer
publication. Independently establish transport eligibility/refusal before
using it to require metadata; trusting an arbitrary printed refusal alone is
not a satisfactory fix.

## Requested checks

1. **R704-D1 and original probes.** All original witness modules pass as
   ordinary tests. Complete copy comparisons cover floor/resolution class and
   source words, discipline words/flags, diagnostics, and claim `floor_limit`,
   both directions. The new copy probe also checks empty-container type and
   presence, `False` versus `0`, and `1` versus `1.0`. No remaining D1 gap was
   found.
2. **R704-D2.** The original unresolved combination now passes its metadata
   check. A usable limited arm retains its diagnostic when its partner lacks
   a gate. `not_computed` retained terms do not classify a limit, and missing
   terms on a computed record refuse `recompute_floor_terms_missing`. Correct
   in-envelope transported metadata passes. The transported-refusal limitation
   is S2 above.
3. **R704-D3 and false agreement.** The original strict-equality comparative
   probe now rejects the wrong printed label. Missing or nonidentical printed
   operands produce recorded limit-decision rows, comparator exit 1, and
   release exit 1 with `within_bar_undetermined`, count and keys only. S1 shows
   why the full decision still lacks an independently verified operand.
   Existing named derivation exemptions remain exemptions; copy equality does
   not prove their scientific semantics. No blanket absence of false agreement
   is claimed.
4. **Hash independence.** The recompute is unchanged across the review range.
   Its SHA-256 is
   `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`.
   AST/import inspection of both production scripts found only stdlib imports,
   no `joulewise` import, and no `exec`, `eval` or `__import__` call. Test code
   imports producers deliberately to compare the independently implemented rules.
5. **Release exits.** Synthetic execution confirms exit 0 on agreement; exit 1
   on an undetermined form or family disagreement; exit 2 when recomputation
   stops. There is a pre-existing qualification to the header's shorthand
   "2 on comparator refusal": a disagreeing mapped fill copy also becomes
   unmapped, so the comparator can exit 2 while release reports
   `comparator_disagreement` and exits 1. The new ordinary exit-matrix witness
   records that exact behavior. It remains fail-closed, but it is not strict
   propagation of comparator exit 2. The lead should clarify whether that
   precedence is the intended public contract. The new undetermined-only path
   itself has coherent 1/1 exits and carries no numeric value.

## Correct output can remain held indefinitely

This is now disclosed in DLE-5 and mechanically enforced. A correct nonlimited
form at or just below the threshold prints no diagnostic. Inside the bar,
absence supplies no operands for the bit-identity exception; it is therefore
undetermined even if every numeric comparison agrees. Repeating the same
deterministic run cannot clear that HOLD. The new test exercises actual
comparative producer outputs with five values of 1 J and half-widths of 0.5 J,
and of `0.5 * (1 - 1e-9)` J: both are correctly nonlimited and remain held.
These are synthetic examples only.

The bar is `max(1e-6 J, 1e-6 * abs(guarded_point_floor))`: away from zero this
is a narrow, roughly one-part-per-million neighborhood on each side. That
suggests a small region for generic continuously varying operands, **not a
measured probability**. Exact algebraic equality is possible, and differing
floating-point reductions can also defeat the exception on correctly printed
limited output. There is no release-liveness guarantee. Conditional on correct
absent-diagnostic output lying in that region, unchanged reruns always HOLD.
Without outcomes or a justified distribution I cannot estimate how often real
Block 5 enters the region. A lead disposition is needed to clear such a case;
rerunning or widening the bar is not an answer.

## Verification

Each listed unittest module ran in its own process with
`JW_B5_SYNTHETIC_ONLY=1 nice -n 10 python3.13 -B -m unittest <module>`.
The four touched independent-recompute modules ran one at a time as requested.

| Module (under `tests.independent_recompute` unless stated) | Tests | Result | Seconds |
|---|---:|---|---:|
| `test_floor_limit` | 37 | pass | 12.159 |
| `test_release_b5` | 29 | pass | 9.283 |
| `test_sol_delta_review_704` | 21 | pass | 192.134 |
| `test_sol_review_704` | 10 | pass | 2.320 |
| `test_rc_cmp11` | 13 | pass | 12.478 |
| `test_input_gate` | 45 | pass | 8.052 |
| `test_comparator` | 28 | pass | 9.757 |
| `test_structural_rules` | 29 | pass | 5.100 |
| `test_review_fixes` | 38 | pass | 8.323 |
| `tests.test_single_count_discipline_census` | 6 | pass | 35.955 |
| `test_sol_delta2_review_704_sol1` | 8 | 5 pass; 3 expected failures | 2.733 |

All **256 existing targeted tests pass**; none is skipped or expected to fail.
The extra regression modules cover the changed threshold, routing, copy and
coverage behavior. Expected-failure traceback inspection separately confirmed
the three new failures at their final desired-behavior assertions. Total test
execution including iterations remained well under 20 minutes. One brief
witness-inspection process overlapped the census test after a pending-session
result was misread; this deviated from the one-at-a-time instruction. Both
finished, and subsequent checks were sequential.

`nice` reports `setpriority: Operation not permitted`; Python continues, so the
wrapper was used but its priority change was not enforced. Compilation and
final diff validation are recorded in the dated run report. Python 3.11 is not
installed here; the lead/CI must verify that interpreter, particularly the
rounding witness's preconditions. No MLX code changed and no new native Metal
test is required by this review.

## Handoff and limits

Changed files: this report, the new witness module, and the dated run-report
pointer. No production fix, coordination-state edit, kernel registration,
network access, model download, real-data access, full suite, heavy pipeline
or hardware measurement was performed. Absolute custody paths in repository
text were not followed. No other review seat was launched from this session.

Next exact step: the lead dispositions S1/S2, clarifies the release exit-code
qualification, fixes the independently decidable metadata checks without
trusting arbitrary printed statuses, and has both independent seats review
the resulting production delta. Audit these tests and convert only genuinely
resolved witnesses to ordinary tests. A blinded real release check and Ed's
separate unseal OK remain lead-owned and unexecuted here.
