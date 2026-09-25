# Disposition of every post-review finding (magistrate)

| Source | Finding | Disposition |
|---|---|---|
| 110a Astra contract lens F1 (nit) | `_ownership` lacks `-> dict` | LANDED in d2e751df per A291-PREMERGE-01 V1(a), with AST assertion |
| 110b Sol execution lens F1 (should_fix) | RecursionError escapes typed refusal | LANDED in d2e751df per V1(b): two-site cure (`_checked_derived`, `_seal`) plus the ruled regression; FAIL with 3fb98469 packer, PASS at d2e751df |
| 111b R6-1 (should_fix; blocker for first REGISTERED night) | level/night confound in `pack` | NOT this merge (V2 affirmed); proposed "R6-1 gate" rule recorded for the cold gate/Ed; joins the headline redesign (AP-5M v5 / A291 contract v5) |
| 111b R6-2 | cubic replay cost; runner must call requeue outside envelope interiors | runner obligation (A292) + follow-up A291-STRUCTURE-INDEX-01 (V1(d)) |
| 111b R6-3 (nit) | truncated-night close-out procedure | runner obligation (A292) |
| 111b CI cost | new modules absent from test_timings.json | follow-up CI-A291-TIMINGS-01 (V1(c)); hosted CI on this PR ran all shards green regardless |
| 112 M5 (follow-up) | `_digest` under finalize=True on unsealed deep roster | follow-up lane, gated like V1(d) |
| 114b F1 | gate-ledger.yml comments stale | carried by the TIER-01 installation branch |
| 114b F2 (nit) | TASK_QUEUE hand-maintained kernel count says 245 | next bookkeeping commit |
| 108b F1 (NIT N3 of 112) | entry witnesses assert inv_38/inv_38/inv_11, not the listed inv_23/inv_36/inv_37 | stated here and in 107b's table; recorded, not a defect of the rule |
| CI drift | main's TASK_QUEUE generated region hand-edited | cured in 37f47475 (kernel retirement), fresh-eyes 114b |
