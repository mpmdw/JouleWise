# A309 PR: gate-ledger evidence (full tier). Merge candidate `58bfd3b0`.

`58bfd3b0` is fix `87aad39c`, plus bench NITs `67231358`, plus main `6a463e87` merged in.

| Row | Evidence |
|---|---|
| 1. Independent audit | The Opus contract lens [11](11-opus-contract-lens.md) ran as a fresh, non-author session at `87aad39c`: **PASS**, 0 BLOCKER, 0 SHOULD-FIX, 2 NITs. |
| 2. Paired distinct lenses | Execution: Sol 6.0 [10](10-sol-execution-lens.md), which built eleven or more adversarial git histories. Contract: Opus 5.5 [11](11-opus-contract-lens.md). |
| 3. Fix contract and triage | The contract is the dictated closure `../../2026-09-26-activation-8e43cfa7/10-liveness/ex-01-dictated-closure-M1.md`, applied verbatim. Triage: Sol F1 (rewrite-then-restore across two merges loads the honest bytes) → no truth impact, dictated text kept; the Fable final pass accepted this (Q2). Opus NIT-1 and NIT-2 → fixed at the bench in `67231358`. Opus's optional (b) direction → not taken, because the check compares bytes. |
| 4. Delta re-audit | The only fix round is the bench NITs (`67231358`: a test assertion and a comment). The cold Fable final pass [21](21-fable-final-pass.md) re-audited `58bfd3b0`, which includes it. |
| 5. Same-signature statement | There was one round. No defect class recurred, so there is no escalation. |
| 6. Opus counter-review | [11](11-opus-contract-lens.md), on the near-final head `87aad39c`. The delta since then is the NIT commit plus a docs-only main merge. |
| 7. Fable final pass | [21](21-fable-final-pass.md): **MERGE** `58bfd3b0`. It also rules that merging A309 BEFORE BFG-S S0 is consistent with BFGS-DESIGN-01 text 3, and sets three S0 obligations (§4). |
| 8. Overbuild prune | The diff is limited to the dictated closure: two history flags, one blob check, one comment, the header comment and three tests. Nothing beyond the closure. |
| 10. Fresh eyes after post-review commits | The Fable final pass ran on the final head `58bfd3b0`, after the NIT commit. |
