## Gate ledger (D-118 / D-121)

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN docs/process_traces/2026-09-24-activation-278ebc9e/39b-a291-delta-reaudit-report.md |
| 2 | Paired distinct lenses: contract + execution (physics if measurement-adjacent) | RUN docs/process_traces/2026-09-24-activation-278ebc9e/110a-a291-r3-contract-lens-astra.md |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied | RUN docs/process_traces/2026-09-24-activation-278ebc9e/95-a291-final-texts-r4b.md |
| 4 | Delta re-audit of every fix round | RUN docs/process_traces/2026-09-24-activation-278ebc9e/110b-a291-r3-execution-lens-sol.md |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | RUN docs/process_traces/2026-09-24-activation-278ebc9e/81b-a291-ownership-harness-report.md |
| 6 | Opus counter-review on the near-final head | RUN docs/process_traces/2026-09-24-activation-278ebc9e/111b-a291-opus-counter-review.md |
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | NOT-RUN |
| 8 | Overbuild / merge-ability prune | RUN docs/process_traces/2026-09-24-activation-278ebc9e/111b-a291-opus-counter-review.md |
| 9 | Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded | NOT-RUN |
| 10 | Final-head fresh-eyes review after every post-review commit | RUN docs/process_traces/2026-09-24-activation-278ebc9e/113b-a291-fresh-eyes.md |
| 11 | CI green on final head + post-merge cross-unit integration review | NOT-RUN |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable | NOT-RUN |

## Summary

A291, the scored-roster packer (`joulewise/scored_packer.py`, `joulewise/scored_registration.py`), and its independent checker, ownership-forgery harness, fuzz and stress modules. Round 3 is the structural cure after the same-signature recurrence ("the seal accepts forged ownership"):
- one `_ownership` view, built once;
- the closed INV-11 (contract v4.1, record 89);
- the harness is the acceptance gate (cold rulings A291-ESC2-02 R4 and R4b).

Gate evidence (records under docs/process_traces/2026-09-24-activation-278ebc9e/):
- the harness is GREEN (0 seal escapes on exhaustive pairs and triples; legal corpus through the seal);
- mutation kills m1–m5 all kill (100b);
- two independent forger seats reached COMPLETED_NO_ESCAPE, and every accepted candidate is OUT_OF_ROUND and refused by replay (104, 106);
- entry-path witnesses (108b);
- lenses (110a/110b), Opus counter-review (111b), post-review commit d2e751df per A291-PREMERGE-01 (112), fresh eyes CLEAN (113b).

Also included: the activation 278ebc9e and 7370d0fb bookkeeping records (docs only). Draft until rows 7, 9, 11 and 12 are filled.

Known and deferred (ruled):
- R6-1 level/night confound in `pack` gates the first REGISTERED night, not this merge (112/20 V2);
- the CI timings (CI-A291-TIMINGS-01), the `_structure` index cut (A291-STRUCTURE-INDEX-01) and the finalize-path `_digest` hardening (M5) are follow-up lanes.

## Verification

See the gate ledger and the records.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
