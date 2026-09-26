Tier: full|light

Impact statement (answer each line for this PR):
(i) Raw-bundle byte or recorded timestamp: TODO
(ii) Reduced energy, time, token count or correctness score: TODO
(iii) Admit, refuse, select or exclude decision over bundles, nights, blocks, envelopes or items: TODO
(iv) Unit or uncertainty: TODO
(v) Registration, prospective manifest, analysis plan or estimator constant: TODO
(vi) Published number or sentence in the paper, README claims or claim renderers: TODO

## Gate ledger (D-118 / D-121)

Replace `Tier: full|light` with `Tier: full` or `Tier: light`. The independent reviewer confirms the tier; any disagreement resolves to full. Fill required rows as `RUN <repo-relative-path>` or `RUN <commit-sha>` (a committed repo-relative artifact at the PR head or a commit sha: no `:N`, no `#anchor`, no URL); Evidence is plain text, no backticks. Full tier requires all twelve rows. Light tier requires rows 1, 9, 11 and 12 with evidence; rows 2–8 and 10 must read `N/A (light tier)`. `NOT-RUN` remains a defect in required rows until filled. The `gate-ledger` check is required on `main`. Item 12 must name the final head sha.

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
