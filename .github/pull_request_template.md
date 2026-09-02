## Gate ledger (D-118 / D-121)

Fill every row as `RUN <repo-relative-path>`, `RUN <commit-sha>`, or `NOT-RUN`; item 12 must name the final head sha.

Row labels are keys; the authoritative gate text is D-118 / D-121 in docs/decision_log.md (and D-170 for this ledger).

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | NOT-RUN |
| 2 | Paired distinct lenses: contract + execution (physics if measurement-adjacent) | NOT-RUN |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied | NOT-RUN |
| 4 | Delta re-audit of every fix round | NOT-RUN |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | NOT-RUN |
| 6 | Opus counter-review on the near-final head | NOT-RUN |
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | NOT-RUN |
| 8 | Overbuild / merge-ability prune | NOT-RUN |
| 9 | Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded | NOT-RUN |
| 10 | Final-head fresh-eyes review after every post-review commit | NOT-RUN |
| 11 | CI green on final head + post-merge cross-unit integration review | NOT-RUN |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable | NOT-RUN |

## Summary

<!-- What changed and why? -->

## Verification

<!-- Commands run and their outcomes. -->
