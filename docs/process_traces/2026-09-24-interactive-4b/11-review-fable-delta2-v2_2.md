# Fable seat: second delta check of v2.2 (read-only, main 57a04e4e)

Filed by the lead from the seat's hand-back, condensed.

- **Lineage tags: no defect.** `launch_lineage_required` only switches on writer/receipt authentication of the CLI config path (`bundle.py:93`, `arm_readiness.py:11437`). No measurement code reads it or the campaign tags.
- **Prechecks as validity gates: safe, with one rule to add.** cadence_ratio = window ÷ max(p95 gap, bracketing max gap) must be ≥ 4.0 (`reduce.py:118`). A D cell at a 275 ms p95 on a 6.4 s window scores ≈ 23. Pre-register the per-arm invalidation rate as a reported endpoint with a stop rule: ≥ 3 of 6 cells invalid in one arm means stop and go to council. An arm-correlated failure is a finding, not something to re-run away.
- **2 runs per cell: fine.** The cell stays the unit. Average log E over the two runs, and report the within-cell difference as the harness noise floor.
- **The 32.6 J drift bound is an artefact of the attended bench.** `bound_w = max |any pre/post idle sample − pre mean|`, then × window duration (`reduce.py:472`). 32.6 J ÷ 6.40 s = 5.09 W on a 10 W attended floor. The quiet floor is ≈ 0.4 W, so in U this collapses to ≲ 1 J. It does not enter the paired-t test. Flag any cell whose E_drift_bound_j ÷ net > δ. An EQUIVALENT verdict must carry the maximum cell drift ratio. If U-state envelopes still exceed 3 % of net, the verdict is INCONCLUSIVE-by-attribution.
- **A new arm-correlated term (SHOULD_FIX).** The samples that straddle the window edges misattribute up to ¼·ΔP·elapsed per edge. That is ≈ 1.9 J per edge for D at 248 ms and ≈ 0.9 J for I at 118 ms: a systematic under-count that scales with cadence. Report it per arm beside the verdict. Downgrade DIFFERENT to INCONCLUSIVE when the D–I contrast is smaller than the difference of the two edge bounds.
- **CPU probe after the runs: fine.** Add a ≥ 30 s idle guard after it.
- **Moot now:** the guard bands, the two-integral check, the request-length worry inside δ, and the net ≤ 0 rule.
- **Stage 0 attended numbers are upper bounds** on both spread and drift. Say so in the sizing table.
- **Verdict:** RUN AFTER LISTED FIXES. All are text edits.
