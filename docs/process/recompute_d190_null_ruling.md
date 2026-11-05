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
