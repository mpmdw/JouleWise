Committed locally on `ops/2026-11-08-prune-fixes`; working tree clean.

- `dcaf2ca2c` — separate B5 test fix requiring the immutable 9b reference.
- `526d11168` — revised plan, 33 named anchors, census/grep scripts, regression tests, and evidence/rollback tables.

Targeted unittest results: equivalence **98 tests, 2 skips**; ops **11 passed**; frozen files **4 passed**; seal landing **9 passed**. Syntax, links, scope and topology checks passed. Full commands and file details are in the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-prune-fixes/docs/run_reports/2026-11-08-prune-fixes.md).

Execution remains gated on Ed’s ruleset, per-tag PR/check evidence, release identities, ledger recovery, branch-name dispositions and durable backups. Nothing was pushed or pruned; no analysis pipeline, network or MLX execution ran.

An early census read tracked legacy fixture traces whose provenance I did not establish. The final scanner excludes those payloads. No sealed or external data roots were accessed.