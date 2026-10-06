Tier: full|light

Impact statement (start each answer with Yes or No, then say why; any Yes makes this PR full tier):
(i) Raw-bundle byte or recorded timestamp: TODO
(ii) Reduced energy, time, token count or correctness score: TODO
(iii) Admit, refuse, select or exclude decision over bundles, nights, blocks, envelopes or items: TODO
(iv) Unit or uncertainty: TODO
(v) Registration, prospective manifest, analysis plan or estimator constant: TODO
(vi) Published number or sentence in the paper, README claims or claim renderers: TODO

## Gate ledger

Set the Tier line to `Tier: full` or `Tier: light`. Full tier: any PR that changes code or configs, or whose Impact statement has a Yes. Light tier: docs, records or tests only, with every Impact line No; light tier runs no audit rounds. Fill each row as `RUN <repo-relative-path>` or `RUN <commit-sha>` (plain text: no backticks, no `:N`, no `#anchor`, no URL), or with the exact N/A text the row allows. Row 3 names the final head sha, so update it after every push. Authority: D-118 as thinned on 2026-09-29 (summary in docs/process_prune_2026-09-29.md).

| # | Gate | Evidence |
| --- | --- | --- |
| 1 | Independent review by a non-author, with a lens that executes the code (light tier: N/A (light tier)) | NOT-RUN |
| 2 | Whole suite on the merged tree (current main merged into the head), exact tail recorded (light tier, docs only: N/A (docs only)) | NOT-RUN |
| 3 | Final head: the local whole suite and the passes ran at this sha (hosted CI is post-merge advisory) | NOT-RUN |
| 4 | Cold Fable final pass on merge code that touches measurement, calibration or claims (otherwise: N/A (no measurement, calibration or claim code); light tier: N/A (light tier)) | NOT-RUN |
| 5 | Findings dispositioned: each fixed, deferred to a named lane, or rejected with a reason (light tier: N/A (light tier)) | NOT-RUN |

## Summary

<!-- What changed and why? -->

## Verification

<!-- Commands run and their outcomes. -->
