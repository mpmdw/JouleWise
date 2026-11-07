# DRAFT — independent-recompute D-190 null agreement

For lead entry in the decision log: the lead ruled **blind on 2026-11-05,
before any block-5 value was seen**, that [D-190](../decision_log.md)'s
registered not-resolvable or not-estimable null agrees only when release and
independent recompute are both null and carry the same registered reason and
code (the complete code set when more than one applies). Record the distinct
status `agree_null:<reason>` and count these agreements separately from numeric
passes. Different reasons/codes, unregistered reasons including lookalikes,
and a null opposite a number disagree. Numeric pairs retain the recompute's
coded comparison bars. Missing data and nonfinite inputs acquire no null
waiver. The renderer retains the registered null wording. This draft records
the supplied lead ruling; adoption into the decision log remains lead-owned.

## Synthetic directory clarification (blind, 2026-11-05)

The lead permits only the S10 harness's freshly generated synthetic
`restricted/` directories under TMPDIR or this clone. Real study paths
remain prohibited. The full r2 driver → recompute → comparator baseline
now completes with exits 0/0/0: 2,514 comparisons, 1,490 numeric and 1,024
categorical agreements, no null agreements (reason counts {}), and no
disagreements. Coverage has 1,056 uncovered and 0 unmapped paths. This
matches the readiness lane's 2,514/0 count. See the [run report](../run_reports/2026-11-05-recompute-d190-nulls.md)
and [fresh baseline metadata](../process_traces/2026-11-05-recompute-d190-nulls/baseline-summary.json).
The issued-output S10 fixture does not certify the n<2 branch.

## Recompute representation ruling (blind, 2026-11-05)

The lead additionally ruled that, wherever the registered estimator is not
estimable, recompute must emit the same registered not-estimable null and
reason code as release, never a numeric placeholder. For n<2 the independently
computed row carries `null_reason={"outcome":"not_estimable",
"codes":["insufficient_complete_blocks"]}`; D, raw p, adjusted p and df are
null. Estimator intervals have null endpoints and deterministic terms are
empty. Primary, timing-bound sensitivity and scaled-allowance recomputations
preserve this representation. Holm keeps the frozen two-test family and
leaves missing tests null; a finite peer still receives the two-test
correction. Finite-pair arithmetic and coded comparison bars are unchanged.

The comparator's df binding now reads the explicitly emitted n<2 null, with
the registered reason checks. A missing df or any numeric placeholder still
disagrees; rule (3), null versus numeric, is unchanged. This is a representation
change on the independent recompute side, not a change to the registered
engine, its estimator or any measurement data. Decision-log adoption remains
lead-owned.

## Post-change synthetic acceptance

The fresh full r2 driver → patched recompute → comparator rerun also exits
0/0/0: **2,514 comparisons, 1,490 numeric and 1,024 categorical agreements,
0 agree_null (by reason {}), 0 disagreements, 1,056 uncovered and 0 unmapped**.
Counts and coverage match the fresh pre-change baseline and the readiness
lane's 2,514/0. No bar changed.

The separate n=1 estimator-field probe compares two contrasts, 13 fields
each: **26 agree_null:not_estimable:insufficient_complete_blocks**, zero
numeric agreements and zero disagreements. Whole-window uncovered/unmapped
are not assessed by that probe. Tests also cover n=0/1 through the real
recompute CLI entrypoint in primary, timing-bound and scaled-allowance
variants. The full S10 fixture retains the registered minimum of five;
no full n<2 window certificate or study validation is claimed. Exact
commands, limits and [fresh post-change metadata](../process_traces/2026-11-05-recompute-d190-nulls/patched-summary.json)
are recorded in the run report and trace.
